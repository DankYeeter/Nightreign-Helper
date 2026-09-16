"""The effect filter window (`UI_SPEC` §3.6, AK-303..309, AK-311).

Driven with a hand-built inventory, so every count below is a count the
case wrote down; one case takes the frozen save to show the real dataset
gives the rows their names.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLabel

from nrplanner import effectfilterdialog as dlg
from nrplanner import effectfilters, inventory

EFFECTS = {
    "10": {"name": "Vigor +2"},
    "11": {"name": "attack power up"},
    "12": {"name": "Mind +1"},
    "90": {"name": "Reduced HP", "is_curse": True},
}


def _relic(*effect_ids: int, curses: tuple = ()) -> inventory.OwnedItem:
    return inventory.OwnedItem(relic_id=1, name="Relic", colour=1,
                               effect_ids=list(effect_ids), is_deep=False,
                               curse_ids=list(curses))


def _owned(*relics) -> inventory.Inventory:
    return inventory.Inventory(source="test", relic_count=len(relics),
                               relics=list(relics))


@pytest.fixture
def filters():
    marks = effectfilters.EffectFilters()
    yield marks
    for effect_id in set(marks.excluded | marks.required):
        marks.mark(effect_id, None)


@pytest.fixture
def window(qapp, filters):
    rows = dlg.rows_from(
        _owned(_relic(10, 11), _relic(10, 12, curses=(90,)), _relic(10, 10)),
        EFFECTS)
    dialog = dlg.EffectFilterWindow(filters, rows)
    yield dialog
    dialog.deleteLater()


def test_one_row_per_id_counted_in_relic_copies():
    """AK-304: three relics carry `10` (one of them twice) -- one row,
    `Copies = 3`; the curse is a row with its own type; a lost id keeps its
    number as its name."""
    rows = {row.effect_id: row for row in dlg.rows_from(
        _owned(_relic(10, 11), _relic(10, 12, curses=(90,)), _relic(10, 10),
               _relic(77)),
        EFFECTS)}
    assert rows[10] == dlg.Row(10, "Vigor +2", False, 3)
    assert rows[90] == dlg.Row(90, "Reduced HP", True, 1)
    assert rows[77].name == "effect 77"
    assert len(rows) == 5


def test_the_window_is_modal_titled_and_sorted_by_name_without_case(window):
    """AK-303, AK-308: `attack power up` sorts before `Mind +1`."""
    assert window.windowTitle() == dlg.TITLE
    assert window.isModal()
    assert window.shown_ids() == [11, 12, 90, 10]
    assert [window.table.horizontalHeaderItem(c).text()
            for c in range(window.table.columnCount())] == list(dlg.HEADINGS)
    assert window.table.item(0, dlg.COL_TYPE).text() == "Effect"
    assert window.table.item(2, dlg.COL_TYPE).text() == "Curse"
    assert window.table.item(3, dlg.COL_COPIES).data(Qt.DisplayRole) == 3


def test_the_two_boxes_are_disjoint_and_write_through(window, filters):
    """AK-305: Favourite takes a set Avoid away and the other way round,
    every click through `EffectFilters.mark`, so the store hears it."""
    favourite, avoid = window.boxes(10)
    assert favourite.toolTip() == dlg.FAVOURITE_TOOLTIP
    assert avoid.toolTip() == dlg.AVOID_TOOLTIP
    avoid.click()
    assert filters.excluded == {10} and filters.required == set()
    favourite.click()
    assert filters.required == {10} and filters.excluded == set()
    assert not avoid.isChecked()
    favourite.click()
    assert filters.required == set() and filters.excluded == set()


def test_a_marking_made_elsewhere_is_drawn_without_a_restart(window, filters):
    """AK-311: the window listens to `changed` like the `Why` dialog does."""
    filters.mark(12, effectfilters.REQUIRED)
    favourite, avoid = window.boxes(12)
    assert favourite.isChecked() and not avoid.isChecked()
    assert window.counter.text() == "4 of 4 effects  ·  1 favourited"


def test_the_counter_says_shown_of_total_and_the_set_counts(window, filters):
    """AK-307: the search narrows `shown`, never `total`; the two clauses
    stand only when their set is not empty."""
    assert window.counter.text() == "4 of 4 effects"
    filters.mark(10, effectfilters.EXCLUDED)
    filters.mark(90, effectfilters.EXCLUDED)
    filters.mark(11, effectfilters.REQUIRED)
    window.search.setText("mind")
    assert window.shown_ids() == [12]
    assert window.counter.text() == (
        "1 of 4 effects  ·  1 favourited  ·  2 avoided")


def test_the_search_speaks_the_picker_syntax(window):
    """AK-306: `NOT` and a quoted phrase, as `search.parse` reads them."""
    assert window.search.placeholderText() == dlg.SEARCH_PLACEHOLDER
    window.search.setText('NOT "+"')
    assert window.shown_ids() == [11, 90]
    window.search.setText("vigor OR mind")
    assert window.shown_ids() == [12, 10]
    window.search.setText("")
    assert len(window.shown_ids()) == 4


def test_the_three_empty_states(qapp, filters, window):
    """AK-309: two reasons for an empty grid without a search, and one
    label under the grid when the search alone empties it."""
    window.search.setText("nothing carries this")
    assert window.shown_ids() == []
    assert not window.empty.isHidden()
    assert window.empty.text() == dlg.NO_MATCH
    assert window.counter.text() == "0 of 4 effects"
    window.search.setText("")
    assert window.empty.isHidden()
    for reason in (dlg.NO_SAVE_WAS_READ, dlg.SAVE_HAS_NO_RELICS):
        empty = dlg.EffectFilterWindow(filters, [], reason)
        try:
            assert empty.table.rowCount() == 0
            assert not empty.empty.isHidden()
            assert empty.empty.text() == reason
            assert empty.counter.text() == "0 of 0 effects"
        finally:
            empty.deleteLater()


def test_tab_walks_favourite_then_avoid_and_space_toggles(window, filters):
    """AK-305: reading order within a row, Space switches the box."""
    window.show()
    QApplication.processEvents()
    favourite, avoid = window.boxes(11)
    favourite.setFocus()
    QApplication.processEvents()
    assert QApplication.focusWidget() is favourite
    QTest.keyClick(favourite, Qt.Key_Tab)
    assert QApplication.focusWidget() is avoid
    QTest.keyClick(avoid, Qt.Key_Space)
    assert filters.excluded == {11}
    window.close()


def test_sorting_by_a_marker_column_keeps_the_boxes_on_their_rows(window,
                                                                    filters):
    """AK-308: a re-sort moves the row, and the box with it (Qt keeps a cell
    widget on its index) -- the box of `10` still marks `10`."""
    filters.mark(10, effectfilters.EXCLUDED)
    window.table.sortItems(dlg.COL_AVOID, Qt.DescendingOrder)
    assert window.shown_ids()[0] == 10
    assert window.table.cellWidget(0, dlg.COL_AVOID) is window.boxes(10)[1]
    window.table.sortItems(dlg.COL_COPIES, Qt.DescendingOrder)
    assert window.shown_ids()[0] == 10


def test_the_frozen_save_names_its_rows_out_of_the_dataset(qapp, filters,
                                                            frozen_inventory,
                                                            game_data):
    """AK-304 against the real dataset: every row has a name, no row is an
    id, and there is one row per distinct id."""
    rows = dlg.rows_from(frozen_inventory, game_data["effects"])
    ids = {i for item in frozen_inventory.relics
           for i in (*item.effect_ids, *item.curse_ids)}
    assert len(rows) == len(ids) > 0
    assert not any(row.name.startswith("effect ") for row in rows)
    assert any(row.is_curse for row in rows)


def test_marks_explanation_label_is_present_and_unfocusable(window):
    """AK-313: the window carries the exact wording, and the label cannot
    take keyboard focus (it must not join the tab order)."""
    labels = [label for label in window.findChildren(QLabel)
              if label.text() == dlg.MARKS_EXPLANATION]
    assert len(labels) == 1
    assert labels[0].focusPolicy() == Qt.NoFocus
