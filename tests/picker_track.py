"""The picker's own advisor track, as a guard has to be able to drive it.

Not a test module: the seven guards of `test_picker_track_guards.py` live on
what is here, and so would any later case about the track.

**Everything here drives the real `AdvisorController` and the real
`SlotAdvice`.** The picker's existing cases state their pool through a stand-in
for `SlotAdvice` (`FakeAdvice` in `test_relic_picker_advisor.py`), which is
right for cases about what the dialog *draws* and wrong for the guards: what
they watch -- the generation counter, the cache hit that answers in the same
call, the one outcome of a question -- lives in the controller, and a stand-in
for the advice replaces exactly the path they are about.

**What is stated instead is the answer function** (AD-028 option D): a
controller runs what it was built with, so a pool named here travels the whole
way a computed one travels -- into the thread, back through `ready`, past the
generation check, into the dialog. It costs no search and states its figures.
"""

from __future__ import annotations

import threading
import time

import pytest
from PySide6.QtCore import QEventLoop

from nrplanner import advisorbar, relicpicker
from nrplanner.advisor import goals as advisor_goals
from nrplanner.advisor import run as advisor_run
from nrplanner.advisor import types, worker

#: How long a held answer waits to be released before it gives up. A fuse
#: against a case that forgot to release it -- a worker blocked for ever holds
#: the one thread the controller has and every later case on the same track
#: would wait behind it. Nothing asserts on it and no guard reads a clock; it
#: is the same device as `ANSWER_FUSE_MS` in `test_relic_picker_advisor.py`.
HELD_FUSE_SECONDS = 30.0

#: The pool order the picker asks under, whatever the player has chosen
#: (Nachtrag IX-2). Named here so a helper does not have to repeat it.
POOL_ORDER = types.PoolOrder(advisor_goals.CANONICAL_POOL_ORDER)

#: The base state a stated pool stands on: one line per direction the picker
#: draws, with the unit that direction's own registry entry hands out. The
#: unit is taken from the registry and not written out, because it is what
#: the card prints after the figure -- a literal here would let the picker
#: print a literal of its own and no case would notice (AK-259).
BASE_LINES = (
    ("max_damage", 100.0, "AR"),
    ("min_damage_taken", 900.0, "effective HP"),
    ("max_attributes", 40.0, advisor_goals.ATTRIBUTE_POINT_UNIT),
)


class StatedAnswers:
    """An answer function of the shape a controller is built with.

    One pool per question, in the order the questions come, and the last one
    over again if there are more questions than pools.

    **It does not stamp the generation, and that is on purpose**: neither does
    `candidates.pool`, and `run.slot_pool` hands back what it built. The
    stamping is the worker's (`_Worker.work`), and an answer function that did
    it for itself would hide the day it stops (W7, the fault T-130 found).

    `hold=True` makes the answer wait in the worker thread until `release()`.
    That is "a track that never answers" (`UI_SPEC` §9) as a state rather than
    as a duration: the question really is out, a thread really is on it, and
    nothing arrives until a case says so.

    `raises=<reason>` makes it a track that cannot answer: the question is
    counted as asked and then gives up with that reason, which is what the
    worker turns into `failed` and the picker into the AK-208 header. A case
    that stated the failure with a function of its own would count nothing,
    and `calls` is what tells a run that happened from one that did not.
    """

    def __init__(self, pools, *, hold: bool = False,
                 raises: str | None = None) -> None:
        self._pools = list(pools)
        if not self._pools:
            raise ValueError("an answer function needs at least one pool")
        self.calls = 0
        self.threads: list[int] = []
        self.handed_back: list[types.SlotPool] = []
        self._raises = raises
        self._released = threading.Event()
        if not hold:
            self._released.set()

    def __call__(self, request, inventory, ctx, goals,
                 should_cancel=None) -> types.SlotPool:
        self.calls += 1
        self.threads.append(threading.get_ident())
        if not self._released.wait(HELD_FUSE_SECONDS):
            raise AssertionError(
                f"the answer was held for {HELD_FUSE_SECONDS} s and never "
                f"released; the case that held it has to release it")
        if self._raises is not None:
            raise ValueError(self._raises)
        pool = self._pools[min(self.calls - 1, len(self._pools) - 1)]
        self.handed_back.append(pool)
        return pool

    def release(self) -> None:
        """Let every held answer through, this one and any later."""
        self._released.set()


class Outcomes:
    """Every outcome signal of one controller, in the order it arrived.

    One list for all three, because what W6 is about is that there is exactly
    **one** of them -- three counters would each be right while the sum was
    two or nought. `started` is kept apart: it says a run began, not how one
    ended.
    """

    def __init__(self, controller: worker.AdvisorController) -> None:
        self.signals: list[tuple[str, object]] = []
        self.started = 0
        controller.ready.connect(lambda result: self.signals.append(
            ("ready", result)))
        controller.failed.connect(lambda reason: self.signals.append(
            ("failed", reason)))
        controller.stopped.connect(lambda: self.signals.append(
            ("stopped", None)))
        controller.started.connect(self._on_started)

    def _on_started(self) -> None:
        self.started += 1

    @property
    def names(self) -> list[str]:
        return [name for name, _payload in self.signals]


def a_track(pools, *, hold: bool = False, raises: str | None = None,
            cache: advisor_run.ResultCache | None = None
            ) -> tuple[worker.AdvisorController, StatedAnswers]:
    """A real picker track over stated answers, with the picker's figures.

    The debounce is the picker's own (`PICKER_DEBOUNCE_MS`, none) rather than
    zero written out here: a guard that stated the figure itself would go on
    passing on the day the constant changed, and the debounce is what decides
    whether a second opening's question waits behind the first.
    """
    answers = StatedAnswers(pools, hold=hold, raises=raises)
    controller = worker.AdvisorController(
        answer=answers,
        cache=advisor_run.ResultCache(worker.PICKER_CACHE_SIZE)
        if cache is None else cache,
        debounce_ms=worker.PICKER_DEBOUNCE_MS)
    return controller, answers


def spin(qapp, until, timeout: float = 10.0) -> bool:
    """Turn the main thread's event loop until something is true.

    A state, never a duration: `timeout` is a fuse against a case that would
    otherwise hang, and no guard asserts on how long anything took (AD-028 --
    no wall clock in the suite).
    """
    deadline = time.monotonic() + timeout
    while not until() and time.monotonic() < deadline:
        qapp.processEvents(QEventLoop.ProcessEventsFlag.AllEvents, 5)
    return until()


def settle(qapp, timeout: float = 0.3) -> None:
    """Turn the event loop with nothing to wait for.

    For the claims that are about something **not** happening: an answer that
    must not arrive has to be given the chance to arrive first, or the guard
    is watching a queue nobody emptied.
    """
    spin(qapp, lambda: False, timeout=timeout)


def slots_that_offer_relics(planner, wanted: int = 1) -> list:
    """`wanted` slots of the open window that really offer cards.

    Skips rather than fails where the save cannot supply them: a runner has no
    Nightreign save, and that is the correct state for a runner to be in.
    """
    found = [slot for slot in planner.active_slots()
             if len(slot.available_items()) >= 4]
    if len(found) < wanted:
        pytest.skip(f"this save offers four relics to {len(found)} slots and "
                    f"this case needs {wanted}")
    return found[:wanted]


def there_is_something_to_ask(planner) -> bool:
    """Whether this window has a save to rank against at all (4.8)."""
    return advisorbar.asking_from(planner, POOL_ORDER) is not None


def pool_for(slot, *, rank_by: str = advisor_goals.CANONICAL_POOL_ORDER,
             unknowns: tuple[str, ...] = ()) -> types.SlotPool:
    """A pool over this slot's own copies, every one of them with a figure.

    The handles come from the slot's own list, so the cards and the pool are
    talking about the same copies -- a pool of invented handles would draw a
    grid of dashes and every claim about "the figures arrived" would be empty.
    The gains descend with the position, which gives the pool a top pick and
    an order without any case having to name figures it does not read.

    **Every direction the picker draws gets a figure and a baseline**, over
    `VALUE_DIRECTIONS` rather than over a pair written out here: a pool that
    is short one direction draws a column of dashes, or raises out of
    `Ranking.unit`, and a guard about the track would fail for a reason that
    has nothing to do with the track (T-194). The directions other than
    `rank_by` get the figure negated, so a case reading the wrong column
    reads a different sign.
    """
    items = [item for item in slot.available_items() if item.handle is not None]
    others = tuple(goal_id for goal_id in relicpicker.VALUE_DIRECTIONS
                   if goal_id != rank_by)
    candidates = tuple(
        types.Candidate(
            slot_index=slot.index, handle=item.handle, relic_id=item.relic_id,
            name=item.name, colour=item.colour, is_deep=item.is_deep,
            effect_ids=tuple(item.effect_ids),
            marginals=((types.Marginal(rank_by, float(len(items) - index)),)
                       + tuple(types.Marginal(other,
                                              -float(len(items) - index))
                               for other in others)))
        for index, item in enumerate(items))
    return types.SlotPool(
        slot_index=slot.index, rank_by=rank_by,
        baseline=tuple(types.Baseline(goal_id, value, unit, ())
                       for goal_id, value, unit in BASE_LINES),
        candidates=candidates, unknowns=unknowns)


def picker_over(slot, track, search_text: str = ""):
    """The picker for this slot, asking the given track through a real advice.

    `SlotAdvice` built here rather than fetched through `advice_for`, which
    would take the window's own track: what a guard states is the answer, and
    the window's track would compute a real one.
    """
    advice = relicpicker.SlotAdvice(slot, slot.window().advisor_bar, track)
    return relicpicker.RelicPicker(slot, slot.icons, search_text,
                                   lambda _text: None, advice=advice)


class CountingPicker(relicpicker.RelicPicker):
    """A picker that counts how often it built the contents of its grid.

    The count is the signal W5 needs and the only thing this class adds
    (L-002: a counter, never a clock). `_refresh` is where the scroll area's
    widget is set -- the waiting line in one branch, the cards in the other --
    so one call is one build of the area, whichever branch it took.

    A class attribute rather than an instance one because the first build
    happens inside `RelicPicker.__init__`, before a subclass could set a field.
    """

    builds = 0

    def _refresh(self) -> None:
        self.builds += 1
        super()._refresh()


def counting_picker_over(slot, track, search_text: str = ""):
    """`picker_over`, with the grid builds counted."""
    advice = relicpicker.SlotAdvice(slot, slot.window().advisor_bar, track)
    return CountingPicker(slot, slot.icons, search_text,
                          lambda _text: None, advice=advice)


def cards_in(dialog) -> list:
    """The relic cards standing in the dialog's scroll area."""
    return dialog.scroll.widget().findChildren(relicpicker.RelicCard)


def tiles_in(dialog) -> list:
    """The custom relic tiles standing in the dialog's scroll area."""
    return dialog.scroll.widget().findChildren(relicpicker.CustomRelicCard)
