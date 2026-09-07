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

It reads the player's own save, read-only, and writes nothing.
"""

from __future__ import annotations

import json
import pathlib
import platform
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import os  # noqa: E402

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from nrplanner import app as appmod  # noqa: E402
from nrplanner import model, paths, relicpicker  # noqa: E402

#: A value row long enough to stand for the worst real case: the survival
#: direction's unit is the longest of the two, and four digits is more than
#: any effective-HP difference this dataset can produce.
LONGEST = "+1234.5 effective HP"


def settle(app: QApplication, rounds: int = 3) -> None:
    for _ in range(rounds):
        app.processEvents()


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
    settle(app)
    slot = window.base_slots[0]
    dialog = relicpicker.RelicPicker(slot, window.icons, "", lambda _t: None)
    dialog.show()
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
    window.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
