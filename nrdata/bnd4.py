"""BND4 archive reader (enough of it to open regulation and msgbnd files)."""

from __future__ import annotations

from dataclasses import dataclass

from .binary import Reader, reverse_bits
from . import dcx

# Binder format bits, as used by SoulsFormats. Note these apply to the format
# byte *after* the bit-order normalisation done in _read_format().
FMT_IDS = 0b0000_0010
FMT_NAMES1 = 0b0000_0100
FMT_NAMES2 = 0b0000_1000
FMT_LONG_OFFSETS = 0b0001_0000
FMT_COMPRESSION = 0b0010_0000

# Where the member headers begin.
HEADER_SIZE = 0x40

# The fixed part of a member header: 4 bytes of flags and padding, an int32
# that is always -1, then the compressed size as an int64.
_ENTRY_FIXED = 16


def _entry_fields_size(has_compression: bool, has_long_offsets: bool,
                       has_ids: bool, has_names: bool) -> int:
    """How many bytes one member header must hold for this archive's format.

    Derived from the fields the walk below actually reads rather than fixed at
    a number, because which fields are present is exactly what the format bits
    have just decided.
    """
    return (_ENTRY_FIXED
            + (8 if has_compression else 0)     # uncompressed size
            + (8 if has_long_offsets else 4)    # data offset
            + (4 if has_ids else 0)
            + (4 if has_names else 0))


def _check_entry_table(data: bytes, file_count: int, entry_size: int,
                       fields_size: int) -> None:
    """The count and the stride come out of the archive and together they
    steer the walk over its member headers, so they are measured against the
    archive's own size before anything is read (SEC-002). Unchecked, a count
    of four billion is walked as four billion, and a stride too small for the
    fields it must hold puts every member on top of the last.
    """
    if (entry_size < fields_size
            or HEADER_SIZE + file_count * entry_size > len(data)):
        raise ValueError(
            f"archive claims {file_count} members of {entry_size} bytes each, "
            f"holding {fields_size} bytes of fields, which do not fit in "
            f"{len(data)} bytes"
        )


@dataclass
class BinderFile:
    id: int
    name: str
    data: bytes

    @property
    def basename(self) -> str:
        return self.name.replace("\\", "/").rsplit("/", 1)[-1]


def _read_format(raw: int, bit_big_endian: bool) -> int:
    if bit_big_endian or ((raw & 0b0000_0001) != 0 and (raw & 0b1000_0000) == 0):
        return raw
    return reverse_bits(raw)


@dataclass
class SplitEntry:
    """One member of a BXF4 pair: metadata only, payload lives elsewhere."""
    id: int
    name: str
    offset: int
    size: int

    @property
    def basename(self) -> str:
        return self.name.replace("\\", "/").rsplit("/", 1)[-1]


def read_split_header(data: bytes) -> list[SplitEntry]:
    """Parse a detached BHF4 header (the .*bhd of a bhd/bdt pair)."""
    r = Reader(data)
    r.magic(b"BHF4")
    r.skip(2)
    r.skip(3)
    big_endian = r.u8() != 0
    bit_big_endian = r.u8() == 0
    r.skip(1)

    r.big = big_endian
    file_count = r.u32()
    r.u64()
    r.ascii(8)
    file_header_size = r.u64()
    r.u64()
    unicode_names = r.u8() != 0
    fmt = _read_format(r.u8(), bit_big_endian)

    has_compression = bool(fmt & FMT_COMPRESSION)
    has_long_offsets = bool(fmt & FMT_LONG_OFFSETS)
    has_ids = bool(fmt & FMT_IDS)
    has_names = bool(fmt & (FMT_NAMES1 | FMT_NAMES2))

    _check_entry_table(
        data, file_count, file_header_size,
        _entry_fields_size(has_compression, has_long_offsets,
                           has_ids, has_names),
    )

    out: list[SplitEntry] = []
    for i in range(file_count):
        e = Reader(data, HEADER_SIZE + i * file_header_size, big_endian)
        e.skip(4)
        e.i32()
        size = e.u64()
        if has_compression:
            e.u64()
        offset = e.u64() if has_long_offsets else e.u32()
        entry_id = e.i32() if has_ids else i
        name = f"file_{i}"
        if has_names:
            name = r.cstr_at(e.u32(), utf16=unicode_names)
        out.append(SplitEntry(id=entry_id, name=name, offset=offset, size=size))
    return out


def read(data: bytes) -> list[BinderFile]:
    """Parse a BND4 archive into its member files."""
    if dcx.is_dcx(data):
        data = dcx.decompress(data)

    r = Reader(data)
    r.magic(b"BND4")
    r.skip(2)  # unk04, unk05
    r.skip(3)  # padding
    big_endian = r.u8() != 0
    bit_big_endian = r.u8() == 0
    r.skip(1)

    r.big = big_endian
    file_count = r.u32()
    r.u64()  # header size, always 0x40
    r.ascii(8)  # version string
    file_header_size = r.u64()
    r.u64()  # end of file headers
    unicode_names = r.u8() != 0
    fmt = _read_format(r.u8(), bit_big_endian)
    extended = r.u8()
    r.skip(1)
    r.u32()
    r.u64()  # buckets offset

    has_compression = bool(fmt & FMT_COMPRESSION)
    has_long_offsets = bool(fmt & FMT_LONG_OFFSETS)
    has_ids = bool(fmt & FMT_IDS)
    has_names = bool(fmt & (FMT_NAMES1 | FMT_NAMES2))

    _check_entry_table(
        data, file_count, file_header_size,
        _entry_fields_size(has_compression, has_long_offsets,
                           has_ids, has_names),
    )

    files: list[BinderFile] = []
    for i in range(file_count):
        e = Reader(data, HEADER_SIZE + i * file_header_size, big_endian)
        e.skip(1)  # file flags
        e.skip(3)  # padding
        e.i32()  # always -1
        compressed_size = e.u64()
        uncompressed_size = e.u64() if has_compression else compressed_size
        offset = e.u64() if has_long_offsets else e.u32()
        file_id = e.i32() if has_ids else i

        name = f"file_{i}"
        if has_names:
            name_offset = e.u32()
            name = r.cstr_at(name_offset, utf16=unicode_names)

        blob = data[offset : offset + compressed_size]
        if dcx.is_dcx(blob):
            blob = dcx.decompress(blob)
        elif has_compression and uncompressed_size != compressed_size:
            raise NotImplementedError(f"unhandled inline compression in {name}")

        files.append(BinderFile(id=file_id, name=name, data=blob))

    return files
