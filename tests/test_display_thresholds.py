"""The display thresholds are absolute, and stay where they are (AK-65).

`app.VISIBLE_CHANGE` is half of the smallest unit the breakdown can print. It
says "this change is not distinguishable from zero **on screen**" -- a
property of the display, not of the game. The 0.6 calibration made every
attack figure smaller, and QA-117 asked whether the threshold should follow
it so that the same *cases* keep their row. `UI_SPEC.md` AK-65 answers no,
and this file is what makes the answer break when somebody changes it.

**Two claims, and neither is enough on its own.** That the threshold is half
of what the display steps in, and that it is that threshold the panel really
uses. So the number is stated here with its recipe, and both directions are
also driven through the real panel, each on an armament searched for at run
time rather than written down:

* one whose `From attributes` figure lands in `[0.5, 0.5/0.6)` -- its row is
  on screen today and would disappear if the threshold were raised to keep
  the pre-calibration cases;
* one whose figure lands in `[0.5*0.6, 0.5)` -- its row is off screen today
  and would appear if the threshold were multiplied by the factor.

**The bands are worked out from `HALF_A_UNIT` below and never from
`app.VISIBLE_CHANGE`.** The first version of this file took them from the
constant it was testing, so both mutations of that constant moved the bands
with them and survived: 620 of 622 green, and the only failures were the
registry's own anchor checks (measured 2026-09-05). A guard that asks the
thing under test what to expect is not a guard.

The search is asserted to have found something, so a dataset where neither
band is occupied fails loudly instead of passing empty.
"""

from __future__ import annotations

import pytest

from nrplanner import app as appmod
from nrplanner import damage, model, weaponslots
from nrplanner.weapons import GAME_ATTACK_POWER_RATE, MIN_UPGRADE

from tests import weapon_damage_cases as cases

LEVEL = 15

#: The row this file is about, as `_ar_breakdown_text` writes it.
ROW = "From attributes"

#: Half of the smallest unit the breakdown can print. The panel writes this
#: figure with `f"{x:+.0f}"`, so one whole number is the smallest step it can
#: show and half of one is the point below which a change is not
#: distinguishable from zero. **Written out here rather than read off
#: `app.VISIBLE_CHANGE`, and that is the whole point of the file:** a case
#: that took its expectation from the constant under test would move with it,
#: and both mutations of that constant survived the first version of this
#: file for exactly that reason (measured 2026-09-05, 620 of 622 green).
SCREEN_UNIT = 1.0
HALF_A_UNIT = SCREEN_UNIT / 2

#: What a calibration-following edit would put in its place: the factor
#: applied, and the factor divided out. Both bands stay where they are when
#: the constant moves, which is what gives the two cases below their teeth.
LOWERED = HALF_A_UNIT * GAME_ATTACK_POWER_RATE
RAISED = HALF_A_UNIT / GAME_ATTACK_POWER_RATE


@pytest.fixture(scope="module")
def hero(game_data):
    return cases.hero_by_name(game_data, "Wylder")


@pytest.fixture(scope="module")
def raising_effect(game_data, hero):
    """One effect that lifts an attribute, found by asking what it does."""
    effect_id = cases.effects_raising_attribute(game_data, hero,
                                                "Dexterity", 1)[0]
    return cases.effect_by_id(game_data, effect_id)


@pytest.fixture(scope="module")
def gaps(game_data, hero, raising_effect):
    """`scaled - base` per armament, the figure the row would print."""
    curves = game_data.get("curves", {})
    bare = model.compute(hero, LEVEL, [], curves)
    raised = model.compute(hero, LEVEL, [raising_effect], curves)
    out = {}
    for weapon in model.offerable_weapons(game_data["weapons"]):
        before = damage.candidate(weapon, MIN_UPGRADE, bare, game_data)
        after = damage.candidate(weapon, MIN_UPGRADE, raised, game_data)
        out[weapon["id"]] = (after.scaled_headline - before.scaled_headline)
    return out


def an_armament_between(gaps, low: float, high: float) -> int:
    """The lowest-id armament whose figure lands in `[low, high)`."""
    found = sorted(weapon_id for weapon_id, gap in gaps.items()
                   if low <= abs(gap) < high)
    if not found:
        pytest.skip(
            f"no armament of this dataset moves by [{low}, {high}) for this "
            f"build, so the case cannot tell the thresholds apart")
    return found[0]


def breakdown_for(planner, game_data, hero, effect, weapon_id) -> str:
    """The breakdown text the panel really produces for this armament."""
    weapon = cases.weapon_by_id(game_data, weapon_id)
    slots = [weaponslots.WeaponSlot() for _ in range(weaponslots.SLOT_COUNT)]
    slots[0] = weaponslots.WeaponSlot(weapon=weapon, tier=MIN_UPGRADE)

    planner.hero_index = game_data["heroes"].index(hero)
    planner.weapon_slots = slots
    planner.declared = {}
    planner.active_weapon = 0
    planner.selected_effects = lambda: [effect]
    build = model.compute(hero, LEVEL, [effect],
                          game_data.get("curves", {}),
                          weapon=weapon, weapons_held=[weapon])
    planner._refresh_weapon_damage(build)
    return planner._ar_breakdown_text()


def test_the_threshold_is_half_a_printed_unit_and_not_a_calibrated_one(gaps):
    """AK-65's claim about the number itself, with its recipe beside it.

    The panel prints this figure as a whole number, so half of one is the
    point below which a change cannot be told from zero on screen. The two
    edits this rules out are the two the calibration invites: 0.5 x 0.6 and
    0.5 / 0.6, neither of which is half of anything the display prints.
    """
    assert appmod.VISIBLE_CHANGE == HALF_A_UNIT, (
        f"the threshold is {appmod.VISIBLE_CHANGE}, which is not half of the "
        f"{SCREEN_UNIT} this display steps in. Both readings the "
        f"calibration invites are here for comparison: {LOWERED} and "
        f"{RAISED}")
    assert LOWERED < HALF_A_UNIT < RAISED, (
        "the calibration factor is no longer below 1, so 'raised' and "
        "'lowered' have swapped and these cases read backwards")
    assert any(HALF_A_UNIT <= abs(gap) < RAISED for gap in gaps.values())
    assert any(LOWERED <= abs(gap) < HALF_A_UNIT for gap in gaps.values())


def test_a_row_just_over_the_threshold_is_shown(planner, game_data, hero,
                                                raising_effect, gaps):
    """It would vanish if the threshold followed the calibration upwards."""
    weapon_id = an_armament_between(gaps, HALF_A_UNIT, RAISED)
    text = breakdown_for(planner, game_data, hero, raising_effect, weapon_id)

    assert ROW in text, (
        f"armament {weapon_id} moves by {gaps[weapon_id]:.4f}, which clears "
        f"the absolute threshold {HALF_A_UNIT} and not a threshold "
        f"scaled to {RAISED:.4f}. Its row is missing: {text!r}")


def test_a_row_just_under_the_threshold_is_not_shown(planner, game_data,
                                                     hero, raising_effect,
                                                     gaps):
    """It would appear if the threshold followed the calibration downwards."""
    weapon_id = an_armament_between(gaps, LOWERED, HALF_A_UNIT)
    text = breakdown_for(planner, game_data, hero, raising_effect, weapon_id)

    assert ROW not in text, (
        f"armament {weapon_id} moves by {gaps[weapon_id]:.4f}, which is under "
        f"the absolute threshold {HALF_A_UNIT} and over one scaled "
        f"to {LOWERED:.4f}. Its row is on screen: {text!r}")


@pytest.mark.parametrize("rate", [0.5, 0.7])
def test_recalibrating_moves_no_threshold(monkeypatch, rate):
    """AK-65 in its own words: a new factor moves cases, never thresholds.

    **What this case does not catch, said out loud:** a threshold written as
    `0.5 * GAME_ATTACK_POWER_RATE` is worked out once at import, so patching
    the factor afterwards does not move it and this case stays green. That
    form is caught by the two cases above, which read the panel instead. What
    is caught here is the other shape of the same mistake -- a threshold that
    consults the factor when it is used.
    """
    from nrplanner import weapons

    before = (appmod.VISIBLE_CHANGE, appmod.VISIBLE_PERCENT,
              appmod.COLOURED_CHANGE)
    monkeypatch.setattr(weapons, "GAME_ATTACK_POWER_RATE", rate)

    assert (appmod.VISIBLE_CHANGE, appmod.VISIBLE_PERCENT,
            appmod.COLOURED_CHANGE) == before, (
        f"a calibration of {rate} moved a display threshold, which is the "
        f"one thing AK-65 forbids")
