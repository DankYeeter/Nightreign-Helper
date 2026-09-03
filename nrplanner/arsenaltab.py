"""Weapons, sorceries and incantations as collapsible sections of tiles."""

from __future__ import annotations

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QScrollArea, QSpinBox, QToolButton, QVBoxLayout, QWidget,
)

from . import damage, search, weapons
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
                 dimmed: bool = False, rarity: int | None = None,
                 blurb: str = ""):
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
            # A value wider than the tile must wrap, not clip: the scaling
            # rows ("STR 43 · DEX 43 · ARC 45") lost their leading characters
            # on a fixed-width card otherwise.
            right.setWordWrap(True)
            # Lead with the headline number, then quieter detail rows.
            emphasis = ("font-size: 13px; color: #f0e2c0;" if index == 0
                        else "font-size: 11px; color: #cfcfcf;")
            right.setStyleSheet(f"{emphasis} font-weight: bold;")
            row.addWidget(left)
            row.addWidget(right, 1)
            layout.addLayout(row)

        # The game's own description, where one exists. Spells carried these
        # in the snapshot from the start and never showed them, so choosing
        # between Ranni's and Rennala's moons came down to which cost 10 FP
        # less.
        if blurb:
            text = QLabel(blurb)
            text.setWordWrap(True)
            text.setStyleSheet(f"color: {MUTED}; font-size: 10px;")
            layout.addWidget(text)

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

    def expand_all(self) -> None:
        """Open this section and every subsection it builds.

        Only for small result sets: the laziness exists because building
        everything is thousands of widgets, and the caller is responsible
        for knowing the count is modest before asking.
        """
        if not self.toggle.isChecked():
            self.toggle.setChecked(True)
            self._on_toggle()
        for child in self.body.findChildren(Section):
            child.expand_all()


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

        self.ratings: list[damage.Rating] = []
        self.recalculate()

    # -- data ------------------------------------------------------------
    def recalculate(self) -> None:
        hero = self.planner.current_hero()
        level = self.planner.level_slider.value()
        # The build the planner tab is showing, not one computed again here.
        # This tab used to work out its own, with four of the seven arguments
        # missing -- no curses, no armament effects, no declared conditionals,
        # no weapon gates -- and then ranked every armament in the game
        # against attributes the stat sheet next door disagreed with (QA-001).
        build = self.planner.current_build()
        self.attributes = build.attributes
        # The tier is handed over explicitly and there is no default that
        # could stand in for it: ranking an armament that sits in no slot at
        # a chosen target tier is this tab's question, and a default would
        # quietly put the slot's tier back (AD-020, point 1; QA-055).
        self.ratings = damage.rank_candidates(
            build, self.upgrade.value(), self.data,
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

        self._top_sections: list[Section] = []
        shown = 0
        shown += self._build_weapons(outer, predicate)
        shown += self._build_spells(outer, predicate, "Sorceries")
        shown += self._build_spells(outer, predicate, "Incantations")

        outer.addStretch()
        self.scroll.setWidget(root)
        # "14 shown" behind three collapsed headings still needed three
        # clicks per group to see anything, which made searching feel
        # broken. A modest result set opens itself; the cap keeps the lazy
        # sections doing their job when a search matches half the arsenal.
        if predicate is not None and 0 < shown <= 60:
            for section in self._top_sections:
                section.expand_all()
        # The attack-rating caveat is measured, not hedging: in the training
        # area the game's own panel reads about 60% of the computed figure,
        # and whether that scale applies on expeditions is still being
        # verified in play. Ratings still rank weapons correctly either way.
        self.summary.setText(
            f"{self.header_text}. {shown} shown. Attack rating is base damage "
            f"plus what your stats add to it. The in-game panel has been seen "
            f"showing about 60% of these figures (under investigation); the "
            f"ranking between weapons is unaffected. Spell damage is not in "
            f"the game's data, so spells show their costs instead."
        )

    def _build_weapons(self, outer, predicate) -> int:
        def effective_rarity(rating) -> int:
            """The rarity band the armament would carry at the tier it got.

            `damage.Rating.tier_applied` counts tiers from 1 and
            `weapon["rarity"]` counts bands from 0, so the band is one below
            the tier. The `min` is kept although `weapons.rate` already
            clamps the request to `MAX_UPGRADE`: that is the same pair of
            guards QA-068 is about, and neither may be dropped on the
            strength of the other alone.
            """
            return min(rating.tier_applied - 1, RARITY_TIERS - 1)

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
            if (wanted_rarity != -1
                    and effective_rarity(rating) != wanted_rarity):
                continue
            by_family.setdefault(weapon.get("family", "Other"), []).append(rating)

        total = sum(len(v) for v in by_family.values())

        # Infusion variants live as sibling rows in one id band -- Longsword
        # 2000000, Fire Longsword 2000500, Sacred 2000700 -- so the band is
        # the family and the lowest id in it is the standard version the
        # others are measured against.
        def band(rating):
            return rating.weapon["id"] // 10000

        standards: dict[int, dict] = {}
        for family_entries in by_family.values():
            for rating in family_entries:
                group = band(rating)
                if (group not in standards
                        or rating.weapon["id"] < standards[group]["id"]):
                    standards[group] = rating.weapon

        def scaling_text(values: dict) -> str:
            parts = [f"{stat[:3].upper()} {value:g}"
                     for stat, value in values.items() if value]
            return " · ".join(parts) if parts else "none"

        def build_family(entries):
            # Rarest first; inside a rarity band the infusions of one weapon
            # sit together, ordered by the standard version's name.
            entries = sorted(entries, key=lambda r: (
                -r.weapon.get("rarity", 0),
                standards[band(r)]["name"].lower(),
                r.weapon["id"],
            ))
            tiles = []
            for rating in entries:
                weapon = rating.weapon
                lines = [("AR", f"{rating.final_total:.0f}")]
                # `damage_type`, not `damage`: the loop variable used to
                # shadow the module of that name, and the resulting
                # UnboundLocalError only fired when a tile was drawn, never
                # on import (QA-072).
                for damage_type, value in rating.final_per_type.items():
                    lines.append((weapons.DAMAGE_LABELS[damage_type],
                                  f"{value:.0f}"))
                # The status the weapon exists for. Elemental variants always
                # showed their element; the status variants hid their one
                # number, so a Poison Cleaver read as a plain cleaver with
                # less damage.
                for status, value in sorted(
                        (weapon.get("inflicts") or {}).items()):
                    lines.append((f"{status} buildup", f"{value:g}"))
                scaling = weapon.get("scaling") or {}
                lines.append(("Scaling", scaling_text(scaling)))
                # An infusion that moves the scaling says by how much, against
                # the standard version of the same weapon.
                standard = standards.get(band(rating))
                if standard is not None and standard["id"] != weapon["id"]:
                    base_scaling = standard.get("scaling") or {}
                    shifts = []
                    for stat in scaling.keys() | base_scaling.keys():
                        delta = (scaling.get(stat, 0) or 0) - (
                            base_scaling.get(stat, 0) or 0)
                        if delta:
                            shifts.append(f"{stat[:3].upper()} {delta:+g}")
                    if shifts:
                        lines.append(("vs standard", " · ".join(shifts)))
                lines.append(("Rarity", RARITY_NAMES.get(weapon.get("rarity", 0), "?")))
                own_tier = weapon.get("rarity", 0) + 1
                reached = min(rating.tier_applied, weapons.MAX_UPGRADE)
                if rating.tier_applied > own_tier:
                    lines.append(("Upgraded to", f"+{reached} "
                                                 f"{RARITY_NAMES.get(reached - 1, '')}"))
                if rating.unmet:
                    need = " ".join(f"{s[:3].upper()} {n}"
                                    for s, (_h, n) in rating.unmet.items())
                    lines.append(("Requires", need))
                # Colour by the rarity the weapon would actually have at the
                # chosen upgrade target, not its shelf rarity.
                tiles.append(Tile(weapon["name"],
                                  self.icons.item(weapon.get("icon")),
                                  lines, dimmed=bool(rating.unmet),
                                  rarity=effective_rarity(rating)))
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

        section = Section(f"Weapons  ({total})", build_body)
        self._top_sections.append(section)
        outer.addWidget(section)
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
                # The game's caption, whitespace reflowed for a card. This is
                # the only place a spell says what it does.
                caption = " ".join((spell.get("caption") or "").split())
                tiles.append(Tile(spell["name"],
                                  self.icons.item(spell.get("icon")), lines,
                                  blurb=caption))
            return self._grid(tiles)

        def build_body():
            body = QWidget()
            inner = QVBoxLayout(body)
            inner.setContentsMargins(10, 0, 0, 0)
            inner.setSpacing(4)
            for family in sorted(by_family):
                entries = by_family[family]
                section = Section(
                    f"{family}  ({len(entries)})",
                    lambda e=entries: build_family(e),
                    level=1,
                )
                if family.startswith("Group "):
                    section.toggle.setToolTip(
                        "The game groups these spells together but names "
                        "the group nowhere, so the number is all there is "
                        "to show.")
                inner.addWidget(section)
            return body

        section = Section(f"{category}  ({total})", build_body)
        self._top_sections.append(section)
        outer.addWidget(section)
        return total
