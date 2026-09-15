"""`WeaponRating.scaled_per_type()` is now the only place the per-type sum is written.

`ARCHITECTURE.md` AD-019 step W1, AD-020 point 7. Until this accessor existed,
`base.get(d, 0) + scaled.get(d, 0)` stood in four places, so each display was
free to drift from the others one edit at a time -- QA-018, QA-055 and QA-056
are what that drift looked like from the outside.

A test that only restated the sum would be worth nothing: it would pass with a
copy of the line under test. So the claims below are the ones a caller relies
on and could not read off the expression -- which types appear, in which
order, and that no armament in the dataset loses a type on the way out.

There used to be a fourth case here, checking that `scaled_per_type()` summed
to the `total` field `WeaponRating` carried beside it -- the two were the same
addends bracketed differently, and the case was the differential check
assurance Z1 needed while both bracketings were live during the W1-W4
migration. `total` fell in W5 (AD-019, AD-024): there is now exactly one
summation of a damage type in the program, so there is nothing left for a
second one to disagree with, and the case would have had to be deleted anyway
to stop reading a field that no longer exists.
"""

from __future__ import annotations

from nrplanner import weapons


def a_rating(base: dict, scaled: dict) -> weapons.WeaponRating:
    """A rating with figures chosen by hand, no dataset in the way."""
    return weapons.WeaponRating(weapon={}, base=dict(base),
                                scaled=dict(scaled))


def test_each_type_is_its_base_plus_its_scaling():
    """Exactly, not approximately: these four numbers add up on paper."""
    rating = a_rating({"Physics": 100.0, "Fire": 20.0},
                      {"Physics": 25.0, "Fire": 5.0})

    assert rating.scaled_per_type() == {"Physics": 125.0, "Fire": 25.0}


def test_a_type_the_weapon_does_not_deal_is_absent_rather_than_zero():
    """`rate` records a type only where there is base damage to record.

    Reporting the other four as 0.0 would put four "Magic 0" rows on the
    breakdown panel and four dead lines on every arsenal tile, because both
    callers show whatever comes back.
    """
    rating = a_rating({"Physics": 90.0}, {"Physics": 10.0})

    assert rating.scaled_per_type() == {"Physics": 100.0}


def test_the_order_is_the_damage_type_order_not_the_insertion_order():
    """Two displays list one weapon alike, whoever filled the dicts.

    Both callers iterate the result straight into rows, so the order here is
    the order on screen.
    """
    rating = a_rating({"Dark": 30.0, "Physics": 60.0, "Magic": 45.0},
                      {"Dark": 3.0, "Physics": 6.0, "Magic": 4.5})

    assert list(rating.scaled_per_type()) == ["Physics", "Magic", "Dark"]


def test_every_type_the_rating_holds_comes_back(game_data):
    """No armament in the dataset loses a damage type on the way out."""
    attributes = {"Strength": 30, "Dexterity": 30, "Intelligence": 30,
                  "Faith": 30, "Arcane": 30}

    for weapon in game_data["weapons"]:
        rating = weapons.rate(weapon, attributes, game_data,
                              upgrade=weapons.MAX_UPGRADE)
        assert set(rating.scaled_per_type()) == set(rating.base), weapon["name"]
