# Interface locale Zéphyr

HTML, CSS et JavaScript natifs, servis par FastAPI sur `/ui/`. Aucun build ni npm install.
Depuis `backend/` avec le venv activé :

```sh
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Ouvrir http://127.0.0.1:8001/ui/. Le profil principal est fourni par la session du compte ; les échanges sont
restaurés depuis SQLite via l’API. Le jeton de session reste dans un cookie HttpOnly,
sans mot de passe ni jeton d’authentification dans localStorage.

## Interaction vocale

- Clic micro : autorisation, analyse du volume réel et dictée si disponible.
- Fin de dictée ou second clic : envoi du texte ; microphone libéré.
- Sans reconnaissance : visualisation du micro disponible, envoi par clavier.
- Lecture des réponses : voix native française, coupure et arrêt accessibles.
- Le bouton « Essayer la voix » ne consomme pas d’appel OpenRouter.
- La dictée peut envoyer l’audio au service du navigateur ; pas de garantie hors ligne.
- La synthèse ne fournit pas de PCM : les points suivent une enveloppe animée et
  les événements de lecture, pas une mesure audio exacte.
- `prefers-reduced-motion` réduit le mouvement.

## Vérification au 12 novembre 2026

261 tests Python réussis, 2 avertissements ; `node --check frontend/app.js` réussi.
Conversation réelle et état de lecture vocale observés, historique restauré après
rechargement, mobile 319 px et ordinateur 1440 × 960 contrôlés. Pas de validation
de dictée ou de capture avec une voix réelle ; qualité sonore à valider avec l’utilisateur.

## Améliorations proposées

1. Langue de conversation, choix de voix et vitesse de lecture.
2. Mode immersif centré sur la sphère, transcription discrète.
3. Choix de couleur et densité des particules, intensité réduite.
4. Fiches profil, progression, évaluation, plan et exercices à côté du chat.
5. Voix continue, détection de fin de phrase et interruption, avec moteur vocal adapté.

## Conversation épurée et interactions

Après le premier message, le démarrage de l’écoute ou de la lecture vocale,
l’introduction et les légendes de la sphère sont masquées. Ce mode est aussi
activé à la restauration d’un historique. Le micro reste accessible ; notifications
et erreurs sont affichées dans le panneau de conversation.

- Mouvement plus ample, sphère agrandie, rotation accélérée et ondulations.
- Pointeur : les points s’écartent localement.
- Clic/toucher ou Entrée/Espace lorsque la sphère est focalisée : pulsation.
- Ces interactions sont purement visuelles, sans activation du micro ni appel IA.
- Mouvement réduit respecté. Validation visuelle à 319 et 1440 px.

## Particules libres et thèmes jour/nuit

Un sixième des points est éligible au détachement. Des cycles décalés les font
s’éloigner et revenir progressivement sur la surface, sans apparition/disparition.
L’amplitude augmente avec l’activité et la voix. Le mouvement réduit coupe le
détachement et fige la rotation/dérive de couleur. Les nuances HSL évoluent lentement
et varient légèrement entre particules, avec une palette adaptée à chaque thème.

Bouton soleil/lune dans l’en-tête : choix conservé sous `zephyr.theme`. Sans préférence
explicite, le thème suit `prefers-color-scheme`, y compris ses changements. Le thème
est appliqué dès le chargement de la page ; les couleurs du canvas interpolent
progressivement lors d’une bascule. Sans localStorage, le bouton fonctionne pour
la session.

Validation du 12 novembre : bascule jour/nuit et mémorisation après rechargement
observées dans le navigateur, rendu à 319 et 1440 px sans débordement, aucun message
d’erreur console observé. Trois tests d’intégration interface réussis, deux avertissements
existants ; syntaxe JavaScript et diff vérifiés. Pas de nouvel appel IA ou capture micro.

## Relief et comportement par état

- Halo : deux dégradés radiaux, plus présents en écoute et pendant la réponse, atténués en mode jour.
- Profondeur : tri de l’arrière vers l’avant, perspective, luminosité/opacité et taille variables ; quelques points brillants au premier plan.
- Repos : respiration lente, rotation douce.
- Écoute : ondes selon la latitude, renforcées par le volume RMS.
- Réflexion : torsion en spirale, rotation accélérée, transition vers le bleu-violet.
- Parole : expansion et vagues, halo renforcé selon l’enveloppe visuelle de synthèse.
- Transitions interpolées entre états, sans bascule brutale de forme ou de couleur.
- Mouvement réduit et thèmes précédents conservés ; nombre de points inchangé.

Validation du 12 novembre : rendu jour et nuit, état réflexion puis synthèse observés
lors d’une conversation OpenRouter réelle, retour au repos, aucune erreur console
observée, absence de débordement à 319 px. Syntaxe JS et diff vérifiés. Microphone
réel non testé pour cet ajustement. La parole conserve une animation synthétique,
sans mesure PCM du son émis. Les 261 tests backend de référence n’ont pas été
réexécutés pour ce changement de rendu seul.

## Nuage libre, formes 3D et traductions

Le rendu conserve 2 100 points et passe progressivement entre promenade libre,
objets au repos, nuage en spirale lors de la réflexion et rassemblement pendant
la lecture vocale. Un cycle de repos dure 20 secondes : promenade, formation, objet
lisible, dissolution. Les légendes apparaissent une fois la forme stabilisée.

Six modèles en volume sont générés par `ZephyrVocabulary.buildGeometry` :
maison (corps, toit prismatique, cheminée), arbre (tronc et feuillage), tasse creuse
avec anse, livre épais, poisson avec nageoires et cœur gonflé. Les points sont
échantillonnés sur les surfaces, puis tournés autour des axes Y/X avant projection.
La rotation automatique se suspend en mouvement réduit ; les légendes restent fixes.
Cette version remplace les silhouettes plates de la première ébauche.

Les points ont une opacité/luminosité renforcée, des cœurs clairs au premier plan et
une composition additive en mode nuit. Le mode jour garde une palette contrastée.

La table hors ligne propose six langues. `resolveLanguage` reconnaît les noms
usuels, accents et codes régionaux ; une langue inconnue reste explicitement non
prise en charge. Le sélecteur met à jour `target_language` dans le profil via l’API.
Sans API ou si l’enregistrement échoue, l’affichage local est indiqué comme aperçu.
Le profil est relu après le chat sans écraser une sélection en cours.

« Autre objet » forme le modèle suivant. « Écouter » est activé seulement lorsque
le mot est affiché et lance la synthèse avec la langue cible. Le chat et la dictée
restent en français. Aucun ajout automatique à la maîtrise du vocabulaire.

Vérifier avec `node --test frontend/tests/visual-vocabulary.test.cjs`. Quatre tests
passent : langues/accents/locales, langues inconnues, couverture lexicale et géométrie
3D (bornes, étendue en profondeur et covariance non planaire des six modèles).
Les trois tests Python d’interface passent aussi, y compris le nouveau fichier JS.
Vérification navigateur : Arbre/Árbol, profil espagnol restauré puis anglais rétabli,
prononciation/rassemblement, tasse et maison en volume, points lumineux en nuage
libre, modes jour/nuit et absence de débordement à 319 px. Le micro réel n’a pas été testé.

## Profil et évaluation

`learning-ui.js` et `learning-ui.css` ajoutent le dialogue natif **Mon profil et mon
niveau**. Il utilise le client API existant et le même identifiant apprenant.
L’ouverture arrête la voix/le micro et verrouille la saisie du chat ; fermeture
ou Échap rend les contrôles disponibles. Navigation Mon profil / Mon niveau.

Profil : lecture et mise à jour de nom/langue/niveau, ajout d’un objectif distinct.
Le niveau vide ne supprime pas un niveau existant, conformément au contrat actuel.
Évaluation : garde de langue anglaise, démarrage, reprise, radio QCM ou texte libre,
correction, question suivante, bilan détaillé et recommencement explicite.
Le résultat enregistré est appliqué au profil par l’API.

Une réponse dont l’accusé réseau est perdu déclenche une relecture de la question
serveur avant d’offrir une nouvelle soumission. Si la vérification échoue, seule
la reprise depuis le serveur est proposée. Les réponses et messages IA sont insérés
comme texte. Aucun appel IA réel n’est utilisé dans les tests automatisés.

Validation du 12 novembre : 263 tests backend (2 avertissements), 4 tests Node,
syntaxe JS et diff valides. Deux nouveaux tests d’intégration couvrent profil/reprise
et bilan idempotent/recommencement avec des apprenants isolés. Le navigateur a
validé le profil, l’entrée du test d’anglais, la première question et le retour au
chat, ainsi que le mobile 319 px. Aucune réponse de test n’a été inscrite dans
l’évaluation de l’utilisateur pendant la vérification UI.

Reste à intégrer : plan, exercices et corrections dans le parcours visuel.

## Comptes et vocal continu — 0.8.0-alpha.1

`account-ui.js` fournit inscription, connexion et déconnexion. Le bootstrap utilise
`/api/auth/session` et ignore l’ancien identifiant local en mode authentifié. Les
requêtes gardent les cookies de même origine et transmettent `X-Zephyr-Request: 1`.
Une expiration de session suspend le vocal, efface la conversation visible et recharge
l’écran de connexion. Déconnexion et nouvelle connexion rechargent l’application
pour ne pas conserver l’état personnel d’un autre compte. Aucun compte personnel
n’a été créé pendant la validation des formulaires.

`voice-loop.js` est un contrôleur à activation explicite, sans préférence persistée.
L’écoute reprend après un tour terminé seulement si le compte est connecté, le
chat libre, le micro arrêté, le document visible et aucune synthèse en attente.
La lecture, le chargement et les erreurs ne provoquent pas de boucle de capture
concurrente. Le micro est libéré à chaque fin de capture ; les permissions refusées
ou erreurs de service désactivent le mode. Une absence de parole permet une nouvelle
écoute. Profil, compte, déconnexion, arrière-plan et départ arrêtent la boucle.

Tests : 7 Node (dont 3 sur activation/arrêt/blocage de la boucle) et 273 Python.
La boucle microphone/réponse réelle reste à essayer après inscription et autorisation.
Voir `docs/ACCOUNTS.md` pour la sécurité et la récupération des anciens profils.

## Connexion/inscription — ajustement du 12 novembre

Nouvelle composition à deux panneaux sur ordinateur et un panneau sur mobile.
Minimum d’inscription huit caractères (maximum 128), aligné sur l’API. Boutons
d’affichage/masquage des deux champs secrets avec labels accessibles ; ces champs
sont vidés à la fermeture même après affichage. L’adresse e-mail est conservée
en mémoire pendant un changement d’onglet, sans stockage local.
Rendu vérifié à 319/1200 px et minimum=8 observé dans le DOM. Tests de limite et
connexion à huit caractères dans `backend/tests/test_auth.py`.
