"""Holding a slot: the control, the request it changes, and where it lives.

**A hold is view state of this window and of nothing else** (AD-017, OF-15).
It is keyed on `(Nightfarer, vessel, Deep)`, it is not written down anywhere,
and it is gone when the program is. Three losses of data in the `QSettings`
key space are the reason (cycles 4 and 5), so one case here is about the
absence of a write rather than about the presence of a behaviour -- which is
the only shape a criterion like OF-15 can take.

**Held is measured at the slots and at the request, never at the button.**
What a hold is worth is that `Apply all` leaves the slot alone and that the
search is not asked about it; the button being checked is how the player says
so and proves neither.

**The vessels are the ones this dataset really has.** Going away and coming
back (AK-60) is a statement about three real vessels of the current
Nightfarer and both Deep states, and a fixture that invented them would not
be travelling anywhere.
"""

from __future__ import annotations

import dataclasses

import pytest
from PySide6.QtCore import Qt, QSettings
from PySide6.QtWidgets import QToolButton

from nrplanner import advisorbar, app as appmod, chalices, favourites
from nrplanner.advisor import types

from tests.test_advisor_apply import (a_live_answer, an_answer_for, keys_of,
                                      two_offers)


def vessels_of(planner) -> list[tuple[int, dict]]:
    """(row, vessel) for every selectable row of the chalice list."""
    return [(row, planner.chalice_list.item(row).data(Qt.UserRole))
            for row in range(planner.chalice_list.count())
            if planner.chalice_list.item(row).data(Qt.UserRole) is not None]


def go_to(planner, row: int, deep: bool) -> None:
    """Stand on this vessel with Deep of Night in this position.

    Through the two controls a player uses, so that whatever the window hangs
    off them runs -- setting the fields would prove that a method calls the
    method beside it and nothing more.
    """
    planner.deep_check.setChecked(deep)
    planner.chalice_list.setCurrentRow(row)


def hold(card, on: bool = True) -> None:
    """Work a card's `Hold` button the way a player does."""
    card.hold_button.setChecked(on)


def a_relic_for(card):
    """One owned copy this slot can take, or a skip."""
    for copy in card._holdable():
        if copy.handle is not None:
            return copy
    pytest.skip("this slot colour has no owned copy in this save")


# --- the control ------------------------------------------------------------

def test_every_card_carries_the_button_the_section_describes(planner):
    """AK-54: a checkable button with a word on it, and the tooltip."""
    for card in list(planner.base_slots) + list(planner.deep_slots):
        button = card.hold_button
        assert isinstance(button, QToolButton)
        assert button.isCheckable()
        assert button.text() == "Hold"
        assert button.toolTip() == (
            "Optimize leaves this slot alone. You can still change it "
            "yourself. Holds are forgotten when the program closes.")


def test_the_button_stands_left_of_the_colour_chip(planner):
    """§4.1 places it there, and the chip is the card's last header item."""
    card = planner.base_slots[0]
    header = card.layout().itemAt(0).layout()
    order = [header.itemAt(i).widget() for i in range(header.count())]
    assert order.index(card.hold_button) == order.index(card.chip) - 1


def test_the_caption_says_which_state_this_is(planner):
    """`Hold` and `Held`, so the two are told apart without colour (AK-54)."""
    card = planner.base_slots[0]
    hold(card)
    assert card.hold_button.text() == "Held"
    hold(card, False)
    assert card.hold_button.text() == "Hold"


def test_no_string_of_the_hold_promises_it_will_last(planner):
    """AK-59: nothing on screen suggests a hold survives a restart.

    The words are the ones that would make the promise -- a `saved` or a
    `remembered` in any of these four strings is a claim the window cannot
    keep. The tooltip has to say the limit out loud, so that is asserted as
    well: silence would not be a promise, but §4.4 asks for more than silence.
    """
    said = " ".join((appmod.HOLD_TOOLTIP, appmod.HELD_EMPTY,
                     appmod.HOLD_RELEASED) + appmod.HOLD_CAPTIONS).lower()
    for promise in ("saved", "remembered", "stored", "kept", "permanent",
                    "next time", "restart"):
        assert promise not in said, f"{promise!r} promises a hold will last"
    assert "forgotten when the program closes" in appmod.HOLD_TOOLTIP


def test_a_slot_held_with_nothing_in_it_says_so(planner):
    """AK-55/§4.2: `held and staying empty` is a state the player may set."""
    card = planner.active_slots()[0]
    card.clear_relic()
    hold(card)

    assert appmod.HELD_EMPTY in card.rolled_label.text()
    assert card.rolled_label.isVisibleTo(card)
    hold(card, False)
    assert appmod.HELD_EMPTY not in card.rolled_label.text()


# --- where the hold lives ---------------------------------------------------

def test_holding_writes_nothing_to_the_settings_store(planner):
    """OF-15, as the absence it is: no key of the store is touched.

    The sharper half of the criterion. A hold written down and never read
    back would leave every behavioural case green -- the window would still
    start free -- while the key space had grown by exactly the kind of entry
    that cost this project data twice.
    """
    settings = QSettings(favourites.ORG, favourites.APP)
    before = sorted(settings.allKeys())

    card = planner.active_slots()[0]
    hold(card)
    hold(planner.active_slots()[-1])

    settings.sync()
    assert sorted(QSettings(favourites.ORG, favourites.APP).allKeys()) == before


def test_a_window_opened_afresh_holds_nothing(planner, game_data):
    """OF-15, the other half: after a restart no slot is held.

    The second window is built **without** emptying the settings store, which
    is what makes this a restart rather than a fresh installation: a hold
    that had been written down would be there to be read back, and this is
    the case that would find it.
    """
    hold(planner.active_slots()[0])
    assert planner.held_slot_indices()

    restarted = appmod.Planner(game_data)
    try:
        assert restarted.held_slot_indices() == frozenset()
        cards = list(restarted.base_slots) + list(restarted.deep_slots)
        assert [card.is_held() for card in cards] == [False] * len(cards)
        assert [card.hold_button.text() for card in cards] == (
            ["Hold"] * len(cards))
    finally:
        restarted.close()
        restarted.deleteLater()


def test_the_hold_survives_ten_round_trips_over_the_vessels(planner):
    """AK-60/OF-12, measured the way QA-014 was: ten trips, not one.

    Three vessels and both Deep states, so six builds each with a hold of its
    own, and the six are visited ten times in turn. One trip would pass on a
    hold that was merely never cleared; the fault class QA-014 records is a
    state that survives the first crossing and not the fourth.

    The slot held is different for the two Deep states on purpose: `Deep` is
    part of the key because it changes which slots exist, and a hold that
    carried across it would be a hold on a slot the player cannot see.
    """
    vessels = vessels_of(planner)
    if len(vessels) < 3:
        pytest.skip("this Nightfarer has fewer than three vessels")
    trips = [(row, vessel, deep) for row, vessel in vessels[:3]
             for deep in (False, True)]

    wanted: dict[tuple[int, bool], frozenset] = {}
    for row, vessel, deep in trips:
        go_to(planner, row, deep)
        cards = planner.active_slots()
        index = 4 if deep else 0
        assert index < len(cards), (
            f"{vessel['name']} with Deep {deep} has {len(cards)} slots")
        hold(cards[index])
        wanted[(vessel["id"], deep)] = frozenset({index})

    for trip in range(10):
        for row, vessel, deep in trips:
            go_to(planner, row, deep)
            here = wanted[(vessel["id"], deep)]
            assert planner.held_slot_indices() == here, (
                f"trip {trip + 1}, {vessel['name']}, Deep {deep}")
            drawn = frozenset(index for index, card
                              in enumerate(planner._all_slots())
                              if card.is_held())
            assert drawn == here, (
                f"trip {trip + 1}, {vessel['name']}, Deep {deep}: the cards "
                f"show {sorted(drawn)}")


def test_a_hold_whose_relic_left_the_save_falls_away_and_says_so(planner):
    """AK-56/§4.3: no hold falls away in silence.

    The save is re-read with every copy of that roll gone, which is what
    melting a relic looks like from in here. Every copy, because a build
    names a roll as well as a handle and would otherwise be answered with the
    copy next door -- the slot would still be full and the case would be
    measuring something else.
    """
    if planner.owned is None:
        pytest.skip("this machine has no save to read")
    card = planner.active_slots()[0]
    copy = a_relic_for(card)
    card.select_copy(copy.handle)
    hold(card)
    assert planner.held_slot_indices() == frozenset({0})

    roll = favourites.key(copy)
    planner.owned = dataclasses.replace(
        planner.owned,
        relics=[r for r in planner.owned.relics if favourites.key(r) != roll])
    planner.reload_chalices()

    assert planner.held_slot_indices() == frozenset()
    released = planner.active_slots()[0]
    assert not released.is_held()
    assert released.hold_button.text() == "Hold"
    assert appmod.HOLD_RELEASED in released.rolled_label.text()


def test_a_hold_whose_relic_is_still_owned_survives_a_re_read(planner):
    """The mirror of AK-56: nothing went, so nothing falls away.

    Without it the release rule could be "drop every hold whenever the save
    is read again", which passes the case above and takes the player's work
    with it. Same road, same call -- only the inventory is left alone.
    """
    if planner.owned is None:
        pytest.skip("this machine has no save to read")
    card = planner.active_slots()[0]
    copy = a_relic_for(card)
    card.select_copy(copy.handle)
    hold(card)

    planner.reload_chalices()

    assert planner.held_slot_indices() == frozenset({0})
    kept = planner.active_slots()[0]
    assert kept.is_held()
    assert kept.hold_button.text() == "Held"
    assert appmod.HOLD_RELEASED not in kept.rolled_label.text()


# --- the hold in the question ----------------------------------------------

def test_a_held_slot_is_a_boundary_of_the_question_not_a_free_slot(planner):
    """AD-014/AD-016: `problem.held` names it and `free_slots` does not."""
    if planner.owned is None:
        pytest.skip("this machine has no save to read")
    card = planner.active_slots()[0]
    copy = a_relic_for(card)
    card.select_copy(copy.handle)
    hold(card)

    asking = advisorbar.asking_from(planner, "max_damage")
    problem = asking.request.problem

    assert [entry.index for entry in problem.held] == [0]
    assert problem.held[0].relic is not None
    assert problem.held[0].relic.handle == copy.handle
    assert 0 not in {slot.index for slot in types.free_slots(problem)}
    assert copy.handle in types.held_handles(problem)


def test_a_slot_held_empty_reaches_the_question_as_held_and_empty(planner):
    """AD-014.7: `relic is None` is an instruction, not a missing value."""
    if planner.owned is None:
        pytest.skip("this machine has no save to read")
    card = planner.active_slots()[0]
    card.clear_relic()
    hold(card)

    problem = advisorbar.asking_from(planner, "max_damage").request.problem

    assert [(entry.index, entry.relic) for entry in problem.held] == [(0, None)]
    assert 0 not in {slot.index for slot in types.free_slots(problem)}


def test_a_held_custom_relic_travels_as_an_input(planner):
    """AK-58: a custom relic may be held, and holding is not suggesting.

    It carries no handle, so it occupies no copy and cannot come back out of
    the search as a suggestion -- which is exactly why AK-16 is untouched by
    it (`types.held_handles` says so in place).
    """
    if planner.owned is None:
        pytest.skip("this machine has no save to read")
    card = planner.active_slots()[0]
    effects = [effect["id"] for effect in card.rollable_effects()[:2]]
    if len(effects) < 2:
        pytest.skip("this slot colour has fewer than two rollable effects")
    card.set_custom(effects)
    hold(card)

    problem = advisorbar.asking_from(planner, "max_damage").request.problem

    assert problem.held[0].relic is not None
    assert problem.held[0].relic.handle is None
    assert list(problem.held[0].relic.effect_ids) == effects
    assert types.held_handles(problem) == frozenset()


def test_no_slot_held_means_the_question_holds_nothing(planner):
    """The state every run before this one was asked in, unchanged."""
    if planner.owned is None:
        pytest.skip("this machine has no save to read")
    problem = advisorbar.asking_from(planner, "max_damage").request.problem

    assert problem.held == ()
    assert len(types.free_slots(problem)) == len(problem.slots)


# --- the hold and applying --------------------------------------------------

def test_apply_all_does_not_touch_a_held_slot(planner):
    """AK-57/§5.4, in the sequence that makes the rule bite.

    A run is asked with the held slots taken out, so an answer worked out
    after the hold names no held slot and a filter over it would prove
    nothing. The sequence that reaches a held slot is the other order: the
    answer arrives, and **then** the player holds one of the slots it names.
    """
    offers = two_offers(planner)
    a_live_answer(planner, an_answer_for(offers))
    held_index, _copy = offers[0]
    free_index, free_copy = offers[1]
    hold(planner.active_slots()[held_index])
    before = keys_of(planner)

    planner.apply_all()

    keys = keys_of(planner)
    assert keys[held_index] == before[held_index]
    assert keys[free_index] == chalices.slot_key(free_copy)


def test_apply_all_does_not_fill_a_slot_held_empty(planner):
    """AK-55's second half: `held and staying empty` is respected."""
    offers = two_offers(planner)
    held_index, _copy = offers[0]
    planner.active_slots()[held_index].clear_relic()
    a_live_answer(planner, an_answer_for(offers))
    hold(planner.active_slots()[held_index])

    planner.apply_all()

    assert keys_of(planner)[held_index] == ""


def test_a_held_slot_is_not_offered_a_use_button(planner):
    """§5.4: no applying touches a held slot, so none is offered for one."""
    offers = two_offers(planner)
    a_live_answer(planner, an_answer_for(offers))
    held_index, _copy = offers[0]
    card = planner.active_slots()[held_index]
    assert card.suggestion.use_button.isVisibleTo(card)

    hold(card)

    assert not card.suggestion.use_button.isVisibleTo(card)


def test_undo_leaves_a_slot_held_since_the_applying_alone(planner):
    """§5.4: there is nothing of the advisor's in it to take back."""
    offers = two_offers(planner)
    a_live_answer(planner, an_answer_for(offers))
    before = keys_of(planner)

    planner.apply_all()
    applied = keys_of(planner)
    held_index, _copy = offers[0]
    hold(planner.active_slots()[held_index])
    planner.undo_apply()

    keys = keys_of(planner)
    assert keys[held_index] == applied[held_index]
    assert keys[offers[1][0]] == before[offers[1][0]]
