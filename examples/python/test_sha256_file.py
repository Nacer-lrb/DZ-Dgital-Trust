"""Known-answer and command-line checks for the educational SHA-256 tool."""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from sha256_file import CHUNK_SIZE, sha256_file

SCRIPT = Path(__file__).with_name("sha256_file.py")
ABC = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
EMPTY = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


class HashTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.file = Path(self.temp.name) / "document de test.bin"

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True
        )

    def test_known_vectors(self):
        for content, expected in ((b"", EMPTY), (b"abc", ABC)):
            with self.subTest(content=content):
                self.file.write_bytes(content)
                self.assertEqual(sha256_file(self.file), expected)
                self.assertEqual(self.file.read_bytes(), content)

    def test_reference_and_altered_file(self):
        self.file.write_bytes(b"abc")
        self.assertEqual(self.run_cli(self.file, "--expect", ABC.upper()).returncode, 0)
        self.file.write_bytes(b"abd")
        result = self.run_cli(self.file, "--expect", ABC)
        self.assertEqual(result.returncode, 1)
        self.assertIn("différente", result.stderr)

    def test_invalid_reference_and_unreadable_input(self):
        self.file.write_bytes(b"abc")
        for reference in ("", "0" * 63, "g" * 64, "é" * 64):
            self.assertEqual(self.run_cli(self.file, "--expect", reference).returncode, 2)
        self.assertEqual(self.run_cli(self.file.parent / "absent").returncode, 2)
        self.assertEqual(self.run_cli(self.file.parent).returncode, 2)

    @unittest.skipUnless(shutil.which("openssl"), "OpenSSL required for independent comparison")
    def test_binary_file_across_multiple_chunks(self):
        content = bytes(range(256)) * (CHUNK_SIZE // 256 + 5) + b"\x00\xff\r\n"
        self.file.write_bytes(content)
        result = subprocess.run(
            ["openssl", "dgst", "-sha256", "-binary", str(self.file)],
            capture_output=True,
            check=True,
        )
        self.assertEqual(sha256_file(self.file), result.stdout.hex())
        self.assertEqual(self.file.read_bytes(), content)


if __name__ == "__main__":
    unittest.main()
