"""The figure the program calls "Attack rating" is the figure the game shows.

Every other test in this suite holds the calculation against itself: the
golden file freezes what it said yesterday, the differential track holds two
trees against each other, the facade tests hold one display against another.
None of them can see the whole calculation being uniformly wrong, and it was
-- by a factor of 1/0.6, for as long as the program existed (QA-095).

This file is the one guard that stands on something outside the program:
`tests/data/game_attack_power.json`, twenty-three readings copied out of a
community measurement of the game's own armament panel. Its header names the
sheet, the day it was read, the game version, what was left out and why, and
the hit rate of the whole sheet -- so that the twenty-three rows can be seen
not to be a selection of the cases that happen to pass.

**Its two killing mutations**, both registered in
`scripts/differential/mutate.py` and both required to turn this file red:

* `attack-power-rate-neutralised` -- `weapons.GAME_ATTACK_POWER_RATE` from
  0.6 to 1.0. Every reading here fails; it is the mutation that says the
  factor is load-bearing rather than decorative.
* `attack-power-rounded-instead-of-truncated` -- `math.floor` in
  `damage.displayed` to `round`. Only the readings whose figure has a
  fractional part of half or more fail, which is why
  `test_at_least_one_reading_tells_truncation_from_rounding` insists there is
  such a reading in the file: without one, the second mutation would survive
  and this file would be silent about the difference between the two rules.

**What it does not check.** Reinforced rarities, infused variants, Scholar
and Undertaker, catalysts, and the two armament/Nightfarer pairings with a
measured deviation nobody has explained (QA-096, QA-097). The header of the
data file lists them; none of them is in the readings, and none of them is
claimed by this file.
"""

from __future__ import annotations

import json
import math
import pathlib

import pytest

from nrplanner import damage, model, weapons
from tests import weapon_damage_cases as cases

READINGS = pathlib.Path(__file__).parent / "data" / "game_attack_power.json"

_MEASUREMENT = json.loads(READINGS.read_text(encoding="utf-8"))
_SOURCE = _MEASUREMENT["source"]
_READINGS = _MEASUREMENT["readings"]
_IDS = [f"{entry['nightfarer']} lv{entry['level']} :: {entry['name']}"
        for entry in _READINGS]


def _same_game(data: dict) -> None:
    """Skip rather than fail where the game underneath has moved on.

    The same reasoning as the golden file's: a figure computed from other
    inputs is evidence in neither direction. Here it is stronger still --
    these readings were taken off a running game of that version, and a patch
    that moved an armament's base damage would move the game's own number
    too, so the two sides would have to be re-measured together.
    """
    recorded = _SOURCE["game_data_version"]
    running = data.get("meta", {}).get("data_version")
    if running != recorded:
        pytest.skip(
            f"the readings in {READINGS.name} were taken from game data "
            f"{recorded}, this machine has {running}. Re-measure against the "
            f"game before trusting either side.")


def _figure(data: dict, entry: dict):
    """What the program shows for one reading, asked the way a display asks.

    Through `damage.candidate`, not `weapons.rate`: the facade is the only
    thing allowed to rate an armament (AD-021), and asking it here means this
    file measures the same path the arsenal tab and the advisor take. With no
    relics equipped every attack multiplier is 1.0, so `final_total` is the
    armament and its scaling and nothing else -- which is what the sheet
    measured.
    """
    hero = cases.hero_by_name(data, entry["nightfarer"])
    weapon = cases.weapon_by_id(data, entry["weapon"])
    build = model.compute(hero, entry["level"], [], data.get("curves", {}))
    own_tier = weapon.get("rarity", 0) + 1
    return weapon, own_tier, damage.candidate(weapon, own_tier, build, data)


@pytest.mark.parametrize("entry", _READINGS, ids=_IDS)
def test_the_program_shows_the_number_the_game_shows(game_data, entry):
    _same_game(game_data)
    weapon, own_tier, rating = _figure(game_data, entry)

    # Two preconditions, so that a green result cannot come from having
    # measured something else. The name pins the id against a patch that
    # renumbers armaments; the tier pins the reading to the armament's own
    # rarity, which is the state the sheet was measured in -- ask for a tier
    # above it and the reinforce table would raise the figure.
    assert weapon["name"] == entry["name"], (
        f"armament {entry['weapon']} is {weapon['name']!r} in this dataset "
        f"and was {entry['name']!r} when the sheet was read")
    assert rating.tier_applied == own_tier, (
        f"{entry['name']!r} was rated at tier {rating.tier_applied}, not at "
        f"its own {own_tier}; the reading is for an unreinforced armament")
    assert not rating.rates, (
        f"{entry['name']!r} carries the multipliers {rating.rates}, but the "
        f"sheet was measured with no relics equipped")

    assert damage.displayed(rating.final_total) == entry["attack_power"], (
        f"{entry['name']!r} for {entry['nightfarer']} at level "
        f"{entry['level']}: the game shows {entry['attack_power']}, this "
        f"program shows {damage.displayed(rating.final_total)} "
        f"(unrounded {rating.final_total!r})")


def test_at_least_one_reading_tells_truncation_from_rounding(game_data):
    """Without this, replacing `floor` with `round` would go unnoticed.

    Truncation and rounding agree on every figure whose fractional part is
    below a half, so a file of readings that all happened to land there would
    pass under either rule and say nothing about which one the game uses. The
    measurement settled that question -- Soldier's Crossbow rates 148, 0.6 x
    148 = 88.8, and the game shows 88 rather than 89 -- and this asserts that
    the case which settles it is still in the file.
    """
    _same_game(game_data)
    telling = []
    for entry in _READINGS:
        _weapon, _tier, rating = _figure(game_data, entry)
        if math.floor(rating.final_total) != round(rating.final_total):
            telling.append((entry["name"], rating.final_total))

    assert telling, (
        "every reading in the file rates at a fractional part below a half, "
        "so all of them would pass with `round` in place of `math.floor` and "
        "this file could not tell the game's rule from the other one. Put a "
        "reading back that does -- Soldier's Crossbow is the plainest.")


def test_the_readings_carry_their_provenance():
    """A number without its source is a number nobody can re-measure.

    Asserted rather than trusted to review: the header is the whole reason
    these twenty-three figures may be used as evidence, and a later edit that
    dropped a field would leave the file looking exactly as authoritative.
    """
    for field_name in ("what", "sheet", "read_on", "game_data_version",
                       "measured_by", "levels", "left_out",
                       "how_these_rows_were_picked",
                       "not_a_selection_of_the_hits"):
        assert _SOURCE.get(field_name), (
            f"{READINGS.name} has no {field_name!r} in its source block")

    assert len(_READINGS) == 23, (
        "the set is meant to stay small and fixed; changing it is a decision "
        "with a reason, so the count is written down here as well")
    nightfarers = {entry["nightfarer"] for entry in _READINGS}
    assert "Duchess" not in nightfarers, (
        "the Duchess column of the sheet is mixed between two levels and is "
        "not usable as a source (QA-098)")
    assert len(nightfarers) == 7, (
        f"the readings cover {sorted(nightfarers)}; seven Nightfarers were "
        f"meant to be in the set")


def test_the_factor_is_named_once_and_is_the_measured_one():
    """The constant is a measured quantity, so its value is part of the test.

    `weapons.rate` is checked against the game by every case above; this adds
    the one thing they cannot say, which is that the figure they agree on is
    reached through the named constant rather than through a number written
    somewhere else. 0.6 is the value the intersection over the nine
    scaling-free armaments allows -- k in [0.599315, 0.600928) -- and the
    only round number in it.
    """
    assert weapons.GAME_ATTACK_POWER_RATE == 0.6
    assert 0.599315 <= weapons.GAME_ATTACK_POWER_RATE < 0.600928
