"""Access to the icon pack built from the player's own installation."""

from __future__ import annotations

import json
import pathlib

from PySide6.QtGui import QIcon, QPixmap

from . import paths
from .datasource import _base_dir


class IconPack:
    @staticmethod
    def locate() -> pathlib.Path:
        """Where the icon pack is, or where it should be built.

        The pack is extracted from the game into the per-user cache, so that
        is checked first. The other two are source trees that still have a
        locally built pack sitting beside the package.
        """
        base = _base_dir()
        candidates = (paths.icons_dir(), base / "icons", base / "data" / "icons")
        return next(
            (d for d in candidates if (d / "manifest.json").exists()),
            paths.icons_dir(),
        )

    def __init__(self) -> None:
        self.dir = self.locate()
        self.manifest: dict = {"portraits": {}, "items": {}, "variants": {},
                               "menu": {}}
        path = self.dir / "manifest.json"
        if path.exists():
            self.manifest = json.loads(path.read_text(encoding="utf-8"))
        self._cache: dict[str, QPixmap] = {}

    @property
    def available(self) -> bool:
        return bool(self.manifest["portraits"] or self.manifest["items"])

    def _pixmap(self, filename: str | None) -> QPixmap | None:
        if not filename:
            return None
        if filename in self._cache:
            return self._cache[filename]
        path = self.dir / filename
        if not path.exists():
            return None
        pixmap = QPixmap(str(path))
        self._cache[filename] = pixmap
        return pixmap

    def portrait(self, hero_id: int) -> QPixmap | None:
        return self._pixmap(self.manifest["portraits"].get(str(hero_id)))

    def variants(self, hero_id: int) -> list[dict]:
        return self.manifest["variants"].get(str(hero_id), [])

    def variant(self, texture_id: int) -> QPixmap | None:
        return self._pixmap(f"variant_{texture_id}.png")

    def item(self, icon_id: int) -> QPixmap | None:
        return self._pixmap(self.manifest["items"].get(str(icon_id)))

    def menu(self, icon_id: int) -> QPixmap | None:
        """Boss art, which lives in the MenuIcon atlas rather than the item one."""
        return self._pixmap(self.manifest.get("menu", {}).get(str(icon_id)))

    def item_icon(self, icon_id: int) -> QIcon | None:
        pixmap = self.item(icon_id)
        return QIcon(pixmap) if pixmap else None
