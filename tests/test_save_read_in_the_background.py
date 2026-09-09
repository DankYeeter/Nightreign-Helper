"""The save is read in a thread, and the window says so (AD-029 stage B).

`UI_SPEC` T-141, AK-220 to AK-227 and AK-229. AK-228 is not covered here: the
slow fall-back way of reading exists since AD-031, and `Inventory` says which
way it was read on, but no state of this window has been given the sentence
that goes with it yet -- that is V5 and a task of its own.

**Everything here is driven through the seam, never around it.** `Planner`
takes what it reads the save with at construction -- the same device AD-028
built for the advisor's two tracks -- so a case can state a read that never
answers, one that answers at once, one that fails and one that finds no save,
and every one of them travels the whole real way: thread, signal, generation
check, window. A stub put in place of the window's own handler would replace
exactly the stretch these cases are about.

**Waited for as states, never for spans.** No case here asserts a duration and
none may: the fuse in `StatedRead` is a guard against a hung run, and it is
long enough that it never fires in a green one.
"""

from __future__ import annotations

import ast
import dataclasses
import pathlib
import threading

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QAbstractButton, QApplication, QProgressBar,
                               QTabWidget)

from nrplanner import app as appmod, chalices, inventory
from tests import conftest, rendered

#: How long a held read waits to be let go before it gives up. A fuse against
#: a hung run and nothing else: in a green run every case releases its read,
#: so this is never reached, and no assertion anywhere below is about it.
READ_FUSE_S = 30.0

#: The three sentences AK-229 forbids behind `Save could not be read: `.
CLAIMS_THE_SAVE_IS_FINE = ("nothing is wrong", "nothing is missing",
                           "nothing needs fixing")


class StatedRead:
    """A reading of the save whose answer, and whose moment, the case states.

    Stands where `app.read_the_save` stands and is called with what it is
    called with -- the dataset and the file the window resolved, in the
    worker's thread, once per reading -- so a case gets the
    four endings of `UI_SPEC` §6 as inputs rather than having to arrange a
    save on disk for each of them.

    `hold=True` is "a read that never answers" as a **state**: it blocks in
    the worker until the case lets it go, which is what makes the window's
    waiting state stand still to be looked at.
    """

    def __init__(self, answer=None, *, raises: Exception | None = None,
                 hold: bool = False) -> None:
        self.answer = answer
        self.raises = raises
        self.calls = 0
        #: The file each reading was asked for, in order. None is "whatever
        #: the automatic route finds", which is what a window with no picked
        #: save hands down.
        self.save_paths: list = []
        self.began = threading.Event()
        self._release = threading.Event()
        if not hold:
            self._release.set()

    def __call__(self, data, save_path=None):
        self.calls += 1
        self.save_paths.append(save_path)
        self.began.set()
        self._release.wait(READ_FUSE_S)
        if self.raises is not None:
            raise self.raises
        return self.answer

    def release(self) -> None:
        self._release.set()

    def hold_the_next_one(self) -> None:
        """Make the reading after this one stand still until it is let go.

        One device for both readings of a session, so that a case about a
        `Rescan` does not have to reach into the reader and swap what it
        reads with -- which would be the one stretch these cases are about.
        """
        self._release.clear()
        self.began.clear()


@pytest.fixture(scope="module")
def a_scan(game_data):
    """One real reading of the player's save, kept for the whole module.

    Real records rather than built ones: every case below that is about what
    arrives is about an inventory the planner can actually put into its slots,
    and the stored builds AK-226 turns on are the player's own. Read once,
    because the reading is what stage B exists to get out of the main thread.
    """
    found = inventory.scan(game_data)
    if found is None:
        pytest.skip("this machine has no save to read")
    return found


def a_window(game_data, read: StatedRead):
    """A planner reading the save the case stated. Never shown by itself."""
    conftest.clear_settings()
    return appmod.Planner(game_data, read_save=read)


def close(window, read: StatedRead) -> None:
    """Let the read go, let it land, and take the window down."""
    read.release()
    try:
        conftest.wait_for_the_save(window)
    finally:
        window.close()
        window.deleteLater()
        rendered.settle(2)


def cards(window) -> list:
    """Every slot card of the window, Deep of Night included."""
    return list(window.base_slots) + list(window.deep_slots)


def whatever_the_reader_is_running(reader) -> tuple:
    """The reader's thread and its worker, to be held while a press is made.

    `SaveReader` keeps the only reference to each of them. A reader that
    started a read while one was already out would overwrite both, and Qt
    would then destroy a thread that is running and the object that thread is
    inside: the process dies where it stands, no assertion below is heard,
    and what comes back names no rule at all (measured, T-142: no summary,
    and again in T-157 at this very case).

    So every case that presses while a read is out keeps what the reader had.
    Under the rule this is the same pair after every press and holding it
    costs nothing; against a reader that broke the rule it is the difference
    between a sentence and a crash.
    """
    return reader._thread, reader._worker


def the_line(window) -> str:
    return window.owned_label.text()


# -- AK-220: the window is there before the save is -------------------------

def test_the_window_stands_complete_before_the_save_has_been_read(
        game_data, qapp, a_scan):
    """AK-220. Nothing that does not need the save waits for it.

    A synchronous read makes every one of these false: the constructor would
    not come back until the read had, so there would be no window to look at
    while `is_reading()` was true.
    """
    read = StatedRead(a_scan, hold=True)
    window = a_window(game_data, read)
    try:
        window.show()
        rendered.settle()
        read.began.wait(READ_FUSE_S)

        assert window.save_reader.is_reading(), "the premise: the read is out"
        assert window.owned is None, "and nothing has come back from it"
        assert window.isVisible()
        assert window.windowTitle()

        tabs = window.findChild(QTabWidget)
        assert tabs.count() >= 3
        for index in range(tabs.count()):
            assert tabs.isTabEnabled(index), tabs.tabText(index)
        assert len(window.hero_tiles) == len(game_data["heroes"])
        assert window.chalice_list.count() > 0
        assert window.level_slider.isEnabled()
        assert window.effects_tab.isEnabled()
    finally:
        close(window, read)


# -- AK-221, AK-222, AK-223: the waiting state ------------------------------

def test_the_waiting_state_is_a_state_and_not_a_nothing(game_data, qapp,
                                                        a_scan):
    """AK-221 and AK-222's first half, at the first read of a session."""
    read = StatedRead(a_scan, hold=True)
    window = a_window(game_data, read)
    try:
        window.show()
        rendered.settle()
        read.began.wait(READ_FUSE_S)

        assert the_line(window) == appmod.READING_THE_SAVE
        assert appmod.NO_SAVE_FOUND not in the_line(window)
        for card in cards(window):
            assert card.current_relic() is None, "the premise: nothing read"
            assert appmod.RELICS_AFTER_THE_SAVE in card.rolled_label.text()
        # Shown, not merely written: the Deep of Night cards are hidden while
        # the switch is off, so the ones on screen are the ones asked.
        for card in window.active_slots():
            assert card.rolled_label.isVisible()

        # Nothing that waits beside the sentence that already says it.
        assert not [bar for bar in window.findChildren(QProgressBar)
                    if bar.isVisible()]
        assert window.cursor().shape() == Qt.ArrowCursor
        assert QApplication.overrideCursor() is None
        assert QApplication.activeModalWidget() is None

        # AK-222: no number nobody knows, anywhere in the window.
        assert not [card for card in cards(window)
                    if "available" in card.title.text()]
    finally:
        close(window, read)


def test_the_arrival_puts_the_count_back_in_every_heading(game_data, qapp,
                                                          a_scan):
    """AK-222's second half: with the stock the bracket comes back."""
    read = StatedRead(a_scan, hold=True)
    window = a_window(game_data, read)
    try:
        window.show()
        rendered.settle()
        read.began.wait(READ_FUSE_S)
        assert not [card for card in cards(window)
                    if "available" in card.title.text()], "the premise"

        read.release()
        conftest.wait_for_the_save(window)
        rendered.settle()

        assert window.owned is not None
        for card in window.active_slots():
            assert "available" in card.title.text(), card.title.text()
            assert appmod.RELICS_AFTER_THE_SAVE not in card.rolled_label.text()
    finally:
        close(window, read)


def test_the_read_shuts_the_relic_button_and_nothing_else(game_data, qapp,
                                                          a_scan):
    """AK-223. Exactly one control is shut, and it opens again at the arrival."""
    read = StatedRead(a_scan, hold=True)
    window = a_window(game_data, read)
    try:
        window.show()
        rendered.settle()
        read.began.wait(READ_FUSE_S)

        for card in cards(window):
            assert not card.choose_button.isEnabled()
            assert card.hold_button.isEnabled()
        for control in (window.rescan_button, window.import_button,
                        window.deep_check, window.chalice_list,
                        window.level_slider, *window.hero_tiles):
            assert control.isEnabled(), control

        # The relation AK-223 is really about: the read shuts the relic
        # buttons and leaves every other control of the window as it found it.
        shut_while_reading = {b for b in window.findChildren(QAbstractButton)
                              if not b.isEnabled()}
        read.release()
        conftest.wait_for_the_save(window)
        rendered.settle()
        shut_after = {b for b in window.findChildren(QAbstractButton)
                      if not b.isEnabled()}

        buttons = {card.choose_button for card in cards(window)}
        assert buttons <= shut_while_reading
        assert not (buttons & shut_after)
        # And the read leaves nothing shut behind it.
        assert shut_after - shut_while_reading == set()

        # Everything else that is shut while the read is out, and open
        # afterwards, is `Optimize` -- and it is shut by the absence of a
        # stock, not by the read: the advisor bar shuts it on any window that
        # has none, which is a deviation from AK-223's "exactly one" reported
        # to the `ui-ux-designer` rather than decided here. The control below
        # is what makes that a measured statement instead of an excuse.
        others = (shut_while_reading - buttons) - shut_after
        assert sorted(b.text() for b in others) == ["Optimize"]
    finally:
        close(window, read)

    no_save = StatedRead(None)
    other = a_window(game_data, no_save)
    try:
        conftest.wait_for_the_save(other)
        other.show()
        rendered.settle()
        assert other.owned is None, "the premise: this window has no stock"
        shut = {b.text() for b in other.findChildren(QAbstractButton)
                if not b.isEnabled()}
        assert "Optimize" in shut, (
            "a window with no stock shuts Optimize whether a read is out or "
            "not, which is what makes the waiting state no stricter than the "
            "state it already had")
    finally:
        close(other, no_save)


def test_a_rescan_says_that_nothing_changes_until_it_is_done(game_data, qapp,
                                                             a_scan):
    """AK-221 (b) and the promise of §3: the second sentence, and it is true."""
    first = StatedRead(a_scan)
    window = a_window(game_data, first)
    try:
        conftest.wait_for_the_save(window)
        window.show()
        rendered.settle()
        before = [card.current_relic() for card in cards(window)]
        headings = [card.title.text() for card in cards(window)]

        first.hold_the_next_one()
        window.rescan_button.click()
        first.began.wait(READ_FUSE_S)

        assert the_line(window) == appmod.READING_THE_SAVE_AGAIN
        assert [card.current_relic() for card in cards(window)] == before
        assert [card.title.text() for card in cards(window)] == headings
        for card in cards(window):
            assert not card.choose_button.isEnabled()
            # No card gains a line on a rescan: what stands there is right.
            assert appmod.RELICS_AFTER_THE_SAVE not in card.rolled_label.text()
    finally:
        close(window, first)


# -- AK-224: the waiting sentence is never the last word --------------------

WAITING_SENTENCES = (appmod.READING_THE_SAVE, appmod.READING_THE_SAVE_AGAIN)


def test_every_ending_of_a_read_leaves_a_sentence_of_its_own(game_data, qapp,
                                                             a_scan):
    """AK-224, over the three endings that exist in this source.

    The fourth of `UI_SPEC` §6 -- read on the slow way -- has no ending of its
    own in this window yet: AD-031 built the way, V5 gives it its sentence, and
    it is AK-228's. The rule this case is built on is the one AK-224 hangs on
    and not the list: whatever way a read ends, the line does not still carry a
    waiting sentence afterwards.
    """
    # The save's own records with its stored builds taken out. On the first
    # read of a session the arrival takes a stored build over (§6), and
    # `load_equipped` writes a line of its own over the note -- which it does
    # on the synchronous path too, and which §6's list of endings does not
    # name. A save with no stored build has nothing to take over, so the
    # inventory note is what stands, and that is the ending being checked.
    without_builds = dataclasses.replace(a_scan, loadouts=[])
    endings = {
        "read": (StatedRead(without_builds),
                 lambda line: line.startswith(
                     f"{len(a_scan.owned)} relics in {a_scan.source}")),
        "no save": (StatedRead(None), lambda line: line == appmod.NO_SAVE_FOUND),
        "unreadable": (StatedRead(raises=ValueError("this is not a save")),
                       lambda line: line == (appmod.UNREADABLE_SAVE
                                             + "this is not a save")),
    }
    for name, (read, says) in endings.items():
        window = a_window(game_data, read)
        try:
            conftest.wait_for_the_save(window)
            rendered.settle()
            line = the_line(window)
            assert line not in WAITING_SENTENCES, name
            assert line, f"{name}: the line is empty, which says nothing"
            assert says(line), f"{name}: {line!r}"
        finally:
            close(window, read)


def test_the_answer_of_the_read_actually_reaches_the_window(game_data, qapp,
                                                            a_scan):
    """The answer arrives -- not merely that it was sent.

    Written because of U5b, where a new track stamped every question with
    generation 0, every answer was dropped as overtaken and the whole way
    stood still without a word. The assertion is on what came back: the
    inventory in the window is built out of the very scan the read handed
    over, down to the count and the source name.
    """
    read = StatedRead(a_scan, hold=True)
    window = a_window(game_data, read)
    try:
        assert window.owned is None, "the premise"
        read.release()
        conftest.wait_for_the_save(window)

        assert read.calls == 1
        assert window.owned is not None, "the answer was dropped in silence"
        assert window.owned.source == a_scan.source
        assert window.owned.relic_count == len(a_scan.owned)
        assert len(window.owned.loadouts) == len(a_scan.loadouts)
        assert window.owned.relics, "records, not an empty shell"
    finally:
        close(window, read)


# -- AK-225: the arrival moves nothing --------------------------------------

def test_the_arrival_moves_neither_the_window_nor_the_focus(game_data, qapp,
                                                            a_scan):
    """AK-225. Size, pane widths, focus, and the height of the save line."""
    read = StatedRead(a_scan, hold=True)
    window = a_window(game_data, read)
    try:
        window.resize(1100, 800)
        window.show()
        rendered.settle()
        if window.width() != 1100:
            pytest.skip(
                f"this platform will not give the window 1100 logical px: it "
                f"is {window.width()} px, and nothing measured across the "
                f"arrival here would be about the arrival")
        # At the left pane's own default width, which is where AK-225 asks
        # for the two heights: a pane squeezed by a narrow window wraps the
        # note further and would be measuring the window instead.
        window.panes.setSizes(list(appmod.PANE_DEFAULTS))
        window.rescan_button.setFocus()
        rendered.settle()

        size = (window.width(), window.height())
        panes = list(window.panes.sizes())
        focused = window.focusWidget()
        waiting_height = window.owned_label.height()

        read.release()
        conftest.wait_for_the_save(window)
        rendered.settle()

        assert (window.width(), window.height()) == size
        assert list(window.panes.sizes()) == panes
        assert window.focusWidget() is focused
        # The line does not push what is under it down when the note replaces
        # the waiting sentence. A relation and not a figure: the figure is a
        # font, the relation is the promise.
        assert window.owned_label.height() <= waiting_height, (
            f"waiting {waiting_height} px, note "
            f"{window.owned_label.height()} px for {the_line(window)!r}")
    finally:
        close(window, read)


# -- AK-226: no overwriting what the player did in the meantime -------------

def a_hero_with_a_stored_build(window):
    """The row of a Nightfarer this save has a stored build for."""
    for index, hero in enumerate(window.heroes):
        if window.owned is not None and window.owned.loadouts_for(hero["id"]):
            return index, hero
    pytest.skip("this save stores no build for any Nightfarer")


def test_the_stored_build_is_taken_over_when_nobody_touched_a_slot(
        game_data, qapp, a_scan):
    """AK-226's second half: with no intervention the arrival is a full read."""
    read = StatedRead(a_scan, hold=True)
    window = a_window(game_data, read)
    try:
        read.release()
        conftest.wait_for_the_save(window)
        rendered.settle()
        hero = window.current_hero()
        if not window.owned.loadouts_for(hero["id"]):
            pytest.skip("this save stores no build for the first Nightfarer")
        assert chalices.imported(hero["id"]), (
            "the arrival takes the stored build over exactly once")
    finally:
        close(window, read)


def test_the_cards_get_the_stock_when_no_build_is_worn(game_data, qapp,
                                                      a_scan):
    """The one way in which the stock reaches the cards and nothing else does.

    A fresh character is the ordinary case here: he has vessels, and none of
    them is worn. `reload_chalices` still hands over to `load_equipped`,
    because the save does store builds for him -- and `load_equipped` leaves
    at `selected_loadout(...) is None`, before `apply_chalice`, which is what
    gives the cards the inventory on every other path. So on this path
    `_hand_the_stock_to_the_slots` is the only thing between the arrival and
    a player looking at six cards that offer him nothing.

    Read off the count in the heading rather than off the cards' own
    attribute: `(n available)` is what he sees, and it is written from what
    the card holds rather than from what the window holds.
    """
    worn_by_nobody = dataclasses.replace(
        a_scan,
        loadouts=[dataclasses.replace(stored, selected=False)
                  for stored in a_scan.loadouts])
    read = StatedRead(worn_by_nobody)
    window = a_window(game_data, read)
    try:
        conftest.wait_for_the_save(window)
        rendered.settle()
        hero = window.current_hero()
        if not window.owned.loadouts_for(hero["id"]):
            pytest.skip("this save stores no build for the first Nightfarer")
        assert window.owned.selected_loadout(hero["id"]) is None, (
            "the premise: this Nightfarer wears none of his builds")

        for card in window.active_slots():
            assert "available" in card.title.text(), card.title.text()
    finally:
        close(window, read)


def test_a_slot_set_during_the_read_survives_the_arrival(game_data, qapp,
                                                         a_scan):
    """AK-226's first half, and the change of Nightfarer that used to undo it.

    The custom relic is the one thing a player can put in a slot while the
    relic button is shut, and it is what the case uses; the rule it proves is
    about any slot the player set themselves.
    """
    read = StatedRead(a_scan, hold=True)
    window = a_window(game_data, read)
    try:
        read.began.wait(READ_FUSE_S)
        hero = window.current_hero()
        slot = window.base_slots[0]
        effects = [int(k) for k in list(game_data["effects"])[:2]]
        slot.set_custom(effects)
        mine = slot.current_relic()
        assert mine is not None, "the premise: the player put something here"

        read.release()
        conftest.wait_for_the_save(window)
        rendered.settle()

        kept = window.base_slots[0].current_relic()
        assert kept is not None
        assert kept.relic_id == inventory.CUSTOM_RELIC_ID
        assert list(kept.effect_ids) == effects

        # And the save's build does not come over the slots at the next
        # change of Nightfarer either, which is where a skipped-but-unmarked
        # import turns up.
        #
        # What the round trip does to the player's own custom relic is not
        # asserted here and must not be: it is emptied on the way back on the
        # unchanged source too (measured against the tree at a8d31bb), so an
        # assertion about it would be about the chalice store and not about
        # this read.
        assert chalices.imported(hero["id"]), (
            "marked as taken over, which is what stops it arriving later")
        worn = window.owned.selected_loadout(hero["id"])
        if worn is not None and any(worn.relics) and len(window.heroes) > 1:
            saves_build = [chalices.slot_key(r) for r in worn.relics]
            window.select_hero(1)
            rendered.settle()
            window.select_hero(window.heroes.index(hero))
            rendered.settle()
            slots = list(window.base_slots) + list(window.deep_slots)
            assert [s.saved_key() for s in slots] != saves_build
    finally:
        close(window, read)


# -- AK-227: one read at a time ---------------------------------------------

def test_pressing_rescan_during_a_read_starts_no_second_one(game_data, qapp,
                                                            a_scan):
    """AK-227: a count against a literal, and nothing moves on screen."""
    first = StatedRead(a_scan)
    window = a_window(game_data, first)
    try:
        conftest.wait_for_the_save(window)
        window.show()
        rendered.settle()

        first.hold_the_next_one()
        window.rescan_button.click()
        first.began.wait(READ_FUSE_S)

        line = the_line(window)
        before = [card.current_relic() for card in cards(window)]
        still_running = [whatever_the_reader_is_running(window.save_reader)]
        for _ in range(5):
            window.rescan_button.click()
            still_running.append(
                whatever_the_reader_is_running(window.save_reader))
            rendered.settle()
        assert still_running[0][0] is not None, "the premise: a read is out"

        # A count against a literal: one reading at the start of the session
        # and one for the first press. The five presses that followed while it
        # was out started nothing.
        assert first.calls == 2
        assert the_line(window) == line
        assert [card.current_relic() for card in cards(window)] == before
    finally:
        close(window, first)


def test_load_equipped_says_nothing_while_a_read_is_out(game_data, qapp,
                                                        a_scan):
    """§5 and §9 (h): the button does nothing and writes nothing into the line."""
    read = StatedRead(a_scan, hold=True)
    window = a_window(game_data, read)
    try:
        read.began.wait(READ_FUSE_S)
        window.import_button.click()
        rendered.settle()
        assert the_line(window) == appmod.READING_THE_SAVE
    finally:
        close(window, read)


# -- the reader itself: one at a time, and silent after shutdown ------------

def test_the_reader_starts_nothing_while_one_read_is_out(game_data, qapp,
                                                         a_scan):
    """AD-029 point 4, at the controller and without a window in the way.

    Whatever the reader is running is held across every press, for the reason
    `whatever_the_reader_is_running` gives: without it a reader that broke
    this rule would take the process down with it and the rule would never be
    named. Held, the broken rule is a sentence: `assert True is False` on the
    second press (measured against `a-read-per-press`, T-157).
    """
    read = StatedRead(a_scan, hold=True)
    reader = appmod.SaveReader(read=read)
    try:
        assert reader.start(game_data) is True
        read.began.wait(READ_FUSE_S)
        still_running = [whatever_the_reader_is_running(reader)]
        assert still_running[0][0] is not None, "the premise: a read is out"

        assert reader.start(game_data) is False
        still_running.append(whatever_the_reader_is_running(reader))
        assert reader.start(game_data) is False
        still_running.append(whatever_the_reader_is_running(reader))
        assert read.calls == 1
    finally:
        read.release()
        wait_until_idle(reader)


def test_nothing_arrives_after_shutdown(game_data, qapp, a_scan):
    """T-137's defect, on this reader: a late answer after the window is gone.

    `shutdown` raises the generation before it waits, exactly as `cancel` and
    the advisor's `shutdown` do. Without that line the answer the worker had
    already sent is still in the main thread's queue, `wait()` does not empty
    that queue, and the next turn of the event loop delivers it into a window
    that is on its way out.
    """
    read = StatedRead(a_scan, hold=True)
    reader = appmod.SaveReader(read=read)
    arrived = []
    reader.ready.connect(arrived.append)
    reader.failed.connect(arrived.append)
    try:
        reader.start(game_data)
        read.began.wait(READ_FUSE_S)
        # Nothing is waited for here: the point is that the answer is on its
        # way and is dropped anyway.
        reader.shutdown(timeout_ms=0)
        read.release()
        wait_until_idle(reader)
        assert arrived == []
    finally:
        read.release()
        wait_until_idle(reader)


def test_a_read_that_fails_is_reported_rather_than_lost(game_data, qapp):
    """A read that raises ends in one line, not in a thread dying quietly."""
    read = StatedRead(raises=ValueError("this is not a save"))
    reader = appmod.SaveReader(read=read)
    said = []
    reader.failed.connect(said.append)
    try:
        reader.start(game_data)
        wait_until_idle(reader)
        assert said == ["this is not a save"]
    finally:
        wait_until_idle(reader)


def wait_until_idle(reader, timeout_ms: int = 60000) -> None:
    """Let the reader's thread end. A fuse, not a claim about a duration."""
    import time

    from PySide6.QtCore import QEventLoop

    deadline = time.monotonic() + timeout_ms / 1000
    while reader.is_reading():
        QApplication.processEvents(QEventLoop.AllEvents, 10)
        if time.monotonic() > deadline:
            raise AssertionError("the reader's thread never ended")
        time.sleep(0.002)
    # The worker's `finished` is queued behind its answer, so the thread is
    # still there for a turn after `is_reading()` has gone false. `shutdown`
    # is what waits for it, and the turns after it are what let the reader
    # clear the thread away -- without both, the `QThread` would be collected
    # while it was still there.
    reader.shutdown()
    for _ in range(5):
        QApplication.processEvents(QEventLoop.AllEvents, 10)


# -- AK-229: the prefix keeps its meaning -----------------------------------

READING_PATH = ("nrdata/savefile.py", "nrplanner/inventory.py")

#: The wording that used to be the one exception on this path, kept as the
#: mask's own control and nowhere else. It was
#: `_check_the_prefilter_can_see_every_id`'s, and AD-031 removed the function
#: with the refusal it belonged to: a dataset numbered above the ceiling is
#: now read the slow way and said so, not declared unreadable. The whitelist
#: that named it is gone with it (`UI_SPEC` T-148 §3: "wer AK-228 baut,
#: entfernt beides in derselben Aenderung").
THE_WORDING_AD_031_TOOK_OFF_THE_PATH = (
    "the game has renumbered its relics and this program is too old to read "
    "what it wrote; nothing is wrong with the save.")


def texts_that_can_land_behind_the_prefix() -> dict[str, list[str]]:
    """Every `raise ValueError(...)` text of the reading path, by function.

    Collected from the source rather than by provoking each one: `UI_SPEC` §8
    counted eight such places and three of them reach the line, and which
    three is a fact about call sites that moves. Collecting all eight is the
    stricter question and the one that does not need a save shaped for each.
    """
    out: dict[str, list[str]] = {}
    root = pathlib.Path(__file__).resolve().parents[1]
    for name in READING_PATH:
        tree = ast.parse((root / name).read_text(encoding="utf-8"))
        for function in ast.walk(tree):
            if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for node in ast.walk(function):
                if not isinstance(node, ast.Raise) or node.exc is None:
                    continue
                for text in ast.walk(node.exc):
                    if isinstance(text, ast.Constant) and isinstance(
                            text.value, str):
                        out.setdefault(function.name, []).append(text.value)
    return out


def says_the_save_is_fine(texts: list[str]) -> bool:
    whole = " ".join(texts).lower()
    return any(claim in whole for claim in CLAIMS_THE_SAVE_IS_FINE)


def test_the_collector_of_the_texts_really_fires():
    """AK-229's positive control, without which the guard measures itself.

    The guard beside this one now asserts the empty set, which is what §8
    promises and what AD-031 made reachable -- and an empty set is exactly
    what a collector that has stopped collecting also returns. So the control
    has to come from somewhere other than the offenders themselves, in two
    parts: the collector still finds a text that is demonstrably on the path,
    and the mask still matches the wording it was written for.

    The wording is the one AD-031 took off the path, kept here as a string and
    not as a place: it is what a future refusal claiming the save is fine
    would look like, and the mask has to catch it whoever writes it next.
    """
    texts = texts_that_can_land_behind_the_prefix()

    assert "read_owned_relics" in texts, sorted(texts)
    density = texts["read_owned_relics"]
    assert any("denser than one record per" in text for text in density), density

    assert says_the_save_is_fine([THE_WORDING_AD_031_TOOK_OFF_THE_PATH])
    assert not says_the_save_is_fine(density)


def test_no_text_behind_the_prefix_says_the_save_is_fine():
    """AK-229, second half. A property of the path, not a fixed list of places.

    No exception since AD-031: the one text that claimed the save was fine was
    the id check's, and it was a refusal of a save that nothing was wrong
    with. What replaced it is a slower read and a sentence in the window, so
    nothing raised on this path may say it any more.
    """
    offenders = {name for name, texts
                 in texts_that_can_land_behind_the_prefix().items()
                 if says_the_save_is_fine(texts)}
    assert offenders == set(), sorted(offenders)


def test_the_prefix_is_written_in_exactly_one_place():
    """AK-229, first half: it stands only where no inventory came out.

    A property and not a fundstelle -- the search is over the whole of
    `nrplanner`, with a mask that does not mention the constant the fix
    introduced, so a second hand-written copy of the sentence is a red case.
    """
    root = pathlib.Path(__file__).resolve().parents[1] / "nrplanner"
    written = [path for path in root.rglob("*.py")
               if "Save could not be read" in path.read_text(encoding="utf-8")]
    assert [p.name for p in written] == ["app.py"]

    source = (root / "app.py").read_text(encoding="utf-8")
    assert source.count("Save could not be read") == 1
    assert source.count("UNREADABLE_SAVE") == 2, (
        "the constant is declared once and written once")


def test_the_prefix_appears_only_where_no_inventory_came_out(game_data, qapp,
                                                             a_scan):
    """AK-229, first half, as behaviour rather than as a search."""
    endings = {"read": StatedRead(a_scan), "no save": StatedRead(None)}
    for name, read in endings.items():
        window = a_window(game_data, read)
        try:
            conftest.wait_for_the_save(window)
            assert not the_line(window).startswith(appmod.UNREADABLE_SAVE), name
        finally:
            close(window, read)

    read = StatedRead(raises=ValueError("this is not a save"))
    window = a_window(game_data, read)
    try:
        conftest.wait_for_the_save(window)
        assert the_line(window).startswith(appmod.UNREADABLE_SAVE)
        assert window.owned is None
    finally:
        close(window, read)


# -- AK-228: the fallback read says so ---------------------------------------

#: `UI_SPEC` §9 (d), copied here rather than read off `appmod`'s own
#: constant: a check against `appmod.READ_THE_SLOW_WAY_NOTE` would measure
#: the constant against itself and stay green through a typo in it (L-008).
THE_SLOW_WAY_NOTE = (
    " — read the slow way: this version of the game numbers its relics "
    "above what the quick scan looks for. Nothing is missing and nothing "
    "needs fixing.")


def test_the_slow_way_note_is_said_and_never_a_failure(game_data, qapp,
                                                        monkeypatch):
    """AK-228, and AK-229's second half made checkable: this is what it was
    written for -- A7 is closed by this test, not by the fallback existing.

    A hand-built `Inventory` rather than `a_scan`: the point is the note's
    wording and its place in the line, not a real save's own numbers, and a
    save that reads on the slow way is not something this machine can be
    made to have. `dataclasses.replace` keeps both cases identical apart
    from the one flag the note is about.

    `StatedRead` stands in for `read_the_save`, whose real answer is the raw
    `found` that `inventory.build` turns into an `Inventory` (AD-006.8) --
    not an `Inventory` itself. `inventory.build` is patched to hand back
    exactly what it is given, so `StatedRead` can carry the finished
    `Inventory` straight through, the same seam AD-028 built for the advisor.
    """
    monkeypatch.setattr(inventory, "build", lambda _data, found: found)
    # hero_id=-1 matches no real Nightfarer, so `reload_chalices` finds no
    # loadout for whichever hero the window opens on and never runs the
    # automatic take-over (AK-224) that would overwrite the note under test.
    fast = inventory.Inventory(
        source="Character 1", relic_count=3,
        loadouts=[inventory.EquippedLoadout(
            hero_id=-1, vessel_id=1, selected=True, relics=[None] * 6)])
    slow = dataclasses.replace(fast, read_the_slow_way=True)

    for owned, says_it in ((fast, False), (slow, True)):
        read = StatedRead(owned)
        window = a_window(game_data, read)
        try:
            conftest.wait_for_the_save(window)
            line = the_line(window)
            assert (THE_SLOW_WAY_NOTE in line) == says_it, owned
            assert not line.startswith(appmod.UNREADABLE_SAVE)
            expected = (f"{owned.relic_count} relics in {owned.source}, "
                       f"{len(owned.loadouts)} stored builds")
            if says_it:
                expected += THE_SLOW_WAY_NOTE
            assert line == expected
        finally:
            close(window, read)


# -- AK-243: two controls are shut, and they open on different things -------

def relic_buttons(window) -> list:
    return [card.choose_button for card in cards(window)]


def optimize(window):
    """The second shut control, in the relic half of the Build planner."""
    return window.advisor_bar.optimize_button


def test_the_two_shut_controls_come_free_on_different_conditions(game_data,
                                                                 qapp, a_scan):
    """AK-243, which is AK-223 made true rather than replaced.

    Shut while a read is out are two: the relic button of every slot card,
    and `Optimize`. They are not shut for the same reason and so do not open
    at the same moment -- the relic button is shut by the read and comes free
    when the read ends, whichever way it ends; `Optimize` is shut by the
    absence of a stock (`UI_SPEC` 4.8, `advisorbar.py:818-820`) and stays shut
    after a read that brought none.

    The five devices of AK-221, each in its own ending: a read that never
    answers, one that answers at once, one that is held and then let go, one
    that fails, and one that finds no save.
    """
    # The stored builds taken out: the takeover they set off writes a line of
    # its own, and this case is about buttons rather than about that line.
    without_builds = dataclasses.replace(a_scan, loadouts=[])

    held = StatedRead(without_builds, hold=True)
    window = a_window(game_data, held)
    try:
        window.show()
        rendered.settle()
        held.began.wait(READ_FUSE_S)

        assert window.save_reader.is_reading(), "the premise: the read is out"
        assert all(not button.isEnabled() for button in relic_buttons(window))
        assert not optimize(window).isEnabled()

        held.release()
        conftest.wait_for_the_save(window)
        rendered.settle()

        # A stock arrived, so both are free -- the second one only now.
        assert window.owned is not None
        assert all(button.isEnabled() for button in relic_buttons(window))
        assert optimize(window).isEnabled()
    finally:
        close(window, held)

    at_once = StatedRead(without_builds)
    window = a_window(game_data, at_once)
    try:
        conftest.wait_for_the_save(window)
        window.show()
        rendered.settle()

        assert all(button.isEnabled() for button in relic_buttons(window))
        assert optimize(window).isEnabled()
    finally:
        close(window, at_once)

    # And the two endings that leave no stock behind: the read is over, so
    # the relic buttons are open, and `Optimize` is not -- it is waiting on
    # something the read did not bring, not on the read.
    barren = {
        "no save": StatedRead(None),
        "unreadable": StatedRead(raises=ValueError("this is not a save")),
    }
    for name, read in barren.items():
        window = a_window(game_data, read)
        try:
            conftest.wait_for_the_save(window)
            window.show()
            rendered.settle()

            assert not window.save_reader.is_reading(), name
            assert window.owned is None, name
            assert all(button.isEnabled()
                       for button in relic_buttons(window)), name
            assert not optimize(window).isEnabled(), name
        finally:
            close(window, read)


# -- AK-244: the fifth sentence, written by the automatic takeover ----------

@dataclasses.dataclass(frozen=True)
class AStoredBuild:
    """One loadout as the save hands it over, before `inventory.build`.

    The three failures of `load_equipped` are states of the save, not of the
    window, so they are stated here rather than arranged on disk: a real save
    with a readable build table cannot be made to fail three different ways.
    """

    hero_id: int
    vessel_id: int
    selected: bool
    handles: tuple = ()


def the_nightfarer_the_window_opens_on(game_data):
    """Which Nightfarer is shown at the start, and a vessel it really has."""
    read = StatedRead(None)
    window = a_window(game_data, read)
    try:
        conftest.wait_for_the_save(window)
        hero = window.current_hero()
        vessels = [window.chalice_list.item(row).data(Qt.UserRole)
                   for row in range(window.chalice_list.count())]
        ids = [vessel["id"] for vessel in vessels if vessel and vessel.get("id")]
        assert ids, "the premise: this Nightfarer has chalices to be in"
        return hero, ids[0]
    finally:
        close(window, read)


def test_a_failed_takeover_writes_its_own_sentence_and_not_the_waiting_one(
        game_data, qapp, a_scan):
    """AK-244. Three endings AK-224 does not know, and each says something.

    `_on_save_read` calls `reload_chalices` unconditionally, and on the first
    read for a Nightfarer whose save stores a build that calls `load_equipped`
    itself. When *that* fails it writes one of three sentences over the stock
    note -- a fifth kind of ending, which the four of `UI_SPEC` §6 do not
    cover. What matters is what they have in common with the four: the
    waiting sentence is never what is left standing.
    """
    hero, a_vessel = the_nightfarer_the_window_opens_on(game_data)
    not_in_the_list = 9_999_999
    endings = {
        "the build table could not be read": (
            [AStoredBuild(hero["id"], a_vessel, False)],
            "the table is damaged",
            "This save's stored builds could not be read: the table is "
            "damaged"),
        "no equipped loadout for this Nightfarer": (
            [AStoredBuild(hero["id"], a_vessel, False)],
            "",
            f"This save stores no equipped loadout for {hero['name']}."),
        "a vessel this list does not hold": (
            [AStoredBuild(hero["id"], not_in_the_list, True)],
            "",
            f"{hero['name']} has vessel {not_in_the_list} equipped, which is "
            "not in this list."),
    }
    for name, (loadouts, error, sentence) in endings.items():
        found = dataclasses.replace(a_scan, loadouts=loadouts,
                                    loadout_error=error)
        read = StatedRead(found)
        window = a_window(game_data, read)
        try:
            conftest.wait_for_the_save(window)
            rendered.settle()
            line = the_line(window)

            assert chalices.imported(hero["id"]), f"{name}: the premise"
            assert line not in WAITING_SENTENCES, name
            assert line, f"{name}: an empty line says nothing at all"
            assert line == sentence, name
        finally:
            close(window, read)


def test_a_takeover_that_works_leaves_no_waiting_sentence_either(game_data,
                                                                 qapp, a_scan):
    """AK-244's other half, as far as the built program carries it.

    **Reported, not asserted:** AK-244 says that where the takeover does not
    fail "die Bestandsnotiz bleibt stehen". It does not: the way out of
    `load_equipped` writes `Loaded {Nightfarer} - ...` over it
    (`app.py:4079`), on this path and on the synchronous one before it. That
    is a fifth sentence of a fifth kind and it is not one of AK-224's four
    either. This case therefore holds what both halves of AK-244 really rest
    on -- the waiting sentence is never the last word, and the line is never
    empty and never a mixture -- and the disagreement over which sentence
    stands is in the report for the `ui-ux-designer`, not decided here.
    """
    hero, a_vessel = the_nightfarer_the_window_opens_on(game_data)
    found = dataclasses.replace(
        a_scan, loadouts=[AStoredBuild(hero["id"], a_vessel, True)],
        loadout_error="")
    read = StatedRead(found)
    window = a_window(game_data, read)
    try:
        conftest.wait_for_the_save(window)
        rendered.settle()
        line = the_line(window)

        assert chalices.imported(hero["id"]), "the premise: it was taken over"
        assert line not in WAITING_SENTENCES
        assert line, "an empty line says nothing at all"
        assert not [word for word in WAITING_SENTENCES if word in line]
    finally:
        close(window, read)
