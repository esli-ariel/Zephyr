import pytest

from app.learning.lesson_generator import LessonGenerator


@pytest.mark.asyncio
async def test_parse_valid_lesson():
    generator = LessonGenerator()

    response = """
    {
        "title": "Greetings",
        "language": "anglais",
        "level": "A1",
        "topic": "Salutations",
        "objectives": [
            "Dire bonjour",
            "Se présenter"
        ],
        "sections": [
            {
                "title": "Introduction",
                "content": "Hello means bonjour.",
                "section_type": "introduction"
            },
            {
                "title": "Vocabulary",
                "content": "Hello, Hi, Good morning.",
                "section_type": "vocabulary"
            }
        ]
    }
    """

    data = generator._parse_response(response)

    assert data["title"] == "Greetings"
    assert data["level"] == "A1"
    assert len(data["sections"]) == 2

def test_invalid_json():
    generator = LessonGenerator()

    with pytest.raises(RuntimeError):
        generator._parse_response(
            "ceci n'est pas du JSON"
        )

def test_missing_field():
    generator = LessonGenerator()

    response = """
    {
        "title": "Greetings",
        "language": "anglais",
        "level": "A1"
    }
    """

    with pytest.raises(RuntimeError):
        generator._parse_response(response)

def test_build_lesson():
    generator = LessonGenerator()

    data = {
        "title": "Greetings",
        "language": "anglais",
        "level": "A1",
        "topic": "Salutations",
        "objectives": [
            "Dire bonjour"
        ],
        "sections": [
            {
                "title": "Introduction",
                "content": "Hello means bonjour.",
                "section_type": "introduction",
            }
        ],
    }

    lesson = generator._build_lesson(data)

    assert lesson.title == "Greetings"
    assert lesson.language == "anglais"
    assert lesson.level == "A1"
    assert len(lesson.sections) == 1

