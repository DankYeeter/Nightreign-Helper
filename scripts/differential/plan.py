"""Expand a raster file into the concrete cases a differential run replays.

Developer tool. See `scripts/differential/__init__.py` for the whole track.

    python scripts/differential/plan.py RASTER.json -o PLAN.json

The raster says what *kind* of case is wanted -- "every armament, at tier 3,
under two effects that measurably move the physical attack rate". This script
answers each of those descriptions against the dataset once and writes the
ids it landed on into the plan, together with the counts that make one run
comparable to another.

The cases come out in the shape `tests.weapon_damage_cases.run` consumes, so
the track drives the calculation down the same path the golden test drives it
down, rather than down a second one written for measuring.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]

SWEPT = "$armament"

#: What a weapon reference in a raster may say, beside `SWEPT`.
NAMED_WEAPON_PREFIXES = ("@starting", "@first:", "@heaviest:")


def _weapon_id(data: dict, hero: dict, reference: str, swept: int) -> int:
    """The armament one raster entry names.

    Every form but `$armament` is a query against the dataset, for the same
    reason `tests/weapon_damage_cases.py` gives: an id written into a raster
    by hand says nothing about why that armament is in the grid, and a game
    patch could move it without anyone noticing.
    """
    from tests import weapon_damage_cases as cases

    if reference == SWEPT:
        return swept
    if reference == "@starting":
        return hero["starting_weapon"]
    if reference.startswith("@first:"):
        return cases.first_of_family(data, reference[len("@first:"):])
    if reference.startswith("@heaviest:"):
        return cases.heaviest_of_family(data, reference[len("@heaviest:"):])
    raise ValueError(
        f"unknown armament reference {reference!r}: expected {SWEPT!r} or one "
        f"of {NAMED_WEAPON_PREFIXES}")


def _effect_ids(data: dict, hero: dict, query: dict) -> list[int]:
    """The effects one raster query asks for, resolved against the dataset."""
    from tests import weapon_damage_cases as cases

    count = int(query.get("count", 1))
    if "rate" in query:
        return cases.effects_raising_rate(data, hero, query["rate"], count)
    if "attribute" in query:
        return cases.effects_raising_attribute(
            data, hero, query["attribute"], count)
    if "scoped" in query:
        return [cases.scoped_effect(data, hero, query["scoped"])]
    raise ValueError(
        f"unknown effect query {query!r}: expected one of 'rate', "
        f"'attribute', 'scoped'")


def swept_armaments(data: dict, step: int) -> list[int]:
    """Every `step`-th armament id, lowest first.

    Sorted before the step is taken, so `step` picks the same armaments on any
    machine -- the order `data["weapons"]` arrives in is not part of the
    contract.
    """
    if step < 1:
        raise ValueError(f"step must be at least 1, not {step}")
    return sorted(w["id"] for w in data["weapons"])[::step]


def _arsenal(data: dict, hero: dict, configuration: dict,
             swept: int) -> dict | None:
    """The arsenal-tab reading one configuration asks for, if it asks.

    Every control the reading depends on is named in the raster and none of
    them has a default here. The target tier above all: it is the tab's own
    question and a default would put the slot's tier back silently (AD-020,
    point 1, and `damage.rank_candidates` takes it without one for the same
    reason).
    """
    request = configuration.get("arsenal")
    if request is None:
        return None
    missing = {"weapon", "tier", "rarity"} - set(request)
    if missing:
        raise ValueError(
            f"the arsenal block of configuration {configuration['name']!r} "
            f"leaves {sorted(missing)} unsaid. Each of them moves the figures "
            f"the tab shows, so a run that guessed one would not be "
            f"comparable to a run that guessed it differently.")
    return {
        "weapon": _weapon_id(data, hero, request["weapon"], swept),
        "tier": int(request["tier"]),
        "rarity": int(request["rarity"]),
    }


def _case(data: dict, hero: dict, raster: dict, configuration: dict,
          swept: int) -> dict:
    """One configuration applied to one swept armament."""
    armaments = [
        {
            "slot": int(entry["slot"]),
            "weapon": _weapon_id(data, hero, entry["weapon"], swept),
            "tier": int(entry["tier"]),
            "effects": list(entry.get("effects", [])),
        }
        for entry in configuration["slots"]
    ]
    relic_effects: list[int] = []
    for query in configuration.get("effects", []):
        relic_effects.extend(_effect_ids(data, hero, query))
    case = {
        "name": f"{configuration['name']} :: armament {swept}",
        "hero": raster["hero"],
        "level": int(raster["level"]),
        "active": int(configuration["active"]),
        "armaments": armaments,
        "relic_effects": relic_effects,
        "curse_effects": [],
        "declared": {},
    }
    arsenal = _arsenal(data, hero, configuration, swept)
    if arsenal is not None:
        case["arsenal"] = arsenal
    return case


def build_plan(data: dict, raster: dict, step: int | None = None) -> dict:
    """The raster, expanded. The counts in the header are the point of it."""
    from tests import weapon_damage_cases as cases

    hero = cases.hero_by_name(data, raster["hero"])
    step = int(raster.get("step", 1) if step is None else step)
    swept = swept_armaments(data, step)
    configurations = raster["configurations"]
    if not configurations:
        raise ValueError("a raster with no configurations measures nothing")

    entries = [_case(data, hero, raster, configuration, armament)
               for armament in swept
               for configuration in configurations]
    meta = data.get("meta", {})
    return {
        "raster": raster["name"],
        "why": raster.get("why", ""),
        "dataset": {
            "data_version": meta.get("data_version"),
            "extract_version": meta.get("extract_version"),
            "regulation_sha256": meta.get("regulation_sha256"),
        },
        # The three numbers a report has to be able to quote. Without them
        # "38 787 of 25 102" cannot be held against any other run (QA-075).
        "step": step,
        "armaments": len(swept),
        "configurations": len(configurations),
        "cases": entries,
    }


def load_data() -> dict:
    """The dataset, exactly as `scripts/capture_weapon_damage.py` takes it."""
    import os

    from nrplanner import datasource, model, paths

    raw = os.environ.get("NIGHTREIGN_TEST_SNAPSHOT")
    if raw:
        data = json.loads(pathlib.Path(raw).read_text(encoding="utf-8"))
    elif paths.snapshot_path().is_file():
        data = json.loads(paths.snapshot_path().read_text(encoding="utf-8"))
    else:
        data = datasource.load_data()
    model.configure(data)
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("raster", type=pathlib.Path,
                        help="the raster file to expand")
    parser.add_argument("-o", "--out", type=pathlib.Path, required=True,
                        help="where to write the plan")
    parser.add_argument("--step", type=int, default=None,
                        help="take every N-th armament instead of the "
                             "raster's own step, for a smoke run. The plan "
                             "records the step it really used, so a figure "
                             "quoted from it still carries its grid.")
    args = parser.parse_args(argv)

    sys.path.insert(0, str(ROOT))
    raster = json.loads(args.raster.read_text(encoding="utf-8"))
    plan = build_plan(load_data(), raster, args.step)
    args.out.write_text(
        json.dumps(plan, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")
    print(f"raster {plan['raster']!r}: {plan['armaments']} armaments "
          f"(every {plan['step']}) x {plan['configurations']} configurations "
          f"= {len(plan['cases'])} cases -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
