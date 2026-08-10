"""FMG string table reader (the localised text format)."""

from __future__ import annotations

import struct


def read(data: bytes) -> dict[int, str]:
    """Return {string id -> text}. Empty entries are skipped."""
    big_endian = data[1] != 0
    version = data[2]
    e = ">" if big_endian else "<"
    wide = version == 2  # DS3/ER/NR use 64-bit offsets

    if wide:
        group_count, string_count = struct.unpack_from(e + "II", data, 0x0C)
        (offsets_offset,) = struct.unpack_from(e + "Q", data, 0x18)
        groups_at = 0x28
        off_fmt, off_size = e + "Q", 8
    else:
        group_count, string_count = struct.unpack_from(e + "II", data, 0x0C)
        (offsets_offset,) = struct.unpack_from(e + "I", data, 0x14)
        groups_at = 0x1C
        off_fmt, off_size = e + "I", 4

    # Groups map a contiguous run of ids onto a contiguous run of offsets.
    out: dict[int, str] = {}
    for i in range(group_count):
        offset_index, first_id, last_id = struct.unpack_from(
            e + "iii", data, groups_at + i * 16
        )
        for n, string_id in enumerate(range(first_id, last_id + 1)):
            idx = offset_index + n
            if idx >= string_count:
                continue
            (str_offset,) = struct.unpack_from(
                off_fmt, data, offsets_offset + idx * off_size
            )
            if not str_offset:
                continue
            end = str_offset
            while data[end : end + 2] != b"\0\0":
                end += 2
            text = data[str_offset:end].decode("utf-16-le", "replace")
            if text:
                out[string_id] = text
    return out
