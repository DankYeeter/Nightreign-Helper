"""The advisor's shapes have to survive being a cache key (QA-066).

`damage.Rating` is `frozen` and is neither hashable nor deeply immutable: its
per-type maps are dicts, handed on as the same object. AD-018 memoises
marginal contributions, so a shape like that used as a key either raises at
the first `hash()` or -- the worse half -- compares equal to a state that has
since moved underneath it. `advisor/types.py` answers that by carrying no
mapping and no list outside two named context types, and this file is what
holds the answer rather than trusting the docstring:

* every dataclass in the module is frozen;
* every one of them except the two named exceptions hashes;
* the sample below covers **every** dataclass in the module, so a new type
  cannot be added without either hashing or being named an exception.

The second half of QA-066 is about what a key must *distinguish*, and the
tests at the bottom are that: two runs whose held state differs are not one
another's cache entry (AD-016 point 2), a slot held empty is not a free slot,
and where a relic is held does not matter while what is held does.
"""

from __future__ import annotations

import dataclasses

import pytest

from nrplanner.advisor import types

#: The two types that carry the extracted dataset, and the whole of the
#: exception. Named here as well as in the module so that adding a third
#: place where a mapping enters the advisor is a decision somebody had to
#: write down twice.
CONTEXT_TYPES = {"GoalContext", "ReferenceArmament"}

A_RELIC = types.HeldRelic(relic_id=7, name="Test relic",
                          effect_ids=(1, 2), curse_ids=(3,), handle=41)

A_PROBLEM = types.SlotProblem(
    slots=(types.Slot(index=0, colour=0, deep=False),
           types.Slot(index=1, colour=4, deep=False)),
    held=(types.HeldSlot(index=0, relic=A_RELIC),),
)

A_SCORE = types.GoalScore(value=1.5, display="Attack rating 2", unit="AR",
                          unknowns=("nothing is verified",))

A_CANDIDATE = types.Candidate(
    slot_index=1, handle=42, relic_id=8, name="Other relic", colour=4,
    is_deep=False, effect_ids=(5,), curse_ids=(),
    marginals=(types.Marginal("max_damage", 2.25),),
)

#: One instance of every dataclass in the module that is not a context type.
#: Written out rather than generated: a generated sample would be built from
#: the annotations, and the claim under test is about what the fields really
#: hold.
SAMPLES = {
    "Slot": types.Slot(index=0, colour=0, deep=True),
    "HeldRelic": A_RELIC,
    "HeldSlot": types.HeldSlot(index=0, relic=A_RELIC),
    "SlotProblem": A_PROBLEM,
    "ArmamentRef": types.ArmamentRef(weapon_id=3, tier=2, effect_ids=(9,)),
    "Budget": types.Budget(candidates_per_slot=20, beam_width=40),
    "AdvisorRequest": types.AdvisorRequest(
        hero_id=1, level=15, problem=A_PROBLEM, goal_id="max_damage",
        weighting_id="even"),
    "GoalScore": A_SCORE,
    "Goal": types.Goal(id="x", label="X", blurb="x", score=lambda b, c: A_SCORE),
    "Weighting": types.Weighting(id="even", label="Even", note="even",
                                 weights=(("slashDamageCutRate", 1.0),)),
    "Baseline": types.Baseline("max_damage", 12.0),
    "Marginal": types.Marginal("max_damage", 1.0),
    "Candidate": A_CANDIDATE,
    "SlotPool": types.SlotPool(slot_index=1, candidates=(A_CANDIDATE,)),
    "SlotChoice": types.SlotChoice(slot_index=1, handle=42, relic_id=8,
                                   name="Other relic"),
    "Suggestion": types.Suggestion(
        choices=(types.SlotChoice(1, 42, 8, "Other relic"),), score=A_SCORE),
    "AdvisorResult": types.AdvisorResult(goal_id="max_damage",
                                         goal_label="Maximise damage"),
}


def dataclasses_in_the_module() -> dict[str, type]:
    """Every dataclass `advisor/types.py` defines, by name.

    `is_dataclass` is true of instances as well as of classes, and the module
    holds `DEFAULT_BUDGET`; the `isinstance(obj, type)` is what keeps a
    constant out of a list of types.
    """
    return {name: obj for name, obj in vars(types).items()
            if isinstance(obj, type) and dataclasses.is_dataclass(obj)
            and obj.__module__ == types.__name__}


def test_the_sample_covers_every_dataclass_in_the_module():
    """A new shape cannot slip in unhashed and unnamed.

    Without this, the two tests below would guard whatever was written down
    for them and say nothing about a type added afterwards -- which is the
    class of blind spot that has cost this project most (QA-070, QA-083).
    """
    covered = set(SAMPLES) | CONTEXT_TYPES

    assert covered == set(dataclasses_in_the_module()), (
        "every dataclass in advisor/types.py is either sampled here or named "
        "a context type; unaccounted for: "
        f"{sorted(set(dataclasses_in_the_module()) ^ covered)}")


@pytest.mark.parametrize("name", sorted(dataclasses_in_the_module()))
def test_every_advisor_shape_is_frozen(name):
    """Mutable-in-fact is the half of QA-066 a `frozen` keyword does cover."""
    shape = dataclasses_in_the_module()[name]

    assert shape.__dataclass_params__.frozen, (
        f"{name} is not frozen, so a run could change it after it has been "
        f"handed across a thread boundary (AD-006 point 8)")


@pytest.mark.parametrize("name", sorted(SAMPLES))
def test_every_shape_outside_the_context_can_be_a_cache_key(name):
    """The half `frozen` does not cover: a dict field hashes to an exception.

    Hashing the instance rather than reading its annotations, because an
    annotation is a claim and a dict put there anyway is what QA-066 predicts.
    """
    hash(SAMPLES[name])


CONTEXT_SAMPLES = {
    "ReferenceArmament": lambda: types.ReferenceArmament(
        weapon={"id": 1, "name": "a weapon"}, tier=1, slot_index=0),
    "GoalContext": lambda: types.GoalContext(
        data={"effects": {}}, hero={"name": "Wylder"}, level=15,
        reference=None,
        weighting=types.Weighting(id="even", label="Even", note="even",
                                  weights=(("slashDamageCutRate", 1.0),))),
}


@pytest.mark.parametrize("name", sorted(CONTEXT_TYPES))
def test_a_context_type_really_is_the_exception_it_is_named_as(name):
    """The exception has to be real, or the rule above is not a rule.

    Shown by hashing rather than by reading a field list: a context type that
    turned out to be hashable would mean the dataset had stopped travelling in
    it, and the entry should then be deleted rather than kept as a standing
    licence for the next mapping somebody wants to put in a shape.
    """
    assert set(CONTEXT_SAMPLES) == CONTEXT_TYPES
    fields = {f.name
              for f in dataclasses.fields(dataclasses_in_the_module()[name])}

    with pytest.raises(TypeError):
        hash(CONTEXT_SAMPLES[name]())
    assert "data" in fields or "weapon" in fields, (
        f"{name} is named a context type but carries neither the dataset nor "
        f"an armament record; the exception in advisor/types.py is stale")


def test_two_requests_that_differ_only_in_what_is_held_are_different_keys():
    """AD-016 point 2, and the reason the held state is in the key at all.

    A hit across two held states hands back a suggestion that overwrites a
    slot the player deliberately held -- the one outcome the feature exists to
    prevent. Costing an unnecessary miss is 0.46 s; costing this is the
    feature.
    """
    free = types.AdvisorRequest(hero_id=1, level=15, goal_id="max_damage",
                                weighting_id="even",
                                problem=types.SlotProblem(slots=A_PROBLEM.slots))
    held = types.AdvisorRequest(hero_id=1, level=15, goal_id="max_damage",
                                weighting_id="even", problem=A_PROBLEM)

    assert free != held
    assert hash(free) != hash(held)
    assert free.held_fingerprint != held.held_fingerprint


def test_where_a_relic_is_held_does_not_change_the_fingerprint():
    """AD-016: the held bundle acts through a flat effect list.

    It contributes its effects and it occupies its copies, and neither
    depends on which slot it sits in. Two problems that differ only in that
    may share a cache entry -- and if the fingerprint said otherwise, the
    picker walking six slots in turn would miss the cache every time, which is
    the case AD-016 option A was rejected for.
    """
    here = types.SlotProblem(slots=A_PROBLEM.slots,
                             held=(types.HeldSlot(0, A_RELIC),))
    there = types.SlotProblem(slots=A_PROBLEM.slots,
                              held=(types.HeldSlot(1, A_RELIC),))

    assert types.held_fingerprint(here) == types.held_fingerprint(there)


def test_a_slot_held_empty_is_not_the_same_question_as_a_free_slot():
    """"Leave this one empty" is an instruction, not the absence of one.

    It changes how many slots there are to fill, so it changes the problem
    (AD-014 point 7). Folding the two together would let a run that must leave
    a slot empty answer out of a run that was free to fill it.
    """
    free = types.SlotProblem(slots=A_PROBLEM.slots)
    empty = types.SlotProblem(slots=A_PROBLEM.slots,
                              held=(types.HeldSlot(0, None),))

    assert types.free_slots(free) == A_PROBLEM.slots
    assert [slot.index for slot in types.free_slots(empty)] == [1]
    assert types.held_fingerprint(free) != types.held_fingerprint(empty)


def test_a_custom_relic_held_beside_an_owned_one_still_fingerprints():
    """A held custom relic has no handle, and `None` does not order with ints.

    Two held slots, one of each kind, is the shortest way to a fingerprint
    that compares them -- and `UI_SPEC` AK-58 allows exactly that pairing. A
    natural sort would raise `TypeError` at the moment a cache key was being
    formed, which is in the worker thread, which is where an exception is
    hardest to trace back to its cause.
    """
    custom = types.HeldRelic(relic_id=-1, name="Custom relic",
                             effect_ids=(1,), handle=None)
    problem = types.SlotProblem(
        slots=A_PROBLEM.slots,
        held=(types.HeldSlot(0, custom), types.HeldSlot(1, A_RELIC)))

    assert len(types.held_fingerprint(problem)) == 2
    assert types.held_fingerprint(problem) == types.held_fingerprint(
        types.SlotProblem(slots=A_PROBLEM.slots,
                          held=(types.HeldSlot(0, A_RELIC),
                                types.HeldSlot(1, custom))))


def test_a_held_custom_relic_occupies_no_copy():
    """A custom relic is imaginary, so it takes nothing out of the inventory.

    It is a legitimate thing to hold -- it is an input, not a suggestion
    (AD-014.5, `UI_SPEC` AK-58) -- and AD-013 point 4 already keeps it from
    ever being suggested, because it has no handle.
    """
    custom = types.HeldRelic(relic_id=-1, name="Custom relic",
                             effect_ids=(1,), handle=None)
    problem = types.SlotProblem(slots=A_PROBLEM.slots,
                                held=(types.HeldSlot(0, custom),))

    assert types.held_handles(problem) == frozenset()
    assert types.held_relics(problem) == (custom,)


def test_a_marginal_that_was_never_scored_is_a_failure_not_a_zero():
    """A silent 0.0 would rank every candidate of an unscored goal alike.

    Which is indistinguishable, on screen, from a goal under which nothing
    the player owns helps.
    """
    with pytest.raises(KeyError):
        types.marginal_for(A_CANDIDATE, "min_damage_taken")


def test_asking_for_a_slot_the_vessel_has_not_got_is_a_failure():
    """Rather than an empty pool, which reads as a poor inventory."""
    with pytest.raises(KeyError):
        types.slot_at(A_PROBLEM, 5)
