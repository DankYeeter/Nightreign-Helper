"""How mutation weighting shifts across the five depths.

HANDOVER section 7.3 expected this to live in
ChaosMatchingMutationEnemyTableParam. It does not: that table's 3067 rows
carry no weight column and no per-depth structure. The weighting is in
ChaosMatchingMutationCategoryParam, whose every 20-byte row begins with five
u16 -- one per depth -- and 20 of whose 46 rows genuinely differ across them.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox, QHBoxLayout, QHeaderView, QLabel, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

ACCENT = "#c8a45c"
MUTED = "#8a8a8a"

# A weight of 0 at depth 1 that turns on later is the most interesting thing
# in the table, so it gets its own colour rather than reading as "no data".
ZERO_COLOUR = QColor("#4a4a4a")
BAR_COLOUR = QColor("#9a6fc4")


def _heading(text: str) -> QLabel:
    label = QLabel(text)
    label.setStyleSheet(
        f"color: {ACCENT}; font-size: 12px; font-weight: bold;"
        " letter-spacing: 1px;"
    )
    return label


class DepthsTab(QWidget):
    def __init__(self, data: dict):
        super().__init__()
        deep = data.get("deep_of_night") or {}
        self.mutations = deep.get("mutations", [])
        self.depths = deep.get("depth_count", 5)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        layout.addWidget(_heading("MUTATION WEIGHTING BY DEPTH"))

        intro = QLabel(
            "Each row is one mutation category and each column one depth. The "
            "figures are the game's own draw weights, shown raw: what pool "
            "they are drawn against is not stated anywhere in the files, and "
            "the categories themselves are unnamed, so only their ids appear."
        )
        intro.setWordWrap(True)
        intro.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        layout.addWidget(intro)

        controls = QHBoxLayout()
        controls.setSpacing(10)
        self.varying_only = QCheckBox("Only categories that change with depth")
        self.varying_only.toggled.connect(self.refresh)
        controls.addWidget(self.varying_only)

        self.share_within = QCheckBox(
            "Show share within category (assumes the category is the pool)")
        self.share_within.toggled.connect(self.refresh)
        controls.addWidget(self.share_within)
        controls.addStretch(1)
        layout.addLayout(controls)

        self.summary = QLabel()
        self.summary.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        layout.addWidget(self.summary)

        headers = ["Category", "Pool", "Member"] + [
            f"Depth {i + 1}" for i in range(self.depths)
        ]
        self.table = QTableWidget(0, len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSortingEnabled(True)
        self.table.sortByColumn(0, Qt.AscendingOrder)
        # Every cell is shaded to show the weight, and Qt's default selection
        # paints over that in a colour that reads as an error. The table is
        # read-only reference data, so a quiet highlight is enough.
        self.table.setStyleSheet(
            "QTableWidget::item:selected { background: rgba(200, 164, 92, 60);"
            " color: #f0f0f0; }"
        )
        header = self.table.horizontalHeader()
        for column in range(3):
            header.setSectionResizeMode(column, QHeaderView.ResizeToContents)
        for column in range(3, len(headers)):
            header.setSectionResizeMode(column, QHeaderView.Stretch)
        layout.addWidget(self.table, 1)

        self.refresh()

    def refresh(self) -> None:
        rows = [
            m for m in self.mutations
            if not self.varying_only.isChecked() or m.get("varies")
        ]

        # Totals per pool per depth, used only when the user opts into the
        # share view -- normalising by pool is an assumption, not a fact.
        totals: dict[int, list[int]] = {}
        for m in self.mutations:
            bucket = totals.setdefault(m["category"], [0] * self.depths)
            for i, weight in enumerate(m["weights"][: self.depths]):
                bucket[i] += weight

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(rows))
        peak = max((max(m["weights"]) for m in rows), default=1) or 1

        for r, mutation in enumerate(rows):
            for c, value in enumerate(
                (mutation["id"], mutation["category"], mutation["group"])
            ):
                item = QTableWidgetItem()
                item.setData(Qt.DisplayRole, value)
                self.table.setItem(r, c, item)

            weights = mutation["weights"][: self.depths]
            for i, weight in enumerate(weights):
                if self.share_within.isChecked():
                    total = totals[mutation["category"]][i]
                    text = f"{weight / total * 100:.1f}%" if total else "-"
                else:
                    text = str(weight)
                item = QTableWidgetItem()
                item.setData(Qt.DisplayRole, text)
                item.setTextAlignment(Qt.AlignCenter)
                if weight == 0:
                    item.setForeground(ZERO_COLOUR)
                else:
                    # A faint bar behind the number, so the shape across the
                    # row is visible without reading every figure.
                    shade = QColor(BAR_COLOUR)
                    shade.setAlphaF(0.10 + 0.45 * (weight / peak))
                    item.setBackground(shade)
                self.table.setItem(r, 3 + i, item)

        self.table.setSortingEnabled(True)

        varying = sum(1 for m in self.mutations if m.get("varies"))
        self.summary.setText(
            f"{len(rows)} of {len(self.mutations)} categories  ·  "
            f"{varying} change with depth  ·  "
            f"{len(self.mutations) - varying} are flat"
        )
