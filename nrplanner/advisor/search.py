"""The beam over the free slots: which set of copies is worth most together.

Picking the best relic for each slot on its own is AD-003's option B, and it
is measured wrong exactly where the question gets interesting: two copies of
one `isStrongestEffect` both get chosen and the second is worth nothing, two
effects of one exclusivity group both get chosen and only one applies. The
advisor would then recommend builds whose score it disproves itself. This
module is option C -- a beam of width W over the free slots, branching K wide,
scoring every partial assignment with the real scorer, so the coupling
between the slots is measured instead of assumed.

**It consumes `candidates.pool()`; it computes no marginal contribution of
its own.** What it branches on, and in what order, is the pre-sort's list --
the same list the picker shows (AD-018). A second arithmetic here would be
the duplication AD-018 was written against, and the two views would then be
free to disagree about a figure.

**Levels are the free slots** (S7+, AD-014.2). A held slot is a boundary
condition and never a level, so a vessel with everything held has no level at
all: the loop below runs zero times and hands back the base state, scored.
That is an answer rather than a special case, and there is deliberately no
branch for it -- a branch is a place where the two readings can come apart.

**The copies are the search state** (AD-013 point 2). Every state carries the
handles it has already spent, starting with the ones the held relics occupy
(AD-014.5), and a candidate whose copy is spent is skipped. Without that rule
`Wylder's Urn` yields 40 unusable suggestions out of 40, the best one
included, each with a plausible score and one relic lying in two slots.

**Determinism is a promise here, not a side effect.** This project has twice
shipped a display whose order followed the hash seed of the process (QA-059,
QA-142), and a cache is not checkable against a search that answers one state
two ways (AD-009 point 6). So nothing here iterates a set or a dict: the beam
is a list, the order it is cut down to is a total order over the *content* of
a state -- its value first, then the copies it names -- and not over the
order the states happened to be generated in.

**The scorer is a parameter** (AD-003, S7), so AD-002/C can be hung behind
the same call without touching this file. `goal_scorer` below is the ordinary
one: evaluate the assignment through the one door and ask a goal what it is
worth.

**What this module does not do:** it does not explain itself (S8,
`explain.py`), it does not run in a thread and it holds no cache (S9,
`worker.py`), and it sets no budget -- `Budget` arrives as a parameter and
the `performance-tuner` fills it in S11.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from . import candidates, types
from .evaluate import evaluate
from .types import Cancelled, never_cancelled


@dataclass(frozen=True)
class Scorer:
    """What a search ranks an assignment by, and which direction that is.

    `score` takes the copies chosen so far, in slot order, and gives what
    that build is worth -- see `goal_scorer` for the ordinary one. It is a
    parameter and not a fixed call, so AD-002 option C stays reachable
    without this file changing (AD-003).

    `goal_id` is the whole of D-4, and it travels **with** the callable
    rather than beside it as a second argument to `beam`: a direction handed
    in separately is a third thing that can disagree with the other two, and
    the check below would then compare the pools against a label instead of
    against what really ranks. `goal_scorer` fills it from the goal it was
    given, so the ordinary path cannot mislabel itself.

    This does not tell the search what it is ranking. It tells the search
    whether the two things it was handed name the same direction, which is a
    comparison of two strings and no knowledge of either.
    """

    goal_id: str
    score: Callable[[tuple[types.Candidate, ...]], types.GoalScore]


def goal_scorer(problem: types.SlotProblem, ctx: types.GoalContext,
                goal: types.Goal) -> Scorer:
    """The ordinary scorer: evaluate the assignment, then ask the goal.

    Through `evaluate`, which is the one place under `advisor/` that reaches
    `model.compute` (AD-014.1), so the held slots go into every step of the
    search without this module having to remember them.

    The goal arrives as an object rather than as an id, so nothing here
    imports the registry -- the same reason `candidates.py` gives for taking
    its goals as a parameter (AD-004).
    """
    def score(assignment: tuple[types.Candidate, ...]) -> types.GoalScore:
        return goal.score(evaluate(problem, assignment, ctx), ctx)

    return Scorer(goal_id=goal.id, score=score)


@dataclass(frozen=True)
class _State:
    """One partial assignment the beam is still carrying.

    `spent` is AD-013 point 2's `frozenset[int]`: the copies this branch has
    already used, the held ones included from the start. It is only ever
    asked whether it contains something -- never iterated, because the order a
    set iterates in follows the hash seed of the process and this search
    promises the same answer twice (QA-059, QA-142).
    """

    chosen: tuple[types.Candidate, ...]
    spent: frozenset[int]
    score: types.GoalScore


def _symmetry_group(slot: types.Slot) -> tuple[int, bool]:
    """What makes two free slots interchangeable.

    Colour and Deep together, because those two are exactly what
    `inventory.relics_for` asks before it says what fits: two free slots that
    agree on both are offered the same copies, measured against the same base
    state, in the same order, so choosing `(a, b)` and `(b, a)` for them are
    two spellings of one build.
    """
    return slot.colour, slot.deep


def _floor_in_the_group(state: _State, group: frozenset[int],
                        rank_of: dict[int, int]) -> int:
    """The lowest rank this slot may still take within its symmetry group.

    AD-003 point 2 keeps a group of interchangeable slots to ascending
    candidate order, which is what stops the result list from showing one
    assignment twice with two slots swapped. AD-014.4 is the correction that
    makes it survive a held slot: the group is formed over the **free** slots
    alone, so a hold on the first red slot does not silently forbid the free
    one every candidate that ranks above whatever is being held.

    `max` over what the group has already taken rather than "one more than
    the slot before": a slot that had nothing left to choose from contributes
    nothing to the group, and asking the previous slot alone would then need
    a branch for a state no data can produce.
    """
    taken = [rank_of[choice.handle] for choice in state.chosen
             if choice.slot_index in group]
    return max(taken) + 1 if taken else 0


def _branches(state: _State, offers: Sequence[types.Candidate],
              floor: int, width: int) -> list[types.Candidate]:
    """The first `width` copies this state may still put in this slot.

    The first K **available** ones, not the first K of the list with some of
    them missing (AD-013 point 2): a copy an earlier slot has spent is passed
    over rather than counted, or the branching would narrow at the deeper
    slots -- quietly, and worst where the vessel repeats a colour, which is
    where the ownership rule bites hardest.

    The symmetry floor is read the same way and for the same reason. A
    candidate below it is not a narrower choice, it is the same build already
    reachable with the two slots the other way round.
    """
    out: list[types.Candidate] = []
    for rank, offer in enumerate(offers):
        if rank < floor or offer.handle in state.spent:
            continue
        out.append(offer)
        if len(out) == width:
            break
    return out


def _successors(state: _State, offers: Sequence[types.Candidate], floor: int,
                budget: types.Budget, scorer: Scorer) -> list[_State]:
    """This state, one level deeper. Three outcomes, and each has a reason.

    The ordinary one is a successor per branch. The state itself is never
    among them: the search fills every free slot it can, because leaving one
    empty on purpose is what **holding** it empty says (AD-014.7) -- the
    player's decision, not the search's.

    A slot with nothing left to offer does not end the branch. The state
    carries on with one slot fewer filled, which is what lets a run answer
    `3 of 4 slots filled` (`UI_SPEC` 4.11) instead of answering nothing.

    A slot emptied by the **symmetry floor alone** is the third, and there the
    state is dropped. It is not a build the player could not have; it is this
    build with two interchangeable slots the other way round, which another
    branch is already carrying (AD-003 point 2). Keeping it would put the one
    exception to the rule above on the screen, and it would say `1 of 2 slots
    filled` about a vessel that had a relic for both.
    """
    branches = _branches(state, offers, floor, budget.candidates_per_slot)
    if not branches:
        return [] if _branches(state, offers, 0, 1) else [state]
    grown = []
    for offer in branches:
        chosen = state.chosen + (offer,)
        grown.append(_State(chosen=chosen,
                            spent=state.spent | {offer.handle},
                            score=scorer.score(chosen)))
    return grown


def _order(state: _State) -> tuple[float, tuple[int, ...]]:
    """The total order the beam is cut down by: value first, then the copies.

    Bigger is better for every goal (AD-004), so the value is negated and one
    comparison serves all of them. Ties are the common case rather than the
    exception -- the scaling curves are piecewise linear, so two assignments
    inside one segment are worth exactly the same -- and the handles settle
    those, in slot order.

    The tie-break is over the **content** of a state and not over the order it
    was generated in. Python's sort is stable, so the generation order would
    hold today; it would also make the list the player reads a function of the
    loop above rather than of what is in it, and the next change to that loop
    would move the answer without moving a figure.
    """
    return -state.score.value, tuple(choice.handle for choice in state.chosen)


def _refuse_pools_that_are_not_the_free_slots(
        free: Sequence[types.Slot],
        pools: Sequence[types.SlotPool]) -> None:
    """Refuse pools that are not one per free slot, in the vessel's order.

    Loud rather than forgiving, the way `types.slot_at` is loud: a pool list
    that does not line up with the free slots means the caller and the vessel
    disagree about what is being searched, and the search would answer the
    other question with this question's slot indices.
    """
    wanted = [slot.index for slot in free]
    given = [pool.slot_index for pool in pools]
    if wanted != given:
        raise ValueError(
            f"the search runs over the free slots {wanted} and was handed "
            f"pools for {given}; one pool per free slot, in the vessel's own "
            f"order (AD-003 point 1)")


def _refuse_pools_ranked_by_another_direction(
        pools: Sequence[types.SlotPool], scorer: Scorer) -> None:
    """Refuse pools whose order is not the order this scorer would give.

    D-4. The beam branches on the **head** of each pool -- the first K
    available copies -- and scores what it builds with the scorer it was
    handed. Ranked one way and scored another, it therefore searches the best
    copies of a direction nobody asked about and reports the figure of the one
    that was asked about: same shape, same number of suggestions, no
    complaint. Measured on `Wylder's Chalice` with Deep at the default budget:
    attack rating **290,39 instead of 323,30, 10,2 % worse**, four of the six
    handles different (T-077).

    Loud, and by the same argument as the two refusals around it: the caller
    and the vessel would otherwise disagree about what is being searched, and
    every figure in the answer would look reasonable.
    """
    wrong = sorted({pool.rank_by for pool in pools
                    if pool.rank_by != scorer.goal_id})
    if wrong:
        raise ValueError(
            f"the scorer ranks by {scorer.goal_id!r} and was handed pools "
            f"ordered by {wrong}; the beam branches on the head of each pool, "
            f"so pools and scorer have to mean one direction (D-4)")


def _refuse_a_budget_that_searches_nothing(budget: types.Budget) -> None:
    """Refuse K or W below one.

    Either of them at zero makes the beam empty at the first level, and an
    empty beam is the shape of "this run was stopped" and of "every slot is
    held" -- both of which the window says something about. A budget that
    quietly answers nothing would be read as one of those two.
    """
    if budget.candidates_per_slot < 1 or budget.beam_width < 1:
        raise ValueError(
            f"a search branches at least one candidate wide and keeps at "
            f"least one state, so K and W are at least 1; this budget is "
            f"K={budget.candidates_per_slot}, W={budget.beam_width}")


def beam(problem: types.SlotProblem, pools: Sequence[types.SlotPool],
         budget: types.Budget, scorer: Scorer,
         should_cancel: Callable[[], bool] = never_cancelled
         ) -> tuple[types.Suggestion, ...]:
    """The best complete assignments this budget finds, best first.

    One level per free slot, in the vessel's own order -- AD-003 point 1
    measured that against "narrowest colour first" and found no difference in
    hit quality, so the stable order is the one that is kept. Every level
    branches at most `budget.candidates_per_slot` wide from every state and
    then keeps the best `budget.beam_width` of what came out.

    `pools` are `candidates.pools(...)`, one per free slot and ranked by the
    same direction `scorer` scores in. That the two agree is checked here
    since D-4: a `SlotPool` records the direction that ordered it and a
    `Scorer` the direction it ranks, so the pairing is refused instead of
    being the caller's to keep. It used to be the caller's, and it cost 10,2 %
    of an attack rating without a word (T-077).

    **What comes back is the beam itself**, ordered best first: AD-003 point 5
    asks for the best `top_n` end states, and the width is that number. A
    second cut here would be a second figure to justify, and a caller that
    wants fewer takes the head of the list.

    `should_cancel` is asked **between** the levels and not inside one
    (AD-003 point 4, AD-006 point 6). With six levels and the measured worst
    case that is a reaction time of about a sixth of a run, and checking
    inside a level costs more than it buys.
    """
    free = types.free_slots(problem)
    _refuse_pools_that_are_not_the_free_slots(free, pools)
    _refuse_pools_ranked_by_another_direction(pools, scorer)
    _refuse_a_budget_that_searches_nothing(budget)

    groups: dict[tuple[int, bool], set[int]] = {}
    for slot in free:
        groups.setdefault(_symmetry_group(slot), set()).add(slot.index)

    live = [_State(chosen=(), spent=types.held_handles(problem),
                   score=scorer.score(()))]
    for level, slot in enumerate(free):
        if should_cancel():
            raise Cancelled(
                f"stopped after {level} of {len(free)} slots")
        offers = candidates.shortlist(pools[level], budget, len(free))
        rank_of = {offer.handle: rank for rank, offer in enumerate(offers)}
        group = frozenset(groups[_symmetry_group(slot)])
        grown: list[_State] = []
        for state in live:
            grown.extend(_successors(
                state, offers, _floor_in_the_group(state, group, rank_of),
                budget, scorer))
        grown.sort(key=_order)
        live = grown[:budget.beam_width]

    return tuple(
        types.Suggestion(
            choices=tuple(types.SlotChoice(slot_index=choice.slot_index,
                                           handle=choice.handle,
                                           relic_id=choice.relic_id,
                                           name=choice.name)
                          for choice in state.chosen),
            score=state.score)
        for state in live
    )
