"""The five depths: how much tougher enemies get, and what it pays.

Every number here is read from the game's own params, but none of those params
ship a paramdef, so the layouts were inferred. What makes the inference solid
is stated on the tab itself rather than buried: 89 of 90 correction rows read
as five SpEffect ids that all resolve, and the values they carry are monotonic
across the five depths.
"""

from __future__ import annotations

import statistics

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QHeaderView, QLabel, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

ACCENT = "#c8a45c"
MUTED = "#8a8a8a"
PANEL = "#1e1f23"
BORDER = "#2e2f35"
DEEP = "#9a6fc4"

# The five elemental attack rates move together in every profile, so showing
# five identical columns would be noise. They are collapsed when equal and
# split apart automatically if a profile ever disagrees.
ATTACK_FIELDS = [
    "physicsAttackPowerRate", "magicAttackPowerRate", "fireAttackPowerRate",
    "thunderAttackPowerRate", "darkAttackPowerRate",
]


# Rating changes per expedition. These are NOT in regulation.bin: no param
# carries them, no field name anywhere mentions rank or rating, and the text
# tables state only the band thresholds. They come from play instead, and the
# tab says so rather than passing them off as extracted.
#
# Confirmed in game by this project's owner: +200 for a win, +100 for an
# unknown Nightlord. The map bonus and the loss table are community-reported
# and mutually consistent -- a reported +300 for a Depth 3 win on an invisible
# map is exactly 200 + 100, which corroborates both the win value and the map
# bonus from an independent direction.
RATING_BONUSES = [
    ("Win (defeat the Nightlord)", 200, "confirmed in game"),
    ("Unknown Nightlord", 100, "confirmed in game"),
    ("Obstructed map", 100, "community-reported"),
]

# Depth -> (lost to the Nightlord, lost on day 2, lost on day 1).
# Depth 1 never costs rating, confirmed in game.
RATING_LOSSES = {
    1: (0, 0, 0),
    2: (0, -100, -200),
    3: (-200, -300, -400),
    4: (-400, -500, -600),
    5: (-600, -700, -800),
}


def _heading(text: str) -> QLabel:
    label = QLabel(text)
    label.setStyleSheet(
        f"color: {ACCENT}; font-size: 12px; font-weight: bold;"
        " letter-spacing: 1px;"
    )
    return label


def _note(text: str) -> QLabel:
    label = QLabel(text)
    label.setWordWrap(True)
    label.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
    return label


class DeepTab(QWidget):
    def __init__(self, data: dict):
        super().__init__()
        self.deep = data.get("deep_of_night") or {}
        self.scaling = self.deep.get("scaling", [])
        self.labels = self.deep.get("field_labels", {})
        depths = self.deep.get("depth_count", 5)
        self.depth_names = [f"Depth {i + 1}" for i in range(depths)]

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        layout.addWidget(self._build_rewards())
        layout.addWidget(self._build_rating())
        layout.addWidget(self._build_scaling())
        layout.addWidget(self._build_unidentified())
        layout.addStretch(1)


    # -- rewards ---------------------------------------------------------
    def _build_rewards(self) -> QWidget:
        panel = QWidget()
        box = QVBoxLayout(panel)
        box.setContentsMargins(0, 0, 0, 0)
        box.setSpacing(5)
        box.addWidget(_heading("REWARDS BY DEPTH"))

        rewards = self.deep.get("rewards", [])
        table = QTableWidget(2, len(self.depth_names))
        table.setHorizontalHeaderLabels(self.depth_names)
        # The second row is deliberately not called "Points". Nothing in the
        # files names it, and it is far too small to be the depth rating.
        sigil = self.deep.get("sigil_name") or "Sovereign Sigils"
        table.setVerticalHeaderLabels(["Reward multiplier", sigil])
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setFixedWidth(150)

        for column, reward in enumerate(rewards[: len(self.depth_names)]):
            if reward is None:
                continue
            multiplier = QTableWidgetItem(f"x{reward['multiplier']:g}")
            sigils = QTableWidgetItem(str(reward["sigils"]))
            table.setItem(0, column, multiplier)
            table.setItem(1, column, sigils)
        # Sized to its two rows. A fixed height left a blank strip under the
        # last row that read like a third, empty category.
        table.setFixedHeight(table.horizontalHeader().height()
                             + table.rowHeight(0) + table.rowHeight(1)
                             + 2 * table.frameWidth() + 2)
        box.addWidget(table)
        rating = self.deep.get("rating_text")
        if rating:
            box.addSpacing(6)
            box.addWidget(_heading("WHAT DEPTH MEANS"))
            # The game's own tutorial, verbatim -- this is where the rating
            # bands behind each Depth are actually stated.
            body = QLabel(self._depth_bands(rating))
            body.setWordWrap(True)
            body.setStyleSheet("color: #d8d8d8; font-size: 11px;")
            box.addWidget(body)
        return panel

    @staticmethod
    def _depth_bands(rating: str) -> str:
        """Just the rating bands, without the tutorial's framing prose.

        The game's text opens by restating what a rating is and closes on
        matchmaking, neither of which is a number a player needs here.
        """
        blocks = [b.strip() for b in rating.splitlines() if b.strip()]
        return "\n".join(b for b in blocks
                         if "Rating" in b or "Depths in total" in b)


    # -- rating per expedition --------------------------------------------
    def _build_rating(self) -> QWidget:
        panel = QWidget()
        box = QVBoxLayout(panel)
        box.setContentsMargins(0, 0, 0, 0)
        box.setSpacing(5)
        box.addWidget(_heading("RATING PER EXPEDITION"))

        gains = QTableWidget(len(RATING_BONUSES), 1)
        gains.setHorizontalHeaderLabels(["Rating"])
        gains.setVerticalHeaderLabels([n for n, _v, _s in RATING_BONUSES])
        gains.setEditTriggers(QTableWidget.NoEditTriggers)
        gains.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        gains.verticalHeader().setFixedWidth(180)
        for row, (_name, value, source) in enumerate(RATING_BONUSES):
            item = QTableWidgetItem(f"+{value}    ({source})")
            gains.setItem(row, 0, item)
        gains.setFixedHeight(gains.horizontalHeader().height()
                             + sum(gains.rowHeight(r)
                                   for r in range(len(RATING_BONUSES)))
                             + 2 * gains.frameWidth() + 2)
        box.addWidget(gains)

        labels = ["Lost to the Nightlord", "Lost on day 2", "Lost on day 1"]
        losses = QTableWidget(len(labels), len(self.depth_names))
        losses.setHorizontalHeaderLabels(self.depth_names)
        losses.setVerticalHeaderLabels(labels)
        losses.setEditTriggers(QTableWidget.NoEditTriggers)
        losses.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        losses.verticalHeader().setFixedWidth(180)
        for col, _name in enumerate(self.depth_names):
            values = RATING_LOSSES.get(col + 1)
            for row in range(len(labels)):
                text = "?" if values is None else f"{values[row]:+d}"
                item = QTableWidgetItem(text.replace("+0", "0"))
                item.setTextAlignment(Qt.AlignCenter)
                losses.setItem(row, col, item)
        losses.setFixedHeight(losses.horizontalHeader().height()
                              + sum(losses.rowHeight(r)
                                    for r in range(len(labels)))
                              + 2 * losses.frameWidth() + 2)
        box.addWidget(losses)

        box.addWidget(_note(
            "Unlike everything else on this tab, these figures are not read "
            "from the game files -- no param holds them. The win and unknown-"
            "Nightlord values are confirmed in game; the map bonus and the "
            "loss table are community-reported; Depth 1 costing nothing is "
            "confirmed in game. Bonuses add together: a Depth 3 win against "
            "an unknown Nightlord on an obstructed map is 200 + 100 + 100."
        ))
        return panel

    # -- enemy scaling ---------------------------------------------------
    # What a player actually wants to know: how much tougher do enemies get,
    # and in which way. The five elemental attack rates are identical on every
    # profile and every depth shipped, so they are one number, not five.
    # Two similarly named fields point in opposite directions, and the first
    # label here was wrong until it was checked: staminaAttackRate is stamina
    # the enemy's blows drain from you, while saReceiveDamageRate is stance
    # damage the enemy takes. Only the second answers "are they harder to
    # break". Both are named for who is on the receiving end.
    SUMMARY_ROWS = (
        ("Enemy HP", "maxHpRate"),
        ("Enemy attack power", "physicsAttackPowerRate"),
        ("Stance damage they take", "saReceiveDamageRate"),
        ("Stamina drain on block", "staminaAttackRate"),
    )

    def _summary(self) -> list[dict]:
        """Typical and extreme scaling per depth, across every enemy group.

        ChaosMatchingCorrectParam splits enemies into 89 rows across 25
        profiles and never records which creature sits in which row, so a
        single exact figure per depth would be a fiction. What the data does
        support is the typical multiplier and the spread around it, weighted
        by how many groups share each profile.
        """
        out = []
        for depth in range(len(self.depth_names)):
            column: dict[str, list] = {}
            for _label, field in self.SUMMARY_ROWS:
                values: list[float] = []
                for profile in self.scaling:
                    per_depth = profile.get("per_depth") or []
                    if depth >= len(per_depth) or not per_depth[depth]:
                        continue
                    value = per_depth[depth].get(field)
                    if isinstance(value, (int, float)):
                        weight = max(1, len(profile.get("rows") or []))
                        values += [value] * weight
                column[field] = values
            out.append(column)
        return out

    def _build_scaling(self) -> QWidget:
        panel = QWidget()
        box = QVBoxLayout(panel)
        box.setContentsMargins(0, 0, 0, 0)
        box.setSpacing(5)
        box.addWidget(_heading("HOW MUCH TOUGHER ENEMIES GET"))

        summary = self._summary()
        self.scaling_table = QTableWidget(len(self.SUMMARY_ROWS),
                                          len(self.depth_names))
        self.scaling_table.setHorizontalHeaderLabels(self.depth_names)
        self.scaling_table.setVerticalHeaderLabels(
            [label for label, _f in self.SUMMARY_ROWS])
        self.scaling_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.scaling_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.scaling_table.verticalHeader().setFixedWidth(180)

        for row, (_label, field) in enumerate(self.SUMMARY_ROWS):
            for col in range(len(self.depth_names)):
                values = summary[col].get(field) or []
                if not values:
                    text = "-"
                else:
                    typical = statistics.median(values)
                    low, high = min(values), max(values)
                    text = f"x{typical:.2f}"
                    if high - low > 0.005:
                        text += f"\n{low:.2f} to {high:.2f}"
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                self.scaling_table.setItem(row, col, item)
        self.scaling_table.resizeRowsToContents()
        height = (self.scaling_table.horizontalHeader().height()
                  + 2 * self.scaling_table.frameWidth() + 2)
        for row in range(len(self.SUMMARY_ROWS)):
            height += self.scaling_table.rowHeight(row)
        self.scaling_table.setFixedHeight(height)
        box.addWidget(self.scaling_table)

        box.addWidget(_note(self._scaling_headline()))
        return panel

    def _scaling_headline(self) -> str:
        """The one sentence worth taking away, plus what the figures are not."""
        summary = self._summary()
        if not summary:
            return ""
        lines: list[str] = []
        lines.append(
            "The top figure is the typical multiplier; the range below it is "
            "the spread across enemy groups. The game files sort enemies into "
            "89 groups but never record which creature is in which, so a "
            "single exact number per depth is not derivable -- the spread is "
            "shown instead of inventing one."
        )
        return "\n".join(lines)

    # -- the part that is not solved --------------------------------------

    # -- an open question --------------------------------------------------
    def _build_unidentified(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("unid")
        panel.setStyleSheet(
            f"#unid {{ background: {PANEL}; border: 1px solid {BORDER};"
            f" border-radius: 6px; }}"
            " #unid QLabel { background: transparent; border: none; }"
        )
        box = QVBoxLayout(panel)
        box.setContentsMargins(10, 8, 10, 8)
        box.setSpacing(3)

        title = QLabel("CATACLYSMS AND CONCEALMENT")
        title.setStyleSheet(
            f"color: {MUTED}; font-size: 11px; font-weight: bold;"
            " letter-spacing: 1px;"
        )
        box.addWidget(title)

        control = self.deep.get("control_raw", [])
        two, three = [], []
        for row in control:
            data = row.get("bytes", [])
            if len(data) > 7:
                two.append(f"depth {row['id']}: {data[6]}% / {data[7]}%")
                three.append(f"depth {row['id']}: {data[2]}/{data[3]}/{data[4]}")
        box.addWidget(_note(
            "How often each outcome comes up, by depth. Both sets are shares "
            "out of 100, read from the game's own depth table."
        ))
        box.addWidget(_note("Cataclysms -- one / two:    "
                            + "    ".join(two)))
        box.addWidget(_note("Concealment -- map / Nightlord / neither "
                            "(bytes +2/+3/+4):    " + "    ".join(three)))
        box.addWidget(_note(
            "The two-way split is the number of cataclysm events on the map -- "
            "the empowered camps that carry night invaders. It is one or the "
            "other, never none, which is why the pair always sums to 100: an "
            "even chance of one or two at Depths 1-2, shifting to almost "
            "always two by Depth 5. Community-sourced and consistent with "
            "play; it is not stated anywhere in the files."
        ))
        box.addWidget(_note(
            "The three-way split is what may be hidden from you. It switches "
            "on exactly at Depth 3, the same threshold the wiki gives for the "
            "map being concealed or the Nightlord obscured until the final "
            "day, and its two active buckets match that pair: 10% concealed "
            "map, 10% obscured Nightlord, 80% neither. Because it is one roll "
            "of three, the two never occur in the same run."
        ))
        box.addWidget(_note(
            "Both readings come from matching the shape of the numbers against "
            "what the game and its players describe. The files state neither. "
            "Ruled out along the way: neither split carries the Everdark "
            "chance, which begins at Depth 2, because neither moves between "
            "Depths 1 and 2."
        ))
        return panel
