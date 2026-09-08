"""What a relic is worth to this build, said on its card in the picker.

**This is the advisor's main way in** (`GOAL.md` F2, AD-018), so the cases
here are about a figure a player reads rather than about a figure a search
consumes. Three things they keep coming back to:

* **The card is the same height before the figures and after them** (AK-41).
  Measured on the card's own `heightForWidth`, with the longest text a
  direction can produce, because with 29 cards a block that grew when the
  answer arrived would move the whole grid under the reader's hand.
* **The number is not computed here** (AD-018 checkpoint 15). Every figure is
  read out of the `SlotPool` the pre-sort produced, bit for bit, and the case
  that says so compares floats rather than the one decimal a card shows -- a
  second arithmetic that agreed to a tenth would pass a case written on the
  text.
* **A pool built by hand, not hunted for in the save.** Ties, an exact zero
  and a negative top value are the states §3.5 is written about, and a real
  inventory offers them only by luck. The handles come from the slot's own
  list, so the cards and the pool are talking about the same copies.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import QEventLoop, Qt, QTimer
from PySide6.QtWidgets import QFrame, QLabel

from nrplanner import relicpicker
from nrplanner.advisor import types

#: A value row long enough to stand for the worst real case: the survival
#: direction carries the longer unit, and four digits is more than any
#: effective-HP difference this dataset produces.
LONGEST = "+1234.5 effective HP"


class FakeAdvice:
    """A `SlotAdvice` whose pool is stated rather than computed.

    It answers the four things the picker asks of one -- which direction the
    program stands on, that it should stand on another, this slot's question,
    and that the dialog is closing -- and writes down the second, which is how
    the two directions of AK-43's coupling are told apart.

    **It is also the four fixtures the waiting state needs** (`UI_SPEC` §9,
    AK-211 to AK-218): a track that answers at once (`at_once`, the default),
    one that never answers (`at_once=False` and nobody calls `answer`), one
    that fails and one that is stopped. They are one class because they differ
    in one thing only -- when and with what the one answer of an opening
    arrives -- and four classes would have hidden that.

    `pools` is keyed by direction, and the pool handed over is the one of the
    direction the program is standing on when the question is asked. The real
    track asks under `goals.CANONICAL_POOL_ORDER` whatever is chosen (Nachtrag
    IX-2); what is under test here is what the picker **draws**, and that is
    the chosen direction (AK-205), so a case states the pool it wants read.
    """

    def __init__(self, pools: dict, goal_id: str = "max_damage", *,
                 at_once: bool = True):
        self.pools = pools
        self._goal_id = goal_id
        self.chosen: list[str] = []
        self.at_once = at_once
        self.asked = 0
        self.listening = False
        self._answered = None
        self._pool = None

    def goal_id(self) -> str:
        return self._goal_id

    def choose_goal(self, goal_id: str) -> None:
        self._goal_id = goal_id
        self.chosen.append(goal_id)

    def ask(self, answered):
        pool = self.pools.get(self._goal_id)
        if pool is None:
            return None
        self.asked += 1
        if self.at_once:
            return relicpicker.Asked(relicpicker.Ranking(pool))
        self._pool = pool
        self._answered = answered
        self.listening = True
        return relicpicker.Asked(None)

    def stop_listening(self) -> None:
        self.listening = False
        self._answered = None

    def _deliver(self, ranking, reason: str) -> None:
        """One outcome, and none at all once nobody is listening.

        A dialog that has closed has stopped listening, and the real track
        drops what belongs to an earlier opening at its generation counter.
        Delivering into nothing has to be as harmless here as it is there, or
        the case for AK-207 would be testing this class.
        """
        answered = self._answered
        self.stop_listening()
        if answered is not None:
            answered(ranking, reason)

    def answer(self) -> None:
        """The track's `ready`: the pool this question was asked for."""
        self._deliver(relicpicker.Ranking(self._pool), "")

    def fail(self, reason: str) -> None:
        """The track's `failed`, with the one line it carries."""
        self._deliver(None, reason)

    def stop(self) -> None:
        """The track's `stopped`, in the picker's own words (AK-218)."""
        self._deliver(None, relicpicker.SEARCH_WAS_STOPPED)


def a_slot(planner):
    """A relic slot of the open window that really offers cards."""
    for slot in planner.active_slots():
        if len(slot.available_items()) >= 4:
            return slot
    pytest.skip("no slot of this save offers four relics to rank")


def pool_of(slot, gains, taken=(), *, rank_by="max_damage",
            baseline=(("max_damage", 100.0, "AR", ()),
                      ("min_damage_taken", 900.0, "effective HP", ())),
            unknowns=()):
    """A `SlotPool` over this slot's own copies, with the gains named.

    `gains` maps the position of a copy in the slot's list to its gain under
    `rank_by`; the other direction gets the same figure negated, so a case
    that reads the wrong column reads a different sign. Copies not named get
    nothing at all -- which is how the pool says "this save gives me no
    handle for it".
    """
    items = slot.available_items()
    other = next(goal_id for goal_id in relicpicker.VALUE_DIRECTIONS
                 if goal_id != rank_by)
    candidates = []
    for index, item in enumerate(items):
        if index not in gains or index in taken or item.handle is None:
            continue
        gain = gains[index]
        candidates.append(types.Candidate(
            slot_index=slot.index, handle=item.handle,
            relic_id=item.relic_id, name=item.name, colour=item.colour,
            is_deep=item.is_deep, effect_ids=tuple(item.effect_ids),
            marginals=(types.Marginal(rank_by, gain),
                       types.Marginal(other, -gain))))
    candidates.sort(key=lambda c: (-types.marginal_for(c, rank_by), c.name,
                                   c.handle))
    return types.SlotPool(
        slot_index=slot.index, rank_by=rank_by,
        baseline=tuple(types.Baseline(goal_id, value, unit, found)
                       for goal_id, value, unit, found in baseline),
        candidates=tuple(candidates), unknowns=unknowns)


#: How long a case waits for the real track before calling it a fault. The
#: most expensive slot this save has is measured at 318,1 ms (S11-C), and a
#: machine ten times slower than that one is still well inside this. It is a
#: fuse against a question that ends in none of its three outcomes -- not a
#: budget, and nothing here asserts on how long the answer took (AD-028: no
#: wall clock in the suite).
ANSWER_FUSE_MS = 30000


def the_one_answer(advice, fuse_ms: int = ANSWER_FUSE_MS):
    """Ask a real `SlotAdvice` and wait for the one answer of the opening.

    The window's track computes in a thread and answers into the event loop,
    so a case that wants the figures has to give it one. `None` is "there was
    nothing to ask" -- no save on this machine -- and is the caller's to skip
    on; a question that ends in none of its three outcomes is a failure here
    and not a hang.
    """
    got = []
    loop = QEventLoop()

    def answered(ranking, reason):
        got.append((ranking, reason))
        loop.quit()

    asked = advice.ask(answered)
    if asked is None:
        return None
    if asked.ranking is not None:
        return asked.ranking
    fuse = QTimer()
    fuse.setSingleShot(True)
    fuse.timeout.connect(loop.quit)
    fuse.start(fuse_ms)
    loop.exec()
    assert got, "the track ended in none of ready, failed and stopped"
    ranking, reason = got[0]
    assert not reason, reason
    return ranking


def picker_for(slot, advice):
    """The picker for this slot, driven by a stated advice."""
    return relicpicker.RelicPicker(slot, slot.icons, "", lambda _text: None,
                                   advice=advice)


def relic_cards(dialog):
    """The relic cards in the order the grid holds them."""
    holder = dialog.scroll.widget()
    return holder.findChildren(relicpicker.RelicCard)


def a_card(slot, item, values=None, chip=""):
    """One card as the picker builds it, optionally already given figures."""
    card = relicpicker.RelicCard(
        item, slot.effect_names(item), None, False, lambda _i: None,
        captions=[relicpicker.VALUE_CAPTIONS[goal_id]
                  for goal_id in relicpicker.VALUE_DIRECTIONS])
    card.setFixedWidth(relicpicker.CARD_WIDTH)
    if values is not None:
        card.show_values(values, chip)
    return card


def card_height(card) -> tuple[int, int]:
    """The card's height, read both ways.

    **Two readings, because neither alone is sensitive to both faults.**
    `heightForWidth` is what the grid gives a row and is what moves when a
    label wraps to another line; `sizeHint` is what moves when a widget is
    added or taken away.

    **Measured on a card built that way, never on one changed afterwards.**
    Against the counterbuild that builds the value block only once the
    figures are there, a card that was measured, then filled and measured
    again reported 169 px both times although the block's own `sizeHint` had
    gone from 3 px to 31: the layout caches are cleared by a layout request
    that nothing delivers without an event loop, and invalidating every
    layout in the card by hand did not clear them either. Two cards, each
    measured once, have no cache to be stale.
    """
    return (card.sizeHint().height(),
            card.heightForWidth(relicpicker.CARD_WIDTH))


def values_of(card) -> list[str]:
    return [label.text() for label in card.block.values]


def captions_of(card) -> list[str]:
    """The row captions of one card's value block, in order."""
    layout = card.block.layout()
    out = []
    for index in range(layout.count()):
        row = layout.itemAt(index).layout()
        if row is not None:
            out.append(row.itemAt(0).widget().text())
    return out


@pytest.fixture
def slot(planner):
    return a_slot(planner)


def open_picker(slot, gains, **kwargs):
    """A picker over a stated pool, closed again by the caller."""
    goal = kwargs.pop("goal_id", "max_damage")
    pool = pool_of(slot, gains, rank_by=goal, **kwargs)
    return picker_for(slot, FakeAdvice({goal: pool}, goal_id=goal))


# --- the block, and the room it takes (AK-41) ------------------------------

def test_every_relic_card_carries_a_value_block(slot):
    """AK-41: first line of the card body, both directions, on every card."""
    dialog = open_picker(slot, {0: 12.44})
    try:
        cards = relic_cards(dialog)
        assert cards, "this slot drew no relic cards, so nothing is measured"
        for card in cards:
            assert captions_of(card) == [
                relicpicker.VALUE_CAPTIONS[goal_id]
                for goal_id in relicpicker.VALUE_DIRECTIONS]
    finally:
        dialog.deleteLater()


def test_the_block_stands_between_the_header_and_the_effects(slot):
    """§3.3: under the header, over the effect points, with the hairline."""
    dialog = open_picker(slot, {0: 1.0})
    try:
        card = relic_cards(dialog)[0]
        layout = card.layout()
        order = [layout.itemAt(i) for i in range(layout.count())]
        assert order[0].layout() is not None, "the header leads the card"
        assert order[1].widget() is card.block, (
            "the value block is the first line of the card body")
        rule = card.block.layout().itemAt(0).widget()
        assert isinstance(rule, QFrame) and rule.frameShape() == QFrame.HLine
        assert rule.height() == 1
    finally:
        dialog.deleteLater()


def test_a_card_is_the_same_height_before_the_figures_and_after(slot):
    """AK-41, the measurement: difference 0 px.

    Two cards of the same relic, one still carrying `…` and one carrying the
    longest text a direction can produce. With 29 cards a block that arrived
    with the answer would move the whole grid under the reader's hand.
    """
    item = slot.available_items()[0]
    waiting = a_card(slot, item)
    answered = a_card(slot, item, [LONGEST, LONGEST],
                      relicpicker.chip_text("max_damage"))
    assert card_height(answered) == card_height(waiting), (
        f"the card measures {card_height(waiting)} while it waits and "
        f"{card_height(answered)} once the figures are in (sizeHint, "
        f"heightForWidth); with 29 cards that moves the whole grid")
    assert values_of(waiting) == [relicpicker.PENDING] * 2, (
        "the block has to be built with the room already reserved")
    waiting.deleteLater()
    answered.deleteLater()


def test_the_block_asks_for_no_more_width_than_the_card_has(slot):
    """A child that states a width widens every card past the viewport.

    The relation, not the number: the card asks for as much room with the
    block as without it. Measured offscreen, one 400-character name without a
    space took the column from 479 px to 4846 the last time a child here
    stated a width.
    """
    item = slot.available_items()[0]
    captions = [relicpicker.VALUE_CAPTIONS[goal_id]
                for goal_id in relicpicker.VALUE_DIRECTIONS]
    without = relicpicker.RelicCard(item, slot.effect_names(item), None,
                                    False, lambda _i: None)
    with_block = relicpicker.RelicCard(item, slot.effect_names(item), None,
                                       False, lambda _i: None,
                                       captions=captions)
    with_block.show_values([LONGEST, LONGEST])
    assert (with_block.minimumSizeHint().width()
            == without.minimumSizeHint().width())
    without.deleteLater()
    with_block.deleteLater()


# --- what the figures say (AK-42, AK-47, AK-49) ----------------------------

def test_a_gain_of_nothing_is_said_in_words():
    """AK-42: `no change`, never `+0.0`.

    Decided after rounding, because `+0.0` is what a gain of 0.04 would
    otherwise be called -- three characters that mean something else.
    """
    assert relicpicker.gain_text(0.0, "AR") == relicpicker.NO_CHANGE
    assert relicpicker.gain_text(0.04, "AR") == relicpicker.NO_CHANGE
    assert relicpicker.gain_text(-0.04, "AR") == relicpicker.NO_CHANGE
    assert relicpicker.gain_text(12.44, "AR") == "+12.4 AR"
    assert relicpicker.gain_text(-18.0, "effective HP") == "-18.0 effective HP"
    assert relicpicker.gain_text(0.09, "") == "+0.1"


def test_both_directions_stand_on_every_card(slot):
    """AK-42: both, whatever the pool was put in order by.

    The stated pool gives the second direction the negated figure, so a card
    that showed the ranked direction twice would show two figures of one
    sign.
    """
    dialog = open_picker(slot, {0: 12.44, 1: 3.0, 2: 0.0})
    try:
        shown = values_of(relic_cards(dialog)[0])
        assert len(shown) == len(relicpicker.VALUE_DIRECTIONS)
        assert relicpicker.PENDING not in shown, (
            "a card still says '…' after the figures were handed to it")
    finally:
        dialog.deleteLater()


def test_the_word_unverified_is_nowhere_in_the_picker(slot):
    """AK-47, second half: QA-018 is closed, so the word is gone.

    Read off every label the dialog draws, not off the module source: the
    source search is the second, independent one below.
    """
    dialog = open_picker(slot, {0: 12.44, 1: -3.0})
    try:
        drawn = [label.text() for label in dialog.findChildren(QLabel)]
        assert not [text for text in drawn if "unverified" in text.lower()]
    finally:
        dialog.deleteLater()


def test_no_string_in_the_picker_carries_the_word_unverified():
    """The second search of L-006, over the source rather than the screen."""
    import pathlib

    source = pathlib.Path(relicpicker.__file__).read_text(encoding="utf-8")
    assert "unverified" not in source.lower()


def test_a_copy_the_pool_does_not_carry_gets_a_dash_not_a_zero(slot):
    """AD-013 point 4: a copy with no handle is reported, never measured.

    `—` and not `0`: nothing was measured, which is a different statement
    from "measured, and it came to nothing".
    """
    dialog = open_picker(slot, {0: 5.0})
    try:
        cards = relic_cards(dialog)
        assert len(cards) > 1, "this slot offers one card, so nothing is left out"
        assert values_of(cards[-1]) == [relicpicker.NO_FIGURE] * 2
    finally:
        dialog.deleteLater()


def test_with_no_ranking_every_card_says_so_and_the_header_says_why(slot):
    """AK-49: `—` on every card, and the header sentence, not a made-up rank."""
    dialog = picker_for(slot, FakeAdvice({}, goal_id="max_damage"))
    try:
        for card in relic_cards(dialog):
            assert values_of(card) == [relicpicker.NO_FIGURE] * 2
        assert dialog.headline.text() == relicpicker.NO_FIGURES_AT_ALL
        assert dialog.headline.isVisibleTo(dialog)
    finally:
        dialog.deleteLater()


# --- the tie mark (AK-45, AK-46) -------------------------------------------

def test_the_chip_carries_a_word_and_every_card_worth_the_most_wears_it(slot):
    """AK-46: text, not only a colour, and five cards if five are worth it."""
    dialog = open_picker(slot, {0: 12.0, 1: 12.0, 2: 3.0})
    try:
        marked = [card for card in relic_cards(dialog) if card.chip.text()]
        assert len(marked) == 2, (
            f"{len(marked)} cards carry the mark, and two are worth the most")
        assert {card.chip.text() for card in marked} == {"BEST FOR DAMAGE"}
    finally:
        dialog.deleteLater()


def test_two_cards_showing_one_figure_carry_one_mark(slot):
    """AK-45: equality is decided at the precision the card shows.

    12.44 and 12.36 are different floats and the same `+12.4`. The worst case
    this rules out is two visibly equal numbers of which only one is marked.
    """
    dialog = open_picker(slot, {0: 12.44, 1: 12.36, 2: 1.0})
    try:
        cards = relic_cards(dialog)
        column = relicpicker.VALUE_DIRECTIONS.index("max_damage")
        by_text: dict[str, set[str]] = {}
        for card in cards:
            by_text.setdefault(values_of(card)[column],
                               set()).add(card.chip.text())
        for text, marks in by_text.items():
            assert len(marks) == 1, (
                f"cards showing {text!r} carry different marks: {marks}")
        assert by_text["+12.4 AR"] == {"BEST FOR DAMAGE"}
    finally:
        dialog.deleteLater()


def test_nothing_is_marked_best_when_the_best_is_no_change(slot):
    """AK-46: twenty cards marked at a top value of nothing would be a lie."""
    dialog = open_picker(slot, {0: 0.0, 1: 0.0, 2: -4.0})
    try:
        assert not [card for card in relic_cards(dialog) if card.chip.text()]
        assert dialog.headline.text() == (
            "Nothing you own raises damage in this slot.")
    finally:
        dialog.deleteLater()


def test_nothing_is_marked_best_when_the_best_is_negative(slot):
    """AK-46, the other half of the same rule."""
    dialog = open_picker(slot, {0: -1.0, 1: -4.0})
    try:
        assert not [card for card in relic_cards(dialog) if card.chip.text()]
        assert dialog.headline.text() == (
            "Nothing you own raises damage in this slot.")
    finally:
        dialog.deleteLater()


def test_the_mark_names_the_direction_it_is_about(slot):
    """§3.5 point 4: `BEST FOR SURVIVAL` for the other direction."""
    dialog = open_picker(slot, {0: 30.0, 1: 2.0}, goal_id="min_damage_taken")
    try:
        marked = [card for card in relic_cards(dialog) if card.chip.text()]
        assert [card.chip.text() for card in marked] == ["BEST FOR SURVIVAL"]
    finally:
        dialog.deleteLater()


def test_the_mark_does_not_change_the_card_it_is_on(slot):
    """AK-41 again, from the chip's side: the strip is there either way."""
    item = slot.available_items()[0]
    plain = a_card(slot, item, ["+1.0 AR", "-2.0 effective HP"])
    marked = a_card(slot, item, ["+1.0 AR", "-2.0 effective HP"],
                    "BEST FOR DAMAGE")
    assert card_height(marked) == card_height(plain)
    plain.deleteLater()
    marked.deleteLater()


def test_no_card_and_no_header_carries_an_ordinal(slot):
    """AK-44: the figure is the rank, so nothing numbers the cards."""
    dialog = open_picker(slot, {0: 12.0, 1: 5.0, 2: 1.0})
    try:
        drawn = [label.text() for label in dialog.findChildren(QLabel)
                 if label.text()]
        for text in drawn:
            assert not text.strip().startswith(("1.", "2.", "3.", "#")), text
            assert "Top " not in text
    finally:
        dialog.deleteLater()


# --- one calculation, two views (AD-018 checkpoint 15) ---------------------

def test_the_figure_on_a_card_is_the_pools_own_float(planner):
    """Checkpoint 15: the picker and `Optimize` pre-sort on one number.

    Compared as floats and not as the one decimal a card shows: a second
    arithmetic that agreed to a tenth would pass a case written on the text,
    which is exactly the duplication AD-018 is built against.
    """
    slot = a_slot(planner)
    advice = relicpicker.advice_for(slot)
    if advice is None:
        pytest.skip("this window carries no advisor bar")
    ranking = the_one_answer(advice)
    if ranking is None or not ranking.pool.candidates:
        pytest.skip("no save to rank against on this machine")
    for candidate in ranking.pool.candidates:
        item = next((i for i in slot.available_items()
                     if i.handle == candidate.handle), None)
        if item is None:
            continue
        for goal_id in relicpicker.VALUE_DIRECTIONS:
            assert (ranking.gain(item, goal_id).hex()
                    == types.marginal_for(candidate, goal_id).hex()), (
                f"{candidate.name} is shown a figure the pool did not carry")


# --- one goal setting in the whole program (AK-43, AK-44, AK-52) -----------

def test_sort_by_offers_the_two_directions_and_name(slot):
    """§3.4: the registry's own labels, in the registry's own order."""
    from nrplanner.advisor import goals as advisor_goals

    dialog = open_picker(slot, {0: 1.0})
    try:
        box = dialog.sort_box
        assert [box.itemData(i) for i in range(box.count())] == [
            "max_damage", "min_damage_taken", relicpicker.NAME_ORDER]
        assert [box.itemText(i) for i in range(box.count())] == [
            advisor_goals.GOALS["max_damage"].label,
            advisor_goals.GOALS["min_damage_taken"].label,
            "Name"]
        assert box.maximumWidth() == relicpicker.SORT_BOX_WIDTH
    finally:
        dialog.deleteLater()


def test_the_bar_decides_what_sort_by_opens_on(slot):
    """AK-43, one direction of the coupling: the setting reaches the picker."""
    for goal_id in ("min_damage_taken", "max_damage"):
        dialog = picker_for(slot, FakeAdvice(
            {goal_id: pool_of(slot, {0: 1.0}, rank_by=goal_id)},
            goal_id=goal_id))
        try:
            assert dialog.sort_box.currentData() == goal_id
        finally:
            dialog.deleteLater()


def test_choosing_a_direction_in_the_picker_moves_the_one_setting(slot):
    """AK-43, the other direction: the picker writes the same setting.

    Written to the advice rather than kept here, because a `Sort by` with a
    setting of its own would be the fourth place in the program that can say
    which direction the player is asking about.
    """
    advice = FakeAdvice(
        {"max_damage": pool_of(slot, {0: 1.0, 1: 2.0}),
         "min_damage_taken": pool_of(slot, {0: 3.0},
                                     rank_by="min_damage_taken")},
        goal_id="max_damage")
    dialog = picker_for(slot, advice)
    try:
        box = dialog.sort_box
        box.setCurrentIndex(box.findData("min_damage_taken"))
        dialog._sort_chosen(box.currentIndex())
        assert advice.chosen == ["min_damage_taken"]
        assert advice.goal_id() == "min_damage_taken"
        # And nothing was asked a second time (AK-206, Nachtrag IX-0): the
        # answer on screen is the one this opening asked for, and it serves
        # the other direction as it stands. The direction that is drawn is
        # the setting, not the pool's `rank_by` (AK-205).
        assert advice.asked == 1
        assert dialog.ranking.pool.rank_by == "max_damage"
        assert dialog._drawn_direction() == "min_damage_taken"
    finally:
        dialog.deleteLater()


def test_choosing_name_order_changes_no_direction(slot):
    """§3.4: `Name` is a way of looking, not a question."""
    advice = FakeAdvice({"max_damage": pool_of(slot, {0: 1.0})},
                        goal_id="max_damage")
    dialog = picker_for(slot, advice)
    try:
        box = dialog.sort_box
        box.setCurrentIndex(box.findData(relicpicker.NAME_ORDER))
        dialog._sort_chosen(box.currentIndex())
        assert advice.chosen == []
        assert advice.goal_id() == "max_damage"
    finally:
        dialog.deleteLater()


def names_in_order(dialog) -> list[str]:
    return [card.item.name for card in relic_cards(dialog)]


def test_the_value_leads_the_order_and_ties_keep_the_order_they_had(slot):
    """AK-44: the figure sorts, and where it cannot, nothing moves.

    Three copies worth the same and one worth more: the one worth more comes
    first, and the three keep the order the grid would have had without any
    advisor at all.
    """
    items = slot.available_items()
    if len(items) < 4:
        pytest.skip("this slot offers fewer than four relics")
    gains = {0: 1.0, 1: 1.0, 2: 1.0, 3: 9.0}
    plain = picker_for(slot, FakeAdvice({}))
    try:
        untouched = names_in_order(plain)
    finally:
        plain.deleteLater()
    dialog = open_picker(slot, gains)
    try:
        ranked = names_in_order(dialog)
        assert ranked[0] == untouched[3], (
            "the copy worth the most does not lead the grid")
        assert ranked[1:4] == [untouched[0], untouched[1], untouched[2]], (
            "the three tied copies were reordered by something that is not "
            "the figure")
    finally:
        dialog.deleteLater()


def test_the_same_state_opens_in_the_same_order_twice(slot):
    """AK-44: nothing wobbles between two openings."""
    gains = {0: 2.0, 1: 2.0, 2: 5.0, 3: 5.0}
    first = open_picker(slot, gains)
    second = open_picker(slot, gains)
    try:
        assert names_in_order(first) == names_in_order(second)
    finally:
        first.deleteLater()
        second.deleteLater()


def test_name_order_puts_the_grid_back_the_way_it_was(slot):
    """§3.4: with `Name` the grid is the one the picker has always had."""
    advice = FakeAdvice({"max_damage": pool_of(slot, {0: 1.0, 1: 9.0})},
                        goal_id="max_damage")
    dialog = picker_for(slot, advice)
    plain = picker_for(slot, FakeAdvice({}))
    try:
        box = dialog.sort_box
        box.setCurrentIndex(box.findData(relicpicker.NAME_ORDER))
        dialog._sort_chosen(box.currentIndex())
        assert names_in_order(dialog) == names_in_order(plain)
    finally:
        dialog.deleteLater()
        plain.deleteLater()


def test_both_directions_still_stand_on_every_card_in_name_order(slot):
    """AK-42: whatever the sorting, both figures are there."""
    advice = FakeAdvice({"max_damage": pool_of(slot, {0: 1.0, 1: 9.0})},
                        goal_id="max_damage")
    dialog = picker_for(slot, advice)
    try:
        box = dialog.sort_box
        box.setCurrentIndex(box.findData(relicpicker.NAME_ORDER))
        dialog._sort_chosen(box.currentIndex())
        shown = values_of(relic_cards(dialog)[0])
        assert len(shown) == 2 and relicpicker.PENDING not in shown
    finally:
        dialog.deleteLater()


def test_the_custom_tile_leads_the_grid_in_every_order(slot):
    """§3.4, unchanged: the answer to "none of these" is never sorted away."""
    for order in ("max_damage", relicpicker.NAME_ORDER):
        dialog = open_picker(slot, {0: 1.0, 1: 9.0})
        try:
            box = dialog.sort_box
            box.setCurrentIndex(box.findData(order))
            dialog._sort_chosen(box.currentIndex())
            holder = dialog.scroll.widget()
            first = holder.layout().itemAtPosition(0, 0).widget()
            assert isinstance(first, relicpicker.CustomRelicCard)
        finally:
            dialog.deleteLater()


# --- both top picks lead the grid (AK-195) ----------------------------------

def handles_in_order(dialog) -> list:
    return [card.item.handle for card in relic_cards(dialog)]


def test_the_survival_top_pick_leads_when_sorted_by_damage(slot):
    """AK-195, the core case: sorted by damage, the best survival card too.

    Four candidates, all with a damage figure so their plain value order is
    unambiguous: index 1 is the best on damage, index 0 the worst -- and,
    being the only one with a *negative* damage gain, the best on survival.
    Under plain value order alone index 0 would sink to the very back,
    behind index 2 and index 3; AK-195 says it leads right after index 1
    instead, which is the one thing that tells this case apart from a
    picker that only ever promoted the sorted direction.
    """
    items = slot.available_items()
    dialog = open_picker(slot, {0: -5.0, 1: 12.0, 2: 8.0, 3: 6.0})
    try:
        order = handles_in_order(dialog)
        assert order[:2] == [items[1].handle, items[0].handle], (
            "the best survival card does not lead right after the best "
            "damage card when sorted by damage")
    finally:
        dialog.deleteLater()


def test_the_damage_top_pick_leads_when_sorted_by_survival(slot):
    """AK-195, the other variant ("in beiden Varianten"): sorted by survival,
    the best damage card leads right after the best survival card.

    The mirror of the case above: index 1 is the best on survival, index 0
    the worst -- and, being the only one with a positive damage gain, the
    best on damage. Under plain value order it would sink behind index 2
    and index 3; AK-195 keeps it right after index 1.
    """
    items = slot.available_items()
    dialog = open_picker(slot, {0: -5.0, 1: 12.0, 2: 8.0, 3: 6.0},
                         goal_id="min_damage_taken")
    try:
        order = handles_in_order(dialog)
        assert order[:2] == [items[1].handle, items[0].handle], (
            "the best damage card does not lead right after the best "
            "survival card when sorted by survival")
    finally:
        dialog.deleteLater()


def test_no_promotion_when_sort_by_name(slot):
    """AK-195 Gegenbau 2: `Sort by` = `Name` promotes nothing at all."""
    advice = FakeAdvice({"max_damage": pool_of(slot, {0: -5.0, 1: 12.0})},
                        goal_id="max_damage")
    dialog = picker_for(slot, advice)
    plain = picker_for(slot, FakeAdvice({}))
    try:
        box = dialog.sort_box
        box.setCurrentIndex(box.findData(relicpicker.NAME_ORDER))
        dialog._sort_chosen(box.currentIndex())
        assert names_in_order(dialog) == names_in_order(plain), (
            "cards were promoted although `Sort by` stands on `Name`")
    finally:
        dialog.deleteLater()
        plain.deleteLater()


def test_no_promotion_when_the_other_top_is_no_change(slot):
    """AK-195 Gegenbau 3: a `no change` top pulls nothing for that direction.

    Sorted by damage: index 1 (5.0) leads as the damage top. Index 2 (2.0)
    is the second-best damage card. Index 0's damage gain is exactly 0.0, so
    its survival figure -- the pool's own maximum on that direction -- is
    also exactly 0.0, `no change`, and AK-46 marks no card at all. It must
    therefore stay in its ordinary value position, behind index 2, and not
    be spliced in as a second-direction leader.
    """
    items = slot.available_items()
    dialog = open_picker(slot, {0: 0.0, 1: 5.0, 2: 2.0})
    try:
        order = handles_in_order(dialog)
        h0, h1, h2 = items[0].handle, items[1].handle, items[2].handle
        assert order.index(h1) < order.index(h2) < order.index(h0), (
            "a 'no change' top pick was promoted, where AK-46 would give it "
            "no chip at all")
    finally:
        dialog.deleteLater()


def test_tied_top_picks_keep_favourite_then_name_order(slot):
    """AK-195 Gegenbau 4: a real tie among the leaders is not reordered by
    value -- AK-44 forbids a rank the figure did not decide.

    Index 0 and 1 have different *raw* gains (12.36 and 12.44) that round to
    the identical *displayed* figure (AK-45), so both earn the chip and
    both lead. Only the raw figure could tell them apart, and AK-44 forbids
    a rank drawn on it: they must stay in the order the grid has without an
    advisor at all -- index 0 before index 1, not the other way round.
    """
    items = slot.available_items()
    dialog = open_picker(slot, {0: 12.36, 1: 12.44})
    try:
        order = handles_in_order(dialog)
        assert order[:2] == [items[0].handle, items[1].handle], (
            "the tied top picks were reordered by value instead of keeping "
            "the favourite/name order the grid has without an advisor")
    finally:
        dialog.deleteLater()


def focus_chain(dialog) -> list:
    """Every widget of the dialog, in the order tabbing walks them."""
    walked = []
    widget = dialog.search
    for _ in range(2000):
        widget = widget.nextInFocusChain()
        if widget is dialog.search:
            break
        walked.append(widget)
    return walked


def test_sort_by_stands_between_the_filter_and_the_cards(slot):
    """AK-52: after the filter field, before the first card.

    Walked rather than read off the layout: `setTabOrder` is what decides
    this, and a layout order that happened to agree today would keep the case
    green after the widget moved.
    """
    dialog = open_picker(slot, {0: 1.0})
    try:
        chain = focus_chain(dialog)
        first_card = relic_cards(dialog)[0].button
        assert dialog.sort_box in chain, (
            "Sort by is not in the dialog's tab order at all")
        assert first_card in chain, "no card is reachable by tabbing"
        assert chain.index(dialog.sort_box) < chain.index(first_card), (
            "the reader reaches a card before Sort by")
    finally:
        dialog.deleteLater()


# --- the lines outside the grid (AK-50, AK-62, AK-162 to AK-166) -----------

def test_line_three_names_the_size_the_figures_are_measured_against(slot):
    """§3.2: without the reference size `+12.4` says nothing.

    The build as it stands with **this** slot emptied -- including for the
    relic sitting in it right now, which is what makes it comparable with the
    ones that might replace it (AD-018.1).
    """
    dialog = open_picker(slot, {0: 12.4})
    try:
        assert (f"ranked against your build with {slot.slot_name()} empty"
                in dialog.summary.text())
    finally:
        dialog.deleteLater()


def test_line_four_carries_the_mandatory_line_and_then_the_registrys(slot):
    """AK-62 and AK-162: the fixed sentence, then `Goal.scope`, word for word."""
    from nrplanner.advisor import goals as advisor_goals

    dialog = open_picker(slot, {0: 1.0})
    try:
        text = dialog.caveats.text()
        assert dialog.caveats.isVisibleTo(dialog)
        assert text.startswith(relicpicker.ONE_SLOT_AT_A_TIME)
        scope = advisor_goals.GOALS["max_damage"].scope
        at = [text.index(sentence) for sentence in scope]
        assert at == sorted(at), "the scope sentences are not in tuple order"
    finally:
        dialog.deleteLater()


def test_line_four_follows_the_direction_it_is_about(slot):
    """AK-162: the other direction brings its own sentences, not a constant.

    A picker with the attack-rating reservation wired in as a string would
    stand on the wrong sentence here and the case would not see it, which is
    why the comparison is against the registry rather than against a wording.
    """
    from nrplanner.advisor import goals as advisor_goals

    dialog = open_picker(slot, {0: 1.0}, goal_id="min_damage_taken")
    try:
        text = dialog.caveats.text()
        for sentence in advisor_goals.GOALS["min_damage_taken"].scope:
            assert sentence in text
        for sentence in advisor_goals.GOALS["max_damage"].scope:
            assert sentence not in text
    finally:
        dialog.deleteLater()


def test_a_sentence_added_to_the_registry_reaches_the_picker(slot,
                                                             monkeypatch):
    """AK-162's check: no UI string is touched to add a reservation."""
    import dataclasses

    from nrplanner.advisor import goals as advisor_goals

    extra = "A sixth sentence nobody has wired into a widget."
    goal = advisor_goals.GOALS["max_damage"]
    monkeypatch.setattr(
        relicpicker.advisor_goals, "GOALS",
        dict(advisor_goals.GOALS,
             max_damage=dataclasses.replace(goal, scope=goal.scope + (extra,))))
    dialog = open_picker(slot, {0: 1.0})
    try:
        assert extra in dialog.caveats.text()
    finally:
        dialog.deleteLater()


def test_line_three_b_carries_the_run_findings_in_the_order_handed_over(slot):
    """AK-163: the direction's findings first, then the pool's.

    The first sentence is about the **figure** on every card, the second
    about the **stock** the cards came from, and the player reads the figure
    first.
    """
    dialog = picker_for(slot, FakeAdvice({"max_damage": pool_of(
        slot, {0: 1.0},
        baseline=(("max_damage", 100.0, "AR", ("about the figure",)),
                  ("min_damage_taken", 900.0, "effective HP", ())),
        unknowns=("about the stock",))}))
    try:
        assert dialog.findings.isVisibleTo(dialog)
        assert dialog.findings.text() == (
            "about the figure  ·  about the stock")
    finally:
        dialog.deleteLater()


def test_line_three_b_is_gone_when_both_sources_are_empty(slot):
    """AK-163: empty is an answer, not a gap -- and not an empty line."""
    dialog = open_picker(slot, {0: 1.0})
    try:
        assert dialog.findings.text() == ""
        assert not dialog.findings.isVisibleTo(dialog)
        assert dialog.caveats.isVisibleTo(dialog), (
            "line 4 must stand whether or not there is a run finding")
    finally:
        dialog.deleteLater()


def test_a_sentence_in_both_sources_is_drawn_twice(slot):
    """AK-165: the display de-duplicates nothing.

    A sentence in both classes is a fault of the calculation (checkpoint 30).
    A display that filtered it out would hide exactly the fault the
    checkpoint is written against.
    """
    twice = "Said by both halves."
    dialog = picker_for(slot, FakeAdvice({"max_damage": pool_of(
        slot, {0: 1.0},
        baseline=(("max_damage", 100.0, "AR", (twice,)),
                  ("min_damage_taken", 900.0, "", ())),
        unknowns=(twice,))}))
    try:
        assert dialog.findings.text().count(twice) == 2
    finally:
        dialog.deleteLater()


def test_the_weighting_note_is_nowhere_in_the_picker(slot):
    """AK-166: while there is no control for it, it would read as a repeat.

    `EVEN_WEIGHTING.note` opens with the same eight words as the second scope
    sentence of the survival direction, and two lines under each other that
    begin alike are read as one and skipped.
    """
    from nrplanner.advisor import goals as advisor_goals

    note = advisor_goals.EVEN_WEIGHTING.note
    dialog = picker_for(slot, FakeAdvice({"min_damage_taken": pool_of(
        slot, {0: 1.0}, rank_by="min_damage_taken",
        baseline=(("max_damage", 100.0, "AR", ()),
                  ("min_damage_taken", 900.0, "effective HP", ())))},
        goal_id="min_damage_taken"))
    try:
        drawn = " ".join(label.text()
                         for label in dialog.findChildren(QLabel))
        assert note not in drawn
    finally:
        dialog.deleteLater()


def test_the_three_lines_stand_outside_the_scroll_area_and_wrap(slot):
    """AK-50: visible without interaction, and never shortened."""
    dialog = open_picker(slot, {0: 1.0})
    try:
        layout = dialog.layout()
        held = [layout.itemAt(i).widget() for i in range(layout.count())]
        for line in (dialog.summary, dialog.findings, dialog.caveats):
            assert line in held, "a line was put inside the scroll area"
            assert line.wordWrap(), "a line that does not wrap gets cut"
            assert line.textFormat() == Qt.PlainText
    finally:
        dialog.deleteLater()


# --- the empty grid, and the one answer that fills it (§3.8 fassung 3) -----
#
# Four fixtures, all of them `FakeAdvice`: a track that answers at once, one
# that never answers, one that fails and one that is stopped. Not one of the
# cases below reads a clock -- what they state is which state the display is
# in, which is what the App Designer's decision is about (F-P, F-R).


def waiting_picker(slot, gains=None):
    """The picker over a track that has been asked and has not answered."""
    pools = {"max_damage": pool_of(slot, {0: 1.0, 1: 9.0}
                                   if gains is None else gains)}
    advice = FakeAdvice(pools, goal_id="max_damage", at_once=False)
    return picker_for(slot, advice), advice


def custom_tiles(dialog):
    return dialog.scroll.widget().findChildren(relicpicker.CustomRelicCard)


def area_lines(dialog):
    """Every line standing in the card area, in order."""
    return [label.text()
            for label in dialog.scroll.widget().findChildren(QLabel)]


def test_the_card_area_is_empty_until_the_answer_arrives(slot):
    """AK-212: the waiting state is a state, not an absence.

    The App Designer weighed cards that reorder under the pointer against a
    third of a second of nothing and chose the nothing (F-P), for every
    opening including `Sort by` = `Name` (F-R). What stands is one line, at
    the place the first card will take.
    """
    dialog, advice = waiting_picker(slot)
    try:
        assert relic_cards(dialog) == []
        assert custom_tiles(dialog) == [], (
            "the custom tile is a card and waits with the rest")
        assert area_lines(dialog) == [relicpicker.NOTHING_YET]
        assert dialog.summary.text() == relicpicker.working_out(
            slot.slot_name())
        assert not dialog.headline.isVisibleTo(dialog)
        assert advice.asked == 1
    finally:
        dialog.deleteLater()


def test_the_waiting_line_says_nothing_a_card_would_say(slot):
    """AK-214: line 3 counts nothing that is not standing."""
    dialog, _advice = waiting_picker(slot)
    try:
        line = dialog.summary.text()
        assert "relics" not in line
        assert "ranked against" not in line
        assert "right-click" not in line
        assert line.endswith("empty")
    finally:
        dialog.deleteLater()


def test_the_mandatory_lines_do_not_wait(slot):
    """AK-201: what is true before any run stands from the first paint."""
    from nrplanner.advisor import goals as advisor_goals

    dialog, _advice = waiting_picker(slot)
    try:
        assert dialog.caveats.isVisibleTo(dialog)
        text = dialog.caveats.text()
        assert text.startswith(relicpicker.ONE_SLOT_AT_A_TIME)
        for sentence in advisor_goals.GOALS["max_damage"].scope:
            assert sentence in text
        assert not dialog.findings.isVisibleTo(dialog), (
            "the run findings belong to a pool and are the one line that "
            "may wait")
    finally:
        dialog.deleteLater()


def test_nothing_is_locked_while_the_area_is_empty(slot):
    """AK-213: the dialog is the window, and A6 wants it answerable."""
    dialog, advice = waiting_picker(slot)
    try:
        assert dialog.search.isEnabled()
        assert dialog.sort_box.isEnabled()
        assert dialog.scroll.isEnabled()
        assert dialog.sort_box.currentData() == "max_damage", (
            "`Sort by` is not put back to Name while the question is out")
        dialog.search.setText("hp")
        assert dialog.search.text() == "hp"
        assert advice.asked == 1, "a keystroke asked a second question"
    finally:
        dialog.deleteLater()


def test_a_filter_that_matches_nothing_leaves_the_line_standing(slot):
    """§3's named edge case: the state does not change under a keystroke."""
    dialog, _advice = waiting_picker(slot)
    try:
        dialog.search.setText("nothing matches this at all zzzz")
        assert area_lines(dialog) == [relicpicker.NOTHING_YET]
    finally:
        dialog.deleteLater()


def test_the_answer_fills_the_grid_in_one_go(slot):
    """AK-211: the cards, the figures, the chips and the order together."""
    dialog, advice = waiting_picker(slot)
    try:
        advice.answer()
        cards = relic_cards(dialog)
        assert cards, "the answer did not fill the grid"
        drawn = [label.text() for card in cards
                 for label in card.findChildren(QLabel)]
        assert relicpicker.PENDING not in drawn, (
            "AK-219: no card standing in the area carries the pending mark")
        assert relicpicker.NOTHING_YET not in area_lines(dialog)
        assert dialog.summary.text().startswith(f"{len(cards)} of ")
    finally:
        dialog.deleteLater()


def test_a_failure_fills_the_grid_and_says_why(slot):
    """AK-208 and AK-218: no figures is not the same as no cards."""
    dialog, advice = waiting_picker(slot)
    try:
        advice.fail("the run gave up")
        cards = relic_cards(dialog)
        assert cards
        assert dialog.headline.isVisibleTo(dialog)
        assert dialog.headline.text() == (
            "Could not work out what these are worth — the run gave up. "
            "They are in name order below.")
        assert relicpicker.NO_FIGURES_AT_ALL not in dialog.headline.text()
        for card in cards:
            values = [label.text()
                      for block in card.findChildren(relicpicker.ValueBlock)
                      for label in block.values]
            assert values == [relicpicker.NO_FIGURE] * len(
                relicpicker.VALUE_DIRECTIONS)
    finally:
        dialog.deleteLater()


def test_a_stopped_search_is_a_failure_with_its_own_reason(slot):
    """AK-218: `stopped` fills the grid too, in the picker's own words."""
    dialog, advice = waiting_picker(slot)
    try:
        advice.stop()
        assert relic_cards(dialog)
        assert dialog.headline.text() == relicpicker.could_not_work_out(
            relicpicker.SEARCH_WAS_STOPPED)
    finally:
        dialog.deleteLater()


def test_a_closed_dialog_hears_nothing_more(slot):
    """AK-207: an answer on its way reaches a dialog that has gone."""
    dialog, advice = waiting_picker(slot)
    try:
        dialog.done(0)
        assert not advice.listening
        advice.answer()
        assert relic_cards(dialog) == [], (
            "an answer after the close still drew into the dialog")
    finally:
        dialog.deleteLater()


def test_an_opening_with_no_relic_to_offer_does_not_wait(slot):
    """AK-212's stated exception: nothing to order, nothing to value.

    Stated at the first paint, which is where the exception lives: a filter
    typed *during* the wait leaves the line where it is (the case above), and
    a filter that was already typed when the dialog opened never puts it
    there.
    """
    dialog, advice = waiting_picker(slot)
    try:
        assert area_lines(dialog) == [relicpicker.NOTHING_YET]
    finally:
        dialog.deleteLater()
    empty = relicpicker.RelicPicker(
        slot, slot.icons, "zzz no effect is called this zzz",
        lambda _text: None,
        advice=FakeAdvice({"max_damage": pool_of(slot, {0: 1.0})},
                          goal_id="max_damage", at_once=False))
    try:
        assert relic_cards(empty) == []
        assert relicpicker.NOTHING_YET not in area_lines(empty)
        assert "relics" in empty.summary.text()
    finally:
        empty.deleteLater()


def test_the_dialog_takes_its_size_at_the_first_paint(slot):
    """AK-216: the answer must not resize the dialog under the player.

    Both openings of AK-216's own fixture -- one track that never answers,
    one that answers at once -- and the size across the answer of the first.
    The figures themselves are reported with their environment rather than
    written down here: a pixel count is a fact about a style and a scaling
    (L-009), and what this case states is a relation between two of them.
    """
    waiting, advice = waiting_picker(slot)
    try:
        before = (waiting.width(), waiting.height())
        advice.answer()
        assert (waiting.width(), waiting.height()) == before, (
            "the dialog changed size when the answer arrived")
    finally:
        waiting.deleteLater()
    at_once = picker_for(slot, FakeAdvice(
        {"max_damage": pool_of(slot, {0: 1.0, 1: 9.0})}, goal_id="max_damage"))
    try:
        assert (at_once.width(), at_once.height()) == before, (
            "an opening that waits and one that does not took two sizes")
    finally:
        at_once.deleteLater()


def test_the_drawn_direction_is_the_setting_and_not_the_pools_order(slot):
    """AK-205: `SlotPool.rank_by` is an ordering, never a choice.

    The picker asks under one fixed direction now (Nachtrag IX-2), so a pool
    that says `max_damage` is the ordinary case while the player stands on
    survival. Reading the direction off the pool draws the wrong column, the
    wrong chip and the wrong sentences -- and agrees with itself most of the
    time, which is what made the same fault cost 10,2 % silently wrong
    figures at its twin (T-077).
    """
    # Ordered by damage and negative in it, so the figures the player is
    # reading -- survival -- are the positive ones. A card wears the mark of
    # the direction it is read in or of none.
    ordered_by_damage = pool_of(slot, {0: -1.0, 1: -9.0}, rank_by="max_damage")
    advice = FakeAdvice({"min_damage_taken": ordered_by_damage},
                        goal_id="min_damage_taken")
    dialog = picker_for(slot, advice)
    try:
        assert dialog.ranking.pool.rank_by == "max_damage"
        assert dialog._drawn_direction() == "min_damage_taken"
        chips = [label.text() for card in relic_cards(dialog)
                 for label in card.findChildren(QLabel)
                 if label.text().startswith("BEST FOR ")]
        assert chips, "no card wore the mark of the direction being read"
        assert set(chips) == {relicpicker.chip_text("min_damage_taken")}
    finally:
        dialog.deleteLater()
