"""The `1H`/`2H` switch: one per build, saved with it, and what it decides.

AK-292: a checkable word button between the six armament tiles and the AR
caption, `1H` by default, part of the build rather than of the session.
AK-293: it decides which hand the damage direction ranks -- the mean of the
attack multipliers takes the `when Two-Handing` bucket only two-handed, and
with a reference armament the two-handed figure is ranked where the armament
has one -- and it changes no figure a display shows. A toggle while Optimize
is working ends the run in 4.7, not in the AK-289 marking sentence. T-255c.

The frozen save carries five copies with a `when Two-Handing` effect and all
five are `Improved Stance-Breaking when Two-Handing` (7006000/7006001), which
moves no attack rating -- so the ranking cases below build their copies on
the real dataset instead of reading them off the frozen save.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt

from nrplanner import advisorbar, chalices, damage, model, statsheet
from nrplanner.advisor import candidates, goals, run, types

from tests import advisor_cases as advisor
from tests import weapon_damage_cases as cases
from tests.conftest import _new_planner, wait_for_the_save

HERO = 1
VESSEL = 7
SLOTS = ["5|1|2,3|", "", "", "", "", ""]
DAMAGE = goals.MAX_DAMAGE.id
#: `Improved Attack Power when Two-Handing`, the first payload tier (x1.12).
TWO_HANDING_BUFF = 8300000
#: `Physical Attack Up +3`, an ordinary attack rate (x1.105) on either hand.
ORDINARY_BUFF = 6001400


# -- the store: part of the build, no schema step ---------------------------

def test_a_record_written_before_the_switch_reads_one_handed():
    old = chalices.FIELD.join(["7", "0"] + SLOTS)
    assert chalices._decode(old) == (7, False, SLOTS, False)


def test_one_handed_is_stored_exactly_as_every_build_before_the_switch_was():
    assert chalices._encode(7, False, SLOTS) == chalices.FIELD.join(
        ["7", "0"] + SLOTS)
    assert chalices._encode(7, False, SLOTS, True) == chalices.FIELD.join(
        ["7", "0"] + SLOTS + [chalices.TWO_HANDED])


def test_the_hand_round_trips_through_both_stores(qapp):
    from tests.conftest import clear_settings

    clear_settings()
    chalices.save(HERO, VESSEL, False, SLOTS, True)
    assert chalices.load(HERO, VESSEL) == (VESSEL, False, SLOTS, True)
    chalices.save(HERO, VESSEL, False, SLOTS)
    assert chalices.load(HERO, VESSEL)[3] is False
    chalices.save_build(HERO, "both hands", VESSEL, False, SLOTS, True)
    assert chalices.load_build(HERO, "both hands") == (VESSEL, False, SLOTS,
                                                       True)


# -- the switch on the sheet -------------------------------------------------

def test_the_switch_sits_between_the_tiles_and_the_ar_caption(planner):
    sheet = planner.stat_sheet
    layout = sheet.widget().layout()
    switch_at = layout.indexOf(sheet.hand_switch)
    assert switch_at == layout.indexOf(sheet.ar_label) - 1
    assert layout.itemAt(switch_at - 1).layout() is not None, \
        "the item before the switch is the tile grid"
    assert layout.itemAt(switch_at).alignment() & Qt.AlignLeft


def test_the_switch_reads_1h_by_default_and_2h_checked(planner):
    switch = planner.stat_sheet.hand_switch
    assert switch.isCheckable()
    assert not switch.isChecked() and switch.text() == "1H"
    assert switch.toolTip() == statsheet.HAND_TOOLTIP
    assert switch.focusPolicy() & Qt.TabFocus
    switch.setChecked(True)
    assert switch.text() == "2H"
    assert switch.toolTip() == statsheet.HAND_TOOLTIP


def test_a_toggle_reaches_the_advisor_as_a_build_change_not_a_marking(
        planner, monkeypatch):
    heard = []
    monkeypatch.setattr(planner.advisor_bar, "the_build_changed",
                        lambda **kwargs: heard.append(kwargs))
    planner.stat_sheet.hand_switch.click()
    assert heard == [{}]
    assert advisorbar.status_line(advisorbar.Situation(
        advisorbar.State.OUTDATED)) == (
        "Your build changed while this was working out — use Optimize "
        "again.")


def test_the_ask_carries_the_hand_in_context_and_key(planner):
    planner.stat_sheet.hand_switch.setChecked(True)
    asking = advisorbar.asking_from(planner, DAMAGE)
    assert asking.ctx.two_handed is True
    assert asking.request.two_handed is True


def test_the_hand_survives_a_restart(game_data, qapp):
    first = _new_planner(game_data)
    try:
        hero_id = first.current_hero()["id"]
        vessel_id = first.current_vessel()["id"]
        assert any(chalices.load(hero_id, vessel_id)[2]), \
            "a build with something in it, or nothing is stored"
        first.stat_sheet.hand_switch.click()
        assert chalices.load(hero_id, vessel_id)[3] is True
    finally:
        first.close()
        first.deleteLater()

    from nrplanner import app as appmod

    second = wait_for_the_save(appmod.Planner(game_data))
    try:
        assert second.current_vessel()["id"] == vessel_id
        assert second.stat_sheet.hand_switch.isChecked()
        assert second.stat_sheet.hand_switch.text() == "2H"
    finally:
        second.close()
        second.deleteLater()


# -- what the hand decides in the ranking -----------------------------------

@pytest.fixture(scope="module")
def wylder(game_data):
    return cases.hero_by_name(game_data, "Wylder")


def _built(game_data, wylder, *effect_ids):
    return model.compute(wylder, advisor.LEVEL,
                         [cases.effect_by_id(game_data, e) for e in effect_ids],
                         game_data.get("curves", {}))


def test_the_two_handing_bucket_counts_in_the_mean_two_handed_only(
        game_data, wylder):
    build = _built(game_data, wylder, TWO_HANDING_BUFF)
    assert goals._attack_multiplier_mean(build, two_handed=False) == 1.0
    assert goals._attack_multiplier_mean(build, two_handed=True) == \
        pytest.approx(1.12, abs=1e-6)


def test_the_order_of_two_relics_turns_with_the_hand(game_data, wylder):
    owned = advisor.make_inventory(
        game_data, wylder, count=2,
        rolls=[[TWO_HANDING_BUFF], [ORDINARY_BUFF], [ORDINARY_BUFF]])
    problem = advisor.problem((advisor.RED,))
    by_hand = {}
    for two_handed in (False, True):
        ctx = advisor.context(game_data, wylder, two_handed=two_handed)
        pool = candidates.pool(owned, problem, 0, ctx, goals.GOALS, DAMAGE)
        by_hand[two_handed] = [
            (candidate.effect_ids[0],
             round(types.marginal_for(candidate, DAMAGE), 4))
            for candidate in pool.candidates]
    # A single field's +10.5 % is +2.1 % on the mean of five; the
    # two-handing buff lifts all five, so two-handed it is +12 % outright.
    assert by_hand[False] == [(ORDINARY_BUFF, 0.021), (TWO_HANDING_BUFF, 0.0)]
    assert by_hand[True] == [(TWO_HANDING_BUFF, 0.12), (ORDINARY_BUFF, 0.021)]


def test_a_key_that_names_the_other_hand_is_refused(game_data, wylder):
    owned = advisor.make_inventory(game_data, wylder, count=1)
    problem = advisor.problem((advisor.RED,))
    ctx = advisor.context(game_data, wylder, two_handed=True)
    frozen = run.frozen_inventory(owned, problem)
    request = advisor.request_for(problem, ctx, frozen)
    run._refuse_a_request_that_asks_about_another_run(request, frozen, ctx)
    with pytest.raises(ValueError, match="two_handed"):
        run._refuse_a_request_that_asks_about_another_run(
            request, frozen, advisor.context(game_data, wylder))


def test_with_a_reference_armament_the_two_handed_figure_is_ranked(
        game_data, wylder):
    reference = advisor.scaling_armament(game_data, wylder)
    build = _built(game_data, wylder)
    _bare, now = damage.equipped(reference, reference.slot_index, build,
                                 wylder, game_data)
    assert now.two_handed is not None
    one = goals._max_damage(build, advisor.context(game_data, wylder,
                                                   reference=reference))
    two = goals._max_damage(build, advisor.context(game_data, wylder,
                                                   reference=reference,
                                                   two_handed=True))
    assert one.value == now.final_headline
    assert two.value == now.two_handed.final_headline
    assert two.value > one.value


def test_an_armament_without_a_second_figure_keeps_its_one_two_handed(
        game_data, wylder):
    bow = cases.weapon_by_id(game_data, cases.first_of_family(game_data, "Bow"))
    reference = types.ReferenceArmament(weapon=bow, tier=1, slot_index=0)
    build = _built(game_data, wylder)
    two = goals._max_damage(build, advisor.context(game_data, wylder,
                                                   reference=reference,
                                                   two_handed=True))
    assert two.value == damage.equipped(reference, 0, build, wylder,
                                        game_data)[1].final_headline


def test_the_switch_changes_no_figure_the_sheet_shows(game_data, wylder):
    """AK-293 point 1: both hands stay side by side whatever the switch says
    -- the facade is never asked about the switch at all."""
    build = _built(game_data, wylder, TWO_HANDING_BUFF)
    weapon = advisor.scaling_armament(game_data, wylder).weapon
    rating = damage.candidate(weapon, 1, build, game_data)
    assert rating.two_handed.rates and not rating.rates
