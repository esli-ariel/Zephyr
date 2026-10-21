# Points ouverts — Zéphyr

Mise à jour : 21 octobre 2026 — backend V0.7.1.

Les points ouverts ci-dessous comprennent des défauts, limites techniques et
travaux restants. « Résolu » concerne le périmètre indiqué, sans préjuger d’une
validation en production.

| ID | Point | État / prochaine action |
|---|---|---|
| B001 | Agent et évaluation partagés entre clients | Résolu en V0.7.1 : instances et sauvegardes distinctes par identifiant |
| B002 | Données perdues au redémarrage | Résolu en V0.7.0 : SQLite et copie de sauvegarde |
| B003 | Exercice sans lien explicite vers un mot ou une règle | Ouvert : ajouter ce lien pour actualiser automatiquement leur maîtrise après correction |
| B004 | Résultats LLM peu strictement validés | Ouvert : renforcer les schémas de réponse et les chemins d’erreur |
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

## Validation de référence — V0.7.1

Dernière suite exécutée pour le code : `python -m pytest -q` → **159 réussis,
2 avertissements de dépendances**. Les tests de séparation/migration/concurrence
sont dans `backend/tests/test_learners.py` ; ceux de restauration et rollback dans
`backend/tests/test_persistence.py`. Les appels OpenRouter sont simulés.

Prochaine priorité : B003 et B004 en V0.7.2. B006 doit être traité avant une
ouverture publique ; B007 avant le passage à plusieurs processus API.
Les décisions associées sont consignées dans ADR-005 et ADR-007 à ADR-010
([DECISIONS.md](DECISIONS.md)).
