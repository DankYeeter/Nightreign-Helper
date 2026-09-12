"""What the program shows for a staff or a seal is what the game shows.

The companion of `tests/test_attack_power_against_the_game.py`, for the one
class of armament that file explicitly does not cover. The game shows a
catalyst's spell scaling where it shows every other armament's attack power,
and until T-046 this program showed the physical attack rating instead --
a figure the game never puts on screen for a catalyst, and one that ranked
them in a different order (QA-099: Rotten Crystal Staff ahead of Carian Regal
Scepter, where the game reads 182 against 237).

This file stands on something outside the program:
`tests/data/game_catalyst_scaling.json`, the whole catalyst block of the same
community sheet -- 28 catalysts x 3 Nightfarers, taken entire, nothing
selected -- and a second, independently collected list of 28 figures beside
it. Its header names the sheet, the rows, the day, the game version, what was
left out and which two armament names in the data are shared, so the 84 cells
can be seen not to be a selection of the ones that pass.

**Its four killing mutations**, each registered in
`scripts/differential/mutate.py`, each measured on 2026-09-05 against this
file's own readings:

* `catalyst-scaling-rate-ignored` -- the reinforce rate is not read and every
  catalyst falls back on the bare constant. 78 of the 84 cells and 26 of the
  28 reference figures fail. This is QA-099 c in its behavioural form: the
  shape a renamed paramdef field would have produced silently.
* `catalyst-curve-hardcoded-to-zero` -- the armament's own curve id is
  replaced by a fixed one. 84 of 84 and 28 of 28 fail. It stands for the
  whole family T-043 ruled out: exactly one of the 82 curves in the data
  admits any constant at all.
* `catalyst-influence-inside-the-bracket` -- the AttackElementCorrectParam
  influence of 0.9, which the attack rating does apply, taken inside the
  bracket here as well. 84 of 84 and 6 of 28 fail. Without this mutation
  nothing would say that the influence belongs to the attack rating and not
  to this figure.
* `attack-power-rounded-instead-of-truncated` -- `math.floor` in
  `damage.displayed` to `round`. 39 of the 84 cells and 16 of the 28
  reference figures fail. It is the mutation the attack-rating file already
  registers, reused rather than copied: there is one display rule and one
  place it lives, so a second entry with the same anchor would be a second
  name for one edit. `test_at_least_one_reading_tells_truncation_from_
  rounding` is what keeps a reading that can tell the two apart in the file.

**What this file does not check.** Upgraded catalysts -- every reading is at
the armament's own rarity, which is the state the sheet was read in, and
nothing here says what a reinforced staff shows. What a spell actually hits
for: this is the number on the armament panel, and MagicParam has never been
read. The 227 unnamed catalyst rows of the params, which carry the same
structure and no figure to compare against.
"""

from __future__ import annotations

import json
import math
import pathlib

import pytest

from nrplanner import damage, model, weapons
from tests import weapon_damage_cases as cases

READINGS = (pathlib.Path(__file__).parent / "data"
            / "game_catalyst_scaling.json")

_MEASUREMENT = json.loads(READINGS.read_text(encoding="utf-8"))
_SOURCE = _MEASUREMENT["source"]
_READINGS = _MEASUREMENT["readings"]
_REFERENCE = _MEASUREMENT["reference_list"]
_IDS = [f"{entry['nightfarer']} lv{entry['level']} :: {entry['name']}"
        for entry in _READINGS]
_REFERENCE_IDS = [entry["name"] for entry in _REFERENCE["readings"]]


def _same_game(data: dict) -> None:
    """Skip rather than fail where the game underneath has moved on.

    The same reasoning as the attack-rating file's: these readings were taken
    off a running game of that version, and a patch that moved a reinforce
    rate would move the game's own display with it, so the two sides would
    have to be re-measured together.
    """
    recorded = _SOURCE["game_data_version"]
    running = data.get("meta", {}).get("data_version")
    if running != recorded:
        pytest.skip(
            f"the readings in {READINGS.name} were taken from game data "
            f"{recorded}, this machine has {running}. Re-measure against the "
            f"game before trusting either side.")


def _rate_it(data: dict, weapon_id: int, build: model.Build):
    """The armament and what the facade says about it at its own rarity.

    Through `damage.candidate`, not `weapons.rate`: the facade is the only
    thing allowed to rate an armament (AD-021), so asking it here measures
    the path the arsenal tab, the weapon tile and the advisor all take.
    """
    weapon = cases.weapon_by_id(data, weapon_id)
    own_tier = weapon.get("rarity", 0) + 1
    return weapon, own_tier, damage.candidate(weapon, own_tier, build, data)


def _checked(weapon: dict, own_tier: int, rating, expected_name: str) -> None:
    """The preconditions, so a green result cannot come from another figure.

    The name pins the id against a patch that renumbers armaments; the tier
    pins the reading to the armament's own rarity, which is the state the
    sheet was read in; the absence of multipliers pins it to a bare build.
    The fourth is this file's own: the figure has to have come out of the
    catalyst branch. Without it a program that quietly went back to printing
    the physical attack rating could still pass a cell whose two figures
    happened to land on the same whole number.
    """
    assert weapon["name"] == expected_name, (
        f"armament {weapon['id']} is {weapon['name']!r} in this dataset and "
        f"was {expected_name!r} when the sheet was read")
    assert rating.tier_applied == own_tier, (
        f"{weapon['name']!r} was rated at tier {rating.tier_applied}, not at "
        f"its own {own_tier}; the reading is for an unreinforced armament")
    assert not rating.rates, (
        f"{weapon['name']!r} carries the multipliers {rating.rates}, but the "
        f"sheet was measured with no relics equipped")
    assert rating.catalyst_scaling is not None, (
        f"{weapon['name']!r} is being answered with an attack rating; the "
        f"game shows no attack rating for a staff or a seal at all")


@pytest.mark.parametrize("entry", _READINGS, ids=_IDS)
def test_the_program_shows_the_number_the_game_shows(game_data, entry):
    _same_game(game_data)
    hero = cases.hero_by_name(game_data, entry["nightfarer"])
    build = model.compute(hero, entry["level"], [],
                          game_data.get("curves", {}))
    weapon, own_tier, rating = _rate_it(game_data, entry["weapon"], build)
    _checked(weapon, own_tier, rating, entry["name"])

    assert damage.displayed(rating.final_headline) == entry["spell_scaling"], (
        f"{entry['name']!r} for {entry['nightfarer']} at level "
        f"{entry['level']}: the game shows {entry['spell_scaling']}, this "
        f"program shows {damage.displayed(rating.final_headline)} "
        f"(unrounded {rating.final_headline!r})")


@pytest.mark.parametrize("entry", _REFERENCE["readings"], ids=_REFERENCE_IDS)
def test_the_second_list_agrees_at_its_own_attribute_value(game_data, entry):
    """The independently collected list, which no Nightfarer stands behind.

    Its 28 figures are all reproduced at one attribute value, which is what
    makes it a second shape of the claim rather than a second reading of the
    first source: the same reinforce rates and the same constant explain a
    differently collected list without a further free parameter.

    The build is constructed rather than computed, because the reference is
    an attribute value and not a hero at a level -- no Nightfarer in the game
    stands at Intelligence 2. It carries no relics, so every multiplier is
    1.0 and the facade's second layer changes nothing.
    """
    _same_game(game_data)
    value = _REFERENCE["attribute_value"]
    build = model.Build(attributes={"Intelligence": value, "Faith": value},
                        base_attributes={"Intelligence": value,
                                         "Faith": value})
    weapon, own_tier, rating = _rate_it(game_data, entry["weapon"], build)
    _checked(weapon, own_tier, rating, entry["name"])

    assert damage.displayed(rating.final_headline) == entry["spell_scaling"], (
        f"{entry['name']!r} at attribute {value}: the reference list says "
        f"{entry['spell_scaling']}, this program says "
        f"{damage.displayed(rating.final_headline)} "
        f"(unrounded {rating.final_headline!r})")


def test_at_least_one_reading_tells_truncation_from_rounding(game_data):
    """Without this, replacing `floor` with `round` would go unnoticed here.

    Truncation and rounding agree on every figure whose fractional part is
    below a half, so a file of readings that all happened to land there would
    pass under either rule and say nothing about which one the game uses.
    39 of these 84 land at or above it (measured 2026-09-05); this asserts
    that at least one still does.
    """
    _same_game(game_data)
    telling = []
    for entry in _READINGS:
        hero = cases.hero_by_name(game_data, entry["nightfarer"])
        build = model.compute(hero, entry["level"], [],
                              game_data.get("curves", {}))
        _weapon, _tier, rating = _rate_it(game_data, entry["weapon"], build)
        if math.floor(rating.final_headline) != round(rating.final_headline):
            telling.append((entry["name"], rating.final_headline))

    assert telling, (
        "every reading in the file rates at a fractional part below a half, "
        "so all of them would pass with `round` in place of `math.floor` and "
        "this file could not tell the game's rule from the other one")


def test_the_ranking_agrees_with_the_game_about_two_catalysts(game_data):
    """QA-099's own case: the ranking the physical figure got backwards.

    Recluse at level 12, both staves at their own rarity. The game reads
    Carian Regal Scepter 237 and Rotten Crystal Staff 182; the physical
    attack rating reads 37.1 and 67.8 and so puts them the other way round.
    The two halves are asserted together on purpose -- that the order is
    right, and that it is right because both figures are the game's.
    """
    _same_game(game_data)
    hero = cases.hero_by_name(game_data, "Recluse")
    build = model.compute(hero, 12, [], game_data.get("curves", {}))
    ranked = damage.rank_candidates(build, weapons.MIN_UPGRADE, game_data)
    order = {rating.weapon["id"]: place
             for place, rating in enumerate(ranked)}

    scepter, rotten = 33090000, 33270000
    assert order[scepter] < order[rotten], (
        "the ranking still puts Rotten Crystal Staff ahead of Carian Regal "
        "Scepter, which is the order the physical attack rating gives and "
        "the opposite of the game's")

    by_id = {rating.weapon["id"]: rating for rating in ranked}
    assert damage.displayed(by_id[scepter].final_headline) == 237
    assert damage.displayed(by_id[rotten].final_headline) == 182


def test_only_staves_and_seals_are_answered_this_way(game_data):
    """Reading the field changes nothing for any other armament.

    T-043 counted this in the params -- 53 of 2317 rows sit on a reinforce
    group whose rate is not 1.0, and every one of them is a catalyst. This
    is the same count taken through the program: of the 1793 named armaments
    the dataset holds, exactly the 30 catalysts come back with a spell
    scaling, and every one of the other 1763 comes back with `None` and is
    rated exactly as it was before.
    """
    _same_game(game_data)
    hero = cases.hero_by_name(game_data, "Recluse")
    build = model.compute(hero, 12, [], game_data.get("curves", {}))

    catalysts, others = [], []
    for weapon in game_data["weapons"]:
        rating = damage.candidate(weapon, weapons.MIN_UPGRADE, build,
                                  game_data)
        if rating.catalyst_scaling is None:
            others.append(weapon)
            assert rating.final_headline == rating.final_total
            assert rating.shown_per_type == rating.final_per_type
            assert rating.headline_label == damage.ATTACK_RATING_LABEL
        else:
            catalysts.append(weapon)
            assert rating.final_headline == rating.catalyst_scaling
            # The whole of the App Designer's decision, in one line: the
            # physical rating a catalyst used to be shown by reaches no
            # display, headline or per-type row.
            assert rating.shown_per_type == {}
            assert rating.headline_label == damage.SPELL_POWER_LABEL
            assert model.weapon_class(weapon) == "catalyst"

    assert len(catalysts) == 30, (
        f"this dataset holds {len(catalysts)} catalysts, not the 30 the "
        f"measurement was taken over -- 20 staves and 10 seals, of which 28 "
        f"carry a figure in the sheet and two are the duplicate rows of "
        f"QA-099 a")
    assert len(others) == 1763


def test_the_readings_carry_their_provenance():
    """A number without its source is a number nobody can re-measure.

    Asserted rather than trusted to review: the header is the whole reason
    these 84 figures may be used as evidence, and a later edit that dropped a
    field would leave the file looking exactly as authoritative.
    """
    for field_name in ("what", "sheet", "read_on", "game_data_version",
                       "measured_by", "levels", "left_out",
                       "how_these_rows_were_picked",
                       "not_a_selection_of_the_hits", "name_collisions"):
        assert _SOURCE.get(field_name), (
            f"{READINGS.name} has no {field_name!r} in its source block")
    for field_name in ("what", "source", "attribute_value", "read_on"):
        assert _REFERENCE.get(field_name), (
            f"{READINGS.name} has no {field_name!r} in its reference block")

    assert len(_READINGS) == 84, (
        "the block is the sheet's 28 catalyst rows across its 3 filled "
        "columns, taken whole; changing the count is a decision with a "
        "reason, so it is written down here as well")
    assert len(_REFERENCE["readings"]) == 28
    nightfarers = {entry["nightfarer"] for entry in _READINGS}
    assert nightfarers == {"Duchess", "Revenant", "Recluse"}, (
        f"the readings cover {sorted(nightfarers)}; the sheet fills the "
        f"catalyst block for exactly these three")


def test_the_constant_is_named_once_and_is_the_measured_one():
    """The constant is a measured quantity, so its value is part of the test.

    Every case above is checked against the game through the named constant;
    this adds the one thing they cannot say, which is that the figure they
    agree on is reached through it rather than through a number written
    somewhere else. 90 is the only two-digit figure the intersection over the
    84 cells allows -- K in [89.9982, 90.0147] -- and the margin is 0.0018
    down and 0.0147 up.
    """
    assert weapons.CATALYST_DISPLAY_RATE == 90.0
    assert 89.9982 <= weapons.CATALYST_DISPLAY_RATE <= 90.0147

    # And it is not the attack rating's constant wearing another name: the
    # 0.6 was measured against a different display and does not apply here.
    assert weapons.CATALYST_DISPLAY_RATE != weapons.GAME_ATTACK_POWER_RATE
