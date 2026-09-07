"""The advisor's one row in the Build planner, and the states it can be in.

**One row, one place that decides what it says.** `UI_SPEC` §4 is a table of
fourteen states, and the way to get a table like that wrong is to spread it
over the call sites that reach it -- a `setText` here when a run starts, one
there when it fails, and a fifteenth state nobody named that shows the
waiting text with no run behind it. So the words live in `status_line`, a
function of a `Situation` and of nothing else: no widget, no controller, no
clock. Every row of the table is one case of it, and a case can be read
beside the row it comes from.

**What this file does not do.** It draws no suggestion, applies nothing and
never touches a relic slot: `Optimize` asks, the status line reports, and the
answer is handed on as it arrived (`suggestion_changed`). The block in the
slot card, `Apply all`, `Undo apply` and the `Why` dialog are S10b; they dock
onto the signals below without this row changing shape.

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
GOAL_ORDER = ("max_damage", "min_damage_taken")

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
    #: Effects the run wrote no figure for, plus the conditional ones it did
    #: not count (4.9). The two are told apart in the `Why` dialog, not here.
    silent_effects: int = 0
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
        return ("Your build changed while this was working out. Optimize "
                "again.")
    if state is State.NO_SAVE:
        return ("No save was read, so there are no relics to choose from "
                "— use Rescan save.")
    if state is State.SUGGESTED_WITH_SILENT_EFFECTS:
        return (f"{goal} — {situation.slots_filled} of "
                f"{situation.slots} slots filled{CLAUSES}"
                f"some effects carry no numbers.")
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


def asking_from(planner, goal_id: str) -> Asking | None:
    """What the window would ask the advisor right now, or `None` (4.8).

    `None` means there is no save to choose relics from, which is a state of
    the window and not a failure -- the caller shows 4.8 and asks nothing.

    **Every slot is free.** `Optimize` says it fills every slot from the
    relics in the save, so the problem holds no held slots at all; holding is
    S10b's, and a held slot arriving here would be a boundary condition this
    row never showed the player.

    The request is derived from the context beside it, field by field, and
    that is not tidiness: `run.run` refuses a request whose fields describe
    another run, because the request is the cache key. The armaments are
    read once and both halves built from that reading for the same reason.
    """
    owned = planner.owned
    if owned is None:
        return None
    hero = planner.current_hero()
    level = planner.level_slider.value()

    slots = tuple(types.Slot(index=index, colour=slot.colour, deep=slot.deep)
                  for index, slot in enumerate(planner.active_slots()))
    problem = types.SlotProblem(slots=slots)

    armed = [slot for slot in planner.weapon_slots if slot.filled]
    armaments = tuple(types.ArmamentRef(weapon_id=slot.weapon["id"],
                                        tier=slot.tier,
                                        effect_ids=tuple(slot.effect_ids))
                      for slot in armed)
    armament_effect_ids = tuple(effect_id for armament in armaments
                                for effect_id in armament.effect_ids)

    active = planner.active_slot()
    reference = None
    if active.weapon is not None:
        reference = types.ReferenceArmament(weapon=active.weapon,
                                            tier=active.tier,
                                            slot_index=planner.active_weapon)
    # Sorted, not in `dict` order: a cache key that depended on the order the
    # player happened to flip the switches would miss its own entries.
    declared = tuple(sorted(planner.declared.items()))
    weighting = advisor_goals.DEFAULT_WEIGHTING
    ctx = types.GoalContext(
        data=planner.data,
        hero=hero,
        level=level,
        reference=reference,
        weighting=weighting,
        weapons_held=tuple(planner.equipped_weapons()),
        armament_effect_ids=armament_effect_ids,
        declared=declared,
    )
    meta = planner.data.get("meta") or {}
    request = types.AdvisorRequest(
        hero_id=hero["id"],
        level=level,
        problem=problem,
        goal_id=goal_id,
        weighting_id=weighting.id,
        reference_weapon_id=(None if reference is None
                             else reference.weapon["id"]),
        armaments=armaments,
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
    #: The three actions that need a slot card to mean anything (S10b). They
    #: are emitted by controls this task does not build, and are named here
    #: so that adding those controls does not change this row's shape.
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
        self.goal_box.setMaximumWidth(200)
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
        """
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

    # -- the controls -------------------------------------------------------

    def _goal_chosen(self, _index: int) -> None:
        """A direction is a different question, so the old answer goes.

        Nothing is asked here: `Optimize` is what starts a run (§5.1), and a
        combo that computed on selection would spend a search on a player
        reading the list.
        """
        self.the_build_changed()

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
        silent = len(result.effects_without_a_figure) + len(result.not_counted)
        if slots - filled > 0:
            situation = Situation(State.SUGGESTED_WITH_AN_EMPTY_SLOT,
                                  goal_label=label, slots=slots,
                                  slots_filled=filled,
                                  slots_without_a_choice=slots - filled)
        elif silent:
            situation = Situation(State.SUGGESTED_WITH_SILENT_EFFECTS,
                                  goal_label=label, slots=slots,
                                  slots_filled=filled, silent_effects=silent)
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
        self.clear_button.setVisible(situation.state in ANSWERED_STATES)
