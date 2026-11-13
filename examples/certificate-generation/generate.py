"""Generate a local, encrypted test PKI. Never use these identities in production."""

import argparse
import getpass
import json
import os
import shutil
import stat
import sys
import tempfile
import warnings
from datetime import UTC, datetime, timedelta
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

DEFAULT_OUTPUT = Path(__file__).resolve().parents[2] / ".local/dz-sign/pki"


def read_password(path, prompt):
    if path is None:
        with warnings.catch_warnings():
            warnings.simplefilter("error", getpass.GetPassWarning)
            value = getpass.getpass(prompt).encode("utf-8")
            confirmation = getpass.getpass("Confirmer la phrase secrète : ").encode("utf-8")
        if value != confirmation:
            raise ValueError("Les phrases secrètes ne correspondent pas.")
    else:
        # Open once, refuse links and inspect the actual opened file.
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, "rb") as source:
            info = os.fstat(source.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077:
                raise ValueError("Le fichier secret doit être un fichier régulier privé (0600).")
            value = source.read(4097)
        if len(value) > 4096:
            raise ValueError("Le fichier secret dépasse 4096 octets.")
        value = value.rstrip(b"\r\n")
    if len(value) < 16:
        raise ValueError("Utiliser une phrase secrète d’au moins 16 octets UTF-8.")
    return value


def name(common_name):
    return x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "DZ"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "DZ Digital Trust - TEST ONLY"),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ]
    )


def certificate(subject, key, issuer_name, issuer_key, now, days, ca, path_length):
    return (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer_name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=5))
        .not_valid_after(now + timedelta(days=days))
        .add_extension(x509.BasicConstraints(ca=ca, path_length=path_length), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=not ca,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=ca,
                crl_sign=ca,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(issuer_key.public_key()),
            critical=False,
        )
        .sign(issuer_key, hashes.SHA256())
    )


def write_private(path, data):
    with path.open("xb") as target:
        os.chmod(path, 0o600)
        target.write(data)


def generate(output, authority_password, signer_password):
    """Refuse existing destinations and roll back a failed publication."""
    if output.exists() or output.is_symlink():
        raise FileExistsError("Destination déjà présente ; aucun fichier n’a été remplacé.")
    output.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".pki-", dir=output.parent))
    try:
        for directory in ("generation", "runtime", "trust"):
            (staging / directory).mkdir(mode=0o700)
        now = datetime.now(UTC).replace(microsecond=0)
        root_key, intermediate_key, signer_key = [
            rsa.generate_private_key(public_exponent=65537, key_size=3072) for _ in range(3)
        ]
        root_name = name("DZ Root - TEST ONLY")
        intermediate_name = name("DZ Intermediate - TEST ONLY")
        root = certificate(root_name, root_key, root_name, root_key, now, 365, True, 1)
        intermediate = certificate(
            intermediate_name, intermediate_key, root_name, root_key, now, 180, True, 0
        )
        signer = certificate(
            name("Amel - TEST ONLY"),
            signer_key,
            intermediate_name,
            intermediate_key,
            now,
            30,
            False,
            None,
        )
        for relative, key, password in (
            ("generation/root.key.pem", root_key, authority_password),
            ("generation/intermediate.key.pem", intermediate_key, authority_password),
            ("runtime/signer.key.pem", signer_key, signer_password),
        ):
            write_private(
                staging / relative,
                key.private_bytes(
                    serialization.Encoding.PEM,
                    serialization.PrivateFormat.PKCS8,
                    serialization.BestAvailableEncryption(password),
                ),
            )
        for relative, cert in (
            ("trust/root.cert.pem", root),
            ("runtime/intermediate.cert.pem", intermediate),
            ("runtime/signer.cert.pem", signer),
        ):
            write_private(staging / relative, cert.public_bytes(serialization.Encoding.PEM))
        write_private(
            staging / "manifest.json",
            json.dumps(
                {
                    "purpose": "TEST ONLY - no legal qualification",
                    "generated_at": now.isoformat(),
                    "key_algorithm": "RSA-3072",
                    "certificate_signature": "SHA256 with RSA PKCS1v1.5",
                    "validity_days": {"root": 365, "intermediate": 180, "signer": 30},
                    "root_sha256": root.fingerprint(hashes.SHA256()).hex(),
                    "revocation": "not configured",
                    "timestamping": "not configured",
                },
                indent=2,
            ).encode()
            + b"\n",
        )
        # Reserve the final name exclusively, so even an empty existing directory
        # cannot be replaced. Remove the reservation if publication fails.
        output.mkdir(mode=0o700)
        try:
            for child in staging.iterdir():
                child.rename(output / child.name)
        except BaseException:
            shutil.rmtree(output)
            raise
    finally:
        shutil.rmtree(staging)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--authority-password-file", type=Path)
    parser.add_argument("--signer-password-file", type=Path)
    args = parser.parse_args()
    if os.name != "posix":
        parser.error("Cet exemple nécessite un système POSIX pour les permissions privées.")
    try:
        if args.output.exists() or args.output.is_symlink():
            raise FileExistsError("Destination déjà présente ; aucun fichier n’a été remplacé.")
        authorities = read_password(
            args.authority_password_file, "Phrase secrète des autorités de TEST : "
        )
        signer = read_password(args.signer_password_file, "Phrase secrète du signataire de TEST : ")
        if authorities == signer:
            raise ValueError("Utiliser deux phrases secrètes distinctes.")
        previous_umask = os.umask(0o077)
        try:
            generate(args.output, authorities, signer)
        finally:
            os.umask(previous_umask)
    except (OSError, ValueError, getpass.GetPassWarning) as error:
        print(f"Génération refusée : {error}", file=sys.stderr)
        return 1
    print(f"PKI de TEST générée dans {args.output}")
    print("Aucun service de révocation ou d’horodatage n’est configuré.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
