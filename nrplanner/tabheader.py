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

from PySide6.QtWidgets import QLabel

#: The gold the whole window uses for a section title.
ACCENT = "#c8a45c"
#: The grey for text that explains rather than states.
MUTED = "#8a8a8a"


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
