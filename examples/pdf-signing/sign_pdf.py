"""Sign a local test PDF with the generated test identity; preserve the original."""

import argparse
import io
import os
import stat
import sys
from pathlib import Path

from pyhanko.keys import load_cert_from_pemder
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.pdf_utils.writer import copy_into_new_writer
from pyhanko.sign import fields, signers
from pyhanko.sign.validation import validate_pdf_signature
from pyhanko.sign.validation.settings import KeyUsageConstraints
from pyhanko_certvalidator import ValidationContext

# Reuse the password handling and private-file checks of the PKI example.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "certificate-generation"))
from generate import read_password

DEFAULT_PKI = Path(__file__).resolve().parents[2] / ".local/dz-sign/pki"
MAX_BYTES = 10 * 1024 * 1024
TEST_KEY_USAGE = KeyUsageConstraints(key_usage={"digital_signature"})


def sign_test_pdf(source, output, pki, password):
    if output.exists() or output.is_symlink():
        raise ValueError("La sortie existe déjà ; aucun fichier n’a été remplacé.")
    with os.fdopen(os.open(source, os.O_RDONLY | os.O_NONBLOCK), "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError("L’entrée doit être un fichier régulier.")
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("Le PDF dépasse la limite de 10 Mio.")
    reader = PdfFileReader(io.BytesIO(data), strict=True)
    if reader.security_handler is not None:
        raise ValueError("Les PDF chiffrés ne sont pas pris en charge par cet exemple.")
    if reader.embedded_signatures:
        raise ValueError("Utiliser un PDF sans signature pour ce premier parcours.")
    normalized = reader.xrefs.hybrid_xrefs_present
    if normalized:
        # Rewrite an unsigned hybrid file instead of disabling strict parsing.
        # The imported original stays untouched; only the copy is rewritten.
        buffer = io.BytesIO()
        copy_into_new_writer(reader).write(buffer)
        data = buffer.getvalue()
        if len(data) > MAX_BYTES:
            raise ValueError("La copie réenregistrée dépasse la limite de 10 Mio.")
    signer = signers.SimpleSigner.load(
        str(pki / "runtime/signer.key.pem"),
        str(pki / "runtime/signer.cert.pem"),
        ca_chain_files=(str(pki / "runtime/intermediate.cert.pem"),),
        key_passphrase=password,
    )
    if signer is None:
        raise ValueError(
            "Impossible de charger l’identité de test ; vérifier la clé et sa phrase secrète."
        )
    context = ValidationContext(
        trust_roots=[load_cert_from_pemder(str(pki / "trust/root.cert.pem"))],
        allow_fetching=False,
        revocation_mode="soft-fail",
    )
    metadata = signers.PdfSignatureMetadata(
        field_name="DZSignTest",
        md_algorithm="sha256",
        subfilter=fields.SigSeedSubFilter.PADES,
        reason="Démonstration DZ Digital Trust - TEST ONLY",
        embed_validation_info=False,
        use_pades_lta=False,
    )
    signed = signers.PdfSigner(metadata, signer=signer).sign_pdf(
        IncrementalPdfFileWriter(io.BytesIO(data), strict=True)
    )
    signed.seek(0)
    result_reader = PdfFileReader(signed, strict=True)
    if len(result_reader.embedded_signatures) != 1:
        raise ValueError("Le résultat ne contient pas exactement une signature.")
    status = validate_pdf_signature(
        result_reader.embedded_signatures[0],
        signer_validation_context=context,
        key_usage_settings=TEST_KEY_USAGE,
    )
    if not (status.intact and status.valid and status.trusted):
        raise ValueError("Le contrôle local du résultat a échoué ; aucun PDF n’a été publié.")
    signed.seek(0)
    # Exclusive creation prevents overwriting a file or following an output link.
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as target:
            target.write(signed.read())
    except BaseException:
        output.unlink()
        raise
    return {"normalized_before_signing": normalized}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--pki", type=Path, default=DEFAULT_PKI)
    parser.add_argument("--password-file", type=Path)
    args = parser.parse_args()
    try:
        if args.output.exists() or args.output.is_symlink():
            raise ValueError("La sortie existe déjà ; choisir un nouveau nom.")
        password = read_password(args.password_file, "Phrase secrète du signataire de TEST : ")
        result = sign_test_pdf(args.input, args.output, args.pki, password)
    except Exception as error:
        print(f"Signature impossible : {error}", file=sys.stderr)
        return 1
    print(f"PDF signé de TEST : {args.output}")
    if result["normalized_before_signing"]:
        print(
            "La structure hybride du PDF a été réenregistrée avant signature de la copie ; l’original est intact."
        )
    print("Intégrité et chaîne de test contrôlées localement avec pyHanko.")
    print("Révocation non vérifiée ; aucun horodatage de confiance ni qualification juridique.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
