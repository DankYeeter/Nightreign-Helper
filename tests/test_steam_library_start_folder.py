"""`gamefiles.steam_common_folders` and the dialog start it feeds (AK-110).

No mutation proof here (Nutzerentscheidung 08.09.2026, T-153): a wrong
candidate list, or one `where_to_start_looking` never reaches, shows up the
moment somebody works through AK-110 by hand -- the dialog opens somewhere
that is plainly not the player's library -- so the cheaper functional check
below is the one that was asked for.

Real Steam roots and a real registry are neither built nor read here:
`_steam_roots` is monkeypatched to a folder this test owns, and
`libraryfolders.vdf` is a real file written in it, so the parsing this
function relies on (`gamefiles._library_paths`, untouched) runs for real.
"""

from __future__ import annotations

import pathlib

from nrdata import gamefiles
from nrplanner import firstrun


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
