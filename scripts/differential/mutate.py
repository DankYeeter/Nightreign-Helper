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
    "row-tooltip-left-empty": Mutation(
        path="nrplanner/advisorbar.py",
        old="""        self.setToolTip(self.status.toolTip())
""",
        new="""        self.setToolTip("")
""",
        survival_means=(
            "on a desktop that caps the opening width the status shrinks to "
            "0 px (QA-250) and its sentence is then nowhere to be hovered. "
            "Killed by `test_on_a_narrow_desktop_the_boxes_keep_their_"
            "captions_and_the_row_carries_the_status` (T-230a)."),
    ),
    "open-picker-keeps-the-answer-over-a-replaced-stock": Mutation(
        path="nrplanner/relicpicker.py",
        old="""        slot.stock_replaced.connect(self._the_stock_was_replaced)
""",
        new="""        slot.stock_replaced.connect(self._refresh)
""",
        survival_means=(
            "a dialog standing open through a rescan keeps the track's "
            "answer about the stock that has gone and says `ranked against "
            "your build` over an empty grid (DR-022). Killed by `test_a_"
            "picker_standing_open_falls_back_to_the_state_before_any_save` "
            "(T-230b)."),
    ),
    "dcx-size-mismatch-is-a-bare-valueerror": Mutation(
        path="nrdata/dcx.py",
        old="""    if len(out) != uncompressed_size:
        raise NotWhatItClaims(
""",
        new="""    if len(out) != uncompressed_size:
        raise ValueError(
""",
        survival_means=(
            "a DCX whose payload belies its header reaches the surface as "
            "`Something went wrong that this program has no sentence for "
            "(ValueError).` instead of its own sentence (QA-232, A7). Killed "
            "by `test_a_dcx_whose_payload_belies_its_header_is_refused_in_"
            "its_own_words` (T-230c)."),
    ),
    "tpf-refusal-quotes-the-member-name": Mutation(
        path="nrdata/tpf.py",
        old="""                f"TPF member {index} claims {file_size} bytes at offset "
""",
        new="""                f"TPF member {name!r} claims {file_size} bytes at offset "
""",
        survival_means=(
            "a buffer-long string out of a game file is quoted verbatim on "
            "the surface again (SEC-043, SEC-019 class). Killed by `test_a_"
            "tpf_member_is_refused_by_its_index_and_not_by_its_name` and by "
            "`test_no_refusal_quotes_what_a_game_file_wrote` (T-230d)."),
    ),
    "asking-takes-the-other-reading": Mutation(
        path="nrplanner/advisorbar.py",
        old="""    declared = tuple(sorted({**model.reading_defaults(planner.worst_case),
""",
        new="""    declared = tuple(sorted({**model.reading_defaults(not planner.worst_case),
""",
        survival_means=(
            "the run is asked under the reading the player did not choose: "
            "`Worst case` declares the conditional buffs and moves copies "
            "without a curse. Killed by `test_the_worst_case_moves_the_"
            "counted_copies_of_the_frozen_save` on any machine, and by the "
            "live-save case on this one (T-230e)."),
    ),
    "cancel-waits-for-the-worker": Mutation(
        path="nrplanner/advisor/worker.py",
        old="""        self._interrupt_the_running_worker()
        self.stopped.emit()
""",
        new="""        self._interrupt_the_running_worker()
        if self._thread is not None:
            self._thread.wait()
        self.stopped.emit()
""",
        survival_means=(
            "the window is told it has stopped only once the worker has "
            "finished, however long that takes (AK-11 broken). A worker that "
            "was through its scorings before the cancel could not show it; "
            "one held inside a scoring can. Killed by `test_cancel_is_"
            "visible_at_once_however_long_the_worker_takes` (T-230f)."),
    ),
    "status-reports-the-ellipsis-to-the-bridge": Mutation(
        path="nrplanner/advisorbar.py",
        old="""        self.setAccessibleName(text)
        self.setAccessibleDescription(text)
""",
        new="""        self.setAccessibleName("")
        self.setAccessibleDescription("")
""",
        survival_means=(
            "a screen reader is read the elided `text()` -- one word and an "
            "ellipsis at 67 px -- and a keyboard user has no way to the "
            "sentence at all (DR-023). Killed by `test_a_shortened_status_"
            "keeps_its_whole_sentence_for_the_accessibility_bridge` (T-230g)."),
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
