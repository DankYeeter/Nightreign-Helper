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
    "arsenal-spinbox-does-not-recalculate": Mutation(
        path="nrplanner/arsenaltab.py",
        old="""        self.upgrade.valueChanged.connect(self.recalculate)
""",
        new="""        self.upgrade.valueChanged.connect(lambda _: None)
""",
        survival_means=(
            "moving the 'Upgrade to +n' spinbox recalculates nothing. Every "
            "tile keeps the figure from whichever tier the tab last "
            "recalculated at, and the spinbox becomes a control that reads "
            "as live and is not (QA-085). Every existing test and the "
            "differential harness call `recalculate()` themselves before "
            "reading a figure, so none of them can see this: it takes a "
            "case that moves the control and reads the render without "
            "calling `recalculate()` in between. Killed since by "
            "test_moving_the_spinbox_alone_repaints_the_tile."),
    ),
    "arsenal-tab-switch-does-not-recalculate": Mutation(
        path="nrplanner/app.py",
        old="""        tabs.currentChanged.connect(
            lambda index: self.weapons_tab.recalculate()
            if tabs.widget(index) is self.weapons_tab else None
        )
""",
        new="""        tabs.currentChanged.connect(lambda index: None)
""",
        survival_means=(
            "bringing the Weapons && spells tab to the front recalculates "
            "nothing. The tab goes on ranking against whichever build was "
            "current the last time it was shown, which is QA-001 returned "
            "in a new shape -- the tab disagreeing with the Build planner "
            "tab beside it, this time because nobody told it the build had "
            "moved rather than because it computed its own. Every existing "
            "test reaches the tab through `recalculate()` or "
            "`current_build()` directly, never by switching tabs, so none "
            "of them can see this. Killed since by "
            "test_switching_to_the_tab_alone_repaints_it_for_the_current_build."),
    ),
    "arsenal-rarity-band-off-by-one": Mutation(
        path="nrplanner/arsenaltab.py",
        old="""            return min(rating.tier_applied - 1, RARITY_TIERS - 1)
""",
        new="""            return min(rating.tier_applied, RARITY_TIERS - 1)
""",
        survival_means=(
            "the rarity filter shows the wrong armaments in every band but "
            "the top one, and the summary count agrees with the wrong list "
            "rather than the right one. Measured on the tree before this "
            "guard existed: at tier 1 the 'Common' band showed 856 "
            "armaments instead of 160 (QA-086 c), and every existing test "
            "stayed green because none of them read the rarity filter or "
            "the section count. Killed since by "
            "test_the_rarity_filter_agrees_with_the_section_count."),
    ),
    "arsenal-tile-type-row-duplicated": Mutation(
        path="nrplanner/arsenaltab.py",
        old="""                for damage_type, value in rating.final_per_type.items():
                    lines.append((weapons.DAMAGE_LABELS[damage_type],
                                  f"{value:.0f}"))
""",
        new="""                for damage_type, value in rating.final_per_type.items():
                    lines.append((weapons.DAMAGE_LABELS[damage_type],
                                  f"{value:.0f}"))
                    lines.append((weapons.DAMAGE_LABELS[damage_type],
                                  f"{value:.0f}"))
""",
        survival_means=(
            "a multi-type tile carries a duplicate row for every damage "
            "type it deals, and nothing on the tab or in the suite reads "
            "far enough down a tile to notice (QA-086 a) -- the AR-only "
            "guard from AD-019 W4/QA-083 stops at the headline row. Killed "
            "since by "
            "test_every_type_row_and_the_upgrade_line_match_the_facade."),
    ),
    "arsenal-upgraded-to-names-the-wrong-tier": Mutation(
        path="nrplanner/arsenaltab.py",
        old="""                if rating.tier_applied > own_tier:
                    lines.append(("Upgraded to", f"+{reached} "
                                                 f"{RARITY_NAMES.get(reached - 1, '')}"))
""",
        new="""                if rating.tier_applied > own_tier:
                    lines.append(("Upgraded to", f"+{weapons.MAX_UPGRADE} "
                                                 f"{RARITY_NAMES.get(weapons.MAX_UPGRADE - 1, '')}"))
""",
        survival_means=(
            "the 'Upgraded to' line names the dataset's own maximum tier "
            "for every upgraded armament, regardless of the tier it was "
            "actually rated at (QA-086 b) -- '+4 Legendary' shown for an "
            "armament rated to +3 Rare. Killed since by "
            "test_every_type_row_and_the_upgrade_line_match_the_facade."),
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
