# Points ouverts — Zéphyr

Mise à jour : 21 octobre 2026 — backend V0.7.2.

Les points ouverts ci-dessous comprennent des défauts, limites techniques et
travaux restants. « Résolu » concerne le périmètre indiqué, sans préjuger d’une
validation en production.

| ID | Point | État / prochaine action |
|---|---|---|
| B001 | Agent et évaluation partagés entre clients | Résolu en V0.7.1 : instances et sauvegardes distinctes par identifiant |
| B002 | Données perdues au redémarrage | Résolu en V0.7.0 : SQLite et copie de sauvegarde |
| B003 | Exercice sans lien explicite vers un mot ou une règle | Résolu en V0.7.2 : lien serveur facultatif et maîtrise actualisée après correction |
| B004 | Résultats LLM peu strictement validés | Résolu en V0.7.2 : schémas stricts et erreur 502 sans progrès enregistré |
| B005 | Deux avertissements Starlette/httpx/AnyIO dans les tests | Ouvert : migration des dépendances de test à traiter séparément |
| B006 | Identifiant de sélection sans authentification | Ouvert : comptes et droits d’accès avant ouverture publique |
| B007 | Verrous locaux au processus | Ouvert : coordination nécessaire avant plusieurs workers |

## Corrigés en V0.6.9

- Réponse attendue exposée par l’API de génération d’exercices : sérialisation publique sans corrigé.
- Priorité d’activité calculée mais ignorée par le tri du plan : tri corrigé.
- Routes absentes pour la correction d’exercices, la grammaire et l’autoévaluation du vocabulaire : ajoutées.
- Dépendances pytest absentes du dépôt : `backend/requirements-dev.txt` ajouté.

## Corrigés en V0.7.0

- Plan actif non initialisé par le moteur : initialisation, mémorisation et reprise après redémarrage.
- Sauvegarde transactionnelle et annulation des modifications en cas d’échec d’écriture.

## Corrigés en V0.7.1

- Les requêtes pédagogiques exigent un identifiant explicite et refusent les identifiants inconnus.
- Profil, conversation, contenus, vocabulaire, grammaire, plan et évaluation séparés par apprenant.
- Sauvegarde, annulation et verrou limités à l’apprenant sélectionné.
- Migration atomique de l’ancienne base sans duplication du profil dans les nouveaux apprenants.

## Validation de référence — V0.7.2

Dernière suite exécutée pour le code : `python -m pytest -q` → **258 réussis,
2 avertissements de dépendances**. Les tests de séparation/migration/concurrence
sont dans `backend/tests/test_learners.py` ; ceux de restauration et rollback dans
`backend/tests/test_persistence.py`. Les appels OpenRouter sont simulés.

B003 et B004 sont résolus pour les liens explicites et la validation du format.
La qualité pédagogique réelle reste non vérifiée. B006 doit être traité avant
une ouverture publique ; B007 avant le passage à plusieurs processus API.
Les décisions associées sont consignées dans ADR-005 et ADR-007 à ADR-012
([DECISIONS.md](DECISIONS.md)).

## Corrigés en V0.7.2

- Chaînes `"false"`, scores hors bornes et listes invalides auparavant convertis silencieusement : rejetés.
- Erreur d’évaluation ouverte auparavant transformée en score zéro : `502` et annulation de la mutation.
- Générations incomplètes, QCM invalides et profils mal formés : refusés avant enregistrement.
- Identifiants d’exercices fournis par le modèle : remplacés par des UUID serveur pour éviter les collisions.
- Exercices liés à une notion existante : mise à jour des compteurs et de la maîtrise après correction.
- Réponse fournisseur brute dans les erreurs : remplacée par un message contrôlé.

Validation dédiée : `backend/tests/test_llm_validation.py` et
`backend/tests/test_exercise_targets.py`. Les anciennes sauvegardes d’exercices
sans lien restent compatibles.
