# 📓 Journal de développement — Zéphyr

## 13/11/2026 — Activités exécutables, révisions espacées et présence vocale

- Demande : terminer l’exécution des activités et les révisions ; choix confirmé de caméra locale et avatar animé par la voix.
- Mon parcours enrichi avec Mon plan et Révisions. Séance personnalisée, première séance sans recommandations, leçon/exercices/correction et enchaînement après validation, reprise au premier élément inachevé.
- Résultats persistés, corrections idempotentes, score moyen calculé côté serveur ; lecture et autoévaluation sans faux score. Erreur fournisseur/disque et autre langue n’entraînent aucun progrès partiel.
- Calendrier de notions : 1/3/7/14/30/60 jours en réussite, 10 minutes après oubli. Anciennes notions dues immédiatement ; filtrage par langue et compatibilité des snapshots. Bibliothèque de mots/règles dans l’interface.
- Caméra vidéo seule sur activation explicite, aperçu local en miroir, arrêt et annulation de permission tardive ; aucune transmission ou capture. Avatar SVG suit repos/écoute/réflexion/parole, thèmes et mouvement réduit.
- Validation complète : 287 Python et 27 Node réussis, deux avertissements connus ; CI et syntaxe vérifiées. 13 nouveaux tests pédagogiques et quatre tests caméra.
- Navigateur : parcours QA simulé complet, reprise après rechargement, 66,67/100 sur trois exercices, carte repoussée au lendemain, avatar speaking et annulation caméra sans flux ; 319/1280 px sans débordement. Aucun compte personnel ou appel fournisseur réel dans la QA.
- Caméra réelle et boucle acoustique toujours à valider après autorisation ; garde-fou de synthèse observé en QA. Serveur local 8001 relancé, serveur QA distinct arrêté. Guides JOURNEY/COMPANION, progression, décisions et limites mis à jour ; push autorisé dans la continuité du projet.

## 12/11/2026 — Réglages vocaux et transcription

- Langues indépendantes, voix réellement disponibles, vitesse/volume/tonalité, pause et validation manuelle optionnelle ; réglages conservés localement.
- Transcription finale/provisoire reconstruite sans doublons ; arrêt manuel attend la finalisation, brouillon et texte en erreur conservés pour relecture.
- Moteur isolé : pistes libérées, permissions/événements tardifs neutralisés, longues lectures découpées et garde-fou de synthèse.
- Exemple/arrêt et diagnostic de niveau sans envoi d’audio à Zephyr. Paramètres du navigateur pour choisir le microphone.
- 23 tests Node et 3 Python interface réussis, syntaxe/diff valides, 2 avertissements connus. Suite complète Python précédente : 274, non relancée ici.
- Navigateur : synthèse native et persistance observées, valeurs françaises par défaut restaurées, mobile 319 px sans débordement. Diagnostic arrêté car autorisation micro en attente ; dictée et boucle acoustique restent à valider par l’utilisateur.
- Guide VOICE, suivi, CI et documentation actualisés ; livraison Git dans la continuité des demandes de push.

## 12/11/2026 — Mot de passe huit caractères et nouvelle interface de compte

- Demande explicite : accepter un mot de passe de huit caractères et soigner connexion/inscription.
- Minimum serveur/formulaire abaissé à huit, maximum inchangé (128). Mots de passe existants toujours valides.
- Nouveau panneau de marque, mise en page à deux colonnes sur ordinateur et compacte sur mobile, onglets Connexion/Inscription, champs structurés et CTA plus lisible.
- Affichage/masquage pour mot de passe et confirmation ; vidage à la fermeture indépendamment du type visible/masqué.
- Test de limite : sept refusés, huit acceptés puis connexion réussie.
- Vérification navigateur : minimum=8, affichage en texte puis retour au formulaire masqué, rendu 319/1200 px sans débordement. Aucun identifiant personnel saisi.
- Validation : 274 tests Python et 7 Node ; deux avertissements connus. Suivi et documentation actualisés, livraison Git dans la continuité des demandes de push.

## 12/11/2026 — Comptes locaux et vocal continu

- Demandes : création de compte, bouton vocal continu et push.
- Inscription/connexion/déconnexion, cookie HttpOnly SameSite Strict, sessions révocables de 7 jours, hachage scrypt et limites de tentatives persistantes.
- Authentification activée par défaut ; propriété vérifiée sur chaque profil. Inscription et profil initial atomiques. Le mode production exige les cookies HTTPS sécurisés.
- En-tête de mutation et contrôle d’origine, validation sans réécriture de mot de passe dans les erreurs, documentation OpenAPI adaptée.
- Profils anonymes conservés ; sauvegarde locale pré-authentification et commande locale de rattachement, aucun endpoint public de réclamation par UUID.
- Interface de compte ajoutée. Aucun compte personnel créé par l’agent ; l’utilisateur choisit ses identifiants.
- Vocal continu : activation explicite, écoute → réponse → reprise, sans capture pendant la réflexion/synthèse. Arrêt volontaire, erreur, profil/compte, arrière-plan ou déconnexion ; pas de reprise au rechargement.
- Validation : 273 tests Python et 7 Node réussis, 2 avertissements connus. Tests de comptes isolés, révocation/rotation/expiration, redémarrage, rattachement, erreurs de création et limitation. Contrôleur vocal testé avec ordonnanceur simulé.
- UI : formulaires connexion/inscription, largeur 319/1100 px, aucun démarrage vocal automatique. Pas de validation de boucle avec une voix réelle.
- Version backend 0.8.0-alpha.1 ; guide ACCOUNTS et suivi complétés. Livraison Git demandée, résultat du push communiqué dans le chat.


## 12/11/2026 — Prochain jalon : profil et évaluation, préparation du push

- Demande : reporter les prochains ajustements visuels, poursuivre les fonctionnalités et pousser le travail sur GitHub.
- Ajout du bouton « Mon profil et mon niveau » et d’un dialogue natif avec deux sections.
- Profil : prénom, langue, niveau déclaré et ajout d’objectifs ; synchronisation avec le vocabulaire visuel.
- Évaluation : anglais explicitement indiqué, démarrage/reprise, QCM/texte libre, correction et progression adaptative, bilan enregistré, recommencement explicite.
- Réponse réseau incertaine : relecture du serveur avant de proposer une nouvelle soumission.
- Chat/micro suspendus pendant le dialogue, contrôles rétablis à sa fermeture.
- Tests : 263 Python réussis, 4 Node réussis, 2 avertissements de dépendances existants ; syntaxe JS et diff valides.
- Deux tests d’intégration supplémentaires : profil/reprise et bilan unique/recommencement sans perte d’historique.
- Navigateur : profil, entrée du test, première question, mobile 319 px, retour aux contrôles du chat. Aucun faux score ajouté au profil de l’utilisateur.
- CI complétée avec un job Node 22, vérification de syntaxe et tests frontend.
- Dépôt distant récupéré : aucun écart avec origin/main avant préparation du commit. Livraison sur main demandée ; résultat du push rapporté dans le chat. Aucune publication web.
- Suite fonctionnelle : affichage du plan, exécution d’exercices et correction.


## 12/11/2026 — Nuage libre, objets 3D tournants et vocabulaire visuel

- Nouvelle demande : les points ne sont plus contraints à une sphère ; promenade libre, rassemblement pendant la synthèse et objets au repos.
- Six objets : maison, arbre, tasse, livre, poisson et cœur ; nom français, traduction et prononciation cible.
- Six langues hors ligne ; choix relié au profil, restauré et actualisé après le chat. Langues non prises en charge signalées.
- Cycle de repos de 20 s, transitions progressives, bouton « Autre objet » et lecture seulement quand le mot est affiché.
- Retour utilisateur : la première ébauche en silhouettes était plate et les points trop ternes. Remplacement par des surfaces 3D volumétriques, rotation lente et légendes fixes.
- Brillance rétablie : opacité/luminosité renforcées, cœurs clairs et composition additive nocturne. Contraste adapté au jour.
- Tests : quatre tests Node réussis, dont volume non planaire des six modèles ; trois tests d’intégration interface réussis, deux avertissements existants ; syntaxe JS/diff vérifiés.
- Navigateur : arbre traduit en espagnol, sauvegarde/restauration de la langue, retour au profil anglais, prononciation et rassemblement, tasse/maison en volume, nuage brillant. Mobile 319 px et jour/nuit sans débordement, aucune erreur console observée.
- Pas de nouvel appel OpenRouter pour cette évolution ; la prononciation utilise le navigateur. Pas de test micro réel, de push ou de publication.
- L’affichage des objets n’attribue aucun progrès ni maîtrise automatiquement.


## 12/11/2026 — Halo, relief et mouvements selon l’état

- Halo diffus à deux dégradés, intensité liée aux états et à la parole ; palette claire atténuée.
- Profondeur renforcée par perspective, tri des points, tailles et opacités différenciées, accents lumineux limités.
- Repos : respiration lente. Écoute : ondes selon le volume. Réflexion : torsion en spirale et rotation plus rapide. Réponse : expansion et ondes.
- Transitions de forme, halo et teintes interpolées. Détachement et interaction existants conservés.
- Validation visuelle jour/nuit ; requête réelle « Présente-toi en trois courtes phrases, en français. » : réflexion, synthèse et retour au repos observés.
- Aucun message d’erreur console observé ; document/viewport égaux à 319 px.
- `node --check frontend/app.js` et `git diff --check` validés. Pas de nouvelle exécution de pytest pour ce changement de rendu seul ; référence antérieure : 261 tests réussis.
- Micro réel non testé ; animation de synthèse toujours sans analyse PCM. Aucun push/publication.


## 12/11/2026 — Particules détachables et modes jour/nuit

- Points détachables sur cycles décalés : éloignement puis retour fluide à la sphère.
- Amplitude liée à l’activité, à la voix et aux pulsations ; interaction pointeur conservée.
- Variation lente et discrète des teintes, adaptée au fond sombre ou clair.
- Sélecteur soleil/lune dans l’en-tête ; choix mémorisé, sinon suivi de la préférence système.
- Palette claire pour le fond, le chat, les contrôles et les particules ; transitions douces.
- Mouvement réduit : détachement/rotation/dérive de teinte suspendus.
- Vérification navigateur : deux thèmes observés, persistance après rechargement, 319/1440 px sans débordement ; aucune erreur console observée.
- Trois tests interface réussis, deux avertissements connus ; `node --check` et `git diff --check` valides.
- Fichiers de suivi complétés ; aucun push/publication ni nouvel appel IA.



## 12/11/2026 — Conversation épurée et particules interactives

- Demande : retirer les textes près de la sphère au début de la conversation et intensifier/interagir avec les points.
- Activation au premier message ajouté, à l’écoute effective, au début de la synthèse et à la restauration des messages.
- Introduction, légendes, phrases décoratives et aide visuelle micro masquées dans la zone de la sphère. Le bouton micro reste disponible et nommé.
- Notifications et erreurs conservées dans la conversation ; états de lecture/écoute accessibles sans texte visuel près de la sphère.
- Champ de points plus grand, rotation et déformations fluides renforcées pendant la conversation et la parole.
- Interaction pointeur (répulsion), clic/toucher (onde), clavier Entrée/Espace (pulsation) ; respect du mouvement réduit.
- Vérification navigateur : historique restauré avec introduction masquée, pulsation clavier, glissement du pointeur et déformation visibles, aucun débordement à 319/1440 px, aucune erreur console observée.
- `node --check frontend/app.js`, `git diff --check` et trois tests d’intégration interface réussis ; deux avertissements existants.
- Pas de nouvel appel IA ni de capture micro réelle dans cette validation.

## 12/11/2026 — Première interface conversationnelle locale

- Interface sombre inspirée d’un assistant futuriste, avec sphère de 2 100 points cyan.
- Veille, écoute, réflexion et parole ; analyse RMS du micro et enveloppe visuelle de synthèse.
- Conversation connectée à `/api/chat`, identifiant apprenant stocké localement, mémoire restaurée.
- Dictée `fr-FR` si disponible ; texte en repli, erreurs explicites, arrêt du micro et de la voix.
- Bouton d’essai vocal indépendant du fournisseur IA ; affichage mobile et ordinateur.
- Montage FastAPI `/ui/`, conservation de `/`, `/health`, `/docs` et des contrats API.
- Trois tests d’intégration : interface/assets, contrat API/identifiant, absence d’exposition backend.
- Validation : 261 tests réussis, deux avertissements existants, `node --check` réussi.
- Navigateur : conversation réelle OpenRouter réussie et état de synthèse observé ; aucune erreur console.
- Contrôle à 319 px (débordement corrigé) et 1440 × 960 ; reprise après rechargement.
- Le micro réel, la dictée et le son perçu restent à valider avec l’utilisateur.
- Serveur local port 8001, car 8000 occupé ; aucune publication ni opération Git distante.
- Suivi : README, PROGRESSION, BUGS, DECISIONS, CHANGELOG et documentation frontend.
- Suite proposée : langues/voix, mode immersif, écrans pédagogiques, conversation vocale continue.


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


# V0.6.8 — Learning Plan Engine

## Objectif

Après avoir développé le Recommendation Engine en V0.6.7,
l'objectif de V0.6.8 est de transformer les recommandations
en activités pédagogiques ordonnées.

## Implémentation

Création de :

text
learning_plan.py



## V0.6.8 — Learning Plan Engine

### Date

Septembre 2026

### Objectif

Transformer les recommandations pédagogiques de Zéphyr en un plan d'apprentissage concret, ordonné et adapté au temps disponible.

### Implémentation

Création du fichier :

`backend/app/learning/learning_plan.py`

Classes principales :

- `LearningPlanItem`
- `LearningPlan`
- `LearningPlanEngine`

Le LearningPlanEngine dépend du RecommendationEngine.

Le flux est désormais :


LearnerProfile
      ↓
RecommendationEngine
      ↓
Recommendation
      ↓
LearningPlanEngine
      ↓
LearningPlan
      ↓
LearningPlanItem

## 21/10/2026 — V0.6.9 : intégration pédagogique et revue du dépôt

### Travaux réalisés

- Revue du code, des versions documentées et des points d’intégration manquants.
- Ajout des routes de correction d’exercice, de grammaire et d’autoévaluation du vocabulaire.
- Mise à jour des difficultés du profil après correction d’exercice.
- Masquage de la réponse attendue dans l’énoncé public et tri du plan sur `activity_priority`.
- Ajout des dépendances de développement, de la configuration pytest et de GitHub Actions.

### Validation

129 tests réussis localement, 2 avertissements de dépendances. Appels OpenRouter
simulés. Le backend restait mono-apprenant et ses données étaient temporaires.

## 21/10/2026 — V0.7.0 : sauvegarde durable

### Travaux réalisés

- Ajout de la sauvegarde SQLite et de la restauration du profil, conversation,
  contenus pédagogiques, vocabulaire, grammaire, plan actif et évaluation.
- Annulation des mutations lors d’un échec de requête ou d’écriture ; erreur `503`
  lorsqu’une sauvegarde ne peut pas être confirmée.
- Ajout de la commande de copie `python -m app.backup` et exclusion des données de Git.
- Correction de l’initialisation du plan actif et ajout de sa consultation.
- Intégration du commit distant `726a307`, qui enrichissait le profil et le suivi des activités.

### Validation et publication

143 tests réussis localement, 2 avertissements de dépendances : redémarrage,
effacements, rollback, état invalide et copie/restauration SQLite.
Publication sur `main` : [5f9478a](https://github.com/esli-ariel/Zephyr/commit/5f9478a).

## 21/10/2026 — V0.7.1 : séparation des apprenants

### Travaux réalisés

- Création des apprenants via `POST /api/learners` ; sélection explicite par `X-Learner-ID`.
- Remplacement de l’agent et de l’évaluation globaux par des instances propres à chaque apprenant.
- Injection de ces instances dans toutes les routes pédagogiques.
- Sauvegardes par identifiant, restauration à la demande et verrou par apprenant.
- Migration transactionnelle de l’ancienne base vers le profil historique
  `00000000-0000-0000-0000-000000000001`.
- Documentation de la nouvelle sélection, de la migration et des limites d’accès.

### Validation et publication

159 tests réussis localement, 2 avertissements de dépendances. Vérifications :
séparation de deux profils et de leurs ressources, redémarrage, effacements,
échecs de sauvegarde/création, identifiants refusés, migration, copie multi-apprenant
et concurrence. Un appel IA lent d’un apprenant ne bloque pas les autres.
Publication sur `main` : [f01c4d4](https://github.com/esli-ariel/Zephyr/commit/f01c4d4).
Aucun appel OpenRouter réel ni résultat CI distant n’a été vérifié pendant ces validations.

### Limites et suite

L’identifiant sélectionne les données sans authentifier leur propriétaire ; un seul
processus API est pris en charge. La V0.7.2 doit renforcer la validation des réponses
IA et relier les exercices aux mots/règles pour actualiser leur maîtrise.
L’interface web et l’authentification restent à réaliser.

## 21/10/2026 — Synchronisation des documents de suivi

Mise à jour coordonnée de `BUGS.md`, `DECISIONS.md`, `JOURNAL.md` et
`PROGRESSION.md` après la V0.7.1. Ajout des ADR-007 à ADR-010 et clarification
de l’ADR-005. Les résultats ci-dessus correspondent aux validations du code
réalisées pour chaque version ; cette synchronisation modifie uniquement la documentation.


## 21/10/2026 — V0.7.2 : validation IA et maîtrise des notions

### Préparation locale

Création de `backend/.env` et `backend/app/.env` depuis leurs exemples, hors Git.
Dépendances de développement vérifiées dans `.venv`, sans conflit. La clé ajoutée
par l’utilisateur est chargée depuis `backend/.env` ; aucune clé n’est consignée ici.

### Travaux réalisés

- Schémas stricts communs aux cinq types de réponses structurées du modèle.
- Rejet des types/bornes invalides, clés dupliquées, champs manquants ou supplémentaires.
- Contrôles des QCM et de la conformité des générations à la demande.
- Erreurs OpenRouter normalisées sans recopier les réponses brutes.
- Suppression de la note zéro artificielle en cas d’échec d’évaluation ouverte.
- Lien explicite et facultatif des exercices vers une règle ou un mot appartenant à l’apprenant.
- Identifiants d’exercices générés par le serveur, maîtrise actualisée après correction,
  et historique grammatical synchronisé avec le profil.
- Mise à jour coordonnée de BUGS, DECISIONS, JOURNAL et PROGRESSION.

### Validation

**258 tests réussis localement, 2 avertissements de dépendances.** Scénarios :
formats invalides, erreurs HTTP et transport, absence de mutation sur erreur,
correction réessayable, maîtrise correcte/incorrecte, séparation entre apprenants,
restauration du lien et compatibilité des anciens exercices sans lien.
Aucun appel OpenRouter réel n’a été effectué ; les réponses du fournisseur sont simulées.
Le résultat CI distant n’a pas été vérifié.

### Limites et suite

L’association est explicite : aucun lien n’est inventé pour les anciens exercices.
Chaque nouvelle soumission compte comme une tentative. Les contrôles de format
ne valident pas la qualité pédagogique d’un modèle réel. Prochain jalon : première
interface web V0.8.0 ; authentification et droits requis avant ouverture publique.
