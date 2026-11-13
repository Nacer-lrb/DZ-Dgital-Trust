"""Run the repository's checks without installing or downloading dependencies."""

import os
import shutil
import subprocess
from pathlib import Path

from check_docs import check_docs

ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".local/dz-sign/venv/bin/python"


def run(command, directory=ROOT):
    print(
        f"\n{Path(directory).relative_to(ROOT) or '.'}: {' '.join(map(str, command))}", flush=True
    )
    subprocess.run(
        list(map(str, command)),
        cwd=directory,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        check=True,
    )


def main():
    if not PYTHON.is_file() or shutil.which("npm") is None:
        raise SystemExit("Install the documented development environment before running checks.")
    check_docs()
    run([PYTHON, "-m", "ruff", "check", "demo/backend", "examples", "scripts"])
    run([PYTHON, "-m", "ruff", "format", "--check", "demo/backend", "examples", "scripts"])
    for directory in [
        "demo/backend",
        "examples/certificate-generation",
        "examples/python",
        "examples/pdf-signing",
    ]:
        source = "tests" if directory == "demo/backend" else "."
        run(
            [PYTHON, "-m", "unittest", "discover", "-s", source, "-p", "test_*.py", "-v"],
            ROOT / directory,
        )
    frontend = ROOT / "demo/frontend"
    for script in ("format:check", "test", "typecheck", "build"):
        run(["npm", "run", script], frontend)


if __name__ == "__main__":
    main()
