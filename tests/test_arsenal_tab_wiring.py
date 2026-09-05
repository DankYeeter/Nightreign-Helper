"""The arsenal tab's controls have to trigger `recalculate()` themselves.

`qa/findings.md` QA-085, `ARCHITECTURE.md` AD-019/W5. `test_one_build.py`
guards which build every tab computes, and
`test_arsenal_tab_asks_the_facade.py` guards that the tab's figure is the
facade's answer -- but both of those, and every other case in this suite,
call `recalculate()` themselves before reading a figure. That leaves the two
lines that are supposed to call it *for* the player -- the spinbox and the
tab switch -- checked by nobody: removing either
`self.upgrade.valueChanged.connect(self.recalculate)` or
`tabs.currentChanged.connect(...recalculate())` left the full suite green,
because the render the test then reads was already produced by its own
setup call.

Both cases below move the control under test exactly once and read the
rendered tile straight after, with no `recalculate()` call of their own in
between. That is the whole point: a wiring gap and a working wire produce the
same figure until the control moves.
"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel

from nrplanner import arsenaltab, damage, weapons, weaponslots

from tests import weapon_damage_cases as cases

LEVEL = 15

#: `Tile` writes rows as (label, value) pairs; this is the row this file reads.
AR_ROW = "AR"


def tile_name(tile) -> str:
    """The armament name a tile carries (icon badge first, name second)."""
    labels = tile.findChildren(QLabel)
    assert len(labels) >= 2 and labels[0].text() == "", (
        "the tile header is not the icon badge followed by the name any "
        "more; this helper reads the wrong label")
    return labels[1].text()


def tile_ar(tile) -> str:
    """The AR figure as the tile renders it, located by its own row label."""
    labels = tile.findChildren(QLabel)
    texts = [label.text() for label in labels]
    assert AR_ROW in texts, f"no {AR_ROW!r} row on this tile: {texts!r}"
    return texts[texts.index(AR_ROW) + 1]


def named_tile(tab, name: str):
    """The one tile currently on screen for this armament's name, or none.

    Reads whatever the tab is already showing -- it does not search, filter
    or recalculate, because doing any of those would be a second way to
    force the redraw this file is testing the absence of.
    """
    tiles = [tile for tile in tab.scroll.widget().findChildren(arsenaltab.Tile)
             if tile_name(tile) == name]
    assert tiles, f"no tile for {name!r} is on screen to read"
    return tiles[0]


def empty_slots() -> list:
    return [weaponslots.WeaponSlot() for _ in range(weaponslots.SLOT_COUNT)]


def test_moving_the_spinbox_alone_repaints_the_tile(planner, game_data):
    """`upgrade.valueChanged` has to reach `recalculate()` on its own.

    QA-085, first mutation: `self.upgrade.valueChanged.connect(self.recalculate)`
    removed. Registered as `arsenal-spinbox-does-not-recalculate` in
    `scripts/differential/mutate.py`.
    """
    hero = cases.hero_by_name(game_data, "Wylder")
    weapon = cases.weapon_by_id(game_data, hero["starting_weapon"])
    planner.hero_index = game_data["heroes"].index(hero)
    planner.weapon_slots = empty_slots()
    planner.declared = {}
    planner.recompute()

    tab = planner.weapons_tab
    # Setup only: puts one tile for this armament on screen and expands its
    # section. Not the call under test -- everything after this line reaches
    # the tab through the spinbox alone.
    tab.search.setText(f'"{weapon["name"]}"')
    tab.recalculate()

    build = planner.current_build()
    low, high = weapons.MIN_UPGRADE, weapons.MAX_UPGRADE
    expected_low = damage.candidate(weapon, low, build, game_data).final_total
    expected_high = damage.candidate(weapon, high, build, game_data).final_total
    assert (damage.displayed(expected_low)
            != damage.displayed(expected_high)), (
        f"{weapon['name']!r} rates the same at +{low} and +{high}, so this "
        f"case cannot tell the two tiers apart. Pick an armament the "
        f"upgrade moves.")

    tab.upgrade.setValue(low)
    assert (tile_ar(named_tile(tab, weapon["name"]))
            == str(damage.displayed(expected_low)))

    # The only action under test: nothing here calls recalculate() or
    # rebuild() -- if the spinbox's own signal is wired, this alone has to
    # repaint the tile.
    tab.upgrade.setValue(high)

    assert (tile_ar(named_tile(tab, weapon["name"]))
            == str(damage.displayed(expected_high))), (
        "moving the spinbox alone must repaint the tile; reading the +1 "
        "figure here means self.upgrade.valueChanged is not wired to "
        "recalculate() any more")


def test_switching_to_the_tab_alone_repaints_it_for_the_current_build(
        planner, game_data):
    """`tabs.currentChanged` has to reach `recalculate()` on its own.

    QA-085, second mutation, and QA-001 in a new shape: the tab must not go
    on ranking against a build the player has since moved away from.
    Registered as `arsenal-tab-switch-does-not-recalculate` in
    `scripts/differential/mutate.py`.
    """
    hero = cases.hero_by_name(game_data, "Wylder")
    weapon = cases.weapon_by_id(game_data, hero["starting_weapon"])
    planner.hero_index = game_data["heroes"].index(hero)
    planner.weapon_slots = empty_slots()
    planner.declared = {}
    planner.recompute()

    tab = planner.weapons_tab
    tab.search.setText(f'"{weapon["name"]}"')
    tab.recalculate()
    before = tile_ar(named_tile(tab, weapon["name"]))

    # Move the build without telling the weapons tab: a Strength effect on
    # the starting armament's own slot, which is the raise
    # `test_a_declared_conditional_reaches_every_tab`'s sibling cases already
    # rely on to move this Nightfarer's own weapon.
    strength_id = cases.effects_raising_attribute(
        game_data, hero, "Strength", 1)[0]
    planner.weapon_slots[0].effect_ids = [strength_id]
    planner.recompute()

    build = planner.current_build()
    tier = tab.upgrade.value()
    expected = damage.candidate(weapon, tier, build, game_data).final_total
    assert str(damage.displayed(expected)) != before, (
        f"raising Strength did not move {weapon['name']!r}'s figure, so "
        f"this case cannot tell the stale build from the current one. Pick "
        f"an effect the armament's damage responds to.")

    tabs = planner.centralWidget()
    assert tabs.currentWidget() is not tab, (
        "the weapons tab is already the front tab before this test switches "
        "to it, so switching to it again would fire no currentChanged "
        "signal and this case would prove nothing")

    # The only action under test: no recalculate() call of this test's own
    # follows. If tabs.currentChanged is wired, bringing the tab to the
    # front has to repaint it for the build set up just above.
    tabs.setCurrentWidget(tab)

    assert (tile_ar(named_tile(tab, weapon["name"]))
            == str(damage.displayed(expected))), (
        "switching to the tab alone must repaint it for the current build; "
        "reading the pre-Strength figure here means tabs.currentChanged is "
        "not wired to recalculate() any more")
