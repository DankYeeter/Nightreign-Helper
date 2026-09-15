"""T-261: both hands of one armament, `weapons.rate`'s shared work done once.

`weapons._rate_pair` replaced the two independent `weapons.rate` calls
`damage._rate` and `damage.rank_candidates` used to make for every
two-handable armament -- one via `weapons.rank`/the old `damage._scaled`, one
via the old `damage._other_hand` -- with one call that shares the raw
`base`/`bonus` arithmetic between both hands instead of running it twice
(T-260 performance-tuner report, section 5: profiled at 3529 `weapons.rate`
calls for 1792 `rank_candidates` candidates, ~29 % of that function's time).

Two claims, two tests:

* `_rate_pair` is bit for bit what two independent `weapons.rate` calls
  produce -- over the whole shipped dataset, not just the cases
  `tests/test_weapon_damage_golden.py` freezes (T-260 section 5, spec item
  4).
* the doubling is actually gone: `rank_candidates` reaches the shared
  arithmetic exactly once per candidate, never twice.
"""

from __future__ import annotations

from nrplanner import damage, model, weapons

from tests import weapon_damage_cases as cases

#: The same reduced grid `scripts/bracketing_residue.py` uses for a
#: last-bit measurement over the whole dataset, held smaller here because
#: this runs in the suite rather than by hand: the floor and the top of the
#: level range and of the tier range, every Nightfarer. `_rate_shared`
#: branches on neither level nor tier beyond the reinforce-table lookup both
#: tiers here already walk, so a fuller cross of levels would not reach a
#: case this grid misses.
LEVELS = (1, 15)
TIERS = (weapons.MIN_UPGRADE, weapons.MAX_UPGRADE)


def _hex(rating: weapons.WeaponRating) -> tuple:
    """A `WeaponRating`'s figures, as hex floats -- exact, unlike `==`."""
    return (
        {k: v.hex() for k, v in rating.base.items()},
        {k: v.hex() for k, v in rating.scaled.items()},
        None if rating.catalyst_scaling is None
        else rating.catalyst_scaling.hex(),
    )


def test_rate_pair_matches_two_independent_rate_calls(game_data):
    curves = game_data.get("curves", {})
    checked = 0
    for hero in game_data["heroes"]:
        nightfarer = str(hero.get("name", ""))
        for level in LEVELS:
            attributes = model.compute(hero, level, [], curves).attributes
            for upgrade in TIERS:
                for weapon in game_data["weapons"]:
                    one_handed, two_handed = weapons._rate_pair(
                        weapon, attributes, game_data, upgrade, nightfarer)
                    want_one = weapons.rate(weapon, attributes, game_data,
                                            upgrade, nightfarer)
                    assert _hex(one_handed) == _hex(want_one), \
                        weapon.get("name")

                    if weapons.can_two_hand(weapon):
                        want_two = weapons.rate(
                            weapon, attributes, game_data, upgrade,
                            nightfarer, two_handed=True)
                        assert two_handed is not None, weapon.get("name")
                        assert _hex(two_handed) == _hex(want_two), \
                            weapon.get("name")
                    else:
                        assert two_handed is None, weapon.get("name")
                    checked += 1

    assert checked == (len(game_data["heroes"]) * len(LEVELS) * len(TIERS)
                       * len(game_data["weapons"]))


def test_rank_candidates_reaches_the_shared_arithmetic_once_per_candidate(
        monkeypatch, game_data):
    """The doubling T-260 profiled is gone: one `_rate_shared` per candidate.

    Wraps `weapons._rate_shared` rather than `weapons.rate`: since T-261
    `rank_candidates` no longer calls `weapons.rate`/`weapons.rank` at all --
    both hands come from `weapons._rate_pair`, which reaches `_rate_shared`
    exactly once regardless of whether the armament can be two-handed.
    `_rate_shared` is the function that used to run twice per two-handable
    candidate (the base/bonus loop T-260 profiled at ~29 % of this call), so
    it is what a call counter has to watch to say the fix held.
    """
    hero = cases.hero_by_name(game_data, "Wylder")
    build = model.compute(hero, 15, [], game_data.get("curves", {}))

    calls: list[None] = []
    original = weapons._rate_shared

    def counting(*args, **kwargs):
        calls.append(None)
        return original(*args, **kwargs)

    monkeypatch.setattr(weapons, "_rate_shared", counting)

    ranked = damage.rank_candidates(build, weapons.MAX_UPGRADE, game_data)

    assert len(calls) == len(ranked)
