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

import re

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


#: The watched line every panel with a buff or defence section carries, and
#: the reference the two cases below read the sighting colour off. Written out
#: rather than imported for the reason the module docstring gives: a case that
#: took the colour from `nrplanner.bosstab` would follow that colour wherever
#: it went, including onto lines that were never watched.
WATCHED_REFERENCE = "Stacks: yes"

#: A figure this panel computes for every Nightlord with a stance bar, so it
#: is extracted by construction and can never legitimately be a sighting. It
#: is the other end of the comparison: a panel painted all one colour has to
#: fail, not pass.
COMPUTED_REFERENCE = "for bar size"

_COLOUR = re.compile(r"color:\s*(#[0-9a-fA-F]{6})")


def colour_of(markup: str, needle: str) -> str:
    """The colour this panel draws `needle` in.

    Every span and div the panel builds opens with its own `color:`
    declaration immediately before the text it carries, so the last
    declaration before that text is the one that reaches the reader. Read off
    the markup the label is handed rather than off the module, because what a
    colour says is a claim about what a reader sees.
    """
    at = markup.find(needle)
    assert at >= 0, f"the panel does not draw {needle!r} at all"
    found = _COLOUR.findall(markup, 0, at)
    assert found, f"nothing before {needle!r} on this panel sets a colour"
    return found[-1]


def test_the_buff_trigger_is_drawn_as_the_sighting_it_is(tab):
    """QA-152, the first of AK-94's two gaps. `Set off by` read as extracted.

    `BUFF_TRIGGER` is a list this module keeps from play -- the files carry
    the animation id and never what provokes it -- and its value was printed
    in the same colour as the multiplier extracted directly above it. On a
    panel whose whole point is that a reader can tell a sighting from a
    reading, that row was the one place where the two looked the same.

    Neither colour is imported. The watched one is read off the panel's own
    watched line and the ordinary one off a figure the panel computes, so the
    two have to genuinely differ on the panel for this case to pass at all.
    """
    seen = 0
    for boss in tab.bosses:
        name = boss["name"]
        trigger = bosstab.BUFF_TRIGGER.get(name)
        if trigger is None:
            continue
        panel(tab, name)
        markup = tab.detail_body.text()
        if trigger not in markup:
            continue
        watched = colour_of(markup, WATCHED_REFERENCE)
        computed = colour_of(markup, COMPUTED_REFERENCE)
        assert watched != computed, (
            f"{name}: this panel draws its watched line and its computed "
            f"figures in the same colour ({watched}), so nothing here can "
            f"tell a sighting from a reading")
        assert colour_of(markup, trigger) == watched, (
            f"{name}: `Set off by` was watched in play, and the panel draws "
            f"it in {colour_of(markup, trigger)} -- the colour it gives "
            f"extracted figures -- rather than in {watched}")
        seen += 1
    assert seen, (
        "no Nightlord in this dataset shows a watched buff trigger, so this "
        "case checked nothing")


def test_a_defence_trigger_is_drawn_as_the_sighting_it_is(tab):
    """QA-152, the second gap, and the awkward one T-060 stopped at.

    Half of a defence line is extracted and half of it was watched: the
    figures come from `defence_buffs`, the clause saying what sets the step
    off comes from `DEFENCE_TRIGGER` and somebody's eyes. One colour over the
    whole line would have said the figures were watched too, so the colour
    goes on the clause.

    Both ends of the comparison come off the very same line, which is the
    strongest form this check takes anywhere on the panel: the figure and the
    sighting stand side by side and must not read alike.
    """
    seen = 0
    for boss in tab.bosses:
        name = boss["name"]
        triggers = [text
                    for (owner, _), text in bosstab.DEFENCE_TRIGGER.items()
                    if owner == name]
        if not triggers:
            continue
        panel(tab, name)
        markup = tab.detail_body.text()
        for trigger in triggers:
            if trigger not in markup:
                continue
            extracted = colour_of(markup, "% less damage")
            assert colour_of(markup, trigger) != extracted, (
                f"{name}: the clause saying what sets this defence step off "
                f"was watched in play and is drawn in {extracted}, the same "
                f"colour as the figure beside it on the same line")
            assert colour_of(markup, trigger) == colour_of(
                markup, WATCHED_REFERENCE), (
                f"{name}: the trigger clause is drawn in "
                f"{colour_of(markup, trigger)}, which is not the colour this "
                f"panel keeps for what was watched")
            seen += 1
    assert seen, (
        "no Nightlord in this dataset shows a watched defence trigger, so "
        "this case checked nothing")


# -- AD-041: the same panel, describing a sub-boss -------------------------
#
# The tab's second population. What a sub-boss entry brings with it the panel
# already drew for a Nightlord -- bars, status, stance, body parts -- and the
# cases above cover that. These are about the four places the two differ: the
# HP line the Nightlords never show, the loot block, the stance rank that
# must *not* follow a boss out of the field it ranks against, and the two
# ways the files can decline to say who is on a card.


def subboss(tab, key: str) -> dict:
    """One card of the snapshot, as the tree hands it to the panel."""
    entry = tab.subbosses[key]
    return dict(entry, key=key, share=1.0)


def cards_with(tab, wanted: str) -> list[str]:
    return [key for key, entry in tab.subbosses.items()
            if (entry.get("weakness") or {}).get("confidence") == wanted]


def needs_cards(tab) -> None:
    if not tab.subbosses:
        pytest.skip("this dataset carries no sub-boss cards")


def sub_panel(tab, entry: dict) -> str:
    tab.show_detail(entry)
    return tabtext.plain(tab.detail_body.text())


def a_resolved_card(tab) -> str:
    """A card the files do name, or a skip."""
    needs_cards(tab)
    keys = [key for key in tab.subbosses
            if bosstab.has_card_name(tab.subbosses[key])
            and (tab.subbosses[key]["weakness"] or {}).get("profile")]
    if not keys:
        pytest.skip("no card of this dataset resolves to a named boss")
    return sorted(keys)[0]


def test_a_sub_boss_panel_leads_with_its_role_and_no_borrowed_blurb(tab):
    """AK-322.1/.2 and AK-321.3: what stands above the figures.

    The role line describes the card and not the way in, the description
    stays empty because a sub-boss entry has no such field, and the portrait
    label gives its 180 px back rather than opening every one of these
    panels with an empty block.
    """
    key = a_resolved_card(tab)
    entry = subboss(tab, key)
    tab.show_detail(entry)
    assert tab.detail_name.text() == bosstab.card_name(entry)
    expected = ("Field boss" if not entry["days"]
                else bosstab.card_role(entry["days"]))
    assert tab.detail_expedition.text() == expected
    assert tab.detail_text.text() == "", (
        "the panel puts a description on a card that carries none")
    assert tab.detail_art.minimumHeight() == 0, (
        "a sub-boss panel still reserves room for artwork that does not "
        "exist")

    # And the height comes back for a Nightlord, who does have a portrait.
    tab.show_detail(tab.bosses[0])
    assert tab.detail_art.minimumHeight() == bosstab.DETAIL_ART_HEIGHT


def test_the_hp_of_a_sub_boss_is_shown_and_no_nightlord_shows_one(tab):
    """AK-323: one figure, from the card's own profile, in its own section.

    Both directions. `profile["hp"]` has been in the dataset all along and
    reached nothing, and the block AD-041 adds is for sub-bosses only -- a
    VITALS heading on a Nightlord panel would be the same line put where
    nobody decided to put it.
    """
    key = a_resolved_card(tab)
    entry = subboss(tab, key)
    hp = entry["weakness"]["profile"]["hp"]
    text = sub_panel(tab, entry)
    assert "VITALS" in text
    assert f"HP {hp:g}" in text, (
        f"card {key} carries {hp:g} HP and the panel reads: {text[:200]}")

    for boss in tab.bosses:
        assert "VITALS" not in panel(tab, boss["name"]), (
            f"{boss['name']} is a Nightlord and his panel carries a VITALS "
            f"block")


def test_a_sub_boss_is_not_ranked_against_the_ten_nightlords(tab):
    """AD-041 point 3: the rank's field is the ten, and this is not one.

    The raw stance figures stay -- they are this boss's own numbers -- so the
    case insists on the bar and refuses the ranking beside it. Compared with
    a Nightlord in the same run, or a panel that simply lost its STANCE block
    would pass.
    """
    key = a_resolved_card(tab)
    entry = subboss(tab, key)
    if not (entry["weakness"]["profile"].get("stance") or {}):
        pytest.skip(f"card {key} carries no stance figures to rank")
    text = sub_panel(tab, entry)
    assert "STANCE" in text
    assert "Ranking" not in text, (
        f"a sub-boss is ranked against the ten Nightlords: {text[:300]}")

    ranked = [boss["name"] for boss in tab.bosses
              if "Ranking" in panel(tab, boss["name"])]
    assert ranked, ("no Nightlord shows a ranking either, so this case "
                    "cannot tell the two apart")


def test_a_card_the_files_do_not_identify_shows_no_name_and_stops_there(tab):
    """AK-322.3/.4/.5, both ways the identification can fail.

    Built here rather than fished out of the dataset: which cards are
    `ambiguous` today is a property of the extractor, and a case that
    skipped when the extractor got better at naming them would stop guarding
    the sentence exactly when it still has to.
    """
    needs_cards(tab)
    shared = {"map": "m99_99_00_00", "categories": [120], "days": [],
              "nightlords": [], "chr": None, "share": 1.0}
    ambiguous = dict(shared, key="9998", name="",
                     candidates=[{"chr": 1, "hp": 900},
                                 {"chr": 2, "hp": 2450.5}],
                     weakness={"map": "m99_99_00_00", "chars": [1, 2],
                               "primary": None, "confidence": "ambiguous",
                               "profile": None, "parts": {}})
    unresolved = dict(shared, key="9999", name="", candidates=[],
                      weakness={"map": "m99_99_00_00", "chars": [],
                                "primary": None, "confidence": "unresolved",
                                "profile": None, "parts": {}})

    text = sub_panel(tab, ambiguous)
    assert tab.detail_name.text() == "Multiple possible bosses"
    assert "IDENTITY" in text and "WEAKNESSES" not in text, (
        "the two cases share a heading, so the stronger one reads as the "
        "weaker")
    assert ("Multiple bosses could be on this card — the files don't say "
            "which. Candidates by HP: 2450.5, 900.") in text, text
    for gone in ("VITALS", "LOOT", "DAMAGE TAKEN", "STATUS BUILDUP"):
        assert gone not in text, f"{gone} is drawn for a card nobody named"
    assert not tab.loot_button.isVisibleTo(tab.detail_panel)

    text = sub_panel(tab, unresolved)
    assert tab.detail_name.text() == "Not identified"
    assert "IDENTITY" in text
    assert "Not derivable for this fight." in text
    assert "Candidates by HP" not in text, (
        "a card with no candidates at all lists candidates")
    for gone in ("VITALS", "LOOT", "DAMAGE TAKEN"):
        assert gone not in text


def test_the_loot_of_a_sub_boss_is_shown_rarest_first_five_at_a_time(tab):
    """AK-324: the block itself, its order, and the toggle behind it.

    The order is checked against `world_events.drops` as the snapshot holds
    it, because "rarest first" is a claim about the data and not about the
    module: sorting the other way round, or not at all, has to fail here.
    """
    needs_cards(tab)
    # The card whose open five span the widest range of chances. On a card
    # whose twenty drops all read `5%` the order is decided entirely by the
    # alphabetical tiebreaker, and reversing the sort would hold such a list
    # the wrong way round just as happily -- so the case picks one where
    # rarest-first is something the screen can actually show.
    def spread(key: str) -> float:
        drops = sorted(tab.drops.get(str(tab.subbosses[key].get("chr")))
                       or [], key=lambda drop: (drop["share"], drop["name"]))
        if len(drops) <= bosstab.LOOT_OPEN:
            return 0.0
        return drops[bosstab.LOOT_OPEN - 1]["share"] - drops[0]["share"]

    keys = [key for key in sorted(tab.subbosses)
            if (tab.subbosses[key]["weakness"] or {}).get("profile")]
    keys.sort(key=spread, reverse=True)
    if not keys or spread(keys[0]) <= 0:
        pytest.skip(f"no card of this dataset shows more than "
                    f"{bosstab.LOOT_OPEN} drops at two different chances")
    entry = subboss(tab, keys[0])
    drops = sorted(tab.drops[str(entry["chr"])],
                   key=lambda drop: (drop["share"], drop["name"]))

    text = sub_panel(tab, entry)
    loot = text[text.index("LOOT"):]
    assert loot.count("%") == bosstab.LOOT_OPEN + 1, (
        f"the open loot list shows {loot.count('%') - 1} figures instead of "
        f"{bosstab.LOOT_OPEN} (the note's own `100%` is the extra one)")
    at = [loot.index(drop["name"]) for drop in drops[:bosstab.LOOT_OPEN]]
    assert at == sorted(at), (
        f"the five open drops are not in rarest-first order: "
        f"{[(d['name'], d['share']) for d in drops[:bosstab.LOOT_OPEN]]}")
    assert drops[-1]["name"] not in loot, (
        f"{drops[-1]['name']} falls at {drops[-1]['share']:g}%, the "
        f"commonest thing this boss drops, and it stands in the open five")
    assert ("Percentages are the game's own drop tables" in loot
            and "the shortfall is missing data" in loot), (
        "the block of percentages carries no word about the ones that do "
        "not add up")

    rest = len(drops) - bosstab.LOOT_OPEN
    assert rest > 0
    assert tab.loot_button.text() == f"Show {rest} more"
    tab.loot_button.click()
    opened = tabtext.plain(tab.detail_body.text())
    opened = opened[opened.index("LOOT"):]
    assert opened.count("%") == len(drops) + 1, (
        f"opening the list shows {opened.count('%') - 1} of {len(drops)} "
        f"drops")
    assert opened.count("LOOT") == 1, "the rest went into a second block"
    assert tab.loot_button.text() == "Show fewer"
    tab.loot_button.click()
    assert tab.loot_button.text() == f"Show {rest} more"

    # And another card starts closed again, however the last one was left.
    tab.loot_button.click()
    other = next((key for key in sorted(keys) if key != entry["key"]), None)
    if other is not None:
        sub_panel(tab, subboss(tab, other))
        assert tab.loot_button.text().startswith("Show "), (
            "the next card opened with the last card's toggle state")
        assert tab.loot_button.text() != "Show fewer"


def test_the_loot_toggle_answers_to_more_than_a_mouse(tab):
    """QA-288: `toggle()` opens the list, the way `Hold`/`Held` does.

    The button came bound to `clicked`, which a mouse and a pressed space bar
    emit and nothing else. A screen reader calls `TogglePattern.Toggle()`,
    the accessibility bridge turns that into `QAbstractButton::toggle()`, and
    the panel stayed as it was -- checked button, five drops (found at the
    artefact, T-312c). `toggled` is the one signal all three ways pass
    through, which is why AK-54's `Hold` button has always used it.
    """
    needs_cards(tab)
    key = next((key for key in sorted(tab.subbosses)
                if (tab.subbosses[key]["weakness"] or {}).get("profile")
                and len(tab.drops.get(str(tab.subbosses[key].get("chr")))
                        or []) > bosstab.LOOT_OPEN), None)
    if key is None:
        pytest.skip(f"no card of this dataset drops more than "
                    f"{bosstab.LOOT_OPEN} things")
    entry = subboss(tab, key)
    count = len(tab.drops[str(entry["chr"])])
    closed = sub_panel(tab, entry)
    assert closed.count("%") == bosstab.LOOT_OPEN + 1

    tab.loot_button.toggle()
    opened = tabtext.plain(tab.detail_body.text())
    assert opened.count("%") == count + 1, (
        f"toggling the button left {opened.count('%') - 1} of {count} drops "
        f"on screen: the list answers to the mouse and not to the keyboard "
        f"or to assistive software, which reach `toggle()`")
    assert tab.loot_button.text() == "Show fewer"
    tab.loot_button.toggle()
    shut = tabtext.plain(tab.detail_body.text())
    assert shut.count("%") == bosstab.LOOT_OPEN + 1, (
        "toggling a second time did not close the list again")
    assert tab.loot_button.text() == f"Show {count - bosstab.LOOT_OPEN} more"

    # And the Tab key gets there in the first place: a button nobody can
    # focus is one nobody can press the space bar on. Read off the policy
    # rather than off a Tab keystroke, because focus travels only in an
    # active window and this panel is built offscreen.
    from PySide6.QtCore import Qt

    assert tab.loot_button.focusPolicy() & Qt.TabFocus, (
        "the toggle is out of the tab order")
    assert tab.loot_button.isVisibleTo(tab.detail_panel), (
        "the toggle is not on the panel at all")


def test_a_sub_boss_with_no_drops_says_so_rather_than_showing_nothing(tab):
    """AK-324.2, in the voice the panel already uses for a missing blurb."""
    needs_cards(tab)
    key = next((key for key in sorted(tab.subbosses)
                if not tab.drops.get(str(tab.subbosses[key].get("chr")))
                and (tab.subbosses[key]["weakness"] or {}).get("profile")),
               None)
    if key is None:
        pytest.skip("every named card of this dataset drops something")
    text = sub_panel(tab, subboss(tab, key))
    assert "LOOT" in text
    assert "no loot recorded in the files" in text
    assert "Percentages are the game" not in text, (
        "the note about percentages stands over a block with none in it")


# -- AD-040.3/.5: the night bosses of day 1 and day 2 ----------------------


def test_both_night_groups_stand_under_every_nightlord(tab):
    """Stage two, seen from the tab: `days` is what fills the two groups.

    The groups were built in T-306 and stood empty, because the night
    lottery (`LotResultPlayAreaParam`) had not been read yet -- an expedition
    that shows only field bosses is what this tab looked like then, and it is
    what a lost join would make it look like again. Every Nightlord draws on
    both of its nights, so every one of the ten has to show both groups.
    """
    needs_cards(tab)
    for boss in tab.bosses:
        tab.show_detail(boss)
        groups = [tab.tree.topLevelItem(index).text(0)
                  for index in range(tab.tree.topLevelItemCount())]
        assert groups == ["NIGHT BOSSES  ·  DAY 1",
                          "NIGHT BOSSES  ·  DAY 2",
                          "FIELD BOSSES"], (
            f"{boss['name']} opens the tree with the groups {groups}")


def test_a_night_card_says_which_night_it_is_drawn_for(tab):
    """AK-322.1, now that there are cards to say it of.

    Read off the panel and against the card's own `days`, both ways round: a
    field card must not pick up a night line either.

    No card of this dataset is drawn on both nights (measured T-308: 18 cards
    on day 1, 17 on day 2, none on both), so the `also Day 2` line of
    `card_role` has no case here and is left to `test_nightlord_selection`,
    where the tree row carries it.
    """
    needs_cards(tab)
    for key, entry in sorted(tab.subbosses.items()):
        sub_panel(tab, subboss(tab, key))
        role = tab.detail_expedition.text()
        days = entry["days"]
        expected = ("Field boss" if not days
                    else "Night boss  ·  Day 1 & 2" if days == [1, 2]
                    else f"Night boss  ·  Day {days[0]}")
        assert role == expected, (
            f"card {key} is drawn on {days} and the panel calls it {role!r}")
