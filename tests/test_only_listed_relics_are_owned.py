"""A relic record is only the player's when the slot's inventory list names it.

Reported 2026-11-16: one player saw relics of another in his planner. The
reader took every relic record in a character slot as owned, and a slot can
carry records of copies its player does not hold.
"""

from __future__ import annotations

import struct

from nrdata import savefile
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


def test_a_slot_whose_list_is_not_recognised_is_read_as_before():
    assert read(slot(listed=())) == [OWN_RELIC, FOREIGN_RELIC]


def test_the_planner_is_offered_only_the_listed_relics(tmp_path):
    found = inventory._scan_save(prepared_save(tmp_path,
                                               slot(listed=(OWN_HANDLE,))),
                                 IDS, set(), mode=savefile.FAST)
    assert [relic.relic_id for relic in found.owned] == [OWN_RELIC]
    assert list(found.handle_of.values()) == [OWN_HANDLE]
