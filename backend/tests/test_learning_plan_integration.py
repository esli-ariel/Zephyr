from app.learning.learner_manager import LearnerProfileManager
from app.learning.learning_engine import LearningEngine


def test_learning_plan_with_weak_grammar():
    learner = LearnerProfileManager()

    learner.set_name("Test")
    learner.set_target_language("anglais")
    learner.set_level("A2")

    learner.add_weak_point("Past Simple")

    engine = LearningEngine(
        learner_manager=learner
    )

    engine.add_grammar_rule(
        rule="Past Simple",
        explanation="Utilisation du passé simple en anglais.",
        category="tenses",
        examples=[
            "I worked yesterday.",
            "She visited London last week.",
        ],
        difficulty=2,
    )

    plan = engine.get_learning_plan(
        limit=5
    )

    assert "count" in plan
    assert "items" in plan

    assert plan["count"] > 0

    grammar_items = [
        item
        for item in plan["items"]
        if item["target"] == "Past Simple"
    ]

    assert len(grammar_items) > 0

    activity_types = {
        item["activity_type"]
        for item in grammar_items
    }

    assert "lesson" in activity_types
    assert "exercise" in activity_types
    assert "review" in activity_types


def test_learning_plan_with_weak_vocabulary():
    learner = LearnerProfileManager()

    learner.set_target_language("anglais")
    learner.set_level("A2")

    learner.add_weak_point("travel")

    engine = LearningEngine(
        learner_manager=learner
    )

    engine.add_vocabulary(
        word="travel",
        translation="voyager",
        category="travel",
        examples=[
            "I like to travel."
        ],
        difficulty=2,
    )

    plan = engine.get_learning_plan(
        limit=5
    )

    assert plan["count"] > 0

    vocabulary_items = [
        item
        for item in plan["items"]
        if item["category"] == "vocabulary"
    ]

    assert len(vocabulary_items) > 0


def test_learning_plan_with_competency():
    learner = LearnerProfileManager()

    learner.set_target_language("anglais")
    learner.set_level("A2")

    learner.update_competency_scores(
        {
            "grammar": 35,
            "vocabulary": 80,
        }
    )

    engine = LearningEngine(
        learner_manager=learner
    )

    plan = engine.get_learning_plan(
        limit=5
    )

    assert plan["count"] > 0

    competency_items = [
        item
        for item in plan["items"]
        if item["category"] == "competency"
    ]

    assert len(competency_items) > 0

    activity_types = {
        item["activity_type"]
        for item in competency_items
    }

    assert "practice" in activity_types
    assert "exercise" in activity_types