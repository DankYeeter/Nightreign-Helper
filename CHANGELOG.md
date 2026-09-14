# Changelog

All notable changes to Nightreign Helper are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
History before 1.10.0 was not reconstructed; this file starts here.

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
