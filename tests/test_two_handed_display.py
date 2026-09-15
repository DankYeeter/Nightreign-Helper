"""The two-handed figure stands beside the one-handed one -- and only there.

AK-286: where the game offers an armament two-handed, every attack figure on
screen reads `{1H} / {2H} 2H` under the label it already had; where it does
not (a bow, a staff), the figure is unchanged -- no `/ -- 2H`, no `n/a`
(AK-288). Three surfaces show the figure: the weapon tile, the stat sheet's
panel with its click-through popup, and the arsenal tile. T-255b.

AK-293 point 4: the `when Two-Handing` multipliers appear in the sheet's
Multipliers section under the condition's own sentence, not as an armament
class called `two_handed`.

AK-298: on all three surfaces the half the switch (AK-292) stands on wears
the surface's emphasis -- bold and `ACCENT` -- and the other half is `MUTED`
and unbolded; the figures themselves do not move (AK-293). T-268b.
"""

from __future__ import annotations

import pytest
from PySide6.QtGui import QTextDocument
from PySide6.QtWidgets import QLabel

from nrplanner import (arsenaltab, damage, effecttext, model, statsheet,
                       weaponslots)
from nrplanner.advisor.explain import _field_label

from tests import tabtext
from tests import weapon_damage_cases as cases

LEVEL = 15
TIER = 3
TWO_HANDED = "\u00a02H"
QUIET = "<span style='color:#8a8a8a; font-weight:normal'>"
BOLD = 700
NORMAL = 400


def test_a_lone_figure_is_the_truncated_number_and_nothing_else():
    assert damage.displayed_hands(147.9, None) == "147"
    assert damage.displayed_hands(147.9, None, True) == "147"


def test_both_hands_join_with_no_break_spaces():
    assert tabtext.unmarked(damage.displayed_hands(147.9, 151.2)) == (
        "147\u00a0/\u00a0151\u00a02H")


def test_the_other_hand_is_the_quiet_one():
    """AK-298: the `/` goes with the quiet half, the `2H` with its figure."""
    assert damage.displayed_hands(147.9, 151.2) == (
        f"147{QUIET}\u00a0/\u00a0151\u00a02H</span>")
    assert damage.displayed_hands(147.9, 151.2, True) == (
        f"{QUIET}147\u00a0/</span>\u00a0151\u00a02H")
    assert damage.MUTED == weaponslots.MUTED == statsheet.MUTED \
        == arsenaltab.MUTED


def fragments(markup: str) -> list[tuple[str, int, str]]:
    """`(text, weight, colour)` per run of one format, as Qt lays it out."""
    document = QTextDocument()
    document.setHtml(markup)
    out = []
    fragment = document.firstBlock().begin()
    while not fragment.atEnd():
        piece = fragment.fragment()
        style = piece.charFormat()
        out.append((piece.text(), style.fontWeight(),
                    style.foreground().color().name()))
        fragment += 1
    return out


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
    assert tabtext.unmarked(rating.displayed_hands(
        lambda r: r.final_headline)) == (
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


def _tile_detail(weapon, rating, two_handing: bool = False) -> str:
    tile = weaponslots.WeaponTile(0, lambda *_: None, lambda *_: None,
                                  lambda *_: None)
    try:
        tile.show_slot(weaponslots.WeaponSlot(weapon=weapon, tier=TIER),
                       rating, two_handing=two_handing)
        return tile.detail.text()
    finally:
        tile.deleteLater()


def test_the_weapon_tile_puts_both_hands_inside_the_bold_figure(
        game_data, build, greatsword, bow):
    rating = damage.candidate(greatsword, TIER, build, game_data)
    figure, label = _tile_detail(greatsword, rating).split("</b>", 1)
    assert figure.endswith(TWO_HANDED + "</span>")
    assert label == f" {damage.ATTACK_RATING_LABEL}"
    assert TWO_HANDED not in _tile_detail(
        bow, damage.candidate(bow, TIER, build, game_data))


def test_the_tile_bolds_and_colours_the_chosen_hand_only(game_data, build,
                                                         greatsword):
    """AK-298 on the tile, as Qt renders it: the chosen half is bold and
    `ACCENT`, the other half normal and `MUTED`, both channels at once."""
    rating = damage.candidate(greatsword, TIER, build, game_data)
    one = str(damage.displayed(rating.final_headline))
    two = damage.displayed(rating.two_handed.final_headline)
    quiet, loud = weaponslots.MUTED, weaponslots.ACCENT

    def figure_runs(markup: str) -> list[tuple[str, int, str]]:
        runs = fragments(markup)
        first = next(i for i, run in enumerate(runs) if run[0].startswith(one))
        return runs[first:first + 2]

    assert figure_runs(_tile_detail(greatsword, rating)) == [
        (f"{one}", BOLD, loud),
        (f" / {two} 2H", NORMAL, quiet)]
    assert figure_runs(_tile_detail(greatsword, rating, True)) == [
        (f"{one} /", NORMAL, quiet),
        (f" {two} 2H", BOLD, loud)]


def test_an_armament_without_a_second_figure_looks_the_same_either_hand(
        game_data, build, bow):
    """AK-298: nothing to distribute, so no contrast is invented (A12)."""
    rating = damage.candidate(bow, TIER, build, game_data)
    assert _tile_detail(bow, rating, True) == _tile_detail(bow, rating)


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


def _arsenal_over_an_empty_build(shared_planner, game_data, hero):
    shared_planner.hero_index = game_data["heroes"].index(hero)
    shared_planner.level_slider.setValue(LEVEL)
    shared_planner.weapon_slots = [weaponslots.WeaponSlot()
                                   for _ in range(weaponslots.SLOT_COUNT)]
    shared_planner.declared = {}
    shared_planner.selected_effects = lambda: []
    shared_planner.stat_sheet.hand_switch.setChecked(False)
    shared_planner.recompute()
    tab = shared_planner.weapons_tab
    tab.upgrade.setValue(TIER)
    return tab


def test_the_arsenal_tile_shows_both_hands_only_for_a_two_handable_armament(
        shared_planner, game_data, hero, greatsword, bow):
    tab = _arsenal_over_an_empty_build(shared_planner, game_data, hero)
    assert tabtext.unmarked(_arsenal_headline(tab, greatsword)).endswith(
        TWO_HANDED)
    assert TWO_HANDED not in _arsenal_headline(tab, bow)


def test_the_arsenal_tile_quiets_the_hand_the_switch_is_not_on(
        shared_planner, game_data, hero, greatsword, bow):
    """AK-298 on the arsenal: the tile is drawn from the switch's stand
    when the tab is (re)built; the bow's lone figure is left alone."""
    tab = _arsenal_over_an_empty_build(shared_planner, game_data, hero)
    one_handed = _arsenal_headline(tab, greatsword)
    bow_one_handed = _arsenal_headline(tab, bow)
    expected = damage.candidate(greatsword, TIER,
                                shared_planner.current_build(), game_data)
    assert one_handed.startswith(
        f"{damage.displayed(expected.final_headline)}{QUIET}")
    try:
        shared_planner.stat_sheet.hand_switch.setChecked(True)
        two_handed = _arsenal_headline(tab, greatsword)
        assert two_handed.startswith(QUIET) and two_handed.endswith(TWO_HANDED)
        assert tabtext.unmarked(two_handed) == tabtext.unmarked(one_handed)
        assert _arsenal_headline(tab, bow) == bow_one_handed
    finally:
        shared_planner.stat_sheet.hand_switch.setChecked(False)


def test_flipping_the_switch_moves_the_emphasis_without_a_rebuild(
        shared_planner, game_data, hero, greatsword):
    """AK-298: the tile and the sheet -- panel and popup -- follow the
    switch on its own signal, no closing or re-choosing the armament; no
    figure changes with it (AK-293)."""
    sheet = _sheet_with(shared_planner, game_data, hero, greatsword)
    shared_planner.level_slider.setValue(LEVEL)
    shared_planner.stat_sheet.hand_switch.setChecked(False)
    shared_planner.recompute()
    tile = sheet.weapon_tiles[1]

    def drawn() -> tuple[str, str, str]:
        return (tile.detail.text(), sheet.ar_label.text(),
                sheet._ar_breakdown_text())

    before = drawn()
    try:
        shared_planner.stat_sheet.hand_switch.setChecked(True)
        after = drawn()
        for was, now in zip(before, after):
            assert was != now
            assert tabtext.unmarked(was) == tabtext.unmarked(now)
            assert was.count(QUIET) == now.count(QUIET) > 0
        final = damage.displayed(sheet.last_ar["final"])
        assert f"<b>Total {final}{QUIET}" in before[2]
        assert f"<b>Total {QUIET}{final}" in after[2]
    finally:
        shared_planner.stat_sheet.hand_switch.setChecked(False)
    assert drawn() == before


def test_the_switch_s_tooltip_says_where_the_hand_shows():
    """AK-298: the one added half-sentence, otherwise AK-292's text."""
    assert statsheet.HAND_TOOLTIP == (
        "Ranks the build's attack power one-handed or two-handed — Optimize "
        "and effects that only read while two-handing follow this switch, "
        "and the figure it uses is the one highlighted on every tile, sheet "
        "and arsenal row. Armaments that cannot be two-handed keep their "
        "one-handed figure either way. Saved with this build.")


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
