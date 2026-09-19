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

**The first of those is only worth the state it is asked in** (QA-100). It
used to be asked in a default window -- level 1, one armament, nothing
declared, Deep off, Wylder -- where four of the seven arguments the advisor
hands `model.compute` could be thrown away and the whole suite stayed green.
The state is now built, and what it carries is asserted before the comparison
is made. The one argument no comparison of builds can reach, the reference
armament, is held by a second case that reads the call itself.

The guard that there is only one door is in `test_one_build.py`; its
counter-build is the mutation `advisor-computes-in-a-second-place`.
"""

from __future__ import annotations

import dataclasses

import pytest

from nrplanner import model, weaponslots
from nrplanner.advisor import evaluate as evaluate_module
from nrplanner.advisor.evaluate import evaluate

from tests import advisor_cases as advisor
from tests import relics as relic_helpers
from tests import weapon_damage_cases as cases


def equip_what_the_slots_will_take(planner) -> int:
    """Put an owned relic into every active slot that has one on offer.

    Through the combo box, the way the picker does it, so the window reacts
    as it would for the player -- the reaction is what the comparison below
    is about. Every active slot and not only the ordinary ones: with Deep of
    Night switched on the Deep slots are where the curses are, and a curse is
    one of the four things QA-001's shorter argument list left out.
    """
    filled = 0
    for slot in planner.active_slots():
        offered = relic_helpers.offered(slot)
        if offered:
            relic_helpers.equip(slot, offered[0])
            filled += 1
    return filled


def a_nightfarer_other_than_the_first(planner, level: int) -> int:
    """The index of a Nightfarer whose own numbers differ from `heroes[0]`.

    Wylder is `heroes[0]` and is what every synthetic case in this package
    asks about, so a comparison run on him cannot see a mix-up between "the
    Nightfarer on screen" and "the first one in the dataset" -- which is one
    of the four QA-100 measured surviving. Chosen by the base attributes
    rather than by name or by index, because it is the numbers that have to
    differ for the comparison to see anything.
    """
    first = planner.heroes[0]["levels"][str(level)]
    for index, hero in enumerate(planner.heroes[1:], start=1):
        if hero["levels"][str(level)] != first:
            return index
    raise LookupError("every Nightfarer in this dataset carries the same "
                      "attributes at this level")


def a_state_worth_comparing(planner, data: dict) -> dict:
    """Put the window into a state where every input the advisor reads bites.

    This is the whole of QA-100. The state the case used to compare was
    hollowed out -- level 1 because the slider is never moved and its minimum
    is 1, one armament which was also the reference, no armament effects,
    nothing declared, Deep of Night off, and Wylder, who is `heroes[0]`. Four
    of the seven arguments `evaluate` hands `model.compute` could therefore be
    thrown away with the whole suite staying green, at the one case whose
    entire purpose is to compare the advisor against the world outside it.

    Each line below exists to make one of them tell: a second armament of
    another type and an effect gated on that type (the grid against the
    armament being rated), a level that is not the slider's floor, a
    Nightfarer that is not the first, a declared condition, and Deep of Night
    for the curses. What the state carries is asserted rather than assumed --
    a case that believes in a state it has not got is the fault being fixed
    here, not the technique for fixing it.
    """
    level = cases.PROBE_LEVEL
    planner.select_hero(a_nightfarer_other_than_the_first(planner, level))
    planner.level_slider.setValue(level)
    planner.deep_check.setChecked(True)

    hero = planner.current_hero()
    gated_on_a_type, carrier, other = advisor.an_armament_type_gate(data, hero)
    declarable = advisor.a_gated_attribute_effect(data, hero)
    slots = [weaponslots.WeaponSlot() for _ in range(weaponslots.SLOT_COUNT)]
    # The gate rides on the armament that does **not** satisfy it, so only the
    # rest of the grid can make it live.
    slots[0] = weaponslots.WeaponSlot(
        weapon=other, tier=3, effect_ids=[gated_on_a_type, declarable])
    slots[1] = weaponslots.WeaponSlot(weapon=carrier, tier=2)
    planner.weapon_slots = slots
    planner.active_weapon = 0
    planner.declared = {declarable: 1}

    filled = equip_what_the_slots_will_take(planner)
    planner.recompute()
    return {"filled": filled, "gate": gated_on_a_type,
            "declared": declarable, "level": level}


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
    """Checkpoint 13: one build, whoever asks for it -- for one question.

    **What "whoever asks" no longer covers, said before anything else**
    (QA-227). Since A17 the running program does not put this question to
    the advisor at all: `advisorbar.asking_from` leaves `weapons_held` and
    `armament_effect_ids` empty and fills `reference` with the starting
    armament rather than the active tile (AD-038), because the armaments
    are rolled again every expedition, so the advisor's build is deliberately
    not the stat sheet's. What this case compares is the **arithmetic at the
    two doors given the same inputs** -- QA-001's fault was a second, shorter
    argument list, and that fault is still possible and still worth a guard.
    The context comes from `advisor_cases.context_from_planner`, which is the
    program's own context with the grid put back on for exactly this
    comparison; the three places it departs from the program are held to
    three by `tests/test_the_fixture_asks_what_the_program_asks.py`.

    Read off the window's own `current_build()` rather than assembled twice
    in the test: assembling the same argument list here would compare this
    file against itself and prove nothing about which list is right.

    **The state is built, not taken** (QA-100). The comparison is only worth
    the difference between its two sides, and a default window makes every
    input the same on both -- see `a_state_worth_comparing`. The assertions
    before the comparison are that state, said out loud: they are cheap, and
    the case they replace was green for years while three of the four inputs
    it is named for could be dropped without anything noticing.

    **What this case still cannot see, said rather than left implicit:** the
    reference armament itself. `model.compute` reads `weapon` only when
    `weapons_held` is empty, and the window fills both from the same grid, so
    the two are never in that combination. Dropping `weapon` therefore
    produces the identical build and no comparison of builds can catch it.
    That half is `test_evaluate_hands_the_whole_context_to_the_model` below,
    which reads what the model was *given* instead of what it said.
    """
    if planner.owned is None:
        pytest.skip("this machine has no save, so no slot can be filled")
    state = a_state_worth_comparing(planner, game_data)
    if not state["filled"]:
        pytest.skip("this save owns nothing the current vessel can take")

    problem = advisor.problem_from_planner(planner)
    ctx = advisor.context_from_planner(planner, game_data)
    held_curses = [entry for entry in problem.held
                   if entry.relic is not None and entry.relic.curse_ids]

    assert ctx.level != 1, "the level has to be off the slider's floor"
    assert ctx.hero is not game_data["heroes"][0], (
        "the Nightfarer has to be one that heroes[0] cannot stand in for")
    assert len({weapon.get("wep_type") for weapon in ctx.weapons_held}) > 1, (
        "the grid has to hold two armament types, or 'every armament held' "
        "and 'the one being rated' are the same set")
    assert state["gate"] in ctx.armament_effect_ids, (
        "the weapon-type gate has to be on the grid, or nothing depends on "
        "the grid being passed on whole")
    assert dict(ctx.declared), "no condition is declared, so `declared` is {}"
    if not held_curses:
        pytest.skip("this save owns no Deep of Night relic carrying a curse")

    # The sheet's own declarations, without the advisor's baseline on top:
    # the advisor's `declared` carries every switchable condition as met
    # (AD-036.6), and the sheet is the one thing A18 leaves untouched
    # (AK-282) -- so the comparison has to ask the sheet's question, exactly
    # as `ranking_with(..., as_the_bar_asked_before_a16)` does in
    # `test_advisor_goals.py`.
    as_the_sheet_declares = dataclasses.replace(
        ctx, declared=tuple(sorted(planner.declared.items())))
    assert figures(evaluate(problem, (), as_the_sheet_declares)) == \
        figures(planner.current_build())


#: Every field of `GoalContext`, and the argument of `model.compute` it
#: reaches -- or the reason it reaches none. QA-001 was a second, shorter
#: argument list; a field added to the context and then quietly not passed on
#: is the same fault arriving one field at a time, and the case below fails
#: until whoever adds one writes down which of the two this is.
CONTEXT_REACHES_COMPUTE = {
    "hero": "hero",
    "level": "level",
    "data": "curves, and the effect records behind the ids",
    "reference": "weapon",
    "weapons_held": "weapons_held",
    "armament_effect_ids": "effects",
    "declared": "declared",
    # The weighting is the goal's business and never the model's: it decides
    # how a figure is averaged after the build exists (AD-004, OF-3).
    "weighting": None,
    # The hand is the damage direction's business (AK-293): the model books
    # the `when Two-Handing` bucket either way, the goal decides whether to
    # count it. No display changes with the switch (AK-293 point 1).
    "two_handed": None,
}


def test_every_field_of_the_context_is_accounted_for():
    """A field can be added to the context; it cannot be added unnoticed.

    Needs no dataset: it reads the shape, not a run.
    """
    import dataclasses

    from nrplanner.advisor import types

    named = {field.name for field in dataclasses.fields(types.GoalContext)}

    assert named == set(CONTEXT_REACHES_COMPUTE), (
        "a field of GoalContext is not in the table above, so nothing says "
        "whether the model is meant to receive it: "
        f"{sorted(named ^ set(CONTEXT_REACHES_COMPUTE))}")


def test_evaluate_hands_the_whole_context_to_the_model(monkeypatch,
                                                       game_data):
    """What `model.compute` is given, argument by argument.

    The comparison against the window can only see arguments that move a
    number in the state a window can be in, and one of the seven cannot: with
    any armament on the grid `weapons_held` is not empty, and `weapon` is read
    only in the branch where it is (`model.compute`). Both are filled from the
    same grid, so no window state puts them in that combination and no
    comparison of builds can tell whether `weapon` was passed at all.

    So this case reads the call rather than its result. It is the cheap half
    of QA-100's proposal and the only half that reaches the seventh argument.
    Recording rather than replacing: the real `compute` still runs, so a
    context this test builds wrongly fails loudly here instead of passing on
    a build nobody looked at.
    """
    hero = cases.hero_by_name(game_data, "Wylder")
    reference = advisor.scaling_armament(game_data, hero)
    declarable = advisor.a_gated_attribute_effect(game_data, hero)
    ctx = advisor.context(game_data, hero, reference=reference,
                          armament_effect_ids=(declarable,),
                          declared=((declarable, 2),))
    problem = advisor.problem([advisor.RED])
    seen: dict = {}
    real = model.compute

    def recording(hero_arg, level, effects, curves=None, **kwargs):
        seen.update(hero=hero_arg, level=level, effects=effects,
                    curves=curves, **kwargs)
        return real(hero_arg, level, effects, curves, **kwargs)

    monkeypatch.setattr(model, "compute", recording)
    evaluate(problem, (), ctx)

    assert seen["hero"] is ctx.hero
    assert seen["level"] == ctx.level
    assert seen["curves"] == game_data["curves"]
    assert seen["weapon"] is ctx.reference.weapon, (
        "the reference armament did not reach the model; no build comparison "
        "can see this, which is why it is asserted here")
    assert seen["weapons_held"] == list(ctx.weapons_held)
    assert seen["declared"] == dict(ctx.declared)
    assert [int(effect["id"]) for effect in seen["effects"]] == [declarable], (
        "the armament's own rolls have to reach the model as effects")


def test_a_curse_reaches_the_advisor_as_an_ordinary_effect(planner,
                                                           game_data):
    """AD-015: there is no second reckoning for a curse.

    The window counts a curse into the same `model.compute` call as the good
    rolls, and it has to, or a Deep of Night build's sheet is quietly wrong.
    The advisor inherits that by holding the curses of a held relic in the
    same list -- so a cursed relic on screen and the same cursed relic held
    produce one set of numbers, not two.

    A copy without a gated roll, because the two sides disagree on gates by
    design: the advisor's baseline counts a conditional effect (A18), the
    sheet counts it only while its switch is on. On the frozen slot the first
    cursed Deep copy carries `Madness in Vicinity Improves Attack Power +1`,
    and the case would then be about A18 rather than about the curse.
    """
    if planner.owned is None:
        pytest.skip("this machine has no save, so no relic can be equipped")

    def ungated(item) -> bool:
        return not any(
            model.is_conditional(game_data["effects"][str(effect_id)], None)
            for effect_id in [*item.effect_ids, *item.curse_ids])

    planner.deep_check.setChecked(True)
    cursed = None
    for slot in planner.deep_slots:
        for item in relic_helpers.offered(slot):
            if item.curse_ids and ungated(item):
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


def test_each_source_of_an_effect_reaches_the_model_exactly_once(game_data):
    """A4's stacking clause where the advisor meets the model: **how often**.

    `model.compute` refuses to count an `isStrongestEffect` twice, but only
    over the list it is handed, and `effect_ids_of` is what hands it that
    list. Nothing said how many times a chosen copy may put its effects into
    it. Adding a second `ids.extend(candidate.effect_ids)` therefore raised
    `physicsAttackRate` from 1.1200 to 1.2544 and `max_damage` by 2.6 % --
    and the whole suite stayed green (QA-181).

    The expectation is a multiset built here out of the three inputs, the
    problem, the assignment and the context, and never out of the list the
    function returns. The cases already in this file cannot see it: they ask
    **which** sources arrive and in what order, never how often, and the
    comparison against the window compares two builds, which a doubling on
    both sides would move alike.
    """
    from collections import Counter

    hero = cases.hero_by_name(game_data, "Wylder")
    inventory = advisor.make_inventory(game_data, hero, count=3)
    kept, first, second = inventory.relics[:3]
    on_the_armament = advisor.a_gated_attribute_effect(game_data, hero)
    problem = advisor.problem([advisor.RED, advisor.RED, advisor.RED],
                              held={0: advisor.held_relic(kept)})
    ctx = advisor.context(game_data, hero,
                          armament_effect_ids=(on_the_armament,))
    assignment = (model_candidate(first, slot_index=1),
                  model_candidate(second, slot_index=2))

    expected: Counter[int] = Counter()
    for relic in (kept, first, second):
        expected.update(relic.effect_ids)
        expected.update(relic.curse_ids)
    expected.update(ctx.armament_effect_ids)

    assert (kept.effect_ids and first.effect_ids and second.effect_ids
            and ctx.armament_effect_ids), (
        "one of the four sources carries nothing, so a doubled list would "
        "not be visible at it")
    assert Counter(evaluate_module.effect_ids_of(
        problem, assignment, ctx)) == expected


def test_a_declared_conditional_reaches_the_build(game_data):
    """A gated effect counts exactly as often as the player says it is live.

    The advisor has to inherit the declaration or it would rank a situational
    relic at nothing while the sheet beside it counts it three times.
    """
    hero = cases.hero_by_name(game_data, "Wylder")
    declarable = advisor.a_gated_attribute_effect(game_data, hero)
    problem = advisor.problem([advisor.RED])

    silent = evaluate(problem, (), advisor.context(
        game_data, hero, armament_effect_ids=(declarable,)))
    declared = evaluate(problem, (), advisor.context(
        game_data, hero, armament_effect_ids=(declarable,),
        declared=((declarable, 1),)))

    assert declared.attributes != silent.attributes


def test_without_the_prose_every_number_is_the_same_bit_for_bit(game_data):
    """`want_qualitative=False` may drop the two text lists and nothing else.

    The beam scores through this switch (T-267), so a number it moved would
    be a ranking the window's stat sheet -- computed with the prose -- could
    not reproduce. Compared on a build that does carry prose, or an empty
    list on both sides would prove the switch was never reached.
    """
    hero = cases.hero_by_name(game_data, "Wylder")
    declarable = advisor.a_declarable_effect(game_data, hero)
    problem = advisor.problem([advisor.RED])
    ctx = advisor.context(game_data, hero, armament_effect_ids=(declarable,))

    told = evaluate(problem, (), ctx)
    silent = evaluate(problem, (), ctx, want_qualitative=False)

    assert told.qualitative and told.situational, (
        "the build carries no prose, so the comparison would see nothing")
    assert silent.qualitative == [] and silent.situational == []
    assert dataclasses.replace(silent, qualitative=told.qualitative,
                               situational=told.situational) == told


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


def test_an_excluded_id_is_struck_before_the_model_sees_it(monkeypatch,
                                                           game_data):
    """`GOAL.md` A18, AD-036.2: an excluded effect reaches no calculation.

    Struck in `effect_ids_of`, the one road every source takes -- held
    relic, chosen copy, curse -- so the case excludes one id from each of
    the three and reads the call to `model.compute` itself: a build
    comparison would show the total, not whether the id was ever asked.
    Kills the `MUTATIONS` entry `exclusion-ignored` (AD-033).
    """
    hero = cases.hero_by_name(game_data, "Wylder")
    inventory = advisor.make_inventory(game_data, hero, count=2)
    held, chosen = inventory.relics
    curse = advisor.a_curse_of_this_dataset(game_data)
    chosen = dataclasses.replace(chosen, curse_ids=[curse])
    kept = (held.effect_ids[0], chosen.effect_ids[0], curse)
    problem = advisor.problem([advisor.RED, advisor.RED],
                              held={0: advisor.held_relic(held)})
    struck = dataclasses.replace(problem, excluded=frozenset(kept))
    ctx = advisor.context(game_data, hero)
    assignment = (model_candidate(chosen, 1),)
    seen: list[list[int]] = []
    real = model.compute

    def recording(hero_arg, level, effects, curves=None, **kwargs):
        seen.append([int(effect["id"]) for effect in effects])
        return real(hero_arg, level, effects, curves, **kwargs)

    monkeypatch.setattr(model, "compute", recording)

    assert set(kept) <= set(evaluate_module.effect_ids_of(problem,
                                                          assignment, ctx))
    assert evaluate_module.effect_ids_of(struck, assignment, ctx) == ()
    evaluate(struck, assignment, ctx)
    assert seen == [[]], "an excluded id reached `model.compute`"
    assert figures(evaluate(struck, assignment, ctx)) == \
        figures(evaluate(advisor.problem([advisor.RED, advisor.RED]),
                         (), ctx)), (
        "three excluded ids and nothing else is the empty build")


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
