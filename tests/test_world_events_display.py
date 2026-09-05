"""What a world event card says, read off the card.

**What guarded this tab before this file: nothing.** Two independent searches
of `tests/` on 2026-09-05 -- for `eventstab`/`eventlore` and for
`WorldEventsTab` -- found 0 files. Rewriting the gating sentence to say
`Fires on Day 2 only`, a false statement on all eleven events at once, left
622 of 622 green (QA-137, mutation M5).

Three findings are held here:

* the day sentence stood word for word on all eleven events while the split
  was in the data and being thrown away -- Judgment is 19 of 20 patterns on
  Day 1 (QA-134);
* a one-off payout was printed with a duration: `10,000 runes for 1s`
  (QA-133);
* source names, a param row and this project's own repair history were on
  screen, against the rule at the top of the module they were on (QA-135).

**The counts come out of `world_events.gating`,** never out of the sentence
being checked. A case that read the numbers off the label it is testing would
agree with any label at all.
"""

from __future__ import annotations

import pytest

from nrplanner import eventstab

from tests import tabtext

#: AK-104: derivation and source language that may not appear in any text the
#: tab draws. `Eldenpedia` is matched case-insensitively because the module
#: writes it both ways.
BANNED = ("fextralife", "game8", "eldenpedia", "thefifthmatt",
          "pattern modifier", "the row this project had wrong")

#: AK-102, the scope of the percentage and of the all-Nightlords assurance.
PERCENTAGE_SCOPE = (
    "The percentage is how much of that Nightlord's map pool carries the "
    "event. The pool is drawn with weights, so it is not the chance of "
    "seeing it on a given run.")
NEVER_SCOPE = (
    "Every other Nightlord: never — across every map pattern in the game's "
    "data.")

#: QA-133's three cases, by the text the extractor writes for them. The first
#: two hand over an amount once; the third is a state and keeps its window.
AMOUNT_LINES = ("10,000 runes", "restores 100 stamina")
STATE_LINE = "invulnerable for 5s"


@pytest.fixture(scope="module")
def tab(game_data, qapp):
    widget = eventstab.WorldEventsTab(game_data)
    yield widget
    widget.deleteLater()


def page(tab, row: int) -> str:
    tab.list.setCurrentRow(row)
    return tabtext.everything(tab.detail_area.widget())


def every_page(tab) -> dict[str, str]:
    return {tab.list.item(row).text(): page(tab, row)
            for row in range(tab.list.count())}


def gated_rows(tab) -> list[tuple[int, dict]]:
    """(list row, gating entry) for every event the files gate."""
    out = []
    for row, (kind, entry) in enumerate(tab.rows):
        if kind != "event":
            continue
        gate = tab.gating.get(str(entry["log_id"]))
        if gate:
            out.append((row, gate))
    return out


def test_the_day_sentence_names_this_event_s_own_split(tab):
    """QA-134 and AK-101: one sentence stood on eleven events.

    Every gated event is checked against its own `day1_patterns` and
    `day2_patterns`, and the case insists the sentences are not all the same
    -- which is the state it exists to end, and the state mutation M5 puts
    the tab back into.
    """
    rows = gated_rows(tab)
    assert len(rows) > 1, "fewer than two gated events in this dataset"

    sentences = set()
    for row, gate in rows:
        text = page(tab, row)
        day1, day2 = gate.get("day1_patterns", 0), gate.get("day2_patterns", 0)
        if day1 and day2:
            sentence = (f"Can fire on Day 1 or Day 2 — {day1} of the "
                        f"{day1 + day2} map patterns that carry it are Day 1.")
        else:
            sentence = f"Fires on Day {1 if day1 else 2}."
        assert sentence in text, (
            f"{tab.list.item(row).text()!r}: expected {sentence!r}")
        sentences.add(sentence)

    assert len(sentences) > 1, (
        f"all {len(rows)} gated events carry the same day sentence, so it "
        f"says nothing about any of them: {sentences!r}")


def test_the_percentage_says_what_it_is_a_share_of(tab):
    """AK-102: a bare `18%` beside a Nightlord's name, and an allness claim.

    The pool is drawn with weights, so the share is not the chance of meeting
    the event on a run -- and `Every other Nightlord: never` is worth having
    only with the ground it is asserted over.
    """
    rows = gated_rows(tab)
    for row, _gate in rows:
        text = page(tab, row)
        assert PERCENTAGE_SCOPE in text, tab.list.item(row).text()
        assert NEVER_SCOPE in text, tab.list.item(row).text()
    assert rows


def test_a_duration_stands_only_where_there_is_a_state_to_have_it(tab):
    """QA-133 and AK-103: `10,000 runes for 1s`.

    The three cases are checked by their own text: the two amounts must appear
    without any window at all, and the state must keep its five seconds. A
    duration of 0.0 is not an entry and is never printed as `for 0s`.
    """
    pages = every_page(tab)
    everything = "\n".join(pages.values())

    for line in AMOUNT_LINES:
        assert line in everything, (
            f"{line!r} is not on any card, so this case checked nothing")
        assert f"{line} for " not in everything, (
            f"{line!r} is printed with a duration, and it is an amount "
            f"handed over once")
    assert STATE_LINE in everything, (
        f"{STATE_LINE!r} is not on any card; a state has to keep its window "
        f"or this case only proves durations were dropped everywhere")
    assert "for 0s" not in everything


def test_no_card_says_how_any_of_it_was_derived(tab):
    """QA-135 and AK-104, and the module's own rule about its own text.

    Source names, a param row and this project's own repair history were all
    on screen. What a player can act on stays -- that the sources disagreed,
    and what the game's own outcome line says.
    """
    pages = every_page(tab)
    for name, text in pages.items():
        lowered = text.lower()
        for banned in BANNED:
            assert banned not in lowered, (
                f"{name!r} still says {banned!r} on screen")
    assert any("Sources disagree" in text for text in pages.values()), (
        "no card records a disagreement any more, which is more than AK-104 "
        "asked for and less than a reader needs")


def test_the_rune_claim_carries_the_figures_that_were_loaded_for_it(tab,
                                                                    game_data):
    """AK-104: `rises the more expeditions you have cleared`, unnumbered.

    `world_events.rune_scaling` is read on every start and was thrown away
    every time. It is the only place those multipliers appear, and it appears
    where the claim is.
    """
    scaling = (game_data.get("world_events") or {}).get("rune_scaling") or []
    assert scaling, "this dataset carries no rune scaling text"

    with_runes = [text for text in every_page(tab).values()
                  if "rises the more expeditions you have cleared" in text]
    assert with_runes, "no card shows a creature's rune figure"
    for text in with_runes:
        assert "×1.1" in text, (
            "the multipliers that number the claim are not beside it")
        assert "Param." not in text, (
            "a param name reached the screen with them")


def test_one_creature_is_not_two_unconnected_entries(tab):
    """QA-136 and AK-105: the Scale-Bearing Merchant, described twice.

    The list mixes two orderings -- extracted events by id, community-reported
    phenomena by name -- and this creature falls into both. Whether that is
    one thing or two is a content decision; that a reader can get from one to
    the other is not.
    """
    pages = every_page(tab)
    name = "Scale-Bearing Merchant"
    describing = [title for title, text in pages.items() if name in text]
    assert describing, f"no card mentions the {name!r} at all"
    if len(describing) == 1:
        return    # one thing, one card: nothing to cross-refer to

    titled = [title for title in describing if name in title]
    assert len(titled) == 1, (
        f"{name!r} is a list entry {len(titled)} times over: {titled!r}")
    others = [title for title in describing if title not in titled]
    assert any(other.split("  ·")[0] in pages[titled[0]] for other in others), (
        f"the card headed {titled[0]!r} describes the same creature as "
        f"{others!r} and names none of them, so a reader who lands on one "
        f"never learns the other exists")


def test_the_tab_opens_with_the_question_it_answers(tab):
    """AK-68: this tab already did, and is the pattern the other five took."""
    lines = tabtext.labels(tab)
    assert lines[0] == "WORLD EVENTS"
    assert lines[1].startswith("Events that can interrupt an expedition")
    assert "community-reported" in lines[1], (
        "the sentence naming the blue lines is gone, and the colour carries "
        "a meaning nothing else states")
