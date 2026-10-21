import logging
from contextlib import asynccontextmanager
from typing import Annotated, Literal
from uuid import UUID

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field, model_validator
from starlette.responses import JSONResponse

from app.config import settings
from app.agent.zephyr import ZephyrAgent
from app.learning.adaptive_assessment import AdaptiveAssessment
from app.persistence import StateStore, capture_state, restore_state
from app.sessions import LearnerSessions
from app.learning.llm_schemas import Level, Skill

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    store = StateStore(settings.database_path) if settings.persistence_enabled else None
    app.state.store = store
    app.state.learners = LearnerSessions(store)
    try:
        yield
    finally:
        app.state.learners = None
        app.state.store = None


app = FastAPI(
    title=settings.app_name,
    description="API de l'assistant intelligent Zéphyr",
    version="0.7.2",
    lifespan=lifespan,
)


@app.middleware("http")
async def persist_learning_state(request: Request, call_next):
    if not request.url.path.startswith("/api/") or (
        request.url.path == "/api/learners" and request.method == "POST"
    ):
        return await call_next(request)
    values = request.headers.getlist("X-Learner-ID")
    try:
        if len(values) != 1:
            raise ValueError("Un seul identifiant est requis.")
        learner_id = str(UUID(values[0]))
    except ValueError:
        return JSONResponse(status_code=400, content={
            "detail": "L'en-tête X-Learner-ID doit contenir un identifiant UUID unique.",
        })
    registry = request.app.state.learners
    try:
        session = registry.get(learner_id)
    except Exception:
        logger.exception("Échec de chargement de l'apprenant")
        return JSONResponse(status_code=503, content={"detail": "Données indisponibles."})
    if session is None:
        return JSONResponse(status_code=404, content={"detail": "Apprenant introuvable."})
    request.state.learner_session = session
    # Les requêtes d'un même apprenant sont sérialisées, les autres restent indépendantes.
    async with session.lock:
        before = capture_state(session.agent, session.assessment)
        try:
            response = await call_next(request)
            if response.status_code >= 400:
                restore_state(before, session.agent, session.assessment)
                return response
            after = capture_state(session.agent, session.assessment)
            if after != before and registry.store is not None:
                try:
                    registry.store.save(after, learner_id)
                except Exception:
                    logger.exception("Échec de sauvegarde de l'apprenant")
                    restore_state(before, session.agent, session.assessment)
                    return JSONResponse(status_code=503, content={
                        "detail": "Sauvegarde indisponible. Veuillez réessayer.",
                    })
            response.headers["X-Learner-ID"] = learner_id
            return response
        except BaseException:
            restore_state(before, session.agent, session.assessment)
            raise


async def get_agent(
    request: Request,
    x_learner_id: Annotated[str, Header(description="Identifiant retourné par POST /api/learners")],
) -> ZephyrAgent:
    return request.state.learner_session.agent


async def get_assessment(
    request: Request,
    x_learner_id: Annotated[str, Header(description="Identifiant retourné par POST /api/learners")],
) -> AdaptiveAssessment:
    return request.state.learner_session.assessment


Agent = Annotated[ZephyrAgent, Depends(get_agent)]
Assessment = Annotated[AdaptiveAssessment, Depends(get_assessment)]


class LearnerCreated(BaseModel):
    learner_id: UUID


@app.post("/api/learners", status_code=201, response_model=LearnerCreated)
async def create_learner(request: Request, response: Response):
    try:
        session = request.app.state.learners.create()
    except Exception:
        logger.exception("Échec de création de l'apprenant")
        raise HTTPException(status_code=503, detail="Création de l'apprenant indisponible.")
    response.headers["X-Learner-ID"] = session.learner_id
    return {"learner_id": session.learner_id}


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )

@app.get("/")
async def root():
    return {
        "agent": settings.app_name,
        "status": "online",
        "version": app.version,
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
    }


@app.post("/api/chat")
async def chat(agent: Agent, request: ChatRequest):

    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Le message ne peut pas être vide.",
        )

    try:

        response = await agent.process(
            request.message
        )

        return {
            "agent": "Zéphyr",
            "message": request.message,
            "response": response,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    except RuntimeError as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )

@app.delete("/api/chat/memory")
async def clear_memory(agent: Agent):

    agent.clear_memory()

    return {
        "status": "success",
        "message": "La mémoire conversationnelle a été effacée.",
    }

@app.get("/api/chat/memory")
async def get_memory(agent: Agent):

    return agent.memory.get_memory_info()

@app.get("/api/learner/profile")
async def get_learner_profile(agent: Agent):

    return agent.get_learner_profile()

@app.delete("/api/learner/profile")
async def clear_learner_profile(agent: Agent):

    agent.clear_learner_profile()

    return {
        "status": "success",
        "message": "Le profil de l'apprenant a été effacé.",
    }

class LearnerProfileRequest(BaseModel):
    name: str | None = None
    target_language: str | None = None
    level: Level | None = None
    goal: str | None = None

@app.put("/api/learner/profile")
async def update_learner_profile(
    agent: Agent,
    request: LearnerProfileRequest,
):

    if request.name is not None:
        agent.learner.set_name(request.name)

    if request.target_language is not None:
        agent.learner.set_target_language(
            request.target_language
        )

    if request.level is not None:
        agent.learner.set_level(request.level)

    if request.goal is not None:
        agent.learner.add_goal(request.goal)

    return agent.get_learner_profile()

@app.post("/api/assessment/start")
async def start_assessment(assessment: Assessment):
    """
    Démarre une nouvelle évaluation adaptative.
    """

    assessment.reset()

    question = (
        assessment.get_current_question()
    )

    return {
        "status": "started",
        "message": (
            "L'évaluation adaptative "
            "a commencé."
        ),
        "question": question,
        "progress": (
            assessment.get_progress()
        ),
    }

@app.get("/api/assessment/question")
async def get_assessment_question(assessment: Assessment):
    """
    Retourne la question actuelle.
    """

    question = (
        assessment.get_current_question()
    )

    if question is None:
        return {
            "finished": True,
            "question": None,
            "progress": (
                assessment.get_progress()
            ),
        }

    return {
        "finished": False,
        "question": question,
        "progress": (
            assessment.get_progress()
        ),
    }

class AssessmentAnswerRequest(BaseModel):
    answer: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )

@app.post("/api/assessment/answer")
async def submit_assessment_answer(
    assessment: Assessment,
    request: AssessmentAnswerRequest,
):
    """
    Soumet une réponse et déclenche
    son évaluation.
    """

    try:

        result = (
            await assessment.submit_answer(
                request.answer
            )
        )

        return result

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

@app.get("/api/assessment/progress")
async def get_assessment_progress(assessment: Assessment):
    """
    Retourne la progression de l'évaluation.
    """

    return (
        assessment.get_progress()
    )

@app.get("/api/assessment/result")
async def get_assessment_result(agent: Agent, assessment: Assessment):
    """
    Retourne le résultat pédagogique complet
    de l'évaluation.
    """

    if not assessment.session.finished:
        raise HTTPException(
            status_code=400,
            detail=(
                "L'évaluation n'est pas encore terminée."
            ),
        )

    try:
        result = await assessment.get_final_result()
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    agent.apply_assessment_result(
        result
    )

    return result

@app.delete("/api/assessment")
async def reset_assessment(assessment: Assessment):
    """
    Réinitialise l'évaluation.
    """

    assessment.reset()

    return {
        "status": "success",
        "message": (
            "L'évaluation a été réinitialisée."
        ),
    }

@app.get("/api/learning/context")
async def get_learning_context(agent: Agent):
    return agent.get_learning_context()

class LessonRequest(BaseModel):
    topic: str = Field(
        ...,
        min_length=2,
        max_length=200,
    )

@app.post("/api/learning/lesson")
async def generate_lesson(
    agent: Agent,
    request: LessonRequest,
):
    try:
        lesson = await agent.learning_engine.generate_lesson(
            request.topic
        )

        return lesson.to_dict()

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )

class ExerciseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    target_category: Literal["vocabulary", "grammar"] | None = None
    target: str | None = Field(default=None, min_length=1, max_length=200, pattern=r"\S")

    @model_validator(mode="after")
    def validate_target(self):
        if (self.target_category is None) != (self.target is None):
            raise ValueError("La catégorie et la notion doivent être fournies ensemble.")
        return self

    topic: str = Field(
        ...,
        min_length=2,
        max_length=200,
    )

    skill: Skill

    count: int = Field(
        default=5,
        ge=1,
        le=20,
    )

@app.post("/api/learning/exercises")
async def generate_exercises(
    agent: Agent,
    request: ExerciseRequest,
):
    try:
        exercises = (
            await agent.learning_engine.generate_exercises(
                topic=request.topic,
                skill=request.skill,
                count=request.count,
                target_category=request.target_category,
                target=request.target,
            )
        )

        return {
            "count": len(exercises),
            "exercises": [
                exercise.to_public_dict()
                for exercise in exercises
            ],
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )

class VocabularyRequest(BaseModel):
    word: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    translation: str = Field(
        ...,
        min_length=1,
        max_length=200,
    )

    category: str = Field(
        default="general",
        max_length=50,
    )

    examples: list[str] = Field(
        default_factory=list,
    )

    difficulty: int = Field(
        default=1,
        ge=1,
        le=5,
    )

@app.post("/api/learning/vocabulary")
async def add_vocabulary(
    agent: Agent,
    request: VocabularyRequest,
):
    try:
        item = agent.learning_engine.add_vocabulary(
            word=request.word,
            translation=request.translation,
            category=request.category,
            examples=request.examples,
            difficulty=request.difficulty,
        )

        return item.to_dict()

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

@app.get("/api/learning/vocabulary")
async def get_vocabulary(agent: Agent):
    items = (
        agent.learning_engine
        .vocabulary
        .get_all_words()
    )

    return {
        "count": len(items),
        "vocabulary": [
            item.to_dict()
            for item in items
        ],
    }

@app.get("/api/learning/vocabulary/statistics")
async def get_vocabulary_statistics(agent: Agent):
    return (
        agent.learning_engine
        .get_vocabulary_statistics()
    )

@app.get("/api/learning/vocabulary/review")
async def get_vocabulary_to_review(agent: Agent):
    items = (
        agent.learning_engine
        .vocabulary
        .get_words_to_review()
    )

    return {
        "count": len(items),
        "words": [
            item.to_dict()
            for item in items
        ],
    }

@app.get("/api/learning/recommendations")
async def get_learning_recommendations(
    agent: Agent,
    limit: int = 5,
):
    """
    Retourne les recommandations pédagogiques
    personnalisées de l'apprenant.
    """

    if limit < 1:
        raise HTTPException(
            status_code=400,
            detail="La limite doit être supérieure ou égale à 1.",
        )

    if limit > 50:
        raise HTTPException(
            status_code=400,
            detail="La limite ne peut pas dépasser 50.",
        )

    try:
        recommendations = (
            agent.learning_engine
            .get_recommendations(limit=limit)
        )

        return {
            "count": len(recommendations),
            "recommendations": recommendations,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

@app.get("/api/learning/plan")
async def get_learning_plan(
    agent: Agent,
    limit: int = 5,
    available_minutes: int | None = None,
):
    """
    Retourne un plan d'apprentissage
    personnalisé.
    """

    if limit < 1:
        raise HTTPException(
            status_code=400,
            detail="La limite doit être supérieure ou égale à 1.",
        )

    if limit > 20:
        raise HTTPException(
            status_code=400,
            detail="La limite ne peut pas dépasser 20.",
        )

    if (
        available_minutes is not None
        and available_minutes < 1
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Le temps disponible doit être "
                "supérieur ou égal à 1 minute."
            ),
        )

    try:
        plan = (
            agent.learning_engine
            .get_learning_plan(
                limit=limit,
                available_minutes=available_minutes,
            )
        )

        return plan

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

@app.get("/api/learning/plan/current")
async def get_current_learning_plan(agent: Agent):
    plan = agent.learning_engine.current_learning_plan
    if plan is None:
        raise HTTPException(status_code=404, detail="Aucun plan d'apprentissage actif.")
    return plan.to_dict()


class CompleteLearningItemRequest(BaseModel):
    score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Score compris entre 0 et 100.",
    )


@app.post("/api/learning/plan/items/{item_id}/complete")
async def complete_learning_plan_item(
    agent: Agent,
    item_id: str,
    request: CompleteLearningItemRequest,
):
    """
    Marque une activité du plan comme terminée.
    """

    try:
        item = (
            agent.learning_engine
            .complete_learning_plan_item(
                item_id=item_id,
                score=request.score,
            )
        )

        return {
            "status": "completed",
            "item": item,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

class ExerciseAnswerRequest(BaseModel):
    answer: str = Field(min_length=1, max_length=5000)


@app.post("/api/learning/exercises/{exercise_id}/answer")
async def answer_exercise(agent: Agent, exercise_id: str, request: ExerciseAnswerRequest):
    exercise = next(
        (item for item in agent.learning_engine.get_exercises()
         if item.id == exercise_id),
        None,
    )
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercice introuvable.")
    try:
        result = await agent.evaluate_exercise(exercise, request.answer)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except (RuntimeError, httpx.HTTPError) as exc:
        raise HTTPException(
            status_code=502, detail="Le service de correction est indisponible."
        ) from exc
    return {"exercise_id": exercise.id, "evaluation": result}


class VocabularyAnswerRequest(BaseModel):
    word: str = Field(min_length=1, max_length=100, pattern=r"\S")
    correct: bool = Field(strict=True)


@app.post("/api/learning/vocabulary/answer")
async def answer_vocabulary(agent: Agent, request: VocabularyAnswerRequest):
    item = agent.learning_engine.vocabulary.get_word(request.word)
    if item is None:
        raise HTTPException(status_code=404, detail="Mot introuvable.")
    agent.learning_engine.register_vocabulary_answer(request.word, request.correct)
    return item.to_dict()


class GrammarRequest(BaseModel):
    rule: str = Field(min_length=1, max_length=200, pattern=r"\S")
    explanation: str = Field(min_length=1, max_length=5000, pattern=r"\S")
    category: str = Field(default="general", max_length=50)
    examples: list[str] = Field(default_factory=list)
    difficulty: int = Field(default=1, ge=1, le=5)


@app.post("/api/learning/grammar")
async def add_grammar(agent: Agent, request: GrammarRequest):
    try:
        item = agent.learning_engine.add_grammar_rule(**request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return item.to_dict()


@app.get("/api/learning/grammar")
async def get_grammar(agent: Agent):
    items = agent.learning_engine.grammar.get_all_rules()
    return {"count": len(items), "rules": [item.to_dict() for item in items]}


@app.get("/api/learning/grammar/statistics")
async def get_grammar_statistics(agent: Agent):
    return agent.learning_engine.get_grammar_statistics()


@app.get("/api/learning/grammar/review")
async def get_grammar_to_review(agent: Agent):
    items = agent.learning_engine.get_grammar_to_review()
    return {"count": len(items), "rules": [item.to_dict() for item in items]}


class GrammarAnswerRequest(BaseModel):
    rule: str = Field(min_length=1, max_length=200, pattern=r"\S")
    correct: bool = Field(strict=True)


@app.post("/api/learning/grammar/answer")
async def answer_grammar(agent: Agent, request: GrammarAnswerRequest):
    item = agent.learning_engine.grammar.get_rule(request.rule)
    if item is None:
        raise HTTPException(status_code=404, detail="Règle introuvable.")
    agent.learning_engine.register_grammar_answer(request.rule, request.correct)
    return item.to_dict()
