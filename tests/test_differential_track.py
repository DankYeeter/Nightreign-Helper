"""The measuring track has to be trustworthy before its numbers are.

`scripts/differential/` is the strip that produced every acceptance figure
from AD-019 W0 onwards. It was rebuilt from nothing five times and never
committed, so the numbers in those reports could only be checked by building
it a sixth time (QA-075). Now that it is in the repository, the ways it could
lie quietly are what this file pins down:

* a plan whose cases the harness cannot drive would be measuring nothing;
* a comparer that summarised what it could not place would hide the one case
  nobody predicted, which is the whole reason the track exists;
* a mutation whose anchor no longer matches would patch **nothing**, and the
  green suite that followed would read as proof that a guard holds.

The last one is the important one. Every mutation in the registry is held
against the real source here, so a refactoring that moves the line breaks
this test rather than quietly disarming the next mutation run.

The sweep itself is not here and does not belong here: it costs minutes and
needs two trees. See the package docstring for how it is driven.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

from scripts.differential import capture, compare, mutate, plan

from tests import weapon_damage_cases as cases

ROOT = pathlib.Path(__file__).resolve().parents[1]

SMALL_RASTER = {
    "name": "test",
    "hero": "Wylder",
    "level": 15,
    "step": 700,
    "configurations": [
        {
            "name": "alone and active",
            "active": 0,
            "slots": [{"slot": 0, "weapon": "$armament", "tier": 3}],
            "effects": [{"rate": "physicsAttackRate", "count": 2}],
        },
        {
            "name": "beside the starting armament, idle",
            "active": 0,
            "slots": [
                {"slot": 0, "weapon": "@starting", "tier": 3},
                {"slot": 1, "weapon": "$armament", "tier": 3},
            ],
            "effects": [{"attribute": "Strength", "count": 1}],
        },
    ],
}


# --- the plan ---------------------------------------------------------------

def test_a_plan_carries_the_three_numbers_that_make_runs_comparable(game_data):
    """`armaments`, `configurations`, `step` -- the reason for QA-075.

    "38 787 of 25 102" against "10 276 of 19 392" could not be reconciled
    because neither number came with its grid. A plan that lost these would
    put the track straight back there.
    """
    written = plan.build_plan(game_data, SMALL_RASTER)

    assert written["step"] == 700
    assert written["armaments"] == len(
        plan.swept_armaments(game_data, 700))
    assert written["configurations"] == 2
    assert len(written["cases"]) == written["armaments"] * 2
    assert written["dataset"]["data_version"] == \
        game_data.get("meta", {}).get("data_version")


def test_the_step_picks_the_same_armaments_on_any_machine(game_data):
    """Sorted before the step, so `data["weapons"]` order is not a contract."""
    every = plan.swept_armaments(game_data, 1)

    assert every == sorted(every)
    assert plan.swept_armaments(game_data, 700) == every[::700]


def test_every_case_a_plan_writes_is_one_the_harness_can_drive(game_data):
    """The plan speaks the shape `weapon_damage_cases` consumes, or it is a
    second harness written for measuring -- and then the track would no longer
    be measuring the path the golden test replays."""
    written = plan.build_plan(game_data, SMALL_RASTER)

    for case in written["cases"]:
        build = cases.build_for(game_data, case)
        slots = cases.armament_slots(game_data, case)
        assert build is not None
        assert len(slots) == 6


def test_a_raster_query_resolves_to_effects_that_really_move_something(
        game_data):
    """Ids come out of a query, never out of the raster by hand.

    An id written into a raster says nothing about why that effect is in the
    grid, and a gated effect -- most of the ones carrying an attack rate are
    gated -- would move no number at all and make the sweep look sharp while
    measuring a bare armament.
    """
    written = plan.build_plan(game_data, SMALL_RASTER)
    first = written["cases"][0]
    hero = cases.hero_by_name(game_data, "Wylder")

    assert len(first["relic_effects"]) == 2
    for effect_id in first["relic_effects"]:
        effect = cases.effect_by_id(game_data, effect_id)
        alone = cases._alone(game_data, hero, effect)
        assert abs(alone.rates.get("physicsAttackRate", 1.0) - 1.0) > 1e-9


def test_an_unknown_query_is_refused_rather_than_skipped(game_data):
    hero = cases.hero_by_name(game_data, "Wylder")

    with pytest.raises(ValueError, match="unknown effect query"):
        plan._effect_ids(game_data, hero, {"nonsense": "physicsAttackRate"})
    with pytest.raises(ValueError, match="unknown armament reference"):
        plan._weapon_id(game_data, hero, "@whatever", 1)


# --- the comparer -----------------------------------------------------------

def _record(index: int, **fields) -> dict:
    base = {"index": index, "case": f"case {index}",
            "panel": "same", "tiles": ["a", "b"], "last_ar": {}}
    base.update(fields)
    return base


def test_identical_captures_differ_in_nothing():
    both = [_record(0), _record(1)]
    report = compare.compare(both, list(both), set())

    assert (report.compared, report.differing) == (2, 0)
    assert report.unexpected_records == 0


def test_a_moved_field_is_counted_by_name_and_printed_in_full():
    old = [_record(0), _record(1)]
    new = [_record(0), _record(1, panel="moved")]

    report = compare.compare(old, new, set())
    lines = "\n".join(compare.render(report, set(), examples=20))

    assert report.by_field["panel"] == 1
    assert report.unexpected_records == 1
    # The record itself, not only a tally: this is the property W3 rested on.
    assert "case 1" in lines
    assert "'same'" in lines and "'moved'" in lines


def test_an_expected_field_is_still_counted_but_not_dumped():
    """`--expected` means "somebody accounted for this", not "hide it"."""
    old = [_record(0)]
    new = [_record(0, panel="moved")]

    report = compare.compare(old, new, {"panel"})
    lines = "\n".join(compare.render(report, {"panel"}, examples=20))

    assert report.by_field["panel"] == 1
    assert report.differing == 1
    assert report.unexpected_records == 0
    assert "panel: 1 records" in lines and "(expected)" in lines
    assert "'moved'" not in lines


def test_tiles_are_counted_once_per_tile_and_once_per_record():
    """Two different numbers, and a report that gave only one would mislead:
    one record can carry five moved tiles."""
    old = [_record(0, tiles=["a", "b", "c"])]
    new = [_record(0, tiles=["a", "x", "y"])]

    report = compare.compare(old, new, set())

    assert report.by_field["tiles"] == 1
    assert report.tiles_moved == 2


def test_a_field_only_one_side_holds_is_a_difference_not_a_shrug():
    """The union of the field names, never the intersection.

    A capture that grew a field is the most interesting difference there is --
    it is exactly what the tile capture did to the golden harness.
    """
    old = [_record(0)]
    new = [_record(0, breakdown="new text")]

    report = compare.compare(old, new, set())
    lines = "\n".join(compare.render(report, set(), examples=20))

    assert report.by_field["breakdown"] == 1
    assert compare.ABSENT in lines


def test_captures_of_two_different_plans_are_refused():
    with pytest.raises(SystemExit, match="one length"):
        compare.compare([_record(0)], [_record(0), _record(1)], set())
    with pytest.raises(SystemExit, match="do not line up"):
        compare.compare([_record(0)], [_record(0, case="another")], set())


def test_withheld_records_are_announced_rather_than_dropped():
    old = [_record(i) for i in range(5)]
    new = [_record(i, panel="moved") for i in range(5)]

    report = compare.compare(old, new, set())
    lines = "\n".join(compare.render(report, set(), examples=2))

    assert "3 further unexpected records not printed" in lines
    assert "--examples 0" in lines


# --- the mutations ----------------------------------------------------------

@pytest.mark.parametrize("name", sorted(mutate.MUTATIONS))
def test_every_mutation_still_finds_its_anchor_in_the_real_source(name):
    """A mutation that matches nothing patches nothing, and the green suite
    that follows reads as proof that a guard holds. That is the failure this
    whole file exists to prevent, so it is checked against the source itself
    and not against a fixture.
    """
    mutation = mutate.MUTATIONS[name]
    raw = (ROOT / mutation.path).read_bytes()
    newline = mutate.newline_of(raw)
    anchor = mutation.old.encode("utf-8").replace(b"\n", newline)

    assert raw.count(anchor) == 1, (
        f"the anchor of mutation {name!r} occurs {raw.count(anchor)} times in "
        f"{mutation.path}. Update the mutation to the new source; do not "
        f"loosen the anchor, or the next mutation run proves nothing.")
    assert mutation.new != mutation.old
    assert mutation.survival_means.strip()


def _tree_with(tmp_path: pathlib.Path, text: str,
               newline: bytes) -> pathlib.Path:
    target = tmp_path / "nrplanner" / "app.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(text.encode("utf-8").replace(b"\n", newline))
    return tmp_path


@pytest.mark.parametrize("newline", [b"\n", b"\r\n"])
def test_a_mutation_keeps_the_line_endings_the_file_already_had(
        tmp_path, newline):
    """`app.py` is CRLF here and the other modules are LF. A mutation that
    normalised the file would turn every later diff into noise."""
    mutation = mutate.Mutation(
        path="nrplanner/app.py", old="    keep = one\n",
        new="    keep = two\n", survival_means="nothing")
    tree = _tree_with(tmp_path, "head\n    keep = one\ntail\n", newline)

    line, moved = mutate.apply(mutation, tree)
    raw = (tree / "nrplanner" / "app.py").read_bytes()

    assert (line, moved) == (2, 0)
    assert raw == b"head" + newline + b"    keep = two" + newline \
        + b"tail" + newline


def test_an_anchor_that_matches_once_too_often_writes_nothing(tmp_path):
    mutation = mutate.Mutation(
        path="nrplanner/app.py", old="    keep = one\n",
        new="    keep = two\n", survival_means="nothing")
    tree = _tree_with(tmp_path, "    keep = one\n    keep = one\n", b"\n")
    before = (tree / "nrplanner" / "app.py").read_bytes()

    with pytest.raises(SystemExit, match="occurs 2 times"):
        mutate.apply(mutation, tree)

    assert (tree / "nrplanner" / "app.py").read_bytes() == before


def test_an_anchor_that_matches_nothing_writes_nothing(tmp_path):
    mutation = mutate.Mutation(
        path="nrplanner/app.py", old="    gone = one\n",
        new="    gone = two\n", survival_means="nothing")
    tree = _tree_with(tmp_path, "    keep = one\n", b"\n")

    with pytest.raises(SystemExit, match="occurs 0 times"):
        mutate.apply(mutation, tree)


def test_the_checkout_itself_is_never_mutated():
    """A half-restored mutation in a working tree costs more than any
    measurement is worth, so the copy is not a convention but a rule."""
    with pytest.raises(SystemExit, match="checkout this script lives in"):
        mutate.guard_the_own_tree(ROOT)


def test_a_tree_with_its_own_git_is_refused_too(tmp_path):
    """A second clone or `git worktree add` is refused for the same reason as
    the checkout itself (QA-079 b).

    The old guard only compared paths against `ROOT`, so a second clone --
    or a worktree, which is a more direct way back to the unmutated source
    than `git archive HEAD | tar -x` -- was never caught. A `.git` file
    stands in for a worktree's own (it holds a `gitdir:` pointer, not a
    repository), so `.exists()` is used rather than `.is_dir()`.
    """
    (tmp_path / ".git").mkdir()
    with pytest.raises(SystemExit, match=r"\.git"):
        mutate.guard_the_own_tree(tmp_path)


def test_a_plain_extraction_without_git_is_left_alone(tmp_path):
    """The ordinary case -- `git archive HEAD | tar -x` -- is not refused."""
    mutate.guard_the_own_tree(tmp_path)


# --- the capture ------------------------------------------------------------

def test_the_capture_refuses_when_the_interpreter_itself_is_unseeded(
        monkeypatch):
    """Reads `sys.flags.hash_randomization`, not `os.environ` (QA-079 a).

    `PYTHONHASHSEED` only takes effect if it is set before the interpreter
    starts; the environment variable can still be changed afterwards without
    moving anything that already happened. A check that read `os.environ`
    would pass in exactly that state -- the announcement says "fixed" -- while
    set iteration order kept moving, which is measured 2026-09-02: the same
    tree in two processes came back with 5 802 of 11 718 armament tiles
    differing, purely from the hash seed. `sys.flags.hash_randomization` is
    fixed at interpreter start and cannot be forged from Python code after the
    fact, so this test stands in for the forged state with a monkeypatched
    flags object rather than pretending it could reproduce it for real.
    """
    monkeypatch.setenv("PYTHONHASHSEED", "0")  # the announcement says "fixed"

    class Flags:
        hash_randomization = 1  # ...but the interpreter itself was not

    monkeypatch.setattr(capture.sys, "flags", Flags())

    with pytest.raises(SystemExit, match="PYTHONHASHSEED=0"):
        capture.prepare_environment()


def test_use_tree_refuses_a_path_that_did_not_actually_win_the_import(
        tmp_path):
    """`sys.path.insert` is a preference, not a guarantee (QA-079 c).

    Until this test, `use_tree` had no guard test at all in the repository --
    it works (shown by rebuilding the whole differential track by hand
    against a real second tree), but a guard without a test of its own counts
    as unproven here.

    Run in a fresh subprocess rather than in-process: this test process has
    already imported the real `nrplanner`, and `import` caches by name in
    `sys.modules`, so `use_tree`'s own claim -- that it notices when its
    `sys.path.insert` did not win -- could not be exercised against a module
    already sitting in the cache. `tmp_path` holds no `nrplanner` package at
    all, so the import falls through to the real tree on `sys.path`, which is
    exactly the "asked for one tree, got another" case `use_tree` exists to
    catch.
    """
    root = pathlib.Path(__file__).resolve().parents[1]
    script = (
        "import sys, pathlib\n"
        f"sys.path.insert(0, {str(root)!r})\n"
        "from scripts.differential import capture\n"
        f"capture.use_tree(pathlib.Path({str(tmp_path)!r}))\n"
    )
    result = subprocess.run([sys.executable, "-c", script],
                            capture_output=True, text=True)

    assert result.returncode != 0, (
        "use_tree silently accepted an import that came from somewhere "
        f"other than the tree it was asked for.\nstdout: {result.stdout}")
    assert "Nothing captured" in result.stderr
    assert str(tmp_path) in result.stderr


def test_floats_go_out_bit_exact_and_not_through_repr():
    """Rounding hides a one-ULP move, and one ULP is exactly what the
    `sum()`-against-a-loop question in this repository turns on."""
    value = {"final": 0.1 + 0.2, "rates": {"a": 1.0}, "name": "sword"}

    assert capture.hexed(value) == {
        "final": (0.1 + 0.2).hex(),
        "rates": {"a": (1.0).hex()},
        "name": "sword",
    }
    assert capture.hexed(0.1 + 0.2) != capture.hexed(0.3)
