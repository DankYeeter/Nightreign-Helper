"""Link each Nightlord to its characters, and so to its resistances.

Nothing in regulation.bin connects the boss menu to an NpcParam row. The
connection exists, but it runs through two files the planner did not read
before:

    NightBossMenuParam.defeatEventFlag
      -> EMEVD 2000[0], which starts the boss event with (flag, entity id)
      -> MSB PARTS_PARAM_ST, where that entity is attached to a placed part
      -> the part's cNNNN model and its NpcParam row
      -> damage cut rates and status resistances

Two details make this work rather than nearly work. Part name offsets are
relative to the record and their terminator has to be found on an even
boundary, or every name decodes to garbage. And a multi-part boss hangs the
flag on whichever half the script watches -- Gnoster's flag sits on entity
...827 -- so the whole entity block is collected, not just the flagged one.

Directions of the two field groups, both settled from the data:
  *DamageCutRate  0.0-2.0, mode 1.0. A damage MULTIPLIER: 2.0 takes double,
                  0.0 is immune. Higher means weaker. The 0.0 rows settle it;
                  as a reduction fraction 0.0 would mean "no reduction", which
                  nothing would pair with resistances on the same row.
  resist_*        0-999. Buildup resistance, 999 = immune (the commonest
                  value), 0 = none. Lower means weaker.
"""

from __future__ import annotations

import struct
from typing import Any

from . import bnd4, dvdbnd, oodle, param, tae

INSTRUCTION_RECORD = 32

DAMAGE_FIELDS = {
    "neutralDamageCutRate": "Standard",
    "slashDamageCutRate": "Slash",
    "blowDamageCutRate": "Strike",
    "thrustDamageCutRate": "Pierce",
    "magicDamageCutRate": "Magic",
    "fireDamageCutRate": "Fire",
    "thunderDamageCutRate": "Lightning",
    "darkDamageCutRate": "Holy",
}
STATUS_FIELDS = {
    "resist_poison": "Poison",
    "resist_desease": "Scarlet Rot",
    "resist_blood": "Blood loss",
    "resist_sleep": "Sleep",
    "resist_madness": "Madness",
    "resist_freeze": "Frostbite",
}

NEUTRAL_CUT = 1.0
IMMUNE_RESIST = 999
# Characters that stand in every arena and are never the boss.
CREW = {0, 100, 1000, 100, 200}


def _utf16(buf: bytes, offset: int) -> str:
    """A UTF-16 name, terminated on an even boundary.

    Searching for a b"\\0\\0" without alignment lands a byte early on roughly
    half of these names and decodes the whole string one byte out.
    """
    out = bytearray()
    i = offset
    while i + 1 < len(buf) and buf[i : i + 2] != b"\0\0":
        out += buf[i : i + 2]
        i += 2
    return out.decode("utf-16-le", "replace")


def _param_section(blob: bytes, name: str) -> tuple[list[int], int]:
    """Entry offsets of one MSB section, located via its own name string."""
    needle = name.encode("utf-16-le") + b"\0\0"
    string_at = blob.find(needle)
    if string_at < 0:
        raise KeyError(name)
    header = blob.rfind(struct.pack("<Q", string_at), 0, string_at)
    if header < 0:
        raise KeyError(f"{name}: header pointer not found")
    base = header - 8
    count = struct.unpack_from("<I", blob, base + 4)[0]
    offsets = list(struct.unpack_from(f"<{count - 1}Q", blob, base + 16))
    return offsets[:-1], offsets[-1]


def _flag_entities(blob: bytes) -> dict[int, int]:
    """defeat flag -> entity id, from the event that initialises each boss."""
    (_events, _event_off, count, offset) = struct.unpack_from("<4Q", blob, 0x10)
    arg_base = offset + count * INSTRUCTION_RECORD

    out: dict[int, int] = {}
    for i in range(count):
        record = offset + i * INSTRUCTION_RECORD
        bank, index = struct.unpack_from("<II", blob, record)
        if (bank, index) != (2000, 0):
            continue
        size, arg_offset = struct.unpack_from("<Qq", blob, record + 8)
        if arg_offset < 0 or size < 16:
            continue
        args = blob[arg_base + arg_offset : arg_base + arg_offset + size]
        ints = struct.unpack_from(f"<{len(args) // 4}i", args)
        # (slot, eventId, flag, entity): a menu flag is small, an entity large.
        if len(ints) >= 4 and 100 <= ints[2] < 1000 and ints[3] > 1_000_000:
            out.setdefault(ints[2], ints[3])
    return out


def _map_of(entity: int) -> str:
    """Entity ids are mAA_BB prefixed, so the arena is implied by the id."""
    return f"m{entity // 1_000_000:02d}_{(entity // 10_000) % 100:02d}_00_00"


# A boss inferred from its arena rather than proven by an entity id has to
# clear both bars: tuned resistances (a flat profile is a prop, not a boss)
# and boss-scale HP (an arena is full of small adds).
INFERRED_MIN_SPREAD = 0.1
INFERRED_MIN_HP = 2000
# A group boss is identified by an arena being unusually full of one tuned
# character. Ten is well clear of the one-or-two an ordinary add gets, and
# well under Harmonia's twenty-one.
INFERRED_GROUP_MIN = 10


def _tuned(rows: list) -> bool:
    """Has someone deliberately set this character's resistances apart?"""
    profile = _profile(rows)
    if not profile:
        return False
    return (max(profile["damage"].values())
            - min(profile["damage"].values())) >= INFERRED_MIN_SPREAD


def _parts(blob: bytes) -> list[tuple[str, bytes]]:
    entries, end = _param_section(blob, "PARTS_PARAM_ST")
    bounds = entries + [end]
    out = []
    for i, start in enumerate(entries):
        record = blob[start : bounds[i + 1]]
        out.append((_utf16(record, struct.unpack_from("<Q", record, 0)[0]),
                    record))
    return out


# SpEffectParam 7330-7398 is a per-boss buff/debuff family: every row pairs an
# attack-power multiplier with a stance-damage-taken multiplier. Which row a
# boss uses is authored individually, so the band has to be read per boss
# rather than assumed. Confirmed against play in OPEN_QUESTIONS section 11 --
# the owner's list of which bosses show an attack up matched, including Maris,
# who has no row in the band at all.
LADDER = range(7330, 7399)

# A boss buffing its own defence is rare enough to be worth its own pass:
# Libra is the only one of the ten who does it. The attack ladder above lives
# in a fixed band, but a defence buff is authored wherever its author put it,
# so it is found by shape instead -- reduces every damage type, and runs for a
# stated time rather than being a permanent trait.
DAMAGE_CUTS = ("neutralDamageCutRate", "slashDamageCutRate",
               "blowDamageCutRate", "thrustDamageCutRate",
               "magicDamageCutRate", "fireDamageCutRate",
               "thunderDamageCutRate", "darkDamageCutRate")


def _tae(archives, chr_id: int) -> bytes | None:
    """The boss's TAE, or None. An unreadable anibnd costs that boss its
    ladder, never the whole snapshot."""
    path = f"/chr/c{chr_id}.anibnd.dcx"
    archive = next((a for a in archives.values() if path in a), None)
    if archive is None:
        return None
    try:
        return next((f.data for f in bnd4.read(archive.read(path))
                     if f.basename.lower().endswith(".tae")), None)
    except Exception:  # noqa: BLE001 - an unreadable anibnd is not fatal
        return None


def _defence_buffs(sp_rows: dict, reachable: set[int],
                   located: dict[int, set]) -> list[dict]:
    """Timed damage reduction a boss puts on itself."""
    out = []
    for sid in sorted(reachable):
        row = sp_rows.get(sid)
        if row is None:
            continue
        cuts = [row.values.get(f) for f in DAMAGE_CUTS
                if isinstance(row.values.get(f), (int, float))]
        duration = row.values.get("effectEndurance") or -1
        # All eight types, all reduced, and time-limited. A permanent cut is
        # the boss's base resistance profile and already shown elsewhere.
        if len(cuts) != len(DAMAGE_CUTS) or max(cuts) >= 0.99 or duration <= 0:
            continue
        entry = {"id": sid, "taken": round(float(max(cuts)), 3),
                 "seconds": round(float(duration), 1)}
        if sid in located:
            entry["from"] = [{"animation": anim, "at": round(at, 3)}
                             for anim, at in sorted(located[sid])]
        out.append(entry)
    return out


def _ladder(sp_rows: dict, reachable: set[int],
            located: dict[int, tuple[int, float]]) -> dict[str, list] | None:
    """The boss's attack-up / attack-down rows and where they come from.

    `located` maps a SpEffect to the animation that applies it and the time
    it fires, which is the part that says *when* a boss buffs itself. Several
    bosses -- Heolstor among them -- carry ladder rows with no animation
    behind them at all, so the field stays absent rather than guessed.
    """
    up, down = [], []
    for sid in sorted(reachable & set(LADDER)):
        row = sp_rows.get(sid)
        if row is None:
            continue
        atk = row.values.get("physicsAttackPowerRate")
        stance = row.values.get("saReceiveDamageRate")
        if not isinstance(atk, (int, float)) or abs(atk - 1.0) < 1e-6:
            continue
        entry = {"id": sid, "attack": round(float(atk), 3),
                 "stance_taken": (round(float(stance), 3)
                                  if isinstance(stance, (int, float)) else None)}
        # An effect can be applied from more than one animation -- Gladius's
        # buff comes off both 3025 and the taunt 20004 -- so all of them are
        # kept. Showing only the first read as "this is the move that does it".
        if sid in located:
            entry["from"] = [{"animation": anim, "at": round(at, 3)}
                             for anim, at in sorted(located[sid])]
        (up if atk > 1.0 else down).append(entry)
    if not up and not down:
        return None
    return {"up": up, "down": down}


def _profile(rows: list[param.ParamRow]) -> dict[str, Any] | None:
    """The weakness picture for one character."""
    if not rows:
        return None
    best = max(rows, key=lambda r: r.values.get("hp") or 0)
    damage = {label: best.values.get(field)
              for field, label in DAMAGE_FIELDS.items()
              if isinstance(best.values.get(field), (int, float))}
    status = {label: best.values.get(field)
              for field, label in STATUS_FIELDS.items()
              if isinstance(best.values.get(field), (int, float))}
    if not damage:
        return None

    hardest = max(damage.values())
    softest = min(status.values()) if status else IMMUNE_RESIST

    # Body parts. weakPartsDamageRate is the bonus for hitting a designated
    # weak point; partsDamageRateN are per-part multipliers, so a value below
    # 1.0 is armour and above 1.0 a soft spot.
    weak_part = best.values.get("weakPartsDamageRate")
    part_rates = {
        f"Part {i}": round(float(best.values[f"partsDamageRate{i}"]), 3)
        for i in range(1, 9)
        if isinstance(best.values.get(f"partsDamageRate{i}"), (int, float))
        and abs(best.values[f"partsDamageRate{i}"] - 1.0) > 1e-6
    }
    # isWeakA..F are single-bit flags, separate from the per-part rates above
    # and set on only three of the ten. What body part each letter stands for
    # is NOT in the files -- the paramdef gives the fields no description and
    # the AI scripts only ever number parts (ANIME_ID_PART1_DAMAGE and so on).
    weak_flags = [letter for letter in "ABCDEF"
                  if best.values.get(f"isWeak{letter}")]
    # Stance. `superArmorDurability` is the size of the poise bar that has to
    # be emptied to break the boss, and `superArmorRecoverCorrection` scales
    # how fast it refills -- so a big bar that refills fast is a boss you
    # cannot stagger by chipping at it. Both vary per Nightlord where
    # weakPartsDamageRate does not, which is what makes them worth showing.
    # Reported raw. Nothing here says a weakness hit does extra stance damage:
    # no boss carries a `toughnessDamageCutRate`, and all 17 rows in the game
    # that do are elsewhere. See OPEN_QUESTIONS 5.13.
    stance = {
        key: round(float(best.values[field]), 3)
        for field, key in (("superArmorDurability", "bar"),
                           ("superArmorRecoverCorrection", "recovery"),
                           ("toughnessRecoverCorrection", "toughness_recovery"))
        if isinstance(best.values.get(field), (int, float))
    }
    return {
        "hp": best.values.get("hp"),
        "npc_row": best.id,
        "damage": damage,
        "status": status,
        "stance": stance,
        "weak_part_rate": (round(float(weak_part), 3)
                           if isinstance(weak_part, (int, float))
                           and abs(weak_part - 1.0) > 1e-6 else None),
        "part_rates": part_rates,
        "weak_flags": weak_flags,
        "parts_damage_type": best.values.get("partsDamageType"),
        # Whether a weak-point hit plays its own reaction. Six of the ten
        # Nightlords set this, and for those there is no visual feedback by
        # design -- which is why "hit it and watch" cannot identify a part on
        # them. 384 of 3016 NpcParam rows game-wide set it.
        "skips_weak_animation": bool(best.values.get("isSkipWeakDamageAnim")),
        # Only report a weakness where the game actually tuned one. A flat
        # profile means no designed weakness, and saying "weak to Standard"
        # because every rate is 1.0 would be an invention.
        "weak_damage": sorted(k for k, v in damage.items()
                              if v == hardest and v > NEUTRAL_CUT),
        "weak_status": sorted(k for k, v in status.items()
                              if v == softest and v < IMMUNE_RESIST),
        "resistant_to": sorted(k for k, v in damage.items()
                               if v < NEUTRAL_CUT),
    }


def derive(game_dir, members: dict, defs: dict,
           npc: param.ParamTable) -> dict[int, dict]:
    """defeat flag -> {entity, map, chars, profile} for every boss it can."""
    # The archives are Oodle-compressed; without this every read raises and
    # the whole chain silently resolves nothing.
    oodle.load(game_dir)
    archives = dvdbnd.open_all(game_dir)

    by_chr: dict[int, list] = {}
    npc_ids = {row.id for row in npc.rows}
    for row in npc.rows:
        by_chr.setdefault(row.id // 10000, []).append(row)

    boss = param.read(members["NightBossMenuParam"],
                      defs.get("NightBossMenuParam"))
    flags = {row.values.get("defeatEventFlag") for row in boss.rows}
    flags.discard(0)
    flags.discard(None)

    # Every event file, since the later bosses are not all in one arena.
    # Two things are collected: the exact (flag, entity) pair where the script
    # provides one, and otherwise just which script mentions the flag at all,
    # which still pins the arena.
    pairs: dict[int, int] = {}
    candidates: dict[int, list[tuple[int, str]]] = {}
    for name in _event_names(archives):
        path = f"/event/{name}"
        arc = next((a for a in archives.values() if path in a), None)
        if arc is None:
            continue
        try:
            blob = arc.read(path)
            found = _flag_entities(blob)
        except Exception:  # noqa: BLE001 - an unreadable script is not fatal
            continue
        for flag, entity in found.items():
            if flag in flags:
                pairs.setdefault(flag, entity)
        if name.startswith("m"):
            # Keep how many boss flags each script mentions. The hub script
            # lists every one of them for the menu, so first-mention-wins
            # would point every unresolved boss at the hub; an arena script
            # mentions only its own boss, which is what identifies it.
            found_flags = _flags_mentioned(blob, flags)
            for flag in found_flags:
                candidates.setdefault(flag, []).append(
                    (len(found_flags), name[: -len(".emevd.dcx")]))

    out: dict[int, dict] = {}
    parts_cache: dict[str, list[tuple[str, bytes]]] = {}
    for flag, entity in pairs.items():
        map_name = _map_of(entity)
        if map_name not in parts_cache:
            path = f"/map/mapstudio/{map_name}.msb.dcx"
            arc = next((a for a in archives.values() if path in a), None)
            if arc is None:
                parts_cache[map_name] = []
            else:
                try:
                    parts_cache[map_name] = _parts(arc.read(path))
                except Exception:  # noqa: BLE001
                    parts_cache[map_name] = []
        parts = parts_cache[map_name]
        if not parts:
            continue

        # A multi-part boss shares one block of ten entity ids.
        block = (entity // 10) * 10
        chars: list[int] = []
        rows_for: dict[int, list] = {}
        for name, record in parts:
            ints = struct.unpack_from(f"<{len(record) // 4}i", record, 0)
            if not any(block <= v <= block + 9 for v in ints):
                continue
            model = name.split("_")[0]
            if not (model.startswith("c") and model[1:].isdigit()):
                continue
            chr_id = int(model[1:])
            if chr_id in CREW or chr_id in chars:
                continue
            chars.append(chr_id)
            # The exact NpcParam row is named on the part itself: an int that
            # is a real row id and belongs to this character.
            exact = [v for v in ints
                     if v in npc_ids and v // 10000 == chr_id]
            rows_for[chr_id] = ([r for r in npc.rows if r.id in exact]
                                or by_chr.get(chr_id, []))

        if not chars:
            continue
        primary = max(chars,
                      key=lambda c: max((r.values.get("hp") or 0)
                                        for r in rows_for.get(c, [])) or 0)
        out[flag] = {
            "entity": entity,
            "map": map_name,
            "chars": chars,
            "primary": primary,
            "confidence": "exact",
            "profile": _profile(rows_for.get(primary, [])),
            "parts": {c: _profile(rows_for.get(c, [])) for c in chars},
        }

    # Bosses whose script names the flag but never pairs it with an entity.
    # The arena is still known, so the boss can be picked out of it -- but
    # that is an inference from "it is the only tuned, boss-scale character
    # in there", not the proven chain above, and it says so.
    for flag, options in candidates.items():
        if flag in out:
            continue
        # Fewest-flags-first, but try every candidate: the arena that names
        # only this boss is the best guess, not the only one worth opening.
        for _count, map_name in sorted(set(options)):
            path = f"/map/mapstudio/{map_name}.msb.dcx"
            arc = next((a for a in archives.values() if path in a), None)
            if arc is None:
                continue
            try:
                parts = _parts(arc.read(path))
            except Exception:  # noqa: BLE001
                continue

            seen: dict[int, list] = {}
            placements: dict[int, int] = {}
            for name, _record in parts:
                model = name.split("_")[0]
                if not (model.startswith("c") and model[1:].isdigit()):
                    continue
                chr_id = int(model[1:])
                if chr_id in CREW:
                    continue
                seen.setdefault(chr_id, by_chr.get(chr_id, []))
                placements[chr_id] = placements.get(chr_id, 0) + 1

            best, best_profile = None, None
            for chr_id, rows in seen.items():
                profile = _profile(rows)
                if not profile:
                    continue
                spread = (max(profile["damage"].values())
                          - min(profile["damage"].values()))
                if spread < INFERRED_MIN_SPREAD:
                    continue
                if (profile["hp"] or 0) < INFERRED_MIN_HP:
                    continue
                if best_profile is None or profile["hp"] > best_profile["hp"]:
                    best, best_profile = chr_id, profile

            # A group boss has no single boss-scale body. Harmonia is "seven
            # valkyries", and its arena places c7620 twenty-one times (seven
            # by three player-count variants) where every other map in the
            # game places it exactly once. So when nothing clears the HP bar,
            # fall back to the character this arena is unusually full of.
            group = False
            if best is None:
                crowd = [(n, c) for c, n in placements.items()
                         if n >= INFERRED_GROUP_MIN and _tuned(seen.get(c, []))]
                if crowd:
                    _n, chr_id = max(crowd)
                    best, best_profile = chr_id, _profile(seen[chr_id])
                    group = True
            if best is None:
                continue
            out[flag] = {
                "entity": None,
                "map": map_name,
                "chars": [best],
                "primary": best,
                "confidence": "inferred",
                "group_boss": group,
                "placements": placements.get(best),
                "profile": best_profile,
                "parts": {best: best_profile},
            }
            break

    # The buff/debuff ladder, attached in one pass so every confidence path
    # gets it. A boss reaches these rows either from an NpcParam slot or from
    # its own animations, and several use only the second route.
    sp_rows = {r.id: r for r in param.read(members["SpEffectParam"],
                                           defs.get("SpEffectParam")).rows}
    slots = [f"spEffectID{i}" for i in range(30)]
    for entry in out.values():
        chr_id = entry["primary"]
        reachable = {v for row in by_chr.get(chr_id, []) for s in slots
                     if (v := row.values.get(s, -1)) and v > 0}
        blob = _tae(archives, chr_id)
        located: dict[int, set[tuple[int, float]]] = {}
        if blob:
            for event in tae.applied_speffects(blob):
                reachable.add(event.param0)
                located.setdefault(event.param0, set()).add(
                    (event.animation, event.start))
        ladder = _ladder(sp_rows, reachable, located)
        if ladder and entry.get("profile"):
            entry["profile"]["ladder"] = ladder
        defence = _defence_buffs(sp_rows, reachable, located)
        if defence and entry.get("profile"):
            entry["profile"]["defence_buffs"] = defence
    return out


def _flags_mentioned(blob: bytes, flags: set[int]) -> set[int]:
    """Which of these flags appear anywhere in a script's arguments."""
    (_e, _eo, count, offset) = struct.unpack_from("<4Q", blob, 0x10)
    base = offset + count * INSTRUCTION_RECORD
    out: set[int] = set()
    for i in range(count):
        record = offset + i * INSTRUCTION_RECORD
        size, arg_offset = struct.unpack_from("<Qq", blob, record + 8)
        if arg_offset < 0 or size < 4:
            continue
        args = blob[base + arg_offset : base + arg_offset + size]
        for value in struct.unpack_from(f"<{len(args) // 4}i", args):
            if value in flags:
                out.add(value)
    return out


def _event_names(archives) -> list[str]:
    """Event scripts worth opening.

    Every mAA_BB, not just every tenth: the later bosses do not live in the
    round-numbered maps, and a missed script silently loses a boss.
    """
    names = ["common.emevd.dcx", "common_func.emevd.dcx"]
    for aa in range(10, 70):
        for bb in range(100):
            names.append(f"m{aa:02d}_{bb:02d}_00_00.emevd.dcx")
    return names
