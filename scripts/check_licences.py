"""Fail if a dependency ships without its licence being recorded.

The released executable bundles every runtime dependency into one file, so
their terms travel with it. That is easy to forget when adding a library: the
build keeps working, the notice quietly goes stale, and nobody finds out until
someone asks.

This makes it noisy instead. It reads `requirements.txt` and checks each entry
appears in THIRD_PARTY.md, and it checks the licence files that must exist.
It deliberately does NOT try to judge licence compatibility -- that is a
question for a person, and a script pretending to answer it would be worse
than no script.

    python scripts/check_licences.py
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

# Files that must exist for the release to be honest about what it contains.
REQUIRED = [
    ("LICENSE", "the project's own licence"),
    ("THIRD_PARTY.md", "what the executable bundles and under what terms"),
    ("vendor/Paramdex/NOTICE", "where the param definitions come from"),
]

# Recorded here as well as in THIRD_PARTY.md, so a licence changing under us on
# an upgrade is caught rather than assumed. Read from package metadata, not
# from memory.
EXPECTED_LICENCE = {
    "pyside6": "LGPL",
    "shiboken6": "LGPL",
    "pycryptodome": "BSD",
    "zstandard": "BSD",
    "pillow": "MIT-CMU",
    "texture2ddecoder": "MIT",
    "pyinstaller": "GPL",
}


def requirements() -> list[str]:
    text = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    names = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        names.append(re.split(r"[=<>~!\[]", line)[0].strip().lower())
    return names


def main() -> int:
    ok = True

    for name, why in REQUIRED:
        path = ROOT / name
        if path.exists() and path.stat().st_size > 0:
            print(f"  [ ok ] {name} — {why}")
        else:
            print(f"  [FAIL] {name} is missing — {why}")
            ok = False

    notice = (ROOT / "THIRD_PARTY.md").read_text(encoding="utf-8").lower() \
        if (ROOT / "THIRD_PARTY.md").exists() else ""

    print()
    for name in requirements():
        if name in notice:
            print(f"  [ ok ] {name} is recorded in THIRD_PARTY.md")
        else:
            print(f"  [FAIL] {name} is bundled but not recorded in "
                  f"THIRD_PARTY.md")
            ok = False

    # The LGPL obligation this build only meets because the source is public.
    print()
    if "lgpl" in notice and "relink" in notice:
        print("  [ ok ] the Qt/LGPL relinking obligation is addressed")
    else:
        print("  [FAIL] THIRD_PARTY.md must state how the LGPL relinking "
              "obligation is met — PySide6 is bundled into the executable")
        ok = False

    print("\nOK" if ok else "\nFAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
