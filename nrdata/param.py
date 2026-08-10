"""PARAM table reader.

Layout was verified against Nightreign's own regulation.bin: 64-bit row
descriptors (id / data offset / name offset) starting at 0x40, with the row
stride implied by (stringsOffset - dataOffset) / rowCount.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass

from .binary import Reader
from .paramdef import STRUCT_CODES, Field, ParamDef


@dataclass
class ParamRow:
    id: int
    name: str
    values: dict[str, object]

    def __getitem__(self, key: str):
        return self.values[key]

    def get(self, key: str, default=None):
        return self.values.get(key, default)


@dataclass
class ParamTable:
    param_type: str
    data_version: int
    row_size: int
    rows: list[ParamRow]
    # True when the paramdef is older than the game's data and only describes a
    # leading prefix of each row. Fields it does cover are still read normally;
    # the trailing bytes the game added are simply not exposed.
    def_is_prefix: bool = False

    def by_id(self, row_id: int) -> ParamRow | None:
        for r in self.rows:
            if r.id == row_id:
                return r
        return None


def _read_field(data: bytes, base: int, f: Field):
    off = base + f.offset

    if f.type == "dummy8":
        return None
    if f.type == "fixstr":
        return data[off : off + f.size].split(b"\0")[0].decode("shift-jis", "replace")
    if f.type == "fixstrW":
        return data[off : off + f.size].split(b"\0\0")[0].decode("utf-16-le", "replace")

    code = STRUCT_CODES[f.type]
    if f.bits is not None:
        (raw,) = struct.unpack_from("<" + code, data, off)
        mask = (1 << f.bits) - 1
        return (raw >> f.bit_offset) & mask
    if f.count > 1:
        return list(struct.unpack_from(f"<{f.count}{code}", data, off))
    (value,) = struct.unpack_from("<" + code, data, off)
    return value


def read(data: bytes, pdef: ParamDef | None = None, strict: bool = False) -> ParamTable:
    r = Reader(data)
    strings_offset = r.u32()
    r.u16()  # short data offset, unused in this variant
    r.u16()  # unk06
    data_version = r.u16()
    row_count = r.u16()

    r.seek(0x10)
    param_type_offset = r.u64()
    param_type = r.cstr_at(param_type_offset) if param_type_offset else ""

    r.seek(0x30)
    data_offset = r.u64()

    row_size = (strings_offset - data_offset) // row_count if row_count else 0

    # A def shorter than the row is a stale def describing a prefix -- usable.
    # A def longer than the row would read past the row and is never safe.
    def_is_prefix = False
    if pdef is not None and pdef.row_size != row_size:
        if pdef.row_size < row_size:
            def_is_prefix = True
        else:
            msg = (
                f"paramdef {pdef.param_type} is larger ({pdef.row_size} B) than the "
                f"actual row ({row_size} B) in {param_type or '?'}; refusing to decode"
            )
            if strict:
                raise ValueError(msg)
            pdef = None

    rows: list[ParamRow] = []
    for i in range(row_count):
        e = Reader(data, 0x40 + i * 24)
        row_id = e.i64()
        row_data_offset = e.u64()
        name_offset = e.u64()

        name = ""
        if name_offset:
            try:
                name = r.cstr_at(name_offset, utf16=True)
            except (ValueError, IndexError):
                name = ""

        values: dict[str, object] = {}
        if pdef is not None:
            for f in pdef.fields:
                if f.is_padding:
                    continue
                values[f.name] = _read_field(data, row_data_offset, f)

        rows.append(ParamRow(id=row_id, name=name, values=values))

    return ParamTable(
        param_type=param_type,
        data_version=data_version,
        row_size=row_size,
        rows=rows,
        def_is_prefix=def_is_prefix,
    )
