"""Random access into the data*.bhd/bdt archive pairs.

Layout was read off Nightreign's own data0.bhd:
  header  : "BHD5", bucketCount @0x10, bucketsOffset @0x14, salt (len-prefixed)
  bucket  : u32 count, u32 offset
  file    : u64 hash, u32 paddedSize, u32 unpaddedSize,
            u64 offset, u64 shaOffset, u64 aesKeyOffset
"""

from __future__ import annotations

import pathlib
import struct
from dataclasses import dataclass

from Crypto.Cipher import AES

from . import bhd5, dcx

FILE_HEADER_SIZE = 40


@dataclass
class FileEntry:
    hash: int
    padded_size: int
    unpadded_size: int
    offset: int
    aes_key_offset: int


class Archive:
    """One data*.bhd / data*.bdt pair."""

    def __init__(self, bhd_path: pathlib.Path, pem: str):
        self.bdt_path = bhd_path.with_suffix(".bdt")
        self.header = bhd5.decrypt_header(bhd_path.read_bytes(), pem)
        if self.header[:4] != b"BHD5":
            raise ValueError(f"{bhd_path.name}: wrong key, no BHD5 magic")

        bucket_count, buckets_offset = struct.unpack_from("<II", self.header, 0x10)
        # The bucket count and every per-bucket file count are read out of the
        # header and steer the two loops below, so each is measured against
        # the header's own size first (SEC-002). Unchecked, one number in a
        # damaged header asks for four billion FileEntry objects.
        size = len(self.header)
        if buckets_offset + bucket_count * 8 > size:
            raise ValueError(
                f"{bhd_path.name}: {bucket_count} buckets do not fit in a "
                f"{size}-byte header"
            )
        self.entries: dict[int, FileEntry] = {}
        for i in range(bucket_count):
            count, offset = struct.unpack_from("<II", self.header, buckets_offset + i * 8)
            if offset + count * FILE_HEADER_SIZE > size:
                raise ValueError(
                    f"{bhd_path.name}: bucket {i} claims {count} files, which "
                    f"do not fit in a {size}-byte header"
                )
            for j in range(count):
                (h, padded, unpadded, off, _sha, aes) = struct.unpack_from(
                    "<QIIQQQ", self.header, offset + j * FILE_HEADER_SIZE
                )
                self.entries[h] = FileEntry(h, padded, unpadded, off, aes)

    def __contains__(self, path: str) -> bool:
        return bhd5.path_hash(path) in self.entries

    def read_range_hash(self, name_hash: int, offset: int, size: int) -> bytes:
        """Ranged read of an entry addressed by hash rather than by name."""
        entry = self.entries[name_hash]
        if entry.aes_key_offset:
            raise ValueError("entry is encrypted; ranged reads are unavailable")
        with open(self.bdt_path, "rb") as fh:
            fh.seek(entry.offset + offset)
            data = fh.read(size)
        return dcx.decompress(data) if dcx.is_dcx(data) else data

    def read_range(self, path: str, offset: int, size: int) -> bytes:
        """Read a slice of an entry without loading the whole thing.

        Only valid for unencrypted entries; the large data files are stored in
        the clear, which is what makes streaming a 454 MB archive practical.
        """
        entry = self.entries[bhd5.path_hash(path)]
        if entry.aes_key_offset:
            raise ValueError(f"{path} is encrypted; ranged reads are unavailable")
        with open(self.bdt_path, "rb") as fh:
            fh.seek(entry.offset + offset)
            data = fh.read(size)
        return dcx.decompress(data) if dcx.is_dcx(data) else data

    def read_hash(self, name_hash: int) -> bytes:
        """Read an entry whose path name is unknown.

        Some assets added by the DLC patch have paths that are not in any
        published dictionary, but their hashes are stable, so they can still
        be addressed directly.
        """
        return self._read_entry(self.entries[name_hash])

    def read(self, path: str) -> bytes:
        return self._read_entry(self.entries[bhd5.path_hash(path)])

    def _read_entry(self, entry: FileEntry) -> bytes:
        with open(self.bdt_path, "rb") as fh:
            fh.seek(entry.offset)
            data = bytearray(fh.read(entry.padded_size))

        if entry.aes_key_offset:
            self._decrypt_ranges(data, entry.aes_key_offset)

        size = entry.unpadded_size or entry.padded_size
        out = bytes(data[:size])
        return dcx.decompress(out) if dcx.is_dcx(out) else out

    def _decrypt_ranges(self, data: bytearray, key_offset: int) -> None:
        key = self.header[key_offset : key_offset + 16]
        (range_count,) = struct.unpack_from("<I", self.header, key_offset + 16)
        cipher = AES.new(key, AES.MODE_ECB)
        for i in range(range_count):
            start, end = struct.unpack_from("<qq", self.header, key_offset + 20 + i * 16)
            if start < 0 or end < 0 or start >= end:
                continue
            end = min(end, len(data))
            length = (end - start) // 16 * 16
            if length > 0:
                data[start : start + length] = cipher.decrypt(
                    bytes(data[start : start + length])
                )


def open_all(game_dir: pathlib.Path) -> dict[str, Archive]:
    """Open every archive whose key is known."""
    out: dict[str, Archive] = {}
    for name, pem in bhd5.ARCHIVE_KEYS.items():
        path = game_dir / f"{name}.bhd"
        if path.exists():
            out[name] = Archive(path, pem)
    return out
