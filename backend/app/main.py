from fastapi import FastAPI
from app.agent.zephyr import ZephyrAgent

app = FastAPI(
    title="Zéphyr API",
    description="API de l'assistant intelligent Zéphyr",
    version="0.1.0"
)

zephyr = ZephyrAgent()


@app.get("/")
async def root():
    return {
        "agent": "Zéphyr",
        "status": "online",
        "message": "Bonjour, je suis Zéphyr."
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }


@app.post("/api/chat")
async def chat(message: str):
    response = await zephyr.process(message)

    return {
        "agent": "Zéphyr",
        "message": message,
        "response": response
    }