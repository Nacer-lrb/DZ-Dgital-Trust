"""Server-controlled signing identity and bounded operation subprocesses."""

import os
import stat
from dataclasses import dataclass
from pathlib import Path

from fastapi import HTTPException

from .processes import run_json_worker

DEFAULT_IDENTITY = Path(__file__).resolve().parents[3] / ".local/dz-sign/app-identity"


@dataclass(frozen=True)
class SigningConfig:
    identity: Path = DEFAULT_IDENTITY
    password_file: Path | None = None

    @classmethod
    def from_environment(cls):
        identity = Path(os.environ.get("DZ_SIGN_IDENTITY_DIR", str(DEFAULT_IDENTITY))).resolve()
        secret = os.environ.get("DZ_SIGN_PASSWORD_FILE")
        return cls(identity=identity, password_file=Path(secret).resolve() if secret else None)

    @property
    def secret(self):
        return self.password_file or self.identity / "runtime/signer.secret"

    @property
    def trust_root(self):
        path = self.identity / "trust/root.cert.pem"
        return path if path.is_file() and not path.is_symlink() else None

    def ready(self):
        paths = [
            self.identity / "runtime/signer.key.pem",
            self.identity / "runtime/signer.cert.pem",
            self.identity / "runtime/intermediate.cert.pem",
            self.secret,
        ]
        if self.trust_root is None or not all(p.is_file() and not p.is_symlink() for p in paths):
            return False
        try:
            return all(
                not (stat.S_IMODE(p.stat().st_mode) & 0o077) for p in (paths[0], self.secret)
            )
        except OSError:
            return False


async def run_operation(config):
    result = await run_json_worker(Path(__file__).with_name("operation_worker.py"), payload=config)
    if not result["ok"]:
        messages = {
            "already_signed": "Ce PDF contient déjà une signature. Vous pouvez le vérifier directement.",
            "result_too_large": "La copie signée dépasse 10 Mio. Utilisez un PDF d’origine plus petit.",
        }
        raise HTTPException(
            422,
            messages.get(
                result.get("code"),
                "Le traitement a échoué. Vérifiez le document et la configuration de l’identité de test.",
            ),
        )
    return result
