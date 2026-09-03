"""What an armament actually hits for, once everything equipped is counted.

`weapons.rate` answers the first half: base damage plus attribute scaling.
This module answers the second -- the attack multipliers a build lays on top
of that figure, and the one place they do not apply flatly.

It was inside the window until now (`Planner._refresh_weapon_damage`), woven
through the widgets that display it, which meant the only way to ask for an
attack rating was to draw one. The build advisor has to ask without drawing,
and two implementations of one number are worse than one uncertain number, so
the calculation lives here and the window formats what it returns (AD-005).

**This module is also the facade** (AD-019). Rating an armament needs three
inputs -- which attribute set, which tier, and whether the attack multipliers
belong to the question -- and until now every display chose all three for
itself, as a side effect of which module it had imported. Three numbers for
one armament stood on screen at once (QA-018, QA-055, QA-056), and none of the
three was wrong on its own. So the choice is made here, once per named
question, and a display names its question instead of assembling inputs:
`Question`, `MULTIPLIERS_FOR`, `ATTRIBUTES_FOR`.

What the facade deliberately does *not* flatten is in AD-020: the arsenal tab
ranks at a chosen target tier, the breakdown's left-hand column stands on the
level's own attributes, the starting-armament penalty follows a slot-and-hero
pairing, class-scoped rates stay per weapon class, and the critical rate stays
out. Five differences that are the questions, not the drift.

Nothing here imports Qt, and nothing here reads a widget or a Planner.
"""

from __future__ import annotations

import enum
import math
from dataclasses import dataclass, field

from . import model, weapons


# Which build.rates multiplier applies to which damage type. Attack rates
# scale the finished number, so they belong in the comparison as much as the
# attribute changes do -- a relic granting Physical Attack +12% moves the
# damage without moving a single stat.
#
# `*AttackRate` is the general buff, carried by 213-216 effects, and it lifts
# whatever you are swinging.
#
# Deliberately NOT here, having checked every attack multiplier in the data:
# saAttackPowerRate and staminaAttackRate are stance and guard damage rather
# than attack rating, guardCounterAttackRate applies only to a guard counter,
# and characterSkillAttackRate only to Duchess' skill. None of the four scales
# an ordinary hit.
AR_RATE_FOR = {
    "Physics": ("physicsAttackRate",),
    "Magic": ("magicAttackRate",),
    "Fire": ("fireAttackRate",),
    "Thunder": ("thunderAttackRate",),
    "Dark": ("darkAttackRate",),
}

# `*AttackPowerRate` is the second family, carried by exactly three effects --
# the "Starting armament inflicts frost / poison / blood loss" relics, each
# x0.85 -- and it is the price the game charges for the status: the armament
# inflicts it and hits 15% softer for it.
#
# It is **not** a global debuff, which is how it was implemented until 1.7.0
# and what a player reported from play: it reaches the starting armament alone
# -- and "starting armament" means both conditions at once, the Nightfarer's
# own default weapon sitting in slot 1 (verified in play 2026-08-22: moved to
# another slot it loses the penalty, and a different weapon in slot 1 never
# gains it). So it is applied there and to nothing else, and it is kept out of
# the Multipliers section, where an "All damage -15.0%" line said the whole
# build was hitting softer.
STARTING_AR_RATE_FOR = {
    "Physics": ("physicsAttackPowerRate",),
    "Magic": ("magicAttackPowerRate",),
    "Fire": ("fireAttackPowerRate",),
    "Thunder": ("thunderAttackPowerRate",),
    "Dark": ("darkAttackPowerRate",),
}

# Slot 1 holds the armament the expedition starts with -- it is seeded with
# the Nightfarer's own starting armament, see `Planner.apply_hero_weapon`.
STARTING_SLOT = 0


def displayed(figure: float) -> int:
    """The whole number a display puts on screen for an attack rating.

    **Truncated, not rounded**, and that is a measurement rather than a
    preference: over nine armaments that scale off nothing, "the game rounds"
    leaves an empty interval for the calibration factor and "the game
    truncates" leaves a consistent one, and Soldier's Crossbow settles it on
    its own -- 148 base, 0.6 x 148 = 88.8, and the game shows **88**
    (QA-095, `docs/berichte/T-038-qa-engineer.md` section 4.1).

    **One place, because there is one number.** Every display that prints an
    attack rating goes through here: the weapon tile, the breakdown panel and
    its click-through, the arsenal tab's tiles and the advisor's goal line. A
    second `f"{x:.0f}"` anywhere is the shape QA-018 had -- one armament, two
    figures on screen at the same moment -- and this time it would be one
    figure agreeing with the game and one not.

    **The rounding stays out of the arithmetic** (QA-074). What is truncated
    is the text; rankings, marginal contributions and the multiplier layer go
    on working with the unrounded figure, so a comparison between two
    armaments is never decided by a digit that only exists for the screen.
    Consequently a shown difference is not always the difference of the two
    shown figures -- it is the real one, rounded for display.
    """
    return math.floor(figure)


class Question(enum.Enum):
    """Which question is being asked of an armament. Exactly these three.

    Named `Question` and not `Basis`: this module already says `base` for
    "before the attribute scaling" and `bare` for "on the level's own
    attributes", and a third meaning of the same word is the trap AD-022 has
    just cleared out.

    A fourth question needs an entry in `ARCHITECTURE.md` first. That is the
    point of the enum: a new display has to decide what it is asking, instead
    of inheriting an answer from whichever module it imported.
    """

    EQUIPPED = "equipped"    # this armament, in this slot, as it stands
    CANDIDATE = "candidate"  # an armament in no slot, at a chosen target tier
    BARE = "bare"            # the level's own attributes, nothing equipped


# The only place that says whether the multiplier layer belongs to a question.
#
# **Decided by the measurement in play, 2026-09-03 (AD-019 step W6, QA-018).**
# The arsenal tab used to rank without the multipliers while the breakdown
# panel showed them, and one armament stood on screen as 203.4 and as 244.1 at
# the same moment. Neither number was reached by a wrong sum: the panel's
# figure carried a x1.20 that the tab's did not.
#
# The user checked which of the two the game agrees with, and the answer was
# **both of them, once the buff behind the x1.20 stops being counted flat**.
# "Improved Thrusting Counterattack" reaches a thrusting counterattack and no
# other swing, so it belongs to no ordinary attack rating at all; it is out of
# the layer since `model.MOVE_SCOPED_EFFECT_IDS`, together with the three
# spell families beside it. What is left in the layer -- "Improved Physical
# Attack Power" and its 200-odd relatives -- lifts every swing, so it belongs
# to a candidate exactly as it belongs to an equipped armament, and a tab that
# left it out ranked a bow above a greatsword for a build that buffs neither.
#
# BARE stays off, and that is a different question rather than the same one
# answered differently: it is the breakdown's left-hand column, the figure the
# armament would have with nothing equipped, and multipliers that come from
# what is equipped have no place in it (AD-020, point 2).
MULTIPLIERS_FOR = {
    Question.EQUIPPED: True,
    Question.CANDIDATE: True,
    Question.BARE: False,
}

# Which attribute set of the computed build the question stands on. The bare
# figure is the "before" column of the breakdown, and it stays on the level's
# own attributes on purpose -- otherwise the panel's before-and-after has
# nothing to compare (AD-020, point 2).
ATTRIBUTES_FOR = {
    Question.EQUIPPED: "attributes",
    Question.CANDIDATE: "attributes",
    Question.BARE: "base_attributes",
}


@dataclass(frozen=True)
class Rating:
    """One armament's damage, and the question it is the answer to.

    Two layers, named after AD-022: `scaled_*` is the armament with its
    attribute scaling, `final_*` is that figure after the attack multipliers.
    Where the question excludes the multipliers, the two are the same numbers.

    Each layer is held **once**, as a figure per damage type; both totals are
    derived from it and cannot be supplied from outside (assurance Z1). That
    is not tidiness: the advisor's marginal contribution is a difference of
    two totals, so if the two sides were bracketed differently, the noise
    floor of the comparison would be set by that inconsistency rather than by
    the arithmetic -- and marginal contributions are small.
    """

    question: Question
    # The layer-one rating this was built from. No display reads it any more
    # -- the breakdown panel took its requirement check and its per-stat
    # figures off it in W3 and asks this dataclass instead. It stays for
    # `applied_upgrade` (`tier_applied` below) and for `AttackRating.before`/
    # `.after`, the older view the golden test's window-free half and
    # `test_marginal_returns.py` still read. `WeaponRating.total` itself fell
    # in W5 (assurance Z1) -- it had no reader left once this field's own
    # `scaled_per_type()` could be summed instead.
    weapon_rating: weapons.WeaponRating
    scaled_per_type: dict[str, float]
    final_per_type: dict[str, float]
    # Only the multipliers that are not 1.0, for the click-through breakdown.
    rates: dict[str, float] = field(default_factory=dict)
    weapon_class: str | None = None
    starting_armament: bool = False

    @property
    def weapon(self) -> dict:
        return self.weapon_rating.weapon

    @property
    def scaled_total(self) -> float:
        """Layer one, summed from the map beside it and from nothing else.

        Since W3 this is the **only** place in the module that sums a
        layer-one per-type map: the panel's own accumulation went with the
        step that put the panel on `equipped()`. `final_total` beside this
        property is a second summation, but it sums layer two, not layer one,
        so it is not an "other" in the sense assurance Z1 forbids (QA-064/b).

        `weapons.WeaponRating.total` used to bracket the same addends
        differently outside this module, and deliberately so until W5
        (do-not rule 27): it was the reference point the differential
        comparison during the W1-W4 migration stood on. It fell in W5 --
        there was nothing left to compare it against once every display
        stood on the facade.
        """
        return sum(self.scaled_per_type.values())

    @property
    def final_total(self) -> float:
        """Layer two, summed the same way. The number a display shows."""
        return sum(self.final_per_type.values())

    @property
    def tier_applied(self) -> int:
        """The rarity tier the armament was actually rated at.

        The reinforce group of a weapon holds exactly the tiers above its own,
        so asking for a tier below where an armament already sits leaves it
        where it is. Measured over the whole dataset (2026-09-02): for a
        requested tier within 1..`weapons.MAX_UPGRADE` -- the only range the
        arsenal tab's spinbox can ask for -- this is always `max(own tier,
        requested tier)`, never short of the request.

        `candidate()` places no ceiling on `target_tier` (AD-020, point 1),
        so a caller can ask past `weapons.MAX_UPGRADE` where the spinbox
        cannot: `weapons.rate` clamps the request to `MAX_UPGRADE` before it
        ever reaches the reinforce table, so tier 5 or 6 comes back as tier 4,
        short of what was asked (QA-064/c).
        """
        return (self.weapon.get("rarity", 0) + 1
                + self.weapon_rating.applied_upgrade)


@dataclass(frozen=True)
class AttackRating:
    """The breakdown panel's older view of an `equipped()`-shaped pair.

    Every figure on it is read off the two `Rating`s it holds, so it cannot
    be a second answer to a question the facade has already answered -- which
    is how QA-018 arose. The panel itself stopped asking in these terms in
    W3; what still asks is the advisor's marginal-contribution measure
    (AD-018) and the window-free half of the golden file.

    **QA-071, decided in W5: kept, not folded into `Rating`.** This class and
    `attack_rating()` below have no production reader any more -- confirmed
    by search, not by memory, before writing this. What they still have is a
    calling convention `equipped()` cannot offer: a bare `(weapon, tier,
    starting_armament)`, with no slot and no hero. `equipped()` needs both to
    work out the tier and the starting-armament pairing on its own (AD-020,
    point 6), which is right for a tab with a real slot and wrong for a case
    that is evaluating a weapon nothing has equipped -- exactly the shape
    `test_marginal_returns.py`'s AD-018 prototype and the golden file's
    window-free half are in. Folding this into `Rating` would not remove a
    second calculation, because there is only ever the one call to `_rate()`
    underneath; it would only replace this pair with a bare tuple and push
    the slot-free construction into every caller instead of once here. That
    is a larger, riskier edit for a purely cosmetic gain -- the golden file
    in particular is not to move a digit in this task -- so the second
    interface stays, documented rather than merged away in silence.
    """

    bare: Rating
    now: Rating

    @property
    def weapon(self) -> dict:
        return self.now.weapon

    @property
    def before(self) -> weapons.WeaponRating:
        return self.bare.weapon_rating

    @property
    def after(self) -> weapons.WeaponRating:
        return self.now.weapon_rating

    @property
    def final_per_type(self) -> dict[str, float]:
        """Damage type -> the figure after the multipliers, the number shown."""
        return self.now.final_per_type

    @property
    def bare_scaled_total(self) -> float:
        return self.bare.scaled_total

    @property
    def scaled_total(self) -> float:
        return self.now.scaled_total

    @property
    def final_total(self) -> float:
        return self.now.final_total

    @property
    def rates(self) -> dict[str, float]:
        """Only the multipliers that are not 1.0, for the click-through panel."""
        return self.now.rates

    @property
    def weapon_class(self) -> str | None:
        return self.now.weapon_class

    @property
    def starting_armament(self) -> bool:
        return self.now.starting_armament

    def figures(self) -> dict:
        return breakdown_figures(self.bare, self.now)


def breakdown_figures(bare: Rating, now: Rating) -> dict:
    """The numbers the breakdown popup needs, and nothing else.

    Takes the pair `equipped()` returns, because the popup's left-hand figure
    answers a different question from its right-hand one and the pair is what
    holds both answers together.

    `class` is in here because a class-scoped buff records its source under a
    prefixed key: without knowing which class to look under, "Improved Ranged
    Weapon Attacks" raised the total and then named nothing that did it.
    """
    return {
        "base": bare.scaled_total,
        "scaled": now.scaled_total,
        "final": now.final_total,
        "rates": dict(now.rates),
        "weapon": now.weapon.get("name", "weapon"),
        "class": now.weapon_class,
    }


def is_starting_armament(weapon: dict, hero: dict, slot_index: int) -> bool:
    """Is this the Nightfarer's own starting armament, in the starting slot?

    Both halves are required, and that is not a detail: the penalty follows
    the pairing, not the weapon and not the slot (verified in play).
    """
    return (slot_index == STARTING_SLOT
            and weapon["id"] == hero.get("starting_weapon"))


def _scaled(weapon: dict, question: Question, tier: int,
            build: model.Build, data: dict) -> weapons.WeaponRating:
    """Layer one, on the attribute set this question stands on."""
    attributes = getattr(build, ATTRIBUTES_FOR[question])
    return weapons.rate(weapon, attributes, data, tier)


def _answer(rating: weapons.WeaponRating, question: Question,
            build: model.Build, *, starting_armament: bool = False) -> Rating:
    """Layer two: the attack multipliers, where the question includes them."""
    scaled_per_type = rating.scaled_per_type()
    weapon_class = model.weapon_class(rating.weapon)

    if not MULTIPLIERS_FOR[question]:
        return Rating(
            question=question,
            weapon_rating=rating,
            scaled_per_type=scaled_per_type,
            final_per_type=dict(scaled_per_type),
            weapon_class=weapon_class,
        )

    class_rates = build.class_rates.get(weapon_class, {})
    final_per_type: dict[str, float] = {}
    rates_in_play: dict[str, float] = {}

    for damage, total in scaled_per_type.items():
        fields = AR_RATE_FOR.get(damage, ())
        if starting_armament:
            fields += STARTING_AR_RATE_FOR.get(damage, ())
        # Deliberately excludes model.CRIT_RATE: attack rating is the ordinary
        # hit, and folding a critical-only bonus into it would overstate the
        # weapon by a fifth.
        # A buff tied to a weapon *class* covers only that class: "Improved
        # Melee Attack Power" lifts the greatsword and not the bow beside it.
        # A buff merely *gated* on a weapon type is not restricted at all --
        # that is a flat rate and already counted.
        rate = 1.0
        for field_name in fields:
            from_build = build.rates.get(field_name, 1.0)
            from_class = class_rates.get(field_name, 1.0)
            # Kept for the click-through breakdown: what the player would read
            # as one percentage, which is the two sources multiplied.
            together = from_build * from_class
            if abs(together - 1.0) > 1e-9:
                rates_in_play[field_name] = together
            # One factor at a time and in this order, which is the order the
            # figure has always been multiplied in. Multiplying the two
            # sources together first and applying the product would regroup
            # the arithmetic and can move the last bit (AD-019, W2/A2).
            rate *= from_build
            rate *= from_class
        final_per_type[damage] = total * rate

    return Rating(
        question=question,
        weapon_rating=rating,
        scaled_per_type=scaled_per_type,
        final_per_type=final_per_type,
        rates=rates_in_play,
        weapon_class=weapon_class,
        starting_armament=starting_armament,
    )


def _rate(weapon: dict, question: Question, tier: int, build: model.Build,
          data: dict, *, starting_armament: bool = False) -> Rating:
    """Both layers for one armament and one question."""
    return _answer(_scaled(weapon, question, tier, build, data),
                   question, build, starting_armament=starting_armament)


def equipped(slot, slot_index: int, build: model.Build, hero: dict,
             data: dict) -> tuple[Rating, Rating]:
    """The armament in a slot: the bare comparison figure, then the real one.

    The tier comes from the slot, and the starting-armament pairing from the
    slot index together with the Nightfarer -- neither is something a caller
    gets to choose, which is what makes the tile and the panel one question
    with one answer (AD-020, point 6).

    `slot` is left untyped because `weaponslots` imports Qt and this module
    does not; anything with a `weapon` and a `tier` will do.
    """
    starting = is_starting_armament(slot.weapon, hero, slot_index)
    return (_rate(slot.weapon, Question.BARE, slot.tier, build, data),
            _rate(slot.weapon, Question.EQUIPPED, slot.tier, build, data,
                  starting_armament=starting))


def candidate(weapon: dict, target_tier: int, build: model.Build,
              data: dict) -> Rating:
    """An armament that sits in no slot, at a tier the caller has to name.

    `target_tier` has no default on purpose: a default would quietly put back
    the slot tier this question exists to keep out (AD-020, point 1). And with
    no slot there is no starting-armament pairing to be had, so the penalty
    cannot reach this question at all (AD-020, point 3).
    """
    return _rate(weapon, Question.CANDIDATE, target_tier, build, data)


def rank_candidates(build: model.Build, target_tier: int,
                    data: dict) -> list[Rating]:
    """Every armament in the dataset as a candidate, best first.

    **Best by the figure a display shows, which is `final_total`.** Ordering
    is done here and not left to `weapons.rank`, because `rank` sees layer one
    only: it cannot know the attack multipliers, and since W6 they are part of
    a candidate's answer. A list ordered by layer one while every row printed
    layer two would rank a bow above a greatsword whenever a class-scoped rate
    lifted one of them -- sorted by a number that is nowhere on screen. The
    layer-one order `rank` hands over is therefore an intermediate result, not
    this function's answer; it is re-sorted rather than trusted.

    **The second key is the armament id, and it is not decoration** (do-not
    rule 29). Two orderings of the same addends can disagree by a ULP --
    `WeaponRating.total` sums the base and scaled maps whole, `final_total`
    sums the merged per-type map, and 584 of 7 172 measured records move by
    exactly one (AD-024). Near-ties are common in this dataset, so without a
    tie-break the order of equal figures would follow whatever `rank` happened
    to hand over, and two runs could disagree about rows a player cannot tell
    apart.

    This is **not** the order the arsenal tab draws:
    `arsenaltab._build_weapons` discards this list's order outright and
    re-sorts each family of its own accord, by descending rarity, then the
    standard version's name, then id. Reversing this function's order leaves
    every row the tab draws where it was; the count behind that sentence is in
    QA-064/a and not here, because it was measured by the run recorded there
    and not by this module's author (QA-069).

    There used to be a `require_usable` flag here, passed straight through
    from a checkbox in the arsenal tab. QA-061 measured that it could never
    filter anything on real data -- 1791 of 1793 armaments carry an all-zero
    requirement, the other two ask for Arcane 1, and every Nightfarer starts
    above that -- and the user confirmed Nightreign has no attribute
    requirement for armaments at all (T-034). The flag, the checkbox, and the
    branch in `weapons.rate` it gated are gone together.
    """
    attributes = getattr(build, ATTRIBUTES_FOR[Question.CANDIDATE])
    ranked = weapons.rank(data, attributes, target_tier)
    answers = [_answer(rating, Question.CANDIDATE, build) for rating in ranked]
    answers.sort(key=lambda answer: (-answer.final_total, answer.weapon["id"]))
    return answers


def attack_rating(weapon: dict, tier: int, build: model.Build, data: dict,
                  starting_armament: bool = False) -> AttackRating:
    """The armament's attack rating for this build.

    `build` supplies both the attributes and the multipliers, so the two
    halves of the figure -- what the stats do and what the buffs do -- come
    from the same computed build and cannot disagree with the stat sheet.

    Takes the starting-armament pairing as a flag rather than working it out
    from a slot: its callers have a weapon and a tier, not a slot. Where there
    is a slot, `equipped()` is the question to ask -- it works the pairing out
    itself and cannot be handed the wrong answer (AD-020, point 6).
    """
    return AttackRating(
        bare=_rate(weapon, Question.BARE, tier, build, data),
        now=_rate(weapon, Question.EQUIPPED, tier, build, data,
                  starting_armament=starting_armament),
    )
