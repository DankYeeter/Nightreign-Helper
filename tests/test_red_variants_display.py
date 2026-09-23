"""What the Red variants table counts, read off the table.

**What guarded this tab before this file: nothing.** Two independent searches
of `tests/` on 2026-09-05 -- for `depthstab` and for `DepthsTab` -- found 0
files. Moving mutation category 160 out of its own row and into the
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
    ("Named minibosses", {101, 104, 110, 135, 136, 137, 138}),
    ("Mixed-boss arena locations", {160}),
    ("Field bosses & arena locations", {120}),
    ("Merchants", {103}),
    ("Unidentified enemies", {130, 131}),
]

#: The first column of the depth figures. One text column stands in front of
#: them since AK-326 took `Examples (any map)` away.
FIRST_DEPTH_COLUMN = 1

#: What QA-286 found on screen, and what AK-325/AK-326 took off it. Written
#: out here rather than imported, for the reason the grouping above is: a
#: case reading the module's own strings would follow the wrong word wherever
#: it was moved to.
RETIRED_WORDS = ("Evergaol", "evergaol", "Night bosses (unconfirmed)",
                 "Named field enemies & minibosses", "Examples (any map)",
                 "— the files name none")


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
                      for c in range(FIRST_DEPTH_COLUMN,
                                     tab.table.columnCount())]
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
    worked out here. The case also insists the category-160 row is present and
    non-empty, because moving its one category away is the mutation that made
    the row disappear entirely rather than show a wrong number.
    """
    deep = game_data.get("deep_of_night") or {}
    mutations = deep.get("mutations") or []
    assert mutations, "this dataset carries no mutation counts"

    checked = 0
    mixed_maps = 0
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
                    f"{headers(tab)[FIRST_DEPTH_COLUMN + column]}: shows "
                    f"{shown[label][column]!r} against {count}")
                checked += 1

        mixed_maps += "Mixed-boss arena locations" in shown

        totals = [sum(expected_counts(mutations, group, cats, tab.depths)[i]
                      for _label, cats in GROUPS)
                  for i in range(tab.depths)]
        row = "Total red variants on the map"
        for column, depths in enumerate(tab.depth_groups):
            assert shown[row][column] == str(totals[depths[0]]), (
                f"{tab.map_box.currentText()}: the total column "
                f"{headers(tab)[FIRST_DEPTH_COLUMN + column]} does not add "
                f"up")

    assert checked > 50, f"only {checked} figures were compared"
    assert mixed_maps, (
        "the category-160 row is on none of the maps, which is what mutation "
        "M3 does to it")


def test_the_depth_columns_merge_only_where_the_data_repeats(tab, game_data):
    """AK-100: five columns said three columns' worth, on every map.

    Depth 2 equals Depth 3 and Depth 4 equals Depth 5 for all six maps and all
    22 data rows. The merge is the tab's own reading of the data, so this case
    checks the reading against the data and then feeds a row that breaks the
    pattern to see the table fall back.
    """
    assert headers(tab)[FIRST_DEPTH_COLUMN:] == [
        "Depth 1", "Depth 2–3", "Depth 4–5"], (
        f"unexpected depth columns for this dataset: "
        f"{headers(tab)[FIRST_DEPTH_COLUMN:]!r}")

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
        assert headers(widened)[FIRST_DEPTH_COLUMN:] == [
            f"Depth {i}" for i in range(1, 6)], (
            f"a row with five different figures still shows merged columns: "
            f"{headers(widened)[FIRST_DEPTH_COLUMN:]!r}")
    finally:
        widened.deleteLater()


def test_the_examples_column_is_gone_and_the_depth_figures_moved_up(tab):
    """AK-326: the column fell, so the depth figures start one column earlier.

    Read off the table rather than off `depthstab`: a case that took the
    column index from the module would follow it back if the column ever
    came back, and pass while the table said `Examples (any map)` again.
    """
    drawn = headers(tab)
    assert drawn[0] == "What can be red"
    assert all(header.startswith("Depth") for header in drawn[1:]), (
        f"something other than the depth figures follows the name column: "
        f"{drawn!r}")
    assert tab.table.rowCount(), "the table drew no rows"
    # Every cell past the name column carries a figure or the dash. An empty
    # one would be the examples column back under another name.
    blanks = [(row, column)
              for row in range(tab.table.rowCount())
              for column in range(1, tab.table.columnCount())
              if not tab.table.item(row, column).text()]
    assert not blanks, f"these cells past the name column are empty: {blanks}"


def test_the_two_boss_rows_are_named_after_places_and_not_after_a_cast(tab):
    """AK-325, QA-286: categories 120 and 160 are locations, not characters.

    The whole tab is searched and not only the two labels, because the words
    QA-286 found also stood in the summary line under the map box.
    """
    everything = tabtext.everything(tab)
    labels = [tab.table.item(row, 0).text()
              for row in range(tab.table.rowCount())]
    assert "Field bosses & arena locations" in labels
    assert "Mixed-boss arena locations" in labels
    left = [word for word in RETIRED_WORDS if word in everything]
    assert not left, f"the tab still says {left}"


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
