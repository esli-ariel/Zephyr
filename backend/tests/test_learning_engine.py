from app.learning.exercise import Exercise
from app.learning.lesson import Lesson
from app.learning.learning_engine import LearningEngine
from app.learning.learner_manager import LearnerProfileManager
from app.learning.exercise import Exercise


def test_create_lesson():
    engine = LearningEngine()

    lesson = engine.create_lesson(
        title="Se présenter en anglais",
        language="anglais",
        level="A1",
        topic="Présentation",
        objectives=[
            "Se présenter",
            "Dire son nom",
        ],
    )

    assert isinstance(lesson, Lesson)
    assert lesson.title == "Se présenter en anglais"
    assert lesson.language == "anglais"
    assert lesson.level == "A1"
    assert len(lesson.objectives) == 2


def test_add_lesson_section():
    engine = LearningEngine()

    lesson = engine.create_lesson(
        title="Greetings",
        language="anglais",
        level="A1",
        topic="Greetings",
    )

    lesson.add_section(
        title="Introduction",
        content="Hello means bonjour.",
        section_type="introduction",
    )

    assert len(lesson.sections) == 1
    assert lesson.sections[0].title == "Introduction"


def test_create_exercise():
    engine = LearningEngine()

    exercise = engine.create_exercise(
        exercise_type="multiple_choice",
        question="What is the opposite of big?",
        level="A1",
        skill="vocabulary",
        options=[
            "small",
            "long",
            "tall",
        ],
        expected_answer="small",
    )

    assert isinstance(exercise, Exercise)
    assert exercise.level == "A1"
    assert exercise.skill == "vocabulary"
    assert exercise.expected_answer == "small"


def test_learning_engine_stores_content():
    engine = LearningEngine()

    engine.create_lesson(
        title="Lesson 1",
        language="anglais",
        level="A1",
        topic="Vocabulary",
    )

    engine.create_exercise(
        exercise_type="fill_blank",
        question="I ___ a student.",
        level="A1",
        skill="grammar",
        expected_answer="am",
    )

    assert len(engine.get_lessons()) == 1
    assert len(engine.get_exercises()) == 1


def test_lesson_to_dict():
    engine = LearningEngine()

    lesson = engine.create_lesson(
        title="Present Simple",
        language="anglais",
        level="A1",
        topic="Grammar",
    )

    lesson.add_section(
        title="Grammar",
        content="The present simple...",
        section_type="grammar",
    )

    data = lesson.to_dict()

    assert data["title"] == "Present Simple"
    assert len(data["sections"]) == 1
    assert data["sections"][0]["section_type"] == "grammar"


def test_exercise_to_dict():
    engine = LearningEngine()

    exercise = engine.create_exercise(
        exercise_type="translation",
        question="Translate: Bonjour",
        level="A1",
        skill="translation",
        expected_answer="Hello",
    )

    data = exercise.to_dict()

    assert data["exercise_type"] == "translation"
    assert data["expected_answer"] == "Hello"


def test_clear_learning_engine():
    engine = LearningEngine()

    engine.create_lesson(
        title="Test",
        language="anglais",
        level="A1",
        topic="Test",
    )

    engine.create_exercise(
        exercise_type="writing",
        question="Write a sentence.",
        level="A1",
        skill="expression",
    )

    engine.clear()

    assert len(engine.get_lessons()) == 0
    assert len(engine.get_exercises()) == 0

def test_learning_engine_uses_learner_profile():
    learner = LearnerProfileManager()

    learner.set_name("Ariel")
    learner.set_target_language("anglais")
    learner.set_level("A2")
    learner.add_goal("Parler avec mes clients")
    learner.add_weak_point("Grammaire")

    engine = LearningEngine(
        learner_manager=learner
    )

    context = engine.get_learning_context()

    assert context["name"] == "Ariel"
    assert context["target_language"] == "anglais"
    assert context["level"] == "A2"
    assert "Parler avec mes clients" in context["goals"]
    assert "Grammaire" in context["weak_points"]

def test_learning_engine_without_learner():
    engine = LearningEngine()

    context = engine.get_learning_context()

    assert context["name"] is None
    assert context["target_language"] is None
    assert context["level"] is None
    assert context["goals"] == []

import pytest

from app.learning.learner_manager import LearnerProfileManager
from app.learning.learning_engine import LearningEngine


@pytest.mark.asyncio
async def test_generate_lesson_uses_learner_profile(
    monkeypatch,
):
    learner = LearnerProfileManager()

    learner.set_name("Ariel")
    learner.set_target_language("anglais")
    learner.set_level("A2")
    learner.add_goal(
        "Parler avec mes clients"
    )
    learner.add_weak_point(
        "Grammaire"
    )

    engine = LearningEngine(
        learner_manager=learner
    )

    async def fake_generate(
        language,
        level,
        topic,
        objectives,
        weak_points,
        common_mistakes,
    ):
        return engine.create_lesson(
            title="Communication avec les clients",
            language=language,
            level=level,
            topic=topic,
            objectives=objectives,
        )

    monkeypatch.setattr(
        engine.lesson_generator,
        "generate",
        fake_generate,
    )

    lesson = await engine.generate_lesson(
        "Communication professionnelle"
    )

    assert lesson.language == "anglais"
    assert lesson.level == "A2"
    assert lesson.topic == (
        "Communication professionnelle"
    )
    assert (
        "Parler avec mes clients"
        in lesson.objectives
    )

@pytest.mark.asyncio
async def test_generate_exercises_uses_learner_profile(
    monkeypatch,
):
    learner = LearnerProfileManager()

    learner.set_name("Ariel")
    learner.set_target_language("anglais")
    learner.set_level("A2")
    learner.add_goal(
        "Parler avec mes clients"
    )
    learner.add_weak_point(
        "Grammaire"
    )

    engine = LearningEngine(
        learner_manager=learner
    )

    async def fake_generate(
        language,
        level,
        topic,
        skill,
        count,
        objectives,
        weak_points,
    ):
        return [
            Exercise(
                id="ex1",
                exercise_type="multiple_choice",
                question="Choose the correct answer.",
                level=level,
                skill=skill,
                options=[
                    "A",
                    "B",
                    "C",
                ],
                expected_answer="A",
                difficulty=1,
            )
        ]

    monkeypatch.setattr(
        engine.exercise_generator,
        "generate",
        fake_generate,
    )

    exercises = await engine.generate_exercises(
        topic="Communication avec un client",
        skill="grammar",
        count=1,
    )

    assert len(exercises) == 1
    assert exercises[0].level == "A2"
    assert exercises[0].skill == "grammar"

def test_add_vocabulary_updates_profile():

    learner = LearnerProfileManager()

    learner.set_target_language(
        "anglais"
    )

    learner.set_level("A1")

    engine = LearningEngine(
        learner_manager=learner
    )

    item = engine.add_vocabulary(
        word="customer",
        translation="client",
        category="business",
    )

    assert item.word == "customer"

    profile = learner.get_profile()

    assert "customer" in (
        profile["learned_vocabulary"]
    )

def test_learning_engine_has_recommendation_engine():
    learner = LearnerProfileManager()

    engine = LearningEngine(
        learner_manager=learner,
    )

    assert engine.recommendation is not None
    assert engine.recommendation.learner is learner
    assert engine.recommendation.vocabulary is engine.vocabulary
    assert engine.recommendation.grammar is engine.grammar

def test_learning_engine_returns_recommendations():
    learner = LearnerProfileManager()

    learner.update_competency_scores(
        {
            "grammar": 40,
            "vocabulary": 80,
        }
    )

    engine = LearningEngine(
        learner_manager=learner,
    )

    recommendations = engine.get_recommendations()

    assert isinstance(recommendations, list)
    assert len(recommendations) == 1

    recommendation = recommendations[0]

    assert recommendation["category"] == "competency"
    assert recommendation["target"] == "grammar"
    assert recommendation["mastery"] == 40