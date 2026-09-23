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
    "place-route-back-under-the-hp-bar": Mutation(
        path="nrdata/bossdata.py",
        old="        found, group = _candidates(rows_for, placements, min_hp=0)\n",
        new="        found, group = _candidates(rows_for, placements)\n",
        survival_means=(
            "Nothing holds the place cards to AD-042. The HP bar belongs to "
            "the Nightlord arenas, and back on the place route it cuts 16 of "
            "the 29 field bosses away (904-5753 HP): those cards lose their "
            "character and say 'not derivable'. Since AD-044 the same bar "
            "would meet all 64 cards of the block. A green suite would mean "
            "the sub-boss roster can quietly shrink to a third of itself."
        ),
    ),
    "health-bar-name-bound-to-the-map": Mutation(
        path="nrdata/bossdata.py",
        old='        on_entities = entities.get(entry["primary"], [])\n',
        new="        on_entities = [e for row in entities.values() for e in row]\n",
        survival_means=(
            "Nothing holds a health-bar name to the character it was passed "
            "in for. Taking whichever entity of the map the script names "
            "first renames `4551` to 'Black Knife Assassin', `4659` to "
            "'Royal Revenant' and `4662` to \"Night's Cavalry\": on all "
            "three the chosen character carries no entity at all, and the "
            "one the script names belongs to somebody else standing in the "
            "same map (AD-043.1, measured T-310). A "
            "green suite would mean a name on a card proves nothing about "
            "who is on it, which is the failure QA-286 is made of."
        ),
    ),
    "health-bar-name-behind-the-table-order": Mutation(
        path="nrdata/extract.py",
        old='            "name": (npc_names.get(entry.get("name_id"))\n'
            '                     or chr_names.get(chr_id, "")),\n',
        new='            "name": (chr_names.get(chr_id)\n'
            '                     or npc_names.get(entry.get("name_id"), "")),\n',
        survival_means=(
            "Nothing holds the two name routes to their order. Reversed, "
            "`4666` is called 'Valiant Gargoyle' again -- c4770 carries "
            "three names in the structured block and the table order picks "
            "the first, while the script of the place calls it 'Black Blade "
            "Kindred' (AD-043.2). The two cards that gained a name keep it "
            "either way, so a green suite would mean only the disagreement "
            "is unguarded -- the one case the decision is about."
        ),
    ),
    "spread-bar-back-on-the-knife-edge": Mutation(
        path="nrdata/bossdata.py",
        old='            - min(profile["damage"].values())) '
            ">= INFERRED_MIN_SPREAD - 1e-6\n",
        new='            - min(profile["damage"].values())) '
            ">= INFERRED_MIN_SPREAD\n",
        survival_means=(
            "Nothing holds the tuning bar to the width of float32 noise. "
            "The cut rates are float32, so a spread authored as 0.7 - 0.6 "
            "arrives as 0.09999996 and misses the bar by a float: `4920` "
            "drops the Stoneskin Lords (628 HP) and falls back to a 162 HP "
            "add (AD-044.2). A green suite would mean the bar may be a "
            "knife edge that a rounding error decides."
        ),
    ),
    "place-route-takes-the-smallest": Mutation(
        path="nrdata/bossdata.py",
        old='            best = max(found, key=lambda pair: pair[1]["hp"] or 0)\n',
        new='            best = min(found, key=lambda pair: pair[1]["hp"] or 0)\n',
        survival_means=(
            "Nothing holds a card to the boss standing on it. With the "
            "smallest taken, `4659` names c4021 (2279 HP) instead of the "
            "Decaying Rancor Dragon (5753) and `4671` names a blossom (119) "
            "instead of Miranda (1939). A green suite would mean the name a "
            "card carries is unguarded -- the failure QA-286 is made of."
        ),
    ),
    "night-lottery-forgets-day-two": Mutation(
        path="nrdata/extract.py",
        old='NIGHT_BOSS_FIELDS = ("bossId1", "bossId2")\n',
        new='NIGHT_BOSS_FIELDS = ("bossId1",)\n',
        survival_means=(
            "Nothing holds the night lottery to both of its days. With "
            "`bossId2` dropped, every card only day 2 draws leaves the "
            "block and the tab's DAY 2 group is empty, while the cards both "
            "days draw quietly claim to be day 1 only. A green suite would "
            "mean half of stage two can go missing unnoticed."
        ),
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
