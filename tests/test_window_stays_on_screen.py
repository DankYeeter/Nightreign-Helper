"""The window opens on the screen, not partly beside it (QA-175).

Found at 2560x1600 and 150 %: Windows placed the window for the small size
it was created with, `showEvent` then set the opening size over that spot,
and the frame ran 266 px past the right edge and 101 px past the bottom.

The desktop under the offscreen platform is 800x600 and the window's own
minimum is wider than that, so "entirely on screen" is not a claim this case
can make. What it asserts instead is the rule: no more of the window is off
the desktop than the desktop forces -- the visible part is as large as the
smaller of the two in each direction.
"""

from __future__ import annotations

from PySide6.QtCore import QSize

from nrplanner import app as appmod

from tests import rendered
from tests.conftest import clear_settings


def test_a_window_placed_near_the_corner_is_pushed_back_onto_the_desktop(
        game_data, qapp):
    clear_settings()
    window = appmod.Planner(game_data)
    try:
        room = window.screen().availableGeometry()
        window.move(room.right() - 100, room.bottom() - 100)
        window.show()
        rendered.settle()

        frame = window.frameGeometry()
        visible = frame.intersected(room).size()
        assert visible == QSize(min(frame.width(), room.width()),
                                min(frame.height(), room.height())), (
            f"the frame {frame} shows only {visible} of itself on the "
            f"{room} desktop")
    finally:
        window.close()
        window.deleteLater()
        rendered.settle(2)
