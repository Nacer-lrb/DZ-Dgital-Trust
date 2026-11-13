"""Worker protocol failures must remain controlled API errors."""

import tempfile
import unittest
from pathlib import Path

from app.processes import run_json_worker
from fastapi import HTTPException


class WorkerProtocolTests(unittest.IsolatedAsyncioTestCase):
    async def run_script(self, source, **kwargs):
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "worker.py"
            script.write_text(source)
            return await run_json_worker(script, **kwargs)

    async def test_invalid_json_is_an_explicit_rejection(self):
        with self.assertRaises(HTTPException) as caught:
            await self.run_script("print('not JSON')")
        self.assertEqual(caught.exception.status_code, 422)

    async def test_non_object_and_missing_status_are_rejected(self):
        for source in ["print('[]')", "print('{}')", "print('{\"ok\": 1}')"]:
            with self.subTest(source=source), self.assertRaises(HTTPException):
                await self.run_script(source)

    async def test_output_limit_is_enforced(self):
        with self.assertRaises(HTTPException):
            await self.run_script("print('x' * 10000)", output_limit=1024)

    async def test_large_response_is_read_to_completion(self):
        result = await self.run_script(
            "import json; print(json.dumps({'ok': True, 'value': 'x' * 100000}))"
        )
        self.assertEqual(len(result["value"]), 100000)


if __name__ == "__main__":
    unittest.main()
