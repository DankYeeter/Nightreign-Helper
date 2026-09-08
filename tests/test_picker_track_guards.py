"""Nine guards over the picker's advisor track (U6/U10, AD-028, IX and X).

The track was built in U5a and U5b, and the fault T-130 found is what these
are for: **the way was wired, looked finished and did nothing.**
`run.slot_pool` handed back a pool carrying `generation = 0`, `_on_ready`
judged every answer overtaken and dropped it without a word, and the suite was
green. Nothing on the screen said anything; the dialog simply waited.

**Every guard here states a state, and not one of them reads a clock**
(AD-028's express condition, and the reason the `ui-ux-designer` wrote AK-211
to AK-219 without a single millisecond). Where a case turns the event loop it
turns it *until something is true*, and the timeout it passes is a fuse
against a hang -- nothing is asserted about how long anything took.

**Every W here is an AD-028 W, and there is a second series.** The facade
chain of AD-019 counts its own `W0` to `W6` (`ARCHITECTURE.md` 1835, 2650,
2662), and `AD-019 W6` is not `AD-028 W6`. Neither series is renamed -- both
stand in tests, reports and drafts -- so every mention carries where it comes
from (`director`, 08.09.2026). Everything below is **AD-028**.

Which guard is which, and where it comes from:

* **W1** (AD-028, wording drawn level by Nachtrag X-3 Fassung 2) -- nobody
  under `nrplanner/` reaches the calculation but the four places named below;
* **W2** (AD-028, in the form of AK-212, which is what the App Designer's
  decision of 08.09.2026 left of it) -- the first paint is an empty grid and
  it is a *state*;
* **W3** (Nachtrag IX-4) -- an overtaken answer reaches no dialog, in the two
  shapes that can still occur;
* **W4** (Nachtrag IX-4) -- what the picker draws is a subset of what the pool
  scores;
* **W5** (Nachtrag IX-4, holding IX-1.3) -- a known answer is drawn in the
  first paint, in one build of the grid;
* **W6** (`worker.py`'s own promise, AK-218) -- a question ends in exactly one
  of `ready`, `failed` and `stopped`;
* **W7** (T-130's fault) -- the answer is stamped with the generation it was
  asked under;
* **W8** (Nachtrag X, AK-218 Fassung 2) -- every way *into* the track has a
  row in a table here, and every row says what the player then has in front
  of them;
* **W9** (Nachtrag X-2) -- every place that *interrupts* a running worker has
  a row in a table here, and the row says what the outgoing question hears.
"""

from __future__ import annotations

import ast
import pathlib

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QWidget

from nrplanner import advisorbar, relicpicker
from nrplanner.advisor import goals as advisor_goals
from nrplanner.advisor import run as advisor_run
from nrplanner.advisor import types, worker

from tests import advisor_cases as advisor
from tests import picker_track
from tests import weapon_damage_cases as cases
from tests.test_one_build import call_sites, python_modules

REPO = pathlib.Path(__file__).resolve().parents[1]

DAMAGE = "max_damage"
SURVIVAL = "min_damage_taken"


# --- W1: only one place computes, and it is not the main thread ------------

#: Which file under `nrplanner/` may name each of the four, and why.
#:
#: **This is wider than AD-028's first wording, and the difference is
#: measured, not assumed.** Fassung 1 said "no file but `advisor/worker.py`";
#: it was written before U5b existed, and two of the entries below could not
#: be anywhere else:
#:
#: * `run.slot_pool` is what `app.py` **hands to** the picker's controller at
#:   construction (AD-028 option D). It is named there and called nowhere: a
#:   track that was not given its answer function would have no answer.
#: * `candidates.pool` is called by `run.slot_pool` itself, which is the pool
#:   function -- forbidding it there would forbid the function.
#:
#: Nachtrag X-3 drew the wording level with this table (Fassung 2, binding)
#: and added the fourth row, `candidates.pools`. That one is not bookkeeping:
#: it is the **nearest way round this guard**. IX-5 had the plural on the
#: table as a proposal -- warming the whole set of pools when the Build
#: planner opens, a measured 610,7 ms in the main thread (S11-C) -- and the
#: proposal was refused. Without the row, the pool function may not be named
#: outside the worker's thread while the function that builds *every* pool
#: may be named anywhere.
#:
#: What AD-028 is about survives untouched: no window, no dialog and no tab
#: reaches the calculation, so nothing but the worker's thread can run it.
#: The expectation is this table, never what the watched files say (L-008b).
#:
#: **Where this guard stops, and it is a boundary rather than a hole**
#: (Nachtrag X-3, last paragraph): it hangs on `test_one_build.call_sites`
#: and therefore on **module short name plus function name**. It sees the
#: seven spellings of the names listed here; it does not see arithmetic that
#: reaches the main thread under some **other** name -- a direct grip into
#: `search`, say. Whoever writes a new computing entry point enters it here;
#: nothing in this file can notice that they did not.
MAY_REACH_THE_CALCULATION = {
    ("run", "run"): {
        "nrplanner/advisor/worker.py":
            "the Advisor bar's controller is built with it (AD-028 option D)",
    },
    ("run", "slot_pool"): {
        "nrplanner/app.py":
            "the picker's controller is built with it (AD-028 option D); "
            "handed over, never called",
    },
    ("candidates", "pool"): {
        "nrplanner/advisor/run.py":
            "`slot_pool` is the pool function and this is the pre-sort it is "
            "a wrapper for",
    },
    ("candidates", "pools"): {
        "nrplanner/advisor/run.py":
            "the whole run builds every slot's pool once, inside `run.run` "
            "and so inside the worker's thread (Nachtrag X-3.3); named "
            "anywhere else it is IX-5's refused warm-up, 610,7 ms in the "
            "main thread",
    },
}


def names_of(module_short_name: str, function_name: str) -> dict[str, int]:
    """Every file under `nrplanner/` that gets hold of one function, and how
    often.

    Read off the syntax tree by `test_one_build.call_sites`, which is the walk
    AD-028 names for this guard: it sees the seven spellings a second
    calculation would plausibly be written in -- the function imported by
    name, the module under an alias, `getattr`, a line break after the dot,
    `functools.partial` -- where a text search sees one.
    """
    found = {}
    for path in python_modules(REPO / "nrplanner"):
        count = call_sites(path.read_text(encoding="utf-8"), module_short_name,
                           frozenset({function_name}))
        if count:
            found[path.relative_to(REPO).as_posix()] = count
    return found


@pytest.mark.parametrize(
    "module_short_name,function_name",
    sorted(MAY_REACH_THE_CALCULATION),
    ids=lambda part: part)
def test_w1_nothing_but_the_named_places_reaches_the_calculation(
        module_short_name, function_name):
    """AD-028: the picker's arithmetic is reachable from one place only.

    The picker used to work its own pool out in the calling thread on the
    strength of a figure that was never measured but calculated -- ~51 ms
    against a real 318,1 ms (S11-C), six times A6's budget for the main
    thread. What keeps it from coming back is not that the call was deleted
    but that nowhere may hold it: a reference handed to `functools.partial` or
    assigned to a name is a call one step later.
    """
    allowed = MAY_REACH_THE_CALCULATION[(module_short_name, function_name)]
    found = names_of(module_short_name, function_name)

    assert set(found) == set(allowed), (
        f"{module_short_name}.{function_name} is named in {sorted(found)}; "
        f"AD-028 allows {sorted(allowed)}. A file that gets hold of it can "
        f"run it in the thread it is called from, which is the main one")


def test_w1_the_picker_holds_none_of_the_four():
    """The same rule read from the other end, at the file it was written for.

    Set equality above says this too, and says it as an absence. This case
    says it as a presence -- `relicpicker.py` names none of the four -- so
    that a reader of a failure knows at once which file broke the rule, and so
    that a table entry added by mistake cannot quietly re-admit the picker.
    """
    source = (REPO / "nrplanner" / "relicpicker.py").read_text(
        encoding="utf-8")

    reached = {
        f"{module}.{function}": call_sites(source, module,
                                           frozenset({function}))
        for module, function in MAY_REACH_THE_CALCULATION}

    assert reached == {"run.run": 0, "run.slot_pool": 0, "candidates.pool": 0,
                       "candidates.pools": 0}


# --- W2: the empty grid is a state, not an absence (AK-212) ----------------

@pytest.fixture
def a_track_to_ask(shared_planner):
    """A window that has something to rank against, or a skip (4.8).

    `shared_planner` and not `planner`: building a window costs about ten
    seconds of save reading, and not one case here writes to the window --
    they open a dialog over a track of their own, read it and close it again.
    The condition the shared fixture states is met: every case sets what it
    depends on, so the order they run in cannot matter.
    """
    if not picker_track.there_is_something_to_ask(shared_planner):
        pytest.skip("this machine has no save, so the picker asks nothing")
    return shared_planner


def area_labels(dialog) -> list[str]:
    """Every line standing in the card area, in order."""
    return [label.text()
            for label in dialog.scroll.widget().findChildren(QLabel)]


def test_w2_the_first_paint_is_an_empty_grid_that_says_so(a_track_to_ask,
                                                          qapp):
    """AK-212, whole, over a track that has been asked and is still working.

    Every clause of the criterion in one case, because what the App Designer
    decided is a *state*: no card widget and no custom tile, no relic name, no
    figure, no chip, nothing in the area reachable by Tab, one line where the
    top left card will stand, an empty header, the waiting sentence in line 3,
    the two mandatory lines standing in full, and nothing locked.

    The track really is working: the case waits for the answer function to be
    entered before it reads anything, so this is not a dialog that has not got
    round to asking yet.
    """
    slot, = picker_track.slots_that_offer_relics(a_track_to_ask, 1)
    track, answers = picker_track.a_track([picker_track.pool_for(slot)],
                                          hold=True)
    dialog = None
    try:
        dialog = picker_track.picker_over(slot, track)
        assert picker_track.spin(qapp, lambda: answers.calls == 1), (
            "the question never reached the track, so this case would be "
            "reading a dialog that had not asked yet")

        assert dialog.waiting, "the dialog does not know it is waiting"
        assert picker_track.cards_in(dialog) == []
        assert picker_track.tiles_in(dialog) == [], (
            "the custom tile is a card and waits with the rest (AK-212)")
        assert area_labels(dialog) == ["Your relics appear here."]
        assert [child for child in dialog.scroll.widget().findChildren(QWidget)
                if child.focusPolicy() != Qt.NoFocus] == [], (
            "something in the empty area takes the keyboard focus, so Tab "
            "reaches into a grid that is not there")
        assert dialog.summary.text() == (
            f"Working out what each relic is worth with "
            f"{slot.slot_name()} empty")
        assert not dialog.headline.isVisibleTo(dialog), (
            "the header belongs to an answer and there is none")

        assert dialog.caveats.isVisibleTo(dialog)
        assert dialog.caveats.text().startswith(
            "One slot at a time — some relics only pay off together; "
            "Optimize on the Build planner looks for those.")
        for sentence in advisor_goals.GOALS[dialog.advice.goal_id()].scope:
            assert sentence in dialog.caveats.text(), (
                "AK-201: what is true before any run stands from the first "
                "paint")

        assert dialog.search.isEnabled()
        assert dialog.sort_box.isEnabled()
        assert dialog.scroll.isEnabled()
        assert dialog.cursor().shape() != Qt.WaitCursor
        assert QApplication.overrideCursor() is None, (
            "AK-213: no wait cursor while the area is empty")
    finally:
        answers.release()
        if dialog is not None:
            dialog.done(0)
            dialog.deleteLater()
        track.shutdown()


# --- W3: an overtaken answer reaches nothing (Nachtrag IX-4) ---------------

def test_w3_the_answer_of_a_closed_opening_never_fills_the_next_one(
        a_track_to_ask, qapp):
    """Two openings at one track, and the first answer arrives last.

    The track lives at the window and outlives every picker (AD-028 point 5).
    Slot A is opened and closed before its answer is there, then slot B is
    opened; A's answer arrives while B's dialog stands. Without the generation
    counter B's grid carries A's figures -- the same cards, plausible values,
    and nothing anywhere to say they belong to another slot.

    The direction the old wording used -- a change of goal in the open dialog
    -- cannot make a second question any more (Nachtrag IX-0, AK-204), which
    is why this fixture replaces it.
    """
    first_slot, second_slot = picker_track.slots_that_offer_relics(
        a_track_to_ask, 2)
    track, answers = picker_track.a_track(
        [picker_track.pool_for(first_slot),
         picker_track.pool_for(second_slot)], hold=True)
    opened_first = opened_second = None
    try:
        opened_first = picker_track.picker_over(first_slot, track)
        assert picker_track.spin(qapp, lambda: answers.calls == 1), (
            "the first question never reached the track")
        opened_first.done(0)

        opened_second = picker_track.picker_over(second_slot, track)
        assert opened_second.waiting, (
            "the second opening was answered before the first, so the "
            "ordering this case is about did not happen")

        answers.release()
        assert picker_track.spin(qapp, lambda: not opened_second.waiting), (
            "the second opening never got an answer of its own")
        picker_track.settle(qapp)

        assert opened_second.ranking.pool.slot_index == second_slot.index, (
            f"the second opening is showing the pool of slot "
            f"{opened_second.ranking.pool.slot_index} and it asked about "
            f"{second_slot.index}: the overtaken answer reached the screen")
        assert picker_track.cards_in(opened_first) == [], (
            "the answer drew into the dialog that had asked for it and gone")
    finally:
        answers.release()
        for dialog in (opened_first, opened_second):
            if dialog is not None:
                dialog.done(0)
                dialog.deleteLater()
        track.shutdown()


def test_w3_an_answer_arriving_after_the_close_touches_nothing(
        a_track_to_ask, qapp):
    """The second fixture of the same guard, and it covers the survivor.

    With one opening there is no later question, so the generation counter has
    nothing to compare against: what keeps the answer out here is that the
    dialog stopped listening when it closed (AK-207). The two devices are
    deliberately both there, and a counterbuild that removes only one has to
    be caught by one of the two cases -- this is the other one.
    """
    slot, = picker_track.slots_that_offer_relics(a_track_to_ask, 1)
    track, answers = picker_track.a_track([picker_track.pool_for(slot)],
                                          hold=True)
    dialog = None
    try:
        dialog = picker_track.picker_over(slot, track)
        assert picker_track.spin(qapp, lambda: answers.calls == 1), (
            "the question never reached the track")
        dialog.done(0)

        answers.release()
        picker_track.settle(qapp)

        assert picker_track.cards_in(dialog) == [], (
            "an answer that arrived after the close drew into the dialog")
        assert dialog.waiting, (
            "the closed dialog left the waiting state, so something wrote "
            "into it after it had gone")
    finally:
        answers.release()
        if dialog is not None:
            dialog.deleteLater()
        track.shutdown()


# --- W4: the picker draws no direction the pool cannot score ---------------

def test_w4_every_direction_the_picker_draws_is_one_the_pool_scores():
    """Nachtrag IX-4: the whole of IX-0's reuse rests on this.

    The picker asks under one fixed direction and reads *both* columns out of
    the one pool that comes back, so a direction offered on screen that the
    pool never measured would draw an empty column -- or a `Sort by` entry
    whose label cannot be built at all. Two files, no window, and nobody
    holding them together but this case.
    """
    drawn = set(advisorbar.GOAL_ORDER)
    scored = set(advisor_goals.GOALS)

    assert drawn <= scored, (
        f"the picker and the Advisor bar offer {sorted(drawn - scored)}, "
        f"which the registry does not score; the pool would carry no figure "
        f"for it")
    assert advisor_goals.CANONICAL_POOL_ORDER in scored, (
        "the order every picker question is asked under is not a direction "
        "the registry scores")


# --- W5: a known answer is drawn in the first paint (IX-1.3) ---------------

def test_w5_a_known_answer_is_one_build_of_the_grid_and_never_pending(
        a_track_to_ask, qapp):
    """Nachtrag IX-1.3, which the empty grid turned from a saving into a
    precondition.

    At a measured 30 % of openings the answer is already in the track's cache
    (S11-F). If the controller answered those through the timer and the signal
    like any other question, the empty grid would appear and be replaced one
    turn of the event loop later -- a whole grid flashing up and going again,
    at every third opening.

    Counted, never timed (L-002): the grid's contents are built once for a
    known answer and twice for an unknown one, and both halves are in this
    case because a grid that is never rebuilt at all would satisfy the first
    half on its own.
    """
    slot, = picker_track.slots_that_offer_relics(a_track_to_ask, 1)
    track, answers = picker_track.a_track([picker_track.pool_for(slot)])
    unknown = known = None
    try:
        unknown = picker_track.counting_picker_over(slot, track)
        assert unknown.waiting, "the counter-check needs an unknown answer"
        assert picker_track.spin(qapp, lambda: not unknown.waiting), (
            "no answer arrived")
        assert unknown.builds == 2, (
            f"the opening that had to wait built its grid {unknown.builds} "
            f"times; the empty one and the filled one are two")
        unknown.done(0)

        known = picker_track.counting_picker_over(slot, track)

        assert not known.waiting, (
            "the answer was in the cache and the dialog waited for it anyway")
        assert known.builds == 1, (
            f"the opening whose answer was already known built its grid "
            f"{known.builds} times, so the empty grid flashed up before it")
        assert answers.calls == 1, "a known answer was worked out again"
        assert picker_track.cards_in(known), (
            "the first build of a known answer drew no cards")
        assert relicpicker.PENDING not in [
            label.text()
            for label in known.scroll.widget().findChildren(QLabel)], (
            "AK-219: no card standing in the area ever carries the pending "
            "mark")
    finally:
        for dialog in (unknown, known):
            if dialog is not None:
                dialog.done(0)
                dialog.deleteLater()
        track.shutdown()


# --- W6: a question ends in exactly one of the three -----------------------

@pytest.fixture(scope="module")
def wylder(game_data):
    return cases.hero_by_name(game_data, "Wylder")


@pytest.fixture
def question(game_data, wylder):
    """One small question, and the material it is asked against."""
    return advisor.a_question(game_data, wylder, count=4)


def a_bare_track(answer, cache: advisor_run.ResultCache | None = None):
    """A picker track over a stated answer function, with no window at all."""
    return worker.AdvisorController(
        answer=answer,
        cache=advisor_run.ResultCache(worker.PICKER_CACHE_SIZE)
        if cache is None else cache,
        debounce_ms=worker.PICKER_DEBOUNCE_MS)


def a_pool(request) -> types.SlotPool:
    """The smallest answer of the picker's shape."""
    return types.SlotPool(slot_index=0, rank_by=request.goal_id)


def _the_answer_comes_back(qapp, question):
    inventory, _problem, ctx, request = question
    track = a_bare_track(lambda req, *rest: a_pool(req))
    seen = picker_track.Outcomes(track)
    track.ask(request, inventory, ctx)
    picker_track.spin(qapp, lambda: bool(seen.signals))
    picker_track.settle(qapp)
    return track, seen


def _the_answer_raises(qapp, question):
    inventory, _problem, ctx, request = question

    def raising(*_args, **_kwargs):
        raise ValueError("the dataset lost a curve")

    track = a_bare_track(raising)
    seen = picker_track.Outcomes(track)
    track.ask(request, inventory, ctx)
    picker_track.spin(qapp, lambda: bool(seen.signals))
    picker_track.settle(qapp)
    return track, seen


def _the_question_is_cancelled_before_it_runs(qapp, question):
    inventory, _problem, ctx, request = question
    track = a_bare_track(lambda req, *rest: a_pool(req))
    seen = picker_track.Outcomes(track)
    track.ask(request, inventory, ctx)
    assert track.cancel() is True, "there was nothing waiting to cancel"
    picker_track.settle(qapp)
    return track, seen


def _the_run_is_cancelled_while_it_works(qapp, question):
    inventory, _problem, ctx, request = question
    answers = picker_track.StatedAnswers([a_pool(request)], hold=True)
    track = a_bare_track(answers)
    seen = picker_track.Outcomes(track)
    track.ask(request, inventory, ctx)
    assert picker_track.spin(qapp, lambda: answers.calls == 1), (
        "the run never started, so nothing was cancelled while it worked")
    assert track.cancel() is True
    answers.release()
    picker_track.settle(qapp)
    return track, seen


def _the_data_is_rebuilt_under_the_run(qapp, question):
    inventory, _problem, ctx, request = question
    answers = picker_track.StatedAnswers([a_pool(request)], hold=True)
    track = a_bare_track(answers)
    seen = picker_track.Outcomes(track)
    track.ask(request, inventory, ctx)
    assert picker_track.spin(qapp, lambda: answers.calls == 1), (
        "the run never started")
    track.before_the_data_changes()
    answers.release()
    picker_track.settle(qapp)
    return track, seen


def _the_window_is_closing(qapp, question):
    """The run is still out when `shutdown` comes, and the answer is late.

    The one ordering the promise of Nachtrag X-0 is about: the worker has
    been entered, `shutdown` interrupts it and waits with no patience at all
    (`timeout_ms=0`, so the wait is over before the answer exists), and only
    then is the answer let through. Whatever the worker sends now is sent
    after the window has gone.
    """
    inventory, _problem, ctx, request = question
    answers = picker_track.StatedAnswers([a_pool(request)], hold=True)
    track = a_bare_track(answers)
    seen = picker_track.Outcomes(track)
    track.ask(request, inventory, ctx)
    assert picker_track.spin(qapp, lambda: answers.calls == 1), (
        "the run never started, so there was nothing still out when the "
        "window closed and this fixture would be about nothing")
    track.shutdown(timeout_ms=0)
    answers.release()
    picker_track.settle(qapp)
    return track, seen


#: Every way one question of one opening can end, and what the window hears.
#:
#: The list is the ways the controller offers, read off `worker.py`: the
#: answer function returns or raises, and the question is abandoned before it
#: runs, while it runs, by a rebuild of the data, or by the window closing.
#:
#: **The last one is the exception of Nachtrag X-0 and its expectation is an
#: empty list written out here** (L-008b), never one worked out from what
#: `shutdown` does: the window is closing, `stopped` would be a sentence to a
#: player who is no longer there (`UI_SPEC` 4.5, AK-11), and an answer that
#: was already on its way must not arrive either. What makes that a property
#: rather than a race is the line `shutdown` shares with `cancel` -- the
#: generation goes up before the worker is interrupted (Nachtrag X-1,
#: decision D).
WAYS_A_QUESTION_ENDS = {
    "the answer comes back": (_the_answer_comes_back, ["ready"]),
    "the answer raises": (_the_answer_raises, ["failed"]),
    "cancelled before it runs": (_the_question_is_cancelled_before_it_runs,
                                 ["stopped"]),
    "cancelled while it works": (_the_run_is_cancelled_while_it_works,
                                 ["stopped"]),
    "the data is rebuilt": (_the_data_is_rebuilt_under_the_run, ["stopped"]),
    "the window is closing": (_the_window_is_closing, []),
}


@pytest.mark.parametrize("way", sorted(WAYS_A_QUESTION_ENDS))
def test_w6_a_question_ends_in_exactly_one_of_the_three(qapp, question, way):
    """`worker.py`'s own promise, and AK-218 hangs on it.

    *"The window asks with `ask` and hears back on exactly one of `ready`,
    `failed` and `stopped` -- for the question that is still the current one
    when it ends."* The existing cases hold single instances of that --
    `stopped` exactly once, no `ready` after a cancel -- and none of them
    holds the promise itself. Under the empty grid it carries the dialog's
    usability and not merely its completeness: every one of the three fills
    the grid, so an outcome that stayed away leaves a dialog in which no relic
    can be chosen at all, for ever, with no error anywhere.

    One list for all three signals, because the claim is about their sum: two
    outcomes are as wrong as none, and three counters would each be right
    while the sum was two. The one way out that says nothing at all is the
    window closing, and it is in the same table because "nothing" is a value
    of the same measurement, not a case that was left out.
    """
    drive, expected = WAYS_A_QUESTION_ENDS[way]
    track, seen = drive(qapp, question)
    try:
        assert seen.names == expected, (
            f"a question that ended by '{way}' was answered with "
            f"{seen.names} and not with {expected}; exactly one of ready, "
            f"failed and stopped is what the window is built on -- and after "
            f"`shutdown` there is nobody left to hear any of them "
            f"(AK-218, Nachtrag X-0)")
    finally:
        track.shutdown()


# --- W7: the answer carries the generation it was asked under --------------

def test_w7_an_answer_that_stamps_nothing_still_arrives_stamped(qapp,
                                                                question):
    """T-130's fault, as a guard: the way was wired and did nothing.

    `run.slot_pool` hands back what `candidates.pool` built, and the pre-sort
    knows nothing about controllers, threads or windows -- so the pool carries
    `generation = 0`. The stamping is `_Worker.work`'s, and it is the one
    place that knows the question and the answer at once. Take it out and
    `_on_ready` judges **every** picker answer overtaken and drops it without
    a word: no error, no log line, a dialog that waits for ever.

    The answer function here stamps nothing on purpose, and the case says so
    before it asserts anything -- an answer function that stamped itself would
    make this guard green whatever the worker did (L-008b).

    Two questions rather than one, and the cache is emptied between them: a
    hit is stamped by `ResultCache.get` on its way out and would pass this
    guard with the worker's stamping gone.
    """
    inventory, _problem, ctx, request = question
    handed_back: list[types.SlotPool] = []

    def unstamped(req, *_rest):
        pool = types.SlotPool(slot_index=0, rank_by=req.goal_id)
        handed_back.append(pool)
        return pool

    cache = advisor_run.ResultCache(worker.PICKER_CACHE_SIZE)
    track = a_bare_track(unstamped, cache=cache)
    seen = picker_track.Outcomes(track)
    try:
        first = track.ask(request, inventory, ctx)
        assert picker_track.spin(qapp, lambda: seen.names == ["ready"]), (
            f"the first answer never reached the window ({seen.names}): an "
            f"answer whose generation is not stamped is judged overtaken and "
            f"dropped without a word")
        cache.clear()
        second = track.ask(request, inventory, ctx)
        assert picker_track.spin(qapp, lambda: seen.names == ["ready",
                                                             "ready"]), (
            f"the second answer never reached the window ({seen.names})")

        assert [pool.generation for pool in handed_back] == [0, 0], (
            "the answer function stamped the generation itself, so this "
            "guard would be green with the worker's stamping gone")
        assert second > first >= 1
        assert [payload.generation for name, payload in seen.signals
                if name == "ready"] == [first, second], (
            "the answers did not come back carrying the generation they were "
            "asked under, so the window has no way to know whose they are")
    finally:
        track.shutdown()


# --- W8: every way into the track has a row, and the row says what is shown -

#: The one method that turns an asking into a `Question`, and the reason a
#: way *into* the track can be counted at all: `ask` and
#: `ask_and_answer_if_known` both go through it (`worker.py`, `_question_from`,
#: "one place for both ways of asking"), and a third way in would have to as
#: well or it could not raise the generation, freeze the inventory or build
#: the cache key.
THE_ONE_PLACE_A_QUESTION_IS_BUILT = "_question_from"

#: The two ways an answer can get from the track to the dialog. Named rather
#: than spelled out at each use, because the whole of AK-218 Fassung 2 is that
#: these two look the same on screen at the end and are told apart by what the
#: player saw on the way there.
BY_RETURN_VALUE = "the answer comes back as the return value"
BY_SIGNAL = "the answer comes back as one of the three signals"

#: What the failing opening's answer function says it could not do. Stated
#: here so that the reason the dialog draws is the reason the track was given
#: and not a second spelling of it in the same file.
BROKEN_RUN = "the dataset lost a curve"

#: **Every way into the track, and how an answer can come back from it.**
#:
#: This is the table Nachtrag X-2 chose for the interrupting places, in the
#: form the `ui-ux-designer` asked for in AK-218 Fassung 2 (§3.5): a way in
#: per row, what the surface then shows beside it, and set equality in
#: **both** directions against the source. A third way in without a row here
#: turns W8 red -- which is the point of the guard: `ask_and_answer_if_known`
#: was built on the U5b day, AK-218 Fassung 1 counted the three signals and
#: never grew a row for it, and the criterion was wrong about the commonest
#: opening there is (30 % of them, S11-F) from that day until T-135 found it.
#:
#: The expectation is what stands here, never what `worker.py` says (L-008b).
WAYS_INTO_THE_TRACK = {
    "ask": (
        frozenset({BY_SIGNAL}),
        "the question always runs: the counter goes up, the debounce starts, "
        "and the answer arrives on `ready`, `failed` or `stopped`. This is "
        "the Advisor bar's way in; the picker reaches it through the miss "
        "branch of the other one.",
    ),
    "ask_and_answer_if_known": (
        frozenset({BY_RETURN_VALUE, BY_SIGNAL}),
        "a hit hands the answer straight back and emits nothing (Nachtrag "
        "IX-1.3); a miss leaves the question waiting exactly as `ask` does, "
        "so this way in can end either way and both are driven below.",
    ),
}


def asking_methods_of_the_controller() -> set[str]:
    """Every method of `AdvisorController` that starts a question.

    Off the syntax tree rather than out of a text search: a method that got
    hold of `_question_from` under an alias, or called it inside a nested
    function, would be a way in that a search for `def ask` never sees. What
    is counted is the *calls*, so a method that merely names it in a docstring
    is not one of them.
    """
    source = (REPO / "nrplanner" / "advisor" / "worker.py").read_text(
        encoding="utf-8")
    controller = next(
        node for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ClassDef) and node.name == "AdvisorController")
    return {
        method.name
        for method in controller.body
        if isinstance(method, ast.FunctionDef)
        for call in ast.walk(method)
        if isinstance(call, ast.Call)
        and isinstance(call.func, ast.Attribute)
        and call.func.attr == THE_ONE_PLACE_A_QUESTION_IS_BUILT}


def test_w8_every_way_into_the_track_has_a_row_and_every_row_a_way_in():
    """AK-218 Fassung 2 (§3.5), and the fault it was written after.

    The criterion is not "the three signals fill the grid" -- that counts the
    **wiring**, and it goes red at a cache hit, which is the opening the
    player likes best. It is "an end after which the grid stays empty is a
    fault", and the ways an end can be reached grow with the code. So they are
    counted: set equality against `worker.py` in both directions, and each row
    states what the surface shows below.

    What this cannot do is named in Nachtrag X-2 and holds here too: it sees
    the ways that exist, never the absence of one nobody has written. What it
    does see is the day one is added without a decision about what the player
    then has in front of them.
    """
    found = asking_methods_of_the_controller()

    assert found == set(WAYS_INTO_THE_TRACK), (
        f"the ways into the track are {sorted(found)} and this table knows "
        f"{sorted(WAYS_INTO_THE_TRACK)}. A way in without a row is a way for "
        f"which nobody said what the player sees (AK-218 Fassung 2); a row "
        f"without a way in is a rule about a method that has gone")


def test_w8_both_ways_back_are_driven_by_an_opening():
    """The other set equality: no way back is named and left undriven.

    The table above says which ways back each way in can take; the openings
    below say what each way back puts on the screen. If the two sets came
    apart -- a way back named and never opened, or an opening for a way back
    the table does not know -- the guard would look complete and cover less
    than it claims.
    """
    named = {way for ways, _why in WAYS_INTO_THE_TRACK.values()
             for way in ways}

    assert named == set(WHAT_THE_SURFACE_SHOWS), (
        f"the table names the ways back {sorted(named)} and there are "
        f"openings for {sorted(WHAT_THE_SURFACE_SHOWS)}")


def values_on(card) -> list[str]:
    """The two value rows of one card, as they read."""
    return [label.text() for label in card.block.values]


def _the_answer_is_there_at_once(slot, qapp):
    """Way (b), `ready`: the question ran and the pool came back."""
    track, answers = picker_track.a_track([picker_track.pool_for(slot)])
    dialog = picker_track.picker_over(slot, track)
    assert picker_track.spin(qapp, lambda: not dialog.waiting), (
        "no answer arrived, so this opening never reached the state it is "
        "named after")
    return track, answers, dialog


def _the_answer_fails(slot, qapp):
    """Way (b), `failed`: the run could not be finished."""
    track, answers = picker_track.a_track([picker_track.pool_for(slot)],
                                          raises=BROKEN_RUN)
    dialog = picker_track.picker_over(slot, track)
    assert picker_track.spin(qapp, lambda: not dialog.waiting), (
        "the failure never reached the dialog")
    return track, answers, dialog


def _the_search_is_stopped(slot, qapp):
    """Way (b), `stopped`: the question was abandoned while it was out."""
    track, answers = picker_track.a_track([picker_track.pool_for(slot)],
                                          hold=True)
    dialog = picker_track.picker_over(slot, track)
    assert picker_track.spin(qapp, lambda: answers.calls == 1), (
        "the run never started, so there was nothing to stop")
    assert track.cancel() is True, "there was nothing running to stop"
    answers.release()
    picker_track.spin(qapp, lambda: not dialog.waiting)
    return track, answers, dialog


def _the_answer_was_already_known(slot, qapp):
    """Way (a): the same slot opened a second time over the same track.

    The first opening is closed before the second is built, exactly as a
    player closes one dialog and opens another, and nothing between them
    changes the build -- so the second asking is the same request as the
    first, the generation being the one field the cache key leaves out
    (`advisor/run.py`, `cache_key`).

    **The dialog handed back is the second one, and the event loop has not
    been turned since it was built**: everything the caller reads on it is the
    first paint.
    """
    track, answers = picker_track.a_track([picker_track.pool_for(slot)])
    first = picker_track.picker_over(slot, track)
    assert picker_track.spin(qapp, lambda: not first.waiting), (
        "the first opening never got its answer, so there would be nothing "
        "in the cache for the second to hit")
    first.done(0)
    first.deleteLater()
    return track, answers, picker_track.picker_over(slot, track)


def _a_grid_with_figures(dialog) -> None:
    """What `ready` and a hit both leave standing (AK-218 (a) and (b))."""
    cards = picker_track.cards_in(dialog)
    assert cards, "the grid is empty after an answer that carried figures"
    assert relicpicker.NOTHING_YET not in area_labels(dialog)
    assert any(card.chip.text() for card in cards), (
        "no card carries the mark, so nothing was read out of the pool")
    assert any(values_on(card) != [relicpicker.NO_FIGURE] * 2
               for card in cards), (
        "every card says the no-figure dash, which is the state for an answer "
        "that carried no figures at all (AK-49), not for one that did")
    assert not dialog.headline.isVisibleTo(dialog), (
        "the header stands in for a mark nobody may wear, and this grid has "
        "its marks")


def _a_grid_without_figures(dialog, reason: str) -> None:
    """What `failed` and `stopped` leave standing (AK-208, AK-218 (b))."""
    cards = picker_track.cards_in(dialog)
    assert cards, (
        "the grid is empty after an outcome that had no figures to show, and "
        "a dialog in which no relic can be chosen is what AK-218 forbids")
    assert relicpicker.NOTHING_YET not in area_labels(dialog)
    assert dialog.headline.isVisibleTo(dialog)
    assert dialog.headline.text() == relicpicker.could_not_work_out(reason)
    for card in cards:
        assert values_on(card) == [relicpicker.NO_FIGURE] * 2
        assert card.chip.text() == ""


def _shows_a_filled_grid(dialog, _answers) -> None:
    _a_grid_with_figures(dialog)


def _shows_the_reason_it_could_not(dialog, _answers) -> None:
    _a_grid_without_figures(dialog, BROKEN_RUN)


def _shows_that_the_search_was_stopped(dialog, _answers) -> None:
    _a_grid_without_figures(dialog, relicpicker.SEARCH_WAS_STOPPED)


def _shows_the_grid_in_the_first_paint(dialog, answers) -> None:
    """Way (a), and the two beliefs that tell it from way (b) (§3.2).

    A second opening that **missed** the cache ends up looking exactly like
    one that hit it -- the same cards, the same figures, one paint later. A
    case that read only the end state would be green without ever driving the
    way it is named after. So both of the `ui-ux-designer`'s positive controls
    are here, and neither reads a clock:

    * the track computed **once** over the two openings, so the second answer
      was not worked out again;
    * the cards are standing **before** the event loop has been turned at all
      -- this is the first paint, and the waiting line was never in it.
    """
    assert answers.calls == 1, (
        f"the track computed {answers.calls} times over two openings of the "
        f"same slot, so the second opening missed the cache and this case is "
        f"not driving way (a) at all (AK-218 Fassung 2 (§3.3))")
    assert not dialog.waiting, (
        "the answer was known and the dialog waited for it anyway")
    _a_grid_with_figures(dialog)


#: Each way back, the openings that reach it, and what stands in the scroll
#: area afterwards. **Counted is what stands there, never which signal
#: flowed** -- the whole of AK-218 Fassung 2 (§3.1).
WHAT_THE_SURFACE_SHOWS = {
    BY_SIGNAL: {
        "the answer is there at once": (_the_answer_is_there_at_once,
                                        _shows_a_filled_grid),
        "the answer fails": (_the_answer_fails,
                             _shows_the_reason_it_could_not),
        "the search is stopped": (_the_search_is_stopped,
                                  _shows_that_the_search_was_stopped),
    },
    BY_RETURN_VALUE: {
        "the answer was already known": (_the_answer_was_already_known,
                                         _shows_the_grid_in_the_first_paint),
    },
}


@pytest.mark.parametrize(
    "way_back,opening",
    [(way_back, opening)
     for way_back, openings in sorted(WHAT_THE_SURFACE_SHOWS.items())
     for opening in sorted(openings)],
    ids=lambda part: part)
def test_w8_every_way_back_leaves_cards_to_choose_from(a_track_to_ask, qapp,
                                                       way_back, opening):
    """AK-218 Fassung 2: an end after which the grid stays empty is a fault.

    Four openings, two ways back, one claim: whatever the way, the player is
    left with cards to choose from -- with figures where there were figures,
    with the no-figure dash and a sentence where there were none, and never
    with the waiting line still standing.

    No wall clock anywhere (§3.4): where the event loop is turned it is turned
    *until a state holds*, the fuse in `spin` is asserted on by nobody, and
    the opening for way (a) does not turn it at all.
    """
    drive, shows = WHAT_THE_SURFACE_SHOWS[way_back][opening]
    slot, = picker_track.slots_that_offer_relics(a_track_to_ask, 1)
    track, answers, dialog = drive(slot, qapp)
    try:
        shows(dialog, answers)
    finally:
        answers.release()
        dialog.done(0)
        dialog.deleteLater()
        track.shutdown()


# --- W9: every place that interrupts a run says what the question hears -----

#: The private method every interruption of a running worker goes through
#: (`worker.py`, "ask the search to stop, and the thread to end when it has").
#: Counting its call sites is what makes the places countable at all: a place
#: that stopped a run without it would have to reach into the thread itself.
THE_INTERRUPTING_CALL = "_interrupt_the_running_worker"

#: The four things the outgoing question can hear, named rather than spelled
#: out in each row. Nachtrag X-2 states three of them as the rule -- send one
#: of the three exits in this same call, or ask a successor question in this
#: same call that will send one, or end the track -- and its own table adds
#: the fourth, the cache hit that answered by return value (IX-1.3). Prose
#: and table part company there, and the table is what is binding.
STOPPED_IN_THE_SAME_CALL = "`stopped`, in this same call"
THE_SUCCESSOR_QUESTION_WILL_ANSWER = (
    "nothing here: the successor question is the current one now and ends "
    "in exactly one of the three")
THE_RETURN_VALUE_ALREADY_ANSWERED = (
    "nothing here: the answer went back as the return value of this same "
    "call")
NOTHING_HERE_AND_NOTHING_AFTER = "nothing here, and nothing after it"

#: **Every place that interrupts a running worker, and what the outgoing
#: question hears.** Nachtrag X-2, in the same form as W1 above: the places
#: are read off the syntax tree of `worker.py` and compared against this
#: table, set equality in both directions, and the expectation is what stands
#: here -- never what the watched file says (L-008b).
#:
#: **Why a table and not a sentence.** The promise this replaces was prose:
#: "it holds over three callers". That says something about the *complement*
#: of a set of call sites -- that no fourth one interrupts in silence -- and
#: no case that can be played shows the absence of a place nobody has
#: written. The evidence is the sentence itself: it was written with "three"
#: on 08.09.2026 while the fourth place had stood in the same file since
#: `1a2cc5b` of that morning. What can be watched is the table: the day a
#: fifth place is added, somebody has to write down what the question it
#: interrupts is going to hear, and that line is exactly the thought that was
#: missing.
INTERRUPTING_PLACES = {
    "AdvisorController.cancel": (
        STOPPED_IN_THE_SAME_CALL,
        "AK-11: the window says 4.5 within microseconds, however long the "
        "worker takes to notice",
    ),
    "AdvisorController._wait_for": (
        THE_SUCCESSOR_QUESTION_WILL_ANSWER,
        "the caller is asking something else; the run being interrupted is "
        "the one whose answer nobody wants any more",
    ),
    "AdvisorController.ask_and_answer_if_known": (
        THE_RETURN_VALUE_ALREADY_ANSWERED,
        "the hit branch, and the commonest opening there is (30 % of them, "
        "S11-F): no `ready`, no `started`, nothing begun (IX-1.3)",
    ),
    "AdvisorController.shutdown": (
        NOTHING_HERE_AND_NOTHING_AFTER,
        "the window is closing and there is nobody left to read a sentence; "
        "the generation goes up first so a late answer is silent too (X-1)",
    ),
}


def _named_scopes(node, prefix: str = ""):
    """Every function in the tree under the name a reader would call it by."""
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name = f"{prefix}{child.name}"
            yield name, child
            yield from _named_scopes(child, f"{name}.")
        elif isinstance(child, ast.ClassDef):
            yield from _named_scopes(child, f"{prefix}{child.name}.")
        else:
            yield from _named_scopes(child, prefix)


def _calls_of_this_scope(node, attribute: str) -> int:
    """How often one method is called here, not counting nested functions.

    Nested functions are counted under their own name by `_named_scopes`, so
    walking into them here would count one call site twice.
    """
    found = 0
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef,
                              ast.ClassDef)):
            continue
        if (isinstance(child, ast.Call)
                and isinstance(child.func, ast.Attribute)
                and child.func.attr == attribute):
            found += 1
        found += _calls_of_this_scope(child, attribute)
    return found


def places_that_interrupt_a_running_worker() -> dict[str, int]:
    """Every place in `worker.py` that interrupts a run, and how often.

    Off the syntax tree and over the whole file, not over one class: a place
    put in a second class, in a module-level function or in a nested one
    would interrupt just as effectively, and a walk that only knew
    `AdvisorController` would report the table as kept.
    """
    tree = ast.parse((REPO / "nrplanner" / "advisor" / "worker.py").read_text(
        encoding="utf-8"))
    found = {name: _calls_of_this_scope(scope, THE_INTERRUPTING_CALL)
             for name, scope in _named_scopes(tree)}
    found["<module>"] = _calls_of_this_scope(tree, THE_INTERRUPTING_CALL)
    return {name: count for name, count in found.items() if count}


def test_w9_every_interrupting_place_has_a_row_and_every_row_a_place():
    """AD-028 W9 (Nachtrag X-2): the interrupting places are counted and named.

    The binding promise is not a number of callers but this: *every place
    that interrupts a running worker says what the outgoing question hears* --
    either it sends one of the three exits in the same call, or it asks a
    successor question in the same call that will send one, or it ends the
    track for good.

    What this guard cannot do, and X-2 says so in as many words: it sees the
    places that exist, never the absence of one nobody has written. What it
    does see is the day one is added without a decision about what the
    question it cut off is going to hear.

    It watches the count and the names, not the behaviour. That `cancel`
    really sends `stopped` is held by AD-028 W6; that the successor question
    really answers is held by AD-028 W6 and W3. W9 is the guard over those
    two being **complete** -- the gap "three callers" could not close.
    """
    found = places_that_interrupt_a_running_worker()

    assert set(found) == set(INTERRUPTING_PLACES), (
        f"a running worker is interrupted in {sorted(found)} (counted: "
        f"{found}) and this table knows {sorted(INTERRUPTING_PLACES)}. A "
        f"place without a row cuts a question off without anybody having "
        f"said what the player then waits for; a row without a place is a "
        f"rule about code that has gone")
