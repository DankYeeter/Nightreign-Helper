"""A game file the program was handed cannot read past a buffer, allocate
without bound, expand without bound, or name something the file never held.

The counterpart to test_hostile_savefile.py, one layer further in: everything
here comes out of the installation rather than the save, and the player's own
installation is well formed, which is exactly why none of these states was
ever reached by accident.

* **SEC-005**, `test_a_payload_*`: the DDS reader handed the payload straight
  to `texture2ddecoder`, which never compares what it was given against what
  the image needs -- it walks `ceil(w/4) * ceil(h/4)` blocks and advances the
  input pointer blindly. A header claiming a larger image than its bytes can
  fill read past the end of the buffer in native code.
* **SEC-006**, `test_a_member_claiming_*`: the decompressed size out of a DCX
  header sized the output buffer with nothing in between. Four bytes could ask
  for four gibibytes.
* **SEC-010**, `test_a_layout_*`: the atlas layout XML went through
  ElementTree, which expands the entities a document declares about itself.
  Thirteen nested ten-fold entities are a gigabyte, and the file decided how
  much memory the program used.
* **SEC-014**, `test_*_part_name_*`: the map reader walked to the end of a
  record looking for a terminator and, finding none, returned what it had
  collected -- a name the map never contained, on which a boss is then
  identified. Not a hang like SEC-001, a fabrication.
"""

from __future__ import annotations

import struct
import time

import pytest

from nrdata import bossdata, dds, icons, oodle

# BC1 stores one 4x4 block of pixels in eight bytes, so an 8x8 image is four
# blocks and exactly 32 bytes. Every size case below is measured against that.
BC1_BLOCK_BYTES = 8
IMAGE_EDGE = 8
BC1_PAYLOAD_BYTES = 32

# Long enough that a machine under load cannot fail it, short enough that an
# expansion the size of the old one cannot pass it.
EXPANSION_LIMIT_SECONDS = 10.0


def dds_file(fourcc: bytes, width: int, height: int, payload: bytes) -> bytes:
    """A DDS with a well-formed header and whatever payload is asked for."""
    header = bytearray(128)
    header[0:4] = b"DDS "
    struct.pack_into("<I", header, 4, 124)          # header size
    struct.pack_into("<II", header, 12, height, width)
    struct.pack_into("<I", header, 76, 32)          # pixel format size
    struct.pack_into("<I", header, 80, 0x4)         # DDPF_FOURCC
    header[84:88] = fourcc
    return bytes(header) + payload


# ---------------------------------------------------------------------------
# SEC-005 -- the native texture decoder


def test_a_payload_one_byte_short_is_refused():
    short = dds_file(b"DXT1", IMAGE_EDGE, IMAGE_EDGE,
                     b"\0" * (BC1_PAYLOAD_BYTES - 1))
    with pytest.raises(ValueError) as raised:
        dds.decode(short)
    # The message has to name both numbers, or a report of it says nothing
    # about which file is wrong.
    assert str(BC1_PAYLOAD_BYTES - 1) in str(raised.value)
    assert str(BC1_PAYLOAD_BYTES) in str(raised.value)


def test_a_payload_of_exactly_the_right_size_still_decodes():
    exact = dds_file(b"DXT1", IMAGE_EDGE, IMAGE_EDGE,
                     b"\0" * BC1_PAYLOAD_BYTES)
    width, height, rgba = dds.decode(exact)
    assert (width, height) == (IMAGE_EDGE, IMAGE_EDGE)
    assert len(rgba) == IMAGE_EDGE * IMAGE_EDGE * 4


def test_the_needed_size_counts_a_partial_edge_block_whole():
    # 5x5 is two blocks by two, not one and a quarter: the decoder walks whole
    # blocks, so a bound that rounded down would be a bound below the read.
    assert dds.payload_needed(5, 5, BC1_BLOCK_BYTES) == 4 * BC1_BLOCK_BYTES


def test_a_payload_short_for_an_odd_size_is_refused():
    needed = dds.payload_needed(5, 5, BC1_BLOCK_BYTES)
    with pytest.raises(ValueError):
        dds.decode(dds_file(b"DXT1", 5, 5, b"\0" * (needed - 1)))


def test_a_header_claiming_no_pixels_is_refused():
    with pytest.raises(ValueError):
        dds.decode(dds_file(b"DXT1", 0, IMAGE_EDGE, b"\0" * BC1_PAYLOAD_BYTES))


def test_a_file_too_short_to_hold_a_header_is_refused():
    with pytest.raises(ValueError):
        dds.decode(b"DDS " + b"\0" * 40)


def test_a_dx10_file_without_its_extended_header_is_refused():
    # The extended header is read from offset 128, so a file that stops at 128
    # used to be unpacked from bytes that are not there.
    with pytest.raises(ValueError):
        dds.decode(dds_file(b"DX10", IMAGE_EDGE, IMAGE_EDGE, b""))


def test_an_unknown_fourcc_never_reaches_a_decoder():
    with pytest.raises(NotImplementedError):
        dds.decode(dds_file(b"ZZZZ", IMAGE_EDGE, IMAGE_EDGE,
                            b"\0" * BC1_PAYLOAD_BYTES))


# ---------------------------------------------------------------------------
# SEC-006 -- the size an archive member claims


def test_a_member_claiming_more_than_the_ceiling_is_refused():
    with pytest.raises(ValueError) as raised:
        oodle.decompress(b"\0" * 16, oodle.MAX_UNCOMPRESSED_SIZE + 1)
    assert str(oodle.MAX_UNCOMPRESSED_SIZE) in str(raised.value)


def test_a_member_claiming_nothing_is_refused():
    with pytest.raises(ValueError):
        oodle.decompress(b"\0" * 16, 0)


def test_a_member_claiming_a_negative_size_is_refused():
    with pytest.raises(ValueError):
        oodle.decompress(b"\0" * 16, -1)


def test_a_member_within_the_ceiling_gets_past_the_size_check(monkeypatch):
    """The ceiling has to let the game's own archives through.

    Reaching "the DLL is not loaded" is the proof that the size was accepted;
    the DLL is deliberately taken away first so the test can never call into
    it with a payload that is not one.
    """
    monkeypatch.setattr(oodle, "_handle", None)
    with pytest.raises(oodle.OodleUnavailable):
        oodle.decompress(b"\0" * 16, oodle.MAX_UNCOMPRESSED_SIZE)


def test_the_ceiling_clears_the_largest_member_the_game_ships():
    # Measured over the 5103 unencrypted Oodle members of data0-3.bdt in an
    # installation: the largest unpacks to 982464964 bytes. A ceiling under
    # that would refuse an asset the planner has to read.
    largest_measured = 982_464_964
    assert oodle.MAX_UNCOMPRESSED_SIZE > largest_measured


# ---------------------------------------------------------------------------
# SEC-010 -- entity expansion in the atlas layout


def entity_bomb(levels: int) -> str:
    """A layout whose sprite name expands to 10**levels characters."""
    declarations = ['<!ENTITY e0 "A">']
    for level in range(1, levels + 1):
        body = f"&e{level - 1};" * 10
        declarations.append(f'<!ENTITY e{level} "{body}">')
    return (
        '<?xml version="1.0"?>'
        f'<!DOCTYPE TextureAtlas [{"".join(declarations)}]>'
        f'<TextureAtlas><SubTexture name="&e{levels};" x="0" y="0" '
        'width="1" height="1"/></TextureAtlas>'
    )


def test_a_layout_that_declares_entities_is_refused():
    with pytest.raises(icons.LayoutError):
        icons.read_subtextures(entity_bomb(2))


def test_a_layout_bomb_is_refused_before_it_expands():
    """Not the case SEC-010 rests on: expat refuses this one on its own.

    Take the entity guard out of icons.read_subtextures and this stays green
    -- expat caps entity expansion itself and raises long before the gigabyte
    exists. So the case tells nothing about this program and is no evidence
    that the refusal works; that hangs on
    test_a_layout_that_declares_entities_is_refused alone. Kept because the
    ceiling it watches is expat's, and a parser that lifted it would turn this
    red, which is worth knowing.
    """
    started = time.monotonic()
    with pytest.raises(icons.LayoutError):
        # Nine levels is a gigabyte if anything expands it, and nothing here
        # should get as far as looking.
        icons.read_subtextures(entity_bomb(9))
    assert time.monotonic() - started < EXPANSION_LIMIT_SECONDS


def test_a_layout_that_is_not_well_formed_is_refused():
    with pytest.raises(icons.LayoutError):
        icons.read_subtextures("<TextureAtlas><SubTexture></TextureAtlas>")


def test_an_ordinary_layout_still_reads():
    sprites = icons.read_subtextures(
        '<TextureAtlas imagePath="a.png">'
        '<SubTexture name="MENU_ItemIcon_00001.png" x="1" y="2" '
        'width="3" height="4"/>'
        '<SubTexture name="MENU_ItemIcon_00002.png" x="5" y="6" '
        'width="7" height="8"/>'
        "</TextureAtlas>"
    )
    assert [s["name"] for s in sprites] == ["MENU_ItemIcon_00001.png",
                                            "MENU_ItemIcon_00002.png"]
    assert sprites[0]["x"] == "1"


# ---------------------------------------------------------------------------
# SEC-014 -- a part name the map never held


PART_HEADER_BYTES = 32
NAME_AT = 8
PART_NAME = "c7500_0000"


def msb_with_one_part(record: bytes) -> bytes:
    """The smallest blob `bossdata._parts` reads one part out of.

    The section is located by its own name string and the entry offsets are
    read relative to the pointer that names it, so the shape matters even
    though the content does not: a count, a pointer to the section name, and
    one offset per entry plus one for the end.

    The gap between the end of the section and its name string is not padding
    for padding's sake. The reader finds the section header by searching
    backwards for the pointer value, so a name sitting exactly at the section
    end would make the end offset and the pointer the same eight bytes and the
    search would settle on the wrong one.
    """
    needle = "PARTS_PARAM_ST".encode("utf-16-le") + b"\0\0"
    gap = b"\0" * 8
    record_at = PART_HEADER_BYTES
    end_at = record_at + len(record)
    string_at = end_at + len(gap)
    blob = bytearray()
    blob += struct.pack("<I", 0)                    # unused
    blob += struct.pack("<I", 3)                    # count: two offsets follow
    blob += struct.pack("<Q", string_at)            # pointer to the name
    blob += struct.pack("<QQ", record_at, end_at)   # this entry, and the end
    assert len(blob) == PART_HEADER_BYTES
    blob += record
    blob += gap
    blob += needle
    return bytes(blob)


def part_record(name: str, terminated: bool) -> bytes:
    text = name.encode("utf-16-le")
    return (struct.pack("<Q", NAME_AT) + text
            + (b"\0\0" if terminated else b""))


def test_a_terminated_part_name_is_still_read():
    blob = msb_with_one_part(part_record(PART_NAME, terminated=True))
    assert [name for name, _record in bossdata._parts(blob)] == [PART_NAME]


def test_an_unterminated_part_name_is_a_data_error():
    """Not a shorter name -- no name.

    The old reader returned "c7500_0000" here as well, from a record that
    never said where the name ended. A boss is identified by that name, so a
    fabrication is worse than losing the map.
    """
    blob = msb_with_one_part(part_record(PART_NAME, terminated=False))
    with pytest.raises(ValueError):
        bossdata._parts(blob)


def test_a_part_name_offset_past_the_record_is_a_data_error():
    record = struct.pack("<Q", 4096) + PART_NAME.encode("utf-16-le") + b"\0\0"
    with pytest.raises(ValueError):
        bossdata._parts(msb_with_one_part(record))
