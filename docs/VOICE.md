# Voix et transcription

Dans `/ui/`, ouvrir **Réglages vocaux ⚙**, près du microphone. La conversation nécessite une connexion ; les réglages, l’exemple vocal et le diagnostic sont accessibles avant connexion.

## Réglages par défaut

| Paramètre | Valeur |
|---|---|
| Langue de transcription | Français (`fr-FR`) |
| Langue de lecture | Français (`fr-FR`) |
| Voix | Recommandée du navigateur, priorité à une voix locale de la langue |
| Vitesse / tonalité / volume | 0,95× / 1 / 100 % |
| Pause avant finalisation | 1,6 seconde |
| Envoi automatique | Activé pour une transcription confirmée sans erreur |

Dictée et lecture se règlent indépendamment : français, anglais britannique ou américain, espagnol, allemand, italien et portugais brésilien. L’option « langue étudiée » suit le profil ; un profil absent/non reconnu indique explicitement le repli français. La langue de lecture change la prononciation, sans traduire le message.

Les voix sont celles réellement proposées par l’appareil et son navigateur ; la liste se met à jour quand elles deviennent disponibles. Un choix est mémorisé par langue. Écouter un exemple puis l’arrêter permet de vérifier volume, débit et voix sans appel IA.

## Transcription et conversation

Cliquer le micro, autoriser son accès dans le navigateur et parler dans la langue choisie. Le panneau distingue les mots confirmés et provisoires ; les résultats révisés remplacent le texte précédent sans le dupliquer. La pause réglable de 0,9 à 3,5 secondes demande une finalisation ; le navigateur peut terminer l’écoute plus tôt.

Un second clic termine l’écoute en attendant les derniers mots confirmés. Le microphone est ensuite libéré. Une annulation ou une erreur conserve le texte reçu pour relecture. Aucun mot provisoire ni résultat en erreur n’est envoyé automatiquement. Le brouillon déjà tapé reste conservé.

Désactiver « Envoyer automatiquement » pour modifier la transcription dans la saisie, puis **Envoyer la dictée** ou **Effacer**. Le vocal continu attend cette validation ; il attend aussi la fin de la lecture avant de réécouter. Il reste volontaire, s’arrête en arrière-plan/sur erreur et ne reprend pas au chargement. Ouvrir les réglages suspend la conversation vocale.

La lecture des longues réponses est découpée ; un garde-fou arrête une synthèse bloquée. Les événements tardifs après arrêt ne relancent ni dictée ni lecture. La visualisation suit le volume capté ; la voix synthétique utilise toujours une animation, sans analyse PCM.

## Diagnostic et confidentialité

**Tester mon micro** mesure seulement le niveau et affiche le microphone obtenu par le navigateur, sans transcription ni envoi de son à Zephyr. Arrêter le test, fermer le dialogue ou masquer l’onglet libère le flux ; un test démarré s’arrête automatiquement après 30 secondes. Une demande d’autorisation annulée ne laisse pas le micro actif si elle aboutit plus tard.

Pour changer d’entrée, utiliser les paramètres du navigateur/système. Le flux d’analyse et la reconnaissance native ne permettent pas de garantir un même périphérique choisi par l’application ; aucun sélecteur trompeur n’est proposé.

Seules les préférences vocales sont mémorisées dans `localStorage` (`zephyr.voicePreferences`), sans audio, transcription ou identifiant dans cette clé. Les messages envoyés suivent la persistance habituelle du chat. La reconnaissance peut utiliser un service distant du navigateur ; fonctionnement hors ligne et disponibilité non garantis.

## Validation du 12 novembre 2026

23 tests Node réussis : résultats révisés, brouillon, mots provisoires, erreurs, permissions tardives, libération des pistes, arrêt/finalisation, découpage et blocage de synthèse, contrôleur continu et vocabulaire 3D. Trois tests Python d’interface réussis ; deux avertissements de dépendances connus. La suite Python complète précédente comptait 274 tests, non relancée pour ce changement frontend.

Dans le navigateur : lecture d’exemple déclenchée, sauvegarde après rechargement vérifiée, valeurs par défaut rétablies, absence de débordement à 319 px. Le diagnostic réel attend l’autorisation micro ; aucune phrase parlée ni boucle acoustique complète n’a été validée. B008/B016 restent ouverts.

Références des API : [arrêt avec résultat final](https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition/stop), [résultats provisoires](https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition/interimResults), [résultat confirmé](https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognitionResult/isFinal), [synthèse native](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis).
