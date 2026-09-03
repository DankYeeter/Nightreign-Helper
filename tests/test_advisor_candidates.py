"""What may go into a slot, and what it is worth there.

The sharp claim in this file is not that a red slot gets red relics. It is
**against what** a candidate is measured (AD-014.3, AD-018.1):

* against the held build, not against nothing -- otherwise the advisor
  recommends a buff the held relic already caps, the score does not move, and
  the suggestion still looks plausible. `isStrongestEffect` is what makes that
  visible: two copies of such an effect are worth exactly one, so a candidate
  carrying it is worth zero beside a held relic that carries it and something
  beside a build that does not;
* against the build with **this slot emptied**, including for the relic
  already sitting in it -- or the relic in the slot would be competing with
  itself and would score nothing.

The other claims are AD-013's: a candidate is a copy, not a role; a copy the
save gives no handle for is not offered and is reported; a copy already held
is not offered again. On a vessel with repeated slot colours the last of those
is the difference between forty usable suggestions and none.
"""

from __future__ import annotations

import pytest

from nrplanner.advisor import candidates, goals, types
from nrplanner.advisor.evaluate import evaluate

from tests import advisor_cases as advisor
from tests import weapon_damage_cases as cases

DAMAGE = "max_damage"
SURVIVAL = "min_damage_taken"


@pytest.fixture(scope="module")
def wylder(game_data):
    return cases.hero_by_name(game_data, "Wylder")


def pool_for(inventory, problem, slot_index, ctx, rank_by=DAMAGE):
    return candidates.pool(inventory, problem, slot_index, ctx, goals.GOALS,
                           rank_by)


def names(pool: types.SlotPool) -> list[str]:
    return [candidate.name for candidate in pool.candidates]


def handles(pool: types.SlotPool) -> list[int]:
    return [candidate.handle for candidate in pool.candidates]


# -- who is offered ---------------------------------------------------------

def test_a_coloured_slot_is_offered_only_its_own_colour(game_data, wylder):
    inventory = advisor.make_inventory(game_data, wylder, colour=advisor.RED,
                                       count=3, other_colour=advisor.BLUE)
    problem = advisor.problem([advisor.RED])
    ctx = advisor.context(game_data, wylder)

    pool = pool_for(inventory, problem, 0, ctx)

    assert len(pool.candidates) == 3
    assert {candidate.colour for candidate in pool.candidates} == {advisor.RED}


def test_a_white_slot_draws_every_colour(game_data, wylder):
    """The wildcard rule, asked of `inventory.relics_for` and not restated.

    A white slot is where the pre-sort carries the most weight: the
    `architect` counted 205 candidates for one against 21-55 for a coloured
    slot (AD-003, measured 2026-09-01 against the real inventory), so a
    filter that quietly read a white slot as its own colour would cost most
    exactly where it hurts most.
    """
    inventory = advisor.make_inventory(game_data, wylder, colour=advisor.RED,
                                       count=3, other_colour=advisor.BLUE)
    problem = advisor.problem([advisor.WHITE])
    ctx = advisor.context(game_data, wylder)

    pool = pool_for(inventory, problem, 0, ctx)

    assert {candidate.colour for candidate in pool.candidates} == \
        {advisor.RED, advisor.BLUE}


def test_a_deep_slot_and_an_ordinary_slot_see_different_relics(game_data,
                                                               wylder):
    """Deep of Night is a separation, not a filter on top of one."""
    inventory = advisor.make_inventory(game_data, wylder, colour=advisor.RED,
                                       count=2, deep_count=2)
    ctx = advisor.context(game_data, wylder)

    ordinary = pool_for(inventory, advisor.problem([advisor.RED]), 0, ctx)
    deep = pool_for(inventory, advisor.problem([advisor.RED], deep=True), 0,
                    ctx)

    assert len(ordinary.candidates) == 2
    assert len(deep.candidates) == 2
    assert not set(handles(ordinary)) & set(handles(deep))
    assert all(candidate.is_deep for candidate in deep.candidates)
    assert not any(candidate.is_deep for candidate in ordinary.candidates)


def test_a_copy_without_a_handle_is_not_offered_and_is_reported(game_data,
                                                                wylder):
    """AD-013 point 4, both halves.

    Taking it silently would give up copy identity for exactly the relics
    whose identity cannot be checked; dropping it silently would leave the
    player looking for a relic they own and cannot find in the list.
    """
    inventory = advisor.make_inventory(game_data, wylder, count=3,
                                       handles=[10, None, 12])
    problem = advisor.problem([advisor.RED])
    ctx = advisor.context(game_data, wylder)

    pool = pool_for(inventory, problem, 0, ctx)

    # A set rather than a sorted list: with a handle-less copy in the pool,
    # sorting mixes None with ints and the case would die of a TypeError
    # instead of of the thing it is about.
    assert set(handles(pool)) == {10, 12}
    assert pool.unknowns, "a relic left out has to be said out loud (A7)"
    assert any("handle" in line for line in pool.unknowns)


def test_nothing_left_out_says_nothing(game_data, wylder):
    """The pool's `unknowns` reports what happened, not a standing warning.

    The guarantee that a run always says *something* is on `GoalScore`, which
    is where A7 lives; a pool that always printed a line would be the static
    warning AD-010 rejected.
    """
    inventory = advisor.make_inventory(game_data, wylder, count=2)
    ctx = advisor.context(game_data, wylder)

    assert pool_for(inventory, advisor.problem([advisor.RED]), 0,
                    ctx).unknowns == ()


def test_a_held_copy_is_not_offered_a_second_time(game_data, wylder):
    """AD-014.5. On a vessel with two slots of one colour this is the
    difference between forty usable suggestions and none (AD-013, measured on
    `Wylder's Urn`)."""
    inventory = advisor.make_inventory(game_data, wylder, count=3)
    held = inventory.relics[0]
    problem = advisor.problem([advisor.RED, advisor.RED],
                              held={0: advisor.held_relic(held)})
    ctx = advisor.context(game_data, wylder)

    pool = pool_for(inventory, problem, 1, ctx)

    assert held.handle not in handles(pool)
    assert len(pool.candidates) == 2


def test_two_copies_of_one_roll_are_two_candidates(game_data, wylder):
    """AD-013: no role dedup, because the candidate is the copy.

    The `architect` measured it on 2026-09-01: 309 copies carry 306 distinct
    rolls, so collapsing them saves one per cent and gives up the identity a
    suggestion has to be tradeable on.
    """
    roll = advisor.raising_effects(game_data, wylder, 1)[0]
    inventory = advisor.make_inventory(game_data, wylder, count=2,
                                       rolls=[roll, list(roll)])
    ctx = advisor.context(game_data, wylder)

    pool = pool_for(inventory, advisor.problem([advisor.RED]), 0, ctx)

    assert len(pool.candidates) == 2
    assert len(set(handles(pool))) == 2


# -- what a candidate is measured against -----------------------------------

def test_a_candidate_is_measured_against_the_held_build(game_data, wylder):
    """AD-014.3 and do-not rule 13, in the one shape that can tell them apart.

    The effect is one the game refuses to count twice. Held in slot 0 it is
    already at full value, so a second copy of it adds **nothing** -- and a
    pre-sort run against the empty build would put that same second copy at
    the top of the list.
    """
    capped = advisor.a_non_stacking_effect(game_data, wylder, "maxHpRate")
    inventory = advisor.make_inventory(game_data, wylder, count=2,
                                       rolls=[[capped], [capped]])
    first, second = inventory.relics
    ctx = advisor.context(game_data, wylder)
    slots = [advisor.RED, advisor.RED]

    free = pool_for(inventory, advisor.problem(slots), 1, ctx, SURVIVAL)
    holding = pool_for(inventory,
                       advisor.problem(slots,
                                       held={0: advisor.held_relic(first)}),
                       1, ctx, SURVIVAL)

    alone = types.marginal_for(
        next(c for c in free.candidates if c.handle == second.handle),
        SURVIVAL)
    beside_it = types.marginal_for(
        next(c for c in holding.candidates if c.handle == second.handle),
        SURVIVAL)

    assert alone > 0, "the case needs an effect that is worth something alone"
    assert beside_it == pytest.approx(0.0), (
        "a candidate the held relic already caps must be worth nothing; it "
        "was measured against the wrong base state")


def test_the_base_state_of_a_slot_is_the_build_with_that_slot_emptied(
        game_data, wylder):
    """AD-018.1 and `UI_SPEC` §3.2: "ranked against your build with slot N
    empty".

    Every other slot stays held. Without the emptying, the relic in the slot
    would be measured against a build that already contains it -- and the one
    number the player most wants, "is what I have in there any good", would
    be zero for every relic they already own.
    """
    inventory = advisor.make_inventory(game_data, wylder, count=3)
    sitting, other = inventory.relics[0], inventory.relics[1]
    problem = advisor.problem(
        [advisor.RED, advisor.RED],
        held={0: advisor.held_relic(sitting),
              1: advisor.held_relic(other)})
    ctx = advisor.context(game_data, wylder)

    pool = pool_for(inventory, problem, 0, ctx, SURVIVAL)
    emptied = candidates.base_state_for(problem, 0)

    assert types.baseline_for(pool, SURVIVAL) == pytest.approx(
        goals.GOALS[SURVIVAL].score(evaluate(emptied, (), ctx), ctx).value)
    assert sitting.handle in handles(pool), (
        "the relic already in the slot has to be offered for it, or it "
        "cannot be compared with what would replace it")
    assert other.handle not in handles(pool), (
        "the other slot is still held, so its copy is still taken")


def test_the_relic_in_the_slot_is_worth_what_it_actually_adds(game_data,
                                                             wylder):
    """The picker's own number for the relic the player already has in.

    It is measured from the same base state as every rival, so the comparison
    is a comparison. Against a base state that still held it, it would score
    zero and read as worthless.

    Ranked by damage, because these copies carry Strength effects and the
    reference armament scales on Strength: a goal the roll does not touch
    would put every candidate at zero and the assertion would say nothing.
    """
    inventory = advisor.make_inventory(game_data, wylder, count=2)
    sitting = inventory.relics[0]
    problem = advisor.problem([advisor.RED],
                              held={0: advisor.held_relic(sitting)})
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))

    pool = pool_for(inventory, problem, 0, ctx, DAMAGE)
    itself = next(c for c in pool.candidates if c.handle == sitting.handle)

    assert types.marginal_for(itself, DAMAGE) > 0


def test_every_candidate_carries_both_directions(game_data, wylder):
    """AD-018 point 2 and AD-023/OF-13: two figures, never one weighted one.

    There is no conversion between damage dealt and damage survived, so a
    cost is named in its own unit rather than converted into a foreign one.
    Scoring the finished build a second time is two function calls over
    fields that already exist.
    """
    inventory = advisor.make_inventory(game_data, wylder, count=2)
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))

    pool = pool_for(inventory, advisor.problem([advisor.RED]), 0, ctx)

    for candidate in pool.candidates:
        assert {marginal.goal_id for marginal in candidate.marginals} == \
            set(goals.GOALS)
    assert {baseline.goal_id for baseline in pool.baseline} == set(goals.GOALS)


# -- order ------------------------------------------------------------------

def test_the_order_is_the_ranking_goals_order(game_data, wylder):
    inventory = advisor.make_inventory(game_data, wylder, count=4)
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))

    pool = pool_for(inventory, advisor.problem([advisor.RED]), 0, ctx, DAMAGE)
    gains = [types.marginal_for(c, DAMAGE) for c in pool.candidates]

    assert gains == sorted(gains, reverse=True)


def test_two_runs_over_one_inventory_agree_about_a_tie(game_data, wylder):
    """Ties are the common case, not the exception.

    The scaling curves are piecewise linear, so two candidates inside one
    segment are worth exactly the same (`test_marginal_returns.py`). Without
    a second key their order would follow whatever `relics_for` handed over,
    and two runs could disagree about rows the player cannot tell apart --
    the same reasoning as do-not rule 29 for the armament ranking.
    """
    roll = advisor.raising_effects(game_data, wylder, 1)[0]
    inventory = advisor.make_inventory(game_data, wylder, count=4,
                                       rolls=[roll] * 4)
    ctx = advisor.context(game_data, wylder)
    problem = advisor.problem([advisor.RED])

    first = pool_for(inventory, problem, 0, ctx, SURVIVAL)
    again = pool_for(inventory, problem, 0, ctx, SURVIVAL)
    tied = {types.marginal_for(c, SURVIVAL) for c in first.candidates}

    assert len(tied) == 1, "the case needs candidates that really tie"
    assert handles(first) == handles(again)
    assert names(first) == sorted(names(first))


def test_ranking_by_a_goal_nobody_scored_is_refused(game_data, wylder):
    inventory = advisor.make_inventory(game_data, wylder, count=1)
    ctx = advisor.context(game_data, wylder)

    with pytest.raises(KeyError):
        pool_for(inventory, advisor.problem([advisor.RED]), 0, ctx,
                 "invented")


# -- what the search gets ---------------------------------------------------

def test_pools_are_built_for_the_free_slots_only(game_data, wylder):
    """A held slot is a boundary condition; the search does not run over it."""
    inventory = advisor.make_inventory(game_data, wylder, count=3)
    problem = advisor.problem(
        [advisor.RED, advisor.RED, advisor.RED],
        held={0: advisor.held_relic(inventory.relics[0]), 2: None})
    ctx = advisor.context(game_data, wylder)

    built = candidates.pools(inventory, problem, ctx, goals.GOALS, SURVIVAL)

    assert [pool.slot_index for pool in built] == [1]


def test_every_slot_held_leaves_nothing_to_search(game_data, wylder):
    """AD-014 point 2: not an error, an answer -- the build as it stands."""
    inventory = advisor.make_inventory(game_data, wylder, count=1)
    problem = advisor.problem(
        [advisor.RED], held={0: advisor.held_relic(inventory.relics[0])})
    ctx = advisor.context(game_data, wylder)

    assert candidates.pools(inventory, problem, ctx, goals.GOALS,
                            SURVIVAL) == ()


def test_the_shortlist_leaves_room_for_the_copies_the_other_slots_take(
        game_data, wylder):
    """S5+/AD-013.3: `K + (free slots - 1)`, not `K`.

    The search skips candidates whose copy an earlier slot has taken and then
    takes the first K **available**. With a list only K long, every copy taken
    elsewhere narrows the branching at the deeper slots -- silently, and worst
    where the vessel repeats a colour, which is where the ownership rule bites
    hardest.
    """
    inventory = advisor.make_inventory(game_data, wylder, count=6)
    ctx = advisor.context(game_data, wylder)
    pool = pool_for(inventory, advisor.problem([advisor.RED] * 3), 0, ctx,
                    SURVIVAL)
    budget = types.Budget(candidates_per_slot=2, beam_width=4)

    assert len(candidates.shortlist(pool, budget, 3)) == 4
    assert len(candidates.shortlist(pool, budget, 1)) == 2
    assert candidates.shortlist(pool, budget, 3) == pool.candidates[:4]


def test_the_picker_number_and_the_search_pre_sort_are_one_number(game_data,
                                                                  wylder):
    """Checkpoint 15: two views, one figure, and not two that agree.

    The shortlist is a slice of the very list the picker shows -- the same
    objects, not a second computation over the same inputs -- so the two
    cannot come to disagree about what a candidate is worth. If this
    assertion ever needed a tolerance, there would be two calculations again
    and S5++ would have quietly been undone.
    """
    inventory = advisor.make_inventory(game_data, wylder, count=4)
    ctx = advisor.context(game_data, wylder)
    pool = pool_for(inventory, advisor.problem([advisor.RED] * 2), 0, ctx,
                    SURVIVAL)

    short = candidates.shortlist(pool, types.Budget(candidates_per_slot=2,
                                                    beam_width=4), 2)

    assert len(short) == 3
    assert all(taken is shown for taken, shown in zip(short, pool.candidates))


def test_a_shortlist_shorter_than_the_room_is_the_whole_pool(game_data,
                                                             wylder):
    inventory = advisor.make_inventory(game_data, wylder, count=2)
    ctx = advisor.context(game_data, wylder)
    pool = pool_for(inventory, advisor.problem([advisor.RED]), 0, ctx,
                    SURVIVAL)

    assert candidates.shortlist(pool, types.DEFAULT_BUDGET, 1) == \
        pool.candidates


def test_a_pool_the_advisor_produced_can_be_a_cache_key(game_data, wylder):
    """QA-066 on the producing side, not only on the declared shape.

    A frozen dataclass whose field is handed a dict is frozen in name and
    shared in fact, and the failure only shows where a marginal contribution
    is memoised (AD-018). Hashing what the pool really produced is the half
    that an annotation cannot claim.
    """
    inventory = advisor.make_inventory(game_data, wylder, count=2)
    ctx = advisor.context(game_data, wylder)

    pool = pool_for(inventory, advisor.problem([advisor.RED]), 0, ctx,
                    SURVIVAL)

    hash(pool)
    for candidate in pool.candidates:
        hash(candidate)
    hash(candidates.base_state_for(advisor.problem([advisor.RED]), 0))
