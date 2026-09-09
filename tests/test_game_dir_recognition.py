"""Recognising a game folder, and finding one around the folder picked.

The Qt-free half of AD-030: `looks_like_the_game` (stage 1, AK-112),
`is_named_nightreign` (stage 2, AK-113), `search_from` (UI_SPEC 4.2, AK-111)
and `find_game_dir` (the Steam-registry route, SEC-031). Nothing here builds
a window -- the panel that shows E1 and W1 is V2, and its cases live in
`test_first_run_panel.py`.

Three of the properties held here would break silently, so each names the
mutation that has to kill it:

* the ceiling on `regulation.bin` (SEC-028). A missing ceiling is invisible
  until somebody points the program at a folder with a twenty-gigabyte file
  in it, and then it is a start that never finishes;
* the search does not step through a junction (SEC-030). Without the rule
  the search leaves the tree the user picked -- and can walk in a circle --
  and every case that only counts directories stays green.
* `find_game_dir` asks `looks_like_the_game` rather than the presence of
  `regulation.bin` alone (SEC-031). Without it, a folder that only has that
  one file goes straight to the build, and nobody notices until it happens.
* `find_game_dir` asks about nothing Steam did not name (SEC-031, second
  half). The six bare-drive candidates that used to stand beside the library
  list would come back unremarked: a route that takes a folder off a drive
  letter and runs a library out of it looks exactly like one that does not.

A folder is built by hand rather than looked for on this machine: the three
files stage 1 asks about are three empty files and a byte, and a case that
needs the installed game could not run on a machine without one.
"""

from __future__ import annotations

import os
import pathlib

import pytest

from nrdata import bhd5, gamefiles, oodle

# One name out of each of the two lists the program itself carries, so a case
# that builds a folder builds the same folder the program would accept.
AN_ARCHIVE = f"{sorted(bhd5.ARCHIVE_KEYS)[0]}.bhd"
AN_OODLE_DLL = oodle._DLL_NAMES[0]


def make_game(folder: pathlib.Path,
              regulation_bytes: int = 16) -> pathlib.Path:
    """A folder that passes stage 1, with a regulation.bin of a given size."""
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / "regulation.bin").open("wb") as handle:
        handle.truncate(regulation_bytes)
    (folder / AN_ARCHIVE).write_bytes(b"")
    (folder / AN_OODLE_DLL).write_bytes(b"")
    return folder


# --- stage 1 -------------------------------------------------------------


def test_regulation_alone_is_not_a_game(tmp_path):
    (tmp_path / "regulation.bin").write_bytes(b"x")

    assert not gamefiles.looks_like_the_game(tmp_path)


def test_regulation_and_an_archive_are_not_a_game(tmp_path):
    (tmp_path / "regulation.bin").write_bytes(b"x")
    (tmp_path / AN_ARCHIVE).write_bytes(b"")

    assert not gamefiles.looks_like_the_game(tmp_path)


def test_all_three_together_are_a_game(tmp_path):
    make_game(tmp_path)

    assert gamefiles.looks_like_the_game(tmp_path)


def test_the_dll_alone_is_not_a_game(tmp_path):
    """The third condition is a condition, not a bonus."""
    (tmp_path / "regulation.bin").write_bytes(b"x")
    (tmp_path / AN_OODLE_DLL).write_bytes(b"")

    assert not gamefiles.looks_like_the_game(tmp_path)


def test_an_empty_regulation_is_not_a_game(tmp_path):
    make_game(tmp_path, regulation_bytes=0)

    assert not gamefiles.looks_like_the_game(tmp_path)


def test_a_folder_that_is_not_there_is_not_a_game(tmp_path):
    assert not gamefiles.looks_like_the_game(tmp_path / "gone")


def test_a_path_that_cannot_exist_is_not_a_game(tmp_path):
    """A stored path with a null byte raises out of pathlib, not upwards."""
    assert not gamefiles.looks_like_the_game(f"{tmp_path}\0here")


def test_a_regulation_at_the_ceiling_is_still_a_game(tmp_path):
    """SEC-028: the ceiling rejects what is over it, not what is at it."""
    make_game(tmp_path, regulation_bytes=gamefiles.MAX_REGULATION_BYTES)

    assert gamefiles.looks_like_the_game(tmp_path)


def test_a_regulation_over_the_ceiling_is_not_a_game(tmp_path):
    """SEC-028, the killing case: rejected before anything reads the file.

    Dies with the ceiling removed, and with `<=` widened to anything the file
    below satisfies. The size is one byte over the constant so that no other
    limit on this machine can be what rejects it.
    """
    make_game(tmp_path, regulation_bytes=gamefiles.MAX_REGULATION_BYTES + 1)

    assert not gamefiles.looks_like_the_game(tmp_path)


def test_the_ceiling_leaves_the_measured_installation_room():
    """The recipe of the number, as a case rather than as a comment.

    1 974 720 bytes measured on this installation (08.09.2026, SEC-028,
    sample of one). The ceiling is not that measurement -- it is two orders
    of magnitude above it, so a game that grows does not turn into a folder
    the program refuses to look at.
    """
    measured_here = 1_974_720

    assert gamefiles.MAX_REGULATION_BYTES > 30 * measured_here


# --- find_game_dir asks the same predicate (SEC-031) ---------------------

# A name that cannot collide with a real install directory anywhere on the
# machine running the suite, so no folder this suite did not build can turn
# up in a "rejected" case below and make it pass for the wrong reason.
_SENTINEL_INSTALL_DIR = "NRHELPER-TEST-SEC031-INSTALL-DIR"


def _the_only_candidate(tmp_path: pathlib.Path, monkeypatch) -> pathlib.Path:
    """Wire find_game_dir's Steam search down to one controlled folder.

    Every candidate is built from INSTALL_DIR under a library, so patching
    the install directory and both library helpers steers all of them, not
    just the one this test cares about.
    """
    monkeypatch.setattr(gamefiles, "INSTALL_DIR", _SENTINEL_INSTALL_DIR)
    root = tmp_path / "steam"
    root.mkdir()
    library = tmp_path / "lib"
    monkeypatch.setattr(gamefiles, "_steam_roots", lambda: [root])
    monkeypatch.setattr(gamefiles, "_library_paths", lambda _root: [library])
    return library / "common" / _SENTINEL_INSTALL_DIR / "Game"


def test_find_game_dir_finds_a_folder_that_passes_all_three_conditions(
        tmp_path, monkeypatch):
    game = make_game(_the_only_candidate(tmp_path, monkeypatch))

    assert gamefiles.find_game_dir() == game


def test_find_game_dir_rejects_regulation_bin_alone(tmp_path, monkeypatch):
    """SEC-031, the killing case: existence used to be the whole check.

    Dies the moment the loop goes back to
    `(path / "regulation.bin").exists()` -- the folder below satisfies that
    and nothing else, and the old find_game_dir handed it straight to the
    build without ever asking looks_like_the_game.
    """
    candidate = _the_only_candidate(tmp_path, monkeypatch)
    candidate.mkdir(parents=True)
    (candidate / "regulation.bin").write_bytes(b"x")

    assert gamefiles.find_game_dir() is None


def test_find_game_dir_rejects_an_empty_regulation(tmp_path, monkeypatch):
    """SEC-031's other still value: an empty file also `.exists()`."""
    candidate = _the_only_candidate(tmp_path, monkeypatch)
    make_game(candidate, regulation_bytes=0)

    assert gamefiles.find_game_dir() is None


def test_find_game_dir_rejects_a_regulation_over_the_ceiling(
        tmp_path, monkeypatch):
    candidate = _the_only_candidate(tmp_path, monkeypatch)
    make_game(candidate, regulation_bytes=gamefiles.MAX_REGULATION_BYTES + 1)

    assert gamefiles.find_game_dir() is None


def test_find_game_dir_accepts_a_regulation_at_the_ceiling(
        tmp_path, monkeypatch):
    """The control for the case above: the ceiling itself still passes."""
    candidate = _the_only_candidate(tmp_path, monkeypatch)
    game = make_game(candidate, regulation_bytes=gamefiles.MAX_REGULATION_BYTES)

    assert gamefiles.find_game_dir() == game


def test_find_game_dir_finds_nothing_when_no_candidate_exists(
        tmp_path, monkeypatch):
    _the_only_candidate(tmp_path, monkeypatch)  # never created on disk

    assert gamefiles.find_game_dir() is None


def test_find_game_dir_asks_about_nothing_steam_did_not_name(tmp_path,
                                                             monkeypatch):
    """SEC-031, second half: the six bare-drive candidates are gone.

    The killing case for the decision of 09.09.2026. Put the fallback back
    and this counts seven folders instead of one, six of them
    `?:/SteamLibrary/steamapps/common/.../Game` -- the one candidate an
    attacker could fill without being in the user's account already, on the
    one route that has no window between the find and the library it runs.

    Asked as the list of folders the predicate is put to, not as the answer:
    a candidate that happens not to exist on this machine today is still a
    candidate, and a case that only read the answer would be green on any
    machine with nothing plugged in.
    """
    asked: list[pathlib.Path] = []

    def watched(path) -> bool:
        asked.append(pathlib.Path(path))
        return False

    candidate = _the_only_candidate(tmp_path, monkeypatch)
    monkeypatch.setattr(gamefiles, "looks_like_the_game", watched)

    assert gamefiles.find_game_dir() is None
    assert asked == [candidate]


# --- stage 2 -------------------------------------------------------------


@pytest.mark.parametrize("folder, named", [
    (r"D:\SteamLibrary\steamapps\common\ELDEN RING NIGHTREIGN\Game", True),
    (r"D:\games\elden ring nightreign\Game", True),
    (r"D:\SteamLibrary\steamapps\common\ELDEN RING\Game", False),
    (r"D:\Nightreign", True),
    (r"D:\NIGHTREIGN\a\b\c\Game", False),
    (r"D:\NIGHTREIGN\a\b\Game", True),
])
def test_the_name_is_read_off_the_folder_and_three_levels_above(folder, named):
    """AK-113: the found folder and its three parent levels, case ignored.

    The fifth case is what the depth is for: four levels up is out of reach,
    and the same tree one level shorter is not.
    """
    assert gamefiles.is_named_nightreign(
        pathlib.PureWindowsPath(folder)) is named


def test_the_name_it_looks_for_is_the_one_the_install_folder_carries():
    """The word is derived from INSTALL_DIR, not written out beside it."""
    assert gamefiles.IDENTITY_WORD == "NIGHTREIGN"
    assert gamefiles.IDENTITY_WORD in gamefiles.INSTALL_DIR


# --- the search around the picked folder ---------------------------------


def test_the_folder_the_user_picked_is_the_game_itself(tmp_path):
    game = make_game(tmp_path / "Game")

    assert gamefiles.search_from(game) == game.resolve()


def test_one_level_down_is_found(tmp_path):
    """The case UI_SPEC 4.2 is written for: Steam opens the folder above."""
    game = make_game(tmp_path / gamefiles.INSTALL_DIR / "Game")

    assert gamefiles.search_from(tmp_path / gamefiles.INSTALL_DIR) \
        == game.resolve()


def test_three_levels_down_are_found(tmp_path):
    """steamapps -> common -> ELDEN RING NIGHTREIGN -> Game."""
    game = make_game(tmp_path / "steamapps" / "common"
                     / gamefiles.INSTALL_DIR / "Game")

    assert gamefiles.search_from(tmp_path / "steamapps") == game.resolve()


def test_four_levels_down_are_not_found(tmp_path):
    """The depth is a limit. Dies the moment SEARCH_DEPTH becomes 4."""
    make_game(tmp_path / "a" / "steamapps" / "common"
              / gamefiles.INSTALL_DIR / "Game")

    assert gamefiles.search_from(tmp_path / "a") is None


def test_a_subfolder_of_the_game_finds_the_game(tmp_path):
    """One level up, for somebody who was already inside his install."""
    game = make_game(tmp_path / "Game")
    (game / "sfx").mkdir()

    assert gamefiles.search_from(game / "sfx") == game.resolve()


def test_two_levels_up_are_found(tmp_path):
    game = make_game(tmp_path / "Game")
    (game / "sfx" / "deep").mkdir(parents=True)

    assert gamefiles.search_from(game / "sfx" / "deep") == game.resolve()


def test_three_levels_up_are_not_found(tmp_path):
    """Dies the moment SEARCH_PARENTS becomes 3."""
    game = make_game(tmp_path / "Game")
    (game / "sfx" / "deep" / "deeper").mkdir(parents=True)

    assert gamefiles.search_from(game / "sfx" / "deep" / "deeper") is None


def test_the_shallowest_hit_wins(tmp_path):
    """Two installs below one folder: the one nearer the user's pick."""
    near = make_game(tmp_path / "one" / "Game")
    make_game(tmp_path / "two" / "deeper" / "Game")

    assert gamefiles.search_from(tmp_path / "one") == near.resolve()


def test_of_two_hits_at_the_same_depth_the_newer_wins(tmp_path):
    older = make_game(tmp_path / "a" / "Game")
    newer = make_game(tmp_path / "b" / "Game")
    os.utime(older, (1_000_000, 1_000_000))
    os.utime(newer, (2_000_000, 2_000_000))

    assert gamefiles.search_from(tmp_path) == newer.resolve()


def test_a_folder_with_nothing_in_it_is_not_recognised(tmp_path):
    assert gamefiles.search_from(tmp_path) is None


# --- the two budgets ------------------------------------------------------

# One more than the budget allows, so the walk has to stop inside the level
# rather than at the end of it.
MORE_FOLDERS_THAN_THE_BUDGET = 500


def crowd(folder: pathlib.Path, how_many: int) -> None:
    """Folders that hold nothing, named so they are walked first."""
    folder.mkdir(parents=True, exist_ok=True)
    for number in range(how_many):
        (folder / f"aaa{number:04d}").mkdir()


def test_the_search_stops_after_four_hundred_directories(tmp_path):
    """AK-111, as a count against the literal.

    Dies with the count removed and with MAX_DIRECTORIES raised: the tree
    below holds 501 directories, so a search without a budget visits them
    all.
    """
    crowd(tmp_path, MORE_FOLDERS_THAN_THE_BUDGET)

    found, visited = gamefiles._search_within_budget(tmp_path)

    assert found is None
    assert visited == 400


def test_a_game_behind_the_budget_is_not_found(tmp_path):
    """A drive root ends in "not recognised", not in a search of the disk."""
    crowd(tmp_path, MORE_FOLDERS_THAN_THE_BUDGET)
    make_game(tmp_path / "zzz" / "Game")

    assert gamefiles.search_from(tmp_path) is None


def test_the_search_stops_when_its_seconds_are_up(tmp_path, monkeypatch):
    """The second budget, driven by a clock of the test's own.

    No wall-clock bound is asserted anywhere: the case hands the search a
    clock that jumps, so what is measured is the rule and not the machine.
    Dies with the deadline removed -- the game two levels down is there and
    is found without it, which the case below shows.
    """
    make_game(tmp_path / "a" / "Game")
    ticks = iter([0.0, 0.5, 1.0, 3.0] + [9.0] * 100)
    monkeypatch.setattr(gamefiles, "_monotonic", lambda: next(ticks))

    assert gamefiles.search_from(tmp_path) is None


def test_the_same_tree_is_found_when_the_clock_does_not_jump(tmp_path):
    """The control for the case above, on the same tree."""
    game = make_game(tmp_path / "a" / "Game")

    assert gamefiles.search_from(tmp_path) == game.resolve()


# --- junctions (SEC-030) --------------------------------------------------


def make_junction(link: pathlib.Path, target: pathlib.Path) -> None:
    """A directory junction, the form Windows makes without a privilege."""
    import _winapi

    _winapi.CreateJunction(str(target), str(link))


needs_junctions = pytest.mark.skipif(
    not hasattr(__import__("_winapi"), "CreateJunction"),
    reason="junctions are a Windows thing, and Windows is the target",
)


@needs_junctions
def test_the_search_does_not_step_through_a_junction(tmp_path):
    """SEC-030, the killing case.

    The game sits outside the tree the user picked and is reachable only
    through a junction inside it. Dies the moment the reparse check is
    dropped: the search then walks into `elsewhere` and hands back a folder
    the user never saw.
    """
    outside = make_game(tmp_path / "elsewhere" / "Game")
    picked = tmp_path / "picked"
    picked.mkdir()
    make_junction(picked / "door", outside.parent)

    assert gamefiles.search_from(picked) is None


@needs_junctions
def test_the_same_folder_is_found_when_it_is_reached_by_a_real_folder(
        tmp_path):
    """The control: what the junction hides is found through a real path."""
    game = make_game(tmp_path / "picked" / "here" / "Game")

    assert gamefiles.search_from(tmp_path / "picked") == game.resolve()


@needs_junctions
def test_the_answer_is_the_real_folder_when_the_pick_was_a_junction(tmp_path):
    """SEC-030, the other half: the result is held through resolve().

    A junction the user picked himself is a folder he chose, so it is
    searched -- but what is remembered and read afterwards is the folder it
    stands for, not the door to it. Dies the moment the result is handed back
    unresolved.
    """
    real = make_game(tmp_path / "real" / "Game")
    picked = tmp_path / "picked"
    make_junction(picked, real)

    found = gamefiles.search_from(picked)

    assert found == real.resolve()
    assert found != picked


@needs_junctions
def test_a_junction_that_points_at_itself_does_not_hang_the_search(tmp_path):
    """A loop is the second half of SEC-030, and costs nothing extra."""
    picked = tmp_path / "picked"
    picked.mkdir()
    make_junction(picked / "round", picked)

    found, visited = gamefiles._search_within_budget(picked)

    assert found is None
    assert visited < gamefiles.MAX_DIRECTORIES
