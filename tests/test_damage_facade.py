"""Every rating names the question it answers, and the answer names its inputs.

`ARCHITECTURE.md` AD-019 step W2, AD-020, AD-022, assurance Z1.

Rating an armament needs three inputs -- which attribute set, which tier, and
whether the attack multipliers belong to the question. Until the facade
existed, each display chose all three for itself as a side effect of which
module it had imported, and three numbers for one armament stood on screen at
once (QA-018, QA-055, QA-056). The tests below are about the choosing, not
about the arithmetic: that the choice is made in one place per question, that
the five differences AD-020 calls deliberate survive it, and that a total is
never anything other than the sum of the per-type map beside it.

The arithmetic itself is unchanged in this step and is covered where it
already was -- `tests/test_weapon_damage_golden.py` for the finished figures,
`tests/test_weapon_rating_scaled_per_type.py` for the layer beneath.
"""

from __future__ import annotations

import dataclasses

import pytest

from nrplanner import damage, model, weapons, weaponslots

from tests import weapon_damage_cases as cases

LEVEL = 15
ALL_TIERS = range(weapons.MIN_UPGRADE, weapons.MAX_UPGRADE + 1)


@pytest.fixture(scope="module")
def hero(game_data):
    """Wylder, the Nightfarer QA measured the divergence on."""
    return cases.hero_by_name(game_data, "Wylder")


@pytest.fixture(scope="module")
def build(game_data, hero):
    """A build that moves all three inputs at once.

    It carries an attack rate, so the multiplier layer is visible; a class
    rate, so the per-class part of it is visible; and an attribute bonus, so
    `attributes` and `base_attributes` are two different sets and a question
    that picked the wrong one shows it. Every effect is chosen by asking
    `model.compute` what it does, never by an id written down here.
    """
    ids = (cases.effects_raising_rate(game_data, hero, "physicsAttackRate", 1)
           + cases.effects_raising_attribute(game_data, hero, "Strength", 1)
           + [cases.scoped_effect(game_data, hero, "melee")])
    effects = [cases.effect_by_id(game_data, i) for i in ids]
    return model.compute(hero, LEVEL, effects, game_data.get("curves", {}))


@pytest.fixture(scope="module")
def starting_weapon(game_data, hero):
    """The Nightfarer's own starting armament, half of the pairing."""
    return cases.weapon_by_id(game_data, hero["starting_weapon"])


def slot_holding(weapon: dict, tier: int) -> weaponslots.WeaponSlot:
    return weaponslots.WeaponSlot(weapon=weapon, tier=tier)


# -- assurance Z1 --------------------------------------------------------

def test_a_rating_has_no_total_to_be_given(game_data, build, starting_weapon):
    """A total cannot be handed in, so it cannot disagree with its own map.

    This is assurance Z1 at its source: `scaled_total` and `final_total` are
    not fields at all, so there is no way to construct a `Rating` whose total
    was worked out somewhere else. A test that only compared the two would
    pass just as well against a stored field that happened to be right today.

    QA-063: excluding those two names is not the same claim as "no total can
    be handed in from outside". A `Rating` carrying a field named
    `scaled_total_` (note the underscore) and a `scaled_total` property that
    reads `self.scaled_total_ or sum(...)` passes both `not in` checks and
    still hands a total in from outside. Nailing the complete field set turns
    every new field into a decision this test has to be told about, rather
    than a name it has to dodge.
    """
    field_names = {f.name for f in dataclasses.fields(damage.Rating)}

    assert field_names == {
        "question", "weapon_rating", "scaled_per_type", "final_per_type",
        "rates", "weapon_class", "starting_armament",
    }

    rating = damage.candidate(starting_weapon, weapons.MAX_UPGRADE, build,
                              game_data)
    with pytest.raises(TypeError):
        dataclasses.replace(rating, final_total=1.0)


def test_a_total_follows_the_map_it_belongs_to(game_data, build,
                                               starting_weapon):
    """Change the per-type figures and the total changes with them.

    The other half of Z1: one representation per layer. If the totals were
    kept alongside the maps rather than derived from them, this rating would
    keep answering with the old number.
    """
    rating = damage.candidate(starting_weapon, weapons.MAX_UPGRADE, build,
                              game_data)
    doubled = dataclasses.replace(
        rating,
        final_per_type={k: v * 2 for k, v in rating.final_per_type.items()})

    assert doubled.final_total == rating.final_total * 2


def test_every_total_is_exactly_the_sum_of_its_own_map(game_data, build,
                                                       hero):
    """Exactly, over the whole dataset -- `==`, never `approx`.

    A tolerance here would hide precisely the drift the assurance exists to
    prevent. The advisor values a candidate by a **difference of two totals**;
    if the two sides were bracketed differently, the noise floor of that
    comparison would be set by the inconsistency rather than by the
    arithmetic, and marginal contributions are small (AD-019, do-not rule 28).
    """
    checked = 0
    for weapon in game_data["weapons"]:
        for tier in ALL_TIERS:
            slot = slot_holding(weapon, tier)
            for rating in damage.equipped(slot, damage.STARTING_SLOT, build,
                                          hero, game_data):
                assert rating.scaled_total == sum(
                    rating.scaled_per_type.values()), weapon["name"]
                assert rating.final_total == sum(
                    rating.final_per_type.values()), weapon["name"]
                checked += 1
    assert checked == len(game_data["weapons"]) * len(ALL_TIERS) * 2


# -- the three questions and their inputs --------------------------------

def test_the_tables_answer_for_every_question_and_no_other(game_data):
    """A fourth question cannot slip in with its inputs left unstated.

    Both policy tables are keyed by the enum itself, so adding a member
    without deciding its attribute set and its multiplier layer fails here
    rather than silently inheriting whatever the caller had to hand.
    """
    assert set(damage.MULTIPLIERS_FOR) == set(damage.Question)
    assert set(damage.ATTRIBUTES_FOR) == set(damage.Question)
    for attribute in damage.ATTRIBUTES_FOR.values():
        assert hasattr(model.Build(), attribute)


def test_the_bare_question_stands_on_the_level_s_own_attributes(
        game_data, build, hero, starting_weapon):
    """The panel's left-hand column, and why it is not a bug (AD-020, 2).

    The bare figure is the armament before anything equipped raised the
    Nightfarer's attributes. Take that away and the panel's before-and-after
    has nothing to compare.
    """
    assert build.attributes != build.base_attributes, \
        "this build was supposed to raise an attribute"

    slot = slot_holding(starting_weapon, weapons.MAX_UPGRADE)
    bare, now = damage.equipped(slot, damage.STARTING_SLOT, build, hero,
                                game_data)

    on_own = weapons.rate(starting_weapon, build.base_attributes, game_data,
                          weapons.MAX_UPGRADE)
    on_raised = weapons.rate(starting_weapon, build.attributes, game_data,
                             weapons.MAX_UPGRADE)

    assert bare.scaled_per_type == on_own.scaled_per_type()
    assert now.scaled_per_type == on_raised.scaled_per_type()
    assert bare.scaled_total != now.scaled_total


def test_only_the_equipped_question_carries_the_multipliers(
        game_data, build, hero, starting_weapon):
    """Which layer belongs to which question is read off one table.

    The answer to QA-018 is a value in `MULTIPLIERS_FOR`, so this test says
    what the table says rather than repeating today's three answers: where the
    table says no, the shown figure is the scaled figure untouched and the
    breakdown has no rates to list.
    """
    slot = slot_holding(starting_weapon, weapons.MAX_UPGRADE)
    bare, now = damage.equipped(slot, damage.STARTING_SLOT, build, hero,
                               game_data)
    other = damage.candidate(starting_weapon, weapons.MAX_UPGRADE, build,
                             game_data)

    for rating in (bare, now, other):
        if damage.MULTIPLIERS_FOR[rating.question]:
            assert rating.final_per_type != rating.scaled_per_type
            assert rating.rates
        else:
            assert rating.final_per_type == rating.scaled_per_type
            assert rating.rates == {}


def test_a_candidate_has_to_be_told_which_tier_it_is_asked_about(
        game_data, build, starting_weapon):
    """No default tier, on purpose (AD-020, 1).

    The arsenal tab ranks at a tier the player chooses, which is the question
    it exists to ask; a default would quietly put the slot tier back and turn
    the deliberate difference of QA-055 into an accident again.
    """
    with pytest.raises(TypeError):
        damage.candidate(starting_weapon, build=build, data=game_data)


def test_the_equipped_question_takes_its_tier_from_the_slot(
        game_data, build, hero, starting_weapon):
    """The slot is the only source of the tier for an equipped armament."""
    for tier in ALL_TIERS:
        slot = slot_holding(starting_weapon, tier)
        bare, now = damage.equipped(slot, damage.STARTING_SLOT, build, hero,
                                    game_data)
        expected = max(starting_weapon.get("rarity", 0) + 1, tier)

        assert bare.tier_applied == expected
        assert now.tier_applied == expected


def test_a_tier_request_past_the_maximum_clamps_rather_than_reaching_past_it(
        game_data, build, starting_weapon):
    """`tier_applied` is `max(own, requested)` only within the reachable range.

    QA-064/c: the spinbox never offers more than `weapons.MAX_UPGRADE`, but
    `candidate()` places no ceiling on `target_tier` (AD-020, point 1), so 5
    or 6 is a reachable call even though it is not a reachable click.
    `weapons.rate` clamps the request before it reaches the reinforce table,
    so the answer comes back at `MAX_UPGRADE`, short of what was asked.
    """
    rating = damage.candidate(starting_weapon, weapons.MAX_UPGRADE + 2, build,
                              game_data)

    assert rating.tier_applied == weapons.MAX_UPGRADE


def test_a_candidate_never_takes_the_starting_armament_penalty(
        game_data, build, hero, starting_weapon):
    """The x0.85 follows a pairing, and a candidate is in no slot (AD-020, 3).

    Verified in play on 2026-08-22: the penalty needs the Nightfarer's own
    starting armament **and** slot 1. A weapon that sits nowhere has no slot
    to be in, so the question cannot reach the penalty even for the very
    armament that would take it if it were equipped.
    """
    penalty = cases.effects_raising_rate(game_data, hero,
                                         "physicsAttackPowerRate", 1)
    with_penalty = model.compute(
        hero, LEVEL, [cases.effect_by_id(game_data, penalty[0])],
        game_data.get("curves", {}))

    slot = slot_holding(starting_weapon, weapons.MAX_UPGRADE)
    _, equipped_here = damage.equipped(slot, damage.STARTING_SLOT,
                                       with_penalty, hero, game_data)
    _, equipped_elsewhere = damage.equipped(slot, damage.STARTING_SLOT + 1,
                                            with_penalty, hero, game_data)
    asked_about = damage.candidate(starting_weapon, weapons.MAX_UPGRADE,
                                   with_penalty, game_data)

    assert equipped_here.starting_armament
    assert equipped_here.final_total < equipped_elsewhere.final_total
    assert not asked_about.starting_armament
    assert not any(field_name in asked_about.rates
                   for fields in damage.STARTING_AR_RATE_FOR.values()
                   for field_name in fields)


def test_the_multiplier_layer_excludes_the_critical_rate(
        game_data, hero, starting_weapon):
    """A critical-only buff must not move the ordinary hit (AD-020, point 5).

    QA-063: of the five AD-020 differences, four are enforced by a table this
    module reads (`MULTIPLIERS_FOR`, `ATTRIBUTES_FOR`) or by a structural
    check (Z1); the critical-rate exclusion was only the comment above the
    `rate = 1.0` line in `_answer`. A build that raises `model.CRIT_RATE` and
    nothing else must come back unchanged, because no `*AttackRate` or
    `*AttackPowerRate` field is set -- if the exclusion slipped, `CRIT_RATE`
    would have to be the thing moving the number.
    """
    build = model.Build(rates={model.CRIT_RATE: 2.0})
    slot = slot_holding(starting_weapon, weapons.MAX_UPGRADE)
    # A slot other than STARTING_SLOT, so the starting-armament penalty --
    # which does legitimately read build.rates -- cannot also explain a
    # difference here (AD-020, point 3).
    _, now = damage.equipped(slot, damage.STARTING_SLOT + 1, build, hero,
                             game_data)

    assert now.final_per_type == now.scaled_per_type
    assert now.final_total == now.scaled_total


def test_the_equipped_pair_is_the_panel_s_two_columns(game_data, build, hero,
                                                      starting_weapon):
    """`equipped()` answers two questions at once, in the order shown."""
    slot = slot_holding(starting_weapon, weapons.MAX_UPGRADE)
    bare, now = damage.equipped(slot, damage.STARTING_SLOT, build, hero,
                                game_data)

    assert bare.question is damage.Question.BARE
    assert now.question is damage.Question.EQUIPPED
    assert bare.weapon is starting_weapon and now.weapon is starting_weapon


# -- ranking candidates --------------------------------------------------

def test_ranking_answers_the_candidate_question_for_every_armament(
        game_data, build):
    """Best first, every one of them asked the same question at one tier.

    "Best first" is `weapons.rank`'s own promise: descending
    `WeaponRating.total`, layer one, which is the key it actually sorts by.
    That is a different claim from descending `final_total` (QA-065):
    `WeaponRating.total` sums the base and scaled maps whole, `final_total`
    sums the merged per-type map, and the two bracketings of the same
    addends can disagree by a ULP without the sort key moving at all --
    measured at Wylder, level 1, no relics, `MAX_UPGRADE`: positions 319/320
    are Gargoyle's Black Halberd and Gargoyle's Sacred Black Halberd,
    bit-identical on `weapon_rating.total` and one ULP apart on
    `final_total` (2026-09-02). A test pinned to `final_total` order would be
    red on that reachable input while `rank_candidates` did exactly what it
    promises. W6, which moves the sort onto layer two, is what has to bring a
    stable secondary key with it.
    """
    ranked = damage.rank_candidates(build, weapons.MAX_UPGRADE, game_data,
                                    require_usable=False)

    assert len(ranked) == len(game_data["weapons"])
    assert all(r.question is damage.Question.CANDIDATE for r in ranked)
    assert all(r.tier_applied >= weapons.MAX_UPGRADE for r in ranked)
    totals = [r.weapon_rating.total for r in ranked]
    assert totals == sorted(totals, reverse=True)


def test_a_candidate_is_the_scaled_figure_the_arsenal_tab_shows_today(
        game_data, build):
    """Today's value of `MULTIPLIERS_FOR[CANDIDATE]`, stated as behaviour.

    The arsenal tab ranks without the attack multipliers and the breakdown
    panel shows them, which is the 203.4 against 244.1 of QA-018. W2 moves
    that choice into one table without deciding it, so what the facade answers
    for a candidate is still, to the last bit, the figure the tab shows.

    Which of the two is right is a measurement the user makes in game, and the
    step that acts on it is W6: it sets one value in `MULTIPLIERS_FOR` and
    brings this test with it, naming the finding in the commit. Until then a
    flipped table value is a silent change of a shown number, and this is what
    catches it.
    """
    ranked = damage.rank_candidates(build, weapons.MAX_UPGRADE, game_data,
                                    require_usable=False)
    by_id = {r.weapon["id"]: r for r in ranked}

    for weapon in game_data["weapons"]:
        today = weapons.rate(weapon, build.attributes, game_data,
                             weapons.MAX_UPGRADE)
        answer = by_id[weapon["id"]]
        assert answer.final_per_type == today.scaled_per_type(), weapon["name"]


def test_the_usable_filter_reaches_the_requirement_check(game_data):
    """`require_usable` is the caller's input, not a policy of the question.

    Asked with an attribute set of nothing but zeros, because with a real one
    the flag has nothing to do: QA-061 measured that every armament in this
    dataset can be held by every Nightfarer from level 1, so the checkbox
    filters 1793 down to 1793. Whether that is intended is the user's call and
    is not settled here -- but the branch behind the flag has to be shown to
    work, and an attribute set the game cannot produce is the only way to show
    it on this data.
    """
    nothing = model.Build(
        attributes={k: 0 for k in ("Strength", "Dexterity", "Intelligence",
                                   "Faith", "Arcane")})

    everything = damage.rank_candidates(nothing, weapons.MIN_UPGRADE,
                                        game_data, require_usable=False)
    usable = damage.rank_candidates(nothing, weapons.MIN_UPGRADE, game_data,
                                    require_usable=True)

    unusable = {r.weapon["id"] for r in everything if not r.meets_requirements}

    assert unusable, ("this dataset was supposed to have armaments with "
                      "requirements a zeroed attribute set cannot meet")
    assert all(r.meets_requirements for r in usable)
    assert ({r.weapon["id"] for r in usable}
            == {r.weapon["id"] for r in everything} - unusable)


# -- the panel's own view ------------------------------------------------

def test_the_panel_s_rating_is_the_equipped_question(game_data, build, hero,
                                                     starting_weapon):
    """`attack_rating` is a view of `equipped()`, not a second calculation.

    It still exists because the breakdown panel asks in its own terms until
    AD-019 step W3; what it must not be is a second answer to the same
    question, which is how QA-018 arose in the first place.
    """
    slot = slot_holding(starting_weapon, weapons.MAX_UPGRADE)
    bare, now = damage.equipped(slot, damage.STARTING_SLOT, build, hero,
                                game_data)
    panel = damage.attack_rating(
        starting_weapon, slot.tier, build, game_data,
        starting_armament=damage.is_starting_armament(
            starting_weapon, hero, damage.STARTING_SLOT))

    assert panel.final_per_type == now.final_per_type
    assert panel.final_total == now.final_total
    assert panel.rates == now.rates
    assert panel.before.scaled_per_type() == bare.scaled_per_type
