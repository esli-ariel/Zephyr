# Séances du plan et révisions espacées

## Utilisation

Après connexion, ouvrir **Mon parcours**. Dans **Mon profil**, renseigner langue et niveau, puis choisir **Mon plan**. Sélectionner une durée et préparer le plan ; s’il n’existe aucune recommandation, une première séance utilise le premier objectif ou « Se présenter et faire connaissance ».

**Lancer ou reprendre ma séance** prépare la première activité inachevée. Une leçon attend « J’ai terminé la lecture ». Un exercice attend votre réponse puis affiche la correction. Avec « Enchaîner les activités après validation », la suite se prépare après votre validation de lecture ou de correction. Aucune réponse n’est produite à votre place et aucune séance ne tourne en arrière-plan.

Les activités lesson/review affichent une leçon ou une notion connue. Les activités exercise/practice/correction génèrent trois exercices adaptés, avec correction locale ou IA selon leur type. Un score moyen n’est calculé qu’après toutes les corrections ; lecture et autoévaluation n’ont pas de score fictif. Les réponses attendues restent masquées avant correction.

Le contenu préparé, les réponses et le plan sont sauvegardés par apprenant. Reprendre ne régénère pas l’activité. Renvoyer la même réponse renvoie le résultat enregistré sans crédit supplémentaire ; une autre réponse pour cet exercice est refusée. Une activité en cours bloque le remplacement du plan. Un changement de langue exige un nouveau plan ; les données des autres langues sont conservées. Les erreurs fournisseur/disque ne terminent pas une activité et le middleware restaure l’état précédent.

## Révisions

Dans **Révisions**, ajouter un mot avec sa traduction ou une règle avec son explication. La carte est due immédiatement. Essayer de retrouver la réponse, cliquer **Afficher la réponse**, puis **Je l’ai retrouvé** ou **À revoir**. C’est une autoévaluation explicitement distincte d’une correction d’exercice.

| Réussites consécutives | Prochaine échéance |
|---|---|
| 1 | 1 jour |
| 2 | 3 jours |
| 3 | 7 jours |
| 4 | 14 jours |
| 5 | 30 jours |
| 6 et plus | 60 jours |
| Oubli | 10 minutes ; série remise à zéro |

Les échéances utilisent UTC côté serveur et s’affichent dans l’heure du navigateur. Le calendrier est simple et déterministe ; la maîtrise reste le taux de bonnes réponses historique. Les corrections d’exercices explicitement liés à un mot/règle actualisent aussi ce calendrier. Les anciennes notions sans calendrier sont dues immédiatement. Une carte déjà notée ou révisée ailleurs est refusée avec 409 ; recharger les échéances. La liste porte sur la langue du profil, affiche au plus 50 cartes dues à la fois et annonce la prochaine échéance. Aucun rappel système, e-mail ou tâche de fond n’est créé.

## API

Toutes ces routes gardent authentification, propriété du profil, `X-Learner-ID`, garde de mutation et sauvegarde atomique habituelles.

| Route | Fonction |
|---|---|
| POST `/api/learning/plan/generate` | Plan personnalisé ; limit et available_minutes |
| POST `/api/learning/plan/next` | Préparer/reprendre la première activité inachevée |
| GET `/api/learning/plan/items/{id}/activity` | Lire sans nouvelle génération |
| POST `/api/learning/plan/items/{id}/read` | Lecture terminée, ou révision avec correct booléen |
| POST `/api/learning/plan/items/{id}/answer` | exercise_id + answer ; correction idempotente |
| GET `/api/learning/reviews/due` | Cartes dues et prochaine échéance, sans corrigés |
| POST `/api/learning/reviews/reveal` | category + target + review_count ; révéler une carte |
| POST `/api/learning/reviews/grade` | Même référence + correct booléen ; notation unique |

L’ancien GET `/plan` reste compatible, avec protection contre le remplacement d’une activité commencée. L’ancien endpoint de complétion manuelle ne peut pas forcer le score d’une activité exécutée par ce parcours. Les anciens endpoints de listes de révision restent fondés sur la maîtrise ; `/reviews/due` fournit le calendrier temporel.

`ReviewSchedule` est sauvegardé dans les objets vocabulaire/grammaire, avec valeurs par défaut compatibles avec les anciens snapshots. Les données d’exécution restent dans les métadonnées des activités. SQLite et le verrou par apprenant conservent le modèle à un processus API.

## Validation — 13 novembre 2026

Suite complète : **287 tests Python et 27 tests Node réussis**, deux avertissements de dépendances existants. Les 13 nouveaux tests pédagogiques couvrent échéances, reprise disque, anciens snapshots, erreurs fournisseur/disque, absence de double crédit, score calculé, isolement, authentification et changement de langue. Quatre nouveaux tests Node couvrent le cycle de vie caméra.

Navigateur : séance complète avec contenus simulés sur une base de QA isolée, rechargement après la première réponse puis reprise au deuxième exercice, 2/2 activités terminées avec 66,67/100 pour les exercices, ajout/révélation/notation d’une carte et échéance le lendemain. Aucun compte personnel ni appel IA réel créé par ces essais. Contrôles à 319 et 1280 px sans débordement. La génération/correction réelle utilise toujours le fournisseur OpenRouter configuré ; son contenu n’a pas été évalué dans cette session.

## Extension du 13 novembre : quotidien et oral

L’accueil Aujourd’hui lit les échéances et le plan courant ; l’accès Ma séance reste compact. Les exercices du plan proposent désormais la dictée modifiable, le report explicite puis la correction. Les textes libres et QCM sont pris en charge ; l’évaluation de niveau garde ses contrôles précédents. [Guide DAILY_SESSION](DAILY_SESSION.md). Référence actuelle : 293 Python et 34 Node ; voix réelle restante.
