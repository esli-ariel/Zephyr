import json

import httpx
import pytest

from app.learning.assessment_evaluator import AssessmentEvaluator
from app.learning.exercise_evaluator import ExerciseEvaluator
from app.learning.exercise_generator import ExerciseGenerator
from app.learning.lesson_generator import LessonGenerator
from app.learning.profile_extractor import ProfileExtractor
from app.learning.llm_schemas import EvaluationResponse, ExerciseBatch, LessonResponse, ProfileResponse, parse_response
from app.llm.openrouter import OpenRouterClient

EVALUATION = {"score": 80, "correct": True, "feedback": "Bien.", "errors": [], "strengths": ["grammar"], "weak_points": []}
EXERCISE = {"exercise_type": "multiple_choice", "question": "Opposite of big?", "level": "A1", "skill": "vocabulary", "options": ["small", "long", "tall"], "expected_answer": "small", "difficulty": 1}
LESSON = {"title": "Greetings", "language": "anglais", "level": "A1", "topic": "Greetings", "objectives": ["Say hello"], "sections": [{"title": "Hello", "content": "Bonjour", "section_type": "vocabulary"}]}
PROFILE = {"name": "Alice", "target_language": "anglais", "level": "A1", "goals": []}


@pytest.mark.parametrize("model", [EvaluationResponse, ExerciseBatch, LessonResponse, ProfileResponse])
@pytest.mark.parametrize("payload", ["null", "[]", '"text"', "false", "{bad}"])
def test_non_object_and_invalid_json_are_rejected(model, payload):
    with pytest.raises(RuntimeError, match="Réponse IA invalide"):
        parse_response(model, payload)


@pytest.mark.parametrize("field,value", [
    ("score", "80"), ("score", True), ("score", 101), ("score", -1), ("score", 80.5),
    ("correct", "false"), ("correct", 1), ("feedback", "   "),
    ("errors", None), ("errors", "error"), ("errors", [1]),
    ("strengths", [{}]), ("weak_points", [None]), ("extra", "secret"),
])
def test_evaluations_do_not_coerce_invalid_fields(field, value):
    payload = {**EVALUATION, field: value}
    with pytest.raises(RuntimeError):
        ExerciseEvaluator()._parse_llm_result(json.dumps(payload))
    with pytest.raises(RuntimeError):
        AssessmentEvaluator()._parse_open_result({"id": 1, "level": "A1", "category": "grammar"}, json.dumps(payload))


@pytest.mark.parametrize("payload", [
    {**PROFILE, "goals": "travel"}, {**PROFILE, "goals": [42]},
    {**PROFILE, "name": {}}, {**PROFILE, "level": "beginner"},
    {**PROFILE, "target_language": True}, {"name": "Alice"},
])
def test_invalid_profile_is_rejected(payload):
    with pytest.raises(RuntimeError):
        ProfileExtractor()._parse_response(json.dumps(payload))


@pytest.mark.parametrize("field,value", [
    ("difficulty", True), ("difficulty", 6), ("difficulty", "1"),
    ("question", " "), ("question", {}), ("level", "B9"),
    ("skill", "unknown"), ("exercise_type", "unknown"),
    ("options", ["a", "b"]), ("options", ["small", "SMALL", "long"]),
    ("expected_answer", "missing"), ("expected_answer", None),
    ("target", "injected"),
])
def test_generated_exercises_are_validated(field, value):
    with pytest.raises(RuntimeError):
        ExerciseGenerator()._parse_response(json.dumps({"exercises": [{**EXERCISE, field: value}]}))


@pytest.mark.parametrize("payload", [
    {"exercises": []}, {"exercises": [None]}, {"exercises": ["text"]},
    {"exercises": [{"question": "Incomplete"}]},
])
def test_invalid_batch_is_rejected(payload):
    with pytest.raises(RuntimeError):
        ExerciseGenerator()._parse_response(json.dumps(payload))


@pytest.mark.parametrize("field,value", [
    ("sections", []), ("sections", [None]), ("sections", [{"title": "Missing content"}]),
    ("sections", [{"title": "Hi", "content": "Hi", "section_type": "unknown"}]),
    ("objectives", "hello"), ("objectives", [True]), ("title", " "), ("level", "beginner"),
])
def test_invalid_lessons_are_rejected(field, value):
    with pytest.raises(RuntimeError):
        LessonGenerator()._parse_response(json.dumps({**LESSON, field: value}))


@pytest.mark.asyncio
async def test_generated_ids_are_unique_across_repeated_batches(monkeypatch):
    generator = ExerciseGenerator()

    async def response(messages):
        return json.dumps({"exercises": [{**EXERCISE, "id": "ex1"}]})

    monkeypatch.setattr(generator.llm, "chat", response)
    first = await generator.generate("anglais", "A1", "Opposites", "vocabulary", count=1)
    second = await generator.generate("anglais", "A1", "Opposites", "vocabulary", count=1)
    assert first[0].id != second[0].id
    assert first[0].id != "ex1"


@pytest.mark.asyncio
@pytest.mark.parametrize("patch,count", [({}, 2), ({"level": "B2"}, 1), ({"skill": "grammar"}, 1)])
async def test_generated_batch_must_match_request(monkeypatch, patch, count):
    generator = ExerciseGenerator()

    async def response(messages):
        return json.dumps({"exercises": [{**EXERCISE, **patch}]})

    monkeypatch.setattr(generator.llm, "chat", response)
    with pytest.raises(RuntimeError):
        await generator.generate("anglais", "A1", "Opposites", "vocabulary", count=count)


@pytest.mark.asyncio
@pytest.mark.parametrize("patch", [{"language": "espagnol"}, {"level": "C2"}])
async def test_lesson_must_match_request(monkeypatch, patch):
    generator = LessonGenerator()

    async def response(messages):
        return json.dumps({**LESSON, **patch})

    monkeypatch.setattr(generator.llm, "chat", response)
    with pytest.raises(RuntimeError):
        await generator.generate("anglais", "A1", "Greetings")


@pytest.mark.asyncio
@pytest.mark.parametrize("payload", [None, [], {"choices": []}, {"choices": [{"message": {"content": " "}}]}, {"choices": [{"message": {"content": []}}]}])
async def test_openrouter_rejects_invalid_envelope(monkeypatch, payload):
    from app.llm import openrouter
    # Contourner uniquement le blocage de chat des tests, avec un transport HTTP simulé.
    client = OpenRouterClient()
    client.api_key, client.model = "test-only", "test-only"
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=payload))
    original = httpx.AsyncClient
    monkeypatch.setattr(openrouter.httpx, "AsyncClient", lambda **kwargs: original(transport=transport, **kwargs))
    with pytest.raises(RuntimeError):
        await ORIGINAL_CHAT(client, [])


ORIGINAL_CHAT = OpenRouterClient.chat


def test_duplicate_json_fields_are_rejected():
    payload = json.dumps(EVALUATION)[:-1] + ', "correct": false}'
    with pytest.raises(RuntimeError):
        ExerciseEvaluator()._parse_llm_result(payload)


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["status", "timeout", "invalid_json", "success"])
async def test_openrouter_transport_and_response_errors(monkeypatch, mode):
    from app.llm import openrouter
    client = OpenRouterClient()
    client.api_key, client.model = "test-only", "test-only"

    def handler(request):
        if mode == "timeout":
            raise httpx.ReadTimeout("private upstream detail")
        if mode == "status":
            return httpx.Response(429, text="private upstream detail")
        if mode == "invalid_json":
            return httpx.Response(200, text="private upstream detail")
        return httpx.Response(200, json={"choices": [{"message": {"content": "Hello"}}]})

    original = httpx.AsyncClient
    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(openrouter.httpx, "AsyncClient", lambda **kwargs: original(transport=transport, **kwargs))
    if mode == "success":
        assert await ORIGINAL_CHAT(client, []) == "Hello"
    else:
        with pytest.raises(RuntimeError) as error:
            await ORIGINAL_CHAT(client, [])
        assert "private upstream detail" not in str(error.value)
