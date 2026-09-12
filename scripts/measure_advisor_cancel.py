"""What asking `should_cancel` once per offered relic costs (SEC-022).

Developer tool. The pre-sort of the advisor used to run to the end because it
was only 43 ms of a 960 ms run on the worst real case
(`scripts/measure_advisor_search.py`); a save the player did not write makes it
the whole run, so the question is now asked inside the loop. This is the recipe
behind the microseconds in the T-098 report, so that they can be repeated
rather than believed (L-001).

    .venv\\Scripts\\python.exe scripts\\measure_advisor_cancel.py

Three figures, because the cost of the check is not one number:

* the **default** check, `types.never_cancelled`, which is what a headless run
  and every test carries;
* the **real** check, `QThread.isInterruptionRequested`, which is what the
  window carries (`advisor/worker.py`) and which is the only one AK-11's 200 ms
  depends on -- a Python `return False` would understate it;
* the **pre-sort itself** on the player's own inventory, with the check and
  with a check that is not there at all, so that the per-call figure can be
  held against the work it sits inside.

The per-call figures are a loop of `CALLS` calls divided by its own duration,
median of `REPEATS`; the loop overhead is measured separately against an empty
call and subtracted, or the figure would be mostly `for`.

Every figure carries the environment it was taken in (L-009). No window is
opened: `QThread` needs a `QCoreApplication` and nothing more. It reads the
player's save read-only and writes nothing.
"""

from __future__ import annotations

import json
import pathlib
import platform
import statistics
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from PySide6.QtCore import QCoreApplication, QThread  # noqa: E402

from nrplanner import inventory as inventory_module  # noqa: E402
from nrplanner import model, paths  # noqa: E402
from nrplanner.advisor import candidates, goals, types  # noqa: E402

#: The same worst real case `measure_advisor_search.py` uses: six free slots,
#: three of them Deep, nothing held.
HERO = "Wylder"
VESSEL = "Wylder's Chalice"
LEVEL = 15
GOAL = "max_damage"
CALLS = 1_000_000
REPEATS = 5
PRE_SORTS = 3


def nothing() -> bool:
    """The floor: a call that does as little as a Python call can do.

    Subtracted from the other two, so what is reported is the check and not
    the loop that drives it.
    """
    return False


def per_call_seconds(check) -> float:
    """Seconds one call to `check` costs, median of `REPEATS` loops."""
    durations = []
    for _ in range(REPEATS):
        start = time.perf_counter()
        for _ in range(CALLS):
            check()
        durations.append((time.perf_counter() - start) / CALLS)
    return statistics.median(durations)


def slots_of(vessel: dict) -> tuple[types.Slot, ...]:
    colours = list(vessel["slots"]) + list(vessel["deep_slots"])
    ordinary = len(vessel["slots"])
    return tuple(types.Slot(index=index, colour=colour, deep=index >= ordinary)
                 for index, colour in enumerate(colours))


def main() -> int:
    app = QCoreApplication.instance() or QCoreApplication([])
    thread = QThread()

    print(f"{platform.platform()}, Python "
          f"{platform.python_version()} ({platform.python_implementation()})")

    floor = per_call_seconds(nothing)
    default = per_call_seconds(types.never_cancelled)
    real = per_call_seconds(thread.isInterruptionRequested)
    print(f"  bare Python call:            {floor * 1e9:8.1f} ns "
          f"({CALLS} calls, median of {REPEATS})")
    print(f"  types.never_cancelled:       {default * 1e9:8.1f} ns, "
          f"{(default - floor) * 1e9:+.1f} ns over the bare call")
    print(f"  QThread.isInterruption...:   {real * 1e9:8.1f} ns, "
          f"{(real - floor) * 1e9:+.1f} ns over the bare call")

    data = json.loads(paths.snapshot_path().read_text(encoding="utf-8"))
    model.configure(data)
    owned = inventory_module.load(data)
    if owned is None:
        print("no save on this machine, so the pre-sort is not measured")
        return 1

    hero = next(h for h in data["heroes"] if h["name"] == HERO)
    vessel = next(v for v in data["vessels"] if v["name"] == VESSEL)
    starting = next(w for w in data["weapons"]
                    if w["id"] == hero["starting_weapon"])
    problem = types.SlotProblem(slots=slots_of(vessel))
    ctx = types.GoalContext(
        data=data, hero=hero, level=LEVEL,
        reference=types.ReferenceArmament(weapon=starting, tier=1,
                                          slot_index=0),
        weighting=goals.DEFAULT_WEIGHTING, weapons_held=(starting,))

    free = len(types.free_slots(problem))
    offered = sum(len(owned.relics_for(slot.colour, slot.deep))
                  for slot in types.free_slots(problem))
    print(f"data_version {data['meta']['data_version']}, "
          f"{owned.relic_count} relics owned, {owned.source_bytes} bytes of "
          f"character slot")
    print(f"{VESSEL}, {HERO} at level {LEVEL}, nothing held, ranked by "
          f"{GOAL}: {free} free slots, {offered} relics offered in all")

    with_check, without = [], []
    for _ in range(PRE_SORTS):
        start = time.perf_counter()
        candidates.pools(owned, problem, ctx, goals.GOALS, GOAL,
                         thread.isInterruptionRequested)
        middle = time.perf_counter()
        candidates.pools(owned, problem, ctx, goals.GOALS, GOAL)
        without.append(time.perf_counter() - middle)
        with_check.append(middle - start)

    asked = statistics.median(with_check)
    quiet = statistics.median(without)
    print(f"  pre-sort, real check:        {asked * 1000:8.1f} ms "
          f"median of {PRE_SORTS}")
    print(f"  pre-sort, default check:     {quiet * 1000:8.1f} ms "
          f"median of {PRE_SORTS}")
    print(f"  one offered relic costs      "
          f"{quiet / offered * 1e6:8.1f} us, of which the check is "
          f"{real * 1e6:.3f} us "
          f"({real / (quiet / offered) * 100:.2f} %)")
    del app
    return 0


if __name__ == "__main__":
    sys.exit(main())
