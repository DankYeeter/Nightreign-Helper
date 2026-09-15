"""What the Deep of Night tables put on screen, read off the tables.

**What guarded this tab before this file: nothing.** Two independent searches
of `tests/` on 2026-09-05 -- for `deeptab` and for `DeepTab` -- found 0 files.
Two mutations measured on that tree left 622 of 622 green (QA-137):

* `WIN_RATING = 200` raised to `999`, so every cell of the win row read
  `+999`;
* `saReceiveDamageRate` and `staminaAttackRate` swapped between their two row
  labels -- exactly the mix-up the module's own comment records as having
  happened once already, one field being stamina an enemy drains from you and
  the other stance damage the enemy takes.

**Neither expectation comes out of `nrplanner.deeptab`.** The win figure is
written out here with its provenance, not read from `WIN_RATING`, because
`WIN_RATING` is the thing under guard. The scaling figures are aggregated here
from `deep_of_night.scaling`, by the rule stated in the module rather than by
calling `_summary()`, so a swap of the two fields has something to disagree
with.
"""

from __future__ import annotations

import statistics

import pytest

from nrplanner import deeptab

from tests import tabtext

#: +200 for a win. Not imported: `deeptab.WIN_RATING` is what mutation M1
#: moves, and a case reading it would follow it to 999 without a word.
#:
#: Where the number comes from (L-001): no param in `regulation.bin` carries
#: it -- no field name anywhere mentions rank or rating, and the text tables
#: state only the band thresholds -- so it was confirmed in the running game
#: by this project's owner, and the tab says on screen that it was. A
#: community report of +300 for a Depth 3 win on an invisible map is exactly
#: 200 + 100 and corroborates it from an independent direction.
WIN_RATING_CONFIRMED_IN_GAME = 200

#: The two rows the module's comment says were once labelled the wrong way
#: round, with the field each of them is about.
SWAPPABLE_ROWS = {
    "Stance damage they take": "saReceiveDamageRate",
    "Stamina drain on block": "staminaAttackRate",
}

#: AK-96, the two references that were missing from the first table, and the
#: formula every one of AK-70's cases has to contain.
NOT_IN_THE_FILES = "The files do not say"
REWARD_MULTIPLIER_NOTE = (
    "Reward multiplier: the game's own multiplier for this Depth. The files "
    "do not say what it multiplies, so it is shown as a comparison between "
    "Depths and nothing more.")


@pytest.fixture(scope="module")
def tab(game_data, qapp):
    widget = deeptab.DeepTab(game_data)
    yield widget
    widget.deleteLater()


def table_with_row(tab, label: str):
    """The table carrying this vertical header, and the row it is on."""
    from PySide6.QtWidgets import QTableWidget

    for table in tab.findChildren(QTableWidget):
        for row in range(table.rowCount()):
            header = table.verticalHeaderItem(row)
            if header is not None and header.text() == label:
                return table, row
    raise LookupError(f"no table on this tab has a row headed {label!r}")


def typical(scaling: list[dict], field: str, depth: int) -> float | None:
    """The figure the scaling table shows for one field at one depth.

    The rule is the module's, written out again here rather than imported:
    the median over every enemy profile that carries the field, each profile
    weighted by how many enemy groups share it. A case that called
    `tab._summary()` would agree with a swapped pair of fields, because the
    swap is in the labelling and not in the aggregation.
    """
    values: list[float] = []
    for profile in scaling:
        per_depth = profile.get("per_depth") or []
        if depth >= len(per_depth) or not per_depth[depth]:
            continue
        value = per_depth[depth].get(field)
        if isinstance(value, (int, float)):
            values += [value] * max(1, len(profile.get("rows") or []))
    return statistics.median(values) if values else None


def test_the_win_row_shows_the_rating_confirmed_in_game(tab):
    """M1: `+999` in every column of the win row and nothing noticed.

    The row does not vary by depth -- winning pays the same at Depth 1 and at
    Depth 5 -- so every cell is checked, and the case asserts the row has more
    than one cell to check.
    """
    table, row = table_with_row(tab, "Win")
    assert table.columnCount() > 1, "the win row has one column to check"
    for column in range(table.columnCount()):
        assert table.item(row, column).text() == (
            f"+{WIN_RATING_CONFIRMED_IN_GAME}"), (
            f"the win row shows {table.item(row, column).text()!r} at column "
            f"{column}; the figure confirmed in game is "
            f"+{WIN_RATING_CONFIRMED_IN_GAME}")

    # The same figure appears once more in prose, added to both bonuses, and
    # a mutation that moves the constant moves that sentence too.
    everything = tabtext.everything(tab)
    assert f"is +{WIN_RATING_CONFIRMED_IN_GAME + 200}." in everything, (
        f"the sentence adding the two +100 bonuses to a win no longer says "
        f"+{WIN_RATING_CONFIRMED_IN_GAME + 200}")


def test_each_scaling_row_holds_the_field_its_label_names(tab, game_data):
    """M2: the two similarly named fields point in opposite directions.

    One is stamina the enemy's blows drain from you, the other is stance
    damage the enemy takes; the module records getting them the wrong way
    round once already. Swapping the labels changes no number on the tab, only
    which row each belongs to, so the case refuses to run unless the two rows
    differ at some depth.
    """
    scaling = (game_data.get("deep_of_night") or {}).get("scaling") or []
    assert scaling, "this dataset carries no enemy scaling profiles"

    differ = False
    for label, field in SWAPPABLE_ROWS.items():
        table, row = table_with_row(tab, label)
        for depth in range(table.columnCount()):
            expected = typical(scaling, field, depth)
            shown = table.item(row, depth).text()
            if expected is None:
                assert shown == "-", (label, depth, shown)
                continue
            assert shown.startswith(f"x{expected:.2f}"), (
                f"row {label!r} at depth {depth + 1} shows {shown!r}; the "
                f"field {field} is {expected:.2f}")
            other = SWAPPABLE_ROWS[
                next(k for k in SWAPPABLE_ROWS if k != label)]
            if typical(scaling, other, depth) != expected:
                differ = True

    assert differ, (
        "the two fields hold the same figure at every depth in this dataset, "
        "so swapping their labels would change nothing and this case cannot "
        "tell one from the other")


def test_the_reward_multiplier_says_what_it_does_not_say(tab):
    """AK-96 and QA-128: a multiplier with no stated subject.

    `x1.47` invites a reader to supply a subject of their own. The subject is
    not in the files and not known in the code either, so the tab says that
    (A7) rather than leaving the invitation open.
    """
    everything = tabtext.everything(tab)
    assert REWARD_MULTIPLIER_NOTE in everything
    assert NOT_IN_THE_FILES in everything


def test_the_sigil_line_separates_what_was_read_from_what_was_identified(
        tab, game_data):
    """AK-96: the count comes from the depth table, the name from play.

    The game's own description of the item has been loaded on every start
    since the extractor first read that table and thrown away every time. It
    appears once, quoted, so it reads as the game's wording.
    """
    deep = game_data.get("deep_of_night") or {}
    sigil = deep.get("sigil_name") or "Sovereign Sigils"
    info = (deep.get("sigil_info") or "").strip()
    everything = tabtext.everything(tab)

    assert (f"{sigil}: the figure comes from the depth table. That the item "
            f"is the {sigil} was identified in game, not read from a link in "
            f"the files.") in everything
    if info:
        assert everything.count(info) == 1, (
            f"the game's own description of the {sigil} appears "
            f"{everything.count(info)} times")


def test_the_tab_opens_with_the_question_it_answers(tab):
    """AK-68 and AK-95: a roof over four headings that had none."""
    lines = tabtext.labels(tab)
    assert lines[0] == deeptab.HEADING
    assert lines[1] == deeptab.QUESTION
    assert lines[2] == "WHAT EACH DEPTH IS WORTH", (
        f"the four original headings no longer follow the roof: {lines[2]!r}")
