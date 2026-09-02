"""The attack rating must still say exactly what it said before.

`tests/golden/weapon_damage.json` was captured from `Planner._refresh_weapon_
damage` **before** that calculation was moved out of the window and into
`nrplanner/damage.py` (AD-005). Every number and every line of the panel is
frozen in it, so a move that quietly changed one shows up here as a failure
rather than as a wrong figure in front of a player months later.

Two tests, because there are two claims:

* the panel still says the same thing -- what the player sees;
* the extracted module says the same thing on its own, with no window
  anywhere near it -- which is what the build advisor will call.

Re-capture (`python scripts/capture_weapon_damage.py`) under one of exactly
two conditions, and say which in the commit:

* a game patch has genuinely changed the inputs; or
* a documented decision has changed one of them -- the commit names the AD or
  QA number, so the next reader gets the reason and not "was adjusted once"
  (`ARCHITECTURE.md` AD-019, checkpoint 22).

Capturing it to make a red test green is neither, and would delete the only
evidence that the calculation is unchanged.

**What this file does not hold, said out loud rather than left to be
discovered:** the weapon *tile* above the panel. `weapon_damage_cases.run`
records the panel's text and the figures behind it, and nothing of the six
tiles -- which is why the tile could answer a different question from the
panel for as long as it did (QA-056). The tile is covered between two guards
instead of by this one: the panel's total is frozen here, and
`test_weapon_tile_and_panel_agree.py` holds the tile to that total. Remove
either and the tile is unguarded again.

AD-019 step W3 was allowed to re-capture and did not need to: a fresh capture
on the post-W3 tree came back byte-identical to this file. W3 changed what the
tile asks, not what the panel answers.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from tests import weapon_damage_cases as cases

GOLDEN = pathlib.Path(__file__).parent / "golden" / "weapon_damage.json"

_FROZEN = json.loads(GOLDEN.read_text(encoding="utf-8"))
_CASES = _FROZEN["cases"]
_IDS = [entry["case"]["name"] for entry in _CASES]


def _same_dataset(data: dict) -> None:
    """Skip rather than fail when the game underneath has moved on.

    A figure computed from other inputs is not evidence in either direction:
    it neither shows the calculation intact nor shows it broken. So the honest
    answer on a patched game is "not checked here", loudly, with the two
    versions named.
    """
    recorded = _FROZEN["dataset"]
    meta = data.get("meta", {})
    if meta.get("data_version") != recorded.get("data_version"):
        pytest.skip(
            f"golden file was captured from game data "
            f"{recorded.get('data_version')}, this machine has "
            f"{meta.get('data_version')}. Verify the numbers in game, then "
            f"re-run scripts/capture_weapon_damage.py."
        )


@pytest.mark.parametrize("entry", _CASES, ids=_IDS)
def test_weapon_damage_panel_matches_the_golden_values(
        shared_planner, game_data, entry):
    _same_dataset(game_data)
    assert cases.run(shared_planner, game_data, entry["case"]) \
        == entry["expected"]


@pytest.mark.parametrize("entry", _CASES, ids=_IDS)
def test_damage_module_matches_the_golden_values(game_data, entry):
    """The same figures, computed without a window.

    This is the test the advisor depends on. It builds no Planner, so a
    calculation that still needed one would fail here.
    """
    from nrplanner import damage

    _same_dataset(game_data)
    case = entry["case"]
    expected = entry["expected"]["last_ar"]
    slots = cases.armament_slots(game_data, case)
    active = slots[case["active"]]
    if not active.filled:
        assert expected == {}, "an empty tile has no attack rating to give"
        return

    hero = cases.hero_by_name(game_data, case["hero"])
    rating = damage.attack_rating(
        active.weapon, active.tier, cases.build_for(game_data, case),
        game_data,
        starting_armament=damage.is_starting_armament(
            active.weapon, hero, case["active"]),
    )

    assert cases.rounded(rating.figures()) == expected
