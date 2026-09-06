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
from PySide6.QtCore import QEvent, QPoint, QPointF, Qt
from PySide6.QtGui import QEnterEvent, QMouseEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLabel

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


# -- QA-154: what the pointer says before the button goes down -------------
#
# The finding read as a hit-area fault and is not one. Measured on 2026-09-06
# on Windows under Fusion at 150 % scale, at a 1600x900 logical-px window (the
# window reached both figures, so it is the size this note is named for):
# 3 420 probe points, one every 4 logical px over the whole 302x178 card, each
# delivered through `qApp.notify` so Qt's own propagation decided it --
# **3 420 of 3 420 opened that card, 0 dead**. The labels on the card do not
# swallow a press.
#
# What is dead is the strip between two cards: 8 logical px at every width
# measured (1600, 1250, 1067), and a click in it opens nothing. Of the grid
# rectangle at 1600 px, 79.3 % is card; of the 20.7 % that is not, three
# quarters is the unfilled remainder of the last row (ten cards in four
# columns) and the rest is that 8 px lattice.
#
# So the reader had no way to see which side of an 8 px line he was on: a near
# miss opened the neighbour and a miss opened nothing, and the grid looked the
# same in both cases. These cases are about the mark that now says which.
#
# **How the pointer is delivered here, and what that does not prove.** The
# arrival and departure are sent to the card with `QApplication.sendEvent`, so
# what runs is `QWidget::event` -> `enterEvent` -> the repaint. What does not
# run is `QApplicationPrivate::dispatchEnterLeave`, which decides *which*
# widget gets them -- and it cannot be driven from a test on this program:
# measured 2026-09-06, `QTest.mouseMove` lands where it is aimed only in the
# first window a process opens. Every window after it inherits a pointer
# position from the window before, gets an Enter for whatever card sits under
# it, and never gets the matching Leave, so a second window opens with a card
# already marked and keeps it marked through every later move. Under the
# `windows` platform not even the first move lands. A case built on it would
# pass or skip by test order.
#
# That half was measured instead, at a running window, with the real cursor
# moved by `QCursor.setPos` (Windows, Fusion, 150 % scale, 1600x900 logical
# px): pointer on the card marks it; pointer on the **name label inside** the
# card keeps the same card marked and no other; pointer in the 8 px gap marks
# nothing; pointer on the neighbour hands the mark over. And a card that Qt
# could not reach with a pointer at all would fail the press case at the foot
# of this file, which goes through the propagation that decides delivery.


def in_the_same_row(tab) -> tuple:
    """Two cards side by side, and the point of the gap between them."""
    placed = [(card.mapTo(tab.cards, QPoint(0, 0)), card)
              for card in cards(tab)]
    top = min(point.y() for point, _card in placed)
    row = sorted((entry for entry in placed if entry[0].y() == top),
                 key=lambda entry: entry[0].x())
    if len(row) < 2:
        pytest.skip("this window is one card wide, so it has no gap between "
                    "two cards for this case to stand in")
    (left_at, left), (right_at, right) = row[0], row[1]
    gap = QPoint((left_at.x() + left.width() + right_at.x()) // 2,
                 left_at.y() + left.height() // 2)
    return left, right, gap


def under_the_pointer(tab) -> set:
    """Cards Qt has WA_UnderMouse set on, whoever put the pointer there."""
    return {card.boss["name"] for card in cards(tab) if card.underMouse()}


def moved(before, tab, *placed) -> list[str]:
    """Which cards changed, other than ones no pointer was placed on.

    Under a display the window opens wherever the physical cursor happens to
    be and Qt marks the card under it -- correct behaviour of the program,
    and noise in a comparison about a pointer this case placed itself. Only a
    card that Qt says has the pointer on it **and** that this case never
    touched is taken out; a third card marked for any other reason is still a
    failure.

    Under `offscreen`, which the suite runs on, the set taken out is always
    empty: the only cards with the pointer on them are the ones named in
    `placed`. Nothing here is loosened for the run that counts.
    """
    intended = {card.boss["name"] for card in placed}
    return sorted(set(differing(before, pictures(tab)))
                  - (under_the_pointer(tab) - intended))


def own_the_pointer(tab, *targets) -> None:
    """Give up if the physical cursor is on a card the case wants to drive."""
    taken = sorted(under_the_pointer(tab)
                   & {card.boss["name"] for card in targets})
    if taken:
        pytest.skip(
            f"the physical pointer is sitting on {taken}, which is a card "
            f"this case places a pointer on itself -- the two cannot be told "
            f"apart in a picture. Never the case under `offscreen`.")


def pointer_onto(card) -> None:
    """The pointer arrives on `card`."""
    centre = QPointF(card.rect().center())
    QApplication.sendEvent(card, QEnterEvent(
        centre, centre, QPointF(card.mapToGlobal(centre.toPoint()))))
    rendered.settle()


def pointer_off(card) -> None:
    """The pointer leaves `card` -- for the gap, or for anywhere else."""
    QApplication.sendEvent(card, QEvent(QEvent.Leave))
    rendered.settle()


def test_the_grid_marks_the_card_the_pointer_is_on(game_data, qapp):
    """QA-154. A near miss has to be visible before the button goes down."""
    with rendered.laid_out(game_data, "boss_tab", WIDTH) as (_, tab):
        target = cards(tab)[2]
        own_the_pointer(tab, target)
        before = pictures(tab)
        pointer_onto(target)

        assert moved(before, tab, target) == [target.boss["name"]], (
            f"the pointer resting on the {target.boss['name']} card changed "
            f"{moved(before, tab, target)} on the grid")


def test_the_mark_moves_to_the_card_the_pointer_moves_to(game_data, qapp):
    """One card at a time, which is the whole point of a pointer mark.

    A mark that was added and never taken away would leave the row claiming
    two targets at once -- the state QA-150's own marker is guarded against
    two cases above, arrived at from the other direction.
    """
    with rendered.laid_out(game_data, "boss_tab", WIDTH) as (_, tab):
        left, right, _gap = in_the_same_row(tab)
        own_the_pointer(tab, left, right)
        before = pictures(tab)
        pointer_onto(left)
        assert moved(before, tab, left) == [left.boss["name"]], (
            "the pointer marked nothing, so this case cannot tell whether "
            "the mark is handed on")

        pointer_off(left)
        pointer_onto(right)
        assert moved(before, tab, right) == [right.boss["name"]], (
            f"with the pointer on {right.boss['name']} the grid marks "
            f"{moved(before, tab, right)}")


def test_the_mark_goes_when_the_pointer_leaves_for_the_gap(game_data, qapp):
    """The half of QA-154 a hit area cannot fix.

    Eight logical px separate two cards and a pointer in there is on nothing.
    That is correct behaviour, and it was indistinguishable from a broken
    program because the grid looked the same either way.
    """
    with rendered.laid_out(game_data, "boss_tab", WIDTH) as (_, tab):
        left, _right, _gap = in_the_same_row(tab)
        own_the_pointer(tab, left)
        before = pictures(tab)
        pointer_onto(left)
        assert moved(before, tab, left) == [left.boss["name"]], (
            "the pointer marked nothing on its way in, so this case cannot "
            "tell whether leaving takes the mark away")

        pointer_off(left)
        marked = moved(before, tab)
        assert marked == [], (
            f"the mark stayed on {marked} after the pointer left the card")


def test_a_click_between_two_cards_opens_nothing(game_data, qapp):
    """The gap itself, and how narrow it is.

    A press here goes through Qt's own propagation, the same path that makes
    every pixel of a card live. Nothing opening is the correct outcome; what
    was missing is any way for a reader to see he was in the gap before he
    pressed, which the mark above now gives him.
    """
    with rendered.laid_out(game_data, "boss_tab", WIDTH) as (window, tab):
        left, right, gap = in_the_same_row(tab)
        width = (right.mapTo(tab.cards, QPoint(0, 0)).x()
                 - left.mapTo(tab.cards, QPoint(0, 0)).x() - left.width())

        opened: list[str] = []
        for card in cards(tab):
            card.clicked.connect(lambda boss: opened.append(boss["name"]))
        point = tab.cards.mapTo(window, gap)
        target = window.childAt(point) or window
        QTest.mouseClick(target, Qt.LeftButton, Qt.NoModifier,
                         target.mapFrom(window, point))
        rendered.settle()

        assert width > 0, (
            f"{left.boss['name']} and {right.boss['name']} are drawn with no "
            f"gap between them, so this case is pressing on a card")
        assert opened == [], (
            f"a press in the {width} px gap between {left.boss['name']} and "
            f"{right.boss['name']} opened {opened}")


def test_the_pointer_mark_and_the_chosen_mark_are_told_apart(game_data, qapp):
    """Three states, three pictures.

    A hover drawn as the selection is drawn would tell a reader he had
    already chosen the card he is merely pointing at -- which is the mistake
    QA-150's marker exists to prevent, made the other way round.

    Read inside the border, for the reason the Everdark case above is: the
    selection changes the one pixel edge as well as the fill, so a whole-card
    comparison stays green with the two fills set to the very same colour.
    It did: the counter-build `HOVER_FILL = SELECTED_FILL` survived the first
    version of this case, and the border alone was carrying the difference.
    """
    with rendered.laid_out(game_data, "boss_tab", WIDTH) as (_, tab):
        left, _right, _gap = in_the_same_row(tab)
        own_the_pointer(tab, left)
        plain = interiors(tab)[left.boss["name"]]

        pointer_onto(left)
        hovered = interiors(tab)[left.boss["name"]]
        pointer_off(left)

        tab.show_detail(left.boss)
        rendered.settle()
        chosen = interiors(tab)[left.boss["name"]]

        assert hovered != plain, (
            f"the pointer on {left.boss['name']} draws its inside exactly as "
            f"it is drawn untouched")
        assert hovered != chosen, (
            f"inside its border, {left.boss['name']} looks the same under "
            f"the pointer as it does when the panel is describing it")


def test_the_chosen_card_keeps_its_mark_under_the_pointer(game_data, qapp):
    """Selection outranks hover.

    A reader running the pointer along the row to find the next Nightlord
    must not lose sight of the one the panel is describing.
    """
    with rendered.laid_out(game_data, "boss_tab", WIDTH) as (_, tab):
        left, _right, _gap = in_the_same_row(tab)
        own_the_pointer(tab, left)
        tab.show_detail(left.boss)
        rendered.settle()
        chosen = pictures(tab)[left.boss["name"]]

        pointer_onto(left)
        assert pictures(tab)[left.boss["name"]] == chosen, (
            f"the pointer changed how the chosen {left.boss['name']} card is "
            f"drawn, so the panel's card and the pointer's card look alike")


def test_a_press_on_a_label_inside_a_card_opens_that_card(game_data, qapp):
    """The hit area, guarded rather than assumed.

    Every pixel of the card is live because the labels on it ignore a press
    and Qt hands it to the frame underneath. That is Qt's default, and a
    single `WA_NoMousePropagation` -- or a label that accepts the event --
    would put a dead patch in the middle of a card with nothing on screen to
    show it. The press goes to the label and is delivered through
    `qApp.notify`, which is where the propagation lives; a card Qt could not
    reach with a pointer at all fails here too.
    """
    with rendered.laid_out(game_data, "boss_tab", WIDTH) as (_, tab):
        target = cards(tab)[1]
        labels = target.findChildren(QLabel)
        assert labels, "the card carries no labels, so nothing is covered"

        opened: list[str] = []
        target.clicked.connect(lambda boss: opened.append(boss["name"]))
        missed = []
        for label in labels:
            opened.clear()
            QTest.mouseClick(label, Qt.LeftButton, Qt.NoModifier,
                             label.rect().center())
            if opened != [target.boss["name"]]:
                missed.append((label.text() or "<image>", list(opened)))

        assert not missed, (
            f"a press on these parts of the {target.boss['name']} card did "
            f"not open it: {missed}")
