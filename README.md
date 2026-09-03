<div align="center">

<img src="nrplanner/data/icon.png" width="128" alt="Nightreign Helper">

# Nightreign Helper

**A build planner and reference for ELDEN RING NIGHTREIGN that reads your own game install.**

Every number here is read out of the game's own files on your machine. Nothing is
copied from a wiki, and nothing is typed in by hand. Where the game files do not
answer a question, the tool says so instead of guessing.

</div>

---

## Contents

- [What it is](#what-it-is)
- [Requirements](#requirements)
- [Install](#install)
- **The guide**
  - [1. Build planner](#1-build-planner)
  - [2. Effects & chances](#2-effects--chances)
  - [3. Weapons & spells](#3-weapons--spells)
  - [4. Nightlords](#4-nightlords)
  - [5. Deep of Night](#5-deep-of-night)
  - [6. Red variants](#6-red-variants)
  - [7. World Events](#7-world-events)
- [The window](#the-window)
- [Searching](#searching)
- [Where your data lives](#where-your-data-lives)
- [Running from source](#running-from-source)
- [How values are derived](#how-values-are-derived)
- [Known limits](#known-limits)
- [Disclaimer](#disclaimer)

---

## What it is

A desktop tool for planning relic builds and for looking up things the game does
not tell you: what an effect actually does, which effects refuse to stack, how
much tougher enemies get at Depth 4, what a world event pays out.

It reads your save file, so the relics it offers are the relics you own, and it
can pull a Nightfarer's current loadout straight out of the game. Builds you put
together are kept per Nightfarer and are still there the next time you open it.

**What it is not.** Your save is opened **read-only**. This tool never writes to
it. It is not a mod, a trainer, a save editor, or anything that touches the game
while it runs.

## Requirements

- **Windows**
- **ELDEN RING NIGHTREIGN installed.** Not optional — the tool ships no game data
  and reads yours instead. See [Where your data lives](#where-your-data-lives).
- A save file is optional. Without one the relic slots stay empty and every
  reference tab still works in full.

## Install

Download `NightreignHelper.exe` from the [Releases](../../releases) page and run
it. No Python, no installer, no admin rights.

**First launch takes about a minute.** It reads your installation and builds a
local copy of the data, and offers to put itself in your Start Menu. Every
launch after that is immediate, until the data needs rereading — when the game
is patched, or when a new version of the tool reads something the old one did
not. It says so and does it once.

---

# The guide

## 1. Build planner

![Build planner](docs/screenshots/build_planner.png)

The main screen. Pick a Nightfarer, pick a vessel, fill the slots, read the
consequences on the right.

**Nightfarer** — the ten portraits at the top left. Some have alternate artwork;
your choice is remembered between sessions.

**Vessel** — split into that Nightfarer's own vessels and the **Shared Grails**,
which any Nightfarer can carry. The vessel decides how many relic slots you get
and what colour each one is.

**Relic slots** — each slot names its colour and how many relics of that colour
are available to it. Open one to choose from a picker that lists only relics
which fit. A relic's three effects appear under it once slotted.

A relic you have put in one slot is not offered in the others: you own one of
it, and it can only be worn once. To plan around a relic you have not found
yet — or a second copy of one you have — use **Custom relic** in the picker,
which is not limited by what your save holds. It is remembered with the build
like any other relic and comes back with the chalice it was built in; a chalice
that gives that slot another colour drops it, because it was built for the
colour it had.

Two copies of the same roll are two relics, and you may wear both: the picker
shows one card per roll, but each slot is given a copy of its own.

A build saved before that rule existed can name the same relic in two slots.
Restoring one sorts it out on screen: the first slot keeps the relic, and the
other says where it went instead of standing empty for no stated reason. The
stored build is left exactly as it was — which slot should keep the relic is
yours to decide, so the note comes back every time you open that chalice until
you decide it.

**Your build stays put.** The vessel, the Deep of Night toggle and every slot
are remembered per Nightfarer and come back the next time you open the tool. A
build is worked out once and then referred to for as long as you own the relics
behind it; rebuilding all six slots on every launch is what stops it being
referred to at all.

What is stored is the relic's **roll** as well as the exact copy, so a build
survives your save being rewritten — melting an unrelated relic renumbers the
copies internally, and the roll is what still identifies the one you meant.

**Reset Chalice**, at the top right of the relic slots, empties every slot and
forgets that chalice's stored build. It is the way back to an empty vessel now
that builds stick, and the build list moves to **Unsaved build** so it is not
left naming something you have just cleared.

**Saved builds** — the row under the vessel strip. Whatever is in the slots is
already remembered per chalice; a *saved* build is a copy of that, put aside
under a name, so several can be compared without building each one again from
six slots.

- **Equipped in game** is always the first entry, and is never stored: it is
  read out of your save each time, so it cannot go stale. It is also what
  repairs a chalice the tool has got wrong — it clears every chalice your save
  says is empty.
- **Unsaved build** means the slots are not one of your saved builds. It is
  where you land after Reset Chalice. Choosing it deliberately changes nothing
  on screen: it is the list saying what you are looking at, not an action.
- **Save** stores the slots as they stand under a name; **Delete** forgets one.
- **Hide** keeps a build out of the list without deleting it — for work you
  have finished with and do not want to lose. **Show hidden**, beside it, lists
  the hidden ones again, and selecting one turns the button into **Unhide**.
  What is in the build is untouched by any of this.

**Favourites** — mark a relic in the picker as wanted for one or more
Nightfarers, and it leads the grid the next time you open a slot for that
Nightfarer. It changes nothing about the build; it just saves hunting for a good
roll in a grid of two hundred.

A favourite follows the **roll**, not the copy. Two relics with the same effects
and curses are interchangeable in a build, so they count as the same favourite —
and melting one down and earning another with the same roll keeps the mark.
Curses are part of that identity: the same relic with and without a curse is not
the same thing. The picker also collapses duplicate rolls down to one tile for
the same reason.

**Deep of Night** — the checkbox under the vessel list adds the three extra
slots that Deep of Night runs give you.

Every chalice a Nightfarer owns is drawn in the list with its slots and
whatever is in them, so the list answers "which one had the poison build?"
without opening each in turn. A gold dot marks the chalice you have equipped
in game.

The first time you open a Nightfarer, all of their chalices are read out of
the save and the equipped one is shown. After that the app reopens on whatever
chalice you last had open, across sessions, along with the Deep of Night
setting. **Load equipped** reads the save again and goes back to the equipped
chalice; **Rescan save** re-reads the save from disk after you have earned or
melted relics.

Chalices you change here are remembered per chalice, so switching between them
does not disturb what is in the others. A chalice that is empty in game stays
empty here.

The line beneath them says what was read — how many relics, from which profile,
and how many stored builds. If the builds cannot be read it says why there,
rather than reporting none and leaving you to guess.

Saves are looked for under `%APPDATA%\Nightreign`, and **every** save found is
tried rather than only the most recently written one. A second Steam account
folder or a restored backup can otherwise sit in front of the save you actually
play.

**Level** — the slider runs 1 to 15, and the attribute figures come from the
game's own per-Nightfarer level tables, not a formula.

### Reading the right-hand panel

| Section | What it shows |
|---|---|
| **Base stats** | HP, FP and Stamina — your base, the change, and the total. |
| **Attributes** | All eight, same three-column layout. |
| **Weapon damage** | Six armament tiles. Double-click one to choose a weapon, its upgrade tier and the effects it rolled; the panel below breaks its attack rating down. |
| **Rally recovery** | How much HP a landed hit rallies back. A flat amount, not a share of damage dealt. |
| **Resistances** | The net change from everything equipped — changes, not totals. |
| **Multipliers** | Anything applying as a multiplier rather than a flat figure. |
| **Conditional & situational** | Effects that are not simply on. Each gets a switch, and its numbers join the totals only when you say the condition is met. |

Grey is your base at that level; the coloured figure is what the equipped relics
add. **Curses are shown in red** with a ✦, both on the slot and in the totals —
they are folded into the maths rather than quietly ignored.

**About the switches.** The tool cannot know whether you are below 40% HP, or
how many Night Invaders you have killed, or whether your Character Skill is up
right now. What it can know is what each of those is worth, so a gated effect is
kept out of the flat totals and offered as a switch instead. Counting one
unconditionally invents a bonus you usually do not have — and worse, corrupts
every buff multiplied against it.

An effect that only lasts a number of seconds once triggered belongs there too.
The Character Skill auras, "Power of the Blood Lord", "Power of Dark Moon" and
the rest are timed windows, not passives, and are treated as such.

**Every figure is clickable** for a per-buff breakdown showing which relic and
which effect contributed what.

---

## 2. Effects & chances

![Effects and chances](docs/screenshots/effects.png)

Every relic effect in the game — 577 buffs and 75 curses — with what each one
actually does and how likely you are to roll it.

| Column | Meaning |
|---|---|
| **Type** | Buff or curse. |
| **Tier** | Where an effect sits in a ladder of strengths sharing one name — "2 of 2" is the stronger. |
| **Copies** | How many times it can appear on a single relic. |
| **Colours** | Which relic colours can roll it. |
| **Pools** | How many draw pools contain it. |
| **Avg / Best chance** | How likely on one roll of the selected colour and mode. Where an effect comes from several pools you get its average and its best. |
| **Stacks** | Whether a second copy adds anything. Read from the game's own mutual-exclusion keys, not guessed from a shared category. |
| **Comes with curse** | Whether rolling it drags a curse along — *sometimes* or *always cursed*. |
| **What it does** | The game's own caption paired with the derived numbers. |

**Filters** — colour, Normal or Deep, *Rollable on relics only*, *Non-stacking
only*, *Stacking only*, and a buffs/curses selector.

Identical duplicates are merged. Around 50 effects carry nothing beyond a name in
the game files; they are labelled as such rather than padded out.

---

## 3. Weapons & spells

![Weapons and spells](docs/screenshots/weapons.png)

Every armament, sorcery and incantation, grouped by family with counts.

- **Upgrade to +N** recalculates at that upgrade level.
- **Rarity** filters to a tier.

The line under the search box states exactly what is being assumed — the
Nightfarer, the level, the upgrade, and every attribute feeding the calculation.

Attack rating is base damage plus what your stats add to it. **Spell damage is
not in the game data**, so sorceries and incantations show their costs instead of
an invented figure.

Every tile carries the weapon's **scaling**, and the infusions of one armament
sit together so they can be read against each other. Where an infusion moves
the scaling, the tile says by how much against the uninfused version — a Sacred
Longsword reads `STR 43 · DEX 43 · FAI 30`, with `vs standard: FAI +30 · STR −7
· DEX −7`.

### Which armaments can roll effects

Of the 395 distinct armaments, **387 roll effects**. The eight that never do are
Unarmed and the Nightfarers' own starting armaments.

An **infused** weapon has no pool of its own, because the infusion is the effect
it rolled. It can still carry **one further buff and one debuff** on top — the
planner offers it the uninfused version's pool and caps it at one of each, while
an uninfused weapon takes up to three. Negative rolls come from the same pool as
everything else and are marked in red, in the picker and on the tile.

---

## 4. Nightlords

![Nightlords](docs/screenshots/nightlords.png)

Ten Nightlords, each carrying its Everdark Sovereign rather than repeating it.
The two are the same character and every extracted figure is identical between
them, so one entry shows both: the portrait is a single circle split on the
diagonal, regular art in the lower-left and Everdark in the upper-right.
Straghess and Heolstor have no Everdark version. Select one for its detail
panel.

**What a weakness is for.** The panel opens with the interaction rather than
the chart: the right damage type builds a hidden meter, and filling it breaks
the boss's stance and opens it up for a critical. Three bosses are also seen to
take a debuff while broken — double damage taken, a fifth off their attack —
shown with the visual tell that says it has landed.

**Also on the panel.** Damage and status charts. The stance bar, its refill
rate and where the boss ranks among the ten. The attack buff each boss puts on
itself, whether it stacks and what sets it off. Per-part damage where a boss
tunes it — only Gladius has a soft spot and only Caligo has armour. Libra's
defence buff, which no other boss has.

**Where the figures stop.** The break threshold is not extracted: the chain is
named in the game's own AI script, but those scripts are compiled and their
constants are not yet tied to the functions that use them. Which body part a
number refers to is not in the files either, so the panel says "Part 1" rather
than naming it. Both say so on the page instead of guessing.

---

## 5. Deep of Night

![Deep of Night](docs/screenshots/deep_of_night.png)

What each of the five Depths changes, in the order the questions get asked.

- **What each depth is worth** — the rating band that puts you in it, the reward
  multiplier, the Sovereign Sigil award and the relic tier the depth can hand
  out, side by side. The tier climbs as you sink: Depth 1 still pays Polished
  relics, from Depth 4 only Grand ones are on the table.
- **How much tougher enemies get** — HP, attack power, stance damage taken and
  stamina drain on block, per Depth. The big figure is typical and the range
  under it is the spread from the weakest enemy group to the toughest, because
  the game sorts enemies into groups without recording which creature is in
  which.
- **What moves your rating** — a win, and what each kind of loss costs, per
  Depth. This block is **not** from the game files and says so on itself: no
  param holds it. The win value and Depth 1 costing nothing are confirmed in
  game; the bonuses and the loss table are community-reported.
- **What else changes with depth** — the chance of a second cataclysm, of the
  map or the Nightlord being hidden from you, and the rates at which relics
  come cursed. Read from the game's own depth table.

The tables are read, not operated, so nothing on this tab responds to a click.

---

## 6. Red variants

![Red variants](docs/screenshots/depth_weighting.png)

How many red, empowered variants a Deep of Night run puts on the map, and of
what. A red variant is always the same enemy re-tuned — never a different one
— and they appear as individuals scattered through the map, several per camp.

One row per sort of thing that can be red: ordinary enemies in camps and
ruins, named field enemies and minibosses (Golden Hippopotamus, Grave Warden
Duelist, …), evergaol bosses, night bosses, merchants. One column per Depth,
showing the game's own placement counts — on the default map, 87 red variants
at Depth 1 rising to 100 at Depth 5, and the boss tiers only join the pool
from Depth 2 on. A map selector covers the Shifting Earths and the Great
Hollow, which runs noticeably hotter than Limveld.

These counts are not published anywhere else — they are read straight out of
the game's data.

---

## 7. World Events

![World events](docs/screenshots/world_events.png)

The events that can interrupt an expedition, one card each: which Nightlords
it can appear under and how often, what happens, what you win, what you lose.

The percentages beside each Nightlord say how much of that boss's map pool
carries the event — the closest thing to "how likely am I to see this" the
game's data supports. The demon's card lists everything the demon can do, in
the game's own words.

Anything shown in blue is community-reported and could not be verified against
the game's data. The three expansion events are tagged **Deep of Night only**,
and events with no announcement banner are marked *no banner*.

---

## The window

**The three panels can be resized.** Drag the dividers between the Nightfarer
sidebar, the relic slots and the stat sheet — useful in both directions, since
a long relic name needs a wider sidebar and a wide monitor can give the slots
more room than the old fixed widths allowed. Where you leave them is remembered
between sessions, and none of the three can be dragged shut.

**UI scale**, top right. It multiplies whatever Windows' own display scaling
already asks for, so **Automatic** is your Windows setting unchanged — which is
why there is no "100%" entry saying the same thing twice. Qt reads the scale
once, as the program starts, and gives no way to change it after; so choosing a
new one offers to restart the tool rather than pretending to redraw. Your
relics, saved builds and favourites are kept across that restart. The armament
tiles and any conditions you have switched on are only kept for the run of the
program, and start again.

## Searching

The **relic picker** and the **Weapons** tab take a query syntax:

| Query | Finds |
|---|---|
| `poise stamina` | entries matching **both** words |
| `poise OR stamina` | either |
| `poise NOT curse` | poise, excluding anything matching *curse* |
| `"attack power"` | that exact phrase |

The **Effects** box is simpler — a plain substring match, no operators. It
searches descriptions as well as names. The Nightlords tab has no search: ten
entries fit on screen at once.

## Where your data lives

Everything the tool extracts goes to:

```
%LOCALAPPDATA%\NightreignHelper
```

That folder holds the data snapshot and the icon pack, both built from your
installation on first run. Your saved builds, favourites, artwork choices,
panel widths and interface scale are small enough to live in the registry,
under `HKCU\Software\DankYeeter`, and
the Start Menu entry — if you accept it — is one shortcut in your own profile.
**Nothing is written anywhere else**, and nothing is sent anywhere: the tool
makes no network connections at all. Uninstalling means deleting that folder,
that registry key, the shortcut and the EXE.

The snapshot is rebuilt when it no longer matches. That is either because the
game was patched, so `regulation.bin` changed, or because a new version of the
tool reads more out of the game than the version that built the snapshot did.
The icon pack is rebuilt the same way, when a new version needs artwork the
one on disk was never asked for. All of it is noticed on the next launch, and
says so while it rebuilds.

## Running from source

Install Python 3.12 from [python.org](https://www.python.org/downloads/), then:

```bat
py -3.12 scripts\setup_check.py --fix
```

That one command creates the virtual environment, installs every dependency and
verifies the result:

```
[  ok   ] Python interpreter                    3.12.10
[  ok   ] virtual environment                   ...\.venv
[  ok   ] python packages                       pycryptodome, zstandard, PySide6, ...
[  ok   ] paramdefs (required to read the game) 226 files
[  ok   ] Nightreign installation               D:\SteamLibrary\...\Game
[  ok   ] save file                             2 profile(s)
```

Then start it — the first launch builds the data itself:

```bat
.venv\Scripts\python.exe run.py
```

To build the data deliberately instead:

```bat
.venv\Scripts\python.exe scripts\build_snapshot.py
.venv\Scripts\python.exe scripts\build_icons.py
```

To package your own EXE:

```bat
.venv\Scripts\pyinstaller.exe NightreignHelper.spec --noconfirm
```

Close any running copy first, or Windows' file lock makes PyInstaller fail with
`PermissionError`. The EXE takes its version from `nrplanner/__init__.py`, so
Properties → Details reports the build without having to run it.

To refresh the screenshots in this README after a tab changes:

```bat
.venv\Scripts\python.exe scripts\make_screenshots.py
```

### Tests

```bat
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m pytest
```

They need no display and open no window. Tests that need the game data read
your own installation, or the snapshot it built; on a machine without
NIGHTREIGN they skip and say so rather than fail. Nothing in
`requirements-dev.txt` reaches the packaged EXE.

`tests/golden/weapon_damage.json` holds what the weapon-damage panel said at
one game version, so a change to the calculation cannot pass unnoticed. It is
regenerated with `scripts\capture_weapon_damage.py` — but only after the new
figures have been checked, because regenerating it is how the evidence gets
thrown away.

### Layout

| Path | Purpose |
|---|---|
| `nrdata/` | Reading the game's own formats — archives, params, textures, saves. No GUI code. |
| `nrplanner/` | The GUI, the build maths, and save inventory. |
| `scripts/` | Environment check, data builders, icon generator, screenshot generator. |
| `tests/` | The test suite. Headless; skips what needs a game it cannot find. |
| `vendor/Paramdex/NR/Defs` | Field schemas for the params. Required to read anything. |

## How values are derived

One rule runs through the whole project: **every value comes from the game files,
and anything that does not is labelled.**

In practice that means stacking rules are read from the game's own exclusivity
keys rather than inferred from a shared category; conditional effects stay out of
the flat totals rather than being applied unconditionally; and where a chain from
the menu to the underlying data cannot be closed, the tab says so on itself.

The handful of figures that genuinely are not in the files — the expedition
rating table, the cataclysm split — are marked *confirmed in game* or
*community-reported* where they appear, never presented as extracted data.

It also means a field is shown only when it is understood. Some values in the
game's tables are pointers into other tables rather than quantities, and a few
are named for Elden Ring in a way that does not hold for Nightreign; those are
left off the sheet rather than printed as stats with impossible numbers.

The same rule applies to the tool's own past conclusions. The twenty
"[Nightfarer] Improved X, Reduced Y" relics were recorded as unreadable — their
effect rows carry no numbers anywhere — and that was wrong. The numbers are in a
second family of `HeroStatusParam` blocks, stored as signed deltas in unsigned
byte fields, so a −1 reads as 255 and looks like noise. All twenty now show
their real attribute changes; each is only shipped if the sign of every delta
agrees with the effect's own name, so a block assigned to the wrong Nightfarer
would be dropped rather than displayed.

## Known limits

Stated plainly rather than hidden:

- **Attack rating has not been verified against an in-game number.** The maths
  follows the game's own fields, but the final figure has not been checked
  against what the game displays.
- **Don't scan while the game is saving.** A save read part-way through being
  written gives records that were never there — measured once at 290 against a
  true 284. The reader now waits for the file to settle, and on a settled file
  the count matches the game exactly, but a scan timed badly enough can still
  be wrong. Rescan after the game has written, or with it closed.
- **The break threshold is unknown.** The weakness chain is named in the AI
  scripts, but their constants are not yet scoped to the functions using them.
- **Weak parts are numbered, not named.** Nothing in the files says which body
  part a slot refers to.
- **Spell damage is unavailable** — no such field exists in the data.
- **Mutation categories are unnamed** in the files, so the Depth weighting tab
  shows ids.

## Disclaimer

Nightreign Helper is an unofficial fan project. It is **not affiliated with,
endorsed by, sponsored by, or approved by** FromSoftware, Inc. or Bandai Namco
Entertainment Inc.

ELDEN RING NIGHTREIGN, its data, artwork, text and trademarks are the property of
their respective owners. This project distributes none of that content. All game
values and images the tool displays are read at runtime from the copy of the game
on the user's own machine, into that machine's local storage only.

Screenshots in this README show the tool's own interface displaying data read
from a personal installation.

The application icon was generated with Google Gemini and contains no game
assets. The source artwork is in `art/`; `scripts/make_icon.py` produces the
shipped PNG and ICO from it.

The byte layouts of the game's param tables come from the community
[Paramdex](https://github.com/soulsmods/Paramdex) project — the schema only,
which is what makes an otherwise opaque binary readable. Everything built on
top of it is this project's own. See [`vendor/Paramdex/NOTICE`](vendor/Paramdex/NOTICE).

## Licence

[MIT](LICENSE) © DankYeeter — source code only. See the disclaimer above for game
content.

The released executable bundles its runtime dependencies, so their terms travel
with it — most notably **Qt, via PySide6, under the LGPL-3.0**. What is included
and how the LGPL obligations are met is set out in
[THIRD_PARTY.md](THIRD_PARTY.md), and `scripts/check_licences.py` fails the
build if a dependency is added without being recorded there.
