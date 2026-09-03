"""The named directions to optimise in, as a registry of pure functions.

AD-004: a goal is not a number, it is a number **with a stated scope**. Each
entry below therefore hands back a `GoalScore` whose `unknowns` is never
empty -- where the game files do not support a judgement, the result says so
instead of guessing (`GOAL.md` A7).

**Two figures, never one.** There is no conversion between damage dealt and
damage survived, and inventing an exchange rate is what AD-023 and OF-13
forbid: a curse that costs HP under "Maximise damage" is counted in the
build, is *not* in that goal's ranking figure, and is named rather than
marked down. So every candidate carries a gain under each goal, side by side,
and the caller decides which one to sort by (`candidates.py`).

**What a goal here does and does not do.** It reads a finished
`model.Build` and the context. It never sees the base state and never forms a
difference -- the marginal contribution is the caller's subtraction (do-not
rule 20). It never calls `weapons.rate` or `weapons.rank`: an armament's
figure comes from the facade in `nrplanner/damage.py` and from nowhere else,
which `tests/test_one_build.py::test_only_the_facade_calls_weapons_rate_or_rank`
holds for this package as it does for every tab (AD-021).

**Adding a third goal** is one function and one registry entry. It must not
need a change in `candidates.py`, `evaluate.py` or the search; if it does,
the shape here is wrong and belongs in `ARCHITECTURE.md` before it is built.
"""

from __future__ import annotations

# The standard library's `types`, not the module beside this one: absolute
# imports mean this line cannot reach `advisor/types.py`, but a reader can be
# caught by the two names, and this project has already lost a test round to
# one shadowed module name (QA-072).
from types import MappingProxyType

from .. import damage, model
from . import types


#: The eight fields that say how much of an incoming hit gets through: the
#: four physical kinds and the four elemental ones. Neutral is 1.0, below 1.0
#: is less damage taken.
#:
#: **Scope, said out loud because a list without one is read as a list without
#: limits:** these eight and nothing else. Status ailments
#: (`bloodDamageRate` and its three relatives), stance damage
#: (`toughnessDamageCutRate`) and the resistance points in
#: `model.RESISTANCES` are all real and all outside this figure; the
#: `unknowns` below say so. `model.RATE_LABELS` names all of them, which is
#: why the list here is written out rather than filtered out of that table by
#: a name pattern.
DAMAGE_CUT_FIELDS = (
    "slashDamageCutRate",
    "blowDamageCutRate",
    "thrustDamageCutRate",
    "neutralDamageCutRate",
    "magicDamageCutRate",
    "fireDamageCutRate",
    "thunderDamageCutRate",
    "darkDamageCutRate",
)

EVEN_WEIGHTING = types.Weighting(
    id="even",
    label="All damage types equally",
    note=("The game data gives no relative frequency of damage types, so all "
          "eight are weighted equally."),
    weights=tuple((field_name, 1.0) for field_name in DAMAGE_CUT_FIELDS),
)

#: Until a control for OF-3 exists, every run is asked with this one. Changing
#: it is a different `Weighting` instance passed by the caller, never an edit
#: to the goal function -- `weighting.id` is part of the cache key, so a
#: mutated default would be served stale results.
DEFAULT_WEIGHTING = EVEN_WEIGHTING


# The three things an attack rating cannot tell the player, whatever the
# build. Written as a constant so that both branches of `_max_damage` carry
# them and neither can be trimmed on its own.
_ATTACK_RATING_UNKNOWNS = (
    "Attack rating has not been verified against an in-game number.",
    "Spell damage is not in the game data, so spells are not rated.",
    "Critical-only bonuses are excluded — attack rating is the ordinary hit.",
)

_NO_ARMAMENT = ("No armament selected — ranked on attack multipliers only, "
                "without weapon scaling.")

_NO_ARMAMENT_NOTE = ("With no armament chosen there is nothing to scale, so "
                     "the five attack multipliers are averaged with equal "
                     "weight.")

_DAMAGE_TAKEN_UNKNOWNS = (
    "The game data gives no relative frequency of damage types, so the "
    "weighting between them is an assumption.",
    "Ailment and status resistance are not part of this figure.",
    "Only the damage reduction the equipped effects carry is counted; "
    "nothing else that lowers damage in play is in this figure.",
)


def _attack_multiplier_mean(build: model.Build) -> float:
    """The mean of the five attack multipliers, for a build with no armament.

    OF-5, confirmed by the `director`: a run without a reference armament is
    not refused, it is answered against a named assumption. This is that
    assumption, and `_NO_ARMAMENT_NOTE` states it in the result.

    The five fields come from `damage.AR_RATE_FOR`, the facade's own account
    of which multiplier reaches which damage type, so this cannot drift from
    the figure the armament branch produces. Attribute bonuses move nothing
    here, and that is correct rather than a gap: without an armament there is
    no scaling for them to feed.
    """
    rates = [build.rates.get(field_name, 1.0)
             for field_names in damage.AR_RATE_FOR.values()
             for field_name in field_names]
    return sum(rates) / len(rates)


def _max_damage(build: model.Build, ctx: types.GoalContext) -> types.GoalScore:
    """What this build hits for with the reference armament.

    Asked through `damage.equipped`, which is the question the weapon panel
    asks -- the armament in its slot, at its tier, with the
    starting-armament pairing worked out from the slot and the Nightfarer
    rather than handed in (AD-020 point 6). `damage.candidate` would answer a
    different question: an armament in no slot, which cannot carry the
    starting-armament penalty at all (AD-020 point 3). The ranking would
    survive that swap -- the penalty is a constant factor over every
    candidate -- but the absolute figure would not, and AD-014.6 keeps the
    absolute figure as the one authority.

    `equipped` returns the bare comparison figure beside the real one; only
    the second is the ranking size. The first is the breakdown panel's
    left-hand column and is computed here whether it is read or not, which is
    a cost worth naming: it is a second `weapons.rate` per evaluation. See
    the report to the `performance-tuner` for S11.
    """
    unknowns = _ATTACK_RATING_UNKNOWNS
    if ctx.reference is None:
        mean = _attack_multiplier_mean(build)
        # No unit: the figure is a ratio, not an attack rating, and `UI_SPEC`
        # §3.3 drops the "AR" suffix -- and with it the attack-rating
        # reservation -- exactly when the unit is empty.
        return types.GoalScore(
            value=mean,
            display=f"Attack multipliers ×{mean:.2f}",
            unit="",
            unknowns=unknowns + (_NO_ARMAMENT,),
            weights_note=_NO_ARMAMENT_NOTE,
        )
    _bare, now = damage.equipped(ctx.reference, ctx.reference.slot_index,
                                 build, ctx.hero, ctx.data)
    return types.GoalScore(
        value=now.final_total,
        display=f"Attack rating {now.final_total:.0f}",
        unit="AR",
        unknowns=unknowns,
    )


def _min_damage_taken(build: model.Build,
                      ctx: types.GoalContext) -> types.GoalScore:
    """How much this build can take before it falls over, as effective HP.

    HP divided by what gets through, one damage kind at a time, then averaged
    over the eight with the weights the context carries. Bigger is better, so
    it ranks the same way round as the damage goal does and one comparison
    serves both.

    **The averaging is an assumption and it is spoken out loud**, in
    `weights_note` and again in `unknowns`: nothing in the game files says how
    often a player meets fire rather than slash. Whoever knows better passes a
    different `Weighting`; the goal holds no numbers of its own (AD-004,
    OF-3).

    A damage-cut factor is never zero in this dataset: measured over all 2076
    effects of data_version 10350000 on 2026-09-03, the eight fields carry 421
    values between them, the smallest of which is 0.52 and none of which is
    zero or negative -- so a product of them is positive as well. There is
    therefore no branch here for a zero divisor: a branch no data can reach is
    the dead code QA-061 had this project delete, and a division that fails
    loudly beats one that guesses. The two preconditions a caller *can* get
    wrong are checked instead, because a caller is not the dataset.
    """
    weights = dict(ctx.weighting.weights)
    if not weights:
        raise ValueError(
            f"weighting {ctx.weighting.id!r} carries no weights, so there is "
            f"nothing to average the eight damage kinds with")
    hp = build.derived.get("HP")
    if hp is None:
        raise ValueError(
            "this build has no HP: the dataset handed to the advisor carries "
            "no attribute curves, so effective HP cannot be formed")
    # `derived` is (before relics, after relics); the figure the player has is
    # the second.
    after = hp[1]
    total = sum(weights.values())
    effective = sum(weight * after / build.rates.get(field_name, 1.0)
                    for field_name, weight in weights.items()) / total
    return types.GoalScore(
        value=effective,
        display=f"Effective HP {effective:.0f}",
        unit="effective HP",
        unknowns=_DAMAGE_TAKEN_UNKNOWNS,
        weights_note=ctx.weighting.note,
    )


MAX_DAMAGE = types.Goal(
    id="max_damage",
    label="Maximise damage",
    blurb="Ranks by what your reference armament hits for.",
    score=_max_damage,
)

MIN_DAMAGE_TAKEN = types.Goal(
    id="min_damage_taken",
    label="Minimise damage taken",
    blurb="Ranks by how much punishment the build absorbs.",
    score=_min_damage_taken,
)

#: The registry. Read-only: a goal added at run time would not be in any cache
#: key, and the entries a run was scored under would stop being knowable.
GOALS = MappingProxyType({
    MAX_DAMAGE.id: MAX_DAMAGE,
    MIN_DAMAGE_TAKEN.id: MIN_DAMAGE_TAKEN,
})
