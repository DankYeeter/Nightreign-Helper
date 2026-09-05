"""The field behind a catalyst's figure arrives, or the extraction stops.

QA-099 c. The spell scaling of every staff and seal in the game hangs on one
field of `ReinforceParamWeapon` that the Paramdex has no name for: it is read
as `unknown_1`, which is a placeholder, and a Paramdex update that gives it
its real name is an ordinary event. Written the way the rest of that block is
written -- `row.values.get(name, 1.0)` -- such an update would hand back 1.0
for every row, all 28 catalysts would quietly collapse onto the same figure
of 90, and nothing anywhere would say the data had stopped arriving. A wrong
number that looks like a right one is the failure this project keeps having,
so the field is required rather than defaulted.

Built on stub tables rather than on the installed game, deliberately: the
cases are about what happens when the data is **not** what it is today, and
the real regulation cannot be asked to be missing a field. The case that the
real data does satisfy the guard is in
`test_catalyst_scaling_against_the_game.py`, which reads it through the
snapshot.

**Its killing mutation**, registered in `scripts/differential/mutate.py`:
`catalyst-scaling-field-renamed` -- `extract.CATALYST_SCALING_FIELD` to a
name the paramdef does not carry, which is exactly the Paramdex update this
guards against, only from the other side. `test_a_well_formed_table_hands_
back_every_rate` below is what fails under it.

That works because `PARAMDEX_NAME` is **written out here** rather than read
off the code under test. A stub built from `extract.CATALYST_SCALING_FIELD`
agrees with whatever the extractor happens to be looking for, so it would
pass while the extractor read a field the game data does not have -- which
is the whole failure. The literal is the fact about the data; the constant
is the claim about it, and the two are held against each other.

Measured on 2026-09-05: 3 of the 4 cases here fail under that mutation. The
one that stays green is `test_a_table_without_the_field_is_refused` -- and
that is the point of naming which case dies. A guard that only ever refuses
is satisfied by refusing everything, so a file holding the refusal cases
alone would report the extractor reading a field the game does not have as
a clean run.
"""

from __future__ import annotations

import pytest

from nrdata import extract, param

#: What the Paramdex calls the field at offset 128 of a ReinforceParamWeapon
#: row today (`vendor/Paramdex/NR/Defs/ReinforceParamWeapon.xml`). Written
#: out rather than imported: see the module docstring.
PARAMDEX_NAME = "unknown_1"

#: A name the paramdef does not carry, for the refusal case. Deliberately
#: the sort of name a Paramdex update would give this field, so the case
#: reads as the event it stands for.
RENAMED = "spellScalingRate"


def table(rates: dict[int, float], *,
          field_name: str = PARAMDEX_NAME) -> param.ParamTable:
    """A ReinforceParamWeapon-shaped table carrying only what is read here.

    The rows hold one further field, so a row that is missing the catalyst
    one is still a row with values on it -- otherwise "the field is absent"
    and "the row is empty" would be the same state and the guard could pass
    by noticing the wrong one.
    """
    return param.ParamTable(
        param_type="REINFORCE_PARAM_WEAPON",
        data_version=1,
        row_size=132,
        rows=[param.ParamRow(id=row_id, name="",
                             values={"physicsAtkRate": 1.0,
                                     field_name: value})
              for row_id, value in rates.items()],
    )


def test_a_well_formed_table_hands_back_every_rate():
    """Every row, keyed by its own id, and the values unchanged.

    The rows that read 1.0 are in the result as well: which reinforce groups
    belong to a catalyst is not this table's to decide -- the armament says
    it -- and a function that dropped them would leave `weapons.rate` unable
    to tell "no rate for this group" from "a rate of exactly 1.0", which is
    the distinction the whole guard is about.
    """
    rates = extract.catalyst_scaling_rates(
        table({3000: 1.0, 3400: 1.5675, 4800: 0.85}))

    assert rates == {3000: 1.0, 3400: 1.5675, 4800: 0.85}


def test_a_table_without_the_field_is_refused():
    """The Paramdex update this exists for: the field under another name."""
    with pytest.raises(ValueError) as refused:
        extract.catalyst_scaling_rates(
            table({3000: 1.0, 3400: 1.5675}, field_name=RENAMED))

    message = str(refused.value)
    assert extract.CATALYST_SCALING_FIELD in message, (
        "the refusal does not name the field that is missing, so the reader "
        "cannot find out what to look for at offset 128")
    assert "CATALYST_SCALING_FIELD" in message, (
        "the refusal does not say where to put the new name, which is the "
        "one thing whoever hits this has to do")


def test_a_table_that_never_moves_is_refused():
    """A field read at the wrong offset can exist and still say nothing.

    Padding, a flag or a reserved word reads as a constant, and a constant
    passes the "is the field there" check unremarked while making every
    catalyst identical. Two checks, because either alone is satisfied by a
    dataset that says nothing.
    """
    with pytest.raises(ValueError) as refused:
        extract.catalyst_scaling_rates(table({3000: 1.0, 3400: 1.0}))

    assert "1.0" in str(refused.value)


def test_one_row_that_moves_is_enough():
    """The threshold is one, and it is not the count the game happens to hold.

    The shipped data holds 97 rows with a rate other than 1.0, and that
    number is written down beside the check so the margin can be seen -- but
    a patch that retires catalysts is a game change and not a broken
    extractor. A guard that failed on it would be read as noise and switched
    off, which is worth more than the sharpness it would buy.
    """
    rates = extract.catalyst_scaling_rates(
        table({3000: 1.0, 3100: 1.0, 3400: 1.5675}))

    assert rates[3400] == 1.5675
    assert extract.CATALYST_SCALING_ROWS_TODAY == 97
