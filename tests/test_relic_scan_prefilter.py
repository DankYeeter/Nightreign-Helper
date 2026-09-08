"""The prefilter in front of the relic scan finds what the full walk finds.

`read_owned_relics` used to look at every fourth byte of every slot: 10 293 488
`unpack_from` calls and 6,15 s on the thread that builds the window, at every
start and every rescan (T-118 P2, AD-029). It now asks `bytes.find` for the
one byte a record must carry and only looks at what comes back.

**Why these cases carry a full mutation proof.** A prefilter that hands over
too few offsets does not raise, log or crash -- it returns a shorter list, and
a shorter list of relics is exactly what a player with an empty inventory
sees. There is no other signal, so the guard is the only one there will be.

The expectation is never taken from the prefilter. `full_walk` below is the
scan as it stood before it, written out here so a mutation of the prefilter
has something independent to be caught by.
"""

from __future__ import annotations

import struct

import pytest

from nrdata import savefile

# One relic id the reader will accept, and one effect id, so a record can be
# built. Neither number is special; what the cases are about is which offsets
# the scan looks at.
RELIC_ID = 1234
EFFECT_ID = 7


def record_at(buffer: bytearray, off: int, relic_id: int = RELIC_ID,
              effects: bool = False) -> None:
    """Write one relic record into `buffer` at `off`, as the game writes it."""
    flagged = relic_id | savefile.RELIC_ID_FLAG
    struct.pack_into("<II", buffer, off, flagged, flagged)
    if effects:
        for delta in savefile.EFFECT_OFFSETS:
            struct.pack_into("<I", buffer, off + delta, EFFECT_ID)


def full_walk(slot_data: bytes, valid_relic_ids: set[int],
              valid_effect_ids: set[int]) -> list[savefile.OwnedRelic]:
    """The scan as it stood before the prefilter, offset by offset.

    A deliberate duplicate of the loop in `read_owned_relics`, and the only
    one in the tree: it is the independent expectation the prefilter is held
    against, so sharing code with the thing under test would be the whole
    point missed. It walks every fourth byte, which is what the prefilter
    claims to be able to skip without losing anything.
    """
    out: list[savefile.OwnedRelic] = []
    seen_offsets: set[int] = set()
    limit = max(1, len(slot_data) // savefile.MIN_BYTES_PER_RELIC_RECORD)

    for off in range(0, len(slot_data) - 24, 4):
        first, second = struct.unpack_from("<II", slot_data, off)
        if first != second or first < savefile.RELIC_ID_FLAG:
            continue
        relic_id = first - savefile.RELIC_ID_FLAG
        if relic_id not in valid_relic_ids or off in seen_offsets:
            continue
        seen_offsets.add(off + 4)

        effects = [value for delta in savefile.EFFECT_OFFSETS
                   for (value,) in [struct.unpack_from("<I", slot_data,
                                                       off + delta)]
                   if value in valid_effect_ids]
        curses = []
        for delta in savefile.CURSE_OFFSETS:
            if off + delta + 4 > len(slot_data):
                break
            (value,) = struct.unpack_from("<I", slot_data, off + delta)
            if value in valid_effect_ids:
                curses.append(value)

        out.append(savefile.OwnedRelic(relic_id, effects, off, curses))
        if len(out) > limit:
            raise ValueError("denser than the limit")
    return out


def outcome(scan, blob: bytes, relic_ids: set[int]):
    """What a scan says about this slot: its records, or that it refused.

    Refusals are part of the equality. The density limit (SEC-022) counts
    records *found*, so a prefilter that found fewer would quietly move it.
    """
    try:
        return [(r.relic_id, r.offset, tuple(r.effect_ids), tuple(r.curse_ids))
                for r in scan(blob, relic_ids, {EFFECT_ID})]
    except ValueError:
        return "refused"


def both_scans_agree(blob: bytes, relic_ids: set[int] | None = None):
    """Assert prefilter and full walk say the same, and return what they said."""
    relic_ids = relic_ids if relic_ids is not None else {RELIC_ID}
    expected = outcome(full_walk, blob, relic_ids)
    got = outcome(savefile.read_owned_relics, blob, relic_ids)
    assert got == expected, (
        f"the prefiltered scan found {got}, the full walk over every fourth "
        f"byte found {expected}")
    return expected


# --------------------------------------------------------------------------
# Equality against the full walk, on the shapes where a prefilter can go wrong


def test_a_record_at_the_very_first_offset_is_found():
    """The flag byte sits at index 3, which is where the search may start.

    A search beginning one byte later would lose this record and nothing
    else, so no other case in this file would notice.
    """
    buffer = bytearray(4096)
    record_at(buffer, 0, effects=True)

    assert both_scans_agree(bytes(buffer)) == [
        (RELIC_ID, 0, (EFFECT_ID,) * 3, ())]


def test_records_at_the_stride_the_game_writes_are_all_found():
    """Three records 80 bytes apart, the shape of a real inventory."""
    buffer = bytearray(4096)
    for index in range(3):
        record_at(buffer, index * 80, effects=True)

    assert [entry[1] for entry in both_scans_agree(bytes(buffer))] == [
        0, 80, 160]


def test_a_doubled_id_off_the_four_byte_grid_is_not_a_record():
    """Alignment is a property of the record, not a convenience of the walk.

    The full walk only ever looked at multiples of four, so a doubled id at
    offset 2 is data that happens to look like one. `bytes.find` has no such
    grid: it reports every hit, and a prefilter that passed them all on would
    invent a relic the player does not own.
    """
    buffer = bytearray(4096)
    record_at(buffer, 2, effects=True)

    assert both_scans_agree(bytes(buffer)) == []


def test_a_record_at_the_walks_own_upper_bound_is_not_read():
    """The last offset is `len - 24`, exclusive -- both scans stop there.

    Not a rounding: the bound is what the old walk did, and the fields of a
    record would still fit at that offset. A prefilter that ended one offset
    later would read a record here that today's scan never returned.
    """
    length = 1024
    buffer = bytearray(length)
    record_at(buffer, length - 24, effects=True)

    assert both_scans_agree(bytes(buffer)) == []


def test_the_last_record_the_walk_does_reach_is_read():
    """The control on the other side of that bound, one record earlier.

    Without it a prefilter that stopped far too early would pass the case
    above, since both say "nothing found".
    """
    length = 1024
    buffer = bytearray(length)
    record_at(buffer, length - 28, effects=True)

    assert [entry[1] for entry in both_scans_agree(bytes(buffer))] == [
        length - 28]


def test_an_id_carrying_the_flag_byte_inside_itself_is_still_found():
    """0x00800080: the record then holds the searched byte three times.

    Two of those hits are off the grid, and one of them sits *before* the
    aligned one. A search that skipped forward by a whole word after a hit
    would step over the real offset and lose the relic.
    """
    tricky = 0x00800080
    buffer = bytearray(4096)
    record_at(buffer, 100, relic_id=tricky, effects=True)

    assert [entry[1] for entry in both_scans_agree(bytes(buffer), {tricky})
            ] == [100]


def test_a_slot_that_is_nothing_but_the_searched_byte_is_still_refused():
    """SEC-022 through the prefilter: the density limit is untouched.

    Every fourth byte begins a record here, which is far denser than an
    inventory. The prefilter decides which offsets are looked at, so a
    prefilter that found fewer records would move a limit that counts found
    records -- and this file is the one that would notice.
    """
    packed = 0x00808080
    blob = b"\x80" * 4096

    assert both_scans_agree(blob, {packed}) == "refused"
    with pytest.raises(ValueError,
                       match="denser than one record per 64 bytes"):
        savefile.read_owned_relics(blob, {packed}, set())


def test_a_slot_too_short_to_hold_a_record_yields_nothing():
    """Shorter than the fields of one record; the bound goes negative."""
    assert both_scans_agree(b"\x80" * 12) == []
    assert both_scans_agree(b"") == []


# --------------------------------------------------------------------------
# The prefilter really is one


def test_the_prefilter_hands_over_a_fraction_of_the_offsets():
    """The point of the change, as a number the walk cannot also produce.

    Every case above stays green if the prefilter is replaced by the full
    walk again -- it would be *correct*, just as slow as before. This is the
    case that would not.

    A 64 KiB slot holding three records: the walk visits (65 536 - 24) / 4 =
    16 378 offsets. The prefilter visits two per record -- the doubled id
    carries the searched byte twice, four bytes apart, and both land on the
    grid -- so six, and everything else in the slot is skipped in C.
    """
    length = 64 * 1024
    buffer = bytearray(length)
    for index in range(3):
        record_at(buffer, index * 80, effects=True)

    candidates = list(savefile._relic_id_offsets(bytes(buffer)))

    assert candidates == [0, 4, 80, 84, 160, 164]
    assert len(candidates) * 100 < len(range(0, length - 24, 4))


# --------------------------------------------------------------------------
# The assumption the prefilter rests on, checked rather than commented


def test_a_relic_id_above_the_ceiling_is_refused_out_loud():
    """The failure mode this whole file exists for, made loud.

    An id at or above the ceiling does not carry the flag byte at its fourth,
    so the prefilter cannot see it and the player would be shown an inventory
    missing every relic of that band. The scan refuses instead.
    """
    buffer = bytearray(4096)
    record_at(buffer, 0)

    with pytest.raises(ValueError, match="cannot find"):
        savefile.read_owned_relics(bytes(buffer),
                                   {RELIC_ID, savefile.RELIC_ID_CEILING},
                                   set())


def test_the_refusal_says_the_program_is_too_old_and_names_no_file():
    """What the player is shown: whose fault it is, and no path.

    The save folder is named after the Steam account id, so no message out of
    this module may name a file (SEC-023). And the save is not the broken
    thing here -- the program is.
    """
    with pytest.raises(ValueError) as raised:
        savefile.read_owned_relics(b"", {savefile.RELIC_ID_CEILING}, set())

    message = str(raised.value)
    assert "\\" not in message and "/" not in message, message
    assert ".sl2" not in message.lower(), message
    assert "too old" in message, message


def test_the_largest_id_the_prefilter_can_see_is_read_in_full():
    """The control at the boundary, one below the ceiling.

    Without it the check would pass just as well set to zero, which would
    refuse every save on the machine.
    """
    biggest = savefile.RELIC_ID_CEILING - 1
    buffer = bytearray(4096)
    record_at(buffer, 0, relic_id=biggest, effects=True)

    assert both_scans_agree(bytes(buffer), {biggest}) == [
        (biggest, 0, (EFFECT_ID,) * 3, ())]


def test_the_games_own_relic_ids_are_all_below_the_ceiling(game_data):
    """The coupling itself, against the dataset of the installed game.

    The ceiling is an assumption about numbers this program does not own. The
    cases above prove the reader is loud when it breaks; this one is what
    reports that a patch has broken it, on the machine of whoever runs the
    suite. Largest id on 2026-09-08: 2 013 322, a factor 8 below.
    """
    biggest = max(relic["id"] for relic in game_data["relics"])

    assert biggest < savefile.RELIC_ID_CEILING, (
        f"the game now numbers a relic {biggest}; the inventory scan cannot "
        f"find ids at or above {savefile.RELIC_ID_CEILING}")
