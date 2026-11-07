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
list.** `Slot`, `HeldRelic`, `HeldSlot`, `SlotProblem`, `Budget` and
`AdvisorRequest` hold ints, strs, bools and tuples of those, so
each of them hashes to a value derived from its whole content, and the cache
key of AD-007/AD-016 is the request object itself -- there is no second key
form that could drift from the state it stands for. That sentence was false
until T-048: a derived `held_fingerprint` stood beside the request and
claimed a property the request does not have (QA-107). It is gone, and what
the key knows about the held state it knows through `AdvisorRequest.problem`,
which carries `held` in the vessel's own order.

The answers (`GoalScore`, `Baseline`, `Marginal`, `Candidate`, `SlotPool`,
`SlotChoice`, `ReasonLine`, `SlotReasons`, `Suggestion`, `AdvisorResult`)
keep the same rule, for a different reason: AD-006 point 8 sends them across
a thread boundary, and a dict field would be frozen in name and shared in
fact.

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


# --- stopping a run --------------------------------------------------------

class Cancelled(Exception):
    """Raised when a run was stopped before it had an answer (AD-006 point 6).

    An exception rather than a short result, because a truncated beam and a
    finished one are the same shape: the window says `Stopped. Nothing was
    changed.` for the first and shows suggestions for the second (`UI_SPEC`
    4.5 against 4.6), and a caller that has to tell them apart by counting
    slots would get it wrong on the vessel where a slot had nothing to choose
    from anyway.

    It lives here rather than in `search.py` because the pre-sort raises it
    too, and `candidates.py` is imported *by* `search.py`.
    """


def never_cancelled() -> bool:
    """The default check: nothing is stopping this run."""
    return False


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
    once; there is no problem-wide Deep flag, and the cache key reaches this
    field the way it reaches every other one -- through `SlotProblem.slots`,
    in the vessel's own order (AD-016.2 as D3 rewrote it). The canonical
    `(colour, deep)` form AD-008 proposed was never built and is not the key.
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

    `colour` and `is_deep` say which slots of another vessel it would fit
    (AD-062.5). White on a custom relic built in a white slot: any slot of its
    Deep kind.
    """

    relic_id: int
    name: str
    effect_ids: tuple[int, ...] = ()
    curse_ids: tuple[int, ...] = ()
    handle: int | None = None
    colour: int = model.WHITE_SLOT
    is_deep: bool = False


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


#: A copy by what it rolled, not by its handle: relic id, effects, curses. Two
#: copies of one roll are the same relic to a player (`favourites.key`).
Roll = tuple[int, tuple[int, ...], tuple[int, ...]]


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

    `excluded` are the effect ids the player marked `Avoid` (`GOAL.md`
    A18, AD-036, AD-057): a boundary condition of the same kind as holding. A
    copy carrying such an id -- effect or curse -- is never offered
    (`candidates.pool`). A relic the player put there themselves stays where
    it is, with the id struck before the calculation sees it
    (`evaluate.effect_ids_of`), and the `Why` says it was excluded rather
    than that it carried no number.

    `rejected` are the rolls the player turned down for this question (A28,
    AD-060): no copy of such a roll is offered, whichever copy was shown.
    What the player holds is untouched, as it is for `excluded`.

    `required` are the effect ids the player marked `Favourite` (A19, A28,
    AD-036.4, AD-058): every suggestion carries each of them the vessel can
    carry at once, on a held relic or a chosen copy, and the run says which
    it had to leave out (A7). A boundary condition of the beam, like holding
    (AD-014.5) -- never a filter over its result. An id in both sets is
    refused: the window keeps them apart, and a problem that asked for both
    would have no answer that is not a lie about one of them.

    `pinned` are the rolls the player starred for this Nightfarer (A28,
    AD-059), sorted: each goes into the suggestion when it fits, and the run
    says why when it does not. Not `favourites`' text form: this package is
    Qt-free, and the window reads the store.
    """

    slots: tuple[Slot, ...] = ()
    held: tuple[HeldSlot, ...] = ()
    excluded: frozenset[int] = frozenset()
    required: frozenset[int] = frozenset()
    rejected: frozenset[Roll] = frozenset()
    pinned: tuple[Roll, ...] = ()

    def __post_init__(self) -> None:
        both = self.excluded & self.required
        if both:
            raise ValueError(
                f"effects {sorted(both)} are both excluded and required; an "
                f"effect is one or the other (AD-036.1)")


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

    **Where the held state is in the key: in `problem`, and nowhere else**
    (AD-016.2 as D3 rewrote it). `SlotProblem` holds `held` as an ordered
    tuple, so the key is position-dependent -- two questions that differ only
    in *which* slot a relic is held in are different questions, and they have
    to be, because the answer carries slot indices (`SlotChoice.slot_index`).
    A hit across a permutation would hand back a suggestion whose indices
    point at the other question's slots, and the remapping that would
    straighten it out does not exist (AD-016.4). There is no derived
    fingerprint beside this and there will not be one: a second form of the
    key can drift from the state it stands for, and a drifted one overwrites
    a slot the player deliberately held.
    """

    hero_id: int
    level: int
    problem: SlotProblem
    #: The player's choice on the Advisor bar's track, an ordering and
    #: nothing else on the picker's (Nachtrag IX-2): the picker asks under
    #: `goals.CANONICAL_POOL_ORDER` whatever the player selected, because a
    #: pool serves every direction (AK-43, AK-205). Taking the picker's
    #: `goal_id` for the choice repeats T-077 at `SlotPool.rank_by`'s twin.
    goal_id: str
    weighting_id: str
    #: The armament the damage goal ranks on, `None` when none is chosen
    #: (AD-004, OF-5: the run is not refused, the assumption is stated).
    reference_weapon_id: int | None = None
    #: effect id -> how many times the player declares its condition met.
    declared: tuple[tuple[int, int], ...] = ()
    #: `GoalContext.assumed_armament_counts`: they follow the selected
    #: armament tile, so two tiles of two types are two questions.
    assumed_armament_counts: tuple[int, ...] = ()
    #: `GoalContext.pick_ailment` and `.pick_swap`: the selected tile's rolls
    #: are not in the key, so `declared` alone does not say whether a
    #: condition rests on a swappable pick (QA-322).
    pick_ailment: tuple[int, ...] = ()
    pick_swap: str = ""
    #: `GoalContext.selected_catalyst`'s id: a spell asked of another staff
    #: is another question.
    selected_catalyst_id: int | None = None
    #: `GoalContext.selected_spell_id`: another spell of the same staff is
    #: another question (AK-415). Empty unless a spell row is asked.
    selected_spell_id: int | None = None
    #: `GoalContext.art_tile.key`: another armament, tier, art or slot on the
    #: selected tile is another question (AK-415). Empty unless `Weapon art`
    #: is asked of a filled tile.
    art_tile: tuple[int, int, int | None, int] | None = None
    #: Which hand the damage direction ranks (AK-292/AK-293). In the key
    #: because a run ranked one-handed is not the answer to a two-handed ask.
    two_handed: bool = False
    #: What the damage direction ranks a hit *with*, empty for the armament
    #: itself (AD-051 point 1): an art key of `model.attack_arts` --
    #: `skill` for a Weapon Art, `sorceries`/`incantations` for a spell of
    #: that kind, `family:<id>` for a spell school.
    #: The id form and never the label, so a patch that renames a spell
    #: school leaves the key -- and the cache under it -- alone.
    #:
    #: **Never taken out of the key**, although two of the three directions
    #: do not read it: the picker measures every pool under all three, so
    #: what a pool *contains* depends on this. A key that kept quiet about
    #: it would hand a run's answer back for another run's question, which
    #: is T-077 at this field's twin (AD-051 point 2).
    hit_with: str = ""
    #: Which damage type the damage direction ranks, empty for all of them:
    #: one name out of `weapons.DAMAGE_TYPES`. In the key for the same
    #: reason as `hit_with`, and free to be combined with it -- the two are
    #: two questions about one figure, which is why they are two fields and
    #: not one prefixed value (AD-051).
    damage_type: str = ""
    budget: Budget = DEFAULT_BUDGET
    #: `meta.data_version` of the dataset this was asked against.
    data_version: str = ""
    #: What the player owned when this was asked. Supplied by the caller that
    #: reads the save; the advisor never recomputes it from a live inventory.
    inventory_fingerprint: str = ""
    generation: int = 0


# --- the answer ------------------------------------------------------------

@dataclass(frozen=True)
class GoalScore:
    """What one goal makes of one build (AD-004).

    `value` is the ranking figure and is **never rounded** -- rounding is the
    display's business and belongs in `display`, which is the discipline
    QA-074 cost this project once already. Bigger is better for every goal, so
    one comparison serves all of them.

    `unknowns` carries **run findings only** and may be empty (AD-025.2): a
    sentence that would read the same before any run is a procedural sentence
    and lives in `Goal.scope`, where the registry keeps it. Empty here means
    "this run left nothing out", which is a statement rather than an omission
    (AD-010 as AD-025.2 sharpens it). `weights_note` is empty exactly when the
    goal made no weighting assumption of its own; it is a run finding too,
    because which of the possible wordings applies is settled by the run
    (AD-025.3).
    """

    value: float
    display: str
    unit: str
    unknowns: tuple[str, ...] = ()
    weights_note: str = ""


@dataclass(frozen=True)
class Goal:
    """One named direction to optimise in, as a registry entry (AD-004).

    `score` takes a computed build and a `GoalContext` and gives a
    `GoalScore`. It never sees the base state and never forms a difference:
    the marginal contribution is the caller's arithmetic (do-not rule 20),
    or knowledge of the base state would leak into the registry.

    `scope` is what this direction cannot know **whatever the run** -- the
    procedural sentences of AD-025.1, and it is never empty: a direction
    without a stated scope is not one. It lives here rather than on
    `GoalScore` because the registry has no run to look at, so a sentence
    that needs one cannot be written here by mistake; and a caller can read
    it without a dataset, a build or an inventory, which is what makes the
    A7 promise checkable on a runner with no game installed (QA-106,
    checkpoint 29). The run's own findings go the other way and travel in
    `GoalScore.unknowns`.
    """

    id: str
    label: str
    scope: tuple[str, ...]
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

    `art_id` is the tile's own art pick (`WeaponSlot.art_id`), the third
    attribute `damage.weapon_art` asks a slot for.
    """

    weapon: Mapping
    tier: int
    slot_index: int
    art_id: int | None = None

    @property
    def key(self) -> tuple[int, int, int | None, int]:
        """This armament as a cache key holds it (`AdvisorRequest.art_tile`)."""
        return (self.weapon["id"], self.tier, self.art_id, self.slot_index)


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
    effects the player has declared live.

    **Two of those fields are no longer filled by the program**, and that
    is A17 rather than an omission: `weapons_held` and `armament_effect_ids`
    still come back empty from `advisorbar.asking_from` (T-188 for the first,
    AD-032 for the second); `reference` is filled again since AD-038, with
    the Nightfarer's own starting armament, so an attribute a relic moves can
    reach the ranking figure through its scaling (A22) without any armament
    the player actually carries moving it (A17 holds all the same). The
    advisor's build is
    therefore *not* the stat sheet's build any more -- it answers "what is
    this relic worth between runs", where the sheet answers "what am I
    hitting for right now", and the difference is stated in `Goal.scope`
    (A12) instead of being closed. The fields stay because the other
    question is still asked from tests and will be asked again by A16; the
    one thing that must not happen is filling them here and not in
    `AdvisorRequest`, which `run._refuse_a_request_that_asks_about_another_
    run` catches.
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
    #: Armament-count conditions ("3+ X Equipped") the baseline counts as
    #: met, sorted. The window fills in those of the selected tile's
    #: armament type only (user decision 28.10.2026); given several types,
    #: `evaluate` counts **one** per build (AD-036.6, addendum 12.10.2026,
    #: QA-299). Apart from `declared` because a type declared by hand
    #: replaces them, and a declaration by hand is never narrowed. In the key
    #: as `AdvisorRequest.assumed_armament_counts`.
    assumed_armament_counts: tuple[int, ...] = ()
    #: Conditions on an enemy ailment (`effecttext.ailment_awaited`) the
    #: baseline counts in a build only where one of its relics makes the
    #: attacks inflict the ailment (`inflicts_on_hit`, user decision
    #: 01.11.2026), sorted. Those the selected tile's armament inflicts
    #: (its rolls, art or spell included) are in `declared` instead; an
    #: armament on another tile is no source. Not in the key: they are the conditions of that
    #: kind `declared` leaves out, so `declared` decides them.
    awaiting_ailment: tuple[int, ...] = ()
    #: Conditions of that kind only the art or spell of the selected tile
    #: inflicts, where a swap relic reaches it (the starting armament's art,
    #: the starting catalyst's spell), sorted. They count in a build without
    #: such a relic and are awaited in one with it: a swap beats the pick
    #: (AD-056.4, QA-322). In the key as `AdvisorRequest.pick_ailment`.
    pick_ailment: tuple[int, ...] = ()
    #: Which swap takes them: `arts` or `spells`, the block of
    #: `evaluate._swapped_in`; empty where `pick_ailment` is. In the key as
    #: `AdvisorRequest.pick_swap`.
    pick_swap: str = ""
    #: The staff or seal on the selected tile, `None` where it holds none:
    #: the spell cells cast from it before the starting catalyst
    #: (`damage.spell_catalyst`, T-335b). In the key as
    #: `AdvisorRequest.selected_catalyst_id`.
    selected_catalyst: Mapping | None = None
    #: The spell the player chose on that tile (`WeaponSlot.spell_id`), cast
    #: where it lies in the staff's pools (`damage.spell_thrown`, AK-415).
    #: `None` unless a spell row is asked, so the key splits only where the
    #: answer moves. In the key as `AdvisorRequest.selected_spell_id`.
    selected_spell_id: int | None = None
    #: The selected tile -- armament, tier, art pick, slot -- that a
    #: `Weapon art` question swings (`damage.weapon_art`, user decision
    #: 31.10.2026 13:50: "Markierte Kachel"), `None` unless that art is asked
    #: of a filled tile; the goal then swings `reference`. Its rolls stay out
    #: (A17). In the key as `AdvisorRequest.art_tile`.
    art_tile: ReferenceArmament | None = None
    #: The art ids the player's **held** relics swap onto the starting
    #: armament (`modifiers["startSwordArtsId"]`). Only these swap the art a
    #: `Weapon art` question swings: a candidate that would swap it is never
    #: proposed for it (AD-056.7). Follows `SlotProblem.held`, so the key
    #: carries it already.
    held_swapped_art_ids: tuple[int, ...] = ()
    #: The hand the damage direction ranks -- the stat sheet's `1H`/`2H`
    #: switch (AK-292). Changes what the direction *counts*, not what any
    #: display shows (AK-293 point 1).
    two_handed: bool = False
    #: What the hit is made with and which damage type is counted, in the
    #: same form as `AdvisorRequest.hit_with`/`.damage_type` and empty for
    #: the armament itself and for every type. Read by `goals._max_damage`
    #: and by nothing else, which is also the one place that combines them
    #: (AD-051 points 1 and 3).
    hit_with: str = ""
    damage_type: str = ""


@dataclass(frozen=True)
class Baseline:
    """What one pool knows about one goal -- one line per direction.

    Kept apart from `Marginal` although both begin with a goal id and a float:
    one is an absolute value and the other a difference, and a type that let
    them be mixed up would put an attack rating where a gain belongs. That
    separation is about the **figure** and is unaffected by the text beside
    it.

    `value` is the base state's own figure, the reference point the
    candidates were measured against. The three fields after it are the rest
    of the same answer: until T-048 `pool()` took `.value` off the
    `GoalScore` and dropped everything else, so the run findings of a
    direction never reached the one result the player actually reads
    (QA-102, checkpoint 32). They are carried here rather than in a second
    per-goal record beside this one, because two records mean two lookups,
    two places a `goal_id` can be missing, and two things to keep in step.

    `unknowns` holds **run findings only**, never the procedural sentences:
    those live in `Goal.scope`, are drawn once for the screen, and six pools
    of a Deep vessel repeating them six times is exactly what AK-50 is
    written against (AD-025).

    `GoalScore.display` deliberately does **not** travel with them: it
    formats the base state's absolute figure and the picker shows a
    difference, so a formatted absolute here would be an invitation to put
    the wrong number on a card, and a second representation of `value`.
    """

    goal_id: str
    value: float
    unit: str = ""
    unknowns: tuple[str, ...] = ()
    weights_note: str = ""


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
    (AD-010, A7) -- run findings, and only those (AD-025.2). It is empty when
    there was nothing to leave out, which is the ordinary case; the guarantee
    that a direction always says something is on `Goal.scope`, which the
    registry holds and no run can empty.

    **`rank_by` is which direction put this list in this order** (D-4), and it
    has no default: a pool that could not say what ranked it is exactly the
    state this field exists against. The beam branches on the head of the
    list and scores with a scorer of its own, so pools ranked one way and
    scored another answer a question nobody asked -- silently, in the right
    shape, with a plausible figure. Measured on `Wylder's Chalice` with Deep
    at the default budget, `max_damage` scored over `min_damage_taken` pools:
    attack rating **290,39 against 323,30**, four of six handles different,
    and no complaint anywhere (T-077). `search.beam` compares this against
    `Scorer.goal_id` and refuses the pairing.
    """

    slot_index: int
    rank_by: str
    baseline: tuple[Baseline, ...] = ()
    candidates: tuple[Candidate, ...] = ()
    unknowns: tuple[str, ...] = ()
    #: Which question this is the answer to, when it is an answer at all
    #: (AD-006 point 3, AD-028). The picker's track hands pools back through
    #: the same controller the Advisor bar's results go through, and that
    #: controller decides by this field whether an answer is still the one
    #: being waited for. It belongs to the **asking** and not to the pool:
    #: `candidates.pool` never sets it, so a pool the beam search consumes
    #: carries 0 and two pools of the same question compare equal whatever
    #: was asked in between.
    generation: int = 0
    #: Why this pool may be short (AD-057.4): the `Avoid` ids that took copies
    #: out of it, sorted; how many copies a Reject took; the names of the
    #: favourite relics whose copy fits here and is already placed. Read by
    #: `explain.empty_slots` and by nothing else.
    avoided_by: tuple[int, ...] = ()
    rejected_out: int = 0
    pin_taken: tuple[str, ...] = ()


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


# --- the lines of one suggestion, and what the window must not work out -----
#
# `explain.py` writes the words. These two shapes are how the words reach the
# window without the window reading them, and they exist for one rule
# (`UI_SPEC` T-078 §6, extended in T-080 §7): **the display never takes a
# sentence apart.** A line arrives with the slot it belongs under, with
# whether it is a curse, and with why it carries no figure; a slot arrives
# with the two counts its heading states. Every one of those was once
# readable out of the text alone -- and the text contains an em dash in the
# middle of a field name (`model.RATE_LABELS["regainRate"]` is `Regain — HP
# won back by attacking after a hit`), so splitting on the dash breaks today
# rather than at some future relic name. Coupling display to the shape of a
# sentence is what QA-107 cost this project once already.

#: `ReasonLine.silence` for a line that carries a figure. Everything else is
#: a reason a line has none, and `explain.py` picks exactly one of them in the
#: order T-080 §4 lays down.
CARRIES_A_FIGURE = ""
#: The effect works for another Nightfarer, so it is dead weight on this one.
#: Drawn like every other dead effect in the program -- `NOT WORKING` with a
#: strikethrough, as `effecttext` and the slot cards draw it -- and not as an
#: ordinary muted line (Director, 06.09.2026): two ways of saying one thing
#: is one thing for the player to remember, and this is the commonest case
#: there is.
SILENT_ANOTHER_NIGHTFARER = "another_nightfarer"
#: The figure is in the build, from another copy of the same effect, from
#: another member of its exclusivity group, or from a relic the player is
#: holding; this copy added none of it.
SILENT_ALREADY_COUNTED = "already_counted"
#: The effect waits on a condition the player can be in -- the same set that
#: feeds `AdvisorResult.not_counted`, so the two cannot disagree.
SILENT_UNDER_A_CONDITION = "under_a_condition"
#: What the effect is worth is a question about the armaments carried.
SILENT_ARMAMENT_BOUND = "armament_bound"
#: It works, and nothing here reduces it to a number.
SILENT_NO_NUMBER_HERE = "no_number_here"
#: The dataset does not carry this effect, so there is no name to write.
SILENT_NOT_IN_THE_DATA = "not_in_the_data"
#: The player excluded it (`SlotProblem.excluded`, A18): it never reached the
#: calculation, so it is not "waiting on a condition" -- it was not asked.
SILENT_EXCLUDED = "excluded"
#: The player required it (`SlotProblem.required`, A19) and it moved no
#: figure of its own: the line says why the copy was suggested all the same.
SILENT_REQUIRED = "required"
#: The player required a weapon-count condition of one armament type, and the
#: build counts another type's or none: a build meets the condition of only
#: one type (AD-036.6, addendum 12.10.2026), the selected tile's unless one
#: is declared by hand (28.10.2026), so this one moved nothing (AK-383).
#: Likewise a weapon-type bonus of another type and a condition on an enemy
#: ailment the build does not inflict (01.11.2026, QA-321), and an effect that
#: acts on the enemy (07.11.2026, QA-321).
SILENT_REQUIRED_OTHER_TYPE = "required_other_type"


@dataclass(frozen=True)
class ReasonLine:
    """One drawn line of one slot group, and where it belongs.

    `text` is the whole of what the line says: strip every colour, bullet and
    strikethrough from it and the statement is still complete (AK-156). The
    bullet is **not** in here -- `•` for an effect and `✦` for a curse are the
    window's, taken from `is_curse`, because a window that had to look for a
    `✦` in the text would be reading the sentence again.

    `effect_id` is the id the line is about -- an effect's or a curse's, the
    same one `SlotProblem.excluded`/`required` name. AK-276 binds the
    marking control to the id, not to the drawn line: two lines about one
    effect show one state, and a click on either moves both.
    """

    slot_index: int
    effect_id: int
    text: str
    is_curse: bool = False
    silence: str = CARRIES_A_FIGURE


@dataclass(frozen=True)
class SlotReasons:
    """What one filled slot of a suggestion says for itself (A5).

    `count_line` carries the denominator of the group: how many of the copy's
    effect roles moved a figure, out of how many there are. It is the sentence
    that keeps a silent effect from disappearing, and `effects_total -
    effects_with_a_figure` is exactly the number of silent lines below it
    (AK-155) -- a claim a case can recompute rather than believe.

    `effects_with_a_figure` counts **effects, not lines**: an effect that
    moves two figures the stat sheet does not merge is two lines and one
    effect.
    """

    slot_index: int
    relic_name: str
    effects_total: int
    effects_with_a_figure: int
    count_line: str
    lines: tuple[ReasonLine, ...] = ()


def drawn_in_the_block(line: ReasonLine) -> bool:
    """Does this line stand in the suggestion block, or only in `Why`?

    Decided here rather than at each drawing site, and decided on the shape
    rather than on the words. **A curse is a trap, a silent effect is not**
    (Director, 06.09.2026): the price of a suggestion has to be readable
    before it is applied, so every curse of the suggested copy stands in the
    block, including the one no figure covers. An effect that merely does
    nothing here costs no slot the player would not have spent anyway, and it
    is what made the worst measured card 16 lines tall, so it waits in the
    `Why` dialog.
    """
    return line.is_curse or line.silence == CARRIES_A_FIGURE


@dataclass(frozen=True)
class Suggestion:
    """One complete assignment of the free slots, with its score (AD-010).

    `reasons` are what says which effects decided it (A5): one group per
    filled slot, in slot order, each with its heading counts and its lines.
    They are written by `explain.py`, which is S8.
    """

    choices: tuple[SlotChoice, ...]
    score: GoalScore
    reasons: tuple[SlotReasons, ...] = ()


#: Why a free slot has no choice in the best suggestion (AD-057.4), in the
#: order `explain.empty_slots` asks. The copies were there and another slot
#: spent them, one of them a carrier of a `Favourite` effect:
EMPTY_REQUIREMENT = "requirement"
#: Nothing was left because a favourite relic's copy is placed elsewhere:
EMPTY_PIN = "pin"
#: Nothing was left because of the player's marks, one or the other or both:
EMPTY_AVOIDED_AND_REJECTED = "avoided_and_rejected"
EMPTY_AVOIDED = "avoided"
EMPTY_REJECTED = "rejected"
#: Nothing of the kind: the save holds no unused relic for this slot.
EMPTY_NOTHING = "nothing"


@dataclass(frozen=True)
class EmptySlot:
    """A free slot the best suggestion leaves empty, and why (AK-441).

    `line` is the card's whole sentence, written by `explain.py` because it
    takes the dataset to name an effect. `effect_ids` belongs to
    `EMPTY_AVOIDED` and `EMPTY_REQUIREMENT`, `relic_name` to `EMPTY_PIN`.
    """

    slot_index: int
    reason: str
    effect_ids: tuple[int, ...] = ()
    relic_name: str = ""
    line: str = ""


#: Why a starred relic is not in the suggestion (AD-059.5), in the order
#: `candidates.pin` asks. A roll that carries an avoided id or was rejected:
PIN_AVOIDED = "avoided"
PIN_REJECTED = "rejected"
#: Every copy of the roll lacks a handle, so none can be applied (AD-013.4):
PIN_NO_COPY = "no_copy"
#: This vessel has no slot of its colour and Deep kind, or all of them are held:
PIN_NO_SLOT = "no_slot"
PIN_SLOTS_HELD = "slots_held"
#: A stronger starred relic took the last slot it fits:
PIN_OTHER_PIN = "other_pin"
#: Placing it would lower how many `Favourite` effects the vessel can carry:
PIN_BLOCKS_REQUIREMENT = "blocks_requirement"


@dataclass(frozen=True)
class PinLeftOut:
    """A starred relic the suggestion does not carry, and why (AK-439, AK-456).

    `effect_id` belongs to `PIN_AVOIDED` and `PIN_BLOCKS_REQUIREMENT`, `other`
    to `PIN_OTHER_PIN`. `because` and `line` are the bar's half sentence and
    the `Why` dialog's row, written by `explain.py`: it takes the dataset to
    name an effect, and the window has none to read.
    """

    name: str
    roll: Roll
    reason: str
    is_deep: bool = False
    effect_id: int | None = None
    other: str = ""
    because: str = ""
    line: str = ""


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
    #: The base state's `GoalScore.display` under the asked direction: what a
    #: vessel with no suggestion shows in the comparison (AK-449).
    baseline_display: str = ""
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
    #: The curses of the suggested copies to which the calculation wrote no
    #: figure at all, and the effects likewise (`UI_SPEC` T-078 §4, T-080 §7).
    #: The criterion is neither a claim about what the game files hold nor
    #: "conditional": no line was written, which is the one thing this program
    #: can state about them. How many there are is the length of the tuple.
    #:
    #: **These are the same objects the slot groups already carry, not a
    #: second copy of them** -- the subset of `Suggestion.reasons` whose
    #: `silence` is set. Drawn once, from the groups; kept here so the status
    #: line can count them without walking the groups, exactly as `curses` is
    #: the curse-carrying subset of the same lines (§6 point 4).
    curses_without_a_figure: tuple[ReasonLine, ...] = ()
    effects_without_a_figure: tuple[ReasonLine, ...] = ()
    #: The card's own summary of `explain.required_met_by_a_hold`, empty
    #: when no favourited effect sits on a held relic (AK-314). The `Why`
    #: dialog does not read this -- it keeps every sentence of `unknowns`
    #: unabridged (AK-314.5); this is the space-saving line for the
    #: `SuggestionBlock` alone.
    favourites_met_line: str = ""
    data_note: str = ""
    budget_note: str = ""
    generation: int = 0
    #: The `Favourite` effects the best suggestion does not carry, sorted
    #: (AD-058.5). `explain.required_but_unmet` wrote one sentence for each.
    required_left_out: tuple[int, ...] = ()
    #: The same sentences `unknowns` carries for them, for the bar's tooltip
    #: (AK-455: one source, and the bar does not pick through `unknowns`).
    required_unmet: tuple[str, ...] = ()
    #: Every free slot the best suggestion leaves empty, in slot order. Empty
    #: under `no_carrier_for`: the whole suggestion fell, and that is the
    #: reason given (AD-057.4).
    empty_slots: tuple[EmptySlot, ...] = ()
    #: The slots a starred relic was laid in before the search, and the stars
    #: left out by name and reason, sorted by name (AD-059.4, .5). `held` stays
    #: what the player holds: a star comes back as an ordinary choice, so
    #: `Apply all` writes it and the slot count is untouched (QA-284).
    pins_placed: tuple[int, ...] = ()
    pins_left_out: tuple[PinLeftOut, ...] = ()
    #: The chosen damage type or attack art, lowered as it stands mid-sentence,
    #: when every suggestion was dropped because nothing owned moves the
    #: ranked figure under it (QA-290); empty otherwise. The status line reads
    #: it to name that cause instead of the bare "nothing to choose from"
    #: (AK-365).
    no_carrier_for: str = ""


@dataclass(frozen=True)
class VesselQuestion:
    """One vessel of the comparison (AD-062): what to ask about it, or, with
    `request` `None`, the held relics that keep it from being asked at all."""

    vessel_id: int
    request: AdvisorRequest | None = None
    unfit_holds: tuple[str, ...] = ()


@dataclass(frozen=True)
class VesselRow:
    """What the vessel list says of one vessel, read off its whole answer
    (AD-062.6). Every figure is the run's: `figure` and `value` under the
    asked direction, `other_value` under the other (AK-463)."""

    vessel_id: int
    figure: str = ""
    value: float = 0.0
    other_value: float = 0.0
    required_left_out: tuple[int, ...] = ()
    pins_left_out: tuple[str, ...] = ()
    unfit_holds: tuple[str, ...] = ()


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


def roll_of(copy) -> Roll:
    """This copy's roll: anything that carries the three fields."""
    return copy.relic_id, tuple(copy.effect_ids), tuple(copy.curse_ids)


def unwanted(problem: SlotProblem, copy) -> bool:
    """May no suggestion use this copy (A18, A28, AD-057.1)?

    It carries an id marked `Avoid`, effect or curse, or its roll was turned
    down.
    """
    return (not problem.excluded.isdisjoint(copy.effect_ids)
            or not problem.excluded.isdisjoint(copy.curse_ids)
            or roll_of(copy) in problem.rejected)


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
