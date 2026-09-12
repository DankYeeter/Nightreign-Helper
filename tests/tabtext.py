"""Read what a content tab actually draws, not what it was asked to draw.

QA-137 measured the gap these helpers exist to close: seven display mutations
applied at once -- every percentage on the effects tab times ten, the win
rating at 999, a boss debuff at x9.9 -- left the suite at 622 of 622 green,
while the control mutation on the one guarded tab took six cases down. Five of
the six content tabs were read by nothing.

**Everything here reads a widget.** A test standing on `tab._summary()` or on
`tab.ratings` guards the function and not the screen, and the screen is where
QA-125 through QA-136 all lived. The rule the arsenal guard was built on
(`test_arsenal_tab_asks_the_facade`, "read off the rendered tile, not off the
list behind it") is the rule for the whole family.

**Tooltips count as displayed text.** Three of the acceptance criteria put a
sentence in a header tooltip and one of them -- AK-79 -- says a definition
appears exactly once on the tab. A count that skipped the tooltips could pass
with the same sentence standing twice.
"""

from __future__ import annotations

import re

from PySide6.QtWidgets import QLabel, QTableWidget, QWidget

#: Qt's own markup, which several panels build their text out of. Stripped
#: rather than matched around: a test looking for a sentence should not have
#: to know which half of it sits inside a `<span>`.
_TAG = re.compile(r"<[^>]+>")
_ENTITY = {"&nbsp;": " ", "&amp;": "&", "&lt;": "<", "&gt;": ">",
           "&#9608;": "█"}


def plain(markup: str) -> str:
    """`markup` with tags removed and the entities these panels use resolved.

    Whitespace is collapsed, so a sentence broken across two `<div>`s reads as
    one line and a test can search for it whole.
    """
    text = _TAG.sub(" ", markup)
    for entity, character in _ENTITY.items():
        text = text.replace(entity, character)
    return " ".join(text.split())


def labels(widget: QWidget) -> list[str]:
    """Every non-empty label the widget draws, in the order Qt built them.

    Construction order and layout order are the same thing in all six tabs --
    each builds its widgets in the order it adds them -- which is what lets
    `first_line` below answer "what does a reader meet first".
    """
    return [plain(label.text()) for label in widget.findChildren(QLabel)
            if plain(label.text())]


def first_line(widget: QWidget) -> str:
    """The first piece of text a reader meets on this tab.

    AK-68 is a claim about order, not about presence: the heading stands above
    every control and every figure, because a reader who meets a filter box
    first has to work out what the tab is for before they can use it.
    """
    found = labels(widget)
    assert found, "this widget draws no text at all"
    return found[0]


def table_text(table: QTableWidget) -> list[str]:
    """Header labels, header tooltips, cell texts and cell tooltips."""
    out: list[str] = []
    for column in range(table.columnCount()):
        item = table.horizontalHeaderItem(column)
        if item is not None:
            out += [plain(item.text()), plain(item.toolTip())]
    for row in range(table.rowCount()):
        for column in range(table.columnCount()):
            cell = table.item(row, column)
            if cell is not None:
                out += [plain(cell.text()), plain(cell.toolTip())]
    return [text for text in out if text]


def everything(widget: QWidget) -> str:
    """One string holding every piece of text the tab can put on screen.

    Labels, their tooltips, and every table it owns. Joined with newlines so a
    search for a sentence cannot run over the join between two of them and
    match text that is never next to itself on screen.
    """
    pieces: list[str] = []
    for label in widget.findChildren(QLabel):
        pieces += [plain(label.text()), plain(label.toolTip())]
    for table in widget.findChildren(QTableWidget):
        pieces += table_text(table)
    return "\n".join(piece for piece in pieces if piece)
