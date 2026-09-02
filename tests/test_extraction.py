"""The container parsers are run against the game, not around it.

DEBT-001. Every other data-backed test takes `game_data`, which uses the
snapshot the program has already cached when there is one. That is the right
trade for a test that only needs a dataset to compute on -- and it meant that
in a green run `fmg`, `bnd4`, `dvdbnd`, `tpf` and `tae` were never executed.
All five read bytes that come out of a file rather than out of this program,
which is where every parser finding so far has been, so a change to any of
them looked tested without being tested.

These cases force the read. They are marked `slow` and they skip themselves
where there is no installation, so a runner without the game stays green and
green means something different there than it does here -- deliberately. The
developer run is the one that covers this. To leave them out:

    pytest -m "not slow"

What is asserted is deliberately shallow. This is not a test of what the game
contains -- that changes with every patch and is not ours to pin -- but of
whether the readers get through real containers and come back with something
that is recognisably the thing they were asked for.
"""

from __future__ import annotations

import pytest

from nrdata import icons

pytestmark = pytest.mark.slow


def test_a_snapshot_can_be_built_from_the_installed_game(extracted_game_data):
    """regulation, BND4, param and paramdef, end to end."""
    for section in ("relics", "effects", "heroes", "vessels", "weapons"):
        assert extracted_game_data.get(section), f"{section} came back empty"


def test_the_message_files_supply_the_names(extracted_game_data):
    """FMG. Names come from nothing else, so blank names mean it did not run."""
    named = [relic for relic in extracted_game_data["relics"]
             if str(relic.get("name") or "").strip()]
    assert len(named) > len(extracted_game_data["relics"]) // 2
    # Not one name repeated: a string table read at the wrong offset produces
    # a full list of identical or empty entries, which a count alone accepts.
    assert len({relic["name"] for relic in named}) > 1


def test_the_archives_supply_the_boss_resistances(extracted_game_data):
    """dvdbnd, Oodle, the event scripts and the map part names (SEC-014).

    The part name is what identifies the character behind a boss, so a boss
    with a resistance profile is a part name that was read and terminated.
    """
    profiled = [boss for boss in extracted_game_data["bosses"]
                if (boss.get("weakness") or {}).get("profile")]
    assert profiled, "no boss resolved to an NpcParam row"
    assert all(profile["damage"]
               for profile in (boss["weakness"]["profile"]
                               for boss in profiled))


def test_the_animation_files_supply_the_buff_ladders(extracted_game_data):
    """TAE. A ladder with a `from` came off an animation and nowhere else."""
    located = [
        entry
        for boss in extracted_game_data["bosses"]
        for entry in ((((boss.get("weakness") or {}).get("profile") or {})
                       .get("ladder") or {}).get("up") or [])
        if entry.get("from")
    ]
    assert located, "no self-buff was traced to an animation"


def test_a_real_icon_can_be_cut_out_of_a_real_atlas(installed_game):
    """TPF, the DDS decoder with its new size check, and the layout reader.

    The icon pack path is the one `extract.build` does not touch, and it is
    where SEC-005 and SEC-010 live: a texture whose payload is measured
    against the image its header claims, and a layout parsed without letting
    the document declare entities. If either check were wrong for a file the
    game actually ships, this is where it shows.
    """
    pytest.importorskip("PIL", reason="Pillow is needed to crop an atlas")
    game, _defs = installed_game
    source = icons.IconSource(game)
    try:
        assert source.sprites, "no sprite rectangles came out of the layouts"
        sprite_name = next(iter(source.sprites))
        cut = source.crop(sprite_name)
        assert cut is not None
        assert cut.size == (source.sprites[sprite_name].width,
                            source.sprites[sprite_name].height)
    finally:
        source.release()
