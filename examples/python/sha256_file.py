"""Calculate or check the SHA-256 digest of a regular file, without modifying it."""

import argparse
import hashlib
import hmac
import os
import re
import stat
import sys
from pathlib import Path

CHUNK_SIZE = 1024 * 1024


def expected_digest(value):
    if re.fullmatch(r"[0-9a-fA-F]{64}", value) is None:
        raise argparse.ArgumentTypeError(
            "L’empreinte doit contenir exactement 64 caractères hexadécimaux."
        )
    return value.lower()


def sha256_file(path):
    # Non-blocking opening prevents a named pipe from hanging before the type check.
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NONBLOCK), "rb") as source:
        before = os.fstat(source.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise ValueError("Le chemin doit désigner un fichier régulier.")
        digest = hashlib.sha256()
        total = 0
        while chunk := source.read(CHUNK_SIZE):
            digest.update(chunk)
            total += len(chunk)
        after = os.fstat(source.fileno())
        if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        ) or total != before.st_size:
            raise ValueError(
                "Le fichier a changé pendant la lecture ; recommencer sur une copie stable."
            )
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path, help="Fichier à lire, sans modification")
    parser.add_argument(
        "--expect",
        type=expected_digest,
        help="Empreinte de référence fiable, 64 caractères hexadécimaux",
    )
    args = parser.parse_args()
    try:
        actual = sha256_file(args.file)
    except (OSError, ValueError) as error:
        print(f"Calcul impossible : {error}", file=sys.stderr)
        return 2
    print(actual)
    if args.expect is None:
        return 0
    if hmac.compare_digest(actual, args.expect):
        print("Empreinte conforme à la référence.")
        return 0
    print("Empreinte différente de la référence.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
