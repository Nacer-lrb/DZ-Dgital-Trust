"""Check report semantics using real signatures and altered PDF bytes."""

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from create_demo_pdf import make_pdf
from pki_fixture import generate
from pyhanko.pdf_utils import generic
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from sign_pdf import sign_test_pdf
from verify_pdf import exit_code, verify_pdf


class VerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.directory = Path(cls.temp.name)
        cls.pki = cls.directory / "pki"
        password = b"signer-test-password-only"
        generate(cls.pki, b"authority-test-password-only", password)
        cls.source = cls.directory / "input.pdf"
        cls.signed = cls.directory / "signed.pdf"
        cls.root = cls.pki / "trust/root.cert.pem"
        make_pdf(cls.source)
        sign_test_pdf(cls.source, cls.signed, cls.pki, password)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_intact_offline_report(self):
        before = self.signed.read_bytes()
        with patch("socket.socket.connect", side_effect=AssertionError("Network forbidden")):
            report = verify_pdf(self.signed, self.root)
        self.assertEqual(exit_code(report), 0)
        signature = report["signatures"][0]
        self.assertEqual(signature["coverage"], "ENTIRE_FILE")
        self.assertEqual(signature["integrity"], "passed")
        self.assertEqual(signature["revocation"], "not_verified")
        self.assertEqual(signature["timestamp"], "not_verified")
        self.assertEqual(report["legal_qualification"], "not_assessed")
        self.assertEqual(self.signed.read_bytes(), before)

    def test_altered_covered_bytes(self):
        altered = self.directory / "altered.pdf"
        original = self.signed.read_bytes()
        changed = original.replace(b"Fictitious", b"Alteration", 1)
        self.assertNotEqual(changed, original)
        self.assertEqual(len(changed), len(original))
        altered.write_bytes(changed)
        report = verify_pdf(altered, self.root)
        self.assertEqual(report["outcome"], "checks_failed")
        self.assertEqual(report["signatures"][0]["integrity"], "failed")
        self.assertEqual(exit_code(report), 1)

    def test_no_anchor_does_not_mean_bad_integrity(self):
        with self.assertLogs("pyhanko.sign.validation", level="WARNING"):
            report = verify_pdf(self.signed)
        item = report["signatures"][0]
        self.assertEqual(item["integrity"], "passed")
        self.assertEqual(item["certificate_validation"], "not_established")
        self.assertIsNone(report["trust_root_sha256"])
        self.assertEqual(exit_code(report), 1)

    def test_expired_at_evaluation(self):
        future = datetime.now(UTC) + timedelta(days=31)
        with self.assertLogs("pyhanko.sign.validation", level="WARNING"):
            report = verify_pdf(self.signed, self.root, moment=future)
        self.assertEqual(
            report["signatures"][0]["certificate_period"]["at_evaluation"], "outside_period"
        )
        self.assertEqual(report["signatures"][0]["integrity"], "passed")
        self.assertEqual(exit_code(report), 1)

    def test_unsigned_and_invalid_pdf(self):
        report = verify_pdf(self.source, self.root)
        self.assertEqual(report["outcome"], "no_signature")
        self.assertEqual(report["signatures"], [])
        self.assertEqual(exit_code(report), 1)
        invalid = self.directory / "invalid.pdf"
        invalid.write_bytes(b"not a PDF")
        command = [
            sys.executable,
            str(Path(__file__).with_name("verify_pdf.py")),
            str(invalid),
            "--json",
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["outcome"], "indeterminate")

    def test_json_command(self):
        command = [
            sys.executable,
            str(Path(__file__).with_name("verify_pdf.py")),
            str(self.signed),
            "--trust-root",
            str(self.root),
            "--json",
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["outcome"], "checks_passed_with_limits")

    def test_later_revision_is_not_accepted_as_whole_file(self):
        revised = self.directory / "revised.pdf"
        with self.signed.open("rb") as source, revised.open("wb") as target:
            writer = IncrementalPdfFileWriter(source)
            writer.root[generic.pdf_name("/DZTestNote")] = generic.pdf_string("Later revision")
            writer.update_root()
            writer.write(target)
        report = verify_pdf(revised, self.root)
        self.assertNotEqual(report["outcome"], "checks_passed_with_limits")
        self.assertNotEqual(report["signatures"][0]["coverage"], "ENTIRE_FILE")
        self.assertNotEqual(exit_code(report), 0)


if __name__ == "__main__":
    unittest.main()
