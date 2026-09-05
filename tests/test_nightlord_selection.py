"""Which Nightlord the grid says you are looking at.

QA-150: `show_detail` moved the detail panel and nothing else. The ten cards
sit 8 px apart, so a near miss opens the neighbour -- and with no marker on
the grid the screen after the miss looks exactly like the screen before it.
The `power-user` run of 2026-09-05 ended on Gnoster while aiming at Adel and
noticed only from the profile text. A player who does not notice plans the
fight against a Nightlord he never chose.

**Everything here is read off pixels.** A case asking `card.selected` would
be asking the module whether it thinks it has drawn something, which is the
question the finding is about: the state was never the problem, the screen
was. So each case grabs the cards, does one thing, grabs them again, and
compares the images. That also makes the case blind to *how* the marker is
drawn, which is what keeps it from following an implementation that stopped
reaching the screen.

**Why an interior sample and not the whole card.** The grid already carries
one marker: an Everdark twin puts a different colour on the card's one pixel
border. A selection drawn only there would be one hue away from a marker that
means something else entirely -- so the second case reads a rectangle set
well inside the border and requires the selection to have changed that too.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

from nrplanner import bosstab

from tests import rendered

#: How far inside a card the fill is read, in px of the rendered card. Past
#: the 1 px border the Everdark marker owns, and past the 7 px corner radius,
#: so nothing sampled here can be either of those.
INSET = 8

#: A width the offscreen platform can give the window (its floor is 964) and
#: the Windows platform can give it too, so both run the same case rather than
#: one of them skipping it.
WIDTH = 1250


def cards(tab) -> list:
    return tab.holder.findChildren(bosstab.BossCard)


def pictures(tab) -> dict:
    """Every card as it is drawn right now, by Nightlord name."""
    return {card.boss["name"]: card.grab().toImage() for card in cards(tab)}


def interiors(tab) -> dict:
    """The same cards with their border and corners cropped away."""
    out = {}
    for card in cards(tab):
        image = card.grab().toImage()
        out[card.boss["name"]] = image.copy(
            image.rect().adjusted(INSET, INSET, -INSET, -INSET))
    return out


def differing(before: dict, after: dict) -> list[str]:
    return sorted(name for name in before if before[name] != after[name])


def click(card) -> None:
    """A real press on the card, delivered the way a mouse delivers one."""
    centre = QPointF(card.rect().center())
    QApplication.sendEvent(card, QMouseEvent(
        QEvent.MouseButtonPress, centre, card.mapToGlobal(centre.toPoint()),
        Qt.LeftButton, Qt.LeftButton, Qt.NoModifier))
    rendered.settle()


def a_twin_and_a_plain_one(tab) -> tuple[dict, dict]:
    """One Nightlord with an Everdark twin and one without.

    Both, because the twin marker and the selection marker meet on the same
    card and the case has to see what happens there as well as where they do
    not meet.
    """
    twin = next((b for b in tab.bosses if b.get("everdark")), None)
    plain = next((b for b in tab.bosses if not b.get("everdark")), None)
    assert twin is not None and plain is not None, (
        "this dataset has no Nightlord with an Everdark twin, or none "
        "without one, so these cases cannot tell the two markers apart")
    return twin, plain


@pytest.mark.parametrize("kind", ["with an Everdark twin", "without one"])
def test_the_grid_marks_the_card_the_panel_is_describing(
        game_data, qapp, kind):
    """The finding itself: after a choice the grid must not look unchanged.

    And exactly one card may move. A marker that also touched its neighbours
    would answer the reader's question with a different wrong answer.
    """
    with rendered.laid_out(game_data, "boss_tab", WIDTH) as (_, tab):
        twin, plain = a_twin_and_a_plain_one(tab)
        boss = twin if kind == "with an Everdark twin" else plain

        before = pictures(tab)
        tab.show_detail(boss)
        rendered.settle()
        after = pictures(tab)

        assert differing(before, after) == [boss["name"]], (
            f"choosing {boss['name']} ({kind}) changed the look of "
            f"{differing(before, after)} on the grid")


@pytest.mark.parametrize("kind", ["with an Everdark twin", "without one"])
def test_the_marker_reaches_the_inside_of_the_card(game_data, qapp, kind):
    """Not only the border, which already means something else.

    A selection that lived on the one pixel edge would be a colour swap on
    the very stroke that says "this Nightlord has an Everdark version", and
    the two would have to be told apart by hue alone. Reading a rectangle
    inset past the border makes this a claim about a second channel, not
    about a shade.
    """
    with rendered.laid_out(game_data, "boss_tab", WIDTH) as (_, tab):
        twin, plain = a_twin_and_a_plain_one(tab)
        boss = twin if kind == "with an Everdark twin" else plain

        before = interiors(tab)
        tab.show_detail(boss)
        rendered.settle()
        after = interiors(tab)

        assert boss["name"] in differing(before, after), (
            f"the mark on {boss['name']} ({kind}) does not reach {INSET} px "
            f"inside the card, so it lives on the same stroke the Everdark "
            f"marker uses")


def test_a_click_is_what_marks_a_card(game_data, qapp):
    """The path a player actually takes, press included.

    `show_detail` can be called from a test all day; what the finding is
    about is a click landing on a card. This case presses one and reads the
    grid, so a marker wired to something other than the click fails here.
    """
    with rendered.laid_out(game_data, "boss_tab", WIDTH) as (_, tab):
        target = cards(tab)[2]
        before = pictures(tab)
        click(target)
        after = pictures(tab)

        assert differing(before, after) == [target.boss["name"]], (
            f"a press on the {target.boss['name']} card changed "
            f"{differing(before, after)} on the grid")


def test_the_marker_moves_to_the_card_chosen_next(game_data, qapp):
    """Two in a row, which is the state the misclick actually produces.

    The `power-user` clicked once, read the wrong profile and clicked again.
    A marker that was added and never taken away would leave two cards
    claiming to be the one on screen, which is worse than none.
    """
    with rendered.laid_out(game_data, "boss_tab", WIDTH) as (_, tab):
        first, second = tab.bosses[0], tab.bosses[1]

        untouched = pictures(tab)
        tab.show_detail(first)
        rendered.settle()
        after_first = pictures(tab)
        tab.show_detail(second)
        rendered.settle()
        after_second = pictures(tab)

        assert differing(untouched, after_first) == [first["name"]]
        assert differing(untouched, after_second) == [second["name"]], (
            f"after choosing {second['name']} the grid still shows "
            f"{differing(untouched, after_second)} as chosen")
        assert after_second[first["name"]] == untouched[first["name"]], (
            f"{first['name']} kept its mark after {second['name']} was "
            f"chosen, so two cards claim the panel at once")


def test_nothing_is_marked_before_a_choice_and_after_it_is_cleared(
        game_data, qapp):
    """An empty panel says `Select a Nightlord`; the grid has to agree.

    The tab opens with no Nightlord chosen and `show_detail(None)` puts it
    back into that state, so a mark left standing would point at a profile
    that is no longer on screen.
    """
    with rendered.laid_out(game_data, "boss_tab", WIDTH) as (_, tab):
        opening = pictures(tab)
        tab.show_detail(tab.bosses[3])
        rendered.settle()
        assert differing(opening, pictures(tab)) == [tab.bosses[3]["name"]], (
            "nothing changed on the grid, so this case cannot tell whether "
            "clearing the choice put anything back")

        tab.show_detail(None)
        rendered.settle()
        assert differing(opening, pictures(tab)) == [], (
            "the grid still marks a card while the panel says `Select a "
            "Nightlord`")
