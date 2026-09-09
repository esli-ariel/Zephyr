from app.learning.learner_manager import LearnerProfileManager
from app.learning.learning_engine import LearningEngine


def test_update_grammar_mastery():
    learner = LearnerProfileManager()

    learner.update_grammar_mastery(
        "Present Simple",
        85,
    )

    assert learner.get_grammar_mastery(
        "Present Simple"
    ) == 85


def test_grammar_history():
    learner = LearnerProfileManager()

    learner.add_grammar_history(
        rule="Past Simple",
        correct=False,
        mastery=0,
    )

    profile = learner.get_profile()

    assert len(profile["grammar_history"]) == 1
    assert profile["grammar_history"][0]["rule"] == "Past Simple"
    assert profile["grammar_history"][0]["correct"] is False
    assert profile["grammar_history"][0]["mastery"] == 0


def test_grammar_answer_updates_profile():
    learner = LearnerProfileManager()

    learner.set_target_language("anglais")
    learner.set_level("A1")

    engine = LearningEngine(
        learner_manager=learner
    )

    engine.add_grammar_rule(
        rule="Present Simple",
        explanation="Utilisé pour parler des habitudes.",
    )

    engine.register_grammar_answer(
        "Present Simple",
        True,
    )

    profile = learner.get_profile()

    assert profile["grammar_mastery"]["Present Simple"] == 100
    assert len(profile["grammar_history"]) == 1


def test_grammar_mastery_changes_with_answers():
    learner = LearnerProfileManager()

    learner.set_target_language("anglais")
    learner.set_level("B1")

    engine = LearningEngine(
        learner_manager=learner
    )

    engine.add_grammar_rule(
        rule="Present Perfect",
        explanation="Lien entre passé et présent.",
    )

    engine.register_grammar_answer(
        "Present Perfect",
        True,
    )

    engine.register_grammar_answer(
        "Present Perfect",
        False,
    )

    profile = learner.get_profile()

    assert profile["grammar_mastery"]["Present Perfect"] == 50
    assert len(profile["grammar_history"]) == 2