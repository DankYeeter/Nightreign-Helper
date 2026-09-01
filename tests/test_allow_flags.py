"""The allow flags may still speak about the base eight Nightfarers only.

Background, because this test is a standing condition rather than a plain
assertion. AttachEffectParam carries one allow* flag per Nightfarer, and the
param predates the expansion: there is no flag for Scholar or Undertaker. The
program therefore reads an allow list that does not name them as *silence*,
not as exclusion, and lets the 38 restricted effects count on the DLC pair
(QA-006). The files do not settle whether that is right; the user decided on
2026-09-01 that it stands as it is.

**This test is the condition attached to that decision.** The moment a game
patch adds allow flags for Scholar or Undertaker, the assumption behind
"works" is disproved -- the param would then be speaking about them, and its
silence would no longer be silence. That is when the decision has to be taken
again, by the user, not quietly by whoever is reading the diff. So the test
fails loudly instead of the numbers drifting.

It is not a test of the reading being correct. It cannot be: the data does
not decide it.
"""

from __future__ import annotations

from nrdata import extract
from nrplanner import effecttext

# The two the expansion added, and the two the param has no room for.
DLC_NIGHTFARERS = ("Scholar", "Undertaker")


def test_the_allow_fields_and_the_hero_set_are_the_same_eight():
    """The extractor's field list and the model's set cannot drift apart.

    They are written down twice -- once as param field names, once as
    Nightfarer names -- and the second is only correct while it is derived
    from the first.
    """
    from_fields = {name[len("allow"):] for name in extract.ALLOW_FIELDS}

    assert from_fields == set(effecttext.ALLOW_FLAG_HEROES)
    assert len(effecttext.ALLOW_FLAG_HEROES) == 8


def test_allow_flags_still_name_exactly_the_base_eight(game_data):
    """No effect in the installed game names a DLC Nightfarer in its allow list.

    If this fails, the game has been patched and QA-006 is open again.
    """
    named = {hero for effect in game_data["effects"].values()
             for hero in (effect.get("allowed_heroes") or [])}

    assert named <= set(effecttext.ALLOW_FLAG_HEROES), (
        "the game data now carries allow flags this program does not know "
        f"about: {sorted(named - set(effecttext.ALLOW_FLAG_HEROES))}"
    )
    assert not named & set(DLC_NIGHTFARERS), (
        "the allow flags now speak about the DLC Nightfarers. The decision "
        "of 2026-09-01 -- restricted effects work on Scholar and Undertaker "
        "-- rested on the param being silent about them, and it no longer "
        "is. QA-006 has to be decided again."
    )


def test_the_dlc_nightfarers_are_in_the_data_at_all(game_data):
    """Otherwise the test above would pass on a game without the expansion
    and prove nothing."""
    heroes = {hero["name"] for hero in game_data["heroes"]}

    assert set(DLC_NIGHTFARERS) <= heroes, (
        "this installation has no DLC Nightfarers, so the guard above cannot "
        "say anything about them"
    )
