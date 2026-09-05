"""What the effects table puts on screen, read off the table.

**What guarded this tab before this file: nothing.** Two independent searches
of `tests/` on 2026-09-05 -- for the module name `effectstab` and for the
class name `EffectsTab` -- found 0 files. Multiplying `format_chance` by 1000
instead of 100, so every percentage on the tab read ten times over, left
622 of 622 green (QA-137, mutation M4).

Three of the tab's figures did not mean what their heading said, and all three
are checked here against numbers this file works out for itself:

* `Avg chance` averaged the (colour x mode) buckets instead of the slots
  (QA-126). The expectation below is computed from the effect's own chance
  entries, never by calling the tab.
* `Pools` counted relic effect slots (QA-125). Both the new heading and the
  sentence that has to be gone are pinned.
* `Tier` and `Copies` were built from the filtered view (QA-127), so an effect
  described its own ladder differently depending on which colours were shown.

**The percentage is formatted here rather than imported.** `format_chance` is
the function mutation M4 breaks, so a case that called it would agree with
whatever it does. The rule is written out again on purpose; that duplication
is the whole guard.
"""

from __future__ import annotations

import pytest

from nrplanner import effectstab

from tests import tabtext

#: The one sentence AK-79 allows on this tab about what a chance is a chance
#: of, verbatim, and the two it replaces. Written out rather than imported for
#: the reason at the top of this file.
CHANCE_DEFINITION = (
    "Chance is per relic effect slot, over every slot that can roll the "
    "effect under the filters above — not per relic and not per run.")
GONE = (
    "averaged over every pool that can produce it",
    "how likely an effect is on one roll",
    "A pool is one of the lists a relic's effects are drawn from",
)

#: AK-78, the heading and the tooltip the renamed column carries.
SLOTS_HEADER = "Relic slots"
SLOTS_TIP = (
    "How many of the game's relic effect slots can roll this effect, counted "
    "over every relic and every slot on it. It is not a count of loot pools, "
    "and more slots does not mean more likely — the chance column says that.")

#: The effect QA-126 measured the divergence on. Looked up by name, so the
#: case fails loudly if the dataset stops carrying it rather than quietly
#: checking nothing.
DIVERGENT = "[Wylder] Improved Mind, Reduced Vigor"


@pytest.fixture
def tab(game_data, qapp):
    widget = effectstab.EffectsTab(game_data)
    yield widget
    widget.deleteLater()


def as_shown(value: float) -> str:
    """A chance the way the tab writes it, from the rule and not the code."""
    if value >= 0.01:
        return f"{value * 100:.1f}%"
    return f"{value * 100:.2f}%"


def buckets(effect: dict) -> list[dict]:
    """Every (colour x mode) chance entry of one effect, at no filter."""
    out = []
    for key in ("chance", "deep_chance"):
        out += list((effect.get(key) or {}).values())
    return out


def cell(tab, name: str, column: str) -> str:
    """One cell of the row carrying this effect name, by column heading."""
    index = effectstab.COLUMNS.index(column)
    for row in range(tab.table.rowCount()):
        if tab.table.item(row, 0).text() == name:
            return tab.table.item(row, index).text()
    raise LookupError(
        f"no row named {name!r} on the tab; the table shows "
        f"{tab.table.rowCount()} rows")


def rows_named(tab, name: str) -> list[int]:
    return [row for row in range(tab.table.rowCount())
            if tab.table.item(row, 0).text() == name]


def test_the_average_is_weighted_by_how_many_slots_each_entry_stands_for(
        tab, game_data):
    """QA-126 and AK-80, on the effect the divergence was measured on.

    `[Wylder] Improved Mind, Reduced Vigor` carries one guaranteed slot at
    100% and 240 slots at 0.5012%. Averaged over the five buckets the single
    slot takes a fifth of the weight and the tab printed 20.4%; weighted by
    occurrence it is 0.91%, a factor of 22 apart.

    Both figures are computed here. The case refuses to run if they round to
    the same string, because it could then not tell a weighted average from an
    unweighted one -- which is the only thing it is for.
    """
    effect = next(e for e in game_data["effects"].values()
                  if " ".join(str(e.get("name", "")).split()) == DIVERGENT)
    entries = buckets(effect)
    slots = sum(entry["pools"] for entry in entries)
    weighted = sum(entry["avg"] * entry["pools"] for entry in entries) / slots
    unweighted = sum(entry["avg"] for entry in entries) / len(entries)

    assert as_shown(weighted) != as_shown(unweighted), (
        f"{DIVERGENT!r} rounds to the same string either way "
        f"({as_shown(weighted)}), so this case cannot tell the two averages "
        f"apart. Pick an effect whose buckets differ in size.")

    tab.search.setText(DIVERGENT)
    assert cell(tab, DIVERGENT, "Avg chance") == as_shown(weighted), (
        f"the tab does not show the occurrence-weighted average for "
        f"{DIVERGENT!r}; unweighted would be {as_shown(unweighted)}")


def test_every_row_shows_the_weighted_average_and_the_best_slot(tab,
                                                                game_data):
    """The same claim over the whole table, so it is not one lucky row.

    Read cell by cell against figures worked out here from the dataset. This
    is the case mutation M4 dies on: with `format_chance` multiplying by 1000
    every one of these strings moves, and with the average unweighted 129 of
    616 do.
    """
    by_name = {}
    for effect in game_data["effects"].values():
        by_name.setdefault(
            " ".join(str(effect.get("name", "")).split()), []).append(effect)

    checked = 0
    seen: set[str] = set()
    for row in range(tab.table.rowCount()):
        name = tab.table.item(row, 0).text()
        candidates = by_name.get(name) or []
        # Two genuinely different effects can share a name, and the table
        # merges by more than the name (see `effectstab.identity`). Only rows
        # whose name picks out exactly one effect are compared.
        if len(candidates) != 1:
            continue
        entries = buckets(candidates[0])
        slots = sum(entry["pools"] for entry in entries)
        if not slots:
            continue
        weighted = (sum(entry["avg"] * entry["pools"] for entry in entries)
                    / slots)
        best = max(entry["max"] for entry in entries)
        assert cell(tab, name, "Avg chance") == as_shown(weighted), name
        assert cell(tab, name, "Best chance") == as_shown(best), name
        assert cell(tab, name, "Relic slots") == str(slots), name
        checked += 1
        seen.add(as_shown(weighted))

    assert checked > 100, (
        f"only {checked} rows could be compared, which is too few to stand "
        f"for the table")
    assert len(seen) > 10, (
        "every row compared shows the same percentage, so an assertion on it "
        "could not tell one effect from another")


def test_the_slot_column_says_what_it_counts(tab):
    """QA-125: the column counted relic effect slots and was named for pools.

    The heading and its tooltip are both pinned, and the sentence that
    explained the word `pool` has to be gone from the tab entirely -- it
    described something the figure never was.
    """
    header = tab.table.horizontalHeaderItem(
        effectstab.COLUMNS.index(SLOTS_HEADER))
    assert header is not None and header.text() == SLOTS_HEADER
    assert tabtext.plain(header.toolTip()) == SLOTS_TIP

    headings = [tab.table.horizontalHeaderItem(c).text()
                for c in range(tab.table.columnCount())]
    assert "Pools" not in headings, (
        f"a column is still headed `Pools`: {headings!r}")


def test_one_definition_of_chance_and_only_one(tab):
    """AK-79. Two definitions stood six lines apart and disagreed.

    Counted over labels, tooltips, headers and cells together: a count that
    skipped the tooltips would pass with the sentence standing twice, which is
    the state this criterion exists to end.
    """
    everything = tabtext.everything(tab)
    assert CHANCE_DEFINITION in everything, (
        "the tab does not carry the one sentence saying what a chance is a "
        "chance of")
    assert everything.count("per relic effect slot") == 1, (
        f"`per relic effect slot` appears "
        f"{everything.count('per relic effect slot')} times on this tab")
    for sentence in GONE:
        assert sentence not in everything, (
            f"a definition AK-78/AK-79 removed is still on screen: "
            f"{sentence!r}")


def test_the_ladder_rung_does_not_change_with_the_colour_filter(tab,
                                                                game_data):
    """QA-127 and AK-81: a ladder is a property of the data, not of the view.

    Under `All colours` an effect that comes in a ladder of strengths shows
    which rung it is. Under a colour filter the same row used to show an empty
    cell, because the ladder was rebuilt from whatever the filter left.

    The effect is chosen by asking the dataset for one that is both a ladder
    and reachable under a single colour, not by writing a name down here.
    """
    tab.colour_box.setCurrentIndex(0)
    assert tab.colour_box.currentData() == -1, "expected `All colours` first"

    unfiltered = {}
    for row in range(tab.table.rowCount()):
        rung = tab.table.item(row, effectstab.COLUMNS.index("Tier")).text()
        colours = tab.table.item(row, effectstab.COLUMNS.index("Colours"))
        if rung:
            unfiltered.setdefault(
                (tab.table.item(row, 0).text(), rung), colours.text())

    assert unfiltered, "no effect on this tab comes in a ladder of strengths"

    for index in range(tab.colour_box.count()):
        if tab.colour_box.itemData(index) == -1:
            continue
        tab.colour_box.setCurrentIndex(index)
        colour = tab.colour_box.itemText(index)
        for row in range(tab.table.rowCount()):
            name = tab.table.item(row, 0).text()
            rung = tab.table.item(row, effectstab.COLUMNS.index("Tier")).text()
            available = [r for (n, r) in unfiltered if n == name]
            if not available:
                continue
            assert rung in available, (
                f"{name!r} shows rung {rung!r} under the {colour} filter and "
                f"{available!r} with no filter, so the ladder is being built "
                f"from the filtered view")


def test_the_tab_opens_with_the_question_it_answers(tab):
    """AK-68 and AK-76: the heading stands above the filters and the counts.

    Until T-057 the first line a reader met was `577 buffs (blue) then 75
    curses (red).` -- a stock count, before anything said what the stock was
    for.
    """
    lines = tabtext.labels(tab)
    assert lines[0] == effectstab.HEADING
    assert lines[1] == effectstab.QUESTION
    assert not any(character.isdigit() for character in lines[0]), (
        f"the first line of the tab carries a figure: {lines[0]!r}")
