"""How large the interface is drawn, as the player wants it.

Qt reads Windows' own display scaling when the QApplication is made, and the
program has always taken whatever that came to. That is right for most
machines and not adjustable on any: a player who finds the sheet small on a
4K monitor, or wants more of the relic list on screen than the desktop's own
scaling allows, had nothing to reach for.

The factor is applied through `QT_SCALE_FACTOR`, which multiplies whatever
the operating system already asked for rather than replacing it -- so
**Automatic is the absence of the variable**, not a factor of its own, and
there is deliberately no "100%" entry saying the same thing twice.

It has to be in the environment before the QApplication exists, which is why
`main()` reads it first and why choosing a new one offers a restart rather
than redrawing. Qt fixes the scale once, at startup, and gives no way to
change it afterwards; a control that quietly did nothing until the next
launch would look broken.
"""

from __future__ import annotations

import os

from PySide6.QtCore import QSettings

from . import favourites

KEY = "ui/scale"

# (what the player sees, what is stored). "" is Automatic.
CHOICES: list[tuple[str, str]] = [
    ("Automatic", ""),
    ("90%", "0.9"),
    ("110%", "1.1"),
    ("125%", "1.25"),
    ("150%", "1.5"),
    ("175%", "1.75"),
    ("200%", "2.0"),
]

_VALUES = {value for _label, value in CHOICES}


def _settings() -> QSettings:
    return QSettings(favourites.ORG, favourites.APP)


def stored() -> str:
    """The stored choice, always one of the CHOICES values."""
    value = str(_settings().value(KEY, "", type=str) or "")
    return value if value in _VALUES else ""


def set_stored(value: str) -> None:
    _settings().setValue(KEY, value or "")


def label_for(value: str) -> str:
    for label, stored_value in CHOICES:
        if stored_value == value:
            return label
    return CHOICES[0][0]


def apply_to_environment() -> None:
    """Tell Qt the factor, before there is a QApplication to tell.

    A factor already in the environment wins. Someone who starts the program
    with QT_SCALE_FACTOR set has said something more specific than a setting
    chosen once inside it, and quietly overruling that would leave them with
    no way to win.
    """
    if os.environ.get("QT_SCALE_FACTOR"):
        return
    value = stored()
    if value:
        os.environ["QT_SCALE_FACTOR"] = value
