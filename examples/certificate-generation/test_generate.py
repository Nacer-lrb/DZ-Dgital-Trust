"""Integration checks: encrypted material, strict chain and failure cases."""

import shutil
import stat
import subprocess
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from generate import generate, read_password


class GenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temp.name) / "pki"
        cls.authority_password = b"authority-test-password-only"
        cls.signer_password = b"signer-test-password-only"
        generate(cls.output, cls.authority_password, cls.signer_password)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_private_material_and_permissions(self):
        for path in self.output.rglob("*"):
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o700 if path.is_dir() else 0o600)
        for relative, password in (
            ("generation/root.key.pem", self.authority_password),
            ("generation/intermediate.key.pem", self.authority_password),
            ("runtime/signer.key.pem", self.signer_password),
        ):
            data = (self.output / relative).read_bytes()
            self.assertTrue(data.startswith(b"-----BEGIN ENCRYPTED PRIVATE KEY-----"))
            self.assertEqual(serialization.load_pem_private_key(data, password).key_size, 3072)
            with self.assertRaises(ValueError):
                serialization.load_pem_private_key(data, b"incorrect-password")
        signer = serialization.load_pem_private_key(
            (self.output / "runtime/signer.key.pem").read_bytes(), self.signer_password
        )
        cert = x509.load_pem_x509_certificate(
            (self.output / "runtime/signer.cert.pem").read_bytes()
        )
        self.assertEqual(signer.public_key().public_numbers(), cert.public_key().public_numbers())
        self.assertFalse(cert.extensions.get_extension_for_class(x509.BasicConstraints).value.ca)
        self.assertEqual(
            list((self.output / "runtime").glob("*.key.pem")),
            [self.output / "runtime/signer.key.pem"],
        )

    @unittest.skipUnless(shutil.which("openssl"), "OpenSSL required for independent validation")
    def test_strict_chain_and_negative_cases(self):
        command = [
            "openssl",
            "verify",
            "-x509_strict",
            "-no-CApath",
            "-no-CAstore",
            "-CAfile",
            str(self.output / "trust/root.cert.pem"),
        ]
        intermediate = str(self.output / "runtime/intermediate.cert.pem")
        signer = str(self.output / "runtime/signer.cert.pem")
        valid = subprocess.run(command + ["-untrusted", intermediate, signer], capture_output=True)
        self.assertEqual(valid.returncode, 0, valid.stderr.decode())
        missing = subprocess.run(command + [signer], capture_output=True)
        self.assertNotEqual(missing.returncode, 0)
        future = str(int((datetime.now(UTC) + timedelta(days=31)).timestamp()))
        expired = subprocess.run(
            command + ["-attime", future, "-untrusted", intermediate, signer], capture_output=True
        )
        self.assertNotEqual(expired.returncode, 0)
        self.assertIn(b"expired", expired.stderr)

    def test_existing_destination_is_untouched(self):
        before = {
            p.relative_to(self.output): p.read_bytes()
            for p in self.output.rglob("*")
            if p.is_file()
        }
        with self.assertRaises(FileExistsError):
            generate(self.output, self.authority_password, self.signer_password)
        after = {
            p.relative_to(self.output): p.read_bytes()
            for p in self.output.rglob("*")
            if p.is_file()
        }
        self.assertEqual(before, after)

    def test_password_file_must_be_private(self):
        path = Path(self.temp.name) / "password"
        path.write_bytes(b"local-test-password-only\n")
        path.chmod(0o644)
        with self.assertRaises(ValueError):
            read_password(path, "")
        path.chmod(0o600)
        self.assertEqual(read_password(path, ""), b"local-test-password-only")


if __name__ == "__main__":
    unittest.main()
