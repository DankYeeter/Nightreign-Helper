"""`effects[].triggered` (EXTRACT_VERSION 23): the numbers on the rows an
effect only switches on, and the fences that keep another effect's number out.
"""

from nrdata import extract
from nrplanner import effecttext, stacking

BASELINE = {"physicsAttackRate": 1.0, "changeHpPoint": 0,
            "slashDamageCutRate": 1.0}


def _rows(sp_ids, values_of, gated_on=None, owned=()):
    return extract.triggered_rows(sp_ids, values_of, gated_on or {},
                                  set(owned), BASELINE)


def test_number_two_hand_offs_on_is_found_with_its_duration():
    values = {
        7032200: {"cycleOccurrenceSpEffectId": 7032201},
        7032201: {"replaceSpEffectId": 7032202},
        7032202: {"physicsAttackRate": 1.15, "effectEndurance": 10.0},
    }
    assert _rows([7032200], values) == [{
        "sp_id": 7032202,
        "modifiers": {"physicsAttackRate": 1.15, "effectEndurance": 10.0}}]


def test_row_waiting_on_the_state_the_effect_sets_is_found():
    values = {
        8620100: {"stateInfo": 2284},
        8620102: {"slashDamageCutRate": 0.79,
                  "invocationConditionsStateChange1": 2284},
    }
    found = _rows([8620100], values, gated_on={2284: [8620102]})
    assert [row["sp_id"] for row in found] == [8620102]


def test_engine_row_outside_the_effects_own_block_is_not_claimed():
    values = {
        6820000: {"cycleOccurrenceSpEffectId": 505},
        505: {"changeHpPoint": 10},
    }
    assert _rows([6820000], values) == []


def test_row_another_effect_owns_is_not_entered():
    values = {
        8800200: {"replaceSpEffectId": 8800250},
        8800250: {"physicsAttackRate": 1.3},
    }
    assert _rows([8800200], values, owned=[8800250]) == []


def test_ailment_row_is_left_to_inflicts():
    values = {
        6820000: {"cycleOccurrenceSpEffectId": 6820002},
        6820002: {"changeHpPoint": 10, "poizonAttackPower": 52},
    }
    assert _rows([6820000], values) == []


def test_the_effects_own_row_is_never_its_own_trigger():
    values = {7000000: {"physicsAttackRate": 1.2,
                        "replaceSpEffectId": 7000000}}
    assert _rows([7000000], values) == []


def test_description_names_the_number_as_triggered_and_timed():
    effect = {"id": 1, "modifiers": {"cycleOccurrenceSpEffectId": 2},
              "triggered": [{"sp_id": 2, "modifiers": {
                  **{f: 1.15 for f in effecttext.ATTACK_RATES},
                  "effectEndurance": 10.0}}]}
    assert effecttext.describe(effect) == (
        "when triggered: All damage +15% for 10 s")


def test_pulse_carries_no_duration_and_stamina_reads_as_a_gain():
    effect = {"id": 1, "modifiers": {"atkOccurrenceSpEffectId": 2},
              "triggered": [{"sp_id": 2, "modifiers": {
                  "changeStaminaPoint": -2, "effectEndurance": 0.3}}]}
    assert effecttext.describe(effect) == "when triggered: Stamina +2"


def test_fp_rate_is_not_read_as_a_multiplier():
    text = effecttext.describe({"id": 1, "modifiers": {"changeMpRate": -13.0}})
    assert text.startswith("FP recovery rate 13") and "%" not in text


def test_evidence_says_what_the_files_leave_open():
    effect = {"id": 1, "stacks": True, "exclusivity": -1,
              "modifiers": {"cycleOccurrenceSpEffectId": 2},
              "triggered": [{"sp_id": 2, "modifiers": {"changeHpPoint": -4}}]}
    assert "do not say whether a second copy adds" in stacking.evidence(effect)
