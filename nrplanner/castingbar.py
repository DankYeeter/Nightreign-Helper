"""The casting bar: which spell and which weapon art the selected tile uses.

AK-410..419 (`UI_SPEC.md` Nachtrag T-335r), figure version F1, with OF-59:
a spell slot rolled from a pool opens a popup like the art does. The bar
shows only what lies on the selected armament and decides nothing itself --
which art and which spell count is `damage.art_in_use` / `spell_thrown`, and
what a slot carries without a choice is `damage.fixed_entry` (AD-056.4,
AD-019). A choice goes out as a signal; the window stores it on the tile and
recomputes (AK-414), the way the stat sheet hands out `declared_changed`.
"""

from __future__ import annotations

import html
from dataclasses import dataclass

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor, QFontMetrics, QPixmap
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QVBoxLayout, QWidget,
)

from . import cardgrid, damage, weaponslots
from .theme import ACCENT, BORDER, HOVER_FILL, MUTED, PANEL

ICON_SIZE = 40
POPUP_COLUMNS = 6
POPUP_VISIBLE_ROWS = 5
POPUP_CELL = ICON_SIZE + 10
NAME_LINES = 2
DEFAULT_MARK = "●"

ART_CAPTION = "ART"
RELIC_CAPTION = "RELIC"
CHOOSE_ART = "Choose a weapon art"
CHOOSE_SPELL = "Choose a spell"
NO_DAMAGE = "no damage"
ONLY_ONE = "the only one this weapon has"
DEFAULT_NOTE = "default of this weapon"
OWN_ART_NOTE = "this weapon's own art"
SWAP_NOTE = ("A relic changed the starting armament's {what} to {name}. "
             "Your choice applies again without it.")


@dataclass(frozen=True)
class Chip:
    """One chip of the bar, as data: what it shows and what a click does."""

    kind: str                   # "art" or "spell"
    caption: str                # R1 / R2 / ART / RELIC
    record: dict | None         # the spell or art shown; None: choose one
    #: What the popup offers, default first; empty: no popup.
    pool: tuple[dict, ...]
    #: Clicking selects `record` (a slot that holds exactly one spell).
    selectable: bool
    default_id: int | None
    selected: bool
    figure_line: str

    @property
    def name(self) -> str:
        if self.record is not None:
            return str(self.record.get("name", ""))
        return CHOOSE_ART if self.kind == "art" else CHOOSE_SPELL

    def accessible_name(self) -> str:
        parts = [f"{self.caption}: {self.name}"]
        if self.figure_line:
            parts.append(self.figure_line)
        if self.selected:
            parts.append("selected")
        return ", ".join(parts)


def _fp(record: dict | None) -> str:
    fp = (record or {}).get("fp")
    return f"FP {fp}" if isinstance(fp, int) and fp >= 0 else ""


def _by_id(records, ids) -> dict[int, dict]:
    wanted = set(ids)
    return {r["id"]: r for r in records if r.get("id") in wanted}


def _pool(records: dict[int, dict], ids, default_id) -> tuple[dict, ...]:
    """The popup's entries: the default first, the rest by name (AK-411)."""
    entries = [records[i] for i in ids if i in records]
    return tuple(sorted(entries, key=lambda r: (r["id"] != default_id,
                                                str(r.get("name", "")))))


def _spell_figure(spell: dict, slot, build, data) -> str:
    rating = damage.spell(
        spell, slot.weapon, slot.tier, build, data,
        hit_with=damage.GENUS_OF_CATALYST[slot.weapon["wep_type"]])
    if rating.reason:
        return NO_DAMAGE
    return str(damage.displayed(rating.figure))


def _spell_chips(slot, build, hero, data) -> tuple[list[Chip], str | None]:
    weapon = slot.weapon
    own = damage.spell_catalyst(weapon, hero, data)[1]
    spells = data.get("spells") or ()
    thrown, swaps = damage.spell_thrown(build, data, weapon, starting=own,
                                        chosen=slot.spell_id)
    if swaps:
        chip = Chip("spell", RELIC_CAPTION, thrown, (), False, None, True,
                    _spell_figure(thrown, slot, build, data))
        return [chip], SWAP_NOTE.format(what="spell", name=thrown["name"])
    default = damage.spell_thrown(build, data, weapon, starting=own)[0]
    pools = weapon.get("spell_pools") or ()
    chips = []
    for index, own_spell in enumerate(weapon.get("equipped_spells") or ()):
        if own_spell == -1:
            continue
        pool = pools[index] if index < len(pools) else []
        shown = (slot.spell_id if slot.spell_id in pool
                 else damage.fixed_entry(own_spell, pool, own))
        record = _by_id(spells, [shown]).get(shown)
        records = _by_id(spells, pool)
        chips.append(Chip(
            "spell", f"R{index + 1}", record,
            _pool(records, pool, own_spell) if len(pool) > 1 else (),
            record is not None and len(pool) == 1 and shown in pool,
            default and default["id"],
            record is not None and thrown is not None
            and record["id"] == thrown["id"],
            _spell_figure(record, slot, build, data) if record else ""))
    return chips, None


def _art_chips(slot, slot_index, build, hero, data
               ) -> tuple[list[Chip], str | None]:
    weapon = slot.weapon
    art, swaps = damage.art_in_use(slot, slot_index, build, hero, data)
    if swaps:
        chip = Chip("art", RELIC_CAPTION, art, (), False, None, True, _fp(art))
        return [chip], SWAP_NOTE.format(what="skill", name=art["name"])
    arts = data.get("arts") or ()
    default_id = weapon.get("art_default")
    pool = weapon.get("art_pool") or []
    records = _by_id(arts, pool)
    if not records and default_id not in _by_id(arts, [default_id]):
        return [], None
    chip = Chip("art", ART_CAPTION, art,
                _pool(records, pool, default_id) if len(pool) > 1 else (),
                False, default_id, art is not None, _fp(art))
    return [chip], None


def chips_for(slot, slot_index: int, build, hero: dict,
              data: dict) -> tuple[list[Chip], str | None]:
    """The bar's chips for the selected tile, and the swap note, if any.

    One of three forms (AK-410): a staff or seal with a spell gets a chip per
    occupied spell slot, any other armament with an art one art chip, and an
    empty tile -- or an armament with neither -- nothing at all.
    """
    if not slot.filled:
        return [], None
    weapon = slot.weapon
    if (weapon.get("wep_type") in damage.GENUS_OF_CATALYST
            and any(s != -1 for s in weapon.get("equipped_spells") or ())):
        return _spell_chips(slot, build, hero, data)
    return _art_chips(slot, slot_index, build, hero, data)


def _icon(icons, record: dict | None) -> QPixmap:
    """The record's symbol, or a neutral square where there is none (AK-418)."""
    pixmap = icons.item(record.get("icon")) if icons and record else None
    if pixmap is None:
        pixmap = QPixmap(ICON_SIZE, ICON_SIZE)
        pixmap.fill(QColor(PANEL))
    return pixmap.scaled(ICON_SIZE, ICON_SIZE, Qt.KeepAspectRatio,
                         Qt.SmoothTransformation)


def _tooltip(chip: Chip) -> str:
    """Name, school or art, FP, and the default note -- escaped (AK-419)."""
    record = chip.record or {}
    lines = [chip.name,
             str(record.get("family") or "") if chip.kind == "spell"
             else "Weapon art", _fp(record)]
    if record and record.get("id") == chip.default_id:
        lines.append(DEFAULT_NOTE)
    if chip.kind == "art" and not chip.pool and chip.caption != RELIC_CAPTION:
        lines.append(ONLY_ONE)
    return "<br>".join(html.escape(line) for line in lines if line)


class ChipWidget(cardgrid.HoverCard):
    """One chip: caption, symbol, name, the muted line (AK-410/418)."""

    def __init__(self, chip: Chip, icons, on_activate) -> None:
        super().__init__()
        self.chip = chip
        self.on_activate = on_activate
        self.setFocusPolicy(Qt.StrongFocus)
        if chip.pool or chip.selectable:
            self.setCursor(Qt.PointingHandCursor)
        self.setAccessibleName(chip.accessible_name())
        self.setToolTip(_tooltip(chip))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(2)
        head = QHBoxLayout()
        caption = QLabel(chip.caption)
        caption.setStyleSheet(f"border: none; color: {MUTED};"
                              f" font-size: 9px;")
        head.addWidget(caption)
        head.addStretch(1)
        if chip.record is not None and chip.record.get("id") == chip.default_id:
            mark = QLabel(DEFAULT_MARK)
            mark.setStyleSheet(f"border: none; color: {ACCENT};"
                               f" font-size: 9px;")
            head.addWidget(mark)
        layout.addLayout(head)
        if chip.record is not None:
            self.icon = QLabel()
            self.icon.setStyleSheet("border: none;")
            self.icon.setPixmap(_icon(icons, chip.record))
            layout.addWidget(self.icon, alignment=Qt.AlignHCenter)
        self.name = QLabel()
        self.name.setTextFormat(Qt.PlainText)
        self.name.setWordWrap(True)
        self.name.setAlignment(Qt.AlignHCenter)
        self.name.setStyleSheet("border: none;")
        self.name.setText(chip.name)
        layout.addWidget(self.name)
        self.figure = QLabel(chip.figure_line)
        self.figure.setTextFormat(Qt.PlainText)
        self.figure.setAlignment(Qt.AlignHCenter)
        self.figure.setStyleSheet(f"border: none; color: {MUTED};"
                                  f" font-size: 10px;")
        layout.addWidget(self.figure)
        self._apply_appearance()

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt naming
        """Two lines of name, then an ellipsis; the tooltip has it whole."""
        metrics = QFontMetrics(self.name.font())
        room = max(1, self.name.width()) * NAME_LINES - metrics.averageCharWidth()
        self.name.setText(metrics.elidedText(self.chip.name, Qt.ElideRight,
                                             room))
        super().resizeEvent(event)

    def _apply_appearance(self) -> None:
        chip = self.chip
        border = ACCENT if chip.selected or self.hasFocus() else BORDER
        width = 2 if chip.selected or self.hasFocus() else 1
        style = "dashed" if chip.record is None else "solid"
        fill = HOVER_FILL if self.hovered or self.hasFocus() else PANEL
        self.setStyleSheet(
            f"QFrame {{ background: {fill}; border: {width}px {style}"
            f" {border}; border-radius: 6px; }}")

    def focusInEvent(self, event) -> None:  # noqa: N802 - Qt naming
        self._apply_appearance()
        super().focusInEvent(event)

    def focusOutEvent(self, event) -> None:  # noqa: N802 - Qt naming
        self._apply_appearance()
        super().focusOutEvent(event)

    def mousePressEvent(self, event) -> None:  # noqa: N802 - Qt naming
        if event.button() == Qt.LeftButton:
            self.on_activate(self)

    def keyPressEvent(self, event) -> None:  # noqa: N802 - Qt naming
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self.on_activate(self)
        else:
            super().keyPressEvent(event)


class PoolPopup(QFrame):
    """The pool of one chip: six symbols a row, five rows, then a scrollbar.

    A `QListWidget` in icon mode, so arrow keys, Enter and the scrollbar are
    Qt's own; Esc closes the popup and hands the focus back (AK-413).
    """

    def __init__(self, chip: Chip, icons, on_choose, anchor: QWidget,
                 width: int) -> None:
        super().__init__(anchor, Qt.Popup)
        self.chip = chip
        self.anchor = anchor
        self.on_choose = on_choose
        self.setStyleSheet(f"QFrame {{ background: {PANEL};"
                           f" border: 1px solid {BORDER}; }}")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        self.list = QListWidget()
        self.list.setViewMode(QListWidget.IconMode)
        self.list.setMovement(QListWidget.Static)
        self.list.setResizeMode(QListWidget.Adjust)
        self.list.setWrapping(True)
        self.list.setMouseTracking(True)
        self.list.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
        cell = max(POPUP_CELL, (width - 30) // POPUP_COLUMNS)
        self.list.setGridSize(QSize(cell, POPUP_CELL))
        rows = -(-len(chip.pool) // POPUP_COLUMNS)
        self.list.setFixedHeight(min(rows, POPUP_VISIBLE_ROWS) * POPUP_CELL + 6)
        for record in chip.pool:
            item = QListWidgetItem(_icon(icons, record), "")
            item.setData(Qt.UserRole, record["id"])
            item.setToolTip(html.escape(str(record.get("name", ""))))
            item.setData(Qt.AccessibleTextRole, str(record.get("name", "")))
            self.list.addItem(item)
        layout.addWidget(self.list)
        self.footer = QLabel()
        self.footer.setTextFormat(Qt.PlainText)
        self.footer.setWordWrap(True)
        self.footer.setStyleSheet(f"border: none; color: {MUTED};")
        layout.addWidget(self.footer)
        self.list.currentItemChanged.connect(
            lambda item, _old: self._describe(item))
        self.list.itemEntered.connect(self._describe)
        self.list.itemClicked.connect(self._choose)
        self.list.itemActivated.connect(self._choose)
        self.setFixedWidth(width)
        shown = next((i for i in range(self.list.count())
                      if self.list.item(i).data(Qt.UserRole)
                      == (chip.record or {}).get("id")), 0)
        self.list.setCurrentRow(shown)

    def _describe(self, item) -> None:
        if item is None:
            return
        record = self.chip.pool[self.list.row(item)]
        parts = [str(record.get("name", "")), _fp(record)]
        if record["id"] == self.chip.default_id:
            parts.append(OWN_ART_NOTE if self.chip.kind == "art"
                         else DEFAULT_NOTE)
        self.footer.setText(" · ".join(p for p in parts if p))

    def _choose(self, item) -> None:
        if not self.isVisible():
            return
        self.close()
        self.on_choose(self.chip.kind, item.data(Qt.UserRole))

    def keyPressEvent(self, event) -> None:  # noqa: N802 - Qt naming
        if event.key() == Qt.Key_Escape:
            self.close()
            self.anchor.setFocus(Qt.OtherFocusReason)
        else:
            super().keyPressEvent(event)

    def open_under(self) -> None:
        self.move(self.anchor.mapToGlobal(self.anchor.rect().bottomLeft()))
        self.show()
        self.list.setFocus(Qt.PopupFocusReason)


class CastingBar(QWidget):
    """The `CASTING` block between the tiles and the hand switch (AK-410)."""

    art_chosen = Signal(int)
    spell_chosen = Signal(int)

    def __init__(self, heading: QLabel, icons) -> None:
        super().__init__()
        self.icons = icons
        self.chip_widgets: list[ChipWidget] = []
        self.popup: PoolPopup | None = None
        self._shown = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(heading)
        self.grid = QGridLayout()
        self.grid.setHorizontalSpacing(6)
        for column in range(weaponslots.SLOT_COLUMNS):
            self.grid.setColumnStretch(column, 1)
        layout.addLayout(self.grid)
        self.note = QLabel()
        self.note.setTextFormat(Qt.PlainText)
        self.note.setWordWrap(True)
        self.note.setStyleSheet(f"color: {MUTED};")
        layout.addWidget(self.note)
        self.hide()

    def show_chips(self, chips: list[Chip], note: str | None) -> None:
        """Rebuild the chips; the bar takes no height when there are none.

        Skipped when nothing changed, so a recompute on every keystroke does
        not take the focus off a chip; after a choice the focus stays on the
        chip of the same caption.
        """
        if (chips, note) == self._shown:
            return
        self._shown = (chips, note)
        focused = next((w.chip.caption for w in self.chip_widgets
                        if w.hasFocus()), None)
        for widget in self.chip_widgets:
            widget.setParent(None)
            widget.deleteLater()
        self.chip_widgets = [ChipWidget(chip, self.icons, self._activate)
                             for chip in chips]
        for column, widget in enumerate(self.chip_widgets):
            self.grid.addWidget(widget, 0, column)
        self.note.setText(note or "")
        self.note.setVisible(bool(note))
        self.setVisible(bool(chips))
        for widget in self.chip_widgets:
            if widget.chip.caption == focused:
                widget.setFocus(Qt.OtherFocusReason)

    def _activate(self, widget: ChipWidget) -> None:
        chip = widget.chip
        if chip.pool:
            self.popup = PoolPopup(chip, self.icons, self._emit, widget,
                                   self.width())
            self.popup.open_under()
        elif chip.selectable and not chip.selected:
            self._emit(chip.kind, chip.record["id"])

    def _emit(self, kind: str, chosen: int) -> None:
        (self.art_chosen if kind == "art" else self.spell_chosen).emit(chosen)
