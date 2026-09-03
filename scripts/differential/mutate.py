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
    "active-tile-only": Mutation(
        path="nrplanner/app.py",
        old="""                answers[index] = damage.equipped(slot, index, build, hero,
                                                 self.data)
                equipped = answers[index][1]
""",
        new="""                answers[index] = damage.equipped(slot, index, build, hero,
                                                 self.data)
                equipped = (answers[index][1]
                            if index == self.active_weapon
                            else answers[index][0])
""",
        survival_means=(
            "the five tiles that are not the active one are drawn by no "
            "guard. They would show the figure from before the attack "
            "multipliers, and a click on another tile would make the number "
            "jump -- QA-056 in new clothes. Measured surviving on 2026-09-03: "
            "36 958 tile figures moved in 12 551 of 25 102 cases, 237 of 237 "
            "tests green (QA-073 a)."),
    ),
    "breakdown-base-and-scaled-swapped": Mutation(
        path="nrplanner/app.py",
        old="""        base, scaled, final = ar["base"], ar["scaled"], ar["final"]
""",
        new="""        base, scaled, final = ar["scaled"], ar["base"], ar["scaled"]
""",
        survival_means=(
            "the click-through breakdown is read by nobody. The golden file "
            "freezes `last_ar`, which is this display's **input**, never its "
            "output, and the text went only to a QToolTip. Measured "
            "surviving on 2026-09-03: 237 of 237 tests green (QA-073 b)."),
    ),
    "arsenal-tile-figure-halved": Mutation(
        path="nrplanner/arsenaltab.py",
        old="""                lines = [("AR", f"{rating.final_total:.0f}")]
""",
        new="""                lines = [("AR", f"{rating.final_total * 0.5:.0f}")]
""",
        survival_means=(
            "no test reads a single figure off the arsenal tab. Every AR "
            "line on every tile of the tab would be half of what the "
            "armament does, and the player's whole comparison between "
            "armaments would stand on it. Measured surviving on 2026-09-03, "
            "on the tree before W4 and with the same edit against "
            "`rating.total`: 264 of 264 tests green. Guarded since by "
            "tests/test_arsenal_tab_asks_the_facade.py, which reads the "
            "rendered tile and not the list behind it."),
    ),
    "arsenal-ranks-at-the-slot-tier": Mutation(
        path="nrplanner/arsenaltab.py",
        old="""        self.ratings = damage.rank_candidates(
            build, self.upgrade.value(), self.data,
""",
        new="""        self.ratings = damage.rank_candidates(
            build, weapons.MAX_UPGRADE, self.data,
""",
        survival_means=(
            "the tier the arsenal tab ranks at is held by nothing, and the "
            "'Upgrade to +n' spinbox moves no figure at all. This is the "
            "shape QA-055 has: a list computed at a tier that is nowhere on "
            "screen. Measured surviving on 2026-09-03, on the tree before W4 "
            "and with the same edit against `upgrade=self.upgrade.value()`: "
            "264 of 264 tests green. Checkpoint 20 is the assertion it now "
            "fails."),
    ),
    "last-sources-not-assigned": Mutation(
        path="nrplanner/app.py",
        old="""        self.last_sources = dict(build.sources)
""",
        new="""        self.last_sources = {}
""",
        survival_means=(
            "the click-through breakdown loses every source line in the "
            "running program the moment `recompute()` runs, while the test "
            "suite reports nothing: `tests/weapon_damage_cases.run` sets "
            "`last_sources` itself before drawing, so no golden case ever "
            "exercises this assignment inside `recompute()`. Measured "
            "surviving on 2026-09-03: 259 of 259 tests green (QA-076). "
            "Guarded since by test_breakdown_sources_wiring.py, which calls "
            "`recompute()` directly."),
    ),
    "move-scope-constant-emptied": Mutation(
        path="nrplanner/model.py",
        old="""MOVE_SCOPED_EFFECT_IDS = frozenset({
    320600, 8430000, 8851800, 8851850,                    # Thrusting Counter.
    330000, 6611200, 6611201, 6611202,                    # Sorceries
    8330000, 8330001, 8330002,
    330400, 6611300, 6611301, 6611302,                    # Incantations
    8330100, 8330101, 8330102,
    8330103, 8330104, 8851200, 8851250,                   # both at once
})
""",
        new="""MOVE_SCOPED_EFFECT_IDS = frozenset()
""",
        survival_means=(
            "the list itself can be emptied unremarked. This is the literal "
            "edit `move-scope-list-emptied` stands in for behaviourally, and "
            "it is kept beside it because it reaches one guard the other "
            "cannot: test_every_effect_of_the_four_families_is_listed sweeps "
            "the dataset by name against this constant, so it dies only when "
            "the constant moves, never when the lookup that reads it does."),
    ),
    "move-scope-list-emptied": Mutation(
        path="nrplanner/model.py",
        old="""    return effect.get("id") in MOVE_SCOPED_EFFECT_IDS
""",
        new="""    return False
""",
        survival_means=(
            "the list of buffs the game restricts in prose reaches nothing, "
            "which is the state the program was in before QA-018 was "
            "decided: 'Improved Thrusting Counterattack' lifts every swing "
            "by 20% again, and Wylder's Greatsword reads 244 where the game "
            "says 203. Behaviourally identical to writing "
            "`frozenset()` for the list itself, and anchored on the lookup "
            "because the lookup is the one line the list is read through. "
            "Killed since by tests/test_move_scoped_effects.py."),
    ),
    "move-scope-catches-every-unscoped-attack-buff": Mutation(
        path="nrplanner/model.py",
        old="""    return effect.get("id") in MOVE_SCOPED_EFFECT_IDS
""",
        new="""    return any(f in (effect.get("modifiers") or {})
               for f in ELEMENT_ATTACK_RATES)
""",
        survival_means=(
            "nothing bounds the exclusion from the other side. The four "
            "families would be out of the attack rating and so would the 162 "
            "flat buffs beside them -- 'Improved Physical Attack Power' among "
            "them -- and every multiplier a player equips would stop counting "
            "while the sheet went on listing it. The counterpart of "
            "`move-scope-list-emptied`: one mutation makes the list too "
            "small, this one makes it too large, and a guard that catches "
            "only the first says nothing about where the list ends."),
    ),
    "candidate-without-the-multipliers": Mutation(
        path="nrplanner/damage.py",
        old="""    Question.CANDIDATE: True,
""",
        new="""    Question.CANDIDATE: False,
""",
        survival_means=(
            "AD-019 step W6 can be undone by one word and nothing notices. "
            "The arsenal tab would go back to ranking and printing the figure "
            "from below the attack multipliers while the breakdown panel next "
            "door printed the one above them -- QA-018's two numbers for one "
            "armament, restored. Killed since by "
            "test_a_candidate_carries_the_attack_multipliers."),
    ),
    "ranking-left-in-layer-one-order": Mutation(
        path="nrplanner/damage.py",
        old="""    answers.sort(key=lambda answer: (-answer.final_total, answer.weapon["id"]))
    return answers
""",
        new="""    return answers
""",
        survival_means=(
            "`rank_candidates` hands back the order `weapons.rank` produced, "
            "which is descending `WeaponRating.total` -- the layer below the "
            "attack multipliers. Every row would print one number and be "
            "placed by another, and a class-scoped rate would move an "
            "armament's figure without moving its position. Killed since by "
            "test_ranking_answers_the_candidate_question_for_every_armament."),
    ),
    "ranking-without-the-tie-break": Mutation(
        path="nrplanner/damage.py",
        old="""    answers.sort(key=lambda answer: (-answer.final_total, answer.weapon["id"]))
""",
        new="""    answers.sort(key=lambda answer: -answer.final_total)
""",
        survival_means=(
            "do-not rule 29 is unenforced. Armaments that rate alike -- "
            "1 424 of 1 793 of them at Wylder, level 15, MAX_UPGRADE, "
            "measured 2026-09-03 -- would come back in whatever order "
            "`weapons.rank` happened to produce, and a one-ULP move anywhere "
            "upstream (584 of 7 172 records, AD-024) could reshuffle rows a "
            "player cannot tell apart. This is the mutation "
            "`ranking-left-in-layer-one-order` cannot make: there the figures "
            "themselves move, here only equal ones do."),
    ),
}


def newline_of(raw: bytes) -> bytes:
    """The line ending the file already uses.

    `app.py` is CRLF in the working tree and the other modules are LF. A
    mutation that normalised the whole file would show up in every later diff
    as a change nobody made.
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
