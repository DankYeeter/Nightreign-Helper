"""The relic picker's query syntax: what counts as an operator, what does not.

T-244 (`docs/berichte/T-244-qa-engineer.md`) found two ways the search
missed a relic the player could see on the card:

* **QA-263** -- a lower-case operator word swallowed itself. Typing an
  effect's own text, `but not for self`, found nothing, because `not`
  parsed as `NOT`. The fix (T-245) makes only the upper-case spelling an
  operator; `not`/`and`/`or` in any other case are searched as text.
* **QA-264** -- a relic's curse never matched, because the haystack was
  built from `effect_ids` alone. `curse_names` gives the picker's search a
  second list to fold in (`relicpicker.py`'s `_candidates`), without
  touching `effect_names`, which still feeds the card's own effect block
  and must not show a curse twice.

These are unit-level guards against synthetic haystacks -- the exact
relic counts T-244 measured (4 rolls, 315 copies, ...) came out of a real
save and are qa-engineer's to reconfirm, not reproducible from here.
"""

from __future__ import annotations

from nrplanner import inventory, relicslots, search

CARD_TEXT = "Raised stamina recovery for nearby allies, but not for self"
HYPHENATED = "Bolsters attack power for a frostbite-afflicted enemy"


def _matches(query: str, haystack: str) -> bool:
    predicate = search.parse(query)
    assert predicate is not None
    return predicate([haystack])


def test_lower_case_operator_words_are_plain_text():
    """QA-263: typing the card's own text must find the card."""
    assert _matches("but not for self", CARD_TEXT)


def test_upper_case_NOT_still_excludes():
    assert _matches("poise NOT curse", "poise")
    assert not _matches("poise NOT poise", "poise")


def test_upper_case_AND_and_OR_still_combine():
    assert _matches("vigor AND attack", "vigor attack")
    assert not _matches("vigor AND attack", "vigor")
    assert _matches("vigor OR mind", "mind")


def test_symbols_are_unaffected_by_case_sensitivity():
    """Director decision (T-245): `&`, `+`, `!`, leading `-` keep working;
    only the alphabetic operator words became case-sensitive."""
    assert _matches("vigor & attack", "vigor attack")
    assert _matches("vigor + attack", "vigor attack")
    assert _matches("poise !curse", "poise")
    assert not _matches("-curse", "curse")


def test_leading_dash_word_stays_NOT_kein_wort_beginnt_so():
    """Director decision: a leading `-` on a token stays NOT, even though
    that swallows a literal search for `-afflicted` (QA-263, accepted --
    quoting is the documented workaround)."""
    assert not _matches("-afflicted", HYPHENATED)


def test_quoted_leading_dash_is_literal():
    assert _matches('"-afflicted"', HYPHENATED)


def test_quoted_phrase_bypasses_operators_regardless_of_case():
    assert _matches('"not curse"', "not curse")


def _slot_with(effects: dict[int, str]) -> relicslots.RelicSlot:
    slot = relicslots.RelicSlot(0, False, lambda: None)
    slot.effect_by_id = {
        eid: {"id": eid, "name": name} for eid, name in effects.items()
    }
    return slot


def test_curse_names_reads_the_curse_ids_not_the_effect_ids():
    slot = _slot_with({1: "Poise", 2: "All Resistances Down"})
    item = inventory.OwnedItem(
        relic_id=1, name="Test Relic", colour=0, effect_ids=[1],
        is_deep=True, handle=1, curse_ids=[2],
    )
    assert slot.effect_names(item) == ["Poise"]
    assert slot.curse_names(item) == ["All Resistances Down"]


def test_curse_only_term_matches_through_the_combined_haystack():
    """QA-264: what `RelicPickerDialog._candidates` now searches."""
    slot = _slot_with({1: "Poise", 2: "All Resistances Down"})
    item = inventory.OwnedItem(
        relic_id=1, name="Test Relic", colour=0, effect_ids=[1],
        is_deep=True, handle=1, curse_ids=[2],
    )
    predicate = search.parse("All Resistances Down")
    haystack = slot.effect_names(item) + slot.curse_names(item)
    assert predicate(haystack)
