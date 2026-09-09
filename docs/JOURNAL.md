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

## 2026-09-09 — V0.6.5 : Vocabulary Manager

### Travail réalisé

Finalisation du système de gestion du vocabulaire de Zéphyr.

Le `VocabularyManager` permet maintenant de créer et gérer les éléments du vocabulaire de l'apprenant tout en conservant des informations pédagogiques permettant de suivre la progression.

### Fonctionnalités

Chaque élément du vocabulaire contient notamment :

* le mot ;
* sa traduction ;
* la langue ;
* le niveau ;
* la catégorie ;
* des exemples ;
* la difficulté ;
* le nombre de révisions ;
* le nombre de réponses correctes ;
* le nombre de réponses incorrectes ;
* le taux de maîtrise.

La maîtrise est calculée automatiquement à partir des réponses de l'apprenant.

### Intégration

Le `VocabularyManager` a été intégré au `LearningEngine`.

Lorsqu'un nouveau mot est ajouté :

```text
LearningEngine
      ↓
VocabularyManager
      ↓
VocabularyItem
```

Le mot est également ajouté au profil de l'apprenant :

```text
VocabularyManager
      ↓
LearnerProfileManager
      ↓
learned_vocabulary
```

Cette intégration permet à Zéphyr de conserver une vision globale des connaissances lexicales de l'apprenant.

### API

Les endpoints suivants ont été ajoutés :

```text
POST /api/learning/vocabulary
GET  /api/learning/vocabulary
GET  /api/learning/vocabulary/statistics
GET  /api/learning/vocabulary/review
```

### Tests

Une erreur d'intégration a été rencontrée lors de la première exécution :

```text
AttributeError:
'LearningEngine' object has no attribute 'vocabulary'
```

Le problème a été corrigé en initialisant :

```python
self.vocabulary = VocabularyManager()
```

Une seconde erreur concernait l'intégration avec le profil :

```text
AttributeError:
'LearnerProfileManager' object has no attribute
'add_learned_vocabulary'
```

La méthode `add_learned_vocabulary()` a été ajoutée au `LearnerProfileManager`.

Après correction :

```text
42 passed
```

### Conclusion

La V0.6.5 est considérée comme terminée et validée.

Le système dispose maintenant d'une première mémoire pédagogique consacrée au vocabulaire.

### Prochaine étape

La prochaine étape est **V0.6.6 — Grammar Manager**.

L'objectif sera de permettre à Zéphyr de suivre les compétences grammaticales de l'apprenant, d'identifier les erreurs récurrentes et d'estimer progressivement la maîtrise de différentes règles grammaticales.

## 2026-09-09 — V0.6.6 Grammar Manager

La V0.6.6 introduit le système de gestion et de suivi des connaissances grammaticales.

### Réalisations

Création de `GrammarRule` permettant de représenter :

- une règle grammaticale ;
- son explication ;
- la langue ;
- le niveau ;
- la catégorie ;
- les exemples ;
- la difficulté ;
- le nombre de révisions ;
- les réponses correctes et incorrectes ;
- le niveau de maîtrise.

Création de `GrammarManager` permettant :

- l'ajout de règles ;
- la détection des doublons ;
- la recherche ;
- la suppression ;
- le suivi des réponses ;
- le calcul de la maîtrise ;
- l'identification des règles à réviser ;
- l'identification des règles maîtrisées ;
- le calcul des statistiques.

### Intégration

Le `GrammarManager` a été intégré au `LearningEngine`.

Le profil apprenant possède désormais :

- `grammar_mastery`
- `grammar_history`

Les résultats des exercices grammaticaux peuvent donc enrichir progressivement le profil de l'apprenant.

### Tests

La suite complète comporte désormais 59 tests.

Résultat final :

59 passed

Une erreur d'intégration concernant `get_learning_context()` a été détectée puis corrigée lorsque le `LearningEngine` fonctionnait sans `LearnerProfileManager`.

### Prochaine étape

La prochaine fonctionnalité est la V0.6.7 :

**Recommendation Engine**

Objectif : permettre à Zéphyr de déterminer automatiquement ce que l'apprenant devrait étudier ensuite en fonction de son profil et de ses performances.

# Journal — V0.6.7

## Recommendation Engine

### Objectif

Cette étape avait pour objectif de rendre Zéphyr capable de transformer les données du profil apprenant en recommandations pédagogiques concrètes.

L'idée est de passer progressivement d'un système qui se contente de conserver les résultats de l'apprenant à un système capable de décider :

> « Que devrait travailler l'apprenant maintenant ? »

### Travail réalisé

Un nouveau composant `RecommendationEngine` a été développé dans :

```text
backend/app/learning/recommendation.py
```

Le moteur analyse :

* les compétences faibles ;
* les points faibles ;
* les erreurs fréquentes ;
* le vocabulaire ;
* la grammaire ;
* les objectifs de l'apprenant ;
* la difficulté des notions.

Chaque élément peut produire une recommandation.

### Priorisation

Un système de scoring a été mis en place afin d'éviter de simplement retourner une liste de notions.

La priorité augmente notamment lorsque :

* la maîtrise est faible ;
* la notion est identifiée comme point faible ;
* des erreurs fréquentes sont associées ;
* la notion correspond à un objectif ;
* la difficulté est élevée ;
* une activité récente est détectée.

Cela permet à Zéphyr de distinguer une notion simplement intéressante d'une notion réellement urgente à travailler.

### Intégration

Le moteur a ensuite été intégré au :

```text
LearningEngine
```

Une nouvelle méthode permet d'obtenir les recommandations :

```python
get_recommendations(limit=5)
```

### API

L'API REST a été complétée avec :

```text
GET /api/learning/recommendations
```

Exemple :

```text
GET /api/learning/recommendations?limit=10
```

L'API retourne le nombre de recommandations ainsi que leur contenu.

### Tests

Les tests du Recommendation Engine ont été développés et validés.

Résultats :

```text
Recommendation Engine : 21/21
API recommandations   : 5/5
Suite complète         : 87/87
```

Aucun test n'est en échec.

### Résultat

Zéphyr possède désormais une première couche de décision pédagogique.

Le système est capable d'identifier automatiquement les éléments qui méritent une attention particulière et de les classer par priorité.

### Limites actuelles

Le moteur reste volontairement déterministe dans cette version.

Certaines améliorations sont réservées aux prochaines versions :

* prise en compte réelle de la récence des activités ;
* prise en compte de l'historique temporel ;
* recommandations de leçons complètes ;
* recommandations d'exercices ;
* adaptation automatique de la difficulté ;
* génération d'un plan quotidien ;
* prise en compte du temps disponible ;
* personnalisation par objectif ;
* recommandations utilisant éventuellement le LLM.

### Prochaine étape

La prochaine évolution sera la création du :

**Learning Plan Engine**

Il devra transformer les recommandations en un véritable programme d'apprentissage personnalisé.
