from app.learning.learner_manager import LearnerProfileManager
from app.learning.recommendation import RecommendationEngine
from app.learning.learning_engine import LearningEngine


def test_profile_contains_strengths():
    manager = LearnerProfileManager()

    manager.add_strength(
        "bonne compréhension orale"
    )

    profile = manager.get_profile()

    assert "strengths" in profile

    assert (
        "bonne compréhension orale"
        in profile["strengths"]
    )


def test_strength_is_not_duplicated():
    manager = LearnerProfileManager()

    manager.add_strength("vocabulaire")

    manager.add_strength("vocabulaire")

    profile = manager.get_profile()

    assert profile["strengths"].count(
        "vocabulaire"
    ) == 1


def test_apply_exercise_result_updates_profile():
    manager = LearnerProfileManager()

    result = {
        "competency_scores": {
            "vocabulary": 72,
            "grammar": 55,
        },
        "weak_points": [
            "past tense",
        ],
        "strengths": [
            "vocabulary",
        ],
        "errors": [
            "confusion between do and make",
        ],
    }

    manager.apply_exercise_result(
        result
    )

    profile = manager.get_profile()

    assert profile[
        "competency_scores"
    ]["vocabulary"] == 72

    assert profile[
        "competency_scores"
    ]["grammar"] == 55

    assert "past tense" in profile[
        "weak_points"
    ]

    assert "vocabulary" in profile[
        "strengths"
    ]

    assert (
        "confusion between do and make"
        in profile["common_mistakes"]
    )


def test_apply_assessment_result_updates_profile():
    manager = LearnerProfileManager()

    result = {
        "assessment_id": "assessment-001",
        "estimated_level": "B1",
        "validated_levels": [
            "A2",
            "B1",
        ],
        "overall_score": 68,
        "competency_scores": {
            "grammar": 60,
            "vocabulary": 75,
        },
        "weak_points": [
            "past tense",
        ],
        "strengths": [
            "vocabulary",
        ],
        "errors": [
            "irregular verbs",
        ],
    }

    manager.apply_assessment_result(
        result
    )

    profile = manager.get_profile()

    assert profile["level"] == "B1"

    assert profile[
        "competency_scores"
    ]["grammar"] == 60

    assert profile[
        "competency_scores"
    ]["vocabulary"] == 75

    assert "past tense" in profile[
        "weak_points"
    ]

    assert "vocabulary" in profile[
        "strengths"
    ]

    assert "irregular verbs" in profile[
        "common_mistakes"
    ]

    assert len(
        profile["assessment_history"]
    ) == 1


def test_assessment_result_is_not_duplicated():
    manager = LearnerProfileManager()

    result = {
        "assessment_id": "assessment-001",
        "estimated_level": "B1",
        "overall_score": 70,
    }

    manager.apply_assessment_result(
        result
    )

    manager.apply_assessment_result(
        result
    )

    profile = manager.get_profile()

    assert len(
        profile["assessment_history"]
    ) == 1


def test_learning_context_contains_strengths():
    manager = LearnerProfileManager()

    manager.set_name("Esli")

    manager.set_target_language(
        "anglais"
    )

    manager.set_level("B1")

    manager.add_goal(
        "conversation"
    )

    manager.add_weak_point(
        "past tense"
    )

    manager.add_strength(
        "vocabulary"
    )

    engine = LearningEngine(
        learner_manager=manager
    )

    context = engine.get_learning_context()

    assert context["name"] == "Esli"

    assert (
        context["target_language"]
        == "anglais"
    )

    assert context["level"] == "B1"

    assert "conversation" in context[
        "goals"
    ]

    assert "past tense" in context[
        "weak_points"
    ]

    assert "vocabulary" in context[
        "strengths"
    ]


def test_recommendation_engine_reads_profile():
    manager = LearnerProfileManager()

    manager.set_target_language(
        "anglais"
    )

    manager.set_level("B1")

    manager.add_goal(
        "conversation"
    )

    manager.add_weak_point(
        "grammar"
    )

    manager.add_strength(
        "vocabulary"
    )

    manager.update_competency_scores(
        {
            "grammar": 30,
            "vocabulary": 80,
        }
    )

    recommendation_engine = (
        RecommendationEngine(
            learner_manager=manager
        )
    )

    recommendations = (
        recommendation_engine.generate(
            limit=10
        )
    )

    competency_recommendations = [
        recommendation
        for recommendation in recommendations
        if recommendation.category
        == "competency"
    ]

    assert any(
        recommendation.target == "grammar"
        for recommendation in competency_recommendations
    )

    grammar_recommendation = next(
        recommendation
        for recommendation in competency_recommendations
        if recommendation.target == "grammar"
    )

    assert "weak_point" in grammar_recommendation.metadata[
        "signals"
    ]