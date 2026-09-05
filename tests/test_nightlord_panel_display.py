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
