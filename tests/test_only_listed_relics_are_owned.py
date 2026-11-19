"""A relic record is only the player's when the slot's inventory list names it.

Reported 2026-11-16: one player saw relics of another in his planner. The
reader took every relic record in a character slot as owned, and for an
expedition the game writes the equipped relics of all three players into
that table (measured 2026-11-19).
"""

from __future__ import annotations

import struct

import pytest

from nrdata import savefile
from nrdata.binary import NotWhatItClaims
from nrplanner import inventory

from .test_hostile_savefile import prepared_save

OWN_RELIC, FOREIGN_RELIC = 1234, 5678
OWN_HANDLE, FOREIGN_HANDLE = 0xC0800054, 0xC08002BD
IDS = {OWN_RELIC, FOREIGN_RELIC}


def record(relic_id: int, handle: int) -> bytes:
    """Handle, doubled id, and the rest of the game's 80 bytes left empty."""
    flagged = relic_id | savefile.RELIC_ID_FLAG
    return struct.pack("<III", handle, flagged, flagged) + bytes(68)


def list_entry(handle: int) -> bytes:
    """One 14-byte entry of the inventory list: handle, quantity, order."""
    return struct.pack("<IIIH", handle, 1, 7, 0)


def slot(*, listed: tuple[int, ...]) -> bytes:
    records = record(OWN_RELIC, OWN_HANDLE) + record(FOREIGN_RELIC,
                                                     FOREIGN_HANDLE)
    # Two bytes in front so the list is off the four-byte grid, as it is in
    # the game's own slot.
    body = records + bytes(2) + b"".join(list_entry(h) for h in listed)
    return body + bytes(4096 - len(body))


def read(blob: bytes) -> list[int]:
    owned = savefile.read_owned_relics(blob, IDS, set())
    return [relic.relic_id
            for relic in savefile.relics_the_inventory_lists(blob, owned)]


def test_a_record_the_inventory_list_does_not_name_is_not_owned():
    assert read(slot(listed=(OWN_HANDLE,))) == [OWN_RELIC]


def test_every_record_the_list_names_is_owned():
    assert read(slot(listed=(OWN_HANDLE, FOREIGN_HANDLE))) == [OWN_RELIC,
                                                               FOREIGN_RELIC]


def test_a_player_with_no_relic_of_his_own_is_offered_none():
    """Only other players' records and a list that names none of them."""
    assert read(slot(listed=())) == []


def test_a_record_without_a_handle_is_not_owned():
    blob = bytearray(slot(listed=(OWN_HANDLE,)))
    struct.pack_into("<I", blob, 80, 0)        # the second record's handle
    assert read(bytes(blob)) == [OWN_RELIC]


def expedition_slot(own: int, *, listed: bool) -> bytes:
    """`own` relics of the player, then what a session of three leaves."""
    handles = [OWN_HANDLE + n for n in range(own)]
    left = savefile.MOST_RECORDS_AN_EXPEDITION_LEAVES
    records = b"".join(record(OWN_RELIC, h) for h in handles) + b"".join(
        record(FOREIGN_RELIC, FOREIGN_HANDLE + n) for n in range(left))
    entries = b"".join(list_entry(h) for h in handles) if listed else b""
    body = records + bytes(2) + entries
    return body + bytes(16384 - len(body))


def test_what_an_expedition_of_three_leaves_is_not_owned():
    """The save measured 2026-11-19: 327 owned, 18 more records, 327 shown."""
    assert read(expedition_slot(40, listed=True)) == [OWN_RELIC] * 40


def test_a_list_this_reader_does_not_recognise_is_refused_not_guessed():
    with pytest.raises(NotWhatItClaims, match="names none of them"):
        read(expedition_slot(40, listed=False))


def test_the_refusal_reaches_the_window_as_an_unreadable_save(tmp_path):
    path = prepared_save(tmp_path, expedition_slot(40, listed=False))
    with pytest.raises(inventory.SaveNotReadable, match="names none of them"):
        inventory._scan_save(path, IDS, set(), mode=savefile.FAST)


def test_the_planner_is_offered_only_the_listed_relics(tmp_path):
    found = inventory._scan_save(prepared_save(tmp_path,
                                               slot(listed=(OWN_HANDLE,))),
                                 IDS, set(), mode=savefile.FAST)
    assert [relic.relic_id for relic in found.owned] == [OWN_RELIC]
    assert list(found.handle_of.values()) == [OWN_HANDLE]
