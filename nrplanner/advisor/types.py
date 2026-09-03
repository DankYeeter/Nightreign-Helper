"""The shapes the advisor passes around, and the lookups over them.

Every dataclass here is `frozen`, and none of them has a method that
calculates anything: what a build is worth is `goals.py`, what a slot may
hold is `candidates.py`, and the one door to `model.compute` is
`evaluate.py`. This module is the vocabulary those three speak (AD-001,
AD-004, AD-006, AD-010).

**Hashability, decided here rather than retrofitted (QA-066).**
`damage.Rating` is `frozen` and yet neither hashable nor deeply immutable --
its per-type maps are ordinary dicts, handed on as the same object. AD-018
memoises marginal contributions, so a key built out of a shape like that
would either raise at the first `hash()` or, worse, compare equal to a state
that has since been changed underneath it. The rule that keeps this module
out of that: **the shapes that describe a question carry no mapping and no
list.** `Slot`, `HeldRelic`, `HeldSlot`, `SlotProblem`, `ArmamentRef`,
`Budget` and `AdvisorRequest` hold ints, strs, bools and tuples of those, so
each of them hashes to a value derived from its whole content, and the cache
key of AD-007/AD-016 is the request object itself -- there is no second key
form that could drift from the state it stands for.

The answers (`GoalScore`, `Baseline`, `Marginal`, `Candidate`, `SlotPool`,
`SlotChoice`, `Suggestion`, `AdvisorResult`) keep the same rule, for a
different reason: AD-006 point 8 sends them across a thread boundary, and a
dict field would be frozen in name and shared in fact.

**The two named exceptions are `ReferenceArmament` and `GoalContext`**, and
they are the whole of the exception: they carry the extracted dataset, which
*is* a mapping and which no rewriting here would make hashable. Neither is
ever a cache key and neither travels as one -- a run is keyed by
`AdvisorRequest`, whose `data_version` names the dataset instead of holding
it. `tests/test_advisor_types.py` holds both halves of that claim: every
other dataclass in this module is hashed there, and the exception list is
checked against the module rather than trusted.

**What this module does not decide:** which slots the vessel has (the window
builds a `SlotProblem` from what the player has on screen), what a goal is
worth (AD-004, `goals.py`), and whether a held slot is still valid -- a hold
on a relic that has been melted down falls away when the request is built
(AD-017.3), which is S10 and not here.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from .. import model


# --- the question ----------------------------------------------------------

@dataclass(frozen=True)
class Slot:
    """One relic slot of the vessel, as the advisor sees it.

    `colour` is the game's own colour number, so colour 4 is the white slot
    that takes any colour -- the rule itself lives in `inventory.relics_for`
    and is deliberately not restated here (one place, not two).

    `deep` says whether this is one of the three Deep of Night slots, which
    take Deep relics and only those. It sits on the slot rather than on the
    problem because a vessel with Deep of Night switched on has both kinds at
    once; the problem-wide flag AD-016 puts in the cache key is the set of
    `(colour, deep)` pairs of the free slots, not a separate field.
    """

    index: int
    colour: int
    deep: bool


@dataclass(frozen=True)
class HeldRelic:
    """What sits in a slot the player has held (AD-014, `GOAL.md` F1).

    `handle` is the save's own identifier for this physical copy and is what
    keeps a held relic from being suggested a second time (AD-014.5). It is
    `None` for a custom relic, which is imaginary and owns no copy; a custom
    relic may be held -- it is an input, not a suggestion (AD-014.5,
    `UI_SPEC` AK-58).

    `effect_ids` and `curse_ids` are what this copy actually rolled. Curses
    are in here beside the effects and not in a compartment of their own,
    because they go into the same `model.compute` call as ordinary effects
    (AD-015): there is no second reckoning for a curse anywhere under
    `advisor/`.
    """

    relic_id: int
    name: str
    effect_ids: tuple[int, ...] = ()
    curse_ids: tuple[int, ...] = ()
    handle: int | None = None


@dataclass(frozen=True)
class HeldSlot:
    """One held slot and its content, or the decision to leave it empty.

    `relic is None` means "held and staying empty" (AD-014.7) -- a different
    thing from a slot that is simply free, which is not named in
    `SlotProblem.held` at all. Both states have to exist: the search must be
    able to tell "do not fill this" from "fill this".
    """

    index: int
    relic: HeldRelic | None = None


@dataclass(frozen=True)
class SlotProblem:
    """The slots in play and which of them the player is holding.

    Holding is a **boundary condition, not a starting value** (AD-014): a
    held relic's effects go into every evaluation of this problem, and the
    search runs over the free slots alone. That is why the held state is part
    of the problem rather than of some initial state -- an initial state is
    something a search may overwrite.

    `slots` are the slots in play, in the vessel's own order (AD-003 point 1),
    which for Deep of Night is the three ordinary slots followed by the three
    Deep ones. A vessel with Deep of Night switched off contributes three.
    """

    slots: tuple[Slot, ...] = ()
    held: tuple[HeldSlot, ...] = ()


@dataclass(frozen=True)
class ArmamentRef:
    """One armament on the weapon grid, in the shape a cache key can hold.

    The key form of the weapon context AD-006 puts in the request: the
    armament's id rather than its record, so an `AdvisorRequest` stays
    hashable. `GoalContext` carries the resolved records for the calculation
    itself.
    """

    weapon_id: int
    tier: int
    effect_ids: tuple[int, ...] = ()


@dataclass(frozen=True)
class Budget:
    """How wide the search may look (AD-003).

    `candidates_per_slot` is K and `beam_width` is W. The defaults in
    `DEFAULT_BUDGET` are AD-003's, measured against the real inventory: the
    worst real case, a six-slot Deep vessel with a white slot, costs 0.46 s at
    K=20/W=40 and 0.98 s at K=30/W=60. They are a starting point the
    `performance-tuner` confirms or corrects in S11, not a measurement of
    this build.

    Only `candidates_per_slot` is read in this task -- it sets how long a
    pre-sorted list has to be (S5+, `candidates.shortlist`). `beam_width` is
    carried because it belongs to the same decision and to the same cache key;
    the beam that consumes it is S7.
    """

    candidates_per_slot: int
    beam_width: int


#: AD-003's measured default. See `Budget` for where the two figures come from.
DEFAULT_BUDGET = Budget(candidates_per_slot=20, beam_width=40)


@dataclass(frozen=True)
class AdvisorRequest:
    """One question to the advisor, and the whole of its cache key.

    Every field is either a scalar or a tuple of scalars, so the request
    hashes as a value: AD-007's cache and AD-016's canonical form key on this
    object and nothing else. `data_version` and `inventory_fingerprint` stand
    in for the two big mutable things a run depends on -- the extracted
    dataset and what the player owns -- precisely so that neither has to be
    held here (QA-066).

    `generation` is AD-006 point 3: a result whose generation is not the
    current one is dropped without touching the display. It is part of the
    request rather than of the controller so that a result can carry it back.
    """

    hero_id: int
    level: int
    problem: SlotProblem
    goal_id: str
    weighting_id: str
    #: The armament the damage goal ranks on, `None` when none is chosen
    #: (AD-004, OF-5: the run is not refused, the assumption is stated).
    reference_weapon_id: int | None = None
    armaments: tuple[ArmamentRef, ...] = ()
    #: effect id -> how many times the player declares its condition met.
    declared: tuple[tuple[int, int], ...] = ()
    budget: Budget = DEFAULT_BUDGET
    #: `meta.data_version` of the dataset this was asked against.
    data_version: str = ""
    #: What the player owned when this was asked. Supplied by the caller that
    #: reads the save; the advisor never recomputes it from a live inventory.
    inventory_fingerprint: str = ""
    generation: int = 0

    @property
    def held_fingerprint(self) -> tuple[tuple, ...]:
        """AD-016's fingerprint of the held state, derived and never stored.

        A stored copy is a second representation of the same thing and can
        drift from it; a drifted fingerprint produces exactly the failure
        AD-016 point 2 is written against -- a cache hit across two different
        held states, which hands back a suggestion that overwrites a slot the
        player deliberately held. Deriving it costs a sort over at most six
        entries.

        This is the one property on any dataclass in this module, and it
        calculates nothing: it re-reads `problem.held`. `damage.Rating` sets
        the precedent for a derived reading on a frozen dataclass.
        """
        return held_fingerprint(self.problem)


# --- the answer ------------------------------------------------------------

@dataclass(frozen=True)
class GoalScore:
    """What one goal makes of one build (AD-004).

    `value` is the ranking figure and is **never rounded** -- rounding is the
    display's business and belongs in `display`, which is the discipline
    QA-074 cost this project once already. Bigger is better for every goal, so
    one comparison serves all of them.

    `unknowns` is not optional and is never empty (AD-010, `GOAL.md` A7): a
    figure that does not say what it cannot know is the thing the house rule
    forbids. `weights_note` is empty exactly when the goal made no weighting
    assumption of its own.
    """

    value: float
    display: str
    unit: str
    unknowns: tuple[str, ...]
    weights_note: str = ""


@dataclass(frozen=True)
class Goal:
    """One named direction to optimise in, as a registry entry (AD-004).

    `score` takes a computed build and a `GoalContext` and gives a
    `GoalScore`. It never sees the base state and never forms a difference:
    the marginal contribution is the caller's arithmetic (do-not rule 20),
    or knowledge of the base state would leak into the registry.
    """

    id: str
    label: str
    blurb: str
    score: Callable[[model.Build, "GoalContext"], GoalScore]


@dataclass(frozen=True)
class Weighting:
    """How a goal weighs several figures against each other (AD-004).

    Data rather than constants inside the goal, so that OF-3 -- whether the
    player gets a control for it -- can be answered later without touching
    the registry. `note` is the sentence that reaches `GoalScore.weights_note`
    and it has to say the assumption out loud.

    `weights` is a tuple of pairs and not a mapping: see the module docstring.
    """

    id: str
    label: str
    note: str
    weights: tuple[tuple[str, float], ...]


@dataclass(frozen=True)
class ReferenceArmament:
    """The armament a damage goal ranks on, in the shape the facade reads.

    One of the two types in this module that carry dataset records (see the
    module docstring). `weapon` and `tier` are the two attributes
    `damage.equipped` asks a slot for, and `slot_index` is what the
    starting-armament pairing needs: the penalty follows the pairing of slot 1
    with the Nightfarer's own starting armament, not the weapon and not the
    slot alone (`damage.is_starting_armament`, verified in play).
    """

    weapon: Mapping
    tier: int
    slot_index: int


@dataclass(frozen=True)
class GoalContext:
    """Everything a run needs that is not the relic assignment (AD-004).

    The second of the two dataset-carrying types, and the reason the first
    exists: `data`, `hero` and the armament records are mappings out of the
    extraction, and a run needs them at every evaluation. It is never a cache
    key -- `AdvisorRequest.data_version` is what a key holds instead.

    Beyond AD-004's four fields this carries what `model.compute` needs in
    order to give the same build the stat sheet shows: every armament held
    (weapon-type gates are met by any armament on the grid, not only the one
    being rated), the effects those armaments rolled, and the conditional
    effects the player has declared live. Leaving any of them out would make
    the advisor's figure disagree with the sheet beside it, which is QA-001
    in a new place.
    """

    data: Mapping
    hero: Mapping
    level: int
    reference: ReferenceArmament | None
    weighting: Weighting
    weapons_held: tuple[Mapping, ...] = ()
    armament_effect_ids: tuple[int, ...] = ()
    #: effect id -> how many times its condition is declared met.
    declared: tuple[tuple[int, int], ...] = ()


@dataclass(frozen=True)
class Baseline:
    """One goal's figure for the base state a slot is measured against.

    Kept apart from `Marginal` although both are a goal id and a float: one is
    an absolute value and the other a difference, and a type that let them be
    mixed up would put an attack rating where a gain belongs.
    """

    goal_id: str
    value: float


@dataclass(frozen=True)
class Marginal:
    """What one candidate adds to one goal (AD-018.1, `GOAL.md` F2).

    `gain` is `goal(base state + this candidate) - goal(base state)`,
    unrounded. It is the number the picker shows and the number the search
    pre-sorts by -- one figure, two views (checkpoint 15).
    """

    goal_id: str
    gain: float


@dataclass(frozen=True)
class Candidate:
    """One owned relic offered for one slot, with what it is worth there.

    The candidate is the **copy**, identified by its handle, not the role
    (AD-013): 309 owned relics carry 306 distinct rolls, so collapsing them
    would save one per cent and lose exactly the cases where telling two
    copies apart matters. A relic without a handle is not a candidate at all
    and is reported instead (AD-013 point 4).

    `marginals` holds one entry per goal in the registry, always all of them:
    scoring a finished build under a second goal is two function calls over
    fields that are already there, so both directions are computed whatever
    the picker chooses to show (AD-018 point 2, `UI_SPEC` §3.3).
    """

    slot_index: int
    handle: int
    relic_id: int
    name: str
    colour: int
    is_deep: bool
    effect_ids: tuple[int, ...] = ()
    curse_ids: tuple[int, ...] = ()
    marginals: tuple[Marginal, ...] = ()


@dataclass(frozen=True)
class SlotPool:
    """Every relic that may go into one slot, best first, and what is missing.

    This is a **public** result, not a step on the way to one (S5++): the
    picker shows it and the beam consumes the same list, so the two views
    cannot disagree about a figure.

    `baseline` is the base state's own value under each goal -- the reference
    point `candidates` measured against, which is the current build with
    *this* slot emptied (AD-018.1). Without it a gain of "+12.4" says nothing.

    `unknowns` is what this pool could not consider, in the player's language
    (AD-010, A7). It is empty when there was nothing to leave out, which is
    the ordinary case; the guarantee that a goal always says something is on
    `GoalScore`, not here.
    """

    slot_index: int
    baseline: tuple[Baseline, ...] = ()
    candidates: tuple[Candidate, ...] = ()
    unknowns: tuple[str, ...] = ()


@dataclass(frozen=True)
class SlotChoice:
    """One slot of a suggestion: which copy, and how to name it (AD-013.5).

    The handle is what the window puts back into the slot, so the suggestion
    picks the same copy the picker offers. The name is for reading, never for
    identity.
    """

    slot_index: int
    handle: int
    relic_id: int
    name: str


@dataclass(frozen=True)
class Suggestion:
    """One complete assignment of the free slots, with its score (AD-010).

    `reasons` are the English lines that say which effects decided it (A5).
    They are written by `explain.py`, which is S8: this task fixes the shape
    they travel in and produces none of them.
    """

    choices: tuple[SlotChoice, ...]
    score: GoalScore
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class AdvisorResult:
    """What one run hands back, with everything it does not know (AD-010).

    The fields below are AD-010's mandatory content plus S4+: the base
    state's value, the gain over it (AD-014.6) and the slots that were held.
    The gain is carried beside the absolute figure rather than instead of it,
    because the ranking number stays the whole build's value -- one authority
    -- and the gain is what the player reads.

    Nothing in this task fills one in. S7 produces the suggestions, S8 the
    reasons and the curse lines, S9 the generation and the notes; what is
    fixed here is the shape they have to fit into, so that none of them can
    quietly drop `unknowns` on the way to the screen.
    """

    goal_id: str
    goal_label: str
    suggestions: tuple[Suggestion, ...] = ()
    baseline: tuple[Baseline, ...] = ()
    gain: tuple[Marginal, ...] = ()
    held: tuple[HeldSlot, ...] = ()
    unknowns: tuple[str, ...] = ()
    weights_note: str = ""
    #: Conditional effects the player owns that went into no total, by name.
    #: How many there are is `len(not_counted)`; a second count field would be
    #: a second thing to keep in step.
    not_counted: tuple[str, ...] = ()
    #: The curses of the suggested relics, read out of `Build.sources` rather
    #: than out of the relic definitions, so a curse that the calculation did
    #: not apply cannot be shown as though it had (AD-015).
    curses: tuple[str, ...] = ()
    data_note: str = ""
    budget_note: str = ""
    generation: int = 0


# --- lookups over the shapes above -----------------------------------------
#
# Free functions, not methods: the dataclasses above stay free of behaviour
# (S4), and `evaluate.py` needs the held relics before `candidates.py` exists
# in the import order, so the lookups cannot live in either of them.

def slot_at(problem: SlotProblem, index: int) -> Slot:
    """The slot with this index, or `KeyError`.

    Loud rather than forgiving: an index no slot carries means the caller and
    the vessel disagree about how many slots are in play, and a `None` here
    would surface later as an empty candidate list that looks like a poor
    inventory.
    """
    for slot in problem.slots:
        if slot.index == index:
            return slot
    raise KeyError(f"this vessel has no slot {index}")


def free_slots(problem: SlotProblem) -> tuple[Slot, ...]:
    """The slots the advisor may fill, in the vessel's own order.

    A slot named in `held` is not free, whether it holds a relic or is held
    empty (AD-014 points 2 and 7). With every slot held there are no free
    ones, and that is not an error state: the answer is then the current
    build, evaluated (AD-014 point 2).
    """
    taken = {entry.index for entry in problem.held}
    return tuple(slot for slot in problem.slots if slot.index not in taken)


def held_relics(problem: SlotProblem) -> tuple[HeldRelic, ...]:
    """The relics the held slots contain, skipping the ones held empty."""
    return tuple(entry.relic for entry in problem.held
                 if entry.relic is not None)


def held_handles(problem: SlotProblem) -> frozenset[int]:
    """The copies the base state already occupies (AD-014.5).

    A held copy cannot be suggested a second time. A held **custom** relic
    has no handle and contributes none: it is imaginary, so it occupies no
    copy, and AD-013 point 4 already keeps handle-less relics out of the
    candidate space, so it cannot be suggested either.
    """
    return frozenset(relic.handle for relic in held_relics(problem)
                     if relic.handle is not None)


def held_fingerprint(problem: SlotProblem) -> tuple[tuple, ...]:
    """AD-016's canonical fingerprint of the held state.

    Position-independent and sorted, because the held bundle acts through a
    flat effect list and through the handles it occupies -- neither of which
    depends on which slot a held relic sits in. Two problems whose held
    bundles fingerprint alike may share a cache entry; two that do not, may
    not.

    A slot held empty contributes an entry as well. It changes the problem --
    one slot fewer to fill -- so leaving it out would let a run with an empty
    held slot answer from the cache of a run without one.
    """
    entries = []
    for entry in sorted(problem.held, key=lambda held: held.index):
        relic = entry.relic
        if relic is None:
            entries.append(("empty",))
            continue
        entries.append((
            "relic",
            relic.handle,
            relic.relic_id,
            tuple(sorted(relic.effect_ids)),
            tuple(sorted(relic.curse_ids)),
        ))
    # Ordered by `repr` rather than naturally: a custom relic's handle is
    # `None` and an owned one's is an int, and Python refuses to order those
    # against each other -- a held custom relic would turn the fingerprint
    # into a TypeError at the moment a cache key was formed. `repr` is a total
    # order over these tuples and deterministic for the strings, ints and
    # tuples they hold. The order only has to be the *same* every time; it
    # does not have to mean anything.
    return tuple(sorted(entries, key=repr))


def marginal_for(candidate: Candidate, goal_id: str) -> float:
    """This candidate's gain under one goal, or `KeyError`.

    The price of holding the marginals as a tuple instead of a mapping, and
    the reason the module docstring gives for paying it. `KeyError` rather
    than a default: a goal that was never scored is a bug in the caller, and
    a silent 0.0 would rank every candidate of an unscored goal alike.
    """
    for marginal in candidate.marginals:
        if marginal.goal_id == goal_id:
            return marginal.gain
    raise KeyError(f"{candidate.name} carries no marginal for goal "
                   f"{goal_id!r}")


def baseline_for(pool: SlotPool, goal_id: str) -> float:
    """The base state's own value under one goal, or `KeyError`."""
    for baseline in pool.baseline:
        if baseline.goal_id == goal_id:
            return baseline.value
    raise KeyError(f"slot {pool.slot_index} carries no baseline for goal "
                   f"{goal_id!r}")
