"""Relic cards, armament tiles and the favourite menu: pointer, ring, name.

QA-157: the relic cards, the custom-relic tile, the armament tiles and the
favourite-menu portraits had a pointing hand but no mark for the card the
pointer is on -- the class QA-154 fixed on the Nightlord grid, with the same
8 px gaps. The pointer is delivered with `sendEvent`, as in
`test_nightlord_selection.py`, which says why `QTest.mouseMove` cannot be.

QA-158: the favourite menu showed the ten Nightfarers as bare portraits, the
name only in a tooltip -- QA-155(b) a second time.

QA-078: no test read which armament tile carries the gold ring.
"""

from __future__ import annotations

import re
from types import SimpleNamespace

import pytest
from PySide6.QtCore import QEvent, QPoint, QPointF, Qt
from PySide6.QtGui import QColor, QCursor, QEnterEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QToolButton

from nrplanner import favourites, relicpicker, weaponslots
from nrplanner.theme import ACCENT, HOVER_FILL, PANEL


def pointer_onto(widget) -> None:
    centre = QPointF(widget.rect().center())
    QApplication.sendEvent(widget, QEnterEvent(
        centre, centre, QPointF(widget.mapToGlobal(centre.toPoint()))))


def pointer_off(widget) -> None:
    QApplication.sendEvent(widget, QEvent(QEvent.Leave))


def fill(widget) -> str:
    """The colour drawn just inside the left border."""
    image = widget.grab().toImage()
    return image.pixelColor(4, image.height() // 2).name()


def edge(widget) -> str:
    """The border as the card declares it -- a dashed one has no one pixel."""
    return re.search(r"border: [^;]+;", widget.styleSheet()).group()


def relic_card(selected: bool):
    item = SimpleNamespace(name="A relic", has_curse=False)
    return relicpicker.RelicCard(item, ["An effect"], None, selected,
                                 lambda _item: None)


CARDS = {
    "relic card": lambda: relic_card(False),
    "selected relic card": lambda: relic_card(True),
    "custom relic tile": lambda: relicpicker.CustomRelicCard(
        [], False, lambda: None),
    "armament tile": lambda: weaponslots.WeaponTile(
        0, lambda *_: None, lambda *_: None, lambda *_: None),
}


@pytest.mark.parametrize("make", CARDS.values(), ids=CARDS.keys())
def test_the_pointer_fills_the_card_and_leaves_its_edge(qapp, make):
    """QA-157: hover fills, leave unfills, the edge never moves (QA-154)."""
    card = make()
    # Shown, and clear of wherever the real pointer is: a card re-reads the
    # pointer on show, move and resize (QA-164), and a hidden one gets those
    # again on every grab.
    card.move(QCursor.pos() + QPoint(40, 40))
    card.show()
    QApplication.processEvents()
    try:
        plain_edge = edge(card)
        assert fill(card) == QColor(PANEL).name()

        pointer_onto(card)
        assert fill(card) == QColor(HOVER_FILL).name(), (
            "the card the pointer is on looks like every other card")
        assert edge(card) == plain_edge, (
            "hover moved the edge, which belongs to selection")

        pointer_off(card)
        assert fill(card) == QColor(PANEL).name(), (
            "the mark stayed after the pointer left")
    finally:
        card.close()
        card.deleteLater()


@pytest.fixture
def favourite_menu(game_data, qapp, monkeypatch):
    monkeypatch.setattr(favourites, "heroes_for", lambda _item: set())
    menu = relicpicker.FavouriteMenu(None, object(), game_data["heroes"],
                                     None)
    yield menu
    menu.deleteLater()


def portraits(menu) -> list[QToolButton]:
    return menu.findChildren(QToolButton)


def test_the_favourite_menu_marks_the_portrait_under_the_pointer(
        favourite_menu):
    """QA-157: the menu's portraits answer the pointer too."""
    tile = portraits(favourite_menu)[0]
    assert ":hover" in tile.styleSheet() and HOVER_FILL in tile.styleSheet()
    plain = tile.grab().toImage().pixelColor(4, 4).name()
    tile.setAttribute(Qt.WA_UnderMouse, True)
    try:
        hovered = tile.grab().toImage().pixelColor(4, 4).name()
    finally:
        tile.setAttribute(Qt.WA_UnderMouse, False)
    assert (plain, hovered) == (QColor(PANEL).name(),
                                QColor(HOVER_FILL).name())


def test_the_favourite_menu_names_every_nightfarer(favourite_menu, game_data):
    """QA-158: the name stands under the portrait, whole, on every tile."""
    names = [hero["name"] for hero in game_data["heroes"]]
    tiles = portraits(favourite_menu)
    assert [tile.text() for tile in tiles] == names
    for tile in tiles:
        assert tile.toolButtonStyle() == Qt.ToolButtonTextUnderIcon
        assert not tile.icon().isNull(), (
            f"{tile.text()}: no portrait, so the name is all the tile is")
        # Whether the name fits the width is a Windows font question -- the
        # offscreen platform's fallback font is a third wider; see
        # `relicpicker.NAME_POINT_SIZE`. That it has a line of its own is not.
        assert tile.height() > relicpicker.HERO_ICON + 8, (
            f"{tile.text()}: no room under the portrait for the name")
    assert len({tile.height() for tile in tiles}) == 1, (
        "tiles with and without artwork came out different heights")


def test_the_gold_ring_follows_the_active_armament(planner):
    """QA-078: after a click on tile i, tile i and only it carries the ring."""
    tiles = planner.stat_sheet.weapon_tiles
    for index, tile in enumerate(tiles):
        QTest.mouseClick(tile, Qt.LeftButton)
        assert [t.active for t in tiles] == [
            i == index for i in range(len(tiles))]
        ringed = [i for i, t in enumerate(tiles) if ACCENT in t.styleSheet()]
        assert ringed == [index], (
            f"clicked tile {index}, the gold ring is on {ringed}")
