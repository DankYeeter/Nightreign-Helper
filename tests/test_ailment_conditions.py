"""An ailment-gated condition counts only where the build inflicts it.

User decision 01.11.2026: "Attack power up when facing frostbite-afflicted
enemy" and its poison and scarlet-rot twins count in the advisor's baseline only where the build inflicts the ailment
itself -- an armament anywhere on the grid, or a relic that makes the attacks
inflict it ("Starting armament inflicts frost"). A declaration by hand
stands. Every effect is found by a property of the dataset.
"""

from __future__ import annotations

import pytest

from nrplanner import advisorbar, effecttext, weaponslots
from nrplanner.advisor import types

from tests.test_one_armament_count_type import DAMAGE, counted, suggest

NAMED_AS = {"Poison": "poison", "Scarlet Rot": "rot", "Frost": "frost"}


def test_every_holder_of_a_state_names_its_ailment(game_data):
    """The table is read off the names; a state value whose holder names
    another ailment would count the wrong source."""
    labels = {label for weapon in game_data["weapons"]
              for label in weapon.get("inflicts") or {}}
    assert set(effecttext.AILMENT_OF_ENEMY_STATE.values()) <= labels
    holders = 0
    for effect in game_data["effects"].values():
        ailment = effecttext.ailment_awaited(effect)
        if ailment is not None:
            holders += 1
            assert NAMED_AS[ailment] in effecttext.name(effect).lower(), (
                effecttext.name(effect), ailment)
    assert holders


def awaiting(data: dict, hero: dict, ailment: str) -> int:
    """The lowest-numbered attack buff gated on `ailment` that works for this
    Nightfarer."""
    for key in sorted(data["effects"], key=int):
        effect = data["effects"][key]
        if (effecttext.ailment_awaited(effect) == ailment
                and effect["modifiers"].get("physicsAttackRate", 1.0) > 1.0
                and effecttext.works_for(effect, hero["name"])):
            return effect["id"]
    pytest.skip(f"this dataset has no attack buff gated on {ailment}")


def inflicting(data: dict, ailment: str) -> int:
    """The lowest-numbered relic effect that makes the attacks inflict
    `ailment` -- "Starting armament inflicts frost"."""
    for key in sorted(data["effects"], key=int):
        effect = data["effects"][key]
        if (ailment in (effect.get("inflicts_on_hit") or {})
                and effect.get("colours")):
            return effect["id"]
    pytest.skip(f"no relic effect in this dataset inflicts {ailment}")


def an_armament_inflicting(data: dict, ailment: str) -> dict:
    return next(weapon for weapon in data["weapons"]
                if ailment in (weapon.get("inflicts") or {}))


def test_without_a_source_the_condition_does_not_count(planner, game_data):
    """Wylder, his greatsword alone on the grid: the frost buff was counted
    as a figure before, though nothing in the build inflicts frost. The Why
    says it waits on its condition, as every uncounted condition does."""
    planner.declared = {}
    frost = awaiting(game_data, planner.current_hero(), "Frost")
    assert not any("Frost" in (slot.weapon.get("inflicts") or {})
                   for slot in planner.weapon_slots if slot.weapon)

    asking = advisorbar.asking_from(planner, DAMAGE)

    assert frost not in dict(asking.ctx.declared)
    assert frost in asking.ctx.awaiting_ailment
    result = suggest(asking, game_data, [[frost]], slots=1)
    assert counted(result.suggestions[0], (frost,)) == set()
    assert {line.silence for group in result.suggestions[0].reasons
            for line in group.lines if line.effect_id == frost} == {
        types.SILENT_UNDER_A_CONDITION}


def test_an_armament_on_any_tile_is_a_source(planner, game_data):
    planner.declared = {}
    hero = planner.current_hero()
    frost = awaiting(game_data, hero, "Frost")
    poison = awaiting(game_data, hero, "Poison")
    elsewhere = (planner.active_weapon + 1) % weaponslots.SLOT_COUNT
    cold = an_armament_inflicting(game_data, "Frost")
    assert "Poison" not in cold["inflicts"]
    planner.weapon_slots[elsewhere] = weaponslots.WeaponSlot(weapon=cold)

    asking = advisorbar.asking_from(planner, DAMAGE)

    declared = dict(asking.ctx.declared)
    assert frost in declared and poison not in declared
    result = suggest(asking, game_data, [[frost]], slots=1)
    assert counted(result.suggestions[0], (frost,)) == {frost}


def test_a_relic_source_and_its_beneficiary_are_found_as_a_pair(
        planner, game_data):
    """Relic A makes the starting armament inflict frost, relic B profits:
    held or suggested, A lets B count, and the search keeps both."""
    planner.declared = {}
    frost = awaiting(game_data, planner.current_hero(), "Frost")
    source = inflicting(game_data, "Frost")
    asking = advisorbar.asking_from(planner, DAMAGE)

    held = suggest(asking, game_data, [[source], [frost]], slots=2,
                   holding_first=True)
    both = suggest(asking, game_data, [[source], [frost]], slots=2)

    assert counted(held.suggestions[0], (frost,)) == {frost}
    assert counted(both.suggestions[0], (frost,)) == {frost}


def test_a_declaration_by_hand_stands(planner, game_data):
    frost = awaiting(game_data, planner.current_hero(), "Frost")
    planner.declared = {frost: 1}

    asking = advisorbar.asking_from(planner, DAMAGE)

    assert dict(asking.ctx.declared)[frost] == 1
    assert frost not in asking.ctx.awaiting_ailment
