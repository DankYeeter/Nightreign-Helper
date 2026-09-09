"""What the suggestion block and the `Why` dialog come out as, once built.

Developer tool for AK-160 and AK-161, which ask two different questions and
have to be answered separately (Director, 06.09.2026):

1. **how many lines a suggestion is**, counted at the widgets that draw it --
   in the block on the card and in the `Why` dialog. The figures in
   `scripts/measure_advisor_language.py` were counted off the shapes before
   there was anything drawing them, and they count two headings per group; a
   block draws **three** (`SUGGESTED — <goal>`, the relic name, the counting
   line);
2. **whether it fits**, at the window width AK-160 names, with the tallest
   card this save can make in every slot.

    .venv\\Scripts\\python.exe scripts\\measure_advisor_block.py

**Measuring environment**, named because a figure without one is not a
measurement (L-009): it is printed at the top of every run -- Qt platform, Qt
style, `QT_SCALE_FACTOR`, the device pixel ratio, and whether the widths are
logical or physical. Widths here are **logical** px, which is what
`UI_SPEC.md` is written in. Run it a second time with `QT_SCALE_FACTOR=1.5`
in the environment for the 150 % half of AK-160: Qt fixes the scale when the
QApplication is made, so one process cannot measure both.

Nothing is written anywhere: the dataset comes from the snapshot, the save is
read in the background the way the window itself reads it (AD-029 stage B,
T-142) and this script waits for `window.save_reader.is_reading()` to turn
false before reading `window.owned`, and there are no screen grabs (NH-002 --
this repository is public).
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from PySide6.QtCore import QEventLoop  # noqa: E402
from PySide6.QtWidgets import QApplication, QScrollArea  # noqa: E402

from nrplanner import advisorblock, model, paths  # noqa: E402
from nrplanner.advisor import goals, run, types  # noqa: E402
from nrplanner.advisor.evaluate import evaluate  # noqa: E402
from nrplanner.advisor import explain  # noqa: E402

#: AK-160's width, in logical px: the window's own starting width.
AK_160_WIDTH = 1320
LEVEL = 15
GOAL = "max_damage"
#: The two Nightfarers the acceptance asks for. Filling (a) hit 150 of 426
#: silent lines on the first and 159 of 434 on the second, so a block that
#: fits on one can still overflow on the other.
NIGHTFARERS = ("Wylder", "Ironeye")


def the_environment(window) -> str:
    ratio = window.devicePixelRatioF()
    return (f"platform {QApplication.platformName()!r}, style "
            f"{QApplication.style().objectName()!r}, QT_SCALE_FACTOR "
            f"{os.environ.get('QT_SCALE_FACTOR', '(unset -- Automatic)')!r}, "
            f"device pixel ratio {ratio}, screen "
            f"{QApplication.primaryScreen().size().width()}x"
            f"{QApplication.primaryScreen().size().height()} logical px")


def settle(passes: int = 12) -> None:
    for _ in range(passes):
        QApplication.instance().processEvents()


#: Ten times `run.run`'s worst measured real case (960 ms), the same margin
#: `measure_picker_cards.py` uses for the advisor's own answer -- generous,
#: not tuned.
SAVE_READ_TIMEOUT_S = 10.0


def wait_for_the_save(window, timeout: float = SAVE_READ_TIMEOUT_S) -> None:
    """Let the window finish reading its save before anything reads `owned`.

    Since T-142 (AD-029 stage B) the save is read in a background `QThread`;
    a window is complete before its relics are. Without this, `window.owned`
    is still `None` when this script gets to it -- not an error, just a wrong
    answer measured with confidence (the failure class T-132 found in
    `measure_picker_cards.py`, before the picker track moved to a thread of
    its own).
    """
    deadline = time.monotonic() + timeout
    app = QApplication.instance()
    while window.save_reader.is_reading():
        app.processEvents(QEventLoop.ProcessEventsFlag.AllEvents, 10)
        if time.monotonic() > deadline:
            raise SystemExit(
                f"the save was still being read after {timeout:.0f} s; "
                f"nothing to measure")
    settle(5)


def the_slot_scroller(window) -> QScrollArea:
    """The middle column's scroll area: the one the relic cards live in."""
    card = window.base_slots[0]
    for scroller in window.findChildren(QScrollArea):
        parent = card.parentWidget()
        while parent is not None:
            if parent is scroller:
                return scroller
            parent = parent.parentWidget()
    raise LookupError("no scroll area holds the relic cards")


def lines_in(label) -> int:
    """How many lines this rich-text label draws, before any wrapping."""
    return label.text().count("<div")


def block_lines(card) -> int:
    """Every line the block on this card draws, its three headings included."""
    block = card.suggestion
    if not block.isVisible():
        return 0
    if block.already_equipped.isVisibleTo(block):
        return 1
    return 3 + lines_in(block.lines)


def dialog_lines(dialog) -> tuple[int, int]:
    """(lines in the whole dialog, tallest single slot group)."""
    total = 1                       # the head
    tallest = 0
    for _title, _count, lines in dialog.groups:
        group = 2 + lines_in(lines)
        tallest = max(tallest, group)
        total += group
    for label in (dialog.conditional, dialog.legend, dialog.footer):
        if label.isVisibleTo(dialog) and label.text():
            total += len(label.text().splitlines())
    return total, tallest


def an_answer(window):
    """The advisor's real answer to what this window is showing right now."""
    from nrplanner.advisorbar import asking_from

    import dataclasses

    asking = asking_from(window, GOAL)
    if asking is None:
        raise SystemExit("no save on this machine, so there is nothing to "
                         "measure")
    # The two fields `AdvisorController.ask` fills in: they are about this
    # asking rather than about what is asked, and `run.run` refuses a request
    # that does not describe the run it is the key of.
    frozen = run.frozen_inventory(asking.inventory, asking.request.problem)
    request = dataclasses.replace(
        asking.request,
        inventory_fingerprint=run.inventory_fingerprint(frozen))
    return run.run(request, frozen, asking.ctx, goals.GOALS)


def the_tallest_group(data: dict, window):
    """The tallest slot group any relic in this save can make, on this hero.

    One relic in one slot against an empty base state, which is how
    `measure_advisor_language.py` finds it too. AK-160 names
    `Deep Grand Tranquil Scene`; this asks the save rather than trusting the
    name, so the figure keeps meaning something on another save.
    """
    from nrplanner.advisorbar import asking_from

    asking = asking_from(window, GOAL)
    goal = goals.GOALS[GOAL]
    tallest = None
    for relic in run.frozen_inventory(asking.inventory,
                                      asking.request.problem).relics:
        problem = types.SlotProblem(
            slots=(types.Slot(index=0, colour=relic.colour,
                              deep=relic.is_deep),))
        copy = types.Candidate(slot_index=0, handle=relic.handle or 0,
                               relic_id=relic.relic_id, name=relic.name,
                               colour=relic.colour, is_deep=relic.is_deep,
                               effect_ids=tuple(relic.effect_ids),
                               curse_ids=tuple(relic.curse_ids))
        base = evaluate(problem, (), asking.ctx)
        built = evaluate(problem, (copy,), asking.ctx)
        group = explain.reasons(problem, (copy,), base, built, asking.ctx,
                                goal)[0]
        if tallest is None or len(group.lines) > len(tallest.lines):
            tallest = group
    return tallest


def repeated_over_every_slot(group, window):
    """That one group in every slot of this vessel, as a whole answer."""
    import dataclasses

    cards = window.active_slots()
    groups = tuple(dataclasses.replace(group, slot_index=index)
                   for index in range(len(cards)))
    choices = tuple(types.SlotChoice(slot_index=one.slot_index, handle=0,
                                     relic_id=0, name=one.relic_name)
                    for one in groups)
    return types.AdvisorResult(
        goal_id=GOAL, goal_label=goals.GOALS[GOAL].label,
        suggestions=(types.Suggestion(
            choices=choices,
            score=types.GoalScore(value=0.0, display="0", unit=""),
            reasons=groups),))


def a_window(data: dict):
    from nrplanner import app as appmod

    window = appmod.Planner(data)
    window.resize(AK_160_WIDTH, 900)
    window.show()
    wait_for_the_save(window)
    return window


def set_up(window, nightfarer: str) -> bool:
    """Put this Nightfarer, a six-slot vessel and Deep of Night on screen."""
    index = next((i for i, hero in enumerate(window.heroes)
                  if hero["name"] == nightfarer), None)
    if index is None:
        return False
    window.select_hero(index)
    window.level_slider.setValue(LEVEL)
    window.deep_check.setChecked(True)
    settle()
    return len(window.active_slots()) == 6


def report(window, nightfarer: str) -> None:
    # The state before anything of the advisor is drawn: a scrollbar that is
    # already there is not this block's doing, and a figure without its
    # before-state says nothing.
    window.show_the_suggestion(None)
    settle()
    empty = the_slot_scroller(window).horizontalScrollBar().maximum()
    answer = an_answer(window)
    window.show_the_suggestion(answer)
    settle()
    cards = window.active_slots()
    per_card = [block_lines(card) for card in cards]
    heading = advisorblock.WhyHeading(
        goal_label=answer.goal_label, nightfarer=nightfarer,
        vessel=str((window.current_vessel() or {}).get("name", "")),
        deep=window.deep_check.isChecked(),
        relics=0 if window.owned is None else window.owned.relic_count)
    dialog = advisorblock.WhyDialog(heading, answer, window)
    whole, tallest_group = dialog_lines(dialog)
    print(f"\n{nightfarer} — {heading.vessel}, Deep of Night on, "
          f"{heading.relics} relics, direction {answer.goal_label!r}")
    print(f"  block, per card:      {per_card}  (tallest "
          f"{max(per_card)}, {sum(per_card)} lines over the six cards)")
    print(f"  Why dialog:           {whole} lines, tallest slot group "
          f"{tallest_group}")
    dialog.deleteLater()

    group = the_tallest_group(window.data, window)
    print(f"  tallest group this save can make: {len(group.lines)} lines on "
          f"{group.relic_name!r}")
    window.show_the_suggestion(repeated_over_every_slot(group, window))
    settle()
    worst = [block_lines(card) for card in cards]
    scroller = the_slot_scroller(window)
    bar = scroller.horizontalScrollBar()
    print(f"  with that group in every slot: {worst} lines per card")
    print(f"  window {window.width()}x{window.height()} logical px, middle "
          f"column {scroller.width()} px, cards {cards[0].width()} px")
    print(f"  horizontal scroll in the middle column: 0..{bar.maximum()} px "
          f"with the blocks, 0..{empty} px with no suggestion drawn")
    for card in cards:
        label = card.suggestion.lines
        if label.width() < label.minimumSizeHint().width():
            print(f"  card {card.index}: the lines label is narrower than it "
                  f"asks for ({label.width()} < "
                  f"{label.minimumSizeHint().width()})")
    window.show_the_suggestion(None)
    settle()


def main() -> int:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    data = json.loads(paths.snapshot_path().read_text(encoding="utf-8"))
    model.configure(data)
    from nrplanner.app import _dark_palette

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(_dark_palette())
    window = a_window(data)
    print(the_environment(window))
    version = (data.get("meta") or {}).get("data_version")
    print(f"data_version {version}, level {LEVEL}, window asked for "
          f"{AK_160_WIDTH} logical px")
    for nightfarer in NIGHTFARERS:
        if not set_up(window, nightfarer):
            print(f"\n{nightfarer}: no six-slot vessel on this save, skipped")
            continue
        report(window, nightfarer)
    window.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
