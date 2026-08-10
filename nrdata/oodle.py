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
