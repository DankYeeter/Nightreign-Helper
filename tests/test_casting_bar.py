"""The casting bar under the tiles (AK-410..419, F1, OF-59), offscreen.

No dialog is opened: the pool popup is built and read, never shown, and a
choice goes through the bar's own signal as a click would send it.
"""

from __future__ import annotations

import html

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QColor, QKeyEvent

from nrplanner import castingbar, damage, weaponslots
from tests import weapon_damage_cases as cases
from tests.test_stat_sheet_art_and_spell import draw, spell_row

GLINTSTONE_PEBBLE = 4000
GLINTSTONE_ARC = 4070
LIGHTNING_SLASH_RELIC = 7123200
MAGIC_LONGSWORD = 2000800


def bar(planner):
    return planner.stat_sheet.casting


def shown(planner) -> bool:
    return bar(planner).isVisibleTo(planner.stat_sheet.widget())


def chips(planner) -> list[castingbar.Chip]:
    return [w.chip for w in bar(planner).chip_widgets]


def popup_ids(planner, caption: str) -> list[int]:
    widget = next(w for w in bar(planner).chip_widgets
                  if w.chip.caption == caption)
    popup = castingbar.PoolPopup(widget.chip, None, lambda *_: None, widget,
                                 300)
    ids = [popup.list.item(i).data(Qt.UserRole)
           for i in range(popup.list.count())]
    popup.deleteLater()
    return ids


def art_popup(planner) -> castingbar.PoolPopup:
    widget = bar(planner).chip_widgets[0]
    return castingbar.PoolPopup(widget.chip, None, lambda *_: None, widget,
                                300)


def accent_pixels(item) -> int:
    image = item.icon().pixmap(castingbar.ICON_SIZE).toImage()
    accent = QColor(castingbar.ACCENT).rgb()
    return sum(image.pixel(x, y) == accent for x in range(image.width())
               for y in range(image.height()))


def footer(popup, row: int) -> str:
    popup.list.setCurrentRow(row)
    return popup.footer.text()


def test_the_default_art_carries_the_dot_in_the_popup(planner, game_data):
    """QA-313/AK-411: Wylder's own art, first, with the ACCENT dot; the
    second entry without it."""
    draw(planner, game_data, cases.hero_by_name(game_data, "Wylder"))
    popup = art_popup(planner)

    assert [accent_pixels(popup.list.item(row)) > 0 for row in (0, 1)] == [
        True, False]
    assert footer(popup, 0).endswith(castingbar.OWN_ART_NOTE)
    popup.deleteLater()


def test_wylder_gets_one_art_chip_whose_popup_is_his_pool(planner, game_data):
    wylder = cases.hero_by_name(game_data, "Wylder")
    draw(planner, game_data, wylder)
    greatsword = cases.weapon_by_id(game_data, wylder["starting_weapon"])

    assert shown(planner)
    assert [c.caption for c in chips(planner)] == [castingbar.ART_CAPTION]
    assert chips(planner)[0].record["id"] == greatsword["art_default"]
    ids = popup_ids(planner, castingbar.ART_CAPTION)
    assert set(ids) == set(greatsword["art_pool"])
    assert ids[0] == greatsword["art_default"]


def test_an_empty_tile_has_no_bar(planner, game_data):
    wylder = cases.hero_by_name(game_data, "Wylder")
    draw(planner, game_data, wylder, active=1)

    assert not shown(planner)
    assert not chips(planner)


def test_recluse_reads_r1_and_r2_and_r2_opens_her_slot_2_pool(
        planner, game_data):
    recluse = cases.hero_by_name(game_data, "Recluse")
    draw(planner, game_data, recluse)
    staff = cases.weapon_by_id(game_data, recluse["starting_weapon"])

    first, second = chips(planner)
    assert (first.caption, first.record["id"], first.selected) == (
        "R1", GLINTSTONE_PEBBLE, True)
    assert (second.caption, second.record["id"]) == ("R2", GLINTSTONE_ARC)
    assert set(popup_ids(planner, "R2")) == set(staff["spell_pools"][1])
    # AK-415 (a): the chip in use shows the spell row's figure.
    assert first.figure_line == str(spell_row(planner)[3])


def test_a_chosen_spell_is_cast_and_survives_a_nightfarer_switch(
        planner, game_data):
    """AK-414 over `weapon_loadouts`, the road `apply_hero_weapon` takes."""
    recluse = cases.hero_by_name(game_data, "Recluse")
    draw(planner, game_data, recluse)
    planner._store_weapon_loadout()
    bar(planner).spell_chosen.emit(GLINTSTONE_ARC)

    assert spell_row(planner)[0] == "Glintstone Arc"
    assert [c.selected for c in chips(planner)] == [False, True]
    planner.hero_index = game_data["heroes"].index(
        cases.hero_by_name(game_data, "Wylder"))
    planner.apply_hero_weapon()
    planner.hero_index = game_data["heroes"].index(recluse)
    planner.apply_hero_weapon()
    assert planner.active_slot().spell_id == GLINTSTONE_ARC


def test_the_dialog_keeps_the_choice_for_the_same_armament_only(
        qapp, game_data):
    recluse = cases.hero_by_name(game_data, "Recluse")
    staff = cases.weapon_by_id(game_data, recluse["starting_weapon"])
    slot = weaponslots.WeaponSlot(staff, art_id=None, spell_id=GLINTSTONE_ARC)
    dialog = weaponslots.WeaponDialog(None, game_data, slot)
    try:
        assert dialog.result_slot().spell_id == GLINTSTONE_ARC
        other = cases.weapon_by_id(game_data, cases.first_of_family(
            game_data, "Bow"))
        dialog.slot.weapon = staff
        item = weaponslots.QListWidgetItem()
        item.setData(Qt.UserRole, other)
        dialog._on_weapon_changed(item, None)
        assert dialog.result_slot().spell_id is None
    finally:
        dialog.deleteLater()


def test_a_swap_relic_shows_one_relic_chip_and_says_so(planner, game_data):
    wylder = cases.hero_by_name(game_data, "Wylder")
    draw(planner, game_data, wylder, [LIGHTNING_SLASH_RELIC])

    (chip,) = chips(planner)
    assert chip.caption == castingbar.RELIC_CAPTION
    assert bar(planner).note.text() == castingbar.SWAP_NOTE.format(
        what="skill", name=chip.record["name"])


def test_the_chips_sit_between_the_tiles_and_the_hand_switch_in_tab_order(
        planner, game_data):
    """AK-413: tiles -> R1 -> R2 -> hand switch (QA-312: the tiles too)."""
    draw(planner, game_data, cases.hero_by_name(game_data, "Recluse"))
    chain = [*planner.stat_sheet.weapon_tiles, *bar(planner).chip_widgets,
             planner.stat_sheet.hand_switch]

    def next_tab_stop(widget):
        widget = widget.nextInFocusChain()
        while not widget.focusPolicy() & Qt.TabFocus:
            widget = widget.nextInFocusChain()
        return widget

    assert [next_tab_stop(widget) for widget in chain[:-1]] == chain[1:]


def test_enter_on_a_tile_selects_it(planner, game_data):
    """QA-312: a tile reached by Tab is selected with Enter or Space."""
    draw(planner, game_data, cases.hero_by_name(game_data, "Wylder"),
         armaments=((1, MAGIC_LONGSWORD), (2, MAGIC_LONGSWORD)))
    tiles = planner.stat_sheet.weapon_tiles
    for index, key in ((1, Qt.Key_Return), (2, Qt.Key_Space)):
        tiles[index].keyPressEvent(
            QKeyEvent(QEvent.KeyPress, key, Qt.NoModifier))
        assert planner.active_weapon == index


def test_a_chip_shows_game_text_as_text(planner, game_data):
    """AK-419: name as plain text, tooltip escaped."""
    draw(planner, game_data, cases.hero_by_name(game_data, "Wylder"))
    hostile = dict(chips(planner)[0].record, name="<b>Stamp</b>")
    widget = castingbar.ChipWidget(
        castingbar.Chip("art", "ART", hostile, (), False, None, True, ""),
        None, lambda _w: None)

    assert widget.name.textFormat() == Qt.PlainText
    assert html.escape("<b>Stamp</b>") in widget.toolTip()
    assert "<b>Stamp</b>" not in widget.toolTip()
    widget.deleteLater()


def test_the_bar_asks_the_facade_for_the_art(planner, game_data):
    """AK-415 (one source): the chip's art is `damage.art_in_use`'s."""
    wylder = cases.hero_by_name(game_data, "Wylder")
    build = draw(planner, game_data, wylder)

    art, _ = damage.art_in_use(planner.active_slot(), 0, build, wylder,
                               game_data)
    assert chips(planner)[0].record is art
