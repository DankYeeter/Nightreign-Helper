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
