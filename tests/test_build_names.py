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
#
# The leading space tests the contract between the layers, not what a player
# gets: chalices.save_build stores the name it is handed, untouched, because
# a store that trims returns a different name than the one it was given.
# Through the window the space never reaches it -- app._save_build trims
# first, a confirmed decision of the ui-ux-designer, since a space at the end
# is invisible in the list and two rows that read alike would be a new trap of
# the same kind as the one this file is about. Both are right; they are
# different layers.
AWKWARD_NAME = " Fire / ice \\ storm | ⚔"

# Long enough that the derived key overruns what the store accepts: every "/"
# becomes "%2F", three characters of key for one of name.
TOO_LONG_NAME = "/" * (chalices.MAX_KEY_LENGTH // 3 + 1)

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


def old_slots(index: int) -> list[str]:
    """One build's slots, told apart from every other build's.

    Filling every build with the same relics would let the migration hand a
    build the contents of its neighbour and still pass: what came back would
    equal what went in, for the wrong build. The value has to name the build
    it belongs to for a swap to be visible at all.
    """
    return [f"relic-{index}", "", "", "", "", ""]


def write_the_old_way(hero_id: int, names: list[str]) -> dict[str, list[str]]:
    """Save builds exactly as the code before this change did.

    The name went in as the key and into the order list unaltered; that is
    the state on the machine of anyone who has used the program. Returns the
    slots each name was written with, so a case can hold the migration to
    giving every build back its own.
    """
    settings = QSettings(favourites.ORG, favourites.APP)
    settings.beginGroup(f"{chalices.BUILDS}/{hero_id}")
    for index, name in enumerate(names):
        settings.setValue(
            name, chalices._encode(index + 1, False, old_slots(index)))
    settings.setValue("__order", chalices.SEPARATOR.join(names))
    settings.endGroup()
    settings.sync()
    return {name: old_slots(index) for index, name in enumerate(names)}


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
    expected = write_the_old_way(HERO, ["plain"])
    assert chalices.build_names(HERO) == ["plain"]
    assert slots_of(chalices.load_build(HERO, "plain")) == expected["plain"]


def test_a_build_a_slash_had_hidden_comes_back(qapp):
    """The one the bug actually swallowed.

    It was stored as a group and a key, which is why the list stopped showing
    it; the entry itself was still there and is recovered by name.
    """
    expected = write_the_old_way(HERO, ["Fire / ice"])
    assert chalices.build_names(HERO) == ["Fire / ice"]
    assert (slots_of(chalices.load_build(HERO, "Fire / ice"))
            == expected["Fire / ice"])


def test_every_old_shape_of_name_comes_back(qapp):
    old = ["plain", "Fire / ice", "back\\slash", " lead", "uni⚔"]
    expected = write_the_old_way(HERO, old)
    assert chalices.build_names(HERO) == old
    for name in old:
        assert slots_of(chalices.load_build(HERO, name)) == expected[name]


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


# ---------------------------------------------------------------------------
# Regression 3 -- QA-033: the migration reads everything before it removes
# anything
#
# A name holding a "/" is a group as much as a key, so an old store holding
# "Fire ice" and "Fire ice/v2" holds an entry and a group of that one name
# side by side -- and QSettings.remove() takes the group away with the entry.
# The migration used to remove while it was still reading, so the second build
# was deleted before anyone had looked at it and the empty string that came
# back was written under its new key: the name still in the list, the build
# gone from the store for good. What these cases hold to account is the order
# of the steps; the pair of names is only what made it visible.


def stored_entries(hero_id: int) -> dict[str, str]:
    """Everything under this Nightfarer's build group, key by key."""
    settings = QSettings(favourites.ORG, favourites.APP)
    settings.beginGroup(f"{chalices.BUILDS}/{hero_id}")
    try:
        return {key: str(settings.value(key, "", type=str))
                for key in settings.allKeys()}
    finally:
        settings.endGroup()


class RecordingSettings(QSettings):
    """A settings store that notes every read, write and removal, in order.

    The migration reaches its store through chalices._settings and nowhere
    else, so standing in for it there is what makes the sequence of steps
    observable instead of merely its outcome.
    """

    def __init__(self, log: list[tuple[str, str]]):
        super().__init__(favourites.ORG, favourites.APP)
        self.log = log

    def value(self, key, *args, **kwargs):
        self.log.append(("read", key))
        return super().value(key, *args, **kwargs)

    def setValue(self, key, value):
        self.log.append(("write", key))
        super().setValue(key, value)

    def remove(self, key):
        self.log.append(("remove", key))
        super().remove(key)


def test_the_migration_removes_nothing_until_it_has_read_and_written(
        qapp, monkeypatch):
    """The property itself: after the first removal, nothing is touched again.

    The pair of names below is only the shape that made the loss visible. A
    migration that reads a value after it has removed anything is one edit
    away from losing a build again, whatever the names happen to be, so the
    order of the steps is what is pinned here.
    """
    write_the_old_way(HERO, ["Fire ice", "Fire ice/v2"])
    log: list[tuple[str, str]] = []
    monkeypatch.setattr(chalices, "_settings", lambda: RecordingSettings(log))

    chalices._migrate_keys(HERO)

    steps = [what for what, _ in log]
    assert {"read", "write", "remove"} <= set(steps)
    assert set(steps[steps.index("remove"):]) == {"remove"}


@pytest.mark.parametrize("saved", [
    ["Fire ice", "Fire ice/v2"],
    ["Fire ice/v2", "Fire ice"],
])
def test_a_name_and_a_name_beneath_it_both_survive_the_migration(qapp, saved):
    """Both orders of writing them: neither may take the other with it."""
    expected = write_the_old_way(HERO, saved)
    assert chalices.build_names(HERO) == saved
    for name in saved:
        assert slots_of(chalices.load_build(HERO, name)) == expected[name]


def test_two_names_beneath_a_third_all_survive_the_migration(qapp):
    saved = ["a-b", "a-b/c", "a-b/d"]
    expected = write_the_old_way(HERO, saved)
    assert chalices.build_names(HERO) == saved
    for name in saved:
        assert slots_of(chalices.load_build(HERO, name)) == expected[name]


def test_a_second_migration_leaves_the_store_exactly_as_it_found_it(qapp):
    """Idempotence, on the shapes the removal step now has to handle."""
    write_the_old_way(HERO, ["Fire ice", "Fire ice/v2", "plain"])
    chalices.build_names(HERO)
    after_the_first = stored_entries(HERO)
    chalices.build_names(HERO)
    assert stored_entries(HERO) == after_the_first


# ---------------------------------------------------------------------------
# Regression 4 -- QA-034: the hidden list keeps no name that names nothing


def test_a_hidden_name_holding_the_list_separator_leaves_no_phantom(qapp):
    """A hidden "a|b" used to come back as hidden "a" and hidden "b".

    Neither is a build, so neither could be un-hidden through the window, and
    both stayed in the store for good. The build itself comes back visible
    now, which the player can put right in a click.
    """
    write_the_old_way(HERO, ["a|b", "plain"])
    settings = QSettings(favourites.ORG, favourites.APP)
    settings.setValue(f"{chalices.BUILDS}/{HERO}/__hidden", "a|b|plain")
    settings.sync()

    hidden = chalices.hidden_builds(HERO)

    assert hidden == {"plain"}
    assert hidden <= set(chalices.build_names(HERO)) | set(
        chalices.RESERVED_NAMES)
    chalices.set_hidden(HERO, "plain", False)
    assert chalices.hidden_builds(HERO) == set()


def test_the_equipped_build_stays_hidden_across_the_migration(qapp):
    """It is hideable and stored nowhere, so it is no phantom either."""
    write_the_old_way(HERO, ["plain"])
    settings = QSettings(favourites.ORG, favourites.APP)
    settings.setValue(f"{chalices.BUILDS}/{HERO}/__hidden",
                      chalices.SEPARATOR.join([chalices.EQUIPPED_NAME,
                                               "plain"]))
    settings.sync()
    assert chalices.hidden_builds(HERO) == {chalices.EQUIPPED_NAME, "plain"}


def test_an_old_store_holding_both_faults_at_once_loses_nothing(qapp):
    """A name beneath another and a "|" in the hidden list, in one store."""
    saved = ["Fire ice", "Fire ice/v2", "a|b"]
    expected = write_the_old_way(HERO, saved)
    settings = QSettings(favourites.ORG, favourites.APP)
    settings.setValue(f"{chalices.BUILDS}/{HERO}/__hidden", "a|b")
    settings.sync()

    assert sorted(chalices.build_names(HERO)) == sorted(saved)
    for name in saved:
        assert slots_of(chalices.load_build(HERO, name)) == expected[name]
    assert chalices.hidden_builds(HERO) == set()


# ---------------------------------------------------------------------------
# Regression 5 -- QA-035: a name the store cannot take is refused, not dropped


def test_a_name_too_long_for_the_store_is_refused_and_not_listed(qapp):
    assert len(chalices.build_key(TOO_LONG_NAME)) > chalices.MAX_KEY_LENGTH
    chalices.save_build(HERO, TOO_LONG_NAME, 1, False, SLOTS_A)
    assert chalices.build_names(HERO) == []
    order = stored_entries(HERO).get("__order", "")
    assert chalices.build_key(TOO_LONG_NAME) not in order


def test_a_long_name_that_still_fits_is_saved(qapp):
    """The refusal is a limit, not a blanket: the measured ceiling holds."""
    name = "/" * (chalices.MAX_KEY_LENGTH // 3)
    assert len(chalices.build_key(name)) <= chalices.MAX_KEY_LENGTH
    chalices.save_build(HERO, name, 1, False, SLOTS_A)
    assert chalices.build_names(HERO) == [name]
    assert slots_of(chalices.load_build(HERO, name)) == SLOTS_A


def test_the_panel_says_so_when_a_name_is_too_long(planner, monkeypatch):
    """The player is told. Refusing in silence is the fault, not the fix."""
    from nrplanner import app as appmod

    said: list[str] = []

    class Dialog:
        @staticmethod
        def getText(*args, **kwargs):
            return TOO_LONG_NAME, True

    class Tip:
        @staticmethod
        def showText(position, text):
            said.append(text)

    monkeypatch.setattr(appmod, "QInputDialog", Dialog)
    monkeypatch.setattr(appmod, "QToolTip", Tip)

    planner._save_build()

    assert len(said) == 1 and "too long" in said[0]
    assert chalices.build_names(planner.current_hero()["id"]) == []


# ---------------------------------------------------------------------------
# Regression 6 -- QA-041: an old build is given up only where the new key can
# be read back holding it
#
# The guard that refuses a name the store cannot take sits in save_build. The
# migration had none: it wrote, it removed, and asked nothing in between, so a
# build whose name fits the store while its derived key does not was deleted
# on the first launch after the update -- silently, and past recovery. What is
# held to account here is not the length. Length is one reason a store can
# have for keeping nothing; the rule is that a removal follows a read-back,
# whatever the reason was.


# Six characters of key for one of name, so the derived key overruns a limit
# the name itself is nowhere near: 2 731 characters of name, 16 386 of key.
NAME_WHOSE_KEY_IS_TOO_LONG = "é" * (chalices.MAX_KEY_LENGTH // 6 + 1)


class SettingsThatLoseOneWrite(QSettings):
    """A store that takes one write and keeps nothing of it.

    Nothing here is a matter of length, which is the point: setValue reports
    nothing either way, and a write can be lost for reasons this code has no
    list of -- a quota, a refused permission, a name some backend will not
    take. What the migration may act on is only what it can read back.
    """

    def __init__(self, lose: str):
        super().__init__(favourites.ORG, favourites.APP)
        self.lose = lose

    def setValue(self, key, value):
        if key == self.lose:
            return
        super().setValue(key, value)


def test_an_old_build_whose_key_is_too_long_is_not_lost(qapp):
    """The measured case: a name of 2 731 characters, a key of 16 386."""
    assert len(NAME_WHOSE_KEY_IS_TOO_LONG) <= chalices.MAX_KEY_LENGTH
    assert (len(chalices.build_key(NAME_WHOSE_KEY_IS_TOO_LONG))
            > chalices.MAX_KEY_LENGTH)
    expected = write_the_old_way(HERO, [NAME_WHOSE_KEY_IS_TOO_LONG])

    listed = chalices.build_names(HERO)

    entries = stored_entries(HERO)
    assert NAME_WHOSE_KEY_IS_TOO_LONG in entries
    assert (chalices._decode(entries[NAME_WHOSE_KEY_IS_TOO_LONG])[2]
            == expected[NAME_WHOSE_KEY_IS_TOO_LONG])
    assert listed == [NAME_WHOSE_KEY_IS_TOO_LONG]


def test_an_old_path_whose_write_was_lost_is_not_removed(qapp, monkeypatch):
    """The same rule where nothing is long: the write is simply dropped."""
    saved = ["Fire / ice", "Fire ice"]
    expected = write_the_old_way(HERO, saved)
    lost = chalices.build_key("Fire / ice")
    monkeypatch.setattr(chalices, "_settings",
                        lambda: SettingsThatLoseOneWrite(lost))

    chalices._migrate_keys(HERO)
    monkeypatch.undo()

    entries = stored_entries(HERO)
    assert lost not in entries
    assert "Fire / ice" in entries
    assert (chalices._decode(entries["Fire / ice"])[2]
            == expected["Fire / ice"])
    # The build whose write did land moved, and gave up its old path.
    assert "Fire ice" not in entries
    assert (slots_of(chalices.load_build(HERO, "Fire ice"))
            == expected["Fire ice"])


# ---------------------------------------------------------------------------
# Regression 7 -- QA-042: a removal spares a path that is now somebody's key
#
# "Fire ice" derives the key "Fire%20ice", and in a store that also holds a
# build of that name the derived key is the second build's old path. Removing
# it after the write takes the first build's rescue with it. The case is not
# about the order of the steps -- these removals are already last -- so the
# order test cannot see it, and did not.


def test_a_name_whose_key_is_another_name_leaves_both_builds_standing(qapp):
    saved = ["Fire ice", "Fire%20ice"]
    expected = write_the_old_way(HERO, saved)

    assert chalices.build_names(HERO) == saved
    for name in saved:
        assert slots_of(chalices.load_build(HERO, name)) == expected[name]


def test_a_chain_of_three_such_names_leaves_all_three_standing(qapp):
    """Each name derives the next one's old path, twice over."""
    saved = ["Fire ice", "Fire%20ice", "Fire%2520ice"]
    assert chalices.build_key(saved[0]) == saved[1]
    assert chalices.build_key(saved[1]) == saved[2]
    expected = write_the_old_way(HERO, saved)

    assert chalices.build_names(HERO) == saved
    for name in saved:
        assert slots_of(chalices.load_build(HERO, name)) == expected[name]


# ---------------------------------------------------------------------------
# Regression 8 -- QA-040: the order list keeps no key with no build behind it


def test_the_order_list_keeps_no_key_without_a_build(qapp):
    """A name holding the list separator reached the migration as two halves,
    and neither half is a build. Carried over, they left the list naming keys
    nothing answers to -- invisible on screen, and in the store for good."""
    write_the_old_way(HERO, ["a|b", "plain"])

    chalices.build_names(HERO)

    entries = stored_entries(HERO)
    order = [k for k in entries["__order"].split(chalices.SEPARATOR) if k]
    assert order == [chalices.build_key("plain")]
    for key in order:
        assert key in entries


def test_a_build_named_after_a_phantom_is_appended_like_any_other(qapp):
    """What the dead keys did to the player: "a" was in the order list
    already, so a build later saved under that name inherited the phantom's
    place and stood in front of builds older than itself."""
    write_the_old_way(HERO, ["a|b", "plain"])
    chalices.build_names(HERO)

    chalices.save_build(HERO, "a", 5, False, SLOTS_B)

    names = chalices.build_names(HERO)
    assert names.index("a") > names.index("plain")
    assert slots_of(chalices.load_build(HERO, "a")) == SLOTS_B


# ---------------------------------------------------------------------------
# Regression 9 -- QA-039: a deleted build leaves nothing of itself behind
#
# Hiding is a view of a build. Left behind by a delete, it was inherited by
# the next build saved under that name: visible while it stayed selected,
# gone from the list at the next refresh and in every later session, with a
# checkbox nobody points at as the only way back.


def test_deleting_a_hidden_build_takes_its_hidden_mark_with_it(qapp):
    chalices.save_build(HERO, "Ghost", 1, False, SLOTS_A)
    chalices.set_hidden(HERO, "Ghost", True)

    chalices.delete_build(HERO, "Ghost")

    assert chalices.build_names(HERO) == []
    assert chalices.hidden_builds(HERO) == set()


def test_a_build_saved_again_under_a_deleted_name_is_not_hidden(qapp):
    chalices.save_build(HERO, "Ghost", 1, False, SLOTS_A)
    chalices.set_hidden(HERO, "Ghost", True)
    chalices.delete_build(HERO, "Ghost")

    chalices.save_build(HERO, "Ghost", 2, False, SLOTS_B)

    assert chalices.build_names(HERO) == ["Ghost"]
    assert chalices.hidden_builds(HERO) == set()
    assert chalices.load_build(HERO, "Ghost") == (2, False, SLOTS_B)


def test_deleting_the_selected_build_leaves_the_equipped_one_selected(qapp):
    chalices.save_build(HERO, "Ghost", 1, False, SLOTS_A)
    chalices.set_selected_build(HERO, "Ghost")

    chalices.delete_build(HERO, "Ghost")

    assert chalices.selected_build(HERO) == chalices.EQUIPPED_NAME


def test_the_list_keeps_a_build_saved_again_under_a_deleted_name(planner):
    """The symptom on screen: the player saves a build and cannot find it."""
    hero_id = planner.current_hero()["id"]
    chalices.save_build(hero_id, "Ghost", None, False, SLOTS_A)
    chalices.set_hidden(hero_id, "Ghost", True)
    chalices.delete_build(hero_id, "Ghost")
    chalices.save_build(hero_id, "Ghost", None, False, SLOTS_B)

    planner.refresh_build_list()

    shown = [planner.build_box.itemData(i)
             for i in range(planner.build_box.count())]
    assert "Ghost" in shown
