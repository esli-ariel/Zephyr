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
from app.learning.grammar import GrammarManager
from app.learning.recommendation import RecommendationEngine


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
        self.grammar = GrammarManager()

        self.vocabulary = VocabularyManager()
        self.grammar = GrammarManager()

        self.recommendation = RecommendationEngine(
            learner_manager=self.learner,
            vocabulary_manager=self.vocabulary,
            grammar_manager=self.grammar,
        )

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
                "grammar_mastery": {},
                "grammar_history": [],
            }

        profile = self.learner.get_profile()

        return {
            "name": profile["name"],
            "target_language": profile["target_language"],
            "level": profile["level"],
            "goals": profile["goals"],
            "weak_points": profile["weak_points"],
            "learned_vocabulary": profile["learned_vocabulary"],
            "common_mistakes": profile["common_mistakes"],
            "competency_scores": profile["competency_scores"],
            "assessment_history": profile["assessment_history"],
            "grammar_mastery": profile["grammar_mastery"],
            "grammar_history": profile["grammar_history"],
        }

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

    def add_grammar_rule(
        self,
        rule: str,
        explanation: str,
        category: str = "general",
        examples: list[str] | None = None,
        difficulty: int = 1,
    ):
        context = self.get_learning_context()

        language = context.get("target_language")
        level = context.get("level")

        if not language:
            raise ValueError(
                "La langue cible de l'apprenant n'est pas définie."
            )

        if not level:
            raise ValueError(
                "Le niveau de l'apprenant n'est pas défini."
            )

        return self.grammar.add_rule(
            rule=rule,
            explanation=explanation,
            language=language,
            level=level,
            category=category,
            examples=examples,
            difficulty=difficulty,
        )


    def register_grammar_answer(
        self,
        rule: str,
        correct: bool,
    ) -> None:

        self.grammar.register_answer(
            rule,
            correct,
        )

        grammar_rule = self.grammar.get_rule(rule)

        if grammar_rule is None:
            return

        if self.learner is not None:
            self.learner.update_grammar_mastery(
                rule=grammar_rule.rule,
                mastery=grammar_rule.mastery,
            )

            self.learner.add_grammar_history(
                rule=grammar_rule.rule,
                correct=correct,
                mastery=grammar_rule.mastery,
            )
        


    def get_grammar_statistics(self) -> dict:
        return self.grammar.get_statistics()


    def get_grammar_to_review(self):
        return self.grammar.get_rules_to_review()


    def get_mastered_grammar(self):
        return self.grammar.get_mastered_rules()

    def get_recommendations(
        self,
        limit: int = 5,
    ) -> list[dict]:
        recommendations = self.recommendation.generate(
            limit=limit
        )

        return [
            recommendation.to_dict()
            for recommendation in recommendations
        ]