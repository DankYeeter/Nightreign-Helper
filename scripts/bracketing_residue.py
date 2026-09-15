"""Where the game's constant is applied, and what it costs in last bits.

Developer tool, run by hand. It answers one question and no other: of the two
places `weapons.rate` could apply `GAME_ATTACK_POWER_RATE`, which one keeps
every per-type figure a rounding of the figure the program showed before the
constant existed?

    python scripts/bracketing_residue.py
    python scripts/bracketing_residue.py --step 50        # a smoke run

The two brackets, written out because the whole difference is where one pair
of parentheses sits:

    on the finished figure     scaled = fl(fl(base * bonus) * K)   (shipped)
    on the base beforehand     scaled = fl(fl(base * K) * bonus)

and the yardstick is `fl(old * K)`, where `old = fl(base * bonus)` is what
the figure was before T-045 put the constant in. The first bracket **is**
that expression, so its residue is zero by construction, and saying so is
the point: the number worth reporting is the second one's.

**Why this exists.** The comment beside `result.scaled` in
`nrplanner/weapons.py` justified the bracketing with a measurement -- "574 of
350 160 come out 2 ULP from 0.6 instead of 1" -- taken with a script called
`dump_rate.py` that was never committed. A number in the source that the next
reader cannot re-run is not a justification, it is a claim (QA-115, house rule
L-001). This is that script, and the comment now names it and carries what it
actually prints.

**It re-derives the arithmetic rather than calling `weapons.rate` twice**, and
it has to: the two brackets differ only inside that function, and the two
ingredients -- the reinforced base and the scaling bonus -- are not
recoverable from its output without a division that would round again. An
independent re-derivation can drift from the thing it is measuring, so it is
held against it: for every figure, the shipped bracket computed here must
equal `weapons.rate`'s own output **bit for bit**, and the run fails if a
single one does not. A number about arithmetic that is no longer the
program's would be worse than no number.
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import struct
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from nrplanner import model, weapons  # noqa: E402
from scripts.differential.plan import load_data  # noqa: E402

#: The levels the sheet is read at elsewhere in this repository: the floor,
#: the middle of the ladder and the top. Written out rather than swept,
#: because what is being counted is a rounding residue and it does not grow
#: more informative with more levels -- it grows only longer.
LEVELS = (1, 12, 15)

#: Every rarity the reinforce table has a row for.
TIERS = tuple(range(weapons.MIN_UPGRADE, weapons.MAX_UPGRADE + 1))


def ordinal(value: float) -> int:
    """The rank of a double among the doubles, so a gap can be counted.

    Two adjacent doubles differ by one here whatever their exponent, which is
    what "1 ULP" has to mean if the count is to hold across the whole range
    of attack ratings. Negative zero maps onto zero, and no figure below is
    a NaN.
    """
    bits = struct.unpack("<q", struct.pack("<d", value))[0]
    return bits if bits >= 0 else -(bits & 0x7FFFFFFFFFFFFFFF)


def ulps_apart(a: float, b: float) -> int:
    return abs(ordinal(a) - ordinal(b))


def ingredients(weapon: dict, attributes: dict, data: dict,
                upgrade: int) -> dict[str, tuple[float, float]]:
    """`(reinforced base, scaling bonus)` per damage type, before the constant.

    The same steps `weapons.rate` takes, up to but not including the two
    lines that write into the rating. The loop over the scaling attributes is
    written out as a running sum rather than as `sum()` for the reason stated
    in `weapons.rate`: since Python 3.12 the built-in carries a correction
    term the loop does not, and this measurement is about last bits.
    """
    curves = data["calc_curves"]
    reinforce_table = data["reinforce"]
    element_correct = data["element_correct"]

    base_type = weapon.get("reinforce_type", 0)
    own_tier = weapon.get("rarity", 0) + 1
    steps = max(0, min(upgrade, weapons.MAX_UPGRADE) - own_tier)
    reinforce = None
    for level in range(steps, -1, -1):
        reinforce = reinforce_table.get(str(base_type + level))
        if reinforce is not None:
            break
    if reinforce is None:
        reinforce = {"atk": {}, "correct": {}}

    aec = element_correct.get(str(weapon.get("element_correct_id")), {})
    out: dict[str, tuple[float, float]] = {}
    for damage in weapons.DAMAGE_TYPES:
        base = weapon["base"].get(damage, 0)
        if not base:
            continue
        base *= reinforce["atk"].get(damage, 1.0)
        rules = aec.get(damage, {})
        curve = curves.get(str(weapon["curve"].get(damage)))
        bonus = 0.0
        if curve is not None:
            for stat, scaling in weapon["scaling"].items():
                rule = rules.get(stat)
                if not scaling or not rule or not rule["on"]:
                    continue
                correct = scaling / 100.0 * reinforce["correct"].get(stat, 1.0)
                ratio = model.evaluate_curve(curve,
                                             attributes.get(stat, 0)) / 100.0
                # `influence / 100` on its own line, as `weapons.rate` has
                # it: folding it into the product below is a different
                # bracketing and lands a last bit away, which is the whole
                # quantity being counted here. The guard in `measure` caught
                # exactly that on the first run of this script.
                influence = rule["influence"] / 100.0
                bonus += correct * ratio * influence
        out[damage] = (base, bonus)
    return out


def measure(data: dict, step: int) -> dict:
    """Count how far each bracket lands from `fl(old * K)`, in last bits."""
    factor = weapons.GAME_ATTACK_POWER_RATE
    curves = data.get("curves", {})
    armaments = data["weapons"][::step]

    per_type = {"shipped": collections.Counter(),
                "on_the_base": collections.Counter()}
    totals = {"shipped": collections.Counter(),
              "on_the_base": collections.Counter()}
    cases = figures = disagreed = 0

    for hero in data["heroes"]:
        for level in LEVELS:
            attributes = model.compute(hero, level, [], curves).attributes
            for upgrade in TIERS:
                for weapon in armaments:
                    cases += 1
                    parts = ingredients(weapon, attributes, data, upgrade)
                    shipped_rating = weapons.rate(weapon, attributes, data,
                                                  upgrade)
                    old_sum = shipped_sum = base_sum = 0.0
                    for damage, (base, bonus) in parts.items():
                        old = base * bonus
                        want = old * factor
                        shipped = base * bonus * factor
                        on_the_base = (base * factor) * bonus
                        # The re-derivation has to be the program's own
                        # arithmetic, or the counts below describe a third
                        # calculation nobody ships.
                        if shipped != shipped_rating.scaled[damage]:
                            disagreed += 1
                        figures += 1
                        per_type["shipped"][ulps_apart(shipped, want)] += 1
                        per_type["on_the_base"][
                            ulps_apart(on_the_base, want)] += 1
                        old_sum += old
                        shipped_sum += shipped
                        base_sum += on_the_base
                    wanted_sum = old_sum * factor
                    totals["shipped"][ulps_apart(shipped_sum, wanted_sum)] += 1
                    totals["on_the_base"][
                        ulps_apart(base_sum, wanted_sum)] += 1

    return {
        "data_version": data.get("meta", {}).get("data_version"),
        "factor": factor,
        "heroes": len(data["heroes"]),
        "levels": list(LEVELS),
        "tiers": list(TIERS),
        "armaments": len(armaments),
        "step": step,
        "cases": cases,
        "per_type_figures": figures,
        "disagreed_with_weapons_rate": disagreed,
        "per_type": {name: dict(sorted(counts.items()))
                     for name, counts in per_type.items()},
        "totals": {name: dict(sorted(counts.items()))
                   for name, counts in totals.items()},
    }


def report(result: dict) -> None:
    print(f"data_version {result['data_version']}, "
          f"K = {result['factor']}")
    print(f"{result['heroes']} Nightfarers x levels {result['levels']} x "
          f"tiers {result['tiers']} x {result['armaments']} armaments "
          f"(step {result['step']}) = {result['cases']} cases, "
          f"{result['per_type_figures']} figures per damage type")
    if result["disagreed_with_weapons_rate"]:
        print(f"  !! {result['disagreed_with_weapons_rate']} of them do not "
              f"match weapons.rate; the arithmetic here is not the "
              f"program's and the counts below mean nothing")
    else:
        print("  every shipped figure matches weapons.rate bit for bit")
    for what, counts in (("per damage type", result["per_type"]),
                         ("summed per case", result["totals"])):
        print(f"  {what}:")
        for name, spread in counts.items():
            beyond = sum(n for ulps, n in spread.items() if int(ulps) >= 2)
            total = sum(spread.values())
            print(f"    {name:12s} {beyond} of {total} at 2 ULP or more; "
                  f"spread {spread}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--step", type=int, default=1,
                        help="take every N-th armament, for a smoke run. The "
                             "step is printed with the counts, so a "
                             "subsampled figure cannot be quoted as the "
                             "whole one.")
    parser.add_argument("--json", type=pathlib.Path,
                        help="write the counts here as well")
    args = parser.parse_args(argv)
    if args.step < 1:
        raise SystemExit("--step counts armaments, so it is at least 1")

    result = measure(load_data(), args.step)
    report(result)
    if args.json:
        args.json.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"wrote {args.json}")
    return 1 if result["disagreed_with_weapons_rate"] else 0


if __name__ == "__main__":
    sys.exit(main())
