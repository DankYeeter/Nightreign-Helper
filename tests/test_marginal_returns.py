"""The same +attribute relic must be worth less once that attribute is high.

`ARCHITECTURE.md` checkpoint 16, and the property the whole build advisor
rests on. The advisor values a candidate by its **marginal contribution** --
`compute(build + candidate) - compute(build)` run through
`damage.attack_rating` (AD-018) -- and the diminishing return the user asked
for in F2 ("a +Strength matters less when I already have a lot of Strength")
is nothing other than the slope of that curve. A constant offset cancels in a
difference; a wrong slope does not. Until this file existed, nothing in the
suite measured the slope at all.

**What the arithmetic actually does, measured rather than assumed.** The
scaling comes from `weapons.rate`, which is linear in
`model.evaluate_curve(curve, attribute)`, and every calc curve the armaments
in this dataset use (0, 4 and 16) is piecewise linear with all four
adjustment exponents at 1.0. So the marginal contribution is **constant
inside a segment and drops at each soft cap** -- for curve 0 the breakpoints
are at 24, 49 and 74, and one point of Strength is worth 4.00, then 2.88,
then 1.92, then 0.96 curve units.

That is why the assertions below are "never rises" plus "is smaller at the
top than at the bottom", and not "falls at every step": a strictly falling
ladder is not what the game's data says, and a test demanding it would be
demanding a bug. It is also worth knowing one storey up -- two candidates in
the same segment tie exactly, so whatever shows these numbers has to cope
with a tie rather than promise a strict order.

The ladder is built from the Nightfarer's own level table, which is the only
source of a *rising* attribute that costs nothing to arrange. The candidate
is required to grant the same amount at every rung: a stat swap grants more
at a higher level, and a candidate that grows along its own ladder produces a
rising marginal that says nothing about the model.
"""

from __future__ import annotations

import pytest

from nrplanner import damage, model

from tests.weapon_damage_cases import hero_by_name

# The plainest armament state there is: rarity tier 1, no reinforcement.
# Reinforcement multiplies base and scaling alike, so it would scale every
# figure below by one constant and change nothing about the shape under test.
TIER = 1

# Three Nightfarers, three attributes, so a single attribute cannot carry the
# result by luck. Each is the attribute that Nightfarer's own level table
# climbs fastest, which is what gives the ladder its range.
LADDERS = [("Wylder", "Strength"),
           ("Ironeye", "Dexterity"),
           ("Recluse", "Intelligence")]


def rising_levels(hero: dict, attribute: str) -> list[int]:
    """The levels at which this Nightfarer's `attribute` is strictly higher.

    Levels that repeat the previous value are left out: they would be the
    same rung twice and would turn "never rises" into a claim about float
    equality rather than about the curve.
    """
    out: list[int] = []
    highest = None
    for key in sorted(hero["levels"], key=int):
        value = hero["levels"][key].get(attribute, 0)
        if highest is None or value > highest:
            out.append(int(key))
            highest = value
    return out


def level_independent_candidate(data: dict, hero: dict, attribute: str,
                                levels: list[int]) -> dict:
    """The lowest-numbered effect granting one fixed `attribute` bonus.

    Fixed meaning the same at every rung of the ladder.

    Asked of `model.compute` rather than read off the modifier names, as the
    golden cases are: a stat swap carries its numbers in HeroStatusParam and
    would not be found by looking for an attribute field, and it is exactly
    the kind that must not be chosen.
    """
    curves = data.get("curves", {})
    for key in sorted(data["effects"], key=int):
        effect = data["effects"][key]
        deltas = set()
        for level in levels:
            build = model.compute(hero, level, [effect], curves)
            deltas.add(build.attributes.get(attribute, 0)
                       - build.base_attributes.get(attribute, 0))
        if len(deltas) == 1 and deltas.pop() > 0:
            return effect
    raise LookupError(
        f"this dataset has no effect that raises {attribute} by a fixed "
        f"amount for {hero['name']}")


def marginal_contribution(data: dict, hero: dict, level: int, weapon: dict,
                          candidate: dict) -> float:
    """What the candidate adds to this armament's attack rating at this level.

    The advisor's own measure, taken through the advisor's own path: two
    builds from `model.compute`, both run through `damage.attack_rating`, and
    the difference of the finished figures.
    """
    curves = data.get("curves", {})
    without = model.compute(hero, level, [], curves,
                            weapon=weapon, weapons_held=[weapon])
    with_it = model.compute(hero, level, [candidate], curves,
                            weapon=weapon, weapons_held=[weapon])
    return (damage.attack_rating(weapon, TIER, with_it, data).final_total
            - damage.attack_rating(weapon, TIER, without, data).final_total)


def most_responsive_armament(data: dict, hero: dict, attribute: str,
                             candidate: dict, level: int) -> dict:
    """The armament this candidate moves furthest at the bottom of the ladder.

    Chosen by measuring rather than by naming an id: which attribute feeds
    which damage type is decided by AttackElementCorrectParam, so an armament
    with a large Strength coefficient can still be unmoved by Strength, and a
    case built on one would compare zero against zero and pass on nothing.

    Restricted to armaments this Nightfarer can already hold at the lowest
    rung. An unmet requirement drops the scaling contribution entirely, so an
    armament that becomes usable partway up the ladder would show a jump from
    nothing to something -- a rise, and one that is a property of the
    requirement check rather than of the curve.
    """
    attributes = hero["levels"][str(level)]
    best_weapon = None
    best_key = None
    for weapon in data["weapons"]:
        if not (weapon.get("scaling") or {}).get(attribute):
            continue
        if any(attributes.get(stat, 0) < needed
               for stat, needed in weapon["requires"].items() if needed):
            continue
        gain = marginal_contribution(data, hero, level, weapon, candidate)
        # Largest gain wins; the lowest id breaks a tie, so two runs against
        # one dataset choose the same armament.
        key = (gain, -weapon["id"])
        if best_key is None or key > best_key:
            best_key, best_weapon = key, weapon
    if best_weapon is None:
        raise LookupError(
            f"no armament in this dataset scales on {attribute} and is "
            f"usable by {hero['name']} at level {level}")
    return best_weapon


@pytest.fixture(scope="module", params=LADDERS, ids=lambda p: f"{p[0]}-{p[1]}")
def ladder(request, game_data):
    """One (attribute, marginal contribution) ladder, computed once per pair.

    Module-scoped because the three assertions below all read the same
    ladder, and building one costs a few hundred milliseconds.
    """
    hero_name, attribute = request.param
    hero = hero_by_name(game_data, hero_name)
    levels = rising_levels(hero, attribute)
    candidate = level_independent_candidate(game_data, hero, attribute, levels)
    weapon = most_responsive_armament(game_data, hero, attribute, candidate,
                                      levels[0])
    steps = []
    for level in levels:
        build = model.compute(hero, level, [], game_data.get("curves", {}),
                              weapon=weapon, weapons_held=[weapon])
        steps.append((build.attributes.get(attribute, 0),
                      marginal_contribution(game_data, hero, level, weapon,
                                            candidate)))
    return {
        "hero": hero_name,
        "attribute": attribute,
        "candidate": " ".join(str(candidate.get("name", "")).split()),
        "weapon": weapon["name"],
        "steps": steps,
    }


def describe(ladder: dict) -> str:
    """The whole ladder in the message: the shape is what is being claimed."""
    steps = "  ".join(f"{value}:{gain:.4f}" for value, gain in ladder["steps"])
    return (f"{ladder['hero']} / {ladder['attribute']}, candidate "
            f"{ladder['candidate']!r} on {ladder['weapon']!r} at tier {TIER}"
            f" -- {ladder['attribute']}:gain = {steps}")


def test_the_candidate_is_worth_something_at_the_bottom(ladder):
    """Without this, the two tests below would hold over a ladder of zeroes."""
    _value, first = ladder["steps"][0]

    assert first > 0, (
        "the candidate adds nothing at the bottom of the ladder, so nothing "
        f"below says anything about diminishing returns: {describe(ladder)}")


def test_the_marginal_contribution_never_rises(ladder):
    """Rising returns would rank a relic higher the more of it you have.

    That is the failure the user would see as the advisor recommending more
    Strength precisely where Strength has stopped paying.
    """
    rises = [(ladder["steps"][i], ladder["steps"][i + 1])
             for i in range(len(ladder["steps"]) - 1)
             if ladder["steps"][i + 1][1] > ladder["steps"][i][1] + 1e-9]

    assert not rises, (
        f"the same candidate got worth MORE as {ladder['attribute']} rose, "
        f"at {rises}. Checkpoint 16 says to look in damage.py / model.py, "
        f"not in the advisor: {describe(ladder)}")


def test_the_marginal_contribution_is_smaller_at_the_top(ladder):
    """Never rising is not enough -- a flat line never rises either.

    A flat result here means the arithmetic has no soft cap in it at all,
    which is what linearising the scaling curve produces, and it is the
    difference between an advisor that models the game and one that ranks by
    a straight line.
    """
    (low, first), (high, last) = ladder["steps"][0], ladder["steps"][-1]

    assert last < first, (
        f"the candidate is worth as much at {ladder['attribute']} {high} as "
        f"at {low}, so this ladder shows no diminishing return. Either the "
        f"scaling curve has been flattened, or the ladder no longer crosses "
        f"a soft cap: {describe(ladder)}")
