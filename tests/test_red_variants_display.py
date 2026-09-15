"""What the Red variants table counts, read off the table.

**What guarded this tab before this file: nothing.** Two independent searches
of `tests/` on 2026-09-05 -- for `depthstab` and for `DepthsTab` -- found 0
files. Moving mutation category 160 out of the evergaol row and into the
ordinary-enemies row, which makes a whole row of the table vanish and tips
every figure in the rest, left 622 of 622 green (QA-137, mutation M3).

**The expected counts are summed here from `deep_of_night.mutations`,** with
the category ids written out again rather than imported from
`depthstab.PLAYER_GROUPS`. That duplication is the guard: a case importing the
grouping would follow category 160 wherever it was moved to and report a green
run either way.
"""

from __future__ import annotations

import pytest

from nrplanner import depthstab

from tests import tabtext

#: The player-facing grouping, written out again. Kept in the order the tab
#: draws it, so a row that changed place shows here as a mismatched label
#: rather than as a wrong number.
GROUPS = [
    ("Ordinary enemies in camps & ruins", {100, 105, 140, 141, 150, 151}),
    ("Named field enemies & minibosses", {101, 104, 110, 135, 136, 137, 138}),
    ("Evergaol bosses", {160}),
    ("Night bosses (unconfirmed)", {120}),
    ("Merchants", {103}),
    ("Unidentified enemies", {130, 131}),
]

#: AK-99, the heading and tooltip of the column that used to claim a link to
#: the map box above it, and the cell two rows have to carry instead of being
#: left blank.
EXAMPLES_HEADER = "Examples (any map)"
EXAMPLES_TIP = (
    "Named members of this group anywhere in the game. The files do not list "
    "them per map, so these names are not tied to the map selected above.")
NO_NAMES = "— the files name none"


@pytest.fixture
def tab(game_data, qapp):
    widget = depthstab.DepthsTab(game_data)
    yield widget
    widget.deleteLater()


def headers(tab) -> list[str]:
    return [tab.table.horizontalHeaderItem(c).text()
            for c in range(tab.table.columnCount())]


def shown_rows(tab) -> dict[str, list[str]]:
    """Row label -> the figures it shows, one per depth column."""
    out = {}
    for row in range(tab.table.rowCount()):
        label = tab.table.item(row, 0).text()
        out[label] = [tab.table.item(row, c).text()
                      for c in range(2, tab.table.columnCount())]
    return out


def expected_counts(mutations, group: int, categories: set[int],
                    depths: int) -> list[int]:
    """What a run places on this map, per depth, summed here from the data."""
    pool = [m for m in mutations if m["group"] in (group, 0)]
    return [sum(m["counts"][i] for m in pool if m["category"] in categories)
            for i in range(depths)]


def test_every_row_counts_the_categories_its_label_names(tab, game_data):
    """M3: a category moved between rows, and no figure was held by anything.

    Every map the box offers, every row, every depth column -- against sums
    worked out here. The case also insists the evergaol row is present and
    non-empty, because moving its one category away is the mutation that made
    the row disappear entirely rather than show a wrong number.
    """
    deep = game_data.get("deep_of_night") or {}
    mutations = deep.get("mutations") or []
    assert mutations, "this dataset carries no mutation counts"

    checked = 0
    evergaol_maps = 0
    for index in range(tab.map_box.count()):
        tab.map_box.setCurrentIndex(index)
        group = tab.map_box.currentData()
        shown = shown_rows(tab)
        for label, categories in GROUPS:
            counts = expected_counts(mutations, group, categories, tab.depths)
            if not any(counts):
                assert label not in shown, (
                    f"{tab.map_box.currentText()}: {label!r} is drawn with "
                    f"nothing in it")
                continue
            assert label in shown, (
                f"{tab.map_box.currentText()}: {label!r} carries "
                f"{counts!r} and is not on the table")
            for column, depths in enumerate(tab.depth_groups):
                count = counts[depths[0]]
                assert shown[label][column] == (str(count) if count else "—"), (
                    f"{tab.map_box.currentText()}, {label!r}, column "
                    f"{headers(tab)[2 + column]}: shows "
                    f"{shown[label][column]!r} against {count}")
                checked += 1

        evergaol_maps += "Evergaol bosses" in shown

        totals = [sum(expected_counts(mutations, group, cats, tab.depths)[i]
                      for _label, cats in GROUPS)
                  for i in range(tab.depths)]
        row = "Total red variants on the map"
        for column, depths in enumerate(tab.depth_groups):
            assert shown[row][column] == str(totals[depths[0]]), (
                f"{tab.map_box.currentText()}: the total column "
                f"{headers(tab)[2 + column]} does not add up")

    assert checked > 50, f"only {checked} figures were compared"
    assert evergaol_maps, (
        "the evergaol row is on none of the maps, which is what mutation M3 "
        "does to it")


def test_the_depth_columns_merge_only_where_the_data_repeats(tab, game_data):
    """AK-100: five columns said three columns' worth, on every map.

    Depth 2 equals Depth 3 and Depth 4 equals Depth 5 for all six maps and all
    22 data rows. The merge is the tab's own reading of the data, so this case
    checks the reading against the data and then feeds a row that breaks the
    pattern to see the table fall back.
    """
    assert headers(tab)[2:] == ["Depth 1", "Depth 2–3", "Depth 4–5"], (
        f"unexpected depth columns for this dataset: {headers(tab)[2:]!r}")

    # Counter-build: one row with five different figures, in a category the
    # tab draws. If the merge were written down rather than read, the table
    # would go on showing three columns for data that needs five.
    data = {"deep_of_night": dict(game_data["deep_of_night"])}
    data["deep_of_night"]["mutations"] = list(
        data["deep_of_night"]["mutations"]) + [
        {"id": -1, "group": 0, "category": 160, "varies": True,
         "counts": [1, 2, 3, 4, 5]}]
    widened = depthstab.DepthsTab(data)
    try:
        assert headers(widened)[2:] == [f"Depth {i}" for i in range(1, 6)], (
            f"a row with five different figures still shows merged columns: "
            f"{headers(widened)[2:]!r}")
    finally:
        widened.deleteLater()


def test_the_examples_column_does_not_claim_the_selected_map(tab):
    """QA-132 and AK-99: the same names came back whatever map was chosen.

    The rosters carry no map dimension, so the column could not be map-bound;
    what it could do is stop saying it is. The two rows whose rosters name
    nobody say so rather than leaving the cell blank (A7).
    """
    assert EXAMPLES_HEADER in headers(tab)
    header = tab.table.horizontalHeaderItem(headers(tab).index(EXAMPLES_HEADER))
    assert tabtext.plain(header.toolTip()) == EXAMPLES_TIP
    assert "For example" not in headers(tab)

    first = {label: cells for label, cells in shown_rows(tab).items()}
    examples = {}
    for row in range(tab.table.rowCount()):
        examples[tab.table.item(row, 0).text()] = tab.table.item(row, 1).text()
    assert examples.get("Ordinary enemies in camps & ruins") == NO_NAMES, (
        "the largest row of the table still shows an empty examples cell")

    # Same cells on another map, because the column now says so.
    tab.map_box.setCurrentIndex((tab.map_box.currentIndex() + 1)
                                % tab.map_box.count())
    for row in range(tab.table.rowCount()):
        label = tab.table.item(row, 0).text()
        if label in examples:
            assert tab.table.item(row, 1).text() == examples[label], (
                f"{label!r}: the examples changed with the map, so the "
                f"heading `(any map)` is now the wrong claim")
    assert first, "the table drew no rows"


def test_the_tab_opens_with_what_a_red_variant_is(tab):
    """AK-98: the answer used to sit in a clause halfway down the intro.

    And the limit stands beside the answer: the files carry counts and
    categories, and no strength figure at all.
    """
    lines = tabtext.labels(tab)
    assert lines[0] == depthstab.HEADING
    assert lines[1] == depthstab.QUESTION
    assert "do not say by how much" in lines[1]
    everything = tabtext.everything(tab)
    assert everything.count("the same enemy") == 1, (
        "the sentence saying what a red variant is stands twice")
