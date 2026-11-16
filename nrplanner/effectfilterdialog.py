"""The effect filter window: Favourite, Avoid and Ignore per owned effect
and per family (`UI_SPEC` §3.6, GOAL A21, A23; Ignore, and no Allow any
more: user 2026-11-16).

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
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QCheckBox, QDialog, QHeaderView, QLabel,
                               QLineEdit, QTreeWidget, QTreeWidgetItem,
                               QVBoxLayout)

from . import effectfilters, effecttext, model, search
from .advisorbar import CLAUSES, families_avoided, ignored_count
from .theme import ACCENT, BAD, MUTED

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
#: clause was gone. AK-445 (offscreen, Fusion, 07.11.2026): the legend takes
#: 39 px more with the star's sentence, the tree keeps its 449 px. User
#: decision 07.11.2026 (offscreen, Fusion): the sentences on marks of another
#: Nightfarer take 26 px more, the tree keeps its 449 px. T-336 (offscreen,
#: Fusion, 339 rows, 07.11.2026): the `Stacks` column asks 94 px more before the
#: name column has the 104 px it had; the wider legend makes up for its new
#: sentence, the tree keeps its 449 px at the same height. T-336b (offscreen,
#: Fusion, 07.11.2026): the longer Stacks sentence takes 26 px more, the tree
#: keeps its 449 px. T-336h (07.11.2026): a row with a Stacks field no longer
#: stands taller than the others, which moves neither the size nor the tree's
#: 449 px (offscreen) and 542 px (live, Windows, at 100, 125 and 150 %).
#: Ignore in the place of Allow (16.11.2026): the column asks 4 px more than
#: Allow did, and on Windows (offscreen, CI runner) the legend's Ignore
#: sentence takes one line of 13 px more; with both the tree keeps its 449 px.
OPENING_SIZE = (706, 746)

(COL_FAVOURITE, COL_AVOID, COL_IGNORE, COL_STACKS, COL_NAME, COL_TYPE,
 COL_COPIES) = range(7)
HEADINGS = ("Favourite", "Avoid", "Ignore", "Stacks", "Name", "Type", "Copies")
FLAG_COLUMNS = (COL_FAVOURITE, COL_AVOID, COL_IGNORE)

#: As wide as the stat sheet's count box; two digits and their margins fit.
STACKS_FIELD_WIDTH = 42
#: What a row without a value sorts by: under 0, which is a value.
NO_STACKS = -1

#: AK-304: `Copies` here is not the `Copies` of the Effects & chances tab.
COPIES_DEFINITION = ("Copies counts relics you own that carry this effect or "
                     "curse — not game-data entries (that count is on the "
                     "Effects & chances tab).")

#: AK-445: what the three marks do here, and how they differ from the star.
MARKS_EXPLANATION = ("Favourite: every suggestion must carry this effect, "
                     "if it can — on a family header, any one member. "
                     "Avoid: no suggestion uses a relic that carries it — on "
                     "a family header, every member below, unless one has "
                     "a mark of its own. Ignore: the effect may be on a "
                     "suggested relic, but it counts as nothing — no gain, "
                     "and for a curse no loss. These marks are saved "
                     "for every Nightfarer; one that only works for another "
                     "Nightfarer is ignored here. "
                     "They are separate from the ★ you can "
                     "give a relic in the relic picker: that is per "
                     "Nightfarer, and Optimize puts a favourited relic in "
                     "when it fits. "
                     "Stacks: how many stacks Optimize and the relic picker's "
                     "figures count for an effect that stacks, not the stat "
                     "sheet; 0 does not count it, empty uses the count ticked "
                     "on the stat sheet, otherwise 1.")
SEARCH_PLACEHOLDER = ("Filter by effect or curse — supports AND, OR, NOT and "
                      "\"quoted phrases\"")
FAVOURITE_TOOLTIP = ("Every suggestion for this Nightfarer must carry this "
                     "effect, if it can.")
AVOID_TOOLTIP = "No suggestion uses a relic that carries this effect."
IGNORE_TOOLTIP = ("Suggestions may carry this effect, but it counts as "
                  "nothing: no relic is picked because of it.")
FAMILY_IGNORE_TOOLTIP = ("Suggestions may carry effects of this family, but "
                         "they count as nothing, unless a member below is "
                         "set to Favourite or Avoid.")
#: User decision 2026-11-15.
FAMILY_FAVOURITE_TOOLTIP = ("Every suggestion for this Nightfarer must carry "
                            "at least one effect of this family, if it can; "
                            "which one does not matter.")
#: AK-317.2-4.
FAMILY_AVOID_TOOLTIP = ("No suggestion uses a relic that carries an effect "
                        "of this family, unless a member below is set to "
                        "Favourite or Ignore.")
STACKS_TOOLTIP = ("How many stacks Optimize and the relic picker's figures "
                  "count, a whole number from 0 to {limit}; 0 leaves this effect "
                  "out. Empty: the count ticked on the stat sheet, otherwise "
                  "1. Anything else turns red and counts as empty. The stat "
                  "sheet itself does not change.")

#: AK-309, the three empty states in the tab's own tone.
NO_SAVE_WAS_READ = ("No save was read, so there are no effects to filter "
                    "yet — use Find my save.")
SAVE_HAS_NO_RELICS = ("That save has no relics in it yet, so there is "
                      "nothing to filter.")
#: The automatic route read a save with no relics (AK-389): "That save"
#: would point at nothing, "No save was read" would be false.
YOUR_SAVE_HAS_NO_RELICS = ("Your save has no relics in it yet, so there is "
                           "nothing to filter.")
NO_MATCH = "No effect matches your search."


@dataclasses.dataclass(frozen=True)
class Row:
    effect_id: int
    name: str
    is_curse: bool
    copies: int
    family: str
    #: A stack effect (`model.accumulates`): the one kind with a Stacks field.
    stacks: bool = False


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
                        family=families.get(effect_id, name),
                        stacks=bool(effect and model.accumulates(effect))))
    return rows


def counter_line(shown: int, total: int, filters) -> str:
    """AK-307, AK-316.5: `{shown} of {total} effects`, and the three counts
    when set -- ids avoided on their own and families avoided are two
    numbers, never one."""
    favourited = len(filters.required) + len(filters.favourite_families)
    clauses = ([f"{favourited} favourited"] if favourited else []) + (
               [f"{len(filters.excluded)} avoided"]
               if filters.excluded else []) + (
               [families_avoided(len(filters.avoided_families))]
               if filters.avoided_families else []) + (
               [f"{ignored_count(filters)} ignored"]
               if ignored_count(filters) else [])
    return CLAUSES.join([f"{shown} of {total} effects", *clauses])


def _is_refused(text: str, effect_id: int) -> bool:
    """Typed, and neither empty nor a count of this effect."""
    return bool(text) and effectfilters.stack_count(text, effect_id) is None


class _Item(QTreeWidgetItem):
    """A row that sorts by its boxes on the flag columns (the box on top is
    the control; `on` is what a click on the column head sorts by, the value
    of the field under `Stacks`), by the number under `Copies`, and by the
    text elsewhere, without regard to case on the name (AK-308) -- a family
    heading's empty `Type` is the empty text. (Not `super().__lt__`: PySide
    routes that back into this override.)"""

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.on = {column: False for column in FLAG_COLUMNS}
        self.on[COL_STACKS] = NO_STACKS

    def __lt__(self, other) -> bool:
        column = self.treeWidget().sortColumn()
        if column in self.on:
            return self.on[column] < other.on[column]
        if column == COL_COPIES:
            return (self.data(column, Qt.DisplayRole)
                    < other.data(column, Qt.DisplayRole))
        return self.text(column).casefold() < other.text(column).casefold()


class EffectFilterWindow(QDialog):
    """AK-303..309, AK-316: search, counter, definition line, the tree, and
    the empty-state label under it.

    `no_rows_reason` is AK-309's case 1 or 2 when `rows` is empty, and `""`
    otherwise -- the window cannot tell the two apart from the rows alone,
    and the caller already does (`NO_SAVE_FOUND`/`CHOSEN_SAVE_IS_EMPTY`).
    """

    def __init__(self, filters: effectfilters.EffectFilters, rows: list[Row],
                 no_rows_reason: str = "", parent=None, *,
                 symbol_of=None) -> None:
        super().__init__(parent)
        self._filters = filters
        self._rows = rows
        self._symbol_of = symbol_of or (lambda _effect_id: None)
        #: effect id -> (row, Favourite box, Avoid box, Ignore box, item)
        self._marks: dict[int, tuple] = {}
        #: family key -> (Avoid box, heading item, Favourite box, Ignore box)
        self._family_marks: dict[str, tuple] = {}
        #: effect id -> its Stacks field, stack effects only
        self.stack_fields: dict[int, QLineEdit] = {}
        self._box_css = ("QCheckBox::indicator:checked {{ background-color: "
                         "{c}; border: 1px solid {c}; border-radius: 2px; }}")
        self._colours = {COL_FAVOURITE: ACCENT, COL_AVOID: BAD,
                         COL_IGNORE: MUTED}
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
        # A tree's head stretches its last section too, and `Copies` would
        # then share the room with the name (QA-334).
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(COL_NAME, QHeaderView.Stretch)
        by_family = collections.defaultdict(list)
        for row in rows:
            by_family[row.family].append(row)
        for key, members in by_family.items():
            if len(members) < 2:
                self._add_id_row(members[0], self.tree.invisibleRootItem())
                continue
            head = _Item(self.tree)
            head.setText(COL_NAME, key)
            head.setData(COL_COPIES, Qt.DisplayRole,
                         sum(row.copies for row in members))
            avoid = self._box(FAMILY_AVOID_TOOLTIP, BAD)
            avoid.clicked.connect(
                lambda on, k=key: self._filters.mark_family(k, on))
            favour = self._box(FAMILY_FAVOURITE_TOOLTIP, ACCENT)
            favour.clicked.connect(
                lambda on, k=key: self._filters.favour_family(k, on))
            self.tree.setItemWidget(head, COL_FAVOURITE, favour)
            self.tree.setItemWidget(head, COL_AVOID, avoid)
            ignore = self._box(FAMILY_IGNORE_TOOLTIP, MUTED)
            ignore.clicked.connect(
                lambda on, k=key: self._filters.ignore_family(k, on))
            self.tree.setItemWidget(head, COL_IGNORE, ignore)
            self._family_marks[key] = (avoid, head, favour, ignore)
            for row in members:
                self._add_id_row(row, head)
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

    def _add_id_row(self, row: Row, parent) -> None:
        item = _Item(parent)
        item.setText(COL_NAME, row.name)
        symbol = self._symbol_of(row.effect_id)
        if symbol is not None:
            item.setIcon(COL_NAME, QIcon(symbol))
        item.setData(COL_NAME, Qt.UserRole, row.effect_id)
        item.setText(COL_TYPE, "Curse" if row.is_curse else "Effect")
        item.setData(COL_COPIES, Qt.DisplayRole, row.copies)
        # In column order: it is the order Tab walks them in.
        columns = [(COL_FAVOURITE, FAVOURITE_TOOLTIP, effectfilters.REQUIRED),
                   (COL_AVOID, AVOID_TOOLTIP, effectfilters.EXCLUDED),
                   (COL_IGNORE, IGNORE_TOOLTIP, effectfilters.IGNORED)]
        boxes = []
        for column, tooltip, kind in columns:
            box = self._box(tooltip, self._colours.get(column))
            box.clicked.connect(
                lambda on, i=row.effect_id, k=kind: self._filters.mark(
                    i, k if on else None))
            self.tree.setItemWidget(item, column, box)
            boxes.append(box)
        if row.stacks:
            self._add_stacks_field(row, item)
        self._marks[row.effect_id] = (row, *boxes, item)

    def _add_stacks_field(self, row: Row, item: _Item) -> None:
        """Written on every keystroke, as a box on every click: a value typed
        and left by closing the window is a value kept (no `editingFinished`
        on that way out). No validator: one drops a refused key and takes the
        next, which made 25 of `2.5`."""
        field = QLineEdit()
        field.setFixedWidth(STACKS_FIELD_WIDTH)
        # What a row without a field takes, the taller of its box and a line of
        # text: the field's own size hint made its row 1.5 times as high (AK-469).
        box = self.tree.itemWidget(item, COL_FAVOURITE)
        field.setFixedHeight(max(box.sizeHint().height(),
                                 field.fontMetrics().height()))
        field.setAlignment(Qt.AlignCenter)
        field.setToolTip(STACKS_TOOLTIP.format(
            limit=effectfilters.stack_limit(row.effect_id)))
        field.setAccessibleName(f"Stacks: {row.name}")
        field.textEdited.connect(
            lambda text, i=row.effect_id, f=field: self._stacks_typed(i, f, text))
        self.tree.setItemWidget(item, COL_STACKS, field)
        self.stack_fields[row.effect_id] = field

    def _stacks_typed(self, effect_id: int, field: QLineEdit, text: str) -> None:
        """A text that is no count stays as typed, in red, and counts as empty."""
        field.setStyleSheet(
            f"color: {BAD};" if _is_refused(text, effect_id) else "")
        self._filters.set_stacks(effect_id,
                                 effectfilters.stack_count(text, effect_id))

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

    def family_box(self, key: str) -> QCheckBox:
        """The Avoid box on the heading of one family."""
        return self._family_marks[key][0]

    def ignore_box(self, effect_id: int) -> QCheckBox:
        """The Ignore box of one row."""
        return self._marks[effect_id][3]

    def family_ignore_box(self, key: str) -> QCheckBox:
        """The Ignore box on the heading of one family."""
        return self._family_marks[key][3]

    def family_favourite_box(self, key: str) -> QCheckBox:
        """The Favourite box on the heading of one family."""
        return self._family_marks[key][2]

    def _draw_the_marks(self) -> None:
        filters = self._filters
        for effect_id, (row, favourite, avoid, ignore, item) in self._marks.items():
            favourite.setChecked(effect_id in filters.required)
            avoid.setChecked(effect_id in filters.excluded)
            item.on[COL_FAVOURITE] = favourite.isChecked()
            item.on[COL_AVOID] = avoid.isChecked()
            ignore.setChecked(effect_id in filters.ignored)
            item.on[COL_IGNORE] = ignore.isChecked()
        for key, (avoid, head, favour, ignore) in self._family_marks.items():
            ignore.setChecked(key in filters.ignored_families)
            head.on[COL_IGNORE] = ignore.isChecked()
            avoid.setChecked(key in filters.avoided_families)
            head.on[COL_AVOID] = avoid.isChecked()
            favour.setChecked(key in filters.favourite_families)
            head.on[COL_FAVOURITE] = favour.isChecked()
        for effect_id, field in self.stack_fields.items():
            count = filters.stacks.get(effect_id, NO_STACKS)
            shown = "" if count == NO_STACKS else str(count)
            # Not when equal: `setText` would throw the cursor to the end. Not
            # over a refused text either: it is what the red is about.
            if (field.text() != shown
                    and not _is_refused(field.text(), effect_id)):
                field.setText(shown)
            self._marks[effect_id][-1].on[COL_STACKS] = count
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
