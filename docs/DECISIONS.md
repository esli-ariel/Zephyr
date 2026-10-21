# 🧠 Décisions techniques — Zéphyr

Mise à jour : 21 octobre 2026 — backend V0.7.1.

## ADR-001 — Backend Python

**Décision :** utiliser Python avec FastAPI.

**Raison :**

* excellent écosystème IA ;
* intégration facile avec les modèles de langage ;
* nombreuses bibliothèques pour la vision et la voix ;
* FastAPI est adapté aux API modernes et asynchrones.

---

## ADR-002 — Frontend

**Décision :** utiliser Next.js avec React et TypeScript.

**Raison :**

* interface moderne ;
* excellente intégration avec les applications temps réel ;
* TypeScript apporte une meilleure sécurité du code ;
* adapté à une interface interactive avec avatar, voix et caméra.

---

## ADR-003 — Communication

**Décision :** REST pour les opérations classiques et WebSocket pour les interactions temps réel.

**Raison :**

Zéphyr devra gérer :

* conversation ;
* voix ;
* événements ;
* état de l'agent ;
* interactions avec l'interface.

Le temps réel sera donc important.

---

## ADR-004 — Fournisseur LLM

**Décision :** utiliser OpenRouter.

**Raison :**

* accès à plusieurs modèles ;
* API compatible avec les applications modernes ;
* possibilité de changer de modèle sans reconstruire toute l'application.

---

## ADR-005 — Authentification

**Décision :** ne pas implémenter l'authentification dans la première version.

**Raison :**

L'objectif actuel est de construire et tester le cœur de Zéphyr avant d'ajouter les comptes utilisateurs.

L'authentification devra être ajoutée avant une ouverture publique.
En V0.7.1, `X-Learner-ID` sélectionne un profil ; connaître cet identifiant
permet de l'utiliser. La séparation des états ne remplace pas les droits d'accès.

---

## ADR-006 — Architecture

**Décision :** conserver tout le projet dans un seul dossier racine.

```text
zephyr/
```

**Raison :**

Faciliter :

* le développement ;
* la sauvegarde ;
* Git ;
* la documentation ;
* le déploiement ;
* la compréhension du projet.

---

## ADR-007 — Persistance SQLite du prototype

**Date :** 21/10/2026 — V0.7.0, étendue en V0.7.1.

**Décision :** utiliser SQLite et un snapshot JSON versionné et validé par
Pydantic pour conserver l’état pédagogique. PostgreSQL reste une piste pour
une architecture de production ; il n’est pas implémenté actuellement.

**Raison :** rendre les données durables sans ajouter de serveur de base de données.
Le snapshot conserve ensemble le profil, la conversation, les contenus, les
maîtrises, le plan actif et la session d’évaluation.

**Conséquences :** le fichier est configuré par `DATABASE_PATH` et exclu de Git.
`python -m app.backup` produit une copie SQLite cohérente sans remplacer une copie
existante. Le push GitHub ne constitue pas une sauvegarde des données locales.

## ADR-008 — État explicite par apprenant

**Date :** 21/10/2026 — V0.7.1.

**Décision :** créer un UUID via `POST /api/learners` et exiger `X-Learner-ID`
sur les routes pédagogiques. Chaque identifiant possède un `ZephyrAgent`, une
`AdaptiveAssessment` et un état SQLite distincts, injectés dans les routes par
les dépendances FastAPI. Les profils sont restaurés à la demande.

**Raison :** éviter le partage implicite de mémoire et de progression entre clients.

**Conséquences :** absence, format invalide ou doublon d’en-tête → `400` ;
identifiant inconnu → `404`, sans création implicite. Aucun profil par défaut
n’est sélectionné. L’authentification reste régie par ADR-005.

## ADR-009 — Transactions, migration et concurrence

**Date :** 21/10/2026 — V0.7.0 et V0.7.1.

**Décision :** confirmer une mutation après sauvegarde et restaurer l’état précédent
lorsqu’une requête ou son écriture échoue. Utiliser un verrou par apprenant,
dans un seul processus API (`--workers 1`).

**Raison :** préserver la cohérence d’un profil sans bloquer les autres apprenants
pendant ses appels IA. Un échec d’écriture renvoie `503`.

**Migration :** l’ancien état unique est validé puis transféré, dans une transaction,
vers `00000000-0000-0000-0000-000000000001`. Les nouveaux profils restent vides.
Un état ancien invalide annule la migration. Une base migrée nécessite la V0.7.1
ou une version ultérieure ; conserver une copie avant migration.

**Limite :** les verrous et caches sont locaux au processus. Plusieurs workers
nécessiteront une coordination supplémentaire pour éviter des écrasements.

## ADR-010 — Validation automatisée sans appels IA réels

**Date :** 21/10/2026 — depuis V0.6.9.

**Décision :** déclarer les dépendances de test dans `backend/requirements-dev.txt`,
exécuter `python -m pytest -q` et bloquer les appels OpenRouter réels dans les tests.
Les scénarios nécessitant l’IA utilisent des réponses simulées.

**Raison :** obtenir une suite reproductible sans clé API ni consommation du fournisseur.

**Validation V0.7.1 :** 159 tests réussis localement, 2 avertissements de dépendances.
La configuration GitHub Actions est présente ; son résultat distant n’a pas été
vérifié dans cette session. Ces tests ne valident pas la qualité pédagogique d’un
modèle réel ni la disponibilité d’OpenRouter.
