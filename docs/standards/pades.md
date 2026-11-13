# PAdES : la signature PDF visée par DZ Sign

Amel importe une attestation fictive, la signe et télécharge un PDF. Le résultat doit pouvoir être transmis comme un document unique, avec sa signature intégrée. C’est le parcours retenu dans le [cadrage](../introduction/project-scope.md).

L’application produit des copies signées et vise PAdES-B-B. Cette fiche décrit le profil retenu et les limites de la vérification de conformité. Source consultée le **11 novembre 2026** : [ETSI EN 319 142-1 V1.2.1, janvier 2024](https://www.etsi.org/deliver/etsi_en/319100_319199/31914201/01.02.01_60/en_31914201v010201p.pdf), sections 5 et 6.

## Ce que contient une signature PAdES

La signature utilise un dictionnaire PDF et une structure CMS. `ByteRange` indique les plages d’octets couvertes ; `Contents` contient la valeur de signature. La couverture concerne la révision signée, en excluant l’emplacement réservé à cette valeur. L’apparence visible d’une signature ne suffit pas à vérifier son intégrité.

Les niveaux baseline peuvent être résumés ainsi :

| Niveau | Objectif |
|---|---|
| B-B | Signature de base répondant aux exigences du profil |
| B-T | Ajout d’une preuve temporelle d’existence de la signature |
| B-LT | Incorporation des éléments nécessaires à la validation |
| B-LTA | Protection temporelle supplémentaire pour prolonger la disponibilité et l’intégrité des preuves |

Ce résumé ne remplace pas les exigences du tableau 1 de la norme. La conservation exige un suivi des preuves et des technologies ; un niveau LTA n’assure pas une validité perpétuelle.

## Objectif retenu : PAdES-B-B

La première version visera **PAdES-B-B**, avec un certificat de test. Aucun service d’horodatage de confiance n’étant prévu dans ce parcours, nous n’annoncerons pas les niveaux supérieurs. Ce choix devra être confirmé avec la bibliothèque retenue, sa version et les paramètres de signature.

Avant d’annoncer une conformité, nous devrons :

- Vérifier les champs et attributs exigés par l’édition de référence.
- Générer des fichiers d’essai reproductibles.
- Contrôler leur structure et les résultats avec un outil indépendant, dont la version et la configuration seront consignées.
- Documenter les écarts et les cas non pris en charge.

Le certificat ne sera jamais présenté comme qualifié au seul motif que le fichier respecte un profil PAdES.

## Lire les modifications après signature

Le rapport DZ Sign devra identifier la révision couverte et examiner les changements ultérieurs. Nous voulons éviter de confondre « signature correcte sur une ancienne révision » et « document actuel intégralement approuvé ».

Voici les scénarios à préparer lors de l’implémentation :

| Fichier d’essai | Comportement attendu du rapport |
|---|---|
| PDF signé sans changement ultérieur | Présenter couverture, intégrité et validation du certificat séparément |
| Octets couverts altérés | Signaler l’échec du contrôle cryptographique si celui-ci est réalisable |
| Révision ajoutée après signature | Identifier le changement et son analyse ; ne pas conclure à partir du seul calcul cryptographique |
| Plusieurs signatures | Présenter chaque signature et sa couverture ; signaler les limites d’analyse |
| Image de signature sans signature cryptographique | Indiquer qu’aucune signature cryptographique n’a été trouvée |
| PDF illisible ou structure non prise en charge | Indiquer que la vérification n’a pas pu être menée |

Les tests de signature et de vérification couvrent notamment les documents intacts, altérés et les révisions ultérieures. La revue des permissions et de la conformité au profil reste distincte de ces contrôles ; elle ne doit pas être déduite de leur réussite.

## Prochaine décision technique

L’architecture devra fixer les responsabilités entre interface, API, moteur de signature et stockage temporaire. Les choix d’algorithmes et de gestion des clés seront consignés avant les exemples exécutables. Les notions de confiance et de preuve temporelle sont expliquées dans les fiches [PKI](../cryptography/pki.md) et [vérification](../cryptography/signature-validation.md).
