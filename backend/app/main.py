from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.agent.zephyr import ZephyrAgent


app = FastAPI(
    title=settings.app_name,
    description="API de l'assistant intelligent Zéphyr",
    version="0.2.0",
)


zephyr = ZephyrAgent()


class ChatRequest(BaseModel):
    message: str


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