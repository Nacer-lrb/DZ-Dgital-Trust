"""Bounded multipart imports and an ephemeral, single-process document store."""

import asyncio
import fcntl
import hashlib
import os
import re
import secrets
import shutil
import stat
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from fastapi import HTTPException, Request
from starlette.datastructures import UploadFile
from starlette.formparsers import MultiPartException, MultiPartParser

from .operations import SigningConfig, run_operation
from .processes import run_json_worker

MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_BODY_BYTES = MAX_FILE_BYTES + 64 * 1024
WORKSPACE = Path(__file__).resolve().parents[3] / ".local/dz-sign/uploads"
ID_PATTERN = re.compile(r"[0-9a-f]{32}\Z")


@dataclass(frozen=True)
class DocumentSettings:
    root: Path = WORKSPACE
    retention_seconds: float = 900
    operation_timeout: float = 30
    cleanup_interval: float = 60
    max_documents: int = 10


async def inspect_pdf(path):
    result = await run_json_worker(
        Path(__file__).with_name("pdf_worker.py"), str(path), output_limit=16384
    )
    if not result["ok"]:
        messages = {
            "invalid_pdf": "Ce fichier n’est pas un PDF lisible pris en charge.",
            "encrypted_pdf": "Les PDF chiffrés ne sont pas pris en charge dans cet atelier.",
            "empty_pdf": "Le PDF ne contient aucune page.",
        }
        raise HTTPException(
            422, messages.get(result.get("code"), "Le PDF ne peut pas être analysé.")
        )
    if type(result.get("page_count")) is not int or result["page_count"] < 1:
        raise HTTPException(422, "Le nombre de pages du PDF ne peut pas être établi.")
    return result


class DocumentStore:
    def __init__(
        self,
        settings=None,
        *,
        clock=time.time,
        monotonic=time.monotonic,
        inspector=inspect_pdf,
        signing_config=None,
        runner=run_operation,
    ):
        self.settings = settings or DocumentSettings()
        self.clock = clock
        self.monotonic = monotonic
        self.inspector = inspector
        self.signing_config = signing_config or SigningConfig.from_environment()
        self.runner = runner
        self.entries = {}
        self.results = {}
        self.processing = False
        self.active_identifier = None
        self.lock_file = None

    def start(self):
        root = self.settings.root
        root.mkdir(parents=True, mode=0o700, exist_ok=True)
        if root.is_symlink() or not root.is_dir() or stat.S_IMODE(root.stat().st_mode) & 0o077:
            raise RuntimeError(
                "Le dossier temporaire doit être privé (0700) et sans lien symbolique."
            )
        fd = os.open(root / ".lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        self.lock_file = os.fdopen(fd, "r+b")
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.lock_file.close()
            self.lock_file = None
            raise RuntimeError("Un autre processus utilise déjà le stockage temporaire.") from None
        # Only generated document directories are cleaned; unrelated paths stay intact.
        for child in root.iterdir():
            if ID_PATTERN.fullmatch(child.name) and child.is_dir() and not child.is_symlink():
                shutil.rmtree(child)

    def remove(self, identifier):
        if identifier == self.active_identifier:
            raise HTTPException(
                409, "Ce document est en cours de traitement. Réessayez après sa fin."
            )
        entry = self.entries.get(identifier)
        if entry is not None:
            try:
                shutil.rmtree(self.settings.root / identifier)
            except FileNotFoundError:
                pass
            if entry.get("signed_result"):
                self.results.pop(entry["signed_result"]["id"], None)
            self.entries.pop(identifier, None)

    def cleanup(self):
        for identifier, entry in list(self.entries.items()):
            if self.expired(entry) and identifier != self.active_identifier:
                self.remove(identifier)

    def expired(self, entry):
        return (
            self.clock() >= entry["expires_timestamp"]
            or self.monotonic() >= entry["expires_monotonic"]
        )

    def close(self):
        for identifier in list(self.entries):
            self.remove(identifier)
        if self.lock_file is not None:
            self.lock_file.close()
            self.lock_file = None

    def get(self, identifier):
        entry = self.entries.get(identifier) if ID_PATTERN.fullmatch(identifier) else None
        if entry is None:
            raise HTTPException(404, "Document introuvable ou déjà supprimé.")
        if self.expired(entry):
            if identifier != self.active_identifier:
                self.remove(identifier)
            raise HTTPException(410, "Le document a expiré. Importez-le à nouveau.")
        return entry

    @staticmethod
    def metadata(entry):
        return {
            key: value
            for key, value in entry.items()
            if key not in {"expires_timestamp", "expires_monotonic"}
        }

    async def import_document(self, request: Request):
        if self.processing:
            raise HTTPException(409, "Un traitement est déjà en cours. Réessayez dans un instant.")
        self.processing = True
        directory = None
        committed = False
        started_at = self.clock()
        started_monotonic = self.monotonic()
        try:
            async with asyncio.timeout(self.settings.operation_timeout):
                self.cleanup()
                if len(self.entries) >= self.settings.max_documents:
                    raise HTTPException(
                        429,
                        "L’atelier contient déjà dix documents. Supprimez-en un ou attendez leur expiration.",
                    )
                content_type = (
                    request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
                )
                if content_type != "multipart/form-data":
                    raise HTTPException(415, "Envoyez un seul fichier PDF dans le champ « file ».")
                content_length = request.headers.get("content-length")
                if content_length is not None:
                    try:
                        length = int(content_length)
                    except ValueError:
                        raise HTTPException(400, "Taille de requête incorrecte.") from None
                    if length < 0:
                        raise HTTPException(400, "Taille de requête incorrecte.")
                    if length > MAX_BODY_BYTES:
                        raise HTTPException(413, "Le PDF doit faire au maximum 10 Mio.")
                # Bound the stream before invoking the multipart parser or its spool.
                body = bytearray()
                async for chunk in request.stream():
                    if len(body) + len(chunk) > MAX_BODY_BYTES:
                        raise HTTPException(413, "Le PDF doit faire au maximum 10 Mio.")
                    body.extend(chunk)

                async def buffered_body():
                    yield bytes(body)

                parser = MultiPartParser(
                    request.headers, buffered_body(), max_files=1, max_fields=0
                )
                parser.spool_max_size = (
                    MAX_BODY_BYTES  # Bounded in-memory spool; no global temp files.
                )
                try:
                    form = await parser.parse()
                except MultiPartException:
                    raise HTTPException(
                        400, "Le formulaire doit contenir exactement un fichier nommé « file »."
                    ) from None
                except Exception:
                    # The pinned Starlette parser closes its spools on all failures.
                    raise HTTPException(400, "Le formulaire d’import est illisible.") from None
                try:
                    items = form.multi_items()
                    if (
                        len(items) != 1
                        or items[0][0] != "file"
                        or not isinstance(items[0][1], UploadFile)
                    ):
                        raise HTTPException(
                            400, "Le formulaire doit contenir exactement un fichier nommé « file »."
                        )
                    upload = items[0][1]
                    data = await upload.read(MAX_FILE_BYTES + 1)
                    if len(data) > MAX_FILE_BYTES:
                        raise HTTPException(413, "Le PDF doit faire au maximum 10 Mio.")
                    if not data:
                        raise HTTPException(422, "Le fichier est vide.")
                    filename = (upload.filename or "document.pdf").replace("\\", "/").split("/")[-1]
                    filename = (
                        "".join(c for c in filename if c.isprintable())[:180] or "document.pdf"
                    )
                finally:
                    await form.close()
                body.clear()
                identifier = secrets.token_hex(16)
                candidate = self.settings.root / identifier
                candidate.mkdir(mode=0o700)
                directory = candidate
                with (directory / "original.pdf").open("xb") as target:
                    os.chmod(target.name, 0o600)
                    target.write(data)
                inspected = await self.inspector(directory / "original.pdf")
                expiry = started_at + self.settings.retention_seconds
                monotonic_expiry = started_monotonic + self.settings.retention_seconds
                if self.clock() >= expiry or self.monotonic() >= monotonic_expiry:
                    raise HTTPException(410, "L’import a expiré. Réessayez.")
                entry = {
                    "id": identifier,
                    "name": filename,
                    "size_bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "page_count": inspected["page_count"],
                    "created_at": datetime.fromtimestamp(started_at, UTC).isoformat(),
                    "expires_at": datetime.fromtimestamp(expiry, UTC).isoformat(),
                    "expires_timestamp": expiry,
                    "expires_monotonic": monotonic_expiry,
                    "signed_result": None,
                }
                self.entries[identifier] = entry
                committed = True
                return self.metadata(entry)
        except TimeoutError:
            raise HTTPException(
                504, "L’import a dépassé 30 secondes. Réessayez avec un autre PDF."
            ) from None
        finally:
            if directory is not None and not committed:
                shutil.rmtree(directory, ignore_errors=True)
            self.processing = False

    def list_documents(self):
        self.cleanup()
        return [
            self.metadata(entry)
            for entry in reversed(list(self.entries.values()))
            if not self.expired(entry)
        ]

    def get_result(self, identifier):
        document_id = self.results.get(identifier) if ID_PATTERN.fullmatch(identifier) else None
        if document_id is None:
            raise HTTPException(404, "Copie signée introuvable ou expirée.")
        entry = self.get(document_id)
        return entry, self.settings.root / document_id / "signed.pdf"

    def begin_operation(self, identifier):
        if self.processing:
            raise HTTPException(409, "Un traitement est déjà en cours. Réessayez dans un instant.")
        entry = self.get(identifier)
        self.processing = True
        self.active_identifier = identifier
        return entry

    def finish_operation(self):
        self.active_identifier = None
        self.processing = False
        self.cleanup()

    async def sign_document(self, identifier):
        entry = self.get(identifier)
        if entry["signed_result"] is not None:
            return entry["signed_result"]
        if not self.signing_config.ready():
            raise HTTPException(
                503, "L’identité de signature de test n’est pas configurée sur ce poste."
            )
        self.begin_operation(identifier)
        destination = self.settings.root / identifier / "signed.pdf"
        published = False
        try:
            async with asyncio.timeout(self.settings.operation_timeout):
                operation_result = await self.runner(
                    {
                        "action": "sign",
                        "input": str(destination.with_name("original.pdf")),
                        "output": str(destination),
                        "identity": str(self.signing_config.identity),
                        "password_file": str(self.signing_config.secret),
                    }
                )
                self.get(identifier)  # Recheck expiry before publishing the result.
                data = destination.read_bytes()
                if len(data) > MAX_FILE_BYTES:
                    raise HTTPException(
                        413, "La copie signée dépasse 10 Mio. Utilisez un PDF plus petit."
                    )
                result_id = secrets.token_hex(16)
                if result_id in self.results:
                    raise HTTPException(500, "La copie n’a pas pu être enregistrée. Réessayez.")
                result = {
                    "id": result_id,
                    "document_id": identifier,
                    "name": f"{Path(entry['name']).stem}-signe-test.pdf",
                    "size_bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "created_at": datetime.fromtimestamp(self.clock(), UTC).isoformat(),
                    "expires_at": entry["expires_at"],
                    "normalized_before_signing": bool(
                        operation_result.get("normalized_before_signing", False)
                    ),
                }
                self.results[result_id] = identifier
                entry["signed_result"] = result
                published = True
                return result
        except TimeoutError:
            raise HTTPException(504, "La signature a dépassé le délai de 30 secondes.") from None
        finally:
            if not published:
                destination.unlink(missing_ok=True)
            self.finish_operation()

    async def verify_document(self, identifier, source="original"):
        entry = self.begin_operation(identifier)
        try:
            if source == "signed" and entry["signed_result"] is None:
                raise HTTPException(404, "Aucune copie signée n’est disponible pour ce document.")
            async with asyncio.timeout(self.settings.operation_timeout):
                root = self.signing_config.trust_root
                result = await self.runner(
                    {
                        "action": "verify",
                        "input": str(
                            self.settings.root
                            / identifier
                            / ("signed.pdf" if source == "signed" else "original.pdf")
                        ),
                        "trust_root": str(root) if root else None,
                    }
                )
                self.get(identifier)
                report = result["report"]
                report["document_id"] = identifier
                report["source"] = source
                return report
        except TimeoutError:
            raise HTTPException(504, "La vérification a dépassé le délai de 30 secondes.") from None
        finally:
            self.finish_operation()
