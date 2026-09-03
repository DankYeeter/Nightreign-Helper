"""Hold two captures against each other and spell out everything that moved.

Developer tool. See `scripts/differential/__init__.py` for the whole track.

    python scripts/differential/compare.py OLD.jsonl NEW.jsonl \\
        [--expected FIELD ...] [--examples N]

Counts first, then the records themselves. A field named with `--expected` is
still counted -- it never disappears from the summary -- it is only left out
of the dump, because it is a difference somebody has already accounted for.
**Everything else is printed in full.** That is the property that made the W3
measurement usable and the one not to trade away for a tidier report: a
comparer that summarises what it does not understand hides exactly the case
nobody predicted.

Exit code 1 when anything differed in a field that was not named as expected,
0 when nothing did. The exit code is a convenience; the counts above it are
the evidence, and they name the field and the case, which no exit code can.
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys

#: Printed when a record is missing a field the other one has. A plain
#: `KeyError` here would look like a broken script rather than a finding.
ABSENT = "<field not in this capture>"


def read(path: pathlib.Path) -> list[dict]:
    return [json.loads(line) for line in
            path.read_text(encoding="utf-8").splitlines() if line.strip()]


def field_names(old: dict, new: dict) -> list[str]:
    """Every field either side holds, in a stable order.

    The union rather than the intersection: a field one capture has and the
    other has not is the single most interesting difference there is, and an
    intersection would drop it silently.
    """
    names = list(old)
    names += [name for name in new if name not in old]
    return [name for name in names if name not in ("index", "case")]


def differences(old: dict, new: dict) -> dict[str, tuple]:
    """Field name -> (before, after), for the fields that are not equal."""
    out = {}
    for name in field_names(old, new):
        before = old.get(name, ABSENT)
        after = new.get(name, ABSENT)
        if before != after:
            out[name] = (before, after)
    return out


def tile_entries_moved(before, after) -> int:
    """How many of the six tile texts moved, when the field is `tiles`.

    Reported beside the record count because the two say different things: a
    mutation can touch one record and five of its tiles, and "50 % of cases"
    alone would not say how much of the screen that is.
    """
    if not isinstance(before, list) or not isinstance(after, list):
        return 0
    pairs = zip(before, after)
    return sum(1 for one, other in pairs if one != other)


class Report:
    """What the comparison found. Kept apart from printing so it is testable."""

    def __init__(self) -> None:
        self.compared = 0
        self.differing = 0
        self.by_field: collections.Counter = collections.Counter()
        self.tiles_moved = 0
        self.unexpected: list[tuple[dict, dict, dict]] = []
        self.misaligned: list[tuple[int, str, str]] = []

    @property
    def unexpected_records(self) -> int:
        return len(self.unexpected)


def compare(old: list[dict], new: list[dict], expected: set[str]) -> Report:
    """Align the two captures by position and diff them field by field."""
    report = Report()
    if len(old) != len(new):
        raise SystemExit(
            f"{len(old)} records on one side and {len(new)} on the other. "
            f"Two captures of one plan have one length; nothing compared.")

    for one, other in zip(old, new):
        report.compared += 1
        if one.get("case") != other.get("case"):
            report.misaligned.append(
                (one.get("index"), one.get("case"), other.get("case")))
            continue
        found = differences(one, other)
        if not found:
            continue
        report.differing += 1
        for name, (before, after) in found.items():
            report.by_field[name] += 1
            if name == "tiles":
                report.tiles_moved += tile_entries_moved(before, after)
        surprising = {name: pair for name, pair in found.items()
                      if name not in expected}
        if surprising:
            report.unexpected.append((one, other, surprising))
    if report.misaligned:
        raise SystemExit(
            f"{len(report.misaligned)} records do not line up by case name, "
            f"first at index {report.misaligned[0][0]}: "
            f"{report.misaligned[0][1]!r} against "
            f"{report.misaligned[0][2]!r}. The two captures ran different "
            f"plans; nothing compared.")
    return report


def render(report: Report, expected: set[str], examples: int) -> list[str]:
    """The report as lines, so a test can read it instead of stdout."""
    lines = [
        f"compared {report.compared} records",
        f"differing {report.differing} records"
        f"{_share(report.differing, report.compared, prefix=' ')}",
    ]
    for name, count in sorted(report.by_field.items()):
        mark = " (expected)" if name in expected else ""
        lines.append(f"  {name}: {count} records"
                     f"{_share(count, report.compared, prefix=' ')}{mark}")
    if report.tiles_moved:
        lines.append(f"  tiles: {report.tiles_moved} single tile texts moved "
                     f"across those records")
    lines.append(f"unexpected: {report.unexpected_records} records differ in a "
                 f"field nobody named")

    shown = report.unexpected if examples == 0 else report.unexpected[:examples]
    for one, _other, surprising in shown:
        lines.append("")
        lines.append(f"--- index {one.get('index')}: {one.get('case')}")
        for name, (before, after) in sorted(surprising.items()):
            lines.append(f"  {name}")
            lines.append(f"    before {before!r}")
            lines.append(f"    after  {after!r}")
    withheld = report.unexpected_records - len(shown)
    if withheld:
        lines.append("")
        lines.append(f"{withheld} further unexpected records not printed. "
                     f"Re-run with --examples 0 to see all of them.")
    return lines


def _share(part: int, whole: int, prefix: str = "") -> str:
    if not whole:
        return ""
    return f"{prefix}({part / whole * 100:.1f} %)"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("old", type=pathlib.Path)
    parser.add_argument("new", type=pathlib.Path)
    parser.add_argument("--expected", action="append", default=[],
                        metavar="FIELD",
                        help="a field whose difference is already accounted "
                             "for: counted, but not dumped. Repeatable.")
    parser.add_argument("--examples", type=int, default=20,
                        help="how many unexpected records to print in full; "
                             "0 for all of them (default: 20)")
    args = parser.parse_args(argv)

    expected = set(args.expected)
    report = compare(read(args.old), read(args.new), expected)
    print("\n".join(render(report, expected, args.examples)))
    return 1 if report.unexpected_records else 0


if __name__ == "__main__":
    sys.exit(main())
