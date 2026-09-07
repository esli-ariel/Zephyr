from app.learning.learner import LearnerProfile


class LearnerProfileManager:
    """
    Gestionnaire du profil d'apprentissage de Zéphyr.
    """

    def __init__(self):
        self.profile = LearnerProfile()

    def set_name(self, name: str) -> None:
        self.profile.name = name.strip()

    def set_target_language(self, language: str) -> None:
        self.profile.target_language = language.strip()

    def set_level(self, level: str) -> None:
        self.profile.level = level.strip()

    def add_goal(self, goal: str) -> None:
        goal = goal.strip()

        if goal and goal not in self.profile.goals:
            self.profile.goals.append(goal)

    def add_weak_point(self, weak_point: str) -> None:
        weak_point = weak_point.strip()

        if weak_point and weak_point not in self.profile.weak_points:
            self.profile.weak_points.append(weak_point)

    def add_vocabulary(self, word: str) -> None:
        word = word.strip()

        if word and word not in self.profile.learned_vocabulary:
            self.profile.learned_vocabulary.append(word)

    def add_common_mistake(self, mistake: str) -> None:
        mistake = mistake.strip()

        if mistake and mistake not in self.profile.common_mistakes:
            self.profile.common_mistakes.append(mistake)

    def get_profile(self) -> dict:
        return self.profile.to_dict()

    def clear_profile(self) -> None:
        self.profile = LearnerProfile()