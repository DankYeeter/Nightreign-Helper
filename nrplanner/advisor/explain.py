"""Why this build, in the player's own language (`GOAL.md` A5, A7).

A suggestion the player cannot check is a suggestion they have to believe, and
this project does not ask that of anyone. So every line here names an effect
that is really in the build, with what it really moved, in the wording and the
number format of the stat sheet beside it.

**The reference point is the base state, not the empty build** (S8+,
AD-014.6). AD-010 first said "the difference to the empty build"; with held
slots that is wrong, because the reasoning would then credit the suggestion
with the effects of the relic the player is holding. What is read here is
`built.sources` **minus** `base.sources`, entry by entry, which is exactly
what the chosen copies added and nothing else.

**Nothing is calculated a second time.** Every figure comes out of
`Build.sources`, which `model.compute` filled while it was working the total
out (AD-015). A curse is an ordinary effect in that reckoning and has no
second one anywhere under `advisor/`: `curses` below reports what the
calculation *applied*, so a curse it did not apply -- a conditional one, or a
second copy of a curse the game refuses to stack -- cannot be shown as though
it had.

**A curse is named, never charged twice** (OF-13, AD-023). It is already in
the ranking figure, so no line here says a relic placed lower *because of* it.
What the lines do say is which negatives were counted against it (`GOAL.md`
F3), because a suggestion whose price only shows after applying it is a trap.

**The two `unknowns` lines this step adds are run findings** in the sense of
AD-025: one names how many slots were held, the other names a relic and a
field. Both need a run to be written, so both travel in the result rather than
in the registry -- where the procedural sentences of the directions live and
are drawn once for the screen (AK-50).

**What this module cannot say, said here rather than left to be discovered:**

* `model.NON_ACCUMULATING` fields are recorded once. A second, stronger source
  of `additionalCharacterSkillUse` moves the total and adds no entry to
  `sources`, so no line here names it. That is the model's account of what
  counted, and a second reading of the effect records would be the second
  opinion AD-015 forbids;
* an effect the dataset no longer carries contributes nothing and is named
  nowhere, exactly as `evaluate` skips it (P4, QA-004/QA-032);
* two effects that share a name and were both counted are told apart by the
  order they sit in on the relics, because `sources` records names and not
  ids. That is right for the case it was built for -- one effect on three
  relics, three entries, one per relic -- and it is a guess where a dataset
  gives one name to two different effects.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Sequence
from dataclasses import dataclass

from .. import model
from . import types
from .evaluate import evaluate


# --- what one chosen copy actually moved -----------------------------------

@dataclass(frozen=True)
class _Contribution:
    """One effect of one chosen copy, and the one figure it moved.

    Private on purpose. `types.py` is the vocabulary the advisor passes
    around; this is the working of one step, and every public function below
    hands back English lines rather than this.
    """

    candidate: types.Candidate
    effect_id: int
    effect_name: str
    is_curse: bool
    field_key: str
    own: float


def _effect_name(ctx: types.GoalContext, effect_id: int) -> str | None:
    """This effect's name as `Build.sources` writes it, or `None`.

    Whitespace-folded the same way `model.compute` folds it, because the name
    in `sources` is what has to be matched and a name that differs by a line
    break matches nothing. `None` for an id this dataset does not carry:
    `evaluate` skips those, so they moved nothing and there is nothing to say
    about them.
    """
    effect = ctx.data["effects"].get(str(effect_id))
    if effect is None:
        return None
    return " ".join(str(effect.get("name", "")).split())


def _added(base: model.Build, built: model.Build) -> list[tuple[str, str,
                                                                float]]:
    """What the chosen copies added to `sources`, entry by entry.

    A multiset difference rather than a subtraction of totals: two relics
    carrying one stacking effect are two entries under one name, and the base
    state's own copy of that effect has to cancel exactly one of them. The
    order is `built`'s, which is the order `model.compute` counted them in.
    """
    out: list[tuple[str, str, float]] = []
    for key, entries in built.sources.items():
        before = list(base.sources.get(key, ()))
        for name, own in entries:
            if (name, own) in before:
                before.remove((name, own))
                continue
            out.append((key, name, own))
    return out


def _moved_nothing(key: str, own: float, built: model.Build) -> bool:
    """Is this entry a figure that did not move?

    An effect may carry a field at its own neutral value -- 1.0 for a
    multiplier, 0 for anything that adds -- and `model.compute` records it
    like any other. `+0.0%` is not a reason, and calling it a cost because it
    is not a gain would be worse than saying nothing.
    """
    return own == (1.0 if _scales(key, built) else 0.0)


def _attributed(chosen: Sequence[types.Candidate], base: model.Build,
                built: model.Build,
                ctx: types.GoalContext) -> tuple[_Contribution, ...]:
    """Which chosen copy each added entry belongs to, in slot order.

    Every entry is claimed by exactly one copy, so a stacking effect that
    three relics carry gives three contributions and one apiece -- and an
    effect the game refuses to stack gives one, to the first copy that
    carries it, which is the honest reading: the second copy really did
    contribute nothing (`model.compute` reports it as a duplicate instead).

    The fields one effect moved are merged where the game split one idea over
    several of them, through `model.collapse_by_label` -- the model's own
    rule, and the reason one relic does not produce five lines saying that FP
    costs 8 % less.
    """
    added = _added(base, built)
    claimed = [False] * len(added)
    out: list[_Contribution] = []
    for candidate in sorted(chosen, key=lambda copy: copy.slot_index):
        curses = set(candidate.curse_ids)
        for effect_id in tuple(candidate.effect_ids) + candidate.curse_ids:
            name = _effect_name(ctx, effect_id)
            if name is None:
                continue
            moved: dict[str, float] = {}
            for position, (key, entry, own) in enumerate(added):
                if claimed[position] or entry != name or key in moved:
                    continue
                claimed[position] = True
                moved[key] = own
            for key, own in model.collapse_by_label(moved).items():
                if _moved_nothing(key, own, built):
                    continue
                out.append(_Contribution(
                    candidate=candidate, effect_id=effect_id,
                    effect_name=name, is_curse=effect_id in curses,
                    field_key=key, own=own))
    return tuple(out)


# --- how one figure is written down ----------------------------------------

def _real_field(key: str) -> str:
    """The field behind a key `sources` filed under a scope.

    A buff the game restricts to melee or ranged armaments is recorded under
    `wepclass:<class>:<field>` (`model.compute`), and every question about the
    field itself -- its label, whether less of it is better -- is a question
    about the part after the class.
    """
    if key.startswith(model.WEAPON_CLASS_PREFIX):
        return key.split(":", 2)[2]
    return key


def _scales(key: str, built: model.Build) -> bool:
    """Does this figure multiply what it touches, or add to it?

    Read off the build the number came from, the way the breakdown popup in
    `app.py` reads it: a key standing in `Build.rates` is a multiplier, and an
    attribute or a flat bonus is not. A weapon-class key never reaches
    `rates` -- its value lives in `class_rates` under the class -- and it is
    only ever written by the multiplier branch, so it is answered on its own.
    """
    if key.startswith(model.WEAPON_CLASS_PREFIX):
        return True
    return key in built.rates


def _field_label(key: str) -> str:
    """The name the stat sheet gives this figure.

    `model.label_for` for everything the sheet shows plainly, and the class
    spelled out for a buff that only lifts one kind of armament -- the same
    addition `app.py` makes in the attack-rating breakdown, because "Physical
    Attack +20 %" without it is a claim about every armament on the grid.
    """
    if key.startswith(model.WEAPON_CLASS_PREFIX):
        _prefix, weapon_class, field_name = key.split(":", 2)
        return f"{model.label_for(field_name)}, {weapon_class} armaments only"
    return model.label_for(key)


def _amount(key: str, own: float, built: model.Build) -> str:
    """One contribution in the stat sheet's own format (`UI_SPEC` 3.2).

    `+15.0%` for a multiplier and `+1` for something that adds, the two forms
    the breakdown popup uses, so a figure read here and the same figure read
    there are written the same way.
    """
    if _scales(key, built):
        return f"{(own - 1.0) * 100:+.1f}%"
    return f"{own:+g}"


def _is_a_cost(key: str, own: float, built: model.Build) -> bool:
    """Does this contribution make its field worse?

    The direction comes from `model.is_better_lower`, which knows that a
    damage-cut rate and an FP cost are better small -- guessing it from the
    sign would call an 8 % cheaper skill a penalty. `GOAL.md` F3 is what needs
    the answer: the reasoning has to say which negatives were counted against
    a relic, and the sign alone does not say it.
    """
    above = own - 1.0 if _scales(key, built) else own
    return (above > 0) == model.is_better_lower(_real_field(key))


def _line(contribution: _Contribution, built: model.Build) -> str:
    """One effect of one slot, as the player reads it.

    The slot is numbered the way the window numbers it, from one --
    `SlotChoice.slot_index` counts from zero because it addresses a slot, and
    this line is read rather than followed.
    """
    key, own = contribution.field_key, contribution.own
    cost = ", counted against it" if _is_a_cost(key, own, built) else ""
    return (f"Slot {contribution.candidate.slot_index + 1}, "
            f"{contribution.candidate.name} — {contribution.effect_name}: "
            f"{_named(contribution, built)}{cost}")


def _named(contribution: _Contribution, built: model.Build) -> str:
    """The figure and what it is called, without saying the name twice.

    A buff the game restricts to one move is filed under the effect's own
    name (`model.label_for`, `SCOPED_PREFIX`), because the name already
    states the scope. Written out beside the effect it would read
    `Improved Skill Attack Power: Improved Skill Attack Power +15.0%`, which
    is a longer way of saying nothing new.
    """
    key, own = contribution.field_key, contribution.own
    label = _field_label(key)
    amount = _amount(key, own, built)
    return amount if label == contribution.effect_name else f"{label} {amount}"


# --- the lines themselves --------------------------------------------------

def chosen_for(suggestion: types.Suggestion,
               pools: Sequence[types.SlotPool]) -> tuple[types.Candidate, ...]:
    """The copies a suggestion names, back as the candidates they came from.

    A `SlotChoice` carries what the window needs to put a relic in a slot --
    a handle and a name -- and not what an explanation needs, which is the
    roll. The pools the search consumed still hold it, so it is looked up
    there rather than carried twice: a second copy of the roll beside the
    suggestion is a second thing to keep in step, and this project has paid
    for one of those already (QA-107).

    Loud when a choice is in no pool: that means the pools and the suggestion
    are from two different runs, and explaining one with the other would name
    effects that are not in the build.
    """
    by_slot = {pool.slot_index: pool for pool in pools}
    found = []
    for choice in suggestion.choices:
        pool = by_slot.get(choice.slot_index)
        if pool is None:
            raise KeyError(
                f"this suggestion fills slot {choice.slot_index}, for which "
                f"there is no pool: the suggestion and the pools are from "
                f"two different runs")
        offer = next((entry for entry in pool.candidates
                      if entry.handle == choice.handle), None)
        if offer is None:
            raise KeyError(
                f"slot {choice.slot_index} was filled with handle "
                f"{choice.handle}, which its pool does not offer")
        found.append(offer)
    return tuple(found)


def reasons(chosen: Sequence[types.Candidate], base: model.Build,
            built: model.Build,
            ctx: types.GoalContext) -> tuple[str, ...]:
    """Which effects decided this suggestion, one line each (A5, F3).

    One line per effect and per figure it moved, in slot order and then in the
    order the effects sit on the relic -- the relic's own order, which is the
    order the picker shows them in, and not an order of size: a percentage and
    a flat bonus cannot be put on one scale without inventing the exchange
    rate A7 forbids.

    The negatives are in here beside the gains, marked as counted against the
    relic. That is `GOAL.md` F3 -- *"falls meine negativen auf Relikten meine
    Benefits vernichten, muss ich das wissen"* -- and it is why they are not
    quietly dropped for reading better.
    """
    return tuple(_line(contribution, built)
                 for contribution in _attributed(chosen, base, built, ctx))


def curses(chosen: Sequence[types.Candidate], base: model.Build,
           built: model.Build,
           ctx: types.GoalContext) -> tuple[str, ...]:
    """The curses of the suggested relics, with the field and the amount.

    AD-010 asks for them by name; AD-015 asks for them **out of
    `Build.sources`**, which is the difference between naming what the
    calculation applied and naming what the relic definition says. A
    conditional curse the run did not count is not in here -- it is in
    `not_counted`, which is where an uncounted thing belongs.

    No line says the relic placed lower because of its curse (OF-13). The
    figure is shown in its own unit, and what it is worth against the gains
    is the player's to weigh -- the game files carry no exchange rate, and
    inventing one is what AD-023 refuses.
    """
    return tuple(
        f"Slot {contribution.candidate.slot_index + 1}, "
        f"{contribution.candidate.name} — {contribution.effect_name}: "
        f"{_named(contribution, built)}"
        for contribution in _attributed(chosen, base, built, ctx)
        if contribution.is_curse)


def not_counted(built: model.Build) -> tuple[str, ...]:
    """The conditional effects of this build that went into no total (AD-010).

    Read off `Build.situational`, which is what `model.compute` actually
    parked, so an effect whose condition the player has declared live is not
    in here -- it was counted, and saying otherwise would be the second
    opinion this module does not give.

    **Scope, because a list without one is read as a list of everything:**
    these are the conditions the player can be in. An effect gated on a
    Nightfarer you are not or an armament you are not carrying went into no
    total either and is not in here; `Build.qualitative` holds those, and
    they are a different sentence (QA-104).

    Duplicates are kept. Two relics carrying one uncounted condition are two
    effects that did not count, and `len(not_counted)` is the count AD-010
    asks for.
    """
    return tuple(entry.name for entry in built.situational if not entry.live)


def data_note(ctx: types.GoalContext) -> str:
    """Which dataset this run was ranked on (AD-010, F7).

    Two things, because they are two different reasons to distrust a figure:
    which version of the game's data it came from, and whether that data was
    read from the installation now or has been sitting in a snapshot since
    the last time. `datasource` marks a fresh extraction with `regenerated`.
    """
    meta = ctx.data.get("meta") or {}
    where = ("read from the installed game" if meta.get("regenerated")
             else "from the stored snapshot")
    version = str(meta.get("data_version") or "")
    if not version:
        return (f"Ranked on game data {where}, which records no version, so "
                f"there is no way to say which patch it is from.")
    return f"Ranked on game data version {version}, {where}."


def _held_slots_line(problem: types.SlotProblem) -> str:
    """What the search was not allowed to touch, or "" when it was all free.

    A run finding in the sense of AD-025 -- it carries a count, and whether it
    stands at all is settled by the run. The two fillings are two different
    pieces of news: some slots held is a smaller search, every slot held is
    **no** search, and the answer is then the build as it stands (AD-014.2).
    """
    held = len(problem.held)
    slots = len(problem.slots)
    if not held:
        return ""
    if held == slots:
        return (f"All {slots} slots are held, so nothing was searched: this "
                f"is the build as it stands, scored.")
    one = held == 1
    return (f"{held} of {slots} slots {'is' if one else 'are'} held, so only "
            f"the other {slots - held} were filled.")


def _without_the_curse(chosen: Sequence[types.Candidate],
                       carrier: types.Candidate,
                       curse_id: int) -> tuple[types.Candidate, ...]:
    """The same assignment with one curse taken off one copy."""
    return tuple(
        dataclasses.replace(
            copy, curse_ids=tuple(other for other in copy.curse_ids
                                  if other != curse_id))
        if copy.slot_index == carrier.slot_index else copy
        for copy in chosen)


def _curses_the_goal_cannot_feel(problem: types.SlotProblem,
                                 chosen: Sequence[types.Candidate],
                                 base: model.Build, built: model.Build,
                                 ctx: types.GoalContext,
                                 goal: types.Goal) -> list[str]:
    """AD-015's mandatory line: a cost the ranking figure does not carry.

    Everything is weighed, one number is **ranked**. A curse that moves a
    field the chosen direction does not measure -- `-HP` under "Maximise
    damage" -- is correctly counted in the build and moves the ranking figure
    not at all, so the suggestion block is the only place it becomes visible.

    Whether the direction feels it is asked of the direction, by scoring the
    same assignment once more with that one curse taken off. That is the one
    authority again and not a second one: no list here says what a goal
    measures, so a third direction brings its own answer without a line
    changing (AD-004).

    **Scope:** the question is asked per curse and answered on the figure. A
    curse that moves two fields, one of which the direction ranks, moves the
    figure and gets no line -- it is visible in the ranking, which is what the
    line exists to supply when it is not. Naming the other half would need a
    per-field question the registry cannot answer.
    """
    ranked = goal.score(built, ctx).value
    by_curse: dict[tuple[int, int], list[_Contribution]] = {}
    for contribution in _attributed(chosen, base, built, ctx):
        if contribution.is_curse:
            by_curse.setdefault(
                (contribution.candidate.slot_index, contribution.effect_id),
                []).append(contribution)

    lines: list[str] = []
    for moved in by_curse.values():
        carrier = moved[0].candidate
        without = _without_the_curse(chosen, carrier, moved[0].effect_id)
        if goal.score(evaluate(problem, without, ctx), ctx).value != ranked:
            continue
        lines.extend(
            f"A curse on {carrier.name} changes "
            f"{_field_label(contribution.field_key)}, which this goal does "
            f"not rank."
            for contribution in moved)
    return lines


def unknowns(problem: types.SlotProblem, chosen: Sequence[types.Candidate],
             base: model.Build, built: model.Build, ctx: types.GoalContext,
             goal: types.Goal) -> tuple[str, ...]:
    """What this run left out, in the player's language (AD-010, A7).

    Both lines are run findings (AD-025.2): the first carries a count of
    slots, the second names a relic and a field, and neither could be written
    before the run. The procedural sentences of the direction are not here --
    they stand in `Goal.scope`, are read from there once for the screen, and
    repeating them per result is the noise AK-50 is written against.

    Empty is an answer: nothing was held and no curse fell outside the figure.
    """
    lines = []
    held = _held_slots_line(problem)
    if held:
        lines.append(held)
    lines.extend(_curses_the_goal_cannot_feel(problem, chosen, base, built,
                                              ctx, goal))
    return tuple(lines)
