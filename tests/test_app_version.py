"""nrplanner/__init__.py is the one place the app version is written down.

T-169: the built 1.8.0 artifact from cycle 16 and the 1.8.0 artifact rebuilt
after it share a name but not a byte -- two different programs, one label.
That happened because nothing enforced the single-source-of-truth the file's
own comment already claimed. `app.py`, `NightreignHelper.spec`,
`.github/workflows/release.yml` and `scripts/setup_check.py` all read
`__version__` back dynamically rather than spelling it out again; this guard
is what keeps that true instead of merely documented.
"""

from __future__ import annotations

import re
from pathlib import Path

from nrplanner import __version__

REPO_ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = REPO_ROOT / "nrplanner" / "__init__.py"

# Files that need the current version at build or run time. Each is expected
# to read it back from VERSION_FILE rather than spelling it out itself.
DYNAMIC_READERS = (
    REPO_ROOT / "nrplanner" / "app.py",
    REPO_ROOT / "NightreignHelper.spec",
    REPO_ROOT / ".github" / "workflows" / "release.yml",
    REPO_ROOT / "scripts" / "setup_check.py",
)


def test_version_is_assigned_exactly_once_in_the_source_file() -> None:
    text = VERSION_FILE.read_text(encoding="utf-8")
    assignments = re.findall(r'^__version__\s*=\s*"[^"]+"', text, re.MULTILINE)
    assert assignments == [f'__version__ = "{__version__}"']


def test_version_has_the_expected_shape() -> None:
    # release.yml strips a leading "v" from the tag and compares the rest
    # against this string verbatim, so it has to be plain major.minor.patch.
    assert re.fullmatch(r"\d+\.\d+\.\d+", __version__), __version__


def test_no_other_source_file_hardcodes_the_current_version() -> None:
    literal = re.escape(__version__)
    pattern = re.compile(rf"""["']{literal}["']""")
    offenders = [
        str(path.relative_to(REPO_ROOT))
        for path in DYNAMIC_READERS
        if pattern.search(path.read_text(encoding="utf-8"))
    ]
    assert offenders == []
