"""One quantity, one name, wherever the program says it (AK-88).

The tile of a staff or a seal is headed `Spell power`. Until now the advisor's
own scope sentence called the same figure *"the spell scaling the game
shows"*, so a player reading the card and the reservation under it met two
names for one number. The director's addendum of 2026-09-05 settles the reach
of AK-88: **displayed text**, not the tree -- comments and internal field
names go on saying `catalyst_scaling`, and 31 of them do.

**Two searches, by different routes.** The first compares the two places that
draw the figure, so a rename in one of them fails here rather than on a
player's screen. The second walks every string constant in `nrplanner/` that
is not a docstring, so a third place saying it a third way is caught even
though nothing in this file knows that place exists (L-006).
"""

from __future__ import annotations

import ast
import pathlib
import re

import pytest

from nrplanner import arsenaltab, damage
from nrplanner.advisor import goals

#: The wording AK-88 retired, and a second mask for the same sentence written
#: without the retired phrase in it. Two independent masks, because a search
#: for the one phrase you expect is how a rewording slips through.
MASKS = (re.compile(r"spell\s+scaling", re.I),
         re.compile(r"scaling the game", re.I))

NRPLANNER = pathlib.Path(__file__).resolve().parents[1] / "nrplanner"


def displayed_literals(path: pathlib.Path):
    """Every string constant in `path` outside a docstring, with its line."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    docstrings = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if (isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                              ast.AsyncFunctionDef)) and body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)):
            docstrings.add(id(body[0].value))
    for node in ast.walk(tree):
        if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                and id(node) not in docstrings):
            yield node.lineno, node.value


def test_the_catalyst_figure_is_named_the_same_on_the_card_and_in_the_scope():
    """The tile's heading and the advisor's reservation say one thing.

    Both sides are read, neither is written down here: the assertion is that
    they agree, and pinning either would turn a disagreement into a passing
    test with a stale literal in it.
    """
    catalyst_lines = [line for line in goals.GOALS["max_damage"].scope
                      if "staves and seals" in line.lower()]
    assert catalyst_lines, "no line of the damage scope names the catalysts"
    figure = damage.SPELL_POWER_LABEL.lower()
    assert any(figure in line.lower() for line in catalyst_lines), (
        f"the tile heads a catalyst {damage.SPELL_POWER_LABEL!r} and the "
        f"scope calls the same figure something else: {catalyst_lines}")
    assert figure in arsenaltab.CATALYST_SENTENCE.lower(), (
        f"the arsenal summary no longer uses {damage.SPELL_POWER_LABEL!r} "
        f"either: {arsenaltab.CATALYST_SENTENCE!r}")


@pytest.mark.parametrize("mask", MASKS,
                         ids=("spell-scaling", "scaling-the-game"))
def test_the_retired_name_is_in_no_displayed_string_anywhere(mask):
    """The project-wide search, on the whole package rather than one file."""
    found = [(path.relative_to(NRPLANNER.parent).as_posix(), line, text[:70])
             for path in sorted(NRPLANNER.rglob("*.py"))
             for line, text in displayed_literals(path)
             if mask.search(text)]
    assert not found, (
        f"{len(found)} displayed strings still name the figure the retired "
        f"way: {found}")
