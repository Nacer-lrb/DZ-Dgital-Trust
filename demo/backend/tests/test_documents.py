"""Import lifecycle, stream bounds and actual subprocess PDF inspection."""

import asyncio
import hashlib
import io
import re
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.documents import (
    MAX_BODY_BYTES,
    MAX_FILE_BYTES,
    DocumentSettings,
    DocumentStore,
    inspect_pdf,
)
from app.main import create_app
from httpx import ASGITransport, AsyncClient
from pyhanko.pdf_utils import generic
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.pdf_utils.writer import PdfFileWriter


def pdf_bytes(encrypted=False):
    writer = PdfFileWriter()
    content = writer.add_object(generic.StreamObject(stream_data=b"% Fictitious test PDF\n"))
    writer.insert_page(
        generic.DictionaryObject(
            {
                generic.pdf_name("/Type"): generic.pdf_name("/Page"),
                generic.pdf_name("/MediaBox"): generic.ArrayObject(
                    [generic.NumberObject(n) for n in (0, 0, 100, 100)]
                ),
                generic.pdf_name("/Resources"): generic.DictionaryObject(),
                generic.pdf_name("/Contents"): content,
            }
        )
    )
    if encrypted:
        writer.encrypt("owner-test-password", "reader-test-password")
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def hybrid_pdf_bytes():
    data = pdf_bytes()
    reader = PdfFileReader(io.BytesIO(data), strict=True)
    stream_offset = int(re.findall(rb"startxref\s+(\d+)\s+%%EOF", data)[-1])
    objects = {
        int(match[1]): (match.start(), int(match[2]))
        for match in re.finditer(rb"(?m)^(\d+) (\d+) obj\b", data)
    }
    count = max(objects) + 1
    table = [f"xref\n0 {count}\n".encode(), b"0000000000 65535 f \n"]
    for number in range(1, count):
        if number in objects:
            offset, generation = objects[number]
            table.append(f"{offset:010} {generation:05} n \n".encode())
        else:
            table.append(b"0000000000 00000 f \n")
    root = reader.root_ref
    trailer = f"trailer\n<< /Size {count} /Root {root.idnum} {root.generation} R /XRefStm {stream_offset} >>\nstartxref\n{len(data)}\n%%EOF\n"
    return data + b"".join(table) + trailer.encode()


async def quick_inspector(path):
    return {"ok": True, "page_count": 1}


class DocumentTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.now = 1794567600.0
        self.root = Path(self.temp.name) / "uploads"
        self.store = DocumentStore(
            DocumentSettings(root=self.root, cleanup_interval=0.02),
            clock=lambda: self.now,
            inspector=quick_inspector,
        )
        self.app = create_app(store=self.store)
        self.lifespan = self.app.router.lifespan_context(self.app)
        await self.lifespan.__aenter__()
        self.addAsyncCleanup(self.lifespan.__aexit__, None, None, None)
        self.client = AsyncClient(
            transport=ASGITransport(app=self.app), base_url="http://127.0.0.1:8000"
        )
        self.addAsyncCleanup(self.client.aclose)

    async def upload(self, data=b"%PDF-test", name="attestation.pdf"):
        return await self.client.post(
            "/api/documents", files={"file": (name, data, "application/pdf")}
        )

    def document_directories(self):
        return [path for path in self.root.iterdir() if path.is_dir()]

    async def test_import_consult_download_delete(self):
        original = pdf_bytes()
        response = await self.upload(original, name="../../attestation.pdf")
        self.assertEqual(response.status_code, 201, response.text)
        info = response.json()
        self.assertEqual(info["name"], "attestation.pdf")
        self.assertEqual(info["sha256"], hashlib.sha256(original).hexdigest())
        self.assertEqual(info["size_bytes"], len(original))
        self.assertEqual(info["page_count"], 1)
        identifier = info["id"]
        path = self.root / identifier / "original.pdf"
        self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(path.parent.stat().st_mode), 0o700)
        self.assertEqual((await self.client.get(f"/api/documents/{identifier}")).json(), info)
        download = await self.client.get(f"/api/documents/{identifier}/download")
        self.assertEqual(download.content, original)
        self.assertIn("attachment", download.headers["content-disposition"])
        self.assertEqual(download.headers["cache-control"], "no-store")
        self.assertEqual(
            (await self.client.delete(f"/api/documents/{identifier}")).status_code, 204
        )
        self.assertFalse(path.exists())
        self.assertEqual((await self.client.get(f"/api/documents/{identifier}")).status_code, 404)

    async def test_actual_pdf_worker_and_invalid_content(self):
        self.store.inspector = inspect_pdf
        accepted = await self.upload(pdf_bytes(), name="not-a-pdf-extension.txt")
        self.assertEqual(accepted.status_code, 201, accepted.text)
        self.assertEqual(accepted.json()["page_count"], 1)
        rejected = await self.upload(b"not a PDF", name="looks-valid.pdf")
        self.assertEqual(rejected.status_code, 422)
        self.assertEqual(len(self.document_directories()), 1)
        encrypted = await self.upload(pdf_bytes(encrypted=True))
        self.assertEqual(encrypted.status_code, 422)
        self.assertIn("chiffrés", encrypted.json()["detail"])

    async def test_size_and_multipart_limits(self):
        response = await self.upload(b"x" * (MAX_FILE_BYTES + 1))
        self.assertEqual(response.status_code, 413)
        self.assertEqual(self.document_directories(), [])
        self.assertEqual((await self.upload(b"")).status_code, 422)
        duplicate = await self.client.post(
            "/api/documents", files=[("file", ("a.pdf", b"abc")), ("file", ("b.pdf", b"def"))]
        )
        self.assertEqual(duplicate.status_code, 400)
        self.assertEqual(
            (
                await self.client.post("/api/documents", files={"wrong": ("a.pdf", b"abc")})
            ).status_code,
            400,
        )
        self.assertEqual(
            (await self.client.post("/api/documents", content=b"abc")).status_code, 415
        )

    async def test_chunked_body_is_bounded_without_content_length(self):
        async def content():
            yield b"x" * MAX_BODY_BYTES
            yield b"x"

        response = await self.client.post(
            "/api/documents",
            content=content(),
            headers={"Content-Type": "multipart/form-data; boundary=test"},
        )
        self.assertEqual(response.status_code, 413)
        self.assertEqual(self.document_directories(), [])

    async def test_expiry_is_checked_before_download(self):
        identifier = (await self.upload()).json()["id"]
        self.now += 901
        self.assertEqual(
            (await self.client.get(f"/api/documents/{identifier}/download")).status_code, 410
        )
        self.assertFalse((self.root / identifier).exists())

    async def test_periodic_cleanup(self):
        identifier = (await self.upload()).json()["id"]
        self.now += 901
        await asyncio.sleep(0.06)
        self.assertFalse((self.root / identifier).exists())
        self.assertEqual(self.store.entries, {})

    async def test_wall_clock_rewind_cannot_extend_retention(self):
        identifier = (await self.upload()).json()["id"]
        deadline = self.store.entries[identifier]["expires_monotonic"]
        self.now -= 3600
        with patch.object(self.store, "monotonic", return_value=deadline + 1):
            response = await self.client.get(f"/api/documents/{identifier}")
        self.assertEqual(response.status_code, 410)
        self.assertFalse((self.root / identifier).exists())

    async def test_identifier_collision_does_not_remove_existing_document(self):
        info = (await self.upload(b"original")).json()
        path = self.root / info["id"] / "original.pdf"
        with patch("app.documents.secrets.token_hex", return_value=info["id"]):
            with self.assertRaises(FileExistsError):
                await self.upload(b"replacement")
        self.assertEqual(path.read_bytes(), b"original")
        self.assertEqual(self.store.metadata(self.store.get(info["id"])), info)

    async def test_failed_analysis_and_timeout_clean_partial_files(self):
        async def failure(path):
            raise RuntimeError("simulated worker failure")

        self.store.inspector = failure
        with self.assertRaises(RuntimeError):
            await self.upload()
        self.assertFalse(self.store.processing)
        self.assertEqual(self.document_directories(), [])

        async def slow(path):
            await asyncio.sleep(10)

        self.store.inspector = slow
        with patch.object(
            self.store, "settings", DocumentSettings(root=self.root, operation_timeout=0.02)
        ):
            response = await self.upload()
        self.assertEqual(response.status_code, 504)
        self.assertFalse(self.store.processing)
        self.assertEqual(self.document_directories(), [])

    async def test_busy_import_and_quota(self):
        self.store.processing = True
        self.assertEqual((await self.upload()).status_code, 409)
        self.store.processing = False
        await self.upload()
        with patch.object(
            self.store, "settings", DocumentSettings(root=self.root, max_documents=1)
        ):
            self.assertEqual((await self.upload()).status_code, 429)

    async def test_bad_ids_and_origin(self):
        self.assertEqual((await self.client.get("/api/documents/not-an-id")).status_code, 404)
        rejected = await self.client.post(
            "/api/documents",
            files={"file": ("a.pdf", b"abc")},
            headers={"Origin": "https://unrelated.example"},
        )
        self.assertEqual(rejected.status_code, 403)
        self.assertEqual(self.document_directories(), [])


class StoreAndProcessTests(unittest.IsolatedAsyncioTestCase):
    async def test_startup_removes_only_generated_directories_and_locks_store(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            orphan = root / ("a" * 32)
            orphan.mkdir()
            (orphan / "original.pdf").write_bytes(b"old")
            unrelated = root / "notes"
            unrelated.mkdir()
            store = DocumentStore(DocumentSettings(root=root))
            store.start()
            try:
                self.assertFalse(orphan.exists())
                self.assertTrue(unrelated.exists())
                with self.assertRaises(RuntimeError):
                    DocumentStore(DocumentSettings(root=root)).start()
            finally:
                store.close()

    async def test_cancelled_worker_is_killed_and_reaped(self):
        original_spawn = asyncio.create_subprocess_exec
        spawned = []

        async def slow_spawn(*args, **kwargs):
            process = await original_spawn(
                sys.executable, "-c", "import time; time.sleep(30)", **kwargs
            )
            spawned.append(process)
            return process

        with patch("app.documents.asyncio.create_subprocess_exec", side_effect=slow_spawn):
            with self.assertRaises(TimeoutError):
                await asyncio.wait_for(inspect_pdf(Path("unused.pdf")), timeout=0.1)
        self.assertEqual(len(spawned), 1)
        self.assertIsNotNone(spawned[0].returncode)


if __name__ == "__main__":
    unittest.main()
