import pytest

from app.learning.exercise_generator import (
    ExerciseGenerator,
)


@pytest.mark.asyncio
async def test_parse_valid_exercises():

    generator = ExerciseGenerator()

    response = """
    {
        "exercises": [
            {
                "id": "ex1",
                "exercise_type": "multiple_choice",
                "question": "What is the opposite of big?",
                "level": "A1",
                "skill": "vocabulary",
                "options": [
                    "small",
                    "long",
                    "tall"
                ],
                "expected_answer": "small",
                "difficulty": 1
            }
        ]
    }
    """

    data = generator._parse_response(response)

    assert "exercises" in data
    assert len(data["exercises"]) == 1
    assert (
        data["exercises"][0]["expected_answer"]
        == "small"
    )

def test_invalid_json():

    generator = ExerciseGenerator()

    with pytest.raises(RuntimeError):
        generator._parse_response(
            "ceci n'est pas du JSON"
        )

def test_missing_exercises():

    generator = ExerciseGenerator()

    response = """
    {
        "lesson": "test"
    }
    """

    with pytest.raises(RuntimeError):
        generator._parse_response(response)

def test_build_exercises():

    generator = ExerciseGenerator()

    data = {
        "exercises": [
            {
                "id": "ex1",
                "exercise_type": "fill_blank",
                "question": "I ___ a student.",
                "level": "A1",
                "skill": "grammar",
                "options": [],
                "expected_answer": "am",
                "difficulty": 1,
            }
        ]
    }

    exercises = generator._build_exercises(
        data,
        language="anglais",
        level="A1",
        skill="grammar",
    )

    assert len(exercises) == 1

    exercise = exercises[0]

    assert exercise.id == "ex1"
    assert exercise.exercise_type == "fill_blank"
    assert exercise.expected_answer == "am"