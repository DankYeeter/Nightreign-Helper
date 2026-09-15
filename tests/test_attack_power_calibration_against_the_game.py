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

The second half holds the two-handing factors (R-008, AD-037) to the six
cells the App Designer read on the same day: the same figure one-handed and
then two-handed, every Nightfarer at level 15 with no relics. Mutations
`two-handed-rate-neutralised` and `raider-two-handed-rate-neutralised` set
each to 1.0; `two-handing-buff-left-on-the-scoped-line` puts scope 124 back
outside every attack rating.

The thirteen pairs of 2026-09-15 (GOAL.md A20-Messzellen II, QA-276) follow:
twinblades and pairs two-hand by a rule of their own, and three more single
armaments and three armaments with no second figure stand guard around them.
Mutations `twinblade-two-handed-rate-neutralised` and
`paired-two-handed-rate-neutralised` put each back on the plain factor.
"""

from __future__ import annotations

import pytest

from nrplanner import damage, model, weaponslots, weapons
from tests import tabtext
from tests import weapon_damage_cases as cases

LEVEL = 15
GREAT_STARS = 12180000
TWINBLADE = 10000000
CAESTUS = 21000000
HOOKCLAWS = 22000000
ORNAMENTAL_STRAIGHT_SWORD = 2060000

#: (Nightfarer, armament id, what the game showed)
READINGS = [
    ("Wylder", 3750000, 122),                     # own starting armament
    ("Raider", GREAT_STARS, 188),                 # x1.18: great hammer
    ("Wylder", GREAT_STARS, 147),                 # same armament, no factor
    ("Wylder", weapons.CURSED_CLAWS_ID, 54),      # x0.88: borrowed claws
    ("Revenant", weapons.CURSED_CLAWS_ID, 88),    # the owner, no factor
]
_IDS = [f"{hero} :: {weapon}" for hero, weapon, _shown in READINGS]


def _rating(data: dict, hero_name: str, weapon_id: int,
            effects: list[dict] = ()) -> damage.Rating:
    """Through the facade, the path every display and the advisor take."""
    hero = cases.hero_by_name(data, hero_name)
    weapon = cases.weapon_by_id(data, weapon_id)
    build = model.compute(hero, LEVEL, list(effects), data.get("curves", {}))
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
    # Both hands on the same row (AK-286/AK-299): 188 one-handed, and the
    # Raider two-handing factor of R-008 on top for the second figure; the
    # markup that quiets one hand (AK-298) is not what this case is about.
    assert "Total 188\u00a01H\u00a0/\u00a0216\u00a02H" in tabtext.unmarked(text)


# --- two-handing (R-008, AD-037) -------------------------------------------

#: (Nightfarer, armament id, one-handed, two-handed) -- GOAL.md A20.
TWO_HANDED_READINGS = [
    ("Duchess", 1750000, 72, 74),         # dagger, DEX: no STR rule fits
    ("Wylder", 3750000, 122, 125),        # own greatsword
    ("Raider", 23750000, 158, 180),       # colossal weapon, no x1.18
    ("Guardian", 18750000, 107, 110),     # halberd
    ("Raider", GREAT_STARS, 188, 216),    # x1.18 and the Raider hand factor
    ("Wylder", GREAT_STARS, 147, 151),    # same armament, neither
    # 2026-09-15 (QA-276): single armaments stay on 1.03 ...
    ("Executor", 9750000, 94, 97),
    ("Scholar", 5750000, 63, 64),
    ("Undertaker", 11750000, 91, 93),
    # ... a twinblade halves, for the Raider too ...
    ("Wylder", TWINBLADE, 108, 54),
    ("Raider", TWINBLADE, 99, 49),
    # ... and a pair has its own figure, x0.88 or not.
    ("Wylder", CAESTUS, 93, 71),
    ("Wylder", HOOKCLAWS, 80, 62),
    ("Wylder", ORNAMENTAL_STRAIGHT_SWORD, 161, 124),
    ("Revenant", weapons.CURSED_CLAWS_ID, 88, 68),
    ("Revenant", HOOKCLAWS, 59, 46),
]
_TWO_HANDED_IDS = [f"{hero} :: {weapon}"
                   for hero, weapon, _one, _two in TWO_HANDED_READINGS]

WHEN_TWO_HANDING_ATTACK_POWER = 8300000
WHEN_TWO_HANDING_STANCE = 7006000


@pytest.mark.parametrize("hero, weapon, one, two", TWO_HANDED_READINGS,
                         ids=_TWO_HANDED_IDS)
def test_both_hands_show_the_numbers_the_game_showed(game_data, hero,
                                                     weapon, one, two):
    rating = _rating(game_data, hero, weapon)
    assert damage.displayed(rating.final_total) == one
    assert rating.two_handed is not None
    assert rating.two_handed.two_handed is None, "nested once, not twice"
    assert damage.displayed(rating.two_handed.final_total) == two, (
        f"{rating.weapon['name']!r} for {hero} two-handed: the game showed "
        f"{two}, this program shows "
        f"{damage.displayed(rating.two_handed.final_total)} "
        f"(unrounded {rating.two_handed.final_total!r})")


def test_the_two_handing_factors_are_the_measured_ones():
    """R-008's intersections over its six cells, and QA-276's over its seven:
    the pair window is nine millionths wide, see the note at the constant."""
    assert 1.025889 <= weapons.TWO_HANDED_RATE < 1.032358
    assert 1.143863 <= weapons.RAIDER_TWO_HANDED_RATE < 1.144480
    assert 0.497042 <= weapons.TWINBLADE_TWO_HANDED_RATE < 0.501018
    assert 0.773656 <= weapons.PAIRED_TWO_HANDED_RATE < 0.773665


def test_the_paired_flag_reaches_every_fist_and_claw_and_no_twinblade(
        game_data):
    """`isDualBlade` as the extractor writes it (EXTRACT_VERSION 12): all 45
    fists and 32 claws, the Ornamental Straight Sword, the Starscourge
    Greatsword -- 79 -- and none of the 35 twinblades, which two-hand by
    their own rule and must not take the pair's."""
    paired = [w for w in game_data["weapons"] if w[weapons.PAIRED_KEY]]
    assert len(paired) == 79
    assert {w["wep_type"] for w in paired} == {3, 7, 35, 37}
    assert not [w for w in paired if w["wep_type"] == weapons.TWINBLADE_TYPE]
    assert all(w[weapons.PAIRED_KEY] for w in game_data["weapons"]
               if w["wep_type"] in (35, 37))


@pytest.mark.parametrize("hero, weapon, factor, reason", [
    ("Raider", TWINBLADE, weapons.TWINBLADE_TWO_HANDED_RATE,
     "two-handing a twinblade"),
    ("Raider", CAESTUS, weapons.PAIRED_TWO_HANDED_RATE, "two-handing a pair"),
    ("Wylder", weapons.CURSED_CLAWS_ID, weapons.PAIRED_TWO_HANDED_RATE,
     "two-handing a pair"),
])
def test_the_shape_of_the_armament_names_the_factor_before_the_nightfarer(
        game_data, hero, weapon, factor, reason):
    """The Raider's 1.144 does not reach a twinblade or a pair; the borrowed
    claws keep their x0.88 in both hands beside the pair's own factor."""
    rating = _rating(game_data, hero, weapon)
    assert rating.two_handed.weapon_rating.two_handed == weapons.Calibration(
        factor, reason)
    assert rating.two_handed.weapon_rating.calibration ==         rating.weapon_rating.calibration


def test_the_two_handed_answer_names_its_factor(game_data):
    rating = _rating(game_data, "Raider", GREAT_STARS)
    assert rating.weapon_rating.two_handed is None
    assert rating.two_handed.weapon_rating.two_handed == weapons.Calibration(
        weapons.RAIDER_TWO_HANDED_RATE, "Raider two-handing")
    assert rating.two_handed.weapon_rating.calibration == weapons.Calibration(
        weapons.RAIDER_HEAVY_ARMAMENT_RATE,
        "Raider with a greataxe or great hammer"), "x1.18 stays in both hands"


@pytest.mark.parametrize("family", ["Bow", "Crossbow", "Ballista",
                                    "Glintstone Staff", "Sacred Seal",
                                    "Unarmed"])
def test_no_second_figure_where_the_game_shows_none(game_data, family):
    weapon_id = cases.first_of_family(game_data, family)
    assert _rating(game_data, "Wylder", weapon_id).two_handed is None


def test_a_when_two_handing_buff_lifts_the_two_handed_figure_only(game_data):
    """Scope 124 leaves the `scoped:` line and reaches one hand (AD-037, 3)."""
    buff = cases.effect_by_id(game_data, WHEN_TWO_HANDING_ATTACK_POWER)
    plain = _rating(game_data, "Wylder", GREAT_STARS)
    buffed = _rating(game_data, "Wylder", GREAT_STARS, [buff])

    assert buffed.final_total == plain.final_total
    assert not buffed.rates
    assert buffed.two_handed.rates == pytest.approx(
        {"physicsAttackRate": 1.12}), "Great Stars hits with one type"
    assert damage.displayed(buffed.two_handed.final_total) == 169  # 151.6 x 1.12

    hero = cases.hero_by_name(game_data, "Wylder")
    build = model.compute(hero, LEVEL, [buff], game_data.get("curves", {}))
    assert not any(key.startswith(model.SCOPED_PREFIX) for key in build.rates)
    assert build.class_rates[model.TWO_HANDED_CLASS]["physicsAttackRate"] \
        == pytest.approx(1.12)


def test_the_stance_buff_travels_with_its_condition_and_moves_no_figure(
        game_data):
    stance = cases.effect_by_id(game_data, WHEN_TWO_HANDING_STANCE)
    hero = cases.hero_by_name(game_data, "Wylder")
    build = model.compute(hero, LEVEL, [stance], game_data.get("curves", {}))

    assert "saAttackPowerRate" not in build.rates
    assert build.class_rates[model.TWO_HANDED_CLASS]["saAttackPowerRate"] \
        == pytest.approx(1.05)

    plain = _rating(game_data, "Wylder", GREAT_STARS)
    with_stance = _rating(game_data, "Wylder", GREAT_STARS, [stance])
    assert with_stance.final_total == plain.final_total
    assert with_stance.two_handed.final_total == plain.two_handed.final_total
    assert not with_stance.two_handed.rates
