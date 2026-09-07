"""What the advisor's own sentences come out as on the real save.

Developer tool. It answers the two questions T-081 hands over as acceptance
and it answers them with a recipe rather than a claim (L-001):

1. **how often each filling occurs** -- the six silent-effect fillings and the
   three curse fillings, each with its denominator, counted over every relic
   the player owns;
2. **how many lines a suggestion is**, counted separately for the suggestion
   block and for the `Why` dialog, which is AK-161. The two differ because a
   silent effect line waits in the dialog while every curse stands in the
   block (Director, 06.09.2026).

    .venv\\Scripts\\python.exe scripts\\measure_advisor_language.py

**Measuring environment**, named because a count without one is not a
measurement (L-009): the dataset out of `paths.snapshot_path()` with whatever
`data_version` it carries, the player's own save read through
`inventory.load` (read-only, nothing is written), Nightfarer **Wylder** at
level 15, his starting armament as the reference **and** as the only armament
held, no condition declared met, `goals.DEFAULT_WEIGHTING`. All figures are
**lines and characters, never pixels**: what a line becomes on the screen is
AK-160's question and needs the running window.

Part 1 puts one relic in one slot against an empty base state, so it cannot
see an effect that is silent only because a second copy already counted, and
it sees one Nightfarer's answer to the ownership question. Both limits are
printed with the counts.
"""

from __future__ import annotations

import collections
import json
import pathlib
import statistics
import sys
from collections.abc import Sequence

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from nrplanner import inventory as inventory_module  # noqa: E402
from nrplanner import model, paths  # noqa: E402
from nrplanner.advisor import candidates, explain, goals, search, types  # noqa: E402
from nrplanner.advisor.evaluate import evaluate  # noqa: E402

DEFAULT_HERO = "Wylder"
#: The vessel part 2 fills, named from the Nightfarer: the Chalice is the
#: six-slot one, so it is the widest question that Nightfarer can be asked.
VESSEL_OF = "{hero}'s Chalice"
LEVEL = 15
GOAL = "max_damage"
#: The white slot is colour 4: it takes a relic of any colour, so one slot of
#: it can stand in for every relic the player owns.
WHITE_SLOT = 4

FILLINGS = {
    types.SILENT_ANOTHER_NIGHTFARER: "(a)  works only for another Nightfarer",
    types.SILENT_ALREADY_COUNTED: "(a2) another copy is already counted",
    types.SILENT_UNDER_A_CONDITION: "(b)  waits on a condition",
    types.SILENT_ARMAMENT_BOUND: "(c)  depends on the armaments carried",
    types.SILENT_NO_NUMBER_HERE: "(d)  no number here",
    types.SILENT_NOT_IN_THE_DATA: "(e)  not in the game data",
}


def a_context(data: dict, hero: dict) -> types.GoalContext:
    starting = next(w for w in data["weapons"]
                    if w["id"] == hero["starting_weapon"])
    return types.GoalContext(
        data=data, hero=hero, level=LEVEL,
        reference=types.ReferenceArmament(weapon=starting, tier=1,
                                          slot_index=0),
        weighting=goals.DEFAULT_WEIGHTING, weapons_held=(starting,))


def one_slot(deep: bool) -> types.SlotProblem:
    return types.SlotProblem(
        slots=(types.Slot(index=0, colour=WHITE_SLOT, deep=deep),))


def every_relic(data: dict, owned, ctx: types.GoalContext):
    """One group per owned relic, that relic alone in one slot.

    Hands back the build beside the group: the fillings are counted off the
    lines and the list 4.9b off `Build.situational`, and the two readings
    have to come out of one run to be comparable at all (AK-181).
    """
    goal = goals.GOALS[GOAL]
    for relic in owned.relics:
        problem = one_slot(relic.is_deep)
        copy = types.Candidate(
            slot_index=0, handle=relic.handle or 0, relic_id=relic.relic_id,
            name=relic.name, colour=relic.colour, is_deep=relic.is_deep,
            effect_ids=tuple(relic.effect_ids),
            curse_ids=tuple(relic.curse_ids))
        base = evaluate(problem, (), ctx)
        built = evaluate(problem, (copy,), ctx)
        groups = explain.reasons(problem, (copy,), base, built, ctx, goal)
        yield relic, groups[0], built


def count_the_fillings(data: dict, owned, ctx: types.GoalContext) -> None:
    silent = collections.Counter()
    curses = collections.Counter()
    relics_with_a_silent_effect = 0
    relics_with_no_figure_at_all = 0
    headings = collections.Counter()
    effects = 0
    curse_lines = 0
    left_out = 0
    worst = ("", 0, 0)
    for relic, group, built in every_relic(data, owned, ctx):
        left_out += len(explain.not_counted(built))
        quiet = [line for line in group.lines if not line.is_curse
                 and line.silence != types.CARRIES_A_FIGURE]
        effects += group.effects_total
        curse_lines += len([line for line in group.lines if line.is_curse])
        for line in quiet:
            silent[line.silence] += 1
        for line in group.lines:
            if not line.is_curse:
                continue
            if line.silence != types.CARRIES_A_FIGURE:
                curses["(iii) no number here shows what this costs"] += 1
            elif line.text.endswith("this figure does not count it."):
                curses["(ii)  moved a figure this direction does not rank"] += 1
            else:
                curses["(i)   moved a figure the direction ranks"] += 1
        relics_with_a_silent_effect += bool(quiet)
        relics_with_no_figure_at_all += (group.effects_with_a_figure == 0
                                         and group.effects_total > 0)
        headings[group.count_line.split(" ")[0]] += 1
        assert group.effects_total - group.effects_with_a_figure == len(quiet)
        card = len(group.lines) + 2
        in_block = len([line for line in group.lines
                        if types.drawn_in_the_block(line)]) + 2
        if card > worst[1]:
            worst = (relic.name, card, in_block)

    total_silent = sum(silent.values())
    print(f"\n{owned.relic_count} relics owned, {effects} effect roles on "
          f"them, {total_silent} of those moved no figure")
    print(f"  the list 4.9b (`not_counted`: `Build.situational` with "
          f"live == False) holds {left_out} of them -- a **list** count and "
          f"not a filling count (AK-181)")
    print(f"  {relics_with_a_silent_effect} relics carry at least one silent "
          f"effect, {relics_with_no_figure_at_all} carry no effect with a "
          f"figure at all")
    for silence, label in FILLINGS.items():
        count = silent[silence]
        share = 100.0 * count / total_silent if total_silent else 0.0
        print(f"  {label:<44s} {count:4d} of {total_silent}  ({share:4.1f} %)")
    print(f"\n  {curse_lines} curse lines over the same relics")
    for label, count in sorted(curses.items()):
        print(f"  {label:<44s} {count:4d} of {curse_lines}")
    print("\n  the heading of each group, by its first word:")
    for word, count in headings.most_common():
        print(f"    {word:<10s} {count:4d}")
    print(f"\n  the tallest card one owned relic can make: {worst[1]} lines "
          f"in the Why dialog and {worst[2]} in the block, both counting its "
          f"two headings, on {worst[0]!r}")
    print("\n  not seen by this part: (a2) across two slots -- one relic per "
          "run here -- and the ownership answer of any Nightfarer but "
          f"{ctx.hero['name']}.")


def measure_the_suggestions(data: dict, owned, ctx: types.GoalContext) -> None:
    """AK-161: how many lines a whole suggestion is, in each of its two places.

    The figures from T-067 (10 to 43 lines, median 21) were counted before
    the silent lines existed and before the block and the dialog came apart,
    so they do not carry.
    """
    wanted = VESSEL_OF.format(hero=ctx.hero["name"])
    vessel = next(v for v in data["vessels"] if v["name"] == wanted)
    colours = list(vessel["slots"]) + list(vessel["deep_slots"])
    slots = tuple(types.Slot(index=i, colour=colour, deep=i >= 3)
                  for i, colour in enumerate(colours))
    problem = types.SlotProblem(slots=slots)
    goal = goals.GOALS[GOAL]
    pools = candidates.pools(owned, problem, ctx, goals.GOALS, GOAL)
    found = search.beam(problem, pools, types.DEFAULT_BUDGET,
                        search.goal_scorer(problem, ctx, goal))
    base = evaluate(problem, (), ctx)

    block, dialog, per_group, longest = [], [], [], ("", 0)
    silent = collections.Counter()
    for suggestion in found:
        chosen = explain.chosen_for(suggestion, pools)
        groups = explain.reasons(problem, chosen, base,
                                 evaluate(problem, chosen, ctx), ctx, goal)
        drawn = [line for group in groups for line in group.lines]
        headings = 2 * len(groups)     # relic name and counting line
        block.append(len([line for line in drawn
                          if types.drawn_in_the_block(line)]) + headings)
        dialog.append(len(drawn) + headings)
        for group in groups:
            per_group.append(len(group.lines) + 2)
            for line in group.lines:
                if len(line.text) > longest[1]:
                    longest = (line.text, len(line.text))
                if not line.is_curse and line.silence:
                    silent[line.silence] += 1

    def spread(name: str, counts: list[int]) -> None:
        print(f"  {name:<28s} {min(counts):3d} to {max(counts):3d} lines, "
              f"median {statistics.median(counts):5.1f}")

    print(f"\n{len(found)} suggestions over {wanted}, {len(slots)} free "
          f"slots, direction {goal.label!r}")
    spread("whole suggestion, block", block)
    spread("whole suggestion, Why dialog", dialog)
    spread("one slot group, Why dialog", per_group)
    print(f"  longest line: {longest[1]} characters\n    {longest[0]!r}")
    total = sum(silent.values())
    print(f"  {total} silent effect lines over these suggestions, six slots "
          f"at a time -- the only place (a2) can arise at all:")
    for silence, label in FILLINGS.items():
        print(f"    {label:<44s} {silent[silence]:4d} of {total}")


def main(argv: Sequence[str]) -> int:
    name = argv[1] if len(argv) > 1 else DEFAULT_HERO
    data = json.loads(paths.snapshot_path().read_text(encoding="utf-8"))
    model.configure(data)
    owned = inventory_module.load(data)
    if owned is None:
        print("no save on this machine, so there is nothing to measure")
        return 1
    hero = next((one for one in data["heroes"] if one["name"] == name), None)
    if hero is None:
        known = ", ".join(one["name"] for one in data["heroes"])
        print(f"no Nightfarer called {name!r} in this dataset; it knows "
              f"{known}")
        return 2
    version = (data.get("meta") or {}).get("data_version")
    print(f"data_version {version}, {len(data['effects'])} effects, "
          f"{name} at level {LEVEL}, the starting armament held and rated, "
          f"no condition declared met")

    ctx = a_context(data, hero)
    count_the_fillings(data, owned, ctx)
    measure_the_suggestions(data, owned, ctx)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
