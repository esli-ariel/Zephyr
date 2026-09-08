from app.learning.assessment_questions import (
    ASSESSMENT_QUESTIONS,
)


class AssessmentSession:
    """
    Session d'évaluation adaptative du niveau CECRL.

    Principe :

    - Commence au niveau A1.
    - Pose d'abord quelques questions du niveau courant.
    - Si le niveau semble maîtrisé, passe au niveau supérieur.
    - Si le niveau est clairement trop difficile, arrête l'évaluation.
    - Si le résultat est intermédiaire, pose davantage de questions
      au même niveau pour confirmer.
    - La session reste indépendante du LLM.
      L'évaluation des réponses est fournie par l'extérieur.
    """

    CEFR_LEVELS = [
        "A1",
        "A2",
        "B1",
        "B2",
        "C1",
        "C2",
    ]

    # Nombre de questions initiales avant de décider
    # si l'on doit monter de niveau ou approfondir.
    INITIAL_QUESTIONS_PER_LEVEL = 3

    # Nombre maximum de questions pour un niveau.
    MAX_QUESTIONS_PER_LEVEL = 6

    # Score moyen permettant de monter au niveau supérieur.
    ADVANCE_THRESHOLD = 70

    # En dessous de ce score, le niveau est considéré
    # comme insuffisamment maîtrisé.
    STOP_THRESHOLD = 50

    def __init__(self):
        self.questions_by_level = {
            level: [
                question.copy()
                for question in ASSESSMENT_QUESTIONS
                if question["level"] == level
            ]
            for level in self.CEFR_LEVELS
        }

        self.current_level = "A1"

        self.question_index = 0

        self.answers = []

        self.level_scores = {
            level: []
            for level in self.CEFR_LEVELS
        }

        self.level_question_counts = {
            level: 0
            for level in self.CEFR_LEVELS
        }

        self.pending_answer_index = None

        self.finished = False

        self.stop_reason = None

    def get_current_question(self) -> dict | None:
        """
        Retourne la question actuellement active.
        """

        if self.finished:
            return None

        questions = self.questions_by_level.get(
            self.current_level,
            [],
        )

        if self.question_index >= len(questions):
            return None

        question = questions[
            self.question_index
        ].copy()

        # Ne jamais exposer la réponse correcte
        # au client.
        question.pop(
            "correct_answer",
            None,
        )

        return question

    def submit_answer(
        self,
        answer: str,
    ) -> dict:
        """
        Enregistre une réponse.

        La progression n'est pas encore décidée ici,
        car la réponse doit d'abord être évaluée.

        Utiliser ensuite record_evaluation(score).
        """

        if self.finished:
            raise ValueError(
                "L'évaluation est déjà terminée."
            )

        if self.pending_answer_index is not None:
            raise ValueError(
                "La réponse précédente doit être "
                "évaluée avant de continuer."
            )

        question = self._get_active_question()

        if question is None:
            raise ValueError(
                "Aucune question active."
            )

        answer = str(answer).strip()

        if not answer:
            raise ValueError(
                "La réponse ne peut pas être vide."
            )

        record = {
            "question_id": question["id"],
            "category": question["category"],
            "level": question["level"],
            "type": question.get("type"),
            "question": question["question"],
            "answer": answer,
        }

        self.answers.append(record)

        self.pending_answer_index = (
            len(self.answers) - 1
        )

        return {
            "question_id": question["id"],
            "answer_recorded": True,
            "needs_evaluation": True,
            "current_level": self.current_level,
            "finished": False,
        }

    def record_evaluation(
        self,
        score: int,
    ) -> dict:
        """
        Enregistre le score d'une réponse et décide
        de la progression de l'évaluation.

        Le score doit être compris entre 0 et 100.
        """

        if self.finished:
            raise ValueError(
                "L'évaluation est déjà terminée."
            )

        if self.pending_answer_index is None:
            raise ValueError(
                "Aucune réponse en attente "
                "d'évaluation."
            )

        try:
            score = int(score)

        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Le score doit être un nombre."
            ) from exc

        score = max(
            0,
            min(score, 100),
        )

        answer = self.answers[
            self.pending_answer_index
        ]

        answer["score"] = score

        self.level_scores[
            self.current_level
        ].append(score)

        self.level_question_counts[
            self.current_level
        ] += 1

        self.pending_answer_index = None

        self.question_index += 1

        return self._decide_progression()

    def _decide_progression(self) -> dict:
        """
        Détermine la prochaine étape.
        """

        level = self.current_level

        scores = self.level_scores[level]

        question_count = len(scores)

        average_score = round(
            sum(scores) / len(scores)
        )

        # Cas 1 : performance insuffisante.
        if (
            question_count
            >= self.INITIAL_QUESTIONS_PER_LEVEL
            and average_score
            < self.STOP_THRESHOLD
        ):
            self.finished = True

            self.stop_reason = (
                "niveau_insuffisant"
            )

            return self._progression_result(
                action="stop",
                average_score=average_score,
            )

        # Cas 2 : niveau clairement maîtrisé.
        if (
            question_count
            >= self.INITIAL_QUESTIONS_PER_LEVEL
            and average_score
            >= self.ADVANCE_THRESHOLD
        ):
            if level == "C2":
                self.finished = True

                self.stop_reason = (
                    "niveau_maximum_atteint"
                )

                return self._progression_result(
                    action="finish",
                    average_score=average_score,
                )

            self._move_to_next_level()

            return self._progression_result(
                action="advance",
                average_score=average_score,
            )

        # Cas 3 : résultat intermédiaire.
        # On continue au même niveau jusqu'à
        # atteindre le nombre maximal de questions.
        if (
            question_count
            < self.MAX_QUESTIONS_PER_LEVEL
        ):
            return self._progression_result(
                action="continue",
                average_score=average_score,
            )

        # Cas 4 : toutes les questions du niveau
        # ont été utilisées.
        self.finished = True

        self.stop_reason = (
            "niveau_confirme"
        )

        return self._progression_result(
            action="finish",
            average_score=average_score,
        )

    def _move_to_next_level(self) -> None:
        """
        Passe au niveau CECRL suivant.
        """

        current_index = (
            self.CEFR_LEVELS.index(
                self.current_level
            )
        )

        next_index = current_index + 1

        if next_index >= len(
            self.CEFR_LEVELS
        ):
            self.finished = True
            self.stop_reason = (
                "niveau_maximum_atteint"
            )
            return

        self.current_level = (
            self.CEFR_LEVELS[next_index]
        )

        self.question_index = 0

    def _get_active_question(self) -> dict | None:
        """
        Retourne la question active sans exposer
        la réponse correcte.
        """

        questions = self.questions_by_level.get(
            self.current_level,
            [],
        )

        if self.question_index >= len(
            questions
        ):
            return None

        return questions[
            self.question_index
        ]

    def get_progress(self) -> dict:
        """
        Retourne l'état actuel de l'évaluation.
        """

        current_scores = self.level_scores[
            self.current_level
        ]

        if current_scores:
            current_average = round(
                sum(current_scores)
                / len(current_scores)
            )
        else:
            current_average = None

        return {
            "current_level": self.current_level,
            "question_number": (
                self.question_index + 1
            ),
            "answered": len(self.answers),
            "total_answered": len(
                self.answers
            ),
            "current_level_answered": len(
                current_scores
            ),
            "current_level_average": (
                current_average
            ),
            "initial_questions": (
                self.INITIAL_QUESTIONS_PER_LEVEL
            ),
            "max_questions_per_level": (
                self.MAX_QUESTIONS_PER_LEVEL
            ),
            "finished": self.finished,
            "stop_reason": self.stop_reason,
        }

    def get_answers(self) -> list[dict]:
        """
        Retourne une copie des réponses.
        """

        return [
            answer.copy()
            for answer in self.answers
        ]

    def get_level_scores(self) -> dict:
        """
        Retourne les scores obtenus par niveau.
        """

        return {
            level: scores.copy()
            for level, scores
            in self.level_scores.items()
        }

    def get_result(self) -> dict:
        """
        Retourne le résultat courant de la session.
        """

        validated_levels = []

        for level in self.CEFR_LEVELS:
            scores = self.level_scores[level]

            if not scores:
                break

            average = round(
                sum(scores) / len(scores)
            )

            if average < self.STOP_THRESHOLD:
                break

            validated_levels.append(level)

        estimated_level = (
            validated_levels[-1]
            if validated_levels
            else None
        )

        return {
            "estimated_level": estimated_level,
            "validated_levels": validated_levels,
            "level_scores": self.get_level_scores(),
            "answers": self.get_answers(),
            "finished": self.finished,
            "stop_reason": self.stop_reason,
        }

    def reset(self) -> None:
        """
        Réinitialise complètement la session.
        """

        self.current_level = "A1"

        self.question_index = 0

        self.answers.clear()

        self.level_scores = {
            level: []
            for level in self.CEFR_LEVELS
        }

        self.level_question_counts = {
            level: 0
            for level in self.CEFR_LEVELS
        }

        self.pending_answer_index = None

        self.finished = False

        self.stop_reason = None

    def _progression_result(
        self,
        action: str,
        average_score: int,
    ) -> dict:
        """
        Construit la réponse standard de progression.
        """

        return {
            "action": action,
            "current_level": self.current_level,
            "average_score": average_score,
            "finished": self.finished,
            "stop_reason": self.stop_reason,
            "next_question": (
                self.get_current_question()
            ),
        }