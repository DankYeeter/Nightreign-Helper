"""A relic card's chip and value cells, measured with the real font (AK-46,
AK-42, QA-229, QA-230).

Both findings are about text that is wider than the label drawn for it, and
that is a relation between a font and `relicpicker.CARD_WIDTH`. Offscreen the
fallback font runs about twice as wide as Segoe UI (T-084), so a card that
holds every text under Windows cuts every text there -- the reading has to
come from the Windows platform, the way `advisor_row_at_the_window` takes
its own (L-009). A real card in a child process, kept off the screen with
`WA_DontShowOnScreen`; the same figures as on a shown card.

Measured 2026-09-14 (Fusion, Segoe UI 9 pt, device pixel ratio 1.25): before
the fix a favourite card gave its chip 79 px for `BEST FOR SURVIVAL` at 95,
and every card gave the survival cell 93 to 95 px for `+64.2 effective HP`
at 104. After it: 118 px for the chip, 111 px for `+999.9 effective HP`, and
one to eight pixels to spare.

Run as `python -m tests.relic_card_at_the_window`; the parent side is
`measure`.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import types

REPO = pathlib.Path(__file__).resolve().parents[1]

#: The widest chip a direction has (AK-46, AK-262) and the widest figure each
#: direction can put in its cell: three digits of effective HP is the
#: ceiling this dataset reaches for (`measure_picker_cards.LONGEST` probes
#: four for height, not for width), `+100.0 pts` and `+123.4` are wider than
#: any attribute or damage gain a relic yields.
CHIP = "BEST FOR SURVIVAL"
VALUES = ("+123.4", "+999.9 effective HP", "+100.0 pts")


def measure() -> dict:
    """The card's cut texts, out of a child process under Windows."""
    done = subprocess.run(
        [sys.executable, "-m", "tests.relic_card_at_the_window"],
        cwd=REPO, capture_output=True, text=True, check=False,
        env={**os.environ, "QT_QPA_PLATFORM": "windows"})
    assert done.returncode == 0, (
        f"the card could not be measured under the Windows platform:\n"
        f"{done.stderr}")
    return json.loads(done.stdout.splitlines()[-1])


def _cut(label) -> bool:
    return label.fontMetrics().horizontalAdvance(label.text()) > label.width()


def _one_card(favourite: bool, selected: bool) -> dict:
    from PySide6.QtCore import Qt

    from nrplanner import relicpicker
    from tests import rendered

    from nrplanner import effectfilters

    item = types.SimpleNamespace(name="Grand Luminous Scene", has_curse=False)
    card = relicpicker.RelicCard(
        item, [(1, "Vigor +3")], None, selected, lambda _i: None,
        marks=effectfilters.EffectFilters(), favourite=favourite,
        captions=[relicpicker.VALUE_CAPTIONS[goal_id]
                  for goal_id in relicpicker.VALUE_DIRECTIONS])
    card.setAttribute(Qt.WA_DontShowOnScreen)
    card.show()
    card.show_values(list(VALUES), CHIP)
    rendered.settle(20)
    return {
        "chip_width": card.chip.width(),
        "chip_cut": _cut(card.chip),
        "cells_cut": [label.text() for label in card.block.values
                      if _cut(label)],
    }


def main() -> dict:
    from PySide6.QtWidgets import QApplication

    from nrplanner import app as appmod

    app = QApplication([])
    appmod.apply_appearance(app)
    return {
        "platform": app.platformName(),
        "style": app.style().objectName(),
        "plain": _one_card(favourite=False, selected=False),
        "favourite": _one_card(favourite=True, selected=False),
        "favourite_selected": _one_card(favourite=True, selected=True),
    }


if __name__ == "__main__":
    print(json.dumps(main()))
