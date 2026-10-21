"""Configuration de test indépendante des variables de l'application hôte."""
import os

import pytest

os.environ["DEBUG"] = "false"
os.environ["OPENROUTER_API_KEY"] = ""
os.environ["OPENROUTER_MODEL"] = ""
os.environ["PERSISTENCE_ENABLED"] = "false"


@pytest.fixture(autouse=True)
def block_real_llm_calls(monkeypatch):
    from app.llm.openrouter import OpenRouterClient

    async def blocked(*args, **kwargs):
        raise AssertionError("Les tests doivent simuler les appels OpenRouter.")

    monkeypatch.setattr(OpenRouterClient, "chat", blocked)
