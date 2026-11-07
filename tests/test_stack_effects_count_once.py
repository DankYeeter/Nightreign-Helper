"""A stack effect counts on one relic, however many carry it (T-339.1).

User decision 2026-11-07, after T-337: "Attack power increased for each Night
Invader defeated" on two relics gave Optimize 1.07^4 at n=2, so it proposed the
second carrier. The count n belongs to the effect: the first carrier expands it,
every further one is reported the way a duplicate is and moves no figure. The
eight effects `model.accumulates` names all take this rule. `stacks` stays
true on all of them: `False` would end the count itself (measured in T-337).
"""

from __future__ import annotations

import pytest

from nrplanner import model, stacking
from nrplanner.advisor import explain, goals, run, search, types
from nrplanner.advisor.evaluate import evaluate

from tests import advisor_cases as advisor

NIGHT_INVADER = 7060200
LEVEL = 15


@pytest.fixture(scope="module")
def raider(game_data):
    return next(hero for hero in game_data["heroes"]
                if hero["name"] == "Raider")


def _rate(game_data, hero, carriers: int, declared: dict) -> model.Build:
    effect = game_data["effects"][str(NIGHT_INVADER)]
    return model.compute(hero, LEVEL, [effect] * carriers,
                         game_data.get("curves", {}), declared=declared)


def test_two_carriers_at_two_stacks_are_two_stacks_and_not_four(game_data,
                                                                raider):
    """The figure of T-339: 1.1449, where it was 1.3108."""
    one = _rate(game_data, raider, 1, {NIGHT_INVADER: 2})
    two = _rate(game_data, raider, 2, {NIGHT_INVADER: 2})
    assert one.rates["physicsAttackRate"] == pytest.approx(1.1449, abs=1e-4)
    assert two.rates["physicsAttackRate"] == pytest.approx(1.1449, abs=1e-4)


def test_every_stack_effect_counts_on_one_carrier(game_data, raider):
    """All eight, by the marker and not by a list: the second carrier leaves
    the totals as they were, and the warning names it."""
    stacking_ones = [effect for effect in game_data["effects"].values()
                     if model.accumulates(effect)]
    assert {effect["id"] for effect in stacking_ones} == model.STACK_EFFECT_IDS
    curves = game_data.get("curves", {})
    for effect in stacking_ones:
        declared = {effect["id"]: 2}
        one = model.compute(raider, LEVEL, [effect], curves, declared=declared)
        two = model.compute(raider, LEVEL, [effect, effect], curves,
                            declared=declared)
        assert (two.rates, two.attributes, two.other) == (
            one.rates, one.attributes, one.other), effect["name"]
        assert one.warnings == []
        assert [warning.kind for warning in two.warnings] == ["duplicate"]
        assert "x2 — only one will apply" in two.warnings[0].text


def test_a_second_carrier_is_reported_while_the_switch_is_off(game_data, raider):
    """Laid in a slot and not declared: still a duplicate worth saying."""
    two = _rate(game_data, raider, 2, {})
    assert [warning.kind for warning in two.warnings] == ["duplicate"]


def test_the_effects_tab_says_a_second_copy_adds_nothing(game_data):
    """`stacking` agrees with the totals rather than with the flag."""
    effect = game_data["effects"][str(NIGHT_INVADER)]
    assert effect["stacks"] is True, "the flag itself is not what changed"
    assert stacking.repetition(effect) == stacking.STRONGEST
    assert "second relic" in stacking.evidence(effect)


# -- the search -------------------------------------------------------------

def _answer(game_data, hero, rolls, colours, declared=()):
    owned = advisor.make_inventory(game_data, hero, count=len(rolls),
                                   rolls=rolls)
    problem = advisor.problem(colours)
    ctx = advisor.context(game_data, hero,
                          reference=advisor.scaling_armament(game_data, hero),
                          declared=declared)
    frozen = run.frozen_inventory(owned, problem)
    request = advisor.request_for(problem, ctx, frozen, goals.MAX_DAMAGE.id)
    return run.run(request, frozen, ctx, goals.GOALS), owned


def test_optimize_suggests_one_carrier_and_leaves_the_slot_empty_for_a_second(
        game_data, raider):
    """Two slots, two carriers, nothing else owned: the search fills what it
    can, and a second carrier is nothing it may fill a slot with."""
    result, owned = _answer(game_data, raider,
                            [[NIGHT_INVADER], [NIGHT_INVADER]],
                            [advisor.RED, advisor.RED],
                            declared=((NIGHT_INVADER, 2),))
    assert len(owned.relics) == 2
    best = result.suggestions[0]
    assert len(best.choices) == 1, [choice.name for choice in best.choices]


def test_a_carrier_is_not_suggested_beside_one_that_is_held(game_data, raider):
    """The first carrier may be the player's own."""
    owned = advisor.make_inventory(game_data, raider, count=2,
                                   rolls=[[NIGHT_INVADER], [NIGHT_INVADER]])
    held = advisor.held_relic(owned.relics[0])
    problem = advisor.problem([advisor.RED, advisor.RED])
    problem = types.SlotProblem(
        slots=problem.slots, held=(types.HeldSlot(index=0, relic=held),))
    ctx = advisor.context(game_data, raider,
                          reference=advisor.scaling_armament(game_data, raider),
                          declared=((NIGHT_INVADER, 2),))
    frozen = run.frozen_inventory(owned, problem)
    request = advisor.request_for(problem, ctx, frozen, goals.MAX_DAMAGE.id)
    result = run.run(request, frozen, ctx, goals.GOALS)
    assert all(not suggestion.choices for suggestion in result.suggestions)


def test_a_favourite_only_a_second_carrier_brings_still_gets_its_slot(
        game_data, raider):
    """A favourite binds harder than this rule: the player asked for the relic
    (`search._successors`, the forced branches)."""
    other = next(int(effect_id) for effect_id, effect
                 in game_data["effects"].items()
                 if not model.is_conditional(effect) and effect["stacks"]
                 and (effect.get("modifiers") or {}).get("physicsAttackRate"))
    owned = advisor.make_inventory(
        game_data, raider, count=2,
        rolls=[[NIGHT_INVADER], [NIGHT_INVADER, other]])
    problem = advisor.problem([advisor.RED, advisor.RED])
    problem = types.SlotProblem(slots=problem.slots,
                                required=frozenset({NIGHT_INVADER, other}))
    ctx = advisor.context(game_data, raider,
                          reference=advisor.scaling_armament(game_data, raider),
                          declared=((NIGHT_INVADER, 2),))
    frozen = run.frozen_inventory(owned, problem)
    request = advisor.request_for(problem, ctx, frozen, goals.MAX_DAMAGE.id)
    result = run.run(request, frozen, ctx, goals.GOALS)
    assert other not in result.required_left_out


def test_the_second_carrier_a_player_laid_says_it_adds_nothing(game_data, raider):
    """`Why` on a carrier the first one already counts for: AK-167 (a2)."""
    owned = advisor.make_inventory(game_data, raider, count=2,
                                   rolls=[[NIGHT_INVADER], [NIGHT_INVADER]])
    problem = advisor.problem([advisor.RED, advisor.RED])
    ctx = advisor.context(game_data, raider,
                          reference=advisor.scaling_armament(game_data, raider),
                          declared=((NIGHT_INVADER, 2),))
    frozen = run.frozen_inventory(owned, problem)
    pools = search.candidates.pools(frozen, problem, ctx, goals.GOALS,
                                    goals.MAX_DAMAGE.id)
    first = pools[0].candidates[0]
    second = next(copy for copy in pools[1].candidates
                  if copy.handle != first.handle)
    chosen = (first, second)
    built = evaluate(problem, chosen, ctx, goal=goals.MAX_DAMAGE)
    groups = explain.reasons(problem, chosen, evaluate(
        problem, (), ctx, goal=goals.MAX_DAMAGE), built, ctx, goals.MAX_DAMAGE)
    assert groups[0].effects_with_a_figure == 1
    assert [line.silence for line in groups[1].lines] == [
        types.SILENT_ALREADY_COUNTED]
