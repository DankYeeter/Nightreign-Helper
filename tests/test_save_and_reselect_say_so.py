"""Saving a build and re-clicking the chosen Nightfarer answer (QA-301).

AK-381: a saved build is confirmed at the build list, and an overwrite says
so. AK-382: a click on the Nightfarer already chosen loads nothing again and
says why nothing happened. Both are hints in the window's tooltip pattern,
anchored at the widget that changed rather than at the pointer.
"""

from __future__ import annotations

import pytest

from nrplanner import app as appmod
from nrplanner import favourites


@pytest.fixture(autouse=True)
def a_store_of_our_own():
    """Nothing of another test is inherited, and nothing is left behind."""
    from tests.conftest import clear_settings

    clear_settings()
    yield
    clear_settings()


@pytest.fixture
def hints(monkeypatch) -> list[tuple]:
    """Every tooltip the window shows, as (text, widget, msec)."""
    said: list[tuple] = []

    class Tip:
        @staticmethod
        def showText(position, text, widget=None, rect=None, msec=-1):
            said.append((text, widget, msec))

    monkeypatch.setattr(appmod, "QToolTip", Tip)
    return said


def save_as(planner, monkeypatch, name: str) -> None:
    class Dialog:
        @staticmethod
        def getText(*_args, **_kwargs):
            return name, True

    monkeypatch.setattr(appmod, "QInputDialog", Dialog)
    planner._save_build()


def test_a_saved_build_is_confirmed_at_the_build_list(planner, monkeypatch,
                                                      hints):
    """AK-381: `Saved "{name}".`, then `Saved over "{name}".` for the same
    name, each once, at `build_box`, for 4 s."""
    save_as(planner, monkeypatch, "Mine")
    save_as(planner, monkeypatch, "Mine")

    assert hints == [('Saved "Mine".', planner.build_box, 4000),
                     ('Saved over "Mine".', planner.build_box, 4000)]


def test_a_long_name_is_cut_after_forty_letters(planner, monkeypatch, hints):
    """AK-381: a name over 40 letters stands cut at the end with `…`."""
    name = "A" * 40 + "B" * 5
    save_as(planner, monkeypatch, name)

    assert hints[0][0] == f'Saved "{"A" * 40}…".'


def test_a_refused_name_says_only_why(planner, monkeypatch, hints):
    """AK-381: no confirmation after a refusal, its own hint is the one."""
    save_as(planner, monkeypatch, appmod.chalices.EQUIPPED_NAME)

    assert len(hints) == 1 and not hints[0][0].startswith("Saved")


def test_the_first_choice_runs_in_full_even_for_the_first_nightfarer(
        planner):
    """AK-382: `hero_index` starts at 0, so the start's own choice of index 0
    must not be taken for a re-click."""
    assert planner.hero_index == 0
    assert planner.hero_name_label.text() == planner.heroes[0]["name"]
    assert planner.hero_tiles[0].isChecked()


def test_a_click_on_the_chosen_nightfarer_loads_nothing_and_says_so(
        planner, monkeypatch, hints):
    """AK-382: the tile stays ticked, nothing is reloaded or written, and
    `{Name} is already selected.` stands under the tile."""
    reloads: list[int] = []
    monkeypatch.setattr(planner, "reload_chalices",
                        lambda: reloads.append(1))
    favourites.settings().setValue(appmod.HERO_KEY, -1)
    tile = planner.hero_tiles[planner.hero_index]
    name = planner.current_hero()["name"]

    tile.click()

    assert reloads == []
    assert tile.isChecked()
    assert favourites.settings().value(appmod.HERO_KEY, type=int) == -1
    assert hints == [(f"{name} is already selected.", tile, 4000)]

    other = (planner.hero_index + 1) % len(planner.hero_tiles)
    planner.hero_tiles[other].click()
    assert reloads == [1], "another Nightfarer still loads in full"
