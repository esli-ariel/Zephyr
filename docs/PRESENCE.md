# Présence visuelle — 13 novembre 2026

Choisir **Points** ou **Avatar humanoïde** sous la scène. Le choix est mémorisé localement (`zephyr.visualMode`), sans donnée de compte, audio ou caméra. Les phrases d’accueil sont conservées ; elles s’effacent au début d’une conversation.

## Objets et matières

36 objets : maison, arbre, tasse, livre, poisson, cœur, pomme, banane, poire, voiture, avion, bateau, fusée, vélo, chaise, table, lampe, clé, parapluie, horloge, étoile, lune, fleur, bouteille, chapeau, château, pont, théière, ballon, diamant, tambour, bonhomme de neige, globe, appareil photo, guitare et ananas.

Un sac mélangé parcourt tous les objets avant de recommencer, sans répétition immédiate entre cycles. Le cycle de 20 secondes alterne promenade, formation, objet et dissolution. Les modèles sont construits en volumes, éclairés et tournants : matériaux bois, métal, céramique, papier, tissu, pierre et fruits. Les textures sont générées localement par Canvas ; ce sont des illustrations 3D texturées, pas des scans photographiques. Nom français et traduction suivent la langue du profil (six langues hors ligne). Aucun vocabulaire n’est marqué appris automatiquement.

Les points restent lumineux et se rassemblent pendant la synthèse. **Aucune interaction au pointeur, au toucher, au clic ou au clavier sur les points** : canvas décoratif accessible comme image, sans focus ni capture tactile. Le micro reste commandé par ses boutons.

## Moteur et repli

Three.js 0.187.0 et MeshSurfaceSampler, paquet npm officiel sous licence MIT conservée dans `frontend/vendor/three/`. Distribution locale, sans CDN, téléchargement de modèles ou installation npm à l’usage. Échantillonnage pondéré des surfaces ; cache limité à quatre géométries, matériaux et textures réutilisés, ressources libérées à la sortie. Résolution de rendu plafonnée, rendu suspendu quand la vue est masquée.

WebGL 2 est nécessaire aux matières 3D. Sans ce moteur ou lors d’une perte de contexte, repli sur les objets en points Canvas 2D et sur un buste SVG pour l’avatar ; ces replis ne proposent pas les textures 3D. Mouvement réduit : rotation/déplacements et cycle aléatoire suspendus, objet statique. Thèmes jour/nuit conservés.

Références techniques : [WebGLRenderer](https://threejs.org/docs/pages/WebGLRenderer), [MeshSurfaceSampler](https://github.com/mrdoob/three.js/blob/dev/docs/pages/MeshSurfaceSampler.html.md).

## Avatar et voix

Buste humanoïde stylisé : respiration, clignement des yeux, inclinaison et bouche animée par l’état vocal. Aucun suivi du visage ou de la souris. La synthèse native ne fournit pas de PCM : mouvement de bouche par enveloppe, sans synchronisation phonétique. Le choix de l’avatar n’active pas la caméra. Le bouton **Caméra** conserve l’aperçu local volontaire, sans image envoyée ou enregistrée.

## Validation

39 tests Node réussis, dont géométrie et échantillonnage des 36 objets, mélange sans répétition et récupération du choix ; 3 tests Python interface réussis, avec 2 avertissements de dépendances existants. Syntaxe et diff vérifiés. Dans le navigateur : moteur WebGL actif, lampe texturée et avatar observés, choix restauré après rechargement, thèmes jour/nuit, synthèse native déclenchée puis retour au repos, largeur 319 px sans débordement, caméra inactive. Le repli et la restauration de contexte ne sont pas validés sur un appareil privé de WebGL ; voix et caméra matérielles restent à valider avec l’utilisateur.
