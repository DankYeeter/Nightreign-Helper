"""Locating a Nightreign installation."""

from __future__ import annotations

import os
import pathlib
import stat
import time

STEAM_APP_ID = "2622380"
INSTALL_DIR = "ELDEN RING NIGHTREIGN"


def _steam_roots() -> list[pathlib.Path]:
    roots: list[pathlib.Path] = []
    try:
        import winreg

        for hive, sub in (
            (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"),
        ):
            try:
                with winreg.OpenKey(hive, sub) as key:
                    value = winreg.QueryValueEx(key, "SteamPath")[0]
                    roots.append(pathlib.Path(value))
            except OSError:
                continue
    except ImportError:
        pass

    roots += [
        pathlib.Path(r"C:\Program Files (x86)\Steam"),
        pathlib.Path(r"C:\Steam"),
    ]
    return roots


def _library_paths(steam_root: pathlib.Path) -> list[pathlib.Path]:
    """Read libraryfolders.vdf to find libraries on other drives."""
    out = [steam_root / "steamapps"]
    vdf = steam_root / "steamapps" / "libraryfolders.vdf"
    if vdf.exists():
        for line in vdf.read_text(encoding="utf-8", errors="replace").splitlines():
            parts = line.split('"')
            if len(parts) >= 4 and parts[1] == "path":
                out.append(pathlib.Path(parts[3].replace("\\\\", "\\")) / "steamapps")
    return out


def find_game_dir() -> pathlib.Path | None:
    """Return the folder the installed game sits in, or None.

    Asks `looks_like_the_game` (SEC-031) rather than the presence of
    `regulation.bin` alone: a folder that fails the ceiling or lacks a
    `.bhd` or the DLL is one nothing could be extracted from anyway, so
    checking it here costs nothing real. It closes the gap between what
    this route used to accept and what the same predicate, asked again
    the moment a remembered folder is re-checked, would have accepted.
    """
    candidates: list[pathlib.Path] = []
    for root in _steam_roots():
        if not root.exists():
            continue
        for lib in _library_paths(root):
            candidates.append(lib / "common" / INSTALL_DIR / "Game")

    # Bare-drive fallback for non-default library layouts.
    for drive in "CDEFGH":
        candidates.append(
            pathlib.Path(f"{drive}:/SteamLibrary/steamapps/common/{INSTALL_DIR}/Game")
        )

    for path in candidates:
        if looks_like_the_game(path):
            return path
    return None


def steam_common_folders() -> list[pathlib.Path]:
    """Every Steam library's ``common`` folder, nearest root first.

    Public so a folder-choosing dialog can wake up in the player's own
    library rather than only the default one (`UI_SPEC` 4.1, AK-110): a
    library on another drive is nearer to the game than
    `C:\\Program Files (x86)\\Steam\\steamapps\\common`, the hard-coded
    fallback that stands in for it when Steam cannot be found at all.

    Existence is for the caller to check, exactly as `find_game_dir` checks
    it against the same two private helpers above -- a library the vdf
    names but that is not there (an unplugged drive, a stale entry) is a
    candidate and not a folder.
    """
    folders: list[pathlib.Path] = []
    for root in _steam_roots():
        if not root.exists():
            continue
        for lib in _library_paths(root):
            folders.append(lib / "common")
    return folders


# --- Recognising a folder the user picked (UI_SPEC 4.2/4.3, AK-111 to AK-113)


# The word out of INSTALL_DIR that tells the two FromSoftware games apart.
# ELDEN RING carries a regulation.bin, data*.bhd archives and an Oodle DLL as
# well, so the structure alone cannot say which game a folder holds; the name
# is the only cheap evidence there is. Derived from the constant rather than
# written out again, so a rename of the install directory moves both.
IDENTITY_WORD = INSTALL_DIR.rsplit(" ", 1)[-1]

# The found folder and its three parent levels carry the name (UI_SPEC 4.3):
# a Steam install is ...\common\ELDEN RING NIGHTREIGN\Game, so the name sits
# one level up from the folder that is returned.
NAMED_LEVELS = 3

# regulation.bin is read whole and hashed on every start (datasource,
# firstrun, regulation), and the folder it comes from is one the user picked,
# so its size is an input like any other. Measured on this installation
# 1 974 720 bytes (08.09.2026, stat().st_size, sample of one, SEC-028); the
# ceiling leaves that a factor of 34, more room than the accepted
# MAX_UNCOMPRESSED_SIZE leaves its own measurement. A file above it is not a
# regulation.bin, so the folder is rejected out loud (text E1) rather than
# read.
MAX_REGULATION_BYTES = 64 * 1024 * 1024

# The search from a picked folder (UI_SPEC 4.2). Three levels down carries
# ...\ELDEN RING NIGHTREIGN (1), common (2) and steamapps (3); two levels up
# carries somebody who landed in a subfolder of the game. The two budgets are
# what keeps a drive root from turning into a search of the whole disk: the
# user waits at most this long for a no.
SEARCH_DEPTH = 3
SEARCH_PARENTS = 2
MAX_DIRECTORIES = 400
SEARCH_SECONDS = 2.0

# The clock the budget is read from, as a module attribute so a test can hand
# the search a clock of its own. A test that waited for real seconds would be
# measuring this machine, and a wall-clock bound has no place in the suite.
_monotonic = time.monotonic


def looks_like_the_game(path) -> bool:
    """Stage 1: does this folder hold an installed FromSoftware game?

    The hard condition, and the only one there is: what this says yes to is
    accepted (AK-112), and what it said yes to yesterday is what is still
    valid at the next start (AK-107). One predicate for both questions on
    purpose -- two of them drift apart, and the drift shows as a folder that
    was accepted once and is rejected afterwards for no reason the user can
    see.

    Says nothing about *which* game this is; ELDEN RING passes it too. That
    is the question is_named_nightreign answers.

    Any OSError -- an unplugged drive, a dead network path, a folder that
    cannot be read -- means "not valid", never an error thrown at the caller.
    """
    from . import bhd5, oodle  # heavy imports; a path check must stay cheap

    try:
        folder = pathlib.Path(path)
        regulation = folder / "regulation.bin"
        size = regulation.stat().st_size
        if not 0 < size <= MAX_REGULATION_BYTES:
            return False
        with regulation.open("rb") as handle:
            if not handle.read(1):
                return False
        if not any((folder / f"{name}.bhd").exists()
                   for name in bhd5.ARCHIVE_KEYS):
            return False
        return any((folder / name).exists() for name in oodle._DLL_NAMES)
    except (OSError, ValueError):
        return False


def is_named_nightreign(path) -> bool:
    """Stage 2: does the folder or one of its parents name this game?

    Soft on purpose (UI_SPEC 4.3): renaming an install folder is allowed and
    happens, so a no is a question to the user (text W1), not a rejection.
    """
    folder = pathlib.Path(path)
    levels = [folder, *list(folder.parents)[:NAMED_LEVELS]]
    return any(IDENTITY_WORD in level.name.upper() for level in levels)


def _is_a_door_out_of_the_tree(entry: os.DirEntry) -> bool:
    """Is this directory entry a junction or a symbolic link?

    The budgets below limit how long the search runs and how far it goes, but
    not *where* it ends up: a junction inside the picked folder leads out of
    the tree the user saw, and can lead back into it as a loop (SEC-030). The
    search therefore does not step through one. A link the user picked
    himself is another matter -- that folder is what he chose.
    """
    if entry.is_symlink():
        return True
    try:
        attributes = entry.stat(follow_symlinks=False).st_file_attributes
    except (AttributeError, OSError):
        return False  # not Windows, or gone between listing and asking
    return bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def _subfolders(folder: pathlib.Path) -> list[pathlib.Path]:
    """The folders directly inside this one, junctions left alone."""
    found: list[pathlib.Path] = []
    try:
        with os.scandir(folder) as entries:
            for entry in entries:
                try:
                    if not entry.is_dir(follow_symlinks=False):
                        continue
                    if _is_a_door_out_of_the_tree(entry):
                        continue
                except OSError:
                    continue
                found.append(pathlib.Path(entry.path))
    except OSError:
        return []
    return sorted(found)


def _changed_at(folder: pathlib.Path) -> float:
    try:
        return folder.stat().st_mtime
    except OSError:
        return 0.0


def _the_best_of(matches) -> pathlib.Path | None:
    """The closest match to the picked folder, newest first on a tie."""
    if not matches:
        return None
    _distance, _changed, folder = min(matches, key=lambda m: (m[0], -m[1]))
    return folder.resolve()


def _search_within_budget(start) -> tuple[pathlib.Path | None, int]:
    """search_from, plus how many directories it looked at.

    The count is what the budget is spent on, and a test holds it against the
    literal 400 -- which is the whole reason it leaves this function.
    """
    started_at = _monotonic()
    chosen = pathlib.Path(start)
    matches: list[tuple[int, float, pathlib.Path]] = []
    visited = 0

    # Down first, level by level, so the shallowest hit is found first; then
    # up, nearest parent first. Both directions carry their distance from the
    # picked folder, and the smallest distance wins.
    level = [chosen]
    for distance in range(SEARCH_DEPTH + 1):
        below: list[pathlib.Path] = []
        for folder in level:
            if (visited >= MAX_DIRECTORIES
                    or _monotonic() - started_at >= SEARCH_SECONDS):
                return _the_best_of(matches), visited
            visited += 1
            if looks_like_the_game(folder):
                matches.append((distance, _changed_at(folder), folder))
            if distance < SEARCH_DEPTH:
                below += _subfolders(folder)
        if matches:
            return _the_best_of(matches), visited
        level = below
        if not level:
            break

    for distance, parent in enumerate(list(chosen.parents)[:SEARCH_PARENTS],
                                      start=1):
        if (visited >= MAX_DIRECTORIES
                or _monotonic() - started_at >= SEARCH_SECONDS):
            break
        visited += 1
        if looks_like_the_game(parent):
            matches.append((distance, _changed_at(parent), parent))
            break
    return _the_best_of(matches), visited


def search_from(start) -> pathlib.Path | None:
    """The game folder at or around the one the user picked, or None.

    A player picks the folder Steam shows him, which is one above the one
    that holds regulation.bin; someone who was already browsing his install
    picks one below it. Both are a step from the answer, so both directions
    are searched: three levels down, two levels up, within 400 directories
    and two seconds (UI_SPEC 4.2). Reaching a budget without a hit means "not
    recognised" -- a drive root must not turn into a search of the disk.

    The result is always the folder that holds regulation.bin itself, in the
    form find_game_dir() returns, resolved (SEC-030).
    """
    found, _visited = _search_within_budget(start)
    return found
