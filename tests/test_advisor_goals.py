"""Three named directions, each with what it cannot know written into it.

AD-004 and `GOAL.md` A3/A7. A goal is not a number, it is a number with a
stated scope, so the first assertion in this file is not about a figure at
all: no direction in the registry has an empty `scope`. Since AD-025 that is
where the promise lives -- and it is checkable **without a dataset**, which is
the point of the move rather than a side effect (QA-106, checkpoint 29). What
a *run* left out is the other class, travels in `GoalScore.unknowns`, and may
be empty. The rest are about the two figures being the ones the rest of the
program already stands on --

* the damage goal is the question the weapon panel asks, `damage.equipped`,
  which works the starting-armament pairing out from the slot and the
  Nightfarer. `damage.candidate` answers a different question and would drop
  that penalty (AD-020 point 3). Neither the figure **nor the order** would
  survive the swap: a candidate can carry the penalty itself, so it is not a
  constant factor over the candidates, and the belief that it was stood in
  this project as settled until it was measured (QA-101). Two cases tell the
  questions apart -- `test_the_damage_goal_charges_the_starting_armament_
  penalty` for the amount and
  `test_the_damage_goal_ranks_a_self_inflicted_penalty_below` for the order;
* the survival goal weighs the eight damage kinds with the weights the
  context carries and with none of its own (AD-004, OF-3).

**What is not tested here, said rather than left implicit:** that either
figure is the one the *game* shows. The damage goal's figure is held against
the game in `tests/test_attack_power_against_the_game.py` and nowhere else;
the survival goal's is held against nothing outside the program at all. What
this file does check is that the registry states the scope of that agreement
in `Goal.scope` -- including the armaments the agreement does not cover.
"""

from __future__ import annotations

import dataclasses

import pytest

from nrplanner import advisorbar, damage, model, weaponslots
from nrplanner.advisor import candidates, explain, goals, types
from nrplanner.advisor.evaluate import evaluate

from tests import advisor_cases as advisor
from tests import weapon_damage_cases as cases


@pytest.fixture(scope="module")
def wylder(game_data):
    return cases.hero_by_name(game_data, "Wylder")


def build_with(game_data, hero, effect_ids=(), reference=None):
    """A build carrying these effects, through the advisor's own door."""
    ctx = advisor.context(game_data, hero, reference=reference,
                          armament_effect_ids=tuple(effect_ids))
    return evaluate(advisor.problem([advisor.RED]), (), ctx), ctx


def test_the_project_promised_two_named_directions(game_data):
    """`GOAL.md` A3: at least two, named, and reachable by id."""
    assert set(goals.GOALS) >= {"max_damage", "min_damage_taken"}
    assert goals.GOALS["max_damage"].label == "Maximise damage"
    assert goals.GOALS["min_damage_taken"].label == "Minimise damage taken"


def test_the_registry_cannot_be_added_to_at_run_time():
    """A goal nobody could name in a cache key is a goal nobody can cache.

    `weighting.id` and `goal_id` are what a cached run is keyed under
    (AD-007, AD-018); a registry that grew while the program ran would leave
    entries whose goal no longer exists.
    """
    with pytest.raises(TypeError):
        goals.GOALS["invented"] = goals.MAX_DAMAGE


@pytest.mark.parametrize("goal_id", sorted(goals.GOALS))
def test_no_direction_carries_an_empty_scope(goal_id):
    """Checkpoint 29: `GOAL.md` A7 as a property of the registry.

    **No `game_data` on purpose.** Before AD-025 the same promise was read off
    a `GoalScore`, so it could only be checked where a build could be
    computed, which is a machine with the game or a snapshot of it -- and on a
    runner it was skipped along with everything else (QA-106). A direction's
    scope needs no dataset, no build and no inventory, and this case is the
    first advisor case that holds anything on a bare runner. Adding a fixture
    here would give that up again.

    A static warning in the tab would say the same thing whatever the run did,
    and AD-010 rejected that; what makes this different is that the sentence
    is the *program's*, read by the display rather than written into it
    (`UI_SPEC` AK-63), and that the run's own findings are a second source
    beside it.
    """
    scope = goals.GOALS[goal_id].scope

    assert scope, (
        f"{goal_id} ranks builds and says nothing about what its figure "
        f"cannot know, whatever the run")
    assert all(line.strip() for line in scope), (
        f"{goal_id} carries a blank scope line, which reads as a sentence "
        f"and says nothing")


@pytest.mark.parametrize("goal_id", sorted(goals.GOALS))
def test_every_score_is_sayable_to_the_player(game_data, wylder, goal_id):
    """The half of the old case that does need a run: `display`.

    Split off from the scope assertion above rather than left beside it: the
    two now need different things -- one needs a registry, the other needs a
    dataset -- and a case that needs both is skipped wherever either is
    missing.
    """
    reference = advisor.scaling_armament(game_data, wylder)
    build, ctx = build_with(game_data, wylder, reference=reference)

    assert goals.GOALS[goal_id].score(build, ctx).display, (
        "a score has to be sayable to the player")


@pytest.mark.parametrize("goal_id", sorted(goals.GOALS))
def test_no_sentence_stands_in_both_classes(game_data, wylder, goal_id):
    """Checkpoint 30: the same sentence twice is not emphasis, it is a fault.

    Drawn from two sources, one sentence in both would appear at two places on
    one screen with two justifications behind it -- once outside the cards as
    the scope of the figure, once on the card as something this run left out.
    AD-025.4 forbids it, and this is the case that holds the ban.

    Asked over both contexts the direction can really be in, because a
    duplicate that only showed up without an armament would be invisible in
    the ordinary one.
    """
    reference = advisor.scaling_armament(game_data, wylder)
    scope = set(goals.GOALS[goal_id].scope)
    with_armament = build_with(game_data, wylder, reference=reference)
    without = build_with(game_data, wylder)

    for build, ctx in (with_armament, without):
        shared = scope & set(goals.GOALS[goal_id].score(build, ctx).unknowns)

        assert not shared, (
            f"{goal_id} says {sorted(shared)!r} twice: once in the registry "
            f"as a procedural sentence and once in the result as a finding "
            f"of this run (AD-025.4)")


@pytest.mark.parametrize("goal_id", sorted(goals.GOALS))
def test_a_run_finding_does_not_survive_every_run(game_data, wylder, goal_id):
    """Checkpoint 31: what stands in every run is a procedural sentence.

    The yardstick of AD-025.1 read backwards, and the only version of it a
    test can hold: if a line comes back from two genuinely different runs of
    one direction, then whether it applies did **not** depend on the run, and
    it belongs in `Goal.scope` where it is drawn once instead of once per
    card. Two contexts are the fewest that can show it; with an armament and
    without one are the two the registry really distinguishes.

    **Scope of this case:** it needs the dataset and is skipped on a runner
    without one (QA-106, standing limitation). Checkpoint 29 is the half that
    survives that.
    """
    reference = advisor.scaling_armament(game_data, wylder)
    with_armament, ctx = build_with(game_data, wylder, reference=reference)
    without, plain_ctx = build_with(game_data, wylder)

    goal = goals.GOALS[goal_id]
    always = (set(goal.score(with_armament, ctx).unknowns)
              & set(goal.score(without, plain_ctx).unknowns))

    assert not always, (
        f"{goal_id} reports {sorted(always)!r} whether an armament is chosen "
        f"or not, so it is a statement about the method and belongs in "
        f"Goal.scope (AD-025.1)")


@pytest.mark.parametrize("goal_id", sorted(goals.GOALS))
def test_every_goal_gives_a_finite_number_for_a_known_build(game_data, wylder,
                                                            goal_id):
    reference = advisor.scaling_armament(game_data, wylder)
    build, ctx = build_with(game_data, wylder, reference=reference)

    score = goals.GOALS[goal_id].score(build, ctx)

    assert score.value > 0
    assert isinstance(score.value, float)


def test_the_damage_goal_always_carries_the_attack_rating_reservation():
    """The promise the README's Known limits makes, kept in the registry.

    The figure the advisor ranks by is the weapon panel's figure, and since
    T-045 that figure **is** the game's own -- but only over a stated range.
    A run that stopped saying so would be the first place in the program
    where the scope was dropped, and it would be dropped exactly where the
    player is being asked to act on the number.

    Two lines have been replaced here rather than deleted, and both times for
    the same reason: an untrue reservation is worse than none, and *nothing*
    in its place is worse than either.

    * "Attack rating has not been verified against an in-game number" became
      false when 2256 comparisons against the game settled it (QA-095), so
      what stands there now is the **scope** of the agreement.
    * "Staves and seals are outside that match" became false when T-046 put
      the game's own catalyst figure on screen (QA-099). What stands there
      now is the scope of *that* figure: measured at the catalyst's own
      rarity, and the game's display rather than a claim about spell damage.
      This case asserts the replacement, not merely the absence -- a
      reservation dropped for a fault that was fixed is right; a scope
      dropped with it is the A7 failure this project keeps repeating.
    * "Spell damage is not in the game data, so spells are not rated" became
      false when A26-1 extracted it and AD-052 gave the spell rows a figure
      of their own. What stands there now is the scope of *that* figure: the
      spell rows only, and the equipment the Nightfarer starts an expedition
      with -- never a spell found in a run.

    Read off the registry since AD-025 and no longer off a score: the two runs
    this used to loop over asked the same question of the same constant, and
    the constant is now where it belongs. The eight assertions below are
    unchanged -- they are the whole record of QA-095 and QA-099 and are the
    reason this case exists. Like checkpoint 29 it needs no dataset now.
    """
    stated = goals.GOALS["max_damage"].scope

    assert not any("has not been verified" in line for line in stated), (
        "the old reservation is back; it says the attack rating was "
        "never checked against the game, which is no longer true")
    scope = [line for line in stated
             if "matches the game's own display" in line]
    assert scope, "no line says where the agreement with the game holds"
    for outside in ("reinforced", "infused", "Scholar", "Undertaker"):
        assert any(outside in line for line in scope), (
            f"the scope line does not say that {outside} armaments or "
            f"Nightfarers are outside the measurement")
    assert not any("outside that match" in line for line in stated), (
        "the old catalyst reservation is back; it says this program "
        "shows a staff's physical attack rating, which since T-046 it "
        "does not")
    catalysts = [line for line in stated
                 if "staves and seals" in line.lower()]
    assert catalysts, (
        "nothing says what a catalyst's figure is; the scope of a "
        "second measured quantity cannot be left out because the "
        "quantity is now right")
    for said in ("own rarity", "spell hits for"):
        assert any(said in line for line in catalysts), (
            f"the catalyst line does not say {said!r}: it was measured "
            f"at the base rarity only, and it is the game's display "
            f"rather than what a spell does")
    spell_rows = [line for line in stated if "spell rows" in line]
    assert spell_rows, (
        "nothing says what a spell's figure is formed on; the line that "
        "used to say spells are not rated at all became false with AD-052, "
        "and a scope dropped along with a false reservation is the A7 "
        "failure this project keeps repeating")
    assert any("starts an expedition with" in line for line in spell_rows), (
        "the spell line does not say that the figure hangs on the equipment "
        "the Nightfarer starts with, which is the whole of what it can and "
        "cannot promise (AD-052)")
    assert any("Critical-only" in line for line in stated)
    assert not any("convert" in line for line in stated), (
        "the old conversion reservation is back; it says a relic that "
        "converts part of the starting armament's damage is not in this "
        "figure, and it is -- measured on 2026-09-19 at +1.80 on Wylder "
        "and +2.78 on Revenant (AD-047 point 6)")


def test_the_damage_goal_counts_the_attack_multipliers(game_data, wylder):
    """A build that buffs physical attack hits harder, and the goal says so.

    The mutation this stands against is asking the facade for the bare figure
    -- the breakdown panel's left-hand column, which is the armament with
    nothing equipped. Every relic that buffs an attack rate rather than an
    attribute would then be worth exactly nothing, and the advisor would rank
    a build's whole multiplier stack at zero (AD-019 step W6, QA-018).
    """
    reference = advisor.scaling_armament(game_data, wylder)
    buff = cases.effects_raising_rate(game_data, wylder, "physicsAttackRate")

    plain, ctx = build_with(game_data, wylder, reference=reference)
    buffed, _ = build_with(game_data, wylder, effect_ids=buff,
                           reference=reference)

    assert goals.GOALS["max_damage"].score(buffed, ctx).value > \
        goals.GOALS["max_damage"].score(plain, ctx).value


def test_the_damage_goal_moves_with_the_attributes(game_data, wylder):
    """The half `weapons.rate` owns: scaling, and with it F2's whole point."""
    reference = advisor.scaling_armament(game_data, wylder)
    stronger = cases.effects_raising_attribute(
        game_data, wylder, "Strength", 1)

    plain, ctx = build_with(game_data, wylder, reference=reference)
    raised, _ = build_with(game_data, wylder, effect_ids=stronger,
                           reference=reference)

    assert goals.GOALS["max_damage"].score(raised, ctx).value > \
        goals.GOALS["max_damage"].score(plain, ctx).value


def test_the_damage_goal_charges_the_starting_armament_penalty(game_data,
                                                               wylder):
    """The pairing of slot 1 with the Nightfarer's own starting armament.

    Both halves at once, verified in play on 2026-08-22: moved to another
    slot the armament loses the penalty, and a different armament in slot 1
    never gains it. `damage.equipped` works that out from the slot index and
    the hero; `damage.candidate` has no slot and so cannot carry it at all
    (AD-020 point 3). This is the assertion that tells which of the two the
    goal asks -- the figures differ by the 0.85 the game charges.
    """
    starting = next(w for w in game_data["weapons"]
                    if w["id"] == wylder["starting_weapon"])
    penalty = cases.effects_raising_rate(
        game_data, wylder, "physicsAttackPowerRate")

    in_slot_one = types.ReferenceArmament(weapon=starting, tier=1,
                                          slot_index=damage.STARTING_SLOT)
    elsewhere = dataclasses.replace(in_slot_one,
                                    slot_index=damage.STARTING_SLOT + 1)
    paired, ctx_paired = build_with(game_data, wylder, effect_ids=penalty,
                                    reference=in_slot_one)
    moved, ctx_moved = build_with(game_data, wylder, effect_ids=penalty,
                                  reference=elsewhere)

    assert goals.GOALS["max_damage"].score(paired, ctx_paired).value < \
        goals.GOALS["max_damage"].score(moved, ctx_moved).value, (
        "the starting-armament penalty did not reach the damage goal, so it "
        "is not asking the question the weapon panel asks")


def test_the_damage_goal_ranks_a_self_inflicted_penalty_below(game_data,
                                                              wylder):
    """The order, not only the amount -- and they are not the same claim.

    The case above holds that the 0.85 reaches the figure. This holds that it
    reaches the **ranking**, which the project believed for a while it could
    not: `damage.candidate` was said to give the same order because the
    penalty is a constant factor over every candidate. It is not a constant
    factor, because a candidate can bring it with it -- three effects of this
    dataset carry `*AttackPowerRate` 0.85 themselves, and 10 of the 309
    relics on the save the `qa-engineer` measured carry one (QA-101).

    The first assertion is the one that makes the second worth making: it
    checks that the two questions really disagree about this pair. Without it
    the case would pass on any pair whose order the swap happens not to move,
    and an order test whose input cannot see the key is an empty test.
    """
    penalty = cases.effects_raising_rate(
        game_data, wylder, "physicsAttackPowerRate", 1)[0]
    buff = cases.effects_raising_rate(
        game_data, wylder, "physicsAttackRate", 1)[0]
    stronger = cases.effects_raising_attribute(
        game_data, wylder, "Strength", 1)[0]
    starting = next(w for w in game_data["weapons"]
                    if w["id"] == wylder["starting_weapon"])
    reference = types.ReferenceArmament(weapon=starting, tier=1,
                                        slot_index=damage.STARTING_SLOT)

    base, ctx = build_with(game_data, wylder, reference=reference)
    carrying, _ = build_with(game_data, wylder, effect_ids=[penalty, buff],
                             reference=reference)
    plain, _ = build_with(game_data, wylder, effect_ids=[stronger],
                          reference=reference)

    def asked_as_the_goal_asks(build):
        return goals.GOALS["max_damage"].score(build, ctx).value

    def asked_without_a_slot(build):
        return damage.candidate(reference.weapon, reference.tier, build,
                                game_data).final_headline

    slotless = asked_without_a_slot(carrying) - asked_without_a_slot(base)
    slotless_plain = asked_without_a_slot(plain) - asked_without_a_slot(base)
    charged = asked_as_the_goal_asks(carrying) - asked_as_the_goal_asks(base)
    unburdened = asked_as_the_goal_asks(plain) - asked_as_the_goal_asks(base)

    assert slotless > slotless_plain, (
        "asked as an armament in no slot these two come back the other way "
        "round; without that this case cannot tell the two questions apart")
    assert charged < unburdened, (
        "a relic that costs the armament 15 % ranked above one that costs it "
        "nothing, so the goal is not charging the penalty to the candidate "
        "that brought it")


#: The two starting-armament relics `GOAL.md` A25 names, by id: 7120100
#: moves 30 points of physical damage into 33 of fire, 7120400 charges 0.85
#: on every rate for the frost it adds. A closed pair of this dataset, and
#: the ids are what AD-047 measured the conversion on.
FIRE_CONVERSION = 7120100
FROST_STATUS = 7120400


def starting_armament(game_data, hero) -> types.ReferenceArmament:
    """The Nightfarer's own armament in slot 1 -- what AD-038 ranks on.

    At its lowest tier and without rolls, the way `advisorbar.asking_from`
    hands it in. A spell row does not use it: its reference object is the
    start catalyst, which for Revenant is the other hand (AD-052).
    """
    return types.ReferenceArmament(
        weapon=next(w for w in game_data["weapons"]
                    if w["id"] == hero["starting_weapon"]),
        tier=1, slot_index=damage.STARTING_SLOT)


def rate_of(game_data, effect_id: int, field_name: str) -> float:
    """One effect's own multiplier on one field, off the dataset."""
    return cases.effect_by_id(game_data, effect_id)["modifiers"][field_name]


def damage_scores(game_data, hero, carried, *, hit_with="", damage_type=""):
    """The damage figure under one chosen cell, one entry per relic carried.

    `carried` maps a name to the effect ids one candidate brings, and `()` is
    the build that brings nothing -- the base state every gain below is
    measured against. One context per entry, because the two fields of the
    question belong to the question and not to the build (AD-051).
    """
    reference = starting_armament(game_data, hero)
    scores = {}
    for name, effect_ids in carried.items():
        ctx = dataclasses.replace(
            advisor.context(game_data, hero, reference=reference,
                            armament_effect_ids=tuple(effect_ids)),
            hit_with=hit_with, damage_type=damage_type)
        build = evaluate(advisor.problem([advisor.RED]), (), ctx)
        scores[name] = goals.GOALS["max_damage"].score(build, ctx)
    return scores


def test_a_damage_type_ranks_on_that_type_and_turns_the_order_over(game_data,
                                                                   wylder):
    """AD-049 M4: `type:Fire` is another number of the same answer, and it
    ranks another relic first.

    Wylder's own starting armament deals no fire at all, so the base state
    under `type:Fire` is 0.00 -- a ranking and not a fault (OF-53): every
    relic that brings fire then stands above every relic that does not,
    however hard the second one hits.

    **The same case is the regression anchor for AD-047 point 6.** Under
    `All` the conversion relic is worth +1.80 rather than nothing: the figure
    already counts what the deleted scope sentence claimed it left out, and
    it is pinned here to four places so that a change which quietly drops the
    conversion again shows up as a number rather than as a missing sentence.
    """
    attack_only = cases.effects_raising_rate(
        game_data, wylder, "physicsAttackRate", 1)[0]
    carried = {"nothing": (), "fire": (FIRE_CONVERSION,),
               "attack": (attack_only,)}

    everything = damage_scores(game_data, wylder, carried)
    fire = damage_scores(game_data, wylder, carried,
                         damage_type="Fire")

    assert everything["nothing"].value == pytest.approx(122.0506, abs=5e-5)
    assert everything["fire"].value == pytest.approx(123.8506, abs=5e-5), (
        "the starting-armament conversion is not in the figure any more; "
        "AD-047 point 6 deleted the sentence that said so because it is")
    assert fire["nothing"].value == 0.0
    assert fire["fire"].value == pytest.approx(19.80, abs=5e-5)
    assert fire["attack"].value == 0.0

    assert everything["attack"].value > everything["fire"].value
    assert fire["fire"].value > fire["attack"].value, (
        "under one damage type the ranking is the same as under all of "
        "them, so the choice reaches the order of nothing")
    assert fire["fire"].display == "Fire attack rating 19", (
        f"the line names the figure it ranks on: {fire['fire'].display!r}")


def test_a_chosen_type_turns_the_revenants_order_over(game_data):
    """OF-50 (b): the Revenant half of A25, on the armament he really carries.

    Revenant with his own Cursed Claws, 71.63 of 88.65 of it magic: under
    `Magic` a point of Faith beats the fire conversion that beat it under
    `All`. The order and not the figure, because the order is what a
    suggestion is.

    **The incantation half of this case has moved** (AD-052/AD-053): asking
    about incantations is now asking about a spell and no longer about a
    rate on the claws, so it is answered from the seal Revenant carries in
    his left hand, and the cases for it start at
    `test_the_spell_row_rates_the_spell_the_equipment_throws`.
    """
    revenant = cases.hero_by_name(game_data, "Revenant")
    faith = cases.effects_raising_attribute(game_data, revenant, "Faith", 1)[0]
    carried = {"fire": (FIRE_CONVERSION,), "faith": (faith,)}

    everything = damage_scores(game_data, revenant, carried)
    chosen = damage_scores(game_data, revenant, carried, damage_type="Magic")

    assert everything["fire"].value > everything["faith"].value, (
        "under All fire already ranks below faith, so this pair cannot show "
        "that a chosen type turns anything over")
    assert chosen["faith"].value > chosen["fire"].value


#: The relic the A26 proof runs on: "Changes compatible armament's
#: incantation to Beast Claw at start of expedition", the one of the ten
#: swap relics Revenant can hold whose spell carries physical damage
#: (6820, `Physics` 362). The other nine belong to the other genus or to
#: another damage type, and `allowed_heroes` names one Nightfarer for each.
BEAST_CLAW_SWAP = 7370900

#: A second swap relic for the same hand -- "O, Flame!" (6001, `Fire` 351),
#: the case AD-052 point 3 is about.
FLAME_SWAP = 7370600

#: "Improved Bestial Incantations" (scope 23) and "Improved Incantations",
#: which carries no scope of its own and reaches the genus through
#: `model.MOVE_SCOPED_ARTS`. Beast Claw is a Bestial incantation, so both
#: count under `family:23` and only the second under `incantations`
#: (user decision OF-51).
BESTIAL_BUFF = 7044400
INCANTATION_BUFF = 8330100

#: What Revenant's Finger Seal throws with no relic on the build: Rejection
#: hits for nothing, which is the measured state AD-052 point 5 refuses to
#: paper over with a spell-power figure.
REVENANT_DEFAULT_SPELL = "Rejection"

#: Level 15, Finger Seal at tier 1, no relics: 362 physical times the seal's
#: spell power of 159.545 / 100. Pinned to four places because every case
#: below is a factor on it, and because it is the first figure this program
#: shows that no screen of the game can be held against (OF-54).
BEAST_CLAW_FIGURE = 577.5545


def test_the_spell_row_rates_the_spell_the_equipment_throws(game_data):
    """AD-052: N4's first half -- the reference object of a spell row.

    Revenant is the case the criterion names: his starting armament is a
    pair of claws, and the spell row is answered from the **seal in his left
    hand** and the spell that seal casts. Without a swap relic that spell is
    Rejection and it hits for nothing, so the figure is 0.00 with the
    facade's own sentence -- not a spell power standing in for a damage,
    which would put two yardsticks in one ranking (AD-052 point 5, QA-018).

    With the swap relic the same row is the Beast Claw figure, and the
    headline names the spell it was formed on: a player cannot check a
    number whose subject he has to guess (AD-025.2).
    """
    revenant = cases.hero_by_name(game_data, "Revenant")
    carried = {"nothing": (), "claw": (BEAST_CLAW_SWAP,)}

    spell = damage_scores(game_data, revenant, carried,
                          hit_with=model.INCANTATIONS_ART)

    assert spell["nothing"].value == 0.0
    assert REVENANT_DEFAULT_SPELL in spell["nothing"].display
    assert REVENANT_DEFAULT_SPELL in spell["nothing"].unknowns[0], (
        f"a 0.00 has to say whose it is: {spell['nothing'].unknowns!r}")
    assert spell["claw"].value == pytest.approx(BEAST_CLAW_FIGURE, abs=5e-5)
    assert "Beast Claw" in spell["claw"].display
    assert damage.SPELL_DAMAGE_NAME in spell["claw"].display
    assert any("uncalibrated" in line for line in spell["claw"].unknowns), (
        f"OF-54: the figure has to say it is a premise, not a measurement: "
        f"{spell['claw'].unknowns!r}")


def test_a_physical_buff_lifts_the_beast_claw_and_a_holy_one_does_not(
        game_data):
    """N4: the element rates reach a spell, each on its own damage type.

    Beast Claw is physical, so `physicsAttackRate` multiplies it and
    `darkAttackRate` -- what this dataset calls holy -- multiplies nothing
    of it. That is the premise of A26 stated as a measurement rather than as
    a rule written into the goal: the facade does the multiplying per damage
    type, and this case reads the two rows of it apart.
    """
    revenant = cases.hero_by_name(game_data, "Revenant")
    physical = cases.effects_raising_rate(
        game_data, revenant, "physicsAttackRate", 1)[0]
    holy = cases.effects_raising_rate(
        game_data, revenant, "darkAttackRate", 1)[0]
    carried = {"claw": (BEAST_CLAW_SWAP,),
               "claw+physical": (BEAST_CLAW_SWAP, physical),
               "claw+holy": (BEAST_CLAW_SWAP, holy)}

    spell = damage_scores(game_data, revenant, carried,
                          hit_with=model.INCANTATIONS_ART)
    rate = rate_of(game_data, physical, "physicsAttackRate")

    assert spell["claw+physical"].value == pytest.approx(
        spell["claw"].value * rate, abs=5e-5)
    assert spell["claw+holy"].value == pytest.approx(spell["claw"].value), (
        "a holy buff lifted a physical spell, so the rates are not being "
        "read per damage type")


def test_a_school_counts_only_where_the_spell_belongs_to_it(game_data):
    """N4's second half: Bestial counts on Beast Claw, Dragon Cult does not.

    And under the school the genus counts as well, multiplied with it (OF-51,
    `damage._art_of`): a Bestial incantation is an incantation too. Asked
    under `family:22` the same relics reach nothing -- the spell is of
    another school, and the answer is the genus figure rather than an error.
    """
    revenant = cases.hero_by_name(game_data, "Revenant")
    carried = {"claw": (BEAST_CLAW_SWAP,),
               "school": (BEAST_CLAW_SWAP, BESTIAL_BUFF),
               "genus": (BEAST_CLAW_SWAP, INCANTATION_BUFF),
               "both": (BEAST_CLAW_SWAP, BESTIAL_BUFF, INCANTATION_BUFF)}
    school_rate = rate_of(game_data, BESTIAL_BUFF, "physicsAttackRate")
    genus_rate = rate_of(game_data, INCANTATION_BUFF, "physicsAttackRate")

    bestial = damage_scores(game_data, revenant, carried,
                            hit_with=f"{model.ART_FAMILY_PREFIX}23")
    dragon_cult = damage_scores(game_data, revenant, carried,
                                hit_with=f"{model.ART_FAMILY_PREFIX}22")

    assert bestial["school"].value == pytest.approx(
        bestial["claw"].value * school_rate, abs=5e-5)
    assert bestial["both"].value == pytest.approx(
        bestial["claw"].value * school_rate * genus_rate, abs=5e-5), (
        "under a school the genus buff counts beside the school's own, "
        "multiplied (OF-51)")
    assert dragon_cult["school"].value == pytest.approx(
        dragon_cult["claw"].value), (
        "a Bestial buff lifted the figure under Dragon Cult, so the school "
        "is being applied without asking whether the spell belongs to it")
    assert dragon_cult["genus"].value == pytest.approx(
        dragon_cult["claw"].value * genus_rate, abs=5e-5), (
        "asking about a school the spell is not in still leaves it an "
        "incantation, so the genus buff has to reach it")


def test_a_swap_relic_offered_as_a_candidate_is_the_gain_of_the_run(
        game_data):
    """AD-052 point 2: the one effect family that moves a **base** value.

    The reference object of a spell row is chosen from the finished build,
    so a swap relic that is merely offered counts exactly as one that is
    held -- and that is what makes the row rankable at all for Revenant: his
    own equipment throws Rejection for 0.00, and the relic that changes it
    is the only candidate in the pool that moves the figure.

    Asked through `candidates.pool` and not through a score, because the
    claim is about the **gain** a player is shown: a run whose every
    candidate is worth the same suggests nothing (QA-290), and this one has
    to suggest the swap.
    """
    revenant = cases.hero_by_name(game_data, "Revenant")
    physical = cases.effects_raising_rate(
        game_data, revenant, "physicsAttackRate", 1)[0]
    faith = cases.effects_raising_attribute(game_data, revenant, "Faith", 1)[0]
    inventory = advisor.make_inventory(
        game_data, revenant, count=3,
        rolls=[[BEAST_CLAW_SWAP], [physical], [faith], [physical]])
    ctx = dataclasses.replace(
        advisor.context(game_data, revenant,
                        reference=starting_armament(game_data, revenant)),
        hit_with=model.INCANTATIONS_ART)

    pool = candidates.pool(inventory, advisor.problem([advisor.RED]), 0, ctx,
                           goals.GOALS, "max_damage")
    gains = [(offer.name, marginal.gain) for offer in pool.candidates
             for marginal in offer.marginals
             if marginal.goal_id == "max_damage"]

    assert [line.value for line in pool.baseline
            if line.goal_id == "max_damage"] == [0.0], (
        "Revenant's own equipment throws a spell that deals no damage, so "
        "the base state of this row is 0.00")
    assert gains[0][1] == pytest.approx(BEAST_CLAW_FIGURE, abs=5e-5)
    assert all(gain == 0.0 for _, gain in gains[1:]), (
        f"only the swap relic can move a figure that starts at 0.00: "
        f"{gains!r}")


def test_two_swap_relics_rank_the_stronger_and_say_which(game_data):
    """AD-052 point 3: `exclusivityId` 200 on all ten, and no rule for which.

    The game applies one of two swap relics and the files do not say which,
    so the reader takes the stronger under the damage type asked about --
    the one a player would be aiming for -- and says in the run's findings
    that it did. Under `All` that is Beast Claw's 362 physical, under `Fire`
    it is O, Flame!'s 351, and the same pair of relics gives two different
    answers because the question is a different one.
    """
    revenant = cases.hero_by_name(game_data, "Revenant")
    carried = {"both": (BEAST_CLAW_SWAP, FLAME_SWAP)}

    everything = damage_scores(game_data, revenant, carried,
                               hit_with=model.INCANTATIONS_ART)["both"]
    fire = damage_scores(game_data, revenant, carried,
                         hit_with=model.INCANTATIONS_ART,
                         damage_type="Fire")["both"]

    assert "Beast Claw" in everything.display
    assert everything.value == pytest.approx(BEAST_CLAW_FIGURE, abs=5e-5)
    assert "O, Flame!" in fire.display
    assert any("only one of them work" in line
               for line in everything.unknowns), (
        f"the choice between two swap relics is a finding of the run, not "
        f"something done quietly: {everything.unknowns!r}")


def test_the_spell_headline_names_the_damage_type_asked_about(game_data):
    """AK-342's own Pruefweg, and AK-335's rule applied to a spell row.

    Revenant with the Beast Claw relic, asked under `Incantations` x
    `Fire`: the claw deals physical, so the fire row is 0 -- a measured
    ranking figure and not a fault, which is why the headline carries the
    digit and the cell stays out of `_empty_cell`'s "not counted" shape
    (AK-344). The type earns its place in the headline whenever it was
    chosen, so the number is never drawn under a label that omits the
    restriction it was measured with.
    """
    revenant = cases.hero_by_name(game_data, "Revenant")
    carried = {"claw": (BEAST_CLAW_SWAP,)}

    fire = damage_scores(game_data, revenant, carried,
                         hit_with=model.INCANTATIONS_ART,
                         damage_type="Fire")["claw"]

    assert fire.value == 0.0
    assert fire.display == "Fire spell damage (Beast Claw) 0"
    assert len(fire.unknowns) == 1 and "uncalibrated" in fire.unknowns[0], (
        f"a measured zero is a ranking, so the only sentence here is the "
        f"caveat the figure always carries: {fire.unknowns!r}")


def test_a_school_earns_the_spell_headline_only_once_it_moves_the_figure(
        game_data):
    """AK-342, the `hit_with` half: the same test the weapon row uses, read
    against `SpellRating.rates`.

    Asked under `Bestial` with no Bestial buff on the build the figure is
    the `Incantations` figure verbatim, so the headline says nothing about
    the school; with the school's own buff carried it names it. A headline
    naming a school that reached nothing is the false label AK-335 was
    written against.
    """
    revenant = cases.hero_by_name(game_data, "Revenant")
    carried = {"claw": (BEAST_CLAW_SWAP,),
               "school": (BEAST_CLAW_SWAP, BESTIAL_BUFF)}

    bestial = damage_scores(game_data, revenant, carried,
                            hit_with=f"{model.ART_FAMILY_PREFIX}23")

    assert bestial["claw"].display == "Spell damage (Beast Claw) 577"
    assert bestial["school"].display.startswith(
        "Bestial spell damage (Beast Claw) "), (
        f"the school moved the figure, so it names it: "
        f"{bestial['school'].display!r}")
    assert bestial["school"].value > bestial["claw"].value


def test_both_halves_of_the_question_name_the_spell_headline_once(game_data):
    """AK-342's fourth example: damage type before hit with, one label.

    The order is `chosen_label`'s and not this file's, so the goal card, the
    picker caption and the chip cannot drift apart (AK-346).
    """
    revenant = cases.hero_by_name(game_data, "Revenant")
    carried = {"school": (BEAST_CLAW_SWAP, BESTIAL_BUFF)}

    cell = damage_scores(game_data, revenant, carried,
                         hit_with=f"{model.ART_FAMILY_PREFIX}23",
                         damage_type="Physics")["school"]

    assert cell.display.startswith("Physical Bestial spell damage "
                                   "(Beast Claw) ")


@pytest.mark.parametrize("hero_name, hit_with, catalyst", [
    ("Revenant", model.SORCERIES_ART, "Finger Seal"),
    ("Recluse", model.INCANTATIONS_ART, "Recluse's Staff"),
])
def test_a_seal_casts_no_sorceries_and_a_staff_no_incantations(
        game_data, hero_name, hit_with, catalyst):
    """AD-052 point 4: the genus of the catalyst decides, `wep_type` says it.

    The cell is empty rather than 0.00: nothing was measured and nothing
    ranks, so no candidate can outrank another and the run suggests nothing
    here (QA-290). The sentence names the armament, because that is what the
    player can look at.
    """
    hero = cases.hero_by_name(game_data, hero_name)
    carried = {"nothing": (), "claw": (BEAST_CLAW_SWAP,)}

    spell = damage_scores(game_data, hero, carried, hit_with=hit_with)

    assert spell["nothing"].value == spell["claw"].value == 0.0
    assert "0.00" not in spell["nothing"].display
    assert catalyst in spell["nothing"].unknowns[0]
    assert goals.chosen_label(hit_with, "") in spell["nothing"].unknowns[0]


def test_a_nightfarer_without_a_catalyst_has_no_spell_row(game_data, wylder):
    """N5: eight of the ten start with neither a staff nor a seal.

    Wylder's greatsword casts nothing, so the row is empty and says so --
    and a silent 0.00 would be the worse answer of the two, because it reads
    as a measured figure of a spell that was never cast (AD-052 point 6).
    """
    carried = {"nothing": (), "attack": (FIRE_CONVERSION,)}

    spell = damage_scores(game_data, wylder, carried,
                          hit_with=model.SORCERIES_ART)

    assert spell["nothing"].value == spell["attack"].value == 0.0
    assert "0.00" not in spell["nothing"].display
    assert len(spell["nothing"].unknowns) == 1
    assert goals.chosen_label(model.SORCERIES_ART, "") in \
        spell["nothing"].unknowns[0]


def test_recluse_is_ranked_on_the_pebble_her_own_staff_carries(game_data):
    """AD-052 point 1: the catalyst in the **right** hand, and its own spell.

    Recluse is the other half of the pair: her staff is her starting
    armament, so the spell row and the weapon row are formed on the same
    armament and still answer two different questions -- the staff's spell
    power under `Weapon` (AD-048) and Glintstone Pebble's magic damage here.
    """
    recluse = cases.hero_by_name(game_data, "Recluse")
    magic = cases.effects_raising_rate(game_data, recluse, "magicAttackRate",
                                       1)[0]
    carried = {"nothing": (), "magic": (magic,),
               "claw": (BEAST_CLAW_SWAP,)}

    spell = damage_scores(game_data, recluse, carried,
                          hit_with=model.SORCERIES_ART, damage_type="Magic")
    rate = rate_of(game_data, magic, "magicAttackRate")

    assert "Glintstone Pebble" in spell["nothing"].display
    assert spell["nothing"].value == pytest.approx(206.1327, abs=5e-5)
    assert spell["magic"].value == pytest.approx(
        spell["nothing"].value * rate, abs=5e-5)
    assert spell["claw"].display == spell["nothing"].display, (
        "a swap relic of the other genus reached a staff: each of the ten "
        "works for one Nightfarer only (`allowed_heroes`), which is what "
        "keeps a sorcery off a seal and an incantation off a staff")


def test_the_starting_armament_pair_keeps_its_conversion_under_an_art(
        game_data, wylder):
    """`GOAL.md` A25, second half: Wylder with both starting-armament relics
    and `Weapon art` chosen counts the conversion in the damage figure.

    The pair is what the criterion asks for, and what the dataset does with
    it is worth saying: the two relics claim the same attribute on the
    armament, so the figure carries the conversion and not the frost penalty
    -- 123.85 and not 103.74. Either way the point of the case holds:
    choosing an art does not put the figure back on a state where the
    conversion is missing.
    """
    carried = {"nothing": (), "pair": (FIRE_CONVERSION, FROST_STATUS)}

    skill = damage_scores(game_data, wylder, carried,
                          hit_with="skill")

    assert skill["nothing"].value == pytest.approx(122.0506, abs=5e-5)
    assert skill["pair"].value == pytest.approx(123.8506, abs=5e-5)


#: "Improved Skill Attack Power": scope 112, +15 % on every element rate
#: while a Weapon Art is out -- the one effect of this dataset that moves
#: `art_rate` away from 1.0 for `art:skill` (`model.SKILL_SCOPES`).
SKILL_ATTACK_BUFF = 312300


def test_an_art_choice_that_leaves_the_value_unmoved_keeps_the_all_headline(
        game_data, wylder):
    """AK-335: an art choice earns the headline only once it actually moves
    the figure. No relic here scopes a buff to `Weapon art`, so `art_rate`
    stays 1.0 and the figure is the `All` figure verbatim -- the headline
    says so by staying `Attack rating` rather than claiming a difference
    that is not there.
    """
    carried = {"nothing": ()}

    skill = damage_scores(game_data, wylder, carried,
                          hit_with="skill")["nothing"]

    assert skill.display.startswith("Attack rating"), (
        f"art_rate is 1.0 here, so the headline must not change: "
        f"{skill.display!r}")


def test_an_art_choice_that_moves_the_value_earns_the_headline(game_data,
                                                                wylder):
    """AK-335: the art counterpart of DR-034's type fix. Once a relic scopes
    a buff to the chosen art (`art_rate != 1.0`), the headline names the
    choice exactly as a type does -- since AK-338 in the entry's new
    wording, `Weapon art`, which shares no word with `attack rating` and is
    therefore written out in full beside it.
    """
    carried = {"nothing": (), "buffed": (SKILL_ATTACK_BUFF,)}

    everything = damage_scores(game_data, wylder, carried)
    skill = damage_scores(game_data, wylder, carried,
                          hit_with="skill")

    assert skill["buffed"].value != pytest.approx(everything["buffed"].value), (
        "this case needs a buff that actually moves art_rate for `skill`, "
        "or it cannot show AK-335's condition is met")
    assert skill["buffed"].display.startswith("Weapon art attack rating"), (
        f"the headline names the entry as the box shows it: "
        f"{skill['buffed'].display!r}")
    assert "Skill attack" not in skill["buffed"].display


def test_an_art_and_a_type_are_combined_exactly_once(game_data, wylder):
    """AD-051 point 3, the cell A25 could not express: `hit_with="skill"`
    **and** `damage_type="Fire"` together.

    The facade multiplies the art per damage type already, so the cell is
    the fire row of that answer and nothing is multiplied a second time. The
    case holds it as a relation rather than as a literal: the art moves the
    fire row by exactly the factor it moves the headline -- once, not
    squared -- and the fire row is not the row the armament alone has.

    Wylder's own armament deals no fire, so the conversion relic is what
    puts fire in the figure at all and the skill buff is what makes
    `art_rate` differ from 1.0 (`model.SKILL_SCOPES`).
    """
    carried = {"both": (FIRE_CONVERSION, SKILL_ATTACK_BUFF)}

    everything = damage_scores(game_data, wylder, carried)["both"]
    art = damage_scores(game_data, wylder, carried,
                        hit_with="skill")["both"]
    fire = damage_scores(game_data, wylder, carried,
                         damage_type="Fire")["both"]
    cell = damage_scores(game_data, wylder, carried, hit_with="skill",
                         damage_type="Fire")["both"]

    factor = art.value / everything.value
    assert factor > 1.0, (
        "this case needs a buff that moves `art_rate` for `skill`, or it "
        "cannot tell one application from two")
    assert cell.value == pytest.approx(fire.value * factor, abs=5e-5)
    assert cell.value != pytest.approx(fire.value * factor * factor,
                                       abs=5e-5)
    assert cell.display.startswith("Fire Weapon art attack rating"), (
        f"the cell names both halves of the question: {cell.display!r}")


def test_the_chosen_kind_is_named_in_the_run_findings_and_only_then(game_data,
                                                                    wylder):
    """AK-331: one sentence, with the entry's own label, first letter lowered.

    A run finding rather than a scope sentence, because whether it holds is
    settled by the question that was asked (AD-025.2) -- and exactly one, so
    that the dialog does not say the same thing twice.
    """
    carried = {"nothing": ()}

    everything = damage_scores(game_data, wylder, carried)["nothing"]
    holy = damage_scores(game_data, wylder, carried,
                         damage_type="Dark")["nothing"]
    art = damage_scores(game_data, wylder, carried,
                        hit_with="skill")["nothing"]

    assert everything.unknowns == (), (
        "a run that was asked about every kind of damage says so by having "
        "nothing to report, not by a sentence")
    assert holy.unknowns == (
        "Ranked on holy damage only — every other effect on a candidate "
        "still shows, but only this counts toward the ranking. It scales "
        "the armament's attack rating; what a spell hits for is a figure of "
        "its own and is asked for on the spell rows.",)
    assert art.unknowns[0].startswith("Ranked on weapon art damage only")


def test_a_type_and_an_art_together_keep_the_arts_own_capital(game_data,
                                                               wylder):
    """DR-038: joining `chosen_label`'s two labels and then lowering only the
    chain's first character left the art's capital stranded mid-sentence
    (`"Ranked on fire Weapon art damage only"`) whenever both fields were
    chosen -- a combination AK-341 names as ordinary, not a corner case.
    `_ranked_on_choice` lowers only the type and leaves the art's label
    exactly as `ART_LABELS` spells it, joined by "with".
    """
    carried = {"nothing": ()}

    both = damage_scores(game_data, wylder, carried, hit_with="skill",
                         damage_type="Fire")["nothing"]

    assert both.unknowns[0].startswith(
        "Ranked on fire damage with Weapon art only"), (
        f"the type is lowered and the art's own label is not: "
        f"{both.unknowns[0]!r}")


def test_a_type_and_a_school_are_cased_the_same_way(game_data):
    """The same DR-038 rule, for a school's own name rather than one of the
    three spec-worded arts (AK-338's `Weapon art` among them).

    Asked through `max_damage`, a school routes to `_spell_cell` instead
    (AD-052: `Bestial` names a spell row, never the armament row this
    sentence belongs to) and never reaches `_RANKED_ON_ONE_ART`, so the only
    way to hold the school case to the same rule is `_ranked_on_choice`
    itself.
    """
    bestial = f"{model.ART_FAMILY_PREFIX}23"

    assert goals._ranked_on_choice(bestial, "Fire") == (
        "fire damage with Bestial")


def test_a_catalyst_says_the_choice_reaches_nothing(game_data):
    """AD-048: Recluse's staff is ranked on spell power, and no kind of
    damage reaches that figure -- so the run says so instead of applying a
    relationship nobody has measured (A7).

    The figure itself is the one it would be under `All`, down to the last
    bit: the choice changes the sentence, not the number.

    **The question is the weapon one** since AD-053 point 5 narrowed AD-048
    to it: asked about the staff (`hit_with=""`) under one damage type, this
    is the sentence, word for word. Asked about sorceries the question is
    about a spell and is answered elsewhere.
    """
    recluse = cases.hero_by_name(game_data, "Recluse")
    carried = {"nothing": ()}

    everything = damage_scores(game_data, recluse, carried)["nothing"]
    fire = damage_scores(game_data, recluse, carried,
                         damage_type="Fire")["nothing"]

    assert everything.unit == damage.SPELL_POWER_LABEL, (
        "this case needs a Nightfarer whose starting armament is a "
        "catalyst; this one is ranked on an attack rating")
    assert fire.value == everything.value
    assert fire.unknowns == (
        "Fire is not counted for this Nightfarer: a staff or a seal is "
        "ranked on the spell power the game shows for it, and no damage type "
        "and no attack art reaches that figure.",)


def test_a_kind_this_dataset_cannot_name_is_refused(game_data, wylder):
    """A choice the program cannot name is no choice a player could have
    made, and ranking on it silently would be the invented label AD-046
    point 5 keeps out of the chooser, arriving through the back door."""
    with pytest.raises(ValueError, match="names no damage type"):
        damage_scores(game_data, wylder, {"nothing": ()},
                      hit_with="family:999999")
    with pytest.raises(ValueError, match="names no damage type"):
        damage_scores(game_data, wylder, {"nothing": ()},
                      damage_type="Sunlight")


def test_without_an_armament_the_damage_goal_still_orders_two_builds(
        game_data, wylder):
    """A17: the armament-free figure is an **order**, not just a fallback.

    What this case asserted until T-188 was the sentence beside the figure --
    "No armament selected" and an empty unit -- and that was the right claim
    while the branch was OF-5's way out of a run with no weapon in the slot.
    Since A17 it is the figure the program ranks by whatever is in the slot,
    so the claim worth holding here is the one a ranking stands on: more
    attack multiplier is more of it.

    The wording of the line beside it is AK-190's, is about to change with
    it, and is deliberately not asserted here -- a case holding both would
    have to be rewritten again for a change that does not touch this claim.
    """
    buff = cases.effects_raising_rate(game_data, wylder, "physicsAttackRate")
    plain, ctx = build_with(game_data, wylder)
    buffed, _ = build_with(game_data, wylder, effect_ids=buff)

    assert ctx.reference is None, (
        "this case is about the figure formed without an armament, so the "
        "context may not carry one")
    assert goals.GOALS["max_damage"].score(buffed, ctx).value > \
        goals.GOALS["max_damage"].score(plain, ctx).value


#: `Reduced Intelligence and Dexterity` (Dex -3, Int -3): the curse of the
#: user's own A22 proof, on a Nightfarer whose dagger scales on Dexterity.
REDUCED_INTELLIGENCE_AND_DEXTERITY = 6830200


def test_an_attribute_curse_lowers_the_figure_through_the_starting_armament(
        planner, game_data):
    """`GOAL.md` A22 through the program's own door (AD-038).

    Duchess at level 15 with her starting armament hits for 72; holding a
    relic that carries Dex -3 she hits for 70. Literals, not a comparison of
    two computed figures: the two are the user's in-game reading (AD-038,
    measured on the v12 extract), and a figure that fell to anything else
    would be a scaling this program invented. The context is what
    `asking_from` asks, so this goes red when the starting armament leaves
    the question again.
    """
    if planner.owned is None:
        pytest.skip("`asking_from` answers nothing without a save to choose "
                    "relics from")
    planner.select_hero(planner.heroes.index(
        cases.hero_by_name(game_data, "Duchess")))
    planner.level_slider.setValue(advisor.LEVEL)
    ctx = advisorbar.asking_from(planner, "max_damage").ctx
    cursed = types.HeldRelic(
        relic_id=0, name="a relic with the curse",
        curse_ids=(REDUCED_INTELLIGENCE_AND_DEXTERITY,))

    plain = evaluate(advisor.problem([advisor.RED]), (), ctx)
    with_curse = evaluate(advisor.problem([advisor.RED], held={0: cursed}),
                          (), ctx)

    score = goals.GOALS["max_damage"].score
    assert damage.displayed(score(plain, ctx).value) == 72
    assert damage.displayed(score(with_curse, ctx).value) == 70


# -- the third direction: attribute points (AD-032 option C) ----------------

ATTRIBUTES = "max_attributes"


def test_the_offensive_attributes_are_the_ones_armaments_scale_on(game_data):
    """AD-032 named five; the dataset is asked whether it still knows five.

    `goals.OFFENSIVE_ATTRIBUTES` is a decision written out by hand, which is
    right -- which attributes an "offensive" direction counts is not a
    reading of the files -- and it is a decision that can go stale. The
    files can say one thing about it: which attributes an armament's damage
    actually scales on. Today the two agree exactly, and this is where the
    day they stop agreeing becomes loud instead of invisible.

    A mis-spelled entry would be caught here as well, and by nothing else:
    `build.attributes.get("Strenght", 0)` is 0 and adds up perfectly.
    """
    scaled_on = {stat for weapon in game_data["weapons"]
                 for stat, coefficient in (weapon.get("scaling") or {}).items()
                 if coefficient}

    assert set(goals.OFFENSIVE_ATTRIBUTES) == scaled_on, (
        f"the registry counts {sorted(goals.OFFENSIVE_ATTRIBUTES)} as the "
        f"offensive attributes, the armaments of this dataset scale on "
        f"{sorted(scaled_on)}")
    assert set(goals.OFFENSIVE_ATTRIBUTES) <= set(model.ATTRIBUTE_ORDER)


def test_the_attribute_goal_counts_the_points_and_not_a_conversion(game_data,
                                                                   wylder):
    """The figure is the sum of five numbers off the build, to the point.

    Stated as an equality rather than as "it goes up", because what AD-032
    chose is precisely the unweighted sum: any weighting by scaling, however
    defensible, is Option B reached the long way round and is the invented
    exchange rate AD-023 and OF-13 forbid. An equality is the only assertion
    that a later weight could not slip past.
    """
    stronger = cases.effects_raising_attribute(game_data, wylder, "Strength",
                                               1)
    raised, ctx = build_with(game_data, wylder, effect_ids=stronger)
    said = goals.GOALS[ATTRIBUTES].score(raised, ctx)

    assert said.value == float(sum(raised.attributes[attribute]
                                   for attribute
                                   in goals.OFFENSIVE_ATTRIBUTES))
    assert said.unit == goals.ATTRIBUTE_POINT_UNIT
    assert f"{said.value:.0f}" in said.display, said.display


def test_the_attribute_goal_rises_with_the_points_a_relic_brings(game_data,
                                                                 wylder):
    """The direction of the direction: more offensive points is more of it.

    Against the build with no relic at all, which is the base state every
    marginal contribution is formed against -- so this is the same
    subtraction the pool does, asked of one candidate.
    """
    stronger = cases.effects_raising_attribute(game_data, wylder, "Strength",
                                               1)
    plain, ctx = build_with(game_data, wylder)
    raised, _ = build_with(game_data, wylder, effect_ids=stronger)

    assert goals.GOALS[ATTRIBUTES].score(raised, ctx).value > \
        goals.GOALS[ATTRIBUTES].score(plain, ctx).value


def test_the_attribute_goal_leaves_the_other_three_attributes_alone(game_data,
                                                                    wylder):
    """Vigor, Mind and Endurance are outside the figure, and it says so.

    The scope line claims it in words; this is the same claim as a number.
    A relic that raises Vigor is a real relic and a real gain -- it is what
    the survival direction is for -- and counting it here would make the two
    directions two names for one figure.
    """
    tougher = cases.effects_raising_attribute(game_data, wylder, "Vigor", 1)
    plain, ctx = build_with(game_data, wylder)
    raised, _ = build_with(game_data, wylder, effect_ids=tougher)

    assert raised.attributes["Vigor"] > plain.attributes["Vigor"], (
        "this effect does not raise Vigor in this dataset, so the case "
        "below would hold whatever the goal counted")
    assert goals.GOALS[ATTRIBUTES].score(raised, ctx).value == \
        goals.GOALS[ATTRIBUTES].score(plain, ctx).value
    assert goals.GOALS["min_damage_taken"].score(raised, ctx).value > \
        goals.GOALS["min_damage_taken"].score(plain, ctx).value


def test_the_attribute_points_are_not_a_summand_of_the_damage_figure(
        game_data, wylder):
    """AD-032's first vote, as a property: two figures, not one mixed one.

    The repair this forbids is the one T-189 told the `developer` not to
    make -- adding attribute points into `_max_damage` so that the 184 zeros
    go away. Without an armament there is nothing for a point to scale, so
    the damage figure has to stay exactly where it was while the attribute
    figure moves; a mixed figure would move both.
    """
    stronger = cases.effects_raising_attribute(game_data, wylder, "Strength",
                                               1)
    plain, ctx = build_with(game_data, wylder)
    raised, _ = build_with(game_data, wylder, effect_ids=stronger)

    assert ctx.reference is None, (
        "with an armament in the context the damage figure scales on the "
        "attributes by design, and this case would be about the wrong branch")
    assert goals.GOALS["max_damage"].score(raised, ctx).value == \
        goals.GOALS["max_damage"].score(plain, ctx).value, (
        "the attribute points reached the damage figure: AD-032 put them in "
        "a direction of their own precisely so that they would not")
    assert goals.GOALS[ATTRIBUTES].score(raised, ctx).value > \
        goals.GOALS[ATTRIBUTES].score(plain, ctx).value


def test_the_third_direction_is_named_and_stands_last(game_data):
    """AK-257: the wording of the third entry, and where it stands.

    **This case replaces `test_the_third_direction_is_scored_but_not_yet_
    offered`**, which held the opposite -- that the direction was scored and
    deliberately not offered (T-191). T-194 offers it, so the old case is
    not turned round but struck: two guards that contradict each other are
    worse than one, and what it guarded is now AK-256 point 1 in
    `test_advisor_bar.py`.

    The wording is a literal here because `UI_SPEC.md` AK-257 writes it out
    and this is the file that holds the registry against the spec. Nothing
    in `relicpicker` or `advisorbar` may carry it a second time -- that is
    AK-256 point 2, and `test_no_direction_label_is_written_into_a_control`
    is where it is measured.

    `Maximise attributes` is the wording this rules out: the direction counts
    five of the eight attributes, and the short name promises eight.
    """
    assert goals.GOALS[ATTRIBUTES].label == "Maximise offensive attributes"
    assert advisorbar.GOAL_ORDER[-1] == ATTRIBUTES, (
        "the third direction does not stand behind the pair of GOAL.md A3, "
        "so the second value row of every card has moved (AK-258)")
    assert advisorbar.GOAL_ORDER[:2] == ("max_damage", "min_damage_taken")


def test_no_direction_label_is_written_into_a_control(game_data):
    """AK-256 point 2: the words live in the registry and nowhere else.

    Read out of the source rather than off a widget, because the fault this
    rules out is a second copy that happens to agree today. Docstrings and
    module comments are not part of it: `advisorbar._lower_case_first`
    explains itself with `Maximise damage`, and a rule that forbade an
    example in prose would buy nothing -- what reaches a player is a string
    the code evaluates, and that is what is walked here.
    """
    import ast
    import pathlib

    labels = {goal.label for goal in goals.GOALS.values()}
    root = pathlib.Path(advisorbar.__file__).parent
    for name in ("advisorbar.py", "relicpicker.py"):
        path = root / name
        tree = ast.parse(path.read_text(encoding="utf-8"))
        holders = (ast.Module, ast.ClassDef, ast.FunctionDef,
                   ast.AsyncFunctionDef)
        docstrings = set()
        for node in ast.walk(tree):
            first = node.body[0] if isinstance(node, holders) and node.body                 else None
            if (isinstance(first, ast.Expr)
                    and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)):
                docstrings.add(id(first.value))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Constant):
                continue
            if not isinstance(node.value, str) or id(node) in docstrings:
                continue
            for label in labels:
                assert label not in node.value, (
                    f"{name} line {node.lineno} writes {label!r} down; the "
                    f"control is to take it from goals.GOALS[...].label")


#: The five attack multipliers, as the damage facade accounts for them.
#: `goals._max_damage` averages exactly these when it ranks without an
#: armament, so a weapon-type gate that moves none of them cannot tell two
#: armaments apart, and the two cases below would hold vacuously on one.
AR_RATE_FIELDS = tuple(sorted(field_name
                              for field_names in damage.AR_RATE_FOR.values()
                              for field_name in field_names))


def armament_gates(game_data, hero, count: int = 2):
    """`count` (effect id, armament) pairs, each gated on its own weapon type.

    AK-191 names a Greatsword against a Bow as its sample. The pair here is
    **found** rather than written down: a weapon type is a number in the game
    files, and pinning 5 and 51 would leave this case quietly comparing an
    armament with itself the day they move -- the one failure a case about
    invariance cannot notice, because everything it asserts would still hold.

    Measured through `model.compute`, never read off a modifier name, the way
    `advisor_cases.an_armament_type_gate` does it. The dataset gives the
    reason: "Improved Attack Power with 3+ Greatswords Equipped" carries the
    same weapon-type gate as "Improved Greatsword Attack Power" and a gate on
    the **count** on top, so it stays conditional whatever is held and moves
    nothing at all. An effect is taken only where holding its own type moves
    the five multipliers and holding another type does not.

    Lowest effect id per type, types in ascending order, so two runs over one
    dataset pick the same pair.
    """
    an_armament_of = {}
    for weapon in game_data["weapons"]:
        an_armament_of.setdefault(weapon.get("wep_type"), weapon)
    an_armament_of.pop(None, None)
    curves = game_data.get("curves", {})

    def multipliers(effect, held):
        build = model.compute(hero, advisor.LEVEL, [effect], curves,
                              weapons_held=[held])
        return [build.rates.get(field_name, 1.0)
                for field_name in AR_RATE_FIELDS]

    found = {}
    for key in sorted(game_data["effects"], key=int):
        effect = game_data["effects"][key]
        modifiers = effect.get("modifiers") or {}
        wanted = next((modifiers[field_name]
                       for field_name in model.WEAPON_TYPE_GATES
                       if field_name in modifiers), None)
        if wanted in found or wanted not in an_armament_of:
            continue
        elsewhere = next(weapon for wep_type, weapon in an_armament_of.items()
                         if wep_type != wanted)
        if multipliers(effect, an_armament_of[wanted]) != \
                multipliers(effect, elsewhere):
            found[wanted] = (int(effect["id"]), an_armament_of[wanted])
        if len(found) == count:
            return [found[wep_type] for wep_type in sorted(found)]
    pytest.skip(f"this dataset has fewer than {count} weapon-type gates that "
                f"move the attack multipliers")


def an_inventory_telling_two_armaments_apart(game_data, hero):
    """Four copies, two of which are worth something only to one armament.

    The two AK-191 measured on -- `Deep Polished Drizzly Scene` with
    `Improved Greatsword Attack Power` and `Grand Luminous Scene` with
    `Improved Bow Attack Power` -- are two copies of the player's save
    carrying one gated effect each. This is that shape, stated: two copies
    whose worth depends on what is held and two whose worth does not, so an
    order over them is a claim about both kinds at once.
    """
    gates = armament_gates(game_data, hero)
    rolls = [[effect_id] for effect_id, _armament in gates]
    rolls += advisor.raising_effects(game_data, hero, 3)
    inventory = advisor.make_inventory(game_data, hero, colour=advisor.RED,
                                       count=4, rolls=rolls)
    return inventory, [armament for _effect_id, armament in gates]


def ranking_with(planner, armament, inventory, question, rank_by, *,
                 rolls: tuple[int, ...] = (),
                 as_the_bar_asked_before_a16: bool = False,
                 as_the_bar_asked_before_a17: bool = False,
                 as_the_bar_asked_before_ad_032: bool = False):
    """What the pre-sort makes of one inventory while this armament is held.

    The context comes out of `advisorbar.asking_from`, because that is where
    the program decides what a run is asked about. A context assembled here
    would be this file agreeing with itself, and the fields A17 moves are
    exactly the ones such a copy would restate.

    `rolls` are the buffs this armament rolled, put in the slot the way the
    weapon panel puts them there -- so a case about them goes through the
    same reading `asking_from` does, rather than around it.

    The `as_the_bar_asked_before_*` flags put back what the decisions took
    out or in: A17 the reference armament and the grid, AD-032 the rolls on
    it, A16 the advisor's own defaults -- today the A18 baseline (the bar
    asked with the player's declarations alone before). Each is the counter-case of an invariance,
    not a second way of asking for it -- and each has to be restorable by
    hand, or the invariance could be holding because nothing in the case can
    tell two runs apart.
    """
    slots = [weaponslots.WeaponSlot() for _ in range(weaponslots.SLOT_COUNT)]
    slots[0] = weaponslots.WeaponSlot(weapon=armament,
                                      effect_ids=list(rolls))
    planner.weapon_slots = slots
    planner.active_weapon = 0

    ctx = advisorbar.asking_from(planner, rank_by).ctx
    if as_the_bar_asked_before_a16:
        ctx = dataclasses.replace(
            ctx, declared=tuple(sorted(planner.declared.items())))
    if as_the_bar_asked_before_a17:
        ctx = dataclasses.replace(
            ctx,
            reference=types.ReferenceArmament(weapon=armament,
                                              tier=slots[0].tier,
                                              slot_index=0),
            weapons_held=(armament,))
    if as_the_bar_asked_before_ad_032:
        ctx = dataclasses.replace(ctx, armament_effect_ids=tuple(rolls))
    pool = candidates.pool(inventory, question, 0, ctx, goals.GOALS, rank_by)
    return (tuple((line.goal_id, line.value) for line in pool.baseline),
            tuple((offer.name, offer.handle,
                   tuple((marginal.goal_id, marginal.gain)
                         for marginal in offer.marginals))
                  for offer in pool.candidates))


def test_the_ranking_does_not_depend_on_the_armament_held(planner, game_data):
    """AK-191: two runs differing only in the armament rank alike.

    The armaments and the buffs on them are rolled again every expedition, so
    they are not what a relic is worth optimising against (`GOAL.md` A17).
    The figures and the order therefore have to come out the same whichever
    armament is in the slot -- for **both** directions, which is why the pool
    is asked once under each and the whole answer compared rather than the
    head of it.

    **Leaving the reference armament out is not enough**, and that is the
    half this case is written for: a weapon-type gate is met by anything on
    the grid, so a run with `weapons_held` still filled goes on counting
    "Improved Greatsword Attack Power" for a greatsword and not for a bow.
    AK-191 measured that as 2 of 309 copies changing their figure, with the
    order differing from rank 0;
    `test_the_armament_moved_the_ranking_before_a17` is that counter-case
    here.

    The survival direction is asserted and **cannot** be moved by the
    armament in this dataset: of the effects carrying a weapon-type gate,
    three touch a damage-cut field and all three demand `wep_type` 256, which
    no armament in the extraction carries (`explain._Armaments`). It is held
    all the same, because AK-191 asks for both directions and because an
    effect that did reach it would otherwise arrive unnoticed.
    """
    if planner.owned is None:
        pytest.skip("`asking_from` answers nothing without a save to choose "
                    "relics from")
    hero = planner.current_hero()
    inventory, armaments = an_inventory_telling_two_armaments_apart(game_data,
                                                                    hero)
    question = advisor.problem([advisor.RED, advisor.RED])
    first, second = armaments

    assert first.get("wep_type") != second.get("wep_type"), (
        "both runs would hold the same kind of armament, so there is nothing "
        "for the ranking to depend on")

    for rank_by in sorted(goals.GOALS):
        assert ranking_with(planner, first, inventory, question, rank_by) == \
            ranking_with(planner, second, inventory, question, rank_by), (
            f"ranked by {rank_by}, swapping the armament in the slot moved "
            f"the answer: the run is still asked about what the player "
            f"happens to be carrying (AK-191)")


def test_the_armament_moved_the_ranking_before_a17(planner, game_data):
    """The counter-case the invariance above is worth anything against.

    Same inventory, same slot, same two armaments -- and the context of the
    Advisor bar as it stood before A17, with the reference armament and the
    grid put back by hand. If this came back equal, neither the pair of
    armaments nor the four copies could tell the two runs apart, and the case
    above would hold for a reason that has nothing to do with A17.

    Only the damage direction: the survival figure is not reachable by a
    weapon-type gate in this dataset, so ranking by it would come back equal
    here as well and prove the opposite of what this case is for.

    Before the A18 baseline as well: with every weapon-type gate declared
    met (AD-036.6) the armament has nothing left to decide, so the two runs
    could not differ for the reason this case is about.
    """
    if planner.owned is None:
        pytest.skip("`asking_from` answers nothing without a save to choose "
                    "relics from")
    hero = planner.current_hero()
    inventory, armaments = an_inventory_telling_two_armaments_apart(game_data,
                                                                    hero)
    question = advisor.problem([advisor.RED, advisor.RED])
    first, second = armaments

    _baseline_first, order_first = ranking_with(
        planner, first, inventory, question, "max_damage",
        as_the_bar_asked_before_a16=True, as_the_bar_asked_before_a17=True)
    _baseline_second, order_second = ranking_with(
        planner, second, inventory, question, "max_damage",
        as_the_bar_asked_before_a16=True, as_the_bar_asked_before_a17=True)

    # By handle as well as by name: `relics.templates_for` hands out four
    # copies of one relic name, so a list of names alone is the same list
    # whatever order the copies are in.
    assert [offer[:2] for offer in order_first] != \
        [offer[:2] for offer in order_second], (
        "asked the way the Advisor bar asked before A17, these two armaments "
        "give the same order, so this inventory cannot see the difference "
        "A17 removes")


def a_stacking_rate_effect(game_data, hero, field_name: str) -> int:
    """An effect that moves `field_name` and that the game **does** stack.

    The other half of `advisor_cases.a_non_stacking_effect`, and needed for
    the same reason: whether an effect stacks is a field on the record, and
    a case that wants one of each may not take "it is not the non-stacking
    one" as proof that this one stacks.
    """
    for effect_id in cases.effects_raising_rate(game_data, hero, field_name,
                                                count=6):
        if game_data["effects"][str(effect_id)].get("stacks"):
            return effect_id
    pytest.skip(f"this dataset has no stacking effect moving {field_name}")


def an_inventory_the_rolls_can_tell_apart(game_data, hero):
    """Four copies, one of which is worth nothing beside a particular roll.

    The sharp shape of QA-226, stated rather than hoped for. A
    **non-stacking** effect is worth once whatever else carries it, so the
    copy that brings it is worth nothing beside an armament that rolled the
    same effect and worth its full figure beside one that did not -- while
    the copy carrying a **stacking** rate effect is worth something either
    way and the two Strength copies are worth nothing to the damage figure
    and something to the attribute figure. An order over the four is
    therefore a claim about all three directions at once.

    Which effect stacks and which does not is asked of `model.compute`
    (`advisor_cases.a_non_stacking_effect`), never read off a name: QA-226
    counted six non-stacking effects moving an attack rate in this dataset,
    and this picks whichever of them the dataset offers for the physical
    rate, so the case cannot quietly start comparing two stacking ones.
    """
    non_stacking = advisor.a_non_stacking_effect(game_data, hero,
                                                 "physicsAttackRate")
    stacking = a_stacking_rate_effect(game_data, hero, "physicsAttackRate")
    strength = advisor.raising_effects(game_data, hero, 2)
    rolls = [[stacking]] + strength + [[non_stacking], [non_stacking]]
    inventory = advisor.make_inventory(game_data, hero, colour=advisor.RED,
                                       count=4, rolls=rolls)
    return inventory, non_stacking, stacking


def test_the_ranking_does_not_depend_on_the_rolls_on_the_armament(planner,
                                                                  game_data):
    """AK-191 word for word: the *buffs* on the armament move nothing either.

    The decision A17 rests on names them in the same breath as the armament
    -- *"waffen **und deren buffs** sind alle in der runde RNG-basiert"* --
    and until AD-032 they were still in every build
    (`evaluate.effect_ids_of`). T-189 measured what that cost: a stacking
    roll moved 10 of 210 figures and no place in the order, a non-stacking
    one moved the order from rank 3 (QA-226). The first is a common factor,
    the second is not, and this case is written on the second.

    Two runs that differ in the armament **and** in what it rolled. They
    have to come back identical -- same figures, same order, under every
    direction in the registry, which is what the loop is for and why the
    whole answer is compared rather than the head of it.
    """
    if planner.owned is None:
        pytest.skip("`asking_from` answers nothing without a save to choose "
                    "relics from")
    hero = planner.current_hero()
    inventory, non_stacking, stacking = an_inventory_the_rolls_can_tell_apart(
        game_data, hero)
    armaments = [armament for _effect_id, armament
                 in armament_gates(game_data, hero)]
    question = advisor.problem([advisor.RED, advisor.RED])
    first, second = armaments

    for rank_by in sorted(goals.GOALS):
        assert ranking_with(planner, first, inventory, question, rank_by,
                            rolls=(non_stacking,)) == \
            ranking_with(planner, second, inventory, question, rank_by,
                         rolls=(stacking,)), (
            f"ranked by {rank_by}, swapping the armament and the buffs it "
            f"rolled moved the answer: the run is still asked about what the "
            f"expedition happened to roll (AK-191, QA-226)")


def asking_with(planner, armament, rolls: tuple[int, ...]):
    """What the Advisor bar would ask with this armament in slot 1."""
    slots = [weaponslots.WeaponSlot() for _ in range(weaponslots.SLOT_COUNT)]
    slots[0] = weaponslots.WeaponSlot(weapon=armament, effect_ids=list(rolls))
    planner.weapon_slots = slots
    planner.active_weapon = 0
    return advisorbar.asking_from(planner, "max_damage")


def test_the_cache_key_does_not_know_the_armament_or_its_rolls(planner,
                                                               game_data):
    """The other half of AD-032, and the one no ranking can show (P-1).

    Two runs that compute the same answer must not be filed under two keys.
    Until AD-032 the request carried the armaments and their rolls, so
    swapping a weapon threw away an answer that was still correct and paid
    for a second search to get the same list back -- invisible from any
    figure, because both lists are right.

    The two halves have to go together, which is the second thing asserted
    here: `run._refuse_a_request_that_asks_about_another_run` compares the
    rolls in the key against the rolls in the context, so a request that
    still carried them beside a context that no longer did would refuse
    every question the player asked.
    """
    if planner.owned is None:
        pytest.skip("`asking_from` answers nothing without a save to choose "
                    "relics from")
    hero = planner.current_hero()
    inventory, non_stacking, stacking = an_inventory_the_rolls_can_tell_apart(
        game_data, hero)
    first, second = [armament for _effect_id, armament
                     in armament_gates(game_data, hero)]

    one = asking_with(planner, first, (non_stacking,))
    other = asking_with(planner, second, (stacking,))

    assert one.request == other.request, (
        "the cache key still separates two runs that are asked the same "
        "question, so the second one pays for a search whose answer was "
        "already there (P-1)")
    for asking in (one, other):
        assert asking.request.armaments == ()
        assert asking.ctx.armament_effect_ids == ()
        assert tuple(effect_id for armament in asking.request.armaments
                     for effect_id in armament.effect_ids) \
            == asking.ctx.armament_effect_ids, (
            "the key and the context disagree about the rolls, which is the "
            "one shape `run.run` refuses outright")


def test_the_rolls_on_the_armament_moved_the_ranking_before_ad_032(
        planner, game_data):
    """The counter-case the invariance above is worth anything against.

    Same inventory, same two armaments, same two rolls -- and the context as
    it stood before AD-032, with `armament_effect_ids` put back by hand. If
    this came back equal, neither the four copies nor the two rolls could
    tell the two runs apart, and the case above would be green for a reason
    that has nothing to do with the buffs.

    **The order, not only the figures.** That a roll moves the numbers was
    true of the stacking half as well, and QA-226 measured that it leaves
    every place alone; what AD-032 is answering is that a non-stacking roll
    turns the copy carrying the same effect into a copy worth nothing. Only
    the damage direction: the attribute figure cannot be reached by an
    attack-rate roll at all, and the survival figure is not reachable by
    one in this dataset, so both would come back equal here and prove the
    opposite of what this case is for.
    """
    if planner.owned is None:
        pytest.skip("`asking_from` answers nothing without a save to choose "
                    "relics from")
    hero = planner.current_hero()
    inventory, non_stacking, stacking = an_inventory_the_rolls_can_tell_apart(
        game_data, hero)
    armaments = [armament for _effect_id, armament
                 in armament_gates(game_data, hero)]
    question = advisor.problem([advisor.RED, advisor.RED])
    first, second = armaments

    _baseline_first, order_first = ranking_with(
        planner, first, inventory, question, "max_damage",
        rolls=(non_stacking,), as_the_bar_asked_before_ad_032=True)
    _baseline_second, order_second = ranking_with(
        planner, second, inventory, question, "max_damage",
        rolls=(stacking,), as_the_bar_asked_before_ad_032=True)

    assert [offer[:2] for offer in order_first] != \
        [offer[:2] for offer in order_second], (
        "asked the way the advisor asked before AD-032, these two sets of "
        "rolls give the same order, so this inventory cannot see the "
        "difference AD-032 removes")


def test_the_survival_goal_rises_with_hp(game_data, wylder):
    """Effective HP is HP over what gets through, so more HP is more of it."""
    more_hp = cases.effects_raising_rate(game_data, wylder, "maxHpRate")
    plain, ctx = build_with(game_data, wylder)
    tougher, _ = build_with(game_data, wylder, effect_ids=more_hp)

    assert goals.GOALS["min_damage_taken"].score(tougher, ctx).value > \
        goals.GOALS["min_damage_taken"].score(plain, ctx).value


def test_the_survival_goal_rises_when_less_damage_gets_through(game_data,
                                                               wylder):
    """Bigger is better for this goal too, so one comparison serves both.

    A cut rate below 1.0 is *less* damage taken. If the goal ranked on the
    raw figure rather than on what it protects, this would be the assertion
    that came out backwards -- and the advisor would recommend the relics
    that get you killed.
    """
    negation = cases.effects_raising_rate(game_data, wylder,
                                          "magicDamageCutRate")
    plain, ctx = build_with(game_data, wylder)
    protected, _ = build_with(game_data, wylder, effect_ids=negation)

    assert model.compute(wylder, advisor.LEVEL,
                         [cases.effect_by_id(game_data, negation[0])],
                         game_data.get("curves", {})
                         ).rates["magicDamageCutRate"] < 1.0, (
        "the case needs an effect that lowers incoming damage")
    assert goals.GOALS["min_damage_taken"].score(protected, ctx).value > \
        goals.GOALS["min_damage_taken"].score(plain, ctx).value


def test_the_survival_goal_uses_the_weights_it_is_handed(game_data, wylder):
    """OF-3: the weights are data in the context, never numbers in the goal.

    Weighted entirely onto fire, a relic that only negates magic damage must
    move nothing. If the goal carried its own eight weights, it would move --
    and the control OF-3 may yet ask for would silently do nothing.
    """
    negation = cases.effects_raising_rate(game_data, wylder,
                                          "magicDamageCutRate")
    fire_only = types.Weighting(
        id="fire", label="Fire only", note="Fire alone, for this case.",
        weights=(("fireDamageCutRate", 1.0),))
    ctx = advisor.context(game_data, wylder, weighting=fire_only)
    problem = advisor.problem([advisor.RED])
    plain = evaluate(problem, (), ctx)
    protected = evaluate(problem, (), advisor.context(
        game_data, wylder, weighting=fire_only,
        armament_effect_ids=tuple(negation)))

    score = goals.GOALS["min_damage_taken"]
    assert score.score(protected, ctx).value == score.score(plain, ctx).value
    assert score.score(plain, ctx).weights_note == fire_only.note


def test_a_weighting_with_no_weights_is_refused(game_data, wylder):
    """A caller can get this wrong; the dataset cannot.

    So it is checked, where the divide-by-zero the data cannot produce is
    not -- a branch no data can reach is the dead code QA-061 had this
    project delete.
    """
    empty = types.Weighting(id="none", label="None", note="", weights=())
    ctx = advisor.context(game_data, wylder, weighting=empty)
    build = evaluate(advisor.problem([advisor.RED]), (), ctx)

    with pytest.raises(ValueError, match="no weights"):
        goals.GOALS["min_damage_taken"].score(build, ctx)


def test_a_dataset_without_curves_has_no_effective_hp(game_data, wylder):
    """HP comes from the attribute curves; without them there is no figure.

    Loudly rather than as a zero, which would rank every build alike and look
    like an inventory that helps with nothing.
    """
    without_curves = dict(game_data)
    without_curves["curves"] = {}
    ctx = advisor.context(without_curves, wylder)
    build = evaluate(advisor.problem([advisor.RED]), (), ctx)

    with pytest.raises(ValueError, match="no HP"):
        goals.GOALS["min_damage_taken"].score(build, ctx)


def test_the_score_is_unrounded_and_the_display_is_the_rounded_one(game_data,
                                                                   wylder):
    """QA-074's discipline: characterise on the figure, show the text.

    Marginal contributions are small, so a value that had already been
    rounded for the screen would put the noise floor of every comparison at
    half a unit -- and the diminishing return the whole feature rests on is
    smaller than that near the top of a curve.

    The text is the facade's own, `damage.displayed` -- truncated rather than
    rounded, because that is what the game does with an attack rating
    (QA-095) -- so this line and the weapon panel cannot show one armament as
    two figures. Asserted through that function and not against a second
    `f"{...:.0f}"` written out here: a copy of the rule in the test is a
    second rule, and it would go on passing after the display's own stopped
    matching the game.
    """
    reference = advisor.scaling_armament(game_data, wylder)
    build, ctx = build_with(game_data, wylder, reference=reference)

    score = goals.GOALS["max_damage"].score(build, ctx)

    assert score.value != int(score.value), (
        "this armament happens to rate at a whole number; the case needs one "
        "that does not, or it says nothing about rounding")
    assert str(damage.displayed(score.value)) in score.display


def test_the_eight_damage_kinds_are_the_ones_the_model_knows(game_data):
    """The list's scope, checked against the data rather than asserted.

    A field named here that the dataset does not carry would be weighted into
    the average as a neutral 1.0 for ever, and nothing would say so.
    """
    known = set(model.RATE_LABELS)

    assert set(goals.DAMAGE_CUT_FIELDS) <= known
    assert len(goals.DAMAGE_CUT_FIELDS) == 8
    assert dict(goals.EVEN_WEIGHTING.weights).keys() == \
        set(goals.DAMAGE_CUT_FIELDS)


# --- the baseline of A18 ----------------------------------------------------

#: The conditional curses of this dataset, counted on 2026-09-13 over the
#: 2 076 effects of the Testabzug (`EXTRACT_VERSION` 11): 24 carry
#: `is_curse`, and these seven are gated (`model.is_conditional(eff, None)`).
#: They count in the baseline like every other switchable condition (OF-37,
#: user decision 2026-09-14) -- the case a baseline that took `is_curse` for
#: "not a condition you can be in" would drop.
CONDITIONAL_CURSES = (6850700, 6850800, 6850900, 6851200, 6851300, 6851400,
                      6851700)

#: Every gated effect the sheet offers a switch for, less the one in
#: `model.NO_SWITCH`: 413 that are not curses plus the seven above (same
#: dataset, counted 2026-09-14). The baseline's whole vocabulary (AD-036.6).
SWITCHABLE_CONDITIONS = 420

#: How many copies of the frozen save (`conftest.FROZEN_INVENTORY`, 315
#: copies) change their `min_damage_taken` figure between the baseline and
#: the bar as it asked before A16 -- the player's declarations alone.
#: Counted 2026-09-14 on the frozen copy (21 of the 314 frozen the day
#: before; seven rolls came, six went, T-252).
COPIES_THE_BASELINE_MOVES = 24

SURVIVAL = "min_damage_taken"


def test_advisor_defaults_name_every_switchable_condition_at_one(game_data):
    """AD-036.6 with OF-37: the baseline declares every gated effect the
    sheet offers a switch for -- buffs and curses alike -- at count 1.

    Qt-free: the table is filled by `model.configure`, and this asks it
    against literals counted on the dataset rather than against
    `is_conditional` restated here -- a table that lost the curses, or took
    `is_debuff` (78 ids) for "curse", shows up as the wrong count and the
    missing seven, not as a restatement agreeing with itself.
    """
    defaults = model.advisor_defaults()

    assert len(defaults) == SWITCHABLE_CONDITIONS
    assert set(CONDITIONAL_CURSES) <= set(defaults), (
        "a conditional curse fell out of the baseline (OF-37)")
    assert model.NO_SWITCH.isdisjoint(defaults), (
        "an effect the sheet offers no switch for is being declared")
    # One copy per occurrence, a switch simply turned on -- never a maximum
    # for a counting effect (A7: the condition is assumed, not the number).
    assert set(defaults.values()) == {1}


def one_relic_builds(planner, ctx):
    """Every copy of the save, alone in a white slot of its own kind."""
    for item in planner.owned.relics:
        question = advisor.problem([advisor.WHITE], deep=item.is_deep)
        alone = types.Candidate(
            slot_index=0, handle=item.handle, relic_id=item.relic_id,
            name=item.name, colour=item.colour, is_deep=item.is_deep,
            effect_ids=tuple(item.effect_ids),
            curse_ids=tuple(item.curse_ids))
        yield item, evaluate(question, (alone,), ctx)


def not_counted_under(planner, ctx) -> list[str]:
    return [name for _item, built in one_relic_builds(planner, ctx)
            for name in explain.not_counted(built)]


def test_the_baseline_leaves_no_switchable_condition_uncounted(
        planner, frozen_inventory):
    """A18 sentence 1: a conditional effect goes into the figures like an
    unconditional one. Over the one-relic problems of the frozen save the
    baseline parks nothing in `not_counted`, where the bar as it asked
    before A16 parked every gated effect -- so the case can tell the two
    apart, and a baseline that missed one kind of condition shows up here
    by name.
    """
    planner.owned = frozen_inventory
    ctx = advisorbar.asking_from(planner, SURVIVAL).ctx

    before_a16 = not_counted_under(planner, dataclasses.replace(
        ctx, declared=()))
    assert before_a16, ("a save whose copies carry no condition proves "
                        "nothing about the baseline")
    assert not_counted_under(planner, ctx) == []


def what_the_baseline_moves(planner, inventory) -> tuple[bool, list[str]]:
    """(the survival order changed, the copies whose figure changed).

    Against the bar as it asked before A16 -- the player's declarations and
    nothing else -- because that is the ranking A18's acceptance is measured
    from. Both kinds of copy, ordinary and Deep, through one white slot
    each, which is every copy the inventory holds (`Inventory.relics_for`);
    and every copy whose figure moves has to carry a switchable condition.
    """
    planner.owned = inventory
    by_handle = {item.handle: item for item in inventory.relics}
    switchable = set(model.advisor_defaults())
    moved: list[str] = []
    orders_differ = False
    for deep in (False, True):
        question = advisor.problem([advisor.WHITE], deep=deep)
        _base, baseline = ranking_with(planner, None, inventory, question,
                                       SURVIVAL)
        _base, before = ranking_with(planner, None, inventory, question,
                                     SURVIVAL,
                                     as_the_bar_asked_before_a16=True)
        orders_differ |= ([offer[:2] for offer in baseline]
                          != [offer[:2] for offer in before])
        figures_before = {offer[:2]: dict(offer[2])[SURVIVAL]
                          for offer in before}
        for name, handle, marginals in baseline:
            if dict(marginals)[SURVIVAL] == figures_before[(name, handle)]:
                continue
            moved.append(name)
            item = by_handle[handle]
            assert (set(item.effect_ids) | set(item.curse_ids)) & switchable, (
                f"{name!r} changed its figure without a switchable condition")
    return orders_differ, moved


def test_the_baseline_moves_the_ranking_where_a_condition_sits(planner):
    """`GOAL.md` A18, on the save of this machine: the switchable conditions
    move the survival ranking against the player's declarations alone,
    demonstrably -- and nothing else does. No count: the save changes with
    every evening played (QA-252), so the figure lives on the frozen copy.
    """
    if planner.owned is None:
        pytest.skip("`asking_from` answers nothing without a save to choose "
                    "relics from")
    orders_differ, moved = what_the_baseline_moves(planner, planner.owned)
    assert orders_differ, "the baseline left the survival order as it was"
    assert moved, "no copy moved, so the order cannot have"


def test_the_baseline_moves_the_counted_copies_of_the_frozen_save(
        planner, frozen_inventory):
    """A18's figure, on the same save wherever the suite runs: the copies of
    the 315 frozen on 2026-09-14 that change their survival figure under
    the baseline, no more and no fewer -- a baseline that declared one
    condition too many or too few moves a different count. Kills the
    `MUTATIONS` entry `baseline-dropped-from-the-ask` (AD-033).
    """
    orders_differ, moved = what_the_baseline_moves(planner, frozen_inventory)
    assert orders_differ, "the baseline left the survival order as it was"
    assert len(moved) == COPIES_THE_BASELINE_MOVES, sorted(moved)
