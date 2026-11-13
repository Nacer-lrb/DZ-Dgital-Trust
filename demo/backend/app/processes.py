"""JSON protocol used by the bounded PDF worker processes."""

import asyncio
import json
import sys
from pathlib import Path

from fastapi import HTTPException


async def run_json_worker(script: Path, *args: str, payload=None, output_limit=2 * 1024 * 1024):
    process = await asyncio.create_subprocess_exec(
        sys.executable,
        "-B",
        str(script),
        *args,
        stdin=asyncio.subprocess.PIPE if payload is not None else asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,
    )
    try:
        if payload is not None:
            process.stdin.write(json.dumps(payload).encode())
            await process.stdin.drain()
            process.stdin.close()
        output = bytearray()
        while chunk := await process.stdout.read(65536):
            if len(output) + len(chunk) > output_limit:
                raise HTTPException(422, "La sortie du traitement dépasse la limite autorisée.")
            output.extend(chunk)
        await process.wait()
        if process.returncode != 0:
            raise HTTPException(422, "Le traitement PDF n’a pas abouti dans les limites prévues.")
        try:
            result = json.loads(output)
        except (ValueError, UnicodeDecodeError):
            raise HTTPException(422, "Le traitement PDF a renvoyé une réponse illisible.") from None
        if not isinstance(result, dict) or not isinstance(result.get("ok"), bool):
            raise HTTPException(422, "Le traitement PDF a renvoyé une réponse incomplète.")
        return result
    finally:
        if process.returncode is None:
            try:
                process.kill()
            except ProcessLookupError:
                pass
            await process.wait()
