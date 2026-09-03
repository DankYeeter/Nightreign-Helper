"""A buff the game restricts in prose only, and the list that has to carry it.

`ARCHITECTURE.md` AD-019 step W6, QA-018, `nrplanner/model.py`
`MOVE_SCOPED_EFFECT_IDS`.

`model.attack_scope` finds a restricted attack buff by reading
`magicSubCategoryChange1/2/3`, which is the one field in the data that says
"this covers one kind of attack". Four effect families say it in their
description text and in no field at all, and until W6 they were multiplied
into every swing:

    Improved Thrusting Counterattack    "Enhances counterattacks unique to
                                         thrusting weapons"
    Improved Sorceries                  "Raises potency of sorceries"
    Improved Incantations               "Raises potency of incantations"
    Improved Sorceries & Incantations   both of the above

**The measurement.** The user checked the first of them in play on
2026-09-03: Wylder holding Wylder's Greatsword, one relic carrying the +20%,
the attack rating read off the game's own menu with and without it. It did not
move. Verbatim: "counterattack ist nur bei konter. nicht global." That is what
decided QA-018 -- 203.4 was the right figure and 244.1 carried a multiplier
that reaches a move this armament was not making.

**The three spell families are inferred and not measured**, and the tests
below treat them the same as the measured one on purpose: they make the same
claim in the same words. If one of them is ever measured and turns out to be
flat, `test_every_effect_of_the_four_families_is_listed` is what has to be
told about it -- it is the place that says which effects are held to this.

**What these tests do not claim.** Nothing here says the list is complete for
any dataset but the one in front of it. A game patch that adds a fifth family
adds effects nothing here knows, and they will be counted flat until someone
adds them. What the sweep below does hold is the narrower and checkable half:
no member of these four families, in *this* dataset, is missing from the list.
"""

from __future__ import annotations

import pytest

from nrplanner import damage, model, weaponslots

from tests import weapon_damage_cases as cases

LEVEL = 15
TIER = 1

#: The armament QA-018 was measured on. Common tier, so `TIER` is where it
#: already sits and no reinforcement enters the comparison.
ARMAMENT = "Wylder's Greatsword"

#: The four names the list is drawn from. Held here as text because that is
#: what the game states and what the user read off the relic; the ids they
#: resolve to are the production constant under test and are not repeated.
FAMILY_NAMES = (
    "Improved Thrusting Counterattack",
    "Improved Sorceries",
    "Improved Incantations",
    "Improved Sorceries & Incantations",
)

#: A flat buff of the same shape, and the control for the whole file: it
#: carries `physicsAttackRate`, carries no scope field, and carries
#: `magParamChange` exactly as three of the four families do. Nothing in the
#: params tells it apart from them -- only its text, which names no move. It
#: has to go on lifting the armament, or the exclusion is too wide.
FLAT_BUFF_NAME = "Improved Physical Attack Power"


def named_effects(game_data: dict, name: str) -> list[dict]:
    """Every effect in the dataset carrying this name, lowest id first.

    Names repeat -- five effects are called "Improved Sorceries" and differ
    only in how much they give -- so this hands back all of them and the
    caller says what it wants with them.
    """
    wanted = " ".join(name.split())
    found = [effect for effect in game_data["effects"].values()
             if " ".join(str(effect.get("name", "")).split()) == wanted]
    if not found:
        raise LookupError(
            f"no effect called {name!r} in this dataset; the four families "
            f"this file is about are named in its docstring")
    return sorted(found, key=lambda effect: int(effect["id"]))


def family_members(game_data: dict) -> list[dict]:
    """Every effect of the four families, including the +1 and +2 steps.

    The game numbers the stronger version of a relic effect by appending
    " +1" / " +2" to the same name, so the sweep asks for both spellings
    rather than for the bare name alone. Reading it off the name is the point:
    the ids are what is under test and cannot also be the query.
    """
    out = []
    for effect in game_data["effects"].values():
        name = " ".join(str(effect.get("name", "")).split())
        for family in FAMILY_NAMES:
            if name == family or name.startswith(f"{family} +"):
                out.append(effect)
                break
    return sorted(out, key=lambda effect: int(effect["id"]))


@pytest.fixture(scope="module")
def hero(game_data):
    """Wylder, the Nightfarer the measurement was made on."""
    return cases.hero_by_name(game_data, "Wylder")


@pytest.fixture(scope="module")
def greatsword(game_data):
    """Wylder's Greatsword. Thrusting counterattacks are not what it does."""
    found = [weapon for weapon in game_data["weapons"]
             if weapon["name"] == ARMAMENT]
    assert len(found) == 1, f"expected one {ARMAMENT!r}, found {len(found)}"
    return found[0]


def rating_with(game_data, hero, weapon, effects) -> damage.AttackRating:
    """The armament's attack rating for a build carrying exactly these."""
    build = model.compute(hero, LEVEL, list(effects),
                          game_data.get("curves", {}),
                          weapon=weapon, weapons_held=[weapon])
    return damage.attack_rating(weapon, TIER, build, game_data)


def test_no_effect_of_the_four_families_moves_an_attack_rating(
        game_data, hero, greatsword):
    """The claim QA-018 was decided on, over all of them, one at a time.

    Bit-for-bit against the same armament with no relic at all, not merely
    close to it: what these effects contribute to an ordinary swing is
    nothing, and "nothing" has an exact representation.

    Each one is also checked to be worth something in the first place -- an
    effect whose `physicsAttackRate` were 1.0 would pass this test on a tree
    that had never heard of the list.
    """
    bare = rating_with(game_data, hero, greatsword, [])
    members = family_members(game_data)
    assert members, "this dataset holds none of the four families"

    for effect in members:
        modifiers = effect.get("modifiers") or {}
        given = [modifiers[field] for field in model.ELEMENT_ATTACK_RATES
                 if field in modifiers]
        assert given and max(given) > 1.0, (
            f"{effect['name']!r} ({effect['id']}) raises no attack rate at "
            f"all, so it cannot show whether the exclusion works")

        rated = rating_with(game_data, hero, greatsword, [effect])
        assert rated.final_total == bare.final_total, (
            f"{effect['name']!r} ({effect['id']}) moved the attack rating of "
            f"{ARMAMENT} from {bare.final_total} to {rated.final_total}. It "
            f"reaches one kind of attack, and an attack rating is the "
            f"ordinary swing (QA-018)")
        assert rated.final_total == rated.scaled_total, (
            f"{effect['name']!r} ({effect['id']}) left a multiplier on the "
            f"layer-two figure")


def test_every_effect_of_the_four_families_is_listed(game_data):
    """The list and the dataset say the same thing, in both directions.

    A sweep by name against a constant of ids. It catches the two ways the
    constant can rot: a dataset that grows another "Improved Sorceries +3"
    nobody added, and an id in the list that no longer names one of these
    families. On the dataset this was written against the two sides are 22
    ids; the count is not asserted, because the equality already fixes it and
    a number written here would have to be maintained beside it.
    """
    from_data = {int(effect["id"]) for effect in family_members(game_data)}
    listed = set(model.MOVE_SCOPED_EFFECT_IDS)

    assert from_data - listed == set(), (
        "these effects belong to the four families and are not in "
        "model.MOVE_SCOPED_EFFECT_IDS, so they are being multiplied into "
        "every swing: "
        + ", ".join(sorted(str(i) for i in from_data - listed)))
    assert listed - from_data == set(), (
        "these ids are in model.MOVE_SCOPED_EFFECT_IDS and name no effect of "
        "the four families in this dataset: "
        + ", ".join(sorted(str(i) for i in listed - from_data)))


def test_a_flat_buff_the_params_cannot_tell_apart_still_lifts_the_rating(
        game_data, hero, greatsword):
    """The control. An exclusion this file cannot bound is worth nothing.

    `Improved Physical Attack Power` is indistinguishable from the four
    families by any modifier: same `physicsAttackRate`, no scope field, the
    same `magParamChange`. Only its text differs, and its text names no move.
    It must go on lifting the armament by exactly its own factor.
    """
    bare = rating_with(game_data, hero, greatsword, [])
    effect = named_effects(game_data, FLAT_BUFF_NAME)[0]
    factor = (effect["modifiers"] or {})["physicsAttackRate"]
    assert factor > 1.0, f"{FLAT_BUFF_NAME!r} gives nothing in this dataset"

    rated = rating_with(game_data, hero, greatsword, [effect])

    assert rated.final_total > bare.final_total, (
        f"{FLAT_BUFF_NAME!r} moved nothing, so the exclusion has reached "
        f"past the four families it is meant to cover")
    assert rated.final_total == pytest.approx(bare.final_total * factor)


def test_a_text_scoped_buff_is_kept_out_of_the_rating_and_not_out_of_sight(
        game_data, hero, greatsword):
    """Excluded from the attack rating, still shown, still named.

    The player equipped the relic and it does something; what it does is not
    an attack rating. So it keeps its own line under its own name, carrying
    its own number -- the same treatment a buff scoped by an actual param
    field gets -- rather than disappearing from the sheet.
    """
    effect = named_effects(game_data, "Improved Thrusting Counterattack")[0]
    build = model.compute(hero, LEVEL, [effect],
                          game_data.get("curves", {}),
                          weapon=greatsword, weapons_held=[greatsword])

    key = f"{model.SCOPED_PREFIX}{effect['name'].strip()}"
    assert key in build.rates, (
        f"the relic left no line at all: {sorted(build.rates)}")
    assert build.rates[key] == (effect["modifiers"] or {})["physicsAttackRate"]
    assert model.label_for(key) == effect["name"].strip()
    assert any(name == effect["name"].strip()
               for name, _ in build.sources.get(key, [])), (
        "the line names no source, so a click on it would explain nothing")

    for field_name in model.ELEMENT_ATTACK_RATES:
        assert field_name not in build.rates, (
            f"{field_name} is still in the flat pool, where it lifts every "
            f"swing")


def strongest(effects: list[dict]) -> dict:
    """The step of a family that gives the most, which is the relic held."""
    return max(effects, key=lambda effect:
               (effect["modifiers"] or {}).get("physicsAttackRate", 0.0))


def test_the_tab_and_the_panel_name_one_figure_for_the_measured_case(
        planner, game_data, hero, greatsword):
    """QA-018's own case, on both displays at once, after W6.

    Wylder, Wylder's Greatsword in slot 1 at Common, one relic carrying
    "Improved Thrusting Counterattack (+20%)", the arsenal tab's spinbox on
    the slot's own tier so that both displays are asking the same question.
    The tab read 203 and the panel 244, and neither was arrived at by a wrong
    sum: the panel's figure carried the +20% flat and the tab's carried no
    multipliers at all.

    Both halves are asserted, and the second is what makes the case sharp. An
    equality alone would also hold on a tree that applied the +20% on both
    sides -- so the agreed figure is then held against the figure the armament
    has with no relic at all, which is what the user read off the game.

    The two displays are read through the helpers that already own them:
    `drawn_tiles`/`tile_ar` render the arsenal tile,
    `test_weapon_tile_and_panel_agree.panel_total` picks the total out of the
    panel's markup. Copies of either would drift from the originals, and the
    originals are older than this case.
    """
    from tests.test_arsenal_tab_asks_the_facade import (
        drawn_tiles, empty_slots, prepare, tile_ar)
    from tests.test_weapon_tile_and_panel_agree import panel_total

    relic = strongest(named_effects(game_data,
                                    "Improved Thrusting Counterattack"))
    factor = (relic["modifiers"] or {})["physicsAttackRate"]

    slots = empty_slots()
    slots[0] = weaponslots.WeaponSlot(weapon=greatsword, tier=TIER)
    prepare(planner, game_data, hero, slots)
    planner.selected_effects = lambda: [relic]
    planner.recompute()

    tab = planner.weapons_tab
    tab.upgrade.setValue(TIER)

    tiles = drawn_tiles(tab, greatsword)
    assert tiles, f"the tab drew no tile for {ARMAMENT!r}"
    on_the_tab = {tile_ar(tile) for tile in tiles}
    assert len(on_the_tab) == 1, f"the tab drew two figures: {on_the_tab}"
    on_the_panel = f"{panel_total(planner):.0f}"

    assert on_the_tab == {on_the_panel}, (
        f"the arsenal tab says {on_the_tab} and the breakdown panel says "
        f"{on_the_panel} for {ARMAMENT!r} in one build at one tier. That is "
        f"QA-018")

    unbuffed = rating_with(game_data, hero, greatsword, []).final_total
    assert on_the_panel == f"{unbuffed:.0f}", (
        f"both displays agree on {on_the_panel}, and that is not the figure "
        f"{ARMAMENT!r} has without the relic ({unbuffed:.0f}). The +20% is "
        f"still being counted somewhere")
    assert f"{unbuffed:.0f}" != f"{unbuffed * factor:.0f}", (
        f"with and without the relic round to the same text on this "
        f"armament, so the case cannot tell them apart")
