"""PARAMDEF XML parsing (Paramdex format) into a concrete field layout."""

from __future__ import annotations

import pathlib
import re
from dataclasses import dataclass, field
from xml.etree import ElementTree

# Storage size in bytes for each primitive PARAMDEF type.
TYPE_SIZES = {
    "s8": 1,
    "u8": 1,
    "dummy8": 1,
    "s16": 2,
    "u16": 2,
    "s32": 4,
    "u32": 4,
    "f32": 4,
    "angle32": 4,
    "s64": 8,
    "u64": 8,
    "f64": 8,
}

STRUCT_CODES = {
    "s8": "b",
    "u8": "B",
    "s16": "h",
    "u16": "H",
    "s32": "i",
    "u32": "I",
    "f32": "f",
    "angle32": "f",
    "s64": "q",
    "u64": "Q",
    "f64": "d",
}

# "u8 name:1", "dummy8 pad[3]", "f32 rate = 1", "fixstrW label[16]"
_DEF_RE = re.compile(
    r"^\s*(?P<type>\w+)\s+(?P<name>\w+)"
    r"(?:\[(?P<count>\d+)\])?"
    r"(?:\s*:\s*(?P<bits>\d+))?"
    r"(?:\s*=.*)?\s*$"
)


@dataclass
class Field:
    name: str
    type: str
    offset: int          # byte offset of the storage unit holding this field
    size: int            # storage unit size in bytes
    count: int = 1       # array length (fixstr/dummy8 arrays)
    bits: int | None = None
    bit_offset: int = 0

    @property
    def is_padding(self) -> bool:
        return self.type == "dummy8"


@dataclass
class ParamDef:
    param_type: str
    data_version: int
    fields: list[Field] = field(default_factory=list)
    row_size: int = 0

    def by_name(self, name: str) -> Field | None:
        for f in self.fields:
            if f.name == name:
                return f
        return None


def parse(path: pathlib.Path | str) -> ParamDef:
    root = ElementTree.parse(str(path)).getroot()
    param_type = root.findtext("ParamType", "").strip()
    data_version = int(root.findtext("DataVersion", "0").strip())

    fields: list[Field] = []
    offset = 0
    # State for packing consecutive bitfields into one storage unit.
    bit_type: str | None = None
    bit_used = 0
    bit_base = 0

    for node in root.findall("./Fields/Field"):
        raw = node.get("Def", "")
        m = _DEF_RE.match(raw)
        if not m:
            raise ValueError(f"cannot parse field definition {raw!r} in {path}")

        ftype = m.group("type")
        name = m.group("name")
        count = int(m.group("count") or 1)
        bits = int(m.group("bits")) if m.group("bits") else None

        if ftype in ("fixstr", "fixstrW"):
            size = count * (2 if ftype == "fixstrW" else 1)
            bit_type = None
            fields.append(Field(name, ftype, offset, size, count))
            offset += size
            continue

        unit = TYPE_SIZES.get(ftype)
        if unit is None:
            raise ValueError(f"unknown PARAMDEF type {ftype!r} in {path}")

        if bits is not None:
            # dummy8 is just padding; for bit packing it shares storage with u8.
            pack_type = "u8" if ftype == "dummy8" else ftype
            capacity = unit * 8
            if bit_type != pack_type or bit_used + bits > capacity:
                # Start a fresh storage unit for this run of bitfields.
                bit_type = pack_type
                bit_base = offset
                bit_used = 0
                offset += unit
            fields.append(
                Field(name, ftype, bit_base, unit, 1, bits=bits, bit_offset=bit_used)
            )
            bit_used += bits
            continue

        bit_type = None
        size = unit * count
        fields.append(Field(name, ftype, offset, unit, count))
        offset += size

    return ParamDef(param_type, data_version, fields, row_size=offset)


def load_all(defs_dir: pathlib.Path | str) -> dict[str, ParamDef]:
    """Load every def in a Paramdex Defs folder, keyed by file stem."""
    out: dict[str, ParamDef] = {}
    for xml in sorted(pathlib.Path(defs_dir).glob("*.xml")):
        out[xml.stem] = parse(xml)
    return out
