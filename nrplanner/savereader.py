"""Reading the save for the Build planner: where it is, and in a thread.

`read_the_save` is the one place the three exits of AK-124 are told apart --
a scan, a file that holds nothing, a file that cannot be read -- and
`SaveReader` runs it off the main thread with a generation counter, the
same build as the advisor's controller (AD-029). The window hands in what
to read and listens for `ready` and `failed`; nothing here reaches into the
window (AD-034).
"""

from __future__ import annotations

import os
import pathlib
import traceback

from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import QFileDialog

from nrdata import savefile

from . import errortext, inventory

#: S2. Unlike the folder dialog of the first run, whose caption is left to
#: Qt, this one is written here: the spec gives it as a text of this program
#: (AK-128), and a file dialog's caption is the only place that says which
#: file is being asked for.
CHOOSE_YOUR_SAVE = "Choose your Nightreign save file"

#: The three filter entries of section 5, in that order. The third is not an
#: oversight: `find_saves` deliberately takes renamed backups as well, so a
#: dialog that refused them would be stricter than the program behind it.
SAVE_FILE_FILTERS = ("Nightreign save (NR*.sl2);;"
                     "Save file (*.sl2);;"
                     "All files (*)")


#: How long the window waits for a running save read when it is closing. A
#: `wait()` in the main thread is forbidden while the program is running
#: (AD-006.4) and is the only correct thing here: the alternative is a
#: `QThread` deleted while its read is still going.
#:
#: Derived, not chosen. What this waits for is `inventory.scan`, measured at
#: 657,2 ms (p50, the player's own save, S11-E carried forward in T-140). Its
#: worst measured shape is the same read on the same save and the same machine
#: before the prefilter existed: 6147,6 ms. Ten per cent over that is what is
#: waited, so a save the prefilter turns out not to help still finishes its
#: read instead of losing its thread underneath it: 6147,6 x 1,1 = 6762 ms,
#: rounded up.
SAVE_READ_SHUTDOWN_WAIT_MS = 6800

def where_saves_usually_are() -> pathlib.Path | None:
    """Where the file dialog opens (AK-123, section 5).

    The start location is the actual help in this dialog: the player cannot
    type the variable his profile lives under and should not have to. So the
    `Nightreign` folder if it is there, the profile itself if it is not, and
    None -- "wherever Qt would" -- if neither is.

    Resolved, always, and never named as a variable anywhere he can read it
    (AK-127): what he sees in the dialog is a path.
    """
    roots = savefile.save_roots()
    for folder in roots:
        if folder.is_dir():
            return folder.resolve()
    for folder in roots:
        if folder.parent.is_dir():
            return folder.parent.resolve()
    return None


def _pick_a_save_file(parent) -> pathlib.Path | None:
    """The system's own file dialog, opened where the saves are.

    Native, for the reason `firstrun._pick_a_folder` gives: it is the dialog
    the player knows from everything else on his machine, with his quick
    access places and his network drives in it.

    A file and not a folder, which is the difference from the first run's
    question and the reason it is the right one here: with two Steam accounts
    the file is the only thing that says *which* account he means.
    """
    start_at = where_saves_usually_are()
    picked, _chosen_filter = QFileDialog.getOpenFileName(
        parent, CHOOSE_YOUR_SAVE,
        "" if start_at is None else os.fspath(start_at),
        SAVE_FILE_FILTERS)
    return pathlib.Path(picked) if picked else None


def read_the_save(data: dict, save_path: pathlib.Path | None = None):
    """Read the save the window is to show, and answer for the file it read.

    The default reading of `SaveReader`, and the one place the three exits of
    AK-124 are told apart. `inventory.scan` cannot tell them apart and should
    not: it answers None both for "there is no save here" and for "this file
    holds no relics", and it swallows an unreadable file on purpose, because
    on the automatic route the next file may well be the good one.

    For a file the **player pointed at** those are three different pieces of
    news, and he is owed the difference: a scan gives the ordinary line, a
    None means the file was read and holds nothing (S3), and a raise carries
    the reason he cannot be expected to guess (S4).

    **No path and no Windows wording is ever put into the reason.** The save
    folder is named after the Steam account id (AK-126), and an `OSError`
    writes the whole path into its message; `strerror` drops the path but is
    in the language of the Windows installation and broke A8 (QA-211). What
    comes out of one here is `errortext`'s sentence for its `errno`, and it
    leaves as this module's own class so that the window may quote it.
    """
    if save_path is None:
        return inventory.scan(data)
    try:
        inventory.refuse_a_size_no_save_can_have(save_path.stat().st_size)
        found = inventory.scan(data, save_path)
        if found is None:
            # Reading it again is what tells S3 from S4, and it is only ever
            # done when the scan came back empty -- so the ordinary case pays
            # nothing for it, and the two cases that are left are the ones
            # the player is about to ask about.
            savefile.read(save_path)
        return found
    except OSError as exc:
        raise inventory.SaveNotReadable(errortext.in_english(exc)) from None


class _SaveReadWorker(QObject):
    """One reading of the save, off the main thread. Built once and dropped.

    Never touches a widget, not even to read one: it is built with the dataset
    it needs and everything it has to say goes out as a signal Qt delivers
    into the main thread's event loop.

    **The generation is stamped on here and nowhere else**, exactly as the
    advisor's `_Worker` stamps an answer (AD-006.3): this is the one place
    that knows both which reading was asked for and what came back, so
    `inventory.scan` does not have to know that generations exist.
    """

    #: What the save held, as a `SaveScan` -- or `None` when no save was
    #: found, which is an answer and not a failure.
    ready = Signal(int, object)
    #: A read that could not be finished, in one line and without a traceback.
    #: An exception that merely propagated would end the thread in silence and
    #: leave the window on its waiting sentence for ever (AK-224). The line is
    #: `errortext`'s and never the exception's own: anything at all can come
    #: out of `self._read`, and whatever Windows would have said here it would
    #: have said in its own language (QA-211, A8).
    failed = Signal(int, str)
    #: Always last, whatever happened, so the thread is quit from one place.
    finished = Signal()

    def __init__(self, generation: int, data: dict, read,
                 save_path: pathlib.Path | None = None) -> None:
        super().__init__()
        self._generation = generation
        self._data = data
        self._read = read
        # Which file this reading is about, or None for "whichever the
        # automatic route finds". Handed in rather than looked up here: the
        # settings store is the main thread's, and a `stat` on a dead network
        # path is exactly what this thread exists to keep off it.
        self._save_path = save_path

    def work(self) -> None:
        try:
            found = self._read(self._data, self._save_path)
        except Exception as exc:  # noqa: BLE001 - reported, never raised on
            traceback.print_exc()
            self.failed.emit(self._generation, errortext.in_english(exc))
        else:
            self.ready.emit(self._generation, found)
        self.finished.emit()


class SaveReader(QObject):
    """One reading of the save at a time, in a thread, and never out of date.

    The same build as `AdvisorController` and deliberately not a second
    mechanism (AD-029, AD-028): a worker in a `QThread`, a generation counter
    that decides whether an answer still belongs to anybody, and a `shutdown`
    that is the one place a `wait()` in the main thread is right.

    Three differences, each because the two are asked different questions:

    * **no debounce.** `Rescan save` is a click, not a dragged slider, and a
      second click while a read is out starts nothing at all (AD-029 point 4)
      rather than replacing what is running.
    * **no cache.** A rescan exists to find out what changed on disk; an
      answer kept from the last one is the one thing it must not hand back.
    * **no cancelling.** `inventory.scan` has no place to look at a flag, and
      a read the player abandoned costs the window nothing -- the generation
      is what keeps its answer off the screen.

    What crosses the thread boundary is a `SaveScan` and nothing else
    (AD-029 point 1): records read out of bytes, never the living `Inventory`,
    which the main thread builds out of them at the arrival (AD-006.8).

    **What is read is handed in at construction**, the seam AD-028 built for
    the advisor's two tracks: a case can state a read that never answers, one
    that answers at once, or one that fails, and drive the whole real way --
    thread, signal, generation check, window.
    """

    #: The scan for the read that is still the current one. Never for an
    #: overtaken one: those are dropped here, wordlessly.
    ready = Signal(object)
    #: A read that could not be finished, in one line.
    failed = Signal(str)

    def __init__(self, parent: QObject | None = None, *, read=None) -> None:
        super().__init__(parent)
        # Looked up when a read starts and not written down here, so that
        # `None` really means "whatever `read_the_save` is at that moment".
        # A default bound at import time would be a different function from
        # the one a case had put in the module, and the case would pass by
        # measuring the wrong thing.
        self._read = read
        self._generation = 0
        self._answering = False
        self._thread: QThread | None = None
        self._worker: _SaveReadWorker | None = None

    def is_reading(self) -> bool:
        """Is an answer still to come?

        Not "is a thread alive": the window asks this to decide what it may
        say and what it may do, and from the moment the answer has been handed
        over there is nothing left to wait for. The two part company for one
        turn of the event loop -- the worker's `finished` is queued behind its
        `ready` -- and a window that read the thread instead would refuse, at
        the arrival, the very import the arrival is there to do.
        """
        return self._answering

    def start(self, data: dict, save_path: pathlib.Path | None = None) -> bool:
        """Begin a read, unless one is already out. Says which it did.

        One read at a time (AD-029 point 4). A second `Rescan` while the first
        is still going does nothing whatever -- it does not queue, it does not
        replace -- because the line under the button already says what is
        happening and the answer that is coming is the one the player wants.

        `save_path` is the file the player picked, resolved by the caller in
        the main thread (AD-030). None is "let the automatic route decide",
        which is what it has always been.

        Hands back whether it started one, so the window can tell a read it
        has to draw a waiting state for from a click that changed nothing.
        """
        if self._thread is not None:
            return False
        self._generation += 1
        self._answering = True
        self._thread = QThread()
        self._worker = _SaveReadWorker(self._generation, data,
                                       self._read or read_the_save, save_path)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.work)
        self._worker.ready.connect(self._on_ready)
        self._worker.failed.connect(self._on_failed)
        self._worker.finished.connect(self._thread.quit)
        self._thread.finished.connect(self._on_thread_finished)
        self._thread.start()
        return True

    def shutdown(self, timeout_ms: int = SAVE_READ_SHUTDOWN_WAIT_MS) -> None:
        """Stop caring about the read and wait for it. Closing only.

        **The generation goes up first**, and that line is the whole of the
        lesson from the advisor's `shutdown` (Nachtrag X-1): a worker that
        emitted its answer between the last check and the wait has left a
        `ready` in the main thread's queue, `wait()` does not empty that
        queue, and the turn of the event loop that the closing itself is would
        deliver it to a window that is already going. Silence after `shutdown`
        is meant to be a property of this class, and this is what makes it one
        rather than a race no guard could watch without flickering.

        Nothing is emitted here and nothing will be. There is nobody left to
        read a sentence.
        """
        self._generation += 1
        self._answering = False
        thread = self._thread
        if thread is not None:
            thread.wait(timeout_ms)

    def _on_thread_finished(self) -> None:
        """Clear the read away, so the next `Rescan` can start one."""
        self._worker.deleteLater()
        self._thread.deleteLater()
        self._worker = None
        self._thread = None

    def _on_ready(self, generation: int, found) -> None:
        """Pass the scan on, if it is still the reading anybody is waiting for."""
        self._answering = False
        if generation != self._generation:
            return
        self.ready.emit(found)

    def _on_failed(self, generation: int, reason: str) -> None:
        """A read that could not be finished, if anyone is still waiting.

        Judged by the same generation as an answer: a failure of a reading
        nobody is waiting for any more is not news, and the sentence on screen
        would be about a state that no longer exists.
        """
        self._answering = False
        if generation != self._generation:
            return
        self.failed.emit(reason)
