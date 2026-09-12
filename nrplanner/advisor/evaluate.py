"""The one place under `advisor/` that reaches `model.compute` (AD-014.1).

Held slots, chosen candidates, the curses of both and the effects the
armaments rolled are assembled here and nowhere else. The pre-sort, the beam
step and the base state all come through this door, so none of them can
forget the held slots -- and forgetting them at *one* evaluation is the
failure Nachtrag I names first: the advisor would then recommend candidates
whose contribution the held relic already caps, the score would not rise, and
the suggestion would still look plausible.

That is not a matter of care. "The held contribution goes into every
evaluation" is a rule one can forget at three places for as long as there are
three places, so there is one, and
`tests/test_one_build.py::test_the_user_interface_holds_exactly_one_call_to_compute`
holds it: the expectation there is `{"nrplanner/app.py": 1,
"nrplanner/advisor/evaluate.py": 1}`, and a second reference anywhere under
`nrplanner/` fails it. The mutation `advisor-computes-in-a-second-place` in
`scripts/differential/mutate.py` is the counter-build.

**What the guard behind this cannot see, said here rather than assumed:** it
reads the syntax tree, so a call reached at run time -- `importlib`, a lookup
in `sys.modules`, a name bound from a string -- is invisible to it (QA-023,
held over). It catches the spellings a second calculation would plausibly be
written in.

**Curses are ordinary effects** (AD-015, `GOAL.md` F3). They go into the same
list as everything else, exactly as `Planner._rebuild` does it, and there is
no curse malus, no curse weight and no curse branch anywhere under
`advisor/`. Whether a curse is *shown* is `explain.py`'s question, and it
reads `Build.sources`, which this call fills.
"""

from __future__ import annotations

from .. import model
from . import types


def effect_ids_of(problem: types.SlotProblem,
                  assignment: tuple[types.Candidate, ...],
                  ctx: types.GoalContext) -> tuple[int, ...]:
    """Every effect id that counts towards this build, in a settled order.

    Held relics first, then the chosen candidates in slot order, then the
    armaments -- the same three sources `Planner._rebuild` gathers, in the
    same order, so that two runs over one state produce the same list.

    Order matters to `model.compute` in one respect only: duplicates of an
    `isStrongestEffect` are reported in the order they arrive. It does not
    move a total.
    """
    ids: list[int] = []
    for relic in types.held_relics(problem):
        ids.extend(relic.effect_ids)
        ids.extend(relic.curse_ids)
    for candidate in sorted(assignment, key=lambda chosen: chosen.slot_index):
        ids.extend(candidate.effect_ids)
        ids.extend(candidate.curse_ids)
    ids.extend(ctx.armament_effect_ids)
    return tuple(ids)


def _effects(ctx: types.GoalContext,
             effect_ids: tuple[int, ...]) -> list[dict]:
    """The effect records behind those ids.

    An id the dataset does not carry is skipped, which is what
    `Planner.selected_effects` and `Planner.weapon_effects` both do. Diverging
    here would make the advisor's figure disagree with the stat sheet for a
    save that mentions an effect this dataset version has dropped, and the
    figures agreeing is the whole point of there being one calculation.
    Skipping quietly is a known weakness of that path (P4, QA-004/QA-032); it
    is inherited on purpose rather than solved in a second place.
    """
    known = ctx.data["effects"]
    found = []
    for effect_id in effect_ids:
        effect = known.get(str(effect_id))
        if effect is not None:
            found.append(effect)
    return found


def evaluate(problem: types.SlotProblem,
             assignment: tuple[types.Candidate, ...],
             ctx: types.GoalContext) -> model.Build:
    """The build that results from holding `problem` and choosing `assignment`.

    `assignment` may only name free slots. A candidate for a held slot is
    refused rather than applied: holding is a boundary condition and not a
    starting value (AD-014), and silently overwriting a held slot is the one
    outcome the player asked the feature to prevent. Two candidates for one
    slot are refused for the same reason -- there is no rule that says which
    of them wins.

    The empty assignment is the base state: `evaluate(problem, (), ctx)` is
    what a marginal contribution is measured against (AD-014.6, AD-018.1).
    """
    free = {slot.index for slot in types.free_slots(problem)}
    seen: set[int] = set()
    for candidate in assignment:
        if candidate.slot_index not in free:
            raise ValueError(
                f"slot {candidate.slot_index} is held, so nothing may be "
                f"assigned to it: a held slot is a boundary condition of the "
                f"search, not a starting value (AD-014)")
        if candidate.slot_index in seen:
            raise ValueError(
                f"two candidates were assigned to slot "
                f"{candidate.slot_index}")
        seen.add(candidate.slot_index)

    reference = ctx.reference
    return model.compute(
        ctx.hero,
        ctx.level,
        _effects(ctx, effect_ids_of(problem, assignment, ctx)),
        ctx.data.get("curves", {}),
        weapon=reference.weapon if reference is not None else None,
        weapons_held=list(ctx.weapons_held),
        declared=dict(ctx.declared),
    )
