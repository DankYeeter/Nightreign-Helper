"""Access to the icon pack built from the player's own installation."""

from __future__ import annotations

import json
import time
import pathlib

from PySide6.QtGui import QIcon, QPixmap

from . import paths
from .datasource import _base_dir


def _read_with_retries(path: pathlib.Path, attempts: int = 4) -> bytes | None:
    """Read a file that may be briefly held by something else.

    Seen in practice: OSError 22 on open() while getsize() succeeds, across
    a whole directory, minutes after it was written -- the signature of a
    scanner or sync client sitting on new files. A short backoff outlasts
    that; a genuine failure still returns None rather than raising.
    """
    delay = 0.05
    for attempt in range(attempts):
        try:
            return path.read_bytes()
        except OSError:
            if attempt == attempts - 1:
                return None
            time.sleep(delay)
            delay *= 3
    return None


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
                               "menu": {}, "ui": {}}
        path = self.dir / "manifest.json"
        if path.exists():
            # A read can fail transiently -- a scanner or sync client holding
            # the directory right after a rebuild produced OSError 22 on
            # files whose sizes read fine. The manifest is the one file that
            # takes the whole pack down with it, so it gets retries, and a
            # final failure degrades to "no icons" rather than a crash.
            raw = _read_with_retries(path)
            if raw is not None:
                try:
                    self.manifest = json.loads(raw.decode("utf-8"))
                except ValueError:
                    pass
        self._cache: dict[str, QPixmap] = {}

    @property
    def available(self) -> bool:
        return bool(self.manifest["portraits"] or self.manifest["items"])

    def _inside_pack(self, filename: str | None) -> pathlib.Path | None:
        """The file a manifest entry names, or None if it names another place.

        Every file name here comes out of manifest.json, which is an ordinary
        file in an ordinary folder: anything that can write there decides
        which paths this program opens. Joined straight onto the pack folder,
        "..\\..\\somewhere\\secret.png" and "C:\\somewhere\\secret.png" both
        leave it -- the second silently, because joining an absolute path onto
        a folder discards the folder (SEC-008).

        So the join is not trusted; the result is resolved and has to still be
        under the pack. Resolving both sides is what makes that a fact rather
        than a spelling comparison -- a junction or a "." in the middle
        changes the text without changing where it lands.
        """
        if not filename:
            return None
        base = self.dir.resolve()
        try:
            path = (base / filename).resolve()
        except OSError:
            # A name Windows will not even resolve is not one of ours.
            return None
        return path if path.is_relative_to(base) else None

    def _pixmap(self, filename: str | None) -> QPixmap | None:
        if not filename:
            return None
        if filename in self._cache:
            return self._cache[filename]
        path = self._inside_pack(filename)
        if path is None or not path.exists():
            return None
        pixmap = QPixmap(str(path))
        if pixmap.isNull():
            # The direct load failed. Read the bytes ourselves, with
            # retries, and decode from memory -- the two fail for different
            # reasons, so one regularly works where the other does not.
            raw = _read_with_retries(path)
            if raw:
                pixmap = QPixmap()
                pixmap.loadFromData(raw)
        if pixmap.isNull():
            # Deliberately NOT cached: caching a null here is what turned a
            # transient read failure at startup into a session with no
            # icons. Leaving the miss uncached lets a later call succeed.
            return None
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

    def ui_path(self, sprite: str) -> str | None:
        """Absolute path of a UI sprite, for embedding in rich text."""
        path = self._inside_pack(self.manifest.get("ui", {}).get(sprite))
        return str(path) if path is not None and path.exists() else None

    def ui(self, sprite: str) -> QPixmap | None:
        """One of the game's own UI sprites, by its sprite name."""
        return self._pixmap(self.manifest.get("ui", {}).get(sprite))

    def item_icon(self, icon_id: int) -> QIcon | None:
        pixmap = self.item(icon_id)
        return QIcon(pixmap) if pixmap else None
