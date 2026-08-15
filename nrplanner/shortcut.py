"""A Start Menu entry, so the tool can be launched by name.

The program ships as a single executable that the player puts wherever they
like -- Downloads, the Desktop, a folder of game tools. That is deliberate:
no installer, no admin rights, delete the file to uninstall. The cost is that
something used often has to be found again every time.

This closes that without giving any of it up. A shortcut in the *user's* own
Start Menu needs no elevation, no installer and no registry beyond what
Windows does itself, and removing it is deleting one file. Nothing outside the
user's profile is touched.

Deliberately not done here: pinning to the taskbar (Windows offers no
supported way to do it programmatically and every method that works is an
exploit of an undocumented interface), a machine-wide entry under
ProgramData (needs admin, and this is a single-user tool), and any kind of
auto-start.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys

SHORTCUT_NAME = "Nightreign Helper.lnk"

# Only the packaged executable is worth a Start Menu entry. From a source
# checkout the target would be a .py needing the right interpreter and working
# directory, which is a shortcut that breaks the moment the venv moves.
FROZEN = bool(getattr(sys, "frozen", False))


def start_menu_dir() -> pathlib.Path | None:
    """The user's own Start Menu programs folder."""
    appdata = os.environ.get("APPDATA")
    if not appdata:
        return None
    return (pathlib.Path(appdata) / "Microsoft" / "Windows" / "Start Menu"
            / "Programs")


def shortcut_path() -> pathlib.Path | None:
    folder = start_menu_dir()
    return folder / SHORTCUT_NAME if folder else None


def target() -> pathlib.Path:
    """What the shortcut should point at."""
    return pathlib.Path(sys.executable).resolve()


def available() -> bool:
    """Can a Start Menu entry be offered at all?"""
    return (sys.platform == "win32" and FROZEN
            and start_menu_dir() is not None)


def exists() -> bool:
    path = shortcut_path()
    return bool(path and path.exists())


def create() -> str:
    """Make the shortcut. Returns an error message, or "" on success.

    Written through WScript.Shell rather than by adding a COM wrapper to the
    dependencies. A .lnk is an undocumented binary format that must not be
    written by hand, and the one interface for it that is guaranteed present
    on every Windows install is this one -- which costs a subprocess at the
    moment the user asks for it, and no new library in the 60 MB executable.
    """
    if not available():
        return "A Start Menu entry can only be created from the packaged .exe."

    path = shortcut_path()
    exe = target()
    if path is None:
        return "Windows did not report a Start Menu folder for this account."

    script = (
        "$ErrorActionPreference='Stop';"
        "$s=(New-Object -ComObject WScript.Shell).CreateShortcut($env:NRH_LNK);"
        "$s.TargetPath=$env:NRH_EXE;"
        "$s.WorkingDirectory=Split-Path $env:NRH_EXE;"
        "$s.IconLocation=$env:NRH_EXE;"
        "$s.Description='Build planner and reference for ELDEN RING NIGHTREIGN';"
        "$s.Save()"
    )
    # The paths go through the environment rather than into the script text, so
    # a folder name containing a quote or a $ cannot end up being executed.
    env = {**os.environ, "NRH_LNK": str(path), "NRH_EXE": str(exe)}

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive",
             "-ExecutionPolicy", "Bypass", "-Command", script],
            env=env, capture_output=True, text=True, timeout=30,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except Exception as exc:  # noqa: BLE001 - reported to the user as text
        return str(exc) or exc.__class__.__name__

    if result.returncode != 0 or not path.exists():
        detail = (result.stderr or result.stdout or "").strip().splitlines()
        return detail[0] if detail else "the shortcut could not be written"
    return ""


def remove() -> str:
    """Delete the shortcut. Returns an error message, or "" on success."""
    path = shortcut_path()
    if path is None:
        return "Windows did not report a Start Menu folder for this account."
    try:
        path.unlink(missing_ok=True)
    except OSError as exc:
        return str(exc)
    return ""
