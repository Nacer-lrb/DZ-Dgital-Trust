# Installation and local operation

[Handbook](README.md) · [Français](../fr/installation.md) · [العربية](../ar/installation.md)

## Requirements

Linux or a POSIX environment, Python 3.12, Node.js 22 or later and npm. OpenSSL 3 is required for the independent cryptographic checks. Installation downloads dependencies; subsequent PDF operations do not automatically fetch remote resources.

From the project root:

```bash
python3 -m venv .local/dz-sign/venv
.local/dz-sign/venv/bin/python -m pip install -r demo/backend/requirements-dev.txt
.local/dz-sign/venv/bin/python demo/backend/setup_demo.py
```

Do not recreate an existing environment. The setup script creates a fictional identity in `.local/dz-sign/app-identity/` and refuses to overwrite an existing identity. Its signing certificate lasts thirty days. To create another generation, use `--output` with a new directory and configure `DZ_SIGN_IDENTITY_DIR`.

## Starting the services

First terminal, from the project root:

```bash
.local/dz-sign/venv/bin/python -m uvicorn app.main:app --app-dir demo/backend --host 127.0.0.1 --port 8000
```

Second terminal:

```bash
cd demo/frontend
npm ci
npm run dev
```

Open `http://127.0.0.1:3000`. API health is at `http://127.0.0.1:8000/api/health`, with its contract at `/docs`. Restart the backend after changing its code. Stop each service with `Ctrl+C`.

## Configuration

| Variable | Default |
|---|---|
| `DZ_SIGN_FRONTEND_ORIGIN` | `http://127.0.0.1:3000` |
| `NEXT_PUBLIC_API_ORIGIN` | `http://127.0.0.1:8000` |
| `DZ_SIGN_IDENTITY_DIR` | `.local/dz-sign/app-identity/`, resolved by the server |
| `DZ_SIGN_PASSWORD_FILE` | That identity's `runtime/signer.secret` |

`localhost` and `127.0.0.1` are different browser origins. `NEXT_PUBLIC_*` values are public and embedded during compilation; changing them requires rebuilding a production frontend.

Only one backend instance may use the temporary store. Do not add independent workers or bind to `0.0.0.0` within this unauthenticated local scope.

## Troubleshooting

| Symptom | Check |
|---|---|
| Service unavailable | Backend running, correct port and origin, matching frontend/backend versions |
| Signing disabled | Identity prepared; key and secret present with `0600` permissions |
| `409` | Another operation is active or another instance owns the store |
| `410` | Document expired; import it again |
| `413` | Original or signed copy exceeds 10 MiB |
| `422` | Read the message: encrypted/unsupported PDF, missing confirmation or incorrect identity configuration |
| `504` | Processing deadline exceeded; partial results are removed |

An `OPTIONS 200` response is a normal CORS check. It does not mean the following `POST` will succeed.
