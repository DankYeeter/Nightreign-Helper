"""How long a reader has to hold still before a cut-short heading says more.

QA-151. The effects table shortens a heading that will not fit and puts the
whole name in the heading's tooltip (QA-140). T-064 proved at the running
window that the tooltip is really there -- and measured what it costs:
**750-800 ms** of a pointer held perfectly still, which is Fusion's own
`SH_ToolTip_WakeUpDelay` of 700 ms plus the platform's overhead. The player of
2026-09-05 "waited only briefly" over `Comes with c…` and saw nothing at all.
At 833 px it is sharper still: `Copies`, `Colours` and `Comes with curse` are
all drawn `Co…` and there is no other way to tell them apart.

**Why a green run here can only come from the mechanism under test.** Every
case waits a span it has worked out from the style's own figure and asserted
to be *shorter* than it -- so Qt's ordinary tooltip machinery cannot have
produced what is measured, whatever the platform does. The counter-case makes
the same point from the other side: a heading drawn whole must show nothing
in exactly that span, which is the promise that the quick answer is a signal
and not a reflex.

**Both halves of the finding are here.** That a shortened heading answers
quickly is the first; that an unshortened one does not is the second, because
the difference between them is the only thing on screen that says "something
was taken away from this one, and it is a moment away".
"""

from __future__ import annotations

import time

import pytest
from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication, QStyle, QToolTip

from tests import rendered

#: A width both platforms can give the window, so neither skips this file.
#: The offscreen platform will not go below 964 logical px and the Windows
#: platform's screen stops at 1709 (QA-146).
WIDTH = 1250

#: What this file calls a brief hover, as a fraction of the style's own
#: wake-up delay. Half of it: long enough that the answer is a considered one
#: and not a twitch, and -- the point of the whole file -- strictly short of
#: what the style asks for, so Qt's own tooltip cannot be what is seen. Under
#: Fusion that is 350 ms against the style's 700.
PATIENCE_FRACTION = 2

#: The lower bound the delay has to clear, in ms: about what a pointer sweeping
#: a 1600 px window in one second spends crossing the widest heading the table
#: ever shortens (the label columns are capped at 160 logical px). Written out
#: here rather than imported, so a delay that dropped under it fails instead of
#: taking this case with it. Windows, 150 % scale, Fusion, logical px.
SWEEP_MS = 100


def wake_up_delay(widget) -> int:
    """What the running style asks a reader to wait for any tooltip."""
    return widget.style().styleHint(QStyle.SH_ToolTip_WakeUpDelay, None,
                                    widget)


def patience(widget) -> int:
    return max(1, wake_up_delay(widget) // PATIENCE_FRACTION)


def hold_still(milliseconds: int) -> None:
    """Let real time pass with the event loop running.

    Real time, because what is under test is a timer. `processEvents` alone
    would return before it had fired and read the state from before the wait.
    """
    app = QApplication.instance()
    deadline = time.monotonic() + milliseconds / 1000
    while time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.005)
    app.processEvents()


def shortened(table) -> list[int]:
    """The columns whose heading is drawn shorter than its name."""
    return [column for column in range(table.columnCount())
            if table.horizontalHeaderItem(column).text()
            != table.heading(column)]


def hover(table, column: int) -> None:
    """Put a pointer in the middle of one heading, the way a mouse does."""
    header = table.horizontalHeader()
    QToolTip.hideText()
    where = QPointF(
        header.sectionViewportPosition(column) + header.sectionSize(column) / 2,
        header.height() / 2)
    QApplication.sendEvent(header.viewport(), QMouseEvent(
        QEvent.MouseMove, where,
        QPointF(header.viewport().mapToGlobal(where.toPoint())),
        Qt.NoButton, Qt.NoButton, Qt.NoModifier))


def test_a_shortened_heading_answers_inside_a_brief_hover(game_data, qapp):
    """The finding: the name was reachable, and not in the time a reader gives.

    The wait is derived from the style and asserted to be short of what the
    style itself would wait, so nothing Qt does on its own can make this pass.
    """
    with rendered.laid_out(game_data, "effects_tab", WIDTH) as (_, tab):
        table = tab.table
        cut = shortened(table)
        assert cut, (
            f"no heading is shortened at {WIDTH} px on this platform, so "
            f"this case has nothing to hover over")

        brief = patience(table)
        assert brief < wake_up_delay(table), (
            f"this case waits {brief} ms and the style opens a tooltip after "
            f"{wake_up_delay(table)} ms, so a pass would prove nothing")

        hover(table, cut[0])
        hold_still(brief)

        assert QToolTip.isVisible(), (
            f"after {brief} ms over `{table.horizontalHeaderItem(cut[0]).text()}` "
            f"nothing has opened; the style would take "
            f"{wake_up_delay(table)} ms and that is the wait the finding is "
            f"about")
        assert table.heading(cut[0]) in QToolTip.text(), (
            f"what opened does not name the column: {QToolTip.text()!r}")


def test_a_heading_drawn_whole_is_left_to_the_style(game_data, qapp):
    """The other half, and what makes the quick answer a signal.

    If every heading answered quickly, a reader would learn nothing from one
    that did -- and the tab would be putting an explanation in front of
    someone who had not asked for it. Nothing was taken from a heading drawn
    whole, so there is nothing to hand back sooner.
    """
    with rendered.laid_out(game_data, "effects_tab", WIDTH) as (_, tab):
        table = tab.table
        whole = [column for column in range(table.columnCount())
                 if column not in shortened(table)]
        assert whole, (
            f"every heading is shortened at {WIDTH} px on this platform, so "
            f"this case has nothing to hover over")

        hover(table, whole[0])
        hold_still(patience(table))

        assert not QToolTip.isVisible(), (
            f"`{table.heading(whole[0])}` is drawn in full and still answered "
            f"a hover early with {QToolTip.text()!r}, so the quick answer no "
            f"longer marks the headings that were cut")


def test_each_shortened_heading_answers_with_its_own_name(game_data, qapp):
    """The `Co…` case, at the narrowest window this platform will make.

    Three headings drawn identically is what makes the wait expensive rather
    than merely slow: until one of them answers, a reader cannot even tell
    which column he is looking at. So every shortened heading is hovered in
    turn and has to come back with its own name, and any two drawn alike have
    to come back with different text.

    The window is squeezed to 1 px and takes whatever the platform allows --
    964 offscreen, 760 under Windows -- because a case parametrised on the
    acceptance widths would skip the narrow end on the very platform the suite
    runs (QA-146), and the narrow end is where this finding lives.
    """
    with rendered.laid_out(game_data, "effects_tab", 1600) as (window, tab):
        window.resize(1, 900)
        rendered.settle()
        table = tab.table
        cut = shortened(table)
        assert len(cut) > 1, (
            f"only {len(cut)} heading is shortened at the narrowest window "
            f"this platform allows ({window.width()} px)")

        answers = {}
        for column in cut:
            hover(table, column)
            hold_still(patience(table))
            assert QToolTip.isVisible(), (
                f"`{table.heading(column)}` gave no answer at "
                f"{window.width()} px")
            assert table.heading(column) in QToolTip.text(), (
                f"the answer over `{table.horizontalHeaderItem(column).text()}`"
                f" does not name `{table.heading(column)}`: "
                f"{QToolTip.text()!r}")
            answers[column] = QToolTip.text()

        drawn = {}
        for column in cut:
            drawn.setdefault(
                table.horizontalHeaderItem(column).text(), []).append(column)
        for stub, columns in drawn.items():
            texts = {answers[column] for column in columns}
            assert len(texts) == len(columns), (
                f"{len(columns)} headings are drawn `{stub}` at "
                f"{window.width()} px and {len(texts)} different answers come "
                f"back, so at least two of them cannot be told apart at all")


def test_the_quick_answer_stays_between_its_two_bounds(game_data, qapp):
    """The figure itself, against the two things that bound it.

    Above, the style's own wake-up delay: a wait at or over it is the wait the
    finding is about and changes nothing. Below, the time a pointer merely
    crossing the header spends over the widest heading the table shortens: a
    wait under that opens tooltips at a reader who is on his way somewhere
    else. Neither bound is read out of `nrplanner.effectstab` -- one comes
    from the running style and the other is written out at the top of this
    file with its derivation.
    """
    with rendered.laid_out(game_data, "effects_tab", WIDTH) as (_, tab):
        delay = tab.table.hint.delay()
        assert delay < wake_up_delay(tab.table), (
            f"the shortened headings wait {delay} ms and the style waits "
            f"{wake_up_delay(tab.table)} ms, so nothing about them is quicker")
        assert delay > SWEEP_MS, (
            f"the shortened headings answer after {delay} ms, inside the "
            f"~{SWEEP_MS} ms a pointer spends crossing one on its way past")


def leaving() -> QEvent:
    return QEvent(QEvent.Leave)


def pressing() -> QEvent:
    return QMouseEvent(QEvent.MouseButtonPress, QPointF(1, 1), QPointF(1, 1),
                       Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)


@pytest.mark.parametrize("interrupt", [leaving, pressing],
                         ids=["the pointer leaves", "the reader clicks"])
def test_an_abandoned_hover_is_not_answered_afterwards(
        game_data, qapp, interrupt):
    """A hover the reader gave up on must not be answered a moment later.

    Both events say the pointer has stopped asking about this heading: one
    that it has left the header, one that the reader has gone on to sort by a
    column. An answer arriving after either would open over something it does
    not describe -- which is the risk a shorter wait brings with it, and the
    reason it is worth a case of its own.
    """
    with rendered.laid_out(game_data, "effects_tab", WIDTH) as (_, tab):
        table = tab.table
        cut = shortened(table)
        assert cut, f"no heading is shortened at {WIDTH} px on this platform"

        hover(table, cut[0])
        QApplication.sendEvent(table.horizontalHeader().viewport(),
                               interrupt())
        hold_still(patience(table))

        assert not QToolTip.isVisible(), (
            f"the hover over `{table.heading(cut[0])}` was given up and the "
            f"answer came anyway: {QToolTip.text()!r}")
