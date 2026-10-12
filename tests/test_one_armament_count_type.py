"""The baseline assumes 3+ armaments of one type, never of two (QA-299).

AD-036.6, addendum 12.10.2026: of the armament-count conditions ("3+ X
Equipped") the advisor's baseline counts at most **one armament type** as met
in a suggestion; several copies of that type still stack as before, and a
condition the player declared by hand stands as declared. On the player's save
the first suggestion for Wylder counted "3+ Hammers" and "3+ Great Hammers"
together -- seven armaments with the starting one, against six places -- and
ranked at 90.2 where 62.7 was reachable without either.

The cases go the way the window goes: the context and its baseline from
`advisorbar.asking_from`, the answer from `run.run`. Every effect is found by
a property of the dataset, never by an id written down here.
"""

from __future__ import annotations

import dataclasses

import pytest

from nrplanner import advisorbar, effecttext, model
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


def answer(planner, data: dict, declared: dict[int, int]):
    """Three red copies -- one buff each -- for two red slots, asked the
    window's way under the damage direction, with `declared` by hand."""
    planner.declared = dict(declared)
    asking = advisorbar.asking_from(planner, DAMAGE)
    both = two_armament_count_buffs(data, asking.ctx.hero)
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
    """The baseline: one type counts, the second is worth nothing, so the
    weaker always-on buff takes the second slot instead of it."""
    result, both = answer(planner, game_data, {})

    for suggestion in result.suggestions:
        assert len(counted(suggestion, both)) <= 1, (
            "a suggestion counted 3+ armaments of two types at once")
    assert LESSER in best_handles(result), (
        "the search kept the second armament type, which counts for nothing, "
        "over a buff that does count")


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
    figure."""
    planner.declared = {}
    asking = advisorbar.asking_from(planner, DAMAGE)
    weaker, stronger = weaker_and_stronger_armament_count_buff(
        game_data, asking.ctx.hero)
    result = suggest(asking, game_data, [[weaker], [stronger]], slots=2,
                     holding_first=True)

    assert result.suggestions
    for suggestion in result.suggestions:
        assert counted(suggestion, (weaker, stronger)) == {stronger}
