"""The picture behind the whole window, and the rail that replaces the tab bar.

The window is a stack of translucent panels over one fixed picture. Qt's
widgets cannot blur what is behind them, and they do not have to: the picture
never moves, so it is softened once, here, and every panel on top of it is a
plain translucent fill. That is the whole of the "glass".

**Where the picture comes from.** Nothing ships with the program (see
`paths`), and that includes artwork: the picture is read from the icon pack
the first run builds out of the player's own installed game, if that pack
holds one (`BACKDROP_FILE`). Where it does not -- an older pack, no game, a
runner -- the scene is painted here from gradients, and is nobody's artwork
but this file's.
"""

from __future__ import annotations

import math
import random

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import (
    QBrush, QColor, QImage, QLinearGradient, QPainter, QPainterPath, QPen,
    QPixmap, QRadialGradient,
)
from PySide6.QtWidgets import (
    QButtonGroup, QFrame, QLabel, QPushButton, QSizePolicy, QVBoxLayout,
    QWidget,
)

from . import paths
from .theme import ACCENT, ACCENT_BRIGHT, MUTED, SERIF

#: The file the icon pack may hold; see the module docstring.
BACKDROP_FILE = "backdrop.png"

#: The painted scene is drawn this many times smaller than the window and
#: scaled up smoothly: that is the blur, and it costs nothing per frame.
SOFTEN = 14

SKY_TOP = QColor("#05070f")
SKY_MID = QColor("#0d1230")
SKY_LOW = QColor("#241a4d")
GLOW = QColor(217, 181, 106)
HAZE = QColor(120, 110, 255)


def painted_scene(size: QSize) -> QPixmap:
    """A night sky, a far light and two ridges, in the window's own colours."""
    w, h = max(size.width(), 16), max(size.height(), 16)
    small = QImage(max(w // SOFTEN, 8), max(h // SOFTEN, 8),
                   QImage.Format_ARGB32_Premultiplied)
    sw, sh = small.width(), small.height()
    p = QPainter(small)
    p.setRenderHint(QPainter.Antialiasing)

    sky = QLinearGradient(0, 0, 0, sh)
    sky.setColorAt(0.0, SKY_TOP)
    sky.setColorAt(0.45, SKY_MID)
    sky.setColorAt(1.0, SKY_LOW)
    p.fillRect(small.rect(), sky)

    def glow(cx, cy, rx, ry, colour, alpha):
        p.save()
        p.translate(cx * sw, cy * sh)
        p.scale(rx * sw, ry * sh)
        g = QRadialGradient(0, 0, 1)
        c = QColor(colour)
        c.setAlpha(alpha)
        g.setColorAt(0, c)
        c.setAlpha(0)
        g.setColorAt(1, c)
        p.fillRect(QRectF(-1, -1, 2, 2), g)
        p.restore()

    glow(0.12, -0.10, 0.45, 0.55, HAZE, 80)
    glow(0.72, 1.00, 0.55, 0.55, HAZE, 90)
    glow(0.74, 1.08, 0.30, 0.70, GLOW, 110)

    # The far light: a trunk and a crown of branches, wide and soft.
    def branch(points, width, alpha):
        path = QPainterPath(QPointF(points[0][0] * sw, points[0][1] * sh))
        (c1, c2, end) = points[1:]
        path.cubicTo(c1[0] * sw, c1[1] * sh, c2[0] * sw, c2[1] * sh,
                     end[0] * sw, end[1] * sh)
        fade = QLinearGradient(0, points[0][1] * sh, 0, end[1] * sh)
        a, b = QColor(255, 242, 200, alpha), QColor(217, 181, 106, 0)
        fade.setColorAt(0, a)
        fade.setColorAt(1, b)
        pen = QPen(QBrush(fade), max(width * sw / 1600, 0.6))
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        p.drawPath(path)

    branch([(.737, 1.0), (.735, .78), (.744, .58), (.740, .37)], 70, 34)
    branch([(.740, .58), (.706, .48), (.662, .44), (.619, .33)], 40, 20)
    branch([(.741, .52), (.781, .43), (.831, .41), (.875, .28)], 40, 20)
    branch([(.740, .44), (.719, .36), (.700, .29), (.687, .19)], 30, 16)
    branch([(.741, .42), (.762, .33), (.789, .27), (.806, .17)], 30, 16)

    def ridge(points, colour):
        path = QPainterPath(QPointF(0, sh))
        for x, y in points:
            path.lineTo(x * sw, y * sh)
        path.lineTo(sw, sh)
        p.fillPath(path, colour)

    ridge([(0, .80), (.075, .77), (.13, .81), (.21, .71), (.26, .78),
           (.35, .73), (.40, .80), (.49, .78), (.56, .84), (.65, .81),
           (.74, .87), (.83, .82), (.91, .88), (1, .83)],
          QColor(5, 6, 13, 190))
    ridge([(0, .89), (.10, .86), (.19, .91), (.29, .87), (.39, .92),
           (.50, .89), (.63, .94), (.75, .91), (.88, .96), (1, .92)],
          QColor(3, 4, 9, 230))
    p.end()

    scene = QPixmap.fromImage(
        small.scaled(w, h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))

    # Rain, drawn sharp over the soft scene. Seeded: the same window size
    # gets the same rain, so the picture does not flicker on a resize back.
    rng = random.Random(7)
    p = QPainter(scene)
    p.setRenderHint(QPainter.Antialiasing)
    slant = math.tan(math.radians(14))
    for _ in range(int(w * h / 9000)):
        x, y = rng.uniform(-0.1 * w, w), rng.uniform(0, h)
        length = rng.uniform(18, 70)
        p.setPen(QPen(QColor(190, 200, 255, rng.randint(8, 26)), 1))
        p.drawLine(QPointF(x, y), QPointF(x + slant * length, y + length))
    p.end()
    return scene


def game_scene(size: QSize) -> QPixmap | None:
    """The picture out of the player's own icon pack, fitted and dimmed."""
    path = paths.icons_dir() / BACKDROP_FILE
    if not path.is_file():
        return None
    source = QImage(str(path))
    if source.isNull():
        return None
    w, h = max(size.width(), 16), max(size.height(), 16)
    # Softened the same way the painted scene is, then covered and centred.
    soft = source.scaled(max(source.width() // 3, 8),
                         max(source.height() // 3, 8),
                         Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    cover = soft.scaled(w, h, Qt.KeepAspectRatioByExpanding,
                        Qt.SmoothTransformation)
    scene = QPixmap(w, h)
    p = QPainter(scene)
    p.drawImage((w - cover.width()) // 2, (h - cover.height()) // 2, cover)
    # Text has to stay readable over any picture: a dark veil, heavier at
    # the top where the headings are.
    veil = QLinearGradient(0, 0, 0, h)
    veil.setColorAt(0, QColor(5, 7, 15, 190))
    veil.setColorAt(1, QColor(5, 7, 15, 120))
    p.fillRect(scene.rect(), veil)
    p.end()
    return scene


class Backdrop(QWidget):
    """The central widget: paints the picture, holds everything else."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._scene: QPixmap | None = None

    def resizeEvent(self, event) -> None:
        self._scene = None
        super().resizeEvent(event)

    def paintEvent(self, _event) -> None:
        if self._scene is None or self._scene.size() != self.size():
            self._scene = game_scene(self.size()) or painted_scene(self.size())
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._scene)


#: The rail at its full width, and the least it shrinks to before the window
#: stops getting narrower. At the narrow end an entry says its short name:
#: the window has to fit a 1366 px laptop, and the three panes of the Build
#: planner need what is left of that.
RAIL_WIDTH = 168
RAIL_NARROW = 100
#: Below this the full names no longer fit their buttons.
RAIL_SHORT_BELOW = 150

#: What an entry is called while the rail is narrow.
SHORT_NAMES = {
    "Build planner": "Build",
    "Effects && chances": "Effects",
    "Weapons && spells": "Weapons",
    "Nightlords": "Lords",
    "Deep of Night": "Deep",
    "Red variants": "Red",
    "World Events": "Events",
}


class NavRail(QFrame):
    """The list of views down the left edge, in place of a row of tabs."""

    chosen = Signal(int)
    #: The rail went narrow (True) or came back to its full width.
    narrowed = Signal(bool)

    def __init__(self, version: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("navRail")
        self.setMinimumWidth(RAIL_NARROW)
        self.setMaximumWidth(RAIL_WIDTH)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(8, 14, 8, 10)
        self._layout.setSpacing(3)
        self._names: dict[int, str] = {}
        self._short = False

        self.brand = QLabel("NIGHTREIGN")
        self.brand.setObjectName("brand")
        self.brand.setMinimumWidth(0)
        self._layout.addWidget(self.brand)
        self.sub = QLabel(f"Helper {version}")
        self.sub.setStyleSheet(f"color: {MUTED}; font-size: 11px;"
                               " padding: 0 6px 10px 6px;")
        self._layout.addWidget(self.sub)

        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        self.group.idClicked.connect(self.chosen)
        self._entries = QVBoxLayout()
        self._entries.setSpacing(3)
        self._layout.addLayout(self._entries)
        self._layout.addStretch(1)
        self.foot = QVBoxLayout()
        self.foot.setSpacing(6)
        self._layout.addLayout(self.foot)

    def sizeHint(self) -> QSize:
        return QSize(RAIL_WIDTH, super().sizeHint().height())

    def minimumSizeHint(self) -> QSize:
        return QSize(RAIL_NARROW, super().minimumSizeHint().height())

    def add_entry(self, index: int, text: str) -> QPushButton:
        button = QPushButton()
        button.setObjectName("navEntry")
        button.setCheckable(True)
        button.setCursor(Qt.PointingHandCursor)
        button.setMinimumWidth(0)
        button.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        # The full name whichever one is drawn: for a reader of the narrow
        # rail, and for a screen reader at either width.
        button.setToolTip(text.replace("&&", "&"))
        button.setAccessibleName(text.replace("&&", "&"))
        self._names[index] = text
        self.group.addButton(button, index)
        self._entries.addWidget(button)
        self._name(index)
        return button

    def full_name(self, index: int) -> str:
        return self._names[index]

    def _name(self, index: int) -> None:
        text = self._names[index]
        self.group.button(index).setText(
            SHORT_NAMES.get(text, text) if self._short else text)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        short = self.width() < RAIL_SHORT_BELOW
        if short != self._short:
            self._short = short
            self.brand.setText("NR" if short else "NIGHTREIGN")
            self.sub.setVisible(not short)
            for index in self._names:
                self._name(index)
            self.narrowed.emit(short)

    def show_current(self, index: int) -> None:
        button = self.group.button(index)
        if button is not None:
            button.setChecked(True)


RAIL_STYLE = f"""
#navRail {{
    background: rgba(255, 255, 255, 14);
    border: 1px solid rgba(255, 255, 255, 30);
    border-radius: 16px;
}}
#navRail QLabel#brand {{
    color: {ACCENT_BRIGHT}; font-size: 15px; letter-spacing: 2px;
    padding: 0 6px; font-family: {SERIF};
}}
QPushButton#navEntry {{
    border: 1px solid transparent; border-radius: 10px;
    padding: 8px 9px; text-align: left; color: #c9cadb; font-size: 13px;
    background: transparent;
}}
QPushButton#navEntry:hover {{ background: rgba(255, 255, 255, 16); }}
QPushButton#navEntry:checked {{
    color: {ACCENT_BRIGHT};
    border: 1px solid rgba(217, 181, 106, 70);
    border-left: 3px solid {ACCENT};
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(217, 181, 106, 70), stop:1 rgba(217, 181, 106, 12));
}}
"""
