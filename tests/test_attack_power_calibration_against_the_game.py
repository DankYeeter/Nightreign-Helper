"""The two measured pairing factors hit the numbers the game showed in play.

`tests/test_attack_power_against_the_game.py` holds the plain formula and
`GAME_ATTACK_POWER_RATE` against a community sheet, and its header leaves two
pairings out on purpose: the Raider on a greataxe or great hammer, and
Revenant's Cursed Claws in anyone else's hands. The sheet reads x1.18 and
x0.88 off the formula there, no param carries either figure (QA-096, QA-097,
addendum T-042), so both are declared as measured calibration in
`weapons.nightfarer_calibration` -- and this file is what holds them to the
game.

The readings are the App Designer's own, taken in play on 2026-09-14 from
the 1.10.0 artefact: every Nightfarer at level 15, one-handed, no relics,
each armament at its own rarity. Four rows carry a factor and three carry
none; the three are here so that the factor can be shown to reach the
pairings it names and no other -- a factor that leaked onto Wylder's Great
Stars would still pass the Raider row.

Each factor has a mutation in `scripts/differential/mutate.py` that sets it
to 1.0 (`raider-heavy-armament-rate-neutralised`,
`borrowed-cursed-claws-rate-neutralised`); the row it names fails under it.
"""

from __future__ import annotations

import pytest

from nrplanner import damage, model, weaponslots, weapons
from tests import weapon_damage_cases as cases

LEVEL = 15
GREAT_STARS = 12180000

#: (Nightfarer, armament id, what the game showed)
READINGS = [
    ("Wylder", 3750000, 122),                     # own starting armament
    ("Raider", GREAT_STARS, 188),                 # x1.18: great hammer
    ("Wylder", GREAT_STARS, 147),                 # same armament, no factor
    ("Wylder", weapons.CURSED_CLAWS_ID, 54),      # x0.88: borrowed claws
    ("Revenant", weapons.CURSED_CLAWS_ID, 88),    # the owner, no factor
]
_IDS = [f"{hero} :: {weapon}" for hero, weapon, _shown in READINGS]


def _rating(data: dict, hero_name: str, weapon_id: int) -> damage.Rating:
    """Through the facade, the path every display and the advisor take."""
    hero = cases.hero_by_name(data, hero_name)
    weapon = cases.weapon_by_id(data, weapon_id)
    build = model.compute(hero, LEVEL, [], data.get("curves", {}))
    return damage.candidate(weapon, weapon.get("rarity", 0) + 1, build, data)


@pytest.mark.parametrize("hero, weapon, shown", READINGS, ids=_IDS)
def test_the_program_shows_the_number_the_game_showed(game_data, hero,
                                                      weapon, shown):
    rating = _rating(game_data, hero, weapon)
    assert not rating.rates, "measured with no relics equipped"
    assert damage.displayed(rating.final_total) == shown, (
        f"{rating.weapon['name']!r} for {hero} at level {LEVEL}: the game "
        f"showed {shown}, this program shows "
        f"{damage.displayed(rating.final_total)} "
        f"(unrounded {rating.final_total!r})")


def test_the_factors_are_the_measured_ones():
    """Both intervals are from the addendum to QA-096/QA-097 (T-042)."""
    assert 1.179733 <= weapons.RAIDER_HEAVY_ARMAMENT_RATE < 1.180116
    assert 0.877440 <= weapons.BORROWED_CURSED_CLAWS_RATE < 0.882700


def test_the_facade_hands_the_factor_to_the_breakdown(game_data):
    """Only where one applies: the golden file freezes this dictionary for
    pairings no factor reaches, and an always-present key would move every
    frozen record for nothing."""
    with_factor = _rating(game_data, "Raider", GREAT_STARS)
    figures = damage.breakdown_figures(with_factor, with_factor)
    assert figures["calibration"] == {
        "factor": weapons.RAIDER_HEAVY_ARMAMENT_RATE,
        "reason": "Raider with a greataxe or great hammer"}

    without = _rating(game_data, "Wylder", GREAT_STARS)
    assert "calibration" not in damage.breakdown_figures(without, without)


def test_the_popup_names_the_factor_and_where_it_is_from(shared_planner,
                                                         game_data):
    """A7: a number not read from the files says so where the figure is shown."""
    hero = cases.hero_by_name(game_data, "Raider")
    weapon = cases.weapon_by_id(game_data, GREAT_STARS)
    slots = [weaponslots.WeaponSlot() for _ in range(weaponslots.SLOT_COUNT)]
    slots[0] = weaponslots.WeaponSlot(weapon=weapon, tier=weapons.MIN_UPGRADE)
    shared_planner.hero_index = game_data["heroes"].index(hero)
    shared_planner.weapon_slots = slots
    shared_planner.declared = {}
    shared_planner.active_weapon = 0
    shared_planner.selected_effects = lambda: []
    build = model.compute(hero, LEVEL, [], game_data.get("curves", {}),
                          weapon=weapon, weapons_held=[weapon])
    shared_planner.stat_sheet._refresh_weapon_damage(build)

    text = shared_planner.stat_sheet._ar_breakdown_text()
    assert ("Raider with a greataxe or great hammer &nbsp; <b>x1.18</b> "
            "<span style='color:#8a8a8a'>measured, not read from the files; "
            "in every figure here</span>") in text
    assert "<b>Total 188</b>" in text
