"""Nothing on the stat sheet is cut at the pane's edge (DR-028, A13).

The review of T-258 read 630 px off `Flat bonuses` in a 370-px pane and
saw the pane cut in its screenshot. Neither was the sheet: the label was
hidden (no relic equipped, nothing to list) and kept the geometry of a
layout pass from before the splitter sized the pane, and the screenshot was
a `PrintWindow` bitmap of the window's logical size (1 608 px plus frame)
under a device pixel ratio of 1.25, which drops the right 388 px of the
rendering. Measured 2026-09-15 (T-259, Fusion, Segoe UI 9 pt, ratio 1.25):
every drawn child of the sheet is 348 px wide in a 356-px viewport, at
1 608 px and on both narrow desktops.

The figures come from the same window the advisor row is measured at, so
they are read off the running window under Windows, not offscreen (L-009).
"""

from __future__ import annotations

import pytest

from tests.advisor_row_at_the_window import NARROW_DESKTOPS


def test_at_the_opening_width_nothing_on_the_sheet_is_cut(
        advisor_row_at_the_window):
    sheet = advisor_row_at_the_window["sheet"]
    assert sheet["cut"] == [], (
        f"cut at the {sheet['viewport_width']}-px viewport: {sheet['cut']}")


@pytest.mark.parametrize("room", [str(room) for room in NARROW_DESKTOPS])
def test_on_a_narrow_desktop_nothing_on_the_sheet_is_cut(
        advisor_row_at_the_window, room):
    sheet = advisor_row_at_the_window["rooms"][room]["sheet"]
    assert sheet["cut"] == [], (
        f"cut at the {sheet['viewport_width']}-px viewport: {sheet['cut']}")
