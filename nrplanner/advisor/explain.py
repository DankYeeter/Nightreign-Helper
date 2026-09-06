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

**The `unknowns` line this step adds is a run finding** in the sense of
AD-025: it names how many slots were held. It needs a run to be written, so
it travels in the result rather than in the registry -- where the procedural
sentences of the directions live and are drawn once for the screen (AK-50).

**A line arrives knowing where it belongs, and the window never reads it.**
Every drawn line comes back inside the group of its slot, saying for itself
whether it is a curse and why it carries no figure (`types.ReasonLine`,
`types.SlotReasons`). What used to stand in the text -- `Slot 4, <relic> —`
in front of every line -- is in the heading of the group now, because a
window that has to split a sentence to place it splits it on the wrong
character sooner or later: one field of this dataset is called `Regain — HP
won back by attacking after a hit` (`UI_SPEC` T-078 §6, AK-147).

**What this module cannot say, said here rather than left to be discovered:**

* `model.NON_ACCUMULATING` fields are recorded once. A second, stronger source
  of `additionalCharacterSkillUse` moves the total and adds no entry to
  `sources`, so no line here names it. That is the model's account of what
  counted, and a second reading of the effect records would be the second
  opinion AD-015 forbids;
* an effect the dataset no longer carries contributes nothing and is named
  nowhere, exactly as `evaluate` skips it (P4, QA-004/QA-032);
* two effects that share a name are told apart by their **id**, which
  `Build.sources` carries beside the figure. Attributing by name was the
  guess this module used to make, and on the real save it put 130 lines under
  a relic that cannot produce them and left 23 of 296 best suggestions with a
  filled slot the reasoning says nothing about (QA-180): `7000090` and
  `6610400` are both `Increased Maximum HP`, so the first relic claimed both
  figures and the second looked as though it had contributed nothing.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Sequence
from dataclasses import dataclass

from .. import effecttext, model
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

    Whitespace-folded the same way `model.compute` folds it, so that the name
    on a line here and the name in the breakdown popup are the same string --
    several effect names in this dataset end in a line break. `None` for an id
    this dataset does not carry: `evaluate` skips those, so they moved nothing
    and there is nothing to say about them.
    """
    effect = ctx.data["effects"].get(str(effect_id))
    if effect is None:
        return None
    return " ".join(str(effect.get("name", "")).split())


def _added(base: model.Build,
           built: model.Build) -> list[tuple[str, model.SourceEntry]]:
    """What the chosen copies added to `sources`, entry by entry.

    A multiset difference rather than a subtraction of totals: two relics
    carrying one stacking effect are two entries under one name, and the base
    state's own copy of that effect has to cancel exactly one of them. The
    order is `built`'s, which is the order `model.compute` counted them in.

    An entry cancels only against an entry of the **same effect**, id and all.
    Two effects this dataset gives one name to are two entries and not two
    copies of one (QA-180), and the base state's `Increased Maximum HP` must
    not swallow a chosen copy's differently-numbered one.
    """
    out: list[tuple[str, model.SourceEntry]] = []
    for key, entries in built.sources.items():
        before = list(base.sources.get(key, ()))
        for entry in entries:
            if entry in before:
                before.remove(entry)
                continue
            out.append((key, entry))
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

    **Matched on the effect id, never on the name** (QA-180). The name is
    what the line says; the id is what says whose figure it is. Two effects
    this dataset calls `Increased Maximum HP` moved two different fields, and
    matching by name gave both figures to the copy in the lower slot and left
    the other slot without a line -- 130 such lines on the real save.

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
            for position, (key, entry) in enumerate(added):
                if (claimed[position] or entry.effect_id != effect_id
                        or key in moved):
                    continue
                claimed[position] = True
                moved[key] = entry.own
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
    """One effect and one figure it moved, as the player reads it.

    **Neither the slot number nor the relic name is in here** (`UI_SPEC`
    T-078 §2 and §4). Both stand in the heading of the group this line hangs
    under, and repeating them cost up to seven consecutive lines the same
    thirty-five characters -- the longest line on the real save measured 142
    characters, of which the repetition was a quarter.
    """
    key, own = contribution.field_key, contribution.own
    cost = ", counted against it" if _is_a_cost(key, own, built) else ""
    return (f"{contribution.effect_name}: "
            f"{_named(contribution, built)}{cost}")


def _line_the_figure_does_not_count(contribution: _Contribution,
                                    built: model.Build) -> str:
    """A curse that moved a number this direction does not rank (AD-015).

    One sentence where there were two. The figure stood in `reasons` and a
    second line in `unknowns` said `A curse on <relic> changes <field>, which
    this goal does not rank.` -- the same curse said twice, in two places, the
    second of them naming a relic that the group heading already names
    (`UI_SPEC` T-078 §3 filling ii).

    No `, counted against it`: it was not counted against the ranking figure,
    which is the whole of what this filling says.
    """
    return (f"{contribution.effect_name}: {_named(contribution, built)} — "
            f"this figure does not count it.")


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


# --- the effects that moved nothing, and why -------------------------------

#: The gates that make an effect's worth a question about the armaments on
#: the grid rather than about the build. They are the keys of
#: `model.GATE_FIELDS` whose wording says so -- "only with a matching weapon
#: type", "needs several of that weapon equipped", "changes the armament's
#: skill" -- and they are named here rather than sniffed out of that wording,
#: because a family picked by searching another module's English would move
#: the day someone rewrote a sentence. `tests/test_advisor_explain.py` holds
#: the two lists against each other.
_ARMAMENT_GATES = ("triggerOnWepType", "wepTypeTrigger", "wepTypeTriggerCount",
                   "startSwordArtsId")


def _silent_effect(candidate: types.Candidate, effect_id: int,
                   ctx: types.GoalContext, built: model.Build,
                   counted_elsewhere: bool) -> types.ReasonLine:
    """An effect of a chosen copy that produced no line, said in one sentence.

    Six fillings, and **the first that fits wins** in the order `UI_SPEC`
    T-080 §4 sets: the strongest piece of news first. They are not one
    sentence with six wordings -- what a player can do about a silent effect
    differs completely between them. An effect that works for another
    Nightfarer is dead weight in that slot forever; one waiting on a
    condition counts the moment the condition holds, and the advisor measured
    150 of the first and 170 of the second among 426 silent effects on one
    save.

    **Why the reason is asked of the same reckoning that produced the
    build** (AD-015): `built.situational` is what `model.compute` actually
    parked, matched by **id** rather than by name, and the ownership gate is
    `effecttext.works_for`, which is the function `compute_qualitative`
    itself asks. Nothing here re-decides what an effect does; it reads back
    why the calculation had nothing to write down.
    """
    def said(text: str, silence: str) -> types.ReasonLine:
        return types.ReasonLine(slot_index=candidate.slot_index, text=text,
                                silence=silence)

    name = _effect_name(ctx, effect_id)
    if not name:
        return said("One of its effects is not in your game data, so it has "
                    "no name here and counted for nothing.",
                    types.SILENT_NOT_IN_THE_DATA)
    effect = ctx.data["effects"][str(effect_id)]
    hero = str(ctx.hero.get("name", ""))
    if not effecttext.works_for(effect, hero):
        owner = effecttext.owner(effect)
        return said(
            f"{name}: works only for {owner}, and you are {hero}." if owner
            else f"{name}: works only for another Nightfarer, not for "
                 f"{hero}.",
            types.SILENT_ANOTHER_NIGHTFARER)
    if counted_elsewhere:
        return said(f"{name}: another copy of it is already counted, so this "
                    f"one adds nothing.", types.SILENT_ALREADY_COUNTED)
    if any(entry.effect_id == effect_id and not entry.live
           for entry in built.situational):
        return said(f"{name}: only applies under a condition, so no number "
                    f"here.", types.SILENT_UNDER_A_CONDITION)
    if any(gate in (effect.get("modifiers") or {}) for gate in _ARMAMENT_GATES):
        return said(f"{name}: it depends on the armaments you carry, so no "
                    f"number here.", types.SILENT_ARMAMENT_BOUND)
    return said(f"{name}: no number here shows what this adds.",
                types.SILENT_NO_NUMBER_HERE)


def _count_line(effects: int, with_a_figure: int, moved_something: bool
                ) -> str:
    """The heading sentence of one slot group, and its denominator (L-013).

    Without it an effect that moved nothing vanishes and the player goes
    looking for it; with it the group states how many of the copy's roles are
    accounted for below (`UI_SPEC` T-078 §6, two fillings added in T-080 §5).

    **Precedence, decided here because the two sources leave it open:** a
    copy that moved nothing at all gets the sentence that says so, even when
    it carries exactly one effect. T-080 §5 names that filling as the
    replacement for `None of its {total} effects ...`, and the question it
    answers -- why is this being suggested to me at all -- is the same
    question at one effect as at three. `This relic carries no effects of its
    own.` still wins over it: with no roles there is nothing for the other
    sentence to be about.
    """
    if not effects:
        return "This relic carries no effects of its own."
    if not moved_something:
        return ("Nothing on this relic moved a number in this build — it "
                "fills the slot without changing the figure.")
    if effects == 1:
        return ("Its one effect moved a number in this build."
                if with_a_figure else
                "Its one effect moved no number in this build.")
    if not with_a_figure:
        return f"None of its {effects} effects moved a number in this build."
    if with_a_figure == effects:
        return f"All {effects} of its effects moved a number in this build."
    return (f"{with_a_figure} of its {effects} effects moved a number in "
            f"this build.")


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


def reasons(problem: types.SlotProblem, chosen: Sequence[types.Candidate],
            base: model.Build, built: model.Build, ctx: types.GoalContext,
            goal: types.Goal) -> tuple[types.SlotReasons, ...]:
    """Which effects decided this suggestion, one group per slot (A5, F3).

    One line per effect and per figure it moved, then one line for each
    effect that moved none, then the curses -- in slot order, and inside a
    slot in the order the effects sit on the relic. That is the order the
    picker shows and the order the player reads down the card; it is not an
    order of size, because a percentage and a flat bonus cannot be put on one
    scale without inventing the exchange rate A7 forbids. **The curses stay
    last**: the price belongs at the end, not in the middle.

    The negatives are in here beside the gains, marked as counted against the
    relic. That is `GOAL.md` F3 -- *"falls meine negativen auf Relikten meine
    Benefits vernichten, muss ich das wissen"* -- and it is why they are not
    quietly dropped for reading better.

    `problem` and `goal` are here for one filling only: whether the ranking
    figure feels a curse is a question only the direction can answer, and it
    is answered by scoring the same assignment again without that one curse
    (AD-015). With no curse to ask about, nothing is scored.
    """
    contributions = _attributed(chosen, base, built, ctx)
    unfelt = _curses_the_goal_cannot_feel(problem, chosen, ctx, goal,
                                          built, contributions)
    already = {entry.effect_id for entries in base.sources.values()
               for entry in entries}
    groups = []
    for candidate in sorted(chosen, key=lambda copy: copy.slot_index):
        mine = [one for one in contributions
                if one.candidate.slot_index == candidate.slot_index]
        with_a_figure = {one.effect_id for one in mine}
        elsewhere = ({one.effect_id for one in contributions} | already
                     ) - with_a_figure
        lines: list[types.ReasonLine] = []
        for effect_id in candidate.effect_ids:
            if effect_id in with_a_figure:
                lines.extend(
                    types.ReasonLine(slot_index=candidate.slot_index,
                                     text=_line(one, built))
                    for one in mine if one.effect_id == effect_id)
            else:
                lines.append(_silent_effect(candidate, effect_id, ctx, built,
                                            effect_id in elsewhere))
        for curse_id in candidate.curse_ids:
            lines.extend(_curse_lines(candidate, curse_id, ctx, built, mine,
                                      unfelt))
        counted = sum(1 for effect_id in candidate.effect_ids
                      if effect_id in with_a_figure)
        groups.append(types.SlotReasons(
            slot_index=candidate.slot_index,
            relic_name=candidate.name,
            effects_total=len(candidate.effect_ids),
            effects_with_a_figure=counted,
            count_line=_count_line(len(candidate.effect_ids), counted,
                                   bool(mine)),
            lines=tuple(lines)))
    return tuple(groups)


def _curse_lines(candidate: types.Candidate, curse_id: int,
                 ctx: types.GoalContext, built: model.Build,
                 mine: Sequence[_Contribution],
                 unfelt: frozenset[tuple[int, int]]
                 ) -> tuple[types.ReasonLine, ...]:
    """One curse of one copy, in whichever of the three fillings fits.

    A curse is read **once**, under the relic that carries it (`UI_SPEC`
    T-078 §3). It used to fall into up to three places: a line in `reasons`,
    the same thing again in `curses`, and for AD-015 a third sentence in
    `unknowns`.

    A curse the dataset does not carry gets no line, because there is no name
    to write and `evaluate` counted nothing for it either. That is the one
    place this differs from a silent effect, which does get a line even
    unnamed: the heading of a group states how many **effects** moved a
    figure, and a silent effect that said nothing would make that arithmetic
    wrong (AK-155). No count covers the curses.
    """
    moved = [one for one in mine if one.effect_id == curse_id]
    if not moved:
        name = _effect_name(ctx, curse_id)
        if not name:
            return ()
        return (types.ReasonLine(
            slot_index=candidate.slot_index,
            text=f"{name}: no number here shows what this costs.",
            is_curse=True, silence=types.SILENT_NO_NUMBER_HERE),)
    felt = (candidate.slot_index, curse_id) not in unfelt
    return tuple(
        types.ReasonLine(
            slot_index=candidate.slot_index,
            text=(_line(one, built) if felt
                  else _line_the_figure_does_not_count(one, built)),
            is_curse=True)
        for one in moved)


def curses_without_a_figure(groups: Sequence[types.SlotReasons]
                            ) -> tuple[types.ReasonLine, ...]:
    """The curses of the suggested copies to which no figure was written.

    Read back off the groups rather than worked out a second time: these are
    the very lines the block already shows, and a second derivation of the
    same set is the fault QA-082 and QA-087 each cost this project a round of
    work for. The criterion is `UI_SPEC` T-078 §4 -- no line was written, not
    "the game files carry no numbers", which for `All Resistances Down` would
    be false.
    """
    return tuple(line for group in groups for line in group.lines
                 if line.is_curse and line.silence != types.CARRIES_A_FIGURE)


def effects_without_a_figure(groups: Sequence[types.SlotReasons]
                             ) -> tuple[types.ReasonLine, ...]:
    """The effects of the suggested copies to which no figure was written.

    The same reading as `curses_without_a_figure`, and the same set the
    heading of each group counts: one line per silent effect, so that
    `effects_total - effects_with_a_figure` can be checked against it
    (AK-155).
    """
    return tuple(line for group in groups for line in group.lines
                 if not line.is_curse
                 and line.silence != types.CARRIES_A_FIGURE)


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
    which version of the game's data it came from, and **when** that data was
    read from the installation. `datasource` marks a fresh extraction with
    `regenerated`.

    The second half says the time and not the storage place, and the word
    `snapshot` is gone with it (`UI_SPEC` T-078 §8): a player does not know
    what a stored snapshot is -- AK-127 bars the word from the first-run
    screen -- and what they need to know is whether these are today's figures
    or older ones.
    """
    meta = ctx.data.get("meta") or {}
    where = ("read from your game files just now" if meta.get("regenerated")
             else "read from your game files earlier and kept since")
    version = str(meta.get("data_version") or "")
    if not version:
        return (f"Ranked on game data {where}. It does not say which game "
                f"version it is from, so these figures cannot be tied to a "
                f"patch.")
    return f"Ranked on game data version {version}, {where}."


def _held_slots_line(problem: types.SlotProblem) -> str:
    """What the search was not allowed to touch, or "" when it was all free.

    A run finding in the sense of AD-025 -- it carries a count, and whether it
    stands at all is settled by the run. The two fillings are two different
    pieces of news: some slots held is a smaller search, every slot held is
    **no** search, and the answer is then the build as it stands (AD-014.2).

    **Two counts, two verbs** (QA-183). `is`/`are` follows the slots that are
    held; `was`/`were` follows the ones that were filled, which is the *rest*.
    On a two-slot vessel with one held they disagree, and the sentence read
    `1 of 2 slots is held, so only the other 1 were filled.`

    The last filling says what the player is looking at in the words the rest
    of the advisor uses for it (`UI_SPEC` T-078 §8). It read `scored.`, a
    participle on its own at the end of a sentence, where A11 asks for a word
    the player can already see on the screen.
    """
    held = len(problem.held)
    slots = len(problem.slots)
    if not held:
        return ""
    if held == slots:
        return (f"All {slots} slots are held, so there was nothing to search "
                f"— this is your build as it stands, with its figure.")
    rest = slots - held
    return (f"{held} of {slots} slots {'is' if held == 1 else 'are'} held, so "
            f"only the other {rest} {'was' if rest == 1 else 'were'} filled.")


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
                                 ctx: types.GoalContext, goal: types.Goal,
                                 built: model.Build,
                                 contributions: Sequence[_Contribution]
                                 ) -> frozenset[tuple[int, int]]:
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

    What comes back is which curses those are, by slot and id; the sentence
    they get is `_line_the_figure_does_not_count`, in the group of the relic
    that carries them. Nothing is scored when no curse moved a figure -- the
    question has nothing to be about, and asking it anyway would cost a full
    evaluation per suggestion for an empty answer.
    """
    by_curse: dict[tuple[int, int], list[_Contribution]] = {}
    for contribution in contributions:
        if contribution.is_curse:
            by_curse.setdefault(
                (contribution.candidate.slot_index, contribution.effect_id),
                []).append(contribution)
    if not by_curse:
        return frozenset()

    ranked = goal.score(built, ctx).value
    unfelt: set[tuple[int, int]] = set()
    for carried, moved in by_curse.items():
        carrier = moved[0].candidate
        without = _without_the_curse(chosen, carrier, moved[0].effect_id)
        if goal.score(evaluate(problem, without, ctx), ctx).value != ranked:
            continue
        unfelt.add(carried)
    return frozenset(unfelt)


def unknowns(problem: types.SlotProblem) -> tuple[str, ...]:
    """What this run left out, in the player's language (AD-010, A7).

    One line, and it is a run finding in the sense of AD-025.2: it carries a
    count of slots and could not be written before the run. The procedural
    sentences of the direction are not here -- they stand in `Goal.scope`,
    are read from there once for the screen, and repeating them per result is
    the noise AK-50 is written against.

    The second line this used to carry -- `A curse on <relic> changes
    <field>, which this goal does not rank.` -- is gone from here on purpose.
    It said the same thing as the curse's own line two groups further up, and
    a player should read a curse once, under the relic that carries it
    (`UI_SPEC` T-078 §3 filling ii). What it said is now the end of that
    line.

    Empty is an answer: nothing was held.
    """
    held = _held_slots_line(problem)
    if held:
        return (held,)
    return ()
