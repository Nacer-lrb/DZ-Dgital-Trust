# Signer un PDF avec une identité de test

Cet exemple utilise la PKI locale de l’[exercice précédent](../certificate-generation/README.md) pour signer un PDF fictif. Il conserve le fichier d’origine, refuse une sortie existante et vérifie le résultat avant de le publier.

## Préparer l’environnement

Environnement testé : Linux, Python 3.12.3, pyHanko 0.38.1, cryptography 50.0.2 et OpenSSL 3.0.13. Les versions Python exactes sont consignées dans `requirements.txt`. Depuis la racine du dépôt :

```bash
python3 -m venv .local/dz-sign/venv
.local/dz-sign/venv/bin/python -m pip install -r examples/pdf-signing/requirements.txt
.local/dz-sign/venv/bin/python examples/certificate-generation/generate.py
```

L’installation télécharge les dépendances ; la génération et la signature sont locales. Si la PKI existe déjà, ne pas relancer sa génération. Utiliser celle créée précédemment tant que ses certificats sont valides, ou générer une autre PKI avec `--output` et transmettre son chemin à la signature avec `--pki`.

## Créer puis signer un document fictif

```bash
mkdir -p .local/dz-sign/documents
.local/dz-sign/venv/bin/python examples/pdf-signing/create_demo_pdf.py .local/dz-sign/documents/attestation.pdf
.local/dz-sign/venv/bin/python examples/pdf-signing/sign_pdf.py .local/dz-sign/documents/attestation.pdf .local/dz-sign/documents/attestation-signed.pdf
```

Saisir et confirmer la phrase secrète du **signataire**, et non celle des autorités. La saisie reste invisible. Pour une exécution automatisée, `--password-file` accepte un fichier secret privé selon les règles du générateur de PKI. Aucun mot de passe n’est passé en clair comme argument.

Le PDF contient un texte explicitement fictif. La signature est cryptographique et invisible : aucune image de signature ou de cachet n’est ajoutée. Les deux scripts refusent d’écraser un fichier existant. Pour refaire l’exercice, choisir de nouveaux noms.

Pour un PDF non signé à références croisées hybrides, le script réenregistre la structure dans une copie avant de signer. Il conserve la lecture stricte, refuse toujours les documents déjà signés et laisse l’original intact. Le résultat indique `normalized_before_signing` et la commande affiche un message explicite dans ce cas.

## Choix et contrôles réalisés

Le script utilise les API `SimpleSigner`, `PdfSignatureMetadata`, `PdfSigner` et `IncrementalPdfFileWriter` documentées dans le [guide officiel de signature](https://docs.pyhanko.eu/en/latest/lib-guide/signing.html) et la [référence des signataires](https://docs.pyhanko.eu/en/latest/api-docs/pyhanko.sign.signers.html), consultés le 11 novembre 2026. Leur comportement a été vérifié sur la version installée.

La signature utilise SHA-256 et le sous-filtre PAdES `ETSI.CAdES.detached`. L’objectif reste **PAdES-B-B** ; ce sous-filtre et une signature valide ne constituent pas une vérification exhaustive de toutes les exigences du profil.

Avant d’enregistrer la sortie, le script exige une seule signature, une intégrité cryptographique correcte et une chaîne approuvée à partir de la racine de test explicitement fournie. La politique locale exige l’usage `digitalSignature`, correspondant au certificat généré. C’est un choix de laboratoire distinct de la politique par défaut du validateur.

La validation est configurée sans récupération réseau. Son mode de révocation tolère l’absence d’information pour ce laboratoire : **la révocation reste non vérifiée**, même si la chaîne est approuvée. Aucun horodatage de confiance n’est demandé et aucune qualification juridique n’est affirmée.

Le script lit au maximum 10 Mio d’entrée, refuse les fichiers non réguliers, les PDF chiffrés et les PDF déjà signés. Il n’est pas encore le backend isolé décrit dans l’architecture : il ne fournit ni limite de temps du processus, ni service partagé, ni rapport complet par signature. Utiliser des fichiers de test locaux.

## Vérifier l’exemple

```bash
PYTHONDONTWRITEBYTECODE=1 .local/dz-sign/venv/bin/python -m unittest discover -s examples/pdf-signing -p 'test_*.py' -v
```

Les tests créent une PKI et un PDF dans un répertoire temporaire, puis les suppriment. Ils contrôlent la signature et la chaîne avec pyHanko, la conservation de l’original, le refus d’écrasement, la mauvaise phrase secrète et les entrées invalides ou déjà signées. Toute tentative de connexion réseau pendant le parcours de signature testé fait échouer le test.

Un contrôle indépendant extrait le CMS et les octets couverts : OpenSSL vérifie la signature détachée puis rejette un contenu altéré. Ce contrôle utilise `-noverify` pour se concentrer sur la signature CMS ; il n’évalue ni la confiance du certificat ni les permissions PDF. La chaîne X.509 est testée séparément dans l’exercice PKI. Si OpenSSL manque, le contrôle indépendant est indiqué comme ignoré.

## Vérifier un PDF sans utiliser de clé privée

La commande de vérification lit le PDF et, si vous le choisissez, un certificat racine public. Elle ne demande pas de phrase secrète :

```bash
.local/dz-sign/venv/bin/python examples/pdf-signing/verify_pdf.py .local/dz-sign/documents/attestation-signed.pdf --trust-root .local/dz-sign/pki/trust/root.cert.pem
```

Pour obtenir le même rapport sous forme structurée :

```bash
.local/dz-sign/venv/bin/python examples/pdf-signing/verify_pdf.py .local/dz-sign/documents/attestation-signed.pdf --trust-root .local/dz-sign/pki/trust/root.cert.pem --json
```

L’option `--trust-root` approuve explicitement ce certificat pour cet essai. Sans elle, aucune racine, y compris celle du magasin système, n’est approuvée : l’intégrité peut réussir sans que la confiance soit établie. N’approuver que la racine de test que vous avez choisie ; sa présence dans un document ne la rend pas fiable.

### Lire les résultats

Le rapport contient l’empreinte du PDF, la date d’évaluation UTC, l’empreinte de l’ancre choisie et un résultat par signature. Les dates de validité et les informations du certificat sont séparées du calcul cryptographique. Les libellés structurés sont conservés dans le rapport texte pour faciliter la comparaison avec JSON.

| Résultat | Interprétation |
|---|---|
| `checks_passed_with_limits` | Les contrôles locaux retenus réussissent ; révocation et horodatage restent non vérifiés |
| `checks_failed` | Au moins un contrôle échoue : examiner les champs, par exemple intégrité ou validation du certificat |
| `needs_review` | La signature ne couvre pas le fichier entier ou les permissions demandent un examen |
| `no_signature` | Aucune signature cryptographique détectée |
| `indeterminate` | L’analyse ne permet pas de conclure ; ce résultat ne prouve pas une signature incorrecte |

Le champ `certificate_validation` tient compte de la chaîne, des usages et de la date dans la politique locale ; il ne représente pas seulement l’existence d’un chemin vers la racine. Le champ `certificate_period` indique séparément si le certificat du signataire couvre la date d’évaluation. Les certificats intermédiaires restent également soumis aux contrôles du moteur.

Une révision postérieure est traitée de façon conservatrice : même si la signature reste correcte sur sa révision, la commande ne renvoie pas un succès global pour le fichier actuel. L’analyse des modifications par pyHanko est incluse, sans prétendre remplacer l’examen de tous les contenus et comportements d’un lecteur PDF.

| Code de sortie | Signification |
|---|---|
| `0` | Contrôles locaux réussis avec les limites annoncées |
| `1` | Échec, révision à examiner ou absence de signature |
| `2` | Lecture ou analyse impossible, configuration incorrecte ou arguments invalides |

Le code `0` ne signifie jamais « signature juridiquement qualifiée » ou « tous les contrôles effectués ». Le JSON précise `legal_qualification: not_assessed`, `revocation: not_verified` et `timestamp: not_verified`. La commande n’établit pas de validité historique et n’utilise pas une date déclarée par le signataire comme date d’évaluation.

Les tests supplémentaires vérifient le PDF intact, une altération des octets couverts, l’absence d’ancre approuvée, l’expiration à la date d’évaluation, une révision ajoutée, un PDF sans signature et un fichier illisible. Ils contrôlent aussi la sortie JSON et l’absence de modification du fichier reçu. L’API utilisée est décrite dans la [documentation de validation pyHanko](https://docs.pyhanko.eu/en/latest/api-docs/pyhanko.sign.validation.html), consultée le 11 novembre 2026 ; son comportement est testé avec la version 0.38.1 installée.
