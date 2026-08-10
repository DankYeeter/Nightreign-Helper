"""Open Nightreign's regulation.bin and hand back its param files."""

from __future__ import annotations

import pathlib

from Crypto.Cipher import AES

from . import bnd4, dcx
from .bnd4 import BinderFile
from .keys import NIGHTREIGN_REGULATION_KEY


def decrypt(path: pathlib.Path | str) -> bytes:
    """AES-256-CBC decrypt regulation.bin; the IV is the first 16 bytes."""
    raw = pathlib.Path(path).read_bytes()
    iv, body = raw[:16], raw[16:]
    return AES.new(NIGHTREIGN_REGULATION_KEY, AES.MODE_CBC, iv).decrypt(body)


def load_params(path: pathlib.Path | str) -> list[BinderFile]:
    """regulation.bin -> decrypted -> DCX/ZSTD -> BND4 -> *.param members."""
    return bnd4.read(dcx.decompress(decrypt(path)))
