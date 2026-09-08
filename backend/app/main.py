from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.agent.zephyr import ZephyrAgent
from pydantic import BaseModel, Field
from app.learning.adaptive_assessment import (
    AdaptiveAssessment,
)




app = FastAPI(
    title=settings.app_name,
    description="API de l'assistant intelligent Zéphyr",
    version="0.2.0",
)


zephyr = ZephyrAgent()
adaptive_assessment = AdaptiveAssessment()


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
        "version": "0.2.0",
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
