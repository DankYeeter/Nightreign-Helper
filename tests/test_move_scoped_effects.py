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

from tests import tabtext
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
    assert any(entry.name == effect["name"].strip()
               for entry in build.sources.get(key, [])), (
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
    `drawn_tiles`/`tile_headline` render the arsenal tile,
    `test_weapon_tile_and_panel_agree.panel_total` picks the total out of the
    panel's markup. Copies of either would drift from the originals, and the
    originals are older than this case.
    """
    from tests.test_arsenal_tab_asks_the_facade import (
        drawn_tiles, empty_slots, prepare, tile_headline)
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
    expected = damage.candidate(greatsword, TIER, planner.current_build(),
                                game_data)
    # The one-handed figure in front of the `/ <n> 2H` twin (AK-286,
    # `damage.displayed_hands`, its markup taken off); `panel_total` reads
    # the same one off the panel, and the twin has its own guard in
    # `test_two_handed_display.py`.
    on_the_tab = {tabtext.unmarked(tile_headline(tile, expected))
                  .split("\u00a0")[0] for tile in tiles}
    assert len(on_the_tab) == 1, f"the tab drew two figures: {on_the_tab}"
    on_the_panel = f"{panel_total(planner):.0f}"

    assert on_the_tab == {on_the_panel}, (
        f"the arsenal tab says {on_the_tab} and the breakdown panel says "
        f"{on_the_panel} for {ARMAMENT!r} in one build at one tier. That is "
        f"QA-018")

    unbuffed = rating_with(game_data, hero, greatsword, []).final_total
    assert on_the_panel == str(damage.displayed(unbuffed)), (
        f"both displays agree on {on_the_panel}, and that is not the figure "
        f"{ARMAMENT!r} has without the relic "
        f"({damage.displayed(unbuffed)}). The +20% is "
        f"still being counted somewhere")
    assert (damage.displayed(unbuffed)
            != damage.displayed(unbuffed * factor)), (
        f"with and without the relic round to the same text on this "
        f"armament, so the case cannot tell them apart")


# -- the art each of these buffs belongs to (AD-046, assurance M2) --------
#
# `MOVE_SCOPED_EFFECT_IDS` above says which buffs stay out of an ordinary
# swing. `MOVE_SCOPED_ARTS` and `attack_arts_of` say which kind of attack
# each of them does reach, so that a player who asks about one kind gets the
# buffs that cover it. The sweep below holds the mapping against the dataset
# it was derived from, in the same shape as the sweep above: no number is
# written here that the data does not state.

#: The effects that belong to two arts at once in this dataset, by id --
#: 330900 carries scope 110 and 111 together, the other four are the
#: "Improved Sorceries & Incantations" family. They are the case the set
#: semantics of `attack_arts_of` exists for, so they are named rather than
#: counted.
IDS_IN_TWO_ARTS = frozenset({330900, 8330103, 8330104, 8851200, 8851250})


def arts_in_the_data(game_data: dict) -> dict[str, set[int]]:
    """Art key -> the ids of the effects covering it, over the whole data."""
    found: dict[str, set[int]] = {}
    for effect in game_data["effects"].values():
        for art in model.attack_arts_of(effect):
            found.setdefault(art, set()).add(int(effect["id"]))
    return found


#: `family:110` "Charged" is the one scope the dataset names as a school and
#: no spell of it belongs to: being charged is a property of a cast, not a
#: school a spell is in (measured T-324c). Six buffs cover it and none of
#: them can be asked about, which is the director's decision of 2026-09-20
#: rather than an oversight -- the spell rows rank the spell the equipment
#: throws, and there is no spell to find under this one.
NOT_A_SCHOOL = f"{model.ART_FAMILY_PREFIX}110"


def test_every_art_offered_is_one_some_relic_can_actually_move(game_data):
    """The chooser and the data say the same thing, in both directions.

    An art with no effect behind it is a line the player can pick and that
    can never change a figure; an effect whose art is not offered is a buff
    nobody can ask about. Both are caught by comparing the two sides rather
    than by a count written down here -- with the one named exception above,
    which is stated rather than counted, so that a second one arriving
    quietly fails this case.
    """
    offered = model.attack_arts(game_data)
    covered = arts_in_the_data(game_data)

    assert set(offered) == set(covered) - {NOT_A_SCHOOL}, (
        f"offered and not covered: {sorted(set(offered) - set(covered))}; "
        f"covered and not offered: "
        f"{sorted(set(covered) - set(offered) - {NOT_A_SCHOOL})}")
    assert NOT_A_SCHOOL in covered, (
        "the exception above is about a scope this dataset no longer "
        "carries, so it is a sentence nobody can check any more")
    assert all(label.strip() for label in offered.values()), (
        f"an art is offered without a name: {offered}")


def test_a_school_no_spell_belongs_to_is_not_offered(game_data):
    """The rule behind the exception, read off the data rather than listed.

    `spell_families` names 21 schools and the spells of this dataset are in
    20 of them. The 21st is `Charged`, and a chooser entry for it would ask
    about a spell the program can never find (director's decision
    2026-09-20). The rule is written as "no spell is in it" and not as the
    number 110, so a patch that gives Charged a spell -- or empties another
    school -- moves the offer by itself.
    """
    offered = model.attack_arts(game_data)
    in_a_school = {str(spell.get("family") or "")
                   for spell in game_data["spells"]}

    empty = {f"{model.ART_FAMILY_PREFIX}{value}": label
             for value, label in model.spell_family_names(game_data).items()
             if label not in in_a_school}

    assert set(empty.values()) == {"Charged"}, (
        f"another school lost its spells: {empty}")
    assert not set(empty) & set(offered), (
        f"a school no spell is in is being offered: {empty}")


def test_a_scope_the_data_does_not_name_stays_without_an_art(game_data):
    """A movement scope is no art, and neither is a scope a patch adds.

    Every `family:` key has to resolve to a school the dataset names in
    `spell_families`; the twelve movement scopes (jump, guard counter and
    their kin) name none and keep their `scoped:` line and nothing else
    (AD-046 point 5). This is what keeps the chooser free of invented
    labels -- A7.
    """
    named = model.spell_family_names(game_data)
    for art in arts_in_the_data(game_data):
        if not art.startswith(model.ART_FAMILY_PREFIX):
            assert art in model.ART_LABELS, (
                f"{art!r} is an art key the program has no wording for")
            continue
        value = int(art[len(model.ART_FAMILY_PREFIX):])
        assert value in named, (
            f"{art!r} was derived from scope {value}, which "
            f"`spell_families` does not name")


def test_an_effect_in_two_arts_is_named_and_counts_once_in_each(game_data):
    """Set semantics, not first-hit: the ids that need it are held here.

    330900 carries 112's sibling 111 beside scope 110. Reading the first
    field alone would drop it out of `skill`, which its own name states, and
    reading the fields as a list would multiply 112 and 111 into the same
    figure twice (AD-046 points 2 and 3).
    """
    covered = arts_in_the_data(game_data)
    counts: dict[int, int] = {}
    for ids in covered.values():
        for effect_id in ids:
            counts[effect_id] = counts.get(effect_id, 0) + 1

    assert {i for i, n in counts.items() if n > 1} == IDS_IN_TWO_ARTS
    assert all(n <= 2 for n in counts.values()), (
        f"an effect reached three arts: "
        f"{sorted(i for i, n in counts.items() if n > 2)}")

    both = model.attack_arts_of(game_data["effects"]["330900"])
    assert both == frozenset({model.SKILL_ART,
                              f"{model.ART_FAMILY_PREFIX}110"}), both


def test_one_scalar_per_art_holds_while_no_effect_splits_its_rates(game_data):
    """The ceiling under `Build.art_rates` being a number and not a bucket.

    `art_rates` keeps one factor per art because no effect of this dataset
    gives its five element rates different values -- a five-field bucket
    would carry the same number in every cell. The day a patch ships one that
    does, this fails, and the scalar becomes a bucket (AD-046 point 6).
    """
    split = []
    for effect in game_data["effects"].values():
        if not model.attack_arts_of(effect):
            continue
        rates = {float(v) for f, v in (effect.get("modifiers") or {}).items()
                 if f in model.ELEMENT_ATTACK_RATES
                 and isinstance(v, (int, float))}
        if len(rates) > 1:
            split.append((int(effect["id"]), sorted(rates)))

    assert split == [], (
        f"these effects give their element rates different values, so one "
        f"number per art no longer says what they do: {split}")
