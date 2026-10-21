import httpx
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse

from app.config import settings
from app.agent.zephyr import ZephyrAgent
from app.persistence import StateStore, capture_state, restore_state
from app.learning.adaptive_assessment import (
    AdaptiveAssessment,
)




@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.store = None
    app.state.state_lock = asyncio.Lock()
    if settings.persistence_enabled:
        store = StateStore(settings.database_path)
        snapshot = store.load()
        if snapshot is not None:
            restore_state(snapshot, zephyr, adaptive_assessment)
        app.state.store = store
    try:
        yield
    finally:
        app.state.store = None


app = FastAPI(
    title=settings.app_name,
    description="API de l'assistant intelligent Zéphyr",
    version="0.7.0",
    lifespan=lifespan,
)


zephyr = ZephyrAgent()
adaptive_assessment = AdaptiveAssessment()


@app.middleware("http")
async def persist_learning_state(request, call_next):
    store = getattr(app.state, "store", None)
    if store is None:
        return await call_next(request)
    # Le prototype mono-apprenant traite les mutations dans l'ordre et ne
    # confirme une requête qu'après la validation de la transaction SQLite.
    async with app.state.state_lock:
        before = capture_state(zephyr, adaptive_assessment)
        try:
            response = await call_next(request)
            if response.status_code >= 400:
                restore_state(before, zephyr, adaptive_assessment)
                return response
            after = capture_state(zephyr, adaptive_assessment)
            if after != before:
                try:
                    store.save(after)
                except Exception:
                    logging.getLogger(__name__).exception("Échec de sauvegarde de l'état")
                    restore_state(before, zephyr, adaptive_assessment)
                    return JSONResponse(
                        status_code=503,
                        content={"detail": "Sauvegarde indisponible. Veuillez réessayer."},
                    )
            return response
        except BaseException:
            restore_state(before, zephyr, adaptive_assessment)
            raise


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
async def chat(request: ChatRequest):

    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Le message ne peut pas être vide.",
        )

    try:

        response = await zephyr.process(
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
async def clear_memory():

    zephyr.clear_memory()

    return {
        "status": "success",
        "message": "La mémoire conversationnelle a été effacée.",
    }

@app.get("/api/chat/memory")
async def get_memory():

    return zephyr.memory.get_memory_info()

@app.get("/api/learner/profile")
async def get_learner_profile():

    return zephyr.get_learner_profile()

@app.delete("/api/learner/profile")
async def clear_learner_profile():

    zephyr.clear_learner_profile()

    return {
        "status": "success",
        "message": "Le profil de l'apprenant a été effacé.",
    }

class LearnerProfileRequest(BaseModel):
    name: str | None = None
    target_language: str | None = None
    level: str | None = None
    goal: str | None = None

@app.put("/api/learner/profile")
async def update_learner_profile(
    request: LearnerProfileRequest,
):

    if request.name is not None:
        zephyr.learner.set_name(request.name)

    if request.target_language is not None:
        zephyr.learner.set_target_language(
            request.target_language
        )

    if request.level is not None:
        zephyr.learner.set_level(request.level)

    if request.goal is not None:
        zephyr.learner.add_goal(request.goal)

    return zephyr.get_learner_profile()

@app.post("/api/assessment/start")
async def start_assessment():
    """
    Démarre une nouvelle évaluation adaptative.
    """

    adaptive_assessment.reset()

    question = (
        adaptive_assessment.get_current_question()
    )

    return {
        "status": "started",
        "message": (
            "L'évaluation adaptative "
            "a commencé."
        ),
        "question": question,
        "progress": (
            adaptive_assessment.get_progress()
        ),
    }

@app.get("/api/assessment/question")
async def get_assessment_question():
    """
    Retourne la question actuelle.
    """

    question = (
        adaptive_assessment.get_current_question()
    )

    if question is None:
        return {
            "finished": True,
            "question": None,
            "progress": (
                adaptive_assessment.get_progress()
            ),
        }

    return {
        "finished": False,
        "question": question,
        "progress": (
            adaptive_assessment.get_progress()
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
    request: AssessmentAnswerRequest,
):
    """
    Soumet une réponse et déclenche
    son évaluation.
    """

    try:

        result = (
            await adaptive_assessment.submit_answer(
                request.answer
            )
        )

        return result

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

@app.get("/api/assessment/progress")
async def get_assessment_progress():
    """
    Retourne la progression de l'évaluation.
    """

    return (
        adaptive_assessment.get_progress()
    )

@app.get("/api/assessment/result")
async def get_assessment_result():
    """
    Retourne le résultat pédagogique complet
    de l'évaluation.
    """

    if not adaptive_assessment.session.finished:
        raise HTTPException(
            status_code=400,
            detail=(
                "L'évaluation n'est pas encore terminée."
            ),
        )

    result = (
        await adaptive_assessment.get_final_result()
    )

    zephyr.apply_assessment_result(
        result
    )

    return result

@app.delete("/api/assessment")
async def reset_assessment():
    """
    Réinitialise l'évaluation.
    """

    adaptive_assessment.reset()

    return {
        "status": "success",
        "message": (
            "L'évaluation a été réinitialisée."
        ),
    }

@app.get("/api/learning/context")
async def get_learning_context():
    return zephyr.get_learning_context()

class LessonRequest(BaseModel):
    topic: str = Field(
        ...,
        min_length=2,
        max_length=200,
    )

@app.post("/api/learning/lesson")
async def generate_lesson(
    request: LessonRequest,
):
    try:
        lesson = await zephyr.learning_engine.generate_lesson(
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
    topic: str = Field(
        ...,
        min_length=2,
        max_length=200,
    )

    skill: str = Field(
        ...,
        min_length=2,
        max_length=50,
    )

    count: int = Field(
        default=5,
        ge=1,
        le=20,
    )

@app.post("/api/learning/exercises")
async def generate_exercises(
    request: ExerciseRequest,
):
    try:
        exercises = (
            await zephyr.learning_engine.generate_exercises(
                topic=request.topic,
                skill=request.skill,
                count=request.count,
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
    request: VocabularyRequest,
):
    try:
        item = zephyr.learning_engine.add_vocabulary(
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
async def get_vocabulary():
    items = (
        zephyr.learning_engine
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
async def get_vocabulary_statistics():
    return (
        zephyr.learning_engine
        .get_vocabulary_statistics()
    )

@app.get("/api/learning/vocabulary/review")
async def get_vocabulary_to_review():
    items = (
        zephyr.learning_engine
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
            zephyr.learning_engine
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
            zephyr.learning_engine
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
async def get_current_learning_plan():
    plan = zephyr.learning_engine.current_learning_plan
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
    item_id: str,
    request: CompleteLearningItemRequest,
):
    """
    Marque une activité du plan comme terminée.
    """

    try:
        item = (
            zephyr.learning_engine
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
async def answer_exercise(exercise_id: str, request: ExerciseAnswerRequest):
    exercise = next(
        (item for item in zephyr.learning_engine.get_exercises()
         if item.id == exercise_id),
        None,
    )
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercice introuvable.")
    try:
        result = await zephyr.evaluate_exercise(exercise, request.answer)
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
async def answer_vocabulary(request: VocabularyAnswerRequest):
    item = zephyr.learning_engine.vocabulary.get_word(request.word)
    if item is None:
        raise HTTPException(status_code=404, detail="Mot introuvable.")
    zephyr.learning_engine.register_vocabulary_answer(request.word, request.correct)
    return item.to_dict()


class GrammarRequest(BaseModel):
    rule: str = Field(min_length=1, max_length=200, pattern=r"\S")
    explanation: str = Field(min_length=1, max_length=5000, pattern=r"\S")
    category: str = Field(default="general", max_length=50)
    examples: list[str] = Field(default_factory=list)
    difficulty: int = Field(default=1, ge=1, le=5)


@app.post("/api/learning/grammar")
async def add_grammar(request: GrammarRequest):
    try:
        item = zephyr.learning_engine.add_grammar_rule(**request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return item.to_dict()


@app.get("/api/learning/grammar")
async def get_grammar():
    items = zephyr.learning_engine.grammar.get_all_rules()
    return {"count": len(items), "rules": [item.to_dict() for item in items]}


@app.get("/api/learning/grammar/statistics")
async def get_grammar_statistics():
    return zephyr.learning_engine.get_grammar_statistics()


@app.get("/api/learning/grammar/review")
async def get_grammar_to_review():
    items = zephyr.learning_engine.get_grammar_to_review()
    return {"count": len(items), "rules": [item.to_dict() for item in items]}


class GrammarAnswerRequest(BaseModel):
    rule: str = Field(min_length=1, max_length=200, pattern=r"\S")
    correct: bool = Field(strict=True)


@app.post("/api/learning/grammar/answer")
async def answer_grammar(request: GrammarAnswerRequest):
    item = zephyr.learning_engine.grammar.get_rule(request.rule)
    if item is None:
        raise HTTPException(status_code=404, detail="Règle introuvable.")
    zephyr.learning_engine.register_grammar_answer(request.rule, request.correct)
    return item.to_dict()
