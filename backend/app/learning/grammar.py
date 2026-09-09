from dataclasses import dataclass, field


@dataclass
class GrammarRule:
    rule: str
    explanation: str
    language: str
    level: str
    category: str = "general"
    examples: list[str] = field(default_factory=list)
    difficulty: int = 1
    review_count: int = 0
    correct_count: int = 0
    incorrect_count: int = 0
    mastery: float = 0.0

    def register_correct_answer(self) -> None:
        self.review_count += 1
        self.correct_count += 1
        self._update_mastery()

    def register_incorrect_answer(self) -> None:
        self.review_count += 1
        self.incorrect_count += 1
        self._update_mastery()

    def _update_mastery(self) -> None:
        if self.review_count == 0:
            self.mastery = 0.0
            return

        self.mastery = round(
            (self.correct_count / self.review_count) * 100,
            2,
        )

    def to_dict(self) -> dict:
        return {
            "rule": self.rule,
            "explanation": self.explanation,
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


class GrammarManager:
    def __init__(self):
        self.rules: dict[str, GrammarRule] = {}

    def add_rule(
        self,
        rule: str,
        explanation: str,
        language: str,
        level: str,
        category: str = "general",
        examples: list[str] | None = None,
        difficulty: int = 1,
    ) -> GrammarRule:

        key = self._normalize(rule)

        if key in self.rules:
            return self.rules[key]

        grammar_rule = GrammarRule(
            rule=rule.strip(),
            explanation=explanation.strip(),
            language=language,
            level=level,
            category=category,
            examples=examples or [],
            difficulty=max(1, min(difficulty, 5)),
        )

        self.rules[key] = grammar_rule

        return grammar_rule

    def get_rule(self, rule: str) -> GrammarRule | None:
        return self.rules.get(self._normalize(rule))

    def remove_rule(self, rule: str) -> bool:
        key = self._normalize(rule)

        if key not in self.rules:
            return False

        del self.rules[key]

        return True

    def register_answer(
        self,
        rule: str,
        correct: bool,
    ) -> None:

        grammar_rule = self.get_rule(rule)

        if grammar_rule is None:
            return

        if correct:
            grammar_rule.register_correct_answer()
        else:
            grammar_rule.register_incorrect_answer()

    def get_all_rules(self) -> list[GrammarRule]:
        return list(self.rules.values())

    def get_rules_to_review(
        self,
        mastery_threshold: float = 70,
    ) -> list[GrammarRule]:

        return [
            rule
            for rule in self.rules.values()
            if rule.mastery < mastery_threshold
        ]

    def get_mastered_rules(
        self,
        mastery_threshold: float = 80,
    ) -> list[GrammarRule]:

        return [
            rule
            for rule in self.rules.values()
            if rule.mastery >= mastery_threshold
        ]

    def get_statistics(self) -> dict:
        rules = self.get_all_rules()

        if not rules:
            return {
                "total_rules": 0,
                "mastered_rules": 0,
                "rules_to_review": 0,
                "average_mastery": 0,
            }

        total_mastery = sum(
            rule.mastery
            for rule in rules
        )

        return {
            "total_rules": len(rules),
            "mastered_rules": len(
                self.get_mastered_rules()
            ),
            "rules_to_review": len(
                self.get_rules_to_review()
            ),
            "average_mastery": round(
                total_mastery / len(rules),
                2,
            ),
        }

    def clear(self) -> None:
        self.rules.clear()

    @staticmethod
    def _normalize(rule: str) -> str:
        return rule.strip().lower()