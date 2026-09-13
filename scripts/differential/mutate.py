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
    "reading-takes-is-debuff-for-curse": Mutation(
        path="nrplanner/model.py",
        old="""        (CONDITIONAL_CURSE_IDS if effect.get("is_curse")
         else CONDITIONAL_BUFF_IDS).add(effect["id"])
""",
        new="""        (CONDITIONAL_CURSE_IDS if effect.get("is_debuff")
         else CONDITIONAL_BUFF_IDS).add(effect["id"])
""",
        survival_means=(
            "the worst case would declare every conditional debuff (78 ids "
            "carry `is_debuff`, not all of them curses) and miss the curses "
            "that are not debuffs, and no test reads the seven ids back. "
            "Killed by `test_reading_defaults_name_the_seven_conditional_"
            "curses_and_nothing_else` (T-224)."),
    ),
    "worst-case-declares-the-buffs": Mutation(
        path="nrplanner/model.py",
        old="""    return dict.fromkeys(CONDITIONAL_CURSE_IDS if worst
                         else CONDITIONAL_BUFF_IDS, 1)
""",
        new="""    return dict.fromkeys(CONDITIONAL_BUFF_IDS if worst
                         else CONDITIONAL_CURSE_IDS, 1)
""",
        survival_means=(
            "the two readings are swapped: `Worst case` counts every "
            "conditional buff and `Best case` every conditional curse, the "
            "opposite of `GOAL.md` A16, and the sum of AK-187 still holds. "
            "Killed by the seven-ids case and by `test_the_worst_case_moves_"
            "the_ranking_where_a_conditional_curse_sits` (T-224)."),
    ),
    "reading-overwrites-the-declaration": Mutation(
        path="nrplanner/advisorbar.py",
        old="""    declared = tuple(sorted({**model.reading_defaults(planner.worst_case),
                             **planner.declared}.items()))
""",
        new="""    declared = tuple(sorted({**planner.declared,
                             **model.reading_defaults(planner.worst_case)}.items()))
""",
        survival_means=(
            "the reading wins over the player's own declaration: `I carry 3 "
            "bows` becomes 1 in the best case and the advisor's figure "
            "disagrees with the stat sheet beside it (AK-186's Rot-vorher). "
            "Killed by `test_a_declared_condition_outlives_both_readings` "
            "(T-224)."),
    ),
    "reading-change-starts-a-run": Mutation(
        path="nrplanner/advisorbar.py",
        old="""        self.reading_changed.emit(self.reading_box.currentData())
        self.the_build_changed()
""",
        new="""        self.reading_changed.emit(self.reading_box.currentData())
        self.the_build_changed()
        self._ask()
""",
        survival_means=(
            "switching the reading spends a search nobody asked for, whose "
            "cost was never measured (AK-183's Rot-vorher, §5.1). Killed by "
            "`test_the_reading_is_a_second_box_that_puts_the_answer_away_"
            "and_asks_nothing` (T-224)."),
    ),
    "e1-headline-ignores-the-origin": Mutation(
        path="nrplanner/firstrun.py",
        old="""        headline=("That folder does not hold a copy of the game." if inside
                  else "That folder is not part of a Steam installation."),
""",
        new="""        headline="That folder does not hold a copy of the game.",
""",
        survival_means=(
            "a folder turned down for lying outside every Steam library is "
            "called `not a copy of the game`, which it may well be (AK-264). "
            "Killed by `test_e1_says_when_the_folder_lies_outside_every_"
            "steam_library` and the flow case beside it (T-225)."),
    ),
    "wanted-height-is-read-afresh": Mutation(
        path="nrplanner/relicpicker.py",
        old="""        if self._wanted is None:
            return self._chrome_height() + self._room_for_three_rows(cards)
        return self._wanted
""",
        new="""        return self._chrome_height() + self._room_for_three_rows(cards)
""",
        survival_means=(
            "`wanted_height` after the answer is 90 px above the height the "
            "dialog gave itself (QA-242, AK-266). Killed by `test_the_height_"
            "asked_for_is_the_figure_of_the_sizing_and_stays_it` (T-225)."),
    ),
    "cards-keep-the-stock-of-a-save-no-longer-held": Mutation(
        path="nrplanner/app.py",
        old="""        self._hand_the_stock_to_the_slots()
        self._say_how_many_relics_are_owned()
""",
        new="""        if self.owned is not None:
            self._hand_the_stock_to_the_slots()
        self._say_how_many_relics_are_owned()
""",
        survival_means=(
            "a rescan that finds no save leaves the cards holding the old "
            "relics while the header says no save was read (AK-267, QA-247). "
            "Killed by `test_a_rescan_that_finds_no_save_takes_the_cards_out_"
            "of_the_picker` and `test_a_picker_standing_open_loses_its_cards_"
            "with_the_save` (T-225)."),
    ),
    "goal-box-400-px": Mutation(
        path="nrplanner/advisorbar.py",
        old="""        self.goal_box.setMaximumWidth(GOAL_BOX_WIDTH)
""",
        new="""        self.goal_box.setFixedWidth(400)
""",
        survival_means=(
            "the status has no width at the opening width and nothing "
            "measured it at the running window (AK-05, AK-194). Killed by "
            "`test_at_the_opening_width_only_the_status_is_shortened` and "
            "`test_at_the_opening_width_the_status_keeps_some_width` (T-225)."),
    ),
    "reading-box-stays-live-without-a-save": Mutation(
        path="nrplanner/advisorbar.py",
        old="""        self.goal_box.setEnabled(answerable)
        self.reading_box.setEnabled(answerable)
        self.optimize_button.setEnabled(answerable)
""",
        new="""        self.goal_box.setEnabled(answerable)
        self.optimize_button.setEnabled(answerable)
""",
        survival_means=(
            "4.8 leaves a reading to choose with nothing to read (AK-268). "
            "Killed by `test_without_a_save_the_row_says_so_and_disables_its_"
            "own_two_controls` (T-225)."),
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
