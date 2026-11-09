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
        "sp_id": 7032202, "sp_category": None,
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


def test_evidence_names_the_triggered_row_that_decides():
    effect = {"id": 1, "stacks": True, "exclusivity": -1,
              "modifiers": {"cycleOccurrenceSpEffectId": 2},
              "triggered": [{"sp_id": 2, "sp_category": 20,
                             "modifiers": {"changeHpPoint": -4}}]}
    assert "two copies give the buff once" in stacking.evidence(effect)


def test_aura_number_is_reached_through_the_bullet_that_lays_it():
    values = {
        7050000: {"behaviorId": 990500000},
        7050001: {"changeHpPoint": -4, "effectEndurance": 1.0},
    }
    found = extract.triggered_rows(
        [7050000], values, {}, set(), BASELINE,
        applied_by=lambda behavior: [7050001] if behavior == 990500000 else [])
    assert [row["sp_id"] for row in found] == [7050001]


def test_effect_that_also_fires_behaviours_outside_its_block_is_not_summed_up():
    """`Items confer effect to all nearby allies`: the row inside the block is
    one item's share, so it does not stand for the effect."""
    values = {
        7050100: {"stateInfo": 2013},
        7050101: {"changeHpPoint": -30,
                  "invocationConditionsStateChange1": 2013},
        708504: {"behaviorId": 760000350,
                 "invocationConditionsStateChange1": 2013},
    }
    assert _rows([7050100], values, gated_on={2013: [708504, 7050101]}) == []


def test_concealment_is_named_and_a_pulse_of_it_is_not():
    values = {
        7260702: {"cycleOccurrenceSpEffectId": 7260703,
                  "replaceSpEffectId": 7260704},
        7260703: {"stateInfo": 600, "effectEndurance": 5.0},
        7260704: {"stateInfo": 600, "effectEndurance": 0.1},
    }
    assert _rows([7260702], values) == [{
        "sp_id": 7260703, "sp_category": None,
        "modifiers": {"stateInfo": 600, "effectEndurance": 5.0}}]
    effect = {"id": 1, "modifiers": {"cycleOccurrenceSpEffectId": 7260703},
              "triggered": _rows([7260702], values)}
    assert effecttext.describe(effect) == "when triggered: concealed for 5 s"


def test_own_hit_and_its_buildup_are_worded_in_the_games_damage_names():
    effect = {"id": 1, "modifiers": {"cycleOccurrenceSpEffectId": 2},
              "proc_damage": {"Thunder": 60}, "proc_inflicts": {"Frost": 9}}
    assert effecttext.describe(effect) == (
        "its own hit: Lightning 60 attack value, "
        "its own hit builds up Frost 9")


class _Row:
    def __init__(self, row_id, hp, holy):
        self.id = row_id
        self.values = {"hp": hp, "darkDamageCutRate": holy,
                       "fireDamageCutRate": 1.0, "resist_poison": 252}


def test_form_that_takes_damage_differently_is_listed_and_a_twin_is_not():
    from nrdata import bossdata
    rows = [_Row(75802000, 2880, 1.2), _Row(75802010, 2880, 1.2),
            _Row(75800000, 1408, 1.35)]
    main = bossdata._profile(rows)
    forms = bossdata._other_forms(rows, main)
    assert [(form["npc_row"], form["hp"]) for form in forms] == [
        (75800000, 1408)]


def test_row_outside_the_stacking_category_makes_the_effect_one_copy():
    own = {"id": 1, "stacks": True, "exclusivity": -1, "one_instance": True,
           "modifiers": {"physicsAttackRate": 1.1}}
    assert stacking.repetition(own) == stacking.ONE_COPY
    assert stacking.classify(own) == "One copy only (multiplies)"

    fired = {"id": 2, "stacks": True, "exclusivity": -1,
             "modifiers": {"cycleOccurrenceSpEffectId": 3},
             "triggered": [{"sp_id": 3, "sp_category": 20,
                            "modifiers": {"physicsAttackRate": 1.15}}]}
    assert stacking.repetition(fired) == stacking.ONE_COPY
    assert "7" not in stacking.evidence(fired) and "3" in stacking.evidence(fired)

    stacking_row = {**fired, "triggered": [{
        "sp_id": 3, "sp_category": 10, "modifiers": {"changeHpPoint": -20}}]}
    assert stacking.repetition(stacking_row) == stacking.STACKS


def test_second_relic_of_a_one_instance_effect_counts_once(game_data):
    """`Rune discount for shop purchases` on two relics is 10, not 20: its
    row 7230000 is category 0, which the game holds once."""
    from nrplanner import model
    effect = game_data["effects"]["7230000"]
    assert effect.get("one_instance") is True
    hero = game_data["heroes"][0]
    once = model.compute(hero, 15, [effect], game_data["curves"])
    twice = model.compute(hero, 15, [effect, effect], game_data["curves"])
    assert twice.other == once.other and once.other
    assert any("keeps one instance" in w.text for w in twice.warnings)


def test_two_copies_of_a_category_ten_effect_still_both_count(game_data):
    from nrplanner import model
    effect = game_data["effects"]["7001400"]      # Physical Attack Up
    assert "one_instance" not in effect
    hero = game_data["heroes"][0]
    once = model.compute(hero, 15, [effect], game_data["curves"])
    twice = model.compute(hero, 15, [effect, effect], game_data["curves"])
    assert twice.rates["physicsAttackRate"] > once.rates["physicsAttackRate"]
