"""`effecttext.family_key`: the AD-039 rule, held at literals.

A family is the display name without the Nightfarer prefix, the tier at
the end, the armament type or affinity, and the `3+ ... Equipped` count
clause. The rule is over English names, so a renaming in the game reorders
families silently -- these literals are what would tell.
"""

from __future__ import annotations

import pytest

from nrplanner import effecttext

WEAPON_FAMILIES = {"1": "Dagger", "5": "Greatsword", "7": "Colossal Sword",
                   "9": "Torch", "13": "Bow", "21": "Sacred Seal"}


@pytest.mark.parametrize("name, family", [
    ("Improved Dagger Attack Power", "Improved Attack Power"),
    ("Improved Attack Power with 3+ Daggers Equipped", "Improved Attack Power"),
    ("Improved Greatsword Attack Power", "Improved Attack Power"),
    ("Fire Attack Power Up +2", "Attack Power Up"),
    ("Holy Attack Power Up", "Attack Power Up"),
    ("Physical Attack Up +2", "Physical Attack Up"),
    ("Improved Lightning Damage Negation +1", "Improved Damage Negation"),
    ("Dormant Power Helps Discover Sacred Seals", "Dormant Power Helps Discover"),
    ("HP Restoration upon Colossal Sword Attacks", "HP Restoration upon Attacks"),
    ("Dexterity +3", "Dexterity"),
    ("[Wylder] +1 additional Character Skill use",
     "+1 additional Character Skill use"),
    ("[Duchess] Improved Mind and Faith, Reduced Intelligence",
     "Improved Mind and Faith, Reduced Intelligence"),
    ("Improved Affinity Attack Power +2", "Improved Affinity Attack Power"),
    ("Torches Discovered", "Discovered"),
])
def test_the_family_is_the_name_without_prefix_tier_and_variant(name, family):
    assert effecttext.family_key({"name": name}, WEAPON_FAMILIES) == family


def test_a_name_that_is_nothing_but_a_variant_keeps_its_full_name():
    assert effecttext.family_key({"name": "Fire"}, WEAPON_FAMILIES) == "Fire"


def test_a_type_inside_a_word_is_not_a_variant():
    """`Bow` is a whole word: `Bowing` and `Elbow` keep theirs."""
    assert effecttext.family_key({"name": "Elbow Strike"},
                                 WEAPON_FAMILIES) == "Elbow Strike"


@pytest.mark.parametrize("damaged", [None, "Dagger", ["Dagger"],
                                     {"1": 1}, {"1": None}])
def test_a_damaged_weapon_families_field_makes_no_family_and_no_error(damaged):
    """SEC (T-292c point 1): a field that is missing, not a mapping or not
    strings strips no type; the affinities and the tier still go."""
    effect = {"name": "Fire Dagger Attack Power +1"}
    assert effecttext.family_key(effect, damaged) == "Dagger Attack Power"


def test_a_type_name_with_regex_characters_is_a_value():
    """`re.escape` on every name: a `.` in a type name matches a dot."""
    families = {"1": "Great.Sword"}
    assert effecttext.family_key({"name": "Improved Great.Sword Attack Power"},
                                 families) == "Improved Attack Power"
    assert effecttext.family_key({"name": "Improved GreatXSword Attack Power"},
                                 families) == "Improved GreatXSword Attack Power"


def test_the_two_dagger_effects_of_the_dataset_share_one_family(game_data):
    """AD-039, the user's own example: 7330000 and 7080000 are one family."""
    families = game_data["weapon_families"]
    keys = {effecttext.family_key(game_data["effects"][str(i)], families)
            for i in (7330000, 7080000)}
    assert keys == {"Improved Attack Power"}
