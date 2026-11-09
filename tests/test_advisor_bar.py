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

from nrplanner import advisorbar, effecttext, favourites, relicpicker
from nrplanner.advisor import goals, types
from nrplanner.advisor import run as advisor_run
from nrplanner.advisor.evaluate import evaluate
from tests import advisor_cases as advisor
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
    ("4.8a", advisorbar.Situation(advisorbar.State.NO_SAVE),
     "No save was read, so there are no relics to choose from — use Find my "
     "save."),
    ("4.8b", advisorbar.Situation(advisorbar.State.NO_SAVE,
                                  save_is_empty=True),
     "Your save has no relics in it yet — if you just played, use Rescan "
     "save; if they are on another Steam account, use Find my save."),
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
        slots_without_a_choice=1,
        empty_slots=(types.EmptySlot(3, types.EMPTY_NOTHING),)),
     "Maximise damage — 3 of 4 slots filled  ·  1 slot empty: nothing left to "
     "choose from."),
    ("4.11 two of one reason (AK-443)", advisorbar.Situation(
        advisorbar.State.SUGGESTED_WITH_AN_EMPTY_SLOT,
        goal_label="Maximise damage", slots=4, slots_filled=2,
        slots_without_a_choice=2,
        empty_slots=(types.EmptySlot(2, types.EMPTY_AVOIDED),
                     types.EmptySlot(3, types.EMPTY_AVOIDED))),
     "Maximise damage — 2 of 4 slots filled  ·  2 slots empty: everything "
     "left carries an effect you avoided."),
    ("4.11 two reasons (AK-443)", advisorbar.Situation(
        advisorbar.State.SUGGESTED_WITH_AN_EMPTY_SLOT,
        goal_label="Maximise damage", slots=4, slots_filled=2,
        slots_without_a_choice=2,
        empty_slots=(types.EmptySlot(2, types.EMPTY_AVOIDED),
                     types.EmptySlot(3, types.EMPTY_REJECTED))),
     "Maximise damage — 2 of 4 slots filled  ·  2 slots empty for different "
     "reasons — see the slot cards."),
    *[(f"4.11 {reason} (AK-457)", advisorbar.Situation(
        advisorbar.State.SUGGESTED_WITH_AN_EMPTY_SLOT,
        goal_label="Maximise damage", slots=1, slots_filled=0,
        slots_without_a_choice=1,
        empty_slots=(types.EmptySlot(0, reason, relic_name="Urn"),)),
       f"Maximise damage — 0 of 1 slots filled  ·  1 slot empty: {short}.")
      for reason, short in (
          (types.EMPTY_REQUIREMENT,
           "what is left is needed for your Favourite effects"),
          (types.EMPTY_PIN, "your favourite “Urn” uses the rest"),
          (types.EMPTY_AVOIDED_AND_REJECTED,
           "everything left is rejected or carries an avoided effect"),
          (types.EMPTY_REJECTED, "everything left is rejected"))],
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

    def ask(self, request, inventory, ctx, debounce_ms=None) -> int:
        self.asked.append(request)
        self.debounce_ms = debounce_ms
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
               held: int = 0, empty: tuple = ()) -> types.AdvisorResult:
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
        held=held_slots, empty_slots=empty)


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
        "Find my save.")
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
    bar._controller.answers(_an_answer(filled=5, empty=(types.EmptySlot(5, types.EMPTY_NOTHING),)))
    assert bar.status.accessibleName() == (
        "Maximise damage — 5 of 6 slots filled  ·  1 slot empty: nothing left to choose from.")


def test_nothing_owned_reaching_the_choice_is_a_yellow_line_under_the_row(
        bar):
    """T-335a (user decision 28.10.2026): the run's whole sentence, `⚠ `
    first, in the theme's yellow, under the row; the status line keeps its
    clause and its tooltip, and the next state takes the line away."""
    assert bar.warning.isHidden()
    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.answers(dataclasses.replace(
        _an_answer(filled=0), suggestions=(), no_carrier_for="fire damage"))

    assert not bar.warning.isHidden()
    assert bar.warning.text() == (
        "⚠ Nothing you own reaches fire damage here: the armament it is "
        "ranked on does not carry it — for a spell the staff or seal on the "
        "selected tile, for a weapon art the armament on it, and the starting "
        "one where the tile has none; otherwise the starting "
        "armament — and nothing in your inventory swaps in a spell or weapon "
        "art that does.")
    assert advisorbar.WARNING_COLOUR in bar.warning.styleSheet()
    assert bar.warning.wordWrap()
    assert bar.status.accessibleName().endswith(
        "nothing you own reaches fire damage here.")
    assert "nothing you own reaches fire damage here" in bar.toolTip()
    layout = bar.layout()
    assert layout.indexOf(bar.warning) == layout.count() - 1

    bar.clear()
    assert bar.warning.isHidden()


def test_an_empty_slot_for_another_cause_shows_no_warning_line(bar):
    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.answers(_an_answer(filled=5))

    assert bar.warning.isHidden()
    assert bar.warning.text() == ""


def test_a_held_slot_does_not_count_as_nothing_to_choose_from(bar):
    """QA-284: a held slot is a boundary condition the search never looked
    at (AD-014.2), not a pool it searched and found empty -- one held slot
    plus one genuinely empty one must say only the empty one has nothing to
    choose from."""
    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.answers(_an_answer(
        filled=4, held=1,
        empty=(types.EmptySlot(5, types.EMPTY_NOTHING),)))
    assert bar.status.accessibleName() == (
        "Maximise damage — 5 of 6 slots filled  ·  1 slot empty: nothing "
        "left to choose from.")


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
                                                    bar.damage_type_box,
                                                    bar.incoming_box]


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
        "Art, or the spell of the staff or seal on the selected tile (or "
        "else the starting one). Weapon art counts Weapon Arts only — a "
        "Nightfarer's own skills are never counted. Sorceries, Incantations "
        "and a school rank the one spell that staff or seal casts, not a "
        "spell found in the run.")
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


def test_the_selected_staff_reaches_the_key_and_the_context(planner):
    """T-335b: the spell cells cast from the selected tile's staff, so its id
    is in the key beside the context that reads it, and a tile without one
    puts neither there. Red with either assignment in `asking_from` taken
    out (`run._refuse_a_request_that_asks_about_another_run`)."""
    from nrplanner import weaponslots
    from nrplanner.advisor import run as advisor_run

    staff = planner.weapon_by_id(33200000)
    for weapon, expected in ((staff, staff["id"]), (None, None)):
        planner.weapon_slots = [weaponslots.WeaponSlot(weapon=weapon)] + [
            weaponslots.WeaponSlot()
            for _ in range(weaponslots.SLOT_COUNT - 1)]
        planner.active_weapon = 0
        asking = advisorbar.asking_from(planner, "max_damage")
        assert asking.request.selected_catalyst_id == expected
        assert (asking.ctx.selected_catalyst or {}).get("id") == expected
        frozen = advisor_run.frozen_inventory(asking.inventory,
                                              asking.request.problem)
        request = dataclasses.replace(
            asking.request, inventory_fingerprint=advisor_run.
            inventory_fingerprint(frozen))
        advisor_run._refuse_a_request_that_asks_about_another_run(
            request, frozen, asking.ctx)
        with pytest.raises(ValueError, match="selected_catalyst_id"):
            advisor_run._refuse_a_request_that_asks_about_another_run(
                dataclasses.replace(request, selected_catalyst_id=-1),
                frozen, asking.ctx)


def test_the_chosen_spell_reaches_the_key_only_under_a_spell_row(
        planner, monkeypatch):
    """AK-415: the tile's spell is in key and context under Sorceries, and
    nowhere where it moves no answer."""
    from nrplanner import model, weaponslots

    staff = planner.weapon_by_id(33200000)
    planner.weapon_slots = [weaponslots.WeaponSlot(weapon=staff, spell_id=4070)
                            ] + [weaponslots.WeaponSlot()
                                 for _ in range(weaponslots.SLOT_COUNT - 1)]
    planner.active_weapon = 0
    for hit_with, expected in ((model.SORCERIES_ART, 4070), ("", None)):
        monkeypatch.setattr(planner.advisor_bar, "hit_with",
                            lambda chosen=hit_with: chosen)
        asking = advisorbar.asking_from(planner, "max_damage")
        assert asking.request.selected_spell_id == expected
        assert asking.ctx.selected_spell_id == expected


def test_the_fallback_catalyst_casts_the_spell_chosen_on_its_tile(
        planner, game_data, monkeypatch):
    """Director, 31.10.2026 (T-335qa): Recluse with Arc chosen on her staff
    and a greatsword selected -- the spell row falls back to her staff and
    casts Arc, not Pebble."""
    from nrplanner import model, weaponslots
    from tests import weapon_damage_cases as cases

    recluse = cases.hero_by_name(game_data, "Recluse")
    planner.hero_index = planner.heroes.index(recluse)
    staff = planner.weapon_by_id(recluse["starting_weapon"])
    sword = planner.weapon_by_id(2000800)
    planner.weapon_slots = [
        weaponslots.WeaponSlot(weapon=staff, spell_id=4070),
        weaponslots.WeaponSlot(weapon=sword)] + [
        weaponslots.WeaponSlot() for _ in range(weaponslots.SLOT_COUNT - 2)]
    planner.active_weapon = 1
    monkeypatch.setattr(planner.advisor_bar, "hit_with",
                        lambda: model.SORCERIES_ART)

    asking = advisorbar.asking_from(planner, "max_damage")

    assert asking.request.selected_catalyst_id is None
    assert asking.request.selected_spell_id == 4070
    assert asking.ctx.selected_spell_id == 4070


def test_the_selected_tile_reaches_the_key_only_under_weapon_art(
        planner, monkeypatch):
    """User decision 31.10. 13:50: under `Weapon art` the selected tile --
    armament, tier, art pick, slot -- is in key and context; elsewhere it is
    in neither. Red with the key half taken out of `asking_from`."""
    from nrplanner import model, weaponslots
    from nrplanner.advisor import run as advisor_run

    sword = planner.weapon_by_id(2000800)
    planner.weapon_slots = [weaponslots.WeaponSlot()] + [
        weaponslots.WeaponSlot(weapon=sword, tier=3, art_id=200)] + [
        weaponslots.WeaponSlot() for _ in range(weaponslots.SLOT_COUNT - 2)]
    planner.active_weapon = 1
    for hit_with, expected in ((model.SKILL_ART, (2000800, 3, 200, 1)),
                               ("", None)):
        monkeypatch.setattr(planner.advisor_bar, "hit_with",
                            lambda chosen=hit_with: chosen)
        asking = advisorbar.asking_from(planner, "max_damage")
        assert asking.request.art_tile == expected
        assert (None if asking.ctx.art_tile is None
                else asking.ctx.art_tile.key) == expected
    frozen = advisor_run.frozen_inventory(asking.inventory,
                                          asking.request.problem)
    with pytest.raises(ValueError, match="art_tile"):
        advisor_run._refuse_a_request_that_asks_about_another_run(
            dataclasses.replace(
                asking.request, art_tile=(2000800, 3, 200, 1),
                inventory_fingerprint=advisor_run.inventory_fingerprint(
                    frozen)),
            frozen, asking.ctx)


def test_held_swap_relics_are_read_without_a_calculation():
    """AD-056.7: the art ids of the held relics' swap effects, nothing else
    -- a slot held empty, an effect without the field, an unknown id."""
    effects = {"1": {"modifiers": {"startSwordArtsId": 217}},
               "2": {"modifiers": {"startSwordArtsId": 200}},
               "3": {"modifiers": {}}}
    held = (types.HeldSlot(index=0),
            types.HeldSlot(index=1, relic=types.HeldRelic(
                relic_id=1, name="a", effect_ids=(2, 3, 9))),
            types.HeldSlot(index=2, relic=types.HeldRelic(
                relic_id=2, name="b", effect_ids=(1, 2))))

    assert advisorbar.held_swapped_art_ids(held, effects) == (200, 217)


def test_a_declared_condition_outlives_the_baseline(planner):
    """AD-036.6: the baseline is a default for a condition, never a value.

    An effect the baseline would set to 1 is declared at 3 by the player;
    the run carries the declaration as the player made it, in the context
    and in the key, and every other switchable condition at the baseline --
    the armament-count ones apart from `declared`, because only one armament
    type of them may hold in a build (QA-299).
    """
    from nrplanner import effecttext, model

    effect = min(model.advisor_defaults())
    planner.declared = {effect: 3}

    asking = advisorbar.asking_from(planner, "max_damage")
    declared = dict(asking.ctx.declared)
    assert declared[effect] == 3, "the baseline overwrote what the player declared"
    assert asking.request.declared == asking.ctx.declared
    assumed = set(asking.ctx.assumed_armament_counts)
    assert assumed and not assumed & declared.keys()
    # Of the armament-count ones only the selected tile's type is assumed
    # (28.10.2026): `tests/test_one_armament_count_type.py`.
    counts = {effect_id for effect_id in model.advisor_defaults()
              if effecttext.counts_armaments(
                  planner.data["effects"][str(effect_id)])}
    assert assumed <= counts
    # The weapon-type buffs follow the selected tile's type (01.11.2026):
    # `tests/test_one_armament_count_type.py`.
    weapon_type = {effect_id for effect_id in model.advisor_defaults()
                   if "triggerOnWepType" in planner.data["effects"][
                       str(effect_id)]["modifiers"]}
    # So do the enemy-ailment conditions the grid does not inflict
    # (01.11.2026): `tests/test_ailment_conditions.py`.
    awaiting = set(asking.ctx.awaiting_ailment)
    assert not awaiting & declared.keys()
    assert declared.keys() | counts | weapon_type | awaiting >= set(
        model.advisor_defaults())


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


def _answer_of_the_window(planner):
    """The real run on what the window asks, fingerprint filled as
    `AdvisorController.ask` fills it."""
    from nrplanner.advisor import run as advisor_run

    asking = advisorbar.asking_from(planner, "max_damage")
    frozen = advisor_run.frozen_inventory(asking.inventory,
                                          asking.request.problem)
    return advisor_run.run(
        dataclasses.replace(asking.request,
                            inventory_fingerprint=advisor_run.
                            inventory_fingerprint(frozen)),
        frozen, asking.ctx, goals.GOALS)


def _guardian_effect_on_a_copy(planner) -> int:
    """A "[Guardian]" effect the frozen slot carries, so a requirement would
    change the answer on another Nightfarer."""
    for relic in planner.owned.relics:
        for effect_id in relic.effect_ids:
            name = planner.data["effects"].get(str(effect_id), {}).get("name", "")
            if name.startswith("[Guardian]"):
                return effect_id
    pytest.fail("no copy in the frozen slot carries a [Guardian] effect")


def _an_effect_no_copy_carries(planner, works_on_wylder: bool) -> int:
    carried = {effect_id for relic in planner.owned.relics
               for effect_id in relic.effect_ids}
    return next(int(key) for key, effect in planner.data["effects"].items()
                if int(key) not in carried and effect.get("name")
                and effecttext.works_for(effect, "Wylder") == works_on_wylder)


def _select_hero(planner, name: str) -> None:
    planner.select_hero(next(index for index, hero in enumerate(planner.heroes)
                             if hero["name"] == name))


def test_a_favourite_of_another_nightfarer_changes_no_answer(planner):
    """User decision 07.11.2026: a "[Guardian]" favourite on Wylder takes no
    slot and costs no figure. The mark stays. Red with the split in
    `asking_from` taken out."""
    from nrplanner import effectfilters

    _select_hero(planner, "Wylder")
    free = _answer_of_the_window(planner)
    foreign = _guardian_effect_on_a_copy(planner)
    planner.effect_filters.mark(foreign, effectfilters.REQUIRED)
    try:
        marked = _answer_of_the_window(planner)
        problem = advisorbar.asking_from(planner, "max_damage").request.problem
        assert problem.favourites_of_others == {foreign}
        assert foreign in planner.effect_filters.required
    finally:
        planner.effect_filters.mark(foreign, None)
    assert marked.suggestions[0].score == free.suggestions[0].score
    assert marked.suggestions[0].choices == free.suggestions[0].choices
    assert marked.required_left_out == ()
    assert marked.unknowns == free.unknowns


def test_the_same_favourite_binds_on_its_own_nightfarer(planner):
    """The other half of the decision: on Guardian the mark is what it was."""
    from nrplanner import effectfilters

    _select_hero(planner, "Guardian")
    own = _guardian_effect_on_a_copy(planner)
    planner.effect_filters.mark(own, effectfilters.REQUIRED)
    try:
        assert advisorbar.asking_from(
            planner, "max_damage").request.problem.required == {own}
        answer = _answer_of_the_window(planner)
    finally:
        planner.effect_filters.mark(own, None)
    assert answer.required_left_out == ()
    carriers = {relic.handle for relic in planner.owned.relics
                if own in relic.effect_ids}
    assert carriers & {choice.handle for choice in answer.suggestions[0].choices}


def test_a_favourite_of_another_nightfarer_is_not_missing_in_the_comparison(
        planner):
    """Nothing counts it as left out (AK-455, the vessel list's rank); a
    favourite of the Nightfarer's own that no copy carries still does."""
    from nrplanner import effectfilters
    from nrplanner.advisor import run as advisor_run

    _select_hero(planner, "Wylder")
    foreign = _an_effect_no_copy_carries(planner, works_on_wylder=False)
    own = _an_effect_no_copy_carries(planner, works_on_wylder=True)
    filters = planner.effect_filters
    filters.mark(own, effectfilters.REQUIRED)
    try:
        without = advisor_run.vessel_row(7, _answer_of_the_window(planner))
        filters.mark(foreign, effectfilters.REQUIRED)
        with_foreign = advisor_run.vessel_row(7, _answer_of_the_window(planner))
    finally:
        filters.mark(own, None)
        filters.mark(foreign, None)
    assert with_foreign.required_left_out == (own,)
    assert advisor_run.rank_key(with_foreign) == advisor_run.rank_key(without)


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
        assert widget.toolTip().endswith("use Find my save.</span>")
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
    assert order[order.index(planner.advisor_bar) + 1:order.index(area)] == [
        planner.rejected_list]
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


#: The row's two lines, by the names `advisor_row_at_the_window` gives the
#: controls (AK-396). The status line stands between `optimize_button` and
#: `apply_button` and is measured on its own.
FIRST_LINE = ("heading", "goal_box", "hit_with_label", "hit_with_box",
              "damage_type_label", "damage_type_box")
SECOND_LINE = ("filters_button", "optimize_button", "apply_button",
               "why_button", "clear_button")
BOXES = ("goal_box", "hit_with_box", "damage_type_box")


def _every_width(figures) -> dict:
    """The check table's widths and the window's least width, by name."""
    return {**figures["at"], "least": figures["window_minimum"]}


def _middle(rect) -> float:
    _x, y, _width, height = rect
    return y + height / 2


def _first_line_need(row) -> int:
    """What line one asks for with nothing shortened (AK-399)."""
    return (sum(row["hints"][name] for name in FIRST_LINE)
            + (len(FIRST_LINE) - 1) * advisorbar.SPACING)


def test_the_window_minimum_is_one_figure_under_1366(
        advisor_row_at_the_window):
    """AK-400, replacing AK-03: the row asks for the wider of its two lines
    at their tightest, in every direction, with and without a suggestion;
    and the window does not get narrower than that."""
    least = advisor_row_at_the_window["window_minimum"]
    assert len(set(least["window_minimums"])) == 1, least["window_minimums"]
    assert least["window_minimums"][0] <= 1366
    assert least["width"] == least["window_minimums"][0]
    first_line_floor = (sum(least["hints"][name] for name in FIRST_LINE
                            if name not in BOXES)
                        + sum(least["minimums"][name] for name in BOXES)
                        + (len(FIRST_LINE) - 1) * advisorbar.SPACING)
    # Five gaps, not four: the status line, 0 px here, is a sixth item.
    second_line_floor = (sum(least["hints"][name] for name in SECOND_LINE)
                         + len(SECOND_LINE) * advisorbar.SPACING)
    assert least["row_width"] == max(first_line_floor, second_line_floor)


def test_one_line_holds_the_status_floor_and_two_lines_start_below_it(
        advisor_row_at_the_window):
    """AK-401/AK-194: one line at the opening width, two at 1728 and 1536,
    and the status at least `STATUS_FLOOR` on one line, never 0 on two."""
    figures = advisor_row_at_the_window
    assert figures["lines"] == 1
    assert figures["failed"]["status_width"] >= advisorbar.STATUS_FLOOR
    for name, row in _every_width(figures).items():
        if row["lines"] == 2:
            assert row["status_width"] > 0, name
    assert figures["at"]["1728"]["lines"] == 2
    assert figures["at"]["1536"]["lines"] == 2


@pytest.mark.parametrize("goal_id", advisorbar.GOAL_ORDER)
def test_the_row_breaks_one_px_under_its_one_line_need(
        advisor_row_at_the_window, goal_id):
    """AK-395: two lines exactly below the need of the direction shown --
    line one as the direction shows it, every action button and
    `STATUS_FLOOR` counted on line two."""
    threshold = advisor_row_at_the_window["threshold"][goal_id]
    hints = advisor_row_at_the_window["at"]["1959"]["hints"]
    first_line = {"max_damage": FIRST_LINE,
                  "max_attributes": ("heading", "goal_box")}.get(
        goal_id, ("heading", "goal_box", "incoming_label", "incoming_box"))
    assert threshold["need"] == (
        sum(hints[name] for name in first_line + SECOND_LINE)
        + advisorbar.STATUS_FLOOR
        + (len(first_line) + len(SECOND_LINE)) * advisorbar.SPACING)
    for step, lines in (("-1", 2), ("0", 1)):
        at = threshold[step]
        assert at["row_width"] == threshold["need"] + int(step), (
            "the row was not sized where this case asks about")
        assert at["lines"] == lines, f"{step}: {at}"


def test_the_damage_question_counts_in_the_need(bar):
    """AK-395: the direction's own controls are part of the need -- the
    need of `max_damage` is wider by exactly what its two pairs ask."""
    bar.choose_goal("max_attributes")
    narrower = bar._lines.one_line_need()
    bar.choose_goal("max_damage")
    assert (bar._lines.one_line_need() - narrower
            == bar.damage_question_extra_width())


@pytest.mark.parametrize("goal_id", ["min_damage_taken", "balanced"])
def test_the_incoming_pair_takes_less_than_the_damage_question(bar, goal_id):
    """User decision 2026-11-08: `Incoming` stands where the two pairs of
    `max_damage` are hidden, and is narrower than they are, so every width
    counted on those pairs holds for it."""
    bar.choose_goal("max_attributes")
    bare = bar._lines.one_line_need()
    bar.choose_goal(goal_id)
    assert not bar.incoming_box.isHidden() and bar.hit_with_box.isHidden()
    assert 0 < (bar._lines.one_line_need() - bare
                ) <= bar.damage_question_extra_width()
    bar.choose_goal("max_damage")
    assert bar.incoming_box.isHidden() and bar.incoming_label.isHidden()


def test_the_incoming_box_offers_physical_and_the_four_elements(bar):
    box = bar.incoming_box
    entries = [(box.itemText(i), box.itemData(i)) for i in range(box.count())
               if box.itemText(i)]
    assert entries == [("Physical", ""), ("Magic", "Magic"), ("Fire", "Fire"),
                       ("Lightning", "Thunder"), ("Holy", "Dark")]
    assert bar.incoming() == ""
    box.setCurrentIndex(box.findData("Fire"))
    assert bar.incoming() == "Fire"
    assert goals.incoming_weighting(bar.incoming()).id == "physical+Fire"


@pytest.mark.parametrize("goal_id", advisorbar.GOAL_ORDER)
def test_nothing_the_row_shows_moves_it_between_its_lines(
        advisor_row_at_the_window, goal_id):
    """AK-397: a suggestion, `Undo apply`, a run, `Cancel`, 4.12 and the
    empty row, one after the other, at either side of the break."""
    threshold = advisor_row_at_the_window["threshold"][goal_id]
    for step in ("-1", "0"):
        seen = threshold[step]["through_the_states"]
        assert set(seen) == {threshold[step]["lines"]}, f"{step}: {seen}"


@pytest.mark.parametrize("goal_id", advisorbar.GOAL_ORDER)
def test_another_layout_pass_leaves_the_lines_as_they_are(
        advisor_row_at_the_window, goal_id):
    """AK-404: no circle between the line count and the width."""
    threshold = advisor_row_at_the_window["threshold"][goal_id]
    for step in ("-1", "0"):
        at = threshold[step]
        assert at["after_another_pass"] == at["lines"], step


@pytest.mark.parametrize("width", ["1536", "1959"])
def test_the_lines_keep_the_order_of_one_line(advisor_row_at_the_window,
                                              width):
    """AK-396: on two lines the question stands above the doing, 6 px
    between them, both from the same left edge; on one line everything
    stands side by side; in the same left-to-right order either way."""
    row = advisor_row_at_the_window["at"][width]
    geometry = row["geometry"]
    first = [geometry[name] for name in FIRST_LINE]
    second = [geometry[name] for name in SECOND_LINE]
    if row["lines"] == 1:
        everything = first + second
        assert len({_middle(rect) for rect in everything}) == 1
        assert [rect[0] for rect in everything] == sorted(
            rect[0] for rect in everything)
        return
    assert len({_middle(rect) for rect in first}) == 1
    assert len({_middle(rect) for rect in second}) == 1
    first_bottom = max(y + height for _x, y, _w, height in first)
    second_top = min(y for _x, y, _w, _h in second)
    assert second_top - first_bottom == advisorbar.SPACING
    assert first[0][0] == second[0][0] == 0
    for line in (first, second):
        assert [rect[0] for rect in line] == sorted(rect[0] for rect in line)


def test_no_label_or_button_is_ever_under_its_size_hint(
        advisor_row_at_the_window):
    """AK-398 at every width of the check table and at the window's least:
    never 100 -> 70 -> 57 px again (QA-292)."""
    for name, row in _every_width(advisor_row_at_the_window).items():
        for control in FIRST_LINE + SECOND_LINE:
            if control in BOXES:
                continue
            assert row["geometry"][control][2] >= row["hints"][control], (
                f"{name}: {control}")


def test_the_boxes_give_way_only_on_line_one_and_only_so_far(
        advisor_row_at_the_window):
    """AK-399, replacing AK-05/AK-269/AK-271's "the boxes may be cut":
    each box's least width is `min(floor, sizeHint)`, it is never narrower,
    and it is cut only on two lines with line one under its own need."""
    for name, row in _every_width(advisor_row_at_the_window).items():
        for box, floor in zip(BOXES, advisorbar.BOX_FLOORS):
            assert row["minimums"][box] == min(floor, row["hints"][box])
            assert row["geometry"][box][2] >= row["minimums"][box], (
                f"{name}: {box}")
        may_cut = (row["lines"] == 2
                   and row["row_width"] < _first_line_need(row))
        allowed = set(BOXES) if may_cut else set()
        assert set(row["cut"]) <= allowed, f"{name}: {row['cut']}"


def test_the_row_is_as_tall_as_its_lines_and_the_column_follows(
        advisor_row_at_the_window):
    """AK-402 and AK-04: 36 px on one line, 66 on two; nothing reaches out of
    the row; the column lays the first card right under it and its own least
    height grows by the second line."""
    rows = _every_width(advisor_row_at_the_window)
    heights = {1: 36, 2: 66}
    for name, row in rows.items():
        assert abs(row["height"] - heights[row["lines"]]) <= 1, name
        assert row["outside_the_row"] == [], name
        assert row["gap_below"] == row["column_spacing"], name
    one, two = rows["1959"], rows["1728"]
    assert (one["lines"], two["lines"]) == (1, 2)
    assert (two["column_minimum_height"] - one["column_minimum_height"]
            == two["height"] - one["height"])


def test_dragging_across_the_break_keeps_order_focus_and_names(
        advisor_row_at_the_window):
    """AK-403: the same tab chain on both sides, `Optimize` keeps the focus,
    and the accessible names (AK-380) stay."""
    sides = advisor_row_at_the_window["across_the_break"]
    one, two = sides["0"], sides["-1"]
    assert (one["lines"], two["lines"]) == (1, 2)
    assert one["tab_chain"] == two["tab_chain"] == [
        "goal_box", "hit_with_box", "damage_type_box", "filters_button",
        "optimize_button", "apply_button", "why_button", "clear_button"]
    assert one["focus_is_optimize"] and two["focus_is_optimize"]
    assert one["accessible_names"] == two["accessible_names"]


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


@pytest.mark.parametrize("room", [str(room) for room in NARROW_DESKTOPS])
def test_on_a_narrow_desktop_the_row_cuts_nothing_and_carries_the_status(
        advisor_row_at_the_window, room):
    """AK-05/AK-269/AK-271 since T-334n: the window opens at 1536 px on both
    desktops, the row on two lines with every control whole -- the boxes
    no longer give way there -- and the tooltip carries the status."""
    at_room = advisor_row_at_the_window["rooms"][room]
    assert at_room["width"] < advisor_row_at_the_window["width"], (
        "this desktop does not cap the opening width, so the case would "
        "measure the same row twice")
    assert at_room["lines"] == 2
    for state in ("failed", "suggested"):
        base = advisor_row_at_the_window[state]
        row = at_room[state]
        assert set(row["on_screen"]) == set(base["on_screen"])
        assert row["cut"] == [], f"{state}: {row['cut']}"
        assert html.escape(row["status_whole_text"]) in row["row_tooltip"]


@pytest.mark.parametrize("room", [str(room) for room in NARROW_DESKTOPS])
def test_on_a_narrow_desktop_the_warning_line_covers_nothing(
        advisor_row_at_the_window, room):
    """T-335a, QA-292/304: the warning line wraps inside the row, whole,
    and the row grows for it rather than reaching over the slots below."""
    warning = advisor_row_at_the_window["rooms"][room]["warning"]
    assert warning["shown"]
    assert warning["inside_the_row"]
    assert warning["short_by"] <= 0
    assert warning["gap_below"] >= 0
    assert warning["cut"] == []


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
    monkeypatch.setattr(planner.advisor_bar, "the_level_changed",
                        lambda: told.append(True))
    planner.level_slider.setValue(planner.level_slider.value() + 1)
    assert told


def test_a_level_with_nothing_on_screen_is_a_change_like_any_other(
        planner, monkeypatch):
    """With no suggestion there is nothing to keep (user, 2026-11-08)."""
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


# --- what the suggestion goes without (AK-455, AK-439) -----------------------

@pytest.mark.parametrize("state,extra,head", [
    (advisorbar.State.SUGGESTED, {},
     "Maximise damage — 6 of 6 slots filled"),
    (advisorbar.State.SUGGESTED_WITH_SILENT_EFFECTS,
     {"curses_without_a_number": 1},
     "Maximise damage — 6 of 6 slots filled  ·  1 curse carries no number."),
    (advisorbar.State.SUGGESTED_WITH_AN_EMPTY_SLOT,
     {"slots_without_a_choice": 1,
      "empty_slots": (types.EmptySlot(5, types.EMPTY_NOTHING),)},
     "Maximise damage — 6 of 6 slots filled  ·  1 slot empty: nothing left to "
     "choose from."),
])
def test_all_three_result_states_say_what_they_go_without(state, extra, head):
    """AK-455: empty slots, then effects, then relics, in each of the three."""
    situation = advisorbar.Situation(
        state, goal_label="Maximise damage", slots=6, slots_filled=6,
        favourite_effects_unmet=2, favourite_relics_left_out=3, **extra)

    assert advisorbar.status_line(situation) == (
        f"{head}  ·  2 favourite effects could not be met.  ·  3 favourited "
        f"relics did not fit.")


def test_one_of_each_is_said_in_the_singular():
    situation = advisorbar.Situation(
        advisorbar.State.SUGGESTED, goal_label="Maximise damage", slots=6,
        slots_filled=6, favourite_effects_unmet=1, favourite_relics_left_out=1)

    assert advisorbar.status_line(situation) == (
        "Maximise damage — 6 of 6 slots filled  ·  1 favourite effect could "
        "not be met.  ·  1 favourited relic did not fit.")


def test_a_full_suggestion_with_every_favourite_met_says_neither(bar):
    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.answers(_an_answer())

    assert bar.status.accessibleName() == (
        "Maximise damage — 6 of 6 slots filled.")


def test_the_clauses_count_the_answer_and_the_tooltip_says_each_one(bar):
    """AK-455: `{n}` is the length of `required_left_out`, the tooltip is the
    sentence the `Why` dialog reads. AK-439: `{name}: {reason}`. A name out of
    the save comes through as text (SEC-019)."""
    pin = types.PinLeftOut("<b>Urn</b>", (1, (), ()), types.PIN_REJECTED,
                           because="you rejected it for this build")
    answer = dataclasses.replace(
        _an_answer(), required_left_out=(7, 8),
        required_unmet=("No copy you own carries A.", "No copy you own carries B."),
        pins_left_out=(pin,))

    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.answers(answer)

    assert bar.status.accessibleName() == (
        "Maximise damage — 6 of 6 slots filled  ·  2 favourite effects could "
        "not be met.  ·  1 favourited relic did not fit.")
    for tooltip in (bar.status.toolTip(), bar.toolTip()):
        assert "No copy you own carries A.<br>No copy you own carries B." in tooltip
        assert "&lt;b&gt;Urn&lt;/b&gt;: you rejected it for this build" in tooltip
        assert "<b>" not in tooltip


def test_the_next_state_takes_the_details_off_the_tooltip(bar):
    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.answers(dataclasses.replace(
        _an_answer(), required_left_out=(7,), required_unmet=("Unmet.",)))

    bar.the_build_changed()

    assert "Unmet." not in bar.status.toolTip()


# --- asking again from the block (AD-061, AK-424 to AK-426, AK-429) ----------

def test_asking_again_keeps_the_answer_and_waits_for_nothing(bar):
    """AK-424: no debounce. AK-425: the old blocks stay until the new one."""
    bar.optimize_button.click()
    bar._controller.begins()
    answer = _an_answer()
    bar._controller.answers(answer)

    bar.ask_again(done="“Strength” avoided.")

    assert bar.answer is answer
    assert bar.is_working()
    assert bar._controller.debounce_ms == 0
    assert len(bar._controller.asked) == 2


def test_the_answer_names_what_the_player_asked_for_last(bar):
    """AK-426: the last clause, and where to take it back in the tooltip."""
    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.answers(_an_answer())

    bar.ask_again(done="“Strength” avoided.", done_tip="Undo this in Filters.")
    bar._controller.begins()
    bar._controller.answers(dataclasses.replace(_an_answer(),
                                                required_left_out=(7,)))

    assert bar.status.accessibleName() == (
        "Maximise damage — 6 of 6 slots filled  ·  1 favourite effect could "
        "not be met.  ·  “Strength” avoided.")
    assert "Undo this in Filters." in bar.status.toolTip()


def test_the_next_optimize_forgets_that_clause(bar):
    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.answers(_an_answer())
    bar.ask_again(stopped="Stopped. “Urn” stays rejected.",
                  done="“Urn” rejected.")
    bar._controller.begins()
    bar._controller.answers(_an_answer())

    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.answers(_an_answer())

    assert bar.status.accessibleName() == (
        "Maximise damage — 6 of 6 slots filled.")


def test_cancel_says_what_stays_and_the_blocks_go(bar):
    """AK-425, AK-429."""
    seen = []
    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.answers(_an_answer())
    bar.suggestion_changed.connect(seen.append)

    bar.ask_again(stopped="Stopped. “Strength” stays avoided.")
    bar._controller.begins()
    bar.optimize_button.click()

    assert bar.status.accessibleName() == "Stopped. “Strength” stays avoided."
    assert bar.answer is None
    assert seen == [None]


def test_a_plain_cancel_keeps_its_sentence(bar):
    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.answers(_an_answer())
    bar.ask_again(stopped="Stopped. “Strength” stays avoided.")
    bar._controller.begins()
    bar._controller.answers(_an_answer())

    bar.optimize_button.click()
    bar._controller.begins()
    bar.optimize_button.click()

    assert bar.status.accessibleName() == "Stopped. Nothing was changed."


def test_a_failed_run_takes_the_old_blocks_with_it(bar):
    """Otherwise they would stand locked under a line saying it failed."""
    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.answers(_an_answer())

    bar.ask_again()
    bar._controller.failed.emit("the run gave up")

    assert bar.answer is None
    assert bar.situation.state is advisorbar.State.FAILED


def test_a_build_changed_under_a_run_from_the_block_still_outdates_it(bar):
    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.answers(_an_answer())
    bar.ask_again(stopped="Stopped. “Strength” stays avoided.")
    bar._controller.begins()

    bar.the_build_changed()

    assert bar.situation.state is advisorbar.State.OUTDATED
    assert bar.answer is None


def test_asking_again_without_a_save_says_so_and_takes_the_blocks(bar):
    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.answers(_an_answer())
    bar.asking["value"] = None

    bar.ask_again()

    assert bar.situation.state is advisorbar.State.NO_SAVE
    assert bar.answer is None


# --- the list of what was rejected (AK-430) ----------------------------------

@pytest.fixture
def rejected(qapp):
    widget = advisorbar.RejectedList()
    yield widget
    widget.deleteLater()


def test_with_nothing_rejected_the_list_takes_no_room(rejected):
    rejected.show_these([])

    assert rejected.isHidden()


def test_closed_it_is_one_line_that_counts(rejected):
    rejected.show_these([((1, (), ()), "Urn", "")])
    assert not rejected.isHidden()
    assert rejected.scroller.isHidden()
    assert rejected.fold.text() == "▸ 1 relic rejected for this build"

    rejected.show_these([((1, (), ()), "Urn", ""), ((2, (), ()), "Jar", "")])
    assert rejected.fold.text() == "▸ 2 relics rejected for this build"


def test_open_it_names_each_and_gives_it_back(rejected):
    roll = (1, (2,), ())
    rejected.show_these([(roll, "<b>Urn</b>", "Strength, Vigor")])
    rejected.fold.click()
    seen = []
    rejected.suggest_again.connect(seen.append)

    assert rejected.fold.text() == "▾ 1 relic rejected for this build"
    label = rejected.scroller.widget().findChild(advisorbar._ElidingLabel)
    assert label.accessibleName() == "<b>Urn</b> — Strength, Vigor"
    assert label.textFormat() == Qt.PlainText
    assert "&lt;b&gt;Urn" in label.toolTip()
    again = rejected.scroller.widget().findChild(QPushButton)
    assert again.text() == "Suggest again"
    again.click()
    assert seen == [roll]


def test_past_four_it_scrolls_in_here(rejected):
    """AK-430: four rows at most, the rest in the list's own scrolling."""
    four = [((index, (), ()), f"Relic {index}", "") for index in range(4)]
    six = [((index, (), ()), f"Relic {index}", "") for index in range(6)]

    rejected.show_these(four)
    height_of_four = rejected.scroller.maximumHeight()
    rejected.show_these(six)

    assert rejected.scroller.maximumHeight() == height_of_four


def test_six_blocks_with_x_and_reject_stay_inside_the_narrow_column(planner):
    """AK-421, AK-427, measured at the window's least width: no sideways
    scrolling under six cards, no button cut, and a line is as tall as its X
    and no taller."""
    planner.deep_check.setChecked(True)
    cards = planner.active_slots()
    lines = tuple(types.ReasonLine(slot_index=0, effect_id=index + 1,
                                   text=f"Effect {index}: Physical Attack +1")
                  for index in range(3)) + (
        types.ReasonLine(slot_index=0, effect_id=4, text="Curse: Vigor -1",
                         is_curse=True),)
    groups = tuple(types.SlotReasons(
        slot_index=index, relic_name="Grand Luminous Scene", effects_total=3,
        effects_with_a_figure=3, count_line="3 of its 3 effects moved a number.",
        lines=lines) for index in range(len(cards)))
    answer = types.AdvisorResult(
        goal_id="max_damage", goal_label="Maximise damage",
        suggestions=(types.Suggestion(
            choices=tuple(types.SlotChoice(index, 900 + index, 1, "Relic")
                          for index in range(len(cards))),
            score=types.GoalScore(1.0, "1", ""), reasons=groups),))
    planner.advisor_bar._answer = answer
    planner.advisor_bar._show(advisorbar.Situation(
        advisorbar.State.SUGGESTED, goal_label="Maximise damage",
        slots=len(cards), slots_filled=len(cards)))
    planner.show_the_suggestion(answer)
    planner.resize(planner.minimumWidth(), 900)
    planner.show()
    rendered.settle()
    try:
        area = _the_slot_area(planner)
        assert area.horizontalScrollBar().maximum() == 0
        block = cards[0].suggestion
        for button in (block.use_button, block.why_button, block.reject_button):
            assert button.width() >= button.minimumSizeHint().width(), (
                f"{button.text()} is cut: {button.width()} of "
                f"{button.minimumSizeHint().width()}")
            assert button.geometry().right() <= block.contentsRect().right()
        assert [line.height() for line in block.drawn_lines] == [24] * 4
    finally:
        planner.advisor_bar.clear()
        planner.hide()


# -- the row starts and stops the vessel comparison (AD-062.3, .4) ------------

class _Comparison(QObject):
    """What the row asks of `VesselComparison`, written down."""

    row_ready = Signal(object)
    finished = Signal(object)
    failed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.calls = []

    def start(self, questions, inventory, ctx) -> None:
        self.calls.append(("start", questions))

    def cancel(self) -> None:
        self.calls.append("cancel")

    def before_the_data_changes(self) -> None:
        self.calls.append("data")

    def shutdown(self) -> None:
        self.calls.append("shutdown")


FOUR_VESSELS = tuple({"id": index, "slots": [1, 1, 1], "deep_slots": [1, 1, 1]}
                     for index in (7, 8, 9, 10))


@pytest.fixture
def comparing_bar(qapp):
    asked = dataclasses.replace(_an_asking(), vessels=FOUR_VESSELS, vessel_id=8,
                                deep=True)
    widget = advisorbar.AdvisorBar(lambda goal_id: asked,
                                   controller=_Controller(),
                                   comparison=_Comparison())
    widget.asked = asked
    yield widget
    widget.deleteLater()


def test_an_answer_starts_the_comparison_with_the_chosen_vessel_first(
        comparing_bar):
    comparing_bar._ask()
    assert comparing_bar.comparison.calls == ["cancel"]
    comparing_bar._on_ready(_an_answer())
    _cancel, (name, questions) = comparing_bar.comparison.calls
    assert name == "start"
    assert [question.vessel_id for question in questions] == [8, 7, 9, 10]
    assert questions[0].request is comparing_bar.asked.request


def test_a_row_with_no_vessels_compares_nothing(bar):
    bar._on_ready(_an_answer())
    assert bar.comparison._waiting == []
    assert bar.comparison._controller._thread is None


@pytest.mark.parametrize("what_happens, expected", [
    (lambda widget: widget._ask(), "cancel"),
    (lambda widget: widget.ask_again(), "cancel"),
    (lambda widget: widget.the_data_is_changing(), "data"),
    (lambda widget: widget.shutdown(), "shutdown"),
], ids=["optimize", "ask_again", "data", "shutdown"])
def test_what_stops_the_comparison(comparing_bar, what_happens, expected):
    """AD-062.4; the last two are not optional (AD-006.7)."""
    what_happens(comparing_bar)
    assert comparing_bar.comparison.calls[0] == expected


# -- what the comparison says (AK-432, AK-449 to AK-453, AK-463 to AK-465) -----

NAMES = {1: "Urn", 2: "Chalice", 3: "Goblet", 4: "Grail"}


def _comparing(*rows, state=advisorbar.Compared.DONE, vessel_ids=(1, 2, 3, 4),
               held=0, carries=False) -> advisorbar.Comparing:
    return advisorbar.Comparing(
        goal_label="Maximise damage", other_label="Minimise damage taken",
        vessel_ids=vessel_ids, asked_vessel=1, held_relics=held,
        carries=carries, signature=(),
        rows={row.vessel_id: row for row in rows}, state=state)


def _row(vessel_id, value, other=1.0, figure=None, **kwargs) -> types.VesselRow:
    return types.VesselRow(vessel_id, figure or f"Attack rating {int(value)}",
                           value, other, **kwargs)


def _status(*rows, chosen=1, worn=None):
    return advisorbar.comparison_status(_comparing(*rows), chosen, worn, NAMES)


def test_the_chosen_vessel_being_the_best_offers_nothing():
    """AK-450 (1)."""
    assert _status(_row(1, 120), _row(2, 100), _row(3, 90), _row(4, 80)) == (
        "This is the best of 4 vessels for Maximise damage: AR 120.",
        None)


def test_a_better_vessel_is_named_with_the_difference():
    """AK-450 (2): also where it meets more favourites besides (AK-464)."""
    rows = (_row(1, 100, required_left_out=(5,)), _row(2, 118), _row(3, 90),
            _row(4, 80))
    assert _status(*rows) == (
        "Best of 4 for Maximise damage: Chalice — AR 118, 18 more than this "
        "one.", 2)


def test_the_same_value_with_more_favourites_says_so():
    """AK-464 (3)."""
    rows = (_row(1, 100, pins_left_out=("Urn",)), _row(2, 100), _row(3, 90),
            _row(4, 80))
    assert _status(*rows) == (
        "Best of 4 for Maximise damage: Chalice — AR 100, same as this one, "
        "but it meets more of your favourites.", 2)


def test_the_same_value_and_favourites_is_decided_by_the_other_direction():
    """AK-464 (3b): neither (3) nor (5)."""
    rows = (_row(1, 100, other=5.0), _row(2, 100, other=9.0), _row(3, 90),
            _row(4, 80))
    assert _status(*rows) == (
        "Best of 4 for Maximise damage: Chalice — AR 100, same as this one, "
        "but better for Minimise damage taken.", 2)


def test_a_smaller_value_is_explained_by_the_favourites():
    """AK-464 (4); nowhere the word "more" for the figure."""
    rows = (_row(1, 118, required_left_out=(5,)), _row(2, 100), _row(3, 90),
            _row(4, 80))
    assert _status(*rows) == (
        "Best of 4 for Maximise damage: Chalice — AR 100, 18 less than this "
        "one, but it meets more of your favourites.", 2)


@pytest.mark.parametrize("best, here, clause", [
    (100.4, 100.1, ""),
    (100.1, 100.4, ", but it meets more of your favourites"),
], ids=["higher", "lower"])
def test_a_difference_that_reads_zero_is_left_out(best, here, clause):
    """AK-449."""
    left_out = {"required_left_out": (5,)} if best < here else {}
    rows = (_row(1, here, **left_out), _row(2, best), _row(3, 1), _row(4, 1))
    assert _status(*rows)[0] == (
        f"Best of 4 for Maximise damage: Chalice — AR 100{clause}.")


def test_the_difference_is_that_of_the_numbers_on_screen():
    """QA-333: 118.16 and 113.18 stand as 118 and 113, and 5 is what that says."""
    rows = (_row(1, 113.18, figure="Attack rating 113"),
            _row(2, 118.16, figure="Attack rating 118"), _row(3, 1), _row(4, 1))
    assert "AR 118, 5 more than this one." in _status(*rows)[0]


def test_a_multiplier_differs_in_two_places():
    """AK-449: the form of the figure."""
    rows = (_row(1, 1.2, figure="Attack multipliers ×1.20"),
            _row(2, 1.42, figure="Attack multipliers ×1.42"), _row(3, 0.0),
            _row(4, 0.0))
    assert "— ×1.42, 0.22 more than this one." in _status(*rows)[0]
    assert advisorbar.vessel_line(_comparing(*rows), 2) == ("", "×1.42")


def test_a_tie_needs_every_key_of_the_rank_level():
    """AK-464 (5): with the chosen one among them, no button."""
    rows = (_row(1, 100), _row(2, 100), _row(3, 90), _row(4, 80))
    assert _status(*rows) == (
        "2 vessels tie for best at AR 100: Urn, Chalice", None)


def test_a_tie_without_the_chosen_goes_to_the_worn_then_the_first():
    """AK-432."""
    rows = (_row(1, 80), _row(2, 100), _row(3, 100), _row(4, 90))
    assert _status(*rows, worn=3)[1] == 3
    assert _status(*rows, worn=4)[1] == 2


def test_three_names_of_a_tie_are_cut_and_all_of_them_are_one_sentence():
    rows = (_row(1, 100), _row(2, 100), _row(3, 100), _row(4, 80))
    assert _status(*rows)[0] == (
        "3 vessels tie for best at AR 100: Urn, Chalice …and 1 more")
    rows = (_row(1, 100), _row(2, 100), _row(3, 100), _row(4, 100))
    assert _status(*rows) == ("All 4 vessels tie at AR 100.", None)


def test_an_unfit_vessel_opened_compares_with_no_figure_of_its_own():
    rows = (_row(1, 100), types.VesselRow(2, unfit_holds=("Urn",)), _row(3, 90),
            _row(4, 80))
    assert _status(*rows, chosen=2) == (
        "Best of 4 for Maximise damage: Urn — AR 100.", 1)


@pytest.mark.parametrize("state, reason, line", [
    (advisorbar.Compared.WAITING, "", "Comparing your vessels for Maximise damage…"),
    (advisorbar.Compared.RUNNING, "",
     "Comparing your vessels for Maximise damage… 1 of 4"),
    (advisorbar.Compared.OUTDATED, "",
     "Out of date — use Optimize again to compare."),
    (advisorbar.Compared.FAILED, "It broke",
     "Could not compare the vessels — It broke."),
])
def test_the_states_around_the_result(state, reason, line):
    comparing = _comparing(_row(1, 100), state=state)
    comparing.reason = reason
    assert advisorbar.comparison_status(comparing, 1, None, NAMES) == (line, None)


def test_best_waits_for_the_last_row():
    """AK-433: open rows show dots, and no mark flickers on the way."""
    running = _comparing(_row(1, 100), state=advisorbar.Compared.RUNNING)
    assert advisorbar.vessel_line(running, 1) == ("", "AR 100")
    assert advisorbar.vessel_line(running, 2) == ("", "…")
    done = _comparing(_row(1, 100), _row(2, 90))
    assert advisorbar.vessel_line(done, 1) == ("", "AR 100")
    assert advisorbar.vessel_line(done, 2) == ("", "AR 90")


def test_no_comparison_no_line_and_outdated_keeps_the_figures_without_best():
    """AK-453, AK-432."""
    assert advisorbar.vessel_line(None, 1) is None
    outdated = _comparing(_row(1, 100), state=advisorbar.Compared.OUTDATED)
    assert advisorbar.vessel_line(outdated, 1) == ("", "AR 100")
    assert advisorbar.vessel_line(outdated, 2) is None


def test_missing_favourites_stand_in_the_tooltip_not_on_the_line():
    """AK-452, AK-465 since `GOAL.md` A28: the line has no room for them."""
    one = _row(1, 100, pins_left_out=("Urn",))
    two = _row(2, 90, required_left_out=(5,), pins_left_out=("Urn",))
    comparing = _comparing(one, two)
    assert advisorbar.vessel_line(comparing, 1) == ("", "AR 100")
    assert advisorbar.vessel_line(comparing, 2) == ("", "AR 90")
    assert "Misses: 5, Urn." in advisorbar.vessel_compared_lines(comparing, 2, str)


def test_the_row_of_a_vessel_that_cannot_take_the_holds():
    """AK-451: no figure, never `BEST`, a tooltip and a spoken form of its own."""
    unfit = types.VesselRow(2, unfit_holds=("A", "B", "C"))
    comparing = _comparing(_row(1, 100), unfit)
    assert advisorbar.vessel_line(comparing, 2) == (
        "", "Your held relics do not fit")
    assert advisorbar.vessel_compared_lines(comparing, 2, str) == [
        "Not compared: A, B …and 1 more would not fit any slot of this vessel."]
    assert advisorbar.vessel_accessible_name(comparing, 2, "Chalice") == (
        "Chalice, your held relics do not fit, not ranked")


def test_the_tooltip_of_a_row_names_rank_misses_and_what_travelled():
    """AK-432, AK-452, AK-454: equal figures, equal rank."""
    rows = (_row(1, 100), _row(2, 100),
            _row(3, 90, required_left_out=(5, 6), pins_left_out=("Urn",)))
    comparing = _comparing(*rows, vessel_ids=(1, 2, 3), held=2, carries=True)
    assert advisorbar.vessel_compared_lines(comparing, 1, str) == [
        "Compared: Attack rating 100 for Maximise damage — rank 1 of 3."]
    assert advisorbar.vessel_compared_lines(comparing, 3, lambda eid: f"E{eid}") == [
        "Compared: Attack rating 90 for Maximise damage — rank 3 of 3.",
        "Misses: E5, E6, Urn.",
        "Compared with your 2 held relics placed in it.",
        "Click opens it as you left it. Switch to it brings your held relics "
        "and rejections along."]
    assert advisorbar.vessel_compared_lines(None, 1, str) == []


def test_misses_are_cut_after_four_names():
    row = _row(1, 90, required_left_out=(1, 2, 3, 4, 5))
    assert advisorbar.vessel_compared_lines(
        _comparing(row), 1, str)[1] == "Misses: 1, 2, 3, 4 …and 1 more."


def test_what_a_screen_reader_says_of_a_row():
    """AK-436."""
    comparing = _comparing(_row(1, 100), _row(2, 90))
    spoken = advisorbar.vessel_accessible_name
    assert spoken(comparing, 1, "Urn") == "Urn, Attack rating 100, best of 4"
    assert spoken(comparing, 2, "Urn") == "Urn, Attack rating 90, rank 2 of 4"
    assert spoken(None, 2, "Urn") == "Urn"


def _answered(comparing_bar):
    comparing_bar._ask()
    comparing_bar._controller.answers(_an_answer())
    return comparing_bar.comparing


def test_the_comparison_runs_through_its_states(comparing_bar):
    """AK-453: dots from the start of the run, figures as they come."""
    comparing_bar._ask()
    assert comparing_bar.comparing.state is advisorbar.Compared.WAITING
    comparing_bar._on_ready(_an_answer())
    assert comparing_bar.comparing.state is advisorbar.Compared.RUNNING
    comparing_bar.comparison.row_ready.emit(_row(8, 100))
    assert list(comparing_bar.comparing.rows) == [8]
    comparing_bar.comparison.finished.emit(())
    assert comparing_bar.comparing.state is advisorbar.Compared.DONE


def test_a_new_run_shows_no_old_figure(comparing_bar):
    """AK-453."""
    comparing = _answered(comparing_bar)
    comparing_bar.comparison.row_ready.emit(_row(8, 100))
    comparing_bar.ask_again()
    assert comparing_bar.comparing is not comparing
    assert comparing_bar.comparing.rows == {}


def test_cancel_leaves_a_list_without_a_comparison(comparing_bar):
    """AK-453: `Cancel` of the suggestion, no `Comparison stopped.`."""
    comparing_bar._ask()
    comparing_bar._on_started()
    comparing_bar._controller.running = True
    comparing_bar._optimize_or_cancel()
    assert comparing_bar.comparing is None


def test_a_run_that_failed_leaves_a_list_without_a_comparison(comparing_bar):
    comparing_bar._ask()
    comparing_bar._on_failed("no")
    assert comparing_bar.comparing is None


def test_a_failed_comparison_says_why(comparing_bar):
    _answered(comparing_bar)
    comparing_bar.comparison.failed.emit("It broke.")
    comparing = comparing_bar.comparing
    assert comparing.state is advisorbar.Compared.FAILED
    assert comparing.reason == "It broke"


def _changed(asking, **fields):
    return dataclasses.replace(asking, request=dataclasses.replace(
        asking.request, **fields))


@pytest.mark.parametrize("change", [
    lambda asked: _changed(asked, level=14),
    lambda asked: _changed(asked, goal_id="min_damage_taken"),
    lambda asked: _changed(asked, hero_id=2),
    lambda asked: _changed(asked, hit_with="Sorceries"),
    lambda asked: dataclasses.replace(asked, deep=False),
    lambda asked: _changed(asked, problem=dataclasses.replace(
        asked.request.problem, excluded=frozenset({1}))),
    lambda asked: _changed(asked, problem=dataclasses.replace(
        asked.request.problem, pinned=((1, (), ()),))),
], ids=["level", "goal", "hero", "hit_with", "deep", "avoid", "star"])
def test_what_makes_the_comparison_out_of_date(qapp, change):
    """AK-434, read from one seam (AD-062.8). The figures stay."""
    asked = {"value": dataclasses.replace(
        _an_asking(), vessels=FOUR_VESSELS, vessel_id=8, deep=True)}
    widget = advisorbar.AdvisorBar(lambda goal_id: asked["value"],
                                   controller=_Controller(),
                                   comparison=_Comparison())
    try:
        _answered(widget)
        widget.comparison.row_ready.emit(_row(8, 100))
        asked["value"] = change(asked["value"])
        widget.the_build_changed()
        assert widget.comparing.state is advisorbar.Compared.OUTDATED
        assert widget.comparison.calls[-1] == "cancel"
        assert list(widget.comparing.rows) == [8]
    finally:
        widget.deleteLater()


@pytest.mark.parametrize("change", [
    lambda asked: dataclasses.replace(asked, vessel_id=9),
    lambda asked: _changed(asked, two_handed=True),
    lambda asked: _changed(asked, problem=dataclasses.replace(
        asked.request.problem, slots=asked.request.problem.slots[:1])),
    lambda asked: _changed(asked, problem=dataclasses.replace(
        asked.request.problem, held=(types.HeldSlot(0),),
        rejected=frozenset({(1, (), ())}))),
], ids=["vessel", "stored hand", "slots", "another vessel's holds"])
def test_what_a_change_of_vessel_brings_does_not_outdate_it(qapp, change):
    """AK-434; the holds of the open vessel say so themselves (`_hold_changed`)."""
    asked = {"value": dataclasses.replace(
        _an_asking(), vessels=FOUR_VESSELS, vessel_id=8, deep=True)}
    widget = advisorbar.AdvisorBar(lambda goal_id: asked["value"],
                                   controller=_Controller(),
                                   comparison=_Comparison())
    try:
        _answered(widget)
        asked["value"] = change(asked["value"])
        widget.the_build_changed()
        assert widget.comparing.state is advisorbar.Compared.RUNNING
    finally:
        widget.deleteLater()


def test_the_data_changing_outdates_the_comparison(comparing_bar):
    """AK-434: the save read again."""
    _answered(comparing_bar)
    comparing_bar.the_data_is_changing()
    assert comparing_bar.comparing.state is advisorbar.Compared.OUTDATED
    assert "data" in comparing_bar.comparison.calls


def test_an_answer_the_comparison_knows_is_drawn_without_a_run(comparing_bar):
    """AK-435."""
    known = _an_answer(filled=2)
    comparing_bar._controller.known_answer = lambda *_: known
    assert comparing_bar.show_the_answer_if_known() is False, "nothing compared"
    _answered(comparing_bar)
    comparing_bar._forget_the_answer()
    asked_before = len(comparing_bar._controller.asked)
    calls_before = list(comparing_bar.comparison.calls)

    assert comparing_bar.show_the_answer_if_known() is True
    assert comparing_bar.answer is known
    assert len(comparing_bar._controller.asked) == asked_before
    assert comparing_bar.comparison.calls == calls_before, "AD-062.3"


def test_an_unknown_answer_leaves_the_row_alone(comparing_bar):
    comparing_bar._controller.known_answer = lambda *_: None
    _answered(comparing_bar)
    comparing_bar._forget_the_answer()
    assert comparing_bar.show_the_answer_if_known() is False
    assert comparing_bar.answer is None


def test_an_outdated_comparison_answers_for_no_vessel(comparing_bar):
    comparing_bar._controller.known_answer = lambda *_: _an_answer()
    _answered(comparing_bar)
    comparing_bar.the_comparison_is_out_of_date()
    assert comparing_bar.show_the_answer_if_known() is False


@pytest.mark.parametrize("figure, base, said", [
    ("Attack rating 90", "Attack rating 56", "AR 90 (+61 %)"),
    ("Fire attack rating 90", "Fire attack rating 45", "AR 90 (+100 %)"),
    ("Spell damage (Weapon art) 90", "Spell damage (Weapon art) 60",
     "Spell 90 (+50 %)"),
    ("Weapon art (Spell Parry) 90", "Weapon art (Spell Parry) 60",
     "Art 90 (+50 %)"),
    ("Effective HP 1100", "Effective HP 1000", "EHP 1100 (+10 %)"),
    ("Offensive attributes 33", "Offensive attributes 30", "33 pts (+10 %)"),
    ("Attack multipliers ×1.23", "Attack multipliers ×1.00", "×1.23 (+23 %)"),
    ("Attack rating 50", "Attack rating 100", "AR 50 (-50 %)"),
    ("Fire attack rating 90", "Fire attack rating 0", "AR 90"),
    ("Attack rating 90", "", "AR 90"),
    ("Spell damage not counted", "Spell damage not counted", "—"),
], ids=["ar", "typed", "spell", "art", "ehp", "points", "factor", "down",
        "base-zero", "no-base", "no-figure"])
def test_the_figure_says_its_unit_and_how_far_it_is_from_no_relics(figure, base,
                                                                   said):
    """GOAL.md A28: what "90" means; a base of 0 has no percentage."""
    row = _row(1, 90, figure=figure, base_figure=base)
    assert advisorbar.vessel_line(
        _comparing(row, state=advisorbar.Compared.RUNNING), 1) == ("", said)


def test_every_direction_says_a_unit_the_row_can_read(game_data, wylder):
    """The unit is read off the goal's own wording, so that wording is held."""
    _inventory, problem, ctx, _request = advisor.a_question(game_data, wylder)
    said = {}
    for goal in goals.GOALS.values():
        figure = goal.score(evaluate(problem, (), ctx, goal=goal), ctx).display
        said[goal.id] = advisorbar.vessel_line(_comparing(
            _row(1, 1, figure=figure), state=advisorbar.Compared.RUNNING), 1)[1]
    assert said["max_damage"].startswith("AR ")
    assert said["min_damage_taken"].startswith("EHP ")
    assert said["max_attributes"].endswith(" pts")


def test_the_sentence_and_the_tooltips_carry_the_percent_and_the_base():
    """GOAL.md A28: the base itself stands in the tooltip."""
    rows = (_row(1, 100, base_figure="Attack rating 50"),
            _row(2, 118, base_figure="Attack rating 50"),
            _row(3, 90, base_figure="Attack rating 50"),
            _row(4, 80, base_figure="Attack rating 50"))
    comparing = _comparing(*rows)
    assert advisorbar.comparison_status(comparing, 1, None, NAMES)[0] == (
        "Best of 4 for Maximise damage: Chalice — AR 118 (+136 %), 18 more "
        "than this one.")
    assert advisorbar.comparison_status(comparing, 2, None, NAMES)[0] == (
        "This is the best of 4 vessels for Maximise damage: AR 118 (+136 %).")
    assert advisorbar.vessel_line(comparing, 2) == ("", "AR 118 (+136 %)")
    assert "Without relics: Attack rating 50." in (
        advisorbar.vessel_compared_lines(comparing, 3, str))
    assert advisorbar.comparison_base(comparing) == (
        "Without relics: Attack rating 50.")
    comparing.state = advisorbar.Compared.OUTDATED
    assert advisorbar.comparison_base(comparing) == ""


NIGHT_INVADER = 7060200
#: "Max HP increased for each great enemy defeated at a Great Church".
HP_PER_GREAT_CHURCH_ENEMY = 6060300


def _stacks_in_the_question(planner):
    return dict(advisorbar.asking_from(planner, "max_damage").request.declared)


def test_the_stacks_value_goes_over_the_stat_sheet_and_leaves_it_alone(planner):
    """User decision 07.11.2026: empty is what it was (declared, else 1), a
    value goes over it, in the context and in the key alike, and the stat
    sheet's own declaration stays as it stood."""
    filters = planner.effect_filters
    try:
        assert _stacks_in_the_question(planner)[NIGHT_INVADER] == 1
        planner.declared = {NIGHT_INVADER: 5}
        assert _stacks_in_the_question(planner)[NIGHT_INVADER] == 5
        for count in (2, 0):
            filters.set_stacks(NIGHT_INVADER, count)
            asking = advisorbar.asking_from(planner, "max_damage")
            assert dict(asking.request.declared)[NIGHT_INVADER] == count
            assert asking.request.declared == asking.ctx.declared
        assert planner.declared == {NIGHT_INVADER: 5}
    finally:
        filters.set_stacks(NIGHT_INVADER, None)
    assert _stacks_in_the_question(planner)[NIGHT_INVADER] == 5


def test_a_changed_stacks_value_is_another_key(planner):
    """An old answer must not come back out of the cache for a new value."""
    filters = planner.effect_filters
    requests = []
    try:
        for count in (None, 2, 3, 0):
            filters.set_stacks(NIGHT_INVADER, count)
            requests.append(
                advisorbar.asking_from(planner, "max_damage").request)
    finally:
        filters.set_stacks(NIGHT_INVADER, None)
    assert len(set(requests)) == len(requests)


class _AnsweredAtOnce:
    """A picker track that computes the real pool in the same call."""

    def ask_and_answer_if_known(self, request, inventory, ctx):
        request = dataclasses.replace(
            request,
            inventory_fingerprint=advisor_run.inventory_fingerprint(inventory))
        return advisor_run.slot_pool(request, inventory, ctx, goals.GOALS)


def _picker_gain(planner, effect_id: int, goal_id: str) -> float:
    """What the picker of the first slot offering a relic with this effect
    shows for that relic: the real `SlotAdvice`, the real pool."""
    for slot in planner.active_slots():
        ranking = relicpicker.SlotAdvice(
            slot, planner.advisor_bar, _AnsweredAtOnce()).ask(None).ranking
        for candidate in ranking.pool.candidates:
            if effect_id in candidate.effect_ids:
                return types.marginal_for(candidate, goal_id)
    raise AssertionError(f"the frozen save offers no relic with {effect_id}")


@pytest.mark.parametrize("effect_id, goal_id", [
    (NIGHT_INVADER, "max_damage"),
    (HP_PER_GREAT_CHURCH_ENEMY, "min_damage_taken"),
])
def test_the_relic_picker_counts_the_stacks_value_too(
        planner, effect_id, goal_id):
    """QA-335, user decision 07.11.2026: the picker's question is built on
    `asking_from` and carries the value, in every column it moves, not only
    Damage. Red with the value taken out of `asking_from`."""
    planner.deep_check.setChecked(True)
    filters = planner.effect_filters
    try:
        filters.set_stacks(effect_id, 0)
        none = _picker_gain(planner, effect_id, goal_id)
        filters.set_stacks(effect_id, 4)
        four = _picker_gain(planner, effect_id, goal_id)
    finally:
        filters.set_stacks(effect_id, None)
    assert four != none


def test_a_stacks_change_reaches_the_row_as_a_marking(planner, monkeypatch):
    heard = []
    monkeypatch.setattr(planner.advisor_bar, "the_build_changed",
                        lambda **kwargs: heard.append(kwargs))
    planner.effect_filters.set_stacks(NIGHT_INVADER, 2)
    planner.effect_filters.set_stacks(NIGHT_INVADER, None)
    assert heard == [{"marking_changed": True}] * 2


def test_a_stacks_value_counts_as_declared_where_the_baseline_sorts_out(
        planner, monkeypatch):
    """The three places that ask "did the player say so": a value keeps a
    condition the baseline would take away for the armament or the ailment,
    and it does not stand among the assumed armament counts. None of the eight
    stack effects carries such a gate today, so three that do are made one."""
    from nrplanner import effecttext, model

    effects = planner.data["effects"]
    ids = {
        "weapon type": next(i for i in sorted(model.advisor_defaults())
                            if effects[str(i)]["modifiers"].get(
                                "triggerOnWepType") is not None
                            and i not in _stacks_in_the_question(planner)),
        "ailment": next(i for i in sorted(model.advisor_defaults())
                        if effecttext.ailment_awaited(effects[str(i)])
                        and i not in _stacks_in_the_question(planner)),
        "count": next(i for i in sorted(model.advisor_defaults())
                      if effecttext.counts_armaments(effects[str(i)])),
    }
    for effect_id in ids.values():
        monkeypatch.setitem(effects[str(effect_id)]["modifiers"],
                            "saveCategory", 9)
    filters = planner.effect_filters
    try:
        for effect_id in ids.values():
            filters.set_stacks(effect_id, 2)
        asking = advisorbar.asking_from(planner, "max_damage")
    finally:
        for effect_id in ids.values():
            filters.set_stacks(effect_id, None)
    declared = dict(asking.request.declared)
    assert {declared[effect_id] for effect_id in ids.values()} == {2}
    assert not set(ids.values()) & set(asking.ctx.assumed_armament_counts)
    assert not set(ids.values()) & set(asking.ctx.awaiting_ailment)


def test_the_store_cannot_make_another_condition_count_several_times(planner):
    """A hand in the registry: an id that is no stack effect, and one the
    dataset does not carry. Neither reaches the question."""
    from nrplanner import model

    other = next(effect_id for effect_id in sorted(model.advisor_defaults())
                 if effect_id in _stacks_in_the_question(planner)
                 and not model.accumulates(
                     planner.data["effects"][str(effect_id)]))
    lost = 999_999_999
    filters = planner.effect_filters
    filters.set_stacks(other, 5)
    filters.set_stacks(lost, 5)
    try:
        declared = _stacks_in_the_question(planner)
    finally:
        filters.set_stacks(other, None)
        filters.set_stacks(lost, None)
    assert declared[other] == 1
    assert lost not in declared
