from dataclasses import dataclass, field


@dataclass
class LearnerProfile:
    """
    Profil d'apprentissage de l'utilisateur.

    Ce profil contient les informations nécessaires
    pour personnaliser l'enseignement de Zéphyr.
    """

    name: str | None = None
    target_language: str | None = None
    level: str | None = None

    goals: list[str] = field(default_factory=list)

    weak_points: list[str] = field(default_factory=list)

    learned_vocabulary: list[str] = field(
        default_factory=list
    )

    common_mistakes: list[str] = field(
        default_factory=list
    )

    competency_scores: dict = field(
        default_factory=dict
    )

    assessment_history: list[dict] = field(
        default_factory=list
    )
    grammar_mastery: dict = field(default_factory=dict)
    grammar_history: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "target_language": self.target_language,
            "level": self.level,
            "goals": self.goals,
            "weak_points": self.weak_points,
            "learned_vocabulary": (
                self.learned_vocabulary
            ),
            "common_mistakes": (
                self.common_mistakes
            ),
            "competency_scores": (
                self.competency_scores
            ),
            "assessment_history": (
                self.assessment_history
            ),
            "grammar_mastery": self.grammar_mastery,
            "grammar_history": self.grammar_history,
        }