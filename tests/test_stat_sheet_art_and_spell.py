"""The two new rows of the damage panel: `Weapon art` and `Spell damage`.

`UI_SPEC.md` section 4.5, AK-353..AK-364, and the criterion `GOAL.md` A27
states in the player's own words: Revenant with the Beast Claw relic reads
`Spell damage (Beast Claw)` beside his claws' attack rating and a physical
attack relic moves both rows, while Wylder reads `Weapon art` and a skill
buff moves that row alone.

Read off the rendered label, not off the objects behind it: what the player
compares are the two figures as they are written, and a row that is computed
but not drawn is not a row. The figures themselves are asserted against the
facade rather than against literals -- the point of every case here is that
the panel asks `damage` the same question the advisor asks it (AD-019), not
that the uncalibrated product has a particular value (OF-54).
"""

from __future__ import annotations

import html
import re

import pytest

from nrplanner import damage, model, statsheet, weaponslots, weapons

from tests import weapon_damage_cases as cases

LEVEL = 15
TIER = 1

#: "Changes compatible armament's incantation to Beast Claw at start of
#: expedition" -- one of the ten swap relics (AD-052 point 2), Revenant's.
#: It carries no rate at all: what it moves is the base value of the spell in
#: his hand, which is why it is the relic the A27 criterion is written around.
BEAST_CLAW_RELIC = 7370900
#: "Improved Skill Attack Power": scope 112/111, so its five attack rates
#: reach the Weapon Art and nothing else (`model.art_factor`).
SKILL_BUFF = 312300

#: A figure with its two-handed twin where the armament has one (AK-286):
#: `123 1H / 151 2H`, the twin in a quiet span of its own
#: (`damage.displayed_hands`). Only the one-handed figure is read.
FIGURE = (r"(-?\d+)"
          r"(?: 1H<span[^>]*> / -?\d+ 2H</span>)?")

#: `Weapon art <grey> <change> <bold>` (AK-355), the wording out of
#: `model.ART_LABELS` (AK-363).
ART_ROW = re.compile(
    rf"<div>Weapon art <span style='color:[^']*'>{FIGURE}</span> "
    rf"<span style='color:[^']*'>([^<]*)</span> "
    rf"<b style='color:[^']*'>{FIGURE}</b></div>")

#: `Spell damage (<spell>) <grey> <change> <bold, a link>` (AK-359/AK-361),
#: and deliberately without the two-handed alternative above: the two-handing
#: bucket does not reach a spell (AD-053 point 4), so a twin here would be a
#: failure to match rather than a case this pattern has to allow for.
SPELL_ROW = re.compile(
    r"<div>Spell damage \(([^)]*)\) "
    r"<span style='color:[^']*'>(-?\d+)</span> "
    r"<span style='color:[^']*'>([^<]*)</span> "
    rf"<a href='{statsheet.SPELL_BREAKDOWN_KEY}'[^>]*>"
    r"<b>(-?\d+)</b></a></div>")

#: The panel's own total row, the yardstick the Weapon art row is compared
#: against (AK-355) and the row AK-362 keeps apart from the other two.
TOTAL_ROW = re.compile(
    rf"<b>Total</b> <span style='color:[^']*'>{FIGURE}</span> "
    rf"<a href='{statsheet.AR_BREAKDOWN_KEY}'[^>]*>([^<]*)</a>")


def panel(planner) -> str:
    return planner.stat_sheet.ar_label.text()


def art_row(planner):
    """(grey, change, bold) of the Weapon art row, or None where none is drawn."""
    match = ART_ROW.search(panel(planner))
    return match and (int(match.group(1)), match.group(2), int(match.group(3)))


def spell_row(planner):
    """(spell, grey, change, bold), or None where the row is not drawn."""
    match = SPELL_ROW.search(panel(planner))
    return match and (match.group(1), int(match.group(2)), match.group(3),
                      int(match.group(4)))


def total_row(planner):
    match = TOTAL_ROW.search(panel(planner))
    assert match, f"no total row in the panel: {panel(planner)!r}"
    return int(match.group(1)), match.group(2)


def draw(planner, game_data, hero, effect_ids=(), armaments=None,
         active: int = 0):
    """Fill the grid, draw it, and hand back the build it was drawn on.

    `armaments` is `(slot index, armament id)` pairs; slot 1 holds this
    Nightfarer's own starting armament by default, which is the state the
    window opens in (`Planner.apply_hero_weapon`).

    The whole sheet is drawn and not only the damage panel, because the
    click-through reads the build's effect sources off the sheet and `draw`
    is what puts them there -- the window's own order.
    """
    effects = [cases.effect_by_id(game_data, i) for i in effect_ids]
    pairs = armaments or ((0, hero["starting_weapon"]),)
    slots = [weaponslots.WeaponSlot() for _ in range(weaponslots.SLOT_COUNT)]
    for index, weapon_id in pairs:
        slots[index] = weaponslots.WeaponSlot(
            weapon=cases.weapon_by_id(game_data, weapon_id), tier=TIER)
    planner.hero_index = game_data["heroes"].index(hero)
    planner.weapon_slots = slots
    planner.declared = {}
    planner.active_weapon = active
    planner.selected_effects = lambda: effects
    build = model.compute(
        hero, LEVEL, effects, game_data.get("curves", {}),
        weapon=slots[active].weapon,
        weapons_held=[s.weapon for s in slots if s.filled])
    planner.stat_sheet.draw(build, {})
    return build


def spell_figure(game_data, hero, build) -> damage.SpellRating:
    """What the facade answers for this build -- the panel's own question."""
    catalyst = damage.start_catalyst(hero, game_data)
    thrown = damage.spell_thrown(build, game_data, catalyst)[0]
    return damage.spell(
        thrown, catalyst, weapons.MIN_UPGRADE, build, game_data,
        hit_with=damage.GENUS_OF_CATALYST[catalyst["wep_type"]])


@pytest.fixture
def physical_relic(game_data):
    """A relic that raises the general physical attack rate, whoever holds it.

    Asked of the dataset rather than written down: it has to reach the spell
    and the swing alike, which is the premise A26 stands on.
    """
    def pick(hero):
        return cases.effects_raising_rate(
            game_data, hero, "physicsAttackRate", 1)[0]
    return pick


def test_revenant_reads_his_swapped_spell_beside_the_claws_attack_rating(
        planner, game_data):
    """The A27 criterion: `Spell damage (Beast Claw)` under the claws' total.

    The seal is in Revenant's left hand and sits on no tile at all, so the
    row hangs off the right starting hand (AK-353 point 2, first case). The
    figure is the facade's, and the band around it is the one the criterion
    names -- a product two decimal orders away from it would mean the panel
    is asking about something else.
    """
    hero = cases.hero_by_name(game_data, "Revenant")
    build = draw(planner, game_data, hero, [BEAST_CLAW_RELIC])

    rating = spell_figure(game_data, hero, build)
    assert rating.spell["name"] == "Beast Claw"
    row = spell_row(planner)
    assert row, f"no spell row in the panel: {panel(planner)!r}"
    spell_name, grey, change, bold = row
    assert spell_name == "Beast Claw"
    assert bold == damage.displayed(rating.figure)
    assert 500 <= bold <= 650, (
        f"the criterion reads about 578 for this pairing and the panel shows "
        f"{bold}")
    # Nothing but the swap relic is equipped, and it carries no rate: the
    # baseline and the figure are one and the same (AK-359).
    assert grey == bold
    assert change == "no change"


def test_a_physical_attack_relic_moves_the_spell_row_and_the_total_alike(
        planner, game_data, physical_relic):
    """The second half of the A27 criterion, and the premise of A26.

    The general `*AttackRate` family reaches a spell exactly as it reaches a
    swing (combination table), so both rows move -- and the spell row's
    baseline stays where it was, because a relic-free figure is what it is.
    """
    hero = cases.hero_by_name(game_data, "Revenant")
    draw(planner, game_data, hero, [BEAST_CLAW_RELIC])
    before_spell = spell_row(planner)
    before_total = total_row(planner)

    draw(planner, game_data, hero,
         [BEAST_CLAW_RELIC, physical_relic(hero)])
    spell_name, grey, change, bold = spell_row(planner)

    assert spell_name == "Beast Claw"
    assert grey == before_spell[1], (
        "the baseline of the spell row moved with an equipped relic, so it "
        "is not a baseline")
    assert re.fullmatch(r"\+\d+", change), (
        f"the physical relic left the spell row's change at {change!r}")
    assert bold > before_spell[3]
    assert re.fullmatch(r"\+\d+", total_row(planner)[1]), (
        f"the same relic left the total row's change at "
        f"{total_row(planner)[1]!r}, so the case shows nothing about both "
        f"rows moving")
    assert total_row(planner)[0] == before_total[0]


def test_wylder_s_weapon_art_row_moves_under_a_skill_buff_and_not_otherwise(
        planner, game_data, physical_relic):
    """The other half of the A27 criterion, in both directions.

    A skill-scoped relic moves this row and leaves the total alone; a
    physical attack relic moves the total and leaves this row's difference at
    `no change`, because its baseline is the total beside it rather than a
    relic-free figure (AK-355). Both halves are needed: with either one
    missing, a row that simply repeated the total would pass.
    """
    hero = cases.hero_by_name(game_data, "Wylder")
    draw(planner, game_data, hero)
    assert art_row(planner) == pytest.approx(art_row(planner))
    bare_grey, bare_change, bare_bold = art_row(planner)
    assert bare_change == "no change" and bare_grey == bare_bold, (
        "with nothing equipped the Weapon Art reaches no factor, so the row "
        "has to read as unmoved")

    draw(planner, game_data, hero, [SKILL_BUFF])
    grey, change, bold = art_row(planner)
    assert re.fullmatch(r"\+\d+", change), (
        f"the skill buff left the Weapon art row at {change!r}")
    assert bold > grey
    assert total_row(planner)[1] == "no change", (
        "the skill buff moved the total row as well, and scope 112/111 "
        "reaches the Weapon Art alone")

    draw(planner, game_data, hero, [physical_relic(hero)])
    assert art_row(planner)[1] == "no change", (
        "a physical attack relic moved the Weapon art row's difference; its "
        "baseline is the total above it, which the same relic lifts by the "
        "same amount")
    assert re.fullmatch(r"\+\d+", total_row(planner)[1])


def test_wylder_gets_no_spell_row_at_all(planner, game_data):
    """AK-358: eight of the ten start with neither staff nor seal.

    Not a sentence either -- this panel leaves out what does not apply, the
    way it leaves out a status it inflicts nothing of.
    """
    hero = cases.hero_by_name(game_data, "Wylder")
    draw(planner, game_data, hero, [BEAST_CLAW_RELIC])

    assert damage.start_catalyst(hero, game_data) is None
    assert damage.SPELL_DAMAGE_NAME not in panel(planner)


def test_a_catalyst_in_the_starting_hand_says_why_it_has_no_weapon_art(
        planner, game_data):
    """AK-356, and AK-358's other half: Recluse gets the sentence and a spell.

    Her staff is the starting armament, so the head of the tile is a spell
    power and no attack art reaches it (AD-053 point 5) -- but the spell row
    below is untouched by that and shows the sorcery the staff really casts.
    """
    hero = cases.hero_by_name(game_data, "Recluse")
    build = draw(planner, game_data, hero)

    assert art_row(planner) is None, (
        "a catalyst was given a Weapon art figure, and the game shows it no "
        "attack rating for an art to reach")
    assert statsheet.ART_ON_A_CATALYST.format(
        art=model.ART_LABELS[model.SKILL_ART]) in panel(planner)

    rating = spell_figure(game_data, hero, build)
    spell_name, _grey, _change, bold = spell_row(planner)
    assert spell_name == rating.spell["name"]
    assert bold == damage.displayed(rating.figure)


def test_a_nightfarer_whose_seal_throws_nothing_reads_a_figure_of_zero(
        planner, game_data):
    """AK-360: `Spell damage (Rejection) 0`, and the facade's own sentence.

    Revenant's default state, not an edge case: the Finger Seal casts
    Rejection, which damages nothing, and a zero with a reason is the answer
    (AD-052 point 5). The sentence is in the click-through, where AK-361 puts
    it, and it is the particular one -- never both, never the general one.
    """
    hero = cases.hero_by_name(game_data, "Revenant")
    draw(planner, game_data, hero)

    spell_name, grey, change, bold = spell_row(planner)
    assert (spell_name, grey, bold) == ("Rejection", 0, 0)
    assert change == "no change"

    # Escaped where it is drawn, because this tooltip is rich text and the
    # spell's name is game text (SEC-019).
    note = planner.stat_sheet._spell_breakdown_text()
    assert html.escape(damage.NO_SPELL_DAMAGE.format(name="Rejection")) in note
    assert "uncalibrated" not in note


def test_the_click_through_carries_the_baseline_and_the_uncalibrated_note(
        planner, game_data, physical_relic):
    """AK-361: the baseline, the rates with their relics, the figure, the note.

    Exactly one of the two sentences, and here the general one -- the spell
    does carry damage, so the particular sentence has nothing to say.
    """
    hero = cases.hero_by_name(game_data, "Revenant")
    relic = physical_relic(hero)
    build = draw(planner, game_data, hero, [BEAST_CLAW_RELIC, relic])
    rating = spell_figure(game_data, hero, build)

    note = planner.stat_sheet._spell_breakdown_text()
    assert "Beast Claw" in note
    assert f"<b>{damage.displayed(rating.bare_figure)}</b>" in note
    assert f"{damage.SPELL_DAMAGE_NAME} {damage.displayed(rating.figure)}" \
        in note
    # The sources are filed under the effect's name with its whitespace
    # collapsed, the way `model.compute` records it.
    name = " ".join(cases.effect_by_id(game_data, relic)["name"].split())
    assert name in note, (
        "the click-through names no relic behind the rate that moved the "
        "figure, which is the whole of what it is for")
    assert html.escape(damage.SPELL_DAMAGE_UNCALIBRATED.format(
        name=damage.SPELL_DAMAGE_NAME)) in note
    assert "deals no damage" not in note


def test_neither_row_stands_on_an_armament_found_in_the_run(
        planner, game_data):
    """AK-353 point 3: on any other tile the panel is exactly what it was.

    The claws stay in slot 1 in the background; what is active is a bow the
    player picked up, and neither row belongs to it.
    """
    hero = cases.hero_by_name(game_data, "Revenant")
    draw(planner, game_data, hero, [BEAST_CLAW_RELIC],
         armaments=((0, hero["starting_weapon"]),
                    (2, cases.first_of_family(game_data, "Bow"))),
         active=2)

    assert art_row(planner) is None
    assert damage.SPELL_DAMAGE_NAME not in panel(planner)


def test_the_starting_catalyst_carries_the_spell_row_onto_its_own_tile(
        planner, game_data):
    """AK-353 point 2, second case: the seal put on a tile by the player.

    Revenant's seal is in his left hand, which has no tile of its own; a
    player who gives it one reads the spell row there -- and no Weapon art
    row, because that follows the starting **armament** pairing (AK-353
    point 1) and a seal in slot 3 is not it.
    """
    hero = cases.hero_by_name(game_data, "Revenant")
    seal = damage.start_catalyst(hero, game_data)
    build = draw(planner, game_data, hero, [BEAST_CLAW_RELIC],
                 armaments=((0, hero["starting_weapon"]), (2, seal["id"])),
                 active=2)

    assert art_row(planner) is None
    assert statsheet.ART_ON_A_CATALYST.format(
        art=model.ART_LABELS[model.SKILL_ART]) not in panel(planner)
    rating = spell_figure(game_data, hero, build)
    assert spell_row(planner)[3] == damage.displayed(rating.figure)


def test_the_hand_switch_moves_no_figure_of_the_spell_row(
        planner, game_data):
    """AK-359: no two-handed twin, at either stand of the switch.

    A criterion of its own and not a footnote: the two-handing bucket is one
    of the four things AD-053 keeps out of a spell, so a row that grew a
    `/ ... 2H` here would be showing a factor the spell never took.
    """
    hero = cases.hero_by_name(game_data, "Revenant")
    draw(planner, game_data, hero, [BEAST_CLAW_RELIC])
    one_handed = spell_row(planner)

    planner.stat_sheet.hand_switch.setChecked(True)
    draw(planner, game_data, hero, [BEAST_CLAW_RELIC])
    assert spell_row(planner) == one_handed
    assert damage.TWO_HANDED_MARK not in SPELL_ROW.search(panel(planner))[0]
