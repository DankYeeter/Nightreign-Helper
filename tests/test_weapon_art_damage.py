"""Which art and which spell a tile uses, and what the art hits for (AD-056.3/4).

The expected figures M1-M4 are `ARCHITECTURE.md` P.4: derived from
`damage.equipped` on the v16 snapshot times the motion value. M1 is also
measured at the training dummy (31.10. 12:59): Stamp hits for 262 one- and
two-handed alike, so an art has one figure and no two-handed twin. M2-M4 pin
the program's own arithmetic and are not measured. M5 (P.7.2) is measured
too: Wylder's Glintblade Phalanx on a grey Magic Longsword, 34 per blade.

Level 15, the starting armament at `MIN_UPGRADE`, no relic unless named.
"""

from __future__ import annotations

import pytest

from nrplanner import damage, model, weapons
from nrplanner.weaponslots import WeaponSlot
from tests import weapon_damage_cases as cases

LEVEL = 15
STAMP = 106
LIGHTNING_SLASH = 217
LIGHTNING_SLASH_RELIC = 7123200
GLINTBLADE_PHALANX_RELIC = 7122700
MIGHTY_SHOT = 402
ENDURE = 700
WYLDERS_GREATSWORD = 3750000
GLINTSTONE_PEBBLE = 4000
GLINTSTONE_ARC = 4070
GLINTBLADE_PHALANX = 200
LONGSWORD = 2000000
MAGIC_LONGSWORD = 2000800
#: "Magic Attack Power Up +4" (+12 %).
MAGIC_UP_4 = 6001501
#: Flame Spit names AttackElementCorrect 1005, which the table lacks.
FLAME_SPIT = 1001
FLAME_SPIT_ARMAMENT = 32150000


def build_for(game_data, hero, effect_ids=()):
    effects = [cases.effect_by_id(game_data, i) for i in effect_ids]
    return model.compute(hero, LEVEL, effects, game_data["curves"],
                         weapon=cases.weapon_by_id(game_data,
                                                   hero["starting_weapon"]))


def tile(game_data, weapon_id, art_id=None, spell_id=None) -> WeaponSlot:
    return WeaponSlot(cases.weapon_by_id(game_data, weapon_id),
                      weapons.MIN_UPGRADE, art_id=art_id, spell_id=spell_id)


def starting_art(game_data, name, effect_ids=(), slot_index=0, art_id=None):
    hero = cases.hero_by_name(game_data, name)
    slot = tile(game_data, hero["starting_weapon"], art_id=art_id)
    return damage.weapon_art(slot, slot_index, build_for(game_data, hero,
                                                         effect_ids),
                             hero, game_data)


@pytest.mark.parametrize("name, effect_ids, art_id, figure", [
    ("Wylder", (), STAMP, 262),                                  # M1
    ("Wylder", (LIGHTNING_SLASH_RELIC,), LIGHTNING_SLASH, 207),  # M2
    ("Executor", (), None, 180),                                 # M3
    ("Undertaker", (), None, 214),                               # M4
])
def test_the_art_hits_for_the_derived_figure(game_data, name, effect_ids,
                                             art_id, figure):
    rating = starting_art(game_data, name, effect_ids)

    assert rating.reason is None
    assert damage.displayed(rating.figure) == figure
    if art_id is not None:
        assert rating.art["id"] == art_id


def test_with_nothing_equipped_the_art_stands_on_its_baseline(game_data):
    rating = starting_art(game_data, "Wylder")

    assert rating.bare_figure == pytest.approx(rating.figure)


def test_a_held_swap_relic_is_counted(game_data):
    rating = starting_art(game_data, "Wylder", (LIGHTNING_SLASH_RELIC,))

    assert rating.swaps == 1


def test_a_swap_beats_the_choice_on_the_starting_armament(game_data):
    rating = starting_art(game_data, "Wylder", (LIGHTNING_SLASH_RELIC,),
                          art_id=STAMP)

    assert rating.art["id"] == LIGHTNING_SLASH


def test_a_swap_does_not_reach_another_tile(game_data):
    wylder = cases.hero_by_name(game_data, "Wylder")
    build = build_for(game_data, wylder, (LIGHTNING_SLASH_RELIC,))
    slot = tile(game_data, WYLDERS_GREATSWORD, art_id=STAMP)

    art, swaps = damage.art_in_use(slot, 1, build, wylder, game_data)

    assert (art["id"], swaps) == (STAMP, 0)


def test_a_rolled_armament_without_a_choice_has_no_figure(game_data):
    wylder = cases.hero_by_name(game_data, "Wylder")
    slot = tile(game_data, WYLDERS_GREATSWORD)

    rating = damage.weapon_art(slot, 1, build_for(game_data, wylder), wylder,
                               game_data)

    assert rating.art is None
    assert rating.per_type == {}
    assert rating.reason == damage.NO_ART_CHOSEN


def test_a_choice_outside_the_pool_is_dropped(game_data):
    wylder = cases.hero_by_name(game_data, "Wylder")
    greatsword = cases.weapon_by_id(game_data, WYLDERS_GREATSWORD)
    outside = next(art["id"] for art in game_data["arts"]
                   if art["id"] not in greatsword["art_pool"])
    slot = tile(game_data, WYLDERS_GREATSWORD, art_id=outside)

    art, _ = damage.art_in_use(slot, 1, build_for(game_data, wylder), wylder,
                               game_data)

    assert art is None


@pytest.mark.parametrize("name, effect_ids, reason", [
    ("Raider", (), damage.ART_DEALS_NO_DAMAGE.format(name="Endure")),
    ("Ironeye", (), damage.ART_FROM_A_PROJECTILE.format(name="Mighty Shot")),
])
def test_an_art_without_a_figure_says_why(game_data, name, effect_ids,
                                          reason):
    rating = starting_art(game_data, name, effect_ids)

    assert rating.reason == reason
    assert rating.per_type == {}


def wylders_art_on(game_data, weapon_id, art_id, effect_ids=(),
                    tier=weapons.MIN_UPGRADE):
    """Wylder, level 15, the armament on his second tile with this art."""
    wylder = cases.hero_by_name(game_data, "Wylder")
    slot = WeaponSlot(cases.weapon_by_id(game_data, weapon_id), tier,
                      art_id=art_id)
    return damage.weapon_art(slot, 1, build_for(game_data, wylder, effect_ids),
                             wylder, game_data)


@pytest.mark.parametrize("weapon_id, tier, figure", [
    (MAGIC_LONGSWORD, weapons.MIN_UPGRADE, 34),  # M5, measured
    (MAGIC_LONGSWORD, 3, 34),                    # no tier factor before M6
    (LONGSWORD, weapons.MIN_UPGRADE, 30),        # no Intelligence scaling
])
def test_glintblade_phalanx_hits_for_its_flat_figure(game_data, weapon_id,
                                                     tier, figure):
    rating = wylders_art_on(game_data, weapon_id, GLINTBLADE_PHALANX,
                            tier=tier)

    assert rating.reason is None
    assert damage.displayed(rating.figure) == figure


def test_a_magic_attack_relic_lifts_the_flat_figure(game_data):
    plain = wylders_art_on(game_data, MAGIC_LONGSWORD, GLINTBLADE_PHALANX)
    buffed = wylders_art_on(game_data, MAGIC_LONGSWORD, GLINTBLADE_PHALANX,
                            (MAGIC_UP_4,))

    assert buffed.figure > plain.figure
    assert buffed.bare_figure == pytest.approx(plain.bare_figure)


def test_glintblade_phalanx_by_relic_on_the_starting_armament(game_data):
    rating = starting_art(game_data, "Wylder", (GLINTBLADE_PHALANX_RELIC,))

    assert rating.art["id"] == GLINTBLADE_PHALANX
    assert rating.reason is None and rating.figure > 0


def test_a_flat_art_on_an_unknown_scaling_row_says_why(game_data):
    rating = wylders_art_on(game_data, FLAME_SPIT_ARMAMENT, FLAME_SPIT)

    assert rating.reason == damage.ART_NOT_CALIBRATED.format(name="Flame Spit")
    assert rating.per_type == {}


def recluse_spell(game_data, spell_id=None, slot_index=1):
    """Recluse's Staff on a tile that is not her starting one."""
    recluse = cases.hero_by_name(game_data, "Recluse")
    staff = cases.weapon_by_id(game_data, recluse["starting_weapon"])
    slot = tile(game_data, staff["id"], spell_id=spell_id)
    return damage.spell_thrown(build_for(game_data, recluse), game_data,
                               slot.weapon, starting=slot_index == 0,
                               chosen=slot.spell_id)[0]


def test_without_a_choice_the_staff_casts_slot_1(game_data):
    assert recluse_spell(game_data)["id"] == GLINTSTONE_PEBBLE


def test_a_chosen_spell_from_the_pool_is_cast(game_data):
    assert recluse_spell(game_data, GLINTSTONE_ARC)["id"] == GLINTSTONE_ARC


def test_a_chosen_spell_outside_the_pools_is_dropped(game_data):
    staff = cases.weapon_by_id(
        game_data, cases.hero_by_name(game_data, "Recluse")["starting_weapon"])
    outside = next(spell["id"] for spell in game_data["spells"]
                   if not any(spell["id"] in pool
                              for pool in staff["spell_pools"]))

    assert recluse_spell(game_data, outside)["id"] == GLINTSTONE_PEBBLE


def test_the_choice_travels_with_the_tile():
    slot = WeaponSlot(art_id=STAMP, spell_id=GLINTSTONE_ARC)

    assert (slot.copy().art_id, slot.copy().spell_id) == (STAMP,
                                                          GLINTSTONE_ARC)
