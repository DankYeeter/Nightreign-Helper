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

import pytest
from PySide6.QtWidgets import QPushButton

from nrplanner import advisorbar, chalices, inventory
from nrplanner.advisor import goals, types


# --- the answers the cases apply -------------------------------------------

def a_group(slot: int, relic: str) -> types.SlotReasons:
    return types.SlotReasons(slot_index=slot, relic_name=relic,
                             effects_total=1, effects_with_a_figure=1,
                             count_line="1 of its 1 effects moved a number "
                                        "in this build.",
                             lines=(types.ReasonLine(
                                 slot_index=slot,
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
    if planner.owned is None:
        pytest.skip("this machine has no save to read")
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
    """The captions of the row's action buttons, `Optimize` excluded."""
    return [button.text() for button in bar.findChildren(QPushButton)
            if button is not bar.optimize_button and not button.isHidden()]


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
        assert bar.status.whole_text() == (
            "Applied. Undo puts your slots back as they were.")
        assert visible_actions(bar) == ["Undo apply", "Why", "Clear"]

        bar.the_suggestion_was_undone()
        assert bar.status.whole_text() == (
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
    _stored, _deep, stored_keys = chalices.load(planner.current_hero()["id"],
                                                vessel["id"])
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
    assert planner.advisor_bar.status.whole_text() == (
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

    if planner.owned is None:
        pytest.skip("this machine has no save to read")
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
                    f"apply: {bar.status.whole_text()!r}")

    planner.apply_all()
    applied = keys_of(planner)
    assert applied != before, (
        "the run suggested exactly what was already equipped, so this case "
        "would pass whatever apply did")
    assert bar.situation.state is advisorbar.State.APPLIED

    planner.undo_apply()
    assert keys_of(planner) == before
    bar.shutdown()


def test_at_the_opening_width_no_action_button_is_cut(planner):
    """AK-05 for the three controls this task put in the row.

    The existing case measures the row in a state where none of them is on
    screen, so the row's busiest state was never measured at the opening
    width. Measured, not argued: the row is horizontally `Ignored` and hands
    its status label whatever is left, and what is left is a figure of the
    three captions and of the font.
    """
    from tests import rendered

    planner.resize(1320, 900)
    planner.show()
    rendered.settle()
    try:
        if planner.width() != 1320:
            pytest.skip(f"this platform will not give the window 1320 "
                        f"logical px: it is {planner.width()} px wide")
        bar = planner.advisor_bar
        bar._answer = types.AdvisorResult(
            goal_id="max_damage", goal_label="Maximise damage",
            suggestions=(types.Suggestion(
                choices=(types.SlotChoice(slot_index=0, handle=7, relic_id=1,
                                          name="X"),),
                score=types.GoalScore(value=1.0, display="1", unit="")),))
        bar._show(advisorbar.Situation(advisorbar.State.SUGGESTED,
                                       goal_label="Maximise damage",
                                       slots=6, slots_filled=1))
        rendered.settle()
        actions = [bar.apply_button, bar.why_button, bar.clear_button]
        assert [button.isHidden() for button in actions] == [False] * 3, (
            "no action button is on screen, so this case would pass whatever "
            "the row's width did")
        assert rendered.clipped(actions + [bar.goal_box,
                                           bar.optimize_button], bar) == []
    finally:
        planner.close()
