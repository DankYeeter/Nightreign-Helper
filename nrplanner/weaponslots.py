"""The six weapon tiles on the Build planner, and the dialog behind them.

A tile holds one armament, its upgrade tier, and the effects it has rolled.
Only effects the weapon can genuinely roll are offered -- `weapon["effect_pool"]`
comes from that weapon's own AttachEffectTable pools, the same mechanism that
gives a relic its three effects.
"""

from __future__ import annotations

import collections
from dataclasses import dataclass, field

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QListWidgetItem, QScrollArea, QVBoxLayout,
    QWidget,
)

from . import damage, effecttext, weapons

ACCENT = "#c8a45c"
MUTED = "#8a8a8a"
PANEL = "#1e1f23"
BORDER = "#2e2f35"
GOOD = "#78b57e"
# The red the Effects tab gives a curse, so a negative roll
# reads the same wherever it appears.
DEBUFF = "#e07a74"

# The rarity a weapon reads as, in the same colours the Weapons tab uses for
# its tiles. An upgrade raises the tier a weapon counts as, so the name is
# coloured by where it ends up rather than where it started.
RARITY_NAMES = {0: "Common", 1: "Uncommon", 2: "Rare", 3: "Legendary"}
RARITY_TEXT = {
    0: "#b9b9b9",
    1: "#6fa8d6",
    2: "#a97fe0",
    3: "#e0a94a",
}

SLOT_COUNT = 6
SLOT_COLUMNS = 3
# A weapon draws from up to three pools, so it can carry three rolled effects,
# exactly as a relic does.
MAX_WEAPON_EFFECTS = 3

TIERS = ((1, "Common"), (2, "Uncommon"), (3, "Rare"), (4, "Legendary"))


@dataclass
class WeaponSlot:
    """One tile's contents. An empty tile has no weapon."""
    weapon: dict | None = None
    tier: int = weapons.MIN_UPGRADE
    effect_ids: list[int] = field(default_factory=list)

    def copy(self) -> "WeaponSlot":
        return WeaponSlot(self.weapon, self.tier, list(self.effect_ids))

    @property
    def filled(self) -> bool:
        return self.weapon is not None


def rollable_effects(weapon: dict | None, effects: dict,
                     all_weapons: list[dict] | None = None) -> list[dict]:
    """The effects this weapon can roll, by name.

    An infused armament carries an empty pool in the game's data, and taken
    literally that would mean it can hold nothing at all. It does not: the
    owner reports from play that an infused weapon either carries just its
    infusion, or the infusion **plus a buff and a debuff**. So an infused
    weapon is offered its own uninfused version's pool, and the picker caps
    it at one of each -- see `effect_limits`. The empty pool is read as
    "the infusion is the roll it already spent", not as "nothing is
    possible".
    """
    if not weapon:
        return []
    source = weapon
    if not weapon.get("effect_pool") and all_weapons:
        # Only an *infused* variant inherits, and an infused variant always
        # has a lower-id sibling: the uninfused version it came from. A base
        # armament with an empty pool -- Unarmed, the Nightfarers' starting
        # weapons -- has no lower sibling and must stay empty, or it would
        # be handed a pool it never rolls from.
        band = weapon["id"] // 10000
        lower = [w for w in all_weapons if w["id"] // 10000 == band
                 and w["id"] < weapon["id"] and w.get("effect_pool")]
        if lower:
            source = min(lower, key=lambda w: w["id"])
    out = []
    for entry in source.get("effect_pool", []):
        effect = effects.get(str(entry["effect"]))
        if effect is not None:
            out.append(effect)
    return sorted(out, key=lambda e: " ".join(e["name"].split()))


def is_debuff(effect: dict) -> bool:
    return bool(effect.get("is_debuff") or effect.get("is_curse"))


def effect_limits(weapon: dict, bases: set[int]) -> tuple[int, int]:
    """How many buffs and debuffs this armament may carry.

    Uninfused: up to three effects, any mix, exactly as a relic rolls.
    Infused: the infusion is already one roll, so at most one further buff
    and one debuff. Both figures are the owner's, from play.
    """
    if weapon["id"] in bases:
        return MAX_WEAPON_EFFECTS, MAX_WEAPON_EFFECTS
    return 1, 1


def base_ids(all_weapons: list[dict]) -> set[int]:
    """The id of the uninfused version of every armament.

    Infusion variants are sibling rows in one id band -- Longsword 2000000,
    Fire Longsword 2000500, Sacred 2000700 -- and the lowest id in a band is
    the uninfused one.
    """
    lowest: dict[int, int] = {}
    for weapon in all_weapons:
        band = weapon["id"] // 10000
        if band not in lowest or weapon["id"] < lowest[band]:
            lowest[band] = weapon["id"]
    return set(lowest.values())


def why_no_effects(weapon: dict, bases: set[int]) -> str:
    """Why this armament offers nothing to choose, in the player's terms.

    There are exactly two reasons and the difference matters. An infused
    armament has **already rolled** -- the infusion is the effect it came
    with, which is why the game offers it no pool on top. The eight that
    never roll at all are Unarmed and the Nightfarers' own starting
    armaments, and no other choice fixes that.
    """
    if weapon["id"] not in bases:
        return ("Its infusion is the effect it rolled. The uninfused version "
                "rolls from a pool instead.")
    return "This armament never rolls effects."


class WeaponTile(QFrame):
    """One of the six armament slots.

    Single-click makes the tile active, which is what the damage breakdown
    below describes. Double-click opens the dialog to choose or edit the
    armament. Right-click empties it.
    """

    def __init__(self, index: int, on_edit, on_clear, on_activate):
        super().__init__()
        self.index = index
        self.on_edit = on_edit
        self.on_clear = on_clear
        self.on_activate = on_activate
        self.active = False

        self.setFrameShape(QFrame.StyledPanel)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(62)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(2)

        self.title = QLabel()
        self.title.setWordWrap(True)
        self.title.setStyleSheet("border: none; font-weight: bold;")
        layout.addWidget(self.title)

        self.detail = QLabel()
        self.detail.setWordWrap(True)
        self.detail.setStyleSheet(f"border: none; color: {MUTED};"
                                  f" font-size: 10px;")
        layout.addWidget(self.detail)

        self.show_slot(WeaponSlot(), None)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.RightButton:
            self.on_clear(self.index)
        else:
            self.on_activate(self.index)

    def mouseDoubleClickEvent(self, event) -> None:
        # Qt delivers a press before the double-click, so the tile is already
        # active by the time this runs -- opening the dialog is all that is
        # left to do. Empty tiles open it too, which is how a weapon gets in.
        if event.button() != Qt.RightButton:
            self.on_edit(self.index)

    def show_slot(self, slot: WeaponSlot, rating, active: bool = False,
                  effects: dict | None = None) -> None:
        """Draw one tile. `rating` is the slot's `damage.Rating`, or None.

        The rating answers `damage.Question.EQUIPPED` -- this armament, in
        this slot, as it stands -- and the tile shows its finished figure, the
        one after the attack multipliers, under the name the facade gives it.
        It is the same number the breakdown panel puts under the grid, out of
        the same call, which is what W3 of AD-019 was for: the tile used to
        rate the armament for itself and arrived at a different total for the
        same slot (QA-056).

        Left untyped for the same reason `damage.equipped` leaves its slot
        untyped: this module imports Qt and `damage` does not, so the arrow
        between them only ever points one way.
        """
        self.active = active
        border = ACCENT if active else BORDER
        width = 2 if active else 1
        self.setStyleSheet(
            f"QFrame {{ background: {PANEL}; border: {width}px solid {border};"
            f" border-radius: 6px; }}"
        )
        if not slot.filled:
            self.title.setText(f"<span style='color:{MUTED}'>Slot "
                               f"{self.index + 1} — empty</span>")
            self.detail.setText("double-click to add an armament")
            return

        # The upgrade tier is an absolute rarity: a Common weapon taken to +2
        # reads as Rare, so the name is coloured for what it has become and
        # the tier is named beside it.
        native = slot.weapon.get("rarity", 0)
        reached = min(max(native, slot.tier - 1), max(RARITY_TEXT))
        colour = RARITY_TEXT.get(reached, "#e4e4e4")
        self.title.setText(
            f"<span style='color:{colour}'>{slot.weapon['name']}</span>")
        tier_name = RARITY_NAMES.get(reached, "")
        upgrade = slot.tier - 1 - native
        if upgrade > 0:
            tier_name += f" +{upgrade}"
        bits = [tier_name]
        if rating is not None:
            # Figure and label both from the facade: a staff shows the spell
            # scaling the game shows for it and no attack rating (QA-099).
            bits.append(f"<b style='color:{ACCENT}'>"
                        f"{damage.displayed(rating.final_headline)}</b>"
                        f" {rating.headline_label}")
        if slot.effect_ids:
            # Count the negative rolls apart from the rest, in the same red
            # the picker uses, so a tile shows at a glance that one of its
            # effects is a downside.
            bad = 0
            if effects:
                bad = sum(1 for i in slot.effect_ids
                          if is_debuff(effects.get(str(i), {})))
            good = len(slot.effect_ids) - bad
            if good:
                bits.append(f"{good} effect{'s' if good != 1 else ''}")
            if bad:
                bits.append(f"<span style='color:{DEBUFF}'>{bad} debuff"
                            f"{'s' if bad != 1 else ''}</span>")
        self.detail.setText(" · ".join(b for b in bits if b))


class WeaponDialog(QDialog):
    """Choose an armament, its tier, and the effects it has rolled."""

    def __init__(self, parent, data: dict, slot: WeaponSlot, icons=None):
        super().__init__(parent)
        self.data = data
        self.icons = icons
        self.slot = slot.copy()
        self._bases = base_ids(data["weapons"])
        self._name_counts = collections.Counter(
            w["name"] for w in data["weapons"])
        self._effects_by_id = {int(k): v for k, v in data["effects"].items()}
        self._pool: list[dict] = []
        self.setWindowTitle("Armament")
        self.resize(560, 640)

        layout = QVBoxLayout(self)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search armaments…")
        self.search.textChanged.connect(self._refresh_list)
        layout.addWidget(self.search)

        self.list = QListWidget()
        self.list.setIconSize(QSize(28, 28))
        self.list.currentItemChanged.connect(self._on_weapon_changed)
        layout.addWidget(self.list, 1)

        row = QHBoxLayout()
        row.addWidget(QLabel("Upgrade"))
        self.tier = QComboBox()
        for value, label in TIERS:
            self.tier.addItem(label, value)
        index = self.tier.findData(self.slot.tier)
        if index >= 0:
            self.tier.setCurrentIndex(index)
        row.addWidget(self.tier, 1)
        layout.addLayout(row)

        self.effects_note = QLabel()
        self.effects_note.setWordWrap(True)
        self.effects_note.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        layout.addWidget(self.effects_note)

        # A Longsword rolls from 369 effects, so the list is unusable without
        # a filter. It hides rows rather than rebuilding them, which keeps
        # what is already ticked ticked -- and keeps a chosen effect visible
        # even when it does not match, so nothing can be silently lost behind
        # a search term.
        self.effect_search = QLineEdit()
        self.effect_search.setPlaceholderText("Search effects…")
        self.effect_search.setClearButtonEnabled(True)
        self.effect_search.textChanged.connect(self._filter_effects)
        layout.addWidget(self.effect_search)

        area = QScrollArea()
        area.setWidgetResizable(True)
        self.effects_host = QWidget()
        self.effects_layout = QVBoxLayout(self.effects_host)
        self.effects_layout.setContentsMargins(2, 2, 2, 2)
        self.effects_layout.setSpacing(2)
        area.setWidget(self.effects_host)
        layout.addWidget(area, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._boxes: list[QCheckBox] = []
        self._refresh_list()

    # -- weapon list ------------------------------------------------------
    def _list_label(self, weapon: dict) -> str:
        """The armament's name, and its id where the name is not its own.

        Three names in the data belong to more than one row: `Recluse's
        Staff` (33750000 is the Recluse's own, 33770000 cannot hold a spell
        and carries a different spell scaling), `Finger Seal` and `Scholar's
        Thrusting Sword`. Picking one of two identical rows in this list is
        picking blind, and the two `Recluse's Staff` rows do not even rate
        alike -- so where a name is shared, the id that tells them apart is
        put beside it (QA-099 a).

        Whether the unplayable rows belong in the dataset at all is not
        settled and is not this dialog's to settle; until it is, the player
        can at least see that there are two and which one they chose.
        """
        name = weapon["name"]
        if self._name_counts[name] > 1:
            return f"{name} · {weapon['id']}"
        return name

    def _refresh_list(self) -> None:
        term = self.search.text().strip().lower()
        self.list.blockSignals(True)
        self.list.clear()
        current = self.slot.weapon["id"] if self.slot.filled else None
        chosen_row = -1
        for weapon in sorted(self.data["weapons"], key=lambda w: w["name"]):
            if term and term not in weapon["name"].lower():
                continue
            item = QListWidgetItem(self._list_label(weapon))
            item.setData(Qt.UserRole, weapon)
            if weapon.get("effect_pool"):
                item.setToolTip(f"{len(weapon['effect_pool'])} rollable effects")
            elif weapon["id"] in self._bases:
                # The eight that genuinely roll nothing -- Unarmed and the
                # Nightfarers' starting armaments. Dimmed, because no other
                # choice makes effects appear.
                item.setForeground(QColor(MUTED))
                item.setToolTip(why_no_effects(weapon, self._bases))
            else:
                # Infused: its own pool is empty because the infusion is the
                # roll it spent, but it can still take a buff and a debuff,
                # so it is not dimmed.
                item.setToolTip("Infused — can still roll one buff and one "
                                "debuff")
            if self.icons is not None:
                icon = self.icons.item_icon(weapon.get("icon"))
                if icon is not None:
                    item.setIcon(icon)
            self.list.addItem(item)
            if weapon["id"] == current:
                chosen_row = self.list.count() - 1
        self.list.blockSignals(False)
        if chosen_row >= 0:
            self.list.setCurrentRow(chosen_row)
        elif self.list.count():
            self.list.setCurrentRow(0)
        else:
            self._rebuild_effects()

    def _on_weapon_changed(self, current, _previous) -> None:
        if current is None:
            return
        weapon = current.data(Qt.UserRole)
        if self.slot.weapon is None or weapon["id"] != self.slot.weapon["id"]:
            # A different armament rolls from a different pool, so effects
            # chosen for the old one cannot be carried across.
            self.slot.effect_ids = []
        self.slot.weapon = weapon
        self._rebuild_effects()

    # -- effects ----------------------------------------------------------
    def _rebuild_effects(self) -> None:
        while self.effects_layout.count():
            item = self.effects_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._boxes = []
        self._pool = []

        pool = rollable_effects(self.slot.weapon, self.data["effects"],
                                self.data["weapons"])
        if not pool:
            self.effects_note.setText(
                why_no_effects(self.slot.weapon, self._bases)
                if self.slot.weapon else "Choose an armament first.")
            return
        infused = self.slot.weapon["id"] not in self._bases
        if infused:
            self._pool_note = (
                "Infused: it already carries its elemental effect. On top of "
                "that it can roll one more buff and one debuff — or neither."
            )
        else:
            self._pool_note = (
                f"{len(pool)} effects this armament can roll. Choose up to "
                f"{MAX_WEAPON_EFFECTS}, as it would carry in game."
            )
        self.effects_note.setText(self._pool_note)
        for effect in pool:
            box = QCheckBox(" ".join(effect["name"].split()))
            box.setChecked(effect["id"] in self.slot.effect_ids)
            box.setToolTip(effecttext.describe_full(effect))
            # A negative roll comes from the same pool as everything else and
            # is only told apart by what it does, so it is coloured rather
            # than separated out.
            if is_debuff(effect):
                box.setStyleSheet(f"color: {DEBUFF};")
            box.toggled.connect(
                lambda checked, e=effect: self._on_toggle(e, checked))
            self.effects_layout.addWidget(box)
            self._boxes.append(box)
            self._pool.append(effect)
        self.effects_layout.addStretch(1)
        self._sync_limit()
        # A term typed for the last armament still applies to this one.
        self._filter_effects()

    def _filter_effects(self) -> None:
        """Show the effects matching the term, plus anything already chosen."""
        term = self.effect_search.text().strip().lower()
        shown = 0
        for box, effect in zip(self._boxes, self._pool):
            keep = (not term
                    or term in " ".join(effect["name"].split()).lower()
                    or term in (effect.get("info") or "").lower()
                    or box.isChecked())
            box.setVisible(keep)
            shown += bool(keep)
        if term and hasattr(self, "_pool_note"):
            self.effects_note.setText(
                f"{shown} of {len(self._pool)} shown  ·  {self._pool_note}")
        elif hasattr(self, "_pool_note"):
            self.effects_note.setText(self._pool_note)

    def _on_toggle(self, effect: dict, checked: bool) -> None:
        if checked:
            if effect["id"] not in self.slot.effect_ids:
                self.slot.effect_ids.append(effect["id"])
        elif effect["id"] in self.slot.effect_ids:
            self.slot.effect_ids.remove(effect["id"])
        self._sync_limit()

    def _sync_limit(self) -> None:
        """Stop at what the armament could actually carry.

        An uninfused weapon takes three of anything; an infused one takes a
        buff and a debuff on top of its infusion, so the two are counted
        separately and a full half stops offering more of its own kind.
        """
        if not self.slot.weapon:
            return
        max_buffs, max_debuffs = effect_limits(self.slot.weapon, self._bases)
        chosen = [self._effects_by_id[i] for i in self.slot.effect_ids
                  if i in self._effects_by_id]
        buffs = sum(1 for e in chosen if not is_debuff(e))
        debuffs = sum(1 for e in chosen if is_debuff(e))
        total_full = len(self.slot.effect_ids) >= MAX_WEAPON_EFFECTS
        for box, effect in zip(self._boxes, self._pool):
            if box.isChecked():
                box.setEnabled(True)
                continue
            if is_debuff(effect):
                box.setEnabled(debuffs < max_debuffs)
            else:
                box.setEnabled(buffs < max_buffs and not total_full)

    def result_slot(self) -> WeaponSlot:
        self.slot.tier = self.tier.currentData() or weapons.MIN_UPGRADE
        return self.slot
