from app.learning.assessment import (
    AssessmentSession,
)


def test_assessment_starts_at_a1():
    session = AssessmentSession()

    question = (
        session.get_current_question()
    )

    assert question is not None
    assert question["level"] == "A1"


def test_correct_answers_advance_level():
    session = AssessmentSession()

    session.submit_answer("answer 1")
    session.record_evaluation(100)

    session.submit_answer("answer 2")
    session.record_evaluation(100)

    session.submit_answer("answer 3")
    result = session.record_evaluation(100)

    assert result["action"] == "advance"
    assert session.current_level == "A2"


def test_low_score_stops_assessment():
    session = AssessmentSession()

    session.submit_answer("answer 1")
    session.record_evaluation(20)

    session.submit_answer("answer 2")
    session.record_evaluation(30)

    session.submit_answer("answer 3")
    result = session.record_evaluation(20)

    assert result["action"] == "stop"
    assert session.finished is True


def test_intermediate_score_continues():
    session = AssessmentSession()

    session.submit_answer("answer 1")
    session.record_evaluation(60)

    session.submit_answer("answer 2")
    session.record_evaluation(60)

    session.submit_answer("answer 3")
    result = session.record_evaluation(60)

    assert result["action"] == "continue"
    assert session.finished is False
    assert session.current_level == "A1"


def test_progress_is_updated():
    session = AssessmentSession()

    session.submit_answer("answer")
    session.record_evaluation(100)

    progress = session.get_progress()

    assert progress["answered"] == 1
    assert progress[
        "current_level_answered"
    ] == 1


def test_reset_clears_session():
    session = AssessmentSession()

    session.submit_answer("answer")
    session.record_evaluation(100)

    session.reset()

    assert session.current_level == "A1"
    assert len(session.answers) == 0
    assert session.finished is False