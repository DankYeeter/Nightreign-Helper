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

    "Best" is `final_total`, the figure a display prints, since W6 moved the
    ordering out of `weapons.rank` and into `rank_candidates`. Until then the
    key was `WeaponRating.total`, layer one, and this assertion was written on
    it for a measured reason (QA-065): the two bracketings of the same addends
    disagree by a ULP -- at Wylder, level 1, no relics, `MAX_UPGRADE`,
    positions 319/320 were Gargoyle's Black Halberd and Gargoyle's Sacred
    Black Halberd, bit-identical on `weapon_rating.total` and one ULP apart on
    `final_total` (2026-09-02). A test pinned to `final_total` order was red on
    that input while the function kept its own promise.

    What settles it is not that layer two is the better number but that it is
    the **shown** one, and that the ordering now carries the stable second key
    ULP noise made necessary (do-not rule 29).
    """
    ranked = damage.rank_candidates(build, weapons.MAX_UPGRADE, game_data)

    assert len(ranked) == len(game_data["weapons"])
    assert all(r.question is damage.Question.CANDIDATE for r in ranked)
    assert all(r.tier_applied >= weapons.MAX_UPGRADE for r in ranked)
    keys = [(-r.final_total, r.weapon["id"]) for r in ranked]
    assert keys == sorted(keys)


def test_armaments_that_rate_alike_come_back_in_one_fixed_order(game_data):
    """The second sort key, on the one input where it is visible at all.

    Equal figures are not an edge case here: over 400 groups of armaments
    share a `final_total` at Wylder, level 15, MAX_UPGRADE alone. But a
    tie-break that only reorders is invisible whenever the order it replaces
    was already the id order, and since W5 `weapons.rank` sorts on the same
    per-type sum `final_total` is built from (`scaled_per_type()`, before the
    attack multipliers), with its own id tie-break already in place -- so a
    **bare** build's ties agree with `rank_candidates` before that function's
    own tie-break ever runs, and a case built on one would pass against a
    `rank_candidates` with no tie-break of its own. That is a real change
    from before W5, when the two layers bracketed the same addends
    differently and a bare build (Wylder, level 1, MIN_UPGRADE) was enough to
    show it (AD-024) -- `WeaponRating.total` fell in W5, and with it that
    disagreement.

    A **multiplier** still opens a gap between the two layers, and it opens a
    new one besides: multiplying two per-type sums that already differ by a
    ULP can land on the same float, so `final_total` can tie two armaments
    `scaled_per_type()` does not. The build below is the answer to a search
    over that grid: every Nightfarer at levels 1 and 15, with no effects and
    with the lowest one to three effects raising `physicsAttackRate`,
    `magicAttackRate` or `fireAttackRate`, plus one class-scoped melee buff,
    over all four tiers.

    **Re-measured 2026-09-03 for T-045**, and the case moved. The build this
    test used to stand on -- Duchess, level 1, MIN_UPGRADE, with the two
    lowest-numbered effects raising `magicAttackRate` -- discriminates
    nothing once `weapons.GAME_ATTACK_POWER_RATE` is in the sum: the extra
    multiplication moves the last bit, and the ULP disagreement that case was
    picked for is gone. 33 configurations of the grid still discriminate; the
    one below has the most groups of them and is otherwise the same shape.

    Guardian, level 1, MIN_UPGRADE, with the single lowest-numbered effect
    that raises `physicsAttackRate` ("Physical Attack Up +3", id 6001400):
    409 groups tie on `final_total`, two of them out of id order in the
    layer-one order. The plainer of the two is `final_total` 62.416742...,
    shared by Fire and Lightning Iron Greatsword, Fire and Lightning Vulgar
    Militia Shotel, Magic Brass Shield and Magic Great Turtle Shell -- the
    first four sum to 59.25887999999999 in layer one and the last two to
    59.25888, a ULP higher, which the shared multiplier 1.1050000190734863
    erases. Layer one therefore puts the two highest-id armaments of the six
    in front, and the tie-break is what puts them back.

    So the case asserts three things and not one: that ties exist, that at
    least one of them is out of id order before the tie-break (without which
    this test proves nothing), and that none of them is out of it afterwards.
    """
    hero = cases.hero_by_name(game_data, "Guardian")
    rate_ids = cases.effects_raising_rate(
        game_data, hero, "physicsAttackRate", 1)
    effects = [cases.effect_by_id(game_data, i) for i in rate_ids]
    build = model.compute(hero, 1, effects, game_data.get("curves", {}))
    tier = weapons.MIN_UPGRADE
    attributes = getattr(build,
                         damage.ATTRIBUTES_FOR[damage.Question.CANDIDATE])

    ranked = damage.rank_candidates(build, tier, game_data)
    layer_one = [rating.weapon["id"] for rating in
                 weapons.rank(game_data, attributes, tier)]
    place = {weapon_id: index for index, weapon_id in enumerate(layer_one)}

    groups: dict[float, list[int]] = {}
    for rating in ranked:
        groups.setdefault(rating.final_total, []).append(rating.weapon["id"])
    tied = {figure: ids for figure, ids in groups.items() if len(ids) > 1}

    assert tied, ("no two armaments rate alike here, so this case cannot see "
                  "the tie-break at all")
    discriminating = {figure: ids for figure, ids in tied.items()
                      if sorted(ids, key=place.__getitem__) != sorted(ids)}
    assert discriminating, (
        "every tie in this build was already in id order when `weapons.rank` "
        "handed it over, so dropping the second sort key would change "
        "nothing and this case would pass without it. Pick a build and tier "
        "where layer one and layer two disagree -- see the docstring")

    for figure, ids in tied.items():
        assert ids == sorted(ids), (
            f"the {len(ids)} armaments rating {figure} came back as {ids}, "
            f"which is not their id order")


def test_a_candidate_carries_the_attack_multipliers(game_data, build):
    """W6's value of `MULTIPLIERS_FOR[CANDIDATE]`, stated as behaviour.

    Until W6 this table entry was False: the arsenal tab ranked without the
    attack multipliers while the breakdown panel showed them, and one armament
    stood on screen as two figures at once (QA-018, 203.4 against 244.1). The
    user's measurement in play settled it -- what was wrong was not that the
    tab left the multipliers out but that a move-restricted buff was in them
    (`model.MOVE_SCOPED_EFFECT_IDS`). With that buff gone from the layer, the
    layer belongs to a candidate exactly as it belongs to an equipped
    armament.

    Asserted against the layer-one figure times the build's own rates rather
    than against a frozen number, and the case refuses to run on a build whose
    rates are all 1.0 -- there the two answers coincide and the entry could be
    flipped back without a test noticing.
    """
    ranked = damage.rank_candidates(build, weapons.MAX_UPGRADE, game_data)
    by_id = {r.weapon["id"]: r for r in ranked}

    moved = 0
    for weapon in game_data["weapons"]:
        layer_one = weapons.rate(weapon, build.attributes, game_data,
                                 weapons.MAX_UPGRADE)
        answer = by_id[weapon["id"]]
        assert answer.scaled_per_type == layer_one.scaled_per_type(), \
            weapon["name"]
        if answer.final_per_type != answer.scaled_per_type:
            moved += 1

    assert moved, (
        "not one armament's figure moved between the two layers, so this "
        "build carries no multiplier and the case cannot tell "
        "MULTIPLIERS_FOR[CANDIDATE] True from False")


# -- the panel's own view ------------------------------------------------

def test_the_panel_s_rating_is_the_equipped_question(game_data, build, hero,
                                                     starting_weapon):
    """`attack_rating` is a view of `equipped()`, not a second calculation.

    The panel stopped asking in these terms in W3; the advisor's marginal
    contribution (AD-018) and the window-free half of the golden file still
    do. What it must not be is a second answer to the same question, which is
    how QA-018 arose in the first place.

    The two totals are asserted with `==` and no tolerance on purpose. Until
    W3 this view carried its own accumulation of layer one -- a plain loop
    where `Rating.scaled_total` uses a compensated `sum()` -- and the two
    disagreed in the last bit. An `approx` here would let that summation back
    in without a word, which is exactly what assurance Z1 forbids.
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
    assert panel.scaled_total == now.scaled_total
    assert panel.bare_scaled_total == bare.scaled_total
    assert panel.figures() == damage.breakdown_figures(bare, now)


# The reciprocal of the divergence rate QA-064/d records for this pair of
# summations (about 0.15% of armament-tier-build combinations), times three.
# Below it, a second summation put back into the panel view would be caught by
# luck or not at all; at three times over, the case set is expected to hold
# several counterexamples rather than one.
ENOUGH_MULTI_TYPE = 3 * 667


def test_the_panel_view_forms_no_total_of_its_own(game_data, build, hero,
                                                  starting_weapon):
    """Assurance Z1 through `attack_rating`, and it needs the whole dataset.

    One armament cannot hold this. A plain accumulation and a compensated
    `sum()` over the same addends in the same order agree for all but a
    fraction of a percent of cases, and they agree always for an armament with
    a single damage type -- so the obvious single-case assertion passes with
    the second summation back in place. That is not hypothetical: this view
    carried exactly such an accumulation until AD-019 step W3.

    So the assertion runs over every armament at every tier the arsenal
    spinbox can ask for, and the case set is counted before it is trusted.
    """
    multi_type = 0
    for weapon in game_data["weapons"]:
        for tier in ALL_TIERS:
            slot = slot_holding(weapon, tier)
            bare, now = damage.equipped(slot, damage.STARTING_SLOT, build,
                                        hero, game_data)
            panel = damage.attack_rating(
                weapon, tier, build, game_data,
                starting_armament=damage.is_starting_armament(
                    weapon, hero, damage.STARTING_SLOT))

            if len(now.scaled_per_type) > 1:
                multi_type += 1
            assert panel.scaled_total == now.scaled_total, weapon["name"]
            assert panel.bare_scaled_total == bare.scaled_total, weapon["name"]
            assert panel.final_total == now.final_total, weapon["name"]

    assert multi_type >= ENOUGH_MULTI_TYPE, (
        f"only {multi_type} armament-tier cases in this dataset carry more "
        f"than one damage type, and a single-type case cannot tell two "
        f"summations apart -- the assertions above would pass on arithmetic "
        f"that had drifted")
