"""The baseline assumes 3+ armaments of one type, never of two (QA-299).

AD-036.6, addendum 12.10.2026: of the armament-count conditions ("3+ X
Equipped") the advisor's baseline counts at most **one armament type** as met
in a suggestion; several copies of that type still stack as before, and a
condition the player declared by hand stands as declared. On the player's save
the first suggestion for Wylder counted "3+ Hammers" and "3+ Great Hammers"
together -- seven armaments with the starting one, against six places -- and
ranked at 90.2 where 62.7 was reachable without either.

User decision 28.10.2026 narrows it further: the type is the one of the
armament on the selected tile, and an empty tile assumes none. Ingame,
Wylder with his greatsword selected was offered "3+ Daggers Equipped".

The cases go the way the window goes: the context and its baseline from
`advisorbar.asking_from`, the answer from `run.run`. Every effect is found by
a property of the dataset, never by an id written down here.
"""

from __future__ import annotations

import dataclasses

import pytest

from nrplanner import advisorbar, effecttext, model, weaponslots
from nrplanner.advisor import goals, run, types
from nrplanner.advisor.evaluate import evaluate

from tests import advisor_cases as advisor

DAMAGE = "max_damage"
FIRST, SECOND, LESSER = 100, 101, 102


def two_armament_count_buffs(data: dict, hero: dict) -> tuple[int, int]:
    """The two lowest-numbered attack buffs gated on 3+ armaments of a type,
    of two different types, that work for this Nightfarer."""
    found: dict = {}
    for key in sorted(data["effects"], key=int):
        effect = data["effects"][key]
        mods = effect.get("modifiers") or {}
        if (effecttext.counts_armaments(effect)
                and mods.get("physicsAttackRate", 1.0) > 1.0
                and effecttext.works_for(effect, hero["name"])):
            found.setdefault(mods.get("wepTypeTrigger"), effect["id"])
        if len(found) == 2:
            return tuple(found.values())
    pytest.skip("this dataset has no two armament-count attack buffs")


def weaker_and_stronger_armament_count_buff(data: dict,
                                            hero: dict) -> tuple[int, int]:
    """Attack buffs gated on 3+ armaments of two types, the weaker type's
    first, by their physical rate."""
    rate_of = {}
    for key in sorted(data["effects"], key=int):
        effect = data["effects"][key]
        mods = effect.get("modifiers") or {}
        if (effecttext.counts_armaments(effect)
                and mods.get("physicsAttackRate", 1.0) > 1.0
                and effecttext.works_for(effect, hero["name"])):
            rate_of.setdefault(mods.get("wepTypeTrigger"),
                               (mods["physicsAttackRate"], effect["id"]))
    rates = sorted(set(rate for rate, _ in rate_of.values()))
    if len(rates) < 2:
        pytest.skip("this dataset has no two unequal armament-count buffs")
    return tuple(next(effect_id for rate, effect_id in rate_of.values()
                      if rate == wanted) for wanted in (rates[0], rates[-1]))


def armament_type(data: dict, effect_id: int):
    """The armament type a count condition asks for; without
    `wepTypeTrigger` it is the field's baseline (the dagger condition)."""
    return data["effects"][str(effect_id)]["modifiers"].get(
        "wepTypeTrigger", data["field_baselines"]["wepTypeTrigger"])


def select_an_armament_of(planner, data: dict, wep_type) -> None:
    """Put an armament of `wep_type` on the selected tile; `None` empties
    it."""
    weapon = None if wep_type is None else next(
        w for w in data["weapons"] if w["wep_type"] == wep_type)
    planner.weapon_slots[planner.active_weapon] = weaponslots.WeaponSlot(
        weapon=weapon)


def a_lesser_attack_buff(ctx: types.GoalContext, ceiling: float) -> int:
    """An always-on buff with a physical rate under `ceiling` that moves the
    damage figure -- measured, because a rate scoped to sorceries does not."""
    damage = goals.GOALS[DAMAGE]
    problem = advisor.problem([advisor.RED])

    def figure(effect_ids: tuple[int, ...]) -> float:
        carrying = dataclasses.replace(ctx, armament_effect_ids=effect_ids)
        return damage.score(evaluate(problem, (), carrying), carrying).value

    plain = figure(())
    for key in sorted(ctx.data["effects"], key=int):
        effect = ctx.data["effects"][key]
        rate = (effect.get("modifiers") or {}).get("physicsAttackRate", 1.0)
        if (1.0 < rate < ceiling and not model.is_conditional(effect, None)
                and effecttext.works_for(effect, ctx.hero["name"])
                and figure((effect["id"],)) > plain):
            return effect["id"]
    pytest.skip("this dataset has no weaker always-on attack buff")


def suggest(asking, data: dict, rolls: list[list[int]], slots: int,
            holding_first: bool = False):
    """The window's way: relics carrying one `rolls` entry each, offered to
    `slots` red places -- the first relic already held in the first place
    if `holding_first`."""
    owned = advisor.make_inventory(
        data, asking.ctx.hero, count=len(rolls),
        handles=list(range(FIRST, FIRST + len(rolls))), rolls=rolls)
    held = ({0: advisor.held_relic(owned.relics[0])} if holding_first
            else None)
    problem = advisor.problem([advisor.RED] * slots, held=held)
    frozen = run.frozen_inventory(owned, problem)
    request = advisor.request_for(problem, asking.ctx, frozen)
    return run.run(request, frozen, asking.ctx, goals.GOALS)


def answer(planner, data: dict, declared: dict[int, int],
           selected_type_of_first: bool = False):
    """Three red copies -- one buff each -- for two red slots, asked the
    window's way under the damage direction, with `declared` by hand and,
    if `selected_type_of_first`, an armament of the first buff's type on
    the selected tile."""
    planner.declared = dict(declared)
    both = two_armament_count_buffs(data, planner.current_hero())
    if selected_type_of_first:
        select_an_armament_of(planner, data, armament_type(data, both[0]))
    asking = advisorbar.asking_from(planner, DAMAGE)
    ceiling = min(data["effects"][str(effect_id)]["modifiers"]
                  ["physicsAttackRate"] for effect_id in both)
    lesser = a_lesser_attack_buff(asking.ctx, ceiling)
    rolls = [[both[0]], [both[1]], [lesser]]
    return suggest(asking, data, rolls, slots=2), both


def counted(suggestion: types.Suggestion, effect_ids) -> set[int]:
    """Which of these effects the suggestion's `Why` gives a figure."""
    return {line.effect_id for group in suggestion.reasons
            for line in group.lines
            if line.effect_id in effect_ids
            and line.silence == types.CARRIES_A_FIGURE}


def best_handles(result: types.AdvisorResult) -> set[int]:
    return {choice.handle for choice in result.suggestions[0].choices}


def test_no_suggestion_counts_two_armament_types_and_the_search_plans_for_it(
        planner, game_data):
    """The baseline: the selected tile's type counts, the second is worth
    nothing, so the weaker always-on buff takes the second slot instead."""
    result, both = answer(planner, game_data, {},
                          selected_type_of_first=True)

    for suggestion in result.suggestions:
        assert len(counted(suggestion, both)) <= 1, (
            "a suggestion counted 3+ armaments of two types at once")
    assert best_handles(result) == {FIRST, LESSER}, (
        "the search kept the second armament type, which counts for nothing, "
        "over a buff that does count")
    assert counted(result.suggestions[0], both) == {both[0]}


def test_a_type_the_selected_armament_is_not_counts_for_nothing(
        planner, game_data):
    """The ingame case: Wylder, his greatsword on the selected tile -- the
    dagger and the straight-sword condition are worth nothing."""
    selected = planner.active_slot().weapon
    both = two_armament_count_buffs(game_data, planner.current_hero())
    assert selected is not None
    assert selected["wep_type"] not in {armament_type(game_data, effect_id)
                                        for effect_id in both}

    result, both = answer(planner, game_data, {})

    for suggestion in result.suggestions:
        assert counted(suggestion, both) == set()
    assert LESSER in best_handles(result)


@pytest.mark.parametrize("hero_name", ["Wylder", "Duchess"])
def test_the_baseline_assumes_the_selected_armament_type_only(
        planner, game_data, hero_name):
    """The window's context: of the "3+ X Equipped" conditions only those
    of the selected armament's type -- "3+ Greatswords" for Wylder's
    greatsword, and the dagger condition, which carries no `wepTypeTrigger`,
    for Duchess' dagger only."""
    planner.select_hero(next(index for index, hero in enumerate(planner.heroes)
                             if hero["name"] == hero_name))
    planner.declared = {}
    wep_type = planner.active_slot().weapon["wep_type"]
    counts = {effect_id for effect_id in model.advisor_defaults()
              if effecttext.counts_armaments(
                  game_data["effects"][str(effect_id)])}

    asking = advisorbar.asking_from(planner, DAMAGE)

    assumed = set(asking.ctx.assumed_armament_counts)
    expected = {effect_id for effect_id in counts
                if armament_type(game_data, effect_id) == wep_type}
    assert expected and assumed == expected
    assert not counts & dict(asking.ctx.declared).keys()
    assert asking.request.assumed_armament_counts == (
        asking.ctx.assumed_armament_counts)


def test_an_empty_selected_tile_assumes_no_armament_type(planner, game_data):
    planner.declared = {}
    select_an_armament_of(planner, game_data, None)

    asking = advisorbar.asking_from(planner, DAMAGE)

    assert asking.ctx.assumed_armament_counts == ()
    assert not any(effecttext.counts_armaments(
        game_data["effects"][str(effect_id)])
        for effect_id, _ in asking.ctx.declared)


def test_two_selected_types_are_two_keys(planner, game_data):
    """A cached answer for one tile's type is not handed back for another."""
    planner.declared = {}
    first = advisorbar.asking_from(planner, DAMAGE).request
    select_an_armament_of(planner, game_data, None)
    second = advisorbar.asking_from(planner, DAMAGE).request

    assert run.cache_key(first) != run.cache_key(second)


@pytest.mark.parametrize("by_hand, expected", [
    ("both", {FIRST, SECOND}),
    ("first", {FIRST, LESSER}),
])
def test_a_declaration_by_hand_stands_and_fixes_the_type(planner, game_data,
                                                         by_hand, expected):
    """Declared by hand, both types count -- the player said so. Declared
    for one type, the baseline adds no second one beside it."""
    first, second = two_armament_count_buffs(game_data,
                                             planner.current_hero())
    declared = ({first: 1, second: 1} if by_hand == "both" else {first: 1})
    result, both = answer(planner, game_data, declared)

    assert best_handles(result) == expected
    assert counted(result.suggestions[0], both) == (
        set(both) if by_hand == "both" else {first})


def test_the_type_that_counts_is_the_stronger_not_the_first_or_the_worst(
        planner, game_data):
    """The weaker type is held in the first place, so it always comes first
    in the build: only the stronger type, carried second, may carry a
    figure. A context that assumes two types: `evaluate`'s contract -- the
    window assumes the selected tile's type only (28.10.2026)."""
    planner.declared = {}
    asking = advisorbar.asking_from(planner, DAMAGE)
    weaker, stronger = weaker_and_stronger_armament_count_buff(
        game_data, asking.ctx.hero)
    asking = dataclasses.replace(asking, ctx=dataclasses.replace(
        asking.ctx, assumed_armament_counts=tuple(sorted((weaker, stronger)))))
    result = suggest(asking, game_data, [[weaker], [stronger]], slots=2,
                     holding_first=True)

    assert result.suggestions
    for suggestion in result.suggestions:
        assert counted(suggestion, (weaker, stronger)) == {stronger}


def a_weapon_type_attack_buff(data: dict, hero: dict, wep_type) -> int:
    """The lowest-numbered "Improved <type> Attack Power" -- an attack buff
    gated on `triggerOnWepType` alone -- for this type and Nightfarer."""
    for key in sorted(data["effects"], key=int):
        effect = data["effects"][key]
        mods = effect.get("modifiers") or {}
        if (mods.get("triggerOnWepType") == wep_type
                and mods.get("physicsAttackRate", 1.0) > 1.0
                and effecttext.works_for(effect, hero["name"])):
            return effect["id"]
    pytest.skip(f"this dataset has no attack buff for weapon type {wep_type}")


def test_a_weapon_type_buff_counts_only_for_the_selected_type(
        planner, game_data):
    """Ingame 1.19.0: Wylder, his greatsword on the selected tile, was
    offered "Improved Dagger Attack Power" as a figure. User decision
    01.11.2026: only the selected tile's type counts -- an armament of the
    other type on another tile changes nothing. A `triggerOnWepType` no
    armament carries (256, 512) stays."""
    planner.declared = {}
    hero = planner.current_hero()
    selected = planner.active_slot().weapon["wep_type"]
    known = {weapon.get("wep_type") for weapon in game_data["weapons"]}
    other = min(known - {selected, None})
    off = a_weapon_type_attack_buff(game_data, hero, other)
    on = a_weapon_type_attack_buff(game_data, hero, selected)
    no_armament = next(effect_id for effect_id in model.advisor_defaults()
                       if game_data["effects"][str(effect_id)]["modifiers"]
                       .get("triggerOnWepType", 0) not in known | {0})
    elsewhere = (planner.active_weapon + 1) % weaponslots.SLOT_COUNT
    planner.weapon_slots[elsewhere] = weaponslots.WeaponSlot(weapon=next(
        w for w in game_data["weapons"] if w["wep_type"] == other))

    asking = advisorbar.asking_from(planner, DAMAGE)

    declared = dict(asking.ctx.declared)
    assert off not in declared, "a buff for an unselected type was assumed"
    assert on in declared and no_armament in declared
    result = suggest(asking, game_data, [[off], [on]], slots=2)
    assert counted(result.suggestions[0], (off, on)) == {on}

    select_an_armament_of(planner, game_data, other)
    assert off in dict(advisorbar.asking_from(planner, DAMAGE).ctx.declared)
