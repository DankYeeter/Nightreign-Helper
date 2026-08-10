"""DCX container decompression.

Nightreign's regulation.bin uses DCX with a ZSTD payload, so this needs no
external codec DLL. DEFLATE is supported as a fallback for other files.
"""

from __future__ import annotations

import struct
import zlib


def is_dcx(data: bytes) -> bool:
    return data[:4] == b"DCX\0"


def decompress(data: bytes) -> bytes:
    """Unwrap a DCX container and return the payload."""
    if not is_dcx(data):
        return data

    dcs = data.find(b"DCS\0")
    dcp = data.find(b"DCP\0")
    dca = data.find(b"DCA\0")
    if dcs < 0 or dcp < 0 or dca < 0:
        raise ValueError("malformed DCX: missing DCS/DCP/DCA block")

    uncompressed_size, compressed_size = struct.unpack_from(">II", data, dcs + 4)
    method = data[dcp + 4 : dcp + 8]
    (dca_header_size,) = struct.unpack_from(">I", data, dca + 4)

    start = dca + dca_header_size
    payload = data[start : start + compressed_size]

    if method == b"ZSTD":
        import zstandard

        out = zstandard.ZstdDecompressor().decompress(
            payload, max_output_size=uncompressed_size
        )
    elif method == b"DFLT":
        out = zlib.decompress(payload)
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
