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
"""

from __future__ import annotations

import struct
import threading

import pytest

from nrdata import binary, savefile

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
