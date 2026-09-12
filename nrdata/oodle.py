"""Oodle (KRAK) decompression via the oo2core DLL that ships with the game.

The DLL cannot be redistributed, so this is only available when the user has
Nightreign installed. regulation.bin itself uses ZSTD and never needs this;
only the data*.bdt archive members do.
"""

from __future__ import annotations

import ctypes
import pathlib

_DLL_NAMES = ("oo2core_9_win64.dll", "oo2core_8_win64.dll", "oo2core_6_win64.dll")
_handle: ctypes.CDLL | None = None

# A DCX header states its decompressed size in 32 bits, so a damaged or
# tampered archive can ask for up to 4 GiB of memory before a single byte has
# been read. Nothing downstream notices: the buffer is allocated first and the
# claim is only compared against what Oodle actually wrote afterwards.
#
# The ceiling is set by what the game's own archives need, with room over. The
# largest Oodle member measured in an installation unpacks to 937 MiB (over
# the 5103 unencrypted KRAK members of data0-3.bdt); two gibibytes clears that
# and still refuses a header that has simply named the largest number it can
# hold. A member above this is not an asset the planner has to read, and
# saying so is better than allocating for it (SEC-006).
MAX_UNCOMPRESSED_SIZE = 2 * 1024 ** 3


class OodleUnavailable(RuntimeError):
    pass


def load(game_dir: pathlib.Path | str) -> None:
    """Load the Oodle DLL from the game directory."""
    global _handle
    if _handle is not None:
        return

    game_dir = pathlib.Path(game_dir)
    for name in _DLL_NAMES:
        candidate = game_dir / name
        if candidate.exists():
            _handle = ctypes.CDLL(str(candidate))
            fn = _handle.OodleLZ_Decompress
            fn.restype = ctypes.c_int64
            fn.argtypes = [
                ctypes.c_void_p, ctypes.c_int64,   # src, srcSize
                ctypes.c_void_p, ctypes.c_int64,   # dst, dstSize
                ctypes.c_int, ctypes.c_int, ctypes.c_int,   # fuzz, crc, verbosity
                ctypes.c_void_p, ctypes.c_int64,   # decBufBase, decBufSize
                ctypes.c_void_p, ctypes.c_void_p,  # callback, userdata
                ctypes.c_void_p, ctypes.c_int64,   # scratch, scratchSize
                ctypes.c_int,                      # threadPhase
            ]
            return

    raise OodleUnavailable(
        f"none of {_DLL_NAMES} found in {game_dir}; Oodle-compressed archive "
        "members cannot be read without the installed game"
    )


def available() -> bool:
    return _handle is not None


def decompress(payload: bytes, uncompressed_size: int) -> bytes:
    # The size is checked before the DLL is, because it is the argument that
    # comes out of a file and the other is a fact about this process.
    if not 0 < uncompressed_size <= MAX_UNCOMPRESSED_SIZE:
        raise ValueError(
            f"archive member claims {uncompressed_size} decompressed bytes, "
            f"outside the 1 to {MAX_UNCOMPRESSED_SIZE} this reader will "
            f"allocate for"
        )
    if _handle is None:
        raise OodleUnavailable("oodle.load(game_dir) has not been called")

    dst = ctypes.create_string_buffer(uncompressed_size)
    written = _handle.OodleLZ_Decompress(
        payload, len(payload),
        dst, uncompressed_size,
        1, 0, 0,
        None, 0, None, None, None, 0,
        3,
    )
    if written != uncompressed_size:
        raise ValueError(
            f"Oodle returned {written} bytes, expected {uncompressed_size}"
        )
    return dst.raw[:uncompressed_size]
