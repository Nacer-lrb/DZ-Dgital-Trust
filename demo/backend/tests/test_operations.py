"""Real signing and verification through HTTP, including failures and expiry."""

import asyncio
import hashlib
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from app.documents import DocumentSettings, DocumentStore
from app.main import create_app
from app.operations import SigningConfig, run_operation
from httpx import ASGITransport, AsyncClient
from setup_demo import setup_identity
from test_documents import hybrid_pdf_bytes, pdf_bytes


class OperationTests(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.identity_temp = tempfile.TemporaryDirectory()
        cls.identity = Path(cls.identity_temp.name) / "identity"
        setup_identity(cls.identity)

    @classmethod
    def tearDownClass(cls):
        cls.identity_temp.cleanup()

    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = DocumentStore(
            DocumentSettings(root=Path(self.temp.name) / "uploads"),
            signing_config=SigningConfig(identity=self.identity),
        )
        self.api = create_app(store=self.store)
        self.context = self.api.router.lifespan_context(self.api)
        await self.context.__aenter__()
        self.addAsyncCleanup(self.context.__aexit__, None, None, None)
        self.client = AsyncClient(
            transport=ASGITransport(app=self.api), base_url="http://127.0.0.1:8000"
        )
        self.addAsyncCleanup(self.client.aclose)
        self.original = pdf_bytes()
        response = await self.client.post(
            "/api/documents", files={"file": ("attestation.pdf", self.original)}
        )
        self.assertEqual(response.status_code, 201, response.text)
        self.document = response.json()
        self.path = f"/api/documents/{self.document['id']}"

    async def sign(self):
        return await self.client.post(self.path + "/sign", json={"confirm_test_signature": True})

    async def test_real_signature_verification_and_deletion(self):
        response = await self.sign()
        self.assertEqual(response.status_code, 200, response.text)
        signed = response.json()
        self.assertEqual(signed["expires_at"], self.document["expires_at"])
        binary = await self.client.get(f"/api/results/{signed['id']}/download")
        self.assertEqual(binary.status_code, 200)
        self.assertEqual(hashlib.sha256(binary.content).hexdigest(), signed["sha256"])
        self.assertEqual((await self.client.get(self.path + "/download")).content, self.original)
        report = await self.client.post(self.path + "/verify", json={"source": "signed"})
        self.assertEqual(report.status_code, 200, report.text)
        data = report.json()
        self.assertEqual(data["outcome"], "checks_passed_with_limits")
        self.assertEqual(data["signatures"][0]["revocation"], "not_verified")
        self.assertEqual(data["signatures"][0]["timestamp"], "not_verified")
        self.assertNotIn("signer.secret", json.dumps(data))
        self.assertEqual((await self.sign()).json()["id"], signed["id"])
        self.assertEqual(
            (await self.client.get("/api/documents")).json()[0]["signed_result"]["id"], signed["id"]
        )
        self.assertEqual((await self.client.delete(self.path)).status_code, 204)
        self.assertEqual(
            (await self.client.get(f"/api/results/{signed['id']}/download")).status_code, 404
        )

    async def test_original_unsigned_and_missing_copy(self):
        report = await self.client.post(self.path + "/verify", json={"source": "original"})
        self.assertEqual(report.status_code, 200)
        self.assertEqual(report.json()["outcome"], "no_signature")
        self.assertEqual(
            (await self.client.post(self.path + "/verify", json={"source": "signed"})).status_code,
            404,
        )
        self.assertEqual(
            (
                await self.client.post(self.path + "/verify", json={"source": "../../elsewhere"})
            ).status_code,
            422,
        )

    async def test_hybrid_pdf_is_rewritten_only_in_the_signed_copy(self):
        import io

        from pyhanko.pdf_utils.reader import PdfFileReader

        hybrid = hybrid_pdf_bytes()
        self.assertTrue(PdfFileReader(io.BytesIO(hybrid), strict=True).xrefs.hybrid_xrefs_present)
        imported = await self.client.post("/api/documents", files={"file": ("hybride.pdf", hybrid)})
        self.assertEqual(imported.status_code, 201, imported.text)
        path = f"/api/documents/{imported.json()['id']}"
        signed = await self.client.post(path + "/sign", json={"confirm_test_signature": True})
        self.assertEqual(signed.status_code, 200, signed.text)
        self.assertTrue(signed.json()["normalized_before_signing"])
        self.assertEqual((await self.client.get(path + "/download")).content, hybrid)
        result = await self.client.post(path + "/verify", json={"source": "signed"})
        self.assertEqual(result.json()["outcome"], "checks_passed_with_limits")

    async def test_confirmation_and_missing_configuration(self):
        self.assertEqual((await self.client.post(self.path + "/sign", json={})).status_code, 422)
        self.assertEqual(
            (
                await self.client.post(self.path + "/sign", json={"confirm_test_signature": False})
            ).status_code,
            422,
        )
        self.store.signing_config = SigningConfig(identity=Path(self.temp.name) / "missing")
        self.assertEqual((await self.sign()).status_code, 503)
        health = (await self.client.get("/api/health")).json()
        self.assertFalse(health["capabilities"]["sign"])
        self.assertTrue(health["capabilities"]["verify"])

    async def test_tampered_pdf_and_unapproved_root(self):
        signed = (await self.sign()).json()
        binary = (await self.client.get(f"/api/results/{signed['id']}/download")).content
        changed = binary.replace(b"Fictitious", b"Alteration", 1)
        self.assertNotEqual(binary, changed)
        imported = await self.client.post(
            "/api/documents", files={"file": ("modifie.pdf", changed)}
        )
        self.assertEqual(imported.status_code, 201, imported.text)
        result = await self.client.post(
            f"/api/documents/{imported.json()['id']}/verify", json={"source": "original"}
        )
        self.assertEqual(result.json()["outcome"], "checks_failed")
        self.assertEqual(result.json()["signatures"][0]["integrity"], "failed")
        self.store.signing_config = SigningConfig(identity=Path(self.temp.name) / "no-trust")
        result = await self.client.post(self.path + "/verify", json={"source": "signed"})
        self.assertEqual(result.json()["signatures"][0]["integrity"], "passed")
        self.assertEqual(
            result.json()["signatures"][0]["certificate_validation"], "not_established"
        )

    async def test_incorrect_secret_does_not_publish_partial_result(self):
        secret = Path(self.temp.name) / "wrong.secret"
        secret.write_bytes(b"incorrect-test-password-only")
        secret.chmod(0o600)
        self.store.signing_config = SigningConfig(identity=self.identity, password_file=secret)
        self.assertEqual((await self.sign()).status_code, 422)
        self.assertEqual(self.store.results, {})
        self.assertFalse((self.store.settings.root / self.document["id"] / "signed.pdf").exists())

    async def test_timeout_removes_partial_copy(self):
        async def slow(config):
            Path(config["output"]).write_bytes(b"partial")
            await asyncio.sleep(30)

        self.store.runner = slow
        self.store.settings = replace(self.store.settings, operation_timeout=0.03)
        self.assertEqual((await self.sign()).status_code, 504)
        self.assertFalse((self.store.settings.root / self.document["id"] / "signed.pdf").exists())
        self.assertFalse(self.store.processing)

    async def test_expiry_removes_signed_result_and_original(self):
        result = (await self.sign()).json()
        deadline = self.store.entries[self.document["id"]]["expires_timestamp"]
        self.store.clock = lambda: deadline + 1
        response = await self.client.get(f"/api/results/{result['id']}/download")
        self.assertEqual(response.status_code, 410)
        self.assertEqual(self.store.results, {})
        self.assertFalse((self.store.settings.root / self.document["id"]).exists())

    async def test_active_operation_pins_files_but_does_not_extend_expiry(self):
        entered, release = asyncio.Event(), asyncio.Event()

        async def delayed(config):
            entered.set()
            await release.wait()
            return await run_operation(config)

        self.store.runner = delayed
        task = asyncio.create_task(
            self.client.post(self.path + "/verify", json={"source": "original"})
        )
        await asyncio.wait_for(entered.wait(), 2)
        self.assertEqual((await self.client.delete(self.path)).status_code, 409)
        self.store.clock = lambda: self.store.entries[self.document["id"]]["expires_timestamp"] + 1
        self.store.cleanup()
        self.assertTrue((self.store.settings.root / self.document["id"] / "original.pdf").exists())
        release.set()
        self.assertEqual((await task).status_code, 410)
        self.assertEqual(self.store.entries, {})


if __name__ == "__main__":
    unittest.main()
