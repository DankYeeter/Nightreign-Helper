"""The game's own symbols stand beside names, and a missing one costs nothing
(T-340): no symbol is no `<img>`, no exception, and the name unchanged."""

from __future__ import annotations

import json
import pathlib
import types

import pytest
from PySide6.QtGui import QColor, QImage, QPixmap

from nrplanner import iconpack, paths, relicslots

RED, BLUE, DEEP_RED = QColor("#ff0000"), QColor("#0000ff"), QColor("#800000")


def _sprite(folder: pathlib.Path, name: str, colour: QColor) -> str:
    image = QImage(64, 64, QImage.Format_ARGB32)
    image.fill(colour)
    image.save(str(folder / name))
    return name


@pytest.fixture
def pack(tmp_path, monkeypatch, qapp) -> iconpack.IconPack:
    """A pack with one slot light per kind, a status and an item symbol."""
    manifest = {
        "portraits": {}, "items": {"7": _sprite(tmp_path, "item_7.png", RED)},
        "variants": {}, "menu": {},
        "status": {"20206": _sprite(tmp_path, "status.png", BLUE)},
        "ui": {
            "MENU_MenuIcon_40240.png": _sprite(tmp_path, "red.png", RED),
            "MENU_MenuIcon_40241.png": _sprite(tmp_path, "blue.png", BLUE),
            "MENU_MenuIcon_40254.png": _sprite(tmp_path, "deep.png", DEEP_RED),
            "MENU_FL_40173.png": _sprite(tmp_path, "blood.png", RED),
        },
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    monkeypatch.setattr(paths, "icons_dir", lambda: tmp_path)
    monkeypatch.setattr(relicslots, "_CHIP_CACHE", {})
    return iconpack.IconPack()


def _middle(chip: QPixmap) -> QColor:
    image = chip.toImage()
    return image.pixelColor(image.width() // 2, image.height() // 2)


def test_a_slot_shows_the_light_of_its_colour_and_of_its_kind(pack):
    assert _middle(relicslots.slot_chip(pack, 0)) == RED
    assert _middle(relicslots.slot_chip(pack, 1)) == BLUE
    assert _middle(relicslots.slot_chip(pack, 0, deep=True)) == DEEP_RED


def test_a_slot_without_sprites_keeps_its_colour_as_an_outline(qapp):
    chip = relicslots.slot_chip(None, 3, size=27).toImage()
    middle_of_the_edge = chip.pixelColor(chip.width() // 2, 0)
    assert middle_of_the_edge != chip.pixelColor(chip.width() // 2,
                                                 chip.height() // 2)


def test_a_filled_slot_dims_the_light_and_shows_its_relic(pack):
    relic = types.SimpleNamespace(icon=7)
    white_light_only = relicslots.slot_chip(pack, 1, size=40)
    filled = relicslots.slot_chip(pack, 1, relic, size=40)
    corner = 2
    assert (filled.toImage().pixelColor(corner, 20)
            != white_light_only.toImage().pixelColor(corner, 20))
    assert _middle(filled) == RED


def test_an_inline_symbol_is_an_image_of_that_size(pack):
    tag = pack.inline("status", 20206, 14)
    assert tag.startswith("<img src='file:") and "status.png" in tag
    assert "width='14'" in tag


@pytest.mark.parametrize("group, key", [
    ("status", 1), ("status", None), ("nothing", 20206),
])
def test_no_symbol_is_no_image(pack, group, key):
    assert pack.inline(group, key) == ""
    assert iconpack.inline(None, "status", 20206) == ""


def test_a_manifest_naming_another_place_gets_no_image(pack):
    pack.manifest["status"]["9"] = "..\\..\\secret.png"
    assert pack.inline("status", 9) == ""


@pytest.mark.parametrize("label", ["Blood loss", "Blood Loss"])
def test_both_spellings_of_a_status_find_its_symbol(pack, label):
    assert "blood.png" in iconpack.inline_type(pack, label)


def test_a_type_without_a_symbol_is_no_image(pack):
    assert iconpack.inline_type(pack, "Vigor") == ""
    assert iconpack.type_pixmap(None, "Poison") is None


def test_the_dataset_names_the_symbols_the_game_names(game_data):
    effects = {effect["name"]: effect for effect in game_data["effects"].values()}
    assert effects["Attacks Inflict Poison"]["icon"] == 20980
    assert game_data["deep_of_night"]["sigil_icon"] == 19952
    world = game_data["world_events"]
    assert {buff["icon"] for buff in world["buffs"]} >= {20720, 20726}
    fell_omen = world["drops"]["2130"]
    assert fell_omen and all(drop["icon"] for drop in fell_omen)


def test_an_effect_line_of_a_card_shows_its_symbol_and_keeps_its_text(pack):
    slot = relicslots.RelicSlot(0, False, lambda: None, pack)
    slot.effect_by_id = {5: {"id": 5, "name": "<b>Odd</b>", "icon": 20206,
                             "stacks": True}}
    assert slot._effect_symbol(5) is not None
    assert slot._effect_symbol(6) is None
    relic = types.SimpleNamespace(effect_ids=[5], curse_ids=[])
    assert list(slot.effect_symbols(relic)) == ["<b>Odd</b>"]


def test_a_card_line_with_a_symbol_stays_a_plain_text_label(pack):
    from nrplanner import advisorblock
    from nrplanner.advisor import types as advisor_types

    line = advisor_types.ReasonLine(0, 5, "<b>Odd</b>: +1")
    drawn = advisorblock.BlockLine(line, "<b>Odd</b>", False, lambda *_a: None,
                                   symbol=pack.status(20206))
    plain = advisorblock.BlockLine(line, "<b>Odd</b>", False, lambda *_a: None)
    assert drawn.label.text() == plain.label.text() == "<b>Odd</b>: +1"
    assert len(drawn.findChildren(type(drawn.label))) == len(
        plain.findChildren(type(plain.label))) + 1


def test_game_text_behind_a_symbol_is_escaped(pack, game_data):
    from nrplanner import eventstab

    tab = eventstab.WorldEventsTab(game_data, pack)
    tab.boss_icons["<b>Odd</b>"] = 20206
    pack.manifest["menu"] = {"20206": pack.manifest["status"]["20206"]}
    assert "&lt;b&gt;" in tab._nightlord("<b>Odd</b>")
    assert tab._nightlord("no such boss") == "no such boss"


def test_the_effects_table_keeps_its_text_and_sorts_on_it(pack, game_data):
    from nrplanner import effectstab

    tab = effectstab.EffectsTab(game_data, pack)
    plain = effectstab.EffectsTab(game_data)
    assert (tab.table.item(0, 0).text() == plain.table.item(0, 0).text())
    with_a_symbol = [row for row in range(tab.table.rowCount())
                     if not tab.table.item(row, 0).icon().isNull()]
    assert with_a_symbol
    assert plain.table.item(0, 0).icon().isNull()
    gems = tab._gem_strip((0,))
    assert gems is None, "this pack carries no gem"
    pack.manifest["ui"]["MENU_MenuIcon_40480.png"] = "red.png"
    tab._gem_strips.clear()
    assert tab._gem_strip((0, 4)) is not None


def test_the_gems_in_colours_cost_what_it_does_nothing(qapp):
    """QA-342: the four gems widen `Colours`; `Effect` gives up that room, the
    sentences in `What it does` keep theirs. Widths measured at 125 % on
    Windows (T-340c): `What it does` 477 px at `9cd99ca`, before the gems,
    458 after them; `Colours` 195 px, the window 1931 px of table."""
    from nrplanner import effectstab

    table = effectstab.EffectTable(11)
    table._natural = [0, 53, 48, 64, 195, 82, 91, 93, 159, 125, 0]
    widths = table.column_widths(1931)
    assert widths[10] >= 477
    assert widths[0] > widths[10] and sum(widths.values()) == 1931
