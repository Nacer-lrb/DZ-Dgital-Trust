import asyncio
import os
from contextlib import asynccontextmanager, suppress
from typing import Literal
from urllib.parse import urlsplit

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .documents import MAX_FILE_BYTES, DocumentStore


class SignedResultInfo(BaseModel):
    id: str
    document_id: str
    name: str
    size_bytes: int
    sha256: str
    created_at: str
    expires_at: str
    normalized_before_signing: bool = False


class DocumentInfo(BaseModel):
    id: str
    name: str
    size_bytes: int
    sha256: str
    page_count: int
    created_at: str
    expires_at: str
    signed_result: SignedResultInfo | None = None


class SignRequest(BaseModel):
    confirm_test_signature: Literal[True]


class VerifyRequest(BaseModel):
    source: Literal["original", "signed"] = "original"


def create_app(*, store=None):
    frontend_origin = os.environ.get("DZ_SIGN_FRONTEND_ORIGIN", "http://127.0.0.1:3000")
    parsed = urlsplit(frontend_origin)
    if (
        parsed.scheme != "http"
        or parsed.hostname not in {"127.0.0.1", "localhost"}
        or parsed.path
        or parsed.query
        or parsed.fragment
        or parsed.username
        or parsed.password
    ):
        raise ValueError("DZ_SIGN_FRONTEND_ORIGIN doit être une origine HTTP locale sans chemin.")
    documents = store or DocumentStore()

    @asynccontextmanager
    async def lifespan(api):
        documents.start()

        async def cleanup_loop():
            while True:
                await asyncio.sleep(documents.settings.cleanup_interval)
                documents.cleanup()

        cleanup_task = asyncio.create_task(cleanup_loop())
        try:
            yield
        finally:
            cleanup_task.cancel()
            try:
                with suppress(asyncio.CancelledError):
                    await cleanup_task
            finally:
                documents.close()

    api = FastAPI(
        title="DZ Sign — démonstration locale",
        version="0.1.0",
        description="Documents temporaires, signature fictive de test et vérification hors ligne.",
        lifespan=lifespan,
    )
    api.state.documents = documents
    api.add_middleware(
        CORSMiddleware,
        allow_origins=[frontend_origin],
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Accept", "Content-Type"],
        allow_credentials=False,
    )
    api.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])

    @api.middleware("http")
    async def local_origin_only(request, call_next):
        origin = request.headers.get("origin")
        if origin is not None and origin != frontend_origin:
            return JSONResponse(status_code=403, content={"detail": "Origine non autorisée."})
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @api.get("/api/health", tags=["État"])
    async def health():
        return {
            "status": "ok",
            "service": "dz-sign",
            "version": "0.1.0",
            "mode": "local-demo",
            "stage": "sign-and-verify",
            "capabilities": {
                "upload": True,
                "sign": documents.signing_config.ready(),
                "verify": True,
            },
            "limits": {
                "max_upload_bytes": MAX_FILE_BYTES,
                "retention_seconds": documents.settings.retention_seconds,
            },
        }

    @api.get("/api/documents", response_model=list[DocumentInfo], tags=["Documents"])
    async def list_documents():
        return documents.list_documents()

    @api.post(
        "/api/documents",
        status_code=201,
        response_model=DocumentInfo,
        tags=["Documents"],
        openapi_extra={
            "requestBody": {
                "required": True,
                "content": {
                    "multipart/form-data": {
                        "schema": {
                            "type": "object",
                            "required": ["file"],
                            "properties": {"file": {"type": "string", "format": "binary"}},
                            "additionalProperties": False,
                        }
                    }
                },
            }
        },
    )
    async def import_document(request: Request):
        return await documents.import_document(request)

    @api.get("/api/documents/{identifier}", response_model=DocumentInfo, tags=["Documents"])
    async def document_info(identifier: str):
        return documents.metadata(documents.get(identifier))

    @api.get("/api/documents/{identifier}/download", tags=["Documents"])
    async def download_document(identifier: str):
        documents.get(identifier)
        data = (documents.settings.root / identifier / "original.pdf").read_bytes()
        return Response(
            data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'attachment; filename="document-original.pdf"',
            },
        )

    @api.delete("/api/documents/{identifier}", status_code=204, tags=["Documents"])
    async def delete_document(identifier: str):
        documents.get(identifier)
        documents.remove(identifier)
        return Response(status_code=204)

    @api.post(
        "/api/documents/{identifier}/sign", response_model=SignedResultInfo, tags=["Traitements"]
    )
    async def sign_document(identifier: str, confirmation: SignRequest):
        return await documents.sign_document(identifier)

    @api.post("/api/documents/{identifier}/verify", tags=["Traitements"])
    async def verify_document(identifier: str, options: VerifyRequest):
        return await documents.verify_document(identifier, options.source)

    @api.get("/api/results/{identifier}/download", tags=["Traitements"])
    async def download_result(identifier: str):
        _, path = documents.get_result(identifier)
        return Response(
            path.read_bytes(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'attachment; filename="document-signe-test.pdf"',
            },
        )

    return api


app = create_app()
