from dataclasses import dataclass, field


@dataclass
class LearnerProfile:
    """
    Profil d'apprentissage d'un utilisateur.
    """

    # ==========================================================
    # IDENTITÉ
    # ==========================================================

    name: str | None = None

    target_language: str | None = None

    level: str | None = None

    # ==========================================================
    # OBJECTIFS
    # ==========================================================

    goals: list[str] = field(
        default_factory=list
    )

    # ==========================================================
    # DIFFICULTÉS
    # ==========================================================

    weak_points: list[str] = field(
        default_factory=list
    )

    # ==========================================================
    # FORCES
    # ==========================================================

    strengths: list[str] = field(
        default_factory=list
    )

    # ==========================================================
    # VOCABULAIRE
    # ==========================================================

    learned_vocabulary: list[str] = field(
        default_factory=list
    )

    # ==========================================================
    # ERREURS
    # ==========================================================

    common_mistakes: list[str] = field(
        default_factory=list
    )

    # ==========================================================
    # COMPÉTENCES
    # ==========================================================

    competency_scores: dict = field(
        default_factory=dict
    )

    # ==========================================================
    # HISTORIQUE DES ÉVALUATIONS
    # ==========================================================

    assessment_history: list[dict] = field(
        default_factory=list
    )

    # ==========================================================
    # MAÎTRISE DE LA GRAMMAIRE
    # ==========================================================

    grammar_mastery: dict = field(
        default_factory=dict
    )

    # ==========================================================
    # HISTORIQUE GRAMMATICAL
    # ==========================================================

    grammar_history: list[dict] = field(
        default_factory=list
    )

    # ==========================================================
    # SERIALISATION
    # ==========================================================

    def to_dict(self) -> dict:
        """
        Convertit le profil en dictionnaire.
        """

        return {
            "name": self.name,
            "target_language": self.target_language,
            "level": self.level,
            "goals": self.goals,
            "weak_points": self.weak_points,
            "strengths": self.strengths,
            "learned_vocabulary": self.learned_vocabulary,
            "common_mistakes": self.common_mistakes,
            "competency_scores": self.competency_scores,
            "assessment_history": self.assessment_history,
            "grammar_mastery": self.grammar_mastery,
            "grammar_history": self.grammar_history,
        }