"""Cut individual icons out of the menu sprite atlases.

Addressing, verified against the params:
  hero portrait   MENU_MenuIcon_{properPortraitId}.png
  item icon       MENU_ItemIcon_{iconId:05d}.png
Sprite rectangles come from the .layout XML in 01_common_h.sblytbnd.dcx, the
pixels from the matching atlas in 01_common_h.tpf.dcx.
"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass
from xml.etree import ElementTree

from . import bnd4, dds, dvdbnd, oodle, tpf

LAYOUT_PATH = "/menu/01_common_h.sblytbnd.dcx"
ATLAS_PATH = "/menu/01_common_h.tpf.dcx"

# The DLC patch added a second layout/atlas pair for Scholar and Undertaker.
# Its path is in no published dictionary, so it is addressed by name hash --
# located by scanning unnamed entries for a layout mentioning icon 41080.
DLC_LAYOUT_HASH = 0x24505FCC2D785AB5
DLC_ATLAS_HASH = 0x77AFABA2209B66D9

PORTRAIT_SPRITE = "MENU_MenuIcon_{id}.png"
ITEM_SPRITE = "MENU_ItemIcon_{id:05d}.png"


@dataclass
class Sprite:
    atlas: str
    x: int
    y: int
    width: int
    height: int


class IconSource:
    """Lazily decodes only the atlases actually asked for."""

    def __init__(self, game_dir: pathlib.Path):
        oodle.load(game_dir)
        archives = dvdbnd.open_all(game_dir)
        self._archive = next(a for a in archives.values() if LAYOUT_PATH in a)

        self.sprites: dict[str, Sprite] = {}
        self._load_layout(bnd4.read(self._archive.read(LAYOUT_PATH)))

        self._dlc_available = DLC_LAYOUT_HASH in self._archive.entries
        if self._dlc_available:
            self._load_layout(
                bnd4.read(self._archive.read_hash(DLC_LAYOUT_HASH))
            )

        self._textures: dict[str, bytes] | None = None
        self._decoded: dict[str, object] = {}

    def _load_layout(self, members) -> None:
        for member in members:
            if not member.basename.endswith(".layout"):
                continue
            atlas = member.basename[: -len(".layout")]
            root = ElementTree.fromstring(member.data.decode("utf-8", "replace"))
            for sub in root.findall("SubTexture"):
                self.sprites[sub.get("name")] = Sprite(
                    atlas=atlas,
                    x=int(sub.get("x")),
                    y=int(sub.get("y")),
                    width=int(sub.get("width")),
                    height=int(sub.get("height")),
                )

    def _atlas_image(self, name: str):
        from PIL import Image

        if name in self._decoded:
            return self._decoded[name]

        if self._textures is None:
            self._textures = {
                t.name.strip("\x00"): t.dds
                for t in tpf.read(self._archive.read(ATLAS_PATH))
            }
            if self._dlc_available:
                self._textures.update({
                    t.name.strip("\x00"): t.dds
                    for t in tpf.read(self._archive.read_hash(DLC_ATLAS_HASH))
                })

        key = name if name in self._textures else next(
            (k for k in self._textures if k.startswith(name)), None
        )
        if key is None:
            raise KeyError(f"atlas {name} not present")

        width, height, rgba = dds.decode(self._textures[key])
        image = Image.frombytes("RGBA", (width, height), rgba)
        self._decoded[name] = image
        return image

    def crop(self, sprite_name: str, size: int | None = None):
        from PIL import Image

        sprite = self.sprites.get(sprite_name)
        if sprite is None:
            return None
        atlas = self._atlas_image(sprite.atlas)
        box = (sprite.x, sprite.y, sprite.x + sprite.width, sprite.y + sprite.height)
        icon = atlas.crop(box)
        if size:
            icon = icon.resize((size, size), Image.LANCZOS)
        return icon

    def portrait(self, portrait_id: int, size: int | None = None):
        return self.crop(PORTRAIT_SPRITE.format(id=portrait_id), size)

    def item_icon(self, icon_id: int, size: int | None = None):
        return self.crop(ITEM_SPRITE.format(id=icon_id), size)

    def release(self) -> None:
        """Drop decoded atlases; each one is ~67 MB of RGBA."""
        self._decoded.clear()
        self._textures = None
