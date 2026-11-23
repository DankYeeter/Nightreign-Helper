"""The effect filter window (`UI_SPEC` §3.6, AK-303..309, AK-311, AK-316,
AK-317).

Driven with a hand-built inventory, so every count below is a count the
case wrote down; one case takes the frozen save to show the real dataset
gives the rows their names and families.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QTreeWidget, QApplication, QLabel

from nrplanner import effectfilterdialog as dlg
from nrplanner import effectfilters, effecttext, inventory
from nrplanner.theme import BAD

EFFECTS = {
    "10": {"name": "Vigor +2"},
    "11": {"name": "attack power up"},
    "12": {"name": "Mind +1"},
    "13": {"name": "Fire Damage Negation Up"},
    "14": {"name": "Holy Damage Negation Up +1"},
    "90": {"name": "Reduced HP", "is_curse": True},
}
FAMILY = "Damage Negation Up"
FAMILIES = {10: "Vigor", 11: "attack power up", 12: "Mind", 13: FAMILY,
            14: FAMILY, 90: "Reduced HP"}


def _relic(*effect_ids: int, curses: tuple = ()) -> inventory.OwnedItem:
    return inventory.OwnedItem(relic_id=1, name="Relic", colour=1,
                               effect_ids=list(effect_ids), is_deep=False,
                               curse_ids=list(curses))


def _owned(*relics) -> inventory.Inventory:
    return inventory.Inventory(source="test", relic_count=len(relics),
                               relics=list(relics))


@pytest.fixture
def filters():
    marks = effectfilters.EffectFilters(families=FAMILIES)
    yield marks
    for effect_id in set(marks.excluded | marks.required | marks.ignored):
        marks.mark(effect_id, None)
    for key in set(marks.avoided_families):
        marks.mark_family(key, False)
    for key in set(marks.ignored_families):
        marks.ignore_family(key, False)


@pytest.fixture
def window(qapp, filters):
    rows = dlg.rows_from(
        _owned(_relic(10, 11), _relic(10, 12, curses=(90,)), _relic(10, 10),
               _relic(13, 14)),
        EFFECTS, FAMILIES)
    dialog = dlg.EffectFilterWindow(filters, rows)
    yield dialog
    dialog.deleteLater()


def _top_level(window) -> list:
    return [window.tree.topLevelItem(i)
            for i in range(window.tree.topLevelItemCount())]


def _head(window):
    return window._family_marks[FAMILY][1]


def test_one_row_per_id_counted_in_relic_copies():
    """AK-304: three relics carry `10` (one of them twice) -- one row,
    `Copies = 3`; the curse is a row with its own type; a lost id keeps its
    number as its name and is a family of its own."""
    rows = {row.effect_id: row for row in dlg.rows_from(
        _owned(_relic(10, 11), _relic(10, 12, curses=(90,)), _relic(10, 10),
               _relic(77)),
        EFFECTS, FAMILIES)}
    assert rows[10] == dlg.Row(10, "Vigor +2", False, 3, "Vigor", ids=(10,))
    assert rows[90] == dlg.Row(90, "Reduced HP", True, 1, "Reduced HP",
                               ids=(90,))
    assert rows[77].name == rows[77].family == "effect 77"
    assert len(rows) == 5


def test_the_window_is_modal_titled_and_sorted_by_name_without_case(window):
    """AK-303, AK-308: `attack power up` sorts before `Damage Negation Up`
    and `Mind +1`; the family's members stand under it, sorted among
    themselves."""
    assert window.windowTitle() == dlg.TITLE
    assert window.isModal()
    assert window.shown_ids() == [11, 13, 14, 12, 90, 10]
    assert [window.tree.headerItem().text(c)
            for c in range(window.tree.columnCount())] == list(dlg.HEADINGS)
    top = _top_level(window)
    assert top[0].text(dlg.COL_TYPE) == "Effect"
    assert top[3].text(dlg.COL_TYPE) == "Curse"
    assert top[4].data(dlg.COL_COPIES, Qt.DisplayRole) == 3


def test_a_family_of_two_or_more_rows_has_a_heading_with_two_boxes(window):
    """AK-316.1, and the user decision of 2026-11-15: the heading carries
    the family key as its name, the sum of copies, a Favourite and an Avoid
    box, and since 2026-11-16 an Ignore box; no row has an Allow any more."""
    head = _head(window)
    assert head.text(dlg.COL_NAME) == FAMILY
    assert head.text(dlg.COL_TYPE) == ""
    assert head.data(dlg.COL_COPIES, Qt.DisplayRole) == 2
    assert head.childCount() == 2 and head.isExpanded()
    assert window.tree.itemWidget(head, dlg.COL_AVOID) is window.family_box(FAMILY)
    assert window.family_box(FAMILY).toolTip() == dlg.FAMILY_AVOID_TOOLTIP
    assert (window.tree.itemWidget(head, dlg.COL_FAVOURITE)
            is window.family_favourite_box(FAMILY))
    assert (window.tree.itemWidget(head, dlg.COL_IGNORE)
            is window.family_ignore_box(FAMILY))
    assert "Allow" not in dlg.HEADINGS
    assert not hasattr(window, "allow_box")
    assert all(item.childCount() == 0 for item in _top_level(window)
               if item is not head)


def test_the_two_boxes_are_disjoint_and_write_through(window, filters):
    """AK-305: Favourite takes a set Avoid away and the other way round,
    every click through `EffectFilters.mark`, so the store hears it."""
    favourite, avoid = window.boxes(10)
    assert favourite.toolTip() == dlg.FAVOURITE_TOOLTIP
    assert avoid.toolTip() == dlg.AVOID_TOOLTIP
    avoid.click()
    assert filters.excluded == {10} and filters.required == set()
    favourite.click()
    assert filters.required == {10} and filters.excluded == set()
    assert not avoid.isChecked()
    favourite.click()
    assert filters.required == set() and filters.excluded == set()


def test_a_members_own_ignore_lets_it_back_into_an_avoided_family(window,
                                                                  filters):
    """AK-316.3, and the user decision of 2026-11-16 that took Allow away:
    the heading's box calls `mark_family` both ways, a member set to Ignore
    is not avoided with its family, and its mark survives the family
    toggling either way."""
    ignore = window.ignore_box(13)
    ignore.click()
    assert filters.ignored == {13}
    assert filters.resolved_excluded == set()
    window.family_box(FAMILY).click()
    assert filters.avoided_families == {FAMILY}
    assert ignore.isEnabled() and ignore.isChecked()
    assert filters.resolved_excluded == {14}
    assert filters.resolved_ignored == {13}
    # The members' own marks are untouched by the family (AK-316.3).
    assert not window.boxes(13)[1].isChecked()
    window.family_box(FAMILY).click()
    assert filters.avoided_families == set()
    assert ignore.isChecked() and ignore.isEnabled()


def test_a_marking_made_elsewhere_is_drawn_without_a_restart(window, filters):
    """AK-311: the window listens to `changed` like the `Why` dialog does."""
    filters.mark(12, effectfilters.REQUIRED)
    favourite, avoid = window.boxes(12)
    assert favourite.isChecked() and not avoid.isChecked()
    assert window.counter.text() == "6 of 6 effects  ·  1 favourited"
    filters.mark_family(FAMILY, True)
    assert window.family_box(FAMILY).isChecked()


def test_the_counter_says_shown_of_total_and_the_set_counts(window, filters):
    """AK-307, AK-316.5: the search narrows `shown`, never `total`; the
    clauses stand only when their set is not empty, ids and families as
    two numbers."""
    assert window.counter.text() == "6 of 6 effects"
    filters.mark(10, effectfilters.EXCLUDED)
    filters.mark(90, effectfilters.EXCLUDED)
    filters.mark(11, effectfilters.REQUIRED)
    filters.mark_family(FAMILY, True)
    window.search.setText("mind")
    assert window.shown_ids() == [12]
    assert window.counter.text() == (
        "1 of 6 effects  ·  1 favourited  ·  2 avoided  ·  1 family avoided")


def test_a_third_counter_clause_keeps_the_opening_size(window, filters):
    """DR-032: `setWordWrap` on the counter absorbs a wider line by wrapping
    it, instead of the label's one-line `minimumSizeHint` forcing the whole
    window past `OPENING_SIZE` -- and never releasing it again once the
    clause is gone (measured offscreen at 814x642 before this fix, for
    exactly this text).
    """
    window.show()
    QApplication.processEvents()
    filters.mark(10, effectfilters.REQUIRED)
    filters.mark(11, effectfilters.REQUIRED)
    filters.mark(90, effectfilters.EXCLUDED)
    filters.mark_family(FAMILY, True)
    QApplication.processEvents()
    assert window.counter.text() == (
        "6 of 6 effects  ·  2 favourited  ·  1 avoided  ·  1 family avoided")
    assert (window.width(), window.height()) == dlg.OPENING_SIZE
    window.close()


def test_the_search_speaks_the_picker_syntax(window):
    """AK-306: `NOT` and a quoted phrase, as `search.parse` reads them."""
    assert window.search.placeholderText() == dlg.SEARCH_PLACEHOLDER
    window.search.setText('NOT "+"')
    # `14` carries a `+`, but its heading does not, and a hit on the
    # heading keeps every member (AK-316.6).
    assert window.shown_ids() == [11, 13, 14, 90]
    window.search.setText("vigor OR mind")
    assert window.shown_ids() == [12, 10]
    window.search.setText("")
    assert len(window.shown_ids()) == 6


def test_the_search_keeps_a_family_together_by_head_or_by_member(window):
    """AK-316.6: a hit on the heading keeps every member; a hit on one
    member keeps the heading and that member; no hit hides the family."""
    head = _head(window)
    window.search.setText("fire")
    assert not head.isHidden() and window.shown_ids() == [13]
    window.search.setText("negation")
    assert window.shown_ids() == [13, 14]
    window.search.setText("mind")
    assert head.isHidden() and window.shown_ids() == [12]


def test_the_three_empty_states(qapp, filters, window):
    """AK-309: two reasons for an empty grid without a search, and one
    label under the grid when the search alone empties it."""
    window.search.setText("nothing carries this")
    assert window.shown_ids() == []
    assert not window.empty.isHidden()
    assert window.empty.text() == dlg.NO_MATCH
    assert window.counter.text() == "0 of 6 effects"
    window.search.setText("")
    assert window.empty.isHidden()
    for reason in (dlg.NO_SAVE_WAS_READ, dlg.SAVE_HAS_NO_RELICS):
        empty = dlg.EffectFilterWindow(filters, [], reason)
        try:
            assert empty.tree.topLevelItemCount() == 0
            assert not empty.empty.isHidden()
            assert empty.empty.text() == reason
            assert empty.counter.text() == "0 of 0 effects"
        finally:
            empty.deleteLater()


def test_tab_walks_favourite_avoid_ignore_and_space_toggles(window, filters):
    """AK-305: reading order within a row, Space switches the box."""
    window.show()
    QApplication.processEvents()
    favourite, avoid = window.boxes(13)
    favourite.setFocus()
    QApplication.processEvents()
    assert QApplication.focusWidget() is favourite
    QTest.keyClick(favourite, Qt.Key_Tab)
    assert QApplication.focusWidget() is avoid
    QTest.keyClick(avoid, Qt.Key_Space)
    assert filters.excluded == {13}
    filters.mark_family(FAMILY, True)
    QTest.keyClick(avoid, Qt.Key_Tab)
    assert QApplication.focusWidget() is window.ignore_box(13)
    window.close()


def test_sorting_by_a_column_keeps_the_boxes_and_the_families_together(
        window, filters):
    """AK-308, AK-316.2: a re-sort moves the row, and the box with it; a
    family keeps its members under its heading, sorted among themselves."""
    filters.mark(10, effectfilters.EXCLUDED)
    filters.mark(14, effectfilters.EXCLUDED)
    window.tree.sortItems(dlg.COL_AVOID, Qt.DescendingOrder)
    top = _top_level(window)
    assert top[0].data(dlg.COL_NAME, Qt.UserRole) == 10
    assert window.tree.itemWidget(top[0], dlg.COL_AVOID) is window.boxes(10)[1]
    head = _head(window)
    assert [head.child(c).data(dlg.COL_NAME, Qt.UserRole)
            for c in range(2)] == [14, 13]
    window.tree.sortItems(dlg.COL_COPIES, Qt.DescendingOrder)
    assert window.shown_ids()[0] == 10
    assert _head(window).childCount() == 2


def test_sorting_by_type_puts_a_family_heading_with_its_empty_cell_first(window):
    """A heading has no type: its cell held nothing a `<` could compare with
    the text of a row, and the click on the column head raised `TypeError`."""
    window.tree.sortItems(dlg.COL_TYPE, Qt.AscendingOrder)
    top = _top_level(window)
    assert top[0] is _head(window)
    assert [item.text(dlg.COL_TYPE) for item in top[1:]] == [
        "Curse", "Effect", "Effect", "Effect"]
    window.tree.sortItems(dlg.COL_TYPE, Qt.DescendingOrder)
    assert _top_level(window)[-1] is _head(window)
    assert _head(window).childCount() == 2


def test_the_frozen_save_names_its_rows_out_of_the_dataset(qapp, filters,
                                                            frozen_inventory,
                                                            game_data):
    """AK-304 against the real dataset: every row has a name, no row is an
    id, one row per distinct name and every id in exactly one row (owner,
    23.11.2026) -- and the user's two dagger effects sit in one family
    (AD-039)."""
    effects = game_data["effects"]
    families = {int(i): effecttext.family_key(e, game_data["weapon_families"])
                for i, e in effects.items()}
    rows = dlg.rows_from(frozen_inventory, effects, families)
    ids = {i for item in frozen_inventory.relics
           for i in (*item.effect_ids, *item.curse_ids)}
    assert sorted(i for row in rows for i in row.all_ids) == sorted(ids)
    named = [(row.name, row.is_curse, row.family) for row in rows]
    assert len(named) == len(set(named)) > 0
    assert not any(row.name.startswith("effect ") for row in rows)
    assert any(row.is_curse for row in rows)
    by_id = {row.effect_id: row for row in rows}
    assert by_id[7330000].family == by_id[7080000].family == "Improved Attack Power"


def test_the_longer_legend_leaves_the_tree_its_height(window):
    """AK-445, AK-303."""
    window.show()
    QApplication.processEvents()
    assert window.findChildren(QTreeWidget)[0].height() == 449


def test_marks_explanation_label_is_present_and_unfocusable(window):
    """AK-445: the window carries the exact wording, and the label cannot
    take keyboard focus (it must not join the tab order)."""
    assert dlg.MARKS_EXPLANATION == (
        "Favourite: every suggestion must carry this effect, if it can — "
        "on a family header, any one member. Avoid: no "
        "suggestion uses a relic that carries it — on a family header, every "
        "member below, unless one has a mark of its own. Ignore: the effect "
        "may be on a suggested relic, but it counts as nothing — no gain, "
        "and for a curse no loss. These marks are saved "
        "for every Nightfarer; one that only works for another "
        "Nightfarer is ignored here. They are separate from the ★ you can give a "
        "relic in the relic picker: that is per Nightfarer, and Optimize puts "
        "a favourited relic in when it fits. Stacks: how many stacks Optimize "
        "and the relic picker's figures count for an effect that stacks, not "
        "the stat sheet; 0 does not count it, empty uses the count ticked on "
        "the stat sheet, otherwise 1.")
    assert dlg.FAVOURITE_TOOLTIP == (
        "Every suggestion for this Nightfarer must carry this effect, if it "
        "can.")
    assert dlg.AVOID_TOOLTIP == (
        "No suggestion uses a relic that carries this effect.")
    assert dlg.FAMILY_AVOID_TOOLTIP == (
        "No suggestion uses a relic that carries an effect of this family, "
        "unless a member below is set to Favourite or Ignore.")
    labels = [label for label in window.findChildren(QLabel)
              if label.text() == dlg.MARKS_EXPLANATION]
    assert len(labels) == 1
    assert labels[0].focusPolicy() == Qt.NoFocus


def test_the_name_takes_the_room_and_copies_only_its_content(window):
    """QA-334: both stood at 162 px of an opened window, names cut at 20 letters."""
    window.resize(*dlg.OPENING_SIZE)
    window.show()
    QApplication.processEvents()
    header = window.tree.header()
    assert header.sectionSize(dlg.COL_NAME) > header.sectionSize(dlg.COL_COPIES)
    window.hide()


STACKING = 15
STACKING_MEMBER = 16
STACK_EFFECTS = {**EFFECTS,
                 "15": {"name": "Attack up for each kill",
                        "modifiers": {"saveCategory": 9}},
                 "16": {"name": "Fire Damage Negation for each kill",
                        "modifiers": {"saveCategory": 9}}}
STACK_FAMILIES = {**FAMILIES, 15: "Attack up for each kill", 16: FAMILY}


@pytest.fixture
def stack_window(qapp, filters):
    rows = dlg.rows_from(
        _owned(_relic(10, 15), _relic(13, 16), _relic(11)),
        STACK_EFFECTS, STACK_FAMILIES)
    dialog = dlg.EffectFilterWindow(filters, rows)
    yield dialog
    dialog.close()
    dialog.deleteLater()
    for effect_id in set(filters.stacks):
        filters.set_stacks(effect_id, None)


def test_only_a_stack_effect_has_a_stacks_field(stack_window):
    """A headless single and a family member, not a heading, not a plain row."""
    window = stack_window
    assert dlg.HEADINGS[dlg.COL_STACKS] == "Stacks"
    assert set(window.stack_fields) == {STACKING, STACKING_MEMBER}
    assert window.tree.itemWidget(_head(window), dlg.COL_STACKS) is None
    field = window.stack_fields[STACKING]
    assert field.toolTip() == dlg.STACKS_TOOLTIP.format(limit=10) == (
        "How many stacks Optimize and the relic picker's figures count, a whole "
        "number from 0 to 10; 0 leaves this effect out. Empty: the count ticked "
        "on the stat sheet, otherwise 1. Anything else turns red and counts as "
        "empty. The stat sheet itself does not change.")
    assert field.accessibleName() == "Stacks: Attack up for each kill"
    assert window.tree.itemWidget(window._marks[STACKING][-1],
                                  dlg.COL_STACKS) is field


def test_the_red_field_starts_above_the_limit_of_its_own_effect(qapp, filters):
    """Night Invaders stop at 4 (`model.STACK_LIMITS`), and the tooltip says so."""
    night_invader = 7060200
    row = dlg.Row(effect_id=night_invader, name="Night Invader", is_curse=False,
                  copies=1, family="Night Invader", stacks=True)
    window = dlg.EffectFilterWindow(filters, [row])
    field = window.stack_fields[night_invader]
    assert "from 0 to 4;" in field.toolTip()
    QTest.keyClicks(field, "4")
    assert filters.stacks == {night_invader: 4} and field.styleSheet() == ""
    field.clear()
    QTest.keyClicks(field, "5")
    assert filters.stacks == {} and dlg.BAD in field.styleSheet()
    window.close()
    window.deleteLater()


def test_typing_a_stacks_value_writes_through_and_clearing_empties_it(
        stack_window, filters):
    field = stack_window.stack_fields[STACKING]
    QTest.keyClicks(field, "2")
    assert filters.stacks == {STACKING: 2}
    assert effectfilters.stored_stacks() == {STACKING: 2}
    QTest.keyClick(field, Qt.Key_Backspace)
    assert filters.stacks == {} and field.text() == ""
    QTest.keyClicks(field, "0")
    assert filters.stacks == {STACKING: 0} and field.text() == "0"


@pytest.mark.parametrize("typed", ["2.5", "-1", "x", "11", "100", "2 "])
def test_a_text_that_is_no_count_stays_as_typed_in_red_and_counts_as_empty(
        stack_window, filters, typed):
    """`2.5` once became 25: the validator swallowed the point and let the 5
    through, and 100 became 10 the same way."""
    field = stack_window.stack_fields[STACKING]
    QTest.keyClicks(field, typed)
    assert field.text() == typed
    assert BAD in field.styleSheet()
    assert filters.stacks == {}
    assert effectfilters.stored_stacks() == {}


def test_a_refused_text_stays_when_another_mark_is_drawn_and_can_be_put_right(
        stack_window, filters):
    field = stack_window.stack_fields[STACKING]
    QTest.keyClicks(field, "2.5")
    filters.mark(10, effectfilters.REQUIRED)
    assert field.text() == "2.5" and BAD in field.styleSheet()
    field.clear()
    QTest.keyClicks(field, "5")
    assert filters.stacks == {STACKING: 5}
    assert field.text() == "5" and field.styleSheet() == ""


def test_a_stacks_field_counts_the_largest_value_and_a_zero_in_front(
        stack_window, filters):
    field = stack_window.stack_fields[STACKING]
    QTest.keyClicks(field, "10")
    assert filters.stacks == {STACKING: 10} and field.styleSheet() == ""
    field.clear()
    QTest.keyClicks(field, "07")
    assert filters.stacks == {STACKING: 7} and field.text() == "7"


def test_a_stacks_field_refuses_a_digit_of_another_script(stack_window, filters):
    """By `insert`, as a paste: `QTest.keyClicks` ends the process on anything
    outside Latin-1."""
    field = stack_window.stack_fields[STACKING]
    field.insert("٣")
    assert field.text() == "٣" and BAD in field.styleSheet()
    assert filters.stacks == {}


def test_a_stacks_value_is_drawn_at_opening_and_when_it_changes(
        qapp, filters, stack_window):
    filters.set_stacks(STACKING, 4)
    assert stack_window.stack_fields[STACKING].text() == "4"
    filters.set_stacks(STACKING, None)
    assert stack_window.stack_fields[STACKING].text() == ""
    filters.set_stacks(STACKING_MEMBER, 0)
    rows = dlg.rows_from(_owned(_relic(13, 16)), STACK_EFFECTS, STACK_FAMILIES)
    opened = dlg.EffectFilterWindow(filters, rows)
    assert opened.stack_fields[STACKING_MEMBER].text() == "0"
    opened.deleteLater()


def test_sorting_by_stacks_puts_empty_under_zero_and_keeps_the_family(
        stack_window, filters):
    window = stack_window
    filters.set_stacks(STACKING, 0)
    filters.set_stacks(STACKING_MEMBER, 3)
    window.tree.sortItems(dlg.COL_STACKS, Qt.DescendingOrder)
    top = _top_level(window)
    assert top[0].data(dlg.COL_NAME, Qt.UserRole) == STACKING
    assert window.tree.itemWidget(top[0], dlg.COL_STACKS) is (
        window.stack_fields[STACKING])
    head = _head(window)
    assert head.childCount() == 2
    assert head.child(0).data(dlg.COL_NAME, Qt.UserRole) == STACKING_MEMBER
    window.tree.sortItems(dlg.COL_STACKS, Qt.AscendingOrder)
    assert _top_level(window)[-1].data(dlg.COL_NAME, Qt.UserRole) == STACKING


def test_the_search_hides_a_row_with_its_stacks_field_and_keeps_the_value(
        stack_window, filters):
    filters.set_stacks(STACKING, 2)
    stack_window.search.setText("vigor")
    assert STACKING not in stack_window.shown_ids()
    stack_window.search.setText("")
    assert STACKING in stack_window.shown_ids()
    assert stack_window.stack_fields[STACKING].text() == "2"


def test_a_row_with_a_stacks_field_is_as_high_as_one_without(stack_window):
    """AK-469: the field's own size hint made its row 1.5 times as high. A red
    text changes the field's style, and must not bring that back."""
    window = stack_window
    window.show()
    QApplication.processEvents()

    def row_heights() -> dict[int, int]:
        return {effect_id: window.tree.visualItemRect(
                    window._marks[effect_id][-1]).height()
                for effect_id in (11, STACKING, STACKING_MEMBER)}

    assert len(set(row_heights().values())) == 1, row_heights()
    QTest.keyClicks(window.stack_fields[STACKING], "11")
    QApplication.processEvents()
    assert len(set(row_heights().values())) == 1, row_heights()
    assert row_heights()[11] > 0


def test_tab_reaches_the_stacks_field_after_the_boxes_of_its_row(stack_window):
    """After Ignore, on a single and on a member alike."""
    window = stack_window
    window.show()
    QApplication.processEvents()
    avoid = window.boxes(STACKING)[1]
    avoid.setFocus()
    QApplication.processEvents()
    QTest.keyClick(avoid, Qt.Key_Tab)
    assert QApplication.focusWidget() is window.ignore_box(STACKING)
    QTest.keyClick(window.ignore_box(STACKING), Qt.Key_Tab)
    assert QApplication.focusWidget() is window.stack_fields[STACKING]
    last = window.ignore_box(STACKING_MEMBER)
    last.setFocus()
    QApplication.processEvents()
    QTest.keyClick(last, Qt.Key_Tab)
    assert QApplication.focusWidget() is window.stack_fields[STACKING_MEMBER]


def test_favourite_on_a_family_header_asks_for_any_one_member(window, filters):
    """User decision 2026-11-15: the header's Favourite box, stored like the
    Avoid one, and a family is one or the other."""
    try:
        favour = window.family_favourite_box(FAMILY)
        assert favour.toolTip() == dlg.FAMILY_FAVOURITE_TOOLTIP
        favour.click()
        assert filters.favourite_families == {FAMILY}
        assert filters.favoured == {13, 14}
        assert filters.favourite_groups(
            lambda effect_id: EFFECTS[str(effect_id)]["name"]) in (
                ((13, 14),), ((14, 13),))
        restarted = effectfilters.EffectFilters(families=FAMILIES)
        assert restarted.favourite_families == {FAMILY}

        window.family_box(FAMILY).click()
        assert filters.avoided_families == {FAMILY}
        assert filters.favourite_families == set()
        assert not favour.isChecked()
    finally:
        filters.favour_family(FAMILY, False)


def test_ignore_is_the_third_box_on_a_row_and_on_a_heading(window, filters):
    """User request 2026-11-16: the effect may be there and counts as
    nothing. One state per row, like the other boxes; on a heading the whole
    family, and a family is avoided, favourited or ignored."""
    assert dlg.HEADINGS[dlg.COL_IGNORE] == "Ignore"
    ignore = window.ignore_box(11)
    assert ignore.toolTip() == dlg.IGNORE_TOOLTIP
    ignore.click()
    assert filters.ignored == {11} and filters.resolved_ignored == {11}
    assert "1 ignored" in window.counter.text()
    assert effectfilters.EffectFilters(families=FAMILIES).ignored == {11}

    window.boxes(11)[1].click()
    assert filters.excluded == {11} and not filters.ignored
    assert not ignore.isChecked()
    ignore.click()
    assert filters.ignored == {11} and not filters.excluded
    assert not window.boxes(11)[1].isChecked()

    family = window.family_ignore_box(FAMILY)
    assert family.toolTip() == dlg.FAMILY_IGNORE_TOOLTIP
    family.click()
    assert filters.ignored_families == {FAMILY}
    assert filters.resolved_ignored == {11, 13, 14}
    assert "3 ignored" not in window.counter.text()
    assert "2 ignored" in window.counter.text()
    window.family_box(FAMILY).click()
    assert filters.avoided_families == {FAMILY}
    assert not filters.ignored_families and not family.isChecked()
    assert filters.resolved_ignored == {11}


# -- one row per name (owner, 23.11.2026) -------------------------------------

TWINS = {"20": {"name": "Taking attacks improves attack power"},
         "21": {"name": "Taking attacks improves attack power"},
         "22": {"name": "Taking attacks improves attack power"}}
TWIN_FAMILIES = {20: "Taking attacks improves attack power",
                 21: "Taking attacks improves attack power",
                 22: "Taking attacks improves attack power"}


def test_several_entries_of_one_name_are_one_row():
    """The game keeps "Taking attacks improves attack power" as three
    entries and shows one name. Three equal rows under a heading read as
    levels of an effect that has one. One row, the id most relics carry
    first, `Copies` in relics that carry any of them."""
    (row,) = dlg.rows_from(
        _owned(_relic(21), _relic(20), _relic(21, 22), _relic(22, 22)),
        TWINS, TWIN_FAMILIES)

    assert row.name == "Taking attacks improves attack power"
    assert row.all_ids == (21, 22, 20)
    assert row.effect_id == 21 and row.copies == 4


def test_a_box_on_a_row_of_several_entries_marks_them_all(qapp, filters):
    """One box, one mark: every id of the row goes into the set in one
    write, the row reads marked while all of them are, and the counter says
    one mark."""
    filters.names = {int(i): e["name"] for i, e in TWINS.items()}
    rows = dlg.rows_from(_owned(_relic(20), _relic(21), _relic(22)),
                         TWINS, TWIN_FAMILIES)
    window = dlg.EffectFilterWindow(filters, rows)
    try:
        _favourite, avoid = window.boxes(22)
        assert window.shown_ids() == [20]
        avoid.click()
        assert filters.excluded == {20, 21, 22}
        assert avoid.isChecked()
        assert "1 avoided" in window.counter.text()
        filters.mark(21, None)
        assert not avoid.isChecked()
    finally:
        filters.mark_all((20, 21, 22), None)
        window.deleteLater()
