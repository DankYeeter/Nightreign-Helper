"""One question to the advisor, answered whole -- and the memo of the answer.

Everything above this module answers a part of the question: `candidates.py`
what may go into one slot, `search.py` which set of copies is worth most
together, `explain.py` what to say about it. This is where the three become
the one `AdvisorResult` the window draws (AD-010), and where the answer is
kept in case the same question is asked again (AD-007).

**Qt-free, like everything below it** (AD-001). The thread is `worker.py`'s
and nothing here knows about it: a run is a function call that takes a
`should_cancel` and may raise `search.Cancelled`. That is what lets the whole
answer -- not merely the search -- be checked on a machine with no display.

**The cache is a speed-up and never a second way to compute** (AD-007). A hit
is the very object a fresh run produced, with one field changed: the
generation, which belongs to the asking and not to the answer. Everything a
run reads is therefore in the key, and the key is the `AdvisorRequest`
itself -- there is no second key form that could drift from the state it
stands for (`types.py`). What keeps that true is not care but
`_refuse_a_request_that_asks_about_another_run`: a request whose fields
disagree with the material handed in beside them is refused, because a key
that does not describe the run is a hit on the wrong answer.

**What crosses into the thread is frozen** (AD-006 point 8), which is why
`frozen_inventory` is here rather than in `worker.py`: the snapshot has to be
taken in the thread that owns the `Inventory`, and it is the same snapshot a
headless run should take, or the two paths would read two different things.
The colour rule is not restated here -- the snapshot **asks**
`inventory.relics_for` while it is built, once per slot in play, and answers
from what it was told (the reason is in `candidates.py`: one rule, one place,
or the advisor and the picker come to differ about what fits).

**What this module does not do:** it draws nothing (S10), it sets no budget
(S11, `performance-tuner`), and it says nothing about the search's own
breadth -- `AdvisorResult.budget_note` is AD-010's field for that and stays
empty until the sentence for it exists; the wording of everything the player
reads is the `ui-ux-designer`'s and no run may invent one.
"""

from __future__ import annotations

import dataclasses
import hashlib
from collections import OrderedDict
from collections.abc import Callable, Mapping, Sequence

from .. import model
from . import candidates, explain, search, types
from .evaluate import evaluate


def _never_cancelled() -> bool:
    """The default check: nothing is stopping this run."""
    return False


# --- what the run reads, frozen at the moment it is handed over ------------

@dataclasses.dataclass(frozen=True)
class OfferedCopy:
    """One owned copy as the advisor reads it, in a shape a thread may hold.

    The seven fields `candidates._offer` asks an owned relic for, and nothing
    else. `inventory.OwnedItem` carries lists and is written by the main
    thread on every rescan; this is a value, so a run that has been overtaken
    keeps reading exactly what it started with (AD-006 point 8).
    """

    handle: int | None
    relic_id: int
    name: str
    colour: int
    is_deep: bool
    effect_ids: tuple[int, ...] = ()
    curse_ids: tuple[int, ...] = ()


class FrozenInventory:
    """What the player owns, as one run may read it, and nothing more.

    Built by `frozen_inventory` and never by hand. `relics_for` answers only
    the `(colour, deep)` pairs the problem it was built for asks about, and
    raises for anything else: a pair nobody precomputed means the snapshot
    and the vessel are from two different questions, and a quiet empty list
    would read as a poor inventory.
    """

    def __init__(self, relics: tuple[OfferedCopy, ...],
                 offers: Mapping[tuple[int, bool], tuple[OfferedCopy, ...]]
                 ) -> None:
        self.relics = relics
        self._offers = dict(offers)

    def relics_for(self, colour: int, deep: bool) -> tuple[OfferedCopy, ...]:
        try:
            return self._offers[(colour, deep)]
        except KeyError:
            raise KeyError(
                f"this snapshot was taken for other slots and was not asked "
                f"what fits a {'Deep ' if deep else ''}slot of colour "
                f"{colour}; it answers {sorted(self._offers)}") from None


def _copy_of(relic) -> OfferedCopy:
    return OfferedCopy(
        handle=relic.handle,
        relic_id=relic.relic_id,
        name=relic.name,
        colour=relic.colour,
        is_deep=relic.is_deep,
        effect_ids=tuple(relic.effect_ids),
        curse_ids=tuple(relic.curse_ids),
    )


def frozen_inventory(inventory,
                     problem: types.SlotProblem) -> FrozenInventory:
    """The owned relics as values, with what fits each slot already asked.

    Taken in the thread that owns the `Inventory`. Two things come out of it
    and both are needed: every owned copy, which is what the fingerprint of a
    request is over (AD-007), and the answer of `inventory.relics_for` for
    each slot in play, which is the colour and Deep rule asked rather than
    restated.

    Every slot is asked, held ones included: a hold can be lifted between the
    snapshot and the run only by asking a new question, and asking for all of
    them keeps the snapshot a property of the vessel rather than of which
    slots happened to be free.
    """
    offers = {}
    for slot in problem.slots:
        pair = (slot.colour, slot.deep)
        if pair not in offers:
            offers[pair] = tuple(_copy_of(relic) for relic
                                 in inventory.relics_for(slot.colour,
                                                         slot.deep))
    return FrozenInventory(
        relics=tuple(_copy_of(relic) for relic in inventory.relics),
        offers=offers)


def inventory_fingerprint(inventory) -> str:
    """AD-007's fingerprint of what the player owned when this was asked.

    Over `(handle, relic_id, sorted effect ids, sorted curse ids, colour,
    deep)` per copy, sorted, hashed. **The handle is in it**, against the
    original wording of AD-007 and by its own correction of 2026-09-01: the
    answer contains handles (AD-013), and a hit after the save has handed out
    new ones would name copies that are somewhere else or nowhere. A needless
    miss costs a run; a stale handle costs a recommendation the player cannot
    wear.

    The lines are sorted as text rather than the tuples as tuples, because a
    copy this save gives no handle for carries `None` there and `None` does
    not order against an int. Sorted text is a total order over the same
    content, which is all a fingerprint needs.
    """
    lines = sorted(
        "|".join((
            str(relic.handle),
            str(relic.relic_id),
            ",".join(str(effect_id) for effect_id in sorted(relic.effect_ids)),
            ",".join(str(curse_id) for curse_id in sorted(relic.curse_ids)),
            str(relic.colour),
            str(int(relic.is_deep)),
        ))
        for relic in inventory.relics)
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


# --- the key, and the memo over it -----------------------------------------

def cache_key(request: types.AdvisorRequest) -> types.AdvisorRequest:
    """The request, with the one field that is about the asking taken out.

    `generation` says which question this is in a sequence of questions, not
    what is being asked (AD-006 point 3). Leaving it in the key would make
    every question new and the cache dead, and no test that only asked twice
    would notice: the second answer would be right, merely computed again.
    Everything else the request carries is in the key, because everything
    else a run reads is in the request.
    """
    return dataclasses.replace(request, generation=0)


#: AD-007's proposal, and the whole of the cache's size. Thirty-two answers
#: of a few kilobytes each; the point is switching back and forth between a
#: handful of vessels, not holding a history.
CACHE_SIZE = 32


class ResultCache:
    """The answers already worked out, newest use last (AD-007, LRU).

    In memory and bound to the controller that holds it -- nothing on disk.
    A stored answer becomes wrong the moment the player melts a relic down or
    the game is patched, and the invalidation that would keep a file honest
    costs more to maintain than the run it saves (AD-007 option C).

    A hit hands back the stored answer with the **asking** request's
    generation on it, and nothing else changed. That one field is what the
    window decides by whether an answer is still wanted (AD-006 point 3), so
    an answer that kept the generation of the run that produced it would be
    dropped as stale by the very controller that had just fetched it.
    """

    def __init__(self, size: int = CACHE_SIZE) -> None:
        if size < 1:
            raise ValueError(f"a cache holds at least one answer; {size} "
                             f"would be a cache that is never a hit and is "
                             f"still a second path through the code")
        self._size = size
        self._answers: OrderedDict[types.AdvisorRequest,
                                   types.AdvisorResult] = OrderedDict()

    def __len__(self) -> int:
        return len(self._answers)

    def get(self, request: types.AdvisorRequest) -> types.AdvisorResult | None:
        """The answer to this question, or `None`."""
        key = cache_key(request)
        found = self._answers.get(key)
        if found is None:
            return None
        self._answers.move_to_end(key)
        return dataclasses.replace(found, generation=request.generation)

    def put(self, request: types.AdvisorRequest,
            result: types.AdvisorResult) -> None:
        """Keep this answer, dropping the least recently used one if full."""
        key = cache_key(request)
        self._answers[key] = result
        self._answers.move_to_end(key)
        while len(self._answers) > self._size:
            self._answers.popitem(last=False)

    def clear(self) -> None:
        """Forget everything. A data rebuild does this (AD-006 point 7)."""
        self._answers.clear()


# --- the run ---------------------------------------------------------------

def _refuse_a_request_that_asks_about_another_run(
        request: types.AdvisorRequest, inventory,
        ctx: types.GoalContext) -> None:
    """Refuse a request that does not describe the material beside it.

    The request is the cache key and the context is what the run reads. Where
    the two disagree the key stands for a run that did not happen, and the
    next hit on it answers a question nobody asked -- silently, because both
    halves are individually plausible. The fields checked here are the ones
    that exist on both sides and mean the same thing on both.

    The armaments are compared by the effects they bring, because that is
    what reaches `model.compute`; the tier is not on the context except for
    the one armament being rated, so nothing here claims to check it.
    """
    meta = ctx.data.get("meta") or {}
    reference = ctx.reference
    disagreements = []
    for name, asked, given in (
            ("hero_id", request.hero_id, ctx.hero.get("id")),
            ("level", request.level, ctx.level),
            ("weighting_id", request.weighting_id, ctx.weighting.id),
            ("reference_weapon_id", request.reference_weapon_id,
             None if reference is None else reference.weapon.get("id")),
            ("declared", request.declared, tuple(ctx.declared)),
            ("data_version", request.data_version,
             str(meta.get("data_version") or "")),
            ("armament effect ids",
             tuple(effect_id for armament in request.armaments
                   for effect_id in armament.effect_ids),
             tuple(ctx.armament_effect_ids)),
            ("inventory_fingerprint", request.inventory_fingerprint,
             inventory_fingerprint(inventory)),
    ):
        if asked != given:
            disagreements.append(f"{name}: the request says {asked!r}, this "
                                 f"run reads {given!r}")
    if disagreements:
        raise ValueError(
            "this request is the cache key of a run it does not describe, so "
            "an answer kept under it would be handed back for another "
            "question: " + "; ".join(disagreements))


def _base_lines(base_scores: Mapping[str, types.GoalScore]
                ) -> tuple[types.Baseline, ...]:
    """The base state's value under every direction, whole (QA-102)."""
    return tuple(types.Baseline(goal_id, score.value, score.unit,
                                score.unknowns, score.weights_note)
                 for goal_id, score in base_scores.items())


def _gain_over_the_base_state(
        goals: Mapping[str, types.Goal], ctx: types.GoalContext,
        built: model.Build, base_scores: Mapping[str, types.GoalScore]
        ) -> tuple[types.Marginal, ...]:
    """What the suggestion adds to the build as it stands (AD-014 point 6).

    The ranking figure stays the whole build's absolute value -- one
    authority -- and this is the number the player reads beside it. Under
    every direction and not only the ranked one, for the reason `pool()`
    gives for its second figure: the build is computed, so asking a second
    goal what it is worth is two function calls over fields that are already
    there.
    """
    return tuple(types.Marginal(goal_id,
                                goal.score(built, ctx).value
                                - base_scores[goal_id].value)
                 for goal_id, goal in goals.items())


def _explained(suggestion: types.Suggestion, problem: types.SlotProblem,
               pools: Sequence[types.SlotPool], base: model.Build,
               ctx: types.GoalContext, goal: types.Goal
               ) -> tuple[types.Suggestion, tuple[types.Candidate, ...],
                          model.Build]:
    """One suggestion with its reasons, the copies it names, and its build.

    The build is handed back beside the suggestion because the result's own
    fields are read off it -- the curses the calculation applied, the
    conditions it parked, the gain over the base state -- and computing it a
    second time for those would be a second `model.compute` of one assignment
    (AD-014.1).
    """
    chosen = explain.chosen_for(suggestion, pools)
    built = evaluate(problem, chosen, ctx)
    groups = explain.reasons(problem, chosen, base, built, ctx, goal)
    return dataclasses.replace(suggestion, reasons=groups), chosen, built


def run(request: types.AdvisorRequest, inventory,
        ctx: types.GoalContext, goals: Mapping[str, types.Goal],
        should_cancel: Callable[[], bool] = _never_cancelled
        ) -> types.AdvisorResult:
    """The whole answer to one question (AD-010), or `search.Cancelled`.

    The three steps are the three modules above this one: what may go into
    each free slot, which set of copies is worth most together, and what to
    say about it. Every figure in the answer comes out of the run that
    produced it and none is recomputed on the way to the screen.

    **Where a stopped run is noticed.** `should_cancel` is asked between the
    pre-sort and the search, and inside the search between the slot levels
    (AD-003 point 4). The pre-sort is not cut in two, and that is a measured
    decision rather than a convenient one: on the worst real case -- 309
    relics, `Wylder's Chalice` with Deep of Night, six free slots -- it costs
    **43 ms of a 960 ms run** (`scripts/measure_advisor_search.py`, median of
    three, this machine), a fifth of the 200 ms `UI_SPEC` AK-11 allows. The
    search is where the time is (916 ms), and the widest of its levels is
    where the coarse reaction time comes from.

    **Every suggestion is explained, not only the first.** `Suggestion`
    carries its own reasons and the window may draw any of them; a beam whose
    head was explained and whose tail was not would be one shape with two
    meanings. The result's singular fields -- the gain, the curses, what went
    uncounted -- belong to the **best** suggestion, which is the one
    `Apply all` applies.
    """
    _refuse_a_request_that_asks_about_another_run(request, inventory, ctx)
    if request.goal_id not in goals:
        raise KeyError(f"nothing ranks by goal {request.goal_id!r}; this run "
                       f"knows {sorted(goals)}")
    goal = goals[request.goal_id]
    problem = request.problem

    pools = candidates.pools(inventory, problem, ctx, goals, request.goal_id)
    if should_cancel():
        raise search.Cancelled("stopped after the pre-sort, before the search")
    found = search.beam(problem, pools, request.budget,
                        search.goal_scorer(problem, ctx, goal), should_cancel)

    base = evaluate(problem, (), ctx)
    base_scores = {goal_id: entry.score(base, ctx)
                   for goal_id, entry in goals.items()}

    suggestions = []
    best_chosen: tuple[types.Candidate, ...] = ()
    best_built = base
    for index, suggestion in enumerate(found):
        explained, chosen, built = _explained(suggestion, problem, pools,
                                              base, ctx, goal)
        suggestions.append(explained)
        if index == 0:
            best_chosen, best_built = chosen, built

    ranked = (suggestions[0].score if suggestions
              else base_scores[request.goal_id])
    groups = suggestions[0].reasons if suggestions else ()
    # Two run findings of one run, and neither is the other's: what the
    # direction could not know about this build, and what the search was not
    # allowed to touch. Kept in that order and de-duplicated, so a sentence
    # both halves happen to give is read once (AD-025.2).
    unknowns = tuple(dict.fromkeys(ranked.unknowns
                                   + explain.unknowns(problem)))
    return types.AdvisorResult(
        goal_id=goal.id,
        goal_label=goal.label,
        suggestions=tuple(suggestions),
        baseline=_base_lines(base_scores),
        gain=_gain_over_the_base_state(goals, ctx, best_built, base_scores),
        held=problem.held,
        unknowns=unknowns,
        weights_note=ranked.weights_note,
        not_counted=explain.not_counted(best_built),
        curses=explain.curses(best_chosen, base, best_built, ctx),
        curses_without_a_figure=explain.curses_without_a_figure(groups),
        effects_without_a_figure=explain.effects_without_a_figure(groups),
        data_note=explain.data_note(ctx),
        generation=request.generation,
    )
