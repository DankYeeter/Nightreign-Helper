"""What a player can and cannot see: window height, cards, columns.

Four findings of T-056 are one sentence each and all of them are pixels
(DR-013 to DR-016). What guarded them before this file: nothing. Two
independent searches of `tests/` on 2026-09-05 -- for `minimumSizeHint` and
for `viewport` -- found 0 files that read a rendered size of any of the six
content tabs. Measured on the tree before a line was changed, on Windows at
150 % scale:

* the window asked for **1225** logical px of height, 1838 physical, against
  a screen 1600 px tall, because `Deep of Night` asked for **1195** and
  `QTabWidget` hands the tallest page to the whole window;
* the Nightlord grid drew **4 of 10** cards sliced at 1067 px and **2 of 10**
  at 1250 px, with a horizontal scrollbar at the bottom edge of the tab;
* the arsenal drew **15 of 77** tiles sliced at 1067 px, and **0** tiles at
  all until the reader unfolded a heading;
* the effects table gave `Effect` **138** px at 1067 px against `Stacking` at
  159, with **573 of 652** names cut short, and **32** px at 833 px.

**The suite renders offscreen and the offscreen font is not the player's.**
Measured the same day: an effect name is about 12 px per character under
`QT_QPA_PLATFORM=offscreen` and about 6 under the Windows platform, so every
absolute pixel count here comes out differently in a green run than it does on
the machine. The assertions are therefore written as relations that hold on
both -- `Effect` is the widest column, no card is sliced, no horizontal
scrollbar -- and the two absolute floors are asserted only at the widths at
which they hold on the narrower of the two. The figures above and the
screenshots under `docs/screenshots/2026-09-05-T058/` are the evidence for the
player's machine; this file is the evidence that a change would be noticed.

**Nothing here is imported from the module it guards.** 860, 320 and 260 are
written out as `UI_SPEC.md` states them; the column count is never
recomputed, only the rendered rectangles are read. A case that asked
`cardgrid.columns_for` how many columns there should be would agree with the
grid however wrong both were -- which is exactly how `COLUMNS = 4` survived.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import (
    QLabel, QScrollArea, QStyle, QStyleOptionHeader,
)

from nrplanner import arsenaltab, bosstab

from tests import rendered, tabtext

#: AK-71. No tab may ask the window for more height than this.
TAB_HEIGHT_LIMIT = 860

#: What a shortened heading ends with. U+2026, the one Qt's own `elidedText`
#: appends -- written out here rather than imported so a change of character
#: shows up as a failure rather than following the module under test.
ELLIPSIS = "…"

#: The eleven headings of the effects table, in order, written out rather
#: than imported: `Relic slots` is AK-78's second outcome verbatim and the
#: other ten are what the tab has drawn since T-057. A case that read them
#: back off the module would follow a heading that had quietly become
#: something else, which is the whole thing this file is here not to do.
EFFECT_COLUMNS = ("Effect", "Type", "Tier", "Copies", "Colours",
                  "Relic slots", "Avg chance", "Best chance", "Stacking",
                  "Comes with curse", "What it does")

#: AK-77, the two floors, in logical px.
NAME_FLOOR = 320
DESCRIPTION_FLOOR = 260

#: AK-77's own test width.
EFFECTS_TEST_WIDTH = 1516

#: AK-72, AK-84 and AK-90 name 1250, 1600 and 2100. The two narrower ones are
#: DR-013's and DR-016a's own widths: the review ran on a 2560x1600 screen at
#: 150 % scale, so its "1600 px" and "1250 px" are 1067 and 833 logical px --
#: and at 1250 logical px the arsenal is not broken at all. Leaving them out
#: would have meant testing three widths at which DR-016a does not reproduce.
WIDTHS = (833, 1067, 1250, 1600, 2100)

#: The two cards DR-013 found missing while the line above them said
#: "10 Nightlords", and the two the same grid cut in half one column earlier.
NAMED_MISSING = ("Maris", "Harmonia")

#: AK-97: the last line of the Deep of Night tab, which was on no screen and
#: reachable by no scrollbar.
LAST_DEEP_LINE = "Read from the game's own depth table."

TABS = ("effects_tab", "weapons_tab", "boss_tab", "deep_tab", "depths_tab",
        "events_tab")


# -- AK-71: the height every tab imposes on the window ---------------------

def test_no_content_tab_asks_the_window_for_more_than_the_limit(
        game_data, qapp):
    """AK-71. One page over the limit is a window that will not fit.

    Measured as a whole window rather than as six loose widgets, because
    `QTabWidget` taking the maximum is the mechanism that turns one tall page
    into a tall program.
    """
    with rendered.laid_out(game_data, "effects_tab", 1600) as (window, _):
        too_tall = {name: getattr(window, name).minimumSizeHint().height()
                    for name in TABS
                    if getattr(window, name).minimumSizeHint().height()
                    > TAB_HEIGHT_LIMIT}
        assert not too_tall, (
            f"these tabs set a minimum height over {TAB_HEIGHT_LIMIT} px and "
            f"hand it to the whole window: {too_tall}")


def test_the_last_line_of_deep_of_night_can_be_reached_by_scrolling(
        game_data, qapp):
    """AK-97, the half of it a height figure cannot show.

    The tab may be taller than the window; what it may not be is taller than
    the window with no way down. 900 px is the height AK-97 names.
    """
    with rendered.laid_out(game_data, "deep_tab", 1600, 900) as (_, tab):
        line = next((label for label in tab.findChildren(QLabel)
                     if label.text().strip() == LAST_DEEP_LINE), None)
        assert line is not None, (
            f"the tab no longer draws {LAST_DEEP_LINE!r}, so this case is "
            f"watching nothing")
        areas = [area for area in tab.findChildren(QScrollArea)
                 if area.widget() is not None
                 and line in area.widget().findChildren(QLabel)]
        assert areas, (
            "the last line sits in no scroll area, so a window shorter than "
            "the tab cannot reach it -- DR-015 as it was found")
        rendered.scrolled_to_bottom(areas[0])
        assert rendered.fully_visible(line, areas[0]), (
            "scrolled to the bottom, the last line is still not on screen")


# -- QA-146: which machine these figures are off -------------------------

def test_the_suite_measures_under_the_appearance_the_program_starts_with(
        qapp):
    """QA-146. The guards ran under one style and the program under another.

    Applying the program's own `apply_appearance` to the application the suite
    is already running under has to change nothing. That is the whole claim,
    and it holds either way round: a fixture that stopped applying it fails
    here, and so would a program that started applying something else without
    the suite following.

    Not asserted against the literal `"Fusion"`: what matters is that the two
    agree, not which of the two they agree on.
    """
    from nrplanner import app as appmod

    style = qapp.style().objectName()
    palette = QPalette(qapp.palette())
    appmod.apply_appearance(qapp)
    assert qapp.style().objectName() == style, (
        f"the suite measures under the {style!r} style and the program starts "
        f"under {qapp.style().objectName()!r}; every pixel figure in this "
        f"file is then off a machine nobody runs")
    assert qapp.palette() == palette, (
        "the suite measures under a different palette than the program starts "
        "with, and the palette moves a Qt style's own metrics")


# -- AK-72 / AK-90: every Nightlord card, whole ---------------------------

@pytest.mark.parametrize("width", WIDTHS)
def test_every_nightlord_card_is_drawn_whole(game_data, qapp, width):
    """AK-90. Ten cards, none of them sliced, at every width."""
    with rendered.laid_out(game_data, "boss_tab", width) as (_, tab):
        area = next(a for a in tab.findChildren(QScrollArea)
                    if a.widget() is tab.holder)
        cards = tab.holder.findChildren(bosstab.BossCard)
        assert len(cards) == len(tab.bosses), (
            f"{len(cards)} cards drawn for {len(tab.bosses)} Nightlords")
        cut = rendered.clipped(cards, area.viewport())
        assert not cut, (
            f"at {width} px these cards are cut off at the viewport edge: "
            f"{[c.boss['name'] for c in cut]}")
        assert not area.horizontalScrollBar().isVisible(), (
            f"at {width} px the card area needs a horizontal scrollbar, and "
            f"that scrollbar sits at the bottom edge of the tab")


#: QA-147. The panel takes at most this share of the tab, so `PANEL_SHARE - 1`
#: parts are always left for the cards it describes. Written out here rather
#: than imported: a case reading the ratio back off the module would hold
#: whatever ratio the module had.
PANEL_SHARE = 3


@pytest.mark.parametrize("width", WIDTHS)
def test_the_detail_panel_gives_way_where_the_cards_run_out_of_room(
        game_data, qapp, width):
    """QA-147. A fixed 330 px panel took two fifths of a narrow tab.

    At 833 px it held 330 px of `Select a Nightlord` while the ten cards it
    describes stood one to a row in the 463 px left over. What it gets now
    depends on how much tab there is, so the claim is a relation and holds at
    every width rather than at a figure.

    Read off the two rendered widths, and the share is compared against the
    tab's own width rather than against their sum -- the sum would move with
    whatever margins the layout has and would hide a panel that had eaten
    them.
    """
    with rendered.laid_out(game_data, "boss_tab", width) as (_, tab):
        area = next(a for a in tab.findChildren(QScrollArea)
                    if a.widget() is tab.holder)
        panel = next(a for a in tab.findChildren(QScrollArea)
                     if a is not area)
        assert panel.width() * PANEL_SHARE <= tab.width(), (
            f"at {width} px the tab is {tab.width()} px, the detail panel "
            f"holds {panel.width()} of it and the cards {area.width()}")
        assert area.width() > panel.width(), (
            f"at {width} px the cards have {area.width()} px and the detail "
            f"panel {panel.width()}")


@pytest.mark.parametrize("width", WIDTHS)
def test_the_two_cards_the_review_lost_are_among_them(game_data, qapp, width):
    """AK-90 by name. `Maris` and `Harmonia` were column four."""
    with rendered.laid_out(game_data, "boss_tab", width) as (_, tab):
        area = next(a for a in tab.findChildren(QScrollArea)
                    if a.widget() is tab.holder)
        whole = {card.boss["name"]
                 for card in tab.holder.findChildren(bosstab.BossCard)
                 if rendered.inside_horizontally(card, area.viewport())}
        assert set(NAMED_MISSING) <= whole, (
            f"at {width} px {sorted(set(NAMED_MISSING) - whole)} is not drawn "
            f"whole, while the line above the grid counts it")


def test_the_count_above_the_grid_matches_the_cards_drawn(game_data, qapp):
    """The half of DR-013 that made it a lie rather than a nuisance.

    "10 Nightlords" over eight visible cards is the program contradicting
    itself, and it is the sentence that stops a reader looking for the rest.
    """
    with rendered.laid_out(game_data, "boss_tab", 1067) as (_, tab):
        area = next(a for a in tab.findChildren(QScrollArea)
                    if a.widget() is tab.holder)
        whole = [card for card in tab.holder.findChildren(bosstab.BossCard)
                 if rendered.inside_horizontally(card, area.viewport())]
        claimed = tab.summary.text().split()[0]
        assert claimed == str(len(whole)), (
            f"the line says {claimed!r} Nightlords and {len(whole)} cards are "
            f"drawn whole")


# -- AK-84: every arsenal tile, whole, and one section already open -------

@pytest.mark.parametrize("width", WIDTHS)
def test_every_weapon_tile_is_drawn_whole(game_data, qapp, width):
    """AK-84. A tile cut off loses its figures first: they are right-aligned.

    The count is asserted before the clipping, because a tab that has drawn
    nothing clips nothing -- which is the shape a broken version of this case
    would take.
    """
    with rendered.laid_out(game_data, "weapons_tab", width, 950) as (_, tab):
        tiles = [tile for tile in tab.findChildren(arsenaltab.Tile)
                 if tile.isVisible()]
        assert tiles, (
            f"no tile is on screen at {width} px, so nothing here is measured")
        cut = rendered.clipped(tiles, tab.scroll.viewport())
        assert not cut, (
            f"at {width} px {len(cut)} of {len(tiles)} tiles are cut off at "
            f"the viewport edge, and their figures go first")
        assert not tab.scroll.horizontalScrollBar().isVisible(), (
            f"at {width} px the tile area needs a horizontal scrollbar")


def test_the_arsenal_shows_a_tile_without_being_asked(game_data, qapp):
    """AK-83. The tab with the most data opened on an empty black page."""
    with rendered.laid_out(game_data, "weapons_tab", 1600, 950) as (_, tab):
        visible = [tile for tile in tab.findChildren(arsenaltab.Tile)
                   if tile.isVisible()]
        assert visible, (
            "the tab opens with every heading collapsed: a reader meets "
            "1 952 entries as three lines of text and blank space (DR-017)")


def test_opening_the_tab_does_not_build_the_whole_arsenal(game_data, qapp):
    """The other side of AK-83, and the reason the sections are lazy.

    A first view that opened everything would answer AK-83 by building tens
    of thousands of widgets on a tab the reader may only be passing through.
    The bound is the count of one family, generously: `Weapons (1792)` in one
    go is the outcome this forbids.
    """
    with rendered.laid_out(game_data, "weapons_tab", 1600, 950) as (_, tab):
        built = tab.findChildren(arsenaltab.Tile)
        assert len(built) < 500, (
            f"{len(built)} tiles were built before the reader asked for "
            f"anything")


# -- AK-77: the column that carries the name ------------------------------

#: Where the two floors of AK-77 are asserted. Below roughly 1 100 logical px
#: of window width the eleven columns and the two floors do not fit together
#: at all, and the module gives the floors up rather than push a column past
#: the right-hand edge, where no reachable scrollbar leads. Measured on
#: Windows at 150 %% scale: `Effect` 310 px at 1067 px, 321 px at 1250 px.
FLOOR_WIDTHS = (1250, EFFECTS_TEST_WIDTH, 1600, 2100)


@pytest.mark.parametrize("width", WIDTHS + (EFFECTS_TEST_WIDTH,))
def test_the_effect_column_is_the_widest_column_at_every_width(
        game_data, qapp, width):
    """AK-77's first sentence, read off the header rather than off a constant.

    The column that carries the name was the narrowest of the eleven, at
    138 px against `Stacking` at 159 on a 1067 px window and at 32 px on an
    833 px one, with every one of the 652 names cut short.
    """
    with rendered.laid_out(game_data, "effects_tab", width) as (_, tab):
        header = tab.table.horizontalHeader()
        # By position, not by the drawn heading: since QA-140 a narrow section
        # shortens what stands in it, and a case keyed on the drawn text would
        # stop recognising the very column it is about.
        widths = {name: header.sectionSize(column)
                  for column, name in enumerate(EFFECT_COLUMNS)}
        wider = {name: size for name, size in widths.items()
                 if name != EFFECT_COLUMNS[0]
                 and size >= header.sectionSize(0)}
        assert not wider, (
            f"at {width} px these columns are at least as wide as `Effect` "
            f"({header.sectionSize(0)} px): {wider}")


@pytest.mark.parametrize("width", FLOOR_WIDTHS)
def test_the_two_reading_columns_hold_their_floors(game_data, qapp, width):
    """AK-77's two figures, at the widths at which they are reachable."""
    with rendered.laid_out(game_data, "effects_tab", width) as (_, tab):
        header = tab.table.horizontalHeader()
        last = tab.table.columnCount() - 1
        widths = {name: header.sectionSize(column)
                  for column, name in enumerate(EFFECT_COLUMNS)}
        assert header.sectionSize(0) >= NAME_FLOOR, (
            f"at {width} px `Effect` is {header.sectionSize(0)} px, under the "
            f"{NAME_FLOOR} px floor: {widths}")
        assert header.sectionSize(last) >= DESCRIPTION_FLOOR, (
            f"at {width} px `What it does` is {header.sectionSize(last)} px, "
            f"under the {DESCRIPTION_FLOOR} px floor: {widths}")


@pytest.mark.parametrize("width", WIDTHS)
def test_the_effects_table_needs_no_horizontal_scrollbar(
        game_data, qapp, width):
    """A13, and the other half of DR-014.

    A column past the right-hand edge is unreachable on this program, because
    the scrollbar that would reach it sits at the bottom edge of the tab,
    behind the taskbar (DR-015). This is the case that keeps the two floors
    above from being bought at that price.
    """
    with rendered.laid_out(game_data, "effects_tab", width) as (_, tab):
        header = tab.table.horizontalHeader()
        total = sum(header.sectionSize(column)
                    for column in range(tab.table.columnCount()))
        assert not tab.table.horizontalScrollBar().isVisible(), (
            f"at {width} px the table is {total} px wide in a "
            f"{tab.table.viewport().width()} px viewport")


def test_every_cut_off_cell_carries_its_full_text(game_data, qapp):
    """Capped has to mean reachable, not lost.

    Every column of this table is narrower than its longest cell at some
    width, so a cell whose text does not fit has to hand it over some other
    way. The check is on the rendered width, not on a guessed one.
    """
    with rendered.laid_out(game_data, "effects_tab", 1600) as (_, tab):
        table = tab.table
        metrics = table.fontMetrics()
        header = table.horizontalHeader()
        naked = []
        for row in range(min(table.rowCount(), 120)):
            for column in range(table.columnCount()):
                cell = table.item(row, column)
                if cell is None or not cell.text():
                    continue
                room = header.sectionSize(column) - 8
                if (metrics.horizontalAdvance(cell.text()) > room
                        and cell.text() not in cell.toolTip()):
                    naked.append((row, column, cell.text()))
        assert not naked, (
            f"{len(naked)} cells are cut off and their text is nowhere else; "
            f"first three: {naked[:3]}")


# -- QA-140: the column headings, which the tooltip promise did not cover --

def header_label_room(table, column: int) -> int:
    """The px the style leaves this heading, asked of the style directly.

    Not taken from the module under test and not a guessed margin: this is the
    rect Qt itself hands the header label, so a heading elided against a
    different width than the one it is drawn in still shows up here as text
    that does not fit. The margin is 2 px a side under Fusion and 4 under
    windowsvista, which is one of the two things QA-146 is about.

    The sort arrow counts, and only on the section carrying it. Leaving it out
    is a mistake worth ten px: it drew `Type` -- the column this table sorts
    on from the start -- as `y.` at an 833 px window, an ellipsis cut in half.
    """
    header = table.horizontalHeader()
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


@pytest.mark.parametrize("width", WIDTHS)
def test_no_column_heading_is_drawn_cut_off(game_data, qapp, width):
    """QA-140. A heading was clipped at both ends, mid-word and unmarked.

    Measured on Windows at 150 % scale under the style the program sets:
    `Avg chance` and `Best chance` both drew as four letters out of the middle
    of the word -- `vg chanc` and `est chanc` -- over the two columns the tab
    exists for, at a half-width window. At 833 px eight headings stood as
    three- to six-letter fragments.

    The heading may be shortened; what it may not be is cut. Reading what is
    actually in the header item against the room the style gives it is the
    difference: a heading that Qt clips is still the whole string in the item
    and shows up here.
    """
    with rendered.laid_out(game_data, "effects_tab", width) as (_, tab):
        table = tab.table
        metrics = table.horizontalHeader().fontMetrics()
        over = []
        for column in range(table.columnCount()):
            item = table.horizontalHeaderItem(column)
            room = header_label_room(table, column)
            if metrics.horizontalAdvance(item.text()) > room:
                over.append((item.text(),
                             metrics.horizontalAdvance(item.text()), room))
        assert not over, (
            f"at {width} px these headings are wider than the room their "
            f"section leaves them, so the style cuts them: {over}")


@pytest.mark.parametrize("width", WIDTHS)
def test_every_shortened_heading_says_so_and_keeps_its_name(
        game_data, qapp, width):
    """The other half of QA-140, and the half the tooltip promise missed.

    Two things a reader needs from a heading that did not fit: a sign that it
    was shortened, and a way back to the whole name. `Effect`, `Type` and
    `What it does` carried no tooltip at all, and `Type` was drawn as `yp`.

    The names come from `EFFECT_COLUMNS` at the top of this file, not from the
    tab -- a case that read them back off the header items would follow the
    shortening wherever it went.
    """
    with rendered.laid_out(game_data, "effects_tab", width) as (_, tab):
        table = tab.table
        assert table.columnCount() == len(EFFECT_COLUMNS), (
            f"the table has {table.columnCount()} columns and this case knows "
            f"{len(EFFECT_COLUMNS)} headings")
        unreachable, unmarked = [], []
        for column, name in enumerate(EFFECT_COLUMNS):
            item = table.horizontalHeaderItem(column)
            shown = item.text()
            if name not in tabtext.plain(item.toolTip()):
                unreachable.append((name, item.toolTip()))
            if shown != name and not shown.endswith(ELLIPSIS):
                unmarked.append((name, shown))
        assert not unreachable, (
            f"at {width} px these headings do not carry their own name where "
            f"a reader can get at it: {unreachable}")
        assert not unmarked, (
            f"at {width} px these headings are drawn shorter than their name "
            f"with nothing saying so: {unmarked}")


# -- QA-144: the examples column against the column it illustrates --------

@pytest.mark.parametrize("width", WIDTHS)
def test_the_examples_column_never_outgrows_the_column_it_illustrates(
        game_data, qapp, width):
    """AK-99's last sentence, at the width where it stopped holding.

    `Examples (any map)` was left to `ResizeToContents`, which hands a column
    its natural width whatever is left for the rest. From 1 067 px up the
    natural widths fell the right way round on their own and the rule looked
    kept; at 833 px the examples took 349 px against 281 px for the column
    that says what the row is (QA-144), on Windows at 150 % scale under
    Fusion.

    The two headings are identified by position rather than by their drawn
    text, and the widths are read off the header rather than off the policy
    that set them.
    """
    with rendered.laid_out(game_data, "depths_tab", width) as (_, tab):
        header = tab.table.horizontalHeader()
        name, examples = header.sectionSize(0), header.sectionSize(1)
        assert tab.table.rowCount(), "the table drew no rows"
        assert examples <= name, (
            f"at {width} px `{tab.table.horizontalHeaderItem(1).text()}` is "
            f"{examples} px and "
            f"`{tab.table.horizontalHeaderItem(0).text()}` is {name} px")
        assert not tab.table.horizontalScrollBar().isVisible(), (
            f"at {width} px the red-variants table needs a horizontal "
            f"scrollbar")


# -- QA-143: the search that showed nothing at all ------------------------

#: A search term that matches far more of the arsenal than the cap at which
#: `rebuild` opens every group. `a` matched 1 099 of 1 952 entries on
#: 2026-09-05; the assertion below reads the count off the tab rather than
#: trusting that figure, so a dataset where `a` is rare fails loudly instead
#: of passing on an empty tab.
BROAD_SEARCH = "a"


def test_a_search_with_more_hits_than_the_cap_still_draws_a_tile(
        game_data, qapp):
    """QA-143. Over sixty hits fell through both branches and drew nothing.

    A modest result set opens every group; the first view opens one. A search
    matching more than the cap matched neither rule, so the tab answered
    `1 099 shown` over three collapsed headings and an empty black page --
    DR-017 exactly, at the one state nobody had looked at.
    """
    with rendered.laid_out(game_data, "weapons_tab", 1600, 950) as (_, tab):
        tab.search.setText(BROAD_SEARCH)
        tab.rebuild()
        rendered.settle()
        shown = int(tab.summary.text().split(" shown")[0].split(". ")[-1])
        assert shown > 60, (
            f"{BROAD_SEARCH!r} matches only {shown} entries in this dataset, "
            f"which is under the cap, so this case is watching the branch it "
            f"is not about")
        visible = [tile for tile in tab.findChildren(arsenaltab.Tile)
                   if tile.isVisible()]
        assert visible, (
            f"the tab says {shown} shown and draws no tile at all")
