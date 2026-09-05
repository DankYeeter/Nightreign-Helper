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

**A staff or a seal is not rated by that formula at all.** The game shows a
catalyst's spell scaling where it shows every other armament's attack power,
and that is a different quantity out of a different field --
`_catalyst_scaling` below, the one place it is formed.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .model import evaluate_curve, weapon_class

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


#: The scale the game lays over a catalyst's spell scaling, the number it
#: shows for a staff or a seal where it shows an attack rating for everything
#: else: `floor(CATALYST_DISPLAY_RATE x rate x (1 + curve(attribute)/100))`.
#:
#: **Measured, not found in a param** -- and unlike `GAME_ATTACK_POWER_RATE`
#: the search for it was exhaustive and is written down: all 252 param tables
#: of the regulation decode, 208 of them have a paramdef, 6082 readable
#: fields per row set, and no table holds this number in a place the 28
#: catalysts share (`docs/berichte/T-043-qa-engineer.md` section 5).
#:
#: The recipe of the number itself: never a point estimate, always the
#: intersection of the 84 `floor` conditions the measured cells impose, which
#: is `K in [89.9982, 90.0147]`. 90 is the only figure with two significant
#: digits inside it; the margin is 0.0018 (0.002 %) down and 0.0147 (0.016 %)
#: up. Below 89.998 the Albinauric Staff falls out, above 90.015 the Carian
#: Glintstone Staff does.
#:
#: **Two readings the data cannot separate**, said out loud because the
#: second would put the number somewhere else entirely: either 90 is an
#: engine constant, or it is `correct{Stat}` (100 for all 28) x the
#: AttackElementCorrectParam influence (90 for all 28) / 100 -- the same
#: multiplication the attack rating knows, applied **outside** the bracket
#: instead of inside it. Telling them apart needs a catalyst with a different
#: `correct{Stat}` or a different influence row, and the game has none. The
#: ranking is the same under both readings, which is why this is an
#: assumption that can be carried rather than one that has to be resolved.
#:
#: **`GAME_ATTACK_POWER_RATE` is not applied to this figure.** The 0.6 was
#: measured against the attack power the game displays; this constant was
#: measured against the spell scaling the game displays. Both are already on
#: the screen's scale, and multiplying one by the other would be counting the
#: same calibration twice.
CATALYST_DISPLAY_RATE = 90.0


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
    #: The spell scaling the game shows for this armament, unrounded, or
    #: `None` where the game shows an attack rating instead -- which is every
    #: armament that is not a staff or a seal. `None` rather than 0.0 on
    #: purpose: a zero would sum, sort and print like a figure.
    catalyst_scaling: float | None = None

    def scaled_headline(self) -> float:
        """The figure this armament is ranked and shown by, before layer two.

        For a staff or a seal that is its spell scaling, because the game
        shows no attack rating for one and the physical figure underneath is
        not a quantity the player can compare with anything (QA-099: the
        physical rating ranks the catalysts in a different order from the
        game's own). For everything else it is the per-type sum, unchanged.

        The multiplier layer does not reach the catalyst branch: see
        `damage.Rating.final_headline` for why, and for where that is decided.
        """
        if self.catalyst_scaling is not None:
            return self.catalyst_scaling
        return sum(self.scaled_per_type().values())

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


#: Which attribute a catalyst scales its spell power off, in the order the
#: figure is looked for. A staff carries `correctMagic` 100 and
#: `correctFaith` 0, a seal the other way round -- checked over all 255
#: catalyst rows of the game data, where no row carries both and none
#: carries neither (T-043 section 2). The armament's own scaling is read
#: rather than its weapon type, so this needs no table of type numbers.
CATALYST_ATTRIBUTES = ("Intelligence", "Faith")

#: The key `nrdata.extract` writes the spell scaling rate under.
CATALYST_SCALING_KEY = "catalyst_scaling"


def _catalyst_scaling(weapon: dict, attributes: dict[str, int],
                      reinforce: dict, curves: dict) -> float | None:
    """The spell scaling the game shows for a staff or a seal, unrounded.

    `None` for every armament the game shows an attack rating for, which is
    everything that is not a catalyst. **The one place this figure is
    formed** -- `rate()` calls it and hands the result on, so a display
    reaches it through `damage.Rating` and never by computing it again
    (AD-019, AD-021).

        floor is NOT applied here (QA-074). The truncation belongs to the
        display, `damage.displayed`, so a ranking is never decided by a digit
        that exists only for the screen.

    The measurement behind the shape of it is QA-099 /
    `docs/berichte/T-043-qa-engineer.md`: 84 of 84 cells read off the game's
    own display and 28 of 28 figures from a second, independent list, with no
    exception. Three neighbouring shapes were each tried and each leaves an
    empty interval for the constant: rounding instead of truncating, the
    AttackElementCorrectParam influence of 0.9 taken **inside** the bracket,
    and any of the 81 other curves in the data in place of the armament's own.

    The curve is the armament's own `correctType_Physics`, read out of the
    weapon rather than written down here -- it is 16 for all 255 catalyst
    rows, and a hardcoded 16 would be a fact about today's data sitting in
    code that looks like arithmetic.
    """
    if weapon_class(weapon) != "catalyst":
        return None

    if CATALYST_SCALING_KEY not in reinforce:
        raise KeyError(
            f"this dataset's reinforce table carries no "
            f"{CATALYST_SCALING_KEY!r}, so the figure the game shows for "
            f"{weapon.get('name', 'this catalyst')!r} cannot be formed. It "
            f"was built by an extractor older than EXTRACT_VERSION 9: "
            f"delete the cached snapshot and let it be rebuilt. Nothing is "
            f"substituted here -- a stand-in rate would show every catalyst "
            f"the same figure and say nothing (QA-099 c).")
    scaling_rate = reinforce[CATALYST_SCALING_KEY]
    if scaling_rate is None:
        # No reinforce row for this armament's group at all, which is the
        # same state `rate()` treats as unreinforced above. There is no
        # figure to show, and 1.0 would invent the same one for every
        # catalyst. No armament in the shipped data reaches this.
        return None

    attribute = next((name for name in CATALYST_ATTRIBUTES
                      if weapon.get("scaling", {}).get(name)), None)
    curve = curves.get(str(weapon.get("curve", {}).get("Physics")))
    if attribute is None or curve is None:
        # Neither happens in the shipped data -- every one of the 30 named
        # catalysts scales off exactly one of the two attributes, and all of
        # them carry curve 16. Said out loud because the consequence is
        # visible rather than quiet: such an armament would fall back to
        # showing an attack rating, labelled as one, among neighbours
        # showing spell power.
        return None

    ratio = evaluate_curve(curve, attributes.get(attribute, 0)) / 100.0
    return CATALYST_DISPLAY_RATE * scaling_rate * (1.0 + ratio)


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
        # `catalyst_scaling` is spelled out as None rather than left absent:
        # absent means "this dataset predates the field", which
        # `_catalyst_scaling` refuses loudly, and that is a different state
        # from "this armament's group has no row".
        reinforce = {"atk": {}, "correct": {}, CATALYST_SCALING_KEY: None}

    aec = element_correct.get(str(weapon.get("element_correct_id")), {})
    result = WeaponRating(
        weapon=weapon, applied_upgrade=applied,
        catalyst_scaling=_catalyst_scaling(weapon, attributes, reinforce,
                                           curves))

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
        # where it used to carry one, and its ratio to the old figure drifts.
        #
        # Re-run on 2026-09-05 with `scripts/bracketing_residue.py`, which is
        # the whole of the measurement and takes no arguments: over 350 160
        # per-type figures (ten Nightfarers x levels 1, 12, 15 x four tiers x
        # all 1793 armaments), **544** come out 2 ULP from `fl(old x 0.6)`
        # the shorter way, and **0 of 350 160** do it this way -- written
        # this way every per-type figure is exactly `fl(old x 0.6)`, to the
        # last bit and not merely within one.
        #
        # The figure that stood here until then was 574, taken with a script
        # that was never committed and cannot be re-run (QA-115). The case
        # count and the figure count are reproduced exactly, so it is the
        # same measurement; what the 30 come from is not knowable without the
        # script, and the most likely reading is that its `bonus` was
        # accumulated with `sum()` where this function uses a running loop --
        # a difference of one last bit, which is the whole quantity being
        # counted. The script above holds itself to the program's own
        # arithmetic instead: every shipped figure it forms must equal
        # `weapons.rate`'s bit for bit, and it stops if one does not.
        #
        # The summed totals keep a residue either way -- 447 of 215 160 at
        # 2 ULP here against 3058 the other way, same run -- and that residue
        # cannot be removed from inside this function: a sum of separately
        # rounded terms is not the rounded sum, whichever term carries the
        # constant. Said out loud so the next reader does not go looking for
        # the bracketing that makes it zero (AD-024: bracketing is decided by
        # what it makes unambiguous, not by which looks more careful). These
        # two counts are of the per-type sum this script forms; the pair that
        # stood here before (480 against 1081) named no definition of "the
        # total" and cannot be matched to one.
        result.scaled[damage] = base * bonus * GAME_ATTACK_POWER_RATE

    return result


def rank(data: dict, attributes: dict[str, int],
         upgrade: int = MIN_UPGRADE) -> list[WeaponRating]:
    """Every armament in the dataset, rated and ordered best first.

    `WeaponRating.total` fell in AD-019 step W5 (assurance Z1): it bracketed
    the same addends `scaled_per_type()` sums differently, and after W1 it
    had no purpose but to be that second bracketing. Sorting on
    `scaled_headline()` -- which is that one summation for every armament the
    game shows an attack rating for -- means there is still exactly one
    summation of a damage type in the whole program, not two that happen to
    agree to within a ULP.

    Staves and seals are ordered by the figure the game shows for them and
    not by their physical rating (QA-099): rating them by the latter put
    Rotten Crystal Staff (182 in game) ahead of Carian Regal Scepter (237),
    so the list disagreed with the game about which of two catalysts is
    better. The physical rating of a catalyst now appears in no ranking.

    The second sort key is not decoration (do-not rule 29, AD-024): two
    orderings of the same addends can disagree by a ULP, so without a
    tie-break the order of a near-tie would follow whatever this loop
    happened to hand over, and two runs over the same data could disagree
    about rows nobody could tell apart on screen.
    """
    out = [rate(weapon, attributes, data, upgrade)
           for weapon in data["weapons"]]
    out.sort(key=lambda r: (-r.scaled_headline(), r.weapon["id"]))
    return out
