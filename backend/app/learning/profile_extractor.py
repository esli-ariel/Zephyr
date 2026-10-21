from app.learning.llm_schemas import ProfileResponse, parse_response

from app.llm.openrouter import OpenRouterClient


class ProfileExtractor:
    """
    Extrait automatiquement les informations importantes
    concernant l'apprenant à partir de ses messages.
    """

    EXTRACTION_PROMPT = """
Tu es un système d'extraction de profil d'apprenant.

Analyse le message de l'utilisateur et identifie uniquement
les informations que l'utilisateur donne explicitement
ou qui sont clairement déductibles.

Retourne UNIQUEMENT un objet JSON valide avec exactement
ces champs :

{
    "name": null,
    "target_language": null,
    "level": null,
    "goals": []
}

Règles :

- name : prénom ou nom donné par l'utilisateur.
- target_language : langue que l'utilisateur souhaite apprendre.
- level : uniquement A1, A2, B1, B2, C1 ou C2 si indiqué explicitement ; sinon null.
- goals : liste des objectifs d'apprentissage.
- Si une information n'est pas présente, utilise null.
- Si aucun objectif n'est indiqué, utilise [].
- Ne fais aucune supposition.
- Ne réponds pas à l'utilisateur.
- Retourne uniquement le JSON.

Message utilisateur :
"""

    def __init__(self):
        self.llm = OpenRouterClient()

    async def extract(self, message: str) -> dict:
        """
        Extrait les informations du profil depuis un message.
        """

        prompt = self.EXTRACTION_PROMPT + message

        messages = [
            {
                "role": "system",
                "content": (
                    "Tu es un extracteur de données. "
                    "Tu dois respecter strictement le format JSON."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        response = await self.llm.chat(messages)

        return self._parse_response(response)

    def _parse_response(self, response: str) -> dict:
        """
        Convertit la réponse du modèle en dictionnaire.
        """

        return parse_response(ProfileResponse, response)
