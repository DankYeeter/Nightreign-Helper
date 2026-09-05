"""The sentences a pool reports itself with, word for word (AK-67).

`SlotPool.unknowns` is read straight onto the screen -- `UI_SPEC.md` §3.2
line 3b shows each string verbatim -- so the wording is a decision of the
`ui-ux-designer` and not of this module. The Nachtrag of 2026-09-05 settles
two of the three lines this field can carry, and both are pinned here
literally: a paraphrase would pass a test written on "does it mention the
colour" while showing the player something nobody chose.

The one that is **not** settled is the conversion line (QA-113). It reached
the code in T-048, after the two sentences above were drafted, and the
decision names neither it nor its subject -- it says the field carries at
most two sentences, and the field carries three. So it goes on wearing the
marker that says its text is a stand-in, and the case at the bottom of this
file is what keeps a stand-in from being shipped as though it were decided.
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
    assert candidates.WORDING_PENDING not in lines[0], (
        "the settled sentence still carries the stand-in marker")


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


# -- the line whose wording is still open ----------------------------------

def test_an_undecided_line_says_so_on_its_face(game_data, wylder):
    """The conversion line is a stand-in and has to look like one.

    AK-67 settled the other two sentences of this field and states that it
    carries at most two; the conversion line (QA-113) is a third, drafted by
    the `developer` in T-048 and named in no wording decision. Until one names
    it, the marker in front of it is what keeps a placeholder from being read
    as finished text -- by a player if the picker is built, and by the next
    reader of this module either way.

    This case is meant to fail the day the wording is decided. That is what
    it is for: the marker has to be removed deliberately, not survive because
    nothing was watching.
    """
    converting = advisor.a_damage_type_conversion(game_data)
    inventory = advisor.make_inventory(game_data, wylder, count=1,
                                       rolls=[[converting]])
    ctx = advisor.context(game_data, wylder)

    pool = pool_for(inventory, advisor.problem([advisor.RED]), 0, ctx)
    lines = [line for line in pool.unknowns if "convert" in line]

    assert len(lines) == 1, (
        f"one relic converts, so one line: {pool.unknowns!r}")
    assert lines[0].startswith(candidates.WORDING_PENDING), (
        f"the conversion line reads as decided text and is not: "
        f"{lines[0]!r}")
    assert "QA-113" in candidates.WORDING_PENDING, (
        "the marker no longer says which decision is missing, which is the "
        "only thing that makes it actionable")
