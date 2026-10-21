# Points ouverts — Zéphyr

Mise à jour : 21 octobre 2026.

| ID | Point | État / prochaine action |
|---|---|---|
| B001 | Agent et évaluation partagés entre clients | Ouvert : isoler les apprenants avant tout usage à plusieurs |
| B002 | Données perdues au redémarrage | Résolu en V0.7.0 : SQLite et copie de sauvegarde |
| B003 | Exercice sans lien explicite vers un mot ou une règle | Ouvert : ajouter ce lien pour actualiser automatiquement leur maîtrise après correction |
| B004 | Résultats LLM peu strictement validés | Ouvert : renforcer les schémas de réponse et les chemins d’erreur |
| B005 | Deux avertissements Starlette/httpx/AnyIO dans les tests | Ouvert : migration des dépendances de test à traiter séparément |

## Corrigés en V0.6.9

- Réponse attendue exposée par l’API de génération d’exercices : sérialisation publique sans corrigé.
- Priorité d’activité calculée mais ignorée par le tri du plan : tri corrigé.
- Routes absentes pour la correction d’exercices, la grammaire et l’autoévaluation du vocabulaire : ajoutées.
- Dépendances pytest absentes du dépôt : `backend/requirements-dev.txt` ajouté.

## Corrigés en V0.7.0

- Plan actif non initialisé par le moteur : initialisation, mémorisation et reprise après redémarrage.
- Sauvegarde transactionnelle et annulation des modifications en cas d’échec d’écriture.
