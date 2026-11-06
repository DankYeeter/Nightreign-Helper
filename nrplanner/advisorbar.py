"""The advisor's one row in the Build planner, and the states it can be in.

**One row, one place that decides what it says.** `UI_SPEC` §4 is a table of
fourteen states, and the way to get a table like that wrong is to spread it
over the call sites that reach it -- a `setText` here when a run starts, one
there when it fails, and a fifteenth state nobody named that shows the
waiting text with no run behind it. So the words live in `status_line`, a
function of a `Situation` and of nothing else: no widget, no controller, no
clock. Every row of the table is one case of it, and a case can be read
beside the row it comes from.

**What this file does not do.** It draws no suggestion and never touches a
relic slot: `Optimize` asks, the status line reports, and the answer is handed
on as it arrived (`suggestion_changed`). The three action buttons say what the
player asked for and nothing more -- the window owns the slots, so the window
is what puts a relic in one and what takes it out again. This row only knows
that it happened, because 4.13 is a state of the row.

**Why the row asks for one width and no more.** Release 1.7.1 was cut for a
label that put a 3900 px minimum on the window (`UI_SPEC` §7), and every
pixel of minimum width a widget outside the middle column's `QScrollArea`
asks for moves the whole window's floor by one. Asking for none (AK-03, until
T-334n) left the row 68 px wide at the window's 760 px floor, every control
in it 0 to 1 px (QA-292). So the row breaks into two lines below the width
one line needs (AK-395), and asks for exactly the wider of the two lines at
its tightest -- one figure, about 1190 px of window and under 1366 (AK-400)
-- horizontally `Ignored` otherwise, with the status label `Ignored` inside
it as §3.1 requires.

**Two clocks that are not the same clock.** `WAIT_VISIBLE_MS` is how long a
*run* may take before the waiting is worth drawing (4.2 against 4.3), and
`worker.DEBOUNCE_MS` is how long the player is left to change their mind
before a run starts at all. Both are 250 ms today and they measure different
things; importing one for the other would make a change to either silently
change the other's behaviour.
"""

from __future__ import annotations

import contextlib
import dataclasses
import enum
import html

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import (QBoxLayout, QComboBox, QFrame, QHBoxLayout,
                               QLabel, QProgressBar, QPushButton, QScrollArea,
                               QSizePolicy, QVBoxLayout, QWidget)

from . import damage, effecttext, favourites, model, weapons, weaponslots
from .advisorblock import FoldButton
from .advisor import goals as advisor_goals
from .advisor import run as advisor_run
from .advisor import types
from .advisor.worker import AdvisorController
from .theme import SLOT_COLOURS

#: The warning line's colour: the theme's one yellow, the Yellow slot's
#: (user decision 28.10.2026, "Gelb mit ⚠"; no colour of its own).
WARNING_COLOUR = SLOT_COLOURS[2]

#: How long a run may take before the waiting is said out loud (`UI_SPEC`
#: 4.2 and 4.3, AK-09: a run under this shows neither bar nor text). Measured
#: from the moment the run *starts*, not from the click: 4.2 is a state of
#: the computation, and the debounce before it is a state of the player.
WAIT_VISIBLE_MS = 250

#: When the figures join the waiting line (`UI_SPEC` 4.4). The waiting text
#: is already up by then; this only adds what the window knew all along.
FIGURES_VISIBLE_MS = 3000

#: The directions, in the order §3.1 lists them for the combo box. A tuple
#: rather than `GOALS.keys()`: the registry is a mapping and the order of the
#: control a player reads is a decision, not an iteration order.
#:
#: **The order is a decision, the membership is not** (AK-256 point 1). Every
#: direction `advisor.goals.GOALS` scores stands here, because a direction
#: that is computed, cached and offered nowhere is one the player pays for
#: and cannot reach -- the state T-191 left behind for `max_attributes`
#: (QA-228). Where each one stands is still a decision: `max_attributes` goes
#: last because the two before it are `GOAL.md` A3's pair and the player
#: already knows their order, and because this tuple is also the order of the
#: value rows on every relic card (AK-257, AK-258).
GOAL_ORDER = ("max_damage", "min_damage_taken", "max_attributes")

#: Widest the direction box may get (§3.1). The tighter of the two boxes a
#: direction label has to fit -- the picker's `Sort by` has 220 px -- so a
#: label measured against this one fits in both, and AK-257 argues from that.
#: What stands to the right of it is the status line, whose own width is
#: bound by AK-194, which is why a label that will not fit is shortened and
#: this number is not raised.
GOAL_BOX_WIDTH = 200

#: §3.1: the gap between two controls of the row, and between its two lines.
SPACING = 6

#: AK-395: the least width the status line keeps while the row stays on one
#: line. One pixel less and the row breaks in two, so one line always means
#: nothing shortened and a status that is more than a stroke.
STATUS_FLOOR = 48

#: AK-399: how far `goal_box`, `hit_with_box` and `damage_type_box` may
#: shrink, each capped at its own `sizeHint` -- only on the first of two
#: lines, and only below the width that line asks for.
BOX_FLOORS = (120, 100, 80)

#: The two captions of each two-sided button (4.2, 4.13), indexed by "is the
#: run being waited for" and "has it been applied". The row's width counts
#: the wider of each, so a caption changing never moves the row from one line
#: to two (AK-397).
OPTIMIZE_CAPTIONS = ("Optimize", "Cancel")
APPLY_CAPTIONS = ("Apply all", "Undo apply")

#: The separator of the two-clause status lines (4.9, 4.11), a middle dot
#: with two spaces a side. Written once because it is invisible in a diff.
CLAUSES = "  ·  "

#: `UI_SPEC` 4.1: what `Optimize` promises and what it does not do.
OPTIMIZE_TOOLTIP = ("Fills every slot from the relics in your save. Nothing "
                    "changes until you apply it.")

#: AK-302: the `Filters` button, in every state, outside AK-07's budget.
FILTERS_TOOLTIP = ("Mark effects you always want (Favourite) or never want "
                   "(Avoid) in a suggestion.")

#: AK-351: the row's first box has no label beside it, unlike the two that
#: follow it -- so its own tooltip is what a reader has once its text no
#: longer fits at the derived opening width (AK-350). Static, like the two
#: beside it (AK-340): what the control is for, never what happens to be
#: chosen in it.
GOAL_BOX_TOOLTIP = "Chooses what the Advisor ranks your build for."

#: AK-340: what the "Hit with" box chooses, which of the two things the game
#: calls a skill it counts, and that the spell it ranks is the one the
#: selected or the starting catalyst throws -- without the third sentence
#: `Incantations` reads as "any incantation I find in the run", the
#: non-goal `GOAL.md` A26 names. Static, like the one beside it.
HIT_WITH_TOOLTIP = ("Chooses what the figure ranks: the starting armament, "
                    "its Weapon Art, or the spell of the staff or seal on "
                    "the selected tile (or else the starting one). Weapon "
                    "art counts Weapon Arts only — a Nightfarer's own skills "
                    "are never counted. Sorceries, Incantations and a school "
                    "rank the one spell that staff or seal casts, not a "
                    "spell found in the run.")

#: AK-340: what the damage-type box does, one sentence now that the arts
#: have a box of their own. Static -- it says what the control is for, never
#: what happens to be chosen in it. The direction's name is filled in from
#: the registry rather than written here, because AK-256 point 2 gives the
#: registry the only copy of it (`test_no_direction_label_is_written_
#: into_a_control` walks this file for the others).
DAMAGE_TYPE_TOOLTIP = "Restricts {direction} to one kind of damage."

#: AK-347: both halves of the question survive a restart, in the same store
#: `uiscale.KEY` and `app.PANES_KEY` use. Two flat keys and not one joined
#: value: flat and without `/` or a comma on purpose -- unlike
#: `favourites.key()` neither ever has a value built onto it, so nothing here
#: can grow the two characters that would make it one (Sicherheitsvorgabe 4,
#: T-321; AD-051.5's `advisor/hit_with` describes the pair, it is not the
#: spelling of the key). The value kept under each is its box's own id form
#: (`"family:23"`, `"Fire"`), never a label -- the same rule the id form
#: answers to everywhere else. The single old key `damage_art` is not
#: translated, it is ignored (AD-051.5): it is days old.
HIT_WITH_KEY = "hit_with"
DAMAGE_TYPE_KEY = "damage_type"


class State(enum.Enum):
    """The rows of `UI_SPEC` §4, by their number and by a name.

    The number is the value so that a report, a test and the table can be
    lined up without a second lookup; the name is what the code reads.
    """

    NOTHING_YET = "4.1"
    WORKING_QUIETLY = "4.2"
    WORKING = "4.3"
    WORKING_WITH_FIGURES = "4.4"
    STOPPED = "4.5"
    SUGGESTED = "4.6"
    OUTDATED = "4.7"
    NO_SAVE = "4.8"
    SUGGESTED_WITH_SILENT_EFFECTS = "4.9"
    NOT_RANKABLE = "4.10"
    SUGGESTED_WITH_AN_EMPTY_SLOT = "4.11"
    FAILED = "4.12"
    APPLIED = "4.13"


@dataclasses.dataclass(frozen=True)
class Situation:
    """One state and everything its line needs in order to be written.

    Held as a value rather than as fields of the widget for the reason the
    module docstring gives: a status line that reads a widget can be written
    at a moment when the widget says something the run never said. A
    `Situation` is what was true when it was made.
    """

    state: State
    #: The direction's own label, as the registry spells it.
    goal_label: str = ""
    #: How many relics the save holds, for 4.4.
    relics: int = 0
    #: The slots the run was asked about, and how many of them got a relic.
    slots: int = 0
    slots_filled: int = 0
    #: Slots the run had nothing to offer for (4.11), and why (AK-443).
    slots_without_a_choice: int = 0
    empty_slots: tuple[types.EmptySlot, ...] = ()
    #: Favourite effects and favourited relics the suggestion goes without
    #: (AK-455, AK-439), in any of the three result states, and what the
    #: tooltip says about each under the line.
    favourite_effects_unmet: int = 0
    favourite_relics_left_out: int = 0
    details: tuple[str, ...] = ()
    #: AK-426, AK-429: the last clause of a result the player asked for with
    #: an X or `Reject`. AK-425: what `Cancel` says then, and 4.5 has only one
    #: other sentence.
    note: str = ""
    stopped_note: str = ""
    #: AK-365's cause: the chosen type or art nothing owned reaches,
    #: as `AdvisorResult.no_carrier_for` spells it; empty for the other two.
    no_carrier_for: str = ""
    #: The two clauses of 4.9, counted apart because they are two different
    #: things (AK-142/AK-143): a curse of a suggested copy that the run wrote
    #: no figure for is a **price** nobody put a number on, and an effect left
    #: out is one the ranking declined to count because it is conditional.
    #: Each clause appears only when its own count is not zero, so a
    #: `Situation` with both at zero is not this state at all.
    curses_without_a_number: int = 0
    effects_left_out: int = 0
    #: The Nightfarer named in 4.10, and the one-line reason of 4.12.
    nightfarer: str = ""
    reason: str = ""
    #: 4.7 only (AK-289): the run was abandoned because a *marking*
    #: (`Avoid`/`Favourite`) changed rather than the build, so the
    #: sentence must name that cause.
    marking_changed: bool = False
    #: 4.8 only (AK-406): a save was read and holds no relics, so "No save
    #: was read" would be false and `Rescan save` alone the wrong advice.
    save_is_empty: bool = False


def _lower_case_first(label: str) -> str:
    """`Maximise damage` as the waiting line spells it: `maximise damage`.

    Only the first letter, and `str.lower()` is not that: a direction whose
    label carries a proper noun would lose it.
    """
    return label[:1].lower() + label[1:]


def _slots_with_nothing(count: int) -> str:
    """AK-365's lead-in, in the number the run came back with.

    The table writes the singular. The plural is this sentence's own plural
    and not a second wording -- but it has never been reviewed, and it is in
    the report to the `ui-ux-designer` for that reason.
    """
    if count == 1:
        return "1 slot has nothing to choose from"
    return f"{count} slots have nothing to choose from"


def _empty_short(empty: types.EmptySlot) -> str:
    """AK-457's `{short}`. An unknown reason is a `KeyError`, not a fallback."""
    return {
        types.EMPTY_REQUIREMENT:
            "what is left is needed for your Favourite effects",
        types.EMPTY_PIN: f"your favourite “{empty.relic_name}” uses the rest",
        types.EMPTY_AVOIDED_AND_REJECTED:
            "everything left is rejected or carries an avoided effect",
        types.EMPTY_AVOIDED: "everything left carries an effect you avoided",
        types.EMPTY_REJECTED: "everything left is rejected",
        types.EMPTY_NOTHING: "nothing left to choose from",
    }[empty.reason]


def _slots_empty(count: int, empty_slots: tuple[types.EmptySlot, ...]) -> str:
    """The second clause of 4.11 (AK-443): one reason, or see the cards."""
    shorts = {_empty_short(empty) for empty in empty_slots}
    if len(shorts) == 1:
        return f"{count} slot{'' if count == 1 else 's'} empty: {shorts.pop()}"
    return f"{count} slots empty for different reasons — see the slot cards"


def _slots_no_carrier(count: int, choice: str) -> str:
    """The second clause of 4.11 when the run dropped its suggestions
    because nothing owned reaches the chosen type or art (AK-365)."""
    return (f"{_slots_with_nothing(count)}: nothing you own reaches "
            f"{choice} here")


def _curses_with_no_number(count: int) -> str:
    """Clause 4.9a, in the number the run came back with.

    Verbs and nouns both move with the number, which is why this is a
    function and not an f-string with a plural `s` glued on.
    """
    if count == 1:
        return "1 curse carries no number."
    return f"{count} curses carry no number."


def _effects_left_out(count: int) -> str:
    """Clause 4.9b: the conditional effects the ranking declined to count."""
    if count == 1:
        return "1 effect was left out: it only applies under a condition."
    return (f"{count} effects were left out: they only apply under a "
            f"condition.")


def _marked(count: int, state: str) -> str:
    """One AK-280 clause: `{n} effect(s) {avoided|favourited}` (AK-300)."""
    return f"{count} effect{'' if count == 1 else 's'} {state}"


def families_avoided(count: int) -> str:
    """AK-316.5: the families clause, counted apart from the ids -- one
    family can pull dozens of ids along, and a sum would read as a small,
    deliberate selection where a whole group went."""
    return f"{count} {'family' if count == 1 else 'families'} avoided"


def marking_clauses(filters) -> list[str]:
    """The AK-280 clauses of the `Filters` tooltip (AK-302, AK-316.5): how
    many effects and families the player marked, in every one of the
    fourteen states, because a marking is a standing setting and not a
    property of one run. `None` -- a row built with no filters behind it --
    has nothing to count."""
    if filters is None:
        return []
    return ([_marked(len(filters.excluded), "avoided")]
            if filters.excluded else []) + (
            [_marked(len(filters.required), "favourited")]
            if filters.required else []) + (
            [families_avoided(len(filters.avoided_families))]
            if filters.avoided_families else [])


def _closing_clauses(situation: Situation) -> tuple[str, ...]:
    """What the result goes without, effects then relics (AK-455, AK-439), and
    what the player just asked for last (AK-426).

    One clause per kind and only where there is something to say. Each ends on
    its own full stop, as 4.9's do.
    """
    effects = situation.favourite_effects_unmet
    relics = situation.favourite_relics_left_out
    return (*((f"{effects} favourite effect{'' if effects == 1 else 's'} could "
               f"not be met.",) if effects else ()),
            *((f"{relics} favourited relic{'' if relics == 1 else 's'} did not "
               f"fit.",) if relics else ()),
            *((situation.note,) if situation.note else ()))


def _clauses(head: str, *clauses: str) -> str:
    """A result sentence with whichever of its clauses have something to say.

    The order is the table's own -- first the price, then what was left out
    -- and an empty clause is not written, not written as an empty one.
    """
    return head + "".join(CLAUSES + clause for clause in clauses if clause)


def status_line(situation: Situation) -> str:
    """What the status label says in this situation -- `UI_SPEC` §4, verbatim.

    Qt-free and side-effect-free on purpose: this is the one place the
    fourteen rows are written down, so a case can hold a row of the table as
    a literal and compare. 4.14 is not in here because it is not a state --
    it is the rule that nothing in this row forces width, which the widget
    keeps by its size policies rather than by a sentence.
    """
    state = situation.state
    goal = situation.goal_label
    if state is State.NOTHING_YET:
        return "Nothing suggested yet."
    if state is State.WORKING_QUIETLY:
        return ""
    if state is State.WORKING:
        return f"Working out {_lower_case_first(goal)}…"
    if state is State.WORKING_WITH_FIGURES:
        return (f"Working out {_lower_case_first(goal)} — "
                f"{situation.relics} relics, {situation.slots} slots.")
    if state is State.STOPPED:
        return situation.stopped_note or "Stopped. Nothing was changed."
    if state is State.SUGGESTED:
        head = f"{goal} — {situation.slots_filled} of {situation.slots} slots filled"
        closing = _closing_clauses(situation)
        return _clauses(head, *closing) if closing else f"{head}."
    if state is State.OUTDATED:
        if situation.marking_changed:
            return ("The effects you marked changed while this was working "
                    "out — use Optimize again.")
        return ("Your build changed while this was working out — use "
                "Optimize again.")
    if state is State.NO_SAVE and situation.save_is_empty:
        return ("Your save has no relics in it yet — if you just played, use "
                "Rescan save; if they are on another Steam account, use Find "
                "my save.")
    if state is State.NO_SAVE:
        return ("No save was read, so there are no relics to choose from "
                "— use Find my save.")
    if state is State.SUGGESTED_WITH_SILENT_EFFECTS:
        return _clauses(
            f"{goal} — {situation.slots_filled} of "
            f"{situation.slots} slots filled",
            _curses_with_no_number(situation.curses_without_a_number)
            if situation.curses_without_a_number else "",
            _effects_left_out(situation.effects_left_out)
            if situation.effects_left_out else "",
            *_closing_clauses(situation))
    if state is State.NOT_RANKABLE:
        return (f"The game files carry no figures this goal can be ranked "
                f"on for {situation.nightfarer}, so there is nothing to "
                f"suggest.")
    if state is State.SUGGESTED_WITH_AN_EMPTY_SLOT:
        count = situation.slots_without_a_choice
        if situation.no_carrier_for:
            empty = _slots_no_carrier(count, situation.no_carrier_for)
        else:
            empty = _slots_empty(count, situation.empty_slots)
        return _clauses(f"{goal} — {situation.slots_filled} of "
                        f"{situation.slots} slots filled{CLAUSES}{empty}.",
                        *_closing_clauses(situation))
    if state is State.FAILED:
        return f"Could not work that out — {situation.reason}."
    if state is State.APPLIED:
        return "Applied. Undo puts your slots back as they were."
    raise KeyError(f"no status line is written for {state!r}")


#: Which states are a run in progress. The progress bar, the `Cancel`
#: caption and "may this be overtaken" all ask this one question.
WORKING_STATES = frozenset({State.WORKING_QUIETLY, State.WORKING,
                            State.WORKING_WITH_FIGURES})

#: Which states have an answer standing behind them. `Clear` is offered for
#: exactly these, and a change to the build throws exactly these away.
ANSWERED_STATES = frozenset({State.SUGGESTED,
                             State.SUGGESTED_WITH_SILENT_EFFECTS,
                             State.SUGGESTED_WITH_AN_EMPTY_SLOT,
                             State.NOT_RANKABLE})

#: Which states have an answer the player can still act on. 4.13 is one of
#: them: the answer is still standing after it has been applied, which is
#: what `Undo apply` and `Why` are still there for.
ACTING_STATES = ANSWERED_STATES | {State.APPLIED}


@dataclasses.dataclass(frozen=True)
class Asking:
    """One press of `Optimize`, as everything downstream needs to read it.

    The request, the live inventory and the context are what
    `AdvisorController.ask` takes. The other two are the window's own
    knowledge, needed before any answer exists: how many relics the save
    holds and whose build this is, which are 4.4's figures and 4.10's name.
    """

    request: types.AdvisorRequest
    #: The living `Inventory`. `ask()` freezes it in the calling thread and
    #: fills in the fingerprint and the generation, so nothing here may.
    inventory: object
    ctx: types.GoalContext
    nightfarer: str
    relics: int


def held_slot(index: int, card) -> types.HeldSlot:
    """One slot the player is holding, as the search has to read it.

    Public because the relic picker asks the same question of every slot but
    the open one (AD-018.1, `UI_SPEC` §3.1): the two screens read a slot card
    the same way or they are ranking against two different builds.

    A held slot with nothing in it is `relic=None`, which the search reads as
    "held and staying empty" (AD-014.7) -- a different instruction from a slot
    that is simply free, and one the player is entitled to give (AK-55).

    Curses travel with the effects and not in a compartment of their own,
    because the evaluation puts both through the same `model.compute` call
    (AD-015). A custom relic comes through here as it is: it is an **input**,
    not a suggestion, so AK-16 is untouched and AK-58 is what applies.
    """
    item = card.current_relic()
    if item is None:
        return types.HeldSlot(index=index)
    return types.HeldSlot(index=index, relic=types.HeldRelic(
        relic_id=item.relic_id,
        name=item.name,
        effect_ids=tuple(item.effect_ids),
        curse_ids=tuple(getattr(item, "curse_ids", ()) or ()),
        handle=getattr(item, "handle", None),
        colour=item.colour, is_deep=item.is_deep))


def held_swapped_art_ids(held, effects) -> tuple[int, ...]:
    """The art ids the held relics swap onto the starting armament, read off
    their effects without a calculation (AD-056.7); sorted, without repeats."""
    return tuple(sorted({
        art_id for slot in held if slot.relic is not None
        for effect_id in slot.relic.effect_ids
        if isinstance(art_id := ((effects.get(str(effect_id)) or {}).get(
            "modifiers") or {}).get("startSwordArtsId"), int)}))


def asking_from(planner, goal_id: str) -> Asking | None:
    """What the window would ask the advisor right now, or `None` (4.8).

    `None` means there is no save to choose relics from, which is a state of
    the window and not a failure -- the caller shows 4.8 and asks nothing.

    **A held slot is a boundary condition of the question, not a starting
    value** (AD-014, AD-016): it is named in `problem.held`, its effects go
    into every evaluation, and the search runs over what is left. That is why
    holding belongs in the request at all rather than in some state the
    search could overwrite -- and it is why the hold reaches the run frozen,
    as part of the cache key, and never as a live reading of the window.
    The two effect sets the player marked (A18/A19) travel the same way, on
    the same type (AD-036.1): the picker's own question is built from this
    one by replacing `held`, so it carries them without knowing. The relics
    starred for this Nightfarer too (AD-059.1) and the rolls rejected for this
    build (AD-060.3); those two the picker takes off again, because the picker
    is the hand choice.

    The request is derived from the context beside it, field by field, and
    that is not tidiness: `run.run` refuses a request whose fields describe
    another run, because the request is the cache key. Where a field is left
    empty it is left empty in **both** halves for that reason, and never in
    one of them.

    **What the run is deliberately not told: which armaments are in hand**
    (`GOAL.md` A17, AK-191). The user's decision, on which the whole feature
    turns: *"wir optimieren die stats und passiven am besten weil nur die fix
    sind. waffen und deren buffs sind alle in der runde RNG-basiert."* An
    armament and the buffs on it are rolled again every expedition, so a
    relic ranked against the one on the grid is ranked against something the
    player will not have -- and the ranking would move with it.

    **Three** fields carry that in, and leaving out any one of them alone is
    not enough. `reference` is the armament the figure is formed against --
    since AD-038 the Nightfarer's **own starting armament** at its lowest
    tier, a property of the dataset and not of the grid, so that an attribute
    a relic moves reaches the figure through that armament's scaling (A22)
    while nothing the player carries moves the ranking (A17 holds word for
    word). `weapons_held` is the grid, and a weapon-type gate is met by
    **anything** on it (`model.compute`), so "Improved Greatsword Attack
    Power" would go on counting for a greatsword and not for a bow with no
    reference in sight. Measured on 2026-09-12 over the 312 copies of the user's save,
    Wylder at the probe level, a greatsword against a bow, with the
    reference armament already left out and the grid still filled: 2 copies
    changed their figure on the grid alone -- `Deep Polished Drizzly Scene`
    (+0.0900 against 0.0000, rank 0 of the 102 Deep candidates) and `Grand
    Luminous Scene` (0.0000 against +0.0600, rank 3 of the 210 ordinary
    ones). Two copies are enough: both sat at or near the head of their
    list, which is the part of a ranking anyone reads.

    The third is `armament_effect_ids`, **the rolls on those armaments**, and
    it left with AD-032 rather than with T-188 -- the sentence above names it
    (*"und deren buffs"*), and until it went, AK-191 read word for word was
    not kept. A *stacking* roll was the harmless half: measured over the 210
    ordinary copies it moved 10 figures and not one place in the order,
    because a common factor lifts every marginal alike. A **non-stacking**
    one is the other half. It is worth once whatever else carries it, so a
    candidate that brings the same effect the armament already rolled is
    worth nothing beside it and worth something without it -- the order came
    apart from rank 3 for `Improved Holy Attack Power` and for `Physical
    Attack Up` (8850550), from rank 4 for `Improved Fire Attack Power`
    (QA-226, measured in T-189). Six such effects are in the dataset, none of
    them on a relic of this save, every one of them rollable on 120 to 141
    armaments -- so this is a state the player reaches by playing, not a
    constructed one.

    **The request loses the armaments with it.** They were in the cache key
    only because the run read them; a key that separates two runs which
    compute the same answer costs a second full search and returns the same
    list (P-1 from T-188). The starting armament's id stays in the key
    (`reference_weapon_id`): it changes only with the Nightfarer, so it
    never separates two runs that compute the same answer (AD-038.4).

    The consequence, said out loud because it reverses a rule this file used
    to keep: the advisor's build is no longer the stat sheet's build. The
    sheet answers "what am I hitting for right now" with the grid and its
    rolls; this answers "what is this relic worth between runs" against the
    one armament every expedition starts with and keeps nothing else.
    `GoalScore.scope` is where the figure says which of the two it is (A12).

    **One exception, by the user's decision of 28.10.2026:** the armament
    type of the selected tile decides which "3+ X Equipped" conditions the
    baseline counts as met (`ctx.assumed_armament_counts`). It is in the key
    beside `declared`, because a hit across two selected tiles would answer
    for the other type. **And a second (T-335b):** a staff or seal on the
    selected tile is what the spell cells cast from (`ctx.selected_catalyst`,
    in the key as `selected_catalyst_id`), the one the stat sheet's spell
    row stands on; its tier and rolls stay out, as the starting armament's.
    **And a third (01.11.2026):** the selected tile's type also decides
    which weapon-type buffs ("Improved Dagger Attack Power") the baseline
    counts as met; it reaches the key through `declared`. **And a fourth
    (01.11.2026):** the ailments the selected tile's armament inflicts
    (the starting armament for an empty tile) decide which ailment-gated
    conditions the baseline counts as met, again through `declared`.
    """
    owned = planner.owned
    if owned is None:
        return None
    hero = planner.current_hero()
    level = planner.level_slider.value()

    cards = planner.active_slots()
    slots = tuple(types.Slot(index=index, colour=slot.colour, deep=slot.deep)
                  for index, slot in enumerate(cards))
    holding = planner.held_slot_indices()
    held = tuple(held_slot(index, card) for index, card in enumerate(cards)
                 if index in holding)
    problem = types.SlotProblem(slots=slots, held=held,
                                excluded=planner.effect_filters.resolved_excluded,
                                required=planner.effect_filters.required,
                                rejected=planner.rejected_rolls(),
                                pinned=favourites.marked_for(hero["id"]))

    # The baseline counts every switchable condition as met (AD-036.6): the
    # player's own declarations are merged over it, so a condition they
    # declared stands as declared. Sorted, not in `dict` order: a cache key
    # that depended on the order the player happened to flip the switches
    # would miss its own entries. The armament-count conditions the player
    # did not declare are not part of it: only one armament type of them may
    # hold in a build (QA-299), and since 28.10.2026 it is the type of the
    # armament on the selected tile, or none for an empty tile (user
    # decision: "man kann einen waffen-slot highlighten. für den soll dann
    # auch die waffengattung genommen werden können."). The one armament the
    # grid lends the question, and only its type -- A17 holds for the rest.
    # A condition without `wepTypeTrigger` carries the field's baseline,
    # the dagger type (`field_baselines`, the extractor drops a value equal
    # to it).
    baseline = {**model.advisor_defaults(), **planner.declared}
    effects = planner.data["effects"]
    selected = planner.active_slot().weapon
    # A weapon-type buff ("Improved Dagger Attack Power") the player did not
    # declare holds only for the selected tile's type, by the same user
    # decision as the count conditions below (01.11.2026); an empty tile
    # leaves it to the starting armament `model.compute` gates against. A
    # `triggerOnWepType` no armament carries (256, 512) is no type and stays.
    unselected = ({weapon.get("wep_type") for weapon in planner.data["weapons"]}
                  - {None if selected is None else selected.get("wep_type"),
                     None})
    # "Attack power up when facing frostbite-afflicted enemy" and its twins,
    # if the player did not declare them, hold only where the build inflicts
    # the ailment itself (user decision 01.11.2026): the selected tile's
    # armament, its rolls ("Attacks Inflict Frost") and the art or spell the
    # casting bar has it use, here; a relic of the build, swap relics
    # included, in `evaluate` (`ctx.awaiting_ailment`). Where a swap relic
    # reaches that art or spell, what it inflicts counts only in a build
    # without one (`ctx.pick_ailment`, QA-322). An armament on another tile
    # is not a source -- only the selected one is in hand -- and an empty
    # selected tile stands for the starting armament.
    tile, tile_index = planner.active_slot(), planner.active_weapon
    if tile.weapon is None:
        tile = weaponslots.WeaponSlot(
            weapon=planner.weapon_by_id(hero.get("starting_weapon")))
        tile_index = damage.STARTING_SLOT
    inflicted: set[str] = set()
    picked: set[str] = set()
    pick_swap = ""
    if tile.weapon is not None:
        inflicted.update(tile.weapon.get("inflicts") or {})
        for effect_id in tile.effect_ids:
            inflicted.update((effects.get(str(effect_id)) or {}).get(
                "inflicts_on_hit") or {})
        if (tile.weapon.get("wep_type") in damage.GENUS_OF_CATALYST
                and any(s != -1 for s in
                        tile.weapon.get("equipped_spells") or ())):
            own = damage.spell_catalyst(tile.weapon, hero, planner.data)[1]
            used = damage.spell_thrown(model.Build(), planner.data,
                                       tile.weapon, starting=own,
                                       chosen=tile.spell_id)[0]
            pick_swap = "spells" if own else ""
        else:
            used = damage.art_in_use(tile, tile_index,
                                     model.Build(), hero, planner.data)[0]
            pick_swap = "arts" if damage.is_starting_armament(
                tile.weapon, hero, tile_index) else ""
        (picked if pick_swap else inflicted).update(
            (used or {}).get("inflicts") or {})
    unmet = {effect_id for effect_id in baseline
             if effect_id not in planner.declared
             and effecttext.ailment_awaited(effects[str(effect_id)])
             not in inflicted | {None}}
    pick_ailment = {effect_id for effect_id in unmet
                    if effecttext.ailment_awaited(effects[str(effect_id)])
                    in picked}
    awaiting = unmet - pick_ailment
    baseline = {effect_id: count for effect_id, count in baseline.items()
                if effect_id not in unmet
                and (effect_id in planner.declared
                     or effects[str(effect_id)]["modifiers"].get(
                         "triggerOnWepType") not in unselected)}
    counts = {effect_id for effect_id in baseline
              if effect_id not in planner.declared
              and effecttext.counts_armaments(effects[str(effect_id)])}
    neutral_type = (planner.data.get("field_baselines") or {}).get(
        "wepTypeTrigger")
    assumed = set() if selected is None else {
        effect_id for effect_id in counts
        if effects[str(effect_id)]["modifiers"].get(
            "wepTypeTrigger", neutral_type) == selected.get("wep_type")}
    declared = tuple(sorted(item for item in baseline.items()
                            if item[0] not in counts))
    weighting = advisor_goals.DEFAULT_WEIGHTING
    # The hand is read, although the grid is not: it is a feature of the
    # build the player sets, not of an armament that is rolled (AK-293).
    two_handed = planner.stat_sheet.hand_switch.isChecked()
    # And both halves of the damage question, for the same reason and off the
    # row that owns them (AK-337): they are features of the question, not
    # second directions (AD-051), and each box answers its own field, so
    # nothing is taken apart here. Both go into **both** halves below or
    # `run.run` refuses the question -- the key would be standing for a run
    # that was not asked.
    hit_with = planner.advisor_bar.hit_with()
    damage_type = planner.advisor_bar.damage_type()
    # The starting armament, without its rolls: `weapons_held` and
    # `armament_effect_ids` stay empty (A17, AD-032, QA-226). Of the grid
    # only the selected tile is read: its type above, its staff or seal
    # below. Missing from the dataset, the run falls back to the multiplier
    # mean and says so (`goals._NO_ARMAMENT`, AD-038.1).
    starting = planner.weapon_by_id(hero.get("starting_weapon"))
    catalyst = (selected if selected is not None
                and selected.get("wep_type") in damage.GENUS_OF_CATALYST
                else None)
    # AK-415: the spell chosen on that tile, only where a spell row is asked;
    # without a staff or seal there, the one chosen on the first tile holding
    # the starting catalyst the row falls back to (director, 31.10.2026).
    start_id = (damage.start_catalyst(hero, planner.data) or {}).get("id")
    spell_tile = planner.active_slot() if catalyst is not None else next(
        (slot for slot in planner.weapon_slots
         if slot.weapon is not None and slot.weapon["id"] == start_id), None)
    spell_id = (spell_tile.spell_id
                if spell_tile is not None and advisor_goals.is_a_spell(hit_with)
                else None)
    # User decision 31.10.2026 13:50: `Weapon art` swings the selected tile's
    # armament at its tier with its art pick, as the stat sheet does; an
    # empty tile leaves the starting armament to it, as T-335b leaves the
    # starting catalyst to a spell row.
    tile = planner.active_slot()
    art_tile = (types.ReferenceArmament(
        weapon=tile.weapon, tier=tile.tier, slot_index=planner.active_weapon,
        art_id=tile.art_id)
        if hit_with == model.SKILL_ART and tile.weapon is not None else None)
    reference = None if starting is None else types.ReferenceArmament(
        weapon=starting, tier=weapons.MIN_UPGRADE,
        slot_index=damage.STARTING_SLOT)
    ctx = types.GoalContext(
        data=planner.data,
        hero=hero,
        level=level,
        reference=reference,
        weighting=weighting,
        declared=declared,
        assumed_armament_counts=tuple(sorted(assumed)),
        awaiting_ailment=tuple(sorted(awaiting)),
        pick_ailment=tuple(sorted(pick_ailment)),
        pick_swap=pick_swap if pick_ailment else "",
        selected_catalyst=catalyst,
        selected_spell_id=spell_id,
        art_tile=art_tile,
        held_swapped_art_ids=held_swapped_art_ids(held, effects),
        two_handed=two_handed,
        hit_with=hit_with,
        damage_type=damage_type,
    )
    meta = planner.data.get("meta") or {}
    request = types.AdvisorRequest(
        hero_id=hero["id"],
        level=level,
        problem=problem,
        goal_id=goal_id,
        weighting_id=weighting.id,
        # The key says what the run was asked: since AD-038 about the starting
        # armament, since AD-032 not about any rolls. Anything else here
        # would be a key standing for a run that did not happen, and
        # `run.run` refuses it: it compares the id in the key against the
        # context.
        reference_weapon_id=None if starting is None else starting["id"],
        declared=declared,
        assumed_armament_counts=ctx.assumed_armament_counts,
        pick_ailment=ctx.pick_ailment,
        pick_swap=ctx.pick_swap,
        selected_catalyst_id=None if catalyst is None else catalyst["id"],
        selected_spell_id=spell_id,
        art_tile=None if art_tile is None else art_tile.key,
        two_handed=two_handed,
        hit_with=hit_with,
        damage_type=damage_type,
        data_version=str(meta.get("data_version") or ""),
    )
    return Asking(request=request, inventory=owned, ctx=ctx,
                  nightfarer=hero["name"], relics=owned.relic_count)


def _a_tooltip(line: str, details: tuple[str, ...] = ()) -> str:
    """The sentence and its details, one per row, shown letter for letter."""
    if not line:
        return ""
    rows = "<br>".join(html.escape(row) for row in (line, *details))
    return f"<span>{rows}</span>"


class _ElidingLabel(QLabel):
    """A label that shortens its own text and never asks for room.

    §3.1: the status area contributes nothing to the width of the row, is cut
    to `…` when there is not enough room, and carries the whole sentence
    as its tooltip. It re-elides in its own `resizeEvent` because that is the
    only moment its width is settled -- eliding from the row's `resizeEvent`
    reads the width the label had before the layout ran.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        # D-10: a relic name, a Nightfarer name and an exception message all
        # reach this label, and all three are foreign text.
        self.setTextFormat(Qt.PlainText)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self._whole = ""

    def set_whole_text(self, text: str, details: tuple[str, ...] = ()) -> None:
        """`details` go into the tooltip under the sentence, and nowhere else."""
        self._whole = text
        # A tooltip has no text format to set, so Qt decides for itself
        # whether what it is given is markup (SEC-013). Escaped **and**
        # wrapped: without the wrapper an escaped `<` would be shown as the
        # five characters `&lt;` rather than as `<`, because Qt reads a text
        # with no `<` in it as plain.
        self.setToolTip(_a_tooltip(text, details))
        # A label with no accessible name of its own reports `text()` to the
        # accessibility bridge -- the elided one -- so a screen reader never
        # got past the ellipsis, and a keyboard user has no hover (DR-023).
        # Plain strings: an accessible name has no text format either.
        self.setAccessibleName(text)
        self.setAccessibleDescription(text)
        self._draw()

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt naming
        super().resizeEvent(event)
        self._draw()

    def _draw(self) -> None:
        metrics = QFontMetrics(self.font())
        self.setText(metrics.elidedText(self._whole, Qt.ElideRight,
                                        self.width()))


#: How many rejected relics the list shows before it scrolls (AK-430).
REJECTED_ROWS_SHOWN = 4


class RejectedList(QWidget):
    """The relics rejected for this build, under the row and not in it (AK-430).

    Nothing at all with none rejected; closed, the one fold button. Open, one
    line per relic with `Suggest again`, scrolling in here rather than in the
    middle column.
    """

    #: The player took a rejection back. Carries the roll.
    suggest_again = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(0)
        self.scroller = QScrollArea()
        self.scroller.setWidgetResizable(True)
        self.scroller.setFrameShape(QFrame.NoFrame)
        self.scroller.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.fold = FoldButton("", "", self.scroller)
        column.addWidget(self.fold, 0, Qt.AlignLeft)
        column.addWidget(self.scroller)
        self.setVisible(False)

    def show_these(self, rows) -> None:
        """Draw `(roll, relic name, its effects joined)` per rejected relic."""
        self.setVisible(bool(rows))
        if not rows:
            self.fold.setChecked(False)
            return
        count = len(rows)
        said = f"{count} relic{'' if count == 1 else 's'} rejected for this build"
        self.fold.say(said, said)
        # The press that took a row back is still in that row's button.
        old_page = self.scroller.takeWidget()
        if old_page is not None:
            old_page.deleteLater()
        page = QWidget()
        lines = QVBoxLayout(page)
        lines.setContentsMargins(0, 0, 0, 0)
        lines.setSpacing(0)
        height = 0
        for roll, name, effects in rows:
            row = QHBoxLayout()
            label = _ElidingLabel()
            label.set_whole_text(f"{name} — {effects}" if effects else name)
            again = QPushButton("Suggest again")
            again.setAccessibleName(f"Suggest {name} again")
            again.clicked.connect(
                lambda _checked=False, taken=roll: self.suggest_again.emit(taken))
            row.addWidget(label, 1)
            row.addWidget(again)
            lines.addLayout(row)
            height = again.sizeHint().height()
        self.scroller.setWidget(page)
        self.scroller.setFixedHeight(height * min(count, REJECTED_ROWS_SHOWN))


class _OneOrTwoLines(QBoxLayout):
    """The question beside the doing while both fit, the doing below it
    when they do not (AK-395, AK-396).

    Two widgets laid side by side or stacked, so every control keeps its
    object, its order and its place in the tab chain (AK-403). The line
    count is settled in `setGeometry` from the width alone, before a single
    child is placed, and `heightForWidth` answers from the same rule -- so
    the column above sizes the row for the arrangement it is about to get,
    and no frame shows the other one.
    """

    def __init__(self, parent: QWidget, question: QWidget, doing: QWidget,
                 doing_need: int) -> None:
        super().__init__(QBoxLayout.LeftToRight, parent)
        self._question = question
        self._doing = doing
        self._doing_need = doing_need
        self.setContentsMargins(0, SPACING, 0, SPACING)
        self.setSpacing(SPACING)
        self.addWidget(question, 0, Qt.AlignLeft)
        self.addWidget(doing, 1)

    def one_line_need(self) -> int:
        """AK-395: the question as the direction shows it, plus the doing
        with every action button and `STATUS_FLOOR` counted."""
        return (self._question.sizeHint().width() + self.spacing()
                + self._doing_need)

    def lines_at(self, width: int) -> int:
        return 2 if width < self.one_line_need() else 1

    def setGeometry(self, rect) -> None:  # noqa: N802 - Qt naming
        self.setDirection(QBoxLayout.TopToBottom
                          if self.lines_at(rect.width()) == 2
                          else QBoxLayout.LeftToRight)
        super().setGeometry(rect)

    def hasHeightForWidth(self) -> bool:  # noqa: N802 - Qt naming
        return True

    def heightForWidth(self, width: int) -> int:  # noqa: N802 - Qt naming
        margins = self.contentsMargins()
        heights = (self._question.sizeHint().height(),
                   self._doing.sizeHint().height())
        lines = (sum(heights) + self.spacing()
                 if self.lines_at(width) == 2 else max(heights))
        return margins.top() + lines + margins.bottom()


def _widest_hint(button: QPushButton, captions: tuple[str, ...]) -> int:
    """The button's `sizeHint` width under the widest of its captions,
    leaving it on the first."""
    widths = []
    for caption in captions:
        button.setText(caption)
        widths.append(button.sizeHint().width())
    button.setText(captions[0])
    return max(widths)


class AdvisorBar(QWidget):
    """`ADVISOR [ goal ] [ Filters ] [ Optimize ] <status> [ Clear ]`, and
    its states.

    Built with a callable rather than with the window: everything the bar
    needs of the planner is "what would you ask right now", which is one
    question with one answer, and a bar that reached into the window would
    have to be given a window in every case that tests a state.

    `data` is the one exception and it is not a way back in: the kinds of
    damage the box offers are the dataset's own (AK-328, `model.attack_arts`),
    read **once** at construction because the dataset a window computes on
    does not change under it -- a row built without one offers the entries
    that need no dataset, which is what `All` and the five types are.
    """

    #: The answer that is standing on screen, or `None` when none is. S10b
    #: draws the blocks from this; nothing else here reads it.
    suggestion_changed = Signal(object)
    #: The three actions that need a slot card to mean anything. The row asks
    #: for them and does none of them: the window owns the slots.
    apply_all_requested = Signal()
    undo_apply_requested = Signal()
    why_requested = Signal()
    #: AK-302: the player asked for the effect filter window. The window
    #: opens it, because the window knows what the player owns.
    filters_requested = Signal()

    def __init__(self, asking, parent: QWidget | None = None, *,
                 controller: AdvisorController | None = None,
                 filters=None, data=None) -> None:
        super().__init__(parent)
        self._asking = asking
        #: The two marked sets (`effectfilters.EffectFilters`), read for the
        #: AK-280 clauses of the tooltip and for nothing else here.
        self._filters = filters
        self._controller = (AdvisorController(self) if controller is None
                            else controller)
        self._situation = Situation(State.NOTHING_YET)
        self._answer = None
        #: AK-425, AK-426, AK-429: what a run asked for from the block says
        #: if it is stopped and when it is done, and what the tooltip adds.
        self._stopped_note = ""
        self._done_note = ""
        self._done_tip = ""
        #: The asking a running or finished run was started from: 4.4 counts
        #: its relics and slots, and no answer carries them back.
        self._asked = None
        #: What to show when the controller says it has stopped. `cancel()`
        #: is how a run is abandoned whoever abandons it, so the reason has
        #: to travel beside it: the player's `Cancel` is 4.5, a build that
        #: changed under a running search is 4.7.
        self._stop_shows = None
        #: The line the row carried before the answer was applied, so that
        #: `Undo apply` puts the row back where it puts the slots back.
        self._applied_over = None
        #: True while the window is changing the build **because this row was
        #: asked to**. Applying is a change to the build like any other, so
        #: without this the answer would be thrown away as outdated (AK-12)
        #: between the first slot and the second, and there would be nothing
        #: left to undo.
        self._applying = False

        # Horizontally the row asks for no width beyond its explicit minimum
        # (set at the end, AK-400); vertically it takes the height its line
        # count gives it, which `_OneOrTwoLines.heightForWidth` reports.
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        # AK-396: the question is line one, the doing is line two -- or
        # both side by side on one line, in the same order either way.
        question_line = QWidget()
        question = QHBoxLayout(question_line)
        doing_line = QWidget()
        doing = QHBoxLayout(doing_line)
        for line in (question, doing):
            line.setContentsMargins(0, 0, 0, 0)
            line.setSpacing(SPACING)

        from .app import _heading

        # Inline rather than as a block line of its own, which is the whole
        # difference between this heading and every other one.
        heading = _heading("Advisor")
        question.addWidget(heading)

        self.goal_box = QComboBox()
        self.goal_box.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.goal_box.setMaximumWidth(GOAL_BOX_WIDTH)
        self.goal_box.setToolTip(GOAL_BOX_TOOLTIP)
        # AK-380: a name for a screen reader, and no visible label -- the
        # entries are whole sentences, and the row has 72 px to spare (AK-302).
        self.goal_box.setAccessibleName("Goal")
        for goal_id in GOAL_ORDER:
            self.goal_box.addItem(advisor_goals.GOALS[goal_id].label, goal_id)
        self.goal_box.activated.connect(self._goal_chosen)
        question.addWidget(self.goal_box)

        # AK-337: the two halves of the question, beside the direction and
        # before `Filters` -- what is hit with, and which damage counts.
        # Settings of the question and not second directions (AD-051), so
        # they are drawn like `goal_box` and shown only where the question is
        # asked at all: `max_damage` is the one direction that reads them.
        # Each has a label of its own, because an entry saying `Holy` or
        # `Bestial` on its own could be an attribute, a filter or a school.
        #
        # An entry's **data** is its field's own id form, `""` for the
        # default of each box: since AD-051 point 1 the value *is* the
        # answer, so there is no prefix to put on and nothing to take apart
        # again. No entry carries a label as its data -- `Thunder` is the
        # entry the player reads as `Lightning`.
        #
        # The dataset's own words (a school's name) are read once here and
        # not at every ranking; a `QComboBox` draws an entry through
        # `QStyledItemDelegate`, which paints the display role as plain text,
        # so game text arrives as it is written (SEC-019, and the same reason
        # `goals.chosen_label` does not escape it either).
        self.hit_with_label = QLabel("Hit with")
        question.addWidget(self.hit_with_label)
        self.hit_with_box = QComboBox()
        self.hit_with_box.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.hit_with_box.setMaximumWidth(GOAL_BOX_WIDTH)
        self.hit_with_box.setToolTip(HIT_WITH_TOOLTIP)
        self.hit_with_box.setAccessibleName("Hit with")
        # AK-338: `Weapon` first -- the armament itself, the figure this
        # program gave before there was a choice at all -- then the three
        # arts, and behind a line the schools this dataset carries. A school
        # no spell of the dataset is in is not offered at all
        # (`model.attack_arts`, AK-338 point 3), which is why `Charged` is
        # absent for every Nightfarer alike and not as a reaction to a
        # choice.
        self.hit_with_box.addItem("Weapon", "")
        arts = model.attack_arts(data or {})
        schools = [(key, label) for key, label in arts.items()
                   if key not in model.ART_LABELS]
        for key, label in arts.items():
            if key in model.ART_LABELS:
                self.hit_with_box.addItem(label, key)
        if schools:
            self.hit_with_box.insertSeparator(self.hit_with_box.count())
            for key, label in schools:
                self.hit_with_box.addItem(label, key)
        self._remember_the_choice(self.hit_with_box, HIT_WITH_KEY)
        question.addWidget(self.hit_with_box)

        self.damage_type_label = QLabel("Damage type")
        question.addWidget(self.damage_type_label)
        self.damage_type_box = QComboBox()
        self.damage_type_box.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.damage_type_box.setMaximumWidth(GOAL_BOX_WIDTH)
        self.damage_type_box.setAccessibleName("Damage type")
        self.damage_type_box.setToolTip(DAMAGE_TYPE_TOOLTIP.format(
            direction=advisor_goals.MAX_DAMAGE.label))
        # AK-339: `All` -- every kind at once -- then a line and the five
        # types. Six entries whatever the dataset holds: the arts moved to
        # the box above, so nothing here depends on what was loaded.
        self.damage_type_box.addItem("All", "")
        self.damage_type_box.insertSeparator(self.damage_type_box.count())
        for damage_type, label in weapons.DAMAGE_LABELS.items():
            self.damage_type_box.addItem(label, damage_type)
        self._remember_the_choice(self.damage_type_box, DAMAGE_TYPE_KEY)
        question.addWidget(self.damage_type_box)

        # AK-302: visible and live in all fourteen states, a run in flight
        # included -- AK-289 presupposes a marking under a run.
        self.filters_button = QPushButton("Filters")
        self.filters_button.clicked.connect(self.filters_requested)
        doing.addWidget(self.filters_button)

        self.optimize_button = QPushButton("Optimize")
        self.optimize_button.setToolTip(OPTIMIZE_TOOLTIP)
        self.optimize_button.clicked.connect(self._optimize_or_cancel)
        doing.addWidget(self.optimize_button)

        self.status = _ElidingLabel()
        doing.addWidget(self.status, 1)

        # The same indeterminate bar `firstrun._Window` uses: there is no
        # total to count towards, and AD-006.1 says so in the worker.
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)
        self.progress.setMinimumWidth(0)
        self.progress.setVisible(False)
        doing.addWidget(self.progress)

        # The three action buttons of §3.1, in the order that section writes
        # them. `Apply all` and `Undo apply` are one button because they are
        # one action seen from two sides -- two buttons would have to disagree
        # about which of them is live, and the table gives the row one state
        # for it (4.13).
        self.apply_button = QPushButton("Apply all")
        self.apply_button.clicked.connect(self._apply_or_undo)
        doing.addWidget(self.apply_button)

        self.why_button = QPushButton("Why")
        # AK-378: the card's button reads `Why this relic`; this one is the
        # whole account, and the tooltip says so where the 80 px do not.
        self.why_button.setToolTip("Why this whole suggestion")
        self.why_button.clicked.connect(self.why_requested)
        doing.addWidget(self.why_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.setToolTip("Put the suggestion away")
        self.clear_button.clicked.connect(self.clear)
        doing.addWidget(self.clear_button)

        # AK-399: the boxes may give way, each only so far; the labels and
        # every button never do (AK-398), which is their own size policy.
        boxes = (self.goal_box, self.hit_with_box, self.damage_type_box)
        for box, floor in zip(boxes, BOX_FLOORS):
            box.setMinimumWidth(min(floor, box.sizeHint().width()))
        #: What the three action buttons take on a line, each at its wider
        #: caption -- counted whether or not they are up (AK-395).
        self._action_widths = (
            _widest_hint(self.apply_button, APPLY_CAPTIONS),
            self.why_button.sizeHint().width(),
            self.clear_button.sizeHint().width())
        doing_floor = (self.filters_button.sizeHint().width()
                       + _widest_hint(self.optimize_button, OPTIMIZE_CAPTIONS)
                       + sum(self._action_widths) + 5 * SPACING)
        self._lines = _OneOrTwoLines(None, question_line, doing_line,
                                     doing_floor + STATUS_FLOOR)
        # T-335a (user decision 28.10.2026): the cause of an empty slot that
        # nothing owned reaches, whole, in yellow under the row -- the status
        # line cuts it to `…`. Wraps rather than asking for width, and takes
        # no height while hidden.
        self.warning = QLabel()
        self.warning.setTextFormat(Qt.PlainText)
        self.warning.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.warning.setWordWrap(True)
        self.warning.setStyleSheet(f"color: {WARNING_COLOUR};")
        rows = QVBoxLayout(self)
        rows.setContentsMargins(0, 0, 0, 0)
        rows.setSpacing(0)
        rows.addLayout(self._lines)
        rows.addWidget(self.warning)
        # AK-400: the width of the wider line at its tightest, the pairs of
        # the damage question counted under every direction -- so the
        # window's minimum is one figure, whatever the row is showing.
        question_floor = (sum(label.sizeHint().width() for label in (
            heading, self.hit_with_label, self.damage_type_label))
            + sum(box.minimumWidth() for box in boxes) + 5 * SPACING)
        self.setMinimumWidth(max(question_floor, doing_floor))

        self._wait_timer = QTimer(self)
        self._wait_timer.setSingleShot(True)
        self._wait_timer.timeout.connect(self._waiting_is_worth_saying)
        self._figures_timer = QTimer(self)
        self._figures_timer.setSingleShot(True)
        self._figures_timer.timeout.connect(self._say_the_figures)

        self._controller.started.connect(self._on_started)
        self._controller.ready.connect(self._on_ready)
        self._controller.failed.connect(self._on_failed)
        self._controller.stopped.connect(self._on_stopped)

        self._show_the_damage_types()
        self._show(Situation(State.NOTHING_YET))

    @property
    def lines(self) -> int:
        """AK-395: 1 while the row stands on one line, 2 once it broke."""
        return (2 if self._lines.direction() == QBoxLayout.TopToBottom
                else 1)

    def action_buttons_extra_width(self) -> int:
        """What `Apply all`/`Why`/`Clear` take on a line, at their `sizeHint`.

        From the hints and not from the row's minimum: that minimum is one
        figure now (AK-400) and says nothing about what a suggestion adds.
        Counted whether or not a suggestion is up, so `Planner._opening_width`
        gives the same answer before one and after (AK-05).
        """
        return sum(width + SPACING for width in self._action_widths)

    def damage_question_extra_width(self) -> int:
        """What the two pairs of the damage question take on a line, at their
        `sizeHint` (AK-349, AK-401).

        Counted under every direction: the pairs are hidden under the other
        two (AK-337), and the opening width may not depend on which
        direction the player left the row on.
        """
        return sum(widget.sizeHint().width() + SPACING for widget in (
            self.hit_with_label, self.hit_with_box,
            self.damage_type_label, self.damage_type_box))

    # -- what the window says to the bar ------------------------------------

    @property
    def situation(self) -> Situation:
        """Which state the row is in, and the figures its line was written
        from."""
        return self._situation

    @property
    def answer(self):
        """The `AdvisorResult` on screen, or `None`."""
        return self._answer

    def the_build_changed(self, *, marking_changed: bool = False) -> None:
        """Nightfarer, vessel, Deep, level or a slot changed (AK-12).

        A run in flight is abandoned and says 4.7: it was asked about a build
        that no longer exists, and its answer would name slots the player has
        since filled by hand. An answer already on screen is thrown away for
        the same reason -- §4 has no line for a suggestion that outlived its
        build, so the row goes back to saying that nothing is suggested,
        which is then true.

        **Applying is the one change that is not an outdating.** `Apply all`,
        `Undo apply` and `Use` all change the build, and every change to the
        build ends up here -- so an answer being applied would throw itself
        away half way through. `while_the_player_applies_it` is how the
        window says that this change is the one the row asked for.

        `marking_changed` (AK-289) is `True` only when an effect was marked
        or unmarked (`effectfilters.EffectFilters.changed`): the abandonment
        is real either way, but the sentence must not blame the build for a
        change the player made to the question.

        **Asked of the controller, not of the row's state** (QA-268). Between
        the click and `started` a question waits out the debounce while the
        row still draws 4.1; it is the row's question from the click, and a
        change in that window outdates it exactly as it outdates a run.
        `cancel()` says whether there was anything to stop, and `stopped`
        arrives inside it -- so the reason is laid down first and picked up
        again when there was nothing.
        """
        if self._applying:
            return
        self._stop_shows = Situation(State.OUTDATED,
                                     marking_changed=marking_changed)
        if self._controller.cancel():
            return
        self._stop_shows = None
        self._forget_the_answer()
        self._show(self._resting())

    def the_data_is_changing(self) -> None:
        """Called before the save or the dataset is read again (AD-006.7).

        Stops the run and empties the cache **before** the material changes:
        `model` keeps its tables in module globals, and every stored answer
        was worked out on what is about to be replaced.
        """
        self._forget_the_answer()
        self._controller.before_the_data_changes()

    def shutdown(self) -> None:
        """The window is closing: stop the run and wait for the thread."""
        self._wait_timer.stop()
        self._figures_timer.stop()
        self._controller.shutdown()

    def clear(self) -> None:
        """Put the answer away and go back to 4.1."""
        self._forget_the_answer()
        self._show(self._resting())

    @contextlib.contextmanager
    def while_the_player_applies_it(self):
        """The build is about to change because this row was asked to change
        it.

        A context manager rather than a flag the window sets and clears: an
        exception raised half way through an apply would otherwise leave the
        row deaf to every later change of the build, and a row that never
        hears about a change is a row that shows a suggestion for a build
        that is gone -- exactly what AK-12 exists to prevent.
        """
        was_applying = self._applying
        self._applying = True
        try:
            yield
        finally:
            self._applying = was_applying

    def the_suggestion_was_applied(self) -> None:
        """The window has put the answer into the slots: 4.13.

        The answer is kept, because `Undo apply` and `Why` are both still
        about it. The line the row was carrying is kept too -- undoing puts
        the row back exactly as far as it puts the slots back.
        """
        if self._answer is None:
            return
        if self._situation.state is not State.APPLIED:
            self._applied_over = self._situation
        self._show(Situation(State.APPLIED))

    def the_suggestion_was_undone(self) -> None:
        """The window has put the slots back: the row goes back with them."""
        situation = self._applied_over or self._resting()
        self._applied_over = None
        self._show(situation)

    def has_been_applied(self) -> bool:
        """Is there an applying that `Undo apply` would take back?"""
        return self._situation.state is State.APPLIED

    # -- the controls -------------------------------------------------------

    def _goal_chosen(self, _index: int) -> None:
        """A direction is a different question, so the old answer goes.

        Nothing is asked here: `Optimize` is what starts a run (§5.1), and a
        combo that computed on selection would spend a search on a player
        reading the list.
        """
        self._show_the_damage_types()
        self.the_build_changed()

    def _remember_the_choice(self, box: QComboBox, key: str) -> None:
        """Open this box where the last session left it, and keep it there.

        AK-347: each key is checked against **its own** box's entries rather
        than trusted -- a school the dataset no longer carries, or a store a
        hand-edited file broke, is `findData(...) == -1` and leaves the box
        on its default, which is already the opening index. One box falling
        back does not move the other: two keys, two checks.

        `setCurrentIndex` alone, never `activated.emit`: this is the box
        catching up with an earlier session, not a player choosing something,
        and `_choice_made` would ask a question of a build that does not
        exist yet (`choose_goal` reasons the same way).
        """
        found_at = box.findData(favourites.settings().value(key, "", type=str))
        if found_at >= 0:
            box.setCurrentIndex(found_at)
        box.activated.connect(self._choice_made)

    def _choice_made(self, _index: int) -> None:
        """AK-341: either box is another question, whichever one it was.

        The same consequence as a direction and for the same reason -- both
        are conditions of one question (AD-051), so an answer worked out
        under the old pair answers nothing now. The choices themselves stay
        when the direction leaves `max_damage` and comes back: the pairs are
        hidden, never rebuilt.

        Kept past this session too (AK-347): only a choice the player
        actually made reaches the store, the same restraint
        `gamepath.remember_save` is held to -- the restore at construction
        reads it back and never writes, so nothing loops. Both keys are
        written, not only the box that was used: the store then holds the
        pair the player is asking about, which is what the next session has
        to open on.
        """
        settings = favourites.settings()
        settings.setValue(HIT_WITH_KEY, self.hit_with())
        settings.setValue(DAMAGE_TYPE_KEY, self.damage_type())
        self.the_build_changed()

    def _show_the_damage_types(self) -> None:
        """AK-337: both halves are a question only under `max_damage`.

        Hidden rather than disabled: the other two directions do not read the
        fields at all (AD-045 point 4), and a greyed-out control that could
        never apply is the kind of furniture AK-297 already cleared away
        once. Hiding also takes both pairs out of the tab order for free
        (AK-348).
        """
        wanted = self.goal_id() == advisor_goals.MAX_DAMAGE.id
        for widget in (self.hit_with_label, self.hit_with_box,
                       self.damage_type_label, self.damage_type_box):
            widget.setVisible(wanted)

    def _apply_or_undo(self) -> None:
        """One button, and which of the two actions it is is the row's state.

        Asked of the state rather than of the caption: the caption is drawn
        from the state, and a control that read its own label back would be
        two sources for one fact.
        """
        if self.has_been_applied():
            self.undo_apply_requested.emit()
            return
        self.apply_all_requested.emit()

    def _optimize_or_cancel(self) -> None:
        if self._situation.state in WORKING_STATES:
            self._stop_shows = Situation(State.STOPPED,
                                         stopped_note=self._stopped_note)
            self._controller.cancel()
            return
        self._ask()

    def _ask(self) -> None:
        asking = self._asking(self.goal_id())
        if asking is None:
            self._show(self._no_save())
            return
        self._asked = asking
        self._stopped_note = self._done_note = self._done_tip = ""
        self._forget_the_answer()
        self._controller.ask(asking.request, asking.inventory, asking.ctx)

    def ask_again(self, *, stopped: str = "", done: str = "",
                  done_tip: str = "") -> None:
        """The same question with one mark more, asked from the block (AD-061).

        Unlike `_ask` the answer stays on screen until the new one arrives, so
        nothing jumps (AK-425), and there is no debounce: the block is locked
        meanwhile, so nothing can overtake this (AK-424). The state changes at
        once because the window reads it to lock the block.
        """
        asking = self._asking(self.goal_id())
        if asking is None:
            self._forget_the_answer()
            self._show(self._no_save())
            return
        self._asked = asking
        self._stopped_note, self._done_note = stopped, done
        self._done_tip = done_tip
        self._show(Situation(State.WORKING_QUIETLY))
        self._controller.ask(asking.request, asking.inventory, asking.ctx,
                             debounce_ms=0)

    def is_working(self) -> bool:
        """Is a run being waited for?"""
        return self._situation.state in WORKING_STATES

    def goal_id(self) -> str:
        """The direction the combo is standing on."""
        return self.goal_box.currentData()

    def hit_with(self) -> str:
        """What the question is about hitting with, `""` for the armament.

        The id form the box carries, and never the entry's text: a dataset
        that renames a school leaves the question, and the cache under it,
        exactly where it was (AD-051 point 1).
        """
        return self.hit_with_box.currentData() or ""

    def damage_type(self) -> str:
        """Which kind of damage the question counts, `""` for every kind.

        The other half of the pair, in the same id form: `Thunder` is what
        the entry `Lightning` carries.
        """
        return self.damage_type_box.currentData() or ""

    def choose_goal(self, goal_id: str) -> None:
        """Stand on another direction, asked from outside the row (AK-256).

        The relic picker's `Sort by` is not a second setting, it is this one
        seen from the other screen, so it comes through here and takes
        `_goal_chosen`'s consequence with it: the answer on screen was an
        answer to the other question and goes.

        Silent when the direction is already the one being shown -- a combo
        set to what it already says is not a change, and throwing an answer
        away for it would cost the player a search they never asked to
        repeat.
        """
        index = self.goal_box.findData(goal_id)
        if index < 0:
            raise KeyError(f"no direction {goal_id!r} in this row; it offers "
                           f"{list(GOAL_ORDER)}")
        if index == self.goal_box.currentIndex():
            return
        self.goal_box.setCurrentIndex(index)
        self._goal_chosen(index)

    # -- what the controller says -------------------------------------------

    def _on_started(self) -> None:
        """A run has begun. Nothing is drawn yet -- 4.2, and AK-09."""
        self._wait_timer.start(WAIT_VISIBLE_MS)
        self._figures_timer.start(FIGURES_VISIBLE_MS)
        self._show(Situation(State.WORKING_QUIETLY))

    def _waiting_is_worth_saying(self) -> None:
        self._show(Situation(State.WORKING, goal_label=self._goal_label()))

    def _say_the_figures(self) -> None:
        asked = self._asked
        if asked is None:
            return
        self._show(Situation(State.WORKING_WITH_FIGURES,
                             goal_label=self._goal_label(),
                             relics=asked.relics,
                             slots=len(asked.request.problem.slots)))

    def _on_ready(self, result) -> None:
        """An answer for the question being asked. The row reads its counts.

        Which of 4.6, 4.9 and 4.11 this is depends on what the run could not
        do, and an empty slot is said before a silent effect: a slot with
        nothing in it is the one the player can see for themselves.
        """
        self._stop_the_clocks()
        self._answer = result
        label = result.goal_label
        slots = len(self._asked.request.problem.slots) if self._asked else 0
        best = result.suggestions[0] if result.suggestions else None
        chosen = len(best.choices) if best is not None else 0
        # A held slot already carries its own relic, or is held empty on
        # purpose (AD-014.2/.7) -- a boundary condition the search never
        # touched, not a pool it searched and came back empty for. Left out
        # of `filled` it counted as "nothing to choose from" on every run
        # that held anything at all (QA-284).
        filled = chosen + len(result.held)
        curses = len(result.curses_without_a_figure)
        left_out = len(result.not_counted)
        said = {"goal_label": label, "slots": slots, "slots_filled": filled,
                "favourite_effects_unmet": len(result.required_left_out),
                "favourite_relics_left_out": len(result.pins_left_out),
                "note": self._done_note,
                "details": (*result.required_unmet,
                            *(f"{pin.name}: {pin.because}"
                              for pin in result.pins_left_out),
                            *((self._done_tip,) if self._done_tip else ()))}
        if slots - filled > 0:
            situation = Situation(State.SUGGESTED_WITH_AN_EMPTY_SLOT, **said,
                                  slots_without_a_choice=slots - filled,
                                  empty_slots=result.empty_slots,
                                  no_carrier_for=result.no_carrier_for)
        elif curses or left_out:
            situation = Situation(State.SUGGESTED_WITH_SILENT_EFFECTS, **said,
                                  curses_without_a_number=curses,
                                  effects_left_out=left_out)
        else:
            situation = Situation(State.SUGGESTED, **said)
        self._show(situation)
        self.suggestion_changed.emit(result)

    def _on_failed(self, reason: str) -> None:
        """4.12: one line, the run's own words, and no stack trace.

        The full stop is this sentence's, so a reason that brought its own is
        not given a second one.
        """
        self._stop_the_clocks()
        self._forget_the_answer()
        self._show(Situation(State.FAILED, reason=reason.rstrip(". ")))

    def _on_stopped(self) -> None:
        """The run was abandoned. Who abandoned it decides what is said."""
        self._stop_the_clocks()
        situation = self._stop_shows or Situation(State.STOPPED)
        self._stop_shows = None
        self._forget_the_answer()
        self._show(situation)

    # -- drawing ------------------------------------------------------------

    def _resting(self) -> Situation:
        """What the row says when nothing is running and nothing is shown."""
        if self._asking(self.goal_id()) is None:
            return self._no_save()
        return Situation(State.NOTHING_YET)

    def _no_save(self) -> Situation:
        """4.8, told apart by the mark the relic picker reads (AK-406)."""
        return Situation(State.NO_SAVE, save_is_empty=getattr(
            self.window(), "save_holds_no_relics", False))

    def _goal_label(self) -> str:
        return self.goal_box.currentText()

    def _stop_the_clocks(self) -> None:
        self._wait_timer.stop()
        self._figures_timer.stop()

    def _forget_the_answer(self) -> None:
        """Drop the answer and everything that was only true about it.

        The line to undo back to goes with the answer: it describes a state
        of a suggestion that no longer stands, and a later applying would
        otherwise undo into it.
        """
        self._applied_over = None
        if self._answer is None:
            return
        self._answer = None
        self.suggestion_changed.emit(None)

    def _show(self, situation: Situation) -> None:
        """Enter a state: the line, the progress bar, and the two captions.

        The one place any of the four changes. A caller that wanted to change
        only the caption would be describing a state, and would have to name
        which one.
        """
        self._situation = situation
        working = situation.state in WORKING_STATES
        self.status.set_whole_text(status_line(situation), situation.details)
        carrier = situation.no_carrier_for
        self.warning.setText(
            f"⚠ {advisor_run.no_carrier_sentence(carrier)}" if carrier else "")
        self.warning.setVisible(bool(carrier))
        # The status is the one thing that gives way on every width (AK-399),
        # and a label a few px wide has little to be hovered -- so the row
        # carries the sentence too. The AK-280 count of what the player
        # marked stands on the button that changes it (AK-302), not here.
        line = status_line(situation)
        self.setToolTip(_a_tooltip(line, situation.details))
        self.filters_button.setToolTip("<span>" + html.escape(CLAUSES.join(
            (FILTERS_TOOLTIP, *marking_clauses(self._filters)))) + "</span>")
        # 4.2 is a run with nothing drawn: the bar comes up with the text, at
        # the same moment, so there is no half-second of a bar on its own.
        # Asked of the situation and not of the widget: `isVisible()` is
        # false for every child of a window that has not been shown, and the
        # caption would then be wrong in exactly the cases a test drives.
        waiting_is_drawn = working and situation.state is not State.WORKING_QUIETLY
        self.progress.setVisible(waiting_is_drawn)
        self.optimize_button.setText(OPTIMIZE_CAPTIONS[waiting_is_drawn])
        # 4.8: with no save there is nothing to choose from, so neither
        # control has anything to do. Nothing else on the window is touched
        # (AK-08) -- disabling belongs to this row alone.
        answerable = situation.state is not State.NO_SAVE
        self.goal_box.setEnabled(answerable)
        self.optimize_button.setEnabled(answerable)
        self._show_the_actions(situation)

    def _show_the_actions(self, situation: Situation) -> None:
        """The action group of §3.1: none, or three, and never a fourth.

        Three states of the group, in the section's own words -- no answer
        offers none; a living answer offers `Apply all`, `Why` and `Clear`;
        an applied one offers `Undo apply`, `Why` and `Clear`.

        **4.10 offers two, and that is the same rule.** An answer that could
        not be ranked carries no suggestion, so there is nothing to apply: a
        drawn `Apply all` there would be a control with no work to do, and
        the section's first case ("no suggestion: none") is what covers it.
        `Why` stays, because 4.10 says in the table that it does.
        """
        acting = situation.state in ACTING_STATES
        applied = situation.state is State.APPLIED
        self.apply_button.setText(APPLY_CAPTIONS[applied])
        self.apply_button.setVisible(acting and (applied
                                                 or self._can_be_applied()))
        self.why_button.setVisible(acting)
        self.clear_button.setVisible(acting)

    def _can_be_applied(self) -> bool:
        """Does the answer on screen name a relic for any slot at all?"""
        answer = self._answer
        return bool(answer is not None and answer.suggestions
                    and answer.suggestions[0].choices)
