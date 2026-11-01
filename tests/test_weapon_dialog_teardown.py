"""The armament dialog takes its old effect boxes down at once (QA-305),
and no closed modal dialog stays alive under its parent (QA-308).

Switching from an armament with rollable effects to one without (Unarmed, a
shield, Finger Seal 34750000) and closing the dialog ended the process with an
access violation. The boxes were only scheduled for deletion, so they outlived
the dialog's modal loop and were destroyed afterwards, at the top level. Their
`toggled` slots hold the dialog; with nothing else on the new armament holding
it, destroying the last box released the dialog's Python wrapper, and shiboken
deleted the dialog from inside the destruction of its own child.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog,
                               QMessageBox)

from nrplanner import weaponslots

WITH_EFFECTS = "Academy Glintstone Staff"
WITHOUT_EFFECTS = "Unarmed"


def test_switching_to_an_armament_without_effects_drops_the_boxes_now(
        planner, game_data):
    staff = next(w for w in game_data["weapons"]
                 if w["name"] == WITH_EFFECTS and w.get("effect_pool"))
    dialog = weaponslots.WeaponDialog(planner, game_data,
                                      weaponslots.WeaponSlot(weapon=staff))
    try:
        assert dialog.effects_host.findChildren(QCheckBox), (
            f"{WITH_EFFECTS} shows no effect boxes, so this test proves "
            f"nothing")

        dialog.search.setText(WITHOUT_EFFECTS)

        assert dialog.slot.weapon["name"] == WITHOUT_EFFECTS
        left = dialog.effects_host.findChildren(QCheckBox)
        assert not left, (
            f"{len(left)} boxes of {WITH_EFFECTS} still hang on the dialog, "
            f"waiting for a deferred delete that runs after the modal loop")
    finally:
        dialog.deleteLater()


# --- QA-308: a closed modal dialog is let go ------------------------------

OPENINGS = 3


def _open_armament(planner, game_data):
    staff = next(w for w in game_data["weapons"]
                 if w["name"] == WITH_EFFECTS and w.get("effect_pool"))
    planner.weapon_slots[0] = weaponslots.WeaponSlot(weapon=staff)
    planner._edit_weapon_slot(0)


def _open_why(planner, _game_data):
    from nrplanner.advisor import types
    planner.advisor_bar._answer = types.AdvisorResult(
        goal_id="max_damage", goal_label="Maximise damage")
    planner.open_why()


def _open_effect_filters(planner, _game_data):
    planner.open_effect_filters()


def _open_relic_picker(planner, _game_data):
    planner.base_slots[0]._open_picker()


def _open_restart_question(planner, _game_data):
    planner._choose_scale(0)


@pytest.mark.parametrize("open_it", [_open_armament, _open_why,
                                     _open_effect_filters, _open_relic_picker,
                                     _open_restart_question])
def test_no_closed_dialog_stays_alive(planner, game_data, monkeypatch,
                                      open_it):
    """Every opening built a dialog under the window and none was freed: the
    armament dialog's effect boxes hold it, about 32 MB each (QA-308)."""
    _no_dialog_waits(monkeypatch)
    before = _live_dialogs()
    for _ in range(OPENINGS):
        open_it(planner, game_data)
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)

    left = _live_dialogs() - before
    assert not left, (
        f"{len(left)} dialogs are still alive after {OPENINGS} openings: "
        f"{sorted(type(d).__name__ for d in left)}")


def test_what_the_picker_opens_goes_while_the_picker_stays(
        planner, monkeypatch):
    """The custom relic dialog and the favourite menu are opened from inside
    the relic picker, so each lived as long as the picker did -- one more for
    every time it was opened there (QA-308)."""
    from PySide6.QtCore import QPoint

    from nrplanner import relicpicker

    _no_dialog_waits(monkeypatch)
    monkeypatch.setattr(relicpicker.FavouriteMenu, "exec",
                        lambda self, _position: None)
    slot = planner.base_slots[0]
    picker = relicpicker.RelicPicker(slot, slot.icons, slot.search_text,
                                     slot.on_search_changed)
    try:
        relic = slot.relic_box.itemData(1)
        assert relic is not None and picker._heroes(), (
            "the slot offers no relic or the window no Nightfarer to "
            "favourite for, so the favourite menu is never opened here")
        for _ in range(OPENINGS):
            picker._open_custom()
            picker._open_favourites(relic, QPoint())
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)

        left = (picker.findChildren(relicpicker.CustomRelicDialog)
                + picker.findChildren(relicpicker.FavouriteMenu))
        assert not left, (
            f"{len(left)} of what the picker opened are still alive under it "
            f"after {OPENINGS} openings each: "
            f"{sorted(type(w).__name__ for w in left)}")
    finally:
        picker.deleteLater()


def _no_dialog_waits(monkeypatch) -> None:
    """Every dialog closes the moment it opens; the restart question is
    asked as if a different scale had been chosen, and stores nothing."""
    from nrplanner import uiscale

    monkeypatch.setattr(QDialog, "exec", lambda self: 0)
    monkeypatch.setattr(QMessageBox, "exec", lambda self: 0)
    monkeypatch.setattr(uiscale, "stored", lambda: "a different scale")
    monkeypatch.setattr(uiscale, "set_stored", lambda _value: None)


def _live_dialogs() -> set:
    return {w for w in QApplication.allWidgets() if isinstance(w, QDialog)}
