"""An exclusivity group is worth one effect, wherever it is added up (QA-257).

`GOAL.md` A4: the advisor respects the program's own stacking rules, and
"not stackable" effects are not counted twice. `stacking.repetition` calls an
effect with a positive `exclusivity` an `EXCLUSIVE` one -- "one of the group
applies" -- and until T-242 `model.compute` only warned about that while
adding every copy up. On the real save the advisor then filled two slots
with `[Revenant] Improved Strength, Reduced Faith` and showed Strength +50.

The rule lives in `model.compute` and nowhere else (`advisor/search.py`
scores with the real scorer), so the cases here ask the model, the run and
the reasons in turn, and every effect is found by a property of the dataset
-- never by an id written down here.
"""

from __future__ import annotations

import pytest

from nrplanner import model, stacking
from nrplanner.advisor import explain, goals, run, types
from nrplanner.advisor.evaluate import evaluate

from tests import advisor_cases as advisor
from tests import weapon_damage_cases as cases

ATTRIBUTES = "max_attributes"
DAMAGE = "max_damage"
ONLY_ONE_APPLIES = "only one will apply"


def an_exclusive_attribute_effect(data: dict, hero: dict) -> dict:
    """The lowest-numbered `EXCLUSIVE` effect that raises an offensive
    attribute here -- one the attribute direction can see.

    Asked of `stacking.repetition` -- the Effects tab's own word for it -- so
    the case binds the tab's classification to the model's arithmetic, which
    is the pair QA-257 found disagreeing.
    """
    curves = data.get("curves", {})
    for key in sorted(data["effects"], key=int):
        effect = data["effects"][key]
        if stacking.repetition(effect) != stacking.EXCLUSIVE:
            continue
        built = model.compute(hero, advisor.LEVEL, [effect], curves)
        if any(built.attributes.get(a, 0) > built.base_attributes.get(a, 0)
               for a in goals.OFFENSIVE_ATTRIBUTES):
            return effect
    pytest.skip("this dataset has no exclusive-group effect raising an "
                "offensive attribute for this Nightfarer")


def two_members_of_one_group_moving_a_rate(data: dict, hero: dict
                                           ) -> tuple[dict, dict]:
    """Two different effects of one exclusivity group that each move a rate."""
    curves = data.get("curves", {})
    by_group: dict[int, list[dict]] = {}
    for key in sorted(data["effects"], key=int):
        effect = data["effects"][key]
        if stacking.repetition(effect) != stacking.EXCLUSIVE:
            continue
        if model.compute(hero, advisor.LEVEL, [effect], curves).rates:
            by_group.setdefault(effect["exclusivity"], []).append(effect)
    for group in by_group.values():
        if len(group) >= 2:
            return group[0], group[1]
    pytest.skip("this dataset has no exclusivity group with two members "
                "that move a rate")


def a_stacking_attribute_effect(data: dict, hero: dict) -> int:
    """An ordinary attribute raiser -- one the game does stack."""
    for effect_id in cases.effects_raising_attribute(data, hero, "Strength", 6):
        if stacking.repetition(data["effects"][str(effect_id)]) == stacking.STACKS:
            return effect_id
    pytest.skip("this dataset has no stacking Strength raiser")


def figures(build: model.Build) -> tuple[dict, dict, dict]:
    return dict(build.attributes), dict(build.rates), dict(build.other)


# -- the model --------------------------------------------------------------

def test_two_copies_of_an_exclusive_effect_are_worth_one(game_data, revenant):
    """Red before T-242: Strength +50 and no warning for `[e, e]`."""
    effect = an_exclusive_attribute_effect(game_data, revenant)
    curves = game_data.get("curves", {})

    once = model.compute(revenant, advisor.LEVEL, [effect], curves)
    twice = model.compute(revenant, advisor.LEVEL, [effect, effect], curves)

    assert figures(twice) == figures(once), (
        "the second copy of an exclusive-group effect moved a total")
    assert once.warnings == []
    assert [w.kind for w in twice.warnings] == ["exclusive"]
    assert ONLY_ONE_APPLIES in twice.warnings[0].text
    assert " ".join(effect["name"].split()) in twice.warnings[0].text


def test_two_members_of_one_group_are_worth_the_first(game_data, wylder):
    """Different names, one group: the first equipped counts, the other is
    named in the warning beside it."""
    first, second = two_members_of_one_group_moving_a_rate(game_data, wylder)
    curves = game_data.get("curves", {})

    alone = model.compute(wylder, advisor.LEVEL, [first], curves)
    both = model.compute(wylder, advisor.LEVEL, [first, second], curves)

    assert figures(both) == figures(alone)
    assert [w.kind for w in both.warnings] == ["exclusive"]
    for effect in (first, second):
        assert " ".join(effect["name"].split()) in both.warnings[0].text
    assert ONLY_ONE_APPLIES in both.warnings[0].text


# -- the advisor ------------------------------------------------------------

def test_the_advisor_does_not_fill_two_slots_from_one_group(game_data,
                                                             revenant):
    """The Revenant case of QA-257, on a made inventory.

    Two copies of the exclusive effect and one plainly weaker stacking one:
    with the doubling, the pair scores highest; without it the second copy is
    worth nothing and the weaker relic wins the slot.
    """
    exclusive = int(an_exclusive_attribute_effect(game_data, revenant)["id"])
    weaker = a_stacking_attribute_effect(game_data, revenant)
    owned = advisor.make_inventory(
        game_data, revenant, count=3,
        rolls=[[exclusive], [exclusive], [weaker]])
    problem = advisor.problem([advisor.RED, advisor.RED])
    ctx = advisor.context(game_data, revenant)
    frozen = run.frozen_inventory(owned, problem)
    request = advisor.request_for(problem, ctx, frozen, ATTRIBUTES)

    result = run.run(request, frozen, ctx, goals.GOALS)

    chosen = {choice.handle for choice in result.suggestions[0].choices}
    carrying = [relic.handle for relic in owned.relics
                if exclusive in relic.effect_ids]
    assert len(chosen) == 2
    assert len(chosen & set(carrying)) == 1, (
        f"both copies of the exclusive effect were suggested: {chosen}")


def test_the_second_copy_of_the_group_says_it_is_already_counted(
        game_data, revenant):
    """`Why` names the copy that did not count, in the wording the second
    copy of an `isStrongestEffect` gets (AK-167 (a2))."""
    exclusive = int(an_exclusive_attribute_effect(game_data, revenant)["id"])
    owned = advisor.make_inventory(game_data, revenant, count=2,
                                   rolls=[[exclusive], [exclusive]])
    problem = advisor.problem([advisor.RED, advisor.RED])
    ctx = advisor.context(game_data, revenant)
    frozen = run.frozen_inventory(owned, problem)
    request = advisor.request_for(problem, ctx, frozen, ATTRIBUTES)

    result = run.run(request, frozen, ctx, goals.GOALS)

    first, second = result.suggestions[0].reasons
    assert first.effects_with_a_figure == 1
    assert [line.silence for line in second.lines] == [
        types.SILENT_ALREADY_COUNTED], (
        f"the second copy is not named as uncounted: "
        f"{[line.text for line in second.lines]}")
    assert "already counted" in second.lines[0].text


def test_another_member_of_the_group_says_the_group_is_already_counted(
        game_data, wylder):
    """A different effect of the same group is silent for the same reason,
    and the line says so rather than `no number here`."""
    first, second = two_members_of_one_group_moving_a_rate(game_data, wylder)
    problem = advisor.problem([advisor.RED, advisor.RED])
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data, wylder))
    chosen = tuple(
        types.Candidate(slot_index=index, handle=100 + index,
                        relic_id=9100 + index, name=f"Copy {index}",
                        colour=advisor.RED, is_deep=False,
                        effect_ids=(int(effect["id"]),), curse_ids=())
        for index, effect in enumerate((first, second)))

    counted, silent = explain.reasons(
        problem, chosen, evaluate(problem, (), ctx),
        evaluate(problem, chosen, ctx), ctx, goals.GOALS[DAMAGE])

    assert counted.effects_with_a_figure == 1
    assert [line.silence for line in silent.lines] == [
        types.SILENT_ALREADY_COUNTED]
    assert "only one effect of its group" in silent.lines[0].text
