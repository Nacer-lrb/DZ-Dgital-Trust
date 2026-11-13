"""Prepare an explicit, local TEST identity without overwriting existing data."""

import argparse
import os
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "examples/certificate-generation"))
from generate import generate, write_private

DEFAULT_OUTPUT = Path(__file__).resolve().parents[2] / ".local/dz-sign/app-identity"


def setup_identity(output):
    authority_password = secrets.token_urlsafe(40).encode()
    signer_password = secrets.token_urlsafe(40).encode()
    previous = os.umask(0o077)
    try:
        generate(output, authority_password, signer_password)
        write_private(output / "generation/authority.secret", authority_password + b"\n")
        write_private(output / "runtime/signer.secret", signer_password + b"\n")
    finally:
        os.umask(previous)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        setup_identity(args.output)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Préparation impossible : {error}\n")
    print(f"Identité fictive Amel - TEST ONLY préparée dans {args.output}")
    print("Les secrets locaux sont privés et restent hors du suivi Git.")
