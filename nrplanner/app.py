"""Nightreign Helper -- Nightfarer, chalice, relic slots, stat sheet."""

from __future__ import annotations

import sys

from PySide6.QtCore import QPoint, QSettings, QSize, Qt
from PySide6.QtGui import (
    QColor, QCursor, QFont, QIcon, QPainter, QPalette, QPixmap,
)
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QCompleter, QDialog, QFrame,
    QGridLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QLineEdit, QMainWindow, QMessageBox, QPushButton, QScrollArea, QSizePolicy,
    QSlider, QTabWidget, QToolButton, QToolTip, QVBoxLayout, QWidget,
)

from . import (datasource, effecttext, firstrun, inventory, model, search,
               weaponslots, weapons)
from .effectstab import EffectsTab
from .iconpack import IconPack
from .arsenaltab import ArsenalTab
from .bosstab import BossTab
from .datasource import load_data
from .deeptab import DeepTab
from .depthstab import DepthsTab
from .eventstab import WorldEventsTab

EFFECTS_PER_RELIC = 3
WHITE_SLOT = 4

# The four shared Grails sit under their own heroType rather than any
# Nightfarer's, because every Nightfarer can use them.
GRAIL_HERO_TYPE = 11

# Link target for the weapon attack-rating breakdown. Not a modifier field, so
# it is namespaced to keep it out of the way of the real ones.
AR_BREAKDOWN_KEY = "ar:total"

# Sentinel for the "build your own relic" entry in a slot's relic list.
CUSTOM_RELIC = object()

TILE_SIZE = 50
TILE_PAD = 6
VARIANT_STRIP = 46

ACCENT = "#c8a45c"
GOOD = "#6fbf73"
BAD = "#d1655f"
MUTED = "#8a8a8a"
PANEL = "#1e1f23"
BORDER = "#2e2f35"
CURSE = BAD   # curses are a cost, and read in the same colour as one

SLOT_COLOURS = {
    0: "#b4544e",   # Red
    1: "#4e7ab4",   # Blue
    2: "#c2a24a",   # Yellow
    3: "#5c9e63",   # Green
    4: "#d8d8d8",   # White -- wildcard
}


def _dark_palette() -> QPalette:
    p = QPalette()
    p.setColor(QPalette.Window, QColor("#16171a"))
    p.setColor(QPalette.WindowText, QColor("#e4e4e4"))
    p.setColor(QPalette.Base, QColor(PANEL))
    p.setColor(QPalette.AlternateBase, QColor("#26272c"))
    p.setColor(QPalette.Text, QColor("#e4e4e4"))
    p.setColor(QPalette.Button, QColor("#26272c"))
    p.setColor(QPalette.ButtonText, QColor("#e4e4e4"))
    p.setColor(QPalette.Highlight, QColor(ACCENT))
    p.setColor(QPalette.HighlightedText, QColor("#16171a"))
    return p


def _heading(text: str) -> QLabel:
    label = QLabel(text.upper())
    font = label.font()
    font.setPointSize(8)
    font.setBold(True)
    font.setLetterSpacing(QFont.AbsoluteSpacing, 1.2)
    label.setFont(font)
    label.setStyleSheet(f"color: {MUTED};")
    return label


class RelicSlot(QFrame):
    """One relic slot: a fixed colour from the chalice, up to three effects."""

    def __init__(self, index: int, deep: bool, on_change, icons=None,
                 on_search_changed=None):
        super().__init__()
        self.index = index
        self.deep = deep
        self.on_change = on_change
        self.icons = icons
        self.on_search_changed = on_search_changed or (lambda _text: None)
        self.search_text = ""
        self.owned = None
        self.colour = 0
        self.pool: list[dict] = []
        self.effect_by_id: dict[int, dict] = {}
        self.all_effects: list[dict] = []
        self.custom_item = None
        self.hero_name = ""

        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(
            f"QFrame {{ background: {PANEL}; border: 1px solid {BORDER};"
            f" border-radius: 6px; }}"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 10)
        layout.setSpacing(5)

        header = QHBoxLayout()
        self.title = QLabel()
        self.title.setStyleSheet("font-weight: bold; border: none;")
        header.addWidget(self.title)
        header.addStretch()
        self.chip = QLabel()
        self.chip.setFixedSize(14, 14)
        header.addWidget(self.chip)
        layout.addLayout(header)

        # A slot holds a relic you own, exactly as in game: the effects come
        # with the relic and cannot be mixed and matched. The combo is kept as
        # hidden state so the visible control can be a proper icon grid.
        self.relic_box = QComboBox()
        self.relic_box.setVisible(False)
        self.relic_box.currentIndexChanged.connect(self._on_relic_changed)
        layout.addWidget(self.relic_box)

        self.choose_button = QPushButton("Empty slot")
        self.choose_button.setStyleSheet("text-align: left; padding: 6px 8px;")
        self.choose_button.clicked.connect(self._open_picker)
        layout.addWidget(self.choose_button)

        self.rolled_label = QLabel()
        self.rolled_label.setWordWrap(True)
        self.rolled_label.setStyleSheet("border: none;")
        layout.addWidget(self.rolled_label)

    # -- state -----------------------------------------------------------
    def _on_relic_changed(self, *_args) -> None:
        self._sync_mode()
        self.on_change()

    def _open_picker(self) -> None:
        from .relicpicker import RelicPicker

        dialog = RelicPicker(
            self, self.icons, self.search_text, self.on_search_changed
        )
        if dialog.exec() and dialog.chosen is not None:
            index = self.relic_box.findData(dialog.chosen)
            if index >= 0:
                self.relic_box.setCurrentIndex(index)
        elif dialog.chosen is None and dialog.result():
            self.relic_box.setCurrentIndex(0)

    def _sync_mode(self) -> None:
        """Show the rolled effects of the relic currently in this slot."""
        item = self.relic_box.currentData()
        self.choose_button.setText(item.name if item is not None else "Empty slot")
        if item is None:
            self.rolled_label.setVisible(False)
            self.rolled_label.clear()
            return

        lines = []
        for eid in item.effect_ids:
            eff = self.effect_by_id.get(eid)
            name = effecttext.name(eff) if eff else f"<{eid}>"
            mark = "" if not eff or eff["stacks"] else "  ⚠"
            colour = "#d1655f" if eff and eff.get("is_curse") else "#cfcfcf"
            # An effect belonging to another Nightfarer is doing nothing at
            # all here. Say so on the slot rather than letting it sit among
            # the working rolls looking identical to them.
            if eff is not None and not effecttext.works_for(eff, self.hero_name):
                who = effecttext.owner(eff) or "another Nightfarer"
                lines.append(
                    f"<div style='color:{CURSE}'>&bull; <s>{name}</s>"
                    f" — not working ({who} only)</div>"
                )
                continue
            lines.append(f"<div style='color:{colour}'>&bull; {name}{mark}</div>")
        if not lines:
            lines = ["<div style='color:#8a8a8a'>no rolled effects</div>"]
        lines.extend(self.curse_lines(item))
        self.rolled_label.setText("".join(lines))
        self.rolled_label.setToolTip(self.curse_tooltip(item))
        self.rolled_label.setVisible(True)

    def curse_lines(self, item) -> list[str]:
        """The curses this relic actually carries, named rather than hinted at.

        A relic that came out of the save knows exactly which curses it rolled,
        so say so. One that does not -- a template the player has never picked
        up -- can only report that it has curse slots at all.
        """
        curse_ids = list(getattr(item, "curse_ids", ()) or ())
        if curse_ids:
            out = []
            for cid in curse_ids:
                eff = self.effect_by_id.get(cid)
                name = effecttext.name(eff) if eff else f"<{cid}>"
                out.append(f"<div style='color:{CURSE}'>✦ {name}</div>")
            return out
        if getattr(item, "has_curse", False):
            count = getattr(item, "curse_count", 0) or 0
            what = f"{count} curses" if count > 1 else "a curse"
            return [f"<div style='color:{CURSE}'>✦ comes with {what}</div>"]
        return []

    def curse_tooltip(self, item) -> str:
        """Full wording for each curse, so the cost is legible not cryptic."""
        curse_ids = list(getattr(item, "curse_ids", ()) or ())
        if not curse_ids:
            return ""
        parts = ["This relic's curses:"]
        for cid in curse_ids:
            eff = self.effect_by_id.get(cid)
            if eff is None:
                parts.append(f"  • <{cid}>")
                continue
            parts.append(f"  • {effecttext.name(eff)}")
            parts.append(f"      {effecttext.describe_full(eff)}")
        return "\n".join(parts)

    def _chance_suffix(self, effect: dict, colour: int) -> str:
        """Roll chance for this exact slot: its colour and its mode.

        Normal and Deep of Night relics draw from different pools, and the slot
        knows which it is, so only the matching pools are considered.
        """
        chance = effect.get("deep_chance" if self.deep else "chance", {})
        if colour == WHITE_SLOT:
            # A White slot accepts any colour, so every colour's pools count.
            entries = list(chance.values())
        else:
            entry = chance.get(str(colour))
            entries = [entry] if entry else []
        if not entries:
            return ""

        avg = sum(e["avg"] for e in entries) / len(entries)
        best = max(e["max"] for e in entries)
        fmt = (lambda v: f"{v * 100:.2f}%") if best < 0.01 else (lambda v: f"{v * 100:.1f}%")
        chance = fmt(avg) if abs(best - avg) < 1e-9 else f"{fmt(avg)}–{fmt(best)}"

        curse = effect.get("curse", "never")
        mark = "  ✦ cursed" if curse == "always" else "  ✦?" if curse == "sometimes" else ""
        return f"   [{chance}]{mark}"

    def set_colour(self, colour: int, all_effects: list[dict], owned=None,
                   effect_filter: str = "", hero_name: str = "") -> None:
        self.hero_name = hero_name or self.hero_name
        self.colour = colour
        self.owned = owned
        self.all_effects = list(all_effects)
        self.effect_by_id = {e["id"]: e for e in all_effects}
        # A custom relic is built for one slot colour; changing the colour
        # invalidates it rather than silently leaving an illegal relic in place.
        self.custom_item = None
        self.chip.setStyleSheet(
            f"background: {SLOT_COLOURS.get(colour, '#888')};"
            f" border: 1px solid {BORDER}; border-radius: 7px;"
        )
        self.populate(effect_filter)

    def effect_names(self, item) -> list[str]:
        return [
            effecttext.name(self.effect_by_id.get(e) or {"name": f"<{e}>"})
            for e in item.effect_ids
        ]

    def rollable_effects(self) -> list[dict]:
        """Effects that can legitimately appear on a relic in this slot.

        Drawn from what the game says can roll in this colour and mode, not
        from what the player happens to own -- the whole point of a custom
        relic is to plan around one they have not found yet. A White slot
        takes any colour, so it accepts everything.
        """
        key = "deep_colours" if self.deep else "colours"
        out = []
        for eff in self.all_effects:
            colours = eff.get(key) or []
            if not colours:
                continue
            if self.colour == WHITE_SLOT or self.colour in colours:
                out.append(eff)
        return sorted(out, key=effecttext.name)

    def set_custom(self, effect_ids: list[int]) -> None:
        """Put a made-up relic in this slot, or clear it when given nothing."""
        if not effect_ids:
            self.custom_item = None
        else:
            self.custom_item = inventory.OwnedItem(
                relic_id=inventory.CUSTOM_RELIC_ID,
                name="Custom relic",
                colour=self.colour,
                effect_ids=list(effect_ids),
                is_deep=self.deep,
            )
        self.populate(self.search_text)
        if self.custom_item is not None:
            index = self.relic_box.findData(self.custom_item)
            if index >= 0:
                self.relic_box.setCurrentIndex(index)
        self.on_change()

    def populate(self, effect_filter: str = "") -> None:
        """List the relics the player owns that fit this slot.

        A search term keeps only relics carrying a matching effect, which
        answers "which of my relics has this?" -- the effects themselves are
        fixed to the relic, exactly as in game.
        """
        self.search_text = effect_filter
        predicate = search.parse(effect_filter)
        items = []
        if self.owned is not None:
            items = self.owned.relics_for(self.colour, self.deep, WHITE_SLOT)
        if predicate is not None:
            items = [i for i in items if predicate(self.effect_names(i))]

        previous = self.relic_box.currentData()
        self.relic_box.blockSignals(True)
        self.relic_box.clear()
        self.relic_box.addItem("Empty slot", None)
        # A custom relic is not owned, so it survives repopulation only by
        # being re-added here; it ignores the effect filter deliberately, so
        # searching cannot make the relic you just built disappear.
        if self.custom_item is not None:
            summary = ", ".join(self.effect_names(self.custom_item))
            self.relic_box.addItem(
                f"Custom relic — {summary}"[:120], self.custom_item)
        for item in items:
            summary = ", ".join(self.effect_names(item))
            label = f"{item.name} — {summary}" if summary else item.name
            self.relic_box.addItem(label[:120], item)
        if previous is not None:
            idx = self.relic_box.findData(previous)
            if idx >= 0:
                self.relic_box.setCurrentIndex(idx)
        self.relic_box.blockSignals(False)

        suffix = f"{len(items)} match" if predicate else f"{len(items)} owned"
        self.title.setText(
            f"{'Deep ' if self.deep else ''}Slot {self.index + 1} — "
            f"{model.COLOUR_NAMES.get(self.colour, self.colour)}  ({suffix})"
        )
        self._sync_mode()

    def selected_ids(self) -> list[int]:
        item = self.relic_box.currentData()
        return list(item.effect_ids) if item is not None else []

    def select_handle(self, handle: int | None) -> bool:
        """Put the relic with this save handle in the slot, or empty it.

        Matching on the handle rather than the name matters: several copies of
        one relic can be owned with different rolls, and this save equips the
        second copy of The Wylder's Earring while the first sits unused.

        Signals are held back so importing six slots recomputes the build once
        at the end rather than six times.
        """
        self.relic_box.blockSignals(True)
        try:
            if handle is None:
                self.relic_box.setCurrentIndex(0)
                return True
            for i in range(self.relic_box.count()):
                item = self.relic_box.itemData(i)
                if item is not None and getattr(item, "handle", None) == handle:
                    self.relic_box.setCurrentIndex(i)
                    return True
            return False
        finally:
            self.relic_box.blockSignals(False)
            self._sync_mode()


class VariantDialog(QDialog):
    """Artwork picker: the current image, with the alternatives beneath it."""

    PREVIEW = 200

    def __init__(self, tile: "HeroTile"):
        super().__init__(tile.window())
        self.tile = tile
        self.setWindowTitle(tile.hero["name"])
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setFixedSize(self.PREVIEW, self.PREVIEW)
        layout.addWidget(self.preview, 0, Qt.AlignHCenter)

        row = QHBoxLayout()
        row.setSpacing(8)

        choices = [(None, tile.icons.portrait(tile.hero["id"]))]
        choices += [(v["id"], tile.icons.variant(v["id"]))
                    for v in tile.icons.variants(tile.hero["id"])]

        for texture_id, pixmap in choices:
            if pixmap is None:
                continue
            button = QToolButton()
            button.setToolButtonStyle(Qt.ToolButtonIconOnly)
            button.setIconSize(QSize(self.PREVIEW, self.PREVIEW))
            button.setFixedSize(self.PREVIEW + 8, self.PREVIEW + 8)
            button.setAutoRaise(True)
            button.setCheckable(True)
            button.setChecked(texture_id == tile.variant_id)
            button.setIcon(QIcon(pixmap))
            button.clicked.connect(
                lambda _checked=False, tid=texture_id: self._choose(tid)
            )
            row.addWidget(button)

        if row.count() == 0:
            row.addWidget(QLabel("No artwork available for this Nightfarer."))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        holder = QWidget()
        holder.setLayout(row)
        scroll.setWidget(holder)
        scroll.setFixedHeight(self.PREVIEW + 30)
        layout.addWidget(scroll)

        self._refresh_preview()

    def _refresh_preview(self) -> None:
        pixmap = self.tile.current_pixmap()
        if pixmap is not None:
            self.preview.setPixmap(
                pixmap.scaled(self.PREVIEW, self.PREVIEW,
                              Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )

    def _choose(self, texture_id) -> None:
        self.tile.set_variant(texture_id)
        self._refresh_preview()
        self.accept()


class HeroTile(QToolButton):
    """One portrait in the 2x5 Nightfarer grid.

    Left click selects the Nightfarer; right click offers that character's
    alternate illustrations so the tile can show a preferred one.
    """

    def __init__(self, index: int, hero: dict, icons):
        super().__init__()
        self.index = index
        self.hero = hero
        self.icons = icons
        self.variant_id: int | None = None

        self.setCheckable(True)
        self.setAutoRaise(True)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.setIconSize(QSize(TILE_SIZE, TILE_SIZE))
        self.setFixedSize(TILE_SIZE + TILE_PAD, TILE_SIZE + TILE_PAD)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # A visible frame keeps neighbouring portraits from reading as one
        # continuous image, since the artwork itself has no margin.
        self.setStyleSheet(
            f"QToolButton {{ border: 1px solid {BORDER}; border-radius: 4px;"
            f" background: {PANEL}; padding: 0px; }}"
            f"QToolButton:checked {{ border: 2px solid {ACCENT}; }}"
        )
        self.setToolTip(f"{hero['name']}\nRight-click to change the artwork")
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_variants)
        self._apply_image()

    def current_pixmap(self):
        if self.variant_id is not None:
            pixmap = self.icons.variant(self.variant_id)
            if pixmap is not None:
                return pixmap
        return self.icons.portrait(self.hero["id"])

    def _apply_image(self) -> None:
        pixmap = self.current_pixmap()
        if pixmap is not None:
            self.setIcon(QIcon(pixmap))
        else:
            # No artwork for this Nightfarer: the DLC characters' assets live
            # in dlc01, whose archive key is not published. Draw initials so
            # the tile keeps the exact same footprint as the others.
            self.setIcon(QIcon(self._placeholder()))

    def _placeholder(self) -> QPixmap:
        pixmap = QPixmap(TILE_SIZE, TILE_SIZE)
        pixmap.fill(QColor("#26272c"))
        painter = QPainter(pixmap)
        painter.setPen(QColor(MUTED))
        font = painter.font()
        font.setPointSize(18)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, self.hero["name"][:2])
        painter.end()
        return pixmap

    def _show_variants(self, _point) -> None:
        # Handled by the window, which shows the strip inside the sidebar.
        window = self.window()
        if hasattr(window, "show_variant_strip"):
            window.show_variant_strip(self)

    def set_variant(self, texture_id: int | None) -> None:
        self.variant_id = texture_id
        self._apply_image()
        settings = QSettings("DankYeeter", "NightreignHelper")
        settings.setValue(f"variant/{self.hero['id']}", texture_id if texture_id else "")

    def restore_variant(self) -> None:
        settings = QSettings("DankYeeter", "NightreignHelper")
        stored = settings.value(f"variant/{self.hero['id']}", "")
        if stored:
            self.variant_id = int(stored)
            self._apply_image()


class Planner(QMainWindow):
    def __init__(self, data: dict):
        super().__init__()
        self.data = data
        self.effects = data["effects"]
        self.effect_list = list(self.effects.values())
        self.heroes = data["heroes"]
        self.vessels = data["vessels"]
        self.curves = data.get("curves", {})
        self.icons = IconPack()
        self.hero_index = 0
        # The six armament tiles, and one saved set per Nightfarer. Slot 1
        # defaults to that Nightfarer's starting armament, but anything you
        # build is kept for the rest of the session, so switching Nightfarer
        # and back does not undo it. Not persisted to disk -- it lasts the run
        # of the program, no longer.
        self.weapon_slots: list[weaponslots.WeaponSlot] = [
            weaponslots.WeaponSlot() for _ in range(weaponslots.SLOT_COUNT)
        ]
        self.weapon_loadouts: dict[int, list[weaponslots.WeaponSlot]] = {}
        # Which tile the damage breakdown describes.
        self.active_weapon = 0

        # The data version is a build number off the game install. It means
        # nothing to a player and ate half the title bar, so the title just
        # names the tool. Only a re-read after a patch is worth saying, and it
        # is said in words rather than as a version id.
        stale = data.get("meta", {}).get("regenerated")
        self.setWindowTitle(
            "Nightreign Helper"
            + ("  —  updated for your installed game version" if stale else "")
        )
        self.resize(1320, 860)

        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        planner = QWidget()
        root = QHBoxLayout(planner)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(14)
        root.addWidget(self._build_left(), 0)
        root.addWidget(self._build_middle(), 1)
        root.addWidget(self._build_right(), 0)

        tabs.addTab(planner, "Build planner")
        self.effects_tab = EffectsTab(data)
        tabs.addTab(self.effects_tab, "Effects && chances")

        self.owned = None
        self.rescan_save(initial=True)
        self.select_hero(0)

        self.weapons_tab = ArsenalTab(data, self, self.icons)
        tabs.addTab(self.weapons_tab, "Weapons && spells")
        # Recalculate when the weapons tab comes to the front, so it always
        # reflects the build currently set up on the planner tab.
        tabs.currentChanged.connect(
            lambda index: self.weapons_tab.recalculate()
            if tabs.widget(index) is self.weapons_tab else None
        )

        # Reference tabs. None of these depend on the build, so they are built
        # once and never recalculated. They are skipped entirely when the
        # snapshot predates them rather than showing three empty tabs.
        if data.get("bosses"):
            self.boss_tab = BossTab(data, self.icons)
            tabs.addTab(self.boss_tab, "Nightlords")
        if data.get("deep_of_night"):
            self.deep_tab = DeepTab(data)
            tabs.addTab(self.deep_tab, "Deep of Night")
            self.depths_tab = DepthsTab(data)
            tabs.addTab(self.depths_tab, "Depth weighting")
        if (data.get("world_events") or {}).get("events"):
            self.events_tab = WorldEventsTab(data)
            tabs.addTab(self.events_tab, "World Events")

    # -- panels ----------------------------------------------------------
    def _build_left(self) -> QWidget:
        panel = QWidget()
        panel.setFixedWidth(250)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(_heading("Nightfarer"))
        grid = QGridLayout()
        grid.setSpacing(4)
        self.hero_tiles: list[HeroTile] = []
        for i, hero in enumerate(self.heroes):
            tile = HeroTile(i, hero, self.icons)
            tile.restore_variant()
            tile.clicked.connect(
                lambda _checked=False, index=i: self.select_hero(index)
            )
            self.hero_tiles.append(tile)
            grid.addWidget(tile, i // 5, i % 5)
        layout.addLayout(grid)

        # Artwork chooser lives inside the sidebar rather than in its own
        # window, and stays hidden until a portrait is right-clicked.
        self.variant_panel = QFrame()
        self.variant_panel.setVisible(False)
        self.variant_panel.setStyleSheet(
            f"QFrame {{ background: {PANEL}; border: 1px solid {BORDER};"
            f" border-radius: 5px; }}"
        )
        strip_outer = QVBoxLayout(self.variant_panel)
        strip_outer.setContentsMargins(6, 5, 6, 6)
        strip_outer.setSpacing(4)

        self.variant_title = QLabel()
        self.variant_title.setStyleSheet(
            f"border: none; color: {MUTED}; font-size: 10px;"
        )
        strip_outer.addWidget(self.variant_title)

        # A grid, not a row. Seven variants at 50px need 374px of width and
        # the sidebar has about 250, so a single row was being squeezed until
        # the tiles overlapped each other. Wrapping keeps every tile its full
        # size however many there are.
        self.variant_row = QGridLayout()
        self.variant_row.setSpacing(4)
        self.variant_row.setContentsMargins(0, 0, 0, 0)
        strip_outer.addLayout(self.variant_row)
        layout.addWidget(self.variant_panel)

        self.hero_name_label = QLabel()
        self.hero_name_label.setAlignment(Qt.AlignCenter)
        self.hero_name_label.setStyleSheet(
            f"color: {ACCENT}; font-size: 14px; font-weight: bold;"
        )
        layout.addWidget(self.hero_name_label)

        layout.addSpacing(8)
        # "Chalice" named the section and also one of the seven things in it,
        # next to Urns and Goblets. "Vessel" is the category; a Chalice is one
        # kind of vessel.
        layout.addWidget(_heading("Vessel"))
        self.chalice_list = QListWidget()
        self.chalice_list.setIconSize(QSize(34, 34))
        self.chalice_list.currentRowChanged.connect(lambda *_: self.apply_chalice())
        layout.addWidget(self.chalice_list, 1)

        self.deep_check = QCheckBox("Deep of Night (3 extra slots)")
        self.deep_check.toggled.connect(lambda *_: self.apply_chalice())
        layout.addWidget(self.deep_check)

        layout.addSpacing(6)
        row = QHBoxLayout()
        self.rescan_button = QPushButton("Rescan save")
        self.rescan_button.clicked.connect(self.rescan_save)
        row.addWidget(self.rescan_button)
        self.import_button = QPushButton("Load equipped")
        self.import_button.setToolTip(
            "Load this Nightfarer's equipped vessel and relics from the save"
        )
        self.import_button.clicked.connect(self.load_equipped)
        row.addWidget(self.import_button)
        layout.addLayout(row)

        self.owned_label = QLabel()
        self.owned_label.setWordWrap(True)
        self.owned_label.setStyleSheet(f"color: {MUTED}; font-size: 10px;")
        layout.addWidget(self.owned_label)

        layout.addSpacing(8)
        layout.addWidget(_heading("Level"))
        self.level_label = QLabel()
        self.level_label.setStyleSheet(
            f"color: {ACCENT}; font-size: 17px; font-weight: bold;"
        )
        layout.addWidget(self.level_label)
        self.level_slider = QSlider(Qt.Horizontal)
        self.level_slider.setMinimum(1)
        self.level_slider.setMaximum(15)
        self.level_slider.setTickPosition(QSlider.TicksBelow)
        self.level_slider.valueChanged.connect(lambda *_: self.recompute())
        layout.addWidget(self.level_slider)
        self.level_note = QLabel()
        self.level_note.setWordWrap(True)
        self.level_note.setStyleSheet(f"color: {MUTED}; font-size: 10px;")
        layout.addWidget(self.level_note)
        return panel

    def _build_middle(self) -> QWidget:
        outer = QScrollArea()
        outer.setWidgetResizable(True)
        outer.setFrameShape(QFrame.NoFrame)

        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 6, 0)
        layout.addWidget(_heading("Relic slots"))

        # No search box here. A single filter across every slot narrowed each
        # slot's own list, so a relic already chosen could stop matching and be
        # dropped out from under you -- relics would not stay put. Filtering
        # belongs to the picker, where it narrows the grid you are choosing
        # from and cannot disturb what is already equipped. The picker keeps
        # its own box, and the term carries from one opening to the next.
        hint = QLabel("Open a slot to choose a relic — the picker has its own "
                      "filter, supporting AND, OR, NOT and \"quoted phrases\".")
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        layout.addWidget(hint)

        self.base_slots = [
            RelicSlot(i, False, self.recompute, self.icons, self._set_search)
            for i in range(3)
        ]
        for slot in self.base_slots:
            layout.addWidget(slot)

        self.deep_heading = _heading("Deep of Night slots")
        layout.addWidget(self.deep_heading)
        self.deep_slots = [
            RelicSlot(i, True, self.recompute, self.icons, self._set_search)
            for i in range(3)
        ]
        for slot in self.deep_slots:
            layout.addWidget(slot)

        layout.addStretch()
        outer.setWidget(panel)
        return outer

    def _build_right(self) -> QWidget:
        # The whole sheet scrolls. With six relics equipped the conditional and
        # curse sections alone can outrun the window, and content was simply
        # falling off the bottom with no way to reach it.
        outer = QScrollArea()
        outer.setFixedWidth(348)
        outer.setWidgetResizable(True)
        outer.setFrameShape(QFrame.NoFrame)
        outer.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 8, 0)

        layout.addWidget(_heading("Base stats"))
        self.derived_grid = QGridLayout()
        self.derived_grid.setHorizontalSpacing(10)
        self.derived_grid.setVerticalSpacing(4)
        layout.addLayout(self.derived_grid)

        layout.addSpacing(12)
        layout.addWidget(_heading("Attributes"))
        self.attr_grid = QGridLayout()
        self.attr_grid.setHorizontalSpacing(10)
        self.attr_grid.setVerticalSpacing(4)
        layout.addLayout(self.attr_grid)

        layout.addSpacing(12)
        layout.addWidget(_heading("Weapon damage"))
        # Six armament tiles, 3x2. Slot 1 starts as this Nightfarer's own
        # starting armament -- CharaInitParam rows 90000-90009, agreed by three
        # other row families (see verify_starting_weapons.py). Every tile's
        # rolled effects count towards the sheet; the active one, ringed in
        # gold, is the one the damage breakdown below describes.
        # Single-click activates, double-click edits, right-click empties.
        grid = QGridLayout()
        grid.setHorizontalSpacing(6)
        grid.setVerticalSpacing(6)
        self.weapon_tiles = []
        for index in range(weaponslots.SLOT_COUNT):
            tile = weaponslots.WeaponTile(
                index, self._edit_weapon_slot, self._clear_weapon_slot,
                self._activate_weapon_slot,
            )
            self.weapon_tiles.append(tile)
            grid.addWidget(tile, index // weaponslots.SLOT_COLUMNS,
                           index % weaponslots.SLOT_COLUMNS)
        layout.addLayout(grid)
        self.apply_hero_weapon()

        self.ar_label = QLabel()
        self.ar_label.setWordWrap(True)
        self.ar_label.linkActivated.connect(self._show_breakdown)
        layout.addWidget(self.ar_label)

        layout.addSpacing(12)
        layout.addWidget(_heading("Resistances"))
        self.resist_label = QLabel()
        self.resist_label.setWordWrap(True)
        layout.addWidget(self.resist_label)

        layout.addSpacing(12)
        layout.addWidget(_heading("Multipliers"))
        self.rates_label = QLabel()
        self.rates_label.setWordWrap(True)
        self.rates_label.linkActivated.connect(self._show_breakdown)
        layout.addWidget(self.rates_label)

        layout.addSpacing(12)
        self.qual_heading = _heading("Conditional &amp; situational")
        # Pinned to rich text: the count carries markup only when something is
        # not working, and without this the plain case printed "&amp;" raw.
        self.qual_heading.setTextFormat(Qt.RichText)
        layout.addWidget(self.qual_heading)
        self.qual_label = QLabel()
        self.qual_label.setWordWrap(True)
        layout.addWidget(self.qual_label)

        layout.addSpacing(12)
        self.other_heading = _heading("Flat bonuses")
        layout.addWidget(self.other_heading)
        self.other_label = QLabel()
        self.other_label.setWordWrap(True)
        self.other_label.linkActivated.connect(self._show_breakdown)
        layout.addWidget(self.other_label)

        layout.addSpacing(12)
        layout.addWidget(_heading("Curses"))
        self.curse_label = QLabel()
        self.curse_label.setWordWrap(True)
        layout.addWidget(self.curse_label)

        layout.addSpacing(12)
        layout.addWidget(_heading("Stacking"))
        self.warn_label = QLabel()
        self.warn_label.setWordWrap(True)
        self.warn_label.setAlignment(Qt.AlignTop)
        layout.addWidget(self.warn_label)

        layout.addStretch(1)
        outer.setWidget(panel)
        return outer

    # -- logic -----------------------------------------------------------
    def current_hero(self) -> dict:
        return self.heroes[self.hero_index]

    def select_hero(self, index: int) -> None:
        self.hero_index = index
        for i, tile in enumerate(self.hero_tiles):
            tile.setChecked(i == index)
        self.hero_name_label.setText(self.heroes[index]["name"])
        self.apply_hero_weapon()
        self.reload_chalices()

    # -- armament tiles ---------------------------------------------------
    def weapon_by_id(self, weapon_id: int) -> dict | None:
        return next((w for w in self.data["weapons"] if w["id"] == weapon_id),
                    None)

    def active_slot(self) -> weaponslots.WeaponSlot:
        return self.weapon_slots[self.active_weapon]

    def equipped_weapons(self) -> list[dict]:
        return [s.weapon for s in self.weapon_slots if s.filled]

    def weapon_effects(self) -> list[dict]:
        """Rolled effects from every armament on the grid, not just the active
        one. A weapon's passive is not switched off by holding something else;
        the ones that genuinely need the weapon in hand carry their own gate
        and land under Conditional & situational."""
        out = []
        for slot in self.weapon_slots:
            for effect_id in slot.effect_ids:
                effect = self.effects.get(str(effect_id))
                if effect is not None:
                    out.append(effect)
        return out

    def _store_weapon_loadout(self) -> None:
        self.weapon_loadouts[self.current_hero()["id"]] = [
            s.copy() for s in self.weapon_slots
        ]

    def _activate_weapon_slot(self, index: int) -> None:
        self.active_weapon = index
        self.recompute()

    def _clear_weapon_slot(self, index: int) -> None:
        self.weapon_slots[index] = weaponslots.WeaponSlot()
        self._store_weapon_loadout()
        self.recompute()

    def _edit_weapon_slot(self, index: int) -> None:
        dialog = weaponslots.WeaponDialog(
            self, self.data, self.weapon_slots[index], self.icons)
        if dialog.exec():
            self.weapon_slots[index] = dialog.result_slot()
            self._store_weapon_loadout()
        self.recompute()

    def apply_hero_weapon(self) -> None:
        """Load this Nightfarer's tiles: what was built earlier this session,
        or slot 1 seeded with their own starting armament."""
        if not hasattr(self, "weapon_tiles"):
            return                      # called before the panel exists
        hero = self.current_hero()
        saved = self.weapon_loadouts.get(hero["id"])
        if saved is not None:
            self.weapon_slots = [s.copy() for s in saved]
        else:
            self.weapon_slots = [weaponslots.WeaponSlot()
                                 for _ in range(weaponslots.SLOT_COUNT)]
            starting = self.weapon_by_id(hero.get("starting_weapon", -1))
            if starting is not None:
                self.weapon_slots[0] = weaponslots.WeaponSlot(weapon=starting)
        self.active_weapon = 0

    def reload_chalices(self) -> None:
        hero = self.current_hero()
        self.chalice_list.blockSignals(True)
        self.chalice_list.clear()
        # A Nightfarer's own vessels, then the four shared Grails. The Grails
        # belong to every Nightfarer, which the save confirms: each one stores
        # its own arrangement of all four.
        own = [v for v in self.vessels if v["hero_type"] == hero["id"]]
        grails = [v for v in self.vessels if v["hero_type"] == GRAIL_HERO_TYPE]
        self.hero_vessels = own + grails

        def add_separator(text: str) -> None:
            """A caption row. Selecting it would mean nothing, so it cannot be
            picked -- without it the four shared Grails read as four more of
            this Nightfarer's own vessels, and the list looks twice as long as
            the Nightfarer actually has."""
            item = QListWidgetItem(text)
            item.setFlags(Qt.NoItemFlags)
            item.setForeground(QColor(MUTED))
            self.chalice_list.addItem(item)

        first_row = None
        for group, vessels in ((f"{hero['name']}'s own", own),
                               ("Shared Grails — any Nightfarer", grails)):
            if not vessels:
                continue
            add_separator(group)
            for vessel in vessels:
                item = QListWidgetItem(vessel["name"])
                item.setData(Qt.UserRole, vessel)
                icon = self.icons.item_icon(vessel.get("icon"))
                if icon is not None:
                    item.setIcon(icon)
                slots = " ".join(
                    model.COLOUR_NAMES.get(c, "?")[0] for c in vessel["slots"]
                )
                item.setToolTip(f"{vessel['name']} — slots {slots}")
                self.chalice_list.addItem(item)
                if first_row is None:
                    first_row = self.chalice_list.count() - 1
        self.chalice_list.blockSignals(False)
        if first_row is not None:
            self.chalice_list.setCurrentRow(first_row)
        self.apply_chalice()

    def current_vessel(self) -> dict | None:
        """The vessel selected in the list, ignoring the caption rows."""
        item = self.chalice_list.currentItem()
        vessel = item.data(Qt.UserRole) if item is not None else None
        if vessel is None:
            vessel = self.hero_vessels[0] if self.hero_vessels else None
        return vessel

    def apply_chalice(self) -> None:
        if not self.hero_vessels:
            return
        vessel = self.current_vessel()
        if vessel is None:
            return
        deep_on = self.deep_check.isChecked()

        owned = self.owned
        # Slots always list everything they can hold. Narrowing them from
        # outside is what made an equipped relic disappear.
        for i, slot in enumerate(self.base_slots):
            slot.set_colour(vessel["slots"][i], self.effect_list, owned, "",
                            hero_name=self.current_hero()["name"])
        for i, slot in enumerate(self.deep_slots):
            slot.set_colour(vessel["deep_slots"][i], self.effect_list, owned,
                            "", hero_name=self.current_hero()["name"])
            slot.setVisible(deep_on)
        self.deep_heading.setVisible(deep_on)

        self.recompute()

    def show_variant_strip(self, tile) -> None:
        """Inline artwork chooser for one Nightfarer, inside the sidebar."""
        while self.variant_row.count():
            item = self.variant_row.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
                item.widget().deleteLater()

        choices = [(None, self.icons.portrait(tile.hero["id"]))]
        choices += [(v["id"], self.icons.variant(v["id"]))
                    for v in self.icons.variants(tile.hero["id"])]
        choices = [(tid, pix) for tid, pix in choices if pix is not None]

        if not choices:
            self.variant_title.setText(f"{tile.hero['name']} — no artwork")
            self.variant_panel.setVisible(True)
            return

        self.variant_title.setText(f"{tile.hero['name']} — pick artwork")
        # How many fit across the panel at full size, never fewer than one.
        available = max(self.variant_panel.width() - 16, VARIANT_STRIP + 4)
        per_row = max(1, available // (VARIANT_STRIP + 4 + 4))
        for index, (texture_id, pixmap) in enumerate(choices):
            button = QToolButton()
            button.setIconSize(QSize(VARIANT_STRIP, VARIANT_STRIP))
            button.setFixedSize(VARIANT_STRIP + 4, VARIANT_STRIP + 4)
            button.setCheckable(True)
            button.setChecked(texture_id == tile.variant_id)
            button.setIcon(QIcon(pixmap))
            button.setStyleSheet(
                f"QToolButton {{ border: 1px solid {BORDER}; border-radius: 3px; }}"
                f"QToolButton:checked {{ border: 2px solid {ACCENT}; }}"
            )
            button.clicked.connect(
                lambda _c=False, t=tile, tid=texture_id: self._apply_variant(t, tid)
            )
            self.variant_row.addWidget(button, index // per_row, index % per_row)
        self.variant_row.setColumnStretch(per_row, 1)
        self.variant_panel.setVisible(True)

    def _apply_variant(self, tile, texture_id) -> None:
        tile.set_variant(texture_id)
        self.variant_panel.setVisible(False)

    def _set_search(self, text: str) -> None:
        """Remember the picker's filter so the next slot opens with it.

        Deliberately does not re-filter the slots themselves -- that is what
        used to drop an equipped relic when it stopped matching.
        """
        self.last_search = text
        for slot in self.base_slots + self.deep_slots:
            slot.search_text = text

    # Populated by recompute(), read by the click-to-break-down popup.
    last_sources: dict = {}
    last_rates: dict = {}

    # Which build.rates multiplier applies to which damage type. Attack rates
    # scale the finished number, so they belong in the comparison as much as
    # the attribute changes do -- a relic granting Physical Attack +12% moves
    # the damage without moving a single stat.
    #
    # Two families do this, and both belong here. `*AttackRate` is the general
    # buff, carried by 213-216 effects. `*AttackPowerRate` is carried by
    # exactly three -- the "Starting armament inflicts frost / poison / blood
    # loss" relics, each x0.85 -- and it is the price the game charges for the
    # status: the weapon inflicts a status and hits 15% softer for it. Leaving
    # it out meant equipping one of those relics moved the weapon damage not at
    # all, when it should drop it by 15%.
    #
    # Deliberately NOT here, having checked every attack multiplier in the
    # data: saAttackPowerRate and staminaAttackRate are stance and guard
    # damage rather than attack rating, guardCounterAttackRate applies only to
    # a guard counter, and characterSkillAttackRate only to Duchess' skill.
    # None of the four scales an ordinary hit.
    AR_RATE_FOR = {
        "Physics": ("physicsAttackRate", "physicsAttackPowerRate"),
        "Magic": ("magicAttackRate", "magicAttackPowerRate"),
        "Fire": ("fireAttackRate", "fireAttackPowerRate"),
        "Thunder": ("thunderAttackRate", "thunderAttackPowerRate"),
        "Dark": ("darkAttackRate", "darkAttackPowerRate"),
    }

    def _show_breakdown(self, key: str) -> None:
        """Which buffs make up one figure, shown beside the number clicked.

        A single "+12.4%" hides how many relics contributed and how much each
        one gave, which is exactly what you need when deciding whether one is
        worth a slot.
        """
        if key == AR_BREAKDOWN_KEY:
            self._show_ar_breakdown()
            return

        # An "All damage" row stands for five fields; its sources live under
        # the real one behind it.
        entries = self.last_sources.get(model.real_field(key), [])
        label = model.label_for(key)
        if not entries:
            QToolTip.showText(QCursor.pos(),
                              f"{label}\nno contributing effects recorded")
            return

        multiplicative = model.real_field(key) in self.last_rates
        rows = [f"<b>{label}</b>"]
        for name, value in entries:
            if multiplicative:
                shown = f"{(value - 1.0) * 100:+.1f}%"
            else:
                shown = f"{value:+g}"
            rows.append(f"&nbsp;&nbsp;{name} &nbsp; <b>{shown}</b>")

        if multiplicative and len(entries) > 1:
            total = 1.0
            for _n, v in entries:
                total *= v
            rows.append(f"&nbsp;&nbsp;<i>combined multiplicatively: "
                        f"{(total - 1.0) * 100:+.1f}%</i>")
        elif not multiplicative and len(entries) > 1:
            rows.append(f"&nbsp;&nbsp;<i>total {sum(v for _n, v in entries):+g}"
                        f"</i>")

        # Offset to the right of the cursor so the number stays readable.
        QToolTip.showText(QCursor.pos() + QPoint(18, 0), "<br>".join(rows))

    def _show_ar_breakdown(self) -> None:
        """Where the weapon's attack-rating change came from.

        Two different things move this number and they are worth telling apart:
        raising an attribute makes the weapon scale harder, while an attack
        multiplier scales the finished figure. A relic can do either, and "+35"
        alone does not say which -- or whether it came from one relic or six.
        """
        ar = getattr(self, "last_ar", None)
        if not ar:
            QToolTip.showText(QCursor.pos(), "No weapon selected.")
            return

        base, scaled, final = ar["base"], ar["scaled"], ar["final"]
        rows = [f"<b>Attack rating — {ar['weapon']}</b>",
                f"&nbsp;&nbsp;Base &nbsp; <b>{base:.0f}</b>"]

        from_attributes = scaled - base
        if abs(from_attributes) >= 0.5:
            rows.append(f"&nbsp;&nbsp;From attributes &nbsp; "
                        f"<b>{from_attributes:+.0f}</b>")

        for field_name, value in ar["rates"].items():
            rows.append(f"&nbsp;&nbsp;{model.label_for(field_name)} &nbsp; "
                        f"<b>{(value - 1.0) * 100:+.1f}%</b>")
            # Which relics produced that multiplier, in the same order and
            # wording the other breakdowns use.
            for name, own in self.last_sources.get(field_name, []):
                rows.append(f"&nbsp;&nbsp;&nbsp;&nbsp;"
                            f"<span style='color:{MUTED}'>{name} "
                            f"{(own - 1.0) * 100:+.1f}%</span>")

        if not ar["rates"] and abs(from_attributes) < 0.5:
            rows.append(f"&nbsp;&nbsp;<i>nothing equipped moves this weapon</i>")

        delta = final - base
        pct = (delta / base * 100) if base else 0.0
        rows.append(f"&nbsp;&nbsp;<b>Total {final:.0f}</b> "
                    f"({delta:+.0f}{f', {pct:+.1f}%' if base else ''})")
        QToolTip.showText(QCursor.pos() + QPoint(18, 0), "<br>".join(rows))

    def _refresh_weapon_damage(self, build) -> None:
        """Attack rating before and after everything equipped.

        Every tile is rated so each can show its own total; the active one gets
        the full breakdown underneath.
        """
        for index, slot in enumerate(self.weapon_slots):
            rating = None
            if slot.filled:
                rating = weapons.rate(slot.weapon, build.attributes,
                                      self.data, slot.tier)
            self.weapon_tiles[index].show_slot(
                slot, rating, active=index == self.active_weapon)

        slot = self.active_slot()
        if not slot.filled:
            self.last_ar = {}
            self.ar_label.setText(
                f"<span style='color:{MUTED}'>Slot "
                f"{self.active_weapon + 1} is empty — double-click a tile to "
                f"choose an armament, single-click one to break it down here."
                f"</span>")
            return
        weapon = slot.weapon
        tier = slot.tier

        before = weapons.rate(weapon, build.base_attributes, self.data, tier)
        after = weapons.rate(weapon, build.attributes, self.data, tier)

        # Apply the attack multipliers on top of the scaled figure.
        boosted: dict[str, float] = {}
        # Kept for the click-through breakdown: the figure before any rate is
        # applied, so the attribute scaling and the multipliers can be shown as
        # the two separate things they are.
        scaled_total = 0.0
        rates_in_play: dict[str, float] = {}
        for damage in weapons.DAMAGE_TYPES:
            total = after.base.get(damage, 0.0) + after.scaled.get(damage, 0.0)
            if not total:
                continue
            scaled_total += total
            typed_here = build.weapon_rates.get(weapon.get("wep_type"), {})
            class_here = build.class_rates.get(model.weapon_class(weapon), {})
            for field_name in self.AR_RATE_FOR.get(damage, ()):
                value = (build.rates.get(field_name, 1.0)
                         * typed_here.get(field_name, 1.0)
                         * class_here.get(field_name, 1.0))
                if abs(value - 1.0) > 1e-9:
                    rates_in_play[field_name] = value
            # Deliberately excludes model.CRIT_RATE: attack rating is the
            # ordinary hit, and folding a critical-only bonus into it would
            # overstate the weapon by a fifth.
            # Buffs tied to a weapon type only count for an armament of that
            # type, so a katana buff lifts the katana and leaves the bow alone.
            # The same for buffs tied to a class: "Improved Melee Attack Power"
            # covers the greatsword and not the bow beside it.
            typed = build.weapon_rates.get(weapon.get("wep_type"), {})
            by_class = build.class_rates.get(model.weapon_class(weapon), {})
            rate = 1.0
            for field_name in self.AR_RATE_FOR.get(damage, ()):
                rate *= build.rates.get(field_name, 1.0)
                rate *= typed.get(field_name, 1.0)
                rate *= by_class.get(field_name, 1.0)
            boosted[damage] = total * rate

        base_total = before.total
        final_total = sum(boosted.values())
        delta = final_total - base_total
        self.last_ar = {
            "base": base_total,
            "scaled": scaled_total,
            "final": final_total,
            "rates": rates_in_play,
            "weapon": weapon.get("name", "weapon"),
        }

        rows = []
        for damage, value in boosted.items():
            was = before.base.get(damage, 0.0) + before.scaled.get(damage, 0.0)
            diff = value - was
            colour = GOOD if diff > 0.05 else (BAD if diff < -0.05 else MUTED)
            change = f"{diff:+.0f}" if abs(diff) >= 0.5 else "—"
            rows.append(
                f"<div>{weapons.DAMAGE_LABELS[damage]} "
                f"<span style='color:{MUTED}'>{was:.0f}</span> "
                f"<span style='color:{colour}'>{change}</span> "
                f"<b>{value:.0f}</b></div>"
            )

        colour = GOOD if delta > 0.05 else (BAD if delta < -0.05 else MUTED)
        change = f"{delta:+.0f}" if abs(delta) >= 0.5 else "no change"
        pct = (delta / base_total * 100) if base_total else 0.0
        rows.append(
            f"<div style='margin-top:4px'><b>Total</b> "
            f"<span style='color:{MUTED}'>{base_total:.0f}</span> "
            f"<a href='{AR_BREAKDOWN_KEY}' style='color:{colour};"
            f"text-decoration:none'>{change}</a> "
            f"<b style='color:{ACCENT}'>{final_total:.0f}</b>"
            + (f" <span style='color:{colour}'>({pct:+.1f}%)</span>"
               if abs(pct) >= 0.05 else "") +
            f"</div>"
        )

        # Status the armament applies on a landed hit. This belongs with the
        # weapon rather than in the relic list: "Starting armament inflicts
        # frost" is the reason the attack rating above is 15% lower, and the
        # buildup is what you are buying with it.
        #
        # Only statuses your attacks apply are shown. The ones that build up on
        # you -- "Taking Damage Causes Poison Buildup" and the like -- reach the
        # player, not the enemy, and would read as a weapon property here.
        on_hit: dict[str, list[tuple[str, float]]] = {}
        for eff in self.selected_effects():
            for status, value in (eff.get("inflicts_on_hit") or {}).items():
                label = " ".join(str(eff.get("name", "")).split())
                on_hit.setdefault(status, []).append((label, value))

        for status, entries in sorted(on_hit.items()):
            total = sum(v for _n, v in entries)
            detail = ""
            if len(entries) > 1:
                # Whether two sources of one status really add is not stated in
                # the params, so the parts are shown rather than only the sum.
                parts = ", ".join(f"{n} {v:g}" for n, v in entries)
                detail = (f"<div style='color:{MUTED};font-size:11px'>"
                          f"{parts} — shown added; the params do not say "
                          f"whether they truly stack.</div>")
            rows.append(
                f"<div style='margin-top:6px'>Inflicts {status} "
                f"<b style='color:{ACCENT}'>{total:g}</b>"
                f"<span style='color:{MUTED}'> buildup per hit</span></div>"
                + detail
            )

        # Rally: how much HP this armament wins back per landed hit. It is a
        # flat figure carried by the weapon, not a share of the damage dealt,
        # so it belongs here next to the weapon rather than with the relic that
        # enables the mechanic. A weapon on 0 reclaims nothing no matter which
        # rally relic is equipped, which is the one thing worth seeing before
        # committing a slot to one.
        regain = weapon.get("regain_hp") or 0
        if regain:
            # "Partial HP Restoration upon Post-Damage Attacks" carries
            # regainRate, so it scales what the armament reclaims. Shown the
            # same way as the damage rows -- grey base, the change, then the
            # figure that actually applies -- because a rally relic changing
            # nothing on screen is exactly what makes it look broken.
            rate = build.rates.get("regainRate", 1.0)
            final_regain = regain * rate
            diff = final_regain - regain
            colour = GOOD if diff > 0.05 else (BAD if diff < -0.05 else MUTED)
            change = f"{diff:+.0f}" if abs(diff) >= 0.5 else "—"
            rows.append(
                f"<div style='margin-top:6px'>Rally recovery "
                f"<span style='color:{MUTED}'>{regain:.0f}</span> "
                f"<span style='color:{colour}'>{change}</span> "
                f"<b style='color:{ACCENT}'>{final_regain:.0f} HP</b>"
                f"<span style='color:{MUTED}'> per landed hit</span></div>"
                f"<div style='color:{MUTED};font-size:11px'>"
                f"A flat amount, not a share of the damage you deal, and it "
                f"varies by attack — some recover nothing.</div>"
            )
        else:
            rows.append(
                f"<div style='margin-top:6px;color:{MUTED}'>Rally recovery "
                f"<b style='color:{BAD}'>none</b> — this armament reclaims no "
                f"HP, so rally relics do nothing with it.</div>"
            )

        if not after.meets_requirements:
            unmet = ", ".join(
                f"{stat} {have}/{need}"
                for stat, (have, need) in after.unmet.items()
            )
            rows.append(
                f"<div style='color:{BAD}; font-size:10px'>requirements not "
                f"met: {unmet} — scaling from those stats is lost</div>"
            )
        rows.append(
            f"<div style='color:{MUTED}; font-size:10px; margin-top:2px'>"
            f"Grey is your base at this level; the change is what the equipped "
            f"relics add, counting stat gains and attack multipliers.</div>"
        )
        self.ar_label.setText("".join(rows))

    def rescan_save(self, initial: bool = False) -> None:
        """Re-read the save so newly found relics show up without a restart."""
        try:
            self.owned = inventory.load(self.data)
        except Exception as exc:  # noqa: BLE001
            self.owned = None
            self.owned_label.setText(f"Save could not be read: {exc}")
            return

        if self.owned is None:
            self.owned_label.setText(
                "No save file found. Relic slots stay empty; the Effects and "
                "Weapons tabs still work in full."
            )
            return

        self.owned_label.setText(
            f"{self.owned.relic_count} relics in {self.owned.source}"
        )
        # The folder is named after the Steam account id, so it is offered on
        # hover rather than printed where every screenshot would carry it.
        self.owned_label.setToolTip(self.owned.folder)
        if not initial:
            self.apply_chalice()

    def load_equipped(self) -> None:
        """Load the current Nightfarer's equipped loadout out of the save.

        Reads the vessel that Nightfarer has selected and the relics sitting in
        it, so the planner starts from the real build rather than an empty one.
        """
        if self.owned is None:
            self.owned_label.setText("No save loaded, so there is nothing to import.")
            return

        hero = self.current_hero()
        loadout = self.owned.selected_loadout(hero["id"])
        if loadout is None:
            self.owned_label.setText(
                f"This save stores no equipped loadout for {hero['name']}."
            )
            return

        # Rows include the two caption rows, so the vessel is found by its own
        # id on the item rather than by position.
        row = next(
            (i for i in range(self.chalice_list.count())
             if (self.chalice_list.item(i).data(Qt.UserRole) or {}).get("id")
             == loadout.vessel_id),
            None,
        )
        if row is None:
            self.owned_label.setText(
                f"{hero['name']} has vessel {loadout.vessel_id} equipped, which "
                "is not in this list."
            )
            return

        # Set the vessel and mode first: both rebuild the slots, which would
        # otherwise discard the relics just put in them.
        self.chalice_list.setCurrentRow(row)
        self.deep_check.blockSignals(True)
        self.deep_check.setChecked(loadout.deep_used)
        self.deep_check.blockSignals(False)
        self.apply_chalice()

        slots = list(self.base_slots) + list(self.deep_slots)
        missing = 0
        for slot, item in zip(slots, loadout.relics):
            if not slot.select_handle(item.handle if item else None):
                missing += 1

        vessel_name = self.chalice_list.item(row).data(Qt.UserRole)["name"]
        filled = sum(1 for r in loadout.relics if r is not None)
        note = (f"Loaded {hero['name']} — {vessel_name}, {filled} relics"
                f"{' (Deep of Night)' if loadout.deep_used else ''}.")
        if missing:
            # Only reachable if a search filter is hiding an equipped relic.
            note += f" {missing} could not be placed; clear the search and retry."
        self.owned_label.setText(note)
        self.recompute()

    def active_slots(self) -> list:
        slots = list(self.base_slots)
        if self.deep_check.isChecked():
            slots += self.deep_slots
        return slots

    def selected_curses(self) -> list[tuple[str, dict]]:
        """Every curse on the currently equipped relics, with its source.

        Only Deep of Night relics carry curses, so this is empty unless the
        Deep slots are in play.
        """
        out = []
        for slot in self.active_slots():
            item = slot.relic_box.currentData()
            if item is None:
                continue
            for cid in getattr(item, "curse_ids", ()) or ():
                eff = self.effects.get(str(cid))
                if eff:
                    out.append((item.name, eff))
        return out

    def selected_effects(self) -> list[dict]:
        slots = self.active_slots()
        out = []
        for slot in slots:
            for eid in slot.selected_ids():
                eff = self.effects.get(str(eid))
                if eff:
                    out.append(eff)
        return out

    def recompute(self) -> None:
        if not hasattr(self, "level_slider"):
            return
        hero = self.current_hero()
        level = self.level_slider.value()
        self.level_label.setText(str(level))
        exact = hero["exact_levels"]
        self.level_note.setText(
            "Exact value from the game data."
            if level in exact
            else f"Interpolated — the game defines levels {', '.join(map(str, exact))}."
        )

        # Curses are part of the relic you equipped, so they count towards the
        # totals exactly as the good rolls do. Leaving them out meant a curse
        # reading "Reduced Dexterity and Faith -3" changed no attribute, which
        # made the sheet quietly wrong for every Deep of Night build.
        curses = self.selected_curses()
        build = model.compute(
            hero, level,
            # Armament effects count towards the sheet alongside the relics.
            self.selected_effects() + self.weapon_effects()
            + [eff for _src, eff in curses],
            self.curves,
            # A weapon-type buff such as "Improved Axe Attack Power" is live
            # when any armament on the grid is of that type, so the gate is
            # tested against all six rather than only the active tile.
            weapon=self.active_slot().weapon,
            weapons_held=self.equipped_weapons(),
        )

        for grid in (self.attr_grid, self.derived_grid):
            while grid.count():
                item = grid.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

        for r, label in enumerate(("HP", "FP", "Stamina")):
            if label not in build.derived:
                continue
            base, total = build.derived[label]
            delta = total - base

            name = QLabel(label)
            name.setStyleSheet("font-size: 13px;")
            self.derived_grid.addWidget(name, r, 0)

            base_lbl = QLabel(f"{base:.0f}")
            base_lbl.setStyleSheet(f"color: {MUTED};")
            base_lbl.setAlignment(Qt.AlignRight)
            self.derived_grid.addWidget(base_lbl, r, 1)

            diff = QLabel(f"{delta:+.0f}" if abs(delta) >= 0.5 else "")
            diff.setStyleSheet(f"color: {GOOD if delta > 0 else BAD};")
            diff.setAlignment(Qt.AlignRight)
            self.derived_grid.addWidget(diff, r, 2)

            total_lbl = QLabel(f"{total:.0f}")
            total_lbl.setStyleSheet(
                f"font-weight: bold; font-size: 15px; color: {ACCENT};"
            )
            total_lbl.setAlignment(Qt.AlignRight)
            self.derived_grid.addWidget(total_lbl, r, 3)

        for r, name in enumerate(model.ATTRIBUTE_ORDER):
            base = build.base_attributes.get(name, 0)
            total = build.attributes.get(name, 0)
            delta = total - base

            self.attr_grid.addWidget(QLabel(name), r, 0)
            base_lbl = QLabel(str(base))
            base_lbl.setStyleSheet(f"color: {MUTED};")
            base_lbl.setAlignment(Qt.AlignRight)
            self.attr_grid.addWidget(base_lbl, r, 1)

            # ":+d" already carries the sign; prefixing another "+" printed
            # "+-3" for every curse. Clickable for the same reason as the
            # multipliers: a net +6 could be one relic or three fighting a curse.
            colour = GOOD if delta > 0 else BAD
            diff = QLabel(
                f"<a href='{name}' style='color:{colour}; "
                f"text-decoration:none'>{delta:+d}</a>" if delta else ""
            )
            diff.linkActivated.connect(self._show_breakdown)
            diff.setAlignment(Qt.AlignRight)
            self.attr_grid.addWidget(diff, r, 2)

            total_lbl = QLabel(str(total))
            total_lbl.setStyleSheet("font-weight: bold; font-size: 13px;")
            total_lbl.setAlignment(Qt.AlignRight)
            self.attr_grid.addWidget(total_lbl, r, 3)

        # Kept for the click-to-break-down popup, which fires long after this
        # method has returned.
        self.last_sources = dict(build.sources)
        self.last_rates = dict(build.rates)

        self._refresh_weapon_damage(build)

        # Every resistance type, always, so an untouched one is visibly zero
        # rather than absent. Buffs and curses are already summed per type by
        # compute_resistances, so what shows is the single net figure.
        lines = []
        for label in model.RESISTANCES:
            points, rate = build.resistances.get(label, (0, 1.0))
            parts = []
            if points:
                parts.append(
                    f"<span style='color:{GOOD if points > 0 else BAD}'>"
                    f"{points:+d}</span>"
                )
            if abs(rate - 1.0) > 1e-9:
                pct = (rate - 1.0) * 100
                parts.append(
                    f"<span style='color:{GOOD if pct > 0 else BAD}'>"
                    f"{pct:+.0f}%</span>"
                )
            value = " ".join(parts) or f"<span style='color:{MUTED}'>—</span>"
            lines.append(f"<div>{label} {value}</div>")
        lines.append(
            f"<div style='color:{MUTED}; font-size:10px; margin-top:4px'>"
            f"The net change from everything you have equipped. These are "
            f"changes to your resistances, not the totals.</div>"
        )
        self.resist_label.setText("".join(lines))

        if build.rates:
            lines = []
            cooldown = float(hero.get("ability_cooldown") or 0.0)
            # A buff that raises all five damage types by the same amount is one
            # buff, not five. Printing a row each turned "Starting armament
            # inflicts frost" into five identical -15.0% lines.
            shown_rates = dict(build.rates)
            for family in (model.ELEMENT_ATTACK_RATES,
                           model.ELEMENT_ATTACK_POWER_RATES):
                present = [f for f in family if f in shown_rates]
                values = {round(shown_rates[f], 6) for f in present}
                if len(present) == len(family) and len(values) == 1:
                    for f in present:
                        del shown_rates[f]
                    # Linked to a real field so the click-through breakdown
                    # still names the relics behind the number.
                    shown_rates[f"{model.ALL_DAMAGE_PREFIX}{present[0]}"] = \
                        build.rates[present[0]]
            for fname, value in sorted(shown_rates.items()):
                pct = (value - 1.0) * 100
                # For damage taken and resource costs, less is the good news.
                helpful = pct <= 0 if model.is_better_lower(model.real_field(fname)) else pct >= 0
                colour = GOOD if helpful else BAD
                # A percentage on its own is not actionable. Where the game
                # gives a time base, show what the number actually becomes.
                suffix = ""
                if fname == "characterSkillCooldownReduction" and cooldown:
                    suffix = (f" <span style='color:{MUTED}'>"
                              f"{cooldown:.1f}s → {cooldown * value:.1f}s</span>")
                # The number is a link: clicking it breaks the total back down
                # into the individual buffs behind it.
                lines.append(
                    f"<div>{model.label_for(fname)} "
                    f"<a href='{fname}' style='color:{colour}; "
                    f"text-decoration:none'>{pct:+.1f}%</a>{suffix}</div>"
                )
            self.rates_label.setText("".join(lines))
        else:
            lines = []

        # Buffs that cover only some armaments are held apart from the flat
        # totals so they cannot lift a weapon they do not apply to -- but they
        # still have to be visible, or a melee buff looks like it does nothing.
        def spell_out(bucket: dict, where: str) -> list[tuple[str, str, float]]:
            """One line per figure, but the five element rates collapse into a
            single "All damage" when they carry the same number between them --
            which they almost always do, and five identical rows read as five
            separate buffs."""
            rest = dict(bucket)
            values = [rest.pop(f) for f in model.ELEMENT_ATTACK_RATES
                      if f in rest] if all(
                f in rest for f in model.ELEMENT_ATTACK_RATES) else []
            out = []
            if values and len({round(v, 6) for v in values}) == 1:
                out.append((where, "All damage", values[0]))
            else:
                rest = dict(bucket)
            out += [(where, model.label_for(f), v)
                    for f, v in sorted(rest.items())]
            return out

        restricted: list[tuple[str, str, float]] = []
        for wep_type, bucket in sorted(build.weapon_rates.items()):
            family = next((w["family"] for w in self.data["weapons"]
                           if w.get("wep_type") == wep_type), None)
            where = f"{family} only" if family else f"weapon type {wep_type}"
            restricted += spell_out(bucket, where)
        for class_name, bucket in sorted(build.class_rates.items()):
            restricted += spell_out(bucket, f"{class_name} armaments only")

        for where, label, value in restricted:
            pct = (value - 1.0) * 100
            colour = GOOD if pct >= 0 else BAD
            lines.append(
                f"<div>{label} "
                f"<span style='color:{colour}'>{pct:+.1f}%</span>"
                f"<span style='color:{MUTED}'> — {where}</span></div>"
            )

        self.rates_label.setText(
            "".join(lines) if lines
            else f"<span style='color:{MUTED}'>none</span>")

        # Flat additions are not percentages and were being computed into
        # build.other and then never shown at all.
        if build.other:
            lines = []
            for fname, value in sorted(build.other.items()):
                colour = GOOD if value >= 0 else BAD
                # Additive fields whose neutral is 0 but which the game states
                # as a percentage -- item discovery, bow drop-off and the like.
                shown, unit = value, ""
                if fname in model.PERCENT_FIELDS:
                    shown, unit = model.percent_value(fname, value), "%"
                lines.append(
                    f"<div>{model.label_for(fname)} "
                    f"<a href='{fname}' style='color:{colour}; "
                    f"text-decoration:none'>{shown:+g}{unit}</a></div>"
                )
            self.other_label.setText("".join(lines))
            self.other_label.setVisible(True)
            self.other_heading.setVisible(True)
        else:
            self.other_label.setVisible(False)
            self.other_heading.setVisible(False)

        # Effects that do something real but move no number in the sheet. They
        # are listed rather than dropped, so an equipped effect is never
        # silently absent from the overview.
        # The heading always shows, with a count. Hiding the section outright
        # when empty meant you could not tell whether an effect had been filed
        # here or had simply vanished -- which is exactly how a conditional
        # attack buff reads as doing nothing at all.
        dead_count = sum(1 for _n, _d, why in build.qualitative
                         if why.startswith("NOT WORKING"))
        total = len(build.qualitative)
        if total:
            suffix = f" — {total}"
            if dead_count:
                suffix += (f", <span style='color:{BAD}'>{dead_count} not "
                           f"working</span>")
        else:
            suffix = " — none"
        self.qual_heading.setText(f"Conditional &amp; situational{suffix}")
        self.qual_heading.setVisible(True)

        if build.qualitative:
            lines = []
            for name, detail, why in build.qualitative:
                dead = why.startswith("NOT WORKING")
                head = BAD if dead else ACCENT
                shown = f"<s>{name}</s>" if dead else name
                lines.append(
                    f"<div style='margin-bottom:6px'>"
                    f"<span style='color:{head}'>{shown}</span>"
                    f"<div style='color:#cfcfcf; font-size:11px'>{detail}</div>"
                    f"<div style='color:{BAD if dead else MUTED}; "
                    f"font-size:10px'>{why}</div>"
                    f"</div>"
                )
            self.qual_label.setText("".join(lines))
        else:
            self.qual_label.setText(
                f"<span style='color:{MUTED}; font-size:11px'>Nothing you have "
                f"equipped depends on a condition. Effects that only work "
                f"below a HP threshold, with a particular armament, or on a "
                f"trigger would be listed here.</span>"
            )
        self.qual_label.setVisible(True)

        curses = self.selected_curses()
        if curses:
            lines = []
            for source, eff in curses:
                detail = effecttext.describe_full(eff)
                lines.append(
                    f"<div style='margin-bottom:6px'>"
                    f"<span style='color:{BAD}'>✦ {effecttext.name(eff)}</span>"
                    f"<div style='color:{MUTED}; font-size:11px'>{detail}</div>"
                    f"<div style='color:{MUTED}; font-size:10px'>from {source}</div>"
                    f"</div>"
                )
            self.curse_label.setText("".join(lines))
        elif self.deep_check.isChecked():
            self.curse_label.setText(
                f"<span style='color:{GOOD}'>none on the equipped relics</span>"
            )
        else:
            self.curse_label.setText(
                f"<span style='color:{MUTED}'>only Deep of Night relics carry "
                f"curses — tick Deep of Night to plan with them</span>"
            )

        if build.warnings:
            self.warn_label.setText(
                "".join(
                    f"<div style='color:{BAD}; margin-bottom:6px'>⚠ {w.text}</div>"
                    for w in build.warnings
                )
            )
        else:
            self.warn_label.setText(
                f"<span style='color:{GOOD}'>All selected effects stack.</span>"
            )


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(_dark_palette())

    icon = datasource.icon_path()
    if icon:
        app.setWindowIcon(QIcon(str(icon)))

    # Nothing ships with the program, so the first launch on a machine has
    # to read the installed game before there is anything to show.
    from nrdata import gamefiles

    error = firstrun.ensure_data(gamefiles.find_game_dir())
    if error:
        QMessageBox.critical(
            None, "Nightreign Helper", f"Could not read your game:\n\n{error}"
        )
        return 1

    try:
        data = load_data()
    except Exception as exc:  # noqa: BLE001
        QMessageBox.critical(None, "Nightreign Helper", str(exc))
        return 1

    window = Planner(data)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
