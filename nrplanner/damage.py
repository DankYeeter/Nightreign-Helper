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
# The measurement in play behind QA-018 changes one value here and nothing
# else in the program (AD-019 step W6).
#
# These are today's values, including where today's value is the wrong one:
# the arsenal tab ranks without the multipliers and the breakdown panel shows
# them, which is exactly the 203.4-against-244.1 of QA-018. W2 moves the
# choice, it does not decide it.
MULTIPLIERS_FOR = {
    Question.EQUIPPED: True,
    Question.CANDIDATE: False,
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
    # The layer-one rating this was built from. The breakdown panel still
    # reads it directly for the requirement check and the per-stat scaling
    # figures; it goes when the last such reader does (AD-019 steps W3, W5).
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

        `_accumulated` below is the only other place in the module that sums
        a layer-one per-type map the way this one does, and it belongs to the
        panel rather than to the facade -- see there for why it outlives this
        step. `final_total` beside this property is a third summation, but it
        sums layer two, not layer one, so it is not the "other" this docstring
        means (QA-064/b).
        """
        return sum(self.scaled_per_type.values())

    @property
    def final_total(self) -> float:
        """Layer two, summed the same way. The number a display shows."""
        return sum(self.final_per_type.values())

    @property
    def unmet(self) -> dict[str, tuple[int, int]]:
        return self.weapon_rating.unmet

    @property
    def meets_requirements(self) -> bool:
        return self.weapon_rating.meets_requirements

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
    """One armament's damage, before and after everything equipped.

    The breakdown panel's own view of a `Rating` pair, kept until the panel
    itself moves onto the facade (AD-019 step W3).
    """

    weapon: dict
    # The scaled figures at the level's own attributes, and at the attributes
    # the relics raised them to. Both carry the requirement check.
    before: weapons.WeaponRating
    after: weapons.WeaponRating
    # Damage type -> the figure after the multipliers, the number shown.
    final_per_type: dict[str, float]
    bare_scaled_total: float
    scaled_total: float
    final_total: float
    # Only the multipliers that are not 1.0, for the click-through breakdown.
    rates: dict[str, float]
    weapon_class: str | None
    starting_armament: bool

    def figures(self) -> dict:
        """The numbers the breakdown popup needs, and nothing else.

        `class` is in here because a class-scoped buff records its source
        under a prefixed key: without knowing which class to look under,
        "Improved Ranged Weapon Attacks" raised the total and then named
        nothing that did it.
        """
        return {
            "base": self.bare_scaled_total,
            "scaled": self.scaled_total,
            "final": self.final_total,
            "rates": dict(self.rates),
            "weapon": self.weapon.get("name", "weapon"),
            "class": self.weapon_class,
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


def _accumulated(per_type: dict[str, float]) -> float:
    """Layer one summed the way the breakdown panel has always summed it.

    `Rating.scaled_total` uses `sum()`, which since Python 3.12 carries a
    running correction term; the panel's figure was accumulated in a plain
    loop. The two disagree by one unit in the last place for 214 of the
    143 440 armament-tier-build combinations measured on 2026-09-02 -- the
    same addends in the same order, summed by two algorithms. Nothing on
    screen and nothing in the golden file can show a difference that small,
    but W2 is promised bit-for-bit unchanged and that promise is what makes
    the differential comparison mean anything, so the panel keeps its own
    summation for one more step.

    It goes when the panel moves onto the facade in W3, along with the other
    total this module still forms outside `Rating` -- and then there is one
    summation left in the module, which is what assurance Z1 is for.
    """
    total = 0.0
    for value in per_type.values():
        total += value
    return total


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


def rank_candidates(build: model.Build, target_tier: int, data: dict, *,
                    require_usable: bool) -> list[Rating]:
    """Every armament in the dataset as a candidate, best first.

    `weapons.rank` orders them by descending `WeaponRating.total` -- the
    layer below the attack multipliers, layer one. That is **not** the order
    the arsenal tab draws: `arsenaltab._build_weapons` discards this list's
    order outright and re-sorts each family of its own accord, by descending
    rarity, then the standard version's name, then id (measured 2026-09-02:
    reversing this function's order changes 0 of 1654 rows the tab draws, and
    W4, which puts the tab onto this function, has to read this paragraph and
    not the one this replaces -- QA-064/a). What does hold while
    `MULTIPLIERS_FOR[Question.CANDIDATE]` is off is that the ranked figure and
    the figure a display would show are the same number; switching it on in
    W6 makes the order come from the layer below the multipliers, and a
    class-scoped rate would reorder the answer without reordering the list.

    `require_usable` is passed straight through and is a caller's input, not a
    policy of the question -- it is a checkbox in the arsenal tab today
    (QA-061 asks whether it can ever filter anything; that is a question about
    the dataset, and it is not settled here).
    """
    attributes = getattr(build, ATTRIBUTES_FOR[Question.CANDIDATE])
    ranked = weapons.rank(data, attributes, target_tier,
                          require_usable=require_usable)
    return [_answer(rating, Question.CANDIDATE, build) for rating in ranked]


def attack_rating(weapon: dict, tier: int, build: model.Build, data: dict,
                  starting_armament: bool = False) -> AttackRating:
    """The armament's attack rating for this build.

    `build` supplies both the attributes and the multipliers, so the two
    halves of the figure -- what the stats do and what the buffs do -- come
    from the same computed build and cannot disagree with the stat sheet.

    The panel's view of `equipped()`, for as long as the panel asks in these
    terms (AD-019 step W3). It takes the pairing as a flag rather than working
    it out from a slot, which is what the caller has to hand today.
    """
    bare = _rate(weapon, Question.BARE, tier, build, data)
    now = _rate(weapon, Question.EQUIPPED, tier, build, data,
                starting_armament=starting_armament)

    return AttackRating(
        weapon=weapon,
        before=bare.weapon_rating,
        after=now.weapon_rating,
        final_per_type=now.final_per_type,
        # The two totals in this module that are not `sum()` of a per-type map
        # of their own, and both for the same reason: they are what the panel
        # shows today, and W2 changes no shown figure by so much as a bit.
        # `WeaponRating.total` sums the two dicts whole instead of type by
        # type and is the reference point of the bit-for-bit comparison that
        # carries the rebuild, so it may not be redefined before W5 (AD-019,
        # do-not rule 27); the two bracketings disagree in the last bit for
        # about a tenth of the dataset. Both become the `Rating` totals beside
        # them when the panel moves onto the facade in W3.
        bare_scaled_total=bare.weapon_rating.total,
        scaled_total=_accumulated(now.scaled_per_type),
        final_total=now.final_total,
        rates=now.rates,
        weapon_class=now.weapon_class,
        starting_armament=starting_armament,
    )
