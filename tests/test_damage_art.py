"""Asking the facade about one kind of attack, and what that multiplies.

`ARCHITECTURE.md` AD-045 to AD-049 (assurance M3), `UI_SPEC.md` AK-327 ff.

`damage.equipped(..., art=...)` asks the same question as always under one
condition: count only the buffs that reach Weapon Arts, or sorceries, or one
spell school. Those buffs sit outside every figure the program shows (QA-018
decided that, `test_move_scoped_effects.py` holds it) -- under an art they
are exactly what is being asked about, and they reach the figure through the
same loop the ordinary rates go through.

What is asserted here is the arithmetic of that condition, not the mapping
behind it (`test_move_scoped_effects.py`) and not the ranking in front of it
(`test_advisor_goals.py`):

* the factor lands, and only under the art it belongs to;
* a buff two scope fields name is counted once, not squared;
* `Question.BARE` carries no multipliers and so is the same under every art;
* the second hand carries the same factor as the first;
* under a school the general incantation buff counts too (OF-51).

Every effect is named by id, and every factor is read off the dataset rather
than written down here: the ids are the production constant under test, the
numbers behind them are the game's and move with a patch.
"""

from __future__ import annotations

import pytest

from nrplanner import damage, model, weaponslots

from tests import weapon_damage_cases as cases

LEVEL = 15
TIER = 1

#: "Improved Skill Attack Power", the strongest step: all five element rates
#: at 1.21, scope 112 with 111 beside it. The art it belongs to is `skill`.
SKILL_BUFF = 8350002

#: "Improved Charged Spells & Skills": scope 110 **and** 111, so it belongs
#: to `family:110` and to `skill`. The case the set semantics of
#: `model.attack_arts_of` exists for -- counted once per art, never squared.
TWO_SCOPE_BUFF = 330900

#: "Improved Bestial Incantations", scope 23, and "Improved Incantations",
#: which carries no scope at all and lives in `MOVE_SCOPED_ARTS`. Under
#: `family:23` both count, multiplied (user decision OF-51, 2026-09-19).
SCHOOL_BUFF = 7044400
GENUS_BUFF = 8330100

#: A school of the other genus. The incantation buff must not reach it.
SORCERY_SCHOOL_ART = f"{model.ART_FAMILY_PREFIX}2"
BESTIAL_ART = f"{model.ART_FAMILY_PREFIX}23"
CHARGED_ART = f"{model.ART_FAMILY_PREFIX}110"


@pytest.fixture(scope="module")
def hero(game_data):
    """Wylder, whose starting armament is the greatsword AD-038 ranks on."""
    return cases.hero_by_name(game_data, "Wylder")


@pytest.fixture(scope="module")
def slot(game_data, hero):
    """The Nightfarer's own armament in slot 1, the advisor's question."""
    weapon = cases.weapon_by_id(game_data, hero["starting_weapon"])
    return weaponslots.WeaponSlot(weapon=weapon, tier=TIER)


def rate_of(game_data, effect_id: int) -> float:
    """What the dataset says this buff multiplies by."""
    modifiers = cases.effect_by_id(game_data, effect_id)["modifiers"] or {}
    given = [float(modifiers[f]) for f in model.ELEMENT_ATTACK_RATES
             if f in modifiers]
    assert given and max(given) > 1.0, (
        f"{effect_id} raises no attack rate in this dataset, so it cannot "
        f"show whether an art reaches the figure")
    return max(given)


def build_with(game_data, hero, effect_ids) -> model.Build:
    """A build carrying exactly these effects and nothing else."""
    effects = [cases.effect_by_id(game_data, i) for i in effect_ids]
    return model.compute(hero, LEVEL, effects, game_data.get("curves", {}))


def figures(game_data, hero, slot, build,
            art: str | None = None) -> tuple[float, float]:
    """The bare and the real headline for this slot under this art."""
    bare, real = damage.equipped(slot, 0, build, hero, game_data, art=art)
    return bare.final_headline, real.final_headline


def test_the_art_factor_reaches_the_figure_and_no_other_art_does(
        game_data, hero, slot):
    """A skill buff counts under `skill`, and under nothing else.

    Without an art the figure is bit-for-bit the one the program has always
    shown, which is AD-047 point 1: the buff is scoped out of an ordinary
    swing and stays out. Under `sorceries` it is equally absent -- asking
    about the wrong kind of attack must not hand over somebody else's buff.
    """
    build = build_with(game_data, hero, [SKILL_BUFF])
    factor = rate_of(game_data, SKILL_BUFF)
    _, plain = figures(game_data, hero, slot, build)

    _, under_skill = figures(game_data, hero, slot, build, model.SKILL_ART)
    assert under_skill == pytest.approx(plain * factor), (
        f"{SKILL_BUFF} did not reach the figure under its own art: "
        f"{plain} -> {under_skill}, expected {plain * factor}")

    for other in (None, model.SORCERIES_ART, SORCERY_SCHOOL_ART):
        _, under_other = figures(game_data, hero, slot, build, other)
        assert under_other == plain, (
            f"{SKILL_BUFF} moved the figure under {other!r}, where it covers "
            f"nothing: {plain} -> {under_other}")


def test_a_buff_two_scope_fields_name_counts_once(game_data, hero, slot):
    """Scope 110 and 111 on one effect are one buff, not two.

    Squaring it is the very mistake the scoped line was built against: 1.18
    twice is 1.3924, and the player holds one relic. It has to be the same
    single factor under both of the arts it belongs to.
    """
    build = build_with(game_data, hero, [TWO_SCOPE_BUFF])
    factor = rate_of(game_data, TWO_SCOPE_BUFF)
    _, plain = figures(game_data, hero, slot, build)

    for art in (model.SKILL_ART, CHARGED_ART):
        _, under_art = figures(game_data, hero, slot, build, art)
        assert under_art == pytest.approx(plain * factor), (
            f"under {art!r} {TWO_SCOPE_BUFF} counts as "
            f"{under_art / plain if plain else 0}, and it is worth {factor}")
        assert under_art != pytest.approx(plain * factor * factor), (
            f"under {art!r} the two scope fields of {TWO_SCOPE_BUFF} were "
            f"multiplied in one after the other")


def test_the_bare_figure_is_the_same_under_every_art(game_data, hero, slot):
    """`Question.BARE` has no multiplier layer, so an art cannot move it.

    It is the comparison figure the tile shows beside the real one, and a
    comparison that moved with the question would compare nothing.
    """
    build = build_with(game_data, hero, [SKILL_BUFF])
    plain, _ = figures(game_data, hero, slot, build)

    for art in (model.SKILL_ART, model.INCANTATIONS_ART, BESTIAL_ART):
        bare, _ = figures(game_data, hero, slot, build, art)
        assert bare == plain, (
            f"the bare figure moved from {plain} to {bare} under {art!r}")


def test_both_hands_carry_the_same_art_factor(game_data, hero, slot):
    """The two-handed answer is the same question, so it takes the factor.

    `_rate` builds both hands from one pair of weapon ratings and hands the
    art to each; a two-handed figure without it would say that holding the
    armament differently changes which buffs the player owns.
    """
    build = build_with(game_data, hero, [SKILL_BUFF])
    factor = rate_of(game_data, SKILL_BUFF)

    _, plain = damage.equipped(slot, 0, build, hero, game_data)
    _, under_skill = damage.equipped(slot, 0, build, hero, game_data,
                                     art=model.SKILL_ART)
    assert plain.two_handed is not None, (
        f"{slot.weapon['name']!r} has no two-handed figure, so this case "
        f"cannot show one")
    assert under_skill.two_handed.final_headline == pytest.approx(
        plain.two_handed.final_headline * factor)


def test_a_school_counts_the_general_buff_of_its_own_genus_too(
        game_data, hero, slot):
    """Bestial is an incantation school, so "Improved Incantations" counts.

    The two multiply: a Bestial incantation is buffed by both relics at once
    (OF-51, user decision 2026-09-19). Which genus a school belongs to is
    read off the game's own spells, so the sorcery school beside it gets
    neither -- that is the half of the claim that makes it a claim.
    """
    build = build_with(game_data, hero, [SCHOOL_BUFF, GENUS_BUFF])
    school = rate_of(game_data, SCHOOL_BUFF)
    genus = rate_of(game_data, GENUS_BUFF)
    _, plain = figures(game_data, hero, slot, build)

    _, under_school = figures(game_data, hero, slot, build, BESTIAL_ART)
    assert under_school == pytest.approx(plain * school * genus), (
        f"under {BESTIAL_ART!r} the school buff and the incantation buff do "
        f"not both count: {plain} -> {under_school}")

    _, under_sorcery = figures(game_data, hero, slot, build,
                               SORCERY_SCHOOL_ART)
    assert under_sorcery == plain, (
        f"an incantation buff reached {SORCERY_SCHOOL_ART!r}, which is a "
        f"sorcery school: {plain} -> {under_sorcery}")

    _, under_genus = figures(game_data, hero, slot, build,
                             model.INCANTATIONS_ART)
    assert under_genus == pytest.approx(plain * genus), (
        f"under {model.INCANTATIONS_ART!r} the school buff counted as well, "
        f"and a Bestial relic does not raise every incantation")
