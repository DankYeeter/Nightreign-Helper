"""How long one `Optimize` run of the advisor costs on the real inventory.

Developer tool, and **not a budget**: A6's figure is the `performance-tuner`'s
to set in S11 (AD-003 leaves K and W to it). This is the recipe behind the
seconds in the T-067 report, so that they can be repeated rather than believed
(L-001).

    .venv\\Scripts\\python.exe scripts\\measure_advisor_search.py

The companion of `scripts/measure_advisor_picker.py`, which times AD-018's
picker case -- one slot open, every other one held. This one times the other
question: the whole beam over the free slots, on the worst real case AD-003
names, `Wylder's Chalice` with Deep of Night, six slots including a white one,
with nothing held.

Every figure it prints carries the environment it was taken in, because a
second of Python is a statement about a machine and an interpreter and not
about this code (L-009): platform, interpreter, dataset version, how many
relics the save holds, the vessel, the level, and K and W.

It reads the player's own save, read-only, and writes nothing.
"""

from __future__ import annotations

import json
import pathlib
import platform
import statistics
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from nrplanner import inventory as inventory_module  # noqa: E402
from nrplanner import model, paths  # noqa: E402
from nrplanner.advisor import candidates, goals, search, types  # noqa: E402

#: The Nightfarer and vessel AD-003 measured its worst real case against:
#: three ordinary slots including a white one, three Deep slots.
HERO = "Wylder"
VESSEL = "Wylder's Chalice"
LEVEL = 15
REPEATS = 3
GOAL = "max_damage"


def counting(scorer: search.Scorer) -> tuple[search.Scorer, list[int]]:
    """The same scorer, plus how often it was asked.

    AD-003 costs the beam as `levels x W x K` evaluations and measured 3 929
    of them for this vessel at K=20/W=40. A stopwatch alone cannot say whether
    a run that is fast is fast because the search is cheap or because it
    branched less than it was asked to.
    """
    asked = [0]

    def score(assignment):
        asked[0] += 1
        return scorer(assignment)

    return score, asked


def slots_of(vessel: dict) -> tuple[types.Slot, ...]:
    colours = list(vessel["slots"]) + list(vessel["deep_slots"])
    ordinary = len(vessel["slots"])
    return tuple(types.Slot(index=index, colour=colour, deep=index >= ordinary)
                 for index, colour in enumerate(colours))


def main() -> int:
    data = json.loads(paths.snapshot_path().read_text(encoding="utf-8"))
    model.configure(data)
    owned = inventory_module.load(data)
    if owned is None:
        print("no save on this machine, so there is nothing to measure")
        return 1

    hero = next(h for h in data["heroes"] if h["name"] == HERO)
    vessel = next(v for v in data["vessels"] if v["name"] == VESSEL)
    starting = next(w for w in data["weapons"]
                    if w["id"] == hero["starting_weapon"])
    slots = slots_of(vessel)
    problem = types.SlotProblem(slots=slots)
    ctx = types.GoalContext(
        data=data, hero=hero, level=LEVEL,
        reference=types.ReferenceArmament(weapon=starting, tier=1,
                                          slot_index=0),
        weighting=goals.DEFAULT_WEIGHTING, weapons_held=(starting,))
    budget = types.DEFAULT_BUDGET

    print(f"{platform.platform()}, Python "
          f"{platform.python_version()} ({platform.python_implementation()})")
    print(f"data_version {data['meta']['data_version']}, "
          f"{owned.relic_count} relics owned")
    print(f"{VESSEL} {vessel['slots']} deep {vessel['deep_slots']}, {HERO} "
          f"at level {LEVEL}, nothing held, ranked by {GOAL}, "
          f"K={budget.candidates_per_slot} W={budget.beam_width}")

    presorts, searches, evaluations, results = [], [], [], []
    for _ in range(REPEATS):
        start = time.perf_counter()
        pools = candidates.pools(owned, problem, ctx, goals.GOALS, GOAL)
        middle = time.perf_counter()
        scorer, asked = counting(
            search.goal_scorer(problem, ctx, goals.GOALS[GOAL]))
        found = search.beam(problem, pools, budget, scorer)
        done = time.perf_counter()
        presorts.append(middle - start)
        searches.append(done - middle)
        evaluations.append(asked[0])
        results.append(found)

    print(f"  pool sizes: "
          f"{[len(pool.candidates) for pool in pools]}")
    print(f"  pre-sort:   {statistics.median(presorts) * 1000:8.1f} ms "
          f"median of {REPEATS}")
    print(f"  beam:       {statistics.median(searches) * 1000:8.1f} ms "
          f"median of {REPEATS}, "
          f"{statistics.median(evaluations):.0f} evaluations")
    print(f"  whole run:  "
          f"{statistics.median(p + s for p, s in zip(presorts, searches)) * 1000:8.1f} ms median")
    print(f"  {len(results[0])} suggestions, best "
          f"{results[0][0].score.display}, "
          f"{len(results[0][0].choices)} of {len(slots)} slots filled")
    print(f"  the three runs agree: "
          f"{all(run == results[0] for run in results)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
