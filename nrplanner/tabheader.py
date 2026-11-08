"""The two lines every content tab opens with (AK-68).

A heading that names the question the tab answers, and one sentence under it
saying what that question is -- and, where it matters, what the tab does
**not** answer.

One helper rather than one per module: three of the six tabs already carried a
private `_heading` with the same three style rules written out again each
time, and AK-68 asks for the same two lines on all six. Six copies of a style
sheet is six chances for them to drift, and drifting is exactly what A13
(`GOAL.md`) forbids.

The order is load-bearing, not decorative: AK-68 puts both lines above every
control and every figure, because a reader who meets a filter box or a count
first has to work out what the tab is for before they can use either.
"""

from __future__ import annotations

from html import escape

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QWidget

from .theme import ACCENT, MUTED


def heading(text: str) -> QLabel:
    """A tab or section title. Written in capitals by the caller."""
    label = QLabel(text)
    label.setStyleSheet(
        f"color: {ACCENT}; font-size: 12px; font-weight: bold;"
        " letter-spacing: 1px;"
    )
    return label


def question(text: str) -> QLabel:
    """The sentence under a heading saying which question the tab answers.

    Wrapped, and that is not cosmetic: an unwrapped `QLabel`'s minimum width
    is its whole text width, and `QTabWidget` hands the widest page's minimum
    to the window. One unwrapped sentence here would push every other tab's
    content off the right edge of the screen.
    """
    label = QLabel(text)
    label.setWordWrap(True)
    label.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
    return label


def legend(items: list[tuple[str, str]], columns: int = 2) -> QWidget:
    """A short bullet legend: one `term: meaning` line per entry.

    Replaces the paragraphs that used to stand over the tables -- a reader
    skims a legend for the one term they are wondering about, and a paragraph
    has to be read whole to find it.

    Laid out in `columns` columns, filled row by row, so a legend of six
    entries costs three lines and not six. Every entry is wrapped, for the
    same reason `question` is: an unwrapped label hands its whole width to
    the window.
    """
    panel = QWidget()
    grid = QGridLayout(panel)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setHorizontalSpacing(18)
    grid.setVerticalSpacing(1)
    for index, (term, meaning) in enumerate(items):
        label = QLabel(f"• <b>{escape(term, quote=False)}:</b> "
                       f"{escape(meaning, quote=False)}")
        label.setTextFormat(Qt.RichText)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        label.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        grid.addWidget(label, index // columns, index % columns,
                       Qt.AlignTop)
    for column in range(columns):
        grid.setColumnStretch(column, 1)
    return panel
