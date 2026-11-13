# Technical foundations

[Handbook](README.md) · [Français](../fr/foundations.md) · [العربية](../ar/foundations.md)

## From a digest to a signature

SHA-256 produces a 32-byte digest, commonly displayed as 64 hexadecimal characters. It covers the file's exact bytes. A digest alone does not authenticate the author or establish the reliability of the reference used for comparison.

A private key creates a signature; its public key permits verification. A certificate associates that public key with a subject, issuer, validity period and permitted uses. A PKI manages issuance, use and revocation. A chain is trusted only relative to a chosen anchor and validation policy.

The examples use a 365-day root, 180-day intermediate and thirty-day signing certificate. Keys are RSA-3072 and certificate signatures use SHA-256. These laboratory parameters do not establish legal qualification.

## Formats and evidence

PAdES concerns PDF signatures, CAdES CMS structures and XAdES XML signatures. DZ Sign handles PDFs and targets PAdES-B-B without claiming exhaustive conformance. A signer-declared date is not independent timestamp evidence.

A CRL publishes revoked certificates; OCSP provides certificate status responses. Missing evidence does not justify a favorable result. This version marks these checks as not verified. Certificate expiration and document alteration are different findings.

## Vocabulary

| Term | Meaning in this project |
|---|---|
| Integrity | Correspondence between covered data and the signature |
| Trust anchor | Root explicitly trusted by the verifier |
| Revocation | Status change before the planned validity end |
| Coverage | PDF portion or revision protected by the signature |
| Electronic seal | Mechanism for data origin and integrity; not implemented here |

Longer studies on [PKI](../cryptography/pki.md), [validation](../cryptography/signature-validation.md) and [formats](../standards/signature-formats.md) are available in French. The [reference register](../../resources/references.md) lists primary technical sources.
