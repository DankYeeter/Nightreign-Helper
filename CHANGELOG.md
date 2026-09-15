# Changelog

All notable changes to Nightreign Helper are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
History before 1.10.0 was not reconstructed; this file starts here.

## [1.12.2] - 2026-09-15

### Changed
- Paired weapons (twinblades, fists, claws, paired swords) now use their own
  two-handed damage multiplier instead of the single-weapon one, matching
  measured values (twinblades x0.5, the others x0.77366).
- On the Weapons tab, the row for a paired weapon's type now shows both the
  one-handed and two-handed value, like the rest of the tab already does.
- The relic picker dialog now appears about 0.1 s faster; the relic cards
  are grouped into batches while drawing instead of all at once.

### Note
- This release changes how weapon data is extracted. The first start after
  updating rebuilds the local game-data cache, which takes about 2 minutes;
  afterwards nothing further is needed.

## [1.12.1] - 2026-09-15

### Added
- A legend explaining the relic marking colours (must include / don't
  include) is now always visible in the relic picker, not just on hover.
- The hand a build is set to (one-handed or two-handed) is now visually
  highlighted on the stat sheet and in the arsenal; the unused hand's values
  are shown dimmed instead of both looking equally current.

### Changed
- The advisor's sentence for a relic you own but that cannot fill any open
  slot now says so directly ("you own N copies ... but none fits the open
  slots"), instead of using the same wording as for a relic you don't own
  at all.

### Fixed
- Switching a build to two-handed no longer leaks into the next equipment
  import or reset; loading equipped gear and resetting the chalice both
  start from one-handed again, as intended.

## [1.12.0] - 2026-09-15

### Added
- Weapon damage on the relic card, stat sheet and arsenal now shows a
  two-handed value next to the one-handed one (e.g. "218 / 225 2H AR").
- A one-handed/two-handed switch on the stat sheet is saved per build; the
  relic advisor now ranks suggestions for whichever hand is selected.

### Changed
- The "comes with a curse" verdict on the effects tab is now decided once
  per relic identity across all its rows, instead of per row, so it no
  longer contradicts itself for the same relic.
- The label next to a starting-item requirement no longer misnames it as a
  weapon-count condition.
- Arsenal tiles that only differ by count are now combined into a single
  tile per name instead of listed separately.
- The window is kept on screen after opening, even when it would otherwise
  land partly off a smaller or differently arranged display.
- The vessel list now has a tooltip explaining what the slot colours mean.
- Relic-picker cards are cached, cutting the time to open the picker.
- Relic-advisor recalculation after a change is noticeably faster.

### Fixed
- The icon pack is now checked against the files actually present, not
  only against its version number, so a damaged or incomplete pack is
  caught instead of silently assumed complete.

## [1.11.0] - 2026-09-15

### Added
- Relic suggestions no longer offer a Worst-case/Best-case switch. There is
  one reading now, and it always counts conditional effects (the ones that
  only apply under a stated condition), so the suggestion matches what the
  build actually does.
- You can mark any effect or curse line, on a relic card or in its "Why"
  dialog, as "Don't include" or "Must include" for suggestions. A counter in
  the advisor bar shows how many marks are active, and marks are kept
  between sessions.
- When a "Must include" mark can no longer be met by any relic combination,
  the advisor bar now says so instead of giving no answer.
- The mark button can be reached and pressed with the keyboard (Enter).

### Fixed
- Overlapping relic markings could stop the advisor from producing any
  suggestion at all.

## [1.10.1] - 2026-09-14

### Changed
- Search operators (AND, OR, NOT) now only work written in capitals; in
  lowercase they are treated as ordinary search text, matching what the
  field's hint says. Curse names are now searched along with effects.
- Each suggestion card in the relic advisor has its own "Why" button, next
  to "Use", opening the same explanation as the advisor bar's.
- The effect search field shows a hint on its syntax (AND, OR, NOT, "quoted
  phrases"), matching the weapon search field.
- Relic picker cards size themselves from the font in use instead of a
  fixed width.

### Fixed
- Starting-armament damage that converts to an element (e.g. "deals fire
  damage") is now measured as its own step instead of folded into a flat
  multiplier; corrects three measured damage values (Wylder, Revenant,
  Duchess).
- The Raider's attack-power bonus on Greataxes and Great Hammers is now
  1.18x (was off), and the Revenant's Cursed Claws bonus when carried by
  another character is now 0.88x (was off).

## [1.10.0] - 2026-09-14

### Added
- When the game folder cannot be found automatically, a folder picker lets
  you choose it yourself. Only folders that belong to a Steam library are
  accepted; anything else is rejected with a clear message instead of
  failing silently.
- The relic advisor now offers two readings, Worst case and Best case, so
  you can see both the guaranteed and the optimistic outcome of a build.
- "Maximise damage" now ranks relics without needing a reference weapon;
  it uses attack multipliers, attributes and passives instead, the things
  that stay fixed between rounds.
- Relic cards show a third chip, "BEST FOR ATTRIBUTES", when a relic is the
  best pick on that basis.

### Changed
- The window now opens wider (1608 px) so the advisor bar's suggestion fits
  without resizing; the minimum usable width is now 1536 px, below which
  some controls may be clipped (a tooltip says so).
- Relic picker cards are now 208 px wide.

### Fixed
- An exclusive relic group's effect now counts once towards attribute
  totals, ranking and suggestions, instead of once per copy held (e.g.
  Strength +25 was being counted, and recommended, twice). The "only one
  will apply" warning now names it.

### Internal
- Parts of the main window (build stat sheet, save-file reading, relic slot
  handling) were moved into their own files. No user-visible change.
