from app.agent.prompts import ZEPHYR_SYSTEM_PROMPT
from app.memory.memory_manager import MemoryManager


class ContextBuilder:
    """
    Construit le contexte envoyé au modèle de langage.
    """

    def __init__(self, memory: MemoryManager):
        self.memory = memory

    def build(self) -> list[dict]:
        messages = [
            {
                "role": "system",
                "content": ZEPHYR_SYSTEM_PROMPT,
            }
        ]

        messages.extend(
            self.memory.get_conversation()
        )

        return messages