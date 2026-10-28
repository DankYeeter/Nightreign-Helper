"""The armament dialog takes its old effect boxes down at once (QA-305).

Switching from an armament with rollable effects to one without (Unarmed, a
shield, Finger Seal 34750000) and closing the dialog ended the process with an
access violation. The boxes were only scheduled for deletion, so they outlived
the dialog's modal loop and were destroyed afterwards, at the top level. Their
`toggled` slots hold the dialog; with nothing else on the new armament holding
it, destroying the last box released the dialog's Python wrapper, and shiboken
deleted the dialog from inside the destruction of its own child.
"""

from __future__ import annotations

from PySide6.QtWidgets import QCheckBox

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
