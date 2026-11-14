"""Turn a Nightreign installation into a single self-contained data snapshot.

Everything here is derived from the user's own game files; the only external
inputs are the container keys and the PARAMDEF field schemas.
"""

from __future__ import annotations

import bisect
import collections
import functools
import hashlib
import json
import os
import pathlib
import re
import struct
from typing import Any

from . import bnd4, bossdata, dvdbnd, fmg, oodle, param, paramdef, regulation
from .binary import NotWhatItClaims

MSG_PATHS = [
    "/msg/engus/item_dlc01.msgbnd.dcx",
    "/msg/engus/menu_dlc01.msgbnd.dcx",
]

STAT_FIELDS = [
    ("statVigor", "Vigor"),
    ("statMind", "Mind"),
    ("statEndurance", "Endurance"),
    ("statStrength", "Strength"),
    ("statDexterity", "Dexterity"),
    ("statIntelligence", "Intelligence"),
    ("statFaith", "Faith"),
    ("statArcane", "Arcane"),
]

# Levels the game defines explicitly; everything between is interpolated.
MAX_LEVEL = 15

# What this extractor produces, as opposed to what the game contains.
#
# The cached snapshot was only ever rebuilt when the game's regulation.bin
# changed, which is right for a patch and wrong for an update to this file: a
# player upgrading the tool kept a snapshot built by the old extractor forever,
# and so never saw a field the new one adds. That is how the stat-swap relics
# would have stayed blank for everyone but the developer.
#
# Raise this whenever a change here alters the shape or the content of the
# snapshot, and every existing cache rebuilds itself once, in the background,
# on the next launch.
#   1  the schema as it shipped up to 1.1.0
#   2  attribute_swap on the twenty stat-swap relics; the state gate they
#      carried is dropped
#   3  Flame of Frenzy re-matched to modifier 140 (230 is the Difficult
#      Sorcerer's Rise); the three DLC events gain gating (600 / 10000 /
#      10001); day and DLC-block counts on every gating entry
#   4  deep_of_night.kinds -- what each mutation category covers, from the
#      enemy table (characters with the game's own names where it has one,
#      Limveld tiles for the area-scoped kinds)
#   5  real paramdefs for the six ChaosMatching params (Smithbox ships them,
#      Paramdex does not): the depth control table is named rather than raw
#      bytes, and the mutation figures are counts, not weights
#   6  what each depth rewards (relics, via ItemLotParam_map and the new lot
#      category 5), and the game's own filter category per effect
#   7  stacks_to on the event buffs -- the highest "+N" tier the game names
#   8  weapons[].inflicts -- status buildup per hit from the armament's own
#      spEffectBehaviorId rows, so a Poison Cleaver finally states its poison
#   9  reinforce[].catalyst_scaling -- the rate behind the spell scaling the
#      game shows for a staff or a seal, where it shows an attack rating for
#      everything else (QA-099)
#  10  weapons[].equipped_spells -- the armament's own spell slots, which is
#      what tells the catalyst row no player can hold from the one they can
#      (QA-119; the criterion and its scope are model.is_unequippable_catalyst)
#  11  world_events.rune_scaling -- the step each rune multiplier belongs to,
#      and no param name in the sentence. The figures were a bare ladder of
#      seven with no rung numbered, and the tab had to strip the param name
#      out again before it could show them (QA-148). Nothing is added to the
#      dataset's shape; the strings themselves changed, which is exactly what
#      the version check is for -- a cached snapshot would otherwise keep
#      showing the old sentence for good.
#  12  weapons[].paired -- `EquipParamWeapon.isDualBlade`, the flag that says
#      an armament is a pair held one in each hand. Two-handing a pair rates
#      by a rule of its own (QA-276), and until now nothing in the dataset
#      told a pair from a sword; R-008 had to note the flag as absent.
#  13  subbosses -- the field bosses, by the place that puts them on the map,
#      each with the weakness block a Nightlord already carries. The same
#      pass corrects deep_of_night.kinds: `smallBaseId` is a place and not a
#      character (QA-286), so `chrs` gives way to `places`. A cache left on
#      12 would keep the twenty-one character names that are places for good.
#  14  subbosses gains the night bosses of day 1 and day 2 -- the second
#      entry into the same block, over LotResultPlayAreaParam (T-299 3b), so
#      `days` is filled where it was empty on 13 and 35 more cards stand in
#      the block. A cache left on 13 would show the tab's two night groups
#      empty for good.
#  15  subbosses[].name and .chr on 21 of the 64 cards: the health bar names
#      the place rather than the character (AD-043), and one rule now reads
#      both sets of cards (AD-044). A cache left on 14 would keep sixteen
#      night cards saying "not derivable" and three cards naming the crew.
#  16  the three readings A26 needs for real spell figures (AD-050):
#      `spells[].damage`/`damage_atk` over Magic -> Bullet -> AtkParam_Pc,
#      `heroes[].starting_weapon_left`, and `effects[].start_magic_id` from
#      SpEffectParam's undescribed row tail. A cache left on 15 would leave
#      every spell cell of the Advisor without a figure.
#  17  the weapon arts (AD-056): an `arts` block with name, symbol, FP cost
#      and the motion value of the AtkParam row the art names, and on every
#      armament `art_default`, `art_pool` and, on a catalyst, `spell_pools`,
#      resolved through SwordArtsTableParam / MagicTableParam. A cache left on
#      16 would leave every tile without an art to choose and every art
#      without a figure.
#  18  `arts[].element_correct_id` -- the AttackElementCorrect row an art's
#      AtkParam row puts in place of the armament's (Glintblade Phalanx
#      scales with Intelligence alone), and the pools of an armament whose
#      EquipParamCustomWeapon rows name none taken from its base armament
#      (`id // 10000 * 10000`, AD-056 P.7): a Magic Longsword is found with
#      the Longsword's arts. A cache left on 17 would fix every found
#      variant on one art.
#  19  the status buildup an art or a spell applies to what it hits,
#      `arts[].inflicts` and `spells[].inflicts`, over AtkParam/Bullet
#      spEffectId0..4, and `effects[].inflicts_on_hit` also over the attach
#      row's onHitSpEffect ("Attacks Inflict Rot" 8110400-402). A cache left
#      on 18 would leave the advisor without those sources of an ailment
#      (user decision 01.11.2026).
#  20  the symbols the game shows for what had none here (T-340): `icon` on
#      `effects[]` (`AttachEffectParam.statusIconId`), on the world events'
#      `buffs[]` and `states[]` (`SpEffectParam.iconId`) and on every entry of
#      `drops`, and `deep_of_night.sigil_icon`. A cache left on 19 draws those
#      names without a symbol.
#  21  spell damage follows a bullet's interval-created bullets as well
#      (`Bullet.intervalCreateBulletId`, read by offset: the vendored def puts
#      it 4 bytes late) and up to 12 bullets deep. Eight spells that showed no
#      damage now carry one -- Glintstone Stars, Star Shower, Founding Rain of
#      Stars, Stars of Ruin, Magic Downpour, Rykard's Rancor, Lightning Strike,
#      Ancient Dragons' Lightning Strike -- and none of the 111 others moves
#      (measured against data_version 10350000, 08.11.2026).
#  22  a spell's own bullets that only a BehaviorParam_PC row launches count
#      too -- the counter of Carian Retaliation (Magic 245) and the burst of
#      Law of Causality (Holy 800). Their bullets sit in the spell's own id
#      block (10 000 000 + magic id x 100), and an animation fires them, so no
#      Magic or Bullet field names them (measured 08.11.2026).
#  23  `effects[].triggered` -- the numbers on the rows an effect only
#      switches on (`triggered_rows`): "Taking Damage Boosts Damage Negation"
#      is -21% for 10 s, and its own row says nothing but which row to fire.
#      A cache left on 22 keeps describing those 81 relic effects as
#      "triggers a linked effect" with no figure.
#      With it `effects[].proc_damage` and `proc_inflicts` (what the effect's
#      own bullet hits for), `effects[].one_instance` (`STACKING_CATEGORY`),
#      and `other_forms` on a Nightlord's weakness (Heolstor's first half).
#  24  what was still open after 23. `effects[].one_instance` also where the
#      number sits on a state or adjacent payload row of another category
#      (29 rollable effects); the flask effects' own rows (`FLASK_ROWS`) and
#      "Demon's Plating"'s curve (`RUNES_HELD_CURVE`) on the event buffs; and
#      the five field bosses no health bar names, by the name id their own
#      script carries (`bossdata._spawned_boss`, confidence "script"). A
#      cache left on 23 shows four of those places with the figures of an
#      add and without a name.
#  25  `heroes[].levels` between the levels the files hold is cut off
#      instead of rounded: 242 of the 1,200 values come out one lower. A
#      cache left on 24 shows those attributes one above the game's.
EXTRACT_VERSION = 25

RELIC_COLOURS = {0: "Red", 1: "Blue", 2: "Yellow", 3: "Green", 4: "White"}

# CalcCorrectGraph rows that turn an attribute into a derived stat. Verified
# against Guardian at level 1 (HP 280 / FP 55 / Stamina 60) -- all three match
# exactly with no offset or scaling factor.
DERIVED_CURVES = {
    "HP": (100, "Vigor"),
    "FP": (101, "Mind"),
    "Stamina": (81, "Endurance"),
}

# EquipParamAntique.unknown_1b == this marks a Deep of Night relic. Verified:
# all 252 "Deep ..." relics carry it and none of the 597 others do.
DEEP_MARKER = 251

# Undocumented EquipParamAntique fields holding the curse effect tables.
# Verified: every effect they yield is flagged isDebuff, and every relic that
# references one is a Deep of Night relic.
CURSE_FIELDS = ("unknown_8", "unknown_9", "unknown_10")

DAMAGE_TYPES = ("Physics", "Magic", "Fire", "Thunder", "Dark")

# Where a spell's own figures sit: the AtkParam field behind each damage type.
# A spell carries no number itself -- Magic points at bullets, a bullet points
# at an AtkParam row, and that row holds the base damage (AD-050.2).
SPELL_DAMAGE_FIELDS = {
    "Physics": "atkPhys",
    "Magic": "atkMag",
    "Fire": "atkFire",
    "Thunder": "atkThun",
    "Dark": "atkDark",
}

# The same AtkParam row carries, beside the flat figure, a percentage of the
# swing's own attack rating per damage type: the motion value of a weapon art
# (AD-056.1, ARCHITECTURE.md P.1).
ART_MOTION_FIELDS = {damage: f"{field}Correction"
                     for damage, field in SPELL_DAMAGE_FIELDS.items()}

# Where an art's AtkParam row scales by an AttackElementCorrect row of its
# own rather than the armament's (AD-056 P.7.2); -1 keeps the armament's.
ART_ELEMENT_CORRECT_FIELD = "overwriteAttackElementCorrectId"

# An armament's variants share one block of ids: the Longsword is 2000000,
# its Magic affinity 2000800 (AD-056 P.7.4).
VARIANT_SPAN = 10000

# Magic.refCategory: which table refId names. 0 is an attack row, 1 a bullet;
# 2 is a special effect and carries no damage of its own.
MAGIC_REF_ATTACK = 0
MAGIC_REF_BULLET = 1
MAGIC_REF_SPEFFECT = 2
MAGIC_REF_SLOTS = 10

# The SpEffect rows an AtkParam or Bullet row applies to what it hits: where
# an art's or a spell's status buildup sits (Zamor Ice Storm's frost 35 on
# its bullet's spEffectId0, Poison Moth Flight's poison on its attack row's
# spEffectId1).
HIT_SP_EFFECT_FIELDS = tuple(f"spEffectId{i}" for i in range(5))

# A bullet that spawns another (HitBulletID) is how a charged or delayed hit
# is built, and the strongest figure of a spell often sits on such a child:
# Beast Claw's 362 is two bullets down. The walk is capped and remembers what
# it has seen, because these chains do loop back on themselves.
MAX_BULLET_DEPTH = 12

# The bullet a bullet keeps creating while it flies -- Star Shower's stars,
# Rykard's Rancor's skulls, Magic Downpour's drops. The vendored Bullet def
# (334 bytes against Nightreign's 348-byte row) puts `intervalCreateBulletId`
# at 176 and decodes garbage there; at 172 12 248 of 12 254 rows hold -1 or an
# existing bullet id, and the other six name ids that are simply not in the
# table (measured 08.11.2026, data_version 10350000). So it is read by
# offset, beside the def, the way `startMagicId` is (below), and refused
# loudly if the def is not the one that was measured against.
BULLET_INTERVAL_FIELD = "intervalCreateBulletIdByOffset"
BULLET_INTERVAL_OFFSET = 172
BULLET_DEF_SIZE = 334

# Where a spell's bullets are numbered: Glintstone Pebble (4000) shoots
# 10400000, Carian Retaliation (4640) 10464000..10464022. 987 of the 1036
# bullets the Magic rows reach lie in their spell's block; the other 49 are
# shared helpers. The block is used one way only: a bullet in it that a
# BehaviorParam_PC row launches belongs to the spell, because the animation
# that fires it is the spell's own.
SPELL_BULLET_BLOCK_BASE = 10_000_000
SPELL_BULLET_BLOCK_SIZE = 100
BEHAVIOR_REF_BULLET = 1
BEHAVIOR_REF_ATTACK = 0
#: The mists hit for Physical 1 only to register a touch; that is not damage.
PROC_DAMAGE_FLOOR = 1

# SpEffectParam's row is 1024 bytes and the shipped def describes 976 of them.
# Offset 1020 holds the spell a swap relic hands the player (AD-050.4).
START_MAGIC_FIELD = "startMagicId"
START_MAGIC_OFFSET = 1020
SP_EFFECT_DEF_SIZE = 976

# The rate behind the number the game shows for a staff or a seal. It is the
# last field of a ReinforceParamWeapon row -- offset 128, f32 -- and the
# Paramdex has no name for it, so the placeholder is the only handle there
# is: `vendor/Paramdex/NR/Defs/ReinforceParamWeapon.xml` writes
# `<Field Def="f32 unknown_1" />`. The def covers the row exactly (row_size
# 132 = pdef.row_size 132), so the offset is read off the schema rather than
# guessed.
#
# What it is was measured, not inferred from the name: the game shows
# `floor(90 x this x (1 + curve(INT or FAI)/100))`, which hits 84 of 84
# measured cells and 28 of 28 of a second, independent list exactly
# (`docs/berichte/T-043-qa-engineer.md`, QA-099).
CATALYST_SCALING_FIELD = "unknown_1"

# What the shipped game data holds, so a later reader can see how much room
# the check below leaves: 97 of the 255 reinforce rows carry a rate other
# than 1.0, spread over 30 groups, and every armament sitting on one of them
# is a staff or a seal (measured 2026-09-03, T-043 section 2).
CATALYST_SCALING_ROWS_TODAY = 97

# Magic.spEffectCategory: verified against the spell names themselves --
# 3 holds Glintstone Pebble and Comet, 4 holds Catch Flame and O, Flame!
SPELL_CATEGORIES = {3: "Sorceries", 4: "Incantations"}

# Weapon types no relic buff names, read off from what they contain.
# Status buildup fields on a SpEffect row, shared by two walks: the relic
# effects follow their hand-off chain to these (the curse rows are empty and
# the number sits three hops on), and every armament's own
# spEffectBehaviorId0..2 rows carry the same fields for what the weapon
# inflicts on hit. Module-level so both readers and the probe script agree
# on one list by construction.
STATUS_POWER = {
    "poizonAttackPower": "Poison",
    "diseaseAttackPower": "Scarlet Rot",
    "bloodAttackPower": "Blood Loss",
    "freezeAttackPower": "Frost",
    "sleepAttackPower": "Sleep",
    "madnessAttackPower": "Madness",
    "curseAttackPower": "Death Blight",
}

# ---- Numbers on the rows an effect only triggers ---------------------------
# 81 relic effects carry a hand-off and nothing else on their own rows:
# "Taking Damage Boosts Damage Negation" is cycleOccurrenceSpEffectId 8620101,
# and the eight cut rates at 0.79 for 10 s sit on 8620102, which that row
# switches on through state 2284. The state and adjacent payloads above never
# look, because a hand-off counts as substance. `triggered_rows` walks the
# hand-offs and returns those rows.
#
# Only these fields, because every one of them has a reading the planner
# already prints. ponytail: a whitelist; a triggered row whose only content
# is another field stays unreported until the field is added here.
TRIGGERED_FIELDS = frozenset({
    "physicsAttackRate", "magicAttackRate", "fireAttackRate",
    "thunderAttackRate", "darkAttackRate",
    "slashDamageCutRate", "blowDamageCutRate", "thrustDamageCutRate",
    "neutralDamageCutRate", "magicDamageCutRate", "fireDamageCutRate",
    "thunderDamageCutRate", "darkDamageCutRate", "toughnessDamageCutRate",
    "changeHpPoint", "changeMpPoint", "changeStaminaPoint",
    "changeHpRate", "changeMpRate",
    "maxHpRate", "maxMpRate", "maxStaminaRate",
    "soul", "staminaRecoverChangeSpeed",
    "sightSearchEnemyRate", "hearingSearchEnemyRate",
    "ultimateArtDuration",
})
#: Concealment. Five rows set it, and the three with a game text are Cold
#: Mirage ("Conceals oneself"), "Frostbite in Vicinity Conceals Self" and the
#: Duchess's "difficult to spot". `_buff_lines` words it "invulnerable" after
#: Cold Mirage's caption; the relic that is named invulnerability sets 2394.
CONCEALED_STATE = 600
# ---- Which SpEffect can be on a character twice -----------------------------
# Not in any param: read out of nightreign.exe (data_version 10350000,
# 09.11.2026). The function at 0x14050d05f puts a SpEffect on a character. It
# walks the list of active ones first and asks of each (0x140510b20) "is this
# the same id?" -- and that test answers no without looking when the active
# one's spCategory is 10. Only then is a second node appended (0x14050d368).
# For every other category the same id is found: category 20 has the active
# node written over, which restarts its timer (0x140511450, 0x140511700), and
# category 0 has the new one dropped. So a row of category 10 stacks with
# itself and no other row does.
#
# The totals then take every active node in turn and multiply its rate in
# (0x140503730, 0x140504387: `mulss` into the running product, node after
# node), which is why two *different* effects on one field multiply.
#
# It agrees with the one case measured in the game: "+1 additional Character
# Skill use" would not add up over several relics (`model.NON_ACCUMULATING`),
# and its row 7033200 is category 20.
STACKING_CATEGORY = 10

TRIGGER_LINKS = ("replaceSpEffectId", "cycleOccurrenceSpEffectId",
                 "atkOccurrenceSpEffectId", "applyIdOnGetSoul",
                 "accumuOverFireId")
TRIGGER_DEPTH = 6
#: A state more rows than this wait on is the engine's, not one effect's.
TRIGGER_STATE_ROWS = 8


def effect_rows(sp_ids, values_of, gated_on, owned, applied_by=None):
    """Every SpEffect row an effect reaches, as (id, hops, values), own first.

    `values_of` is SpEffect id -> field values, `gated_on` is state -> ids of
    the rows waiting on it, `owned` the ids other effects name as their own,
    and `applied_by` turns a row's behaviorId into the SpEffect ids its
    bullets put on whoever they touch -- the only link to the number of an
    aura ("Raised stamina recovery for nearby allies" is a bullet applying
    7050001).

    Fenced to the id block of the effect's own rows, and never into a row
    another effect owns.
    """
    blocks = {sp_id // 100 for sp_id in sp_ids}
    seen = set(sp_ids)
    queue = [(sp_id, 0) for sp_id in sp_ids]
    while queue:
        sp_id, depth = queue.pop(0)
        values = values_of.get(sp_id)
        if values is None:
            continue
        yield sp_id, depth, values
        if depth >= TRIGGER_DEPTH:
            continue
        nxt = [values.get(link) for link in TRIGGER_LINKS]
        waiting = gated_on.get(values.get("stateInfo") or 0, ())
        if len(waiting) <= TRIGGER_STATE_ROWS:
            nxt += waiting
        behavior = values.get("behaviorId") or 0
        if applied_by is not None and behavior > 0:
            nxt += applied_by(behavior)
        for target in nxt:
            if (isinstance(target, int) and target > 0 and target not in seen
                    and target not in owned and target // 100 in blocks):
                seen.add(target)
                queue.append((target, depth + 1))


def triggered_rows(sp_ids, values_of, gated_on, owned, baseline,
                   applied_by=None) -> list[dict]:
    """The rows an effect switches on, with the numbers they hold.

    The arguments are `effect_rows`'s, whose fences this relies on.

    So it cannot report another effect's number (7032200 reaches 7032202,
    never the engine's poison row 505), and it skips a row that builds up an
    ailment -- `inflicts` reports that one, and what follows it is the
    ailment's own tick, not the relic's.
    """
    # An effect whose state also fires behaviours outside its own block does
    # more than this walk can see, and the part inside the block would stand
    # for the whole: "Items confer effect to all nearby allies" sets state
    # 2013, which fires 708504 and 708505 besides its own 7050101, and
    # 7050102's FP figure is one item's share of it.
    blocks = {sp_id // 100 for sp_id in sp_ids}
    for sp_id in sp_ids:
        state = (values_of.get(sp_id) or {}).get("stateInfo") or 0
        waiting = gated_on.get(state, ())
        if len(waiting) <= TRIGGER_STATE_ROWS and any(
                row // 100 not in blocks
                and ((values_of.get(row) or {}).get("behaviorId") or 0) > 0
                for row in waiting):
            return []
    found: list[dict] = []
    for sp_id, depth, values in effect_rows(sp_ids, values_of, gated_on,
                                            owned, applied_by):
        if not depth or any((values.get(f) or 0) > 0 for f in STATUS_POWER):
            continue
        numbers = {f: values[f] for f in sorted(TRIGGERED_FIELDS)
                   if f in values and f in baseline
                   and values[f] != baseline[f]}
        # Not the 0.1 s pulse the Duchess's row opens with.
        if (values.get("stateInfo") == CONCEALED_STATE
                and values.get("effectEndurance", 0) >= 1):
            numbers["stateInfo"] = CONCEALED_STATE
        if numbers:
            duration = values.get("effectEndurance", -1.0)
            if duration > 0:
                numbers["effectEndurance"] = duration
            found.append({"sp_id": sp_id,
                          "sp_category": values.get("spCategory"),
                          "modifiers": numbers})
    return found


FALLBACK_WEAPON_FAMILIES = {
    "33": "Unarmed",
    "53": "Greatbow",
    "55": "Crossbow",
    "56": "Ballista",
    "57": "Glintstone Staff",
    "61": "Sacred Seal",
    "65": "Small Shield",
    "67": "Medium Shield",
    "69": "Greatshield",
    "87": "Torch",
}

# Attribute name -> the token FromSoftware uses in the scaling field names.
AEC_STATS = {
    "Strength": "Strength",
    "Dexterity": "Dexterity",
    "Intelligence": "Magic",
    "Faith": "Faith",
    "Arcane": "Luck",
}

ALLOW_FIELDS = [
    "allowWylder", "allowGuardian", "allowIroneye", "allowDuchess",
    "allowRaider", "allowRevenant", "allowRecluse", "allowExecutor",
]


def _load_text(archives) -> dict[str, dict[int, str]]:
    """Load every FMG from the localised message archives.

    Base and expansion tables are merged under the base name, since every
    caller wants one lookup. Which ids came from the expansion is still worth
    knowing -- a player without the DLC will never see those lines -- so each
    table that has an expansion half also gets a `"<name>::dlc"` entry holding
    only that half. Nothing is lost and no existing key changes meaning.
    """
    out: dict[str, dict[int, str]] = {}
    for path in MSG_PATHS:
        arc = next((a for a in archives.values() if path in a), None)
        if arc is None:
            continue
        for member in bnd4.read(arc.read(path)):
            if not member.basename.endswith(".fmg"):
                continue
            name = member.basename[: -len(".fmg")].replace("_dlc01", "")
            try:
                strings = fmg.read(member.data)
            except Exception:  # noqa: BLE001 - a broken FMG must not kill the run
                continue
            out.setdefault(name, {}).update(strings)
            if "_dlc01" in member.basename:
                out.setdefault(f"{name}::dlc", {}).update(strings)
    return out


def _modal_baseline(rows: list[param.ParamRow], fields: list[str]) -> dict[str, Any]:
    """The neutral, do-nothing value per field.

    Only fields with a clear dominant value are kept. Where no value dominates,
    there is no meaningful "unchanged" state, so reporting a deviation from the
    mode would be noise rather than a real effect.
    """
    baseline: dict[str, Any] = {}
    for name in fields:
        counter = collections.Counter(
            r.values[name] for r in rows if not isinstance(r.values.get(name), list)
        )
        if not counter:
            continue
        value, count = counter.most_common(1)[0]
        if count >= 0.9 * len(rows):
            baseline[name] = value
    return baseline


# ---------------------------------------------------------------------------
# Bosses and Deep of Night
# ---------------------------------------------------------------------------

# NightBossMenuParam holds each Nightlord expedition twice. The sortId says
# which is which: the ordinary expeditions sort below 200, their Everdark
# Sovereign counterparts above it, and row 100 (sortId 300) is the Deep of
# Night mode itself rather than a boss.
EVERDARK_SORT_THRESHOLD = 200
DEEP_MODE_SORT = 300

# The game's own name for the second group, so the label is not invented
# here. 131040 = "Everdark Sovereign".
EVERDARK_LABEL_ID = 131040

# TutorialBody row explaining Depth and the rating bands behind it.
DEEP_RATING_TEXT_ID = 403500

# EquipParamAntique row for the Sovereign Sigil, the everdark currency.
SOVEREIGN_SIGIL_ID = 11

# SessionRewardByModeRankParam ids. 5100..5500 are the five depths; the 1000
# and 2000 rows are the other modes and are not part of this tab.
DEEP_REWARD_IDS = [5100, 5200, 5300, 5400, 5500]

# The scaling SpEffects move these and nothing else. Field names are the
# game's own; the labels are only for display.
SCALING_FIELDS = {
    "maxHpRate": "HP",
    "physicsAttackPowerRate": "Physical attack",
    "magicAttackPowerRate": "Magic attack",
    "fireAttackPowerRate": "Fire attack",
    "thunderAttackPowerRate": "Lightning attack",
    "darkAttackPowerRate": "Holy attack",
    "staminaAttackRate": "Stamina damage",
    # How much stance damage the enemy *receives*. It falls with depth
    # (0.88 down to 0.84), so deeper enemies are harder to stagger. Without
    # it the tab could not answer "are they harder to break", and the
    # similarly named staminaAttackRate answers the opposite question.
    "saReceiveDamageRate": "Stance damage taken",
}

DEPTH_COUNT = 5


def _raw_rows(data: bytes) -> tuple[list[tuple[int, bytes]], int]:
    """Every row as (id, bytes).

    param.read exposes decoded fields only, which is no use for the Deep of
    Night params -- none of them ship a paramdef, so their layout has to be
    read from the bytes directly.
    """
    r = param.Reader(data)
    strings_offset = r.u32()
    r.u16()
    r.u16()
    r.u16()
    row_count = r.u16()
    r.seek(0x30)
    data_offset = r.u64()
    row_size = (strings_offset - data_offset) // row_count if row_count else 0

    rows = []
    for i in range(row_count):
        e = param.Reader(data, 0x40 + i * 24)
        row_id = e.i64()
        offset = e.u64()
        rows.append((row_id, data[offset : offset + row_size]))
    return rows, row_size


def _bosses(members: dict, defs: dict, menu_text: dict[int, str],
            game_dir: pathlib.Path | None = None) -> list[dict]:
    """The Nightlords, their expeditions and their artwork.

    The second block of rows is the **Everdark Sovereign** set, not a Deep of
    Night one. They reuse the base bosses' exact expeditionNameId, bossNameId
    and descriptionId and differ only in sortId and artwork, and the game's own
    label for the group is CL_MenuText 131040, "Everdark Sovereign". The Deep
    of Night is a separate menu entry entirely (131150, sortId 300).

    Resistances are absent, and that is a data limit. They live in NpcParam and
    nothing in regulation.bin links the menu to an NPC row: no NpcParam row
    carries a boss nameId, the name ids appear in no NpcParam field, unknown_5
    is a scenario id (it resolves through the boss music table to
    "_CL_Scenario_05_Power_R1" and friends), and the reward-lot chain dead-ends
    because ItemLotParam_enemy ships no def. The link is in the map files.
    Both routes were followed to their ends rather than assumed shut.
    """
    table = param.read(members["NightBossMenuParam"], defs.get("NightBossMenuParam"))

    # Resistances, via the event scripts and the arena map. See nrdata/bossdata.
    # A failure here costs the weakness block and nothing else, so it must not
    # be able to take the whole snapshot down.
    weakness: dict[int, dict] = {}
    if game_dir is not None:
        try:
            npc = param.read(members["NpcParam"], defs.get("NpcParam"))
            weakness = bossdata.derive(game_dir, members, defs, npc)
        except Exception as exc:  # noqa: BLE001
            print(f"   boss weaknesses unavailable: {exc}")

    def caption(text_id: int) -> str:
        return (menu_text.get(text_id) or "").strip()

    everdark_label = caption(EVERDARK_LABEL_ID) or "Everdark Sovereign"

    # unknown_5 is a scenario id, and the boss music table turns it into that
    # scenario's own Wwise cue name -- "_CL_Scenario_06_Necromancer". Only some
    # of the eight have a row, so this is best-effort.
    cues: dict[int, str] = {}
    bgm = members.get("WwiseValueToStrParam_BgmBossChrIdConv")
    if bgm is not None:
        for row_id, blob in _raw_rows(bgm)[0]:
            printable = "".join(chr(b) if 32 <= b < 127 else "" for b in blob)
            if printable.strip():
                cues[row_id] = printable.strip().lstrip("_")

    bosses = []
    for row in table.rows:
        v = row.values
        sort_id = v.get("sortId", 0)
        if sort_id == DEEP_MODE_SORT:
            continue  # the mode itself, carried on the Deep of Night tab
        name = caption(v.get("bossNameId", -1))
        if not name:
            continue
        bosses.append(
            {
                "id": row.id,
                "name": name,
                "expedition": caption(v.get("expeditionNameId", -1)),
                "description": caption(v.get("descriptionId", -1)),
                "icon": v.get("bossIconId"),
                "large_icon": v.get("largeBossIconId"),
                "defeated_icon": v.get("defeatedBossIconId"),
                "background": v.get("expeditionBackgroundId"),
                "sort": sort_id,
                "is_everdark": sort_id >= EVERDARK_SORT_THRESHOLD,
                # The game names the Everdark group itself; it has no label of
                # its own for the base set, so that heading is the app's.
                "group": (everdark_label
                          if sort_id >= EVERDARK_SORT_THRESHOLD else "Nightlords"),
                "unlock_event_flag": v.get("unlockEventFlag"),
                "defeat_event_flag": v.get("defeatEventFlag"),
                "scenario_id": v.get("unknown_5"),
                "music_cue": cues.get(v.get("unknown_5", -1), ""),
                "weakness": weakness.get(v.get("defeatEventFlag")),
                # Four fields the def does not name. They are real and they
                # differ per boss, so they are carried rather than dropped --
                # but nothing in the files says what they mean, so the tab
                # shows them as unidentified. Observed shape: unknown_12 is 0
                # on every Everdark row and non-zero on every base row.
                "unnamed": {
                    "unknown_11": v.get("unknown_11"),
                    "unknown_12": v.get("unknown_12"),
                    "unknown_13": v.get("unknown_13"),
                    "unknown_14": v.get("unknown_14"),
                },
            }
        )
    # An Everdark row shares its base boss's resistances, and that is a
    # finding rather than a shortcut: every boss character has exactly ONE
    # distinct damage/status profile across all of its NpcParam rows (Gladius
    # has 28 rows, all identical), and no separate Everdark character or row
    # exists anywhere. The Everdark differences players report -- Adel's
    # poison stagger not firing, for one -- are behavioural, and behaviour is
    # not resistance data. The tab says exactly that rather than implying the
    # fight is unchanged.
    by_unlock = {b["defeat_event_flag"]: b for b in bosses if not b["is_everdark"]}
    for boss in bosses:
        if not boss["is_everdark"] or boss.get("weakness"):
            continue
        base = by_unlock.get(boss["unlock_event_flag"])
        if base and base.get("weakness"):
            boss["weakness"] = dict(base["weakness"], confidence="shared",
                                    shared_from=base["name"])

    bosses.sort(key=lambda b: b["sort"])
    return bosses


# The sub-bosses of stage one are one category of the place roster: 120, the
# field bosses. It holds 45 places, of which the world map shows 29; the other
# 16 are m20_00 to m21_50, which no SmallBaseAndSpotDefine row names and which
# all hold the same c4680 -- arena shells, not boss places (T-299 2b/2c).
# Reading a map costs the first run time, and those 16 would buy one character
# sixteen times, so the roster is the 29 the world map places.
FIELD_BOSS_CATEGORY = 120

# The two card fields of one `LotResultPlayAreaParam` row, day 1 then day 2.
# The two `extraBoss` fields beside them are left alone: nothing establishes
# what they draw for, and a card named from them would be a guess (A7).
NIGHT_BOSS_FIELDS = ("bossId1", "bossId2")


def _map_of_place(place: int) -> str:
    """A place id is a map: 4651 is m46_51_00_00, for all 116 (T-299 2a)."""
    return f"m{place // 100:02d}_{place % 100:02d}_00_00"


def _subbosses(members: dict, defs: dict, text: dict[str, dict[int, str]],
               archives, sp_rows: dict[int, param.ParamRow]) -> dict[str, Any]:
    """Every sub-boss a run can put on the map, keyed by its place.

    Two lotteries fill one block: the place lottery draws the field bosses
    (`ChaosMatchingMutationEnemyTableParam` plus `LotResultSmallBaseAndSpot`),
    and the night lottery draws the bosses of day 1 and day 2
    (`LotResultPlayAreaParam`, T-299 3b). They are joined on `patternId` and
    their card ids do not overlap, so `days` alone says which lottery a card
    came from.

    The place is the unit, not the character: the same character carries
    different figures from one place to the next (Draconic Tree Sentinel has
    2324 HP on m46_52 and 1633 on m48_50), so a character-keyed block would
    be wrong wherever it repeats. The key is text because the snapshot is
    JSON and has no other kind of key (D-001), and `weakness` is exactly the
    block a Nightlord already carries, so one panel renders both.

    `nightlords[].patterns` of `of` is how much of that Nightlord's own map
    patterns draw this place. That is the composition of the pool and not a
    draw probability -- `MapPatternSet` weights the patterns themselves --
    which is the same limit `_gating` states for the events.
    """
    define = param.read(members["SmallBaseAndSpotDefine"],
                        defs.get("SmallBaseAndSpotDefine"))
    on_world_map = {value for row in define.rows
                    for field, value in row.values.items()
                    if field.startswith("mapId") and value}

    enemy_table = param.read(
        members["ChaosMatchingMutationEnemyTableParam"],
        defs.get("ChaosMatchingMutationEnemyTableParam"))
    categories: dict[int, set[int]] = {}
    for row in enemy_table.rows:
        place = row.values["smallBaseId"]
        if (row.values["categoryId"] != FIELD_BOSS_CATEGORY
                or place not in on_world_map):
            continue
        categories.setdefault(place, set()).add(row.values["categoryId"])

    # Which Nightlord draws which place, over patternId -- the same join
    # `_gating` uses for the events, and rows with `unknown_0` set are left
    # out here for the same reason.
    flag_table = param.read(members["LotResultMapPatternFlag"],
                            defs.get("LotResultMapPatternFlag"))
    pattern_boss = {values["patternId"]: values["targetBoss"]
                    for values in (row.values for row in flag_table.rows)
                    if not values["unknown_0"]}
    pool = collections.Counter(pattern_boss.values())

    drawn: dict[int, dict[int, set[int]]] = {}
    spot_table = param.read(members["LotResultSmallBaseAndSpot"],
                            defs.get("LotResultSmallBaseAndSpot"))
    for row in spot_table.rows:
        place = row.values["smallBaseMapId"]
        boss = pattern_boss.get(row.values["patternId"])
        if place not in categories or boss is None:
            continue
        drawn.setdefault(place, {}).setdefault(boss, set()).add(
            row.values["patternId"])

    # The night bosses, from their own lottery: one row per pattern, the
    # card of day 1 in `bossId1` and the card of day 2 in `bossId2`, in the
    # same card-id space as `smallBaseId` (T-299 3b). The place lottery
    # never draws these cards -- its own boss spots do not appear in it at
    # all (T-299 3c) -- so this is the only pass that can name them.
    play_table = param.read(members["LotResultPlayAreaParam"],
                            defs.get("LotResultPlayAreaParam"))
    days: dict[int, set[int]] = {}
    for row in play_table.rows:
        boss = pattern_boss.get(row.values["patternId"])
        for day, field in enumerate(NIGHT_BOSS_FIELDS, start=1):
            place = row.values[field]
            if not place:
                continue
            days.setdefault(place, set()).add(day)
            if boss is not None:
                drawn.setdefault(place, {}).setdefault(boss, set()).add(
                    row.values["patternId"])

    npc = param.read(members["NpcParam"], defs.get("NpcParam"))

    # Names are the game's own (NpcName). Two routes to one: the map script
    # hands a name id in per entity for the health bar, and the structured id
    # (90 <4-digit character> <3-digit variant>) names the character where no
    # script does -- `nameId` on the row carries nothing in Nightreign, but
    # costs one lookup to keep (T-307 section 1). The script goes first:
    # where both speak and disagree, the name chosen for this place beats the
    # one that happened to come first in the table (AD-043 point 2).
    npc_names = text.get("NpcName", {})
    chr_names: dict[int, str] = {}
    for name_id, label in npc_names.items():
        if 900000000 <= name_id <= 909999999 and label and label.strip():
            chr_names.setdefault((name_id - 900000000) // 1000, label.strip())
    for row in npc.rows:
        label = (npc_names.get(row.values.get("nameId", -1)) or "").strip()
        if label:
            chr_names.setdefault(row.id // 10000, label)

    # One call for both lotteries: the same rule reads both sets of cards
    # (AD-044), and their id spaces do not overlap (T-299 3b). The named
    # characters go in so that a place whose map holds none of them can be
    # given the boss its script brings in.
    weakness = bossdata.derive_places(
        archives, npc,
        {place: _map_of_place(place) for place in set(categories) | set(days)},
        sp_rows, named=set(chr_names))

    out: dict[str, Any] = {}
    for place in sorted(set(categories) | set(days)):
        entry = weakness[place]
        chr_id = entry["primary"]
        out[str(place)] = {
            "map": entry["map"],
            "categories": sorted(categories.get(place, ())),
            "days": sorted(days.get(place, ())),
            "nightlords": [
                {"boss": boss, "patterns": len(patterns), "of": pool[boss]}
                for boss, patterns in sorted(drawn.get(place, {}).items())
            ],
            "chr": chr_id,
            "name": (npc_names.get(entry.get("name_id"))
                     or chr_names.get(chr_id, "")),
            # Filled only where the files put more than one boss-scale
            # character in the place: then none of them is named, and the
            # candidates stand for themselves (GOAL A7).
            "candidates": [
                {"chr": candidate, "hp": entry["parts"][str(candidate)]["hp"]}
                for candidate in entry["chars"]
            ] if entry["confidence"] == "ambiguous" else [],
            "weakness": entry,
        }
    return out


def _icon(value: Any) -> int | None:
    """A symbol id as a param row states it; 0 and -1 mean there is none."""
    return value if isinstance(value, int) and value > 0 else None


def _deep_of_night(members: dict, defs: dict, menu_text: dict[int, str],
                   text: dict[str, dict[int, str]],
                   subbosses: dict[str, Any]) -> dict:
    """The five depths: enemy scaling, reward scaling and mutation weighting.

    None of the ChaosMatching params ship a paramdef, so the layouts here are
    inferred. Two things make the inference solid rather than a guess: every
    20-byte ChaosMatchingCorrectParam row reads as five consecutive SpEffect
    ids and 89 of 90 rows resolve all five in SpEffectParam with none missing,
    and the resulting values are monotonic across the five depths. Five is also
    the row count of ChaosMatchingRankControlParam.
    """
    sp = param.read(members["SpEffectParam"], defs.get("SpEffectParam"))
    sp_by_id = {r.id: r for r in sp.rows}

    # ---- per-depth enemy scaling ----------------------------------------
    profiles: dict[tuple, dict] = {}
    unresolved = 0
    correct_rows, _ = _raw_rows(members["ChaosMatchingCorrectParam"])
    for row_id, blob in correct_rows:
        ids = tuple(struct.unpack_from("<5i", blob))
        if ids[0] == -1:
            continue
        if not all(i in sp_by_id for i in ids):
            unresolved += 1
            continue
        if ids in profiles:
            profiles[ids]["rows"].append(row_id)
            continue

        # Rounded because these are f32: the authored 1.55 reads back as
        # 1.5499999523162842, and four places is far past anything the game
        # distinguishes while keeping the snapshot readable.
        per_depth = []
        for effect_id in ids:
            values = sp_by_id[effect_id].values
            per_depth.append(
                {
                    field: round(float(values[field]), 4)
                    for field in SCALING_FIELDS
                    if isinstance(values.get(field), (int, float))
                }
            )
        # A field that is 1.0 at every depth is the neutral value and says
        # nothing; drop it rather than filling the table with ones.
        moving = [
            field for field in SCALING_FIELDS
            if any(abs((d.get(field) or 1.0) - 1.0) > 1e-6 for d in per_depth)
        ]
        profiles[ids] = {
            "sp_effect_ids": list(ids),
            "rows": [row_id],
            "fields": moving,
            "per_depth": [{f: d.get(f) for f in moving} for d in per_depth],
        }

    # ---- what each depth actually hands you ------------------------------
    # `SessionRewardByModeRankParam` carries `itemLotId_1..4`, which nothing
    # here read until the param gained a def. The lots are in
    # `ItemLotParam_map` -- not `_enemy`, which is why earlier passes found
    # nothing -- and they resolve through lot category 5 to relics. The tier
    # climbs with depth: Polished and Deep Delicate Burning Scene at Depth 1,
    # Grand Burning Scene by Depth 3. Ids sharing a name differ in their
    # rolled effects, so the reward is "one of these rolls", which is how the
    # game hands relics out; the names are therefore deduplicated.
    reward_items = _depth_reward_items(members, defs, text)

    # ---- per-depth reward scaling ---------------------------------------
    reward_rows = dict(_raw_rows(members["SessionRewardByModeRankParam"])[0])
    rewards = []
    for reward_id in DEEP_REWARD_IDS:
        blob = reward_rows.get(reward_id)
        if blob is None:
            rewards.append(None)
            continue
        # Nine identical f32 multipliers, then an s32 that steps 8/10/12/15/18.
        # That second value is not the depth rating -- the game's own tutorial
        # puts the Depth 1 -> 2 threshold at 1000, which 8 a win could not
        # feed. It was identified in game as the Sovereign Sigil award, and
        # AntiqueName 11 / AntiqueInfo 11 name that item and call it "rays of
        # everdark used for bartering in the Roundtable Hold". The value is the
        # game's; the field has no name in the files, so the label rests on
        # that identification rather than on a link the params provide.
        rewards.append(
            {
                "multiplier": round(struct.unpack_from("<f", blob, 0)[0], 4),
                "sigils": struct.unpack_from("<i", blob, 36)[0],
                "items": reward_items.get(reward_id, []),
            }
        )

    # ---- mutations per depth ---------------------------------------------
    # Read by inspection until 2026-08-16, when a real paramdef turned up
    # (Smithbox ships one; Paramdex does not). It confirms the layout that
    # was inferred and corrects the most important thing about it:
    #
    #   depth1Count .. depth5Count  -- these are **counts, not weights**.
    #       The figure is how many mutations of that kind the map places at
    #       that depth, so it is a number a player can go and count, not a
    #       share of an unknown pool. That also matches what the owner
    #       reports from play: "many, several in every camp."
    #   categoryId    -- the kind. Confirms the inferred offset.
    #   modifierMapId -- the map, by the game's own field name, confirming
    #       the identification made from the Shifting Earth modifier ids.
    mutations = []
    category_table = param.read(
        members["ChaosMatchingMutationCategoryParam"],
        defs.get("ChaosMatchingMutationCategoryParam"))
    for row in category_table.rows:
        values = row.values
        counts = [values[f"depth{i}Count"] for i in range(1, 6)]
        mutations.append(
            {
                "id": row.id,
                "counts": counts,
                "category": values["categoryId"],
                "group": values["modifierMapId"],
                "varies": len(set(counts)) > 1,
            }
        )

    # ---- what each mutation kind covers ----------------------------------
    # ChaosMatchingMutationEnemyTableParam: 3067 x 48-byte rows, no def.
    # Read by inspection, with three anchors that make the layout solid:
    #
    # - The low byte of the leading u16 is the category. Its 19 observed
    #   values are exactly the 18 category bytes of the weight table above
    #   plus one (102) that has no weight row -- present in the roster,
    #   absent from the draw.
    # - `smallBaseId` at +6, where set, is a **place**: all 116 of its values
    #   name an existing m{AA}_{BB}_00_00 map, 100 of them stand as `mapIdN`
    #   in SmallBaseAndSpotDefine and the other 16 as an attach point's
    #   `defaultSmallBase` (T-299 section 2a). Reading it as a character hit
    #   21 of the 116 by coincidence -- two number spaces overlapping, not a
    #   correct read: place 4650 is m46_50, which holds no c4650, while
    #   c4650 stands in two maps that are not it (QA-286).
    # - u32 at +12, where set (667 rows, exactly the rows with no place),
    #   reads 604|XX|YY with XX 42-45 and YY 36-39 -- the Limveld tile grid,
    #   so those kinds are scoped to map areas rather than to places.
    #
    # A name for a place is the boss standing in it, and that is resolved
    # once, in `_subbosses`, for the places this extractor reads maps for.
    # The rest carry the place and no name, which is what the files say.
    kinds: dict[int, dict] = {}
    enemy_table = param.read(
        members["ChaosMatchingMutationEnemyTableParam"],
        defs.get("ChaosMatchingMutationEnemyTableParam"))
    for row in enemy_table.rows:
        values = row.values
        category = values["categoryId"]
        target = values["smallBaseId"]
        # Likewise `mapUnk_1/2/3`, which the def leaves unnamed: read as one
        # little-endian u32 the field is packed decimal 60|XX|YY, giving the
        # 4x4 grid of real m60_4X_3Y Limveld tiles. The def's byte split
        # produces (76, 56, 9), which names nothing.
        tile = (values["mapUnk_1"] | (values["mapUnk_2"] << 8)
                | (values["mapUnk_3"] << 16))
        kind = kinds.setdefault(
            category, {"rows": 0, "places": {}, "tiles": set()})
        kind["rows"] += 1
        if target:
            kind["places"][target] = kind["places"].get(target, 0) + 1
        elif tile:
            kind["tiles"].add(f"m60_{tile // 100 % 100}_{tile % 100}")
    for kind in kinds.values():
        kind["places"] = [
            {"place": place, "map": _map_of_place(place), "rows": count,
             "name": (subbosses.get(str(place)) or {}).get("name") or None}
            for place, count in sorted(kind["places"].items(),
                                       key=lambda kv: -kv[1])
        ]
        kind["tiles"] = sorted(kind["tiles"])
    kinds_out = {str(cat): kind for cat, kind in sorted(kinds.items())}

    # ---- the depth control table -----------------------------------------
    # SOLVED 2026-08-16. This was read byte by byte for the life of the
    # project, with the meaning of each column matched against what players
    # describe rather than stated by the files. A paramdef for it exists
    # after all -- Smithbox ships defs for all six ChaosMatching params that
    # Paramdex does not -- and the game's own field names confirm the
    # community reading exactly:
    #
    #   +2/+3/+4  mapChallengeWeight_Map / _Nightlord / _None
    #             0/0/100 at Depths 1-2, 10/10/80 from Depth 3 -- one roll of
    #             three, which is why the map and the Nightlord are never
    #             concealed together.
    #   +5/+6/+7  cataclysmWeight_0 / _1 / _2
    #             the number of cataclysm sites. Weight_0 is 0 in every row,
    #             so a run always has at least one, and the 50/50 -> 5/95
    #             series is the chance of the second.
    #   +0/+1     cursedUncommonRate 25, cursedRareRate 40, flat across all
    #             five depths -- new, and not previously readable at all.
    control = []
    control_table = param.read(members["ChaosMatchingRankControlParam"],
                               defs.get("ChaosMatchingRankControlParam"))
    for row in control_table.rows:
        values = row.values
        control.append({
            "depth": row.id,
            "cursed_uncommon": values["cursedUncommonRate"],
            "cursed_rare": values["cursedRareRate"],
            "conceal_map": values["mapChallengeWeight_Map"],
            "conceal_nightlord": values["mapChallengeWeight_Nightlord"],
            "conceal_none": values["mapChallengeWeight_None"],
            "cataclysms_1": values["cataclysmWeight_1"],
            "cataclysms_2": values["cataclysmWeight_2"],
        })

    # TutorialBody 403500, "The Deep of Night: Depth and Rating" -- the game's
    # own statement of the rating bands behind each Depth.
    # The tutorial strings carry inline gamepad/image markup like
    # "<?image@4500##17?>", which is a button glyph the app cannot render.
    sigil_name = (text.get("AntiqueName", {}).get(SOVEREIGN_SIGIL_ID) or "").strip()
    sigil_info = (text.get("AntiqueInfo", {}).get(SOVEREIGN_SIGIL_ID) or "").strip()
    sigil_icon = next(
        (_icon(row.values.get("iconId")) for row in param.read(
            members["EquipParamAntique"], defs.get("EquipParamAntique")).rows
         if row.id == SOVEREIGN_SIGIL_ID), None)

    rating_text = re.sub(
        r"<\?[^>]*\?>", "",
        (text.get("TutorialBody", {}).get(DEEP_RATING_TEXT_ID) or ""),
    ).strip()

    mode_text = ""
    boss_table = param.read(members["NightBossMenuParam"],
                            defs.get("NightBossMenuParam"))
    for row in boss_table.rows:
        if row.values.get("sortId") == DEEP_MODE_SORT:
            mode_text = (menu_text.get(row.values.get("descriptionId", -1)) or "").strip()
            break

    return {
        "description": mode_text,
        # The game's own explanation of what Depth actually is, including the
        # rating bands. Carried verbatim so the tab can say what "rating"
        # means without the app paraphrasing it.
        "rating_text": rating_text,
        "sigil_name": sigil_name,
        "sigil_info": sigil_info,
        "sigil_icon": sigil_icon,
        "depth_count": DEPTH_COUNT,
        "rewards": rewards,
        "scaling": list(profiles.values()),
        "scaling_unresolved": unresolved,
        "mutations": mutations,
        "kinds": kinds_out,
        "depth_control": control,
        "field_labels": SCALING_FIELDS,
    }


# The demon's offerings are one contiguous, self-contained run of CL_MenuText
# ids, every line beginning "A demon ...". Nothing in the params groups them,
# so the block is the grouping, and it is checked rather than assumed: a line
# that does not start that way ends the run instead of being carried in.
DEMON_OFFER_LO, DEMON_OFFER_HI = 337931, 337939
DEMON_EVENT_LOG_ID = 11130

# CL_MenuText keeps two different kinds of line apart by id block, and the
# distinction matters here: 337900 upwards is the in-expedition banner block
# ("A meteorite has fallen"), while 146xxx is the session log ("First Day:
# Noontide", "Defeated by ..."). Both are announcement-shaped in
# UserDispLogParam, so without this bound the day cycle and the death log come
# through as world events.
BANNER_BLOCK_LO = 337900


# PermanentBuffParam rows in this band are exactly the world-event rewards.
# What identifies the set is not the range being picked by eye: the row id is
# also its PermanentBuffName id, and every row in the band resolves to one of
# the seven buffs the events are known to hand out, while no row outside it
# does. Checked by smoke_reference_tabs.py.
EVENT_BUFF_LO, EVENT_BUFF_HI = 8970000, 8979999


# Rate fields are multipliers: 1.02 is +2%. Damage *cut* rates run the other
# way round in meaning -- higher means more damage taken, not less -- which is
# the same direction trap section 6c records for NpcParam.
_ATTACK_RATES = ("physicsAttackRate", "magicAttackRate", "fireAttackRate",
                 "thunderAttackRate", "darkAttackRate")
_CUT_RATES = ("slashDamageCutRate", "blowDamageCutRate", "thrustDamageCutRate",
              "neutralDamageCutRate", "magicDamageCutRate", "fireDamageCutRate",
              "thunderDamageCutRate", "darkDamageCutRate")


def _pct(value: float) -> str:
    return f"{(value - 1.0) * 100:+.0f}%"


def _states_allies(caption: str) -> bool | None:
    """True only when the game's own caption says the effect reaches allies.

    None -- not False -- when it says nothing, because silence is not a claim
    that the buff is personal. The distinction matters: a False here would put
    "only you" on screen for six of the seven buffs on no evidence at all.
    """
    lowered = caption.lower()
    if "allies" in lowered or "nearby all" in lowered or " team" in lowered:
        return True
    return None


def _buff_lines(values: dict) -> list[str]:
    """Plain wording for the fields that carry a buff's actual magnitude.

    Only fields whose meaning is established elsewhere in this project are
    worded; anything else is left to the raw dump in the probe scripts rather
    than being given a confident label it has not earned.
    """
    lines = []

    rates = {values.get(f) for f in _ATTACK_RATES if values.get(f) not in (None, 1.0)}
    if len(rates) == 1:
        lines.append(f"{_pct(rates.pop())} attack power, all damage types")

    cuts = {values.get(f) for f in _CUT_RATES if values.get(f) not in (None, 1.0)}
    if len(cuts) == 1:
        # A cut rate above 1.0 is damage taken going up.
        lines.append(f"{_pct(cuts.pop())} damage taken, all damage types")

    simple = [
        ("maxHpRate", "maximum HP"),
        ("maxMpRate", "maximum FP"),
        ("maxStaminaRate", "maximum stamina"),
        ("ultimateArtGauge", "Ultimate Art charge rate"),
    ]
    for field, label in simple:
        value = values.get(field)
        if value not in (None, 1.0):
            lines.append(f"{_pct(value)} {label}")

    if values.get("soul"):
        lines.append(f"{values['soul']:,} runes")
    if values.get("changeStaminaPoint"):
        # Negative is a restore on these rows -- the cost is what is stored.
        lines.append(f"restores {abs(values['changeStaminaPoint'])} stamina")
    if values.get("staminaRecoverChangeSpeed"):
        lines.append(
            f"stamina recovery speed {values['staminaRecoverChangeSpeed']:+}")
    if values.get("disableDisease"):
        lines.append("immune to Scarlet Rot")
    if values.get("stateInfo") == CONCEALED_STATE:
        lines.append("invulnerable")
    return lines


# ---- What a flask does once an effect has taken it over -------------------
# Three effects set a state and nothing else: "Flask Also Heals Allies"
# (2344), "Gradual Restoration by Flask" (2015) and the event buff "Unifying
# Fate" (2262). Row 7010211 waits on all three and zeroes the flask's plain
# heal; what the flask does instead is in the same id block, and nothing in a
# param says which row answers which state. They are told apart by what they
# hold, which is unambiguous: one pair restores FP and one effect says FP; one
# pair is followed by a timed HP rate and one effect says "slowly"; the third
# is what is left. Each has an ally copy that a bullet lays (7010221 through
# 900102221, and so on). A plain flask is `changeHpEstusFlaskRate` -60 on
# rows 501000..501012, so these are on the same scale.
FLASK_ROWS = {
    2344: (7010220, 7010221),             # 50 to the drinker, 30 to allies
    2015: (7010230, 7010231),             # 10 at once, then a rate for 8 s
    2262: (7010250, 7010260),             # FP: 30 to the drinker, 15 to allies
}
FLASK_FIELDS = ("changeHpEstusFlaskRate", "changeMpEstusFlaskRate",
                "changeHpRate")


def flask_rows(state: int, values_of) -> list[dict]:
    """The rows of `FLASK_ROWS` for this state, in `triggered`'s shape."""
    found = []
    for sp_id in FLASK_ROWS.get(state, ()):
        values = values_of.get(sp_id) or {}
        numbers = {field: values[field] for field in FLASK_FIELDS
                   if values.get(field)}
        if not numbers:
            continue
        if values.get("effectEndurance", 0) >= 1:
            numbers["effectEndurance"] = values["effectEndurance"]
        found.append({"sp_id": sp_id,
                      "sp_category": values.get("spCategory"),
                      "modifiers": numbers})
    return found


# "Demon's Plating" -- "Enhances attack power depending on runes in
# possession" -- has no number on any SpEffect row: its row 8970030 is state
# 2118 and nothing else. The number is a curve, and which one is in the code,
# not in a param (nightreign.exe 0x1406c3299, data_version 10350000): where
# the attacker carries state 0x846 the runes held go through CalcCorrectGraph
# row 60 (the lookup at 0x140e87b10 with id 0x3c, the curve at 0x1406d2670)
# and the result multiplies the attack.
RUNES_HELD_STATE = 2118
RUNES_HELD_CURVE = 60


def _runes_held_lines(members: dict, defs: dict) -> list[str]:
    """The attack multiplier of `RUNES_HELD_CURVE`, point by point."""
    graph = param.read(members["CalcCorrectGraph"],
                       defs.get("CalcCorrectGraph"))
    row = next((r for r in graph.rows if r.id == RUNES_HELD_CURVE), None)
    if row is None:
        return []
    points = [(row.values[f"stageMaxVal{i}"], row.values[f"stageMaxGrowVal{i}"])
              for i in range(5)]
    steps = [f"×{rate:.3g} at {runes:,.0f}" for runes, rate in points
             if runes > 0]
    if not steps:
        return []
    return ["attack power by runes held: " + ", ".join(steps)
            + ", rising evenly in between"]


def _flask_lines(state: Any, sp_rows: dict) -> list[str]:
    """`flask_rows` in the wording of a buff line: the FP a flask restores."""
    rates = [abs(row["modifiers"]["changeMpEstusFlaskRate"])
             for row in flask_rows(state or 0, sp_rows)
             if row["modifiers"].get("changeMpEstusFlaskRate")]
    if not rates:
        return []
    line = f"a flask also restores FP at rate {rates[0]:g}"
    if len(rates) > 1:
        line += f", {rates[1]:g} for an ally it reaches"
    return [line + " (a plain flask restores HP at rate 60)"]


def _event_buffs(members: dict, defs: dict,
                 text: dict[str, dict[int, str]]) -> list[dict]:
    """The buffs the world events pay out, with who they land on.

    Everything here is read, not reported. `PermanentBuffParam.spEffectId`
    points into `SpEffectParam`, and those rows answer the questions a player
    actually asks:

    - **Who gets it — only where the game says so.** An earlier revision read
      this off `effectTargetFriend`, and that was wrong: those `effectTarget*`
      fields are *eligibility* filters, and 1 is the modal value across the
      whole table, so "team-wide" was being reported from a default rather
      than from evidence. They say what an effect is allowed to land on, not
      how many people it is handed to. The only trustworthy statement of
      scope is the game's own caption, so scope is now taken from that text
      and left unstated when the text does not mention allies.
    - **How long it lasts.** `effectEndurance` of -1 is permanent -- no timer,
      nothing to use up. Every one of these buffs is -1, so none of them is
      consumed and none is on a cooldown at this level. Where a buff has an
      internal proc, that lives on a *sub*-effect with its own short duration,
      which is why those are carried too.
    - **Whether it stacks.** `accumuOverVal` / `accumuOverFireId` is a
      threshold-and-fire pair, the shape of "charges up, then triggers".
    """
    name = text.get("PermanentBuffName", {})
    info = text.get("PermanentBuffInfo", {})
    caption = text.get("PermanentBuffCaption", {})
    sp_name = text.get("SpEffectName", {})

    buffs = param.read(members["PermanentBuffParam"],
                       defs.get("PermanentBuffParam"))
    sp = param.read(members["SpEffectParam"], defs.get("SpEffectParam"))
    sp_rows = {r.id: r.values for r in sp.rows}

    out = []
    for row in buffs.rows:
        if not (EVENT_BUFF_LO <= row.id <= EVENT_BUFF_HI):
            continue
        root = sp_rows.get(row.values["spEffectId"], {})

        # Sub-effects sit in the same ten-id block as their parent. They are
        # what carries the proc timing, so the "used up or on cooldown"
        # question is answered from them rather than from the marker row.
        parts = []
        for offset in range(0, 10):
            sub_id = row.values["spEffectId"] + offset
            sub = sp_rows.get(sub_id)
            if sub is None or sub_id == row.values["spEffectId"]:
                continue
            parts.append({
                "sp_id": sub_id,
                "name": (sp_name.get(sub.get("permanentBuffTextId", -1))
                         or sp_name.get(sub_id) or "").strip(),
                "duration": sub.get("effectEndurance"),
                "fires_at": sub.get("accumuOverVal"),
                "lines": _buff_lines(sub),
            })

        out.append({
            "id": row.id,
            "name": (name.get(row.id) or "").strip(),
            "info": (info.get(row.id) or "").strip(),
            "caption": (caption.get(row.id) or "").strip(),
            "sp_id": row.values["spEffectId"],
            "icon": _icon(root.get("iconId")),
            # -1 means no timer at all: it lasts the rest of the expedition.
            "duration": root.get("effectEndurance"),
            # None means the files do not say. See the docstring: the
            # effectTarget* flags cannot answer this.
            "shares_with_allies": _states_allies(info.get(row.id) or ""),
            "fires_at": root.get("accumuOverVal") or None,
            "lines": _buff_lines(root) + (
                _runes_held_lines(members, defs)
                if root.get("stateInfo") == RUNES_HELD_STATE else []
            ) + _flask_lines(root.get("stateInfo"), sp_rows),
            # A buff whose magnitude lives on a *separate* row applied on a
            # trigger, not on the marker itself. Traces of Grace-Given Lord is
            # the case that matters: graceSpEffectId is what a new Site of
            # Grace applies, and that row is where the +2% actually is.
            "per_trigger": _buff_lines(
                sp_rows.get(row.values.get("graceSpEffectId"), {})),
            # How far the game itself counts the stacks. A buff that stacks
            # ships one named tier per step -- "Traces of Grace-Given Lord
            # +1" through "+10" -- so the highest "+N" the game names is the
            # display's own ceiling. Read from the strings, not asserted.
            "stacks_to": _named_stack_cap(sp_name,
                                          (name.get(row.id) or "").strip()),
            "parts": parts,
        })
    out.sort(key=lambda b: b["id"])
    return out


def _named_stack_cap(sp_name: dict[int, str], buff_name: str) -> int | None:
    """The highest "+N" tier the game names for this buff, if any."""
    if not buff_name:
        return None
    cap = None
    prefix = buff_name + " +"
    for label in sp_name.values():
        if label and label.startswith(prefix):
            tail = label[len(prefix):].strip()
            if tail.isdigit():
                cap = max(cap or 0, int(tail))
    return cap


# The band that holds the expedition-wide states: the Shifting Earth favours,
# and the debuffs a failed event leaves behind. They are named the same way
# the buffs are -- through SpEffectParam.permanentBuffTextId -- but several
# have no PermanentBuffParam row at all, so they are only reachable from the
# SpEffect side. "Unhealed Wound Carved by the Night" is one of those, which
# is why an earlier round missed it entirely.
STATE_LO, STATE_HI = 6999000, 6999999


def _event_states(members: dict, defs: dict,
                  text: dict[str, dict[int, str]]) -> list[dict]:
    """Shifting Earth favours and the debuffs events leave behind."""
    buff_name = text.get("PermanentBuffName", {})
    sp_name = text.get("SpEffectName", {})

    sp = param.read(members["SpEffectParam"], defs.get("SpEffectParam"))
    out = []
    for row in sp.rows:
        if not (STATE_LO <= row.id <= STATE_HI):
            continue
        text_id = row.values.get("permanentBuffTextId", -1)
        label = (buff_name.get(text_id) or sp_name.get(text_id) or "").strip()
        lines = _buff_lines(row.values)
        if not label or not lines:
            continue
        out.append({
            "sp_id": row.id,
            "name": label,
            "icon": _icon(row.values.get("iconId")),
            "duration": row.values.get("effectEndurance"),
            "lines": lines,
            "shares_with_allies": _states_allies(label),
        })
    return out


# Which map-pattern modifier is which world event. This was the blocker for
# every earlier round, and it is now settled -- by matching, not by guessing.
#
# The test: a published source gave, for nine events, the exact set of
# Nightlords each can appear under. Those sets were compared against the boss
# sets the modifiers actually draw for in LotResultMapPatternFlag. **Eight of
# the nine matched a modifier exactly**, each a distinct 3- or 4-element
# subset of ten bosses. Eight independent exact subset matches do not happen
# by chance, so the pairing is real in both directions: the published pools
# are confirmed by the files, and the files' anonymous modifier ids are named
# by the pools.
#
# The ninth assignment was wrong for two releases and is now corrected.
# 11180 (Flame of Frenzy) was matched to modifier 230 as "one short,
# undersampled". A per-pattern community dump (thefifthmatt's map-pattern
# sheet, whose global pattern numbers align 1:1 with patternId -- verified on
# all nine of Adel's Fell Omen patterns) splits the two candidates cleanly:
# every pattern it marks "Frenzy Tower" carries modifier **140**, and every
# pattern it marks "Difficult Sorcerer's Rise" carries modifier **230**, six
# of six each. So 230 is the hard Sorcerer's Rise (no banner, not an
# announced event) and the Flame of Frenzy is 140 -- whose boss set includes
# Straghess, so there was never an undersampling gap, just the wrong row.
#
# The three DLC events are named through their reward buffs rather than
# through published pools. LotBaseMapPatternFlag gives the seven invasion
# modifiers one contiguous eventFlag band, and common.emevd's initializer
# pairs each flag with the SpEffect of the buff the event awards:
#
#   flag 8075 = mod   604 -> sp 8970001 Traces of Grace-Given Lord (Fell Omen)
#   flag 8076 = mod   603 -> sp 8970020 Unifying Fate            (Bubbles)
#   flag 8077 = mod   600 -> sp 8970050 Beast's Hunt             (Fire-Summoning)
#   flag 8078 = mod   601 -> sp 8970010 Integration of Intelligence (Locusts)
#   flag 8079 = mod   602 -> sp 8970030 Demon's Plating          (Demon)
#   flag 8080 = mod 10000 -> sp 8970040 Cold Mirage              (Blizzard)
#   flag 8081 = mod 10001 -> sp 8970060 Power to Balance the World (Judgment)
#
# The four base rows are the controls: each reaches exactly the reward its
# event is known to give, so the bridge is trusted for the three DLC rows.
# Which buff belongs to which DLC event is community-reported (Fextralife
# names all three); everything else in the chain is the files' own.
# The same initializer wires penalty row 6999400 (Unhealed Wound) to flags
# 8075 AND 8076 -- so losing the bubble fight carries the same wound as
# losing to the Fell Omen, which had only ever been a community claim.
#
# Every row was compared, not a sample of them.
EVENT_MODIFIER = {
    11110: 604,     # Fell Omen             Adel, Gnoster, Heolstor, Straghess
    11120: 603,     # Giant Bubbles         Gnoster, Caligo, Heolstor, Straghess
    11130: 602,     # Demon / Libra         Fulghor, Caligo, Heolstor, Straghess
    11140: 601,     # Plague of Locusts     Maris, Libra, Heolstor, Straghess
    11150: 120,     # Additional Night Boss Adel, Fulghor, Harmonia, Straghess
    11160: 200,     # Meteor Strike         Gladius, Adel, Caligo, Harmonia
    11170: 180,     # Hordes of the Night   Gladius, Maris, Fulghor, Harmonia
    11180: 140,     # Flame of Frenzy       Gnoster, Libra, Harmonia, Straghess
                    #                       (+ Gladius, DLC block only)
    110000: 600,    # Fire-Summoning Beasts everyone but Gladius and Maris
    110050: 10001,  # Judgment / Balancers  everyone but Adel, Gnoster, Harmonia
    110200: 10000,  # Blizzard              everyone but Libra, Fulghor, Caligo
}
UNDERSAMPLED: set[int] = set()

# The DLC added ten map patterns per base Nightlord, in their own id block --
# patternId 1000 + 10*boss .. 1009 + 10*boss. The three DLC events sit only
# in that block on the eight base Nightlords, which the tab states from the
# ids alone; players report the block as Deep of Night, and that label stays
# in the community layer.
DLC_PATTERN_LO, DLC_PATTERN_HI = 1000, 1079


def _gating(members: dict, defs: dict,
            text: dict[str, dict[int, str]]) -> dict[str, Any]:
    """Which Nightlords each event appears under, and how much of the pool.

    **`targetBoss` is the `NightBossMenuParam` row id, not its sort order.**
    An earlier revision used the sort order, which put Heolstor, Harmonia and
    Straghess in each other's slots and silently shifted three bosses in every
    pool. The eight exact set matches above only appear once the row id is
    used, which is itself the strongest evidence that the row id is right.

    The percentage is the share of that Nightlord's own map patterns carrying
    the modifier. Exact as a share. Whether the game draws patterns uniformly
    is **not** established -- `MapPatternSet` carries per-pattern weights --
    so this is the composition of the pool, which is the honest form of the
    answer, and not a spin probability.
    """
    menu_text = text.get("CL_MenuText", {})
    boss_table = param.read(members["NightBossMenuParam"],
                            defs.get("NightBossMenuParam"))
    names = {row.id: (menu_text.get(row.values.get("bossNameId", -1)) or "?").strip()
             for row in boss_table.rows if row.id <= 9}

    table = param.read(members["LotResultMapPatternFlag"],
                       defs.get("LotResultMapPatternFlag"))
    rows = [r.values for r in table.rows if not r.values["unknown_0"]]

    pattern_boss: dict[int, int] = {}
    pattern_mods: dict[int, set[int]] = {}
    for values in rows:
        pattern_boss[values["patternId"]] = values["targetBoss"]
        if values["modifier"]:
            pattern_mods.setdefault(values["patternId"], set()).add(
                values["modifier"])

    totals: dict[int, int] = {}
    for boss in pattern_boss.values():
        totals[boss] = totals.get(boss, 0) + 1

    out: dict[str, Any] = {}
    for log_id, modifier in EVENT_MODIFIER.items():
        per: dict[int, int] = {}
        per_dlc: dict[int, int] = {}
        # Modifiers 800 and 801 mark the day the event fires. Named the same
        # way 140/230 were: in the per-pattern community dump every pattern
        # with a "Day 1" event carries 800 (52 of 52) and every "Day 2"
        # pattern carries 801 (57 of 57), with no exceptions either way.
        day1 = day2 = 0
        for pattern, mods in pattern_mods.items():
            if modifier in mods:
                boss = pattern_boss[pattern]
                per[boss] = per.get(boss, 0) + 1
                if DLC_PATTERN_LO <= pattern <= DLC_PATTERN_HI:
                    per_dlc[boss] = per_dlc.get(boss, 0) + 1
                if 800 in mods:
                    day1 += 1
                if 801 in mods:
                    day2 += 1
        out[str(log_id)] = {
            "modifier": modifier,
            "undersampled": modifier in UNDERSAMPLED,
            "day1_patterns": day1,
            "day2_patterns": day2,
            "bosses": [
                {
                    "name": names.get(boss, str(boss)),
                    "patterns": count,
                    "of": totals[boss],
                    "share": round(100 * count / totals[boss], 1),
                    # How many of those sit in the DLC-added pattern block.
                    # Only meaningful for the eight base Nightlords; Harmonia
                    # and Straghess have no such block.
                    "dlc_patterns": per_dlc.get(boss, 0),
                }
                for boss, count in sorted(per.items(), key=lambda kv: -kv[1])
            ],
        }
    return out


# Item lot categories, derived rather than assumed: each number's ids were
# tested against every name table and every param's row ids, and only these
# reached better than chance. Category 3 (115 references) resolves to nothing
# and is carried raw.
LOT_GOODS, LOT_WEAPON, LOT_ACCESSORY = 1, 2, 4
LOT_RELIC = 5              # -> EquipParamAntique. See below
LOT_CUSTOM_WEAPON = 6      # -> EquipParamCustomWeapon.targetWeaponId
LOT_TABLE = 7              # -> ItemTableParam, and it nests inside itself
MAX_TABLE_DEPTH = 4

# Category 5 was missing from the list above until 2026-08-16, for a good
# reason: it never appears in `ItemLotParam_enemy`, which is the only lot
# table this project used to read. It shows up in `ItemLotParam_map`, where
# **all 27 distinct category-5 ids are rows in `EquipParamAntique`** -- 100%,
# against 81% for the nearest rival param -- and the names that come out are
# real and coherent rather than merely plausible. So category 5 is a relic.


def _depth_reward_items(members: dict, defs: dict,
                        text: dict[str, dict[int, str]]) -> dict[int, list]:
    """Which relics each Deep of Night depth can hand out.

    `SessionRewardByModeRankParam.itemLotId_1..4` -> `ItemLotParam_map` ->
    category 5 -> `EquipParamAntique`. Two things had kept this unread: the
    param shipped no def until 2026-08-16, and the lots are in the *map*
    table rather than the *enemy* one every earlier pass searched.

    Names are deduplicated on purpose. A reward lot points at several ids
    that share a name and differ in their rolled effects (1007001 / 1007011 /
    1007021 are all "Polished Burning Scene"), so listing each id would show
    the same relic three times and say nothing.
    """
    reward = param.read(members["SessionRewardByModeRankParam"],
                        defs.get("SessionRewardByModeRankParam"))
    lots = param.read(members["ItemLotParam_map"], defs.get("ItemLotParam"))
    lot_rows = {row.id: row.values for row in lots.rows}
    if not lot_rows:
        return {}
    fields = list(next(iter(lot_rows.values())))
    id_fields = [f for f in fields if f.startswith("lotItemId")]
    cat_fields = [f for f in fields if f.startswith("lotItemCategory")]

    antique = param.read(members["EquipParamAntique"],
                         defs.get("EquipParamAntique"))
    names = text.get("AntiqueName", {})
    relic_name = {}
    for row in antique.rows:
        label = (names.get(row.values.get("nameId", -1))
                 or names.get(row.id) or "").strip()
        if label:
            relic_name[row.id] = label

    tables = param.read(members["ItemTableParam"], defs.get("ItemTableParam"))
    groups: dict[int, list] = {}
    for row in tables.rows:
        groups.setdefault(row.id, []).append(row.values)

    def collect(category: int, item_id: int, found: set, depth: int) -> None:
        if category == LOT_TABLE:
            if depth > MAX_TABLE_DEPTH:
                return
            for entry in groups.get(item_id, []):
                collect(entry["itemCategory"], entry["itemId"], found,
                        depth + 1)
        elif category == LOT_RELIC:
            label = relic_name.get(item_id)
            if label:
                found.add(label)

    out: dict[int, list] = {}
    for row in reward.rows:
        found: set[str] = set()
        for slot in range(1, 5):
            lot_id = row.values.get(f"itemLotId_{slot}", 0)
            values = lot_rows.get(lot_id)
            if not values:
                continue
            for id_field, cat_field in zip(id_fields, cat_fields):
                item_id = values[id_field]
                if item_id:
                    collect(values[cat_field], item_id, found, 0)
        if found:
            out[row.id] = sorted(found)
    return out


def _event_drops(members: dict, defs: dict,
                 text: dict[str, dict[int, str]]) -> dict[str, list]:
    """What each creature actually drops, with weights, as percentages.

    Three separate mistakes kept this unreadable through several rounds, and
    all three have to be undone at once for anything to come out:

    1. `ItemLotParam_enemy` ships no def -- but Paramdex's generic
       `ItemLotParam.xml` is 216 bytes against a 224-byte row, and a *short*
       def is a safe prefix (section 4). Only a longer one is unusable.
    2. `lotItemCategory` **7 is not an item**. It is a pointer into
       `ItemTableParam`, which does ship a def. Two thirds of all references
       are category 7, and tables nest inside tables, so a correct read still
       looks like noise until the recursion is followed.
    3. Event bosses hang their drops off **`rewardItemLot_2`**, not
       `itemLotId_enemy`, which is -1 on nearly all of them.

    Two independent checks say the read is right rather than merely plausible.
    The Mausoleum Knight drops the Eclipse Crest Greatshield -- the shield
    whose own caption calls the eclipsed sun the symbol of the Wandering
    Mausoleum -- and the Fell Omen's table is 20 entries that **all twenty**
    resolve to Dormant Powers. A misaligned read produces neither.
    """
    def fmg(name: str) -> dict[int, str]:
        return text.get(name, {})

    goods, weapons = fmg("GoodsName"), fmg("WeaponName")
    accessories, buffs = fmg("AccessoryName"), fmg("PermanentBuffName")

    custom = param.read(members["EquipParamCustomWeapon"],
                        defs.get("EquipParamCustomWeapon"))
    custom_target = {r.id: r.values.get("targetWeaponId") for r in custom.rows}

    lots = param.read(members["ItemLotParam_enemy"], defs.get("ItemLotParam"))
    lot_rows = {r.id: r.values for r in lots.rows}
    fields = list(lots.rows[0].values) if lots.rows else []
    id_fields = [f for f in fields if f.startswith("lotItemId")]
    cat_fields = [f for f in fields if f.startswith("lotItemCategory")]

    tables = param.read(members["ItemTableParam"], defs.get("ItemTableParam"))
    groups: dict[int, list] = {}
    for row in tables.rows:
        groups.setdefault(row.id, []).append(row.values)

    def name_of(category: int, item_id: int) -> tuple[str, str]:
        if category == LOT_GOODS:
            # Dormant Powers appear here as a PermanentBuffName id -- usually
            # plus one, but six of the Fell Omen's twenty use the id exactly.
            # Both forms are tried; assuming only the +1 form silently
            # demoted those six to unnamed goods.
            buff = buffs.get(item_id - 1) or buffs.get(item_id)
            if buff:
                return buff.strip(), "power"
            return (goods.get(item_id) or f"goods {item_id}").strip(), "item"
        if category == LOT_WEAPON:
            return (weapons.get(item_id) or f"weapon {item_id}").strip(), "weapon"
        if category == LOT_ACCESSORY:
            return (accessories.get(item_id)
                    or f"talisman {item_id}").strip(), "talisman"
        if category == LOT_CUSTOM_WEAPON:
            target = custom_target.get(item_id)
            label = weapons.get(target) if target else None
            return (label or f"weapon {item_id}").strip(), "weapon"
        return f"[{category}:{item_id}]", "unknown"

    def symbol_rows(name: str) -> dict[int, Any]:
        return {r.id: r.values.get("iconId")
                for r in param.read(members[name], defs.get(name)).rows}

    goods_symbols = symbol_rows("EquipParamGoods")
    weapon_symbols = symbol_rows("EquipParamWeapon")
    talisman_symbols = symbol_rows("EquipParamAccessory")
    power_symbols = symbol_rows("PermanentBuffParam")

    def symbol_of(category: int, item_id: int) -> int | None:
        """The drop's symbol, by the same two id forms `name_of` tries."""
        if category == LOT_GOODS:
            if (item_id - 1 in buffs and buffs[item_id - 1]) or buffs.get(item_id):
                return _icon(power_symbols.get(
                    item_id - 1 if buffs.get(item_id - 1) else item_id))
            return _icon(goods_symbols.get(item_id))
        if category == LOT_WEAPON:
            return _icon(weapon_symbols.get(item_id))
        if category == LOT_ACCESSORY:
            return _icon(talisman_symbols.get(item_id))
        if category == LOT_CUSTOM_WEAPON:
            return _icon(weapon_symbols.get(custom_target.get(item_id)))
        return None

    symbols: dict[tuple[str, str], int | None] = {}

    def named(category: int, item_id: int) -> tuple[str, str]:
        """`name_of`, noting which symbol that name is drawn with."""
        key = name_of(category, item_id)
        symbols.setdefault(key, symbol_of(category, item_id))
        return key

    def walk(table_id: int, weight: float, depth: int,
             out: dict[tuple[str, str], float]) -> None:
        entries = groups.get(table_id)
        if not entries or depth > MAX_TABLE_DEPTH:
            return
        total = sum(e["chanceWeight"] for e in entries)
        if not total:
            return
        for entry in entries:
            share = weight * entry["chanceWeight"] / total
            if not share:
                continue
            category, item_id = entry["itemCategory"], entry["itemId"]
            if category == LOT_TABLE:
                walk(item_id, share, depth + 1, out)
            else:
                key = named(category, item_id)
                out[key] = out.get(key, 0.0) + share

    npc = param.read(members["NpcParam"], defs.get("NpcParam"))
    by_chr: dict[int, list] = {}
    for row in npc.rows:
        by_chr.setdefault(row.id // 10000, []).append(row)

    out: dict[str, list] = {}
    for chr_id, rows in by_chr.items():
        lot_ids: set[int] = set()
        for row in rows:
            for field in ("rewardItemLot_2", "rewardItemLot_1",
                          "itemLotId_enemy"):
                value = row.values.get(field)
                if value and value != -1:
                    lot_ids.add(value)

        collected: dict[tuple[str, str], float] = {}
        for lot_id in lot_ids:
            lot = lot_rows.get(lot_id)
            if lot is None:
                continue
            for id_field, cat_field in zip(id_fields, cat_fields):
                item_id, category = lot[id_field], lot[cat_field]
                if not item_id:
                    continue
                if category == LOT_TABLE:
                    walk(item_id, 1.0, 0, collected)
                else:
                    key = named(category, item_id)
                    collected[key] = collected.get(key, 0.0) + 1.0

        if not collected:
            continue
        total = sum(collected.values())
        # Two decimals, because the biggest tables run to 300 entries and a
        # single decimal rounds the rarest of them to a flat 0%, which reads
        # as "cannot drop" rather than "rare". Anything still below 0.005% is
        # dropped and counted instead of being shown as zero.
        entries = []
        omitted = 0
        for (name, kind), value in collected.items():
            share = round(100 * value / total, 2)
            if share <= 0:
                omitted += 1
                continue
            entries.append({"name": name, "kind": kind, "share": share,
                            "icon": symbols.get((name, kind))})
        entries.sort(key=lambda e: (-e["share"], e["name"]))
        if omitted:
            entries.append({"name": f"{omitted} entries rarer than 0.005%",
                            "kind": "omitted", "share": 0.0})
        out[str(chr_id)] = entries
    return out


def _rune_scaling(members: dict, defs: dict) -> list[str]:
    """Why a base `getSoul` is smaller than what a run actually pays.

    Read, not described, so the figures cannot drift. Two multipliers are
    named in the params and both are extracted here; a third factor -- how a
    kill's runes are split or shared across a party -- is not in
    regulation.bin at all, so it is not claimed.
    """
    lines = []

    clear = param.read(members["ClearCountCorrectParam"],
                       defs.get("ClearCountCorrectParam"))
    # Ordered by the row id, which is the step the figure belongs to. Sorting
    # by the figure instead threw that away, and the sentence then offered
    # seven multipliers with nothing saying which was which -- a ladder a
    # reader cannot climb (QA-148). The rows carrying no rate at all are left
    # out; row 0 is one of them.
    rungs = [(row.id, row.values["SoulRate"]) for row in clear.rows
             if row.values.get("SoulRate")]
    rungs.sort()
    if rungs:
        # What the step number is *counted in* is not in the files: the rows
        # are numbered and nothing says how many expeditions reach each one.
        # Said out loud rather than guessed at, which is A7 and is also why
        # the sentence no longer carries the param name it was quoting. The
        # name was being stripped again in the tab, leaving `Expeditions
        # completed: runs ×1 …` -- a repair at the wrong end (AK-104).
        lines.append(
            "Expedition progress moves it up a "
            f"{len(rungs)}-step ladder: step {rungs[0][0]} ×{rungs[0][1]:g}, "
            "then "
            + ", ".join(f"×{rate:g}" for _step, rate in rungs[1:])
            + f" at step {rungs[-1][0]}. The game's files number the steps "
            "and do not say how many expeditions reach each one.")

    # Deep of Night is the other thing that moves, but its multiplier table
    # ships no paramdef and is read by inspection in _deep_of_night, so it is
    # pointed at rather than restated here -- a second, independently parsed
    # copy of those numbers is exactly how two figures drift apart.
    lines.append(
        "Deep of Night depth: the expedition reward multiplier climbs with "
        "depth. The Deep of Night tab shows that table in full. It is a "
        "session reward rather than a proven factor on a single kill, so it "
        "is not folded into the figure above.")

    lines.append(
        "Several tuned copies of the same creature exist, and which one an "
        "expedition places is decided at runtime — that is why a creature "
        "can show more than one base figure.")
    return lines


def _event_creatures(members: dict, defs: dict,
                     text: dict[str, dict[int, str]]) -> dict[str, dict]:
    """Every named character's rune value, keyed by character id.

    `getSoul` on `NpcParam` is the rune drop, and `NpcParam` ships a def, so
    this half of "what does it pay" was readable all along -- the earlier
    round wrote rewards off as underivable because it only looked at the item
    lots. Runes are not an item lot.

    **These are base values.** What actually lands is scaled at runtime by
    Deep of Night and the multiplayer bonus tables, so the figure is a
    baseline to compare events against, not a number to expect on screen.
    """
    names = text.get("NpcName", {})

    npc = param.read(members["NpcParam"], defs.get("NpcParam"))
    by_chr: dict[int, list] = {}
    for row in npc.rows:
        by_chr.setdefault(row.id // 10000, []).append(row)

    out: dict[str, dict] = {}
    for name_id, label in names.items():
        text_label = (label or "").strip()
        if not text_label or name_id < 900000000:
            continue
        chr_id = (name_id // 1000) % 10000
        rows = by_chr.get(chr_id)
        if not rows:
            continue
        runes = sorted({r.values["getSoul"] for r in rows
                        if r.values.get("getSoul")})
        if not runes:
            continue
        entry = out.setdefault(str(chr_id), {
            "chr": chr_id, "names": [], "runes": runes,
            "hp": sorted({r.values["hp"] for r in rows if r.values.get("hp")}),
        })
        if text_label not in entry["names"]:
            entry["names"].append(text_label)
    return out


def _world_events(members: dict, defs: dict,
                  text: dict[str, dict[int, str]]) -> dict[str, Any]:
    """The Limveld world events, from the banners the game puts on screen.

    The chain is two steps, and the middle one is the part that is not
    obvious:

        EMEVD  ->  UserDispLogParam row  ->  CL_MenuText banner

    The banner ids themselves appear **nowhere** in any event script. All 193
    were searched, including the ones missing from every published dictionary,
    and 338080 ("A demon casts its curse") occurs in none of them, as raw
    bytes or as instruction arguments. What the scripts reference is a
    display-log row, and that row carries the text id. So UserDispLogParam is
    the roster, not the scripts.

    Grouping is structural rather than chosen. The rows sit in decades: an
    announcement at `...0` and its outcomes above it. An announcement is
    recognisable on its own shape -- it fills only `textId_2` and leaves
    `textId_1` empty, which no outcome row does. So a decade whose anchor has
    an empty `textId_1` is a timed world event, and one whose anchor fills
    both is a one-shot notice ("Rise's contraption unlocked"). That rule alone
    separates the two, which is why it is applied here in place of a
    hand-written list of which row is which.

    **Deliberately absent: occurrence chance, rewards, penalties, and which
    Nightlord gates which event.** None of the four is derivable today, and
    none is guessed:

    - *Chance.* The map lottery is real and readable --
      `LotResultMapPatternFlag` gives 520 patterns, each with a `targetBoss`
      and a set of `modifier` ids, and `LotBaseMapPatternFlag` gives every
      modifier a draw weight. But the modifier ids are unnamed everywhere in
      the files, so no modifier can be tied to an event, and a percentage
      would be a real number attached to the wrong thing.
    - *Rewards and penalties.* They are item lots, and `ItemLotParam_enemy`
      ships no paramdef -- the same dead end already recorded for boss drops.
    - *Nightlord gating.* `targetBoss` is recorded per map pattern, not per
      event, so it only becomes usable once the modifier ids are named.
    """
    menu = text.get("CL_MenuText", {})
    dlc = text.get("CL_MenuText::dlc", {})

    table = param.read(members["UserDispLogParam"], defs.get("UserDispLogParam"))
    rows = {r.id: r.values for r in table.rows}

    def caption(text_id: Any) -> str:
        if not isinstance(text_id, int) or text_id <= 0:
            return ""
        return (menu.get(text_id) or "").strip()

    decades: dict[int, list[int]] = {}
    for row_id in sorted(rows):
        decades.setdefault(row_id // 10 * 10, []).append(row_id)

    events = []
    for anchor, ids in sorted(decades.items()):
        if anchor not in ids:
            continue
        values = rows[anchor]
        # An announcement fills only textId_2; outcomes fill both.
        if values.get("textId_1", -1) > 0:
            continue
        banner_id = values.get("textId_2")
        announce = caption(banner_id)
        if not announce or banner_id < BANNER_BLOCK_LO:
            continue
        # Several outcomes are worded identically on more than one log row --
        # two ways of repelling a Fell Omen, two of losing the flame of
        # frenzy. Those are merged, keeping every row id, rather than shown as
        # a bullet repeated verbatim.
        outcomes: list[dict] = []
        for row_id in ids:
            if row_id == anchor:
                continue
            line = (caption(rows[row_id].get("textId_1"))
                    or caption(rows[row_id].get("textId_2")))
            if not line:
                continue
            existing = next((o for o in outcomes if o["text"] == line), None)
            if existing:
                existing["log_ids"].append(row_id)
            else:
                outcomes.append({"log_ids": [row_id], "text": line})
        events.append({
            "log_id": anchor,
            "announce": announce,
            "announce_text_id": banner_id,
            "outcomes": outcomes,
            "is_dlc": banner_id in dlc,
        })

    # The demon's offerings, carried only as far as the run actually holds.
    offers = []
    for text_id in range(DEMON_OFFER_LO, DEMON_OFFER_HI + 1):
        line = (menu.get(text_id) or "").strip()
        if not line.startswith("A demon "):
            break
        offers.append({"text_id": text_id, "text": line})
    for event in events:
        if event["log_id"] == DEMON_EVENT_LOG_ID:
            event["variants"] = offers

    return {
        "events": events,
        "buffs": _event_buffs(members, defs, text),
        "states": _event_states(members, defs, text),
        "creatures": _event_creatures(members, defs, text),
        "rune_scaling": _rune_scaling(members, defs),
        "drops": _event_drops(members, defs, text),
        "gating": _gating(members, defs, text),
        # The one real gap left. Chance and gating were both on this list
        # and are now resolved -- see _gating.
        "unknowns": [
            "Drop tables are read through a borrowed def and a nested "
            "ItemTableParam, so a few ids resolve only to a raw category "
            "and number. Those are shown as-is rather than guessed at.",
        ],
    }


def catalyst_scaling_rates(table: param.ParamTable) -> dict[int, float]:
    """Reinforce group -> the rate behind the game's spell scaling figure.

    **Loud rather than defaulting** (QA-099 c). `CATALYST_SCALING_FIELD` is a
    placeholder name, and a Paramdex update that gives the field its real name
    would leave `row.values.get(name, 1.0)` handing back 1.0 for every row --
    at which point all 28 catalysts would quietly show the same figure, 90,
    and nothing anywhere would say the data had stopped arriving. A field that
    is not there is therefore an error, not a default.

    Two things are checked, because either on its own can be satisfied by a
    dataset that says nothing:

    * the field exists on every row -- a renamed or dropped field fails here;
    * at least one row carries a rate other than 1.0 -- a field that exists
      and is uniformly 1.0 is a field read from the wrong offset, and it
      would pass the first check unremarked.

    **The threshold is one, not** `CATALYST_SCALING_ROWS_TODAY`. The shipped
    data holds 97 such rows, and that number is written down beside this so
    the margin can be seen; the check itself asks for one, because a patch
    that retires catalysts is a game change and not a broken extractor, and a
    guard that fails on it would be read as noise and switched off.
    """
    rates: dict[int, float] = {}
    for row in table.rows:
        if CATALYST_SCALING_FIELD not in row.values:
            raise NotWhatItClaims(
                f"ReinforceParamWeapon has no {CATALYST_SCALING_FIELD!r} "
                f"field in this paramdef, and it is the only place the spell "
                f"scaling of staves and seals is written (offset 128, the "
                f"last field of the row). It has most likely been renamed by "
                f"a Paramdex update: find the new name for offset 128 and "
                f"put it in extract.CATALYST_SCALING_FIELD. Nothing is "
                f"defaulted here -- a default would show every catalyst the "
                f"same figure and say nothing (QA-099 c).")
        rates[row.id] = float(row.values[CATALYST_SCALING_FIELD])

    moving = sum(1 for value in rates.values() if value != 1.0)
    if not moving:
        raise NotWhatItClaims(
            f"every one of the {len(rates)} ReinforceParamWeapon rows reads "
            f"{CATALYST_SCALING_FIELD!r} as 1.0, where this game data held "
            f"{CATALYST_SCALING_ROWS_TODAY} rows with another value. A field "
            f"that exists and never moves is a field read at the wrong "
            f"offset; check what {CATALYST_SCALING_FIELD!r} names in the "
            f"paramdef before trusting any catalyst figure.")
    return rates


def build(game_dir: pathlib.Path, defs_dir: pathlib.Path) -> dict[str, Any]:
    game_dir = pathlib.Path(game_dir)
    reg_path = game_dir / "regulation.bin"

    # The regulation's own BND4 version string, e.g. "10350000". Recorded so a
    # user can see which game data build the snapshot came from; the integrity
    # check itself uses the file hash, which also catches silent hotfixes.
    from . import dcx as _dcx

    regulation_blob = _dcx.decompress(regulation.decrypt(reg_path))
    data_version = regulation_blob[0x18:0x20].decode("ascii", "replace").strip("\x00")

    defs = paramdef.load_all(defs_dir)

    # The shipped AntiqueStandParam def stops 4 bytes short of the real row.
    # Those bytes hold the three extra slots a chalice exposes in Deep of Night
    # (the 4th is padding), so declare them rather than leaving them unread.
    stand_def = defs.get("AntiqueStandParam")
    if stand_def is not None and stand_def.row_size == 20:
        for i in range(3):
            stand_def.fields.append(
                paramdef.Field(f"deepSlot{i + 1}", "u8", 20 + i, 1)
            )
        stand_def.row_size = 24

    # The same treatment for SpEffectParam, whose def stops 48 bytes short of
    # the real row. Offset 1020 holds the spell a swap relic hands the player:
    # exactly ten rows differ from -1, and each one is the Magic id the
    # effect's own name states. Declared here and not in vendor/Paramdex,
    # which stays the upstream file it was vendored as.
    #
    # Loud rather than silent when the def is not the one measured against:
    # a def *longer* than the row is discarded whole by param.read, and the
    # entire effect table would then read as rows without a single field.
    sp_def = defs.get("SpEffectParam")
    if sp_def is not None and sp_def.by_name(START_MAGIC_FIELD) is None:
        if sp_def.row_size != SP_EFFECT_DEF_SIZE:
            raise NotWhatItClaims(
                f"{START_MAGIC_FIELD!r} is declared at offset "
                f"{START_MAGIC_OFFSET} rather than by name, and the "
                f"SpEffectParam paramdef describes {sp_def.row_size} bytes "
                f"per row where it was measured against "
                f"{SP_EFFECT_DEF_SIZE}. A def of another length means the "
                f"offset has not been checked: re-measure it before "
                f"trusting any swap relic's spell.")
        sp_def.fields.append(
            paramdef.Field(START_MAGIC_FIELD, "s32", START_MAGIC_OFFSET, 4)
        )
        sp_def.row_size = START_MAGIC_OFFSET + 4
    members = {
        f.basename[: -len(".param")]: f.data for f in regulation.load_params(reg_path)
    }

    def table(name: str) -> param.ParamTable:
        return param.read(members[name], defs.get(name))

    # Opened once and handed on. Finding the archives costs 9,3 s of the
    # first run (`docs/perf/baselines.md` S13), and the sub-boss pass reads
    # maps out of the same set the message files come from.
    oodle.load(game_dir)
    archives = dvdbnd.open_all(game_dir)

    text = _load_text(archives)
    antique_name = text.get("AntiqueName", {})
    antique_caption = text.get("AntiqueCaption", {})
    effect_name = text.get("AttachEffectName", {})
    effect_info = text.get("AttachEffectInfo", {})
    permanent_buff_name = text.get("PermanentBuffName", {})
    permanent_buff_info = text.get("PermanentBuffInfo", {})

    # ---- Derived stat curves ---------------------------------------------
    calc = table("CalcCorrectGraph")
    calc_by_id = {r.id: r for r in calc.rows}
    curves = {}
    for label, (curve_id, attribute) in DERIVED_CURVES.items():
        row = calc_by_id.get(curve_id)
        if row is None:
            continue
        curves[label] = {
            "curve_id": curve_id,
            "attribute": attribute,
            "x": [row.values[f"stageMaxVal{i}"] for i in range(5)],
            "y": [row.values[f"stageMaxGrowVal{i}"] for i in range(5)],
            "adj": [row.values[f"adjPt_maxGrowVal{i}"] for i in range(5)],
        }

    # Every curve, since weapon scaling references arbitrary rows.
    all_curves = {
        str(row.id): {
            "x": [row.values[f"stageMaxVal{i}"] for i in range(5)],
            "y": [row.values[f"stageMaxGrowVal{i}"] for i in range(5)],
            "adj": [row.values[f"adjPt_maxGrowVal{i}"] for i in range(5)],
        }
        for row in calc.rows
    }

    hero_param = table("HeroParam")
    hero_status = table("HeroStatusParam")
    antique = table("EquipParamAntique")
    stands = table("AntiqueStandParam")
    attach_table = table("AttachEffectTableParam")
    attach = table("AttachEffectParam")

    # The game's own filing for an effect, which nothing here read until
    # `AttachEffectFilterSubCategoryParam` gained a def (see OPEN_QUESTIONS
    # section 24). The chain is
    #   AttachEffectParam.attachFilterParamId
    #     -> AttachEffectFilterParam.attachEffectFilterCategory
    #     -> AttachEffectFilterSubCategoryParam row -> CL_MenuText
    # and it covers 568 of the 2,079 effects, so it is shown where present
    # and left out otherwise rather than filled in with a guess. The group
    # the game calls "Demerits" is its own word for curses.
    #
    # NOTE the sub-category table also holds a 32-entry weapon-type list in
    # its own UI numbering, where 53 is Colossal Sword. That is NOT `wepType`,
    # where 53 is Greatbow. Do not use it to name weapon families.
    filter_category: dict[int, str] = {}
    try:
        sub_rows = table("AttachEffectFilterSubCategoryParam").rows
        filter_rows = table("AttachEffectFilterParam").rows
        filter_text = text.get("CL_MenuText", {})
        sub_label = {r.id: (filter_text.get(r.values.get("textId", -1)) or "").strip()
                     for r in sub_rows}
        for row in filter_rows:
            label = sub_label.get(row.values.get("attachEffectFilterCategory"))
            if label:
                filter_category[row.id] = label
    except KeyError:
        # A game build without these params must not break the extract.
        filter_category = {}
    speffect = table("SpEffectParam")
    # The extended def is only usable if the row really is as long as it says.
    # Were it shorter, param.read would have dropped the def and every row
    # here would carry no fields at all -- silently, and every effect in the
    # snapshot would come out empty.
    if not speffect.rows or START_MAGIC_FIELD not in speffect.rows[0].values:
        raise NotWhatItClaims(
            f"SpEffectParam rows came back without {START_MAGIC_FIELD!r}, so "
            f"the paramdef does not fit this game's rows ({speffect.row_size} "
            f"bytes each). Every effect would read as having no fields; "
            f"re-measure the row length before extracting anything.")

    # ---- SpEffect: work out which fields an effect actually changes --------
    sp_def = defs["SpEffectParam"]
    numeric_fields = [
        f.name
        for f in sp_def.fields
        if f.type in ("f32", "s32", "u32", "s16", "u16", "u8", "s8")
        and f.count == 1
        and not f.name.startswith("unknown")
        # A row id, not a quantity: it rides on the effect as its own key
        # rather than among the numbers the build maths adds up.
        and f.name != START_MAGIC_FIELD
    ]
    sp_baseline = _modal_baseline(speffect.rows, numeric_fields)
    sp_by_id = {r.id: r for r in speffect.rows}

    # The proc chance of an "on occasion" effect, in percent. The paramdef has
    # no name for it, so the modal-baseline sweep above skips it along with
    # every other unknown_* field -- which is why these effects read as having
    # no numbers at all. It is a genuine field: nightreign.exe loads this exact
    # byte (SpEffect row offset 0x3c6) and compares it against a roll of 0..99,
    # at 0x1405043f6. Non-zero on exactly 2 of 13,472 rows, both of them
    # "Attacks Impaired on Occasion", at 3 and 5. The field was read out
    # of the executable rather than guessed at from the param alone.
    PROC_CHANCE_FIELD = "unknown_241c"

    # ---- Payload rows reached through the state an effect sets -------------
    # A large family of relic effects carries no numbers at all on its own row.
    # Its whole row is a marker: `stateInfo` and nothing else. The numbers live
    # on *separate* SpEffect rows that are gated on that same state through
    # invocationConditionsStateChange*, and no field on the effect points at
    # them -- the link exists only in the values.
    #
    # "Critical hits fill more of the Art gauge" is the clearest case: row
    # 7030800 holds only stateInfo 2011, and row 7030802 holds
    # characterSkillGauge 5.0 gated on state 2011. Its "+1" is stateInfo 2384
    # and 6.5. Matching on the state recovers both, and the 6.5 agrees with a
    # community datamine found independently, which is a useful cross-check.
    #
    # The gate field is deliberately kept in the merged modifiers: it puts the
    # effect in model.CONDITIONAL_FIELDS, so these numbers are reported under
    # Conditional & situational rather than folded into the flat totals, which
    # is correct -- they only apply when the trigger happens.
    STATE_GATES = ("invocationConditionsStateChange1",
                   "invocationConditionsStateChange2",
                   "invocationConditionsStateChange3")
    # A state shared by a great many rows is a general engine state rather than
    # one effect's payload, and merging all of it would invent nonsense.
    MAX_PAYLOAD_ROWS = 8

    by_gate_state: dict[int, list] = collections.defaultdict(list)
    for _r in speffect.rows:
        for _g in STATE_GATES:
            _v = _r.values.get(_g, 0)
            if _v:
                by_gate_state[_v].append(_r)

    # The category of each payload row that handed an effect a number, filled
    # by the two payload readers below and emptied per effect. The number is
    # on that row, so that row's category says whether two copies give it
    # twice (`STACKING_CATEGORY`): "Successful guarding fills more of the Art
    # gauge" is a marker of category 10, and the +1.0 sits on 7030602,
    # category 20, which the game holds once however many markers there are.
    payload_categories: list[Any] = []

    def state_payload(sp_id: int) -> dict[str, Any]:
        row = sp_by_id.get(sp_id)
        if row is None:
            return {}
        state = row.values.get("stateInfo", 0)
        if not state:
            return {}
        rows = by_gate_state.get(state, [])
        if not rows or len(rows) > MAX_PAYLOAD_ROWS:
            return {}
        out: dict[str, Any] = {}
        for r in rows:
            if r.id == sp_id:
                continue
            # A row that waits on several states is a switch the engine
            # shares, not this effect's payload. 7010211 is the one case:
            # it waits on "Flask Also Heals Allies", "Gradual Restoration by
            # Flask" and the event buff "Unifying Fate" alike and zeroes the
            # flask's plain heal while their own delivery runs. Merged, it
            # read "HP restored per flask -100%" on three effects, one of
            # which the game captions "increased HP restoration".
            if sum(1 for g in STATE_GATES if r.values.get(g)) > 1:
                continue
            gave = False
            for name in sp_baseline:
                value = r.values.get(name)
                if (value is not None
                        and not isinstance(value, list)
                        and value != sp_baseline[name]):
                    out.setdefault(name, value)
                    gave = gave or name in TRIGGERED_FIELDS or name == GAUGE_FIELD
            if gave:
                payload_categories.append(r.values.get("spCategory"))
        return out

    # ---- Payload rows sitting immediately after the effect's own row -------
    # The other half of the same convention. Where a state gate does not exist,
    # the numbers are on the rows at the very next ids: 7120100 "Starting
    # armament deals fire damage" is empty, and 7120101..7120104 hold
    # physicsAttackPower -30/-40/-50/-60 with fireAttackPower +33/+44/+55/+66.
    #
    # Adjacency alone would be a guess, so it is fenced three ways: the walk
    # stops at the first missing id, it stops at any row that another
    # AttachEffectParam row claims as its own passive effect (so one effect can
    # never eat another's payload), and it is capped. It is also corroborated:
    # for the effects that have both a state gate and adjacent rows -- 7030800
    # and its 7030801/7030802 -- the two mechanisms select the same rows.
    owned_sp_ids = set()
    for _r in attach.rows:
        for _i in (1, 2, 3):
            _v = _r.values.get(f"passiveSpEffectId_{_i}")
            if _v and _v > 0:
                owned_sp_ids.add(_v)

    # The same two indexes by id, for `triggered_rows`.
    sp_values = {r.id: r.values for r in speffect.rows}
    gated_ids = {state: [r.id for r in rows]
                 for state, rows in by_gate_state.items()}

    MAX_ADJACENT = 8
    NO_DURATION = -1.0   # "lasts until removed" rather than a timed window

    def adjacent_payload(sp_id: int) -> list[dict[str, Any]]:
        """Substantive fields of each consecutive row after `sp_id`."""
        tiers: list[dict[str, Any]] = []
        own_row = sp_by_id.get(sp_id)
        own_state = own_row.values.get("stateInfo", 0) if own_row else 0
        nxt = sp_id + 1
        while nxt - sp_id <= MAX_ADJACENT:
            if nxt in owned_sp_ids:
                break  # that row belongs to another effect; stop here
            row = sp_by_id.get(nxt)
            if row is None:
                # A hole is not the end of the family: "[Guardian] Slowly
                # restores nearby allies' HP" is 7012000 with its payload on
                # 7012002 and nothing at 7012001. Keep walking to the cap, but
                # never past a row another effect owns.
                nxt += 1
                continue
            # If the row declares when it applies, believe it over adjacency.
            # A row gated on a state this effect does not set is somebody
            # else's payload, and claiming it is exactly how this convention
            # would produce a confidently wrong number. Seven such rows
            # exist, found by auditing every payload link in turn.
            row_gates = [row.values.get(g) for g in STATE_GATES
                         if row.values.get(g)]
            if row_gates and own_state and own_state not in row_gates:
                nxt += 1
                continue
            values = {
                name: row.values[name]
                for name in sp_baseline
                if name in row.values
                and not isinstance(row.values[name], list)
                and row.values[name] != sp_baseline[name]
            }
            # effectEndurance has no dominant value across the table, so
            # _modal_baseline drops it and the loop above cannot see it. It is
            # the entire content of the invulnerability relics, so it is
            # compared against its own do-nothing sentinel instead.
            duration = row.values.get("effectEndurance", NO_DURATION)
            if duration not in (NO_DURATION, 0.0) and duration > 0:
                values["effectEndurance"] = duration
            if values:
                tiers.append(values)
                if (set(values) & TRIGGERED_FIELDS) or GAUGE_FIELD in values:
                    payload_categories.append(row.values.get("spCategory"))
            nxt += 1
        # A real ladder repeats the same fields with different numbers. Rows
        # that merely sit next to each other but describe different things are
        # not tiers, and calling them tiers invented "HP per tick +10 to +250"
        # out of two unrelated rows. Require an identical field set.
        if len(tiers) > 1 and len({frozenset(t) for t in tiers}) != 1:
            tiers = tiers[:1]
        return tiers

    def sp_modifiers(sp_id: int) -> dict[str, Any]:
        row = sp_by_id.get(sp_id)
        if row is None:
            return {}
        out = {
            name: row.values[name]
            for name in sp_baseline
            if name in row.values
            and not isinstance(row.values[name], list)
            and row.values[name] != sp_baseline[name]
        }
        chance = row.values.get(PROC_CHANCE_FIELD)
        if chance:
            out["procChancePercent"] = chance
        return out

    # Fields by which one SpEffect hands off to another. A great many effects
    # carry no numbers of their own and do all their work through these, which
    # is why they used to render as a blank row.
    CHAIN_FIELDS = ("replaceSpEffectId", "cycleOccurrenceSpEffectId",
                    "atkOccurrenceSpEffectId", "applyIdOnGetSoul",
                    "accumuOverFireId")

    # The one chain field that fires when your attack lands, so anything
    # reached through it is something your weapon does to the enemy.
    ATTACK_CHAIN_FIELD = "atkOccurrenceSpEffectId"

    # Flat Art/Skill gauge awards, also only reachable through the chain.
    # "Defeating enemies fills more of the Art gauge +1" carries nothing
    # itself; two hops on via applyIdOnGetSoul sits characterSkillGauge 6.5.
    # The field's baseline across all 13,472 SpEffect rows is 0.0, so these
    # are point awards rather than multipliers.
    GAUGE_FIELD = "characterSkillGauge"

    def follow_chain(sp_id: int, depth: int = 0,
                     seen: set[int] | None = None) -> dict[str, Any]:
        """Walk the SpEffect hand-off chain and collect the status it inflicts.

        Depth is capped because the chains loop back on themselves -- the
        "taking damage" curses alternate between a dormant row and an armed
        one, so a naive walk never terminates.
        """
        seen = seen if seen is not None else set()
        if sp_id in seen or sp_id <= 0 or depth > 6:
            return {}
        seen.add(sp_id)
        row = sp_by_id.get(sp_id)
        if row is None:
            return {}

        found: dict[str, Any] = {}
        for field_name, label in STATUS_POWER.items():
            value = row.values.get(field_name)
            if isinstance(value, (int, float)) and value > 0:
                found[label] = value

        gauge = row.values.get(GAUGE_FIELD)
        if isinstance(gauge, (int, float)) and gauge:
            found["Art gauge"] = gauge

        for field_name in CHAIN_FIELDS:
            nxt = row.values.get(field_name)
            if isinstance(nxt, int) and nxt > 0 and nxt not in seen:
                for label, value in follow_chain(nxt, depth + 1, seen).items():
                    found.setdefault(label, value)
        return found

    # ---- Heroes -----------------------------------------------------------
    status_by_block: dict[int, list[param.ParamRow]] = collections.defaultdict(list)
    for row in hero_status.rows:
        status_by_block[row.id // 1000].append(row)

    hero_name_fmg = text.get("CL_MenuText", {})

    # ---- Each Nightfarer's starting armament -------------------------------
    # CharaInitParam carries 1,683 rows with a heroId, most of them variants,
    # so the work is picking the canonical one. Rows 90000-90009 are exactly one
    # per Nightfarer, in heroId order, all at soulLv 1, each holding that
    # Nightfarer's signature weapon in equip_Wep_Right_1.
    #
    # Three further row families -- 50x00, 60x00 and 61x00 -- are laid out the
    # same way and name the identical weapon for all ten. The paramdef marks no
    # row as "the starting one", so agreement across four independent families
    # is the evidence.
    STARTING_ROW_BASE = 90000
    chara_init = table("CharaInitParam")
    init_by_id = {r.id: r for r in chara_init.rows}
    starting_weapon: dict[int, int] = {}
    # The left hand of the same rows. Three Nightfarers start with something
    # in it -- two shields and the seal Revenant casts from -- and the other
    # seven carry -1, an empty hand rather than an unknown armament.
    starting_weapon_left: dict[int, int] = {}
    for row in hero_param.rows:
        init = init_by_id.get(STARTING_ROW_BASE + row.id - 1)
        if init is None:
            continue
        weapon_id = init.values.get("equip_Wep_Right_1", -1)
        if isinstance(weapon_id, int) and weapon_id > 0:
            starting_weapon[row.id] = weapon_id
        left_id = init.values.get("equip_Wep_Left_1", -1)
        if isinstance(left_id, int) and left_id > 0:
            starting_weapon_left[row.id] = left_id

    heroes = []
    for row in hero_param.rows:
        # heroStatusParamId points at the first row of the block (e.g. 10000),
        # while the block itself is keyed by id // 1000.
        block = (row.values.get("heroStatusParamId") or 0) // 1000
        anchors = sorted(
            status_by_block.get(block, []), key=lambda r: r.values["totalLevel"]
        )
        if not anchors:
            continue

        # Keyed by the level as *text*, like every other mapping in this
        # dataset and like `_swap_anchors` below. JSON has no other kind of
        # key, so an int here would mean the extractor's result and the same
        # result read back out of nightreign_data.json are two different
        # objects and every consumer has to handle both (D-001).
        levels: dict[str, dict[str, int]] = {}
        exact = {a.values["totalLevel"] for a in anchors}
        for lvl in range(1, MAX_LEVEL + 1):
            lo = max([a for a in anchors if a.values["totalLevel"] <= lvl], key=lambda a: a.values["totalLevel"], default=anchors[0])
            hi = min([a for a in anchors if a.values["totalLevel"] >= lvl], key=lambda a: a.values["totalLevel"], default=anchors[-1])
            lo_lvl, hi_lvl = lo.values["totalLevel"], hi.values["totalLevel"]
            span = hi_lvl - lo_lvl
            # Cut off, not rounded, and in whole numbers so that an exact
            # 15.0 cannot come out as 14. The files hold levels 1, 2, 12 and
            # 15 only and do not say how the game fills the rest; the
            # published per-level tables do, on two Nightfarers: Wylder (the
            # eleven levels between the anchors, five attributes, all 55
            # values cut off; rounding misses 9) and the Guardian as he was
            # before patch 1.02.2 (Vigor 19 -> 54 is 3.5 a level, and the
            # table reads 22, 29, 36, 43, 50 on levels 3, 5, 7, 9, 11) --
            # eldenring.wiki.gg Nightreign:Attributes and Nightreign:Guardian,
            # the Fextralife Wylder page, read 14.11.2026.
            levels[str(lvl)] = {
                label: lo.values[key] + (
                    0 if span == 0 else
                    (hi.values[key] - lo.values[key]) * (lvl - lo_lvl) // span)
                for key, label in STAT_FIELDS
            }

        name_id = row.values.get("characterNameId", -1)
        name = hero_name_fmg.get(name_id) or f"Hero {row.id}"
        heroes.append(
            {
                "id": row.id,
                "name": name,
                "status_block": block,
                "levels": levels,
                "exact_levels": sorted(exact),
                # Character Skill cooldown in seconds, per Nightfarer. This is
                # the time base that makes "Character Skill Cooldown Reduction
                # -10%" mean something absolute. Zero for the Nightfarers whose
                # skill is not on a timer.
                "ability_cooldown": row.values.get("characterAbilityCooldown", 0.0),
                # The armament this Nightfarer starts an expedition holding.
                # -1 when no canonical row names one.
                "starting_weapon": starting_weapon.get(row.id, -1),
                # The off-hand one, absent where the hand starts empty --
                # like weapons[].inflicts, and unlike the field above, whose
                # -1 already means "no row names one" and cannot also mean
                # "named as empty".
                **({"starting_weapon_left": starting_weapon_left[row.id]}
                   if row.id in starting_weapon_left else {}),
            }
        )

    # ---- Chalices ---------------------------------------------------------
    # Three slots normally; three more become active in Deep of Night, and
    # those only accept Deep of Night relics.
    goods_name = text.get("GoodsName", {})
    vessels = []
    for r in stands.rows:
        goods_id = r.values.get("goodsId")
        vessels.append(
            {
                "id": r.id,
                "name": goods_name.get(goods_id, f"Chalice {r.id}"),
                "icon": r.values.get("iconId"),
                "hero_type": r.values.get("heroType"),
                "slots": [
                    r.values.get("relicSlot1"),
                    r.values.get("relicSlot2"),
                    r.values.get("relicSlot3"),
                ],
                "deep_slots": [
                    r.values.get("deepSlot1"),
                    r.values.get("deepSlot2"),
                    r.values.get("deepSlot3"),
                ],
            }
        )

    # ---- Effects ----------------------------------------------------------
    # A table id is not unique: several rows share one id to form a weighted
    # pool, so this has to be a multimap rather than a dict.
    attach_table_by_id: dict[int, list[param.ParamRow]] = collections.defaultdict(list)
    for r in attach_table.rows:
        attach_table_by_id[r.id].append(r)
    attach_by_id = {r.id: r for r in attach.rows}

    effects: dict[str, Any] = {}

    def register_effect(effect_id: int) -> str | None:
        row = attach_by_id.get(effect_id)
        if row is None:
            return None

        key = str(effect_id)
        if key in effects:
            return key

        # Rows with no SpEffect ids, no caption and no name of their own are
        # table padding, not effects -- ids 0, 9990000 and 999999999. They only
        # ever rendered as "Effect 999999999" with nothing to say.
        if (not any(row.values.get(f"passiveSpEffectId_{i}") and
                    row.values.get(f"passiveSpEffectId_{i}") > 0 for i in (1, 2, 3))
                and not (effect_name.get(row.values.get("attachTextId", -1)) or "").strip()
                and not (effect_info.get(row.values.get("attachTextId", -1)) or "").strip()):
            return None

        sp_ids = [
            row.values.get(f"passiveSpEffectId_{i}") for i in (1, 2, 3)
        ]
        passive_categories = [
            sp_by_id[s].values.get("spCategory") for s in sp_ids
            if s and s > 0 and s in sp_by_id]
        # permanentSpEffectId and onHitSpEffect were never read, and they hold
        # the whole payload for a handful of effects: "Max HP increased for
        # each great enemy defeated" carries nothing on its passive rows, and
        # maxHpRate 1.05 on its permanent one.
        sp_ids += [row.values.get("permanentSpEffectId"),
                   row.values.get("onHitSpEffect")]
        sp_ids = [s for s in sp_ids if s and s > 0]

        modifiers: dict[str, Any] = {}
        categories: list[int] = []
        inflicts: dict[str, Any] = {}
        payload_categories.clear()
        for sp_id in sp_ids:
            modifiers.update(sp_modifiers(sp_id))
        # Only when the effect says nothing of substance on its own. An effect
        # that already carries numbers does not need its state's payload merged
        # in, and doing so risks double-counting figures that are already right.
        # Lifetime and net-sync flags do not count as substance -- "Critical
        # Hits Earn Runes" carries nothing but dontDeleteOnDead, and testing
        # for an empty dict left it blank when its payload row holds soul 600.
        BOOKKEEPING = {"dontDeleteOnDead", "isWaitModeDelete", "isDisableNetSync",
                       "saveCategory", "isExtendSpEffectLife",
                       "isContractSpEffectLife", "bCurrHPIndependeMaxHP",
                       # Engine references, not player-facing numbers. Without
                       # these, "Raised stamina recovery for nearby allies"
                       # counted a behaviourId as substance and stayed blank
                       # while its payload row held the actual figure.
                       "behaviorId", "dmypolyId", "vfxId", "vfxId1",
                       "magParamChange", "miracleParamChange",
                       "shamanParamChange",
                       # Classification and targeting, not content. Without
                       # these, "[Duchess] Use Character Skill for Brief
                       # Invulnerability" counted spCategory as substance and
                       # never reached its payload row, which holds the
                       # 0.4 s window as effectEndurance.
                       "spCategory", "categoryPriority",
                       # A NaN on most rows; never equal to the baseline
                       # and never meaningful.
                       "grabityRate",
                       "effectTargetSelf", "effectTargetEnemy",
                       "effectTargetFriend", "effectTargetPlayer",
                       "effectTargetAI", "effectTargetLive",
                       "effectTargetGhost", "effectTargetOpposeTarget",
                       "effectTargetFriendlyTarget", "effectTargetPcDeceased"}
        payload_tiers: list[dict[str, Any]] = []
        # Which mechanism supplied the numbers, recorded so provenance can be
        # audited rather than re-derived and guessed at. "state" is a link the
        # data declares outright; "adjacent" is a convention, and is the one
        # worth checking by hand.
        payload_source = ""
        if not (set(modifiers) - BOOKKEEPING):
            for sp_id in sp_ids:
                found = state_payload(sp_id)
                if found:
                    payload_source = "state"
                modifiers.update(found)
        if not (set(modifiers) - BOOKKEEPING):
            for sp_id in sp_ids:
                payload_tiers = payload_tiers or adjacent_payload(sp_id)
            if payload_tiers:
                payload_source = "adjacent"
                # The lowest tier goes into modifiers so the build maths has
                # plain numbers to work with; the full ladder rides alongside
                # so the description can show the range rather than implying
                # the lowest rung is the only value.
                modifiers.update(payload_tiers[0])
        for sp_id in sp_ids:
            inflicts.update(follow_chain(sp_id))
            sp_row = sp_by_id.get(sp_id)
            if sp_row is not None:
                cat = sp_row.values.get("spCategory")
                if cat:
                    categories.append(cat)

        # The payload rows found above can hand off in turn, and the chain has
        # to be picked up from them as well. "Starting armament inflicts frost"
        # is the clear case: row 7120400 is a bare marker carrying neither the
        # penalty nor the status, while the adjacent armed rows carry both --
        # physicsAttackPowerRate 0.85 and an atkOccurrenceSpEffectId leading to
        # freezeAttackPower 35. Walking only sp_ids stopped at the marker and
        # reported the relic as inflicting nothing at all.
        for field_name in CHAIN_FIELDS:
            nxt = modifiers.get(field_name)
            if isinstance(nxt, int) and nxt > 0:
                for label, value in follow_chain(nxt).items():
                    inflicts.setdefault(label, value)

        # Of those, the ones your own attacks apply, as opposed to the ones
        # that build up on you. Both arrive as "inflicts", and telling them
        # apart matters: "Starting armament inflicts frost" is a weapon
        # property, while "Taking Damage Causes Poison Buildup" is a curse on
        # the wearer. The difference is the field the chain starts from --
        # atkOccurrenceSpEffectId fires on an attack landing, the other chain
        # fields fire on a timer or on being hit.
        # The attach row's own onHitSpEffect is the other door: "Attacks
        # Inflict Rot" 8110400-402 carries nothing else, and its payload
        # is the very row 8110410 reaches through atkOccurrenceSpEffectId.
        on_hit_ids = [modifiers.get(ATTACK_CHAIN_FIELD),
                      row.values.get("onHitSpEffect")]
        on_hit_ids += [sp_by_id[i].values.get(ATTACK_CHAIN_FIELD)
                       for i in sp_ids if i in sp_by_id]
        inflicts_on_hit: dict[str, Any] = {}
        for nxt in on_hit_ids:
            if isinstance(nxt, int) and nxt > 0:
                for label, value in follow_chain(nxt).items():
                    inflicts_on_hit.setdefault(label, value)

        # The spell a swap relic hands the player. The field is there on
        # every row -- the read above refuses to go on otherwise -- and -1
        # on all but ten of them.
        swapped_spells = [sp_by_id[i].values[START_MAGIC_FIELD] for i in sp_ids
                          if i in sp_by_id
                          and sp_by_id[i].values[START_MAGIC_FIELD] > 0]

        text_id = row.values.get("attachTextId", -1)

        # A few effects are named and described only in the PermanentBuff
        # tables, reached through the SpEffect's own permanentBuffTextId. The
        # three "Rune of the Strong" rows are the whole of it: without this
        # they render as "Effect 8500100" with no description, when the game
        # ships both a name and "Gain 10000 runes" for them.
        buff_name = buff_info = ""
        for sp_id in sp_ids:
            sp_row = sp_by_id.get(sp_id)
            if sp_row is None:
                continue
            buff_id = sp_row.values.get("permanentBuffTextId", -1)
            if buff_id and buff_id > 0:
                buff_name = buff_name or permanent_buff_name.get(buff_id, "")
                buff_info = buff_info or permanent_buff_info.get(buff_id, "")

        effects[key] = {
            "id": effect_id,
            "icon": _icon(row.values.get("statusIconId")),
            "name": (effect_name.get(text_id) or effect_name.get(effect_id)
                     or buff_name or f"Effect {effect_id}"),
            # Mirror the name lookup's fallback. The name tries the text id
            # then the effect's own id; the caption only ever tried the text
            # id, so any caption filed under the effect id was being missed.
            "info": (effect_info.get(text_id)
                     or effect_info.get(effect_id)
                     or buff_info
                     or ""),
            # isStrongestEffect: only the single strongest copy applies.
            "stacks": not bool(row.values.get("isStrongestEffect")),
            "is_debuff": bool(row.values.get("isDebuff")),
            "sp_effect_ids": sp_ids,
            "sp_categories": categories,
            # The game's own mutual-exclusion key. Two effects sharing a
            # positive exclusivityId genuinely cannot both apply; anything
            # else can. Only 64 of 2079 rows set it, which is why guessing
            # from a shared SpEffect category produced false conflicts
            # between effects that plainly stack.
            "exclusivity": row.values.get("exclusivityId", -1),
            # How the game itself files this effect in its own UI filters --
            # "Attack Power", "Damage Negation", a Nightfarer's name, or
            # "Demerits (...)" for a curse. Empty where the game files it
            # nowhere, which is most of them.
            "game_category": filter_category.get(
                row.values.get("attachFilterParamId", -1), ""),
            "modifiers": modifiers,
            # Kept out of "modifiers" deliberately: the build maths reads that
            # dict and expects plain numbers, while this is a ladder of them.
            "payload_tiers": payload_tiers if len(payload_tiers) > 1 else [],
            "payload_source": payload_source,
            # Status buildup this effect inflicts, reached through the chain
            # rather than sitting on the effect's own row.
            "inflicts": inflicts,
            # The subset your own attacks apply, for the weapon block.
            "inflicts_on_hit": inflicts_on_hit,
            "allowed_heroes": [
                f[len("allow"):] for f in ALLOW_FIELDS if row.values.get(f)
            ],
            # Taken from the param itself rather than matched on the
            # effect's name. Absent unless the effect swaps a spell.
            **({"start_magic_id": swapped_spells[0]} if swapped_spells else {}),
            # None of its own rows is one the game holds twice
            # (`STACKING_CATEGORY`): a second relic carrying this effect
            # leaves one of it. Absent where a copy adds.
            **({"one_instance": True} if (
                passive_categories
                and STACKING_CATEGORY not in passive_categories)
               or (payload_source and any(
                   category != STACKING_CATEGORY
                   for category in payload_categories)) else {}),
        }
        return key

    def pool_weight(row: param.ParamRow) -> int:
        """chanceWeight lives in the low 16 bits.

        The shipped paramdef declares it as s32, but the high half is a
        constant -1, which would otherwise read as a nonsensical -65536.
        """
        return row.values["chanceWeight"] & 0xFFFF

    def resolve_table(table_id: int) -> list[tuple[str, float]]:
        """attachEffectTableId -> (effect key, chance) for entries that can roll.

        A single-entry pool is a guaranteed effect, so its chance is 1. In a
        multi-entry pool an entry with zero weight can never come up, so it is
        dropped entirely rather than reported as 0%.
        """
        entries = attach_table_by_id.get(table_id, [])
        if not entries:
            return []

        if len(entries) == 1:
            key = register_effect(entries[0].values.get("attachEffectId"))
            return [(key, 1.0)] if key else []

        total = sum(pool_weight(e) for e in entries)
        if total <= 0:
            return []

        out = []
        for entry in entries:
            weight = pool_weight(entry)
            if weight <= 0:
                continue
            key = register_effect(entry.values.get("attachEffectId"))
            if key:
                out.append((key, weight / total))
        return out

    # ---- Relics -----------------------------------------------------------
    # A relic template does not carry fixed effects: each slot references a
    # pool the game rolls from on drop. So rather than inlining those (huge)
    # pools per relic, record for each effect which slot colours can yield it.
    colours_by_effect: dict[str, set[int]] = collections.defaultdict(set)
    deep_colours_by_effect: dict[str, set[int]] = collections.defaultdict(set)
    # (effect key, colour, is_deep) -> that effect's share of each pool it is in.
    # Deep of Night relics draw from different pools, so the two modes must be
    # kept apart: a slot knows its colour and its mode, and can then filter.
    shares: dict[tuple[str, int, bool], list[float]] = collections.defaultdict(list)
    # effect key -> [relic slots that can roll it, of which on cursed relics]
    curse_sources: dict[str, list[int]] = {}
    curse_effects: set[str] = set()

    for row in attach.rows:
        register_effect(row.id)

    relics = []
    for row in antique.rows:
        name = antique_name.get(row.id)
        if not name:
            continue  # unnamed rows are placeholders / cut content
        colour = row.values.get("relicColor")
        is_deep = row.values.get("unknown_1b") == DEEP_MARKER
        target = deep_colours_by_effect if is_deep else colours_by_effect

        # Curse slots: extra effect tables that only ever yield debuffs, so a
        # relic referencing one always drags a curse along with its good rolls.
        curses = [row.values.get(f, -1) for f in CURSE_FIELDS]
        curse_pools = [c for c in curses if c and c > 0]
        has_curse = bool(curse_pools)

        pool_sizes = []
        for i in (1, 2, 3):
            tid = row.values.get(f"attachEffectTableId_{i}", -1)
            if tid and tid > 0:
                entries = resolve_table(tid)
                pool_sizes.append(len(entries))
                for key, chance in entries:
                    target[key].add(colour)
                    shares[(key, colour, is_deep)].append(chance)
                    stats = curse_sources.setdefault(key, [0, 0])
                    stats[0] += 1
                    if has_curse:
                        stats[1] += 1

        # Which curses this relic can actually land, per curse slot. A relic
        # rolls one curse from each pool it references, so keeping the pools
        # separate lets the planner say "one of these, then one of these"
        # rather than lumping them into a single undifferentiated list.
        curse_options = []
        for tid in curse_pools:
            keys = []
            for key, chance in resolve_table(tid):
                curse_effects.add(key)
                keys.append(key)
                # Curses draw from their own pools, so they never picked up a
                # colour from the ordinary ones and came out with an empty
                # colour list -- which made the Effects tab's "rollable only"
                # filter hide every curse in the game. Record the colour of
                # the relic that can inflict it, exactly as for a good roll.
                target[key].add(colour)
                shares[(key, colour, is_deep)].append(chance)
            curse_options.append(sorted(set(keys)))

        relics.append(
            {
                "id": row.id,
                "name": name,
                "caption": antique_caption.get(row.id, ""),
                "colour": colour,
                "colour_name": RELIC_COLOURS.get(colour, str(colour)),
                "icon": row.values.get("iconId"),
                "is_deep": is_deep,
                "has_curse": has_curse,
                "curse_count": len(curse_pools),
                "curse_options": curse_options,
                "pool_sizes": pool_sizes,
            }
        )

    for key, colours in colours_by_effect.items():
        effects[key]["colours"] = sorted(colours)
    for key, colours in deep_colours_by_effect.items():
        effects[key]["deep_colours"] = sorted(colours)

    # Roll chance per colour and mode. A pool is one draw, so an effect's share
    # of a pool is its chance in that draw; an effect sitting in several pools
    # gets the average share plus the best case, since pools are not equally
    # likely to be the one rolled.
    for (key, colour, is_deep), values in shares.items():
        entry = effects.get(key)
        if entry is None:
            continue
        field_name = "deep_chance" if is_deep else "chance"
        entry.setdefault(field_name, {})[str(colour)] = {
            "pools": len(values),
            "avg": round(sum(values) / len(values), 6),
            "max": round(max(values), 6),
        }

    # Curse relationship. "always" means every relic that can roll this effect
    # also carries a curse slot, so taking it means taking a curse.
    for key, (total, cursed) in curse_sources.items():
        entry = effects.get(key)
        if entry is None or total == 0:
            continue
        entry["curse"] = (
            "always" if cursed == total else "sometimes" if cursed else "never"
        )
        entry["curse_share"] = round(cursed / total, 4)

    for key in curse_effects:
        if key in effects:
            effects[key]["is_curse"] = True

    # Caption inheritance. Many effects ship as a ladder -- "Successful
    # guarding fills more of the Art gauge" and the same thing "+1", "+2" --
    # and only the unnumbered member carries a caption, leaving the rest with
    # nothing to show. The caption describes the mechanic, not the magnitude,
    # so a sibling's applies verbatim; the magnitude is already in the name and
    # in the derived modifier text, so nothing is misstated by borrowing it.
    def base_name(text_value: str) -> str:
        flat = " ".join(str(text_value).split())
        # Strips a trailing "+3" and also a bare trailing "+", so that
        # "Ultimate Art Auto Charge +3" and "Ultimate Art Auto Charge +" land
        # on the same base and can share the latter's caption.
        return re.sub(r"\s*\+\s*\d*$", "", flat).strip().lower()

    captions_by_base: dict[str, str] = {}
    for entry in effects.values():
        caption = " ".join(str(entry.get("info") or "").split())
        if caption:
            captions_by_base.setdefault(base_name(entry.get("name", "")), caption)

    inherited = 0
    for entry in effects.values():
        if str(entry.get("info") or "").strip():
            continue
        borrowed = captions_by_base.get(base_name(entry.get("name", "")))
        if borrowed:
            entry["info"] = borrowed
            entry["info_inherited"] = True
            inherited += 1

    for entry in effects.values():
        entry.setdefault("info_inherited", False)
        entry.setdefault("colours", [])
        entry.setdefault("deep_colours", [])
        entry.setdefault("chance", {})
        entry.setdefault("deep_chance", {})
        entry.setdefault("curse", "never")
        entry.setdefault("curse_share", 0.0)
        entry.setdefault("is_curse", False)

    # ---- Weapons ----------------------------------------------------------
    weapon_name = text.get("WeaponName", {})
    weapon_table = table("EquipParamWeapon")
    reinforce_table = table("ReinforceParamWeapon")
    aec_table = table("AttackElementCorrectParam")

    catalyst_scaling = catalyst_scaling_rates(reinforce_table)

    reinforce = {
        str(r.id): {
            "atk": {
                "Physics": r.values.get("physicsAtkRate", 1.0),
                "Magic": r.values.get("magicAtkRate", 1.0),
                "Fire": r.values.get("fireAtkRate", 1.0),
                "Thunder": r.values.get("thunderAtkRate", 1.0),
                "Dark": r.values.get("darkAtkRate", 1.0),
            },
            "correct": {
                "Strength": r.values.get("correctStrengthRate", 1.0),
                "Dexterity": r.values.get("correctAgilityRate", 1.0),
                "Intelligence": r.values.get("correctMagicRate", 1.0),
                "Faith": r.values.get("correctFaithRate", 1.0),
                "Arcane": r.values.get("correctLuckRate", 1.0),
            },
            # The rate behind the figure the game shows for a staff or a
            # seal instead of an attack rating. Read for every group, not
            # only for the catalyst ones: which groups are catalyst groups is
            # not this table's to decide, and the armament says it (QA-099).
            "catalyst_scaling": catalyst_scaling[r.id],
        }
        for r in reinforce_table.rows
    }

    element_correct = {}
    for r in aec_table.rows:
        entry = {}
        for damage in DAMAGE_TYPES:
            entry[damage] = {
                stat: {
                    "on": bool(r.values.get(f"is{field}Correct_by{damage}")),
                    "influence": r.values.get(
                        f"Influence{field}CorrectRate_by{damage}", 1.0
                    ),
                }
                for stat, field in AEC_STATS.items()
            }
        element_correct[str(r.id)] = entry

    # ---- Which effects a weapon can actually roll ---------------------------
    # Nightreign weapons carry rolled effects exactly as relics do, through the
    # same AttachEffectTable pools. EquipParamCustomWeapon maps a weapon to up
    # to three of them in attachEffectTableId_1..3, alongside its Skill
    # (swordArtsTableId) and any spells (magicTableId_1/2).
    #
    # 388 of the armaments have at least one pool; the rest hold -1 throughout
    # and can roll nothing. A weapon usually appears on several rows -- one per
    # variant -- so the pools are unioned per weapon and the entries deduped,
    # keeping the highest weight seen for an effect.
    #
    # The art and spell tables resolve the same way, to ids rather than
    # weights (AD-056.1): every row of SwordArtsTableParam / MagicTableParam
    # carries its table's id as its own, so one table is all rows sharing it.
    #
    # Only base armaments name tables. A variant's rows (Magic Longsword
    # 2000800) carry -1 in every one of them, and the variant is found with
    # its base armament's pools (Longsword 2000000): in play a Magic Longsword
    # carried Glintblade Phalanx from the Longsword's art table (AD-056 P.7,
    # M5). The effect tables sit on the same rows; `effect_pool` stays the
    # armament's own, because `weaponslots.rollable_effects` already offers
    # an infused variant its base's effects under limits of its own.
    CUSTOM_POOL_FIELDS = ("attachEffectTableId_1", "attachEffectTableId_2",
                          "attachEffectTableId_3")
    CUSTOM_SPELL_FIELDS = ("magicTableId_1", "magicTableId_2")

    def table_entries(name: str, entry_field: str) -> dict[int, set[int]]:
        """Table id -> the ids it can hand out, zero-weight entries left out."""
        entries: dict[int, set[int]] = collections.defaultdict(set)
        for row in table(name).rows:
            entry = row.values.get(entry_field, -1)
            weight = row.values.get("chanceWeight", 0)
            if isinstance(entry, int) and entry > 0 and weight > 0:
                entries[row.id].add(entry)
        return entries

    art_tables = table_entries("SwordArtsTableParam", "swordArtsId")
    spell_tables = table_entries("MagicTableParam", "magicId")
    custom_weapon = table("EquipParamCustomWeapon")
    weapon_pool_ids: dict[int, set[int]] = collections.defaultdict(set)
    weapon_art_pools: dict[int, set[int]] = collections.defaultdict(set)
    weapon_spell_pools: dict[int, list[set[int]]] = collections.defaultdict(
        lambda: [set() for _ in CUSTOM_SPELL_FIELDS])
    for r in custom_weapon.rows:
        target = r.values.get("targetWeaponId", -1)
        if not isinstance(target, int) or target <= 0:
            continue
        for field_name in CUSTOM_POOL_FIELDS:
            pool = r.values.get(field_name, -1)
            if isinstance(pool, int) and pool > 0:
                weapon_pool_ids[target].add(pool)
        weapon_art_pools[target] |= art_tables.get(
            r.values.get("swordArtsTableId", -1), set())
        for spell_slot, field_name in zip(weapon_spell_pools[target],
                                          CUSTOM_SPELL_FIELDS):
            spell_slot |= spell_tables.get(r.values.get(field_name, -1), set())

    def own_or_base(pools: dict, weapon_id: int):
        """This armament's pool, or its base armament's where its own is empty."""
        base = weapon_id // VARIANT_SPAN * VARIANT_SPAN
        return next((pools[owner] for owner in (weapon_id, base)
                     if any(pools.get(owner, ()))), ())

    def weapon_effect_pool(weapon_id: int) -> list[dict[str, Any]]:
        """The effects this weapon can roll, with the game's own weights."""
        best: dict[int, int] = {}
        for pool in sorted(weapon_pool_ids.get(weapon_id, ())):
            for entry in attach_table_by_id.get(pool, []):
                effect_id = entry.values.get("attachEffectId")
                if not isinstance(effect_id, int) or effect_id <= 0:
                    continue
                weight = pool_weight(entry)
                if weight <= 0:
                    # A zero-weight entry can never be rolled. Counting them
                    # corrupted relic roll chances once already; same here.
                    continue
                if weight > best.get(effect_id, 0):
                    best[effect_id] = weight
        return [{"effect": eid, "weight": w} for eid, w in sorted(best.items())]

    def weapon_inflicts(row) -> dict[str, float]:
        """Status buildup the armament itself applies on hit.

        The armament's own spEffectBehaviorId0..2 rows carry the same
        *AttackPower fields the relic-effect chain walk reads. Where two of
        the three rows raise the same status the larger figure is kept
        rather than their sum -- whether the game adds them is unmeasured,
        and the one weapon whose rows were checked (Blood Great Omenkiller
        Cleaver, 69) carries its whole figure on a single row.
        """
        found: dict[str, float] = {}
        for field in ("spEffectBehaviorId0", "spEffectBehaviorId1",
                      "spEffectBehaviorId2"):
            ref = row.values.get(field, -1)
            if not isinstance(ref, int) or ref <= 0:
                continue
            target = sp_by_id.get(ref)
            if target is None:
                continue
            for power_field, label in STATUS_POWER.items():
                value = target.values.get(power_field, 0)
                if isinstance(value, (int, float)) and value > 0:
                    found[label] = max(found.get(label, 0), value)
        return found

    weapons = []
    for r in weapon_table.rows:
        name = weapon_name.get(r.id)
        if not name or not name.strip():
            continue
        bases = {d: r.values.get(f"attackBase{d}", 0) for d in DAMAGE_TYPES}
        if not any(bases.values()):
            continue
        inflicts = weapon_inflicts(r)
        spell_pools = own_or_base(weapon_spell_pools, r.id)
        weapons.append(
            {
                "id": r.id,
                "name": name.strip(),
                "icon": r.values.get("iconId"),
                "weight": r.values.get("weight"),
                "wep_type": r.values.get("wepType"),
                "rarity": r.values.get("rarity", 0),
                # A pair held one in each hand -- every fist and claw, the
                # Ornamental Straight Sword, the Starscourge Greatsword; not
                # the twinblades, which the game keeps as one armament. The
                # game rates two-handing a pair by its own rule (QA-276).
                "paired": bool(r.values.get("isDualBlade", 0)),
                # Flat HP won back per landed hit under the rally mechanic. It
                # is a property of the armament, not of the damage dealt, so it
                # belongs beside the weapon rather than with the relic. 0 means
                # the weapon reclaims nothing at all, which 132 of them do --
                # worth knowing before building around a rally relic.
                "regain_hp": r.values.get("wepRegainHp", 0),
                "base": bases,
                "scaling": {
                    "Strength": r.values.get("correctStrength", 0.0),
                    "Dexterity": r.values.get("correctAgility", 0.0),
                    "Intelligence": r.values.get("correctMagic", 0.0),
                    "Faith": r.values.get("correctFaith", 0.0),
                    "Arcane": r.values.get("correctLuck", 0.0),
                },
                "curve": {d: r.values.get(f"correctType_{d}") for d in DAMAGE_TYPES},
                # Kept because it is in the param, not because anything reads
                # it: `nrplanner` no longer gates scaling on it (T-034). The
                # gate it used to drive never fired on real data -- 1791 of
                # 1793 armaments carry an all-zero requirement here, the other
                # two ask for Arcane 1, and every Nightfarer starts above that
                # (QA-061) -- and the user confirmed in play that Nightreign
                # has no attribute requirement for armaments at all. Two test
                # helpers still read this field directly, to pick a weapon
                # deterministically rather than through the removed gate:
                # `tests/weapon_damage_cases.heaviest_of_family` and
                # `tests/test_marginal_returns.most_responsive_armament`.
                "requires": {
                    "Strength": r.values.get("properStrength", 0),
                    "Dexterity": r.values.get("properAgility", 0),
                    "Intelligence": r.values.get("properMagic", 0),
                    "Faith": r.values.get("properFaith", 0),
                    "Arcane": r.values.get("properLuck", 0),
                },
                "reinforce_type": r.values.get("reinforceTypeId", 0),
                "element_correct_id": r.values.get("attackElementCorrectId"),
                # The armament's own spell slots, -1 where it has none. Read
                # because it is the one field that tells the two rows called
                # `Recluse's Staff` apart by something a player would care
                # about: 33770000 can hold no spell, so it is not a catalyst
                # anybody can cast with (QA-119). Carried as a list rather
                # than a tuple so a live extraction and a snapshot read back
                # out of JSON hand back the same thing. What it does **not**
                # say on its own: 1764 of the 1793 named armaments carry -1
                # in both, because a sword holds no spell either -- the scope
                # that makes this usable is in
                # `nrplanner.model.is_unequippable_catalyst`.
                "equipped_spells": [r.values.get("equippedSpell_R1", -1),
                                    r.values.get("equippedSpell_R2", -1)],
                # The art the armament carries in its own row, raw: whether a
                # tile starts on it or has to choose is the planner's rule
                # (`damage.art_in_use`), not this file's (AD-056.4/6).
                "art_default": r.values.get("swordArtsParamId", -1),
                # Every art this armament can be found with, across its
                # variants. Empty where it rolls none.
                "art_pool": sorted(own_or_base(weapon_art_pools, r.id)),
                # The spells a found staff or seal can carry, per slot. Slot 1
                # holds one, slot 2 is rolled from 64 or 92 (AD-056, P.2), so
                # `equipped_spells` is only the row's default for slot 2.
                **({"spell_pools": [sorted(s) for s in spell_pools]}
                   if spell_pools else {}),
                # Effects this weapon can roll, from its own pools. Empty for
                # the armaments that roll nothing.
                "effect_pool": weapon_effect_pool(r.id),
                # Status buildup per hit, when the armament applies any. The
                # elemental variants always showed their element; the status
                # variants hid the one number they exist for until 1.7.1.
                **({"inflicts": inflicts} if inflicts else {}),
            }
        )

    # ---- Weapon and spell families, named by the buffs that target them ----
    # Nightreign ships no wepType enum, but a relic effect like "Improved
    # Katana Attack Power" carries triggerOnWepType, and one like "Improved
    # Bestial Incantations" carries magicSubCategoryChange1. So the buffs
    # supply the category names for both.
    weapon_families: dict[str, str] = {}
    spell_families: dict[str, str] = {}
    # Case-insensitive: the game writes both "Sorcery" and "sorcery".
    wep_pattern = re.compile(r"^Improved (.+?) Attack Power$", re.I)
    spell_pattern = re.compile(r"^Improved (.+?) (?:sorcer\w*|incantations?)$", re.I)

    for row in attach.rows:
        label = (effect_name.get(row.values.get("attachTextId")) or "").strip()
        if not label:
            continue
        for i in (1, 2, 3):
            sp = sp_by_id.get(row.values.get(f"passiveSpEffectId_{i}"))
            if sp is None:
                continue
            wep_match = wep_pattern.match(label)
            trigger = sp.values.get("triggerOnWepType")
            if wep_match and trigger and trigger > 0:
                weapon_families.setdefault(str(trigger), wep_match.group(1))
            spell_match = spell_pattern.match(label)
            sub = sp.values.get("magicSubCategoryChange1")
            if spell_match and sub and sub > 0:
                spell_families.setdefault(str(sub), spell_match.group(1))

    weapon_families.update(FALLBACK_WEAPON_FAMILIES)

    for weapon in weapons:
        weapon["family"] = weapon_families.get(
            str(weapon["wep_type"]), f"Type {weapon['wep_type']}"
        )

    # ---- Spells -----------------------------------------------------------
    magic_name = text.get("MagicName", {})
    magic_caption = text.get("MagicCaption", {})
    magic_table = table("Magic")

    # ---- What a spell hits for: Magic -> Bullet -> AtkParam_Pc ------------
    # No spell carries a figure of its own. Magic names bullets, a bullet
    # names an AtkParam row, and that row holds the base damage per type.
    #
    # The def for that table is filed under another name: `AtkParam.xml`
    # describes AtkParam_Pc exactly -- 464 bytes, the table's own row length
    # -- while `defs["AtkParam_Pc"]` does not exist. Without the alias,
    # param.read has no def, reads no field, and every spell comes out
    # undamaging, which is a lie rather than a gap.
    atk_def = defs.get("AtkParam_Pc") or defs.get("AtkParam")

    def only(pdef: paramdef.ParamDef | None, names: set[str]):
        """The same def cut down to the fields this chain reads.

        Offsets and row length are the def's own, so param.read still checks
        the def against the row exactly as it would otherwise. Reading all
        211 AtkParam and 132 Bullet fields of 21,000 rows instead costs 1,3 s
        and a few hundred megabytes of dictionaries for six numbers a row.
        """
        if pdef is None:
            return None
        return paramdef.ParamDef(
            pdef.param_type,
            pdef.data_version,
            [f for f in pdef.fields if f.name in names],
            pdef.row_size,
        )

    atk_table = param.read(
        members["AtkParam_Pc"],
        only(atk_def, {*SPELL_DAMAGE_FIELDS.values(), *ART_MOTION_FIELDS.values(),
                       ART_ELEMENT_CORRECT_FIELD, *HIT_SP_EFFECT_FIELDS}),
    )
    if not atk_table.rows or not atk_table.rows[0].values:
        raise NotWhatItClaims(
            f"AtkParam_Pc read back {len(atk_table.rows)} rows without a "
            f"single field, so no paramdef fits its {atk_table.row_size}-byte "
            f"rows. That is where every spell's damage is: extracting past it "
            f"would report all {len(magic_table.rows)} spells as harmless.")
    atk_by_id = {r.id: r for r in atk_table.rows}
    bullet_def = only(defs.get("Bullet"), {"atkId_Bullet", "HitBulletID",
                                           *HIT_SP_EFFECT_FIELDS})
    if bullet_def is not None:
        if bullet_def.row_size != BULLET_DEF_SIZE:
            raise NotWhatItClaims(
                f"{BULLET_INTERVAL_FIELD!r} is read at offset "
                f"{BULLET_INTERVAL_OFFSET} rather than by name, and the Bullet "
                f"paramdef describes {bullet_def.row_size} bytes per row where "
                f"it was measured against {BULLET_DEF_SIZE}. Re-measure the "
                f"offset before trusting any spell's damage.")
        bullet_def.fields.append(paramdef.Field(
            BULLET_INTERVAL_FIELD, "s32", BULLET_INTERVAL_OFFSET, 4))
    bullet_by_id = {
        r.id: r
        for r in param.read(members["Bullet"], bullet_def).rows
    }
    # Bullets an animation fires through BehaviorParam_PC (refType 1). The def
    # is filed as `BehaviorParam`, the same layout for the player's table.
    behavior_def = only(defs.get("BehaviorParam_PC") or defs.get("BehaviorParam"),
                        {"refType", "refId"})
    launched_by_behavior = sorted({
        r.values.get("refId")
        for r in param.read(members["BehaviorParam_PC"], behavior_def).rows
        if r.values.get("refType") == BEHAVIOR_REF_BULLET
        and isinstance(r.values.get("refId"), int) and r.values["refId"] > 0
    })
    statuses = set(STATUS_POWER.values())

    def hit_inflicts(sp_ids) -> dict[str, Any]:
        """The status buildup these SpEffect rows apply to what is hit."""
        found: dict[str, Any] = {}
        for sp_id in sp_ids:
            if isinstance(sp_id, int) and sp_id > 0:
                for label, value in follow_chain(sp_id).items():
                    if label in statuses:
                        found.setdefault(label, value)
        return found

    def hit_sp_ids(row) -> list:
        return [row.values.get(field) for field in HIT_SP_EFFECT_FIELDS]

    def spell_damage(row: param.ParamRow
                     ) -> tuple[dict[str, int], int, dict[str, Any]]:
        """The spell's strongest single hit, per damage type, its row, and
        the status buildup any of its hits applies.

        Strongest rather than first: across the shipped data both name the
        same set of damage types, so the choice moves no ranking, and the
        strongest needs no assumption about the order of refId1..10 (Rock
        Blaster opens on 64 and lands its main hit for 260). Where a spell has
        a charged form this is the charged figure -- Beast Claw 362, not 323.
        """
        atk_ids: list[int] = []
        on_hit: list = []
        seen: set[int] = set()

        def follow_bullet(bullet_id, depth: int) -> None:
            # A bullet that spawns another is how a charged or delayed hit is
            # built, and those chains loop back on themselves -- hence both
            # the set and the cap.
            if not isinstance(bullet_id, int) or bullet_id <= 0:
                return
            if bullet_id in seen or depth > MAX_BULLET_DEPTH:
                return
            seen.add(bullet_id)
            bullet = bullet_by_id.get(bullet_id)
            if bullet is None:
                return
            atk_ids.append(bullet.values.get("atkId_Bullet", -1))
            on_hit.extend(hit_sp_ids(bullet))
            follow_bullet(bullet.values.get("HitBulletID", -1), depth + 1)
            follow_bullet(bullet.values.get(BULLET_INTERVAL_FIELD, -1),
                          depth + 1)

        for slot in range(1, MAGIC_REF_SLOTS + 1):
            ref = row.values.get(f"refId{slot}", -1)
            if not isinstance(ref, int) or ref <= 0:
                continue
            category = row.values.get(f"refCategory{slot}")
            if category == MAGIC_REF_BULLET:
                follow_bullet(ref, 0)
            elif category == MAGIC_REF_ATTACK:
                atk_ids.append(ref)
            elif category == MAGIC_REF_SPEFFECT and ref in sp_by_id:
                # A buff on the caster ("Poison Armament"): only what it
                # makes the caster's attacks apply, never what it does to
                # the caster.
                on_hit.append(sp_by_id[ref].values.get(ATTACK_CHAIN_FIELD))

        # The spell's own bullets that only its animation fires (v22); after
        # everything the rows name, so a status found there keeps its place.
        block = SPELL_BULLET_BLOCK_BASE + row.id * SPELL_BULLET_BLOCK_SIZE
        start = bisect.bisect_left(launched_by_behavior, block)
        for bullet_id in launched_by_behavior[start:]:
            if bullet_id >= block + SPELL_BULLET_BLOCK_SIZE:
                break
            follow_bullet(bullet_id, 0)

        best: dict[str, int] = {}
        best_atk = -1
        for atk_id in atk_ids:
            atk_row = atk_by_id.get(atk_id)
            if atk_row is None:
                continue
            on_hit.extend(hit_sp_ids(atk_row))
            # Whole numbers above zero only. A type a hit does not deal has
            # no place in the mapping, and a value that is not an integer is
            # not this field -- NaN would go into the snapshot as a token no
            # JSON reader accepts.
            hit = {
                damage: atk_row.values[field]
                for damage, field in SPELL_DAMAGE_FIELDS.items()
                if isinstance(atk_row.values.get(field), int)
                and atk_row.values[field] > 0
            }
            if sum(hit.values()) > sum(best.values()):
                best, best_atk = hit, atk_row.id
        return best, best_atk, hit_inflicts(on_hit)

    # Families the buffs do not name: mine the spell descriptions, which say
    # things like "one of the primeval sorceries". Only accept a phrase that
    # every spell in the group agrees on, so nothing is guessed.
    caption_pattern = re.compile(
        r"\b(?:the\s+)?([A-Za-z][A-Za-z'\- ]{2,28}?)\s+(?:sorcer\w*|incantations?)\b",
        re.I,
    )
    STOP = {"the", "a", "an", "this", "these", "those", "of", "and", "other",
            "such", "all", "many", "some", "one", "his", "her", "their", "its"}

    by_sub: dict[int, list] = collections.defaultdict(list)
    for r in magic_table.rows:
        if magic_name.get(r.id, "").strip():
            by_sub[r.values.get("subCategory1")].append(r)

    for sub, rows in by_sub.items():
        if str(sub) in spell_families or not sub:
            continue
        proposals = []
        for r in rows:
            found = set()
            for match in caption_pattern.finditer(magic_caption.get(r.id, "")):
                phrase = " ".join(
                    w for w in match.group(1).split() if w.lower() not in STOP
                ).strip()
                if phrase:
                    found.add(phrase.title())
            proposals.append(found)
        shared = set.intersection(*proposals) if proposals and all(proposals) else set()
        if len(shared) == 1:
            spell_families[str(sub)] = next(iter(shared))

    # Named by hand where neither the buffs nor the captions supply it, on
    # the same footing as FALLBACK_WEAPON_FAMILIES: only groups whose every
    # member wears the name on its face. 1 is the two moons, 8 all magma,
    # 10 all death sorceries (Rancorcall, Ancient Death Rancor, Explosive
    # Ghostflame, Tibia's Summons), 13 all frost. The groups that would need
    # an invented name -- 6 mixes Comet with Eternal Darkness, and 14, 15,
    # 27, 126 hold one spell each -- stay "Group N", which is the honest
    # label for "the game groups these and names the group nowhere".
    spell_families.setdefault("1", "Moon")
    spell_families.setdefault("8", "Magma")
    spell_families.setdefault("10", "Death")
    spell_families.setdefault("13", "Frost")

    spells = []
    for r in magic_table.rows:
        name = magic_name.get(r.id)
        if not name or not name.strip():
            continue
        category = SPELL_CATEGORIES.get(r.values.get("spEffectCategory"))
        if category is None:
            continue
        sub = r.values.get("subCategory1")
        damage_by_type, damage_atk, inflicts = spell_damage(r)
        spells.append(
            {
                "id": r.id,
                "name": name.strip(),
                "caption": magic_caption.get(r.id, ""),
                "icon": r.values.get("iconId"),
                "category": category,
                # subCategory1 == 0 really is "no family". A non-zero id with
                # no name is still a distinct group, so keep it separate
                # rather than merging unrelated spells into one bucket.
                "family": (
                    spell_families.get(str(sub))
                    or ("General" if not sub else f"Group {sub}")
                ),
                "fp": r.values.get("mp"),
                "fp_charged": r.values.get("mp_charge"),
                "stamina": r.values.get("stamina"),
                "slots": r.values.get("slotLength"),
                # Base damage per type, and the AtkParam row it was read
                # from so a later check knows where to look. Both absent on a
                # spell that damages nothing -- a heal, a buff, a shield.
                **({"damage": damage_by_type, "damage_atk": damage_atk}
                   if damage_by_type else {}),
                # Status buildup per hit; absent where no hit applies one.
                **({"inflicts": inflicts} if inflicts else {}),
            }
        )

    # ---- Weapon arts: SwordArtsParam -> AtkParam_Pc (AD-056.1) -------------
    # An art names one AtkParam row. Where that row carries no flat figure,
    # its corrections are the motion value -- the percentage of the swing's
    # attack rating the hit deals. Where it does carry one, the figure is kept
    # without a reader, so the dummy measurement OF-60 waits for can calibrate
    # it without another version step. `damage_atk` is the row the game
    # names, also where AtkParam_Pc holds no such row (Ironeye's 402): that is
    # what tells "deals no damage" (-1) from "comes from a projectile this
    # program does not read" (AD-056.5).
    arts_name = text.get("ArtsName", {})
    arts = []
    for r in table("SwordArtsParam").rows:
        name = (arts_name.get(r.values.get("textId")) or "").strip()
        if not name:
            continue
        fp = r.values.get("useMagicPoint_L2", -1)
        fp_follow_up = max(r.values.get("useMagicPoint_R1", -1),
                           r.values.get("useMagicPoint_R2", -1))
        atk_id = r.values.get("atkParamId", -1)
        atk_row = atk_by_id.get(atk_id)
        flat: dict[str, int] = {}
        motion: dict[str, int] = {}
        element_correct_id = -1
        inflicts = {}
        if atk_row is not None:
            inflicts = hit_inflicts(hit_sp_ids(atk_row))
            element_correct_id = atk_row.values.get(
                ART_ELEMENT_CORRECT_FIELD, -1)
            flat = {damage: atk_row.values[field]
                    for damage, field in SPELL_DAMAGE_FIELDS.items()
                    if atk_row.values.get(field, 0) > 0}
            if not flat:
                motion = {damage: atk_row.values[field]
                          for damage, field in ART_MOTION_FIELDS.items()
                          if atk_row.values.get(field, 0) > 0}
        arts.append({
            "id": r.id,
            "name": name,
            "icon": r.values.get("iconId"),
            **({"fp": fp} if fp != -1 else {}),
            **({"fp_follow_up": fp_follow_up} if fp_follow_up > 0 else {}),
            **({"damage_atk": atk_id} if atk_id > 0 else {}),
            **({"motion_value": motion} if motion else {}),
            **({"damage": flat} if flat else {}),
            # The attribute scaling the hit uses in place of the armament's
            # (AD-056 P.7.2); absent where the art keeps the armament's.
            **({"element_correct_id": element_correct_id}
               if element_correct_id != -1 else {}),
            # Status buildup of the row the art names; absent where none.
            # Hoarfrost Stomp's frost is not on it (01.11.2026).
            **({"inflicts": inflicts} if inflicts else {}),
        })

    # ---- What an effect only sets off: its buff rows and its own hit -------
    # Here and not in register_effect, because half the links run through the
    # bullet and attack tables read above. A SpEffect row's behaviorId names a
    # Behavior row, that row a bullet (refType 1), and the bullet either hits
    # for an AtkParam row -- "Multiple Periodical Glintblades" is Magic 60 --
    # or lays a SpEffect on whoever it touches, which is how every aura hands
    # out its number. The player's table is asked first; the four "... Follows
    # Charge Attacks that Land" rows are only in the NPC ones (910610300).
    behavior_ref: dict[int, tuple[int, int]] = {}
    for _member in ("BehaviorParam", "BehaviorParam_PC"):   # the PC row wins
        for _r in param.read(members[_member], behavior_def).rows:
            behavior_ref[_r.id] = (_r.values.get("refType"),
                                   _r.values.get("refId"))
    _npc_atk = {
        r.id: r for r in param.read(
            members["AtkParam_Npc"],
            only(atk_def, {*SPELL_DAMAGE_FIELDS.values(),
                           *HIT_SP_EFFECT_FIELDS})).rows
    }

    @functools.lru_cache(maxsize=None)
    def behavior_reach(behavior_id: int) -> tuple[tuple, tuple]:
        """(attack rows, SpEffect ids laid on what is touched) of a behaviour."""
        ref_type, ref_id = behavior_ref.get(behavior_id, (None, None))
        if not isinstance(ref_id, int) or ref_id <= 0:
            return (), ()
        atk_rows: list = []
        laid: list[int] = []
        seen_bullets: set[int] = set()

        def follow(bullet_id, depth: int) -> None:
            if (not isinstance(bullet_id, int) or bullet_id <= 0
                    or bullet_id in seen_bullets or depth > MAX_BULLET_DEPTH):
                return
            seen_bullets.add(bullet_id)
            bullet = bullet_by_id.get(bullet_id)
            if bullet is None:
                return
            atk_id = bullet.values.get("atkId_Bullet", -1)
            atk_rows.append(atk_by_id.get(atk_id) or _npc_atk.get(atk_id))
            laid.extend(hit_sp_ids(bullet))
            follow(bullet.values.get("HitBulletID", -1), depth + 1)
            follow(bullet.values.get(BULLET_INTERVAL_FIELD, -1), depth + 1)

        if ref_type == BEHAVIOR_REF_BULLET:
            follow(ref_id, 0)
        elif ref_type == BEHAVIOR_REF_ATTACK:
            atk_rows.append(atk_by_id.get(ref_id) or _npc_atk.get(ref_id))
        atk_rows = [row for row in atk_rows if row is not None]
        for atk_row in atk_rows:
            laid.extend(hit_sp_ids(atk_row))
        return tuple(atk_rows), tuple(
            s for s in laid if isinstance(s, int) and s > 0)

    def laid_by(behavior_id: int) -> list[int]:
        """What a behaviour's bullets lay on allies: nothing where one of
        them deals damage, because that bullet touches the enemy, and
        "[Guardian] Successful guards send out shockwaves" would read as
        costing the wearer HP (7033405, on a Physical 100 hit)."""
        atk_rows, laid = behavior_reach(behavior_id)
        for atk_row in atk_rows:
            if any(isinstance(atk_row.values.get(field), int)
                   and atk_row.values[field] > PROC_DAMAGE_FLOOR
                   for field in SPELL_DAMAGE_FIELDS.values()):
                return []
        return list(laid)

    for _effect in effects.values():
        _sp_ids = _effect["sp_effect_ids"]
        # Absent where the effect already carries one of these numbers
        # itself: the state and adjacent payloads have then merged the same
        # rows into "modifiers", and listing them twice would read as two
        # buffs.
        if not (set(_effect["modifiers"]) & TRIGGERED_FIELDS):
            _fired = triggered_rows(
                _sp_ids, sp_values, gated_ids, owned_sp_ids, sp_baseline,
                laid_by)
            # A flask effect's rows hang on no link at all (`FLASK_ROWS`).
            for _sp_id in _sp_ids:
                _fired = _fired or flask_rows(
                    (sp_values.get(_sp_id) or {}).get("stateInfo") or 0,
                    sp_values)
            if _fired:
                _effect["triggered"] = _fired

        # The effect's own hit: strongest single one per damage type, as a
        # spell's is, and the buildup its hits lay on what they touch.
        _best: dict[str, int] = {}
        _laid: list[int] = []
        for _sp_id, _depth, _values in effect_rows(
                _sp_ids, sp_values, gated_ids, owned_sp_ids,
                laid_by):
            _behavior = _values.get("behaviorId") or 0
            if _behavior <= 0:
                continue
            _atk_rows, _hit_sp = behavior_reach(_behavior)
            _laid.extend(_hit_sp)
            for _atk_row in _atk_rows:
                _hit = {
                    damage: _atk_row.values[field]
                    for damage, field in SPELL_DAMAGE_FIELDS.items()
                    if isinstance(_atk_row.values.get(field), int)
                    and _atk_row.values[field] > PROC_DAMAGE_FLOOR
                }
                if sum(_hit.values()) > sum(_best.values()):
                    _best = _hit
        if _best:
            _effect["proc_damage"] = _best
        _buildup = hit_inflicts(_laid)
        if _buildup:
            _effect["proc_inflicts"] = _buildup

    # ---- Chances the engine keeps in PlayerCommonParam's undescribed tail --
    # PlayerCommonParam's row is 760 bytes and its paramdef describes only the
    # first 392, so these sit inside the row but past everything the def names.
    # That is why they were previously reported as "not in the params": no
    # field-name search could reach them.
    #
    # The offsets are not guesses. nightreign.exe reads the same struct in 289
    # places, and those reads land on the def's own named fields at their own
    # offsets -- including the blood and madness resist-recover rates this
    # project had already confirmed. Offset 0x2dc is loaded at 0x14043d5d0 and
    # compared against a roll of 0..99, so it is a percentage.
    player_common = members["PlayerCommonParam"]
    _pc_base = struct.unpack_from("<Q", player_common, 0x48)[0]

    def _pc_s32(offset: int) -> int:
        return struct.unpack_from("<i", player_common, _pc_base + offset)[0]

    ENGINE_CHANCES = {
        # "Occasionally Nullify Attacks When Damage Negation is Lowered"
        7037800: 0x2DC,
    }
    for effect_id, offset in ENGINE_CHANCES.items():
        key = str(effect_id)
        if key in effects:
            effects[key]["modifiers"]["procChancePercent"] = _pc_s32(offset)

    # ---- The stat-swap relics: numbers that are not in SpEffectParam ------
    # Twenty effects read "[Nightfarer] Improved X, Reduced Y" and their
    # SpEffect rows carry no numbers at all -- 7641000 "[Guardian] Improved
    # Strength and Dexterity, Reduced Vigor" holds nothing but stateInfo 2123
    # and a gate on state 2249. Neither a state payload nor an adjacent row
    # exists for any of the twenty, so the effect reached the planner as a
    # bare gated marker: parked under Conditional & situational, moving no
    # attribute, for something that is in fact on the whole time.
    #
    # The numbers are in HeroStatusParam instead, in a second family of blocks
    # the base stats never touch. Blocks 300..309 run parallel to the ten
    # Nightfarers -- 301 is Guardian, whose base block is 20 -- and each holds
    # two variants, 30N000/30N001 and 30N100/30N101, matching the two swap
    # relics each Nightfarer has. The rows are *deltas*, not stats, stored in
    # the same u8 fields, so a reduction wraps: statVigor 255 is -1.
    #
    # The pairing is not asserted, it is checked. For all 20 of 20 the sign of
    # every non-zero delta agrees with the effect's own name -- every stat
    # named after "Improved" comes out positive, every stat after "Reduced"
    # negative, and no stat moves that the name does not mention. A wrong
    # block assignment could not survive that, and any effect that fails it is
    # dropped here rather than shipped with a number that might be another
    # Nightfarer's.
    #
    # Anchors are levels 1 and 12 only, against the base stats' 1/2/12/15, so
    # the ladder is clamped above 12 rather than extrapolated.
    SWAP_STATE = 2123
    SWAP_BLOCK_BASE = 300
    _swap_family = sorted(
        r.id for r in speffect.rows if r.values.get("stateInfo") == SWAP_STATE
    )

    def _signed_u8(value: int) -> int:
        return value - 256 if value >= 128 else value

    def _swap_anchors(block: int, variant: int) -> dict[str, dict[str, int]]:
        out: dict[str, dict[str, int]] = {}
        prefix = (block * 1000 + variant * 100) // 100
        for row in hero_status.rows:
            if row.id // 100 != prefix:
                continue
            deltas = {
                label: _signed_u8(row.values[key])
                for key, label in STAT_FIELDS
                if _signed_u8(row.values.get(key, 0)) != 0
            }
            out[str(row.values["totalLevel"])] = deltas
        return out

    def _named_stats(name: str) -> tuple[set[str], set[str]]:
        """The stats the effect's own name says go up, and the ones it says down."""
        labels = [label for _key, label in STAT_FIELDS]
        up_text, _, down_text = name.partition("Reduced")
        pick = lambda text_: {s for s in labels if re.search(rf"\b{s}\b", text_)}
        return pick(up_text), pick(down_text)

    _hero_id_by_name = {h["name"]: h["id"] for h in heroes}
    # The effect that owns each of the family's SpEffect rows, found through
    # the effect's own sp_effect_ids rather than by an id arithmetic that only
    # happens to hold.
    _effect_by_sp: dict[int, Any] = {}
    for _entry in effects.values():
        for _sp in _entry.get("sp_effect_ids") or ():
            _effect_by_sp.setdefault(_sp, _entry)

    _rank_by_hero: dict[str, int] = {}
    for _sp_id in _swap_family:
        _effect = _effect_by_sp.get(_sp_id)
        if _effect is None:
            continue
        # AttachEffectParam's allow* flags cover the base eight Nightfarers
        # only, so Scholar's and Undertaker's rows come back with no owner at
        # all. Their names still carry it -- every one of the twenty begins
        # "[Nightfarer]" -- and the sign check below is what actually keeps a
        # wrong owner from shipping, so the name is a safe fallback.
        _allowed = _effect.get("allowed_heroes") or []
        if not _allowed:
            _bracket = re.match(r"\s*\[(.+?)\]", str(_effect.get("name", "")))
            _allowed = [_bracket.group(1)] if _bracket else []
        if len(_allowed) != 1 or _allowed[0] not in _hero_id_by_name:
            continue
        _hero = _allowed[0]
        _variant = _rank_by_hero.get(_hero, 0)
        _rank_by_hero[_hero] = _variant + 1
        if _variant > 1:
            continue
        _block = SWAP_BLOCK_BASE + _hero_id_by_name[_hero] - 1
        _anchors = _swap_anchors(_block, _variant)
        if not _anchors:
            continue

        _name = " ".join(str(_effect["name"]).split())
        _up, _down = _named_stats(_name)
        _top = _anchors[max(_anchors, key=int)]
        if ({s for s, v in _top.items() if v > 0} != _up
                or {s for s, v in _top.items() if v < 0} != _down):
            continue

        _effect["attribute_swap"] = _anchors
        _effect["attribute_swap_source"] = f"HeroStatusParam {_block}xxx"
        # The gate is what parked this under Conditional & situational. State
        # 2249 is set by exactly one row, 7999010, which itself carries nothing
        # and is referenced by nothing -- so the params say nothing about when
        # it holds. Reported in game as permanently active, which is also what
        # a relic that rewrites your starting stats has to be. The gate is
        # therefore dropped rather than left to hide the effect.
        _effect["modifiers"].pop("invocationConditionsStateChange1", None)

    # ---- Bosses and Deep of Night ----------------------------------------
    menu_text = text.get("CL_MenuText", {})
    bosses = _bosses(members, defs, menu_text, game_dir)
    # A failure here costs the sub-bosses and nothing else, the same trade
    # `_bosses` makes for the weakness block: both read the map files, and
    # neither is worth the whole snapshot.
    subbosses: dict[str, Any] = {}
    try:
        subbosses = _subbosses(members, defs, text, archives, sp_by_id)
    except Exception as exc:  # noqa: BLE001
        # The class name and not the exception's own text, which is
        # Windows' to word and in Windows' language (A8,
        # tests/test_exception_text_is_english.py).
        failed = exc.__class__.__name__
        print(f"   sub-bosses unavailable: {failed}")
    deep_of_night = _deep_of_night(members, defs, menu_text, text, subbosses)
    world_events = _world_events(members, defs, text)

    return {
        "meta": {
            "extract_version": EXTRACT_VERSION,
            "regulation_sha256": hashlib.sha256(reg_path.read_bytes()).hexdigest(),
            "regulation_size": reg_path.stat().st_size,
            "data_version": data_version,
            "game_dir": str(game_dir),
            "hero_count": len(heroes),
            "relic_count": len(relics),
            "deep_relic_count": sum(1 for r in relics if r["is_deep"]),
            "chalice_count": len(vessels),
            "effect_count": len(effects),
            "weapon_count": len(weapons),
            "boss_count": len(bosses),
            "world_event_count": len(world_events["events"]),
            "note": (
                "Stats for levels other than the game's explicit anchor levels "
                "are linearly interpolated and cut off to a whole number."
            ),
        },
        "curves": curves,
        "calc_curves": all_curves,
        "weapons": weapons,
        "spells": spells,
        "arts": arts,
        "weapon_families": weapon_families,
        "spell_families": spell_families,
        "reinforce": reinforce,
        "element_correct": element_correct,
        # What "no effect" looks like for each SpEffect field, taken as the
        # modal value across all 13,472 rows. This is what says whether a
        # number multiplies or adds, and it is derived rather than assumed:
        #   baseline 1.0  -> a multiplier; 1.07 means +7%
        #   baseline 0.0  -> an additive amount; 0.2 means +0.2, or +20% for
        #                    the fields whose name ends in Rate
        #   baseline -1   -> a sentinel, not a quantity at all
        # Reading an additive field as a multiplier is what made "Improved
        # Item Discovery" show -60%: itemDropRate sits at 0.0 when nothing
        # touches it, so 0.2 is +20%, not x0.2.
        "field_baselines": {
            name: value for name, value in sp_baseline.items()
            if isinstance(value, (int, float)) and not isinstance(value, bool)
        },
        "heroes": heroes,
        "vessels": vessels,
        "relics": relics,
        "effects": effects,
        "bosses": bosses,
        "subbosses": subbosses,
        "deep_of_night": deep_of_night,
        "world_events": world_events,
    }


def write_snapshot(game_dir: pathlib.Path, defs_dir: pathlib.Path, out: pathlib.Path) -> dict:
    data = build(game_dir, defs_dir)
    out.parent.mkdir(parents=True, exist_ok=True)
    # Written beside `out` and swapped in whole, so an interrupted write
    # leaves the previous snapshot rather than half a file.
    partial = out.with_name(out.name + ".partial")
    try:
        partial.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
        os.replace(partial, out)
    except BaseException:
        partial.unlink(missing_ok=True)
        raise
    return data
