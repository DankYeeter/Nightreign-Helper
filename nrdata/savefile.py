"""Nightreign save file (.sl2) reader.

The container is a plain BND4 whose members are individually AES-CBC encrypted
with a static key, the IV being the member's own first 16 bytes.
"""

from __future__ import annotations

import hashlib
import os
import pathlib
import struct
from dataclasses import dataclass, field

from Crypto.Cipher import AES

# Static save key, shared by Dark Souls 3 and Elden Ring.
SAVE_KEY = bytes([
    0x18, 0xF6, 0x32, 0x66, 0x05, 0xBD, 0x17, 0x8A,
    0x55, 0x24, 0x52, 0x3A, 0xC0, 0xA0, 0xC6, 0x09,
])


@dataclass
class SaveSlot:
    index: int
    name: str
    raw: bytes           # encrypted member as stored
    data: bytes          # decrypted payload, checksum stripped
    checksum_ok: bool


def _members(blob: bytes) -> list[tuple[int, str, int, int]]:
    """Yield (index, name, offset, size) for each BND4 member."""
    if blob[:4] != b"BND4":
        raise ValueError("not a BND4 save container")

    file_count = struct.unpack_from("<I", blob, 0x0C)[0]
    file_header_size = struct.unpack_from("<Q", blob, 0x20)[0]
    unicode_names = blob[0x30] != 0

    out = []
    for i in range(file_count):
        base = 0x40 + i * file_header_size
        # Read off the real file: u32 flags, i32 -1, u64 size, u32 offset,
        # u32 name offset, then padding.
        size = struct.unpack_from("<Q", blob, base + 8)[0]
        offset = struct.unpack_from("<I", blob, base + 16)[0]
        name_offset = struct.unpack_from("<I", blob, base + 20)[0]

        name = f"slot_{i}"
        if name_offset and name_offset < len(blob):
            end = name_offset
            if unicode_names:
                while blob[end : end + 2] != b"\0\0":
                    end += 2
                name = blob[name_offset:end].decode("utf-16-le", "replace")
            else:
                end = blob.index(b"\0", name_offset)
                name = blob[name_offset:end].decode("shift-jis", "replace")

        out.append((i, name, offset, size))
    return out


def decrypt_member(blob: bytes, key: bytes = SAVE_KEY) -> tuple[bytes, bool]:
    """Decrypt one member and verify its trailing MD5 checksum."""
    iv, body = blob[:16], blob[16:]
    body = body[: len(body) // 16 * 16]
    plain = AES.new(key, AES.MODE_CBC, iv).decrypt(body)

    # Layout: u32 payload length, payload, 16-byte MD5 of the payload.
    (length,) = struct.unpack_from("<I", plain, 0)
    if not (0 < length <= len(plain) - 20):
        return plain, False

    payload = plain[4 : 4 + length]
    stored = plain[4 + length : 4 + length + 16]
    return payload, hashlib.md5(payload).digest() == stored


def read(path: pathlib.Path | str, key: bytes = SAVE_KEY) -> list[SaveSlot]:
    blob = pathlib.Path(path).read_bytes()
    slots = []
    for index, name, offset, size in _members(blob):
        raw = blob[offset : offset + size]
        data, ok = decrypt_member(raw, key)
        slots.append(SaveSlot(index, name, raw, data, ok))
    return slots


# Inventory ids are stored with this category bit set.
RELIC_ID_FLAG = 0x80000000

# Record layout, relative to the relic id:
#   -4  the relic's handle, 0xC08000NN -- see HANDLE_OFFSET
#   +0  relic id | flag
#   +4  same id again
#   +8  0xffffffff
#   +12 / +16 / +20   the three rolled effect ids (-1 when the slot is empty)
#   +52 / +56 / +60   the rolled curses, same encoding
EFFECT_OFFSETS = (12, 16, 20)

# Every relic instance has a handle, and the equipped-loadout table references
# relics by handle rather than by id. It sits immediately BEFORE the doubled id,
# so the record really begins at -4.
#
# An earlier reading put it at +76. That is the same byte whenever records are
# contiguous at stride 80, so it silently reads the *next* relic's handle -- and
# 272 of 275 records here are contiguous, which is why it looked right. Three
# things say -4 is correct and +76 is not:
#   * -4 gives 275 distinct, well-formed handles; +76 gives 273 and two zeroes,
#     the zeroes being the two records that follow a gap;
#   * every equipped relic then satisfies its vessel's own slot colour, 109 of
#     109, against 21 of 109 for +76 and ~25% for any other shift;
#   * the six handles in the character's equipped-gear block match exactly one
#     of the 110 loadout records, and that record's vessel is the one the table
#     independently names as that Nightfarer's selected vessel.
HANDLE_OFFSET = -4

# Deep of Night relics roll curses into a second group of slots further into
# the record. Established the same way as the effect slots: scan every offset
# across the whole 80-byte record and see which ones hold a valid effect id.
# Only these three ever do, and on this save every id landing in them is
# flagged isDebuff -- 112 of them across 273 relics, with no exceptions.
#
# Two independent checks say the reading is right rather than coincidental:
# the number of curses found matches the relic template's own curse_count for
# 273 of 273 owned relics, and no relic whose template has no curse slot ever
# has a value here. Record stride is a uniform 80 bytes, so these offsets sit
# well inside the record they are read from and are not bleeding into the next.
CURSE_OFFSETS = (52, 56, 60)


@dataclass
class OwnedRelic:
    relic_id: int
    effect_ids: list[int]
    offset: int
    curse_ids: list[int] = field(default_factory=list)


def read_owned_relics(
    slot_data: bytes, valid_relic_ids: set[int], valid_effect_ids: set[int]
) -> list[OwnedRelic]:
    """Scan a decrypted character slot for relic inventory records.

    Anchors on the doubled relic id rather than a fixed stride, so it stays
    correct even if the surrounding record size changes between patches.
    """
    out: list[OwnedRelic] = []
    seen_offsets: set[int] = set()

    for off in range(0, len(slot_data) - 24, 4):
        first, second = struct.unpack_from("<II", slot_data, off)
        if first != second or first < RELIC_ID_FLAG:
            continue
        relic_id = first - RELIC_ID_FLAG
        if relic_id not in valid_relic_ids:
            continue
        if off in seen_offsets:
            continue
        seen_offsets.add(off + 4)

        effects = []
        for delta in EFFECT_OFFSETS:
            (value,) = struct.unpack_from("<I", slot_data, off + delta)
            if value in valid_effect_ids:
                effects.append(value)

        curses = []
        for delta in CURSE_OFFSETS:
            if off + delta + 4 > len(slot_data):
                break
            (value,) = struct.unpack_from("<I", slot_data, off + delta)
            if value in valid_effect_ids:
                curses.append(value)

        out.append(OwnedRelic(relic_id, effects, off, curses))

    return out


# ---------------------------------------------------------------------------
# The equipped loadout: which relic sits in which vessel slot, per Nightfarer.
#
# Two adjacent tables in the character slot, both built from the same 28-byte
# record: u32 vessel id (an AntiqueStandParam row), then six u32 relic handles,
# 0 for an empty slot. Slots 0-2 are the normal ones, 3-5 the three a vessel
# only exposes in Deep of Night.
#
#   Table A  ten groups of 120 bytes, one per Nightfarer in heroType order:
#              u32 0x0000ff0N   N = heroType, 1..10
#              u32 vessel id    the vessel that Nightfarer has selected
#              4 x record       one per shared Grail (hero_type 11)
#   Table B  immediately after: 70 records, one per personal vessel
#              (10 Nightfarers x 7), in vessel-id order
#
# The Grails get a record per Nightfarer because they are shared, so each
# Nightfarer needs its own arrangement of them; personal vessels belong to one
# Nightfarer already and so need only a single flat table.
LOADOUT_RECORD = 28
LOADOUT_SLOTS = 6
LOADOUT_GROUP = 8 + 4 * LOADOUT_RECORD      # 120
HERO_MARKER_BASE = 0xFF00
GRAILS_PER_HERO = 4
VESSELS_PER_HERO = 7

# How many Nightfarers the table can hold, and the fewest that still make it
# recognisable. Neither is fixed at ten on purpose. A save from a player who
# does not own the DLC carries fewer groups than one that does, and requiring
# exactly ten markers meant such a save reported no stored builds at all --
# not "some", none, which is precisely how the failure shows up. Four
# consecutive markers in ascending order is already far too specific a pattern
# to occur by chance in a save this size.
MAX_HEROES = 16
MIN_HEROES = 4


@dataclass
class Loadout:
    vessel_id: int
    handles: list[int]              # six, 0 where the slot is empty
    hero_id: int | None             # set for the per-Nightfarer Grail records
    selected: bool                  # is this the vessel that Nightfarer has on
    offset: int


# The most Grail records one Nightfarer's group can hold before the walk
# gives up. Generous on purpose: it only bounds a scan.
MAX_GRAILS = 12


def find_loadout_table(slot_data: bytes) -> list[tuple[int, int]]:
    """Table A as a list of (group offset, Grail-record count), one per
    Nightfarer, in marker order.

    Anchors on a run of markers ascending by one, so a stray 0x0000ff01
    elsewhere in the slot cannot be mistaken for the table -- but nothing
    about the layout is assumed beyond the record size. This function has
    now been wrong twice by assuming one number too many, and the third
    report settled the shape for good:

    - Through 1.3.0 the group width was hardcoded at 120 bytes (four Grail
      records). A save without the DLC carries three Grails -- 92-byte
      groups -- and reported no builds at all.
    - 1.3.1 measured the width but required it to be the SAME for every
      Nightfarer. The next report's diagnostics showed all ten markers
      present with no constant spacing between them: **group widths vary
      per Nightfarer** on that save, which is what a group holding records
      only for what that save has unlocked looks like.

    So each group's width is now measured individually: from a marker, the
    group runs until the next marker up sits at a well-formed distance
    (8 + k x 28 bytes), each Nightfarer with its own k.
    """
    limit = len(slot_data)
    best: list[tuple[int, int]] = []
    for off in range(0, max(limit - 8, 0), 4):
        if struct.unpack_from("<I", slot_data, off)[0] != HERO_MARKER_BASE + 1:
            continue
        groups: list[tuple[int, int]] = []
        pos = off
        hero = 1
        while hero <= MAX_HEROES:
            # How many records until the next marker up? The last group has
            # no next marker, so it cannot be measured this way and is
            # handled after the loop.
            found = None
            for records in range(0, MAX_GRAILS + 1):
                probe = pos + 8 + records * LOADOUT_RECORD
                if probe + 4 > limit:
                    break
                if (struct.unpack_from("<I", slot_data, probe)[0]
                        == HERO_MARKER_BASE + hero + 1):
                    found = records
                    break
            if found is None:
                break
            groups.append((pos, found))
            pos = pos + 8 + found * LOADOUT_RECORD
            hero += 1
        if len(groups) >= MIN_HEROES and len(groups) > len(best):
            # The final Nightfarer's group has no next marker to bound it,
            # but it does not need one: a shared-Grail record's own vessel id
            # sits in the 19000 band, and the personal vessels that follow in
            # table B do not, so the records are counted by what they are.
            records = 0
            while records < MAX_GRAILS:
                probe = pos + 8 + records * LOADOUT_RECORD
                if probe + 4 > limit:
                    break
                vessel = struct.unpack_from("<I", slot_data, probe)[0]
                if not 19000 <= vessel <= 19999:
                    break
                records += 1
            groups.append((pos, records))
            best = groups
    if not best:
        # Say what was actually seen, so the next report from a machine this
        # code has never met carries the numbers needed to diagnose it.
        seen = []
        for n in range(1, MAX_HEROES + 1):
            marker = struct.pack("<I", HERO_MARKER_BASE + n)
            hits = slot_data.count(marker)
            if hits:
                seen.append(f"ff{n:02x}×{hits}")
        raise ValueError(
            "equipped-loadout table not found in this save slot "
            f"(no ascending run of {MIN_HEROES}+ Nightfarer markers; "
            f"markers present: {', '.join(seen) or 'none'})"
        )
    return best


def read_relic_handles(slot_data: bytes, owned: list[OwnedRelic]) -> dict[int, OwnedRelic]:
    """Map each relic instance's handle to the relic it belongs to."""
    out: dict[int, OwnedRelic] = {}
    for relic in owned:
        off = relic.offset + HANDLE_OFFSET
        if off < 0:
            continue
        (handle,) = struct.unpack_from("<I", slot_data, off)
        out[handle] = relic
    return out


def read_loadouts(slot_data: bytes) -> list[Loadout]:
    """Read every stored loadout, both the Grail and the personal-vessel ones."""
    groups = find_loadout_table(slot_data)
    heroes = len(groups)
    out: list[Loadout] = []

    def record(off: int, hero: int | None, selected_id: int | None) -> Loadout:
        vessel_id = struct.unpack_from("<I", slot_data, off)[0]
        handles = list(struct.unpack_from(f"<{LOADOUT_SLOTS}I", slot_data, off + 4))
        return Loadout(vessel_id, handles, hero, vessel_id == selected_id, off)

    selected_by_hero: dict[int, int] = {}
    for group, grails in groups:
        marker, selected_id = struct.unpack_from("<2I", slot_data, group)
        hero = marker - HERO_MARKER_BASE
        selected_by_hero[hero] = selected_id
        for k in range(grails):
            out.append(record(group + 8 + k * LOADOUT_RECORD, hero, selected_id))

    # Table B carries no hero marker; the vessel's own heroType names its owner,
    # and whether it is selected is settled from that Nightfarer's group header.
    # The personal-vessel table is walked rather than counted off a fixed 70.
    # Its length follows from how many Nightfarers the save knows about, which
    # is the very thing that differs between installations, so the walk stops
    # on the first record whose vessel id is not a well-formed one: a vessel is
    # 1000-1006 for Nightfarer 1, 2000-2006 for Nightfarer 2, and so on.
    last_group, last_grails = groups[-1]
    flat = last_group + 8 + last_grails * LOADOUT_RECORD
    for k in range(heroes * VESSELS_PER_HERO):
        off = flat + k * LOADOUT_RECORD
        if off + LOADOUT_RECORD > len(slot_data):
            break
        vessel_id = struct.unpack_from("<I", slot_data, off)[0]
        hero = vessel_id // 1000          # 1000-1006 -> 1, 2000-2006 -> 2, ...
        if not (1 <= hero <= heroes and vessel_id % 1000 < VESSELS_PER_HERO):
            break
        out.append(record(off, hero, selected_by_hero.get(hero)))

    return out


def save_roots() -> list[pathlib.Path]:
    """Every directory a Nightreign save could be sitting in.

    %APPDATA% comes first and matters: it is the variable the game itself
    uses, and it is not always ~/AppData/Roaming. Folder redirection, a
    OneDrive-backed profile and a roaming enterprise profile all move it, and
    on those machines the hardcoded path finds nothing while the game is
    saving quite happily a directory away. Both are searched rather than one
    being picked, because either can be the real one.
    """
    roots: list[pathlib.Path] = []
    appdata = os.environ.get("APPDATA")
    if appdata:
        roots.append(pathlib.Path(appdata))
    roots.append(pathlib.Path.home() / "AppData" / "Roaming")

    out: list[pathlib.Path] = []
    for root in roots:
        folder = root / "Nightreign"
        if folder not in out:
            out.append(folder)
    return out


def find_saves() -> list[pathlib.Path]:
    """Every readable save file, newest last.

    The glob is deliberately wider than NR0000.sl2. The file is named that on
    every install seen so far, but a backup restored under another name, or a
    second slot file a future patch adds, is still a save this program can
    read -- and returning nothing at all is a far worse answer than returning
    one file too many, which the caller drops when it holds no relics.
    """
    seen: dict[pathlib.Path, None] = {}
    for root in save_roots():
        if not root.is_dir():
            continue
        for pattern in ("*/NR*.sl2", "NR*.sl2", "*/*.sl2"):
            for path in sorted(root.glob(pattern)):
                if path.is_file():
                    seen.setdefault(path.resolve(), None)
    return list(seen)
