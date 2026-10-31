"""A grid of cards that reflows to the width it is actually given.

Two tabs draw a wall of cards: the Nightlords and the arsenal. Both used to
hard-code how many fitted across -- four and five -- and both were measured
drawing a card the reader could not see (DR-013, DR-016a). A fixed column
count is a claim about the window, and no widget is in a position to make it.

The rule here is the one AK-72 states: **never draw a card partly.** The
column count follows from the width, and where the width only takes three
cards the fourth moves to the next row rather than being sliced.

**Why this widget reports a minimum of one card.** A QGridLayout's own minimum
width is the sum of its columns, so a holder inside a QScrollArea can never be
squeezed below the row it is currently laid out in -- the scroll area gives up
and shows a horizontal scrollbar instead, the widget never receives a smaller
size, and the reflow that would have fixed it never runs. That feedback loop
is what made the fourth Nightlord column unreachable at 1250 px: the scrollbar
that was supposed to rescue it sits at the bottom edge of the tab, behind the
taskbar (DR-015). Reporting one card as the minimum breaks the loop; the
resize event that follows sets the column count before anything is painted.
"""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QApplication, QFrame, QGridLayout, QWidget

#: Gap between neighbouring cards, in logical px. One value for both grids so
#: the two tabs keep the same rhythm (A13).
SPACING = 8


def columns_for(width: int, card_width: int) -> int:
    """How many cards of `card_width` fit whole into `width`.

    `n` cards need `n * card_width + (n - 1) * SPACING`, so the largest `n`
    that fits is `(width + SPACING) // (card_width + SPACING)`. At least one,
    because a window narrower than a single card still has to show that card
    rather than nothing.
    """
    if card_width <= 0:
        return 1
    return max(1, (width + SPACING) // (card_width + SPACING))


def room_for(columns: int, card_width: int) -> int:
    """How much room `columns` cards need side by side.

    The inverse of `columns_for`, and it exists because a window that opens at
    a size chosen by hand and a grid that reflows to the size it is given are
    two rules that can disagree. The relic picker opened at `card_width *
    columns + 80`, which left out the grid's own margins: five 190 px cards
    need 982 px, the viewport got 988 and the grid asked for 1 002, so eleven
    of fifty-five cards were drawn past the right-hand edge before the reader
    had touched anything (QA-141). Deriving the opening size from the same
    arithmetic the reflow uses is what keeps the two from parting again.
    """
    return columns * card_width + max(0, columns - 1) * SPACING


class CardGrid(QWidget):
    """Cards laid out across as many columns as the current width allows.

    `stretch` is the difference between the two callers. The Nightlord cards
    carry a minimum width and share the row between them, so a wide window has
    no dead strip down its right-hand side; the arsenal tiles are a fixed
    width and pack from the left.
    """

    def __init__(self, card_width: int, cards: list[QWidget], *,
                 stretch: bool = False,
                 margins: tuple[int, int, int, int] = (0, 0, 0, 0)):
        super().__init__()
        self._card_width = card_width
        self._stretch = stretch
        self._cards = list(cards)
        self._columns = 0

        self._grid = QGridLayout(self)
        self._grid.setSpacing(SPACING)
        self._grid.setContentsMargins(*margins)
        if not stretch:
            self._grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self._apply(columns_for(self._usable(self.width()), card_width))

    # -- geometry ---------------------------------------------------------
    def _usable(self, width: int) -> int:
        margins = self._grid.contentsMargins()
        return width - margins.left() - margins.right()

    def minimumSizeHint(self) -> QSize:  # noqa: N802 - Qt naming
        """One card wide. See the module docstring for why this matters."""
        hint = super().minimumSizeHint()
        margins = self._grid.contentsMargins()
        return QSize(self._card_width + margins.left() + margins.right(),
                     hint.height())

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt naming
        super().resizeEvent(event)
        self._apply(columns_for(self._usable(event.size().width()),
                                self._card_width))

    def _apply(self, columns: int) -> None:
        """Re-place the cards across `columns`, if that is a change.

        Guarded, because re-placing triggers a layout pass which can produce
        another resize event: without the guard the two would call each other
        for as long as the window was being dragged.
        """
        if columns == self._columns:
            return
        self._columns = columns
        while self._grid.count():
            self._grid.takeAt(0)
        for index, card in enumerate(self._cards):
            self._grid.addWidget(card, index // columns, index % columns)
        for column in range(self._grid.columnCount()):
            self._grid.setColumnStretch(
                column, 1 if (self._stretch and column < columns) else 0)

    def extend(self, cards: list[QWidget]) -> None:
        """Place `cards` after the ones already here, in the current columns.

        The relic picker builds its grid in paints (QA-258): the rows the
        dialog opens with at once, the rest from the event loop. Appending
        rather than rebuilding is what keeps the cards already on screen
        where the reader saw them.
        """
        for card in cards:
            index = len(self._cards)
            self._cards.append(card)
            self._grid.addWidget(card, index // self._columns,
                                 index % self._columns)

    # -- for tests and callers -------------------------------------------
    @property
    def columns(self) -> int:
        """The column count the grid is laid out in right now."""
        return self._columns


class HoverCard(QFrame):
    """A card that marks itself while the pointer is on it.

    The answer to QA-154 on the Nightlord grid and QA-157 on the relic cards
    and armament tiles: a click that lands in the gap between two cards opens
    nothing, a near miss opens the neighbour, and without a mark a reader
    cannot see which side of that line he is on. A subclass draws itself in
    `_apply_appearance`, reading `hovered`; this class only says when.
    """

    _hovered = False
    #: The focus came by Tab, so it is drawn dashed (T-335fix3).
    keyboard_focus = False

    def _note_focus_reason(self, reason: Qt.FocusReason) -> None:
        """Tab sets `keyboard_focus`, a click clears it; a popup closing or
        the window coming back leaves it as it was."""
        if reason in (Qt.TabFocusReason, Qt.BacktabFocusReason):
            self.keyboard_focus = True
        elif reason == Qt.MouseFocusReason:
            self.keyboard_focus = False

    @property
    def hovered(self) -> bool:
        """Is the pointer on this card, its own area or a label inside it?"""
        return self._hovered

    def _set_hovered(self, hovered: bool) -> None:
        if hovered == self._hovered:
            return
        self._hovered = hovered
        self._apply_appearance()

    def enterEvent(self, event) -> None:  # noqa: N802 - Qt naming
        """The pointer arrived, here or on one of the labels.

        Qt sends Enter down the whole chain under the pointer and Leave only
        to the widgets it actually left, so moving from the card onto the
        name inside it is not a departure and this card stays marked.
        """
        self._set_hovered(True)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # noqa: N802 - Qt naming
        self._set_hovered(False)
        super().leaveEvent(event)

    def _pointer_is_here(self) -> bool:
        """Is the pointer standing on this card at this instant?

        Asked of the screen instead of remembering the last Enter and Leave,
        because Qt sends those on pointer movement only. `widgetAt` answers
        for this application's windows and takes clipping and stacking with
        it, so a card scrolled out of sight or covered by another program
        does not claim the pointer.
        """
        under = QApplication.widgetAt(QCursor.pos())
        return under is not None and (under is self or self.isAncestorOf(under))

    def follow_the_pointer(self) -> None:
        """Put the mark where the pointer actually is, not where it was.

        QA-164: the grid reflows from three columns to two while the pointer
        rests, and the mark stays on a card that is no longer under it -- or
        a card appears under a resting pointer and never takes the mark at
        all. Both are the same gap: geometry changed and no pointer event
        followed. The card's own move, resize and show are exactly the
        moments that happens, so it re-reads the pointer there.
        """
        self._set_hovered(self._pointer_is_here())

    def moveEvent(self, event) -> None:  # noqa: N802 - Qt naming
        super().moveEvent(event)
        self.follow_the_pointer()

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt naming
        super().resizeEvent(event)
        self.follow_the_pointer()

    def showEvent(self, event) -> None:  # noqa: N802 - Qt naming
        super().showEvent(event)
        self.follow_the_pointer()
