<div align="center">

<img src="nrplanner/data/icon.png" width="128" alt="Nightreign Helper">

# Nightreign Helper

**A build planner for ELDEN RING NIGHTREIGN that reads your own game install.**

Every number in this tool is read out of the game's own files on your machine.
Nothing is copied from a wiki, and nothing is typed in by hand.

</div>

---

## What it does

| Tab | What you get |
|---|---|
| **Planner** | Pick a Nightfarer and a chalice, fill the relic slots, watch the stat sheet. Every figure is clickable for a per-buff breakdown. |
| **Weapons** | Armaments, sorceries and incantations with attack rating. |
| **Effects** | All 616 relic effects, what each one actually does, and which ones refuse to stack — read from the game's own exclusivity keys, not guessed. |
| **Nightlords** | The eight bosses and the Everdark Sovereigns: expedition, artwork, and damage/status charts where the game files resolve them. |
| **Deep of Night** | Enemy scaling and rewards across the five depths. |
| **Depth weighting** | Which mutations can appear at which depth. |
| **World events** | The Limveld events and how each one can end. |

It reads your save file too, so your actual owned relics fill the picker, and
**Load equipped** pulls a Nightfarer's current loadout straight out of the save.

Your save is opened **read-only**. This tool never writes to it, and it is not
a mod, a trainer or a save editor.

## Requirements

- **Windows**
- **ELDEN RING NIGHTREIGN installed.** This is not optional — the tool has no
  bundled copy of the game's data and cannot start without the game to read.
  See *Why there is no bundled data* below.

## Install

Grab the latest `NightreignHelper.exe` from the
[Releases](../../releases) page and run it. No Python, no installer, no admin
rights.

**First launch takes about half a minute** while it reads your installation and
builds a local copy of the data. Every launch after that is instant, until the
game patches — then it re-reads itself automatically.

## Running from source

Install Python 3.12 from [python.org](https://www.python.org/downloads/), then:

```bat
py -3.12 scripts\setup_check.py --fix
```

That one command creates the virtual environment, installs every dependency,
and verifies the result. It reports on each piece:

```
[  ok   ] Python interpreter                    3.12.10
[  ok   ] virtual environment                   ...\.venv
[  ok   ] python packages                       pycryptodome, zstandard, PySide6, ...
[  ok   ] paramdefs (required to read the game) 226 files
[  ok   ] Nightreign installation               D:\SteamLibrary\...\Game
[  ok   ] save file                             2 profile(s)
```

Then build the data from your install and start it:

```bat
.venv\Scripts\python.exe scripts\build_snapshot.py
.venv\Scripts\python.exe scripts\build_icons.py
.venv\Scripts\python.exe run.py
```

To package your own EXE:

```bat
.venv\Scripts\pyinstaller.exe NightreignHelper.spec --noconfirm
```

Close any running copy first, or Windows' file lock makes PyInstaller fail with
`PermissionError`.

## Why there is no bundled data

Shipping a prebuilt snapshot would mean redistributing FromSoftware's data, and
that is not mine to redistribute. So the repository and the released EXE contain
none of it. Instead the tool reads the installation you already own and builds
its data locally, on your machine, for your use.

The practical consequence is the one stated above: **the game must be
installed.** If it is not found, the tool says so plainly rather than falling
back to numbers from somewhere else.

## Layout

| Path | Purpose |
|---|---|
| `nrdata/` | Reading the game's own formats — archives, params, textures, saves. No GUI code. |
| `nrplanner/` | The GUI, the build maths, and save inventory. |
| `scripts/` | Environment check, data builders, icon generator. |
| `vendor/Paramdex/NR/Defs` | Field schemas for the params. Required to read anything. |

## Disclaimer

Nightreign Helper is an unofficial fan project. It is **not affiliated with,
endorsed by, sponsored by, or approved by** FromSoftware, Inc. or Bandai Namco
Entertainment Inc.

ELDEN RING NIGHTREIGN, its data, artwork, text and trademarks are the property
of their respective owners. This project distributes none of that content. All
game values and images the tool displays are read at runtime from the copy of
the game on the user's own machine, and are generated into that machine's local
storage only.

The application icon is original artwork and contains no game assets. It is set
in [Cinzel](https://github.com/NDISCOVER/Cinzel), licensed under the SIL Open
Font License.

Param field definitions in `vendor/Paramdex` come from the community
[Paramdex](https://github.com/soulsmods/Paramdex) project and remain under
their own terms.

## Licence

[MIT](LICENSE) © DankYeeter — source code only. See the disclaimer above for
game content.
