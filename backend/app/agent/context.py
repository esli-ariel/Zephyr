from app.agent.prompts import ZEPHYR_SYSTEM_PROMPT
from app.memory.memory_manager import MemoryManager
from app.learning.learner_manager import LearnerProfileManager


class ContextBuilder:
    """
    Construit le contexte complet envoyé au modèle de langage.
    """

    def __init__(
        self,
        memory: MemoryManager,
        learner: LearnerProfileManager,
    ):
        self.memory = memory
        self.learner = learner

    def build(self) -> list[dict]:
        """
        Construit les messages envoyés à OpenRouter.
        """

        profile = self.learner.get_profile()

        profile_context = f"""
Profil actuel de l'apprenant :

Nom : {profile["name"]}
Langue cible : {profile["target_language"]}
Niveau : {profile["level"]}
Objectifs : {profile["goals"]}
Points faibles : {profile["weak_points"]}
Vocabulaire appris : {profile["learned_vocabulary"]}
Erreurs fréquentes : {profile["common_mistakes"]}

Utilise ces informations lorsque cela est pertinent
pour personnaliser ton enseignement.
"""

        messages = [
            {
                "role": "system",
                "content": ZEPHYR_SYSTEM_PROMPT,
            },
            {
                "role": "system",
                "content": profile_context,
            },
        ]

        messages.extend(
            self.memory.get_conversation()
        )

        return messages