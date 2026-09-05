"""What the Nightlord detail panel says about a boss, read off the panel.

**What guarded this tab before this file: one case about markup escaping.** A
search of `tests/` for `bosstab` and for `BossTab` on 2026-09-05 found
`test_game_text_is_never_markup.py` and nothing else; it checks that a name
cannot smuggle a tag in, and reads no figure. Raising the panel's debuff
figures to x9.9 and x0.1 left 622 of 622 green (QA-137, mutation M6).

The panel was the one place in the program that told a player something about
a boss that was not true (QA-129). `Debuff x2.0 damage taken` and `Debuff
x0.8 attack power` were constants in the module, printed against a hand-kept
list of three names:

    Gladius    ladder.down attack 0.815  -- shown, figure disagrees
    Caligo     no down step in the data  -- shown anyway
    Heolstor   no down step in the data  -- shown anyway
    Harmonia   ladder.down attack 0.8    -- not shown
    Straghess  ladder.down attack 0.8    -- not shown

Seven of the ten carry a down step and none of them reached the screen. Every
figure below is compared against `weakness.profile` as the dataset holds it,
never against a constant in `nrplanner.bosstab` -- a case that read its
expectation out of the module it guards would stay green through any edit to
that module, which is the trap that has caught this repository twice.
"""

from __future__ import annotations

import pytest

from nrplanner import bosstab

from tests import tabtext

#: The two figures QA-129 found standing against the wrong bosses. They are
#: gone from the module, and the panel must not put them back under any name.
RETIRED_FIGURES = ("x2.0 damage taken", "x0.8 attack power")

#: AK-91, the three lines that say what each block of figures is measured
#: against and which direction is better.
BLOCK_NOTES = (
    "Bars compare this Nightlord's damage types with each other, not with "
    "another Nightlord. Green marks the type it is weak to.",
    "How much status you have to apply before it lands — lower is easier. "
    "Green marks this Nightlord's easiest statuses.",
    "Bar to break is in the game's own stance points. The refill figure is "
    "the rate the files give; they do not say what it is per, so compare it "
    "between Nightlords rather than reading it as a speed.",
)


@pytest.fixture(scope="module")
def tab(game_data, qapp):
    widget = bosstab.BossTab(game_data, None)
    yield widget
    widget.deleteLater()


def panel(tab, name: str) -> str:
    """The detail panel for one Nightlord, as plain text."""
    boss = next((b for b in tab.bosses if b["name"] == name), None)
    assert boss is not None, f"no Nightlord named {name!r} in this dataset"
    tab.show_detail(boss)
    return tabtext.plain(tab.detail_body.text())


def profile_of(tab, name: str) -> dict:
    boss = next(b for b in tab.bosses if b["name"] == name)
    return ((boss.get("weakness") or {}).get("profile")) or {}


def with_a_down_step(tab) -> list[str]:
    return [boss["name"] for boss in tab.bosses
            if (profile_of(tab, boss["name"]).get("ladder") or {}).get("down")]


def test_every_weakened_step_in_the_data_reaches_the_panel(tab):
    """QA-129: the figures come from `ladder.down`, boss by boss.

    Checked against the dataset for all ten, in both directions -- a boss with
    a step shows its own figures, a boss without one shows no such row. The
    second half is what stops the panel going back to a fixed list of names:
    Caligo and Heolstor have no down step, and both used to carry one.
    """
    carriers = with_a_down_step(tab)
    assert 1 < len(carriers) < len(tab.bosses), (
        f"{len(carriers)} of {len(tab.bosses)} Nightlords carry a weakened "
        f"step, so this case cannot tell the two states apart")

    for boss in tab.bosses:
        name = boss["name"]
        text = panel(tab, name)
        steps = (profile_of(tab, name).get("ladder") or {}).get("down") or []
        if not steps:
            assert "Weakened" not in text, (
                f"{name} has no weakened step in the data and the panel "
                f"shows one")
            continue
        assert "IT IS WEAKENED" in text, (
            f"{name} carries {len(steps)} weakened step(s) and the panel "
            f"shows none")
        for step in steps:
            assert f"x{step['attack']:g} its attack power" in text, (
                f"{name}: the panel does not show the attack figure "
                f"{step['attack']:g} its own data gives. Panel reads: {text}")
            taken = step.get("stance_taken")
            if taken and abs(taken - 1.0) > 1e-6:
                assert f"x{taken:g} the stance damage it takes" in text, name


def test_the_two_typed_in_debuff_figures_are_gone_from_every_panel(tab):
    """QA-129, the other half: no magnitude the files do not carry.

    The sighting itself stays, because somebody watched it happen; what it may
    not do is put a number on it. `Watched in play` has to be the sentence,
    and it has to be in the colour the tab keeps for sightings, so a reader
    can see the difference from the extracted figures above it.
    """
    seen = 0
    for boss in tab.bosses:
        text = panel(tab, boss["name"])
        for figure in RETIRED_FIGURES:
            assert figure not in text, (
                f"{boss['name']}: `{figure}` is back on the panel, and no "
                f"field of this dataset carries it")
        if boss["name"] in bosstab.DEBUFF_ON_BREAK:
            assert bosstab.DEBUFF_ON_BREAK_SIGHTING in text, boss["name"]
            assert bosstab.OBSERVED_COLOUR in tab.detail_body.text(), (
                f"{boss['name']}: the sighting is not in the colour this tab "
                f"keeps for what was watched rather than read")
            seen += 1
    assert seen, "no Nightlord on this tab carries the sighting at all"


def test_a_sentinel_is_never_printed_as_a_rate(tab):
    """QA-130 and AK-92: `Refills at x-1` was an impossible number.

    `-1` is the files' way of saying there is no value, and Maris is the one
    Nightlord carrying it. Every other refill figure on the tab is positive,
    which is asserted rather than assumed -- if the dataset ever loses its
    sentinel this case says so instead of passing on an empty set.
    """
    sentinels = 0
    for boss in tab.bosses:
        name = boss["name"]
        text = panel(tab, name)
        recovery = (profile_of(tab, name).get("stance") or {}).get("recovery")
        if recovery is None:
            continue
        if recovery > 0:
            assert f"Refills at x{recovery:g}" in text, name
        else:
            sentinels += 1
            assert "Refills at — not in the game's files" in text, name
            assert f"x{recovery:g}" not in text, (
                f"{name}: the sentinel {recovery:g} is printed as a rate")
    assert sentinels, (
        "no Nightlord in this dataset carries a sentinel refill rate, so "
        "this case checked nothing")


def test_a_status_only_weakness_still_opens_the_weakness_section(tab):
    """QA-131 and AK-93: Adel's whole section was unreachable.

    The section was gated on the damage types alone, and Adel is the one
    Nightlord of the ten with no type that hurts him more than another -- so
    his panel began at DAMAGE TAKEN and the note written for him never
    appeared once.

    The boss is found by asking the dataset for the shape, not by name, so the
    case keeps its meaning if another Nightlord ever joins him there.
    """
    status_only = [
        boss["name"] for boss in tab.bosses
        if not profile_of(tab, boss["name"]).get("weak_damage")
        and profile_of(tab, boss["name"]).get("weak_status")]
    assert status_only, (
        "no Nightlord in this dataset has a status weakness and no damage "
        "weakness, so this case checked nothing")

    for name in status_only:
        text = panel(tab, name)
        assert "WEAKNESS SPECIAL INTERACTION" in text, name
        assert "Where it gives way is status" in text, name
        if name in bosstab.WEAKNESS_NOTE:
            assert bosstab.WEAKNESS_NOTE[name] in text, (
                f"{name}: the note written for this Nightlord never reaches "
                f"the panel")


def test_each_block_of_figures_says_what_it_is_measured_against(tab):
    """AK-91: three blocks of numbers, no units and no direction.

    A bar chart that compares a boss with itself looks exactly like one that
    compares it with the others, and on the status list the lower number is
    the better one -- neither was said anywhere.
    """
    text = panel(tab, tab.bosses[0]["name"])
    for note in BLOCK_NOTES:
        assert note in text, f"missing from the panel: {note!r}"


def test_the_tab_opens_with_the_question_it_answers(tab):
    """AK-68 and AK-89, and the click hint said once instead of not at all."""
    lines = tabtext.labels(tab)
    assert lines[0] == bosstab.HEADING
    assert lines[1] == bosstab.QUESTION
    assert lines[2].startswith(f"{len(tab.bosses)} Nightlords"), (
        f"the stock line no longer follows the question: {lines[2]!r}")
    assert lines[2].count("click a card") == 0, (
        "the click hint stands twice on the same screen")


#: The section headings that carry figures, and the note each one has to be
#: read with (A12, QA-149). Written out here rather than imported so a note
#: that quietly changed shows up as a failure instead of following the module.
SECTIONS_AND_THEIR_NOTES = (
    ("DAMAGE TAKEN", "Bars compare this Nightlord's damage types"),
    ("STATUS BUILDUP", "How much status you have to apply before it lands"),
    ("STANCE", "Bar to break is in the game's own stance points"),
    ("IT BUFFS ITSELF", "Buff steps multiply this Nightlord's own attack"),
    ("IT IS WEAKENED", "A step the game's own data gives this Nightlord"),
    ("BODY PARTS", "Damage dealt to that part, against the same hit"),
)


def test_no_block_of_figures_is_left_without_its_reference(tab):
    """QA-149. Four sections carried a note and two did not.

    `Buff x1.35 attack` stood between three neighbours that each said what
    their figures were measured against, and `Part 1  x1.5 damage` under a
    heading whose names the files never give. Checked over all ten panels and
    only where the section is actually drawn: a note under a heading that is
    not there would explain nothing.
    """
    covered = {heading: 0 for heading, _note in SECTIONS_AND_THEIR_NOTES}
    for boss in tab.bosses:
        text = panel(tab, boss["name"])
        for heading, note in SECTIONS_AND_THEIR_NOTES:
            if heading not in text:
                continue
            covered[heading] += 1
            assert note in text, (
                f"{boss['name']}: the section {heading!r} shows figures with "
                f"nothing saying what they are measured against")
    missing = [heading for heading, seen in covered.items() if not seen]
    assert not missing, (
        f"no panel in this dataset draws these sections, so they are not "
        f"checked by this case: {missing}")


def test_the_colour_kept_for_sightings_is_named_where_it_is_used(tab):
    """QA-145 and AK-74. `#7fae72` sat one step from `#6fbf73`, unexplained.

    Two greens differing only in the red channel, one meaning "this is in your
    favour" and the other "somebody watched this happen", and nothing on the
    tab said either. The legend belongs on the panels that use the colour and
    nowhere else: a Nightlord with no sighting must not carry a sentence about
    a colour that is not on its panel.

    Checked over all ten, in both directions, and counted rather than found --
    a legend printed once per sighting would be three sentences on Gladius.

    **Which panels ought to carry it is worked out from the dataset and the
    two sighting lists, not from the colour on the panel.** Reading the colour
    back off the rendered panel would find the legend's own line -- it is
    drawn in the colour it explains -- and agree with itself whatever the
    panel did.
    """
    with_legend, without = 0, 0
    for boss in tab.bosses:
        name = boss["name"]
        text = panel(tab, name)
        profile = profile_of(tab, name)
        expected = bool(
            name in bosstab.WEAKNESS_NOTE
            or name in bosstab.DEBUFF_ON_BREAK
            or (profile.get("ladder") or {}).get("up")
            or profile.get("defence_buffs"))
        count = text.count(bosstab.SIGHTING_LEGEND)
        if expected:
            with_legend += 1
            assert count == 1, (
                f"{name}: the panel carries a line that was watched rather "
                f"than read, and names the colour it is in {count} times")
            assert bosstab.OBSERVED_COLOUR in tab.detail_body.text(), name
        else:
            without += 1
            assert count == 0, (
                f"{name}: the panel explains the sighting colour and has no "
                f"line in it")
    assert with_legend and without, (
        f"{with_legend} panels carry a sighting and {without} do not; this "
        f"case can only tell the two apart when both exist")


def test_the_green_on_the_weakened_step_is_named_like_the_other_two(tab):
    """The third meaning `GOOD` carries, and the one AK-91 does not name.

    `DAMAGE TAKEN` and `STATUS BUILDUP` each say what their green marks. The
    same green then appeared on `Weakened`, against figures describing the
    Nightlord rather than the player, with nothing saying so (QA-145).
    """
    carriers = with_a_down_step(tab)
    assert carriers, "no Nightlord in this dataset carries a weakened step"
    for name in carriers:
        text = panel(tab, name)
        assert bosstab.WEAKENED_NOTE in text, (
            f"{name}: the weakened step is drawn in the same green as the two "
            f"blocks above it and nothing on the panel says what it means")
