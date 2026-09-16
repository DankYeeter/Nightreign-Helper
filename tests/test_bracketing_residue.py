"""The script that justifies a bracketing has to be the program's arithmetic.

`scripts/bracketing_residue.py` re-derives what `weapons.rate` does, because
the two brackets it compares differ only inside that function and its output
cannot be taken apart again without rounding a third time. A re-derivation can
drift from the thing it measures, and a drifted one would report a number
about a calculation nobody ships -- which is the failure QA-115 found in the
figure it replaces: a script that was never committed, quoted in the source as
though it could be re-run.

So the script checks itself against `weapons.rate` on every figure, and this
file checks that the check is real. It caught something on the first run:
folding `influence / 100` into the product below it is a different bracketing
and lands a last bit away, which is the whole quantity being counted.
"""

from __future__ import annotations

import math

import pytest

from nrplanner import weapons

from scripts import bracketing_residue as residue

#: Every 300th armament. The claim under test is about arithmetic, not about
#: coverage: it either holds for a figure or it does not, and the full sweep
#: is the script's own job rather than the suite's.
STEP = 300


def test_two_adjacent_doubles_are_one_last_bit_apart():
    """The unit the counts are in, checked where it is unambiguous."""
    one = 1.0
    next_one = math.nextafter(one, math.inf)

    assert residue.ulps_apart(one, one) == 0
    assert residue.ulps_apart(one, next_one) == 1
    assert residue.ulps_apart(one, math.nextafter(next_one, math.inf)) == 2
    assert residue.ulps_apart(-0.0, 0.0) == 0, (
        "a signed zero would count as a gap of its own and put every "
        "unscaled figure in the wrong bucket")


def test_the_script_forms_the_figure_weapons_rate_forms(game_data):
    """The guard the script's whole answer rests on, exercised.

    Held here as well as inside the script so that a refactoring of
    `weapons.rate` fails a test run rather than waiting for somebody to
    remember to re-run a tool -- the same reason the mutation anchors are held
    in `test_differential_track.py`.
    """
    measured = residue.measure(game_data, STEP)

    assert measured["per_type_figures"] > 0, "nothing was measured"
    assert measured["disagreed_with_weapons_rate"] == 0, (
        f"{measured['disagreed_with_weapons_rate']} of "
        f"{measured['per_type_figures']} figures the script forms are not "
        f"the ones weapons.rate forms, so its counts describe a third "
        f"calculation")


def test_the_shipped_bracket_is_exactly_the_old_figure_times_the_factor(
        game_data):
    """The claim the comment in `weapons.rate` makes, at sample size.

    Not "within one last bit" but **equal**: `fl(fl(base * bonus) * K)` is
    `fl(old * K)` by construction, and that is the property the bracketing
    was chosen for. The other bracket is measured against the same yardstick
    and does not have it.
    """
    measured = residue.measure(game_data, STEP)

    assert set(measured["per_type"]["shipped"]) == {0}, (
        f"a shipped figure is not exactly fl(old x K): "
        f"{measured['per_type']['shipped']}")
    assert max(measured["per_type"]["on_the_base"]) >= 1, (
        "the other bracket lands on the same figure everywhere in this "
        "sample, so the sample cannot tell the two apart and the comparison "
        "says nothing")


def test_a_subsample_says_that_it_is_one():
    """A count taken at a step cannot be quoted as the whole one."""
    with pytest.raises(SystemExit):
        residue.main(["--step", "0"])
    assert residue.TIERS == tuple(
        range(weapons.MIN_UPGRADE, weapons.MAX_UPGRADE + 1)), (
        "the script sweeps the tiers the reinforce table has rows for; a "
        "hand-written range here would stop following that table")
