from app.learning.grammar import GrammarManager
from app.learning.learner_manager import LearnerProfileManager
from app.learning.recommendation import Recommendation
from app.learning.recommendation import RecommendationEngine
from app.learning.vocabulary import VocabularyManager


def test_recommendation_to_dict():

    recommendation = Recommendation(
        category="grammar",
        target="Past Simple",
        priority=80,
        reason="Maîtrise faible.",
        mastery=20,
        suggested_action="Réviser.",
    )

    data = recommendation.to_dict()

    assert data["category"] == "grammar"
    assert data["target"] == "Past Simple"
    assert data["priority"] == 80
    assert data["mastery"] == 20


def test_grammar_recommendation():

    grammar = GrammarManager()

    rule = grammar.add_rule(
        rule="Past Simple",
        explanation="Actions passées.",
        language="anglais",
        level="A2",
    )

    grammar.register_answer(
        "Past Simple",
        False,
    )

    engine = RecommendationEngine(
        grammar_manager=grammar,
    )

    recommendations = engine.generate()

    assert len(recommendations) == 1
    assert recommendations[0].category == "grammar"
    assert recommendations[0].target == "Past Simple"
    assert recommendations[0].mastery == 0
    assert recommendations[0].priority == 60


def test_mastered_grammar_is_not_recommended():

    grammar = GrammarManager()

    grammar.add_rule(
        rule="Present Simple",
        explanation="Habitudes.",
        language="anglais",
        level="A1",
    )

    for _ in range(4):
        grammar.register_answer(
            "Present Simple",
            True,
        )

    engine = RecommendationEngine(
        grammar_manager=grammar,
    )

    recommendations = engine.generate()

    assert len(recommendations) == 0


def test_vocabulary_recommendation():

    vocabulary = VocabularyManager()

    vocabulary.add_word(
        word="journey",
        translation="voyage",
        language="anglais",
        level="B1",
    )

    vocabulary.register_answer(
        "journey",
        False,
    )

    engine = RecommendationEngine(
        vocabulary_manager=vocabulary,
    )

    recommendations = engine.generate()

    assert len(recommendations) == 1
    assert recommendations[0].category == "vocabulary"
    assert recommendations[0].target == "journey"
    assert recommendations[0].mastery == 0
    assert recommendations[0].priority == 60


def test_competency_recommendation():

    learner = LearnerProfileManager()

    learner.update_competency_scores(
        {
            "grammar": 45,
            "vocabulary": 80,
        }
    )

    engine = RecommendationEngine(
        learner_manager=learner,
    )

    recommendations = engine.generate()

    assert len(recommendations) == 1
    assert recommendations[0].category == "competency"
    assert recommendations[0].target == "grammar"
    assert recommendations[0].mastery == 45
    assert recommendations[0].priority == 33


def test_recommendations_are_sorted_by_priority():

    grammar = GrammarManager()

    grammar.add_rule(
        rule="Present Perfect",
        explanation="Lien passé-présent.",
        language="anglais",
        level="B1",
    )

    grammar.add_rule(
        rule="Past Simple",
        explanation="Actions passées.",
        language="anglais",
        level="A2",
    )

    # Present Perfect : 50 % de maîtrise
    grammar.register_answer(
        "Present Perfect",
        True,
    )

    grammar.register_answer(
        "Present Perfect",
        False,
    )

    # Past Simple : 0 % de maîtrise
    grammar.register_answer(
        "Past Simple",
        False,
    )

    engine = RecommendationEngine(
        grammar_manager=grammar,
    )

    recommendations = engine.generate()

    assert len(recommendations) == 2

    assert (
        recommendations[0].target
        == "Past Simple"
    )

    assert (
        recommendations[0].priority
        > recommendations[1].priority
    )

def test_recommendation_limit():

    grammar = GrammarManager()

    for i in range(10):

        grammar.add_rule(
            rule=f"Grammar Rule {i}",
            explanation="Test.",
            language="anglais",
            level="A1",
        )

    engine = RecommendationEngine(
        grammar_manager=grammar,
    )

    recommendations = engine.generate(
        limit=3,
    )

    assert len(recommendations) == 3


def test_invalid_recommendation_limit():

    engine = RecommendationEngine()

    try:
        engine.generate(limit=0)
        assert False
    except ValueError as exc:
        assert "supérieure ou égale à 1" in str(exc)

def test_weak_point_increases_priority():

    learner = LearnerProfileManager()

    learner.add_weak_point(
        "Past Simple"
    )

    grammar = GrammarManager()

    grammar.add_rule(
        rule="Past Simple",
        explanation="Actions terminées dans le passé.",
        language="anglais",
        level="A2",
    )

    grammar.register_answer(
        "Past Simple",
        False,
    )

    engine = RecommendationEngine(
        learner_manager=learner,
        grammar_manager=grammar,
    )

    recommendations = engine.generate()

    assert len(recommendations) == 1

    recommendation = recommendations[0]

    assert recommendation.target == "Past Simple"

    assert recommendation.category == "grammar"

    assert recommendation.priority == 85

    assert (
        "point faible"
        in recommendation.reason.lower()
    )

def test_common_mistake_increases_priority():

    learner = LearnerProfileManager()

    learner.add_common_mistake(
        "Past Simple"
    )

    grammar = GrammarManager()

    grammar.add_rule(
        rule="Past Simple",
        explanation="Actions terminées dans le passé.",
        language="anglais",
        level="A2",
    )

    grammar.register_answer(
        "Past Simple",
        False,
    )

    engine = RecommendationEngine(
        learner_manager=learner,
        grammar_manager=grammar,
    )

    recommendations = engine.generate()

    grammar_recommendation = next(
        item
        for item in recommendations
        if item.category == "grammar"
    )

    assert grammar_recommendation.priority == 80

def test_goal_increases_priority():

    learner = LearnerProfileManager()

    learner.add_goal(
        "Past Simple"
    )

    grammar = GrammarManager()

    grammar.add_rule(
        rule="Past Simple",
        explanation="Actions terminées dans le passé.",
        language="anglais",
        level="A2",
    )

    grammar.register_answer(
        "Past Simple",
        False,
    )

    engine = RecommendationEngine(
        learner_manager=learner,
        grammar_manager=grammar,
    )

    recommendations = engine.generate()

    grammar_recommendation = next(
        item
        for item in recommendations
        if item.category == "grammar"
    )

    assert grammar_recommendation.priority == 65


def test_duplicate_recommendations_are_merged():

    learner = LearnerProfileManager()

    learner.add_weak_point(
        "Past Simple"
    )

    learner.add_common_mistake(
        "Past Simple"
    )

    grammar = GrammarManager()

    grammar.add_rule(
        rule="Past Simple",
        explanation="Actions terminées dans le passé.",
        language="anglais",
        level="A2",
    )

    grammar.register_answer(
        "Past Simple",
        False,
    )

    engine = RecommendationEngine(
        learner_manager=learner,
        grammar_manager=grammar,
    )

    recommendations = engine.generate(
        limit=10
    )

    past_simple = [
        recommendation
        for recommendation in recommendations
        if recommendation.target.lower()
        == "past simple"
    ]

    assert len(past_simple) == 1

def test_merged_recommendation_keeps_highest_priority():

    learner = LearnerProfileManager()

    learner.add_weak_point(
        "Past Simple"
    )

    grammar = GrammarManager()

    grammar.add_rule(
        rule="Past Simple",
        explanation="Actions terminées dans le passé.",
        language="anglais",
        level="A2",
    )

    grammar.register_answer(
        "Past Simple",
        False,
    )

    engine = RecommendationEngine(
        learner_manager=learner,
        grammar_manager=grammar,
    )

    recommendations = engine.generate(
        limit=10
    )

    past_simple = next(
        recommendation
        for recommendation in recommendations
        if recommendation.target.lower()
        == "past simple"
    )

    assert past_simple.priority == 85


def test_priority_score_basic():

    engine = RecommendationEngine()

    priority = engine._calculate_priority(
        mastery=50,
    )

    assert priority == 30

def test_priority_score_with_weak_point():

    engine = RecommendationEngine()

    priority = engine._calculate_priority(
        mastery=50,
        is_weak_point=True,
    )

    assert priority == 45

def test_priority_score_with_multiple_signals():

    engine = RecommendationEngine()

    priority = engine._calculate_priority(
        mastery=40,
        is_weak_point=True,
        is_common_mistake=True,
        matches_goal=True,
        difficulty=3,
        recent_activity=True,
    )

    assert priority == 73.5

def test_priority_score_is_clamped():

    engine = RecommendationEngine()

    priority = engine._calculate_priority(
        mastery=-50,
        is_weak_point=True,
        is_common_mistake=True,
        matches_goal=True,
        difficulty=5,
        recent_activity=True,
    )

    assert priority == 100

def test_grammar_priority_uses_goal():
    learner = LearnerProfileManager()

    learner.add_goal("Past Simple")

    grammar = GrammarManager()

    grammar.add_rule(
        rule="Past Simple",
        explanation="Actions terminées dans le passé.",
        language="anglais",
        level="A2",
        difficulty=3,
    )

    grammar.register_answer(
        "Past Simple",
        False,
    )

    engine = RecommendationEngine(
        learner_manager=learner,
        grammar_manager=grammar,
    )

    recommendations = engine.generate()

    recommendation = next(
        item
        for item in recommendations
        if item.category == "grammar"
    )

    # mastery = 0
    # base = 60
    # goal = +5
    # difficulty 3 = +2.5
    # weak point = 0
    # mistake = 0
    # recent activity = 0
    # total = 67.5
    assert recommendation.priority == 67.5

    assert "goal" in recommendation.metadata["signals"]
    assert "difficulty" in recommendation.metadata["signals"]

def test_vocabulary_priority_uses_difficulty():
    vocabulary = VocabularyManager()

    vocabulary.add_word(
        word="journey",
        translation="voyage",
        language="anglais",
        level="B1",
        difficulty=5,
    )

    vocabulary.register_answer(
        "journey",
        False,
    )

    engine = RecommendationEngine(
        vocabulary_manager=vocabulary,
    )

    recommendations = engine.generate()

    recommendation = recommendations[0]

    # mastery = 0
    # base = 60
    # difficulty 5 = +5
    # total = 65
    assert recommendation.priority == 65

    assert recommendation.metadata["difficulty"] == 5
    assert "difficulty" in recommendation.metadata["signals"]

def test_vocabulary_priority_uses_weak_point():
    learner = LearnerProfileManager()

    learner.add_weak_point("journey")

    vocabulary = VocabularyManager()

    vocabulary.add_word(
        word="journey",
        translation="voyage",
        language="anglais",
        level="B1",
    )

    vocabulary.register_answer(
        "journey",
        False,
    )

    engine = RecommendationEngine(
        learner_manager=learner,
        vocabulary_manager=vocabulary,
    )

    recommendations = engine._recommend_vocabulary()

    recommendation = recommendations[0]

    # mastery = 0
    # base = 60
    # weak point = +15
    # difficulty = 1 → +0
    # total = 75
    assert recommendation.priority == 75

    assert "weak_point" in recommendation.metadata["signals"]

def test_competency_priority_uses_weak_point():
    learner = LearnerProfileManager()

    learner.update_competency_scores(
        {
            "grammar": 40,
            "vocabulary": 80,
        }
    )

    learner.add_weak_point("grammar")

    engine = RecommendationEngine(
        learner_manager=learner,
    )

    recommendations = engine._recommend_competencies()

    recommendation = recommendations[0]

    # mastery = 40
    # base = 36
    # weak point = +15
    # total = 51
    assert recommendation.priority == 51

    assert "weak_point" in recommendation.metadata["signals"]