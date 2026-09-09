import pytest

from app.learning.exercise import Exercise
from app.learning.exercise_evaluator import (
    ExerciseEvaluator,
)


@pytest.mark.asyncio
async def test_multiple_choice_correct():

    evaluator = ExerciseEvaluator()

    exercise = Exercise(
        id="ex1",
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

    result = await evaluator.evaluate(
        exercise,
        "small",
    )

    assert result["score"] == 100
    assert result["correct"] is True

@pytest.mark.asyncio
async def test_multiple_choice_wrong():

    evaluator = ExerciseEvaluator()

    exercise = Exercise(
        id="ex1",
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

    result = await evaluator.evaluate(
        exercise,
        "long",
    )

    assert result["score"] == 0
    assert result["correct"] is False
    assert len(result["weak_points"]) == 1

@pytest.mark.asyncio
async def test_fill_blank():

    evaluator = ExerciseEvaluator()

    exercise = Exercise(
        id="ex2",
        exercise_type="fill_blank",
        question="I ___ a student.",
        level="A1",
        skill="grammar",
        expected_answer="am",
    )

    result = await evaluator.evaluate(
        exercise,
        "AM",
    )

    assert result["score"] == 100
    assert result["correct"] is True

def test_parse_llm_result():

    evaluator = ExerciseEvaluator()

    response = """
    {
        "score": 85,
        "correct": true,
        "feedback": "Good answer.",
        "errors": [],
        "strengths": ["grammar"],
        "weak_points": []
    }
    """

    result = evaluator._parse_llm_result(
        response
    )

    assert result["score"] == 85
    assert result["correct"] is True
    assert result["strengths"] == ["grammar"]

def test_invalid_llm_result():

    evaluator = ExerciseEvaluator()

    with pytest.raises(RuntimeError):
        evaluator._parse_llm_result(
            "not valid json"
        )

def test_missing_llm_field():

    evaluator = ExerciseEvaluator()

    response = """
    {
        "score": 80,
        "correct": true
    }
    """

    with pytest.raises(RuntimeError):
        evaluator._parse_llm_result(
            response
        )

@pytest.mark.asyncio
async def test_empty_answer():

    evaluator = ExerciseEvaluator()

    exercise = Exercise(
        id="ex1",
        exercise_type="multiple_choice",
        question="Test",
        level="A1",
        skill="vocabulary",
        expected_answer="hello",
    )

    with pytest.raises(ValueError):
        await evaluator.evaluate(
            exercise,
            "   ",
        )

