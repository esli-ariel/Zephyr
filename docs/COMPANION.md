# Caméra locale et avatar

Ouvrir **Caméra**, près du microphone. Le panneau est indépendant de l’authentification : l’exemple vocal fonctionne avant connexion ; la conversation personnelle nécessite votre compte.

Choisir **Avatar humanoïde** ou **Points** sous la scène principale. Le buste 3D stylisé suit les états repos, écoute, réflexion et parole ; la bouche suit une enveloppe de synthèse, sans synchronisation phonétique. Repli SVG sans WebGL 2, thèmes et mouvement réduit conservés. Le choix est mémorisé et n’active pas la caméra. Voir [PRESENCE.md](PRESENCE.md).

**Activer ma caméra** demande une entrée vidéo seule (`audio: false`), affiche un aperçu local en miroir puis permet l’arrêt. La caméra ne démarre pas à l’ouverture du panneau ou au chargement. L’activation en attente reste annulable. Masquer le panneau, ouvrir un dialogue de compte/parcours/réglages, passer en arrière-plan ou quitter libère les pistes. Une autorisation accordée après annulation libère immédiatement le flux tardif. Déconnexion matérielle et erreurs de permission sont signalées.

Aucune image n’est enregistrée, capturée ou transmise au backend, à OpenRouter ou à un service vidéo. Aucun flux caméra n’est mémorisé. Le choix du périphérique et ses autorisations se règlent dans le navigateur. La synthèse et la dictée conservent leurs réglages : [VOICE.md](VOICE.md).

Validation : quatre tests Node du contrôleur (opt-in, vidéo sans audio, libération, permission tardive, refus et déconnexion). Dans le navigateur, état speaking de l’avatar observé avec la synthèse native, puis retour au repos ; demande caméra annulée et absence de flux confirmée. La caméra réelle reste à autoriser et vérifier par l’utilisateur. Un arrêt par le garde-fou de synthèse a été observé dans l’environnement de contrôle ; la qualité audio et la boucle parlée ne sont pas déclarées validées. Interface à 319/1280 px sans débordement. Zephyr local relancé sur 8001 avec les comptes et la base existants ; instance de QA séparée arrêtée.

API de référence : [getTracks](https://developer.mozilla.org/en-US/docs/Web/API/MediaStream/getTracks), [MediaStreamTrack.stop](https://developer.mozilla.org/en-US/docs/Web/API/MediaStreamTrack/stop).
