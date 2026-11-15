"""The best relic effects for one Nightfarer and goal, and which you own.

User request 2026-11-15: "do I have the best, or what do I need to buy to
possibly get the best effects?" Every rollable effect is rated on its own by
the advisor's goals -- one copy against the Nightfarer with no relic at all --
and stands beside how many relics of the save carry it, normal and Deep of
Night counted apart, and where it can roll.
"""

from __future__ import annotations

import collections
import dataclasses
from collections.abc import Callable, Mapping

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon
from PySide6.QtWidgets import (
    QCheckBox, QFrame, QHBoxLayout, QHeaderView, QLabel, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

from . import damage, effecttext, model, tabheader, weapons
from .advisor import evaluate, goals, types
from .advisorbar import GOAL_ORDER
from .backdrop import ChoiceBox
from .effectstab import (
    BUFF_COLOUR, ChanceItem, FilterCaption, format_chance, identity,
)
from .theme import BAD, BORDER, DEEP, GOOD, MUTED, PANEL

HEADING = "THE BEST EFFECTS, AND WHETHER YOU OWN THEM"
QUESTION = (
    "Every effect a relic can roll, ranked by what one copy adds for this "
    "Nightfarer and goal, beside how many of your relics carry it. A "
    "conditional effect counts as if its condition held; one that needs an "
    "armament type or an ailment counts only where the Nightfarer's starting "
    "armament brings it.")

COLUMNS = ["#", "Effect", "Gain", "Owned", "Owned Deep", "Rolls on normal",
           "Rolls on Deep", "Status"]
COL_RANK, COL_NAME, COL_GAIN, COL_OWNED, COL_DEEP = range(5)
COL_ROLLS, COL_ROLLS_DEEP, COL_STATUS = 5, 6, 7

HEADER_TIPS = {
    COL_GAIN: "What one copy adds to the goal's figure, against this "
              "Nightfarer with no relic at all.",
    COL_OWNED: "Normal relics in your save that carry this effect.",
    COL_DEEP: "Deep of Night relics in your save that carry this effect.",
    COL_ROLLS: "Colours of normal relics that can roll it, and the chance "
               "per relic effect slot that can.",
    COL_ROLLS_DEEP: "Colours of Deep of Night relics that can roll it, and "
                    "the chance per relic effect slot that can.",
    COL_STATUS: "'other version': you own a weaker tier or another variant "
                "of this effect, not this one.",
}

OWNED, OTHER_VERSION, MISSING = "owned", "other version", "missing"
NO_SAVE = "No save was read, so nothing is counted as owned."
SHOW = (("Top 30", 30), ("Top 50", 50), ("Top 100", 100), ("All", 0))


@dataclasses.dataclass(frozen=True)
class Source:
    """Where one kind of relic rolls an effect: colours and the chance per
    slot that can roll it, each colour weighted by its slots."""
    colours: tuple[int, ...] = ()
    chance: float = 0.0


@dataclasses.dataclass(frozen=True)
class Row:
    effect: Mapping
    gain: float
    normal: Source
    deep: Source
    family: str
    owned: int = 0
    owned_deep: int = 0
    #: Relics carrying another effect of the same family.
    other_versions: int = 0

    @property
    def status(self) -> str:
        if self.owned or self.owned_deep:
            return OWNED
        return OTHER_VERSION if self.other_versions else MISSING


def _source(rows: list[Mapping], colour_key: str, chance_key: str) -> Source:
    colours = sorted({c for row in rows for c in row.get(colour_key) or ()})
    entries = [c for row in rows for c in (row.get(chance_key) or {}).values()]
    slots = sum(c["pools"] for c in entries)
    return Source(tuple(colours),
                  sum(c["avg"] * c["pools"] for c in entries) / slots
                  if slots else 0.0)


def context(data: Mapping, hero: Mapping, level: int) -> types.GoalContext:
    """The advisor's question with the starting armament on the selected
    tile and nothing held (`advisorbar.asking_from`, same baseline rules)."""
    effects = data["effects"]
    start = next((w for w in data["weapons"]
                  if w["id"] == hero.get("starting_weapon")), None)
    start_type = None if start is None else start.get("wep_type")
    inflicted = set((start or {}).get("inflicts") or {}) | {None}
    neutral = (data.get("field_baselines") or {}).get("wepTypeTrigger")
    declared, assumed = {}, []
    for effect_id, count in model.advisor_defaults().items():
        effect = effects[str(effect_id)]
        mods = effect["modifiers"]
        if effecttext.ailment_awaited(effect) not in inflicted:
            continue
        if mods.get("triggerOnWepType") not in (None, start_type) and any(
                w.get("wep_type") == mods["triggerOnWepType"]
                for w in data["weapons"]):
            continue
        if effecttext.counts_armaments(effect):
            if (start is not None
                    and mods.get("wepTypeTrigger", neutral) == start_type):
                assumed.append(effect_id)
            continue
        declared[effect_id] = count
    return types.GoalContext(
        data=data, hero=hero, level=level,
        reference=None if start is None else types.ReferenceArmament(
            weapon=start, tier=weapons.MIN_UPGRADE,
            slot_index=damage.STARTING_SLOT),
        weighting=goals.DEFAULT_WEIGHTING,
        declared=tuple(sorted(declared.items())),
        assumed_armament_counts=tuple(assumed))


def rank(data: Mapping, hero: Mapping, level: int, goal_id: str,
         owned=None) -> list[Row]:
    """Every rollable buff this Nightfarer gains from, best first."""
    goal = goals.GOALS[goal_id]
    ctx = context(data, hero, level)
    nothing = types.SlotProblem()

    def figure(effect_ids: tuple[int, ...]) -> float:
        asked = dataclasses.replace(ctx, armament_effect_ids=effect_ids)
        build = evaluate.evaluate(nothing, (), asked, want_qualitative=False,
                                  goal=goal)
        return goal.score(build, asked).value

    base = figure(())
    # Points are read as points; every other figure as a share of the bare one.
    relative = goal_id != goals.MAX_ATTRIBUTES.id and base > 0
    families = data.get("weapon_families", {})
    hero_name = str(hero.get("name", ""))
    identities: dict[tuple, list[Mapping]] = collections.defaultdict(list)
    for effect in data["effects"].values():
        identities[identity(effect)].append(effect)
    # One row per name and gain: the game keeps some effects as several
    # records that do the same ("Taking attacks improves attack power" is
    # three), and a reader counts them as one.
    groups: dict[tuple, list[Mapping]] = collections.defaultdict(list)
    for rows in identities.values():
        first = rows[0]
        if first.get("is_curse") or first.get("is_debuff"):
            continue
        if not any(row.get("colours") or row.get("deep_colours")
                   for row in rows):
            continue
        if not effecttext.works_for(first, hero_name):
            continue
        gain = figure((first["id"],)) - base
        if relative:
            gain /= base
        if gain > 1e-9:
            groups[effecttext.name(first), round(gain, 9)].extend(rows)

    carried: collections.Counter = collections.Counter()
    carried_deep: collections.Counter = collections.Counter()
    by_family: collections.Counter = collections.Counter()
    if owned is not None:
        of_id = {row["id"]: key for key, rows in groups.items()
                 for row in rows}
        family_of = {str(effect["id"]): effecttext.family_key(effect, families)
                     for effect in data["effects"].values()}
        for relic in owned.relics:
            keys = {of_id[i] for i in relic.effect_ids if i in of_id}
            (carried_deep if relic.is_deep else carried).update(keys)
            by_family.update({family_of[str(i)] for i in relic.effect_ids
                              if str(i) in family_of})

    ranked = [Row(
        effect=rows[0], gain=key[1],
        normal=_source(rows, "colours", "chance"),
        deep=_source(rows, "deep_colours", "deep_chance"),
        family=effecttext.family_key(rows[0], families),
        owned=carried[key], owned_deep=carried_deep[key],
        other_versions=by_family[effecttext.family_key(rows[0], families)])
        for key, rows in groups.items()]
    ranked.sort(key=lambda row: (-row.gain, effecttext.name(row.effect)))
    return ranked


def best_versions(rows: list[Row]) -> list[Row]:
    """The strongest effect of each family; `rows` is best first."""
    seen: set[str] = set()
    return [row for row in rows
            if row.family not in seen and not seen.add(row.family)]


def gain_text(gain: float, goal_id: str) -> str:
    if goal_id == goals.MAX_ATTRIBUTES.id:
        return f"+{gain:g} {goals.ATTRIBUTE_POINT_UNIT}"
    return f"+{gain * 100:.1f}%"


class _Card(QFrame):
    """One figure of the summary, on glass."""

    def __init__(self, caption: str):
        super().__init__()
        self.setStyleSheet(
            f"_Card {{ background: {PANEL}; border: 1px solid {BORDER};"
            " border-radius: 10px; }")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(0)
        self.figure = QLabel("—")
        self.figure.setTextFormat(Qt.RichText)
        self.figure.setStyleSheet("font-size: 20px; font-weight: 600;")
        caption_label = QLabel(caption)
        caption_label.setWordWrap(True)
        caption_label.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        layout.addWidget(self.figure)
        layout.addWidget(caption_label)


class RecommendedTab(QWidget):
    def __init__(self, data: dict, icons=None,
                 gem_strip: Callable | None = None):
        super().__init__()
        self.data = data
        self.icons = icons
        self._gem_strip = gem_strip
        self.owned = None
        self.level = 15
        self._followed_hero: int | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.addWidget(tabheader.heading(HEADING))
        layout.addWidget(tabheader.question(QUESTION))

        controls = QHBoxLayout()
        controls.addWidget(FilterCaption("Nightfarer"))
        self.hero_box = ChoiceBox()
        for hero in data["heroes"]:
            self.hero_box.addItem(hero["name"], hero["id"])
        controls.addWidget(self.hero_box)
        controls.addWidget(FilterCaption("Goal"))
        self.goal_box = ChoiceBox()
        for goal_id in GOAL_ORDER:
            self.goal_box.addItem(goals.GOALS[goal_id].label, goal_id)
        self.goal_box.setCurrentIndex(GOAL_ORDER.index(goals.BALANCED.id))
        controls.addWidget(self.goal_box)
        controls.addWidget(FilterCaption("Show"))
        self.show_box = ChoiceBox()
        for label, count in SHOW:
            self.show_box.addItem(label, count)
        controls.addWidget(self.show_box)
        self.best_only = QCheckBox("Best version only")
        self.best_only.setToolTip(
            "Of the tiers and variants of one effect, show the strongest.")
        self.best_only.setChecked(True)
        controls.addWidget(self.best_only)
        self.missing_only = QCheckBox("Missing only")
        controls.addWidget(self.missing_only)
        controls.addStretch(1)
        layout.addLayout(controls)

        cards = QHBoxLayout()
        self.owned_card = _Card("of the effects shown are on your relics")
        self.split_card = _Card("on normal · on Deep of Night relics")
        self.missing_card = _Card("still missing; where they roll is below")
        for card in (self.owned_card, self.split_card, self.missing_card):
            cards.addWidget(card, 1)
        layout.addLayout(cards)

        self.summary = QLabel()
        self.summary.setWordWrap(True)
        self.summary.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        layout.addWidget(self.summary)

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        for column, tip in HEADER_TIPS.items():
            self.table.horizontalHeaderItem(column).setToolTip(tip)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(COL_NAME, QHeaderView.Stretch)
        layout.addWidget(self.table, 1)

        for box in (self.hero_box, self.goal_box, self.show_box):
            box.currentIndexChanged.connect(self.refresh)
        for check in (self.best_only, self.missing_only):
            check.toggled.connect(self.refresh)
        self.refresh()

    def set_inventory(self, owned) -> None:
        self.owned = owned
        self.refresh()

    def follow(self, hero_id: int, level: int) -> None:
        """Take the planner's level, and its Nightfarer when that changed
        since the last look; one chosen here stays otherwise."""
        self.level = level
        if hero_id != self._followed_hero:
            self._followed_hero = hero_id
            index = self.hero_box.findData(hero_id)
            if index >= 0 and index != self.hero_box.currentIndex():
                self.hero_box.setCurrentIndex(index)   # refreshes
                return
        self.refresh()

    def rows(self) -> list[Row]:
        """What the table shows, in order."""
        hero = self.data["heroes"][self.hero_box.currentIndex()]
        ranked = rank(self.data, hero, self.level,
                      self.goal_box.currentData(), self.owned)
        if self.best_only.isChecked():
            ranked = best_versions(ranked)
        count = self.show_box.currentData()
        if count:
            ranked = ranked[:count]
        return ranked

    def _rolls_item(self, source: Source) -> QTableWidgetItem:
        item = ChanceItem(source.chance)
        names = ", ".join(model.COLOUR_NAMES.get(c, str(c))
                          for c in source.colours)
        if source.colours:
            item.setText(format_chance(source.chance))
            item.setToolTip(f"{names}: {format_chance(source.chance)} per "
                            "relic effect slot that can roll it")
            strip = (self._gem_strip(source.colours)
                     if self._gem_strip is not None else None)
            if strip is not None:
                item.setData(Qt.DecorationRole, strip)
            else:
                item.setText(f"{names} {format_chance(source.chance)}")
        else:
            item.setToolTip("Does not roll on these relics.")
        return item

    def refresh(self) -> None:
        shown = self.rows()
        goal_id = self.goal_box.currentData()
        have = [row for row in shown if row.status == OWNED]
        counted = self.owned is not None
        self.owned_card.figure.setText(
            f"<span style='color:{GOOD}'>{len(have)} / {len(shown)}</span>"
            if counted else "—")
        self.split_card.figure.setText(
            f"{sum(1 for row in have if row.owned)} · <span style='color:"
            f"{DEEP}'>{sum(1 for row in have if row.owned_deep)}</span>"
            if counted else "—")
        self.missing_card.figure.setText(
            f"<span style='color:{BAD}'>{len(shown) - len(have)}</span>"
            if counted else "—")
        self.summary.setText(
            f"Rated at level {self.level}."
            + ("" if counted else f" {NO_SAVE}"))

        if self.missing_only.isChecked() and counted:
            shown = [(rank_, row) for rank_, row in enumerate(shown, 1)
                     if row.status != OWNED]
        else:
            shown = list(enumerate(shown, 1))

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(shown))
        for r, (position, row) in enumerate(shown):
            effect = row.effect
            name = QTableWidgetItem(effecttext.name(effect))
            name.setForeground(BUFF_COLOUR)
            name.setToolTip(f"{effecttext.name(effect)}\n"
                            f"{effecttext.describe_full(effect)}")
            if self.icons is not None:
                symbol = self.icons.status(effect.get("icon"))
                if symbol is not None:
                    name.setIcon(QIcon(symbol))
            place = QTableWidgetItem()
            place.setData(Qt.DisplayRole, position)
            gain = ChanceItem(row.gain)
            gain.setText(gain_text(row.gain, goal_id))
            gain.setForeground(QColor(GOOD))
            cells = [place, name, gain]
            for count, colour in ((row.owned, None), (row.owned_deep, DEEP)):
                cell = QTableWidgetItem()
                if counted:
                    cell.setData(Qt.DisplayRole, count)
                    cell.setForeground(QColor(
                        colour or GOOD if count
                        else MUTED if row.status == OWNED else BAD))
                else:
                    cell.setText("—")
                cells.append(cell)
            cells += [self._rolls_item(row.normal),
                      self._rolls_item(row.deep)]
            status = QTableWidgetItem(row.status if counted else "")
            status.setForeground(QColor(
                {OWNED: GOOD, MISSING: BAD}.get(row.status, MUTED)))
            if counted and row.status == OTHER_VERSION:
                status.setToolTip(
                    f"{row.other_versions} of your relics carry another "
                    f"version of {row.family}.")
            cells.append(status)
            for column, cell in enumerate(cells):
                if column not in (COL_NAME, COL_STATUS):
                    cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if not cell.toolTip():
                    cell.setToolTip(cell.text())
                self.table.setItem(r, column, cell)
        self.table.setSortingEnabled(True)
        self.table.sortByColumn(COL_RANK, Qt.AscendingOrder)
