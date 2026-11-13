# Fondements techniques

[Manuel](README.md) · [English](../en/foundations.md) · [العربية](../ar/foundations.md)

## De l’empreinte à la signature

SHA-256 calcule une empreinte de 32 octets, affichée sous forme de 64 caractères hexadécimaux. Le calcul concerne les octets exacts du fichier. Une empreinte seule ne prouve ni son auteur ni la fiabilité de la référence utilisée pour la comparer.

La clé privée produit une signature ; la clé publique permet son contrôle. Un certificat associe cette clé publique à un sujet, un émetteur, une période et des usages. Une PKI organise leur délivrance, leur utilisation et leur révocation. Une chaîne ne devient fiable que par rapport à une ancre choisie et à une politique de validation.

Dans les exemples, la racine dure 365 jours, l’intermédiaire 180 jours et le signataire trente jours. Les clés RSA ont 3072 bits et les certificats utilisent SHA-256. Ces paramètres de laboratoire n’établissent pas une qualification juridique.

## Formats et preuves

PAdES concerne les signatures PDF, CAdES les structures CMS et XAdES les signatures XML. DZ Sign traite les PDF et vise PAdES-B-B, sans déclaration de conformité exhaustive. Une date déclarée par le signataire n’est pas une preuve d’horodatage indépendante.

Une CRL publie des certificats révoqués ; OCSP fournit un statut de certificat. Leur absence n’autorise pas une conclusion favorable. Cette version marque ces contrôles comme non vérifiés. L’expiration d’un certificat et l’altération du document sont deux résultats différents.

## Vocabulaire

| Terme | Sens dans le projet |
|---|---|
| Intégrité | Correspondance entre données couvertes et signature |
| Ancre de confiance | Racine explicitement approuvée par le vérificateur |
| Révocation | Changement de statut avant la fin de validité prévue |
| Couverture | Partie ou révision PDF protégée par la signature |
| Cachet | Mécanisme attestant l’origine et l’intégrité des données, non implémenté ici |

Les études détaillées sur la [PKI](../cryptography/pki.md), la [vérification](../cryptography/signature-validation.md) et les [formats](../standards/signature-formats.md) sont en français. Le [registre de références](../../resources/references.md) rassemble les sources techniques primaires.
