import uuid

from app.learning.exercise import Exercise
from app.learning.lesson import Lesson
from app.learning.lesson_generator import LessonGenerator
from app.learning.exercise_generator import (
    ExerciseGenerator,
)
from app.learning.exercise_evaluator import (
    ExerciseEvaluator,
)
from app.learning.vocabulary import (
    VocabularyManager,
)


class LearningEngine:
    """
    Moteur pédagogique de Zéphyr.

    Il organise les contenus pédagogiques en fonction
    du profil de l'apprenant.
    """

    def __init__(self, learner_manager=None):
        self.learner = learner_manager
        
        self.lessons: list[Lesson] = []
        self.exercises: list[Exercise] = []
        self.lesson_generator = LessonGenerator()
        self.exercise_generator = ExerciseGenerator()
        self.exercise_evaluator = ExerciseEvaluator()

        self.vocabulary = VocabularyManager()

    def create_lesson(
        self,
        title: str,
        language: str,
        level: str,
        topic: str,
        objectives: list[str] | None = None,
    ) -> Lesson:

        lesson = Lesson(
            id=str(uuid.uuid4()),
            title=title,
            language=language,
            level=level,
            topic=topic,
            objectives=objectives or [],
        )

        self.lessons.append(lesson)

        return lesson

    def create_exercise(
        self,
        exercise_type: str,
        question: str,
        level: str,
        skill: str,
        options: list[str] | None = None,
        expected_answer: str | None = None,
        difficulty: int = 1,
    ) -> Exercise:

        exercise = Exercise(
            id=str(uuid.uuid4()),
            exercise_type=exercise_type,
            question=question,
            level=level,
            skill=skill,
            options=options or [],
            expected_answer=expected_answer,
            difficulty=difficulty,
        )

        self.exercises.append(exercise)

        return exercise

    def get_lessons(self) -> list[Lesson]:
        return self.lessons.copy()

    def get_exercises(self) -> list[Exercise]:
        return self.exercises.copy()

    def get_learning_context(self) -> dict:
        """
        Retourne le contexte pédagogique actuel
        de l'apprenant.
        """

        if self.learner is None:
            return {
                "name": None,
                "target_language": None,
                "level": None,
                "goals": [],
                "weak_points": [],
                "learned_vocabulary": [],
                "common_mistakes": [],
                "competency_scores": {},
                "assessment_history": [],
            }

        return self.learner.get_profile()

    def clear(self) -> None:
        self.lessons.clear()
        self.exercises.clear()

    async def generate_lesson(
        self,
        topic: str,
        ) -> Lesson:
        """
        Génère une leçon adaptée au profil
        de l'apprenant.
        """

        context = self.get_learning_context()

        language = context.get("target_language")
        level = context.get("level")

        if not language:
            raise ValueError(
            "La langue cible de l'apprenant "
            "n'est pas définie."
        )

        if not level:
            raise ValueError(
                "Le niveau de l'apprenant "
                "n'est pas défini."
            )

        lesson = await self.lesson_generator.generate(
            language=language,
            level=level,
            topic=topic,
            objectives=context.get(
                "goals",
                [],
            ),
            weak_points=context.get(
                "weak_points",
                [],
            ),
            common_mistakes=context.get(
                "common_mistakes",
                [],
            ),
        )

        self.lessons.append(lesson)

        return lesson

    async def generate_exercises(
        self,
        topic: str,
        skill: str,
        count: int = 5,
    ) -> list[Exercise]:
        """
        Génère des exercices adaptés au profil
        de l'apprenant.
        """

        context = self.get_learning_context()

        language = context.get("target_language")
        level = context.get("level")

        if not language:
            raise ValueError(
                "La langue cible de l'apprenant "
                "n'est pas définie."
            )

        if not level:
            raise ValueError(
                "Le niveau de l'apprenant "
                "n'est pas défini."
            )

        exercises = await self.exercise_generator.generate(
            language=language,
            level=level,
            topic=topic,
            skill=skill,
            count=count,
            objectives=context.get(
                "goals",
                [],
            ),
            weak_points=context.get(
                "weak_points",
                [],
            ),
        )

        self.exercises.extend(exercises)

        return exercises

    async def evaluate_exercise(
        self,
        exercise: Exercise,
        answer: str,
    ) -> dict:
        """
        Évalue une réponse à un exercice.
        """

        return await self.exercise_evaluator.evaluate(
            exercise,
            answer,
        )

    def add_vocabulary(
        self,
        word: str,
        translation: str,
        category: str = "general",
        examples: list[str] | None = None,
        difficulty: int = 1,
    ):
        """
        Ajoute un mot au vocabulaire de l'apprenant.
        """

        context = self.get_learning_context()

        language = context.get(
            "target_language"
        )

        level = context.get("level")

        if not language:
            raise ValueError(
            "La langue cible de l'apprenant "
            "n'est pas définie."
            )

        if not level:
            raise ValueError(
                "Le niveau de l'apprenant "
                "n'est pas défini."
            )

        item = self.vocabulary.add_word(
                word=word,
            translation=translation,
            language=language,
            level=level,
            category=category,
            examples=examples,
            difficulty=difficulty,
        )

        self.learner.add_learned_vocabulary(
            word
        )

        return item

    def register_vocabulary_answer(
        self,
        word: str,
        correct: bool,
    ) -> None:
        """
        Enregistre une réponse concernant
        un mot de vocabulaire.
        """

        self.vocabulary.register_answer(
            word,
            correct,
        )

    def get_vocabulary_statistics(
        self,
    ) -> dict:
        return self.vocabulary.get_statistics()