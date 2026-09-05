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
from PySide6.QtWidgets import QLabel, QScrollArea

from nrplanner import arsenaltab, bosstab

from tests import rendered

#: AK-71. No tab may ask the window for more height than this.
TAB_HEIGHT_LIMIT = 860

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
        widths = {tab.table.horizontalHeaderItem(column).text():
                  header.sectionSize(column)
                  for column in range(tab.table.columnCount())}
        wider = {name: size for name, size in widths.items()
                 if name != "Effect" and size >= header.sectionSize(0)}
        assert not wider, (
            f"at {width} px these columns are at least as wide as `Effect` "
            f"({header.sectionSize(0)} px): {wider}")


@pytest.mark.parametrize("width", FLOOR_WIDTHS)
def test_the_two_reading_columns_hold_their_floors(game_data, qapp, width):
    """AK-77's two figures, at the widths at which they are reachable."""
    with rendered.laid_out(game_data, "effects_tab", width) as (_, tab):
        header = tab.table.horizontalHeader()
        last = tab.table.columnCount() - 1
        widths = {tab.table.horizontalHeaderItem(column).text():
                  header.sectionSize(column)
                  for column in range(tab.table.columnCount())}
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
