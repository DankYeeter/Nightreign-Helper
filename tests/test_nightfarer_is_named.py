"""Who the ten portraits are, and where a player goes to change which one.

QA-155, both halves of it. The `power-user` of 2026-09-06 wanted to compare
armaments for his character and met two walls at once:

* the ten Nightfarer tiles carried **artwork and nothing else**, so he had to
  click one and then find the answer somewhere else on the screen to learn
  whom he had picked;
* the `Weapons & spells` tab said `rated for the Nightfarer, level and
  upgrade set above` while only the upgrade is set above -- the character
  lives on the `Build planner`. He looked for it on the weapons tab, because
  that is what the sentence told him, and found it by opening every tab in
  turn.

**Neither case reads a constant of the module it guards.** The name on a tile
is read off the picture the tile draws: the same tile is rendered twice, once
with its name and once with the name taken away, and the two have to differ.
A tile that went back to drawing icons only would render the same picture
both times. The sentence on the weapons tab is required to name a tab that
`QTabWidget` actually has, taken from `tabText`, so a sentence pointing at a
tab that had been renamed or removed fails here rather than on screen.

**No pixel figure of a font is asserted.** The offscreen font is about twice
as wide per character as the player's (tests/rendered.py), so `Undertaker`
fits its tile on Windows and does not fit it here. Whether Qt shortens a name
is measured at the running window and reported; what this file holds is that
the name is drawn at all.
"""

from __future__ import annotations

from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QGridLayout, QTabWidget

from tests import rendered, tabtext

#: The tab the Nightfarer is chosen on, as `addTab` names it. Written out
#: rather than imported, and then required to be a tab the window really has:
#: the point of the case is that the sentence sends a reader somewhere that
#: exists.
PLANNER_TAB = "Build planner"


def tile_pictures(tile):
    """The tile as it is drawn, and as it would be drawn with no name.

    The name is put back before the pair is returned, so the window this ran
    on is left as it was found.
    """
    with_name = tile.grab().toImage()
    tile.setText("")
    rendered.settle()
    without = tile.grab().toImage()
    tile.setText(tile.hero["name"])
    rendered.settle()
    return with_name, without


def test_every_nightfarer_tile_draws_its_own_name(game_data, qapp):
    """QA-155. Ten portraits and no caption on any of them."""
    with rendered.laid_out(game_data, "effects_tab", 1250) as (window, _):
        silent = []
        for tile in window.hero_tiles:
            with_name, without = tile_pictures(tile)
            if with_name == without:
                silent.append(tile.hero["name"])

        assert not silent, (
            f"these Nightfarer tiles draw the same picture with their name "
            f"as without it, so the name is not on the tile: {silent}")


def test_the_name_on_the_tile_is_the_name_of_its_own_nightfarer(
        game_data, qapp):
    """One caption per portrait, and the right one.

    Ten tiles all captioned `Wylder` would pass the case above.
    """
    with rendered.laid_out(game_data, "effects_tab", 1250) as (window, _):
        wrong = [(tile.hero["name"], tile.text())
                 for tile in window.hero_tiles
                 if tile.text() != tile.hero["name"]]
        assert not wrong, (
            f"these tiles carry a caption that is not their Nightfarer's "
            f"name: {wrong}")


def test_the_weapons_tab_says_where_the_nightfarer_is_changed(
        game_data, qapp):
    """The second half of QA-155, and the sentence that caused it.

    The tab is rated for a Nightfarer it cannot change. Saying so, and saying
    where the change is made, is the whole fix -- a second picker would be a
    second home for one piece of state and is the App Designer's decision.
    """
    with rendered.laid_out(game_data, "weapons_tab", 1250) as (window, tab):
        tabs = window.findChild(QTabWidget)
        labels = [tabs.tabText(i).replace("&&", "&")
                  for i in range(tabs.count())]
        assert PLANNER_TAB in labels, (
            f"no tab is called {PLANNER_TAB!r} any more -- this window shows "
            f"{labels}, so the sentence under test points nowhere")

        said = tabtext.everything(tab)
        assert PLANNER_TAB in said, (
            f"nothing on the weapons tab names the {PLANNER_TAB!r} tab, so a "
            f"reader looking for the character picker has only the other "
            f"tabs to try")


def test_the_weapons_tab_does_not_claim_the_nightfarer_is_set_on_it(
        game_data, qapp):
    """The half of QA-155 that was an untruth rather than an omission.

    `set above` covered three things and was right about one of them. A
    reader who trusts it hunts the tab for a picker that is not there.
    """
    with rendered.laid_out(game_data, "weapons_tab", 1250) as (_, tab):
        said = tabtext.everything(tab)
        assert "Nightfarer, level and upgrade set above" not in said, (
            "the tab still tells the reader that the Nightfarer is set on "
            "this tab, which is where he looked for it and where it is not")


def test_the_arsenal_question_names_the_tab_and_not_this_one(game_data, qapp):
    """Where the sentence sends the reader has to be somewhere else.

    A sentence naming the weapons tab itself would be worse than the one it
    replaces: the reader would stay put and keep looking.
    """
    with rendered.laid_out(game_data, "weapons_tab", 1250) as (window, tab):
        tabs = window.findChild(QTabWidget)
        here = tabs.tabText(tabs.indexOf(tab)).replace("&&", "&")
        question = tabtext.labels(tab)[1]
        assert PLANNER_TAB in question, (
            f"the question line of this tab does not name {PLANNER_TAB!r}: "
            f"{question!r}")
        assert here not in question, (
            f"the question line sends the reader to {here!r}, which is the "
            f"tab he is already on: {question!r}")


def test_the_tile_says_the_same_name_the_rest_of_the_window_says(
        game_data, qapp):
    """One Nightfarer, one name, wherever it is written.

    The tile, the label under the grid and the weapons summary all name the
    chosen character. Two of them disagreeing is the fault QA-155 is the
    other side of: the player read `Wylder at level 1` on one tab and could
    not tell which portrait that was.

    The weapons tab is brought to the front the way a reader brings it, and
    not refreshed by hand: it recalculates on `currentChanged` and nowhere
    else, so a case that read it while another tab was in front would be
    reading the Nightfarer of the last visit.
    """
    with rendered.laid_out(game_data, "effects_tab", 1250) as (window, _):
        index = 3
        window.select_hero(index)
        rendered.settle()
        tile = window.hero_tiles[index]

        assert tile.isChecked(), (
            "choosing a Nightfarer left its tile unmarked, so this case "
            "cannot tell which tile it is asking about")
        assert tile.text() == window.hero_name_label.text(), (
            f"the tile says {tile.text()!r} and the label under the grid "
            f"says {window.hero_name_label.text()!r}")

        window.findChild(QTabWidget).setCurrentWidget(window.weapons_tab)
        rendered.settle()
        assert tile.text() in tabtext.everything(window.weapons_tab), (
            f"the weapons tab does not name {tile.text()!r}, the Nightfarer "
            f"whose tile is marked")


def test_the_tile_is_tall_enough_for_the_portrait_and_the_name(
        game_data, qapp):
    """A caption that ate the artwork would trade one fault for another.

    The height is asked of Qt rather than added up, and this is the case that
    notices when the answer comes back for a button Qt thinks has no icon:
    `initStyleOption` reports a text-only button while the icon is still
    unset, and a tile sized in that moment comes out one line tall with no
    portrait on it at all.
    """
    with rendered.laid_out(game_data, "effects_tab", 1250) as (window, _):
        short = [(tile.hero["name"], tile.height())
                 for tile in window.hero_tiles
                 if tile.height() <= tile.iconSize().height()]
        assert not short, (
            f"these tiles are no taller than the portrait they carry, so the "
            f"name has nowhere to be drawn: {short}")
        assert not [t for t in window.hero_tiles if t.icon().isNull()], (
            "a tile carries no icon at all")


def test_the_chosen_tile_is_drawn_differently_from_the_others(
        game_data, qapp):
    """The mark on the grid, which the caption had to make room for.

    The border went from one pixel to two so that choosing a tile cannot
    narrow the room its name has -- and a border that stopped changing at all
    would take the mark off the grid while leaving every case above green.

    **What is not guarded here, and cannot be.** That the two border widths
    are equal is a relation between two lines of one stylesheet, and Qt
    exposes it nowhere: measured on 2026-09-06, `contentsRect`,
    `subControlRect(CC_ToolButton, SC_ToolButton)` and
    `subElementRect(SE_ToolButtonLayoutItem)` all report 56x73 for a tool
    button whose checked border is 2, 4 or 8 px. A case built on any of them
    stayed green with the checked border at four pixels; it was deleted
    rather than kept as a green that meant nothing. The reason the two are
    equal is written where the stylesheet is.
    """
    with rendered.laid_out(game_data, "effects_tab", 1250) as (window, _):
        tile = window.hero_tiles[0]
        window.select_hero(1)
        rendered.settle()
        loose = tile.grab().toImage()
        window.select_hero(0)
        rendered.settle()
        chosen = tile.grab().toImage()

        assert chosen != loose, (
            f"the {tile.hero['name']} tile is drawn the same whether it is "
            f"the chosen Nightfarer or not")


def test_the_tiles_fit_the_narrowest_the_sidebar_may_become(game_data, qapp):
    """Five across, inside the sidebar's own floor.

    The names could have been bought with width, and the price would have
    been the whole window's minimum: the tiles live in a pane whose floor is
    what a vessel row needs, and QSplitter hands a pane's minimum on to the
    window.

    **What is measured is what the grid needs, not where it happens to sit.**
    The columns share whatever width the pane has, so at the opening 430 px
    the five tiles stand 82 px apart with 56 px of tile in each -- a reading
    that says nothing about how narrow they can go. `QGridLayout.minimumSize`
    is Qt's own answer to that, built from the tiles' fixed widths and the
    grid's spacing. A first version of this case read the laid-out positions
    instead, and a counter-build widening every tile by 24 px walked straight
    through it twice.

    The floor is read off the pane rather than written out here, because it
    is not this file's number: it belongs to the vessel row below the grid
    and may move for reasons that have nothing to do with ten portraits.
    What this case holds is the relation.
    """
    with rendered.laid_out(game_data, "effects_tab", 1250) as (window, _):
        tiles = window.hero_tiles
        pane = tiles[0].parentWidget()
        grid = next(
            (candidate for candidate in pane.findChildren(QGridLayout)
             if any(candidate.itemAt(i).widget() is tiles[0]
                    for i in range(candidate.count()))), None)
        assert grid is not None, (
            "the Nightfarer tiles are no longer in a QGridLayout, so this "
            "case cannot ask how narrow the grid can go")

        needs = grid.minimumSize().width()
        floor = pane.minimumWidth()
        assert floor > 0, (
            "the sidebar declares no floor, so this case has nothing to "
            "measure the tiles against")
        assert needs <= floor, (
            f"a row of Nightfarer tiles needs {needs} px and the sidebar is "
            f"only guaranteed {floor} px, so the grid now sets the window's "
            f"minimum width")

        drawn = max(tile.mapTo(pane, QPoint(0, 0)).x() + tile.width()
                    for tile in tiles)
        assert drawn <= pane.width(), (
            f"the tiles reach {drawn} px in a pane {pane.width()} px wide")
