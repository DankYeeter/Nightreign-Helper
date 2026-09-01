"""Putting a build back must never be how a build is lost.

Enforcing ownership (QA-002) taught the slots to rebuild their lists from what
the other five are holding, and the trouble is every moment that rebuild runs
while the slots do not yet hold the build being asked about.

**QA-013** -- the picker's search term was remembered on every slot, and the
next relic chosen re-filtered all six. A relic that no longer matched the term
was dropped out of its slot, and the loss was written down; a typo emptied the
lot.

None of the 60 tests that existed when this was found touched a restore or a
rebuild, which is why it came out of manual testing against a real save.
"""

from __future__ import annotations

from nrplanner import chalices, inventory
from tests.relics import (equip, make_relic, offered, select_vessel,
                          some_effect_ids, templates_for)

# Handles for the relics the test owns. Distinct per relic, which is all a
# handle has to be.
WORN_HANDLE = 7001
SECOND_HANDLE = 7002


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
