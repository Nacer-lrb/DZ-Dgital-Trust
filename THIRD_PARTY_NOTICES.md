# Third-party material

The MIT license in `LICENSE` applies to original project code and documentation. It does not relicense dependencies, standards or official publications.

- `legal/laws/loi-26-02-2026.pdf` is a copy of the Algerian Official Journal, issue 14 of 18 February 2026, published by the Secrétariat général du Gouvernement. The file contains the full issue. [Official publication](https://www.joradp.dz/FTP/jo-francais/2026/F2026014.pdf).
- ETSI standards, IETF RFCs and NIST publications are linked as references. Their respective notices apply; the project does not redistribute their full text as original documentation.
- Python and JavaScript packages retain their own licenses. Their versions are recorded in `examples/pdf-signing/requirements.txt`, `demo/backend/requirements*.txt` and `demo/frontend/package-lock.json`.
- Next.js creates `next-env.d.ts` and build artifacts. The framework reference file and dependency lockfile are retained because the build relies on them.

No production signing key or private certificate authority is distributed. The local setup scripts create test material under `.local/dz-sign/`.
