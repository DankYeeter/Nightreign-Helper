"""The weapon arts and the pools a tile chooses from arrive (AD-056.1, P.6 step 1).

Anchors measured against the installation on 2026-10-31 (`data_version`
10350000, `ARCHITECTURE.md` Themenbereich P): Wylder's Greatsword starts on
Stamp (106) and can be found with 54 arts; Stamp names AtkParam_Pc row
300000290, which carries no flat figure and a correction of 215 on all five
types; Recluse's Staff holds Glintstone Pebble alone in slot 1 and a pool of
64 in slot 2. Counts are exact for the reason `test_spell_damage_extraction`
gives: both directions are news.

P.7 (T-335w): a variant whose own rows name no art table is found with its
base armament's (M5: Magic Longsword with Glintblade Phalanx); 34 armaments
are left without a pool. Glintblade Phalanx scales by AttackElementCorrect
51080, not the armament's.

Nothing here holds game prose beyond names (A-001).
"""

from __future__ import annotations

WYLDERS_GREATSWORD = 3750000
STAMP = 106
WYLDERS_POOL_TODAY = 54
STAMP_MOTION_VALUE = 215
RECLUSES_STAFF = 33750000
GLINTSTONE_PEBBLE = 4000
GLINTSTONE_ARC = 4070
RECLUSE_SLOT_2_TODAY = 64
FINGER_SEAL = 34750000
SWAP_RELIC_ARTS_TODAY = 20
#: Ironeye's own art names an AtkParam_Pc row the table does not hold.
MIGHTY_SHOT = 402
LONGSWORD = 2000000
MAGIC_LONGSWORD = 2000800
GLINTBLADE_PHALANX = 200
GLINTBLADE_PHALANX_AEC = 51080
WITHOUT_ART_POOL_TODAY = 34


def arts_by_id(game_data) -> dict[int, dict]:
    return {art["id"]: art for art in game_data["arts"]}


def weapon(game_data, weapon_id: int) -> dict:
    return next(w for w in game_data["weapons"] if w["id"] == weapon_id)


def test_wylders_greatsword_starts_on_stamp_and_can_be_found_with_54(game_data):
    greatsword = weapon(game_data, WYLDERS_GREATSWORD)

    assert greatsword["art_default"] == STAMP
    assert len(greatsword["art_pool"]) == WYLDERS_POOL_TODAY
    assert STAMP in greatsword["art_pool"]
    assert greatsword["art_pool"] == sorted(greatsword["art_pool"])


def test_stamp_carries_its_motion_value_on_all_five_types(game_data):
    stamp = arts_by_id(game_data)[STAMP]

    assert stamp["name"] == "Stamp (Upward Cut)"
    assert stamp["motion_value"] == {damage: STAMP_MOTION_VALUE for damage in
                                     ("Physics", "Magic", "Fire", "Thunder",
                                      "Dark")}
    assert "damage" not in stamp


def test_an_art_is_motion_or_flat_and_never_both(game_data):
    assert not [art["id"] for art in game_data["arts"]
                if "motion_value" in art and "damage" in art]


def test_an_unresolved_row_keeps_the_id_the_game_names(game_data):
    """What tells a projectile art from one that deals no damage (AD-056.5)."""
    mighty_shot = arts_by_id(game_data)[MIGHTY_SHOT]

    assert mighty_shot["damage_atk"] > 0
    assert "motion_value" not in mighty_shot and "damage" not in mighty_shot


def test_recluses_staff_holds_one_spell_in_slot_1_and_a_pool_in_slot_2(
        game_data):
    first, second = weapon(game_data, RECLUSES_STAFF)["spell_pools"]

    assert first == [GLINTSTONE_PEBBLE]
    assert len(second) == RECLUSE_SLOT_2_TODAY
    assert GLINTSTONE_ARC in second


def test_a_seal_no_custom_row_names_carries_no_pools(game_data):
    assert "spell_pools" not in weapon(game_data, FINGER_SEAL)


def test_every_swap_relic_names_an_art_of_the_block(game_data):
    known = arts_by_id(game_data)
    swapped = [effect["modifiers"]["startSwordArtsId"]
               for effect in game_data["effects"].values()
               if "startSwordArtsId" in (effect.get("modifiers") or {})]

    assert len(swapped) == SWAP_RELIC_ARTS_TODAY
    assert all(art_id in known for art_id in swapped)


def test_a_variant_is_found_with_its_base_armaments_arts(game_data):
    variant = weapon(game_data, MAGIC_LONGSWORD)

    assert variant["art_pool"] == weapon(game_data, LONGSWORD)["art_pool"]
    assert GLINTBLADE_PHALANX in variant["art_pool"]


def test_34_armaments_are_found_with_no_art_to_choose(game_data):
    without = [w for w in game_data["weapons"] if not w["art_pool"]]

    assert len(without) == WITHOUT_ART_POOL_TODAY


def test_glintblade_phalanx_scales_by_its_own_element_correct_row(game_data):
    arts = arts_by_id(game_data)

    assert arts[GLINTBLADE_PHALANX]["element_correct_id"] == GLINTBLADE_PHALANX_AEC
    assert "element_correct_id" not in arts[STAMP]
