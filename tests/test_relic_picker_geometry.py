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

import time

import pytest

from nrplanner import relicpicker

from tests import rendered

#: How long the fixture waits for the picker track before calling the opening
#: a fault. The most expensive slot of this save is measured at 318,1 ms
#: (S11-C); this is a fuse against a question that never ends, not a budget,
#: and nothing here asserts on the time.
ANSWER_FUSE_S = 30.0

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
    # The figures come from the window's picker track now (AD-028), so the
    # card area is empty until it answers (§3.8 fassung 3). Everything below
    # measures cards, so the fixture waits for the one answer of this opening
    # -- and calls a question that ends in none of its three outcomes a
    # failure rather than a hang. Nothing here reads how long it took.
    deadline = time.monotonic() + ANSWER_FUSE_S
    while dialog.waiting and time.monotonic() < deadline:
        rendered.settle()
    assert not dialog.waiting, (
        "the picker track ended in none of ready, failed and stopped")
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


def whole_rows(dialog) -> int:
    """How many complete rows of cards the viewport shows.

    Per row, because the rows are not the same height: one relic with a long
    name and two curses makes its own row 100 px taller than its neighbour,
    and counting every row by the tallest card anywhere in the grid measures
    a layout that does not exist.
    """
    holder = dialog.scroll.widget()
    drawn = holder.findChildren(relicpicker.RelicCard)
    bottoms: dict[int, int] = {}
    for card in drawn:
        top = card.mapTo(holder, card.rect().topLeft()).y()
        bottoms[top] = max(bottoms.get(top, 0), top + card.height())
    room = dialog.scroll.viewport().height()
    return sum(1 for bottom in bottoms.values() if bottom <= room)


def test_the_height_the_picker_asks_for_shows_three_whole_rows(picker):
    """AK-51, at the height the dialog asks for rather than the one it gets.

    The two are different statements and only the first is about this
    program: the offscreen desktop is 800 px tall, so a case written on the
    height the dialog *reaches* would agree with itself whatever the sizing
    said. Measured on this machine 2026-09-07: the dialog asks for 1122 px
    and the real desktop offers 1027, so the third row is 95 px short of
    fitting on the screen -- which is reported, not hidden.
    """
    holder = picker.scroll.widget()
    cards = ([holder.findChild(relicpicker.CustomRelicCard)]
             + holder.findChildren(relicpicker.RelicCard))
    picker.resize(picker.width(),
                  picker.wanted_height([c for c in cards if c is not None]))
    rendered.settle()
    assert whole_rows(picker) >= relicpicker.MINIMUM_ROWS, (
        f"at the height the dialog asks for, {whole_rows(picker)} whole rows "
        f"of cards are readable, not {relicpicker.MINIMUM_ROWS}")
    assert not picker.scroll.horizontalScrollBar().isVisible()


def test_the_picker_never_opens_taller_than_the_desktop(picker):
    """A dialog past the bottom edge is one whose last row cannot be read.

    AK-51 asks for more height than this desktop has, so the bound is what
    decides the opening size here -- and without it the dialog would open
    322 px past the screen offscreen, where the desktop is 800 px tall.
    """
    room = picker.screen().availableGeometry().height()
    assert picker.height() <= room, (
        f"the picker opens {picker.height()} px tall on a desktop of {room}")
