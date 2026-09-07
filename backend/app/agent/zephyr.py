from app.llm.openrouter import OpenRouterClient
from app.agent.prompts import ZEPHYR_SYSTEM_PROMPT


class ZephyrAgent:

    def __init__(self):
        self.name = "Zéphyr"
        self.llm = OpenRouterClient()

    async def process(self, message: str) -> str:

        messages = [
            {
                "role": "system",
                "content": ZEPHYR_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": message,
            },
        ]

        response = await self.llm.chat(messages)

        return response