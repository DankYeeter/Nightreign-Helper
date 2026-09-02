"""A build is filed under a key derived from its name, not under the name.

QA-003. QSettings reads "/" in a key as the path separator it is, so a build
called "Fire / ice" was never an entry of that name -- it was a group called
"Fire " holding an entry called " ice". `childKeys()` cannot see into a group,
so the build disappeared from the list the moment it was saved, and clearing
the Nightfarer's builds took the whole group with it. Two quieter versions sat
beside it: "|" is the separator of the order list, so one name became two, and
a name beginning "__" reads as one of the bookkeeping entries.

Every case here writes to the test settings store that conftest names through
NIGHTREIGN_SETTINGS_ORG / _APP, never the player's own.

The migration cases write the old way on purpose -- straight into QSettings,
as the previous code did -- because a migration that is only ever fed its own
output proves nothing. A player who saved builds before this change must find
them afterwards; losing them would be worse than the bug.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import QSettings

from nrplanner import chalices, favourites

HERO = 4321

# One name carrying every shape the key space used to swallow: the separator
# QSettings reads as a path, a backslash, a leading space the old code trimmed
# away, the separator of the order list, and a character outside ASCII.
AWKWARD_NAME = " Fire / ice \\ storm | ⚔"

# Two names that would collide if a key were derived and then read back
# without escaping the escape: encoding the first must not produce the second.
LOOKS_ENCODED = "Fire%2Fice"
ENCODES_TO_THAT = "Fire/ice"

SLOTS_A = ["a", "", "", "", "", ""]
SLOTS_B = ["b", "", "", "", "", ""]


def slots_of(build) -> list[str]:
    return build[2]


@pytest.fixture(autouse=True)
def a_store_of_our_own():
    """Nothing of another test is inherited, and nothing is left behind."""
    from tests.conftest import clear_settings

    clear_settings()
    yield
    clear_settings()


def write_the_old_way(hero_id: int, names: list[str]) -> None:
    """Save builds exactly as the code before this change did.

    The name went in as the key and into the order list unaltered; that is
    the state on the machine of anyone who has used the program.
    """
    settings = QSettings(favourites.ORG, favourites.APP)
    settings.beginGroup(f"{chalices.BUILDS}/{hero_id}")
    for index, name in enumerate(names):
        settings.setValue(name, chalices._encode(index + 1, False, SLOTS_A))
    settings.setValue("__order", chalices.SEPARATOR.join(names))
    settings.endGroup()
    settings.sync()


# ---------------------------------------------------------------------------
# The derivation itself


def test_a_key_carries_nothing_the_store_reads_as_structure():
    key = chalices.build_key(AWKWARD_NAME)
    for forbidden in ("/", "\\", chalices.SEPARATOR, chalices.FIELD, " "):
        assert forbidden not in key
    assert not key.startswith("_")


def test_a_name_comes_back_out_of_its_key_unchanged():
    for name in (AWKWARD_NAME, LOOKS_ENCODED, ENCODES_TO_THAT,
                 chalices.EQUIPPED_NAME, "__order", "plain"):
        assert chalices.build_name(chalices.build_key(name)) == name


def test_two_names_never_share_a_key():
    assert (chalices.build_key(LOOKS_ENCODED)
            != chalices.build_key(ENCODES_TO_THAT))


# ---------------------------------------------------------------------------
# Regression 1 -- an awkward name survives a round trip and does not collide


def test_an_awkward_name_is_stored_loaded_and_listed_exactly(qapp):
    chalices.save_build(HERO, AWKWARD_NAME, 7, False, SLOTS_A)
    assert chalices.build_names(HERO) == [AWKWARD_NAME]
    assert chalices.load_build(HERO, AWKWARD_NAME) == (7, False, SLOTS_A)


def test_a_name_that_could_collide_does_not_overwrite_the_first(qapp):
    chalices.save_build(HERO, LOOKS_ENCODED, 1, False, SLOTS_A)
    chalices.save_build(HERO, ENCODES_TO_THAT, 2, False, SLOTS_B)
    assert sorted(chalices.build_names(HERO)) == sorted(
        [LOOKS_ENCODED, ENCODES_TO_THAT])
    assert slots_of(chalices.load_build(HERO, LOOKS_ENCODED)) == SLOTS_A
    assert slots_of(chalices.load_build(HERO, ENCODES_TO_THAT)) == SLOTS_B


def test_deleting_one_awkward_name_leaves_the_other(qapp):
    chalices.save_build(HERO, AWKWARD_NAME, 1, False, SLOTS_A)
    chalices.save_build(HERO, ENCODES_TO_THAT, 2, False, SLOTS_B)
    chalices.delete_build(HERO, ENCODES_TO_THAT)
    assert chalices.build_names(HERO) == [AWKWARD_NAME]
    assert slots_of(chalices.load_build(HERO, AWKWARD_NAME)) == SLOTS_A


def test_saving_the_same_name_twice_replaces_it_rather_than_repeating_it(qapp):
    chalices.save_build(HERO, AWKWARD_NAME, 1, False, SLOTS_A)
    chalices.save_build(HERO, AWKWARD_NAME, 2, False, SLOTS_B)
    assert chalices.build_names(HERO) == [AWKWARD_NAME]
    assert chalices.load_build(HERO, AWKWARD_NAME) == (2, False, SLOTS_B)


def test_a_name_of_nothing_but_whitespace_is_refused(qapp):
    chalices.save_build(HERO, "   ", 1, False, SLOTS_A)
    assert chalices.build_names(HERO) == []


def test_hiding_and_selecting_survive_an_awkward_name(qapp):
    chalices.save_build(HERO, AWKWARD_NAME, 1, False, SLOTS_A)
    chalices.set_hidden(HERO, AWKWARD_NAME, True)
    chalices.set_selected_build(HERO, AWKWARD_NAME)
    assert chalices.hidden_builds(HERO) == {AWKWARD_NAME}
    assert chalices.selected_build(HERO) == AWKWARD_NAME
    chalices.set_hidden(HERO, AWKWARD_NAME, False)
    assert chalices.hidden_builds(HERO) == set()


def test_the_list_on_screen_shows_the_name_exactly_as_it_was_saved(planner):
    """The panel, not just the store: the name reaches the box unaltered."""
    hero_id = planner.current_hero()["id"]
    chalices.save_build(hero_id, AWKWARD_NAME, None, False, SLOTS_A)
    planner.refresh_build_list()
    shown = [planner.build_box.itemData(i)
             for i in range(planner.build_box.count())]
    assert AWKWARD_NAME in shown


# ---------------------------------------------------------------------------
# Regression 2 -- builds saved before this change are still there


def test_a_build_saved_before_the_change_is_still_there(qapp):
    write_the_old_way(HERO, ["plain"])
    assert chalices.build_names(HERO) == ["plain"]
    assert slots_of(chalices.load_build(HERO, "plain")) == SLOTS_A


def test_a_build_a_slash_had_hidden_comes_back(qapp):
    """The one the bug actually swallowed.

    It was stored as a group and a key, which is why the list stopped showing
    it; the entry itself was still there and is recovered by name.
    """
    write_the_old_way(HERO, ["Fire / ice"])
    assert chalices.build_names(HERO) == ["Fire / ice"]
    assert slots_of(chalices.load_build(HERO, "Fire / ice")) == SLOTS_A


def test_every_old_shape_of_name_comes_back(qapp):
    old = ["plain", "Fire / ice", "back\\slash", " lead", "uni⚔"]
    write_the_old_way(HERO, old)
    assert chalices.build_names(HERO) == old
    for name in old:
        assert slots_of(chalices.load_build(HERO, name)) == SLOTS_A


def test_migrating_twice_does_not_encode_the_encoding(qapp):
    write_the_old_way(HERO, ["Fire / ice"])
    assert chalices.build_names(HERO) == ["Fire / ice"]
    assert chalices.build_names(HERO) == ["Fire / ice"]
    chalices.save_build(HERO, "later", 9, False, SLOTS_B)
    assert chalices.build_names(HERO) == ["Fire / ice", "later"]


def test_a_hidden_and_selected_build_survive_the_migration(qapp):
    write_the_old_way(HERO, ["Fire / ice", "plain"])
    settings = QSettings(favourites.ORG, favourites.APP)
    settings.setValue(f"{chalices.BUILDS}/{HERO}/__hidden", "plain")
    settings.setValue(f"{chalices.BUILDS}/{HERO}/__selected", "Fire / ice")
    settings.sync()
    assert chalices.hidden_builds(HERO) == {"plain"}
    assert chalices.selected_build(HERO) == "Fire / ice"
