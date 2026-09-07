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