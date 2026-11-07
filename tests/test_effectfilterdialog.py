"""The effect filter window (`UI_SPEC` §3.6, AK-303..309, AK-311, AK-316,
AK-317).

Driven with a hand-built inventory, so every count below is a count the
case wrote down; one case takes the frozen save to show the real dataset
gives the rows their names and families.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QValidator
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QTreeWidget, QApplication, QLabel

from nrplanner import effectfilterdialog as dlg
from nrplanner import effectfilters, effecttext, inventory

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
    for effect_id in set(marks.excluded | marks.required | marks.allowed):
        marks.mark(effect_id, None)
    for key in set(marks.avoided_families):
        marks.mark_family(key, False)


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
    assert rows[10] == dlg.Row(10, "Vigor +2", False, 3, "Vigor")
    assert rows[90] == dlg.Row(90, "Reduced HP", True, 1, "Reduced HP")
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


def test_a_family_of_two_or_more_rows_has_a_heading_with_avoid_only(window):
    """AK-316.1: the heading carries the family key as its name, the sum
    of copies, one Avoid box and nothing else; members carry Allow, a
    headless single does not."""
    head = _head(window)
    assert head.text(dlg.COL_NAME) == FAMILY
    assert head.text(dlg.COL_TYPE) == ""
    assert head.data(dlg.COL_COPIES, Qt.DisplayRole) == 2
    assert head.childCount() == 2 and head.isExpanded()
    assert window.tree.itemWidget(head, dlg.COL_AVOID) is window.family_box(FAMILY)
    assert window.family_box(FAMILY).toolTip() == dlg.FAMILY_AVOID_TOOLTIP
    for column in (dlg.COL_FAVOURITE, dlg.COL_ALLOW):
        assert window.tree.itemWidget(head, column) is None
    assert window.allow_box(13) is not None
    assert window.allow_box(10) is None
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


def test_allow_is_clickable_regardless_of_the_family_state(window, filters):
    """AK-316.3, AK-317 Nachtrag: the heading's box calls `mark_family`
    both ways; Allow stays enabled and keeps one tooltip whether or not
    the family is avoided, and its stored check survives the family
    toggling either way."""
    allow = window.allow_box(13)
    assert allow.isEnabled()
    assert allow.toolTip() == dlg.ALLOW_TOOLTIP
    allow.click()
    assert filters.allowed == {13}
    # Not yet avoided, so Allow has nothing to pull back in.
    assert filters.resolved_excluded == set()
    window.family_box(FAMILY).click()
    assert filters.avoided_families == {FAMILY}
    assert allow.isEnabled() and allow.isChecked()
    assert filters.resolved_excluded == {14}
    # The members' own marks are untouched by the family (AK-316.3).
    assert not window.boxes(13)[1].isChecked()
    window.family_box(FAMILY).click()
    assert filters.avoided_families == set()
    assert allow.isChecked() and allow.isEnabled()


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


def test_tab_walks_favourite_avoid_allow_and_space_toggles(window, filters):
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
    assert QApplication.focusWidget() is window.allow_box(13)
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
    id, one row per distinct id -- and the user's two dagger effects sit
    in one family (AD-039)."""
    effects = game_data["effects"]
    families = {int(i): effecttext.family_key(e, game_data["weapon_families"])
                for i, e in effects.items()}
    rows = dlg.rows_from(frozen_inventory, effects, families)
    ids = {i for item in frozen_inventory.relics
           for i in (*item.effect_ids, *item.curse_ids)}
    assert len(rows) == len(ids) > 0
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
        "Favourite: every suggestion for this Nightfarer must carry this "
        "effect, if it can. Avoid: no "
        "suggestion uses a relic that carries it — on a family header, every "
        "member below, unless one is set to Allow. Allow lets that one member "
        "back in without allowing the rest of the family. These marks are saved "
        "for every Nightfarer; one that only works for another "
        "Nightfarer is ignored here. They are separate from the ★ you can give a "
        "relic in the relic picker: that is per Nightfarer, and Optimize puts "
        "a favourited relic in when it fits. Stacks: how many stacks Optimize "
        "counts for an effect that stacks; 0 does not count it, empty uses the "
        "stat sheet's count.")
    assert dlg.FAVOURITE_TOOLTIP == (
        "Every suggestion for this Nightfarer must carry this effect, if it "
        "can.")
    assert dlg.AVOID_TOOLTIP == (
        "No suggestion uses a relic that carries this effect.")
    assert dlg.FAMILY_AVOID_TOOLTIP == (
        "No suggestion uses a relic that carries an effect of this family, "
        "unless a member below is set to Allow.")
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
    assert field.toolTip() == dlg.STACKS_TOOLTIP
    assert field.accessibleName() == "Stacks: Attack up for each kill"
    assert window.tree.itemWidget(window._marks[STACKING][-1],
                                  dlg.COL_STACKS) is field


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


@pytest.mark.parametrize("typed, kept", [("-1", "1"), ("x", ""), ("1.5", "15"),
                                         ("1234", "123")])
def test_a_stacks_field_takes_a_whole_number_of_at_most_three_digits(
        stack_window, filters, typed, kept):
    field = stack_window.stack_fields[STACKING]
    QTest.keyClicks(field, typed)
    assert field.text() == kept
    assert filters.stacks == ({STACKING: int(kept)} if kept else {})


def test_a_stacks_field_refuses_a_digit_of_another_script(stack_window):
    """Asked of the validator: `QTest.keyClicks` ends the process on anything
    outside Latin-1."""
    state = stack_window.stack_fields[STACKING].validator().validate("٣", 0)
    assert state[0] == QValidator.State.Invalid


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


def test_tab_reaches_the_stacks_field_after_the_boxes_of_its_row(stack_window):
    """On a member after Allow, on a single after Avoid."""
    window = stack_window
    window.show()
    QApplication.processEvents()
    avoid = window.boxes(STACKING)[1]
    avoid.setFocus()
    QApplication.processEvents()
    QTest.keyClick(avoid, Qt.Key_Tab)
    assert QApplication.focusWidget() is window.stack_fields[STACKING]
    allow = window.allow_box(STACKING_MEMBER)
    allow.setFocus()
    QApplication.processEvents()
    QTest.keyClick(allow, Qt.Key_Tab)
    assert QApplication.focusWidget() is window.stack_fields[STACKING_MEMBER]
