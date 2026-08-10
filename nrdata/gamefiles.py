"""Locating a Nightreign installation."""

from __future__ import annotations

import pathlib

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
    """Return the folder containing regulation.bin, or None."""
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
        if (path / "regulation.bin").exists():
            return path
    return None
