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

    def counting(org, app):
        assert (org, app) == (favourites.ORG, favourites.APP)
        settings = QSettings(favourites.ORG, favourites.APP)
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


def test_a_family_marking_is_there_again_and_an_old_allow_is_not_read(store):
    """AK-316.7: the family key, read back by a new instance. `Allow` went
    on 2026-11-16: what an older version left under its key is neither read
    nor overwritten."""
    store.setValue("advisor/allowed", "2")
    filters = effectfilters.EffectFilters(families=FAMILIES)
    filters.mark_family("Improved Attack Power", True)

    restarted = effectfilters.EffectFilters(families=FAMILIES)
    assert restarted.avoided_families == {"Improved Attack Power"}
    assert restarted.resolved_excluded == {1, 2, 3}
    assert not hasattr(restarted, "allowed")
    assert store.value("advisor/allowed", "", type=str) == "2"
    store.setValue("advisor/allowed", "")
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


def test_the_resolved_set_is_the_family_less_ignore_and_favourite(store):
    """AD-039.3: every dataset id of an avoided family, less the ones set
    to Ignore and the ones favourited (a member's own mark wins), plus the
    ids avoided on their own. `changed` fires for a family marking too."""
    filters = effectfilters.EffectFilters(families=FAMILIES)
    heard = []
    filters.changed.connect(lambda: heard.append(True))
    filters.mark_family("Improved Attack Power", True)
    filters.mark(2, effectfilters.IGNORED)
    filters.mark(3, effectfilters.REQUIRED)
    filters.mark(4, effectfilters.EXCLUDED)
    assert filters.resolved_excluded == {1, 4}
    assert types.SlotProblem(excluded=filters.resolved_excluded,
                             required=filters.required).required == {3}
    filters.mark_family("Improved Attack Power", False)
    assert filters.resolved_excluded == {4}
    assert filters.ignored == {2}, "the own mark stays for the next Avoid"
    filters.mark_family("Improved Attack Power", False)
    assert len(heard) == 5


def test_ignore_is_a_third_state_of_the_same_id(store):
    filters = effectfilters.EffectFilters()
    filters.mark(5, effectfilters.EXCLUDED)
    filters.mark(5, effectfilters.IGNORED)
    assert (filters.excluded, filters.ignored) == (frozenset(), {5})
    filters.mark(5, effectfilters.REQUIRED)
    assert (filters.ignored, filters.required) == (frozenset(), {5})


def test_an_id_under_three_keys_is_required_and_under_two_is_excluded(store):
    """T-292c point 2: loading makes the three id sets disjoint --
    `required`, then `excluded`, then `ignored` -- and the overlap in every
    pair reaches `SlotProblem` without a `ValueError`."""
    store.setValue(effectfilters.KEYS[effectfilters.EXCLUDED], "5,6,7,8")
    store.setValue(effectfilters.KEYS[effectfilters.REQUIRED], "6,9")
    store.setValue(effectfilters.KEYS[effectfilters.IGNORED], "7,9")
    store.sync()

    filters = effectfilters.EffectFilters(families={5: "a", 9: "a"})
    filters.mark_family("a", True)

    assert (filters.excluded, filters.required,
            filters.ignored) == ({5, 7, 8}, {6, 9}, frozenset())
    assert store.value("advisor/excluded", "", type=str) == "5,7,8"
    assert store.value("advisor/ignored", "", type=str) == ""
    assert types.SlotProblem(excluded=filters.resolved_excluded,
                             ignored=filters.resolved_ignored,
                             required=filters.required).excluded == {5, 7, 8}


@pytest.mark.parametrize("damaged, names", [
    ("", set()), ("\n\n", set()), (" a \r\nb\r\n", {"a", "b"}),
    ("a, b", {"a, b"})])
def test_a_damaged_family_value_reads_as_whatever_names_it_still_holds(
        store, damaged, names):
    store.setValue(effectfilters.KEYS[effectfilters.AVOIDED_FAMILIES], damaged)
    assert effectfilters.stored_text(effectfilters.AVOIDED_FAMILIES) == names


def test_stacks_stand_under_the_fifth_key_and_are_there_at_the_next_start(store):
    """Ids in the value, never in the key; 0 is a value, `None` none at all."""
    filters = effectfilters.EffectFilters()
    filters.set_stacks(7060200, 2)
    filters.set_stacks(6060300, 0)
    assert store.value("advisor/stacks", "", type=str) == "6060300=0,7060200=2"
    assert effectfilters.EffectFilters().stacks == {6060300: 0, 7060200: 2}

    filters.set_stacks(6060300, None)
    assert effectfilters.EffectFilters().stacks == {7060200: 2}


def test_a_stacks_change_is_heard_once_and_only_when_it_moved_something(store):
    filters = effectfilters.EffectFilters()
    heard = []
    filters.changed.connect(lambda: heard.append(True))
    filters.set_stacks(5, 2)
    filters.set_stacks(5, 2)
    filters.set_stacks(6, None)
    assert len(heard) == 1
    filters.set_stacks(5, None)
    assert len(heard) == 2 and filters.stacks == {}


@pytest.mark.parametrize("damaged, stacks", [
    ("", {}),
    ("abc", {}),
    ("5", {}),
    ("5=", {}),
    ("=2", {}),
    ("5=x", {}),
    ("5=-1", {}),
    ("5=1.5", {}),
    ("5=10", {5: 10}),
    ("5=11", {}),
    ("5=99", {}),
    ("5=100", {}),
    ("5=" + "9" * 5000, {}),
    ("5=2,,x,6=abc,7=0", {5: 2, 7: 0}),
])
def test_a_damaged_stacks_value_reads_as_empty_and_never_as_an_error(
        store, damaged, stacks):
    store.setValue(effectfilters.KEYS[effectfilters.STACKS], damaged)
    assert effectfilters.stored_stacks() == stacks


_UNUSED_HERO_IDS = iter(range(9101, 9200))


@pytest.fixture
def two_heroes(store):
    """Two Nightfarer ids no dataset uses and no other test has written,
    their keys emptied afterwards (an emptied key is a written key, so the
    next test takes fresh ones)."""
    ids = next(_UNUSED_HERO_IDS), next(_UNUSED_HERO_IDS)
    yield ids
    for hero_id in ids:
        for kind in effectfilters.KEYS:
            store.setValue(effectfilters.key_for(kind, hero_id), "")
    store.sync()


def test_each_nightfarer_keeps_its_own_markings(store, two_heroes):
    """User 2026-11-08: guarding effects are a Favourite on a Guardian and
    nothing on a Duchess."""
    guardian, duchess = two_heroes
    filters = effectfilters.EffectFilters(hero_id=guardian)
    filters.mark(7000100, effectfilters.REQUIRED)
    heard = []
    filters.changed.connect(lambda: heard.append(1))
    filters.set_hero(duchess)
    assert filters.required == frozenset()
    assert heard == [1]
    filters.mark(8850550, effectfilters.EXCLUDED)
    filters.set_hero(guardian)
    assert filters.required == {7000100}
    assert filters.excluded == frozenset()
    again = effectfilters.EffectFilters(hero_id=duchess)
    assert again.excluded == {8850550} and again.required == frozenset()


def test_a_nightfarer_without_own_markings_starts_from_the_shared_ones(
        store, two_heroes):
    """What was marked before markings were per Nightfarer is not lost."""
    store.setValue(effectfilters.KEYS[effectfilters.REQUIRED], "7000200")
    filters = effectfilters.EffectFilters(hero_id=two_heroes[0])
    assert filters.required == {7000200}
    filters.mark(7000200, None)
    assert effectfilters.EffectFilters(
        hero_id=two_heroes[0]).required == frozenset()
    assert effectfilters.EffectFilters(
        hero_id=two_heroes[1]).required == {7000200}


def test_ignore_is_stored_per_id_and_per_family_and_yields_to_the_others(
        store):
    """User request 2026-11-16: `Ignore` counts an effect as nothing without
    taking its relic away. It is a state of its own, so marking another way
    moves the id; a member favourited or avoided on its own is not ignored
    with its family, a member ignored on its own is not avoided with it, and a member ignored on its own does not stand for a
    favourited family."""
    families = {1: "A", 2: "A", 3: "B", 4: "B", 5: "C"}
    filters = effectfilters.EffectFilters(families=families)
    filters.mark(5, effectfilters.IGNORED)
    filters.ignore_family("A", True)
    filters.mark(2, effectfilters.REQUIRED)
    assert store.value("advisor/ignored", "", type=str) == "5"
    assert store.value("advisor/ignored_families", "", type=str) == "A"

    restarted = effectfilters.EffectFilters(families=families)
    assert restarted.ignored == {5}
    assert restarted.ignored_families == {"A"}
    assert restarted.resolved_ignored == {1, 5}
    assert restarted.resolved_excluded == frozenset()
    types.SlotProblem(excluded=restarted.resolved_excluded,
                      ignored=restarted.resolved_ignored,
                      required=restarted.required)

    restarted.mark(5, effectfilters.EXCLUDED)
    assert not restarted.ignored and restarted.excluded == {5}
    restarted.mark(5, effectfilters.IGNORED)
    assert restarted.ignored == {5} and not restarted.excluded

    restarted.favour_family("B", True)
    restarted.mark(3, effectfilters.IGNORED)
    assert restarted.favoured == {2, 4}
    assert restarted.favourite_groups(lambda effect_id: "x") == ((4,),)
    assert restarted.resolved_ignored == {1, 3, 5}
    restarted.ignore_family("B", True)
    assert restarted.favourite_families == frozenset()
    assert restarted.resolved_ignored == {1, 3, 4, 5}
    restarted.mark_family("B", True)
    assert restarted.ignored_families == {"A"}
    # 3 is ignored on its own, and that lets it back in (no Allow any more).
    assert restarted.resolved_excluded == {4}
    assert restarted.resolved_ignored == {1, 3, 5}


def test_a_store_that_says_ignored_and_another_state_reads_as_the_other(store):
    store.setValue("advisor/ignored", "1,2,3")
    store.setValue("advisor/required", "1")
    store.setValue("advisor/excluded", "2")
    store.sync()
    filters = effectfilters.EffectFilters()
    assert (filters.required, filters.excluded, filters.ignored) == (
        {1}, {2}, {3})
    assert store.value("advisor/ignored", "", type=str) == "3"
