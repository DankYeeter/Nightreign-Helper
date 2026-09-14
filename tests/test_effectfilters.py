"""The two marked effect sets: stored under two fixed keys, disjoint, heard.

AD-036.5 and AK-283: what the player marked `Don't include` or `Must include`
is written on the marking and read again at the next start -- a new
`EffectFilters` is that start, as far as the store can tell. The keys live
in the store `favourites` names, which is the one `NIGHTREIGN_SETTINGS_ORG`
moves (conftest), so nothing here reaches the player's own entries.
"""

from __future__ import annotations

import os

import pytest
from PySide6.QtCore import QSettings

from nrplanner import effectfilters, favourites


@pytest.fixture
def store():
    """The test store, with both keys emptied afterwards.

    Emptied by writing an empty value, never by `remove` (the rule
    `test_game_path_memory.py` holds for every `QSettings` key).
    """
    settings = QSettings(favourites.ORG, favourites.APP)
    yield settings
    for key in effectfilters.KEYS.values():
        settings.setValue(key, "")
    settings.sync()


def test_a_marking_is_there_again_at_the_next_start(store):
    filters = effectfilters.EffectFilters()
    filters.mark(8850550, effectfilters.EXCLUDED)
    filters.mark(7000100, effectfilters.REQUIRED)
    filters.mark(7000200, effectfilters.REQUIRED)

    restarted = effectfilters.EffectFilters()
    assert restarted.excluded == {8850550}
    assert restarted.required == {7000100, 7000200}


def test_the_two_keys_are_these_two_keys_in_the_redirected_store(store):
    """Proof by positive read-back (QA-237): the value stands under the fixed
    key, in the store the environment moved."""
    assert favourites.ORG == os.environ["NIGHTREIGN_SETTINGS_ORG"]
    effectfilters.EffectFilters().mark(42, effectfilters.EXCLUDED)
    assert store.value("advisor/excluded", "", type=str) == "42"
    assert store.value("advisor/required", "", type=str) == ""


def test_marking_the_other_way_moves_the_id_rather_than_refusing(store):
    """AK-276: never excluded and required at once; a second marking is a
    change of state, not an error (`SlotProblem.__post_init__` would refuse
    a pair that reached it)."""
    filters = effectfilters.EffectFilters()
    filters.mark(5, effectfilters.EXCLUDED)
    filters.mark(5, effectfilters.REQUIRED)
    assert (filters.excluded, filters.required) == (frozenset(), {5})
    filters.mark(5, effectfilters.EXCLUDED)
    assert (filters.excluded, filters.required) == ({5}, frozenset())
    filters.mark(5, None)
    assert (filters.excluded, filters.required) == (frozenset(), frozenset())
    assert effectfilters.EffectFilters().excluded == frozenset()


def test_changed_fires_once_per_marking_that_moved_something(store):
    filters = effectfilters.EffectFilters()
    heard = []
    filters.changed.connect(lambda: heard.append(True))
    filters.mark(5, effectfilters.EXCLUDED)
    filters.mark(5, effectfilters.EXCLUDED)
    filters.mark(6, None)
    assert len(heard) == 1


def test_a_kind_that_is_not_one_of_the_two_is_refused(store):
    with pytest.raises(ValueError):
        effectfilters.EffectFilters().mark(5, "held")


@pytest.mark.parametrize("damaged", ["", "abc", "1,,x, 2 ,", "3.5"])
def test_a_damaged_value_reads_as_whatever_ids_it_still_holds(store, damaged):
    store.setValue(effectfilters.KEYS[effectfilters.REQUIRED], damaged)
    ids = effectfilters.stored(effectfilters.REQUIRED)
    assert ids == {int(part) for part in damaged.split(",")
                   if part.strip().isdigit()}
