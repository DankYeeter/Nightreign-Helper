"""The prefilter in front of `find_loadout_table` finds what the full walk finds.

`find_loadout_table` used to look at every fourth byte of the slot, checking
each one against the first Nightfarer marker: on a slot that carries no table
at all -- the common case, since only one of a save's fourteen character
slots ever does -- that walk runs to the very end and finds nothing (T-136,
following the shape T-133 gave the relic scan's own prefilter). `bytes.find`
now searches for the marker's own four bytes in C, and the loop only pays for
a hit and its alignment check.

**Why these cases carry a full mutation proof.** A prefilter that misses the
marker does not raise, log or crash -- `find_loadout_table` reports "table not
found", which is exactly what a save without a stored build (or a Nightfarer
never played) looks like. There is no other signal, so the guard is the only
one there will be.

The expectation is never taken from the prefilter. `full_walk` below is
`find_loadout_table` as it stood before the prefilter -- the range-based walk,
written out here so a mutation of the prefilter has something independent to
be caught by, and so this file shares no code with the thing it tests.
"""

from __future__ import annotations

import struct

import pytest

from nrdata import savefile

# A group holding no Grail records at all, so a table is nothing but its
# markers back to back: what these cases are about is which offsets the walk
# looks at, not the record content inside a group.
NO_GRAILS = 0

# The fewest real, consecutive markers a table needs before it is recognised
# at all. MIN_HEROES itself is one short -- the last group is only counted
# once a marker one higher than it has been found, so a run of exactly
# MIN_HEROES markers is rejected today (see test_loadout_table.py, "a short
# run of Nightfarers"; QA-009). A prefilter test needs a table that is
# actually found, so it uses this instead.
A_FOUND_TABLE = savefile.MIN_HEROES + 1


def group_marker(hero: int) -> bytes:
    return struct.pack("<I", savefile.HERO_MARKER_BASE + hero)


def table_at(buffer: bytearray, off: int, heroes: int = A_FOUND_TABLE,
             grails: int = NO_GRAILS, vessel_id: int = 1000) -> None:
    """Write `heroes` consecutive Nightfarer groups into `buffer`, starting
    at `off`, each carrying `grails` Grail records -- all zero bytes, since
    `find_loadout_table` only reads a Grail record's vessel id, and that
    band (19000-19999) is never zero.
    """
    pos = off
    for hero in range(1, heroes + 1):
        struct.pack_into("<II", buffer, pos,
                         savefile.HERO_MARKER_BASE + hero, vessel_id)
        pos += 8 + grails * savefile.LOADOUT_RECORD


def full_walk(slot_data: bytes) -> list[tuple[int, int]]:
    """`find_loadout_table` as it stood before the prefilter (T-136).

    A deliberate duplicate of the loop that used to open this function, the
    only one in the tree: it is the independent expectation the prefilter is
    held against, so calling the function under test to build it would be
    the whole point missed. It walks every fourth byte, which is what the
    prefilter claims to be able to skip without losing anything.
    """
    limit = len(slot_data)
    allowed_starts = max(1, limit // savefile.MIN_BYTES_PER_LOADOUT_TABLE)
    starts = 0
    best: list[tuple[int, int]] = []
    for off in range(0, max(limit - 8, 0), 4):
        if (struct.unpack_from("<I", slot_data, off)[0]
                != savefile.HERO_MARKER_BASE + 1):
            continue
        starts += 1
        if starts > allowed_starts:
            raise ValueError(
                f"a save slot of {limit} bytes begins a Nightfarer loadout "
                f"table at more than {allowed_starts} places, denser than "
                f"one table per {savefile.MIN_BYTES_PER_LOADOUT_TABLE} "
                f"bytes, which is not a save; the file is damaged or was "
                f"not written by the game. Take it out of the save folder "
                f"and rescan.")
        groups: list[tuple[int, int]] = []
        pos = off
        hero = 1
        while hero <= savefile.MAX_HEROES:
            found = None
            for records in range(0, savefile.MAX_GRAILS + 1):
                probe = pos + 8 + records * savefile.LOADOUT_RECORD
                if probe + 4 > limit:
                    break
                if (struct.unpack_from("<I", slot_data, probe)[0]
                        == savefile.HERO_MARKER_BASE + hero + 1):
                    found = records
                    break
            if found is None:
                break
            groups.append((pos, found))
            pos = pos + 8 + found * savefile.LOADOUT_RECORD
            hero += 1
        if len(groups) >= savefile.MIN_HEROES and len(groups) > len(best):
            records = 0
            while records < savefile.MAX_GRAILS:
                probe = pos + 8 + records * savefile.LOADOUT_RECORD
                if probe + 4 > limit:
                    break
                vessel = struct.unpack_from("<I", slot_data, probe)[0]
                if not 19000 <= vessel <= 19999:
                    break
                records += 1
            groups.append((pos, records))
            best = groups
    if not best:
        seen = []
        for n in range(1, savefile.MAX_HEROES + 1):
            marker = struct.pack("<I", savefile.HERO_MARKER_BASE + n)
            hits = slot_data.count(marker)
            if hits:
                seen.append(f"ff{n:02x}×{hits}")
        raise ValueError(
            "equipped-loadout table not found in this save slot "
            f"(no ascending run of {savefile.MIN_HEROES}+ Nightfarer "
            f"markers; markers present: {', '.join(seen) or 'none'})"
        )
    return best


def outcome(scan, blob: bytes):
    """What a scan says about this slot: its groups, or that it refused."""
    try:
        return scan(blob)
    except ValueError as exc:
        return ("refused", str(exc))


def both_walks_agree(blob: bytes):
    """Assert the prefiltered walk and the full walk say the same, and
    return what they said."""
    expected = outcome(full_walk, blob)
    got = outcome(savefile.find_loadout_table, blob)
    assert got == expected, (
        f"the prefiltered walk said {got}, the full walk over every fourth "
        f"byte said {expected}")
    return expected


# --------------------------------------------------------------------------
# `_loadout_marker_offsets` itself: which offsets it hands the outer walk


def test_a_marker_at_offset_zero_is_a_candidate():
    """The marker sits at index 0, which is where the search may start."""
    buffer = bytearray(64)
    buffer[0:4] = group_marker(1)

    assert list(savefile._loadout_marker_offsets(bytes(buffer))) == [0]


def test_a_marker_off_the_four_byte_grid_is_not_a_candidate():
    """`bytes.find` reports every hit, aligned or not; only the aligned one
    may start a table, exactly as `range(0, ..., 4)` only ever visited
    aligned offsets before.
    """
    buffer = bytearray(64)
    buffer[2:6] = group_marker(1)

    assert list(savefile._loadout_marker_offsets(bytes(buffer))) == []


def test_a_marker_at_the_walks_own_upper_bound_is_not_a_candidate():
    """The last offset the walk may start at is `len(slot_data) - 8`,
    exclusive -- a marker needs its own four bytes plus the four of the
    vessel id that follows, and the old walk's `range(0, limit - 8, 4)`
    never reached `limit - 8` itself.
    """
    length = 1024
    buffer = bytearray(length)
    buffer[length - 8 : length - 4] = group_marker(1)

    assert list(savefile._loadout_marker_offsets(bytes(buffer))) == []


def test_the_last_offset_the_walk_does_reach_is_a_candidate():
    """The control on the other side of that bound, four bytes earlier.

    Without it a prefilter that stopped short by a whole extra word would
    pass the case above too, since both would report no candidates.
    """
    length = 1024
    buffer = bytearray(length)
    buffer[length - 12 : length - 8] = group_marker(1)

    assert list(savefile._loadout_marker_offsets(bytes(buffer))) == [
        length - 12]


def test_the_prefilter_only_reports_offsets_on_the_four_byte_grid():
    """Two decoys either side of the grid the walk cares about, one real hit
    between them, so a prefilter that dropped the alignment check would hand
    back three offsets instead of one.
    """
    buffer = bytearray(64)
    buffer[1:5] = group_marker(1)    # off the grid by one
    buffer[18:22] = group_marker(1)  # off the grid by two
    buffer[8:12] = group_marker(1)   # the one real, aligned hit

    assert list(savefile._loadout_marker_offsets(bytes(buffer))) == [8]


def test_several_real_markers_come_out_ascending():
    """Ascending order is part of the contract: `find_loadout_table`'s outer
    walk relies on visiting the earliest possible start first.
    """
    buffer = bytearray(64)
    for off in (40, 0, 24, 8):
        buffer[off:off + 4] = group_marker(1)

    assert list(savefile._loadout_marker_offsets(bytes(buffer))) == [
        0, 8, 24, 40]


def test_the_prefilter_hands_over_a_fraction_of_the_offsets():
    """The point of the change, as a number the walk cannot also produce.

    Every case above stays green if the prefilter is replaced by the full
    walk again -- it would be *correct*, just as slow as before. This is the
    case that would not: it looks at `_loadout_marker_offsets` directly.

    A 1 MiB slot with one real marker and nothing else that looks like it:
    the full walk visits (1 048 576 - 8) / 4 = 262 142 offsets. The
    prefilter visits one.
    """
    length = 1024 * 1024
    buffer = bytearray(length)
    buffer[4096:4100] = group_marker(1)

    candidates = list(savefile._loadout_marker_offsets(bytes(buffer)))

    assert candidates == [4096]
    assert len(candidates) * 1000 < len(range(0, length - 8, 4))


# --------------------------------------------------------------------------
# `find_loadout_table` end to end, against the full walk on realistic shapes


def test_a_table_at_the_very_first_offset_is_found():
    """The marker sits at index 0, which is where the outer walk may start,
    and a real, complete table follows it.
    """
    buffer = bytearray(4096)
    table_at(buffer, 0)

    groups = both_walks_agree(bytes(buffer))
    assert [off for off, _count in groups] == [
        n * 8 for n in range(A_FOUND_TABLE)]


def test_a_full_table_off_the_four_byte_grid_is_not_found():
    """The whole table is well-formed, just shifted two bytes -- neither
    walk may recognise a table the game never wrote there.
    """
    buffer = bytearray(4096)
    table_at(buffer, 2)

    assert both_walks_agree(bytes(buffer))[0] == "refused"


def test_a_slot_with_no_marker_at_all_is_the_expensive_case_made_cheap():
    """The 244,3 ms case (T-136): a character slot without a stored build.

    Thirteen of a save's fourteen character slots carry no Table A -- the
    walk used to run every fourth byte of the whole slot before saying so.
    `nothing found` is the correct answer here, not an error in the reader.
    """
    blob = bytes(1024 * 1024)

    assert both_walks_agree(blob)[0] == "refused"


def test_a_lone_marker_amid_unrelated_data_is_still_not_a_table():
    """One real marker, nothing that continues it -- the shape the note
    about "markers present" exists to describe.
    """
    buffer = bytearray(4096)
    buffer[100:104] = group_marker(1)

    result = both_walks_agree(bytes(buffer))
    assert result == ("refused",
                       "equipped-loadout table not found in this save slot "
                       "(no ascending run of 4+ Nightfarer markers; markers "
                       "present: ff01×1)")


def test_two_tables_in_one_slot_the_longer_one_wins():
    """Two separate runs of markers; the walk keeps the longer, exactly as
    the full walk does (`len(groups) > len(best)`).
    """
    buffer = bytearray(8192)
    table_at(buffer, 0, heroes=A_FOUND_TABLE)
    table_at(buffer, 4096, heroes=A_FOUND_TABLE + 2)

    groups = both_walks_agree(bytes(buffer))
    assert groups[0][0] == 4096
    assert len(groups) == A_FOUND_TABLE + 2


# --------------------------------------------------------------------------
# SEC-024 density, through the prefilter


def test_a_slot_that_is_nothing_but_the_marker_is_still_refused():
    """Every fourth byte begins a table here -- SEC-024's own shape, now
    reached through the prefilter instead of the range() it replaced.
    """
    blob = group_marker(1) * (64 * 1024 // 4)

    assert both_walks_agree(blob)[0] == "refused"
    with pytest.raises(ValueError, match="denser than one table per 1920"):
        savefile.find_loadout_table(blob)


def test_a_slot_too_short_to_hold_a_marker_yields_nothing():
    """Shorter than a marker and its vessel id; the bound goes negative."""
    assert both_walks_agree(b"\0" * 4)[0] == "refused"
    assert both_walks_agree(b"")[0] == "refused"
    assert list(savefile._loadout_marker_offsets(b"\0" * 4)) == []
    assert list(savefile._loadout_marker_offsets(b"")) == []
