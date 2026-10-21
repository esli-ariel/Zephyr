import httpx
import pytest
from fastapi.testclient import TestClient

from app import main
from app.agent.zephyr import ZephyrAgent


@pytest.fixture
def learning(monkeypatch):
    agent = ZephyrAgent()
    agent.learner.set_target_language("anglais")
    agent.learner.set_level("A1")
    monkeypatch.setattr(main, "zephyr", agent)
    with TestClient(main.app) as client:
        yield client, agent


def test_generated_exercises_hide_answers_and_accept_correction(learning, monkeypatch):
    client, agent = learning
    exercise = agent.learning_engine.create_exercise(
        exercise_type="fill_blank", question="I ___ a student.",
        level="A1", skill="grammar", expected_answer="am",
    )

    async def generate(**kwargs):
        return [exercise]

    monkeypatch.setattr(agent.learning_engine.exercise_generator, "generate", generate)
    response = client.post("/api/learning/exercises", json={
        "topic": "Present simple", "skill": "grammar", "count": 1,
    })
    assert response.status_code == 200
    public = response.json()["exercises"][0]
    assert "expected_answer" not in public
    assert exercise.expected_answer == "am"
    response = client.post(
        f"/api/learning/exercises/{public['id']}/answer", json={"answer": "is"},
    )
    assert response.status_code == 200
    assert response.json()["evaluation"]["correct"] is False
    profile = client.get("/api/learner/profile").json()
    assert "grammar" in profile["weak_points"]
    assert profile["common_mistakes"]
    assert client.get("/api/learning/recommendations").json()["count"] > 0
    assert client.get("/api/learning/plan").json()["count"] > 0


def test_grammar_review_updates_profile_and_recommendations(learning):
    client, _ = learning
    response = client.post("/api/learning/grammar", json={
        "rule": "Present Simple", "explanation": "Habitudes.",
    })
    assert response.status_code == 200
    assert client.get("/api/learning/grammar").json()["count"] == 1
    assert client.get("/api/learning/grammar/review").json()["count"] == 1
    assert client.get("/api/learning/recommendations").json()["count"] == 1
    response = client.post("/api/learning/grammar/answer", json={
        "rule": " present SIMPLE ", "correct": True,
    })
    assert response.status_code == 200
    assert response.json()["mastery"] == 100
    profile = client.get("/api/learner/profile").json()
    assert profile["grammar_mastery"]["Present Simple"] == 100
    assert len(profile["grammar_history"]) == 1
    assert client.get("/api/learning/grammar/statistics").json()["mastered_rules"] == 1
    assert client.get("/api/learning/grammar/review").json()["count"] == 0
    assert client.get("/api/learning/recommendations").json()["count"] == 0
    assert client.get("/api/learning/plan").json()["count"] == 0


def test_vocabulary_review_updates_mastery(learning):
    client, _ = learning
    assert client.post("/api/learning/vocabulary", json={
        "word": "hello", "translation": "bonjour",
    }).status_code == 200
    for correct in (True, False):
        response = client.post("/api/learning/vocabulary/answer", json={
            "word": " HELLO ", "correct": correct,
        })
        assert response.status_code == 200
    assert response.json()["mastery"] == 50
    assert response.json()["review_count"] == 2
    assert client.get("/api/learning/vocabulary/statistics").json()["average_mastery"] == 50


@pytest.mark.parametrize("path,body", [
    ("exercises/missing/answer", {"answer": "test"}),
    ("grammar/answer", {"rule": "missing", "correct": True}),
    ("vocabulary/answer", {"word": "missing", "correct": True}),
])
def test_unknown_review_target_returns_404(learning, path, body):
    client, agent = learning
    assert client.post(f"/api/learning/{path}", json=body).status_code == 404
    assert agent.learner.get_profile()["grammar_history"] == []


@pytest.mark.parametrize("path,body", [
    ("grammar/answer", {"rule": "test", "correct": "false"}),
    ("vocabulary/answer", {"word": "test", "correct": 1}),
    ("grammar", {"rule": "   ", "explanation": "test"}),
])
def test_invalid_review_input_returns_422(learning, path, body):
    client, _ = learning
    assert client.post(f"/api/learning/{path}", json=body).status_code == 422


@pytest.mark.parametrize("answer,status", [("am", 200), ("   ", 400), ("", 422)])
def test_exercise_answer_validation(learning, answer, status):
    client, agent = learning
    exercise = agent.learning_engine.create_exercise(
        exercise_type="fill_blank", question="I ___ a student.",
        level="A1", skill="grammar", expected_answer="am",
    )
    response = client.post(
        f"/api/learning/exercises/{exercise.id}/answer", json={"answer": answer},
    )
    assert response.status_code == status
    if status == 200:
        assert response.json()["evaluation"]["correct"] is True


@pytest.mark.parametrize("error", [RuntimeError("provider error"), httpx.ReadTimeout("timeout")])
def test_correction_failure_keeps_profile_unchanged(learning, monkeypatch, error):
    client, agent = learning
    exercise = agent.learning_engine.create_exercise(
        exercise_type="open", question="Introduce yourself.", level="A1", skill="writing",
    )

    async def fail(*args):
        raise error

    monkeypatch.setattr(agent.learning_engine.exercise_evaluator, "evaluate", fail)
    before = agent.learner.get_profile()
    response = client.post(
        f"/api/learning/exercises/{exercise.id}/answer", json={"answer": "Hello"},
    )
    assert response.status_code == 502
    assert agent.learner.get_profile() == before
