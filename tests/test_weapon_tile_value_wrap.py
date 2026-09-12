"""A tile value never breaks inside one of its groups (DR-016b, AK-73).

`STR -7 · ARC +45 · DEX` ended a line on the weapons tab and `-7` stood
alone on the next: a stat parted from its own figure, reading as a different
and smaller number. Measured before the fix, on the 77 tiles the tab opens
with at 1600 px: **46 of 122** multi-group values broke inside a group.

**Laid out, not spot-checked**, for the reason `test_weapon_slot_tile_wrap.py`
gives one finding earlier: asserting that the string holds a no-break space
would pass just as well if Qt ignored the character, and that is the
interesting half of the claim. Every value is run through `QTextLayout` at the
label's own rendered width, and the same value with ordinary spaces is laid
out beside it as the control -- if the control does not break inside a group,
the width proves nothing and the case says so.

**The expectation is not imported.** `arsenaltab.unbroken` is the function
under guard; a case that called it would agree with whatever it did.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextLayout, QTextOption
from PySide6.QtWidgets import QLabel

from nrplanner import arsenaltab

from tests import rendered

#: How the tiles separate the groups of one value, written out here rather
#: than imported from the module this file exists to check.
SEPARATOR = " · "

#: The character that has to do the holding, likewise written out.
NO_BREAK_SPACE = " "


def lines_of(text: str, label) -> list[int]:
    """Where Qt starts each line of `text` in `label`'s font and width.

    The first line starts at 0 and that is no break, so it is dropped.
    """
    layout = QTextLayout(text, label.font())
    option = QTextOption()
    option.setWrapMode(QTextOption.WordWrap)
    layout.setTextOption(option)
    layout.beginLayout()
    starts = []
    while True:
        line = layout.createLine()
        if not line.isValid():
            break
        line.setLineWidth(label.width())
        starts.append(line.textStart())
    layout.endLayout()
    return starts[1:]


def group_spans(text: str) -> list[tuple[int, int]]:
    """(first, last) character offset of every group in `text`."""
    spans, at = [], 0
    for group in text.split(SEPARATOR):
        spans.append((at, at + len(group)))
        at += len(group) + len(SEPARATOR)
    return spans


def breaks_inside_a_group(text: str, label) -> list[int]:
    """The line starts that fall strictly within one group."""
    spans = group_spans(text)
    return [start for start in lines_of(text, label)
            if any(first < start < last for first, last in spans)]


@pytest.fixture(scope="module")
def value_labels(game_data, qapp):
    """Every right-aligned value label of every tile the tab opens with."""
    with rendered.laid_out(game_data, "weapons_tab", 1600, 950) as (_, tab):
        found = [(label.text(), label)
                 for tile in tab.findChildren(arsenaltab.Tile)
                 for label in tile.findChildren(QLabel)
                 if label.alignment() == Qt.AlignRight]
        yield found


def test_there_are_multi_group_values_to_measure(value_labels):
    """Without this the case below could hold over an empty list."""
    multi = [text for text, _ in value_labels if SEPARATOR in text]
    assert len(multi) > 20, (
        f"only {len(multi)} values on screen carry more than one group, so "
        f"there is next to nothing here to break")


def test_the_width_the_tiles_use_would_break_an_unjoined_value(value_labels):
    """The control. Without it the case below could pass on a wide tile."""
    would_break = [
        text for text, label in value_labels
        if SEPARATOR in text
        and breaks_inside_a_group(text.replace(NO_BREAK_SPACE, " "), label)
    ]
    assert would_break, (
        "with ordinary spaces not one value on these tiles would break "
        "inside a group, so the tile is wide enough for anything and the "
        "case below measures nothing")


def test_no_value_breaks_inside_one_of_its_groups(value_labels):
    """AK-73 at the width the tab actually draws."""
    broken = [(text, breaks_inside_a_group(text, label))
              for text, label in value_labels if SEPARATOR in text
              and breaks_inside_a_group(text, label)]
    assert not broken, (
        f"{len(broken)} of {len(value_labels)} values break inside a group; "
        f"first three: {broken[:3]}")


def test_a_value_with_one_group_is_left_as_it_was(value_labels):
    """`+3 Rare` keeps its ordinary space.

    The join is for values that have groups to keep apart. A single-group
    value has none, and rewriting it would change a displayed string no
    finding asked to be changed -- which is how this was caught: an existing
    case compared the `Upgraded to` row byte for byte.
    """
    joined = [text for text, _ in value_labels
              if SEPARATOR not in text and NO_BREAK_SPACE in text]
    assert not joined, (
        f"these single-group values were rewritten anyway: {joined[:3]}")
