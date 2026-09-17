from app.learning.learner import LearnerProfile


class LearnerProfileManager:
    """
    Gestionnaire du profil d'apprentissage de Zéphyr.
    """

    def __init__(self):
        self.profile = LearnerProfile()

    # ==========================================================
    # IDENTITÉ
    # ==========================================================

    def set_name(self, name: str) -> None:
        self.profile.name = name.strip()

    def set_target_language(self, language: str) -> None:
        self.profile.target_language = language.strip()

    def set_level(self, level: str) -> None:
        self.profile.level = level.strip()

    # ==========================================================
    # OBJECTIFS
    # ==========================================================

    def add_goal(self, goal: str) -> None:
        goal = goal.strip()

        if goal and goal not in self.profile.goals:
            self.profile.goals.append(goal)

    # ==========================================================
    # DIFFICULTÉS
    # ==========================================================

    def add_weak_point(self, weak_point: str) -> None:
        weak_point = weak_point.strip()

        if (
            weak_point
            and weak_point not in self.profile.weak_points
        ):
            self.profile.weak_points.append(
                weak_point
            )

    # ==========================================================
    # FORCES
    # ==========================================================

    def add_strength(self, strength: str) -> None:
        strength = strength.strip()

        if (
            strength
            and strength not in self.profile.strengths
        ):
            self.profile.strengths.append(
                strength
            )

    # ==========================================================
    # VOCABULAIRE
    # ==========================================================

    def add_vocabulary(self, word: str) -> None:
        word = word.strip()

        if (
            word
            and word not in self.profile.learned_vocabulary
        ):
            self.profile.learned_vocabulary.append(
                word
            )

    def add_learned_vocabulary(self, word: str) -> None:
        word = word.strip()

        if not word:
            return

        if word not in self.profile.learned_vocabulary:
            self.profile.learned_vocabulary.append(
                word
            )

    # ==========================================================
    # ERREURS
    # ==========================================================

    def add_common_mistake(self, mistake: str) -> None:
        mistake = mistake.strip()

        if (
            mistake
            and mistake not in self.profile.common_mistakes
        ):
            self.profile.common_mistakes.append(
                mistake
            )

    # ==========================================================
    # PROFIL
    # ==========================================================

    def get_profile(self) -> dict:
        return self.profile.to_dict()

    def get_profile_object(self) -> LearnerProfile:
        return self.profile

    def clear_profile(self) -> None:
        self.profile = LearnerProfile()

    # ==========================================================
    # COMPÉTENCES
    # ==========================================================

    def update_competency_scores(
        self,
        scores: dict,
    ) -> None:

        for competency, score in scores.items():

            if score is None:
                continue

            self.profile.competency_scores[
                competency
            ] = score

    # ==========================================================
    # ÉVALUATIONS
    # ==========================================================

    def add_assessment_result(
        self,
        result: dict,
    ) -> None:

        assessment_id = result.get(
            "assessment_id"
        )

        if assessment_id:

            for existing in self.profile.assessment_history:

                if (
                    existing.get("assessment_id")
                    == assessment_id
                ):
                    return

        assessment_record = {
            "assessment_id": assessment_id,
            "estimated_level": result.get(
                "estimated_level"
            ),
            "validated_levels": result.get(
                "validated_levels",
                [],
            ),
            "overall_score": result.get(
                "overall_score",
                0,
            ),
            "competency_scores": result.get(
                "competency_scores",
                {},
            ),
        }

        self.profile.assessment_history.append(
            assessment_record
        )

    def apply_assessment_result(
        self,
        result: dict,
    ) -> None:

        # ------------------------------------------------------
        # NIVEAU
        # ------------------------------------------------------

        estimated_level = result.get(
            "estimated_level"
        )

        if estimated_level:
            self.set_level(
                estimated_level
            )

        # ------------------------------------------------------
        # COMPÉTENCES
        # ------------------------------------------------------

        self.update_competency_scores(
            result.get(
                "competency_scores",
                {},
            )
        )

        # ------------------------------------------------------
        # POINTS FAIBLES
        # ------------------------------------------------------

        for weak_point in result.get(
            "weak_points",
            [],
        ):
            self.add_weak_point(
                weak_point
            )

        # ------------------------------------------------------
        # FORCES
        # ------------------------------------------------------

        for strength in result.get(
            "strengths",
            [],
        ):
            self.add_strength(
                strength
            )

        # ------------------------------------------------------
        # ERREURS
        # ------------------------------------------------------

        for error in result.get(
            "errors",
            [],
        ):
            self.add_common_mistake(
                error
            )

        # ------------------------------------------------------
        # HISTORIQUE
        # ------------------------------------------------------

        self.add_assessment_result(
            result
        )

    # ==========================================================
    # RÉSULTATS D'EXERCICES
    # ==========================================================

    def apply_exercise_result(
        self,
        result: dict,
    ) -> None:

        # ------------------------------------------------------
        # COMPÉTENCES
        # ------------------------------------------------------

        self.update_competency_scores(
            result.get(
                "competency_scores",
                {},
            )
        )

        # ------------------------------------------------------
        # POINTS FAIBLES
        # ------------------------------------------------------

        for weak_point in result.get(
            "weak_points",
            [],
        ):
            self.add_weak_point(
                weak_point
            )

        # ------------------------------------------------------
        # FORCES
        # ------------------------------------------------------

        for strength in result.get(
            "strengths",
            [],
        ):
            self.add_strength(
                strength
            )

        # ------------------------------------------------------
        # ERREURS
        # ------------------------------------------------------

        for error in result.get(
            "errors",
            [],
        ):
            self.add_common_mistake(
                error
            )

    # ==========================================================
    # GRAMMAIRE
    # ==========================================================

    def update_grammar_mastery(
        self,
        rule: str,
        mastery: float,
    ) -> None:

        rule = rule.strip()

        if not rule:
            return

        self.profile.grammar_mastery[
            rule
        ] = mastery

    def add_grammar_history(
        self,
        rule: str,
        correct: bool,
        mastery: float,
    ) -> None:

        self.profile.grammar_history.append(
            {
                "rule": rule,
                "correct": correct,
                "mastery": mastery,
            }
        )

    def get_grammar_mastery(
        self,
        rule: str,
    ) -> float:

        rule = rule.strip()

        return self.profile.grammar_mastery.get(
            rule,
            0.0,
        )