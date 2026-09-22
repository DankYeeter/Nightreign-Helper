"""The two marked effect sets: stored under two fixed keys, disjoint, heard.

AD-036.5 and AK-283: what the player marked `Avoid` or `Favourite` (AK-300)
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
    real = favourites.QSettings

    def counting(*args, **kwargs):
        settings = real(*args, **kwargs)
        built.append(settings)
        return settings

    monkeypatch.setattr(favourites, "QSettings", counting)
    filters = effectfilters.EffectFilters()
    built.clear()

    filters.mark(5, effectfilters.REQUIRED)

    assert len(built) == 1


FAMILIES = {1: "Improved Attack Power", 2: "Improved Attack Power",
            3: "Improved Attack Power", 4: "Dexterity",
            5: "Improved Mind and Faith, Reduced Intelligence"}


def test_a_family_marking_and_an_allow_are_there_again_at_the_next_start(store):
    """AD-039.4, AK-316.7: the two new keys, read back by a new instance."""
    filters = effectfilters.EffectFilters(families=FAMILIES)
    filters.mark_family("Improved Attack Power", True)
    filters.mark(2, effectfilters.ALLOWED)

    restarted = effectfilters.EffectFilters(families=FAMILIES)
    assert restarted.avoided_families == {"Improved Attack Power"}
    assert restarted.allowed == {2}
    assert store.value("advisor/allowed", "", type=str) == "2"
    assert store.value("advisor/avoided_families", "",
                       type=str) == "Improved Attack Power"


def test_a_family_key_with_a_comma_survives_the_store(store):
    """T-292c point 5: through the real `QSettings` store, not a mock -- a
    comma in the name is not a separator, the line break is."""
    filters = effectfilters.EffectFilters(families=FAMILIES)
    filters.mark_family("Improved Mind and Faith, Reduced Intelligence", True)
    filters.mark_family("Dexterity", True)
    restarted = effectfilters.EffectFilters(families=FAMILIES)
    assert restarted.avoided_families == {
        "Improved Mind and Faith, Reduced Intelligence", "Dexterity"}
    assert restarted.resolved_excluded == {4, 5}


def test_the_resolved_set_is_the_family_less_allow_and_favourite(store):
    """AD-039.3: every dataset id of an avoided family, less the ones on
    Allow and the ones favourited (Favourite wins), plus the ids avoided
    on their own. `changed` fires for a family marking too."""
    filters = effectfilters.EffectFilters(families=FAMILIES)
    heard = []
    filters.changed.connect(lambda: heard.append(True))
    filters.mark_family("Improved Attack Power", True)
    filters.mark(2, effectfilters.ALLOWED)
    filters.mark(3, effectfilters.REQUIRED)
    filters.mark(4, effectfilters.EXCLUDED)
    assert filters.resolved_excluded == {1, 4}
    assert types.SlotProblem(excluded=filters.resolved_excluded,
                             required=filters.required).required == {3}
    filters.mark_family("Improved Attack Power", False)
    assert filters.resolved_excluded == {4}
    assert filters.allowed == {2}, "Allow stays stored for the next Avoid"
    filters.mark_family("Improved Attack Power", False)
    assert len(heard) == 5


def test_allow_is_a_third_state_of_the_same_id(store):
    filters = effectfilters.EffectFilters()
    filters.mark(5, effectfilters.EXCLUDED)
    filters.mark(5, effectfilters.ALLOWED)
    assert (filters.excluded, filters.allowed) == (frozenset(), {5})
    filters.mark(5, effectfilters.REQUIRED)
    assert (filters.allowed, filters.required) == (frozenset(), {5})


def test_an_id_under_three_keys_is_required_and_under_two_is_allowed(store):
    """T-292c point 2: loading makes the three id sets disjoint --
    `required`, then `allowed`, then `excluded` -- and the overlap in every
    pair reaches `SlotProblem` without a `ValueError`."""
    store.setValue(effectfilters.KEYS[effectfilters.EXCLUDED], "5,6,7,8")
    store.setValue(effectfilters.KEYS[effectfilters.REQUIRED], "6,9")
    store.setValue(effectfilters.KEYS[effectfilters.ALLOWED], "7,9")
    store.sync()

    filters = effectfilters.EffectFilters(families={5: "a", 9: "a"})
    filters.mark_family("a", True)

    assert (filters.excluded, filters.required,
            filters.allowed) == ({5, 8}, {6, 9}, {7})
    assert store.value("advisor/excluded", "", type=str) == "5,8"
    assert store.value("advisor/allowed", "", type=str) == "7"
    assert types.SlotProblem(excluded=filters.resolved_excluded,
                             required=filters.required).excluded == {5, 8}


@pytest.mark.parametrize("damaged, names", [
    ("", set()), ("\n\n", set()), (" a \r\nb\r\n", {"a", "b"}),
    ("a, b", {"a, b"})])
def test_a_damaged_family_value_reads_as_whatever_names_it_still_holds(
        store, damaged, names):
    store.setValue(effectfilters.KEYS[effectfilters.AVOIDED_FAMILIES], damaged)
    assert effectfilters.stored_text(effectfilters.AVOIDED_FAMILIES) == names
