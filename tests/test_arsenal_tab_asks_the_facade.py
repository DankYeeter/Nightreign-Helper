"""The arsenal tab's figure is the facade's answer, at the tab's own tier.

`ARCHITECTURE.md` Nachtrag III, checkpoint 20 -- and the blind spot that
checkpoint had to be written into, because nothing else covered it.

**What guarded the arsenal tab before this file: its attribute set, and
nothing else.** `test_one_build.py` checks three times that
`weapons_tab.attributes` is the build the planner tab shows (QA-001). No test
read a single figure off the tab, and none read the tier it ranked at.
Measured on 2026-09-03, on the tree before AD-019 step W4:

* halving the AR figure of **every** tile on the tab -- `rating.total * 0.5` --
  left **264 of 264** tests green;
* ranking the whole tab at `weapons.MAX_UPGRADE` instead of at the spinbox,
  so the "Upgrade to +n" control moved nothing at all, left **264 of 264**
  green.

Both are kept by name in `scripts/differential/mutate.py`
(`arsenal-tile-figure-halved`, `arsenal-ranks-at-the-slot-tier`) so the claim
can be re-run rather than believed.

**Read off the rendered tile, not off `tab.ratings`.** The list behind the tab
is what W4 changed; the label is what a player compares with the tile on the
planner tab. A test standing on the list would have moved with the change it
is meant to hold still. The AR row is located by its own left-hand label, so
a change in how a tile is laid out fails the match instead of quietly reading
a different number.

The two questions are separate cases on purpose. That the tab shows the
facade's `candidate()` answer, and that it asks that question at the
**spinbox's** tier rather than at the slot's, are different claims: the first
one holds just as well for a tab that ranks everything at tier 4.

**QA-086, added in W5: the guard above holds the AR row alone.** Measured
2026-09-03 on this tree, 275 of 275 green against four independent edits: a
damage-type row on a multi-type tile appended twice, the "Upgraded to" line
naming a tier the armament was not actually rated at, `effective_rarity`
dropped the `-1` that turns a rating tier into a rarity band (which the
rarity filter reads to decide what to show), and a spell's FP row doubled.
Two of those four get a case below -- a multi-type armament checked row by
row, and the rarity filter checked against an independently counted
expectation. The third (the "Upgraded to" line) rides along with the first
case, because both live on the same tile read at the same tier. The fourth
does not: see `_build_spells` in `nrplanner/arsenaltab.py` for why the spell
figures stay unguarded on purpose rather than by omission.
"""

from __future__ import annotations

import re

import pytest
from PySide6.QtWidgets import QLabel

from nrplanner import arsenaltab, damage, model, weapons, weaponslots

from tests import weapon_damage_cases as cases

LEVEL = 15

#: The two left-hand labels the headline row of a tile can carry. `Tile`
#: writes the rows as (label, value) pairs, headline first. Which of the two
#: a given armament gets is the facade's answer and not a constant here: a
#: staff or a seal is headed by the spell scaling the game shows for it and
#: has no attack rating at all (QA-099).
HEADLINE_ROWS = (damage.ATTACK_RATING_LABEL, damage.SPELL_POWER_LABEL)


def armaments(game_data, hero) -> list[int]:
    """Four armaments of four different kinds, chosen by query, never by id.

    The Nightfarer's own starting armament, a bow, a colossal sword and a
    catalyst: melee and ranged, physical and magic scaling, and one whose
    Strength wall is the steepest in the game.
    """
    return [
        hero["starting_weapon"],
        cases.first_of_family(game_data, "Bow"),
        cases.heaviest_of_family(game_data, "Colossal Sword"),
        cases.first_of_family(game_data, "Glintstone Staff"),
    ]


def drawn_tiles(tab, weapon: dict) -> list:
    """Every tile the tab really drew for this armament's name.

    The tab builds its sections lazily and opens them itself when a search
    matches a modest number of rows, so a search on the armament's own name
    is what puts a tile on screen at all. Names are not unique in the dataset
    -- four armaments are called "Scholar's Thrusting Sword" -- so this hands
    back every tile carrying the name and the caller says what it expects.
    """
    tab.search.setText(f'"{weapon["name"]}"')
    tab.recalculate()
    tiles = tab.scroll.widget().findChildren(arsenaltab.Tile)
    return [tile for tile in tiles if tile_name(tile) == weapon["name"]]


def tile_name(tile) -> str:
    """The armament name a tile carries.

    `Tile` adds the icon badge first and the name second, both `QLabel`, so
    the name is the second child. The badge holds no text, which is asserted
    rather than assumed: if the header ever gains a label, this reads the
    wrong one and has to fail here rather than compare the wrong armament.
    """
    labels = tile.findChildren(QLabel)
    assert len(labels) >= 2 and labels[0].text() == "", (
        "the tile header is not the icon badge followed by the name any "
        "more; this helper reads the wrong label")
    return labels[1].text()


def tile_headline(tile, expected) -> str:
    """The headline figure as the tile renders it, under its own row label.

    The label is taken from the facade's answer for this armament rather than
    searched for among both: a tile that headed a staff "AR" would then be
    found under the label it should not be carrying, and this helper would
    hide the very swap it is here to catch.
    """
    labels = [label.text() for label in tile.findChildren(QLabel)]
    row = expected.headline_label
    assert row in HEADLINE_ROWS, (
        f"the facade calls this figure {row!r}, which is neither of the two "
        f"labels this file knows: {HEADLINE_ROWS!r}")
    assert row in labels, f"no {row!r} row on this tile: {labels!r}"
    return labels[labels.index(row) + 1]


@pytest.fixture(scope="module")
def hero(game_data):
    """Wylder, the Nightfarer QA measured the QA-018/055 divergence on."""
    return cases.hero_by_name(game_data, "Wylder")


def prepare(planner, game_data, hero, slots) -> None:
    """Put the planner on this Nightfarer, this level and these tiles."""
    planner.hero_index = game_data["heroes"].index(hero)
    planner.level_slider.setValue(LEVEL)
    planner.weapon_slots = slots
    planner.declared = {}
    planner.selected_effects = lambda: []
    planner.recompute()


def empty_slots() -> list:
    return [weaponslots.WeaponSlot() for _ in range(weaponslots.SLOT_COUNT)]


def test_every_tile_shows_the_candidate_answer_for_the_chosen_tier(
        planner, game_data, hero):
    """The rendered AR is `damage.candidate()` at the tab's own tier.

    Over four armaments and every tier the spinbox can ask for. The figure is
    compared as the tile writes it, because that is what a player reads; the
    unrounded comparison over the whole dataset belongs to the differential
    track (`scripts/differential/rasters/arsenal_tab.json`), not here.
    """
    prepare(planner, game_data, hero, empty_slots())
    tab = planner.weapons_tab
    build = planner.current_build()

    seen = 0
    figures: set[str] = set()
    for weapon_id in armaments(game_data, hero):
        weapon = cases.weapon_by_id(game_data, weapon_id)
        for tier in range(weapons.MIN_UPGRADE,
                          weapons.MAX_UPGRADE + 1):
            tab.upgrade.setValue(tier)
            tiles = drawn_tiles(tab, weapon)
            assert tiles, (
                f"the tab drew no tile for {weapon['name']!r} at tier {tier}, "
                f"so there is nothing here to check")

            expected = damage.candidate(weapon, tier, build, game_data)
            for tile in tiles:
                shown = tile_headline(tile, expected)
                assert shown == str(
                        damage.displayed(expected.final_headline)), (
                    f"{weapon['name']!r} at tier {tier}: the tab and the "
                    f"facade name different figures")
                seen += 1
                figures.add(f"{weapon['name']}@{tier}={shown}")

    assert seen >= len(armaments(game_data, hero)), "nothing was compared"
    assert len(figures) > 1, (
        "every tile in this case shows the same figure, so an assertion on "
        "it could not tell the armaments or the tiers apart")


def test_the_tab_ranks_at_its_spinbox_tier_and_not_at_the_slot_s(
        planner, game_data, hero):
    """Checkpoint 20, and it is QA-055's own case.

    Slot on tier 3, spinbox on 1, not a single relic: the tab must go on
    ranking at tier 1, and it **may** differ from the tile and the panel next
    door. That difference is the tab's question, not a defect (AD-020,
    point 1) -- a test demanding equality here would be the error.

    What the case does insist on is that the two figures are the answers to
    the tiers they were asked for. Without the second half a tab that ranked
    at the slot's tier and a tab that ranked at the spinbox's would both pass
    whenever the two tiers happened to agree, which is why the guard below
    refuses a case where they do.
    """
    weapon = cases.weapon_by_id(game_data, hero["starting_weapon"])
    slot_tier, spinbox_tier = 3, 1

    slots = empty_slots()
    slots[0] = weaponslots.WeaponSlot(weapon=weapon, tier=slot_tier)
    prepare(planner, game_data, hero, slots)

    tab = planner.weapons_tab
    tab.upgrade.setValue(spinbox_tier)
    build = planner.current_build()

    at_spinbox = damage.candidate(weapon, spinbox_tier, build, game_data)
    at_slot = damage.candidate(weapon, slot_tier, build, game_data)
    assert (damage.displayed(at_spinbox.final_total)
            != damage.displayed(at_slot.final_total)), (
        f"{weapon['name']!r} rates the same at tier {spinbox_tier} and at "
        f"tier {slot_tier}, so this case cannot tell the two tiers apart. "
        f"Pick an armament the upgrade moves.")

    tiles = drawn_tiles(tab, weapon)
    assert tiles, f"the tab drew no tile for {weapon['name']!r}"
    for tile in tiles:
        assert tile_headline(tile, at_spinbox) == str(
                damage.displayed(at_spinbox.final_headline)), (
            f"the tab is ranking {weapon['name']!r} at a tier the spinbox "
            f"does not show")


# -- QA-086: two targeted additions, not a wider guard -----------------------

def tile_rows(tile) -> list[tuple[str, str]]:
    """Every (label, value) row on a tile, in the order `Tile` laid them out.

    The header is the icon badge (an empty label) and the name -- both
    asserted away rather than assumed, same as `tile_name` -- and everything
    after them comes in pairs.
    """
    labels = [label.text() for label in tile.findChildren(QLabel)]
    assert len(labels) >= 2 and labels[0] == "", (
        "the tile header is not the icon badge followed by the name any "
        "more; this helper reads the wrong labels")
    body = labels[2:]
    assert len(body) % 2 == 0, (
        f"the tile's rows are not (label, value) pairs any more: {labels!r}")
    return list(zip(body[0::2], body[1::2]))


def multitype_weapon(game_data, build, tier: int) -> dict:
    """The lowest-id armament this build rates at two or more damage types.

    Chosen by asking the facade, not by an id written down here: which
    armaments deal more than one damage type does not change often, but a
    hardcoded id would still be a guess about the dataset rather than a fact
    read off it.

    `shown_per_type`, so the answer is the rows the tile really draws. A
    catalyst has none of them whatever its physical rating breaks down into
    (QA-099), and one picked here would leave the case reading rows that are
    not on the tile.
    """
    for weapon in sorted(game_data["weapons"], key=lambda w: w["id"]):
        rating = damage.candidate(weapon, tier, build, game_data)
        if len(rating.shown_per_type) >= 2:
            return weapon
    raise LookupError(
        "no armament in this dataset rates at two or more damage types at "
        "this tier, so this case has nothing to check row by row")


def test_every_type_row_and_the_upgrade_line_match_the_facade(
        planner, game_data, hero):
    """QA-086 (a) and (b): the tile is checked past its headline AR row.

    `test_every_tile_shows_the_candidate_answer_for_the_chosen_tier` above
    reads only the AR row, which is exactly the gap QA-086 measured: doubling
    every damage-type row underneath it, or naming the wrong tier on the
    "Upgraded to" line, left that case and the whole suite green. A
    single-type armament could not catch either -- there would be only one
    type row to duplicate into, and duplicating one row that already carries
    the total looks the same as not duplicating it -- so this case picks a
    multi-type one and reads every row the facade has an opinion on.
    """
    prepare(planner, game_data, hero, empty_slots())
    tab = planner.weapons_tab
    build = planner.current_build()
    # Not MAX_UPGRADE: `reached` and the dataset's own ceiling would then be
    # the same number, and a mutation that hardcodes the ceiling in place of
    # `reached` would have nothing to disagree with.
    tier = weapons.MAX_UPGRADE - 1

    weapon = multitype_weapon(game_data, build, tier)
    tab.upgrade.setValue(tier)
    tiles = drawn_tiles(tab, weapon)
    assert tiles, f"the tab drew no tile for {weapon['name']!r}"

    expected = damage.candidate(weapon, tier, build, game_data)
    assert len(expected.shown_per_type) >= 2, (
        f"{weapon['name']!r} no longer rates at two or more damage types at "
        f"tier {tier}; this case needs one that does")
    own_tier = weapon.get("rarity", 0) + 1
    assert expected.tier_applied > own_tier, (
        f"{weapon['name']!r} is not actually upgraded by asking for tier "
        f"{tier}, so the 'Upgraded to' line has nothing to check")

    for tile in tiles:
        rows = tile_rows(tile)
        assert rows[0] == (expected.headline_label, str(damage.displayed(
            expected.final_headline)))

        type_rows = rows[1:1 + len(expected.shown_per_type)]
        expected_type_rows = [
            (weapons.DAMAGE_LABELS[damage_type],
             str(damage.displayed(value)))
            for damage_type, value in expected.shown_per_type.items()
        ]
        assert type_rows == expected_type_rows, (
            f"{weapon['name']!r}: the damage-type rows are "
            f"{type_rows!r}, the facade says {expected_type_rows!r}. A "
            f"doubled or dropped row would show here as an extra or "
            f"missing pair rather than a wrong number")

        remaining_type_labels = [label for label, _ in rows[len(expected_type_rows) + 1:]
                                 if label in weapons.DAMAGE_LABELS.values()]
        assert not remaining_type_labels, (
            f"{weapon['name']!r}: a damage-type row appears again after the "
            f"contiguous block the facade accounts for: {remaining_type_labels!r}")

        reached = min(expected.tier_applied, weapons.MAX_UPGRADE)
        expected_upgrade_row = (
            "Upgraded to",
            f"+{reached} {arsenaltab.RARITY_NAMES.get(reached - 1, '')}")
        assert expected_upgrade_row in rows, (
            f"{weapon['name']!r}: expected the row {expected_upgrade_row!r} "
            f"among {rows!r}")


def weapons_section_total(tab) -> int:
    """The N in the tab's "Weapons  (N)" heading.

    Read off the section's own toggle text rather than off `tab.ratings`, for
    the same reason `tile_headline` reads a label instead of a list entry:
    the count a player sees is the one this case is about.
    """
    heading = tab._top_sections[0].toggle.text()
    match = re.match(r"Weapons\s+\((\d+)\)", heading)
    assert match, f"unexpected weapons section heading: {heading!r}"
    return int(match.group(1))


def test_the_rarity_filter_agrees_with_the_section_count(
        planner, game_data, hero):
    """QA-086 (c): the band a player picks is the band the count describes.

    `effective_rarity` in `nrplanner/arsenaltab.py` turns a rating tier
    (1-based) into a rarity band (0-based) with a `-1` that this case is the
    only thing standing on: dropping it left every existing test green while
    every band but the top one showed the wrong armaments -- 856 armaments
    where the "Common" band should have shown 160 at tier 1 (QA-086).

    The expectation is counted independently of `effective_rarity` here, from
    the same tier-to-band relationship written out again rather than
    imported, so a wrong `-1` in the tab has nothing to agree with by
    sharing the code that computes it.
    """
    prepare(planner, game_data, hero, empty_slots())
    tab = planner.weapons_tab
    build = planner.current_build()
    tier = weapons.MIN_UPGRADE
    band = 0    # "Common"

    expected = sum(
        1 for rating in damage.rank_candidates(build, tier, game_data)
        if min(rating.tier_applied - 1, weapons.RARITY_TIERS - 1) == band
    )
    assert 0 < expected < len(game_data["weapons"]), (
        "the 'Common' band at this tier is empty or holds the whole "
        "dataset, so this case cannot tell a correct filter from a broken "
        "one")

    tab.upgrade.setValue(tier)
    index = tab.rarity_box.findData(band)
    assert index >= 0, f"the rarity filter has no entry for band {band}"
    tab.rarity_box.setCurrentIndex(index)
    tab.recalculate()

    assert weapons_section_total(tab) == expected, (
        f"the tab shows {weapons_section_total(tab)} armaments for the "
        f"'Common' band at tier {tier}, an independent count over the "
        f"facade's own ratings says {expected}")


def test_the_summary_names_the_level_the_build_was_computed_at(planner,
                                                               game_data,
                                                               hero):
    """QA-124: the level beside the figures comes from the same build.

    In the running program the slider and the build never disagree, so this
    changes nothing a player sees. It changes what a **tool** sees, and the
    differential track is one: it sets `planner._build` directly, never moves
    the slider, and every arsenal record it has ever written therefore says
    "level 1" whatever level it was measuring (QA-088 a). A summary line that
    can name a level the figures beside it do not belong to is a trap for the
    next measurement, and the next measurement is the thing this repository
    argues from.

    The two are pulled apart here on purpose: the slider stays where
    `prepare` left it and the build is replaced with one computed at another
    level, which is exactly the state the track puts the tab in.

    **Matched with the comma after the number**, which is not fussiness: the
    slider sits at 15 and the build is computed at 1, and "at level 1" is a
    substring of "at level 15". Written without the comma this case passed
    against its own counter-build -- measured, on the first run of
    `arsenal-summary-reads-the-slider`.
    """
    prepare(planner, game_data, hero, empty_slots())
    tab = planner.weapons_tab
    from_the_slider = planner.level_slider.value()
    elsewhere = weapons.MIN_UPGRADE    # any level the slider is not on
    assert from_the_slider != elsewhere, (
        "the slider already sits at the level this case swaps in, so it "
        "cannot tell the two sources apart")

    planner._build = model.compute(hero, elsewhere, [],
                                   game_data.get("curves", {}))
    tab.recalculate()

    assert f"at level {elsewhere}," in tab.summary.text(), (
        f"the summary does not name the level the figures beside it were "
        f"computed at: {tab.summary.text()!r}")
    assert f"at level {from_the_slider}," not in tab.summary.text(), (
        f"the summary names the slider's level, not the build's: "
        f"{tab.summary.text()!r}")


#: The sentence `UI_SPEC.md` AK-64 puts after the attack-rating definition,
#: verbatim, with the one word AK-88 settled: the tile heads a catalyst
#: `Spell power`, so the sentence says `spell power` too. Written out here
#: rather than imported from the tab, or the case would agree with whatever
#: the tab happens to say.
CATALYST_SENTENCE = ("Staves and seals show the spell power the game "
                     "displays for them instead of an attack rating.")


def test_the_summary_defines_both_figures_the_grid_can_show(planner,
                                                            game_data, hero):
    """QA-121: the grid shows two quantities, the sentence knew one.

    Since T-046 a staff or a seal is headed by its spell power, and a search
    for a staff's name fills the grid with cards whose figure the first
    sentence does not describe -- the state DR-008's screenshot was taken in.
    AK-64 answers it with a sentence that stands whatever the search shows,
    so both halves are checked: with the whole arsenal on screen, and with a
    grid holding nothing but catalysts.
    """
    prepare(planner, game_data, hero, empty_slots())
    tab = planner.weapons_tab

    assert CATALYST_SENTENCE in tab.summary.text(), (
        f"the summary does not define the figure a catalyst card shows: "
        f"{tab.summary.text()!r}")

    catalyst = cases.weapon_by_id(
        game_data, cases.first_of_family(game_data, "Glintstone Staff"))
    tab.search.setText(f'"{catalyst["name"]}"')
    tab.recalculate()

    drawn = tab.scroll.widget().findChildren(arsenaltab.Tile)
    assert drawn, "this search drew no card, so the grid shows nothing"
    for tile in drawn:
        weapon = next(w for w in game_data["weapons"]
                      if w["name"] == tile_name(tile))
        assert model.weapon_class(weapon) == "catalyst", (
            f"{tile_name(tile)!r} is not a catalyst, so this grid is not the "
            f"catalyst-only case QA-121 is about")

    assert CATALYST_SENTENCE in tab.summary.text(), (
        f"with only catalysts on screen the summary still explains only the "
        f"attack rating: {tab.summary.text()!r}")
