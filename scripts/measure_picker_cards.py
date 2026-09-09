"""What the advisor's value block costs the relic picker, in pixels.

The recipe behind the figures in the T-093 report (L-001), so that they can be
repeated rather than believed:

    .venv\\Scripts\\python.exe scripts\\measure_picker_cards.py

Three questions, and they are the two acceptance criteria plus the reason for
the second one:

* **AK-41** -- is a card the same height before the figures arrive and after?
  Measured on the card's own `sizeHint`, once with the block carrying `…` and
  once with the longest text a direction can put there, so the answer is about
  this program's fonts and not about a happy short number.
* **AK-51** -- at the size the dialog opens itself at, does the card area need
  a horizontal scrollbar, and how many **whole** rows of cards can be seen?
* What the widest value row actually asks for, against the room a card has:
  a figure wider than the card is a clipped number, which is the failure the
  block would fail by.

**Every figure carries the environment it was taken in** (L-009): platform,
Qt platform plugin, style, UI scale, and whether the pixels are logical or
physical. Offscreen these are logical pixels on a desktop Qt reports as
800 x 800, which is *narrower* than the picker opens -- so the row count is
read off the viewport the dialog asks for, not off what a screen would grant.

**The grid is empty until the answer arrives** (AK-211 to AK-219, T-130).
Since the picker track was wired to the window's `AdvisorController` the
pool is worked out in a real `QThread` and delivered by a Qt signal, not
computed in the call that opens the dialog -- so a fixed number of
`processEvents()` rounds no longer guarantees the cards exist by the time
this script reads them; it only happened to, here, because loading the
snapshot and building the whole window took long enough to mask the race. A
smaller vessel, a warmer disk cache or a faster machine reads the empty grid
AK-212 draws instead. This script waits for `dialog.waiting` to turn false --
the same property the test suite polls -- before it measures anything.

**The save itself is read the same way, and on a thread of its own**
(AD-029 stage B, T-142): the window is complete before `window.owned` is.
This script waits for `window.save_reader.is_reading()` to turn false right
after the window is built, before reading anything that depends on the
player's stock -- the same class of race as the one above, at an earlier
point in the same run.

It reads the player's own save, read-only, and writes nothing.
"""

from __future__ import annotations

import json
import pathlib
import platform
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import os  # noqa: E402

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEventLoop  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from nrplanner import app as appmod  # noqa: E402
from nrplanner import model, paths, relicpicker  # noqa: E402

#: A value row long enough to stand for the worst real case: the survival
#: direction's unit is the longest of the two, and four digits is more than
#: any effective-HP difference this dataset can produce.
LONGEST = "+1234.5 effective HP"

#: How long to let the picker's own answer arrive before giving up. Ten
#: times `run.run`'s worst measured real case (960 ms, `Wylder's Chalice`
#: with Deep of Night, six free slots, S11-C) -- the picker's own pre-sort is
#: one slot of that, so this is a generous margin and not a tuned figure.
ANSWER_TIMEOUT_S = 10.0


def settle(app: QApplication, rounds: int = 3) -> None:
    for _ in range(rounds):
        app.processEvents()


def spin(app: QApplication, still_waiting,
         timeout: float = ANSWER_TIMEOUT_S) -> bool:
    """Turn the main thread's event loop until the picker's answer lands.

    Mirrors `tests/test_advisor_worker.py::spin`: the same idiom the suite
    uses to wait on the real `AdvisorController` thread, so this script
    watches the same thing the window does while a run goes on. Returns
    whether the wait ended because the answer arrived rather than because
    the timeout did.
    """
    deadline = time.monotonic() + timeout
    while still_waiting() and time.monotonic() < deadline:
        app.processEvents(QEventLoop.ProcessEventsFlag.AllEvents, 5)
    return not still_waiting()


def wait_for_the_save(app: QApplication, window,
                      timeout: float = ANSWER_TIMEOUT_S) -> bool:
    """Let the window finish reading its save before anything reads `owned`.

    Since T-142 (AD-029 stage B) the save is read in a background `QThread`
    of its own, separate from the picker's `AdvisorController` thread that
    `spin()` below already waits on. A window is complete before its relics
    are -- this is the wait that `settle()`'s fixed rounds used to cover by
    accident, until this script's own picker track moved to a thread (T-130)
    and made that accident visible.
    """
    return spin(app, lambda: window.save_reader.is_reading(), timeout)


def whole_rows(dialog) -> int:
    """How many complete rows of cards fit the viewport as it stands.

    Per row, because the rows are not the same height: one relic with a long
    name and two curses makes its own row 100 px taller than its neighbour,
    and counting every row by the tallest card anywhere in the grid measures
    a layout that does not exist.
    """
    holder = dialog.scroll.widget()
    cards = holder.findChildren(relicpicker.RelicCard)
    if not cards:
        return 0
    bottoms: dict[int, int] = {}
    for card in cards:
        top = card.mapTo(holder, card.rect().topLeft()).y()
        bottoms[top] = max(bottoms.get(top, 0), top + card.height())
    room = dialog.scroll.viewport().height()
    return sum(1 for bottom in bottoms.values() if bottom <= room)


def main() -> int:
    data = json.loads(paths.snapshot_path().read_text(encoding="utf-8"))
    model.configure(data)
    app = QApplication.instance() or QApplication([])
    appmod.apply_appearance(app)

    window = appmod.Planner(data)
    window.show()
    if not wait_for_the_save(app, window):
        raise SystemExit(
            f"the save was still being read after {ANSWER_TIMEOUT_S:.0f} s; "
            f"nothing to measure")
    settle(app)
    slot = window.base_slots[0]
    dialog = relicpicker.RelicPicker(slot, window.icons, "", lambda _t: None)
    dialog.show()
    if not spin(app, lambda: dialog.waiting):
        raise SystemExit(
            f"the picker's answer for {slot.slot_name()} did not arrive "
            f"within {ANSWER_TIMEOUT_S:.0f} s; nothing to measure")
    settle(app)

    holder = dialog.scroll.widget()
    cards = holder.findChildren(relicpicker.RelicCard)
    print(f"platform {platform.platform()}, Qt plugin "
          f"{app.platformName()}, style {app.style().objectName()}, "
          f"logical px")
    print(f"{len(cards)} relic cards, dialog {dialog.width()} x "
          f"{dialog.height()}, viewport {dialog.scroll.viewport().width()} x "
          f"{dialog.scroll.viewport().height()}, grid asks "
          f"{holder.sizeHint().width()}")
    print(f"horizontal scrollbar: "
          f"{dialog.scroll.horizontalScrollBar().isVisible()}")
    print(f"whole card rows visible: {whole_rows(dialog)}")
    holder = dialog.scroll.widget()
    all_cards = ([holder.findChild(relicpicker.CustomRelicCard)]
                 + holder.findChildren(relicpicker.RelicCard))
    wanted = dialog.wanted_height([c for c in all_cards if c is not None])
    room = app.primaryScreen().availableGeometry().height()
    print(f"AK-51 asks for {wanted} px; this desktop offers {room}")
    dialog.resize(dialog.width(), wanted)
    settle(app)
    print(f"at {wanted} px: viewport {dialog.scroll.viewport().height()}, "
          f"whole card rows {whole_rows(dialog)}")

    if cards:
        card = cards[0]
        print(f"card {card.width()} x {card.height()}, "
              f"minimum width {card.minimumSizeHint().width()}")

    # The AK-41 measurement: one card, built as the picker builds it, asked
    # for its height with `…` and again with the longest text.
    probe = relicpicker.RelicCard(
        cards[0].item, slot.effect_names(cards[0].item), None, False,
        lambda _i: None, captions=[relicpicker.VALUE_CAPTIONS[g]
                                   for g in relicpicker.VALUE_DIRECTIONS])
    probe.setFixedWidth(relicpicker.CARD_WIDTH)
    before = probe.sizeHint().height()
    probe.show_values([LONGEST, LONGEST], relicpicker.chip_text("max_damage"))
    after = probe.sizeHint().height()
    print(f"card height with '…' {before}, with '{LONGEST}' {after}, "
          f"difference {after - before}")

    without = relicpicker.RelicCard(
        cards[0].item, slot.effect_names(cards[0].item), None, False,
        lambda _i: None)
    print(f"card height with no value block "
          f"{without.sizeHint().height()}, minimum width "
          f"{without.minimumSizeHint().width()}")

    block = probe.block
    print(f"value block asks {block.sizeHint().width()} x "
          f"{block.sizeHint().height()}, minimum width "
          f"{block.minimumSizeHint().width()}, card body has "
          f"{relicpicker.CARD_WIDTH - 16}")

    dialog.close()
    second_sample(app, window)
    window.close()
    return 0


def second_sample(app: QApplication, window) -> None:
    """The same reading on both slot kinds and two Nightfarers.

    The fillings and the candidate sets are strongly hero-dependent, so one
    slot of one Nightfarer is not a sample. Deep of Night is switched on so
    that a Deep slot exists to open at all.
    """
    print("")
    print("-- second sample: both slot kinds, two Nightfarers --")
    window.deep_check.setChecked(True)
    settle(app)
    for index in range(2):
        window.select_hero(index)
        settle(app)
        hero = window.current_hero()["name"]
        slots = window.active_slots()
        kinds = [next((s for s in slots if not s.deep), None),
                 next((s for s in slots if s.deep), None)]
        for slot in kinds:
            if slot is None:
                print(f"  {hero}: no slot of this kind on this vessel")
                continue
            picker = relicpicker.RelicPicker(slot, window.icons, "",
                                             lambda _t: None)
            picker.show()
            if not spin(app, lambda: picker.waiting):
                print(f"  {hero} {slot.slot_name()}: no answer within "
                      f"{ANSWER_TIMEOUT_S:.0f} s, skipped")
                picker.close()
                picker.deleteLater()
                settle(app)
                continue
            settle(app)
            cards = picker.scroll.widget().findChildren(relicpicker.RelicCard)
            shown = [label.text() for card in cards[:3]
                     for label in card.block.values]
            marked = sum(1 for card in cards if card.chip.text())
            pool = None if picker.ranking is None else picker.ranking.pool
            print(f"  {hero} {slot.slot_name()}: {len(cards)} cards, "
                  f"{0 if pool is None else len(pool.candidates)} candidates, "
                  f"{marked} marked best, top rows {shown}")
            print(f"      headline {picker.headline.text()!r}")
            print(f"      line 3b  {picker.findings.text()[:110]!r}")
            picker.close()
            picker.deleteLater()
            settle(app)


if __name__ == "__main__":
    sys.exit(main())
