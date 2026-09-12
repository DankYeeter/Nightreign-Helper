"""Minimal DDS reader with BC decompression, enough for menu textures.

The size check in `decode` is not defensive habit, it is load-bearing.
`texture2ddecoder` 1.0.6 never compares the payload it was handed against the
payload the image needs: the bridge fills `view.len` and does not read it
again, and the decoder walks `ceil(w/4) * ceil(h/4)` blocks, advancing the
input pointer blindly by the block size each time. The only bounds check in
the package is on the *output* image. So a texture whose header claims a
larger image than its bytes can fill reads past the end of the buffer in
native code, and the caller is the only place left that can stop it (SEC-005,
evidence in docs/research/R-001.md).
"""

from __future__ import annotations

import struct

import texture2ddecoder

# DXGI formats seen in Nightreign's menu textures.
DXGI_BC1_UNORM = 71
DXGI_BC1_UNORM_SRGB = 72
DXGI_BC3_UNORM = 77
DXGI_BC3_UNORM_SRGB = 78
DXGI_BC4_UNORM = 80
DXGI_BC5_UNORM = 83
DXGI_BC7_UNORM = 98
DXGI_BC7_UNORM_SRGB = 99

HEADER_SIZE = 128
DX10_HEADER_SIZE = 148

# Every block-compressed format stores one 4x4 block of pixels in a fixed
# number of bytes: eight where a block carries a single colour line, sixteen
# where it carries two.
BLOCK = 4

# Decoder and bytes-per-block, per format. This table is also the list of
# formats that may be decoded at all: a DXGI value that is not a key here
# never reaches the native code, so an unknown format cannot be handed to a
# decoder that would read it as something else.
_FORMATS = {
    DXGI_BC1_UNORM: (texture2ddecoder.decode_bc1, 8),
    DXGI_BC1_UNORM_SRGB: (texture2ddecoder.decode_bc1, 8),
    DXGI_BC3_UNORM: (texture2ddecoder.decode_bc3, 16),
    DXGI_BC3_UNORM_SRGB: (texture2ddecoder.decode_bc3, 16),
    DXGI_BC4_UNORM: (texture2ddecoder.decode_bc4, 8),
    DXGI_BC5_UNORM: (texture2ddecoder.decode_bc5, 16),
    DXGI_BC7_UNORM: (texture2ddecoder.decode_bc7, 16),
    DXGI_BC7_UNORM_SRGB: (texture2ddecoder.decode_bc7, 16),
}


def payload_needed(width: int, height: int, block_bytes: int) -> int:
    """Bytes the top mip level of this image occupies.

    The same arithmetic the decoder does, which is what makes it the right
    bound: a partial block at the right or bottom edge is stored whole.
    """
    blocks = ((width + BLOCK - 1) // BLOCK) * ((height + BLOCK - 1) // BLOCK)
    return blocks * block_bytes


def decode(dds: bytes) -> tuple[int, int, bytes]:
    """Return (width, height, RGBA bytes) for the top mip level."""
    if dds[:4] != b"DDS ":
        raise ValueError(f"not a DDS file (magic {dds[:4]!r})")
    if len(dds) < HEADER_SIZE:
        raise ValueError(
            f"a DDS header is {HEADER_SIZE} bytes, this file is {len(dds)}"
        )

    height, width = struct.unpack_from("<II", dds, 12)
    pf_flags = struct.unpack_from("<I", dds, 80)[0]
    fourcc = dds[84:88]

    header_size = HEADER_SIZE
    if fourcc == b"DX10":
        if len(dds) < DX10_HEADER_SIZE:
            raise ValueError(
                f"a DX10 DDS header is {DX10_HEADER_SIZE} bytes, this file "
                f"is {len(dds)}"
            )
        dxgi = struct.unpack_from("<I", dds, HEADER_SIZE)[0]
        header_size = DX10_HEADER_SIZE
    elif fourcc == b"DXT1":
        dxgi = DXGI_BC1_UNORM
    elif fourcc in (b"DXT4", b"DXT5"):
        dxgi = DXGI_BC3_UNORM
    elif fourcc == b"BC4U":
        dxgi = DXGI_BC4_UNORM
    elif fourcc == b"BC5U":
        dxgi = DXGI_BC5_UNORM
    elif not (pf_flags & 0x4):
        raise NotImplementedError("uncompressed DDS is not supported")
    else:
        raise NotImplementedError(f"unsupported FourCC {fourcc!r}")

    known = _FORMATS.get(dxgi)
    if known is None:
        raise NotImplementedError(f"unsupported DXGI format {dxgi}")
    decoder, block_bytes = known

    if width <= 0 or height <= 0:
        raise ValueError(f"DDS header declares a {width}x{height} image")

    payload = dds[header_size:]
    needed = payload_needed(width, height, block_bytes)
    if len(payload) < needed:
        raise ValueError(
            f"DDS payload is {len(payload)} bytes; a {width}x{height} image "
            f"in DXGI format {dxgi} needs {needed}"
        )

    raw = decoder(payload, width, height)

    # texture2ddecoder returns BGRA; swap to RGBA.
    out = bytearray(raw)
    out[0::4], out[2::4] = out[2::4], out[0::4]
    return width, height, bytes(out)
