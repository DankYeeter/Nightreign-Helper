"""Decide where the planner's data comes from.

Preferred: extract live from the installed game, so the numbers follow patches.
Fallback: the snapshot bundled into the executable.
"""

from __future__ import annotations

import json
import pathlib
import sys

BUNDLED_NAME = "nightreign_data.json"


def _base_dir() -> pathlib.Path:
    # PyInstaller unpacks bundled data into _MEIPASS.
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return pathlib.Path(meipass)
    return pathlib.Path(__file__).resolve().parent


def bundled_path() -> pathlib.Path:
    """Where the snapshot is, preferring the one built from the live game.

    The cache comes first because it is the only writable location once the
    program is installed, and so the only place a rebuild after a game patch
    can land. The two fallbacks are for running from a source tree that still
    has a locally built snapshot beside the package.
    """
    from . import paths

    base = _base_dir()
    for candidate in (
        paths.snapshot_path(),
        base / "data" / BUNDLED_NAME,
        base / BUNDLED_NAME,
    ):
        if candidate.exists():
            return candidate
    return paths.snapshot_path()


def icon_path() -> pathlib.Path | None:
    """The application icon, or None if it was not packaged."""
    base = _base_dir()
    for candidate in (base / "data" / "icon.ico", base / "icon.ico"):
        if candidate.exists():
            return candidate
    return None


def defs_dir() -> pathlib.Path | None:
    base = _base_dir()
    for candidate in (
        base / "paramdefs",
        base.parent / "vendor" / "Paramdex" / "NR" / "Defs",
    ):
        if candidate.is_dir():
            return candidate
    return None


def _snapshot() -> dict | None:
    path = bundled_path()
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _regulation_matches(snapshot: dict) -> bool:
    """Is the bundled snapshot still current for the installed game?

    Extracting takes ~16 seconds, so it is only worth doing when the game's
    regulation.bin has actually changed since the snapshot was built. Hashing
    2 MB costs a few milliseconds.
    """
    import hashlib

    from nrdata import gamefiles

    recorded = snapshot.get("meta", {}).get("regulation_sha256")
    if not recorded:
        return False

    game = gamefiles.find_game_dir()
    if game is None:
        # No install to compare against; the snapshot is all we have.
        return True

    path = game / "regulation.bin"
    if not path.exists():
        return True
    if path.stat().st_size != snapshot["meta"].get("regulation_size"):
        return False
    return hashlib.sha256(path.read_bytes()).hexdigest() == recorded


def load_data(prefer_live: bool = True) -> dict:
    """Return the planner dataset, with the build maths configured for it.

    model.configure has to run before anything computes a build: it is what
    tells the model which fields multiply and which add, taken from the data
    rather than guessed from the field name.
    """
    data = _load_data(prefer_live)
    from . import model

    model.configure(data)
    return data


def _load_data(prefer_live: bool = True) -> dict:
    """Return the planner dataset.

    Uses the bundled snapshot whenever it still matches the installed game,
    and only falls back to a full extraction after a game patch.
    """
    snapshot = _snapshot()

    if snapshot is not None and prefer_live:
        try:
            if _regulation_matches(snapshot):
                return snapshot
        except Exception:  # noqa: BLE001 - a failed check must not block startup
            return snapshot

    if prefer_live:
        try:
            from nrdata import extract, gamefiles

            game = gamefiles.find_game_dir()
            defs = defs_dir()
            if game is not None and defs is not None:
                fresh = extract.build(game, defs)
                fresh.setdefault("meta", {})["regenerated"] = True
                return fresh
        except Exception:  # noqa: BLE001 - fall back to the snapshot
            pass

    if snapshot is None:
        raise FileNotFoundError(_no_data_message())
    return snapshot


def _no_data_message() -> str:
    """Say which of the two things is missing, rather than both.

    This is the whole of the no-game experience, so it has to explain the
    design rather than just report a missing file: the tool ships no game
    content on purpose, which is why an install is required and not merely
    preferred.
    """
    from nrdata import gamefiles

    lines = ["Nightreign Helper could not read your game data."]

    if gamefiles.find_game_dir() is None:
        lines += [
            "",
            "No ELDEN RING NIGHTREIGN installation was found.",
            "",
            "This tool ships no game data of its own -- every value it shows is "
            "read from the copy of the game on your machine. So the game has to "
            "be installed for it to have anything to show.",
            "",
            "If the game is installed somewhere unusual, it was looked for "
            "through Steam's library list and on the drives C to H.",
        ]
    elif defs_dir() is None:
        lines += [
            "",
            "The game was found, but the param definitions were not.",
            "",
            f"Expected them at: {_base_dir() / 'paramdefs'}",
            "",
            "These describe the layout of the game's data tables and are "
            "required to read anything. Reinstalling Nightreign Helper should "
            "restore them.",
        ]
    else:
        lines += [
            "",
            "The game and the definitions were both found, but reading them "
            "failed. This usually means the game was updated in a way the tool "
            "does not understand yet.",
        ]

    return "\n".join(lines)
