import argparse
import os
from pathlib import Path

from pyhanko.pdf_utils import generic
from pyhanko.pdf_utils.writer import PdfFileWriter


def make_pdf(path):
    writer = PdfFileWriter()
    font = writer.add_object(
        generic.DictionaryObject(
            {
                generic.pdf_name("/Type"): generic.pdf_name("/Font"),
                generic.pdf_name("/Subtype"): generic.pdf_name("/Type1"),
                generic.pdf_name("/BaseFont"): generic.pdf_name("/Helvetica"),
            }
        )
    )
    content = writer.add_object(
        generic.StreamObject(
            stream_data=(
                b"BT /F1 16 Tf 50 770 Td (DZ Digital Trust - TEST ONLY) Tj "
                b"0 -30 Td /F1 11 Tf (Fictitious document for the PDF signing exercise.) Tj ET\n"
            )
        )
    )
    writer.insert_page(
        generic.DictionaryObject(
            {
                generic.pdf_name("/Type"): generic.pdf_name("/Page"),
                generic.pdf_name("/MediaBox"): generic.ArrayObject(
                    [generic.NumberObject(n) for n in (0, 0, 595, 842)]
                ),
                generic.pdf_name("/Resources"): generic.DictionaryObject(
                    {
                        generic.pdf_name("/Font"): generic.DictionaryObject(
                            {generic.pdf_name("/F1"): font}
                        ),
                    }
                ),
                generic.pdf_name("/Contents"): content,
            }
        )
    )
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as target:
            writer.write(target)
    except BaseException:
        path.unlink()
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        make_pdf(args.output)
    except OSError as error:
        parser.exit(1, f"Création impossible : {error}\n")
    print(f"PDF fictif créé : {args.output}")
