**Not affiliated.** Nightreign Helper is an unofficial fan project. It is not
affiliated with, endorsed by, sponsored by, or approved by FromSoftware, Inc.
or Bandai Namco Entertainment Inc. ELDEN RING NIGHTREIGN, its data, artwork,
text and trademarks are the property of their respective owners.

**What this program does.** It reads and decrypts, locally, the game files
and the save data of an installed copy of ELDEN RING NIGHTREIGN, using
decryption keys that have been publicly known in the modding community for
years. To open the game's own archives it also runs a small decompression
program out of that installation folder — a library that ships with the game
itself, not something this project adds. On first run it asks you to point it
at a copy of the game you trust, which for almost everyone is simply the one
they play. It never writes to the game or to the save file, and it makes no
network connection.

This executable contains no game data; it reads your own installation.

**Before you run it:** back up your save. This tool opens it read-only and
is not known to write to it, but it is provided "AS IS", under the MIT
licence, without warranty of any kind.

**Licence notices.** A notice package with the full licence text of every
bundled component — including Qt, used here through PySide6 under the
LGPL-3.0 — is attached to this release as `NightreignHelper-notices.zip`
(it contains `THIRD_PARTY.md`, the `licenses/` texts, `LICENSE`, and
`vendor/Paramdex/NOTICE`). Read it before redistributing this executable
yourself.

**Checksum.** Verify the download against the attached
`NightreignHelper.exe.sha256` before you run it:

```
Get-FileHash NightreignHelper.exe -Algorithm SHA256
```

or, without PowerShell:

```
certutil -hashfile NightreignHelper.exe SHA256
```

The value must match the one in `NightreignHelper.exe.sha256`.

---

## How to install

1. From the Assets list below, download `NightreignHelper.exe`. If you want
   to verify it (recommended), also download `NightreignHelper.exe.sha256`
   and run one of the commands above.
2. Windows will likely show a SmartScreen warning ("Windows protected your
   PC") because the executable is not code-signed. Click **More info**, then
   **Run anyway** to start it.
3. Run `NightreignHelper.exe`. No installer, no admin rights, no Python. On
   first launch it looks for your own ELDEN RING NIGHTREIGN install; if it
   cannot find it automatically, a panel asks you to point at the folder —
   only a Steam installation is accepted. Nothing in that folder is moved,
   copied or deleted.

## What's new since 1.7.1

Versions before 1.10.0 were not reconstructed (`CHANGELOG.md`); this list
starts there.

- **1.10.0** — a folder picker when the game install isn't found
  automatically (Steam installs only); the relic advisor gained Worst-case
  and Best-case readings; "Maximise damage" now works without a reference
  weapon; the window opens wider by default.
- **1.10.1** — search operators (`AND`/`OR`/`NOT`) now only work in capitals;
  every suggestion card got its own "Why" button; three measured damage
  values and two passive-bonus multipliers were corrected.
- **1.11.0** — relic suggestions now always count conditional effects (one
  reading instead of a Worst/Best-case choice); any effect or curse line can
  be marked "Must include" or "Don't include" for suggestions, with keyboard
  support.
- **1.12.0** — weapon cards, the stat sheet and the arsenal now show a
  two-handed damage value next to the one-handed one; the hand a build uses
  is saved per build; the relic picker and advisor recalculation are faster.
- **1.12.1** — a legend for the relic marking colours is now always visible
  in the picker; the equipped hand is highlighted on the stat sheet and
  arsenal; a bug where switching to two-handed leaked into the next
  equipment import was fixed.
- **1.12.2** — paired weapons (twinblades, fists, claws, paired swords) now
  use their own two-handed damage multiplier, matching measured values; the
  relic picker opens faster.
- **1.12.3** — attack power is now labelled `147 1H / 151 2H`; the relic
  picker no longer leaves its grid incomplete while you filter, sort or
  rescan.
- **1.13.0 / 1.13.1** — the "Must include"/"Don't include" relic marks are
  now called **Favourite**/**Avoid** and moved out of dots on each effect
  line into a dedicated Filters window listing every effect and curse a
  relic of yours carries, with its own search and sorting; that window now
  also explains, in a line under the search field, what the two marks do
  and that they are separate from the star on a relic card. Enter now
  selects a focused Nightfarer tile the same way Space already does. This
  build is only produced after the full automated test suite has passed.
- **1.13.2** — if a relic you are already holding carries a Favourite effect,
  the suggestion now says so directly under its effect lines, not only in
  the "Why" dialog.
- **1.14.0** — attribute effects and curses on a relic now change the attack
  figure through the Nightfarer's starting armament, in both directions,
  with the amount named in the "Why" line; the Filters window now groups
  effects by family under a shared Avoid header, with a per-member Allow to
  let one effect of an avoided family back into suggestions.
- **1.15.0** — the Nightlords tab gained a sub-boss tree (Night bosses Day 1/
  Day 2, Field bosses) with HP and loot for each; the Red variants tab drops
  its "Examples" column now that those names appear in full there. The data
  cache rebuilds once on first launch after this update (about 35 seconds,
  plus the icon pack).
- **1.16.0** — "Maximise damage" gained a "Damage type" choice (All,
  Physical, Magic, Fire, Lightning, Holy, Skill attack (Weapon Arts only),
  Sorceries, Incantations, or a spell school), remembered the next time you
  start the program; the ranking, the "Why" line, the card headline and the
  relic picker all follow it, and starting-armament conversion relics count
  toward the figure. For a spell-type choice, the "Why" line also notes that
  it scales the reference weapon's attack rating, not spell damage itself. A
  choice that raises nothing you own no longer fills suggestion slots with
  candidates that change nothing.
- **1.17.0** — "Maximise damage" now asks two things: **Hit with** (Weapon,
  Weapon art, Sorceries, Incantations, or a spell school) and **Damage
  type** (All, Physical, Magic, Fire, Lightning, Holy); a spell row ranks
  the spell your starting catalyst casts, and a "starting spell" relic
  (for example Beast Claw) replaces it and counts as a candidate — spell
  damage is uncalibrated, following the known Elden Ring formula. "Skill
  attack" is renamed **Weapon art**. Both choices are remembered. The data
  cache rebuilds once on first launch after this update (about 40
  seconds). The opening window width now scales with your screen (90% of
  available width, 1536-1959 px) instead of a fixed size.
- **1.18.0** — the Build planner's damage block can now show a **Weapon
  art** row (what your character skill adds on top of the Total; a
  sentence instead of a figure on a staff or seal) and a **Spell damage**
  row for a starting catalyst (the spell a "starting spell" relic sets, or
  else the catalyst's default), each carrying only the change your relics
  make to it. The "Why" line under a spell-school choice now names the
  correct relic that moved a figure.
- **1.19.0** — your last selected Nightfarer is now remembered across a
  restart; Deep of Night, Red variant and World Event values sourced from
  community write-ups no longer carry a separate note or colour; the note
  under your inventory now tells you when a save-file scan passed over
  other readable saves; a damaged data cache no longer stops the program
  from starting; the relic advisor now counts a "3+ ... Equipped" weapon-count
  effect only for the weapon type on your highlighted weapon tile (and never
  two of them at once); a yellow warning line under the advisor bar says
  when nothing you own reaches your chosen Hit with / Damage type; the
  **Spell damage** row now appears for any Nightfarer who puts a staff or
  seal on the selected weapon tile; a crash when switching a weapon slot to
  a weapon without effects in the armament dialog and closing it is fixed,
  and closed dialogs no longer pile up in memory. The "Why" dialog now
  leads with the answer and folds away effects without a number and the
  footnotes; saving a build and re-clicking the selected Nightfarer now
  confirm what happened; the advisor bar wraps into two rows on a narrow
  window (smallest window width is now about 1190 px, was 760 px); each
  character slot of your save is now checked against its stored checksum,
  and a mismatch is reported as "not readable" with the reason instead of
  showing possibly wrong relics; a new **Casting** block under the weapon
  tiles lets you choose, with icons, the spell (staff or seal: `R1` fixed to
  the default, `R2` from the weapon's pool) or the weapon art (from the
  weapon's pool) the panel counts for the selected tile, and the advisor
  now calculates with the highlighted tile's weapon, spell and art; the
  **Weapon art** row shows one figure (flat-bonus arts included); spell
  damage was checked against the in-game training dummy; effect lines of a
  relic with the same value are combined (a curse of six equal lines is one
  line); the build line, the no-save sentences and the folder picker ("This
  PC" as start) were reworked; an empty build can be saved; and the pool list
  stays on screen at every display scaling. **The data cache rebuilds once on
  first launch after this update (about 40 seconds, plus the icon pack).**
  Many smaller wording and tooltip fixes (see `CHANGELOG.md`).
- **1.19.1** — the relic advisor, its "Why" dialog and the relic picker's
  Damage column now count a weapon-type bonus (for example "Improved Dagger
  Attack Power") only for the weapon on your highlighted weapon tile, as they
  already did for the "3+ ... Equipped" effects; with an empty tile only your
  Nightfarer's starting weapon type counts. The relic picker no longer
  stretches its cards to the full window height when a filter leaves only a
  few relics. The data cache is not rebuilt.
- **1.20.0** — the relic advisor counts "Attack power up when facing
  frostbite-afflicted enemy" and its poison and scarlet rot versions only
  when your build inflicts that ailment itself (a weapon on any tile, a
  rolled effect such as "Attacks Inflict Frost", the weapon skill or spell
  chosen in the casting bar, or a relic that adds the ailment or swaps in a
  skill that inflicts it); the "Why" dialog no longer claims a favourited
  effect "always counts" when it does not, and says why it is not counted.
  **The data cache rebuilds once on first launch after this update (about
  45 seconds; the icon pack is not rebuilt).** Saved builds and favourites
  are kept.
- **1.20.1** — changes what 1.20.0 said: the ailment bonuses ("Attack power
  up when facing frostbite-afflicted enemy" and its poison and scarlet rot
  versions) no longer count when a weapon on *any* tile inflicts the ailment.
  They now count only for the weapon on your **highlighted tile** (its rolled
  effects, skill or spell; your Nightfarer's starting weapon if that tile is
  empty) or for a relic that adds the ailment; weapons on other tiles no
  longer count. A relic that swaps the highlighted weapon's skill or spell for
  one without the ailment now also removes it as a source. The relic picker
  no longer shows stray relic cards beside the
  list when you type into the filter while the list is still filling. The
  data cache is not rebuilt.
