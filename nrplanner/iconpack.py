"""Access to the icon pack built from the player's own installation."""

from __future__ import annotations

import json
import time
import pathlib

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QIcon, QPixmap
from PySide6.QtWidgets import QLabel

from . import paths

#: How tall a symbol stands beside a line of text, in logical pixels.
INLINE_ICON = 14

#: A damage type or status, however a tab spells it, to the game's own symbol.
#: The relic screen's filter list holds the first twelve; the three grey
#: physical icons were pinned by looking at them enlarged -- club on rubble is
#: Strike, the broad blade Slash, the gauntlet thrust Pierce. `Physical`, which
#: the game shows for the sum of those, wears the plain one. Scarlet Rot, Sleep
#: and Death Blight come from the equipment screen's status symbols instead:
#: see iconbuild's UI_SPRITES for the working.
TYPE_SPRITES = {
    "standard": "MENU_FL_40141.png",
    "physical": "MENU_FL_40141.png",
    "strike": "MENU_FL_40142.png",
    "slash": "MENU_FL_40143.png",
    "pierce": "MENU_FL_40144.png",
    "holy": "MENU_FL_40145.png",
    "magic": "MENU_FL_40146.png",
    "frostbite": "MENU_FL_40147.png",
    "frost": "MENU_FL_40147.png",
    "fire": "MENU_FL_40148.png",
    "lightning": "MENU_FL_40150.png",
    "madness": "MENU_FL_40151.png",
    "poison": "MENU_FL_40172.png",
    "blood loss": "MENU_FL_40173.png",
    "scarlet rot": "MENU_PropertyIcon_31231.png",
    "rot": "MENU_PropertyIcon_31231.png",
    "sleep": "MENU_PropertyIcon_31234.png",
    "death blight": "MENU_PropertyIcon_31236.png",
    "death": "MENU_PropertyIcon_31236.png",
}

#: The slot-colour gems, by relic colour. The game has exactly four, so a White
#: slot shows none.
GEM_SPRITES = {
    0: "MENU_MenuIcon_40480.png",
    1: "MENU_MenuIcon_40481.png",
    2: "MENU_MenuIcon_40483.png",   # Yellow
    3: "MENU_MenuIcon_40482.png",   # Green
}


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


def inside_pack(base: pathlib.Path, filename: str | None) -> pathlib.Path | None:
    """The file a manifest entry names, or None if it names another place.

    Every file name here comes out of manifest.json, which is an ordinary
    file in an ordinary folder: anything that can write there decides which
    paths this program opens. Joined straight onto the pack folder,
    "..\\..\\somewhere\\secret.png" and "C:\\somewhere\\secret.png" both
    leave it -- the second silently, because joining an absolute path onto a
    folder discards the folder (SEC-008).

    So the join is not trusted; the result is resolved and has to still be
    under `base`, which the caller hands over resolved. Resolving both sides
    is what makes that a fact rather than a spelling comparison -- a junction
    or a "." in the middle changes the text without changing where it lands.

    A name that is absolute, rooted or climbs is refused on sight, before
    that: `resolve()` stats what it resolves, and for a UNC name that is a
    question to the network, asked at every launch (SEC-046). Shared with the
    launch check in `firstrun`, which walks the same manifest and must refuse
    the same names.
    """
    if not filename:
        return None
    name = pathlib.PurePath(filename)
    if name.drive or name.root or ".." in name.parts:
        return None
    try:
        path = (base / filename).resolve()
    except (OSError, ValueError):
        # A name Windows will not even resolve is not one of ours.
        return None
    return path if path.is_relative_to(base) else None


class IconPack:
    def __init__(self) -> None:
        self.dir = paths.icons_dir()
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
        self._cache: dict[str, QPixmap | None] = {}
        self._tags: dict[tuple, str] = {}

    @property
    def available(self) -> bool:
        return bool(self.manifest["portraits"] or self.manifest["items"])

    def _inside_pack(self, filename: str | None) -> pathlib.Path | None:
        return inside_pack(self.dir.resolve(), filename)

    def _pixmap(self, filename: str | None) -> QPixmap | None:
        if not filename:
            return None
        if filename in self._cache:
            return self._cache[filename]
        path = self._inside_pack(filename)
        if path is None or not path.exists():
            # Cached: unlike a failed read below, a refused name or an absent
            # file stays so, since nothing writes the pack once it is open.
            self._cache[filename] = None
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

    def status(self, icon_id: int | None) -> QPixmap | None:
        """A status symbol: what an effect or a world-event buff shows."""
        return self._pixmap(self.manifest.get("status", {}).get(str(icon_id)))

    def inline(self, group: str, key, size: int = INLINE_ICON) -> str:
        """An `<img>` for rich text, empty where the pack has no such symbol.

        Kept once asked for: a sheet redraw asks for dozens, and each answer
        is a path resolved on disk that no longer changes while the pack is
        open.
        """
        asked = (group, str(key), size)
        if asked not in self._tags:
            path = self._inside_pack(self.manifest.get(group, {}).get(str(key)))
            self._tags[asked] = (
                f"<img src='{path.as_uri()}' width='{size}' height='{size}'"
                f" align='middle'>&nbsp;"
                if path is not None and path.exists() else "")
        return self._tags[asked]


def inline(icons: IconPack | None, group: str, key,
           size: int = INLINE_ICON) -> str:
    """`IconPack.inline` for a widget that may have been given no pack."""
    return icons.inline(group, key, size) if icons is not None else ""


def inline_type(icons: IconPack | None, label: str,
                size: int = INLINE_ICON) -> str:
    """The `<img>` of a damage type or status, empty if it has no symbol."""
    return inline(icons, "ui", TYPE_SPRITES.get(label.lower()), size)


def type_pixmap(icons: IconPack | None, label: str) -> QPixmap | None:
    """The pixmap of a damage type or status, for a combo box or a table."""
    if icons is None:
        return None
    return icons.ui(TYPE_SPRITES.get(label.lower()))


def sharp(pixmap: QPixmap, size: int) -> QPixmap:
    """A pixmap at `size` logical pixels, rendered for this screen's scale."""
    ratio = QGuiApplication.primaryScreen().devicePixelRatio()
    scaled = pixmap.scaled(round(size * ratio), round(size * ratio),
                           Qt.KeepAspectRatio, Qt.SmoothTransformation)
    scaled.setDevicePixelRatio(ratio)
    return scaled


def symbol_label(pixmap: QPixmap, size: int = INLINE_ICON) -> QLabel:
    """A symbol standing beside a plain-text label (AK-29: names are no markup)."""
    label = QLabel()
    label.setPixmap(sharp(pixmap, size))
    label.setFixedSize(size, size)
    label.setStyleSheet("border: none; background: transparent;")
    return label
