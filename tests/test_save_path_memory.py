"""The save file the player picked: what keeps it, and what it answers.

R10 and R11 of Nachtrag XI (AK-123 to AK-126), the caller's half of SEC-029
-- the limit itself lives in `inventory` and is asked of both routes there --
and the two endings the automatic route used to tell as one (A7).

Three of the properties here break **silently** when they break, and each of
them has a case written against a named mutation:

* a picked file that has gone missing falls back to the automatic search
  without a word, and **without being forgotten** (R10, AK-125/AK-121). A
  program that deleted the entry instead would look exactly the same on
  screen; the player would find out a week later, when the drive is back and
  he is asked all the same;
* no text of this flow carries the save's folder, which is named after the
  Steam account id (R11, AK-126). A path in a line is invisible until a
  screenshot of it is in a bug report;
* `paths/save` is written from a pick and from nothing else (AD-030). A read
  that wrote back what it found would turn "the file he chose" into "the file
  something found once", and no screen would show the difference.

The window cases go through the seam `Planner` already has for its reading
(AD-028/AD-029): what a reading answers is stated by the case, and the whole
real way is travelled -- thread, signal, generation check, window. The cases
about `read_the_save` itself go the other way round and use real files on
disk, because what that function decides is which of the three exits a real
file falls into, and a stated answer would be the thing under test.
"""

from __future__ import annotations

import ast
import dataclasses
import pathlib
import struct

import pytest
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

from nrdata import savefile
from nrplanner import app as appmod, favourites, gamepath, inventory
from tests import conftest, rendered
from tests.test_save_read_in_the_background import (READ_FUSE_S, StatedRead,
                                                    close)

REPO = pathlib.Path(__file__).resolve().parents[1]

#: A folder name of the shape the save folder really has: the Steam account
#: id, which is the thing AK-126 keeps out of every text.
AN_ACCOUNT_FOLDER = "76561198000000000"

#: The size of the saves on the machine this was written on, in bytes, both
#: accounts alike (measured 09.09.2026 over `%APPDATA%/Nightreign`). Written
#: out rather than read off the file, so that the relation below is between
#: the limit and a **measurement**, not between the limit and itself.
A_REAL_SAVE_IS_BYTES = 19_531_312


@pytest.fixture
def store():
    """The test store, cleared before and with both path keys emptied after.

    Emptied by writing an empty value, never by `remove`: a removal takes the
    group of the same name with it, which is how two of the three settings
    losses of cycles 4 and 5 happened, and the scan in
    `test_game_path_memory.py` runs over this file as well.
    """
    conftest.clear_settings()
    settings = QSettings(favourites.ORG, favourites.APP)
    yield settings
    for key in (gamepath.GAME_KEY, gamepath.SAVE_KEY):
        settings.setValue(key, "")
    settings.sync()


@pytest.fixture(scope="module")
def a_real_scan(game_data):
    """One real reading of the player's save, kept for the whole module.

    Real records rather than built ones, for the case about the exit that
    ends well: what the line says there is the count and the slot name of a
    save the planner could actually fill its slots from.
    """
    found = inventory.scan(game_data)
    if found is None:
        pytest.skip("this machine has no save to read")
    return found


def a_save_file(where: pathlib.Path, body: bytes = b"not a save") -> pathlib.Path:
    """A file in a folder named the way the real save folder is named."""
    folder = where / AN_ACCOUNT_FOLDER
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "NR0000.sl2"
    path.write_bytes(body)
    return path


def an_empty_container() -> bytes:
    """A save container a reader can open and that holds no character slot.

    Sixty-four bytes and every one of them meaningful: the magic, a member
    count of zero and a member header size that passes the SEC-002 check in
    `savefile._members`. This is the one file shape that separates the second
    exit from the third -- readable, and nothing in it.
    """
    blob = bytearray(savefile.BND4_HEADER_SIZE)
    blob[:4] = b"BND4"
    struct.pack_into("<I", blob, 0x0C, 0)
    struct.pack_into("<Q", blob, 0x20, savefile.MEMBER_FIELDS_SIZE)
    return bytes(blob)


def a_window(game_data, read):
    """A planner reading what the case stated, on the store as it stands.

    Deliberately not the helper of `test_save_read_in_the_background`: that
    one empties the settings store as it builds, and every case here is about
    a value standing in the store while the window starts.
    """
    return appmod.Planner(game_data, read_save=read)


def the_line(window) -> str:
    return window.owned_label.text()


def offers_to_find_the_save(window) -> bool:
    """Is `Find my save...` on offer?

    Asked of the widget and not of the screen: `isVisible()` is False for
    every child of a window that was never shown, and most cases here never
    show one. `isVisibleTo` is the same question without the window's own
    state mixed into it.
    """
    return window.find_save_button.isVisibleTo(window)


def names_no_path(text: str, path: pathlib.Path) -> bool:
    """Is this text free of the save's whereabouts (AK-126)?

    The folder, the full path and the parent folder's name each on their own:
    a text may name the file (`NR0000.sl2` is allowed), and it may not name
    the folder the account id is in, under any spelling that would carry it.
    """
    return (str(path) not in text
            and str(path.parent) not in text
            and path.parent.name not in text)


# -- R10: the picked file is preferred, and its loss is silent -------------


def test_a_picked_file_is_what_gets_read(store, tmp_path):
    """AK-125, first half: what he pointed at is what the next start reads."""
    picked = a_save_file(tmp_path)
    gamepath.remember_save(picked)

    assert gamepath.resolve_save() == picked


def test_a_picked_file_that_is_gone_falls_back_and_is_not_forgotten(
        store, tmp_path):
    """R10, and the mutation it is written against.

    `resolve_save` hands back None -- which is "let the automatic route
    decide", the answer `inventory.scan` has always taken -- and the entry is
    left exactly as it was. Deleting it on a failed resolution, or emptying
    it, turns the second assertion red; so does answering the dead path.
    """
    picked = a_save_file(tmp_path)
    gamepath.remember_save(picked)
    before = store.value(gamepath.SAVE_KEY, "", type=str)
    picked.unlink()

    assert gamepath.resolve_save() is None
    assert store.value(gamepath.SAVE_KEY, "", type=str) == before
    assert gamepath.remembered_save() == picked


def test_a_folder_where_the_file_was_is_not_a_save(store, tmp_path):
    """Existence is not enough: what was picked was a file.

    The case a check written as `exists()` gets wrong. A folder that has taken
    the name of the deleted file would be handed to the reader, which would
    fail on it -- and the fall-back this is all about would never run.
    """
    picked = a_save_file(tmp_path)
    picked.unlink()
    picked.mkdir()

    gamepath.remember_save(picked)

    assert gamepath.resolve_save() is None


def test_nothing_picked_is_no_answer_rather_than_a_search(store):
    """None means "decide by the automatic route", and it is not a failure."""
    assert gamepath.remembered_save() is None
    assert gamepath.resolve_save() is None


def test_a_window_whose_picked_file_is_gone_says_nothing_about_it(
        store, game_data, qapp, monkeypatch, tmp_path):
    """R10 at the window: still, no text, no dialog, and the value stands.

    The three halves of "silently", one assertion each: the reading is asked
    for the automatic route rather than for the dead file, the line is the
    ordinary one for a machine without a save, and the file dialog is not
    opened. The spy in place of the dialog is what makes the third one an
    assertion rather than an assumption -- a dialog would otherwise stand
    there and wait for a click nobody is going to give it.
    """
    picked = a_save_file(tmp_path)
    gamepath.remember_save(picked)
    before = store.value(gamepath.SAVE_KEY, "", type=str)
    picked.unlink()
    asked = []
    monkeypatch.setattr(appmod, "_pick_a_save_file",
                        lambda parent: asked.append(parent))

    read = StatedRead(None)
    window = a_window(game_data, read)
    try:
        conftest.wait_for_the_save(window)
        rendered.settle()

        assert read.save_paths == [None]
        assert the_line(window) == appmod.NO_SAVE_FOUND
        assert asked == []
        assert QApplication.activeModalWidget() is None
        assert store.value(gamepath.SAVE_KEY, "", type=str) == before
    finally:
        close(window, read)


def test_an_ordinary_read_writes_no_path(store, game_data, qapp, a_real_scan):
    """AD-030: a find by the automatic route is not a confirmation.

    Driven with a save that **arrives**, and measured: an ending that finds
    nothing never reaches the lines a write-back would be written into, so a
    case built on one is blind to the mutation this is aimed at. The
    behaviour half of the invariant; the source half is the scan below.
    """
    read = StatedRead(dataclasses.replace(a_real_scan, loadouts=[]))
    window = a_window(game_data, read)
    try:
        conftest.wait_for_the_save(window)

        assert store.value(gamepath.SAVE_KEY, "", type=str) == ""
        assert gamepath.remembered_save() is None
    finally:
        close(window, read)


def _functions_that_call(source: str, name: str) -> set[str]:
    """The functions of this source that call `name`, however it is reached."""
    tree = ast.parse(source)
    out: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for inner in ast.walk(node):
            called = inner.func if isinstance(inner, ast.Call) else None
            reached = (called.attr if isinstance(called, ast.Attribute)
                       else called.id if isinstance(called, ast.Name) else "")
            if reached == name:
                out.add(node.name)
    return out


def test_only_the_pick_writes_the_key():
    """AD-030, read off the syntax tree rather than off the cases.

    The behaviour case above can only speak about the endings it drives. A
    `remember_save` added to a branch no case reaches -- the arrival of a
    scan, say, or the automatic fall-back -- is exactly the shape this
    project keeps producing, and it would be invisible on every screen.
    """
    writers = {}
    for module in sorted((REPO / "nrplanner").rglob("*.py")):
        found = _functions_that_call(
            module.read_text(encoding="utf-8"), "remember_save")
        if found:
            writers[module.relative_to(REPO).as_posix()] = found

    assert writers == {"nrplanner/app.py": {"find_my_save"}}, (
        "paths/save may only be written where the player has just named a "
        f"file. Written here instead: {writers}"
    )


# -- R11: the three exits, and none of them names the folder ---------------


def pick_and_read(window, chosen: pathlib.Path, read, monkeypatch) -> None:
    """Press `Find my save...`, with the dialog answering `chosen`."""
    monkeypatch.setattr(appmod, "_pick_a_save_file", lambda parent: chosen)
    window.find_save_button.click()
    read.release()
    conftest.wait_for_the_save(window)
    rendered.settle()


def test_a_picked_save_with_relics_reads_as_one_always_did(
        store, game_data, qapp, monkeypatch, tmp_path, a_real_scan):
    """AK-124, first exit: the line of every other reading, and the tooltip.

    And the half of AK-126 that says where the folder may appear: on hover,
    once a save is loaded, exactly as it did before any of this existed.
    """
    chosen = a_save_file(tmp_path)
    read = StatedRead(None)
    window = a_window(game_data, read)
    try:
        conftest.wait_for_the_save(window)
        # Without its stored builds, because the arrival of a save that has
        # one writes the line of the build it took over instead -- which it
        # does on every reading and is not what this case is about.
        answer = dataclasses.replace(a_real_scan, loadouts=[])
        read.answer = answer
        pick_and_read(window, chosen, read, monkeypatch)

        assert the_line(window).startswith(
            f"{len(answer.owned)} relics in {answer.source}")
        assert not offers_to_find_the_save(window)
        assert window.owned_label.toolTip() == answer.folder
    finally:
        close(window, read)


def test_a_picked_save_without_relics_says_which_account(
        store, game_data, qapp, monkeypatch, tmp_path):
    """AK-124, second exit (S3), and R11's mutation.

    The text is the spec's, word for word, and it is the **whole** text: a
    line that appended the file it read -- the obvious kindness, and the one
    AK-126 forbids -- makes the second assertion red.
    """
    chosen = a_save_file(tmp_path)
    read = StatedRead(None)
    window = a_window(game_data, read)
    try:
        conftest.wait_for_the_save(window)
        pick_and_read(window, chosen, read, monkeypatch)

        assert the_line(window) == (
            "That save has no relics in it yet. If you play on more than one "
            "Steam account, this may be the wrong one.")
        assert names_no_path(the_line(window), chosen)
        assert offers_to_find_the_save(window)
    finally:
        close(window, read)


def test_a_picked_file_that_cannot_be_read_says_so_in_his_words_first(
        store, game_data, qapp, monkeypatch, tmp_path):
    """AK-124, third exit (S4): the player's sentence, the reason under it.

    DESIGN_REVIEW DR-006. The order is the assertion: a line that began with
    the technical reason, or that carried the `Save could not be read: `
    prefix of a reading nobody asked for, is a different line from this one.

    The reason is raised as `SaveNotReadable`, which is what `read_the_save`
    raises and, since QA-211, also what says the sentence is this program's
    own and may be shown. `savefile`'s wording is quoted here rather than
    invented so that the case stays the one the player meets.
    """
    chosen = a_save_file(tmp_path)
    read = StatedRead(None)
    window = a_window(game_data, read)
    try:
        conftest.wait_for_the_save(window)
        read.raises = inventory.SaveNotReadable("not a BND4 save container")
        pick_and_read(window, chosen, read, monkeypatch)

        assert the_line(window) == (
            "That file is not a Nightreign save this can read.\n"
            "not a BND4 save container")
        assert appmod.UNREADABLE_SAVE not in the_line(window)
        assert names_no_path(the_line(window), chosen)
        assert offers_to_find_the_save(window)
    finally:
        close(window, read)


def test_the_button_is_there_only_while_no_save_is(
        store, game_data, qapp, a_real_scan):
    """AK-123, and AK-106 for the case that comes off well.

    Not there while the reading is out either: a button that appeared for the
    length of the first read and went again at the arrival would move this
    row on every start that ends well, which is the one thing AK-106 says
    does not happen.
    """
    read = StatedRead(a_real_scan, hold=True)
    window = a_window(game_data, read)
    try:
        window.show()
        rendered.settle()
        read.began.wait(READ_FUSE_S)

        assert not offers_to_find_the_save(window)

        read.release()
        conftest.wait_for_the_save(window)
        rendered.settle()

        assert not offers_to_find_the_save(window)
    finally:
        close(window, read)


def test_the_button_appears_when_there_is_nothing_to_show(
        store, game_data, qapp):
    read = StatedRead(None)
    window = a_window(game_data, read)
    try:
        conftest.wait_for_the_save(window)
        rendered.settle()

        assert offers_to_find_the_save(window)
        assert window.find_save_button.text() == "Find my save..."
        assert window.find_save_button.toolTip() == (
            "Your save is a file called NR0000.sl2, in a folder named "
            "Nightreign under your Windows user profile. This opens there.")
    finally:
        close(window, read)


def test_the_pick_keeps_the_file_and_a_cancelled_pick_keeps_nothing(
        store, game_data, qapp, monkeypatch, tmp_path):
    """AK-125 and AD-030 at the window: the write is the confirmation.

    Both directions in one case, because they are one property: the store
    moves when he names a file and stands still when he closes the dialog.
    """
    chosen = a_save_file(tmp_path)
    read = StatedRead(None)
    window = a_window(game_data, read)
    try:
        conftest.wait_for_the_save(window)
        monkeypatch.setattr(appmod, "_pick_a_save_file", lambda parent: None)
        window.find_save_button.click()
        rendered.settle()

        assert gamepath.remembered_save() is None

        pick_and_read(window, chosen, read, monkeypatch)

        assert gamepath.remembered_save() == chosen
        assert store.value(gamepath.SAVE_KEY, "", type=str) == str(chosen)
    finally:
        close(window, read)


# -- the dialog: its texts, its filters, and where it opens ----------------


def test_the_dialog_asks_in_english_and_offers_the_three_filters():
    """AK-123 and AK-128, written out rather than read off the constants.

    An expectation taken from `appmod.SAVE_FILE_FILTERS` would follow a
    rewrite of the filters into the dialog of every player and say nothing
    while it did. The order matters as much as the entries: the first is what
    the dialog opens on.
    """
    assert appmod.CHOOSE_YOUR_SAVE == "Choose your Nightreign save file"
    assert appmod.SAVE_FILE_FILTERS.split(";;") == [
        "Nightreign save (NR*.sl2)",
        "Save file (*.sl2)",
        "All files (*)",
    ]


def test_the_dialog_opens_in_the_save_folder_when_there_is_one(
        monkeypatch, tmp_path):
    """AK-123: the start location is the actual help this dialog gives.

    Resolved, and the case says so by handing in a root that has to be
    resolved to be recognised: what the dialog is given is a path the player
    could read out, never a name that only means something to the program
    (AK-127).
    """
    roaming = tmp_path / "roaming"
    (roaming / "Nightreign").mkdir(parents=True)
    roundabout = roaming / "Nightreign" / ".." / "Nightreign"
    monkeypatch.setattr(savefile, "save_roots", lambda: [roundabout])

    assert appmod.where_saves_usually_are() == roaming / "Nightreign"


def test_the_dialog_opens_in_the_profile_when_the_folder_is_missing(
        monkeypatch, tmp_path):
    """A player who has never started the game has no `Nightreign` folder."""
    roaming = tmp_path / "roaming"
    roaming.mkdir()
    monkeypatch.setattr(savefile, "save_roots",
                        lambda: [roaming / "Nightreign"])

    assert appmod.where_saves_usually_are() == roaming


def test_the_dialog_opens_wherever_qt_would_when_neither_is_there(
        monkeypatch, tmp_path):
    """Nothing to offer is an answer, not a path made up out of pieces."""
    monkeypatch.setattr(savefile, "save_roots",
                        lambda: [tmp_path / "nowhere" / "Nightreign"])

    assert appmod.where_saves_usually_are() is None


# -- read_the_save: which exit a real file falls into ----------------------


def test_a_file_that_is_not_a_save_is_refused_with_a_reason(game_data,
                                                            tmp_path):
    """The third exit, on a real file: readable as bytes, not as a save."""
    chosen = a_save_file(tmp_path, b"this is a screenshot, not a save")

    with pytest.raises(ValueError) as raised:
        appmod.read_the_save(game_data, chosen)

    assert "BND4" in str(raised.value)
    assert names_no_path(str(raised.value), chosen)


def test_a_save_that_holds_nothing_is_no_failure(game_data, tmp_path):
    """The second exit, on a real file: it opened, and there was nothing in it.

    The difference between the two exits is a property of the file and is
    decided here, not in the window: `inventory.scan` answers None to both,
    and a caller that took its None for "unreadable" would tell a player with
    a second Steam account that his save is broken.
    """
    chosen = a_save_file(tmp_path, an_empty_container())

    assert appmod.read_the_save(game_data, chosen) is None


def test_no_file_at_that_place_says_so_without_saying_where(game_data,
                                                            tmp_path):
    """An OSError writes the whole path into its message; this one does not.

    The case AK-126 would lose to the operating system. The window prints
    what comes out of here under S4, and `strerror` is the half of an
    `OSError` that carries no path.
    """
    chosen = a_save_file(tmp_path)
    chosen.unlink()

    with pytest.raises(ValueError) as raised:
        appmod.read_the_save(game_data, chosen)

    assert names_no_path(str(raised.value), chosen)
    assert str(raised.value)


def test_nothing_picked_reads_the_way_it_always_did(game_data, monkeypatch):
    """No path in, no path down: the automatic route is untouched by all this."""
    asked = []
    monkeypatch.setattr(inventory, "scan",
                        lambda data, *rest: asked.append(rest))

    assert appmod.read_the_save(game_data) is None
    assert asked == [()]


# -- SEC-029: the size is looked at before the file is -------------------


def test_a_file_too_large_to_be_a_save_is_not_read(game_data, monkeypatch,
                                                   tmp_path):
    """SEC-029. The refusal comes before anything is read, and it is loud.

    The file is made at the real limit rather than at a lowered one, and
    nothing here is allowed to read it: a scan that ran would be a scan of a
    file the finding is about. The spy is what makes that an assertion.
    """
    chosen = a_save_file(tmp_path)
    with open(chosen, "wb") as handle:
        handle.truncate(inventory.LARGEST_SAVE_TO_READ + 1)
    monkeypatch.setattr(inventory, "scan",
                        lambda *args, **rest: pytest.fail(
                            "the file was read before its size was looked at"))

    with pytest.raises(ValueError) as raised:
        appmod.read_the_save(game_data, chosen)

    assert "MB" in str(raised.value)
    assert names_no_path(str(raised.value), chosen)


def test_the_automatic_route_is_held_to_the_same_limit(game_data, monkeypatch,
                                                      tmp_path):
    """SEC-029's other half, and the one no dialog stands in front of.

    Nobody picked this file: it was lying in the profile folder under the
    name the game uses, and the automatic route hands it straight to
    `_read_settled`. The limit therefore cannot live in the caller alone, and
    this case is the one that says so -- it never goes near
    `_refuse_a_file_no_save_can_be`.

    The spy is what makes "not read" an assertion rather than a hope:
    `savefile._members` is the first thing the bytes are handed to, so a run
    that reached it read the whole file first.
    """
    huge = a_save_file(tmp_path)
    with open(huge, "wb") as handle:
        handle.truncate(inventory.LARGEST_SAVE_TO_READ + 1)
    monkeypatch.setattr(savefile, "find_saves", lambda: [huge])
    monkeypatch.setattr(savefile, "_members",
                        lambda blob: pytest.fail(
                            "the file was read whole before its size was "
                            "looked at"))

    with pytest.raises(ValueError) as raised:
        appmod.read_the_save(game_data)

    assert "far larger than any save this game writes" in str(raised.value)
    assert names_no_path(str(raised.value), huge)


def test_a_save_of_the_ordinary_size_is_read(game_data, monkeypatch,
                                             tmp_path):
    """The other side of the limit, and the one that would hurt.

    A limit set below a real save would refuse every player his own file, and
    the case above would stay green while it did. The size is the measured
    one, written out; the file itself is a container with nothing in it, so
    what is asserted is that the size did not stop it.
    """
    chosen = a_save_file(tmp_path)
    with open(chosen, "wb") as handle:
        handle.write(an_empty_container())
        handle.truncate(A_REAL_SAVE_IS_BYTES)

    assert appmod.read_the_save(game_data, chosen) is None


def test_the_limit_is_far_above_a_real_save():
    """L-001: the figure carries its recipe, and the recipe is a measurement.

    256 MiB against 19 531 312 bytes measured on this installation -- both
    accounts, 09.09.2026 -- is a factor of 13,7. Pinned as a relation to the
    measurement rather than as the number itself, so that raising it stays a
    decision and lowering it below a save cannot pass unnoticed.
    """
    assert inventory.LARGEST_SAVE_TO_READ == 256 * 1024 * 1024
    assert inventory.LARGEST_SAVE_TO_READ > 13 * A_REAL_SAVE_IS_BYTES


# -- A7: a save that was found and could not be read is not "none found" --


def test_a_save_that_cannot_be_read_is_not_reported_as_no_save(game_data,
                                                               monkeypatch,
                                                               tmp_path):
    """The A7 break DR-005 named: one unreadable save, and the window said
    `No save file found.`

    A file exists, it carries the name the game gives its save, and it cannot
    be read. "Nothing was found" is not a missing answer there but a wrong
    one, and a wrong one the player acts on: he goes looking for a save he
    already has. What comes out of here instead is the reason, which the
    window puts behind `Save could not be read: ` (`UI_SPEC` T-141 §9 (g)).
    """
    monkeypatch.setattr(savefile, "find_saves",
                        lambda: [a_save_file(tmp_path,
                                             b"this is a screenshot")])

    with pytest.raises(ValueError) as raised:
        appmod.read_the_save(game_data)

    assert "BND4" in str(raised.value)


def test_the_reason_for_an_unopenable_save_carries_no_path(game_data,
                                                           monkeypatch,
                                                           tmp_path):
    """AK-126 on the new way out: an `OSError` writes the path into itself.

    The one failure whose message is written by the operating system rather
    than by this program, and the folder it would name is the one named after
    the Steam account id. A folder standing where the file should be is the
    cheapest way to a real `OSError` from a real read.
    """
    folder = tmp_path / AN_ACCOUNT_FOLDER / "NR0000.sl2"
    folder.mkdir(parents=True)
    monkeypatch.setattr(savefile, "find_saves", lambda: [folder])

    with pytest.raises(ValueError) as raised:
        appmod.read_the_save(game_data)

    assert str(raised.value)
    assert names_no_path(str(raised.value), folder)


def test_one_unreadable_save_does_not_hide_a_good_one(game_data, a_real_scan,
                                                      monkeypatch, tmp_path):
    """The other side of the same rule, and the reason it is not a `raise`
    at the first bad file.

    Two files, the good one older than the bad one, so the bad one is read
    first: a scan that gave up where it stumbled would answer nothing at all.
    The good one is the player's own save, because "good" here has to mean a
    file this reader really gets an inventory out of.
    """
    good = savefile.find_saves()[0]
    bad = a_save_file(tmp_path, b"this is a screenshot")
    monkeypatch.setattr(savefile, "find_saves", lambda: [good, bad])

    found = appmod.read_the_save(game_data)

    assert found is not None, "the bad file took the good one down with it"
    assert found.owned


# -- AK-127 and AK-128: what these texts may not say ----------------------


#: The words no text of this flow may carry (`UI_SPEC` section 7, AK-127),
#: as the first-run guard lists them. The file extension is on that list with
#: its two exceptions written into the rule itself -- S1 and the file filter
#: -- so it is asked about separately below rather than left off here.
FORBIDDEN = ("regulation.bin", "steamapps", "libraryfolders.vdf",
             "AppData", "Steam ID", "account id", "snapshot", "cache",
             "param", "extract", "%")


def the_texts_of_this_flow() -> dict[str, str]:
    """Every fixed text `Find my save...` can put in front of the player."""
    return {
        "S1": appmod.FIND_MY_SAVE_TOOLTIP,
        "S2": appmod.CHOOSE_YOUR_SAVE,
        "S3": appmod.CHOSEN_SAVE_IS_EMPTY,
        "S4": appmod.CHOSEN_SAVE_UNREADABLE,
        "S5": appmod.NO_SAVE_FOUND,
        "the button": appmod.FIND_MY_SAVE,
        "the filters": appmod.SAVE_FILE_FILTERS,
    }


@pytest.mark.parametrize("name", sorted(the_texts_of_this_flow()))
def test_no_text_of_this_flow_says_a_forbidden_word(name):
    """AK-127. The words that would name the machinery instead of the file.

    A path never appears here as a variable either, which is what `%` on the
    list is for: what the dialog opens on is resolved, and what a player is
    shown is a place he can read out.
    """
    text = the_texts_of_this_flow()[name]

    assert not [word for word in FORBIDDEN if word.lower() in text.lower()]


def test_the_file_type_is_named_only_where_it_helps():
    """AK-127's two exceptions, and they are the whole of them.

    The extension belongs in the sentence that tells him what to look for and
    in the filter that shows it to him. Anywhere else it is the program
    talking about itself, and the positive control is above it: the two texts
    that may carry it do carry it, so a case that finds none is a case that
    has stopped looking.
    """
    named = {name for name, text in the_texts_of_this_flow().items()
             if ".sl2" in text.lower()}

    assert named == {"S1", "the filters"}
