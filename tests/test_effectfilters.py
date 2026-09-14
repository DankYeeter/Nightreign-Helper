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
from nrplanner.advisor import types


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


def test_an_id_under_both_keys_is_required_and_no_longer_excluded(store):
    """QA-267/SEC-045: a store left with one id under both keys -- the
    process ending between two writes, or a hand in the registry -- used to
    reach `SlotProblem.__post_init__` as a pair and stop the advisor at
    every start. Loading makes the two disjoint (`required` wins, Director
    2026-09-14) and writes the repair back, so the next start reads it too.
    """
    store.setValue(effectfilters.KEYS[effectfilters.EXCLUDED], "5,6")
    store.setValue(effectfilters.KEYS[effectfilters.REQUIRED], "6,7")
    store.sync()

    filters = effectfilters.EffectFilters()

    assert (filters.excluded, filters.required) == ({5}, {6, 7})
    assert store.value("advisor/excluded", "", type=str) == "5"
    assert types.SlotProblem(excluded=filters.excluded,
                             required=filters.required).required == {6, 7}


def test_a_marking_writes_both_keys_through_one_store_object(store,
                                                            monkeypatch):
    """SEC-045's other half: one `QSettings` and one `sync()` per marking,
    so the two keys land together rather than in two visits to the registry
    with a gap between them for the process to end in."""
    built = []
    real = effectfilters.QSettings

    def counting(*args, **kwargs):
        settings = real(*args, **kwargs)
        built.append(settings)
        return settings

    monkeypatch.setattr(effectfilters, "QSettings", counting)
    filters = effectfilters.EffectFilters()
    built.clear()

    filters.mark(5, effectfilters.REQUIRED)

    assert len(built) == 1
