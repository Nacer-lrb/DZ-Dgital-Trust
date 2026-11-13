# Documents et rapports

[Manuel](README.md) · [English](../en/usage.md) · [العربية](../ar/usage.md)

## Essai dans l’application

Créer un document fictif avec un nom qui n’existe pas encore :

```bash
mkdir -p .local/dz-sign/documents
.local/dz-sign/venv/bin/python examples/pdf-signing/create_demo_pdf.py .local/dz-sign/documents/attestation.pdf
```

Choisir le PDF puis « Importer le PDF ». Son nom dans le registre permet d’afficher ses métadonnées et les traitements disponibles. Le registre est commun à l’instance locale, pas à un compte ou à un onglet.

Pour signer, choisir « Signer une copie de test » et confirmer l’usage de l’identité fictive. L’original est conservé ; une seconde demande restitue la même copie. Les PDF déjà signés sont vérifiables, mais ce parcours refuse de leur ajouter une signature.

Les PDF hybrides non signés sont réenregistrés dans la copie avant signature, sans désactiver la lecture stricte. L’interface signale cette réécriture structurelle. Elle ne prétend pas conserver les octets ou tous les identifiants internes du PDF.

## Lire une vérification

Choisir l’original ou la copie signée puis lancer la vérification. Le rapport distingue l’intégrité, la signature cryptographique, la confiance du certificat, sa période de validité et la couverture du document.

| Résultat | Interprétation |
|---|---|
| `checks_passed_with_limits` | Contrôles locaux réussis, avec limites explicites |
| `checks_failed` | Au moins un contrôle échoue ; lire les résultats séparés |
| `needs_review` | Révisions ou permissions à examiner |
| `no_signature` | Aucune signature cryptographique détectée |
| `indeterminate` | Analyse impossible à conclure |

La révocation, l’horodatage de confiance, la validité historique et la qualification juridique ne sont pas établis. Une image de signature ne remplace pas une signature cryptographique.

## Conserver ou retirer un résultat

Télécharger l’original, la copie ou le rapport JSON avant expiration. Les deux PDF partagent l’échéance de quinze minutes fixée au début de l’import. Supprimer l’original retire aussi sa copie du service. Les fichiers déjà téléchargés restent sur le poste choisi par le navigateur.

## Exemples en ligne de commande

```bash
python3 examples/python/sha256_file.py README.md
.local/dz-sign/venv/bin/python examples/certificate-generation/generate.py
.local/dz-sign/venv/bin/python examples/pdf-signing/sign_pdf.py entree.pdf sortie.pdf --pki .local/dz-sign/pki
.local/dz-sign/venv/bin/python examples/pdf-signing/verify_pdf.py sortie.pdf --trust-root .local/dz-sign/pki/trust/root.cert.pem --json
```

La PKI des exemples et l’identité de l’application sont distinctes. Le générateur interactif demande ses propres phrases secrètes. La vérification n’utilise aucune clé privée ; sa racine doit correspondre à celle choisie pour l’essai.
