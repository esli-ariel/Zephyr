from app.learning.assessment import AssessmentSession
from app.learning.assessment_evaluator import (
    AssessmentEvaluator,
)
import uuid


class AdaptiveAssessment:
    """
    Orchestrateur de l'évaluation adaptative.

    Il fait le lien entre :

    - AssessmentSession
      → gestion de la progression

    - AssessmentEvaluator
      → évaluation des réponses
    """

    def __init__(self):
        self.session = AssessmentSession()
        self.evaluator = AssessmentEvaluator()
        self.assessment_id = str(uuid.uuid4())
        self.final_result = None

    def get_current_question(self) -> dict | None:
        """
        Retourne la question actuellement proposée.
        """

        return self.session.get_current_question()

    async def submit_answer(
        self,
        answer: str,
    ) -> dict:
        """
        Enregistre et évalue une réponse.

        Puis transmet le score au moteur adaptatif.
        """

        submission = self.session.submit_answer(
            answer
        )

        answers = self.session.get_answers()

        current_answer = answers[-1]

        evaluation = await self.evaluator.evaluate_answer(
            current_answer
        )

        progression = self.session.record_evaluation(
            evaluation["score"]
        )

        return {
            "question_id": submission[
                "question_id"
            ],
            "answer": answer,
            "evaluation": evaluation,
            "progression": progression,
            "progress": self.session.get_progress(),
            "finished": self.session.finished,
        }

    def get_progress(self) -> dict:
        return self.session.get_progress()

    async def get_final_result(self) -> dict:
        """
        Retourne le résultat final de l'évaluation.

        Le résultat est calculé une seule fois
        pour une session donnée.
        """

        if self.final_result is not None:
            return self.final_result

        answers = self.session.get_answers()

        if not answers:
            result = self.session.get_result()

            result["assessment_id"] = (
            self.assessment_id
            )

            self.final_result = result

            return result

        result = await self.evaluator.evaluate(
        answers
        )

        result["assessment_id"] = (
        self.assessment_id
        )

        self.final_result = result

        return result

    def get_result(self) -> dict:
        return self.session.get_result()
    
    def reset(self) -> None:
        """
        Démarre une nouvelle session d'évaluation.
        """

        self.assessment_id = str(uuid.uuid4())

        self.session.reset()

        self.final_result = None