"""TAE: the per-animation event track inside a character's anibnd.

TAE is what says *when*, within a specific animation, something happens --
a hitbox opens, a sound plays, a SpEffect is applied. Nothing else this
project reads can express "during the charge, before the swing".

No public paramdef or spec covers this; the layout below was derived from the
files and every step is checked rather than assumed. The derivation, in order,
because the checks are what make it trustworthy:

  * **Event records** were found first, by anchoring on SpEffect ids already
    known to be in the file and reading the bytes around them. Each record is
    `int64 type`, `int64 pointer`, then parameters -- and the pointer is
    always exactly `self+0x10`. That self-reference is a strong signature: it
    matches 8,140 times in Gladius's file and never coincidentally.
  * **Event type 66 applies a SpEffect.** Grouping records by type and asking
    how often the first parameter is a real `SpEffectParam` row id gives
    213 of 213 for type 66, against 33% for the runner-up and 0% for most.
  * **The animation table** was found by anchoring again, on the animation ids
    taken from the anibnd's own `aXXX_YYYYYY.hkx` member names. They appear as
    `int64` on a 16-byte stride starting at 0x110, and 85 entries x 16 bytes
    ends at 0x660 -- which is exactly the value the header stores at 0x60.
    The header agreeing with the arithmetic is the check.
  * **Times are float seconds**, and the first animation's array reads
    0.0, 0.1, 0.3, 3.5. `FLT_MAX` means "to the end of the animation".

One trap, recorded because it cost a wrong answer earlier: **do not scan the
file for plausible SpEffect ids.** TAE offsets in the 0xA000-0xA600 range have
decimal values that collide with the 41000-42500 boss SpEffect band, so a
blind int32 scan reports 42224 and 42320 as effects when they are pointers.
Always go through `events()`.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass

# Header fields, all int64 unless noted.
_ANIM_TABLE = 0x58        # offset of the animation table
_ANIM_TABLE_END = 0x60
_ANIM_COUNT = 0x70
_ANIM_ENTRY = 16          # {int64 animId, int64 headerOffset}

# Per-animation header: four offsets then three int32 counts.
_EVENTS, _GROUPS, _TIMES, _FILE = 0x00, 0x08, 0x10, 0x18
_COUNTS = 0x20
_EVENT_ENTRY = 24         # {int64 startTime*, int64 endTime*, int64 data*}

APPLY_SPEFFECT = 66       # param0 is a SpEffectParam row id
_FLT_MAX = 3.4028234663852886e38


@dataclass(frozen=True)
class Event:
    animation: int
    type: int
    start: float
    end: float
    param0: int

    @property
    def to_end(self) -> bool:
        """Runs to the end of the animation rather than to a set time."""
        return self.end >= _FLT_MAX


def is_tae(blob: bytes) -> bool:
    return len(blob) > 0x80 and blob[:4] == b"TAE "


def animations(blob: bytes) -> list[tuple[int, int]]:
    """(animation id, header offset) for every animation in the file."""
    if not is_tae(blob):
        return []
    count = struct.unpack_from("<q", blob, _ANIM_COUNT)[0]
    start = struct.unpack_from("<q", blob, _ANIM_TABLE)[0]
    end = struct.unpack_from("<q", blob, _ANIM_TABLE_END)[0]
    # The header stores the table's end as well as its start, so the two can
    # be checked against each other before anything is read.
    if count <= 0 or start <= 0 or end - start != count * _ANIM_ENTRY:
        return []
    return [struct.unpack_from("<qq", blob, start + i * _ANIM_ENTRY)
            for i in range(count)]


def events(blob: bytes) -> list[Event]:
    """Every event in the file, located to its animation and its timing."""
    out: list[Event] = []
    size = len(blob)
    for anim_id, header in animations(blob):
        if not 0 < header < size - _COUNTS - 16:
            continue
        ev_off = struct.unpack_from("<q", blob, header + _EVENTS)[0]
        times_off = struct.unpack_from("<q", blob, header + _TIMES)[0]
        ev_n = struct.unpack_from("<i", blob, header + _COUNTS)[0]
        if ev_n <= 0 or not 0 < ev_off < size:
            continue
        for i in range(ev_n):
            entry = ev_off + i * _EVENT_ENTRY
            if entry + _EVENT_ENTRY > size:
                break
            start_p, end_p, data = struct.unpack_from("<3q", blob, entry)
            if not 0 < data < size - 24:
                continue
            # The self-pointer is the integrity check: a record that does not
            # carry it is not an event record and must not be read as one.
            if struct.unpack_from("<q", blob, data + 8)[0] != data + 16:
                continue
            if not (0 < start_p < size - 4 and 0 < end_p < size - 4):
                continue
            if not 0 < times_off < size:
                continue
            out.append(Event(
                animation=anim_id,
                type=struct.unpack_from("<q", blob, data)[0],
                start=struct.unpack_from("<f", blob, start_p)[0],
                end=struct.unpack_from("<f", blob, end_p)[0],
                param0=struct.unpack_from("<i", blob, data + 16)[0],
            ))
    return out


def applied_speffects(blob: bytes) -> list[Event]:
    """Just the events that apply a SpEffect."""
    return [e for e in events(blob) if e.type == APPLY_SPEFFECT]
