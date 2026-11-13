"""Test the foundation API contract and local-origin boundary."""

import os
import unittest
from unittest.mock import patch

from app.main import create_app
from httpx import ASGITransport, AsyncClient


class HealthTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        with patch.dict(os.environ, {"DZ_SIGN_FRONTEND_ORIGIN": "http://127.0.0.1:3000"}):
            self.client = AsyncClient(
                transport=ASGITransport(app=create_app()), base_url="http://127.0.0.1:8000"
            )
        self.addAsyncCleanup(self.client.aclose)

    async def test_health_is_honest_about_capabilities(self):
        response = await self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["service"], "dz-sign")
        self.assertTrue(response.json()["capabilities"]["upload"])
        self.assertTrue(response.json()["capabilities"]["verify"])
        self.assertIsInstance(response.json()["capabilities"]["sign"], bool)
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertEqual((await self.client.post("/api/documents")).status_code, 415)

    async def test_exact_browser_origin(self):
        origin = "http://127.0.0.1:3000"
        allowed = await self.client.get("/api/health", headers={"Origin": origin})
        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(allowed.headers["access-control-allow-origin"], origin)
        rejected = await self.client.get(
            "/api/health", headers={"Origin": "https://unrelated.example"}
        )
        self.assertEqual(rejected.status_code, 403)
        self.assertNotIn("access-control-allow-origin", rejected.headers)

    async def test_preflight_and_host(self):
        response = await self.client.options(
            "/api/health",
            headers={"Origin": "http://127.0.0.1:3000", "Access-Control-Request-Method": "GET"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            (
                await self.client.get("/api/health", headers={"Host": "unrelated.example"})
            ).status_code,
            400,
        )

    async def test_openapi_exposes_only_implemented_operation(self):
        paths = (await self.client.get("/openapi.json")).json()["paths"]
        self.assertEqual(
            set(paths),
            {
                "/api/health",
                "/api/documents",
                "/api/documents/{identifier}",
                "/api/documents/{identifier}/download",
                "/api/documents/{identifier}/sign",
                "/api/documents/{identifier}/verify",
                "/api/results/{identifier}/download",
            },
        )

    async def test_remote_origin_configuration_rejected(self):
        with patch.dict(os.environ, {"DZ_SIGN_FRONTEND_ORIGIN": "https://public.example"}):
            with self.assertRaises(ValueError):
                create_app()


if __name__ == "__main__":
    unittest.main()
