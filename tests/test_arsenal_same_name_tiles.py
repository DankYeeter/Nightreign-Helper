"""QA-099a: armaments the game lists twice under one name, with the same
numbers, take one tile -- and the tile's tooltip says how many it stands for.

The dataset carries `Scholar's Thrusting Sword` four times and `Recluse's
Staff` and `Finger Seal` twice, differing only in fields no tile shows
(icon, effect pool, spell list). Four tiles reading the same made a reader
look for a difference that is not there.
"""

from __future__ import annotations

import collections

import pytest
from PySide6.QtWidgets import QLabel

from nrplanner import arsenaltab

from tests import weapon_damage_cases as cases


def a_name_listed_more_than_once(data: dict) -> tuple[str, int]:
    names = collections.Counter(weapon["name"] for weapon in data["weapons"])
    repeated = [(name, count) for name, count in names.items() if count > 1]
    if not repeated:
        pytest.skip("no armament of this dataset is listed twice under one "
                    "name, so this case has nothing to merge")
    return max(repeated, key=lambda pair: pair[1])


def tiles_named(tab, name: str) -> list:
    return [tile for tile in tab.scroll.widget().findChildren(arsenaltab.Tile)
            if tile.findChildren(QLabel)[1].text() == name]


def test_same_name_same_numbers_is_one_tile_that_says_so(planner, game_data):
    name, count = a_name_listed_more_than_once(game_data)
    hero = cases.hero_by_name(game_data, "Wylder")
    planner.hero_index = game_data["heroes"].index(hero)
    planner.declared = {}
    planner.recompute()
    tab = planner.weapons_tab
    tab.search.setText(f'"{name}"')
    tab.recalculate()

    tiles = tiles_named(tab, name)
    assert len(tiles) == 1, (
        f"{name!r} is listed {count} times with the same numbers and takes "
        f"{len(tiles)} tiles instead of one")
    # Written out rather than imported (L-008): the sentence the tile owes
    # the player, not whatever the constant happens to say.
    assert tiles[0].toolTip() == (
        f"The game lists {count} armaments under this name with these "
        f"numbers; shown once.")
