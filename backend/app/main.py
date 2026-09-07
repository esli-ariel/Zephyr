from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.agent.zephyr import ZephyrAgent
from pydantic import BaseModel, Field



app = FastAPI(
    title=settings.app_name,
    description="API de l'assistant intelligent Zéphyr",
    version="0.2.0",
)


zephyr = ZephyrAgent()


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