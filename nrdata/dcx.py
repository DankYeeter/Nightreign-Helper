"""DCX container decompression.

Nightreign's regulation.bin uses DCX with a ZSTD payload, so this needs no
external codec DLL. DEFLATE is supported as a fallback for other files.
"""

from __future__ import annotations

import struct
import zlib

from .binary import NotWhatItClaims

# A DCX header states its decompressed size in 32 bits, so a damaged or
# tampered archive can ask for up to 4 GiB of memory before a single byte has
# been read. The ceiling is set by what the game's own archives need, with
# room over: the largest member measured in an installation unpacks to
# 937 MiB (over the 5103 unencrypted KRAK members of data0-3.bdt); two
# gibibytes clears that and still refuses a header that has simply named the
# largest number it can hold. A member above this is not an asset the
# planner has to read, and saying so is better than allocating for it
# (SEC-006). Lives here rather than in `oodle` because `dcx` is the only
# caller that needs it before importing that module (SEC-037).
MAX_UNCOMPRESSED_SIZE = 2 * 1024 ** 3


def is_dcx(data: bytes) -> bool:
    return data[:4] == b"DCX\0"


def _over_ceiling_message(uncompressed_size: int) -> str:
    return (
        f"DCX member claims {uncompressed_size} decompressed bytes, over the "
        f"{MAX_UNCOMPRESSED_SIZE} this reader will allocate for"
    )


def decompress(data: bytes) -> bytes:
    """Unwrap a DCX container and return the payload."""
    if not is_dcx(data):
        return data

    dcs = data.find(b"DCS\0")
    dcp = data.find(b"DCP\0")
    dca = data.find(b"DCA\0")
    if dcs < 0 or dcp < 0 or dca < 0:
        raise NotWhatItClaims("malformed DCX: missing DCS/DCP/DCA block")

    uncompressed_size, compressed_size = struct.unpack_from(">II", data, dcs + 4)
    method = data[dcp + 4 : dcp + 8]
    (dca_header_size,) = struct.unpack_from(">I", data, dca + 4)

    start = dca + dca_header_size
    payload = data[start : start + compressed_size]

    if method == b"ZSTD":
        import zstandard

        if uncompressed_size > MAX_UNCOMPRESSED_SIZE:
            raise NotWhatItClaims(_over_ceiling_message(uncompressed_size))
        out = zstandard.ZstdDecompressor().decompress(
            payload, max_output_size=uncompressed_size
        )
    elif method == b"DFLT":
        decompressor = zlib.decompressobj()
        out = decompressor.decompress(payload, MAX_UNCOMPRESSED_SIZE)
        if decompressor.unconsumed_tail:
            raise NotWhatItClaims(_over_ceiling_message(uncompressed_size))
    elif method == b"KRAK":
        from . import oodle

        out = oodle.decompress(payload, uncompressed_size)
    else:
        raise NotImplementedError(
            f"DCX compression {method!r} is not supported (only ZSTD and DFLT)"
        )

    if len(out) != uncompressed_size:
        raise ValueError(
            f"DCX size mismatch: got {len(out)}, header claims {uncompressed_size}"
        )
    return out
