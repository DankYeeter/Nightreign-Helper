"""The relic picker draws whole cards, at the size it opens itself at.

**What guarded the picker's layout before this file: nothing.** Two
independent searches of `tests/` on 2026-09-05 -- for `relicpicker` and for
`RelicPicker` -- found `test_custom_relic.py` and `test_relic_restore.py`,
which between them open the dialog, pick a relic and close it again. Neither
reads a rendered rectangle, and the dialog was slicing eleven of its
fifty-five cards before anybody touched it.

Measured on Windows at 150 % scale under the style the program sets, on the
tree before this change:

* at **1 030** px, the width `RelicPicker` gave itself, the viewport was 988
  and five 190 px cards with their grid margins asked for 1 002 -- eleven of
  fifty-five cards drawn past the right-hand edge, horizontal scrollbar
  showing;
* at **900** px the same eleven cards stood in the same place, 142 of their
  190 px past the edge, relic names ending mid-word;
* at **700** px, twenty-two.

The column count never moved, because it was `COLUMNS = 5` (QA-141, DR-016a
at a place T-058 left out).

**Nothing here recomputes the column count.** `cardgrid.columns_for` would
agree with the grid however wrong both were, which is exactly how `COLUMNS =
4` survived on the Nightlords tab. What is read is where the cards were
actually drawn, against the viewport that has to contain them.
"""

from __future__ import annotations

import pytest

from nrplanner import relicpicker

from tests import rendered

#: Widths to open the dialog at, in logical px. `None` means "leave it at the
#: size it gives itself", which is the case QA-141 was raised on: the defect
#: needed no input from the reader at all.
PICKER_WIDTHS = (None, 900, 700)


@pytest.fixture
def picker(planner, qapp):
    """The picker for the first relic slot of a real window.

    A real slot, not a stub: the card list comes from `available_items()` and
    the count of cards is what makes the grid wide.
    """
    planner.show()
    rendered.settle()
    slot = planner.base_slots[0]
    dialog = relicpicker.RelicPicker(slot, planner.icons, "",
                                     lambda _text: None)
    dialog.show()
    rendered.settle()
    yield dialog
    dialog.close()
    dialog.deleteLater()
    rendered.settle(2)


def cards(dialog) -> list:
    holder = dialog.scroll.widget()
    return (holder.findChildren(relicpicker.CustomRelicCard)
            + holder.findChildren(relicpicker.RelicCard))


@pytest.mark.parametrize("width", PICKER_WIDTHS)
def test_every_card_in_the_picker_is_drawn_whole(picker, width):
    """AK-72 for the picker: never a card the reader can only half see."""
    if width is not None:
        picker.resize(width, picker.height())
        rendered.settle()
    drawn = cards(picker)
    assert drawn, (
        "the picker drew no cards at all, so nothing here is measured")
    cut = rendered.clipped(drawn, picker.scroll.viewport())
    assert not cut, (
        f"at {picker.width()} px {len(cut)} of {len(drawn)} cards are cut off "
        f"at the viewport edge; the relic names go first")
    assert not picker.scroll.horizontalScrollBar().isVisible(), (
        f"at {picker.width()} px the card area needs a horizontal scrollbar")


def test_the_picker_opens_wide_enough_for_the_cards_it_opens_with(picker):
    """The half of QA-141 that made it happen without anyone touching it.

    The dialog asked for `card width x columns + 80`, a figure that left out
    the grid's own margins, and then a grid that could not reflow held five
    columns in it regardless. Both sides come from one arithmetic now, so the
    test is that the opening width really does fit that many whole cards --
    read off the cards, not off the arithmetic.
    """
    drawn = cards(picker)
    assert len(drawn) > relicpicker.OPENING_COLUMNS, (
        f"this slot offers only {len(drawn)} cards, fewer than the "
        f"{relicpicker.OPENING_COLUMNS} the dialog opens wide, so a full row "
        f"is never drawn and this case measures nothing")
    tops = [card.mapTo(picker.scroll.viewport(),
                       card.rect().topLeft()).y() for card in drawn]
    first_row = tops.count(min(tops))
    assert first_row == relicpicker.OPENING_COLUMNS, (
        f"the dialog opens {picker.width()} px wide and fits {first_row} "
        f"cards across, not the {relicpicker.OPENING_COLUMNS} it sized itself "
        f"for")
