"""The effects tab's shortened texts, and where the whole one can be read.

QA-160: the closed filter boxes cut their own value off (`Strongest only
(adds + multiplies)` in 81 px of text room) and nothing gave it back.

QA-162: a shortened column heading reached the accessibility interface as
drawn, `Comes with c…`, with an empty description on all eleven headings.
"""

from __future__ import annotations

from PySide6.QtGui import QAccessible

from nrplanner import effectstab

from tests import rendered

WIDTH = 1250


def filter_boxes(tab):
    return (tab.colour_box, tab.mode_box, tab.stacking_box, tab.kind_box)


def test_every_filter_value_stands_whole_in_the_tooltip(game_data, qapp):
    """QA-160: whatever is chosen leads the closed box's tooltip."""
    tab = effectstab.EffectsTab(game_data)
    try:
        for box in filter_boxes(tab):
            for index in range(box.count()):
                box.setCurrentIndex(index)
                assert box.toolTip().split("\n")[0] == box.currentText(), (
                    f"chose {box.currentText()!r}, the tooltip says "
                    f"{box.toolTip()!r}")
    finally:
        tab.deleteLater()


def test_the_stacking_box_keeps_its_explanation(game_data, qapp):
    """QA-160: the value goes in front of the old tooltip, not over it."""
    tab = effectstab.EffectsTab(game_data)
    try:
        box = tab.stacking_box
        box.setCurrentIndex(box.count() - 1)
        assert box.toolTip().split("\n")[1:] == [
            "How a second copy behaves, and whether the number adds or "
            "multiplies"]
    finally:
        tab.deleteLater()


def heading_cells(table) -> list:
    """The column headers as the accessibility interface hands them out."""
    interface = QAccessible.queryAccessibleInterface(table)
    cells = (interface.child(i) for i in range(interface.childCount()))
    return [cell for cell in cells
            if cell is not None and cell.role() == QAccessible.ColumnHeader]


def test_a_shortened_heading_tells_assistive_tools_its_whole_name(
        game_data, qapp):
    """QA-162: name = the full heading, description = its tooltip."""
    with rendered.laid_out(game_data, "effects_tab", WIDTH) as (_, tab):
        table = tab.table
        drawn = [table.horizontalHeaderItem(c).text()
                 for c in range(table.columnCount())]
        assert drawn != effectstab.COLUMNS, (
            f"no heading is shortened at {WIDTH} px, so this case reads "
            f"nothing the finding is about")
        cells = heading_cells(table)
        assert [cell.text(QAccessible.Name) for cell in cells] == (
            effectstab.COLUMNS)
        assert [cell.text(QAccessible.Description) for cell in cells] == [
            table.horizontalHeaderItem(c).toolTip()
            for c in range(table.columnCount())]
