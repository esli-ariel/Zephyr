from app.agent.context import ContextBuilder
from app.llm.openrouter import OpenRouterClient
from app.memory.memory_manager import MemoryManager


class ZephyrAgent:

    def __init__(self):
        self.name = "Zéphyr"

        self.llm = OpenRouterClient()

        self.memory = MemoryManager()

        self.context = ContextBuilder(
            self.memory
        )

    async def process(self, message: str) -> str:

        self.memory.add_user_message(message)

        messages = self.context.build()

        response = await self.llm.chat(messages)

        self.memory.add_assistant_message(response)

        return response

    def clear_memory(self) -> None:
        self.memory.clear_conversation()