import pytest

from app.learning.assessment_evaluator import (
    AssessmentEvaluator,
)


@pytest.mark.asyncio
async def test_closed_answer_correct():
    evaluator = AssessmentEvaluator()

    result = await evaluator.evaluate_answer(
        {
            "question_id": 1,
            "answer": "small",
        }
    )

    assert result["score"] == 100
    assert result["correct"] is True


@pytest.mark.asyncio
async def test_closed_answer_wrong():
    evaluator = AssessmentEvaluator()

    result = await evaluator.evaluate_answer(
        {
            "question_id": 1,
            "answer": "long",
        }
    )

    assert result["score"] == 0
    assert result["correct"] is False