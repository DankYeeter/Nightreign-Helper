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
        old="""                lines = [(rating.headline_label,
                          f"{damage.displayed(rating.final_headline)}")]
""",
        new="""                lines = [(rating.headline_label,
                          f"{damage.displayed(rating.final_headline * 0.5)}")]
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
    "arsenal-summary-reads-the-slider": Mutation(
        path="nrplanner/arsenaltab.py",
        old="""        build = self.planner.current_build()
        # From the build and not from the slider: they agree in the running
        # program, and for a tool that sets a build directly they do not --
        # this line used to make every arsenal record of the differential
        # track say "level 1" whatever it was measuring (QA-124).
        level = build.level
""",
        new="""        build = self.planner.current_build()
        level = self.planner.level_slider.value()
""",
        survival_means=(
            "the level in the tab's summary line comes from a widget and the "
            "figures beside it from a build, and nothing holds the two "
            "together. In the running program they never differ; for a tool "
            "that sets `planner._build` directly they always do, and this "
            "track is such a tool -- every arsenal record it wrote before "
            "T-048 says 'level 1' whatever level it was measuring (QA-124, "
            "the root of QA-088 a). What that costs is not a wrong figure "
            "but a wrong label on a right one, in the records this "
            "repository argues from. Killed by "
            "test_arsenal_tab_asks_the_facade.py::"
            "test_the_summary_names_the_level_the_build_was_computed_at -- "
            "and on the first run of this entry it was not: the slider sits "
            "at level 15, the build was computed at level 1, and 'at level "
            "1' is a substring of 'at level 15'. The case matches the comma "
            "after the number now. Worth keeping in the file: a "
            "counter-build's first job is to find the case that does not "
            "hold, and this one did."),
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
        old="""    answers.sort(key=lambda answer: (-answer.final_headline,
                                     answer.weapon["id"]))
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
        old="""                for damage_type, value in rating.shown_per_type.items():
                    lines.append((weapons.DAMAGE_LABELS[damage_type],
                                  f"{damage.displayed(value)}"))
""",
        new="""                for damage_type, value in rating.shown_per_type.items():
                    lines.append((weapons.DAMAGE_LABELS[damage_type],
                                  f"{damage.displayed(value)}"))
                    lines.append((weapons.DAMAGE_LABELS[damage_type],
                                  f"{damage.displayed(value)}"))
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
    # -- the build advisor (T-037: S4, S4b, S5, S6) -------------------------
    #
    # The advisor's guards are young and its failures are quiet ones: a
    # pre-sort measured against the wrong base state does not crash, it
    # produces a plausible order. Each entry below is one of those.
    "advisor-computes-in-a-second-place": Mutation(
        path="nrplanner/advisor/candidates.py",
        old="""    base_build = evaluate(base_problem, (), ctx)
""",
        new="""    from .. import model
    base_build = model.compute(ctx.hero, ctx.level, [],
                               ctx.data.get("curves", {}))
""",
        survival_means=(
            "AD-014.1 is unenforced: the advisor may reach `model.compute` "
            "from more than one place, and each of those places can forget "
            "the held slots on its own. The base state written here forgets "
            "them -- every candidate would then be ranked against the empty "
            "build while the search ran against the held one. Killed by "
            "test_one_build.py::"
            "test_the_user_interface_holds_exactly_one_call_to_compute, "
            "whose expectation grew by exactly one entry for evaluate.py."),
    ),
    "advisor-presorts-against-the-empty-build": Mutation(
        path="nrplanner/advisor/candidates.py",
        old="""    base_problem = base_state_for(problem, slot_index)
""",
        new="""    base_problem = types.SlotProblem(slots=problem.slots)
""",
        survival_means=(
            "do-not rule 13 is unenforced. The pre-sort would run against "
            "the empty build with something held, which recommends "
            "candidates whose contribution the held relic already caps: the "
            "score does not move and the suggestion still looks plausible. "
            "Killed by test_advisor_candidates.py::"
            "test_a_candidate_is_measured_against_the_held_build, which "
            "holds an isStrongestEffect and offers a second copy of it."),
    ),
    "advisor-ranks-the-slot-as-it-stands": Mutation(
        path="nrplanner/advisor/candidates.py",
        old="""    kept = tuple(entry for entry in problem.held if entry.index != slot_index)
""",
        new="""    kept = problem.held
""",
        survival_means=(
            "AD-018.1 is unenforced: the slot being ranked keeps its own "
            "hold, so the relic already in it is measured against a build "
            "that still contains it and scores zero. Every relic the player "
            "already owns in place would read as worthless, which is the one "
            "figure the picker exists to give. Killed by "
            "test_advisor_candidates.py::"
            "test_the_relic_in_the_slot_is_worth_what_it_actually_adds."),
    ),
    "advisor-offers-a-relic-without-a-handle": Mutation(
        path="nrplanner/advisor/candidates.py",
        old="""        if relic.handle is None or relic.handle in taken:
            continue
""",
        new="""        if relic.handle in taken:
            continue
""",
        survival_means=(
            "AD-013 point 4 is unenforced. A save whose loadout table cannot "
            "be read yields no handles at all, and copy identity would then "
            "be given up for exactly the relics it cannot be checked for -- "
            "a suggestion naming one could not be applied to a slot. Killed "
            "by test_advisor_candidates.py::"
            "test_a_copy_without_a_handle_is_not_offered_and_is_reported."),
    ),
    "advisor-leaves-a-relic-out-without-saying-so": Mutation(
        path="nrplanner/advisor/candidates.py",
        old="""    lines = []
    if without_handle:
        lines.append(_without_a_handle_line(without_handle))
""",
        new="""    lines = []
""",
        survival_means=(
            "the other half of AD-013 point 4, and `GOAL.md` A7 with it: the "
            "copies are correctly left out and nothing says so, leaving the "
            "player to look for a relic they own and cannot find in the "
            "list. Killed by test_advisor_candidates.py::"
            "test_a_copy_without_a_handle_is_not_offered_and_is_reported, "
            "which asserts both halves rather than only the filter."),
    ),
    "advisor-forgets-the-held-handles": Mutation(
        path="nrplanner/advisor/candidates.py",
        old="""    taken = types.held_handles(base_problem)
""",
        new="""    taken = frozenset()
""",
        survival_means=(
            "AD-014.5 is unenforced: a copy the player is holding is offered "
            "for a second slot as well. On a vessel with two slots of one "
            "colour that is the shape AD-013 measured on `Wylder's Urn` -- "
            "40 of 40 suggestions unusable, the best one included, and all "
            "of them with a plausible score. Killed by "
            "test_advisor_candidates.py::"
            "test_a_held_copy_is_not_offered_a_second_time."),
    ),
    "advisor-scores-only-the-ranking-goal": Mutation(
        path="nrplanner/advisor/candidates.py",
        old="""        marginals = tuple(
            types.Marginal(goal_id, goal.score(build, ctx).value
                           - base_scores[goal_id].value)
            for goal_id, goal in goals.items()
        )
""",
        new="""        marginals = (types.Marginal(
            rank_by, goals[rank_by].score(build, ctx).value
            - base_scores[rank_by].value),)
""",
        survival_means=(
            "AD-018 point 2 and AD-023/OF-13 are unenforced. Only the sorted "
            "direction would carry a figure, so a relic that costs survival "
            "to buy damage could not be shown costing anything -- and the "
            "only remaining way to show it would be a weighted single "
            "number, which is the invented exchange rate A7 forbids. Killed "
            "by test_advisor_candidates.py::"
            "test_every_candidate_carries_both_directions."),
    ),
    "advisor-marginals-as-a-mutable-map": Mutation(
        path="nrplanner/advisor/candidates.py",
        old="""        measured.append(dataclasses.replace(candidate, marginals=marginals))
""",
        new="""        measured.append(dataclasses.replace(candidate,
                                            marginals=list(marginals)))
""",
        survival_means=(
            "QA-066 reaches the advisor after all: a `frozen` dataclass "
            "handed a mutable sequence is frozen in name and shared in fact, "
            "and AD-018 memoises marginal contributions. A **list** rather "
            "than a dict on purpose -- every lookup, every sort and every "
            "figure goes on working, so this changes exactly one thing, "
            "whether the result can be a cache key, and the failure would "
            "otherwise first show in S9 where the key is formed. Killed by "
            "test_advisor_candidates.py::"
            "test_a_pool_the_advisor_produced_can_be_a_cache_key, which "
            "hashes what the pool really produced rather than reading its "
            "annotations."),
    ),
    "advisor-shortlist-without-room-for-the-others": Mutation(
        path="nrplanner/advisor/candidates.py",
        old="""    room = budget.candidates_per_slot + free_slot_count - 1
""",
        new="""    room = budget.candidates_per_slot
""",
        survival_means=(
            "S5+/AD-013 point 3 is unenforced. The search takes the first K "
            "**available** candidates, so every copy taken by an earlier "
            "slot narrows the branching at the deeper ones -- quietly, and "
            "worst where the vessel repeats a colour, which is where the "
            "ownership rule bites hardest. Killed by "
            "test_advisor_candidates.py::"
            "test_the_shortlist_leaves_room_for_the_copies_the_other_slots_take."),
    ),
    "damage-goal-ranks-on-the-bare-figure": Mutation(
        path="nrplanner/advisor/goals.py",
        old="""    _bare, now = damage.equipped(ctx.reference, ctx.reference.slot_index,
                                 build, ctx.hero, ctx.data)
""",
        new="""    now, _later = damage.equipped(ctx.reference, ctx.reference.slot_index,
                                  build, ctx.hero, ctx.data)
""",
        survival_means=(
            "the damage goal ranks on the breakdown panel's left-hand "
            "column -- the armament with nothing equipped. Every relic that "
            "buffs an attack rate rather than an attribute would be worth "
            "exactly nothing, and the advisor would value a build's whole "
            "multiplier stack at zero while the panel beside it printed the "
            "multipliers (AD-019 step W6, QA-018). Killed by "
            "test_advisor_goals.py::"
            "test_the_damage_goal_counts_the_attack_multipliers."),
    ),
    "damage-goal-asks-the-slotless-question": Mutation(
        path="nrplanner/advisor/goals.py",
        old="""    _bare, now = damage.equipped(ctx.reference, ctx.reference.slot_index,
                                 build, ctx.hero, ctx.data)
""",
        new="""    now = damage.candidate(ctx.reference.weapon, ctx.reference.tier,
                           build, ctx.data)
""",
        survival_means=(
            "the damage goal asks `candidate()` -- an armament in no slot -- "
            "where the weapon panel asks `equipped()`. With no slot there is "
            "no starting-armament pairing, so the 0.85 the game charges for "
            "'Starting armament inflicts frost' and its two relatives "
            "disappears from the figure (AD-020 point 3). This entry used to "
            "say the **order** survived because the penalty is a constant "
            "factor over every candidate. That is measurably wrong, and the "
            "sentence stood in this repository being read as settled until "
            "the `qa-engineer` disproved it (QA-101): a candidate can bring "
            "the penalty **with it**. Three effects carry "
            "`*AttackPowerRate` 0.85 themselves (7120400/500/600), and 10 of "
            "the 309 relics on the save measured against carry one. "
            "Re-measured 2026-09-05, Wylder level 15, his own starting "
            "armament in slot 1 at tier 1: `[7120400, 6001400]` gains "
            "-7.4146 as `equipped` and +12.8153 as `candidate`, `[7000300]` "
            "gains +0.4977 either way -- the two change places. So this "
            "mutation moves the order as well as the figure, and `equipped` "
            "is the more right of the two rather than merely the more exact: "
            "a relic that costs the armament 15 % belongs ranked as costing "
            "it. Killed by test_advisor_goals.py::"
            "test_the_damage_goal_charges_the_starting_armament_penalty, "
            "which holds the amount; the order is held by "
            "test_the_damage_goal_ranks_a_self_inflicted_penalty_below."),
    ),
    "advisor-key-forgets-the-held-state": Mutation(
        path="nrplanner/advisor/types.py",
        old="""    slots: tuple[Slot, ...] = ()
    held: tuple[HeldSlot, ...] = ()
""",
        new="""    slots: tuple[Slot, ...] = ()
    held: tuple[HeldSlot, ...] = ()

    def __eq__(self, other) -> bool:
        return type(other) is type(self) and self.slots == other.slots

    def __hash__(self) -> int:
        return hash(self.slots)
""",
        survival_means=(
            "the held state stops reaching the cache key, and AD-016.2 is "
            "unenforced in the one way that costs the feature rather than a "
            "measurement: a run answers out of the cache of a run that held "
            "something else, and the suggestion it hands back overwrites a "
            "slot the player deliberately held. It is written as an explicit "
            "`__eq__`/`__hash__` pair because that is the shape the mistake "
            "would really take -- somebody deciding that two vessels with "
            "the same slots are the same question -- and because "
            "`dataclasses` respects a pair written into the class body. "
            "This is checkpoint 34's counter-build and it replaces "
            "`advisor-fingerprint-sorted-naturally`, which mutated a derived "
            "form that no longer exists (QA-107). Killed by "
            "test_advisor_types.py, three cases: the two requests that "
            "differ in what is held, the two that differ in where, and the "
            "slot held empty against the free one -- they are three "
            "distinctions the key has to make, not one assertion said three "
            "times."),
    ),
    "advisor-rates-an-armament-itself": Mutation(
        path="nrplanner/advisor/goals.py",
        old="""    rates = [build.rates.get(field_name, 1.0)
             for field_names in damage.AR_RATE_FOR.values()
             for field_name in field_names]
""",
        new="""    from .. import weapons
    _own_arithmetic = weapons.rate
    rates = [build.rates.get(field_name, 1.0)
             for field_names in damage.AR_RATE_FOR.values()
             for field_name in field_names]
""",
        survival_means=(
            "the AD-021 assurance does not reach the advisor package, and the "
            "one thing `docs/state.md` promised would be enforced "
            "automatically once `nrplanner/advisor/` existed is not. A "
            "second armament arithmetic under advisor/ would then be free to "
            "grow, and the advisor's figure could part company with the "
            "weapon panel's the way QA-018's two numbers for one armament "
            "did. A reference and not a call on purpose: the guard counts "
            "references, and a call here would crash the run instead of "
            "failing the guard, which proves something else. Killed by "
            "test_one_build.py::"
            "test_only_the_facade_calls_weapons_rate_or_rank."),
    ),
    # -- the seven arguments of one build (T-048: QA-100) -------------------
    #
    # Five edits, one per input the advisor hands `model.compute` and that a
    # shorter argument list could drop. QA-001 was exactly that -- a second,
    # shorter list -- and checkpoint 13 exists to catch its return. It caught
    # none of these until T-048, because the state it compared was hollowed
    # out: level 1, one armament which was also the reference, nothing
    # declared, Deep off, and Wylder, who is `heroes[0]`.
    "advisor-computes-without-the-armaments-held": Mutation(
        path="nrplanner/advisor/evaluate.py",
        old="""        weapons_held=list(ctx.weapons_held),
""",
        new="""        weapons_held=[],
""",
        survival_means=(
            "the advisor rates a build against the armament it is looking at "
            "instead of against the grid the player is carrying. A "
            "weapon-type gate is met by any armament held, not only by the "
            "one being rated (`model.satisfied_by_weapon`), so every effect "
            "gated on one of the other five tiles would silently stop "
            "counting -- and the stat sheet beside it would go on counting "
            "them. That is QA-001 in a new place: two figures for one build, "
            "with nothing on the window to say which is right. Measured "
            "surviving on 2026-09-03 by the `qa-engineer`: 398 passed, 5 "
            "deselected. Killed by test_advisor_evaluate.py::"
            "test_the_advisor_computes_the_build_the_window_shows."),
    ),
    "advisor-computes-without-the-reference-armament": Mutation(
        path="nrplanner/advisor/evaluate.py",
        old="""        weapon=reference.weapon if reference is not None else None,
""",
        new="""        weapon=None,
""",
        survival_means=(
            "the reference armament does not reach the model. **Today this "
            "changes no build at all**, and that is the finding rather than "
            "an excuse: `model.compute` reads `weapon` only where "
            "`weapons_held` is empty, and both are filled from the same grid "
            "in both callers, so the branch is unreachable from the window. "
            "A comparison of builds therefore cannot see this edit -- "
            "measured, not assumed -- and the case that kills it reads the "
            "call instead of its result. It matters because S9 builds the "
            "`GoalContext` in a worker: a context with a reference and no "
            "grid is one line away, and the guard has to be there before it "
            "is written. Killed by test_advisor_evaluate.py::"
            "test_evaluate_hands_the_whole_context_to_the_model."),
    ),
    "advisor-computes-at-the-first-level": Mutation(
        path="nrplanner/advisor/evaluate.py",
        old="""        ctx.level,
        _effects(ctx, effect_ids_of(problem, assignment, ctx)),
""",
        new="""        1,
        _effects(ctx, effect_ids_of(problem, assignment, ctx)),
""",
        survival_means=(
            "the advisor ranks relics for a level-1 Nightfarer whatever the "
            "player is. Every attribute bonus would feed a curve at the "
            "bottom of its first segment, so the marginal contribution of "
            "every +attribute relic would be the wrong size -- and the "
            "ordering would look plausible throughout. It survived until "
            "T-048 for a reason worth keeping in view: the case that should "
            "have caught it never moved the level slider, whose minimum is "
            "1. Killed by test_advisor_evaluate.py::"
            "test_the_advisor_computes_the_build_the_window_shows."),
    ),
    "advisor-computes-for-the-first-nightfarer": Mutation(
        path="nrplanner/advisor/evaluate.py",
        old="""    return model.compute(
        ctx.hero,
""",
        new="""    return model.compute(
        ctx.data["heroes"][0],
""",
        survival_means=(
            "every run is answered for Wylder. The base attributes, the "
            "hero-specific effects and the starting-armament pairing all "
            "follow the Nightfarer, so a Recluse player would be shown a "
            "ranking for somebody else's build -- and `heroes[0]` is the one "
            "substitution no synthetic case in this package could see, "
            "because all of them ask about Wylder. Killed by "
            "test_advisor_evaluate.py::"
            "test_the_advisor_computes_the_build_the_window_shows."),
    ),
    "advisor-computes-with-nothing-declared": Mutation(
        path="nrplanner/advisor/evaluate.py",
        old="""        declared=dict(ctx.declared),
""",
        new="""        declared={},
""",
        survival_means=(
            "a condition the player has switched on counts on the stat sheet "
            "and not in the ranking. A situational relic would then sit at "
            "0.00 in the picker while the sheet beside it counts the effect "
            "three times -- the two halves of one screen contradicting each "
            "other, and the shape AD-004's conditional line exists to "
            "explain rather than to cause. Killed by "
            "test_advisor_evaluate.py::"
            "test_the_advisor_computes_the_build_the_window_shows."),
    ),
    # -- the two classes of reservation (T-048: AD-025, QA-102) -------------
    #
    # Three edits, because AD-025 makes three separate promises and a guard
    # that caught only one would leave the others unheld: that the registry
    # states a scope at all, that no sentence is told twice, and that a
    # sentence which holds whatever the run is not filed as a finding of one.
    "advisor-goal-without-its-scope": Mutation(
        path="nrplanner/advisor/goals.py",
        old="""MIN_DAMAGE_TAKEN = types.Goal(
    id="min_damage_taken",
    label="Minimise damage taken",
    blurb="Ranks by how much punishment the build absorbs.",
    scope=_DAMAGE_TAKEN_SCOPE,
""",
        new="""MIN_DAMAGE_TAKEN = types.Goal(
    id="min_damage_taken",
    label="Minimise damage taken",
    blurb="Ranks by how much punishment the build absorbs.",
    scope=(),
""",
        survival_means=(
            "`GOAL.md` A7 rests on the drawing again. The figure would go to "
            "the screen with nothing saying that ailment resistance is not "
            "in it and that the weighting between the eight damage kinds is "
            "an assumption nothing in the game files supports -- which is "
            "exactly the static-warning arrangement AD-010 rejected. This "
            "is checkpoint 29's counter-build, and it is the one mutation of "
            "the advisor that a runner with no game installed can catch: the "
            "case that kills it takes no fixture. Killed by "
            "test_advisor_goals.py::"
            "test_no_direction_carries_an_empty_scope[min_damage_taken]."),
    ),
    "advisor-scope-sentence-repeated-as-a-run-finding": Mutation(
        path="nrplanner/advisor/goals.py",
        old="""            unknowns=(_NO_ARMAMENT,),
""",
        new="""            unknowns=(_NO_ARMAMENT, _ATTACK_RATING_SCOPE[0]),
""",
        survival_means=(
            "AD-025.4 is unheld and one sentence may stand in both classes. "
            "The player would read where the attack rating agrees with the "
            "game twice on one screen -- once outside the cards, where the "
            "registry's scope is drawn, and once on the card as something "
            "this particular run left out -- with two justifications behind "
            "one sentence. That is the repetition AK-50 is written against, "
            "arriving through the door AD-025 built to keep it out. Chosen "
            "in the branch without a reference armament on purpose: it "
            "leaves checkpoint 31 green, so the two checkpoints are told "
            "apart by their own counter-builds. Killed by "
            "test_advisor_goals.py::"
            "test_no_sentence_stands_in_both_classes[max_damage]."),
    ),
    "advisor-run-finding-that-outlives-every-run": Mutation(
        path="nrplanner/advisor/goals.py",
        old="""        unit="effective HP",
        weights_note=ctx.weighting.note,
""",
        new="""        unit="effective HP",
        unknowns=("Effective HP is not a figure the game displays.",),
        weights_note=ctx.weighting.note,
""",
        survival_means=(
            "a sentence that is true of every run can be filed as a finding "
            "of one, and the split AD-025 rests on stops being enforced by "
            "anything but care. Six pools of a Deep vessel would then repeat "
            "it six times where the registry would have drawn it once "
            "(AK-50), and the yardstick -- can the sentence be written "
            "before the run is known? -- would be back to being a matter of "
            "how carefully somebody read it. The sentence written here is "
            "deliberately **not** one of the four in `_DAMAGE_TAKEN_SCOPE`: "
            "if it were, checkpoint 30 would catch it first and this "
            "counter-build would say nothing about checkpoint 31. Killed by "
            "test_advisor_goals.py::"
            "test_a_run_finding_does_not_survive_every_run[min_damage_taken]."),
    ),
    "advisor-pool-keeps-only-the-figure": Mutation(
        path="nrplanner/advisor/candidates.py",
        old="""        baseline=tuple(types.Baseline(goal_id, score.value, score.unit,
                                      score.unknowns, score.weights_note)
                       for goal_id, score in base_scores.items()),
""",
        new="""        baseline=tuple(types.Baseline(goal_id, score.value)
                       for goal_id, score in base_scores.items()),
""",
        survival_means=(
            "the state QA-102 found: `pool()` scores the base state and "
            "keeps the number alone, so everything the direction said about "
            "this run stops at the pool boundary. A7 would then hold "
            "everywhere except on the one path AD-018 says the player uses "
            "to 100 % -- the picker -- where a run without a reference "
            "armament would show a ratio with nothing saying it is one. "
            "Killed by test_advisor_candidates.py::"
            "test_the_pool_carries_what_the_direction_could_not_know."),
    ),
    "advisor-counts-conditions-it-did-count": Mutation(
        path="nrplanner/advisor/candidates.py",
        old="""    return any(entry.effect_id in brought and not entry.live
               for entry in build.situational)
""",
        new="""    return any(entry.effect_id in brought
               for entry in build.situational)
""",
        survival_means=(
            "the conditional line stops describing what the calculation did "
            "and starts describing what the relics carry -- the counterpart "
            "of AD-015's rule for curses, which is that a condition the "
            "calculation *applied* must not be shown as though it had not. A "
            "player who declares a condition live would still be told the "
            "relic was left out, while the figure beside it counts the "
            "effect in full: the two halves of one screen contradicting each "
            "other. This is the shortest edit that produces the failure "
            "`ARCHITECTURE.md` checkpoint 33 names -- the literal 'second "
            "derivation over the relic definitions' cannot be written here "
            "at all, because this function holds no dataset to read them "
            "from, which is the design working rather than a gap in the "
            "counter-build. Killed by test_advisor_candidates.py::"
            "test_the_conditional_line_counts_what_was_really_left_out."),
    ),
    "advisor-counts-the-held-bundle-s-conditions": Mutation(
        path="nrplanner/advisor/candidates.py",
        old="""    brought = set(candidate.effect_ids) | set(candidate.curse_ids)
""",
        new="""    brought = {entry.effect_id for entry in build.situational}
""",
        survival_means=(
            "the count stops being a count of *this pool's* candidates and "
            "picks up whatever the held bundle and the armaments brought "
            "with them (AD-004.4). The number would then match nothing the "
            "player can count on the screen -- four situational relics in "
            "the list, seven in the line -- and the line exists precisely so "
            "that the figure and the list agree. Killed by "
            "test_advisor_candidates.py::"
            "test_the_conditional_line_counts_this_pool_and_not_the_held_"
            "bundle."),
    ),
    "ranking-without-the-tie-break": Mutation(
        path="nrplanner/damage.py",
        old="""    answers.sort(key=lambda answer: (-answer.final_headline,
                                     answer.weapon["id"]))
""",
        new="""    answers.sort(key=lambda answer: -answer.final_headline)
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
    # -- the game's own number (T-045: QA-095) ------------------------------
    #
    # Two edits, because the calibration is two decisions and a guard that
    # caught only one would leave the other unheld: what the factor is, and
    # what the display does with the fraction that is left over.
    "attack-power-rate-neutralised": Mutation(
        path="nrplanner/weapons.py",
        old="""GAME_ATTACK_POWER_RATE = 0.6
""",
        new="""GAME_ATTACK_POWER_RATE = 1.0
""",
        survival_means=(
            "nothing holds the program's attack rating to the game's. This "
            "is the state the program was in until T-045: every figure on "
            "every tile, in the panel, on the arsenal tab and in the "
            "advisor's goal line 1/0.6 = 1.667 times what the game shows, "
            "with the ordering intact -- which is why no test could see it "
            "from the inside. Killed by "
            "tests/test_attack_power_against_the_game.py, all 23 readings."),
    ),
    "attack-power-rounded-instead-of-truncated": Mutation(
        path="nrplanner/damage.py",
        old="""    return math.floor(figure)
""",
        new="""    return round(figure)
""",
        survival_means=(
            "the second half of QA-095 is unheld: the game **truncates** the "
            "attack rating and rounding it would be off by one wherever the "
            "fraction reaches a half -- about half of all armaments. It is "
            "also the edit that decided the factor: under rounding the "
            "intersection over the nine scaling-free armaments is empty, "
            "under truncation it is [0.599315, 0.600928). Soldier's Crossbow "
            "is the single reading that shows it, 88 against 89. Killed by "
            "tests/test_attack_power_against_the_game.py, and its companion "
            "test_at_least_one_reading_tells_truncation_from_rounding is "
            "what keeps such a reading in the file. It reaches the catalyst "
            "figures as well, which go through the same one formatter: 39 of "
            "the 84 readings and 16 of the 28 reference figures in "
            "tests/data/game_catalyst_scaling.json fail under it. That file "
            "does not register a second entry for the same edit -- there is "
            "one display rule and one place it lives."),
    ),
    # -- the game's other number: staves and seals (T-046: QA-099) ----------
    #
    # Three edits, because the figure is three decisions and a guard that
    # caught only one would leave the others unheld: which rate it is built
    # from, which curve turns the attribute into a bonus, and whether the
    # influence that belongs to the attack rating belongs here too. The
    # fourth, truncation against rounding, is the entry above -- the same
    # display rule reaches both figures.
    "catalyst-scaling-rate-ignored": Mutation(
        path="nrplanner/weapons.py",
        old="""    scaling_rate = reinforce[CATALYST_SCALING_KEY]
""",
        new="""    scaling_rate = 1.0
""",
        survival_means=(
            "the one field that tells the catalysts apart reaches nothing, "
            "and all 28 of them collapse onto the bare constant: every staff "
            "and every seal would read the same figure for a given "
            "attribute, 90 at Intelligence 0. This is QA-099 c in its "
            "behavioural form -- the shape a Paramdex rename would have "
            "produced silently under `values.get(name, 1.0)`. Measured "
            "2026-09-05: 78 of the 84 readings and 26 of the 28 reference "
            "figures fail. Killed by "
            "tests/test_catalyst_scaling_against_the_game.py."),
    ),
    "catalyst-curve-hardcoded-to-zero": Mutation(
        path="nrplanner/weapons.py",
        old="""    curve = curves.get(str(weapon.get("curve", {}).get("Physics")))
""",
        new="""    curve = curves.get("0")
""",
        survival_means=(
            "the curve that turns Intelligence or Faith into the bonus is "
            "held by nothing, and the armament's own `correctType_Physics` "
            "could be replaced by any of the 82 curves in the data. It is "
            "16 for all 255 catalyst rows, and T-043 measured that exactly "
            "one of the 82 admits any constant at all -- the other 81 leave "
            "an empty interval. Measured 2026-09-05: 84 of 84 readings and "
            "28 of 28 reference figures fail. Killed by "
            "tests/test_catalyst_scaling_against_the_game.py."),
    ),
    "catalyst-influence-inside-the-bracket": Mutation(
        path="nrplanner/weapons.py",
        old="""    return CATALYST_DISPLAY_RATE * scaling_rate * (1.0 + ratio)
""",
        new="""    return CATALYST_DISPLAY_RATE * scaling_rate * (1.0 + 0.9 * ratio)
""",
        survival_means=(
            "nothing says that the AttackElementCorrectParam influence "
            "belongs to the attack rating and not to this figure. The "
            "catalyst rows carry an influence of 90, `weapons.rate` applies "
            "it, and applying it here as well is the single most plausible "
            "wrong reading of the formula -- T-043 ruled it out by "
            "intersection, K in [93.8009, 92.5061], which is empty. Measured "
            "2026-09-05: 84 of 84 readings and 6 of 28 reference figures "
            "fail. Killed by "
            "tests/test_catalyst_scaling_against_the_game.py."),
    ),
    "catalyst-scaling-field-renamed": Mutation(
        path="nrdata/extract.py",
        old="""CATALYST_SCALING_FIELD = "unknown_1"
""",
        new="""CATALYST_SCALING_FIELD = "spellAttackRate"
""",
        survival_means=(
            "the extraction does not notice that the field it reads the "
            "catalyst rate out of has gone. The name is a Paramdex "
            "placeholder for an unnamed field at offset 128, so it being "
            "renamed is an ordinary event rather than a hypothetical; what "
            "must not be ordinary is the extraction carrying on without it. "
            "Killed by tests/test_catalyst_scaling_extraction.py::"
            "test_a_well_formed_table_hands_back_every_rate, whose stub rows "
            "carry the Paramdex name written out as a literal rather than "
            "read off the constant -- a stub built from the constant agrees "
            "with whatever the extractor is looking for and cannot see this "
            "at all. Measured 2026-09-05: 3 of that file's 4 cases fail, and "
            "the one that survives is the refusal case, because a guard that "
            "only ever refuses is satisfied by refusing everything. The name "
            "written here is deliberately not the one that file's refusal "
            "case uses: if the two coincided, that case would fail for a "
            "reason that has nothing to do with this mutation."),
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
