"""Every tab reads one build, or the program contradicts itself.

QA-001: the Weapons tab called `model.compute` with its own, shorter argument
list -- no curses, no armament effects, no declared conditionals, no weapon
gates. Measured against the real game data on a Deep of Night build (Wylder,
Wylder's Urn): the Build planner said Vigor 5 and 180 HP, the Weapons tab said
Vigor 8 and 240 HP, and it ranked every weapon in the game on the second set.
Nothing on screen said which was right.

A second argument list is not a thing to correct, it is a thing to remove.
These tests are about the removal: the build is computed once and handed on,
so a new parameter cannot reach one caller and miss the other. The build
advisor will be the third caller, and it is the reason this had to happen
before it was written.
"""

from __future__ import annotations

import pathlib
import re

import pytest

from nrplanner import model


UI_MODULES = sorted(pathlib.Path(__file__).resolve().parents[1]
                    .glob("nrplanner/*.py"))


def attributes_on_the_planner_tab(planner) -> dict[str, int]:
    """The attribute totals as the Build planner tab shows them.

    Read off the widgets rather than from the build behind them: the claim
    under test is what the two tabs tell the player, and a figure that never
    reaches the screen cannot contradict anything.
    """
    out = {}
    for row, name in enumerate(model.ATTRIBUTE_ORDER):
        item = planner.attr_grid.itemAtPosition(row, 3)
        out[name] = int(item.widget().text())
    return out


def test_every_tab_computes_the_same_build(planner, game_data):
    """An armament's own effect must reach the Weapons tab as well.

    Armament effects are one of the four things the second argument list left
    out. This one is set on the tile rather than in a relic slot so the test
    needs no save file -- the divergence is the same either way.
    """
    from tests import weapon_damage_cases as cases

    hero = game_data["heroes"][planner.hero_index]
    raises_strength = cases.effects_raising_attribute(
        game_data, hero, "Strength", 1)[0]
    planner.weapon_slots[0].effect_ids = [raises_strength]
    planner.recompute()
    planner.weapons_tab.recalculate()

    assert planner.weapons_tab.attributes == attributes_on_the_planner_tab(planner)


def a_gated_attribute_effect(data: dict, hero: dict) -> int:
    """A gated effect that raises an attribute once its condition is declared.

    It has to move an attribute rather than a multiplier: the Weapons tab
    ranks on attributes, so a rate it never received is a divergence nothing
    on that tab could show.
    """
    curves = data.get("curves", {})
    for key in sorted(data["effects"], key=int):
        effect = data["effects"][key]
        if not model.is_conditional(effect, None):
            continue
        silent = model.compute(hero, 15, [effect], curves)
        declared = model.compute(hero, 15, [effect], curves,
                                 declared={int(effect["id"]): 1})
        if declared.attributes != silent.attributes:
            return int(effect["id"])
    raise LookupError("no gated attribute effect in this dataset")


def test_a_declared_conditional_reaches_every_tab(planner, game_data):
    """Declaring a gated effect changes the build, so it changes every tab."""
    hero = game_data["heroes"][planner.hero_index]
    declarable = a_gated_attribute_effect(game_data, hero)
    planner.weapon_slots[0].effect_ids = [declarable]
    planner.declared = {declarable: 3}
    planner.recompute()
    planner.weapons_tab.recalculate()

    assert planner.weapons_tab.attributes == attributes_on_the_planner_tab(planner)


def test_a_curse_reaches_every_tab(planner, game_data):
    """The case QA measured: a Deep of Night relic's curse.

    Needs the player's own save, because the curse has to come from a relic
    they actually own -- the planner offers nothing else.
    """
    cursed = _equip_a_cursed_deep_relic(planner)
    if cursed is None:
        pytest.skip("this save owns no Deep of Night relic carrying a curse")

    planner.recompute()
    planner.weapons_tab.recalculate()

    assert planner.weapons_tab.attributes == attributes_on_the_planner_tab(planner)


def _equip_a_cursed_deep_relic(planner):
    """Put the first owned cursed Deep relic into its slot, or return None."""
    planner.deep_check.setChecked(True)
    for slot in planner.deep_slots:
        for index in range(slot.relic_box.count()):
            item = slot.relic_box.itemData(index)
            if item is not None and getattr(item, "curse_ids", None):
                slot.relic_box.setCurrentIndex(index)
                return item
    return None


def test_the_user_interface_holds_exactly_one_call_to_compute():
    """One call site, so a new argument cannot reach one tab and miss another.

    This is the guard that outlives the fix above. Correcting the second
    argument list would have made the numbers agree today and drifted again at
    the next parameter; what keeps them together is that there is only one
    place to pass one.
    """
    callers = {
        path.name: len(re.findall(r"model\.compute\(", path.read_text("utf-8")))
        for path in UI_MODULES
    }

    assert {name: n for name, n in callers.items() if n} == {"app.py": 1}, (
        "every tab must take the build from Planner.current_build(); "
        f"model.compute is called in {callers}"
    )
