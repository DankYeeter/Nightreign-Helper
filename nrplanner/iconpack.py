"""Access to the icon pack bundled alongside the data snapshot."""

from __future__ import annotations

import json
import pathlib

from PySide6.QtGui import QIcon, QPixmap

from .datasource import _base_dir


class IconPack:
    def __init__(self) -> None:
        # Bundled at "icons" inside the executable, "data/icons" from source.
        base = _base_dir()
        self.dir = next(
            (d for d in (base / "icons", base / "data" / "icons")
             if (d / "manifest.json").exists()),
            base / "icons",
        )
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
