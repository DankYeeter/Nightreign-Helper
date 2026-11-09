"""`Balanced`: damage and survival at once (T-339.3, user decision 2026-11-07).

The value joins the damage figure and the survival figure, each as a multiple of
the Nightfarer with no relic, in a mean that lets the half behind count more
(`goals.BALANCE_CURVATURE`, second user decision 2026-11-07): no rate between
them, no dial. AD-023 and OF-13 keep ruling out a rate; multiples need none.
"""

from __future__ import annotations

import dataclasses

from nrplanner import advisorbar, model, relicpicker
from nrplanner.advisor import explain, goals, run, types
from nrplanner.advisor.evaluate import evaluate

from tests import advisor_cases as advisor

BALANCED = goals.BALANCED


def _armament_of(game_data, hero):
    return types.ReferenceArmament(
        weapon=next(weapon for weapon in game_data["weapons"]
                    if weapon["id"] == hero["starting_weapon"]),
        tier=1, slot_index=0)


def test_the_value_balances_the_two_multiples_of_the_bare_nightfarer(question):
    inventory, problem, ctx, _request = question
    built = evaluate(problem, (), ctx, goal=BALANCED)
    damage_figure = goals.MAX_DAMAGE.score(built, ctx)
    survival = goals.MIN_DAMAGE_TAKEN.score(built, ctx)
    bare = model.compute(ctx.hero, ctx.level, [], ctx.data.get("curves", {}),
                         weapon=ctx.reference.weapon,
                         weapons_held=list(ctx.weapons_held))
    damage_base = goals.MAX_DAMAGE.score(bare, ctx).value
    survival_base = goals.MIN_DAMAGE_TAKEN.score(bare, ctx).value
    score = BALANCED.score(built, ctx)
    assert score.value == goals.balanced_value(
        damage_figure.value / damage_base, survival.value / survival_base)
    assert score.display == (
        f"{damage_figure.display}{types.FIGURES_JOIN}{survival.display}")


def test_equal_multiples_give_that_multiple_back():
    assert abs(goals.balanced_value(1.3, 1.3) - 1.3) < 1e-12
    assert abs(goals.balanced_value(1.0, 1.0) - 1.0) < 1e-12


def test_the_half_that_is_behind_counts_more():
    """User decision 2026-11-07: the product leaned to AR +75 % / Defense
    +7 %. One step of the lagging half must now beat a bigger step of the
    leading one, which a product (log-additive) never did."""
    leading = goals.balanced_value(1.75 * 1.12, 1.07)
    lagging = goals.balanced_value(1.75, 1.07 * 1.068)
    assert lagging > leading
    assert 1.75 * 1.12 * 1.07 > 1.75 * 1.07 * 1.068


def test_it_rises_with_either_half():
    base = goals.balanced_value(1.5, 1.2)
    assert goals.balanced_value(1.51, 1.2) > base
    assert goals.balanced_value(1.5, 1.21) > base


def test_the_tooltip_works_out_both_percentages():
    row = _row(1, 1.0, "Attack rating 276 / Effective HP 1284")
    first, ar_line, defense_line = advisorbar.how_the_figures_read(row)
    assert first == "AR 158 → 276 (+75 %), Defense 1200 → 1284 (+7 %)."
    assert ar_line == advisorbar.AR_READS
    assert "strongest physical damage negation" in defense_line
    assert "quarter" in defense_line and "HP" in defense_line


def test_both_figures_are_positive_for_every_nightfarer(game_data):
    """A product only ranks over positive figures; the armament-less fallback
    and each Nightfarer's own armament, relics or none."""
    model.configure(game_data)
    for hero in game_data["heroes"]:
        problem = advisor.problem([advisor.RED])
        for reference in (_armament_of(game_data, hero), None):
            ctx = advisor.context(game_data, hero, reference=reference)
            built = evaluate(problem, (), ctx, goal=BALANCED)
            assert goals.MAX_DAMAGE.score(built, ctx).value > 0, hero["name"]
            assert goals.MIN_DAMAGE_TAKEN.score(built, ctx).value > 0


def test_the_hidden_boxes_do_not_reach_it(game_data, wylder):
    """`Hit with` and `Damage type` are hidden under this direction (AK-337):
    a type the armament deals none of would otherwise zero the whole product."""
    problem = advisor.problem([advisor.RED])
    ctx = advisor.context(game_data, wylder,
                          reference=_armament_of(game_data, wylder))
    built = evaluate(problem, (), ctx, goal=BALANCED)
    asked = dataclasses.replace(ctx, damage_type="Dark",
                                hit_with=model.SKILL_ART)
    assert BALANCED.score(built, asked) == BALANCED.score(built, ctx)
    assert BALANCED.score(built, ctx).value > 0


def test_it_is_a_direction_like_the_others(question):
    """Registry, comparison and scope: a run answers it end to end, and the
    suggestion's value is the product of the suggestion's own build."""
    assert goals.OTHER_GOAL[BALANCED.id] == goals.MAX_DAMAGE.id
    assert BALANCED.scope
    inventory, problem, ctx, request = question
    asked = dataclasses.replace(request, goal_id=BALANCED.id)
    result = run.run(asked, inventory, ctx, goals.GOALS)
    best = result.suggestions[0]
    assert types.FIGURES_JOIN in best.score.display
    assert types.FIGURES_JOIN in result.no_relics_display
    assert best.score.value >= next(line.value for line in result.baseline
                                    if line.goal_id == BALANCED.id)


def test_an_attribute_line_says_no_amount_under_it(game_data, wylder):
    """`{body} → {rating} {delta}` would print a product nobody can read."""
    effect_id = advisor.raising_effects(game_data, wylder, 1)[0][0]
    armament = _armament_of(game_data, wylder)
    owned = advisor.make_inventory(game_data, wylder, count=1,
                                   rolls=[[effect_id]])
    problem = advisor.problem([advisor.RED])
    ctx = advisor.context(game_data, wylder, reference=armament)
    frozen = run.frozen_inventory(owned, problem)
    pool = run.candidates.pools(frozen, problem, ctx, goals.GOALS,
                                BALANCED.id)[0]
    chosen = pool.candidates[:1]
    built = evaluate(problem, chosen, ctx, goal=BALANCED)
    base = evaluate(problem, (), ctx, goal=BALANCED)
    group, = explain.reasons(problem, chosen, base, built, ctx, BALANCED)
    assert group.lines
    assert all("→" not in line.text and types.FIGURES_JOIN not in line.text
               for line in group.lines), [line.text for line in group.lines]


def test_a_card_says_it_as_a_percentage_of_the_base():
    """The mark of AK-45 is decided on this same text."""
    pool = types.SlotPool(
        slot_index=0, rank_by=BALANCED.id,
        baseline=(types.Baseline(BALANCED.id, 200000.0, "", ()),),
        candidates=(), unknowns=())
    ranking = relicpicker.Ranking(pool)
    assert ranking.text_of(20000.0, BALANCED.id) == "+10.0 %"
    assert ranking.text_of(-20000.0, BALANCED.id) == "-10.0 %"
    assert ranking.text_of(0.0, BALANCED.id) == relicpicker.NO_CHANGE


# -- the vessel list (AK-478) ------------------------------------------------

def _row(vessel_id, value, figure, base=("Attack rating 158 / Effective HP 1200")):
    return types.VesselRow(vessel_id=vessel_id, figure=figure, value=value,
                           base_figure=base)


def _comparing(*rows):
    return advisorbar.Comparing(
        goal_label="Balanced", other_label="Maximise damage",
        vessel_ids=tuple(row.vessel_id for row in rows), asked_vessel=1,
        held_relics=0, carries=False, signature=(),
        rows={row.vessel_id: row for row in rows},
        state=advisorbar.Compared.DONE)


def test_a_vessel_row_leads_with_both_percentages_and_sorts_by_the_value():
    """The higher product is best though its attack rating is lower."""
    sharp = _row(1, 299.0 * 1300, "Attack rating 299 / Effective HP 1300")
    even = _row(2, 261.0 * 1602, "Attack rating 261 / Effective HP 1602")
    comparing = _comparing(sharp, even)
    assert comparing.ranked()[0] is even
    assert advisorbar.vessel_line(comparing, 2) == (
        "", "AR +65 % / Defense +34 %")
    assert advisorbar.vessel_line(comparing, 1) == (
        "", "AR +89 % / Defense +8 %")


def test_a_loss_keeps_its_sign_and_the_status_line_names_no_gap():
    """A gap in a product is no number; a negative percentage stands signed."""
    best = _row(1, 261.0 * 1602, "Attack rating 261 / Effective HP 1602")
    here = _row(2, 150.0 * 1100, "Attack rating 150 / Effective HP 1100")
    comparing = _comparing(best, here)
    assert advisorbar.vessel_line(comparing, 2) == (
        "", "AR -5 % / Defense -8 %")
    line, target = advisorbar.comparison_status(
        comparing, 2, None, {1: "Urn", 2: "Goblet"})
    assert line == ("Best of 2 for Balanced: Urn — AR +65 % / Defense +34 %.")
    assert target == 1


def test_a_staff_says_its_own_word_and_a_bare_multiplier_says_damage():
    staff = types.VesselRow(
        vessel_id=1, value=1.0, figure="Spell power 120 / Effective HP 1300",
        base_figure="Spell power 100 / Effective HP 1300")
    assert advisorbar._with_its_base(staff) == "Spell +20 % / Defense +0 %"
    bare = types.VesselRow(
        vessel_id=1, value=1.0, figure="Attack multipliers ×1.20 / Effective HP 1300",
        base_figure="Attack multipliers ×1.00 / Effective HP 1300")
    assert advisorbar._with_its_base(bare) == "Damage +20 % / Defense +0 %"


def test_the_other_directions_keep_their_line():
    row = types.VesselRow(vessel_id=1, value=90.0, figure="Attack rating 90",
                          base_figure="Attack rating 56")
    assert advisorbar._with_its_base(row) == "AR 90 (+61 %)"


def test_the_control_words_come_from_the_registry():
    assert BALANCED.label == "Balanced"
    assert relicpicker.VALUE_CAPTIONS[BALANCED.id] == "Balanced"
    assert relicpicker.chip_text(BALANCED.id) == "BEST FOR BALANCE"


def test_a_share_runs_from_no_relics_to_the_best_alone():
    """User proposal 2026-11-08: each side over its own best."""
    assert goals.share_of_the_best(72, 72, 122) == 0
    assert goals.share_of_the_best(122, 72, 122) == 1
    assert goals.share_of_the_best(97, 72, 122) == 0.5
    assert goals.share_of_the_best(80, 80, 80) == 1.0


def test_halfway_on_both_beats_all_on_one():
    both = goals.balanced_by_span(0.5, 0.5)
    assert both > goals.balanced_by_span(1.0, 0.0)
    assert both > goals.balanced_by_span(0.0, 1.0)
    assert goals.balanced_by_span(0.6, 0.6) > goals.balanced_by_span(0.9, 0.3)
