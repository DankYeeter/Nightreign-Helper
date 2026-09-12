"""Guards ``NightreignHelper.spec``'s ``datas`` list against silently growing
to include a third source, a directory glob, or extracted game data.

A-030 (docs/legal/AUFLAGEN.md): the shipped EXE must carry no game content.
T-106 found that the spec does not itself *draw* that line -- it only
happens to hold it because ``datas`` enumerates exactly two sources and
nothing globs a directory. The workflow's "Refuse to ship game data" step
only inspects the build tree *after* pyinstaller has already run, so a local
build bypasses it entirely. This test is the guarantee that lives in the
spec itself.

The spec is parsed with ``ast`` rather than imported: importing it would
execute code that expects PyInstaller-only globals (``Analysis``, ``EXE``,
``PYZ``, ...) to already be present in the namespace, which is a side effect
this test has no business triggering.
"""

import ast
import pathlib

import pytest

SPEC_PATH = pathlib.Path(__file__).resolve().parent.parent / "NightreignHelper.spec"

# The only two sources A-030 allows: our own icon and the paramdefs needed to
# read the game's own files. Neither is game content by itself.
EXPECTED_DATAS = [
    ("nrplanner/data/icon.ico", "data"),
    ("vendor/Paramdex/NR/Defs", "paramdefs"),
]


def _read_datas_from_spec() -> list:
    """Return the literal value of the ``datas=`` keyword passed to the
    spec's ``Analysis(...)`` call, without executing the spec."""
    tree = ast.parse(SPEC_PATH.read_text(encoding="utf-8"), filename=str(SPEC_PATH))
    for node in ast.walk(tree):
        is_analysis_call = (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "Analysis"
        )
        if not is_analysis_call:
            continue
        for keyword in node.keywords:
            if keyword.arg == "datas":
                return ast.literal_eval(keyword.value)
    pytest.fail(
        f"{SPEC_PATH}: no 'datas' keyword found on an Analysis(...) call"
    )


def test_spec_datas_contains_only_the_two_approved_sources():
    assert _read_datas_from_spec() == EXPECTED_DATAS
