"""The saved-build line: nothing lies over anything (AK-405, QA-304).

The row is measured on its own, at the width it is given, because what broke
it was the width it was given: the block above the advisor row is `Ignored`
horizontally, and a single line squeezed below its minimum laid `Save` over
the field's arrow. Window widths and the 125/150 % scales are the
qa-engineer's, at the running program.
"""

from __future__ import annotations

import itertools

import pytest
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QLabel,
                               QPushButton, QWidget)

from nrplanner import app


@pytest.fixture
def row(qapp):
    box = QComboBox()
    box.setMinimumWidth(180)
    box.addItem("A saved build")
    widget = app.BuildRow(QLabel("Build"), box,
                          [QPushButton("Save"), QPushButton("Delete"),
                           QPushButton("Hide")], QCheckBox("Show hidden"))
    # A child, as in the window: a top-level widget would be held at its
    # layout's minimum, and the defect lived below that minimum.
    holder = QWidget()
    widget.setParent(holder)
    holder.show()
    yield widget
    holder.deleteLater()


def laid_out_at(widget: app.BuildRow, width: int) -> list:
    widget.setGeometry(0, 0, width, 80)
    QApplication.processEvents()
    widget.layout().activate()
    return widget._parts


def assert_nothing_overlaps(widget: app.BuildRow, width: int) -> None:
    label, box, save, delete, hide, show_hidden = laid_out_at(widget, width)
    parts = (label, box, save, delete, hide, show_hidden)
    for first, second in itertools.combinations(parts, 2):
        assert not first.geometry().intersects(second.geometry()), (
            width, first, second)
    assert box.width() >= 180
    for button in (save, delete, hide):
        assert button.width() >= button.sizeHint().width()
    for part in parts:
        assert part.geometry().right() < width
    # (d): the last 20 px of the field are the field's, never `Save`'s.
    edge = box.geometry()
    for x in range(edge.right() - 19, edge.right() + 1):
        assert widget.childAt(x, edge.center().y()) is box


def test_one_line_while_all_six_parts_fit(row):
    for width in (row.one_line_width(), row.one_line_width() + 400):
        assert_nothing_overlaps(row, width)
        assert not row.wrapped
        _label, box, *_rest, show_hidden = row._parts
        assert show_hidden.geometry().top() < box.geometry().bottom()


def test_show_hidden_goes_under_the_field_when_they_do_not(row):
    narrowest = row.one_line_width() - row._parts[-1].sizeHint().width() - 6
    for width in (row.one_line_width() - 1, narrowest):
        assert_nothing_overlaps(row, width)
        assert row.wrapped
        _label, box, *_rest, show_hidden = row._parts
        assert show_hidden.geometry().top() > box.geometry().bottom()
        assert show_hidden.geometry().left() == box.geometry().left()


def test_the_row_goes_back_to_one_line_when_it_widens(row):
    laid_out_at(row, row.one_line_width() - 1)
    assert row.wrapped
    assert_nothing_overlaps(row, row.one_line_width())
    assert not row.wrapped


def test_the_tab_order_is_the_order_on_screen(row):
    """(e): moving `Show hidden` does not move it in the focus chain."""
    label, box, save, delete, hide, show_hidden = laid_out_at(
        row, row.one_line_width() - 1)
    assert box.nextInFocusChain() is save
    assert save.nextInFocusChain() is delete
    assert delete.nextInFocusChain() is hide
    assert hide.nextInFocusChain() is show_hidden


def test_the_window_offers_a_long_build_name_in_full_and_as_text(planner):
    """A long name is cut by the field; its tooltip renders nothing."""
    planner.build_box.addItem("<b>Gladius</b><img src='x.png'>")
    planner.build_box.setCurrentIndex(planner.build_box.count() - 1)
    tip = planner.build_box.toolTip()
    assert "<img" not in tip
    assert "&lt;b&gt;Gladius&lt;/b&gt;" in tip
