"""What the effects table puts on screen, read off the table.

**What guarded this tab before this file: nothing.** Two independent searches
of `tests/` on 2026-09-05 -- for the module name `effectstab` and for the
class name `EffectsTab` -- found 0 files. Multiplying `format_chance` by 1000
instead of 100, so every percentage on the tab read ten times over, left
622 of 622 green (QA-137, mutation M4).

Three of the tab's figures did not mean what their heading said, and all three
are checked here against numbers this file works out for itself:

* `Avg chance` averaged the (colour x mode) buckets instead of the slots
  (QA-126). The expectation below is computed from the effect's own chance
  entries, never by calling the tab.
* `Pools` counted relic effect slots (QA-125). Both the new heading and the
  sentence that has to be gone are pinned.
* `Tier` and `Copies` were built from the filtered view (QA-127), so an effect
  described its own ladder differently depending on which colours were shown.

**The percentage is formatted here rather than imported.** `format_chance` is
the function mutation M4 breaks, so a case that called it would agree with
whatever it does. The rule is written out again on purpose; that duplication
is the whole guard.
"""

from __future__ import annotations

import pytest

from nrplanner import effectstab

from tests import tabtext

#: The one sentence AK-79 allows on this tab about what a chance is a chance
#: of, verbatim, and the two it replaces. Written out rather than imported for
#: the reason at the top of this file.
CHANCE_DEFINITION = (
    "Chance is per relic effect slot, over every slot that can roll the "
    "effect under the filters above — not per relic and not per run.")
GONE = (
    "averaged over every pool that can produce it",
    "how likely an effect is on one roll",
    "A pool is one of the lists a relic's effects are drawn from",
)

#: AK-78, the heading and the tooltip the renamed column carries.
SLOTS_HEADER = "Relic slots"
SLOTS_TIP = (
    "How many of the game's relic effect slots can roll this effect, counted "
    "over every relic and every slot on it. It is not a count of loot pools, "
    "and more slots does not mean more likely — the chance column says that.")

#: The effect QA-126 measured the divergence on. Looked up by name, so the
#: case fails loudly if the dataset stops carrying it rather than quietly
#: checking nothing.
DIVERGENT = "[Wylder] Improved Mind, Reduced Vigor"


@pytest.fixture
def tab(game_data, qapp):
    widget = effectstab.EffectsTab(game_data)
    yield widget
    widget.deleteLater()


def as_shown(value: float) -> str:
    """A chance the way the tab writes it, from the rule and not the code."""
    if value >= 0.01:
        return f"{value * 100:.1f}%"
    return f"{value * 100:.2f}%"


def buckets(effect: dict) -> list[dict]:
    """Every (colour x mode) chance entry of one effect, at no filter."""
    out = []
    for key in ("chance", "deep_chance"):
        out += list((effect.get(key) or {}).values())
    return out


def cell(tab, name: str, column: str) -> str:
    """One cell of the row carrying this effect name, by column heading."""
    index = effectstab.COLUMNS.index(column)
    for row in range(tab.table.rowCount()):
        if tab.table.item(row, 0).text() == name:
            return tab.table.item(row, index).text()
    raise LookupError(
        f"no row named {name!r} on the tab; the table shows "
        f"{tab.table.rowCount()} rows")


def rows_named(tab, name: str) -> list[int]:
    return [row for row in range(tab.table.rowCount())
            if tab.table.item(row, 0).text() == name]


def test_the_average_is_weighted_by_how_many_slots_each_entry_stands_for(
        tab, game_data):
    """QA-126 and AK-80, on the effect the divergence was measured on.

    `[Wylder] Improved Mind, Reduced Vigor` carries one guaranteed slot at
    100% and 240 slots at 0.5012%. Averaged over the five buckets the single
    slot takes a fifth of the weight and the tab printed 20.4%; weighted by
    occurrence it is 0.91%, a factor of 22 apart.

    Both figures are computed here. The case refuses to run if they round to
    the same string, because it could then not tell a weighted average from an
    unweighted one -- which is the only thing it is for.
    """
    effect = next(e for e in game_data["effects"].values()
                  if " ".join(str(e.get("name", "")).split()) == DIVERGENT)
    entries = buckets(effect)
    slots = sum(entry["pools"] for entry in entries)
    weighted = sum(entry["avg"] * entry["pools"] for entry in entries) / slots
    unweighted = sum(entry["avg"] for entry in entries) / len(entries)

    assert as_shown(weighted) != as_shown(unweighted), (
        f"{DIVERGENT!r} rounds to the same string either way "
        f"({as_shown(weighted)}), so this case cannot tell the two averages "
        f"apart. Pick an effect whose buckets differ in size.")

    tab.search.setText(DIVERGENT)
    assert cell(tab, DIVERGENT, "Avg chance") == as_shown(weighted), (
        f"the tab does not show the occurrence-weighted average for "
        f"{DIVERGENT!r}; unweighted would be {as_shown(unweighted)}")


def test_every_row_shows_the_weighted_average_and_the_best_slot(tab,
                                                                game_data):
    """The same claim over the whole table, so it is not one lucky row.

    Read cell by cell against figures worked out here from the dataset. This
    is the case mutation M4 dies on: with `format_chance` multiplying by 1000
    every one of these strings moves, and with the average unweighted 129 of
    616 do.
    """
    by_name = {}
    for effect in game_data["effects"].values():
        by_name.setdefault(
            " ".join(str(effect.get("name", "")).split()), []).append(effect)

    checked = 0
    seen: set[str] = set()
    for row in range(tab.table.rowCount()):
        name = tab.table.item(row, 0).text()
        candidates = by_name.get(name) or []
        # Two genuinely different effects can share a name, and the table
        # merges by more than the name (see `effectstab.identity`). Only rows
        # whose name picks out exactly one effect are compared.
        if len(candidates) != 1:
            continue
        entries = buckets(candidates[0])
        slots = sum(entry["pools"] for entry in entries)
        if not slots:
            continue
        weighted = (sum(entry["avg"] * entry["pools"] for entry in entries)
                    / slots)
        best = max(entry["max"] for entry in entries)
        assert cell(tab, name, "Avg chance") == as_shown(weighted), name
        assert cell(tab, name, "Best chance") == as_shown(best), name
        assert cell(tab, name, "Relic slots") == str(slots), name
        checked += 1
        seen.add(as_shown(weighted))

    assert checked > 100, (
        f"only {checked} rows could be compared, which is too few to stand "
        f"for the table")
    assert len(seen) > 10, (
        "every row compared shows the same percentage, so an assertion on it "
        "could not tell one effect from another")


def test_the_slot_column_says_what_it_counts(tab):
    """QA-125: the column counted relic effect slots and was named for pools.

    The heading and its tooltip are both pinned, and the sentence that
    explained the word `pool` has to be gone from the tab entirely -- it
    described something the figure never was.

    Read through `heading()` rather than off the header item, because since
    QA-140 the item carries whatever fits the section it has been given and a
    narrow window shortens it. The name a reader can still reach is the one in
    the tooltip, which is asserted here in full.
    """
    column = effectstab.COLUMNS.index(SLOTS_HEADER)
    header = tab.table.horizontalHeaderItem(column)
    assert header is not None and tab.table.heading(column) == SLOTS_HEADER
    assert tabtext.plain(header.toolTip()) == f"{SLOTS_HEADER} {SLOTS_TIP}"

    headings = [tab.table.heading(c) for c in range(tab.table.columnCount())]
    assert "Pools" not in headings, (
        f"a column is still headed `Pools`: {headings!r}")


def test_one_definition_of_chance_and_only_one(tab):
    """AK-79. Two definitions stood six lines apart and disagreed.

    Counted over labels, tooltips, headers and cells together: a count that
    skipped the tooltips would pass with the sentence standing twice, which is
    the state this criterion exists to end.
    """
    everything = tabtext.everything(tab)
    assert CHANCE_DEFINITION in everything, (
        "the tab does not carry the one sentence saying what a chance is a "
        "chance of")
    assert everything.count("per relic effect slot") == 1, (
        f"`per relic effect slot` appears "
        f"{everything.count('per relic effect slot')} times on this tab")
    for sentence in GONE:
        assert sentence not in everything, (
            f"a definition AK-78/AK-79 removed is still on screen: "
            f"{sentence!r}")


def test_the_ladder_rung_does_not_change_with_the_colour_filter(tab,
                                                                game_data):
    """QA-127 and AK-81: a ladder is a property of the data, not of the view.

    Under `All colours` an effect that comes in a ladder of strengths shows
    which rung it is. Under a colour filter the same row used to show an empty
    cell, because the ladder was rebuilt from whatever the filter left.

    The effect is chosen by asking the dataset for one that is both a ladder
    and reachable under a single colour, not by writing a name down here.
    """
    tab.colour_box.setCurrentIndex(0)
    assert tab.colour_box.currentData() == -1, "expected `All colours` first"

    unfiltered = {}
    for row in range(tab.table.rowCount()):
        rung = tab.table.item(row, effectstab.COLUMNS.index("Tier")).text()
        colours = tab.table.item(row, effectstab.COLUMNS.index("Colours"))
        if rung:
            unfiltered.setdefault(
                (tab.table.item(row, 0).text(), rung), colours.text())

    assert unfiltered, "no effect on this tab comes in a ladder of strengths"

    for index in range(tab.colour_box.count()):
        if tab.colour_box.itemData(index) == -1:
            continue
        tab.colour_box.setCurrentIndex(index)
        colour = tab.colour_box.itemText(index)
        for row in range(tab.table.rowCount()):
            name = tab.table.item(row, 0).text()
            rung = tab.table.item(row, effectstab.COLUMNS.index("Tier")).text()
            available = [r for (n, r) in unfiltered if n == name]
            if not available:
                continue
            assert rung in available, (
                f"{name!r} shows rung {rung!r} under the {colour} filter and "
                f"{available!r} with no filter, so the ladder is being built "
                f"from the filtered view")


def test_the_tab_opens_with_the_question_it_answers(tab):
    """AK-68 and AK-76: the heading stands above the filters and the counts.

    Until T-057 the first line a reader met was `577 buffs (blue) then 75
    curses (red).` -- a stock count, before anything said what the stock was
    for.
    """
    lines = tabtext.labels(tab)
    assert lines[0] == effectstab.HEADING
    assert lines[1] == effectstab.QUESTION
    assert not any(character.isdigit() for character in lines[0]), (
        f"the first line of the tab carries a figure: {lines[0]!r}")


# -- QA-156: the last two "I would have guessed" ---------------------------
#
# A11 is measured on a player finishing without guessing, and after T-065 two
# guesses were left on this tab. Both are a reader having to work out what he
# is looking at from something other than words on the screen.
#
# (a) `Copies` showed a bare 1 or 2 and was explained only in a header
#     tooltip, which opens after about three quarters of a second of a
#     pointer held still. He never reached it and guessed "how many identical
#     copies exist in different slots" -- which is what `Relic slots` counts.
#     Measured against the dataset on 2026-09-06: 2 076 effect rows resolve
#     to 1 064 distinct effects, and under the tab's opening filters 620 rows
#     say 1, 29 say 2, two say 3 and one says 4. So the column counts entries
#     in the game's own table -- and 29 of the 68 repeated effects differ
#     between their copies in the colours they can roll on, which is why the
#     count has to be the game's and not the view's, and why saying so is
#     part of the definition rather than a footnote.
#
# (b) The four filter boxes carried no caption, so he read the value each one
#     happened to be showing and worked backwards to the question.

#: The heading whose meaning QA-156 says is unreachable. Written out rather
#: than imported, for the reason at the top of this file.
COPIES_HEADER = "Copies"

#: The two columns the definition of `Copies` has to keep it apart from. The
#: first is the reading the player actually arrived at.
NOT_COPIES = ("Relic slots", "Stacking")

#: Which filter box narrows which column of the table. The mode box is absent
#: on purpose: choosing between ordinary and Deep of Night relics is not a
#: column of this table, and inventing one to caption it would be a rule made
#: to be tidy rather than to be true.
BOX_COLUMNS = (("colour_box", "Colours"),
               ("stacking_box", "Stacking"),
               ("kind_box", "Type"))


def headings(tab) -> list[str]:
    """Every column heading, as the table itself would draw it whole."""
    return [tab.table.heading(column)
            for column in range(tab.table.columnCount())]


def column_of(tab, heading: str) -> int:
    found = headings(tab)
    assert heading in found, (
        f"no column of this table is headed {heading!r} any more; it shows "
        f"{found}")
    return found.index(heading)


def row_key(tab, row) -> tuple:
    """What tells one row of this table from another.

    Not the name: 46 of the 652 rows share a display name with another row,
    because the game gives two genuinely different effects the same words.
    The rung and the description are properties of the effect itself and do
    not move when a filter narrows the view, which is what a case comparing
    two views needs.
    """
    return tuple(tab.table.item(row, column_of(tab, heading)).text()
                 for heading in ("Effect", "Tier", "What it does"))


def visible(widget) -> str:
    """Every piece of text the tab shows without being hovered.

    `tabtext.everything` counts tooltips too, and a tooltip is exactly what
    QA-156 says the reader did not reach. This is the half of the tab that is
    simply there.
    """
    return "\n".join(tabtext.labels(widget))


def place_of(tab, box):
    """The layout row `box` sits in, and where in it -- walking the real tree.

    Not `findChildren`: what the case needs is the row a reader sees, which
    is one layout and an index in it, and the ordering is the whole point of
    "the caption stands beside the box".
    """
    pending = [tab.layout()]
    while pending:
        layout = pending.pop()
        for index in range(layout.count()):
            item = layout.itemAt(index)
            if item.widget() is box:
                return layout, index
            if item.layout() is not None:
                pending.append(item.layout())
    return None, -1


def caption_before(tab, box):
    """The label immediately before `box` in its own row, if there is one."""
    from PySide6.QtWidgets import QLabel

    row, index = place_of(tab, box)
    if row is None:
        return None
    for back in range(index - 1, -1, -1):
        widget = row.itemAt(back).widget()
        if isinstance(widget, QLabel):
            return widget
        if widget is not None:
            return None
    return None


def filter_boxes(tab) -> list:
    """The four drop-downs of the filter row."""
    return [tab.colour_box, tab.mode_box, tab.stacking_box, tab.kind_box]


def test_copies_is_explained_where_the_reader_is_already_looking(tab):
    """QA-156a. The answer may not live only in a tooltip.

    `Tier` is explained in the sentence over the table and the player read it
    there; `Copies` was explained on the header alone and he did not. So the
    criterion is the always-visible text of the tab, tooltips excluded.
    """
    heading = headings(tab)[column_of(tab, COPIES_HEADER)]
    shown = visible(tab)
    assert heading in shown, (
        f"nothing a reader can see without hovering names the {heading!r} "
        f"column: {shown!r}")


def test_the_explanation_of_copies_keeps_it_apart_from_the_two_it_is_not(tab):
    """The guess itself, refuted on screen.

    "How many identical copies exist in different slots" is `Relic slots`,
    and "what a second one is worth" is `Stacking`. A sentence that said what
    `Copies` counts without saying which of its neighbours it is not would
    leave the reading he arrived at standing.
    """
    shown = visible(tab)
    for column in NOT_COPIES:
        assert column in headings(tab), (
            f"this table has no {column!r} column any more, so the sentence "
            f"under test would be pointing at nothing")
    missing = [column for column in NOT_COPIES if column not in shown]
    assert not missing, (
        f"the visible text of the tab never names {missing}, so nothing "
        f"tells a reader that {COPIES_HEADER!r} is not one of them")


def test_the_header_and_the_sentence_say_one_thing_about_copies(tab):
    """One definition in two places, and it has to be the same one.

    Both are wanted: the sentence over the table for a reader scanning it,
    the header tooltip for a reader who meets a heading shortened to `Co...`.
    What must not happen is the two drifting apart, which is AK-79's finding
    with another column's name on it. So the tooltip's explanation has to
    stand verbatim in the visible text.
    """
    column = column_of(tab, COPIES_HEADER)
    tip = tabtext.plain(tab.table.horizontalHeaderItem(column).toolTip())
    assert tip.startswith(COPIES_HEADER), (
        f"the header tooltip no longer leads with the column's own name: "
        f"{tip!r}")
    explanation = tip[len(COPIES_HEADER):].strip()
    assert explanation, (
        f"the {COPIES_HEADER!r} header carries nothing but its own name, so "
        f"a heading shortened to `Co...` answers with nothing")
    assert explanation in tabtext.plain(visible(tab)), (
        f"the header explains {COPIES_HEADER!r} in words the rest of the tab "
        f"does not use, so the two can drift apart: {explanation!r}")


def test_the_copies_count_does_not_move_when_a_filter_hides_a_copy(tab):
    """AK-81 for `Copies`, and the clause of the definition that needs it.

    The definition says the count is of the game's own entries "whatever the
    filters show". That is only true while it is: 29 of the 68 repeated
    effects differ between their copies in the colours they roll on, so a
    colour filter can leave one copy out of the view. If the count followed
    the view, the sentence over the table would be a false statement about a
    number the reader can see beside it.
    """
    column = column_of(tab, COPIES_HEADER)
    tab.colour_box.setCurrentIndex(0)
    assert tab.colour_box.currentData() == -1, "expected `All colours` first"

    unfiltered = {}
    for row in range(tab.table.rowCount()):
        unfiltered.setdefault(row_key(tab, row), []).append(
            tab.table.item(row, column).text())
    # A name alone does not name a row: 46 of the 652 rows share a display
    # name with another (the same words over genuinely different effects --
    # `Increased Maximum HP` is Max HP +10 % on one row and Vigor +5 on
    # another). Keyed by name alone this case reported the Copies count as
    # following the filter when what had changed was which of two rows the
    # name matched. Rows whose key is still not unique are left out rather
    # than compared to the wrong twin.
    settled = {key: counts[0] for key, counts in unfiltered.items()
               if len(counts) == 1}
    repeated = [key for key, count in settled.items() if count != "1"]
    assert repeated, (
        "no effect in this dataset is defined more than once, so this case "
        "is watching nothing")

    moved = []
    for index in range(tab.colour_box.count()):
        if tab.colour_box.itemData(index) == -1:
            continue
        tab.colour_box.setCurrentIndex(index)
        colour = tab.colour_box.itemText(index)
        for row in range(tab.table.rowCount()):
            key = row_key(tab, row)
            here = tab.table.item(row, column).text()
            if key in settled and here != settled[key]:
                moved.append((key[0], colour, settled[key], here))
    assert not moved, (
        f"the {COPIES_HEADER!r} count follows the filter for these rows "
        f"(name, filter, unfiltered, filtered): {moved[:5]}")


def test_every_filter_box_says_what_it_filters(tab):
    """QA-156b. Four drop-downs and no caption on any of them.

    The caption is read off the layout, and it has to be a label rather than
    one of the box's own values: a box captioned `All colours` would be the
    state the finding describes, where the reader works out the question from
    the answer currently showing.
    """
    unlabelled = []
    for box in filter_boxes(tab):
        label = caption_before(tab, box)
        values = [box.itemText(i) for i in range(box.count())]
        if label is None or not label.text().strip():
            unlabelled.append((values[0], "no caption"))
        elif label.text() in values:
            unlabelled.append((values[0], f"captioned {label.text()!r}, "
                                          f"which is one of its own values"))
    assert not unlabelled, (
        f"these filter boxes do not say what they filter: {unlabelled}")


def test_the_filter_captions_are_the_names_the_table_uses(tab):
    """One word per idea, on the row and in the table (A13).

    A row that said `Kind` where the table says `Type` would make a reader
    check whether the two are the same thing.

    Three of the four boxes narrow a column of the table and are held to that
    column's heading, singular or plural. The fourth chooses between ordinary
    and Deep of Night relics, which is not a column of anything -- so it is
    held only to having a caption at all, by the case above. Requiring a
    column for it would be a rule invented to be tidy.
    """
    known = set(headings(tab))
    for box, heading in BOX_COLUMNS:
        caption = caption_before(tab, getattr(tab, box))
        assert caption is not None, (
            f"{box} has no caption, which the case above is about")
        assert heading in known, (
            f"this table has no {heading!r} column, so {box} cannot be held "
            f"to it; the headings are {sorted(known)}")
        assert caption.text() in (heading, heading.rstrip("s")), (
            f"{box} is captioned {caption.text()!r} while the column it "
            f"narrows is headed {heading!r}")

    captions = [caption_before(tab, box) for box in filter_boxes(tab)]
    words = [caption.text() for caption in captions if caption is not None]
    assert len(set(words)) == len(words), (
        f"two filter boxes carry the same caption: {words}")


def test_the_filter_captions_do_not_set_the_window_floor(tab):
    """What the captions may cost, measured by taking them away again.

    `QTabWidget` hands the widest page's minimum width to the whole window, so
    a word on this row is a floor under the program. Four plain `QLabel`s cost
    the tab 160 logical px on Windows and, under the font the suite renders
    with, took the window's floor from 964 px to 1276 -- above three of the
    four widths the geometry cases measure at, so 47 of them skipped
    themselves in one run and the suite went green anyway. A silent skip is
    the most expensive way this repository has found to lose a guard.

    The allowance is the row's own spacing, read off the layout: a widget in a
    layout costs at least the gap in front of it however narrow it is, and no
    caption can give that back. Everything above that would be text setting a
    floor.
    """
    row, _index = place_of(tab, tab.colour_box)
    captions = [caption_before(tab, box) for box in filter_boxes(tab)]
    assert all(caption is not None for caption in captions), (
        "a filter box has no caption, so this case is measuring nothing")

    with_captions = tab.minimumSizeHint().width()
    for caption in captions:
        caption.hide()
    tab.layout().activate()
    without = tab.minimumSizeHint().width()
    for caption in captions:
        caption.show()
    tab.layout().activate()

    allowed = row.spacing() * len(captions)
    assert with_captions - without <= allowed, (
        f"the four filter captions add {with_captions - without} px to the "
        f"tab's minimum width, and only the row's own spacing "
        f"({row.spacing()} px each, {allowed} px in all) is free. A word on "
        f"this row becomes the whole window's floor.")
