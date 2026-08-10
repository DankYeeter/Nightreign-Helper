"""Where the data extracted from the player's own game is kept.

Nothing here ships with the program. The snapshot and the icon pack are
built from the installed game on first run, and they have to land somewhere
writable -- which the directory holding the executable is not, once it is in
Program Files or unpacked into a PyInstaller temp folder. So they go to the
per-user cache instead.
"""

from __future__ import annotations

import os
import pathlib

APP_NAME = "NightreignHelper"


def cache_dir() -> pathlib.Path:
    """The per-user directory holding everything built from the game."""
    local = os.environ.get("LOCALAPPDATA")
    if local:
        base = pathlib.Path(local)
    else:
        # Not Windows, or a stripped environment. XDG, then a dotfile.
        xdg = os.environ.get("XDG_CACHE_HOME")
        base = pathlib.Path(xdg) if xdg else pathlib.Path.home() / ".cache"

    return base / APP_NAME


def snapshot_path() -> pathlib.Path:
    return cache_dir() / "nightreign_data.json"


def icons_dir() -> pathlib.Path:
    return cache_dir() / "icons"
