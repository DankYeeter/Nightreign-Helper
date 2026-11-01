"""Reading the save and showing it on the slot cards: the edges T-334 closed.

One case per finding, each one failing on the code before its fix.
"""

from __future__ import annotations

import pathlib
from types import SimpleNamespace

from nrdata import savefile
from nrplanner import datasource, gamepath, inventory, model

HOSTILE_NAME = "<b>Gladius</b>"


# --------------------------------------------------------------------------
# QA-010: a save the game is still writing is given time to settle


class AlwaysMoving:
    """A file whose size changes at every look, as during a game's write."""

    def __init__(self):
        self.looks = 0

    def stat(self):
        self.looks += 1
        return SimpleNamespace(st_size=self.looks, st_mtime_ns=self.looks)

    def read_bytes(self):
        return b"save"


def test_an_unsettled_read_waits_between_its_tries(monkeypatch):
    pauses = []
    monkeypatch.setattr(inventory.time, "sleep", pauses.append)

    assert inventory._read_settled(AlwaysMoving(), attempts=3) == b"save"

    assert pauses == [inventory.SETTLE_PAUSE_SECONDS] * 2


# --------------------------------------------------------------------------
# QA-027: a stored build naming a relic no longer held says so


def test_a_build_naming_a_relic_no_longer_held_counts_it_missing():
    held_handle, gone_handle = 7, 99
    found = inventory.SaveScan(
        source="slot", folder="", source_bytes=None,
        owned=[savefile.OwnedRelic(relic_id=1, effect_ids=[], offset=100,
                                   curse_ids=[])],
        handle_of={100: held_handle},
        loadouts=[savefile.Loadout(
            vessel_id=1000, handles=[held_handle, gone_handle, 0, 0, 0, 0],
            hero_id=1, selected=True, offset=0)])

    inv = inventory.build(
        {"relics": [{"id": 1, "name": "Held relic", "colour": 0}]}, found)

    assert inv.loadouts[0].missing == 1


# --------------------------------------------------------------------------
# QA-012: a gated resistance counts only once its condition is declared


def test_a_gated_resistance_counts_only_when_declared(game_data):
    hero = game_data["heroes"][0]
    plain = next(
        eff for eff in game_data["effects"].values()
        if eff["modifiers"].get("changePoisonResistPoint")
        and not model.is_conditional(eff))
    gated = {**plain, "modifiers": {**plain["modifiers"],
                                    "enemyStateInfoTrigger": 1}}
    curves = game_data.get("curves", {})

    silent = model.compute(hero, 1, [gated], curves)
    declared = model.compute(hero, 1, [gated], curves,
                             declared={gated["id"]: 1})

    assert "Poison" not in silent.resistances
    assert "Poison" in declared.resistances


# --------------------------------------------------------------------------
# QA-171: a snapshot nobody could check against the game is marked


def test_a_failed_check_marks_the_snapshot(monkeypatch):
    def broken(_snapshot):
        raise OSError("the game folder went away")

    monkeypatch.setattr(datasource, "_snapshot", lambda: {"meta": {}})
    monkeypatch.setattr(datasource, "_regulation_matches", broken)

    assert datasource._load_data()["meta"]["stale_check_failed"] is True


def test_an_outdated_snapshot_without_a_game_is_marked(monkeypatch):
    monkeypatch.setattr(datasource, "_snapshot", lambda: {"meta": {}})
    monkeypatch.setattr(datasource, "_regulation_matches", lambda _s: False)
    monkeypatch.setattr(gamepath, "resolve_game", lambda: None)

    assert datasource._load_data()["meta"]["stale_check_failed"] is True


def test_a_snapshot_with_no_game_to_check_against_is_marked(monkeypatch):
    """QA-171's first path: the game folder is gone, the snapshot stands."""
    from nrdata import extract

    snapshot = {"meta": {"extract_version": extract.EXTRACT_VERSION,
                         "regulation_sha256": "recorded"}}
    monkeypatch.setattr(datasource, "_snapshot", lambda: snapshot)
    monkeypatch.setattr(gamepath, "resolve_game", lambda: None)

    assert datasource._load_data()["meta"]["stale_check_failed"] is True


def test_the_title_says_the_figures_were_not_checked(game_data, qapp):
    """QA-171 at the window: the day the data was read, in the title (AK-119)."""
    from nrplanner import app as appmod, firstrun
    from tests import conftest

    unconfirmed = dict(game_data,
                       meta=dict(game_data["meta"], stale_check_failed=True))
    window = conftest.wait_for_the_save(appmod.Planner(unconfirmed))
    try:
        title = window.windowTitle()
        assert "not checked against your installed game" in title, title
        assert firstrun.the_day_the_data_was_read() in title, title
    finally:
        window.close()
        window.deleteLater()


# --------------------------------------------------------------------------
# QA-223: no text promises the drive search that was removed in bd6bd90


def test_the_no_game_message_promises_no_drive_search(monkeypatch):
    monkeypatch.setattr(gamepath, "resolve_game", lambda: None)

    assert "drives" not in datasource._no_data_message()


def test_the_setup_check_promises_no_drive_search():
    script = pathlib.Path(__file__).parent.parent / "scripts" / "setup_check.py"

    assert "drives" not in script.read_text(encoding="utf-8")


# --------------------------------------------------------------------------
# QA-193 and SEC-021: the slot card


def a_card(qapp):
    from nrplanner.relicslots import RelicSlot

    return RelicSlot(0, False, lambda: None)


def test_a_stock_too_dense_to_be_a_save_empties_the_slot_with_the_reason(
        qapp):
    relics = [inventory.OwnedItem(relic_id=n, name=f"Relic {n}", colour=0,
                                  effect_ids=[], is_deep=False, handle=n)
              for n in (1, 2)]
    dense = inventory.Inventory(source="slot", source_bytes=1, relics=relics)
    card = a_card(qapp)

    card.set_colour(0, [], dense)

    assert card.current_relic() is None
    assert "denser than one per" in card.rolled_label.text()
    card.deleteLater()


def test_game_text_on_the_slot_card_is_shown_not_rendered(qapp):
    card = a_card(qapp)
    card.hero_name = "Wylder"
    card.effect_by_id = {
        1: {"id": 1, "name": HOSTILE_NAME, "stacks": True},
        2: {"id": 2, "name": f"[{HOSTILE_NAME}] skill", "stacks": True},
        3: {"id": 3, "name": HOSTILE_NAME, "stacks": True, "is_curse": True,
            "modifiers": {}},
    }
    item = inventory.OwnedItem(relic_id=1, name="Relic", colour=0,
                               effect_ids=[1, 2], is_deep=False, handle=1,
                               curse_ids=[3])
    card.relic_box.addItem(item.name, item)
    card.relic_box.setCurrentIndex(card.relic_box.count() - 1)
    card._sync_mode()

    shown = card.rolled_label.text()
    assert "<b>Gladius" not in shown
    assert shown.count("&lt;b&gt;Gladius&lt;/b&gt;") == 4
    tooltip = card.rolled_label.toolTip()
    assert "<b>Gladius" not in tooltip
    assert "&lt;b&gt;Gladius&lt;/b&gt;" in tooltip
    card.deleteLater()
