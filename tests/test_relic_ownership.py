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
the awkward cases can be described exactly: a relic owned once, two copies of
one roll, and a copy whose handle could not be read.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt

from nrplanner import inventory

# Not a real save offset, only distinct per record, which is all it has to be.
FIRST_OFFSET = 0x1000
OFFSET_STRIDE = 0x50


def make_relic(template: dict, handle: int | None, index: int,
               effects: list[int]) -> inventory.OwnedItem:
    """One owned copy of a relic template."""
    return inventory.OwnedItem(
        relic_id=template["id"],
        name=template["name"].strip(),
        colour=template["colour"],
        effect_ids=list(effects),
        is_deep=bool(template.get("is_deep")),
        handle=handle,
        offset=FIRST_OFFSET + index * OFFSET_STRIDE,
    )


def templates_for(data: dict, colour: int, count: int) -> list[dict]:
    """Ordinary (not Deep) relic templates of one colour, lowest ids first."""
    found = sorted(
        (r for r in data["relics"]
         if r["colour"] == colour and not r.get("is_deep")),
        key=lambda r: r["id"],
    )
    if len(found) < count:
        pytest.skip(f"this dataset has fewer than {count} relics of colour "
                    f"{colour}")
    return found[:count]


def some_effect_ids(data: dict, count: int) -> list[int]:
    return [int(k) for k in sorted(data["effects"], key=int)[:count]]


@pytest.fixture
def two_slots_of_one_colour(planner, game_data):
    """A vessel with two slots of the same colour, selected on the planner.

    Repeated slot colours are where this rule bites: with three different
    colours a relic rarely fits two slots at all, and a test on such a vessel
    would pass while proving nothing (AD-013 measured it -- 5 unusable
    suggestions out of 40 against 40 out of 40).
    """
    for row in range(planner.chalice_list.count()):
        item = planner.chalice_list.item(row)
        vessel = item.data(Qt.UserRole)
        if vessel is None:
            continue
        colours = list(vessel["slots"])
        repeated = next((c for c in colours if colours.count(c) > 1), None)
        if repeated is not None:
            return row, vessel, repeated
    pytest.skip("no vessel in this dataset has two slots of one colour")


def _select(planner, row: int) -> None:
    planner.chalice_list.setCurrentRow(row)


def _slots_holding(planner, item) -> list[int]:
    return [index for index, slot in enumerate(planner.base_slots)
            if slot.current_relic() is item]


def _offered(slot) -> list:
    return [slot.relic_box.itemData(i) for i in range(slot.relic_box.count())
            if slot.relic_box.itemData(i) is not None]


def test_one_relic_cannot_fill_two_slots(planner, game_data,
                                         two_slots_of_one_colour):
    """The copy in slot 1 is not on offer in slot 2, and it is owned once."""
    row, vessel, colour = two_slots_of_one_colour
    template = templates_for(game_data, colour, 1)[0]
    only_copy = make_relic(template, handle=4242, index=0,
                           effects=some_effect_ids(game_data, 2))
    planner.owned = inventory.Inventory(source="test", relics=[only_copy])
    _select(planner, row)

    first, second = [i for i, c in enumerate(vessel["slots"]) if c == colour][:2]
    assert only_copy in _offered(planner.base_slots[second]), \
        "before anything is equipped, both slots may have it"

    planner.base_slots[first].relic_box.setCurrentIndex(
        planner.base_slots[first].relic_box.findData(only_copy))

    assert _slots_holding(planner, only_copy) == [first]
    assert only_copy not in _offered(planner.base_slots[second])
    assert only_copy in _offered(planner.base_slots[first]), \
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
    _select(planner, row)

    first, second = [i for i, c in enumerate(vessel["slots"]) if c == colour][:2]
    offered = _offered(planner.base_slots[first])
    assert len(offered) == 1, "one card per roll, as the picker has always done"

    planner.base_slots[first].relic_box.setCurrentIndex(
        planner.base_slots[first].relic_box.findData(offered[0]))

    still_free = _offered(planner.base_slots[second])
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
    _select(planner, row)

    first, second = [i for i, c in enumerate(vessel["slots"]) if c == colour][:2]
    planner.base_slots[first].relic_box.setCurrentIndex(
        planner.base_slots[first].relic_box.findData(handleless))

    assert handleless not in _offered(planner.base_slots[second])


def test_a_custom_relic_may_be_planned_into_every_slot(
        planner, game_data, two_slots_of_one_colour):
    """Free planning is what "Custom relic" is for, and it is not ownership."""
    row, vessel, colour = two_slots_of_one_colour
    planner.owned = inventory.Inventory(source="test", relics=[])
    _select(planner, row)

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
