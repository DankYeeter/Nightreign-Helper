"""A weapon-count effect counts once, however many relics carry it.

User question 2026-11-08: "Improved Attack Power with 3+ Daggers Equipped" on
two deep relics. The params flag it as stacking; in play a second copy adds
nothing, while two different weapon types do add up (community reports, see
`model.SINGLE_COPY_FIELDS`).
"""

from __future__ import annotations

import pytest

from nrplanner import model, stacking

DAGGERS = 7080000
LEVEL = 15


@pytest.fixture(scope="module")
def duchess(game_data):
    return next(h for h in game_data["heroes"] if h["name"] == "Duchess")


def _build(game_data, hero, effects):
    return model.compute(hero, LEVEL, effects, game_data.get("curves", {}),
                         declared={e["id"]: 1 for e in effects})


def test_two_dagger_relics_give_plus_twenty_and_not_forty_four(game_data,
                                                               duchess):
    daggers = game_data["effects"][str(DAGGERS)]
    one = _build(game_data, duchess, [daggers])
    two = _build(game_data, duchess, [daggers, daggers])
    assert one.rates == two.rates
    assert one.rates.get("physicsAttackRate") == pytest.approx(1.2, abs=1e-6)
    assert any(w.kind == "duplicate" for w in two.warnings)


def test_every_weapon_count_effect_is_single_copy(game_data):
    gated = [e for e in game_data["effects"].values()
             if "wepTypeTriggerCount" in (e.get("modifiers") or {})
             and "startGoodsId" not in e["modifiers"]]
    assert gated
    for effect in gated:
        assert model.single_copy(effect), effect["name"]
        assert stacking.repetition(effect) == stacking.STRONGEST


def test_two_different_weapon_types_still_multiply(game_data, duchess):
    gated = [e for e in game_data["effects"].values()
             if e["name"].startswith("Improved Attack Power with 3+")
             and e["id"] != DAGGERS
             and (e.get("modifiers") or {}).get("physicsAttackRate")]
    other = gated[0]
    daggers = game_data["effects"][str(DAGGERS)]
    both = _build(game_data, duchess, [daggers, other])
    assert both.rates["physicsAttackRate"] == pytest.approx(
        1.2 * other["modifiers"]["physicsAttackRate"], abs=1e-6)
