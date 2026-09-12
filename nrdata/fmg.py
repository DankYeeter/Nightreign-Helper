"""FMG string table reader (the localised text format)."""

from __future__ import annotations

import struct

from .binary import read_cstring

# One group header: {int32 offset index, int32 first id, int32 last id}.
GROUP_SIZE = 16


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

    # Three counts out of the file steer the loops below, so each is measured
    # against the file's own size before it steers anything (SEC-002). All
    # three are read unsigned, so there is nothing to check on the low side.
    if groups_at + group_count * GROUP_SIZE > len(data):
        raise ValueError(
            f"FMG claims {group_count} groups, which do not fit in "
            f"{len(data)} bytes"
        )
    if offsets_offset + string_count * off_size > len(data):
        raise ValueError(
            f"FMG claims {string_count} strings, whose offset table does not "
            f"fit in {len(data)} bytes"
        )

    # Groups map a contiguous run of ids onto a contiguous run of offsets.
    out: dict[int, str] = {}
    for i in range(group_count):
        offset_index, first_id, last_id = struct.unpack_from(
            e + "iii", data, groups_at + i * GROUP_SIZE
        )
        # The run of ids is what the inner loop counts off, and it is read
        # from the file as two signed 32-bit numbers: unchecked, one group
        # header can ask for four billion iterations. No group can name more
        # strings than the file says it holds.
        span = last_id - first_id + 1
        if offset_index < 0 or span <= 0 or span > string_count:
            raise ValueError(
                f"FMG group {i} spans ids {first_id}..{last_id} from offset "
                f"index {offset_index}, which is not a run of "
                f"{string_count} strings"
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
            text = read_cstring(data, str_offset, utf16=True)
            if text:
                out[string_id] = text
    return out
