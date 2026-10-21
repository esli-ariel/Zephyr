import asyncio
import sqlite3
from uuid import UUID, uuid4

import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app import main
from app.agent.zephyr import ZephyrAgent
from app.learning.adaptive_assessment import AdaptiveAssessment
from app.learning.exercise import Exercise
from app.persistence import LEGACY_LEARNER_ID, StateStore, capture_state


@pytest.fixture
def database(tmp_path, monkeypatch):
    path = tmp_path / "learners.sqlite3"
    monkeypatch.setattr(main.settings, "persistence_enabled", True)
    monkeypatch.setattr(main.settings, "database_path", str(path))
    return path


def create(client):
    response = client.post("/api/learners")
    assert response.status_code == 201
    learner_id = response.json()["learner_id"]
    assert str(UUID(learner_id)) == learner_id
    assert response.headers["X-Learner-ID"] == learner_id
    return {"X-Learner-ID": learner_id}


def test_two_learners_are_isolated_and_restored(database, monkeypatch):
    saved = {}
    with TestClient(main.app) as client:
        alice, bob = create(client), create(client)
        for headers, name, level, word in [
            (alice, "Alice", "A1", "hello"), (bob, "Bob", "B1", "travel"),
        ]:
            assert client.put("/api/learner/profile", headers=headers, json={
                "name": name, "target_language": "anglais", "level": level,
            }).status_code == 200
            session = main.app.state.learners.get(headers["X-Learner-ID"])

            async def extract(message):
                return {}

            async def chat(messages):
                return "Hello!"

            monkeypatch.setattr(session.agent.profile_extractor, "extract", extract)
            monkeypatch.setattr(session.agent.llm, "chat", chat)
            assert client.post("/api/chat", headers=headers, json={"message": name}).status_code == 200
            assert client.post("/api/learning/vocabulary", headers=headers, json={
                "word": word, "translation": name,
            }).status_code == 200
            assert client.post("/api/learning/grammar", headers=headers, json={
                "rule": name + " rule", "explanation": name,
            }).status_code == 200
            assert client.post("/api/assessment/start", headers=headers).status_code == 200
        bob_session = main.app.state.learners.get(bob["X-Learner-ID"])
        bob_before = capture_state(bob_session.agent, bob_session.assessment)
        # Même les mutations les plus profondes restent dans le compte sélectionné.
        assert client.post("/api/assessment/answer", headers=alice, json={"answer": "small"}).status_code == 200
        assert client.post("/api/learning/vocabulary/answer", headers=alice, json={
            "word": "hello", "correct": True,
        }).status_code == 200
        assert client.post("/api/learning/grammar/answer", headers=alice, json={
            "rule": "Alice rule", "correct": False,
        }).status_code == 200
        assert client.post("/api/learning/vocabulary/answer", headers=bob, json={
            "word": "hello", "correct": True,
        }).status_code == 404
        assert client.post("/api/learning/grammar/answer", headers=bob, json={
            "rule": "Alice rule", "correct": True,
        }).status_code == 404

        agent = main.app.state.learners.get(alice["X-Learner-ID"]).agent

        async def generate(**kwargs):
            return [Exercise(
                id="alice-exercise", exercise_type="fill_blank", question="I ___ here.",
                level="A1", skill="grammar", expected_answer="am",
            )]

        monkeypatch.setattr(agent.learning_engine.exercise_generator, "generate", generate)
        assert client.post("/api/learning/exercises", headers=alice, json={
            "topic": "Present Simple", "skill": "grammar",
        }).status_code == 200
        assert client.post("/api/learning/exercises/alice-exercise/answer", headers=bob, json={"answer": "am"}).status_code == 404
        plan = client.get("/api/learning/plan", headers=alice).json()
        item_id = plan["items"][0]["id"]
        assert client.post(f"/api/learning/plan/items/{item_id}/complete", headers=alice, json={"score": 90}).status_code == 200
        assert client.post(f"/api/learning/plan/items/{item_id}/complete", headers=bob, json={"score": 0}).status_code == 404
        assert capture_state(bob_session.agent, bob_session.assessment) == bob_before
        for headers in (alice, bob):
            session = main.app.state.learners.get(headers["X-Learner-ID"])
            saved[session.learner_id] = capture_state(session.agent, session.assessment)

    with TestClient(main.app) as client:
        assert main.app.state.learners.sessions == {}  # Restauration à la demande.
        for headers, name, word in [(alice, "Alice", "hello"), (bob, "Bob", "travel")]:
            assert client.get("/api/learner/profile", headers=headers).json()["name"] == name
            assert client.get("/api/learning/vocabulary", headers=headers).json()["vocabulary"][0]["word"] == word
            session = main.app.state.learners.get(headers["X-Learner-ID"])
            assert capture_state(session.agent, session.assessment) == saved[session.learner_id]
        assert client.get("/api/learning/plan/current", headers=alice).json()["items"][0]["completed"] is True
        assert client.get("/api/learning/plan/current", headers=bob).status_code == 404
        assert client.get("/api/assessment/progress", headers=alice).json()["answered"] == 1
        assert client.get("/api/assessment/progress", headers=bob).json()["answered"] == 0
        assert client.delete("/api/learner/profile", headers=alice).status_code == 200
        assert client.delete("/api/chat/memory", headers=alice).status_code == 200
        assert client.delete("/api/assessment", headers=alice).status_code == 200
        bob_session = main.app.state.learners.get(bob["X-Learner-ID"])
        assert capture_state(bob_session.agent, bob_session.assessment) == saved[bob_session.learner_id]

    with TestClient(main.app) as client:
        assert client.get("/api/learner/profile", headers=alice).json()["name"] is None
        assert client.get("/api/chat/memory", headers=alice).json()["message_count"] == 0
        assert client.get("/api/learner/profile", headers=bob).json()["name"] == "Bob"
        assert client.get("/api/chat/memory", headers=bob).json()["message_count"] == 2


@pytest.mark.parametrize("headers,status", [
    ({}, 400), ({"X-Learner-ID": ""}, 400),
    ({"X-Learner-ID": "../../someone"}, 400),
    ({"X-Learner-ID": str(uuid4())}, 404),
    ([("X-Learner-ID", str(uuid4())), ("X-Learner-ID", str(uuid4()))], 400),
])
def test_missing_invalid_or_unknown_id_cannot_read_or_write(database, headers, status):
    with TestClient(main.app) as client:
        assert client.get("/api/learner/profile", headers=headers).status_code == status
        assert client.put("/api/learner/profile", headers=headers, json={"name": "Intruder"}).status_code == status
        assert main.app.state.learners.sessions == {}
        assert client.get("/health").status_code == 200


def test_save_failure_is_limited_to_selected_learner(database, monkeypatch):
    with TestClient(main.app) as client:
        alice, bob = create(client), create(client)
        store = main.app.state.store
        save = store.save

        def fail_alice(snapshot, learner_id):
            if learner_id == alice["X-Learner-ID"]:
                raise sqlite3.OperationalError("disk full")
            save(snapshot, learner_id)

        monkeypatch.setattr(store, "save", fail_alice)
        assert client.put("/api/learner/profile", headers=alice, json={"name": "Alice"}).status_code == 503
        assert client.put("/api/learner/profile", headers=bob, json={"name": "Bob"}).status_code == 200
    with TestClient(main.app) as client:
        assert client.get("/api/learner/profile", headers=alice).json()["name"] is None
        assert client.get("/api/learner/profile", headers=bob).json()["name"] == "Bob"


def test_failed_creation_does_not_publish_an_unsaved_learner(database, monkeypatch):
    with TestClient(main.app) as client:
        def fail(*args):
            raise sqlite3.OperationalError("disk full")

        monkeypatch.setattr(main.app.state.store, "save", fail)
        assert client.post("/api/learners").status_code == 503
        assert main.app.state.learners.sessions == {}


@pytest.mark.asyncio
async def test_slow_learner_does_not_block_another(database, monkeypatch):
    async with main.lifespan(main.app):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=main.app), base_url="http://test") as client:
            alice = (await client.post("/api/learners")).json()["learner_id"]
            bob = (await client.post("/api/learners")).json()["learner_id"]
            started, release = asyncio.Event(), asyncio.Event()
            agent = main.app.state.learners.get(alice).agent

            async def slow(message):
                started.set()
                await release.wait()
                agent.memory.add_user_message(message)
                return "Done"

            monkeypatch.setattr(agent, "process", slow)
            pending = asyncio.create_task(client.post("/api/chat", headers={"X-Learner-ID": alice}, json={"message": "Hello"}))
            try:
                await asyncio.wait_for(started.wait(), timeout=2)
                response = await asyncio.wait_for(client.put(
                    "/api/learner/profile", headers={"X-Learner-ID": bob}, json={"name": "Bob"},
                ), timeout=2)
                assert response.status_code == 200
                assert not pending.done()
            finally:
                release.set()
                assert (await pending).status_code == 200
            assert main.app.state.store.load(alice).profile.name is None
            assert main.app.state.store.load(bob).profile.name == "Bob"


@pytest.mark.asyncio
async def test_same_learner_requests_are_serialized(database, monkeypatch):
    async with main.lifespan(main.app):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=main.app), base_url="http://test") as client:
            learner_id = (await client.post("/api/learners")).json()["learner_id"]
            session = main.app.state.learners.get(learner_id)
            active, max_active = 0, 0

            async def process(message):
                nonlocal active, max_active
                active += 1
                max_active = max(max_active, active)
                await asyncio.sleep(0.01)
                session.agent.memory.add_user_message(message)
                active -= 1
                return "Done"

            monkeypatch.setattr(session.agent, "process", process)
            responses = await asyncio.gather(*[
                client.post("/api/chat", headers={"X-Learner-ID": learner_id}, json={"message": str(index)})
                for index in range(5)
            ])
            assert all(response.status_code == 200 for response in responses)
            assert max_active == 1
            assert len(main.app.state.store.load(learner_id).conversation) == 5


def legacy_database(path, payload):
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE app_state (id INTEGER PRIMARY KEY, payload TEXT)")
        connection.execute("INSERT INTO app_state VALUES (1, ?)", (payload,))


def test_legacy_database_migrates_without_sharing_or_replaying(database):
    agent = ZephyrAgent()
    agent.learner.set_name("Ancien profil")
    snapshot = capture_state(agent, AdaptiveAssessment())
    legacy_database(database, snapshot.model_dump_json())
    with TestClient(main.app) as client:
        headers = {"X-Learner-ID": LEGACY_LEARNER_ID}
        assert client.get("/api/learner/profile", headers=headers).json()["name"] == "Ancien profil"
        new = create(client)
        assert client.get("/api/learner/profile", headers=new).json()["name"] is None
        assert client.put("/api/learner/profile", headers=headers, json={"name": "Modifié"}).status_code == 200
    with TestClient(main.app) as client:
        assert client.get("/api/learner/profile", headers=headers).json()["name"] == "Modifié"
        assert client.get("/api/learner/profile", headers=new).json()["name"] is None
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT name FROM sqlite_master WHERE name='app_state'").fetchone() is None


def test_invalid_legacy_state_rolls_back_migration(database):
    legacy_database(database, '{"version":999}')
    with pytest.raises(ValidationError):
        StateStore(str(database))
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT payload FROM app_state").fetchone()[0] == '{"version":999}'
        assert connection.execute("SELECT name FROM sqlite_master WHERE name='learner_states'").fetchone() is None


def test_corrupt_learner_does_not_prevent_other_learners(database):
    with TestClient(main.app) as client:
        alice, bob = create(client), create(client)
    with sqlite3.connect(database) as connection:
        connection.execute("UPDATE learner_states SET payload = ? WHERE learner_id = ?", ('{"version":999}', alice["X-Learner-ID"]))
    with TestClient(main.app) as client:
        assert client.get("/api/learner/profile", headers=alice).status_code == 503
        assert client.put("/api/learner/profile", headers=bob, json={"name": "Bob"}).status_code == 200
        assert alice["X-Learner-ID"] not in main.app.state.learners.sessions


def test_backup_preserves_all_learners(database, tmp_path):
    from app.backup import backup_database

    with TestClient(main.app) as client:
        alice, bob = create(client), create(client)
        for headers, name in [(alice, "Alice"), (bob, "Bob")]:
            assert client.put("/api/learner/profile", headers=headers, json={"name": name}).status_code == 200
        target = tmp_path / "backup.sqlite3"
        backup_database(str(database), str(target))
    restored = StateStore(str(target))
    assert restored.load(alice["X-Learner-ID"]).profile.name == "Alice"
    assert restored.load(bob["X-Learner-ID"]).profile.name == "Bob"


def test_isolation_remains_active_without_persistence(monkeypatch):
    monkeypatch.setattr(main.settings, "persistence_enabled", False)
    with TestClient(main.app) as client:
        alice, bob = create(client), create(client)
        assert client.put("/api/learner/profile", headers=alice, json={"name": "Alice"}).status_code == 200
        assert client.get("/api/learner/profile", headers=bob).json()["name"] is None
        assert client.get("/api/learner/profile").status_code == 400
    with TestClient(main.app) as client:
        assert client.get("/api/learner/profile", headers=alice).status_code == 404


def test_openapi_exposes_learner_selection_for_existing_routes():
    with TestClient(main.app) as client:
        schema = client.get("/openapi.json").json()
        for path, operations in schema["paths"].items():
            if not path.startswith("/api/") or path == "/api/learners":
                continue
            for operation in operations.values():
                headers = [param for param in operation.get("parameters", []) if param["in"] == "header"]
                assert any(param["name"].lower() == "x-learner-id" and param["required"] for param in headers), path
