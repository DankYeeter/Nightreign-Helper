"""Read geometry off a laid-out widget, never off the constant behind it.

**Why this file exists.** The geometry findings of T-056 all have the same
shape: a number in the source was right and the pixels on screen were not.
`COLUMNS = 4` is a perfectly good four, and four cards still did not fit;
`QHeaderView.Stretch` on the name column is the documented way to say "give
this one the room", and it gave it 248 px out of 2052. A test that reads the
constant, or that recomputes the column count by the same formula the widget
uses, agrees with the widget by construction and would have passed on every
one of those days.

So everything here goes through the widget's own rendered rectangles:
`viewport()`, `mapTo`, `sectionSize`, `isVisible`. The expected values live in
the cases as literals out of `UI_SPEC.md`, never imported from the module
under test.

**Why a whole window.** A tab measured on its own is not the tab a player
sees: `QTabWidget` decides how much width a page gets, and the widths that
matter are window widths. `laid_out` builds the real `Planner`, puts one tab
in front and lets Qt settle before anything is read.
"""

from __future__ import annotations

import contextlib

from PySide6.QtWidgets import QApplication, QTabWidget

#: Layout passes to let run before reading. Qt defers geometry work to the
#: event loop, and reading too early gives the sizes from before the resize --
#: which is how the same table was measured at 1219 px and at 248 px for the
#: same window in one afternoon.
SETTLE_PASSES = 12


def settle(passes: int = SETTLE_PASSES) -> None:
    app = QApplication.instance()
    for _ in range(passes):
        app.processEvents()


@contextlib.contextmanager
def laid_out(data: dict, tab_name: str, width: int, height: int = 900):
    """A real window at `width` x `height`, with one tab in front.

    Yields (window, tab). Both sizes are logical px, which is what the
    acceptance criteria are written in.
    """
    from nrplanner import app as appmod

    from tests.conftest import clear_settings

    clear_settings()
    window = appmod.Planner(data)
    try:
        tab = getattr(window, tab_name)
        window.findChild(QTabWidget).setCurrentWidget(tab)
        window.resize(width, height)
        window.show()
        settle()
        yield window, tab
    finally:
        window.close()
        window.deleteLater()
        settle(2)


def inside_horizontally(widget, viewport) -> bool:
    """Is every pixel of `widget`'s width drawn within `viewport`?

    Horizontal only. A card below the fold is reachable by scrolling; a card
    sliced down its right-hand edge is not, and on this program the horizontal
    scrollbar that would reach it sits at the bottom edge of the tab, behind
    the taskbar (DR-015).
    """
    rect = widget.rect().translated(widget.mapTo(viewport,
                                                 widget.rect().topLeft()))
    return rect.left() >= 0 and rect.right() <= viewport.width()


def clipped(widgets, viewport) -> list:
    """Those of `widgets` that the viewport cuts off at one side."""
    return [w for w in widgets if not inside_horizontally(w, viewport)]


def scrolled_to_bottom(area) -> None:
    bar = area.verticalScrollBar()
    bar.setValue(bar.maximum())
    settle()


def fully_visible(widget, area) -> bool:
    """Is `widget` drawn whole inside `area`'s viewport, top to bottom?"""
    viewport = area.viewport()
    rect = widget.rect().translated(widget.mapTo(viewport,
                                                 widget.rect().topLeft()))
    return viewport.rect().contains(rect)
