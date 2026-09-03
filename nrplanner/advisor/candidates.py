"""What the player owns, turned into what may go into one slot -- and what it
is worth there.

**The pre-sort is the product, not a step towards one** (S5++, AD-018). The
same list answers both of the advisor's questions: the picker shows it -- "what
does *this* relic do for me *now*" -- and the beam search consumes it. One
calculation, two views, so the two cannot disagree about a figure
(checkpoint 15).

**What a candidate is worth is its marginal contribution against the base
state**, `goal(evaluate(base + candidate)) - goal(evaluate(base))`, and never
its value in isolation and never against the empty build (AD-014.3, AD-018.1,
do-not rule 13). Isolated pre-sorting is what makes an advisor recommend a
buff a held relic already caps: the score does not move and the suggestion
still looks plausible.

**The base state of a slot is the current build with that slot emptied** --
including for the relic already sitting in it (AD-018.1, `UI_SPEC` §3.2). Any
other reference point makes "+12.4" a number about a build the player is not
in.

**No role dedup** (AD-013). A candidate is a copy, identified by its handle.
The `architect` measured it against the real inventory on 2026-09-01: 309
copies carry 306 distinct rolls, so collapsing them saves one per cent and
gives up exactly the identity that a suggestion has to be tradeable on. A copy
already held is not offered again (AD-014.5), and a copy with no handle is not
offered at all and is reported instead (AD-013 point 4).

**Scope of this module:** it ranks one slot at a time and knows nothing about
what several slots are worth together. Two relics that only pay off beside
each other are invisible to it -- that is the beam search's question (S7), and
the sentence the player has to be shown about it is `UI_SPEC` §3.2 line 4, not
something this module can make true.

This module imports no registry. The goals it scores under arrive as a
parameter, so a third goal reaches the pre-sort without a line changing here
(AD-004).
"""

from __future__ import annotations

import dataclasses
from collections.abc import Mapping

from . import types
from .evaluate import evaluate


def base_state_for(problem: types.SlotProblem,
                   slot_index: int) -> types.SlotProblem:
    """`problem` with the hold on one slot lifted -- that slot's base state.

    For a slot that is already free this is `problem` unchanged, which is the
    Optimize case. For a slot the player is holding -- and in the picker every
    slot but the open one is held, held by the player or not (AD-018.1) -- it
    is the build without whatever sits in that slot.

    That single rule covers both questions, and it is what makes the relic
    currently in the slot comparable with the ones that might replace it:
    measured against a base state that still contained it, it would be
    competing with itself and would score nothing.
    """
    if slot_index not in {slot.index for slot in problem.slots}:
        raise KeyError(f"this vessel has no slot {slot_index}")
    kept = tuple(entry for entry in problem.held if entry.index != slot_index)
    return dataclasses.replace(problem, held=kept)


def _offer(slot: types.Slot, relic) -> types.Candidate:
    """One owned copy as a candidate for this slot, before it is measured."""
    return types.Candidate(
        slot_index=slot.index,
        handle=relic.handle,
        relic_id=relic.relic_id,
        name=relic.name,
        colour=relic.colour,
        is_deep=relic.is_deep,
        effect_ids=tuple(relic.effect_ids),
        curse_ids=tuple(relic.curse_ids),
    )


def _without_a_handle_line(count: int) -> str:
    """The A7 line for copies this save cannot tell apart (AD-013 point 4)."""
    one = count == 1
    return (f"{count} owned {'relic' if one else 'relics'} of this colour "
            f"{'is' if one else 'are'} not offered: this save carries no "
            f"handle for {'it' if one else 'them'}, so one copy cannot be "
            f"told from another and a suggestion naming one could not be "
            f"applied to a slot.")


def pool(inventory, problem: types.SlotProblem, slot_index: int,
         ctx: types.GoalContext, goals: Mapping[str, types.Goal],
         rank_by: str) -> types.SlotPool:
    """Every relic that may go into one slot, best first under `rank_by`.

    The colour rule -- and with it "a white slot draws every colour" -- is
    `inventory.relics_for`'s, asked rather than restated, so the advisor and
    the picker's own list cannot come to differ about what fits. The Deep
    separation rides along in the same call: a Deep slot takes Deep relics and
    an ordinary slot takes ordinary ones.

    Every goal in `goals` is scored for every candidate, whichever one
    `rank_by` names. Scoring a finished build a second time is two function
    calls over fields that already exist -- `model.compute` is the expensive
    part and it has already run -- so the second figure is effectively free,
    and OF-13 needs it: a cost has to be shown in its own unit rather than
    converted into a foreign one (AD-023).

    Ties are the common case, not the exception: the scaling curves are
    piecewise linear, so two candidates inside one segment are worth exactly
    the same (`tests/test_marginal_returns.py`). The order therefore breaks
    ties by name and then by handle, or two runs over one inventory would
    hand back rows in different orders and the player could not tell why.
    """
    if rank_by not in goals:
        raise KeyError(f"nothing ranks by goal {rank_by!r}; this run knows "
                       f"{sorted(goals)}")
    slot = types.slot_at(problem, slot_index)
    base_problem = base_state_for(problem, slot_index)
    base_build = evaluate(base_problem, (), ctx)
    baseline = {goal_id: goal.score(base_build, ctx).value
                for goal_id, goal in goals.items()}
    taken = types.held_handles(base_problem)

    offered = inventory.relics_for(slot.colour, slot.deep)
    without_handle = sum(1 for relic in offered if relic.handle is None)

    measured: list[types.Candidate] = []
    for relic in offered:
        if relic.handle is None or relic.handle in taken:
            continue
        candidate = _offer(slot, relic)
        build = evaluate(base_problem, (candidate,), ctx)
        marginals = tuple(
            types.Marginal(goal_id, goal.score(build, ctx).value
                           - baseline[goal_id])
            for goal_id, goal in goals.items()
        )
        measured.append(dataclasses.replace(candidate, marginals=marginals))

    measured.sort(key=lambda offer: (-types.marginal_for(offer, rank_by),
                                     offer.name, offer.handle))
    unknowns = ((_without_a_handle_line(without_handle),)
                if without_handle else ())
    return types.SlotPool(
        slot_index=slot_index,
        baseline=tuple(types.Baseline(goal_id, value)
                       for goal_id, value in baseline.items()),
        candidates=tuple(measured),
        unknowns=unknowns,
    )


def pools(inventory, problem: types.SlotProblem, ctx: types.GoalContext,
          goals: Mapping[str, types.Goal],
          rank_by: str) -> tuple[types.SlotPool, ...]:
    """One pool per **free** slot, in the vessel's own order.

    Held slots get no pool: they are a boundary condition and the search does
    not run over them (AD-014 point 2). With every slot held this is empty,
    and that is an answer rather than a failure -- the run's result is then
    the current build, evaluated.
    """
    return tuple(pool(inventory, problem, slot.index, ctx, goals, rank_by)
                 for slot in types.free_slots(problem))


def shortlist(slot_pool: types.SlotPool, budget: types.Budget,
              free_slot_count: int) -> tuple[types.Candidate, ...]:
    """The head of a pool that the beam search may branch on (S5+, AD-013.3).

    `K + (free slots - 1)` entries, not `K`. The search skips candidates whose
    copy an earlier slot has already taken, and it has to be able to take the
    first K **available** ones rather than the first K of the list with some
    of them missing -- otherwise the branching quietly narrows at the deeper
    slots, exactly where the vessel repeats a colour and the ownership rule
    bites hardest. In the worst case the other free slots have taken one copy
    each, which is `free slots - 1` of them.

    Shorter than that only when the pool itself is shorter, in which case
    there is nothing to leave out. This is a **cut for the search**; the
    picker shows `SlotPool.candidates` whole, because the player asked what
    each relic they own is worth, not what the first twenty are worth.
    """
    if free_slot_count < 1:
        raise ValueError("a shortlist is for a slot the search may fill, so "
                         "there is at least one free slot")
    room = budget.candidates_per_slot + free_slot_count - 1
    return slot_pool.candidates[:room]
