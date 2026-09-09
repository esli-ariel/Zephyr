from dataclasses import dataclass, field


@dataclass
class Exercise:
    """
    Représente un exercice pédagogique.
    """

    id: str
    exercise_type: str
    question: str

    level: str
    skill: str

    options: list[str] = field(
        default_factory=list
    )

    expected_answer: str | None = None

    difficulty: int = 1

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "exercise_type": self.exercise_type,
            "question": self.question,
            "level": self.level,
            "skill": self.skill,
            "options": self.options,
            "expected_answer": self.expected_answer,
            "difficulty": self.difficulty,
        }