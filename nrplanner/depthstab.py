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

from . import tabheader

ACCENT = "#c8a45c"
MUTED = "#8a8a8a"
COMMUNITY = "#7fb2e5"

#: AK-98. The old heading, `RED VARIANTS BY DEPTH`, announced counts, and the
#: answer to "what *is* a red variant" sat in a subordinate clause halfway
#: down the intro paragraph -- where a player looking for it did not find it.
#: The limit is named in the same breath as the answer, because the files
#: carry no strength figures at all: `mutations` holds `counts`, `category`,
#: `group` and `varies`, and nothing else.
HEADING = "RED VARIANTS: WHAT THEY ARE, AND HOW MANY"
QUESTION = (
    "A red variant is the same enemy made stronger — never a different "
    "enemy. The game's files do not say by how much. What they do say is how "
    "many of each sort a run places on a map, and that is the table below.")

#: AK-99. The rosters carry no map dimension at all, so the same names come
#: back for every map the box above can be set to. Saying `(any map)` in the
#: heading costs two words and stops the column claiming a link the data has
#: not got.
NAME_HEADER = "What can be red"
EXAMPLES_HEADER = "Examples (any map)"
EXAMPLES_TIP = (
    "Named members of this group anywhere in the game. The files do not list "
    "them per map, so these names are not tied to the map selected above.")
NO_NAMES = "— the files name none"

#: Where the two text columns sit. Named so the width rule below reads as a
#: rule about them rather than about two numbers.
NAME_COLUMN = 0
EXAMPLES_COLUMN = 1

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


class VariantTable(QTableWidget):
    """A table whose examples never outgrow the column they illustrate.

    AK-99 ends with "and the column is **never** wider than `What can be
    red`", and that sentence was left to `QHeaderView.ResizeToContents`, which
    hands a column its natural width whatever is left over for the rest. From
    1 067 px up the natural widths happened to fall the right way round and
    the rule looked kept; at an 833 px window they did not, and the examples
    took **349** px against **281** for the column saying what the row is
    (QA-144, measured on Windows at 150 % scale under Fusion).

    The rule here is a share, not a cap in pixels: the examples take at most
    half of what the two text columns have between them. The name column is
    the stretch column and takes the remainder, so half is exactly the largest
    share that leaves it the wider of the two at every width.
    """

    def __init__(self, columns: int):
        super().__init__(0, columns)
        self._natural_examples = 0

    def measure_columns(self) -> None:
        """Note what the examples would like, then share the width out.

        Asked once per refresh: the widest cell does not change with the
        window, and asking twenty-two rows how wide they are is the expensive
        part.
        """
        header = self.horizontalHeader()
        self._natural_examples = max(
            self.sizeHintForColumn(EXAMPLES_COLUMN),
            header.sectionSizeHint(EXAMPLES_COLUMN))
        self.fit_columns()

    def fit_columns(self) -> None:
        available = self.viewport().width()
        if available <= 0 or not self._natural_examples:
            return
        header = self.horizontalHeader()
        depths = sum(header.sectionSize(column)
                     for column in range(EXAMPLES_COLUMN + 1,
                                         self.columnCount()))
        share = max(available - depths, 0) // 2
        header.resizeSection(EXAMPLES_COLUMN,
                             min(self._natural_examples, share))

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt naming
        super().resizeEvent(event)
        self.fit_columns()


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

        layout.addWidget(tabheader.heading(HEADING))
        layout.addWidget(tabheader.question(QUESTION))

        # What is left of the old intro once its opening clause has moved up
        # into QUESTION, where it answers the tab's own title (AK-98). The
        # last sentence stays: it is the plainest statement of a reference
        # quantity anywhere in the program, and the one the other five tabs
        # were measured against.
        intro = QLabel(
            "They appear scattered through the map, several per camp. Deeper "
            "runs do not just make them stronger: more are placed, and the "
            "boss tiers only join from Depth 2 on. The figures are how many "
            "red variants of each sort a run puts on the selected map."
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

        self.depth_groups = self._depth_groups()
        headers = [NAME_HEADER, EXAMPLES_HEADER] + [
            self._depth_header(group) for group in self.depth_groups
        ]
        self.table = VariantTable(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        item = self.table.horizontalHeaderItem(EXAMPLES_COLUMN)
        if item is not None:
            item.setToolTip(EXAMPLES_TIP)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet(
            "QTableWidget::item:selected { background: rgba(200, 164, 92, 60);"
            " color: #f0f0f0; }"
        )
        header = self.table.horizontalHeader()
        # The leftover width goes to the column that says what the row is,
        # not to the one carrying up to three names (AK-99). The other way
        # round made the examples the widest column of the table while the
        # names themselves were the same on every map.
        header.setSectionResizeMode(NAME_COLUMN, QHeaderView.Stretch)
        # Interactive, because `ResizeToContents` kept the examples at their
        # natural width however little was left for the name column, which is
        # how AK-99's last sentence came apart at 833 px (QA-144). The table
        # sizes this one itself; see `VariantTable.fit_columns`.
        header.setSectionResizeMode(EXAMPLES_COLUMN, QHeaderView.Interactive)
        for column in range(EXAMPLES_COLUMN + 1, len(headers)):
            header.setSectionResizeMode(column, QHeaderView.ResizeToContents)
        layout.addWidget(self.table, 1)

        self.refresh()

    # ------------------------------------------------------------------

    def _counts_for(self, pool: list[dict],
                    categories: list[int]) -> list[int]:
        """How many red variants of these kinds a run places, per depth."""
        return [sum(m["counts"][i] for m in pool
                    if m["category"] in categories)
                for i in range(self.depths)]

    def _depth_groups(self) -> list[list[int]]:
        """Consecutive depths whose figures are equal on every map and row.

        Depth 2 equals Depth 3 and Depth 4 equals Depth 5 for all six maps and
        all 22 data rows, so five columns repeated themselves three times over
        and the table said with five columns what it had to say with three.
        Merging is worked out from the data rather than written down, so a
        patch that ever moves one of them apart drops this straight back to
        one column per depth instead of hiding the difference (AK-100).

        With nothing in the dataset there is nothing to merge on: every column
        would then be trivially equal to its neighbour, and one column headed
        `Depth 1–5` would be an assertion about data that is not there.
        """
        seen: list[list[int]] = []
        for group in GROUP_MAPS:
            pool = [m for m in self.mutations if m["group"] in (group, 0)]
            for _label, categories in PLAYER_GROUPS:
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

    def _pool(self) -> list[dict]:
        group = self.map_box.currentData()
        return [m for m in self.mutations if m["group"] in (group, 0)]

    def _examples(self, categories: list[int]) -> str:
        """Up to three named members across the group's rosters.

        `NO_NAMES` rather than an empty cell where the rosters name nobody:
        two of the six rows are in that state, one of them the largest row of
        the table, and a blank cell reads as a gap in the program rather than
        as an answer (A7, AK-99).
        """
        names: list[str] = []
        for category in categories:
            kind = self.kinds.get(str(category)) or {}
            for entry in kind.get("chrs", []):
                if entry.get("name") and entry["name"] not in names:
                    names.append(entry["name"])
        if not names:
            return NO_NAMES
        return ", ".join(names[:3]) + (" …" if len(names) > 3 else "")

    def refresh(self) -> None:
        pool = self._pool()

        rows: list[tuple[str, str, list[int]]] = []
        for label, categories in PLAYER_GROUPS:
            counts = self._counts_for(pool, categories)
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
            self.table.setItem(r, NAME_COLUMN, name)

            example = QTableWidgetItem(examples)
            example.setForeground(QColor("#b8b8b8"))
            self.table.setItem(r, EXAMPLES_COLUMN, example)

            # One cell per column, and a column may stand for more than one
            # depth. Every member of a group carries the same figure by the
            # way the groups were built, so the first of them is the group's.
            for i, group in enumerate(self.depth_groups):
                count = counts[group[0]]
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
                self.table.setItem(r, EXAMPLES_COLUMN + 1 + i, item)

        self.table.measure_columns()

        joined = [label for label, _ex, counts in rows[:-1] if not counts[0]]
        pieces = [
            f"{totals[0]} red variants at Depth 1, "
            f"{totals[-1]} at Depth {self.depths}",
        ]
        if joined:
            pieces.append("joining from Depth 2: " + ", ".join(
                label.split(" (")[0] for label in joined))
        self.summary.setText("  ·  ".join(pieces))
