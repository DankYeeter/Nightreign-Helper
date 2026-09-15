"""How long one picker run of the advisor costs on the real inventory.

Developer tool, and **not a budget**: A6's figure is the `performance-tuner`'s
to set in S11. This is the recipe behind the numbers in the T-037 report, so
that they can be repeated rather than believed (L-001).

    .venv\\Scripts\\python.exe scripts\\measure_advisor_picker.py

Deliberately not part of `scripts/differential/`. That track compares two
trees' *figures* across a mutation; this counts *seconds* on one tree, needs
no second tree and no plan, and folding a stopwatch into a differential
harness would give both jobs a reason to change.

What it measures is AD-018's picker case: every slot but the open one held
(`h = slots - 1`), one pool built for the open slot, scored under both goals.
It reads the player's own save, read-only, and writes nothing.
"""

from __future__ import annotations

import json
import pathlib
import statistics
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from nrplanner import inventory as inventory_module  # noqa: E402
from nrplanner import model, paths  # noqa: E402
from nrplanner.advisor import candidates, goals, types  # noqa: E402

#: The Nightfarer and vessel AD-003 measured its worst real case against:
#: three ordinary slots including a white one, three Deep slots.
HERO = "Wylder"
VESSEL = "Wylder's Chalice"
LEVEL = 15
REPEATS = 3
#: The white slot is colour 4, and it is the case worth watching: the
#: `architect` counted 205 candidates for one against 21-55 for a coloured
#: slot (AD-003, measured 2026-09-01).
WHITE_SLOT = 4


def a_relic_for(owned, slot: types.Slot):
    """Something the player owns that this slot could hold, or None."""
    for relic in owned.relics:
        if relic.is_deep != slot.deep:
            continue
        if slot.colour == WHITE_SLOT or relic.colour == slot.colour:
            return relic
    return None


def held_everywhere_but(owned, slots, open_index: int) -> types.SlotProblem:
    """The picker's question: this slot open, every other one held."""
    held = []
    for slot in slots:
        if slot.index == open_index:
            continue
        relic = a_relic_for(owned, slot)
        held.append(types.HeldSlot(
            index=slot.index,
            relic=None if relic is None else types.HeldRelic(
                relic_id=relic.relic_id, name=relic.name,
                effect_ids=tuple(relic.effect_ids),
                curse_ids=tuple(relic.curse_ids), handle=relic.handle)))
    return types.SlotProblem(slots=tuple(slots), held=tuple(held))


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
    colours = list(vessel["slots"]) + list(vessel["deep_slots"])
    slots = tuple(types.Slot(index=i, colour=colour, deep=i >= 3)
                  for i, colour in enumerate(colours))
    ctx = types.GoalContext(
        data=data, hero=hero, level=LEVEL,
        reference=types.ReferenceArmament(weapon=starting, tier=1,
                                          slot_index=0),
        weighting=goals.DEFAULT_WEIGHTING, weapons_held=(starting,))

    print(f"{owned.relic_count} relics owned, {VESSEL} "
          f"{vessel['slots']} deep {vessel['deep_slots']}, {HERO} at "
          f"level {LEVEL}, both goals scored")
    for slot in slots:
        problem = held_everywhere_but(owned, slots, slot.index)
        runs = []
        for _ in range(REPEATS):
            start = time.perf_counter()
            pool = candidates.pool(owned, problem, slot.index, ctx,
                                   goals.GOALS, "max_damage")
            runs.append(time.perf_counter() - start)
        print(f"  slot {slot.index} colour {slot.colour} "
              f"deep {str(slot.deep):5s}: {len(pool.candidates):4d} "
              f"candidates, {statistics.median(runs) * 1000:6.1f} ms "
              f"median of {REPEATS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
