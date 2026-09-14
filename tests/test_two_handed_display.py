"""The two-handed figure stands beside the one-handed one -- and only there.

AK-286: where the game offers an armament two-handed, every attack figure on
screen reads `{1H} / {2H} 2H` under the label it already had; where it does
not (a bow, a staff), the figure is unchanged -- no `/ -- 2H`, no `n/a`
(AK-288). Three surfaces show the figure: the weapon tile, the stat sheet's
panel with its click-through popup, and the arsenal tile. T-255b.

AK-293 point 4: the `when Two-Handing` multipliers appear in the sheet's
Multipliers section under the condition's own sentence, not as an armament
class called `two_handed`.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QLabel

from nrplanner import arsenaltab, damage, effecttext, model, weaponslots
from nrplanner.advisor.explain import _field_label

from tests import weapon_damage_cases as cases

LEVEL = 15
TIER = 3
TWO_HANDED = "\u00a02H"


def test_a_lone_figure_is_the_truncated_number_and_nothing_else():
    assert damage.displayed_hands(147.9, None) == "147"


def test_both_hands_join_with_no_break_spaces():
    assert damage.displayed_hands(147.9, 151.2) == "147\u00a0/\u00a0151\u00a02H"


@pytest.fixture(scope="module")
def hero(game_data):
    return cases.hero_by_name(game_data, "Wylder")


@pytest.fixture(scope="module")
def build(game_data, hero):
    return model.compute(hero, LEVEL, [], game_data.get("curves", {}))


@pytest.fixture(scope="module")
def greatsword(game_data):
    return cases.weapon_by_id(game_data,
                              cases.heaviest_of_family(game_data,
                                                       "Colossal Sword"))


@pytest.fixture(scope="module")
def bow(game_data):
    return cases.weapon_by_id(game_data, cases.first_of_family(game_data, "Bow"))


@pytest.fixture(scope="module")
def staff(game_data):
    return cases.weapon_by_id(
        game_data, cases.first_of_family(game_data, "Glintstone Staff"))


def test_the_rating_reads_the_same_figure_off_both_hands(game_data, build,
                                                         greatsword):
    rating = damage.candidate(greatsword, TIER, build, game_data)
    assert rating.two_handed is not None
    assert rating.displayed_hands(lambda r: r.final_headline) == (
        f"{damage.displayed(rating.final_headline)}\u00a0/\u00a0"
        f"{damage.displayed(rating.two_handed.final_headline)}\u00a02H")


@pytest.mark.parametrize("family", ["bow", "staff"])
def test_an_armament_without_a_second_figure_shows_one(game_data, build,
                                                       family, request):
    weapon = request.getfixturevalue(family)
    rating = damage.candidate(weapon, TIER, build, game_data)
    assert rating.two_handed is None
    assert rating.displayed_hands(lambda r: r.final_headline) == str(
        damage.displayed(rating.final_headline))


def test_the_popup_figures_carry_the_other_hand_only_where_there_is_one(
        game_data, build, greatsword, bow):
    both = damage.attack_rating(greatsword, TIER, build, game_data)
    figures = both.figures()
    assert figures["two_handed"] == {
        "base": both.bare.two_handed.scaled_headline,
        "final": both.now.two_handed.final_headline}
    assert "two_handed" not in damage.attack_rating(
        bow, TIER, build, game_data).figures()


def _tile_detail(weapon, rating) -> str:
    tile = weaponslots.WeaponTile(0, lambda *_: None, lambda *_: None,
                                  lambda *_: None)
    try:
        tile.show_slot(weaponslots.WeaponSlot(weapon=weapon, tier=TIER),
                       rating)
        return tile.detail.text()
    finally:
        tile.deleteLater()


def test_the_weapon_tile_puts_both_hands_inside_the_bold_figure(
        game_data, build, greatsword, bow):
    rating = damage.candidate(greatsword, TIER, build, game_data)
    assert f"{TWO_HANDED}</b> {damage.ATTACK_RATING_LABEL}" in _tile_detail(
        greatsword, rating)
    assert TWO_HANDED not in _tile_detail(
        bow, damage.candidate(bow, TIER, build, game_data))


def _sheet_with(shared_planner, game_data, hero, weapon):
    slots = [weaponslots.WeaponSlot() for _ in range(weaponslots.SLOT_COUNT)]
    slots[1] = weaponslots.WeaponSlot(weapon=weapon, tier=TIER)
    shared_planner.hero_index = game_data["heroes"].index(hero)
    shared_planner.weapon_slots = slots
    shared_planner.declared = {}
    shared_planner.active_weapon = 1
    shared_planner.selected_effects = lambda: []
    built = model.compute(hero, LEVEL, [], game_data.get("curves", {}),
                          weapon=weapon, weapons_held=[weapon])
    shared_planner.stat_sheet._refresh_weapon_damage(built)
    return shared_planner.stat_sheet


def test_the_panel_and_its_popup_show_both_hands_on_every_figure(
        shared_planner, game_data, hero, greatsword):
    sheet = _sheet_with(shared_planner, game_data, hero, greatsword)
    panel = sheet.ar_label.text()
    rows = [row for row in panel.split("<div")
            if row.startswith(">Physical") or "<b>Total</b>" in row]
    assert len(rows) == 2, panel
    for row in rows:
        # The grey before-figure and the accented after-figure, both hands.
        assert row.count(TWO_HANDED) == 2, row
    popup = sheet._ar_breakdown_text().split("<br>")
    # The `Base` line right under the heading, and the `Total` line last.
    assert popup[1].startswith("&nbsp;&nbsp;Base") and TWO_HANDED in popup[1]
    assert "<b>Total " in popup[-1] and TWO_HANDED in popup[-1]


def test_the_panel_leaves_a_bow_s_figures_alone(shared_planner, game_data,
                                                hero, bow):
    sheet = _sheet_with(shared_planner, game_data, hero, bow)
    assert TWO_HANDED not in sheet.ar_label.text()
    assert TWO_HANDED not in sheet._ar_breakdown_text()


def _arsenal_headline(tab, weapon) -> str:
    tab.search.setText(f'"{weapon["name"]}"')
    tab.recalculate()
    for tile in tab.scroll.widget().findChildren(arsenaltab.Tile):
        labels = [label.text() for label in tile.findChildren(QLabel)]
        if labels[1] == weapon["name"]:
            return labels[labels.index(damage.ATTACK_RATING_LABEL) + 1]
    raise AssertionError(f"no tile drawn for {weapon['name']!r}")


def test_the_arsenal_tile_shows_both_hands_only_for_a_two_handable_armament(
        shared_planner, game_data, hero, greatsword, bow):
    shared_planner.hero_index = game_data["heroes"].index(hero)
    shared_planner.level_slider.setValue(LEVEL)
    shared_planner.weapon_slots = [weaponslots.WeaponSlot()
                                   for _ in range(weaponslots.SLOT_COUNT)]
    shared_planner.declared = {}
    shared_planner.selected_effects = lambda: []
    shared_planner.recompute()
    tab = shared_planner.weapons_tab
    tab.upgrade.setValue(TIER)
    assert _arsenal_headline(tab, greatsword).endswith(TWO_HANDED)
    assert TWO_HANDED not in _arsenal_headline(tab, bow)


def test_the_two_handing_bucket_is_named_by_its_condition():
    assert effecttext.restricted_to(model.TWO_HANDED_CLASS) == \
        effecttext.ATTACK_CONDITIONS[model.TWO_HANDING_SCOPE]
    assert effecttext.restricted_to("melee") == "melee armaments only"
    assert "two_handed" not in effecttext.restricted_to(model.TWO_HANDED_CLASS)


def test_the_why_names_the_two_handing_bucket_by_its_condition():
    """AK-293 point 4 in the advisor's `Why`: the same sentence as the sheet,
    through the same function, never the bucket's internal name."""
    key = f"{model.WEAPON_CLASS_PREFIX}{model.TWO_HANDED_CLASS}:physicsAttackRate"
    label = _field_label(key)
    assert label.endswith(effecttext.ATTACK_CONDITIONS[model.TWO_HANDING_SCOPE])
    assert "two_handed" not in label
    assert _field_label(f"{model.WEAPON_CLASS_PREFIX}melee:physicsAttackRate"
                        ).endswith("melee armaments only")
