"""Ask two captures whether every figure that moved moved by the same factor.

Developer tool. See `scripts/differential/__init__.py` for the whole track.

    python scripts/differential/ratios.py OLD.jsonl NEW.jsonl \\
        [--factor 0.6] [--examples N]

`compare.py` answers "what moved". That is the right question for a
refactoring, which is supposed to move nothing. It is the wrong one for a
**calibration**: T-045 multiplied every attack rating by a measured constant,
so of course tens of thousands of figures moved, and a comparer that reports
that they did has said nothing about whether they moved by the amount that
was intended. This script answers the second question, over the same two
capture files, and sorts every leaf of every record into one of three kinds:

* **scaled** -- a figure that came out `old x factor`. Held to **one ULP** of
  `fl(old x factor)`, computed in the same double arithmetic the program
  uses, not to a percentage tolerance;
* **still** -- a value the factor never reached: a multiplier, an attribute,
  a tier, a piece of text. It has to be bit-identical, and one that moved is
  a finding rather than a rounding;
* **rendered** -- a whole number on screen. It cannot show the ratio, because
  the two trees do not turn a figure into a digit by the same rule, so it is
  held against the bracket those rules leave open rather than against a
  tolerance somebody picked (see `admissible` below).

Everything it cannot place it prints in full, the way `compare.py` does: a
report that tallies what it does not understand hides the one case nobody
predicted. Exit code 1 when there is any such value, 0 when there is none.

**The bracket, derived.** For a whole number on screen the figure behind it
is not in the capture, so the check is what the two display rules leave
possible:

    old tree   `f"{x:.0f}"`, so |x_old - shown_old| <= 0.5
    new tree   `damage.displayed` = `math.floor`, so 0 <= x_new - shown_new
               < 1 for an attack rating, and `f"{d:+.0f}"` as before for the
               change lines
    claim      x_new = factor x x_old, which the figures above establish
               exactly

so `shown_new` has to be a whole number that the interval
`[factor x (shown_old - 0.5), factor x (shown_old + 0.5)]` can still reach
under one of the two rules. That interval is `factor` wide -- 0.6 here -- so
it admits one or two whole numbers, never a range any value would satisfy.
Which of the two rules a given number is drawn by is not guessed: both are
tried and the report says how many landed under each.
"""

from __future__ import annotations

import argparse
import collections
import json
import math
import pathlib
import re
import struct
import sys

#: One side has a field the other has not. Printed rather than raised: a
#: field that appeared or vanished is a finding, not a broken script.
ABSENT = "<field not in this capture>"

#: `float.hex()`, which is how `capture.py` writes every float -- its
#: docstring says why: a one-ULP change cannot then hide behind `repr`.
HEX_FLOAT = re.compile(r"^[+-]?0x[0-9a-f]+(?:\.[0-9a-f]+)?p[+-]?\d+$")

#: A number on screen. Deliberately blind to the digits inside a colour
#: (`#8a8a8a`) or a length (`10px`): those are not figures, and leaving them
#: in the surrounding text means a colour that changed shows up as text that
#: moved rather than as a figure that moved.
NUMBER = re.compile(r"(?<![\w#.])[+-]?\d+(?:\.\d+)?(?![\w.])")

#: What `NUMBER` leaves behind, so two texts can be held against each other
#: without their figures in the way.
HOLE = "\x00"


class Missing:
    """One capture holds this field and the other does not."""

    def __repr__(self) -> str:
        return ABSENT


MISSING = Missing()


def read(path: pathlib.Path) -> list[dict]:
    return [json.loads(line) for line in
            path.read_text(encoding="utf-8").splitlines() if line.strip()]


def bits(value: float) -> int:
    """A double as the integer that orders doubles the way `<` does.

    So that ULPs between two of them can be counted exactly. `abs(a - b) /
    ulp(b)` would answer in floating point the question being asked *about*
    floating point, and round the answer it is meant to report.
    """
    raw = struct.unpack("<q", struct.pack("<d", value))[0]
    return raw if raw >= 0 else -(raw & 0x7FFFFFFFFFFFFFFF) - 1


def ulps_between(one: float, other: float) -> int:
    return abs(bits(one) - bits(other))


def is_hex_float(value) -> bool:
    return isinstance(value, str) and bool(HEX_FLOAT.match(value))


def admissible(shown_old: float, shown_new: float, factor: float,
               decimals: int) -> str | None:
    """Which display rule, if either, reaches `shown_new` from `shown_old`.

    Hands back `"truncated"`, `"rounded"` or `None`. The interval is the
    whole derivation: the old tree rendered `x_old` to `decimals` places by
    rounding, so `x_old` sits within half a step of `shown_old`; the claim
    under test is that the new tree computed `factor x x_old`; and the new
    tree turns that into digits either by truncating -- the attack ratings,
    through `damage.displayed` -- or by rounding, as the change lines still
    do. A number neither rule can reach is a finding.
    """
    step = 10.0 ** -decimals
    half = step / 2.0
    low = factor * (shown_old - half)
    high = factor * (shown_old + half)
    # A hair of slack against the decimal-to-binary conversion of the two
    # rendered numbers themselves; far below the step, so it cannot widen the
    # bracket by a whole number.
    fuzz = step * 1e-9
    # Truncation: some value in [low, high] has `shown_new` as its step below.
    if shown_new <= high + fuzz and shown_new + step > low - fuzz:
        return "truncated"
    # Rounding: some value in [low, high] is within half a step of it.
    if shown_new - half <= high + fuzz and shown_new + half >= low - fuzz:
        return "rounded"
    return None


def decimals_of(text: str) -> int:
    _, _, fraction = text.partition(".")
    return len(fraction)


def walk(old, new, path: str):
    """Every leaf of the two records, side by side, with where it sits.

    Two dicts are walked over the **union** of their keys, and two lists only
    while they are the same length, for the reason `compare.field_names`
    gives: an entry one side has and the other has not is the most
    interesting difference there is, and it must not be dropped quietly.
    """
    if isinstance(old, dict) and isinstance(new, dict):
        keys = list(old) + [key for key in new if key not in old]
        for key in keys:
            yield from walk(old.get(key, MISSING), new.get(key, MISSING),
                            f"{path}.{key}")
    elif (isinstance(old, list) and isinstance(new, list)
            and len(old) == len(new)):
        for index, (one, other) in enumerate(zip(old, new)):
            yield from walk(one, other, f"{path}[{index}]")
    else:
        yield path, old, new


def collapse(path: str) -> str:
    """`tiles[3].detail` -> `tiles[].detail`, so the summary has rows."""
    return re.sub(r"\[\d+\]", "[]", path)


class Report:
    """What the run found. Kept apart from the printing, so a test can read
    it instead of stdout."""

    def __init__(self, factor: float) -> None:
        self.factor = factor
        self.records = 0
        self.figures = 0
        self.figures_scaled = 0
        self.figures_still = 0
        self.figures_zero = 0
        self.worst_ulps = 0
        self.worst_ulps_where: tuple | None = None
        self.numbers = 0
        self.numbers_still = 0
        self.numbers_truncated = 0
        self.numbers_rounded = 0
        self.worst_gap = 0.0
        self.worst_gap_where: tuple | None = None
        self.texts_still = 0
        self.by_path: collections.Counter = collections.Counter()
        self.unplaced: list[tuple[str, str, str, object, object]] = []

    @property
    def unplaced_count(self) -> int:
        return len(self.unplaced)

    def place(self, path: str, kind: str) -> None:
        self.by_path[(collapse(path), kind)] += 1

    def cannot_place(self, case: str, path: str, why: str, old, new) -> None:
        self.by_path[(collapse(path), "unplaced")] += 1
        self.unplaced.append((case, path, why, old, new))


def _figure(report: Report, case: str, path: str, old: str, new: str) -> None:
    """One captured double against the other. This is the exact half."""
    before, after = float.fromhex(old), float.fromhex(new)
    report.figures += 1
    if before == 0.0 and after == 0.0:
        # Nothing to divide by and nothing the factor could have moved.
        # Counted apart rather than as `still`, so the evidence is not padded
        # with values that would look the same under any factor at all.
        report.figures_zero += 1
        report.place(path, "zero")
        return
    wanted = before * report.factor
    distance = ulps_between(after, wanted)
    if distance <= 1:
        report.figures_scaled += 1
        report.place(path, "scaled")
        if distance > report.worst_ulps:
            report.worst_ulps = distance
            report.worst_ulps_where = (case, path, before, after)
        return
    if after == before:
        report.figures_still += 1
        report.place(path, "still")
        return
    report.cannot_place(
        case, path,
        f"ratio {after / before!r}, {distance} ULP away from {wanted!r} "
        f"= old x {report.factor}", before, after)


def _text(report: Report, case: str, path: str, old: str, new: str) -> None:
    """One rendered string against the other, figure by figure."""
    if old == new:
        report.texts_still += 1
        report.place(path, "still")
        return
    if NUMBER.sub(HOLE, old) != NUMBER.sub(HOLE, new):
        report.cannot_place(
            case, path,
            "the text around the figures moved, not only the figures",
            old, new)
        return
    for one, other in zip(NUMBER.findall(old), NUMBER.findall(new)):
        report.numbers += 1
        if one == other:
            report.numbers_still += 1
            continue
        decimals = max(decimals_of(one), decimals_of(other))
        shown_old, shown_new = float(one), float(other)
        rule = admissible(shown_old, shown_new, report.factor, decimals)
        if rule is None:
            report.cannot_place(
                case, path,
                f"{one} -> {other}: no rounding rule reaches it from "
                f"{report.factor} x {one}", old, new)
            continue
        if rule == "truncated":
            report.numbers_truncated += 1
        else:
            report.numbers_rounded += 1
        gap = abs(shown_new - report.factor * shown_old)
        if gap > report.worst_gap:
            report.worst_gap = gap
            report.worst_gap_where = (case, path, one, other)
    report.place(path, "rendered")


def measure(old: list[dict], new: list[dict], factor: float) -> Report:
    """Walk two captures of one plan and sort every value they hold."""
    report = Report(factor)
    if len(old) != len(new):
        raise SystemExit(
            f"{len(old)} records on one side and {len(new)} on the other. "
            f"Two captures of one plan have one length; nothing measured.")

    for one, other in zip(old, new):
        if one.get("case") != other.get("case"):
            raise SystemExit(
                f"records do not line up by case name at index "
                f"{one.get('index')}: {one.get('case')!r} against "
                f"{other.get('case')!r}. The two captures ran different "
                f"plans; nothing measured.")
        report.records += 1
        case = one.get("case", "")
        for path, before, after in walk(one, other, ""):
            if path in (".index", ".case"):
                continue
            if before is MISSING or after is MISSING:
                report.cannot_place(
                    case, path, "one capture has no such field",
                    before, after)
            elif is_hex_float(before) and is_hex_float(after):
                _figure(report, case, path, before, after)
            elif isinstance(before, str) and isinstance(after, str):
                _text(report, case, path, before, after)
            elif before == after:
                report.place(path, "still")
            else:
                report.cannot_place(
                    case, path, "a value carrying no figure moved",
                    before, after)
    return report


def render(report: Report, examples: int) -> list[str]:
    """The findings as lines, so a test can read them instead of stdout."""
    lines = [
        f"measured {report.records} records against factor {report.factor}",
        f"figures {report.figures}: {report.figures_scaled} scaled by the "
        f"factor within 1 ULP, {report.figures_still} unmoved, "
        f"{report.figures_zero} zero on both sides",
        f"numbers on screen {report.numbers}: {report.numbers_still} unmoved, "
        f"{report.numbers_truncated} moved as truncation allows, "
        f"{report.numbers_rounded} as rounding allows",
        f"texts identical {report.texts_still}",
    ]
    if report.worst_ulps_where:
        case, path, before, after = report.worst_ulps_where
        lines.append(f"furthest figure {report.worst_ulps} ULP: {path} in "
                     f"{case}, {before!r} -> {after!r}")
    else:
        lines.append(f"furthest figure {report.worst_ulps} ULP")
    if report.worst_gap_where:
        case, path, before, after = report.worst_gap_where
        lines.append(f"widest gap on screen {report.worst_gap:.3f}: {path} "
                     f"in {case}, {before} -> {after}")
    lines.append(f"unplaced: {report.unplaced_count} values neither scaled, "
                 f"unmoved, nor reachable by a rounding rule")
    lines.append("")
    lines.append("by field:")
    for (path, kind), count in sorted(report.by_path.items()):
        lines.append(f"  {path or '.'} {kind}: {count}")

    shown = (report.unplaced if examples == 0 else report.unplaced[:examples])
    for case, path, why, old, new in shown:
        lines.append("")
        lines.append(f"--- {case}")
        lines.append(f"  {path}: {why}")
        lines.append(f"    before {old!r}")
        lines.append(f"    after  {new!r}")
    withheld = report.unplaced_count - len(shown)
    if withheld:
        lines.append("")
        lines.append(f"{withheld} further unplaced values not printed. "
                     f"Re-run with --examples 0 to see all of them.")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("old", type=pathlib.Path)
    parser.add_argument("new", type=pathlib.Path)
    parser.add_argument("--factor", type=float, default=0.6,
                        help="the ratio every figure is expected to have "
                             "moved by, or not to have moved at all "
                             "(default: 0.6)")
    parser.add_argument("--examples", type=int, default=20,
                        help="how many unplaced values to print in full; "
                             "0 for all of them (default: 20)")
    args = parser.parse_args(argv)

    report = measure(read(args.old), read(args.new), args.factor)
    print("\n".join(render(report, args.examples)))
    return 1 if report.unplaced_count else 0


if __name__ == "__main__":
    sys.exit(main())
