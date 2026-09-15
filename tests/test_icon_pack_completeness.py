"""A manifest is a promise, and the launch checks that it is kept (QA-036).

On a real machine the installed pack held 105 of the 839 files its manifest
named, `what_is_needed()` said nothing and the program came up with blank
portraits. Two halves: the check at launch walks the manifest against the
files, and the builder writes the manifest so that no half-written one can
ever be the file that check reads.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from nrdata import iconbuild
from nrplanner import firstrun
from nrplanner.iconpack import IconPack

#: One entry of each shape the manifest has: id -> file, and the variants'
#: hero -> [{"id", "file"}].
MANIFEST = {
    "portraits": {"1": "hero_1.png"},
    "items": {"200": "item_200.png"},
    "variants": {"1": [{"id": 49000, "file": "variant_49000.png"}]},
    "menu": {},
    "ui": {"ui_slot": "ui_slot.png"},
    "icon_version": iconbuild.ICON_VERSION,
}
PROMISED = ["hero_1.png", "item_200.png", "variant_49000.png", "ui_slot.png"]


@pytest.fixture
def pack(tmp_path, monkeypatch) -> pathlib.Path:
    """A pack folder the launch check looks at, with a current manifest."""
    (tmp_path / "manifest.json").write_text(json.dumps(MANIFEST))
    monkeypatch.setattr(IconPack, "locate", staticmethod(lambda: tmp_path))
    # Not under test here: a snapshot that is missing is simply reported.
    monkeypatch.setattr(firstrun, "bundled_path",
                        lambda: tmp_path / "no-snapshot.json")
    return tmp_path


def test_the_manifest_walk_names_every_file_of_both_shapes():
    assert sorted(iconbuild.manifest_files(MANIFEST)) == sorted(PROMISED)


def test_a_pack_with_every_promised_file_is_not_rebuilt(pack):
    for name in PROMISED:
        (pack / name).write_bytes(b"png")
    assert "icons" not in firstrun.what_is_needed(pack)


@pytest.mark.parametrize("gone", PROMISED)
def test_a_pack_missing_one_promised_file_is_rebuilt(pack, gone):
    for name in PROMISED:
        if name != gone:
            (pack / name).write_bytes(b"png")
    assert "icons" in firstrun.what_is_needed(pack)


def test_a_manifest_write_that_breaks_off_leaves_the_old_one_whole(
        tmp_path, monkeypatch):
    """Half a manifest is worse than an old one: it names files as present
    that the check above then finds, and drops the rest without a word."""
    target = tmp_path / iconbuild.MANIFEST_NAME
    target.write_text(json.dumps(MANIFEST))

    def breaks_off(self, text, *args, **kwargs):
        pathlib.Path.write_bytes(self, text[: len(text) // 2].encode())
        raise OSError("disk full")

    monkeypatch.setattr(pathlib.Path, "write_text", breaks_off)
    with pytest.raises(OSError):
        iconbuild.write_manifest({"portraits": {"9": "x.png"}}, tmp_path)

    assert json.loads(target.read_text()) == MANIFEST


# -- a manifest is untrusted input (SEC-047) ----------------------------------
#
# The launch check walks manifest.json, an ordinary file anything running as
# the player can write. An entry of the wrong shape is skipped by the walk,
# and a manifest of the wrong shape altogether is a rebuild rather than a
# crash on launch.

def test_the_walk_skips_a_variant_without_a_file_or_with_a_non_string():
    manifest = {**MANIFEST, "variants": {"1": [
        {"id": 1}, {"id": 2, "file": 3}, {"id": 3, "file": None},
        {"id": 4, "file": "variant_4.png"}, "not a dict"]}}
    assert sorted(iconbuild.manifest_files(manifest)) == sorted(
        ["hero_1.png", "item_200.png", "ui_slot.png", "variant_4.png"])


@pytest.mark.parametrize("shape", ["[]", "\"text\"", "42",
                                   '{"variants": {"1": [{"id": 1}]}}'])
def test_a_manifest_of_the_wrong_shape_is_a_rebuild_not_a_crash(pack, shape):
    (pack / "manifest.json").write_text(shape)
    assert "icons" in firstrun.what_is_needed(pack)
