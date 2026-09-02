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
"""

from __future__ import annotations

import struct

import pytest

from nrdata import dds

# BC1 stores one 4x4 block of pixels in eight bytes, so an 8x8 image is four
# blocks and exactly 32 bytes. Every size case below is measured against that.
BC1_BLOCK_BYTES = 8
IMAGE_EDGE = 8
BC1_PAYLOAD_BYTES = 32


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
