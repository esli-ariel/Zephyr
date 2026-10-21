import httpx

from app.config import settings


class OpenRouterClient:
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self):
        self.api_key = settings.openrouter_api_key
        self.model = settings.openrouter_model

    async def chat(self, messages: list[dict]) -> str:

        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY n'est pas configurée."
            )

        if not self.model:
            raise ValueError(
                "OPENROUTER_MODEL n'est pas configuré."
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.frontend_url,
            "X-Title": "Zephyr",
        }

        payload = {
            "model": self.model,
            "messages": messages,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(self.BASE_URL, headers=headers, json=payload)
                if response.status_code != 200:
                    raise RuntimeError(f"Erreur OpenRouter ({response.status_code}).")
                data = response.json()
            content = data["choices"][0]["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise RuntimeError("Réponse OpenRouter vide ou invalide.")
            return content
        except httpx.HTTPError as exc:
            raise RuntimeError("Le service OpenRouter est indisponible.") from exc
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("Réponse OpenRouter invalide.") from exc
