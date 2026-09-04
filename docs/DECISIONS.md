# 🧠 Décisions techniques — Zéphyr

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

L'authentification pourra être ajoutée ultérieurement.

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
