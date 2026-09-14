"""No raw field name stands beside a number on the screen (AK-295, QA-269).

Three rules, each with its own case here: one lookup names a figure
(`effecttext.field_label`), a HP threshold is a condition and not a bonus
(`conditionHp`/`conditionHpRate` never reach a Why line or `Flat bonuses`),
and a field nobody named gives the A7 sentence instead of the field.
"""

from __future__ import annotations

import re

from nrplanner import effecttext, model
from nrplanner.advisor import explain, goals, types
from nrplanner.advisor.evaluate import evaluate

from tests import advisor_cases as advisor
from tests import weapon_damage_cases as cases

#: What QA-269 saw: a camelCase field beside a signed number.
RAW_FIELD_BESIDE_A_NUMBER = re.compile(r": [a-z]+[A-Z]\w* [+-]")


def test_field_label_is_the_one_lookup_over_both_tables():
    """Point 1: an attribute is its own name, then the sheet's table, then
    the tables `describe` reads, and `None` -- not the key -- where none has
    a name."""
    assert effecttext.field_label("Vigor") == "Vigor"
    assert effecttext.field_label("physicsAttackRate") == model.label_for(
        "physicsAttackRate")
    assert effecttext.field_label("physicsAttackPower") == (
        "Physical attack power")
    assert effecttext.field_label("neverNamedField") is None


def _reasons_for(sources: dict, names: dict[int, str]) -> tuple[str, ...]:
    ctx = types.GoalContext(
        data={"effects": {str(eid): {"id": eid, "name": name}
                          for eid, name in names.items()}},
        hero={}, level=advisor.LEVEL, reference=None,
        weighting=goals.DEFAULT_WEIGHTING)
    built = model.Build(sources={key: [model.SourceEntry(*entry)
                                       for entry in entries]
                                 for key, entries in sources.items()})
    copy = types.Candidate(slot_index=0, handle=1, relic_id=9001,
                           name="A relic", colour=advisor.RED, is_deep=False,
                           effect_ids=tuple(names), curse_ids=())
    groups = explain.reasons(advisor.problem([advisor.RED]), (copy,),
                             model.Build(), built, ctx,
                             goals.GOALS["min_damage_taken"])
    return tuple(line.text for group in groups for line in group.lines)


def test_a_why_line_names_the_field_or_says_it_has_no_name():
    """Points 1 to 3 on one hand-built copy: the `effecttext` name for the
    QA-113 field, the A7 sentence for a field nobody named, and no line at
    all for the threshold -- the effect that moved nothing else falls to the
    silent filling rather than showing `conditionHp +40`."""
    lines = _reasons_for(
        {"physicsAttackPower": [("Starting armament deals magic damage",
                                 -30.0, 1)],
         "neverNamedField": [("Odd effect", 3.0, 2)],
         "conditionHp": [("Slowly restore HP when HP is low", 40.0, 3)]},
        {1: "Starting armament deals magic damage", 2: "Odd effect",
         3: "Slowly restore HP when HP is low"})

    assert lines == (
        "Starting armament deals magic damage: Physical attack power -30, "
        "counted against it",
        "Odd effect: carries a number this program has not labelled yet.",
        "Slowly restore HP when HP is low: no number here shows what this "
        "adds.",
    )


def test_the_frozen_save_shows_no_raw_field_in_any_why_line(game_data,
                                                             frozen_inventory):
    """QA-269's own case: every copy of the frozen save alone in a white slot
    under `Minimise damage taken` with the A18 baseline declared. 264 of 360
    line bodies carried a raw field before; now none does, and the QA-113
    conversion reads with the name `effecttext` has had for it all along."""
    hero = cases.hero_by_name(game_data, "Wylder")
    ctx = advisor.context(game_data, hero,
                          declared=tuple(model.advisor_defaults().items()))
    lines: list[str] = []
    for item in frozen_inventory.relics:
        question = advisor.problem([advisor.WHITE], deep=item.is_deep)
        alone = types.Candidate(
            slot_index=0, handle=item.handle, relic_id=item.relic_id,
            name=item.name, colour=item.colour, is_deep=item.is_deep,
            effect_ids=tuple(item.effect_ids), curse_ids=tuple(item.curse_ids))
        groups = explain.reasons(question, (alone,), evaluate(question, (), ctx),
                                 evaluate(question, (alone,), ctx), ctx,
                                 goals.GOALS["min_damage_taken"])
        lines += [line.text for group in groups for line in group.lines]

    raw = [line for line in lines if RAW_FIELD_BESIDE_A_NUMBER.search(line)]
    assert raw == []
    assert not any("conditionHp" in line for line in lines)
    assert ("Starting armament deals magic damage: Physical attack power -30, "
            "counted against it") in lines


def test_the_flat_bonuses_carry_no_threshold_and_no_raw_field(planner):
    """Points 2 and 3 on the sheet: `conditionHp` is not a bonus and is not
    listed; a field nobody named is the A7 sentence under the effects that
    carry it, not the field beside a number."""
    build = planner.current_build()
    build.other.update({"conditionHp": 40.0, "neverNamedField": 3.0,
                        "runeDiscountValue": 5.0})
    build.sources["neverNamedField"] = [
        model.SourceEntry("Odd effect", 3.0, 1),
        model.SourceEntry("Another odd effect", 3.0, 2)]
    build.sources["conditionHp"] = [
        model.SourceEntry("Slowly restore HP when HP is low", 40.0, 3)]
    planner.stat_sheet.draw(build, {})

    text = planner.stat_sheet.other_label.text()
    # Not listed at all -- neither as the field, nor as its carrier under
    # the A7 sentence: the threshold belongs to the Situational row.
    assert "conditionHp" not in text
    assert "Slowly restore HP when HP is low" not in text
    assert "neverNamedField" not in text
    assert ("Another odd effect, Odd effect: carries a number this program "
            "has not labelled yet.") in text
    assert "Shop discount %" in text
