from app.learning.grammar import GrammarManager


def test_add_rule():
    manager = GrammarManager()

    rule = manager.add_rule(
        rule="Present Simple",
        explanation="Utilisé pour parler des habitudes.",
        language="anglais",
        level="A1",
        category="tenses",
    )

    assert rule.rule == "Present Simple"
    assert rule.language == "anglais"
    assert rule.level == "A1"


def test_duplicate_rule():
    manager = GrammarManager()

    first = manager.add_rule(
        rule="Present Simple",
        explanation="Habitudes.",
        language="anglais",
        level="A1",
    )

    second = manager.add_rule(
        rule="present simple",
        explanation="Autre explication.",
        language="anglais",
        level="A1",
    )

    assert first is second
    assert len(manager.rules) == 1


def test_correct_answer():
    manager = GrammarManager()

    rule = manager.add_rule(
        rule="Present Simple",
        explanation="Habitudes.",
        language="anglais",
        level="A1",
    )

    manager.register_answer(
        "Present Simple",
        True,
    )

    assert rule.review_count == 1
    assert rule.correct_count == 1
    assert rule.incorrect_count == 0
    assert rule.mastery == 100


def test_incorrect_answer():
    manager = GrammarManager()

    rule = manager.add_rule(
        rule="Past Simple",
        explanation="Actions passées.",
        language="anglais",
        level="A2",
    )

    manager.register_answer(
        "Past Simple",
        False,
    )

    assert rule.review_count == 1
    assert rule.correct_count == 0
    assert rule.incorrect_count == 1
    assert rule.mastery == 0


def test_mastery_calculation():
    manager = GrammarManager()

    rule = manager.add_rule(
        rule="Present Perfect",
        explanation="Lien entre passé et présent.",
        language="anglais",
        level="B1",
    )

    manager.register_answer("Present Perfect", True)
    manager.register_answer("Present Perfect", True)
    manager.register_answer("Present Perfect", False)
    manager.register_answer("Present Perfect", True)

    assert rule.review_count == 4
    assert rule.correct_count == 3
    assert rule.incorrect_count == 1
    assert rule.mastery == 75


def test_rules_to_review():
    manager = GrammarManager()

    weak_rule = manager.add_rule(
        rule="Conditionnel",
        explanation="Expression d'une condition.",
        language="français",
        level="B1",
    )

    strong_rule = manager.add_rule(
        rule="Présent",
        explanation="Action actuelle.",
        language="français",
        level="A1",
    )

    manager.register_answer("Conditionnel", False)

    for _ in range(4):
        manager.register_answer("Présent", True)

    rules = manager.get_rules_to_review()

    assert weak_rule in rules
    assert strong_rule not in rules


def test_grammar_statistics():
    manager = GrammarManager()

    rule1 = manager.add_rule(
        rule="Present Simple",
        explanation="Habitudes.",
        language="anglais",
        level="A1",
    )

    rule2 = manager.add_rule(
        rule="Past Simple",
        explanation="Actions passées.",
        language="anglais",
        level="A2",
    )

    manager.register_answer("Present Simple", True)
    manager.register_answer("Past Simple", False)

    stats = manager.get_statistics()

    assert stats["total_rules"] == 2
    assert stats["mastered_rules"] == 1
    assert stats["rules_to_review"] == 1
    assert stats["average_mastery"] == 50