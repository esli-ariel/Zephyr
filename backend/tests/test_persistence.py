import sqlite3
from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app import main
from app.agent.zephyr import ZephyrAgent
from app.learning.adaptive_assessment import AdaptiveAssessment
from app.learning.exercise import Exercise
from app.learning.lesson import Lesson, LessonSection
from app.persistence import StateStore, capture_state


@pytest.fixture
def boot(tmp_path, monkeypatch):
    monkeypatch.setattr(main.settings, "persistence_enabled", True)
    monkeypatch.setattr(main.settings, "database_path", str(tmp_path / "data" / "state.sqlite3"))

    @contextmanager
    def start():
        agent = ZephyrAgent()
        assessment = AdaptiveAssessment()
        monkeypatch.setattr(main, "zephyr", agent)
        monkeypatch.setattr(main, "adaptive_assessment", assessment)
        with TestClient(main.app) as client:
            yield client, agent, assessment

    return start


def test_state_survives_application_restart(boot, monkeypatch):
    with boot() as (client, agent, assessment):
        assert client.put("/api/learner/profile", json={
            "name": "Éloïse", "target_language": "anglais", "level": "A1",
            "goal": "voyager",
        }).status_code == 200

        async def extract(message):
            return {}

        async def chat(messages):
            return "Hello!"

        monkeypatch.setattr(agent.profile_extractor, "extract", extract)
        monkeypatch.setattr(agent.llm, "chat", chat)
        assert client.post("/api/chat", json={"message": "Bonjour"}).status_code == 200
        assert client.post("/api/learning/vocabulary", json={
            "word": "hello", "translation": "bonjour",
        }).status_code == 200
        assert client.post("/api/learning/vocabulary/answer", json={
            "word": "hello", "correct": True,
        }).status_code == 200
        assert client.post("/api/learning/grammar", json={
            "rule": "Present Simple", "explanation": "Habitudes",
        }).status_code == 200
        assert client.post("/api/learning/grammar/answer", json={
            "rule": "Present Simple", "correct": False,
        }).status_code == 200

        async def lesson(*args, **kwargs):
            return Lesson(
                id="lesson-1", title="Greetings", language="anglais", level="A1",
                topic="Greetings", sections=[LessonSection("Hello", "Bonjour", "vocabulary")],
            )

        async def exercises(*args, **kwargs):
            return [Exercise(
                id="exercise-1", exercise_type="fill_blank", question="I ___ a student.",
                level="A1", skill="grammar", expected_answer="am",
            )]

        monkeypatch.setattr(agent.learning_engine.lesson_generator, "generate", lesson)
        monkeypatch.setattr(agent.learning_engine.exercise_generator, "generate", exercises)
        assert client.post("/api/learning/lesson", json={"topic": "Greetings"}).status_code == 200
        assert client.post("/api/learning/exercises", json={
            "topic": "Present Simple", "skill": "grammar",
        }).status_code == 200
        plan = client.get("/api/learning/plan").json()
        item_id = plan["items"][0]["id"]
        assert client.post(f"/api/learning/plan/items/{item_id}/complete", json={"score": 80}).status_code == 200
        assert client.post("/api/assessment/start").status_code == 200
        assert client.post("/api/assessment/answer", json={"answer": "small"}).status_code == 200
        saved = capture_state(agent, assessment)

    with boot() as (client, agent, assessment):
        assert capture_state(agent, assessment) == saved
        assert agent.learning_engine.lessons[0].sections[0].content == "Bonjour"
        assert client.get("/api/learner/profile").json()["name"] == "Éloïse"
        assert client.get("/api/chat/memory").json()["message_count"] == 2
        assert client.get("/api/learning/vocabulary/statistics").json()["average_mastery"] == 100
        assert client.get("/api/learning/grammar/statistics").json()["total_rules"] == 1
        active = client.get("/api/learning/plan/current").json()
        assert active["items"][0]["id"] == item_id
        assert active["items"][0]["completed"] is True
        assert client.get("/api/assessment/progress").json()["answered"] == 1
        # L'exercice restauré reste corrigeable, avec son corrigé privé.
        assert client.post("/api/learning/exercises/exercise-1/answer", json={"answer": "am"}).json()["evaluation"]["correct"] is True
        assert client.get("/api/learning/recommendations").json()["count"] > 0


def test_deletions_survive_restart(boot, monkeypatch):
    with boot() as (client, agent, _):
        async def extract(message):
            return {"name": "Test"}

        async def chat(messages):
            return "Hello"

        monkeypatch.setattr(agent.profile_extractor, "extract", extract)
        monkeypatch.setattr(agent.llm, "chat", chat)
        assert client.post("/api/chat", json={"message": "Hello"}).status_code == 200
        assert client.delete("/api/chat/memory").status_code == 200
        assert client.delete("/api/learner/profile").status_code == 200
    with boot() as (client, _, _):
        assert client.get("/api/learner/profile").json()["name"] is None
        assert client.get("/api/chat/memory").json()["message_count"] == 0


def test_failed_save_rolls_back_and_returns_503(boot, monkeypatch):
    with boot() as (client, agent, _):
        assert client.put("/api/learner/profile", json={"name": "Avant"}).status_code == 200

        def fail(snapshot):
            raise sqlite3.OperationalError("disk full")

        monkeypatch.setattr(main.app.state.store, "save", fail)
        response = client.put("/api/learner/profile", json={"name": "Après"})
        assert response.status_code == 503
        assert agent.get_learner_profile()["name"] == "Avant"
    with boot() as (client, _, _):
        assert client.get("/api/learner/profile").json()["name"] == "Avant"


def test_failed_llm_request_does_not_save_partial_mutations(boot, monkeypatch):
    with boot() as (client, agent, assessment):
        async def extract(message):
            return {"name": "À annuler"}

        async def fail(messages):
            raise RuntimeError("provider unavailable")

        monkeypatch.setattr(agent.profile_extractor, "extract", extract)
        monkeypatch.setattr(agent.llm, "chat", fail)
        before = capture_state(agent, assessment)
        assert client.post("/api/chat", json={"message": "Bonjour"}).status_code == 502
        assert capture_state(agent, assessment) == before
        assert main.app.state.store.load() is None


def test_corrupt_state_is_rejected_without_overwriting_database(tmp_path):
    store = StateStore(str(tmp_path / "state.sqlite3"))
    with sqlite3.connect(store.path) as connection:
        connection.execute("INSERT INTO app_state VALUES (1, ?)", ('{"version":999}',))
    with pytest.raises(ValidationError):
        store.load()
    with sqlite3.connect(store.path) as connection:
        assert connection.execute("SELECT payload FROM app_state").fetchone()[0] == '{"version":999}'


def test_backup_restores_the_saved_state_and_refuses_overwrite(tmp_path):
    from app.backup import backup_database

    source = StateStore(str(tmp_path / "state.sqlite3"))
    agent = ZephyrAgent()
    agent.learner.set_name("Sauvegardé")
    snapshot = capture_state(agent, AdaptiveAssessment())
    source.save(snapshot)
    destination = tmp_path / "backup.sqlite3"
    backup_database(str(source.path), str(destination))
    assert StateStore(str(destination)).load() == snapshot
    with pytest.raises(FileExistsError):
        backup_database(str(source.path), str(destination))
    assert StateStore(str(destination)).load() == snapshot


def test_backup_missing_source_does_not_create_empty_files(tmp_path):
    from app.backup import backup_database

    source = tmp_path / "missing.sqlite3"
    destination = tmp_path / "backup.sqlite3"
    with pytest.raises(sqlite3.OperationalError):
        backup_database(str(source), str(destination))
    assert not source.exists()
    assert not destination.exists()
