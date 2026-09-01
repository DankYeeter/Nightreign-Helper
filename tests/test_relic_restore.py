"""Putting a build back must never be how a build is lost.

Two findings, one theme. Enforcing ownership (QA-002) taught the slots to
rebuild their lists from what the other five are holding, and every one of
both is that rebuild running at a moment when the slots do not yet hold the
build being asked about:

* **QA-013** -- the picker's search term was remembered on every slot, and the
  next relic chosen re-filtered all six. A relic that did not match the term
  was dropped out of its slot, and the loss was written down. A typo emptied
  the lot.
* **QA-014** -- the lists are built while the *outgoing* vessel's relics are
  still in the slots, so the incoming build's own relics count as taken and
  cannot be put back. `select_saved` said so with a `False` nobody read, and
  the slot kept the relic of the vessel being left.
None of the 60 tests that existed when these were found touched a restore,
which is why both came out of manual testing against a real save. These do:
every case here goes through the window's own restore paths.
"""

from __future__ import annotations

from nrplanner import chalices, inventory
from tests.relics import (equip, make_relic, offered, select_vessel,
                          some_effect_ids, templates_for, vessel_at)

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


def stored_keys(planner, vessel_id: int) -> list[str]:
    """The build written down for one vessel, as the next session would read it."""
    return chalices.load(planner.current_hero()["id"], vessel_id)[2]


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


def test_a_stored_relic_that_cannot_be_placed_empties_its_slot(
        planner, game_data, two_slots_of_one_colour):
    """A build naming a relic the player no longer owns leaves an empty slot.

    Not the relic that happened to be there. `select_saved` returns False for
    exactly this and nobody read it, so the slot kept what the previous build
    had put in it -- and the next write made that the stored build.
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
