"""Relic chooser laid out like the in-game relic screen: a grid of icons."""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QMenu, QPushButton, QScrollArea, QToolButton,
    QVBoxLayout, QWidget, QWidgetAction,
)

from . import effecttext, favourites, model
from .inventory import CUSTOM_RELIC_ID

COLUMNS = 5
ICON = 56
CARD_WIDTH = 190

ACCENT = "#c8a45c"
MUTED = "#8a8a8a"
PANEL = "#1e1f23"
BORDER = "#2e2f35"
CURSE = "#d1655f"
# Purple against the gold of a selected card: the two states have to be told
# apart at a glance, and gold's opposite is the one colour the rest of the
# window never uses.
FAVOURITE = "#a86fe0"

# The Nightfarer grid inside the favourite menu, matching the sidebar's shape.
HERO_COLUMNS = 5
HERO_ICON = 44

SLOT_COLOURS = {
    0: "#b4544e", 1: "#4e7ab4", 2: "#c2a24a", 3: "#5c9e63", 4: "#d8d8d8",
}


class RelicCard(QFrame):
    """One relic: its icon, name and the effects it actually rolled."""

    def __init__(self, item, effect_names: list[str], icon, selected: bool,
                 on_pick, curses: list[tuple[str, str]] | None = None,
                 tooltip: str = "", favourite: bool = False,
                 on_favourite=None):
        super().__init__()
        self.item = item
        self.on_favourite = on_favourite
        self.setFixedWidth(CARD_WIDTH)
        self.setCursor(Qt.PointingHandCursor)
        # Selection and favourite are different questions -- "is this relic on
        # right now" and "do I want this relic on this character" -- so a card
        # can be both. Selection takes the border because it is about the slot
        # being edited; the star carries the favourite through either state.
        if selected:
            edge, width = ACCENT, 2
        elif favourite:
            edge, width = FAVOURITE, 2
        else:
            edge, width = BORDER, 1
        self.setStyleSheet(
            f"QFrame {{ background: {PANEL};"
            f" border: {width}px solid {edge};"
            f" border-radius: 6px; }}"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        header = QHBoxLayout()
        header.setSpacing(8)

        self.button = QToolButton()
        self.button.setIconSize(QSize(ICON, ICON))
        self.button.setFixedSize(ICON + 6, ICON + 6)
        self.button.setAutoRaise(True)
        self.button.setStyleSheet("border: none;")
        if icon is not None:
            self.button.setIcon(QIcon(icon))
        self.button.clicked.connect(lambda: on_pick(item))
        header.addWidget(self.button)

        if favourite:
            star = QLabel("★")
            star.setStyleSheet(
                f"border: none; color: {FAVOURITE}; font-size: 13px;")
            header.addWidget(star, 0, Qt.AlignTop)

        title = QLabel(item.name)
        title.setWordWrap(True)
        title.setStyleSheet(
            f"border: none; font-weight: bold; "
            f"color: {ACCENT if selected else '#e4e4e4'};"
        )
        header.addWidget(title, 1)
        layout.addLayout(header)

        for name in effect_names:
            label = QLabel(f"• {name}")
            label.setWordWrap(True)
            label.setStyleSheet(f"border: none; color: #cfcfcf; font-size: 11px;")
            layout.addWidget(label)

        # Name the curses outright. "Comes with a curse" tells the player there
        # is a cost but not what it is, which is the one thing they need to
        # know before putting the relic on.
        for curse_name, curse_detail in (curses or []):
            label = QLabel(f"✦ {curse_name}")
            label.setWordWrap(True)
            label.setStyleSheet(f"border: none; color: {CURSE}; font-size: 11px;")
            if curse_detail:
                label.setToolTip(curse_detail)
            layout.addWidget(label)

        if not curses and item.has_curse:
            count = getattr(item, "curse_count", 0) or 0
            what = f"{count} curses" if count > 1 else "a curse"
            curse = QLabel(f"✦ comes with {what}")
            curse.setWordWrap(True)
            curse.setStyleSheet(f"border: none; color: {CURSE}; font-size: 11px;")
            layout.addWidget(curse)

        if tooltip:
            self.setToolTip(tooltip)

        layout.addStretch()

    def mousePressEvent(self, event):  # noqa: N802 - Qt naming
        # Right-click belongs to the favourite menu. Without this guard the
        # menu would open and the card would be picked in the same gesture,
        # closing the picker out from under it.
        if event.button() != Qt.LeftButton:
            event.ignore()
            return
        self.button.click()

    def contextMenuEvent(self, event):  # noqa: N802 - Qt naming
        if self.on_favourite is None:
            return
        self.on_favourite(self.item, event.globalPos())


class CustomRelicCard(QFrame):
    """The build-your-own tile that leads the grid.

    Everything else in the picker is a relic the player actually holds. This
    one is deliberately styled apart so it reads as a tool rather than as a
    relic that has somehow been acquired.
    """

    def __init__(self, effect_names: list[str], selected: bool, on_pick):
        super().__init__()
        self.setFixedWidth(CARD_WIDTH)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(
            f"QFrame {{ background: {PANEL};"
            f" border: 1px dashed {ACCENT if selected else MUTED};"
            f" border-radius: 6px; }}"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        header = QHBoxLayout()
        header.setSpacing(8)
        self.button = QToolButton()
        self.button.setText("+")
        self.button.setFixedSize(ICON + 6, ICON + 6)
        self.button.setAutoRaise(True)
        self.button.setStyleSheet(
            f"border: none; color: {ACCENT}; font-size: 26px;")
        self.button.clicked.connect(on_pick)
        header.addWidget(self.button)

        title = QLabel("Custom relic")
        title.setWordWrap(True)
        title.setStyleSheet(
            f"border: none; font-weight: bold;"
            f" color: {ACCENT if selected else '#e4e4e4'};"
        )
        header.addWidget(title, 1)
        layout.addLayout(header)

        if effect_names:
            for name in effect_names:
                label = QLabel(f"• {name}")
                label.setWordWrap(True)
                label.setStyleSheet(
                    "border: none; color: #cfcfcf; font-size: 11px;")
                layout.addWidget(label)
        else:
            hint = QLabel("Pick any effects that can roll in this slot, to "
                          "plan around a relic you have not found yet.")
            hint.setWordWrap(True)
            hint.setStyleSheet(f"border: none; color: {MUTED}; font-size: 11px;")
            layout.addWidget(hint)

        layout.addStretch()
        self.setToolTip("Build a hypothetical relic for this slot")

    def mousePressEvent(self, event):  # noqa: N802 - Qt naming
        self.button.click()


class FavouriteMenu(QMenu):
    """"Favourite for" — the Nightfarers, in the same 2x5 grid as the sidebar.

    The menu deliberately stays open while portraits are toggled: a relic that
    suits one character usually suits its neighbours too, and reopening the
    menu once per Nightfarer for a good roll would be tedious.
    """

    def __init__(self, parent, item, heroes: list[dict], icons):
        super().__init__(parent)
        self.item = item
        self.changed = False

        heading = QLabel("Favourite for")
        heading.setStyleSheet(
            f"color: {MUTED}; font-size: 11px; padding: 6px 8px 2px 8px;")
        title = QWidgetAction(self)
        title.setDefaultWidget(heading)
        self.addAction(title)

        holder = QWidget()
        grid = QGridLayout(holder)
        grid.setContentsMargins(8, 2, 8, 8)
        grid.setSpacing(4)
        marked = favourites.heroes_for(item)
        for i, hero in enumerate(heroes):
            grid.addWidget(
                self._tile(hero, icons, hero["id"] in marked),
                i // HERO_COLUMNS, i % HERO_COLUMNS,
            )
        body = QWidgetAction(self)
        body.setDefaultWidget(holder)
        self.addAction(body)

    def _tile(self, hero: dict, icons, checked: bool) -> QToolButton:
        button = QToolButton()
        button.setCheckable(True)
        button.setChecked(checked)
        button.setAutoRaise(True)
        button.setCursor(Qt.PointingHandCursor)
        button.setFixedSize(HERO_ICON + 8, HERO_ICON + 8)
        button.setToolTip(hero["name"])
        pixmap = icons.portrait(hero["id"]) if icons is not None else None
        if pixmap is not None:
            button.setToolButtonStyle(Qt.ToolButtonIconOnly)
            button.setIconSize(QSize(HERO_ICON, HERO_ICON))
            button.setIcon(QIcon(pixmap))
        else:
            # The DLC characters have no extractable artwork, so their tiles
            # carry initials and keep the grid the same shape either way.
            button.setText(hero["name"][:2])
        button.setStyleSheet(
            f"QToolButton {{ border: 1px solid {BORDER}; border-radius: 4px;"
            f" background: {PANEL}; color: #cfcfcf; padding: 0px; }}"
            f"QToolButton:checked {{ border: 2px solid {FAVOURITE}; }}"
        )
        button.clicked.connect(
            lambda _checked=False, h=hero, b=button: self._toggle(h, b))
        return button

    def _toggle(self, hero: dict, button: QToolButton) -> None:
        button.setChecked(favourites.toggle(self.item, hero["id"]))
        self.changed = True


class CustomRelicDialog(QDialog):
    """Choose up to three effects to make up a relic that does not exist yet."""

    MAX_EFFECTS = 3

    def __init__(self, parent, choices: list[dict], chosen: list[int]):
        super().__init__(parent)
        self.choices = choices
        self.chosen = list(chosen)[:self.MAX_EFFECTS]

        self.setWindowTitle("Custom relic")
        self.setModal(True)
        self.resize(640, 620)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        blurb = QLabel(
            f"A real relic rolls up to three effects. Only effects that can "
            f"actually appear in this slot are listed ({len(choices)} of them)."
        )
        blurb.setWordWrap(True)
        blurb.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        layout.addWidget(blurb)

        self.picked = QLabel()
        self.picked.setWordWrap(True)
        self.picked.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.picked)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Filter effects…")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self._refresh)
        layout.addWidget(self.search)

        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(self._toggle)
        layout.addWidget(self.list, 1)

        buttons = QHBoxLayout()
        add = QPushButton("Add / remove selected")
        add.clicked.connect(lambda: self._toggle(self.list.currentItem()))
        buttons.addWidget(add)
        clear = QPushButton("Clear")
        clear.clicked.connect(self._clear)
        buttons.addWidget(clear)
        buttons.addStretch()
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        buttons.addWidget(cancel)
        self.ok = QPushButton("Use this relic")
        self.ok.setDefault(True)
        self.ok.clicked.connect(self.accept)
        buttons.addWidget(self.ok)
        layout.addLayout(buttons)

        self._refresh()

    def _refresh(self) -> None:
        needle = self.search.text().strip().lower()
        self.list.clear()
        for eff in self.choices:
            label = effecttext.name(eff)
            detail = effecttext.describe_full(eff)
            if needle and needle not in f"{label} {detail}".lower():
                continue
            mark = "✓ " if eff["id"] in self.chosen else "   "
            entry = QListWidgetItem(f"{mark}{label} — {detail}")
            entry.setData(Qt.UserRole, eff["id"])
            entry.setToolTip(detail)
            self.list.addItem(entry)

        by_id = {e["id"]: e for e in self.choices}
        if self.chosen:
            names = [effecttext.name(by_id[i]) for i in self.chosen if i in by_id]
            self.picked.setText(
                f"<b>{len(self.chosen)} of {self.MAX_EFFECTS} chosen:</b> "
                + ", ".join(names))
        else:
            self.picked.setText(
                f"<b>Nothing chosen yet</b> — double-click up to "
                f"{self.MAX_EFFECTS} effects.")
        self.ok.setEnabled(bool(self.chosen))

    def _toggle(self, entry) -> None:
        if entry is None:
            return
        eid = entry.data(Qt.UserRole)
        if eid in self.chosen:
            self.chosen.remove(eid)
        elif len(self.chosen) < self.MAX_EFFECTS:
            self.chosen.append(eid)
        self._refresh()

    def _clear(self) -> None:
        self.chosen = []
        self._refresh()


class RelicPicker(QDialog):
    """Grid of the relics that fit one slot."""

    def __init__(self, slot, icons, search_text: str, on_search_changed):
        super().__init__(slot.window())
        self.slot = slot
        self.icons = icons
        self.on_search_changed = on_search_changed
        self.chosen = None
        # Favourites are per Nightfarer, so the picker has to know which one
        # the build is for. A slot outside the main window simply has none.
        window = slot.window()
        current = getattr(window, "current_hero", None)
        hero = current() if callable(current) else None
        self.hero_id = hero["id"] if hero else None
        self.hero_label = hero["name"] if hero else ""

        colour = model.COLOUR_NAMES.get(slot.colour, slot.colour)
        self.setWindowTitle(
            f"{'Deep ' if slot.deep else ''}Slot {slot.index + 1} — {colour}"
        )
        self.setModal(True)
        self.resize(CARD_WIDTH * COLUMNS + 80, 720)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        top = QHBoxLayout()
        chip = QLabel()
        chip.setFixedSize(16, 16)
        chip.setStyleSheet(
            f"background: {SLOT_COLOURS.get(slot.colour, '#888')};"
            f" border: 1px solid {BORDER}; border-radius: 8px;"
        )
        top.addWidget(chip)

        self.search = QLineEdit(search_text)
        self.search.setPlaceholderText("Filter by effect…")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self._refresh)
        top.addWidget(self.search, 1)

        clear = QPushButton("Empty slot")
        clear.clicked.connect(lambda: self._pick(None))
        top.addWidget(clear)
        layout.addLayout(top)

        self.summary = QLabel()
        self.summary.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        layout.addWidget(self.summary)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        layout.addWidget(self.scroll, 1)

        self._refresh()

    @staticmethod
    def _distinct(items: list) -> list:
        """One card per roll -- favourites.distinct, kept as a method name
        because the call sites read better for it. The reasoning lives with
        the shared function, which the slot header now uses as well, so the
        picker's count and the header's can no longer disagree.
        """
        return favourites.distinct(items)

    def _candidates(self):
        from . import search

        text = self.search.text()
        predicate = search.parse(text)
        items = []
        if self.slot.owned is not None:
            items = self._distinct(self.slot.owned.relics_for(
                self.slot.colour, self.slot.deep, 4
            ))
        if predicate is not None:
            items = [i for i in items if predicate(self.slot.effect_names(i))]
        # Favourites for the Nightfarer currently being planned lead the grid.
        # sorted() is stable, so everything else keeps the name order it had.
        if self.hero_id is not None:
            items = sorted(
                items,
                key=lambda i: 0 if favourites.is_favourite(i, self.hero_id) else 1,
            )
        return items, text.strip()

    def _heroes(self) -> list[dict]:
        return getattr(self.slot.window(), "heroes", None) or []

    def _open_favourites(self, item, position) -> None:
        heroes = self._heroes()
        if not heroes:
            return
        menu = FavouriteMenu(self, item, heroes, self.icons)
        # Refreshing while the menu is open would delete the card it is
        # anchored to, so the grid is rebuilt only once the menu has closed.
        menu.exec(position)
        if menu.changed:
            self._refresh()

    def _curses(self, item) -> list[tuple[str, str]]:
        """(name, full description) for each curse this relic actually rolled."""
        out = []
        for cid in getattr(item, "curse_ids", ()) or ():
            eff = self.slot.effect_by_id.get(cid)
            if eff is None:
                out.append((f"<{cid}>", ""))
            else:
                out.append((effecttext.name(eff), effecttext.describe_full(eff)))
        return out

    def _refresh(self) -> None:
        items, needle = self._candidates()
        total = 0
        if self.slot.owned is not None:
            total = len(self._distinct(self.slot.owned.relics_for(
                self.slot.colour, self.slot.deep, 4
            )))
        starred = sum(
            1 for i in items
            if self.hero_id is not None and favourites.is_favourite(i, self.hero_id)
        )
        note = f" — {starred} favourited for {self.hero_label}" if starred else ""
        self.summary.setText(
            f"{len(items)} of {total} relics"
            + (f" matching “{needle}”" if needle else "")
            + note
            + "  ·  right-click a relic to favourite it"
        )

        holder = QWidget()
        grid = QGridLayout(holder)
        grid.setSpacing(8)
        grid.setAlignment(Qt.AlignTop)

        current = self.slot.relic_box.currentData()

        # The custom tile always leads, and is never filtered out -- it is the
        # answer to "none of these are what I want", so hiding it behind a
        # search that matched nothing would remove it exactly when it is needed.
        custom = getattr(self.slot, "custom_item", None)
        grid.addWidget(
            CustomRelicCard(
                self.slot.effect_names(custom) if custom is not None else [],
                selected=current is not None
                and getattr(current, "relic_id", None) == CUSTOM_RELIC_ID,
                on_pick=self._open_custom,
            ),
            0, 0,
        )

        for n, item in enumerate(items):
            i = n + 1
            icon = self.icons.item(item.icon) if item.icon else None
            card = RelicCard(
                item,
                self.slot.effect_names(item),
                icon,
                selected=current is not None and current.relic_id == item.relic_id
                and current.effect_ids == item.effect_ids,
                on_pick=self._pick,
                curses=self._curses(item),
                tooltip=self.slot.curse_tooltip(item),
                favourite=self.hero_id is not None
                and favourites.is_favourite(item, self.hero_id),
                on_favourite=self._open_favourites,
            )
            grid.addWidget(card, i // COLUMNS, i % COLUMNS)

        self.scroll.setWidget(holder)

    def _open_custom(self) -> None:
        existing = getattr(self.slot, "custom_item", None)
        dialog = CustomRelicDialog(
            self,
            self.slot.rollable_effects(),
            list(existing.effect_ids) if existing is not None else [],
        )
        if not dialog.exec():
            return
        self.slot.set_custom(dialog.chosen)
        self.chosen = self.slot.custom_item
        self.on_search_changed(self.search.text())
        self.accept()

    def _pick(self, item) -> None:
        self.chosen = item
        self.on_search_changed(self.search.text())
        self.accept()
