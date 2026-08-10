# -*- mode: python ; coding: utf-8 -*-
#
# Note what is NOT bundled: nightreign_data.json and the icon pack. Those are
# extracted from the user's own installation at runtime, so the shipped EXE
# carries no game content. Only the paramdefs -- the field schemas needed to
# read the game at all -- and our own icon travel with it.

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('nrplanner/data/icon.ico', 'data'),
        ('vendor/Paramdex/NR/Defs', 'paramdefs'),
    ],
    hiddenimports=['nrdata.extract', 'nrdata.gamefiles', 'nrdata.savefile'],
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
