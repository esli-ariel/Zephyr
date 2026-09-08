# 📓 Journal de développement — Zéphyr

## 04/09/2026

### 🎯 Objectif

Mettre en place les fondations techniques de l'assistant intelligent Zéphyr.

### ✅ Travaux réalisés

* Création du dossier racine `zephyr/`
* Mise en place de l'architecture générale.
* Création du backend Python.
* Création de l'environnement virtuel.
* Installation de FastAPI.
* Création de l'application FastAPI.
* Création des routes de test.
* Création de la classe `ZephyrAgent`.
* Création du système de prompt.
* Mise en place de la documentation du projet.

### 🧱 Architecture initiale

```text
Zéphyr
│
├── Frontend
│
├── Backend
│   └── FastAPI
│
├── Agent
│
├── Mémoire
│
├── Voix
│
├── Vision
│
├── Apprentissage
│
└── Avatar
```

### 🧪 Tests réalisés

La route `/health` permet de vérifier que le backend fonctionne correctement.

Résultat attendu :

```json
{
    "status": "healthy"
}
```

### ⏭️ Prochaine étape

Connecter Zéphyr à OpenRouter afin qu'il puisse produire de véritables réponses générées par une IA.

### 📌 Statut

🟢 Fondation initiale terminée.

## 07/09/2026 — Connexion de Zéphyr à OpenRouter

### Objectif

Connecter le cerveau de Zéphyr à un véritable modèle de langage afin de permettre des conversations intelligentes.

### Travaux réalisés

- Installation de `httpx`.
- Configuration de la clé API OpenRouter dans `.env`.
- Configuration du modèle `openrouter/free`.
- Création du client `OpenRouterClient`.
- Connexion de `ZephyrAgent` au client OpenRouter.
- Création de l'endpoint `POST /api/chat`.
- Validation des messages utilisateur.
- Gestion des erreurs de configuration.
- Gestion des erreurs retournées par OpenRouter.
- Test réel avec le message :
  `Bonjour Zéphyr, qui es-tu ?`

### Résultat

Zéphyr reçoit correctement un message utilisateur, l'envoie à OpenRouter et retourne une réponse générée par le modèle IA.

### Statut

✅ Terminé

### Prochaine étape

Mettre en place le contexte conversationnel afin que Zéphyr puisse conserver les messages précédents d'une conversation.

## 07/09/2026 — Mémoire conversationnelle V0.3.0

### Objectif

Permettre à Zéphyr de conserver et exploiter le contexte récent d'une conversation.

### Travaux réalisés

- Création de `ShortTermMemory`.
- Création de `MemoryManager`.
- Création de `ContextBuilder`.
- Intégration de la mémoire dans `ZephyrAgent`.
- Ajout de la consultation de la mémoire.
- Ajout de l'effacement de la mémoire.
- Limitation de l'historique à 20 messages.
- Limitation des messages utilisateur à 5000 caractères.
- Tests de mémorisation et de rappel.

### Résultat

Zéphyr peut désormais utiliser les échanges précédents d'une conversation pour générer ses réponses.

### Statut

✅ Terminé

## 07/09/2026 — Extraction automatique du profil V0.4.1

### Objectif

Permettre à Zéphyr d'identifier automatiquement les informations importantes concernant l'apprenant à partir de ses messages.

### Travaux réalisés

- Création de `ProfileExtractor`.
- Utilisation d'OpenRouter pour l'extraction structurée.
- Extraction du nom.
- Extraction de la langue cible.
- Extraction du niveau.
- Extraction des objectifs.
- Intégration de l'extracteur dans `ZephyrAgent`.
- Mise à jour automatique de `LearnerProfile`.
- Vérification du fonctionnement avec des informations absentes.

### Tests réalisés

- Extraction indépendante du profil.
- Test d'un message contenant plusieurs informations.
- Test d'un message ne contenant aucune information de profil.
- Test complet via `/api/chat`.
- Vérification via `/api/learner/profile`.

### Résultat

Zéphyr peut désormais identifier automatiquement certaines informations concernant l'apprenant et les enregistrer dans son profil.

### Statut

✅ Terminé

## 08/09/2026 — V0.5 terminée

### Objectif

Construire un système complet d'évaluation intelligente du niveau
de l'apprenant selon le CECRL.

### Réalisations

- Création de la banque de 36 questions.
- Mise en place de l'évaluation des questions fermées.
- Mise en place de l'évaluation des questions ouvertes avec le LLM.
- Calcul des scores par compétence.
- Calcul des scores par niveau.
- Détermination progressive du niveau CECRL.
- Mise en place de l'évaluation adaptative.
- Création de l'orchestrateur `AdaptiveAssessment`.
- Création des endpoints FastAPI.
- Intégration des résultats dans `LearnerProfile`.
- Ajout de l'historique des évaluations.
- Protection contre les doublons.
- Ajout des tests automatisés.

### Tests

Tous les tests automatisés sont passés avec succès.

### Résultat

V0.5 validée.

### Statut

✅ Terminé