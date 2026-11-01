"""The fixed community figures read like the game's own (T-332a).

GOAL.md non-goals, changed 2026-09-23 with the user's approval: Deep of Night,
Red variants and World Events may carry fixed community figures, and "they
appear like game data, without a mark of their own". Until then each of the
three tabs said "community-reported" on screen and two of them tinted the
material blue.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from nrplanner import deeptab, depthstab, eventstab

from tests import tabtext

#: The blue the retired `theme.COMMUNITY` painted community lines in.
RETIRED_BLUE = "#7fb2e5"
MARK = "community-reported"


def _unmarked(widget) -> None:
    assert MARK not in tabtext.everything(widget).lower(), (
        f"{type(widget).__name__} still says {MARK!r} on screen")
    tinted = [label.text() for label in widget.findChildren(QLabel)
              if RETIRED_BLUE in label.styleSheet()]
    assert not tinted, f"lines still drawn in the community blue: {tinted!r}"


@pytest.mark.parametrize("tab_class", [deeptab.DeepTab, depthstab.DepthsTab])
def test_deep_and_red_variants_carry_no_community_mark(tab_class, game_data,
                                                       qapp):
    widget = tab_class(game_data)
    try:
        _unmarked(widget)
    finally:
        widget.deleteLater()


def test_no_world_event_card_carries_a_community_mark(game_data, qapp):
    widget = eventstab.WorldEventsTab(game_data)
    try:
        assert widget.list.count(), "no world events to read"
        for row in range(widget.list.count()):
            item = widget.list.item(row)
            assert item.foreground().style() == Qt.NoBrush, (
                f"list entry {item.text()!r} is tinted")
            widget.list.setCurrentRow(row)
            _unmarked(widget)
    finally:
        widget.deleteLater()
