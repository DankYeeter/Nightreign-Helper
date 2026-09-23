"""The three readings A26 rests on arrive, and they are the right ones.

AD-050, check point N2. A spell carries no damage figure of its own: `Magic`
names bullets, a bullet names an `AtkParam_Pc` row, and only that row holds a
number. Two things about that chain fail silently rather than loudly, which is
why they are pinned here rather than left to the shape of the data:

* **The paramdef is filed under another name.** `AtkParam.xml` describes
  `AtkParam_Pc` exactly, and `defs["AtkParam_Pc"]` does not exist. Without the
  alias `param.read` finds no def, reads no field, and every spell in the game
  comes back harmless -- a wrong number that looks like a right one.
* **`startMagicId` is declared by offset, not by name.** It sits at 1020, in
  the 48 bytes of each `SpEffectParam` row the shipped def does not describe.
  A patch that rearranges the row moves it silently, and the swap relics would
  then hand out whatever integer landed there.

So the anchors below are the figures themselves, measured against the
installation on 2026-09-20 (`data_version` 10350000, `ARCHITECTURE.md`
Themenbereich N): Glintstone Pebble 152 Magic, Beast Claw 362 Physics -- the
charged claw, which is what "strongest single hit" means (AD-050.3, OF-57) --
and 111 of 160 named spells carrying a figure at all.

A count is asserted exactly rather than as a floor because both directions are
news: fewer means the chain broke, more means it started counting hits that
are not the spell's. A game patch that adds or retires a spell moves it too,
and that is a game change to be read and re-measured, not a defect of this
file.

Nothing here holds game prose. The names are names, the rest are ids and
numbers (A-001).
"""

from __future__ import annotations

import pathlib

import pytest

from nrdata import extract, paramdef

#: Measured 2026-09-20 against data_version 10350000.
SPELLS_TODAY = 160
SPELLS_WITH_DAMAGE_TODAY = 111
SWAP_RELIC_EFFECTS_TODAY = 10

#: (spell id, damage type, base damage) -- the two anchors of N2.
ANCHORS = [
    (4000, "Magic", 152),      # Glintstone Pebble
    (6820, "Physics", 362),    # Beast Claw, charged
]

#: The Nightfarers whose left hand holds something at the start, and what.
#: The other seven start with an empty left hand and carry no field at all.
STARTING_LEFT_HANDS = {
    "Wylder": 30750000,        # Small Shield
    "Guardian": 32750000,      # Greatshield
    "Revenant": 34750000,      # Finger Seal
}

#: The one swap relic A26's own proof runs on: SpEffect row -> Magic row.
BEAST_CLAW_SWAP = (7370900, 6820)

DEFS_DIR = pathlib.Path(__file__).resolve().parents[1] / "vendor" / "Paramdex" / "NR" / "Defs"


def spells_by_id(game_data) -> dict[int, dict]:
    return {s["id"]: s for s in game_data["spells"]}


def test_the_paramdef_for_the_attack_table_is_filed_under_another_name():
    """Why `extract` looks up two keys for one table.

    Read off the vendored defs, which is where the fact lives -- no game
    needed. The day Paramdex ships an `AtkParam_Pc.xml`, this case says so
    and the alias can go.
    """
    defs = paramdef.load_all(DEFS_DIR)

    assert "AtkParam_Pc" not in defs
    assert defs["AtkParam"].row_size == 464, (
        "AtkParam.xml no longer describes a 464-byte row, which is the row "
        "length of AtkParam_Pc in the game data. param.read discards a def "
        "that is longer than the row, and every spell would read as dealing "
        "no damage at all.")


def test_the_spells_that_deal_damage_carry_their_figures(game_data):
    spells = game_data["spells"]
    with_damage = [s for s in spells if s.get("damage")]

    assert len(spells) == SPELLS_TODAY
    assert len(with_damage) == SPELLS_WITH_DAMAGE_TODAY, (
        f"{len(with_damage)} of {len(spells)} spells carry a damage figure, "
        f"where {SPELLS_WITH_DAMAGE_TODAY} of {SPELLS_TODAY} were measured. "
        f"Fewer means the chain Magic -> Bullet -> AtkParam_Pc stopped "
        f"resolving; more means it is counting rows that are not hits of the "
        f"spell.")


@pytest.mark.parametrize("spell_id, damage_type, figure", ANCHORS)
def test_an_anchor_spell_hits_for_the_figure_the_game_data_holds(
        game_data, spell_id, damage_type, figure):
    spell = spells_by_id(game_data)[spell_id]

    assert spell["damage"] == {damage_type: figure}
    assert spell["damage_atk"] > 0


def test_a_spell_that_damages_nothing_says_so_by_omission(game_data):
    """Heals, buffs and shields: no `damage`, and no `damage_atk` either.

    An empty mapping would read as "measured, and it is nothing"; the field
    is absent because there is nothing to measure.
    """
    quiet = [s for s in game_data["spells"] if not s.get("damage")]

    assert len(quiet) == SPELLS_TODAY - SPELLS_WITH_DAMAGE_TODAY
    assert not [s for s in quiet if "damage" in s or "damage_atk" in s]


def test_every_figure_is_a_whole_number_above_zero_of_a_known_type(game_data):
    """No zeroes, no NaN, no type the rest of the program cannot rate."""
    for spell in game_data["spells"]:
        for damage_type, figure in spell.get("damage", {}).items():
            assert damage_type in extract.DAMAGE_TYPES
            assert isinstance(figure, int) and figure > 0, (
                f"{spell['name']} reads {figure!r} for {damage_type}")


def test_the_swap_relics_name_their_spell_in_the_param(game_data):
    """N2. Ten rows, each one the spell the effect's own name states.

    The name is the cross-check and not the route (AD-050.4): the id is read
    from the param, and the text is only asked whether it agrees.
    """
    swaps = {int(key): effect for key, effect in game_data["effects"].items()
             if "start_magic_id" in effect}
    spells = spells_by_id(game_data)

    assert len(swaps) == SWAP_RELIC_EFFECTS_TODAY
    for effect_id, effect in swaps.items():
        magic_id = effect["start_magic_id"]
        assert magic_id in spells, (
            f"effect {effect_id} points at spell {magic_id}, which is not in "
            f"the dataset -- offset 1020 is being read over something else")
        said_in_english = " ".join(effect["name"].split()).lower()
        assert spells[magic_id]["name"].lower() in said_in_english, (
            f"effect {effect_id} carries spell id {magic_id} "
            f"({spells[magic_id]['name']}), and its own name names another "
            f"spell. The offset has moved.")


def test_the_relic_the_proof_runs_on_hands_over_beast_claw(game_data):
    effect_id, magic_id = BEAST_CLAW_SWAP
    effect = game_data["effects"][str(effect_id)]

    assert effect["start_magic_id"] == magic_id
    assert spells_by_id(game_data)[magic_id]["damage"] == {"Physics": 362}


def test_the_swapped_spell_is_not_a_number_among_the_modifiers(game_data):
    """It is a row id, and the build maths adds up quantities.

    Left in `modifiers` it would reach the panel as a stat with an absurd
    value, the way every engine reference did before ENGINE_FIELDS.
    """
    assert not [key for key, effect in game_data["effects"].items()
                if extract.START_MAGIC_FIELD in effect["modifiers"]]


def test_three_nightfarers_start_with_something_in_the_left_hand(game_data):
    holding = {hero["name"]: hero["starting_weapon_left"]
               for hero in game_data["heroes"]
               if "starting_weapon_left" in hero}

    assert holding == STARTING_LEFT_HANDS


def test_an_empty_left_hand_carries_no_field_at_all(game_data):
    """-1 is what `starting_weapon` says when no row names a weapon.

    The left hand is different: the row does name it, as empty. Absence says
    that; a -1 would make the two cases one.
    """
    empty_handed = [hero for hero in game_data["heroes"]
                    if hero["name"] not in STARTING_LEFT_HANDS]

    assert len(empty_handed) == len(game_data["heroes"]) - len(STARTING_LEFT_HANDS)
    assert not [hero for hero in empty_handed if "starting_weapon_left" in hero]
