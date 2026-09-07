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
from PySide6.QtWidgets import QFrame, QLabel

from nrplanner import relicpicker
from nrplanner.advisor import types

#: A value row long enough to stand for the worst real case: the survival
#: direction carries the longer unit, and four digits is more than any
#: effective-HP difference this dataset produces.
LONGEST = "+1234.5 effective HP"


class FakeAdvice:
    """A `SlotAdvice` whose pool is stated rather than computed.

    It answers the three questions the picker asks of one -- which direction
    the program stands on, that it should stand on another, and what this
    slot's pool is -- and writes down the second, which is how the two
    directions of AK-43's coupling are told apart.
    """

    def __init__(self, pools: dict, goal_id: str = "max_damage"):
        self.pools = pools
        self._goal_id = goal_id
        self.chosen: list[str] = []

    def goal_id(self) -> str:
        return self._goal_id

    def choose_goal(self, goal_id: str) -> None:
        self._goal_id = goal_id
        self.chosen.append(goal_id)

    def ranking(self, goal_id: str):
        pool = self.pools.get(goal_id)
        return None if pool is None else relicpicker.Ranking(pool)


def a_slot(planner):
    """A relic slot of the open window that really offers cards."""
    for slot in planner.active_slots():
        if len(slot.available_items()) >= 4:
            return slot
    pytest.skip("no slot of this save offers four relics to rank")


def pool_of(slot, gains, taken=(), *, rank_by="max_damage",
            baseline=(("max_damage", 100.0, "AR"),
                      ("min_damage_taken", 900.0, "effective HP")),
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
        baseline=tuple(types.Baseline(goal_id, value, unit)
                       for goal_id, value, unit in baseline),
        candidates=tuple(candidates), unknowns=unknowns)


def picker_for(slot, advice):
    """The picker for this slot, driven by a stated advice."""
    return relicpicker.RelicPicker(slot, slot.icons, "", lambda _text: None,
                                   advice=advice)


def relic_cards(dialog):
    """The relic cards in the order the grid holds them."""
    holder = dialog.scroll.widget()
    return holder.findChildren(relicpicker.RelicCard)


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

    Asked of `heightForWidth` at the card's own width, which is what the grid
    gives a row -- a wrapped label's `sizeHint` is the one long line it would
    rather have, and sizing anything on that measures a layout the dialog
    never has.
    """
    item = slot.available_items()[0]
    card = relicpicker.RelicCard(
        item, slot.effect_names(item), None, False, lambda _i: None,
        captions=[relicpicker.VALUE_CAPTIONS[goal_id]
                  for goal_id in relicpicker.VALUE_DIRECTIONS])
    card.setFixedWidth(relicpicker.CARD_WIDTH)
    before = card.heightForWidth(relicpicker.CARD_WIDTH)
    assert values_of(card) == [relicpicker.PENDING] * 2, (
        "the block has to be built with the room already reserved")
    card.show_values([LONGEST, LONGEST],
                     relicpicker.chip_text("max_damage"))
    after = card.heightForWidth(relicpicker.CARD_WIDTH)
    assert after == before, (
        f"the card is {after - before} px taller once the figures are in; "
        f"with 29 cards that moves the whole grid")
    card.deleteLater()


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
    card = relicpicker.RelicCard(
        item, slot.effect_names(item), None, False, lambda _i: None,
        captions=["Damage", "Damage taken"])
    card.setFixedWidth(relicpicker.CARD_WIDTH)
    before = card.heightForWidth(relicpicker.CARD_WIDTH)
    card.show_values(["+1.0 AR", "-2.0 effective HP"], "BEST FOR DAMAGE")
    assert card.heightForWidth(relicpicker.CARD_WIDTH) == before
    card.deleteLater()


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
    ranking = advice.ranking("max_damage")
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
