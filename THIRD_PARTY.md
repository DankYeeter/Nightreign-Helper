# Third-party components and notices

This file is the notice package for the released executable. It is meant to be
readable on its own — it also ships as a release asset next to the EXE, not
only inside this repository, so that the licence terms below travel with every
copy. The full notice package is this file plus
[`LICENSE`](LICENSE) (this project's own MIT text),
[`licenses/`](licenses/) (the full licence text of every bundled component),
and [`vendor/Paramdex/NOTICE`](vendor/Paramdex/NOTICE) (the one vendored,
unlicensed third-party data file, kept separate because it is not a licence
grant — see "Param definitions" below). How these files travel with a
release build is not this file's concern.

## Not affiliated

Nightreign Helper is an unofficial fan project. It is not affiliated with,
endorsed by, sponsored by, or approved by FromSoftware, Inc. or Bandai Namco
Entertainment Inc. ELDEN RING NIGHTREIGN, its data, artwork, text and
trademarks are the property of their respective owners. The released
executable contains no game data; it reads your own installation. See
[README.md](README.md).

## What the program does, technically

It reads and decrypts, locally, the game files and the save data of an
installed copy of ELDEN RING NIGHTREIGN, using decryption keys that have been
publicly known in the modding community for years. It never writes to the
game or to the save file. It makes no network connection. Back up your save
before running any third-party tool against it, this one included.

## Licence of this project

Nightreign Helper's own source code is MIT (see [LICENSE](LICENSE)). The
released executable is a single file that also bundles the Python runtime and
the libraries below, so their terms travel with it. Every copyright notice
and licence name in the table was read from the package's own metadata or its
shipped licence file, not from memory — see the "Copyright notice (verbatim)"
column for where each one came from. Full licence texts are in
[`licenses/`](licenses/); the table links to the exact file.

`scripts/check_licences.py` fails if a dependency in `requirements.txt` is
missing from this table, so adding a library without recording its licence
breaks the build rather than shipping quietly.

## Bundled into the executable

| Component | Version | Licence | Copyright notice (verbatim) | Full text |
|---|---|---|---|---|
| PySide6 | 6.11.1 | **LGPL-3.0-only** OR GPL-2.0-only OR GPL-3.0-only | `Copyright (C) 2022 The Qt Company Ltd.` — from the header of the `.pyi` stub files shipped in the wheel (e.g. `PySide6/QtCore.pyi`); the compiled `Qt6Core.dll` inside the same wheel carries the equivalent runtime string `Copyright (C) The Qt Company Ltd. and other contributors.` | [`licenses/LGPL-3.0.txt`](licenses/LGPL-3.0.txt) (licence elected for this project, see below) and [`licenses/GPL-3.0.txt`](licenses/GPL-3.0.txt) (required alongside it, see below) |
| shiboken6 | 6.11.1 | **LGPL-3.0-only** OR GPL-2.0-only OR GPL-3.0-only | `Copyright (C) 2022 The Qt Company Ltd.` — from `shiboken6/Shiboken.pyi` in the wheel | same two files as PySide6 |
| pycryptodome | 3.23.0 | Public Domain (code inherited from PyCrypto) and BSD-2-Clause (direct contributions) | The package's own `LICENSE.rst` names no single copyright holder or year — it states the PyCrypto-derived code is dedicated to the public domain by its authors, and that "the copyright of each piece \[of the BSD-licensed contributions\] belongs to the respective author". The contributor list is in the wheel's `AUTHORS.rst`. | [`licenses/pycryptodome-LICENSE.rst`](licenses/pycryptodome-LICENSE.rst) |
| zstandard | 0.25.0 | BSD-3-Clause | `Copyright (c) 2016, Gregory Szorc` — from the wheel's `licenses/LICENSE` | [`licenses/zstandard-LICENSE.txt`](licenses/zstandard-LICENSE.txt) |
| Pillow | 12.3.0 | MIT-CMU (HPND), plus the licences of the C libraries statically linked into its binary wheel | `Copyright © 1997-2011 by Secret Labs AB`, `Copyright © 1995-2011 by Fredrik Lundh and contributors`, `Copyright © 2010 by Jeffrey 'Alex' Clark and contributors` — from the wheel's `licenses/LICENSE`. That same file also carries the separate copyright and licence text of every C library Pillow's wheel links in (libjpeg-turbo, FreeType, HarfBuzz, brotli, lcms2, libavif, libyuv and others); none of those texts are repeated here — the linked file carries all of them verbatim. | [`licenses/Pillow-LICENSE.txt`](licenses/Pillow-LICENSE.txt) |
| texture2ddecoder | 1.0.6 | MIT | `Copyright (c) 2020 K0lb3` — from the wheel's `LICENSE` | [`licenses/texture2ddecoder-LICENSE.txt`](licenses/texture2ddecoder-LICENSE.txt) |

**Provenance of the LGPL-3.0 and GPL-3.0 full texts.** Neither PySide6 nor
shiboken6 ships the licence text it names — the wheels only carry a
`LicenseRef-Qt-Commercial.txt` pointer file, because Qt for Python is
dual/triple-licensed and the wheel does not pick a licence for you, the
distributor does. `licenses/LGPL-3.0.txt` and `licenses/GPL-3.0.txt` are
therefore unmodified copies of the canonical Free Software Foundation text —
verified byte-identical to a copy found elsewhere on the machine this table
was written on (an OpenOffice extension bundle for LGPL-3.0, `gcc-libs` inside
a Git for Windows install for GPL-3.0), not retyped from memory. The text of
both licences is standardised and identical wherever it comes from; what
varies is the copyright notice above, which is not.

## Build-time only, not shipped

| Component | Version | Licence |
|---|---|---|
| PyInstaller | 6.21.0 | GPL-2.0-or-later **with the bootloader exception**, which permits shipping an application under any licence |

## Qt / PySide6 — what LGPL requires here

The executable contains Qt through PySide6, used under the **LGPL-3.0**. That
carries obligations, and they are met as follows:

- **The licence is named and available.** Qt's LGPLv3 text is bundled with
  this notice package at [`licenses/LGPL-3.0.txt`](licenses/LGPL-3.0.txt),
  and GPL-3.0 alongside it at
  [`licenses/GPL-3.0.txt`](licenses/GPL-3.0.txt), as LGPL-3.0 §4(b) requires.
  Also see <https://www.qt.io/licensing>. (Checked for this release: the
  PySide6 and shiboken6 wheels themselves do **not** carry either licence
  text — only a `LicenseRef-Qt-Commercial.txt` pointer file — so the texts
  here were sourced elsewhere on the build machine; see "Provenance" above.
  A prior version of this file claimed the wheel carries the text; it does
  not, and that line has been corrected.)
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
