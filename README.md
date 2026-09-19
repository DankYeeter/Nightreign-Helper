<div align="center">

<img src="nrplanner/data/icon.png" width="128" alt="Nightreign Helper">

# Nightreign Helper

**A build planner and reference for ELDEN RING NIGHTREIGN that reads your own game install.**

</div>

![Build planner](docs/screenshots/build_planner.png)

## What it does

A desktop tool for planning relic builds and for looking up things the game
does not tell you: what an effect actually does, which effects refuse to
stack, how much tougher enemies get at Depth 4, what a world event pays out.

It reads your save file, so the relics it offers are the relics you own, and
it can pull a Nightfarer's current loadout straight out of the game. Builds
are kept per Nightfarer and are still there the next time you open it.

Your save is opened **read-only**. This tool never writes to it, and it is
not a mod, a trainer, or a save editor.

## Install

1. Download `NightreignHelper.exe` from the
   [latest release](../../releases/latest) and run it. No Python, no
   installer, no admin rights.
2. Windows will likely show a SmartScreen warning ("Windows protected your
   PC") because the executable is not code-signed. Click **More info**,
   then **Run anyway** to start it.
3. On first launch the tool looks for your own ELDEN RING NIGHTREIGN
   install; if it cannot find it automatically, a panel asks you to point
   at the folder — only a Steam installation is accepted, and nothing in
   that folder is moved, copied or deleted. Reading it takes about a
   minute the first time; every launch after that is immediate. See
   [Where your data lives](docs/anleitung/guide.md#where-your-data-lives)
   in the guide for what that first read does.

## Requirements

- **Windows**
- **ELDEN RING NIGHTREIGN installed**, through Steam. Not optional — the
  tool ships no game data and reads yours instead.
- A save file is optional. Without one the relic slots stay empty and every
  reference tab still works in full.

## The guide

Everything else — the seven tabs, the window, search syntax, where your
data lives, running from source, how values are derived, and known limits —
is in the **[guide](docs/anleitung/guide.md)**.

## Disclaimer

Nightreign Helper is an unofficial fan project. It is **not affiliated
with, endorsed by, sponsored by, or approved by** FromSoftware, Inc. or
Bandai Namco Entertainment Inc. ELDEN RING NIGHTREIGN, its data, artwork,
text and trademarks are the property of their respective owners. The
released executable contains no game data; it reads your own installation.

It reads and decrypts, locally, the game files and the save data of your
installed copy of ELDEN RING NIGHTREIGN, using decryption keys that have
been publicly known in the modding community for years. To open the game's
own archives it also runs a small decompression program out of that
installation folder — a library that ships with the game itself, not
something this project adds. On first run it asks you to point it at a copy
of the game you trust, which for almost everyone is simply the one they
play. It never writes to the game or to the save file, and it makes no
network connection.

**Back up your save before running any third-party tool against it,** this
one included. This tool is read-only by design and provided "AS IS" under
the MIT licence — see [Licence](#licence) — which is not the same as a
guarantee.

The application icon was generated with Google Gemini and contains no game
assets. The byte layouts of the game's param tables come from the community
[Paramdex](https://github.com/soulsmods/Paramdex) project — the schema
only; everything built on top of it is this project's own. See
[`vendor/Paramdex/NOTICE`](vendor/Paramdex/NOTICE).

## Licence

[MIT](LICENSE) © DankYeeter — source code only. See the disclaimer above
for game content.

The released executable bundles its runtime dependencies, so their terms
travel with it — most notably **Qt, via PySide6, under the LGPL-3.0**. What
is included and how the LGPL obligations are met is set out in
[THIRD_PARTY.md](THIRD_PARTY.md), and `scripts/check_licences.py` fails the
build if a dependency is added without being recorded there.
