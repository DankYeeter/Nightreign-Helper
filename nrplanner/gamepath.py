"""Where the game is, and where the user said it is.

One place answers the question "where is the game" for the whole program
(AD-030). Before this there were four call sites of `gamefiles.find_game_dir`
and each meant something slightly different by it: one drove the first-run
build, one decided whether the snapshot was still current, one extracted
after a patch, and one told the user that nothing had been found. A folder
the user had picked himself would have reached the first of them and none of
the other three, so the program would have gone on saying it found no
installation while working out of one.

**Two keys, both fixed, and the path lives in the value.** `paths/game` and
`paths/save`, in the settings store `favourites` names -- the shape of
`ui/scale` and `ui/panes`. The three settings losses of cycles 4 and 5 all
had the same cause: text the user had typed became part of a *key*, and
`remove` ran over it (`chalices.py:190-320`). Nothing here derives a key from
anything; the key space this adds is two, for good.

**Nothing here ever calls `QSettings.remove`.** A damaged entry costs one
check per start and is left where it is; `remove` costs more than the key it
names -- on Windows it takes the group of the same name with it, which is how
two of the three losses happened. The values are overwritten, and only by a
folder the user confirmed.
"""

from __future__ import annotations

import os
import pathlib

from PySide6.QtCore import QSettings

from nrdata import gamefiles

from . import favourites

GAME_KEY = "paths/game"
SAVE_KEY = "paths/save"

# Longer than this and the text cannot be something remember_game() wrote:
# the figure is the one Nachtrag XI (R3) names for a stored entry, and it is
# already far past the longest path Windows will hand out. Treated as damage
# rather than trusted to pathlib, so that a stat() is never spent on it.
MAX_STORED_CHARACTERS = 16_383


def _settings() -> QSettings:
    """The one store, under the names the environment may have moved."""
    return QSettings(favourites.ORG, favourites.APP)


def _remembered(key: str) -> pathlib.Path | None:
    """The path stored under this key, or None if there is none to use.

    Damaged is treated as absent (AD-030): empty, not text, text carrying a
    null byte, text too long to be a path, text that is not an absolute path,
    or text pathlib will not take. Resolution simply carries on to the
    automatic route. The entry is *not* deleted -- see the module docstring.

    Absent and empty are the same answer here, because the store has no
    third one: a key that was never written reads back as the default.

    What is stored is always an absolute path (`remember_game` writes one),
    so anything else in this value came from somewhere else and is not a
    folder this program may act on.

    `type=str` is not decoration. Where the store is a file rather than the
    Windows registry, QSettings hands back a *list* as soon as the text holds
    a comma, and a folder may well be called `Elden Ring, alt`; the path
    would silently become a different kind of thing than the one written. On
    the registry it is the check below that catches that value instead -- the
    two cover one hole from two sides, and neither is spare.
    """
    raw = _settings().value(key, "", type=str)
    if not isinstance(raw, str):
        return None
    if not raw or "\0" in raw or len(raw) > MAX_STORED_CHARACTERS:
        return None
    try:
        stored = pathlib.Path(raw)
    except (ValueError, OSError):
        return None
    return stored if stored.is_absolute() else None


def _remember(key: str, path) -> None:
    """Write a confirmed path, as the operating system spells it."""
    _settings().setValue(key, os.fspath(pathlib.Path(path)))


def remembered_game() -> pathlib.Path | None:
    """The game folder the user confirmed, as stored. Not checked here."""
    return _remembered(GAME_KEY)


def remembered_save() -> pathlib.Path | None:
    """The save file the user picked, as stored. Not checked here."""
    return _remembered(SAVE_KEY)


def remember_game(path) -> None:
    """Keep a game folder the user confirmed.

    The only way `paths/game` is ever written. A find by the automatic route
    is not a confirmation and does not come through here: a drive comes back,
    and what the user said last is what he said (UI_SPEC 6).
    """
    _remember(GAME_KEY, path)


def remember_save(path) -> None:
    """Keep a save file the user picked. The only way `paths/save` moves."""
    _remember(SAVE_KEY, path)


def resolve_game() -> pathlib.Path | None:
    """Where the game is: the remembered folder, else the automatic find.

    The chain of AK-107, and the whole of it:

    1. a remembered folder that still passes `looks_like_the_game` is used,
       and nothing else runs;
    2. remembered but not valid any more -- moved, uninstalled, external
       drive unplugged, unreachable share -- counts as absent, never as an
       error, and the search goes on;
    3. `find_game_dir()` decides the rest. Its answer is used as it stands
       and **is not written back**: it was not confirmed by anybody.

    The predicate in step 1 is the one that accepted the folder in the first
    place, which is what keeps "was accepted" and "is still valid" from
    drifting apart.
    """
    remembered = remembered_game()
    if remembered is not None and gamefiles.looks_like_the_game(remembered):
        return remembered
    return gamefiles.find_game_dir()
