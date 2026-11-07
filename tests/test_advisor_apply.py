"""Applying an answer, taking it back, and the three controls that ask for it.

**The slots are the measurement, never the button.** What `Apply all`, `Use`
and `Undo apply` are worth is what is in the six slots afterwards, so every
case here reads the slots through `saved_key()` -- the same string the stored
build is written from. Reading the caption of a card would agree with a
display that drew the right name over the wrong relic, and two copies of one
roll carry the same name (QA-021).

**The answers are built here.** A real run is a second thing under test and
cannot be asked for the awkward case: an answer naming a copy the save does
not own, an answer for a slot this vessel does not have. Both are states the
applying has to survive, and neither is reachable by pressing `Optimize`.
The one case that does drive the real search is at the foot of the file, and
it is the only one that can show that what the window applies is what a run
really hands it.
"""

from __future__ import annotations

import dataclasses
import html

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton

from nrplanner import advisorbar, advisorblock, chalices, effectfilters, inventory
from nrplanner import app as appmod
from nrplanner.advisor import candidates, goals, run, types
from tests import relics
from tests.advisor_row_at_the_window import AK_350_ROOMS


# --- the answers the cases apply -------------------------------------------

def a_group(slot: int, relic: str) -> types.SlotReasons:
    return types.SlotReasons(slot_index=slot, relic_name=relic,
                             effects_total=1, effects_with_a_figure=1,
                             count_line="1 of its 1 effects moved a number "
                                        "in this build.",
                             lines=(types.ReasonLine(
                                 slot_index=slot, effect_id=1,
                                 text=f"{relic}: Physical Attack +1"),))


def an_answer_for(pairs) -> types.AdvisorResult:
    """One answer offering these (slot index, owned copy) pairs."""
    choices = tuple(types.SlotChoice(slot_index=index, handle=copy.handle,
                                     relic_id=copy.relic_id, name=copy.name)
                    for index, copy in pairs)
    reasons = tuple(a_group(index, copy.name) for index, copy in pairs)
    return types.AdvisorResult(
        goal_id="max_damage", goal_label="Maximise damage",
        suggestions=(types.Suggestion(
            choices=choices,
            score=types.GoalScore(value=1.0, display="1", unit=""),
            reasons=reasons),))


def an_answer_with_no_suggestion() -> types.AdvisorResult:
    """4.10's shape: an answer that could not be ranked at all."""
    return types.AdvisorResult(goal_id="max_damage",
                               goal_label="Maximise damage")


def keys_of(planner) -> list[str]:
    """What every slot holds, as the stored build would write it down."""
    return [slot.saved_key()
            for slot in list(planner.base_slots) + list(planner.deep_slots)]


def two_offers(planner):
    """Two (slot index, owned copy) pairs the current vessel can really take.

    Real copies out of the player's own save and two different physical
    relics, because applying both at once is what `Apply all` does and two
    slots given one copy is the loss QA-021 records.
    """
    cards = planner.active_slots()
    taken: set = set()
    offers = []
    for index, card in enumerate(cards):
        for copy in card._holdable():
            key = inventory.copy_key(copy)
            if copy.handle is not None and key not in taken:
                taken.add(key)
                offers.append((index, copy))
                break
        if len(offers) == 2:
            return offers
    pytest.skip("this save cannot fill two slots of this vessel")


def a_live_answer(planner, answer):
    """Put an answer on screen the way a finished run does."""
    planner.advisor_bar._answer = answer
    planner.advisor_bar._show(advisorbar.Situation(
        advisorbar.State.SUGGESTED, goal_label="Maximise damage",
        slots=len(planner.active_slots()),
        slots_filled=len(answer.suggestions[0].choices)
        if answer.suggestions else 0))
    planner.show_the_suggestion(answer)
    return answer


# --- the controls of the row ------------------------------------------------

def visible_actions(bar) -> list[str]:
    """The captions of the row's action buttons -- `Optimize` and `Filters`
    excluded, the latter standing outside AK-07's budget (AK-302)."""
    return [button.text() for button in bar.findChildren(QPushButton)
            if button not in (bar.optimize_button, bar.filters_button)
            and not button.isHidden()]


def a_bare_bar(qapp, filled: int = 6):
    """A row with an answer on it and no window behind it."""
    problem = types.SlotProblem(slots=tuple(
        types.Slot(index=index, colour=1, deep=False) for index in range(6)))
    asking = advisorbar.Asking(
        request=types.AdvisorRequest(
            hero_id=1, level=15, problem=problem, goal_id="max_damage",
            weighting_id=goals.DEFAULT_WEIGHTING.id),
        inventory=object(),
        ctx=types.GoalContext(data={}, hero={"id": 1, "name": "Wylder"},
                              level=15, reference=None,
                              weighting=goals.DEFAULT_WEIGHTING),
        nightfarer="Wylder", relics=1)
    return advisorbar.AdvisorBar(lambda goal_id: asking)


def test_a_row_with_no_answer_offers_no_action_at_all(qapp):
    """§3.1, first case: no suggestion, no action buttons."""
    bar = a_bare_bar(qapp)
    try:
        assert visible_actions(bar) == []
    finally:
        bar.deleteLater()


def test_a_living_answer_offers_the_three_of_the_section(qapp):
    """§3.1, second case: `Apply all`, `Why`, `Clear`, in that order."""
    bar = a_bare_bar(qapp)
    try:
        bar._answer = an_answer_for([])
        bar._answer = types.AdvisorResult(
            goal_id="max_damage", goal_label="Maximise damage",
            suggestions=(types.Suggestion(
                choices=(types.SlotChoice(slot_index=0, handle=7, relic_id=1,
                                          name="X"),),
                score=types.GoalScore(value=1.0, display="1", unit="")),))
        bar._show(advisorbar.Situation(advisorbar.State.SUGGESTED,
                                       goal_label="Maximise damage",
                                       slots=6, slots_filled=1))
        assert visible_actions(bar) == ["Apply all", "Why", "Clear"]
    finally:
        bar.deleteLater()


def test_an_applied_answer_offers_undo_in_the_same_place(qapp):
    """§3.1, third case, and 4.13: `Apply all` becomes `Undo apply`."""
    bar = a_bare_bar(qapp)
    try:
        bar._answer = types.AdvisorResult(
            goal_id="max_damage", goal_label="Maximise damage",
            suggestions=(types.Suggestion(
                choices=(types.SlotChoice(slot_index=0, handle=7, relic_id=1,
                                          name="X"),),
                score=types.GoalScore(value=1.0, display="1", unit="")),))
        bar._show(advisorbar.Situation(advisorbar.State.SUGGESTED,
                                       goal_label="Maximise damage",
                                       slots=6, slots_filled=1))
        bar.the_suggestion_was_applied()
        assert bar.status.accessibleName() == (
            "Applied. Undo puts your slots back as they were.")
        assert visible_actions(bar) == ["Undo apply", "Why", "Clear"]

        bar.the_suggestion_was_undone()
        assert bar.status.accessibleName() == (
            "Maximise damage — 1 of 6 slots filled.")
        assert visible_actions(bar) == ["Apply all", "Why", "Clear"]
    finally:
        bar.deleteLater()


def test_never_a_fourth_action_in_any_state_of_the_row(qapp):
    """AK-07, over every state of §4 rather than over the busiest one.

    A row that keeps to three in the state a case remembered to name can
    still show four in the one it did not: 4.13 arrives from a state that
    already had three, and a caption that was swapped rather than a button
    that was hidden would be a fourth control the moment `Undo apply` is a
    button of its own.
    """
    bar = a_bare_bar(qapp)
    try:
        answer = types.AdvisorResult(
            goal_id="max_damage", goal_label="Maximise damage",
            suggestions=(types.Suggestion(
                choices=(types.SlotChoice(slot_index=0, handle=7, relic_id=1,
                                          name="X"),),
                score=types.GoalScore(value=1.0, display="1", unit="")),))
        for state in advisorbar.State:
            bar._answer = answer
            bar._show(advisorbar.Situation(state, goal_label="Maximise damage",
                                           slots=6, slots_filled=1,
                                           nightfarer="Wylder", reason="x"))
            shown = visible_actions(bar)
            assert len(shown) <= 3, f"{state} shows {shown}"
    finally:
        bar.deleteLater()


def test_the_why_button_is_what_asks_for_the_dialog(qapp):
    """The half T-089 built without a sender: §3.1's `Why`."""
    bar = a_bare_bar(qapp)
    try:
        asked = []
        bar.why_requested.connect(lambda: asked.append(True))
        bar.why_button.click()
        assert asked == [True]
    finally:
        bar.deleteLater()


def test_the_one_button_asks_for_whichever_action_the_state_names(qapp):
    """`Apply all` and `Undo apply` are one control and two requests."""
    bar = a_bare_bar(qapp)
    try:
        applies, undoes = [], []
        bar.apply_all_requested.connect(lambda: applies.append(True))
        bar.undo_apply_requested.connect(lambda: undoes.append(True))
        bar._answer = types.AdvisorResult(
            goal_id="max_damage", goal_label="Maximise damage",
            suggestions=(types.Suggestion(
                choices=(types.SlotChoice(slot_index=0, handle=7, relic_id=1,
                                          name="X"),),
                score=types.GoalScore(value=1.0, display="1", unit="")),))
        bar._show(advisorbar.Situation(advisorbar.State.SUGGESTED,
                                       goal_label="Maximise damage",
                                       slots=6, slots_filled=1))
        bar.apply_button.click()
        assert (applies, undoes) == ([True], [])

        bar.the_suggestion_was_applied()
        bar.apply_button.click()
        assert (applies, undoes) == ([True], [True])
    finally:
        bar.deleteLater()


def test_an_answer_that_could_not_be_ranked_offers_nothing_to_apply(qapp):
    """4.10 carries no suggestion, so `Apply all` has no work to do.

    `Why` stays, because the table says 4.10 explains itself at length.
    """
    bar = a_bare_bar(qapp)
    try:
        bar._answer = an_answer_with_no_suggestion()
        bar._show(advisorbar.Situation(advisorbar.State.NOT_RANKABLE,
                                       nightfarer="Wylder"))
        assert visible_actions(bar) == ["Why", "Clear"]
    finally:
        bar.deleteLater()


# --- what applying does to the slots ---------------------------------------

def test_apply_all_puts_every_suggested_copy_in_its_slot(planner):
    """AK-14: the slots hold what the answer named, by handle.

    By handle and not by name, because a name is not an identity here: this
    save owns two copies of one roll and the second is only reachable by its
    handle (QA-021).
    """
    offers = two_offers(planner)
    a_live_answer(planner, an_answer_for(offers))

    planner.apply_all()

    keys = keys_of(planner)
    for index, copy in offers:
        assert keys[index] == chalices.slot_key(copy)
        assert planner.active_slots()[index].current_relic().handle == (
            copy.handle)


def test_apply_all_leaves_the_stored_build_holding_what_it_applied(planner):
    """AK-14's second half: persistence per chalice, the picker's own way.

    The state after applying is the state choosing the relics one at a time
    would have left, and what makes that testable is that this window writes
    the chalice down on every change: the stored build is read back here.
    """
    offers = two_offers(planner)
    a_live_answer(planner, an_answer_for(offers))

    planner.apply_all()

    vessel = planner.current_vessel()
    stored_keys = chalices.load(planner.current_hero()["id"], vessel["id"])[2]
    for index, copy in offers:
        assert stored_keys[index] == chalices.slot_key(copy)


def test_use_applies_this_slot_and_leaves_the_others_alone(planner):
    """§3.2: `Use` is about one slot, and the answer names more than one."""
    offers = two_offers(planner)
    a_live_answer(planner, an_answer_for(offers))
    before = keys_of(planner)

    cards = planner.active_slots()
    cards[offers[0][0]].suggestion.use_button.click()

    keys = keys_of(planner)
    assert keys[offers[0][0]] == chalices.slot_key(offers[0][1])
    assert keys[offers[1][0]] == before[offers[1][0]]


def test_undo_puts_a_slot_that_was_empty_back_to_empty(planner):
    """AK-15, first of the three shapes the criterion names.

    The one that a restore written in relics rather than in keys gets wrong:
    there is no relic to put back, and "put nothing back" has to be a thing
    the mechanism can express.
    """
    offers = two_offers(planner)
    cards = planner.active_slots()
    for index, _copy in offers:
        cards[index].clear_relic()
    before = keys_of(planner)
    assert [before[index] for index, _ in offers] == ["", ""], (
        "the slots were not empty to begin with, so this case would pass "
        "whatever undo did")
    a_live_answer(planner, an_answer_for(offers))

    planner.apply_all()
    assert keys_of(planner) != before
    planner.undo_apply()

    assert keys_of(planner) == before


def test_undo_puts_a_custom_relic_back_where_it_was(planner):
    """AK-15, second shape: a relic nobody owns and no list can offer.

    A custom relic survives a restore only by being built again out of what
    was written down (QA-025), which is exactly what makes it the case that
    tells an undo written in keys from one written in relics.
    """
    offers = two_offers(planner)
    index = offers[0][0]
    card = planner.active_slots()[index]
    effects = [effect["id"] for effect in card.rollable_effects()[:2]]
    if len(effects) < 2:
        pytest.skip("this slot colour has fewer than two rollable effects")
    card.set_custom(effects)
    before = keys_of(planner)
    assert card.current_relic() is card.custom_item
    a_live_answer(planner, an_answer_for(offers))

    planner.apply_all()
    assert planner.active_slots()[index].current_relic() is not card.custom_item
    planner.undo_apply()

    assert keys_of(planner) == before
    back = planner.active_slots()[index].current_relic()
    assert back is not None
    assert back.relic_id == inventory.CUSTOM_RELIC_ID
    assert list(back.effect_ids) == effects


def test_undo_puts_an_occupied_slot_back_to_its_own_copy(planner):
    """AK-15, third shape: a relic that was there and has to come back."""
    offers = two_offers(planner)
    first, second = offers
    cards = planner.active_slots()
    assert cards[first[0]].select_copy(second[1].handle) or True
    before = keys_of(planner)
    if before[first[0]] == "":
        pytest.skip("the slot could not be given a relic to lose")
    a_live_answer(planner, an_answer_for([first]))

    planner.apply_all()
    assert keys_of(planner)[first[0]] == chalices.slot_key(first[1])
    planner.undo_apply()

    assert keys_of(planner) == before


def test_undo_after_two_uses_takes_both_of_them_back(planner):
    """4.13 says `as they were`, and one button can only mean one moment.

    The moment is before the first applying of this answer, so a player who
    used two cards one after the other gets both slots back rather than the
    later one.
    """
    offers = two_offers(planner)
    a_live_answer(planner, an_answer_for(offers))
    before = keys_of(planner)

    cards = planner.active_slots()
    for index, _copy in offers:
        cards[index].suggestion.use_button.click()
    assert keys_of(planner) != before

    planner.undo_apply()
    assert keys_of(planner) == before


def test_the_row_says_applied_and_the_cards_say_already_equipped(planner):
    """4.13, and the block of an applied slot has nothing left to offer.

    Whether the suggestion is the copy in the slot is decided on the handle
    (QA-180, QA-021), so this is also what shows that the copy that arrived
    is the copy that was named.
    """
    offers = two_offers(planner)
    a_live_answer(planner, an_answer_for(offers))

    planner.apply_all()

    assert planner.advisor_bar.situation.state is advisorbar.State.APPLIED
    assert planner.advisor_bar.status.accessibleName() == (
        "Applied. Undo puts your slots back as they were.")
    for index, _copy in offers:
        block = planner.active_slots()[index].suggestion
        assert block.already_equipped.isVisibleTo(block)
        assert not block.use_button.isVisibleTo(block)


def test_applying_does_not_throw_its_own_answer_away(planner):
    """AK-12 is about the build changing under the player, not by them.

    Every change to the build ends in `recompute`, which tells the row the
    answer is stale -- so without the one exception the act of applying would
    drop the answer between the first slot and the second, and `Undo apply`
    would be gone before it could be pressed.
    """
    offers = two_offers(planner)
    answer = a_live_answer(planner, an_answer_for(offers))

    planner.apply_all()

    assert planner.advisor_bar.answer is answer
    assert planner.advisor_bar.situation.state is advisorbar.State.APPLIED


def test_a_change_of_the_build_after_applying_still_ends_the_answer(planner):
    """The exception is only the applying itself, and lasts only for it."""
    offers = two_offers(planner)
    a_live_answer(planner, an_answer_for(offers))
    planner.apply_all()

    planner.level_slider.setValue(planner.level_slider.value() + 1)

    assert planner.advisor_bar.answer is None
    assert planner.advisor_bar.situation.state is advisorbar.State.NOTHING_YET


def test_a_new_answer_makes_the_old_applying_unundoable(planner):
    """An answer that has been replaced cannot be undone into any more."""
    offers = two_offers(planner)
    a_live_answer(planner, an_answer_for(offers))
    planner.apply_all()
    applied = keys_of(planner)

    planner.advisor_bar.suggestion_changed.emit(None)
    planner.undo_apply()

    assert keys_of(planner) == applied


def test_a_choice_naming_a_copy_the_save_does_not_own_is_passed_over(planner):
    """AK-16 at the place it would otherwise become a relic in a slot.

    The window is the last stop: a choice whose handle is in no save is not
    guessed at by name, and the slot keeps what it had.
    """
    offers = two_offers(planner)
    index = offers[0][0]
    invented = types.SlotChoice(slot_index=index, handle=-1, relic_id=1,
                                name="A relic that was melted")
    answer = types.AdvisorResult(
        goal_id="max_damage", goal_label="Maximise damage",
        suggestions=(types.Suggestion(
            choices=(invented,),
            score=types.GoalScore(value=1.0, display="1", unit=""),
            reasons=(a_group(index, invented.name),)),))
    a_live_answer(planner, answer)
    before = keys_of(planner)

    planner.apply_all()

    assert keys_of(planner) == before
    assert planner.advisor_bar.situation.state is not advisorbar.State.APPLIED


def test_a_real_optimize_can_be_applied_and_taken_back(planner):
    """The whole road once, with the real controller and the real search.

    Everything above builds its own answer, which is right for the awkward
    cases and proves nothing about the shape a run really hands over. This is
    the one case that closes that gap: what `run.run` returns is applied, and
    the slots come back to where they started.
    """
    import time

    from PySide6.QtWidgets import QApplication

    bar = planner.advisor_bar
    before = keys_of(planner)
    bar.optimize_button.click()
    app = QApplication.instance()
    deadline = time.monotonic() + 30.0
    while (bar.situation.state in advisorbar.WORKING_STATES
           or bar.situation.state is advisorbar.State.NOTHING_YET):
        if time.monotonic() > deadline:
            pytest.fail("the run never finished")
        app.processEvents()
        time.sleep(0.005)
    if bar.answer is None or not bar.answer.suggestions:
        pytest.skip(f"the run ended in {bar.situation.state} with nothing to "
                    f"apply: {bar.status.accessibleName()!r}")

    planner.apply_all()
    applied = keys_of(planner)
    assert applied != before, (
        "the run suggested exactly what was already equipped, so this case "
        "would pass whatever apply did")
    assert bar.situation.state is advisorbar.State.APPLIED

    planner.undo_apply()
    assert keys_of(planner) == before
    bar.shutdown()


def test_at_the_opening_width_no_action_button_is_cut(
        advisor_row_at_the_window):
    """AK-05 for the three controls this task put in the row.

    The row's busiest state, measured at the derived opening width under
    the Windows platform (see `tests/advisor_row_at_the_window.py`). The
    opening width holds the row on one line (AK-401), so no caption at all
    is cut -- the boxes included, since T-334n (AK-399).
    """
    row = advisor_row_at_the_window["suggested"]
    actions = {"apply_button", "why_button", "clear_button"}
    assert actions <= set(row["on_screen"]), (
        "no action button is on screen, so this case would pass whatever "
        "the row's width did")
    assert row["cut"] == []


def test_at_1920_px_the_row_takes_two_lines_and_cuts_nothing(
        advisor_row_at_the_window):
    """AK-352 since T-334n: `room=1920` opens the window at AK-350's share
    of it, under the one-line need -- so the row stands on two lines, the
    boxes whole and the status line wide (AK-401), not 0 px with a box cut.
    """
    row = advisor_row_at_the_window["rooms"][str(AK_350_ROOMS[0])]
    assert row["width"] == round(AK_350_ROOMS[0]
                                 * appmod.OPENING_WIDTH_SCREEN_RATIO)
    assert row["lines"] == 2
    suggested = row["suggested"]
    assert suggested["cut"] == []
    assert suggested["status_width"] > 0
    assert html.escape(suggested["status_whole_text"]) in suggested[
        "row_tooltip"]


def test_at_2560_px_the_ratio_already_covers_the_need(
        advisor_row_at_the_window):
    """AK-352: `room=2560` puts AK-350's ratio (2304 px) over the row's need.

    The clamp in `_opening_width` caps it back to the need, the same as an
    uncapped screen -- one line (AK-401), nothing gives way in either state.
    """
    row = advisor_row_at_the_window["rooms"][str(AK_350_ROOMS[1])]
    assert row["width"] == advisor_row_at_the_window["width"]
    assert row["lines"] == 1
    for state in ("failed", "suggested"):
        assert row[state]["cut"] == [], (
            f"{state}: {row[state]['cut']}")


def test_a_slot_without_a_choice_shows_its_reason_on_the_card(planner):
    """AK-441: the one filled slot keeps its block, the empty one says why."""
    (index, copy), (other, _) = two_offers(planner)
    reason = "Every relic left for this slot is one you rejected."
    answer = dataclasses.replace(
        an_answer_for([(index, copy)]),
        empty_slots=(types.EmptySlot(other, types.EMPTY_REJECTED,
                                     line=reason),))

    a_live_answer(planner, answer)

    cards = planner.active_slots()
    assert cards[index].suggestion.empty_reason.isHidden()
    assert cards[other].suggestion.heading.text() == "NO SUGGESTION"
    assert cards[other].suggestion.empty_reason.text() == reason

    planner.show_the_suggestion(None)
    assert cards[other].suggestion.isHidden()


# --- a part-filled answer (AK-444) ------------------------------------------

def test_apply_all_leaves_a_slot_without_a_choice_as_it_was(planner):
    """AK-444: the one slot the answer names changes, the empty one keeps the
    relic the player put there, and `Undo apply` puts everything back."""
    offers = two_offers(planner)
    (kept_index, kept_copy), (named_index, named_copy) = offers
    planner._put_these_keys_in_the_slots([
        chalices.slot_key(kept_copy) if index == kept_index else key
        for index, key in enumerate(keys_of(planner))])
    answer = dataclasses.replace(
        an_answer_for([(named_index, named_copy)]),
        empty_slots=(types.EmptySlot(kept_index, types.EMPTY_NOTHING,
                                     line="Nothing."),))
    a_live_answer(planner, answer)
    before = keys_of(planner)

    planner.apply_all()

    keys = keys_of(planner)
    assert keys[kept_index] == before[kept_index] == chalices.slot_key(kept_copy)
    assert keys[named_index] == chalices.slot_key(named_copy)

    planner.undo_apply()
    assert keys_of(planner) == before


# --- X and `Reject` on the real window (AD-060, AD-061) ----------------------

class _NoRun:
    """A controller that answers nothing: the question is what is measured."""

    def __init__(self, bar, monkeypatch) -> None:
        self.asked = []
        monkeypatch.setattr(bar._controller, "ask", self.ask)

    def ask(self, request, inventory, ctx, debounce_ms=None) -> int:
        self.asked.append((request, debounce_ms))
        return len(self.asked)


def a_card_with_a_line(planner):
    """A live answer whose first card has a relic, a line and an X."""
    index, copy = two_offers(planner)[0]
    effect_id = copy.effect_ids[0]
    answer = an_answer_for([(index, copy)])
    group = dataclasses.replace(answer.suggestions[0].reasons[0], lines=(
        types.ReasonLine(slot_index=index, effect_id=effect_id, text="Line."),))
    answer = dataclasses.replace(answer, suggestions=(dataclasses.replace(
        answer.suggestions[0], reasons=(group,)),))
    a_live_answer(planner, answer)
    return planner.active_slots()[index], copy, effect_id, answer


def test_an_x_marks_the_effect_and_asks_again(planner, monkeypatch):
    """AK-424: the mark, one run at once, and the answer does not go (AK-425)
    though the mark says `changed`, and the block is locked meanwhile."""
    card, _copy, effect_id, answer = a_card_with_a_line(planner)
    run = _NoRun(planner.advisor_bar, monkeypatch)
    try:
        card.suggestion.drawn_lines[0].avoid.click()

        assert effect_id in planner.effect_filters.excluded
        assert planner.advisor_bar.answer is answer
        assert len(run.asked) == 1
        request, debounce = run.asked[0]
        assert debounce == 0
        assert effect_id in request.problem.excluded
        assert not card.suggestion.isEnabled()
        assert card.suggestion.isVisibleTo(card)
    finally:
        planner.effect_filters.mark(effect_id, None)


def test_a_mark_set_in_the_filter_window_starts_no_run(planner, monkeypatch):
    """AK-289, unchanged: only the block asks again."""
    _card, _copy, effect_id, _answer = a_card_with_a_line(planner)
    run = _NoRun(planner.advisor_bar, monkeypatch)
    try:
        planner.effect_filters.mark(effect_id, effectfilters.EXCLUDED)

        assert run.asked == []
        assert planner.advisor_bar.answer is None
    finally:
        planner.effect_filters.mark(effect_id, None)


def test_the_new_answer_unlocks_the_block_and_takes_the_focus(planner,
                                                              monkeypatch):
    """AK-426: back on the first X of the same slot, or on `Optimize`."""
    card, _copy, effect_id, answer = a_card_with_a_line(planner)
    _NoRun(planner.advisor_bar, monkeypatch)
    bar = planner.advisor_bar
    try:
        first = card.suggestion.first_x()
        first.setFocus()
        first.click()
        assert not card.suggestion.isEnabled()

        bar._asked = dataclasses.replace(bar._asked)
        bar._on_ready(answer)

        assert card.suggestion.isEnabled()
        assert planner.focusWidget() is card.suggestion.first_x()

        card.suggestion.first_x().setFocus()
        card.suggestion.first_x().click()
        bar._on_ready(dataclasses.replace(answer, suggestions=()))

        assert planner.focusWidget() is bar.optimize_button
    finally:
        planner.effect_filters.mark(effect_id, None)


def test_reject_is_for_this_build_only_and_goes_with_the_roll(planner,
                                                              monkeypatch):
    """AD-060: the question carries the roll, the store nothing; another
    vessel has no such rejection, and coming back brings it again (AK-428)."""
    card, copy, _effect_id, _answer = a_card_with_a_line(planner)
    run = _NoRun(planner.advisor_bar, monkeypatch)
    roll = types.roll_of(copy)

    card.suggestion.reject_button.click()

    assert run.asked[0][0].problem.rejected == frozenset({roll})
    assert run.asked[0][1] == 0
    assert not planner.rejected_list.isHidden()
    assert not card.suggestion.isEnabled()

    rows = [row for row in range(planner.chalice_list.count())
            if planner.chalice_list.item(row).data(Qt.UserRole) is not None]
    here = planner.chalice_list.currentRow()
    planner.chalice_list.setCurrentRow(next(row for row in rows if row != here))
    assert planner.rejected_rolls() == frozenset()
    assert planner.rejected_list.isHidden()
    planner.chalice_list.setCurrentRow(here)
    assert planner.rejected_rolls() == frozenset({roll})
    assert not planner.rejected_list.isHidden()

    planner.deep_check.toggle()
    assert planner.rejected_rolls() == frozenset({roll}), (
        "a rejection hangs on no slot, so Deep of Night does not part it "
        "from its build (AD-060.2)")
    planner.deep_check.toggle()
    planner._suggest_again(roll)


def test_suggest_again_gives_it_back_and_asks_if_an_answer_stands(planner,
                                                                  monkeypatch):
    """AK-430."""
    card, copy, _effect_id, answer = a_card_with_a_line(planner)
    run = _NoRun(planner.advisor_bar, monkeypatch)
    roll = types.roll_of(copy)
    card.suggestion.reject_button.click()
    planner.advisor_bar._on_ready(answer)
    asked = len(run.asked)

    planner.rejected_list.scroller.widget().findChild(QPushButton).click()

    assert planner.rejected_rolls() == frozenset()
    assert planner.rejected_list.isHidden()
    assert len(run.asked) == asked + 1
    assert run.asked[-1][0].problem.rejected == frozenset()


def test_suggest_again_with_no_answer_starts_nothing(planner, monkeypatch):
    run = _NoRun(planner.advisor_bar, monkeypatch)
    roll = (1, (2,), ())
    planner._rejects[planner._reject_key()] = {roll: "Urn"}
    planner._show_the_rejects()

    planner.rejected_list.suggest_again.emit(roll)

    assert run.asked == []
    assert planner.rejected_rolls() == frozenset()


def test_a_rejection_is_named_in_the_list_with_its_effects(planner):
    card, copy, _effect_id, _answer = a_card_with_a_line(planner)
    roll = types.roll_of(copy)
    planner._rejects[planner._reject_key()] = {roll: copy.name}
    try:
        planner._show_the_rejects()
        page = planner.rejected_list.scroller.widget()
        label = page.findChild(advisorbar._ElidingLabel)
        names = [advisorblock.effect_name(planner.effects, eid)
                 for eid in copy.effect_ids]
        assert label.accessibleName() == f"{copy.name} — {', '.join(names)}"
        assert page.findChild(QPushButton).text() == "Suggest again"
    finally:
        planner._rejects.clear()
        planner._show_the_rejects()


# --- the vessel list after a comparison (AK-431 to AK-436, AK-454) -----------

class _ToldRuns:
    """Runs that answer by the vessel's layout, later in the list is better.

    Told rather than searched: the figures are the claim, and a hit has to find
    its entry by the real key, which is what `Switch to it` depends on. Deep is
    on, where all 11 layouts differ (AD-062).
    """

    def __init__(self, planner, monkeypatch) -> None:
        self.calls = 0
        self.planner = planner
        planner.deep_check.setChecked(True)
        self.value_of = {
            run.vessel_slots(vessel, True): 100.0 + index
            for index, vessel in enumerate(planner.hero_vessels)}
        bar = planner.advisor_bar
        monkeypatch.setattr(bar._controller, "_answer", self)
        monkeypatch.setattr(bar.comparison._controller, "_answer", self)

    def __call__(self, request, _inventory, _ctx, _goals, _stop):
        self.calls += 1
        value = self.value_of[request.problem.slots]
        score = types.GoalScore(value=value, display=f"Attack rating {value:.0f}",
                                unit="AR")
        return types.AdvisorResult(
            goal_id=request.goal_id, goal_label="Maximise damage",
            suggestions=(types.Suggestion(choices=(), score=score),),
            held=request.problem.held)


def _spin_until(what, seconds: float = 20.0) -> None:
    import time

    from PySide6.QtWidgets import QApplication

    deadline = time.monotonic() + seconds
    while not what():
        assert time.monotonic() < deadline, "it never came"
        QApplication.instance().processEvents()
        time.sleep(0.002)


def _compared(planner) -> None:
    bar = planner.advisor_bar
    bar.optimize_button.click()
    _spin_until(lambda: bar.comparing is not None
                and bar.comparing.state is advisorbar.Compared.DONE)


def _row_of(planner, vessel_id: int) -> int:
    return next(row for row in range(planner.chalice_list.count())
                if (planner.chalice_list.item(row).data(Qt.UserRole) or {}
                    ).get("id") == vessel_id)


def _line_of(planner, vessel_id: int):
    return planner.chalice_list.item(_row_of(planner, vessel_id)).data(
        advisorbar.VESSEL_LINE_ROLE)


@pytest.fixture
def told(planner, monkeypatch):
    return _ToldRuns(planner, monkeypatch)


def test_the_comparison_arrives_on_the_list_and_nothing_moves(planner, told):
    """AK-431, AK-432, AK-433."""
    here = planner.current_vessel()
    bar = planner.advisor_bar
    bar.optimize_button.click()
    _spin_until(lambda: bar.answer is not None)
    answer_before = bar.answer
    _spin_until(lambda: bar.comparing.state is advisorbar.Compared.DONE)

    assert planner.current_vessel() == here
    assert bar.answer is answer_before
    best = planner.hero_vessels[-1]
    assert _line_of(planner, best["id"])[0].startswith("BEST  ")
    assert sum(bool(_line_of(planner, vessel["id"])[0])
               for vessel in planner.hero_vessels) == 1
    assert planner.compare_status.text().startswith(
        f"Best of {len(planner.hero_vessels)} for ")
    assert best["name"] in planner.compare_status.text()
    assert not planner.compare_status.isHidden()
    assert not planner.switch_button.isHidden()
    assert planner.switch_button.nextInFocusChain() is planner.chalice_list, (
        "AK-436: the button directly before the list")
    assert told.calls == len(planner.hero_vessels), (
        "the chosen vessel's question has to be a hit on its own answer")
    assert "Compared: " in planner.chalice_list.item(
        _row_of(planner, best["id"])).toolTip()
    assert ", best of " in planner.chalice_list.item(
        _row_of(planner, best["id"])).data(Qt.AccessibleTextRole)


def test_a_click_shows_the_answer_of_that_vessel_without_a_run(planner, told):
    """AK-435 (a), (c), and the status line follows the open row (AK-450)."""
    _compared(planner)
    calls = told.calls
    other = _another_vessel(planner)
    planner.chalice_list.setCurrentRow(_row_of(planner, other["id"]))

    answer = planner.advisor_bar.answer
    assert answer is not None
    assert answer.suggestions[0].score.value == told.value_of[
        run.vessel_slots(other, True)]
    assert told.calls == calls
    assert planner.advisor_bar.comparing.state is advisorbar.Compared.DONE
    assert "more than this one" in planner.compare_status.text()
    planner.chalice_list.setCurrentRow(_row_of(planner, planner.hero_vessels[-1]["id"]))
    assert planner.compare_status.text().startswith("This is the best of ")
    assert planner.switch_button.isHidden()


def test_a_switch_without_holds_opens_the_best_with_its_answer(planner, told):
    """AK-435 (b): two clicks, nothing to undo."""
    _compared(planner)
    assert planner.switch_button.toolTip() == (
        "Opens this vessel with its suggestion.")
    planner.switch_button.click()
    best = planner.hero_vessels[-1]
    assert planner.current_vessel()["id"] == best["id"]
    assert planner.advisor_bar.answer.suggestions[0].score.value == told.value_of[
        run.vessel_slots(best, True)]
    assert not planner.advisor_bar.has_been_applied()


def _another_vessel(planner):
    """A vessel neither open nor the best of the list."""
    return next(vessel for vessel in planner.hero_vessels[:-1]
                if vessel != planner.current_vessel())


def _hold_a_relic(planner):
    """A relic held in the first slot, and the last vessel that takes it."""
    card = planner.active_slots()[0]
    copy = next(copy for copy in card._holdable() if copy.handle is not None)
    relics.equip(card, copy)
    card.hold_button.setChecked(True)
    return card, copy


def _a_vessel_that_takes(planner, copy):
    return next(
        vessel for vessel in reversed(planner.hero_vessels)
        if vessel != planner.current_vessel() and candidates.place(
            [copy], run.vessel_slots(vessel, True))[0])


def _best_fitting(planner):
    """Rows the holds do not fit rank last, so `BEST` is the last that fits."""
    comparing = planner.advisor_bar.comparing
    return comparing.ranked()[0].vessel_id


def test_with_a_hold_a_click_opens_it_as_it_was_left_and_runs_nothing(planner,
                                                                      told):
    """AK-454."""
    _card, copy = _hold_a_relic(planner)
    _compared(planner)
    calls = told.calls
    target = _a_vessel_that_takes(planner, copy)
    tip = planner.chalice_list.item(_row_of(planner, target["id"])).toolTip()
    assert "Click opens it as you left it." in tip
    assert "Compared with your 1 held relic placed in it." in tip

    planner.chalice_list.setCurrentRow(_row_of(planner, target["id"]))

    bar = planner.advisor_bar
    assert bar.answer is None
    assert bar.situation.state is advisorbar.State.NOTHING_YET
    assert told.calls == calls
    assert bar._controller._pending is None
    assert planner.held_slot_indices() == frozenset()
    assert bar.comparing.state is advisorbar.Compared.DONE


def test_a_switch_moves_the_holds_and_rejections_and_undo_takes_all_of_it_back(
        planner, told):
    """AK-454, its acceptance case: the target's saved slots as they were."""
    origin = planner.current_vessel()
    card, copy = _hold_a_relic(planner)
    roll = (7, (1,), ())
    planner._rejects[planner._reject_key()] = {roll: "Rejected"}
    holds_before = dict(planner._holds[planner._hold_key()])
    _compared(planner)
    calls = told.calls
    target_id = _best_fitting(planner)
    assert target_id != origin["id"]
    target = next(vessel for vessel in planner.hero_vessels
                  if vessel["id"] == target_id)
    assert planner.switch_button.toolTip().startswith("Moves your held relics")
    keys_there = relics.stored_keys(planner, target_id)

    planner.switch_button.click()

    bar = planner.advisor_bar
    assert planner.current_vessel()["id"] == target_id
    assert told.calls == calls, "the row has to be the suggestion, not a new run"
    assert bar.answer.suggestions[0].score.value == told.value_of[
        run.vessel_slots(target, True)]
    assert bar.has_been_applied()
    assert bar.status.accessibleName() == (
        "Applied. Undo puts your slots back as they were.")
    index, = planner.held_slot_indices()
    assert planner.active_slots()[index].current_relic().handle == copy.handle
    assert planner.rejected_rolls() == frozenset({roll})
    assert relics.stored_keys(planner, target_id) != keys_there
    assert not planner.rejected_list.isHidden()

    planner.undo_apply()

    assert bar.answer is None
    assert planner.held_slot_indices() == frozenset()
    assert planner.rejected_rolls() == frozenset()
    assert relics.stored_keys(planner, target_id) == keys_there
    planner.chalice_list.setCurrentRow(_row_of(planner, origin["id"]))
    assert planner._holds[planner._hold_key()] == holds_before
    assert planner.rejected_rolls() == frozenset({roll})
    assert planner.active_slots()[0].current_relic().handle == copy.handle
    assert card.hold_button.isChecked()


def test_a_switch_brings_the_hand_the_row_was_compared_in(planner, told):
    """AK-435: a vessel's stored hand would otherwise be a miss."""
    planner.stat_sheet.hand_switch.setChecked(True)
    _compared(planner)
    planner.switch_button.click()
    assert planner.advisor_bar.answer is not None
    assert planner.stat_sheet.hand_switch.isChecked()
    assert planner.current_vessel() == planner.hero_vessels[-1]


def test_a_click_in_the_other_hand_is_not_out_of_date_but_a_miss(planner, told):
    """AK-434: the vessel brought its hand back, the player changed nothing."""
    planner.stat_sheet.hand_switch.setChecked(True)
    _compared(planner)
    planner.chalice_list.setCurrentRow(
        _row_of(planner, _another_vessel(planner)["id"]))
    assert not planner.stat_sheet.hand_switch.isChecked()
    assert planner.advisor_bar.comparing.state is advisorbar.Compared.DONE
    assert planner.advisor_bar.answer is None


@pytest.mark.parametrize("what_changes", [
    lambda planner: planner.active_slots()[0].hold_button.setChecked(True),
    lambda planner: planner.stat_sheet.hand_switch.click(),
    lambda planner: planner.level_slider.setValue(
        14 if planner.level_slider.value() == 15 else 15),
], ids=["hold", "hand", "level"])
def test_what_outdates_it_at_the_window(planner, told, what_changes):
    """AK-434: figures stay, `BEST` goes, and the sentence says so."""
    _compared(planner)
    what_changes(planner)
    assert planner.compare_status.text() == (
        "Out of date — use Optimize again to compare.")
    assert planner.switch_button.isHidden()
    lines = [_line_of(planner, vessel["id"]) for vessel in planner.hero_vessels]
    assert all(line[0] == "" and line[1].isdigit() for line in lines)


def test_cancel_takes_the_comparison_off_the_list(planner, told):
    """AK-453."""
    bar = planner.advisor_bar
    bar.optimize_button.click()
    assert planner.compare_status.text().endswith("…")
    assert _line_of(planner, planner.hero_vessels[0]["id"]) == ("", "…")
    bar._controller.cancel()
    assert bar.comparing is None
    assert planner.compare_status.isHidden()
    assert _line_of(planner, planner.hero_vessels[0]["id"]) is None


def test_a_row_is_drawn_with_room_for_its_second_line(planner, told):
    """AK-432: the height of the row; both lines drawn inside it, none lost."""
    _compared(planner)
    delegate = planner.chalice_list.itemDelegate()
    index = planner.chalice_list.model().index(_row_of(
        planner, planner.hero_vessels[-1]["id"]), 0)
    assert isinstance(delegate, advisorbar.VesselRowDelegate)
    assert (planner.chalice_list.sizeHintForRow(index.row())
            >= advisorbar.VESSEL_ROW_HEIGHT)
    assert not planner.chalice_list.grab().isNull()
