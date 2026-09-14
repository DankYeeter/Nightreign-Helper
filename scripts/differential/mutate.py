"""Break one named thing on purpose, so a guard can be shown to have teeth.

Developer tool. See `scripts/differential/__init__.py` for the whole track.

    python scripts/differential/mutate.py --list
    python scripts/differential/mutate.py --apply NAME --tree DIR

A green suite is not evidence that anything is guarded. The evidence is a
mutation that the suite catches, and the counter-evidence -- the one this
repository keeps running into -- is a mutation that changes tens of thousands
of figures on screen and leaves every test green (QA-070, QA-073).

Each mutation is written out in full: the exact text it replaces, the exact
text it puts there, and what a reader is supposed to conclude when the suite
stays green. It is applied to a **copy** of a tree; this refuses to touch the
checkout it lives in, or any other tree with a `.git` of its own -- a second
clone or a `git worktree add` is a working tree exactly like this one, and is
the more direct path back to the unmutated source than the extraction below,
which makes it the more likely mistake, not a safer one (QA-079 b). A
half-restored mutation in a working tree is a worse outcome than any
measurement is worth:

    git archive HEAD | tar -x -C /tmp/mutant
    python scripts/differential/mutate.py --apply active-tile-only \\
        --tree /tmp/mutant
    cd /tmp/mutant && PYTHONHASHSEED=0 python -m pytest -q

The anchor of every mutation is checked by `tests/test_differential_track.py`
against the real source: if a refactoring moves the line, the registry fails
loudly instead of quietly patching nothing and reporting a green run.
"""

from __future__ import annotations

import argparse
import dataclasses
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]


@dataclasses.dataclass(frozen=True)
class Mutation:
    """One edit, its anchor, and what its survival would mean."""

    #: Path inside the tree, forward slashes.
    path: str
    #: The text to replace. Must occur exactly once, or nothing is written.
    old: str
    #: What to put there instead.
    new: str
    #: What a green suite after this edit tells the reader.
    survival_means: str


#: The anchors below run past the margin every other line in this repository
#: keeps to, and they have to: they are the source verbatim, and a wrapped
#: anchor matches nothing.
MUTATIONS: dict[str, Mutation] = {
    "two-handed-rate-neutralised": Mutation(
        path="nrplanner/weapons.py",
        old="""TWO_HANDED_RATE = 1.03
""",
        new="""TWO_HANDED_RATE = 1.0
""",
        survival_means=(
            "every Nightfarer but the Raider shows the one-handed figure as "
            "the two-handed one -- 122 / 122 where the game shows 122 / 125. "
            "Killed by the Duchess, Wylder and Guardian rows of `tests/test_"
            "attack_power_calibration_against_the_game.py::test_both_hands_"
            "show_the_numbers_the_game_showed` (T-254b, R-008)."),
    ),
    "raider-two-handed-rate-neutralised": Mutation(
        path="nrplanner/weapons.py",
        old="""RAIDER_TWO_HANDED_RATE = 1.144
""",
        new="""RAIDER_TWO_HANDED_RATE = 1.0
""",
        survival_means=(
            "the Raider two-hands for nothing: 158 / 158 and 188 / 188 where "
            "the game shows 180 and 216. Killed by the two Raider rows of "
            "`tests/test_attack_power_calibration_against_the_game.py::test_"
            "both_hands_show_the_numbers_the_game_showed` and by `test_the_"
            "two_handed_answer_names_its_factor` (T-254b, R-008)."),
    ),
    "two-handing-buff-left-on-the-scoped-line": Mutation(
        path="nrplanner/model.py",
        old="""WEAPON_CLASS_SCOPES = {130: "melee", 113: "ranged", 118: "ranged",
                       TWO_HANDING_SCOPE: TWO_HANDED_CLASS}
""",
        new="""WEAPON_CLASS_SCOPES = {130: "melee", 113: "ranged", 118: "ranged"}
""",
        survival_means=(
            "`Improved Attack Power when Two-Handing` is back on a `scoped:` "
            "line outside every attack rating, and the two-handed figure "
            "ignores the one relic written for it. Killed by `tests/test_"
            "attack_power_calibration_against_the_game.py::test_a_when_two_"
            "handing_buff_lifts_the_two_handed_figure_only` and `test_the_"
            "stance_buff_travels_with_its_condition_and_moves_no_figure` "
            "(T-254b, AD-037 point 3)."),
    ),
}


def newline_of(raw: bytes) -> bytes:
    """The line ending the file already uses.

    Measured 2026-09-05, because the reason written here had gone stale by
    half. A tree extracted the way the header of this module says to extract
    one -- `git archive HEAD | tar -x` -- is LF throughout, `.gitattributes`
    carrying `* text=auto eol=lf`, so nothing in that tree needs this. The
    **working tree** is a different matter: `app.py` sits there in CRLF while
    every other module is LF, and a copy of the working tree is a tree someone
    will eventually mutate. Reading the ending out of the file costs one line
    and keeps a mutation from rewriting a file it was only supposed to edit.
    """
    return b"\r\n" if b"\r\n" in raw else b"\n"


def apply(mutation: Mutation, tree: pathlib.Path) -> tuple[int, int]:
    """Write the mutation into `tree`. Hands back (line number, bytes moved).

    Refuses unless the anchor occurs exactly once. A mutation that silently
    matched nothing is the worst outcome this tool can have: the suite then
    runs green against unmutated code and the reader concludes the guard
    holds.
    """
    path = (tree / mutation.path).resolve()
    if not path.is_file():
        raise SystemExit(f"no {mutation.path} in the tree at {tree}")
    raw = path.read_bytes()
    newline = newline_of(raw)
    old = mutation.old.encode("utf-8").replace(b"\n", newline)
    new = mutation.new.encode("utf-8").replace(b"\n", newline)

    found = raw.count(old)
    if found != 1:
        raise SystemExit(
            f"the anchor of this mutation occurs {found} times in "
            f"{mutation.path}, and it has to occur exactly once. Nothing "
            f"written. The source has moved on -- update the mutation, do "
            f"not loosen the anchor.")
    line = raw[:raw.index(old)].count(newline) + 1
    path.write_bytes(raw.replace(old, new))
    return line, len(new) - len(old)


def guard_the_own_tree(tree: pathlib.Path) -> None:
    if tree == ROOT:
        raise SystemExit(
            f"{tree} is the checkout this script lives in. Mutate a copy: "
            f"`git archive HEAD | tar -x -C <somewhere>`. A mutation left "
            f"behind in a working tree costs more than the measurement is "
            f"worth.")
    if (tree / ".git").exists():
        raise SystemExit(
            f"{tree} has a .git of its own. A second clone or a `git "
            f"worktree add` is a working tree the same as this checkout, and "
            f"mutating it is worse than mutating this one: it is the more "
            f"direct way back to the unmutated source, which makes leaving a "
            f"mutation behind in it the more likely mistake (QA-079 b). "
            f"Mutate a plain extraction instead: "
            f"`git archive HEAD | tar -x -C <somewhere>`.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--list", action="store_true",
                        help="name every mutation and what its survival "
                             "would mean")
    parser.add_argument("--apply", metavar="NAME",
                        help="the mutation to write into --tree")
    parser.add_argument("--tree", type=pathlib.Path,
                        help="a copy of the source tree to mutate")
    args = parser.parse_args(argv)

    if args.list or not args.apply:
        for name, mutation in MUTATIONS.items():
            print(f"{name}\n  {mutation.path}\n  if the suite stays green: "
                  f"{mutation.survival_means}\n")
        return 0 if args.list else 2

    mutation = MUTATIONS.get(args.apply)
    if mutation is None:
        raise SystemExit(
            f"no mutation called {args.apply!r}. --list names them all.")
    if args.tree is None:
        raise SystemExit("--apply needs --tree: which copy to write into.")

    tree = args.tree.resolve()
    guard_the_own_tree(tree)
    line, moved = apply(mutation, tree)
    print(f"{args.apply}: {mutation.path}:{line} rewritten "
          f"({moved:+d} bytes) in {tree}")
    print(f"if the suite now stays green: {mutation.survival_means}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
