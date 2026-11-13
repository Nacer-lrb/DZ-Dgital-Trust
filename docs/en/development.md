# Development and contributions

[Handbook](README.md) · [Français](../fr/development.md) · [العربية](../ar/development.md)

## Code organization

`demo/backend/app/` contains HTTP routes, temporary storage, the worker protocol and configuration. `examples/` contains cryptographic operations and exercises. The frontend separates JSON contracts, HTTP transport, the document register and report rendering.

Dependency versions are pinned. Do not edit installed packages or framework-generated files to bypass a failure. Local documents and keys stay under `.local/dz-sign/`, excluded by `.gitignore` if the repository is initialized later.

## Checks

After installing development dependencies:

```bash
python3 scripts/check.py
```

This runs Python tests, static analysis and formatting checks, then frontend checks and compilation. Install OpenSSL for independent cryptographic checks; without it, some tests explicitly report that they were skipped.

To format code:

```bash
.local/dz-sign/venv/bin/ruff format demo/backend examples scripts
cd demo/frontend
npm run format
```

Tests cover encrypted keys, known digest vectors, certificate chains, altered and hybrid PDFs, expiration, HTTP origins and process cleanup. Add tests for reproducible defects or changed contracts, rather than copying the implementation into assertions.

## Review expectations

Describe the problem, resulting behavior and checks performed. Use English commit messages if a history is created. Changes to a limit, route or data handling must be reflected in all three handbooks. Keep limitations explicit; never turn an indeterminate result into success.

Original contributions use the MIT license. Respect [third-party notices](../../THIRD_PARTY_NOTICES.md) and do not include personal documents, private keys or secrets in material intended for sharing.
