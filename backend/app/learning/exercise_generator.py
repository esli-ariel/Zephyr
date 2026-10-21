import uuid

from app.learning.llm_schemas import ExerciseBatch, parse_response

from app.learning.exercise import Exercise
from app.llm.openrouter import OpenRouterClient


class ExerciseGenerator:
    """
    Générateur intelligent d'exercices.

    Les exercices sont générés à partir du profil
    pédagogique de l'apprenant et du contenu étudié.
    """

    EXERCISE_PROMPT = """
Tu es Zéphyr, un professeur de langues intelligent.

Tu dois générer des exercices adaptés à un apprenant.

Tu dois respecter :

- la langue cible ;
- le niveau CECRL ;
- le sujet ;
- les objectifs ;
- les points faibles ;
- la compétence travaillée.

Retourne UNIQUEMENT un JSON valide.

Structure obligatoire :

{
    "exercises": [
        {
            "exercise_type": "multiple_choice",
            "question": "Question",
            "level": "A1",
            "skill": "vocabulary",
            "options": [
                "option 1",
                "option 2",
                "option 3"
            ],
            "expected_answer": "option 1",
            "difficulty": 1
        }
    ]
}

Types autorisés :

- multiple_choice
- fill_blank
- translation
- writing
- reading

Compétences autorisées :

- vocabulary
- grammar
- comprehension
- expression
- translation

Règles :

1. Les exercices doivent être adaptés au niveau.
2. Les questions doivent être claires.
3. Les réponses doivent être vérifiables.
4. Les QCM doivent avoir au moins trois options.
5. Les exercices d'expression peuvent avoir
   une réponse ouverte.
6. La difficulté doit être comprise entre 1 et 5.
7. Génère exactement le nombre d'exercices demandé.
8. Retourne uniquement le JSON, sans champ supplémentaire.
9. Les champs level et skill doivent être identiques à ceux demandés.
10. Pour un exercice fermé, expected_answer est obligatoire.
11. La réponse du QCM doit être l'une des options, et les options sont distinctes.
12. Ne fournis ni identifiant, ni lien vers une notion : le serveur les attribue.
"""

    def __init__(self):
        self.llm = OpenRouterClient()

    async def generate(
        self,
        language: str,
        level: str,
        topic: str,
        skill: str,
        count: int = 5,
        objectives: list[str] | None = None,
        weak_points: list[str] | None = None,
    ) -> list[Exercise]:

        if count < 1 or count > 20:
            raise ValueError(
                "Le nombre d'exercices doit être compris "
                "entre 1 et 20."
            )

        prompt = self._build_prompt(
            language=language,
            level=level,
            topic=topic,
            skill=skill,
            count=count,
            objectives=objectives or [],
            weak_points=weak_points or [],
        )

        messages = [
            {
                "role": "system",
                "content": self.EXERCISE_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        response = await self.llm.chat(messages)

        data = self._parse_response(response)

        if len(data["exercises"]) != count:
            raise RuntimeError("Le nombre d'exercices générés ne correspond pas à la demande.")
        if any(item["level"] != level or item["skill"] != skill for item in data["exercises"]):
            raise RuntimeError("Les exercices générés ne correspondent pas au niveau ou à la compétence demandés.")
        exercises = self._build_exercises(
            data,
            language=language,
            level=level,
            skill=skill,
        )
        for exercise in exercises:
            exercise.id = str(uuid.uuid4())
        return exercises

    def _build_prompt(
        self,
        language: str,
        level: str,
        topic: str,
        skill: str,
        count: int,
        objectives: list[str],
        weak_points: list[str],
    ) -> str:

        return f"""
Profil pédagogique :

Langue cible :
{language}

Niveau :
{level}

Sujet :
{topic}

Compétence :
{skill}

Nombre d'exercices :
{count}

Objectifs :
{objectives}

Points faibles :
{weak_points}

Génère maintenant les exercices.
"""

    def _parse_response(
        self,
        response: str,
    ) -> dict:

        return parse_response(ExerciseBatch, response)

    def _build_exercises(
        self,
        data: dict,
        language: str,
        level: str,
        skill: str,
    ) -> list[Exercise]:

        exercises = []

        for item in data["exercises"]:

            exercise = Exercise(
                id=str(item.get("id")),
                exercise_type=item.get(
                    "exercise_type",
                    "multiple_choice",
                ),
                question=item.get(
                    "question",
                    "",
                ),
                level=item.get(
                    "level",
                    level,
                ),
                skill=item.get(
                    "skill",
                    skill,
                ),
                options=item.get(
                    "options",
                    [],
                ),
                expected_answer=item.get(
                    "expected_answer"
                ),
                difficulty=item.get(
                    "difficulty",
                    1,
                ),
            )

            exercises.append(exercise)

        return exercises