# 📋 Changelog — Zéphyr

## Séance du jour et exercices à l’oral — 13/11/2026

- Accueil compact et onglet Aujourd’hui : révisions dues, reprise d’activité et progression réelle, sans mutation ni génération à l’affichage.
- Réponse orale modifiable dans les exercices du plan : report explicite, QCM exact et correction séparée.
- Répétition/lecture plus lente, arrêt et libération du vocal ; animations existantes et thèmes conservés.
- 293 Python et 34 Node réussis ; parcours navigateur avec voix/contenus simulés et mobile contrôlés. Voix réelle à valider. Guide DAILY_SESSION.

## Parcours, révisions et présence vocale — 13/11/2026

- Exécution des activités du plan dans Mon parcours : préparation, lecture, trois exercices, correction et enchaînement après validation ; reprise persistante sans double crédit.
- Révisions espacées des mots/règles, bibliothèque et échéances ; calendrier compatible avec les anciennes sauvegardes.
- Caméra locale activée volontairement et avatar animé par les états vocaux, sans transmission d’images.
- 287 tests Python et 27 Node réussis ; séance complète testée avec contenus simulés, micro/caméra réels restant à valider. Guides JOURNEY et COMPANION.

## Réglages vocaux et transcription — 12/11/2026

- Langues de dictée/lecture indépendantes, voix disponibles, débit, tonalité, volume et pause configurables ; préférences locales.
- Résultats provisoires distincts, arrêt attend la finalisation, brouillon conservé et relecture avant envoi optionnelle.
- Capture libérée après usage, gardes sur événements/permissions tardifs ; synthèse découpée et arrêt si bloquée.
- Exemple avec arrêt et diagnostic de niveau sans transcription ni envoi audio à Zephyr.
- 23 tests Node et 3 Python interface réussis (2 avertissements connus), exemple/persistance/mobile contrôlés ; parole réelle restante. Guide `docs/VOICE.md`.

Toutes les modifications importantes du projet sont enregistrées ici.

### Ajustement de l’interface — conversation immersive

- Dès le premier message, l’écoute ou la lecture vocale, retrait des textes autour de la sphère.
- Même affichage épuré à la restauration d’un historique ; annonces d’état conservées pour les lecteurs d’écran.
- Messages d’aide et erreurs déplacés dans le panneau de conversation.
- Sphère agrandie, rotation accélérée, ondulations et réaction vocale renforcées.
- Répulsion des points au pointeur, pulsation au clic/toucher ou avec Entrée/Espace.
- Mouvement réduit respecté ; contrôle mobile à 319 px et ordinateur à 1440 px, sans débordement.
- JavaScript et diff vérifiés ; trois tests d’intégration interface réussis, deux avertissements existants.

## [0.8.0-alpha.1] — 12/11/2026 — comptes et vocal continu

- Ajustement utilisateur : inscription avec 8 à 128 caractères, test de limite 7/8 et connexion à huit.
- Écrans de compte recomposés : panneau Zéphyr, onglets, champs structurés et affichage/masquage du mot de passe.
- Validation actuelle : 274 tests Python et 7 Node ; contrôle mobile/ordinateur.


- Inscription, connexion et déconnexion avec mots de passe scrypt, sessions opaques et cookies HttpOnly.
- Contrôle de propriété des profils, transaction d’inscription, limitation des tentatives et garde de mutation/origine.
- Écran de compte ; anciens profils conservés, rattachement réservé à une commande locale.
- Bouton vocal continu : écoute/réponse/reprise avec arrêts explicites et aucun redémarrage automatique au chargement.
- 273 tests Python et 7 Node réussis ; formulaires contrôlés sur mobile et ordinateur.
- Confirmation/récupération e-mail et validation du micro réel restent à réaliser.

## [Non publié] — 12/11/2026 — aperçu interface V0.8

### Profil et évaluation accessibles dans l’interface

- Dialogue « Mon profil et mon niveau » : prénom, langue, niveau déclaré, objectifs.
- Parcours adaptatif d’anglais : reprise, QCM/texte libre, feedback, bilan et recommencement explicite.
- Vérification de la langue et relecture serveur avant renvoi d’une réponse réseau incertaine.
- 263 tests Python et 4 tests Node réussis ; CI enrichie avec les vérifications frontend.


### Nuage libre, objets 3D et traductions

- Promenade libre, formation d’objets au repos, rassemblement pendant la synthèse.
- Six objets en volume tournant lentement ; silhouettes plates de l’ébauche remplacées.
- Noms français et traductions en six langues, choix relié au profil et prononciation cible.
- Boutons « Autre objet » et « Écouter », légendes affichées après stabilisation.
- Brillance rétablie : luminosité, opacité, cœurs clairs et composition additive nocturne.
- Quatre tests Node et trois tests Python interface réussis ; validation navigateur jour/nuit/mobile.


### Halo, profondeur et personnalité de la sphère

- Halo diffus, plus intense pendant l’activité vocale, adapté au mode jour.
- Points de taille et luminosité variables selon leur profondeur, avec accents lumineux discrets.
- Respiration au repos, ondes à l’écoute, spirale en réflexion, expansion pendant la réponse.
- Interpolation des états pour des transitions visuelles progressives.
- Validation navigateur jour/nuit et réflexion/synthèse réelles ; syntaxe JS et diff valides.


### Particules libres et thèmes

- Particules qui se détachent puis rejoignent la sphère, avec cycles décalés.
- Variations discrètes de couleur et palettes jour/nuit adaptées à tout l’écran.
- Bouton soleil/lune, choix mémorisé, suivi du système en l’absence de préférence.
- Mouvement réduit respecté ; bascules et mémorisation vérifiées en navigateur.
- Contrôles à 319 et 1440 px, trois tests interface réussis, deux avertissements connus.


- Interface locale `/ui/` : sphère de points cyan, conversation, mémoire restaurée et suggestions.
- Microphone à activation explicite, analyse du volume et dictée selon compatibilité navigateur.
- Synthèse vocale, essai vocal et arrêt de lecture ; animation pendant la parole.
- Adaptation mobile et ordinateur, repli texte, états de chargement et erreurs.
- Trois tests d’intégration ajoutés ; 261 tests réussis, deux avertissements existants.
- Chat OpenRouter réel et déclenchement de synthèse vérifiés ; micro/dictée réels à valider.
- Backend inchangé en version 0.7.2 ; jalon V0.8 pédagogique encore incomplet.

## [0.7.2] — 21/10/2026

- Schémas stricts pour corrections, évaluations, profils extraits, leçons et exercices ; champs et clés dupliqués contrôlés.
- Contrôle des QCM et de la conformité des contenus générés à la demande.
- Erreurs fournisseur/format renvoyées en 502 sans note zéro artificielle ni mutation sauvegardée.
- Champs facultatifs `target_category` / `target` pour relier un exercice à un mot ou une règle de l’apprenant.
- Mise à jour de la maîtrise et de l’historique grammatical après correction ; liens persistés et anciens exercices compatibles.
- UUID d’exercices attribués côté serveur ; erreurs OpenRouter sans corps brut du fournisseur.
- 258 tests réussis localement, 2 avertissements de dépendances ; documentation de suivi synchronisée.

## [0.7.1] — 21/10/2026

- Création d’apprenants via `POST /api/learners` ; sélection explicite par `X-Learner-ID` sur les routes pédagogiques.
- Suppression de l’agent et de l’évaluation globaux ; dépendances FastAPI liées à la requête.
- États SQLite séparés par identifiant, restauration à la demande et verrou par apprenant.
- Migration atomique de la V0.7.0 vers le profil historique `00000000-0000-0000-0000-000000000001`.
- Identifiants invalides/inconnus refusés sans création implicite ; copie SQLite couvrant tous les apprenants.
- 159 tests réussis localement : séparation, redémarrage, migration, rollback et concurrence.
- Un seul processus API reste pris en charge ; authentification à réaliser.

## [0.7.0] — 21/10/2026

- Persistance SQLite automatique du profil, conversation, contenus pédagogiques, vocabulaire, grammaire, plan actif et évaluation en cours.
- Restauration au démarrage avec validation du format ; annulation des mutations en cas de requête ou d’écriture en échec.
- Configuration `DATABASE_PATH` / `PERSISTENCE_ENABLED` ; données exclues de Git.
- Commande de copie cohérente `python -m app.backup` sans écrasement.
- Reprise du plan via `GET /api/learning/plan/current` et correction de son initialisation.
- Intégration du commit distant `726a307` (forces du profil et suivi des activités).
- 143 tests réussis localement, dont redémarrage, effacement, rollback et restauration d’une copie SQLite.

## [0.6.9] — 21/10/2026

- Correction d’un exercice par identifiant via API, avec mise à jour des difficultés du profil.
- API grammaticale : ajout, liste, statistiques, notions à réviser et autoévaluation.
- Autoévaluation du vocabulaire via API ; erreur 404 pour une cible inconnue.
- Masquage du corrigé dans les exercices générés et tri du plan sur `activity_priority`.
- Dépendances de test, configuration pytest et GitHub Actions.
- Tests d’intégration du parcours pédagogique et des erreurs ; 129 tests réussis localement.
- Documentation de l’état réel et des limites du prototype.

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

## [0.6.7] — Recommendation Engine

### Added

* Ajout du `RecommendationEngine`.
* Ajout du modèle `Recommendation`.
* Génération de recommandations à partir du profil apprenant.
* Analyse des points faibles.
* Analyse des erreurs fréquentes.
* Analyse des compétences.
* Analyse du vocabulaire.
* Analyse de la grammaire.
* Prise en compte des objectifs de l'apprenant.
* Prise en compte de la difficulté des notions.
* Système de calcul de priorité de 0 à 100.
* Fusion automatique des recommandations similaires.
* Tri des recommandations par priorité.
* Limitation du nombre de recommandations.
* Intégration du Recommendation Engine au `LearningEngine`.
* Ajout de l'endpoint REST :
  `GET /api/learning/recommendations`.
* Ajout du paramètre `limit`.
* Validation de `limit` entre 1 et 50.
* Ajout de cinq tests API pour les recommandations.

### Tests

* 21 tests du Recommendation Engine validés.
* Tests d'intégration du Learning Engine validés.
* 5 tests API validés.
* Suite complète : **87 tests réussis**.
* **0 échec**.

### Notes

Deux warnings provenant des dépendances de test (`Starlette/httpx` et `AnyIO`) sont actuellement présents mais n'affectent pas le fonctionnement du projet.

### Next

* V0.6.8 — Learning Plan Engine.

## [0.6.8] - Learning Plan Engine

### Added

- `LearningPlanItem`
- `LearningPlan`
- `LearningPlanEngine`
- génération de plans personnalisés ;
- transformation des recommandations en activités ;
- activités grammaticales ;
- activités lexicales ;
- activités de compétences ;
- activités de révision des points faibles ;
- activités de correction des erreurs ;
- classement des activités par priorité ;
- endpoint `GET /api/learning/plan` ;
- validation du paramètre `limit`.

### Tests

- tests unitaires du Learning Plan Engine ;
- tests API du plan d'apprentissage.

### Limitations

Le plan ne gère pas encore :

- le temps disponible ;
- la durée des activités ;
- le calendrier ;
- la complétion ;
- l'adaptation dynamique ;
- l'historique des plans.

### Next

V0.6.9 — Adaptive Learning Plan.

## [0.6.8] — Septembre 2026

### Added

- Ajout du `LearningPlanEngine`.
- Ajout de `LearningPlan`.
- Ajout de `LearningPlanItem`.
- Génération de plans personnalisés à partir des recommandations.
- Génération d'activités adaptées au niveau de maîtrise.
- Activités de grammaire, vocabulaire et compétences.
- Activités de révision des points faibles.
- Activités de correction des erreurs fréquentes.
- Classement des activités par priorité.
- Ajout de durées estimées par activité.
- Ajout du paramètre `available_minutes`.
- Ajout de l'endpoint `GET /api/learning/plan`.
- Validation du paramètre `limit`.
- Tests unitaires, d'intégration et API.

### Changed

- Intégration du `LearningPlanEngine` dans `LearningEngine`.
- Transformation des recommandations en activités concrètes.
- Adaptation du plan au temps disponible de l'apprenant.

### Limitations

Le plan ne gère pas encore :

- la complétion des activités ;
- l'adaptation selon les performances ;
- l'historique des plans ;
- la répétition espacée ;
- le calendrier d'apprentissage.

### Status

**V0.6.8 — TERMINÉE**

### Next

**V0.6.9 — Adaptive Learning Plan**

- Complétion des activités.
- Enregistrement des scores.
- Adaptation dynamique du plan.
- Historique des plans.
- Préparation de la répétition espacée.