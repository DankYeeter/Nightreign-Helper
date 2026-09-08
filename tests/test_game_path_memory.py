"""The two remembered paths, and the one place that resolves the game.

R1 to R6 of Nachtrag XI. Two of the properties here are the only barrier
SEC-026 leaves standing, and both would break without a sound:

* `paths/game` is written from a confirmation and from nothing else. A find
  by the automatic route that wrote itself back would turn "the folder the
  user vouched for" into "the folder something found once", and no screen
  would show the difference;
* the check that says a remembered folder is still valid is the *same
  function* that accepted it. A second predicate for the same question drifts
  from the first, and the drift is only visible as a folder that was good
  yesterday and is refused today.

And one that would break loudly for whoever it hit, but silently for the
suite: `QSettings.remove` on a `paths/` key. Two of the three settings losses
of cycles 4 and 5 were a `remove` that took more than it named
(`chalices.py:190-320`), so the scan below is over the whole tree and not
over the module that happens to hold the keys today.

The scan is read off the syntax tree for the reason `test_settings_store.py`
gives for its own: the behaviour cases can only speak about the lines they
run, and a `remove` added to a branch no case reaches is exactly the shape
this project keeps producing.

What the scan does not see, and does not claim to: a key put together at run
time out of pieces; `QSettings.clear()`, which the suite itself uses to empty
its own store between runs; anything that is not a `.py` file; and anything
under `.venv` or `.claude`, which hold PySide6 and another checkout of this
repository rather than more of this program.
"""

from __future__ import annotations

import ast
import pathlib

import pytest
from PySide6.QtCore import QSettings

from nrdata import gamefiles, oodle
from nrplanner import favourites, gamepath
from tests.test_settings_store import python_modules

REPO = pathlib.Path(__file__).resolve().parents[1]

# A path that exists nowhere on this machine and is absolute all the same.
A_PATH_NOBODY_HAS = r"D:\Games\Elden Ring, alt\Game"


@pytest.fixture
def store():
    """The test store, with both path keys emptied afterwards.

    Emptied by writing an empty value, which is how a damaged entry reads
    anyway. Nothing in this suite may call `remove` on these keys either --
    the scan below runs over the tests as well.
    """
    settings = QSettings(favourites.ORG, favourites.APP)
    yield settings
    for key in (gamepath.GAME_KEY, gamepath.SAVE_KEY):
        settings.setValue(key, "")
    settings.sync()


def a_game_folder(where: pathlib.Path) -> pathlib.Path:
    """A folder stage 1 accepts, built out of three files and a byte."""
    from tests.test_game_dir_recognition import make_game

    return make_game(where)


# --- R1: the two keys are these two keys ---------------------------------


def test_the_two_keys_are_named_in_full():
    """Written out, not read off the constants they are supposed to pin.

    An expectation taken from `gamepath.GAME_KEY` would follow a rename of
    the key into the registry of every player who ever confirmed a folder,
    and say nothing while it did.
    """
    assert gamepath.GAME_KEY == "paths/game"
    assert gamepath.SAVE_KEY == "paths/save"


def test_a_remembered_folder_comes_back_as_it_went_in(store):
    """R4: a comma in a folder name survives the store."""
    gamepath.remember_game(pathlib.Path(A_PATH_NOBODY_HAS))

    assert gamepath.remembered_game() == pathlib.Path(A_PATH_NOBODY_HAS)


def test_the_save_is_remembered_under_its_own_key(store):
    a_save = pathlib.Path(r"D:\Saves\NR0000.sl2")
    gamepath.remember_save(a_save)

    assert gamepath.remembered_save() == a_save
    assert store.value(gamepath.SAVE_KEY, "", type=str) == str(a_save)


# --- R3: a damaged entry counts as absent, and stays where it is ---------


DAMAGED = {
    "empty": "",
    "a null byte in the text": "D:\\Games\0\\Game",
    "longer than any path": "D:\\" + "a" * 20_000,
    "not a path at all": 42,
    "a list, which is what a file-backed store makes of a comma":
        ["D:\\Games\\Elden Ring", " alt\\Game"],
    "relative, so not something remember_game wrote": "Game",
}


@pytest.mark.parametrize("damage", sorted(DAMAGED))
def test_a_damaged_entry_reads_as_absent(store, damage):
    store.setValue(gamepath.GAME_KEY, DAMAGED[damage])
    store.sync()

    assert gamepath.remembered_game() is None


@pytest.mark.parametrize("damage", sorted(DAMAGED))
def test_a_damaged_entry_falls_through_to_the_automatic_route(
        store, monkeypatch, tmp_path, damage):
    """It resolves, it does not raise, and the entry is left alone."""
    found = a_game_folder(tmp_path / "found")
    monkeypatch.setattr(gamefiles, "find_game_dir", lambda: found)
    store.setValue(gamepath.GAME_KEY, DAMAGED[damage])
    store.sync()
    before = store.value(gamepath.GAME_KEY)

    assert gamepath.resolve_game() == found
    assert store.value(gamepath.GAME_KEY) == before


# --- R5: the chain, and what it does not write ---------------------------


class Counter:
    """A stand-in for the automatic search that says how often it ran."""

    def __init__(self, answer):
        self.answer = answer
        self.calls = 0

    def __call__(self):
        self.calls += 1
        return self.answer


def test_a_valid_remembered_folder_is_used_and_nothing_else_runs(
        store, monkeypatch, tmp_path):
    """AK-107 step 1, as a count against a literal."""
    remembered = a_game_folder(tmp_path / "remembered")
    automatic = Counter(a_game_folder(tmp_path / "automatic"))
    monkeypatch.setattr(gamefiles, "find_game_dir", automatic)
    gamepath.remember_game(remembered)

    assert gamepath.resolve_game() == remembered
    assert automatic.calls == 0


def test_a_folder_that_is_no_longer_a_game_falls_through(
        store, monkeypatch, tmp_path):
    """AK-107 step 2. The folder is still there; the game is not.

    This is the case a second predicate would get wrong: a check that only
    asked whether the folder exists would hand back a folder the program
    cannot read a byte out of.
    """
    remembered = a_game_folder(tmp_path / "remembered")
    (remembered / oodle._DLL_NAMES[0]).unlink()
    automatic = Counter(a_game_folder(tmp_path / "automatic"))
    monkeypatch.setattr(gamefiles, "find_game_dir", automatic)
    gamepath.remember_game(remembered)

    assert gamepath.resolve_game() == automatic.answer
    assert automatic.calls == 1


def test_a_find_by_the_automatic_route_is_not_written_back(
        store, monkeypatch, tmp_path):
    """AK-107 step 3, and the invariant SEC-026 leans on.

    A drive comes back. What the user confirmed stays confirmed until he
    confirms something else, so the value in the store is byte for byte the
    one that was there before the automatic route ran.
    """
    gone = tmp_path / "unplugged" / "Game"
    gamepath.remember_game(gone)
    before = store.value(gamepath.GAME_KEY, "", type=str)
    found = a_game_folder(tmp_path / "found")
    monkeypatch.setattr(gamefiles, "find_game_dir", lambda: found)

    assert gamepath.resolve_game() == found
    assert store.value(gamepath.GAME_KEY, "", type=str) == before
    assert gamepath.remembered_game() == gone


def test_nothing_at_all_is_written_when_there_was_nothing_before(
        store, monkeypatch, tmp_path):
    found = a_game_folder(tmp_path / "found")
    monkeypatch.setattr(gamefiles, "find_game_dir", lambda: found)

    assert gamepath.resolve_game() == found
    assert gamepath.remembered_game() is None


def test_no_game_anywhere_is_no_answer_rather_than_an_error(
        store, monkeypatch):
    monkeypatch.setattr(gamefiles, "find_game_dir", lambda: None)

    assert gamepath.resolve_game() is None


def test_what_is_accepted_today_is_valid_tomorrow(store, tmp_path):
    """One predicate for both questions, taken from both ends.

    Whatever `looks_like_the_game` accepts resolves without the automatic
    route being needed, and whatever it rejects does not. A second predicate
    for the start-up check makes one of the two directions false.
    """
    accepted = a_game_folder(tmp_path / "accepted")
    rejected = tmp_path / "rejected"
    rejected.mkdir()
    (rejected / "regulation.bin").write_bytes(b"x")

    assert gamefiles.looks_like_the_game(accepted)
    gamepath.remember_game(accepted)
    assert gamepath.resolve_game() == accepted

    assert not gamefiles.looks_like_the_game(rejected)
    gamepath.remember_game(rejected)
    assert gamepath.resolve_game() != rejected


# --- R2: no removal of a path key, anywhere in the tree ------------------


# The names the two keys are reachable under, so a removal written as
# `settings.remove(GAME_KEY)` is seen as well as one written out.
PATH_KEY_NAMES = frozenset({"GAME_KEY", "SAVE_KEY"})
PATH_KEY_PREFIX = "paths"

# Call sites that are allowed to remove a `paths/` key. There are none, and
# there is no case in which there could be one: the values are overwritten by
# a confirmation and left alone otherwise. An entry here would need its
# reason beside it -- and the case below holds that the list only shrinks.
REMOVALS_THAT_ARE_ALLOWED: frozenset[str] = frozenset()


def _names_a_path_key(node: ast.AST) -> bool:
    """Does this argument name one of the two keys, or their group?

    The group counts: on Windows a key and a group of the same name are the
    same registry key, which is how QA-033 lost a build that was still being
    read.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return (node.value == PATH_KEY_PREFIX
                or node.value.startswith(f"{PATH_KEY_PREFIX}/"))
    if isinstance(node, ast.Name):
        return node.id in PATH_KEY_NAMES
    if isinstance(node, ast.Attribute):
        return node.attr in PATH_KEY_NAMES
    if isinstance(node, ast.JoinedStr):
        first = node.values[0] if node.values else None
        return (isinstance(first, ast.Constant)
                and isinstance(first.value, str)
                and first.value.startswith(PATH_KEY_PREFIX))
    return False


def removals_of_a_path_key(source: str) -> list[int]:
    """The line of every `remove()` this source aims at a path key."""
    tree = ast.parse(source)
    return sorted(
        node.lineno for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "remove"
        and node.args
        and _names_a_path_key(node.args[0])
    )


def test_no_source_removes_a_remembered_path():
    offenders = {}
    for path in python_modules(REPO):
        lines = removals_of_a_path_key(path.read_text(encoding="utf-8"))
        if lines:
            offenders[path.relative_to(REPO).as_posix()] = lines
    assert not offenders, (
        "these lines remove a key under paths/, and a remove takes the group "
        f"of the same name with it: {offenders}. Overwrite the value, or "
        "leave it where it is."
    )


def test_the_module_that_owns_the_keys_removes_nothing_at_all():
    """A stricter rule for one file, because a key can be a variable there.

    The scan above reads what is written: `settings.remove(key)` inside
    `gamepath` names a path key on every path through the function and looks
    like nothing at all to a scan of literals. Every key that module touches
    is one of the two, so the rule there is simply that it removes nothing.
    """
    source = (REPO / "nrplanner" / "gamepath.py").read_text(encoding="utf-8")
    removals = [node.lineno for node in ast.walk(ast.parse(source))
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "remove"]

    assert not removals, (
        f"nrplanner/gamepath.py removes something at line {removals}, and "
        "every key it touches is paths/game or paths/save."
    )


def test_the_list_of_allowed_removals_is_empty():
    """It may shrink. It has nowhere to shrink to, which is the point."""
    assert REMOVALS_THAT_ARE_ALLOWED == frozenset()


REMOVALS_THE_SCAN_MUST_SEE = {
    "the key written out":
        "settings.remove('paths/game')\n",
    "the other key":
        "settings.remove('paths/save')\n",
    "the group, which takes both with it":
        "settings.remove('paths')\n",
    "through the constant":
        "from .gamepath import GAME_KEY\nsettings.remove(GAME_KEY)\n",
    "through the module":
        "from . import gamepath\nsettings.remove(gamepath.SAVE_KEY)\n",
    "a key put together in an f-string":
        "settings.remove(f'paths/{which}')\n",
}

REMOVALS_THAT_ARE_FINE = {
    "another key of the store":
        "settings.remove('ui/scale')\n",
    "a build, which is what remove is for":
        "settings.remove(f'builds/{name}')\n",
    "something taken out of a list":
        "wanted.remove(item)\n",
    "emptying the whole test store, which the suite does to its own":
        "settings.clear()\n",
}


@pytest.mark.parametrize("spelling", sorted(REMOVALS_THE_SCAN_MUST_SEE))
def test_the_scan_sees_every_way_of_removing_a_path_key(spelling):
    assert removals_of_a_path_key(REMOVALS_THE_SCAN_MUST_SEE[spelling])


@pytest.mark.parametrize("spelling", sorted(REMOVALS_THAT_ARE_FINE))
def test_the_scan_leaves_the_other_removals_alone(spelling):
    assert removals_of_a_path_key(REMOVALS_THAT_ARE_FINE[spelling]) == []


# --- R6: one place resolves the game -------------------------------------


# The modules under nrplanner/ that may still ask the automatic route
# directly, each with the reason it is not gamepath.resolve_game() yet.
# Scripts are outside this scan altogether: they are developer tools with no
# window and no user who could have confirmed anything, which is the named
# exception AD-030 makes for them.
ASKING_THE_AUTOMATIC_ROUTE_DIRECTLY = {
    "nrplanner/gamepath.py":
        "is the resolution point; the automatic route is step 3 of its own "
        "chain",
    "nrplanner/app.py":
        "the first-run build, still on the automatic route until V2 turns "
        "it into the panel (Nachtrag XI). Delete this entry with that line",
}


def calls_to_the_automatic_route(source: str) -> list[int]:
    tree = ast.parse(source)
    return sorted(
        node.lineno for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and ((isinstance(node.func, ast.Attribute)
              and node.func.attr == "find_game_dir")
             or (isinstance(node.func, ast.Name)
                 and node.func.id == "find_game_dir"))
    )


def _modules_of_the_planner() -> dict[str, list[int]]:
    found = {}
    for path in python_modules(REPO / "nrplanner"):
        lines = calls_to_the_automatic_route(path.read_text(encoding="utf-8"))
        if lines:
            found[path.relative_to(REPO).as_posix()] = lines
    return found


def test_only_the_resolution_point_asks_where_the_game_is():
    offenders = {
        name: lines for name, lines in _modules_of_the_planner().items()
        if name not in ASKING_THE_AUTOMATIC_ROUTE_DIRECTLY
    }
    assert not offenders, (
        "these lines call gamefiles.find_game_dir() and so mean 'the folder "
        f"something found', not 'the folder the game is in': {offenders}. "
        "Ask gamepath.resolve_game() instead."
    )


def test_every_named_exception_is_still_one():
    """The list may only shrink, and it shrinks by itself.

    An entry that no longer calls the automatic route is a line V2 or V3 has
    moved on: the entry goes, and this case is what says so.
    """
    still_calling = set(_modules_of_the_planner())
    stale = set(ASKING_THE_AUTOMATIC_ROUTE_DIRECTLY) - still_calling
    assert not stale, (
        f"these modules no longer call find_game_dir(): {sorted(stale)}. "
        "Take them out of ASKING_THE_AUTOMATIC_ROUTE_DIRECTLY."
    )


def test_the_scan_sees_the_call_however_it_is_spelled():
    written_ways = (
        "from nrdata import gamefiles\ngame = gamefiles.find_game_dir()\n",
        "from nrdata.gamefiles import find_game_dir\ngame = find_game_dir()\n",
    )
    for source in written_ways:
        assert calls_to_the_automatic_route(source)


def test_the_scan_passes_a_module_that_asks_the_resolution_point():
    source = "from . import gamepath\ngame = gamepath.resolve_game()\n"

    assert calls_to_the_automatic_route(source) == []
