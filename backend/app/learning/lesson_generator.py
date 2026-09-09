import json
import uuid

from app.learning.lesson import Lesson
from app.llm.openrouter import OpenRouterClient


class LessonGenerator:
    """
    Générateur intelligent de leçons.

    Il utilise le profil de l'apprenant et OpenRouter
    pour générer une leçon structurée.
    """

    LESSON_PROMPT = """
Tu es Zéphyr, un professeur de langues intelligent.

Ta mission est de créer une leçon adaptée à un apprenant.

Tu dois tenir compte de :

- sa langue cible ;
- son niveau CECRL ;
- ses objectifs ;
- ses points faibles ;
- ses erreurs fréquentes ;
- le sujet demandé.

Retourne UNIQUEMENT un JSON valide.

Structure obligatoire :

{
    "title": "Titre de la leçon",
    "language": "Langue cible",
    "level": "Niveau CECRL",
    "topic": "Sujet",
    "objectives": [
        "objectif 1",
        "objectif 2"
    ],
    "sections": [
        {
            "title": "Titre",
            "content": "Contenu",
            "section_type": "introduction"
        }
    ]
}

Types de sections possibles :

- introduction
- vocabulary
- grammar
- examples
- practice
- summary

Règles :

1. La leçon doit être adaptée au niveau.
2. Les explications doivent être pédagogiques.
3. Utilise des exemples concrets.
4. Tiens compte des points faibles.
5. Les objectifs doivent être mesurables.
6. Ne crée pas d'exercices pour le moment.
7. Retourne uniquement le JSON.
"""

    def __init__(self):
        self.llm = OpenRouterClient()

    async def generate(
        self,
        language: str,
        level: str,
        topic: str,
        objectives: list[str] | None = None,
        weak_points: list[str] | None = None,
        common_mistakes: list[str] | None = None,
    ) -> Lesson:

        prompt = self._build_prompt(
            language=language,
            level=level,
            topic=topic,
            objectives=objectives or [],
            weak_points=weak_points or [],
            common_mistakes=common_mistakes or [],
        )

        messages = [
            {
                "role": "system",
                "content": self.LESSON_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        response = await self.llm.chat(messages)

        data = self._parse_response(response)

        return self._build_lesson(data)

    def _build_prompt(
        self,
        language: str,
        level: str,
        topic: str,
        objectives: list[str],
        weak_points: list[str],
        common_mistakes: list[str],
    ) -> str:

        return f"""
Profil pédagogique :

Langue cible :
{language}

Niveau :
{level}

Sujet :
{topic}

Objectifs :
{objectives}

Points faibles :
{weak_points}

Erreurs fréquentes :
{common_mistakes}

Crée maintenant une leçon complète et adaptée.
"""

    def _parse_response(
        self,
        response: str,
    ) -> dict:

        try:
            data = json.loads(response)

        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Le générateur de leçons a retourné "
                "un JSON invalide."
            ) from exc

        required_fields = [
            "title",
            "language",
            "level",
            "topic",
            "objectives",
            "sections",
        ]

        for field in required_fields:
            if field not in data:
                raise RuntimeError(
                    f"Leçon invalide : champ "
                    f"'{field}' manquant."
                )

        if not isinstance(data["sections"], list):
            raise RuntimeError(
                "Le champ 'sections' doit être une liste."
            )

        return data

    def _build_lesson(
        self,
        data: dict,
    ) -> Lesson:

        lesson = Lesson(
            id=str(uuid.uuid4()),
            title=data["title"],
            language=data["language"],
            level=data["level"],
            topic=data["topic"],
            objectives=data["objectives"],
        )

        for section in data["sections"]:

            lesson.add_section(
                title=section.get(
                    "title",
                    "Section",
                ),
                content=section.get(
                    "content",
                    "",
                ),
                section_type=section.get(
                    "section_type",
                    "practice",
                ),
            )

        return lesson