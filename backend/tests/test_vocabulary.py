from app.learning.vocabulary import (
    VocabularyItem,
    VocabularyManager,
)


def test_add_word():

    manager = VocabularyManager()

    item = manager.add_word(
        word="hello",
        translation="bonjour",
        language="anglais",
        level="A1",
    )

    assert isinstance(
        item,
        VocabularyItem,
    )

    assert item.word == "hello"
    assert item.translation == "bonjour"
    assert item.mastery == 0

def test_duplicate_word():

    manager = VocabularyManager()

    first = manager.add_word(
        word="hello",
        translation="bonjour",
        language="anglais",
        level="A1",
    )

    second = manager.add_word(
        word="HELLO",
        translation="salut",
        language="anglais",
        level="A1",
    )

    assert first is second
    assert len(manager.get_all_words()) == 1

def test_correct_answer():

    manager = VocabularyManager()

    manager.add_word(
        word="hello",
        translation="bonjour",
        language="anglais",
        level="A1",
    )

    manager.register_answer(
        "hello",
        True,
    )

    item = manager.get_word("hello")

    assert item is not None
    assert item.review_count == 1
    assert item.correct_count == 1
    assert item.incorrect_count == 0
    assert item.mastery == 100

def test_incorrect_answer():

    manager = VocabularyManager()

    manager.add_word(
        word="hello",
        translation="bonjour",
        language="anglais",
        level="A1",
    )

    manager.register_answer(
        "hello",
        False,
    )

    item = manager.get_word("hello")

    assert item is not None
    assert item.review_count == 1
    assert item.incorrect_count == 1
    assert item.mastery == 0

def test_mastery_calculation():

    manager = VocabularyManager()

    manager.add_word(
        word="hello",
        translation="bonjour",
        language="anglais",
        level="A1",
    )

    manager.register_answer(
        "hello",
        True,
    )

    manager.register_answer(
        "hello",
        True,
    )

    manager.register_answer(
        "hello",
        False,
    )

    item = manager.get_word("hello")

    assert item is not None
    assert item.review_count == 3
    assert item.correct_count == 2
    assert item.incorrect_count == 1
    assert item.mastery == 66.67

def test_words_to_review():

    manager = VocabularyManager()

    manager.add_word(
        word="hello",
        translation="bonjour",
        language="anglais",
        level="A1",
    )

    manager.add_word(
        word="goodbye",
        translation="au revoir",
        language="anglais",
        level="A1",
    )

    manager.register_answer(
        "goodbye",
        True,
    )

    manager.register_answer(
        "goodbye",
        True,
    )

    words = manager.get_words_to_review()

    assert len(words) == 1
    assert words[0].word == "hello"

def test_vocabulary_statistics():

    manager = VocabularyManager()

    manager.add_word(
        word="hello",
        translation="bonjour",
        language="anglais",
        level="A1",
    )

    manager.add_word(
        word="goodbye",
        translation="au revoir",
        language="anglais",
        level="A1",
    )

    manager.register_answer(
        "goodbye",
        True,
    )

    stats = manager.get_statistics()

    assert stats["total_words"] == 2
    assert stats["mastered_words"] == 1
    assert stats["words_to_review"] == 1
    assert stats["average_mastery"] == 50

