"""One question answered whole, and the memo of the answer.

Three claims carry this file.

* **The answer is one run's own.** Every figure in an `AdvisorResult` comes
  out of the run that produced it: the gain is worked out here from the base
  state and the built one, never read back out of the module under test, and
  every suggestion of the beam carries its reasons rather than only the head
  of the list.
* **A hit is a speed-up, never a second way to compute** (AD-007). What comes
  out of the cache is held against a **fresh** run of the same question, over
  every direction the registry holds and both Deep settings, and the
  denominator is asserted -- a case that silently covered one combination
  would say nothing about the others.
* **The key describes the run.** A question that differs in anything the run
  reads is a different key, and a request whose fields disagree with the
  material handed in beside them is refused before it can be stored under a
  key it does not stand for.

The material is made rather than read, for the reason `advisor_cases` gives:
a held slot, a Deep vessel and two directions have to be *stated*, or a green
run means only that this save happens to be arranged conveniently.
"""

from __future__ import annotations

import dataclasses

import pytest

from nrplanner import model
from nrplanner.advisor import explain, goals, run, search, types
from nrplanner.advisor.evaluate import evaluate

from tests import advisor_cases as advisor
from tests import weapon_damage_cases as cases

DAMAGE = "max_damage"
SURVIVAL = "min_damage_taken"
ATTRIBUTES = "max_attributes"


@pytest.fixture(scope="module")
def wylder(game_data):
    return cases.hero_by_name(game_data, "Wylder")


class Counter:
    """A cancel check that counts, and stops after so many questions."""

    def __init__(self, stop_at: int | None = None) -> None:
        self.asked = 0
        self.stop_at = stop_at

    def __call__(self) -> bool:
        self.asked += 1
        return self.stop_at is not None and self.asked > self.stop_at


# -- the answer -------------------------------------------------------------

def test_the_run_answers_with_every_field_the_result_promises(game_data,
                                                              wylder):
    """AD-010's mandatory content, over one real run.

    The one field deliberately left empty is `budget_note`: the sentence that
    would go in it is the `ui-ux-designer`'s and does not exist, and a run
    that invented one would put words on the screen nobody decided on.
    """
    inventory, problem, ctx, request = advisor.a_question(game_data, wylder)

    result = run.run(request, inventory, ctx, goals.GOALS)

    assert result.goal_id == DAMAGE
    assert result.goal_label == goals.GOALS[DAMAGE].label
    assert result.suggestions, "nothing was suggested, so nothing is checked"
    assert {line.goal_id for line in result.baseline} == set(goals.GOALS)
    assert {line.goal_id for line in result.gain} == set(goals.GOALS)
    assert result.data_note
    assert result.generation == request.generation
    assert result.budget_note == ""


def test_the_gain_is_the_difference_to_the_build_as_it_stands(game_data,
                                                              wylder):
    """AD-014 point 6: the ranking figure is absolute, the gain is the news.

    Both halves are worked out here out of `evaluate` and the registry, so
    the case would not follow the module into a wrong reference point -- the
    empty build instead of the held one is exactly the mistake AD-014.6
    corrects, and it looks plausible from the inside.
    """
    kept = advisor.make_inventory(game_data, wylder, count=4)
    held = advisor.held_relic(kept.relics_for(advisor.RED, False)[0])
    inventory, problem, ctx, request = advisor.a_question(
        game_data, wylder, colours=(advisor.RED, advisor.RED), held={0: held})

    result = run.run(request, inventory, ctx, goals.GOALS)

    base = evaluate(problem, (), ctx)
    built = evaluate(problem, _chosen(result, inventory, problem, ctx), ctx)
    given = {line.goal_id: line.gain for line in result.gain}

    assert set(given) == set(goals.GOALS)
    for goal_id, goal in goals.GOALS.items():
        assert given[goal_id] == (goal.score(built, ctx).value
                                  - goal.score(base, ctx).value)
    assert given[DAMAGE] != 0.0, (
        "the suggestion is worth exactly what the held build is worth, so a "
        "gain measured against the empty build would look the same here")
    assert result.held == problem.held


def test_a_chosen_type_the_build_carries_none_of_earns_no_suggestion(
        game_data, wylder):
    """QA-290: a candidate that leaves the ranked figure exactly where the
    base state left it is not a suggestion, once a damage type is chosen.

    Wylder's own starting armament deals no fire at all, so under
    `damage_type="Fire"` the base state and every candidate score 0.00
    alike -- the same zero `_max_damage`'s comment calls "a ranking and not
    a fault" (AK-335). Before this fix the beam filled the three free slots anyway
    (AD-014.7 fills every slot it can) and the bar said `SUGGESTED` over a
    build that changed nothing (director, 2026-09-20); the picker already
    read the same zero correctly (`relicpicker.top_handles`).
    """
    from nrplanner import damage
    from nrplanner.advisor import candidates

    reference = types.ReferenceArmament(
        weapon=next(w for w in game_data["weapons"]
                    if w["id"] == wylder["starting_weapon"]),
        tier=1, slot_index=damage.STARTING_SLOT)
    owned = advisor.make_inventory(game_data, wylder, count=4)
    slot_problem = advisor.problem([advisor.RED, advisor.RED, advisor.RED])
    ctx = dataclasses.replace(
        advisor.context(game_data, wylder, reference=reference),
        damage_type="Fire")
    frozen = run.frozen_inventory(owned, slot_problem)
    request = dataclasses.replace(
        advisor.request_for(slot_problem, ctx, frozen), damage_type="Fire")

    pool = candidates.pool(frozen, slot_problem, 0, ctx, goals.GOALS,
                           request.goal_id)
    assert pool.candidates, ("nothing owned reaches slot 0, so this proves "
                             "nothing about a real pool")
    assert all(types.marginal_for(candidate, DAMAGE) == 0.0
              for candidate in pool.candidates), (
        "some candidate does move the fire figure here, so this is not "
        "QA-290's all-zero case")

    result = run.run(request, frozen, ctx, goals.GOALS)

    assert result.suggestions == (), (
        "every candidate leaves the chosen type at the base state's figure, "
        "so nothing here is a suggestion")
    assert result.held == ()


NO_CARRIER_SENTENCE = (
    "Nothing you own reaches fire damage with Sorceries here: "
    "the armament it is ranked on does not carry it — for a spell the "
    "staff or seal on the selected tile, for a weapon art the armament on "
    "it, and the starting one where the tile has none; otherwise "
    "the starting armament — and nothing in your inventory swaps in a spell "
    "or weapon art that does.")


def _recluse_sorceries(game_data, damage_type, hit_with=None, favourite=False):
    """Recluse under `Sorceries` x `damage_type`, owning four relics that
    each raise magic damage and nothing else a sorcery could use.

    `hit_with=""` leaves the art unchosen, so the type is the only choice.
    `favourite` marks their effect as a `Favourite`."""
    from nrplanner import damage, model

    if hit_with is None:
        hit_with = model.SORCERIES_ART

    recluse = cases.hero_by_name(game_data, "Recluse")
    magic = cases.effects_raising_rate(game_data, recluse, "magicAttackRate",
                                       1)
    reference = types.ReferenceArmament(
        weapon=next(w for w in game_data["weapons"]
                    if w["id"] == recluse["starting_weapon"]),
        tier=1, slot_index=damage.STARTING_SLOT)
    owned = advisor.make_inventory(game_data, recluse, count=4, rolls=[magic])
    slot_problem = dataclasses.replace(
        advisor.problem([advisor.RED, advisor.RED, advisor.RED]),
        required=frozenset(magic if favourite else ()))
    ctx = dataclasses.replace(
        advisor.context(game_data, recluse, reference=reference),
        hit_with=hit_with, damage_type=damage_type)
    frozen = run.frozen_inventory(owned, slot_problem)
    request = dataclasses.replace(
        advisor.request_for(slot_problem, ctx, frozen),
        hit_with=hit_with, damage_type=damage_type)
    return run.run(request, frozen, ctx, goals.GOALS)


def test_a_chosen_kind_nothing_owned_reaches_says_so(game_data):
    """AK-365 (QA-294): Recluse x Sorceries x Fire. Glintstone Pebble deals
    no fire and no owned relic swaps in a spell that does, so QA-290 drops
    every suggestion -- and the result now names that cause for the status
    line and the `Why` dialog instead of leaving the bare 4.11 clause."""
    result = _recluse_sorceries(game_data, "Fire")

    assert result.suggestions == ()
    assert result.no_carrier_for == "fire damage with Sorceries"
    assert NO_CARRIER_SENTENCE in result.unknowns


def test_a_dropped_suggestion_leaves_no_favourite_left_out(game_data):
    """AD-057.4: under AK-365 the whole suggestion falls and that one sentence
    says why. A favourite was not what kept it out, so none is named."""
    result = _recluse_sorceries(game_data, "Fire", favourite=True)

    assert result.suggestions == ()
    assert result.no_carrier_for
    assert result.required_left_out == ()


def test_a_chosen_type_alone_keeps_its_label(game_data):
    """AK-365 wording, decision 22.09.2026 22:45: only with a type **and** an
    art chosen does the cause take the DR-038 form; `Fire` alone, which the
    starting armament does not deal, stays "fire"."""
    result = _recluse_sorceries(game_data, "Fire", hit_with="")

    assert result.suggestions == ()
    assert result.no_carrier_for == "fire"


def test_a_chosen_kind_something_owned_reaches_says_nothing_of_it(game_data):
    """The other half of AK-365: under `Magic` the Pebble carries the type
    and the owned relics move it, so there is a suggestion and neither
    sentence appears."""
    result = _recluse_sorceries(game_data, "Magic")

    assert result.suggestions
    assert result.no_carrier_for == ""
    assert NO_CARRIER_SENTENCE not in result.unknowns


def test_an_excluded_effect_takes_its_carrier_out_of_the_whole_run(
        monkeypatch, game_data, wylder):
    """`GOAL.md` A18 (06.11.2026), the Qt-free proof: exclude the effect one
    copy lives on, and the whole run -- pre-sort, beam, base, reasons -- is
    the run over an inventory **without that copy**: same copies, same order,
    same figures. Read at `model.compute`, the one place every figure of the
    run is formed. With an empty exclusion the run is the baseline run.
    """
    from nrplanner import inventory, model

    rolls = advisor.raising_effects(game_data, wylder, 5)
    struck_out = rolls[0][0]
    owned = advisor.make_inventory(game_data, wylder, count=4, rolls=rolls)
    carrier = owned.relics[0].handle
    bare = inventory.Inventory(source="test", relics=owned.relics[1:])
    problem = advisor.problem([advisor.RED, advisor.RED])
    excluding = dataclasses.replace(problem,
                                    excluded=frozenset({struck_out}))
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))

    def a_run(question, inventory):
        frozen = run.frozen_inventory(inventory, question)
        return run.run(advisor.request_for(question, ctx, frozen), frozen,
                       ctx, goals.GOALS)

    baseline = a_run(problem, owned)
    seen: list[int] = []
    real = model.compute

    def recording(hero_arg, level, effects, curves=None, **kwargs):
        seen.extend(int(effect["id"]) for effect in effects)
        return real(hero_arg, level, effects, curves, **kwargs)

    monkeypatch.setattr(model, "compute", recording)
    excluded = a_run(excluding, owned)
    monkeypatch.setattr(model, "compute", real)

    assert struck_out not in seen, (
        "the excluded id reached a calculation of the run")
    assert _ranking(excluded) == _ranking(a_run(problem, bare))
    assert _ranking(excluded) != _ranking(baseline), (
        "the excluded effect decided nothing, so this inventory cannot show "
        "the exclusion")
    assert _ranking(a_run(dataclasses.replace(problem,
                                              excluded=frozenset()),
                          owned)) == _ranking(baseline)
    assert not any(carrier == choice.handle
                   for suggestion in excluded.suggestions
                   for choice in suggestion.choices)


def test_avoid_beats_a_favourite_on_the_one_copy_that_carries_both(game_data,
                                                                   wylder):
    """A18 against A19 on one relic: the only carrier of a favourited effect
    also carries an avoided one. "Never suggested" holds whatever else it
    carries, so no suggestion names that copy."""
    rolls = advisor.raising_effects(game_data, wylder, 5)
    wanted, avoided = rolls[0][0], rolls[4][0]
    owned = advisor.make_inventory(game_data, wylder, count=4, rolls=rolls)
    carrier = owned.relics[0]
    carrier.effect_ids = [wanted, avoided]
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))
    question = dataclasses.replace(
        advisor.problem([advisor.RED, advisor.RED]),
        excluded=frozenset({avoided}), required=frozenset({wanted}))
    frozen = run.frozen_inventory(owned, question)

    result = run.run(advisor.request_for(question, ctx, frozen), frozen, ctx,
                     goals.GOALS)

    assert not any(choice.handle == carrier.handle
                   for suggestion in result.suggestions
                   for choice in suggestion.choices)


def test_a_required_effect_no_copy_carries_is_said_by_name(game_data, wylder):
    """A19/A7 through `run.run`, AK-281's sentence: the suggestion fills what
    it can (A28, AD-058.1), and the answer says which effect no owned copy
    carries -- and, with a carrier for each but no constellation for the free
    slots, that no combination does. Decided on the pools, so the sentence is
    about what is owned.
    """
    rolls = advisor.raising_effects(game_data, wylder, 5)
    nobody_carries = rolls[4][0]
    owned = advisor.make_inventory(game_data, wylder, count=4, rolls=rolls)
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))

    def a_run(question):
        frozen = run.frozen_inventory(owned, question)
        return run.run(advisor.request_for(question, ctx, frozen), frozen,
                       ctx, goals.GOALS)

    def name(effect_id):
        return " ".join(game_data["effects"][str(effect_id)]["name"].split())

    problem = advisor.problem([advisor.RED, advisor.RED])
    result = a_run(dataclasses.replace(
        problem, required=frozenset({nobody_carries, rolls[0][0]})))
    assert len(result.suggestions[0].choices) == 2
    assert all(owned.relics[0].handle in {c.handle for c in s.choices}
               for s in result.suggestions), (
        "the favourite that can be met went missing with the one that cannot")
    assert result.unknowns[-1] == (
        f"No copy you own carries “{name(nobody_carries)}”, which you "
        f"favourited — no suggestion can meet that.")
    assert result.required_left_out == (nobody_carries,)

    one_slot = advisor.problem([advisor.RED])
    result = a_run(dataclasses.replace(
        one_slot, required=frozenset({rolls[0][0], rolls[1][0]})))
    assert len(result.suggestions[0].choices) == 1
    left_out, = result.required_left_out
    assert left_out in {rolls[0][0], rolls[1][0]}
    assert result.unknowns[-1] == (
        f"Your copies can carry “{name(left_out)}”, which you favourited, "
        f"but not together with the favourites this suggestion already meets.")

    met = a_run(dataclasses.replace(problem,
                                    required=frozenset({rolls[0][0]})))
    assert met.suggestions and all(
        owned.relics[0].handle in {c.handle for c in s.choices}
        for s in met.suggestions)
    assert not any("required" in line for line in met.unknowns)
    assert met.required_left_out == ()


def test_the_search_falls_back_when_the_budget_misses_a_carrier(monkeypatch,
                                                                game_data,
                                                                wylder):
    """AD-058.4, "never blocks" against the K limit of the forced branches:
    with the beam empty under the attainable favourites, the free search
    answers, and what the suggestion then lacks is named."""
    from nrplanner.advisor import candidates

    owned = advisor.make_inventory(game_data, wylder, count=4)
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))
    free = advisor.problem([advisor.RED])
    weakest = candidates.pool(owned, free, 0, ctx, goals.GOALS,
                              DAMAGE).candidates[-1]
    wanted = weakest.effect_ids[0]
    question = dataclasses.replace(free, required=frozenset({wanted}))
    frozen = run.frozen_inventory(owned, question)
    real = search.beam
    asked = []

    def misses_the_carrier(problem, *args, **kwargs):
        asked.append(problem.required)
        return () if problem.required else real(problem, *args, **kwargs)

    monkeypatch.setattr(search, "beam", misses_the_carrier)
    result = run.run(advisor.request_for(question, ctx, frozen), frozen, ctx,
                     goals.GOALS)

    assert asked == [frozenset({wanted}), frozenset()]
    assert result.suggestions[0].choices[0].handle != weakest.handle
    assert result.required_left_out == (wanted,)


def test_a_required_effect_a_held_relic_carries_is_said_to_be_there(
        game_data, wylder):
    """T-288: two favourited effects, one already on the relic the player
    holds. The search rightly adds no second carrier for it, so without a
    sentence the answer shows one favourite and says nothing about the
    other -- the player read that as the second one dropped. The answer
    names the held relic and its slot; the free slots still carry the
    other favourite.
    """
    rolls = advisor.raising_effects(game_data, wylder, 4)
    owned = advisor.make_inventory(game_data, wylder, count=4, rolls=rolls)
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))
    holding, wanted = owned.relics[0], owned.relics[1]
    on_the_hold, in_the_open = rolls[0][0], rolls[1][0]
    problem = dataclasses.replace(
        advisor.problem([advisor.RED, advisor.RED],
                        held={0: advisor.held_relic(holding)}),
        required=frozenset({on_the_hold, in_the_open}))
    frozen = run.frozen_inventory(owned, problem)
    result = run.run(advisor.request_for(problem, ctx, frozen), frozen,
                     ctx, goals.GOALS)

    def name(effect_id):
        return " ".join(game_data["effects"][str(effect_id)]["name"].split())

    assert result.suggestions and all(
        {choice.handle for choice in suggestion.choices} == {wanted.handle}
        for suggestion in result.suggestions)
    assert (f"{name(on_the_hold)}, which you favourited, is carried by "
            f"{holding.name} held in Slot 1.") in result.unknowns
    assert not any(name(in_the_open) in line for line in result.unknowns)
    assert result.required_left_out == ()
    # AK-314.1: the card's own line is the same single sentence, unabridged.
    assert result.favourites_met_line == (
        f"{name(on_the_hold)}, which you favourited, is carried by "
        f"{holding.name} held in Slot 1.")


def test_two_favourites_met_by_a_hold_summarise_on_the_card(game_data,
                                                             wylder):
    """AK-314.2: two favourited effects each on a held relic still list two
    full sentences in `unknowns`/the `Why` dialog, but the card's own line
    (`favourites_met_line`) collapses them to a count -- mutation-killing
    against an implementation that keeps naming both on the card.
    """
    rolls = advisor.raising_effects(game_data, wylder, 5)
    owned = advisor.make_inventory(game_data, wylder, count=5, rolls=rolls)
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))
    holding_a, holding_b = owned.relics[0], owned.relics[1]
    effect_a, effect_b, in_the_open = rolls[0][0], rolls[1][0], rolls[2][0]
    problem = dataclasses.replace(
        advisor.problem([advisor.RED, advisor.RED, advisor.RED],
                        held={0: advisor.held_relic(holding_a),
                              1: advisor.held_relic(holding_b)}),
        required=frozenset({effect_a, effect_b, in_the_open}))
    frozen = run.frozen_inventory(owned, problem)
    result = run.run(advisor.request_for(problem, ctx, frozen), frozen,
                     ctx, goals.GOALS)

    assert result.favourites_met_line == (
        "2 favourited effects are already carried by relics you hold.")
    assert sum(1 for line in result.unknowns if "held in Slot" in line) == 2


def test_a_required_effect_owned_only_deep_says_so_when_deep_is_off(
        game_data, wylder):
    """QA-273's Vermerk to AK-281: two owned copies carry the required
    effect, but both are Deep of Night relics and this vessel has no Deep
    slot in play, so no pool can offer either -- the sentence must say the
    copies are owned and name the reason, not claim none exists.
    """
    rolls = advisor.raising_effects(game_data, wylder, 5)
    deep_effect = rolls[4][0]
    owned = advisor.make_inventory(game_data, wylder, count=4, deep_count=2,
                                   rolls=rolls[:4] + [rolls[4], rolls[4]])
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))

    def name(effect_id):
        return " ".join(game_data["effects"][str(effect_id)]["name"].split())

    question = dataclasses.replace(
        advisor.problem([advisor.RED, advisor.RED]),
        required=frozenset({deep_effect}))
    frozen = run.frozen_inventory(owned, question)
    result = run.run(advisor.request_for(question, ctx, frozen), frozen,
                     ctx, goals.GOALS)

    assert len(result.suggestions[0].choices) == 2
    assert result.unknowns[-1] == (
        f"You own 2 copies carrying “{name(deep_effect)}”, but none fits the "
        f"open slots (Deep of Night is off).")
    assert result.required_left_out == (deep_effect,)


def _ranking(result) -> list[tuple[tuple[int, ...], float]]:
    return [(tuple(choice.handle for choice in suggestion.choices),
             suggestion.score.value) for suggestion in result.suggestions]


def _chosen(result, inventory, problem, ctx):
    """The copies the best suggestion names, looked up by handle.

    Out of the inventory rather than out of the run's own pools, so what the
    figures above are recomputed from is the save and not the module's
    bookkeeping.
    """
    from nrplanner.advisor import candidates

    pools = candidates.pools(inventory, problem, ctx, goals.GOALS,
                             result.goal_id)
    from nrplanner.advisor import explain

    return explain.chosen_for(result.suggestions[0], pools)


def test_every_suggestion_carries_its_reasons_and_not_only_the_first(
        game_data, wylder):
    """A beam whose head is explained and whose tail is not is one shape with
    two meanings, and the window may draw any of them.
    """
    inventory, problem, ctx, request = advisor.a_question(game_data, wylder)

    result = run.run(request, inventory, ctx, goals.GOALS)

    assert len(result.suggestions) > 1, (
        "one suggestion cannot tell the head of a list from its tail")
    for suggestion in result.suggestions:
        assert len(suggestion.reasons) == len(suggestion.choices), (
            f"{len(suggestion.reasons)} slot groups for "
            f"{len(suggestion.choices)} filled slots")


def test_the_beam_builds_no_prose_and_every_explained_suggestion_does(
        monkeypatch, game_data, wylder):
    """The text of a build is written once per build somebody reads (T-267).

    The beam evaluates thousands of assignments and reads a score off each;
    the window reads `Build.qualitative`/`situational` off the base state and
    the explained suggestions only. A beam that builds prose is the whole
    regression T-265d measured; an explained suggestion without it is a card
    with an empty Conditional line. The question carries no curse, so no
    second evaluation per suggestion (`explain._unfelt`) is in the count.
    """
    from nrplanner import model

    inventory, problem, ctx, request = advisor.a_question(game_data, wylder)
    prose_calls = 0
    real_qualitative = model.compute_qualitative
    real_beam = search.beam
    around_the_beam: list[int] = []

    def counting(*args, **kwargs):
        nonlocal prose_calls
        prose_calls += 1
        return real_qualitative(*args, **kwargs)

    def watched_beam(*args, **kwargs):
        around_the_beam.append(prose_calls)
        found = real_beam(*args, **kwargs)
        around_the_beam.append(prose_calls)
        return found

    monkeypatch.setattr(model, "compute_qualitative", counting)
    monkeypatch.setattr(search, "beam", watched_beam)
    result = run.run(request, inventory, ctx, goals.GOALS)

    assert result.suggestions
    before, after = around_the_beam
    assert after == before, f"the beam built prose {after - before} times"
    assert prose_calls - after == 1 + len(result.suggestions), (
        "after the beam, prose is built once for the base state and once "
        "per explained suggestion, nothing more and nothing less")


def test_the_singular_fields_belong_to_the_best_suggestion(game_data, wylder):
    """`Apply all` applies the first, so the curses named are the first's.

    Read off the inventory rather than off the result: the copies of the best
    suggestion are looked up by handle and their curse ids are what the
    dataset gives them names for.
    """
    inventory, problem, ctx, request = advisor.a_question(game_data, wylder, count=6)

    result = run.run(request, inventory, ctx, goals.GOALS)

    best = result.suggestions[0]
    filled = {choice.slot_index for choice in best.choices}
    drawn = {line.slot_index for group in best.reasons
             for line in group.lines}
    named = {line.slot_index for line in result.curses_without_a_figure}
    named |= {line.slot_index for line in result.effects_without_a_figure}

    assert drawn and drawn <= filled, (
        f"the best suggestion fills {sorted(filled)} and its lines speak "
        f"about {sorted(drawn)}")
    assert named <= filled, (
        "a silent line was reported for a slot the best suggestion does not "
        "fill")
    assert result.curses_without_a_figure + result.effects_without_a_figure         == tuple(line for group in best.reasons for line in group.lines
                 if line.silence != types.CARRIES_A_FIGURE
                 and line.is_curse) + tuple(
                     line for group in best.reasons for line in group.lines
                     if line.silence != types.CARRIES_A_FIGURE
                     and not line.is_curse), (
        "the two lists are meant to be the silent subset of the groups the "
        "result already carries, not a second reading of them")


# -- stopping ---------------------------------------------------------------

def whole_pre_sort(inventory, problem) -> int:
    """How many questions a pre-sort that runs to the end asks.

    Worked out from the snapshot rather than read back out of `candidates`:
    the pre-sort offers every relic `relics_for` answers with, once per free
    slot, so this is what the loop under test has to come to. A number taken
    from the loop itself would agree with it however wrong it was.
    """
    return sum(len(inventory.relics_for(slot.colour, slot.deep))
               for slot in types.free_slots(problem))


def test_a_run_stopped_inside_the_pre_sort_says_so(game_data, wylder):
    """The first question is asked before the first candidate is measured.

    The pre-sort used to be left whole, on the measurement that it is 43 ms
    of a 960 ms run on the worst *real* case (`scripts/measure_advisor_search
    .py`). That held only while the number of relics came from a save the
    player wrote: a prepared file makes the pre-sort the entire run
    (SEC-022), and a run that cannot be stopped there cannot be stopped at
    all -- which is what `UI_SPEC` AK-11 asks for within 200 ms.
    """
    inventory, problem, ctx, request = advisor.a_question(game_data, wylder)

    with pytest.raises(search.Cancelled,
                       match="during the pre-sort of slot 0, after 0"):
        run.run(request, inventory, ctx, goals.GOALS, Counter(stop_at=0))


def test_a_run_stopped_between_the_pre_sort_and_the_search_says_so(game_data,
                                                                   wylder):
    """The check between the two steps is still there and still its own.

    Stopped one question after the last relic of the last pool, so the
    pre-sort finishes and the next answer is the one taken between the
    steps. Without that check the same question would be the search's first
    and would name a slot level instead.
    """
    inventory, problem, ctx, request = advisor.a_question(game_data, wylder)

    with pytest.raises(search.Cancelled,
                       match="after the pre-sort, before the search"):
        run.run(request, inventory, ctx, goals.GOALS,
                Counter(stop_at=whole_pre_sort(inventory, problem)))


def test_a_run_asks_once_per_offered_relic_and_once_per_level(game_data,
                                                              wylder):
    """The questions are asked, and asked in the places that were costed.

    Counted rather than watched: a check that ran only inside the search
    would leave the pre-sort uninterruptible without any case going red, and
    the pre-sort is where a hostile inventory spends the run (SEC-022). One
    question per offered relic is the finest grain the loop has -- the unit
    of work is one `evaluate` -- and it is affordable there: the check the
    window carries costs 0,077 us against the 175,6 us one offered relic
    costs, 0,04 % of the pre-sort (`scripts/measure_advisor_cancel.py`,
    this machine, 2026-09-07).
    """
    inventory, problem, ctx, request = advisor.a_question(game_data, wylder)
    watch = Counter()

    run.run(request, inventory, ctx, goals.GOALS, watch)

    free = len(types.free_slots(problem))
    offered = whole_pre_sort(inventory, problem)
    assert watch.asked == offered + 1 + free, (
        f"one question per offered relic over the free slots ({offered}), "
        f"one between the pre-sort and the search, and one before each of "
        f"the {free} levels is {offered + 1 + free}; this run asked "
        f"{watch.asked} times")


def test_a_run_stopped_inside_the_search_says_so(game_data, wylder):
    """`search.Cancelled` travels out of the run unchanged.

    A truncated beam and a finished one are the same shape, so the run may
    not turn a stop into a short answer: `Stopped. Nothing was changed.` and
    a list of suggestions are two states of the window (`UI_SPEC` 4.5
    against 4.6).
    """
    inventory, problem, ctx, request = advisor.a_question(game_data, wylder)
    # The whole pre-sort, the question between the steps, and the first slot
    # level all answered "keep going"; the second level is the one stopped.
    before_the_second_level = whole_pre_sort(inventory, problem) + 2

    with pytest.raises(search.Cancelled, match="1 of 2 slots"):
        run.run(request, inventory, ctx, goals.GOALS,
                Counter(stop_at=before_the_second_level))


# -- the key describes the run ----------------------------------------------

@pytest.mark.parametrize("field, wrong", [
    ("hero_id", 999),
    ("level", 1),
    ("weighting_id", "invented"),
    ("reference_weapon_id", None),
    ("declared", ((1, 1),)),
    ("data_version", "another patch"),
    ("inventory_fingerprint", "another save"),
])
def test_a_request_that_describes_another_run_is_refused(game_data, wylder,
                                                         field, wrong):
    """Seven fields, seven ways for the key to stand for the wrong run.

    Each is refused **before** anything is computed, because the damage is
    not the run -- the run would be right -- but the answer being stored
    under a key that means something else. The next question with those
    fields right would then hit it.
    """
    inventory, problem, ctx, request = advisor.a_question(game_data, wylder)
    lying = dataclasses.replace(request, **{field: wrong})

    with pytest.raises(ValueError, match=field.split()[0]):
        run.run(lying, inventory, ctx, goals.GOALS)


def test_a_request_that_names_an_unknown_direction_is_refused(game_data,
                                                              wylder):
    inventory, problem, ctx, request = advisor.a_question(game_data, wylder)

    with pytest.raises(KeyError, match="invented"):
        run.run(dataclasses.replace(request, goal_id="invented"), inventory,
                ctx, goals.GOALS)


# -- the snapshot that crosses the thread boundary --------------------------

def test_the_snapshot_asks_the_inventory_what_fits_and_does_not_decide_it(
        game_data, wylder):
    """AD-006 point 8 without restating the colour rule.

    The rule that a white slot draws every colour lives in
    `inventory.relics_for`. The snapshot asks it once per slot in play and
    answers from what it was told; here the asking is recorded, so a snapshot
    that had worked the answer out for itself would be visible.
    """
    inventory = advisor.make_inventory(game_data, wylder, count=4,
                                       other_colour=advisor.BLUE)
    problem = advisor.problem([advisor.WHITE, advisor.RED])
    asked = []

    class Recording:
        relics = inventory.relics

        def relics_for(self, colour, deep):
            asked.append((colour, deep))
            return inventory.relics_for(colour, deep)

    frozen = run.frozen_inventory(Recording(), problem)

    assert sorted(asked) == [(advisor.RED, False), (advisor.WHITE, False)]
    assert ([relic.handle for relic in frozen.relics_for(advisor.WHITE, False)]
            == [relic.handle
                for relic in inventory.relics_for(advisor.WHITE, False)])


def test_the_snapshot_refuses_a_slot_it_was_never_asked_about(game_data,
                                                              wylder):
    """A pair nobody precomputed is two questions mixed, not a poor save."""
    inventory = advisor.make_inventory(game_data, wylder, count=2)
    frozen = run.frozen_inventory(inventory, advisor.problem([advisor.RED]))

    with pytest.raises(KeyError, match="colour 1"):
        frozen.relics_for(advisor.BLUE, False)


def test_the_snapshot_holds_values_the_window_can_no_longer_change(game_data,
                                                                   wylder):
    """What crosses into the thread is frozen (AD-006 point 8)."""
    inventory = advisor.make_inventory(game_data, wylder, count=2)
    problem = advisor.problem([advisor.RED])
    frozen = run.frozen_inventory(inventory, problem)

    inventory.relics[0].effect_ids.append(4242)
    inventory.relics[0].name = "renamed after the snapshot"

    copy = frozen.relics_for(advisor.RED, False)[0]
    assert 4242 not in copy.effect_ids
    assert "renamed" not in copy.name
    with pytest.raises(dataclasses.FrozenInstanceError):
        copy.name = "renamed in the snapshot"


# -- the fingerprint --------------------------------------------------------

def test_the_fingerprint_changes_when_a_copy_gets_another_handle(game_data,
                                                                 wylder):
    """AD-007's own correction of 2026-09-01, and the reason for it.

    Handles are handed out again when a relic is melted down or the save is
    opened on another machine. The answer names copies **by handle**
    (AD-013), so a hit across a re-issue would name a copy that is somewhere
    else or nowhere -- exactly the recommendation the player cannot wear.
    """
    inventory = advisor.make_inventory(game_data, wylder, count=3)
    problem = advisor.problem([advisor.RED])
    before = run.inventory_fingerprint(run.frozen_inventory(inventory,
                                                            problem))

    inventory.relics[0].handle = 900

    after = run.inventory_fingerprint(run.frozen_inventory(inventory,
                                                           problem))
    assert before != after


def test_the_fingerprint_does_not_follow_the_order_the_save_read_them_in(
        game_data, wylder):
    """The same relics in another order are the same possessions.

    Without this the cache would miss on every rescan, which is a cost with
    nothing bought: the order a save is read in is not something the player
    changed.
    """
    inventory = advisor.make_inventory(game_data, wylder, count=4)
    problem = advisor.problem([advisor.RED])
    before = run.inventory_fingerprint(run.frozen_inventory(inventory,
                                                            problem))

    inventory.relics.reverse()

    assert run.inventory_fingerprint(
        run.frozen_inventory(inventory, problem)) == before


def test_a_copy_the_save_gives_no_handle_for_is_still_in_the_fingerprint(
        game_data, wylder):
    """`None` does not order against an int, and it is still possession.

    A copy with no handle is not offered (AD-013 point 4) but it is counted
    in the line that says so, so a save that gains one is a save that answers
    differently.
    """
    inventory = advisor.make_inventory(game_data, wylder, count=3,
                                       handles=[100, None, 102])
    problem = advisor.problem([advisor.RED])

    first = run.inventory_fingerprint(run.frozen_inventory(inventory,
                                                           problem))
    inventory.relics = list(reversed(inventory.relics))
    again = run.inventory_fingerprint(run.frozen_inventory(inventory,
                                                           problem))

    assert first == again
    assert len(first) == 64


# -- the cache --------------------------------------------------------------

@pytest.mark.parametrize("goal_id", [DAMAGE, SURVIVAL, ATTRIBUTES])
@pytest.mark.parametrize("deep", [False, True])
def test_a_hit_is_what_a_fresh_run_would_have_said(game_data, wylder,
                                                   goal_id, deep):
    """AD-007: the cache is a speed-up and not a second way to compute.

    Six combinations, and the denominator is the point: three directions
    times both Deep settings. Held against a **fresh** run of the same
    question rather than against the stored object, so the claim is that the
    cache does not answer differently from computing again -- which is also
    the claim that computing again answers the same way at all.
    """
    inventory, problem, ctx, request = advisor.a_question(
        game_data, wylder, colours=(advisor.RED, advisor.RED), deep=deep,
        goal_id=goal_id)
    cache = run.ResultCache()

    stored = run.run(request, inventory, ctx, goals.GOALS)
    cache.put(request, stored)
    fresh = run.run(request, inventory, ctx, goals.GOALS)
    hit = cache.get(request)

    assert hit is not None, "the question that was just stored missed"
    assert fresh.suggestions, (
        "this question has no answer, so two of them being alike says "
        "nothing")
    assert hit == fresh
    assert repr(hit) == repr(fresh), (
        "the two answers compare equal and read differently, which is a "
        "float that only one of them rounded")


def test_all_six_combinations_of_direction_and_deep_are_covered():
    """The denominator of the case above, so that dropping one is visible.

    It did its work when AD-032 added the third direction (T-191): the
    parametrization above went on covering two and this case said so.
    """
    combinations = [(goal_id, deep)
                    for goal_id in (DAMAGE, SURVIVAL, ATTRIBUTES)
                    for deep in (False, True)]

    assert len(combinations) == 6
    assert set(goals.GOALS) == {DAMAGE, SURVIVAL, ATTRIBUTES}, (
        f"the registry holds {sorted(goals.GOALS)}, so the case above no "
        f"longer covers every direction")


@pytest.mark.parametrize("change", [
    {"goal_id": SURVIVAL},
    {"level": 20},
    {"budget": types.Budget(candidates_per_slot=3, beam_width=3)},
    {"hero_id": 4242},
    {"weighting_id": "another weighting"},
    {"declared": ((7, 1),)},
    {"data_version": "the next patch"},
    {"inventory_fingerprint": "after melting one down"},
    {"reference_weapon_id": 4242},
])
def test_a_question_that_differs_in_anything_the_run_reads_misses(game_data,
                                                                  wylder,
                                                                  change):
    """Nine ways to ask something else, nine misses.

    The answer would be right for the question it was stored under and wrong
    for this one, and nothing downstream could tell: the result carries slot
    indices and handles, so a hit across a changed hold overwrites a slot the
    player deliberately kept (AD-016).
    """
    inventory, problem, ctx, request = advisor.a_question(game_data, wylder)
    cache = run.ResultCache()
    cache.put(request, run.run(request, inventory, ctx, goals.GOALS))

    assert cache.get(dataclasses.replace(request, **change)) is None
    assert cache.get(request) is not None, (
        "the question that was stored does not hit either, so the miss above "
        "says nothing about the key")


def test_a_question_that_differs_in_which_slot_is_held_misses(game_data,
                                                              wylder):
    """The held state is in the key through `problem`, in the vessel's order.

    Two questions that differ only in *which* slot a relic is held in are
    different questions: the answer carries slot indices, so a hit across the
    permutation would name the other question's slots (AD-016 point 2 as D3
    rewrote it).
    """
    kept = advisor.make_inventory(game_data, wylder, count=4)
    held = advisor.held_relic(kept.relics_for(advisor.RED, False)[0])
    inventory, problem, ctx, request = advisor.a_question(
        game_data, wylder, colours=(advisor.RED, advisor.RED),
        held={0: held})
    cache = run.ResultCache()
    cache.put(request, run.run(request, inventory, ctx, goals.GOALS))

    elsewhere = dataclasses.replace(
        problem, held=(types.HeldSlot(index=1, relic=held),))

    assert cache.get(dataclasses.replace(request, problem=elsewhere)) is None
    assert cache.get(request) is not None, (
        "the question that was stored no longer hits, so the miss above says "
        "nothing")


def test_the_generation_is_not_part_of_the_question(game_data, wylder):
    """AD-006 point 3 against AD-007: which asking, not what is asked.

    In the key it would make every question new and the cache dead, and no
    case that merely asked twice would notice -- the second answer would be
    right, only computed again.
    """
    inventory, problem, ctx, request = advisor.a_question(game_data, wylder,
                                                  generation=1)
    cache = run.ResultCache()
    cache.put(request, run.run(request, inventory, ctx, goals.GOALS))

    later = dataclasses.replace(request, generation=9)
    hit = cache.get(later)

    assert hit is not None
    assert hit.generation == 9, (
        "a hit that kept the generation of the run that produced it would be "
        "dropped as overtaken by the controller that had just fetched it")


def test_the_cache_keeps_the_last_answers_and_forgets_the_oldest(game_data,
                                                                 wylder):
    """AD-007's LRU, at a size a case can count.

    The size is a parameter here rather than 32, because a case that stored
    33 answers would be timing a full run 33 times to watch one eviction.
    """
    inventory, problem, ctx, request = advisor.a_question(game_data, wylder)
    answer = run.run(request, inventory, ctx, goals.GOALS)
    cache = run.ResultCache(size=2)

    for level in (1, 2, 3):
        cache.put(dataclasses.replace(request, level=level), answer)
    cache.get(dataclasses.replace(request, level=2))
    cache.put(dataclasses.replace(request, level=4), answer)

    kept = [level for level in (1, 2, 3, 4)
            if cache.get(dataclasses.replace(request, level=level))
            is not None]
    assert kept == [2, 4], (
        "the least recently *used* answer goes, not the least recently put")
    assert len(cache) == 2


def test_a_cache_that_can_never_hit_is_refused():
    """A size of zero is a second path through the code that is never a
    speed-up: every question would be computed and every answer thrown away,
    and the cache would still be there to go wrong.
    """
    with pytest.raises(ValueError, match="at least one"):
        run.ResultCache(size=0)


def test_a_slot_the_marks_emptied_says_why_through_the_run(game_data, wylder):
    """AD-057.4: one copy left for two slots, the others avoided. The answer
    names the empty slot and its reason, and the filled one is not in it."""
    rolls = advisor.raising_effects(game_data, wylder, 3)
    owned = advisor.make_inventory(game_data, wylder, count=3, rolls=rolls)
    avoided = {rolls[0][0], rolls[1][0]}
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))
    question = dataclasses.replace(advisor.problem([advisor.RED, advisor.RED]),
                                   excluded=frozenset(avoided))
    frozen = run.frozen_inventory(owned, question)

    result = run.run(advisor.request_for(question, ctx, frozen), frozen, ctx,
                     goals.GOALS)

    assert [choice.slot_index for choice in result.suggestions[0].choices] == [0]
    empty, = result.empty_slots
    assert empty.slot_index == 1
    assert empty.reason == types.EMPTY_NOTHING, (
        "the pool still offers the one copy, which slot 0 spent")


def test_a_dropped_suggestion_has_no_empty_slot_entries(game_data):
    """AD-057.4: AK-365 is the seventh reason, outside the list."""
    result = _recluse_sorceries(game_data, "Fire")

    assert result.no_carrier_for
    assert result.empty_slots == ()


# -- the star (A28, AD-059) --------------------------------------------------

def _starred(game_data, wylder, owned, colours, *, stars, **marks):
    """One run with these copies starred, and the question and frozen save."""
    held = marks.pop("held", None)
    question = dataclasses.replace(
        advisor.problem(colours, held=held), **marks,
        pinned=tuple(sorted(types.roll_of(copy) for copy in stars)))
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data, wylder))
    frozen = run.frozen_inventory(owned, question)
    result = run.run(advisor.request_for(question, ctx, frozen), frozen, ctx,
                     goals.GOALS)
    return result, question, ctx, frozen


def _weakest_copy(game_data, wylder, owned, colours):
    """A copy the plain search leaves out, so that only a star puts it in."""
    plain, *_ = _starred(game_data, wylder, owned, colours, stars=())
    named = {choice.handle for choice in plain.suggestions[0].choices}
    return next(copy for copy in reversed(owned.relics)
                if copy.handle not in named and copy.colour == colours[0])


def test_a_star_goes_in_although_the_search_would_not_take_it(game_data,
                                                              wylder):
    owned = advisor.make_inventory(game_data, wylder, count=4)
    colours = [advisor.RED, advisor.RED]
    star = _weakest_copy(game_data, wylder, owned, colours)

    result, *_ = _starred(game_data, wylder, owned, colours, stars=[star])

    best = result.suggestions[0]
    assert star.handle in {choice.handle for choice in best.choices}
    assert [choice.slot_index for choice in best.choices] == [0, 1]
    assert result.pins_placed == (0,)
    assert result.held == ()
    assert result.pins_left_out == ()


def test_the_gain_and_the_reasons_count_the_star(game_data, wylder):
    """Handing `searched` to the explanation would measure the star against a
    base state that already holds it: no gain, and no line for it."""
    owned = advisor.make_inventory(game_data, wylder, count=4)
    colours = [advisor.RED, advisor.RED]
    star = _weakest_copy(game_data, wylder, owned, colours)

    result, question, ctx, frozen = _starred(game_data, wylder, owned, colours,
                                             stars=[star])

    best = result.suggestions[0]
    by_handle = {copy.handle: copy for copy in frozen.relics}
    chosen = tuple(
        types.Candidate(choice.slot_index, choice.handle, choice.relic_id,
                        choice.name, advisor.RED, False,
                        by_handle[choice.handle].effect_ids,
                        by_handle[choice.handle].curse_ids)
        for choice in best.choices)
    goal = goals.GOALS[DAMAGE]
    base = evaluate(question, (), ctx, goal=goal)
    built = evaluate(question, chosen, ctx, goal=goal)
    gain = {line.goal_id: line.gain for line in result.gain}

    assert gain[DAMAGE] == (goal.score(built, ctx).value
                            - goal.score(base, ctx).value)
    assert best.score.value == goal.score(built, ctx).value
    group = next(group for group in best.reasons
                 if group.slot_index == result.pins_placed[0])
    assert group.relic_name == star.name
    assert any(line.silence == types.CARRIES_A_FIGURE for line in group.lines)


def test_a_slot_a_star_emptied_says_so(game_data, wylder):
    """`EMPTY_PIN` out of a real run: the one copy of the colour is laid, and
    the other slot has nothing left to be offered."""
    owned = advisor.make_inventory(game_data, wylder, count=1)
    star = owned.relics[0]

    result, *_ = _starred(game_data, wylder, owned,
                          [advisor.RED, advisor.RED], stars=[star])

    assert result.pins_placed == (0,)
    assert [(empty.slot_index, empty.reason, empty.relic_name)
            for empty in result.empty_slots] == [
        (1, types.EMPTY_PIN, star.name)]


def test_a_star_is_part_of_the_question(game_data, wylder):
    """A hit across two sets of stars would hand back the other build."""
    owned = advisor.make_inventory(game_data, wylder, count=2)
    plain = advisor.problem([advisor.RED])
    starred = dataclasses.replace(
        plain, pinned=(types.roll_of(owned.relics[0]),))
    ctx = advisor.context(game_data, wylder)
    frozen = run.frozen_inventory(owned, plain)

    assert (run.cache_key(advisor.request_for(plain, ctx, frozen))
            != run.cache_key(advisor.request_for(starred, ctx, frozen)))


def test_a_star_nobody_owns_says_nothing(game_data, wylder):
    """It is nowhere on screen and cannot be taken off, so a line about it
    would stand for ever (AD-059.5)."""
    owned = advisor.make_inventory(game_data, wylder, count=2)
    question = dataclasses.replace(advisor.problem([advisor.RED]),
                                   pinned=((1, (2,), ()),))
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data, wylder))
    frozen = run.frozen_inventory(owned, question)

    result = run.run(advisor.request_for(question, ctx, frozen), frozen, ctx,
                     goals.GOALS)

    assert result.pins_left_out == ()
    assert result.pins_placed == ()


def test_a_star_the_player_holds_is_met_and_not_laid_again(game_data, wylder):
    """Two copies of one roll: the held one is the star."""
    rolls = advisor.raising_effects(game_data, wylder, 1) * 4
    owned = advisor.make_inventory(game_data, wylder, count=3, rolls=rolls)
    first = owned.relics[0]

    result, *_ = _starred(
        game_data, wylder, owned, [advisor.RED, advisor.RED], stars=[first],
        held={0: advisor.held_relic(first)})

    assert result.pins_placed == ()
    assert result.pins_left_out == ()


def _one_left_out(result) -> types.PinLeftOut:
    assert len(result.pins_left_out) == 1
    return result.pins_left_out[0]


def test_an_avoided_star_stays_out_and_names_the_effect(game_data, wylder):
    """`PIN_AVOIDED`: A18 beats the star, and the star stays set."""
    owned = advisor.make_inventory(game_data, wylder, count=2)
    star = owned.relics[0]
    avoided = star.effect_ids[0]

    result, _, ctx, _ = _starred(game_data, wylder, owned, [advisor.RED],
                                 stars=[star], excluded=frozenset({avoided}))

    left = _one_left_out(result)
    name = run.explain._effect_name(ctx, avoided)
    assert left.reason == types.PIN_AVOIDED
    assert left.because == f"it carries “{name}”, which you avoided"
    assert result.pins_placed == ()


def test_a_rejected_star_stays_out(game_data, wylder):
    """`PIN_REJECTED`."""
    owned = advisor.make_inventory(game_data, wylder, count=2)
    star = owned.relics[0]

    result, *_ = _starred(game_data, wylder, owned, [advisor.RED], stars=[star],
                          rejected=frozenset({types.roll_of(star)}))

    left = _one_left_out(result)
    assert left.reason == types.PIN_REJECTED
    assert left.because == "you rejected it for this build"


def test_a_star_without_a_handle_cannot_be_laid(game_data, wylder):
    """`PIN_NO_COPY`: applying it would have no copy to name (AD-013.4)."""
    owned = advisor.make_inventory(game_data, wylder, count=2,
                                   handles=[None, 101])

    result, *_ = _starred(game_data, wylder, owned, [advisor.RED],
                          stars=[owned.relics[0]])

    left = _one_left_out(result)
    assert left.reason == types.PIN_NO_COPY
    assert left.because == "you own no copy that is free"


def test_a_star_of_a_colour_the_vessel_lacks_says_so(game_data, wylder):
    """`PIN_NO_SLOT`, the ordinary form."""
    owned = advisor.make_inventory(game_data, wylder, count=1,
                                   other_colour=advisor.BLUE)
    star = next(copy for copy in owned.relics if copy.colour == advisor.BLUE)

    result, *_ = _starred(game_data, wylder, owned, [advisor.RED], stars=[star])

    left = _one_left_out(result)
    assert left.reason == types.PIN_NO_SLOT
    assert left.because == "this vessel has no slot that fits its colour"


def test_a_deep_star_with_deep_of_night_off_says_that(game_data, wylder):
    """`PIN_NO_SLOT`, the Deep form (AK-456)."""
    owned = advisor.make_inventory(game_data, wylder, count=1, deep_count=1)
    star = next(copy for copy in owned.relics if copy.is_deep)

    result, *_ = _starred(game_data, wylder, owned, [advisor.RED], stars=[star])

    left = _one_left_out(result)
    assert left.reason == types.PIN_NO_SLOT
    assert left.because == ("it is a Deep of Night relic and Deep of Night is "
                            "off")


def test_a_hold_beats_a_star(game_data, wylder):
    """`PIN_SLOTS_HELD`, AD-059.6: a slot held empty is no more free than a
    filled one."""
    owned = advisor.make_inventory(game_data, wylder, count=2)
    star = owned.relics[0]

    result, *_ = _starred(game_data, wylder, owned, [advisor.RED], stars=[star],
                          held={0: None})

    left = _one_left_out(result)
    assert left.reason == types.PIN_SLOTS_HELD
    assert left.because == "every slot it could go in is held"
    assert result.pins_placed == ()
    assert [entry.relic for entry in result.held] == [None]


def test_the_stronger_star_takes_the_only_slot(game_data, wylder):
    """`PIN_OTHER_PIN`, and who is left over is the weakest (AD-059.3)."""
    owned = advisor.make_inventory(game_data, wylder, count=4)
    colours = [advisor.RED]
    plain, *_ = _starred(game_data, wylder, owned, colours, stars=())
    strongest = plain.suggestions[0].choices[0].handle
    strong = next(copy for copy in owned.relics if copy.handle == strongest)
    weak = next(copy for copy in owned.relics if copy.handle != strongest)

    result, *_ = _starred(game_data, wylder, owned, colours,
                          stars=[weak, strong])

    assert result.suggestions[0].choices[0].handle == strongest
    left = _one_left_out(result)
    assert left.reason == types.PIN_OTHER_PIN
    assert left.name == weak.name
    assert left.other == strong.name
    assert left.because == (f"“{strong.name}” is favourited too and takes the "
                            f"only slot it could use")


def test_a_favourite_effect_beats_a_star(game_data, wylder):
    """`PIN_BLOCKS_REQUIREMENT`, AK-440: one slot, one relic carrying the
    favourite, a star that does not. The favourite goes in."""
    owned = advisor.make_inventory(game_data, wylder, count=2)
    star, carrier = owned.relics[0], owned.relics[1]
    wanted = carrier.effect_ids[0]

    result, _, ctx, _ = _starred(game_data, wylder, owned, [advisor.RED],
                                 stars=[star], required=frozenset({wanted}))

    left = _one_left_out(result)
    name = run.explain._effect_name(ctx, wanted)
    assert left.reason == types.PIN_BLOCKS_REQUIREMENT
    assert left.because == f"placing it would leave “{name}” (Favourite) unmet"
    assert result.suggestions[0].choices[0].handle == carrier.handle
    assert result.required_left_out == ()


def test_a_star_that_carries_the_favourite_is_laid(game_data, wylder):
    """The same slot, but the star is itself the carrier: nothing is lost."""
    owned = advisor.make_inventory(game_data, wylder, count=2)
    star = owned.relics[0]

    result, *_ = _starred(game_data, wylder, owned, [advisor.RED], stars=[star],
                          required=frozenset({star.effect_ids[0]}))

    assert result.pins_placed == (0,)
    assert result.required_left_out == ()


def test_the_why_row_of_a_star_left_out_names_its_effects(game_data, wylder):
    """AK-456: `{relic name} ({effect}, {effect}) — {reason}`."""
    owned = advisor.make_inventory(game_data, wylder, count=2)
    star = owned.relics[0]

    result, _, ctx, _ = _starred(game_data, wylder, owned, [advisor.RED],
                                 stars=[star],
                                 rejected=frozenset({types.roll_of(star)}))

    names = ", ".join(run.explain._effect_name(ctx, eid)
                      for eid in star.effect_ids)
    assert _one_left_out(result).line == (
        f"{star.name} ({names}) — you rejected it for this build")


def test_an_unknown_star_reason_is_an_error(game_data, wylder):
    """AK-456: no quiet fallback sentence."""
    left = types.PinLeftOut("Urn", (1, (), ()), "something new")
    ctx = advisor.context(game_data, wylder)

    with pytest.raises(KeyError):
        run.explain.pins_left_out((left,), advisor.problem([advisor.RED]), ctx)


# -- every vessel, the same question (AD-062) --------------------------------

A_VESSEL = {"id": 1, "slots": [advisor.RED, advisor.RED], "deep_slots": []}
BLUE_VESSEL = {"id": 2, "slots": [advisor.BLUE, advisor.BLUE], "deep_slots": []}
WHITE_VESSEL = {"id": 3, "slots": [advisor.BLUE, model.WHITE_SLOT],
                "deep_slots": []}


def _a_held(name="Held", colour=advisor.RED, is_deep=False):
    return types.HeldRelic(relic_id=1, name=name, colour=colour,
                           is_deep=is_deep, handle=5)


def _asked_with_holds(*held):
    return types.AdvisorRequest(
        hero_id=1, level=15, goal_id=DAMAGE, weighting_id="even",
        problem=types.SlotProblem(
            slots=(types.Slot(0, advisor.RED, False),
                   types.Slot(1, advisor.RED, False)),
            held=held, rejected=frozenset({(9, (), ())})))


def test_a_row_says_what_optimize_says_there(game_data, wylder):
    """The guard of AD-062: one number, whichever screen reads it."""
    inventory, _problem, ctx, request = advisor.a_question(game_data, wylder)
    result = run.run(request, inventory, ctx, goals.GOALS)
    row = run.vessel_row(7, result)
    best = result.suggestions[0].score
    assert (row.vessel_id, row.figure, row.value) == (7, best.display,
                                                      best.value)
    assert row.other_value == goals.MIN_DAMAGE_TAKEN.score(
        evaluate(request.problem, _chosen(
            result, inventory, request.problem, ctx), ctx,
            goal=goals.MIN_DAMAGE_TAKEN), ctx).value


def test_a_vessel_with_no_suggestion_shows_its_base_state(game_data):
    """AK-449: the base state's own figure, formatted once, by the goal."""
    result = _recluse_sorceries(game_data, "Fire")
    assert result.suggestions == ()
    base = next(line for line in result.baseline if line.goal_id == DAMAGE)
    row = run.vessel_row(7, result)
    assert row.value == base.value
    assert row.figure == result.baseline_display != ""


@pytest.mark.parametrize("better, worse", [
    (types.VesselRow(1, value=1.0, other_value=1.0),
     types.VesselRow(2, value=9.0, other_value=9.0, required_left_out=(4,))),
    (types.VesselRow(1, value=1.0, other_value=1.0),
     types.VesselRow(2, value=9.0, other_value=9.0, pins_left_out=("Urn",))),
    (types.VesselRow(1, value=2.0, other_value=1.0),
     types.VesselRow(2, value=1.0, other_value=9.0)),
    (types.VesselRow(1, value=1.0, other_value=2.0),
     types.VesselRow(2, value=1.0, other_value=1.0)),
    (types.VesselRow(1, value=0.0, required_left_out=(4, 5)),
     types.VesselRow(2, value=9.0, unfit_holds=("Urn",))),
], ids=["effects", "stars", "this direction", "the other", "unfit"])
def test_one_key_of_the_rank_decides_alone(better, worse):
    """AK-463, each key on its own: the list's order would say the opposite."""
    assert run.ranked((worse, better), (2, 1))[0] is better


def test_favourite_effects_outrank_stars():
    """AK-463: effects before stars, whatever the counts."""
    effect = types.VesselRow(1, required_left_out=(4,))
    stars = types.VesselRow(2, pins_left_out=("Urn", "Goblet"))
    assert run.ranked((effect, stars), (1, 2))[0] is stars


def test_the_list_decides_only_when_every_key_is_level():
    first, second = types.VesselRow(1, value=1.0), types.VesselRow(2, value=1.0)
    assert run.rank_key(first) == run.rank_key(second)
    assert run.ranked((first, second), (2, 1))[0] is second


def test_the_chosen_vessel_is_asked_first_and_unchanged():
    """AD-062.3: its question is the one just answered, so it is a hit."""
    asked = _asked_with_holds(types.HeldSlot(1, _a_held()), types.HeldSlot(0))
    questions = run.vessel_questions(
        asked, (WHITE_VESSEL, A_VESSEL), A_VESSEL["id"], False)
    assert questions[0] == types.VesselQuestion(A_VESSEL["id"], asked)
    assert [question.vessel_id for question in questions] == [1, 3]


def test_a_hold_travels_to_its_own_colour_before_a_white_slot():
    relic = _a_held(colour=advisor.BLUE)
    asked = _asked_with_holds(types.HeldSlot(1, relic))
    _chosen_one, other = run.vessel_questions(
        asked, (A_VESSEL, WHITE_VESSEL), A_VESSEL["id"], False)
    problem = other.request.problem
    assert problem.held == (types.HeldSlot(0, relic),)
    assert problem.slots == run.vessel_slots(WHITE_VESSEL, False)
    assert problem.rejected == asked.problem.rejected


def test_a_slot_held_empty_stays_with_its_vessel():
    asked = _asked_with_holds(types.HeldSlot(0))
    _chosen_one, other = run.vessel_questions(
        asked, (A_VESSEL, BLUE_VESSEL), A_VESSEL["id"], False)
    assert other.request.problem.held == ()


def test_a_vessel_that_cannot_take_the_holds_is_not_asked():
    """AD-062.5: the row says so instead of a figure that is not comparable."""
    asked = _asked_with_holds(types.HeldSlot(0, _a_held("Red one")))
    _chosen_one, other = run.vessel_questions(
        asked, (A_VESSEL, BLUE_VESSEL), A_VESSEL["id"], False)
    assert other == types.VesselQuestion(BLUE_VESSEL["id"],
                                         unfit_holds=("Red one",))


def test_a_custom_relic_of_a_white_slot_fits_any_slot_of_its_kind():
    """AD-062.5: built in a white slot it has no colour to ask for."""
    custom = _a_held("Custom relic", colour=model.WHITE_SLOT)
    asked = _asked_with_holds(types.HeldSlot(0, custom))
    _chosen_one, other = run.vessel_questions(
        asked, (A_VESSEL, BLUE_VESSEL), A_VESSEL["id"], False)
    assert other.request.problem.held == (types.HeldSlot(0, custom),)


def test_a_deep_relic_does_not_travel_to_an_ordinary_slot():
    asked = _asked_with_holds(types.HeldSlot(0, _a_held(is_deep=True)))
    _chosen_one, off, on = run.vessel_questions(
        asked, (A_VESSEL, {**WHITE_VESSEL, "id": 4},
                {**WHITE_VESSEL, "id": 5}), A_VESSEL["id"], False)
    assert off.unfit_holds and on.unfit_holds
    deep = {"id": 6, "slots": [advisor.BLUE], "deep_slots": [advisor.RED]}
    _chosen_one, there = run.vessel_questions(
        asked, (A_VESSEL, deep), A_VESSEL["id"], True)
    assert there.request.problem.held[0].index == 1


def test_the_moved_holds_say_where_each_came_from():
    """`Switch to it` reads this to carry the slot's own stored key along."""
    first, second = _a_held("First"), _a_held("Second", colour=advisor.BLUE)
    moved, unfit = run.held_moved_to(
        (types.HeldSlot(1, first), types.HeldSlot(0, second)),
        run.vessel_slots({"slots": [advisor.BLUE, advisor.RED]}, False))
    assert moved == ((1, types.HeldSlot(1, first)),
                     (0, types.HeldSlot(0, second)))
    assert unfit == ()


# -- every owned carrier turned down (AK-461, the same for `Reject`) ----------

EFFECTS = {"data": {"effects": {
    str(eid): {"name": name} for eid, name in (
        (1, "Wanted"), (2, "Zebra"), (3, "Apple"), (4, "Mango"))}}}


def _a_copy(*effect_ids, relic_id=1, curse_ids=()):
    return run.OfferedCopy(handle=relic_id, relic_id=relic_id, name="Relic",
                           colour=0, is_deep=False, effect_ids=effect_ids,
                           curse_ids=curse_ids)


def _unmet(*copies, avoid=(), rejected=(), pools=()):
    problem = types.SlotProblem(excluded=frozenset(avoid),
                                rejected=frozenset(rejected))
    ctx = types.GoalContext(data=EFFECTS["data"], hero={}, level=1,
                            reference=None, weighting=goals.DEFAULT_WEIGHTING)
    inventory = run.FrozenInventory(relics=copies, offers={})
    line, = explain.required_but_unmet((1,), problem, pools, ctx, inventory)
    return line


def test_one_carrier_avoided_names_the_way_back():
    assert _unmet(_a_copy(1, 2), avoid={2}) == (
        "You own 1 copy carrying “Wanted”, which you favourited, but it also "
        "carries an effect you avoided: “Zebra”. Remove the avoid under "
        "Filters to use it.")


def test_several_carriers_avoided_names_them_alphabetically():
    assert _unmet(_a_copy(1, 2, relic_id=1), _a_copy(1, 3, relic_id=2),
                  _a_copy(1, relic_id=3, curse_ids=(4,)),
                  avoid={2, 3, 4}) == (
        "You own 3 copies carrying “Wanted”, which you favourited, but each "
        "also carries an effect you avoided: “Apple”, “Mango” and 1 more. "
        "Remove the avoid under Filters to use them.")


def test_a_carrier_left_that_merely_does_not_fit_keeps_the_old_sentence():
    assert _unmet(_a_copy(1, 2, relic_id=1), _a_copy(1, relic_id=2),
                  avoid={2}) == (
        "You own 2 copies carrying “Wanted”, but none fits the open slots.")


def test_a_rejected_carrier_points_at_suggest_again():
    one = _a_copy(1, relic_id=1)
    other = _a_copy(1, 3, relic_id=2)
    assert _unmet(one, rejected={types.roll_of(one)}) == (
        "You own 1 copy carrying “Wanted”, which you favourited, but you "
        "rejected it for this build. Use Suggest again to bring it back.")
    assert _unmet(one, other, rejected={types.roll_of(one),
                                        types.roll_of(other)}) == (
        "You own 2 copies carrying “Wanted”, which you favourited, but you "
        "rejected them for this build. Use Suggest again to bring them back.")


def test_carriers_avoided_and_rejected_name_both_ways_back():
    one = _a_copy(1, relic_id=1)
    assert _unmet(one, _a_copy(1, 2, relic_id=2),
                  rejected={types.roll_of(one)}, avoid={2}) == (
        "You own 2 copies carrying “Wanted”, which you favourited, but each is "
        "rejected for this build or also carries an effect you avoided: "
        "“Zebra”. Use Suggest again, or remove the avoid under Filters, to use "
        "them.")
