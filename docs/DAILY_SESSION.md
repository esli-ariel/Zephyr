# Séance du jour et exercices à l’oral

## Direction conservée

Cette étape poursuit la ligne du projet : nuage de points lumineux et objets 3D, conversation immersive, voix centrale et interface discrète. La carte d’accueil est placée dans le panneau de conversation ; ses détails disparaissent pendant la conversation. Aucun tableau de bord massif ni texte supplémentaire autour du nuage. Thèmes jour/nuit, particules, caméra locale et avatar restent compatibles.

Le périmètre réalisé est la première priorité proposée : exercices à l’oral et séance du jour. Les jeux de rôle guidés, le vocabulaire ajouté depuis une sélection du chat et l’analyse volontaire d’une image restent des étapes distinctes.

## Ma séance du jour

Après connexion, **Ma séance ↗** ouvre directement **Mon parcours → Aujourd’hui**. Ce nouvel onglet est aussi l’accueil par défaut du parcours. Il présente :

- les révisions dues dans la langue du profil et un accès direct à la première carte ;
- sinon, la prochaine activité et sa reprise si elle a déjà commencé ;
- le nombre d’activités du plan courant terminées aujourd’hui ;
- le nombre de notions distinctes de la bibliothèque actuelle révisées aujourd’hui ;
- la progression du plan courant, le temps estimé restant et la prochaine échéance connue.

Ces chiffres sont lus dans les données existantes, sans générer de plan, corriger une réponse ni attribuer du progrès. Un changement de langue signale un plan périmé et invite à en préparer un nouveau. Un profil incomplet renvoie au formulaire. Le jour suit le décalage horaire envoyé par le navigateur ; les dates persistées restent en UTC. Les compteurs ne sont pas un historique global de toutes les séances : remplacer un plan remplace le périmètre de son compteur d’activités.

La carte se rafraîchit à la connexion, à la fermeture du parcours et au retour dans l’onglet. Aucun minuteur de rappel ou tâche système n’est créé.

API : `GET /api/learning/today?utc_offset_minutes=0`, décalage signé de −840 à +840 minutes, authentification et propriété du profil habituelles, réponse no-store. Le résumé est en lecture seule.

## Répondre à l’oral

Dans un exercice du plan, choisir **Répondre à l’oral**. La langue parlée suit initialement la langue reconnue du profil ; elle reste modifiable. Pour une langue non prise en charge, le choix est explicite et aucun repli silencieux n’active le micro.

1. Autoriser le micro puis dicter. Le point d’activité et le nuage suivent l’écoute ; les mots provisoires sont signalés.
2. Terminer l’écoute et attendre la finalisation, ou arrêter/annuler. Le moteur libère les pistes ; les mots reçus restent à relire.
3. Modifier **Votre dictée à relire**, puis choisir **Utiliser cette réponse**.
4. Vérifier la saisie ou l’option sélectionnée, puis cliquer **Corriger ma réponse**.

L’envoi automatique du chat ne s’applique jamais à un exercice. Un brouillon dicté ne remplace pas la saisie avant le clic explicite ; la correction ne démarre pas au clic « Utiliser ». Pour un QCM, une seule option doit correspondre exactement, hors casse et ponctuation terminale. Une phrase approximative n’est pas interprétée comme une réponse : corriger le brouillon ou utiliser la liste.

**Écouter la question** permet la répétition ; **Plus lentement** applique un débit réduit avec les limites des réglages existants. L’arrêt reste accessible. Lecture et capture ne se chevauchent pas. Les autres commandes du parcours sont bloquées pendant l’écoute/lecture ; fermer le dialogue reste possible et arrête le vocal. Changer d’écran, passer en arrière-plan ou quitter neutralise les événements tardifs.

La dictée peut utiliser le service distant du navigateur. Aucun audio n’est ajouté à la base ni à localStorage. Seul le texte explicitement envoyé suit la correction et la persistance habituelles. La correction évalue le texte, sans note de prononciation. L’évaluation de niveau conserve son fonctionnement antérieur ; les contrôles oraux ajoutés ici concernent les exercices du plan.

## Architecture et validation — 13 novembre 2026

`daily_session.py` produit un résumé déterministe de l’état ; `oral-answer.js` réutilise le moteur vocal existant dans une session de brouillon séparée du chat. Le parcours transmet les états et le volume au nuage/avatar, sans activer le vocal continu. Les anciens endpoints de correction ne changent pas.

**293 tests Python et 34 tests Node réussis**, deux avertissements de dépendances existants. Six nouveaux tests Python : résumé vide, compteurs réels, limites de journée locale, langue périmée, isolation/no-mutation et authentification. Sept nouveaux tests Node : validation explicite, QCM exact, mots incertains/erreurs, annulation/événements tardifs, langue absente, longueur et lecture sans envoi.

Navigateur : instance QA distincte, dictée et contenus pédagogiques simulés, sans microphone ni fournisseur réel. Brouillon « Hello » non reporté automatiquement, modification puis report explicite, correction séparée, reprise au deuxième exercice, priorité aux révisions dues, état compact pendant la conversation, affichage 319/1280 px sans débordement. Les captures de cette étape représentent ces données de démonstration. Zephyr principal relancé sur 8001 avec authentification conservée ; QA arrêtée après vérification.

La dictée matérielle, les permissions utilisateur et la qualité sonore restent à valider avec une voix réelle (B008/B016). Les essais simulés ne valident ni la prononciation ni un moteur vocal temps réel externe.
