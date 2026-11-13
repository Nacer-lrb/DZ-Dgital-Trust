# Glossaire

Ce glossaire accompagne la lecture et les futurs essais de DZ Sign. Les explications juridiques sont des reformulations ; les définitions légales figurent à l’article 2 de la loi n° 26-02. Sources consultées le 11 novembre 2026 : [registre des références](references.md).

## Documents et signatures

| Terme | Explication | Exemple ou précision |
|---|---|---|
| Document électronique | Contenu créé, transmis, reçu ou conservé sous forme électronique | Un contrat PDF ; loi 26-02, art. 2 |
| Signature électronique | Données électroniques associées à d’autres données, utilisées par le signataire pour signer | Le signataire est une personne physique ; art. 2 |
| Signature numérique | Mécanisme cryptographique utilisant une clé privée et une clé publique | C’est le mécanisme que DZ Sign veut rendre observable |
| Signature avancée | Signature répondant aux exigences de liaison au signataire, d’identification, de contrôle et de détection des modifications | Loi 26-02, art. 4 ; la seule présence d’un certificat ne suffit pas à établir ces exigences |
| Signature qualifiée | Signature répondant aux exigences supplémentaires prévues par la loi | Art. 5 et 6 ; une signature de test ne démontre pas cette qualification |
| Cachet électronique | Données associées à d’autres données pour en garantir l’origine et l’intégrité | Art. 2 ; une image de tampon ne réalise pas ce mécanisme |
| Intégrité | Propriété permettant de vérifier que les données couvertes n’ont pas été altérées | Ne prouve pas à elle seule l’identité réelle de la personne |
| Empreinte | Résultat d’une fonction de hachage appliquée à des données | Une empreinte seule n’authentifie pas l’auteur |

## Clés, certificats et confiance

Les termes de cette section s’appuient sur la [RFC 5280](https://www.rfc-editor.org/rfc/rfc5280).

| Terme | Explication | Dans la démonstration |
|---|---|---|
| Clé privée | Partie secrète d’une paire de clés, utilisée notamment pour signer | Clé réservée aux essais, conservée côté backend |
| Clé publique | Partie de la paire qui permet de vérifier une signature | Peut être contenue dans un certificat |
| Certificat X.509 | Structure signée associant une clé publique à un sujet et à des informations d’usage et de validité | Examiner aussi son émetteur et ses extensions |
| Autorité de certification, CA | Entité qui émet et signe des certificats | Une CA de test ne devient pas une autorité reconnue juridiquement |
| PKI | Ensemble de composants, règles et procédures de gestion des certificats et des clés | Inclut la délivrance, la validation et la révocation |
| Chaîne de certification | Suite de certificats reliant un certificat à une ancre de confiance | Les certificats intermédiaires peuvent être nécessaires |
| Ancre de confiance | Point de confiance choisi dans la configuration de validation | La confiance dépend du contexte du vérificateur |
| Certificat auto-signé | Certificat dont la signature est vérifiable avec la clé publique qu’il contient | L’auto-signature n’établit pas une confiance externe |
| Expiration | Fin de la période de validité d’un certificat | À distinguer du résultat cryptographique et du moment de validation |
| Révocation | Retrait de validité d’un certificat avant son échéance | Motif possible : compromission de la clé |
| CRL | Liste de certificats révoqués signée par son émetteur | Vérifier aussi sa fraîcheur et sa portée |
| OCSP | Protocole de consultation du statut d’un certificat | Une réponse indisponible ne signifie pas « non révoqué » ; [RFC 6960](https://www.rfc-editor.org/rfc/rfc6960) |

## Services et formats

| Terme | Explication | Référence |
|---|---|---|
| Horodatage | Association de données à un instant, afin d’apporter une preuve temporelle | Loi 26-02, art. 2, 14 et 15 ; l’heure locale déclarée dans une signature n’est pas une preuve indépendante |
| TSA | Autorité délivrant des jetons d’horodatage | [RFC 3161](https://www.rfc-editor.org/rfc/rfc3161) |
| CMS | Syntaxe de messages cryptographiques, dont les données signées | [RFC 5652](https://www.rfc-editor.org/rfc/rfc5652) |
| PAdES | Ensemble de spécifications de signatures numériques PDF | ETSI EN 319 142-1 ; un format technique ne détermine pas une qualification juridique |
| Validation | Processus qui évalue une signature selon des règles et des éléments disponibles | Le rapport doit préciser les contrôles réalisés et les inconnues |
| Fournisseur de services de confiance | Catégorie couvrant les tiers et les prestataires de services de confiance | Loi 26-02, art. 26 ; voir les [institutions](../docs/algeria/institutions.md) |
| Liste de confiance | Liste publiée par l’autorité concernant les prestataires et leurs services | Loi 26-02, art. 2 et 48 ; distincte du magasin local de certificats de test |

## Lire un résultat de vérification

« Intégrité vérifiée », « chaîne approuvée », « certificat dans sa période de validité » et « révocation vérifiée » répondent à des questions différentes. Un contrôle impossible à réaliser doit rester indéterminé, avec une explication. Le résultat du prototype ne doit pas conclure automatiquement à une signature juridiquement qualifiée.
