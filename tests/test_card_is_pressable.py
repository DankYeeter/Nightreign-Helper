"""A Nightlord card without a mouse: by keyboard, and by assistive tool.

QA-161. The card answered to `mousePressEvent` and to nothing else, and the
accessibility interface reported that as success: 90 of 90 exposed elements
said they supported `InvokePattern`, `Invoke` on the card returned
`INVOKE_OK`, and the detail panel did not move. Two of four `power-user` runs
gave up on the Nightlords tab because of it, and the second of them raised a
regression report against a release that had none.

**Every case here reads the detail panel, never a return value.** That is the
lesson the finding itself teaches: the thing that lied was the return value,
and the thing that told the truth was the state the program keeps. So a
press has worked when `detail_name` says the Nightlord's name, and not when
some call reported success.

**Why the accessible interface and not just the keyboard.** They are three
separate routes -- mouse, keyboard, `QAccessibleInterface` -- and the finding
is that two of them were missing while the first one worked. A case that only
pressed Enter would pass on a card no screen reader can find.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import (
    QAccessible, QAccessibleActionInterface, QKeyEvent, QKeySequence,
)
from PySide6.QtWidgets import QApplication

from nrplanner import bosstab

from tests import rendered

#: A width the offscreen platform can give the window and Windows can too, so
#: both run these cases rather than one of them skipping.
WIDTH = 1250

EMPTY_PANEL = "Select a Nightlord"


def cards(tab) -> list:
    return tab.holder.findChildren(bosstab.BossCard)


def pictures(tab) -> dict:
    """Every card as it is drawn right now, by Nightlord name."""
    return {card.boss["name"]: card.grab().toImage() for card in cards(tab)}


def interface(card):
    iface = QAccessible.queryAccessibleInterface(card)
    assert iface is not None, (
        "Qt hands out no accessible interface for this card at all, so "
        "nothing below can be asked of it")
    return iface


def type_key(card, key: int) -> None:
    """One key press, delivered to the card the way a keyboard delivers it."""
    QApplication.sendEvent(card, QKeyEvent(
        QEvent.KeyPress, key, Qt.NoModifier))
    rendered.settle()


def press_tab(card) -> None:
    """Tab, through `QApplication`, so Qt moves the focus as it would for a
    reader -- including telling the window that the keyboard is being used,
    which is what makes a focus rectangle appear at all."""
    type_key(card, Qt.Key_Tab)


def test_a_card_carries_the_nightlords_name_for_a_reader_without_eyes(
        game_data, qapp):
    """The card itself, not the label inside it.

    Measured before the fix: the only element in the whole window named
    `Fulghor` was the `QLabel`; the card was `ControlType.Custom` with no
    name, so a client that found the label had found something it could not
    press, and a client looking for the card had nothing to look for.
    """
    with rendered.laid_out(game_data, "boss_tab", WIDTH) as (_, tab):
        for card in cards(tab):
            given = interface(card).text(QAccessible.Name)
            assert given == card.boss["name"], (
                f"the card for {card.boss['name']} tells an assistive tool "
                f"its name is {given!r}")


def test_a_card_says_it_is_a_control_and_not_furniture(game_data, qapp):
    """Role `Button`, because `Border` is skipped over by every reader.

    A card with a press action and the role of a frame is a control nobody
    is offered: assistive tools list what can be acted on, and a border is
    not on that list.
    """
    with rendered.laid_out(game_data, "boss_tab", WIDTH) as (_, tab):
        card = cards(tab)[0]
        assert interface(card).role() == QAccessible.Button, (
            f"the {card.boss['name']} card reports itself as "
            f"{interface(card).role()}")


def test_the_accessible_press_opens_the_profile(game_data, qapp):
    """The finding itself, and the only case that can close it.

    `Invoke` used to answer `INVOKE_OK` and change nothing. So this case
    ignores what the action answers and reads the panel.
    """
    with rendered.laid_out(game_data, "boss_tab", WIDTH) as (_, tab):
        card = cards(tab)[4]
        assert tab.detail_name.text() == EMPTY_PANEL

        actions = interface(card).actionInterface()
        assert actions is not None, (
            "the card offers no actions at all, so an assistive tool has "
            "nothing to invoke")
        assert QAccessibleActionInterface.pressAction() in actions.actionNames()
        actions.doAction(QAccessibleActionInterface.pressAction())
        rendered.settle()

        assert tab.detail_name.text() == card.boss["name"], (
            f"the accessible Press on the {card.boss['name']} card left the "
            f"panel on {tab.detail_name.text()!r}")


def test_every_key_the_card_announces_really_presses_it(game_data, qapp):
    """A screen reader reads the key bindings out. They have to be true.

    Announced and answered are two different lists, and this is the only
    case that puts them together: each name the action publishes is turned
    back into a key and typed at the card, and the panel has to move.
    """
    with rendered.laid_out(game_data, "boss_tab", WIDTH) as (_, tab):
        card = cards(tab)[1]
        actions = interface(card).actionInterface()
        announced = actions.keyBindingsForAction(
            QAccessibleActionInterface.pressAction())
        assert announced, "the Press action names no key a reader could type"

        for name in announced:
            sequence = QKeySequence(name)
            assert not sequence.isEmpty(), (
                f"the card announces {name!r}, which is not a key")
            tab.show_detail(None)
            rendered.settle()
            card.setFocus()
            type_key(card, sequence[0].key())
            assert tab.detail_name.text() == card.boss["name"], (
                f"the card announces {name!r} as a way to press it, and "
                f"typing it left the panel on {tab.detail_name.text()!r}")


def test_tab_moves_from_one_card_to_the_next(game_data, qapp):
    """The cards have to be in the tab order before any key can matter.

    Driven with the Tab key rather than `setFocus`, because that is what a
    reader has: a card that was focusable but skipped by the focus chain
    would pass a `setFocus` case and fail a person.
    """
    with rendered.laid_out(game_data, "boss_tab", WIDTH) as (_, tab):
        first = cards(tab)[0]
        first.setFocus()
        rendered.settle()
        press_tab(first)

        landed = QApplication.focusWidget()
        assert isinstance(landed, bosstab.BossCard) and landed is not first, (
            f"Tab from the first Nightlord card went to {landed}, so the "
            f"grid cannot be walked with the keyboard")


@pytest.mark.parametrize("key, named", [
    (Qt.Key_Return, "Return"), (Qt.Key_Enter, "Enter"),
    (Qt.Key_Space, "Space"),
])
def test_each_press_key_opens_the_profile(game_data, qapp, key, named):
    """All three, separately: a card that took only Enter would fail a
    reader who was told Space and given nothing."""
    with rendered.laid_out(game_data, "boss_tab", WIDTH) as (_, tab):
        card = cards(tab)[6]
        card.setFocus()
        rendered.settle()
        type_key(card, key)

        assert tab.detail_name.text() == card.boss["name"], (
            f"{named} on the {card.boss['name']} card left the panel on "
            f"{tab.detail_name.text()!r}")


def test_a_key_that_is_not_a_press_leaves_the_panel_alone(game_data, qapp):
    """Otherwise the three cases above would pass on a card that opens on
    every key, which is not keyboard operation but a stuck control."""
    with rendered.laid_out(game_data, "boss_tab", WIDTH) as (_, tab):
        card = cards(tab)[6]
        card.setFocus()
        rendered.settle()
        type_key(card, Qt.Key_A)

        assert tab.detail_name.text() == EMPTY_PANEL, (
            f"typing a letter on the {card.boss['name']} card opened "
            f"{tab.detail_name.text()!r}")


def test_the_keyboard_can_be_seen_on_the_grid(game_data, qapp):
    """Focus a reader cannot see is focus a reader cannot use.

    Read off the drawn card and not off `hasFocus`, because what is being
    asserted is that the mark reaches the screen -- the same reason the
    pointer and selection marks are read off pictures (QA-150, QA-154).

    Reached with Tab, and that is load-bearing: Fusion draws a focus
    rectangle only once the window has seen a keyboard focus change, so a
    card focused by a click is deliberately left unmarked and `setFocus`
    alone would measure the wrong state. Exactly one card may change, or the
    mark says "here" in two places.
    """
    with rendered.laid_out(game_data, "boss_tab", WIDTH) as (_, tab):
        first = cards(tab)[0]
        first.setFocus()
        rendered.settle()
        before = pictures(tab)

        press_tab(first)
        landed = QApplication.focusWidget()
        after = pictures(tab)
        changed = sorted(name for name in before if before[name] != after[name])

        assert changed == [landed.boss["name"]], (
            f"Tab put the keyboard on {landed.boss['name']} and the grid "
            f"changed on {changed}, so a reader walking the cards cannot see "
            f"where he is")
