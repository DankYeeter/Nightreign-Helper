"""Text out of the game files and out of the file system is shown, not rendered.

SEC-012 and SEC-013 -- the same defect as SEC-004, at the places T-017 did not
reach.

* The Nightlord panel puts the boss's own FMG name and description into two
  QLabels that were left on Qt's AutoText, which decides for itself whether
  what it was handed is markup.
* The stance ranking line names two other bosses and is built into the
  rich-text body by string concatenation, so their names went in as markup.
* The label naming the loaded save offers the save folder as a tooltip, and a
  tooltip detects rich text exactly as a QLabel does. Qt offers no text format
  for tooltips, so the value is escaped instead.

The hostile names below are injected at the moment of display rather than
planted in the game files: nothing here writes to the player's installation,
and the display is where the decision is made.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt

from nrplanner import inventory
from nrplanner.bosstab import BossTab

# A tag Qt would render, and an image it would try to fetch from another host.
HOSTILE_NAME = "<b>Gladius</b><img src='\\\\host\\share\\x.png'>"


@pytest.fixture
def boss_tab(game_data, qapp):
    tab = BossTab(game_data)
    yield tab
    tab.deleteLater()


def test_the_boss_name_is_shown_as_text(boss_tab):
    assert boss_tab.detail_name.textFormat() == Qt.PlainText


def test_the_boss_description_is_shown_as_text(boss_tab):
    assert boss_tab.detail_text.textFormat() == Qt.PlainText


def test_a_boss_named_in_the_stance_ranking_cannot_bring_markup_with_it(
        boss_tab):
    """The ranking names the smallest and largest bar in the field.

    The intruder is given a bar below every real one, so it is guaranteed to
    be the "smallest" the line reports and the assertion cannot pass by the
    name simply not appearing.
    """
    ranked = [boss for boss in boss_tab.bosses
              if (((boss.get("weakness") or {}).get("profile") or {})
                  .get("stance") or {}).get("bar")]
    if len(ranked) < 2:
        pytest.skip("this dataset ranks fewer than two bosses by stance bar")

    intruder = {
        "name": HOSTILE_NAME,
        "weakness": {"profile": {"stance": {"bar": -1.0}}},
    }
    boss_tab.bosses = boss_tab.bosses + [intruder]
    boss_tab.show_detail(ranked[0])

    body = boss_tab.detail_body.text()
    assert "<b>Gladius</b>" not in body
    assert "&lt;b&gt;Gladius&lt;/b&gt;" in body


def test_the_save_folder_is_offered_as_text(planner, monkeypatch):
    """The tooltip shows the folder; it does not fetch anything named in it.

    The player's own save is what is re-read, with only the folder replaced:
    every other field the line is built from stays real, so the test cannot
    pass by the label taking an error path instead.
    """
    if planner.owned is None:
        pytest.skip("this machine has no save to read")
    owned = planner.owned
    owned.folder = HOSTILE_NAME
    monkeypatch.setattr(inventory, "load", lambda _data: owned)
    planner.rescan_save()
    tip = planner.owned_label.toolTip()
    assert "<img" not in tip
    assert "&lt;b&gt;Gladius&lt;/b&gt;" in tip
