# Présence holographique — version 0.8.9

Choisir **Points** ou **Avatar humanoïde** sous la scène. Le choix est mémorisé localement (`zephyr.visualMode`), sans données de compte, audio ou caméra. Les phrases d’accueil sont conservées ; elles s’effacent au début d’une conversation.

## Objets en points et contours

15 silhouettes sélectionnées : maison, arbre, tasse, livre, poisson, cœur, pomme, voiture, avion, bateau, fusée, vélo, clé, parapluie et guitare. La banque de 36 géométries reste dans le code pour de futurs affinages, mais les autres ne sont plus tirées au sort.

Les textures ont été abandonnées. Les objets sont dessinés par 2 100 points lumineux, avec 40 % d’échantillonnage sur les contours et 60 % sur les surfaces. Courbes complémentaires sur sphères/tores, anse de tasse, cordes et rosace de guitare et cadre du vélo renforcent la lecture. Des lignes très fines accompagnent le volume ; rotation lente limitée autour d’une vue lisible. Transition : promenade, formation, objet, dissolution, sur 20 secondes.

Le sac mélangé parcourt les 15 objets avant de recommencer, sans répétition immédiate à la frontière. Nom français et traduction suivent le profil, en six langues hors ligne. Aucun vocabulaire n’est marqué appris automatiquement. Les points restent lumineux et se rassemblent pendant la synthèse.

**Aucune interaction au pointeur, toucher, clic ou clavier sur les points** : image sans focus ni capture tactile. Le micro reste commandé par ses boutons.

## Humanoïde redessiné

Buste original holographique : tête et mâchoire, cou et épaules continus, traits du visage en lignes, maillage fin et 2 500 particules. Yeux plus discrets, clignement, respiration, inclinaison et ouverture de bouche pendant la parole. Aucun suivi du visage ou de la souris. L’avatar reste stylisé : la synthèse native ne fournit pas de PCM, donc la bouche suit une enveloppe sans synchronisation phonétique.

Le choix de l’avatar n’active pas la caméra. Le bouton **Caméra** conserve l’aperçu local volontaire, sans image envoyée ou enregistrée. Guide [COMPANION](COMPANION.md).

## Moteur et replis

Three.js 0.187.0 et MeshSurfaceSampler, paquet officiel MIT conservé dans `frontend/vendor/three/`, sans CDN, modèle distant ni installation npm à l’usage. Cache limité à quatre géométries, ressources libérées à la sortie, résolution plafonnée et rendu suspendu quand la vue est masquée. Le générateur de textures a été supprimé.

WebGL 2 pour les points/contours et le buste 3D. Sans ce moteur ou lors d’une perte de contexte : repli sur les objets en points Canvas 2D et un humanoïde SVG assorti. Ces replis ne possèdent pas tous les contours et volumes de la version WebGL. Mouvement réduit : rotation, déplacements, clignement et cycle suspendus ; réponse visuelle vocale atténuée. Thèmes jour/nuit conservés.

Références : [WebGLRenderer](https://threejs.org/docs/pages/WebGLRenderer), [MeshSurfaceSampler](https://github.com/mrdoob/three.js/blob/dev/docs/pages/MeshSurfaceSampler.html.md).

## Validation de la version

293 tests Python et 40 tests Node réussis, 2 avertissements de dépendances existants. Contrôles du mélange, des volumes/échantillons, du buste sans textures, de sa réaction vocale, du repos réduit et de la libération des ressources. Syntaxe et diff contrôlés. Navigateur : livre en contours et buste WebGL observés, voix en état speaking puis retour au repos, choix persistant, thèmes jour/nuit, 319/1280 px sans débordement, caméra inactive et aucune erreur console observée. Version API et OpenAPI : 0.8.9, serveur local relancé sur 8001. Le repli sur appareil sans WebGL, voix et caméra matérielles restent à valider avec l’utilisateur.
