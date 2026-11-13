# Architecture, API and security

[Handbook](README.md) · [Français](../fr/reference.md) · [العربية](../ar/reference.md)

## Components

Next.js and React present documents and reports. FastAPI controls browser origins, imports and retention. pyHanko handles PDF operations in child processes. Dependency files record the exact package versions.

The backend keeps metadata in memory and files under `.local/dz-sign/uploads/`. Each document has a random identifier; uploaded filenames are never storage paths. There is no database, account system or session recovery after restart.

## HTTP contract

| Method and route | Body or result |
|---|---|
| `GET /api/health` | Service status and actual capabilities |
| `GET /api/documents` | Unexpired documents |
| `POST /api/documents` | Multipart: one upload named `file` |
| `GET /api/documents/{id}` | Metadata and optional signed-copy reference |
| `GET /api/documents/{id}/download` | Original attachment |
| `POST /api/documents/{id}/sign` | `{"confirm_test_signature": true}` |
| `POST /api/documents/{id}/verify` | `{"source":"original"}` or `{"source":"signed"}` |
| `GET /api/results/{id}/download` | Signed-copy attachment |
| `DELETE /api/documents/{id}` | Delete the original and its copy |

A produced report receives HTTP `200` even when `outcome` records a failed cryptographic check. Request errors and operations that cannot run are separate. Signing responses expose `normalized_before_signing` when a hybrid PDF was structurally rewritten.

## Enforced limits

| Resource | Limit |
|---|---|
| Uploaded file or published signed copy | 10 MiB |
| Multipart envelope | 10 MiB + 64 KiB, checked while reading |
| Documents | Ten; at most 200 MiB of originals and signed copies |
| Active PDF operations | One |
| Duration | 30 seconds per import, signature or verification |
| PDF child process | 512 MiB virtual address space, 30 seconds CPU on POSIX |
| Report output | 2 MiB |
| Retention | At most fifteen minutes from import start |

Expiry is checked before access. An active operation retains its file until the process stops, but an expired result is not published. Cleanup runs every minute, on normal shutdown and on startup. A monotonic clock prevents system-clock rollback from extending retention.

## Trust boundaries

Test keys are encrypted PKCS#8 files. Keys and secrets use private `0600` permissions, document directories `0700`. The server chooses key, secret and trust-root paths; no endpoint accepts them from the client. Secrets are never returned to the browser.

Workers do not automatically fetch network resources. The parent-child JSON protocol is bounded and validated. Unreadable output is rejected rather than interpreted as success.

Origin and Host checks are not authentication. This version is for one local user. Application restrictions do not constitute a complete OS sandbox; another process under the same account can access storage. Deletion is not a promise of forensic erasure.

## Interface

The document register and operation panel are separate from the verification report. Guidance, privacy and terms are real pages. Loading, empty, error and expired states have explicit messages. No fabricated document data, statistics or demonstrations are used to fill the screen.
