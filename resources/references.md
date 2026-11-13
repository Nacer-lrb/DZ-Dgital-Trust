# Registre des références

Consultation : **11 novembre 2026**. Ce registre distingue les textes consultés, les références techniques retenues et les vérifications encore ouvertes. Les liens renvoient aux éditeurs officiels.

## Textes algériens

| ID | Source officielle | Utilisation et vérification |
|---|---|---|
| J01 | [Loi 26-02 du 17 février 2026 — JO n° 14 du 18 février 2026, p. 6–18](https://www.joradp.dz/FTP/jo-francais/2026/F2026014.pdf) | Texte central ; lecture du PDF local et consultation de la publication officielle. Articles de cadrage : 2, 4–12, 26–36, 47–52, 109–115 |
| J02 | [Loi 15-04 du 1er février 2015 — JO n° 6](https://www.joradp.dz/FTP/jo-francais/2015/F2015006.pdf) | Référence historique ; publication et intitulé vérifiés. Abrogation et maintien des textes d’application à lire dans J01, art. 115 |
| J03 | [Loi 18-07 du 10 juin 2018 — JO n° 34](https://www.joradp.dz/FTP/jo-francais/2018/F2018034.pdf) | Texte relatif aux données personnelles ; référence identifiée, analyse détaillée hors du présent cadrage |
| J04 | [Loi 25-11 du 24 juillet 2025 — JO n° 48, p. 14 et suivantes](https://www.joradp.dz/FTP/jo-francais/2025/F2025048.pdf) | Modification de J03 : intitulé et publication vérifiés. Ne pas utiliser J03 comme un texte inchangé |

Les éditions JORADP liées ci-dessus portent la mention « traduction française ». La copie du dépôt `legal/laws/loi-26-02-2026.pdf` contient le numéro complet du Journal officiel, et pas uniquement la loi. Son titre, son numéro et son contenu ont été rapprochés de la source officielle ; l’identité binaire des deux fichiers n’a pas été vérifiée.

## Références techniques

| ID | Document consulté | Usage prévu |
|---|---|---|
| T01 | [RFC 5280 — Internet X.509 PKI Certificate and CRL Profile](https://www.rfc-editor.org/rfc/rfc5280) | Certificats, chaînes et révocation ; tenir compte des mises à jour et errata signalés par l’éditeur |
| T02 | [RFC 5652 — Cryptographic Message Syntax](https://www.rfc-editor.org/rfc/rfc5652) | Structures de données signées |
| T03 | [RFC 3161 — Time-Stamp Protocol](https://www.rfc-editor.org/rfc/rfc3161) | Jetons d’horodatage ; suivre aussi les mises à jour indiquées par l’éditeur |
| T04 | [RFC 6960 — OCSP](https://www.rfc-editor.org/rfc/rfc6960) | Consultation du statut des certificats |
| T05 | [ETSI EN 319 142-1 V1.2.1, janvier 2024](https://www.etsi.org/deliver/etsi_en/319100_319199/31914201/01.02.01_60/en_31914201v010201p.pdf) | Composants et signatures PAdES baseline ; édition de travail identifiée, sans présumer qu’elle restera la dernière édition |
| T06 | [RFC 4158 — Certification Path Building](https://www.rfc-editor.org/rfc/rfc4158) | Référence informative pour distinguer construction et validation d’un chemin ; consultée le 11 novembre 2026 |
| T07 | [RFC 3647 — Certificate Policy and Certification Practices Framework](https://www.rfc-editor.org/rfc/rfc3647) | Cadre informatif : rôles, politiques et cycle de vie, notamment sections 1 et 4 ; consulté le 11 novembre 2026 |
| T08 | [NIST FIPS 180-4 — Secure Hash Standard, août 2015](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf) | Définition de SHA-256, notamment section 6.2 ; édition consultée le 11 novembre 2026, sans présumer de son statut futur |
| T09 | [ETSI EN 319 122-1 V1.3.1, juin 2023](https://www.etsi.org/deliver/etsi_en/319100_319199/31912201/01.03.01_60/en_31912201v010301p.pdf) | Composants et profils CAdES baseline, sections 4 à 6 ; consultée le 11 novembre 2026 |
| T10 | [ETSI EN 319 132-1 V1.2.1, février 2022](https://www.etsi.org/deliver/etsi_en/319100_319199/31913201/01.02.01_60/en_31913201v010201p.pdf) | Composants et profils XAdES baseline, sections 4 à 6 ; consultée le 11 novembre 2026 |
| T11 | [W3C XML Signature Syntax and Processing 1.1, recommandation du 11 avril 2013](https://www.w3.org/TR/xmldsig-core1/) | Références, transformations et vérification XML, sections 3 et 4 ; consultée le 11 novembre 2026 |
| T12 | [Cryptography 41.0.7 — tutoriel X.509](https://cryptography.io/en/41.0.7/x509/tutorial/) | API de construction de certificats du premier exemple ; consultée le 11 novembre 2026 |
| T13 | [Cryptography 41.0.7 — sérialisation](https://cryptography.io/en/41.0.7/hazmat/primitives/asymmetric/serialization/) et [RSA](https://cryptography.io/en/41.0.7/hazmat/primitives/asymmetric/rsa/) | PKCS#8 chiffré et génération RSA ; documentation de la version testée, consultée le 11 novembre 2026 |
| T14 | [NIST SP 800-131A révision 2, mars 2019](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-131Ar2.pdf) | Section 3 : repère historique de taille RSA pour l’exemple ; ne constitue pas une revue de tous les référentiels actuels ; consultée le 11 novembre 2026 |
| T15 | [OpenSSL 3.0 — extensions X.509](https://docs.openssl.org/3.0/man5/x509v3_config/) et [lecture des certificats](https://docs.openssl.org/3.0/man1/openssl-x509/) | Inspection des certificats et de leurs extensions ; consultées le 11 novembre 2026 |
| T16 | [Python — hashlib](https://docs.python.org/3/library/hashlib.html) et [hmac.compare_digest](https://docs.python.org/3/library/hmac.html#hmac.compare_digest) | Hachage SHA-256 par blocs et comparaison d’une référence ; consultées le 11 novembre 2026, exemple exécuté avec Python 3.12.3 |
| T17 | [pyHanko — guide de signature](https://docs.pyhanko.eu/en/latest/lib-guide/signing.html) et [API des signataires](https://docs.pyhanko.eu/en/latest/api-docs/pyhanko.sign.signers.html) | API de signature PDF ; pages `latest` consultées le 11 novembre 2026, comportement contrôlé avec pyHanko 0.38.1 et son code installé |
| T18 | [pyHanko — API de validation](https://docs.pyhanko.eu/en/latest/api-docs/pyhanko.sign.validation.html) | Vérification des signatures PDF ; page `latest` consultée le 11 novembre 2026, résultats et champs contrôlés avec la version 0.38.1 installée |
| T19 | [FastAPI — premiers pas](https://fastapi.tiangolo.com/tutorial/first-steps/) et [CORS](https://fastapi.tiangolo.com/tutorial/cors/) | Base API et origine explicite ; consultées le 11 novembre 2026 |
| T20 | [Next.js — installation App Router](https://nextjs.org/docs/app/getting-started/installation) | Initialisation de l’interface TypeScript ; consultée le 11 novembre 2026, versions exécutées consignées dans `demo/frontend/package-lock.json` |
| T21 | [Starlette — requêtes](https://www.starlette.io/requests/) et [FastAPI — fichiers reçus](https://fastapi.tiangolo.com/tutorial/request-files/) | Import multipart, limites de parsing et fichiers temporaires ; consultées le 13 novembre 2026 et rapprochées du code de Starlette 1.10.0 installé |
| T22 | [Python — sous-processus asyncio](https://docs.python.org/3/library/asyncio-subprocess.html) | Lancement, attente et arrêt du processus d’inspection ; consultée le 13 novembre 2026, exemple exécuté avec Python 3.12.3 |

Pour la [fiche de vérification](../docs/cryptography/signature-validation.md), les passages utilisés sont T01, sections 5 et 6.3 (CRL), T02, sections 5 et 11 (CMS et attributs), T03, sections 2.1 à 2.4 (horodatage), et T04, sections 2.2 à 2.4, 3.2 et 4.2.2 (OCSP). Consultation : 11 novembre 2026.

Le référencement de ces documents ne constitue pas une déclaration de conformité du futur logiciel.

## Vérifications à poursuivre

- Rechercher les textes d’application de la loi 26-02 et les décisions établissant la mise en place effective de l’autorité. La recherche ciblée effectuée ne permet pas de conclure à leur absence.
- Identifier les listes de confiance et politiques effectivement publiées avant toute intégration de certificats réels.
- Compléter l’étude des dispositions relatives à l’identification électronique et aux effets des documents électroniques.
- Étudier J03 et J04 ensemble avant de définir des traitements de données personnelles.
- Préciser l’analyse des révisions et permissions PDF avant l’implémentation. La consultation en ligne du PDF ISO 32000-1 hébergé par Adobe a échoué en raison de sa taille ; cette source n’est pas comptée parmi les documents consultés.

## Comment maintenir ce registre

Pour chaque ajout, enregistrer l’intitulé exact, l’éditeur, le lien officiel, la version ou la date du texte, la date de consultation et les articles ou sections utilisés. Une source non consultée doit être marquée comme piste. Une évolution réglementaire doit conduire à revoir les fiches concernées, pas seulement à ajouter un lien.
