"""A relic is one physical object and cannot be worn in two slots.

QA-002. The same entry could be put into two slots and its effects counted
twice, with no warning and a perfectly plausible total. Verified against a
copy owned exactly once (handle 3229614262): Endurance went from 30 to 33.

That this is the common case and not an exotic one is a measurement: 309
owned relics carry 306 distinct rolls, so an entry in the picker stands for
exactly one physical relic 99 times out of 100. The user decided on
2026-09-01 that ownership is enforced; planning around a relic you do not own
is what "Custom relic" is for.

The inventory here is built in the test rather than read from the save, so
the awkward cases can be described exactly (see tests/relics.py): a relic
owned once, two copies of one roll, and a copy whose handle could not be read.
"""

from __future__ import annotations

from nrplanner import inventory
from tests.relics import (equip, make_relic, offered, select_vessel,
                          some_effect_ids, templates_for)


def slots_holding(planner, item) -> list[int]:
    """Which of the ordinary slots have this very relic in them."""
    return [index for index, slot in enumerate(planner.base_slots)
            if slot.current_relic() is item]


def test_one_relic_cannot_fill_two_slots(planner, game_data,
                                         two_slots_of_one_colour):
    """The copy in slot 1 is not on offer in slot 2, and it is owned once."""
    row, vessel, colour = two_slots_of_one_colour
    template = templates_for(game_data, colour, 1)[0]
    only_copy = make_relic(template, handle=4242, index=0,
                           effects=some_effect_ids(game_data, 2))
    planner.owned = inventory.Inventory(source="test", relics=[only_copy])
    select_vessel(planner, row)

    first, second = [i for i, c in enumerate(vessel["slots"]) if c == colour][:2]
    assert only_copy in offered(planner.base_slots[second]), \
        "before anything is equipped, both slots may have it"

    equip(planner.base_slots[first], only_copy)

    assert slots_holding(planner, only_copy) == [first]
    assert only_copy not in offered(planner.base_slots[second])
    assert only_copy in offered(planner.base_slots[first]), \
        "the slot holding it must still list it, or it could never be changed"


def test_a_second_copy_of_the_same_roll_is_still_offered(
        planner, game_data, two_slots_of_one_colour):
    """Two copies means two slots may have one each.

    The picker collapses identical rolls to one card, so this is the case a
    rule written on cards rather than on copies would get wrong -- it would
    refuse a relic the player owns twice.
    """
    row, vessel, colour = two_slots_of_one_colour
    template = templates_for(game_data, colour, 1)[0]
    rolls = some_effect_ids(game_data, 2)
    copies = [make_relic(template, handle=1000 + n, index=n, effects=rolls)
              for n in range(2)]
    planner.owned = inventory.Inventory(source="test", relics=copies)
    select_vessel(planner, row)

    first, second = [i for i, c in enumerate(vessel["slots"]) if c == colour][:2]
    on_offer = offered(planner.base_slots[first])
    assert len(on_offer) == 1, "one card per roll, as the picker has always done"

    equip(planner.base_slots[first], on_offer[0])

    still_free = offered(planner.base_slots[second])
    assert len(still_free) == 1
    assert still_free[0] is not planner.base_slots[first].current_relic()


def test_a_copy_without_a_handle_is_still_only_one_relic(
        planner, game_data, two_slots_of_one_colour):
    """A save whose loadout table cannot be read yields no handles at all.

    Dropping those relics would leave such a player with an empty planner;
    treating them as endlessly available would drop the rule exactly where it
    cannot be checked. The record's own place in the save says which copy it
    is either way.
    """
    row, vessel, colour = two_slots_of_one_colour
    template = templates_for(game_data, colour, 1)[0]
    handleless = make_relic(template, handle=None, index=7,
                            effects=some_effect_ids(game_data, 1))
    planner.owned = inventory.Inventory(source="test", relics=[handleless])
    select_vessel(planner, row)

    first, second = [i for i, c in enumerate(vessel["slots"]) if c == colour][:2]
    equip(planner.base_slots[first], handleless)

    assert handleless not in offered(planner.base_slots[second])


def test_a_custom_relic_may_be_planned_into_every_slot(
        planner, game_data, two_slots_of_one_colour):
    """Free planning is what "Custom relic" is for, and it is not ownership."""
    row, vessel, colour = two_slots_of_one_colour
    planner.owned = inventory.Inventory(source="test", relics=[])
    select_vessel(planner, row)

    first, second = [i for i, c in enumerate(vessel["slots"]) if c == colour][:2]
    rolls = some_effect_ids(game_data, 1)
    planner.base_slots[first].set_custom(rolls)
    planner.base_slots[second].set_custom(rolls)

    assert planner.base_slots[first].current_relic() is not None
    assert planner.base_slots[second].current_relic() is not None


def test_copy_key_tells_the_cases_apart():
    """The identity itself, without a window around it."""
    template = {"id": 5, "name": "x", "colour": 0}
    with_handle = make_relic(template, handle=9, index=0, effects=[])
    same_handle = make_relic(template, handle=9, index=1, effects=[])
    without = make_relic(template, handle=None, index=2, effects=[])
    other_without = make_relic(template, handle=None, index=3, effects=[])
    custom = inventory.OwnedItem(
        relic_id=inventory.CUSTOM_RELIC_ID, name="Custom relic", colour=0,
        effect_ids=[], is_deep=False)

    assert inventory.copy_key(with_handle) == inventory.copy_key(same_handle)
    assert inventory.copy_key(without) != inventory.copy_key(other_without)
    assert inventory.copy_key(without) != inventory.copy_key(with_handle)
    assert inventory.copy_key(custom) is None
    assert inventory.copy_key(None) is None
