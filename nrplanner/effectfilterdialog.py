"""The effect filter window: Favourite and Avoid per owned effect, Avoid per
family and Allow per member (`UI_SPEC` §3.6, GOAL A21, A23).

One row per effect or curse id over every relic copy the player owns, never
per relic (AK-304), grouped under a heading per family with two or more
rows (AK-316); three check boxes an id row, one on a heading, disjoint
through the two calls the program already has for it, `EffectFilters.mark`
and `mark_family` (AK-305). The window holds no state of its own: a box is
drawn from the sets and every click goes straight to the store, so the
`Why` dialog and the `Filters` tooltip hear the same `changed` signal they
always heard (AK-311), and a run in flight says AK-289 through the wiring
`app.py` already has.

A `QTreeWidget`, not a table (AK-316.1/.2): a click on a column head sorts
siblings -- the top-level entries among themselves and the members of each
family among themselves -- so a family never comes apart, with no sort code
of this module's own.

Since the Director's addendum of 2026-09-15 this window is the **only**
place a marking is made (AK-301) -- the bullets in the picker and the `Why`
dialog are gone, so nothing here has to agree with a second control.
"""

from __future__ import annotations

import collections
import dataclasses
from collections.abc import Mapping

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QCheckBox, QDialog, QHeaderView, QLabel,
                               QLineEdit, QTreeWidget, QTreeWidgetItem,
                               QVBoxLayout)

from . import effectfilters, effecttext, search
from .advisorbar import CLAUSES, families_avoided

TITLE = "Effect filters"

#: AK-303. Measured live (T-277b, Fusion, 340 rows): the name column keeps
#: 227 px beside the four narrow ones, the frame is 520 x 590 with its title.
#: AK-313 (T-281, offscreen, 16.09.2026): the explanation label above the
#: table takes 56 px, so the height grows by the same amount to keep the
#: table at its measured 449 px. AK-316/317 (T-292d, offscreen, Fusion,
#: 339 rows, 17.09.2026): the `Allow` column asks 88 px more before the name
#: column has the width it had, the longer legend 26 px more above the tree
#: -- the tree keeps its 449 px. DR-032/T-294 (offscreen, Fusion,
#: 17.09.2026): re-measured with three counter clauses on screen at once
#: (`2 favourited · 1 avoided · 1 family avoided`, the widest the counter
#: gets, AK-316.5) after giving it `setWordWrap` -- still 608 x 642, where
#: the unwrapped label had forced 814 x 642 and stayed there once the
#: clause was gone.
OPENING_SIZE = (608, 642)

COL_FAVOURITE, COL_AVOID, COL_ALLOW, COL_NAME, COL_TYPE, COL_COPIES = range(6)
HEADINGS = ("Favourite", "Avoid", "Allow", "Name", "Type", "Copies")
FLAG_COLUMNS = (COL_FAVOURITE, COL_AVOID, COL_ALLOW)

#: AK-304: `Copies` here is not the `Copies` of the Effects & chances tab.
COPIES_DEFINITION = ("Copies counts relics you own that carry this effect or "
                     "curse — not game-data entries (that count is on the "
                     "Effects & chances tab).")

#: AK-317.1: what the three marks do here, and that none is the relic star.
MARKS_EXPLANATION = ("Favourite: every suggestion must include this effect. "
                     "Avoid: it never counts — on a family header, it avoids "
                     "every member below unless one is set to Allow. Allow "
                     "lets that one member back in without allowing the rest "
                     "of the family. These marks steer Optimize only — they "
                     "are not the star on a relic.")
SEARCH_PLACEHOLDER = ("Filter by effect or curse — supports AND, OR, NOT and "
                      "\"quoted phrases\"")
FAVOURITE_TOOLTIP = ("Every suggestion must carry this effect through at "
                     "least one owned copy.")
AVOID_TOOLTIP = "This effect counts in no suggestion or ranking."
#: AK-317.2-4.
FAMILY_AVOID_TOOLTIP = ("Every effect in this family counts in no suggestion "
                        "or ranking, unless a member below is set to Allow.")
#: AK-317 Nachtrag: always clickable, one tooltip for both states.
ALLOW_TOOLTIP = ("Let this one effect into suggestions even while its family "
                 "is avoided. It matters only once the family header is set "
                 "to Avoid.")

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
    family: str


def rows_from(owned, effects: dict, families: Mapping[int, str]) -> list[Row]:
    """One row per id the owned relics carry, counted in relic copies.

    A copy that carries the same id twice counts once: the column says how
    many relics carry it, not how many times. A name the dataset has lost
    is written as `effect {id}` the way `WhyDialog` writes it, and is a
    family of its own.
    """
    copies = collections.Counter()
    for item in owned.relics:
        copies.update(set(item.effect_ids) | set(item.curse_ids))
    rows = []
    for effect_id, count in copies.items():
        effect = effects.get(str(effect_id))
        name = effecttext.name(effect) if effect else f"effect {effect_id}"
        rows.append(Row(effect_id=effect_id, name=name,
                        is_curse=bool(effect and effect.get("is_curse")),
                        copies=count,
                        family=families.get(effect_id, name)))
    return rows


def counter_line(shown: int, total: int, filters) -> str:
    """AK-307, AK-316.5: `{shown} of {total} effects`, and the three counts
    when set -- ids avoided on their own and families avoided are two
    numbers, never one."""
    clauses = ([f"{len(filters.required)} favourited"]
               if filters.required else []) + (
               [f"{len(filters.excluded)} avoided"]
               if filters.excluded else []) + (
               [families_avoided(len(filters.avoided_families))]
               if filters.avoided_families else [])
    return CLAUSES.join([f"{shown} of {total} effects", *clauses])


class _Item(QTreeWidgetItem):
    """A row that sorts by its boxes on the flag columns (the box on top is
    the control; `on` is what a click on the column head sorts by), without
    regard to case on the name (AK-308), and by the cell's own value --
    the number under `Copies`, the text under `Type` -- elsewhere. (Not
    `super().__lt__`: PySide routes that back into this override.)"""

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.on = {column: False for column in FLAG_COLUMNS}

    def __lt__(self, other) -> bool:
        column = self.treeWidget().sortColumn()
        if column in FLAG_COLUMNS:
            return self.on[column] < other.on[column]
        if column == COL_NAME:
            return self.text(column).casefold() < other.text(column).casefold()
        return (self.data(column, Qt.DisplayRole)
                < other.data(column, Qt.DisplayRole))


class EffectFilterWindow(QDialog):
    """AK-303..309, AK-316: search, counter, definition line, the tree, and
    the empty-state label under it.

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
        #: effect id -> (row, Favourite box, Avoid box, Allow box or None, item)
        self._marks: dict[int, tuple] = {}
        #: family key -> (Avoid box, heading item)
        self._family_marks: dict[str, tuple] = {}
        self._box_css = ("QCheckBox::indicator:checked {{ background-color: "
                         "{c}; border: 1px solid {c}; border-radius: 2px; }}")
        self._colours = {COL_FAVOURITE: ACCENT, COL_AVOID: BAD}
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
        # DR-032: without this a fourth clause (favourited/avoided/family
        # avoided, T-292d) demands the whole line's width in one go and
        # blows the window out past OPENING_SIZE, wrap-around that Qt's
        # layout minimum then never releases even once the clause is gone.
        self.counter.setWordWrap(True)
        layout.addWidget(self.counter)

        definition = QLabel(COPIES_DEFINITION)
        definition.setWordWrap(True)
        definition.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        layout.addWidget(definition)

        marks_explanation = QLabel(MARKS_EXPLANATION)
        marks_explanation.setWordWrap(True)
        marks_explanation.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        marks_explanation.setFocusPolicy(Qt.NoFocus)
        layout.addWidget(marks_explanation)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(len(HEADINGS))
        self.tree.setHeaderLabels(HEADINGS)
        self.tree.setEditTriggers(QTreeWidget.NoEditTriggers)
        self.tree.setSelectionMode(QTreeWidget.NoSelection)
        # Tab walks the boxes row by row in the widget chain (AK-305); the
        # view's own cell navigation would keep it inside the grid instead.
        self.tree.setTabKeyNavigation(False)
        # The branch marks and the members' indent belong to the name, not
        # to the first box column.
        self.tree.setTreePosition(COL_NAME)
        # The name takes what the five narrow columns leave; measured with
        # 100 px defaults the name got 82 px of a 520 px window (T-277b).
        header = self.tree.header()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(COL_NAME, QHeaderView.Stretch)
        by_family = collections.defaultdict(list)
        for row in rows:
            by_family[row.family].append(row)
        for key, members in by_family.items():
            if len(members) < 2:
                self._add_id_row(members[0], self.tree.invisibleRootItem(),
                                 with_allow=False)
                continue
            head = _Item(self.tree)
            head.setText(COL_NAME, key)
            head.setData(COL_COPIES, Qt.DisplayRole,
                         sum(row.copies for row in members))
            avoid = self._box(FAMILY_AVOID_TOOLTIP, BAD)
            avoid.clicked.connect(
                lambda on, k=key: self._filters.mark_family(k, on))
            self.tree.setItemWidget(head, COL_AVOID, avoid)
            self._family_marks[key] = (avoid, head)
            for row in members:
                self._add_id_row(row, head, with_allow=True)
            head.setExpanded(True)
        self.tree.setSortingEnabled(True)
        self.tree.sortItems(COL_NAME, Qt.AscendingOrder)
        layout.addWidget(self.tree, 1)

        self.empty = QLabel(no_rows_reason or NO_MATCH)
        self.empty.setWordWrap(True)
        self.empty.setStyleSheet(f"color: {MUTED};")
        layout.addWidget(self.empty)

        filters.changed.connect(self._draw_the_marks)
        self._draw_the_marks()
        self._refresh()

    def _box(self, tooltip: str, colour: str | None) -> QCheckBox:
        box = QCheckBox()
        box.setToolTip(tooltip)
        if colour:
            box.setStyleSheet(self._box_css.format(c=colour))
        return box

    def _add_id_row(self, row: Row, parent, with_allow: bool) -> None:
        item = _Item(parent)
        item.setText(COL_NAME, row.name)
        item.setData(COL_NAME, Qt.UserRole, row.effect_id)
        item.setText(COL_TYPE, "Curse" if row.is_curse else "Effect")
        item.setData(COL_COPIES, Qt.DisplayRole, row.copies)
        columns = [(COL_FAVOURITE, FAVOURITE_TOOLTIP, effectfilters.REQUIRED),
                   (COL_AVOID, AVOID_TOOLTIP, effectfilters.EXCLUDED)]
        if with_allow:
            columns.append((COL_ALLOW, ALLOW_TOOLTIP, effectfilters.ALLOWED))
        boxes = []
        for column, tooltip, kind in columns:
            box = self._box(tooltip, self._colours.get(column))
            box.clicked.connect(
                lambda on, i=row.effect_id, k=kind: self._filters.mark(
                    i, k if on else None))
            self.tree.setItemWidget(item, column, box)
            boxes.append(box)
        if not with_allow:
            boxes.append(None)
        self._marks[row.effect_id] = (row, *boxes, item)

    def shown_ids(self) -> list[int]:
        """The ids of the rows the search leaves visible, top to bottom --
        members and headless singles, never a heading (AK-316.6)."""
        ids = []
        for index in range(self.tree.topLevelItemCount()):
            top = self.tree.topLevelItem(index)
            if top.isHidden():
                continue
            rows = ([top.child(c) for c in range(top.childCount())]
                    or [top])
            ids += [row.data(COL_NAME, Qt.UserRole) for row in rows
                    if not row.isHidden()]
        return ids

    def boxes(self, effect_id: int) -> tuple[QCheckBox, QCheckBox]:
        """The (Favourite, Avoid) boxes of one row."""
        _, favourite, avoid, _, _ = self._marks[effect_id]
        return favourite, avoid

    def allow_box(self, effect_id: int) -> QCheckBox | None:
        """The Allow box of one row, `None` on a row without a family head."""
        return self._marks[effect_id][3]

    def family_box(self, key: str) -> QCheckBox:
        """The Avoid box on the heading of one family."""
        return self._family_marks[key][0]

    def _draw_the_marks(self) -> None:
        filters = self._filters
        for effect_id, (row, favourite, avoid, allow, item) in self._marks.items():
            favourite.setChecked(effect_id in filters.required)
            avoid.setChecked(effect_id in filters.excluded)
            item.on[COL_FAVOURITE] = favourite.isChecked()
            item.on[COL_AVOID] = avoid.isChecked()
            if allow is not None:
                # AK-317 Nachtrag: always clickable, stored state keeps
                # showing regardless of the family's Avoid state.
                allow.setChecked(effect_id in filters.allowed)
                item.on[COL_ALLOW] = allow.isChecked()
        for key, (avoid, head) in self._family_marks.items():
            avoid.setChecked(key in filters.avoided_families)
            head.on[COL_AVOID] = avoid.isChecked()
        self._say_the_count()

    def _refresh(self) -> None:
        """AK-306 on every row, AK-316.6 across a family: a hit on the
        heading keeps every member, a hit on members keeps the heading and
        those members, no hit at all hides the family."""
        predicate = search.parse(self.search.text())

        def matches(item) -> bool:
            return predicate is None or predicate([item.text(COL_NAME)])

        for index in range(self.tree.topLevelItemCount()):
            top = self.tree.topLevelItem(index)
            children = [top.child(c) for c in range(top.childCount())]
            head_hit = matches(top)
            if not children or head_hit:
                top.setHidden(not head_hit)
                for child in children:
                    child.setHidden(False)
                continue
            hits = 0
            for child in children:
                hit = matches(child)
                hits += hit
                child.setHidden(not hit)
            top.setHidden(hits == 0)
        self._say_the_count()

    def _say_the_count(self) -> None:
        shown = len(self.shown_ids())
        self.counter.setText(counter_line(shown, len(self._rows),
                                          self._filters))
        self.empty.setVisible(shown == 0)
