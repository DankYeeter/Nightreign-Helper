"""The beam over the free slots: what it may pick, and in what order.

Four claims carry this file, and each of them is a rule the search would
break silently rather than loudly:

* **a copy lies in one slot** (AD-013). Without it `Wylder's Urn` gives 40
  unusable suggestions out of 40, the best one included, each with a plausible
  score. On that vessel the ownership rule and the symmetry rule guard the
  same property, so the case that can tell them apart is the one on a vessel
  with a **white** slot beside a coloured one -- both cases are here, and the
  report to T-067 says why;
* **a held slot is never a level** (AD-014.2). With everything held there is
  no search at all, and the answer is the build as it stands, scored;
* **the symmetry rule is formed over the free slots** (AD-014.4), so a hold on
  the first red slot does not quietly forbid the free one every copy that
  ranks above what is being held;
* **the same question is answered the same way twice**, in this process and in
  the next one (AD-009 point 6). This project has twice shipped a display
  whose order followed the hash seed (QA-059, QA-142), so the second half of
  that is measured across processes rather than argued.

The synthetic cases below build their own pools and their own scorer. That is
not a shortcut around the dataset: it is what lets a case *state* a tie, a
narrow budget or an empty slot instead of hoping the inventory contains one,
and it keeps the cross-process case down to a few tenths of a second.
"""

from __future__ import annotations

import dataclasses
import os
import pathlib
import subprocess
import sys

import pytest

from nrplanner.advisor import candidates, goals, search, types

from tests import advisor_cases as advisor
from tests import weapon_damage_cases as cases

DAMAGE = "max_damage"
SURVIVAL = "min_damage_taken"

REPO = pathlib.Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def wylder(game_data):
    return cases.hero_by_name(game_data, "Wylder")


# -- synthetic material -----------------------------------------------------
#
# A pool the case describes itself, so that a tie, an empty slot or a budget
# narrower than the pool is stated rather than looked for.

def offer(slot_index: int, handle: int, worth: float = 0.0,
          colour: int = advisor.RED) -> types.Candidate:
    """One copy on offer for one slot, with what it is worth on its own."""
    return types.Candidate(
        slot_index=slot_index, handle=handle, relic_id=1000 + handle,
        name=f"Copy {handle}", colour=colour, is_deep=False,
        marginals=(types.Marginal(DAMAGE, worth),),
    )


#: The direction the synthetic scorers below claim, and the one the synthetic
#: pools are built under. It is deliberately not a goal of the registry: the
#: pairing D-4 checks is between two names, and a case that used a real goal
#: id here could pass because the registry happens to hold it.
SYNTHETIC = "the case's own direction"


def pool_of(slot_index: int, offers,
            rank_by: str = SYNTHETIC) -> types.SlotPool:
    return types.SlotPool(slot_index=slot_index, rank_by=rank_by,
                          candidates=tuple(offers))


def adding_scorer(worth: dict[int, float]) -> search.Scorer:
    """A scorer that adds up what each chosen copy is worth.

    Deliberately not a goal: the point of the scorer being a parameter is that
    the search does not know what it is ranking (AD-003, AD-002/C).
    """
    def score(assignment: tuple[types.Candidate, ...]) -> types.GoalScore:
        total = sum(worth[chosen.handle] for chosen in assignment)
        return types.GoalScore(value=total, display=f"{total:.2f}",
                               unit="points")

    return search.Scorer(goal_id=SYNTHETIC, score=score)


def tied_scorer() -> search.Scorer:
    """Every assignment is worth exactly the same.

    Ties are the common case rather than the exception -- the scaling curves
    are piecewise linear, so two assignments inside one segment are worth
    exactly the same (`tests/test_marginal_returns.py`) -- and they are where
    an order is decided by something other than the figure.
    """
    def score(assignment: tuple[types.Candidate, ...]) -> types.GoalScore:
        return types.GoalScore(value=1.0, display="1.00", unit="points")

    return search.Scorer(goal_id=SYNTHETIC, score=score)


def slots_of(*colours, deep: bool = False) -> tuple[types.Slot, ...]:
    return tuple(types.Slot(index=index, colour=colour, deep=deep)
                 for index, colour in enumerate(colours))


def handles_of(suggestion: types.Suggestion) -> list[int]:
    return [choice.handle for choice in suggestion.choices]


# -- material out of the real dataset ---------------------------------------

def vessel_problem(data: dict, name: str, deep: bool = False,
                   held: dict | None = None) -> types.SlotProblem:
    """A named vessel of the dataset as an advisor question.

    By name rather than by colours written out here: AD-009 point 4 asks for
    `Wylder's Urn` specifically, because a vessel with three different colours
    would pass the ownership case while proving nothing, and a vessel spelled
    out in the test would stop being that vessel the day the game changes it.
    """
    vessel = next(v for v in data["vessels"] if v["name"] == name)
    ordinary = list(vessel["slots"])
    colours = ordinary + (list(vessel["deep_slots"]) if deep else [])
    slots = tuple(types.Slot(index=index, colour=colour,
                             deep=index >= len(ordinary))
                  for index, colour in enumerate(colours))
    entries = tuple(types.HeldSlot(index=index, relic=relic)
                    for index, relic in sorted((held or {}).items()))
    return types.SlotProblem(slots=slots, held=entries)


def run_over(inventory, problem, ctx, rank_by=DAMAGE,
             budget=types.DEFAULT_BUDGET) -> tuple[types.Suggestion, ...]:
    """The whole path: pools out of the inventory, then the beam over them."""
    pools = candidates.pools(inventory, problem, ctx, goals.GOALS, rank_by)
    scorer = search.goal_scorer(problem, ctx, goals.GOALS[rank_by])
    return search.beam(problem, pools, budget, scorer)


# -- AD-009 point 3: the colour rule survives the search --------------------

def test_no_suggestion_puts_a_copy_in_a_slot_that_cannot_hold_it(game_data,
                                                                 wylder):
    """A4: the suggestion respects the vessel's own slot colours.

    End to end rather than at the pool boundary, because the pool is not what
    the player is handed: the search picks one pool per level, and a level
    that read the wrong pool would offer a blue slot the red list without any
    figure looking wrong.
    """
    inventory = advisor.make_inventory(game_data, wylder, colour=advisor.RED,
                                       count=4, other_colour=advisor.BLUE)
    problem = vessel_problem(game_data, "Wylder's Urn")
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))

    found = run_over(inventory, problem, ctx)

    assert found, "nothing was suggested, so no colour rule is being watched"
    placed = 0
    for suggestion in found:
        for choice in suggestion.choices:
            slot = types.slot_at(problem, choice.slot_index)
            allowed = {relic.handle for relic
                       in inventory.relics_for(slot.colour, slot.deep)}
            placed += 1
            assert choice.handle in allowed, (
                f"{choice.name} went into slot {choice.slot_index}, which "
                f"takes colour {slot.colour}")
    assert placed, "no suggestion filled a slot, so nothing was checked"


# -- AD-009 point 4: a copy lies in one slot --------------------------------

def test_no_copy_lies_in_two_slots_of_wylders_urn(game_data, wylder):
    """AD-009 point 4, on the vessel it names: `Wylder's Urn` `[0, 0, 1]`.

    A vessel with three different colours would pass this while proving
    nothing -- AD-013 measured 5 unusable suggestions out of 40 there against
    40 out of 40 here. What the case cannot say on this vessel is **which**
    rule kept the copy in one slot: two red slots are one symmetry group, and
    ascending candidate order already forbids the repeat. The case below on
    `Wylder's Chalice` is the one that isolates the ownership rule.
    """
    inventory = advisor.make_inventory(game_data, wylder, colour=advisor.RED,
                                       count=3, other_colour=advisor.BLUE)
    problem = vessel_problem(game_data, "Wylder's Urn")
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))

    found = run_over(inventory, problem, ctx)

    assert found, "nothing was suggested, so no ownership rule is watched"
    unusable = [handles_of(s) for s in found
                if len(set(handles_of(s))) != len(handles_of(s))]
    assert not unusable, (
        f"{len(unusable)} of {len(found)} suggestions lay one copy in two "
        f"slots; first three: {unusable[:3]}")


def test_a_white_slot_does_not_take_the_copy_a_coloured_slot_already_has(
        game_data, wylder):
    """The ownership rule on its own, without the symmetry rule beside it.

    `Wylder's Chalice` is `[Red, Yellow, White]`, and a white slot draws every
    colour (`inventory.relics_for`). So the red slot and the white slot are
    **not** interchangeable -- they are different symmetry groups -- and they
    are offered the same red copies. That is the shape in which only the
    handle set in the search state can keep a copy in one slot.
    """
    inventory = advisor.make_inventory(game_data, wylder, colour=advisor.RED,
                                       count=2)
    problem = vessel_problem(game_data, "Wylder's Chalice")
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))

    found = run_over(inventory, problem, ctx)

    both = [s for s in found if len(s.choices) == 2]
    assert both, (
        "no suggestion filled the red slot and the white slot at once, so "
        "the case cannot see whether one copy went into both")
    unusable = [handles_of(s) for s in both
                if len(set(handles_of(s))) != len(handles_of(s))]
    assert not unusable, (
        f"{len(unusable)} of {len(both)} suggestions put one copy into the "
        f"coloured slot and the white one; first three: {unusable[:3]}")


def test_the_search_spends_the_copies_the_held_relics_occupy(game_data,
                                                             wylder):
    """AD-014.5: the base state occupies its handles before the first level.

    The pool built by `candidates.pool` already leaves a held copy out, so a
    run through it could not see whether the search keeps the rule of its own.
    This case therefore hands the search a pool that **does** carry the held
    copy: the beam state is the last place the rule can hold, and AD-013
    point 2 puts it there.
    """
    inventory = advisor.make_inventory(game_data, wylder, colour=advisor.RED,
                                       count=2)
    kept, spare = inventory.relics_for(advisor.RED, False)
    problem = advisor.problem([advisor.RED, advisor.RED],
                              held={0: advisor.held_relic(kept)})
    offers = [offer(1, kept.handle, 5.0), offer(1, spare.handle, 1.0)]
    worth = {kept.handle: 5.0, spare.handle: 1.0}

    found = search.beam(problem, [pool_of(1, offers)], types.DEFAULT_BUDGET,
                        adding_scorer(worth))

    assert found, "nothing was suggested, so nothing is being watched"
    assert all(kept.handle not in handles_of(s) for s in found), (
        f"the copy held in slot 0 (handle {kept.handle}) was suggested again "
        f"for slot 1: {[handles_of(s) for s in found]}")


# -- AD-013 point 2: the first K available, not the first K of the list -----

def test_the_branching_takes_the_first_available_and_not_the_first_listed():
    """A copy an earlier slot spent is passed over, not counted.

    Three slots of one colour, five copies, K=2, so the shortlist is
    `K + (free slots - 1)` = four long and every level has to find two
    **available** copies inside it. Taking the first K of the list and
    dropping what is no longer available leaves the second level one branch
    and the third none at all: the branching narrows at the deeper slots,
    quietly, and worst where the vessel repeats a colour -- which is where the
    ownership rule bites hardest.
    """
    problem = types.SlotProblem(
        slots=slots_of(advisor.RED, advisor.RED, advisor.RED))
    worth = {10: 5.0, 11: 4.0, 12: 3.0, 13: 2.0, 14: 1.0}
    pools = [pool_of(index, [offer(index, handle, value)
                             for handle, value in worth.items()])
             for index in (0, 1, 2)]
    budget = types.Budget(candidates_per_slot=2, beam_width=40)

    found = search.beam(problem, pools, budget, adding_scorer(worth))

    assert [handles_of(s) for s in found] == [[10, 11, 12], [10, 11, 13],
                                             [10, 12, 13], [11, 12, 13]]


# -- AD-003 point 2 and AD-014.4: symmetry over the free slots --------------

def test_two_slots_of_one_colour_are_not_offered_the_same_pair_twice():
    """AD-003 point 2: within a group, the choice ascends.

    Six copies in two interchangeable slots are fifteen pairs, not thirty. The
    rule is what stops the result list from showing one build twice with the
    two slots swapped.
    """
    problem = types.SlotProblem(slots=slots_of(advisor.RED, advisor.RED))
    worth = {10 + step: 6.0 - step for step in range(6)}
    pools = [pool_of(index, [offer(index, handle, value)
                             for handle, value in worth.items()])
             for index in (0, 1)]

    found = search.beam(problem, pools, types.DEFAULT_BUDGET,
                        adding_scorer(worth))

    assert len(found) == 15, (
        f"{len(found)} suggestions for six copies in two interchangeable "
        f"slots; fifteen pairs is what there are")
    assert all(handles_of(s) == sorted(handles_of(s)) for s in found)


def test_a_slot_alone_in_its_colour_carries_no_constraint():
    """AD-014.4: a single free slot of a colour has no symmetry and no floor.

    Two slots of **different** colours are not interchangeable, so the second
    one may take the best copy of its own pool whatever the first one took. A
    group formed over the slots rather than over their colours would forbid it
    and lose the best build without anything looking wrong.
    """
    problem = types.SlotProblem(slots=slots_of(advisor.RED, advisor.BLUE))
    worth = {10: 5.0, 11: 4.0, 20: 5.0, 21: 4.0}
    pools = [pool_of(0, [offer(0, 10, 5.0, advisor.RED),
                         offer(0, 11, 4.0, advisor.RED)]),
             pool_of(1, [offer(1, 20, 5.0, advisor.BLUE),
                         offer(1, 21, 4.0, advisor.BLUE)])]

    found = search.beam(problem, pools, types.DEFAULT_BUDGET,
                        adding_scorer(worth))

    assert handles_of(found[0]) == [10, 20], (
        f"the best build takes the best copy of each pool; this run chose "
        f"{handles_of(found[0])}")


def test_a_white_slot_is_not_interchangeable_with_a_coloured_one():
    """Being offered the same copies is not the same as being alike.

    A white slot draws every colour, so it sees every copy the red slot beside
    it sees -- and it sees more besides, which is exactly why the two are not
    one symmetry group. Read the group off "this copy is on offer here too"
    instead of off the slot's colour and the white slot may no longer take
    anything the red one ranked above: with two copies that is one build
    instead of two, and the one that goes missing is a build the player could
    wear.
    """
    problem = types.SlotProblem(slots=(
        types.Slot(index=0, colour=advisor.RED, deep=False),
        types.Slot(index=1, colour=advisor.WHITE, deep=False)))
    worth = {10: 2.0, 11: 1.0}
    pools = [pool_of(index, [offer(index, 10, 2.0), offer(index, 11, 1.0)])
             for index in (0, 1)]

    found = search.beam(problem, pools, types.DEFAULT_BUDGET,
                        adding_scorer(worth))

    assert [handles_of(s) for s in found] == [[10, 11], [11, 10]]


def test_a_deep_slot_and_an_ordinary_slot_of_one_colour_are_not_one_group(
        game_data, wylder):
    """Deep separates two slots that share a colour.

    `Wylder's Urn` with Deep of Night switched on is `[Red, Red, Blue]` twice
    over, and the two red pairs see different relics: a Deep slot takes Deep
    relics and an ordinary slot takes ordinary ones
    (`inventory.relics_for`). Group them by colour alone and the Deep pair
    inherits a floor read off a copy that is not in its list at all.
    """
    inventory = advisor.make_inventory(game_data, wylder, colour=advisor.RED,
                                       count=3, deep_count=3,
                                       other_colour=advisor.BLUE)
    problem = vessel_problem(game_data, "Wylder's Urn", deep=True)
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))
    pools = candidates.pools(inventory, problem, ctx, goals.GOALS, DAMAGE)
    deep_first = {pool.slot_index: pool.candidates[0].handle
                  for pool in pools if pool.candidates}

    found = run_over(inventory, problem, ctx)

    best = {choice.slot_index: choice.handle for choice in found[0].choices}
    assert best[3] == deep_first[3], (
        f"the first Deep red slot took handle {best.get(3)} where its own "
        f"pool leads with {deep_first[3]}")
    assert best[0] == deep_first[0], (
        f"the first ordinary red slot took handle {best.get(0)} where its "
        f"own pool leads with {deep_first[0]}")


def test_a_hold_does_not_forbid_the_free_slot_the_better_copies(game_data,
                                                               wylder):
    """Checkpoint 10: `Wylder's Urn`, the first red slot held.

    The two red slots stop being interchangeable the moment one of them is
    held, and AD-014.4 is the correction that follows: the symmetry group is
    formed over the **free** slots alone. Under the rule as AD-003 first wrote
    it, the free red slot could take no copy that ranks above the held one --
    and if the held relic is the last of the list, that is every copy there
    is.
    """
    inventory = advisor.make_inventory(game_data, wylder, colour=advisor.RED,
                                       count=4)
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))
    free_only = vessel_problem(game_data, "Wylder's Urn")
    ranked = candidates.pool(inventory, free_only, 1, ctx, goals.GOALS,
                             DAMAGE).candidates
    last = next(relic for relic in inventory.relics
                if relic.handle == ranked[-1].handle)
    problem = vessel_problem(game_data, "Wylder's Urn",
                             held={0: advisor.held_relic(last)})

    found = run_over(inventory, problem, ctx)

    chosen = {choice.handle for suggestion in found
              for choice in suggestion.choices if choice.slot_index == 1}
    assert ranked[0].handle in chosen, (
        f"the free red slot never got the best-ranked copy "
        f"{ranked[0].handle} while the worst-ranked one was held; it saw "
        f"{sorted(chosen)}")


def test_a_slot_the_symmetry_rule_empties_is_not_a_half_filled_build():
    """The last copy of a group leaves no half-filled suggestion behind.

    Two interchangeable slots and two copies make exactly one build. The
    branch that puts the second copy in the first slot has nothing left above
    it, and it is not the build "one slot filled, one left empty": it is the
    other branch with the slots swapped, which is already in the list.
    """
    problem = types.SlotProblem(slots=slots_of(advisor.RED, advisor.RED))
    worth = {10: 2.0, 11: 1.0}
    pools = [pool_of(index, [offer(index, 10, 2.0), offer(index, 11, 1.0)])
             for index in (0, 1)]

    found = search.beam(problem, pools, types.DEFAULT_BUDGET,
                        adding_scorer(worth))

    assert [handles_of(s) for s in found] == [[10, 11]]


def test_a_slot_with_nothing_to_choose_from_does_not_end_the_run():
    """`UI_SPEC` 4.11: `3 of 4 slots filled` is an answer, not a failure.

    A vessel can hold a colour the save has nothing for. The branch carries
    on with one slot fewer filled -- the alternative is a run that answers
    nothing at all because one slot of six had an empty pool.
    """
    problem = types.SlotProblem(slots=slots_of(advisor.RED, advisor.BLUE))
    pools = [pool_of(0, [offer(0, 10, 2.0)]), pool_of(1, [])]

    found = search.beam(problem, pools, types.DEFAULT_BUDGET,
                        adding_scorer({10: 2.0}))

    assert [handles_of(s) for s in found] == [[10]]


# -- AD-014.2: a held slot is never a level ---------------------------------

def test_every_slot_held_is_no_search_and_the_build_as_it_stands(game_data,
                                                                 wylder):
    """Checkpoint 14: with everything held there is no level to run over.

    The answer is the base state, scored -- an answer rather than a failure,
    and the same score `evaluate(problem, (), ctx)` gives. There is no branch
    in the search for this case, which is the point: a special case is a place
    where the two readings can come apart.
    """
    inventory = advisor.make_inventory(game_data, wylder, colour=advisor.RED,
                                       count=2)
    worn, other = inventory.relics_for(advisor.RED, False)
    problem = advisor.problem(
        [advisor.RED, advisor.RED],
        held={0: advisor.held_relic(worn), 1: advisor.held_relic(other)})
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))
    goal = goals.GOALS[DAMAGE]

    found = search.beam(problem, (), types.DEFAULT_BUDGET,
                        search.goal_scorer(problem, ctx, goal))

    from nrplanner.advisor.evaluate import evaluate
    standing = goal.score(evaluate(problem, (), ctx), ctx)
    assert len(found) == 1 and found[0].choices == ()
    assert found[0].score.value == standing.value


# -- AD-009 point 6: the same question, the same answer ---------------------

def test_the_same_question_answered_twice_gives_the_same_answer(game_data,
                                                                wylder):
    """AD-009 point 6, in one process: order included.

    Without it the cache is not checkable -- a hit and a miss would hand back
    two different lists for one request and neither would be wrong.
    """
    inventory = advisor.make_inventory(game_data, wylder, colour=advisor.RED,
                                       count=5, other_colour=advisor.BLUE)
    problem = vessel_problem(game_data, "Wylder's Urn")
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))

    first = run_over(inventory, problem, ctx)
    second = run_over(inventory, problem, ctx)

    assert first, "nothing was suggested, so nothing is being compared"
    assert first == second


def test_the_order_among_equals_follows_the_copies_and_not_the_pre_sort():
    """Equal builds are ordered by what is in them, not by how they arrived.

    The pool here is in descending handle order and every assignment is worth
    the same, so the order the beam generates its states in and the order it
    hands them back are two different orders. Python's sort is stable, so
    without a tie-break the answer would be the generation order -- which
    makes the list the player reads a property of the loop rather than of the
    build, and moves the day the loop is touched.
    """
    problem = types.SlotProblem(slots=slots_of(advisor.RED, advisor.BLUE))
    pools = [pool_of(0, [offer(0, handle) for handle in (13, 12, 11, 10)]),
             pool_of(1, [offer(1, handle, colour=advisor.BLUE)
                         for handle in (23, 22, 21, 20)])]

    found = search.beam(problem, pools, types.DEFAULT_BUDGET, tied_scorer())

    assert len({s.score.value for s in found}) == 1, (
        "the scorer was meant to tie every assignment; without a tie there "
        "is no tie-break under test")
    assert [handles_of(s) for s in found] == sorted(handles_of(s)
                                                    for s in found)


#: Run in a child process, twice, under two hash seeds. Everything it needs is
#: in `advisor/`, so it costs a few tenths of a second and needs no dataset --
#: which is what makes a second and a third seed affordable.
ACROSS_PROCESSES = '''
import sys
sys.path.insert(0, sys.argv[1])
from nrplanner.advisor import search, types


def offer(slot_index, handle):
    return types.Candidate(slot_index=slot_index, handle=handle,
                           relic_id=1000 + handle, name="Copy %d" % handle,
                           colour=0, is_deep=False)


def tied(assignment):
    return types.GoalScore(value=1.0, display="1.00", unit="points")


scorer = search.Scorer(goal_id="the case's own direction", score=tied)
slots = tuple(types.Slot(index=i, colour=i, deep=False) for i in range(2))
pools = [types.SlotPool(slot_index=i, rank_by=scorer.goal_id,
                        candidates=tuple(offer(i, 10 * i + h)
                                         for h in range(5)))
         for i in range(2)]
found = search.beam(types.SlotProblem(slots=slots), pools,
                    types.DEFAULT_BUDGET, scorer)
for suggestion in found:
    print(" ".join(str(c.handle) for c in suggestion.choices))
'''


def _under_seed(tmp_path: pathlib.Path, seed: str) -> str:
    driver = tmp_path / "across_processes.py"
    driver.write_text(ACROSS_PROCESSES, encoding="utf-8")
    environment = dict(os.environ, PYTHONHASHSEED=seed)
    done = subprocess.run(
        [sys.executable, str(driver), str(REPO)],
        capture_output=True, text=True, env=environment, check=False)
    assert done.returncode == 0, (
        f"the child process under PYTHONHASHSEED={seed} failed:\n"
        f"{done.stderr}")
    return done.stdout


def test_two_processes_under_two_hash_seeds_answer_the_same(tmp_path):
    """QA-059 and QA-142 were both a set iterated into what the player reads.

    Neither could be seen in one process: a set of strings iterates in the
    order the seed gives it, and the seed is fixed for the life of a process.
    So this asks three of them. The assignments are all worth the same, which
    is where an order stops being decided by a figure -- the case would be
    blind on a run where the values settle it.
    """
    answers = {seed: _under_seed(tmp_path, seed)
               for seed in ("0", "1", "12345")}

    lines = answers["0"].splitlines()
    assert len(lines) > 1, (
        f"the child produced {len(lines)} suggestion(s), so there is no "
        f"order here to compare")
    assert len(set(answers.values())) == 1, (
        f"three hash seeds gave {len(set(answers.values()))} different "
        f"orders: {answers}")


# -- AD-009 point 5: a better inventory is never a worse answer -------------

def test_the_best_found_is_the_first_of_the_list():
    """The list is ordered best first, which is what `top_n` means.

    Everything downstream reads the head of it -- `Apply all` applies the
    first, the suggestion blocks draw the first. An order that put the worst
    there would still look like a ranked list.
    """
    problem = types.SlotProblem(slots=slots_of(advisor.RED, advisor.RED))
    worth = {10: 1.0, 11: 2.0, 12: 3.0}
    pools = [pool_of(index, [offer(index, handle, value)
                             for handle, value in worth.items()])
             for index in (0, 1)]

    found = search.beam(problem, pools, types.DEFAULT_BUDGET,
                        adding_scorer(worth))

    assert [s.score.value for s in found] == sorted(
        (s.score.value for s in found), reverse=True)
    assert handles_of(found[0]) == [11, 12]


def test_a_strictly_better_copy_never_lowers_the_best_found(game_data,
                                                            wylder):
    """AD-009 point 5, and the scope it holds in.

    A relic that is strictly better than everything already owned is added,
    and the best score found must not fall. **Measured where the budget
    reaches every assignment** -- five copies in two slots is ten pairs
    against K=20/W=40 -- because AD-003 grants no optimality and therefore no
    monotonicity beyond that: a narrow beam may drop the old best to make room
    for the new one, and a case that claimed otherwise would be claiming a
    guarantee the design refuses.
    """
    rolls = advisor.raising_effects(game_data, wylder, 5)
    poorer = advisor.make_inventory(game_data, wylder, colour=advisor.RED,
                                    count=4, rolls=rolls)
    #: The fifth copy carries two of the effects the others carry one of, so
    #: it is better than any of them by the same arithmetic rather than by
    #: assumption.
    richer = advisor.make_inventory(game_data, wylder, colour=advisor.RED,
                                    count=5,
                                    rolls=rolls[:4] + [rolls[0] + rolls[1]])
    problem = advisor.problem([advisor.RED, advisor.RED])
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))

    before = run_over(poorer, problem, ctx)
    after = run_over(richer, problem, ctx)

    added = candidates.pool(richer, problem, 0, ctx, goals.GOALS,
                            DAMAGE).candidates
    assert types.marginal_for(added[0], DAMAGE) > types.marginal_for(
        added[-1], DAMAGE), (
        "the added copy is not better than what was already owned, so this "
        "case is not measuring monotonicity")
    assert after[0].score.value >= before[0].score.value


# -- AD-006 point 6: stopped between the levels -----------------------------

class Counter:
    """A cancellation check that says yes at a stated level."""

    def __init__(self, stop_at: int | None = None) -> None:
        self.asked = 0
        self.stop_at = stop_at

    def __call__(self) -> bool:
        self.asked += 1
        return self.stop_at is not None and self.asked > self.stop_at


def test_a_run_is_asked_once_before_every_level():
    """AD-003 point 4: between the slot levels, not inside one.

    Inside a level the check would run once per branch -- 20 times as often
    at K=20 -- and AD-006 point 6 costed that out: with six levels the coarse
    reaction time is about a sixth of a run, which is fine, and asking more
    often costs more than it buys.
    """
    problem = types.SlotProblem(slots=slots_of(advisor.RED, advisor.BLUE))
    worth = {10: 1.0, 11: 2.0, 20: 1.0, 21: 2.0}
    pools = [pool_of(0, [offer(0, 10, 1.0), offer(0, 11, 2.0)]),
             pool_of(1, [offer(1, 20, 1.0, advisor.BLUE),
                         offer(1, 21, 2.0, advisor.BLUE)])]
    watch = Counter()

    search.beam(problem, pools, types.DEFAULT_BUDGET, adding_scorer(worth),
                watch)

    assert watch.asked == 2, (
        f"two free slots are two levels and two questions; this run asked "
        f"{watch.asked} times")


def test_a_stopped_run_says_so_instead_of_answering_short():
    """A truncated beam and a finished one are the same shape.

    `Stopped. Nothing was changed.` and a list of suggestions are two states
    of the window (`UI_SPEC` 4.5 against 4.6), and a caller that had to tell
    them apart by counting filled slots would get it wrong on the vessel where
    a slot had nothing to choose from anyway.
    """
    problem = types.SlotProblem(slots=slots_of(advisor.RED, advisor.BLUE))
    worth = {10: 1.0, 20: 1.0}
    pools = [pool_of(0, [offer(0, 10, 1.0)]),
             pool_of(1, [offer(1, 20, 1.0, advisor.BLUE)])]

    with pytest.raises(search.Cancelled, match="1 of 2"):
        search.beam(problem, pools, types.DEFAULT_BUDGET,
                    adding_scorer(worth), Counter(stop_at=1))


# -- the scorer is a parameter ----------------------------------------------

def test_the_search_ranks_by_the_scorer_it_is_handed(game_data, wylder):
    """AD-003: the scorer is a parameter, so AD-002/C stays reachable.

    The two directions of the registry give two answers in two units. If the
    search knew what it was ranking, one of those two could not exist.

    Each direction brings its own pools since D-4: the beam refuses a pool
    list ordered by another direction, so the one thing that varies here is
    the direction, top to bottom. That is a stronger reading of the same
    claim -- the figure now has to come out of the scorer *and* the order it
    branched on has to be the one that scorer would give.
    """
    inventory = advisor.make_inventory(game_data, wylder, colour=advisor.RED,
                                       count=4)
    problem = advisor.problem([advisor.RED])
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))

    by_direction = {}
    for goal_id in (DAMAGE, SURVIVAL):
        pools = candidates.pools(inventory, problem, ctx, goals.GOALS, goal_id)
        scorer = search.goal_scorer(problem, ctx, goals.GOALS[goal_id])
        found = search.beam(problem, pools, types.DEFAULT_BUDGET, scorer)
        by_direction[goal_id] = found[0].score

    assert by_direction[DAMAGE].unit != by_direction[SURVIVAL].unit, (
        f"both directions scored in {by_direction[DAMAGE].unit!r}, so the "
        f"scorer that was handed in cannot be the one that ranked")


# -- preconditions ----------------------------------------------------------

def test_pools_ranked_by_another_direction_are_refused():
    """D-4: the beam branches on an order, so it has to be the right order.

    The two names are the case's own, not the registry's: what is compared
    is one string against another, and a case built on two real goal ids
    could pass because the registry happens to hold them.

    The message has to name both directions. A refusal that said only "the
    pools are wrong" would send the next reader to the pools, and the mistake
    is as often on the other side.
    """
    problem = types.SlotProblem(slots=slots_of(advisor.RED))
    pools = [pool_of(0, [offer(0, 10)], rank_by="what the pools were sorted "
                                                "by")]
    scorer = search.Scorer(goal_id="what the run is ranking",
                           score=tied_scorer().score)

    with pytest.raises(ValueError) as refused:
        search.beam(problem, pools, types.DEFAULT_BUDGET, scorer)

    assert "what the pools were sorted by" in str(refused.value)
    assert "what the run is ranking" in str(refused.value)


def test_pools_and_scorer_of_one_direction_are_accepted():
    """The other half of the refusal above, and it is not decoration.

    A check that refused everything would leave the case above green while
    stopping every run there is. This is the pairing the advisor actually
    makes, and it has to come through.
    """
    problem = types.SlotProblem(slots=slots_of(advisor.RED))
    scorer = adding_scorer({10: 1.0})

    found = search.beam(problem, [pool_of(0, [offer(0, 10, 1.0)],
                                          rank_by=scorer.goal_id)],
                        types.DEFAULT_BUDGET, scorer)

    assert handles_of(found[0]) == [10]


def test_pools_that_are_not_the_free_slots_are_refused():
    """A pool list out of step with the vessel answers the other question.

    The suggestion carries slot indices, and the window puts a copy where they
    point. Pools for the wrong slots would fill the right shape with the wrong
    contents, and every figure in it would look reasonable.
    """
    problem = types.SlotProblem(slots=slots_of(advisor.RED, advisor.BLUE))

    with pytest.raises(ValueError, match=r"\[0, 1\]"):
        search.beam(problem, [pool_of(0, [])], types.DEFAULT_BUDGET,
                    tied_scorer())


@pytest.mark.parametrize("budget", [types.Budget(0, 40), types.Budget(20, 0)])
def test_a_budget_that_searches_nothing_is_refused(budget):
    """An empty answer is already the shape of two other states.

    `every slot is held` and `this run was stopped` both end with nothing to
    show, and the window says something different about each. A budget of zero
    would quietly be read as one of them.
    """
    problem = types.SlotProblem(slots=slots_of(advisor.RED))

    with pytest.raises(ValueError, match="at least 1"):
        search.beam(problem, [pool_of(0, [offer(0, 10)])], budget,
                    tied_scorer())


def test_a_suggestion_the_search_produced_can_be_a_cache_key(game_data,
                                                             wylder):
    """AD-006 point 8: what crosses the thread boundary is hashable.

    Asked of what the search really produced rather than of its annotations:
    a `frozen` dataclass handed a list is frozen in name and shared in fact,
    and the failure would first show in S9 where the key is formed (QA-066).
    """
    inventory = advisor.make_inventory(game_data, wylder, colour=advisor.RED,
                                       count=3)
    problem = advisor.problem([advisor.RED, advisor.RED])
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))

    found = run_over(inventory, problem, ctx)

    assert found, "nothing was suggested, so nothing is being hashed"
    assert len({hash(suggestion) for suggestion in found}) >= 1
    assert dataclasses.replace(found[0], reasons=("a line",)) != found[0]
