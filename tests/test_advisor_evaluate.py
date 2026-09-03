"""One door to `model.compute`, and everything has to fit through it.

`advisor/evaluate.py` exists because "the held slots go into every evaluation"
is a rule that can be forgotten at three places for as long as there are three
places (AD-014.1). Two things therefore have to hold, and neither of them is
about arithmetic:

* the build the advisor computes for the state on screen is the build the
  window computes for it -- otherwise the advisor's ranking contradicts the
  stat sheet beside it, which is QA-001 in a new place;
* a candidate for a held slot is refused rather than applied, because holding
  is a boundary condition and not a starting value (AD-014).

The guard that there is only one door is in `test_one_build.py`; its
counter-build is the mutation `advisor-computes-in-a-second-place`.
"""

from __future__ import annotations

import pytest

from nrplanner import model
from nrplanner.advisor import evaluate as evaluate_module
from nrplanner.advisor.evaluate import evaluate

from tests import advisor_cases as advisor
from tests import relics as relic_helpers
from tests import weapon_damage_cases as cases


def equip_what_the_slots_will_take(planner) -> int:
    """Put an owned relic into every ordinary slot that has one on offer.

    Through the combo box, the way the picker does it, so the window reacts
    as it would for the player -- the reaction is what the comparison below
    is about.
    """
    filled = 0
    for slot in planner.base_slots:
        offered = relic_helpers.offered(slot)
        if offered:
            relic_helpers.equip(slot, offered[0])
            filled += 1
    return filled


def figures(build: model.Build) -> dict:
    """The numbers of a build, without the prose beside them.

    Warnings and the qualitative lists are text about the build rather than
    the build, and two orders of the same warnings would fail a comparison
    that says nothing about a total.
    """
    return {
        "attributes": dict(build.attributes),
        "base_attributes": dict(build.base_attributes),
        "rates": dict(build.rates),
        "class_rates": {k: dict(v) for k, v in build.class_rates.items()},
        "other": dict(build.other),
        "derived": dict(build.derived),
        "resistances": dict(build.resistances),
    }


def test_the_advisor_computes_the_build_the_window_shows(planner, game_data):
    """Checkpoint 13: one build, whoever asks for it.

    Read off the window's own `current_build()` rather than assembled twice
    in the test: assembling the same argument list here would compare this
    file against itself and prove nothing about which list is right.
    """
    if planner.owned is None:
        pytest.skip("this machine has no save, so no slot can be filled")
    if not equip_what_the_slots_will_take(planner):
        pytest.skip("this save owns nothing the current vessel can take")
    planner.recompute()

    problem = advisor.problem_from_planner(planner)
    ctx = advisor.context_from_planner(planner, game_data)

    assert figures(evaluate(problem, (), ctx)) == \
        figures(planner.current_build())


def test_a_curse_reaches_the_advisor_as_an_ordinary_effect(planner,
                                                           game_data):
    """AD-015: there is no second reckoning for a curse.

    The window counts a curse into the same `model.compute` call as the good
    rolls, and it has to, or a Deep of Night build's sheet is quietly wrong.
    The advisor inherits that by holding the curses of a held relic in the
    same list -- so a cursed relic on screen and the same cursed relic held
    produce one set of numbers, not two.
    """
    if planner.owned is None:
        pytest.skip("this machine has no save, so no relic can be equipped")
    planner.deep_check.setChecked(True)
    cursed = None
    for slot in planner.deep_slots:
        for item in relic_helpers.offered(slot):
            if item.curse_ids:
                relic_helpers.equip(slot, item)
                cursed = item
                break
        if cursed is not None:
            break
    if cursed is None:
        pytest.skip("this save owns no Deep of Night relic carrying a curse")
    planner.recompute()

    problem = advisor.problem_from_planner(planner)
    ctx = advisor.context_from_planner(planner, game_data)
    held = advisor.held_relic(cursed)

    assert held.curse_ids, "the case needs a copy that really rolled a curse"
    assert figures(evaluate(problem, (), ctx)) == \
        figures(planner.current_build())


def test_the_held_effects_reach_the_build(game_data):
    """Without this the base state would be the empty build under a new name.

    The failure it stands against is the quiet one: the advisor recommending
    a candidate whose contribution the held relic already caps. The score
    would not move, and the suggestion would still look plausible.
    """
    hero = cases.hero_by_name(game_data, "Wylder")
    inventory = advisor.make_inventory(game_data, hero, count=1)
    relic = inventory.relics[0]
    ctx = advisor.context(game_data, hero)

    empty = evaluate(advisor.problem([advisor.RED]), (), ctx)
    holding = evaluate(
        advisor.problem([advisor.RED],
                        held={0: advisor.held_relic(relic)}), (), ctx)

    assert holding.attributes["Strength"] > empty.attributes["Strength"], (
        "a held relic's effects have to be in every evaluation of this "
        "problem (AD-014)")


def test_a_candidate_for_a_held_slot_is_refused(game_data):
    """"Boundary condition, not starting value", enforced at the one door.

    A search that put a candidate into a held slot would silently overwrite
    the relic the player deliberately held -- the outcome `GOAL.md` F1 exists
    to prevent -- and it would do so with a plausible score.
    """
    hero = cases.hero_by_name(game_data, "Wylder")
    inventory = advisor.make_inventory(game_data, hero, count=2)
    held, offered = inventory.relics[0], inventory.relics[1]
    problem = advisor.problem([advisor.RED, advisor.RED],
                              held={0: advisor.held_relic(held)})
    ctx = advisor.context(game_data, hero)
    into_the_held_slot = model_candidate(offered, slot_index=0)

    with pytest.raises(ValueError, match="held"):
        evaluate(problem, (into_the_held_slot,), ctx)


def test_two_candidates_for_one_slot_are_refused(game_data):
    """Nothing says which of them wins, so nothing may pick one."""
    hero = cases.hero_by_name(game_data, "Wylder")
    inventory = advisor.make_inventory(game_data, hero, count=2)
    problem = advisor.problem([advisor.RED, advisor.RED])
    ctx = advisor.context(game_data, hero)
    both = tuple(model_candidate(relic, slot_index=0)
                 for relic in inventory.relics[:2])

    with pytest.raises(ValueError, match="two candidates"):
        evaluate(problem, both, ctx)


def test_the_armaments_own_effects_reach_the_build(game_data):
    """An armament's roll counts towards the sheet beside the relics'.

    One of the four things QA-001's second argument list left out. The
    advisor takes them from the context rather than from a slot, and a
    context that dropped them would rank every candidate against a build the
    window does not have.
    """
    hero = cases.hero_by_name(game_data, "Wylder")
    raises_strength = cases.effects_raising_attribute(
        game_data, hero, "Strength", 1)[0]
    problem = advisor.problem([advisor.RED])

    without = evaluate(problem, (), advisor.context(game_data, hero))
    with_it = evaluate(problem, (), advisor.context(
        game_data, hero, armament_effect_ids=(raises_strength,)))

    assert with_it.attributes["Strength"] > without.attributes["Strength"]


def test_a_declared_conditional_reaches_the_build(game_data):
    """A gated effect counts exactly as often as the player says it is live.

    The advisor has to inherit the declaration or it would rank a situational
    relic at nothing while the sheet beside it counts it three times.
    """
    hero = cases.hero_by_name(game_data, "Wylder")
    declarable = _a_gated_attribute_effect(game_data, hero)
    problem = advisor.problem([advisor.RED])

    silent = evaluate(problem, (), advisor.context(
        game_data, hero, armament_effect_ids=(declarable,)))
    declared = evaluate(problem, (), advisor.context(
        game_data, hero, armament_effect_ids=(declarable,),
        declared=((declarable, 1),)))

    assert declared.attributes != silent.attributes


def test_an_effect_this_dataset_does_not_know_is_skipped(game_data):
    """The window skips it too, and agreeing with the window is the point.

    Quiet skipping is a known weakness of that path (P4, QA-004/QA-032). It
    is inherited here on purpose: a save that names an effect a later game
    patch dropped must not make the advisor and the stat sheet disagree, and
    solving it in a second place is how they come to disagree.
    """
    hero = cases.hero_by_name(game_data, "Wylder")
    unknown = types_unknown_effect_id(game_data)
    problem = advisor.problem([advisor.RED])
    ctx = advisor.context(game_data, hero,
                          armament_effect_ids=(unknown,))

    assert evaluate_module.effect_ids_of(problem, (), ctx) == (unknown,)
    assert evaluate(problem, (), ctx).attributes == \
        evaluate(problem, (), advisor.context(game_data, hero)).attributes


# -- helpers ---------------------------------------------------------------

def model_candidate(relic, slot_index: int):
    """One owned copy as a candidate for a slot, unmeasured."""
    from nrplanner.advisor import types

    return types.Candidate(
        slot_index=slot_index, handle=relic.handle, relic_id=relic.relic_id,
        name=relic.name, colour=relic.colour, is_deep=relic.is_deep,
        effect_ids=tuple(relic.effect_ids), curse_ids=tuple(relic.curse_ids))


def types_unknown_effect_id(data: dict) -> int:
    """An effect id no record in this dataset carries."""
    return max(int(key) for key in data["effects"]) + 1


def _a_gated_attribute_effect(data: dict, hero: dict) -> int:
    """A gated effect that raises an attribute once its condition is declared.

    It has to move an **attribute**: a rate the advisor's assertion cannot see
    would make this pass for a build that received nothing.
    """
    curves = data.get("curves", {})
    for key in sorted(data["effects"], key=int):
        effect = data["effects"][key]
        if not model.is_conditional(effect, None):
            continue
        silent = model.compute(hero, advisor.LEVEL, [effect], curves)
        declared = model.compute(hero, advisor.LEVEL, [effect], curves,
                                 declared={int(effect["id"]): 1})
        if declared.attributes != silent.attributes:
            return int(effect["id"])
    raise LookupError("no gated attribute effect in this dataset")
