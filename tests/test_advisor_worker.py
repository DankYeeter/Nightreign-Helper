"""The run in a thread of its own: what reaches the window, and how fast.

Four claims, and each of them is a thing the advisor would get wrong
silently rather than loudly:

* **the run really leaves the main thread**, which is asked of the scorer --
  it records the thread it was called in -- and not of the fact that a
  `QThread` was created. A worker that was moved into a thread and then
  called from the main one looks identical from the outside and blocks the
  window exactly as before;
* **the window keeps its event loop** while the run goes on: a timer of the
  main thread is counted during a run, so "not blocked" is a number rather
  than an impression;
* **`Cancel` is visible before the worker has heard of it** (`UI_SPEC`
  AK-11, 200 ms), which is measured from the call to the signal and not
  guessed at;
* **an overtaken answer never arrives** (`UI_SPEC` §5.5, 4.7). The case that
  shows it has the first run finish *after* the second question was asked,
  which is the ordering AD-006 point 3 was written for.

The runs are synthetic and small on purpose. What is under test here is the
thread, the debounce and the generation counter; the arithmetic they carry is
`test_advisor_run.py`'s, and a case that waited a second per run could not
afford to state the orderings this file states.
"""

from __future__ import annotations

import dataclasses
import threading
import time

import pytest
from PySide6.QtCore import QEventLoop, QTimer

from nrplanner import errortext
from nrplanner.advisor import goals, run, types, worker

from tests import advisor_cases as advisor
from tests import weapon_damage_cases as cases

DAMAGE = "max_damage"
SURVIVAL = "min_damage_taken"

#: Long enough that a run cannot finish inside one turn of the event loop,
#: short enough that a file of these cases stays under a few seconds. Ten
#: thousand scorings of the synthetic question below at 20 us apiece is about
#: a fifth of a second.
SLOW_SCORE_SECONDS = 0.00002


@pytest.fixture(scope="module")
def wylder(game_data):
    return cases.hero_by_name(game_data, "Wylder")


class Recorder:
    """Every signal of one controller, in the order it arrived."""

    def __init__(self, controller: worker.AdvisorController) -> None:
        self.ready: list[types.AdvisorResult] = []
        self.failed: list[str] = []
        self.started = 0
        self.stopped: list[float] = []
        controller.ready.connect(self.ready.append)
        controller.failed.connect(self.failed.append)
        controller.started.connect(self._on_started)
        controller.stopped.connect(lambda: self.stopped.append(
            time.perf_counter()))

    def _on_started(self) -> None:
        self.started += 1


class Watched:
    """The registry, with every scoring watched and optionally slowed.

    Wrapped rather than replaced: what a goal is worth is `goals.py`'s and a
    scorer invented here would answer a question this file is not asking. The
    wrapper records which thread did the work, which is the one thing a case
    cannot see from the outside.
    """

    def __init__(self, *, delay: float = 0.0, raises: str = "") -> None:
        self.threads: set[int] = set()
        self.calls = 0
        self._delay = delay
        self._raises = raises
        self.registry = {goal_id: dataclasses.replace(goal,
                                                      score=self._watch(goal))
                         for goal_id, goal in goals.GOALS.items()}

    def _watch(self, goal):
        def score(build, ctx):
            self.threads.add(threading.get_ident())
            self.calls += 1
            if self._raises:
                raise ValueError(self._raises)
            if self._delay:
                time.sleep(self._delay)
            return goal.score(build, ctx)

        return score


def spin(qapp, until, timeout: float = 10.0) -> bool:
    """Turn the main thread's event loop until something is true.

    This is what the window does while a run goes on -- it processes events --
    so a case that spins here is watching the same thing the player sees.
    """
    deadline = time.monotonic() + timeout
    while not until() and time.monotonic() < deadline:
        qapp.processEvents(QEventLoop.ProcessEventsFlag.AllEvents, 5)
    return until()


def wait_without_the_event_loop(until, timeout: float = 10.0) -> bool:
    """Wait for the worker while the main thread processes **nothing**.

    This is the whole of the ordering AD-006 point 3 is written for. A run
    that was interrupted raises and says nothing, so a case that let the
    event loop turn would be watching the interruption and calling it the
    generation counter -- the two look identical from the outside and only
    one of them survives a run that got past its last check. Holding the
    events back puts the answer in the queue and the question that overtakes
    it in front of the delivery.
    """
    deadline = time.monotonic() + timeout
    while not until() and time.monotonic() < deadline:
        time.sleep(0.002)
    return until()


def scorings_of(question) -> int:
    """How many scorings this question costs, run here in the main thread.

    The number is what tells "the worker is still computing" from "the worker
    is past its last cancel check", and it is measured on the same question
    rather than guessed: it changes with the inventory, the vessel and the
    registry.
    """
    inventory, _problem, ctx, request = question
    counted = Watched()
    run.run(request, inventory, ctx, counted.registry)
    return counted.calls


@pytest.fixture
def question(game_data, wylder):
    """One small question, and the material it is asked against."""
    return advisor.a_question(game_data, wylder, count=4)


@pytest.fixture
def controller(qapp):
    """A controller that answers at once, unless a case asks for a wait.

    The debounce is zero here and set by name in the two cases that are about
    it: every other case would otherwise pay 250 ms to test something else,
    and a quarter of a second per case is how a suite stops being run.
    """
    made: list[worker.AdvisorController] = []

    def build(**kwargs):
        kwargs.setdefault("debounce_ms", 0)
        controller = worker.AdvisorController(**kwargs)
        made.append(controller)
        return controller

    yield build
    for controller in made:
        controller.shutdown()


# -- the run leaves the main thread -----------------------------------------

def test_the_run_happens_in_another_thread_and_the_answer_comes_back(
        qapp, controller, question):
    """AD-006 point 1, asked of the scorer rather than of the plumbing."""
    inventory, problem, ctx, request = question
    watched = Watched()
    advisor_controller = controller(goals=watched.registry)
    seen = Recorder(advisor_controller)

    advisor_controller.ask(request, inventory, ctx)
    assert spin(qapp, lambda: bool(seen.ready)), "no answer arrived"

    assert watched.calls, "nothing was scored, so no thread did the work"
    assert threading.get_ident() not in watched.threads, (
        "the scoring ran in the main thread, so the window was blocked for "
        "the whole of it")
    assert seen.ready[0].suggestions
    assert seen.started == 1


def test_the_window_keeps_its_event_loop_while_the_run_goes_on(qapp,
                                                               controller,
                                                               question):
    """A6, as a count rather than an impression.

    A timer of the main thread ticks every 5 ms. If the run held the main
    thread, the ticks would all arrive after it instead of during it -- which
    is what `firstrun`'s `processEvents` loop does and what §5.4 forbids
    here.
    """
    inventory, problem, ctx, request = question
    watched = Watched(delay=SLOW_SCORE_SECONDS)
    advisor_controller = controller(goals=watched.registry)
    seen = Recorder(advisor_controller)
    ticks = []
    timer = QTimer()
    timer.timeout.connect(lambda: ticks.append(watched.calls))
    timer.start(5)

    advisor_controller.ask(request, inventory, ctx)
    assert spin(qapp, lambda: bool(seen.ready)), "no answer arrived"
    timer.stop()

    during = [count for count in ticks if 0 < count < watched.calls]
    assert during, (
        f"the main thread's timer fired {len(ticks)} times and never while "
        f"the run was between its first and its last scoring, so the run had "
        f"the main thread")


# -- cancelling -------------------------------------------------------------

def test_cancel_is_visible_at_once_however_long_the_worker_takes(qapp,
                                                                 controller,
                                                                 question):
    """AK-11: within 200 ms of the click, and this is the whole of that time.

    Two claims, and the timing alone is not enough for either. A run that
    happens to be nearly over would stop inside 200 ms whatever the
    controller did, so this case also asks that the worker was **still
    working** when the window was told: the scorings that arrive after the
    signal are the proof that nothing waited for them. That is the half
    AK-11 words as "even if the worker takes longer to finish".
    """
    inventory, problem, ctx, request = question
    watched = Watched(delay=SLOW_SCORE_SECONDS)
    advisor_controller = controller(goals=watched.registry)
    seen = Recorder(advisor_controller)
    at_the_signal = []
    advisor_controller.stopped.connect(
        lambda: at_the_signal.append(watched.calls))

    advisor_controller.ask(request, inventory, ctx)
    assert spin(qapp, lambda: watched.calls > 0), "the run never started"
    asked_at = time.perf_counter()
    assert advisor_controller.cancel() is True

    assert len(seen.stopped) == 1
    visible = seen.stopped[0] - asked_at
    assert visible < 0.2, (
        f"the window learned it was stopped after {visible * 1000:.1f} ms, "
        f"and AK-11 allows 200")
    spin(qapp, lambda: False, timeout=0.5)
    assert watched.calls > at_the_signal[0], (
        f"the run had scored {at_the_signal[0]} times when the window was "
        f"told it had stopped and {watched.calls} in the end, so the window "
        f"was told after the worker had finished rather than before it "
        f"noticed")
    assert not seen.ready, "a cancelled run put an answer on the screen"


def test_a_cancelled_run_never_answers_even_if_it_finishes(qapp, controller,
                                                           question):
    """Cancelling alone is not enough, which is why the generation exists.

    A run standing between its last check and its `emit` has already sent its
    answer. This case lets the worker run to the end after the cancel and
    asks that nothing reaches the window (AD-006 point 3).
    """
    inventory, problem, ctx, request = question
    costs = scorings_of(question)
    watched = Watched()
    advisor_controller = controller(goals=watched.registry)
    seen = Recorder(advisor_controller)

    advisor_controller.ask(request, inventory, ctx)
    assert spin(qapp, lambda: seen.started == 1), "the run never started"
    assert wait_without_the_event_loop(lambda: watched.calls >= costs), (
        f"the run did {watched.calls} of its {costs} scorings, so it was "
        f"still interruptible and the cancel below would be caught by the "
        f"interruption rather than by the generation")
    advisor_controller.cancel()
    spin(qapp, lambda: False, timeout=0.5)

    assert seen.ready == [], (
        "the answer of a cancelled run reached the window")
    assert len(seen.stopped) == 1


def test_cancelling_when_nothing_runs_says_nothing(qapp, controller):
    """`Cancel` on a click that stopped nothing would put 4.5 on a window
    that never left 4.1.
    """
    advisor_controller = controller()
    seen = Recorder(advisor_controller)

    assert advisor_controller.cancel() is False
    assert seen.stopped == []


# -- an overtaken answer ----------------------------------------------------

def test_an_overtaken_answer_never_reaches_the_window(qapp, controller,
                                                      question, game_data,
                                                      wylder):
    """`UI_SPEC` §5.5 and 4.7: the build changed while this was working out.

    Two questions, and the first is allowed to finish. What tells them apart
    on arrival is the generation and nothing else -- both answers are
    correct, and the first one is about a build the player has left.
    """
    inventory, problem, ctx, request = question
    other = advisor.a_question(game_data, wylder, count=4,
                                 goal_id=SURVIVAL)
    costs = scorings_of(question)
    watched = Watched()
    advisor_controller = controller(goals=watched.registry)
    seen = Recorder(advisor_controller)

    first = advisor_controller.ask(request, inventory, ctx)
    assert spin(qapp, lambda: seen.started == 1), "the run never started"
    assert wait_without_the_event_loop(lambda: watched.calls >= costs), (
        f"the first run did {watched.calls} of its {costs} scorings, so it "
        f"is still interruptible and this case would watch the interruption "
        f"instead of the generation")
    second = advisor_controller.ask(other[3], other[0], other[2])
    assert spin(qapp, lambda: len(seen.ready) == 1), "no answer arrived"
    spin(qapp, lambda: False, timeout=0.3)

    assert second > first
    assert [result.goal_id for result in seen.ready] == [SURVIVAL], (
        "the window was handed an answer to a question it had left")
    assert seen.ready[0].generation == second


def test_the_generation_rises_with_every_question_and_every_cancel(
        qapp, controller, question):
    """AD-006 point 3 couples the counter to the key: what changes the one
    makes a running answer stale, and the other way round.
    """
    inventory, problem, ctx, request = question
    advisor_controller = controller()

    first = advisor_controller.ask(request, inventory, ctx)
    second = advisor_controller.ask(request, inventory, ctx)
    advisor_controller.cancel()

    assert [first, second] == [1, 2]
    assert advisor_controller.generation == 3


# -- the debounce -----------------------------------------------------------

def test_a_burst_of_questions_is_one_run(qapp, controller, question):
    """AD-006 point 5: a dragged level slider must not start forty runs.

    The event loop turns **between** the questions, which is what makes this
    a burst rather than five calls in a row: a slider sends its steps through
    the same loop the timer is waiting in, so a controller that started a run
    per step would get to start them. Five turns of 5 ms sit well inside the
    100 ms the controller is waiting, and the case says so rather than
    trusting it.
    """
    inventory, problem, ctx, request = question
    watched = Watched()
    advisor_controller = controller(goals=watched.registry, debounce_ms=100)
    seen = Recorder(advisor_controller)

    began = time.perf_counter()
    for level in range(1, 6):
        advisor_controller.ask(dataclasses.replace(request, level=level),
                               inventory, dataclasses.replace(ctx,
                                                              level=level))
        spin(qapp, lambda: False, timeout=0.005)
    burst = time.perf_counter() - began

    assert burst < 0.1, (
        f"the burst took {burst * 1000:.0f} ms and the controller waits 100, "
        f"so the questions were not one burst and this case would say "
        f"nothing")
    assert spin(qapp, lambda: bool(seen.ready)), "no answer arrived"
    spin(qapp, lambda: False, timeout=0.3)

    assert seen.started == 1, (
        f"five questions in one burst started {seen.started} runs")
    assert seen.ready[0].generation == advisor_controller.generation


# -- what was already worked out --------------------------------------------

def test_a_question_already_answered_is_not_computed_again(qapp, controller,
                                                           question):
    """AD-007: switching back and forth is what the cache is for.

    The second asking is the same question with a new generation, and the
    answer arrives carrying **that** generation -- an answer stamped with the
    generation of the first run would be dropped as overtaken by the very
    controller that fetched it.
    """
    inventory, problem, ctx, request = question
    watched = Watched()
    advisor_controller = controller(goals=watched.registry)
    seen = Recorder(advisor_controller)

    advisor_controller.ask(request, inventory, ctx)
    assert spin(qapp, lambda: bool(seen.ready))
    computed = watched.calls

    second = advisor_controller.ask(request, inventory, ctx)
    assert spin(qapp, lambda: len(seen.ready) == 2)

    assert watched.calls == computed, (
        "the same question was worked out a second time")
    assert seen.started == 1, "a run was started for an answer already known"
    assert seen.ready[1].generation == second
    assert seen.ready[1] == dataclasses.replace(seen.ready[0],
                                                generation=second)


def test_a_data_rebuild_stops_the_run_and_forgets_every_answer(qapp,
                                                               controller,
                                                               question):
    """AD-006 point 7 against risk F4.

    `model` keeps its tables in module globals, so a run computing during a
    rebuild computes on a half-replaced table -- and every stored answer was
    worked out on data that is about to be gone.
    """
    inventory, problem, ctx, request = question
    watched = Watched()
    advisor_controller = controller(goals=watched.registry)
    seen = Recorder(advisor_controller)

    advisor_controller.ask(request, inventory, ctx)
    assert spin(qapp, lambda: bool(seen.ready))
    computed = watched.calls

    advisor_controller.before_the_data_changes()
    advisor_controller.ask(request, inventory, ctx)
    assert spin(qapp, lambda: len(seen.ready) == 2)

    assert watched.calls > computed, (
        "the answer from before the rebuild was handed back")
    assert seen.started == 2


# -- a run that could not be finished ----------------------------------------

def test_a_run_that_raises_is_a_signal_and_not_a_silence(qapp, controller,
                                                         question):
    """AD-006 point 9: an exception in a thread ends it without a word, and
    the window would wait for an answer that is never coming.

    **What comes back is a sentence of this repository, not the exception's
    own words** (A8, QA-211, closed here by T-191). The scorer raises a
    `ValueError` -- a class of `builtins`, indistinguishable from one Qt or
    pycryptodome raised, and on a German Windows one that would carry German
    into the bar -- so the words it was raised with are exactly what must
    *not* arrive. That they do not is asserted both ways round: the raised
    text is absent, and the sentence `errortext` maps the class on to is
    what the window is handed.
    """
    inventory, problem, ctx, request = question
    raised = "the dataset lost a curve"
    watched = Watched(raises=raised)
    advisor_controller = controller(goals=watched.registry)
    seen = Recorder(advisor_controller)

    advisor_controller.ask(request, inventory, ctx)
    assert spin(qapp, lambda: bool(seen.failed)), "no failure was reported"

    assert seen.ready == []
    assert seen.failed[0] == errortext.in_english(ValueError(raised)), (
        "the bar was handed something other than the one English sentence "
        "this program has for a failure of that class (A8)")
    assert raised not in seen.failed[0], (
        "the exception's own words reached the window; on a German Windows "
        "those words are German and no guard of A8 can see them (QA-211)")
    assert "Traceback" not in seen.failed[0], (
        "`UI_SPEC` 4.12: no stacktrace in the window")


def test_a_failure_of_a_question_nobody_asks_any_more_is_not_shown(
        qapp, controller, question):
    """4.12 would otherwise be about a state that no longer exists."""
    inventory, problem, ctx, request = question
    watched = Watched(raises="the dataset lost a curve")
    advisor_controller = controller(goals=watched.registry)
    seen = Recorder(advisor_controller)

    advisor_controller.ask(request, inventory, ctx)
    assert spin(qapp, lambda: seen.started == 1), "the run never started"
    assert wait_without_the_event_loop(lambda: watched.calls > 0), (
        "the run never got as far as raising, so nothing was reported and "
        "this case would be watching a run that did not happen")
    advisor_controller.cancel()
    spin(qapp, lambda: False, timeout=0.5)

    assert seen.failed == []


# -- the snapshot -----------------------------------------------------------

def test_the_thread_reads_a_snapshot_and_not_the_living_inventory(
        qapp, controller, game_data, wylder):
    """AD-006 point 8, at the one boundary where it can be shown.

    The `Inventory` handed to `ask` is changed the moment the question is
    asked. What the run reads was frozen in the main thread, so the answer is
    about the relics the player had when they asked.
    """
    inventory = advisor.make_inventory(game_data, wylder, count=4)
    problem = advisor.problem([advisor.RED, advisor.RED])
    ctx = advisor.context(game_data, wylder,
                          reference=advisor.scaling_armament(game_data,
                                                             wylder))
    frozen = run.frozen_inventory(inventory, problem)
    request = advisor.request_for(problem, ctx, frozen)
    advisor_controller = controller()
    seen = Recorder(advisor_controller)

    advisor_controller.ask(request, inventory, ctx)
    inventory.relics.clear()
    assert spin(qapp, lambda: bool(seen.ready)), "no answer arrived"

    assert seen.ready[0].suggestions[0].choices, (
        "the run read the emptied inventory, so what it answered about is "
        "not what was asked about")


# -- two tracks, one class (AD-028, Nachtrag IX-1) --------------------------


class Answering:
    """An answer function of the shape a controller is built with.

    A `SlotPool` rather than an `AdvisorResult`, because that is what the
    picker's track answers with. **And it does not stamp the generation on
    purpose**: `candidates.pool` does not, `run.slot_pool` hands back what it
    built, and an answer that arrives carrying 0 is judged overtaken and
    dropped without a word -- every time, on every question, and the only
    sign of it is a dialog that waits for ever. The worker stamps it, and
    this class is what says so.
    """

    def __init__(self) -> None:
        self.calls = 0
        self.threads: list[int] = []

    def __call__(self, request, inventory, ctx, goals, should_cancel=None):
        self.calls += 1
        self.threads.append(threading.get_ident())
        return types.SlotPool(slot_index=0, rank_by=request.goal_id)


def test_a_controller_runs_the_answer_it_was_built_with(qapp, controller,
                                                        question):
    """AD-028 option D: the difference between the two tracks is an argument.

    Nothing in `worker.py` names either of them. A second thread path for the
    picker would have been a second place for the generation, the debounce
    and the cancelling to be got right.
    """
    inventory, _problem, ctx, request = question
    answering = Answering()
    track = controller(answer=answering)
    seen = Recorder(track)

    track.ask(request, inventory, ctx)
    assert spin(qapp, lambda: bool(seen.ready))

    assert answering.calls == 1
    assert answering.threads[0] != threading.get_ident(), (
        "the picker's answer was worked out in the main thread")
    assert isinstance(seen.ready[0], types.SlotPool)
    assert seen.ready[0].generation == track.generation, (
        "the answer did not come back carrying the generation it was asked "
        "under, so the window has no way to know whose answer it is")


def test_a_known_answer_comes_back_in_the_same_call(qapp, controller,
                                                    question):
    """Nachtrag IX-1.3: the hit is the return value, and nothing is started.

    This is what lets a dialog draw a known answer in its **first** paint.
    Without it the empty grid appears and is replaced one turn of the event
    loop later, at a measured 30 % of openings -- a whole grid flashing up
    and going again, which is why IX-1.C is a precondition of the empty grid
    and not a saving.
    """
    inventory, _problem, ctx, request = question
    answering = Answering()
    track = controller(answer=answering)
    seen = Recorder(track)

    track.ask(request, inventory, ctx)
    assert spin(qapp, lambda: bool(seen.ready))

    known = track.ask_and_answer_if_known(request, inventory, ctx)

    assert known is not None, "the answer just given was not recognised"
    assert answering.calls == 1, "a known answer was worked out again"
    assert seen.started == 1, "a run was started for an answer already known"
    assert len(seen.ready) == 1, (
        "the hit went out as a signal as well as coming back")
    assert known.generation == track.generation, (
        "the hit carries the generation of the question that fetched it")


def test_the_counter_rises_for_an_answer_that_was_known(qapp, controller,
                                                        question):
    """Nachtrag IX-1.4: a hit is a question like any other.

    An answer from an earlier opening that is still on its way would
    otherwise overwrite the one just handed back -- the same cards, plausible
    figures, and nothing on the screen to say which question they belong to.
    """
    inventory, _problem, ctx, request = question
    track = controller(answer=Answering())
    seen = Recorder(track)

    track.ask(request, inventory, ctx)
    assert spin(qapp, lambda: bool(seen.ready))
    before = track.generation

    track.ask_and_answer_if_known(request, inventory, ctx)

    assert track.generation == before + 1


def test_a_question_nobody_has_answered_yet_is_asked_as_usual(qapp,
                                                              controller,
                                                              question):
    """The other half of IX-1.3: a miss is `None` and takes the usual way."""
    inventory, _problem, ctx, request = question
    answering = Answering()
    track = controller(answer=answering)
    seen = Recorder(track)

    assert track.ask_and_answer_if_known(request, inventory, ctx) is None
    assert spin(qapp, lambda: bool(seen.ready))
    assert answering.calls == 1
    assert seen.started == 1


def test_the_snapshot_is_taken_once_however_the_question_is_asked(
        qapp, controller, question):
    """IX-1.3's reason for one private place: the freezing is not free.

    `frozen_inventory` copies every owned relic and `inventory_fingerprint`
    hashes them. A caller that asked twice -- once to find out whether it
    need ask at all, once to ask -- would pay for both, and the two would be
    two snapshots of one moment.
    """
    inventory, _problem, ctx, request = question
    counted = []

    class Counting:
        """The frozen inventory, counting how often it was taken."""

        def __init__(self, wrapped):
            self.relics = wrapped.relics
            self._wrapped = wrapped

        def relics_for(self, colour, deep):
            counted.append((colour, deep))
            return self._wrapped.relics_for(colour, deep)

    track = controller(answer=Answering())
    track.ask_and_answer_if_known(request, Counting(inventory), ctx)
    once = len(counted)
    assert once, "nothing was frozen at all"

    counted.clear()
    track.ask(request, Counting(inventory), ctx)
    assert len(counted) == once, (
        "the two ways of asking freeze the inventory differently often")
