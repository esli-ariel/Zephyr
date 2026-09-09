# 📋 Changelog — Zéphyr

Toutes les modifications importantes du projet sont enregistrées ici.

## [0.1.0] — 04/09/2026

### Added

* Architecture initiale du projet.
* Backend FastAPI.
* Environnement virtuel Python.
* API `/`.
* API `/health`.
* Classe `ZephyrAgent`.
* Système initial de prompts.
* Documentation du projet.
* Journal de progression.
* Registre des décisions techniques.
* Registre des bugs.

### Next

* Connexion à OpenRouter.
* Première interaction avec le modèle IA.
* Gestion des erreurs API.
* Création de la première interface frontend.

## [0.2.0] - 07/09/2026

### Ajouté

- Intégration d'OpenRouter.
- Client `OpenRouterClient`.
- Communication avec un modèle de langage.
- Endpoint `POST /api/chat`.
- Validation des messages.
- Gestion des erreurs OpenRouter.
- Première interaction réelle avec Zéphyr.

### Corrigé

- Correction du chargement de la clé API depuis `.env`.
- Correction du problème d'encodage ASCII dans le header `X-Title`.

## [0.3.0] - 07/09/2026

### Ajouté

- Mémoire conversationnelle court terme.
- `ShortTermMemory`.
- `MemoryManager`.
- `ContextBuilder`.
- Consultation de la mémoire via `GET /api/chat/memory`.
- Effacement de la mémoire via `DELETE /api/chat/memory`.
- Limitation de l'historique à 20 messages.
- Validation de la longueur des messages.

### Amélioré

- Architecture de `ZephyrAgent`.
- Gestion du contexte envoyé au modèle.

## [0.4.1] - 07/09/2026

### Ajouté

- Extraction automatique du profil apprenant.
- Nouveau `ProfileExtractor`.
- Extraction du nom.
- Extraction de la langue cible.
- Extraction du niveau.
- Extraction des objectifs.
- Mise à jour automatique du profil depuis les conversations.

### Amélioré

- Personnalisation des conversations.
- Intégration du profil apprenant dans le contexte envoyé au modèle.

## [0.5.0] - 08/09/2026

### Added

- Banque de 36 questions CECRL A1 à C2.
- Évaluation du vocabulaire, de la grammaire, de la compréhension et de l'expression.
- Correction locale des questions fermées.
- Évaluation des questions ouvertes avec OpenRouter.
- Calcul des scores par compétence.
- Calcul des scores par niveau CECRL.
- Évaluation adaptative A1 → C2.
- Progression automatique selon les performances.
- Arrêt anticipé lorsque le niveau est insuffisant.
- Approfondissement des niveaux intermédiaires.
- API FastAPI dédiée à l'évaluation.
- Intégration des résultats dans le profil apprenant.
- Historique des évaluations.
- Identifiant unique des sessions d'évaluation.
- Tests automatisés.

## [0.6.5] - 2026-09-09

### Added

* Ajout du `VocabularyManager`.
* Ajout du modèle `VocabularyItem`.
* Gestion des mots appris.
* Gestion des traductions.
* Gestion des catégories lexicales.
* Gestion des exemples.
* Gestion de la difficulté des mots.
* Détection des doublons.
* Suivi des réponses correctes et incorrectes.
* Calcul du taux de maîtrise.
* Identification des mots à réviser.
* Identification des mots maîtrisés.
* Statistiques du vocabulaire.
* Intégration du vocabulaire au `LearningEngine`.
* Intégration du vocabulaire au `LearnerProfileManager`.
* Ajout de `learned_vocabulary` au profil apprenant.
* Ajout des endpoints REST du vocabulaire.

### Tests

* Ajout des tests du `VocabularyManager`.
* Validation de l'intégration du vocabulaire avec le `LearningEngine`.
* Validation de l'intégration avec le profil apprenant.
* Suite complète : **42 tests passés**.

### Fixed

* Correction de l'initialisation du `VocabularyManager` dans `LearningEngine`.
* Ajout de `add_learned_vocabulary()` dans `LearnerProfileManager`.

### Status

**V0.6.5 — TERMINÉE**

## [0.6.6] - 2026-09-09

### Added

- GrammarManager
- GrammarRule
- Gestion des règles grammaticales
- Explications grammaticales
- Catégories
- Exemples
- Difficulté
- Suivi des réponses
- Calcul de la maîtrise grammaticale
- Règles à réviser
- Règles maîtrisées
- Statistiques grammaticales
- Intégration au LearningEngine
- Intégration au LearnerProfileManager
- `grammar_mastery`
- `grammar_history`

### Tests

- Tests GrammarManager
- Tests d'intégration LearningEngine
- Tests d'intégration avec le profil apprenant
- Suite complète : 59 tests réussis

### Fixed

- Correction de `get_learning_context()` lorsque aucun apprenant n'est associé au LearningEngine.

### Status

V0.6.6 TERMINÉE