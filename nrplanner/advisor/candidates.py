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

**What a pool reports about itself** are run findings and only those
(AD-025.2): the copies this save gives no handle for, the candidates whose
effect no total counted, and the candidates whose damage-type conversion this
figure has no place for (QA-113). Each carries a count, so each belongs to the
run rather than to the method. What the *direction* cannot know whatever the
run stands in `Goal.scope` and is read from there; six pools of a Deep vessel
repeating it six times is the noise AK-50 is written against. The one thing
the pool does carry from a direction is what that direction found out about
**this** run -- `Baseline.unknowns` and `weights_note`, which stopped at this
boundary until T-048 (QA-102).

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

from .. import model
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


def _without_a_handle_line(count: int, slot: types.Slot) -> str:
    """The A7 line for copies this save cannot tell apart (AD-013 point 4).

    One sentence, two fillings for the one place they differ (AK-67). The
    line used to say "of this colour" at every slot, and at a white one that
    is a claim about the count that is not true: `inventory.relics_for` offers
    a white slot relics of **every** colour, so a copy of any colour can fall
    through the same handle gap. The number was always right -- it summed over
    whatever the slot actually offers -- and only the description of what had
    been counted was wrong (QA-108).
    """
    one = count == 1
    reach = "any" if slot.colour == model.WHITE_SLOT else "this"
    return (f"{count} owned {'relic' if one else 'relics'} of {reach} colour "
            f"{'is' if one else 'are'} not offered: this save carries no "
            f"handle for {'it' if one else 'them'}, so one copy cannot be "
            f"told from another and a suggestion naming one could not be "
            f"applied to a slot.")


def _conditional_line(count: int) -> str:
    """The A7 line for candidates whose effect no total counted (AD-004).

    Without it a player sees a strong situational relic sitting at `0.00`
    and concludes the advisor is broken -- which is the reason AD-004 gives
    for the line existing at all.

    Wording and count are settled and they do not describe the same set: the
    sentence says "your relics" (AK-67, verbatim), while the count is over the
    candidates **this pool** offers -- already narrowed by colour and by Deep,
    the same population the handle line above counts over. The
    `ui-ux-designer` decided it that way with both halves in view; the two
    lines of one field would otherwise count over two different totals.
    """
    one = count == 1
    carry = ("carries an effect that only applies" if one
             else "carry effects that only apply")
    return (f"{count} of your relics {carry} under a condition. "
            f"{'It was' if one else 'They were'} not counted.")


def _brought_an_uncounted_condition(build: model.Build,
                                    candidate: types.Candidate) -> bool:
    """Did this candidate bring an effect the calculation left out?

    Read off `Build.situational` -- what `model.compute` actually parked --
    and not off the relic's definition, which is the discipline AD-015 states
    for curses: a condition the calculation *did* apply must not be shown as
    though it had not. Declaring the condition live is exactly what tells the
    two apart, and only the build knows it. A second reading over the effect
    records would also need the weapon type worked out a second time, and a
    second opinion about what was counted is worth less than no line at all.

    **Scope, because a count without one is read as a count of everything:**
    `Build.situational` holds the conditions the player can declare, so an
    effect gated on an armament class this build is not carrying is not in
    here and is not counted. That case is QA-104 and gets a line of its own;
    one figure standing for two different states would be worse than the
    silence it replaced.
    """
    brought = set(candidate.effect_ids) | set(candidate.curse_ids)
    return any(entry.effect_id in brought and not entry.live
               for entry in build.situational)


def _unmodelled_conversion_line(count: int) -> str:
    """The A7 line for candidates whose conversion this figure cannot use.

    The counterpart of the scope sentence in `MAX_DAMAGE.scope`: the sentence
    says the figure does not carry a damage-type conversion, and this says how
    many of the relics in front of the player are affected by that (AD-025,
    QA-113).

    Wording settled by AK-67 on 2026-09-05 and written out verbatim. It stood
    behind a `[wording pending: QA-113]` marker from T-048 until then, because
    the decision of that morning settled the field's other two lines and named
    neither this one nor its subject.

    The four elements are spelled out because QA-113 is a closed set of four
    relics, not an example from an open one -- unlike the conditional line
    above, where naming a condition would have to hold for every relic it
    counts. The sentence claims no size and no direction: what the difference
    would be can only come from a reading in the running game.
    """
    one = count == 1
    return (f"{count} of your relics {'changes' if one else 'change'} what "
            f"damage type your starting armament deals (to magic, fire, "
            f"lightning, or holy). This figure does not count that change.")


def _converts_a_damage_type(candidate: types.Candidate,
                            ctx: types.GoalContext) -> bool:
    """Does this candidate carry a field the attack rating has no place for?

    `model.FLAT_ATTACK_POWER_FIELDS` names them, and the model naming them is
    the point: the criterion is "the calculation has no compartment for this",
    which only the calculation can say. Read off the effect records rather
    than off the build, and that is not the shortcut do-not rule 36 forbids --
    a conditional effect is one `model.compute` **parked**, and a build can be
    asked what it parked, but a field nothing reads leaves no trace in a
    build at all. There is nothing here to ask.
    """
    known = ctx.data["effects"]
    for effect_id in tuple(candidate.effect_ids) + tuple(candidate.curse_ids):
        effect = known.get(str(effect_id))
        modifiers = (effect or {}).get("modifiers") or {}
        if any(name in modifiers for name in model.FLAT_ATTACK_POWER_FIELDS):
            return True
    return False


def _pool_findings(slot: types.Slot, without_handle: int, conditional: int,
                   converting: int) -> tuple[str, ...]:
    """What this pool left out, in the player's language (AD-025.2).

    Every line carries a count, so every one of them is a finding of this run
    rather than a statement about the method, and each is absent when its
    count is zero: "nothing was left out" is said by there being no line, not
    by a line saying so. The procedural sentences are not here at all -- they
    are the registry's, drawn once for the screen instead of once per pool.

    A relic can be named by more than one of these lines, and that is
    intended: the reasons are different, and one of them arriving would not
    make the others untrue.

    The order is fixed and AK-67 gives its reason: the handle line names
    candidates that were **never** counted, the conditional line names ones
    that were counted and then set to zero -- rising order of how far into the
    calculation the relic got. The conversion line sits behind both on the
    same reading: those relics are in the pool and were counted, and it is a
    missing kind of arithmetic rather than a condition that zeroed them.

    The slot is taken rather than the colour alone because the handle line
    asks about the reach of `inventory.relics_for`, which is a property of the
    slot and not of a number.
    """
    lines = []
    if without_handle:
        lines.append(_without_a_handle_line(without_handle, slot))
    if conditional:
        lines.append(_conditional_line(conditional))
    if converting:
        lines.append(_unmodelled_conversion_line(converting))
    return tuple(lines)


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

    The base state is scored once per direction and the **whole** answer is
    kept: `Baseline` carries the figure and, beside it, what that direction
    could not know about this run. Taking only the figure is what left the
    picker -- the one path the player uses -- with no A7 line at all
    (QA-102, checkpoint 32).
    """
    if rank_by not in goals:
        raise KeyError(f"nothing ranks by goal {rank_by!r}; this run knows "
                       f"{sorted(goals)}")
    slot = types.slot_at(problem, slot_index)
    base_problem = base_state_for(problem, slot_index)
    base_build = evaluate(base_problem, (), ctx)
    # The whole answer, not only its number: what a direction could not know
    # about *this* run is the half that used to stop at the pool boundary
    # (QA-102). The procedural half is not here and must not be -- it is read
    # off the registry, once for the screen (AD-025).
    base_scores = {goal_id: goal.score(base_build, ctx)
                   for goal_id, goal in goals.items()}
    taken = types.held_handles(base_problem)

    offered = inventory.relics_for(slot.colour, slot.deep)
    without_handle = sum(1 for relic in offered if relic.handle is None)

    measured: list[types.Candidate] = []
    conditional = 0
    converting = 0
    for relic in offered:
        if relic.handle is None or relic.handle in taken:
            continue
        candidate = _offer(slot, relic)
        build = evaluate(base_problem, (candidate,), ctx)
        if _brought_an_uncounted_condition(build, candidate):
            conditional += 1
        if _converts_a_damage_type(candidate, ctx):
            converting += 1
        marginals = tuple(
            types.Marginal(goal_id, goal.score(build, ctx).value
                           - base_scores[goal_id].value)
            for goal_id, goal in goals.items()
        )
        measured.append(dataclasses.replace(candidate, marginals=marginals))

    measured.sort(key=lambda offer: (-types.marginal_for(offer, rank_by),
                                     offer.name, offer.handle))
    return types.SlotPool(
        slot_index=slot_index,
        baseline=tuple(types.Baseline(goal_id, score.value, score.unit,
                                      score.unknowns, score.weights_note)
                       for goal_id, score in base_scores.items()),
        candidates=tuple(measured),
        unknowns=_pool_findings(slot, without_handle, conditional,
                                converting),
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
