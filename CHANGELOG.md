# Changelog

All notable changes to Nightreign Helper are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
History before 1.10.0 was not reconstructed; this file starts here.

## [1.19.0] - 2026-09-23

### Added
- The Nightfarer you last selected is now remembered across a restart; the
  program reopens with that one instead of always the first in the list.

### Changed
- Deep of Night, Red variant and World Event values that come from
  community write-ups (rather than the game's own data) are no longer
  marked "community-reported" or shown in a different colour; they now
  appear alongside every other value. Their content is unchanged.
- The colours used for community-reported and curse/debuff values are now
  the same on every tab that shows them (they used to differ from tab to
  tab); the curse colour on the effects list also now meets standard
  contrast guidelines.

### Fixed
- If your save-file scan found more than one readable save, the program
  silently picked the one with the most relics without telling you (or,
  on a tie, the wrong one). The note under your inventory now says how
  many other saves were found, correctly credits a tie to the most recent
  one, and keeps the "Find my save" button available so you can pick a
  different save.
- A damaged or cut-short data cache file could stop the program from
  starting when it also could not find your game install; it now falls
  back to extracting fresh data instead, the same as if there were no
  cache file at all.
- The data cache file is now written atomically, so an interruption while
  it is being built can no longer leave a corrupted file behind.

## [1.18.0] - 2026-09-21

### Added
- The Build planner's damage block, under a Nightfarer's starting armament,
  can now show two more rows below the Total: **Weapon art** (the attack
  rating your character skill adds on top of that Total; on a staff or a
  seal, a sentence explaining that a catalyst has no attack art instead of
  a figure) and **Spell damage (\<spell name>)** for a starting catalyst
  (the spell a "starting spell" relic sets, or else the catalyst's own
  default; Revenant's default Rejection/Heal show `0`, not a sentence).
  Each row carries only the change your relics make to it; the two rows
  are never added together. Click the bold spell-damage figure for a
  breakdown tooltip, which always ends with a note that the figure is
  uncalibrated (the known Elden Ring formula, not checked against
  Nightreign) or, for a spell that deals no damage, that only a relic
  swapping the cast spell would bring damage here.

### Fixed
- Under a spell-school choice, the "Why" line now names the "starting
  spell" relic that actually moved the figure, instead of a school buff
  that this choice does not count (QA-293).

### Known
- The Weapon art row's change is plain text, not a coloured link like the
  Total row above it (QA-295).

## [1.17.0] - 2026-09-21

### Added
- "Maximise damage" now asks two things instead of one: **Hit with**
  (Weapon, Weapon art, Sorceries, Incantations, or one of the spell schools
  the game defines) and **Damage type** (All, Physical, Magic, Fire,
  Lightning, Holy). A spell row ranks the spell your starting catalyst
  casts (for example Recluse's Staff or Revenant's Finger Seal); a
  "starting spell" relic (for example Beast Claw) replaces that spell and
  is itself a candidate. Spell damage is computed as base damage times
  spell power over 100 times your buffs and is marked uncalibrated — it
  follows the formula known from Elden Ring, which has not been measured
  against Nightreign. Both choices are remembered the next time you start
  the program, the same way the active Nightfarer is.
- The opening window width is now 90% of your screen's available width,
  capped at what the layout needs (1959 px) and never narrower than
  1536 px, so it scales with the monitor instead of a fixed pixel count.

### Changed
- "Skill attack" is renamed **Weapon art** throughout the advisor, the
  relic picker and the "Why" dialog, to match the game's own term and to
  make room for the new Hit-with choices that are not weapon-based at all.
- The Arsenal tab's introductory sentence was corrected.

### Fixed
- The extractor now also reads spell damage figures, which hand a
  Nightfarer's starting catalyst is held in, and "starting spell" relics.
  The first launch after this update rebuilds the data cache once (about
  40 seconds) to pick this up.

### Note
- The remembered choice now uses two settings keys, `hit_with` and
  `damage_type`. The previous single key (`damage_art`) is no longer read;
  updating from an earlier version starts with no stored choice (Weapon /
  All) instead of carrying the old value over.
- Known issues, to be fixed in the next release: the "Why" line can
  attribute a suggestion to the wrong source when a spell school is chosen
  (QA-293), and a relic-picker cell can show as empty without saying why
  (QA-294).

## [1.16.0] - 2026-09-20

### Added
- "Maximise damage" now has a "Damage type" field next to it: All (the
  previous behaviour), Physical, Magic, Fire, Lightning, Holy, Skill attack
  (Weapon Arts only), Sorceries, Incantations, or one of the spell schools
  the game defines (for example Bestial). The suggestion ranking, the "Why"
  line, the card headline ("Skill attack rating" and similar) and the relic
  picker (which now labels its damage column "Damage (Fire)" and so on)
  all follow the chosen type. A Nightfarer's own skills are never counted
  under "Skill attack" — only Weapon Arts are. Conversion relics for a
  starting armament (attack power shifted between damage types) are
  counted in the figure, not only shown. A staff or seal is unaffected by
  the choice and the "Why" dialog says so by name. Below 1676 px window
  width, the "Maximise damage" and "Damage type" boxes may show a
  shortened label to make room. The chosen damage type is remembered the
  next time you start the program, the same way the active Nightfarer is.
- The "Why" line for a spell-type choice (Sorceries, Incantations, or a
  spell school) now adds a second sentence making clear that the ranking
  scales the reference weapon's attack rating, not spell damage itself,
  which the game's files do not record.

### Fixed
- A "Damage type" choice that raises nothing you currently own (for
  example "Fire" on a build with no fire-boosting relic) no longer fills
  suggestion slots with candidates that change nothing; the status line
  and the relic picker now agree that there is nothing to choose from.
- The relic picker's "Nothing you own raises damage in this slot" header
  now names the chosen damage type, matching the wording already used on
  each card and in the "Why" dialog.

### Note
- The remembered "Damage type" choice is stored under a new settings key
  (`damage_art`). Updating from an earlier version starts with no stored
  choice ("All"); if a stored value is ever unrecognised (for example
  after a downgrade to a version that used a different set of damage
  types), the program falls back to "All" instead of failing to start.

## [1.15.0] - 2026-09-19

### Added
- The Nightlords tab now has a sub-boss tree below the ten Nightlord cards:
  Night bosses Day 1, Night bosses Day 2 and Field bosses for the picked
  Nightlord. Selecting a sub-boss opens the same detail panel, with an HP
  line and, where the game's drop tables record any loot for it, a LOOT
  section — the five rarest drops shown by default, with a "Show N more"
  button for the rest. A card the files cannot narrow to one boss reads
  "Multiple possible bosses" and lists the HP of every candidate; a card the
  files do not identify at all reads "Not identified".

### Changed
- The Red variants tab drops its "Examples (any map)" column. The field-boss
  names it used to hint at now appear in full — with weakness, HP and loot —
  in the new Nightlords sub-boss tree instead. Two rows were renamed for
  accuracy: "Field bosses & arena locations" and "Mixed-boss arena
  locations".

### Fixed
- The "Show N more" button on a sub-boss's loot panel now also responds to a
  toggle sent by assistive technology (screen readers, switch access), not
  only to a mouse click.

### Note
- This release adds sub-boss data to the local game-data cache (data version
  15). The first start after updating rebuilds the cache, which takes about
  35 seconds, plus the icon pack; afterwards nothing further is needed.

## [1.14.0] - 2026-09-19

### Added
- Attribute effects and curses on a relic (Vigor, Mind, Endurance, Strength,
  Dexterity, Intelligence, Faith, Arcane) now change the attack figure
  through the Nightfarer's starting armament, in both directions; the "Why"
  line names the amount.
- The Effect filters window now groups effects by family under a shared
  header with its own **Avoid**; members of an avoided family get a third
  checkbox, **Allow**, so one member can stay in suggestions without pulling
  in the rest of the family.

### Fixed
- The counter label in the Effect filters window no longer wraps to a
  second line and inflates the window.
- The status line no longer counts a slot you are already holding a build
  in as empty.
- The attack-rating amount on an attribute effect is now attached to the
  attribute that actually scales the reference weapon, not always the
  first attribute listed.

## [1.13.2] - 2026-09-17

### Added
- If a relic you are already holding carries a Favourite effect, the
  suggestion now says so directly under its effect lines instead of only in
  the "Why" dialog.

## [1.13.1] - 2026-09-16

### Added
- The Filters window now explains, in a line under the search field, that
  Favourite and Avoid control the relic advisor's suggestions and are
  separate from the star on a relic card.

### Internal
- Releases are now only built after the full automated test suite has
  passed; the release workflow's own test dependencies are pinned to exact
  versions, and it no longer keeps the upload token available once the
  tests are done.

## [1.13.0] - 2026-09-15

### Added
- A new Filters window lists every effect and curse carried by relics you
  own, one row each, with checkboxes to mark it **Favourite** or **Avoid**
  for the relic advisor; it has its own search field, a count of active
  marks, and is sorted by name. It replaces the per-line marking dots on
  relic cards and in a relic's "Why" dialog, which are now plain read-only
  text. Existing marks are kept.
- Enter now selects a focused Nightfarer tile, the same as Space already
  did.

### Changed
- The advisor's "Must include"/"Don't include" marks are now called
  **Favourite** and **Avoid** everywhere they appear.

## [1.12.3] - 2026-09-15

### Changed
- Attack power for both hands is now labelled `147 1H / 151 2H` on the
  weapon card, the stat sheet, and the arsenal.

### Fixed
- The relic picker no longer leaves the grid incomplete if you filter, sort,
  or rescan while cards are still being added to it.

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
