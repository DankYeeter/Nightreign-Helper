"""How fast `Cancel` shows, and whether the window keeps its event loop.

Developer tool. The recipe behind the milliseconds in the T-082 report, so
that they can be repeated rather than believed (L-001).

    .venv\\Scripts\\python.exe scripts\\measure_advisor_worker.py

Two different figures come out of this, and confusing them is the whole
reason it exists:

* **what the window learns**, from the call to `AdvisorController.cancel` to
  the `stopped` signal. That is what `UI_SPEC` AK-11 is about -- "binnen
  200 ms nach dem Klick sichtbar in Zustand 4.5, **auch wenn der Arbeiter
  laenger zum Beenden braucht**";
* **when the worker really stops**, taken as the last moment it was still
  scoring. The search looks for the interruption between the slot levels
  (AD-003 point 4), so this is the coarser of the two by design.

Both are measured twice over: on a handful of the player's own copies, where
the run is short and predictable, and on the whole save with the vessel
AD-003 names as its worst case. The second is the one that matters and the
first is the one that can be read at a glance; a cancel that is fast because
the run was nearly over would say nothing, which is why the length of a
whole run stands beside every set of figures.

Every figure carries the environment it was taken in (L-009): platform,
interpreter, dataset version, how many relics the question was asked over,
the vessel, the level, K and W.

It reads the player's own save, read-only, and writes nothing.
"""

from __future__ import annotations

import dataclasses
import json
import pathlib
import platform
import statistics
import sys
import time

from PySide6.QtCore import QEventLoop, QTimer
from PySide6.QtWidgets import QApplication

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from nrplanner import inventory as inventory_module  # noqa: E402
from nrplanner import model, paths  # noqa: E402
from nrplanner.advisor import goals, types, worker  # noqa: E402

#: The Nightfarer and vessel AD-003 measured its worst real case against:
#: three ordinary slots including a white one, three Deep slots, nothing held.
HERO = "Wylder"
VESSEL = "Wylder's Chalice"
LEVEL = 15
GOAL = "max_damage"

#: How many copies the small sample keeps, and how many slots it fills. Small
#: enough that a whole run is a few milliseconds, which is what "predictable"
#: means here.
SMALL_COPIES = 4
SMALL_SLOTS = 2

#: How many cancels per moment. Ten is enough for a median and a spread of a
#: figure whose whole claim is "well under 200"; it is not enough to argue
#: about a difference of a millisecond, and nothing here does.
REPEATS = 10


class Timed:
    """The registry, with the moment of every scoring kept.

    The last scoring after a cancel is when the worker was last doing work,
    which is as close as anything outside the thread gets to when it stopped.
    Wrapped around the real registry rather than replaced by a stub: a run
    that scored something else would take a different length of time.
    """

    def __init__(self) -> None:
        self.calls = 0
        self.last = 0.0
        self.registry = {goal_id: dataclasses.replace(goal,
                                                      score=self._watch(goal))
                         for goal_id, goal in goals.GOALS.items()}

    def _watch(self, goal):
        def score(build, ctx):
            self.calls += 1
            self.last = time.perf_counter()
            return goal.score(build, ctx)

        return score


class ASmallSave:
    """A handful of the player's own copies of one colour, nothing invented.

    Which copies fit which slot is still `Inventory.relics_for`'s answer,
    filtered down to the ones kept -- the colour rule is asked and not
    restated, for the reason `candidates.py` gives.

    One colour, because both slots of the small question have to have
    something to choose from: a handful taken across the whole save leaves a
    slot with one candidate, and a run with nothing to decide is not a short
    run, it is a different question.
    """

    def __init__(self, owned, colour: int, keep: int) -> None:
        self._owned = owned
        self.colour = colour
        self.relics = [relic for relic in owned.relics_for(colour, False)
                       if relic.handle is not None][:keep]

    def relics_for(self, colour: int, deep: bool):
        kept = {id(relic) for relic in self.relics}
        return [relic for relic in self._owned.relics_for(colour, deep)
                if id(relic) in kept]


def spin(app: QApplication, until, timeout: float = 30.0) -> bool:
    deadline = time.monotonic() + timeout
    while not until() and time.monotonic() < deadline:
        app.processEvents(QEventLoop.ProcessEventsFlag.AllEvents, 2)
    return until()


def a_question(data: dict, colours, deep_count: int):
    """The context and the request for one vessel shape."""
    hero = next(h for h in data["heroes"] if h["name"] == HERO)
    ordinary = len(colours) - deep_count
    problem = types.SlotProblem(slots=tuple(
        types.Slot(index=index, colour=colour, deep=index >= ordinary)
        for index, colour in enumerate(colours)))
    ctx = types.GoalContext(data=data, hero=hero, level=LEVEL, reference=None,
                            weighting=goals.DEFAULT_WEIGHTING)
    request = types.AdvisorRequest(
        hero_id=hero["id"], level=LEVEL, problem=problem, goal_id=GOAL,
        weighting_id=goals.DEFAULT_WEIGHTING.id,
        data_version=str((data.get("meta") or {}).get("data_version") or ""))
    return ctx, request


def spread(name: str, values: list[float]) -> str:
    """Median, range and standard deviation of a set of milliseconds.

    All zeroes is said in words rather than as a figure: it means the run was
    over before the cancel was asked, which is an answer about the run and
    not a reaction time.
    """
    if not any(values):
        return (f"  {name:<32} nothing was scored after the cancel: the run "
                f"had already finished, n={len(values)}")
    return (f"  {name:<32} median {statistics.median(values):7.2f} ms   "
            f"min {min(values):7.2f}   max {max(values):7.2f}   "
            f"sd {statistics.pstdev(values):6.2f}   n={len(values)}")


def one_whole_run(app, owned, ctx, request) -> None:
    """How long the question costs, and whether the main thread kept going."""
    timed = Timed()
    controller = worker.AdvisorController(goals=timed.registry, debounce_ms=0)
    answers: list[types.AdvisorResult] = []
    ticks: list[int] = []
    controller.ready.connect(answers.append)
    heartbeat = QTimer()
    heartbeat.timeout.connect(lambda: ticks.append(timed.calls))
    heartbeat.start(10)
    began = time.perf_counter()
    controller.ask(request, owned, ctx)
    if not spin(app, lambda: bool(answers)):
        raise SystemExit("the run never answered")
    whole = (time.perf_counter() - began) * 1000
    heartbeat.stop()
    during = [count for count in ticks if 0 < count < timed.calls]
    found = len(answers[0].suggestions)
    print(f"  whole run through the controller: {whole:8.1f} ms, "
          f"{found} suggestion{'' if found == 1 else 's'}, "
          f"{timed.calls} scorings")
    print(f"  the main thread's 10 ms timer fired {len(ticks)} times, "
          f"{len(during)} of them while the run was between its first and "
          f"its last scoring")
    controller.shutdown()


def cancels(app, owned, ctx, request, moment_ms: float) -> None:
    """`REPEATS` cancels this many milliseconds into the run."""
    visible, worker_stop = [], []
    for _ in range(REPEATS):
        timed = Timed()
        controller = worker.AdvisorController(goals=timed.registry,
                                              debounce_ms=0)
        stopped_at: list[float] = []
        controller.stopped.connect(
            lambda: stopped_at.append(time.perf_counter()))
        controller.ask(request, owned, ctx)
        spin(app, lambda: timed.calls > 0)
        started = time.perf_counter()
        spin(app, lambda: (time.perf_counter() - started) * 1000 >= moment_ms)
        asked = time.perf_counter()
        controller.cancel()
        visible.append((stopped_at[0] - asked) * 1000)
        before = timed.last
        spin(app, lambda: False, timeout=1.5)
        worker_stop.append(0.0 if timed.last == before
                           else (timed.last - asked) * 1000)
        controller.shutdown()
    print(f"  cancelled {moment_ms:.0f} ms into the run:")
    print(spread("window learns it stopped", visible))
    print(spread("worker's last scoring after", worker_stop))


def main() -> int:
    data = json.loads(paths.snapshot_path().read_text(encoding="utf-8"))
    model.configure(data)
    owned = inventory_module.load(data)
    if owned is None:
        raise SystemExit("no save was read, so there is nothing to measure")
    vessel = next(v for v in data["vessels"] if v["name"] == VESSEL)
    app = QApplication.instance() or QApplication([])

    print(f"{platform.platform()}, Python {sys.version.split()[0]} "
          f"({platform.python_implementation()})")
    print(f"data_version {data['meta']['data_version']}, "
          f"{owned.relic_count} relics owned, {HERO} at level {LEVEL}, "
          f"ranked by {GOAL}, K={types.DEFAULT_BUDGET.candidates_per_slot} "
          f"W={types.DEFAULT_BUDGET.beam_width}")

    colour = next(relic.colour for relic in owned.relics
                  if relic.handle is not None and not relic.is_deep)
    small = ASmallSave(owned, colour, SMALL_COPIES)
    print("")
    print(f"the small sample: {len(small.relics)} copies, "
          f"{SMALL_SLOTS} free slots of colour {colour}, nothing held")
    ctx, request = a_question(data, [colour] * SMALL_SLOTS, 0)
    one_whole_run(app, small, ctx, request)
    cancels(app, small, ctx, request, 0)

    colours = list(vessel["slots"]) + list(vessel["deep_slots"])
    print("")
    print(f"the whole save: {VESSEL} {vessel['slots']} deep "
          f"{vessel['deep_slots']}, six free slots, nothing held")
    ctx, request = a_question(data, colours, len(vessel["deep_slots"]))
    one_whole_run(app, owned, ctx, request)
    for moment in (100, 500):
        cancels(app, owned, ctx, request, moment)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
