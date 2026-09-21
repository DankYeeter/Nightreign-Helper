"""What `damage.spell` hits for, and what deliberately never reaches it.

`ARCHITECTURE.md` AD-053, the combination table's three spell rows, and the
research it stands on (`docs/research/R-010.md` section 7).

The figure is a product of four factors and every one of them is read off the
dataset here rather than written down: the spell's base damage, the
catalyst's spell scaling, the relic rates, the art factor. What is asserted
is the *shape* of the product -- which factors are in it, how often each
counts, and which four are kept out (AD-053 point 4) -- because the product
itself is uncalibrated (OF-54) and there is nothing on any screen of the game
to compare it with.

The two anchors are the two Nightfarers A26 exists for: Revenant, whose seal
casts an incantation that damages nothing until a relic swaps it, and
Recluse, whose staff casts a sorcery that does.
"""

from __future__ import annotations

import pytest

from nrplanner import damage, model

from tests import weapon_damage_cases as cases

LEVEL = 15
TIER = 1

#: Revenant's left hand and the incantation a Tauschrelikt puts in it
#: (AD-050.4): 362 Physics, school Bestial, genus Incantations.
FINGER_SEAL = 34750000
BEAST_CLAW = 6820
#: The Finger Seal's own first spell, which heals and damages nothing.
REJECTION = 6400

#: Recluse's staff and its own first spell: 152 Magic, school General.
RECLUSE_STAFF = 33750000
GLINTSTONE_PEBBLE = 4000

#: "Improved Bestial Incantations" (scope 23) and "Improved Incantations",
#: the same pair `test_damage_art.py` uses on the weapon side -- here they
#: have to reach the spell instead of the swing.
SCHOOL_BUFF = 7044400
GENUS_BUFF = 8330100

BESTIAL_ART = f"{model.ART_FAMILY_PREFIX}23"
#: Dragon Cult: an incantation school Beast Claw does not belong to.
OTHER_SCHOOL_ART = f"{model.ART_FAMILY_PREFIX}22"


def spell_by_id(data: dict, spell_id: int) -> dict:
    for row in data["spells"]:
        if row["id"] == spell_id:
            return row
    raise LookupError(f"no spell with id {spell_id} in this dataset")


@pytest.fixture(scope="module")
def revenant(game_data):
    return cases.hero_by_name(game_data, "Revenant")


@pytest.fixture(scope="module")
def seal(game_data):
    return cases.weapon_by_id(game_data, FINGER_SEAL)


@pytest.fixture(scope="module")
def beast_claw(game_data):
    return spell_by_id(game_data, BEAST_CLAW)


def build_with(game_data, hero, effect_ids=()) -> model.Build:
    effects = [cases.effect_by_id(game_data, i) for i in effect_ids]
    return model.compute(hero, LEVEL, effects, game_data.get("curves", {}))


def rate_of(game_data, effect_id: int) -> float:
    """What the dataset says this buff multiplies by."""
    modifiers = cases.effect_by_id(game_data, effect_id)["modifiers"] or {}
    given = [float(modifiers[f]) for f in model.ELEMENT_ATTACK_RATES
             if f in modifiers]
    assert given and max(given) > 1.0, (
        f"{effect_id} raises no attack rate in this dataset, so it cannot "
        f"show whether it reaches a spell")
    return max(given)


def test_the_figure_is_the_base_damage_times_the_spell_power(
        game_data, revenant, seal, beast_claw):
    """Beast Claw at the Finger Seal: 362 Physics x spell power / 100.

    The whole of AD-053 point 1 with every rate at 1.0, and the one case
    that shows *which* spell power: the seal's, on the build's attributes,
    so the figure moves with Faith through the same curve the staff's
    display does.
    """
    build = build_with(game_data, revenant)
    rated = damage.spell(beast_claw, seal, TIER, build, game_data,
                         hit_with=model.INCANTATIONS_ART)

    base = beast_claw["damage"]["Physics"]
    assert rated.spell_power > 0, (
        f"{seal['name']!r} handed back no spell scaling, so nothing below "
        f"says anything")
    assert rated.per_type == {
        "Physics": pytest.approx(base * rated.spell_power / 100.0)}
    assert rated.figure == pytest.approx(base * rated.spell_power / 100.0)
    assert rated.reason is None


def test_a_sorcery_at_a_staff_is_rated_the_same_way(game_data):
    """Recluse's own pairing, so the case is not one Nightfarer's alone."""
    hero = cases.hero_by_name(game_data, "Recluse")
    staff = cases.weapon_by_id(game_data, RECLUSE_STAFF)
    pebble = spell_by_id(game_data, GLINTSTONE_PEBBLE)
    build = build_with(game_data, hero)

    rated = damage.spell(pebble, staff, TIER, build, game_data,
                         hit_with=model.SORCERIES_ART)

    assert rated.figure == pytest.approx(
        pebble["damage"]["Magic"] * rated.spell_power / 100.0)
    assert set(rated.per_type) == {"Magic"}


def test_a_damage_type_the_spell_does_not_deal_is_zero(
        game_data, revenant, seal, beast_claw):
    """Beast Claw under Fire is 0.00, and under Physical it is the whole of it.

    Not a special case and not a blank: a ranking in which every candidate
    that brings some fire stands above this one (combination table).
    """
    build = build_with(game_data, revenant)

    def figure(damage_type: str) -> float:
        return damage.spell(beast_claw, seal, TIER, build, game_data,
                            hit_with=model.INCANTATIONS_ART,
                            damage_type=damage_type).figure

    assert figure("Fire") == 0.0
    assert figure("Physics") == figure("")


def test_a_spell_without_damage_is_zero_and_says_why(
        game_data, revenant, seal):
    """Rejection: the Finger Seal's own spell, and Revenant's default state.

    The zero is the answer, not a failure -- what has to come with it is the
    sentence, because "0.00" alone reads as a broken calculation rather than
    as "this equipment casts nothing that hurts" (combination table, the
    empty cells).
    """
    build = build_with(game_data, revenant)
    rejection = spell_by_id(game_data, REJECTION)
    assert "damage" not in rejection, (
        f"{rejection['name']!r} carries damage in this dataset, so it can no "
        f"longer stand for the spell that has none")

    rated = damage.spell(rejection, seal, TIER, build, game_data,
                         hit_with=model.INCANTATIONS_ART)

    assert rated.figure == 0
    assert rated.per_type == {}
    assert rated.reason and rejection["name"] in rated.reason


def test_the_school_and_the_genus_buff_both_count_and_each_once(
        game_data, revenant, seal, beast_claw):
    """Beast Claw is a Bestial incantation, so both relics reach it (OF-51).

    And the half that makes it a claim: under Dragon Cult -- an incantation
    school this spell does not belong to -- the school's own factor falls
    away and the general incantation buff stays, which is the combination
    table's rule for a school the reference spell is not in.
    """
    build = build_with(game_data, revenant, [SCHOOL_BUFF, GENUS_BUFF])
    school = rate_of(game_data, SCHOOL_BUFF)
    genus = rate_of(game_data, GENUS_BUFF)
    plain = damage.spell(beast_claw, seal, TIER, build, game_data,
                         hit_with="").figure

    under_school = damage.spell(beast_claw, seal, TIER, build, game_data,
                                hit_with=BESTIAL_ART,
                                damage_type="Physics").figure
    assert under_school == pytest.approx(plain * school * genus)

    under_genus = damage.spell(beast_claw, seal, TIER, build, game_data,
                               hit_with=model.INCANTATIONS_ART).figure
    assert under_genus == pytest.approx(plain * genus), (
        f"under {model.INCANTATIONS_ART!r} the Bestial buff counted too, and "
        f"it raises Bestial incantations rather than every incantation")

    under_other = damage.spell(beast_claw, seal, TIER, build, game_data,
                               hit_with=OTHER_SCHOOL_ART).figure
    assert under_other == pytest.approx(plain * genus), (
        f"under {OTHER_SCHOOL_ART!r} Beast Claw was rated as a member of a "
        f"school it does not belong to")


def test_an_element_rate_reaches_the_spell_and_a_class_rate_does_not(
        game_data, revenant, seal, beast_claw):
    """The premise of A26 and the first of AD-053 point 4's four omissions.

    A relic that lifts physical attack lifts a physical spell -- the general
    `*AttackRate` fields are what the combination table marks "ja, je Typ"
    for every row. "Improved Melee Attack Power" does not: a spell is no
    swing of a weapon class, and the bucket it sits in is never handed to
    the loop at all.
    """
    build = build_with(game_data, revenant)
    plain = damage.spell(beast_claw, seal, TIER, build, game_data,
                         hit_with=model.INCANTATIONS_ART).figure

    element = cases.effects_raising_rate(game_data, revenant,
                                         "physicsAttackRate")[0]
    with_element = build_with(game_data, revenant, [element])
    rated = damage.spell(beast_claw, seal, TIER, with_element, game_data,
                         hit_with=model.INCANTATIONS_ART)
    factor = with_element.rates["physicsAttackRate"]
    assert factor > 1.0
    assert rated.figure == pytest.approx(plain * factor)
    assert rated.rates.get("physicsAttackRate") == pytest.approx(factor)

    melee = cases.scoped_effect(game_data, revenant, "melee")
    with_melee = build_with(game_data, revenant, [melee])
    assert damage.spell(beast_claw, seal, TIER, with_melee, game_data,
                        hit_with=model.INCANTATIONS_ART).figure == plain


def test_an_armament_that_is_no_catalyst_is_refused_loudly(
        game_data, revenant, beast_claw):
    """A sword casts nothing, and a 0.00 would hide the caller's mistake.

    The reference object for a spell question is the starting catalyst
    (AD-052); anything else here is a wrong pick rather than a weak build.
    """
    sword = cases.weapon_by_id(game_data, revenant["starting_weapon"])
    build = build_with(game_data, revenant)

    with pytest.raises(ValueError, match="no catalyst"):
        damage.spell(beast_claw, sword, TIER, build, game_data,
                     hit_with=model.INCANTATIONS_ART)


def test_the_baseline_is_the_same_product_with_nothing_equipped(
        game_data, revenant, seal, beast_claw):
    """`bare_per_type`: the "before" figure a display puts against the figure.

    The spell half's counterpart of what `equipped()` hands back as its
    `bare` half (AK-359), and the same rule: the level's own attributes, and
    none of the multipliers the build brought. Of the factors of the product
    exactly one can move it -- the spell power, through an attribute -- so a
    relic that only raises a rate leaves it where it was. Without this the
    panel's spell row has nothing to show a difference against, and a
    baseline that quietly took the rates too would show a difference of zero
    for every build alike.
    """
    plain = damage.spell(beast_claw, seal, TIER,
                         build_with(game_data, revenant), game_data,
                         hit_with=model.INCANTATIONS_ART)
    assert plain.bare_figure == pytest.approx(plain.figure), (
        "with nothing equipped the two figures are one and the same, and "
        "anything else means the baseline asks a different question")

    element = cases.effects_raising_rate(game_data, revenant,
                                         "physicsAttackRate")[0]
    rated = damage.spell(beast_claw, seal, TIER,
                         build_with(game_data, revenant, [element]), game_data,
                         hit_with=model.INCANTATIONS_ART)
    assert rated.bare_figure == pytest.approx(plain.figure)
    assert rated.figure > rated.bare_figure

    faith = cases.effects_raising_attribute(game_data, revenant, "Faith")[0]
    scaled = damage.spell(beast_claw, seal, TIER,
                          build_with(game_data, revenant, [faith]), game_data,
                          hit_with=model.INCANTATIONS_ART)
    assert scaled.bare_figure == pytest.approx(plain.figure), (
        "the baseline moved with an equipped relic's Faith, so it is not the "
        "figure this build would have without that relic")
    assert scaled.figure > scaled.bare_figure, (
        "a Faith relic did not reach the seal's spell power, and the reason "
        "this figure stands on the catalyst's own headline is that it does")


def test_the_baseline_answers_the_same_damage_type_the_figure_does(
        game_data, revenant, seal, beast_claw):
    """One rule picks both, so a display cannot compare two damage types.

    Beast Claw is physical: asked about fire, the figure and its baseline are
    both 0.00 and a row shows no difference; asked about every type at once,
    both are the whole of it.
    """
    build = build_with(game_data, revenant)

    def rated(damage_type: str):
        return damage.spell(beast_claw, seal, TIER, build, game_data,
                            hit_with=model.INCANTATIONS_ART,
                            damage_type=damage_type)

    assert rated("Fire").bare_figure == 0.0
    assert rated("Physics").bare_figure == pytest.approx(
        rated("").bare_figure)
