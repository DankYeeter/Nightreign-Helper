"""The effect filter window: Favourite and Avoid per owned effect (`UI_SPEC`
§3.6, GOAL A21).

One row per effect or curse id over every relic copy the player owns, never
per relic (AK-304); two check boxes a row, disjoint through the one call the
program already has for it, `EffectFilters.mark` (AK-305). The window holds
no state of its own: a box is drawn from the two sets and every click goes
straight to the store, so the `Why` dialog and the `Filters` tooltip hear
the same `changed` signal they always heard (AK-311), and a run in flight
says AK-289 through the wiring `app.py` already has.

Since the Director's addendum of 2026-09-15 this window is the **only**
place a marking is made (AK-301) -- the bullets in the picker and the `Why`
dialog are gone, so nothing here has to agree with a second control.
"""

from __future__ import annotations

import collections
import dataclasses

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QCheckBox, QDialog, QHeaderView, QLabel,
                               QLineEdit, QTableWidget, QTableWidgetItem,
                               QVBoxLayout)

from . import effectfilters, effecttext, search
from .advisorbar import CLAUSES

TITLE = "Effect filters"

#: AK-303. Measured live (T-277b, Fusion, 340 rows): the name column keeps
#: 227 px beside the four narrow ones, the frame is 520 x 590 with its title.
OPENING_SIZE = (520, 560)

COL_FAVOURITE, COL_AVOID, COL_NAME, COL_TYPE, COL_COPIES = range(5)
HEADINGS = ("Favourite", "Avoid", "Name", "Type", "Copies")

#: AK-304: `Copies` here is not the `Copies` of the Effects & chances tab.
COPIES_DEFINITION = ("Copies counts relics you own that carry this effect or "
                     "curse — not game-data entries (that count is on the "
                     "Effects & chances tab).")
SEARCH_PLACEHOLDER = ("Filter by effect or curse — supports AND, OR, NOT and "
                      "\"quoted phrases\"")
FAVOURITE_TOOLTIP = ("Every suggestion must carry this effect through at "
                     "least one owned copy.")
AVOID_TOOLTIP = "This effect counts in no suggestion or ranking."

#: AK-309, the three empty states in the tab's own tone.
NO_SAVE_WAS_READ = "No save was read, so there are no effects to filter yet."
SAVE_HAS_NO_RELICS = ("That save has no relics in it yet, so there is "
                      "nothing to filter.")
NO_MATCH = "No effect matches your search."


@dataclasses.dataclass(frozen=True)
class Row:
    effect_id: int
    name: str
    is_curse: bool
    copies: int


def rows_from(owned, effects: dict) -> list[Row]:
    """One row per id the owned relics carry, counted in relic copies.

    A copy that carries the same id twice counts once: the column says how
    many relics carry it, not how many times. A name the dataset has lost
    is written as `effect {id}` the way `WhyDialog` writes it.
    """
    copies = collections.Counter()
    for item in owned.relics:
        copies.update(set(item.effect_ids) | set(item.curse_ids))
    rows = []
    for effect_id, count in copies.items():
        effect = effects.get(str(effect_id))
        rows.append(Row(effect_id=effect_id,
                        name=(effecttext.name(effect) if effect
                              else f"effect {effect_id}"),
                        is_curse=bool(effect and effect.get("is_curse")),
                        copies=count))
    return rows


def counter_line(shown: int, total: int, filters) -> str:
    """AK-307: `{shown} of {total} effects`, and the two counts when set."""
    clauses = ([f"{len(filters.required)} favourited"]
               if filters.required else []) + (
               [f"{len(filters.excluded)} avoided"]
               if filters.excluded else [])
    return CLAUSES.join([f"{shown} of {total} effects", *clauses])


class _CaseFoldItem(QTableWidgetItem):
    """A name cell that sorts without regard to case (AK-308)."""

    def __lt__(self, other) -> bool:
        return self.text().casefold() < other.text().casefold()


class _FlagItem(QTableWidgetItem):
    """The sort key under a check box cell: the box on top is the control,
    this item is what a click on the column head sorts by."""

    def __init__(self) -> None:
        super().__init__()
        self.on = False

    def __lt__(self, other) -> bool:
        return self.on < getattr(other, "on", False)


class EffectFilterWindow(QDialog):
    """AK-303..309: search, counter, definition line, the grid, and the
    empty-state label under it.

    `no_rows_reason` is AK-309's case 1 or 2 when `rows` is empty, and `""`
    otherwise -- the window cannot tell the two apart from the rows alone,
    and the caller already does (`NO_SAVE_FOUND`/`CHOSEN_SAVE_IS_EMPTY`).
    """

    def __init__(self, filters: effectfilters.EffectFilters, rows: list[Row],
                 no_rows_reason: str = "", parent=None) -> None:
        super().__init__(parent)
        from .app import ACCENT, BAD, MUTED

        self._filters = filters
        self._rows = rows
        #: effect id -> (Favourite box, Avoid box, Favourite key, Avoid key)
        self._marks: dict[int, tuple] = {}
        self.setWindowTitle(TITLE)
        self.setModal(True)
        self.resize(*OPENING_SIZE)

        layout = QVBoxLayout(self)
        self.search = QLineEdit()
        self.search.setPlaceholderText(SEARCH_PLACEHOLDER)
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self._refresh)
        layout.addWidget(self.search)

        self.counter = QLabel()
        layout.addWidget(self.counter)

        definition = QLabel(COPIES_DEFINITION)
        definition.setWordWrap(True)
        definition.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        layout.addWidget(definition)

        self.table = QTableWidget(len(rows), len(HEADINGS))
        self.table.setHorizontalHeaderLabels(HEADINGS)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        # Tab walks the boxes row by row in the widget chain (AK-305); the
        # view's own cell navigation would keep it inside the grid instead.
        self.table.setTabKeyNavigation(False)
        # The name takes what the four narrow columns leave; measured with
        # 100 px defaults the name got 82 px of a 520 px window (T-277b).
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(COL_NAME, QHeaderView.Stretch)
        box_css = ("QCheckBox::indicator:checked {{ background-color: {c}; "
                   "border: 1px solid {c}; border-radius: 2px; }}")
        for index, row in enumerate(rows):
            favourite = QCheckBox()
            favourite.setToolTip(FAVOURITE_TOOLTIP)
            favourite.setStyleSheet(box_css.format(c=ACCENT))
            favourite.clicked.connect(
                lambda on, i=row.effect_id: self._filters.mark(
                    i, effectfilters.REQUIRED if on else None))
            avoid = QCheckBox()
            avoid.setToolTip(AVOID_TOOLTIP)
            avoid.setStyleSheet(box_css.format(c=BAD))
            avoid.clicked.connect(
                lambda on, i=row.effect_id: self._filters.mark(
                    i, effectfilters.EXCLUDED if on else None))
            favourite_key, avoid_key = _FlagItem(), _FlagItem()
            self._marks[row.effect_id] = (favourite, avoid, favourite_key,
                                          avoid_key)
            self.table.setItem(index, COL_FAVOURITE, favourite_key)
            self.table.setCellWidget(index, COL_FAVOURITE, favourite)
            self.table.setItem(index, COL_AVOID, avoid_key)
            self.table.setCellWidget(index, COL_AVOID, avoid)
            name = _CaseFoldItem(row.name)
            name.setData(Qt.UserRole, row.effect_id)
            self.table.setItem(index, COL_NAME, name)
            self.table.setItem(index, COL_TYPE, QTableWidgetItem(
                "Curse" if row.is_curse else "Effect"))
            copies = QTableWidgetItem()
            copies.setData(Qt.DisplayRole, row.copies)
            self.table.setItem(index, COL_COPIES, copies)
        self.table.setSortingEnabled(True)
        self.table.sortItems(COL_NAME, Qt.AscendingOrder)
        layout.addWidget(self.table, 1)

        self.empty = QLabel(no_rows_reason or NO_MATCH)
        self.empty.setWordWrap(True)
        self.empty.setStyleSheet(f"color: {MUTED};")
        layout.addWidget(self.empty)

        filters.changed.connect(self._draw_the_marks)
        self._draw_the_marks()
        self._refresh()

    def shown_ids(self) -> list[int]:
        """The ids of the rows the search leaves visible, top to bottom."""
        return [self.table.item(index, COL_NAME).data(Qt.UserRole)
                for index in range(self.table.rowCount())
                if not self.table.isRowHidden(index)]

    def boxes(self, effect_id: int) -> tuple[QCheckBox, QCheckBox]:
        """The (Favourite, Avoid) boxes of one row."""
        favourite, avoid, _, _ = self._marks[effect_id]
        return favourite, avoid

    def _draw_the_marks(self) -> None:
        for effect_id, (favourite, avoid, favourite_key,
                        avoid_key) in self._marks.items():
            favourite.setChecked(effect_id in self._filters.required)
            avoid.setChecked(effect_id in self._filters.excluded)
            favourite_key.on = favourite.isChecked()
            avoid_key.on = avoid.isChecked()
        self._say_the_count()

    def _refresh(self) -> None:
        predicate = search.parse(self.search.text())
        for index in range(self.table.rowCount()):
            name = self.table.item(index, COL_NAME).text()
            self.table.setRowHidden(
                index, predicate is not None and not predicate([name]))
        self._say_the_count()

    def _say_the_count(self) -> None:
        shown = len(self.shown_ids())
        self.counter.setText(counter_line(shown, len(self._rows),
                                          self._filters))
        self.empty.setVisible(shown == 0)
