"""Putting a build back must never be how a build is lost.

One theme, six findings. Enforcing ownership (QA-002) taught the slots to
rebuild their lists from what the other five are holding, and the first three
of these are that rebuild running at a moment when the slots do not yet hold
the build being asked about:

* **QA-013** -- the picker's search term was remembered on every slot, and the
  next relic chosen re-filtered all six. A relic that did not match the term
  was dropped out of its slot, and the loss was written down. A typo emptied
  the lot.
* **QA-014** -- the lists are built while the *outgoing* vessel's relics are
  still in the slots, so the incoming build's own relics count as taken and
  cannot be put back. The restore said so with a `False` nobody read, and the
  slot kept the relic of the vessel being left.
* **QA-015** -- a build stored before ownership was enforced can name one
  physical relic twice. It was restored twice, counted twice, and then quietly
  halved at the next unrelated click.

The other three are what the restore does with an identity it has settled on,
and what it says about the result:

* **QA-021** -- a slot's list holds one entry per roll while a build names one
  copy per slot, so the second copy of a roll was read out of the first one's
  entry. Both slots held one relic, the later was emptied, and the loss was
  written down.
* **QA-022** -- "Already worn in Slot 1" stayed on screen after slot 1 gave
  the relic up, so the text was false exactly when the player did what it
  asked.
* **QA-024** -- what "Load equipped" said afterwards counted the save's
  relics rather than the placed ones, and named a search box that no longer
  exists.

None of the 60 tests that existed when the first three were found touched a
restore, which is why all of them came out of manual testing against a real
save. These do: every case here goes through the window's own restore paths.
"""

from __future__ import annotations

import pytest

from nrplanner import app as appmod
from nrplanner import chalices, favourites, inventory, model
from tests.relics import (equip, make_relic, offered, other_vessel_row,
                          select_vessel, some_effect_ids, stored_keys,
                          templates_for, unequip, vessel_at)

# Handles for relics the test owns. Distinct per test so a leftover setting
# from one cannot be mistaken for the relic of another.
WORN_HANDLE = 7001
SECOND_HANDLE = 7002
# A handle no relic in the test inventory carries: the build names it, the
# player no longer has it.
MELTED_HANDLE = 7999


def relics_in(planner) -> list:
    """What the ordinary slots hold, in order."""
    return [slot.current_relic() for slot in planner.base_slots]


def own(planner, relics: list) -> None:
    planner.owned = inventory.Inventory(source="test", relics=list(relics))


# -- QA-013: a search term is not allowed to empty a slot -------------------

def test_a_remembered_search_leaves_the_other_slots_alone(
        planner, game_data, two_slots_of_one_colour):
    """Type into the picker, choose a relic, and the other slots are untouched.

    The reproduction from the finding: slot 1 filled, slot 2 filled through the
    picker with a term typed into it first. The term reached every slot and the
    next rebuild dropped whatever no longer matched -- with a term that matches
    nothing, which is what a typo is, every other slot emptied.
    """
    row, vessel, colour = two_slots_of_one_colour
    templates = templates_for(game_data, colour, 2)
    first_relic = make_relic(templates[0], handle=WORN_HANDLE, index=0,
                             effects=some_effect_ids(game_data, 2))
    second_relic = make_relic(templates[1], handle=SECOND_HANDLE, index=1,
                              effects=some_effect_ids(game_data, 2))
    own(planner, [first_relic, second_relic])
    select_vessel(planner, row)

    first, second = [i for i, c in enumerate(vessel["slots"]) if c == colour][:2]
    equip(planner.base_slots[first], first_relic)

    # What the picker reports when the player types before choosing.
    planner._set_search("no effect is called this")
    equip(planner.base_slots[second], second_relic)

    assert planner.base_slots[first].current_relic() is first_relic, \
        "a search in the picker must not take the relic out of another slot"
    assert planner.base_slots[first].saved_key() == chalices.slot_key(first_relic), \
        "and the loss must not be written down either"


def test_a_search_does_not_reach_the_slot_headings(
        planner, game_data, two_slots_of_one_colour):
    """The window has no search box, so no slot may report a match count.

    The headings stood at "(4 match)" against a filter the player could not
    see and could not clear -- the same remembered term, and the visible half
    of the same mistake.
    """
    row, vessel, colour = two_slots_of_one_colour
    template = templates_for(game_data, colour, 1)[0]
    relic = make_relic(template, handle=WORN_HANDLE, index=0,
                       effects=some_effect_ids(game_data, 2))
    own(planner, [relic])
    select_vessel(planner, row)

    first = [i for i, c in enumerate(vessel["slots"]) if c == colour][0]
    planner._set_search("no effect is called this")
    equip(planner.base_slots[first], relic)

    for slot in planner.base_slots:
        assert "match" not in slot.title.text(), slot.title.text()


def test_a_slot_lists_the_relic_it_holds_whatever_it_is_asked(
        planner, game_data, two_slots_of_one_colour):
    """The rule holds in the slot, not in the caller.

    Both places that narrow a slot's list from outside carry a comment warning
    that this is how an equipped relic disappears, and the ownership rebuild
    walked into it anyway from a third direction. So the slot itself refuses:
    whatever it holds is in its own list, however that list was arrived at.
    """
    row, vessel, colour = two_slots_of_one_colour
    template = templates_for(game_data, colour, 1)[0]
    relic = make_relic(template, handle=WORN_HANDLE, index=0,
                       effects=some_effect_ids(game_data, 2))
    own(planner, [relic])
    select_vessel(planner, row)

    first = [i for i, c in enumerate(vessel["slots"]) if c == colour][0]
    slot = planner.base_slots[first]
    equip(slot, relic)

    # Any caller claiming the relic in this slot is spoken for elsewhere.
    slot.taken_elsewhere = lambda asking: {inventory.copy_key(relic)}
    slot.populate()

    assert slot.current_relic() is relic
    assert relic in offered(slot)


# -- QA-014: the incoming build wins over the one being left ----------------

def test_switching_vessels_restores_the_build_of_the_one_arrived_at(
        planner, game_data, two_vessels_sharing_a_colour):
    """The same relic, in a different slot in each of two vessels.

    Measured against the state before the ownership fix: the incoming vessel
    came up holding the *outgoing* vessel's relic, and its own stored build was
    overwritten with that on the spot.
    """
    pair = two_vessels_sharing_a_colour
    template = templates_for(game_data, pair.colour, 1)[0]
    relic = make_relic(template, handle=WORN_HANDLE, index=0,
                       effects=some_effect_ids(game_data, 2))
    own(planner, [relic])

    other = vessel_at(planner, pair.other_row)
    select_vessel(planner, pair.other_row)
    equip(planner.base_slots[pair.there], relic)
    assert stored_keys(planner, other["id"])[pair.there] == \
        chalices.slot_key(relic), "the test's own premise: that build is stored"

    select_vessel(planner, pair.row)
    equip(planner.base_slots[pair.here], relic)

    select_vessel(planner, pair.other_row)

    assert relics_in(planner) == [relic if i == pair.there else None
                                  for i in range(3)]
    assert stored_keys(planner, other["id"])[pair.there] == \
        chalices.slot_key(relic), "and the stored build still names it"


def test_a_chalice_left_and_returned_to_is_holding_what_it_held(
        planner, game_data, two_vessels_sharing_a_colour):
    """Emptying the slots on the way out must not empty the build behind them.

    A chalice being left has its slots cleared before the lists are rebuilt --
    what is in them belongs to it, and it is going. The build itself is stored
    per vessel and has to survive that, or the fix for QA-014 would cost more
    than the finding did.
    """
    pair = two_vessels_sharing_a_colour
    template = templates_for(game_data, pair.colour, 1)[0]
    relic = make_relic(template, handle=WORN_HANDLE, index=0,
                       effects=some_effect_ids(game_data, 2))
    own(planner, [relic])

    select_vessel(planner, pair.row)
    equip(planner.base_slots[pair.here], relic)

    select_vessel(planner, pair.other_row)
    assert relics_in(planner) == [None, None, None],         "the chalice arrived at has no build of its own yet"

    select_vessel(planner, pair.row)
    assert relics_in(planner) == [relic if i == pair.here else None
                                  for i in range(3)]


def test_a_stored_relic_that_cannot_be_placed_empties_its_slot(
        planner, game_data, two_slots_of_one_colour):
    """A build naming a relic the player no longer owns leaves an empty slot.

    Not the relic that happened to be there. The restore knew it had placed
    nothing and nobody read the answer, so the slot kept what the previous
    build had put in it -- and the next write made that the stored build.
    """
    row, vessel, colour = two_slots_of_one_colour
    templates = templates_for(game_data, colour, 2)
    owned_relic = make_relic(templates[0], handle=WORN_HANDLE, index=0,
                             effects=some_effect_ids(game_data, 2))
    melted = make_relic(templates[1], handle=MELTED_HANDLE, index=1,
                        effects=some_effect_ids(game_data, 3)[1:])
    own(planner, [owned_relic])
    select_vessel(planner, row)

    first = [i for i, c in enumerate(vessel["slots"]) if c == colour][0]
    equip(planner.base_slots[first], owned_relic)

    keys = ["" for _ in range(6)]
    keys[first] = chalices.slot_key(melted)
    planner._apply_stored_build(vessel["id"], False, keys)

    assert planner.base_slots[first].current_relic() is None


# -- QA-015: an old build with one relic in two slots -----------------------

def test_an_old_build_with_one_relic_twice_is_resolved_when_it_is_restored(
        planner, game_data, two_slots_of_one_colour):
    """Resolved at the restore, and said out loud -- not at the next click.

    Builds stored before ownership was enforced can name one physical relic in
    two slots. Restoring it as written counted the relic twice (measured:
    Endurance 5 where the relic gives 4), and the next change to any slot
    emptied one of the two with nothing said anywhere.
    """
    row, vessel, colour = two_slots_of_one_colour
    template = templates_for(game_data, colour, 1)[0]
    effects = some_effect_ids(game_data, 2)
    relic = make_relic(template, handle=WORN_HANDLE, index=0, effects=effects)
    own(planner, [relic])

    first, second = [i for i, c in enumerate(vessel["slots"]) if c == colour][:2]
    hero_id = planner.current_hero()["id"]
    keys = ["" for _ in range(6)]
    keys[first] = keys[second] = chalices.slot_key(relic)
    chalices.save(hero_id, vessel["id"], False, keys)

    select_vessel(planner, row)

    holders = [i for i, item in enumerate(relics_in(planner)) if item is relic]
    assert holders == [first], "one physical relic, one slot"

    counted = [e["id"] for e in planner.selected_effects()]
    assert counted.count(effects[0]) == 1, \
        "and its effects reach the totals once, not twice"

    emptied = planner.base_slots[second]
    # isVisibleTo, not isVisible: the window is never shown in a test, so
    # nothing in it is visible in the sense Qt means by isVisible().
    assert emptied.rolled_label.isVisibleTo(emptied)
    assert (f"Already worn in Slot {first + 1} — pick another relic for "
            "this slot.") in emptied.rolled_label.text()


# -- QA-021: two copies of one roll are two relics --------------------------

def test_both_copies_of_one_roll_come_back_to_their_own_slots(
        planner, two_copies_of_one_roll):
    """Wearing a roll the save holds twice, and coming back to it.

    The list a slot offers holds one entry per roll, and the build names one
    copy per slot. While a restore runs nothing counts as taken, so both
    copies are free, the collapse throws the second away, the build's handle
    for it is no longer in the list and the roll behind it lands on the first
    copy. Two slots then held one relic, the later was emptied and the loss
    written down -- of a relic the same slot went on offering in the same
    list.

    The copies are the player's own: the finding is a list that disagrees
    with the save about what one relic is, and a pair built for the test
    would only show that if it were shaped to.
    """
    pair = two_copies_of_one_roll
    one, other = pair.copies
    select_vessel(planner, pair.row)
    equip(planner.base_slots[pair.first], one)
    equip(planner.base_slots[pair.second], other)

    stored = stored_keys(planner, pair.vessel["id"])
    assert stored[pair.first] == chalices.slot_key(one), \
        "the test's own premise: both copies are worn and both are stored"
    assert stored[pair.second] == chalices.slot_key(other)

    away = other_vessel_row(planner, pair.row)
    select_vessel(planner, away)
    select_vessel(planner, pair.row)

    assert planner.base_slots[pair.first].current_relic() is one
    assert planner.base_slots[pair.second].current_relic() is other, \
        "the second copy is a relic of its own, not a duplicate of the first"
    assert stored_keys(planner, pair.vessel["id"]) == stored, \
        "and neither copy is written out of the build"


def test_a_roll_falls_back_to_a_copy_no_other_slot_was_given(
        planner, two_copies_of_one_roll):
    """Handles are renumbered by the game, so a build can name a roll alone.

    Both slots then ask for the same roll and the answer has to be a copy
    each. Answering both with the first copy is the loss of QA-021 by another
    road: the second slot is emptied at the settle and told it is already
    worn.
    """
    pair = two_copies_of_one_roll
    one, other = pair.copies
    # The build as it reads after the save was rewritten: the roll survives a
    # renumbering, the handles do not.
    roll_only = chalices.SEPARATOR + favourites.key(one)
    keys = ["" for _ in range(6)]
    keys[pair.first] = keys[pair.second] = roll_only
    chalices.save(planner.current_hero()["id"], pair.vessel["id"], False, keys)

    select_vessel(planner, pair.row)

    worn = [planner.base_slots[pair.first].current_relic(),
            planner.base_slots[pair.second].current_relic()]
    assert None not in worn, "two copies are owned, so two slots can be filled"
    assert {inventory.copy_key(w) for w in worn} == \
        {inventory.copy_key(one), inventory.copy_key(other)}


# -- QA-022 and the stored build a restore must not rewrite -----------------

def a_build_wearing_one_relic_twice(planner, game_data, two_slots_of_one_colour):
    """Store a build that names one physical relic in two slots.

    The shape of a build written before ownership was enforced, which is the
    only way to come by one: the slots themselves have refused it since.
    """
    row, vessel, colour = two_slots_of_one_colour
    template = templates_for(game_data, colour, 1)[0]
    relic = make_relic(template, handle=WORN_HANDLE, index=0,
                       effects=some_effect_ids(game_data, 2))
    own(planner, [relic])
    first, second = [i for i, c in enumerate(vessel["slots"]) if c == colour][:2]
    keys = ["" for _ in range(6)]
    keys[first] = keys[second] = chalices.slot_key(relic)
    chalices.save(planner.current_hero()["id"], vessel["id"], False, keys)
    return row, vessel, first, second, relic, keys


def test_resolving_a_doubling_is_not_written_into_the_stored_build(
        planner, game_data, two_slots_of_one_colour):
    """The player's build is theirs until they change it themselves.

    Writing the resolution down made it permanent, and unexplained one click
    later: the label saying which slot kept the relic is gone by then, and
    nothing records that a slot was emptied. The stored build is left as it
    was instead, so the note comes back with the build -- every time, until
    the player resolves it.
    """
    row, vessel, first, second, _relic, keys = a_build_wearing_one_relic_twice(
        planner, game_data, two_slots_of_one_colour)

    select_vessel(planner, row)
    assert stored_keys(planner, vessel["id"]) == keys, \
        "the doubling is resolved on screen, not in the stored build"

    away = other_vessel_row(planner, row)
    select_vessel(planner, away)
    select_vessel(planner, row)

    emptied = planner.base_slots[second]
    assert f"Already worn in Slot {first + 1}" in emptied.rolled_label.text(), \
        "and the note comes back with it, because the state it describes has"


def test_the_note_goes_when_the_slot_it_names_gives_the_relic_up(
        planner, game_data, two_slots_of_one_colour):
    """"Already worn in Slot 1" is false the moment slot 1 is emptied.

    The text is wrong exactly when the player does what it asks: it describes
    a state of another slot and was kept as a property of this one, so
    nothing took it back.
    """
    row, _vessel, first, second, _relic, _keys = a_build_wearing_one_relic_twice(
        planner, game_data, two_slots_of_one_colour)

    select_vessel(planner, row)
    emptied = planner.base_slots[second]
    assert "Already worn" in emptied.rolled_label.text(), "the premise"

    unequip(planner.base_slots[first])

    assert "Already worn" not in emptied.rolled_label.text()
    assert not emptied.rolled_label.isVisibleTo(emptied), \
        "an empty slot with nothing to say says nothing"


# -- QA-024: what "Load equipped" reports afterwards ------------------------

def test_load_equipped_counts_what_it_placed_and_names_the_reason(
        planner, game_data, two_slots_of_one_colour):
    """The message is about the screen, not about the save.

    It counted the relics the save names, said "1 relics", and told the player
    to clear a search box that went away with QA-013. What could not be placed
    is worth saying, but about the right number and for the right reason.

    The reason has to be one that can really happen. A relic the save names
    and the inventory no longer holds arrives as an empty slot and is never
    counted here, so the failure left is a relic of a colour the slot the save
    puts it in will not take.
    """
    row, vessel, colour = two_slots_of_one_colour
    if colour == appmod.WHITE_SLOT:
        pytest.skip("a White slot takes every colour, so nothing can misfit")
    other_colour = next(c for c in sorted(model.COLOUR_NAMES)
                        if c not in (colour, appmod.WHITE_SLOT))
    kept = make_relic(templates_for(game_data, colour, 1)[0],
                      handle=WORN_HANDLE, index=0,
                      effects=some_effect_ids(game_data, 2))
    misfit = make_relic(templates_for(game_data, other_colour, 1)[0],
                        handle=SECOND_HANDLE, index=1,
                        effects=some_effect_ids(game_data, 3)[1:])
    first, second = [i for i, c in enumerate(vessel["slots"]) if c == colour][:2]
    relics = [None for _ in range(6)]
    relics[first] = kept
    relics[second] = misfit
    planner.owned = inventory.Inventory(
        source="test", relics=[kept, misfit],
        loadouts=[inventory.EquippedLoadout(
            hero_id=planner.current_hero()["id"], vessel_id=vessel["id"],
            selected=True, relics=relics)])

    select_vessel(planner, row)
    planner.load_equipped()

    note = planner.owned_label.text()
    assert planner.base_slots[first].current_relic() is kept
    assert planner.base_slots[second].current_relic() is None
    assert "search" not in note, note
    assert "1 relics" not in note, note
    assert "with 1 relic" in note, note
    assert "1 relic could not be placed" in note, note
    assert "does not fit the slot the save has it in" in note, note
