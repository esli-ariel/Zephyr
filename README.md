# 🌪️ Zéphyr

Assistant d’apprentissage des langues. La version **0.8.0-alpha.1** fournit un
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

Interface locale : `http://127.0.0.1:8000/ui/` ; API : `http://127.0.0.1:8000` ; documentation interactive :
`http://127.0.0.1:8000/docs`.

## Tests

Depuis la racine, environnement virtuel activé :

```bash
python -m pytest -q
```

Les tests isolent la configuration et bloquent les appels réels à OpenRouter.
Une configuration GitHub Actions exécute la même suite sous Python 3.12.

## Comptes et sélection de l’apprenant

Les comptes sont activés par défaut. Ouvrir `/ui/`, cliquer **Créer un compte**,
puis renseigner prénom, e-mail et phrase secrète de 8 à 128 caractères. La session
est conservée dans un cookie HttpOnly ; **Mon compte** permet de se déconnecter.
Le serveur rattache chaque profil à son compte et refuse l’accès aux autres profils.

Pour un client API, commencer par `/api/auth/register` ou `/api/auth/login`, conserver
les cookies du client et reprendre le `learner_id` renvoyé. Les opérations pédagogiques
exigent `X-Learner-ID` ; les mutations exigent aussi `X-Zephyr-Request: 1`. `/docs`
propose ces champs. `/`, `/health`, `/ui/`, `/docs` et `/openapi.json` restent publics.

`POST /api/learners` crée un profil supplémentaire uniquement pour le compte connecté.
Un UUID absent/mal formé donne `400`, un profil inconnu ou appartenant à un autre
compte `404`, et une session absente/expirée `401`. Les états restent séparés et
les opérations sont sérialisées par apprenant, dans un seul processus API.

Les anciens profils locaux sont conservés sans attribution automatique. Une commande
locale permet de les rattacher après inscription. Les comptes sont propres à cette
installation ; confirmation et réinitialisation par e-mail ne sont pas encore proposées.
Voir [comptes, API et récupération des anciens profils](docs/ACCOUNTS.md).

## Parcours pédagogique

Avec une session connectée, `X-Learner-ID` et le marqueur de mutation requis :

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

## Exercices liés à une notion

Pour entraîner un mot ou une règle déjà enregistré chez l’apprenant, ajouter
`target_category` et `target` à `POST /api/learning/exercises` :

```json
{
  "topic": "Habitudes quotidiennes",
  "skill": "grammar",
  "count": 2,
  "target_category": "grammar",
  "target": "Present Simple"
}
```

`target_category` accepte `grammar` ou `vocabulary`. Les deux champs doivent être
fournis ensemble ; la notion doit exister chez l’apprenant sélectionné et dans
sa langue cible. Le serveur attache le lien aux exercices générés et attribue
des identifiants uniques. Le modèle ne peut pas choisir ou modifier ce lien.

Chaque soumission corrigée met à jour la maîtrise de la notion liée à partir de
`correct` : réponse correcte ou incorrecte. Pour la grammaire, la maîtrise et
l’historique du profil sont également actualisés. Le score détaillé reste disponible
dans la correction ; il n’est pas utilisé comme pourcentage de maîtrise du mot
ou de la règle. Chaque nouvelle soumission compte comme une tentative.

Les exercices sans lien, y compris les anciens, restent corrigeables et actualisent
les difficultés du profil sans modifier une notion par déduction. Le lien est
conservé dans SQLite et dans les copies de sauvegarde.

## Validation des réponses IA

Les réponses structurées de correction, évaluation, extraction de profil,
génération de leçons et d’exercices sont validées strictement : champs requis,
types, bornes, valeurs autorisées, champs supplémentaires et clés JSON dupliquées.
Les scores doivent être des entiers entre 0 et 100 et `correct` un vrai booléen ;
`"false"`, les scores hors limites et les listes mal formées sont refusés.
Les QCM exigent au moins trois options distinctes et une réponse présente parmi elles.
Le niveau, la compétence et le nombre d’exercices générés doivent correspondre
à la demande ; la langue et le niveau des leçons sont aussi vérifiés.

Une réponse IA invalide ou une panne du fournisseur renvoie `502`. La requête
n’enregistre alors ni contenu partiel ni progrès ; une évaluation indisponible
ne devient plus une note de zéro. Une nouvelle soumission peut être tentée.
L’extraction d’un profil invalide interrompt également le chat sans modifier l’état.
Les erreurs exposées ne recopient pas les réponses brutes du fournisseur.

Le niveau envoyé à `PUT /api/learner/profile` doit être A1, A2, B1, B2, C1 ou C2.
La compétence d’un exercice doit être `vocabulary`, `grammar`, `comprehension`,
`expression` ou `translation`. Une valeur invalide renvoie `422` avant génération.
Ces contrôles garantissent le format, pas la justesse pédagogique d’un modèle réel.

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
`PERSISTENCE_ENABLED=false` est réservé au mode local sans comptes (`AUTH_ENABLED=false`) ;
avec les comptes activés, la persistance est obligatoire.
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

Après rattachement local de ce profil à votre compte, cet identifiant dans
`X-Learner-ID` permet de retrouver les anciennes données (voir `docs/ACCOUNTS.md`).
Il n’existe que si l’ancienne base contenait un état sauvegardé. Les nouveaux
apprenants sont créés vides et ne récupèrent aucune copie de cet état.
Un état ancien invalide annule la migration et empêche le démarrage sans modifier
la base. Conserver une copie de sauvegarde avant une migration ; une base migrée
nécessite la V0.7.1 ou une version ultérieure.

## Limites actuelles

Le prototype gère plusieurs apprenants dans **un seul processus API**
(`--workers 1`, valeur par défaut). Ses sessions et verrous restent en mémoire :
plusieurs processus pourraient écraser leurs sauvegardes respectives pour un même
apprenant. Il dispose maintenant de comptes locaux et de contrôles de propriété des profils. Une première interface de conversation est disponible sur `/ui/`.
Les corrections enrichissent les difficultés du profil et la maîtrise des notions
explicitement liées. La qualité pédagogique du contenu généré n’a pas été validée
par des appels réels pendant les tests de cette version.

La première interface est en HTML/CSS/JavaScript, sans dépendance de compilation. Elle propose une sphère de points, le chat, la dictée lorsque le navigateur la prend en charge et la synthèse vocale. Next.js, caméra et avatar ne sont pas implémentés. Voir `frontend/README.md` pour les détails et limites.

Voir [l’état du projet](docs/PROGRESSION.md) et les [points ouverts](docs/BUGS.md).

## Interface conversationnelle — aperçu V0.8 (12 novembre 2026)

Ouvrir `/ui/` sur le même port que FastAPI. Lors de la validation locale du 12 novembre,
le port 8000 était occupé : lancement avec `python -m uvicorn app.main:app --host 127.0.0.1 --port 8001`,
puis `http://127.0.0.1:8001/ui/`. Le backend garde sa version 0.7.2.

- Création/restauration de l’apprenant et reprise des messages, identifiant conservé dans le navigateur.
- Sphère de 2 100 points : volume réel du microphone à l’écoute, animation pendant la lecture vocale.
- Micro activé par clic, arrêt à la fin d’une dictée ou manuellement, libération des pistes audio.
- Saisie texte et suggestions, lecture des réponses, coupure et arrêt de la voix.
- Reconnaissance `fr-FR`, dépendante du navigateur et éventuellement de son service distant.
- La voix de synthèse utilise le navigateur, pas un fournisseur vocal temps réel. Son animation
  utilise les événements de lecture et une enveloppe visuelle, pas une analyse de son PCM.
- Aucun écran d’évaluation, de plan ou de correction n’est encore intégré à cette interface.

Validation : 261 tests réussis (2 avertissements), JavaScript vérifié par `node --check`,
chat réel OpenRouter depuis l’interface, état de lecture vocale observé, reprise après rechargement
et affichage mobile/ordinateur contrôlés. Microphone réel et dictée à valider avec l’utilisateur.

Pendant une conversation, les textes près de la sphère disparaissent et les points
bougent davantage. Ils réagissent au pointeur et pulsent au clic/toucher ou avec
Entrée/Espace sur la sphère. Les messages utiles restent dans le panneau de discussion.
Le mode épuré s’applique aussi à la reprise d’un historique.

Les points peuvent désormais se détacher de la surface puis la rejoindre. Leurs
nuances évoluent lentement. Le bouton soleil/lune en haut à droite sélectionne
le mode jour ou nuit ; le choix est mémorisé dans le navigateur. Sans choix explicite,
le thème suit la préférence système. Le mouvement réduit suspend le détachement.

La sphère bénéficie aussi d’un halo diffus, de points de tailles et luminosités
différentes selon leur profondeur et de mouvements propres aux états : respiration
au repos, ondulations à l’écoute, torsion en spirale en réflexion, expansion à la parole.

## Nuage libre et objets 3D — 12 novembre 2026

Les points se promènent librement, se rassemblent pendant la synthèse vocale
et alternent au repos avec six objets en volume tournant lentement : maison, arbre,
tasse, livre, poisson et cœur. Le nom français et la traduction restent fixes sous
l’objet ; les points conservent leur éclat, leur halo et leur interaction au pointeur.

Dans « Mots en images », choisir la langue enregistre `target_language` dans le
profil. La sélection suit également le profil restauré ou actualisé après un chat.
Traductions hors ligne en anglais, espagnol, allemand, italien, portugais et français.
Une langue non prise en charge est signalée, sans traduction inventée. « Autre objet »
force la formation suivante ; « Écouter » prononce le mot dans sa langue. Ces cartes
ne marquent pas automatiquement le vocabulaire comme appris.

Validation ciblée : 4 tests Node et 3 tests d’intégration interface réussis (2 avertissements
Python existants). Affichage et profil persisté contrôlés en navigateur, modes jour/nuit
et mobile 319 px. Aucune publication ni push.

## Profil et évaluation accessibles depuis l’interface

Le bouton **Mon profil et mon niveau** ouvre le parcours pédagogique :

- **Mon profil** : prénom, langue étudiée, niveau déclaré A1–C2 et ajout d’objectifs.
- **Mon niveau** : démarrer/reprendre une évaluation adaptative d’anglais, répondre
  aux QCM ou aux questions ouvertes, consulter la correction et le bilan final.
- Le bilan donne le score global, le niveau estimé, les compétences, forces et
  points à travailler ; il est enregistré dans le profil sans duplication.
- Une session peut être reprise après fermeture ou rechargement. Recommencer
  demande une action explicite et conserve les bilans déjà enregistrés.

La banque actuelle est **uniquement en anglais**. L’interface refuse de l’utiliser
pour une autre langue cible ; elle ne change pas automatiquement la langue du profil.
Les questions ouvertes et le bilan qui les reprend nécessitent OpenRouter. Le résultat
est une estimation pédagogique. Le niveau déclaré peut être modifié, mais le champ
vide ne supprime pas un niveau déjà enregistré.

Validation locale : **263 tests Python et 4 tests Node réussis**, deux avertissements
Python existants. CI enrichie avec la syntaxe et les tests frontend. Les écrans
profil/évaluation ont été vérifiés à 319 et 1100 px. Les écrans de plan d’apprentissage,
d’exercices et de correction constituent la suite du jalon V0.8.

## Vocal continu et validation actuelle

Après connexion, le bouton **∞ Vocal continu** enchaîne écoute, réponse puis reprise
de l’écoute. Le micro est suspendu pendant la réflexion et la synthèse. Un second
clic, une erreur, l’ouverture du profil/compte ou le passage en arrière-plan arrête
le mode ; il ne reprend pas automatiquement au rechargement. La dictée dépend du
navigateur. La boucle avec une voix réelle reste à essayer avec l’utilisateur.

Validation de cette version : **274 tests Python et 7 tests Node réussis**, deux
avertissements Python connus. L’authentification, l’isolement des comptes et le
contrôleur de boucle vocale sont testés. Aucun compte personnel n’est créé par l’agent.
La récupération par e-mail et les écrans plan/exercices restent à réaliser.

L’écran de compte propose maintenant une présentation en deux panneaux sur
ordinateur, un formulaire compact sur mobile et des onglets Connexion/Inscription.
Le bouton en forme d’œil affiche ou masque chaque champ de mot de passe.
