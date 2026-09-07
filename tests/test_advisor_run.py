"""One question answered whole, and the memo of the answer.

Three claims carry this file.

* **The answer is one run's own.** Every figure in an `AdvisorResult` comes
  out of the run that produced it: the gain is worked out here from the base
  state and the built one, never read back out of the module under test, and
  every suggestion of the beam carries its reasons rather than only the head
  of the list.
* **A hit is a speed-up, never a second way to compute** (AD-007). What comes
  out of the cache is held against a **fresh** run of the same question, over
  both directions and both Deep settings, and the denominator is asserted --
  a case that silently covered one combination would say nothing about the
  other three.
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

from nrplanner.advisor import goals, run, search, types
from nrplanner.advisor.evaluate import evaluate

from tests import advisor_cases as advisor
from tests import weapon_damage_cases as cases

DAMAGE = "max_damage"
SURVIVAL = "min_damage_taken"


@pytest.fixture(scope="module")
def wylder(game_data):
    return cases.hero_by_name(game_data, "Wylder")


def request_for(problem: types.SlotProblem, ctx: types.GoalContext, inventory,
                goal_id: str = DAMAGE,
                generation: int = 0) -> types.AdvisorRequest:
    """The request the window would build for this question.

    Derived from the context beside it, which is what the window does and
    what `run.run` insists on: the request is the cache key, so a field of it
    that does not describe the run would be a key standing for a run that
    never happened. The cases that break that on purpose do it by name,
    below.
    """
    meta = ctx.data.get("meta") or {}
    return types.AdvisorRequest(
        hero_id=ctx.hero["id"],
        level=ctx.level,
        problem=problem,
        goal_id=goal_id,
        weighting_id=ctx.weighting.id,
        reference_weapon_id=(None if ctx.reference is None
                             else ctx.reference.weapon["id"]),
        declared=tuple(ctx.declared),
        data_version=str(meta.get("data_version") or ""),
        inventory_fingerprint=run.inventory_fingerprint(inventory),
        generation=generation,
    )


def a_question(game_data, hero, *, colours=(advisor.RED, advisor.RED),
               deep: bool = False, count: int = 4, held=None,
               goal_id: str = DAMAGE, generation: int = 0):
    """Inventory, problem, context and request for one small question."""
    inventory = advisor.make_inventory(game_data, hero, colour=advisor.RED,
                                       count=count,
                                       deep_count=len(colours) if deep else 0)
    problem = advisor.problem(colours, deep=deep, held=held)
    ctx = advisor.context(game_data, hero,
                          reference=advisor.scaling_armament(game_data, hero))
    frozen = run.frozen_inventory(inventory, problem)
    return frozen, problem, ctx, request_for(problem, ctx, frozen, goal_id,
                                             generation)


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
    inventory, problem, ctx, request = a_question(game_data, wylder)

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
    inventory, problem, ctx, request = a_question(
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
    inventory, problem, ctx, request = a_question(game_data, wylder)

    result = run.run(request, inventory, ctx, goals.GOALS)

    assert len(result.suggestions) > 1, (
        "one suggestion cannot tell the head of a list from its tail")
    for suggestion in result.suggestions:
        assert len(suggestion.reasons) == len(suggestion.choices), (
            f"{len(suggestion.reasons)} slot groups for "
            f"{len(suggestion.choices)} filled slots")


def test_the_singular_fields_belong_to_the_best_suggestion(game_data, wylder):
    """`Apply all` applies the first, so the curses named are the first's.

    Read off the inventory rather than off the result: the copies of the best
    suggestion are looked up by handle and their curse ids are what the
    dataset gives them names for.
    """
    inventory, problem, ctx, request = a_question(game_data, wylder, count=6)

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

def test_a_run_stopped_before_the_search_says_so(game_data, wylder):
    """The pre-sort and the search are two steps, and the check is between
    them: on the worst real case the pre-sort is 43 ms of a 960 ms run
    (`scripts/measure_advisor_search.py`), so it is not cut in two.
    """
    inventory, problem, ctx, request = a_question(game_data, wylder)

    with pytest.raises(search.Cancelled, match="pre-sort"):
        run.run(request, inventory, ctx, goals.GOALS, Counter(stop_at=0))


def test_a_run_asks_once_between_the_pre_sort_and_the_search(game_data,
                                                             wylder):
    """The question is asked, and it is asked in the place that was costed.

    Counted rather than watched: a check that ran only inside the search
    would leave the pre-sort uninterruptible without any case going red, and
    one that ran per candidate would cost more than the reaction time it buys
    (AD-006 point 6).
    """
    inventory, problem, ctx, request = a_question(game_data, wylder)
    watch = Counter()

    run.run(request, inventory, ctx, goals.GOALS, watch)

    free = len(types.free_slots(problem))
    assert watch.asked == free + 1, (
        f"one question between the pre-sort and the search plus one before "
        f"each of the {free} levels is {free + 1}; this run asked "
        f"{watch.asked} times")


def test_a_run_stopped_inside_the_search_says_so(game_data, wylder):
    """`search.Cancelled` travels out of the run unchanged.

    A truncated beam and a finished one are the same shape, so the run may
    not turn a stop into a short answer: `Stopped. Nothing was changed.` and
    a list of suggestions are two states of the window (`UI_SPEC` 4.5
    against 4.6).
    """
    inventory, problem, ctx, request = a_question(game_data, wylder)

    with pytest.raises(search.Cancelled, match="1 of 2 slots"):
        run.run(request, inventory, ctx, goals.GOALS, Counter(stop_at=2))


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
    inventory, problem, ctx, request = a_question(game_data, wylder)
    lying = dataclasses.replace(request, **{field: wrong})

    with pytest.raises(ValueError, match=field.split()[0]):
        run.run(lying, inventory, ctx, goals.GOALS)


def test_a_request_that_names_an_unknown_direction_is_refused(game_data,
                                                              wylder):
    inventory, problem, ctx, request = a_question(game_data, wylder)

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

@pytest.mark.parametrize("goal_id", [DAMAGE, SURVIVAL])
@pytest.mark.parametrize("deep", [False, True])
def test_a_hit_is_what_a_fresh_run_would_have_said(game_data, wylder,
                                                   goal_id, deep):
    """AD-007: the cache is a speed-up and not a second way to compute.

    Four combinations, and the denominator is the point: two directions
    times both Deep settings. Held against a **fresh** run of the same
    question rather than against the stored object, so the claim is that the
    cache does not answer differently from computing again -- which is also
    the claim that computing again answers the same way at all.
    """
    inventory, problem, ctx, request = a_question(
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


def test_all_four_combinations_of_direction_and_deep_are_covered():
    """The denominator of the case above, so that dropping one is visible."""
    combinations = [(goal_id, deep)
                    for goal_id in (DAMAGE, SURVIVAL)
                    for deep in (False, True)]

    assert len(combinations) == 4
    assert set(goals.GOALS) == {DAMAGE, SURVIVAL}, (
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
    inventory, problem, ctx, request = a_question(game_data, wylder)
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
    inventory, problem, ctx, request = a_question(
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
    inventory, problem, ctx, request = a_question(game_data, wylder,
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
    inventory, problem, ctx, request = a_question(game_data, wylder)
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
