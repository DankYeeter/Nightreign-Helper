"""How many armaments the display thresholds hide, and what moving them would do.

Developer tool, and the recipe behind the figures QA-117/AK-65 are argued
with. `UI_SPEC.md` AK-65 decides that `app.VISIBLE_CHANGE` stays an absolute
half-unit of the screen rather than following the 0.6 calibration factor. The
decision is only as good as the size of what it decides, so this counts it
rather than estimating it.

    python scripts/measure_display_thresholds.py
    python scripts/measure_display_thresholds.py --hero Recluse --level 12

What is counted, per armament of the offered arsenal at one tier, for one
Nightfarer at one level wearing one attribute-raising effect:

    d = scaled_headline(with the effect) - scaled_headline(bare)

`d` is what the panel's `From attributes` row prints, and the row appears
only while `abs(d) >= VISIBLE_CHANGE`. Three counts follow from it, and each
answers a different question that has been asked about this threshold:

* **hidden**            -- `0 < d < VISIBLE_CHANGE`: armaments whose row is
                           not on screen today.
* **hidden by the 0.6** -- of those, the ones whose pre-calibration figure
                           (`d / GAME_ATTACK_POWER_RATE`) would have cleared
                           the threshold. This is QA-117's "89 rows fell
                           away" for this population.
* **lost if raised**    -- `VISIBLE_CHANGE <= d < VISIBLE_CHANGE / rate`:
                           rows on screen today that raising the threshold to
                           keep "the same cases as before" would take away.
* **gained if lowered** -- `VISIBLE_CHANGE * rate <= d < VISIBLE_CHANGE`:
                           rows that multiplying the threshold by the factor
                           would add.

The last two are the two directions AK-65 rules out, counted so the ruling
can be read as a size rather than as a preference.

The dataset comes from the snapshot the program built for itself, or from a
fresh read of the installed game. The game is only ever read.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# No display is available and none is needed; `nrplanner.app` imports Qt.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def load_data() -> dict:
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


def from_attributes(data: dict, weapon: dict, tier: int, bare_build,
                    raised_build) -> float:
    """What the `From attributes` row would print for this armament."""
    from nrplanner import damage

    bare = damage.candidate(weapon, tier, bare_build, data)
    raised = damage.candidate(weapon, tier, raised_build, data)
    return raised.scaled_headline - bare.scaled_headline


def measure(data: dict, hero_name: str, level: int, tier: int,
            effect_id: int | None) -> dict:
    from nrplanner import app as appmod
    from nrplanner import model
    from nrplanner.weapons import GAME_ATTACK_POWER_RATE

    hero = next(h for h in data["heroes"] if h["name"] == hero_name)
    curves = data.get("curves", {})
    if effect_id is None:
        effect_id = _an_attribute_effect(data, hero, level)
    effect = data["effects"][str(effect_id)]

    bare_build = model.compute(hero, level, [], curves)
    raised_build = model.compute(hero, level, [effect], curves)

    visible = appmod.VISIBLE_CHANGE
    raised_threshold = visible / GAME_ATTACK_POWER_RATE
    lowered_threshold = visible * GAME_ATTACK_POWER_RATE

    counts = dict.fromkeys(
        ("armaments", "moves", "hidden", "hidden_by_the_calibration",
         "lost_if_raised", "gained_if_lowered"), 0)
    for weapon in model.offerable_weapons(data["weapons"]):
        counts["armaments"] += 1
        gap = abs(from_attributes(data, weapon, tier, bare_build,
                                  raised_build))
        if gap == 0.0:
            continue
        counts["moves"] += 1
        if gap < visible:
            counts["hidden"] += 1
            if gap / GAME_ATTACK_POWER_RATE >= visible:
                counts["hidden_by_the_calibration"] += 1
            if gap >= lowered_threshold:
                counts["gained_if_lowered"] += 1
        elif gap < raised_threshold:
            counts["lost_if_raised"] += 1

    counts["effect"] = " ".join(effect["name"].split())
    counts["effect_id"] = effect_id
    return counts


def _an_attribute_effect(data: dict, hero: dict, level: int) -> int:
    """The lowest-id effect that raises an attribute this build scales on.

    Chosen by asking `model.compute` what each effect does, so the population
    below stands on a relic that really moves an armament rather than on an
    id written down here.
    """
    from nrplanner import model

    curves = data.get("curves", {})
    base = model.compute(hero, level, [], curves)
    for effect_id in sorted(data["effects"], key=int):
        effect = data["effects"][effect_id]
        build = model.compute(hero, level, [effect], curves)
        if build.attributes != base.attributes:
            return int(effect_id)
    raise SystemExit("no effect in this dataset raises an attribute")


def main(argv: list[str] | None = None) -> int:
    from nrplanner import app as appmod
    from nrplanner.weapons import GAME_ATTACK_POWER_RATE, MIN_UPGRADE

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--hero", default="Wylder")
    parser.add_argument("--level", type=int, default=15)
    parser.add_argument("--tier", type=int, default=MIN_UPGRADE)
    parser.add_argument("--effect", type=int, default=None,
                        help="effect id to wear; the default is searched for")
    args = parser.parse_args(argv)

    data = load_data()
    counts = measure(data, args.hero, args.level, args.tier, args.effect)

    print(f"{args.hero} at level {args.level}, tier +{args.tier}, "
          f"wearing {counts['effect']!r} ({counts['effect_id']})")
    print(f"  threshold        {appmod.VISIBLE_CHANGE} "
          f"(absolute, AK-65); calibration "
          f"{GAME_ATTACK_POWER_RATE}")
    print(f"  armaments        {counts['armaments']}")
    print(f"  row would move   {counts['moves']}")
    print(f"  hidden today     {counts['hidden']}")
    print(f"  of those, hidden by the calibration alone "
          f"{counts['hidden_by_the_calibration']}")
    print(f"  lost if the threshold were raised to "
          f"{appmod.VISIBLE_CHANGE / GAME_ATTACK_POWER_RATE:.4f}: "
          f"{counts['lost_if_raised']}")
    print(f"  gained if it were lowered to "
          f"{appmod.VISIBLE_CHANGE * GAME_ATTACK_POWER_RATE:.4f}: "
          f"{counts['gained_if_lowered']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
