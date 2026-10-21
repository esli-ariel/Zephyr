# Points ouverts — Zéphyr

Mise à jour : 21 octobre 2026.

| ID | Point | État / prochaine action |
|---|---|---|
| B001 | Agent et évaluation partagés entre clients | Résolu en V0.7.1 : instances et sauvegardes distinctes par identifiant |
| B002 | Données perdues au redémarrage | Résolu en V0.7.0 : SQLite et copie de sauvegarde |
| B003 | Exercice sans lien explicite vers un mot ou une règle | Ouvert : ajouter ce lien pour actualiser automatiquement leur maîtrise après correction |
| B004 | Résultats LLM peu strictement validés | Ouvert : renforcer les schémas de réponse et les chemins d’erreur |
| B006 | Identifiant de sélection sans authentification | Ouvert : comptes et droits d’accès avant ouverture publique |
| B007 | Verrous locaux au processus | Ouvert : coordination nécessaire avant plusieurs workers |
| B005 | Deux avertissements Starlette/httpx/AnyIO dans les tests | Ouvert : migration des dépendances de test à traiter séparément |

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
