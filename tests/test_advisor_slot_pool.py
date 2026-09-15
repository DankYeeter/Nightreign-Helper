"""The picker's question, asked the way the cache key can hold it.

`run.slot_pool` is the second answer function of `run.py` (AD-028): one
slot's pool, whole, for the relic picker to draw. Three claims carry this
file.

* **The canonical form answers the same pool as the shape the picker
  computes today.** The picker holds *every* slot and names the open one as
  an argument (`relicpicker.py:311-328`); the canonical form holds every slot
  **but** the open one and names it by leaving it free, which is what keeps
  the slot index out of `AdvisorRequest` (AD-028 point 3, AD-018). Whether
  the two really are one question is the risk the `architect` wrote into the
  table at `ARCHITECTURE.md:4400`, and it is checked here over handles and
  scores rather than assumed.
* **One pool serves both directions** (Nachtrag IX-0, IX-2). A pool measures
  every candidate under every goal it is given; only the order and `rank_by`
  follow the direction it was asked under. That is what lets the picker track
  ask under `goals.CANONICAL_POOL_ORDER` and the screen rank by the player's
  setting.
* **A question that is not the picker's is refused loudly.** No free slot,
  two free slots, or a request that describes another run: each is a key
  standing for a run nobody asked for, and a quiet answer to it would be an
  answer to the wrong question.

The material is made rather than read, for the reason `advisor_cases` gives:
a held slot, a slot held empty, a white slot and a Deep vessel have to be
*stated*, or a green run means only that this save happens to be arranged
conveniently.
"""

from __future__ import annotations

import dataclasses
import pathlib
import subprocess
import sys

import pytest

from nrplanner.advisor import candidates, goals, run, types

from tests import advisor_cases as advisor
from tests import weapon_damage_cases as cases

DAMAGE = "max_damage"
SURVIVAL = "min_damage_taken"

REPO = pathlib.Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def wylder(game_data):
    return cases.hero_by_name(game_data, "Wylder")


@dataclasses.dataclass(frozen=True)
class Vessel:
    """One vessel, what the player owns for it, and what sits in its slots.

    `held` names **every** slot: what is in it, or `None` for a slot that is
    empty. That is the picker's reading of the window -- every slot but the
    open one is a boundary condition, empty ones included (AD-018.1,
    `advisorbar.held_slot`) -- and both shapes below are cut from it, so the
    two questions differ in nothing but the shape under test.
    """

    name: str
    owned: object
    colours: tuple[int, ...]
    deep: bool
    held: dict[int, types.HeldRelic | None]

    def every_slot_held(self) -> types.SlotProblem:
        """The shape the picker computes today: the open slot is held too."""
        return advisor.problem(self.colours, deep=self.deep, held=self.held)

    def canonical(self, open_index: int) -> types.SlotProblem:
        """AD-028 point 3: the open slot is the only slot left free."""
        return advisor.problem(
            self.colours, deep=self.deep,
            held={index: relic for index, relic in self.held.items()
                  if index != open_index})


def ordinary_vessel(data: dict, hero: dict) -> Vessel:
    """Three ordinary slots: one holding a copy, one held empty, one white.

    The white slot is in here because it is the expensive and the awkward
    one: `inventory.relics_for` offers it every colour, so it is the slot
    whose pool is longest -- the one copy of a second colour is owned for
    exactly that -- and the one a difference between two shapes has the most
    room to show up in.

    The two coloured slots are the same colour rather than two, because a
    slot whose colour the player owns a single copy of has a pool of one, and
    a pool of one holds any claim about order or content vacuously.

    **What the copies carry is stated, and it is two kinds.** Strength raises
    what the reference armament hits for and leaves effective HP where it
    was; Vigor does the reverse. A vessel whose every copy carried the same
    kind would rank every candidate at zero under one of the two directions,
    and "the same figures under both directions" would then be a comparison
    of zero with zero -- true, and about nothing.
    """
    strength = advisor.raising_effects(data, hero, 3)
    vigor = [[effect_id] for effect_id
             in cases.effects_raising_attribute(data, hero, "Vigor", 3)]
    rolls = [roll for pair in zip(strength, vigor) for roll in pair]
    owned = advisor.make_inventory(data, hero, colour=advisor.RED, count=5,
                                   other_colour=advisor.BLUE, rolls=rolls)
    copies = list(owned.relics)
    return Vessel(
        name="three ordinary slots",
        owned=owned,
        colours=(advisor.RED, advisor.RED, advisor.WHITE),
        deep=False,
        held={0: advisor.held_relic(copies[0]),
              1: None,
              2: advisor.held_relic(copies[1])})


def deep_vessel(data: dict, hero: dict) -> Vessel:
    """Two Deep slots, one holding a Deep copy, one white and held empty.

    Deep because the separation is a property of what a slot is offered, not
    of the question shape, and a case that only ever asked ordinary slots
    would not notice a shape that lost it.
    """
    owned = advisor.make_inventory(data, hero, colour=advisor.RED, count=3,
                                   deep_count=3)
    deep_copies = [copy for copy in owned.relics if copy.is_deep]
    return Vessel(
        name="two Deep slots",
        owned=owned,
        colours=(advisor.RED, advisor.WHITE),
        deep=True,
        held={0: advisor.held_relic(deep_copies[0]), 1: None})


def vessels(data: dict, hero: dict) -> tuple[Vessel, ...]:
    return (ordinary_vessel(data, hero), deep_vessel(data, hero))


def openings(data: dict, hero: dict) -> list[tuple[Vessel, int]]:
    """Every vessel with every one of its slots open, in turn."""
    return [(vessel, index)
            for vessel in vessels(data, hero)
            for index in range(len(vessel.colours))]


#: How many (vessel, open slot) pairs the two vessels above come to. Written
#: out so a case that quietly stopped covering half of them is a failure
#: rather than a smaller green run (L-002).
OPENINGS = 5


def pool_the_picker_computes_today(vessel: Vessel, open_index: int,
                                   ctx: types.GoalContext,
                                   direction: str) -> types.SlotPool:
    """`SlotAdvice.ranking`'s call, with nothing of the picker imported.

    `relicpicker.py:311-328` holds every slot and hands the open one's index
    to `candidates.pool`, which lifts the hold on it itself. Rewritten here
    rather than called, because `relicpicker` is Qt and this file is not --
    and because the point of the comparison is the shape of the question, so
    the shape has to be stated where the case can be read.
    """
    problem = vessel.every_slot_held()
    frozen = run.frozen_inventory(vessel.owned, problem)
    return candidates.pool(frozen, problem, open_index, ctx, goals.GOALS,
                           direction)


def pool_from_the_canonical_form(vessel: Vessel, open_index: int,
                                 ctx: types.GoalContext,
                                 direction: str) -> types.SlotPool:
    """The same question as a request the cache key can hold."""
    problem = vessel.canonical(open_index)
    frozen = run.frozen_inventory(vessel.owned, problem)
    request = advisor.request_for(problem, ctx, frozen, direction)
    return run.slot_pool(request, frozen, ctx, goals.GOALS)


def handles(pool: types.SlotPool) -> list[int | None]:
    return [candidate.handle for candidate in pool.candidates]


def scores(pool: types.SlotPool) -> dict[tuple[int | None, str], float]:
    """Every candidate's figure under every direction, by handle."""
    return {(candidate.handle, marginal.goal_id): marginal.gain
            for candidate in pool.candidates
            for marginal in candidate.marginals}


# -- the two shapes are one question ----------------------------------------

@pytest.mark.parametrize("direction", [DAMAGE, SURVIVAL])
def test_the_canonical_form_answers_the_pool_the_picker_computes_today(
        game_data, wylder, direction):
    """The risk the `architect` named at `ARCHITECTURE.md:4400`.

    If holding every slot and naming the open one gave a different pool from
    holding every other slot and leaving the open one free, then the slot
    index would have to become a field of `AdvisorRequest` and AD-018's "no
    second key form" would need revising -- which is a decision, not a fix.
    So the two are compared over handles and over every candidate's figure
    under every direction, and then whole.

    The two shapes are asserted to really differ before the pools are
    compared: without that, a case in which both sides built the same problem
    would pass while proving nothing.
    """
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))
    covered = 0
    for vessel, open_index in openings(game_data, wylder):
        where = f"{vessel.name}, slot {open_index} open, ranked by {direction}"
        held_everywhere = vessel.every_slot_held()
        canonical = vessel.canonical(open_index)
        assert len(canonical.held) == len(held_everywhere.held) - 1, where
        assert canonical != held_everywhere, where

        today = pool_the_picker_computes_today(vessel, open_index, ctx,
                                               direction)
        canonical_pool = pool_from_the_canonical_form(vessel, open_index, ctx,
                                                      direction)

        assert len(today.candidates) >= 2, (
            f"{where}: a pool of fewer than two candidates would make this "
            f"comparison hold whatever the two shapes did")
        assert handles(canonical_pool) == handles(today), where
        assert scores(canonical_pool) == scores(today), where
        assert canonical_pool == today, where
        covered += 1
    assert covered == OPENINGS


def test_the_canonical_form_names_the_open_slot_by_leaving_it_free(game_data,
                                                                   wylder):
    """No field says which slot is asked about; the problem says it.

    The pool that comes back carries the index of the slot that was free, and
    that is the whole of how the question names it (AD-028 point 3).
    """
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))
    for vessel, open_index in openings(game_data, wylder):
        answered = pool_from_the_canonical_form(vessel, open_index, ctx,
                                                DAMAGE)
        assert answered.slot_index == open_index, vessel.name


# -- one pool, both directions ----------------------------------------------

def test_one_pool_serves_both_directions_and_only_its_order_follows_one(
        game_data, wylder):
    """Nachtrag IX-0 and IX-2, over every opening of both vessels.

    The picker track asks under `goals.CANONICAL_POOL_ORDER` whatever the
    player has chosen, and the screen ranks by the setting instead (AK-205).
    That only holds while a pool asked under one direction carries the same
    candidates with the same figures as one asked under the other. If it ever
    stops holding, `UI_SPEC` §4's fallback applies and it is a finding, not
    something to work around here (L-008c).

    **The positive control is the reordering**: at least one opening has to
    come back in a different order under the two directions, or "the same
    candidates in another order" would be a claim about pools that are simply
    identical, and a `rank_by` that was never read would satisfy it.
    """
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))
    other = SURVIVAL if goals.CANONICAL_POOL_ORDER == DAMAGE else DAMAGE
    covered = 0
    reordered = 0
    for vessel, open_index in openings(game_data, wylder):
        where = f"{vessel.name}, slot {open_index} open"
        canonical = pool_from_the_canonical_form(
            vessel, open_index, ctx, goals.CANONICAL_POOL_ORDER)
        chosen = pool_from_the_canonical_form(vessel, open_index, ctx, other)

        assert canonical.rank_by == goals.CANONICAL_POOL_ORDER, where
        assert chosen.rank_by == other, where
        assert scores(canonical) == scores(chosen), where
        assert canonical.baseline == chosen.baseline, where
        assert canonical.unknowns == chosen.unknowns, where
        assert sorted(canonical.candidates, key=lambda c: c.handle) == sorted(
            chosen.candidates, key=lambda c: c.handle), where
        if handles(canonical) != handles(chosen):
            reordered += 1
        covered += 1
    assert covered == OPENINGS
    assert reordered >= 1, (
        "no opening came back in a different order under the two directions, "
        "so this case would hold even if nothing read `rank_by` at all")


def test_the_canonical_order_is_a_direction_the_registry_answers_to(game_data,
                                                                    wylder):
    """A canonical direction outside `GOALS` would refuse every picker run.

    The constant is defined off a registry entry, so this cannot drift while
    both live in `goals.py` -- and it is checked all the same, because that
    is the property the picker track depends on and not the line it is
    written on.
    """
    assert goals.CANONICAL_POOL_ORDER in goals.GOALS

    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))
    vessel = ordinary_vessel(game_data, wylder)
    answered = pool_from_the_canonical_form(vessel, 2, ctx,
                                            goals.CANONICAL_POOL_ORDER)
    assert answered.rank_by == goals.CANONICAL_POOL_ORDER
    assert answered.candidates


# -- what is refused --------------------------------------------------------

@pytest.mark.parametrize("free, description", [
    (0, "every slot held, so nothing says which one is open"),
    (2, "two slots free, so the question names two open slots"),
])
def test_a_problem_that_is_not_one_open_slot_is_refused(game_data, wylder,
                                                        free, description):
    """The form is the key, so a form that is not the picker's is refused.

    Answering the first free slot of two would be an answer to a question
    nobody asked, filed under a key that stands for it -- and the next hit on
    that key would hand it back.
    """
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))
    vessel = ordinary_vessel(game_data, wylder)
    open_indices = list(range(len(vessel.colours)))[:free]
    problem = advisor.problem(
        vessel.colours, deep=vessel.deep,
        held={index: relic for index, relic in vessel.held.items()
              if index not in open_indices})
    frozen = run.frozen_inventory(vessel.owned, problem)
    request = advisor.request_for(problem, ctx, frozen, DAMAGE)

    with pytest.raises(ValueError) as refusal:
        run.slot_pool(request, frozen, ctx, goals.GOALS)
    assert f"leaves {free} of them free" in str(refusal.value), description


def test_a_request_that_describes_another_run_is_refused(game_data, wylder):
    """The same guard `run` stands behind, and for the same reason.

    A `SlotPool` is filed in the cache under the request beside it, so a
    request whose fields disagree with the material it was answered from is a
    key for a run that did not happen.
    """
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))
    vessel = ordinary_vessel(game_data, wylder)
    problem = vessel.canonical(2)
    frozen = run.frozen_inventory(vessel.owned, problem)
    request = dataclasses.replace(
        advisor.request_for(problem, ctx, frozen, DAMAGE),
        level=ctx.level + 1)

    with pytest.raises(ValueError) as refusal:
        run.slot_pool(request, frozen, ctx, goals.GOALS)
    assert "level" in str(refusal.value)


def test_a_request_that_names_an_unknown_direction_is_refused(game_data,
                                                              wylder):
    """Nothing orders a pool by a direction the run was not given."""
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))
    vessel = ordinary_vessel(game_data, wylder)
    problem = vessel.canonical(2)
    frozen = run.frozen_inventory(vessel.owned, problem)
    request = advisor.request_for(problem, ctx, frozen, "max_style")

    with pytest.raises(KeyError) as refusal:
        run.slot_pool(request, frozen, ctx, goals.GOALS)
    assert "max_style" in str(refusal.value)


def test_a_stopped_pool_says_so_and_is_asked_once_per_offered_relic(game_data,
                                                                    wylder):
    """`should_cancel` reaches the pre-sort, which is where SEC-022 bites.

    The picker's answer is the pre-sort and nothing else, so a check that did
    not reach it would leave the whole run unstoppable -- on a save the
    player did not write, the pre-sort *is* the run (SEC-022).
    """
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))
    vessel = ordinary_vessel(game_data, wylder)
    problem = vessel.canonical(2)
    frozen = run.frozen_inventory(vessel.owned, problem)
    request = advisor.request_for(problem, ctx, frozen, DAMAGE)

    asked = 0

    def stop_after_two() -> bool:
        nonlocal asked
        asked += 1
        return asked > 2

    with pytest.raises(types.Cancelled) as stopped:
        run.slot_pool(request, frozen, ctx, goals.GOALS, stop_after_two)
    assert "pre-sort of slot 2" in str(stopped.value)
    assert asked == 3


# -- Qt-free ----------------------------------------------------------------

WITHOUT_QT = """
import sys

sys.path.insert(0, sys.argv[1])
from nrplanner.advisor import goals, run

assert run.slot_pool is not None and goals.CANONICAL_POOL_ORDER
print(",".join(sorted(name for name in sys.modules if "PySide" in name)))
"""


def test_the_picker_s_answer_is_reachable_without_qt(tmp_path):
    """AD-001, checked by importing rather than by promising.

    In this process PySide6 is loaded long before any advisor case runs --
    `conftest` imports it -- so the claim can only be made in a process of
    its own. Transitive, which an inspection of these two files would not be:
    an import of Qt anywhere below them would show up here.
    """
    driver = tmp_path / "import_the_advisor.py"
    driver.write_text(WITHOUT_QT, encoding="utf-8")

    done = subprocess.run([sys.executable, str(driver), str(REPO)],
                          capture_output=True, text=True, check=False)

    assert done.returncode == 0, done.stderr
    assert done.stdout.strip() == "", (
        f"importing the picker's answer pulled Qt in: {done.stdout.strip()}")
