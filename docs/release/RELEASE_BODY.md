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
