from dataclasses import dataclass, field


@dataclass
class VocabularyItem:
    """
    Représente un élément de vocabulaire appris
    par l'utilisateur.
    """

    word: str
    translation: str

    language: str
    level: str

    category: str = "general"

    examples: list[str] = field(
        default_factory=list
    )

    difficulty: int = 1

    review_count: int = 0
    correct_count: int = 0
    incorrect_count: int = 0

    mastery: float = 0.0

    def register_correct_answer(self) -> None:
        """
        Enregistre une bonne réponse.
        """

        self.review_count += 1
        self.correct_count += 1

        self._update_mastery()

    def register_incorrect_answer(self) -> None:
        """
        Enregistre une mauvaise réponse.
        """

        self.review_count += 1
        self.incorrect_count += 1

        self._update_mastery()

    def _update_mastery(self) -> None:
        """
        Calcule le niveau de maîtrise
        à partir des réponses.
        """

        if self.review_count == 0:
            self.mastery = 0.0
            return

        self.mastery = round(
            (
                self.correct_count
                / self.review_count
            ) * 100,
            2,
        )

    def to_dict(self) -> dict:
        return {
            "word": self.word,
            "translation": self.translation,
            "language": self.language,
            "level": self.level,
            "category": self.category,
            "examples": self.examples,
            "difficulty": self.difficulty,
            "review_count": self.review_count,
            "correct_count": self.correct_count,
            "incorrect_count": self.incorrect_count,
            "mastery": self.mastery,
        }

class VocabularyManager:
    """
    Gestionnaire du vocabulaire de l'apprenant.
    """

    def __init__(self):
        self.items: dict[str, VocabularyItem] = {}

    def add_word(
        self,
        word: str,
        translation: str,
        language: str,
        level: str,
        category: str = "general",
        examples: list[str] | None = None,
        difficulty: int = 1,
    ) -> VocabularyItem:
        """
        Ajoute un mot au vocabulaire.

        Si le mot existe déjà, retourne l'élément existant.
        """

        key = self._normalize(word)

        if key in self.items:
            return self.items[key]

        item = VocabularyItem(
            word=word.strip(),
            translation=translation.strip(),
            language=language,
            level=level,
            category=category,
            examples=examples or [],
            difficulty=max(
                1,
                min(difficulty, 5),
            ),
        )

        self.items[key] = item

        return item

    def get_word(
        self,
        word: str,
    ) -> VocabularyItem | None:
        """
        Recherche un mot.
        """

        return self.items.get(
            self._normalize(word)
        )

    def remove_word(
        self,
        word: str,
    ) -> bool:
        """
        Supprime un mot.

        Retourne True si le mot existait.
        """

        key = self._normalize(word)

        if key not in self.items:
            return False

        del self.items[key]

        return True

    def register_answer(
        self,
        word: str,
        correct: bool,
    ) -> None:
        """
        Enregistre le résultat d'une réponse.
        """

        item = self.get_word(word)

        if item is None:
            return

        if correct:
            item.register_correct_answer()
        else:
            item.register_incorrect_answer()

    def get_all_words(self) -> list[VocabularyItem]:
        return list(self.items.values())

    def get_words_to_review(
        self,
        mastery_threshold: float = 70,
    ) -> list[VocabularyItem]:
        """
        Retourne les mots dont la maîtrise
        est inférieure au seuil.
        """

        return [
            item
            for item in self.items.values()
            if item.mastery < mastery_threshold
        ]

    def get_mastered_words(
        self,
        mastery_threshold: float = 80,
    ) -> list[VocabularyItem]:
        """
        Retourne les mots maîtrisés.
        """

        return [
            item
            for item in self.items.values()
            if item.mastery >= mastery_threshold
        ]

    def get_statistics(self) -> dict:
        words = self.get_all_words()

        if not words:
            return {
                "total_words": 0,
                "mastered_words": 0,
                "words_to_review": 0,
                "average_mastery": 0,
            }

        total_mastery = sum(
            item.mastery
            for item in words
        )

        return {
            "total_words": len(words),
            "mastered_words": len(
                self.get_mastered_words()
            ),
            "words_to_review": len(
                self.get_words_to_review()
            ),
            "average_mastery": round(
                total_mastery / len(words),
                2,
            ),
        }

    def clear(self) -> None:
        self.items.clear()

    @staticmethod
    def _normalize(word: str) -> str:
        return word.strip().lower()