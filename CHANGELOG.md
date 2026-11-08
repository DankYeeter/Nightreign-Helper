# Changelog

All notable changes to Nightreign Helper are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
History before 1.10.0 was not reconstructed; this file starts here.

## [Unreleased]

## [1.22.0] - 2026-11-08

### Changed
- **The World Events tab is redesigned.** Each event shows its game symbol,
  number tiles (Nightlords, enemy HP, base runes, drops), a bar per Nightlord
  and a Day 1 / Day 2 bar, and Win and Lose side by side with their effect
  symbols, figures and durations. New on the tab: every banner an event can
  end on, enemy HP, and the full drop list with symbols and shares. Hordes of
  the Night now shows its Ultimate Art charge buff (+30 % for 40 s).
- **Shorter explanations on Effects & chances, Weapons & spells and Deep of
  Night.** The paragraphs over the tables are now short bullet legends.
  Deep of Night is more compact, with one short legend under each table.
- **The Red variants tab is rebuilt around figures.** Two short bullets, a bar
  per Depth split by sort with the exact table under it, what each step deeper
  adds, all six maps side by side, and the 24 field bosses the game can turn
  red. The weapon-drop and Everdark lines are gone: the game's files do not
  back the first, and the second is on the Deep of Night tab already.
- **Favourite, Avoid, Allow and Stacks are now kept per Nightfarer.** Guard
  effects can be a Favourite on the Guardian and stay out of the Duchess's
  suggestions. What you marked before this update starts out on every
  Nightfarer; a change after that belongs to the one selected.
- **Balanced no longer leans towards attack.** It first finds the most attack
  and the most Defense the vessel can reach on its own, then picks the relics
  that get furthest towards both. Held, starred and favourite relics count in
  every step. Optimize under Balanced takes about three times as long.
- **Defense counts only the strongest damage negation.** Physical -12 % and
  Magic -10 % now make 12 % less damage taken, where before the eight damage
  types were averaged (+8 % here). The worst damage-taken penalty counts the
  same way. Nothing is ever added up.
- **The vessel tooltip now shows how AR and Defense are worked out**: from
  which number to which (`AR 158 → 276 (+75 %)`), what the AR is measured on,
  and that Defense is effective HP. Max HP counts in it, and only the
  strongest damage negation.

### Fixed
- **Ten spells that showed no damage now have their figure**: Glintstone
  Stars, Star Shower, Founding Rain of Stars, Stars of Ruin, Magic Downpour,
  Rykard's Rancor, Lightning Strike, Ancient Dragons' Lightning Strike,
  Carian Retaliation and Law of Causality. Their hit sits on a projectile
  another projectile keeps creating, nine projectiles deep, or on one the
  cast animation launches, and the program did not look there. No other
  spell's figure changes. **The data cache is rebuilt once on first start.**
- **A spell school of the other kind is now refused like the kind itself.**
  Asking the advisor about an incantation school (Bestial, Dragon Cult,
  Godslayer and the rest) with a staff, or a sorcery school with a seal,
  ranked the staff's Glintstone Pebble without a word. It now says the staff
  casts sorceries, as `Incantations` already did. A school of the right kind
  whose spell the staff does not cast keeps the figure and says so.

## [1.21.0] - 2026-11-07

### Changed
- **Vessel slots now show the game's own slot art**, normal and Deep, in the
  vessel list, the slot strip, the slot cards and the picker, in place of a
  light this program drew. White slots show no gem: the game has none.
- The icon pack and the data cache are rebuilt once on first start.
- **A stack effect now counts on one relic only.** "Attack power increased for
  each Night Invader defeated" and the seven other effects that stack per event
  count their stacks once, however many relics carry them. Optimize no longer
  suggests a second carrier unless a favourite needs that relic, and one you
  place yourself is flagged and moves no figure. Figures that used to count two
  carriers fall (Raider, two stacks: all damage +14.5 % where it was +31.1 %).
- **Each stack effect now has its own limit**, in the Stacks field, in the count
  on the stat sheet and in the figures: Night Invaders 4, evergaol prisoners and
  Sorcerer's Rises 7, great enemies 10. A Stacks value saved above the limit
  reads as empty. These limits are read from the game's event scripts and were
  not tried in play.
- **Avoid now keeps the relic out of Optimize's suggestions.** Before, Avoid
  only counted against a relic; now a relic carrying an effect or curse you
  marked Avoid is never suggested. A relic you hold or place yourself stays
  where you put it. If you want such a relic back in suggestions, set the
  effect to Allow again.
- **A star on a relic now means "must go in, if it fits".** Until now the star
  only sorted the picker. After this update every star you have already set
  also steers Optimize: a favourited relic goes into the suggestion when the
  chalice can hold it. Nothing is changed in your saved data; remove a star to
  go back to the old behaviour. When not every starred relic fits, the
  suggestion still comes, the status line counts the ones it could not place,
  and Why names each with its reason.
- A favourited effect no longer blocks a suggestion: Optimize carries every
  favourite the chalice can hold, fills the other slots, and Why names the
  rest. A slot Optimize leaves empty shows NO SUGGESTION with the reason.
- A favourited effect of another Nightfarer ("[Guardian] ..." while you build
  Wylder) is ignored there: it takes no slot and never counts as missing. The
  mark stays.
- Effects that land on the enemy no longer count as your own build's. They are
  listed as "On the enemy" and move no figure (see Fixed).
- **The count beside a switch on the stat sheet now stops at 99.** A larger
  number becomes 99 when you leave the box; a very large one could stop the
  sheet from drawing.

### Added
- **The game's own symbols, everywhere it has one.** Effects and curses show
  their status symbol on relic cards, in the picker, in suggestions, in `Why`,
  in the filter window, on the Effects tab, in the armament dialog and on the
  stat sheet. Relic, Nightfarer, vessel, damage type, status, weapon art, spell,
  Nightlord, loot, world-event buff and penalty, Sovereign Sigil, relic tier and
  slot colour show theirs beside the name. A name without a symbol reads as it
  did.
- **A new direction, Balanced.** It looks for damage and survival at once: it
  ranks by attack rating times effective HP, so one percent more of either
  counts the same, and there is nothing to set. It has its own row on every
  relic card, as a percentage, and its own entry under Sort by. In the vessel
  list each vessel then says both gains against the empty vessel, for example
  `AR +89 % / Defense +31 %`, and "Best of ..." goes by the Balanced value.
- The armament tiles under Weapon damage now show the armament's symbol above
  its name. Tiles grow a little taller; empty tiles stay as they were.
- **Stacks in the effect filter.** An effect that stacks, such as "Attack power
  increased for each Night Invader defeated", now has a Stacks field under
  Filters: Optimize and the figures in the relic picker count it that many
  times (a whole number from 0 to 10), 0 leaves it out, empty uses the count
  ticked on the stat sheet, otherwise one. The value is saved, changes nothing
  on the stat sheet, and **Why** lists it.
- Every effect and curse in a suggestion has an X that sets it to Avoid and
  asks again. Reject turns down a relic for this build only; the list under
  the advisor bar gives it back.
- Every Optimize now compares all vessels of the Nightfarer in the
  background: nothing waits for it, and a new question or closing the window
  stops it. The vessel list shows each vessel's figure and marks the best one
  (most favourite effects met, then favourite relics, then the figure);
  Switch to it opens that vessel with its suggestion and brings held relics
  and rejections along.
- The vessel figure now says what it means: its unit and the change from the
  same reckoning with no relics, for example `AR 90 (+61 %)`. The tooltip gives
  the figure without relics.
- The filter window, its tooltips and Why now say what Avoid and the star
  really do, and a favourite that went missing says how to get it back.

### Fixed
- In a narrow window the vessel list no longer scrolls sideways: a row too long
  for it ends in "…", and its tooltip carries the whole line.
- The gems in the Effects tab's `Colours` column no longer take room from
  `What it does`; the effect name column gives it up instead.
- The program could crash at the moment a background search or a save read
  ended. The more vessels were compared, the more often that moment came.
- Effects that land on the enemy no longer count as your own. "[Raider] Hit
  With Character Skill to Reduce Enemy Attack Power" lowered your attack
  rating; it and the others of its kind now say "On the enemy".
- Undo apply on a vessel that was empty no longer leaves the applied build
  stored for that vessel.
- Reset Chalice stays on the chalice you reset. It used to open the first
  chalice with its slots empty, and the next relic placed there replaced the
  build stored for that chalice.
- **Why now shows the whole figure of an effect counted several times.** With a
  count above one, its line named the figure of a single stack.
- **Sorting the effect filter by Type no longer fails** when a family heading is
  in the list.

## [1.20.1] - 2026-11-01

### Changed
- An ailment bonus such as "Attack power up when facing frostbite-afflicted
  enemy" now counts only for the weapon on the selected tile (its rolled
  effects, skill or spell; the starting weapon if that tile is empty) or a
  relic; weapons on other tiles no longer count.

### Fixed
- The relic picker no longer shows stray relic cards beside the list
  when you type into the filter while the list is still filling.
- An ailment bonus no longer counts for a skill or spell that a relic in
  the suggested build swaps out, such as Zamor Ice Storm replaced by Night
  Shard.

## [1.20.0] - 2026-11-01

### Changed
- The relic advisor counts "Attack power up when facing frostbite-afflicted
  enemy" and its poison and scarlet rot versions only when your build
  inflicts that ailment itself: a weapon on any tile, or a relic such as
  "Starting armament inflicts frost".
- These ailment sources now also include rolled effects such as "Attacks
  Inflict Frost" on any weapon tile, the weapon skill or spell selected in
  the casting bar, and relics that swap in a skill which inflicts the
  ailment (for example Poison Moth Flight). **The data cache is rebuilt once
  on first launch after this update (about 45 seconds; the icon pack is not
  rebuilt).** Your saved builds and favourites are kept.

### Fixed
- The Why dialog no longer says a favourited effect "always counts" when it
  does not count: a weapon-type bonus for another weapon type, or an ailment
  bonus your build cannot trigger, now says why it is not counted.

## [1.19.1] - 2026-11-01

### Fixed
- The relic advisor, its Why dialog and the relic picker's Damage column
  no longer count a weapon-type bonus such as "Improved Dagger Attack
  Power" for a type other than the weapon on your highlighted weapon tile,
  as for the "3+ ... Equipped" effects; with an empty highlighted tile only
  your Nightfarer's starting weapon type counts.
- The relic picker no longer stretches its cards to the full window height
  when a filter leaves only a few relics; cards stand at the top, each row
  as tall as its tallest card.

## [1.19.0] - 2026-10-28

### Added
- The Nightfarer you last selected is now remembered across a restart; the
  program reopens with that one instead of always the first in the list.
- Saving a build now confirms it with a short note by the build name
  (`Saved "name".`, or `Saved over "name".` when it replaced one).
- Clicking the Nightfarer that is already selected now tells you so
  (`<Name> is already selected.`) instead of doing nothing visible.
- Relic cards and weapon tiles that can be clicked now show which one the
  pointer is on.
- When a suggestion cannot reach the chosen Hit with / Damage type at all
  (for example Sorceries with Fire damage and nothing you own raising it),
  the advisor bar now shows that as its own yellow line, marked with a
  warning sign, directly under the bar; the bar text and tooltip stay.
- The **Spell damage (\<spell>)** row on the stat sheet now appears for
  every Nightfarer, not only those who start with a staff or seal: put any
  staff or seal on the selected weapon tile and the row shows that
  catalyst's spell with the figures of your current build.
- Under the six weapon tiles a **Casting** block now lets you choose which
  spell or weapon art the panel counts for the selected tile, with icons.
  On a staff or seal there is one chip per spell slot (`R1`, `R2`); on
  another weapon one `ART` chip. A click opens the list of spells or arts
  that weapon can carry, the weapon's default marked with a dot. `R1` is
  filled in with the staff's default spell; `R2` and the art can be picked
  from the weapon's list, because which spells a staff rolls is not known in
  advance. A weapon without a default art shows `Choose a weapon art` until
  you pick one. A relic that swaps the starting armament's spell or art wins
  over your choice and the block says so (`RELIC`). The choice is remembered
  per Nightfarer and tile until you close the program. The chips and the
  tiles can be reached with Tab.
- The **Weapon art** row now shows one figure for the chosen art. Arts that
  only add a flat amount (rather than a swing) get a figure too.
- Effect lines of one relic with the same value are now combined into one
  line (a curse that lowered six damage types by the same 45 % now takes one
  line instead of six).
- The build line above the relic grid no longer collides with the **Show
  hidden** button when the window is narrow; it wraps instead.
- The sentences shown when no save was found now name the button that fixes
  the cause.

### Changed
- The "Why" dialog now leads with the answer. Effects that carry no number
  and the footnotes are folded away behind buttons (`Show n effects without
  a number`, `Notes on these figures`); the notes open by themselves when
  they hold something you need to know. The button on the advisor bar is
  now `Why` (the whole suggestion) and the one on a relic card `Why this
  relic`, which opens the dialog at that relic's slot.
- When you have marked an effect as a favourite but a suggestion cannot
  count it (a build can meet the weapon-count condition of only one weapon
  type), the explanation now says so instead of claiming it always counts.
- The advisor bar wraps into two rows when the window is too narrow for one,
  instead of squeezing its buttons. The smallest window width is now about
  1190 px (it was 760 px); the opening size is unchanged.
- Clearer wording when a save has no relics, when relics the save has
  equipped are no longer in your inventory, when the stored builds of a save
  could not be read, and when the data shown is from an earlier day than
  your installed game. A Deep of Night slot left empty because its relic is
  worn elsewhere now says `— n left empty`.
- The filter menus show their full value in a tooltip, the Favourites menu
  shows each Nightfarer's name, and shortened column headers are read out in
  full by screen readers.
- If the Steam entry cannot be found, the folder picker for your game now
  opens at "This PC" rather than at a fixed Steam folder.
- Console error output no longer includes the text of the error itself.
- Deep of Night, Red variant and World Event values that come from
  community write-ups (rather than the game's own data) are no longer
  marked "community-reported" or shown in a different colour; they now
  appear alongside every other value. Their content is unchanged.
- The colours used for community-reported and curse/debuff values are now
  the same on every tab that shows them (they used to differ from tab to
  tab); the curse colour on the effects list also now meets standard
  contrast guidelines.
- The suggestions under **Hit with** Weapon art, Sorceries and Incantations
  now calculate with the weapon, the spell and the art on the weapon tile you
  have highlighted (an empty tile falls back to your starting weapon). Relics
  that swap a spell or an art are counted only when you hold one, and are
  never suggested. The explanation names the tile's spell or art.
- Weapon variants without art or spell choices of their own now inherit those
  of their base weapon (for example Magic Longsword takes the Longsword's).
- Spell damage is now calibrated against measurements on the in-game
  training dummy: the spell figure uses the game's 0.6 factor and the same
  rounding as weapon attack ratings, so it matches the dummy for the
  Glintstone Arc and Pebble cases we measured.
- The data cache is rebuilt once on the first launch after this update
  (about 40 seconds, plus the icon pack), because it now also stores weapon
  arts and each weapon's pools of spells and arts.
- The explanation (`Why`) and the yellow warning line under Weapon art now
  name the highlighted tile and its art.
- A keyboard-focused weapon tile or chip shows a dashed orange frame (a solid
  frame still marks the active one); the frame appears after Tab only, not
  after a mouse click, and no longer shifts the neighbouring tiles.

### Fixed
- The program now checks each character slot of your save against the
  checksum stored in the file. If one does not match, the save is reported
  as not readable, with the reason, rather than showing relics that may be
  wrong.
- A save with more relics than the program will read now ends in the
  explanatory sentence instead of an error trace, and malformed script data
  in the game's files is read within fixed limits.
- Two messages claimed the game was searched for on drives C to H; that
  search no longer exists, and the text now says what actually happens.
- Relic and curse names containing markup characters are now shown as plain
  text in tooltips.
- The survival goal now checks its weighting and damage-pass rate, and a
  weighting that names the same damage field twice is refused, instead of
  producing a wrong or absurd figure.
- The relic advisor no longer counts "3+ ... Equipped" weapon-count
  effects of weapon types you are not using (for example 3+ Daggers while
  your highlighted weapon tile holds a greatsword), and it no longer counts
  two different weapon-count conditions as both fulfilled in one suggestion,
  which would have needed more weapons than the six armament slots. Only
  the condition for the weapon type on the highlighted weapon tile counts;
  with an empty highlighted tile none does. Changing the highlighted tile
  updates the suggestion.
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
- The program could close without a message when you switched a weapon
  slot in the armament dialog from a weapon that has effects to one that
  has none (for example Unarmed, Wylder's Small Shield or a Finger Seal)
  and then pressed OK or Cancel. It no longer does.
- Closing a dialog (armament, Why, Filters, relic picker and the smaller
  ones) did not free it, so memory use grew by about 30 MB each time a
  dialog was opened. Dialogs are now released when they close.
- The explanation of a Hit with Sorceries / Incantations suggestion and its
  tooltip now name the staff or seal on the selected weapon tile, or else
  the starting one, which is the one the figure is computed for.
- A save that you cleared of all relic slots can now be saved as an empty
  build instead of being refused.
- Nightfarer names in the sidebar tooltips and the Favourites menu are shown
  as plain text.
- The pool list for a weapon art or spell opens fully on screen near the
  bottom or right edge of the display, and shows six icons per row at every
  display scaling (it showed five at 150 %).
- The list of World Events is drawn in its normal style again (a stray
  style rule made the console report `Could not parse stylesheet`).
- Without a save, the explanatory sentence for the legend of crossed-out
  relics names both meanings, and the bar without relics names the true
  cause.

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
