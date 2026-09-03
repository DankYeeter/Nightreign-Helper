"""Run one plan against one tree and write down what the displays say.

Developer tool. See `scripts/differential/__init__.py` for the whole track.

    PYTHONHASHSEED=0 python scripts/differential/capture.py PLAN.json \\
        -o RECORDS.jsonl [--tree DIR]

One JSON object per line, so a sweep over every armament can be written and
read without holding the whole thing in memory, and so `wc -l` on the output
is the case count.

`--tree` moves **`nrplanner`** and nothing else. The harness that drives it
(`tests/weapon_damage_cases.py`) is always taken from the checkout this
script lives in, by file path: it is the measuring instrument, and two
captures taken with two different instruments cannot be held against each
other. That is also why the header line prints both paths.

Three things this refuses to do rather than produce a number that looks fine:

* run without `PYTHONHASHSEED=0` -- set iteration order reaches the rendered
  text, and the same tree in two processes then disagrees with itself;
* run against a tree it did not actually import from -- `--tree` only puts a
  path in front of `sys.path`, and an already-imported package would win;
* write floats through `repr` -- `last_ar` goes out as `float.hex()`, so a
  comparison is exact and a one-ULP change cannot hide behind rounding.

The game is only ever read.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]

HARNESS_MODULE = "differential_harness"


def hexed(value):
    """Floats as `float.hex()`, so a diff is bit-exact and not eyeballed."""
    if isinstance(value, dict):
        return {key: hexed(item) for key, item in value.items()}
    if isinstance(value, list):
        return [hexed(item) for item in value]
    if isinstance(value, float):
        return value.hex()
    return value


def prepare_environment() -> None:
    """Everything that has to be true before PySide6 is imported."""
    if os.environ.get("PYTHONHASHSEED") != "0":
        raise SystemExit(
            "refusing to capture without PYTHONHASHSEED=0. Set iteration "
            "order reaches the rendered text: the same tree in two processes "
            "came back with 5 802 of 11 718 armament tiles differing, purely "
            "from the hash seed (measured 2026-09-02). A run without it "
            "produces a plausible number that means nothing.")
    # No display is available and none is needed.
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    # A real Planner stores what it is holding. Without these it would write
    # into the player's own settings.
    os.environ.setdefault("NIGHTREIGN_SETTINGS_ORG", "DankYeeterTests")
    os.environ.setdefault(
        "NIGHTREIGN_SETTINGS_APP",
        f"NightreignHelperDifferential-{os.getpid()}")


def use_tree(tree: pathlib.Path):
    """Import `nrplanner` from `tree`, or fail loudly. Hands back the module.

    `sys.path.insert` is a preference, not a guarantee. A capture that
    silently measured the wrong tree would report "no difference" for a change
    that is really there, which is the one answer this track must never give
    by accident.
    """
    sys.path.insert(0, str(tree))
    import nrplanner

    imported = pathlib.Path(nrplanner.__file__).resolve().parents[1]
    if imported != tree:
        raise SystemExit(
            f"asked for the tree at {tree}, but `nrplanner` came from "
            f"{imported}. Nothing captured.")
    return nrplanner


def load_harness(root: pathlib.Path):
    """`tests/weapon_damage_cases.py` from this checkout, by file path.

    Loaded by path rather than imported, so that `--tree` cannot drag the
    harness along with the package under test. Its own `from nrplanner
    import ...` still resolves to the tree, which is the point: same
    instrument, different subject.
    """
    path = root / "tests" / "weapon_damage_cases.py"
    spec = importlib.util.spec_from_file_location(HARNESS_MODULE, path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"no harness to drive the cases with at {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[HARNESS_MODULE] = module
    spec.loader.exec_module(module)
    return module


def records(planner, data: dict, plan: dict, harness):
    """One record per case: the three display layers, side by side."""
    for index, case in enumerate(plan["cases"]):
        shown = harness.run(planner, data, case)
        # `run` rounds `last_ar` to six decimals for the golden file's sake.
        # Here the exact bits are wanted, so they are read off the planner
        # again -- rounding cannot be undone.
        shown["last_ar"] = hexed(planner.last_ar)
        yield {"index": index, "case": case["name"], **shown}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("plan", type=pathlib.Path,
                        help="a plan written by plan.py")
    parser.add_argument("-o", "--out", type=pathlib.Path, required=True,
                        help="where to write the records, one JSON per line")
    parser.add_argument("--tree", type=pathlib.Path, default=None,
                        help="the tree to take `nrplanner` from "
                             "(default: this one)")
    args = parser.parse_args(argv)

    prepare_environment()
    sys.path.insert(0, str(ROOT))
    from scripts.differential import plan as planmod

    tree = (args.tree or ROOT).resolve()
    use_tree(tree)
    harness = load_harness(ROOT)

    from PySide6.QtWidgets import QApplication

    from nrplanner import app as appmod

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    data = planmod.load_data()
    meta = data.get("meta", {})
    if meta.get("data_version") != plan["dataset"].get("data_version"):
        raise SystemExit(
            f"the plan was made from game data "
            f"{plan['dataset'].get('data_version')}, this machine has "
            f"{meta.get('data_version')}. Re-run plan.py first: ids resolved "
            f"against another version are not the same question.")

    print(f"nrplanner from {tree}", flush=True)
    print(f"harness   from {ROOT / 'tests' / 'weapon_damage_cases.py'}",
          flush=True)

    qapp = QApplication.instance() or QApplication([])
    planner = appmod.Planner(data)
    written = 0
    with args.out.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records(planner, data, plan, harness):
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            written += 1
            if written % 2000 == 0:
                print(f"  {written} of {len(plan['cases'])}", flush=True)
    planner.close()
    del qapp

    print(f"{written} records -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
