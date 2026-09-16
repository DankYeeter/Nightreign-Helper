"""The damage-type conversion lands where the game puts it, 3 readings of 3.

"Starting armament deals fire damage" (7120100) carries `physicsAttackPower`
-30 and `fireAttackPower` +33, and until T-246 the program moved the attack
rating by exactly 0 for it (QA-113). Where the points land is not in the
params; `damage.converted` says which reading was measured and what ruled the
others out. This file holds that reading to the App Designer's three points
of 2026-09-14: level 15, own starting armament in slot 1, the relic at its
first payload tier, nothing else equipped.

The mutation `damage-type-conversion-ignored` in
`scripts/differential/mutate.py` switches the conversion off; every row here
fails under it. The Revenant row is the one that also fails if the floor at
zero is dropped (90 instead of 91).
"""

from __future__ import annotations

import pytest

from nrplanner import damage, model
from tests import weapon_damage_cases as cases

LEVEL = 15
FIRE_CONVERSION = 7120100

#: (Nightfarer, the game without the relic, the game with it)
READINGS = [
    ("Wylder", 122, 123),
    ("Revenant", 88, 91),
    ("Duchess", 72, 74),
]
_IDS = [hero for hero, _before, _after in READINGS]


def _on_own_armament(data: dict, hero_name: str, effects: list[int],
                     starting_armament: bool = True) -> damage.Rating:
    hero = cases.hero_by_name(data, hero_name)
    weapon = cases.weapon_by_id(data, hero["starting_weapon"])
    build = model.compute(hero, LEVEL,
                          [cases.effect_by_id(data, e) for e in effects],
                          data.get("curves", {}), weapon=weapon)
    return damage.attack_rating(weapon, weapon.get("rarity", 0) + 1, build,
                                data, starting_armament=starting_armament).now


@pytest.mark.parametrize("hero, before, after", READINGS, ids=_IDS)
def test_the_relic_moves_the_figure_to_what_the_game_showed(game_data, hero,
                                                            before, after):
    bare = _on_own_armament(game_data, hero, [])
    assert damage.displayed(bare.final_total) == before

    with_relic = _on_own_armament(game_data, hero, [FIRE_CONVERSION])
    assert damage.displayed(with_relic.final_total) == after, (
        f"{hero}: the game showed {after} with the relic, this program shows "
        f"{damage.displayed(with_relic.final_total)} "
        f"(unrounded {with_relic.final_total!r})")


def test_the_breakdown_separates_physical_from_the_element(game_data):
    """Revenant: the physical part is driven to zero and stays as a row."""
    rating = _on_own_armament(game_data, "Revenant", [FIRE_CONVERSION])
    assert rating.final_per_type["Physics"] == 0.0
    assert rating.final_per_type["Fire"] == pytest.approx(33 * 0.6)
    assert set(rating.conversion) == {"Physics", "Fire"}
    assert list(rating.final_per_type) == ["Physics", "Magic", "Fire"]


def test_the_conversion_reaches_the_starting_slot_only(game_data):
    """Same pairing rule as the status penalty: slot 1 and the own armament."""
    elsewhere = _on_own_armament(game_data, "Wylder", [FIRE_CONVERSION],
                                 starting_armament=False)
    assert damage.displayed(elsewhere.final_total) == 122
    assert not elsewhere.conversion


def test_the_relic_is_a_number_now_and_not_a_qualitative_note(game_data):
    hero = cases.hero_by_name(game_data, "Wylder")
    effect = cases.effect_by_id(game_data, FIRE_CONVERSION)
    build = model.compute(hero, LEVEL, [effect], game_data.get("curves", {}))
    assert build.starting_flat == {"Physics": -30.0, "Fire": 33.0}
    assert effect["name"] not in [name for name, _what, _why
                                  in build.qualitative]
