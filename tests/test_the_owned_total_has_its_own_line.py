"""The total the player owns has a line of its own (`UI_SPEC` T-178, AK-250 to AK-252).

**What went wrong, and what these cases hold shut.** The number was on the
screen all along -- `309 relics in USER_DATA000` -- in `owned_label`, a line
ten different messages write into, and the first `Load equipped` wiped it
(QA-201, and a `power-user` who gave up looking for it). So this is not a new
number: it is the same number, in a widget exactly one function writes.

**Every case here is driven through the window's real way in.** The stock
arrives the way a save arrives -- through the reader's seam, into
`_on_save_read`, out of `_the_save_has_been_read` -- and the four messages
that used to take the line over are produced by pressing `Load equipped`
against the four stocks that produce them. Nothing calls the writer directly;
a case that did would be green against a window that never calls it either.

**The stock is built here rather than read from the player's save.** These
cases are about counting and about who writes which line, so the count has to
be a literal the case chose: one relic for the singular, three for the plural.
`SaveScan` is what crosses the reader's thread boundary (AD-006.8), so a
hand-built one travels every step a read one does, from `inventory.build`
onwards, and no case here needs a machine with a save on it.

The wording is transcribed out of `UI_SPEC` T-178 §4 rather than imported from
`nrplanner.app`: a test that compared the label against the constant behind it
would be green whatever either of them said.
"""

from __future__ import annotations

import dataclasses
import re

import pytest
from PySide6.QtCore import Qt

from nrdata import savefile
from nrplanner import app as appmod, inventory
from tests import conftest, rendered
from tests.test_save_read_in_the_background import StatedRead, a_window, close

# --- the wording, transcribed out of UI_SPEC T-178 §4 ---------------------

ONE = "You own 1 relic in total."
THREE = "You own 3 relics in total."
TOOLTIP = ("Counted from your save {source}. The number beside a relic slot "
           "counts only the relics that fit that slot.")

#: The save name and the folder a hand-built scan carries. The folder holds
#: the Steam account id in a real save, which is why it is never on the face
#: of the window -- so a made-up one is used here too.
SOURCE = "USER_DATA000"
FOLDER = r"C:\Users\Someone\AppData\Roaming\Nightreign\76561190000000000"

#: Room enough that the density check of `Inventory` (SEC-022) has nothing to
#: say about three records. It is a property of the save's bytes and not of
#: this test, so it is given generously and never asserted on.
SLOT_BYTES = 1_000_000


def a_scan_of(data: dict, how_many: int, *, loadouts=(), loadout_error=""):
    """A character slot holding `how_many` relics, as it comes off the disk.

    The relic ids are taken from the dataset because `inventory.build` drops a
    record the dataset does not name: an inventory built out of invented ids
    would count zero however many records went in.
    """
    ids = [relic["id"] for relic in data["relics"][:how_many]]
    assert len(ids) == how_many, "the dataset has fewer relics than that"
    owned = [savefile.OwnedRelic(relic_id=relic_id, effect_ids=[],
                                 offset=100 * position, curse_ids=[])
             for position, relic_id in enumerate(ids)]
    return inventory.SaveScan(
        source=SOURCE, folder=FOLDER, source_bytes=SLOT_BYTES, owned=owned,
        handle_of={record.offset: 1 + index
                   for index, record in enumerate(owned)},
        loadouts=list(loadouts), loadout_error=loadout_error)


def the_line(window) -> str:
    """The line of its own, as a player reads it."""
    return window.owned_total_label.text()


def the_note(window) -> str:
    """The shared line under it, which every message takes over."""
    return window.owned_label.text()


def a_window_with(game_data, how_many: int, **kw):
    """A planner that has read a save holding `how_many` relics."""
    read = StatedRead(a_scan_of(game_data, how_many, **kw))
    window = a_window(game_data, read)
    conftest.wait_for_the_save(window)
    rendered.settle(2)
    return window, read


# -- AK-250: the line belongs to the number --------------------------------

def a_vessel_id_in_the_list(window) -> int:
    """The id of a vessel the chalice list really offers, skipping captions."""
    for row in range(window.chalice_list.count()):
        vessel = window.chalice_list.item(row).data(Qt.UserRole)
        if vessel is not None:
            return vessel["id"]
    raise AssertionError("the chalice list offers no vessel at all")


def test_the_total_stands_through_every_message_that_takes_the_note(game_data,
                                                                    qapp):
    """AK-250. The four endings of `Load equipped`, one after another.

    Each of them writes into `owned_label`, and each of them used to be the
    end of the number: that line is where it stood. Here the number is asked
    for again after every one of them, against a literal.

    **The positive control is the second assertion of each round.** The
    message really has to arrive in the note -- otherwise this case presses a
    button that does nothing and the line it checks was never in danger. It is
    the same control the spec asks for against today's fassung, where the note
    *is* where the number lives: there, the arrival of any of these four
    sentences is the moment the number disappears.
    """
    window, read = a_window_with(game_data, 3)
    try:
        assert the_line(window) == THREE, "the premise: the number is up"
        assert "3 relics in" in the_note(window), "and the note carries it too"
        hero = window.current_hero()
        vessel = a_vessel_id_in_the_list(window)

        endings = [
            # `This save stores no equipped loadout for <hero>.`
            ([], "", f"stores no equipped loadout for {hero['name']}"),
            # `This save's stored builds could not be read: ...`
            ([], "the table ran off the end of the slot",
             "stored builds could not be read: the table ran off the end"),
            # `<hero> has vessel <id> equipped, which is not in this list.`
            ([inventory.EquippedLoadout(hero_id=hero["id"], vessel_id=999999,
                                        selected=True, relics=[])], "",
             f"{hero['name']} has vessel 999999 equipped"),
            # `Loaded <hero> — ...`
            ([inventory.EquippedLoadout(hero_id=hero["id"], vessel_id=vessel,
                                        selected=True, relics=[])], "",
             f"Loaded {hero['name']}"),
        ]
        for loadouts, error, expected in endings:
            window.owned.loadouts = list(loadouts)
            window.owned.loadout_error = error

            window.load_equipped()
            rendered.settle(2)

            assert expected in the_note(window), "the message really landed"
            assert the_line(window) == THREE, expected
    finally:
        close(window, read)


def test_nothing_but_the_one_function_writes_the_line(game_data, qapp):
    """AK-250 as a property of the module, not of the four presses above.

    A fifth message added to `owned_label` tomorrow would pass the case above
    untouched. This one says the same thing where it can be said once and for
    all: `owned_total_label` is written in exactly one place, and every ending
    of a read reaches that place.
    """
    source = (appmod.__file__).replace(".pyc", ".py")
    with open(source, encoding="utf-8") as handle:
        lines = handle.read().splitlines()

    writes = [line.strip() for line in lines
              if "owned_total_label.setText(" in line
              or "owned_total_label.clear(" in line]
    assert len(writes) == 2, writes  # the filled branch and the empty one
    inside = [line for line in lines
              if "_say_how_many_relics_are_owned()" in line]
    assert len(inside) == 1, inside  # called from one place: the one ending
    assert "self._say_how_many_relics_are_owned()" in inside[0]


# -- AK-251: the number names its unit and its scope ------------------------

@pytest.mark.parametrize("how_many, expected", [(1, ONE), (3, THREE)])
def test_the_line_says_what_is_counted_and_out_of_which_save(
        game_data, qapp, how_many, expected):
    """AK-251. Singular and plural, the tooltip, and the note it agrees with.

    `1 relics` was on screen once, which is why the count goes through
    `_relic_count` and why the one-relic case is here at all.
    """
    window, read = a_window_with(game_data, how_many)
    try:
        assert the_line(window) == expected
        assert (window.owned_total_label.toolTip()
                == TOOLTIP.format(source=SOURCE))
        assert window.owned_total_label.textFormat() == Qt.PlainText

        # The same number the note names, in the same session: two ways of
        # counting that drift apart are worse than one.
        in_the_note = re.match(r"(\d+) relics? in ", the_note(window))
        assert in_the_note, the_note(window)
        assert f"You own {in_the_note.group(1)} relic" in the_line(window)
        assert str(how_many) == in_the_note.group(1)
    finally:
        close(window, read)


def test_a_save_name_that_looks_like_markup_is_shown_as_the_name_it_is(
        game_data, qapp):
    """AK-251's last clause, and SEC-013's rule for a tooltip.

    A save is a file somebody may have been handed. The name goes into a
    tooltip, and a tooltip decides for itself whether what it is given is
    markup -- there is no text format to set on one.
    """
    read = StatedRead(dataclasses.replace(a_scan_of(game_data, 1),
                                          source="<img src='//host/share/x'>"))
    window = a_window(game_data, read)
    try:
        conftest.wait_for_the_save(window)
        assert "&lt;img" in window.owned_total_label.toolTip()
        assert "<img" not in window.owned_total_label.toolTip()
    finally:
        close(window, read)


# -- AK-252: nothing at all until something has been read -------------------

def the_left_pane(window):
    return window.panes.widget(0)


def where_everything_in_the_left_pane_sits(window) -> dict:
    """Every control of the left pane by name, with its place and its size.

    Read off the rendered widgets and mapped into the window, so a row that
    moves because something above it grew is a difference here even when its
    own geometry is unchanged.
    """
    pane = the_left_pane(window)
    out = {}
    for name in ("hero_name_label", "chalice_list", "deep_check",
                 "rescan_button", "import_button", "owned_label",
                 "level_label", "level_slider", "level_note"):
        widget = getattr(window, name)
        out[name] = (widget.mapTo(window, widget.rect().topLeft()),
                     widget.size())
    out["#pane"] = (pane.mapTo(window, pane.rect().topLeft()), pane.size())
    return out


@pytest.mark.parametrize("state", ["never answers", "no save", "unreadable",
                                   "chosen save with nothing in it"])
def test_the_line_stays_empty_until_there_is_a_stock(game_data, qapp, state):
    """AK-252, all four states. Empty means empty: no 0, no ellipsis, no wait.

    `You own 0 relics in total.` is the reading that looks most like lost
    data, and AK-222 forbids any statement at all about a stock nobody has
    looked at yet. The waiting sentence is not this line's job either -- the
    note underneath already carries `Reading your save.` while a read is out.
    """
    chosen = state == "chosen save with nothing in it"
    if state == "never answers":
        read = StatedRead(a_scan_of(game_data, 3), hold=True)
    elif state == "unreadable":
        read = StatedRead(raises=ValueError("the file could not be opened"))
    else:
        # Held, so that the flag below is set before the answer is let in and
        # not in a race with it.
        read = StatedRead(None, hold=chosen)
    window = a_window(game_data, read)
    try:
        if chosen:
            # What `Find my save...` leaves behind: the read answers about a
            # file the player pointed at himself (AK-124, S3).
            window._answers_a_chosen_save = True
            read.release()
        if state == "never answers":
            read.began.wait(30.0)
            rendered.settle(2)
            assert window.save_reader.is_reading(), "the premise"
            assert the_note(window) == appmod.READING_THE_SAVE
        else:
            conftest.wait_for_the_save(window)
            rendered.settle(2)
            assert window.owned is None, "the premise: nothing came back"
            assert the_note(window), "and the note says which ending it was"

        assert the_line(window) == ""
        assert window.owned_total_label.toolTip() == ""
        # Shown, and empty. A line that is merely hidden is the mutation the
        # case below is about.
        assert window.owned_total_label.isVisibleTo(the_left_pane(window))
    finally:
        close(window, read)


def test_a_stock_that_names_nothing_is_no_stock_at_all(game_data, qapp):
    """AK-252 where it cannot be reached through `scan` today, and could be.

    `inventory.build` drops every record the dataset does not name, so a save
    written by a newer game than the snapshot came from yields an `Inventory`
    that is not None and counts nothing. The line would then say
    `You own 0 relics in total.` -- the one sentence AK-252 rules out -- so
    "nothing has been read" is asked as "there is nothing to name" and not as
    "the object is None".
    """
    read = StatedRead(a_scan_of(game_data, 0))
    window = a_window(game_data, read)
    try:
        conftest.wait_for_the_save(window)
        rendered.settle(2)

        assert window.owned is not None, "the premise: a stock came back"
        assert window.owned.relic_count == 0, "and it names nothing"
        assert the_line(window) == ""
    finally:
        close(window, read)


def test_the_arrival_moves_no_control_of_the_left_pane(game_data, qapp):
    """AK-252's second half: the line has its height from the first paint.

    Without a floor under the empty line the buttons, the note, the level
    slider and the vessel list above them all shift the moment the save
    lands -- under the pointer, at the one moment the player is looking
    somewhere else.
    """
    read = StatedRead(a_scan_of(game_data, 3), hold=True)
    window = a_window(game_data, read)
    try:
        window.show()
        rendered.settle()
        read.began.wait(30.0)
        assert the_line(window) == "", "the premise: nothing read yet"
        before = where_everything_in_the_left_pane_sits(window)
        size_before = (window.width(), window.height())
        panes_before = window.panes.sizes()

        read.release()
        conftest.wait_for_the_save(window)
        rendered.settle()

        assert the_line(window) == THREE, "the premise: the number arrived"
        assert (window.width(), window.height()) == size_before
        assert window.panes.sizes() == panes_before
        after = where_everything_in_the_left_pane_sits(window)
        moved = {name: (before[name], after[name])
                 for name in before if before[name] != after[name]}
        assert not moved, moved
    finally:
        close(window, read)
