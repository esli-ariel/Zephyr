# Interface locale Zéphyr

## Transcription — délai de cinq secondes

Sélecteur de langue dans le chat, français et anglais inclus, synchronisé avec les réglages. Après cinq secondes sans nouvelle parole, la dictée confirmée est envoyée ; compte à rebours et bouton Garder pour relire. Édition, reprise vocale et suspensions gèrent le délai sans envoi tardif ; erreurs et provisoires restent manuels. Exercices oraux toujours validés explicitement. Guide [VOICE](../docs/VOICE.md). 47 Node et 3 Python interface réussis, QA de reconnaissance simulée ; dictée matérielle à valider.


## Présence actuelle — version 0.8.9

Choix mémorisé **Points / Avatar humanoïde**. 15 silhouettes aléatoires en points et contours holographiques ; textures retirées. Guitare/vélo détaillés, rotation douce. Avatar redessiné en buste continu avec traits en lignes, maillage et particules. Three.js local (MIT), sans CDN ni build. Points sans interaction souris/toucher/clavier ; repli Canvas/SVG sans WebGL 2. Guide [PRESENCE](../docs/PRESENCE.md). Validation de version : 293 Python et 40 Node réussis. Les étapes datées ci-dessous décrivent aussi l’historique.

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
- Fin de dictée ou second clic : finalisation, puis envoi confirmé ou relecture selon le réglage ; microphone libéré.
- Sans reconnaissance : saisie clavier et diagnostic du micro dans les réglages.
- Lecture native : langue, voix, vitesse, tonalité et volume configurables ; arrêt accessible.
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

1. Réglages vocaux réalisés : langues, choix de voix et vitesse ; guide [VOICE.md](../docs/VOICE.md).
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
- Aucune interaction des points au pointeur, clic, toucher ou clavier ; le canvas est une image sans focus.
- Les animations suivent uniquement les états vocaux et le cycle automatique.
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

Le cycle utilise désormais 15 modèles sélectionnés (banque géométrique de 36), dont :
maison (corps, toit prismatique, cheminée), arbre (tronc et feuillage), tasse creuse
avec anse, livre épais, poisson avec nageoires et cœur gonflé. Les points sont
échantillonnés sur les surfaces, puis tournés autour des axes Y/X avant projection.
La rotation automatique se suspend en mouvement réduit ; les légendes restent fixes.
Cette version remplace les silhouettes plates de la première ébauche.

Les points ont une opacité/luminosité renforcée, des cœurs clairs au premier plan et
une composition additive en mode nuit. Le mode jour garde une palette contrastée.

La table hors ligne propose six langues. `resolveLanguage` reconnaît les noms
usuels, accents et codes régionaux ; une langue inconnue reste explicitement non
prise en charge. La langue suit désormais Mon profil ; le profil est également
relu après le chat. Les objets se forment automatiquement et conservent nom/traduction.
Les boutons Autre objet/Écouter et le sélecteur ont été retirés à la demande de
l’utilisateur. Aucun ajout automatique à la maîtrise du vocabulaire. Le chat et la
dictée conservent les réglages vocaux indépendants.

Vérifier avec `node --test frontend/tests/*.test.cjs` : 40 tests passent, dont langues, mélange sans répétition, volumes des 15 objets actifs et échantillonnage de surfaces Three.js.
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

## Réglages vocaux et transcription

Bouton **Réglages vocaux ⚙** près du micro : langues séparées (ou langue du profil), voix disponibles, vitesse/volume/tonalité, pause de fin, envoi automatique ou relecture, exemple avec arrêt et diagnostic de niveau. Valeurs par défaut : français, voix recommandée, 0,95×, pause 1,6 s. Préférences seules dans `zephyr.voicePreferences`.

`voice-tools.js` normalise les réglages/résultats ; `voice-engine.js` gère capture, finalisation et synthèse ; `voice-settings.js` fournit le dialogue. Mots provisoires distincts, brouillon préservé et erreur jamais envoyée automatiquement. CI : syntaxe et 23 tests Node. Trois tests Python interface réussis, baseline Python complète précédente 274. Exemple natif et persistance contrôlés ; parole réelle/permissions et boucle complète encore à valider. [Guide et limites](../docs/VOICE.md).

## Plan, révisions, caméra et avatar — 13 novembre 2026

Le bouton **Mon parcours** ouvre profil, niveau, plan et révisions. `journey-ui.js` prépare une séance, présente le contenu et les corrections, reprend l’activité, permet d’ajouter des notions et d’autoévaluer les cartes dues. `companion-ui.js` affiche la présence vocale ; `camera-controller.js` isole les permissions/pistes vidéo. Les styles utilisent les thèmes existants, sans bibliothèque supplémentaire.

Caméra volontaire et locale, arrêt en arrière-plan/dialogue/fermeture ; aucun envoi d’images. Avatar SVG réactif aux états du moteur natif, sans synchronisation phonétique. Nouveaux modules contrôlés dans la CI. Validation : 287 Python et 27 Node ; QA simulée complète et responsive 319/1280 px, permissions réelles restantes. [JOURNEY](../docs/JOURNEY.md) · [COMPANION](../docs/COMPANION.md).

## Séance du jour et exercices à l’oral — 13 novembre 2026

**Ma séance ↗ / Mon parcours → Aujourd’hui** présente les révisions dues, la prochaine activité et les compteurs réels. Cet accueil lit les données sans générer de contenu. La carte reste compacte pendant la conversation.

Dans les exercices du plan, **Répondre à l’oral** produit une dictée modifiable ; **Utiliser cette réponse** reporte le texte, puis **Corriger ma réponse** envoie explicitement. Langue du profil, choix manuel si inconnue, QCM exact, répétition et lecture plus lente. Le vocal du parcours reste séparé de l’envoi automatique du chat ; caméra locale, points et avatar conservent leur direction.

Validation : **293 Python et 34 Node réussis**, deux avertissements existants. Navigateur testé avec voix/contenus simulés, sans microphone ou IA réels ; 319/1280 px sans débordement. Permissions et voix matérielle restent à valider. [Guide et limites](../docs/DAILY_SESSION.md).

## Profil et compte dans la navigation

**Mon profil**, dans la barre latérale, ouvre une page complète avec langue, niveau, objectifs, compétences, bilans et progression. **Modifier mon profil** enregistre les changements sans quitter la page. Le compte est accessible en bas de cette navigation ; sur mobile, ouvrir le menu. La conversation et son brouillon sont conservés entre les vues, tandis que les médias s’arrêtent au passage vers le profil.

Lien direct : `/ui/#profil`. Jour/nuit, clavier et menu mobile vérifiés ; 34 Node et 3 Python interface réussis, baseline Python complète précédente 293. [Guide PROFILE](../docs/PROFILE.md).
