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

import json
import types

import pytest

from nrdata import bossdata, icons

# Marked per test rather than with a module-level pytestmark, because one
# case below (the guard on extracted_game_data itself) needs the game
# installed for nothing -- it never touches installed_game -- and a blanket
# mark would let `pytest -m "not slow"` skip the one guard whose whole job is
# to run on every developer session (QA-220).


@pytest.mark.slow
def test_a_snapshot_can_be_built_from_the_installed_game(extracted_game_data):
    """regulation, BND4, param and paramdef, end to end."""
    for section in ("relics", "effects", "heroes", "vessels", "weapons"):
        assert extracted_game_data.get(section), f"{section} came back empty"


@pytest.mark.slow
def test_the_built_dataset_survives_a_json_round_trip_unchanged(extracted_game_data):
    """One dataset, one shape: `extract.build()` == its own reload (D-001).

    The extractor's result and the same result read back out of
    `nightreign_data.json` used to be two different objects. JSON keys are
    text and nothing else, so a mapping built with `int` keys came back with
    `str` ones, and every consumer had to know which of the two it was
    holding. `model.py` did know and reached for both shapes from the first
    commit on; the tests were written against the file shape and never ran
    without a cached snapshot, so the other shape went uncovered for the
    whole life of the project.

    Asserted as the property, not as the two sites that broke it
    (`heroes[*]["levels"]`, `bosses[*]["weakness"]["parts"]`): any mapping
    added later with a non-text key falls here, and the message names its
    path.
    """
    offenders = []

    def walk(node, path):
        if isinstance(node, dict):
            odd = [key for key in node if not isinstance(key, str)]
            if odd:
                types = sorted({type(key).__name__ for key in odd})
                offenders.append(f"{path}: {len(odd)} of {len(node)} keys are "
                                 f"{'/'.join(types)}, e.g. {odd[0]!r}")
            for key, value in node.items():
                walk(value, f"{path}[{key!r}]")
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, f"{path}[{index}]")

    walk(extracted_game_data, "data")
    assert not offenders, (
        f"{len(offenders)} mappings would be renamed by a JSON round trip:\n"
        + "\n".join(offenders[:10])
    )
    # The contract itself, and it covers more than the keys: a tuple, a set
    # or a NaN on the value side does not come back either, and the walk
    # above says nothing about those.
    assert json.loads(json.dumps(extracted_game_data)) == extracted_game_data


@pytest.mark.slow
def test_the_message_files_supply_the_names(extracted_game_data):
    """FMG. Names come from nothing else, so blank names mean it did not run."""
    named = [relic for relic in extracted_game_data["relics"]
             if str(relic.get("name") or "").strip()]
    assert len(named) > len(extracted_game_data["relics"]) // 2
    # Not one name repeated: a string table read at the wrong offset produces
    # a full list of identical or empty entries, which a count alone accepts.
    assert len({relic["name"] for relic in named}) > 1


@pytest.mark.slow
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


@pytest.mark.slow
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


@pytest.mark.slow
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


def test_extracted_game_data_never_falls_back_to_a_cached_snapshot(
    monkeypatch, tmp_path
):
    """Locks the mechanism T-173 built for QA-220 in place.

    `extracted_game_data` is the one fixture in the suite required to come
    out of `extract.build()` on every developer session with the game
    installed. D-001's bug class -- a mapping that differs from its own JSON
    reload -- only shows on that path; `game_data` hides it behind a
    snapshot whenever `NIGHTREIGN_TEST_SNAPSHOT` or the program's own cache
    is reachable, which on a developer machine it usually is.

    Since D-001's fix, a snapshot and a fresh build carry the same shape, so
    the six cases above cannot tell the two apart any more, and would keep
    passing even if this fixture grew the same snapshot-first fallback
    `game_data` already has -- a plausible "speed it up" change, since
    `game_data` reads like a template for exactly that. Nobody would notice
    until the next bug of the same class outlived another eighteen cycles.

    So this test does not read `extracted_game_data`'s output; it puts a
    snapshot every existing fallback would accept on disk and in the
    environment, replaces `extract.build` with a spy, and calls the
    fixture's own function directly -- bypassing `installed_game`'s skip, so
    this runs on a machine without the game too. The fixture must have
    called the spy and returned exactly what it returned; if it read the
    snapshot instead, neither is true.
    """
    import pathlib

    from nrdata import extract
    from nrplanner import paths
    from tests import conftest

    snapshot_file = tmp_path / "nightreign_data.json"
    snapshot_file.write_text(
        json.dumps({
            "meta": {"extract_version": extract.EXTRACT_VERSION},
            "marker": "from-a-cached-snapshot",
        }),
        encoding="utf-8",
    )
    monkeypatch.setattr(paths, "snapshot_path", lambda: snapshot_file)
    monkeypatch.setenv(conftest.SNAPSHOT_ENV, str(snapshot_file))

    built = {"marker": "from-extract-build"}
    calls = []
    monkeypatch.setattr(
        extract, "build",
        lambda game_dir, defs_dir: calls.append((game_dir, defs_dir)) or built,
    )

    game_dir, defs_dir = pathlib.Path("game"), pathlib.Path("defs")
    result = conftest.extracted_game_data.__wrapped__((game_dir, defs_dir))

    assert calls == [(game_dir, defs_dir)], (
        "extracted_game_data did not call extract.build with the installed "
        "game -- it must have read a snapshot instead"
    )
    assert result is built, (
        "extracted_game_data returned something other than extract.build()'s "
        "own result -- a cached snapshot must have been read instead"
    )


SETTLED = ("single", "group")
CONFIDENCE = {"single", "group", "ambiguous", "unresolved"}


def _map_of(place: str) -> str:
    return f"m{int(place) // 100:02d}_{int(place) % 100:02d}_00_00"


@pytest.mark.slow
def test_the_map_files_supply_the_sub_bosses_by_their_place(
        extracted_game_data):
    """The second entry into the map files: a place, not an event flag.

    The place id *is* a map, which is the whole finding behind this block
    (T-299, QA-286), so every key has to name the map its entry read.
    """
    places = extracted_game_data["subbosses"]
    assert places, "the place roster came back empty"

    for place, entry in places.items():
        assert entry["map"] == _map_of(place), (
            f"place {place} carries {entry['map']}, which is not its own map")
        assert entry["weakness"]["confidence"] in CONFIDENCE
        for drawn in entry["nightlords"]:
            assert 0 < drawn["patterns"] <= drawn["of"], (
                f"place {place} is drawn by {drawn['patterns']} of "
                f"{drawn['of']} patterns of Nightlord {drawn['boss']}")

    resolved = [entry for entry in places.values()
                if entry["weakness"]["confidence"] in SETTLED]
    assert resolved, "no place resolved to a character at all"
    assert all(entry["weakness"]["profile"]["damage"] for entry in resolved)


@pytest.mark.slow
def test_a_place_the_files_do_not_settle_names_nobody(extracted_game_data):
    """GOAL A7. Several boss-scale characters in one place is an answer the
    files do give; which of them the place is for, they do not. So the entry
    lists its candidates and names none of them -- the failure mode QA-286
    is made of is a name that was never in the files.
    """
    for place, entry in extracted_game_data["subbosses"].items():
        confidence = entry["weakness"]["confidence"]
        settled = confidence in SETTLED
        assert (entry["chr"] is not None) is settled, (
            f"place {place} is {confidence} and carries chr {entry['chr']}")
        if not settled:
            assert entry["name"] == "", (
                f"place {place} is {confidence} and still names "
                f"{entry['name']!r}")
        assert bool(entry["candidates"]) is (confidence == "ambiguous")
        if confidence == "ambiguous":
            assert len(entry["candidates"]) > 1, (
                f"place {place} is ambiguous between one character")


@pytest.mark.slow
def test_the_mutation_kinds_list_places_and_not_characters(
        extracted_game_data):
    """QA-286. `smallBaseId` is a place; read as a character it named 21 of
    116 by coincidence and left the other 95 blank."""
    kinds = extracted_game_data["deep_of_night"]["kinds"]
    assert kinds

    for category, kind in kinds.items():
        assert "chrs" not in kind, (
            f"kind {category} still carries the character reading")
        for entry in kind["places"]:
            assert set(entry) == {"place", "map", "rows", "name"}
            assert entry["map"] == _map_of(str(entry["place"]))

    named = [entry for kind in kinds.values() for entry in kind["places"]
             if entry["name"]]
    assert named, "no place carries the name of the boss standing in it"


def _npc_row(row_id: int, hp: int, spread: float):
    """An NpcParam row as `bossdata._profile` reads one."""
    values = {field: 1.0 for field in bossdata.DAMAGE_FIELDS}
    values["neutralDamageCutRate"] = 1.0 + spread
    values["hp"] = hp
    return types.SimpleNamespace(id=row_id, values=values)


def test_both_boss_bars_have_to_be_cleared_to_be_a_candidate():
    """The rule both entries into a map share, on its own.

    A map is full of props and adds, and the two bars are what tell a boss
    from them: resistances someone tuned, and boss-scale HP. Lowering either
    one silently turns a shopkeeper into a sub-boss, which is why this is
    checked here and not only through a dataset.
    """
    from nrdata import bossdata

    boss = {2130: [_npc_row(21300030, 2500, 0.2)]}
    assert [chr_id for chr_id, _p in bossdata._candidates(boss, {2130: 1})[0]] \
        == [2130]

    flat = {4000: [_npc_row(40000010, 2500, 0.0)]}
    assert bossdata._candidates(flat, {4000: 1}) == ([], False)

    small = {4001: [_npc_row(40010010, 1900, 0.2)]}
    assert bossdata._candidates(small, {4001: 1}) == ([], False)

    # Nothing clears the HP bar, but one tuned character fills the map: the
    # group rule answers, and says so.
    found, group = bossdata._candidates(small, {4001: 12})
    assert group and [chr_id for chr_id, _p in found] == [4001]


def test_more_than_one_boss_scale_character_is_left_for_the_caller():
    """`_candidates` hands back both; `derive` takes the larger, and
    `derive_places` refuses to pick (A7). The refusal is only possible if
    the rule itself keeps every candidate."""
    two = {2130: [_npc_row(21300030, 2500, 0.2)],
           4501: [_npc_row(45010000, 5753, 0.3)]}
    found, group = bossdata._candidates(two, {2130: 1, 4501: 1})

    assert not group
    assert sorted(chr_id for chr_id, _p in found) == [2130, 4501]
