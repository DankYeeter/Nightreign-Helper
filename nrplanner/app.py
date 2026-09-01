"""Nightreign Helper -- Nightfarer, chalice, relic slots, stat sheet."""

from __future__ import annotations

import os
import sys

from PySide6.QtCore import QPoint, QPointF, QProcess, QSettings, QSize, Qt
from PySide6.QtGui import (
    QColor, QCursor, QFont, QIcon, QPainter, QPalette, QPen, QPixmap,
    QLinearGradient, QPolygonF, QRadialGradient,
)
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QCompleter, QDialog, QFrame,
    QInputDialog,
    QGridLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QLineEdit, QMainWindow, QMessageBox, QPushButton, QScrollArea, QSizePolicy,
    QSlider, QSplitter, QTabWidget, QToolButton, QToolTip, QVBoxLayout,
    QWidget,
)

from . import __version__
from . import (chalices, datasource, effecttext, favourites, firstrun,
               inventory, model, shortcut, uiscale, weaponslots, weapons)
from .damage import attack_rating, is_starting_armament
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

# Where the three panes' widths are kept, so a window sized once stays
# that way. QSplitter's own encoding, which survives a pane being added.
PANES_KEY = "ui/panes"

# The opening pane widths, shared by first run, the restore fallback and the
# Reset layout button so all three mean the same thing by construction.
PANE_DEFAULTS = (430, 520, 370)

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


class SituationalRow(QFrame):
    """One gated effect, with a switch and -- if it stacks -- a count.

    The sheet cannot know whether the condition is met. This is where the
    player says so: tick it and the effect joins every total, exactly as an
    always-on roll would.
    """

    def __init__(self, entry, count: int, on_change):
        super().__init__()
        self.effect_id = entry.effect_id
        self.accumulates = entry.accumulates
        self.on_change = on_change
        self.setStyleSheet("QFrame { border: none; }")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 5)
        layout.setSpacing(1)

        head = QHBoxLayout()
        head.setSpacing(6)
        # The name is a separate wrapping label rather than the checkbox's own
        # text. A QCheckBox will not wrap, so a long effect name set the whole
        # sheet's minimum width -- which pushed the panel wider than its
        # viewport and clipped every other line in it, count box included.
        self.check = QCheckBox()
        self.check.setChecked(count > 0)
        self.check.setStyleSheet("border: none;")
        self.check.toggled.connect(self._toggled)
        head.addWidget(self.check, 0, Qt.AlignTop)

        self.title = QLabel(entry.name)
        self.title.setWordWrap(True)
        self.title.setCursor(Qt.PointingHandCursor)
        self.title.setStyleSheet(f"color: {ACCENT}; border: none;")
        self.title.mousePressEvent = lambda _e: self.check.toggle()
        head.addWidget(self.title, 1)

        if entry.accumulates:
            # Free text, not a spin box with a ceiling. How many Night Invaders
            # a map can hold, or how many Sites of Grace are in reach, is a
            # fact about the run rather than about this program -- so the
            # player states the number and the arithmetic follows it.
            self.times = QLabel("×")
            self.times.setStyleSheet(f"color: {MUTED}; border: none;")
            head.addWidget(self.times, 0, Qt.AlignTop)
            self.count = QLineEdit(str(max(count, 1)))
            self.count.setFixedWidth(42)
            self.count.setAlignment(Qt.AlignCenter)
            self.count.setToolTip("How many times this is true right now")
            self.count.editingFinished.connect(self._edited)
            head.addWidget(self.count, 0, Qt.AlignTop)
            self._set_count_enabled(count > 0)
        else:
            self.count = None
        layout.addLayout(head)

        detail = QLabel(entry.detail)
        detail.setWordWrap(True)
        detail.setStyleSheet("color: #cfcfcf; font-size: 11px; border: none;")
        layout.addWidget(detail)

        self.why_text = entry.why
        self.why = QLabel()
        self.why.setWordWrap(True)
        self.why.setStyleSheet(f"color: {MUTED}; font-size: 10px; border: none;")
        layout.addWidget(self.why)
        self._refresh_why()

    def _refresh_why(self) -> None:
        """Say whether this is currently counted, not only why it is gated."""
        value = self.value()
        if value:
            times = f" ×{value}" if self.count is not None else ""
            self.why.setText(f"counted in the totals{times} — {self.why_text}")
            self.why.setStyleSheet(
                f"color: {GOOD}; font-size: 10px; border: none;")
        else:
            self.why.setText(self.why_text)
            self.why.setStyleSheet(
                f"color: {MUTED}; font-size: 10px; border: none;")

    def _set_count_enabled(self, on: bool) -> None:
        if self.count is not None:
            self.count.setEnabled(on)
            self.times.setEnabled(on)

    def value(self) -> int:
        """How many times the player says this applies; 0 when switched off."""
        if not self.check.isChecked():
            return 0
        if self.count is None:
            return 1
        text = self.count.text().strip()
        try:
            # A blank or nonsense box means "it is true", not "it is true zero
            # times" -- switching it on is already the statement that it holds.
            return max(int(text), 1)
        except ValueError:
            return 1

    def _toggled(self, on: bool) -> None:
        self._set_count_enabled(on)
        self._refresh_why()
        self.on_change()

    def _edited(self) -> None:
        value = self.value()
        if self.count is not None and self.count.text().strip() != str(value):
            self.count.setText(str(value))
        self._refresh_why()
        if self.check.isChecked():
            self.on_change()


# The slot-colour gems, by relic colour. White ships none -- the game has
# only four -- so it is drawn as a pale diamond to match.
SLOT_GEMS = {
    0: "MENU_MenuIcon_40480.png",
    1: "MENU_MenuIcon_40481.png",
    2: "MENU_MenuIcon_40483.png",   # Yellow
    3: "MENU_MenuIcon_40482.png",   # Green
}


# Drawn chips, keyed by what actually changes their pixels. Without this the
# vessel list redrew every slot of every vessel on each hero switch -- eleven
# vessels times six slots, each a scaled composite -- which took the import
# smoke test from seconds to minutes.
_CHIP_CACHE: dict[tuple, QPixmap] = {}


def slot_chip(icons, colour: int, owned=None, size: int = 26):
    """One relic slot, drawn the way the game presents it.

    A dark cell, a coloured glow rising from its floor, the relic sitting in
    it, and the colour gem in the corner. The gem matters precisely because a
    filled slot hides most of the glow -- which is why the game puts it there
    -- so it is drawn only when something is in the slot.

    The glow is drawn rather than extracted: the sprite atlas carries the
    gems and the relic art but no slot light, so this is the one piece with
    no authentic source, and it is generated to sit under the real ones.
    """
    key = (colour, size, getattr(owned, "icon", None) if owned else None)
    cached = _CHIP_CACHE.get(key)
    if cached is not None:
        return cached

    chip = QPixmap(size, size)
    chip.fill(Qt.transparent)
    tint = QColor(SLOT_COLOURS.get(colour, "#8a8a8a"))
    painter = QPainter(chip)
    painter.setRenderHint(QPainter.Antialiasing, True)

    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor("#15161a"))
    painter.drawRoundedRect(0, 0, size - 1, size - 1, 4, 4)

    # The light standing in the cell. The game renders this per frame -- it
    # is in no sprite anywhere in the menu atlas, which was searched
    # exhaustively -- so it is drawn.
    #
    # It is drawn small and scaled up, which is the whole trick: at a quarter
    # size the shapes are a few pixels across, and the smooth upscale turns
    # their edges into a gradient. Drawing at full size gives either a hard
    # triangle or visible rings, both of which read as a drawn shape rather
    # than as light -- each was tried and looked it.
    lit = 1.0 if owned is None else 0.5
    small = max(8, size // 4)
    layer = QPixmap(small, small)
    layer.fill(Qt.transparent)
    lp = QPainter(layer)
    lp.setRenderHint(QPainter.Antialiasing, True)
    lp.setPen(Qt.NoPen)

    cone = QLinearGradient(0, small * 0.88, 0, small * 0.18)
    base = QColor(tint).lighter(140); base.setAlpha(int(230 * lit))
    tip = QColor(tint); tip.setAlpha(0)
    cone.setColorAt(0.0, base)
    cone.setColorAt(1.0, tip)
    lp.setBrush(cone)
    lp.drawPolygon(QPolygonF([
        QPointF(small * 0.5, small * 0.12),
        QPointF(small * 0.88, small * 0.88),
        QPointF(small * 0.12, small * 0.88),
    ]))

    pool = QRadialGradient(small / 2, small * 0.82, small * 0.5)
    hot = QColor(tint).lighter(170); hot.setAlpha(int(245 * lit))
    pool.setColorAt(0.0, hot)
    rim = QColor(tint); rim.setAlpha(0)
    pool.setColorAt(1.0, rim)
    lp.setBrush(pool)
    lp.drawEllipse(QPointF(small / 2, small * 0.82),
                   small * 0.46, small * 0.20)
    lp.end()

    painter.setClipRect(1, 1, size - 2, size - 2)
    painter.drawPixmap(0, 0, layer.scaled(size, size, Qt.IgnoreAspectRatio,
                                          Qt.SmoothTransformation))
    painter.setClipping(False)

    if owned is not None and icons is not None:
        art = icons.item(getattr(owned, "icon", None))
        if art is not None:
            inner = int(size * 0.78)
            art = art.scaled(inner, inner, Qt.KeepAspectRatio,
                             Qt.SmoothTransformation)
            painter.drawPixmap((size - art.width()) // 2,
                               (size - art.height()) // 2 - 1, art)
        gem = icons.ui(SLOT_GEMS[colour]) if colour in SLOT_GEMS else None
        pip = max(7, size // 3)
        if gem is not None and not gem.isNull():
            gem = gem.scaled(pip, pip, Qt.KeepAspectRatio,
                             Qt.SmoothTransformation)
            painter.drawPixmap(size - pip - 1, size - pip - 1, gem)
        else:
            # White has no gem of its own; a plain diamond stands in for it.
            painter.save()
            painter.translate(size - pip / 2 - 2, size - pip / 2 - 2)
            painter.rotate(45)
            painter.setBrush(tint)
            painter.setPen(QColor("#00000060"))
            painter.drawRect(-pip // 3, -pip // 3, 2 * pip // 3, 2 * pip // 3)
            painter.restore()

    painter.setBrush(Qt.NoBrush)
    painter.setPen(QColor("#00000070"))
    painter.drawRoundedRect(0, 0, size - 1, size - 1, 4, 4)
    painter.end()
    _CHIP_CACHE[key] = chip
    return chip


class VesselStrip(QWidget):
    """The vessel's slots as one small row, the way the game shows them.

    The six editing panels below say what each relic *does*; this says what
    the chalice *is* -- which slots it has, what colour each one is, and which
    are filled. Reading that off six tall panels means scrolling; reading it
    off one row is a glance, which is the whole point of it.

    A Deep of Night vessel exposes three more slots, so the strip is three or
    six tiles wide and never a fixed six: showing three greyed tiles for slots
    the vessel does not have would be inventing a chalice.
    """

    TILE = 40
    ICON = 30
    # The relic screen's own slot sprite. It ships greyscale -- the five that
    # exist are a rarity ladder with no green in it -- so it is tinted to the
    # slot's colour rather than picked from the set.
    SPRITE = "MENU_In_RaritySlot_00.png"

    def __init__(self, icons=None):
        super().__init__()
        self.icons = icons
        self._tinted: dict[int, QPixmap] = {}
        self._row = QHBoxLayout(self)
        self._row.setContentsMargins(0, 2, 0, 2)
        self._row.setSpacing(4)
        self._row.addStretch(1)
        self.tiles: list[QLabel] = []

    def _backing(self, colour: int) -> QPixmap | None:
        """The slot sprite, tinted to one relic colour and cached."""
        if colour in self._tinted:
            return self._tinted[colour]
        base = self.icons.ui(self.SPRITE) if self.icons is not None else None
        if base is None:
            return None
        tile = base.scaled(self.TILE, self.TILE, Qt.KeepAspectRatioByExpanding,
                           Qt.SmoothTransformation)
        # Overlay is the blend that reproduces the game's own colouring:
        # tinting the greyscale sprite this way against the shipped red
        # variant (RaritySlot_10) matches it almost exactly -- dark interior,
        # colour-lit smoke -- where multiply buried the sprite and screen
        # washed it out. Checked side by side, not assumed.
        tinted = QPixmap(tile.size())
        tinted.fill(Qt.transparent)
        painter = QPainter(tinted)
        painter.drawPixmap(0, 0, tile)
        painter.setCompositionMode(QPainter.CompositionMode_Overlay)
        painter.fillRect(tinted.rect(),
                         QColor(SLOT_COLOURS.get(colour, "#8a8a8a")))
        painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        painter.drawPixmap(0, 0, tile)
        painter.end()
        self._tinted[colour] = tinted
        return tinted

    def show_slots(self, colours: list[int], items: list) -> None:
        """One tile per slot the vessel has: its colour, and its relic."""
        while self._row.count() > 1:
            item = self._row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.tiles = []

        for index, colour in enumerate(colours):
            tint = SLOT_COLOURS.get(colour, "#8a8a8a")
            backing = slot_chip(self.icons, colour,
                                items[index] if index < len(items) else None,
                                self.TILE)
            tile = QLabel()
            tile.setFixedSize(self.TILE, self.TILE)
            tile.setAlignment(Qt.AlignCenter)
            owned = items[index] if index < len(items) else None
            if backing is not None:
                tile.setPixmap(backing)
                tile.setStyleSheet("border: none; background: transparent;")
                tile.setToolTip(getattr(owned, "name", "") or "empty slot")
                self._row.insertWidget(index, tile)
                self.tiles.append(tile)
                continue
            # A filled slot is drawn in its colour; an empty one keeps the
            # colour as an outline only, so "this chalice has a red slot" and
            # "there is a red relic in it" never look the same.
            if owned is not None:
                tile.setStyleSheet(
                    f"background: rgba(255,255,255,18);"
                    f" border: 2px solid {tint}; border-radius: 5px;")
                icon = None
                if self.icons is not None:
                    icon = self.icons.item(getattr(owned, "icon", None))
                if icon is not None:
                    tile.setPixmap(icon.scaled(
                        self.ICON, self.ICON, Qt.KeepAspectRatio,
                        Qt.SmoothTransformation))
                tile.setToolTip(getattr(owned, "name", ""))
            else:
                tile.setStyleSheet(
                    f"background: transparent;"
                    f" border: 1px dashed {tint}; border-radius: 5px;")
                tile.setToolTip("empty slot")
            self._row.insertWidget(index, tile)
            self.tiles.append(tile)


def _same_copy(one, other) -> bool:
    """Whether two entries stand for the same physical relic.

    By copy_key where there is one -- the handle the save's loadout table
    uses, or the record's own place in the save. A relic with neither (a
    custom one, or an entry that never came out of a save) stands for itself
    and nothing else.
    """
    key = inventory.copy_key(one)
    if key is None:
        return one is other
    return key == inventory.copy_key(other)


class RelicSlot(QFrame):
    """One relic slot: a fixed colour from the chalice, up to three effects."""

    def __init__(self, index: int, deep: bool, on_change, icons=None,
                 on_search_changed=None, taken_elsewhere=None):
        super().__init__()
        self.index = index
        self.deep = deep
        self.on_change = on_change
        self.icons = icons
        self.on_search_changed = on_search_changed or (lambda _text: None)
        # Which physical relics the other slots are already holding. A slot on
        # its own knows of no others and so blocks nothing.
        self.taken_elsewhere = taken_elsewhere or (lambda _slot: frozenset())
        self.search_text = ""
        # Why this slot is empty, when it was emptied for a reason worth
        # saying. An empty slot otherwise looks the same whether nothing was
        # ever put in it or its relic was taken away by a rule.
        self.empty_reason = ""
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
        # Whatever this slot was last told to say about being empty is spent:
        # the player has just put something here or taken it away themselves.
        self.empty_reason = ""
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
            # An empty slot says nothing unless it was emptied for a reason.
            # A slot whose relic is worn elsewhere used to read exactly like
            # one never filled, leaving the player to work out where the
            # relic went (DR-002).
            if self.empty_reason:
                self.rolled_label.setText(
                    f"<div style='color:{MUTED}'>{self.empty_reason}</div>")
            else:
                self.rolled_label.clear()
            self.rolled_label.setVisible(bool(self.empty_reason))
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
                   hero_name: str = "") -> None:
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
        self.populate()

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
        self.populate()
        if self.custom_item is not None:
            index = self.relic_box.findData(self.custom_item)
            if index >= 0:
                self.relic_box.setCurrentIndex(index)
        self.on_change()

    def available_items(self) -> list:
        """The relics this slot may be given.

        Owned, of a colour and mode this slot takes, and not already lying in
        another slot: a relic is one physical object and cannot be worn twice.
        It used to be offered everywhere it fit, and taking the same entry
        into two slots counted its effects twice -- silently, with no warning
        and a plausible total (QA-002). With 306 distinct rolls across 309
        owned relics, an entry in this list stands for exactly one physical
        relic 99 times out of 100, so the second helping was almost never real.
        Planning around a relic you do not own is what "Custom relic" is for,
        and that stays untouched.

        The ownership filter runs *before* the collapse to one entry per roll,
        not after: a player who owns two copies of the same roll may wear both,
        and the second copy has to survive to be offered.
        """
        if self.owned is None:
            return []
        taken = self.taken_elsewhere(self)
        free = [item for item
                in self.owned.relics_for(self.colour, self.deep, WHITE_SLOT)
                if inventory.copy_key(item) not in taken]
        # The same collapse the picker applies, or the header counts the
        # save's records while the picker counts distinct rolls and the
        # two sit one apart on screen ("50 owned" over "49 of 49").
        return favourites.distinct(free)

    def slot_name(self) -> str:
        """What this slot is called on screen, and in anything said about it."""
        return f"{'Deep ' if self.deep else ''}Slot {self.index + 1}"

    def _may_hold(self, item) -> bool:
        """Whether this slot could take this relic at all: colour and mode.

        Asked about the relic already in the slot, which stays in the list
        whatever else is being filtered out -- but not past a change of
        chalice. A relic of a colour this slot no longer takes belongs to the
        chalice before it, and keeping such a relic is how a Grail came to own
        one nobody put there.
        """
        if self.owned is None or item is None:
            return False
        return any(_same_copy(item, other) for other
                   in self.owned.relics_for(self.colour, self.deep, WHITE_SLOT))

    def populate(self) -> None:
        """List the relics this slot may be given, and the one it has.

        What a slot may be given is a question of ownership, colour and mode.
        Narrowing it by effect is the picker's work: there a filter changes
        what is being *chosen from* and can disturb nothing that is already
        equipped. Applied here it dropped the relic out of a slot the moment
        it stopped matching, and the loss was written down (QA-013) -- one
        mistyped word in the picker emptied every other slot.

        Whatever is in the slot is in the slot's own list, however that list
        was arrived at. The rule is enforced here rather than trusted to the
        callers: two of them already carry a comment saying that narrowing a
        slot from outside is what makes an equipped relic disappear, and a
        third arrived and did it anyway, for an unrelated reason.
        """
        worn = self.relic_box.currentData()
        items = self.available_items()
        if (worn is not None and worn is not self.custom_item
                and self._may_hold(worn)
                and not any(_same_copy(worn, item) for item in items)):
            items = items + [worn]

        self.relic_box.blockSignals(True)
        self.relic_box.clear()
        self.relic_box.addItem("Empty slot", None)
        # A custom relic is not owned, so it survives repopulation only by
        # being re-added here.
        if self.custom_item is not None:
            summary = ", ".join(self.effect_names(self.custom_item))
            self.relic_box.addItem(
                f"Custom relic — {summary}"[:120], self.custom_item)
        for item in items:
            summary = ", ".join(self.effect_names(item))
            label = f"{item.name} — {summary}" if summary else item.name
            self.relic_box.addItem(label[:120], item)
        if worn is not None:
            idx = self.relic_box.findData(worn)
            if idx >= 0:
                self.relic_box.setCurrentIndex(idx)
        self.relic_box.blockSignals(False)

        # "available" rather than "owned": a relic lying in another slot is
        # owned and is not offered here, so counting it would put a number on
        # the heading that the list underneath contradicts.
        self.title.setText(
            f"{self.slot_name()} — "
            f"{model.COLOUR_NAMES.get(self.colour, self.colour)}"
            f"  ({len(items)} available)"
        )
        self._sync_mode()

    def clear_relic(self, reason: str = "") -> None:
        """Take whatever is in this slot out of it, and say why if there is a why.

        Signals are held back. A slot emptied during a restore is part of
        setting one build, not six separate changes by the player, and the
        window settles the slots itself once the restore has finished.
        """
        self.empty_reason = reason
        self.relic_box.blockSignals(True)
        try:
            self.relic_box.setCurrentIndex(0)
        finally:
            self.relic_box.blockSignals(False)
            self._sync_mode()

    def selected_ids(self) -> list[int]:
        item = self.relic_box.currentData()
        return list(item.effect_ids) if item is not None else []

    def current_relic(self):
        """The relic sitting in this slot, or None.

        Named deliberately: `self.owned` is the whole inventory, not the
        chosen relic, and reading it as the relic is a mistake already made
        once -- it renders as a filled slot with no art in it.
        """
        return self.relic_box.currentData()

    def saved_key(self) -> str:
        """How this slot's relic is written down for the next session."""
        return chalices.slot_key(self.relic_box.currentData())

    def select_saved(self, key: str) -> bool:
        """Put back the relic a previous session left here.

        The handle is tried first because it is exact. Falling back to the
        roll matters when the save has been rewritten since -- handles are
        renumbered by the game, and a build that came back empty every time
        the player melted an unrelated relic would not be worth storing.
        """
        self.empty_reason = ""
        if not key:
            return self.select_handle(None)
        handle, roll = chalices.split_key(key)
        if handle is not None and self.select_handle(handle):
            return True
        if not roll:
            return False
        self.relic_box.blockSignals(True)
        try:
            for i in range(self.relic_box.count()):
                item = self.relic_box.itemData(i)
                if item is not None and favourites.key(item) == roll:
                    self.relic_box.setCurrentIndex(i)
                    return True
            return False
        finally:
            self.relic_box.blockSignals(False)
            self._sync_mode()

    def select_handle(self, handle: int | None) -> bool:
        """Put the relic with this save handle in the slot, or empty it.

        Matching on the handle rather than the name matters: several copies of
        one relic can be owned with different rolls, and this save equips the
        second copy of The Wylder's Earring while the first sits unused.

        Signals are held back so importing six slots recomputes the build once
        at the end rather than six times.
        """
        self.empty_reason = ""
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
        # effect id -> how many times the player says its condition is met.
        # Session state, like the armament tiles: a declaration is about the
        # run you are in, not a preference worth remembering across launches.
        self.declared: dict[int, int] = {}
        # The build every tab reads, computed once per change by recompute().
        # None until the first one has been computed.
        self._build: model.Build | None = None
        # Held while a stored build is being put back, so the act of restoring
        # a vessel and six relics does not write a half-restored build over
        # the one still being read.
        self._restoring = False

        # The data version is a build number off the game install. It means
        # nothing to a player and ate half the title bar, so the title just
        # names the tool. Only a re-read after a patch is worth saying, and it
        # is said in words rather than as a version id.
        # The tool's own version does belong in the title: it is the one thing
        # a bug report needs and the one thing a reporter cannot look up after
        # the fact.
        stale = data.get("meta", {}).get("regenerated")
        self.setWindowTitle(
            f"Nightreign Helper {__version__}"
            + ("  —  updated for your installed game version" if stale else "")
        )
        self.resize(1320, 860)

        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        # A Start Menu entry is offered during first-run setup, which a player
        # upgrading from an earlier version never sees, and which anyone can
        # decline and later want. So it also lives here, permanently, in the
        # one piece of chrome that is on screen whichever tab is open. A corner
        # widget rather than a menu bar: the window has never had one, and
        # growing one for a single action would cost more room than it earns.
        self.shortcut_button = QToolButton()
        self.shortcut_button.setAutoRaise(True)
        self.shortcut_button.setCursor(Qt.PointingHandCursor)
        self.shortcut_button.clicked.connect(self._toggle_shortcut)
        self._sync_shortcut_button()

        # How large the interface is drawn goes beside it, for the same
        # reason: it belongs to no tab, and this is the only chrome on screen
        # whichever tab is open. Automatic follows Windows, which is what the
        # program has always done and stays the default.
        corner = QWidget()
        corner_row = QHBoxLayout(corner)
        corner_row.setContentsMargins(0, 0, 6, 0)
        corner_row.setSpacing(6)
        scale_caption = QLabel("UI scale")
        scale_caption.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        corner_row.addWidget(scale_caption)
        self.scale_box = QComboBox()
        for label, value in uiscale.CHOICES:
            self.scale_box.addItem(label, value)
        stored_scale = self.scale_box.findData(uiscale.stored())
        self.scale_box.setCurrentIndex(max(stored_scale, 0))
        self.scale_box.setToolTip(
            "How large everything is drawn, on top of Windows' own display "
            "scaling. Automatic is Windows' setting unchanged."
        )
        self.scale_box.activated.connect(self._choose_scale)
        corner_row.addWidget(self.scale_box)
        # A way back for the panes. Anyone can drag a splitter somewhere
        # unfortunate, and 1.7.0 could store such a state on its own; without
        # an inverse the player's only route was hand-editing the registry.
        reset_layout = QPushButton("Reset layout")
        reset_layout.setToolTip(
            "Put the three Build planner panes back to their opening widths")
        reset_layout.clicked.connect(self._reset_layout)
        corner_row.addWidget(reset_layout)
        if shortcut.available():
            corner_row.addWidget(self.shortcut_button)
        tabs.setCornerWidget(corner, Qt.TopRightCorner)

        planner = QWidget()
        root = QHBoxLayout(planner)
        root.setContentsMargins(14, 14, 14, 14)
        # The splitter draws its own gaps, so the layout no longer adds any.
        root.setSpacing(0)

        # Panes rather than three columns pinned to the pixel. The sidebar was
        # 430 wide and the sheet 370 on every machine, so the same numbers had
        # to serve a laptop and a 4K monitor: relic names were cut off on one
        # while the sheet had room going spare on the other, and nothing could
        # be done about either. Collapsing is off -- a pane dragged shut
        # leaves nothing on screen to say it is still there, and reads as the
        # program having lost it.
        self.panes = QSplitter(Qt.Horizontal)
        self.panes.setChildrenCollapsible(False)
        self.panes.setHandleWidth(10)
        self.panes.addWidget(self._build_left())
        self.panes.addWidget(self._build_middle())
        self.panes.addWidget(self._build_right())
        # Extra width goes to the slots in the middle; the two edges keep the
        # size they were given, which is what they had before.
        self.panes.setStretchFactor(0, 0)
        self.panes.setStretchFactor(1, 1)
        self.panes.setStretchFactor(2, 0)
        self.panes.setSizes(list(PANE_DEFAULTS))
        stored_panes = QSettings(favourites.ORG, favourites.APP).value(PANES_KEY)
        if stored_panes:
            try:
                self.panes.restoreState(stored_panes)
            except TypeError:
                pass    # a key from some older shape of this setting
            # No validation here, and that is deliberate: sizes() before the
            # first layout returns placeholder values (measured: [276, 68,
            # 276] for a stored [520, 328, 420]), so any check at this point
            # condemns good states. The pane floors and childrenCollapsible
            # already clamp a genuinely broken state at layout time --
            # smoke_layout.py proves a stored [4000, 4000, 0] comes back with
            # the stat sheet at its floor -- and Reset layout is the way out
            # of anything merely unfortunate.
        root.addWidget(self.panes)

        # Written once, on the way out. splitterMoved fires for every pixel of
        # a drag, and a settings write per pixel is a lot of nothing.
        instance = QApplication.instance()
        if instance is not None:
            instance.aboutToQuit.connect(self._store_layout)

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
            tabs.addTab(self.depths_tab, "Red variants")
        if (data.get("world_events") or {}).get("events"):
            self.events_tab = WorldEventsTab(data)
            tabs.addTab(self.events_tab, "World Events")

    # -- panels ----------------------------------------------------------
    def _build_left(self) -> QWidget:
        panel = QWidget()
        # 430 is what this pane opens at, and is no longer all it can be:
        # it is a pane of a splitter now, and the player sizes it. The floor
        # is what a vessel's icon and its six slots need before the name has
        # anywhere left to go -- below that the list stops saying which vessel
        # each row is, which is worse than a scrollbar.
        panel.setMinimumWidth(300)
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
        # Wide enough for the vessel's own icon plus its slots drawn beside
        # it; six of them in Deep of Night is the widest case.
        self.chalice_list.setIconSize(QSize(34 + 5 + 6 * 24, 34))
        self.chalice_list.currentRowChanged.connect(lambda *_: self.apply_chalice())
        layout.addWidget(self.chalice_list, 1)

        self.deep_check = QCheckBox("Deep of Night (3 extra slots)")
        self.deep_check.toggled.connect(self._on_deep_toggled)
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

        # The heading and, opposite it, the way out of a build. Equipped
        # relics now survive a restart, so there has to be something that
        # clears them on purpose -- otherwise the only way back to an empty
        # vessel is to empty six slots by hand.
        header = QHBoxLayout()
        header.addWidget(_heading("Relic slots"))
        header.addStretch()
        self.reset_button = QPushButton("Reset Chalice")
        self.reset_button.setToolTip(
            "Empty every slot and forget this Nightfarer's saved build"
        )
        self.reset_button.clicked.connect(self.reset_chalice)
        header.addWidget(self.reset_button)
        layout.addLayout(header)

        # The vessel at a glance, above the six panels that edit it.
        self.vessel_strip = VesselStrip(self.icons)
        layout.addWidget(self.vessel_strip)

        # Saved builds. The scratchpad -- whatever is in the slots now -- is
        # still restored on launch; this is for keeping several worked-out
        # builds and flipping between them to compare.
        builds = QHBoxLayout()
        builds.setSpacing(6)
        builds.addWidget(QLabel("Build"))
        self.build_box = QComboBox()
        self.build_box.setMinimumWidth(180)
        self.build_box.activated.connect(self._on_build_chosen)
        builds.addWidget(self.build_box, 1)
        save_build = QPushButton("Save")
        save_build.setToolTip("Save the slots as they are under a name")
        save_build.clicked.connect(self._save_build)
        builds.addWidget(save_build)
        self.delete_build_button = QPushButton("Delete")
        self.delete_build_button.setToolTip("Forget the selected saved build")
        self.delete_build_button.clicked.connect(self._delete_build)
        builds.addWidget(self.delete_build_button)
        self.hide_build_button = QPushButton("Hide")
        self.hide_build_button.setToolTip(
            "Keep this build out of the list without deleting it — "
            "Show hidden lists it again")
        self.hide_build_button.clicked.connect(self._toggle_hidden_build)
        builds.addWidget(self.hide_build_button)
        # Hiding was one-way. The build left the list as soon as anything else
        # was selected and nothing anywhere offered it back, so the only route
        # a player found was to save a new build under the same name -- which
        # does bring the entry back, and overwrites everything that was in it.
        self.show_hidden_check = QCheckBox("Show hidden")
        self.show_hidden_check.setToolTip(
            "List the builds you have hidden, so one can be selected and "
            "unhidden")
        self.show_hidden_check.toggled.connect(
            lambda *_: self.refresh_build_list())
        builds.addWidget(self.show_hidden_check)
        layout.addLayout(builds)

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
            RelicSlot(i, False, self._relic_changed, self.icons,
                      self._set_search, self._relics_taken_elsewhere)
            for i in range(3)
        ]
        for slot in self.base_slots:
            layout.addWidget(slot)

        self.deep_heading = _heading("Deep of Night slots")
        layout.addWidget(self.deep_heading)
        self.deep_slots = [
            RelicSlot(i, True, self._relic_changed, self.icons,
                      self._set_search, self._relics_taken_elsewhere)
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
        # 348 was tight before the situational switches and cramped after them:
        # a multiplier line such as "All damage +6.0% - melee armaments only"
        # had nowhere to go, and the count box sat past the right edge. 370 is
        # still what it opens at -- the splitter's initial sizes say so -- but
        # a player who wants the sheet wider may now have it, and one who
        # drags it narrow gets the wrapping rather than a cut-off column.
        outer.setMinimumWidth(340)
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

        # The switchable ones first, as widgets, then the rest as text. Only
        # the top group can be acted on, and mixing them would hide that.
        self.qual_rows = QWidget()
        self.qual_rows_layout = QVBoxLayout(self.qual_rows)
        self.qual_rows_layout.setContentsMargins(0, 0, 0, 0)
        self.qual_rows_layout.setSpacing(0)
        layout.addWidget(self.qual_rows)
        self.situational_rows: dict[int, SituationalRow] = {}

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

    # -- window chrome: pane widths, scale, Start Menu entry -------------
    def _store_layout(self) -> None:
        """Remember how wide the player made each pane."""
        if hasattr(self, "panes"):
            QSettings(favourites.ORG, favourites.APP).setValue(
                PANES_KEY, self.panes.saveState())

    def _reset_layout(self) -> None:
        """The panes back to their opening widths, and the stored state gone.

        Both halves matter: setSizes alone would come back wrong on the next
        launch if the stored state is the broken thing being escaped from.
        """
        self.panes.setSizes(list(PANE_DEFAULTS))
        QSettings(favourites.ORG, favourites.APP).remove(PANES_KEY)

    def _choose_scale(self, _index: int) -> None:
        """Store the chosen scale, and offer the restart it needs to show.

        Qt reads the scale factor once, while the QApplication is being made,
        and gives nothing that changes it afterwards. So this cannot redraw
        what is already on screen. Saying that and offering the restart is
        the honest version of a control that would otherwise look broken.
        """
        chosen = self.scale_box.currentData()
        if chosen == uiscale.stored():
            return
        uiscale.set_stored(chosen)

        box = QMessageBox(self)
        box.setWindowTitle("Nightreign Helper")
        box.setIcon(QMessageBox.Question)
        box.setText(
            f"The interface is drawn at {self.scale_box.currentText()} from "
            f"the next launch."
        )
        # What a restart costs, in the player's terms. Relics, builds,
        # favourites and artwork are in the settings and come straight back;
        # the armament tiles and the switched-on conditions are session state
        # by design, and would start again from the Nightfarer's default.
        box.setInformativeText(
            "Your relics, saved builds and favourites are kept. The armament "
            "tiles and any conditions you have switched on last only for the "
            "run of the program, and would start again."
        )
        restart = box.addButton("Restart now", QMessageBox.AcceptRole)
        box.addButton("Later", QMessageBox.RejectRole)
        box.exec()
        if box.clickedButton() is restart:
            self._restart()

    def _restart(self) -> None:
        """Start this program again and leave.

        Frozen, the executable is its own launcher and takes no arguments of
        ours; from a checkout it is the interpreter that has to be started,
        with the script it was given. Nothing is written on the way out that
        is not written already -- every build is stored as it changes.
        """
        if getattr(sys, "frozen", False):
            arguments = []
        else:
            arguments = [os.path.abspath(sys.argv[0]), *sys.argv[1:]]
        if QProcess.startDetached(sys.executable, arguments):
            QApplication.quit()
            return
        QMessageBox.information(
            self, "Nightreign Helper",
            "This could not restart itself. Close it and open it again, and "
            "the new scale will be in place."
        )

    def _sync_shortcut_button(self) -> None:
        """Label the button for what it will do, not for what it is."""
        if not shortcut.available():
            self.shortcut_button.setVisible(False)
            return
        on = shortcut.exists()
        self.shortcut_button.setText(
            "  ✓ In Start Menu  " if on else "  ★ Add to Start Menu  "
        )
        self.shortcut_button.setToolTip(
            f"Remove {shortcut.SHORTCUT_NAME} from your Start Menu"
            if on else
            "Put a shortcut in your Start Menu so this can be launched by "
            "name. Your account only — no admin rights, nothing installed."
        )
        self.shortcut_button.setStyleSheet(
            f"QToolButton {{ color: {ACCENT if on else MUTED}; "
            f"font-size: 11px; border: none; padding: 2px 4px; }}"
            f"QToolButton:hover {{ color: {ACCENT}; }}"
        )

    def _toggle_shortcut(self) -> None:
        error = shortcut.remove() if shortcut.exists() else shortcut.create()
        self._sync_shortcut_button()
        if error:
            QMessageBox.warning(
                self, "Start Menu",
                f"The Start Menu entry could not be changed.\n\n{error}",
            )

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
        # Saved builds are per Nightfarer, so the list and the strip both
        # belong to whoever is selected.
        self.refresh_build_list(
            keep=chalices.selected_build(self.heroes[index]["id"]))
        self.refresh_vessel_strip()

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

    ROW_SLOT = 22

    def _vessel_row_art(self, vessel: dict, items=None, worn: bool = False,
                        selected: bool = False):
        """A vessel's own icon followed by its slots, as one row image.

        Reading a vessel's colours off a letter code -- "R B Y" -- means
        translating in your head every time. Drawing the slots is what the
        game does, and the selected vessel shows what is actually sitting in
        them, which is the thing the list could never say before.

        `worn` marks the chalice the game has equipped, with a mark on the
        vessel rather than words after its name: the name is what the list is
        read for, and a label pushed the longer names out of sight.

        `selected` flips that mark dark. The row highlight is the same accent
        the mark was drawn in -- exactly, #c8a45c on both -- so on the row the
        player had open the mark was gold on gold and only its outline showed.
        That is the row it matters on most: the equipped chalice is the one
        open after an import and on a Nightfarer's first visit.
        """
        cell = self.chalice_list.iconSize().height()
        colours = list(vessel.get("slots", []))
        if self.deep_check.isChecked():
            colours += list(vessel.get("deep_slots") or [])
        gap = 5
        width = cell + gap + len(colours) * (self.ROW_SLOT + 2)
        art = QPixmap(width, cell)
        art.fill(Qt.transparent)
        painter = QPainter(art)
        base = self.icons.item(vessel.get("icon")) if self.icons else None
        if base is not None:
            base = base.scaled(cell, cell, Qt.KeepAspectRatio,
                               Qt.SmoothTransformation)
            painter.drawPixmap(0, (cell - base.height()) // 2, base)
        top = (cell - self.ROW_SLOT) // 2
        for i, colour in enumerate(colours):
            owned = items[i] if items and i < len(items) else None
            painter.drawPixmap(cell + gap + i * (self.ROW_SLOT + 2), top,
                               slot_chip(self.icons, colour, owned,
                                         self.ROW_SLOT))
        if worn:
            # Drawn rather than taken from the game: the menus mark the worn
            # chalice by moving it, not with a sprite this program could
            # borrow, so this mark is the planner's own.
            dot = 10
            painter.setRenderHint(QPainter.Antialiasing, True)
            fill, edge = ((QColor("#14150f"), QColor("#e6d3a3"))
                          if selected else (QColor(ACCENT), QColor("#14150f")))
            painter.setPen(QPen(edge, 1))
            painter.setBrush(fill)
            painter.drawEllipse(cell - dot - 1, 1, dot, dot)
        painter.end()
        return art

    def _relics_by_handle(self) -> dict:
        """Owned relics keyed by their save handle, for drawing rows."""
        if self.owned is None:
            return {}
        return {r.handle: r for r in self.owned.relics
                if getattr(r, "handle", None) is not None}

    def _stored_relics(self, hero_id: int, vessel_id: int, by_handle: dict):
        """What one chalice holds, read from its stored build.

        Rows other than the selected one have no live slots to read, so the
        stored build is the only account of what is in them.
        """
        _vessel, _deep, keys = chalices.load(hero_id, vessel_id)
        if not keys:
            return None
        out = []
        for key in (list(keys) + [""] * 6)[:6]:
            handle, _roll = chalices.split_key(key)
            out.append(by_handle.get(handle) if handle is not None else None)
        return out

    def _worn_vessel_id(self) -> int | None:
        """The chalice the game has equipped on this Nightfarer.

        Read from the save's own record -- the vessel id in the Nightfarer's
        loadout group header -- and not from which chalice holds relics: a
        Nightfarer can be wearing an empty one while built ones sit beside it.
        """
        if (getattr(self, "owned", None) is None
                or not getattr(self, "hero_vessels", None)):
            return None
        worn = self.owned.selected_loadout(self.current_hero()["id"])
        return worn.vessel_id if worn is not None else None

    def refresh_vessel_rows(self) -> None:
        """Redraw every vessel row, not only the selected one.

        The Deep of Night switch changes how many slots a chalice shows, and
        redrawing just the selected row left every chalice the player had not
        clicked on still drawing three -- so turning Deep on appeared to add
        slots to one chalice and not the rest. The relics come from each
        chalice's stored build, so a row says what is in it without being
        opened.
        """
        if not getattr(self, "hero_vessels", None):
            return
        hero_id = self.current_hero()["id"]
        by_handle = self._relics_by_handle()
        current = self.chalice_list.currentRow()
        for row in range(self.chalice_list.count()):
            item = self.chalice_list.item(row)
            vessel = item.data(Qt.UserRole)
            if not vessel:
                continue
            if row == current:
                items = [s.current_relic() for s in self._visible_slots()]
            else:
                items = self._stored_relics(hero_id, vessel["id"], by_handle)
            item.setIcon(QIcon(self._vessel_row_art(
                vessel, items, vessel["id"] == self._worn_vessel_id(),
                row == current)))

    def refresh_vessel_row(self) -> None:
        """Redraw the selected vessel's row so its slots show what is in them."""
        row = self.chalice_list.currentRow()
        item = self.chalice_list.item(row) if row >= 0 else None
        vessel = item.data(Qt.UserRole) if item is not None else None
        if not vessel:
            return
        slots = self._visible_slots()
        # The worn mark has to be passed here too. Without it this redraw --
        # which runs on every slot change -- quietly rubbed the mark off the
        # selected row, and the equipped chalice is the row most likely to be
        # selected, so the mark appeared to not work at all.
        item.setIcon(QIcon(self._vessel_row_art(
            vessel, [s.current_relic() for s in slots],
            vessel["id"] == self._worn_vessel_id(), True)))

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

        worn_id = self._worn_vessel_id()
        first_row = None
        for group, vessels in ((f"{hero['name']}'s own", own),
                               ("Shared Grails — any Nightfarer", grails)):
            if not vessels:
                continue
            add_separator(group)
            for vessel in vessels:
                item = QListWidgetItem(vessel["name"])
                item.setData(Qt.UserRole, vessel)
                item.setIcon(QIcon(self._vessel_row_art(
                    vessel, None, vessel["id"] == worn_id)))
                slots = " ".join(
                    model.COLOUR_NAMES.get(c, "?")[0] for c in vessel["slots"]
                )
                tip = f"{vessel['name']} — slots {slots}"
                if vessel["id"] == worn_id:
                    # The mark is on the vessel, not after the name: the name
                    # is what the list is read for, and a label pushed the
                    # longer chalice names out of the panel.
                    tip += "\nEquipped in game"
                item.setToolTip(tip)
                self.chalice_list.addItem(item)
                if first_row is None:
                    first_row = self.chalice_list.count() - 1
        self.chalice_list.blockSignals(False)

        # The first time a Nightfarer is opened, their chalices are read out
        # of the save and the equipped one is the one shown. Until this ran on
        # its own, a Nightfarer nobody had pressed the button on showed eleven
        # empty chalices, and pressing it changed the whole list at once --
        # the same list, moments apart, telling two different stories.
        #
        # It happens once. From then on the chalice the player last had open
        # is what reopens, across sessions, because that choice is theirs;
        # Load equipped is how the save is asked again.
        if (self.owned is not None
                and not chalices.imported(hero["id"])
                and self.owned.loadouts_for(hero["id"])):
            chalices.set_imported(hero["id"])
            self.load_equipped()
            return

        # The build this Nightfarer was last left holding, if there is one.
        # Restored in the same order load_equipped uses -- vessel and mode
        # first, because both rebuild the slots and would otherwise empty them
        # again straight after they were filled.
        view_vessel, view_deep = chalices.view(hero["id"])
        vessel_id, deep_on, slot_keys = chalices.load(hero["id"], view_vessel)
        # The view wins for both: an empty chalice with Deep on stores no
        # build, and its choice would otherwise be lost on the next launch.
        if view_vessel is not None:
            vessel_id, deep_on = view_vessel, view_deep
        saved_row = None
        if vessel_id is not None:
            saved_row = next(
                (i for i in range(self.chalice_list.count())
                 if (self.chalice_list.item(i).data(Qt.UserRole) or {}).get("id")
                 == vessel_id),
                None,
            )

        self._restoring = True
        try:
            if saved_row is not None:
                self.chalice_list.setCurrentRow(saved_row)
            if saved_row is not None or view_vessel is not None:
                self.deep_check.blockSignals(True)
                self.deep_check.setChecked(bool(deep_on))
                self.deep_check.blockSignals(False)
            if saved_row is None and first_row is not None:
                self.chalice_list.setCurrentRow(first_row)
            self.apply_chalice()

            # Emptied first, every time. This whole block runs with the
            # restoring guard up, so apply_chalice does not set the slots
            # from the chalice -- and rebuilding a slot keeps the relic that
            # was in it when the colour still fits. Changing Nightfarer
            # therefore carried relics across, and the write that followed
            # stored them: a Nightfarer whose chalice is empty in the game
            # inherited whatever the Nightfarer before them had on.
            slots = list(self.base_slots) + list(self.deep_slots)
            for slot in slots:
                slot.select_saved("")

            if saved_row is not None and slot_keys:
                for slot, key in zip(slots, slot_keys):
                    slot.select_saved(key)
            self._mark_vessel_applied()
        finally:
            self._restoring = False
        self._settle_slots()
        # Drawn once the Deep switch and the slots have settled, so every row
        # shows the right number of slots and what that chalice holds.
        self.refresh_vessel_rows()
        self.recompute()

    def _store_chalice(self) -> None:
        """Write down what this Nightfarer is holding, for the next session."""
        self.refresh_vessel_strip()
        # Never mid-apply: see apply_chalice. The slots and the chosen vessel
        # disagree until the apply finishes, and apply_chalice stores itself
        # once it has.
        if getattr(self, "_applying", False):
            return
        if self._restoring or not getattr(self, "hero_vessels", None):
            return
        vessel = self.current_vessel()
        slots = list(self.base_slots) + list(self.deep_slots)
        keys = [slot.saved_key() for slot in slots]
        # The default vessel with nothing in it is not a build worth keeping.
        # Storing it anyway is what made Reset Chalice look as though it had
        # not worked: the reset emptied everything and the write that followed
        # put the starting state straight back as a saved one.
        # The view is always recorded: which chalice is open and whether Deep
        # of Night is on survive even an empty vessel, because they are what
        # the player was looking at rather than what they had equipped.
        chalices.save_view(self.current_hero()["id"],
                           vessel["id"] if vessel else None,
                           self.deep_check.isChecked())
        # The build itself is not. An empty set of slots is never written
        # over a stored one -- Reset Chalice is how a build is forgotten,
        # deliberately and per vessel.
        if not any(keys):
            return
        chalices.save(
            self.current_hero()["id"],
            vessel["id"] if vessel else None,
            self.deep_check.isChecked(),
            keys,
        )

    # -- saved builds ----------------------------------------------------

    def _visible_slots(self) -> list:
        """The slot panels the current vessel actually exposes."""
        slots = list(self.base_slots)
        if self.deep_check.isChecked():
            slots += list(self.deep_slots)
        return slots

    def refresh_vessel_strip(self) -> None:
        """Redraw the small slot row from the vessel and what is in it."""
        if not hasattr(self, "vessel_strip"):
            return
        slots = self._visible_slots()
        self.vessel_strip.show_slots([s.colour for s in slots],
                                     [s.current_relic() for s in slots])
        self.refresh_vessel_row()

    def refresh_build_list(self, keep: str | None = None) -> None:
        """Rebuild the build picker for the current Nightfarer.

        The equipped build is always offered first and is never stored here:
        it is read from the save, so it cannot go stale. Hidden builds drop
        out of the list but keep their entry, which is what "hidden, not
        deleted" has to mean.
        """
        if not hasattr(self, "build_box"):
            return
        hero_id = self.current_hero()["id"]
        hidden = chalices.hidden_builds(hero_id)
        names = ([chalices.EQUIPPED_NAME, chalices.UNSAVED_NAME]
                 + chalices.build_names(hero_id))
        if keep is None:
            # No explicit target means "whatever was selected", and on the
            # first build of the list that is what the last session left.
            keep = self.build_box.currentData() or chalices.selected_build(
                hero_id)
        # A hidden build is listed while the player asks for it, and while it
        # is the one selected. Without the first of those, hiding was a thing
        # that could not be undone.
        show_hidden = getattr(self, "show_hidden_check", None)
        showing = show_hidden is not None and show_hidden.isChecked()

        self.build_box.blockSignals(True)
        self.build_box.clear()
        for name in names:
            if name in hidden and name != keep and not showing:
                continue
            label = f"{name}  (hidden)" if name in hidden else name
            self.build_box.addItem(label, name)
        index = self.build_box.findData(keep)
        self.build_box.setCurrentIndex(index if index >= 0 else 0)
        self.build_box.blockSignals(False)
        self._sync_build_buttons()

    def _sync_build_buttons(self) -> None:
        name = self.build_box.currentData()
        # The equipped build belongs to the save, not to this program: it can
        # be looked at and hidden, never deleted or written over. The unsaved
        # entry is not a build at all -- it is the list's way of saying the
        # slots are nobody's saved work -- so there is nothing to delete and
        # nothing to hide.
        unsaved = name == chalices.UNSAVED_NAME
        self.delete_build_button.setEnabled(
            bool(name) and name not in chalices.RESERVED_NAMES)
        hidden = name in chalices.hidden_builds(self.current_hero()["id"])
        self.hide_build_button.setText("Unhide" if hidden else "Hide")
        self.hide_build_button.setEnabled(bool(name) and not unsaved)

    def _on_build_chosen(self, _index: int) -> None:
        name = self.build_box.currentData()
        if not name:
            return
        chalices.set_selected_build(self.current_hero()["id"], name)
        self._sync_build_buttons()
        if name == chalices.UNSAVED_NAME:
            # A label, not a build. Picking it says "these slots are not one
            # of my saved builds" and changes nothing on screen: emptying them
            # is Reset Chalice's job, and doing it from a name in a list would
            # throw away work nobody asked to lose.
            return
        if name == chalices.EQUIPPED_NAME:
            self.load_equipped()
            return
        hero_id = self.current_hero()["id"]
        vessel_id, deep, keys = chalices.load_build(hero_id, name)
        self._apply_stored_build(vessel_id, deep, keys)

    def _apply_stored_build(self, vessel_id, deep, keys) -> None:
        """Put a stored build into the slots, the way a restore does."""
        self._restoring = True
        try:
            self.deep_check.blockSignals(True)
            self.deep_check.setChecked(bool(deep))
            self.deep_check.blockSignals(False)
            if vessel_id is not None:
                for i in range(self.chalice_list.count()):
                    entry = self.chalice_list.item(i).data(Qt.UserRole)
                    if entry is not None and entry["id"] == vessel_id:
                        self.chalice_list.setCurrentRow(i)
                        break
            self.apply_chalice()
            slots = list(self.base_slots) + list(self.deep_slots)
            for index, slot in enumerate(slots):
                key = keys[index] if index < len(keys) else ""
                if not slot.select_saved(key):
                    # A saved build can name a relic that has since been
                    # melted. The slot it was stored for is empty then, not
                    # left holding whatever the build before it had there.
                    slot.clear_relic()
            self._mark_vessel_applied()
        finally:
            self._restoring = False
        self._settle_slots()
        self.recompute()
        self._store_chalice()

    def _save_build(self) -> None:
        suggested = self.build_box.currentData() or ""
        if suggested in chalices.RESERVED_NAMES:
            suggested = ""
        name, ok = QInputDialog.getText(
            self, "Save build", "Name this build:", text=suggested)
        name = (name or "").strip()
        if not ok or not name:
            return
        if name in chalices.RESERVED_NAMES:
            QToolTip.showText(
                QCursor.pos(),
                "That name belongs to the build your save has equipped."
                if name == chalices.EQUIPPED_NAME else
                "That name means the slots hold no saved build.")
            return
        vessel = self.current_vessel()
        slots = list(self.base_slots) + list(self.deep_slots)
        chalices.save_build(
            self.current_hero()["id"], name,
            vessel["id"] if vessel else None,
            self.deep_check.isChecked(),
            [slot.saved_key() for slot in slots],
        )
        chalices.set_selected_build(self.current_hero()["id"], name)
        self.refresh_build_list(keep=name)

    def _delete_build(self) -> None:
        name = self.build_box.currentData()
        if not name or name == chalices.EQUIPPED_NAME:
            return
        chalices.delete_build(self.current_hero()["id"], name)
        chalices.set_selected_build(self.current_hero()["id"],
                                    chalices.EQUIPPED_NAME)
        self.refresh_build_list(keep=chalices.EQUIPPED_NAME)

    def _toggle_hidden_build(self) -> None:
        name = self.build_box.currentData()
        if not name:
            return
        hero_id = self.current_hero()["id"]
        hidden = name in chalices.hidden_builds(hero_id)
        chalices.set_hidden(hero_id, name, not hidden)
        if not hidden:
            # Said at the moment of hiding, because that is the moment the
            # player has to learn there is a way back. Finding out afterwards
            # meant not finding out at all.
            QToolTip.showText(
                QCursor.pos(),
                'Hidden. Tick "Show hidden" to list it again.')
        # Hiding the one on screen leaves it selected until something else is
        # chosen -- dropping it out from under the player would look like the
        # build had been deleted, which is the one thing Hide must not do.
        self.refresh_build_list(keep=name)

    def reset_chalice(self) -> None:
        """Empty this vessel and forget the build stored for it.

        Scoped to the vessel on screen now that each keeps its own build --
        clearing every vessel's work from one button would be a far bigger
        thing than the label promises.
        """
        vessel = self.current_vessel()
        chalices.clear(self.current_hero()["id"],
                       vessel["id"] if vessel else None)
        self._restoring = True
        try:
            self.deep_check.blockSignals(True)
            self.deep_check.setChecked(False)
            self.deep_check.blockSignals(False)
            # Row 0 is the group caption, which cannot be selected; the first
            # real vessel is whatever follows it.
            for i in range(self.chalice_list.count()):
                if self.chalice_list.item(i).data(Qt.UserRole) is not None:
                    self.chalice_list.setCurrentRow(i)
                    break
            self.apply_chalice()
            for slot in list(self.base_slots) + list(self.deep_slots):
                slot.select_saved("")
            self._mark_vessel_applied()
        finally:
            self._restoring = False
        # The lists were drawn up while the slots still held the build that
        # has just been thrown away, so they are missing every relic that was
        # in it. Nothing else here can put them right: the next rebuild only
        # happens when a relic changes, and there is nothing left to change.
        self._settle_slots()
        self.recompute()
        # The picker went on naming the build that was loaded before the
        # reset. An emptied chalice still read as "Test", clicking that entry
        # put it back, and the reset looked as though it had half worked --
        # so the list now has an entry for exactly this state, and lands on
        # it.
        chalices.set_selected_build(self.current_hero()["id"],
                                    chalices.UNSAVED_NAME)
        self.refresh_build_list(keep=chalices.UNSAVED_NAME)

    def current_vessel(self) -> dict | None:
        """The vessel selected in the list, ignoring the caption rows."""
        item = self.chalice_list.currentItem()
        vessel = item.data(Qt.UserRole) if item is not None else None
        if vessel is None:
            vessel = self.hero_vessels[0] if self.hero_vessels else None
        return vessel

    def _on_deep_toggled(self, *_args) -> None:
        """The Deep switch changes every chalice, so every row is redrawn."""
        self.apply_chalice()
        self.refresh_vessel_rows()

    def apply_chalice(self) -> None:
        if not self.hero_vessels:
            return
        # This is not re-entrant. It rebuilds the slots, and rebuilding a slot
        # can put a relic in it, which is a change like any other and comes
        # back round here. Nesting is never useful -- the outer call finishes
        # by drawing and recomputing anyway -- and left unguarded the nesting
        # grew until the program died of a stack overflow while stepping
        # through one Nightfarer's chalices in order.
        if getattr(self, "_applying", False):
            return
        # Whatever this call changes -- vessel, Deep of Night, slot colours --
        # the strip is drawn from it, so it is refreshed at the end below.
        vessel = self.current_vessel()
        if vessel is None:
            return
        deep_on = self.deep_check.isChecked()
        self._applying = True
        try:
            self._apply_chalice(vessel, deep_on)
        finally:
            self._applying = False
        # Only now, with the slots holding this chalice and nothing of the
        # one before it. Rebuilding a slot can emit, and a store that ran
        # part-way through wrote the old chalice's relics under the new
        # chalice's name: the vessel id had already changed while the slots
        # had not caught up. That is how a chalice empty in the game ended up
        # owning a relic nobody put there.
        self._store_chalice()
        # The whole list, because selection moved: the row being left has to
        # lose the light mark and the row arrived at has to gain it, and only
        # one of the two is the current row. Chip drawing is cached, so this
        # costs little and only runs when the chalice or the mode changes.
        self.refresh_vessel_rows()

    def _apply_chalice(self, vessel: dict, deep_on: bool) -> None:
        """The body of apply_chalice, held apart so it cannot nest."""

        owned = self.owned
        # Whether this is a different chalice from the one the slots are
        # holding, asked before anything is touched: both the emptying just
        # below and the restore at the end turn on the answer.
        changed = getattr(self, "_applied_vessel", None) != vessel["id"]
        # On a change of chalice the slots still hold the one being left, and
        # they are emptied before the lists are rebuilt rather than after. A
        # list drawn up around relics that are on their way out treats them as
        # taken, and the incoming chalice's own build could then not be put
        # back: its relic was "already worn" by the chalice it was replacing
        # (QA-014).
        if changed and not self._restoring:
            for slot in self.base_slots + self.deep_slots:
                slot.clear_relic()
        # Slots always list everything they can hold. Narrowing them from
        # outside is what made an equipped relic disappear.
        for i, slot in enumerate(self.base_slots):
            slot.set_colour(vessel["slots"][i], self.effect_list, owned,
                            hero_name=self.current_hero()["name"])
        for i, slot in enumerate(self.deep_slots):
            slot.set_colour(vessel["deep_slots"][i], self.effect_list, owned,
                            hero_name=self.current_hero()["name"])
            slot.setVisible(deep_on)
        self.deep_heading.setVisible(deep_on)

        # set_colour above does NOT empty the slots. It repopulates them and
        # deliberately keeps the relic that was in one if that relic still
        # fits -- which is what the Deep switch needs, and is wrong the
        # moment the chalice itself changes. Every slot the new
        # chalice happens to share a colour with the old one kept the old
        # relic, and the write that followed stored it: opening a Grail whose
        # slots are all Yellow inherited the Yellow relic from the chalice
        # before it, and the Grail then owned a relic nobody put there.
        #
        # So on a change of chalice the slots are set from that chalice's own
        # stored build and from nothing else, empty included.
        #
        # The note of which chalice was last applied is only made when the
        # slots were actually set from it. Marking it regardless meant a pass
        # that skipped the restore still claimed the chalice as applied, so
        # the next pass saw no change and never cleared -- one relic from the
        # chalice before survived, and was stored.
        if not self._restoring:
            self._applied_vessel = vessel["id"]
            self._restore_vessel_build(vessel, clear=changed)

        self.refresh_vessel_strip()
        self.recompute()

    def _restore_vessel_build(self, vessel: dict, clear: bool = False) -> None:
        """Put back whatever this vessel was last holding.

        With `clear`, a vessel that has no stored build has its slots emptied
        rather than left alone -- the chalice has just changed, and whatever
        is in the slots belongs to the chalice being left.
        """
        _stored_id, deep, keys = chalices.load(
            self.current_hero()["id"], vessel["id"])
        if not any(keys) and not clear:
            return
        self._restoring = True
        try:
            # The Deep of Night switch is left exactly as the player set it.
            # Restoring the stored flag here fought the switch: turning Deep
            # off reloaded a build that had it on and turned it straight back.
            #
            # Every slot is filled regardless, the hidden Deep ones included,
            # so toggling the switch reveals the full array instead of an
            # empty half. Only the visible ones reach the totals --
            # selected_effects() reads active_slots().
            slots = list(self.base_slots) + list(self.deep_slots)
            for index, slot in enumerate(slots):
                key = keys[index] if index < len(keys) else ""
                if not slot.select_saved(key):
                    # The stored relic is not one this slot can be given --
                    # melted since, or belonging to another save. Whatever the
                    # slot is holding belongs to the chalice being left, so it
                    # goes: keeping it would make that relic part of this
                    # chalice's build at the next store. select_saved has
                    # always said so, and nobody read the answer.
                    slot.clear_relic()
        finally:
            self._restoring = False
        self._settle_slots()

    def _settle_slots(self) -> None:
        """Bring the slots into agreement, once a restore has filled them.

        Two things are settled here, and both come of a board being written to
        while it was being read.

        A build stored before ownership was enforced can name one physical
        relic in two slots. Restored as written, both slots showed it and both
        were counted (measured: Endurance 5 where the relic gives 4), and the
        doubling was then resolved by the *next* change to any slot -- which
        emptied the lower-numbered of the two, elsewhere on the screen, with
        nothing said anywhere (QA-015, DR-002). It is resolved here instead:
        at the restore, once, and the slot that loses the relic says why.

        Then every list is rebuilt, because they were drawn up before the
        slots were set and each was written down against a board that no
        longer exists.
        """
        worn_in: dict = {}
        for slot in self.base_slots + self.deep_slots:
            # An empty slot and a custom relic both answer None: the one has
            # nothing to clash with, the other is imaginary by design and may
            # be planned into every slot.
            key = inventory.copy_key(slot.current_relic())
            if key is None:
                continue
            keeper = worn_in.setdefault(key, slot)
            if keeper is not slot:
                slot.clear_relic(f"Already worn in {keeper.slot_name()} — "
                                 "pick another relic for this slot.")
        for slot in self.base_slots + self.deep_slots:
            slot.populate()

    def _mark_vessel_applied(self) -> None:
        """Note the chalice the slots now hold, after a restore has set them.

        `_apply_chalice` makes this note only when it set the slots itself,
        which it does not do while a restore is in progress -- and every
        restoring path sets them afterwards from its own authority: the save,
        a stored build, or an emptying. Leaving the note alone through all of
        that left it naming the chalice the player was on *before*, and one
        click later that was read as "the chalice has not changed": the slots
        were left exactly as they were, and Load equipped's relics were stored
        under a chalice that is empty in the game.

        The mirror of this was a real bug too, which is why the note is not
        simply made every time: a pass that changes the chalice and does
        *not* set the slots must not claim it, or the next pass sees no change
        and never clears.
        """
        vessel = self.current_vessel()
        self._applied_vessel = vessel["id"] if vessel else None

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

    def _relics_taken_elsewhere(self, asking: RelicSlot) -> set:
        """The physical relics the other slots are already holding.

        Asked by a slot while it works out what it can offer. The asking slot
        is skipped, or a slot would hide the very relic sitting in it.

        Every slot is considered, the hidden Deep ones included: they hold
        Deep relics, which no ordinary slot can take anyway, so the two
        never contend -- and a Deep slot that is out of sight still has a
        relic in it, which is exactly the case where a doubled relic would go
        unnoticed.

        Not while a restore is running. The slots are then half the build
        being left and half the one arriving, and an answer drawn from that
        mixture withheld from the incoming build exactly the relics it was
        about to be given (QA-014). The board is settled once, at the end of
        the restore, by _settle_slots.
        """
        if self._restoring:
            return set()
        taken = set()
        for slot in self.base_slots + self.deep_slots:
            if slot is asking:
                continue
            key = inventory.copy_key(slot.current_relic())
            if key is not None:
                taken.add(key)
        return taken

    def _relic_changed(self) -> None:
        """A relic moved, so both the totals and the other slots' lists change.

        The lists have to be rebuilt here and not only when the chalice
        changes: what a slot may offer depends on what the other five are
        holding at this moment, and a list built before the choice was made
        would still be offering the relic that has just been taken.

        The rebuild is about ownership and nothing else. It used to hand each
        slot the term last typed into the picker, which had nothing to do with
        the question being asked and everything to do with QA-013.
        """
        for slot in self.base_slots + self.deep_slots:
            slot.populate()
        self.recompute()

    # Populated by recompute(), read by the click-to-break-down popup.
    last_sources: dict = {}
    last_rates: dict = {}

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

        weapon_class = ar.get("class")
        for field_name, value in ar["rates"].items():
            rows.append(f"&nbsp;&nbsp;{model.label_for(field_name)} &nbsp; "
                        f"<b>{(value - 1.0) * 100:+.1f}%</b>")
            # Which relics produced that multiplier, in the same order and
            # wording the other breakdowns use. A buff scoped to melee or
            # ranged armaments is filed under its own key, so both are read:
            # the flat sources, then the ones that apply because of what this
            # armament is.
            entries = list(self.last_sources.get(field_name, []))
            if weapon_class:
                scoped = (f"{model.WEAPON_CLASS_PREFIX}{weapon_class}:"
                          f"{field_name}")
                entries += [(f"{name} — {weapon_class} armaments only", own)
                            for name, own in
                            self.last_sources.get(scoped, [])]
            for name, own in entries:
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
            tile_rating = None
            if slot.filled:
                tile_rating = weapons.rate(slot.weapon, build.attributes,
                                           self.data, slot.tier)
            self.weapon_tiles[index].show_slot(
                slot, tile_rating, active=index == self.active_weapon,
                effects=self.data["effects"])

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

        # The figure itself is not computed here. It is the one piece of
        # domain arithmetic that had ended up inside the window, and the build
        # advisor needs to ask for it without drawing anything, so it lives in
        # nrplanner/damage.py and this method formats what comes back.
        rating = attack_rating(
            weapon, slot.tier, build, self.data,
            starting_armament=is_starting_armament(
                weapon, self.current_hero(), self.active_weapon),
        )
        before, after = rating.before, rating.after
        boosted = rating.per_type
        base_total = rating.base_total
        final_total = rating.final_total
        delta = final_total - base_total
        self.last_ar = rating.figures()

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
        # frost" is the reason the attack rating above is 15% lower **on slot
        # 1**, and the buildup is what you are buying with it.
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

        note = f"{self.owned.relic_count} relics in {self.owned.source}"
        if self.owned.loadouts:
            note += f", {len(self.owned.loadouts)} stored builds"
        elif self.owned.loadout_error:
            # A save whose relics read but whose builds do not is a specific
            # failure with a specific cause, and reporting "0 builds" without
            # the cause left it undiagnosable from a bug report.
            note += f" — no stored builds could be read: {self.owned.loadout_error}"
        else:
            note += " — this save stores no builds yet"
        self.owned_label.setText(note)
        # The folder is named after the Steam account id, so it is offered on
        # hover rather than printed where every screenshot would carry it.
        self.owned_label.setToolTip(self.owned.folder)
        if not initial:
            # reload_chalices, not apply_chalice: the relics have just changed
            # underneath the slots, so the saved build has to be matched
            # against the new inventory rather than left pointing at the old.
            self.reload_chalices()

    def load_equipped(self) -> None:
        """Load the current Nightfarer's equipped loadout out of the save.

        Reads the vessel that Nightfarer has selected and the relics sitting in
        it, so the planner starts from the real build rather than an empty one.
        """
        if self.owned is None:
            self.owned_label.setText("No save loaded, so there is nothing to import.")
            return

        hero = self.current_hero()
        entries = self.owned.loadouts_for(hero["id"])
        # Every chalice is imported, not only the one being worn. The save
        # stores all of them, and a player who has built several and happens
        # to have an empty one equipped used to get an empty planner back.
        imported = 0
        for entry in entries:
            keys = [chalices.slot_key(r) for r in entry.relics]
            keys += [""] * (6 - len(keys))
            if any(keys):
                chalices.save(hero["id"], entry.vessel_id, entry.deep_used, keys)
                imported += 1
            else:
                # Empty in the game means empty here: this button says the
                # save is the truth. Named builds are stored separately and
                # are not touched, so planning work survives an import.
                chalices.clear(hero["id"], entry.vessel_id)

        # The vessel shown is the one actually worn, even when it is empty:
        # the button says "equipped", and opening a different chalice because
        # it happens to have relics in it would misreport the game. The empty
        # case is explained in the note instead, and the other chalices are
        # already filled in by then.
        loadout = self.owned.selected_loadout(hero["id"])
        if loadout is None:
            if self.owned.loadout_error:
                self.owned_label.setText(
                    "This save's stored builds could not be read: "
                    f"{self.owned.loadout_error}"
                )
            else:
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

        # What is on screen after this is the save's build, so the picker has
        # to say so. It kept naming whichever saved build was chosen before,
        # which then described a chalice it had nothing to do with.
        chalices.set_selected_build(hero["id"], chalices.EQUIPPED_NAME)
        self.refresh_build_list(chalices.EQUIPPED_NAME)

        # The guard goes up before the row changes, not after. Changing the
        # row fires the list's own handler, which stores what the slots hold
        # -- and at that moment they still hold the chalice being left, while
        # the vessel id has already moved on. That wrote one chalice's relics
        # under another one's name: importing a Nightfarer whose equipped
        # chalice is empty gave it whatever was on screen beforehand.
        #
        # It also holds off the per-vessel restore inside apply_chalice: the
        # save is the authority here, and restoring would put the stored
        # build back and take the save's Deep of Night setting with it.
        self._restoring = True
        try:
            # Set the vessel and mode first: both rebuild the slots, which
            # would otherwise discard the relics just put in them.
            self.chalice_list.setCurrentRow(row)
            # Deep of Night is only ever switched ON here, never off. The
            # save says whether the equipped build uses the extra slots, but
            # the switch is also how the player chooses what to look at:
            # turning it on and then importing used to turn it straight back
            # off. Slots are filled either way, so nothing is lost by
            # leaving it on.
            if loadout.deep_used and not self.deep_check.isChecked():
                self.deep_check.blockSignals(True)
                self.deep_check.setChecked(True)
                self.deep_check.blockSignals(False)
            self.apply_chalice()
        finally:
            self._restoring = False

        slots = list(self.base_slots) + list(self.deep_slots)
        missing = 0
        for slot, item in zip(slots, loadout.relics):
            if not slot.select_handle(item.handle if item else None):
                missing += 1
                # The slot the save names a relic for is empty when that relic
                # cannot be placed, never left holding the one the chalice
                # before it had there.
                slot.clear_relic()
        # These slots are the equipped chalice's now, and the next click on
        # the chalice list has to know it. Without this, clicking back on the
        # chalice that was open *before* Load equipped counted as no change
        # at all: nothing cleared the slots, and the equipped build was
        # written into a chalice that is empty in the game.
        self._mark_vessel_applied()

        # Every row, not only the one on screen: the import has just filled
        # the other chalices, and they should say so without being clicked.
        self.refresh_vessel_rows()
        vessel_name = self.chalice_list.item(row).data(Qt.UserRole)["name"]
        filled = sum(1 for r in loadout.relics if r is not None)
        count = f"{imported} {'chalice' if imported == 1 else 'chalices'}"
        if filled:
            note = (f"Loaded {hero['name']} — {count}, showing the equipped "
                    f"{vessel_name} with {filled} relics"
                    f"{' (Deep of Night)' if loadout.deep_used else ''}.")
        elif imported:
            note = (f"Loaded {hero['name']} — {count}. The equipped "
                    f"{vessel_name} is empty in game; the others are in the "
                    "list on the left.")
        else:
            note = (f"Loaded {hero['name']} — every chalice is empty in game.")
        if missing:
            # Reached when a slot could not be given the relic the save
            # names for it: the only relic the slot will not take is one
            # another slot is already holding.
            note += f" {missing} could not be placed; clear the search and retry."
        self.owned_label.setText(note)
        self._settle_slots()
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

    def _sync_situational(self, entries: list) -> None:
        """Draw one switch per gated effect, rebuilding only when the set changes.

        recompute() runs on every keystroke that reaches it, and rebuilding the
        rows each time would take the count box out from under the cursor
        mid-number. The rows are therefore kept while the same effects are
        equipped, and only their values are pushed back.
        """
        wanted = [e.effect_id for e in entries]
        if wanted != list(self.situational_rows):
            while self.qual_rows_layout.count():
                item = self.qual_rows_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self.situational_rows = {}
            for entry in entries:
                row = SituationalRow(
                    entry, self.declared.get(entry.effect_id, 0),
                    self._situational_changed,
                )
                self.situational_rows[entry.effect_id] = row
                self.qual_rows_layout.addWidget(row)
        self.qual_rows.setVisible(bool(entries))

        # An effect that is no longer equipped stops being declared, so putting
        # the same relic back on does not silently bring a stale count with it.
        for eid in list(self.declared):
            if eid not in self.situational_rows:
                del self.declared[eid]

    def _situational_changed(self) -> None:
        self.declared = {
            eid: row.value()
            for eid, row in self.situational_rows.items()
            if row.value() > 0
        }
        self.recompute()

    def _rebuild(self) -> model.Build:
        """Turn what is on screen into a build. The only call to the model.

        Everything that reaches a total is gathered in this one place: the
        relics in the slots, the effects the armaments rolled, the curses
        those relics carry, the weapon-type gates and whatever conditional
        effects the player has declared.

        A second caller with an argument list of its own is how the Weapons
        tab came to rank every armament in the game against a build three
        attributes away from the one on screen, with nothing on the window to
        say which was right (QA-001). So there is one caller, and everyone
        else is handed the result through current_build().
        """
        # Curses are part of the relic you equipped, so they count towards the
        # totals exactly as the good rolls do. Leaving them out meant a curse
        # reading "Reduced Dexterity and Faith -3" changed no attribute, which
        # made the sheet quietly wrong for every Deep of Night build.
        curses = [eff for _source, eff in self.selected_curses()]
        return model.compute(
            self.current_hero(), self.level_slider.value(),
            # Armament effects count towards the sheet alongside the relics.
            self.selected_effects() + self.weapon_effects() + curses,
            self.curves,
            # A weapon-type buff such as "Improved Axe Attack Power" is live
            # when any armament on the grid is of that type, so the gate is
            # tested against all six rather than only the active tile.
            weapon=self.active_slot().weapon,
            weapons_held=self.equipped_weapons(),
            declared=self.declared,
        )

    def current_build(self) -> model.Build:
        """The build every tab reads.

        Kept up to date by recompute(), which runs on every change that can
        move a number. Computed on the spot if something asks before the
        first recompute -- a tab built during startup, for instance.
        """
        if self._build is None:
            self._build = self._rebuild()
        return self._build

    def recompute(self) -> None:
        if not hasattr(self, "level_slider"):
            return
        # Every path that changes a vessel, a mode or a relic ends here, so
        # this is the one place the stored build has to be kept up to date.
        self._store_chalice()
        hero = self.current_hero()
        level = self.level_slider.value()
        self.level_label.setText(str(level))
        exact = hero["exact_levels"]
        self.level_note.setText(
            "Exact value from the game data."
            if level in exact
            else f"Interpolated — the game defines levels {', '.join(map(str, exact))}."
        )

        build = self._build = self._rebuild()

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
            # The `*AttackPowerRate` family is not a build-wide multiplier: it
            # is the "Starting armament inflicts frost / poison / blood loss"
            # penalty, and it reaches the starting armament alone. Reported from
            # play for 1.7.0, having previously read here as "All damage
            # -15.0%" against everything equipped. It is applied to slot 1 by
            # `_refresh_weapon_damage`, where its 15% is visible in that
            # weapon's own figure, so it is dropped from this section rather
            # than shown twice.
            shown_rates = {f: v for f, v in build.rates.items()
                           if f not in model.ELEMENT_ATTACK_POWER_RATES}
            # A buff that raises all five damage types by the same amount is one
            # buff, not five. Printing a row each turned a single relic into
            # five identical lines.
            family = model.ELEMENT_ATTACK_RATES
            present = [f for f in family if f in shown_rates]
            values = {round(shown_rates[f], 6) for f in present}
            if len(present) == len(family) and len(values) == 1:
                for f in present:
                    del shown_rates[f]
                # Linked to a real field so the click-through breakdown
                # still names the relics behind the number.
                shown_rates[f"{model.ALL_DAMAGE_PREFIX}{present[0]}"] = \
                    build.rates[present[0]]
            for fname, value in sorted(
                    model.collapse_by_label(shown_rates).items()):
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
            for fname, value in sorted(
                    model.collapse_by_label(build.other).items()):
                # Damage taken and resource costs read the other way round:
                # more of them is worse news, so the colour follows what the
                # figure means rather than its sign.
                helpful = (value <= 0 if model.is_better_lower(fname)
                           else value >= 0)
                colour = GOOD if helpful else BAD
                # Additive fields whose neutral is 0 but which the game states
                # as a percentage -- item discovery, bow drop-off and the like.
                shown, unit = value, ""
                if fname in model.PERCENT_FIELDS:
                    shown, unit = model.percent_value(fname, value), "%"
                elif fname in model.PERCENT_OF_100_FIELDS:
                    # Already reduced to its distance from the neutral 100.
                    unit = "%"
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

        self._sync_situational(build.situational)

        switchable = {entry.name for entry in build.situational}
        rest = [row for row in build.qualitative if row[0] not in switchable]
        if rest:
            lines = []
            for name, detail, why in rest:
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
        elif build.situational:
            # The switches above are the whole list. Repeating "nothing depends
            # on a condition" underneath them would contradict them.
            self.qual_label.clear()
        else:
            self.qual_label.setText(
                f"<span style='color:{MUTED}; font-size:11px'>Nothing you have "
                f"equipped depends on a condition. Effects that only work "
                f"below a HP threshold, with a particular armament, or on a "
                f"trigger would be listed here.</span>"
            )
        self.qual_label.setVisible(bool(self.qual_label.text()))

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
    # Before the QApplication, which is when Qt reads it and so the last
    # moment it can be said.
    uiscale.apply_to_environment()

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
