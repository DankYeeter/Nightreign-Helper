"""The suggestion in the slot card and the `Why` dialog, line for line.

**Why the cases build their own answers.** Every shape this draws --
`ReasonLine`, `SlotReasons`, `AdvisorResult` -- is frozen and holds nothing
but scalars and tuples, so a case can state the exact awkward group it wants
instead of hunting the player's save for one: a curse with no figure, an
effect that belongs to another Nightfarer, two slots whose relics share a
name. The three findings this task was warned about are all of that kind, and
none of them is guaranteed to be in any one save.

**Nothing here checks a line by its wording where a shape will do.** The
display decides bullet, colour and strikethrough from `is_curse` and
`silence`; a case that looked for `works only for` in the markup would agree
with a display that read the sentence too, which is the coupling AK-147
forbids.

**Nothing here matches a line to a slot by a relic name.** QA-180 is open --
`Build.sources` tells two effects of one name apart by id, and 23 of 296 best
suggestions have a slot whose reasoning went to the wrong relic. A case that
asked "which card shows the line naming *Increased Maximum HP*" would report
that defect as a display defect and would keep reporting it after it is
fixed. The cases ask by `slot_index`, which is the only thing that addresses a
slot.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractButton, QLabel

from nrplanner import advisorblock
from nrplanner.advisor import goals as advisor_goals
from nrplanner.advisor import types

#: A name Qt would render: a tag, and an image it would fetch from another
#: host. The same intruder `test_game_text_is_never_markup` uses.
HOSTILE_NAME = "<b>Gladius</b><img src='\\\\host\\share\\x.png'>"

#: The words of the workings, which no drawn text may contain (AK-144).
THE_WORDS_OF_THE_WORKINGS = ("field", "pool", "handle", "beam", "scorer",
                             "source", "snapshot", "slot_index",
                             "not_counted", "contribution")


# --- the answers the cases draw --------------------------------------------

def a_line(text: str, *, slot: int = 0, curse: bool = False,
           silence: str = types.CARRIES_A_FIGURE) -> types.ReasonLine:
    return types.ReasonLine(slot_index=slot, text=text, is_curse=curse,
                            silence=silence)


def a_group(*lines: types.ReasonLine, slot: int = 0,
            relic: str = "The Will of the Balancers",
            total: int = 3, with_a_figure: int = 2,
            count_line: str = "2 of its 3 effects moved a number in this "
                              "build.") -> types.SlotReasons:
    return types.SlotReasons(slot_index=slot, relic_name=relic,
                             effects_total=total,
                             effects_with_a_figure=with_a_figure,
                             count_line=count_line, lines=tuple(lines))


def an_answer(*groups: types.SlotReasons, goal_id: str = "max_damage",
              goal_label: str = "Maximise damage",
              **fields) -> types.AdvisorResult:
    """One result carrying these groups, filled in as a real one would be."""
    choices = tuple(types.SlotChoice(slot_index=group.slot_index,
                                     handle=700 + group.slot_index,
                                     relic_id=1, name=group.relic_name)
                    for group in groups)
    suggestion = types.Suggestion(
        choices=choices,
        score=types.GoalScore(value=1.0, display="1", unit=""),
        reasons=tuple(groups))
    return types.AdvisorResult(goal_id=goal_id, goal_label=goal_label,
                               suggestions=(suggestion,), **fields)


#: One group carrying one of everything the display has to tell apart.
def a_mixed_group(slot: int = 0) -> types.SlotReasons:
    return a_group(
        a_line("Improved Melee Attack Power: Physical Attack +12.0%",
               slot=slot),
        a_line("[Duchess] Improved Sleep Resistance: works only for Duchess, "
               "and you are Wylder.", slot=slot,
               silence=types.SILENT_ANOTHER_NIGHTFARER),
        a_line("Roar Reduces Damage Taken: only applies under a condition, "
               "so no number here.", slot=slot,
               silence=types.SILENT_UNDER_A_CONDITION),
        a_line("Ultimate Art Charging Impaired: Ultimate Art auto-charge "
               "speed -15.0%, counted against it", slot=slot, curse=True),
        a_line("Taking Damage Causes Madness Buildup: no number here shows "
               "what this costs.", slot=slot, curse=True,
               silence=types.SILENT_NO_NUMBER_HERE),
        slot=slot, total=3, with_a_figure=1,
        count_line="1 of its 3 effects moved a number in this build.")


@pytest.fixture
def block(qapp):
    widget = advisorblock.SuggestionBlock()
    yield widget
    widget.deleteLater()


def a_dialog(qapp, result, **head) -> advisorblock.WhyDialog:
    heading = advisorblock.WhyHeading(
        goal_label=head.get("goal_label", "Maximise damage"),
        nightfarer=head.get("nightfarer", "Wylder"),
        vessel=head.get("vessel", "Wylder's Chalice"),
        deep=head.get("deep", True),
        relics=head.get("relics", 309))
    return advisorblock.WhyDialog(heading, result)


def labels_of(widget) -> list[QLabel]:
    return [child for child in widget.findChildren(QLabel)]


def drawn_text(widget) -> str:
    """Everything the player can read on this widget, markup and all."""
    return "\n".join(label.text() for label in labels_of(widget)
                     if label.isVisibleTo(widget) or not widget.isVisible())


# --- what stands in the block and what does not ----------------------------

def test_the_block_leaves_the_silent_effects_to_the_why_dialog(block):
    """Director's correction 1: a curse is a trap, a silent effect is not.

    The price of a suggestion has to be readable before it is applied; the
    nothing does not, and it is what made the worst measured card 16 lines
    tall.
    """
    group = a_mixed_group()
    block.show_the_suggestion("Maximise damage", group)

    drawn = block.lines.text()
    assert "Improved Melee Attack Power" in drawn
    assert "Ultimate Art Charging Impaired" in drawn
    assert "Taking Damage Causes Madness Buildup" in drawn
    assert "works only for Duchess" not in drawn
    assert "only applies under a condition" not in drawn


def test_every_curse_of_the_copy_stands_in_the_block(block):
    """AK-159, D-2: including the curse to which no figure was written.

    The two curses of `a_mixed_group` are the two halves of it -- one with a
    figure and one without -- and the one without is the half a display that
    drew "the lines that carry a figure, plus the curses among them" would
    lose.
    """
    block.show_the_suggestion("Maximise damage", a_mixed_group())

    drawn = block.lines.text()
    assert drawn.count(advisorblock.CURSE_BULLET) == 2
    assert "Taking Damage Causes Madness Buildup" in drawn


def test_the_count_line_stands_in_the_block(block):
    """AK-158: the denominator is what keeps a silent effect from vanishing.

    It is the whole of what the block says about the three effects it does
    not name.
    """
    block.show_the_suggestion("Maximise damage", a_mixed_group())

    assert block.count_line.text() == (
        "1 of its 3 effects moved a number in this build.")
    assert block.count_line.isVisibleTo(block)


def test_the_block_names_the_goal_and_the_relic(block):
    """§3.2: the block stands for itself once the bar has scrolled away."""
    block.show_the_suggestion("Maximise damage", a_mixed_group())

    assert block.heading.text() == "SUGGESTED — MAXIMISE DAMAGE"
    assert block.relic_name.text() == "The Will of the Balancers"


def test_the_block_carries_no_control(block):
    """The `Use` button of §3.2 is not drawn, not even doing nothing.

    Applying is one thing with one undo model and belongs in one task; a
    button that is on screen and does nothing is worse than no button.
    """
    block.show_the_suggestion("Maximise damage", a_mixed_group())

    assert block.findChildren(QAbstractButton) == []


def test_a_suggestion_already_in_the_slot_is_one_line(block):
    """§3.2: everything falls away but the one line.

    There is nothing to weigh and nothing to change, so the heading, the
    relic name, the count line and the effects all go with it.
    """
    block.show_the_suggestion("Maximise damage", a_mixed_group(),
                              already_equipped=True)

    assert block.already_equipped.isVisibleTo(block)
    assert block.already_equipped.text() == (
        "Already equipped — nothing to change here.")
    for hidden in (block.heading, block.relic_name, block.count_line,
                   block.lines):
        assert not hidden.isVisibleTo(block)


def test_a_block_put_away_shows_nothing(block):
    """An answer that has gone takes its block with it (AK-12)."""
    block.show_the_suggestion("Maximise damage", a_mixed_group())
    block.put_the_suggestion_away()

    assert not block.isVisible()
    assert block.lines.text() == ""
    assert block.lines.toolTip() == ""


def test_the_block_shows_no_summary_sentence(block):
    """AK-133: `Chosen for` does not occur, and no line is shortened."""
    block.show_the_suggestion("Maximise damage", a_mixed_group())

    assert "Chosen for" not in drawn_text(block)
    assert "and 1 more" not in drawn_text(block)


def test_the_legend_is_in_no_block(block):
    """AK-141: the `✦` legend belongs to the dialog, once, and nowhere else."""
    block.show_the_suggestion("Maximise damage", a_mixed_group())

    assert advisorblock.CURSE_LEGEND not in drawn_text(block)


# --- how a line is drawn ---------------------------------------------------

def test_an_effect_of_another_nightfarer_is_drawn_as_the_program_draws_one():
    """Director's correction 2: `NOT WORKING` with a strikethrough, not MUTED.

    It is the commonest silent case there is -- 150 of 426 measured on one
    save -- and the rest of the program already strikes such an effect
    through on the slot card. Two ways of saying one thing is one thing for
    the player to remember.
    """
    from nrplanner.app import BAD, MUTED

    markup = advisorblock.line_markup(
        a_line("X: works only for Duchess, and you are Wylder.",
               silence=types.SILENT_ANOTHER_NIGHTFARER))

    assert "<s>" in markup and "</s>" in markup
    assert BAD in markup
    assert MUTED not in markup


def test_every_other_silent_line_is_muted_and_unmarked():
    """AK-156: no `✦`, no `CURSE`/`BAD`, no `⚠`, no warning colour.

    All four remaining silences at once, because the rule is about the
    silence and not about the sentence.
    """
    from nrplanner.app import BAD, MUTED

    for silence in (types.SILENT_ALREADY_COUNTED,
                    types.SILENT_UNDER_A_CONDITION,
                    types.SILENT_ARMAMENT_BOUND,
                    types.SILENT_NO_NUMBER_HERE,
                    types.SILENT_NOT_IN_THE_DATA):
        markup = advisorblock.line_markup(a_line("X: nothing.",
                                                 silence=silence))
        assert MUTED in markup
        assert BAD not in markup
        assert "✦" not in markup
        assert "⚠" not in markup
        assert "<s>" not in markup


def test_a_curse_keeps_its_mark_whether_or_not_a_figure_covers_it():
    """§3.2: `✦` in `CURSE`, for all three fillings of T-078 §3."""
    from nrplanner.app import CURSE

    for silence in (types.CARRIES_A_FIGURE, types.SILENT_NO_NUMBER_HERE):
        markup = advisorblock.line_markup(
            a_line("A curse: something.", curse=True, silence=silence))
        assert markup.startswith(f"<div style='color:{CURSE}'>✦ ")


# --- the `Why` dialog ------------------------------------------------------

def test_the_dialog_carries_the_lines_the_block_left_out(qapp):
    """The silent effects are not lost, they are one screen further in."""
    dialog = a_dialog(qapp, an_answer(a_mixed_group()))

    drawn = "\n".join(label.text() for _t, _c, label in dialog.groups)
    assert "works only for Duchess" in drawn
    assert "only applies under a condition" in drawn
    dialog.deleteLater()


def test_the_dialog_heads_each_group_with_a_one_based_slot(qapp):
    """AK-135: the slot number is one-based and only in the group heading."""
    dialog = a_dialog(qapp, an_answer(a_mixed_group(slot=0),
                                      a_mixed_group(slot=3)))

    assert [title.text() for title, _c, _l in dialog.groups] == [
        "Slot 1 — The Will of the Balancers",
        "Slot 4 — The Will of the Balancers"]
    for _t, _c, lines in dialog.groups:
        assert "Slot 1" not in lines.text()
    dialog.deleteLater()


def test_the_dialog_names_the_conditional_effects_under_the_groups(qapp):
    """4.9b: the build-wide list, with its heading, one name per line."""
    dialog = a_dialog(qapp, an_answer(a_mixed_group(),
                                      not_counted=("Roar Reduces Damage "
                                                   "Taken", "Poise Up")))

    assert dialog.conditional.isVisibleTo(dialog)
    assert dialog.conditional.text() == (
        "These effects only apply under a condition, so this ranking did "
        "not count them:\nRoar Reduces Damage Taken\nPoise Up")
    dialog.deleteLater()


def test_an_answer_with_nothing_left_out_draws_no_conditional_list(qapp):
    dialog = a_dialog(qapp, an_answer(a_mixed_group()))

    assert not dialog.conditional.isVisibleTo(dialog)
    assert dialog.conditional.text() == ""
    dialog.deleteLater()


def test_the_legend_stands_once_in_the_dialog(qapp):
    """AK-141, with two curse-carrying groups so once is a real claim."""
    dialog = a_dialog(qapp, an_answer(a_mixed_group(slot=0),
                                      a_mixed_group(slot=1)))

    assert dialog.legend.isVisibleTo(dialog)
    assert drawn_text(dialog).count(advisorblock.CURSE_LEGEND) == 1
    dialog.deleteLater()


def test_a_dialog_without_a_curse_carries_no_legend(qapp):
    """A legend for a mark that is not on screen explains nothing."""
    dialog = a_dialog(qapp, an_answer(a_group(
        a_line("Improved Melee Attack Power: Physical Attack +12.0%"))))

    assert not dialog.legend.isVisibleTo(dialog)
    dialog.deleteLater()


def test_the_footer_carries_the_scope_sentences_of_the_direction(qapp):
    """AK-162: the sentences come from `goals.py`, not from a UI constant.

    Both directions are asked, because a constant wired into the dialog would
    show one of them under the other.
    """
    for goal_id in ("max_damage", "min_damage_taken"):
        dialog = a_dialog(qapp, an_answer(a_mixed_group(), goal_id=goal_id))
        footer = dialog.footer.text()
        for sentence in advisor_goals.GOALS[goal_id].scope:
            assert sentence in footer
        dialog.deleteLater()


def test_an_empty_budget_note_draws_nothing_at_all(qapp):
    """AK-170: no heading, no placeholder, no empty bullet, no dash."""
    dialog = a_dialog(qapp, an_answer(a_mixed_group(), goal_id="none",
                                      unknowns=(), weights_note=""))

    assert dialog.footer.text() == ""
    assert not dialog.footer.isVisibleTo(dialog)
    dialog.deleteLater()


def test_a_budget_note_stands_under_the_run_findings(qapp):
    """AK-171: in the dialog, below point 4, and never in the status line."""
    dialog = a_dialog(qapp, an_answer(
        a_mixed_group(), goal_id="none",
        unknowns=("1 of 6 slots is held, so only the other 5 were filled.",),
        weights_note="Both damage types are weighted alike.",
        budget_note="Not every combination was tried.",
        data_note="Ranked on game data version 10350000, read from your "
                  "game files just now."))

    assert dialog.footer.text().splitlines() == [
        "1 of 6 slots is held, so only the other 5 were filled.",
        "Both damage types are weighted alike.",
        "Not every combination was tried.",
        "Ranked on game data version 10350000, read from your game files "
        "just now."]
    dialog.deleteLater()


def test_the_dialog_carries_no_apply(qapp):
    """§3.4: `Close` is the only button. Applying has two places, not three."""
    dialog = a_dialog(qapp, an_answer(a_mixed_group()))

    assert [button.text() for button in
            dialog.findChildren(QAbstractButton)] == ["Close"]
    dialog.deleteLater()


def test_the_dialog_is_modal_and_titled_after_the_goal(qapp):
    dialog = a_dialog(qapp, an_answer(a_mixed_group()))

    assert dialog.isModal()
    assert dialog.windowTitle() == "Why this build — Maximise damage"
    dialog.deleteLater()


# --- the house rules that hold for every element ---------------------------

def test_no_text_element_of_the_advisor_runs_on_autotext(qapp, block):
    """AK-29: every label states its format; the heuristic decides nothing.

    Asked of every label the two widgets own, not of a list of the ones this
    case remembered to name.
    """
    block.show_the_suggestion("Maximise damage", a_mixed_group())
    dialog = a_dialog(qapp, an_answer(a_mixed_group(),
                                      not_counted=("Poise Up",)))

    for widget in (block, dialog):
        for label in labels_of(widget):
            assert label.textFormat() in (Qt.PlainText, Qt.RichText), (
                f"{label.text()!r} decides its own format")
    dialog.deleteLater()


def test_a_hostile_name_is_shown_letter_for_letter(qapp, block):
    """AK-30: in the block, in the dialog and in the tooltip.

    The intruder is injected at the moment of display: nothing here writes to
    the player's installation, and the display is where the decision is made.
    """
    group = a_group(a_line(f"{HOSTILE_NAME}: Physical Attack +12.0%"),
                    relic=HOSTILE_NAME)
    block.show_the_suggestion("Maximise damage", group,
                              curse_tooltip=f"This relic's curses:\n  • "
                                            f"{HOSTILE_NAME}")
    dialog = a_dialog(qapp, an_answer(group, not_counted=(HOSTILE_NAME,)))

    assert "<b>Gladius</b>" not in block.lines.text()
    assert "&lt;b&gt;Gladius&lt;/b&gt;" in block.lines.text()
    assert "<img" not in block.lines.text()
    assert "<b>Gladius</b>" not in block.lines.toolTip()
    assert "&lt;b&gt;Gladius&lt;/b&gt;" in block.lines.toolTip()
    # The relic name and the conditional list draw no markup of their own, so
    # the format is the whole of the answer for them: Qt shows the string.
    assert block.relic_name.textFormat() == Qt.PlainText
    assert block.relic_name.text() == HOSTILE_NAME
    for _t, _c, lines in dialog.groups:
        assert "<b>Gladius</b>" not in lines.text()
    assert dialog.conditional.textFormat() == Qt.PlainText
    dialog.deleteLater()


def test_a_tooltip_is_declared_rich_text_so_the_escaping_shows_as_written():
    """The tooltip has no text format in Qt, so it says what it is.

    Escaping alone would leave Qt reading the value as plain text and show
    the player `&lt;b&gt;`; that is not the name letter for letter either.
    """
    tip = advisorblock.as_a_tooltip("This relic's curses:\n  • <b>x</b>")

    assert tip.startswith("<html>") and tip.endswith("</html>")
    assert "&lt;b&gt;x&lt;/b&gt;" in tip
    assert "<br>" in tip
    assert advisorblock.as_a_tooltip("") == ""


def test_no_drawn_text_uses_the_words_of_the_workings(qapp, block):
    """AK-144: the player is shown the build, never the machinery."""
    block.show_the_suggestion("Maximise damage", a_mixed_group())
    dialog = a_dialog(qapp, an_answer(a_mixed_group(), goal_id="none"))

    seen = (drawn_text(block) + drawn_text(dialog)).lower()
    for word in THE_WORDS_OF_THE_WORKINGS:
        assert word not in seen, f"{word!r} is on screen"
    dialog.deleteLater()


def test_the_display_reads_no_sentence(qapp):
    """AK-147: no line of the answer is split, searched or cut.

    Read off the module rather than argued: the four names that carry lines
    are `reasons`, `curses`, `curses_without_a_figure` and
    `effects_without_a_figure`, and the display reaches a line through the
    group it arrived in.
    """
    import inspect

    text = inspect.getsource(advisorblock)
    for reading in (".split(", ".startswith(", ".find(", ".index(", "re."):
        assert f"line.text{reading}" not in text
        assert f"line{reading}" not in text


# --- the way an answer reaches the cards -----------------------------------

def test_a_line_reaches_the_card_its_slot_names(planner):
    """The routing addresses a slot by index, never by the name on it.

    Both groups carry the same relic name on purpose: QA-180 is open, and a
    display that matched a group to a card by what the relic is called would
    have to pick one of two identical names -- and would keep picking after
    the attribution in `explain.py` is right again.
    """
    cards = planner.active_slots()
    if len(cards) < 2:
        pytest.skip("this vessel has fewer than two slots")
    planner.show_the_suggestion(an_answer(
        a_group(a_line("First: Physical Attack +1", slot=0), slot=0,
                relic="Increased Maximum HP"),
        a_group(a_line("Second: Physical Attack +2", slot=1), slot=1,
                relic="Increased Maximum HP")))

    assert "First: Physical Attack +1" in cards[0].suggestion.lines.text()
    assert "Second: Physical Attack +2" in cards[1].suggestion.lines.text()
    assert "Second" not in cards[0].suggestion.lines.text()


def test_the_bars_answer_reaches_the_cards_without_the_window_asking(planner):
    """The bar says an answer stands; this window draws it (S10b's wiring)."""
    planner.advisor_bar.suggestion_changed.emit(
        an_answer(a_group(a_line("Improved Melee Attack Power: Physical "
                                 "Attack +12.0%", slot=0), slot=0)))

    assert planner.active_slots()[0].suggestion.isVisibleTo(planner)


def test_an_answer_that_has_gone_takes_every_block_with_it(planner):
    """Including the Deep cards, which are not in `active_slots` today.

    A block that outlived its answer names a relic for a slot that may not
    even be in play any more.
    """
    planner.show_the_suggestion(an_answer(
        a_group(a_line("Improved Melee Attack Power: Physical Attack "
                       "+12.0%", slot=0), slot=0)))
    planner.advisor_bar.suggestion_changed.emit(None)

    for card in list(planner.base_slots) + list(planner.deep_slots):
        assert not card.suggestion.isVisible()


def test_an_answer_for_more_slots_than_this_vessel_has_draws_nothing(planner):
    """The answer and the window would be describing different builds."""
    planner.show_the_suggestion(an_answer(
        a_group(a_line("X: Physical Attack +1", slot=99), slot=99)))

    for card in list(planner.base_slots) + list(planner.deep_slots):
        assert not card.suggestion.isVisible()


def test_the_slot_tells_the_suggested_copy_from_the_one_it_holds(qapp):
    """§3.2: identical means the same physical copy, decided on the handle.

    Two copies of one relic are owned with different rolls, so a card that
    compared names would say "already equipped" of a copy the player does not
    have in the slot.
    """
    from nrplanner import inventory
    from nrplanner.app import RelicSlot

    card = RelicSlot(0, False, lambda: None)
    worn = inventory.OwnedItem(relic_id=1, name="The Wylder's Earring",
                               colour=1, effect_ids=[], is_deep=False,
                               handle=700)
    card.relic_box.addItem(worn.name, worn)
    group = a_group(a_line("X: Physical Attack +1"))
    same = types.SlotChoice(slot_index=0, handle=700, relic_id=1,
                            name="The Wylder's Earring")
    other = types.SlotChoice(slot_index=0, handle=701, relic_id=1,
                             name="The Wylder's Earring")

    card.show_the_suggestion("Maximise damage", group, same)
    assert card.suggestion.already_equipped.isVisibleTo(card.suggestion)

    card.show_the_suggestion("Maximise damage", group, other)
    assert not card.suggestion.already_equipped.isVisibleTo(card.suggestion)
    card.deleteLater()


def test_why_opens_on_the_answer_that_is_on_screen(planner, monkeypatch):
    """The dialog is built from the bar's answer and this window's own facts.

    The dialog itself is replaced here: `exec()` on a modal window would sit
    in its own event loop and the case would never come back.
    """
    built = []

    class _Stub:
        def __init__(self, heading, result, parent=None):
            built.append((heading, result))

        def exec(self):
            return 0

    monkeypatch.setattr(advisorblock, "WhyDialog", _Stub)
    answer = an_answer(a_group(a_line("X: Physical Attack +1")))
    planner.advisor_bar._answer = answer
    planner.advisor_bar.why_requested.emit()

    assert len(built) == 1
    heading, seen = built[0]
    assert seen is answer
    assert heading.goal_label == "Maximise damage"
    assert heading.nightfarer == planner.current_hero()["name"]
    assert heading.deep == planner.deep_check.isChecked()


def test_why_with_no_answer_on_screen_opens_nothing(planner, monkeypatch):
    """4.1: nothing is suggested, so there is nothing to explain."""
    def _refuse(*_args, **_kw):
        raise AssertionError("a dialog was opened with no answer behind it")

    monkeypatch.setattr(advisorblock, "WhyDialog", _refuse)
    planner.advisor_bar._answer = None
    planner.advisor_bar.why_requested.emit()
