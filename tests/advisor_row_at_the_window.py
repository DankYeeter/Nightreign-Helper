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

#: A 4.12 failure sentence long enough to need shortening at any width.
A_LONG_FAILURE = ("the dataset carries no attribute curves for this "
                  "Nightfarer, so nothing could be worked out at all")


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
        "status_whole_text": bar.status.whole_text(),
        "status_tooltip": bar.status.toolTip(),
    }


def main(snapshot: pathlib.Path) -> dict:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication, QLabel

    from nrplanner import advisorbar, model
    from nrplanner import app as appmod
    from nrplanner.advisor import types
    # After `nrplanner.app`: `conftest` renames the settings store to this
    # process on import, and `favourites` has to have read the parent's name
    # first, so the child writes where the parent's session fixture cleans.
    from tests import conftest, rendered

    app = QApplication([])
    appmod.apply_appearance(app)
    data = json.loads(snapshot.read_text(encoding="utf-8"))
    model.configure(data)
    planner = conftest.wait_for_the_save(appmod.Planner(data))
    planner.setAttribute(Qt.WA_DontShowOnScreen)
    planner.show()
    rendered.settle(20)
    bar = planner.advisor_bar
    heading = next(label for label in bar.findChildren(QLabel)
                   if label is not bar.status)
    controls = [("heading", heading),
                ("goal_box", bar.goal_box),
                ("reading_box", bar.reading_box),
                ("optimize_button", bar.optimize_button),
                ("apply_button", bar.apply_button),
                ("why_button", bar.why_button),
                ("clear_button", bar.clear_button)]

    bar._on_failed(A_LONG_FAILURE)
    rendered.settle(20)
    failed = _the_row(bar, controls)

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
    suggested = _the_row(bar, controls)

    figures = {
        "platform": app.platformName(),
        "style": app.style().objectName(),
        "font": planner.font().toString(),
        "device_pixel_ratio": planner.devicePixelRatio(),
        "width": planner.width(),
        "opening_width": planner._opening_width(),
        "row_width": bar.width(),
        "failed": failed,
        "suggested": suggested,
    }
    planner.close()
    return figures


if __name__ == "__main__":
    print(json.dumps(main(pathlib.Path(sys.argv[1]))))
