from app.agent.context import ContextBuilder
from app.llm.openrouter import OpenRouterClient
from app.memory.memory_manager import MemoryManager
from app.learning.learner_manager import LearnerProfileManager
from app.learning.profile_extractor import ProfileExtractor


class ZephyrAgent:

    def __init__(self):
        self.name = "Zéphyr"

        self.llm = OpenRouterClient()

        self.memory = MemoryManager()

        self.learner = LearnerProfileManager()

        self.profile_extractor = ProfileExtractor()

        self.context = ContextBuilder(
            memory=self.memory,
            learner=self.learner,
        )
        

    async def process(self, message: str) -> str:
        """
        Traite un message utilisateur et met automatiquement
        à jour le profil de l'apprenant.
        """

        extracted_profile = await self.profile_extractor.extract(
            message
        )

        self._update_profile(extracted_profile)

        self.memory.add_user_message(message)

        messages = self.context.build()

        response = await self.llm.chat(messages)

        self.memory.add_assistant_message(response)

        return response

    def clear_memory(self) -> None:
        """
        Efface la mémoire conversationnelle.
        """

        self.memory.clear_conversation()

    def get_learner_profile(self) -> dict:
        """
        Retourne le profil de l'apprenant.
        """

        return self.learner.get_profile()

    def clear_learner_profile(self) -> None:
        """
        Réinitialise le profil de l'apprenant.
        """

        self.learner.clear_profile()

    def _update_profile(self, extracted: dict) -> None:
        """
        Met à jour le profil à partir des informations extraites.
        """

        if extracted.get("name"):
            self.learner.set_name(
                extracted["name"]
            )

        if extracted.get("target_language"):
            self.learner.set_target_language(
                extracted["target_language"]
            )

        if extracted.get("level"):
            self.learner.set_level(
                extracted["level"]
            )

        for goal in extracted.get("goals", []):
            self.learner.add_goal(goal)

    def apply_assessment_result(
        self,
        result: dict,
    ) -> None:
        """
        Applique un résultat d'évaluation
        au profil de l'apprenant.
        """

        self.learner.apply_assessment_result(
            result
        )