"""`gamefiles.steam_common_folders`, the dialog start it feeds (AK-110), and
the origin a game folder has to have (SEC-026, SEC-036).

No mutation proof here (Nutzerentscheidung 08.09.2026, T-153): a wrong
candidate list, or one `where_to_start_looking` never reaches, shows up the
moment somebody works through AK-110 by hand -- the dialog opens somewhere
that is plainly not the player's library -- so the cheaper functional check
below is the one that was asked for.

Real Steam roots and a real registry are neither built nor read here, with
the two exceptions at the end: `_steam_roots` is monkeypatched to a folder
this test owns, and `libraryfolders.vdf` is a real file written in it, so the
parsing this function relies on (`gamefiles._library_paths`, untouched) runs
for real.
"""

from __future__ import annotations

import pathlib

import pytest

from nrdata import gamefiles
from nrplanner import firstrun
from tests.test_game_dir_recognition import make_game


def a_steam_root(tmp_path: pathlib.Path, *extra_libraries: pathlib.Path
                 ) -> pathlib.Path:
    """A Steam install folder with a `libraryfolders.vdf` naming extras.

    The shape `_library_paths` reads: one `"path"` entry per extra library,
    quoted the way Steam quotes them.
    """
    root = tmp_path / "Steam"
    (root / "steamapps").mkdir(parents=True)
    lines = ['"libraryfolders"', "{"]
    for index, library in enumerate(extra_libraries):
        lines += [f'\t"{index}"', "\t{", f'\t\t"path"\t\t"{library}"', "\t}"]
    lines.append("}")
    (root / "steamapps" / "libraryfolders.vdf").write_text(
        "\n".join(lines), encoding="utf-8")
    return root


def test_the_default_library_is_offered_with_no_vdf_at_all(tmp_path,
                                                            monkeypatch):
    """A fresh Steam install: one root, no extra library, still one folder."""
    root = tmp_path / "Steam"
    (root / "steamapps").mkdir(parents=True)
    monkeypatch.setattr(gamefiles, "_steam_roots", lambda: [root])

    assert gamefiles.steam_common_folders() == [root / "steamapps" / "common"]


def test_every_library_of_every_root_is_offered_in_order(tmp_path,
                                                          monkeypatch):
    """AK-110: "Steams Bibliothekliste", not only the default library."""
    other_drive = tmp_path / "D_drive" / "SteamLibrary"
    other_drive.mkdir(parents=True)
    root = a_steam_root(tmp_path, other_drive)
    monkeypatch.setattr(gamefiles, "_steam_roots", lambda: [root])

    assert gamefiles.steam_common_folders() == [
        root / "steamapps" / "common",
        other_drive / "steamapps" / "common",
    ]


def test_a_root_that_does_not_exist_offers_nothing(tmp_path, monkeypatch):
    """A registry entry can outlive the install it named (a prior uninstall)."""
    monkeypatch.setattr(gamefiles, "_steam_roots",
                        lambda: [tmp_path / "gone"])

    assert gamefiles.steam_common_folders() == []


def test_the_dialog_starts_in_a_library_the_default_folder_is_not(
        tmp_path, monkeypatch):
    """AK-110 end to end: the library list beats the hard-coded fallback.

    Neither exists, so a bare `STEAM_COMMON` on this machine could not be
    told apart from "found nothing" -- a library folder that is built here,
    and is not `STEAM_COMMON`, can.
    """
    library = tmp_path / "SteamLibrary" / "steamapps" / "common"
    library.mkdir(parents=True)
    monkeypatch.setattr(gamefiles, "steam_common_folders", lambda: [library])

    assert firstrun.where_to_start_looking(None) == library


# --- the origin of a game folder (SEC-026, SEC-036, SEC-038) --------------

#: The two registry values `_steam_roots` reads, spelled out once more here
#: so the measurement below does not go through the function it measures.
_STEAM_KEYS = ((r"Software\Valve\Steam", "HKEY_CURRENT_USER"),
               (r"SOFTWARE\WOW6432Node\Valve\Steam", "HKEY_LOCAL_MACHINE"))


def _roots_the_registry_names() -> set[pathlib.Path]:
    import winreg

    named = set()
    for sub, hive in _STEAM_KEYS:
        try:
            with winreg.OpenKey(getattr(winreg, hive), sub) as key:
                named.add(pathlib.Path(winreg.QueryValueEx(key, "SteamPath")[0]))
        except OSError:
            continue
    return named


def test_the_real_root_list_holds_nothing_the_registry_did_not_name():
    """SEC-038: the guard measures `_steam_roots()` itself, no stub of it.

    SEC-036 is what it guards: until 13.09.2026 `C:/Program Files
    (x86)/Steam` and `C:/Steam` stood behind the registry entries as fixed
    roots, and `C:/Steam` is a folder any account on the machine may create.
    """
    assert set(gamefiles._steam_roots()) <= _roots_the_registry_names()


def test_a_registry_without_steam_offers_no_root_at_all(monkeypatch):
    """The same guard on a machine that has Steam in its registry: with the
    registry answering nothing, a fixed root would be the whole list."""
    import winreg

    def no_steam_here(*_args, **_kwargs):
        raise OSError("no Steam in this registry")

    monkeypatch.setattr(winreg, "OpenKey", no_steam_here)

    assert gamefiles._steam_roots() == []


def test_a_game_outside_every_steam_library_is_not_a_game(tmp_path,
                                                          monkeypatch):
    """SEC-026: the folder the DLL is run out of has to come from Steam's
    own list. A folder that is complete but sits elsewhere is turned down."""
    root = a_steam_root(tmp_path)
    monkeypatch.setattr(gamefiles, "_steam_roots", lambda: [root])
    elsewhere = make_game(tmp_path / "Games" / "ELDEN RING NIGHTREIGN" / "Game")

    assert not gamefiles.in_a_steam_library(elsewhere)
    assert not gamefiles.looks_like_the_game(elsewhere)


def test_a_game_in_a_library_the_vdf_names_is_a_game(tmp_path, monkeypatch):
    """A second library, named in `libraryfolders.vdf` only, counts as origin
    -- the shape of a library on another drive, built here on this one."""
    other_drive = tmp_path / "D_drive" / "SteamLibrary"
    root = a_steam_root(tmp_path, other_drive)
    monkeypatch.setattr(gamefiles, "_steam_roots", lambda: [root])
    game = make_game(other_drive / "steamapps" / "common"
                     / "ELDEN RING NIGHTREIGN" / "Game")

    assert gamefiles.in_a_steam_library(game)
    assert gamefiles.looks_like_the_game(game)


def test_a_junction_out_of_a_library_is_not_origin(tmp_path, monkeypatch):
    """The resolved folder decides, not the name it was reached by."""
    import _winapi

    root = a_steam_root(tmp_path)
    monkeypatch.setattr(gamefiles, "_steam_roots", lambda: [root])
    elsewhere = make_game(tmp_path / "Games" / "ELDEN RING NIGHTREIGN" / "Game")
    door = root / "steamapps" / "common" / "ELDEN RING NIGHTREIGN"
    door.parent.mkdir(parents=True)
    try:
        _winapi.CreateJunction(str(elsewhere.parent), str(door))
    except (AttributeError, OSError) as exc:  # not Windows, or not permitted
        pytest.skip(f"no junction could be made here: {exc}")

    assert not gamefiles.in_a_steam_library(door / "Game")
