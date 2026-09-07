from typing import TypedDict


class Message(TypedDict):
    role: str
    content: str


class ShortTermMemory:
    """
    Mémoire conversationnelle temporaire de Zéphyr.

    Elle conserve les derniers messages d'une conversation
    pendant que l'application est en fonctionnement.
    """

    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages
        self.messages: list[Message] = []

    def add_message(self, role: str, content: str) -> None:
        self.messages.append(
            {
                "role": role,
                "content": content,
            }
        )

        self._limit_messages()

    def get_messages(self) -> list[Message]:
        return self.messages.copy()

    def clear(self) -> None:
        self.messages.clear()

    def _limit_messages(self) -> None:
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]