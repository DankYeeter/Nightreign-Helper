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

**Why the row forces no width.** Release 1.7.1 was cut for a label that put a
3900 px minimum on the window (`UI_SPEC` §7), and the measurement that
matters here is narrower than that story: on the Windows platform this
window's minimum width *is* the Build planner page (760 px against the page's
756 on 2026-09-07, this tree, UI scale Automatic), so every pixel of minimum
width a widget outside the middle column's `QScrollArea` asks for moves the
whole window's floor by one. The row therefore asks for none -- horizontally
`Ignored`, with the status label `Ignored` inside it as §3.1 requires -- and
is given whatever the column has. AK-03 is a measurement about this and
nothing else.

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
from PySide6.QtWidgets import (QComboBox, QHBoxLayout, QLabel, QProgressBar,
                               QPushButton, QSizePolicy, QWidget)

from .advisor import goals as advisor_goals
from .advisor import types
from .advisor.worker import AdvisorController

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

#: The separator of the two-clause status lines (4.9, 4.11), a middle dot
#: with two spaces a side. Written once because it is invisible in a diff.
CLAUSES = "  ·  "

#: `UI_SPEC` 4.1: what `Optimize` promises and what it does not do.
OPTIMIZE_TOOLTIP = ("Fills every slot from the relics in your save. Nothing "
                    "changes until you apply it.")


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
    #: Slots the run had nothing to offer for (4.11).
    slots_without_a_choice: int = 0
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


def _lower_case_first(label: str) -> str:
    """`Maximise damage` as the waiting line spells it: `maximise damage`.

    Only the first letter, and `str.lower()` is not that: a direction whose
    label carries a proper noun would lose it.
    """
    return label[:1].lower() + label[1:]


def _slots_with_nothing(count: int) -> str:
    """The second clause of 4.11, in the number the run came back with.

    The table writes the singular. The plural is this sentence's own plural
    and not a second wording -- but it has never been reviewed, and it is in
    the report to the `ui-ux-designer` for that reason.
    """
    if count == 1:
        return "1 slot has nothing to choose from"
    return f"{count} slots have nothing to choose from"


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
        return "Stopped. Nothing was changed."
    if state is State.SUGGESTED:
        return (f"{goal} — {situation.slots_filled} of "
                f"{situation.slots} slots filled.")
    if state is State.OUTDATED:
        return ("Your build changed while this was working out — use "
                "Optimize again.")
    if state is State.NO_SAVE:
        return ("No save was read, so there are no relics to choose from "
                "— use Rescan save.")
    if state is State.SUGGESTED_WITH_SILENT_EFFECTS:
        return _clauses(
            f"{goal} — {situation.slots_filled} of "
            f"{situation.slots} slots filled",
            _curses_with_no_number(situation.curses_without_a_number)
            if situation.curses_without_a_number else "",
            _effects_left_out(situation.effects_left_out)
            if situation.effects_left_out else "")
    if state is State.NOT_RANKABLE:
        return (f"The game files carry no figures this goal can be ranked "
                f"on for {situation.nightfarer}, so there is nothing to "
                f"suggest.")
    if state is State.SUGGESTED_WITH_AN_EMPTY_SLOT:
        return (f"{goal} — {situation.slots_filled} of "
                f"{situation.slots} slots filled{CLAUSES}"
                f"{_slots_with_nothing(situation.slots_without_a_choice)}.")
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
        handle=getattr(item, "handle", None)))


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
    not enough. `reference` is the armament the figure is formed against.
    `weapons_held` is the grid, and a weapon-type gate is met by **anything**
    on it (`model.compute`), so "Improved Greatsword Attack Power" would go
    on counting for a greatsword and not for a bow with no reference in
    sight. Measured on 2026-09-12 over the 312 copies of the user's save,
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
    list (P-1 from T-188).

    The consequence, said out loud because it reverses a rule this file used
    to keep: the advisor's build is no longer the stat sheet's build. The
    sheet answers "what am I hitting for right now" and keeps both fields;
    this answers "what is this relic worth between runs" and keeps neither.
    `GoalScore.scope` is where the figure says which of the two it is (A12).
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
    problem = types.SlotProblem(slots=slots, held=held)

    # Sorted, not in `dict` order: a cache key that depended on the order the
    # player happened to flip the switches would miss its own entries.
    declared = tuple(sorted(planner.declared.items()))
    weighting = advisor_goals.DEFAULT_WEIGHTING
    # No `reference`, no `weapons_held` and no `armament_effect_ids`: see the
    # docstring, A17 and AD-032. The armament grid is not read here at all
    # any more, which is why there is nothing left of it to leave out.
    ctx = types.GoalContext(
        data=planner.data,
        hero=hero,
        level=level,
        reference=None,
        weighting=weighting,
        declared=declared,
    )
    meta = planner.data.get("meta") or {}
    request = types.AdvisorRequest(
        hero_id=hero["id"],
        level=level,
        problem=problem,
        goal_id=goal_id,
        weighting_id=weighting.id,
        # The key says what the run was asked, and since A17 the run is not
        # asked about an armament -- since AD-032 not about its rolls either,
        # so `armaments` stays empty as well. Anything else here would be a
        # key standing for a run that did not happen, and `run.run` refuses
        # it: it compares the rolls in the key against the rolls in the
        # context, and one of the two filled would be the disagreement.
        reference_weapon_id=None,
        declared=declared,
        data_version=str(meta.get("data_version") or ""),
    )
    return Asking(request=request, inventory=owned, ctx=ctx,
                  nightfarer=hero["name"], relics=owned.relic_count)


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

    def whole_text(self) -> str:
        """What the label would say with room enough."""
        return self._whole

    def set_whole_text(self, text: str) -> None:
        self._whole = text
        # A tooltip has no text format to set, so Qt decides for itself
        # whether what it is given is markup (SEC-013). Escaped **and**
        # wrapped: without the wrapper an escaped `<` would be shown as the
        # five characters `&lt;` rather than as `<`, because Qt reads a text
        # with no `<` in it as plain.
        self.setToolTip(f"<span>{html.escape(text)}</span>" if text else "")
        self._draw()

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt naming
        super().resizeEvent(event)
        self._draw()

    def _draw(self) -> None:
        metrics = QFontMetrics(self.font())
        self.setText(metrics.elidedText(self._whole, Qt.ElideRight,
                                        self.width()))


class AdvisorBar(QWidget):
    """`ADVISOR [ goal ] [ Optimize ] <status> [ Clear ]`, and its states.

    Built with a callable rather than with the window: everything the bar
    needs of the planner is "what would you ask right now", which is one
    question with one answer, and a bar that reached into the window would
    have to be given a window in every case that tests a state.
    """

    #: The answer that is standing on screen, or `None` when none is. S10b
    #: draws the blocks from this; nothing else here reads it.
    suggestion_changed = Signal(object)
    #: The three actions that need a slot card to mean anything. The row asks
    #: for them and does none of them: the window owns the slots.
    apply_all_requested = Signal()
    undo_apply_requested = Signal()
    why_requested = Signal()

    def __init__(self, asking, parent: QWidget | None = None, *,
                 controller: AdvisorController | None = None) -> None:
        super().__init__(parent)
        self._asking = asking
        self._controller = (AdvisorController(self) if controller is None
                            else controller)
        self._situation = Situation(State.NOTHING_YET)
        self._answer = None
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

        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        row = QHBoxLayout(self)
        # §3.1: 6 px above and below, and nothing added at the sides -- the
        # column's own margins are already there.
        row.setContentsMargins(0, 6, 0, 6)
        row.setSpacing(6)

        from .app import _heading

        # Inline rather than as a block line of its own, which is the whole
        # difference between this heading and every other one.
        row.addWidget(_heading("Advisor"))

        self.goal_box = QComboBox()
        self.goal_box.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.goal_box.setMaximumWidth(GOAL_BOX_WIDTH)
        for goal_id in GOAL_ORDER:
            self.goal_box.addItem(advisor_goals.GOALS[goal_id].label, goal_id)
        self.goal_box.activated.connect(self._goal_chosen)
        row.addWidget(self.goal_box)

        self.optimize_button = QPushButton("Optimize")
        self.optimize_button.setToolTip(OPTIMIZE_TOOLTIP)
        self.optimize_button.clicked.connect(self._optimize_or_cancel)
        row.addWidget(self.optimize_button)

        self.status = _ElidingLabel()
        row.addWidget(self.status, 1)

        # The same indeterminate bar `firstrun._Window` uses: there is no
        # total to count towards, and AD-006.1 says so in the worker.
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)
        self.progress.setMinimumWidth(0)
        self.progress.setVisible(False)
        row.addWidget(self.progress)

        # The three action buttons of §3.1, in the order that section writes
        # them. `Apply all` and `Undo apply` are one button because they are
        # one action seen from two sides -- two buttons would have to disagree
        # about which of them is live, and the table gives the row one state
        # for it (4.13).
        self.apply_button = QPushButton("Apply all")
        self.apply_button.clicked.connect(self._apply_or_undo)
        row.addWidget(self.apply_button)

        self.why_button = QPushButton("Why")
        self.why_button.clicked.connect(self.why_requested)
        row.addWidget(self.why_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.setToolTip("Put the suggestion away")
        self.clear_button.clicked.connect(self.clear)
        row.addWidget(self.clear_button)

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

        self._show(Situation(State.NOTHING_YET))

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

    def the_build_changed(self) -> None:
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
        """
        if self._applying:
            return
        if self._situation.state in WORKING_STATES:
            self._stop_shows = Situation(State.OUTDATED)
            self._controller.cancel()
            return
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
        self.the_build_changed()

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
            self._stop_shows = Situation(State.STOPPED)
            self._controller.cancel()
            return
        self._ask()

    def _ask(self) -> None:
        asking = self._asking(self.goal_id())
        if asking is None:
            self._show(Situation(State.NO_SAVE))
            return
        self._asked = asking
        self._forget_the_answer()
        self._controller.ask(asking.request, asking.inventory, asking.ctx)

    def goal_id(self) -> str:
        """The direction the combo is standing on."""
        return self.goal_box.currentData()

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
        filled = len(best.choices) if best is not None else 0
        curses = len(result.curses_without_a_figure)
        left_out = len(result.not_counted)
        if slots - filled > 0:
            situation = Situation(State.SUGGESTED_WITH_AN_EMPTY_SLOT,
                                  goal_label=label, slots=slots,
                                  slots_filled=filled,
                                  slots_without_a_choice=slots - filled)
        elif curses or left_out:
            situation = Situation(State.SUGGESTED_WITH_SILENT_EFFECTS,
                                  goal_label=label, slots=slots,
                                  slots_filled=filled,
                                  curses_without_a_number=curses,
                                  effects_left_out=left_out)
        else:
            situation = Situation(State.SUGGESTED, goal_label=label,
                                  slots=slots, slots_filled=filled)
        self._show(situation)
        self.suggestion_changed.emit(result)

    def _on_failed(self, reason: str) -> None:
        """4.12: one line, the run's own words, and no stack trace.

        The full stop is this sentence's, so a reason that brought its own is
        not given a second one.
        """
        self._stop_the_clocks()
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
        asking = self._asking(self.goal_id())
        return Situation(State.NOTHING_YET if asking is not None
                         else State.NO_SAVE)

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
        self.status.set_whole_text(status_line(situation))
        # 4.2 is a run with nothing drawn: the bar comes up with the text, at
        # the same moment, so there is no half-second of a bar on its own.
        # Asked of the situation and not of the widget: `isVisible()` is
        # false for every child of a window that has not been shown, and the
        # caption would then be wrong in exactly the cases a test drives.
        waiting_is_drawn = working and situation.state is not State.WORKING_QUIETLY
        self.progress.setVisible(waiting_is_drawn)
        self.optimize_button.setText("Cancel" if waiting_is_drawn
                                     else "Optimize")
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
        self.apply_button.setText("Undo apply" if applied else "Apply all")
        self.apply_button.setVisible(acting and (applied
                                                 or self._can_be_applied()))
        self.why_button.setVisible(acting)
        self.clear_button.setVisible(acting)

    def _can_be_applied(self) -> bool:
        """Does the answer on screen name a relic for any slot at all?"""
        answer = self._answer
        return bool(answer is not None and answer.suggestions
                    and answer.suggestions[0].choices)
