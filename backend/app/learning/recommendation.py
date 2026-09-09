from dataclasses import dataclass, field


@dataclass
class Recommendation:
    category: str
    target: str
    priority: float
    reason: str
    mastery: float | None = None
    suggested_action: str = ""
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "target": self.target,
            "priority": self.priority,
            "reason": self.reason,
            "mastery": self.mastery,
            "suggested_action": self.suggested_action,
            "metadata": self.metadata,
        }


class RecommendationEngine:

    def __init__(
        self,
        learner_manager=None,
        vocabulary_manager=None,
        grammar_manager=None,
    ):
        self.learner = learner_manager
        self.vocabulary = vocabulary_manager
        self.grammar = grammar_manager

    def generate(
        self,
        limit: int = 5,
    ) -> list[Recommendation]:

        if limit < 1:
            raise ValueError(
                "La limite doit être supérieure ou égale à 1."
            )

        recommendations = []

        recommendations.extend(
            self._recommend_grammar()
        )

        recommendations.extend(
            self._recommend_vocabulary()
        )

        recommendations.extend(
            self._recommend_competencies()
        )

        recommendations.extend(
            self._recommend_weak_points()
        )

        recommendations.extend(
            self._recommend_common_mistakes()
        )

        recommendations = self._merge_recommendations(
        recommendations
        )

        recommendations.sort(
        key=lambda item: item.priority,
        reverse=True,
        )

        return recommendations[:limit]

        
    # ==========================================================
    # PROFILE HELPERS
    # ==========================================================

    def _get_profile(self) -> dict:

        if self.learner is None:
            return {}

        return self.learner.get_profile()

    def _get_weak_points(self) -> list[str]:

        profile = self._get_profile()

        return profile.get(
            "weak_points",
            [],
        )

    def _get_common_mistakes(self) -> list[str]:

        profile = self._get_profile()

        return profile.get(
            "common_mistakes",
            [],
        )

    def _get_goals(self) -> list[str]:

        profile = self._get_profile()

        return profile.get(
            "goals",
            [],
        )

    # ==========================================================
    # GRAMMAR
    # ==========================================================

    def _recommend_grammar(self) -> list[Recommendation]:
        if self.grammar is None:
            return []

        weak_points = self._get_weak_points()
        common_mistakes = self._get_common_mistakes()
        goals = self._get_goals()

        recommendations = []

        for rule in self.grammar.get_all_rules():

            mastery = rule.mastery

            if mastery >= 80:
                continue

            target_lower = rule.rule.lower()

            is_weak_point = any(
                weak_point.lower() in target_lower
                for weak_point in weak_points
            )

            is_common_mistake = any(
                mistake.lower() in target_lower
                for mistake in common_mistakes
            )

            matches_goal = any(
                goal.lower() in target_lower
                for goal in goals
            )

            difficulty = rule.difficulty

            # Pour le moment, l'activité récente n'est pas encore
            # calculée dynamiquement.
            recent_activity = False

            priority = self._calculate_priority(
                mastery=mastery,
                is_weak_point=is_weak_point,
                is_common_mistake=is_common_mistake,
                matches_goal=matches_goal,
                difficulty=difficulty,
                recent_activity=recent_activity,
            )

            if mastery < 40:
                action = (
                    "Revoir la règle puis effectuer "
                    "plusieurs exercices ciblés."
                )
                reason = "Maîtrise grammaticale très faible."

            elif mastery < 70:
                action = (
                    "Réviser la règle et pratiquer "
                    "avec des exercices."
                )
                reason = "Maîtrise grammaticale insuffisante."

            else:
                action = (
                    "Faire quelques exercices de consolidation."
                )
                reason = "La règle est presque maîtrisée."

            signals = []

            if is_weak_point:
                reason += (
                    " Cette notion fait partie des points faibles."
                )
                signals.append("weak_point")

            if is_common_mistake:
                reason += (
                    " Des erreurs fréquentes y sont associées."
                )
                signals.append("common_mistake")

            if matches_goal:
                signals.append("goal")

            if difficulty > 1:
                signals.append("difficulty")

            recommendations.append(
                Recommendation(
                    category="grammar",
                    target=rule.rule,
                    priority=priority,
                    reason=reason,
                    mastery=mastery,
                    suggested_action=action,
                    metadata={
                        "language": rule.language,
                        "level": rule.level,
                        "category": rule.category,
                        "difficulty": rule.difficulty,
                        "signals": signals,
                    },
                )
            )

        return recommendations
    # ==========================================================
    # VOCABULARY
    # ==========================================================

    def _recommend_vocabulary(self) -> list[Recommendation]:
        if self.vocabulary is None:
            return []

        weak_points = self._get_weak_points()
        common_mistakes = self._get_common_mistakes()
        goals = self._get_goals()

        recommendations = []

        for item in self.vocabulary.get_all_words():

            mastery = item.mastery

            if mastery >= 80:
                continue

            target_lower = item.word.lower()

            is_weak_point = any(
                weak_point.lower() in target_lower
                for weak_point in weak_points
            )

            is_common_mistake = any(
                mistake.lower() in target_lower
                for mistake in common_mistakes
            )

            matches_goal = any(
                goal.lower() in target_lower
                for goal in goals
            )

            difficulty = item.difficulty

            # L'activité récente sera intégrée dans une prochaine étape.
            recent_activity = False

            priority = self._calculate_priority(
                mastery=mastery,
                is_weak_point=is_weak_point,
                is_common_mistake=is_common_mistake,
                matches_goal=matches_goal,
                difficulty=difficulty,
                recent_activity=recent_activity,
            )

            if mastery < 40:
                action = (
                    "Réviser le mot puis le pratiquer "
                    "dans plusieurs phrases."
                )
                reason = "Vocabulaire très peu maîtrisé."

            elif mastery < 70:
                action = (
                    "Faire une révision et quelques "
                    "exercices de rappel."
                )
                reason = "Vocabulaire encore fragile."

            else:
                action = "Faire une révision rapide."
                reason = "Vocabulaire presque maîtrisé."

            signals = []

            if is_weak_point:
                reason += (
                    " Ce vocabulaire fait partie "
                    "des points faibles."
                )
                signals.append("weak_point")

            if is_common_mistake:
                reason += (
                    " Des erreurs fréquentes y sont associées."
                )
                signals.append("common_mistake")

            if matches_goal:
                signals.append("goal")

            if difficulty > 1:
                signals.append("difficulty")

            recommendations.append(
                Recommendation(
                    category="vocabulary",
                    target=item.word,
                    priority=priority,
                    reason=reason,
                    mastery=mastery,
                    suggested_action=action,
                    metadata={
                        "language": item.language,
                        "level": item.level,
                        "category": item.category,
                        "difficulty": item.difficulty,
                        "signals": signals,
                    },
                )
            )

        return recommendations
    # ==========================================================
    # COMPETENCIES
    # ==========================================================

    def _recommend_competencies(self) -> list[Recommendation]:
        if self.learner is None:
            return []

        profile = self.learner.get_profile()

        scores = profile.get(
            "competency_scores",
            {},
        )

        weak_points = self._get_weak_points()
        goals = self._get_goals()

        recommendations = []

        for competency, score in scores.items():

            if score >= 70:
                continue

            competency_lower = competency.lower()

            is_weak_point = any(
                weak_point.lower() in competency_lower
                for weak_point in weak_points
            )

            matches_goal = any(
                goal.lower() in competency_lower
                for goal in goals
            )

            # Les compétences n'ont pas encore de difficulté
            # propre dans le modèle. On utilise donc 1 par défaut.
            difficulty = 1

            # L'activité récente sera intégrée ultérieurement.
            recent_activity = False

            priority = self._calculate_priority(
                mastery=score,
                is_weak_point=is_weak_point,
                is_common_mistake=False,
                matches_goal=matches_goal,
                difficulty=difficulty,
                recent_activity=recent_activity,
            )

            if score < 40:
                action = (
                    f"Travailler intensivement la compétence "
                    f"{competency}."
                )
                reason = (
                    "Score très faible dans cette compétence."
                )
            else:
                action = (
                    f"Pratiquer régulièrement la compétence "
                    f"{competency}."
                )
                reason = (
                    "Score inférieur au niveau attendu."
                )

            signals = []

            if is_weak_point:
                reason += (
                    " Cette compétence fait partie "
                    "des points faibles."
                )
                signals.append("weak_point")

            if matches_goal:
                signals.append("goal")

            recommendations.append(
                Recommendation(
                    category="competency",
                    target=competency,
                    priority=priority,
                    reason=reason,
                    mastery=score,
                    suggested_action=action,
                    metadata={
                        "signals": signals,
                    },
                )
            )

        return recommendations

    # ==========================================================
    # WEAK POINTS
    # ==========================================================

    def _recommend_weak_points(self) -> list[Recommendation]:

        weak_points = self._get_weak_points()

        recommendations = []

        for weak_point in weak_points:

            if not weak_point.strip():
                continue

            recommendations.append(
                Recommendation(
                    category="weak_point",
                    target=weak_point,
                    priority=85,
                    reason=(
                        "Cette notion a été identifiée "
                        "comme un point faible."
                    ),
                    suggested_action=(
                        "Réviser cette notion puis effectuer "
                        "des exercices ciblés."
                    ),
                )
            )

        return recommendations

    # ==========================================================
    # COMMON MISTAKES
    # ==========================================================

    def _recommend_common_mistakes(
        self,
    ) -> list[Recommendation]:

        mistakes = self._get_common_mistakes()

        recommendations = []

        for mistake in mistakes:

            if not mistake.strip():
                continue

            recommendations.append(
                Recommendation(
                    category="mistake",
                    target=mistake,
                    priority=80,
                    reason=(
                        "Cette erreur apparaît "
                        "régulièrement dans les réponses."
                    ),
                    suggested_action=(
                        "Analyser l'erreur puis effectuer "
                        "des exercices de correction ciblés."
                    ),
                )
            )

        return recommendations


    def _merge_recommendations(
        self,
        recommendations: list[Recommendation],
    ) -> list[Recommendation]:

        merged: dict[str, Recommendation] = {}

        for recommendation in recommendations:

            key = self._get_recommendation_key(
                recommendation
            )

            if key not in merged:
                merged[key] = recommendation
                continue

            existing = merged[key]

            # Garder la catégorie pédagogique principale
            if (
                existing.category in {
                    "weak_point",
                    "mistake",
                }
                and recommendation.category
                in {
                    "grammar",
                    "vocabulary",
                    "competency",
                }
            ):
                existing.category = recommendation.category

            # Garder la meilleure priorité
            existing.priority = max(
                existing.priority,
                recommendation.priority,
            )

            # Fusionner les raisons
            if recommendation.reason:
                if recommendation.reason not in existing.reason:
                    existing.reason += (
                        " " + recommendation.reason
                    )

            # Fusionner les actions
            if recommendation.suggested_action:
                if (
                    recommendation.suggested_action
                    not in existing.suggested_action
                ):
                    existing.suggested_action += (
                        " "
                        + recommendation.suggested_action
                    )

            # Fusionner les métadonnées
            existing.metadata.update(
                recommendation.metadata
            )

        return list(merged.values())

    def _get_recommendation_key(
        self,
        recommendation: Recommendation,
    ) -> str:

        return recommendation.target.strip().lower()

    def _calculate_priority(
        self,
        mastery: float,
        is_weak_point: bool = False,
        is_common_mistake: bool = False,
        matches_goal: bool = False,
        difficulty: int = 1,
        recent_activity: bool = False,
    ) -> float:

        mastery = max(
            0,
            min(mastery, 100),
        )

        base_score = (
            (100 - mastery) * 0.60
        )

        score = base_score

        if is_weak_point:
            score += 15

        if is_common_mistake:
            score += 10

        if matches_goal:
            score += 5

        difficulty = max(
            1,
            min(difficulty, 5),
        )

        difficulty_bonus = (
                (difficulty - 1) * 1.25
            
        )

        score += difficulty_bonus

        if recent_activity:
            score += 5

        return round(
            min(score, 100),
            2,
        )