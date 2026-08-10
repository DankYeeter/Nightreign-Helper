"""The six weapon tiles on the Build planner, and the dialog behind them.

A tile holds one armament, its upgrade tier, and the effects it has rolled.
Only effects the weapon can genuinely roll are offered -- `weapon["effect_pool"]`
comes from that weapon's own AttachEffectTable pools, the same mechanism that
gives a relic its three effects. See HANDOVER 6j.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QListWidgetItem, QScrollArea, QVBoxLayout,
    QWidget,
)

from . import effecttext, weapons

ACCENT = "#c8a45c"
MUTED = "#8a8a8a"
PANEL = "#1e1f23"
BORDER = "#2e2f35"
GOOD = "#78b57e"
BAD = "#d1655f"

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


def rollable_effects(weapon: dict | None, effects: dict) -> list[dict]:
    """The effects this weapon can roll, best-weighted first then by name."""
    if not weapon:
        return []
    out = []
    for entry in weapon.get("effect_pool", []):
        effect = effects.get(str(entry["effect"]))
        if effect is not None:
            out.append(effect)
    return sorted(out, key=lambda e: " ".join(e["name"].split()))


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

    def show_slot(self, slot: WeaponSlot, rating, active: bool = False) -> None:
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

        tier_name = dict(TIERS).get(slot.tier, "")
        self.title.setText(slot.weapon["name"])
        bits = [tier_name]
        if rating is not None:
            bits.append(f"<b style='color:{ACCENT}'>{rating.total:.0f}</b> AR")
        if slot.effect_ids:
            bits.append(f"{len(slot.effect_ids)} effect"
                        f"{'s' if len(slot.effect_ids) != 1 else ''}")
        if rating is not None and not rating.meets_requirements:
            bits.append(f"<span style='color:{BAD}'>requirements unmet</span>")
        self.detail.setText(" · ".join(b for b in bits if b))


class WeaponDialog(QDialog):
    """Choose an armament, its tier, and the effects it has rolled."""

    def __init__(self, parent, data: dict, slot: WeaponSlot, icons=None):
        super().__init__(parent)
        self.data = data
        self.icons = icons
        self.slot = slot.copy()
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
    def _refresh_list(self) -> None:
        term = self.search.text().strip().lower()
        self.list.blockSignals(True)
        self.list.clear()
        current = self.slot.weapon["id"] if self.slot.filled else None
        chosen_row = -1
        for weapon in sorted(self.data["weapons"], key=lambda w: w["name"]):
            if term and term not in weapon["name"].lower():
                continue
            item = QListWidgetItem(weapon["name"])
            item.setData(Qt.UserRole, weapon)
            if weapon.get("effect_pool"):
                item.setToolTip(f"{len(weapon['effect_pool'])} rollable effects")
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

        pool = rollable_effects(self.slot.weapon, self.data["effects"])
        if not pool:
            self.effects_note.setText(
                "This armament rolls no effects — the game gives it no pool.")
            return
        self.effects_note.setText(
            f"{len(pool)} effects this armament can roll. Choose up to "
            f"{MAX_WEAPON_EFFECTS}, as it would carry in game."
        )
        for effect in pool:
            box = QCheckBox(" ".join(effect["name"].split()))
            box.setChecked(effect["id"] in self.slot.effect_ids)
            box.setToolTip(effecttext.describe_full(effect))
            box.toggled.connect(
                lambda checked, e=effect: self._on_toggle(e, checked))
            self.effects_layout.addWidget(box)
            self._boxes.append(box)
        self.effects_layout.addStretch(1)
        self._sync_limit()

    def _on_toggle(self, effect: dict, checked: bool) -> None:
        if checked:
            if effect["id"] not in self.slot.effect_ids:
                self.slot.effect_ids.append(effect["id"])
        elif effect["id"] in self.slot.effect_ids:
            self.slot.effect_ids.remove(effect["id"])
        self._sync_limit()

    def _sync_limit(self) -> None:
        """Stop at three chosen effects rather than silently allowing more."""
        full = len(self.slot.effect_ids) >= MAX_WEAPON_EFFECTS
        for box in self._boxes:
            box.setEnabled(box.isChecked() or not full)

    def result_slot(self) -> WeaponSlot:
        self.slot.tier = self.tier.currentData() or weapons.MIN_UPGRADE
        return self.slot
