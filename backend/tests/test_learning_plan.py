from app.learning.learning_plan import (
    LearningPlan,
    LearningPlanEngine,
    LearningPlanItem,
)
from app.learning.recommendation import (
    Recommendation,
)


def test_learning_plan_item_to_dict():
    item = LearningPlanItem(
    order=1,
    category="grammar",
    target="Past Simple",
    activity_type="lesson",
    priority=85,
    activity_priority=85,
    estimated_minutes=10,
    suggested_action="Réviser la règle.",
    reason="Maîtrise insuffisante.",
    mastery=40,
)

    data = item.to_dict()

    assert data["order"] == 1
    assert data["category"] == "grammar"
    assert data["target"] == "Past Simple"
    assert data["activity_type"] == "lesson"
    assert data["priority"] == 85
    assert data["mastery"] == 40


def test_learning_plan_add_item():
    plan = LearningPlan()

    item = plan.add_item(
    category="grammar",
    target="Past Simple",
    activity_type="lesson",
    priority=80,
    activity_priority=80,
    estimated_minutes=10,
)

    assert len(plan.items) == 1
    assert item.order == 1
    assert item.target == "Past Simple"


def test_learning_plan_orders_items():
    plan = LearningPlan()

    first = plan.add_item(
        category="grammar",
        target="Past Simple",
        activity_type="lesson",
        priority=80,
    )

    second = plan.add_item(
        category="vocabulary",
        target="Travel",
        activity_type="review",
        priority=60,
    )

    assert first.order == 1
    assert second.order == 2


def test_learning_plan_count():
    plan = LearningPlan()

    plan.add_item(
        category="grammar",
        target="Past Simple",
        activity_type="lesson",
        priority=80,
    )

    plan.add_item(
        category="vocabulary",
        target="Travel",
        activity_type="review",
        priority=60,
    )

    assert plan.get_item_count() == 2


def test_learning_plan_to_dict():
    plan = LearningPlan()

    plan.add_item(
        category="grammar",
        target="Past Simple",
        activity_type="lesson",
        priority=80,
    )

    data = plan.to_dict()

    assert data["count"] == 1
    assert len(data["items"]) == 1


def test_learning_plan_clear():
    plan = LearningPlan()

    plan.add_item(
        category="grammar",
        target="Past Simple",
        activity_type="lesson",
        priority=80,
    )

    plan.clear()

    assert plan.get_item_count() == 0


class FakeRecommendationEngine:

    def generate(self, limit=5):
        recommendations = [
            Recommendation(
                category="grammar",
                target="Past Simple",
                priority=90,
                reason="Grammaire faible.",
                mastery=20,
                suggested_action="Réviser.",
            ),
            Recommendation(
                category="vocabulary",
                target="Travel",
                priority=70,
                reason="Vocabulaire fragile.",
                mastery=50,
                suggested_action="Réviser.",
            ),
        ]

        return recommendations[:limit]


def test_learning_plan_engine_generates_plan():
    engine = LearningPlanEngine(
        recommendation_engine=FakeRecommendationEngine()
    )

    plan = engine.generate()

    assert plan.get_item_count() > 0


def test_learning_plan_engine_grammar_creates_activities():
    engine = LearningPlanEngine(
        recommendation_engine=FakeRecommendationEngine()
    )

    plan = engine.generate()

    grammar_items = [
        item
        for item in plan.items
        if item.category == "grammar"
    ]

    assert len(grammar_items) == 3

    activity_types = {
        item.activity_type
        for item in grammar_items
    }

    assert "lesson" in activity_types
    assert "exercise" in activity_types
    assert "review" in activity_types


def test_learning_plan_engine_vocabulary_creates_activities():
    engine = LearningPlanEngine(
        recommendation_engine=FakeRecommendationEngine()
    )

    plan = engine.generate()

    vocabulary_items = [
        item
        for item in plan.items
        if item.category == "vocabulary"
    ]

    assert len(vocabulary_items) == 2

    activity_types = {
        item.activity_type
        for item in vocabulary_items
    }

    assert "review" in activity_types
    assert "exercise" in activity_types


def test_learning_plan_is_sorted_by_priority():
    engine = LearningPlanEngine(
        recommendation_engine=FakeRecommendationEngine()
    )

    plan = engine.generate()

    priorities = [
        item.priority
        for item in plan.items
    ]

    assert priorities == sorted(
        priorities,
        reverse=True,
    )


def test_learning_plan_order_is_sequential():
    engine = LearningPlanEngine(
        recommendation_engine=FakeRecommendationEngine()
    )

    plan = engine.generate()

    orders = [
        item.order
        for item in plan.items
    ]

    assert orders == list(
        range(1, len(orders) + 1)
    )


def test_learning_plan_invalid_limit():
    engine = LearningPlanEngine(
        recommendation_engine=FakeRecommendationEngine()
    )

    try:
        engine.generate(limit=0)
        assert False
    except ValueError as exc:
        assert str(exc) == (
            "La limite doit être supérieure ou égale à 1."
        )

def test_activity_duration():
    engine = LearningPlanEngine()

    assert engine._get_activity_duration(
        "lesson"
    ) == 10

    assert engine._get_activity_duration(
        "exercise"
    ) == 15

    assert engine._get_activity_duration(
        "review"
    ) == 5


def test_activity_priority():
    engine = LearningPlanEngine()

    assert engine._calculate_activity_priority(
        100,
        "lesson",
    ) == 100

    assert engine._calculate_activity_priority(
        100,
        "exercise",
    ) == 95

    assert engine._calculate_activity_priority(
        100,
        "review",
    ) == 85


def test_plan_respects_available_time():
    engine = LearningPlanEngine(
        recommendation_engine=FakeRecommendationEngine()
    )

    plan = engine.generate(
        available_minutes=30
    )

    total_minutes = sum(
        item.estimated_minutes
        for item in plan.items
    )

    assert total_minutes <= 30


def test_plan_can_fit_fifteen_minutes():
    engine = LearningPlanEngine(
        recommendation_engine=FakeRecommendationEngine()
    )

    plan = engine.generate(
        available_minutes=15
    )

    total_minutes = sum(
        item.estimated_minutes
        for item in plan.items
    )

    assert total_minutes <= 15


def test_plan_rejects_invalid_available_time():
    engine = LearningPlanEngine(
        recommendation_engine=FakeRecommendationEngine()
    )

    try:
        engine.generate(
            available_minutes=0
        )
        assert False
    except ValueError as exc:
        assert str(exc) == (
            "Le temps disponible doit être "
            "supérieur ou égal à 1 minute."
        )