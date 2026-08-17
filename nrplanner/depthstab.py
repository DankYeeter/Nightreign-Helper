"""Red variants by depth -- the Deep of Night mutation numbers, for a player.

The data is the ChaosMatching mutation tables (see `nrdata.extract` for the
derivation; none of that appears on screen). This tab deliberately collapses
the game's internal mutation categories into the handful of things a player
actually recognises, because the category ids mean nothing in a run:

- the area-scoped kinds together are the red *ordinary enemies* scattered
  through camps and ruins;
- the enemy-roster kinds together are the red *named field enemies and
  minibosses* (Golden Hippopotamus, Grave Warden Duelist, ...);
- kind 160 is the evergaol bosses, kind 120 the night-boss cast (no red
  night boss has been sighted, so it is marked unconfirmed), kind 103 the
  merchants, and 130/131 are three characters nothing names.

The counts are the game's own placement counts per map -- how many red
variants a run puts on the board -- and nothing like them is published
anywhere else. The per-kind rosters, tiles and ids stay in the snapshot for
anyone who wants them; the screen shows only what a player can use.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QHeaderView, QLabel, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

ACCENT = "#c8a45c"
MUTED = "#8a8a8a"
COMMUNITY = "#7fb2e5"

ZERO_COLOUR = QColor("#4a4a4a")
BAR_COLOUR = QColor("#9a6fc4")

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

# The player-facing grouping. Each row of the tab is one entry here; the
# category ids are the game's internal kinds, collapsed by what their
# rosters contain. Examples are filled from the extracted rosters at
# runtime so a game patch cannot leave stale names here.
PLAYER_GROUPS: list[tuple[str, list[int]]] = [
    ("Ordinary enemies in camps & ruins", [100, 105, 140, 141, 150, 151]),
    ("Named field enemies & minibosses", [101, 104, 110, 135, 136, 137, 138]),
    ("Evergaol bosses", [160]),
    ("Night bosses (unconfirmed)", [120]),
    ("Merchants", [103]),
    ("Unidentified enemies", [130, 131]),
]


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
        self.kinds = deep.get("kinds", {})
        self.depths = deep.get("depth_count", 5)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        layout.addWidget(_heading("RED VARIANTS BY DEPTH"))

        intro = QLabel(
            "Red variants are individual empowered enemies -- the same "
            "enemy, stronger, never a different one -- and they appear "
            "scattered through the map, several per camp. Deeper runs do "
            "not just make them stronger: more are placed, and the boss "
            "tiers only join from Depth 2 on. The figures are how many red "
            "variants of each sort a run puts on the selected map."
        )
        intro.setWordWrap(True)
        intro.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        layout.addWidget(intro)

        reported = QLabel(
            "COMMUNITY-REPORTED: red enemies always drop a weapon, and red "
            "mini-bosses are guaranteed a unique-tier armament. The "
            "Everdark Sovereign form of the Nightlord is also only possible "
            "from Depth 2, and from Depth 3 the map may hide points of "
            "interest or the Nightlord itself."
        )
        reported.setWordWrap(True)
        reported.setStyleSheet(f"color: {COMMUNITY}; font-size: 11px;")
        layout.addWidget(reported)

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

        self.summary = QLabel()
        self.summary.setWordWrap(True)
        self.summary.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        layout.addWidget(self.summary)

        headers = ["What can be red", "For example"] + [
            f"Depth {i + 1}" for i in range(self.depths)
        ]
        self.table = QTableWidget(0, len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet(
            "QTableWidget::item:selected { background: rgba(200, 164, 92, 60);"
            " color: #f0f0f0; }"
        )
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        for column in range(2, len(headers)):
            header.setSectionResizeMode(column, QHeaderView.ResizeToContents)
        layout.addWidget(self.table, 1)

        self.refresh()

    # ------------------------------------------------------------------

    def _pool(self) -> list[dict]:
        group = self.map_box.currentData()
        return [m for m in self.mutations if m["group"] in (group, 0)]

    def _examples(self, categories: list[int]) -> str:
        """Up to three named members across the group's rosters."""
        names: list[str] = []
        for category in categories:
            kind = self.kinds.get(str(category)) or {}
            for entry in kind.get("chrs", []):
                if entry.get("name") and entry["name"] not in names:
                    names.append(entry["name"])
        return ", ".join(names[:3]) + (" …" if len(names) > 3 else "")

    def refresh(self) -> None:
        pool = self._pool()

        rows: list[tuple[str, str, list[int]]] = []
        for label, categories in PLAYER_GROUPS:
            counts = [sum(m["counts"][i] for m in pool
                          if m["category"] in categories)
                      for i in range(self.depths)]
            if any(counts):
                rows.append((label, self._examples(categories), counts))
        totals = [sum(r[2][i] for r in rows) for i in range(self.depths)]
        rows.append(("Total red variants on the map", "", totals))

        self.table.setRowCount(len(rows))
        peak = max(totals) or 1
        for r, (label, examples, counts) in enumerate(rows):
            is_total = r == len(rows) - 1

            name = QTableWidgetItem(label)
            if is_total:
                name.setForeground(QColor(ACCENT))
            self.table.setItem(r, 0, name)

            example = QTableWidgetItem(examples)
            example.setForeground(QColor("#b8b8b8"))
            self.table.setItem(r, 1, example)

            for i, count in enumerate(counts):
                item = QTableWidgetItem()
                item.setData(Qt.DisplayRole, str(count) if count else "—")
                item.setTextAlignment(Qt.AlignCenter)
                if not count:
                    item.setForeground(ZERO_COLOUR)
                elif not is_total:
                    shade = QColor(BAR_COLOUR)
                    shade.setAlphaF(0.10 + 0.45 * (count / peak))
                    item.setBackground(shade)
                else:
                    item.setForeground(QColor(ACCENT))
                self.table.setItem(r, 2 + i, item)

        joined = [label for label, _ex, counts in rows[:-1] if not counts[0]]
        pieces = [
            f"{totals[0]} red variants at Depth 1, "
            f"{totals[-1]} at Depth {self.depths}",
        ]
        if joined:
            pieces.append("joining from Depth 2: " + ", ".join(
                label.split(" (")[0] for label in joined))
        self.summary.setText("  ·  ".join(pieces))
