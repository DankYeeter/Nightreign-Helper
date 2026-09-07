"""The advisor's row: every line of `UI_SPEC` §4, and the order they come in.

**Two halves, and they prove different things.** The first half drives the row
through a controller of the test's own, because the states of §4 are about
*when* a thing is said and a real search cannot be made to take 251 ms on
demand. The second half builds the real window with the real
`AdvisorController` and runs a real search over the player's own save: that
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
from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QScrollArea

from nrplanner import advisorbar
from nrplanner.advisor import goals, types
from tests import rendered

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
               not_counted: tuple = ()) -> types.AdvisorResult:
    """An answer that fills `filled` slots of the question above."""
    choices = tuple(types.SlotChoice(slot_index=index, handle=100 + index,
                                     relic_id=200 + index, name=f"Relic {index}")
                    for index in range(filled))
    score = types.GoalScore(value=1.0, display="Attack rating 100", unit="AR")
    return types.AdvisorResult(
        goal_id="max_damage", goal_label="Maximise damage",
        suggestions=(types.Suggestion(choices=choices, score=score),),
        curses_without_a_figure=curses, not_counted=not_counted)


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
    assert bar.status.whole_text() == "Nothing suggested yet."
    assert bar.optimize_button.text() == "Optimize"
    assert bar.optimize_button.toolTip() == (
        "Fills every slot from the relics in your save. Nothing changes "
        "until you apply it.")
    assert bar.progress.isHidden()


def test_the_two_directions_stand_in_the_order_the_spec_lists_them(bar):
    """§3.1: `Maximise damage`, then `Minimise damage taken`."""
    assert [bar.goal_box.itemText(i) for i in range(bar.goal_box.count())] == [
        "Maximise damage", "Minimise damage taken"]


def test_without_a_save_the_row_says_so_and_disables_its_own_two_controls(bar):
    """4.8, and only this row's controls (AK-08 is about all the others)."""
    bar.asking["value"] = None
    bar.the_build_changed()
    assert bar.situation.state is advisorbar.State.NO_SAVE
    assert bar.status.whole_text() == (
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
    early = (bar.progress.isHidden(), bar.status.whole_text())
    bar._controller.answers(_an_answer())
    _wait(300)
    assert early == (True, "")
    assert bar.progress.isHidden()
    assert bar.status.whole_text() == "Maximise damage — 6 of 6 slots filled."


def test_a_run_over_the_threshold_waits_out_loud(bar):
    """AK-10, 4.3: the bar, the waiting line, and `Cancel` on the button."""
    bar.optimize_button.click()
    bar._controller.begins()
    _wait(WAITED_OUT_MS)
    assert bar.situation.state is advisorbar.State.WORKING
    assert bar.status.whole_text() == "Working out maximise damage…"
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
    assert bar.status.whole_text() == (
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
    assert bar.status.whole_text() == "Stopped. Nothing was changed."
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
    assert bar.status.whole_text() == (
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
    assert bar.status.whole_text() == (
        "Maximise damage — 5 of 6 slots filled  ·  1 slot has nothing to "
        "choose from.")


def test_an_answer_with_silent_effects_says_that_much(bar):
    """4.9, from the answer's own two fields (AK-142/AK-143).

    Two different questions, two clauses, and they arrive from two different
    fields of the result: a curse of a suggested copy that no figure covers,
    and an effect the ranking left out because it is conditional. Driven
    through the answer rather than through a `Situation` so that the reading
    of the fields is measured as well as the wording.
    """
    curse = types.ReasonLine(slot_index=0, text="Taking Damage Causes Madness",
                             is_curse=True,
                             silence=types.SILENT_NO_NUMBER_HERE)
    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.answers(_an_answer(curses=(curse,),
                                       not_counted=("Under a condition",)))
    assert bar.situation.state is (
        advisorbar.State.SUGGESTED_WITH_SILENT_EFFECTS)
    assert bar.status.whole_text() == (
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
    line = types.ReasonLine(slot_index=0, text="Improved Melee Attack Power",
                            silence=types.SILENT_NO_NUMBER_HERE)
    answer = _an_answer()
    answer = dataclasses.replace(answer, effects_without_a_figure=(line,))
    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.answers(answer)
    assert bar.situation.state is advisorbar.State.SUGGESTED
    assert bar.status.whole_text() == "Maximise damage — 6 of 6 slots filled."


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
               if button is not bar.optimize_button and not button.isHidden()]
    assert 1 <= len(actions) <= 3


def test_a_run_that_failed_says_one_line_and_no_stack_trace(bar):
    """4.12, and the full stop is the sentence's, not the reason's."""
    bar.optimize_button.click()
    bar._controller.begins()
    bar._controller.failed.emit("the dataset carries no attribute curves.")
    assert bar.status.whole_text() == (
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
    assert bar.status.whole_text() == "Could not work that out — <b>relic</b> & co."
    assert "&lt;b&gt;relic&lt;/b&gt; &amp; co" in bar.status.toolTip()
    assert "<b>relic</b>" not in bar.status.toolTip()


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


def test_at_the_opening_width_only_the_status_is_shortened(planner):
    """AK-05: nothing else in the row is cut at 1320 px, and 4.12 is long."""
    planner.resize(1320, 900)
    planner.show()
    rendered.settle()
    try:
        if planner.width() != 1320:
            pytest.skip(f"this platform will not give the window 1320 "
                        f"logical px: it is {planner.width()} px wide")
        bar = planner.advisor_bar
        bar._on_failed("the dataset carries no attribute curves for this "
                       "Nightfarer, so nothing could be worked out at all")
        rendered.settle()
        assert rendered.clipped([bar.goal_box, bar.optimize_button], bar) == []
        assert bar.status.text() != bar.status.whole_text()
        assert bar.status.text().endswith("…")
        assert html.escape(bar.status.whole_text()) in bar.status.toolTip()
    finally:
        planner.close()


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
    if planner.owned is None:
        pytest.skip("this machine has no save to read")
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
        f"{bar.status.whole_text()!r}")
    assert _slot_state(planner) == before
    assert planner._build is sheet
    bar.shutdown()


def test_cancel_is_visible_within_the_two_hundred_milliseconds(planner):
    """AK-11, measured against the real controller.

    The worker is not waited for: the whole point of the figure is that the
    row says `Stopped` while the search is still on its way out.
    """
    if planner.owned is None:
        pytest.skip("this machine has no save to read")
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
    """
    real = planner.advisor_bar.the_data_is_changing
    held = []

    def spy():
        held.append(planner.owned)
        real()

    monkeypatch.setattr(planner.advisor_bar, "the_data_is_changing", spy)
    before = planner.owned
    planner.rescan_save()
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
