# -*- mode: python ; coding: utf-8 -*-
#
# Note what is NOT bundled: nightreign_data.json and the icon pack. Those are
# extracted from the user's own installation at runtime, so the shipped EXE
# carries no game content. Only the paramdefs -- the field schemas needed to
# read the game at all -- and our own icon travel with it.

import pathlib
import re

from PyInstaller.utils.win32.versioninfo import (
    FixedFileInfo,
    StringFileInfo,
    StringStruct,
    StringTable,
    VarFileInfo,
    VarStruct,
    VSVersionInfo,
)

# ---- The version, taken from the source rather than repeated here ----------
#
# nrplanner/__init__.py is the one place the version is written down, and the
# release workflow already fails a tag that disagrees with it. Until now that
# guarantee stopped at the window title: the EXE's own file properties carried
# no version at all, so a built executable could not be identified from Windows
# without running it and reading the title bar. Right-click -> Properties ->
# Details now answers it too, and cannot drift, because it is read from that
# same line at build time.
#
# Read with a regex rather than imported: importing the package here would pull
# PySide6 into the build process for the sake of one string.
_SOURCE = pathlib.Path("nrplanner/__init__.py").read_text(encoding="utf-8")
_MATCH = re.search(r'^__version__\s*=\s*"([^"]+)"', _SOURCE, re.MULTILINE)
if _MATCH is None:
    raise SystemExit("could not find __version__ in nrplanner/__init__.py")
VERSION = _MATCH.group(1)

# Windows wants exactly four integers, so "1.1.1" becomes (1, 1, 1, 0).
_QUAD = tuple(([int(part) for part in VERSION.split(".")] + [0, 0, 0, 0])[:4])

version_info = VSVersionInfo(
    ffi=FixedFileInfo(filevers=_QUAD, prodvers=_QUAD),
    kids=[
        StringFileInfo([
            StringTable("040904B0", [
                StringStruct("CompanyName", "DankYeeter"),
                StringStruct("FileDescription",
                             "Nightreign Helper - build planner and reference "
                             "for ELDEN RING NIGHTREIGN"),
                StringStruct("FileVersion", VERSION),
                StringStruct("InternalName", "NightreignHelper"),
                StringStruct("LegalCopyright",
                             "MIT licensed. Unofficial fan project, not "
                             "affiliated with FromSoftware or Bandai Namco."),
                StringStruct("OriginalFilename", "NightreignHelper.exe"),
                StringStruct("ProductName", "Nightreign Helper"),
                StringStruct("ProductVersion", VERSION),
            ]),
        ]),
        # US English, Unicode. Must agree with the 040904B0 table above.
        VarFileInfo([VarStruct("Translation", [0x0409, 1200])]),
    ],
)

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('nrplanner/data/icon.ico', 'data'),
        ('vendor/Paramdex/NR/Defs', 'paramdefs'),
    ],
    hiddenimports=['nrdata.extract', 'nrdata.gamefiles', 'nrdata.savefile',
                   'nrdata.iconbuild'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='NightreignHelper',
    icon='nrplanner/data/icon.ico',
    version=version_info,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
