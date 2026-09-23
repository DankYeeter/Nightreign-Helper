"""The advisor's row: every line of `UI_SPEC` §4, and the order they come in.

**Two halves, and they prove different things.** The first half drives the row
through a controller of the test's own, because the states of §4 are about
*when* a thing is said and a real search cannot be made to take 251 ms on
demand. The second half builds the real window with the real
`AdvisorController` and runs a real search over the frozen slot: that
is the only thing that can show the request the window builds is a request
the run accepts, and it is where AK-11 and AK-13 are measured.

**The expected words are literals out of `UI_SPEC.md`, never imported.** A
case that formatted the sentence the way the module formats it would agree
with the module whatever either of them said.
"""

from __future__ import annotations

import dataclasses
import html
import time

import pytest
from PySide6.QtCore import QObject, QSettings, Qt, Signal
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QScrollArea

from nrplanner import advisorbar, favourites
from nrplanner.advisor import goals, types
from tests import rendered
from tests.advisor_row_at_the_window import NARROW_DESKTOPS

#: How long a case may wait for a real search of the player's own save. The
#: worst measured run is about 960 ms (`run.py`, 309 relics, six free slots);
#: this is that with room for a machine under load, and it is a timeout, not
#: a budget -- nothing is asserted about how long the run took.
A_RUN_AT_MOST = 30.0

#: How long a case waits for the waiting to be drawn: the 250 ms `UI_SPEC`
#: 4.3 names, plus 120 ms for the event loop to get round to the timer.
#: Deliberately a literal and not `advisorbar.WAIT_VISIBLE_MS` -- a case that
#: waited by the module's own figure would wait longer whenever the figure
#: grew, and would have seen the waiting line at any threshold at all
#: (measured: with the constant, a mutation to 10 s left the case green).
WAITED_OUT_MS = 370


@pytest.fixture(autouse=True)
def _no_remembered_choice(qapp):
    """AK-347's two keys are cleared once for the whole session, not once
    per case (`conftest.settings_store`) -- so a case that lets a real
    choice reach them, as `test_both_choices_survive_a_restart` and the
    `activated.emit` cases below do, must not hand the next case boxes that
    no longer open on `Weapon` and `All`."""
    settings = QSettings(favourites.ORG, favourites.APP)
    for key in (advisorbar.HIT_WITH_KEY, advisorbar.DAMAGE_TYPE_KEY):
        settings.setValue(key, "")
    yield
    for key in (advisorbar.HIT_WITH_KEY, advisorbar.DAMAGE_TYPE_KEY):
        settings.setValue(key, "")


# --- the table of §4, as words ---------------------------------------------

TABLE = [
    ("4.1", advisorbar.Situation(advisorbar.State.NOTHING_YET),
     "Nothing suggested yet."),
    ("4.2", advisorbar.Situation(advisorbar.State.WORKING_QUIETLY), ""),
    ("4.3", advisorbar.Situation(advisorbar.State.WORKING,
                                 goal_label="Maximise damage"),
     "Working out maximise damage…"),
    ("4.4", advisorbar.Situation(advisorbar.State.WORKING_WITH_FIGURES,
                                 goal_label="Maximise damage", relics=292,
                                 slots=6),
     "Working out maximise damage — 292 relics, 6 slots."),
    ("4.5", advisorbar.Situation(advisorbar.State.STOPPED),
     "Stopped. Nothing was changed."),
    ("4.6", advisorbar.Situation(advisorbar.State.SUGGESTED,
                                 goal_label="Maximise damage", slots=6,
                                 slots_filled=6),
     "Maximise damage — 6 of 6 slots filled."),
    ("4.7", advisorbar.Situation(advisorbar.State.OUTDATED),
     "Your build changed while this was working out — use Optimize again."),
    ("4.7-marking", advisorbar.Situation(advisorbar.State.OUTDATED,
                                         marking_changed=True),
     "The effects you marked changed while this was working out — use "
     "Optimize again."),
    ("4.8", advisorbar.Situation(advisorbar.State.NO_SAVE),
     "No save was read, so there are no relics to choose from — use Rescan "
     "save."),
    ("4.9a", advisorbar.Situation(
        advisorbar.State.SUGGESTED_WITH_SILENT_EFFECTS,
        goal_label="Maximise damage", slots=6, slots_filled=6,
        curses_without_a_number=1),
     "Maximise damage — 6 of 6 slots filled  ·  1 curse carries no number."),
    ("4.9b", advisorbar.Situation(
        advisorbar.State.SUGGESTED_WITH_SILENT_EFFECTS,
        goal_label="Maximise damage", slots=6, slots_filled=6,
        effects_left_out=1),
     "Maximise damage — 6 of 6 slots filled  ·  1 effect was left out: it "
     "only applies under a condition."),
    ("4.9a+b", advisorbar.Situation(
        advisorbar.State.SUGGESTED_WITH_SILENT_EFFECTS,
        goal_label="Maximise damage", slots=6, slots_filled=6,
        curses_without_a_number=2, effects_left_out=3),
     "Maximise damage — 6 of 6 slots filled  ·  2 curses carry no number.  "
     "·  3 effects were left out: they only apply under a condition."),
    ("4.10", advisorbar.Situation(advisorbar.State.NOT_RANKABLE,
                                  nightfarer="Wylder"),
     "The game files carry no figures this goal can be ranked on for Wylder, "
     "so there is nothing to suggest."),
    ("4.11", advisorbar.Situation(
        advisorbar.State.SUGGESTED_WITH_AN_EMPTY_SLOT,
        goal_label="Maximise damage", slots=4, slots_filled=3,
        slots_without_a_choice=1),
     "Maximise damage — 3 of 4 slots filled  ·  1 slot has nothing to choose "
     "from."),
    ("4.11 blocked, one", advisorbar.Situation(
        advisorbar.State.SUGGESTED_WITH_AN_EMPTY_SLOT,
        goal_label="Maximise damage", slots=1, slots_filled=0,
        slots_without_a_choice=1, blocked_by_a_requirement=True),
     "Maximise damage — 0 of 1 slots filled  ·  1 slot is blocked by a "
     "requirement you marked."),
    ("4.11 blocked, three", advisorbar.Situation(
        advisorbar.State.SUGGESTED_WITH_AN_EMPTY_SLOT,
        goal_label="Maximise damage", slots=3, slots_filled=0,
        slots_without_a_choice=3, blocked_by_a_requirement=True),
     "Maximise damage — 0 of 3 slots filled  ·  3 slots are blocked by a "
     "requirement you marked."),
    ("4.11 no carrier, one (AK-365)", advisorbar.Situation(
        advisorbar.State.SUGGESTED_WITH_AN_EMPTY_SLOT,
        goal_label="Maximise damage", slots=1, slots_filled=0,
        slots_without_a_choice=1,
        no_carrier_for="fire damage with Sorceries"),
     "Maximise damage — 0 of 1 slots filled  ·  1 slot has nothing to choose "
     "from: nothing you own reaches fire damage with Sorceries here."),
    ("4.11 no carrier, three (AK-365)", advisorbar.Situation(
        advisorbar.State.SUGGESTED_WITH_AN_EMPTY_SLOT,
        goal_label="Maximise damage", slots=3, slots_filled=0,
        slots_without_a_choice=3,
        no_carrier_for="fire damage with Sorceries"),
     "Maximise damage — 0 of 3 slots filled  ·  3 slots have nothing to "
     "choose from: nothing you own reaches fire damage with Sorceries here."),
    ("4.12", advisorbar.Situation(advisorbar.State.FAILED,
                                  reason="the save could not be read"),
     "Could not work that out — the save could not be read."),
    ("4.13", advisorbar.Situation(advisorbar.State.APPLIED),
     "Applied. Undo puts your slots back as they were."),
]


@pytest.mark.parametrize("row,situation,expected",
                         TABLE, ids=[row for row, _, _ in TABLE])
def test_every_row_of_the_table_says_what_the_table_says(row, situation,
                                                         expected):
    """`UI_SPEC.md:223-251`, character for character.

    Including the auxiliaries a diff hides: the horizontal ellipsis of 4.3,
    the em dashes, and the middle dot of 4.9 and 4.11 with two spaces a side.
    """
    assert advisorbar.status_line(situation) == expected


def test_the_second_direction_is_lower_cased_only_at_its_first_letter():
    """`Minimise damage taken` waits as `minimise damage taken`.

    The whole label lower-cased would read the same here and would lose the
    first proper noun a direction is ever named after.
    """
    line = advisorbar.status_line(advisorbar.Situation(
        advisorbar.State.WORKING, goal_label="Minimise damage taken"))
    assert line == "Working out minimise damage taken…"


def test_a_state_with_no_line_written_for_it_is_loud():
    """A fifteenth state is a mistake, not an empty status line."""

    class Invented:
        pass

    with pytest.raises(KeyError):
        advisorbar.status_line(advisorbar.Situation(Invented()))


def test_the_two_thresholds_are_the_figures_the_spec_names():
    """AK-09 and 4.4, as figures rather than as behaviour.

    Both are asserted against `UI_SPEC` and not against `worker.DEBOUNCE_MS`,
    which is the same 250 and measures something else: how long the player is
    left to change their mind before a run starts at all.
    """
    assert advisorbar.WAIT_VISIBLE_MS == 250
    assert advisorbar.FIGURES_VISIBLE_MS == 3000


# --- the row, driven by a controller of the test's own ----------------------

class _Controller(QObject):
    """The four signals of `AdvisorController`, said when a case says so.

    Not a mock of the search: what the row's states are about is the order
    and the timing of these four, and a real search cannot be asked to take
    251 ms. What a real controller does with a real request is the second
    half of this file.
    """

    ready = Signal(object)
    failed = Signal(str)
    started = Signal()
    stopped = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.asked = []
        self.cancels = 0
        self.data_changes = 0
        self.shutdowns = 0
        self.running = False

    def ask(self, request, inventory, ctx) -> int:
        self.asked.append(request)
        self.running = True
        return len(self.asked)

    def cancel(self) -> bool:
        self.cancels += 1
        if not self.running:
            return False
        self.running = False
        self.stopped.emit()
        return True

    def before_the_data_changes(self) -> None:
        self.data_changes += 1
        self.cancel()

    def shutdown(self, timeout_ms: int = 0) -> None:
        self.shutdowns += 1

    def begins(self) -> None:
        self.running = True
        self.started.emit()

    def answers(self, result) -> None:
        self.running = False
        self.ready.emit(result)


def _an_asking(relics: int = 292, slots: int = 6) -> advisorbar.Asking:
    """One press of `Optimize`, with no dataset behind it.

    The request is real -- it is what the row reads its slot count off -- and
    the context is the empty one, because no search is run here.
    """
    problem = types.SlotProblem(slots=tuple(
        types.Slot(index=index, colour=1, deep=index >= 3)
        for index in range(slots)))
    request = types.AdvisorRequest(hero_id=1, level=15, problem=problem,
                                   goal_id="max_damage",
                                   weighting_id=goals.DEFAULT_WEIGHTING.id)
    ctx = types.GoalContext(data={}, hero={"id": 1, "name": "Wylder"},
                            level=15, reference=None,
                            weighting=goals.DEFAULT_WEIGHTING)
    return advisorbar.Asking(request=request, inventory=object(), ctx=ctx,
                             nightfarer="Wylder", relics=relics)


def _an_answer(filled: int = 6, curses: tuple = (),
               not_counted: tuple = (),
               blocked: bool = False, held: int = 0) -> types.AdvisorResult:
    """An answer that fills `filled` slots of the question above, with
    `held` more already decided before the search ran (QA-284)."""
    choices = tuple(types.SlotChoice(slot_index=index, handle=100 + index,
                                     relic_id=200 + index, name=f"Relic {index}")
                    for index in range(filled))
    held_slots = tuple(types.HeldSlot(index=filled + index)
                       for index in range(held))
    score = types.GoalScore(value=1.0, display="Attack rating 100", unit="AR")
    return types.AdvisorResult(
        goal_id="max_damage", goal_label="Maximise damage",
        suggestions=(types.Suggestion(choices=choices, score=score),),
        curses_without_a_figure=curses, not_counted=not_counted,
        blocked_by_a_requirement=blocked, held=held_slots)


@pytest.fixture
def bar(qapp):
    """A row with a controller a case can drive, and a save behind it."""
    asking = {"value": _an_asking()}
    widget = advisorbar.AdvisorBar(lambda goal_id: asking["value"],
                                   controller=_Controller())
    widget.asking = asking      # so a case can take the save away
    yield widget
    widget.deleteLater()


def _wait(milliseconds: int) -> None:
    """Let the event loop run for a while, and let the timers fire in it."""
    app = QApplication.instance()
    deadline = time.monotonic() + milliseconds / 1000
    while time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.005)


def test_a_row_at_rest_is_4_1_and_offers_what_optimize_promises(bar):
    """4.1: the line, and the tooltip that says nothing changes by itself."""
    assert bar.situation.state is advisorbar.State.NOTHING_YET
    assert bar.status.accessibleName() == "Nothing suggested yet."
    assert bar.optimize_button.text() == "Optimize"
    assert bar.optimize_button.toolTip() == (
        "Fills every slot from the relics in your save. Nothing changes "
        "until you apply it.")
    assert bar.progress.isHidden()


def test_every_direction_the_registry_scores_can_be_chosen(bar):
    """AK-256 point 1: the two sets are the same set.

    Not `<=`: a direction the registry scores and the control does not offer
    is computed on every run, kept in every cache and reachable by nobody --
    which is what `max_attributes` was between T-191 and T-194 (QA-228). The
    other direction of the inequality is the older fault, a control offering
    a direction no pool carries, and one assertion holds against both.
    """
    assert set(advisorbar.GOAL_ORDER) == set(goals.GOALS), (
        f"scored but not offered: "
        f"{sorted(set(goals.GOALS) - set(advisorbar.GOAL_ORDER))}; offered "
        f"but not scored: "
        f"{sorted(set(advisorbar.GOAL_ORDER) - set(goals.GOALS))}")
    assert len(set(advisorbar.GOAL_ORDER)) == len(advisorbar.GOAL_ORDER), (
        "a direction stands in the order twice")


def test_the_row_offers_the_registry_projected_and_never_name(bar):
    """AK-256 points 1 and 4: `GOAL_ORDER`'s entries, in its order, no `Name`.

    **The words come from the registry and not from this file**, which is
    the one place this module departs from its own rule about literals: the
    criterion asks for exactly that comparison, because a second list of
    words is the thing it forbids. `UI_SPEC.md` holds the wording of the
    third one and `test_advisor_goals.py` measures it against the registry,
    so the literal is written down once and not nowhere.

    `Name` is the picker's way of reading the grid, not a direction, and a
    row that offered it would be offering a goal setting that no goal
    answers to.
    """
    box = bar.goal_box
    assert [box.itemData(i) for i in range(box.count())] == list(
        advisorbar.GOAL_ORDER)
    assert [box.itemText(i) for i in range(box.count())] == [
        goals.GOALS[goal_id].label for goal_id in advisorbar.GOAL_ORDER]
    from nrplanner import relicpicker

    assert relicpicker.NAME_ORDER_LABEL not in [
        box.itemText(i) for i in range(box.count())]


def test_the_row_takes_its_words_from_the_registry_and_nowhere_else(
        qapp, monkeypatch):
    """AK-256 point 2, the counterbuild: reword a `label`, read the box.

    The mutation is in the registry, far from this row; a box still showing
    the old wording would be a second copy of the words. The row is built
    after the mutation because the entries are added once, at construction.
    """
    from types import MappingProxyType

    reworded = {goal_id: dataclasses.replace(goal, label=f"reworded {goal_id}")
                for goal_id, goal in goals.GOALS.items()}
    monkeypatch.setattr(goals, "GOALS", MappingProxyType(reworded))
    widget = advisorbar.AdvisorBar(lambda goal_id: _an_asking(),
                                   controller=_Controller())
    try:
        box = widget.goal_box
        assert [box.itemText(i) for i in range(box.count())] == [
            f"reworded {goal_id}" for goal_id in advisorbar.GOAL_ORDER]
    finally:
        widget.deleteLater()




def test_without_a_save_the_row_says_so_and_disables_its_own_two_controls(bar):
    """4.8, and only this row's controls (AK-08 is about all the others)."""
    bar.asking["value"] = None
    bar.the_build_changed()
    assert bar.situation.state is advisorbar.State.NO_SAVE
    assert bar.status.accessibleName() == (
        "No save was read, so there are no relics to choose from — use "
        "Rescan save.")
    assert not bar.goal_box.isEnabled()
    assert not bar.optimize_button.isEnabled()


def test_a_run_under_the_threshold_shows_nothing_at_all(bar):
    """AK-09, 4.2: no bar, no waiting text, no flash.

    Measured across the whole run and past it: the case waits 150 ms with the
    run going -- less than the 250 the spec allows -- and then 300 ms more
    after the answer, which is where a timer nobody stopped would fire.
    """
    bar.optimize_button.click()
    bar._controller.begins()
    _wait(150)
    early = (bar.progress.isHidden(), bar.status.accessibleName())
    bar._controller.answers(_an_answer())
    _wait(300)
    assert early == (True, "")
    assert bar.progress.isHidden()
    assert bar.status.accessibleName() == "Maximise damage — 6 of 6 slots filled."


def test_a_run_over_the_threshold_waits_out_loud(bar):
    """AK-10, 4.3: the bar, the waiting line, and `Cancel` on the button."""
    bar.optimize_button.click()
    bar._controller.begins()
    _wait(WAITED_OUT_MS)
    assert bar.situation.state is advisorbar.State.WORKING
    assert bar.status.accessibleName() == "Working out maximise damage…"
    assert not bar.progress.isHidden()
    assert bar.optimize_button.text() == "Cancel"


def test_a_long_run_adds_the_figures_the_window_knew_all_along(bar,
                                                              monkeypatch):
    """4.4. The clock is shortened, the path is the real one.

    The timer is started from the constant when the run begins, so a shorter
    constant moves the moment and nothing else. That the moment is three
    seconds is asserted as a figure above, against the spec.
    """
    monkeypatch.setattr(advisorbar, "WAIT_VISIBLE_MS", 20)
    monkeypatch.setattr(advisorbar, "FIGURES_VISIBLE_MS", 80)
    bar.optimize_button.click()
    bar._controller.begins()
    _wait(200)
    assert bar.situation.state is advisorbar.State.WORKING_WITH_FIGURES
    assert bar.status.accessibleName() == (
        "Working out maximise damage — 292 relics, 6 slots.")


def test_a_long_line_adds_nothing_to_the_width_of_the_row(bar):
    """§3.1: the status area contributes nothing to the width of the row.

    Asserted as the property and not as the size policy that keeps it: what
    the release-1.7.1 defect did was exactly this, a label with a long line
    setting a floor under the whole window.
    """
    narrow = bar.minimumSizeHint().width()
    bar._on_failed("a reason as long as the longest relic name in the game "
                   "and then some, twice over, with room to spare " * 4)
    assert bar.minimumSizeHint().width() == narrow


def test_the_sequence_rest_working_stopped_rest(bar):
    """4.1 → 4.3 → 4.5 → 4.1, in one go.

    A row that shows every state correctly on its own can still hold on to
    one: the progress bar that nobody hid, the `Cancel` that stayed on the
    button. This is why the states are asserted in sequence and not one at a
    time.
    """
    assert bar.situation.state is advisorbar.State.NOTHING_YET
    bar.optimize_button.click()
    bar._controller.begins()
    _wait(WAITED_OUT_MS)
    assert bar.situation.state is advisorbar.State.WORKING

    bar.optimize_button.click()     # it says `Cancel` now
    assert bar.situation.state is advisorbar.State.STOPPED
    assert bar.status.accessibleName() == "Stopped. Nothing was changed."
    assert bar.progress.isHidden()
    assert bar.optimize_button.text() == "Optimize"

    bar.the_build_changed()
    assert bar.situation.state is advisorbar.State.NOTHING_YET
    assert bar.progress.isHidden()


def test_a_build_that_changes_under_a_run_ends_in_4_7_and_not_in_4_5(bar):
    """AK-12: the run is abandoned, and the row says why it was.

    `Cancel` and a build that changed both go through `cancel()`, so the two
    reach the row by the same signal; if the reason did not travel with it,
    this would read `Stopped. Nothing was changed.` and the player would be
    told they had stopped something they did not.
    """
    bar.optimize_button.click()
    bar._controller.begins()
    _wait(WAITED_OUT_MS)
    bar.the_build_changed()
    assert bar.situation.state is advisorbar.State.OUTDATED
    assert bar.status.accessibleName() == (
        "Your build changed while this was working out — use Optimize "
        "again.")
    assert bar.progress.isHidden()
    assert bar.optimize_button.text() == "Optimize"


def test_an_answer_that_outlived_its_build_is_thrown_away(bar):
    """AK-12's other half: no suggestion is ever shown for a build that went.

    §4 has no line for it, so the row goes back to saying that nothing is
    suggested -- which is then true, because the answer has been dropped.
    """
    seen = []
    bar.suggestion_changed.connect(seen.append)
    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.answers(_an_answer())
    assert bar.answer is not None

    bar.the_build_changed()
    assert bar.answer is None
    assert seen[-1] is None
    assert bar.situation.state is advisorbar.State.NOTHING_YET


def test_an_answer_with_an_empty_slot_says_so_before_it_says_anything_else(bar):
    """4.11 rather than 4.6: a slot with nothing in it is the loud one."""
    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.answers(_an_answer(filled=5))
    assert bar.status.accessibleName() == (
        "Maximise damage — 5 of 6 slots filled  ·  1 slot has nothing to "
        "choose from.")


def test_a_held_slot_does_not_count_as_nothing_to_choose_from(bar):
    """QA-284: a held slot is a boundary condition the search never looked
    at (AD-014.2), not a pool it searched and found empty -- one held slot
    plus one genuinely empty one must say only the empty one has nothing to
    choose from."""
    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.answers(_an_answer(filled=4, held=1))
    assert bar.status.accessibleName() == (
        "Maximise damage — 5 of 6 slots filled  ·  1 slot has nothing to "
        "choose from.")


def test_an_empty_slot_under_an_unmeetable_requirement_names_the_requirement(
        bar):
    """AK-294 (QA-270): the pools were full, the `Favourite` effect had no
    constellation -- the second clause says so instead of claiming the slots
    had nothing to choose from. Same state 4.11, the other cause."""
    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.answers(_an_answer(filled=0, blocked=True))
    assert bar.situation.state is advisorbar.State.SUGGESTED_WITH_AN_EMPTY_SLOT
    assert bar.status.accessibleName() == (
        "Maximise damage — 0 of 6 slots filled  ·  6 slots are blocked by a "
        "requirement you marked.")


def test_a_marking_that_changes_under_a_run_names_the_marking_not_the_build(
        bar):
    """AK-289: same abandonment as AK-12, other cause, other sentence."""
    bar.optimize_button.click()
    bar._controller.begins()
    _wait(WAITED_OUT_MS)
    bar.the_build_changed(marking_changed=True)
    assert bar.situation.state is advisorbar.State.OUTDATED
    assert bar.status.accessibleName() == (
        "The effects you marked changed while this was working out — use "
        "Optimize again.")


def test_a_marking_inside_the_debounce_outdates_the_question_that_is_waiting(
        bar):
    """QA-268: the question is the row's from the click, not from `started`.

    Between `Optimize` and the controller's `started` the row still says 4.1
    while a question waits out the debounce. A marking or a build change in
    that window used to leave the waiting question alone: it then ran with
    the old sets and its answer was drawn as if it were current. No clock
    here -- the case's controller never starts, so the whole test *is* the
    debounce window.
    """
    bar.optimize_button.click()
    assert bar.situation.state is advisorbar.State.NOTHING_YET

    bar.the_build_changed(marking_changed=True)

    assert bar._controller.cancels == 1
    assert bar.situation.state is advisorbar.State.OUTDATED
    assert bar.status.accessibleName() == (
        "The effects you marked changed while this was working out — use "
        "Optimize again.")
    assert not bar._controller.running, "the waiting question was left to run"


def test_an_answer_with_silent_effects_says_that_much(bar):
    """4.9, from the answer's own two fields (AK-142/AK-143).

    Two different questions, two clauses, and they arrive from two different
    fields of the result: a curse of a suggested copy that no figure covers,
    and an effect the ranking left out because it is conditional. Driven
    through the answer rather than through a `Situation` so that the reading
    of the fields is measured as well as the wording.
    """
    curse = types.ReasonLine(slot_index=0, effect_id=1,
                             text="Taking Damage Causes Madness",
                             is_curse=True,
                             silence=types.SILENT_NO_NUMBER_HERE)
    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.answers(_an_answer(curses=(curse,),
                                       not_counted=("Under a condition",)))
    assert bar.situation.state is (
        advisorbar.State.SUGGESTED_WITH_SILENT_EFFECTS)
    assert bar.status.accessibleName() == (
        "Maximise damage — 6 of 6 slots filled  ·  1 curse carries no "
        "number.  ·  1 effect was left out: it only applies under a "
        "condition.")


def test_an_effect_with_no_figure_is_not_a_clause_of_the_status_line(bar):
    """The set that lost its clause in T-084, and 4.6 is what is left.

    `effects_without_a_figure` used to be counted into 4.9's one sentence.
    The table now writes two clauses and neither is about it -- 4.9a is
    curses and 4.9b is what was left out -- so an answer carrying only that
    set is a plain result. Written down because it is the half of QA-188 a
    wording comparison does not show.
    """
    line = types.ReasonLine(slot_index=0, effect_id=1,
                            text="Improved Melee Attack Power",
                            silence=types.SILENT_NO_NUMBER_HERE)
    answer = _an_answer()
    answer = dataclasses.replace(answer, effects_without_a_figure=(line,))
    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.answers(answer)
    assert bar.situation.state is advisorbar.State.SUGGESTED
    assert bar.status.accessibleName() == "Maximise damage — 6 of 6 slots filled."


def test_clear_puts_the_answer_away_and_is_offered_only_while_there_is_one(bar):
    """The one action of this row that needs no slot card to mean anything."""
    assert bar.clear_button.isHidden()
    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.answers(_an_answer())
    assert not bar.clear_button.isHidden()

    bar.clear_button.click()
    assert bar.answer is None
    assert bar.situation.state is advisorbar.State.NOTHING_YET
    assert bar.clear_button.isHidden()


def test_never_more_than_three_actions_stand_beside_the_status(bar):
    """AK-07, in the state that holds the most of them.

    A living answer is the busiest the row gets -- `Apply all`, `Why` and
    `Clear`. Every other state is walked in `test_advisor_apply.py`, which is
    where the fourth button would first appear.
    """
    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.answers(_an_answer())
    actions = [button for button in bar.findChildren(QPushButton)
               if button not in (bar.optimize_button, bar.filters_button)
               and not button.isHidden()]
    assert 1 <= len(actions) <= 3


def test_a_run_that_failed_says_one_line_and_no_stack_trace(bar):
    """4.12, and the full stop is the sentence's, not the reason's."""
    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.failed.emit("the dataset carries no attribute curves.")
    assert bar.status.accessibleName() == (
        "Could not work that out — the dataset carries no attribute curves.")
    assert bar.progress.isHidden()


def test_foreign_text_in_a_reason_reaches_the_label_as_text(bar):
    """D-10/AK-29: a reason is foreign input, in the label and in the tooltip.

    The tooltip is the harder half: it has no text format to set, so Qt
    decides for itself whether what it is given is markup. Escaped **and**
    wrapped -- without the wrapper Qt would read the escaped text as plain
    and show the entities themselves.
    """
    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.failed.emit("<b>relic</b> & co")
    assert bar.status.textFormat() == Qt.PlainText
    assert bar.status.accessibleName() == "Could not work that out — <b>relic</b> & co."
    assert "&lt;b&gt;relic&lt;/b&gt; &amp; co" in bar.status.toolTip()
    assert "<b>relic</b>" not in bar.status.toolTip()


def test_a_shortened_status_keeps_its_whole_sentence_for_the_accessibility_bridge(
        bar):
    """DR-023: what a screen reader gets is the sentence, not the ellipsis.

    At 67 px -- the width the status has at the derived opening width under
    Windows (T-225) -- `text()` is one word and `…`, and a `QLabel` reports
    exactly that to the bridge unless told otherwise. Name and description
    both carry the whole sentence, so the reader has it whichever it asks.
    """
    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.failed.emit("the dataset carries no attribute curves.")
    bar.status.resize(67, bar.status.height())
    whole = bar.status.accessibleName()
    assert bar.status.text() != whole and bar.status.text().endswith("…"), (
        "the status is not shortened at this width, so the case proves "
        "nothing")
    assert bar.status.accessibleName() == whole
    assert bar.status.accessibleDescription() == whole


def test_a_new_direction_puts_the_old_answer_away(bar):
    """A direction is a different question; §5.1 keeps the search on the
    button."""
    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.answers(_an_answer())
    asked = len(bar._controller.asked)

    bar.goal_box.setCurrentIndex(1)
    bar.goal_box.activated.emit(1)
    assert bar.answer is None
    assert bar.situation.state is advisorbar.State.NOTHING_YET
    assert len(bar._controller.asked) == asked


def test_the_direction_box_carries_the_registry_and_nothing_else(bar):
    """A18 took the reading box out: the directions in `GOAL_ORDER`, and the
    two pairs AK-337 names beside them -- what is hit with, and which damage
    counts.

    The other boxes are deliberately named here rather than counted away: a
    fourth `QComboBox` on this row is a control nobody specified, and the
    reading box A18 removed is the case that says why that matters.
    """
    assert [bar.goal_box.itemText(i) for i in range(bar.goal_box.count())] \
        == [goals.GOALS[goal_id].label for goal_id in advisorbar.GOAL_ORDER]
    assert bar.findChildren(type(bar.goal_box)) == [bar.goal_box,
                                                    bar.hit_with_box,
                                                    bar.damage_type_box]


#: A dataset with one spell school and three arts, so the school group of
#: AK-338 has something in it that is not the spec's own three wordings.
#: Ids, not prose: 330000 and 330400 are `MOVE_SCOPED_ARTS`' own sorcery and
#: incantation entries, 112 is the skill scope, and 23 is the school
#: `spell_families` names here (A-001).
ONE_SCHOOL = {
    "meta": {"data_version": "test"},
    "spell_families": {"23": "Bestial"},
    # A school is offered only where a spell of this dataset is in it
    # (`model.attack_arts`), so the one school here carries the one spell --
    # id, name and the two words the dataset files it under, nothing else
    # (A-001).
    "spells": [{"id": 6820, "name": "Beast Claw", "family": "Bestial",
                "category": "Incantations"}],
    "effects": {
        "330000": {"id": 330000, "modifiers": {"magicAttackRate": 1.2}},
        "330400": {"id": 330400, "modifiers": {"magicAttackRate": 1.2}},
        "1": {"id": 1, "modifiers": {"fireAttackRate": 1.2,
                                     "magicSubCategoryChange1": 112}},
        "2": {"id": 2, "modifiers": {"fireAttackRate": 1.2,
                                     "magicSubCategoryChange1": 23}},
    },
}


@pytest.fixture
def bar_with_a_school(qapp):
    """A row built over `ONE_SCHOOL`, so the school group has one in it."""
    widget = advisorbar.AdvisorBar(lambda goal_id: _an_asking(),
                                   controller=_Controller(), data=ONE_SCHOOL)
    yield widget
    widget.deleteLater()


def _entries(box):
    """`(text, data)` for every row of a combo, separators included."""
    return [(box.itemText(i), box.itemData(i)) for i in range(box.count())]


def test_hit_with_offers_the_armament_the_arts_and_the_schools(
        bar_with_a_school):
    """AK-338, its own Pruefweg: five entries and a line before `Bestial`.

    The school's label is the dataset's own (`Bestial` is in `ONE_SCHOOL`
    and nowhere in `nrplanner`), and `Weapon art` is the rename AK-338 makes
    -- read out of `model.ART_LABELS`, which is why no second copy of the
    word can drift from the headline the goal card builds from it.
    """
    entries = _entries(bar_with_a_school.hit_with_box)
    separators = [i for i, (text, data) in enumerate(entries)
                  if not text and data is None]

    assert [text for text, _data in entries if text] == [
        "Weapon", "Weapon art", "Sorceries", "Incantations", "Bestial"]
    assert [data for _text, data in entries if data is not None] == [
        "", "skill", "sorceries", "incantations", "family:23"]
    assert separators == [4], "AK-338 wants a line before the schools"


def test_hit_with_takes_its_arts_and_schools_from_the_dataset(qapp):
    """AK-338/AD-046.5: a school no dataset names is no entry.

    The counterbuild to the case above, in the shape
    `test_the_row_takes_its_words_from_the_registry_and_nowhere_else` uses:
    the same row built over a dataset without `spell_families` offers the
    entries that need no dataset and no school -- so a hand-written table of
    schools inside this file would show up here as an entry that should not
    exist. `Charged` is the measured case of this (AK-338 point 3): the
    dataset names the school and no spell is in it.
    """
    without_a_school = {**ONE_SCHOOL, "spell_families": {}}
    widget = advisorbar.AdvisorBar(lambda goal_id: _an_asking(),
                                   controller=_Controller(),
                                   data=without_a_school)
    try:
        entries = _entries(widget.hit_with_box)
        assert [text for text, _data in entries] == [
            "Weapon", "Weapon art", "Sorceries", "Incantations"], (
            "a row without a school offers no school and no line to put it "
            "behind")
    finally:
        widget.deleteLater()


def test_the_damage_type_box_offers_six_entries_whatever_the_dataset_is(
        bar_with_a_school):
    """AK-339: `All`, a line, the five types -- and no third group.

    The five are `weapons.DAMAGE_LABELS` in its own order; `Lightning` and
    `Holy` are what the player reads for `Thunder` and `Dark`, which is
    exactly why the entry's **data** is the id form and not the text
    (AD-051 point 1). Nothing here depends on the dataset, so the row built
    over `ONE_SCHOOL` carries the same seven rows as any other.
    """
    from nrplanner import weapons

    entries = _entries(bar_with_a_school.damage_type_box)
    separators = [i for i, (text, data) in enumerate(entries)
                  if not text and data is None]

    assert bar_with_a_school.damage_type_box.count() == 7
    assert [text for text, _data in entries if text] == [
        "All", "Physical", "Magic", "Fire", "Lightning", "Holy"]
    assert [data for _text, data in entries if data is not None] == [
        "", "Physics", "Magic", "Fire", "Thunder", "Dark"]
    assert separators == [1], "AK-339 wants one line and no second group"
    assert [label for label in weapons.DAMAGE_LABELS.values()] == [
        text for text, _data in entries[2:]]


def test_both_pairs_are_a_question_only_under_maximise_damage(
        bar_with_a_school):
    """AK-337: hidden under the other two directions, and AK-341: both
    choices survive the trip there and back, because the pairs are hidden
    and never rebuilt."""
    bar = bar_with_a_school
    pair = (bar.hit_with_label, bar.hit_with_box,
            bar.damage_type_label, bar.damage_type_box)
    assert not any(widget.isHidden() for widget in pair)

    bar.hit_with_box.setCurrentIndex(bar.hit_with_box.findData("family:23"))
    bar.damage_type_box.setCurrentIndex(
        bar.damage_type_box.findData("Fire"))
    bar.choose_goal("min_damage_taken")
    assert all(widget.isHidden() for widget in pair)

    bar.choose_goal("max_damage")
    assert not any(widget.isHidden() for widget in pair)
    assert (bar.hit_with(), bar.damage_type()) == ("family:23", "Fire")


def test_tab_walks_the_direction_then_both_boxes_then_filters(
        bar_with_a_school):
    """AK-348: `goal_box` -> `hit_with_box` -> `damage_type_box` ->
    `Filters`, which is the order the row builds them in and therefore the
    focus chain Qt hands out without a special case."""
    bar = bar_with_a_school
    wanted = [bar.goal_box, bar.hit_with_box, bar.damage_type_box,
              bar.filters_button]

    walked = []
    widget = bar.goal_box
    for _step in range(200):
        if widget in wanted:
            walked.append(widget)
            if len(walked) == len(wanted):
                break
        widget = widget.nextInFocusChain()

    assert walked == wanted


@pytest.mark.parametrize("box_name, choice", [
    ("hit_with_box", "family:23"),
    ("damage_type_box", "Fire"),
])
def test_either_box_puts_the_old_answer_away(bar_with_a_school, box_name,
                                             choice):
    """AK-341: a choice in **either** box is another question, not another
    view of the answer on screen -- and, like a direction, it asks nothing.
    """
    bar = bar_with_a_school
    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.answers(_an_answer())
    asked = len(bar._controller.asked)

    box = getattr(bar, box_name)
    index = box.findData(choice)
    box.setCurrentIndex(index)
    box.activated.emit(index)

    assert box.currentData() == choice
    assert bar.answer is None
    assert bar.situation.state is advisorbar.State.NOTHING_YET
    assert len(bar._controller.asked) == asked


def test_both_choices_survive_a_restart(qapp):
    """AK-347's Pruefweg, first half: a row built after an earlier one chose
    `Bestial` x `Fire` opens on both, not on `Weapon` x `All` -- the pair a
    session ended on is what the next one starts with."""
    first = advisorbar.AdvisorBar(lambda goal_id: _an_asking(),
                                  controller=_Controller(), data=ONE_SCHOOL)
    try:
        for box, choice in ((first.hit_with_box, "family:23"),
                            (first.damage_type_box, "Fire")):
            index = box.findData(choice)
            box.setCurrentIndex(index)
            box.activated.emit(index)
    finally:
        first.deleteLater()

    second = advisorbar.AdvisorBar(lambda goal_id: _an_asking(),
                                   controller=_Controller(), data=ONE_SCHOOL)
    try:
        assert (second.hit_with(), second.damage_type()) == ("family:23",
                                                             "Fire")
        assert second.hit_with_box.currentText() == "Bestial"
    finally:
        second.deleteLater()


def test_a_remembered_school_the_dataset_lost_falls_back_on_its_own(qapp):
    """AK-347's Pruefweg, second half: each key is checked against its own
    box.

    A school remembered from a dataset that no longer carries it (a patch,
    or a hand-edited settings file) is not offered as if it still meant
    something -- `findData` misses it and `hit_with_box` opens on `Weapon`.
    The other key is untouched by that, so `damage_type_box` still opens on
    `Fire`: two keys, two checks, and one falling back moves nothing else.
    """
    first = advisorbar.AdvisorBar(lambda goal_id: _an_asking(),
                                  controller=_Controller(), data=ONE_SCHOOL)
    try:
        for box, choice in ((first.hit_with_box, "family:23"),
                            (first.damage_type_box, "Fire")):
            index = box.findData(choice)
            box.setCurrentIndex(index)
            box.activated.emit(index)
    finally:
        first.deleteLater()

    second = advisorbar.AdvisorBar(lambda goal_id: _an_asking(),
                                   controller=_Controller())
    try:
        assert second.hit_with() == ""
        assert second.hit_with_box.currentText() == "Weapon"
        assert second.damage_type() == "Fire"
    finally:
        second.deleteLater()


def test_an_old_single_key_from_before_the_two_fields_is_ignored(qapp):
    """AK-347/AD-051.5: `damage_art` is not translated, it is ignored.

    The value it held (`type:Fire`, `art:family:23`) names no entry of
    either box, so a store still carrying it opens the row on `Weapon` x
    `All` -- and nothing in this file knows how to read it.
    """
    settings = QSettings(favourites.ORG, favourites.APP)
    settings.setValue("damage_art", "type:Fire")
    try:
        widget = advisorbar.AdvisorBar(lambda goal_id: _an_asking(),
                                       controller=_Controller(),
                                       data=ONE_SCHOOL)
        try:
            assert (widget.hit_with(), widget.damage_type()) == ("", "")
        finally:
            widget.deleteLater()
    finally:
        settings.remove("damage_art")


def test_the_three_tooltips_are_the_three_the_spec_writes(bar):
    """AK-340/AK-351, word for word out of `UI_SPEC.md`: one tooltip per
    box, and the one on `hit_with_box` is what keeps a Nightfarer's own
    skill apart from a Weapon Art and a found spell apart from the one this
    equipment casts. `goal_box` has no label beside it, unlike the two that
    follow it, so its own tooltip is what a reader has once its text no
    longer fits at the derived opening width (AK-350/AK-351)."""
    assert bar.goal_box.toolTip() == (
        "Chooses what the Advisor ranks your build for.")
    assert bar.hit_with_box.toolTip() == (
        "Chooses what the figure ranks: the starting armament, its Weapon "
        "Art, or the spell the starting catalyst throws. Weapon art counts "
        "Weapon Arts only — a Nightfarer's own skills are never counted. "
        "Sorceries, Incantations and a school rank the one spell this "
        "Nightfarer's own equipment casts, not a spell found in the run.")
    assert bar.damage_type_box.toolTip() == (
        "Restricts Maximise damage to one kind of damage.")


def test_the_chosen_kind_of_damage_stands_in_both_halves_of_the_question(
        planner):
    """AD-051: `hit_with` and `damage_type` are fields of the question, so
    they reach the key and the context together -- filled in one of them
    only, the run refuses the question it is handed
    (`run._refuse_a_request_that_asks_about_another_run`, the same guard
    `two_handed` answers to).

    Each box answers its own field since AK-337, so the case sets the pair
    the row would be standing on and reads it back out of both halves.

    Red with either assignment in `asking_from` taken out.
    """
    from nrplanner.advisor import run as advisor_run

    bar = planner.advisor_bar
    for hit_with, damage_type in (("", ""), ("", "Magic"),
                                  ("incantations", ""),
                                  ("incantations", "Magic")):
        bar.hit_with_box.setCurrentIndex(bar.hit_with_box.findData(hit_with))
        bar.damage_type_box.setCurrentIndex(
            bar.damage_type_box.findData(damage_type))
        asking = advisorbar.asking_from(planner, "max_damage")
        assert (asking.request.hit_with, asking.request.damage_type) == (
            hit_with, damage_type)
        assert (asking.ctx.hit_with, asking.ctx.damage_type) == (
            hit_with, damage_type)
        # The fingerprint is the worker's to fill (`AdvisorController.ask`),
        # and the guard checks it too -- so the case fills it the same way
        # rather than asserting around it.
        frozen = advisor_run.frozen_inventory(asking.inventory,
                                              asking.request.problem)
        advisor_run._refuse_a_request_that_asks_about_another_run(
            dataclasses.replace(asking.request,
                                inventory_fingerprint=advisor_run.
                                inventory_fingerprint(frozen)),
            frozen, asking.ctx)


def test_a_declared_condition_outlives_the_baseline(planner):
    """AD-036.6: the baseline is a default for a condition, never a value.

    An effect the baseline would set to 1 is declared at 3 by the player;
    the run carries the declaration as the player made it, in the context
    and in the key, and every other switchable condition at the baseline.
    """
    from nrplanner import model

    effect = min(model.advisor_defaults())
    planner.declared = {effect: 3}

    asking = advisorbar.asking_from(planner, "max_damage")
    declared = dict(asking.ctx.declared)
    assert declared[effect] == 3, "the baseline overwrote what the player declared"
    assert asking.request.declared == asking.ctx.declared
    assert declared.keys() >= set(model.advisor_defaults())


def test_the_marked_sets_reach_the_problem_the_window_asks(planner):
    """AD-036.5: `asking_from` carries both sets on the `SlotProblem`, so
    they are in the cache key and in every evaluation without a second
    field anywhere (AD-036.1)."""
    from nrplanner import effectfilters

    filters = planner.effect_filters
    family = filters.families[7330000]
    members = {i for i, key in filters.families.items() if key == family}
    filters.mark(11, effectfilters.EXCLUDED)
    filters.mark(22, effectfilters.REQUIRED)
    filters.mark_family(family, True)
    filters.mark(7330000, effectfilters.ALLOWED)
    try:
        problem = advisorbar.asking_from(planner, "max_damage").request.problem
        # AD-039.3: the avoided family, less the member on Allow.
        assert problem.excluded == {11} | members - {7330000}
        assert 7080000 in problem.excluded and len(members) > 2
        assert problem.required == {22}
    finally:
        filters.mark_family(family, False)
        for effect_id in (11, 22, 7330000):
            filters.mark(effect_id, None)


def test_the_question_carries_the_starting_armament_without_its_rolls(planner):
    """AD-038.1: the damage direction ranks against the Nightfarer's own
    starting armament, at its lowest tier, in the starting slot -- and
    against nothing the player carries: no grid, no rolls (A17, QA-226).
    The id stands in the key beside it, or `run.run` refuses the question.

    Red with `reference=None` put back into `asking_from`.
    """
    from nrplanner import damage, weapons

    hero = planner.current_hero()
    asking = advisorbar.asking_from(planner, "max_damage")

    reference = asking.ctx.reference
    assert reference.weapon["id"] == hero["starting_weapon"]
    assert reference.tier == weapons.MIN_UPGRADE
    assert reference.slot_index == damage.STARTING_SLOT
    assert asking.request.reference_weapon_id == hero["starting_weapon"]
    assert asking.ctx.weapons_held == ()
    assert asking.ctx.armament_effect_ids == ()


def test_without_a_record_of_the_starting_armament_the_run_ranks_without_one(
        planner, monkeypatch):
    """AD-038.1, the fallback: a dataset with no record for the starting
    armament leaves `reference` empty in the context **and** in the key,
    and the run takes the multiplier mean and says so (`_NO_ARMAMENT`)."""
    monkeypatch.setattr(planner, "weapon_by_id", lambda weapon_id: None)

    asking = advisorbar.asking_from(planner, "max_damage")

    assert asking.ctx.reference is None
    assert asking.request.reference_weapon_id is None


def test_a_marking_reaches_the_row_as_a_marking(planner, monkeypatch):
    """The window wires `EffectFilters.changed` to the row with the AK-289
    cause -- the path a direction change takes (AK-183), no run started."""
    from nrplanner import effectfilters

    heard = []
    monkeypatch.setattr(planner.advisor_bar, "the_build_changed",
                        lambda **kwargs: heard.append(kwargs))
    planner.effect_filters.mark(11, effectfilters.REQUIRED)
    planner.effect_filters.mark(11, None)
    assert heard == [{"marking_changed": True}] * 2


def test_the_filters_tooltip_counts_the_marked_effects_in_every_state(qapp):
    """AK-280 on the `Filters` button (AK-302, AK-300 words): the count is a
    standing setting, so it stands in 4.1 and 4.8 as much as behind an
    answer, only where a set is not empty -- and no longer on the row."""
    from nrplanner import effectfilters

    filters = effectfilters.EffectFilters()
    asking = {"value": _an_asking()}
    widget = advisorbar.AdvisorBar(lambda goal_id: asking["value"],
                                   controller=_Controller(), filters=filters)
    try:
        assert widget.toolTip() == "<span>Nothing suggested yet.</span>"
        assert widget.filters_button.toolTip() == (
            f"<span>{advisorbar.FILTERS_TOOLTIP}</span>")
        filters.mark(11, effectfilters.EXCLUDED)
        filters.mark(12, effectfilters.EXCLUDED)
        filters.mark(13, effectfilters.REQUIRED)
        widget.the_build_changed(marking_changed=True)
        assert widget.toolTip() == "<span>Nothing suggested yet.</span>"
        assert widget.filters_button.toolTip() == (
            f"<span>{advisorbar.FILTERS_TOOLTIP}  ·  2 effects avoided  ·  "
            "1 effect favourited</span>")
        # AK-316.5: families are a clause of their own, never added to the ids.
        filters.mark_family("Dexterity", True)
        widget.the_build_changed(marking_changed=True)
        assert widget.filters_button.toolTip().endswith(
            "2 effects avoided  ·  1 effect favourited  ·  "
            "1 family avoided</span>")
        filters.mark_family("Dexterity", False)
        asking["value"] = None
        widget.the_build_changed()
        assert widget.toolTip().endswith("use Rescan save.</span>")
        assert widget.filters_button.toolTip().endswith(
            "2 effects avoided  ·  1 effect favourited</span>")
        assert advisorbar.marking_clauses(None) == []
    finally:
        for effect_id in (11, 12, 13):
            filters.mark(effect_id, None)
        widget.deleteLater()


def test_the_filters_button_stands_live_in_every_state(bar):
    """AK-302: outside AK-07's budget, so it is neither hidden nor disabled
    by any of the fourteen states -- not by 4.8, not by a run in flight."""
    heard = []
    bar.filters_requested.connect(lambda: heard.append(True))
    assert bar.filters_button.text() == "Filters"
    bar.asking["value"] = None
    bar.the_build_changed()
    assert bar.situation.state is advisorbar.State.NO_SAVE
    assert not bar.filters_button.isHidden()
    assert bar.filters_button.isEnabled()
    bar.asking["value"] = _an_asking()
    bar.the_build_changed()
    bar.optimize_button.click()
    bar._controller.begins()
    _wait(advisorbar.WAIT_VISIBLE_MS + 50)
    assert bar.situation.state in advisorbar.WORKING_STATES
    assert bar.filters_button.isEnabled()
    bar.filters_button.click()
    assert heard == [True]


def test_the_filters_button_opens_the_window_over_what_is_owned(planner,
                                                                 monkeypatch):
    """The window wires `filters_requested` to the dialog, handing it one row
    per owned id (AK-304) and the store the row already reads (AK-311)."""
    from nrplanner import effectfilterdialog

    opened = []
    monkeypatch.setattr(effectfilterdialog.EffectFilterWindow, "exec",
                        lambda self: opened.append(self))
    planner.advisor_bar.filters_button.click()
    assert len(opened) == 1
    window = opened[0]
    assert window._filters is planner.effect_filters
    assert len(window.shown_ids()) == len(
        effectfilterdialog.rows_from(planner.owned, planner.effects,
                                     planner.effect_filters.families)) > 0
    assert window.empty.isHidden()
    # AK-309's first two cases, told apart as the relic label tells them.
    monkeypatch.setattr(planner, "owned", None)
    planner.open_effect_filters()
    assert opened[-1].empty.text() == effectfilterdialog.NO_SAVE_WAS_READ
    monkeypatch.setattr(planner, "_answers_a_chosen_save", True)
    planner.open_effect_filters()
    assert opened[-1].empty.text() == effectfilterdialog.SAVE_HAS_NO_RELICS


def test_the_row_stops_the_search_before_the_data_under_it_changes(bar):
    """AD-006.7, and the window is what calls it -- see the window cases."""
    bar.the_data_is_changing()
    assert bar._controller.data_changes == 1


def test_closing_shuts_the_thread_down(bar):
    bar.shutdown()
    assert bar._controller.shutdowns == 1


# --- the row in the real window --------------------------------------------

def _the_middle_column(window):
    return window.panes.widget(1)


def _the_slot_area(window) -> QScrollArea:
    return _the_middle_column(window).findChild(QScrollArea)


def test_the_row_stands_between_the_build_line_and_the_hint(planner):
    """AK-02, by the order of the middle column and by what is inside what."""
    column = _the_middle_column(planner)
    stack = column.layout()
    order = [stack.itemAt(i).widget() for i in range(stack.count())]
    area = _the_slot_area(planner)
    assert order.index(planner.advisor_bar) == order.index(area) - 1
    # The build list is above the row and outside the area; the hint is
    # below it and inside.
    assert planner.build_box not in area.findChildren(type(planner.build_box))
    hints = [label for label in area.widget().findChildren(QLabel)
             if label.text().startswith("Open a slot to choose a relic")]
    assert len(hints) == 1


def test_the_row_does_not_scroll_away_with_the_slots(planner):
    """AK-02's second half: a run being waited for stays on screen.

    Short on purpose: at the opening height the six slots fit and there is
    nothing to scroll, so a case at that size would agree whatever the row
    was in (measured -- the scrollbar's maximum is 0 at 1320 x 900).
    """
    planner.resize(1320, 560)
    planner.show()
    rendered.settle()
    try:
        area = _the_slot_area(planner)
        before = planner.advisor_bar.mapTo(planner, planner.advisor_bar.rect().topLeft())
        assert area.verticalScrollBar().maximum() > 0, (
            "nothing to scroll, so this case would pass either way")
        rendered.scrolled_to_bottom(area)
        after = planner.advisor_bar.mapTo(planner, planner.advisor_bar.rect().topLeft())
        assert before == after
        assert area.verticalScrollBar().value() > 0
    finally:
        planner.close()


def test_the_row_asks_the_window_for_no_width_at_all(planner):
    """AK-03, at the place the criterion is really about.

    The window's own floor is a figure of the tab beside this one and of the
    style; what this change may not do is make the middle column insist on
    more room than the scrolling part of it did. Everything outside a scroll
    area is a pixel on the window's floor, and the two blocks this task put
    there ask for none.
    """
    column = _the_middle_column(planner)
    area = _the_slot_area(planner)
    assert column.minimumSizeHint().width() <= area.minimumSizeHint().width()
    assert (planner.advisor_bar.minimumSizeHint().width()
            > area.minimumSizeHint().width()), (
        "the row is wider than the area's floor, so this case would pass "
        "whatever the size policies said")


def test_the_row_keeps_the_vertical_budget(planner):
    """AK-04/§3.1: at most 32 px of content, plus 6 px above and below."""
    assert planner.advisor_bar.sizeHint().height() <= 44


def test_at_the_opening_width_only_the_status_is_shortened(
        advisor_row_at_the_window):
    """AK-05 at the derived opening width (A14), measured at the window.

    4.12 is long, so the status is the one thing shortened -- to `…`, with
    the whole sentence in its tooltip -- and no caption of the row is cut.
    The figures come from a window under the Windows platform, not from
    the offscreen one and not from a `1320` written here (T-226, A31).
    """
    figures = advisor_row_at_the_window
    assert figures["width"] == figures["opening_width"]
    row = figures["failed"]
    assert row["cut"] == []
    assert row["status_text"] != row["status_whole_text"]
    assert row["status_text"].endswith("…")
    assert html.escape(row["status_whole_text"]) in row["status_tooltip"]


def test_at_the_opening_width_the_status_keeps_some_width(
        advisor_row_at_the_window):
    """AK-194: the status is never 0 px at the width the window opens at.

    Measured 67 px on 2026-09-13 (T-225; Fusion, Segoe UI 9 pt, ratio
    1.25, window 1 350 px, row 498). The figure is not written here: the
    criterion is `> 0`, and the environment is what decides the rest.
    """
    assert advisor_row_at_the_window["failed"]["status_width"] > 0


@pytest.mark.parametrize("room", [str(room) for room in NARROW_DESKTOPS])
def test_on_a_narrow_desktop_the_row_keeps_every_control_and_carries_the_status(
        advisor_row_at_the_window, room):
    """AK-05 on a desktop that caps the opening width (QA-250).

    Decided 2026-09-13: the boxes come first and the status may go, down
    to 0 px -- so AK-194's `> 0` is not asked here, and a status too narrow
    to hover has its sentence in the row's own tooltip instead.

    Option B (user decision 2026-09-19): AK-05 itself only holds at 1676 px
    and up, above both desktops of `NARROW_DESKTOPS` -- below that floor
    `goal_box` and `damage_type_box` may give way to eliding, and neither
    desktop's width is asked to keep any caption whole. What stays is
    usability, not full captions: every control this task's rows started
    with is still on screen, and the tooltip carries the status text
    whether or not the boxes gave way too.
    """
    at_room = advisor_row_at_the_window["rooms"][room]
    assert at_room["width"] < advisor_row_at_the_window["width"], (
        "this desktop does not cap the opening width, so the case would "
        "measure the same row twice")
    for state in ("failed", "suggested"):
        base = advisor_row_at_the_window[state]
        row = at_room[state]
        assert set(row["on_screen"]) == set(base["on_screen"]), (
            "a control left the row on this desktop, not just its caption")
        assert html.escape(row["status_whole_text"]) in row["row_tooltip"]


def _spin_until(predicate, timeout: float = A_RUN_AT_MOST) -> bool:
    app = QApplication.instance()
    deadline = time.monotonic() + timeout
    while not predicate() and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.005)
    return predicate()


def _slot_state(planner) -> list:
    return [(slot.relic_box.currentIndex(), slot.relic_box.currentText())
            for slot in planner.active_slots()]


def test_a_real_optimize_answers_and_changes_no_slot(planner):
    """AK-13 and AK-08, through the real controller and the real search.

    This is the case that shows the window builds a request the run accepts:
    a field that did not describe the run beside it would come back as 4.12,
    and `run.run` refuses such a request by name.
    """
    bar = planner.advisor_bar
    before = _slot_state(planner)
    sheet = planner._build

    began_running = []
    bar._controller.started.connect(lambda: began_running.append(True))
    bar.optimize_button.click()
    assert _spin_until(lambda: bool(began_running)), "the run never started"
    assert bar.situation.state in advisorbar.WORKING_STATES
    # AK-08: while it runs, nothing outside this row is turned off, no modal
    # dialog is up and no wait cursor is over the window.
    assert planner.chalice_list.isEnabled()
    assert all(slot.isEnabled() for slot in planner.active_slots())
    assert planner.level_slider.isEnabled()
    assert QApplication.activeModalWidget() is None
    assert QApplication.overrideCursor() is None

    assert _spin_until(lambda: bar.situation.state not in
                       advisorbar.WORKING_STATES), "the run never finished"
    assert bar.situation.state in advisorbar.ANSWERED_STATES, (
        f"the run ended in {bar.situation.state} saying "
        f"{bar.status.accessibleName()!r}")
    assert _slot_state(planner) == before
    assert planner._build is sheet
    bar.shutdown()


def test_cancel_is_visible_within_the_two_hundred_milliseconds(planner):
    """AK-11, measured against the real controller.

    The worker is not waited for: the whole point of the figure is that the
    row says `Stopped` while the search is still on its way out.
    """
    bar = planner.advisor_bar
    began_running = []
    bar._controller.started.connect(lambda: began_running.append(True))
    bar.optimize_button.click()
    assert _spin_until(lambda: bool(began_running)), "the run never started"

    began = time.perf_counter()
    bar.optimize_button.click()
    elapsed_ms = (time.perf_counter() - began) * 1000
    assert bar.situation.state is advisorbar.State.STOPPED
    assert elapsed_ms < 200, f"{elapsed_ms:.1f} ms to reach 4.5"
    bar.shutdown()




def test_a_change_of_the_level_reaches_the_advisor(planner, monkeypatch):
    """AK-12's other end: `recompute` is where the window says what changed.

    Driven from a control a player uses rather than by calling `recompute`,
    because what is asserted is that the one funnel every change ends in
    tells the advisor -- not that a method calls the method beside it.
    """
    told = []
    monkeypatch.setattr(planner.advisor_bar, "the_build_changed",
                        lambda: told.append(True))
    planner.level_slider.setValue(planner.level_slider.value() + 1)
    assert told


def test_rescanning_the_save_stops_the_search_before_the_relics_change(
        planner, monkeypatch):
    """AD-006.7 at its first call site, and in the right order.

    What the window still held at the moment it said so is recorded: a call
    moved below the read would hand the advisor the new inventory to forget.

    Since T-142 the read is in a thread and the moment is the **arrival**, not
    the asking (AD-029 point 3): while the read is out, every answer in the
    cache is still about the stock on screen and is still right. The order
    this case is about is unchanged and is the only thing it asserts -- said
    before `self.owned` is replaced, and about the inventory being replaced.
    """
    from tests import conftest

    real = planner.advisor_bar.the_data_is_changing
    held = []

    def spy():
        held.append(planner.owned)
        real()

    monkeypatch.setattr(planner.advisor_bar, "the_data_is_changing", spy)
    before = planner.owned
    planner.rescan_save()
    assert held == [], "nothing on screen is out of date while the read is out"
    conftest.wait_for_the_save(planner)
    assert len(held) == 1
    assert held[0] is before


def test_importing_the_equipped_build_stops_the_search_first(planner,
                                                             monkeypatch):
    """AD-006.7 at its second call site: every chalice is about to be
    written."""
    told = []
    monkeypatch.setattr(planner.advisor_bar, "the_data_is_changing",
                        lambda: told.append(True))
    planner.load_equipped()
    assert told


def test_closing_the_window_waits_for_the_thread(planner, monkeypatch):
    """A `QThread` that outlives its window ends the process, not the run."""
    told = []
    monkeypatch.setattr(planner.advisor_bar, "shutdown",
                        lambda: told.append(True))
    planner.close()
    assert told
