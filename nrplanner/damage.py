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

What the facade deliberately does *not* flatten is in AD-020.

**Not every armament is answered with an attack rating.** For a staff or a
seal the game shows a spell scaling in that place and no attack rating at
all, so the facade hands displays a `headline` -- figure, label and per-type
rows -- and they print that instead of choosing for themselves which of the
two an armament gets (QA-099).

Nothing here imports Qt, and nothing here reads a widget or a Planner.
"""

from __future__ import annotations

import enum
import math
from collections.abc import Callable
from dataclasses import dataclass, field

from . import model, weapons
from .theme import MUTED


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

# `*AttackPowerRate` is the second **field family**, and exactly three effects
# in the data carry it: the "Starting armament inflicts frost / poison / blood
# loss" relics, each holding all five fields at 0.85 (measured over the 2076
# effects of data_version 10350000 on 2026-09-05 -- three effects, fifteen
# modifier entries). It is the price the game charges for the status: the
# armament inflicts it and hits 15% softer for it.
#
# **Three effects is a statement about this field, not about the relics they
# belong to** (QA-114). The same three sit in a wider group of "starting
# armament" relics whose other members convert a damage type instead --
# "Starting armament deals magic / fire / lightning / holy damage",
# 7120000/100/200/300, which carry flat `*AttackPower` fields that
# `converted` below applies (`model.FLAT_ATTACK_POWER_FIELDS`, QA-113). The claim
# that the game groups all of them under one `stateInfo` is the
# `qa-engineer`'s reading of the params and **cannot be reproduced from the
# extracted dataset**, which carries no such field; what can be counted here
# is the three above and the four beside them. Merging the two counts is what
# sent R-005 looking for the conversion in the wrong three effects.
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

# What the figure at the head of an armament is called, short for a tile row
# and long for a sentence. Two forms because both are already in use: the
# weapon tile and the arsenal tile have room for "AR" and the advisor's goal
# line says "Attack rating".
ATTACK_RATING_LABEL = "AR"
ATTACK_RATING_NAME = "Attack rating"

# A staff or a seal has no attack rating on screen; the game shows its spell
# scaling in that place, so this program shows the same thing there and the
# physical figure nowhere (the App Designer's decision, 2026-09-03: "replace
# physical attack with spell power"). One word for both forms and one word
# for staves and seals alike -- the alternative, "Incantation power" for
# seals, was left to the `ui-ux-designer` and has not been ruled on, and the
# task named this as what to use until it is.
SPELL_POWER_LABEL = "Spell power"

# What a spell hits for is a different quantity from both of those, so it is
# named apart from them (AD-053, point 7): the attack rating and the spell
# power are fitted against figures the game prints, and this one is not.
SPELL_DAMAGE_NAME = "Spell damage"

# ... and it says so wherever it is shown. The Elden Ring damage formula
# applied to Nightreign's params is a premise of A26 and not a measurement
# (user decision OF-54, 2026-09-20): the factors are the game's own, their
# product has never been compared with a number on screen, and no screen of
# this game shows one to compare it with.
SPELL_DAMAGE_UNCALIBRATED = (
    "{name} is uncalibrated: it is the damage formula applied to the game's "
    "own values, and the game shows no spell damage to check it against. "
    "Compare two spells by it, not the figure itself.")

# The spell power is a percentage of the spell's own damage, which is what
# makes the 100 arithmetic rather than a tuning knob.
SPELL_POWER_SCALE = 100.0

# What a spell that damages nothing gets instead of a figure. Rejection and
# Heal are the Finger Seal's two, so this is Revenant's default state rather
# than an edge case. It carries the spell's own name unescaped, like every
# other game text this program passes on: the sinks that draw a finding are
# PlainText, and escaping here would show a spell called `Bell & Bearing` its
# own `&amp;` (SEC-019, AK-29).
NO_SPELL_DAMAGE = (
    "{name} deals no damage, so this is 0.00. Only a relic that swaps the "
    "spell this equipment casts brings damage here.")


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


# The mark a two-handed figure carries on screen (`147 1H / 151 2H`,
# AK-299), and the switch of AK-292 uses the same two letters for the same
# thing.
TWO_HANDED_MARK = "2H"
# Its one-handed counterpart (AK-299): the earlier `{1H} / {2H} 2H` left the
# first figure unlabelled, which read as "base / with build" rather than a
# pair of hands (QA-278).
ONE_HANDED_MARK = "1H"
# Inside the group the three parts never separate: `2H` alone at the start
# of a line would read as a term of its own (AK-73, DR-009).
_NO_BREAK_SPACE = "\u00a0"
# The hand the switch (AK-292) is not set to, on every surface that shows
# both: the panes' `MUTED`, unbolded, whatever emphasis the surface puts
# around the whole figure (AK-298).
_QUIET_HAND = f"<span style='color:{MUTED}; font-weight:normal'>{{}}</span>"


def displayed_hands(one_handed: float, two_handed: float | None,
                    two_handing: bool = False) -> str:
    """`147`, or `147 1H / 151 2H` where the game offers a second figure.

    AK-286/AK-299: the two-handed figure is a suffix to the one-handed one
    under the same label, never a labelled figure of its own; where there is
    none, the text is the one-handed figure and nothing else (AK-288, no
    `/ -- 2H`). Both halves carry their own hand mark (AK-299) -- the bare
    first figure used to read as "base" rather than "one-handed" (QA-278).

    AK-298/AK-299: the half the build is not held in -- with the `/` -- is
    wrapped quiet, number and mark together as one unit, so the surface's
    own emphasis (`<b>`, `ACCENT`, a bold label) lands on the chosen half's
    number and mark alone. Rich text, then, wherever both hands show; a lone
    figure stays the bare number.
    """
    if two_handed is None:
        return str(displayed(one_handed))
    shown = _NO_BREAK_SPACE.join((str(displayed(one_handed)), ONE_HANDED_MARK))
    other = _NO_BREAK_SPACE.join((str(displayed(two_handed)), TWO_HANDED_MARK))
    if two_handing:
        return (_QUIET_HAND.format(shown + _NO_BREAK_SPACE + "/")
                + _NO_BREAK_SPACE + other)
    return shown + _QUIET_HAND.format(_NO_BREAK_SPACE + "/" + _NO_BREAK_SPACE
                                      + other)


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
    #: What the damage-type conversion moved, per type, on the screen's
    #: scale -- empty where none applies. For the popup; already inside
    #: `scaled_per_type`.
    conversion: dict[str, float] = field(default_factory=dict)
    #: The same question answered for the armament held in both hands, or
    #: `None` where the game offers no second figure (`weapons.can_two_hand`)
    #: -- and `None` on the nested answer itself. One question, one answer
    #: with two numbers (AD-037): a display reads both off this and never
    #: asks twice.
    two_handed: Rating | None = None

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

    # -- what the game puts at the head of this armament (QA-099) ----------
    #
    # For everything but a staff or a seal that is the attack rating above,
    # and these three properties hand back exactly it. For a catalyst the
    # game shows a spell scaling instead, and shows no attack rating at all,
    # so these hand back that -- and the physical figure reaches no display.

    @property
    def catalyst_scaling(self) -> float | None:
        """The spell scaling, or None where the game shows an attack rating.

        Read off the layer-one rating rather than stored here, for the same
        reason the totals are derived rather than stored (assurance Z1):
        there is one representation of the figure, `weapons.rate` computed
        it, and no caller can hand this dataclass a different one.
        """
        return self.weapon_rating.catalyst_scaling

    @property
    def scaled_headline(self) -> float:
        """Layer one, as the game labels it: spell scaling or attack rating."""
        return self.weapon_rating.scaled_headline()

    @property
    def final_headline(self) -> float:
        """Layer two, as the game labels it. The number a display shows.

        **The attack multipliers do not reach a catalyst's figure**, and that
        is a measurement rather than an omission. The 90 in
        `weapons.CATALYST_DISPLAY_RATE` was fitted against the spell scaling
        the game displays, with no relic equipped; nothing has been measured
        about what "Improved Physical Attack Power" does to that display, and
        it is a scaling number rather than a damage figure. Multiplying it by
        a physical attack rate would be this program inventing a relationship
        the data does not state (GOAL.md A7). What does move it is an
        attribute: a relic that raises Intelligence raises a staff's figure,
        through the curve, exactly as the game does.
        """
        if self.catalyst_scaling is not None:
            return self.catalyst_scaling
        return self.final_total

    def displayed_hands(self, figure: Callable[[Rating], float],
                        two_handing: bool = False) -> str:
        """`figure` of this answer, and of its two-handed one where it has one.

        `figure` picks which number (`final_headline`, one type's
        `scaled_per_type` entry, ...); the same pick is read off both hands,
        so the two figures beside each other answer the same question.
        `two_handing` is the switch's stand (AK-298).
        """
        other = None if self.two_handed is None else figure(self.two_handed)
        return displayed_hands(figure(self), other, two_handing)

    @property
    def headline_label(self) -> str:
        """"AR" or "Spell power" -- what to write beside the figure."""
        if self.catalyst_scaling is not None:
            return SPELL_POWER_LABEL
        return ATTACK_RATING_LABEL

    @property
    def headline_name(self) -> str:
        """The same thing in a sentence: "Attack rating" or "Spell power"."""
        if self.catalyst_scaling is not None:
            return SPELL_POWER_LABEL
        return ATTACK_RATING_NAME

    @property
    def shown_per_type(self) -> dict[str, float]:
        """The per-damage-type rows a display prints under the headline.

        Empty for a catalyst: those rows *are* the physical attack rating,
        broken down, and the game shows a staff no attack rating to break
        down. Everything else gets `final_per_type` unchanged.
        """
        if self.catalyst_scaling is not None:
            return {}
        return self.final_per_type

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

    `headline` names the quantity the three figures are. It is here rather
    than written into the text because the text is built from this dictionary
    and nothing else, and for a staff the three figures are a spell scaling:
    a popup headed "Attack rating" over them would be the one thing worse
    than the wrong number, which is the right number under the wrong name
    (QA-099).

    `two_handed` holds the same `base` and `final` for the other hand, and
    only where the game offers one (AK-286/AK-288) -- like `calibration`
    below, a key that is absent rather than None where it says nothing.
    """
    figures = {
        "base": bare.scaled_headline,
        "scaled": now.scaled_headline,
        "final": now.final_headline,
        "rates": dict(now.rates),
        "weapon": now.weapon.get("name", "weapon"),
        "class": now.weapon_class,
        "headline": now.headline_name,
    }
    # Only where one applies: the golden file freezes this dictionary for
    # pairings none of the two factors reach, and a key that is always None
    # there would say nothing to the popup and change every frozen record.
    calibration = now.weapon_rating.calibration
    if calibration is not None:
        figures["calibration"] = {"factor": calibration.factor,
                                  "reason": calibration.reason}
    if now.conversion:
        figures["conversion"] = dict(now.conversion)
    if now.two_handed is not None:
        figures["two_handed"] = {"base": bare.two_handed.scaled_headline,
                                 "final": now.two_handed.final_headline}
    return figures


def is_starting_armament(weapon: dict, hero: dict, slot_index: int) -> bool:
    """Is this the Nightfarer's own starting armament, in the starting slot?

    Both halves are required, and that is not a detail: the penalty follows
    the pairing, not the weapon and not the slot (verified in play).
    """
    return (slot_index == STARTING_SLOT
            and weapon["id"] == hero.get("starting_weapon"))


def converted(per_type: dict[str, float],
              flat: dict[str, float]) -> tuple[dict[str, float],
                                               dict[str, float]]:
    """The starting armament's per-type figure after a damage-type conversion.

    Hands back `(per type after, what moved per type)`, both on the screen's
    scale.

    **Measured, not read from the files** (QA-113, T-246). The params say
    `physicsAttackPower` -30 and `<element>AttackPower` +33 and nothing about
    where those points land. Three readings in play on 2026-09-14 -- level 15,
    own starting armament in slot 1, the "Starting armament deals fire
    damage" relic at its first payload tier, no other relics -- settle it:

        Wylder    Greatsword   122 -> 123   (Physics 80 base)
        Revenant  Cursed Claws  88 -> 91    (Physics 12, Magic 54)
        Duchess   Dagger        72 -> 74    (Physics 55)

    The one reading that hits 3 of 3: the points are added **flat** to the
    scaled figure, before `GAME_ATTACK_POWER_RATE` -- so +3 net is +1.8 on
    screen -- and a type driven below zero stops at zero. Revenant's claws
    are the case that needs the floor: 12 x 2.36 - 30 < 0, and without the
    floor the game would show 90. Scaling the points through the attributes
    instead (the reading the task started from) gives 126 / 92 / 76 and is
    ruled out by all three; the next payload tier gives 124 / 98 / 74 and is
    ruled out by two.

    Applied before the attack multipliers, which no reading has measured
    against; the three readings had none in play, so the order is a choice
    and is said to be one. Types stay in `weapons.DAMAGE_TYPES` order so the
    panel lists them as every other display does; a type the conversion
    zeroes stays in the map at 0.0, because "your physical damage is gone" is
    the thing the player is buying the element with.
    """
    after: dict[str, float] = {}
    moved: dict[str, float] = {}
    for damage_type in weapons.DAMAGE_TYPES:
        if damage_type not in per_type and damage_type not in flat:
            continue
        was = per_type.get(damage_type, 0.0)
        now = max(0.0, was + flat.get(damage_type, 0.0)
                  * weapons.GAME_ATTACK_POWER_RATE)
        after[damage_type] = now
        if damage_type in flat:
            moved[damage_type] = now - was
    return after, moved


def _multiplied(per_type: dict[str, float], build: model.Build, *,
                art: str | None = None,
                buckets: list[dict[str, float]] | None = None,
                starting_armament: bool = False,
                ) -> tuple[dict[str, float], dict[str, float]]:
    """The attack multipliers on a per-type figure: `(after, what applied)`.

    The one loop a swing and a spell both go through (AD-053, point 2). What
    differs between the two is what is handed in, not what happens here: an
    armament brings the buckets of its weapon class and, where it is the
    Nightfarer's own in slot 1, the status penalty's field family; a spell
    brings neither -- it is no swing of a weapon class and carries no
    starting-armament pairing (AD-053, point 4), so it is rated on the
    general `*AttackRate` fields and its art alone.

    A second copy of this arithmetic is what assurance Z1 forbids: the
    advisor's marginal contribution is a difference of two figures, and two
    places forming the same product could bracket it differently.
    """
    buckets = buckets or []
    art_rate = model.art_factor(build, art)
    final_per_type: dict[str, float] = {}
    rates_in_play: dict[str, float] = {}
    if abs(art_rate - 1.0) > 1e-9:
        # Under its own key, so the breakdown can show which art it is.
        rates_in_play[art] = art_rate

    for damage, total in per_type.items():
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
            # Kept for the click-through breakdown: what the player would read
            # as one percentage, which is the sources multiplied.
            together = from_build
            for bucket in buckets:
                together *= bucket.get(field_name, 1.0)
            if abs(together - 1.0) > 1e-9:
                rates_in_play[field_name] = together
            # One factor at a time and in this order, which is the order the
            # figure has always been multiplied in. Multiplying the sources
            # together first and applying the product would regroup the
            # arithmetic and can move the last bit (AD-019, W2/A2).
            rate *= from_build
            for bucket in buckets:
                rate *= bucket.get(field_name, 1.0)
        # Last, and once per damage type: the art covers the whole hit, not
        # one of the five rates that make it up (AD-047, point 2).
        rate *= art_rate
        final_per_type[damage] = total * rate

    return final_per_type, rates_in_play


def _answer(rating: weapons.WeaponRating, question: Question,
            build: model.Build, *, starting_armament: bool = False,
            two_handed: Rating | None = None,
            art: str | None = None) -> Rating:
    """Layer two: the attack multipliers, where the question includes them.

    `two_handed` is the finished answer for the other hand, attached as it
    is; a rating that carries a two-handing factor (`rating.two_handed`)
    additionally takes the `when Two-Handing` bucket, and no one-handed
    rating ever does (AD-037, point 3).

    `art` names one kind of attack the figure is asked about -- a Weapon Art,
    a spell school (`model.attack_arts`). Its factor is a third bucket beside
    the class ones, applied in the same loop and on the same figure, so that
    the buffs a scoped relic carries reach the ranking exactly where the
    ordinary ones do. `None` is the question nobody asked, and every figure
    is then the one it has always been (AD-047, point 1).
    """
    scaled_per_type = rating.scaled_per_type()
    weapon_class = model.weapon_class(rating.weapon)

    if not MULTIPLIERS_FOR[question]:
        return Rating(
            question=question,
            weapon_rating=rating,
            scaled_per_type=scaled_per_type,
            final_per_type=dict(scaled_per_type),
            weapon_class=weapon_class,
            two_handed=two_handed,
        )

    # The damage-type conversion follows the same pairing as the status
    # penalty below: the Nightfarer's own armament in slot 1, nothing else.
    conversion: dict[str, float] = {}
    if starting_armament and build.starting_flat:
        scaled_per_type, conversion = converted(scaled_per_type,
                                                build.starting_flat)

    buckets = [build.class_rates.get(weapon_class, {})]
    if rating.two_handed:
        buckets.append(build.class_rates.get(model.TWO_HANDED_CLASS, {}))
    final_per_type, rates_in_play = _multiplied(
        scaled_per_type, build, art=art, buckets=buckets,
        starting_armament=starting_armament)

    return Rating(
        question=question,
        weapon_rating=rating,
        scaled_per_type=scaled_per_type,
        final_per_type=final_per_type,
        rates=rates_in_play,
        weapon_class=weapon_class,
        starting_armament=starting_armament,
        conversion=conversion,
        two_handed=two_handed,
    )


def _rate(weapon: dict, question: Question, tier: int, build: model.Build,
          data: dict, *, starting_armament: bool = False,
          art: str | None = None) -> Rating:
    """Both layers for one armament and one question, both hands.

    Both hands come from one `weapons._rate_pair` call, which shares the
    base/bonus arithmetic between them instead of computing it twice (T-261;
    until then this called `weapons.rate` once for each hand).
    """
    attributes = getattr(build, ATTRIBUTES_FOR[question])
    one_handed, two_handed_rating = weapons._rate_pair(
        weapon, attributes, data, tier, build.nightfarer)
    two_handed = None
    if two_handed_rating is not None:
        two_handed = _answer(two_handed_rating, question, build,
                             starting_armament=starting_armament, art=art)
    return _answer(one_handed, question, build,
                   starting_armament=starting_armament,
                   two_handed=two_handed, art=art)


def equipped(slot, slot_index: int, build: model.Build, hero: dict,
             data: dict, *, art: str | None = None) -> tuple[Rating, Rating]:
    """The armament in a slot: the bare comparison figure, then the real one.

    The tier comes from the slot, and the starting-armament pairing from the
    slot index together with the Nightfarer -- neither is something a caller
    gets to choose, which is what makes the tile and the panel one question
    with one answer (AD-020, point 6).

    `slot` is left untyped because `weaponslots` imports Qt and this module
    does not; anything with a `weapon` and a `tier` will do.

    `art` restricts the real figure to one kind of attack (`_answer`). The
    bare figure carries no multipliers at all and is therefore the same
    under every art, which is what makes it the comparison it is.
    """
    starting = is_starting_armament(slot.weapon, hero, slot_index)
    return (_rate(slot.weapon, Question.BARE, slot.tier, build, data),
            _rate(slot.weapon, Question.EQUIPPED, slot.tier, build, data,
                  starting_armament=starting, art=art))


@dataclass(frozen=True)
class SpellRating:
    """What a spell hits for, cast from this catalyst by this build.

    The sibling of `Rating` for the spell half of the question (AD-053), and
    the same shape of answer: one figure per damage type, held once, with
    both the selected figure and the total derived from it rather than
    supplied beside it (assurance Z1).

    It is deliberately **not** a `Rating`. A `Rating` is an armament's attack
    rating, layer one and layer two, and every display reads
    `final_headline`, `two_handed` and `weapon_rating` off it; a spell has
    none of the three -- no hands, no reinforce tier of its own, and a
    headline that is a different quantity under a different name
    (`SPELL_DAMAGE_NAME`).
    """

    spell: dict
    #: The damage type asked about, `""` for all of them at once. The two
    #: columns of the combination table, and the reason the figure is picked
    #: here rather than by every caller in turn.
    damage_type: str
    #: The art the factor was actually taken for, which is the art asked
    #: about only where the spell belongs to it (`_art_of`). `None` where
    #: nothing was asked.
    art: str | None
    #: The catalyst's spell scaling -- the figure the game prints on the
    #: staff, unrounded, and the one factor of this product that *is*
    #: calibrated (`weapons.CATALYST_DISPLAY_RATE`, QA-099).
    spell_power: float
    per_type: dict[str, float]
    #: The same product with nothing equipped: the spell's own base damage on
    #: the catalyst's spell scaling at the level's own attributes, and no
    #: rates and no art factor on top of it. The "before" figure a display
    #: puts against `per_type` (AK-359), and the counterpart of the `bare`
    #: half of what `equipped()` hands back -- `Question.BARE` for the spell
    #: half, held here rather than asked for a second time so that the two
    #: halves of one difference come out of one call (assurance Z1).
    bare_per_type: dict[str, float]
    #: Only the multipliers that are not 1.0, keyed as `Rating.rates` is.
    rates: dict[str, float] = field(default_factory=dict)
    #: Why this figure is 0.00 where that needs saying, else `None`.
    reason: str | None = None

    def _asked(self, per_type: dict[str, float]) -> float:
        """One damage type's figure out of a per-type map, or all of them.

        The pick is here and not at the two properties below, so that the
        figure and its baseline can never be picked by two different rules.
        """
        if self.damage_type:
            return per_type.get(self.damage_type, 0.0)
        return sum(per_type.values())

    @property
    def figure(self) -> float:
        """The number asked for: one type's, or all of them summed.

        A type the spell does not deal is 0.00 and not an error -- it is a
        ranking in which every candidate that brings some of that type
        stands above this one.
        """
        return self._asked(self.per_type)

    @property
    def bare_figure(self) -> float:
        """The same number with nothing equipped (`bare_per_type`)."""
        return self._asked(self.bare_per_type)


def _casts_under(spell: dict, art: str) -> bool:
    """Does this spell belong to the school `art` names?

    The school is a number in the art key and a name on the spell, so the
    two are matched through `model.SPELL_FAMILY_NAMES` -- the dataset's own
    naming, in both directions, with nothing written down here.
    """
    value = art[len(model.ART_FAMILY_PREFIX):]
    if not value.isdigit():
        return False
    name = model.SPELL_FAMILY_NAMES.get(int(value))
    return bool(name) and spell.get("family") == name


def _art_of(spell: dict, hit_with: str) -> str | None:
    """Which art's factor this spell actually takes under the asked one.

    Asking about a school the spell does not belong to does not leave it
    unbuffed: it is still a sorcery or still an incantation, so it keeps the
    factor of its genus and loses only the school's. The genus is read off
    the spell's own category rather than asserted here.
    """
    if not hit_with:
        return None
    if not hit_with.startswith(model.ART_FAMILY_PREFIX):
        return hit_with
    if _casts_under(spell, hit_with):
        return hit_with
    return model.GENUS_FOR_CATEGORY.get(str(spell.get("category") or ""))


def spell(spell: dict, catalyst: dict, tier: int, build: model.Build,
          data: dict, *, hit_with: str, damage_type: str = "") -> SpellRating:
    """What this spell hits for, cast from this catalyst by this build.

    The spell half of the facade (AD-053), and the same rule as the weapon
    half: the figure is formed here once, and a display or a goal prints
    what it gets back instead of assembling one of its own (AD-019/AD-021).

        figure[T] = base[T] x spell_power / 100 x rate[T] x art_rate

    and, beside it, the same product with nothing equipped (`bare_per_type`),
    so that a display's before-and-after comes out of one call.

    `base[T]` is the spell's strongest single hit in that damage type
    (`spells[].damage`, AD-050.3, user decision OF-57 -- not the sum of a
    multi-hit spell and not its charged variant). `spell_power` is the
    catalyst's own headline, the figure the game prints on the staff, asked
    of this module's own `_rate` rather than of `weapons` a second time, so
    that it is the very number the weapon tile shows and carries the one
    calibration there is (QA-099); the attributes it stands on are the build's, which
    is why a Faith relic raises a seal's incantations. `rate[T]` is the
    general `*AttackRate` family and `art_rate` the genus and school buffs,
    both through `_multiplied`, the same loop a swing goes through.

    **The product itself is uncalibrated** and has to be shown as such
    (`SPELL_DAMAGE_UNCALIBRATED`, OF-54): it is the Elden Ring formula taken
    as a premise, and nothing the game displays confirms it.

    **Four things deliberately do not reach a spell** (AD-053, point 4), and
    each is an omission rather than an oversight: the class rates -- a spell
    is no swing of a weapon class --, the two-handing bucket, the starting
    armament's damage-type conversion and its status penalty, both of which
    are properties of the armature in slot 1 rather than of the spell. None
    of the four can arrive here at all: `_multiplied` is called without the
    buckets and without the pairing.

    `hit_with` names what is being asked about -- `sorceries`,
    `incantations` or `family:<id>`; `damage_type` picks one of the five, or
    `""` for all of them together. Neither decides *which* spell is rated:
    that is the goal's choice (AD-052), and this answers for the spell it is
    handed.

    Raises `ValueError` for an armament the game shows no spell scaling for.
    A spell cast from a sword is not a 0.00 to be ranked -- it is a caller
    that picked the wrong reference object, and a silent zero would hide it.
    """
    spell_power = _rate(catalyst, Question.EQUIPPED, tier, build,
                        data).catalyst_scaling
    if spell_power is None:
        raise ValueError(
            f"{catalyst.get('name', 'this armament')!r} is no catalyst, so "
            f"it has no {SPELL_POWER_LABEL.lower()} to cast "
            f"{spell.get('name', 'a spell')!r} with. The reference object "
            f"for a spell question is the starting catalyst (AD-052).")

    # A value that is not a positive, finite number is no damage: it would
    # travel through every multiplication below and poison a ranking rather
    # than fail loudly (T-077). The extractor writes only positive types, so
    # this holds a snapshot older or newer than this code at arm's length.
    base = {name: float(value)
            for name, value in (spell.get("damage") or {}).items()
            if isinstance(value, (int, float)) and math.isfinite(value)
            and value > 0}
    art = _art_of(spell, hit_with)
    per_type, rates = _multiplied(
        {name: value * spell_power / SPELL_POWER_SCALE
         for name, value in base.items()}, build, art=art)
    # The baseline of the same product (AK-359): the catalyst asked again on
    # the level's own attributes, which is the one factor of the four that a
    # bare build changes -- the rates and the art factor are what the build
    # brought and are left out of a "before" figure by definition, exactly as
    # `MULTIPLIERS_FOR[Question.BARE]` leaves them out of an armament's.
    bare_power = _rate(catalyst, Question.BARE, tier, build,
                       data).catalyst_scaling
    return SpellRating(
        spell=spell,
        damage_type=damage_type,
        art=art,
        spell_power=spell_power,
        per_type=per_type,
        bare_per_type={name: value * bare_power / SPELL_POWER_SCALE
                       for name, value in base.items()},
        rates=rates,
        reason=None if base else NO_SPELL_DAMAGE.format(
            name=spell.get("name", "This spell")),
    )


# -- what a spell question is asked about (AD-052) ----------------------
#
# Which catalyst and which spell a spell question stands on is a choice, not
# an answer, and it lives beside the answer for the reason AD-019 gives: the
# advisor's spell cell and the stat sheet's spell row have to pick the same
# object, and the rule written a second time in the second caller is exactly
# the second place that decision forbids. It was private to
# `advisor/goals.py` until the stat sheet needed it (AK-357).

#: `wep_type` 57 is a staff and 61 a seal, and the pair carries the genus
#: distinction the spell rows need: `enableMagic`/`enableMiracle` say the
#: same thing and are not in the extract, which AD-052 point 4 settled
#: rather than left open. Membership is also the test for "is this armament
#: a catalyst at all", so the one table answers both questions.
GENUS_OF_CATALYST = {57: model.SORCERIES_ART, 61: model.INCANTATIONS_ART}


def _record_by_id(records, wanted: int | None) -> dict | None:
    """The weapon or spell row with this id, or `None` for no such row.

    A scan and not an index, and the cost is measured rather than waved
    through: 113 us of a spell cell's 137 us is this function walking the
    1793 armament rows twice, against 35 us for a whole weapon cell (level
    15, Revenant, 2026-09-20). An index would have to be built out of the
    dataset at every evaluation as well, or kept as module state that a
    second dataset would make stale, and either is a shape the
    `performance-tuner` should choose against a measurement of a whole run
    rather than this one.
    """
    if wanted is None:
        return None
    return next((record for record in records
                 if record.get("id") == wanted), None)


def start_catalyst(hero: dict, data: dict) -> dict | None:
    """The staff or seal this Nightfarer starts with -- right hand first.

    AD-052 point 1: the right hand before the left, and the left only where
    the right carries none. Measured over the ten Nightfarers, exactly two
    carry one and neither carries two -- Recluse's staff is in her right
    hand and Revenant's Finger Seal in his left, which is the reason the
    left hand is read at all (AD-050).
    """
    for hand in ("starting_weapon", "starting_weapon_left"):
        weapon = _record_by_id(data.get("weapons") or (), hero.get(hand))
        if weapon is not None and weapon.get("wep_type") in GENUS_OF_CATALYST:
            return weapon
    return None


def _base_damage(record: dict, damage_type: str) -> float:
    """What a spell hits for before anything of this build reaches it.

    The yardstick AD-052 point 3 picks the stronger of two swap relics by,
    and deliberately the base value rather than the finished figure: the
    spell power and the rates are the same for both, so they cannot change
    which of the two is in front, and the base value is the one number that
    belongs to the spell itself.
    """
    base = record.get("damage") or {}
    if damage_type:
        return float(base.get(damage_type, 0.0))
    return float(sum(base.values()))


def spell_thrown(build: model.Build, data: dict, catalyst: dict, *,
                 damage_type: str = "") -> tuple[dict | None, int]:
    """The spell this equipment casts, and how many relics swapped it.

    AD-052 point 2: a relic that swaps the starting armament's spell puts
    its own spell in the hand, so it is the reference object **and** a
    candidate that moves the figure -- the only effect family of this
    dataset that changes a base value rather than a rate. Held or chosen
    makes no difference here: `model.compute` has put both into the build
    before this is asked.

    A swap relic works for exactly one Nightfarer (`allowed_heroes`, all ten
    of them), and that Nightfarer is the one whose catalyst can cast its
    spell, so a seal cannot be rated on a sorcery. That is the dataset's
    doing rather than this function's, and a case in
    `tests/test_advisor_goals.py` holds it.

    `damage_type` decides nothing but which of two swapped spells is the
    stronger, so a caller that asks about every type at once (the stat
    sheet) leaves it out.
    """
    spells = data.get("spells") or ()
    swapped = [record for record in
               (_record_by_id(spells, magic_id)
                for magic_id in build.swapped_spell_ids)
               if record is not None]
    if swapped:
        return (max(swapped,
                    key=lambda record: _base_damage(record, damage_type)),
                len(swapped))
    slots = catalyst.get(model.SPELL_SLOTS_KEY) or ()
    first = next((slot for slot in slots if slot != model.NO_SPELL_SLOT), None)
    return _record_by_id(spells, first), 0


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
    """Every armament a player can hold, as a candidate, best first.

    **Not every row in the dataset**: the catalyst row nobody can equip is
    not among the answers (`model.is_unequippable_catalyst`, AK-66, QA-119).
    The filter sits here rather than in the arsenal tab because "candidate"
    already means "something the player might choose", so every list built on
    this answer inherits it -- the tab today, the advisor's own candidate list
    when it is built. The rating layer in `weapons` is left seeing the whole
    dataset: a measurement over the game's 30 catalysts has to go on finding
    30 of them.

    **Best by the figure a display shows, which is `final_headline`.**
    Ordering is done here and not by layer one, because layer one cannot know
    the attack multipliers, and since W6 they are part of a candidate's
    answer. A list ordered by layer one while every row printed layer two
    would rank a bow above a greatsword whenever a class-scoped rate lifted
    one of them -- sorted by a number that is nowhere on screen. Until T-261
    this function took layer one from `weapons.rank` and re-sorted its
    output, discarding the order it gave; `weapons._rate_pair` now rates
    each armament directly, since nothing ever trusted that discarded order.

    For a staff or a seal that figure is its spell scaling and not its
    physical rating (QA-099), which is the same rule as everywhere else here:
    the list is ordered by what the row prints. It puts catalysts high in a
    mixed list, because the game's spell scaling runs 78..237 where an attack
    rating at the same tier runs lower -- two quantities in one ordering,
    which is what "show the player the number the game shows" costs once the
    game shows two different numbers.

    **The second key is the armament id, and it is not decoration** (do-not
    rule 29). Two orderings of the same addends can disagree by a ULP --
    `WeaponRating.total` sums the base and scaled maps whole, `final_total`
    sums the merged per-type map, and 584 of 7 172 measured records move by
    exactly one (AD-024). Near-ties are common in this dataset, so without a
    tie-break the order of equal figures would follow whatever order this
    function happened to walk the dataset in, and two runs could disagree
    about rows a player cannot tell apart. It carries the catalysts too:
    `Finger Seal` exists twice in the
    data with identical figures (QA-099 a), so the two rows are separated by
    their ids and by nothing else.

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
    answers = []
    for weapon in data["weapons"]:
        if model.is_unequippable_catalyst(weapon):
            continue
        one_handed, two_handed_rating = weapons._rate_pair(
            weapon, attributes, data, target_tier, build.nightfarer)
        two_handed = None
        if two_handed_rating is not None:
            two_handed = _answer(two_handed_rating, Question.CANDIDATE, build)
        answers.append(_answer(one_handed, Question.CANDIDATE, build,
                               two_handed=two_handed))
    answers.sort(key=lambda answer: (-answer.final_headline,
                                     answer.weapon["id"]))
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
