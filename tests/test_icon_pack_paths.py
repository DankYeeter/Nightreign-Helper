"""A file name in manifest.json cannot point the program at another folder.

SEC-008. The icon pack is an ordinary folder of ordinary files, so anything
that can write manifest.json chooses which paths this program opens. Joined
straight onto the pack folder, "../evil.png" climbs out of it and an absolute
path leaves it without even looking like it did -- joining an absolute path
onto a folder discards the folder.

Every file planted outside the pack here is a real, loadable image. That is
the point: if containment were missing, the load would succeed, so a passing
test means the path was refused rather than merely not found.
"""

from __future__ import annotations

import json

import pytest

from nrplanner import iconpack


@pytest.fixture
def planted_pack(tmp_path, qapp, monkeypatch):
    """An icon pack whose manifest names two files outside itself, and one in.

    Returns (pack, the file outside, its bytes before the pack was read).
    """
    from PySide6.QtGui import QPixmap

    pack_dir = tmp_path / "pack"
    pack_dir.mkdir()
    outside = tmp_path / "outside" / "evil.png"
    outside.parent.mkdir()

    image = QPixmap(2, 2)
    image.fill()
    assert image.save(str(outside), "PNG"), "the test needs a loadable image"
    assert image.save(str(pack_dir / "good.png"), "PNG")

    (pack_dir / "manifest.json").write_text(json.dumps({
        "portraits": {"1": "../outside/evil.png", "2": "good.png"},
        "items": {"3": str(outside), "4": "good.png"},
        "variants": {},
        "menu": {"5": "..\\outside\\evil.png"},
        "ui": {"sprite": "../outside/evil.png", "ok": "good.png"},
    }), encoding="utf-8")

    monkeypatch.setattr(iconpack.IconPack, "locate",
                        staticmethod(lambda: pack_dir))
    return iconpack.IconPack(), outside, outside.read_bytes()


def test_a_relative_climb_out_of_the_pack_is_refused(planted_pack):
    pack, _outside, _before = planted_pack
    assert pack.portrait(1) is None
    assert pack.menu(5) is None


def test_an_absolute_path_in_the_manifest_is_refused(planted_pack):
    pack, _outside, _before = planted_pack
    assert pack.item(3) is None


def test_a_ui_sprite_outside_the_pack_is_refused(planted_pack):
    # This one is handed to rich text as a file:// source, so a path that got
    # through would be fetched by the label rather than by this code.
    pack, _outside, _before = planted_pack
    assert pack.ui_path("sprite") is None


def test_the_file_outside_the_pack_is_left_exactly_as_it_was(planted_pack):
    pack, outside, before = planted_pack
    pack.portrait(1)
    pack.item(3)
    pack.menu(5)
    pack.ui_path("sprite")
    assert outside.exists() and outside.read_bytes() == before


def test_files_inside_the_pack_still_load(planted_pack):
    """The containment check must not be a way of loading nothing at all."""
    pack, _outside, _before = planted_pack
    assert pack.portrait(2) is not None
    assert pack.item(4) is not None
    assert pack.ui_path("ok") is not None
