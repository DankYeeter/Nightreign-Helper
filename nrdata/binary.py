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
        if utf16:
            end = offset
            while self.data[end : end + 2] != b"\0\0":
                end += 2
            return self.data[offset:end].decode("utf-16-le", "replace")
        end = self.data.index(b"\0", offset)
        return self.data[offset:end].decode("shift-jis", "replace")


def reverse_bits(value: int) -> int:
    out = 0
    for _ in range(8):
        out = (out << 1) | (value & 1)
        value >>= 1
    return out
