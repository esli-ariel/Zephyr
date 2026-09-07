from app.memory.short_term import ShortTermMemory


class MemoryManager:
    """
    Gestionnaire central de la mémoire de Zéphyr.
    """

    def __init__(self):
        self.short_term = ShortTermMemory(max_messages=20)

    def add_user_message(self, content: str) -> None:
        self.short_term.add_message(
            role="user",
            content=content,
        )

    def add_assistant_message(self, content: str) -> None:
        self.short_term.add_message(
            role="assistant",
            content=content,
        )

    def get_conversation(self) -> list[dict]:
        return self.short_term.get_messages()

    def clear_conversation(self) -> None:
        self.short_term.clear()

    def get_memory_info(self) -> dict:
        messages = self.short_term.get_messages()

        return {
            "message_count": len(messages),
            "max_messages": self.short_term.max_messages,
            "messages": messages,
        }