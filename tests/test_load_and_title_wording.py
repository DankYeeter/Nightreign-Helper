"""The wording of the Deep switch, the load note, the title and the save line
(`UI_SPEC` "Nachtrag T-334k", AK-390 to AK-394).

Every sentence is transcribed out of the spec rather than imported from
`nrplanner.app`: a test that compared the text against the constant behind it
would be green whatever either of them said.
"""

from __future__ import annotations

import dataclasses

import pytest

from nrdata import savefile
from nrplanner import app as appmod
from tests import conftest, rendered
from tests.test_save_read_in_the_background import StatedRead, a_window, close
from tests.test_the_owned_total_has_its_own_line import SOURCE, a_scan_of

SWITCH = "Deep of Night (3 extra slots)"
ONE_LEFT_EMPTY = ("A Deep of Night slot of this build names a relic that is "
                  "already worn in another slot, so it was left empty. Turn "
                  "Deep of Night on to see it.")
SEVERAL_LEFT_EMPTY = ("Deep of Night slots of this build name relics that are "
                      "already worn in other slots, so they were left empty. "
                      "Turn Deep of Night on to see them.")


# -- AK-390: the Deep of Night switch counts slots ---------------------------

@pytest.mark.parametrize("hidden, text, tooltip", [
    (0, SWITCH, ""),
    (1, f"{SWITCH} — 1 left empty", ONE_LEFT_EMPTY),
    (3, f"{SWITCH} — 3 left empty", SEVERAL_LEFT_EMPTY),
])
def test_the_deep_switch_says_how_many_slots_were_left_empty(
        hidden, text, tooltip):
    assert appmod.deep_switch_note(hidden) == (text, tooltip)


def test_the_longest_deep_switch_text_does_not_widen_the_window(planner):
    """AK-390: the addition, at `n = 3`, moves no floor."""
    plain = planner.minimumSizeHint().width()
    planner.deep_check.setText(appmod.deep_switch_note(3)[0])
    assert planner.minimumSizeHint().width() == plain


# -- AK-391/AK-392: one sentence per reason ----------------------------------

def test_a_second_reason_does_not_open_like_the_first():
    """AK-391: `unfit` and `clashed` together -- the second says `other`."""
    assert appmod.placement_reasons(1, 2, 0) == (
        " 1 relic could not be placed: it does not fit the slot the save has "
        "it in. 2 other relics could not be placed: they are already worn in "
        "another slot.")
    assert appmod.placement_reasons(2, 1, 0) == (
        " 2 relics could not be placed: they do not fit the slots the save "
        "has them in. 1 other relic could not be placed: it is already worn "
        "in another slot.")


def test_a_clash_on_its_own_has_no_other():
    assert appmod.placement_reasons(0, 1, 0) == (
        " 1 relic could not be placed: it is already worn in another slot.")


@pytest.mark.parametrize("missing, sentence", [
    (0, ""),
    (1, " 1 relic the save has equipped is no longer in your inventory."),
    (3, " 3 relics the save has equipped are no longer in your inventory."),
])
def test_a_relic_the_inventory_lost_is_said_once(missing, sentence):
    """AK-392, unchanged: one sentence when `missing > 0`, none otherwise."""
    assert appmod.placement_reasons(0, 0, missing) == sentence


# -- AK-393: the title never says `data from ,` ------------------------------

@pytest.mark.parametrize("day, addition", [
    ("3 October 2026",
     "  —  data from 3 October 2026, not checked against your installed game"),
    ("", "  —  data not checked against your installed game"),
])
def test_the_title_addition_with_and_without_a_day(day, addition):
    assert appmod.unchecked_data(day) == addition


def test_an_unchecked_snapshot_with_no_day_says_so_in_the_title(
        game_data, qapp, monkeypatch):
    """AK-393 at the window: `firstrun.the_day_the_data_was_read()` is `""`."""
    from nrplanner import firstrun

    monkeypatch.setattr(firstrun, "the_day_the_data_was_read", lambda: "")
    unconfirmed = dict(game_data,
                       meta=dict(game_data["meta"], stale_check_failed=True))
    window = conftest.wait_for_the_save(appmod.Planner(unconfirmed))
    try:
        assert window.windowTitle().endswith(
            "  —  data not checked against your installed game")
        assert "data from ," not in window.windowTitle()
    finally:
        window.close()
        window.deleteLater()


# -- AK-394: no stored builds could be read ----------------------------------

def test_a_save_without_nightfarer_markers_says_so_without_the_markers(
        game_data, qapp):
    """AK-394, unchanged: the sentence of `NotWhatItClaims`, and no marker
    count -- that one travels as a note, in the traceback only."""
    with pytest.raises(savefile.NotWhatItClaims) as refused:
        savefile.find_loadout_table(bytes(64))
    scan = dataclasses.replace(a_scan_of(game_data, 3),
                               loadout_error=str(refused.value))
    read = StatedRead(scan)
    window = a_window(game_data, read)
    try:
        conftest.wait_for_the_save(window)
        rendered.settle(2)

        assert window.owned_label.text() == (
            f"3 relics in {SOURCE} — no stored builds could be read: this "
            "save keeps them somewhere this program does not look; the game "
            "may have changed how it stores them")
    finally:
        close(window, read)
