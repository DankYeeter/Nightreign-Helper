"""Build maths: turn a hero, a level and a set of effects into final stats."""

from __future__ import annotations

from dataclasses import dataclass, field

# SpEffect field -> the attribute it adds to.
ATTRIBUTE_FIELDS = {
    "addLifeForceStatus": "Vigor",
    "addWillpowerStatus": "Mind",
    "addEndureStatus": "Endurance",
    "addStrengthStatus": "Strength",
    "addDexterityStatus": "Dexterity",
    "addMagicStatus": "Intelligence",
    "addFaithStatus": "Faith",
    "addLuckStatus": "Arcane",
}

ATTRIBUTE_ORDER = [
    "Vigor", "Mind", "Endurance", "Strength",
    "Dexterity", "Intelligence", "Faith", "Arcane",
]

# Multiplicative fields worth surfacing, with readable labels.
RATE_LABELS = {
    "maxHpRate": "Max HP",
    "maxMpRate": "Max FP",
    "maxStaminaRate": "Max Stamina",
    "physicsAttackRate": "Physical Attack",
    "magicAttackRate": "Magic Attack",
    "fireAttackRate": "Fire Attack",
    "thunderAttackRate": "Lightning Attack",
    "darkAttackRate": "Holy Attack",
    # The second attack family, carried by the three "Starting armament
    # inflicts ..." relics. Unlabelled until now, so the panel printed the raw
    # field name at the player: "darkAttackPowerRate -15.0%". It no longer
    # reaches the Multipliers panel at all -- it scopes to slot 1, see
    # Planner.STARTING_AR_RATE_FOR -- but the attack-rating breakdown still
    # names it, so the labels are still wanted.
    "physicsAttackPowerRate": "Physical Attack",
    "magicAttackPowerRate": "Magic Attack",
    "fireAttackPowerRate": "Fire Attack",
    "thunderAttackPowerRate": "Lightning Attack",
    "darkAttackPowerRate": "Holy Attack",
    "physicsDefenceRate": "Physical Defence",
    "magicDefenceRate": "Magic Defence",
    "fireDefenceRate": "Fire Defence",
    "thunderDefenceRate": "Lightning Defence",
    "darkDefenceRate": "Holy Defence",
    "staminaRecoverRate": "Stamina Recovery",
    "defenceStatusRate": "Status Resistance",
    # Named from the effects that carry them rather than from the field name,
    # which is how the rest of this table was built and the only way to get
    # them right. Each of these reached the panel as its own raw field name --
    # "toughnessDamageCutRate -5.0%" is what a player saw for Poise +1.
    #
    #   artsConsumptionRate       "Reduced Skill FP Cost" 0.75
    #   magicConsumptionRate      "Reduced Spell FP Cost" 0.75
    #   miracleConsumptionRate    same effect, same value
    #   shamanConsumptionRate     same effect, same value
    #   goodsConsumptionRate      "Reduced FP Consumption" 0.92
    #   extendLifeRate            "Extended Spell Duration" 1.30
    #   staminaAttackRate         "Improved Guard Breaking" 1.50
    #   toughnessDamageCutRate    "Improved Poise" 0.75, "Poise +1" 0.95
    #   characterSkillAttackRate  "[Duchess] Improved Character Skill Attack"
    #
    # The three spell-cost fields are separate because the game separates
    # sorceries, incantations and the Nightreign third school, but every relic
    # that touches one touches all three at the same value, so they are given
    # one name and collapse into a single line rather than three identical ones.
    "artsConsumptionRate": "Skill FP cost",
    "magicConsumptionRate": "Spell FP cost",
    "miracleConsumptionRate": "Spell FP cost",
    "shamanConsumptionRate": "Spell FP cost",
    "goodsConsumptionRate": "Item use cost",
    "extendLifeRate": "Spell duration",
    "staminaAttackRate": "Stamina damage you deal",
    # Stance damage *taken*, so below 1.0 is good -- the same convention as the
    # damage-cut family below. This is what Poise relics move.
    "toughnessDamageCutRate": "Stance damage taken",
    "characterSkillAttackRate": "Character Skill attack power",
    # The remaining four that reached the panel raw. All are real quantities,
    # unlike the engine references above, so all they ever needed was a name.
    #   accumuOverVal           "FP Restoration upon Successive Attacks" 32
    #   changeHpRate / changeMpRate   additive despite the name -- see the
    #                           field_baselines note; 0.0 is neutral, not 1.0
    #   bowDistRate             "Projectile Damage Drop-Off Reduced" 50
    #   guardCounterAttackRate  "Guard counter is given a boost ..." 5.0
    # The ailment damage family, neutral 100. The game's own caption on the
    # effect that carries them says what they are: "Increases damage taken
    # from ailments". All four move together at one value, so they are given
    # one name and collapse to a single line.
    "bloodDamageRate": "Ailment damage taken",
    "freezeDamageRate": "Ailment damage taken",
    "madnessDamageRate": "Ailment damage taken",
    "sleepDamageRate": "Ailment damage taken",
    "accumuOverVal": "Hits needed to trigger",
    "changeHpRate": "HP change",
    "changeMpRate": "FP change",
    "bowDistRate": "Projectile drop-off distance",
    "guardCounterAttackRate": "Guard counter attack power",
    # Damage *taken*, not dealt. These are multipliers on incoming damage, so
    # 0.84 means 16% less damage reaches you. Naming them "... damage taken"
    # keeps the sign honest: -16% is unambiguously good, +45% unambiguously
    # bad, and the reader does not have to know what "cut rate" means.
    "slashDamageCutRate": "Slash damage taken",
    "blowDamageCutRate": "Strike damage taken",
    "thrustDamageCutRate": "Thrust damage taken",
    "neutralDamageCutRate": "Standard damage taken",
    "magicDamageCutRate": "Magic damage taken",
    "fireDamageCutRate": "Fire damage taken",
    "thunderDamageCutRate": "Lightning damage taken",
    "darkDamageCutRate": "Holy damage taken",
    # Named here as well as in effecttext, because the Multipliers panel reads
    # these labels and was still printing the raw field names at the player.
    "changeHpEstusFlaskCorrectRate": "HP restored per flask",
    "changeMpEstusFlaskCorrectRate": "FP restored per flask",
    "regainRate": "Regain — HP won back by attacking after a hit",
    "saAttackPowerRate": "Stance damage",
    "itemDropRate": "Item discovery",
    "soulRate": "Runes gained",
}

# Rates where a value below 1.0 is a benefit, so the usual "positive is good"
# colouring has to be flipped. Getting this wrong showed Improved Fire Damage
# Negation as a red -16%, when it is exactly the effect the player wanted.
INVERTED_RATES = {
    "slashDamageCutRate", "blowDamageCutRate", "thrustDamageCutRate",
    "neutralDamageCutRate", "magicDamageCutRate", "fireDamageCutRate",
    "thunderDamageCutRate", "darkDamageCutRate",
    "magicConsumptionRate", "consumeStaminaRate", "spConsumptionRate",
    "characterSkillCooldownReduction",
    # The rest of the cost family, which was only half here: a relic cutting
    # skill or item cost was being coloured as though the reduction were a
    # loss. Stance damage taken and the ailment damage family belong for the
    # same reason -- they are damage arriving at you, so less is the good news.
    "artsConsumptionRate", "miracleConsumptionRate", "shamanConsumptionRate",
    "goodsConsumptionRate", "toughnessDamageCutRate",
    "bloodDamageRate", "freezeDamageRate", "madnessDamageRate",
    "sleepDamageRate",
}


def is_better_lower(field_name: str) -> bool:
    return field_name in INVERTED_RATES


# Multipliers whose field name does not end in "Rate", so compute() never
# routed them anywhere and the Multipliers panel showed "none" while the relic
# plainly granted something. Neutral is 1.0 for all of these: ultimateArtGauge
# is 1.0 on 13,462 of the 13,472 SpEffect rows, and the handful that differ sit
# either side of it (0.85 / 0.90 impairing, 1.05 / 1.075 / 1.10 improving).
# The Ultimate Art and the Character Skill are two separate systems and must
# not be blurred together: the Skill runs off a cooldown timer
# (HeroParam.characterAbilityCooldown, in seconds), the Art off a gauge that
# auto-charges during combat. "Charge speed" rather than "gain" because the
# game's own caption for this field is "Faster auto-charging for Ultimate Art
# during combat" (AttachEffectInfo 8360000).
EXTRA_MULTIPLIERS = {
    "ultimateArtGauge": "Ultimate Art auto-charge speed",
    "characterSkillCooldownReduction": "Character Skill cooldown",
}

# Fields that refuse to add up, established by reading the game rather than the
# params -- which is the only reason this list is hand-written instead of
# derived, and the reason it must stay short and cited.
#
#   additionalCharacterSkillUse
#       Three effects carry it, all worth 1, all flagged as stacking, none in
#       an exclusivity group and none delivered through a state. Nothing in
#       the params distinguishes it from any other flat bonus. Measured
#       2026-08-11: several "+1 additional Character Skill use" relics equipped
#       together still gave 2 charges, not 3 or 4. Summing it, as every other
#       flat bonus is summed, told the player something the game does not do.
#
# Whether this is the field refusing to accumulate or a hard cap of two
# charges cannot be told apart from that reading: no effect grants more than
# +1, so the two are indistinguishable. Taking the maximum reproduces what was
# seen without inventing a cap that has not been observed.
NON_ACCUMULATING = {"additionalCharacterSkillUse"}

# Flat additions, not multipliers -- shown as a count rather than a percentage.
# characterSkillGauge belongs here, not above: its baseline across the 13,472
# SpEffect rows is 0.0, not 1.0, and the values it takes are point awards
# (6.5 on defeating an enemy, 18.0, -45.0) rather than anything near 1.
FLAT_BONUSES = {
    "characterSkillGauge": "Art gauge points",
    "additionalCharacterSkillUse": "Extra Character Skill uses",
    "changeHpPoint": "HP per tick",
    "changeMpPoint": "FP per tick",
    "runeDiscountValue": "Shop discount %",
}

# Fields stored with the opposite sign to how a player reads them. The engine
# treats these as damage applied per tick, so Continuous HP *Recovery* holds
# -2 and the Continuous HP *Loss* curse holds +2. Displaying the raw number
# put a minus in front of a heal, so the value is negated on the way out.
INVERTED_SIGN = {"changeHpPoint", "changeMpPoint"}

# Whether a number multiplies or adds is decided by the field's own neutral
# value in the game data, not by whether its name happens to end in "Rate".
# configure() fills these from the snapshot's field_baselines; until it is
# called the name-based rule below is used, which keeps the module usable on
# its own but is the less accurate of the two.
#
# Five fields ending in "Rate" are additive and were being multiplied:
# changeHpRate, changeMpRate, bowDistRate, itemDropRate and
# guardCounterAttackRate. "[Revenant] Expend own HP to fully heal nearby
# allies" carries changeHpRate 50.0, which as a multiplier reads +4900%.
FIELD_BASELINE: dict[str, float] = {}
# Additive fields whose name ends in Rate, so they read as percentages.
PERCENT_FIELDS: set[str] = set()

# Of those, the ones stated as a fraction of 1 rather than out of 100, so they
# need scaling before they read as a percentage. Told apart by the range of
# values the field actually takes across SpEffectParam:
#   changeHpRate / changeMpRate / changeStaminaRate run -100..100
#   bowDistRate is 30, 40, 50
#   itemDropRate runs 0.16..1.6 in steps of 0.04 -- a fraction, so the 0.2 on
#     "Improved Item Discovery" is +20%
# That last one is why the effect used to show -60%: read as a multiplier
# against an assumed neutral of 1.0 it looked like a large penalty, when the
# field's neutral is 0.0 and the value is a straight gain.
FRACTION_PERCENT_FIELDS = {"itemDropRate"}

# A third way of stating a percentage, after "1.0 is neutral" and "0.0 is
# neutral": neutral is 100, and the value is a percentage *of* normal. 125
# means 25% more, not 125 of something.
#
# Exactly four fields sit at that baseline and all four are the ailment damage
# family, carried by the two tiers of "Ailments Cause Increased Damage" at 125
# and 135. Nothing else in the data comes near it, so this is a small closed
# set rather than a rule waiting to misfire. Filled by configure().
#
# Until now these were dropped on the floor: not a multiplier, not additive,
# not a sentinel, so no branch claimed them and the effect showed no numbers
# at all -- a debuff that reads "Increases damage taken from ailments" and then
# moved nothing on the sheet.
PERCENT_OF_100_BASELINE = 100.0
PERCENT_OF_100_FIELDS: set[str] = set()


def percent_value(field_name: str, value: float) -> float:
    """The value of an additive percentage field, as a percentage."""
    if field_name in FRACTION_PERCENT_FIELDS:
        return value * 100.0
    return value
# Baseline -1 marks a sentinel -- a condition or a row id -- rather than a
# quantity, so those fields are not shown as a number at all.
SENTINEL_BASELINE = -1.0


def configure(data: dict) -> None:
    """Teach the module which fields multiply and which add, from the data."""
    FIELD_BASELINE.clear()
    PERCENT_FIELDS.clear()
    PERCENT_OF_100_FIELDS.clear()
    for name, value in (data.get("field_baselines") or {}).items():
        FIELD_BASELINE[name] = float(value)
        if abs(float(value)) < 1e-9 and name.endswith("Rate"):
            PERCENT_FIELDS.add(name)
        elif abs(float(value) - PERCENT_OF_100_BASELINE) < 1e-9:
            PERCENT_OF_100_FIELDS.add(name)
    RATE_LABELS.update({f: RATE_LABELS.get(f, f) for f in PERCENT_FIELDS})


def is_multiplier(field_name: str) -> bool:
    """Does this field scale what it touches, rather than add to it?"""
    baseline = FIELD_BASELINE.get(field_name)
    if baseline is None:
        return field_name.endswith("Rate") or field_name in EXTRA_MULTIPLIERS
    return abs(baseline - 1.0) < 1e-9


# Fields the shipped Elden Ring paramdef names wrongly for Nightreign. The
# name is all the def gives, and where the values plainly are not the thing the
# name describes, showing them is worse than showing nothing: a number on the
# sheet is a claim about the game.
#
# soulStealRate, at offset 280, is the one found so far. Its values are 20008,
# 20406, 20493 and sixteen more in that band -- and 18 of its 19 distinct
# values also occur as iconId on other rows. It is an icon reference, not a
# rate. Left alone it reached the panel as "soulStealRate 20493", which is not
# a wrong label on a real number but a real label on an engine pointer.
MISNAMED_FIELDS = {"soulStealRate"}

# Fields whose value is a pointer into another table, or a classification code,
# rather than a quantity. They were reaching the panel as their own raw name
# with the id beside it -- "cycleOccurrenceSpEffectId 7011001", "saveCategory
# 10", "vfxId1 1643000" -- which reads as a stat with an absurd value.
#
# These are not unlabelled numbers waiting for a label. There is no honest
# label, because there is no quantity: 7011001 is the row that fires, not an
# amount of anything. What the effect actually does with them is already said
# in words under Conditional & situational, via GATE_FIELDS.
ENGINE_FIELDS = {
    "cycleOccurrenceSpEffectId", "atkOccurrenceSpEffectId",
    "accumuOverFireId", "replaceSpEffectId", "startSwordArtsId",
    "startGoodsId", "behaviorId", "dmypolyId", "vfxId", "vfxId1",
    "spEffectTextId_1", "saveCategory",
}


def is_sentinel(field_name: str) -> bool:
    baseline = FIELD_BASELINE.get(field_name)
    return baseline is not None and abs(baseline - SENTINEL_BASELINE) < 1e-9

RATE_LABELS.update(EXTRA_MULTIPLIERS)
RATE_LABELS.update(FLAT_BONUSES)

# A critical-hit buff raises all five element rates, exactly as an ordinary
# attack buff does, and the two were being multiplied into the same figures.
# That is wrong in both directions: it inflates the Physical Attack line with
# a bonus that only applies to criticals, and it hides the critical bonus
# among numbers that look like general damage. Effects carrying this flag are
# therefore routed into a bucket of their own.
# Fields that gate an effect on something that is not always true. An effect
# carrying one of these must NOT be folded into the flat totals: "Lower Attack
# When Below Max HP" only bites below 85% HP, and counting it unconditionally
# both invented a penalty that is usually absent and corrupted the buffs it
# was multiplied against -- a real +12% Physical Attack was displayed as
# +2.5%. These effects are listed under Conditional & situational instead,
# with their numbers, so nothing is lost.
CONDITIONAL_FIELDS = {
    "conditionHp", "conditionHpRate",
    "invocationConditionsStateChange1", "invocationConditionsStateChange2",
    "enemyStateInfoTrigger",
    "triggerOnWepType", "wepTypeTrigger", "wepTypeTriggerCount",
}

# A payload row that carries a positive effectEndurance is a timed window, not
# a passive: the number applies for that many seconds once something sets the
# buff off, and for none of the rest of the expedition.
#
# "[Guardian] Character Skill Boosts Damage Negation of Nearby Allies" is the
# case that showed it. Its numbers live on payload row 7500101 -- eight damage
# cut rates at 0.82 with effectEndurance 30 -- and nothing on the effect itself
# says "only while the skill is up", so an 18% damage reduction was being
# folded into the flat totals permanently for an aura that lasts half a minute
# and only covers allies standing near you.
#
# The rule is bounded rather than broad: exactly 20 effects carry a positive
# effectEndurance, and all 20 read as timed windows -- the Character Skill
# auras, "Power of the Blood Lord", "Power of Dark Moon", the Duchess's 0.4 s
# invulnerability. None of them is on by default, so all of them belong under
# Conditional & situational with a switch, which is where this puts them.
DURATION_FIELD = "effectEndurance"


def timed_window(effect: dict) -> float:
    """Seconds this effect lasts once triggered, or 0 if it is not timed."""
    value = (effect.get("modifiers") or {}).get(DURATION_FIELD)
    return float(value) if isinstance(value, (int, float)) and value > 0 else 0.0

# Gates gated on a *value* rather than on the field merely being present.
#
# saveCategory 9 marks the effects that accumulate against a counter the save
# keeps -- "Attack power increased for each Night Invader defeated" and the
# seven others like it. Their listed number is what one tally is worth, so a
# fresh expedition gets none of it, and folding it into the flat totals showed
# a +7% attack buff to a player who had killed no Night Invaders.
#
# The value matters: saveCategory 10 is the ordinary always-on case and covers
# 65 effects, including every "Improved Physical Attack Power". Keying on the
# field's presence would wrongly park all of those under Conditional too.
# Exactly 8 effects carry 9, and all 8 read as counters:
# seven named "... for each X" plus Revenant's "upon Ability Activation".
CONDITIONAL_FIELD_VALUES = {"saveCategory": {9}}

# magicSubCategoryChange* narrows an attack buff to one kind of attack: 130 is
# melee, 112/111 skills, 100 charged attacks, 2 Carian sword sorcery, and so
# on for some forty values. Two such buffs must never be multiplied together
# -- Improved Melee Attack Power (+6%) and Improved Skill Attack Power (+15%)
# apply to different attacks entirely, yet merged into a single bogus +21.9%
# on every damage type.
#
# Rather than hand-maintaining a map of forty scope numbers to wordings, which
# would mean inventing labels the game does not state, each scoped buff gets a
# line of its own named after the effect. The effect's name already says what
# it covers, so the result is exact and needs no upkeep.
SCOPE_FIELDS = ("magicSubCategoryChange1", "magicSubCategoryChange2",
                "magicSubCategoryChange3")
SCOPED_PREFIX = "scoped:"
# Source key for a multiplier that only covers one weapon type.
WEAPON_CLASS_PREFIX = "wepclass:"

# Of the 38 scope values, only three restrict a buff by the *kind of armament*
# rather than by the kind of attack, and only those can be applied to an
# ordinary hit. The game's own effect names are what say so:
#   130       "Improved Melee Attack Power"
#   113, 118  "Improved Ranged Weapon Attacks"
# Everything else narrows to a move or a spell family -- 102 jump attacks, 100
# charge attacks, 103 guard counters, 104 chain finishers, 124 two-handing,
# 125 wielding two armaments, 112 skills, 2-12 and 20-26 spell families, and so
# on. None of those is the plain swing an attack rating describes, so they stay
# out of it and keep their own scoped line.
WEAPON_CLASS_SCOPES = {130: "melee", 113: "ranged", 118: "ranged"}

# Which class an armament belongs to, by its family. Families are named by the
# game's own buffs (see "Categories come from the buffs"), so this reads them
# rather than inventing a grouping.
RANGED_FAMILIES = {"Bow", "Greatbow", "Crossbow", "Ballista"}
CATALYST_FAMILIES = {"Glintstone Staff", "Sacred Seal"}


def scoped_class(effect: dict) -> str | None:
    """The armament class a buff is restricted to, if any.

    All three scope fields are read, not just the first: "Improved Ranged
    Weapon Attacks" carries 105, 113 and 118 together, and the 105 in front
    would otherwise hide the two that name the class. Checked across the data
    -- only two effect families carry a class scope at all, neither mixes melee
    with ranged, and the only value they sit beside is 105.
    """
    mods = effect.get("modifiers") or {}
    if not any(f in mods for f in ELEMENT_ATTACK_RATES):
        return None
    for field_name in SCOPE_FIELDS:
        value = mods.get(field_name)
        if isinstance(value, int) and value in WEAPON_CLASS_SCOPES:
            return WEAPON_CLASS_SCOPES[value]
    return None


def weapon_class(weapon: dict | None) -> str | None:
    """"melee", "ranged" or "catalyst" for an armament."""
    if not weapon:
        return None
    family = weapon.get("family") or ""
    if family in RANGED_FAMILIES:
        return "ranged"
    if family in CATALYST_FAMILIES:
        return "catalyst"
    return "melee"


def attack_scope(effect: dict) -> int | None:
    mods = effect.get("modifiers") or {}
    if not any(f in mods for f in ELEMENT_ATTACK_RATES):
        return None
    for field_name in SCOPE_FIELDS:
        value = mods.get(field_name)
        if isinstance(value, int) and value:
            return value
    return None


# Weapon-type gates the selected reference weapon can actually satisfy. The
# test is plain equality against the weapon's own wep_type, which keeps the
# values that are not weapon types honest for free: triggerOnWepType is 256 on
# 70 effects and 512 on 2, neither of which is any weapon's type, so they never
# match and stay conditional. wepTypeTriggerCount is deliberately absent -- it
# wants several of that type equipped, which one reference weapon cannot show.
WEAPON_TYPE_GATES = ("triggerOnWepType", "wepTypeTrigger")


def satisfied_by_weapon(field_name: str, value, wep_type) -> bool:
    """True when an equipped armament meets this weapon-type gate.

    `wep_type` may be a single type or a collection of them -- the planner
    holds six armaments, and "Improved Axe Attack Power" is live whenever any
    of them is an axe, not only when the tile being broken down is.
    """
    if field_name not in WEAPON_TYPE_GATES or wep_type is None:
        return False
    if isinstance(wep_type, (set, frozenset, list, tuple)):
        return value in wep_type
    return value == wep_type


def accumulates(effect: dict) -> bool:
    """Does this effect gain a stack each time something happens?

    These are the ones worth a number rather than a yes/no: "for each Night
    Invader defeated" is worth four times as much with four kills. The marker
    is saveCategory 9, documented above -- exactly 8 effects carry it and all
    8 read as counters. isStrongestEffect is the wrong test and was the first
    one tried: it is true of 407 of the 421 gated effects, which would have
    put a count box on "below 40% HP", where a number means nothing.
    """
    return (effect.get("modifiers") or {}).get("saveCategory") in (
        CONDITIONAL_FIELD_VALUES["saveCategory"])


def is_conditional(effect: dict, wep_type: int | None = None) -> bool:
    """Is this effect gated on something that is not currently true?

    With a reference weapon selected, a weapon-type gate the weapon matches is
    no longer a gate: "Improved Axe Attack Power" is simply active while an axe
    is equipped, so it belongs in the totals rather than parked under
    Conditional & situational. An effect carrying a second, unmet gate stays
    conditional -- every gate has to be satisfied, not just this one.
    """
    mods = effect.get("modifiers") or {}
    for field_name in CONDITIONAL_FIELDS:
        if field_name not in mods:
            continue
        if satisfied_by_weapon(field_name, mods[field_name], wep_type):
            continue
        return True
    for field_name, gating in CONDITIONAL_FIELD_VALUES.items():
        if mods.get(field_name) in gating:
            return True
    return timed_window(effect) > 0


CRIT_FLAG = "throwAttackParamChange"
CRIT_RATE = "criticalDamageRate"
ELEMENT_ATTACK_RATES = ("physicsAttackRate", "magicAttackRate",
                        "fireAttackRate", "thunderAttackRate",
                        "darkAttackRate")
ELEMENT_ATTACK_POWER_RATES = ("physicsAttackPowerRate", "magicAttackPowerRate",
                              "fireAttackPowerRate", "thunderAttackPowerRate",
                              "darkAttackPowerRate")
# Marks a row that stands for all five damage types at once. The real field
# name rides behind it so the click-through breakdown still works.
ALL_DAMAGE_PREFIX = "alldamage:"
RATE_LABELS[CRIT_RATE] = "Critical damage"

# Verified against the wiki's vessel list: 8 of 8 chalices matched exactly.
# Colour 4 is White -- a wildcard slot that accepts a relic of any colour.
COLOUR_NAMES = {0: "Red", 1: "Blue", 2: "Yellow", 3: "Green", 4: "White"}

# Lowest attribute value the sheet will display. See compute() for why.
ATTRIBUTE_FLOOR = 1


# Derived stats: the multiplier each one is scaled by, if any effect touches it.
DERIVED_RATE_FIELD = {
    "HP": "maxHpRate",
    "FP": "maxMpRate",
    "Stamina": "maxStaminaRate",
}

# Status resistances, additive point change and multiplicative rate.
RESISTANCES = {
    "Poison": ("changePoisonResistPoint", "registPoizonChangeRate"),
    "Scarlet Rot": ("changeDiseaseResistPoint", "registDiseaseChangeRate"),
    "Blood Loss": ("changeBloodResistPoint", "registBloodChangeRate"),
    "Death Blight": ("changeCurseResistPoint", "registCurseChangeRate"),
    "Sleep": ("changeSleepResistPoint", "registSleepChangeRate"),
    "Madness": ("changeMadnessResistPoint", "registMadnessChangeRate"),
    "Frost": ("changeFreezeResistPoint", "registFreezeChangeRate"),
}


# The stat-swap relics -- "[Guardian] Improved Strength and Dexterity, Reduced
# Vigor" and the nineteen like them. Their SpEffect rows carry no numbers at
# all; the deltas are in HeroStatusParam's 300-block and are attached to the
# effect by the extractor, keyed by the level they were read at. See the
# "stat-swap relics" section of extract.py for how the blocks were matched and
# checked.
SWAP_FIELD = "attribute_swap"


def swap_deltas(effect: dict, level: int) -> dict[str, int]:
    """This effect's attribute changes at `level`, interpolated between anchors.

    The game defines the swap at levels 1 and 12 only. Between them the value
    is interpolated exactly as the base stats are; above the top anchor it is
    held, because extrapolating past the last number the game states would be
    inventing one.
    """
    anchors = effect.get(SWAP_FIELD) or {}
    if not anchors:
        return {}
    levels = sorted(int(k) for k in anchors)
    lo = max([l for l in levels if l <= level], default=levels[0])
    hi = min([l for l in levels if l >= level], default=levels[-1])
    low, high = anchors[str(lo)], anchors[str(hi)]
    span = hi - lo
    t = 0.0 if span <= 0 else (level - lo) / span
    out: dict[str, int] = {}
    for attr in set(low) | set(high):
        a, b = low.get(attr, 0), high.get(attr, 0)
        value = round(a + (b - a) * t)
        if value:
            out[attr] = int(value)
    return out


def evaluate_curve(curve: dict, x: float) -> float:
    """Piecewise CalcCorrectGraph evaluation, as the engine does it."""
    xs, ys, adj = curve["x"], curve["y"], curve["adj"]
    if x <= xs[0]:
        return ys[0]
    for i in range(4):
        if xs[i] <= x <= xs[i + 1]:
            span = xs[i + 1] - xs[i]
            if span <= 0:
                return ys[i + 1]
            t = (x - xs[i]) / span
            a = adj[i] or 1.0
            t = t ** a if a > 0 else 1.0 - (1.0 - t) ** -a
            return ys[i] + (ys[i + 1] - ys[i]) * t
    return ys[4]


@dataclass
class Warning:
    kind: str          # "duplicate" | "category"
    text: str


# Marks a copy of a gated effect the player has declared live. The original is
# replaced by however many copies were asked for, so the existing arithmetic --
# additive fields summing, rate fields multiplying, isStrongestEffect refusing
# to stack -- applies to a declared condition exactly as it does to two relics
# carrying the same roll. Nothing about how an effect is applied changes; only
# whether it is applied at all.
FORCED = "_declared_live"


@dataclass
class Situational:
    """A gated effect the player can switch on, and how many times it applies.

    The sheet cannot know whether you are below 85% HP, standing in Morgott's
    aura, or how many Night Invaders you have killed. It can know what each of
    those is worth, which is the whole value of being able to say so.
    """
    effect_id: int
    name: str
    detail: str
    why: str
    # True only for the counters -- the effects that gain a stack per event.
    # Everything else is a yes/no condition, and gets a switch with no number.
    accumulates: bool
    count: int = 0

    @property
    def live(self) -> bool:
        return self.count > 0


@dataclass
class Build:
    attributes: dict[str, int] = field(default_factory=dict)
    base_attributes: dict[str, int] = field(default_factory=dict)
    rates: dict[str, float] = field(default_factory=dict)
    # Multipliers that only cover a class of armament -- "Improved Melee Attack
    # Power" against a bow. Keyed by "melee" / "ranged" / "catalyst".
    class_rates: dict[str, dict[str, float]] = field(default_factory=dict)
    other: dict[str, float] = field(default_factory=dict)
    warnings: list[Warning] = field(default_factory=list)
    # label -> (value before relics, value after relics)
    derived: dict[str, tuple[float, float]] = field(default_factory=dict)
    # label -> (added points, multiplier)
    resistances: dict[str, tuple[int, float]] = field(default_factory=dict)
    # Effects that do something real but cannot be reduced to a number in the
    # stat sheet: hero-specific, weapon-specific, or gated on a condition.
    # Without this they were equipped and yet invisible in the overview.
    # (name, what it does, why it does not appear as a number)
    qualitative: list[tuple[str, str, str]] = field(default_factory=list)
    # The gated effects the player can declare live, in the order shown. A
    # subset of `qualitative`: only those whose condition is something the
    # player controls or can count, never a hero or weapon mismatch.
    situational: list["Situational"] = field(default_factory=list)
    # Which effects produced each total, so a figure can be broken back down
    # into the buffs behind it. field name -> [(effect name, its own value)]
    sources: dict[str, list[tuple[str, float]]] = field(default_factory=dict)


def compute_derived(curves: dict, build: "Build") -> None:
    """HP / FP / Stamina from the attribute curves, then relic multipliers."""
    for label, curve in curves.items():
        attribute = curve["attribute"]
        base = evaluate_curve(curve, build.base_attributes.get(attribute, 0))
        # Relic attribute bonuses feed back into the curve, then rate
        # multipliers apply on top of the result.
        raised = evaluate_curve(curve, build.attributes.get(attribute, 0))
        rate = build.rates.get(DERIVED_RATE_FIELD.get(label, ""), 1.0)
        build.derived[label] = (base, raised * rate)


def compute_resistances(build: "Build", effects: list[dict]) -> None:
    for label, (point_field, rate_field) in RESISTANCES.items():
        points = 0
        rate = 1.0
        for eff in effects:
            mods = eff["modifiers"]
            if point_field in mods:
                points += int(mods[point_field])
            if rate_field in mods:
                rate *= float(mods[rate_field])
        if points or abs(rate - 1.0) > 1e-9:
            build.resistances[label] = (points, rate)


def compute(hero: dict, level: int, effects: list[dict], curves: dict | None = None,
            weapon: dict | None = None,
            weapons_held: list[dict] | None = None,
            declared: dict[int, int] | None = None) -> Build:
    """Combine the level's base attributes with every selected effect.

    `weapon` is the reference weapon shown in the Weapon damage block. It is
    what lets a weapon-type buff count: "Improved Axe Attack Power" is inert
    until an axe is equipped, and the sheet cannot know which without it.

    Additive attribute bonuses sum; '*Rate' fields multiply. Effects flagged
    isStrongestEffect (stacks=False) do not add up when picked more than once --
    only the single strongest instance applies -- so duplicates are reported
    rather than counted twice.

    `declared` maps effect id to how many times the player says its condition
    is met right now. A gated effect is otherwise left out of every total,
    because the sheet has no way to know. Declaring one counts it exactly as
    though that many copies were equipped.
    """
    base = dict(hero["levels"][str(level)] if str(level) in hero["levels"] else hero["levels"][level])
    build = Build(base_attributes=dict(base), attributes=dict(base))
    # Weapon-type gates are met by any armament being held, not just the one
    # being broken down. Falls back to the single weapon when no set is given,
    # so older callers keep working.
    if weapons_held:
        wep_type = {w.get("wep_type") for w in weapons_held if w}
        wep_type.discard(None)
        wep_type = wep_type or None
    else:
        wep_type = weapon.get("wep_type") if weapon else None

    # A declared effect is replaced by the number of copies asked for, rather
    # than kept alongside them: leaving the original in would make the first
    # copy of an isStrongestEffect look like a duplicate of it and be dropped.
    live = {int(k): int(v) for k, v in (declared or {}).items() if int(v) > 0}
    if live:
        expanded: list[dict] = []
        for eff in effects:
            times = live.get(eff["id"], 0)
            if times and is_conditional(eff, wep_type):
                expanded.extend([{**eff, FORCED: True}] * times)
            else:
                expanded.append(eff)
        effects = expanded

    seen_ids: dict[int, int] = {}
    counted: list[dict] = []
    for eff in effects:
        eid = eff["id"]
        seen_ids[eid] = seen_ids.get(eid, 0) + 1
        if not eff["stacks"] and seen_ids[eid] > 1:
            build.warnings.append(
                Warning("duplicate", f"{eff['name']} x{seen_ids[eid]} — only the strongest applies")
            )
            continue
        counted.append(eff)

    # An effect the current Nightfarer cannot use contributes to no total.
    # works_for is the single authority here: the slot cards, the totals and
    # the Conditional section all derive from the same predicate, so a figure
    # can never be counted while its own name is crossed out -- which is
    # exactly what an Undertaker build did on 1.7.0 (resistances +75 from an
    # effect struck through as not working). The dead ones are not dropped;
    # compute_qualitative lists every one, so nothing equipped goes unseen.
    from . import effecttext    # local, as in compute_qualitative

    hero_name = str(hero.get("name", ""))
    dead = [eff for eff in counted
            if not effecttext.works_for(eff, hero_name)]
    if dead:
        counted = [eff for eff in counted
                   if effecttext.works_for(eff, hero_name)]

    # Conflicts come from the game's own exclusivityId, not from guesswork.
    # The previous rule -- a shared SpEffect category plus any overlapping
    # modifier field -- reported pairs that plainly do stack, such as Improved
    # Carian Sword Sorcery against Physical Attack Up +4, which touch
    # different things and both carry exclusivityId -1. Only 64 of the 2079
    # effects set the field at all, and effects sharing a positive value are
    # the ones the game actually treats as mutually exclusive.
    by_exclusivity: dict[int, list[dict]] = {}
    for eff in counted:
        key = eff.get("exclusivity", -1)
        if isinstance(key, int) and key > 0:
            by_exclusivity.setdefault(key, []).append(eff)

    reported: set[tuple[str, str]] = set()
    for key, group in by_exclusivity.items():
        for i, a in enumerate(group):
            for b in group[i + 1:]:
                pair = tuple(sorted((" ".join(a["name"].split()),
                                     " ".join(b["name"].split()))))
                if pair[0] == pair[1] or pair in reported:
                    continue
                reported.add(pair)
                build.warnings.append(
                    Warning(
                        "exclusive",
                        f"{pair[0]} and {pair[1]} are mutually exclusive "
                        f"(the game groups them under exclusivity {key}) — "
                        "only one will apply",
                    )
                )

    for eff in counted:
        mods = eff["modifiers"]
        # Gated effects are not part of the always-on totals. They still get
        # reported, with their numbers, under Conditional & situational --
        # unless the player has declared the condition met, which is the one
        # thing the sheet cannot work out for itself.
        if is_conditional(eff, wep_type) and not eff.get(FORCED):
            continue
        # A critical-hit effect raises every element rate, so left alone it
        # would multiply into the same Physical/Fire/... figures as a general
        # attack buff and overstate both. Route it to its own line instead.
        # The five rates carry one number between them, not five, so it is
        # applied once rather than raised to the fifth power.
        label = " ".join(str(eff.get("name", "")).split())

        def record(key: str, own: float) -> None:
            build.sources.setdefault(key, []).append((label, own))

        # A stat swap moves attributes and nothing else, and its numbers come
        # from HeroStatusParam rather than from `modifiers`, so it is applied
        # here rather than in the field loop below.
        for attr, delta in swap_deltas(eff, level).items():
            build.attributes[attr] = build.attributes.get(attr, 0) + delta
            record(attr, delta)

        # A weapon-type gate says what makes an effect live, NOT what it then
        # applies to. Holding three Great Hammers switches "Improved Attack
        # Power with 3+ Great Hammers Equipped" on, and it then lifts
        # everything being carried -- measured, 152 / 183 / 219 with neither,
        # one and both of two +20% buffs. Section 6j has the working.
        #
        # So nothing here buckets a multiplier by weapon type. The scoping that
        # does survive is by weapon *class*, below, which was measured and
        # holds: Improved Melee Attack Power lifts the greatsword and leaves
        # the bow beside it alone.
        crit_only = bool(mods.get(CRIT_FLAG))
        scope = attack_scope(eff)
        # A scope that names a kind of armament rather than a kind of attack is
        # a real attack-rating buff for those armaments, so it is bucketed by
        # class instead of being parked on a scoped line and ignored.
        class_to = scoped_class(eff)
        scoped_out = crit_only or (scope and class_to is None)
        # Both cases take the element rates out of the general pool: the five
        # of them carry one number between them, applied once, on a line that
        # says what it actually covers.
        if scoped_out:
            values = [float(mods[f]) for f in ELEMENT_ATTACK_RATES
                      if isinstance(mods.get(f), (int, float))]
            if values:
                key = CRIT_RATE if crit_only else f"{SCOPED_PREFIX}{label}"
                build.rates[key] = build.rates.get(key, 1.0) * max(values)
                record(key, max(values))

        for fname, value in mods.items():
            if scoped_out and fname in ELEMENT_ATTACK_RATES:
                continue
            if fname in MISNAMED_FIELDS or fname in ENGINE_FIELDS:
                continue
            if fname in ATTRIBUTE_FIELDS:
                attr = ATTRIBUTE_FIELDS[fname]
                build.attributes[attr] = build.attributes.get(attr, 0) + int(value)
                record(attr, int(value))
            elif fname in FLAT_BONUSES and isinstance(value, (int, float)):
                signed = -value if fname in INVERTED_SIGN else value
                if fname in NON_ACCUMULATING:
                    # Measured, not derived: the params mark these as stacking
                    # and they do not. See NON_ACCUMULATING.
                    previous = build.other.get(fname)
                    build.other[fname] = (signed if previous is None
                                          else max(previous, signed))
                    if previous is not None:
                        build.warnings.append(Warning(
                            "no-accumulate",
                            f"{RATE_LABELS.get(fname, fname)} does not add up "
                            f"-- a second source of it is wasted",
                        ))
                    else:
                        record(fname, signed)
                else:
                    build.other[fname] = build.other.get(fname, 0) + signed
                    record(fname, signed)
            elif is_sentinel(fname) and isinstance(value, (int, float)):
                # Neutral -1 means "unset". A value other than -1 is real, but
                # the baseline does not say whether it scales or adds, so it is
                # shown as its own figure rather than folded into a multiplier
                # -- guessing wrong there is what produced +4900% readings.
                if abs(float(value) - SENTINEL_BASELINE) < 1e-9:
                    continue
                build.other[fname] = build.other.get(fname, 0) + value
                record(fname, value)
            elif ((fname.endswith("Rate") or fname in EXTRA_MULTIPLIERS)
                    and isinstance(value, (int, float))
                    and is_multiplier(fname)):
                if class_to is not None:
                    # Tied to melee or ranged armaments, same reasoning.
                    bucket = build.class_rates.setdefault(class_to, {})
                    bucket[fname] = bucket.get(fname, 1.0) * float(value)
                    record(f"{WEAPON_CLASS_PREFIX}{class_to}:{fname}",
                           float(value))
                    continue
                build.rates[fname] = build.rates.get(fname, 1.0) * float(value)
                record(fname, float(value))
            elif fname in PERCENT_FIELDS and isinstance(value, (int, float)):
                # Neutral is 0, so these add rather than scale.
                signed = -value if fname in INVERTED_SIGN else value
                build.other[fname] = build.other.get(fname, 0) + signed
                record(fname, signed)
            elif (fname in PERCENT_OF_100_FIELDS
                    and isinstance(value, (int, float))):
                # Neutral is 100, so the number worth showing is the distance
                # from it: 125 is +25%, and a second source of +25% is +50%
                # rather than 250.
                signed = value - PERCENT_OF_100_BASELINE
                build.other[fname] = build.other.get(fname, 0) + signed
                record(fname, signed)
            elif isinstance(value, (int, float)) and fname in RATE_LABELS:
                build.other[fname] = build.other.get(fname, 0) + value
                record(fname, value)

    # Curses subtract, and enough of them will drive an attribute negative,
    # which is certainly not a state the game can be in. 1 is the floor used
    # here because it is the lowest value any Nightfarer's own starting stats
    # take (Recluse begins with Strength 1). The exact floor is not stated
    # anywhere in the params, so this is an inference, not a read value --
    # but leaving Faith at -1 on the sheet would be worse than saying 1.
    for attr, value in build.attributes.items():
        if value < ATTRIBUTE_FLOOR:
            build.attributes[attr] = ATTRIBUTE_FLOOR
            build.warnings.append(Warning(
                "floor",
                f"{attr} was driven below {ATTRIBUTE_FLOOR} by a curse and is "
                f"shown at {ATTRIBUTE_FLOOR}; the game's true floor is not "
                f"stated in the params",
            ))

    if curves:
        compute_derived(curves, build)
    compute_resistances(build, counted)
    compute_qualitative(build, counted, hero, wep_type, live, dead=dead)

    return build


# Modifier fields that mark an effect as gated rather than always-on.
GATE_FIELDS = {
    "triggerOnWepType": "only with a matching weapon type",
    "wepTypeTrigger": "only with a matching weapon type",
    "wepTypeTriggerCount": "needs several of that weapon equipped",
    "conditionHp": "only below a HP threshold",
    "conditionHpRate": "only at a HP threshold",
    "invocationConditionsStateChange1": "only in a particular state",
    "invocationConditionsStateChange2": "only in a particular state",
    "enemyStateInfoTrigger": "only against enemies in a given state",
    "cycleOccurrenceSpEffectId": "fires periodically",
    "atkOccurrenceSpEffectId": "fires on attacking",
    "replaceSpEffectId": "swaps in another effect when triggered",
    "accumuOverFireId": "fires once a counter fills",
    "startGoodsId": "grants an item at the start of an expedition",
    "startSwordArtsId": "changes the armament's skill",
    "additionalCharacterSkillUse": "grants an extra Character Skill use",
}


# Gated effects that get no switch, because there is nothing for a switch to
# show. A switch exists to answer "what would this be worth if its condition
# held", and that question needs a number the sheet can move. An effect whose
# whole content is a proc chance moves none: declaring it live would tick a box
# and change not one figure on screen, which reads as the switch being broken.
#
#   7037800  "Occasionally Nullify Attacks When Damage Negation is Lowered".
#            Its only quantity is `procChancePercent`, read out of
#            PlayerCommonParam + 0x2DC by the extractor -- how often it happens,
#            not what it is worth. Reported by the owner from play for 1.7.0.
#            It stays listed under Conditional & situational with its wording;
#            only the checkbox goes.
NO_SWITCH = {7037800}


def compute_qualitative(build: "Build", effects: list[dict], hero: dict,
                        wep_type: int | None = None,
                        live: dict[int, int] | None = None,
                        dead: list[dict] | None = None) -> None:
    """Record effects that contribute nothing numeric, so none go unseen.

    The stat sheet can only show what reduces to a number. An effect that is
    conditional, tied to one Nightfarer, or tied to a weapon type changes no
    total, and so used to be equipped and completely invisible. Listing them
    separately is the honest alternative to pretending they are not there.

    `dead` is the effects compute() excluded because works_for ruled them
    out. Every one is listed here -- numeric or not, which is what keeps the
    heading's "not working" count equal to the strikethroughs on the slot
    cards. They are listed first: a slot doing nothing at all outranks a
    buff that is merely waiting on its condition.
    """
    from . import effecttext

    hero_name = str(hero.get("name", ""))
    live = live or {}
    for eff in dead or []:
        who = effecttext.owner(eff) or "another Nightfarer"
        build.qualitative.append((
            effecttext.name(eff),
            effecttext.describe_full(eff),
            f"NOT WORKING — {who} only, you are {hero_name}",
        ))
    # A declared effect was expanded into one copy per application. They are
    # the same effect said several times over, so the list shows it once.
    seen_declared: set[int] = set()
    for eff in effects:
        mods = eff.get("modifiers") or {}
        if eff.get(FORCED):
            if eff["id"] in seen_declared:
                continue
            seen_declared.add(eff["id"])

        # A gated effect never reached the totals, so it always belongs here
        # regardless of whether it carries numbers.
        gated = is_conditional(eff, wep_type)

        # Did this effect already move a number the sheet displays? A stat swap
        # carries no modifiers at all -- its numbers ride alongside them -- so
        # it has to be asked about separately or it would be reported as having
        # no numeric effect while visibly moving three attributes.
        numeric = not gated and bool(eff.get(SWAP_FIELD))
        numeric = numeric or not gated and any(
            f in ATTRIBUTE_FIELDS
            or f in FLAT_BONUSES
            or f in EXTRA_MULTIPLIERS
            or (isinstance(v, (int, float)) and f.endswith("Rate"))
            for f, v in mods.items()
        )
        touches_resist = not gated and any(
            f in (pt, rate)
            for f in mods
            for pt, rate in RESISTANCES.values()
        )
        if numeric or touches_resist:
            continue

        reasons = [text for field_name, text in GATE_FIELDS.items()
                   if field_name in mods
                   and not satisfied_by_weapon(field_name, mods[field_name], wep_type)]
        # Said with its own number rather than from GATE_FIELDS: how long the
        # window lasts is the whole of what makes this one worth switching on.
        seconds = timed_window(eff)
        if seconds:
            reasons.append(
                f"only for {seconds:g} s once triggered, not all the time"
            )
        name = effecttext.name(eff)
        if not effecttext.works_for(eff, hero_name):
            who = effecttext.owner(eff) or "another Nightfarer"
            reasons.insert(0, f"NOT WORKING — {who} only, you are {hero_name}")
        elif effecttext.owner(eff):
            reasons.insert(0, f"{effecttext.owner(eff)}-specific")

        if eff.get("inflicts"):
            reasons.append("inflicts a status build-up")

        detail = effecttext.describe_full(eff)
        # "no numeric effect on the sheet" is the right answer for an effect
        # that reduces to nothing, and the wrong one for a gated effect that
        # carries a plain number and is merely waiting on its condition --
        # which is exactly the case the switches exist for.
        default = ("only while its condition holds" if gated
                   else "no numeric effect on the sheet")
        why = "; ".join(dict.fromkeys(reasons)) or default
        build.qualitative.append((name, detail, why))

        # Offered as a switch only when the condition is one the player can
        # actually be in. An effect belonging to another Nightfarer is not
        # gated on anything you can do, so declaring it live would produce a
        # sheet describing a build that cannot exist.
        if (gated and effecttext.works_for(eff, hero_name)
                and eff["id"] not in NO_SWITCH):
            build.situational.append(Situational(
                effect_id=eff["id"],
                name=name,
                detail=detail,
                why=why,
                accumulates=accumulates(eff),
                count=live.get(eff["id"], 0),
            ))


def label_for(field_name: str) -> str:
    if field_name.startswith(SCOPED_PREFIX):
        # The effect's own name is the label -- it already states the scope.
        return field_name[len(SCOPED_PREFIX):]
    if field_name.startswith(ALL_DAMAGE_PREFIX):
        return "All damage"
    return RATE_LABELS.get(field_name, field_name)


def collapse_by_label(values: dict[str, float]) -> dict[str, float]:
    """Merge fields that share a display name and agree on their number.

    The game splits some single ideas across several fields -- sorceries,
    incantations and the third school each have their own FP cost; the four
    ailment damage rates are one debuff. Every relic that touches one touches
    all of them at the same value, so showing a line each repeats the same
    figure three or four times over.

    Only merged while they actually agree. If a future relic moves one and not
    the others, they split back apart and the difference is on screen rather
    than averaged away or silently dropped.
    """
    groups: dict[str, list[str]] = {}
    for field_name in values:
        groups.setdefault(label_for(field_name), []).append(field_name)

    out: dict[str, float] = {}
    for fields in groups.values():
        distinct = {round(float(values[f]), 6) for f in fields}
        if len(fields) > 1 and len(distinct) == 1:
            first = sorted(fields)[0]
            out[first] = values[first]
        else:
            out.update({f: values[f] for f in fields})
    return out


def real_field(field_name: str) -> str:
    """The underlying field behind a display-only key."""
    if field_name.startswith(ALL_DAMAGE_PREFIX):
        return field_name[len(ALL_DAMAGE_PREFIX):]
    return field_name
