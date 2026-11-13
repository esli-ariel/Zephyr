# Points ouverts — Zéphyr

Mise à jour : 12 novembre 2026 — backend 0.8.0-alpha.1.

Les points ouverts ci-dessous comprennent des défauts, limites techniques et
travaux restants. « Résolu » concerne le périmètre indiqué, sans préjuger d’une
validation en production.

| ID | Point | État / prochaine action |
|---|---|---|
| B001 | Agent et évaluation partagés entre clients | Résolu en V0.7.1 : instances et sauvegardes distinctes par identifiant |
| B002 | Données perdues au redémarrage | Résolu en V0.7.0 : SQLite et copie de sauvegarde |
| B003 | Exercice sans lien explicite vers un mot ou une règle | Résolu en V0.7.2 : lien serveur facultatif et maîtrise actualisée après correction |
| B004 | Résultats LLM peu strictement validés | Résolu en V0.7.2 : schémas stricts et erreur 502 sans progrès enregistré |
| B005 | Deux avertissements Starlette/httpx/AnyIO dans les tests | Ouvert : migration des dépendances de test à traiter séparément |
| B006 | Identifiant de sélection sans authentification | Traité : comptes, sessions et propriété des profils en 0.8.0-alpha.1 |
| B007 | Verrous locaux au processus | Ouvert : coordination nécessaire avant plusieurs workers |

## Corrigés en V0.6.9

- Réponse attendue exposée par l’API de génération d’exercices : sérialisation publique sans corrigé.
- Priorité d’activité calculée mais ignorée par le tri du plan : tri corrigé.
- Routes absentes pour la correction d’exercices, la grammaire et l’autoévaluation du vocabulaire : ajoutées.
- Dépendances pytest absentes du dépôt : `backend/requirements-dev.txt` ajouté.

## Corrigés en V0.7.0

- Plan actif non initialisé par le moteur : initialisation, mémorisation et reprise après redémarrage.
- Sauvegarde transactionnelle et annulation des modifications en cas d’échec d’écriture.

## Corrigés en V0.7.1

- Les requêtes pédagogiques exigent un identifiant explicite et refusent les identifiants inconnus.
- Profil, conversation, contenus, vocabulaire, grammaire, plan et évaluation séparés par apprenant.
- Sauvegarde, annulation et verrou limités à l’apprenant sélectionné.
- Migration atomique de l’ancienne base sans duplication du profil dans les nouveaux apprenants.

## Validation de référence — V0.7.2

Dernière suite exécutée pour le code : `python -m pytest -q` → **258 réussis,
2 avertissements de dépendances**. Les tests de séparation/migration/concurrence
sont dans `backend/tests/test_learners.py` ; ceux de restauration et rollback dans
`backend/tests/test_persistence.py`. Les appels OpenRouter sont simulés.

B003 et B004 sont résolus pour les liens explicites et la validation du format.
La qualité pédagogique réelle reste non vérifiée. B006 doit être traité avant
une ouverture publique ; B007 avant le passage à plusieurs processus API.
Les décisions associées sont consignées dans ADR-005 et ADR-007 à ADR-012
([DECISIONS.md](DECISIONS.md)).

## Corrigés en V0.7.2

- Chaînes `"false"`, scores hors bornes et listes invalides auparavant convertis silencieusement : rejetés.
- Erreur d’évaluation ouverte auparavant transformée en score zéro : `502` et annulation de la mutation.
- Générations incomplètes, QCM invalides et profils mal formés : refusés avant enregistrement.
- Identifiants d’exercices fournis par le modèle : remplacés par des UUID serveur pour éviter les collisions.
- Exercices liés à une notion existante : mise à jour des compteurs et de la maîtrise après correction.
- Réponse fournisseur brute dans les erreurs : remplacée par un message contrôlé.

Validation dédiée : `backend/tests/test_llm_validation.py` et
`backend/tests/test_exercise_targets.py`. Les anciennes sauvegardes d’exercices
sans lien restent compatibles.

## Interface — 12 novembre 2026

| ID | Point | État / prochaine action |
|---|---|---|
| B008 | Compatibilité de la dictée et autorisations micro | Ouvert : tester avec l’utilisateur ; repli texte intégré |
| B009 | Animation de sortie sans analyse du son synthétisé | Limite connue : enveloppe et événements de lecture ; accès audio nécessaire pour synchronisation exacte |
| B010 | Écrans pédagogiques absents de l’interface | Ouvert : profil, évaluation, plan, exercices, correction |
| B011 | Reconnaissance et synthèse fixées en français | Traité : langues séparées, option profil, choix de voix ; validation acoustique réelle restante |

Débordement horizontal à 319 px corrigé ; document et viewport de largeur identique
après correction. Test visuel ordinateur à 1440 × 960. Chat réel OpenRouter réussi.
La synthèse a déclenché l’état de parole ; la qualité sonore et la dictée réelle
restent à tester avec l’utilisateur. 261 tests réussis, 2 avertissements existants.

## Ajustement visuel — 12 novembre 2026

- Textes d’introduction/légendes persistants près de la sphère : masqués dès la conversation, y compris après restauration.
- Animation peu marquée : amplitude, ondulations, rotation et dimension renforcées.
- Interaction ajoutée par pointeur, clic/toucher et clavier ; messages d’erreur déplacés dans la conversation pour rester visibles.
- Aucun débordement observé à 319 ou 1440 px ; aucune erreur console observée.
- B008/B009/B011 restent ouverts : cette modification n’ajoute ni validation réelle du micro ni analyse PCM de la voix synthétisée.

## Particules et thèmes — 12 novembre 2026

- Modes clair/sombre ajoutés avec contraste des particules adapté au fond.
- Sélecteur visible sur petit écran (icône à 319 px) et sur ordinateur (icône et texte).
- Choix mémorisé après rechargement ; repli en session si le stockage est indisponible.
- Mouvement réduit respecté : les détachements et dérives automatiques sont suspendus.
- Les limites micro/dictée et animation de synthèse (B008/B009/B011) restent inchangées.

## Halo et relief — 12 novembre 2026

Halo et profondeur renforcés sans ajouter de particules ni appliquer un filtre de
flou à chaque point. Transitions entre réflexion et synthèse contrôlées avec un
échange réel ; aucun message d’erreur console observé. Les limites B008/B009/B011
restent ouvertes : écoute réelle non validée dans cet ajustement, synthèse animée
sans mesure PCM, reconnaissance et lecture toujours en français.

## Nuage libre et objets 3D — 12 novembre 2026

| ID | Point | État |
|---|---|---|
| B012 | Couverture des traductions d’objets | Six objets et six langues hors ligne ; langues inconnues signalées. Élargissement restant. |
| B013 | Objets plats et points ternes dans l’ébauche | Corrigé : surfaces en volume, rotation Y/X, lumière/opacité et accents renforcés. |

Le sélecteur « Mots en images » sauvegarde la langue cible du profil. Un échec
d’enregistrement reste signalé comme aperçu local. La prononciation des mots
utilise la langue sélectionnée ; B011 reste ouvert pour la dictée et la lecture
des réponses du chat encore en français. B008/B009 restent ouverts pour le micro
réel et l’absence d’analyse PCM de la voix synthétisée.

L’objet est un support visuel de vocabulaire et ne crédite pas automatiquement la
maîtrise. La suite backend de référence reste de 261 tests ; validation ciblée de
cette évolution : 3 tests Python interface et 4 tests Node réussis.

## Profil et évaluation dans l’interface — 12 novembre 2026

- B010 partiellement traité : profil et évaluation disponibles ; plan, exercices et correction visuels restent à intégrer.
- B014 : banque d’évaluation en anglais uniquement. L’interface bloque le démarrage et la poursuite pour un profil d’une autre langue ; étendre la banque reste à faire.
- En cas de réponse réseau perdue, la question serveur est relue avant de permettre une nouvelle soumission. Si cette lecture échoue, la reprise est requise.
- Le niveau déclaré vide ne supprime pas un niveau existant : limite du contrat API, signalée dans l’interface.
- Tests locaux : 263 Python et 4 Node réussis. Les deux avertissements de dépendances restent ouverts (B005).
- Authentification, plusieurs workers, micro réel et analyse PCM restent hors périmètre de cette étape.

## Comptes et vocal continu — 0.8.0-alpha.1

- B006 traité : cookie de compte requis et propriété des profils vérifiée par l’API.
- B015 ouvert : pas encore de confirmation e-mail, récupération de mot de passe ou MFA. Comptes locaux à l’installation.
- B016 ouvert : boucle vocale avec une voix réelle à valider ; les tests actuels couvrent le contrôleur et les arrêts.
- Les anciennes données restent sauvegardées sans rattachement automatique. La procédure locale est dans ACCOUNTS.
- B007 reste ouvert : apprentissage limité à un processus. Les avertissements B005 et la limitation de dictée française B011 restent ouverts.
- 273 tests Python et 7 Node réussis ; UI 319/1100 px sans débordement.

## Ajustement de l’inscription — 12 novembre 2026

- Ancien minimum de 15 caractères remplacé par huit à la demande de l’utilisateur, dans l’API et le formulaire.
- Message de validation et guide de compte synchronisés ; test de limite 7/8 et connexion ajoutés.
- Champs de mot de passe vidés à la fermeture même après affichage en clair.
- Nouvelle interface mobile/ordinateur contrôlée sans débordement horizontal.

## Réglages vocaux — 12 novembre 2026

B011 traité : langues de dictée/lecture configurables et choix de voix. Les mentions françaises précédentes décrivent les versions antérieures. Arrêt prématuré et duplication des résultats couverts par les nouveaux tests. B008/B016 restent ouverts : autorisation micro et essai parlé réels nécessaires. B009 (absence de PCM synthèse), B005 et B007 inchangés. 23 tests Node et 3 Python interface réussis ; exemple natif/persistance vérifiés.

## Parcours et présence vocale — 13 novembre 2026

- B010 : parcours profil → niveau → plan → exercice → correction désormais intégré, avec révisions espacées. Les listes historiques décrivent les étapes précédentes.
- Compatibilité des anciennes sauvegardes, reprise et rollback vérifiés ; 287 Python et 27 Node réussis. B005 (deux avertissements) et B007 (un processus) restent ouverts.
- B008/B016 : parole réelle et boucle micro/réponse à valider après permission. État speaking de l’avatar observé ; garde-fou de synthèse déclenché dans l’environnement de QA, qualité sonore non déclarée validée.
- Caméra locale implémentée, refus/annulation/libération testés ; aperçu matériel réel restant à autoriser/vérifier. Avatar de présence, sans synchronisation phonétique ni rendu vidéo réaliste.
- Qualité pédagogique des nouvelles séances vérifiée par contrats/tests simulés ; essai fournisseur réel encore à effectuer. B014/B015 (autres langues d’évaluation et récupération de compte) inchangés.

## Séance du jour et réponses orales — 13 novembre 2026

- Exercices du plan accessibles par dictée modifiable ; report et correction explicitement séparés, mots incertains jamais envoyés automatiquement. Langue inconnue sans repli implicite ; QCM sans réponse inférée.
- Résumé quotidien isolé en lecture seule, compteurs du plan courant et des notions distinctes ; changement de langue et fuseau local couverts.
- 293 Python et 34 Node réussis ; dictée/contenus simulés en QA navigateur, 319/1280 px sans débordement. B008/B016 (matériel vocal réel), B009 (PCM synthèse), B005/B007/B014/B015 restent ouverts.
- Étapes suivantes : mises en situation guidées, ajout d’un mot sélectionné dans le chat, analyse d’image sur action volontaire ; ni vision ni synchronisation phonétique revendiquées dans cette étape.
