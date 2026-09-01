"""Weapon list ranked by attack rating for the build on the planner tab."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QPushButton,
    QSpinBox, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from . import weapons

COLUMNS = ["Weapon", "AR", "Physical", "Magic", "Fire", "Lightning", "Holy",
           "Requirements", "Weight"]


def requirement_text(weapon: dict, unmet: dict) -> str:
    parts = []
    for stat, needed in weapon["requires"].items():
        if not needed:
            continue
        short = stat[:3].upper()
        parts.append(f"{short} {needed}" + ("!" if stat in unmet else ""))
    return "  ".join(parts) or "—"


class WeaponsTab(QWidget):
    def __init__(self, data: dict, planner):
        super().__init__()
        self.data = data
        self.planner = planner
        self.ratings: list[weapons.WeaponRating] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)

        controls = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search weapons…")
        self.search.textChanged.connect(self.refresh)
        controls.addWidget(self.search, 1)

        controls.addWidget(QLabel("Upgrade +"))
        self.upgrade = QSpinBox()
        self.upgrade.setRange(0, 25)
        self.upgrade.valueChanged.connect(self.recalculate)
        controls.addWidget(self.upgrade)

        self.usable_only = QCheckBox("Meets requirements")
        self.usable_only.setChecked(True)
        self.usable_only.toggled.connect(self.recalculate)
        controls.addWidget(self.usable_only)

        self.refresh_button = QPushButton("Recalculate for current build")
        self.refresh_button.clicked.connect(self.recalculate)
        controls.addWidget(self.refresh_button)
        layout.addLayout(controls)

        self.summary = QLabel()
        self.summary.setStyleSheet("color: #8a8a8a; font-size: 11px;")
        self.summary.setWordWrap(True)
        layout.addWidget(self.summary)

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.table, 1)

        self.recalculate()

    def recalculate(self) -> None:
        hero = self.planner.current_hero()
        level = self.planner.level_slider.value()
        # The build the planner tab is showing, taken rather than worked
        # out again: a second argument list drifts from the first at the next
        # parameter, which is exactly what QA-001 caught it doing.
        build = self.planner.current_build()
        self.attributes = build.attributes
        self.ratings = weapons.rank(
            self.data, build.attributes,
            upgrade=self.upgrade.value(),
            require_usable=self.usable_only.isChecked(),
        )
        stats = "  ".join(f"{k[:3].upper()} {v}"
                          for k, v in build.attributes.items())
        self.summary.setText(
            f"{hero['name']} at level {level}, +{self.upgrade.value()} — {stats}. "
            f"{len(self.ratings)} weapons. Attack rating is base damage plus "
            f"stat scaling; it excludes attack motion values and enemy defences."
        )
        self.refresh()

    def refresh(self) -> None:
        needle = self.search.text().strip().lower()
        rows = [r for r in self.ratings
                if not needle or needle in r.weapon["name"].lower()]

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(rows))
        for i, rating in enumerate(rows):
            weapon = rating.weapon
            per_type = {
                d: rating.base.get(d, 0) + rating.scaled.get(d, 0)
                for d in weapons.DAMAGE_TYPES
            }
            values = [
                weapon["name"],
                rating.total,
                per_type["Physics"],
                per_type["Magic"],
                per_type["Fire"],
                per_type["Thunder"],
                per_type["Dark"],
                requirement_text(weapon, rating.unmet),
                weapon.get("weight") or 0.0,
            ]
            for c, value in enumerate(values):
                item = QTableWidgetItem()
                if isinstance(value, str):
                    item.setText(value)
                elif c == 8:
                    item.setData(Qt.DisplayRole, float(value))
                    item.setText(f"{value:.1f}")
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                else:
                    item.setData(Qt.DisplayRole, float(value))
                    item.setText(f"{value:.0f}" if value else "—")
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if c == 7 and rating.unmet:
                    item.setForeground(Qt.red)
                self.table.setItem(i, c, item)

        self.table.setSortingEnabled(True)
        self.table.sortItems(1, Qt.DescendingOrder)
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
