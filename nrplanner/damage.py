"""What an armament actually hits for, once everything equipped is counted.

`weapons.rate` answers the first half: base damage plus attribute scaling.
This module answers the second -- the attack multipliers a build lays on top
of that figure, and the one place they do not apply flatly.

It was inside the window until now (`Planner._refresh_weapon_damage`), woven
through the widgets that display it, which meant the only way to ask for an
attack rating was to draw one. The build advisor has to ask without drawing,
and two implementations of one number are worse than one uncertain number, so
the calculation lives here and the window formats what it returns (AD-005).

Nothing here imports Qt, and nothing here reads a widget or a Planner.
"""

from __future__ import annotations

from dataclasses import dataclass

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


@dataclass(frozen=True)
class AttackRating:
    """One armament's damage, before and after everything equipped."""

    weapon: dict
    # The scaled figures at the level's own attributes, and at the attributes
    # the relics raised them to. Both carry the requirement check.
    before: weapons.WeaponRating
    after: weapons.WeaponRating
    # Damage type -> the figure after the multipliers, the number shown.
    per_type: dict[str, float]
    base_total: float
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
            "base": self.base_total,
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


def attack_rating(weapon: dict, tier: int, build: model.Build, data: dict,
                  starting_armament: bool = False) -> AttackRating:
    """The armament's attack rating for this build.

    `build` supplies both the attributes and the multipliers, so the two
    halves of the figure -- what the stats do and what the buffs do -- come
    from the same computed build and cannot disagree with the stat sheet.
    """
    before = weapons.rate(weapon, build.base_attributes, data, tier)
    after = weapons.rate(weapon, build.attributes, data, tier)

    weapon_class = model.weapon_class(weapon)
    class_rates = build.class_rates.get(weapon_class, {})

    # Apply the attack multipliers on top of the scaled figure.
    per_type: dict[str, float] = {}
    # Kept for the click-through breakdown: the figure before any rate is
    # applied, so the attribute scaling and the multipliers can be shown as
    # the two separate things they are.
    scaled_total = 0.0
    rates_in_play: dict[str, float] = {}

    for damage, total in after.per_type().items():
        scaled_total += total
        fields = AR_RATE_FOR.get(damage, ())
        if starting_armament:
            fields += STARTING_AR_RATE_FOR.get(damage, ())
        for field_name in fields:
            value = (build.rates.get(field_name, 1.0)
                     * class_rates.get(field_name, 1.0))
            if abs(value - 1.0) > 1e-9:
                rates_in_play[field_name] = value
        # Deliberately excludes model.CRIT_RATE: attack rating is the ordinary
        # hit, and folding a critical-only bonus into it would overstate the
        # weapon by a fifth.
        # A buff tied to a weapon *class* covers only that class: "Improved
        # Melee Attack Power" lifts the greatsword and not the bow beside it.
        # A buff merely *gated* on a weapon type is not restricted at all --
        # that is a flat rate and already counted.
        rate = 1.0
        for field_name in fields:
            rate *= build.rates.get(field_name, 1.0)
            rate *= class_rates.get(field_name, 1.0)
        per_type[damage] = total * rate

    return AttackRating(
        weapon=weapon,
        before=before,
        after=after,
        per_type=per_type,
        base_total=before.total,
        scaled_total=scaled_total,
        final_total=sum(per_type.values()),
        rates=rates_in_play,
        weapon_class=weapon_class,
        starting_armament=starting_armament,
    )
