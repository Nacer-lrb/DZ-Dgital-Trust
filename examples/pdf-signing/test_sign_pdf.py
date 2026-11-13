"""End-to-end signing checks with ephemeral test keys and a synthetic PDF."""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from asn1crypto import cms
from create_demo_pdf import make_pdf
from pki_fixture import generate
from pyhanko.keys import load_cert_from_pemder
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign.validation import validate_pdf_signature
from pyhanko_certvalidator import ValidationContext
from sign_pdf import TEST_KEY_USAGE, sign_test_pdf


class SigningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.directory = Path(cls.temp.name)
        cls.pki = cls.directory / "pki"
        cls.password = b"signer-test-password-only"
        generate(cls.pki, b"authority-test-password-only", cls.password)
        cls.source = cls.directory / "input.pdf"
        make_pdf(cls.source)
        cls.original = cls.source.read_bytes()
        cls.output = cls.directory / "signed.pdf"
        # Any attempted network fetch during signing or verification must fail.
        with patch("socket.socket.connect", side_effect=AssertionError("Network forbidden")):
            sign_test_pdf(cls.source, cls.output, cls.pki, cls.password)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_signed_result_and_original(self):
        self.assertEqual(self.source.read_bytes(), self.original)
        with self.output.open("rb") as stream:
            reader = PdfFileReader(stream)
            self.assertEqual(len(reader.embedded_signatures), 1)
            signature = reader.embedded_signatures[0]
            self.assertEqual(signature.sig_object["/SubFilter"], "/ETSI.CAdES.detached")
            context = ValidationContext(
                trust_roots=[load_cert_from_pemder(str(self.pki / "trust/root.cert.pem"))],
                allow_fetching=False,
                revocation_mode="soft-fail",
            )
            status = validate_pdf_signature(
                signature, signer_validation_context=context, key_usage_settings=TEST_KEY_USAGE
            )
            self.assertTrue(status.intact and status.valid and status.trusted)

    def test_overwrite_refused(self):
        before = self.output.read_bytes()
        with self.assertRaises(ValueError):
            sign_test_pdf(self.source, self.output, self.pki, self.password)
        self.assertEqual(self.output.read_bytes(), before)
        with self.assertRaises(ValueError):
            sign_test_pdf(self.source, self.source, self.pki, self.password)
        self.assertEqual(self.source.read_bytes(), self.original)

    def test_wrong_password_leaves_no_output(self):
        output = self.directory / "wrong-password.pdf"
        with self.assertLogs("pyhanko.sign.signers.pdf_cms", level="ERROR"):
            with self.assertRaises(ValueError):
                sign_test_pdf(self.source, output, self.pki, b"wrong-password")
        self.assertFalse(output.exists())

    @unittest.skipUnless(
        shutil.which("openssl"), "OpenSSL required for independent CMS verification"
    )
    def test_independent_cms_verification_and_tampering(self):
        with self.output.open("rb") as stream:
            signature = PdfFileReader(stream).embedded_signatures[0]
            encoded = cms.ContentInfo(
                {"content_type": "signed_data", "content": signature.signed_data}
            ).dump()
            ranges = list(map(int, signature.byte_range))
        raw = self.output.read_bytes()
        covered = b"".join(
            raw[offset : offset + size] for offset, size in zip(ranges[::2], ranges[1::2])
        )
        signature_file = self.directory / "signature.der"
        content_file = self.directory / "covered.bin"
        signature_file.write_bytes(encoded)
        content_file.write_bytes(covered)
        command = [
            "openssl",
            "cms",
            "-verify",
            "-binary",
            "-inform",
            "DER",
            "-in",
            str(signature_file),
            "-content",
            str(content_file),
            "-noverify",
            "-out",
            os.devnull,
        ]
        result = subprocess.run(command, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        content_file.write_bytes(covered.replace(b"Fictitious", b"Alteration", 1))
        self.assertNotEqual(content_file.read_bytes(), covered)
        self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)

    def test_invalid_and_already_signed_input(self):
        bad = self.directory / "invalid.pdf"
        bad.write_bytes(b"not a PDF")
        output = self.directory / "invalid-output.pdf"
        with self.assertRaises(Exception):
            sign_test_pdf(bad, output, self.pki, self.password)
        self.assertFalse(output.exists())
        with self.assertRaises(ValueError):
            sign_test_pdf(self.output, output, self.pki, self.password)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
