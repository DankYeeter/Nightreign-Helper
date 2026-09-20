"""The named directions to optimise in, as a registry of pure functions.

AD-004: a goal is not a number, it is a number **with a stated scope**. Each
entry below therefore carries a `Goal.scope` that is never empty -- where the
game files do not support a judgement, the registry says so instead of
guessing (`GOAL.md` A7). What the *run* left out is a different sentence and
goes back in `GoalScore.unknowns`, which may be empty; AD-025 splits the two
by the question "can the sentence be written before the run is known?", and
makes the answer a property of where the sentence lives rather than of how it
was worded.

**One figure per direction, never a mixed one.** There is no conversion
between damage dealt and damage survived, and none between an attribute point
and an attack multiplier either; inventing an exchange rate is what AD-023 and
OF-13 forbid: a curse that costs HP under "Maximise damage" is counted in the
build, is *not* in that goal's ranking figure, and is named rather than
marked down. So every candidate carries a gain under each goal, side by side,
and the caller decides which one to sort by (`candidates.py`). AD-032 settled
the third direction the same way: the attribute points a relic brings became
`MAX_ATTRIBUTES` below rather than a summand in `_max_damage`, so the damage
figure goes on saying what it always said.

**What a goal here does and does not do.** It reads a finished
`model.Build` and the context. It never sees the base state and never forms a
difference -- the marginal contribution is the caller's subtraction (do-not
rule 20). It never calls `weapons.rate` or `weapons.rank`: an armament's
figure comes from the facade in `nrplanner/damage.py` and from nowhere else,
which `tests/test_one_build.py::test_only_the_facade_calls_weapons_rate_or_rank`
holds for this package as it does for every tab (AD-021).

**Adding a goal** is one function and one registry entry. It must not need a
change in `candidates.py`, `evaluate.py` or the search; if it does, the shape
here is wrong and belongs in `ARCHITECTURE.md` before it is built. The third
one, `MAX_ATTRIBUTES`, was built that way and needed neither -- what it did
need is a place on the screen, and that is not here: `advisorbar.GOAL_ORDER`
is the list a player reads and its order is a decision of the
`ui-ux-designer`. Its **membership** is not a decision any more (AK-256
point 1): every direction this registry scores stands in that tuple, because
a direction scored and cached with no way to choose it is one the player pays
for and cannot reach -- the state this file left behind between T-191 and
T-194 (QA-228). So a fourth entry here is a fourth entry there, a fourth
`Sort by` line and a fourth value row on every card, and the guard that says
so is
`tests/test_advisor_bar.py::test_every_direction_the_registry_scores_can_be_chosen`.
"""

from __future__ import annotations

# The standard library's `types`, not the module beside this one: absolute
# imports mean this line cannot reach `advisor/types.py`, but a reader can be
# caught by the two names, and this project has already lost a test round to
# one shadowed module name (QA-072).
from types import MappingProxyType

from .. import damage, model, weapons
from . import types


#: The eight fields that say how much of an incoming hit gets through: the
#: four physical kinds and the four elemental ones. Neutral is 1.0, below 1.0
#: is less damage taken.
#:
#: **Scope, said out loud because a list without one is read as a list without
#: limits:** these eight and nothing else. Status ailments
#: (`bloodDamageRate` and its three relatives), stance damage
#: (`toughnessDamageCutRate`) and the resistance points in
#: `model.RESISTANCES` are all real and all outside this figure;
#: `_DAMAGE_TAKEN_SCOPE` below says so. `model.RATE_LABELS` names all of them,
#: which is why the list here is written out rather than filtered out of that
#: table by a name pattern.
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


# The four things this figure cannot tell the player, whatever the build --
# procedural sentences in the sense of AD-025.1, so they hang on
# `MAX_DAMAGE.scope` and not on a score. They used to be a default for both
# branches of `_max_damage`; the registry is the stronger version of the same
# guarantee, because a run cannot empty it and a reader needs no dataset to
# see it (checkpoint 29).
#
# The first line used to read "Attack rating has not been verified against an
# in-game number", and that is simply no longer true: 2256 comparisons
# against the game's own display settled it (QA-095). What replaces it is not
# silence but the **scope** of the agreement, because a figure that says it
# matches the game and does not say where is the failure this project keeps
# having (A7).
#
# The second line used to say that staves and seals were outside the match --
# that this program showed their physical attack rating where the game showed
# a spell scaling. Since T-046 it does not: a catalyst is shown and ranked by
# the game's own figure (QA-099). A reservation against a fault that has been
# fixed is the stale line the next reader repeats as fact, so it is gone and
# what stands in its place is the **scope** of the new figure -- the base
# rarity is what was measured, and the figure is the game's display and not a
# statement about what a spell hits for.
#
# A third line used to say that a damage-type conversion was not in this
# figure. It was measured on 2026-09-19 and it is: the goal ranks on the
# Nightfarer's own starting armament in slot 1 (AD-038), which is the one
# place `damage.converted` applies, and the four relics move it by +1.80 on
# Wylder and +2.78 on Revenant. The sentence was deleted rather than softened
# (AD-047 point 6) -- a weaker version of a false reservation is the same
# reservation said more quietly.
_ATTACK_RATING_SCOPE = (
    "Attack rating matches the game's own display for ordinary armaments at "
    "their own rarity; reinforced rarities, infused variants, Scholar and "
    "Undertaker were not measured.",
    # `spell power`, not `spell scaling`: AK-88, and the director's addendum
    # of 05.09. that binds it to displayed text. The arsenal tile says
    # `Spell power` on up to 1 792 cards; this sentence is drawn once, so it
    # is the sentence that gives way.
    "For staves and seals the figure is the spell power the game shows, "
    "measured at their own rarity only, and it is that display and not what "
    "a spell hits for.",
    "Spell damage is not in the game data, so spells are not rated.",
    "Critical-only bonuses are excluded — attack rating is the ordinary hit.",
    # AD-038: the armament the figure is formed against is a property of the
    # Nightfarer, not of the grid (A17), and it is named here so that the
    # figure says what it is scaled on. Wording AK-318.1.
    "Scaled on the Nightfarer's own starting armament at its lowest tier, "
    "without the roles a carried copy could add; one- or two-handed as the "
    "stat sheet's hand switch says.",
)

# Fallback texts (AD-038.1, AK-318.2): spoken only when the dataset has no
# record for the Nightfarer's starting armament, so the run ranks on the
# multiplier mean and names that cause instead of inventing a scaling (A7).
_NO_ARMAMENT = ("This Nightfarer's starting armament has no entry in the "
                "game data, so this run is ranked on attack multipliers "
                "only, without weapon scaling.")

_NO_ARMAMENT_NOTE = ("With no armament on record there is nothing to scale, "
                     "so the five attack multipliers are averaged with equal "
                     "weight.")

#: The five attributes an armament's damage scales on -- the ones AD-032
#: calls offensive. Written out rather than filtered out of
#: `model.ATTRIBUTE_ORDER` by a name pattern, for the reason
#: `DAMAGE_CUT_FIELDS` is: a list is read as a list of everything unless it
#: says otherwise, and the three left out (Vigor, Mind, Endurance) are left
#: out by a decision, not by their spelling.
#:
#: **Which five is a decision and not a reading of the files** -- that is why
#: it is AD-032's sentence and not a derivation. The dataset agrees with it
#: today, and `tests/test_advisor_goals.py::
#: test_the_offensive_attributes_are_the_ones_armaments_scale_on` is where
#: that agreement is measured rather than assumed; it fails on the day the
#: game gives a sixth stat a scaling coefficient.
OFFENSIVE_ATTRIBUTES = ("Strength", "Dexterity", "Intelligence", "Faith",
                        "Arcane")

#: What the attribute figure is measured in, on the one line that says it and
#: in `GoalScore.unit` -- AD-032's word, written once so the goal line and
#: any column header cannot drift apart.
ATTRIBUTE_POINT_UNIT = "pts"

#: What counting points cannot tell the player, whatever the build -- the
#: procedural sentences of AD-025.1 for the third direction. The first is the
#: one that matters: this figure is deliberately *not* weighted by what the
#: build scales on, because weighting it by scaling is Option B of AD-032
#: built with more steps, and it needs an armament this run does not have.
_ATTRIBUTE_SCOPE = (
    "Attribute points are counted, not converted into damage: ten points of "
    "Faith count as much as ten of Strength, whatever this build scales on.",
    "Only the five attributes an armament scales on are counted — Strength, "
    "Dexterity, Intelligence, Faith and Arcane. Vigor, Mind and Endurance "
    "are outside this figure.",
    "Whether a point is worth anything depends on the armament in hand, and "
    "this direction is asked without one.",
    "What an attribute unlocks rather than scales — an armament's own "
    "requirement — is not in this figure.",
)

_DAMAGE_TAKEN_SCOPE = (
    "Effective HP assumes each damage-reduction rate multiplies the damage "
    "you take; the game files name the fields, not how the engine applies "
    "them.",
    "The game data gives no relative frequency of damage types, so the "
    "weighting between them is an assumption.",
    "Ailment and status resistance are not part of this figure.",
    "Only the damage reduction the equipped effects carry is counted; "
    "nothing else that lowers damage in play is in this figure.",
)


#: The two kinds of choice `damage_art` can carry (AD-045 point 1). Split
#: here and nowhere else: what leaves this module is either a damage type or
#: an art key, never the prefixed form.
_TYPE_CHOICE = "type"
_ART_CHOICE = "art"

#: AK-331, word for word, with the chosen entry's own label in it, first
#: letter lowered the way `advisorbar` lowers a goal label. A run finding and
#: not a scope sentence (AD-025.2): before the run nobody knows whether an
#: art was chosen at all.
_RANKED_ON_ONE_ART = (
    "Ranked on {choice} damage only — every other effect on a candidate "
    "still shows, but only this counts toward the ranking.")

#: AD-048: for a staff or a seal the game shows a spell power and no attack
#: rating, and nothing measured says what an attack buff does to that
#: display. So the choice is answered instead of being applied to a figure
#: that cannot carry it -- the relationship it would need is one this
#: program would be inventing (A7).
_ART_ON_A_CATALYST = (
    "{choice} is not counted for this Nightfarer: a staff or a seal is "
    "ranked on the spell power the game shows for it, and no damage type "
    "and no attack art reaches that figure.")


def chosen_label(damage_art: str) -> str:
    """What the player picked, in the words the dataset or the spec gives it.

    The schools bring their own name out of `spell_families` and the five
    types theirs out of `weapons.DAMAGE_LABELS`; only the three arts the
    files do not name have a wording of their own, and it is the spec's
    (AK-328). Nothing is made up here, which is why a key this program cannot
    name raises instead of falling back on the key itself: a sentence built
    around `family:23` would be the invented label AD-046 point 5 keeps out
    of the chooser, arriving through the back door.

    The labels are game text and go on into `unknowns`, into the picker's
    caption/chip (`relicpicker._named_for_choice`, AK-336) and into the goal
    card's headline (`_max_damage`, AK-335) -- one lookup for all three, so a
    dataset patch that renames a school reaches every sink at once.
    Every sink that draws them is `Qt.PlainText` (`advisorblock._footer_text`
    and the picker's `findings`/`caveats`), so they are passed on as they are
    written -- escaping them here would show a school called `Bell &
    Bearing` its own `&amp;` (SEC-019, AK-29).
    """
    kind, _, key = damage_art.partition(":")
    label = None
    if kind == _TYPE_CHOICE:
        label = weapons.DAMAGE_LABELS.get(key)
    elif kind == _ART_CHOICE:
        label = model.ART_LABELS.get(key)
        if label is None and key.startswith(model.ART_FAMILY_PREFIX):
            family = key[len(model.ART_FAMILY_PREFIX):]
            if family.isdigit():
                label = model.SPELL_FAMILY_NAMES.get(int(family))
    if label is None:
        raise ValueError(
            f"{damage_art!r} names no damage type and no attack art this "
            f"dataset carries, so there is no question here to answer")
    return label


def _headline_with_choice(chosen: str, headline_name_lower: str) -> str:
    """`"{chosen} {headline_name_lower}"`, without saying the shared word twice.

    AK-335's word-collision rule: `"Skill attack"` before `"attack rating"`
    would read `"Skill attack attack rating"` -- the choice's last word and
    the name's first word name the same thing. Dropped here and only here;
    every other combination (`"Fire"` + `"attack rating"`) has no shared word
    and comes out exactly as written.
    """
    name_words = headline_name_lower.split()
    if name_words and chosen.split()[-1].lower() == name_words[0]:
        name_words = name_words[1:]
    return " ".join([chosen, *name_words])


def _attack_multiplier_mean(build: model.Build, two_handed: bool) -> float:
    """The mean of the five attack multipliers: the figure the program ranks by.

    OF-5, confirmed by the `director`: a run without a reference armament is
    not refused, it is answered against a named assumption. This is that
    assumption, and `_NO_ARMAMENT_NOTE` states it in the result.

    Between A17 and AD-038 this was the ordinary case; since AD-038 the
    program ranks against the Nightfarer's starting armament, and this is
    reached only when the dataset has no record of it (`advisorbar.
    asking_from`).

    The five fields come from `damage.AR_RATE_FOR`, the facade's own account
    of which multiplier reaches which damage type, so this cannot drift from
    the figure the armament branch produces. Attribute bonuses move nothing
    here, and that is correct rather than a gap: without an armament there is
    no scaling for them to feed. Where they *are* counted is
    `MAX_ATTRIBUTES`, a direction of its own: AD-032 put them there rather
    than into this mean, so that this figure goes on saying what it said.

    Two-handed, the `when Two-Handing` bucket multiplies into each field the
    way `damage._answer` multiplies it into the two-handed figure (AK-293
    point 2); one-handed it stays out, as it does of every one-handed figure.
    """
    hand = (build.class_rates.get(model.TWO_HANDED_CLASS, {})
            if two_handed else {})
    rates = [build.rates.get(field_name, 1.0) * hand.get(field_name, 1.0)
             for field_names in damage.AR_RATE_FOR.values()
             for field_name in field_names]
    return sum(rates) / len(rates)


def _max_damage(build: model.Build, ctx: types.GoalContext) -> types.GoalScore:
    """What this build hits for -- with an armament only when given one.

    **The branch the program takes is the second one** (AD-038, `GOAL.md`
    A22): `advisorbar.asking_from` hands in the Nightfarer's own starting
    armament as `reference`, at its lowest tier and without its rolls, and
    no grid. That armament is a property of the dataset rather than of what
    the player carries, so A17 still holds -- the grid moves nothing -- and
    an attribute a relic moves reaches the figure through the armament's
    scaling. The first branch is the fallback for a dataset without that
    record (AD-038.1). What follows is about the armament branch.

    Asked through `damage.equipped`, which is the question the weapon panel
    asks -- the armament in its slot, at its tier, with the
    starting-armament pairing worked out from the slot and the Nightfarer
    rather than handed in (AD-020 point 6). `damage.candidate` would answer a
    different question: an armament in no slot, which cannot carry the
    starting-armament penalty at all (AD-020 point 3).

    **The ranking would not survive that swap either**, and the reason this
    docstring used to say it would is worth keeping: the penalty looks like a
    constant factor over the candidates, and it is not, because a candidate
    can **bring it with it**. Three effects of this dataset carry
    `*AttackPowerRate` 0.85 themselves -- 7120400/500/600, "Starting armament
    inflicts frost / poison / blood loss" -- and 10 of the 309 relics on the
    save the `qa-engineer` measured against carry one. Re-measured here on
    2026-09-05, Wylder at level 15 with his own starting armament in slot 1 at
    tier 1: a candidate carrying `[7120400, 6001400]` gains −7.4146 asked as
    `equipped` and +12.8153 asked as `candidate`, while one carrying
    `[7000300]` gains +0.4977 either way -- so the two change places (QA-101).
    `equipped` is therefore the more right of the two rather than merely the
    more exact: a relic that costs the armament 15 % belongs ranked as
    costing it. AD-014.6 keeps the absolute figure as the one authority, and
    here the order agrees with it.

    `equipped` returns the bare comparison figure beside the real one; only
    the second is the ranking size. The first is the breakdown panel's
    left-hand column and is computed here whether it is read or not, which is
    a cost worth naming: it is a second `weapons.rate` per evaluation. See
    the report to the `performance-tuner` for S11.

    **`ctx.damage_art` is read here and in no other direction** (AD-045): it
    says which kind of damage this question is about, and it is the one place
    in the program that takes its prefix apart. A damage type is a different
    number of the same answer -- `final_per_type` instead of the headline,
    nothing recalculated. An attack art is a condition of the question and
    goes to the facade as `art=`, which multiplies it where every other rate
    is multiplied (AD-047). Empty is every kind at once and is the figure
    this goal has always given, down to the last bit.
    """
    if ctx.reference is None:
        mean = _attack_multiplier_mean(build, ctx.two_handed)
        # No unit: the figure is a ratio, not an attack rating, and `UI_SPEC`
        # §3.3 drops the "AR" suffix -- and with it the attack-rating
        # reservation -- exactly when the unit is empty.
        #
        # `_NO_ARMAMENT` is the pattern case of a run finding (AD-025.1): the
        # wording could be written down before any run, but whether it holds
        # could not, and a sentence that stood there with an armament chosen
        # would be false. That is why the yardstick asks about both halves.
        return types.GoalScore(
            value=mean,
            display=f"Attack multipliers ×{mean:.2f}",
            unit="",
            unknowns=(_NO_ARMAMENT,),
            weights_note=_NO_ARMAMENT_NOTE,
        )
    kind, _, key = ctx.damage_art.partition(":")
    # Raises on a choice this program cannot name, before any figure is
    # formed: a run ranked on a question nobody could have asked is worse
    # than a run that stops.
    chosen = chosen_label(ctx.damage_art) if ctx.damage_art else ""
    _bare, now = damage.equipped(ctx.reference, ctx.reference.slot_index,
                                 build, ctx.hero, ctx.data,
                                 art=key if kind == _ART_CHOICE else None)
    # Two-handed where the switch says so and the armament allows it; an
    # armament without a second figure keeps its one (AK-293 point 3).
    if ctx.two_handed and now.two_handed is not None:
        now = now.two_handed
    # `value` is the unrounded figure and `display` the truncated one, and
    # they are deliberately not the same number: the ranking and the marginal
    # contribution are formed from `value`, so a digit that exists only for
    # the screen cannot decide which relic the advisor recommends (QA-074).
    # The text goes through the facade's one formatter, so this line and the
    # weapon panel show the same whole number for the same armament.
    #
    # Which figure that is, and what it is called, comes from the facade as
    # well: with a staff or a seal as the reference armament the goal ranks
    # on the spell scaling the game shows for it, because the physical rating
    # it used to rank on is a quantity the game never puts on screen for a
    # catalyst (QA-099).
    # `unknowns` is empty unless a kind of damage was chosen, and that empty
    # tuple is an answer rather than a gap (AD-025.2): with an armament
    # chosen and every kind counted, this run left nothing out. What the
    # figure cannot know whatever the run stands in `MAX_DAMAGE.scope`.
    value = now.final_headline
    name = now.headline_name
    unknowns: tuple[str, ...] = ()
    if chosen:
        if now.catalyst_scaling is not None:
            # AD-048: the choice reaches nothing here, and saying so is the
            # answer. Applying it anyway would put a damage rate on a
            # scaling number, which is the relationship A7 forbids inventing.
            unknowns = (_ART_ON_A_CATALYST.format(choice=chosen),)
        else:
            if kind == _TYPE_CHOICE:
                # A type this armament deals none of ranks at 0.00, which is
                # a ranking and not a fault: every candidate that brings some
                # of it then stands above every candidate that does not.
                value = now.final_per_type.get(key, 0.0)
                name = _headline_with_choice(chosen, now.headline_name.lower())
            elif key in now.rates:
                # AK-335: an art choice only earns the headline once it has
                # actually moved the value away from `All` -- `now.rates`
                # carries the art's own key exactly when `damage._answer`
                # found `art_rate != 1.0` for it. Where no relic scopes a
                # buff to this art the figure is the `All` figure verbatim,
                # and the headline stays `"Attack rating"` to match it.
                name = _headline_with_choice(chosen, now.headline_name.lower())
            unknowns = (_RANKED_ON_ONE_ART.format(
                choice=chosen[0].lower() + chosen[1:]),)
    return types.GoalScore(
        value=value,
        display=f"{name} {damage.displayed(value)}",
        unit=now.headline_label,
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
    `weights_note` and again in `MIN_DAMAGE_TAKEN.scope`: nothing in the game
    files says how often a player meets fire rather than slash. The two are
    not a repetition -- `weights_note` names *this* run's weighting and comes
    out of the context, the scope line says that a weighting has to be assumed
    at all and is true of every run (AD-025.3). Whoever knows better passes a
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
        weights_note=ctx.weighting.note,
    )


def _max_attributes(build: model.Build,
                    ctx: types.GoalContext) -> types.GoalScore:
    """The offensive attribute points this build stands at (AD-032, C).

    The third direction, and the one the App Designer chose A17 to be read
    with: *"wir optimieren die stats und passiven am besten weil nur die fix
    sind"*. An attribute bonus is written on the relic and waits for nothing
    -- no armament, no roll, no expedition -- so it is fixed between runs in
    the strongest sense this dataset offers, which is what makes it rankable
    when the armament is gone.

    **A sum of points and nothing else.** No weight per attribute, no
    conversion into an attack rating: both would be the invented exchange
    rate AD-023 and OF-13 forbid, and the weighted version is Option B of
    AD-032 -- rank against an armament -- reached by a longer road. The price
    is named in `MAX_ATTRIBUTES.scope` rather than discounted: ten points of
    Faith on a Wylder count as much here as ten of Strength.

    The absolute standing, not a gain. Like every entry here it reads one
    finished build and never the base state; the marginal contribution is the
    caller's subtraction (do-not rule 20), and against an empty base state
    that difference is exactly the points the relics brought.

    `ctx` is unread, and that is the honest shape rather than an oversight:
    this figure needs no dataset, no hero and no weighting, because
    `model.compute` has already applied every stat swap, cap and floor the
    build has. It stays in the signature because `Goal.score` is one type for
    every direction.
    """
    del ctx  # the signature is the registry's, not this function's need
    points = sum(build.attributes.get(attribute, 0)
                 for attribute in OFFENSIVE_ATTRIBUTES)
    # `value` unrounded like everywhere else (QA-074), even though points are
    # whole today: a stat swap could yet arrive at a half, and the rule that
    # the screen's digits never decide a ranking does not take exceptions.
    return types.GoalScore(
        value=float(points),
        display=f"Offensive attributes {points:.0f}",
        unit=ATTRIBUTE_POINT_UNIT,
    )


MAX_DAMAGE = types.Goal(
    id="max_damage",
    label="Maximise damage",
    blurb="Ranks by attack multipliers, attributes and passives — what "
          "stays fixed between runs.",
    scope=_ATTACK_RATING_SCOPE,
    score=_max_damage,
)

MIN_DAMAGE_TAKEN = types.Goal(
    id="min_damage_taken",
    label="Minimise damage taken",
    blurb="Ranks by how much punishment the build absorbs.",
    scope=_DAMAGE_TAKEN_SCOPE,
    score=_min_damage_taken,
)

#: **`label` is the wording AK-257 settled**, and it is on screen: the
#: `Sort by` box and the Advisor bar both draw it from here, so this line is
#: a promise to a player rather than a name in a registry. It is not
#: `Maximise attributes`, which would be shorter and would promise eight
#: attributes where five are counted; the long one was measured to fit the
#: narrower of the two boxes with 17 px to spare.
#:
#: `blurb` is still read by nothing in `nrplanner/` -- AK-256's list is about
#: labels, and §5.4 leaves the blurb alone until something draws it.
MAX_ATTRIBUTES = types.Goal(
    id="max_attributes",
    label="Maximise offensive attributes",
    blurb="Ranks by the attribute points a relic brings — the part of a "
          "build no expedition rerolls.",
    scope=_ATTRIBUTE_SCOPE,
    score=_max_attributes,
)

#: The registry. Read-only: a goal added at run time would not be in any cache
#: key, and the entries a run was scored under would stop being knowable.
GOALS = MappingProxyType({
    MAX_DAMAGE.id: MAX_DAMAGE,
    MIN_DAMAGE_TAKEN.id: MIN_DAMAGE_TAKEN,
    MAX_ATTRIBUTES.id: MAX_ATTRIBUTES,
})

#: The direction a slot pool is **put in order** under when the question is
#: the picker's -- an ordering for the request, never a direction the player
#: picked (Nachtrag IX-2).
#:
#: A pool's *content* does not depend on the direction: `candidates.pool`
#: measures every candidate under every goal it is given, and only
#: `measured.sort` reads `rank_by`. The cache key does not know that --
#: `run.cache_key` keeps every field of the request but `generation` -- so a
#: picker asking under the player's direction computes and stores one list
#: three times over, once per direction, and a player switching direction pays
#: a full run for a list that was already there.
#:
#: Asking under a fixed direction instead makes one entry serve all of them.
#: What the screen ranks by is then the one goal setting of the program
#: (AK-256), read from there and never from `SlotPool.rank_by` (AK-263): that
#: field goes on saying what ordered this list, which stays true, and the
#: shortcut "what ordered it is also what is read off it" is what stops
#: holding here.
#:
#: The value is the damage goal's id so that a pool arrives in the commonest
#: order, and it is taken off the registry entry rather than written out,
#: because a canonical direction no goal answers to would be refused by every
#: run that used it. The firmness is the point; the value is not.
CANONICAL_POOL_ORDER = MAX_DAMAGE.id
