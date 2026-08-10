"""Browsable table of every relic effect, its roll chance and what it does."""

from __future__ import annotations

import collections
import json

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from . import effecttext, model
from .effecttext import caption, describe, describe_full  # noqa: F401

COLUMNS = ["Effect", "Type", "Tier", "Copies", "Colours", "Pools",
           "Avg chance", "Best chance", "Stacks", "Comes with curse",
           "What it does"]

# Column indices used for formatting, kept next to COLUMNS so they move
# together if the layout changes.
COL_TYPE = 1
COL_COPIES = 3
COL_POOLS = 5
COL_AVG = 6
COL_BEST = 7
COL_STACKS = 8
COL_CURSE = 9
NUMERIC = (COL_COPIES, COL_POOLS, COL_AVG, COL_BEST)

# "Buff" sorts before "Curse", so sorting on the Type column groups them the
# way round the player wants without any special-casing. It also survives the
# user clicking other headers -- they can always click Type to get it back.
TYPE_BUFF = "Buff"
TYPE_CURSE = "Curse"

CURSE_LABEL = {
    "always": "always cursed",
    "sometimes": "sometimes",
    "never": "",
}

# Buffs read blue, curses red, so which is which never has to be worked out
# from the wording.
BUFF_COLOUR = QColor("#7fb2e5")
CURSE_COLOUR = QColor("#e07a74")


def format_chance(value: float) -> str:
    if value >= 0.01:
        return f"{value * 100:.1f}%"
    return f"{value * 100:.2f}%"


def identity(effect: dict) -> tuple:
    """What makes two effect rows genuinely the same effect.

    The params carry a great many rows that are byte-for-byte the same effect
    under the same name -- 1000 "Grief" rows are really 30 effects, ten
    Nightfarers times three strengths. Collapsing on the name alone would be
    wrong, though: "Increased Maximum HP" exists twice as genuinely different
    effects, one granting Max HP +10% and the other Vigor +5. So identity is
    the name together with what the effect actually does, and rows only merge
    when both agree.
    """
    return (
        " ".join(str(effect.get("name", "")).split()),
        tuple(effect.get("sp_effect_ids") or []),
        json.dumps(effect.get("modifiers", {}), sort_keys=True),
    )


def deduplicate(effects: list[dict]) -> list[tuple[dict, int]]:
    """Collapse identical rows, keeping a count of how many were merged."""
    groups: dict[tuple, list[dict]] = collections.OrderedDict()
    for eff in effects:
        groups.setdefault(identity(eff), []).append(eff)
    return [(rows[0], len(rows)) for rows in groups.values()]


def tier_label(effect: dict, siblings: list[dict]) -> str:
    """Where this effect sits in a ladder of same-named, differing strengths.

    Several effects ship as a set of increasing magnitudes under one name --
    the Grief relics are +3 / +6 / +9 on two attributes. They are separate
    effects with their own SpEffect ids, not duplicates, so they each keep a
    row; this labels which rung each one is so the repetition makes sense.
    """
    if len(siblings) < 2:
        return ""
    ordered = sorted(siblings, key=_magnitude)
    try:
        position = next(i for i, e in enumerate(ordered)
                        if e["id"] == effect["id"])
    except StopIteration:
        return ""
    return f"{position + 1} of {len(ordered)}"


def _magnitude(effect: dict) -> tuple:
    """A sort key ranking one variant of an effect against its siblings."""
    numbers = [v for v in effect.get("modifiers", {}).values()
               if isinstance(v, (int, float))]
    return (sum(abs(float(v)) for v in numbers), effect.get("id", 0))


class EffectsTab(QWidget):
    def __init__(self, data: dict):
        super().__init__()
        self.effects = list(data["effects"].values())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)

        controls = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search effects and descriptions…")
        self.search.textChanged.connect(self.refresh)
        controls.addWidget(self.search, 1)

        self.colour_box = QComboBox()
        self.colour_box.addItem("All colours", -1)
        for value, name in model.COLOUR_NAMES.items():
            if value == 4:
                continue  # White is a slot property, never a relic colour
            self.colour_box.addItem(name, value)
        self.colour_box.currentIndexChanged.connect(self.refresh)
        controls.addWidget(self.colour_box)

        self.mode_box = QComboBox()
        self.mode_box.addItem("Normal + Deep", "all")
        self.mode_box.addItem("Normal relics", "normal")
        self.mode_box.addItem("Deep of Night", "deep")
        self.mode_box.currentIndexChanged.connect(self.refresh)
        controls.addWidget(self.mode_box)

        self.rollable_only = QCheckBox("Rollable on relics only")
        self.rollable_only.setChecked(True)
        self.rollable_only.toggled.connect(self.refresh)
        controls.addWidget(self.rollable_only)

        self.nonstacking_only = QCheckBox("Non-stacking only")
        self.nonstacking_only.toggled.connect(self._on_nonstacking)
        controls.addWidget(self.nonstacking_only)

        self.stacking_only = QCheckBox("Stacking only")
        self.stacking_only.toggled.connect(self._on_stacking)
        controls.addWidget(self.stacking_only)

        self.kind_box = QComboBox()
        self.kind_box.addItem("Buffs and curses", "all")
        self.kind_box.addItem("Buffs only", "buffs")
        self.kind_box.addItem("Curses only", "curses")
        self.kind_box.currentIndexChanged.connect(self.refresh)
        controls.addWidget(self.kind_box)

        layout.addLayout(controls)

        self.summary = QLabel()
        self.summary.setStyleSheet("color: #8a8a8a; font-size: 11px;")
        layout.addWidget(self.summary)

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(len(COLUMNS) - 1, QHeaderView.Stretch)
        layout.addWidget(self.table, 1)

        self.refresh()

    def _on_nonstacking(self, checked: bool) -> None:
        # The two filters are opposites; ticking one clears the other.
        if checked and self.stacking_only.isChecked():
            self.stacking_only.setChecked(False)
        self.refresh()

    def _on_stacking(self, checked: bool) -> None:
        if checked and self.nonstacking_only.isChecked():
            self.nonstacking_only.setChecked(False)
        self.refresh()

    @staticmethod
    def _matches(effect: dict, needle: str) -> bool:
        """Search the description too, not just the name.

        Now that descriptions are shown, searching only names would leave the
        user able to read "restores FP on successive attacks" but unable to
        find it by typing that.
        """
        haystack = f"{effecttext.name(effect)} {describe_full(effect)}".lower()
        return needle in haystack

    def refresh(self) -> None:
        needle = self.search.text().strip().lower()
        colour = self.colour_box.currentData()
        mode = self.mode_box.currentData()

        if mode == "normal":
            colour_keys, chance_keys = ["colours"], ["chance"]
        elif mode == "deep":
            colour_keys, chance_keys = ["deep_colours"], ["deep_chance"]
        else:
            colour_keys = ["colours", "deep_colours"]
            chance_keys = ["chance", "deep_chance"]

        kind = self.kind_box.currentData()

        candidates = []
        for eff in self.effects:
            bad = bool(eff.get("is_curse") or eff.get("is_debuff"))
            if kind == "buffs" and bad:
                continue
            if kind == "curses" and not bad:
                continue
            colours = sorted(set().union(*(set(eff[k]) for k in colour_keys)))
            # A curse is rollable, just from a curse pool rather than a colour
            # pool, so it must never be filtered out as "not rollable".
            if self.rollable_only.isChecked() and not colours and not bad:
                continue
            if self.nonstacking_only.isChecked() and eff["stacks"]:
                continue
            if self.stacking_only.isChecked() and not eff["stacks"]:
                continue
            if colour != -1 and colour not in colours:
                continue
            if needle and not self._matches(eff, needle):
                continue
            candidates.append((eff, colours))

        # Collapse identical rows before display. Colours are unioned across
        # the merged rows so nothing is lost by dropping the copies.
        merged: dict[tuple, tuple[dict, set, int]] = collections.OrderedDict()
        for eff, colours in candidates:
            key = identity(eff)
            if key in merged:
                prev_eff, prev_colours, count = merged[key]
                merged[key] = (prev_eff, prev_colours | set(colours), count + 1)
            else:
                merged[key] = (eff, set(colours), 1)

        # Siblings: same name, different strength. Needed for the tier column.
        by_name: dict[str, list[dict]] = collections.defaultdict(list)
        for eff, _colours, _count in merged.values():
            by_name[" ".join(str(eff.get("name", "")).split())].append(eff)

        rows = [(eff, sorted(colours), count)
                for eff, colours, count in merged.values()]

        # Buffs first, then curses, each alphabetical. Keeping them in one
        # table rather than splitting into a second tab means a search covers
        # both at once, and the colour makes which is which unmissable.
        rows.sort(key=lambda r: (bool(r[0].get("is_curse")
                                      or r[0].get("is_debuff")),
                                 effecttext.name(r[0]).lower()))

        hidden = len(candidates) - len(rows)
        note = (f" {hidden} identical duplicates merged." if hidden else "")
        n_curses = sum(1 for eff, _c, _n in rows
                       if eff.get("is_curse") or eff.get("is_debuff"))
        undescribed = sum(1 for eff, _c, _n in rows
                          if describe_full(eff) == effecttext.NO_DESCRIPTION)
        missing = (f" {undescribed} carry no detail beyond their name in the "
                   f"game files." if undescribed else "")
        self.summary.setText(
            f"{len(rows) - n_curses} buffs (blue) then {n_curses} curses "
            f"(red).{note}{missing} Chance is how likely an effect is on one "
            f"roll of the selected colour and mode; where an effect can come "
            f"from several pools you see its average and its best. 'Tier' "
            f"marks effects that come in a ladder of strengths under one name."
        )

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(rows))
        for r, (eff, colours, copies) in enumerate(rows):
            relevant = []
            for key in chance_keys:
                chance = eff.get(key, {})
                if colour != -1:
                    if str(colour) in chance:
                        relevant.append(chance[str(colour)])
                else:
                    relevant.extend(chance.values())

            pools = sum(c["pools"] for c in relevant)
            avg = (sum(c["avg"] for c in relevant) / len(relevant)) if relevant else 0.0
            best = max((c["max"] for c in relevant), default=0.0)

            display_name = effecttext.name(eff)
            description = describe_full(eff)
            is_bad = bool(eff.get("is_curse") or eff.get("is_debuff"))
            values = [
                display_name,
                TYPE_CURSE if is_bad else TYPE_BUFF,
                tier_label(eff, by_name[display_name]),
                copies,
                ", ".join(model.COLOUR_NAMES.get(c, str(c)) for c in colours),
                pools,
                avg,
                best,
                "yes" if eff["stacks"] else "strongest only",
                "is a curse" if eff.get("is_curse")
                else CURSE_LABEL.get(eff.get("curse", "never"), ""),
                description,
            ]
            for c, value in enumerate(values):
                if c == COL_COPIES or c == COL_POOLS:
                    item = QTableWidgetItem()
                    item.setData(Qt.DisplayRole, int(value))
                elif c in (COL_AVG, COL_BEST):
                    item = QTableWidgetItem()
                    item.setData(Qt.DisplayRole, float(value))
                    item.setText(format_chance(float(value)) if value else "—")
                else:
                    item = QTableWidgetItem(str(value))
                if c in NUMERIC:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                # Blue for a buff, red for a curse, on the name and on what it
                # does -- the two cells the eye actually lands on.
                if c in (0, COL_TYPE, len(values) - 1):
                    item.setForeground(CURSE_COLOUR if is_bad else BUFF_COLOUR)
                if c == COL_STACKS and not eff["stacks"]:
                    item.setForeground(Qt.red)
                if c == COL_CURSE and value:
                    item.setForeground(CURSE_COLOUR)
                # The full text is often wider than the column; the tooltip
                # gives it in full without forcing a huge column.
                if c == len(values) - 1:
                    item.setToolTip(description)
                    if description == effecttext.NO_DESCRIPTION:
                        item.setForeground(Qt.gray)
                self.table.setItem(r, c, item)

        # Enabling sorting makes Qt immediately re-sort by whatever indicator
        # the header is showing, which would scatter the curses back among the
        # buffs. Sorting on Type explicitly restores the grouping and leaves
        # the header still clickable.
        self.table.setSortingEnabled(True)
        self.table.sortByColumn(COL_TYPE, Qt.AscendingOrder)
        self.table.resizeColumnsToContents()
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(len(COLUMNS) - 1, QHeaderView.Stretch)
