"""The tile and the panel under it name the same number.

`ARCHITECTURE.md` Nachtrag III, checkpoint 19 -- the test QA-018 never had.

Until AD-019 step W3 the weapon tile rated its armament for itself, on the
raised attributes and without the attack multipliers, while the breakdown
panel below it asked `damage.attack_rating` and got both. Same armament, same
slot, same tier, two totals on screen at once and nothing to tell them apart
(QA-056: tile 323, panel 321.4, arsenal tab 204.2). Nothing here checks the
arithmetic -- the golden file does that. What is checked here is that the two
displays ask **one** question.

Read off the widgets, not off the objects behind them: a player compares the
two rendered figures, and rounding is part of what he compares. The regular
expressions are deliberately anchored on the markup the two displays actually
emit, so a change in how either is written shows up as a failed match rather
than as a silently skipped assertion.

The arsenal tab is **not** in here. It ranks at a chosen target tier and is
allowed to differ (AD-020, point 1); it moves onto the facade in W4 and
QA-055 stays open until it does.
"""

from __future__ import annotations

import re

import pytest

from nrplanner import model, weaponslots, weapons

from tests import weapon_damage_cases as cases

LEVEL = 15

# `weaponslots.WeaponTile` writes "<b style='...'>323</b> AR".
TILE_AR = re.compile(r">(-?\d+)</b> AR")
# The panel's total row: the bold "Total", the grey before-figure, the change
# link, and last the accented figure this test is about.
PANEL_TOTAL = re.compile(r"<b>Total</b>.*?<b style='color:[^']*'>(-?\d+)</b>")


def tile_ar(tile) -> int:
    match = TILE_AR.search(tile.detail.text())
    assert match, f"no AR figure in the tile text: {tile.detail.text()!r}"
    return int(match.group(1))


def panel_total(planner) -> int:
    match = PANEL_TOTAL.search(planner.ar_label.text())
    assert match, f"no total in the panel: {planner.ar_label.text()!r}"
    return int(match.group(1))


@pytest.fixture(scope="module")
def hero(game_data):
    """Wylder, the Nightfarer QA measured the divergence on."""
    return cases.hero_by_name(game_data, "Wylder")


@pytest.fixture(scope="module")
def moving_effects(game_data, hero):
    """Effects that move the multipliers and the attributes at once.

    Both halves are needed for this test to have teeth. An attribute bonus
    alone leaves the old tile formula and the new one agreeing, because the
    old tile already stood on the raised attributes; it is the multiplier
    layer that the tile never saw. Chosen by asking `model.compute` what each
    effect does, never by an id written down here.
    """
    ids = (cases.effects_raising_rate(game_data, hero, "physicsAttackRate", 2)
           + cases.effects_raising_attribute(game_data, hero, "Strength", 2))
    return [cases.effect_by_id(game_data, i) for i in ids]


def armaments(game_data, hero) -> list[tuple[int, int]]:
    """(armament id, tier) for the tiles this test fills.

    The Nightfarer's own starting armament, an armament of a class a scoped
    buff can reach, and a third, heavy-looking one, so the grid has enough
    distinct figures for `test_which_tile_is_ringed_moves_no_tile_s_figure`
    to tell tiles apart by. (This third slot used to be picked to exercise a
    "requirements unmet" tile state; T-034 removed that state after QA-061
    measured the requirement it depended on is always met on real data.)
    """
    return [
        (hero["starting_weapon"], 3),
        (cases.first_of_family(game_data, "Bow"), 2),
        (cases.heaviest_of_family(game_data, "Colossal Sword"), 4),
    ]


def fill(planner, game_data, hero, pairs) -> None:
    slots = [weaponslots.WeaponSlot()
             for _ in range(weaponslots.SLOT_COUNT)]
    for index, (weapon_id, tier) in enumerate(pairs):
        slots[index] = weaponslots.WeaponSlot(
            weapon=cases.weapon_by_id(game_data, weapon_id), tier=tier)
    planner.hero_index = game_data["heroes"].index(hero)
    planner.weapon_slots = slots
    planner.declared = {}


def refresh(planner, game_data, hero, effects, active: int):
    """Draw the grid with `active` selected, and hand back the build used."""
    planner.active_weapon = active
    planner.selected_effects = lambda: effects
    slots = planner.weapon_slots
    build = model.compute(
        hero, LEVEL, effects, game_data.get("curves", {}),
        weapon=slots[active].weapon,
        weapons_held=[s.weapon for s in slots if s.filled],
    )
    planner._refresh_weapon_damage(build)
    return build


def test_every_filled_tile_names_the_panel_s_own_total(
        planner, game_data, hero, moving_effects):
    """For each filled slot: the tile figure is the panel figure.

    This is the whole of checkpoint 19. It ran red before W3 for any build
    carrying an attack multiplier, which is what the guard below insists this
    build still is -- otherwise the two formulas coincide and a green result
    would mean nothing.
    """
    pairs = armaments(game_data, hero)
    fill(planner, game_data, hero, pairs)

    had_teeth = False
    for index, (_weapon_id, tier) in enumerate(pairs):
        build = refresh(planner, game_data, hero, moving_effects, index)
        slot = planner.weapon_slots[index]

        assert tile_ar(planner.weapon_tiles[index]) == panel_total(planner), (
            f"slot {index + 1} shows one figure on its tile and another in "
            f"the panel below it")

        # The formula the tile used before W3: the raised attributes, no
        # multipliers. Where it disagrees with what is now shown, this case
        # would have failed before the change -- which is what makes the
        # assertion above evidence rather than decoration.
        # `WeaponRating.total` fell in W5 (AD-019); the per-type sum it used
        # to carry is the same figure, read off `scaled_per_type()` instead.
        before_w3 = sum(weapons.rate(slot.weapon, build.attributes,
                                     game_data, tier).scaled_per_type().values())
        if round(before_w3) != panel_total(planner):
            had_teeth = True

    assert had_teeth, (
        "no slot in this case distinguishes the pre-W3 tile formula from the "
        "one under test, so the assertions above cannot fail and prove "
        "nothing. Pick effects that move an attack multiplier.")


def test_which_tile_is_ringed_moves_no_tile_s_figure(
        planner, game_data, hero, moving_effects):
    """Selecting a tile is decoration; it must not change what another says.

    The test above makes each tile active in turn and reads it only in that
    state. **No test saw a tile while a different one was active**, and that
    hole was not theoretical: the mutation "only the active tile gets the
    finished value" moved 36 958 tile figures in 12 551 of 25 102 cases and
    left 237 of 237 tests green (QA-073 a). For the player it is QA-056 in
    new clothes -- five tiles showing the figure from before the multipliers,
    and a click making the number jump. The mutation is kept, by name, in
    `scripts/differential/mutate.py` as `active-tile-only`, so this claim can
    be re-run rather than believed.

    **The build is held fixed across the draws, for simplicity, not
    necessity.** An earlier version of this docstring justified that by
    saying choosing another slot changes the build because "the weapon gates
    follow the active armament" -- that does not match the code and was
    corrected 2026-09-03 (QA-082). Weapon-type gates are read off
    `weapons_held`, every filled slot at once, not the active one
    (`model.py:739-742`); the starting-armament pairing follows the **slot
    index** an armament sits in, not which slot is ringed (`damage.equipped`,
    `damage.py:376-391`); class-scoped rates key off the class of the
    armament being rated, not the active one (`damage.py:326`). None of the
    three hinges on which tile is active, and the `qa-engineer` measured it
    directly: 0 of 120 grids show a dependency, rounded and unrounded alike
    (2026-09-03). So "a tile figure never depends on the active slot" is, in
    fact, a true and broader assertion this test could make. It stays with
    the narrower one below because that is all the fix this test guards
    needed -- not because the broader one would be wrong.
    """
    pairs = armaments(game_data, hero)
    fill(planner, game_data, hero, pairs)
    build = refresh(planner, game_data, hero, moving_effects, 0)
    with_first_ringed = [tile.detail.text() for tile in planner.weapon_tiles]

    figures = [tile_ar(planner.weapon_tiles[index])
               for index in range(len(pairs))]
    assert len(figures) >= 3 and len(set(figures)) > 1, (
        "this case has fewer than three tiles carrying a figure, or they all "
        "carry the same one, so comparing the draws proves nothing")

    for active in range(1, weaponslots.SLOT_COUNT):
        planner.active_weapon = active
        planner._refresh_weapon_damage(build)

        assert [tile.detail.text() for tile in planner.weapon_tiles] \
            == with_first_ringed, (
                f"ringing slot {active + 1} changed what the other tiles say")


def test_the_starting_armament_penalty_reaches_the_tile_too(
        planner, game_data, hero):
    """The x0.85 pairing is on the tile now, not only in the panel.

    The penalty follows slot 1 **and** the Nightfarer's own armament, so the
    same weapon moved to slot 2 loses it (verified in play 2026-08-22). Before
    W3 the tile could not show either state: it never applied a multiplier.
    """
    frost = cases.effects_raising_rate(
        game_data, hero, "physicsAttackPowerRate", 1)
    effects = [cases.effect_by_id(game_data, i) for i in frost]
    own = hero["starting_weapon"]

    fill(planner, game_data, hero, [(own, 3)])
    refresh(planner, game_data, hero, effects, 0)
    penalised = tile_ar(planner.weapon_tiles[0])
    assert penalised == panel_total(planner)

    # The same armament, the same tier, one slot to the right.
    fill(planner, game_data, hero, [(own, 3), (own, 3)])
    refresh(planner, game_data, hero, effects, 1)
    spared = tile_ar(planner.weapon_tiles[1])
    assert spared == panel_total(planner)

    assert penalised < spared, (
        "the starting-armament penalty is meant to reach slot 1 alone, so the "
        "tile in slot 2 must show the larger figure")
