import json

import pytest
from fastapi.testclient import TestClient

from app import main
from app.persistence import capture_state, StateSnapshot


@pytest.fixture
def learners(tmp_path, monkeypatch):
    monkeypatch.setattr(main.settings, "persistence_enabled", True)
    monkeypatch.setattr(main.settings, "database_path", str(tmp_path / "state.sqlite3"))
    with TestClient(main.app) as client:
        headers = []
        for name in ("Alice", "Bob"):
            learner_id = client.post("/api/learners").json()["learner_id"]
            header = {"X-Learner-ID": learner_id}
            assert client.put("/api/learner/profile", headers=header, json={
                "name": name, "target_language": "anglais", "level": "A1",
            }).status_code == 200
            headers.append(header)
        yield client, *headers


def agent_for(header):
    return main.app.state.learners.get(header["X-Learner-ID"]).agent


def add_target(client, header, category):
    payload = {"word": "small", "translation": "petit"} if category == "vocabulary" else {
        "rule": "Present Simple", "explanation": "Habitudes",
    }
    assert client.post(f"/api/learning/{category}", headers=header, json=payload).status_code == 200
    return "small" if category == "vocabulary" else "Present Simple"


def generated(skill="grammar", exercise_type="fill_blank"):
    return {"exercises": [{"exercise_type": exercise_type, "question": "I ___ a student.",
        "level": "A1", "skill": skill, "expected_answer": "am", "difficulty": 1}]}


def evaluation(**kwargs):
    return {"score": 90, "correct": True, "feedback": "Bien.", "errors": [], "strengths": [], "weak_points": [], **kwargs}


@pytest.mark.parametrize("category", ["grammar", "vocabulary"])
def test_linked_exercise_updates_only_its_target_and_survives_restart(learners, monkeypatch, category):
    client, alice, bob = learners
    target = add_target(client, alice, category)
    add_target(client, bob, category)
    agent = agent_for(alice)
    bob_session = main.app.state.learners.get(bob["X-Learner-ID"])
    bob_before = capture_state(bob_session.agent, bob_session.assessment)

    async def response(messages):
        assert target in messages[-1]["content"]
        return json.dumps(generated(category))

    monkeypatch.setattr(agent.learning_engine.exercise_generator.llm, "chat", response)
    response = client.post("/api/learning/exercises", headers=alice, json={
        "topic": "Practice", "skill": category, "count": 1,
        "target_category": category, "target": " " + target.upper() + " ",
    })
    assert response.status_code == 200
    exercise = response.json()["exercises"][0]
    assert exercise["target_category"] == category
    assert exercise["target"] == target
    assert "expected_answer" not in exercise
    endpoint = f"/api/learning/exercises/{exercise['id']}/answer"
    for answer in ("is", "am"):
        assert client.post(endpoint, headers=alice, json={"answer": answer}).status_code == 200
    manager = agent.learning_engine.grammar if category == "grammar" else agent.learning_engine.vocabulary
    item = manager.get_rule(target) if category == "grammar" else manager.get_word(target)
    assert item.review_count == 2
    assert item.mastery == 50
    if category == "grammar":
        profile = client.get("/api/learner/profile", headers=alice).json()
        assert profile["grammar_mastery"][target] == 50
        assert len(profile["grammar_history"]) == 2
    recommendations = client.get("/api/learning/recommendations", headers=alice).json()["recommendations"]
    assert next(r for r in recommendations if r["target"] == target)["mastery"] == 50
    assert capture_state(bob_session.agent, bob_session.assessment) == bob_before
    saved = main.app.state.store.load(alice["X-Learner-ID"])
    assert saved.exercises[0].target == target
    # Démarrage d'un nouveau registre sur la même base, sans réutiliser les objets.
    from app.sessions import LearnerSessions
    registry = LearnerSessions(main.app.state.store)
    restored = registry.get(alice["X-Learner-ID"])
    assert capture_state(restored.agent, restored.assessment) == saved


@pytest.mark.parametrize("payload,status", [
    ({"target_category": "grammar"}, 422), ({"target": "Present Simple"}, 422),
    ({"target_category": "other", "target": "Present Simple"}, 422),
    ({"target_category": "grammar", "target": "   "}, 422),
    ({"target_category": "grammar", "target": "Unknown"}, 400),
])
def test_invalid_target_is_rejected_before_generation(learners, payload, status):
    client, alice, _ = learners
    response = client.post("/api/learning/exercises", headers=alice, json={
        "topic": "Practice", "skill": "grammar", "count": 1, **payload,
    })
    assert response.status_code == status
    assert not agent_for(alice).learning_engine.exercises


def test_other_learners_target_cannot_be_linked(learners):
    client, alice, bob = learners
    target = add_target(client, alice, "grammar")
    assert client.post("/api/learning/exercises", headers=bob, json={
        "topic": "Practice", "skill": "grammar", "count": 1,
        "target_category": "grammar", "target": target,
    }).status_code == 400


def test_language_mismatch_cannot_be_linked(learners):
    client, alice, _ = learners
    target = add_target(client, alice, "grammar")
    assert client.put("/api/learner/profile", headers=alice, json={"target_language": "espagnol"}).status_code == 200
    assert client.post("/api/learning/exercises", headers=alice, json={
        "topic": "Practice", "skill": "grammar", "target_category": "grammar", "target": target,
    }).status_code == 400


def test_invalid_correction_does_not_change_mastery_and_can_be_retried(learners, monkeypatch):
    client, alice, _ = learners
    target = add_target(client, alice, "grammar")
    agent = agent_for(alice)

    async def generate(messages):
        return json.dumps(generated(exercise_type="writing"))

    async def invalid(messages):
        return json.dumps(evaluation(correct="false"))

    monkeypatch.setattr(agent.learning_engine.exercise_generator.llm, "chat", generate)
    response = client.post("/api/learning/exercises", headers=alice, json={
        "topic": "Practice", "skill": "grammar", "count": 1,
        "target_category": "grammar", "target": target,
    })
    endpoint = f"/api/learning/exercises/{response.json()['exercises'][0]['id']}/answer"
    before = main.app.state.store.load(alice["X-Learner-ID"])
    monkeypatch.setattr(agent.learning_engine.exercise_evaluator.llm, "chat", invalid)
    assert client.post(endpoint, headers=alice, json={"answer": "Hello"}).status_code == 502
    assert main.app.state.store.load(alice["X-Learner-ID"]) == before
    assert agent.learning_engine.grammar.get_rule(target).review_count == 0

    async def valid(messages):
        return json.dumps(evaluation())

    monkeypatch.setattr(agent.learning_engine.exercise_evaluator.llm, "chat", valid)
    assert client.post(endpoint, headers=alice, json={"answer": "Hello"}).status_code == 200
    assert agent.learning_engine.grammar.get_rule(target).review_count == 1
    assert agent.learning_engine.grammar.get_rule(target).mastery == 100


@pytest.mark.parametrize("endpoint,body,component", [
    ("/api/chat", {"message": "Hello"}, "profile_extractor"),
    ("/api/learning/lesson", {"topic": "Greetings"}, "lesson_generator"),
    ("/api/learning/exercises", {"topic": "Greetings", "skill": "grammar", "count": 1}, "exercise_generator"),
])
def test_invalid_generation_has_no_saved_side_effects(learners, monkeypatch, endpoint, body, component):
    client, alice, _ = learners
    agent = agent_for(alice)
    generator = agent.profile_extractor if component == "profile_extractor" else getattr(agent.learning_engine, component)

    async def invalid(messages):
        return "null"

    monkeypatch.setattr(generator.llm, "chat", invalid)
    before = main.app.state.store.load(alice["X-Learner-ID"])
    assert client.post(endpoint, headers=alice, json=body).status_code == 502
    assert main.app.state.store.load(alice["X-Learner-ID"]) == before
    session = main.app.state.learners.get(alice["X-Learner-ID"])
    assert capture_state(session.agent, session.assessment) == before


def test_invalid_assessment_does_not_record_zero_or_block_retry(learners, monkeypatch):
    client, alice, _ = learners
    session = main.app.state.learners.get(alice["X-Learner-ID"])
    assessment = session.assessment
    assessment.session.question_index = next(
        i for i, question in enumerate(assessment.session.questions_by_level["A1"])
        if question["type"] == "open"
    )
    before = capture_state(session.agent, assessment)
    main.app.state.store.save(before, alice["X-Learner-ID"])

    async def invalid(messages):
        return json.dumps(evaluation(score=101))

    monkeypatch.setattr(assessment.evaluator.llm, "chat", invalid)
    assert client.post("/api/assessment/answer", headers=alice, json={"answer": "Hello"}).status_code == 502
    assert capture_state(session.agent, assessment) == before
    assert main.app.state.store.load(alice["X-Learner-ID"]) == before

    async def valid(messages):
        return json.dumps(evaluation())

    monkeypatch.setattr(assessment.evaluator.llm, "chat", valid)
    response = client.post("/api/assessment/answer", headers=alice, json={"answer": "Hello"})
    assert response.status_code == 200
    assert response.json()["evaluation"]["score"] == 90
    assert len(assessment.session.answers) == 1


def test_old_exercises_restore_without_target(learners):
    client, alice, _ = learners
    session = main.app.state.learners.get(alice["X-Learner-ID"])
    session.agent.learning_engine.create_exercise("fill_blank", "I ___ here", "A1", "grammar", expected_answer="am")
    data = capture_state(session.agent, session.assessment).model_dump(mode="json")
    for field in ("target", "target_category"):
        data["exercises"][0].pop(field)
    restored = StateSnapshot.model_validate_json(json.dumps(data))
    assert restored.exercises[0].target is None
    assert restored.exercises[0].target_category is None


def test_invalid_final_assessment_does_not_update_profile(learners, monkeypatch):
    client, alice, _ = learners
    session = main.app.state.learners.get(alice["X-Learner-ID"])
    assessment = session.assessment
    question = next(q for q in assessment.session.questions_by_level["A1"] if q["type"] == "open")
    assessment.session.answers = [{"question_id": question["id"], "answer": "Hello"}]
    assessment.session.finished = True
    before = capture_state(session.agent, assessment)
    main.app.state.store.save(before, alice["X-Learner-ID"])

    async def invalid(messages):
        return "null"

    monkeypatch.setattr(assessment.evaluator.llm, "chat", invalid)
    assert client.get("/api/assessment/result", headers=alice).status_code == 502
    assert capture_state(session.agent, assessment) == before
    assert main.app.state.store.load(alice["X-Learner-ID"]) == before


@pytest.mark.parametrize("endpoint,payload", [
    ("/api/learner/profile", {"level": "beginner"}),
    ("/api/learning/exercises", {"topic": "Practice", "skill": "unknown"}),
])
def test_invalid_generation_inputs_are_rejected(learners, endpoint, payload):
    client, alice, _ = learners
    method = client.put if endpoint.endswith("profile") else client.post
    assert method(endpoint, headers=alice, json=payload).status_code == 422
