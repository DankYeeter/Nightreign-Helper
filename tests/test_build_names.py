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

import string

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


SCHEMA_2_SAFE = frozenset(string.ascii_letters + string.digits)


def schema_2_key(name: str) -> str:
    """The key the derivation before this change produced.

    Written out here rather than taken from chalices, on purpose: a
    migration fed its own output proves nothing, and the stores this one has
    to rescue were written by code that kept the capital letters.
    """
    return "".join(
        character if character in SCHEMA_2_SAFE
        else "".join(f"%{byte:02X}" for byte in character.encode("utf-8"))
        for character in str(name)
    )


def write_the_schema_2_way(hero_id: int, names: list[str]) -> dict[str, list]:
    """Save builds as the first derived-key version did, marker and all.

    That is the state of the machine this was written on. Two names that
    differ only in case land in one entry here, exactly as they did for the
    player -- the second write wins and the order list names both.
    """
    settings = QSettings(favourites.ORG, favourites.APP)
    settings.beginGroup(f"{chalices.BUILDS}/{hero_id}")
    for index, name in enumerate(names):
        settings.setValue(schema_2_key(name),
                          chalices._encode(index + 1, False, old_slots(index)))
    settings.setValue("__order", chalices.SEPARATOR.join(
        schema_2_key(name) for name in names))
    settings.setValue(chalices.SCHEMA_KEY, chalices.DERIVED_KEYS)
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


def test_an_old_path_that_is_itself_another_builds_key_is_not_removed(
        qapp, monkeypatch):
    """The lost write lands on a key that is itself an old path already.

    "fire ice" derives the key "fire%20ice", which the old store already
    holds as a build of its own. `contains()` on that key is true before the
    write is ever attempted, for a reason that has nothing to do with
    whether "fire ice" migrated -- so losing the write must still be caught
    by comparing the value, not by asking whether the key is occupied.

    Lower case since QA-046, for the reason given above the case before it:
    a capital letter is escaped now, so "Fire ice" no longer derives another
    build's name and the case would prove nothing.
    """
    saved = ["fire ice", "fire%20ice"]
    expected = write_the_old_way(HERO, saved)
    lost = chalices.build_key("fire ice")
    assert lost == saved[1]
    monkeypatch.setattr(chalices, "_settings",
                        lambda: SettingsThatLoseOneWrite(lost))

    chalices._migrate_keys(HERO)
    monkeypatch.undo()

    entries = stored_entries(HERO)
    assert "fire ice" in entries
    assert (chalices._decode(entries["fire ice"])[2]
            == expected["fire ice"])


# ---------------------------------------------------------------------------
# Regression 7 -- QA-042: a removal spares a path that is now somebody's key
#
# "fire ice" derives the key "fire%20ice", and in a store that also holds a
# build of that name the derived key is the second build's old path. Removing
# it after the write takes the first build's rescue with it. The case is not
# about the order of the steps -- these removals are already last -- so the
# order test cannot see it, and did not.
#
# The names are lower case since QA-046. They read "Fire ice" and
# "Fire%20ice" until the derivation started escaping capital letters, which
# ends the relation these cases are built on: "Fire ice" now derives
# "%46ire%20ice", which is nobody's old path, and the two cases went on
# passing while holding nothing to account. Same shape, spelled in the
# characters the derivation still passes through.


def test_a_name_whose_key_is_another_name_leaves_both_builds_standing(qapp):
    saved = ["fire ice", "fire%20ice"]
    assert chalices.build_key(saved[0]) == saved[1]
    expected = write_the_old_way(HERO, saved)

    assert chalices.build_names(HERO) == saved
    for name in saved:
        assert slots_of(chalices.load_build(HERO, name)) == expected[name]


def test_a_chain_of_three_such_names_leaves_all_three_standing(qapp):
    """Each name derives the next one's old path, twice over."""
    saved = ["fire ice", "fire%20ice", "fire%2520ice"]
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


# ---------------------------------------------------------------------------
# Regression 10 -- QA-046: a key has to be one of a kind in the store, not in
# the string space
#
# QSettings keys are registry value names on Windows, and the registry tells
# two of them apart without regard to case. The derivation was injective
# against Python strings and filed "Bleed build" and "bleed build" in one
# entry: both names in the list, one build behind them, and deleting either
# took the other away with it. Nothing here is a migration case -- it is what
# the program does on an ordinary afternoon.

# The pair the finding was raised on.
UPPER_CASE_NAME, LOWER_CASE_NAME = "Bleed build", "bleed build"

# Names that are different to Python and have every reason to be run together
# by a store: capitals, escapes that look like names, names that look like
# escapes, non-ASCII that carries a case of its own, and the two separators.
# "Straße"/"STRASSE" and "istanbul"/"ıstanbul" are the pairs where Python's
# own idea of folding case is not the store's -- they belong here because the
# derivation may lean on neither.
LOOKALIKE_NAMES = [
    UPPER_CASE_NAME, LOWER_CASE_NAME, "BLEED BUILD", "BleeD BuilD",
    "fire/ice", "Fire/Ice", "fire%2fice", "fire%2Fice", "FIRE%2FICE",
    "a|b", "A|B", "__order", "__ORDER",
    "%", "%25", "%%",
    "Straße", "STRASSE", "strasse",
    "istanbul", "İstanbul", "ıstanbul", "ISTANBUL",
    "⚔ deep", "⚔ DEEP",
    " lead", "lead ",
]


def build_entries(hero_id: int) -> dict[str, str]:
    """The builds in this Nightfarer's group, as the store spells them."""
    return {key: value for key, value in stored_entries(hero_id).items()
            if not key.startswith("__")}


# ---------------------------------------------------------------------------
# The derivation, and what makes it one of a kind where it is stored


def test_no_two_names_arrive_at_one_key_however_the_store_folds_case():
    """Neither folding can bring two of these keys together.

    The store is asked in the case below; this one holds the property the
    store's answer rests on, over more names than a store test wants to
    write, and in both directions -- Windows folds by putting a name into
    capitals, Python by putting it into lower case, and the derivation may
    not depend on which.
    """
    assert len(set(LOOKALIKE_NAMES)) == len(LOOKALIKE_NAMES)
    keys = [chalices.build_key(name) for name in LOOKALIKE_NAMES]
    assert len({key.casefold() for key in keys}) == len(LOOKALIKE_NAMES)
    assert len({key.upper() for key in keys}) == len(LOOKALIKE_NAMES)


def test_a_key_holds_no_character_that_has_a_second_spelling():
    """Everything a name says reaches the key escaped or in lower case.

    The capitals a key does hold are the hex digits of its own escapes, and
    those are written by this module rather than by the player.
    """
    for name in LOOKALIKE_NAMES:
        key = chalices.build_key(name)
        outside_escapes = [
            character for index, character in enumerate(key)
            if "%" not in key[max(0, index - 2):index + 1]
        ]
        assert not [c for c in outside_escapes if c.isupper()]


def test_a_name_without_capitals_keeps_the_key_schema_2_filed_it_under():
    """The escapes are written one way only, and that way is schema 2's.

    Not a matter of taste: the stores in the field are on schema 2, and a
    name with no capital letter in it is already filed under exactly this
    key. Spelling the hex digits the other way round would move every one of
    those entries to a place the store cannot tell from the old one, for
    nothing.
    """
    for name in ("fire / ice", "uni⚔", "a|b", "%", " lead", "straße"):
        assert schema_2_key(name) == chalices.build_key(name)


# ---------------------------------------------------------------------------
# The store itself


def test_two_names_that_differ_only_in_case_are_two_builds(qapp):
    """The reported case, in ordinary use: save one, save the other.

    Both were one entry, so both loaded the second build, and deleting
    either emptied the list.
    """
    chalices.save_build(HERO, UPPER_CASE_NAME, 1, False, SLOTS_A)
    chalices.save_build(HERO, LOWER_CASE_NAME, 2, False, SLOTS_B)

    assert chalices.build_names(HERO) == [UPPER_CASE_NAME, LOWER_CASE_NAME]
    assert chalices.load_build(HERO, UPPER_CASE_NAME) == (1, False, SLOTS_A)
    assert chalices.load_build(HERO, LOWER_CASE_NAME) == (2, False, SLOTS_B)

    chalices.delete_build(HERO, LOWER_CASE_NAME)

    assert chalices.build_names(HERO) == [UPPER_CASE_NAME]
    assert chalices.load_build(HERO, UPPER_CASE_NAME) == (1, False, SLOTS_A)


def test_a_hidden_mark_on_one_case_leaves_the_other_showing(qapp):
    """The marks are keyed the same way, so they collided the same way."""
    chalices.save_build(HERO, UPPER_CASE_NAME, 1, False, SLOTS_A)
    chalices.save_build(HERO, LOWER_CASE_NAME, 2, False, SLOTS_B)

    chalices.set_hidden(HERO, LOWER_CASE_NAME, True)
    chalices.set_selected_build(HERO, UPPER_CASE_NAME)

    assert chalices.hidden_builds(HERO) == {LOWER_CASE_NAME}
    assert chalices.selected_build(HERO) == UPPER_CASE_NAME


def test_every_lookalike_name_keeps_an_entry_of_its_own(qapp):
    """The guard of the class: the store does the counting, not Python.

    Every name goes in through the layer the program uses, and the store is
    then asked how many entries it is holding. As many entries as names, and
    each one giving back the build that was saved under it, is the whole
    property -- and it is the one that fails the moment the safe set is
    widened again, whatever the derivation looks like on paper.
    """
    for index, name in enumerate(LOOKALIKE_NAMES):
        chalices.save_build(HERO, name, index + 1, False, old_slots(index))

    assert len(build_entries(HERO)) == len(LOOKALIKE_NAMES)
    assert sorted(chalices.build_names(HERO)) == sorted(LOOKALIKE_NAMES)
    for index, name in enumerate(LOOKALIKE_NAMES):
        assert chalices.load_build(HERO, name) == (
            index + 1, False, old_slots(index))


def test_deleting_one_lookalike_leaves_every_other_one_standing(qapp):
    """A delete reaches one entry, not the ones the store spells alike."""
    for index, name in enumerate(LOOKALIKE_NAMES):
        chalices.save_build(HERO, name, index + 1, False, old_slots(index))

    chalices.delete_build(HERO, LOWER_CASE_NAME)

    left = [name for name in LOOKALIKE_NAMES if name != LOWER_CASE_NAME]
    assert sorted(chalices.build_names(HERO)) == sorted(left)
    for index, name in enumerate(LOOKALIKE_NAMES):
        if name != LOWER_CASE_NAME:
            assert (slots_of(chalices.load_build(HERO, name))
                    == old_slots(index))


# ---------------------------------------------------------------------------
# Regression 11 -- QA-046, the two stores in the field
#
# Schema 1 filed a build under the name itself, schema 2 under a key that
# kept the capitals. Both collide in the store, both have to arrive at
# schema 3, and a second pass over either may change nothing.


def test_a_store_of_names_migrates_to_the_new_keys(qapp):
    old = ["plain", "Fire / ice", "back\\slash", " lead", "uni⚔", "CAPITALS"]
    expected = write_the_old_way(HERO, old)

    assert chalices.build_names(HERO) == old
    for name in old:
        assert slots_of(chalices.load_build(HERO, name)) == expected[name]
    assert set(build_entries(HERO)) == {chalices.build_key(n) for n in old}


def test_a_schema_2_store_migrates_to_the_new_keys(qapp):
    """The state of the machine this was written on."""
    old = ["plain", "Fire / ice", "back\\slash", " lead", "uni⚔", "CAPITALS"]
    expected = write_the_schema_2_way(HERO, old)

    assert chalices.build_names(HERO) == old
    for name in old:
        assert slots_of(chalices.load_build(HERO, name)) == expected[name]
    assert set(build_entries(HERO)) == {chalices.build_key(n) for n in old}


def test_a_schema_2_store_keeps_its_hidden_marks_and_its_selection(qapp):
    """Both are stored as keys there, so both have to be read as keys.

    The equipped build is the case that a comparison against the raw entry
    would drop: it is hideable, it is stored nowhere, and on schema 2 its
    mark is spelled "Equipped%20in%20game" rather than in words.
    """
    write_the_schema_2_way(HERO, ["plain", "Fire / ice"])
    settings = QSettings(favourites.ORG, favourites.APP)
    settings.setValue(f"{chalices.BUILDS}/{HERO}/__hidden",
                      chalices.SEPARATOR.join(
                          [schema_2_key(chalices.EQUIPPED_NAME),
                           schema_2_key("plain")]))
    settings.setValue(f"{chalices.BUILDS}/{HERO}/__selected",
                      schema_2_key("Fire / ice"))
    settings.sync()

    assert chalices.hidden_builds(HERO) == {chalices.EQUIPPED_NAME, "plain"}
    assert chalices.selected_build(HERO) == "Fire / ice"


@pytest.mark.parametrize("write", [write_the_old_way, write_the_schema_2_way])
def test_a_collided_pair_arrives_as_two_builds_holding_what_they_held(
        qapp, write):
    """What becomes of a collision that is already in the store.

    One entry, two names in the order list, and no way of telling which of
    the two the value was written for -- so both names are carried over onto
    the build both of them showed before this ran. Nothing is invented and
    no name is dropped; from here on the two are separate entries the player
    can edit apart.
    """
    expected = write(HERO, [UPPER_CASE_NAME, LOWER_CASE_NAME])
    assert len(build_entries(HERO)) == 1, "the store held one entry for both"

    assert chalices.build_names(HERO) == [UPPER_CASE_NAME, LOWER_CASE_NAME]
    assert len(build_entries(HERO)) == 2
    for name in (UPPER_CASE_NAME, LOWER_CASE_NAME):
        assert (slots_of(chalices.load_build(HERO, name))
                == expected[LOWER_CASE_NAME])


@pytest.mark.parametrize("write", [write_the_old_way, write_the_schema_2_way])
def test_the_names_of_a_collided_pair_can_then_be_told_apart(qapp, write):
    """The point of splitting them: an edit reaches one and not the other."""
    write(HERO, [UPPER_CASE_NAME, LOWER_CASE_NAME])
    chalices.build_names(HERO)

    chalices.save_build(HERO, LOWER_CASE_NAME, 9, False, SLOTS_B)

    assert chalices.load_build(HERO, LOWER_CASE_NAME) == (9, False, SLOTS_B)
    assert slots_of(chalices.load_build(HERO, UPPER_CASE_NAME)) != SLOTS_B
    chalices.delete_build(HERO, LOWER_CASE_NAME)
    assert chalices.build_names(HERO) == [UPPER_CASE_NAME]


@pytest.mark.parametrize("write", [write_the_old_way, write_the_schema_2_way])
def test_a_second_migration_of_either_store_changes_nothing(qapp, write):
    write(HERO, [UPPER_CASE_NAME, LOWER_CASE_NAME, "plain", "Fire / ice"])
    chalices.build_names(HERO)
    after_the_first = stored_entries(HERO)

    chalices.build_names(HERO)

    assert stored_entries(HERO) == after_the_first


# A name of capitals: 5 462 characters of name, and 16 386 of key now that a
# capital letter is escaped like anything else. Schema 2 filed it under
# 5 462 characters and the store took it.
NAME_WHOSE_NEW_KEY_IS_TOO_LONG = "A" * (chalices.MAX_KEY_LENGTH // 3 + 1)


def test_a_schema_2_build_the_new_key_is_too_long_for_stays_where_it_is(qapp):
    """QA-044 may not get worse: it may lie there, it may not disappear.

    The new derivation makes keys longer, so a build that fits schema 2 can
    overrun what the store takes. It keeps its old entry and its place in
    the list, because a build is given up only where the new key can be read
    back holding it.
    """
    assert len(schema_2_key(NAME_WHOSE_NEW_KEY_IS_TOO_LONG)) \
        <= chalices.MAX_KEY_LENGTH
    assert len(chalices.build_key(NAME_WHOSE_NEW_KEY_IS_TOO_LONG)) \
        > chalices.MAX_KEY_LENGTH
    expected = write_the_schema_2_way(
        HERO, [NAME_WHOSE_NEW_KEY_IS_TOO_LONG, "plain"])

    listed = chalices.build_names(HERO)

    assert sorted(listed) == sorted([NAME_WHOSE_NEW_KEY_IS_TOO_LONG, "plain"])
    entries = build_entries(HERO)
    old = schema_2_key(NAME_WHOSE_NEW_KEY_IS_TOO_LONG)
    assert old in entries
    assert (chalices._decode(entries[old])[2]
            == expected[NAME_WHOSE_NEW_KEY_IS_TOO_LONG])
    assert (slots_of(chalices.load_build(HERO, "plain")) == expected["plain"])


def test_a_schema_2_path_whose_write_was_lost_is_not_removed(qapp,
                                                             monkeypatch):
    """The T-020 rule, on the store this migration now also has to read.

    Nothing here is a matter of length: the write is simply dropped, which
    is what a quota or a refused permission would look like from in here.
    """
    saved = ["Fire / ice", "plain"]
    expected = write_the_schema_2_way(HERO, saved)
    lost = chalices.build_key("Fire / ice")
    monkeypatch.setattr(chalices, "_settings",
                        lambda: SettingsThatLoseOneWrite(lost))

    chalices._migrate_keys(HERO)
    monkeypatch.undo()

    entries = build_entries(HERO)
    assert lost not in entries
    old = schema_2_key("Fire / ice")
    assert old in entries
    assert chalices._decode(entries[old])[2] == expected["Fire / ice"]
    assert slots_of(chalices.load_build(HERO, "plain")) == expected["plain"]


def test_a_fragment_naming_a_bookkeeping_entry_is_not_taken_for_a_build(
        qapp):
    """The order list is asked what it holds, and it can name itself.

    A name holding a "|" reaches the migration as two fragments (QA-034),
    and a fragment can read "__order". The store answers for that one -- it
    is an entry, only not a build -- so following every fragment the store
    answers for would file the order list itself as a build with the other
    builds' keys for slots.
    """
    write_the_old_way(HERO, ["x|__order"])

    names = chalices.build_names(HERO)

    assert names == ["x|__order"]


def test_the_list_shows_a_collided_pair_as_two_rows(planner):
    """On screen, where the player met it: two names, two builds."""
    hero_id = planner.current_hero()["id"]
    write_the_schema_2_way(hero_id, [UPPER_CASE_NAME, LOWER_CASE_NAME])

    planner.refresh_build_list()

    shown = [planner.build_box.itemData(i)
             for i in range(planner.build_box.count())]
    assert shown.count(UPPER_CASE_NAME) == 1
    assert shown.count(LOWER_CASE_NAME) == 1
