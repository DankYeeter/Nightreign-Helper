"""Browsable table of every relic effect, its roll chance and what it does."""

from __future__ import annotations

import collections
import json

from PySide6.QtCore import QEvent, QObject, QPoint, QRect, QSize, Qt, QTimer
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QStyle, QStyleOptionHeader, QTableWidget, QTableWidgetItem, QToolTip,
    QVBoxLayout, QWidget,
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

#: The one definition of the `Copies` column, and the only one.
#:
#: The column showed a bare 1 or 2 and was explained on the header alone, in
#: a tooltip that opens after three quarters of a second of a pointer held
#: still. The player of 2026-09-06 never reached it and guessed: "how many
#: identical copies exist in different slots" -- which is what `Relic slots`
#: counts, not this. What it really counts is entries in the game's own
#: effect table: 2 076 rows in the current dataset resolve to 1 064 distinct
#: effects, and under the tab's opening filters 620 rows say 1, 29 say 2, two
#: say 3 and one says 4.
#:
#: Two things the wording has to get right. The count is the game's and not
#: the view's (AK-81): 29 of the 68 repeated effects differ between their
#: copies in the colours they roll on, so a filter can hide a copy while the
#: number keeps counting it. And it is not a quantity a player carries, which
#: is exactly the reading he had.
#:
#: Written once and used twice -- in the sentence over the table where `Tier`
#: is explained and it worked, and in the header tooltip that a shortened
#: `Co...` still has to answer with. One string, so the two cannot drift into
#: the disagreement AK-79 is about.
COPIES_DEFINITION = (
    "'Copies' is how many separate entries the game's own data holds for one "
    "and the same effect — merged into a single row here, and counted over "
    "all of them whatever the filters show. It is not something you carry: "
    "'Relic slots' says how many slots can roll it, 'Stacking' what a second "
    "one does.")

#: The one definition of the `Comes with curse` column, and the only one.
#:
#: QA-169: the paragraph over the table explained ten of this tab's eleven
#: columns and left this one out. The player of 2026-09-06 guessed right --
#: but guessed, which is the finding the sentence below closes: the answer
#: existed only in a header tooltip he never reached.
#:
#: 'Sometimes' and 'always cursed' are not two strengths of one warning --
#: they answer whether picking a different relic lets you dodge the curse
#: at all. 'Sometimes': some of the relics carrying the effect also carry a
#: curse and some do not, so the choice is yours. 'Always cursed': none do
#: not, so there is no dodging it.
#:
#: What this sentence deliberately does not claim: that the verdict holds
#: under every filter above. It is worked out once per effect in
#: `nrdata/extract.py`, from which of the effect's relics carry a curse
#: slot, not from what is currently searched or filtered for -- but ten of
#: the game's 1 064 distinct effects exist as two data rows that disagree
#: on it (`sometimes` on one row, `never` on the other -- same name, same
#: modifiers), and the merge in `refresh()` below shows whichever row
#: survives the active filters rather than combining them the way it
#: already does for `Colours` (AK-81). Unticking `Rollable on relics only`
#: with `All colours` selected exposes it: those ten effects then read
#: blank instead of `sometimes`. Found while writing this constant and
#: reported rather than fixed here -- T-073 is one sentence, not a rewrite
#: of the merge.
#:
#: Written once and used twice, exactly as `COPIES_DEFINITION`: in the
#: sentence over the table and in the header tooltip (`COL_CURSE` entry).
CURSE_DEFINITION = (
    "'Comes with curse' says whether rolling this effect can also bring "
    "you a curse. 'Sometimes' means only some of the relics that carry "
    "the effect also carry a curse, so which one you take decides it. "
    "'Always cursed' means every one of them does, so the effect never "
    "comes without one.")

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
    COL_COPIES: COPIES_DEFINITION,
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
    COL_CURSE: CURSE_DEFINITION,
}

#: What stands beside each of the four filter boxes (QA-156).
#:
#: The boxes carried no caption at all, so a reader had to work out what a
#: box was for from the value it happened to be showing -- "All colours"
#: suggests a colour filter, and the other three suggest nothing. Each label
#: is the name of the column the box filters, so the row and the table say
#: the same word for the same thing.
#:
#: They are drawn as `FilterCaption`, and that is not decoration: as plain
#: labels they cost the tab 160 logical px of minimum width and the window 56
#: (760 to 816) on Windows under Fusion at 150 % scale -- and, under the wider
#: font the suite renders with, they took the window's floor from 964 to
#: **1276** px, at which point every case that asks for a 833, 1067 or 1250 px
#: window skips itself rather than measuring the wrong thing. 47 cases went
#: quiet in one run. As `FilterCaption` they cost the window nothing.
COLOUR_LABEL = "Colour"
MODE_LABEL = "Relics"
STACKING_LABEL = "Stacking"
KIND_LABEL = "Type"

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


#: What a shortened heading divides the style's own tooltip delay by.
#:
#: The style's figure is the reference rather than a millisecond count of
#: this module's own, so the wait stays proportional under a style that
#: thinks differently about hovering. Under Fusion, which is what
#: `nrplanner.app.main` sets and therefore what a player runs,
#: `SH_ToolTip_WakeUpDelay` is 700 ms and a quarter of it is 175.
#:
#: It sits between two bounds with room either side. Above: anything near 700
#: changes nothing, and 700 ms is the wait the player of 2026-09-05 gave up
#: before reaching. Below: a pointer merely sweeping across the table on its
#: way somewhere else spends about 100 ms over the widest heading this table
#: ever shortens -- the label columns are capped at 160 logical px, and a
#: sweep across a 1600 px window in one second crosses 160 px in 100 ms
#: (Windows, 150 % scale, Fusion, logical px) -- and a delay under that would
#: open tooltips at a reader who was not asking. How long a reader who *is*
#: asking holds still is measured nowhere, and a figure invented for it would
#: be the guess A7 forbids; a quarter is taken because it clears both bounds
#: by a factor, not because it is the only value that does.
WAKE_UP_DIVISOR = 4


class FilterCaption(QLabel):
    """The word beside a filter box, which gives up room before the box does.

    A plain `QLabel` reports its whole text as its minimum width, a layout
    hands that on to its page and `QTabWidget` hands the widest page's minimum
    to the window -- so four captions on this row set the floor for the whole
    program. Measured on 2026-09-06 in logical px: on Windows under Fusion at
    150 % scale the four cost the tab 160 px and the window 56 (760 to 816),
    and under the suite's own wider font they took the window's floor from
    964 to 1276, at which every case measuring a 833, 1067 or 1250 px window
    skipped itself. The captions were bought with the coverage of 47 cases.

    So they follow the rule the combo boxes beside them already follow: shrink
    below your widest text, and show it in full wherever there is room. The
    minimum is nothing; the preferred size is still the whole word, so the
    word is what stands on any window that has room for it, and where a window
    has not the caption shortens rather than the box it belongs to.

    What is left of the price, measured the same way: the four cost the tab
    24 logical px -- the row's own 6 px of spacing four times over, which no
    widget can give back -- and the window nothing at all, 760 px before and
    760 after. Under the suite's font the window's floor goes from 964 to 988,
    which leaves every width the suite measures at reachable.
    """

    def minimumSizeHint(self) -> QSize:  # noqa: N802 - Qt naming
        """No width at all. The height stays whatever the font asks for."""
        return QSize(0, super().minimumSizeHint().height())

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt naming
        """Draw the caption, shortened to the room it was given.

        `QLabel` clips instead of shortening, which turns `Stacking` into
        `Stackin` with nothing to say that anything was taken -- the exact
        complaint QA-140 records about the table headings one row down.
        """
        painter = QPainter(self)
        painter.setPen(self.palette().color(self.foregroundRole()))
        painter.drawText(
            self.contentsRect(), int(self.alignment()),
            self.fontMetrics().elidedText(self.text(), Qt.ElideRight,
                                          self.contentsRect().width()))


class HeadingHint(QObject):
    """Open a shortened heading's tooltip sooner than the style would.

    A heading this table had to cut short carries its whole name in its
    tooltip (QA-140), and T-064 measured at the running window that the
    tooltip does appear -- after **750-800 ms** of a pointer held still, which
    is Fusion's own `SH_ToolTip_WakeUpDelay` of 700 ms plus the platform's
    overhead. The player of 2026-09-05 "waited only briefly" over
    `Comes with c…` and saw nothing. That is QA-151 whole: information being
    on the screen is not the same as a reader reaching it inside the time he
    gives a hover, and at 833 px three headings read `Co…` with no way to
    tell them apart until he does.

    **The shorter wait is deliberate and not a side effect.** It is granted to
    nothing but a heading this table has itself shortened; a heading drawn
    whole is left entirely to the style. So the quick answer appears exactly
    where something was taken away, and its appearing is itself the sign that
    there is more to see -- the half of the finding an ellipsis alone did not
    cover.

    Nothing is said twice on screen for it. The tooltip that opens is the one
    `set_headings` already wrote; what changed is when.
    """

    def __init__(self, table: EffectTable):
        super().__init__(table)
        self._table = table
        self._section = -1
        self._at = QPoint()
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._answer)
        table.horizontalHeader().viewport().installEventFilter(self)

    def delay(self) -> int:
        """How long a pointer rests on a shortened heading before it opens.

        Asked of the style on every hover rather than worked out once, for
        the same reason `_label_room` asks: the program runs under Fusion
        while the suite used to render under windowsvista, and a figure cached
        at construction would be the wrong style's figure whenever the two
        differ.
        """
        header = self._table.horizontalHeader()
        asked = header.style().styleHint(QStyle.SH_ToolTip_WakeUpDelay,
                                         None, header)
        return max(1, asked // WAKE_UP_DIVISOR)

    def eventFilter(self, watched, event) -> bool:  # noqa: N802 - Qt naming
        """Watch the header for a pointer resting on a shortened heading.

        Nothing is ever swallowed. The style's own tooltip machinery goes on
        working untouched behind this, which is what keeps the heading
        reachable even where this object is never reached at all.
        """
        if event.type() == QEvent.MouseMove:
            self._aim(event.position().toPoint(),
                      event.globalPosition().toPoint())
        elif event.type() in (QEvent.Leave, QEvent.MouseButtonPress,
                              QEvent.Wheel):
            self._forget()
        return False

    def _aim(self, where: QPoint, globally: QPoint) -> None:
        """Start counting, if the heading under `where` was cut short."""
        header = self._table.horizontalHeader()
        section = header.logicalIndexAt(where)
        item = (self._table.horizontalHeaderItem(section)
                if section >= 0 else None)
        if item is None or item.text() == self._table.heading(section):
            self._forget()
            return
        self._at = globally
        # Not restarted while the pointer stays on the same heading: a reader
        # holding still over one column is one hover, and a pixel of movement
        # inside it would otherwise put the answer off again indefinitely.
        if section != self._section:
            self._section = section
            self._timer.start(self.delay())

    def _forget(self) -> None:
        self._timer.stop()
        self._section = -1

    def _answer(self) -> None:
        if self._section < 0:
            return
        header = self._table.horizontalHeader()
        item = self._table.horizontalHeaderItem(self._section)
        if item is None:
            return
        # The section's own rectangle travels with the text, so Qt takes the
        # tooltip away by itself the moment the pointer leaves the heading it
        # belongs to. Without it a quick answer would follow the reader across
        # the table naming a column he is no longer over.
        QToolTip.showText(
            self._at, item.toolTip(), header.viewport(),
            QRect(header.sectionViewportPosition(self._section), 0,
                  header.sectionSize(self._section), header.height()))


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
        # Owned by the table, because what it answers with -- the full name --
        # is the table's own, and no other heading on this tab is ever
        # shortened. See HeadingHint for why the wait is not the style's.
        self.hint = HeadingHint(self)

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

    def _label_room(self, column: int, section: int | None = None) -> int:
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

        `section` names a width to ask about instead of the one the header
        happens to have. That is what lets `width_for_full_headings` put a
        window width to the same style, with the same sort arrow, that will
        decide the elision once the window is that wide -- rather than
        assuming the margin and getting it wrong under the next style.
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
        option.rect = QRect(
            0, 0,
            header.sectionSize(column) if section is None else section,
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
        for column, name in enumerate(self._headings):
            item = self.horizontalHeaderItem(column)
            if item is None:
                continue
            shown = self._as_drawn(column, self._label_room(column))
            if item.text() != shown:
                item.setText(shown)

    def _as_drawn(self, column: int, room: int) -> str:
        """The heading of `column` as it would read in `room` px of label."""
        metrics = self.horizontalHeader().fontMetrics()
        return metrics.elidedText(self._headings[column], Qt.ElideRight, room)

    def headings_as_drawn(self, widths: dict[int, int]) -> list[str]:
        """Every heading as the header would read at these section widths.

        The question `_elide_headings` answers per column, asked of a whole
        share-out. Through `_as_drawn`, so there is one elision rule and it
        is the one the header on screen uses -- a caller here cannot be told
        a heading is whole while the header shortens it.

        The words and not merely which of them are shortened: a heading that
        no width can show whole still shows *more* of itself as its column
        grows, and a width that gave the reader fewer letters than he could
        have had would be the same fault as the one being fixed.
        """
        return [self._as_drawn(column, self._label_room(column, widths[column]))
                if column in widths else self._headings[column]
                for column in range(len(self._headings))]

    def width_for_full_headings(self) -> int:
        """The narrowest viewport width at which the headings read as well
        as they ever will -- normally, at which none is shortened.

        **Derived, not chosen.** The window used to open at a width set by
        hand, and at that width one heading of eleven was drawn as
        `Comes with c…` -- the first thing a reader saw, and the thing two
        `power-user` runs in a row reported (QA-140, T-069). A wider hand-set
        number would only move the same problem to the next font: the widths
        this table needs come out of the data, the style and the font, and
        all three differ between one machine and the next. Measured on
        2026-09-06, same tree, same data: the nine middle columns ask for
        848 px together under Segoe UI 9 on Windows at 150 % scale and for
        1 185 px under the suite's offscreen font -- 337 px apart for the
        same eleven words.

        So the number is asked of `column_widths`, the share-out that will
        actually be applied, and of the style that will actually draw the
        header:

        * the widest the table ever grows to is the two floors plus what
          every other column asks for, capped. Past that, extra width goes to
          `Effect` and `What it does` and no heading gains a letter, so
          whatever is still shortened there is shortened for good;
        * from there it steps back one pixel at a time for as long as the
          header reads word for word the same, and stops at the first pixel
          that costs a letter.

        Tight by construction, in both directions: one pixel wider buys the
        reader nothing, one pixel narrower takes something away. Both are
        what the guard asserts, and both hold whatever the font does --
        including the case where `OTHER_CAP` bounds a column below what its
        own name needs, which no width can rescue and which is where the
        suite's offscreen font puts `Comes with curse`.
        """
        floors = self.NAME_FLOOR + self.DESCRIPTION_FLOOR
        widest = floors + sum(min(self._natural[column], self.OTHER_CAP)
                              for column in self._others())
        best = self.headings_as_drawn(self.column_widths(widest))
        narrowest = widest
        while (narrowest > floors
               and self.headings_as_drawn(
                   self.column_widths(narrowest - 1)) == best):
            narrowest -= 1
        return narrowest

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

        controls.addWidget(FilterCaption(COLOUR_LABEL))
        self.colour_box = QComboBox()
        self.colour_box.addItem("All colours", -1)
        for value, name in model.COLOUR_NAMES.items():
            if value == 4:
                continue  # White is a slot property, never a relic colour
            self.colour_box.addItem(name, value)
        self.colour_box.currentIndexChanged.connect(self.refresh)
        controls.addWidget(self.colour_box)

        controls.addWidget(FilterCaption(MODE_LABEL))
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
        controls.addWidget(FilterCaption(STACKING_LABEL))
        self.stacking_box = QComboBox()
        self.stacking_box.addItem("Any stacking", "all")
        for label in self._stacking_classes(data):
            self.stacking_box.addItem(label, label)
        self.stacking_box.setToolTip(
            "How a second copy behaves, and whether the number adds or "
            "multiplies")
        self.stacking_box.currentIndexChanged.connect(self.refresh)
        controls.addWidget(self.stacking_box)

        controls.addWidget(FilterCaption(KIND_LABEL))
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
            f"one name. {COPIES_DEFINITION} {CURSE_DEFINITION}"
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
