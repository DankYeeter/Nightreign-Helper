"""Symbols per row of the pool popup at scale 1.2 (QA-320), in a child
process: Qt reads `QT_SCALE_FACTOR` once, before the QApplication exists.

The anchor is a ringed chip, the way the popup opens in the window. Run as
`python -m tests.pool_popup_at_scale`; the parent side is `measure`.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SCALE = "1.2"
#: Bar widths around and above the narrowest one a cell of POPUP_CELL needs.
WIDTHS = (300, 330, 348, 420, 600)
#: 30 symbols are five full rows of six, no scrollbar; 36 need one.
COUNTS = (30, 36)


def measure() -> dict:
    done = subprocess.run(
        [sys.executable, "-m", "tests.pool_popup_at_scale"],
        cwd=REPO, capture_output=True, text=True, check=False,
        env={**os.environ, "QT_QPA_PLATFORM": "offscreen",
             "QT_SCALE_FACTOR": SCALE})
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout.splitlines()[-1])


def main() -> dict:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication

    from nrplanner import app as appmod
    from nrplanner import castingbar

    app = QApplication([])
    appmod.apply_appearance(app)
    rows = {}
    for count in COUNTS:
        pool = tuple({"id": i, "name": f"Art {i}"} for i in range(count))
        chip = castingbar.Chip("art", "ART", pool[0], pool, False, 0, True,
                               "")
        anchor = castingbar.ChipWidget(chip, None, lambda _widget: None)
        for width in WIDTHS:
            popup = castingbar.PoolPopup(chip, None, lambda *_: None, anchor,
                                         width)
            popup.setAttribute(Qt.WA_DontShowOnScreen)
            popup.show()
            app.processEvents()
            tops = {popup.list.visualItemRect(popup.list.item(i)).y()
                    for i in range(count)}
            rows[f"{count}@{width}"] = len(tops)
            popup.close()
    return {"scale": app.primaryScreen().devicePixelRatio(), "rows": rows}


if __name__ == "__main__":
    print(json.dumps(main()))
