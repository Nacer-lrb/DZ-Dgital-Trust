# Générer une PKI réservée aux tests

Cet exemple crée trois certificats et leurs clés : une racine, une autorité intermédiaire et « Amel - TEST ONLY ». Il permet d’observer une chaîne X.509 avant de passer à la signature de PDF. Aucune identité réelle n’est vérifiée et aucun service qualifié n’est fourni.

## Prérequis

Un système POSIX, Python 3.12, la bibliothèque `cryptography` (API de la version 41 ou supérieure) et OpenSSL 3 pour la vérification indépendante. L’exemple a été testé avec Python 3.12.3, `cryptography` 41.0.7 et OpenSSL 3.0.13. Ces versions constatées ne constituent pas une recommandation de déploiement : utiliser une version maintenue et conserver les versions effectivement utilisées dans le relevé d’essai.

Le script n’installe rien. Dans votre environnement Python dédié, installer `cryptography` si elle manque, puis exécuter depuis la racine du dépôt :

```bash
python3 examples/certificate-generation/generate.py
```

Saisir et confirmer deux phrases secrètes distinctes : l’une pour les autorités, l’autre pour le signataire. Elles ne s’affichent pas. Chaque phrase doit comporter au moins 16 octets UTF-8 ; privilégier une phrase longue et imprévisible. La longueur minimale n’est pas une mesure de sa qualité.

## Résultat local

```text
.local/dz-sign/pki/
├── generation/
│   ├── root.key.pem
│   └── intermediate.key.pem
├── runtime/
│   ├── signer.key.pem
│   ├── signer.cert.pem
│   └── intermediate.cert.pem
├── trust/
│   └── root.cert.pem
└── manifest.json
```

Les clés sont chiffrées au format PKCS#8 PEM avec `BestAvailableEncryption`. Les dossiers de la génération sont privés (`0700`) et les fichiers sont créés en `0600`. Le répertoire `.local/dz-sign/` est ignoré par Git. Le backend futur devra recevoir uniquement les éléments `runtime` nécessaires et la racine publique de `trust`, jamais les clés des autorités.

Le script refuse une destination existante, même vide ; il n’offre aucune option d’écrasement. Une nouvelle exécution demande un nouveau chemin via `--output`. Pour rester hors du suivi Git, choisir un sous-répertoire de `.local/dz-sign/`. Les clés, numéros de série et dates changent à chaque génération : c’est la procédure qui est reproductible, pas les octets produits.

## Paramètres retenus pour cet exemple

| Élément | Choix pédagogique |
|---|---|
| Clés | RSA 3072 bits, exposant 65537 |
| Signature des certificats | SHA-256 avec RSA PKCS#1 v1.5 |
| Racine | 365 jours, `CA:TRUE`, profondeur maximale 1 |
| Intermédiaire | 180 jours, `CA:TRUE`, profondeur maximale 0 |
| Signataire | 30 jours, `CA:FALSE`, usage `digitalSignature` |
| Autorités | Usages `keyCertSign` et `cRLSign` |
| Début de validité | Heure de génération moins cinq minutes |

Ces durées courtes sont des choix de laboratoire. La taille RSA dépasse le seuil de 2048 bits indiqué pour la génération de signatures RSA dans la [SP 800-131A rév. 2, section 3](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-131Ar2.pdf). Ce repère technique ne vaut pas validation réglementaire algérienne ni revue de tous les référentiels actuels.

La construction utilise les API documentées dans le [tutoriel X.509](https://cryptography.io/en/41.0.7/x509/tutorial/), la [génération RSA](https://cryptography.io/en/41.0.7/hazmat/primitives/asymmetric/rsa/) et la [sérialisation des clés](https://cryptography.io/en/41.0.7/hazmat/primitives/asymmetric/serialization/). Références consultées le 11 novembre 2026. Les extensions sont expliquées dans la [fiche PKI](../../docs/cryptography/pki.md).

L’émission est directe dans ce laboratoire : pas de CSR ni de contrôle d’identité externe. Aucun EKU particulier, URL OCSP, point de distribution CRL ou horodatage n’est ajouté. L’usage `cRLSign` prépare un exercice futur ; aucune CRL n’est encore générée. Le certificat de signature n’affirme aucun statut qualifié. La conformité PAdES sera examinée sur les PDF produits à l’étape suivante.

## Examiner et vérifier

```bash
openssl x509 -in .local/dz-sign/pki/runtime/signer.cert.pem -noout -text
openssl verify -x509_strict -no-CApath -no-CAstore -CAfile .local/dz-sign/pki/trust/root.cert.pem -untrusted .local/dz-sign/pki/runtime/intermediate.cert.pem .local/dz-sign/pki/runtime/signer.cert.pem
```

La seconde commande doit se terminer par `OK` pour les certificats fraîchement générés. Elle prend explicitement la racine locale comme ancre. Elle ne vérifie ni la révocation ni un statut juridique. La racine n’est pas installée dans le magasin système ou dans un navigateur.

Pour les exécutions automatisées, `--authority-password-file` et `--signer-password-file` acceptent des fichiers secrets réguliers privés, sans lien symbolique, contenant chacun une phrase secrète (saut de ligne final facultatif). Les valeurs ne sont jamais des arguments de commande. Créer ces fichiers hors du suivi Git et les protéger avant usage ; le script ne les crée ni ne les conserve dans le résultat.

## Vérifier l’exemple lui-même

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s examples/certificate-generation -p 'test_*.py' -v
```

Les essais génèrent leurs propres clés dans un répertoire temporaire et le suppriment à la fin. Ils vérifient le chiffrement, les permissions, la correspondance clé-certificat, le refus d’écrasement et les fichiers secrets. OpenSSL contrôle la chaîne en mode strict, puis le rejet sans intermédiaire et à une date postérieure à l’expiration du signataire. Si OpenSSL manque, ce contrôle indépendant est signalé comme ignoré.
