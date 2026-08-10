"""Check the environment is complete, and offer to fix what is missing.

Runs on a bare Python with nothing installed, so it uses only the standard
library until it has confirmed the dependencies are present.

    py -3.12 scripts\\setup_check.py          check only
    py -3.12 scripts\\setup_check.py --fix    create the venv and install
"""

from __future__ import annotations

import importlib.util
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
VENV = ROOT / ".venv"
VENV_PY = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")

# import name -> pip requirement
PACKAGES = {
    "Crypto": "pycryptodome",
    "zstandard": "zstandard",
    "PySide6": "PySide6",
    "PIL": "pillow",
    "PyInstaller": "pyinstaller",
    # nrdata/dds.py imports this unconditionally, so the icon pack cannot be
    # rebuilt without it. It was missing from both this list and
    # requirements.txt, which let this script report an environment as
    # complete on which build_icons.py could not run.
    "texture2ddecoder": "texture2ddecoder",
}

# Generated from the player's own installation, so a fresh clone has neither.
# That is the expected state, not a fault -- see BUILT_FILES handling below.
BUILT_FILES = [
    ("nrplanner/data/nightreign_data.json", "game data snapshot"),
    ("nrplanner/data/icons/manifest.json", "icon pack index"),
]

# Shipped with the source. Absent means a broken checkout.
REQUIRED_FILES = [
    ("vendor/Paramdex/NR/Defs", "paramdefs (required to read the game)"),
]

OK, WARN, BAD = "  ok  ", " warn ", " MISSING "


def line(status: str, label: str, detail: str = "") -> None:
    print(f"[{status:^7}] {label:<38}{detail}")


def check_python() -> bool:
    version = sys.version_info
    good = version >= (3, 10)
    line(OK if good else BAD, "Python interpreter",
         f"{version.major}.{version.minor}.{version.micro}")
    if not good:
        print("           Python 3.10+ is required; 3.12 is what this was built on.")
    return good


def check_venv() -> bool:
    if VENV_PY.exists():
        line(OK, "virtual environment", str(VENV))
        return True
    line(WARN, "virtual environment", "not created yet")
    return False


PROBE = """
import importlib.util, sys
for name, pip in %r:
    if importlib.util.find_spec(name) is None:
        print(pip)
"""


def missing_packages(python: pathlib.Path | None) -> list[str]:
    """Which requirements are absent, checked inside the target interpreter."""
    if python is None or str(python) == sys.executable:
        return [pip for name, pip in PACKAGES.items()
                if importlib.util.find_spec(name) is None]
    try:
        out = subprocess.run(
            [str(python), "-c", PROBE % list(PACKAGES.items())],
            capture_output=True, text=True, timeout=180,
        )
        return [l.strip() for l in out.stdout.splitlines() if l.strip()]
    except Exception:  # noqa: BLE001
        return list(PACKAGES.values())


def _describe(path: pathlib.Path) -> str:
    if path.is_dir():
        return f"{sum(1 for _ in path.iterdir())} files"
    return f"{path.stat().st_size / 1024 / 1024:.1f} MB"


def check_required() -> bool:
    every = True
    for rel, label in REQUIRED_FILES:
        path = ROOT / rel
        if path.exists():
            line(OK, label, _describe(path))
        else:
            line(BAD, label, rel)
            every = False
    return every


def check_built() -> bool:
    """Is the extracted data present?

    A fresh clone has none of it, by design -- this project ships no game
    content. So absence is reported as "not built yet" rather than as a
    fault, and it is only fatal when there is no installation to build it
    from either.
    """
    every = True
    for rel, label in BUILT_FILES:
        path = ROOT / rel
        if path.exists():
            line(OK, label, _describe(path))
        else:
            line(WARN, label, "not built yet")
            every = False
    return every


def check_game() -> bool:
    """Required: the app has no data of its own to fall back on."""
    sys.path.insert(0, str(ROOT))
    try:
        from nrdata import gamefiles

        game = gamefiles.find_game_dir()
    except Exception as exc:  # noqa: BLE001
        line(WARN, "Nightreign installation", f"could not check ({exc})")
        return False
    if game:
        line(OK, "Nightreign installation", str(game))
        return True
    line(BAD, "Nightreign installation", "not found")
    return False


def check_save() -> None:
    sys.path.insert(0, str(ROOT))
    try:
        from nrdata import savefile

        saves = savefile.find_saves()
    except Exception as exc:  # noqa: BLE001
        line(WARN, "save file", f"could not check ({exc})")
        return
    if saves:
        line(OK, "save file", f"{len(saves)} profile(s): "
                              f"{', '.join(p.parent.name for p in saves)}")
    else:
        line(WARN, "save file",
             "none found - relic slots will be empty")


def install(missing: list[str]) -> bool:
    if not VENV_PY.exists():
        print(f"\ncreating virtual environment in {VENV} ...")
        subprocess.run([sys.executable, "-m", "venv", str(VENV)], check=True)

    print(f"installing: {', '.join(missing)}")
    result = subprocess.run(
        [str(VENV_PY), "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")]
    )
    return result.returncode == 0


def main() -> int:
    fix = "--fix" in sys.argv
    try:
        sys.path.insert(0, str(ROOT))
        from nrplanner import __version__ as version
    except Exception:  # noqa: BLE001 - this has to run on a bare tree too
        version = "unknown"
    print(f"Nightreign Helper {version} - environment check\n{ROOT}\n")

    python_ok = check_python()
    have_venv = check_venv()
    target = VENV_PY if have_venv else None

    missing = missing_packages(target)
    if missing:
        line(BAD if have_venv else WARN, "python packages",
             f"missing: {', '.join(missing)}")
    else:
        line(OK, "python packages", ", ".join(PACKAGES.values()))

    required_ok = check_required()
    built_ok = check_built()
    game_ok = check_game()
    check_save()

    needs_work = bool(missing) or not have_venv
    if needs_work and fix and python_ok:
        print()
        if install(missing):
            print("\nre-checking ...\n")
            still = missing_packages(VENV_PY)
            if still:
                line(BAD, "python packages", f"still missing: {still}")
                return 1
            line(OK, "python packages", "all installed")
            needs_work = False
        else:
            print("\ninstall failed; see the pip output above")
            return 1

    print()
    if not required_ok:
        print("Part of the source is missing. Re-clone the repository.")
        return 1
    if not game_ok:
        print("No ELDEN RING NIGHTREIGN installation was found.")
        print()
        print("This project ships no game data -- every value it shows is read")
        print("from your own copy of the game, so the game must be installed.")
        print("Steam's library list and the drives C to H were checked.")
        return 1
    if not built_ok:
        print("The game data has not been built yet. Build it with:")
        print("   .venv\\Scripts\\python.exe scripts\\build_snapshot.py")
        print("   .venv\\Scripts\\python.exe scripts\\build_icons.py")
        print("That takes about a minute, and is only needed once per patch.")
        return 1
    if needs_work:
        print("Environment incomplete. Re-run with --fix to install:")
        print("   py -3.12 scripts\\setup_check.py --fix")
        return 1

    print("Everything is in place. Start the app with:")
    print("   .venv\\Scripts\\python.exe run.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
