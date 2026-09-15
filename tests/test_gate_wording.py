"""QA-186: an item-at-start effect is not told it needs several weapons.

The engine stores `wepTypeTriggerCount` on every "X in possession at start
of expedition" effect beside `startGoodsId`, with values like 256 and 1024
that count nothing. `model.GATE_FIELDS` labels the field "needs several of
that weapon equipped", and until this case every such effect carried that
sentence under Conditional & situational next to the item line that is its
whole condition. The wording is written out here rather than imported, so a
change to the model's sentence alone turns this red.
"""

from __future__ import annotations

from nrplanner import effecttext, model

from tests import weapon_damage_cases as cases

COUNTS_WEAPONS = "needs several of that weapon equipped"
GRANTS_AN_ITEM = "grants an item at the start of an expedition"


def holders(data: dict, with_item: bool) -> list[dict]:
    found = []
    for effect in data["effects"].values():
        mods = effect.get("modifiers") or {}
        if "wepTypeTriggerCount" in mods and ("startGoodsId" in mods) == with_item:
            found.append(effect)
    assert found, (
        f"no effect of this dataset holds `wepTypeTriggerCount` "
        f"{'with' if with_item else 'without'} `startGoodsId`, so this case "
        f"is watching nothing")
    return found


def reasons_for(data: dict, effect: dict) -> str:
    hero = cases.hero_by_name(data, "Wylder")
    build = model.compute(hero, cases.PROBE_LEVEL, [effect], data.get("curves", {}))
    return "; ".join(why for _name, _detail, why in build.qualitative)


def test_an_item_at_start_effect_is_not_told_to_carry_several_weapons(game_data):
    wrong = [effect["name"] for effect in holders(game_data, with_item=True)
             if COUNTS_WEAPONS in reasons_for(game_data, effect)
             or GRANTS_AN_ITEM not in reasons_for(game_data, effect)]
    assert not wrong, (
        f"{len(wrong)} item-at-start effects still read {COUNTS_WEAPONS!r} "
        f"or lost {GRANTS_AN_ITEM!r}: {wrong[:3]}")


def test_a_real_weapon_count_keeps_its_sentence(game_data):
    silent = [effect["name"] for effect in holders(game_data, with_item=False)
              if COUNTS_WEAPONS not in reasons_for(game_data, effect)]
    assert not silent, (
        f"{len(silent)} effects counting weapons lost {COUNTS_WEAPONS!r}: "
        f"{silent[:3]}")


def test_the_description_drops_the_count_only_beside_an_item(game_data):
    label = effecttext.FLAT_LABELS["wepTypeTriggerCount"]
    with_item = [effect["name"] for effect in holders(game_data, with_item=True)
                 if label in effecttext.describe_full(effect)]
    without = [effect["name"] for effect in holders(game_data, with_item=False)
               if label not in effecttext.describe_full(effect)]
    assert not with_item, f"item effects describe a weapon count: {with_item[:3]}"
    assert not without, f"weapon counts are not described: {without[:3]}"
