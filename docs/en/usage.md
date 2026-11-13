# Documents and reports

[Handbook](README.md) · [Français](../fr/usage.md) · [العربية](../ar/usage.md)

## Application walkthrough

Create a fictional PDF using an output filename that does not already exist:

```bash
mkdir -p .local/dz-sign/documents
.local/dz-sign/venv/bin/python examples/pdf-signing/create_demo_pdf.py .local/dz-sign/documents/attestation.pdf
```

Choose the PDF and click “Importer le PDF”. Select its name in the register to view metadata and available operations. The register belongs to the local server instance, not to a user account or browser tab.

To sign, select “Signer une copie de test” and confirm use of the fictional identity. The original is preserved; repeated signing requests return the same copy. Existing signed PDFs can be verified, but this workflow does not add another signature to them.

Unsigned hybrid-reference PDFs are rewritten in the copy before signing, without disabling strict parsing. The interface discloses this structural rewrite. It does not claim to preserve the PDF's bytes or every internal identifier.

## Reading verification results

Select the original or signed copy and start verification. The report separates data integrity, the cryptographic signature, certificate trust, the validity period and document coverage.

| Outcome | Meaning |
|---|---|
| `checks_passed_with_limits` | Local checks passed, with explicit limitations |
| `checks_failed` | At least one check failed; inspect the individual results |
| `needs_review` | Revisions or permissions require review |
| `no_signature` | No cryptographic signature detected |
| `indeterminate` | The analysis cannot reach a conclusion |

Revocation, trusted timestamps, historical validity and legal qualification are not established. A signature image does not substitute for a cryptographic signature.

## Keeping or removing results

Download the original, signed copy or JSON report before expiry. Both PDFs share the fifteen-minute deadline set when import began. Deleting the original also removes its signed copy from the service. Previously downloaded files remain wherever the browser saved them.

## Command-line examples

```bash
python3 examples/python/sha256_file.py README.md
.local/dz-sign/venv/bin/python examples/certificate-generation/generate.py
.local/dz-sign/venv/bin/python examples/pdf-signing/sign_pdf.py input.pdf output.pdf --pki .local/dz-sign/pki
.local/dz-sign/venv/bin/python examples/pdf-signing/verify_pdf.py output.pdf --trust-root .local/dz-sign/pki/trust/root.cert.pem --json
```

The examples' PKI and the application identity are separate. The interactive generator requests its own passphrases. Verification requires no private key; the trust root must match the one deliberately chosen for the exercise.
