"""The attack rating must still say exactly what it said before.

`tests/golden/weapon_damage.json` was captured from `Planner._refresh_weapon_
damage` **before** that calculation was moved out of the window and into
`nrplanner/damage.py` (AD-005). Every number and every line of the panel is
frozen in it, so a move that quietly changed one shows up here as a failure
rather than as a wrong figure in front of a player months later.

Re-capture (`python scripts/capture_weapon_damage.py`) only after a game
patch has genuinely changed the inputs, and say so in the commit. Capturing
it to make a red test green would delete the only evidence that the
calculation is unchanged.
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
