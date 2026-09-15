"""The vessel list explains what tells one vessel from another (AK-296).

A player chose "Wylder's Chalice" because the name sounded most like a
chalice (QA-173): the list named the vessels and drew their slot chips, and
said nowhere that the slots are the whole difference. `UI_SPEC` 4.4 fixes
four sentences, word for word, on the existing tooltips -- every case here
compares the whole tooltip, not a part of it, so a colour cut back to its
first letter or a line out of order fails as surely as a missing one.
"""

from __future__ import annotations

from PySide6.QtCore import Qt

from nrplanner import app as appmod

WHY = ("Each vessel has its own fixed slots — choose by colour and count, "
       "not by name.")

#: A vessel with both optional lines, and one with neither. Synthetic: every
#: vessel in the dataset carries `deep_slots`, so the "without" case would
#: otherwise go untested.
WITH_BOTH = {"id": 1, "name": "Test Chalice", "slots": [0, 2, 4],
             "deep_slots": [0, 1, 3]}
WITH_NEITHER = {"id": 2, "name": "Test Urn", "slots": [0, 0, 1]}


def test_a_vessel_with_a_white_slot_and_deep_slots_gets_every_line_in_order():
    assert appmod.vessel_tooltip(WITH_BOTH, worn=False) == (
        "Test Chalice\n"
        "Slots: Red, Yellow, White\n"
        "White accepts a relic of any colour.\n"
        "Deep of Night adds: Red, Blue, Green\n"
        + WHY)


def test_a_vessel_with_neither_gets_neither_line_and_nothing_in_their_place():
    assert appmod.vessel_tooltip(WITH_NEITHER, worn=False) == (
        "Test Urn\nSlots: Red, Red, Blue\n" + WHY)


def test_the_equipped_mark_is_the_last_line_after_the_fixed_sentence():
    assert appmod.vessel_tooltip(WITH_NEITHER, worn=True).endswith(
        WHY + "\nEquipped in game")


def test_the_list_carries_the_tooltips_whatever_the_deep_switch_says(
        shared_planner):
    """Both separators and every selectable row, with the switch on and off.

    Read off the real list rather than the function, so the wiring in
    `reload_chalices` is under test too: the Deep of Night line must not
    follow the switch, and the caption rows -- which had no tooltip at all --
    must name who can equip what is under them.
    """
    window = shared_planner
    hero = window.current_hero()["name"]
    tips = {}
    for deep_on in (True, False):
        window.deep_check.setChecked(deep_on)
        window.reload_chalices()
        rows = [window.chalice_list.item(i)
                for i in range(window.chalice_list.count())]
        captions = [r for r in rows if r.flags() == Qt.NoItemFlags]
        vessels = [r for r in rows if r.flags() != Qt.NoItemFlags]
        assert [c.toolTip() for c in captions] == [
            f"Only {hero} can equip these.",
            "Any Nightfarer can equip these; each keeps its own arrangement."]
        for row in vessels:
            vessel = row.data(Qt.UserRole)
            assert row.toolTip().startswith(f"{vessel['name']}\nSlots: ")
            assert WHY in row.toolTip()
            assert "Deep of Night adds: " in row.toolTip()
        tips[deep_on] = [r.toolTip() for r in vessels]
    assert tips[True] == tips[False]
