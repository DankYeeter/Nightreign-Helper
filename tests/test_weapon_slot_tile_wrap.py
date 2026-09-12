"""A two-word figure name is never split across the wrap (DR-009).

A weapon slot tile writes rarity, figure and effect counts into one string
and lets Qt wrap it inside a box about 120 px wide. Since T-046 a staff or a
seal is headed by `Spell power` rather than by `AR` -- eleven characters
where there were two -- and the break landed inside the term: `Legendary ·
145 Spell` on the first line, `power` alone on the second. Nothing was cut
off and nothing was wrong; it simply read like a defect
(`docs/screenshots/2026-09-05/weapon-slot-tile-wrap-zoom.png`).

**Laid out, not spot-checked.** Asserting that the string holds a no-break
space would pass just as well if Qt ignored it, which is the interesting half
of the claim. So the tile's own text is run through `QTextLayout` at a width
that is deliberately in the dangerous range, and the same text with an
ordinary space is laid out beside it as the control: the control has to break
inside the term, or the width proves nothing and the case is not measuring
what it says it is.
"""

from __future__ import annotations

import re

import pytest
from PySide6.QtGui import QFontMetrics, QTextLayout

from nrplanner import damage, model, weaponslots

from tests import weapon_damage_cases as cases

LEVEL = 15

#: Legendary, so the figure is three digits and the line is at its longest.
TIER = 4

TAG = re.compile(r"<[^>]+>")


def plain(html: str) -> str:
    """The text a reader sees, with the markup taken out."""
    return TAG.sub("", html)


def wrapped(text: str, font, width: float) -> list[str]:
    """The lines Qt breaks `text` into at this width, in order."""
    layout = QTextLayout(text, font)
    layout.beginLayout()
    out = []
    while True:
        line = layout.createLine()
        if not line.isValid():
            break
        line.setLineWidth(width)
        out.append(text[line.textStart():
                        line.textStart() + line.textLength()])
    layout.endLayout()
    return out


def splits(lines: list[str], term: str) -> bool:
    """Did the wrap cut `term` in half?

    True when a word of the term appears without the whole term beside it,
    which is the only shape of the defect: the term is either on one line or
    it is broken. The no-break space is read as the space it renders as --
    the question is where the words ended up, not which character joined
    them, and comparing the raw characters would answer "broken" for the very
    line that proves it is not.
    """
    shown = [line.replace(weaponslots.NO_BREAK_SPACE, " ") for line in lines]
    if any(term in line for line in shown):
        return False
    return any(word in line for line in shown for word in term.split())


@pytest.fixture(scope="module")
def hero(game_data):
    return cases.hero_by_name(game_data, "Recluse")


@pytest.fixture
def catalyst_tile(planner, game_data, hero):
    """Slot 1 holding a staff, drawn by the planner's own refresh."""
    weapon = cases.weapon_by_id(
        game_data, cases.first_of_family(game_data, "Glintstone Staff"))
    slots = [weaponslots.WeaponSlot()
             for _ in range(weaponslots.SLOT_COUNT)]
    slots[0] = weaponslots.WeaponSlot(weapon=weapon, tier=TIER)

    planner.hero_index = game_data["heroes"].index(hero)
    planner.weapon_slots = slots
    planner.declared = {}
    planner.active_weapon = 0
    planner.selected_effects = lambda: []
    build = model.compute(hero, LEVEL, [], game_data.get("curves", {}),
                          weapon=weapon, weapons_held=[weapon])
    planner._refresh_weapon_damage(build)
    return planner.weapon_tiles[0]


def test_the_tile_names_the_spell_figure_at_all(catalyst_tile):
    """Without this the case below could hold over an empty tile."""
    text = plain(catalyst_tile.detail.text())
    assert damage.SPELL_POWER_LABEL.replace(" ", weaponslots.NO_BREAK_SPACE) \
        in text, (
        f"no spell figure on this tile, so there is no two-word label to "
        f"wrap: {text!r}")


def test_the_figure_name_survives_the_wrap_the_tile_wraps_at(catalyst_tile):
    """The term stays whole where an ordinary space would have split it."""
    shown = plain(catalyst_tile.detail.text())
    term = damage.SPELL_POWER_LABEL
    control = shown.replace(weaponslots.NO_BREAK_SPACE, " ")

    font = catalyst_tile.detail.font()
    metrics = QFontMetrics(font)
    # Wide enough for everything up to the first word of the term and no
    # wider, which is the one band of widths in which the defect appears at
    # all. Derived from this very string rather than written down, so it
    # follows the figure and the rarity name instead of pinning them.
    head = control[:control.index(term) + len(term.split()[0])]
    width = metrics.horizontalAdvance(head) + 1

    assert splits(wrapped(control, font, width), term), (
        f"at {width} px the term would not have broken even with an ordinary "
        f"space, so this width tests nothing: "
        f"{wrapped(control, font, width)!r}")
    assert not splits(wrapped(shown, font, width), term), (
        f"the tile still breaks {term!r} across the wrap: "
        f"{wrapped(shown, font, width)!r}")


def test_a_one_word_label_is_left_exactly_as_it_was(game_data, hero):
    """`AR` gains no no-break space, because it has no space to join.

    The join is `str.replace`, so an armament with a one-word label has to
    come back byte for byte unchanged -- otherwise the fix for a catalyst
    would be quietly rewriting every other tile's text as well.
    """
    build = model.compute(hero, LEVEL, [], game_data.get("curves", {}))
    sword = cases.weapon_by_id(
        game_data, cases.first_of_family(game_data, "Straight Sword"))
    rating = damage.candidate(sword, TIER, build, game_data)
    assert rating.headline_label == damage.ATTACK_RATING_LABEL

    tile = weaponslots.WeaponTile(0, lambda *_: None, lambda *_: None,
                                  lambda *_: None)
    try:
        tile.show_slot(weaponslots.WeaponSlot(weapon=sword, tier=TIER),
                       rating)
        text = tile.detail.text()
        assert weaponslots.NO_BREAK_SPACE not in text, (
            f"a no-break space reached a tile with a one-word label: "
            f"{text!r}")
        assert f"</b> {damage.ATTACK_RATING_LABEL}" in text
    finally:
        tile.deleteLater()
