"""Turning an effect record into words.

Two independent sources describe an effect, and they are good at different
things:

* ``info`` is the game's own caption. It reads well and explains conditional
  and triggered effects that have no numbers to read, but only 1519 of 2079
  effects carry one and it never states a magnitude.
* the ``modifiers`` map is exact and always present, but it is raw field
  names, so on its own it says nothing about effects that work by triggering
  another SpEffect.

So neither alone is enough, and they are combined: the caption for what the
effect *is*, the modifiers for how much. That is what closes most of the gap
noted in the handover, where 138 effects produced no description at all.

Nothing here invents text. If both sources are empty the effect is reported
as undescribed rather than given a plausible-sounding guess.
"""

from __future__ import annotations

from . import model

# Fields that gate an effect rather than change a number.
CONDITIONS = {
    "conditionHp": lambda v: f"below {v:.0f}% HP",
    "conditionHpRate": lambda v: ("at full HP" if v >= 100
                                  else f"at or above {v:.0f}% HP"),
}

# Multiplier fields worth naming; anything else ending in Rate is still shown
# with its raw field name rather than being dropped.
EXTRA_RATE_LABELS = {
    "staminaAttackRate": "Stance damage",
    "physicsAttackPowerRate": "Physical attack",
    "magicAttackPowerRate": "Magic attack",
    "fireAttackPowerRate": "Fire attack",
    "thunderAttackPowerRate": "Lightning attack",
    "darkAttackPowerRate": "Holy attack",
    "amuletAttackPowerRate": "Attack",
    "sightSearchEnemyRate": "Enemy sight range",
    "hearingSearchEnemyRate": "Enemy hearing range",
    "itemDropRate": "Item discovery",
    "soulRate": "Runes gained",
    "equipWeightChangeRate": "Equip load",
    "magicConsumptionRate": "FP cost",
    "artsConsumptionRate": "Character Skill FP cost",
    "shamanConsumptionRate": "Incantation FP cost",
    "miracleConsumptionRate": "Miracle FP cost",
    "goodsConsumptionRate": "Item use cost",
    "staminaAttackPowerRate": "Stance damage",
    "consumeStaminaRate": "Stamina cost",
    "spConsumptionRate": "Stamina cost",
    "maxHpRate": "Max HP",
    "maxMpRate": "Max FP",
    "maxStaminaRate": "Max stamina",
    # Regain is the Bloodborne-style mechanic: damage taken briefly stays
    # recoverable, and hitting back reclaims it. The bare field name said
    # nothing, and the effect that uses it is named only "Partial HP
    # Restoration upon Post-Damage Attacks".
    # Regain: after taking a hit, part of the lost HP stays briefly on the bar
    # as recoverable, and landing attacks wins it back. This rate scales how
    # much of it comes back, not how much damage is taken.
    "regainRate": "Regain — HP won back by attacking after a hit",
    "saAttackPowerRate": "Stance damage",
    "changeHpEstusFlaskCorrectRate": "HP restored per flask",
    "changeMpEstusFlaskCorrectRate": "FP restored per flask",
}

# magicSubCategoryChange1 gates an effect to one kind of attack. The values
# are read off the effects that carry them: every effect with 124 is named
# "... when Two-Handing", every effect with 119 is an "Initial ..." one.
ATTACK_CONDITIONS = {
    119: "on the first attack of a chain only",
    124: "only while two-handing the armament",
}

# Multipliers whose names do not end in "Rate", so the pattern match above
# never reached them. Each was left showing nothing at all -- notably
# "Ultimate Art Charging Impaired", whose entire content is a 0.85 here.
#
# That these are multipliers around a neutral 1.0, rather than raw values, is
# established by the effects that ship both directions: ultimateArtGauge is
# 0.85 and 0.90 on the two impairing effects and 1.05 / 1.075 / 1.10 on
# Ultimate Art Auto Charge +1/+2/+3. A raw value could not be read that way.
RATE_LIKE_LABELS = {
    "ultimateArtGauge": "Ultimate Art auto-charge speed",
    "characterSkillCooldownReduction": "Character Skill cooldown",
}

# Flat values that are neither multipliers nor attributes.
FLAT_LABELS = {
    "runeDiscountValue": "Shop discount",
    "wepTypeTriggerCount": "Weapons of the type needed",
    # Payload fields reached through the state an effect sets. They are the
    # whole content of a family of relic effects whose own row holds only a
    # stateInfo -- see the state_payload note in nrdata/extract.py.
    "soul": "Runes",
    # How long the effect lasts. It is the whole content of the
    # invulnerability relics, whose own row says only that they exist.
    "effectEndurance": "Duration (seconds)",
    # Units are not stated anywhere: 22 could be seconds, ticks or
    # points. Labelled so the raw figure is visible without implying one.
    "weakPointValue": "Weak point value (unit not stated)",
    "poizonAttackPower": "Poison buildup",
    "diseaseAttackPower": "Scarlet Rot buildup",
    "bloodAttackPower": "Blood Loss buildup",
    "freezeAttackPower": "Frost buildup",
    "sleepAttackPower": "Sleep buildup",
    "madnessAttackPower": "Madness buildup",
    "curseAttackPower": "Death Blight buildup",
    "staminaRecoverChangeSpeed": "Stamina recovery speed",
    # A relative weighting with no scale given in the files.
    "targetPriority": "Enemy attention (relative, unitless)",
    "physicsAttackPower": "Physical attack power",
    "magicAttackPower": "Magic attack power",
    "fireAttackPower": "Fire attack power",
    "thunderAttackPower": "Lightning attack power",
    "darkAttackPower": "Holy attack power",
}

# The five FP/item consumption rates move together on every effect that sets
# them, so "[Scholar] Reduced FP consumption" printed the same -15% five times.
CONSUMPTION_RATES = ("artsConsumptionRate", "magicConsumptionRate",
                     "shamanConsumptionRate", "miracleConsumptionRate",
                     "goodsConsumptionRate")

# Grouped so "+20% to all five damage types" reads as one statement.
ATTACK_RATES = ("physicsAttackRate", "magicAttackRate", "fireAttackRate",
                "thunderAttackRate", "darkAttackRate")

# The same idea for incoming damage. "Improved Damage Negation at Low HP" sets
# all eight of these to 0.60 and produced eight near-identical lines.
DAMAGE_CUT_RATES = ("slashDamageCutRate", "blowDamageCutRate",
                    "thrustDamageCutRate", "neutralDamageCutRate",
                    "magicDamageCutRate", "fireDamageCutRate",
                    "thunderDamageCutRate", "darkDamageCutRate")

# Set alongside the attack rates when the boost applies only to critical hits.
# Without checking it, "Improved Critical Hits" reads as a flat +24% to
# everything, which is badly wrong -- it is +24% on criticals alone.
CRIT_FLAG = "throwAttackParamChange"

# Bookkeeping flags that carry no player-facing meaning.
IGNORE = {
    "magParamChange", "miracleParamChange", "shamanParamChange",
    "isDisableNetSync", "dontDeleteOnDead", "isWaitModeDelete",
    "saveCategory", "spCategory", "categoryPriority", "isExtendSpEffectLife",
    "magicSubCategoryChange1", "magicSubCategoryChange2",
    "magicSubCategoryChange3",
    # Engine bookkeeping: model attachment points, behaviour ids, visual
    # effects and lifetime flags. Verified to carry nothing a player can act
    # on, so they are dropped rather than printed as raw field names.
    "behaviorId", "dmypolyId", "vfxId1",
    "isUseAtkParamAtkPowerCorrect", "dispIconNonactive", "isPeriodicEffect",
    "isHpBurnEffect", "deleteCriteriaDamage",
    # 20493 = 0x500D: two packed 16-bit halves, like chanceWeight in
    # AttachEffectTableParam. Read as a rate it printed +2049200%.
    "soulStealRate",
}

# Fields that are a reference to something else, where the reference itself is
# the whole story. The effect's name already states which skill or item, so
# these say what kind of thing happens rather than restating the name.
REFERENCE_LABELS = {
    "startSwordArtsId": "replaces the armament's skill",
    "startGoodsId": "grants an item at the start of an expedition",
    "applyIdOnGetSoul": "triggers when runes are collected",
    "accumuOverFireId": "triggers once a counter fills",
}

# Shown when the game ships no caption and the effect changes no field this
# code can read. The name is still on the row, so say that rather than
# implying the effect is unknown.
NO_DESCRIPTION = "no detail beyond the name in the game files"


def _percent(value: float) -> str:
    return f"{(value - 1) * 100:+.0f}%" if abs(value - 1) >= 0.005 else "±0%"


def caption(effect: dict) -> str:
    """The game's own wording for this effect, blank if it ships none."""
    text = str(effect.get("info") or "").strip()
    # Captions wrap with hard newlines for the in-game box; reflow them.
    return " ".join(text.split())


def name(effect: dict) -> str:
    """Display name, with the same hard newlines flattened out."""
    return " ".join(str(effect.get("name", "")).split())


def describe(effect: dict) -> str:
    """Spell out exactly what an effect changes, including its conditions."""
    mods = dict(effect["modifiers"])
    parts: list[str] = []

    # A stat-swap relic keeps its numbers outside `modifiers`, because they
    # come from HeroStatusParam rather than from a SpEffect row. Its top anchor
    # is what the description shows -- the sheet applies the value for the
    # level actually selected, and saying which level this is stops the two
    # from reading as a contradiction.
    swap = effect.get("attribute_swap") or {}
    if swap:
        top = max(swap, key=int)
        moves = ", ".join(
            f"{attr} {value:+d}" for attr, value in swap[top].items() if value
        )
        if moves:
            parts.append(f"{moves} at level {top}, scaling from level 1")

    conditions = [fn(mods.pop(key)) for key, fn in CONDITIONS.items()
                  if key in mods and isinstance(mods.get(key), (int, float))]

    # Which attacks the effect applies to. Without this "Improved Initial
    # Standard Attack" read as a flat +15% to everything.
    gate = ATTACK_CONDITIONS.get(mods.get("magicSubCategoryChange1"))
    if gate:
        conditions.append(gate)

    # All-damage boosts collapse into a single phrase. When the critical flag
    # is set the same numbers mean criticals only, which is a completely
    # different effect and has to be said.
    crit_only = bool(mods.pop(CRIT_FLAG, 0))
    attack = {k: mods[k] for k in ATTACK_RATES if k in mods}
    if len(attack) == len(ATTACK_RATES) and len(set(attack.values())) == 1:
        amount = _percent(next(iter(attack.values())))
        parts.append(f"Critical damage {amount}" if crit_only
                     else f"All damage {amount}")
        for key in ATTACK_RATES:
            mods.pop(key, None)
    elif crit_only:
        parts.append("affects critical hits")

    # Same collapse for incoming damage, so eight identical lines become one.
    spend = {k: mods[k] for k in CONSUMPTION_RATES if k in mods}
    if len(spend) == len(CONSUMPTION_RATES) and len(set(spend.values())) == 1:
        parts.append(f"All FP and item costs {_percent(next(iter(spend.values())))}")
        for key in CONSUMPTION_RATES:
            mods.pop(key, None)

    cuts = {k: mods[k] for k in DAMAGE_CUT_RATES if k in mods}
    if len(cuts) == len(DAMAGE_CUT_RATES) and len(set(cuts.values())) == 1:
        parts.append(f"All damage taken {_percent(next(iter(cuts.values())))}")
        for key in DAMAGE_CUT_RATES:
            mods.pop(key, None)

    # How often an "on occasion" effect fires. The game states this nowhere in
    # its own captions and it is unreachable by any paramdef field name -- see
    # nrdata/extract.py for the two places the values live and how the
    # executable was read to confirm both are percentages rolled against 0..99.
    # It leads the description because it is the whole question the word
    # "Occasionally" leaves open.
    chance = mods.pop("procChancePercent", None)
    if isinstance(chance, (int, float)) and chance:
        parts.append(f"{chance:g}% chance to trigger")

    # changeHpRate carries the same sign convention as changeHpPoint -- the
    # engine stores a restoration as a negative number, and every effect that
    # sets both gives them the same sign, so the direction is safe to state.
    #
    # The UNIT is not. This was previously shown as "% of maximum HP", which
    # was an invented reading: among the effects that also ship a game caption,
    # the field holds 0.10 and 0.15 alongside 12.5 and 10.0 -- two orders of
    # magnitude apart for the same kind of tick -- so no single percentage
    # reading fits them all. The magnitude is therefore shown raw and labelled
    # as unestablished rather than dressed up in a unit the files do not give.
    hp_rate = mods.pop("changeHpRate", None)
    if isinstance(hp_rate, (int, float)) and hp_rate:
        verb = "recovery" if hp_rate < 0 else "loss"
        parts.append(f"HP {verb} rate {abs(hp_rate):g} (unit not stated in the files)")

    for field_name, value in list(mods.items()):
        if field_name in IGNORE or not isinstance(value, (int, float)):
            continue
        if field_name in model.ATTRIBUTE_FIELDS:
            parts.append(f"{model.ATTRIBUTE_FIELDS[field_name]} {int(value):+d}")
        elif "Resist" in field_name:
            label = field_name.replace("change", "").replace("ResistPoint", "")
            parts.append(f"{label} resistance {int(value):+d}")
        elif field_name in RATE_LIKE_LABELS:
            parts.append(f"{RATE_LIKE_LABELS[field_name]} {_percent(value)}")
        elif field_name in FLAT_LABELS:
            parts.append(f"{FLAT_LABELS[field_name]} {value:g}")
        elif field_name.endswith("Rate"):
            label = (EXTRA_RATE_LABELS.get(field_name)
                     or model.RATE_LABELS.get(field_name)
                     or field_name)
            parts.append(f"{label} {_percent(value)}")
        elif field_name in REFERENCE_LABELS and value > 0:
            parts.append(REFERENCE_LABELS[field_name])
        elif field_name.endswith(("SpEffectId", "GoodsId", "MagicId")) and value > 0:
            continue  # a reference, not a number the player can read
        elif field_name in model.FLAT_BONUSES:
            # Same sign flip as the build maths: the engine stores per-tick HP
            # as damage, so Continuous HP Recovery holds a negative number.
            shown = -value if field_name in model.INVERTED_SIGN else value
            parts.append(f"{model.FLAT_BONUSES[field_name]} {shown:+g}")
        elif field_name.startswith(("add", "change")) and value:
            parts.append(f"{field_name} {value:+g}")

    # Status buildup found by following the SpEffect chain. The effect's own
    # row carries no numbers at all for these, so this has to come before the
    # trigger fallback below -- otherwise the effects it rescues are exactly
    # the ones that return early as "triggers a linked effect".
    for label, value in sorted((effect.get("inflicts") or {}).items()):
        if label == "Art gauge":
            parts.append(f"Art gauge {value:+g} points per trigger")
        else:
            parts.append(f"{label} buildup {value:g} per proc")

    if not parts and mods:
        # Never leave a row blank: say what the row actually carries.
        #
        # A *SpEffectId really does hand off to another row holding the
        # numbers. A bare invocationConditionsStateChange* does not -- it is a
        # precondition, "only while in this state", with no linked row to
        # find. Calling that "triggers a linked effect" sent people looking
        # for numbers that are not there.
        #
        # The clearest case is the family of 20 stat-swap effects, two per
        # Nightfarer: "[Duchess] Improved Vigor and Strength, Reduced Mind"
        # and its siblings. Each carries exactly one field, a "you are this
        # Nightfarer" state gate. Their SpEffect rows set state 2123 and hold
        # no numbers; nothing in any param reads that state back; and no row
        # in SpEffectParam raises two attributes while lowering a third. The
        # magnitudes are not in regulation.bin at all.
        if any(k.endswith("SpEffectId") for k in mods):
            return "conditional — triggers a linked effect"
        if any(k.startswith("invocationConditionsStateChange") for k in mods):
            return ("the game files carry no numbers for this — the row is "
                    "only a marker the game code acts on")

    text = ", ".join(parts[:6])
    if conditions:
        text = f"{text} ({', '.join(conditions)})" if text else \
            f"conditional ({', '.join(conditions)})"
    return text


def describe_full(effect: dict, fallback: bool = True) -> str:
    """The game's caption plus the exact numbers, whichever exist.

    The two rarely duplicate each other -- the caption says "Maximum HP
    raised", the modifiers say "Max HP +10%" -- so both are shown, caption
    first, joined by an em dash.
    """
    text = caption(effect)
    numbers = describe(effect)

    if text and numbers:
        # Don't print "Maximum HP raised — Max HP +10%" twice over when the
        # derived text adds nothing the caption did not already say.
        if numbers.lower() in text.lower():
            return text
        return f"{text} — {numbers}"
    result = text or numbers
    if result:
        return result
    return NO_DESCRIPTION if fallback else ""


def is_described(effect: dict) -> bool:
    return bool(caption(effect) or describe(effect))


def owner(effect: dict) -> str:
    """The Nightfarer a '[Name] ...' effect belongs to, or '' if general."""
    text = name(effect)
    if text.startswith("[") and "]" in text:
        return text[1:text.index("]")].strip()
    return ""


def works_for(effect: dict, hero_name: str) -> bool:
    """Is this effect actually doing anything on this Nightfarer?

    Two separate gates. An effect named "[Scholar] ..." is Scholar's alone,
    and the params also carry an allow-list per effect. Either can rule it
    out, and an effect ruled out is dead weight in the slot -- worth saying
    loudly rather than letting it read as a working buff.
    """
    who = owner(effect)
    if who and who.lower() != str(hero_name).lower():
        return False
    allowed = effect.get("allowed_heroes") or []
    if allowed and hero_name and hero_name not in allowed:
        return False
    return True
