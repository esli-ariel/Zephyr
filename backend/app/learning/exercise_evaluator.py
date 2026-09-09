import json

from app.learning.exercise import Exercise
from app.llm.openrouter import OpenRouterClient


class ExerciseEvaluator:
    """
    Évalue les réponses aux exercices.

    Les exercices fermés sont corrigés localement.
    Les exercices ouverts sont évalués avec le LLM.
    """

    LOCAL_TYPES = {
        "multiple_choice",
        "fill_blank",
    }

    def __init__(self):
        self.llm = OpenRouterClient()

    async def evaluate(
        self,
        exercise: Exercise,
        answer: str,
    ) -> dict:

        if not answer.strip():
            raise ValueError(
                "La réponse ne peut pas être vide."
            )

        if exercise.exercise_type in self.LOCAL_TYPES:
            return self._evaluate_local(
                exercise,
                answer,
            )

        return await self._evaluate_with_llm(
            exercise,
            answer,
        )

    def _evaluate_local(
        self,
        exercise: Exercise,
        answer: str,
    ) -> dict:

        expected = exercise.expected_answer

        if expected is None:
            raise ValueError(
                "Cet exercice ne possède pas de "
                "réponse attendue."
            )

        normalized_answer = (
            answer.strip().lower()
        )

        normalized_expected = (
            expected.strip().lower()
        )

        correct = (
            normalized_answer
            == normalized_expected
        )

        score = 100 if correct else 0

        if correct:
            feedback = (
                "Bonne réponse !"
            )
        else:
            feedback = (
                f"Réponse incorrecte. "
                f"La bonne réponse est : "
                f"{expected}."
            )

        return {
            "score": score,
            "correct": correct,
            "feedback": feedback,
            "errors": []
            if correct
            else [f"Réponse attendue : {expected}"],
            "strengths": []
            if not correct
            else [exercise.skill],
            "weak_points": []
            if correct
            else [exercise.skill],
        }

    async def _evaluate_with_llm(
        self,
        exercise: Exercise,
        answer: str,
    ) -> dict:

        prompt = f"""
Évalue la réponse d'un apprenant à un exercice
de langue.

Exercice :
{exercise.question}

Type :
{exercise.exercise_type}

Niveau :
{exercise.level}

Compétence :
{exercise.skill}

Réponse de l'apprenant :
{answer}

Réponse attendue éventuelle :
{exercise.expected_answer}

Retourne uniquement un JSON valide :

{{
    "score": 0,
    "correct": false,
    "feedback": "Explication pédagogique",
    "errors": [],
    "strengths": [],
    "weak_points": []
}}

Règles :

- score entre 0 et 100 ;
- correct doit être true ou false ;
- feedback doit expliquer clairement la réponse ;
- errors contient les erreurs détectées ;
- strengths contient les points réussis ;
- weak_points contient les compétences à travailler ;
- sois pédagogique ;
- ne retourne aucun texte en dehors du JSON.
"""

        messages = [
            {
                "role": "system",
                "content": (
                    "Tu es un correcteur pédagogique "
                    "de langues."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        response = await self.llm.chat(messages)

        return self._parse_llm_result(response)

    def _parse_llm_result(
        self,
        response: str,
    ) -> dict:

        try:
            data = json.loads(response)

        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Le correcteur a retourné "
                "un JSON invalide."
            ) from exc

        required_fields = [
            "score",
            "correct",
            "feedback",
            "errors",
            "strengths",
            "weak_points",
        ]

        for field in required_fields:
            if field not in data:
                raise RuntimeError(
                    f"Résultat invalide : "
                    f"champ '{field}' manquant."
                )

        try:
            score = int(data["score"])
        except (TypeError, ValueError) as exc:
            raise RuntimeError(
                "Le score retourné est invalide."
            ) from exc

        score = max(0, min(score, 100))

        return {
            "score": score,
            "correct": bool(data["correct"]),
            "feedback": str(data["feedback"]),
            "errors": self._ensure_list(
                data["errors"]
            ),
            "strengths": self._ensure_list(
                data["strengths"]
            ),
            "weak_points": self._ensure_list(
                data["weak_points"]
            ),
        }

    @staticmethod
    def _ensure_list(value) -> list:
        if value is None:
            return []

        if isinstance(value, list):
            return value

        return [str(value)]