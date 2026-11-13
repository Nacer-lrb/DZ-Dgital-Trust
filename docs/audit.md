# Audit de qualité du projet

Date : 13 novembre 2026. Périmètre : code applicatif, exemples, tests, interface, dépendances déclarées et documentation du projet. Les paquets tiers et les données privées sous `.local/` ne sont pas réécrits.

## Historique

Le dossier `.git` racine a été supprimé à la demande du propriétaire. Aucun nouvel historique n’a été initialisé. Les règles `.gitignore` restent disponibles pour une éventuelle initialisation ultérieure.

## Constats et corrections

| Constat | Correction |
|---|---|
| Licence et guide de contribution vides | Texte MIT conforme au choix déjà annoncé, mentions tierces et consignes de contribution ajoutés |
| Technologies non présentes annoncées dans le README | Description limitée à Next.js/React/TypeScript, FastAPI et pyHanko réellement utilisés |
| Deux fiches d’introduction vides | Présentation de la signature et du cachet, avec distinction entre notions et fonctions disponibles |
| Documents mêlant projet initial et version actuelle | Cadrage réécrit, descriptions de statut corrigées et navigation des manuels centralisée |
| Documentation de fonctionnement uniquement en français | Sept chapitres équivalents par langue : français, anglais et arabe, avec marqueurs RTL/LTR |
| Gestion des sous-processus répétée | Protocole JSON commun, sortie bornée et rejet explicite des sorties invalides |
| Validation partielle des réponses frontend | Contrats séparés du transport, contrôle des dates, tailles, identifiants et rapports |
| Appel à une API navigateur plus récente que nécessaire | Propagation de l’annulation par écouteur standard, avec nettoyage |
| Métadonnées retirées avant suppression effective du fichier | Suppression des références après nettoyage du stockage, avec reprise possible en cas d’erreur |
| JSX compact, styles répétés et règles devenues inutilisées | Formatage reproductible, consolidation des règles et suppression des styles morts |
| Tests PDF dépendants d’un ordre d’import implicite | Chargement explicite de la fixture PKI, indépendant du tri des imports |
| Éléments d’interface sans fonction propre | Retrait du compteur décoratif de l’état vide, des numéros de navigation et d’un texte explicatif répété |

Les messages `TEST ONLY`, les limites de vérification et les références de framework sont conservés pour leur fonction : distinguer une identité fictive, expliquer la portée du rapport et permettre la compilation.

## Documentation livrée

Les [manuels](README.md) couvrent installation, usage, architecture/API, sécurité, fondements techniques, cadre documentaire juridique et développement. Les commandes d’installation et de contrôle sont vérifiées entre les trois langues. Les études longues d’origine restent identifiées comme références en français ; elles ne sont pas présentées comme des traductions officielles.

Les sources juridiques principales ont été rapprochées des publications officielles. La revue ne certifie ni une conformité réglementaire exhaustive ni l’état opérationnel actuel de chaque institution.

## Validation et limites

`python3 scripts/check.py` rassemble les contrôles de documentation, Ruff, les tests Python, les tests de contrats frontend, le formatage, TypeScript et la compilation Next.js. Les essais cryptographiques indépendants nécessitent OpenSSL.

Validation exécutée : 51 tests Python et cinq tests frontend réussis, sans omission ; Ruff, formatage, TypeScript et build Next.js réussis. Le contrôle documentaire couvre 46 fichiers Markdown, les liens locaux, les sept chapitres dans chacune des trois langues et la cohérence des commandes communes.

La revue concerne une application locale mono-utilisateur. Elle n’est pas un test d’intrusion ni un audit de qualification de service de confiance. L’absence d’authentification, de stockage durable, de vérification de révocation et d’horodatage reste un choix de périmètre documenté. Une mise en service partagée ou publique demanderait une revue distincte.
