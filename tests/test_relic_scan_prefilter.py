"""Both ways of walking a slot find what the full walk finds.

`read_owned_relics` used to look at every fourth byte of every slot: 10 293 488
`unpack_from` calls and 6,15 s on the thread that builds the window, at every
start and every rescan (T-118 P2, AD-029). It now asks `bytes.find` for the
one byte a record must carry and only looks at what comes back.

That prefilter rests on one assumption about the game's own numbering, and a
game patch can break it (`RELIC_ID_CEILING`). When it breaks, the reader falls
back to the old walk and the window says so, rather than refusing a save that
is perfectly intact (AD-031, user's decision of 2026-09-08). So there are two
ways through the same body now, and **every case below runs both**.

**Why these cases carry a full mutation proof.** A way that hands over too few
offsets does not raise, log or crash -- it returns a shorter list, and a
shorter list of relics is exactly what a player with an empty inventory sees.
There is no other signal, so the guard is the only one there will be. That
holds twice over for the slow way: it is the one nobody runs until a patch
makes it the only one that works.

The expectation is never taken from either way. `full_walk` below is the scan
as it stood before the prefilter, written out here so a mutation of either
generator has something independent to be caught by.
"""

from __future__ import annotations

import functools
import struct

import pytest

from nrdata import savefile
from nrplanner import inventory

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
    records *found*, so a way that found fewer would quietly move it.
    """
    try:
        return [(r.relic_id, r.offset, tuple(r.effect_ids), tuple(r.curse_ids))
                for r in scan(blob, relic_ids, {EFFECT_ID})]
    except ValueError:
        return "refused"


def both_scans_agree(blob: bytes, relic_ids: set[int] | None = None):
    """Assert both ways and the full walk agree, and return what they said.

    Run for `FAST` and for `SLOW`, each against `full_walk` and never against
    the other: two ways checked against each other would both be allowed to be
    wrong in the same way, and the point of `full_walk` is that it is neither
    of them.

    The mode is passed in rather than left to `relic_scan_mode`, because that
    function would answer `FAST` for nearly every case in this file -- the
    slow way would then be walked by no case at all, which is exactly the hole
    AD-031 has to keep shut.
    """
    relic_ids = relic_ids if relic_ids is not None else {RELIC_ID}
    expected = outcome(full_walk, blob, relic_ids)
    for mode in (savefile.FAST, savefile.SLOW):
        scan = functools.partial(savefile.read_owned_relics, mode=mode)
        got = outcome(scan, blob, relic_ids)
        assert got == expected, (
            f"the {mode} scan found {got}, the full walk over every fourth "
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
# The assumption the prefilter rests on: which way a dataset is read on


def test_the_choice_is_made_at_three_stated_ids():
    """`relic_scan_mode` at the two sides of the ceiling and at a real id.

    The expectations are written out rather than computed from
    `RELIC_ID_CEILING`: an expectation taken from the constant the choice is
    made on would agree with any value that constant is given, including one
    that reads every save on this machine the slow way.

    2 013 322 is the largest id the installed game numbers a relic with
    (2026-09-08). 0x00FFFFFF is the last id the fast prefilter can see;
    0x01000000 is the first it cannot.
    """
    assert savefile.relic_scan_mode({2013322}) == "fast"
    assert savefile.relic_scan_mode({0x00FFFFFF}) == "fast"
    assert savefile.relic_scan_mode({0x01000000}) == "slow"
    assert savefile.relic_scan_mode(set()) == "fast"


def test_an_id_above_the_ceiling_is_read_the_slow_way_and_not_refused():
    """What this file's `..._is_refused_out_loud` case asserted until AD-031.

    That case required a `ValueError` for a dataset numbered above the
    ceiling, which is the whole save declared unreadable while nothing is
    wrong with it. The user decided on 2026-09-08 that the program reads such
    a save the slow way and says so instead (AK-228), so the refusal is gone
    and this is what stands in its place.

    Three records of an id the fast prefilter is blind to, and the count is
    written out rather than taken from the loop that builds them: a fall-back
    that found two of the three would otherwise still be green, and a short
    inventory is precisely the failure that cannot be seen from outside.
    """
    above = savefile.RELIC_ID_CEILING + 42
    buffer = bytearray(4096)
    for index in range(3):
        record_at(buffer, index * 80, relic_id=above, effects=True)
    ids = {RELIC_ID, above}

    found = savefile.read_owned_relics(bytes(buffer), ids, {EFFECT_ID})

    assert [entry.offset for entry in found] == [0, 80, 160]
    assert [entry.relic_id for entry in found] == [above] * 3
    # The control that says the slow way is what found them, and not some
    # other reading of this slot: the fast way, asked for by name, sees none.
    assert savefile.read_owned_relics(bytes(buffer), ids, {EFFECT_ID},
                                      mode=savefile.FAST) == []


def test_a_mode_that_is_neither_way_is_refused_rather_than_guessed():
    """The keyword is a choice between two ways, not a free string.

    Falling back to one of them for a value that is neither would pick a way
    the caller did not ask for, and the wrong pick is invisible in the result
    -- which is the failure mode this whole file is about.
    """
    with pytest.raises(ValueError, match="not a relic scan mode"):
        savefile.read_owned_relics(b"\x00" * 64, {RELIC_ID}, set(),
                                   mode="quick")


def test_the_largest_id_the_fast_way_can_see_is_read_in_full():
    """The control at the boundary, one below the ceiling.

    Without it the choice would pass just as well set to zero, which would
    read every save on this machine the slow way -- 6 147,6 ms against 657,2,
    and nothing in the result to tell the two apart.
    """
    biggest = savefile.RELIC_ID_CEILING - 1
    buffer = bytearray(4096)
    record_at(buffer, 0, relic_id=biggest, effects=True)

    assert savefile.relic_scan_mode({biggest}) == savefile.FAST
    assert both_scans_agree(bytes(buffer), {biggest}) == [
        (biggest, 0, (EFFECT_ID,) * 3, ())]


def test_the_games_own_relic_ids_still_allow_the_fast_way(game_data):
    """The coupling itself, against the dataset of the installed game.

    The ceiling is an assumption about numbers this program does not own.
    Since AD-031 a broken assumption is no longer an error -- the save is
    still read, on the slow way -- so what this case reports is not a
    breakage but a cost: the reading of every save on this machine would go
    from 657,2 ms to the order of 6 147,6 ms (measured 1.7.1, T-140).

    Largest id on 2026-09-08: 2 013 322, a factor 8 below the ceiling.
    """
    ids = {relic["id"] for relic in game_data["relics"]}

    assert savefile.relic_scan_mode(ids) == savefile.FAST, (
        f"the game now numbers a relic {max(ids)}; every save on this machine "
        f"is now read the slow way, which is correct but far slower")


# --------------------------------------------------------------------------
# The way travels on the inventory, so the window can say which one was used


def a_dataset(relic_id: int) -> dict:
    """The two fields of the dataset an inventory read looks at."""
    return {"relics": [{"id": relic_id, "name": "Test Relic", "colour": 0}],
            "effects": {str(EFFECT_ID): {"name": "Test Effect"}}}


def an_inventory_read_of(monkeypatch, tmp_path, relic_id: int):
    """Load an inventory out of one slot holding one record of `relic_id`.

    What is replaced is the decryption, not the choice under test: the whole
    of `scan` and `build` runs, including the one place the way is decided and
    the two places it is carried. Writing an encrypted container instead would
    duplicate `test_hostile_savefile.py`'s builder here and pull Qt into a
    file that is deliberately free of it.
    """
    buffer = bytearray(4096)
    record_at(buffer, 0, relic_id=relic_id, effects=True)
    save = tmp_path / "NR0000.sl2"
    save.write_bytes(b"")
    monkeypatch.setattr(inventory, "_decrypt_slots",
                        lambda path: {"USER_DATA000": bytes(buffer)})

    return inventory.load(a_dataset(relic_id), save_path=save)


def test_an_inventory_read_the_slow_way_says_so(monkeypatch, tmp_path):
    """AD-031 point 4: the way stands on the inventory, not on a signal.

    And the relic is there: a fall-back that set the field but found nothing
    would leave the player an empty planner with a sentence explaining it.
    """
    inv = an_inventory_read_of(monkeypatch, tmp_path,
                               savefile.RELIC_ID_CEILING + 42)

    assert inv.read_the_slow_way is True
    assert inv.relic_count == 1


def test_an_inventory_read_the_fast_way_says_that_too(monkeypatch, tmp_path):
    """The other side, without which the field could be wired to True."""
    inv = an_inventory_read_of(monkeypatch, tmp_path, RELIC_ID)

    assert inv.read_the_slow_way is False
    assert inv.relic_count == 1


def test_the_way_is_chosen_once_for_a_load_and_not_once_per_slot(monkeypatch,
                                                                 tmp_path):
    """AD-031 point 1, as a count rather than as a state.

    The question is about the dataset, and the dataset does not change between
    the slots of one read -- a save holds up to fourteen of them. Asking per
    slot would give the same answer every time and so could never be seen in a
    result; the count is the only place the difference shows.
    """
    buffer = bytearray(4096)
    for index in range(3):
        record_at(buffer, index * 80, effects=True)
    save = tmp_path / "NR0000.sl2"
    save.write_bytes(b"")
    monkeypatch.setattr(inventory, "_decrypt_slots", lambda path: {
        f"USER_DATA00{index}": bytes(buffer) for index in range(3)})

    asked = []
    real_mode = savefile.relic_scan_mode
    monkeypatch.setattr(savefile, "relic_scan_mode",
                        lambda ids: asked.append(ids) or real_mode(ids))

    found = inventory.scan(a_dataset(RELIC_ID), save_path=save)

    assert len(found.owned) == 3, "the premise: three slots were read"
    assert len(asked) == 1, f"the dataset was asked {len(asked)} times"


def test_an_inventory_nobody_read_makes_no_claim_about_a_way():
    """A hand-built inventory has no save behind it and so no way either."""
    assert inventory.Inventory(source="by hand").read_the_slow_way is False
