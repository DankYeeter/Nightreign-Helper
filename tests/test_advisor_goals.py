"""Two named directions, each with what it cannot know written into it.

AD-004 and `GOAL.md` A3/A7. A goal is not a number, it is a number with a
stated scope, so the first assertion in this file is not about a figure at
all: no goal ever hands back an empty `unknowns`. The rest are about the two
figures being the ones the rest of the program already stands on --

* the damage goal is the question the weapon panel asks, `damage.equipped`,
  which works the starting-armament pairing out from the slot and the
  Nightfarer. `damage.candidate` answers a different question and would drop
  that penalty (AD-020 point 3); the ranking would survive the swap, the
  absolute figure would not, and AD-014.6 keeps the absolute figure as the
  one authority. The test that tells the two apart is
  `test_the_damage_goal_charges_the_starting_armament_penalty`;
* the survival goal weighs the eight damage kinds with the weights the
  context carries and with none of its own (AD-004, OF-3).

**What is not tested here, said rather than left implicit:** that either
figure is the one the *game* shows. The damage goal's figure is held against
the game in `tests/test_attack_power_against_the_game.py` and nowhere else;
the survival goal's is held against nothing outside the program at all. What
this file does check is that every score carries the scope of that agreement
in its `unknowns` -- including the armaments the agreement does not cover.
"""

from __future__ import annotations

import dataclasses

import pytest

from nrplanner import damage, model
from nrplanner.advisor import goals, types
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
def test_no_goal_hands_back_an_empty_unknowns(game_data, wylder, goal_id):
    """`GOAL.md` A7 as a property of the result, not of the drawing.

    A static warning in the tab would say the same thing whatever the run
    did; this is the version the test suite can hold, and it is the reason
    `unknowns` is a field rather than a footnote (AD-010).
    """
    reference = advisor.scaling_armament(game_data, wylder)
    build, ctx = build_with(game_data, wylder, reference=reference)

    score = goals.GOALS[goal_id].score(build, ctx)

    assert score.unknowns, (
        f"{goal_id} gave a figure and said nothing about what it cannot "
        f"know")
    assert score.display, "a score has to be sayable to the player"


@pytest.mark.parametrize("goal_id", sorted(goals.GOALS))
def test_every_goal_gives_a_finite_number_for_a_known_build(game_data, wylder,
                                                            goal_id):
    reference = advisor.scaling_armament(game_data, wylder)
    build, ctx = build_with(game_data, wylder, reference=reference)

    score = goals.GOALS[goal_id].score(build, ctx)

    assert score.value > 0
    assert isinstance(score.value, float)


def test_the_damage_goal_always_carries_the_attack_rating_reservation(
        game_data, wylder):
    """The promise the README's Known limits already make, kept in the result.

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
    """
    reference = advisor.scaling_armament(game_data, wylder)
    with_armament, ctx = build_with(game_data, wylder, reference=reference)
    without, plain_ctx = build_with(game_data, wylder)

    for build, context in ((with_armament, ctx), (without, plain_ctx)):
        unknowns = goals.GOALS["max_damage"].score(build, context).unknowns
        assert not any("has not been verified" in line for line in unknowns), (
            "the old reservation is back; it says the attack rating was "
            "never checked against the game, which is no longer true")
        scope = [line for line in unknowns
                 if "matches the game's own display" in line]
        assert scope, "no line says where the agreement with the game holds"
        for outside in ("reinforced", "infused", "Scholar", "Undertaker"):
            assert any(outside in line for line in scope), (
                f"the scope line does not say that {outside} armaments or "
                f"Nightfarers are outside the measurement")
        assert not any("outside that match" in line for line in unknowns), (
            "the old catalyst reservation is back; it says this program "
            "shows a staff's physical attack rating, which since T-046 it "
            "does not")
        catalysts = [line for line in unknowns
                     if "staves and seals" in line.lower()]
        assert catalysts, (
            "nothing says what a catalyst's figure is; the scope of a "
            "second measured quantity cannot be left out because the "
            "quantity is now right")
        for stated in ("own rarity", "spell hits for"):
            assert any(stated in line for line in catalysts), (
                f"the catalyst line does not say {stated!r}: it was measured "
                f"at the base rarity only, and it is the game's display "
                f"rather than what a spell does")
        assert any("Spell damage" in line for line in unknowns)
        assert any("Critical-only" in line for line in unknowns)


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
    stronger = cases.effects_raising_attribute(game_data, wylder, "Strength", 1)

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


def test_without_an_armament_the_damage_goal_says_so(game_data, wylder):
    """OF-5: the run is not refused, the assumption is stated (AD-004).

    Silence would be the breach of A7, not the assumption. The figure is then
    a ratio rather than an attack rating, so it carries no unit -- which is
    the signal `UI_SPEC` §3.3 reads to drop the "AR" suffix and the
    attack-rating reservation with it.
    """
    buff = cases.effects_raising_rate(game_data, wylder, "physicsAttackRate")
    plain, ctx = build_with(game_data, wylder)
    buffed, _ = build_with(game_data, wylder, effect_ids=buff)

    bare = goals.GOALS["max_damage"].score(plain, ctx)
    lifted = goals.GOALS["max_damage"].score(buffed, ctx)

    assert any("No armament selected" in line for line in bare.unknowns)
    assert bare.unit == ""
    assert bare.weights_note
    assert lifted.value > bare.value


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
