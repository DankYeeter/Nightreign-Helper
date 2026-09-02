"""Minimal endian-aware binary reader for FromSoftware container formats."""

from __future__ import annotations

import struct


class Reader:
    def __init__(self, data: bytes, offset: int = 0, big_endian: bool = False):
        self.data = data
        self.pos = offset
        self.big = big_endian

    @property
    def _e(self) -> str:
        return ">" if self.big else "<"

    def seek(self, pos: int) -> "Reader":
        self.pos = pos
        return self

    def skip(self, n: int) -> "Reader":
        self.pos += n
        return self

    def _unpack(self, fmt: str, size: int):
        (value,) = struct.unpack_from(self._e + fmt, self.data, self.pos)
        self.pos += size
        return value

    def u8(self) -> int:
        return self._unpack("B", 1)

    def i8(self) -> int:
        return self._unpack("b", 1)

    def u16(self) -> int:
        return self._unpack("H", 2)

    def i16(self) -> int:
        return self._unpack("h", 2)

    def u32(self) -> int:
        return self._unpack("I", 4)

    def i32(self) -> int:
        return self._unpack("i", 4)

    def u64(self) -> int:
        return self._unpack("Q", 8)

    def i64(self) -> int:
        return self._unpack("q", 8)

    def f32(self) -> float:
        return self._unpack("f", 4)

    def f64(self) -> float:
        return self._unpack("d", 8)

    def bytes(self, n: int) -> bytes:
        out = self.data[self.pos : self.pos + n]
        self.pos += n
        return out

    def ascii(self, n: int) -> str:
        return self.bytes(n).split(b"\0")[0].decode("ascii", "replace")

    def magic(self, expected: bytes) -> None:
        got = self.bytes(len(expected))
        if got != expected:
            raise ValueError(f"expected magic {expected!r} at {self.pos - len(expected)}, got {got!r}")

    def cstr_at(self, offset: int, utf16: bool = False) -> str:
        return read_cstring(self.data, offset, utf16)


def read_cstring(data: bytes, offset: int, utf16: bool = False) -> str:
    """The NUL-terminated string at `offset`, or a ValueError if there is none.

    The bound is the buffer's own length rather than a chosen constant: a name
    is read exactly as far as there are bytes to read it in, and no further.
    Reaching that bound means the container said "a string starts here" and the
    bytes do not back it up. That is a damaged file and is reported as one --
    not quietly cut short at some invented length, which would hand the caller
    a name the file never held.

    This replaces four copies of a loop that walked forward until it met a
    terminator (SEC-001). Past the end of the buffer the two-byte slice it
    compared is empty forever, so the loop never left, and the copy in the save
    reader ran on the GUI thread before the player had touched anything.

    The UTF-16 terminator only counts at an even distance from the string's
    start. A zero pair on an odd boundary is the high byte of one character
    meeting the low byte of the next, and cutting there would split a
    character in half.
    """
    if not 0 <= offset <= len(data):
        raise ValueError(
            f"string offset {offset} lies outside the {len(data)}-byte buffer"
        )
    if not utf16:
        end = data.find(b"\0", offset)
        if end < 0:
            raise ValueError(
                f"unterminated string at offset {offset} "
                f"in a {len(data)}-byte buffer"
            )
        return data[offset:end].decode("shift-jis", "replace")

    pos = offset
    while True:
        end = data.find(b"\0\0", pos)
        if end < 0:
            raise ValueError(
                f"unterminated UTF-16 string at offset {offset} "
                f"in a {len(data)}-byte buffer"
            )
        if (end - offset) % 2 == 0:
            return data[offset:end].decode("utf-16-le", "replace")
        pos = end + 1


def reverse_bits(value: int) -> int:
    out = 0
    for _ in range(8):
        out = (out << 1) | (value & 1)
        value >>= 1
    return out
