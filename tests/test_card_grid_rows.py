"""A packed card grid with fewer cards than the viewport holds.

1.19.0 user test, relic picker filtered to four relics at 1 400 x 1 400 px:
every card was stretched to the full height of the scroll area, icon and name
floating in the middle. Holding the grid with `AlignTop` instead stretched
nothing but laid the rows out at their size hint, so on the real window the
tallest card of a row lost the rule under its name. Both are row heights the
grid gets wrong, so both are read here as row heights -- on plain frames, no
game data.
"""

from __future__ import annotations

from PySide6.QtWidgets import QFrame, QLabel, QScrollArea, QVBoxLayout

from nrplanner import cardgrid

from tests import rendered

CARD_WIDTH = 190
HEAD_HEIGHT = 20
TEXTS = ("word " * 40, "short", "x" * 30 + " " + "y" * 29)


def card(text: str) -> QFrame:
    """A card the way the picker builds one: fixed head, wrapping text and a
    trailing stretch."""
    frame = QFrame()
    frame.setFixedWidth(CARD_WIDTH)
    layout = QVBoxLayout(frame)
    head = QLabel("head")
    head.setFixedHeight(HEAD_HEIGHT)
    layout.addWidget(head)
    body = QLabel(text)
    body.setWordWrap(True)
    layout.addWidget(body)
    layout.addStretch()
    frame.head, frame.body = head, body
    return frame


def shown(grid: cardgrid.CardGrid) -> QScrollArea:
    area = QScrollArea()
    area.setWidgetResizable(True)
    area.setWidget(grid)
    area.resize(900, 900)
    area.show()
    rendered.settle()
    return area


def rows(cards: list[QFrame]) -> list[list[QFrame]]:
    by_top: dict[int, list[QFrame]] = {}
    for each in cards:
        by_top.setdefault(each.y(), []).append(each)
    return [by_top[top] for top in sorted(by_top)]


def assert_packed(cards: list[QFrame], area: QScrollArea) -> None:
    for row in rows(cards):
        tallest = max(each.heightForWidth(each.width()) for each in row)
        assert [each.height() for each in row] == [tallest] * len(row), (
            "a card is not as tall as the tallest content of its row")
        assert len({each.head.y() for each in row}) == 1
    for each in cards:
        assert each.body.height() >= each.body.heightForWidth(
            each.body.width()), "a text is squeezed"
    bottom = max(each.y() + each.height() for each in cards)
    assert bottom < area.viewport().height(), (
        "the cards fill the viewport instead of leaving the room under them")


def test_a_short_row_stands_at_the_top_at_its_content_height(qapp):
    cards = [card(text) for text in TEXTS]
    area = shown(cardgrid.CardGrid(CARD_WIDTH, cards))
    try:
        assert len(rows(cards)) == 1
        assert_packed(cards, area)
    finally:
        area.close()
        area.deleteLater()
        rendered.settle(2)


def test_rows_added_later_are_packed_the_same_way(qapp):
    cards = [card(text) for text in TEXTS]
    grid = cardgrid.CardGrid(CARD_WIDTH, cards)
    area = shown(grid)
    try:
        area.resize(cardgrid.room_for(4, CARD_WIDTH) + 30, 900)
        rendered.settle()
        assert grid.columns == 4
        more = [card(text) for text in TEXTS]
        grid.extend(more)
        rendered.settle()
        cards += more
        assert len(rows(cards)) == 2
        assert_packed(cards, area)
    finally:
        area.close()
        area.deleteLater()
        rendered.settle(2)
