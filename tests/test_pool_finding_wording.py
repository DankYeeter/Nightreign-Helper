"""The sentences a pool reports itself with, word for word (AK-67).

`SlotPool.unknowns` is read straight onto the screen -- `UI_SPEC.md` §3.2
line 3b shows each string verbatim -- so the wording is a decision of the
`ui-ux-designer` and not of this module. The Nachtrag of 2026-09-05 settles
two of the three lines this field can carry, and both are pinned here
literally: a paraphrase would pass a test written on "does it mention the
colour" while showing the player something nobody chose.

The third, the conversion line (QA-113), reached the code in T-048 wearing a
`[wording pending: QA-113]` marker, because the decision of that morning
settled the other two and named neither it nor its subject. The Nachtrag of
the same day settled it too and lifted the field's ceiling from two sentences
to three, so all three are pinned literally here and the marker is gone.
"""

from __future__ import annotations

import dataclasses

import pytest

from nrplanner import model
from nrplanner.advisor import candidates, goals, types

from tests import advisor_cases as advisor
from tests import weapon_damage_cases as cases

DAMAGE = "max_damage"

HANDLE_SINGULAR_COLOURED = (
    "1 owned relic of this colour is not offered: this save carries no "
    "handle for it, so one copy cannot be told from another and a suggestion "
    "naming one could not be applied to a slot.")
HANDLE_PLURAL_COLOURED = (
    "2 owned relics of this colour are not offered: this save carries no "
    "handle for them, so one copy cannot be told from another and a "
    "suggestion naming one could not be applied to a slot.")
HANDLE_SINGULAR_WHITE = (
    "1 owned relic of any colour is not offered: this save carries no "
    "handle for it, so one copy cannot be told from another and a suggestion "
    "naming one could not be applied to a slot.")

CONDITIONAL_SINGULAR = (
    "1 of your relics carries an effect that only applies under a condition. "
    "It was not counted.")
CONDITIONAL_PLURAL = (
    "2 of your relics carry effects that only apply under a condition. They "
    "were not counted.")

CONVERSION_SINGULAR = (
    "1 of your relics changes what damage type your starting armament deals "
    "(to magic, fire, lightning, or holy). This figure does not count that "
    "change.")
CONVERSION_PLURAL = (
    "2 of your relics change what damage type your starting armament deals "
    "(to magic, fire, lightning, or holy). This figure does not count that "
    "change.")


@pytest.fixture(scope="module")
def wylder(game_data):
    return cases.hero_by_name(game_data, "Wylder")


def pool_for(inventory, problem, slot_index, ctx):
    return candidates.pool(inventory, problem, slot_index, ctx, goals.GOALS,
                           DAMAGE)


def handle_lines(pool) -> list[str]:
    return [line for line in pool.unknowns if "handle" in line]


# -- the handle line (QA-108) ----------------------------------------------

@pytest.mark.parametrize("handles, expected", [
    ([10, None, 12], HANDLE_SINGULAR_COLOURED),
    ([None, None, 12], HANDLE_PLURAL_COLOURED),
])
def test_the_handle_line_at_a_coloured_slot(game_data, wylder, handles,
                                            expected):
    """Singular and plural, and the reach named as "this colour"."""
    inventory = advisor.make_inventory(game_data, wylder, colour=advisor.RED,
                                       count=3, handles=handles)
    ctx = advisor.context(game_data, wylder)

    pool = pool_for(inventory, advisor.problem([advisor.RED]), 0, ctx)

    assert handle_lines(pool) == [expected]


def test_the_handle_line_at_a_white_slot_names_every_colour(game_data,
                                                            wylder):
    """QA-108: "of this colour" is a claim a white slot cannot make.

    `inventory.relics_for` offers a white slot relics of every colour, so the
    copy that falls through the handle gap here is **blue** while the slot is
    white and the rest of the stock is red. The old wording would have called
    that copy "of this colour", of a slot that has none. The count was never
    wrong -- it always summed over what the slot really offers -- and neither
    is it moved by this: it is the description of the counted set that
    changes.
    """
    inventory = advisor.make_inventory(game_data, wylder, colour=advisor.RED,
                                       count=2, handles=[10, 11],
                                       other_colour=advisor.BLUE)
    stranger = inventory.relics[-1]
    assert stranger.colour == advisor.BLUE, (
        "the copy this case makes handle-less is not the one of the second "
        "colour, so it would prove nothing about a white slot's reach")
    inventory.relics[-1] = dataclasses.replace(stranger, handle=None)

    ctx = advisor.context(game_data, wylder)
    white = pool_for(inventory, advisor.problem([advisor.WHITE]), 0, ctx)
    coloured = pool_for(inventory, advisor.problem([advisor.RED]), 0, ctx)

    assert handle_lines(white) == [HANDLE_SINGULAR_WHITE]
    assert handle_lines(coloured) == [], (
        "the red slot never offered the blue copy, so it has nothing to "
        "report about it -- and a case where both slots say the same thing "
        "could not tell the two wordings apart")
    assert advisor.WHITE == model.WHITE_SLOT, (
        "these cases and the code disagree about which slot colour is the "
        "wildcard")


# -- the conditional line (OF-20, D2) --------------------------------------

@pytest.mark.parametrize("count, expected", [
    (1, CONDITIONAL_SINGULAR),
    (2, CONDITIONAL_PLURAL),
])
def test_the_conditional_line_word_for_word(game_data, wylder, count,
                                            expected):
    """AK-67's wording, and no marker in front of it any more.

    The sentence says "your relics" although the count is over the candidates
    of this pool. That is the `ui-ux-designer`'s decision with both halves in
    view (AK-67), not a slip, and it is pinned here so that nobody quietly
    reconciles the two in one direction or the other.
    """
    gated = advisor.a_declarable_effect(game_data, wylder)
    plain = advisor.raising_effects(game_data, wylder, 1)[0]
    rolls = [[gated]] * count + [plain] * (3 - count)
    inventory = advisor.make_inventory(game_data, wylder, count=3,
                                       rolls=rolls)
    ctx = advisor.context(game_data, wylder)

    pool = pool_for(inventory, advisor.problem([advisor.RED]), 0, ctx)
    lines = [line for line in pool.unknowns if "condition" in line]

    assert lines == [expected]
    assert "wording pending" not in lines[0], (
        "the settled sentence still carries a stand-in marker")


def test_the_handle_line_comes_before_the_conditional_one(game_data, wylder):
    """AK-67 fixes the order: never counted, then counted and zeroed."""
    gated = advisor.a_declarable_effect(game_data, wylder)
    inventory = advisor.make_inventory(game_data, wylder, count=2,
                                       handles=[None, 11],
                                       rolls=[[gated], [gated]])
    ctx = advisor.context(game_data, wylder)

    pool = pool_for(inventory, advisor.problem([advisor.RED]), 0, ctx)

    assert len(pool.unknowns) == 2, (
        f"this pool leaves out a copy for each of the two settled reasons, "
        f"so it reports two lines: {pool.unknowns!r}")
    assert pool.unknowns[0] == HANDLE_SINGULAR_COLOURED
    assert pool.unknowns[1] == CONDITIONAL_SINGULAR


# -- the conversion line (QA-113), settled the same day ---------------------

@pytest.mark.parametrize("count, expected", [
    (1, CONVERSION_SINGULAR),
    (2, CONVERSION_PLURAL),
])
def test_the_conversion_line_word_for_word(game_data, wylder, count,
                                           expected):
    """AK-67's third sentence, and no marker in front of it any more.

    The case this replaces was written to fail on the day the wording was
    decided -- "the marker has to be removed deliberately, not survive because
    nothing was watching". The Nachtrag of 2026-09-05 decided it, so what the
    marker was standing in for is now what is pinned.

    The four elements are named in the sentence because QA-113 is a closed set
    of four relics. No size and no direction: the sentence says the figure
    does not count the change and claims nothing about how large it would be,
    which is the only true thing anyone can say until it is read in the
    running game.
    """
    converting = advisor.a_damage_type_conversion(game_data)
    plain = advisor.raising_effects(game_data, wylder, 1)[0]
    rolls = [[converting]] * count + [plain] * (3 - count)
    inventory = advisor.make_inventory(game_data, wylder, count=3,
                                       rolls=rolls)
    ctx = advisor.context(game_data, wylder)

    pool = pool_for(inventory, advisor.problem([advisor.RED]), 0, ctx)
    lines = [line for line in pool.unknowns if "damage type" in line]

    assert lines == [expected]
    assert "wording pending" not in lines[0], (
        "the settled sentence still carries a stand-in marker")
    assert not hasattr(candidates, "WORDING_PENDING"), (
        "the module still holds a stand-in marker constant, and every line "
        "of this field is decided -- a marker with nothing to mark is how "
        "one gets put back in front of settled text")
