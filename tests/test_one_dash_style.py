"""One dash on the screen, not two styles side by side (DR-018, AK-75).

The `Red variants` tab showed *"individual empowered enemies -- the same
enemy"* while the tab next to it showed *"Lasts the rest of the expedition —
not consumed"*. Both are the same punctuation mark, spelled two ways, on one
program.

**Read off the rendered tabs, and off every state they have.** A count taken
on the tab as it first opens finds 0 and always would have: all ten of the
remaining occurrences on 2026-09-05 were in `eventlore`, and a world event's
prose is only drawn once its row is selected. So this file walks the eleven
events and the four unannounced entries, and clicks through all ten Nightlord
cards. That is the difference between a test of the source and a test of the
screen -- the source scan below is the second, independent search (L-006),
not the primary one.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

from tests import rendered, tabtext

#: What may not appear. AK-75 replaces it with an em dash, spaced.
DOUBLE_HYPHEN = " -- "

#: The seven modules the six content tabs are drawn out of. `eventlore` is on
#: the list because it holds the prose of the World Events tab, and it held
#: all ten of the surviving occurrences.
TAB_MODULES = ("effectstab", "arsenaltab", "bosstab", "deeptab", "depthstab",
               "eventstab", "eventlore")


def displayed_literals(path: pathlib.Path):
    """Every string constant in `path` that is not a docstring.

    AK-75 exempts docstrings and comments: they are the module talking about
    itself, and no player reads them. Comments are not constants, so leaving
    the docstrings out is the whole exemption.
    """
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


def test_no_rendered_text_of_the_six_tabs_holds_a_double_hyphen(
        game_data, qapp):
    """AK-75 on the screen, in every state the six tabs can be put into."""
    found: list[str] = []
    with rendered.laid_out(game_data, "effects_tab", 1600) as (window, _):
        for name in ("effects_tab", "weapons_tab", "deep_tab", "depths_tab"):
            tab = getattr(window, name)
            found += [line for line in tabtext.everything(tab).splitlines()
                      if DOUBLE_HYPHEN in line]

        events = window.events_tab
        for row in range(events.list.count()):
            events.list.setCurrentRow(row)
            rendered.settle(2)
            found += [line for line
                      in tabtext.everything(events).splitlines()
                      if DOUBLE_HYPHEN in line]

        bosses = window.boss_tab
        for boss in bosses.bosses:
            bosses.show_detail(boss)
            found += [line for line
                      in tabtext.everything(bosses).splitlines()
                      if DOUBLE_HYPHEN in line]

    assert not found, (
        f"{len(found)} lines of the six tabs are drawn with ' -- '; first "
        f"three: {found[:3]}")


def test_the_walk_above_reaches_the_prose_that_held_the_last_ten(
        game_data, qapp):
    """Without this the case above could pass by never opening anything.

    All ten surviving occurrences were in world-event prose, which is drawn
    only for the selected row. If selecting rows stops reaching that prose,
    the case above goes green for the wrong reason.
    """
    from nrplanner import eventlore

    sample = eventlore.LORE[11170]["what"]
    seen = False
    with rendered.laid_out(game_data, "events_tab", 1600) as (_, events):
        for row in range(events.list.count()):
            events.list.setCurrentRow(row)
            rendered.settle(2)
            if sample[:40] in tabtext.everything(events):
                seen = True
                break
    assert seen, (
        f"walking the event list never drew {sample[:40]!r}, so the case "
        f"above is not reading the text that carried the finding")


@pytest.mark.parametrize("module", TAB_MODULES)
def test_no_displayed_literal_of_a_tab_module_holds_a_double_hyphen(module):
    """The second search, by a different route (L-006).

    The case above reads what is on screen and can only see the states it
    thinks to open. This one reads every string constant in the seven
    modules, so a sentence added behind a condition nobody selects is caught
    as well.
    """
    path = (pathlib.Path(__file__).resolve().parents[1] / "nrplanner"
            / f"{module}.py")
    found = [(line, text) for line, text in displayed_literals(path)
             if DOUBLE_HYPHEN in text]
    assert not found, (
        f"{module}.py has {len(found)} displayed literals with ' -- '; "
        f"first: line {found[0][0]}, {found[0][1][:70]!r}")
