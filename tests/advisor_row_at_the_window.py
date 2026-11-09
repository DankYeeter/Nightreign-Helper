"""The Advisor row, measured at the running window (AK-05, AK-194).

Both criteria are about the width the window opens at on the player's
machine -- the derived opening width of A14, `Planner._opening_width()` --
and that is not a figure the suite's platform can produce. Offscreen, the
fallback font runs about 12 px a character against 6 under Windows (T-084),
the window's floor is 988 px and the row is left 136 px wide, every box in
it squeezed to 28. Under Windows the same code opens the window at 1 350 px
and gives the row 498 (Fusion, Segoe UI 9 pt, device pixel ratio 1.25;
measured 2026-09-13, T-225).

So the row is measured in a process of its own under
`QT_QPA_PLATFORM=windows`: a real window with the real style, font and
scaling (L-009), kept off the screen with `WA_DontShowOnScreen` -- measured
against a shown window, none of the figures moves. `pytest.skip` has no place
here: a machine that cannot open the window is a failure of this guard, not
an exemption from it (AK-05, "keine offscreen-Plattform").

A desktop narrower than the derived width caps it (`_opening_width`'s
`room`), and there the row breaks into two lines (T-334n, AK-395). So the
same window is measured again at the width it would open at on each of
`NARROW_DESKTOPS` and `AK_350_ROOMS`, under `rooms`; at each width of
`LINE_WIDTHS` and at the window's least width, control by control (`at`,
`window_minimum`); and on both sides of the break, in every direction
(`threshold`, `across_the_break`).

The stat sheet, the right-hand pane of the same window, is read in the
same pass (`sheet`): which of its drawn children reach past the pane's
viewport, at the opening width and on each narrow desktop (DR-028, A13).
Only drawn children: a hidden label keeps the geometry of the last layout
pass it took part in, and one hidden before the splitter sized the pane
still reports 630 px while nothing of it is on screen (T-259).

Run as `python -m tests.advisor_row_at_the_window <snapshot.json>`; the
parent side is `measure`, and the `advisor_row_at_the_window` fixture in
`conftest.py` runs it once for the session.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

#: Desktops that cap the derived opening width: 1080p at 125 % scaling
#: (1536) and a legacy 1366-px desktop, both real machines rather than a
#: lower and a higher reading. Since AK-350 (T-325a/e) `_opening_width`
#: takes `OPENING_WIDTH_SCREEN_RATIO` of `room`, floored at
#: `OPENING_WIDTH_FLOOR` (1536) -- so both entries clamp to the same 1536 px
#: opening width now (`round(1536 * 0.9) = 1382` and `round(1366 * 0.9) =
#: 1229`, both under the floor), kept as two entries because both are real
#: desktops a player has, not because they still tell the row apart.
#: Since T-334n the row stands on two lines there, every caption whole
#: (AK-399 replaces Option B's "the boxes may be cut" of AK-05/AK-271).
NARROW_DESKTOPS = (1536, 1366)

#: AK-352's own two reference desktops, on the other side of AK-350's ratio:
#: `1920` sits below `need / OPENING_WIDTH_SCREEN_RATIO` (the ratio itself
#: narrows the row below its one-line need, so it takes two lines), `2560`
#: sits above it (the ratio already covers the need, same as an uncapped
#: screen). Distinct from `NARROW_DESKTOPS`, which the floor caps and the
#: ratio does not.
AK_350_ROOMS = (1920, 2560)

#: The window widths of the T-334n check table (`UI_SPEC.md`, Nachtrag T-334n
#: §5): two legacy desktops, QA-292's own 1522, and the three opening widths.
LINE_WIDTHS = (1366, 1426, 1522, 1536, 1728, 1959)

#: A 4.12 failure sentence long enough to need shortening at any width.
A_LONG_FAILURE = ("the dataset carries no attribute curves for this "
                  "Nightfarer, so nothing could be worked out at all")


def _next_on_screen(stack, bar):
    """What stands under the row: the list of rejected relics takes no room
    with nothing rejected (AK-430), so it is not what the row is measured to."""
    return next(stack.itemAt(index).widget()
                for index in range(stack.indexOf(bar) + 1, stack.count())
                if not stack.itemAt(index).widget().isHidden())


def measure(game_data: dict, tmp_path: pathlib.Path) -> dict:
    """The row's figures at the opening width, out of a child process."""
    snapshot = tmp_path / "snapshot.json"
    snapshot.write_text(json.dumps(game_data), encoding="utf-8")
    done = subprocess.run(
        [sys.executable, "-m", "tests.advisor_row_at_the_window",
         str(snapshot)],
        cwd=REPO, capture_output=True, text=True, check=False,
        env={**os.environ, "QT_QPA_PLATFORM": "windows"})
    assert done.returncode == 0, (
        f"the window could not be measured under the Windows platform:\n"
        f"{done.stderr}")
    return json.loads(done.stdout.splitlines()[-1])


def _room_for_the_caption(widget) -> int:
    """How wide the caption may be before the control cuts it.

    A button draws its text inside the style's button margin; a box draws
    its current entry in the field left of the arrow; a label has the whole
    of itself. Not `sizeHint`: Fusion gives every button 80 px whatever it
    says, so a button 66 px wide may still show all of `Optimize`.
    """
    from PySide6.QtWidgets import (QComboBox, QPushButton, QStyle,
                                   QStyleOptionComboBox)

    style = widget.style()
    if isinstance(widget, QComboBox):
        option = QStyleOptionComboBox()
        widget.initStyleOption(option)
        return style.subControlRect(QStyle.CC_ComboBox, option,
                                    QStyle.SC_ComboBoxEditField,
                                    widget).width()
    if isinstance(widget, QPushButton):
        return widget.width() - 2 * style.pixelMetric(
            QStyle.PM_ButtonMargin, None, widget)
    return widget.width()


def _caption_of(widget) -> str:
    return (widget.currentText() if hasattr(widget, "currentText")
            else widget.text())


def _the_row(bar, controls) -> dict:
    """What the row shows: the status, and every control drawn short."""
    from tests import rendered

    on_screen = [(name, widget) for name, widget in controls
                 if not widget.isHidden()]
    return {
        "on_screen": [name for name, _widget in on_screen],
        "cut": [name for name, widget in on_screen
                if rendered.clipped([widget], bar)
                or widget.fontMetrics().horizontalAdvance(_caption_of(widget))
                > _room_for_the_caption(widget)],
        "widths": {name: widget.width() for name, widget in on_screen},
        "status_width": bar.status.width(),
        "status_text": bar.status.text(),
        "status_whole_text": bar.status.accessibleName(),
        "status_tooltip": bar.status.toolTip(),
        "row_tooltip": bar.toolTip(),
    }


def _suggest(bar) -> None:
    """Put a suggestion up, the three action buttons with it."""
    from nrplanner import advisorbar
    from nrplanner.advisor import types
    from tests import rendered

    bar._answer = types.AdvisorResult(
        goal_id="max_damage", goal_label="Maximise damage",
        suggestions=(types.Suggestion(
            choices=(types.SlotChoice(slot_index=0, handle=7, relic_id=1,
                                      name="X"),),
            score=types.GoalScore(value=1.0, display="1", unit="")),))
    bar._show(advisorbar.Situation(advisorbar.State.SUGGESTED,
                                   goal_label="Maximise damage",
                                   slots=6, slots_filled=1))
    rendered.settle(20)


def _the_warning(bar, controls) -> dict:
    """T-335a: the row with its warning line up (QA-292/304 -- nothing may
    be covered), then back in the suggested state `_both_states` leaves."""
    from PySide6.QtCore import QPoint, QRect, Qt

    from nrplanner import advisorbar
    from tests import rendered

    bar._show(advisorbar.Situation(
        advisorbar.State.SUGGESTED_WITH_AN_EMPTY_SLOT,
        goal_label="Maximise damage", slots=6, slots_filled=0,
        slots_without_a_choice=6,
        no_carrier_for="fire damage with Sorceries"))
    rendered.settle(20)
    warning = bar.warning
    stack = bar.parentWidget().layout()
    below = _next_on_screen(stack, bar)
    figures = {
        "shown": not warning.isHidden(),
        "inside_the_row": bar.rect().contains(QRect(
            warning.mapTo(bar, QPoint(0, 0)), warning.size())),
        # What the whole sentence needs wrapped at the line's width, read off
        # the font rather than off the label, so a line that stopped
        # wrapping is short too.
        "short_by": warning.fontMetrics().boundingRect(
            QRect(0, 0, warning.width(), 1 << 20), Qt.TextWordWrap,
            warning.text()).height() - warning.height(),
        "gap_below": below.y() - (bar.y() + bar.height()),
        "cut": _the_row(bar, controls)["cut"],
    }
    _suggest(bar)
    return figures


def _both_states(bar, controls) -> dict:
    """The row in 4.12 and in the suggested state, at its present width."""
    from tests import rendered

    bar._on_failed(A_LONG_FAILURE)
    rendered.settle(20)
    failed = _the_row(bar, controls)
    _suggest(bar)
    return {"failed": failed, "suggested": _the_row(bar, controls)}


def _laid_out(bar, controls) -> dict:
    """Where each drawn control of the row stands, in the row's own pixels,
    and the line count and height the row has at its present width
    (AK-396, AK-398, AK-399, AK-402)."""
    from PySide6.QtCore import QPoint, QRect

    drawn = [(name, widget) for name, widget in controls
             if not widget.isHidden()]
    column = bar.parentWidget()
    stack = column.layout()
    below = _next_on_screen(stack, bar)
    return {
        "lines": bar.lines,
        "row_width": bar.width(),
        "height": bar.height(),
        "status_width": bar.status.width(),
        "geometry": {name: list(QRect(widget.mapTo(bar, QPoint(0, 0)),
                                      widget.size()).getRect())
                     for name, widget in drawn},
        # The `Incoming` pair stands where the damage question is hidden, so
        # it is not among `drawn`; only its need is read.
        "hints": {**{name: widget.sizeHint().width() for name, widget in drawn},
                  "incoming_label": bar.incoming_label.sizeHint().width(),
                  "incoming_box": bar.incoming_box.sizeHint().width()},
        "minimums": {name: widget.minimumWidth() for name, widget in drawn},
        "outside_the_row": [name for name, widget in drawn
                            if not bar.rect().contains(QRect(
                                widget.mapTo(bar, QPoint(0, 0)),
                                widget.size()))],
        "cut": _the_row(bar, controls)["cut"],
        "gap_below": below.y() - (bar.y() + bar.height()),
        "column_spacing": stack.spacing(),
        "column_minimum_height": column.minimumSizeHint().height(),
    }


def _at_row_width(planner, bar, row_width: int) -> None:
    """Size the window so the row is `row_width` px wide.

    Every pixel of window reaches the middle pane once the side panes stand
    at their default widths, so one step is enough there.
    """
    from tests import rendered

    planner.resize(planner.width() + row_width - bar.width(),
                   planner.height())
    rendered.settle(20)


def _lines_through_the_states(bar) -> list:
    """AK-397: the line count after each state that changes what the row
    shows -- a caption, the action buttons, the progress bar, the status."""
    from nrplanner import advisorbar
    from tests import rendered

    seen = [bar.lines]
    for change in (lambda: _suggest(bar),
                   lambda: bar._show(advisorbar.Situation(
                       advisorbar.State.APPLIED, goal_label="Maximise damage",
                       slots=6, slots_filled=1)),
                   bar._on_started,
                   bar._waiting_is_worth_saying,
                   lambda: bar._on_failed(A_LONG_FAILURE),
                   lambda: bar._show(advisorbar.Situation(
                       advisorbar.State.NOTHING_YET))):
        change()
        rendered.settle(20)
        seen.append(bar.lines)
    return seen


def _the_threshold(planner, bar) -> dict:
    """AK-395, AK-397 and AK-404 for each direction, one px under the
    one-line need and at it."""
    from nrplanner import advisorbar
    from tests import rendered

    figures = {}
    for goal_id in advisorbar.GOAL_ORDER:
        bar.choose_goal(goal_id)
        rendered.settle(20)
        need = bar._lines.one_line_need()
        figures[goal_id] = {"need": need}
        for step in (-1, 0):
            _at_row_width(planner, bar, need + step)
            lines = bar.lines
            # AK-404: another layout pass at the same width.
            bar.layout().invalidate()
            bar.layout().activate()
            rendered.settle(20)
            figures[goal_id][str(step)] = {
                "row_width": bar.width(),
                "lines": lines,
                "after_another_pass": bar.lines,
                "through_the_states": _lines_through_the_states(bar),
            }
    bar.choose_goal("max_damage")
    rendered.settle(20)
    return figures


def _the_window_minimum(planner, bar) -> dict:
    """AK-400: the window's least width in every direction, with and without
    a suggestion, and the row at the narrowest width the window takes."""
    from nrplanner import advisorbar
    from tests import rendered

    minimums = []
    for goal_id in advisorbar.GOAL_ORDER:
        bar.choose_goal(goal_id)
        rendered.settle(20)
        minimums.append(planner.minimumSizeHint().width())
        _suggest(bar)
        minimums.append(planner.minimumSizeHint().width())
    bar.choose_goal("max_damage")
    _suggest(bar)
    planner.resize(300, planner.height())
    rendered.settle(20)
    return {"window_minimums": minimums, "width": planner.width()}


def _tab_chain(bar, controls) -> list:
    """The row's controls in the order Tab reaches them, from `goal_box`."""
    from PySide6.QtCore import Qt

    names = {id(widget): name for name, widget in controls}
    chain = []
    widget = bar.goal_box
    while True:
        if (id(widget) in names and not widget.isHidden()
                and widget.focusPolicy() & Qt.TabFocus):
            chain.append(names[id(widget)])
        widget = widget.nextInFocusChain()
        if widget is bar.goal_box:
            return chain


def _across_the_break(planner, bar, controls) -> dict:
    """AK-403: the same chain, focus and names on both sides of the break,
    the row dragged across it with `Optimize` holding the focus."""
    from tests import rendered

    names = ("goal_box", "hit_with_box", "damage_type_box")
    need = bar._lines.one_line_need()
    _at_row_width(planner, bar, need)
    bar.optimize_button.setFocus()
    rendered.settle(20)
    sides = {}
    for step in ("0", "-1"):
        _at_row_width(planner, bar, need + int(step))
        sides[step] = {
            "lines": bar.lines,
            "tab_chain": _tab_chain(bar, controls),
            "focus_is_optimize": planner.focusWidget() is bar.optimize_button,
            "accessible_names": [getattr(bar, name).accessibleName()
                                 for name in names],
        }
    return sides


def _the_sheet(planner) -> dict:
    """The stat sheet's viewport, and every drawn child cut at its edge.

    The grid labels of the last `draw` but one are still children here,
    each at Qt's 640-px default because no layout pass ever reached them:
    this process runs no event loop, so their `deleteLater` is delivered by
    hand first, as `conftest.deferred_deletes_are_done` does in the suite.
    """
    from PySide6.QtCore import QCoreApplication, QEvent
    from PySide6.QtWidgets import QLabel, QWidget

    from tests import rendered

    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    rendered.settle(5)
    sheet = planner.stat_sheet
    drawn = [child for child in sheet.widget().findChildren(QWidget)
             if child.isVisible()]
    return {
        "viewport_width": sheet.viewport().width(),
        "cut": [(type(child).__name__,
                 child.text() if isinstance(child, QLabel) else "",
                 child.width())
                for child in rendered.clipped(drawn, sheet.viewport())],
    }


def main(snapshot: pathlib.Path) -> dict:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication, QLabel

    from nrplanner import model
    from nrplanner import app as appmod
    # After `nrplanner.app`: `conftest` renames the settings store to this
    # process on import, and `favourites` has to have read the parent's name
    # first, so the child writes where the parent's session fixture cleans.
    from tests import conftest, rendered

    app = QApplication([])
    appmod.apply_appearance(app)
    data = json.loads(snapshot.read_text(encoding="utf-8"))
    model.configure(data)
    # The frozen slot, as in the parent: this child is a process of its own
    # and the session fixture's redirect does not reach it (QA-266).
    planner = conftest.wait_for_the_save(appmod.Planner(
        data, read_save=lambda _data, _path: conftest.frozen_scan()))
    planner.setAttribute(Qt.WA_DontShowOnScreen)
    planner.show()
    rendered.settle(20)
    bar = planner.advisor_bar
    heading = next(label for label in bar.findChildren(QLabel)
                   if label is not bar.status)
    controls = [("heading", heading),
                ("goal_box", bar.goal_box),
                ("hit_with_label", bar.hit_with_label),
                ("hit_with_box", bar.hit_with_box),
                ("damage_type_label", bar.damage_type_label),
                ("damage_type_box", bar.damage_type_box),
                ("filters_button", bar.filters_button),
                ("optimize_button", bar.optimize_button),
                ("apply_button", bar.apply_button),
                ("why_button", bar.why_button),
                ("clear_button", bar.clear_button)]

    figures = {
        "platform": app.platformName(),
        "style": app.style().objectName(),
        "font": planner.font().toString(),
        "device_pixel_ratio": planner.devicePixelRatio(),
        "width": planner.width(),
        "opening_width": planner._opening_width(),
        "row_width": bar.width(),
        "lines": bar.lines,
        **_both_states(bar, controls),
        "sheet": _the_sheet(planner),
        "rooms": {},
    }
    for room in NARROW_DESKTOPS + AK_350_ROOMS:
        planner.resize(planner._opening_width(room=room), planner.height())
        rendered.settle(20)
        figures["rooms"][str(room)] = {"width": planner.width(),
                                  "row_width": bar.width(),
                                  "lines": bar.lines,
                                  **_both_states(bar, controls),
                                  "warning": _the_warning(bar, controls),
                                  "sheet": _the_sheet(planner)}
    figures["at"] = {}
    for width in LINE_WIDTHS:
        planner.resize(width, planner.height())
        rendered.settle(20)
        figures["at"][str(width)] = {"width": planner.width(),
                                     **_laid_out(bar, controls)}
    figures["threshold"] = _the_threshold(planner, bar)
    _suggest(bar)
    figures["across_the_break"] = _across_the_break(planner, bar, controls)
    figures["window_minimum"] = {**_the_window_minimum(planner, bar),
                                 **_laid_out(bar, controls)}
    planner.close()
    return figures


if __name__ == "__main__":
    print(json.dumps(main(pathlib.Path(sys.argv[1]))))
