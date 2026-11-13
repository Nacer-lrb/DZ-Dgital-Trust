# Du fichier à la vérification d’une signature

Quand DZ Sign affiche le résultat d’une vérification, que doit-on comprendre ? Quatre mécanismes se complètent : le hachage résume les données, la signature permet de vérifier leur lien avec une clé, l’horodatage apporte une preuve temporelle et la révocation renseigne sur le statut du certificat.

Cette fiche prolonge la [présentation de la PKI](pki.md). Les exemples décrivent le comportement attendu du futur prototype. Sources consultées le **11 novembre 2026** : [registre des références](../../resources/references.md).

## Hacher : calculer l’empreinte des données

SHA-256 produit une empreinte de 256 bits, soit 32 octets, généralement représentée par 64 caractères hexadécimaux. Le calcul porte sur les octets exacts du fichier. Deux PDF visuellement identiques peuvent donc avoir des empreintes différentes.

Des empreintes différentes établissent que les données diffèrent. Des empreintes identiques constituent un indicateur d’intégrité fondé sur la résistance de la fonction aux collisions ; ce n’est pas une preuve mathématique d’unicité. L’empreinte ne chiffre pas le document et n’identifie pas son auteur. Il faut disposer d’une référence fiable pour qu’une comparaison soit utile. SHA-256 est défini dans le [FIPS 180-4, notamment section 6.2](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf).

Dans DZ Sign, l’empreinte affichée à l’import concernera le fichier complet reçu. Après signature, le fichier téléchargé aura sa propre empreinte. Le guide devra identifier clairement le fichier auquel chaque valeur correspond.

## Signer : utiliser une clé privée

Dans CMS, la structure `SignedData` peut réunir des informations de signature, des certificats et des éléments de révocation. Lorsque des attributs signés sont présents, l’attribut `message-digest` contient l’empreinte du contenu ; la signature porte sur l’encodage des attributs signés. Décrire cela comme un simple « chiffrement de l’empreinte avec la clé privée » serait trompeur : le traitement dépend du schéma de signature.

Le vérificateur recalcule les valeurs nécessaires et vérifie la signature avec la clé publique. Il doit aussi valider le certificat selon sa politique. La date `signingTime`, lorsqu’elle est présente, est une date déclarée par le signataire ; elle n’apporte pas une preuve indépendante de l’instant de signature. Voir la [RFC 5652, sections 5 et 11](https://www.rfc-editor.org/rfc/rfc5652).

Pour notre parcours, Amel signera une attestation fictive avec sa clé de test. L’interface devra expliquer l’intégrité de la signature séparément de la confiance accordée au certificat. L’analyse des révisions PDF et des données couvertes sera précisée dans la fiche PAdES avant l’implémentation.

## Horodater : ajouter une preuve temporelle

Une autorité d’horodatage, ou TSA, reçoit une empreinte et produit un jeton signé qui associe cette empreinte à un instant. Le protocole n’exige pas l’envoi du document complet. La vérification doit notamment contrôler la correspondance de l’empreinte, la signature du jeton et le certificat de la TSA selon la politique retenue. Voir la [RFC 3161, sections 2.1 à 2.4](https://www.rfc-editor.org/rfc/rfc3161).

Un jeton valide apporte une preuve d’existence des données correspondantes au moment indiqué, sous les hypothèses de confiance de la TSA. Il ne prouve pas à lui seul que le contenu du document est vrai. Il faut aussi préciser ce qui est horodaté : le document ou une valeur de signature, par exemple.

La première version de DZ Sign n’intégrera pas de service d’horodatage de confiance. Le rapport affichera cette absence. Un futur service de test devra être explicitement identifié comme tel, sans assimiler le respect du protocole à une qualification juridique.

## Révoquer : publier un changement de statut

Un certificat peut être révoqué avant son expiration, notamment après une compromission de clé. Le certificat déjà émis n’est pas réécrit : le statut est publié séparément.

Une **CRL** est une liste signée. Avant d’utiliser son contenu, il faut vérifier son émetteur, sa signature, sa portée et ses dates, notamment `thisUpdate` et `nextUpdate`. L’absence d’un numéro dans une liste quelconque ne prouve pas que le certificat est acceptable. Les structures et traitements sont décrits dans la [RFC 5280, sections 5 et 6.3](https://www.rfc-editor.org/rfc/rfc5280).

**OCSP** fournit une réponse de statut pour un certificat : `good`, `revoked` ou `unknown`. La réponse doit provenir d’un répondant autorisé et être pertinente à la date d’évaluation. `producedAt` indique sa production, `thisUpdate` la date à laquelle le statut est connu comme correct et `nextUpdate`, s’il est présent, la prochaine mise à jour attendue. `good` ne valide pas à lui seul le certificat. Voir la [RFC 6960, sections 2.2 à 2.4, 3.2 et 4.2.2](https://www.rfc-editor.org/rfc/rfc6960).

Pour DZ Sign, l’indisponibilité d’un service ou l’absence de preuve exploitable devra rester visible. Une révocation ultérieure ne suffira pas à conclure automatiquement sur une signature passée : il faudra examiner les dates, le motif, les preuves disponibles et la politique de validation. Cette analyse historique est hors du premier parcours.

## Construire un rapport compréhensible

Le tableau suivant exprime les résultats que le projet devra pouvoir distinguer. Il sert de base aux futurs scénarios de vérification ; aucun de ces scénarios n’est présenté comme déjà implémenté.

| Contrôle | Question | Exemple de résultat explicite |
|---|---|---|
| Empreinte du fichier | Quel fichier exact a été traité ? | SHA-256 du fichier reçu |
| Intégrité cryptographique | Les données couvertes correspondent-elles à la signature ? | Vérifiée, échec ou contrôle impossible |
| Chaîne de confiance | Peut-on atteindre une ancre approuvée ? | Approuvée dans la configuration de test ou confiance non établie |
| Période de validité | Le certificat couvre-t-il la date d’évaluation ? | Date retenue et résultat du contrôle |
| Révocation | Dispose-t-on d’un statut exploitable ? | Statut, source et dates ; ou non vérifié avec la raison |
| Horodatage | Existe-t-il une preuve temporelle vérifiée ? | Jeton vérifié, invalide, non vérifié ou absent |

Le rapport devra distinguer un contrôle non effectué d’un contrôle effectué sans conclusion possible. Il devra également conserver la date d’évaluation et la configuration de confiance utilisées. Une erreur de lecture du PDF ne sera pas traduite en « signature invalide » si aucune vérification cryptographique n’a pu avoir lieu.

## Scénarios à préparer

- Comparer les empreintes du PDF importé et du PDF signé en expliquant pourquoi elles changent.
- Modifier des données couvertes par la signature et observer l’échec du contrôle d’intégrité.
- Vérifier le même PDF avec et sans l’ancre de confiance de test.
- Présenter un certificat expiré, un statut révoqué et un statut inconnu comme des situations distinctes.
- Simuler une source de révocation indisponible, sans transformer l’erreur en résultat favorable.
- Distinguer une heure déclarée d’un jeton d’horodatage effectivement vérifié.

Les fixtures, les paramètres cryptographiques et les services nécessaires seront définis dans les exemples pratiques. Cette documentation n’ajoute pas de dépendance réseau ni de conservation de documents au prototype.
