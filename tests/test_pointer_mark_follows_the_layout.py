"""The pointer mark after the grid has moved and the pointer has not.

QA-164. The mark on the Nightlord grid was kept by `enterEvent` and
`leaveEvent` alone, and Qt sends those on pointer movement. So the mark was
only ever as current as the last time the reader moved his hand: reflow the
grid from three columns to two under a resting pointer and the mark stayed on
a card that was no longer under it; bring a card under a resting pointer and
it took no mark at all. For the length of that pause the grid said something
untrue about the one thing the mark exists to say -- where a press would land.

**These cases move the pointer and then leave it alone.** Every other case
about this mark sends a synthetic `QEnterEvent`, which is the right tool for
"what does the mark do when the pointer arrives" and the wrong one here: a
synthetic Enter is exactly what does *not* happen when a layout moves. So the
pointer is put somewhere with `QCursor.setPos` -- the call a mouse driver
makes -- and after that only the window moves.

**Read off `hovered` and not off pixels**, unlike its neighbours in
`test_nightlord_selection.py`. There the finding was that a correct state
never reached the screen; here the finding is the state itself, which
outlived the geometry it described. `_set_hovered` redraws the card on every
change, and the neighbouring file guards that the redraw is visible.
"""

from __future__ import annotations

import pytest
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QScrollArea, QTabWidget

from nrplanner import bosstab, cardgrid

from tests import rendered

#: Three cards across under both platforms, and narrow enough that the window
#: below still fits on the offscreen platform's floor.
WIDE = 1250
#: Two cards across. The reflow between the two is the finding.
NARROW = 900


@pytest.fixture
def pointer_put_back():
    """Leave the pointer where the run found it, whatever a case does."""
    where = QCursor.pos()
    yield
    QCursor.setPos(where)


def cards(tab) -> list:
    return tab.holder.findChildren(bosstab.BossCard)


def marked(tab) -> list[str]:
    return sorted(card.boss["name"] for card in cards(tab) if card.hovered)


def under_the_pointer(tab) -> list[str]:
    """Which card the pointer stands on, asked of the cards' own rectangles.

    Deliberately not the call the widget uses to answer the same question: a
    case that asked `QApplication.widgetAt` would be agreeing with the code
    it guards by construction.
    """
    return sorted(card.boss["name"] for card in cards(tab)
                  if card.isVisible()
                  and card.rect().contains(card.mapFromGlobal(QCursor.pos())))


def put_the_pointer_on(card) -> None:
    """Move the pointer onto `card`, or say the platform would not."""
    target = card.mapToGlobal(card.rect().center())
    QCursor.setPos(target)
    rendered.settle()
    if QCursor.pos() != target:
        pytest.skip(
            f"this platform put the pointer at {QCursor.pos()} when asked "
            f"for {target}, so nothing below would be about the card it is "
            f"named for")


def columns(tab) -> int:
    return tab.findChild(cardgrid.CardGrid).columns


def test_the_mark_follows_a_reflow_the_pointer_did_not_ask_for(
        game_data, qapp, pointer_put_back):
    """The finding itself: three columns to two, hand still.

    Before the fix the mark stayed where it was; measured then, the pointer
    stood on no card at all and one card was still marked.
    """
    with rendered.laid_out(game_data, "boss_tab", WIDE) as (window, tab):
        wide_columns = columns(tab)
        put_the_pointer_on(cards(tab)[4])
        assert marked(tab) == under_the_pointer(tab) != [], (
            f"the pointer was put on a card and the grid marks "
            f"{marked(tab)}, so this case cannot tell whether a reflow moves "
            f"the mark")

        window.resize(NARROW, 900)
        rendered.settle()
        if columns(tab) == wide_columns:
            pytest.skip(
                f"the grid stayed at {wide_columns} columns between "
                f"{WIDE} and {NARROW} px, so nothing reflowed under the "
                f"pointer and this case would prove nothing")

        assert marked(tab) == under_the_pointer(tab), (
            f"after the reflow the grid marks {marked(tab)} while the "
            f"pointer stands on {under_the_pointer(tab)}")


def test_the_mark_follows_the_cards_a_scroll_brings_under_the_pointer(
        game_data, qapp, pointer_put_back):
    """The same gap by a third route, and one no card can see for itself.

    Scrolling moves the holder; the cards keep their places inside it, so not
    one of them receives a move of its own. Left to the cards alone the mark
    stayed on the card that had scrolled away.
    """
    with rendered.laid_out(game_data, "boss_tab", WIDE) as (_, tab):
        area = tab.findChild(QScrollArea)
        bar = area.verticalScrollBar()
        if bar.maximum() == 0:
            pytest.skip(
                "the Nightlord grid fits without scrolling at this size, so "
                "there is no scroll for the mark to follow")
        put_the_pointer_on(cards(tab)[4])
        was = marked(tab)
        assert was == under_the_pointer(tab) != []

        bar.setValue(bar.maximum())
        rendered.settle()

        assert marked(tab) == under_the_pointer(tab), (
            f"after scrolling the grid marks {marked(tab)} while the pointer "
            f"stands on {under_the_pointer(tab)}")
        assert marked(tab) != was, (
            f"the scroll left the same card {was} under the pointer, so this "
            f"case cannot tell whether the mark followed it")


def test_a_card_that_appears_under_a_resting_pointer_takes_the_mark(
        game_data, qapp, pointer_put_back):
    """The other half of the finding, and the harder half to notice.

    A mark that is missing looks like a pointer somewhere else. The reader
    only finds out he was wrong by pressing.
    """
    with rendered.laid_out(game_data, "boss_tab", WIDE) as (window, tab):
        tabs = window.findChild(QTabWidget)
        put_the_pointer_on(cards(tab)[4])
        expected = under_the_pointer(tab)
        assert expected != []

        tabs.setCurrentIndex(0)
        rendered.settle()
        assert marked(tab) == [], (
            "a card off screen is marked, so this case cannot tell whether "
            "the mark is put back on the way in")

        tabs.setCurrentWidget(tab)
        rendered.settle()

        assert marked(tab) == expected, (
            f"the grid came back marking {marked(tab)} with the pointer "
            f"standing on {expected}")
