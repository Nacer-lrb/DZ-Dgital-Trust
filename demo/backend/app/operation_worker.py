"""Run a signing or validation task with server-owned configuration only."""

import json
import logging
import sys
from pathlib import Path

from pdf_worker import restrict_process

if __name__ == "__main__":
    restrict_process()
    logging.disable(logging.CRITICAL)
    examples = Path(__file__).resolve().parents[3] / "examples/pdf-signing"
    sys.path.insert(0, str(examples))
    try:
        config = json.loads(sys.stdin.read(16384))
        source = Path(config["input"])
        from verify_pdf import verify_pdf

        if config["action"] == "sign":
            from sign_pdf import MAX_BYTES, read_password, sign_test_pdf

            password = read_password(Path(config["password_file"]), "")
            destination = Path(config["output"])
            signing_result = sign_test_pdf(source, destination, Path(config["identity"]), password)
            if destination.stat().st_size > MAX_BYTES:
                result = {"ok": False, "code": "result_too_large"}
            else:
                result = {"ok": True, **signing_result}
        elif config["action"] == "verify":
            root = Path(config["trust_root"]) if config.get("trust_root") else None
            report = verify_pdf(source, root)
            for signature in report["signatures"]:
                if "error" in signature:
                    signature["error"] = signature["error"][:500]
            result = {"ok": True, "report": report}
        else:
            result = {"ok": False, "code": "unsupported_action"}
    except ValueError as error:
        message = str(error)
        code = "already_signed" if "sans signature" in message else "operation_failed"
        result = {"ok": False, "code": code}
    except Exception:
        result = {"ok": False, "code": "operation_failed"}
    print(json.dumps(result))
