"""The catalyst row no player can hold is offered nowhere (AK-66, QA-119).

Two rows in the shipped data are called `Recluse's Staff`. One is the
Recluse's own; the other holds no spell, and since the catalyst calibration
of T-046 the two stand side by side in the arsenal tab with figures dozens of
points apart and nothing on either card to say which is the weapon. The
decision (`UI_SPEC.md`, Nachtrag zu QA-119) is to drop the row from every
player-facing list rather than to label it.

**The scope is what this file is really about.** "Carries no spell slot" is
true of 1764 of the 1793 named armaments -- every sword in the game -- so a
filter that asked it without asking `weapon_class` first would empty the
arsenal. Every case below therefore checks both halves: that the one row
goes, and that nothing else does.
"""

from __future__ import annotations

import pytest

from nrplanner import arsenaltab, damage, model, weaponslots

from tests import weapon_damage_cases as cases

#: The row this filter exists for. Named here as the *expectation* of a
#: measurement, not as the criterion: the code finds it by asking what a
#: catalyst without a spell slot is, and this file asks whether the answer is
#: still the row three independent criteria pointed at in T-046 section 7.
ARTEFACT_ID = 33770000
ARTEFACT_NAME = "Recluse's Staff"

LEVEL = 15


@pytest.fixture(scope="module")
def hero(game_data):
    return cases.hero_by_name(game_data, "Recluse")


def test_the_criterion_picks_out_one_row_and_the_scope_is_why(game_data):
    """One row of 1793 -- and 1764 would go without the family check.

    The second figure is the whole reason `is_unequippable_catalyst` asks
    `weapon_class` first, so it is measured here rather than described: if the
    family check were dropped, this is the size of the hole it would leave.
    """
    armaments = game_data["weapons"]
    catalysts = [w for w in armaments
                 if model.weapon_class(w) == "catalyst"]

    def holds_no_spell(weapon) -> bool:
        return all(slot == model.NO_SPELL_SLOT
                   for slot in weapon[model.SPELL_SLOTS_KEY])

    without_the_family_check = [w for w in armaments if holds_no_spell(w)]
    assert len(without_the_family_check) > len(armaments) // 2, (
        f"only {len(without_the_family_check)} of {len(armaments)} armaments "
        f"carry no spell slot, so this criterion no longer describes 'an "
        f"ordinary weapon' and the scope argument has to be re-measured")

    dropped = [w for w in armaments if model.is_unequippable_catalyst(w)]
    assert [w["id"] for w in dropped] == [ARTEFACT_ID], (
        f"the filter drops {[(w['id'], w['name']) for w in dropped]}, not the "
        f"single row T-046 section 7 measured")
    assert dropped[0]["name"] == ARTEFACT_NAME
    assert sum(1 for w in catalysts if holds_no_spell(w)) == 1, (
        "inside the catalyst family the criterion is only sharp while it "
        "picks out exactly one row")


def test_the_dataset_keeps_the_row_and_only_the_lists_lose_it(game_data):
    """`data["weapons"]` is the game, not the offer.

    A measurement over the game's catalysts has to go on finding 30 of them
    (`test_catalyst_scaling_against_the_game.py`), so the filter may not reach
    into the dataset itself.
    """
    armaments = game_data["weapons"]
    assert any(w["id"] == ARTEFACT_ID for w in armaments), (
        "the row was removed from the dataset, which is the one place AK-66 "
        "leaves it")

    offered = model.offerable_weapons(armaments)
    assert len(offered) == len(armaments) - 1
    assert all(w["id"] != ARTEFACT_ID for w in offered)
    assert [w["id"] for w in offered] == [w["id"] for w in armaments
                                          if w["id"] != ARTEFACT_ID], (
        "the helper reordered the list; every caller sorts it for itself and "
        "none of them expects that")


def test_an_older_dataset_loses_no_catalyst(game_data):
    """A record without the field answers "no", not "all of them".

    The dangerous reading of a missing field is "carries no spell slot",
    which would take all 30 catalysts off every list at once. Stated as a
    case because the failure would otherwise be silent and total.
    """
    catalysts = [w for w in game_data["weapons"]
                 if model.weapon_class(w) == "catalyst"]
    assert len(catalysts) == 30, (
        f"this dataset holds {len(catalysts)} catalysts, not the 30 the "
        f"decision was taken over")

    older = [{k: v for k, v in w.items() if k != model.SPELL_SLOTS_KEY}
             for w in catalysts]
    assert not any(model.is_unequippable_catalyst(w) for w in older)
    assert len(model.offerable_weapons(older)) == len(older)


def test_the_facade_does_not_offer_it_as_a_candidate(game_data, hero):
    """`damage.rank_candidates` is the funnel every candidate list drinks."""
    build = model.compute(hero, LEVEL, [], game_data.get("curves", {}))
    ranked = damage.rank_candidates(build, 1, game_data)

    assert len(ranked) == len(game_data["weapons"]) - 1
    assert all(r.weapon["id"] != ARTEFACT_ID for r in ranked)
    named = [r for r in ranked if r.weapon["name"] == ARTEFACT_NAME]
    assert len(named) == 1, (
        f"{ARTEFACT_NAME!r} comes back {len(named)} times, so the collision "
        f"the player sees is not resolved")


def test_the_arsenal_tab_draws_one_card_for_the_name(planner, game_data,
                                                     hero):
    """The screen DR-008 was raised on: two identical cards, two figures.

    Read off the rendered tiles rather than off `tab.ratings`, because two
    cards on screen is what the finding is.
    """
    planner.hero_index = game_data["heroes"].index(hero)
    planner.level_slider.setValue(LEVEL)
    planner.recompute()

    tab = planner.weapons_tab
    tab.search.setText(f'"{ARTEFACT_NAME}"')
    tab.recalculate()
    tiles = tab.scroll.widget().findChildren(arsenaltab.Tile)
    names = [_tile_name(tile) for tile in tiles]

    assert names.count(ARTEFACT_NAME) == 1, (
        f"the tab draws {names.count(ARTEFACT_NAME)} cards called "
        f"{ARTEFACT_NAME!r}: {names!r}")


def test_the_armament_dialog_offers_it_under_no_label(planner, game_data):
    """Not in the list, and the surviving row loses its disambiguating id.

    The id was only ever there because two rows shared the name (QA-099 a).
    With one of them gone the name is its own again, and a lone id beside it
    would be a technical number on a card for no reason.
    """
    from PySide6.QtCore import Qt

    dialog = weaponslots.WeaponDialog(planner, game_data,
                                      weaponslots.WeaponSlot())
    try:
        dialog.search.setText(ARTEFACT_NAME)
        dialog._refresh_list()
        rows = [dialog.list.item(i) for i in range(dialog.list.count())]
        offered = [row.data(Qt.UserRole)["id"] for row in rows]
        labels = [row.text() for row in rows]

        assert ARTEFACT_ID not in offered, (
            f"the dialog still offers {ARTEFACT_ID}: {labels!r}")
        assert labels == [ARTEFACT_NAME], (
            f"the dialog shows {labels!r} for this search, not the one "
            f"unadorned name that is left")

        dialog.search.setText("Finger Seal")
        dialog._refresh_list()
        still_shared = [dialog.list.item(i).text()
                        for i in range(dialog.list.count())]
        assert all(" · " in label for label in still_shared), (
            f"the ids of the collisions that remain were dropped along with "
            f"the filtered row: {still_shared!r}")
    finally:
        dialog.deleteLater()


def _tile_name(tile) -> str:
    """The armament name a tile carries: icon badge first, name second."""
    from PySide6.QtWidgets import QLabel

    labels = tile.findChildren(QLabel)
    assert len(labels) >= 2 and labels[0].text() == "", (
        "the tile header is not the icon badge followed by the name any "
        "more; this helper reads the wrong label")
    return labels[1].text()
