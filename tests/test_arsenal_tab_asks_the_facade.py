"""The arsenal tab's figure is the facade's answer, at the tab's own tier.

`ARCHITECTURE.md` Nachtrag III, checkpoint 20 -- and the blind spot that
checkpoint had to be written into, because nothing else covered it.

**What guarded the arsenal tab before this file: its attribute set, and
nothing else.** `test_one_build.py` checks three times that
`weapons_tab.attributes` is the build the planner tab shows (QA-001). No test
read a single figure off the tab, and none read the tier it ranked at.
Measured on 2026-09-03, on the tree before AD-019 step W4:

* halving the AR figure of **every** tile on the tab -- `rating.total * 0.5` --
  left **264 of 264** tests green;
* ranking the whole tab at `weapons.MAX_UPGRADE` instead of at the spinbox,
  so the "Upgrade to +n" control moved nothing at all, left **264 of 264**
  green.

Both are kept by name in `scripts/differential/mutate.py`
(`arsenal-tile-figure-halved`, `arsenal-ranks-at-the-slot-tier`) so the claim
can be re-run rather than believed.

**Read off the rendered tile, not off `tab.ratings`.** The list behind the tab
is what W4 changed; the label is what a player compares with the tile on the
planner tab. A test standing on the list would have moved with the change it
is meant to hold still. The AR row is located by its own left-hand label, so
a change in how a tile is laid out fails the match instead of quietly reading
a different number.

The two questions are separate cases on purpose. That the tab shows the
facade's `candidate()` answer, and that it asks that question at the
**spinbox's** tier rather than at the slot's, are different claims: the first
one holds just as well for a tab that ranks everything at tier 4.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QLabel

from nrplanner import arsenaltab, damage, weapons, weaponslots

from tests import weapon_damage_cases as cases

LEVEL = 15

#: The left-hand label of the row this file reads. `Tile` writes the rows as
#: (label, value) pairs, headline first.
AR_ROW = "AR"


def armaments(game_data, hero) -> list[int]:
    """Four armaments of four different kinds, chosen by query, never by id.

    The Nightfarer's own starting armament, a bow, a colossal sword and a
    catalyst: melee and ranged, physical and magic scaling, and one whose
    Strength wall is the steepest in the game.
    """
    return [
        hero["starting_weapon"],
        cases.first_of_family(game_data, "Bow"),
        cases.heaviest_of_family(game_data, "Colossal Sword"),
        cases.first_of_family(game_data, "Glintstone Staff"),
    ]


def drawn_tiles(tab, weapon: dict) -> list:
    """Every tile the tab really drew for this armament's name.

    The tab builds its sections lazily and opens them itself when a search
    matches a modest number of rows, so a search on the armament's own name
    is what puts a tile on screen at all. Names are not unique in the dataset
    -- four armaments are called "Scholar's Thrusting Sword" -- so this hands
    back every tile carrying the name and the caller says what it expects.
    """
    tab.search.setText(f'"{weapon["name"]}"')
    tab.recalculate()
    tiles = tab.scroll.widget().findChildren(arsenaltab.Tile)
    return [tile for tile in tiles if tile_name(tile) == weapon["name"]]


def tile_name(tile) -> str:
    """The armament name a tile carries.

    `Tile` adds the icon badge first and the name second, both `QLabel`, so
    the name is the second child. The badge holds no text, which is asserted
    rather than assumed: if the header ever gains a label, this reads the
    wrong one and has to fail here rather than compare the wrong armament.
    """
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


@pytest.fixture(scope="module")
def hero(game_data):
    """Wylder, the Nightfarer QA measured the QA-018/055 divergence on."""
    return cases.hero_by_name(game_data, "Wylder")


def prepare(planner, game_data, hero, slots) -> None:
    """Put the planner on this Nightfarer, this level and these tiles."""
    planner.hero_index = game_data["heroes"].index(hero)
    planner.level_slider.setValue(LEVEL)
    planner.weapon_slots = slots
    planner.declared = {}
    planner.selected_effects = lambda: []
    planner.recompute()


def empty_slots() -> list:
    return [weaponslots.WeaponSlot() for _ in range(weaponslots.SLOT_COUNT)]


def test_every_tile_shows_the_candidate_answer_for_the_chosen_tier(
        planner, game_data, hero):
    """The rendered AR is `damage.candidate()` at the tab's own tier.

    Over four armaments and every tier the spinbox can ask for. The figure is
    compared as the tile writes it, because that is what a player reads; the
    unrounded comparison over the whole dataset belongs to the differential
    track (`scripts/differential/rasters/arsenal_tab.json`), not here.
    """
    prepare(planner, game_data, hero, empty_slots())
    tab = planner.weapons_tab
    build = planner.current_build()

    seen = 0
    figures: set[str] = set()
    for weapon_id in armaments(game_data, hero):
        weapon = cases.weapon_by_id(game_data, weapon_id)
        for tier in range(weapons.MIN_UPGRADE,
                          weapons.MAX_UPGRADE + 1):
            tab.upgrade.setValue(tier)
            tiles = drawn_tiles(tab, weapon)
            assert tiles, (
                f"the tab drew no tile for {weapon['name']!r} at tier {tier}, "
                f"so there is nothing here to check")

            expected = damage.candidate(weapon, tier, build, game_data)
            for tile in tiles:
                assert tile_ar(tile) == f"{expected.final_total:.0f}", (
                    f"{weapon['name']!r} at tier {tier}: the tab and the "
                    f"facade name different figures")
                seen += 1
                figures.add(f"{weapon['name']}@{tier}={tile_ar(tile)}")

    assert seen >= len(armaments(game_data, hero)), "nothing was compared"
    assert len(figures) > 1, (
        "every tile in this case shows the same figure, so an assertion on "
        "it could not tell the armaments or the tiers apart")


def test_the_tab_ranks_at_its_spinbox_tier_and_not_at_the_slot_s(
        planner, game_data, hero):
    """Checkpoint 20, and it is QA-055's own case.

    Slot on tier 3, spinbox on 1, not a single relic: the tab must go on
    ranking at tier 1, and it **may** differ from the tile and the panel next
    door. That difference is the tab's question, not a defect (AD-020,
    point 1) -- a test demanding equality here would be the error.

    What the case does insist on is that the two figures are the answers to
    the tiers they were asked for. Without the second half a tab that ranked
    at the slot's tier and a tab that ranked at the spinbox's would both pass
    whenever the two tiers happened to agree, which is why the guard below
    refuses a case where they do.
    """
    weapon = cases.weapon_by_id(game_data, hero["starting_weapon"])
    slot_tier, spinbox_tier = 3, 1

    slots = empty_slots()
    slots[0] = weaponslots.WeaponSlot(weapon=weapon, tier=slot_tier)
    prepare(planner, game_data, hero, slots)

    tab = planner.weapons_tab
    tab.upgrade.setValue(spinbox_tier)
    build = planner.current_build()

    at_spinbox = damage.candidate(weapon, spinbox_tier, build, game_data)
    at_slot = damage.candidate(weapon, slot_tier, build, game_data)
    assert f"{at_spinbox.final_total:.0f}" != f"{at_slot.final_total:.0f}", (
        f"{weapon['name']!r} rates the same at tier {spinbox_tier} and at "
        f"tier {slot_tier}, so this case cannot tell the two tiers apart. "
        f"Pick an armament the upgrade moves.")

    tiles = drawn_tiles(tab, weapon)
    assert tiles, f"the tab drew no tile for {weapon['name']!r}"
    for tile in tiles:
        assert tile_ar(tile) == f"{at_spinbox.final_total:.0f}", (
            f"the tab is ranking {weapon['name']!r} at a tier the spinbox "
            f"does not show")
