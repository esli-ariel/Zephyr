# 🌪️ Zéphyr

Assistant d’apprentissage des langues. La version **0.7.1** fournit un
prototype backend Python/FastAPI : conversation avec OpenRouter, profil apprenant,
évaluation adaptative CECRL, leçons, exercices, correction, vocabulaire,
grammaire, recommandations et plans personnalisés.

## Démarrage local

Python 3.12, depuis la racine du dépôt :

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements-dev.txt
cp backend/.env.example backend/.env
cd backend
python -m uvicorn app.main:app --reload
```

Renseigner `OPENROUTER_API_KEY` et `OPENROUTER_MODEL` dans `backend/.env`
pour les conversations, la génération et les corrections ouvertes.
Si une variable `DEBUG` existe déjà dans le terminal, elle doit contenir un
booléen (`true` ou `false`) : les variables du terminal priment sur `.env`.

API : `http://127.0.0.1:8000` ; documentation interactive :
`http://127.0.0.1:8000/docs`.

## Tests

Depuis la racine, environnement virtuel activé :

```bash
python -m pytest -q
```

Les tests isolent la configuration et bloquent les appels réels à OpenRouter.
Une configuration GitHub Actions exécute la même suite sous Python 3.12.

## Sélection de l’apprenant

Créer un apprenant avec `POST /api/learners` (sans en-tête) :

```bash
curl -X POST http://127.0.0.1:8000/api/learners
```

L’API renvoie `201` et `{"learner_id": "<UUID>"}`. Conserver cet identifiant
côté client et transmettre `X-Learner-ID: <UUID>` à chaque requête `/api/*`
suivante. La documentation `/docs` propose ce champ sur chaque opération.
Les routes `/`, `/health`, `/docs` et `/openapi.json` restent accessibles sans identifiant.

```bash
curl http://127.0.0.1:8000/api/learner/profile \
  -H 'X-Learner-ID: <UUID>'
```

Un identifiant absent, mal formé ou fourni plusieurs fois renvoie `400` ;
un identifiant inconnu renvoie `404` sans créer de profil. Chaque apprenant a
son propre agent, mémoire, évaluation, contenus, vocabulaire, grammaire et plan.
Les opérations d’un même apprenant sont sérialisées ; les appels IA des autres
apprenants peuvent avancer en parallèle.

L’identifiant sélectionne les données ; il ne constitue pas une authentification.
Une personne connaissant cet identifiant peut utiliser le profil correspondant.
L’authentification et les droits d’accès restent à ajouter avant une ouverture publique.

## Parcours pédagogique

Avec `X-Learner-ID` dans chaque requête :

1. Définir langue et niveau avec `PUT /api/learner/profile`, ou effectuer
   l’évaluation via `/api/assessment/*`.
2. Générer des exercices avec `POST /api/learning/exercises`.
3. Soumettre `{"answer": "..."}` à
   `POST /api/learning/exercises/{exercise_id}/answer`.
   La correction actualise les points faibles et erreurs du profil.
4. Consulter `/api/learning/recommendations` puis `/api/learning/plan`.

Les réponses attendues restent côté serveur pendant la génération.
Les corrections d’exercices fermés sont locales ; les exercices ouverts
utilisent OpenRouter.

Le vocabulaire (`/api/learning/vocabulary`) et la grammaire
(`/api/learning/grammar`) disposent de listes, statistiques et révisions.
Leurs routes `POST .../answer` enregistrent une **autoévaluation** :
`{"word": "hello", "correct": true}` ou
`{"rule": "Present Simple", "correct": false}`.
Elles mettent à jour la maîtrise ; les réponses grammaticales actualisent aussi
l’historique du profil. Les recommandations et plans sont recalculés à la lecture.
Le plan décrit des activités ; il ne les exécute pas automatiquement.
`GET /api/learning/plan/current` permet de retrouver le plan actif, y compris après
un redémarrage. `POST /api/learning/plan/items/{item_id}/complete` enregistre
son avancement avec `{"score": 80}`. Un nouvel appel à `/api/learning/plan`
génère un nouveau plan actif.

## Sauvegarde durable

SQLite conserve automatiquement le profil (dont les forces et historiques), les
20 derniers messages, les leçons et exercices avec leurs corrigés privés,
le vocabulaire, la grammaire, le plan actif et la session d’évaluation.
Chaque état est stocké dans une ligne SQLite par identifiant et restauré à sa
première utilisation après un redémarrage. Une requête modifiant les données est
confirmée après l’écriture ; un échec d’écriture renvoie `503` et annule sa
modification pour cet apprenant. Les autres profils restent indépendants.
Un état invalide n’est pas remplacé ; son chargement renvoie `503` sans bloquer
les autres apprenants.

Par défaut : `backend/data/zephyr.sqlite3`, indépendant du répertoire de lancement.
`DATABASE_PATH` permet de choisir un autre emplacement (préférer un chemin absolu).
`PERSISTENCE_ENABLED=false` désactive la sauvegarde : la séparation reste active,
mais profils et identifiants sont perdus au redémarrage.
Ces données sont locales et ignorées par Git ; le push GitHub ne les sauvegarde pas.

Pour créer une copie cohérente de **tous les apprenants**, même lorsque l’API fonctionne, depuis `backend/`
avec l’environnement virtuel activé :

```bash
python -m app.backup data/zephyr-backup.sqlite3
```

Choisir un nom différent à chaque copie ; une sauvegarde existante n’est jamais
écrasée. Pour restaurer : arrêter l’API, conserver l’ancien fichier et configurer
`DATABASE_PATH` vers une copie du fichier de sauvegarde, puis relancer l’API.
Garder également une copie sur un support distinct pour survivre à une perte du disque.

## Migration depuis la V0.7.0

La base existante est migrée automatiquement à son ouverture, dans une transaction.
Son profil unique est conservé sous l’identifiant :

```text
00000000-0000-0000-0000-000000000001
```

Utiliser cet identifiant dans `X-Learner-ID` pour retrouver les anciennes données.
Il n’existe que si l’ancienne base contenait un état sauvegardé. Les nouveaux
apprenants sont créés vides et ne récupèrent aucune copie de cet état.
Un état ancien invalide annule la migration et empêche le démarrage sans modifier
la base. Conserver une copie de sauvegarde avant une migration ; une base migrée
nécessite la V0.7.1 ou une version ultérieure.

## Limites actuelles

Le prototype gère plusieurs apprenants dans **un seul processus API**
(`--workers 1`, valeur par défaut). Ses sessions et verrous restent en mémoire :
plusieurs processus pourraient écraser leurs sauvegardes respectives pour un même
apprenant. Il ne dispose pas encore d’authentification ni d’interface web.
Les corrections d’exercices enrichissent les difficultés du profil ; elles ne
sont pas encore reliées automatiquement à un mot ou une règle précis.

La vision reste une application avec interface Next.js, voix, caméra et avatar.
Ces composants ne sont pas encore présents dans le dépôt.

Voir [l’état du projet](docs/PROGRESSION.md) et les [points ouverts](docs/BUGS.md).
