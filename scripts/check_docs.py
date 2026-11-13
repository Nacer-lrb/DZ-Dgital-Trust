"""Check local documentation links, language parity and Arabic direction markers."""

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {".git", ".local", "node_modules", ".next", "__pycache__", ".ruff_cache"}
CHAPTERS = {
    "README.md",
    "installation.md",
    "usage.md",
    "reference.md",
    "foundations.md",
    "legal.md",
    "development.md",
}


def check_docs():
    problems = []
    count = 0
    for directory, children, files in os.walk(ROOT):
        children[:] = [name for name in children if name not in EXCLUDED]
        for name in files:
            if not name.endswith(".md") or name == "plans.md":
                continue
            path = Path(directory) / name
            content = path.read_text()
            count += 1
            if not content.strip():
                problems.append(f"Empty document: {path.relative_to(ROOT)}")
            for target in re.findall(r"\]\(([^)]+)\)", content):
                if "://" in target or target.startswith("#"):
                    continue
                local = target.split("#", 1)[0]
                if local and not (path.parent / local).exists():
                    problems.append(f"Broken link in {path.relative_to(ROOT)}: {target}")
    for language in ("fr", "en", "ar"):
        directory = ROOT / "docs" / language
        present = {path.name for path in directory.glob("*.md")}
        if present != CHAPTERS:
            problems.append(f"Incomplete {language} handbook: {sorted(CHAPTERS - present)}")
    for path in (ROOT / "docs/ar").glob("*.md"):
        content = path.read_text()
        if '<div dir="rtl" lang="ar">' not in content or content.count("<div ") != content.count(
            "</div>"
        ):
            problems.append(f"Invalid Arabic direction wrappers: {path.name}")
    for chapter in ("installation.md", "development.md"):
        blocks = [
            re.findall(
                r"```bash\n(.*?)\n```", (ROOT / "docs" / language / chapter).read_text(), re.S
            )
            for language in ("fr", "en", "ar")
        ]
        if blocks[0] != blocks[1] or blocks[0] != blocks[2]:
            problems.append(f"Commands differ between translations: {chapter}")
    if problems:
        raise SystemExit("\n".join(problems))
    print(
        f"Documentation: {count} Markdown files, local links and three equivalent handbooks checked."
    )


if __name__ == "__main__":
    check_docs()
