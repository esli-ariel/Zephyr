from app.learning.learner import LearnerProfile


class LearnerProfileManager:
    """
    Gestionnaire du profil d'apprentissage de Zéphyr.
    """

    def __init__(self):
        self.profile = LearnerProfile()

    def set_name(self, name: str) -> None:
        self.profile.name = name.strip()

    def set_target_language(self, language: str) -> None:
        self.profile.target_language = language.strip()

    def set_level(self, level: str) -> None:
        self.profile.level = level.strip()

    def add_goal(self, goal: str) -> None:
        goal = goal.strip()

        if goal and goal not in self.profile.goals:
            self.profile.goals.append(goal)

    def add_weak_point(self, weak_point: str) -> None:
        weak_point = weak_point.strip()

        if weak_point and weak_point not in self.profile.weak_points:
            self.profile.weak_points.append(weak_point)

    def add_vocabulary(self, word: str) -> None:
        word = word.strip()

        if word and word not in self.profile.learned_vocabulary:
            self.profile.learned_vocabulary.append(word)

    def add_common_mistake(self, mistake: str) -> None:
        mistake = mistake.strip()

        if mistake and mistake not in self.profile.common_mistakes:
            self.profile.common_mistakes.append(mistake)

    def get_profile(self) -> dict:
        return self.profile.to_dict()

    def clear_profile(self) -> None:
        self.profile = LearnerProfile()

    def apply_assessment_result(
            self,
            result: dict,
        ) -> None:
        """
        Applique les résultats d'une évaluation
        au profil de l'apprenant.
        """

        estimated_level = result.get(
            "estimated_level"
        )

        if estimated_level:
            self.set_level(
                estimated_level
            )

        for weak_point in result.get(
            "weak_points",
            [],
        ):
            self.add_weak_point(
                weak_point
            )

        for strength in result.get(
            "strengths",
            [],
        ):
            if strength not in (
                self.profile.common_mistakes
            ):
                # Les forces ne sont pas encore
                # stockées dans le profil.
                pass

        for error in result.get(
            "errors",
            [],
        ):
            self.add_common_mistake(
                error
            )

    def update_competency_scores(
        self,
        scores: dict,
        ) -> None:
        """
        Enregistre les scores par compétence.
        """

        for competency, score in scores.items():

            if score is None:
                continue

            self.profile.competency_scores[
                competency
            ] = score

    def add_assessment_result(
        self,
        result: dict,
    ) -> None:
        """
        Enregistre une évaluation dans l'historique.

        Une même évaluation ne peut être enregistrée
        qu'une seule fois.
        """

        assessment_id = result.get(
            "assessment_id"
        )

        if assessment_id:

            for existing in (
                self.profile.assessment_history
            ):
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
        """
        Applique les résultats de l'évaluation
        au profil de l'apprenant.
        """

        estimated_level = result.get(
            "estimated_level"
        )

        if estimated_level:
            self.set_level(
                estimated_level
            )

        self.update_competency_scores(
            result.get(
                "competency_scores",
                {},
            )
        )

        for weak_point in result.get(
            "weak_points",
            [],
        ):
            self.add_weak_point(
                weak_point
            )

        for error in result.get(
            "errors",
            [],
        ):
            self.add_common_mistake(
                error
            )

        self.add_assessment_result(
            result
        )

    def apply_exercise_result(
        self,
        result: dict,
    ) -> None:
        """
        Intègre les résultats d'un exercice
        dans le profil de l'apprenant.
        """

        for weak_point in result.get(
            "weak_points",
            [],
        ):
            self.add_weak_point(
                weak_point
            )

        for error in result.get(
            "errors",
            [],
        ):
            self.add_common_mistake(
                error
            )

    def add_learned_vocabulary(
        self,
        word: str,
        ) -> None:
        """
        Ajoute un mot au vocabulaire appris.
        """

        word = word.strip()

        if not word:
            return

        if word not in self.profile.learned_vocabulary:
            self.profile.learned_vocabulary.append(
                word
            )