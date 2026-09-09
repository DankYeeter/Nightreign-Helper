"""A save file the program was handed cannot freeze it, exhaust it or write
markup into its window.

SEC-001, SEC-002 and SEC-004. One input path -- save file, parser, label --
and three ways a prepared or merely damaged file used to come out the other
end. The buffers here are built byte by byte rather than taken from the
player's own save, because a real save is well formed and cannot produce any
of these three states; that is the whole reason they went unnoticed.

* **SEC-001**, `test_an_unterminated_name_*`: the name search walked forward
  until it met two zero bytes and there were none, so it never stopped. It ran
  on the GUI thread while the window was being built, before the player had
  touched anything, and the window never appeared. These tests carry a time
  limit, because a regression here does not fail an assertion -- it hangs, and
  a test that hangs stops the suite instead of reporting.
* **SEC-002**, `test_a_count_larger_than_the_file_*`: a member count read
  straight out of the file steered the loop that allocates. Four bytes of a
  damaged header asked for four billion members.
* **SEC-004**, `test_the_save_slot_name_is_shown_as_text`: the label that
  names the loaded save was on Qt's AutoText, which decides for itself whether
  what it was given is markup.
* **SEC-022**, `test_a_slot_packed_with_relic_records_*` and
  `test_an_inventory_denser_than_*`: the inventory scan walked the character
  slot without any limit on how many records it would take out of it. A
  prepared file yields 131 069 records per MiB, and the program reads every
  save it finds at startup and keeps the best-populated one, so the prepared
  file wins and the window never appears. Two limits at two places, because
  the class stays shut by a property rather than by a line: the reader
  refuses to build such a list, and the inventory refuses to offer one
  whatever built it.
* **SEC-024**, `test_a_slot_packed_with_table_starts_*`: the search for the
  equipped-loadout table began a walk of up to sixteen groups at every place
  the first Nightfarer marker stood, and a prepared slot stands it at every
  fourth byte. Measured on this machine: 1,03 s per MiB of slot against 36 ms
  for the real save, so a 19 MB file was 24 s of frozen window at startup.
  Neither SEC-022 limit reaches it -- one well-formed relic record is all such
  a file needs to be read at all.
"""

from __future__ import annotations

import pathlib
import struct
import threading

import pytest
from Crypto.Cipher import AES

from nrdata import binary, savefile
from nrplanner import inventory
from nrplanner.advisor import run as advisor_run
from nrplanner.advisor import types as advisor_types

# How long a parse may take before the test calls it a hang. Every parse here
# works on a few hundred bytes and returns in well under a millisecond, so the
# margin is enormous on purpose: it must not fail on a loaded machine, and a
# regression is an endless loop, which no margin saves.
TIME_LIMIT_SECONDS = 10.0

# A save slot name carrying every shape SEC-004 named: a tag Qt would render,
# an image Qt would try to fetch, and a UNC path that would make that fetch a
# request to another host.
HOSTILE_NAME = "<b>NR0000</b><img src='\\\\host\\share\\x.png'>"


def within_time_limit(call):
    """Run `call` on a worker and fail the test if it does not come back.

    A regression in the terminator search is an endless loop, so the test
    cannot simply call the parser and time it afterwards -- there is no
    afterwards. The worker is a daemon: one left spinning by a regression dies
    with the process instead of holding the run open, and the failure is
    reported rather than waited on.
    """
    outcome: dict[str, object] = {}

    def run() -> None:
        try:
            outcome["value"] = call()
        except BaseException as exc:  # noqa: BLE001 -- re-raised below
            outcome["error"] = exc

    worker = threading.Thread(target=run, daemon=True)
    worker.start()
    worker.join(TIME_LIMIT_SECONDS)
    if worker.is_alive():
        pytest.fail(
            f"the parser did not come back within {TIME_LIMIT_SECONDS:g} s, "
            "which is the endless loop of SEC-001"
        )
    if "error" in outcome:
        raise outcome["error"]
    return outcome["value"]


def save_container(name_bytes: bytes, *, file_count: int = 1,
                   file_header_size: int = 0x20) -> bytes:
    """A BND4 save container holding one member, as `_members` reads it.

    Only the fields that reader takes out are filled; everything else is the
    padding a real container has there anyway. `file_count` and
    `file_header_size` are arguments because the counter cases need to state
    something the rest of the buffer does not back up.
    """
    header = bytearray(0x40)
    header[0:4] = b"BND4"
    struct.pack_into("<I", header, 0x0C, file_count)
    struct.pack_into("<Q", header, 0x20, file_header_size)
    header[0x30] = 1                      # names are UTF-16

    entry = bytearray(0x20)
    struct.pack_into("<Q", entry, 8, 0)   # member size
    struct.pack_into("<I", entry, 16, 0)  # member offset
    struct.pack_into("<I", entry, 20, 0x60)   # name offset: right after this
    return bytes(header + entry + name_bytes)


# --------------------------------------------------------------------------
# SEC-001: a name with no terminator


def test_an_unterminated_name_in_a_save_is_a_data_error():
    """The save reader reports the file, rather than walking off the end."""
    blob = save_container("NR0000".encode("utf-16-le"))   # no trailing 00 00

    with pytest.raises(ValueError, match="unterminated"):
        within_time_limit(lambda: savefile._members(blob))


def test_an_unterminated_utf16_string_anywhere_is_a_data_error():
    """The shared reader is what all four parsers now go through."""
    buffer = "a name".encode("utf-16-le")

    with pytest.raises(ValueError, match="unterminated"):
        within_time_limit(lambda: binary.read_cstring(buffer, 0, utf16=True))


def test_a_name_offset_past_the_end_is_a_data_error():
    """The offset itself can be the lie, before a single byte is read."""
    buffer = "a name".encode("utf-16-le") + b"\0\0"

    with pytest.raises(ValueError, match="outside"):
        within_time_limit(
            lambda: binary.read_cstring(buffer, len(buffer) + 4, utf16=True))


def test_a_terminated_name_is_still_read():
    """The bound must not cost the case the bound was added for.

    A test that only proves the error path would pass just as well against a
    reader that raises on everything.
    """
    blob = save_container("NR0000".encode("utf-16-le") + b"\0\0")

    assert [name for _i, name, _o, _s in savefile._members(blob)] == ["NR0000"]


def test_a_terminator_on_an_odd_boundary_does_not_end_the_name():
    """The zero pair inside "AA-macron" is not the end of the string.

    Little-endian UTF-16 writes "A" as 41 00 and "A-macron" as 00 01, so the
    two meet as 41 00 | 00 01 and there is a 00 00 pair sitting at offset 1.
    A search that took the first pair it saw would stop there and return "A",
    a name the file never held. The rule that the terminator counts only at an
    even distance from the start is what keeps that from happening, and this
    is the case that tells the two searches apart.
    """
    text = "AĀ"
    buffer = text.encode("utf-16-le") + b"\0\0"

    assert buffer[1:3] == b"\0\0", "the test's premise, not its subject"
    assert binary.read_cstring(buffer, 0, utf16=True) == text


# --------------------------------------------------------------------------
# SEC-002: a count larger than what is left of the file


def test_a_member_count_larger_than_the_file_is_a_data_error():
    """Four bytes claiming four billion members allocate nothing."""
    blob = save_container(b"", file_count=0xFFFFFFFF)

    with pytest.raises(ValueError, match="do not fit"):
        within_time_limit(lambda: savefile._members(blob))


def test_a_member_header_size_larger_than_the_file_is_a_data_error():
    """The other half of the same product, which is just as unbounded."""
    blob = save_container(b"", file_count=4, file_header_size=1 << 40)

    with pytest.raises(ValueError, match="do not fit"):
        within_time_limit(lambda: savefile._members(blob))


def test_a_member_header_too_small_to_hold_its_fields_is_a_data_error():
    """A header size of zero would put every member at the same address."""
    blob = save_container(b"", file_count=8, file_header_size=0)

    with pytest.raises(ValueError, match="do not fit"):
        within_time_limit(lambda: savefile._members(blob))


def test_a_container_shorter_than_its_own_header_is_a_data_error():
    """Truncation is the ordinary way a save goes wrong, not the exotic one."""
    with pytest.raises(ValueError, match="too short"):
        within_time_limit(lambda: savefile._members(b"BND4" + b"\0" * 8))


def test_a_well_formed_container_still_reads():
    """Again the control: the counter checks pass what a real save states."""
    blob = save_container("NR0000".encode("utf-16-le") + b"\0\0")

    assert len(savefile._members(blob)) == 1


def string_table(first_id: int, last_id: int) -> bytes:
    """An FMG whose one group claims to span the ids given.

    Version 2, little-endian -- the shape Nightreign ships. Only the fields
    the reader takes out are filled: the group count and string count at 0x0C,
    the offset table's position at 0x18, then one group header at 0x28.
    """
    header = bytearray(0x28)
    header[1] = 0                              # little-endian
    header[2] = 2                              # 64-bit offsets
    struct.pack_into("<II", header, 0x0C, 1, 1)     # one group, one string
    struct.pack_into("<Q", header, 0x18, 0x38)      # offset table follows

    group = struct.pack("<iii", 0, first_id, last_id) + b"\0" * 4
    offsets = struct.pack("<Q", 0x40)                # the one string
    return bytes(header) + group + offsets + "s".encode("utf-16-le") + b"\0\0"


def test_a_string_group_wider_than_the_table_is_a_data_error():
    """This is the counter that span nothing but the CPU.

    The other counters in this file steer reads that walk off the end of the
    buffer and stop themselves that way. This one does not: the loop it drives
    skips indices past the end of the table and keeps counting, so a group
    header claiming two billion ids simply ran, for as long as it took. Hence
    the time limit here as well.
    """
    from nrdata import fmg

    data = string_table(0, 0x7FFFFFFF)

    with pytest.raises(ValueError, match="not a run of"):
        within_time_limit(lambda: fmg.read(data))


def test_a_well_formed_string_table_still_reads():
    """The control for the group check: one id, one string, read as before."""
    from nrdata import fmg

    assert fmg.read(string_table(0, 0)) == {0: "s"}


# --------------------------------------------------------------------------
# SEC-004: markup out of the save, in the window


def test_the_save_slot_name_is_shown_as_text(planner):
    """The label that names the loaded save draws the name, not the markup.

    Checked against the widget the program actually builds, and against a
    QLabel left as Qt makes one. The second label is the control: if Qt
    rendered both the same way the comparison would prove nothing, and the
    difference in width is what says one of them drew "<b>" as three
    characters while the other took it as an instruction.
    """
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QLabel

    label = planner.owned_label
    assert label.textFormat() == Qt.PlainText

    label.setText(HOSTILE_NAME)
    as_qt_makes_it = QLabel(HOSTILE_NAME)

    assert label.text() == HOSTILE_NAME
    assert label.sizeHint().width() > as_qt_makes_it.sizeHint().width(), (
        "the label under test is no wider than one that renders the markup, "
        "so it is not showing the name as text"
    )


# --------------------------------------------------------------------------
# SEC-022: a character slot claiming more relics than it has room for


# One relic id the reader will accept. The records built below carry no
# effects: what is under test is how many records a slot may claim, not what
# they hold.
KNOWN_RELIC_ID = 1234
DOUBLED_ID = struct.pack("<II", KNOWN_RELIC_ID | savefile.RELIC_ID_FLAG,
                         KNOWN_RELIC_ID | savefile.RELIC_ID_FLAG)


def relic_records(byte_length: int, stride: int) -> bytes:
    """A decrypted character slot with one relic record every `stride` bytes.

    A record here is the doubled relic id and nothing else, because that is
    what `read_owned_relics` anchors on. `stride` is what makes these cases
    about a density rather than a count: the game writes records 80 bytes
    apart, a prepared file writes them 8 bytes apart, and the reader's limit
    of one per 64 bytes sits between the two.

    Built byte by byte and never written to disk. A `.sl2` in the save folder
    is precisely the attack these cases are about, and the player has a copy
    of the program running.
    """
    buffer = bytearray(byte_length)
    for off in range(0, byte_length - 24, stride):
        buffer[off:off + len(DOUBLED_ID)] = DOUBLED_ID
    return bytes(buffer)


def read_records(blob: bytes, effect_ids: set[int] | None = None,
                 mode: str | None = None):
    return savefile.read_owned_relics(blob, {KNOWN_RELIC_ID},
                                      effect_ids or set(), mode=mode)


#: The two ways a slot is walked since AD-031: the fast prefilter, and the
#: old walk the reader falls back to when a game patch numbers relics above
#: what the prefilter can see. The density limit is one body walked by both,
#: and every case below is asked of both -- a limit that held only on the way
#: nobody runs until such a patch arrives would be no limit at all, and the
#: prepared file that gets past it looks like an ordinary inventory.
BOTH_WAYS = pytest.mark.parametrize("mode", [savefile.FAST, savefile.SLOW])


@BOTH_WAYS
def test_a_slot_packed_with_relic_records_is_a_data_error(mode):
    """One record every eight bytes is what a prepared file writes.

    Measured by the `security-reviewer` on the reader as it stood: 131 069
    records per MiB, 3,31 s and 41 MB of memory per MiB of member, linear in
    the size of the file. Nineteen MB of that is a minute of frozen window
    before the player has touched anything.
    """
    blob = relic_records(64 * 1024, stride=8)

    with pytest.raises(ValueError,
                       match="denser than one record per 64 bytes"):
        within_time_limit(lambda: read_records(blob, mode=mode))


@BOTH_WAYS
def test_the_refusal_over_a_packed_slot_names_no_file_path(mode):
    """What the player is shown says what to do and does not name the file.

    The save folder is named after the Steam account id, so a message that
    named the file would put that id into every screenshot and bug report the
    failure produces -- which is a finding of its own (SEC-023) and not one
    this message may enlarge.
    """
    with pytest.raises(ValueError) as raised:
        read_records(relic_records(64 * 1024, stride=8), mode=mode)

    message = str(raised.value)
    assert "\\" not in message and "/" not in message, message
    assert ".sl2" not in message.lower(), message
    assert "save folder" in message and "rescan" in message, message


@BOTH_WAYS
def test_a_slot_filled_to_the_limit_is_read_in_full(mode):
    """The control at the boundary: the limit must not cost the last record.

    A case that only proved the error path would pass just as well against a
    reader that refuses everything, and one that proved it two orders of
    magnitude away from the limit would say nothing about where the limit is.
    """
    blob = relic_records(6400, stride=64)

    assert len(read_records(blob, mode=mode)) == 6400 // 64


@BOTH_WAYS
def test_one_record_more_than_the_slot_can_hold_is_a_data_error(mode):
    """The other side of the same boundary, one record further on.

    6 432 bytes have room for 100 records at one per 64; this slot claims 101.
    """
    blob = relic_records(6432, stride=64)

    with pytest.raises(ValueError, match="more than 100 relic records"):
        within_time_limit(lambda: read_records(blob, mode=mode))


@BOTH_WAYS
def test_a_slot_at_a_real_saves_density_is_read_with_its_effects(mode):
    """The control the limit exists for: an ordinary inventory still reads.

    Stride 80 is the record width the game writes. The real save on this
    machine holds 309 records in 1 048 608 bytes of character slot -- one per
    3 394 bytes, a factor 53 below the limit -- and this is that shape in
    miniature, three records in 4 096 bytes.
    """
    effect_id = 7
    buffer = bytearray(4096)
    for index in range(3):
        off = index * 80
        buffer[off:off + len(DOUBLED_ID)] = DOUBLED_ID
        for delta in savefile.EFFECT_OFFSETS:
            struct.pack_into("<I", buffer, off + delta, effect_id)

    owned = read_records(bytes(buffer), {effect_id}, mode=mode)

    assert [entry.offset for entry in owned] == [0, 80, 160]
    assert [entry.effect_ids for entry in owned] == [[effect_id] * 3] * 3


def owned_relics(count: int) -> list[inventory.OwnedItem]:
    """`count` copies of one relic, as an `Inventory` carries them."""
    return [inventory.OwnedItem(relic_id=KNOWN_RELIC_ID, name="Relic",
                                colour=0, effect_ids=[], is_deep=False,
                                handle=index, offset=index * 80)
            for index in range(count)]


def test_an_inventory_denser_than_the_slot_it_came_from_offers_nothing():
    """The second limit, reached without the first one being asked at all.

    This list is built here rather than read, and that is the whole point of
    it: it never went through `read_owned_relics`, so it stands for the day
    somebody loosens that limit or writes a second reader beside it. The
    player is protected by the property and not by the line that carries it
    today.
    """
    owned = inventory.Inventory(source="slot", source_bytes=6400,
                                relics=owned_relics(101))

    with pytest.raises(ValueError, match="denser than one per 64 bytes"):
        owned.relics_for(colour=0, deep=False)


def test_an_inventory_filled_to_the_limit_still_offers_its_relics():
    """The control for the second limit, again at the boundary itself."""
    owned = inventory.Inventory(source="slot", source_bytes=6400,
                                relics=owned_relics(100))

    assert len(owned.relics_for(colour=0, deep=False)) == 100


def test_an_inventory_built_by_hand_makes_no_claim_about_a_save():
    """No save behind it, no density to judge -- a state, not a hole.

    Every inventory the program builds comes from `_scan_save` and carries the
    size of the slot it was read from. One built without that is a caller's
    own object, and holding it to a size it never named would refuse lists
    that are not claims about any file.
    """
    owned = inventory.Inventory(source="test", relics=owned_relics(101))

    assert len(owned.relics_for(colour=0, deep=False)) == 101


def test_the_advisor_is_not_handed_an_inventory_of_that_density():
    """Where the second limit is felt: the advisor's pre-sort.

    `frozen_inventory` is the one door between the living inventory and a
    run, and it asks `relics_for` for every slot in play. The pre-sort behind
    that door costs 175,6 us per offered relic
    (`scripts/measure_advisor_cancel.py`, 309 relics, six free slots, this
    machine), so an inventory that got past the reader would be spent there
    rather than reported.
    """
    owned = inventory.Inventory(source="slot", source_bytes=6400,
                                relics=owned_relics(101))
    problem = advisor_types.SlotProblem(
        slots=(advisor_types.Slot(index=0, colour=0, deep=False),))

    with pytest.raises(ValueError, match="denser than one per 64 bytes"):
        advisor_run.frozen_inventory(owned, problem)


# --------------------------------------------------------------------------
# SEC-024: a character slot that begins a Nightfarer table everywhere


# The vessel id the group header and the Grail records below carry. The reader
# counts the last group's records by the 19000 band a shared Grail sits in, so
# a table built out of any other number would be a table it reads short.
A_SHARED_GRAIL = 19001


def first_marker() -> bytes:
    """The four bytes every walk in `find_loadout_table` starts from."""
    return struct.pack("<I", savefile.HERO_MARKER_BASE + 1)


def loadout_table(heroes: int = 10) -> bytes:
    """Table A as the game writes it: one group per Nightfarer, in order.

    A group is that Nightfarer's marker, the vessel it has selected, and one
    record per shared Grail -- the 120 bytes of `LOADOUT_GROUP`. Ten groups is
    what the real save on this machine carries.
    """
    out = bytearray()
    for hero in range(1, heroes + 1):
        out += struct.pack("<II", savefile.HERO_MARKER_BASE + hero,
                           A_SHARED_GRAIL)
        for _ in range(savefile.GRAILS_PER_HERO):
            out += (struct.pack("<I", A_SHARED_GRAIL)
                    + bytes(savefile.LOADOUT_RECORD - 4))
    return bytes(out)


def slot_with_table_starts(byte_length: int, starts: int) -> bytes:
    """A slot holding one well-formed table and `starts` first markers in all.

    The extra markers are spread evenly over what follows the table and stand
    in empty bytes, so each one is a place a walk begins and none of them is a
    table: what these cases vary is how many walks the slot asks for.
    """
    table = loadout_table()
    buffer = bytearray(byte_length)
    buffer[:len(table)] = table
    stride = (byte_length - len(table)) // max(starts - 1, 1)
    stride -= stride % 4
    for index in range(starts - 1):
        off = len(table) + index * stride
        buffer[off:off + 4] = first_marker()
    return bytes(buffer)


def prepared_save(folder: pathlib.Path, slot: bytes) -> pathlib.Path:
    """A .sl2 carrying this one character slot, encrypted as the game does.

    Written into the test's own temporary folder and never into the player's
    save folder: a prepared file there is the attack these cases are about,
    and the player has a copy of the program running.
    """
    name = "USER_DATA000".encode("utf-16-le") + b"\0\0"
    iv = bytes(range(16))
    member = iv + AES.new(savefile.SAVE_KEY, AES.MODE_CBC, iv).encrypt(slot)

    header = bytearray(0x40)
    header[0:4] = b"BND4"
    struct.pack_into("<I", header, 0x0C, 1)          # one member
    struct.pack_into("<Q", header, 0x20, 0x20)       # bytes per member header
    header[0x30] = 1                                 # names are UTF-16
    entry = bytearray(0x20)
    struct.pack_into("<Q", entry, 8, len(member))
    struct.pack_into("<I", entry, 16, 0x60 + len(name))
    struct.pack_into("<I", entry, 20, 0x60)

    path = folder / "NR0000.sl2"
    path.write_bytes(bytes(header) + bytes(entry) + name + member)
    return path


def test_a_slot_packed_with_table_starts_is_a_data_error():
    """Every fourth byte a first marker, which is what a prepared file writes.

    Measured on this machine before the limit: 1,03 s per MiB of slot against
    36 ms for the real save, linear in the file, and every save found is read
    at startup on the thread that builds the window -- 24 s of nothing before
    the player has touched anything. Neither SEC-022 limit sees it: the slot
    needs a single well-formed relic record and no more.
    """
    blob = first_marker() * (64 * 1024 // 4)

    with pytest.raises(ValueError,
                       match="denser than one table per 1920 bytes"):
        within_time_limit(lambda: savefile.find_loadout_table(blob))


def test_the_refusal_over_packed_table_starts_names_no_file_path():
    """The rule the packed-inventory message is held to as well (SEC-023).

    The save folder is named after the Steam account id, so a message that
    named the file would put that id into every screenshot and bug report the
    failure produces.
    """
    with pytest.raises(ValueError) as raised:
        savefile.find_loadout_table(first_marker() * (64 * 1024 // 4))

    message = str(raised.value)
    assert "\\" not in message and "/" not in message, message
    assert ".sl2" not in message.lower(), message
    assert "save folder" in message and "rescan" in message, message


def test_a_slot_with_as_many_table_starts_as_it_has_room_for_is_read():
    """The control at the boundary: the limit must not cost a real table.

    7 680 bytes have room for four tables at one per 1 920, and this slot
    begins four -- the well-formed one and three bare markers. A case that
    only proved the error path would pass just as well against a reader that
    refuses everything.
    """
    blob = slot_with_table_starts(7680, starts=4)

    groups = savefile.find_loadout_table(blob)

    assert [off for off, _ in groups] == [n * savefile.LOADOUT_GROUP
                                          for n in range(10)]
    assert {records for _, records in groups} == {savefile.GRAILS_PER_HERO}


def test_one_table_start_more_than_the_slot_can_hold_is_a_data_error():
    """The other side of that boundary, one marker further on."""
    blob = slot_with_table_starts(7680, starts=5)

    with pytest.raises(ValueError, match="more than 4 places"):
        within_time_limit(lambda: savefile.find_loadout_table(blob))


def test_a_slot_at_a_real_saves_table_density_is_read_in_full():
    """The control the limit exists for: an ordinary save still reads.

    The real save on this machine, read read-only on 2026-09-07: the one
    character slot that carries a table has a single first marker on a
    four-byte boundary in 1 048 608 bytes, and the thirteen other slots of
    that file have none. This is that shape in miniature -- one table in
    64 KiB, where the limit allows 34.
    """
    blob = slot_with_table_starts(64 * 1024, starts=1)

    groups = savefile.find_loadout_table(blob)

    assert len(groups) == 10


def test_the_refusal_reaches_the_window_instead_of_the_console(tmp_path):
    """Where the sentence lands: the note under the save on the Build page.

    `_scan_save` catches ValueError out of `read_loadouts` and keeps it as
    `Inventory.loadout_error`, which the label prints after "no stored builds
    could be read". So this file reads its one relic, reports no builds and
    says why -- rather than reaching the player as a traceback, which is where
    the second SEC-022 limit still stands (QA-193).

    One valid relic record and the rest markers is the whole of the attack: it
    is enough to have an inventory built, and neither SEC-022 limit has
    anything to say about a slot this sparse.
    """
    slot = bytearray(first_marker() * (64 * 1024 // 4))
    slot[0:len(DOUBLED_ID)] = DOUBLED_ID
    path = prepared_save(tmp_path, bytes(slot))
    relic_meta = {KNOWN_RELIC_ID: {"id": KNOWN_RELIC_ID, "name": "Test relic",
                                   "colour": 0}}

    found = within_time_limit(lambda: inventory._scan_save(
        path, {KNOWN_RELIC_ID}, set(), None, mode=savefile.FAST))
    assert found is not None
    inv = inventory.build({"relics": list(relic_meta.values())}, found)

    assert inv.relic_count == 1
    assert inv.loadouts == []
    assert "denser than one table per 1920 bytes" in inv.loadout_error
