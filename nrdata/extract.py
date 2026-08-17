"""Turn a Nightreign installation into a single self-contained data snapshot.

Everything here is derived from the user's own game files; the only external
inputs are the container keys and the PARAMDEF field schemas.
"""

from __future__ import annotations

import collections
import hashlib
import json
import pathlib
import re
import struct
from typing import Any

from . import bnd4, bossdata, dvdbnd, fmg, oodle, param, paramdef, regulation

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
EXTRACT_VERSION = 6

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

# Magic.spEffectCategory: verified against the spell names themselves --
# 3 holds Glintstone Pebble and Comet, 4 holds Catch Flame and O, Flame!
SPELL_CATEGORIES = {3: "Sorceries", 4: "Incantations"}

# Weapon types no relic buff names, read off from what they contain.
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


def _load_text(game_dir: pathlib.Path) -> dict[str, dict[int, str]]:
    """Load every FMG from the localised message archives.

    Base and expansion tables are merged under the base name, since every
    caller wants one lookup. Which ids came from the expansion is still worth
    knowing -- a player without the DLC will never see those lines -- so each
    table that has an expansion half also gets a `"<name>::dlc"` entry holding
    only that half. Nothing is lost and no existing key changes meaning.
    """
    oodle.load(game_dir)
    archives = dvdbnd.open_all(game_dir)

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

# The game's own name for the second group and for the mode, so neither label
# is invented here. 131040 = "Everdark Sovereign", 131150 = "The Deep of Night".
EVERDARK_LABEL_ID = 131040
DEEP_LABEL_ID = 131150

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


def _deep_of_night(members: dict, defs: dict, menu_text: dict[int, str],
                   text: dict[str, dict[int, str]]) -> dict:
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
    # - u16 at +6, where set, is a character id. c5011 resolves through
    #   NpcName to Golden Hippopotamus and c3400 to Grave Warden Duelist,
    #   and category 160's four are the arena bosses (Dragonkin Soldier,
    #   Guardian Golem, Ancestor Spirit, Fallingstar Beast) -- names landing
    #   on real enemies is not something a misaligned read produces.
    # - u32 at +12, where set (667 rows, exactly the rows with no character),
    #   reads 604|XX|YY with XX 42-45 and YY 36-39 -- the Limveld tile grid,
    #   so those kinds are scoped to map areas rather than to enemies.
    #
    # Character names here are the game's own (NpcParam.nameId -> NpcName).
    # Most common enemies are never named by the game at all, so most
    # entries carry only the id; community names stay in the tab's tinted
    # layer, outside this snapshot.
    npc_table = param.read(members["NpcParam"], defs.get("NpcParam"))
    npc_names = text.get("NpcName", {})
    chr_names: dict[int, str] = {}
    # Two routes to a name, both the game's own. The structured NpcName id
    # (90 <4-digit character> <3-digit variant>, section 6e) covers enemies
    # whose NpcParam rows never made it into the table; nameId covers the
    # rest. The structured route runs first because it is keyed by the
    # character itself rather than by whichever row happened to be seen.
    for name_id, label in npc_names.items():
        if 900000000 <= name_id <= 909999999 and label and label.strip():
            chr_names.setdefault((name_id - 900000000) // 1000, label.strip())
    for row in npc_table.rows:
        label = (npc_names.get(row.values.get("nameId", -1)) or "").strip()
        if label:
            chr_names.setdefault(row.id // 10000, label)

    kinds: dict[int, dict] = {}
    enemy_table = param.read(
        members["ChaosMatchingMutationEnemyTableParam"],
        defs.get("ChaosMatchingMutationEnemyTableParam"))
    for row in enemy_table.rows:
        values = row.values
        category = values["categoryId"]
        # The def calls this `smallBaseId`, and that name is wrong: the
        # values run 2000-5391 while SmallBaseAndSpotDefine holds 107 rows
        # in 100-2219, so only 2 of 116 would resolve. As characters they
        # resolve into real, thematically correct names -- c5011 Golden
        # Hippopotamus, the four arena bosses under one kind -- which is
        # what a correct read looks like. Structure from the def, meaning
        # from the data.
        target = values["smallBaseId"]
        # Likewise `mapUnk_1/2/3`, which the def leaves unnamed: read as one
        # little-endian u32 the field is packed decimal 60|XX|YY, giving the
        # 4x4 grid of real m60_4X_3Y Limveld tiles. The def's byte split
        # produces (76, 56, 9), which names nothing.
        tile = (values["mapUnk_1"] | (values["mapUnk_2"] << 8)
                | (values["mapUnk_3"] << 16))
        kind = kinds.setdefault(
            category, {"rows": 0, "chrs": {}, "tiles": set()})
        kind["rows"] += 1
        if target:
            kind["chrs"][target] = kind["chrs"].get(target, 0) + 1
        elif tile:
            kind["tiles"].add(f"m60_{tile // 100 % 100}_{tile % 100}")
    for kind in kinds.values():
        kind["chrs"] = [
            {"chr": chr_id, "rows": count, "name": chr_names.get(chr_id)}
            for chr_id, count in sorted(kind["chrs"].items(),
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
    control_size = 0

    # TutorialBody 403500, "The Deep of Night: Depth and Rating" -- the game's
    # own statement of the rating bands behind each Depth.
    # The tutorial strings carry inline gamepad/image markup like
    # "<?image@4500##17?>", which is a button glyph the app cannot render.
    sigil_name = (text.get("AntiqueName", {}).get(SOVEREIGN_SIGIL_ID) or "").strip()
    sigil_info = (text.get("AntiqueInfo", {}).get(SOVEREIGN_SIGIL_ID) or "").strip()

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
    if values.get("stateInfo") == 600:
        lines.append("invulnerable")
    return lines


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
            # -1 means no timer at all: it lasts the rest of the expedition.
            "duration": root.get("effectEndurance"),
            # None means the files do not say. See the docstring: the
            # effectTarget* flags cannot answer this.
            "shares_with_allies": _states_allies(info.get(row.id) or ""),
            "fires_at": root.get("accumuOverVal") or None,
            "lines": _buff_lines(root),
            # A buff whose magnitude lives on a *separate* row applied on a
            # trigger, not on the marker itself. Traces of Grace-Given Lord is
            # the case that matters: graceSpEffectId is what a new Site of
            # Grace applies, and that row is where the +2% actually is.
            "per_trigger": _buff_lines(
                sp_rows.get(row.values.get("graceSpEffectId"), {})),
            "parts": parts,
        })
    out.sort(key=lambda b: b["id"])
    return out


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
            "duration": row.values.get("effectEndurance"),
            "lines": lines,
            "shares_with_allies": _states_allies(label),
        })
    return out


# NpcName ids are structured `90 <4-digit character> <3-digit variant>` --
# 907540001 is c7540's first named form. That is what lets a creature's name
# reach its NpcParam rows, and therefore its rune value. Worth knowing that
# this is the very link that does NOT exist for the Nightlords (section 6c:
# their names live in CL_MenuText, and no NpcParam row carries a boss nameId);
# ordinary and event enemies are named the normal way.
NPC_NAME_PREFIX = 90


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
                key = name_of(category, item_id)
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
                    key = name_of(category, item_id)
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
            entries.append({"name": name, "kind": kind, "share": share})
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
    rates = [r.values["SoulRate"] for r in clear.rows if r.values.get("SoulRate")]
    if rates:
        lines.append(
            "Expeditions completed: ClearCountCorrectParam.SoulRate runs "
            + " → ".join(f"×{r:g}" for r in sorted(rates))
            + ", so a well-progressed profile earns more from the same kill.")

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
    members = {
        f.basename[: -len(".param")]: f.data for f in regulation.load_params(reg_path)
    }

    def table(name: str) -> param.ParamTable:
        return param.read(members[name], defs.get(name))

    text = _load_text(game_dir)
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

    # ---- SpEffect: work out which fields an effect actually changes --------
    sp_def = defs["SpEffectParam"]
    numeric_fields = [
        f.name
        for f in sp_def.fields
        if f.type in ("f32", "s32", "u32", "s16", "u16", "u8", "s8")
        and f.count == 1
        and not f.name.startswith("unknown")
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
            for name in sp_baseline:
                value = r.values.get(name)
                if (value is not None
                        and not isinstance(value, list)
                        and value != sp_baseline[name]):
                    out.setdefault(name, value)
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

    # Status buildup applied by an effect, once the chain is followed. These
    # are the payload at the end of every "Taking Damage Causes X Buildup"
    # curse: the curse row itself is empty, three hops later sits the number.
    STATUS_POWER = {
        "poizonAttackPower": "Poison",
        "diseaseAttackPower": "Scarlet Rot",
        "bloodAttackPower": "Blood Loss",
        "freezeAttackPower": "Frost",
        "sleepAttackPower": "Sleep",
        "madnessAttackPower": "Madness",
        "curseAttackPower": "Death Blight",
    }

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
    for row in hero_param.rows:
        init = init_by_id.get(STARTING_ROW_BASE + row.id - 1)
        if init is None:
            continue
        weapon_id = init.values.get("equip_Wep_Right_1", -1)
        if isinstance(weapon_id, int) and weapon_id > 0:
            starting_weapon[row.id] = weapon_id

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

        levels: dict[int, dict[str, int]] = {}
        exact = {a.values["totalLevel"] for a in anchors}
        for lvl in range(1, MAX_LEVEL + 1):
            lo = max([a for a in anchors if a.values["totalLevel"] <= lvl], key=lambda a: a.values["totalLevel"], default=anchors[0])
            hi = min([a for a in anchors if a.values["totalLevel"] >= lvl], key=lambda a: a.values["totalLevel"], default=anchors[-1])
            lo_lvl, hi_lvl = lo.values["totalLevel"], hi.values["totalLevel"]
            span = hi_lvl - lo_lvl
            t = 0.0 if span == 0 else (lvl - lo_lvl) / span
            levels[lvl] = {
                label: round(lo.values[key] + (hi.values[key] - lo.values[key]) * t)
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
        on_hit_ids = [modifiers.get(ATTACK_CHAIN_FIELD)]
        on_hit_ids += [sp_by_id[i].values.get(ATTACK_CHAIN_FIELD)
                       for i in sp_ids if i in sp_by_id]
        inflicts_on_hit: dict[str, Any] = {}
        for nxt in on_hit_ids:
            if isinstance(nxt, int) and nxt > 0:
                for label, value in follow_chain(nxt).items():
                    inflicts_on_hit.setdefault(label, value)

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
    CUSTOM_POOL_FIELDS = ("attachEffectTableId_1", "attachEffectTableId_2",
                          "attachEffectTableId_3")
    custom_weapon = table("EquipParamCustomWeapon")
    weapon_pool_ids: dict[int, set[int]] = collections.defaultdict(set)
    weapon_skill_pools: dict[int, set[int]] = collections.defaultdict(set)
    for r in custom_weapon.rows:
        target = r.values.get("targetWeaponId", -1)
        if not isinstance(target, int) or target <= 0:
            continue
        for field_name in CUSTOM_POOL_FIELDS:
            pool = r.values.get(field_name, -1)
            if isinstance(pool, int) and pool > 0:
                weapon_pool_ids[target].add(pool)
        skill = r.values.get("swordArtsTableId", -1)
        if isinstance(skill, int) and skill > 0:
            weapon_skill_pools[target].add(skill)

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

    weapons = []
    for r in weapon_table.rows:
        name = weapon_name.get(r.id)
        if not name or not name.strip():
            continue
        bases = {d: r.values.get(f"attackBase{d}", 0) for d in DAMAGE_TYPES}
        if not any(bases.values()):
            continue
        weapons.append(
            {
                "id": r.id,
                "name": name.strip(),
                "icon": r.values.get("iconId"),
                "weight": r.values.get("weight"),
                "wep_type": r.values.get("wepType"),
                "rarity": r.values.get("rarity", 0),
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
                "requires": {
                    "Strength": r.values.get("properStrength", 0),
                    "Dexterity": r.values.get("properAgility", 0),
                    "Intelligence": r.values.get("properMagic", 0),
                    "Faith": r.values.get("properFaith", 0),
                    "Arcane": r.values.get("properLuck", 0),
                },
                "reinforce_type": r.values.get("reinforceTypeId", 0),
                "element_correct_id": r.values.get("attackElementCorrectId"),
                # Effects this weapon can roll, from its own pools. Empty for
                # the armaments that roll nothing.
                "effect_pool": weapon_effect_pool(r.id),
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

    spells = []
    for r in magic_table.rows:
        name = magic_name.get(r.id)
        if not name or not name.strip():
            continue
        category = SPELL_CATEGORIES.get(r.values.get("spEffectCategory"))
        if category is None:
            continue
        sub = r.values.get("subCategory1")
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
            }
        )

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
    _pc_row = param.read(player_common, None)
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
    deep_of_night = _deep_of_night(members, defs, menu_text, text)
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
                "are linearly interpolated."
            ),
        },
        "curves": curves,
        "calc_curves": all_curves,
        "weapons": weapons,
        "spells": spells,
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
        "deep_of_night": deep_of_night,
        "world_events": world_events,
    }


def write_snapshot(game_dir: pathlib.Path, defs_dir: pathlib.Path, out: pathlib.Path) -> dict:
    data = build(game_dir, defs_dir)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    return data
