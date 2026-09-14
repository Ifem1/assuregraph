#!/usr/bin/env python3
"""Pin live evidence URLs to an immutable Ifem1/assuregraph commit."""

from pathlib import Path
import re
import sys


TARGET = Path(__file__).resolve().parents[1] / "tests" / "integration" / "test_studionet_lifecycle.py"
PLACEHOLDER = 'FIXTURE_COMMIT = "FIXTURE_COMMIT_PLACEHOLDER"'


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python scripts/pin_fixture_commit.py <40-char commit sha>")
        return 2
    sha = sys.argv[1].strip().lower()
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        print("error: commit SHA must be exactly 40 lowercase/uppercase hex characters")
        return 2
    text = TARGET.read_text(encoding="utf-8")
    if PLACEHOLDER not in text:
        print("error: fixture placeholder was not found; inspect the integration test manually")
        return 1
    TARGET.write_text(text.replace(PLACEHOLDER, f'FIXTURE_COMMIT = "{sha}"'), encoding="utf-8")
    print(f"pinned integration fixtures to {sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
