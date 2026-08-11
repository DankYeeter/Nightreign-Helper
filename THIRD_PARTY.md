# Third-party components

Nightreign Helper is MIT (see [LICENSE](LICENSE)). The released executable is a
single file that bundles the Python runtime and the libraries below, so their
terms travel with it. Every entry here was read from the package's own metadata
or its shipped licence file, not from memory.

`scripts/check_licences.py` fails if a dependency in `requirements.txt` is
missing from this table, so adding a library without recording its licence
breaks the build rather than shipping quietly.

## Bundled into the executable

| Component | Version | Licence |
|---|---|---|
| PySide6 | 6.11.1 | **LGPL-3.0-only** OR GPL-2.0-only OR GPL-3.0-only |
| shiboken6 | 6.11.1 | **LGPL-3.0-only** OR GPL-2.0-only OR GPL-3.0-only |
| pycryptodome | 3.23.0 | BSD-2-Clause and Public Domain |
| zstandard | 0.25.0 | BSD-3-Clause — © 2016 Gregory Szorc |
| Pillow | 12.3.0 | MIT-CMU (HPND) |
| texture2ddecoder | 1.0.6 | MIT — © 2020 K0lb3 |

## Build-time only, not shipped

| Component | Version | Licence |
|---|---|---|
| PyInstaller | 6.21.0 | GPL-2.0-or-later **with the bootloader exception**, which permits shipping an application under any licence |

## Qt / PySide6 — what LGPL requires here

The executable contains Qt through PySide6, used under the **LGPL-3.0**. That
carries obligations, and they are met as follows:

- **The licence is named and available.** Qt's LGPLv3 text is at
  <https://www.qt.io/licensing> and in each PySide6 wheel.
- **Qt is not modified.** Stock PySide6 wheels from PyPI are installed, pinned
  by version in `requirements.txt`.
- **The user can relink against their own Qt.** The complete source of this
  application is this repository, and `requirements.txt` plus
  `NightreignHelper.spec` reproduce the build exactly. Anyone wanting a
  different Qt can install their own PySide6 and rebuild:

  ```
  pip install -r requirements.txt
  pyinstaller NightreignHelper.spec --noconfirm
  ```

That last point is the one a single-file PyInstaller build can otherwise fail,
and it is only satisfied because the source is public and the build is
reproducible from it. **If this repository is ever made private, the released
binary stops meeting the LGPL, and the release must be withdrawn.**

## Game data — not third party, not distributed at all

The program ships **no game content**. Values are read from the user's own
Nightreign installation at first run and cached locally. The release workflow
builds on a runner with no game installed and fails if extracted data appears
in the tree, so this cannot be violated by accident.

## Param definitions

`vendor/Paramdex` holds 226 XML schema files from
[soulsmods/Paramdex](https://github.com/soulsmods/Paramdex), describing where
fields sit inside the game's param tables. See [vendor/Paramdex/NOTICE](vendor/Paramdex/NOTICE).

**The upstream repository publishes no licence**, and GitHub reports its licence
as none. It is redistributed here because nothing can read the game without it
and the modding community treats it as freely reusable — but that is a norm and
not a grant, and it is the weakest link in this file. Resolving it means asking
upstream to add a licence.
