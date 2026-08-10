"""TPF texture container reader.

A TPF holds one or more DDS textures plus their names. Only the header layout
is parsed here; decoding the DDS payload is left to the caller.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass


@dataclass
class Texture:
    name: str
    dds: bytes
    format: int
    mipmaps: int


def read(data: bytes) -> list[Texture]:
    if data[:4] != b"TPF\0":
        raise ValueError(f"not a TPF container (magic {data[:4]!r})")

    _data_size, file_count = struct.unpack_from("<II", data, 4)
    platform = data[0x0C]
    flag2 = data[0x0D]
    encoding = data[0x0E]

    big_endian = platform in (1, 2, 4)
    e = ">" if big_endian else "<"

    out: list[Texture] = []
    pos = 0x10
    for _ in range(file_count):
        file_offset, file_size = struct.unpack_from(e + "II", data, pos)
        fmt, _type, mipmaps, _flags = struct.unpack_from(e + "BBBB", data, pos + 8)
        pos += 12

        if flag2 == 2:
            pos += 4  # extended header pointer, unused here

        name_offset = struct.unpack_from(e + "I", data, pos)[0]
        pos += 8  # name offset + unknown

        if encoding == 1:
            # The terminator must be found on an even boundary; a naive search
            # can land on the low byte of a character and cut it in half.
            end = name_offset
            while data[end : end + 2] != b"\0\0":
                end += 2
            name = data[name_offset:end].decode("utf-16-le", "replace")
        else:
            end = data.index(b"\0", name_offset)
            name = data[name_offset:end].decode("shift-jis", "replace")

        out.append(
            Texture(
                name=name,
                dds=data[file_offset : file_offset + file_size],
                format=fmt,
                mipmaps=mipmaps,
            )
        )
    return out
