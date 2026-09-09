from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class LearningPlanItem:
    """
    Représente une activité dans un plan d'apprentissage.
    """

    order: int
    category: str
    target: str
    activity_type: str
    priority: float
    activity_priority: float
    estimated_minutes: int
    suggested_action: str = ""
    reason: str = ""
    mastery: float | None = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """
        Convertit l'activité en dictionnaire.
        """

        return {
            "order": self.order,
            "category": self.category,
            "target": self.target,
            "activity_type": self.activity_type,
            "priority": self.priority,
            "activity_priority": self.activity_priority,
            "estimated_minutes": self.estimated_minutes,
            "suggested_action": self.suggested_action,
            "reason": self.reason,
            "mastery": self.mastery,
            "metadata": self.metadata,
        }


@dataclass
class LearningPlan:
    """
    Représente un plan personnalisé d'apprentissage.
    """

    items: list[LearningPlanItem] = field(default_factory=list)
    recommendation_count: int = 0

    def add_item(
        self,
        category: str,
        target: str,
        activity_type: str,
        priority: float,
        activity_priority: float | None = None,
        estimated_minutes: int | None = None,
        suggested_action: str = "",
        reason: str = "",
        mastery: float | None = None,
        metadata: dict | None = None,
    ) -> LearningPlanItem:
        """
        Ajoute une activité au plan.

        Les valeurs de priorité d'activité et de durée peuvent
        être fournies explicitement ou utiliser des valeurs
        par défaut.
        """

        if activity_priority is None:
            activity_priority = priority

        if estimated_minutes is None:
            estimated_minutes = 10

        if estimated_minutes < 1:
            raise ValueError(
                "La durée estimée doit être supérieure ou égale à 1 minute."
            )

        item = LearningPlanItem(
            order=len(self.items) + 1,
            category=category,
            target=target,
            activity_type=activity_type,
            priority=priority,
            activity_priority=activity_priority,
            estimated_minutes=estimated_minutes,
            suggested_action=suggested_action,
            reason=reason,
            mastery=mastery,
            metadata=metadata or {},
        )

        self.items.append(item)

        return item
            

    def get_items(self) -> list[LearningPlanItem]:
        """
        Retourne les activités du plan.
        """

        return self.items

    def get_item_count(self) -> int:
        """
        Retourne le nombre d'activités.
        """

        return len(self.items)

    def clear(self) -> None:
        """
        Supprime toutes les activités du plan.
        """

        self.items.clear()

    def to_dict(self) -> dict:
        """
        Convertit le plan en dictionnaire.
        """

        return {
            "count": len(self.items),
            "recommendation_count": self.recommendation_count,
            "items": [
                item.to_dict()
                for item in self.items
            ],
        }


class LearningPlanEngine:
    """
    Génère un plan d'apprentissage personnalisé
    à partir des recommandations pédagogiques.
    """

    ACTIVITY_DURATIONS = {
        "lesson": 10,
        "exercise": 15,
        "review": 5,
        "practice": 15,
        "correction": 10,
    }

    ACTIVITY_PRIORITY_MULTIPLIERS = {
        "lesson": 1.00,
        "exercise": 0.95,
        "review": 0.85,
        "practice": 0.90,
        "correction": 0.90,
    }

    def __init__(self, recommendation_engine=None):
        self.recommendation = recommendation_engine

    def generate(
        self,
        limit: int = 5,
        available_minutes: int | None = None,
    ) -> LearningPlan:
        """
        Génère un plan d'apprentissage personnalisé.

        Args:
            limit:
                Nombre maximum de recommandations à utiliser.

            available_minutes:
                Temps disponible pour la session.
                Si None, aucune contrainte de temps n'est appliquée.

        Returns:
            LearningPlan
        """

        if limit < 1:
            raise ValueError(
                "La limite doit être supérieure ou égale à 1."
            )

        if (
            available_minutes is not None
            and available_minutes < 1
        ):
            raise ValueError(
                "Le temps disponible doit être supérieur ou égal à 1 minute."
            )

        if self.recommendation is None:
            return LearningPlan()

        recommendations = self.recommendation.generate(
            limit=limit
        )

        plan = LearningPlan(
            recommendation_count=len(recommendations)
        )

        for recommendation in recommendations:
            self._add_activities_for_recommendation(
                plan,
                recommendation,
            )

        self._reorder(plan)

        self._filter_by_available_time(
            plan,
            available_minutes,
        )

        return plan

    def _add_activities_for_recommendation(
        self,
        plan: LearningPlan,
        recommendation,
    ) -> None:
        """
        Détermine les activités à créer selon
        la catégorie de la recommandation.
        """

        category = recommendation.category

        if category == "grammar":
            self._add_grammar_activities(
                plan,
                recommendation,
            )

        elif category == "vocabulary":
            self._add_vocabulary_activities(
                plan,
                recommendation,
            )

        elif category == "competency":
            self._add_competency_activities(
                plan,
                recommendation,
            )

        elif category == "weak_point":
            self._add_weak_point_activities(
                plan,
                recommendation,
            )

        elif category == "mistake":
            self._add_mistake_activities(
                plan,
                recommendation,
            )

    def _add_grammar_activities(
        self,
        plan: LearningPlan,
        recommendation,
    ) -> None:
        """
        Génère les activités adaptées à une recommandation
        de grammaire.
        """

        mastery = recommendation.mastery

        if mastery is None or mastery < 40:
            activity_types = [
                "lesson",
                "exercise",
                "review",
            ]

        elif mastery < 70:
            activity_types = [
                "review",
                "exercise",
            ]

        else:
            activity_types = [
                "exercise",
            ]

        for activity_type in activity_types:
            self._add_activity(
                plan,
                recommendation,
                activity_type,
            )

    def _add_vocabulary_activities(
        self,
        plan: LearningPlan,
        recommendation,
    ) -> None:
        """
        Génère les activités adaptées à une recommandation
        de vocabulaire.
        """

        mastery = recommendation.mastery

        if mastery is None or mastery < 40:
            activity_types = [
                "lesson",
                "review",
                "exercise",
            ]

        elif mastery < 70:
            activity_types = [
                "review",
                "exercise",
            ]

        else:
            activity_types = [
                "review",
            ]

        for activity_type in activity_types:
            self._add_activity(
                plan,
                recommendation,
                activity_type,
            )

    def _add_competency_activities(
        self,
        plan: LearningPlan,
        recommendation,
    ) -> None:
        """
        Génère les activités pour une compétence faible.
        """

        self._add_activity(
            plan,
            recommendation,
            "practice",
        )

        self._add_activity(
            plan,
            recommendation,
            "exercise",
        )

    def _add_weak_point_activities(
        self,
        plan: LearningPlan,
        recommendation,
    ) -> None:
        """
        Génère les activités pour un point faible.
        """

        self._add_activity(
            plan,
            recommendation,
            "review",
        )

        self._add_activity(
            plan,
            recommendation,
            "exercise",
        )

    def _add_mistake_activities(
        self,
        plan: LearningPlan,
        recommendation,
    ) -> None:
        """
        Génère les activités pour une erreur fréquente.
        """

        self._add_activity(
            plan,
            recommendation,
            "correction",
        )

        self._add_activity(
            plan,
            recommendation,
            "exercise",
        )

    def _add_activity(
        self,
        plan: LearningPlan,
        recommendation,
        activity_type: str,
    ) -> None:
        """
        Ajoute une activité au plan à partir
        d'une recommandation.
        """

        activity_priority = self._calculate_activity_priority(
            recommendation.priority,
            activity_type,
        )

        estimated_minutes = self._get_activity_duration(
            activity_type
        )

        metadata = getattr(
            recommendation,
            "metadata",
            {},
        )

        plan.add_item(
            category=recommendation.category,
            target=recommendation.target,
            activity_type=activity_type,
            priority=recommendation.priority,
            activity_priority=activity_priority,
            estimated_minutes=estimated_minutes,
            suggested_action=recommendation.suggested_action,
            reason=recommendation.reason,
            mastery=recommendation.mastery,
            metadata=metadata.copy(),
        )

    def _get_activity_duration(
        self,
        activity_type: str,
    ) -> int:
        """
        Retourne la durée estimée d'une activité.
        """

        return self.ACTIVITY_DURATIONS.get(
            activity_type,
            10,
        )

    def _calculate_activity_priority(
        self,
        recommendation_priority: float,
        activity_type: str,
    ) -> float:
        """
        Calcule la priorité réelle d'une activité.

        La priorité de la recommandation est ajustée
        selon le type d'activité.
        """

        multiplier = self.ACTIVITY_PRIORITY_MULTIPLIERS.get(
            activity_type,
            1.0,
        )

        return round(
            recommendation_priority * multiplier,
            2,
        )

    def _reorder(
        self,
        plan: LearningPlan,
    ) -> None:
        """
        Trie les activités par priorité décroissante
        et recalcule leur ordre.
        """

        plan.items.sort(
            key=lambda item: item.priority,
            reverse=True,
        )

        for index, item in enumerate(
            plan.items,
            start=1,
        ):
            item.order = index

    def _filter_by_available_time(
        self,
        plan: LearningPlan,
        available_minutes: int | None,
    ) -> None:
        """
        Filtre les activités afin de respecter
        le temps disponible.
        """

        if available_minutes is None:
            return

        if available_minutes < 1:
            raise ValueError(
                "Le temps disponible doit être supérieur ou égal à 1 minute."
            )

        selected_items = []
        total_minutes = 0

        for item in plan.items:
            if (
                total_minutes + item.estimated_minutes
                <= available_minutes
            ):
                selected_items.append(item)

                total_minutes += (
                    item.estimated_minutes
                )

        plan.items = selected_items

        for index, item in enumerate(
            plan.items,
            start=1,
        ):
            item.order = index