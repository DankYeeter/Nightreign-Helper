"""The equipped-loadout table, against saves that are not the usual shape.

This is the guard for the failure class that cost three releases. The table
was read with one assumption too many, twice:

* through 1.3.0 the group width was hardcoded at four Grail records, so a save
  from a player without the DLC -- three Grails, 92-byte groups -- reported no
  stored builds at all;
* 1.3.1 measured the width but demanded the same width for every Nightfarer,
  and the next report had all ten markers present with no constant spacing:
  the widths vary per Nightfarer on that save.

Both shapes are built here from bytes, so neither can come back unnoticed. No
save file is read: the whole point is to describe saves this machine does not
have.
"""

from __future__ import annotations

import struct

import pytest

from nrdata import savefile

# A Grail's own vessel id sits in this band, which is how the last group's
# width is told from the personal-vessel table that follows it.
GRAIL_VESSEL = 19000
LEAD_PADDING = 64
TRAILING_PADDING = 32


def _record(vessel_id: int, handles: list[int]) -> bytes:
    """One 28-byte loadout record: the vessel, then its six slots."""
    assert len(handles) == savefile.LOADOUT_SLOTS
    return struct.pack("<7I", vessel_id, *handles)


def _slot_bytes(grails_per_hero: list[int]) -> bytes:
    """A character slot holding nothing but a loadout table of this shape.

    Table A carries one group per Nightfarer -- marker, selected vessel, then
    that Nightfarer's own arrangement of the shared Grails. Table B follows
    with the seven personal vessels each Nightfarer has.
    """
    out = bytearray(b"\0" * LEAD_PADDING)
    for index, grails in enumerate(grails_per_hero):
        hero = index + 1
        out += struct.pack("<2I", savefile.HERO_MARKER_BASE + hero,
                           hero * 1000)     # this Nightfarer wears vessel N000
        for k in range(grails):
            handles = [hero * 100 + k * 10 + s + 1 for s in range(6)]
            out += _record(GRAIL_VESSEL + k, handles)

    for index in range(len(grails_per_hero)):
        hero = index + 1
        for vessel in range(savefile.VESSELS_PER_HERO):
            out += _record(hero * 1000 + vessel, [0] * 6)

    return bytes(out) + b"\0" * TRAILING_PADDING


SHAPES = {
    # The 1.3.1 report: no DLC, so fewer Nightfarers and three Grails each.
    "eight Nightfarers, three Grails each": [3] * 8,
    # The 1.3.2 report: every marker present, no constant spacing between
    # them, because each group holds only what that save has unlocked.
    "ten Nightfarers, widths differing per Nightfarer":
        [4, 3, 4, 2, 4, 4, 3, 4, 4, 1],
    # The ordinary full save, as a control.
    "ten Nightfarers, four Grails each": [4] * 10,
    # One more than MIN_HEROES, deliberately not MIN_HEROES itself: a table
    # with exactly that many groups is rejected today, because the last group
    # is only counted after a marker one higher has been found. That is
    # QA-009, which is open and belongs to its own task -- a test asserting
    # today's behaviour there would freeze the off-by-one in place.
    "a short run of Nightfarers": [4] * (savefile.MIN_HEROES + 1),
}


@pytest.mark.parametrize("grails_per_hero", list(SHAPES.values()),
                         ids=list(SHAPES))
def test_loadout_table_tolerates_a_dlc_less_save(grails_per_hero):
    blob = _slot_bytes(grails_per_hero)

    groups = savefile.find_loadout_table(blob)

    assert [count for _offset, count in groups] == grails_per_hero
    assert groups[0][0] == LEAD_PADDING


@pytest.mark.parametrize("grails_per_hero", list(SHAPES.values()),
                         ids=list(SHAPES))
def test_every_stored_loadout_is_read_back(grails_per_hero):
    """Not just found -- read: the right vessel, the right six handles."""
    blob = _slot_bytes(grails_per_hero)
    heroes = len(grails_per_hero)

    loadouts = savefile.read_loadouts(blob)

    grails = [entry for entry in loadouts if entry.hero_id is not None
              and entry.vessel_id >= GRAIL_VESSEL]
    personal = [entry for entry in loadouts if entry not in grails]
    assert len(grails) == sum(grails_per_hero)
    assert len(personal) == heroes * savefile.VESSELS_PER_HERO

    first = grails[0]
    assert first.hero_id == 1
    assert first.vessel_id == GRAIL_VESSEL
    assert first.handles == [101, 102, 103, 104, 105, 106]
    # Each Nightfarer wears vessel N000, which is a personal one, so no Grail
    # record may claim to be the selected vessel.
    assert not any(entry.selected for entry in grails)
    assert sum(1 for entry in personal if entry.selected) == heroes


def test_a_save_without_the_table_says_so_rather_than_guessing():
    """The failure has to name what it saw, or the next report is useless."""
    with pytest.raises(ValueError) as raised:
        savefile.find_loadout_table(b"\0" * 4096)

    assert "equipped-loadout table not found" in str(raised.value)
