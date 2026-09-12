"""The five depths: how much tougher enemies get, and what it pays.

Every number here is read from the game's own params except the rating table,
which is labelled where it appears because no param holds it.

Laid out in the order a player asks the questions: what do I get for going
deeper, what does it cost me in difficulty, what moves my rating, and what else
changes. Anything that only answers "how do you know" is either one short line
or is not on the tab at all -- it lives in HANDOVER.md, which is where a reader
who wants the derivation is actually going to look.
"""

from __future__ import annotations

import re
import statistics

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QFrame, QHeaderView, QLabel, QScrollArea, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

from . import tabheader

ACCENT = "#c8a45c"
MUTED = "#8a8a8a"
PANEL = "#1e1f23"
BORDER = "#2e2f35"
DEEP = "#9a6fc4"

#: The roof over this tab's four headings (AK-68, AK-95). Its second sentence
#: is also the reference every scaling figure below is measured against, which
#: is why it is not repeated under the scaling table (QA-128, point 9).
HEADING = "DEEP OF NIGHT"
QUESTION = (
    "What a deeper run pays you, what it costs you, and how your Depth "
    "rating moves. All figures compare a Deep of Night run with a normal "
    "expedition.")


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
WIN_RATING = 200
RATING_BONUSES = [
    ("Unknown Nightlord", 100),
    ("Obstructed map", 100),
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

# The depth-control figures, by the game's own field names. This table was
# read byte by byte until 2026-08-16, when a real paramdef turned up and
# confirmed every column -- see nrdata.extract for the whole story.
CONTROL_ROWS = (
    ("Two cataclysms", "cataclysms_2"),
    ("Map concealed", "conceal_map"),
    ("Nightlord obscured", "conceal_nightlord"),
    ("Cursed relic — Uncommon", "cursed_uncommon"),
    ("Cursed relic — Rare", "cursed_rare"),
)


def _note(text: str) -> QLabel:
    label = QLabel(text)
    label.setWordWrap(True)
    label.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
    return label


def _source(text: str) -> QLabel:
    """A provenance line: present, findable, and visually out of the way."""
    label = QLabel(text)
    label.setWordWrap(True)
    label.setStyleSheet(f"color: {MUTED}; font-size: 10px;")
    return label


# These tables are read, not operated. Nothing on this tab responds to being
# clicked, so a click had no business repainting a cell in full accent gold and
# bolding its column header -- which is what it did, and it dominated the tab:
# one solid gold block on an otherwise even grid, marking a cell the reader
# happened to touch on the way past. The styling below turns selection and
# focus off outright and states every colour, rather than inheriting a palette
# built for editable widgets.
#
# Contrast is set deliberately: figures brightest, because they are the
# content; row and column headers a step down, because they are labels the eye
# should skim; grid lines barely there, because they only need to separate.
TABLE_STYLE = f"""
QTableWidget {{
    background: {PANEL};
    alternate-background-color: #24262b;
    gridline-color: {BORDER};
    color: #e4e4e4;
    border: 1px solid {BORDER};
    border-radius: 4px;
    font-size: 12px;
}}
QTableWidget::item {{ padding: 4px 6px; }}
QTableWidget::item:selected {{ background: transparent; color: #e4e4e4; }}
QHeaderView::section {{
    background: {PANEL};
    color: {MUTED};
    border: none;
    border-bottom: 1px solid {BORDER};
    padding: 5px 6px;
    font-weight: normal;
}}
QHeaderView::section:vertical {{
    border-bottom: none;
    border-right: 1px solid {BORDER};
    padding-left: 2px;
}}
QTableCornerButton::section {{ background: {PANEL}; border: none; }}
"""


def _fit(table: QTableWidget) -> QTableWidget:
    """Size a table to its contents, with no dead strip under the last row.

    Rows must be measured after they have been told to size themselves.
    Reading rowHeight() before that returns the default, which is what clipped
    the last row of the rating table clean off and let the table below it
    overlap what was left.
    """
    table.setEditTriggers(QTableWidget.NoEditTriggers)
    table.setSelectionMode(QAbstractItemView.NoSelection)
    table.setFocusPolicy(Qt.NoFocus)
    table.setAlternatingRowColors(True)
    table.setShowGrid(True)
    table.setStyleSheet(TABLE_STYLE)
    table.horizontalHeader().setHighlightSections(False)
    table.verticalHeader().setHighlightSections(False)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table.resizeRowsToContents()
    height = table.horizontalHeader().height() + 2 * table.frameWidth() + 2
    for row in range(table.rowCount()):
        height += table.rowHeight(row)
    table.setFixedHeight(height)
    return table


def _cell(text: str, tone: str = "") -> QTableWidgetItem:
    item = QTableWidgetItem(text)
    item.setTextAlignment(Qt.AlignCenter)
    return item


class DeepTab(QWidget):
    HEADER_WIDTH = 190

    def __init__(self, data: dict):
        super().__init__()
        self.deep = data.get("deep_of_night") or {}
        self.scaling = self.deep.get("scaling", [])
        self.labels = self.deep.get("field_labels", {})
        depths = self.deep.get("depth_count", 5)
        self.depth_names = [f"Depth {i + 1}" for i in range(depths)]

        # Four tables sized to their rows stack to more than a screen, and a
        # QTabWidget hands the tallest of its pages to the whole window: this
        # one page asked for 1195 logical px on Windows -- 1838 physical at
        # 150 % scale, against a screen 1600 px tall -- so the program had a
        # minimum height no monitor here could satisfy and the tab's last two
        # lines could neither be seen nor scrolled to (DR-015, AK-71, AK-97).
        # Inside a scroll area the same content asks for 69; the tab is as
        # tall as the window allows and the reader scrolls the rest.
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.scroll)

        content = QWidget()
        self.scroll.setWidget(content)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(14)

        layout.addWidget(tabheader.heading(HEADING))
        layout.addWidget(tabheader.question(QUESTION))

        layout.addWidget(self._build_rewards())
        layout.addWidget(self._build_scaling())
        layout.addWidget(self._build_rating())
        layout.addWidget(self._build_odds())
        layout.addStretch(1)

    def _section(self, title: str) -> tuple[QWidget, QVBoxLayout]:
        panel = QWidget()
        box = QVBoxLayout(panel)
        box.setContentsMargins(0, 0, 0, 0)
        box.setSpacing(5)
        box.addWidget(tabheader.heading(title))
        return panel, box

    def _table(self, rows: list[str]) -> QTableWidget:
        table = QTableWidget(len(rows), len(self.depth_names))
        table.setHorizontalHeaderLabels(self.depth_names)
        table.setVerticalHeaderLabels(rows)
        table.verticalHeader().setFixedWidth(self.HEADER_WIDTH)
        return table

    # -- what each depth is worth ------------------------------------------
    def _build_rewards(self) -> QWidget:
        panel, box = self._section("WHAT EACH DEPTH IS WORTH")

        sigil = self.deep.get("sigil_name") or "Sovereign Sigils"
        # The rating band belongs in this table rather than in a list of its
        # own underneath it. It is the entry price for the column it sits in,
        # and reading it against the reward is the whole question.
        bands = self._rating_bands()
        rewards = self.deep.get("rewards", [])
        # The relic tier each depth can hand out. Named rather than listed in
        # full: every tier comes in the same four colours, so the tier is the
        # information and repeating the colours is not.
        tiers = [self._relic_tiers(r) for r in rewards]
        rows = ["Rating needed", "Reward multiplier", sigil]
        if any(tiers):
            rows.append("Relic tier")
        table = self._table(rows)

        for column in range(len(self.depth_names)):
            table.setItem(0, column, _cell(bands.get(column + 1, "-")))
            reward = rewards[column] if column < len(rewards) else None
            if reward is None:
                continue
            table.setItem(1, column, _cell(f"x{reward['multiplier']:g}"))
            table.setItem(2, column, _cell(str(reward["sigils"])))
            if len(rows) > 3:
                table.setItem(3, column, _cell(tiers[column] or "-"))
        box.addWidget(_fit(table))

        # The two figures of this table that carried no reference at all
        # (QA-128, points 7 and 8). The multiplier is real and its subject is
        # not in the files, so the tab says that rather than letting a reader
        # supply a subject of their own; the sigil count is read, while the
        # name against it was identified in game.
        box.addWidget(_note(
            "Reward multiplier: the game's own multiplier for this Depth. "
            "The files do not say what it multiplies, so it is shown as a "
            "comparison between Depths and nothing more."
        ))
        box.addWidget(_note(
            f"{sigil}: the figure comes from the depth table. That the item "
            f"is the {sigil} was identified in game, not read from a link in "
            f"the files."
        ))
        # The game's own description of the item, loaded since the extractor
        # first read the depth table and thrown away every time until now.
        # Quoted, so it reads as the game's wording and not as this tab's.
        info = (self.deep.get("sigil_info") or "").strip()
        if info:
            box.addWidget(_source(f"In the game's own words: “{info}”."))

        # Kept from the game's own tutorial because it changes how you play:
        # it says when a loss cannot cost you the Depth you have reached.
        box.addWidget(_note(
            "Once you reach Depth 2 you cannot drop back to Depth 1, and at "
            "Depth 3 your Depth is held for several expeditions before it can "
            "fall."
        ))
        if any(tiers):
            box.addWidget(_note(
                "Relic tiers run Delicate, Polished, then Grand, and every "
                "tier comes in all four colours. The reward lots drop the "
                "lower tiers as the Depth rises — by Depth 4 only Grand "
                "relics are on the table. A “Deep” relic is one that works "
                "only in the Deep of Night."
            ))
            box.addWidget(_source(
                "Read from the depth reward table's own item lots, through "
                "the map lot table to the relic list."
            ))
        return panel

    @staticmethod
    def _relic_tiers(reward: dict | None) -> str:
        """The tier words a depth's reward relics carry, weakest tier first.

        The extracted names are whole relic names -- "Grand Burning Scene" --
        and the leading word is the tier. Reading the tier off the name is
        safe because all four colours share one naming scheme; a name that
        starts with no known tier is carried whole rather than dropped.
        """
        if not reward:
            return ""
        order = ["Delicate", "Polished", "Grand"]
        found: list[str] = []
        for name in reward.get("items", []):
            deep = name.startswith("Deep ")
            bare = name[len("Deep "):] if deep else name
            tier = next((t for t in order if bare.startswith(t)), None)
            label = f"Deep {tier}" if (tier and deep) else (tier or name)
            if label not in found:
                found.append(label)
        found.sort(key=lambda t: (order.index(t.split()[-1])
                                 if t.split()[-1] in order else len(order), t))
        return ", ".join(found)

    def _rating_bands(self) -> dict[int, str]:
        """Depth -> the rating band that puts you in it, from the game's text."""
        out: dict[int, str] = {}
        for line in (self.deep.get("rating_text") or "").splitlines():
            match = re.search(r"Depth\s*(\d+)\s*:\s*Rating\s*(\S+)", line)
            if match:
                out[int(match.group(1))] = match.group(2)
        return out

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
        panel, box = self._section("HOW MUCH TOUGHER ENEMIES GET")

        summary = self._summary()
        self.scaling_table = self._table(
            [label for label, _f in self.SUMMARY_ROWS])

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
                self.scaling_table.setItem(row, col, _cell(text))
        box.addWidget(_fit(self.scaling_table))

        box.addWidget(_note(
            "The big figure is typical; the range under it is the spread from "
            "the weakest enemy group to the toughest."
        ))
        return panel

    # -- rating per expedition --------------------------------------------
    def _build_rating(self) -> QWidget:
        panel, box = self._section("WHAT MOVES YOUR RATING")

        # One table, not two. Winning and losing are the same question asked
        # in two directions, and splitting them meant the gains table did not
        # vary by depth yet still carried a full set of depth columns.
        rows = ["Win", "Lost to the Nightlord", "Lost on day 2", "Lost on day 1"]
        table = self._table(rows)
        for col in range(len(self.depth_names)):
            table.setItem(0, col, _cell(f"+{WIN_RATING}"))
            losses = RATING_LOSSES.get(col + 1)
            for row in range(3):
                text = "?" if losses is None else f"{losses[row]:+d}"
                table.setItem(row + 1, col, _cell(text.replace("+0", "0")))
        box.addWidget(_fit(table))

        bonuses = ", ".join(f"{name} +{value}"
                           for name, value in RATING_BONUSES)
        box.addWidget(_note(
            f"On top of a win, and they add up: {bonuses}. So a win against an "
            f"unknown Nightlord on an obstructed map is "
            f"+{WIN_RATING + sum(v for _n, v in RATING_BONUSES)}."
        ))
        box.addWidget(_source(
            "The only figures on this tab the game's own data does not "
            "state. The win value and Depth 1 costing nothing are confirmed "
            "in game; the bonuses and the loss table are community-reported."
        ))
        return panel

    # -- what else changes -------------------------------------------------
    def _build_odds(self) -> QWidget:
        panel, box = self._section("WHAT ELSE CHANGES WITH DEPTH")

        table = self._table([label for label, _key in CONTROL_ROWS])
        control = {row.get("depth"): row
                   for row in self.deep.get("depth_control", [])}
        for col in range(len(self.depth_names)):
            data = control.get(col + 1) or {}
            for row, (_label, key) in enumerate(CONTROL_ROWS):
                value = data.get(key)
                text = f"{value}%" if value is not None else "-"
                table.setItem(row, col, _cell(text))
        box.addWidget(_fit(table))

        box.addWidget(_note(
            "Cataclysms are the empowered camps that carry night invaders — "
            "the game never places zero, so the figure above is the chance of "
            "the second. Concealment starts at Depth 3, and because it is one "
            "roll of three, the map and the Nightlord are never hidden in the "
            "same run. The cursed-relic rates do not move with depth."
        ))
        # The raw field names used to be printed here as provenance. They
        # belong in the code, not on screen: to a player they are noise, and
        # the provenance is already said in words.
        box.addWidget(_source(
            "Read from the game's own depth table."
        ))
        return panel
