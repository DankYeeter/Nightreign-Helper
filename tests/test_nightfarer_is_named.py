"""T-328a: the Nightfarer chosen last session is who a new window opens on.

A fixed key, `app.HERO_KEY`, carries the chosen Nightfarer's `id` -- the same
shape as `variant/{hero_id}` (`HeroTile.set_variant`) and AK-347's
`damage_type`/`hit_with`, never a key built from what the player typed.
"""

from __future__ import annotations

from PySide6.QtCore import QSettings

from nrplanner import app as appmod
from nrplanner import favourites

from tests.conftest import _new_planner, clear_settings, wait_for_the_save


def test_chosen_hero_survives_a_restart(game_data, qapp):
    first = _new_planner(game_data)
    first.select_hero(3)
    chosen_id = first.heroes[3]["id"]

    second = wait_for_the_save(appmod.Planner(game_data))
    try:
        assert second.hero_index == 3
        assert second.heroes[second.hero_index]["id"] == chosen_id
    finally:
        clear_settings()


def test_an_id_no_hero_carries_falls_back_to_the_first(game_data, qapp):
    clear_settings()
    QSettings(favourites.ORG, favourites.APP).setValue(appmod.HERO_KEY, -999)

    window = wait_for_the_save(appmod.Planner(game_data))
    try:
        assert window.hero_index == 0
    finally:
        clear_settings()
