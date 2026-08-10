"""Weapons, sorceries and incantations as collapsible sections of tiles."""

from __future__ import annotations

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QScrollArea, QSpinBox, QToolButton, QVBoxLayout, QWidget,
)

from . import model, search, weapons
from .weapons import RARITY_TIERS

COLUMNS = 5
ICON = 52
CARD_WIDTH = 200

ACCENT = "#c8a45c"
MUTED = "#8a8a8a"
PANEL = "#1e1f23"
BORDER = "#2e2f35"

# EquipParamWeapon.rarity, rarest first.
RARITY_NAMES = {3: "Legendary", 2: "Rare", 1: "Uncommon", 0: "Common"}

# Sampled from the game's own MENU_In_RaritySlot_0x sprites in SB_In_Game_1:
# grey, blue, purple, gold. The border uses a lifted version of the same hue
# so it reads clearly against the dark panel.
RARITY_COLOURS = {
    0: ("#5f5f5f", "#8d8d8d"),
    1: ("#294f69", "#4a86b0"),
    2: ("#523676", "#8a5fc4"),
    3: ("#7a4e1a", "#c8892c"),
}


class Tile(QFrame):
    """One weapon or spell: icon, name, and its numbers listed underneath."""

    def __init__(self, title: str, icon, lines: list[tuple[str, str]],
                 dimmed: bool = False, rarity: int | None = None):
        super().__init__()
        self.setFixedWidth(CARD_WIDTH)
        self.setObjectName("tile")
        # Scope the frame styling to this widget and force children to be
        # transparent, otherwise every child label repaints the background and
        # the stat rows read as grey pills.
        if rarity is not None and rarity in RARITY_COLOURS:
            tint, border = RARITY_COLOURS[rarity]
            frame = (
                f"#tile {{ background: qlineargradient(x1:0, y1:0, x2:0, y2:1,"
                f" stop:0 {tint}, stop:0.55 {PANEL}, stop:1 {PANEL});"
                f" border: 1px solid {border}; border-radius: 7px; }}"
            )
        else:
            frame = (f"#tile {{ background: {PANEL}; border: 1px solid {BORDER};"
                     f" border-radius: 7px; }}")
        self.setStyleSheet(frame + " #tile QLabel { background: transparent;"
                                   " border: none; }")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(3)

        header = QHBoxLayout()
        header.setSpacing(8)
        badge = QLabel()
        badge.setFixedSize(ICON, ICON)
        badge.setStyleSheet("border: none;")
        if icon is not None:
            badge.setPixmap(icon.scaled(ICON, ICON, Qt.KeepAspectRatio,
                                        Qt.SmoothTransformation))
        header.addWidget(badge)

        name = QLabel(title)
        name.setWordWrap(True)
        colour = MUTED if dimmed else "#e4e4e4"
        name.setStyleSheet(f"border: none; font-weight: bold; color: {colour};")
        header.addWidget(name, 1)
        layout.addLayout(header)

        rule = QFrame()
        rule.setFrameShape(QFrame.HLine)
        rule.setFixedHeight(1)
        rule.setStyleSheet(f"background: {BORDER}; border: none;")
        layout.addWidget(rule)

        for index, (label, value) in enumerate(lines):
            row = QHBoxLayout()
            row.setSpacing(4)
            left = QLabel(label)
            left.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
            right = QLabel(value)
            right.setAlignment(Qt.AlignRight)
            # Lead with the headline number, then quieter detail rows.
            emphasis = ("font-size: 13px; color: #f0e2c0;" if index == 0
                        else "font-size: 11px; color: #cfcfcf;")
            right.setStyleSheet(f"{emphasis} font-weight: bold;")
            row.addWidget(left)
            row.addWidget(right, 1)
            layout.addLayout(row)

        layout.addStretch()


class Section(QWidget):
    """A folding heading whose contents are built on first expand.

    Building every tile up front means tens of thousands of widgets, which
    stalls the window, so the body is deferred until the user opens it.
    """

    def __init__(self, title: str, builder, level: int = 0):
        super().__init__()
        self._builder = builder
        self._built = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.toggle = QToolButton()
        self.toggle.setText(title)
        self.toggle.setCheckable(True)
        self.toggle.setChecked(False)
        self.toggle.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle.setArrowType(Qt.RightArrow)
        size = 13 if level == 0 else 11
        self.toggle.setStyleSheet(
            f"QToolButton {{ border: none; font-weight: bold; font-size: {size}px;"
            f" color: {ACCENT if level == 0 else '#e4e4e4'}; padding: 4px 0px; }}"
        )
        self.toggle.clicked.connect(self._on_toggle)
        layout.addWidget(self.toggle)

        self.body = QWidget()
        self.body.setVisible(False)
        layout.addWidget(self.body)
        self._layout = layout

    def _on_toggle(self) -> None:
        show = self.toggle.isChecked()
        if show and not self._built:
            self._built = True
            QApplication.setOverrideCursor(Qt.WaitCursor)
            try:
                widget = self._builder()
            finally:
                QApplication.restoreOverrideCursor()
            self._layout.replaceWidget(self.body, widget)
            self.body.deleteLater()
            self.body = widget
        self.body.setVisible(show)
        self.toggle.setArrowType(Qt.DownArrow if show else Qt.RightArrow)


class ArsenalTab(QWidget):
    def __init__(self, data: dict, planner, icons):
        super().__init__()
        self.data = data
        self.planner = planner
        self.icons = icons

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)

        controls = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText(
            "Search — supports AND, OR, NOT and \"quoted phrases\""
        )
        self.search.setClearButtonEnabled(True)
        # Rebuilding the section list costs about half a second, so wait for a
        # pause in typing rather than doing it on every keystroke.
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(250)
        self._debounce.timeout.connect(self.rebuild)
        self.search.textChanged.connect(lambda *_: self._debounce.start())
        controls.addWidget(self.search, 1)

        controls.addWidget(QLabel("Upgrade to +"))
        self.upgrade = QSpinBox()
        self.upgrade.setRange(weapons.MIN_UPGRADE, weapons.MAX_UPGRADE)
        self.upgrade.setToolTip(
            "Target rarity: +1 Common, +2 Uncommon, +3 Rare, +4 Legendary.\n"
            "A weapon already at or above the target is shown unchanged."
        )
        self.upgrade.valueChanged.connect(self.recalculate)
        controls.addWidget(self.upgrade)

        controls.addWidget(QLabel("Rarity"))
        self.rarity_box = QComboBox()
        self.rarity_box.addItem("All", -1)
        for value in sorted(RARITY_NAMES, reverse=True):
            self.rarity_box.addItem(RARITY_NAMES[value], value)
        self.rarity_box.currentIndexChanged.connect(self.rebuild)
        controls.addWidget(self.rarity_box)

        self.usable_only = QCheckBox("Meets requirements")
        self.usable_only.setChecked(True)
        self.usable_only.toggled.connect(self.recalculate)
        controls.addWidget(self.usable_only)
        layout.addLayout(controls)

        self.summary = QLabel()
        self.summary.setWordWrap(True)
        self.summary.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        layout.addWidget(self.summary)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        layout.addWidget(self.scroll, 1)

        self.ratings: list[weapons.WeaponRating] = []
        self.recalculate()

    # -- data ------------------------------------------------------------
    def recalculate(self) -> None:
        hero = self.planner.current_hero()
        level = self.planner.level_slider.value()
        build = model.compute(hero, level, self.planner.selected_effects(),
                              self.planner.curves)
        self.attributes = build.attributes
        self.ratings = weapons.rank(
            self.data, build.attributes,
            upgrade=self.upgrade.value(),
            require_usable=self.usable_only.isChecked(),
        )
        stats = "  ".join(f"{k[:3].upper()} {v}"
                          for k, v in build.attributes.items())
        self.header_text = (
            f"{hero['name']} at level {level}, +{self.upgrade.value()} — {stats}"
        )
        self.rebuild()

    def _grid(self, tiles: list[Tile]) -> QWidget:
        holder = QWidget()
        grid = QGridLayout(holder)
        grid.setSpacing(8)
        grid.setContentsMargins(12, 0, 0, 8)
        grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        for i, tile in enumerate(tiles):
            grid.addWidget(tile, i // COLUMNS, i % COLUMNS)
        return holder

    def rebuild(self) -> None:
        predicate = search.parse(self.search.text())

        root = QWidget()
        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 8, 0)
        outer.setSpacing(6)

        shown = 0
        shown += self._build_weapons(outer, predicate)
        shown += self._build_spells(outer, predicate, "Sorceries")
        shown += self._build_spells(outer, predicate, "Incantations")

        outer.addStretch()
        self.scroll.setWidget(root)
        self.summary.setText(
            f"{self.header_text}. {shown} shown. Attack rating is base damage "
            f"plus what your stats add to it. Spell damage is not in the game "
            f"data, so spells show their costs instead."
        )

    def _build_weapons(self, outer, predicate) -> int:
        wanted_rarity = self.rarity_box.currentData()
        by_family: dict[str, list] = {}
        for rating in self.ratings:
            weapon = rating.weapon
            if predicate is not None and not predicate(
                [weapon["name"], weapon.get("family", "")]
            ):
                continue
            # Match the rarity the weapon would have after upgrading, so the
            # filter agrees with the colour shown on the tile.
            if wanted_rarity != -1:
                effective = min(weapon.get("rarity", 0) + rating.applied_upgrade,
                                RARITY_TIERS - 1)
                if effective != wanted_rarity:
                    continue
            by_family.setdefault(weapon.get("family", "Other"), []).append(rating)

        total = sum(len(v) for v in by_family.values())

        def build_family(entries):
            # Rarest first, then alphabetically inside each rarity band.
            entries = sorted(entries, key=lambda r: (-r.weapon.get("rarity", 0),
                                                     r.weapon["name"].lower()))
            tiles = []
            for rating in entries:
                weapon = rating.weapon
                lines = [("AR", f"{rating.total:.0f}")]
                for damage in weapons.DAMAGE_TYPES:
                    value = rating.base.get(damage, 0) + rating.scaled.get(damage, 0)
                    if value:
                        lines.append((weapons.DAMAGE_LABELS[damage], f"{value:.0f}"))
                lines.append(("Rarity", RARITY_NAMES.get(weapon.get("rarity", 0), "?")))
                reached = min(weapon.get("rarity", 0) + 1 + rating.applied_upgrade,
                              weapons.MAX_UPGRADE)
                if rating.applied_upgrade:
                    lines.append(("Upgraded to", f"+{reached} "
                                                 f"{RARITY_NAMES.get(reached - 1, '')}"))
                if rating.unmet:
                    need = " ".join(f"{s[:3].upper()} {n}"
                                    for s, (_h, n) in rating.unmet.items())
                    lines.append(("Requires", need))
                # Colour by the rarity the weapon would actually have at the
                # chosen upgrade target, not its shelf rarity.
                effective = min(weapon.get("rarity", 0) + rating.applied_upgrade,
                                RARITY_TIERS - 1)
                tiles.append(Tile(weapon["name"],
                                  self.icons.item(weapon.get("icon")),
                                  lines, dimmed=bool(rating.unmet),
                                  rarity=effective))
            return self._grid(tiles)

        def build_body():
            body = QWidget()
            inner = QVBoxLayout(body)
            inner.setContentsMargins(10, 0, 0, 0)
            inner.setSpacing(4)
            for family in sorted(by_family):
                entries = by_family[family]
                inner.addWidget(Section(
                    f"{family}  ({len(entries)})",
                    lambda e=entries: build_family(e),
                    level=1,
                ))
            return body

        outer.addWidget(Section(f"Weapons  ({total})", build_body))
        return total

    def _build_spells(self, outer, predicate, category: str) -> int:
        by_family: dict[str, list] = {}
        for spell in self.data.get("spells", []):
            if spell["category"] != category:
                continue
            if predicate is not None and not predicate(
                [spell["name"], spell.get("family", "")]
            ):
                continue
            by_family.setdefault(spell.get("family", "General"), []).append(spell)

        total = sum(len(v) for v in by_family.values())

        def build_family(entries):
            tiles = []
            for spell in sorted(entries, key=lambda s: s["name"].lower()):
                lines = [("FP", str(spell.get("fp") or 0))]
                if spell.get("fp_charged"):
                    lines.append(("FP charged", str(spell["fp_charged"])))
                if spell.get("stamina"):
                    lines.append(("Stamina", str(spell["stamina"])))
                lines.append(("Slots", str(spell.get("slots") or 1)))
                tiles.append(Tile(spell["name"],
                                  self.icons.item(spell.get("icon")), lines))
            return self._grid(tiles)

        def build_body():
            body = QWidget()
            inner = QVBoxLayout(body)
            inner.setContentsMargins(10, 0, 0, 0)
            inner.setSpacing(4)
            for family in sorted(by_family):
                entries = by_family[family]
                inner.addWidget(Section(
                    f"{family}  ({len(entries)})",
                    lambda e=entries: build_family(e),
                    level=1,
                ))
            return body

        outer.addWidget(Section(f"{category}  ({total})", build_body))
        return total
