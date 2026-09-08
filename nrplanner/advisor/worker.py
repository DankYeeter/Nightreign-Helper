"""The advisor's run in a thread of its own, and what the window may believe.

The one file under `advisor/` that imports Qt (AD-001), and it holds the
thread and nothing else: what it runs is `run.run`, which knows nothing about
threads and is checked without one.

**The pattern is `firstrun.ensure_data`'s, minus its waiting loop.** There a
`QObject` worker is moved into a `QThread` and the caller sits in
`while not thread.wait(50): QApplication.processEvents()` -- right for a
splash screen that has nothing else to do, and wrong here: the main window
must stay answerable, so this starts the run, connects `ready`, and returns
(`UI_SPEC` §5.4, AD-006 point 2). No `processEvents`, no modal dialog, no
`wait()` in the main thread except when the window is closing.

**Two things stop a run, and they are not the same thing.** The interruption
flag stops the *worker*, cooperatively, at the places `run.run` looks: inside
the pre-sort once per offered relic, after the pre-sort, and between the slot
levels. The generation counter stops the
*answer*: every question carries the generation it was asked under, the
answer carries it back, and an answer whose generation is no longer the
current one is dropped without a word (AD-006 point 3). Cancelling alone
would not do -- a run standing between its last check and its `emit` has
already sent its answer while the player is changing the vessel.

**`Cancel` is visible before the worker has heard of it** (`UI_SPEC` AK-11:
within 200 ms). `cancel()` raises the generation, drops what is pending and
emits `stopped` in the same call, so the window is in state 4.5 in
microseconds; the worker notices at its next check and ends quietly, and
whatever it was carrying is already stale by then.

**What crosses into the thread** is the frozen snapshot of `run.py`, the
request, and the `GoalContext`. The context carries the extracted dataset,
which is read-only for a run and is replaced wholesale rather than edited --
and `model` keeps its configuration in module globals (risk F4), so a
rebuild has to stop every run and empty the cache *before* `model.configure`
runs again. That is `before_the_data_changes` and it is not optional
(AD-006 point 7).

**Two tracks, one class** (AD-028, option D). What a controller runs is
handed to it at construction: the Advisor bar's instance answers with
`run.run`, the window's second instance with `run.slot_pool`, and nothing
else about the two differs but three figures -- the debounce, the size of the
cache, and what comes back. A second thread path written for the picker would
have been a second place for the generation counter, the debounce and the
cancelling to be got right, and the two would have drifted.

**No `progress` signal.** AD-006 point 1 names one, and there is nothing for
it to say: the progress bar of the advisor bar is indeterminate by
`UI_SPEC` §3.1 (`setRange(0, 0)`), and the figures state 4.4 puts in the
status line -- how many relics, how many slots -- are known before the run
starts and are the window's own. A signal whose numbers nothing draws could
not be shown to mean anything, so it is not built; the deviation is named
here rather than left to be discovered.
"""

from __future__ import annotations

import dataclasses
import traceback
from collections.abc import Callable, Mapping

from PySide6.QtCore import QObject, QThread, QTimer, Signal

from . import run as advisor_run
from . import search, types
from .goals import GOALS

#: AD-006 point 5's proposal: a dragged level slider must not start forty
#: runs. The `performance-tuner` confirms or corrects it in S11 -- it is a
#: figure about how fast a player changes their mind, not about this code.
DEBOUNCE_MS = 250

#: The picker track's debounce, and it is none (Nachtrag IX-1.1). The 250 ms
#: above damp a player who is still changing their mind -- keystrokes in the
#: filter field, a dragged level slider. The picker asks **once per opening**
#: (AK-206) into a modal dialog, so between two of its questions there is a
#: close and a click; there is nothing to damp, and the constant would be
#: 100 % of the cost of a cache hit and 24 % of the most expensive measured
#: question (318,1 ms, S11-C). **When it comes back:** as soon as the picker
#: track can ask more than once per opening -- that is the return path
#: `UI_SPEC` §4 keeps for the case that one pool does not serve both
#: directions after all, and it comes back with 100 ms, in the same commit.
PICKER_DEBOUNCE_MS = 0

#: How many pool answers the picker track keeps (AD-028 point 2). Sixty-four
#: against the bar's thirty-two, because the two caches hold different things:
#: the measured gain of 32 -> 64 was +41 hits and +16,5 s per session for
#: +1,05 MiB (T-118 3.2, S11-F). **The figure is set, its derivation is not**
#: (Nachtrag IX-3): it was measured on a 33,4 KiB `AdvisorResult` of 20
#: suggestions, and this track answers with a whole `SlotPool` of up to 206
#: candidates. U7 measures an entry of the new shape against the 140 KiB per
#: entry that IX-3.2 fixes as the fall-back line; above it this drops to 32.
PICKER_CACHE_SIZE = 64

#: How long the window waits for a running search when it is closing. A
#: `wait()` in the main thread is forbidden while the program is running
#: (AD-006 point 4) and is the only correct thing here: the alternative is a
#: `QThread` destroyed while its run is still going. The figure is the
#: coarsest reaction time of the search plus room -- one slot level of the
#: worst real case is about 200 ms (`scripts/measure_advisor_search.py`).
SHUTDOWN_WAIT_MS = 2000


#: What a controller runs, handed to it at construction (AD-028 option D).
#: `run.run` and `run.slot_pool` are the two, and this is their shared
#: signature; what comes back is an `AdvisorResult` or a `SlotPool`, and the
#: only thing this file asks of it is that it carries the generation back.
Answer = Callable[..., object]


@dataclasses.dataclass(frozen=True)
class Question:
    """One asking: what is asked, and everything the answer needs to be read.

    Held together rather than passed as three arguments, because the three
    have to travel as one: an answer is filed in the cache under the request
    it was asked with, and a request that met another snapshot would be a key
    for a run that did not happen (`run.py`).
    """

    request: types.AdvisorRequest
    inventory: advisor_run.FrozenInventory
    ctx: types.GoalContext


class _Worker(QObject):
    """One run, off the main thread. Built for one question and thrown away.

    Never touches a widget, not even to read one (AD-006 point 1): everything
    it needs is in the `Question` it was built with, and everything it has to
    say goes out as a signal that Qt delivers into the main thread's event
    loop.

    **What it runs is handed in** and is one of `run.run` and `run.slot_pool`
    (AD-028). This class knows nothing about the difference: both take the
    same five arguments, both may raise `search.Cancelled`, and what comes
    back travels as one object through `ready`.
    """

    #: The whole answer, as an `AdvisorResult`.
    ready = Signal(object)
    #: A run that could not be finished, in one line and without a traceback
    #: (`UI_SPEC` 4.12, AD-006 point 9). An exception that merely propagated
    #: would end the thread silently and leave the window waiting for ever.
    failed = Signal(str)
    #: Always last, whatever happened, so the thread can be quit from one
    #: place. A stopped run says nothing else: `Stopped. Nothing was changed.`
    #: is the controller's and was said at the click (AK-11).
    finished = Signal()

    def __init__(self, question: Question, goals: Mapping[str, types.Goal],
                 answer: Answer) -> None:
        super().__init__()
        self._question = question
        self._goals = goals
        self._answer = answer

    def _was_stopped(self) -> bool:
        """Qt's own interruption flag, read where `run.run` asks.

        The flag rather than a variable of this object: it is set from the
        main thread while this one is computing, and `QThread` is where Qt
        makes that safe.
        """
        thread = self.thread()
        return thread is not None and thread.isInterruptionRequested()

    def work(self) -> None:
        """Answer the one question, and stamp the answer with its asking.

        **The generation is put on here and nowhere else.** AD-006 point 3
        wants every answer to carry back the generation it was asked under,
        and this is the one place that knows both the question and the answer
        -- so an answer function does not have to know that generations
        exist. `run.slot_pool` hands back what `candidates.pool` built, and
        the pre-sort knows nothing about controllers, threads or windows; an
        answer that stamped itself would be a rule kept in as many places as
        there are answer functions, and the one that forgot it would be
        dropped as overtaken every single time, silently.
        """
        try:
            result = self._answer(self._question.request,
                                  self._question.inventory,
                                  self._question.ctx, self._goals,
                                  self._was_stopped)
        except search.Cancelled:
            pass
        except Exception as exc:  # noqa: BLE001 - reported, never raised on
            traceback.print_exc()
            self.failed.emit(str(exc) or exc.__class__.__name__)
        else:
            self.ready.emit(dataclasses.replace(
                result, generation=self._question.request.generation))
        self.finished.emit()


class AdvisorController(QObject):
    """One advisor at a time, debounced, cancellable, and never out of date.

    The window asks with `ask` and hears back on exactly one of `ready`,
    `failed` and `stopped`. Everything else -- which thread, which
    generation, whether the answer was already known -- is settled here, so
    that no drawing code has to remember any of it.

    **Two instances of this class, and the difference is what they were built
    with** (AD-028): `answer` is `run.run` for the Advisor bar and
    `run.slot_pool` for the picker, and `debounce_ms` and the cache's size are
    the other two figures that differ. Nothing here asks which track it is;
    every rule below -- one run at a time, the generation, the cancelling, the
    cache -- is the same rule on both.

    **`ask_and_answer_if_known` is a second way out, not a second way to
    compute** (Nachtrag IX-1.3). A caller that can draw an answer it is handed
    on the spot uses it and is spared the turn of the event loop a signal
    costs; `ask` is unchanged and is what the Advisor bar goes on using.
    """

    #: An answer for the question that is currently being asked. Never for an
    #: overtaken one: those are dropped here, wordlessly (AD-006 point 3).
    ready = Signal(object)
    #: `UI_SPEC` 4.12. One line, no traceback.
    failed = Signal(str)
    #: A run has begun in the background. Not emitted for an answer that was
    #: already known: nothing began, and the window would flash (4.2).
    started = Signal()
    #: The run was abandoned -- `UI_SPEC` 4.5. Emitted in the call that
    #: abandons it, before the worker has noticed anything (AK-11).
    stopped = Signal()

    def __init__(self, parent: QObject | None = None, *,
                 answer: Answer = advisor_run.run,
                 goals: Mapping[str, types.Goal] = GOALS,
                 cache: advisor_run.ResultCache | None = None,
                 debounce_ms: int = DEBOUNCE_MS) -> None:
        super().__init__(parent)
        self._answer = answer
        self._goals = goals
        self._cache = advisor_run.ResultCache() if cache is None else cache
        self._debounce_ms = debounce_ms
        self._generation = 0
        self._pending: Question | None = None
        self._running: Question | None = None
        self._thread: QThread | None = None
        self._worker: _Worker | None = None
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._start_what_is_pending)

    # -- what the window says ----------------------------------------------

    @property
    def generation(self) -> int:
        """Which question is the current one (AD-006 point 3)."""
        return self._generation

    def ask(self, request: types.AdvisorRequest, inventory,
            ctx: types.GoalContext) -> int:
        """Ask this question, after the debounce. Hands back its generation.

        Two fields of the request are filled in here rather than trusted from
        the caller, and both for the same reason -- they are not about what is
        being asked but about *this* asking, and the window cannot know them:
        the generation is this object's counter, and the fingerprint has to be
        of the very snapshot the run will read. Everything else the request
        carries is the window's and is checked against the context by
        `run.run`.

        The snapshot is taken here, in the thread that owns the `Inventory`
        (AD-006 point 8). A run that is overtaken while it computes keeps
        reading exactly what it started with, and the living object stays
        where it belongs.
        """
        self._wait_for(self._question_from(request, inventory, ctx))
        return self._generation

    def ask_and_answer_if_known(self, request: types.AdvisorRequest,
                                inventory,
                                ctx: types.GoalContext) -> object | None:
        """Ask, and hand the answer straight back if it is already known.

        The question is built exactly as `ask` builds it -- the same snapshot,
        the same fingerprint, the same counter raised by one -- and that is
        why the two share `_question_from` rather than each freezing the
        inventory: `frozen_inventory` copies every owned relic and
        `inventory_fingerprint` hashes them, and a caller who asked twice to
        find out whether it need ask at all would pay for both (IX-1.3).

        A hit comes back as the return value and **only** as the return value:
        no `ready`, no `started`, and nothing started. That is what lets a
        window draw a known answer in its first paint instead of drawing an
        empty state and replacing it one turn of the event loop later -- which
        is a wait that flashes, at a measured 30 % of openings (S11-F,
        `UI_SPEC` §2, and it is why IX-1.C is a precondition of the empty grid
        rather than a saving).

        A miss is `None` and is the ordinary course: the question waits for
        the debounce exactly as `ask` leaves it, and the answer arrives on
        `ready` as usual. **The counter goes up either way** (IX-1.4) -- an
        answer from an earlier opening that is still on its way must not
        overwrite the hit that was just handed back.
        """
        question = self._question_from(request, inventory, ctx)
        known = self._cache.get(question.request)
        if known is None:
            self._wait_for(question)
            return None
        self._pending = None
        self._timer.stop()
        self._interrupt_the_running_worker()
        return known

    def _question_from(self, request: types.AdvisorRequest, inventory,
                       ctx: types.GoalContext) -> Question:
        """This asking, whole: the two fields only this object can fill in.

        One place for both ways of asking, so that a question asked the second
        way cannot differ by a field from one asked the first -- and the
        request is the cache key, so a difference of one field is a miss on
        the answer that is lying there.
        """
        frozen = advisor_run.frozen_inventory(inventory, request.problem)
        self._generation += 1
        return Question(
            request=dataclasses.replace(
                request, generation=self._generation,
                inventory_fingerprint=advisor_run.inventory_fingerprint(
                    frozen)),
            inventory=frozen,
            ctx=ctx)

    def _wait_for(self, question: Question) -> None:
        """Let this question be the pending one, after the debounce."""
        self._pending = question
        self._interrupt_the_running_worker()
        self._timer.start(self._debounce_ms)

    def cancel(self) -> bool:
        """Abandon whatever is running or waiting. Says so at once (AK-11).

        The generation goes up first: a run standing between its last check
        and its `emit` has already sent an answer, and raising the generation
        is what keeps that answer off the screen. Then `stopped`, in this
        call, so the window reaches 4.5 within microseconds however long the
        worker takes to notice -- which is what AK-11 asks and all it asks.

        Hands back whether there was anything to stop, so that a window can
        tell `Cancel` on a live run from a click on nothing.
        """
        if self._running is None and self._pending is None:
            return False
        self._generation += 1
        self._pending = None
        self._timer.stop()
        self._interrupt_the_running_worker()
        self.stopped.emit()
        return True

    def before_the_data_changes(self) -> None:
        """Stop everything and forget every answer (AD-006 point 7).

        Called before `model.configure` runs again -- a fresh extraction after
        a game patch, or a rescan of the save. `model` keeps its tables in
        module globals (risk F4), so a run computing during the rebuild
        computes on a half-replaced table; and every stored answer was worked
        out on the old data, which is the one thing a cache must never
        outlive.
        """
        self.cancel()
        self._cache.clear()

    def shutdown(self, timeout_ms: int = SHUTDOWN_WAIT_MS) -> None:
        """Stop the run and wait for it. Only when the window is closing.

        The one place a `wait()` in the main thread is right: the alternative
        is a `QThread` deleted while its run is still going, which ends the
        process rather than the run.
        """
        self._pending = None
        self._timer.stop()
        self._interrupt_the_running_worker()
        thread = self._thread
        if thread is not None:
            thread.wait(timeout_ms)

    # -- how a run is started, and what happens when it ends ----------------

    def _interrupt_the_running_worker(self) -> None:
        """Ask the search to stop, and the thread to end when it has.

        Never `terminate()`: the run holds no lock this program could not
        recover, but it does hold the dataset, and killing a thread mid-read
        is how a half-built answer reaches the screen.
        """
        if self._thread is not None:
            self._thread.requestInterruption()
            self._thread.quit()

    def _start_what_is_pending(self) -> None:
        """Start the waiting question, unless a run is still on the way out.

        At most one run at a time (AD-006 point 4). While the old thread is
        finishing, this does nothing and `_on_thread_finished` comes back to
        it -- rather than building a second `QThread` beside one that is still
        alive.
        """
        if self._pending is None or self._thread is not None:
            return
        question = self._pending
        self._pending = None

        known = self._cache.get(question.request)
        if known is not None:
            self.ready.emit(known)
            return

        self._running = question
        self._thread = QThread()
        self._worker = _Worker(question, self._goals, self._answer)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.work)
        self._worker.ready.connect(self._on_ready)
        self._worker.failed.connect(self._on_failed)
        self._worker.finished.connect(self._thread.quit)
        self._thread.finished.connect(self._on_thread_finished)
        self._thread.start()
        self.started.emit()

    def _on_thread_finished(self) -> None:
        """Clear the run away, then start whatever came in while it ran.

        Not while the debounce is still counting: a question that arrived
        during a run would otherwise start the moment the old run ended, and
        the whole point of the debounce is that a player who is still
        changing their mind is not answered yet (AD-006 point 5).
        """
        self._worker.deleteLater()
        self._thread.deleteLater()
        self._worker = None
        self._thread = None
        self._running = None
        if not self._timer.isActive():
            self._start_what_is_pending()

    def _on_ready(self, result: types.AdvisorResult) -> None:
        """Keep the answer; pass it on only if it is still the question.

        Kept before it is judged, and that is deliberate: an overtaken run
        answered a question that was really asked, and switching back to it
        is exactly the case the cache exists for (AD-007). What makes that
        safe is that the answer is filed under the request that produced it,
        never under the one being asked now.
        """
        self._cache.put(self._running.request, result)
        if result.generation != self._generation:
            return
        self.ready.emit(result)

    def _on_failed(self, reason: str) -> None:
        """A run that could not be finished, if anyone is still waiting.

        Judged by the same generation as an answer: a failure of a question
        nobody is asking any more is not news, and 4.12 on the screen would
        be about a state that no longer exists. The generation comes off the
        question here because there is no answer to carry it back.
        """
        if self._running.request.generation != self._generation:
            return
        self.failed.emit(reason)
