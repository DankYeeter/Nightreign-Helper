"""Attack rating calculation.

The shape of it is the engine's own formula, assembled from four params that
all carry an exact paramdef:

  base   = attackBase{Type} x reinforce.{type}AtkRate
  factor = correct{Stat}/100 x reinforce.correct{Stat}Rate
           x curve(stat) / 100 x influence{Stat}_by{Type}
  AR     = base x (1 + sum of factors over every scaling stat)
           x GAME_ATTACK_POWER_RATE

Which stats feed which damage type comes from AttackElementCorrectParam; the
curve id per damage type comes from the weapon's own correctType_{Type}.

**One term of that first line is not from a param.**
`GAME_ATTACK_POWER_RATE` is measured against the game and not read out of it;
its scope and its evidence are written out where it is defined. Every other
term is a field with a paramdef behind it.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .model import evaluate_curve

DAMAGE_TYPES = ("Physics", "Magic", "Fire", "Thunder", "Dark")

DAMAGE_LABELS = {
    "Physics": "Physical",
    "Magic": "Magic",
    "Fire": "Fire",
    "Thunder": "Lightning",
    "Dark": "Holy",
}


#: The constant the game lays over the figure this formula produces, so that
#: what the program calls "Attack rating" is the number the weapon panel in
#: the game shows -- and, per the App Designer's reading on the training
#: dummy, the number that actually lands.
#:
#: **Measured, not derived.** It is in none of the params this program reads.
#: The evidence is in `docs/berichte/T-038-qa-engineer.md` and QA-095: nine
#: armaments that scale off no attribute (seven crossbows, Hand Ballista, Jar
#: Cannon) pin it without a curve in the way, and the intersection over those
#: nine x eight Nightfarers is k in [0.599315, 0.600928) -- a single interval,
#: which 0.6 is the only round number inside. The same reading rules rounding
#: out: under "the display rounds" the intersection is **empty**, under "the
#: display truncates" it is the interval above. Over the whole measurement --
#: 310 armaments x 8 Nightfarers -- `floor(rate)` reproduces 97.5 % of the
#: readings exactly.
#:
#: **Where it is measured, and where it is only plausible.** Measured at
#: levels 1, 12 and 15, for the eight Nightfarers the source covers, at each
#: armament's **own** rarity with no reinforcement, without relics and without
#: infusion variants. It is *not* measured for reinforced rarities, for
#: infused variants, for Scholar and Undertaker, or for any other level; there
#: it is plausible and nothing more. Catalysts are a separate matter
#: altogether -- for staves and seals the game shows the spell scaling rather
#: than an attack rating, so this factor does not describe them (QA-099).
#:
#: **Not the source, but the only lead there is:** `PlayerCommonParam` carries
#: exactly this value at offset +664, in a slot no paramdef describes
#: (`docs/berichte/T-042-qa-engineer.md`). An undefined field holding the
#: right number is a coincidence until somebody shows the engine reads it, so
#: it is written down here as a thread to pull and **not** as evidence. The
#: number below stands on the measurement above and on nothing else.
GAME_ATTACK_POWER_RATE = 0.6


# The upgrade number is an absolute rarity tier, not a count of upgrades:
# 1 Common, 2 Uncommon, 3 Rare, 4 Legendary. Confirmed by the data -- a
# weapon's reinforce group holds exactly (4 - rarity) tiers, so every weapon
# can climb to Legendary and one already there has nowhere to go. Reaching
# tier 4 only happens in the volcano event.
MIN_UPGRADE = 1
MAX_UPGRADE = 4
RARITY_TIERS = 4


@dataclass
class WeaponRating:
    weapon: dict
    base: dict[str, float] = field(default_factory=dict)
    scaled: dict[str, float] = field(default_factory=dict)
    applied_upgrade: int = 0

    def scaled_per_type(self) -> dict[str, float]:
        """Base damage plus what the attributes add, per damage type.

        The sum itself is one line, and that is exactly why it needs a home:
        `WeaponRating` carried `total` but no way to ask per type, so every
        display that breaks the figure down wrote the line out again. Three
        copies of one line drift apart one call site at a time (AD-019).

        A type whose combined figure is zero is left out rather than reported
        as such -- the filter is on the summed value, not on whether `rate`
        recorded base damage for it (QA-062). On the game's data the two
        coincide, because `rate` only ever writes `base` and `scaled` for the
        same key in the same pass; a hand-built rating with a `scaled` entry
        and no matching `base` would still come back. Every caller wants the
        types the weapon hits with, so the order is DAMAGE_TYPES and two
        displays list the same weapon alike.
        """
        out: dict[str, float] = {}
        for damage in DAMAGE_TYPES:
            value = self.base.get(damage, 0.0) + self.scaled.get(damage, 0.0)
            if value:
                out[damage] = value
        return out


def rate(weapon: dict, attributes: dict[str, int], data: dict,
         upgrade: int = MIN_UPGRADE) -> WeaponRating:
    curves = data["calc_curves"]
    reinforce_table = data["reinforce"]
    element_correct = data["element_correct"]

    # `upgrade` is the target rarity tier (1-4). How far a given weapon has to
    # travel is the gap between its own rarity and that target, so a Rare
    # weapon only moves when the target is Legendary.
    #
    # The ceiling is guarded twice, and neither guard is spare (QA-068): the
    # `min` below, and the shape of the reinforce table, which holds no entry
    # above `MAX_UPGRADE` for any weapon. Removing the `min` on its own
    # changes nothing -- the backward search underneath finds the same row --
    # so a tidying commit will read it as dead. It is not: drop the `min` and
    # the backward search together and a request for tier 5 walks off the top
    # of the table. Whichever is removed, the other has to be shown to hold.
    base_type = weapon.get("reinforce_type", 0)
    own_tier = weapon.get("rarity", 0) + 1
    steps = max(0, min(upgrade, MAX_UPGRADE) - own_tier)

    reinforce = None
    applied = 0
    for level in range(steps, -1, -1):
        reinforce = reinforce_table.get(str(base_type + level))
        if reinforce is not None:
            applied = level
            break
    if reinforce is None:
        reinforce = {"atk": {}, "correct": {}}

    aec = element_correct.get(str(weapon.get("element_correct_id")), {})
    result = WeaponRating(weapon=weapon, applied_upgrade=applied)

    for damage in DAMAGE_TYPES:
        base = weapon["base"].get(damage, 0)
        if not base:
            continue
        base *= reinforce["atk"].get(damage, 1.0)
        # `base` here is still the raw one. The game's constant is applied to
        # each finished per-type figure instead, at the two lines that write
        # into `result` -- see the note beside `result.scaled` below for why
        # this bracketing and not the shorter `base *= GAME_ATTACK_POWER_RATE`
        # on this line.
        result.base[damage] = base * GAME_ATTACK_POWER_RATE

        rules = aec.get(damage, {})
        curve_id = str(weapon["curve"].get(damage))
        curve = curves.get(curve_id)

        # A plain loop, not `sum()`, and that is load-bearing. Since Python
        # 3.12 `sum()` on floats carries a running correction term that this
        # accumulation does not, so the same addends in the same order can
        # land a ULP apart. This is the **larger** of the two places in the
        # program where that bites -- it moves a substantial minority of all
        # weapon-tier-damage cards, where the other place moves a fraction of
        # a percent. The counts are in QA-064/d; they are not repeated here,
        # because a figure a reader cannot trace back to the run that produced
        # it is worse than the comparison it decorates (QA-069).
        #
        # It stays a loop **permanently**, not "until W5" or any other step of
        # the rebuild. AD-024 settled the question this comment used to bind
        # to a step: switching to `sum()` here would not remove a second
        # representation of the same number, because there is only one --
        # unlike the arsenal tab's move onto `final_total`, it would be a
        # one-sided accuracy change with no consistency gain to show for it,
        # and neither bracketing is validated against the game. This place is
        # worth revisiting only once a deviation is measured on screen or
        # against the game itself, not on the strength of which bracketing
        # looks more careful.
        bonus = 0.0
        if curve is not None:
            for stat, scaling in weapon["scaling"].items():
                rule = rules.get(stat)
                if not scaling or not rule or not rule["on"]:
                    continue
                correct = scaling / 100.0 * reinforce["correct"].get(stat, 1.0)
                ratio = evaluate_curve(curve, attributes.get(stat, 0)) / 100.0
                # Influence is stored as a percentage (100 = full effect).
                influence = rule["influence"] / 100.0
                bonus += correct * ratio * influence

        # The second and last place the game's constant is applied, and the
        # bracketing is measured rather than chosen for looks. Written the
        # shorter way -- `base *= GAME_ATTACK_POWER_RATE` above, and this line
        # left as `base * bonus` -- the scaled figure carries two roundings
        # where it used to carry one, and its ratio to the old figure drifts:
        # measured over 350 160 per-type figures (ten Nightfarers x levels 1,
        # 12, 15 x four tiers x every armament, 2026-09-04), 574 of them come
        # out 2 ULP from 0.6 instead of 1. Written this way each per-type
        # figure is exactly `fl(old x 0.6)` and **none** of the 350 160 is
        # further than 1 ULP.
        #
        # The summed totals keep a residue either way -- 480 of 215 160 at
        # 2 ULP here against 1081 the other way -- and that residue cannot be
        # removed from inside this function: a sum of separately rounded terms
        # is not the rounded sum, whichever term carries the constant. Said
        # out loud so the next reader does not go looking for the bracketing
        # that makes it zero (AD-024: bracketing is decided by what it makes
        # unambiguous, not by which looks more careful).
        result.scaled[damage] = base * bonus * GAME_ATTACK_POWER_RATE

    return result


def rank(data: dict, attributes: dict[str, int],
         upgrade: int = MIN_UPGRADE) -> list[WeaponRating]:
    """Every armament in the dataset, rated and ordered best first.

    `WeaponRating.total` fell in AD-019 step W5 (assurance Z1): it bracketed
    the same addends `scaled_per_type()` sums differently, and after W1 it
    had no purpose but to be that second bracketing. Sorting on
    `sum(scaled_per_type().values())` instead means there is now exactly one
    summation of a damage type in the whole program, not two that happen to
    agree to within a ULP.

    The second sort key is not decoration (do-not rule 29, AD-024): two
    orderings of the same addends can disagree by a ULP, so without a
    tie-break the order of a near-tie would follow whatever this loop
    happened to hand over, and two runs over the same data could disagree
    about rows nobody could tell apart on screen.
    """
    out = [rate(weapon, attributes, data, upgrade)
           for weapon in data["weapons"]]
    out.sort(key=lambda r: (-sum(r.scaled_per_type().values()),
                            r.weapon["id"]))
    return out
