"""Browsable table of every relic effect, its roll chance and what it does."""

from __future__ import annotations

import collections
import json

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QStyle, QStyleOptionHeader, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget,
)

from . import effecttext, model, stacking, tabheader
from .effecttext import caption, describe, describe_full  # noqa: F401

#: What this tab is for, above the filter row and above the counts (AK-68,
#: AK-76). Until T-057 the first line a reader met was a stock count.
HEADING = "WHAT A RELIC CAN ROLL, AND HOW OFTEN"
QUESTION = (
    "Every effect a relic can carry, how likely you are to roll it, and "
    "whether carrying a second copy is worth anything.")

#: The one definition of the chance figures on this screen, and the only one
#: (AK-79). There used to be two, six lines apart and disagreeing: a column
#: tooltip averaged over loot pools while the summary spoke of one roll of a
#: colour and mode the reader had not chosen -- `All colours` is the default,
#: so no colour was selected at all. Both are gone; this sentence appears
#: once, and `tests/test_effects_tab_display.py` holds the count at one.
CHANCE_DEFINITION = (
    "Chance is per relic effect slot, over every slot that can roll the "
    "effect under the filters above — not per relic and not per run.")

#: The chance cell of an effect no slot can reach under the current filters.
#: It carries the signal the `Pools` column used to carry with a bare `0`
#: (AK-78): a rung of a ladder can exist while nothing on offer rolls it.
UNREACHABLE_TIP = (
    "No relic effect slot can roll this under the current colour and mode "
    "filters. It exists as a rung of its ladder; other filters may reach it.")

COLUMNS = ["Effect", "Type", "Tier", "Copies", "Colours", "Relic slots",
           "Avg chance", "Best chance", "Stacking", "Comes with curse",
           "What it does"]

# Column indices used for formatting, kept next to COLUMNS so they move
# together if the layout changes.
COL_TYPE = 1
COL_COPIES = 3
COL_SLOTS = 5
COL_AVG = 6
COL_BEST = 7
COL_STACKS = 8
COL_CURSE = 9
NUMERIC = (COL_COPIES, COL_SLOTS, COL_AVG, COL_BEST)

# "Buff" sorts before "Curse", so sorting on the Type column groups them the
# way round the player wants without any special-casing. It also survives the
# user clicking other headers -- they can always click Type to get it back.
TYPE_BUFF = "Buff"
TYPE_CURSE = "Curse"

CURSE_LABEL = {
    "always": "always cursed",
    "sometimes": "sometimes",
    "never": "",
}

# What each column means, on the header itself. Written for a player: no
# param names, no file talk beyond what the provenance genuinely is.
HEADER_TIPS = {
    2: "Some effects come as a ladder of strengths under one name — "
       "'1 of 3' is the weakest rung, and each rung is its own effect.",
    COL_COPIES: "How many identical copies of this effect the game defines. "
                "They are merged into this one row.",
    4: "Relic colours this effect can appear on.",
    COL_SLOTS: "How many of the game's relic effect slots can roll this "
               "effect, counted over every relic and every slot on it. It is "
               "not a count of loot pools, and more slots does not mean more "
               "likely — the chance column says that.",
    COL_AVG: "Averaged over the slots that can roll it, each counting for "
             "how often it occurs. The line under the filters says what the "
             "figure is a chance of.",
    COL_BEST: "The single most favourable slot. 100% means at least one "
              "slot always grants it.",
    COL_STACKS: "What a second copy of the effect does: adds, multiplies, "
                "or is wasted. Hover a cell for the evidence behind its "
                "verdict.",
    COL_CURSE: "Whether relics carrying this effect can also roll a curse "
               "— 'sometimes' by relic, 'always cursed' without exception.",
}

# Buffs read blue, curses red, so which is which never has to be worked out
# from the wording.
BUFF_COLOUR = QColor("#7fb2e5")
CURSE_COLOUR = QColor("#e07a74")


def format_chance(value: float) -> str:
    if value >= 0.01:
        return f"{value * 100:.1f}%"
    return f"{value * 100:.2f}%"


class ChanceItem(QTableWidgetItem):
    """A chance cell that shows a percentage but sorts as a number.

    setText after setData(DisplayRole, float) silently replaces the float
    with the string, so the old cells sorted lexicographically -- "10.0%"
    between "0.20%" and "2.5%", which on a chances column is worse than no
    sorting at all. The value is kept aside and compared directly.
    """

    def __init__(self, value: float):
        super().__init__()
        self.value = float(value)
        self.setText(format_chance(self.value) if value else "—")

    def __lt__(self, other) -> bool:
        return self.value < getattr(other, "value", 0.0)


class EffectTable(QTableWidget):
    """A table that shares its width out by what the reader came for.

    Qt's `Stretch` hands a column whatever is left after every other column
    has taken what it wants, and on this table there was little left. Measured
    on Windows at 150 % scale before this class existed, at a 1067 px window
    -- the width the review ran at: `Effect` rendered at **138** px against
    `Stacking` at 159 and `Colours` at 133, with **573 of 652** names cut
    short, four consecutive rows reading `Successful ...` and no way to tell
    them apart. At an 833 px window `Effect` was **32** px and all 652 were
    cut. The column carrying the name was the narrowest of the eleven, and the
    two columns that answer the tab's question came last in the share-out
    (DR-014).

    The order is reversed here: the name and the description are served first,
    and the nine label columns divide what is over, capped. The share-out runs
    on every width change, as `Stretch` did -- what changed is who is served
    first, not when.
    """

    #: AK-77, in logical px. The name column never goes under the first, the
    #: description column never under the second.
    NAME_FLOOR = 320
    DESCRIPTION_FLOOR = 260

    #: What any other column may take at most. AK-77 asks for a bound "smaller
    #: than the width of `Effect`", and `Effect` is never narrower than
    #: NAME_FLOOR while there is room, so half of NAME_FLOOR keeps that true
    #: with a margin. It is the two enumerations the bound is aimed at:
    #: `Stacking` asked for 159 px to show nine distinct strings and `Colours`
    #: for 133 px to show ten, on Windows at 150 % scale; under the suite's
    #: offscreen font the same two ask for 343 and 295.
    OTHER_CAP = NAME_FLOOR // 2

    def __init__(self, columns: int):
        super().__init__(0, columns)
        self._natural = [0] * columns
        self._headings: list[str] = []

    @property
    def _description_column(self) -> int:
        return self.columnCount() - 1

    def _others(self) -> range:
        return range(1, self._description_column)

    # -- headings ---------------------------------------------------------
    def set_headings(self, headings: list[str],
                     tips: dict[int, str]) -> None:
        """Name the columns, and say on each what it means.

        The names are kept here as well as on the header items because
        `fit_columns` writes a shortened name into the item whenever the
        section is too narrow for the whole one. The full name has to outlive
        that -- to be put back before the next measurement, and to be handed
        to the reader in the tooltip.
        """
        self._headings = list(headings)
        self.setHorizontalHeaderLabels(self._headings)
        for column, name in enumerate(self._headings):
            item = self.horizontalHeaderItem(column)
            if item is None:
                continue
            # The name leads, then whatever the column needs explaining.
            # Every column carries at least its own name here, because a
            # heading narrow enough to read as `vg chanc` is a heading with
            # nowhere else to be read (QA-140); the three that had no tooltip
            # at all -- `Effect`, `Type`, `What it does` -- are exactly the
            # ones a reader had no way back from.
            tip = tips.get(column)
            item.setToolTip(f"{name}\n{tip}" if tip else name)

    def heading(self, column: int) -> str:
        """The column's full name, whatever is drawn in the header today."""
        if 0 <= column < len(self._headings):
            return self._headings[column]
        item = self.horizontalHeaderItem(column)
        return item.text() if item is not None else ""

    def _label_room(self, column: int) -> int:
        """How many px the style leaves this section's text.

        Asked of the style rather than assumed, because the margin around a
        header label is a property of the style and this program runs under
        Fusion while the suite used to render under windowsvista -- 2 px
        against 4, on every one of eleven columns (QA-146). It is the same
        rect `QHeaderView` elides against when its own elide mode is on.

        **The sort arrow is part of the answer.** The style takes its width
        off the label rect, and only for the section that carries it: this
        table sorts on `Type` from the start, and leaving the indicator out of
        the option drew `Type` as `y.` at an 833 px window -- an ellipsis
        clipped in half, which is the very thing being fixed one column over.
        """
        header = self.horizontalHeader()
        option = QStyleOptionHeader()
        option.initFrom(header)
        option.orientation = Qt.Horizontal
        # State_Horizontal, or the style will not take the sort arrow off
        # the label rect: QCommonStyle reads the flag, not the orientation
        # field, and without it `Type` came out as `y.` at 833 px.
        option.state |= QStyle.State_Horizontal
        option.section = column
        option.rect = QRect(0, 0, header.sectionSize(column),
                            max(header.height(), 1))
        if (header.isSortIndicatorShown()
                and header.sortIndicatorSection() == column):
            option.sortIndicator = (
                QStyleOptionHeader.SortDown
                if header.sortIndicatorOrder() == Qt.AscendingOrder
                else QStyleOptionHeader.SortUp)
        return header.style().subElementRect(
            QStyle.SE_HeaderLabel, option, header).width()

    def _restore_headings(self) -> None:
        """Put the full names back, so a measurement never reads a stump.

        `measure_columns` asks Qt how wide each column would like to be, and
        Qt takes the heading into account. Measuring while the heading is
        elided would let a narrow window shrink the column it was elided for,
        and the next wide window would inherit that.
        """
        for column, name in enumerate(self._headings):
            item = self.horizontalHeaderItem(column)
            if item is not None and item.text() != name:
                item.setText(name)

    def _elide_headings(self) -> None:
        """Shorten each heading to the room its section actually leaves it.

        Qt draws a header centred and clips it at both ends, which turned
        `Avg chance` and `Best chance` into `vg chanc` and `est chanc` -- two
        headings a reader cannot tell apart, over the two columns the tab
        exists for (QA-140). An ellipsis says the name is shortened; the
        tooltip set in `set_headings` says what it was.
        """
        metrics = self.horizontalHeader().fontMetrics()
        for column, name in enumerate(self._headings):
            item = self.horizontalHeaderItem(column)
            if item is None:
                continue
            shown = metrics.elidedText(name, Qt.ElideRight,
                                       self._label_room(column))
            if item.text() != shown:
                item.setText(shown)

    def measure_columns(self) -> None:
        """Note what each column would like, then share the width out.

        Called once per refresh, because asking 652 rows how wide they are is
        the expensive part and their contents do not change with the window.
        """
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        self._restore_headings()
        self.resizeColumnsToContents()
        self._natural = [header.sectionSize(column)
                         for column in range(self.columnCount())]
        self.fit_columns()

    def column_widths(self, available: int) -> dict[int, int]:
        """How wide each column should be in `available` px of viewport.

        Kept separate from the widget it sizes so the rule can be read in one
        piece: the two floors are taken off the top, the other columns divide
        what is left up to their cap, and anything still over goes back to the
        two columns the tab is about.

        The share-out always adds up to `available` exactly. A column past the
        right-hand edge is a column the reader cannot get to, because the
        scrollbar that would reach it sits at the bottom edge of the tab
        behind the taskbar (DR-015) -- so where even the two floors do not
        fit, the floors give way rather than the table growing past its own
        viewport. Measured on Windows at 150 % scale: that happens below about
        1 100 logical px of window width, and `Effect` is 310 px there instead
        of 320. Ten pixels of name against `What it does` disappearing off the
        edge is not a trade worth making.
        """
        floors = self.NAME_FLOOR + self.DESCRIPTION_FLOOR
        wanted = {column: min(self._natural[column], self.OTHER_CAP)
                  for column in self._others()}
        # The label columns give way before the two floors do. That is AK-77's
        # order, and it is why every cell carries its own text as a tooltip:
        # squeezed is not the same as lost.
        widths = self._levelled(wanted, available - floors)
        spare = max(available - sum(widths.values()), 2)
        widths[0] = max(spare * self.NAME_FLOOR // floors, 1)
        widths[self._description_column] = max(spare - widths[0], 1)
        return widths

    def _levelled(self, wanted: dict[int, int], budget: int) -> dict[int, int]:
        """Divide `budget` among `wanted`, taking from the widest first.

        Each column in turn, narrowest first, gets the smaller of what it
        wants and an equal share of what is still unspent. A column that wants
        less than its share keeps all of it and leaves the rest to the others,
        so `Type` holds the 37 px its own heading needs while `Stacking` comes
        down from 159 to 51 -- rather than both losing the same percentage,
        which took `Type` to 32 px and drew it as `B...`.

        Never below `minimumSectionSize`, which is the narrowest section Qt
        will draw; below that the widths would be a fiction.
        """
        smallest = self.horizontalHeader().minimumSectionSize()
        order = sorted(wanted, key=lambda column: wanted[column])
        widths: dict[int, int] = {}
        left = budget
        for taken, column in enumerate(order):
            share = max(left // (len(order) - taken), smallest)
            widths[column] = min(wanted[column], share)
            left -= widths[column]
        return widths

    def fit_columns(self) -> None:
        available = self.viewport().width()
        if available <= 0 or not any(self._natural):
            return
        header = self.horizontalHeader()
        for column, width in self.column_widths(available).items():
            header.resizeSection(column, width)
        self._elide_headings()

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt naming
        super().resizeEvent(event)
        self.fit_columns()


def identity(effect: dict) -> tuple:
    """What makes two effect rows genuinely the same effect.

    The params carry a great many rows that are byte-for-byte the same effect
    under the same name -- 1000 "Grief" rows are really 30 effects, ten
    Nightfarers times three strengths. Collapsing on the name alone would be
    wrong, though: "Increased Maximum HP" exists twice as genuinely different
    effects, one granting Max HP +10% and the other Vigor +5. So identity is
    the name together with what the effect actually does, and rows only merge
    when both agree.
    """
    return (
        " ".join(str(effect.get("name", "")).split()),
        tuple(effect.get("sp_effect_ids") or []),
        json.dumps(effect.get("modifiers", {}), sort_keys=True),
    )


def deduplicate(effects: list[dict]) -> list[tuple[dict, int]]:
    """Collapse identical rows, keeping a count of how many were merged."""
    groups: dict[tuple, list[dict]] = collections.OrderedDict()
    for eff in effects:
        groups.setdefault(identity(eff), []).append(eff)
    return [(rows[0], len(rows)) for rows in groups.values()]


def tier_label(effect: dict, siblings: list[dict]) -> str:
    """Where this effect sits in a ladder of same-named, differing strengths.

    Several effects ship as a set of increasing magnitudes under one name --
    the Grief relics are +3 / +6 / +9 on two attributes. They are separate
    effects with their own SpEffect ids, not duplicates, so they each keep a
    row; this labels which rung each one is so the repetition makes sense.
    """
    if len(siblings) < 2:
        return ""
    ordered = sorted(siblings, key=_magnitude)
    try:
        position = next(i for i, e in enumerate(ordered)
                        if e["id"] == effect["id"])
    except StopIteration:
        return ""
    return f"{position + 1} of {len(ordered)}"


def _magnitude(effect: dict) -> tuple:
    """A sort key ranking one variant of an effect against its siblings."""
    numbers = [v for v in effect.get("modifiers", {}).values()
               if isinstance(v, (int, float))]
    return (sum(abs(float(v)) for v in numbers), effect.get("id", 0))


class EffectsTab(QWidget):
    def __init__(self, data: dict):
        super().__init__()
        self.effects = list(data["effects"].values())

        # Ladders and duplicate counts are properties of the game's data, not
        # of what the filters happen to show, so they are worked out once over
        # the whole effect list and looked up per row. Building them from the
        # filtered candidates made `Continuous HP Recovery` say "1 of 2" under
        # `All colours` and nothing at all under a colour filter -- the same
        # effect changing its own definition as the view narrowed (QA-127).
        #
        # The rung is settled per identity and not per row. Which row of an
        # identity group survives the filters is not fixed -- `refresh` keeps
        # the first candidate, and that is a different `id` under a colour
        # filter than with none -- so a lookup that matched on the id found
        # nothing and printed an empty cell for exactly the effects this is
        # about.
        self._copies = collections.Counter(identity(e) for e in self.effects)
        by_name: dict[str, list[dict]] = collections.defaultdict(list)
        for first, _count in deduplicate(self.effects):
            by_name[effecttext.name(first)].append(first)
        self._rung: dict[tuple, str] = {}
        for siblings in by_name.values():
            for effect in siblings:
                self._rung[identity(effect)] = tier_label(effect, siblings)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)

        layout.addWidget(tabheader.heading(HEADING))
        layout.addWidget(tabheader.question(QUESTION))

        controls = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search effects and descriptions…")
        self.search.textChanged.connect(self.refresh)
        controls.addWidget(self.search, 1)

        self.colour_box = QComboBox()
        self.colour_box.addItem("All colours", -1)
        for value, name in model.COLOUR_NAMES.items():
            if value == 4:
                continue  # White is a slot property, never a relic colour
            self.colour_box.addItem(name, value)
        self.colour_box.currentIndexChanged.connect(self.refresh)
        controls.addWidget(self.colour_box)

        self.mode_box = QComboBox()
        self.mode_box.addItem("Normal + Deep", "all")
        self.mode_box.addItem("Normal relics", "normal")
        self.mode_box.addItem("Deep of Night", "deep")
        self.mode_box.currentIndexChanged.connect(self.refresh)
        controls.addWidget(self.mode_box)

        self.rollable_only = QCheckBox("Rollable on relics only")
        self.rollable_only.setChecked(True)
        self.rollable_only.toggled.connect(self.refresh)
        controls.addWidget(self.rollable_only)

        # One class filter rather than two opposed tickboxes. "Stacking" was
        # never a yes/no: whether a second copy counts and whether the number
        # adds or multiplies are separate questions with separate answers, and
        # the old pair could only express the first of them.
        self.stacking_box = QComboBox()
        self.stacking_box.addItem("Any stacking", "all")
        for label in self._stacking_classes(data):
            self.stacking_box.addItem(label, label)
        self.stacking_box.setToolTip(
            "How a second copy behaves, and whether the number adds or "
            "multiplies")
        self.stacking_box.currentIndexChanged.connect(self.refresh)
        controls.addWidget(self.stacking_box)

        self.kind_box = QComboBox()
        self.kind_box.addItem("Buffs and curses", "all")
        self.kind_box.addItem("Buffs only", "buffs")
        self.kind_box.addItem("Curses only", "curses")
        self.kind_box.currentIndexChanged.connect(self.refresh)
        controls.addWidget(self.kind_box)

        # The filter row must be able to shrink below the sum of its widest
        # texts, or it sets the tab's minimum width and, through QTabWidget,
        # the whole window's. The popup lists still show every label in full;
        # only the closed boxes give up width when the window is narrow.
        for box in (self.colour_box, self.mode_box, self.stacking_box,
                    self.kind_box):
            box.setSizeAdjustPolicy(
                QComboBox.AdjustToMinimumContentsLengthWithIcon)
            box.setMinimumContentsLength(8)

        layout.addLayout(controls)

        self.summary = QLabel()
        self.summary.setStyleSheet("color: #8a8a8a; font-size: 11px;")
        # Load-bearing: an unwrapped QLabel's minimum width is its full text
        # width, this line runs to ~3900px, and QTabWidget takes the max of
        # every page's minimum -- so without the wrap this one label forced
        # the whole window wider than most monitors and every tab clipped at
        # the right edge (the stat sheet, the filter boxes on this very row,
        # the Red variants count columns). smoke_layout.py guards the class.
        self.summary.setWordWrap(True)
        layout.addWidget(self.summary)

        self.table = EffectTable(len(COLUMNS))
        # Every column that is not self-explanatory says what it means where
        # the player is already looking. "Pools" in particular was a bare
        # number in the hundreds with nothing anywhere saying what a pool is.
        self.table.set_headings(COLUMNS, HEADER_TIPS)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table, 1)

        self.refresh()

    @staticmethod
    def _stacking_classes(data: dict) -> list[str]:
        """Every class actually present, commonest first.

        Built from the data rather than hard-coded, so the filter can never
        offer a class nothing falls into -- which is what would have happened
        with "different tiers only", a category the game turns out not to
        have. Tier ladders are separate effects and both rungs apply.
        """
        counts = collections.Counter(
            stacking.classify(e) for e in data["effects"].values())
        return [label for label, _n in counts.most_common()]

    @staticmethod
    def _matches(effect: dict, needle: str) -> bool:
        """Search the description too, not just the name.

        Now that descriptions are shown, searching only names would leave the
        user able to read "restores FP on successive attacks" but unable to
        find it by typing that.
        """
        haystack = f"{effecttext.name(effect)} {describe_full(effect)}".lower()
        return needle in haystack

    def refresh(self) -> None:
        needle = self.search.text().strip().lower()
        colour = self.colour_box.currentData()
        mode = self.mode_box.currentData()

        if mode == "normal":
            colour_keys, chance_keys = ["colours"], ["chance"]
        elif mode == "deep":
            colour_keys, chance_keys = ["deep_colours"], ["deep_chance"]
        else:
            colour_keys = ["colours", "deep_colours"]
            chance_keys = ["chance", "deep_chance"]

        kind = self.kind_box.currentData()

        candidates = []
        for eff in self.effects:
            bad = bool(eff.get("is_curse") or eff.get("is_debuff"))
            if kind == "buffs" and bad:
                continue
            if kind == "curses" and not bad:
                continue
            colours = sorted(set().union(*(set(eff[k]) for k in colour_keys)))
            # A curse is rollable, just from a curse pool rather than a colour
            # pool, so it must never be filtered out as "not rollable".
            if self.rollable_only.isChecked() and not colours and not bad:
                continue
            wanted = self.stacking_box.currentData()
            if wanted != "all" and stacking.classify(eff) != wanted:
                continue
            if colour != -1 and colour not in colours:
                continue
            if needle and not self._matches(eff, needle):
                continue
            candidates.append((eff, colours))

        # Collapse identical rows before display. Colours are unioned across
        # the merged rows so nothing is lost by dropping the copies.
        merged: dict[tuple, tuple[dict, set]] = collections.OrderedDict()
        for eff, colours in candidates:
            key = identity(eff)
            if key in merged:
                prev_eff, prev_colours = merged[key]
                merged[key] = (prev_eff, prev_colours | set(colours))
            else:
                merged[key] = (eff, set(colours))

        # The copy count is the game's, not the filter's (AK-81): how many
        # identical rows the params define, whether or not this view shows
        # them all.
        rows = [(eff, sorted(colours), self._copies[identity(eff)])
                for eff, colours in merged.values()]

        # Buffs first, then curses, each alphabetical. Keeping them in one
        # table rather than splitting into a second tab means a search covers
        # both at once, and the colour makes which is which unmissable.
        rows.sort(key=lambda r: (bool(r[0].get("is_curse")
                                      or r[0].get("is_debuff")),
                                 effecttext.name(r[0]).lower()))

        hidden = len(candidates) - len(rows)
        note = (f" {hidden} identical duplicates merged." if hidden else "")
        n_curses = sum(1 for eff, _c, _n in rows
                       if eff.get("is_curse") or eff.get("is_debuff"))
        undescribed = sum(1 for eff, _c, _n in rows
                          if describe_full(eff) == effecttext.NO_DESCRIPTION)
        missing = (f" For {undescribed} the game gives nothing beyond the "
                   f"name." if undescribed else "")
        self.summary.setText(
            f"{len(rows) - n_curses} buffs (blue) then {n_curses} curses "
            f"(red).{note}{missing} {CHANCE_DEFINITION} Where an effect can "
            f"come from several slots you see its average and its best. "
            f"'Tier' marks effects that come in a ladder of strengths under "
            f"one name."
        )

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(rows))
        for r, (eff, colours, copies) in enumerate(rows):
            relevant = []
            for key in chance_keys:
                chance = eff.get(key, {})
                if colour != -1:
                    if str(colour) in chance:
                        relevant.append(chance[str(colour)])
                else:
                    relevant.extend(chance.values())

            slots = sum(c["pools"] for c in relevant)
            # Weighted by how many slots each entry stands for, not averaged
            # over the (colour x mode) buckets. Unweighted, a single
            # guaranteed relic took a fifth of the weight against 240 slots at
            # 0.5%, and `[Wylder] Improved Mind, Reduced Vigor` read 20.4%
            # where a player rolls it on 0.91% of slots -- 129 of 616 effects
            # moved, this one by a factor of 22 (QA-126, AK-80).
            avg = (sum(c["avg"] * c["pools"] for c in relevant) / slots
                   if slots else 0.0)
            best = max((c["max"] for c in relevant), default=0.0)

            display_name = effecttext.name(eff)
            description = describe_full(eff)
            is_bad = bool(eff.get("is_curse") or eff.get("is_debuff"))
            values = [
                display_name,
                TYPE_CURSE if is_bad else TYPE_BUFF,
                self._rung.get(identity(eff), ""),
                copies,
                ", ".join(model.COLOUR_NAMES.get(c, str(c)) for c in colours),
                slots,
                avg,
                best,
                stacking.classify(eff),
                "is a curse" if eff.get("is_curse")
                else CURSE_LABEL.get(eff.get("curse", "never"), ""),
                description,
            ]
            for c, value in enumerate(values):
                if c == COL_COPIES or c == COL_SLOTS:
                    item = QTableWidgetItem()
                    item.setData(Qt.DisplayRole, int(value))
                elif c in (COL_AVG, COL_BEST):
                    item = ChanceItem(float(value))
                    # A rung of a ladder can exist while nothing in the
                    # current filters can roll it. The signal used to hang on
                    # a bare `0` in a column named after loot pools; it lives
                    # on the cell that is showing the dash (AK-78).
                    if not slots:
                        item.setToolTip(UNREACHABLE_TIP)
                else:
                    item = QTableWidgetItem(str(value))
                if c in NUMERIC:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                # Blue for a buff, red for a curse, on the name and on what it
                # does -- the two cells the eye actually lands on.
                if c in (0, COL_TYPE, len(values) - 1):
                    item.setForeground(CURSE_COLOUR if is_bad else BUFF_COLOUR)
                # Where the game itself files this effect in its own UI
                # filters. Only 568 of the effects carry one, so the sentence
                # appears where there is something to say and not otherwise --
                # and it now stands under the name rather than instead of it,
                # because on a 320 px column the name is what the tooltip is
                # most often needed for.
                if c == 0 and eff.get("game_category"):
                    item.setToolTip(
                        f"{display_name}\nThe game files this under: "
                        + eff["game_category"])
                if c == COL_STACKS:
                    # Red is for the classes that cost you something: a second
                    # copy of these is wasted, which is the one case where the
                    # column changes what a player should equip.
                    if stacking.repetition(eff) != stacking.STACKS:
                        item.setForeground(Qt.red)
                    # Naming the deciding field turns the verdict into
                    # something checkable rather than something to take on
                    # trust, which is the whole point of the column. The
                    # verdict itself stands above it now: the column is capped
                    # (EffectTable.OTHER_CAP) and `Exclusive group
                    # (multiplies)` does not fit in 160 px, so a tooltip that
                    # gave only the evidence left the reader with a cut-off
                    # class and its reason underneath.
                    item.setToolTip(
                        f"{item.text()}\n{stacking.evidence(eff)}")
                if c == COL_CURSE and value:
                    item.setForeground(CURSE_COLOUR)
                # The full text is often wider than the column; the tooltip
                # gives it in full without forcing a huge column.
                if c == len(values) - 1:
                    item.setToolTip(description)
                    if description == effecttext.NO_DESCRIPTION:
                        item.setForeground(Qt.gray)
                # Every column of this table is narrower than its longest
                # cell at some window width -- the label columns because they
                # are capped (EffectTable.OTHER_CAP), the name column because
                # 80 of 652 names are still wider than the 320 px floor at a
                # 1067 px window. Cut short has to mean reachable, not lost,
                # so a cell with no tooltip of its own carries its text as one.
                if not item.toolTip():
                    item.setToolTip(item.text())
                self.table.setItem(r, c, item)

        # Enabling sorting makes Qt immediately re-sort by whatever indicator
        # the header is showing, which would scatter the curses back among the
        # buffs. Sorting on Type explicitly restores the grouping and leaves
        # the header still clickable.
        self.table.setSortingEnabled(True)
        self.table.sortByColumn(COL_TYPE, Qt.AscendingOrder)
        self.table.measure_columns()
