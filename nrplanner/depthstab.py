"""Red variants -- what a Deep of Night run turns red, in figures a player uses.

Everything drawn here is read from the game's own params (see
`nrdata.extract` for the derivation; none of it appears on screen):

- `deep_of_night.mutations`: the ChaosMatching placement counts, per map and
  depth. They are counts, not weights -- every run on that map and depth
  places exactly that many.
- `subbosses`: the named places whose `categories` carry mutation kind 120,
  i.e. the field bosses the game can turn red.

What the files do **not** hold is left off the tab rather than filled in from
play: how much stronger a red variant is, and what it drops (user decision
2026-11-07: only figures that can be validated, kept short, figures over prose).

The game's internal mutation kinds are collapsed into the handful of things a
player recognises, because the category ids mean nothing in a run:

- the area-scoped kinds together are the red *ordinary enemies* scattered
  through camps and ruins;
- the enemy-roster kinds together are the red *named minibosses*;
- kinds 120 and 160 are place cards rather than characters: 120 is the 29
  one-boss field-boss locations plus the 16 identically staffed arena shells,
  160 the four arena locations that hold more than one boss (T-299 section
  2b, QA-286 -- the word "evergaol" is nowhere in the files). Kind 103 is the
  merchants, and 130/131 are three characters nothing names.
"""

from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QFrame, QGridLayout, QHBoxLayout,
    QHeaderView, QLabel, QScrollArea, QSizePolicy, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

from . import tabheader
from .theme import ACCENT, BORDER, MUTED, PANEL


HEADING = "RED VARIANTS"

#: The two facts that hold on every map, one short bullet each. The first
#: names the limit beside the answer, because the files carry no strength
#: figure at all: `mutations` holds `counts`, `category`, `group` and `varies`,
#: and nothing else (AK-98).
BULLETS = (
    "Same enemy, made stronger: never a different enemy. "
    "The game's files do not say by how much.",
    "The count is fixed, not luck: every run on a map and Depth places "
    "exactly the numbers below.",
)

#: Kept as a name: the table's first column, and the legend for the bars.
NAME_HEADER = "What can be red"

#: Where the one text column sits; the depth columns follow it.
NAME_COLUMN = 0

ZERO_COLOUR = QColor("#4a4a4a")

#: Field-boss mutation kind: the one whose places carry a boss's name.
FIELD_BOSS_KIND = 120

# group value -> map, in the map patterns' own id space. Group 0 rows carry
# no map and count everywhere.
GROUP_MAPS = {
    10: "Default Limveld",
    11: "Mountaintop",
    12: "Crater",
    13: "Rotted Woods",
    15: "Noklateo",
    14: "Great Hollow",
}

# The player-facing grouping, with the colour each sort has in the bars and
# the table. Each row of the tab is one entry here; the two boss rows are
# named after what their rosters actually are -- places, not a cast (AK-325,
# QA-286).
PLAYER_GROUPS: list[tuple[str, list[int], str]] = [
    ("Ordinary enemies in camps & ruins", [100, 105, 140, 141, 150, 151],
     "#9a6fc4"),
    ("Named minibosses", [101, 104, 110, 135, 136, 137, 138], "#c75c5c"),
    ("Mixed-boss arena locations", [160], "#d0903e"),
    ("Field bosses & arena locations", [120], "#5c9ec4"),
    ("Merchants", [103], "#5c9e63"),
    ("Unidentified enemies", [130, 131], "#7a7a7a"),
]

TABLE_STYLE = f"""
QTableWidget {{
    background: {PANEL};
    alternate-background-color: #24262b;
    gridline-color: {BORDER};
    color: #e4e4e4;
    border: 1px solid {BORDER};
    font-size: 12px;
}}
QTableWidget::item:selected {{ background: transparent; color: #e4e4e4; }}
"""


def _section(text: str) -> QLabel:
    label = QLabel(text)
    label.setStyleSheet(
        f"color: {ACCENT}; font-size: 11px; font-weight: bold;"
        " letter-spacing: 1px; margin-top: 8px;")
    return label


def _muted(text: str) -> QLabel:
    label = QLabel(text)
    label.setWordWrap(True)
    label.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
    return label


def _swatch(colour: str) -> QIcon:
    pixmap = QPixmap(10, 10)
    pixmap.fill(QColor(colour))
    return QIcon(pixmap)


class BarChart(QWidget):
    """Horizontal bars, one per row, each a stack of coloured segments.

    Painted rather than built from widgets: the figures are the content and
    the table under it carries every exact number, so the bars only have to
    make the proportions visible at a glance. The total stands at the end of
    each bar, in the accent colour.
    """

    GAP = 6
    LABEL = 120
    TOTAL = 44
    #: Past this the bars only get longer, not easier to compare.
    MAX_WIDTH = 900

    def __init__(self, row: int = 22) -> None:
        super().__init__()
        self.ROW = row
        self.setMaximumWidth(self.MAX_WIDTH)
        # (label, [(value, colour)], highlighted)
        self.rows: list[tuple[str, list[tuple[int, str]], bool]] = []
        self.scale = 1
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def set_rows(self, rows, scale: int) -> None:
        self.rows = rows
        self.scale = max(scale, 1)
        self.setFixedHeight(self._height())
        self.update()

    def _height(self) -> int:
        return max(len(self.rows), 1) * (self.ROW + self.GAP)

    def sizeHint(self) -> QSize:
        return QSize(400, self._height())

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        font = QFont(self.font())
        font.setPixelSize(12)
        painter.setFont(font)
        width = max(self.width() - self.LABEL - self.TOTAL, 10)
        for index, (label, segments, highlighted) in enumerate(self.rows):
            top = index * (self.ROW + self.GAP)
            painter.setPen(QColor("#f0f0f0" if highlighted else "#c8c8c8"))
            painter.drawText(QRectF(0, top, self.LABEL - 8, self.ROW),
                             Qt.AlignVCenter | Qt.AlignRight, label)
            painter.fillRect(QRectF(self.LABEL, top, width, self.ROW),
                             QColor("#26272c"))
            x = float(self.LABEL)
            total = 0
            for value, colour in segments:
                if value <= 0:
                    continue
                span = width * value / self.scale
                fill = QColor(colour)
                if not highlighted and len(segments) == 1:
                    fill.setAlphaF(0.45)
                painter.fillRect(QRectF(x, top, span, self.ROW), fill)
                x += span
                total += value
            painter.setPen(QColor(ACCENT))
            painter.drawText(QRectF(x + 6, top, self.TOTAL + 40, self.ROW),
                             Qt.AlignVCenter | Qt.AlignLeft, str(total))
        painter.end()


class DepthsTab(QWidget):
    def __init__(self, data: dict):
        super().__init__()
        deep = data.get("deep_of_night") or {}
        self.mutations = deep.get("mutations", [])
        self.depths = deep.get("depth_count", 5)
        self.subbosses = data.get("subbosses") or {}

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        outer.addWidget(self.scroll)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)
        self.scroll.setWidget(content)

        layout.addWidget(tabheader.heading(HEADING))
        for bullet in BULLETS:
            layout.addWidget(tabheader.question("•  " + bullet))

        controls = QHBoxLayout()
        controls.setSpacing(10)
        controls.addWidget(QLabel("Map:"))
        self.map_box = QComboBox()
        for group, name in GROUP_MAPS.items():
            self.map_box.addItem(name, group)
        self.map_box.currentIndexChanged.connect(self.refresh)
        controls.addWidget(self.map_box)
        controls.addStretch(1)
        layout.addLayout(controls)

        # -- red variants per depth: bars, then the exact figures ---------
        layout.addWidget(_section("RED VARIANTS ON THE MAP, PER DEPTH"))
        self.depth_groups = self._depth_groups()
        self.depth_bars = BarChart()
        layout.addWidget(self.depth_bars)

        headers = [NAME_HEADER] + [
            self._depth_header(group) for group in self.depth_groups
        ]
        self.table = QTableWidget(0, len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.setMaximumWidth(BarChart.MAX_WIDTH)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(NAME_COLUMN, QHeaderView.Stretch)
        for column in range(NAME_COLUMN + 1, len(headers)):
            header.setSectionResizeMode(column, QHeaderView.Fixed)
            self.table.setColumnWidth(column, 90)
        layout.addWidget(self.table)

        # -- what each step down adds ------------------------------------
        layout.addWidget(_section("WHAT GOING DEEPER ADDS"))
        self.changes = QLabel()
        self.changes.setWordWrap(True)
        self.changes.setTextFormat(Qt.RichText)
        self.changes.setStyleSheet("color: #d8d8d8; font-size: 12px;")
        layout.addWidget(self.changes)

        # -- every map side by side --------------------------------------
        self.maps_heading = _section("")
        layout.addWidget(self.maps_heading)
        self.map_bars = BarChart(row=16)
        layout.addWidget(self.map_bars)

        # -- the field bosses the game can turn red ----------------------
        names = self._field_boss_names()
        if names:
            layout.addWidget(_section(
                f"FIELD BOSSES THAT CAN BE RED ({len(names)})"))
            layout.addWidget(_muted(
                "From Depth 2 on. The arena locations in the same table row "
                "carry no name in the files."))
            names_box = QWidget()
            names_box.setMaximumWidth(BarChart.MAX_WIDTH)
            grid = QGridLayout(names_box)
            grid.setContentsMargins(0, 0, 0, 0)
            grid.setHorizontalSpacing(18)
            grid.setVerticalSpacing(2)
            columns = 4
            per_column = -(-len(names) // columns)
            for index, name in enumerate(names):
                cell = QLabel("•  " + name)
                cell.setTextFormat(Qt.PlainText)
                cell.setStyleSheet("color: #d8d8d8; font-size: 12px;")
                grid.addWidget(cell, index % per_column, index // per_column)
            layout.addWidget(names_box)

        layout.addStretch(1)
        self.refresh()

    # ------------------------------------------------------------------

    def _counts_for(self, pool: list[dict],
                    categories: list[int]) -> list[int]:
        """How many red variants of these kinds a run places, per depth."""
        return [sum(m["counts"][i] for m in pool
                    if m["category"] in categories)
                for i in range(self.depths)]

    def _pool_of(self, group: int) -> list[dict]:
        return [m for m in self.mutations if m["group"] in (group, 0)]

    def _depth_groups(self) -> list[list[int]]:
        """Consecutive depths whose figures are equal on every map and row.

        Depth 2 equals Depth 3 and Depth 4 equals Depth 5 for all six maps and
        all 22 data rows, so five columns repeated themselves. Merging is
        worked out from the data rather than written down, so a patch that
        ever moves one of them apart drops this straight back to one column
        per depth instead of hiding the difference (AK-100).

        With nothing in the dataset there is nothing to merge on.
        """
        seen: list[list[int]] = []
        for group in GROUP_MAPS:
            pool = self._pool_of(group)
            for _label, categories, _colour in PLAYER_GROUPS:
                seen.append(self._counts_for(pool, categories))
        if not any(any(counts) for counts in seen):
            return [[depth] for depth in range(self.depths)]

        groups: list[list[int]] = []
        for depth in range(self.depths):
            column = [counts[depth] for counts in seen]
            previous = ([counts[groups[-1][-1]] for counts in seen]
                        if groups else None)
            if previous is not None and column == previous:
                groups[-1].append(depth)
            else:
                groups.append([depth])
        return groups

    @staticmethod
    def _depth_header(group: list[int]) -> str:
        if len(group) == 1:
            return f"Depth {group[0] + 1}"
        return f"Depth {group[0] + 1}–{group[-1] + 1}"

    def _field_boss_names(self) -> list[str]:
        """Each name once: several spots hold the same boss."""
        names = {
            (entry.get("name") or "").strip()
            for entry in self.subbosses.values()
            if FIELD_BOSS_KIND in (entry.get("categories") or [])
        }
        return sorted(name for name in names if name)

    def _rows_for(self, group: int) -> list[tuple[str, list[int], str]]:
        pool = self._pool_of(group)
        rows = []
        for label, categories, colour in PLAYER_GROUPS:
            counts = self._counts_for(pool, categories)
            if any(counts):
                rows.append((label, counts, colour))
        return rows

    def _total(self, group: int, depth: int) -> int:
        return sum(counts[depth] for _l, counts, _c in self._rows_for(group))

    def refresh(self) -> None:
        group = self.map_box.currentData()
        rows = self._rows_for(group)
        totals = [sum(r[1][i] for r in rows) for i in range(self.depths)]
        self._fill_table(rows, totals)

        # One scale over every map and depth, so switching the map moves the
        # bars and the eye sees which map runs hotter.
        peak = max((self._total(g, d) for g in GROUP_MAPS
                    for d in range(self.depths)), default=1)
        self.depth_bars.set_rows([
            (self._depth_header(depths),
             [(counts[depths[0]], colour) for _l, counts, colour in rows],
             True)
            for depths in self.depth_groups
        ], peak)

        self.changes.setText(self._changes_text(rows))

        deepest = self.depth_groups[-1] if self.depth_groups else [0]
        self.maps_heading.setText(
            f"EVERY MAP AT {self._depth_header(deepest).upper()}")
        self.map_bars.set_rows([
            (name, [(self._total(g, deepest[0]),
                     ACCENT if g == group else "#9a6fc4")], g == group)
            for g, name in GROUP_MAPS.items()
        ], peak)

    def _changes_text(self, rows) -> str:
        lines = []
        for before, after in zip(self.depth_groups, self.depth_groups[1:]):
            gains = [(counts[after[0]] - counts[before[0]], label)
                     for label, counts, _c in rows
                     if counts[after[0]] != counts[before[0]]]
            if not gains:
                continue
            total = sum(delta for delta, _l in gains)
            parts = ", ".join(f"{delta:+d} {label.lower()}"
                              for delta, label in gains)
            lines.append(
                f"•  <b>{self._depth_header(after)}:</b> "
                f"<span style='color:{ACCENT}'>{total:+d}</span>  ({parts})")
        if not lines:
            return "•  Nothing changes with Depth on this map."
        return "<br>".join(lines)

    def _fill_table(self, rows, totals) -> None:
        shown = rows + [("Total red variants on the map", totals, None)]
        self.table.setRowCount(len(shown))
        for r, (label, counts, colour) in enumerate(shown):
            is_total = colour is None
            name = QTableWidgetItem(label)
            if is_total:
                name.setForeground(QColor(ACCENT))
            else:
                name.setIcon(_swatch(colour))
            self.table.setItem(r, NAME_COLUMN, name)

            # A column may stand for more than one depth; every member of a
            # group carries the same figure by the way the groups were built.
            for i, depths in enumerate(self.depth_groups):
                count = counts[depths[0]]
                item = QTableWidgetItem()
                item.setData(Qt.DisplayRole, str(count) if count else "—")
                item.setTextAlignment(Qt.AlignCenter)
                if not count:
                    item.setForeground(ZERO_COLOUR)
                elif is_total:
                    item.setForeground(QColor(ACCENT))
                self.table.setItem(r, NAME_COLUMN + 1 + i, item)

        # Show every row: the table is short, and the tab scrolls as a whole.
        self.table.resizeRowsToContents()
        height = self.table.horizontalHeader().height() + 2
        height += sum(self.table.rowHeight(r) for r in range(len(shown)))
        self.table.setFixedHeight(height)
