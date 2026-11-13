# Page de profil et navigation latérale

## Accès

La barre latérale contient **Conversation**, **Mon profil**, **Mon parcours** et **Compte**. Le compte est placé en bas de la barre ; il ne se trouve plus dans l’en-tête. Sur mobile, le bouton menu ouvre la navigation sans réduire la largeur utile de la page.

La page **Mon profil** est une vue complète à `/ui/#profil`, et non un dialogue supplémentaire. L’adresse se recharge directement. Conversation reste accessible à `/ui/#conversation` ; le changement de vue conserve les messages, le brouillon et les éléments du nuage dans le même document. Entrer dans le profil arrête micro, lecture et caméra ; le rendu du nuage est suspendu pendant que sa vue est masquée.

## Contenu

- identité du profil, langue étudiée et niveau du profil ;
- progression du plan courant, révisions dues et nombre de bilans enregistrés ;
- objectifs, compétences avec scores réels, points forts et axes de travail ;
- trois derniers bilans enregistrés, sans dates inventées ;
- accès au compte, à l’évaluation et à la séance du jour.

Une compétence absente reste « Non évaluée ». Une progression indisponible affiche un tiret et un message, sans fabriquer de score. Le niveau du profil peut être déclaré ou actualisé par une évaluation ; les bilans restent des estimations pédagogiques. Les compteurs viennent de l’API quotidienne existante et conservent son périmètre de plan/langue.

**Modifier mon profil** ouvre un formulaire dans la page : prénom, langue, niveau et nouvel objectif. Les objectifs existants sont conservés. Une réponse en erreur laisse le formulaire et ses saisies disponibles ; le bouton Annuler n’enregistre rien. Le prénom pédagogique reste distinct du nom du compte. Aucun nouveau paramètre d’authentification ni endpoint de suppression n’est ajouté.

## Compte et confidentialité

Le bouton Compte conserve les écrans existants de connexion, inscription et déconnexion. Une session connectée présente le nom du compte dans la navigation ; la page affiche son e-mail uniquement à partir de la session du propriétaire. Hors connexion, la page reste une invitation à se connecter et ne charge pas les données pédagogiques.

Sur les installations explicitement sans authentification, le bouton indique Profil local et explique ce mode, sans proposer une fausse connexion. Aucun nom, e-mail, mot de passe ou jeton n’est ajouté à localStorage par cette page. Les routes et protections serveur restent inchangées.

## Mobile, clavier et thèmes

La navigation reste permanente sur ordinateur ; sous 760 px, elle devient un panneau latéral avec fond masquant. Le focus entre dans le menu à la fin de son ouverture, reste dans ses liens/boutons avec Tab, et Échap le ferme en ramenant le focus au bouton menu. La page arrière et le menu fermé sont rendus inertes selon leur état. Un lien choisi ferme le menu et active explicitement la vue demandée. Le profil actif est signalé par aria-current et les titres reçoivent le focus à la navigation.

Les thèmes jour/nuit et le mouvement réduit sont conservés. L’espace conversation garde son nuage lumineux et ses contrôles vocaux ; aucun texte supplémentaire n’est ajouté autour du nuage.

## Validation — 13 novembre 2026

34 tests Node et trois tests Python d’interface réussis ; syntaxe des scripts modifiés et diff vérifiés. Le backend fonctionnel n’a pas changé ; la dernière suite Python complète reste à 293 tests, non relancée pour cette évolution frontend. Deux avertissements de dépendances connus.

Dans une instance QA isolée : profil de démonstration, compétences présentes/absentes, modification du prénom et ajout d’un objectif, rechargement direct du profil, conservation du brouillon entre les vues et accès au compte local. Contrôles à 319/1280 px sans débordement, thèmes jour/nuit, focus du menu, cycle Tab et fermeture Échap. Sur Zephyr principal : accès au formulaire de connexion depuis le menu et page de profil hors session vérifiés ; aucun identifiant saisi ni compte personnel modifié. La capture livrée représente les données de démonstration.
