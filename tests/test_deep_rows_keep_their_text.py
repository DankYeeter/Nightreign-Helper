"""A vessel row keeps room for its name and figures with Deep of Night on.

Six slots in one line left 95 px of text in a 288 px list (2560x1600 at
150 %, the window at its opening size): `AR +87 % / Defense +29 %` read
`AR +87 % / Defe…`. A list that narrow draws the Deep slots under the others.
"""

from PySide6.QtCore import Qt

from nrplanner.app import Planner

STEP = Planner.ROW_SLOT + 2
IN_A_LINE = Planner.ROW_CELL + 5 + 6 * STEP
IN_TWO = Planner.ROW_CELL + 5 + 3 * STEP


def _art_of_a_deep_vessel(planner):
    """The row image of the first vessel that has three Deep slots."""
    listed = planner.chalice_list
    for row in range(listed.count()):
        vessel = listed.item(row).data(Qt.UserRole)
        if vessel and len(vessel.get("deep_slots") or []) == 3:
            return listed.item(row).icon().pixmap(listed.iconSize())
    raise AssertionError("no vessel with three Deep slots")


def _narrowest_list_that_holds_a_line(planner) -> int:
    listed = planner.chalice_list
    return (IN_A_LINE + Planner.ROW_TEXT_FLOOR + 2 * listed.frameWidth()
            + listed.verticalScrollBar().sizeHint().width())


def test_a_narrow_list_puts_the_deep_slots_under_the_others(planner):
    listed = planner.chalice_list
    listed.resize(288, 400)
    planner.deep_check.setChecked(True)
    assert listed.iconSize().height() == 2 * STEP
    art = _art_of_a_deep_vessel(planner)
    assert (art.width(), art.height()) == (IN_TWO, 2 * STEP)


def test_a_wide_list_keeps_the_six_in_one_line(planner):
    listed = planner.chalice_list
    listed.resize(_narrowest_list_that_holds_a_line(planner), 400)
    planner.deep_check.setChecked(True)
    assert listed.iconSize().height() == Planner.ROW_CELL
    art = _art_of_a_deep_vessel(planner)
    assert (art.width(), art.height()) == (IN_A_LINE, Planner.ROW_CELL)


def test_one_pixel_less_than_that_is_two_lines(planner):
    listed = planner.chalice_list
    listed.resize(_narrowest_list_that_holds_a_line(planner) - 1, 400)
    planner.deep_check.setChecked(True)
    assert listed.iconSize().height() == 2 * STEP


def test_without_deep_a_narrow_list_stays_at_one_line(planner):
    listed = planner.chalice_list
    listed.resize(288, 400)
    planner.deep_check.setChecked(True)
    planner.deep_check.setChecked(False)
    assert listed.iconSize().height() == Planner.ROW_CELL
