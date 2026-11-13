"""Report local PDF signature checks without network fetching or legal claims."""

import argparse
import hashlib
import io
import json
import logging
import os
import stat
import sys
from datetime import UTC, datetime
from pathlib import Path

from pyhanko.keys import load_cert_from_pemder
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign.validation import validate_pdf_signature
from pyhanko.sign.validation.status import SignatureCoverageLevel
from pyhanko_certvalidator import ValidationContext
from sign_pdf import MAX_BYTES, TEST_KEY_USAGE


def verify_pdf(source, trust_root=None, moment=None):
    moment = moment or datetime.now(UTC)
    if moment.tzinfo is None:
        raise ValueError("La date d’évaluation doit inclure un fuseau horaire.")
    moment = moment.astimezone(UTC)
    with os.fdopen(os.open(source, os.O_RDONLY | os.O_NONBLOCK), "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError("L’entrée doit être un fichier régulier.")
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("Le PDF dépasse la limite de 10 Mio.")
    root = load_cert_from_pemder(str(trust_root)) if trust_root else None
    reader = PdfFileReader(io.BytesIO(data), strict=True)
    if reader.security_handler is not None:
        raise ValueError("Les PDF chiffrés ne sont pas pris en charge.")
    report = {
        "schema_version": 1,
        "evaluated_at": moment.isoformat(),
        "file_sha256": hashlib.sha256(data).hexdigest(),
        "trust_root_sha256": hashlib.sha256(root.dump()).hexdigest() if root else None,
        "policy": "local-test-digitalSignature-v1",
        "network_fetching": False,
        "legal_qualification": "not_assessed",
        "signatures": [],
    }
    for signature in reader.embedded_signatures:
        cert = signature.signer_cert
        validity = cert["tbs_certificate"]["validity"]
        start = validity["not_before"].native
        end = validity["not_after"].native
        item = {
            "field": signature.field_name,
            "subject": cert.subject.human_friendly,
            "issuer": cert.issuer.human_friendly,
            "serial_number": str(cert.serial_number),
            "certificate_sha256": hashlib.sha256(cert.dump()).hexdigest(),
            "certificate_period": {
                "not_before": start.isoformat(),
                "not_after": end.isoformat(),
                "at_evaluation": "within_period" if start <= moment <= end else "outside_period",
            },
            "integrity": "indeterminate",
            "cms_signature": "indeterminate",
            "certificate_validation": "indeterminate",
            "coverage": "indeterminate",
            "modification_level": "indeterminate",
            "pdf_permissions_ok": None,
            "revocation": "not_verified",
            "timestamp": "not_verified",
            "outcome": "indeterminate",
        }
        try:
            context = ValidationContext(
                # An empty list deliberately disables system/default trust roots.
                trust_roots=[root] if root else [],
                moment=moment,
                allow_fetching=False,
                revocation_mode="soft-fail",
            )
            status = validate_pdf_signature(
                signature,
                signer_validation_context=context,
                key_usage_settings=TEST_KEY_USAGE,
            )
            item.update(
                {
                    "integrity": "passed" if status.intact else "failed",
                    "cms_signature": "passed" if status.valid else "failed",
                    "certificate_validation": "passed_local_policy"
                    if status.trusted
                    else "not_established",
                    "coverage": status.coverage.name if status.coverage else "indeterminate",
                    "modification_level": status.modification_level.name
                    if status.modification_level is not None
                    else "indeterminate",
                    "pdf_permissions_ok": status.docmdp_ok,
                }
            )
            if (
                not status.intact
                or not status.valid
                or not status.trusted
                or item["certificate_period"]["at_evaluation"] != "within_period"
            ):
                item["outcome"] = "checks_failed"
            elif status.coverage != SignatureCoverageLevel.ENTIRE_FILE or status.docmdp_ok is False:
                item["outcome"] = "needs_review"
            else:
                item["outcome"] = "checks_passed_with_limits"
        except Exception as error:
            # A failed analysis is not evidence of a cryptographically bad signature.
            item["error"] = f"{type(error).__name__}: {error}"
        report["signatures"].append(item)
    outcomes = [item["outcome"] for item in report["signatures"]]
    if not outcomes:
        report["outcome"] = "no_signature"
    elif "indeterminate" in outcomes:
        report["outcome"] = "indeterminate"
    elif "checks_failed" in outcomes:
        report["outcome"] = "checks_failed"
    elif "needs_review" in outcomes:
        report["outcome"] = "needs_review"
    else:
        report["outcome"] = "checks_passed_with_limits"
    return report


def exit_code(report):
    if report["outcome"] == "checks_passed_with_limits":
        return 0
    return 2 if report["outcome"] == "indeterminate" else 1


def print_report(report):
    print(f"Évaluation UTC : {report['evaluated_at']}")
    print(f"SHA-256 du PDF : {report['file_sha256']}")
    print(f"Ancre approuvée (SHA-256) : {report['trust_root_sha256'] or 'aucune'}")
    print(f"Signatures détectées : {len(report['signatures'])}")
    labels = {
        "checks_passed_with_limits": "Contrôles locaux réussis, avec limites",
        "checks_failed": "Un ou plusieurs contrôles ont échoué",
        "needs_review": "Révisions ou permissions PDF à examiner",
        "indeterminate": "Analyse impossible à conclure",
        "no_signature": "Aucune signature cryptographique détectée",
    }
    for number, item in enumerate(report["signatures"], 1):
        print(f"\nSignature {number} — {item['field']}")
        print(f"  Sujet du certificat : {item['subject']}")
        print(f"  Intégrité des données couvertes : {item['integrity']}")
        print(f"  Signature CMS : {item['cms_signature']}")
        print(f"  Validation du certificat : {item['certificate_validation']}")
        print(f"  Période à la date d’évaluation : {item['certificate_period']['at_evaluation']}")
        print(f"  Couverture PDF : {item['coverage']}")
        print(f"  Modifications : {item['modification_level']}")
        print(f"  Résultat : {labels[item['outcome']]}")
        if "error" in item:
            print(f"  Détail : {item['error']}")
    print(f"\nRésultat du document : {labels[report['outcome']]}")
    print("Révocation et horodatage : non vérifiés par cette commande.")
    print("Aucune qualification juridique ni validation historique n’est établie.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument(
        "--trust-root", type=Path, help="Certificat racine explicitement approuvé pour cet essai"
    )
    parser.add_argument("--json", action="store_true", help="Rapport JSON sur la sortie standard")
    args = parser.parse_args()
    logging.basicConfig(level=logging.CRITICAL)
    try:
        report = verify_pdf(args.input, args.trust_root)
    except Exception as error:
        message = f"{type(error).__name__}: {error}"
        if args.json:
            print(
                json.dumps(
                    {"schema_version": 1, "outcome": "indeterminate", "error": message},
                    ensure_ascii=False,
                )
            )
        else:
            print(f"Vérification impossible : {message}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_report(report)
    return exit_code(report)


if __name__ == "__main__":
    raise SystemExit(main())
