from app.learning.grammar import GrammarManager
from app.learning.learner_manager import LearnerProfileManager
from app.learning.learning_engine import LearningEngine


def test_learning_engine_initializes_grammar_manager():
    learner = LearnerProfileManager()

    engine = LearningEngine(
        learner_manager=learner
    )

    assert isinstance(
        engine.grammar,
        GrammarManager,
    )


def test_add_grammar_rule_requires_language():
    learner = LearnerProfileManager()

    engine = LearningEngine(
        learner_manager=learner
    )

    try:
        engine.add_grammar_rule(
            rule="Present Simple",
            explanation="Habitudes.",
        )
        assert False
    except ValueError as exc:
        assert "langue cible" in str(exc)


def test_add_grammar_rule_requires_level():
    learner = LearnerProfileManager()

    learner.set_target_language("anglais")

    engine = LearningEngine(
        learner_manager=learner
    )

    try:
        engine.add_grammar_rule(
            rule="Present Simple",
            explanation="Habitudes.",
        )
        assert False
    except ValueError as exc:
        assert "niveau" in str(exc)


def test_add_grammar_rule():
    learner = LearnerProfileManager()

    learner.set_target_language("anglais")
    learner.set_level("A1")

    engine = LearningEngine(
        learner_manager=learner
    )

    rule = engine.add_grammar_rule(
        rule="Present Simple",
        explanation="Utilisé pour parler des habitudes.",
        category="tenses",
        examples=[
            "I work every day.",
            "She works every day.",
        ],
        difficulty=1,
    )

    assert rule.rule == "Present Simple"
    assert rule.language == "anglais"
    assert rule.level == "A1"
    assert rule.category == "tenses"


def test_register_grammar_answer():
    learner = LearnerProfileManager()

    learner.set_target_language("anglais")
    learner.set_level("A1")

    engine = LearningEngine(
        learner_manager=learner
    )

    rule = engine.add_grammar_rule(
        rule="Present Simple",
        explanation="Habitudes.",
    )

    engine.register_grammar_answer(
        "Present Simple",
        True,
    )

    assert rule.review_count == 1
    assert rule.correct_count == 1
    assert rule.mastery == 100


def test_get_grammar_statistics():
    learner = LearnerProfileManager()

    learner.set_target_language("anglais")
    learner.set_level("A1")

    engine = LearningEngine(
        learner_manager=learner
    )

    engine.add_grammar_rule(
        rule="Present Simple",
        explanation="Habitudes.",
    )

    engine.add_grammar_rule(
        rule="Past Simple",
        explanation="Actions passées.",
    )

    engine.register_grammar_answer(
        "Present Simple",
        True,
    )

    engine.register_grammar_answer(
        "Past Simple",
        False,
    )

    stats = engine.get_grammar_statistics()

    assert stats["total_rules"] == 2
    assert stats["mastered_rules"] == 1
    assert stats["rules_to_review"] == 1
    assert stats["average_mastery"] == 50