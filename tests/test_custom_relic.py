"""A relic the player does not own, planned with anyway.

"Custom relic" is the answer the user was given when they decided on
2026-09-01 that the planner enforces ownership (QA-002): a build may still be
planned around a roll nobody has, but through a relic that says what it is
rather than by counting a real one twice.

QA-025 is that answer failing. `set_colour` dropped the custom relic whenever
it ran, and it runs on every apply of the chalice -- so one click on the Deep
of Night switch deleted it, the effects fell out of the totals, and the key
the build had written down for it (`|-1|10000,10001|`) stayed behind, being a
key nothing could ever redeem again. The director decided on 2026-09-02 that
the custom relic persists rather than becoming session-local.

Two things have to hold for that, and they are what these tests are: a rebuild
of the slots that changes nothing must not touch it, and a build that names
one must be able to put it back -- from the key alone, because there is
nothing in the save to look it up in. The second holds across a chalice and
across a session, which are the same restore reached from two directions.
"""

from __future__ import annotations

import pytest

from nrplanner import inventory
from tests.relics import select_vessel, stored_keys, vessel_at


def custom_effects_for(slot, count: int = 2) -> list[int]:
    """Effects this slot could really have rolled, which is what it may take."""
    rollable = slot.rollable_effects()
    if len(rollable) < count:
        pytest.skip(f"no {count} effects can roll in this slot")
    return [e["id"] for e in rollable[:count]]


def first_vessel_row(planner) -> int:
    from PySide6.QtCore import Qt

    for row in range(planner.chalice_list.count()):
        if planner.chalice_list.item(row).data(Qt.UserRole) is not None:
            return row
    pytest.skip("this Nightfarer has no chalice")


def test_the_deep_switch_does_not_delete_a_custom_relic(planner):
    """One click on Deep of Night, and the relic is still there.

    The switch rebuilds every slot, which is all it has to do -- the colours
    it gives them are the colours they already had. A custom relic is built
    for a colour, so a colour that has not changed is no reason to drop it.
    """
    row = first_vessel_row(planner)
    select_vessel(planner, row)
    vessel = vessel_at(planner, row)
    slot = planner.base_slots[0]
    effects = custom_effects_for(slot)
    slot.set_custom(effects)

    assert slot.current_relic() is slot.custom_item, "the premise"
    stored = stored_keys(planner, vessel["id"])

    planner.deep_check.setChecked(True)

    worn = planner.base_slots[0].current_relic()
    assert worn is not None, "the Deep switch is not a way to lose a relic"
    assert worn.relic_id == inventory.CUSTOM_RELIC_ID
    assert list(worn.effect_ids) == effects
    counted = [e["id"] for e in planner.selected_effects()]
    for effect_id in effects:
        assert effect_id in counted, "and its effects are still in the totals"
    assert stored_keys(planner, vessel["id"]) == stored, \
        "the stored key still names something that can be put back"


def test_a_custom_relic_comes_back_with_the_chalice_it_was_built_in(
        planner, a_slot_whose_colour_changes):
    """Built for a Red slot, dropped by a Blue one, back when Red returns.

    Both halves matter. A custom relic left in a slot whose colour changed
    would be an illegal relic in a legal build, which is what the drop in
    `set_colour` was for. But it is stored per vessel like any other relic,
    and the vessel it was built in is entitled to have it back -- from the key
    alone, since nothing owns it and no list can offer it until it exists
    again.
    """
    spot = a_slot_whose_colour_changes
    select_vessel(planner, spot.row)
    vessel = vessel_at(planner, spot.row)
    slot = planner.base_slots[spot.index]
    effects = custom_effects_for(slot)
    slot.set_custom(effects)
    stored = stored_keys(planner, vessel["id"])
    assert stored[spot.index], "the premise: the build names the custom relic"

    select_vessel(planner, spot.away_row)
    away = planner.base_slots[spot.index]
    assert away.custom_item is None, \
        "a relic built for another colour is not offered by this one"
    assert getattr(away.current_relic(), "relic_id", None) \
        != inventory.CUSTOM_RELIC_ID, "nor worn in it"

    select_vessel(planner, spot.row)

    back = planner.base_slots[spot.index].current_relic()
    assert back is not None, "the chalice it was built in gets it back"
    assert back.relic_id == inventory.CUSTOM_RELIC_ID
    assert list(back.effect_ids) == effects
    assert stored_keys(planner, vessel["id"]) == stored


def test_a_custom_relic_is_still_there_in_the_next_session(planner, game_data):
    """A second window over the same settings finds the relic it left there.

    The reason "not session-local" had to be decided rather than assumed: a
    custom relic is written into the build like any other, and a key that
    outlives the relic it names is a key nothing can redeem. Either both go or
    both stay, and the user was promised free planning through this relic when
    they asked for ownership to be enforced (QA-002).

    A second Planner over the same settings store is what a second session is.
    """
    from nrplanner import app as appmod

    row = first_vessel_row(planner)
    select_vessel(planner, row)
    vessel = vessel_at(planner, row)
    slot = planner.base_slots[0]
    effects = custom_effects_for(slot)
    slot.set_custom(effects)
    assert stored_keys(planner, vessel["id"])[0], "the premise"

    planner.close()
    next_session = appmod.Planner(game_data)
    try:
        worn = next_session.base_slots[0].current_relic()
        assert worn is not None, "the build named it, so the build gets it back"
        assert worn.relic_id == inventory.CUSTOM_RELIC_ID
        assert list(worn.effect_ids) == effects
    finally:
        next_session.close()
        next_session.deleteLater()
