"""The test fixture and the program must ask the advisor the same thing (QA-227).

`tests/advisor_cases.context_from_planner` is the context every case about
the advisor's arithmetic is run on, and `nrplanner.advisorbar.asking_from` is
the context the running program hands over. They were two implementations of
one idea, written months apart, and they came apart without a single test
going red: T-188 stopped the program filling `reference` and `weapons_held`
(A17), AD-032 stopped it filling `armament_effect_ids`, and the fixture went
on filling all three. Checkpoint 13 -- "the advisor computes the build the
window shows" -- stayed green the whole way, because both sides of its
comparison were fed by the fixture.

**That is the dangerous shape and not the three fields.** Three fields can be
copied across; a second implementation grows a fourth difference the next
time somebody changes one side. So the fixture no longer builds a context: it
takes the program's and adds back exactly what the comparison it serves
needs, and this file is what holds the two together.

Three questions, because one of them alone would be comfortable rather than
true:

* does the fixture actually go through `asking_from`, or has somebody written
  a second implementation again;
* is every field it did not deliberately change identical to the program's;
* are the fields it did change really changes -- an allowance that has
  outlived its reason is a hole with a comment over it.
"""

from __future__ import annotations

import dataclasses

import pytest

from nrplanner import advisorbar, weaponslots
from nrplanner.advisor import goals

from tests import advisor_cases as advisor

#: Which direction is asked about. Named here and not taken from the
#: fixture: `asking_from` derives the context field by field from the
#: window and none of those fields is the goal, so any direction gives the
#: same context -- and a guard that read the fixture's choice would be
#: agreeing with the thing it checks.
A_GOAL_ID = goals.MAX_DAMAGE.id

#: What the fixture is allowed to fill that the program leaves empty, and
#: why. All three are the armament grid, and the reason is one decision:
#: A17 takes the armaments out of the advisor's question because they are
#: rolled again every expedition (AK-191, AD-032). The stat sheet keeps
#: reading them, so a case that compares the advisor's arithmetic against
#: the window's build has to put them back -- and `GoalContext`'s own
#: docstring says as much: the fields stay "because the other question is
#: still asked from tests and will be asked again by A16".
#:
#: **This list may only shrink**, the same rule as `STILL_QUOTING`'s in
#: `test_exception_text_is_english.py`, and for the same reason: growing it
#: is how a second implementation comes back one field at a time.
THE_STAT_SHEET_KEEPS = ("reference", "weapons_held", "armament_effect_ids")


def fields_that_differ(mine, theirs) -> list[str]:
    """Every field of two `GoalContext`s that does not hold the same value.

    By field name off the dataclass rather than against a list written here:
    a field added to `GoalContext` is then compared from the day it exists,
    which is exactly the drift this file is about.
    """
    return [field.name for field in dataclasses.fields(mine)
            if getattr(mine, field.name) != getattr(theirs, field.name)]


def a_window_with_armaments(planner, data) -> None:
    """Put two armaments of different types on the grid, one with a roll.

    Without a grid the three allowances below are empty on both sides and
    the third question cannot be asked at all. The same helper the
    checkpoint-13 case uses for its state, so the two cannot come to mean
    different grids.
    """
    gate, carrier, other = advisor.an_armament_type_gate(
        data, planner.current_hero())
    slots = [weaponslots.WeaponSlot() for _ in range(weaponslots.SLOT_COUNT)]
    slots[0] = weaponslots.WeaponSlot(weapon=other, tier=3, effect_ids=[gate])
    slots[1] = weaponslots.WeaponSlot(weapon=carrier, tier=2)
    planner.weapon_slots = slots
    planner.active_weapon = 0


def a_planner_with_a_save(planner, game_data):
    if planner.owned is None:
        pytest.skip("this machine has no save, so the program asks nothing")
    a_window_with_armaments(planner, game_data)
    return planner


def test_the_fixture_goes_through_the_program(planner, game_data,
                                              monkeypatch):
    """The question QA-227 is really about: one implementation or two.

    A spy and not a comparison of values, because equal values are what a
    second implementation looks like on the day it is written. What has to
    hold is that there is nothing to keep in step in the first place.

    Red before the repair: the fixture assembled a `GoalContext` of its own
    and never called this.
    """
    a_planner_with_a_save(planner, game_data)
    asked: list[str] = []
    program = advisorbar.asking_from

    def spy(window, goal_id):
        asked.append(goal_id)
        return program(window, goal_id)

    monkeypatch.setattr(advisorbar, "asking_from", spy)

    advisor.context_from_planner(planner, game_data)

    assert asked, ("the fixture built a context of its own instead of asking "
                   "the program for one -- which is QA-227 returning")


def test_nothing_but_the_grid_differs_from_the_program(planner, game_data):
    """The second question: whatever the fixture did not mean to change.

    `hero`, `level`, `declared`, `data` and the weighting all have to be the
    program's, whoever changes one of them next. This is what fails if a
    fourth difference is introduced -- deliberately or not.
    """
    a_planner_with_a_save(planner, game_data)

    mine = advisor.context_from_planner(planner, game_data)
    theirs = advisorbar.asking_from(planner, A_GOAL_ID).ctx

    unexpected = set(fields_that_differ(mine, theirs)) - set(THE_STAT_SHEET_KEEPS)
    assert unexpected == set(), sorted(unexpected)


def test_every_allowance_is_still_a_difference(planner, game_data):
    """The third question, and the one that keeps the list above honest.

    An entry that is no longer a difference is not harmless: it says the
    fixture departs from the program where it does not, and the next reader
    believes it. Should A16 bring the armaments back into the program's own
    question, this is what says so -- and the answer is to take the line out
    of `THE_STAT_SHEET_KEEPS`, not to widen it.
    """
    a_planner_with_a_save(planner, game_data)

    mine = advisor.context_from_planner(planner, game_data)
    theirs = advisorbar.asking_from(planner, A_GOAL_ID).ctx

    for name in THE_STAT_SHEET_KEEPS:
        assert not getattr(theirs, name), (
            f"the program fills {name} again, so the allowance is stale")
        assert getattr(mine, name), (
            f"the fixture leaves {name} empty, so there is nothing to allow "
            f"-- the state this case builds was supposed to fill it")


def test_the_comparison_of_two_contexts_really_fires(planner, game_data):
    """The positive control, without which the two cases above measure a mask.

    Both assert that a set is empty, and an empty set is also what a
    comparison that has stopped comparing returns. Driven on a pair built
    here, one field apart.
    """
    a_planner_with_a_save(planner, game_data)
    one = advisorbar.asking_from(planner, A_GOAL_ID).ctx
    other = dataclasses.replace(one, level=one.level + 1)

    assert fields_that_differ(one, other) == ["level"]
    assert fields_that_differ(one, one) == []
