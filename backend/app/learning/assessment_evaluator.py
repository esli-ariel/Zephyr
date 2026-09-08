import json

from app.llm.openrouter import OpenRouterClient
from app.learning.assessment_questions import (
    ASSESSMENT_QUESTIONS,
)


class AssessmentEvaluator:
    """
    Évalue les réponses d'une session d'évaluation.

    - Les questions fermées sont corrigées localement.
    - Les questions ouvertes sont évaluées par le LLM.
    - Les résultats sont regroupés par compétence et par niveau.
    - Le niveau CECRL est déterminé à partir des niveaux réellement validés.
    """

    CEFR_LEVELS = [
        "A1",
        "A2",
        "B1",
        "B2",
        "C1",
        "C2",
    ]

    LEVEL_THRESHOLDS = {
        "A1": 60,
        "A2": 60,
        "B1": 60,
        "B2": 60,
        "C1": 60,
        "C2": 60,
    }

    def __init__(self):
        self.llm = OpenRouterClient()

        self.questions_by_id = {
            question["id"]: question
            for question in ASSESSMENT_QUESTIONS
        }

    async def evaluate_answer(
                self,
                answer: dict,
        ) -> dict:
            """
            Évalue une seule réponse.

            Cette méthode est utilisée par l'évaluation
            adaptative, qui fonctionne question par question.
        """

            question_id = answer.get("question_id")

            question = self.questions_by_id.get(
                question_id
            )

            if question is None:
                raise ValueError(
                f"Question inconnue : {question_id}"
            )

            if question.get("type") == "closed":
                return self._evaluate_closed_answer(
                    answer,
                    question,
                )

            return await self._evaluate_open_answer(
                answer,
                question,
        )
    
    async def evaluate(
        self,
        answers: list[dict],
    ) -> dict:
        """
        Évalue l'ensemble des réponses.
        """

        if not answers:
            return self._empty_result()

        question_results = []

        for answer in answers:

            question_id = answer.get("question_id")

            question = self.questions_by_id.get(
                question_id
            )

            if question is None:
                continue

            if question.get("type") == "closed":
                result = self._evaluate_closed_answer(
                    answer,
                    question,
                )

            else:
                result = await self._evaluate_open_answer(
                    answer,
                    question,
                )

            question_results.append(result)

        competency_scores = (
            self._calculate_competency_scores(
                question_results
            )
        )

        level_scores = (
            self._calculate_level_scores(
                question_results
            )
        )

        validated_levels = (
            self._determine_validated_levels(
                level_scores
            )
        )

        estimated_level = (
            self._determine_level(
                level_scores
            )
        )

        overall_score = (
            self._calculate_overall_score(
                question_results
            )
        )

        strengths = self._extract_strengths(
            question_results
        )

        weak_points = self._extract_weak_points(
            question_results
        )

        errors = self._extract_errors(
            question_results
        )

        return {
            "overall_score": overall_score,
            "estimated_level": estimated_level,
            "validated_levels": validated_levels,
            "competency_scores": competency_scores,
            "level_scores": level_scores,
            "strengths": strengths,
            "weak_points": weak_points,
            "errors": errors,
            "questions": question_results,
        }

    # ==========================================================
    # QUESTIONS FERMÉES
    # ==========================================================

    def _evaluate_closed_answer(
        self,
        answer: dict,
        question: dict,
    ) -> dict:
        """
        Corrige une question fermée localement.
        """

        user_answer = str(
            answer.get("answer", "")
        ).strip()

        correct_answer = str(
            question.get("correct_answer", "")
        ).strip()

        is_correct = (
            user_answer.lower()
            == correct_answer.lower()
        )

        return {
            "question_id": question["id"],
            "level": question["level"],
            "category": question["category"],
            "type": "closed",
            "score": 100 if is_correct else 0,
            "correct": is_correct,
            "feedback": (
                "Correct."
                if is_correct
                else (
                    f"Bonne réponse : "
                    f"{correct_answer}"
                )
            ),
            "errors": (
                []
                if is_correct
                else [
                    "Réponse incorrecte."
                ]
            ),
            "strengths": (
                ["Bonne réponse."]
                if is_correct
                else []
            ),
            "weak_points": (
                []
                if is_correct
                else [
                    (
                        f"Notion {question['level']} "
                        f"à revoir."
                    )
                ]
            ),
        }

    # ==========================================================
    # QUESTIONS OUVERTES
    # ==========================================================

    async def _evaluate_open_answer(
        self,
        answer: dict,
        question: dict,
    ) -> dict:
        """
        Évalue une question ouverte avec OpenRouter.
        """

        prompt = f"""
Tu es un professeur de langue spécialisé
dans l'évaluation du niveau CECRL.

Évalue précisément la réponse de l'apprenant.

Question :
{question["question"]}

Réponse de l'apprenant :
{answer.get("answer", "")}

Compétence :
{question["category"]}

Niveau visé :
{question["level"]}

Retourne UNIQUEMENT un objet JSON valide :

{{
    "score": 0,
    "correct": false,
    "feedback": "",
    "errors": [],
    "strengths": [],
    "weak_points": []
}}

Règles :

- score doit être un nombre entier entre 0 et 100.
- Évalue réellement la qualité de la réponse.
- Ne considère pas automatiquement une réponse courte comme fausse.
- Tiens compte de la grammaire.
- Tiens compte du vocabulaire.
- Tiens compte de la compréhension de la question.
- Tiens compte de la pertinence de la réponse.
- Pour une question d'expression, évalue également la cohérence.
- Pour une réponse correcte et suffisamment maîtrisée,
  correct=true.
- Pour une réponse incorrecte ou insuffisante,
  correct=false.
- feedback doit être pédagogique et concis.
- errors doit être une liste de chaînes.
- strengths doit être une liste de chaînes.
- weak_points doit être une liste de chaînes.
- Ne retourne aucun texte en dehors du JSON.
"""

        messages = [
            {
                "role": "system",
                "content": (
                    "Tu es un évaluateur pédagogique "
                    "CECRL. Respecte strictement "
                    "le format JSON demandé."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        try:

            response = await self.llm.chat(
                messages
            )

            return self._parse_open_result(
                question,
                response,
            )

        except Exception as exc:

            return {
                "question_id": question["id"],
                "level": question["level"],
                "category": question["category"],
                "type": "open",
                "score": 0,
                "correct": False,
                "feedback": (
                    "Impossible d'évaluer "
                    "cette réponse."
                ),
                "errors": [
                    str(exc)
                ],
                "strengths": [],
                "weak_points": [],
            }

    # ==========================================================
    # PARSING
    # ==========================================================

    def _parse_open_result(
        self,
        question: dict,
        response: str,
    ) -> dict:
        """
        Transforme la réponse du LLM
        en résultat standardisé.
        """

        try:

            data = json.loads(response)

        except json.JSONDecodeError:

            return {
                "question_id": question["id"],
                "level": question["level"],
                "category": question["category"],
                "type": "open",
                "score": 0,
                "correct": False,
                "feedback": (
                    "Réponse d'évaluation invalide."
                ),
                "errors": [
                    (
                        "Le modèle n'a pas retourné "
                        "un JSON valide."
                    )
                ],
                "strengths": [],
                "weak_points": [],
            }

        score = data.get(
            "score",
            0,
        )

        try:
            score = int(score)

        except (TypeError, ValueError):
            score = 0

        score = max(
            0,
            min(score, 100),
        )

        return {
            "question_id": question["id"],
            "level": question["level"],
            "category": question["category"],
            "type": "open",
            "score": score,
            "correct": bool(
                data.get(
                    "correct",
                    False,
                )
            ),
            "feedback": data.get(
                "feedback",
                "",
            ),
            "errors": self._ensure_list(
                data.get(
                    "errors",
                    [],
                )
            ),
            "strengths": self._ensure_list(
                data.get(
                    "strengths",
                    [],
                )
            ),
            "weak_points": self._ensure_list(
                data.get(
                    "weak_points",
                    [],
                )
            ),
        }

    # ==========================================================
    # SCORES PAR COMPÉTENCE
    # ==========================================================

    def _calculate_competency_scores(
        self,
        results: list[dict],
    ) -> dict:
        """
        Calcule les scores moyens par compétence.
        """

        categories = {
            "vocabulary": [],
            "grammar": [],
            "expression": [],
            "comprehension": [],
        }

        for result in results:

            category = result.get(
                "category"
            )

            if category in categories:
                categories[category].append(
                    result["score"]
                )

        scores = {}

        for category, values in categories.items():

            if not values:
                scores[category] = None
                continue

            scores[category] = round(
                sum(values) / len(values)
            )

        return scores

    # ==========================================================
    # SCORES PAR NIVEAU
    # ==========================================================

    def _calculate_level_scores(
        self,
        results: list[dict],
    ) -> dict:
        """
        Calcule le score moyen obtenu
        pour chaque niveau CEFR.
        """

        level_values = {
            level: []
            for level in self.CEFR_LEVELS
        }

        for result in results:

            level = result.get(
                "level"
            )

            if level in level_values:
                level_values[level].append(
                    result["score"]
                )

        scores = {}

        for level, values in level_values.items():

            if not values:
                scores[level] = None
                continue

            scores[level] = round(
                sum(values) / len(values)
            )

        return scores

    # ==========================================================
    # NIVEAUX VALIDÉS
    # ==========================================================

    def _determine_validated_levels(
        self,
        level_scores: dict,
    ) -> list[str]:
        """
        Retourne les niveaux CECRL validés
        de manière progressive.

        Un niveau supérieur ne peut être validé
        que si tous les niveaux précédents évalués
        sont eux-mêmes maîtrisés.
        """

        validated = []

        for level in self.CEFR_LEVELS:

            score = level_scores.get(level)

            if score is None:
                break

            threshold = self.LEVEL_THRESHOLDS[level]

            if score < threshold:
                break

            validated.append(level)

        return validated

    # ==========================================================
    # NIVEAU FINAL
    # ==========================================================

    def _determine_level(
        self,
        level_scores: dict,
    ) -> str | None:
        """
        Détermine le niveau CECRL estimé.

        Un niveau n'est considéré comme maîtrisé que si
        son score atteint le seuil défini.

        Le système s'arrête au premier niveau évalué
        qui n'est pas suffisamment maîtrisé.
        """

        highest_validated_level = None

        for level in self.CEFR_LEVELS:

            score = level_scores.get(level)

            # Niveau non évalué
            if score is None:
                break

            threshold = self.LEVEL_THRESHOLDS[level]

            # Niveau insuffisant :
            # on ne peut pas considérer les niveaux
            # supérieurs comme maîtrisés.
            if score < threshold:
                break

            highest_validated_level = level

        return highest_validated_level

    # ==========================================================
    # SCORE GLOBAL
    # ==========================================================

    def _calculate_overall_score(
        self,
        results: list[dict],
    ) -> int:
        """
        Calcule le score global de la session.
        """

        if not results:
            return 0

        scores = [
            result["score"]
            for result in results
        ]

        return round(
            sum(scores) / len(scores)
        )

    # ==========================================================
    # ANALYSE PÉDAGOGIQUE
    # ==========================================================

    def _extract_strengths(
        self,
        results: list[dict],
    ) -> list[str]:
        """
        Récupère les points forts.
        """

        strengths = []

        for result in results:

            for strength in result.get(
                "strengths",
                [],
            ):

                if strength not in strengths:
                    strengths.append(
                        strength
                    )

        return strengths

    def _extract_weak_points(
        self,
        results: list[dict],
    ) -> list[str]:
        """
        Récupère les points faibles.
        """

        weak_points = []

        for result in results:

            for weak_point in result.get(
                "weak_points",
                [],
            ):

                if weak_point not in weak_points:
                    weak_points.append(
                        weak_point
                    )

        return weak_points

    def _extract_errors(
        self,
        results: list[dict],
    ) -> list[str]:
        """
        Récupère les erreurs.
        """

        errors = []

        for result in results:

            for error in result.get(
                "errors",
                [],
            ):

                if error not in errors:
                    errors.append(
                        error
                    )

        return errors

    # ==========================================================
    # UTILITAIRES
    # ==========================================================

    @staticmethod
    def _ensure_list(
        value,
    ) -> list:

        if isinstance(value, list):
            return value

        if value is None:
            return []

        return [str(value)]

    @staticmethod
    def _empty_result() -> dict:
        """
        Résultat lorsqu'aucune réponse
        n'est disponible.
        """

        return {
            "overall_score": 0,
            "estimated_level": None,
            "validated_levels": [],
            "competency_scores": {
                "vocabulary": None,
                "grammar": None,
                "expression": None,
                "comprehension": None,
            },
            "level_scores": {
                "A1": None,
                "A2": None,
                "B1": None,
                "B2": None,
                "C1": None,
                "C2": None,
            },
            "strengths": [],
            "weak_points": [],
            "errors": [],
            "questions": [],
        }