"""Three display findings of 2026-11-23, on 2560x1600 at 150 % scaling.

* A vessel row is three lines -- name, slots, figures -- so six slots in Deep
  of Night no longer take the width the figures are read in.
* An outer pane that gave way to the advisor row grows back when the window
  has the room again.
* The sign of a run is a spinner beside `Optimize`, not a bar in the row.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget

from nrplanner import advisorbar
from nrplanner.app import Planner, _Panes

STEP = Planner.ROW_SLOT + 2


def _vessel_rows(planner):
    listed = planner.chalice_list
    return [listed.item(row) for row in range(listed.count())
            if listed.item(row).data(Qt.UserRole)]


def _slots_width(item) -> int:
    return item.data(advisorbar.VESSEL_SLOTS_ROLE).width()


def test_the_row_icon_is_the_vessel_alone(planner):
    side = Planner.ROW_CELL
    size = planner.chalice_list.iconSize()
    assert (size.width(), size.height()) == (side, side)


def test_the_slots_are_a_line_of_their_own_three_or_six_wide(planner):
    planner.deep_check.setChecked(False)
    assert {_slots_width(item) for item in _vessel_rows(planner)} == {
        3 * STEP - 2}
    planner.deep_check.setChecked(True)
    deep = [item for item in _vessel_rows(planner)
            if len(item.data(Qt.UserRole).get("deep_slots") or []) == 3]
    assert deep
    assert {_slots_width(item) for item in deep} == {6 * STEP - 2}


def test_a_row_is_tall_enough_for_its_three_lines(planner):
    listed = planner.chalice_list
    row = listed.row(_vessel_rows(planner)[0])
    font = listed.fontMetrics().height()
    assert advisorbar.VESSEL_ROW_HEIGHT >= (
        font + Planner.ROW_SLOT + advisorbar.COMPARE_POINT_PX
        + 2 * advisorbar.VESSEL_LINE_GAP)
    assert listed.sizeHintForRow(row) >= advisorbar.VESSEL_ROW_HEIGHT
    assert not listed.grab().isNull()


def _three_panes(qapp, need: int, wanted, sizes, width: int) -> _Panes:
    panes = _Panes(lambda: need, wanted)
    panes.setChildrenCollapsible(False)
    panes.setHandleWidth(0)
    for _ in range(3):
        child = QWidget()
        child.setMinimumWidth(50)
        panes.addWidget(child)
    panes.setStretchFactor(1, 1)
    panes.resize(width, 100)
    panes.setSizes(sizes)
    panes.show()
    QApplication.processEvents()
    return panes


def test_an_edge_that_gave_way_grows_back_out_of_the_middles_surplus(qapp):
    panes = _three_panes(qapp, 500, [430, 370], [200, 500, 200], 900)
    panes.resize(1000, 100)
    QApplication.processEvents()
    left, middle, right = panes.sizes()
    assert middle == 500
    assert left + right == 500
    assert 200 < left <= 430 and 200 < right <= 370
    panes.close()


def test_no_edge_grows_past_what_it_wants(qapp):
    panes = _three_panes(qapp, 300, [430, 370], [430, 300, 370], 1100)
    panes.resize(1600, 100)
    QApplication.processEvents()
    assert panes.sizes() == [430, 800, 370]
    panes.close()


def test_a_drag_is_what_the_edges_want_from_then_on(qapp):
    panes = _three_panes(qapp, 300, [430, 370], [250, 600, 250], 1100)
    panes.wanted = [430, 370]
    panes.setSizes([250, 600, 250])
    panes.splitterMoved.emit(250, 1)
    assert panes.wanted == [250, 250]
    panes.resize(1300, 100)
    QApplication.processEvents()
    assert panes.sizes() == [250, 800, 250]
    panes.close()


def test_the_sign_of_a_run_is_a_spinner_beside_optimize(planner):
    bar = planner.advisor_bar
    assert isinstance(bar.progress, advisorbar._Spinner)
    assert bar.progress.isHidden()
    assert not bar.progress._timer.isActive()
    doing = bar.optimize_button.parentWidget().layout()
    assert (doing.indexOf(bar.progress)
            == doing.indexOf(bar.optimize_button) + 1)
