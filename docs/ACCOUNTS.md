# Comptes locaux et sessions — 0.8.0-alpha.1

## Utilisation

Dans `/ui/`, ouvrir **Se connecter → Créer un compte**. Renseigner prénom, adresse
e-mail et mot de passe de 15 à 128 caractères, puis sa confirmation. Le compte est
utilisable immédiatement. Le bouton **Mon compte** permet de se déconnecter.
Les comptes appartiennent à cette installation de Zéphyr : aucune vérification
ou réinitialisation par e-mail n’est encore disponible. Aucun e-mail n’est envoyé.

Chaque compte reçoit un profil vide. Les anciens profils anonymes restent dans
SQLite, mais un compte ne peut pas les réclamer par leur UUID depuis l’API.

## API

| Route | Fonction |
|---|---|
| `POST /api/auth/register` | Créer le compte et ouvrir une session |
| `POST /api/auth/login` | Ouvrir une nouvelle session et remplacer le cookie présenté |
| `GET /api/auth/session` | Retrouver le compte et son `learner_id` principal |
| `POST /api/auth/logout` | Révoquer la session et supprimer le cookie |

Les mutations exigent `X-Zephyr-Request: 1`. L’origine, lorsqu’elle est fournie,
doit correspondre à celle du serveur. Le marqueur est documenté dans `/docs`
avec la valeur 1. Les requêtes pédagogiques exigent aussi `X-Learner-ID` : le
serveur vérifie que ce profil appartient au compte authentifié. Un profil d’un
autre compte, ou un ancien profil non rattaché, renvoie `404`. Sans session : `401`.

Les cookies sont utilisés automatiquement par l’interface sur la même origine.
Les jetons ne sont pas renvoyés dans le JSON ni stockés dans localStorage.
Pour un script local sans mot de passe dans l’historique du shell :

```python
from getpass import getpass
import httpx

with httpx.Client(base_url="http://127.0.0.1:8001", headers={"X-Zephyr-Request": "1"}) as client:
    response = client.post("/api/auth/login", json={
        "email": input("E-mail : ").strip(), "password": getpass("Mot de passe : "),
    })
    response.raise_for_status()
    client.headers["X-Learner-ID"] = response.json()["learner_id"]
    print(client.get("/api/learner/profile").json())
```

## Stockage et sécurité

- SQLite conserve comptes, propriétaires des profils et sessions dans la même base
  que les états pédagogiques. L’inscription et son premier profil sont atomiques.
- Mots de passe : scrypt avec sel aléatoire de 16 octets, N=131072, r=8, p=1.
  La comparaison utilise `compare_digest` ; les mots de passe ne sont pas enregistrés
  en clair. Les erreurs de validation d’authentification ne recopient pas la saisie.
- Sessions opaques aléatoires de 256 bits, empreintes SHA-256 côté serveur,
  expiration absolue de 7 jours. Déconnexion et remplacement d’une session présentée
  révoquent l’ancien jeton. Une session expirée ne donne plus accès aux données.
- Cookie `HttpOnly`, `SameSite=Strict`, chemin `/`, aucun domaine explicite.
  `Secure` est activé par `AUTH_COOKIE_SECURE=true` en HTTPS.
- Mutations : en-tête dédié et contrôle de l’origine. Aucun CORS permissif ajouté.
- Limitation des tentatives, persistée dans SQLite, sur une fenêtre de 15 minutes :
  connexion 30/IP et 10/e-mail ; inscription 10/IP et 5/e-mail. Réponse `429` avec
  `Retry-After`. Deux calculs de mot de passe simultanés au maximum par processus.

Références : [stockage des mots de passe OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
et [sessions OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html).

## Configuration

`AUTH_ENABLED=true` par défaut, avec `PERSISTENCE_ENABLED=true` requis. L’ancien
mode `AUTH_ENABLED=false` est réservé aux tests et outils locaux. Il ne convient
pas à une installation exposée. Avec `APP_ENV=production`, le démarrage exige
l’authentification et `AUTH_COOKIE_SECURE=true` ; le service doit être servi en HTTPS.
Le prototype pédagogique reste limité à un processus API.

La sauvegarde SQLite existante inclut désormais les comptes et sessions.
Une restauration revient aussi à l’état des sessions à la date de cette copie ;
une maintenance peut les révoquer avant remise en service.

## Récupérer un ancien profil local

Une copie pré-authentification a été créée lors de la mise à jour du 12 novembre :
`backend/data/zephyr-before-accounts-20261112.sqlite3` (locale, ignorée par Git).

1. Créer le compte normalement et conserver une copie de la base actuelle.
2. Arrêter l’API et retrouver l’UUID du profil à récupérer dans les données locales.
3. Depuis `backend/`, avec l’environnement virtuel activé :

   ```sh
   python -m app.auth utilisateur@example.com UUID_ANCIEN_PROFIL
   ```

4. Relancer l’API et se reconnecter. Le profil récupéré devient le profil principal.

Cette commande est uniquement locale, sans endpoint public. Elle refuse un profil
qui appartient déjà à un compte et révoque les sessions du compte destinataire.
Elle ne supprime ni l’ancien profil ni le profil vide créé à l’inscription.

## Vocal continu

Après connexion, cliquer **∞ Vocal continu** et autoriser le microphone. Le cycle
est : écoute → transcription envoyée → réponse → lecture vocale → nouvelle écoute.
Le micro est libéré pendant la réflexion et la voix de Zéphyr. La dictée dépend
du navigateur et peut utiliser son service distant ; elle n’est pas garantie hors ligne.

Le mode s’arrête au second clic, sur erreur de permission/service, à l’ouverture
du profil/compte, à la déconnexion ou quand l’onglet est masqué. Il ne reprend pas
automatiquement au rechargement. La saisie texte reste disponible. La dictée est
encore configurée en français ; la prononciation des mots visuels utilise leur langue.

## Validation

273 tests Python et 7 tests Node réussis, 2 avertissements de dépendances connus.
Les tests couvrent comptes distincts, cookies, rotation/révocation/expiration,
redémarrage, transaction d’inscription, anciennes données, limitation et mutations
interdites. Trois tests du contrôleur vocal valident l’activation explicite,
l’annulation et le blocage de capture pendant un état occupé. Les formulaires ont
été inspectés sur mobile et ordinateur ; aucun compte personnel n’a été créé à
la place de l’utilisateur. La boucle avec une voix réelle reste à essayer après
création du compte et autorisation du micro.
