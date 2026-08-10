"""Minimal DDS reader with BC decompression, enough for menu textures."""

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


def decode(dds: bytes) -> tuple[int, int, bytes]:
    """Return (width, height, RGBA bytes) for the top mip level."""
    if dds[:4] != b"DDS ":
        raise ValueError(f"not a DDS file (magic {dds[:4]!r})")

    height, width = struct.unpack_from("<II", dds, 12)
    pf_flags = struct.unpack_from("<I", dds, 80)[0]
    fourcc = dds[84:88]

    header_size = 128
    if fourcc == b"DX10":
        dxgi = struct.unpack_from("<I", dds, 128)[0]
        header_size = 148
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

    payload = dds[header_size:]

    if dxgi in (DXGI_BC7_UNORM, DXGI_BC7_UNORM_SRGB):
        raw = texture2ddecoder.decode_bc7(payload, width, height)
    elif dxgi in (DXGI_BC1_UNORM, DXGI_BC1_UNORM_SRGB):
        raw = texture2ddecoder.decode_bc1(payload, width, height)
    elif dxgi in (DXGI_BC3_UNORM, DXGI_BC3_UNORM_SRGB):
        raw = texture2ddecoder.decode_bc3(payload, width, height)
    elif dxgi == DXGI_BC4_UNORM:
        raw = texture2ddecoder.decode_bc4(payload, width, height)
    elif dxgi == DXGI_BC5_UNORM:
        raw = texture2ddecoder.decode_bc5(payload, width, height)
    else:
        raise NotImplementedError(f"unsupported DXGI format {dxgi}")

    # texture2ddecoder returns BGRA; swap to RGBA.
    out = bytearray(raw)
    out[0::4], out[2::4] = out[2::4], out[0::4]
    return width, height, bytes(out)
