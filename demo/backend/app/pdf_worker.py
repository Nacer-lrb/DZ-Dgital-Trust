"""Bounded PDF inspection process. No keys, rendering or network access."""

import json
import resource
import socket
import sys
from pathlib import Path


def restrict_process():
    # Apply limits before importing the PDF parser. This is not an OS sandbox.
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

    def deny_network(*args, **kwargs):
        raise OSError("Network access disabled in PDF inspection")

    socket.socket.connect = deny_network
    socket.socket.connect_ex = deny_network
    socket.create_connection = deny_network


def inspect_pdf(path):
    restrict_process()
    from pyhanko.pdf_utils.reader import PdfFileReader

    with path.open("rb") as stream:
        if stream.read(5) != b"%PDF-":
            return {"ok": False, "code": "invalid_pdf"}
        stream.seek(0)
        reader = PdfFileReader(stream, strict=True)
        if reader.security_handler is not None:
            return {"ok": False, "code": "encrypted_pdf"}
        pages = reader.root["/Pages"]
        count = int(pages["/Count"])
        if count <= 0:
            return {"ok": False, "code": "empty_pdf"}
        # Traverse the actual page tree at both ends, rather than trusting Count alone.
        reader.find_page_for_modification(0)
        reader.find_page_for_modification(count - 1)
        return {"ok": True, "page_count": count}


if __name__ == "__main__":
    try:
        result = inspect_pdf(Path(sys.argv[1]))
    except Exception:
        result = {"ok": False, "code": "invalid_pdf"}
    print(json.dumps(result))
