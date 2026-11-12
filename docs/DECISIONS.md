# 🧠 Décisions techniques — Zéphyr

Mise à jour : 21 octobre 2026 — backend V0.7.2.

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


## ADR-011 — Contrats stricts des réponses IA

**Date :** 21/10/2026 — V0.7.2.

**Décision :** centraliser les schémas Pydantic dans `learning/llm_schemas.py`
pour les corrections, évaluations, profils extraits, leçons et exercices.
Refuser les coercitions, champs inconnus, champs requis manquants, clés JSON
dupliquées et valeurs hors bornes. Contrôler aussi la cohérence des QCM et la
conformité des générations au niveau, à la compétence et au nombre demandés.

**Raison :** une réponse techniquement reçue du fournisseur ne suffit pas à
produire des données pédagogiques valides. Une erreur du fournisseur ou un
format invalide ne doit ni enrichir le profil ni pénaliser l’apprenant.

**Conséquences :** erreur `502` et rollback par apprenant ; plus de note zéro
par défaut sur une évaluation ouverte indisponible. L’extraction invalide du
profil interrompt le chat. Les erreurs ne recopient pas le corps de réponse brut.
Les tests simulent le fournisseur ; la validité du format ne garantit pas la
justesse pédagogique du contenu.

## ADR-012 — Lien explicite des exercices et calcul de maîtrise

**Date :** 21/10/2026 — V0.7.2.

**Décision :** accepter `target_category` (`grammar` ou `vocabulary`) et `target`
ensemble à la génération. Vérifier l’existence de la notion dans les données de
l’apprenant et sa langue avant l’appel IA. Le serveur attache sa désignation
canonique aux exercices et leur attribue des UUID ; le modèle ne décide pas du lien.

**Raison :** éviter une association déduite du texte qui pourrait modifier la
maîtrise de la mauvaise notion ou d’un autre apprenant.

**Conséquences :** chaque correction réussie ajoute une tentative correcte ou
incorrecte selon le booléen `correct` et recalcule la maîtrise avec les gestionnaires
existants. La grammaire alimente aussi `grammar_mastery` et `grammar_history`.
Le score de correction n’est pas assimilé à la maîtrise. Les soumissions répétées
comptent comme de nouvelles tentatives. Sans lien, seuls les résultats généraux
du profil sont intégrés. Les liens facultatifs sont compatibles avec les anciens
snapshots de version 1 ; aucune nouvelle migration SQLite n’est requise.


## ADR-013 — Interface locale servie par FastAPI et voix navigateur

**Date :** 12/11/2026.

**Décision :** interface sans compilation dans `frontend/`, montage `/ui/` sur le backend
existant. Les routes API et la version 0.7.2 sont préservées. L’interface utilise
le même origin et `X-Learner-ID`, stocké dans localStorage.

**Raison :** fournir immédiatement une interface locale utilisable sans installation
d’un second serveur ni exposition de clé API au navigateur. La V0.8 complète reste ouverte.

**Voix :** activation explicite, analyse Web Audio du micro sans connexion aux enceintes,
dictée Web Speech selon compatibilité, synthèse native du navigateur. Les pistes sont
arrêtées à la fin de l’écoute, sur erreur et au départ de la page. Pas d’écoute continue.
L’animation de sortie suit les événements de synthèse et une enveloppe visuelle ; elle
ne prétend pas mesurer le son PCM de la voix synthétisée. La dictée peut dépendre
d’un service distant du navigateur ; aucun audio n’est envoyé à l’API Zephyr.

**Limites :** reconnaissance et synthèse en français, qualité et disponibilité selon
le navigateur, microphone/dictée réels à valider. L’identifiant local n’est toujours
pas une authentification. Caméra, avatar, Next.js et streaming vocal non implémentés.

### Complément ADR-013 — état conversation et interaction du champ

Le mode visuel épuré est activé lors du premier échange, de l’écoute effective,
de la synthèse ou de la restauration d’un historique. L’état est déduit de la session,
sans nouvel enregistrement persistant. Les notifications restent dans le chat ;
les annonces de statut sont conservées pour les technologies d’assistance.
Les interactions des points ne démarrent ni microphone ni appel IA. La rotation
progresse par delta de temps ; le pointeur influence les positions projetées,
et une enveloppe amortit les pulsations. Les préférences de mouvement réduit
limitent les déplacements.

### Complément ADR-013 — thème et détachement des points

Le thème est local au navigateur (`zephyr.theme`), indépendant des profils et de
l’API. En l’absence de choix sauvegardé, il suit le système. Les points détachables
sont un sous-ensemble fixe avec enveloppes périodiques décalées ; les mêmes points
reviennent à leur emplacement sans création de particules supplémentaires. Les
couleurs sont calculées en HSL avec transition de palette indépendante du rendu CSS.
`prefers-reduced-motion` suspend détachement, rotation et évolution temporelle des teintes.

### Complément ADR-013 — halo et animation par état

Conserver les 2 100 points et renforcer le relief par taille, opacité, perspective
et tri en profondeur. Deux dégradés radiaux produisent le halo ; seuls quelques
points reçoivent un disque lumineux supplémentaire, sans flou par particule.
Des poids interpolés d’écoute, réflexion et parole pilotent les formes, teintes et
intensités ; les transitions restent progressives. Le mouvement réduit conserve
un rendu calme. La voix synthétisée ne fournit toujours pas de PCM à l’analyseur.

### Complément ADR-013 — objets 3D et vocabulaire visuel hors ligne

Les mêmes points interpolent entre positions libres et modèles volumétriques.
Les surfaces sont construites avec des primitives (boîtes, sphères, cylindres,
tores, prismes et cœur gonflé), puis tournées et projetées sur le canvas existant.
La première ébauche en silhouettes a été remplacée après retour utilisateur.
Les noms/traductions restent indépendants de la rotation.

La table locale de six objets/six langues évite un appel IA pendant les animations.
Aucune traduction n’est substituée pour une langue inconnue. Le profil reste
la référence pour `target_language` ; sélection et sauvegarde utilisent l’API
existante et l’identifiant apprenant. Une sauvegarde échouée reste un aperçu local.
La prononciation définit la langue de l’énoncé ; elle ne change pas la langue de
la dictée ni celle du chat. Aucun progrès n’est attribué à l’observation d’un objet.

## ADR-014 — Profil et évaluation sur l’API existante

**Date :** 12/11/2026.

**Décision :** ajouter un dialogue natif avec les sections profil et niveau, sans
modifier les routes ni la version 0.7.2 du backend. Le même client et l’identifiant
apprenant sont partagés ; l’ouverture suspend voix/micro et verrouille le chat.

**Langue :** la banque de questions est anglaise. Une garde explicite dans le
parcours vérifie le profil à l’entrée et avant réponse/bilan, sans modifier
implicitement sa langue. Cette garde d’interface n’est pas une nouvelle règle
d’authentification ou une restriction des appels API directs.

**Reprise :** lire la progression/question existante ; ne réinitialiser que sur
démarrage vierge ou recommencement explicite. Une réponse incertaine est conciliée
avec le serveur avant un éventuel renvoi. Le bilan utilise l’idempotence existante
de l’identifiant d’évaluation. Les objectifs sont ajoutés sans réécrire leur liste.

**Validation :** tests d’intégration en profils isolés, suite Python complète,
syntaxe/tests Node et contrôle UI mobile/ordinateur. Les cas nécessitant l’IA
sont simulés par la suite de tests ; aucune fausse note enregistrée pour l’utilisateur.

## ADR-015 — Comptes locaux et propriété des profils

**Date :** 12/11/2026 — 0.8.0-alpha.1.

Activer les comptes par défaut, avec tables SQLite partagées avec les états des
apprenants. Stocker les mots de passe avec scrypt N=131072/r=8/p=1 et sel aléatoire.
Utiliser des sessions opaques de 256 bits, empreintes SHA-256 en base et cookie
HttpOnly/SameSite Strict ; Secure requis en production. Vérifier la propriété de
chaque UUID sélectionné. Inscription et état initial sont écrits dans une transaction.
Le cookie présenté est renouvelé à la connexion et révoqué à la déconnexion.

Les mutations requièrent un en-tête dédié et une origine cohérente, sans CORS
permissif. Les tentatives sont limitées par IP et e-mail, avec au plus deux calculs
de hachage simultanés. Les mots de passe ne sont pas recopiés dans les erreurs de
validation. La documentation API expose le marqueur de mutation.

Préserver les profils anciens sans les attribuer au premier inscrit. Une commande
locale, API arrêtée, peut rattacher un profil non possédé à un compte existant et
révoque ses sessions. La sauvegarde SQLite inclut aussi comptes et sessions.
Le mode sans comptes reste uniquement pour les anciens tests/outils locaux et
est refusé en production. Confirmation e-mail, récupération de mot de passe et
MFA ne sont pas encore implémentés.

## ADR-016 — Vocal continu à tours alternés

Le mode est explicite et non mémorisé. Reprendre le micro après une réponse,
seulement si le compte est connecté, le document visible et aucune capture,
requête ou synthèse en attente. Libérer les pistes audio entre les tours pour
prévenir l’auto-transcription de la voix de Zéphyr. Arrêter la boucle au clic,
sur erreur, à l’ouverture d’un dialogue personnel, à la déconnexion ou en
arrière-plan. Le contrôleur isolé est testé sans appareil audio. Cette décision
remplace la limitation antérieure « pas d’écoute continue » de l’ADR-013.
