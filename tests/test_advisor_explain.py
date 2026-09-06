"""Why this build, and what the reasoning is not allowed to say.

The sharp claim is the one from the step table, and it is scharf on purpose:
**every line names an effect that is really in the suggestion.** A plausible
sentence about an effect that is not in there is a fault, not a rounding
error -- and the way to write one by accident is to read `built.sources`
whole instead of the difference to the base state, which credits the
suggestion with everything the player was already holding (AD-014.6).

The case that watches it therefore derives what a line *may* name from the
inventory -- handle, roll, dataset -- and not from the attribution the module
performs. Deriving it from the module would make the case agree with whatever
the module did.

Beside it, three rules that are easy to get subtly wrong:

* **a curse is named, never charged twice** (AD-015, OF-13). What is shown is
  what the calculation applied, read out of `Build.sources`, so a conditional
  curse cannot be shown as though it had bitten;
* **which negatives were counted against a relic** has to be said (`GOAL.md`
  F3), and the direction of "negative" comes from `model.is_better_lower` --
  an FP cost 8 % smaller is a gain, and the sign alone says the opposite;
* **the mandatory line for a curse the ranking figure cannot feel**
  (AD-015): asked of the direction itself rather than of a list of fields
  kept here, so a third direction brings its own answer.

The rendering cases build a `model.Build` outright. That is what lets a case
*state* a multiplier at exactly its neutral value, or one idea split across
five fields, instead of hunting the dataset for one and hoping it stays.
"""

from __future__ import annotations

import pathlib

import pytest

from nrplanner import effecttext, model
from nrplanner.advisor import candidates, explain, goals, search, types
from nrplanner.advisor.evaluate import evaluate

from tests import advisor_cases as advisor
from tests import weapon_damage_cases as cases

DAMAGE = "max_damage"
SURVIVAL = "min_damage_taken"


@pytest.fixture(scope="module")
def wylder(game_data):
    return cases.hero_by_name(game_data, "Wylder")


@pytest.fixture
def armament(game_data, wylder):
    return advisor.scaling_armament(game_data, wylder)


def effect_names(data: dict, effect_ids) -> set[str]:
    """The names those effects go into `Build.sources` under."""
    found = set()
    for effect_id in effect_ids:
        effect = data["effects"].get(str(effect_id))
        if effect is not None:
            found.add(" ".join(str(effect["name"]).split()))
    return found


def labels_moved_by(data: dict, hero: dict, effect_id: int) -> set[str]:
    """What the stat sheet calls the figures this one effect moves.

    Asked of `model.compute` on the single effect and named through
    `model.label_for`, so the expectation comes from the model rather than
    from the attribution being watched. Merged through
    `model.collapse_by_label` for the same reason the reasoning merges: the
    game splits one idea over several fields and the sheet shows it once.
    """
    build = model.compute(hero, advisor.LEVEL,
                          [data["effects"][str(effect_id)]],
                          data.get("curves", {}))
    merged = model.collapse_by_label({key: entries[0].own
                                      for key, entries in
                                      build.sources.items()})
    return {model.label_for(key) for key in merged}


def owned_by_handle(inventory, handle: int):
    return next(relic for relic in inventory.relics if relic.handle == handle)


def a_copy(slot_index: int, handle: int, name: str = "Copy",
           effect_ids=(), curse_ids=()) -> types.Candidate:
    """One chosen copy, stated rather than searched for."""
    return types.Candidate(
        slot_index=slot_index, handle=handle, relic_id=9000 + handle,
        name=name, colour=advisor.RED, is_deep=bool(curse_ids),
        effect_ids=tuple(effect_ids), curse_ids=tuple(curse_ids))


def a_build(sources: dict, rates=()) -> model.Build:
    """A build that says exactly what it recorded and what multiplies.

    `rates` is what tells `explain` a figure scales rather than adds -- the
    same reading `app.py`'s breakdown takes off `last_rates`.

    An entry is `(name, own, effect id)`, the three things `model.compute`
    records. The id is stated rather than derived from the name, because the
    attribution under test is the one that must not go by name (QA-180).
    """
    return model.Build(
        sources={key: [model.SourceEntry(*entry) for entry in entries]
                 for key, entries in sources.items()},
        rates={key: 1.0 for key in rates})


def a_curse_this_armament_cannot_feel(data: dict, hero: dict,
                                      weapon: dict) -> tuple[int, tuple]:
    """A curse that takes away attributes this armament does not scale on.

    ...and takes away the attribute the HP curve is built on, so that the
    other direction does feel it. Both halves are read off the game's own
    account -- `model.compute`, the armament's scaling table, and the
    attribute the dataset's HP curve names -- and never off the question
    `explain` asks, which is whether the direction's figure moves. Selecting
    on that would make the case agree with whatever the module decided.

    Hands back the curse and the attributes it lowers, so the case can say out
    loud why the two directions have to answer differently.
    """
    curves = data.get("curves", {})
    scaling = weapon.get("scaling") or {}
    vitality = (curves.get("HP") or {}).get("attribute")
    for key in sorted(data["effects"], key=int):
        effect = data["effects"][key]
        if not effect.get("is_curse"):
            continue
        build = model.compute(hero, advisor.LEVEL, [effect], curves)
        lowered = tuple(name for name, value in build.attributes.items()
                        if value < build.base_attributes.get(name, 0))
        if (vitality in lowered
                and not any(scaling.get(name) for name in lowered)):
            return int(effect["id"]), lowered
    pytest.skip("no curse in this dataset lowers the attribute HP is built "
                "on while leaving this armament's scaling alone, so the two "
                "directions cannot be told apart")


def a_context(named: dict[int, str]) -> types.GoalContext:
    """A context whose dataset knows exactly these effects, by name."""
    return types.GoalContext(
        data={"effects": {str(effect_id): {"id": effect_id, "name": name}
                          for effect_id, name in named.items()}},
        hero={}, level=advisor.LEVEL, reference=None,
        weighting=goals.DEFAULT_WEIGHTING)


def a_vessel(slots: int) -> types.SlotProblem:
    """A vessel of this many free slots, held by nothing."""
    return advisor.problem([advisor.RED] * slots)


def lines_of(groups) -> tuple[str, ...]:
    """The text of every line of every group, in the order it is drawn.

    The groups are what the window reads; this is the flat view a case wants
    when what it watches is the wording rather than the placing.
    """
    return tuple(line.text for group in groups for line in group.lines)


def with_a_figure(groups) -> tuple[str, ...]:
    """The text of the lines that carry a number."""
    return tuple(line.text for group in groups for line in group.lines
                 if line.silence == types.CARRIES_A_FIGURE)


# -- the reference point ----------------------------------------------------

def test_the_reasons_name_only_effects_the_suggestion_brought(game_data,
                                                              wylder,
                                                              armament):
    """S8's own acceptance, and the reference point that makes it true.

    One slot is held and one is free. Everything the held copy carries is in
    `built.sources` as well -- it is in every evaluation of this problem
    (AD-014.1) -- so a reasoning read off `sources` whole would credit the
    suggestion with it. What a line may name is worked out here from the
    inventory and the dataset, never from the module's own attribution.
    """
    inventory = advisor.make_inventory(game_data, wylder, colour=advisor.RED,
                                       count=4)
    kept = inventory.relics_for(advisor.RED, False)[0]
    problem = advisor.problem([advisor.RED, advisor.RED],
                              held={0: advisor.held_relic(kept)})
    ctx = advisor.context(game_data, wylder, reference=armament)
    pools = candidates.pools(inventory, problem, ctx, goals.GOALS, DAMAGE)
    found = search.beam(problem, pools, types.DEFAULT_BUDGET,
                        search.goal_scorer(problem, ctx, goals.GOALS[DAMAGE]))
    chosen = explain.chosen_for(found[0], pools)

    lines = lines_of(explain.reasons(problem, chosen,
                                     evaluate(problem, (), ctx),
                                     evaluate(problem, chosen, ctx), ctx,
                                     goals.GOALS[DAMAGE]))

    allowed = set()
    for choice in found[0].choices:
        copy = owned_by_handle(inventory, choice.handle)
        allowed |= effect_names(game_data, copy.effect_ids + copy.curse_ids)
    held_names = effect_names(game_data, kept.effect_ids + kept.curse_ids)
    assert lines, "nothing was explained, so nothing is being watched"
    assert held_names and not (held_names & allowed), (
        "the held copy carries the same effect names as the suggested one, "
        "so this case cannot tell the two apart")
    for line in lines:
        assert any(name in line for name in allowed), (
            f"this line names no effect of the suggested copies: {line!r}")
        assert not any(name in line for name in held_names), (
            f"this line names an effect of the **held** copy: {line!r}")


def test_a_stacking_effect_on_three_copies_is_named_once_per_copy(game_data,
                                                                  wylder,
                                                                  armament):
    """One effect on three relics is three contributions, one apiece.

    `Build.sources` files them all under the one name, so the attribution has
    to hand out one entry per copy rather than let the first copy claim all
    three. It is the ordinary case on a Deep vessel -- `Physical Attack Up +4`
    on three relics at once -- and getting it wrong reads as two of the three
    relics contributing nothing at all.
    """
    roll = advisor.raising_effects(game_data, wylder, 1)[0]
    inventory = advisor.make_inventory(game_data, wylder, colour=advisor.RED,
                                       count=3, rolls=[roll, roll, roll,
                                                       roll])
    problem = advisor.problem([advisor.RED, advisor.RED, advisor.RED])
    ctx = advisor.context(game_data, wylder, reference=armament)
    chosen = tuple(a_copy(index, 100 + index, f"Copy {index}", roll)
                   for index in range(3))

    groups = explain.reasons(problem, chosen, evaluate(problem, (), ctx),
                             evaluate(problem, chosen, ctx), ctx,
                             goals.GOALS[DAMAGE])

    name = effect_names(game_data, roll).pop()
    named = [line for group in groups for line in group.lines
             if name in line.text
             and line.silence == types.CARRIES_A_FIGURE]
    assert len(named) == 3, (
        f"three copies carry {name!r}; it is named in {len(named)} lines "
        f"that carry a figure: {[line.text for line in named]}")
    assert sorted(line.slot_index for line in named) == [0, 1, 2], (
        "the slot a line belongs under travels beside it, never in it: the "
        "window has to place the line without reading it (AK-147)")
    assert all(f"Slot {line.slot_index + 1}" not in line.text
               for line in named), (
        f"a line still names its own slot: {[line.text for line in named]}")


def test_a_copy_whose_effect_the_held_relic_already_caps_is_not_credited(
        game_data, wylder, armament):
    """AD-014.6: the reference point is the base state, and this is why.

    The held relic carries an `isStrongestEffect`, and so does the chosen
    copy. Two copies of such an effect are worth exactly one, so
    `model.compute` counts the held one and reports the second as a
    duplicate: `built.sources` carries the entry, and it is the **base
    state's** entry, standing in `base.sources` too.

    Read `sources` whole and the chosen copy is credited with a figure it did
    not add -- the score does not move, the reasoning still reads well, and
    that is the failure Nachtrag I names first (AD-014.3). The entry has to be
    cancelled against the base state, and then there is nothing to say about
    this copy, which is the truth.
    """
    stuck = advisor.a_non_stacking_effect(game_data, wylder,
                                          "physicsAttackRate")
    held = types.HeldRelic(relic_id=1, name="Held copy",
                           effect_ids=(stuck,), handle=1)
    problem = types.SlotProblem(
        slots=(types.Slot(index=0, colour=advisor.RED, deep=False),
               types.Slot(index=1, colour=advisor.RED, deep=False)),
        held=(types.HeldSlot(index=0, relic=held),))
    ctx = advisor.context(game_data, wylder, reference=armament)
    chosen = (a_copy(1, 2, "Chosen copy", [stuck]),)
    base = evaluate(problem, (), ctx)
    built = evaluate(problem, chosen, ctx)

    name = effect_names(game_data, [stuck]).pop()
    assert any(entry.name == name for entries in built.sources.values()
               for entry in entries), (
        f"{name!r} stands in no source of the built build, so there is "
        f"nothing here for a reasoning to claim wrongly")

    groups = explain.reasons(problem, chosen, base, built, ctx,
                             goals.GOALS[DAMAGE])

    assert with_a_figure(groups) == (), (
        "the chosen copy was credited with the held relic's contribution")
    assert lines_of(groups) == (
        f"{name}: another copy of it is already counted, so this one adds "
        f"nothing.",), (
        "the copy contributed nothing, and the reason is that the figure is "
        "already in the build from elsewhere -- not that the effect does "
        "nothing")


def test_a_copy_whose_effect_the_game_refused_to_stack_gets_no_line(
        game_data, wylder, armament):
    """The second copy of an `isStrongestEffect` really did contribute nothing.

    `model.compute` counts it once and reports the rest as duplicates, so
    `sources` carries one entry. Reading the relic definitions instead would
    produce a line for the second copy with a figure the build does not
    contain -- and that is the recommendation AD-014.3 exists to prevent,
    written out as prose.
    """
    stuck = advisor.a_non_stacking_effect(game_data, wylder,
                                          "physicsAttackRate")
    problem = advisor.problem([advisor.RED, advisor.RED])
    ctx = advisor.context(game_data, wylder, reference=armament)
    chosen = (a_copy(0, 101, "First copy", [stuck]),
              a_copy(1, 102, "Second copy", [stuck]))

    first, second = explain.reasons(problem, chosen,
                                    evaluate(problem, (), ctx),
                                    evaluate(problem, chosen, ctx), ctx,
                                    goals.GOALS[DAMAGE])

    assert with_a_figure((first,)), (
        "the first copy was not credited with the effect it did contribute")
    assert with_a_figure((second,)) == (), (
        f"the second copy of a non-stacking effect was credited with a "
        f"figure: {lines_of((second,))}")
    assert [line.silence for line in second.lines] == [
        types.SILENT_ALREADY_COUNTED], (
        f"the second copy says nothing about why it is silent, or says the "
        f"wrong thing: {lines_of((second,))}")


def test_two_effects_of_one_name_are_credited_to_the_slot_that_carries_them():
    """QA-180's smallest case: one name, two ids, two slots.

    The dataset calls both `7000090` (Vigor +5) and `6610400` (Max HP +10 %)
    `Increased Maximum HP`. Attributing by name gives the copy in the lower
    slot both figures -- one of which its effect cannot move -- and leaves the
    other slot without a line at all. On the real save that was 130 lines
    over 592 suggestions and 23 of the 296 best suggestions with a silent
    slot, every one of which had moved the ranking figure.

    **The expectation is stated, not derived.** The case that used to watch
    this checked that every line names *a* name of the suggested copies, and
    `Increased Maximum HP` is such a name whichever slot it is printed under,
    so it could not go red. What is asserted here is the slot each figure is
    printed under, which is the thing that was wrong.
    """
    ctx = a_context({7000090: "Increased Maximum HP",
                     6610400: "Increased Maximum HP"})
    built = a_build({"Vigor": [("Increased Maximum HP", 5, 7000090)],
                     "maxHpRate": [("Increased Maximum HP", 1.1, 6610400)]},
                    rates=("maxHpRate",))

    groups = explain.reasons(a_vessel(2),
                             (a_copy(0, 1, "Vigor relic", [7000090]),
                              a_copy(1, 2, "Max HP relic", [6610400])),
                             a_build({}), built, ctx, goals.GOALS[DAMAGE])

    assert [(group.slot_index, group.relic_name, lines_of((group,)))
            for group in groups] == [
        (0, "Vigor relic", ("Increased Maximum HP: Vigor +5",)),
        (1, "Max HP relic", ("Increased Maximum HP: Max HP +10.0%",)),
    ]


def test_a_name_two_effects_share_in_this_dataset_still_lands_on_two_slots(
        game_data, wylder, armament):
    """The same rule against the dataset, with the figures it really records.

    The pair is looked up rather than named -- 160 of this dataset's 707
    effect names are carried by more than one id -- and what each of the two
    moves is asked of `model.compute` on that one effect. Nothing here reads
    the attribution it is watching, and the two field sets are disjoint by
    construction, so a line under the wrong slot names a figure that slot's
    relic cannot produce.
    """
    first, second = advisor.two_effects_the_dataset_gives_one_name(game_data,
                                                                   wylder)
    problem = advisor.problem([advisor.RED, advisor.RED])
    ctx = advisor.context(game_data, wylder, reference=armament)
    chosen = (a_copy(0, 1, "First relic", [first]),
              a_copy(1, 2, "Second relic", [second]))

    groups = explain.reasons(problem, chosen, evaluate(problem, (), ctx),
                             evaluate(problem, chosen, ctx), ctx,
                             goals.GOALS[DAMAGE])

    assert effect_names(game_data, [first]) == effect_names(game_data,
                                                            [second]), (
        "the two effects no longer share a name, so this case cannot tell an "
        "attribution by name from one by id")
    for slot, effect_id in ((0, first), (1, second)):
        labels = labels_moved_by(game_data, wylder, effect_id)
        group = next(one for one in groups if one.slot_index == slot)
        said = with_a_figure((group,))
        assert said, (
            f"slot {slot} carries an effect that moves {sorted(labels)} and "
            f"the reasoning says nothing about it at all: "
            f"{lines_of(groups)}")
        for line in said:
            assert any(label in line for label in labels), (
                f"this line stands under slot {slot}, whose effect moves "
                f"{sorted(labels)}, and names none of them: {line!r}")


# -- how one figure is written down -----------------------------------------

def test_a_multiplier_reads_as_a_percentage_and_a_bonus_as_a_number():
    """`UI_SPEC` 3.2: the field names and number formats of the stat sheet.

    Which of the two a figure gets is read off the build it came from, the
    way `app.py`'s breakdown reads it -- a key standing in `Build.rates`
    scales, an attribute adds. Guessing it from the field name is a different
    calculation, and QA-011 is what that costs.
    """
    ctx = a_context({1: "Physical Attack Up"})
    built = a_build({"physicsAttackRate": [("Physical Attack Up", 1.12, 1)],
                     "Strength": [("Physical Attack Up", 3, 1)]},
                    rates=("physicsAttackRate",))

    lines = lines_of(explain.reasons(a_vessel(1),
                                     (a_copy(0, 1, "A relic", [1]),),
                                     a_build({}), built, ctx,
                                     goals.GOALS[DAMAGE]))

    assert lines == (
        "Physical Attack Up: Physical Attack +12.0%",
        "Physical Attack Up: Strength +3",
    )


def test_a_figure_that_is_better_small_is_not_called_a_cost_for_falling():
    """`GOAL.md` F3 needs the direction, and the sign does not carry it.

    A damage-cut rate at 0.85 is 15 % less damage taken, and an FP cost at
    0.92 is 8 % cheaper: both fall and both are gains. A flask that restores
    15 % less falls the same way and is a loss. `model.is_better_lower` is the
    one place that knows which is which.

    Both are ordinary effects here, not one of them a curse: the marker comes
    off the direction of the field and not off what carries it, and a curse
    would drag the direction's own question into a case that is not about it.
    """
    ctx = a_context({1: "Improved Fire Damage Negation +1",
                    2: "Reduced Flask HP Restoration"})
    built = a_build(
        {"fireDamageCutRate": [("Improved Fire Damage Negation +1", 0.85, 1)],
         "changeHpEstusFlaskCorrectRate": [("Reduced Flask HP Restoration",
                                            0.85, 2)]},
        rates=("fireDamageCutRate", "changeHpEstusFlaskCorrectRate"))

    lines = lines_of(explain.reasons(a_vessel(1),
                                     (a_copy(0, 1, "A relic", [1, 2]),),
                                     a_build({}), built, ctx,
                                     goals.GOALS[DAMAGE]))

    assert lines == (
        "Improved Fire Damage Negation +1: Fire damage taken -15.0%",
        "Reduced Flask HP Restoration: HP restored per flask -15.0%, "
        "counted against it",
    )


def test_a_figure_that_did_not_move_is_no_reason():
    """A multiplier at 1.0 is not a gain, and calling it a cost is worse.

    `model.compute` records a field an effect carries even where the value is
    the field's own neutral. `+0.0%` explains nothing, and the direction test
    above would file it under "counted against it" because it is not above
    neutral.
    """
    ctx = a_context({1: "Does nothing"})
    built = a_build({"physicsAttackRate": [("Does nothing", 1.0, 1)],
                     "Strength": [("Does nothing", 0, 1)]},
                    rates=("physicsAttackRate",))

    groups = explain.reasons(a_vessel(1), (a_copy(0, 1, "A relic", [1]),),
                             a_build({}), built, ctx, goals.GOALS[DAMAGE])

    assert with_a_figure(groups) == ()
    assert lines_of(groups) == (
        "Does nothing: no number here shows what this adds.",), (
        "the effect was recorded, at its own neutral value, by this very "
        "copy: what it did not do is add a number, and it is not somebody "
        "else's figure")


def test_one_idea_split_over_several_fields_is_not_said_several_times():
    """The game splits one FP cost across five fields; the sheet merges them.

    Through `model.collapse_by_label`, the model's own rule, so what the
    advisor merges and what the stat sheet merges cannot come apart. Five
    lines saying FP costs 8 % less is the noise it exists against; the three
    that remain are three different things the sheet names differently.
    """
    ctx = a_context({1: "Reduced FP Consumption"})
    fields = ("artsConsumptionRate", "magicConsumptionRate",
              "shamanConsumptionRate", "miracleConsumptionRate",
              "goodsConsumptionRate")
    built = a_build({field: [("Reduced FP Consumption", 0.92, 1)]
                     for field in fields}, rates=fields)

    lines = lines_of(explain.reasons(a_vessel(1),
                                     (a_copy(0, 1, "A relic", [1]),),
                                     a_build({}), built, ctx,
                                     goals.GOALS[DAMAGE]))

    assert lines == (
        "Reduced FP Consumption: Skill FP cost -8.0%",
        "Reduced FP Consumption: Spell FP cost -8.0%",
        "Reduced FP Consumption: Item use cost -8.0%",
    )


def test_a_buff_bound_to_one_class_of_armament_says_which():
    """`Physical Attack +6.0%` without the class is a claim about the grid.

    `model.compute` files such a buff under `wepclass:<class>:<field>`, and it
    never reaches `Build.rates` -- its value lives in `class_rates`. So both
    questions about it, whether it scales and what it is called, have to be
    answered off the key rather than off the build.
    """
    ctx = a_context({1: "Improved Melee Attack Power"})
    key = f"{model.WEAPON_CLASS_PREFIX}melee:physicsAttackRate"
    built = a_build({key: [("Improved Melee Attack Power", 1.06, 1)]})

    lines = lines_of(explain.reasons(a_vessel(1),
                                     (a_copy(0, 1, "A relic", [1]),),
                                     a_build({}), built, ctx,
                                     goals.GOALS[DAMAGE]))

    assert lines == (
        "Improved Melee Attack Power: "
        "Physical Attack, melee armaments only +6.0%",
    )


def test_a_buff_the_game_restricts_to_one_move_does_not_say_its_name_twice():
    """`model.label_for` gives a scoped buff the effect's own name as label.

    That is right where the label stands alone -- it states the scope -- and
    beside the effect it reads `X: X +15.0%`, which is a longer way of saying
    nothing new.
    """
    ctx = a_context({1: "Improved Skill Attack Power"})
    key = f"{model.SCOPED_PREFIX}Improved Skill Attack Power"
    built = a_build({key: [("Improved Skill Attack Power", 1.15, 1)]},
                    rates=(key,))

    lines = lines_of(explain.reasons(a_vessel(1),
                                     (a_copy(0, 1, "A relic", [1]),),
                                     a_build({}), built, ctx,
                                     goals.GOALS[DAMAGE]))

    assert lines == ("Improved Skill Attack Power: +15.0%",)


def test_an_effect_this_dataset_does_not_carry_is_named_nowhere():
    """`evaluate` skips an unknown id, so it moved nothing to explain.

    Inherited from `Planner.selected_effects` on purpose rather than solved
    in a second place (P4, QA-004/QA-032). What must not happen is a figure
    for it: a reasoning that credits an effect the calculation never saw is
    the fault this step is accepted against.

    It is still counted, and it still gets a line, because the heading says
    how many of the copy's roles moved a number. An effect that vanished from
    both would make `2 - 1 = 1` come out as no line at all, and the player
    would be reading a denominator that does not add up (AK-155).
    """
    ctx = a_context({1: "Known"})
    built = a_build({"Strength": [("Known", 3, 1)]})

    group, = explain.reasons(a_vessel(1),
                             (a_copy(0, 1, "A relic", [1, 4242]),),
                             a_build({}), built, ctx, goals.GOALS[DAMAGE])

    assert with_a_figure((group,)) == ("Known: Strength +3",)
    assert lines_of((group,))[1:] == (
        "One of its effects is not in your game data, so it has no name "
        "here and counted for nothing.",)
    assert "4242" not in lines_of((group,))[1]
    assert (group.effects_total, group.effects_with_a_figure) == (2, 1)
    assert group.count_line == (
        "1 of its 2 effects moved a number in this build.")


# -- curses -----------------------------------------------------------------

def test_the_curses_are_the_ones_the_calculation_applied(game_data, wylder,
                                                          armament):
    """AD-015: out of `Build.sources`, never out of the relic definition.

    A conditional curse is left out of every total until the player declares
    it, so showing it among the costs of a suggestion would state a price the
    figure beside it does not contain. It is not silence either -- it is in
    `not_counted`, which is where an uncounted thing belongs.
    """
    biting = cases.curses_lowering_an_attribute(game_data, wylder, 1)[0]
    waiting = advisor.a_declarable_effect(game_data, wylder)
    problem = advisor.problem([advisor.RED])
    ctx = advisor.context(game_data, wylder, reference=armament)
    chosen = (a_copy(0, 1, "Cursed copy", (), [biting, waiting]),)
    built = evaluate(problem, chosen, ctx)

    named = explain.curses(chosen, evaluate(problem, (), ctx), built, ctx)

    biting_name = effect_names(game_data, [biting]).pop()
    waiting_name = effect_names(game_data, [waiting]).pop()
    assert any(biting_name in line for line in named), (
        f"the curse that really moved a figure is not named: {named}")
    assert not any(waiting_name in line for line in named), (
        f"a curse the calculation did not apply is shown as though it had: "
        f"{named}")
    assert waiting_name in explain.not_counted(built)


def test_a_curse_is_among_the_reasons_as_a_cost_that_was_counted(game_data,
                                                                  wylder,
                                                                  armament):
    """`GOAL.md` F3, in the user's own words.

    *"Falls meine negativen auf Relikten meine Benefits vernichten, muss ich
    das wissen."* A curse is an ordinary effect in the calculation (AD-015)
    and it has to be an ordinary line in the reasoning, marked for what it is.

    Asked of the direction that **feels** this curse, by construction: one
    that cannot is told so instead, in its own filling, and that is the case
    below.
    """
    biting, _lowered = a_curse_this_armament_cannot_feel(
        game_data, wylder, armament.weapon)
    problem = advisor.problem([advisor.RED])
    ctx = advisor.context(game_data, wylder, reference=armament)
    chosen = (a_copy(0, 1, "Cursed copy", (), [biting]),)

    groups = explain.reasons(problem, chosen, evaluate(problem, (), ctx),
                             evaluate(problem, chosen, ctx), ctx,
                             goals.GOALS[SURVIVAL])

    lines = lines_of(groups)
    name = effect_names(game_data, [biting]).pop()
    charged = [line for line in lines if name in line]
    assert charged, f"the curse is named nowhere in the reasoning: {lines}"
    assert all(line.is_curse for group in groups for line in group.lines), (
        "the window sets ✦ and CURSE off this flag; without it the only way "
        "to know is to read the sentence")
    assert all("counted against it" in line for line in charged), (
        f"a curse that lowers an attribute is not marked as counted against "
        f"the relic: {charged}")


def test_a_curse_to_which_no_figure_was_written_is_still_named(game_data,
                                                               wylder,
                                                               armament):
    """`UI_SPEC` §3.2: a price that only shows after applying is a trap.

    A curse whose whole content the calculation cannot reduce to a number --
    the engine-only ones, `Taking Damage Causes Madness Buildup` and its
    family -- moved nothing, so no ordinary line names it. It is a cost all
    the same, and the sentence says exactly what is true here: no number
    beside it, never that the game files carry none (AK-140).
    """
    silent = a_curse_that_moves_no_number(game_data, wylder)
    problem = advisor.problem([advisor.RED])
    ctx = advisor.context(game_data, wylder, reference=armament)
    chosen = (a_copy(0, 1, "Cursed copy", (), [silent]),)

    groups = explain.reasons(problem, chosen, evaluate(problem, (), ctx),
                             evaluate(problem, chosen, ctx), ctx,
                             goals.GOALS[DAMAGE])

    name = effect_names(game_data, [silent]).pop()
    assert lines_of(groups) == (
        f"{name}: no number here shows what this costs.",)
    assert explain.curses_without_a_figure(groups) == groups[0].lines
    assert explain.effects_without_a_figure(groups) == ()


def test_every_curse_of_the_suggested_copy_stands_in_the_block(game_data,
                                                               wylder,
                                                               armament):
    """AK-159 and the Director's correction of 06.09.2026, in one case.

    **A curse is a trap, a silent effect is not.** Every curse of the copy is
    in the block, the one with a figure and the one without; the effect that
    merely does nothing here waits in the `Why` dialog, where it costs no
    height in a card that measured 16 lines at its worst.

    The names are resolved through the dataset, not through the module: what
    is compared is the set of curse names against `curse_ids`, so a curse
    dropped and a curse shown twice are both red (AK-138, AK-148).
    """
    biting, _lowered = a_curse_this_armament_cannot_feel(
        game_data, wylder, armament.weapon)
    silent_curse = a_curse_that_moves_no_number(game_data, wylder)
    quiet = an_effect_that_moves_no_number(game_data, wylder)
    problem = advisor.problem([advisor.RED])
    ctx = advisor.context(game_data, wylder, reference=armament)
    chosen = (a_copy(0, 1, "Cursed copy", [quiet],
                     [biting, silent_curse]),)

    groups = explain.reasons(problem, chosen, evaluate(problem, (), ctx),
                             evaluate(problem, chosen, ctx), ctx,
                             goals.GOALS[SURVIVAL])
    block = [line for group in groups for line in group.lines
             if types.drawn_in_the_block(line)]
    dialog = [line for group in groups for line in group.lines]

    wanted = effect_names(game_data, [biting, silent_curse])
    named = {name for name in wanted
             for line in block if line.text.startswith(f"{name}: ")}
    assert named == wanted, (
        f"the block names {sorted(named)} where the copy carries "
        f"{sorted(wanted)}. Names, not lines: a curse that moves two figures "
        f"stands in two lines and is one name (AK-159)")
    quiet_name = effect_names(game_data, [quiet]).pop()
    assert any(line.text.startswith(f"{quiet_name}: ") for line in dialog), (
        "the silent effect is named nowhere at all")
    assert not any(line.text.startswith(f"{quiet_name}: ")
                   for line in block), (
        "the silent effect stands in the block, where the Director's "
        "correction of 06.09.2026 keeps it out")


# -- the effects that moved nothing -----------------------------------------

def a_curse_that_moves_no_number(data: dict, hero: dict) -> int:
    """A curse this build records nothing at all for.

    Asked of `model.compute`: it wrote no source entry, which is the
    criterion the whole filling rests on -- not "the game files carry no
    numbers", which for `All Resistances Down` would be false.
    """
    curves = data.get("curves", {})
    for key in sorted(data["effects"], key=int):
        effect = data["effects"][key]
        if not effect.get("is_curse"):
            continue
        if not model.compute(hero, advisor.LEVEL, [effect], curves).sources:
            return int(effect["id"])
    pytest.skip("every curse in this dataset moves a figure, so there is no "
                "curse without one to say anything about")


def an_effect_that_moves_no_number(data: dict, hero: dict) -> int:
    """An ordinary effect that works here and still moves no figure.

    Not gated, not another Nightfarer's, not tied to the armaments -- the
    remainder, which is filling (d) and the commonest thing a relic carries
    that the sheet cannot price. All four questions are asked of the model
    and of `effecttext`, never of `explain`.
    """
    curves = data.get("curves", {})
    hero_name = str(hero.get("name", ""))
    for key in sorted(data["effects"], key=int):
        effect = data["effects"][key]
        if effect.get("is_curse") or effecttext.owner(effect):
            continue
        if any(gate in (effect.get("modifiers") or {})
               for gate in model.GATE_FIELDS):
            continue
        if not effecttext.works_for(effect, hero_name):
            continue
        build = model.compute(hero, advisor.LEVEL, [effect], curves)
        if not build.sources and not build.situational:
            return int(effect["id"])
    pytest.skip("every ungated effect of this dataset moves a figure at this "
                "level, so filling (d) has no case here")


def an_effect_of_this_nightfarer_that_moves_no_number(data: dict,
                                                      hero: dict) -> int:
    """A `[Name] ...` effect belonging to the played Nightfarer, and silent.

    The case AK-152 asks for by name: it works here, so it is never the
    "another Nightfarer" filling, and on anybody else it is exactly that.
    """
    curves = data.get("curves", {})
    hero_name = str(hero.get("name", ""))
    for key in sorted(data["effects"], key=int):
        effect = data["effects"][key]
        if effecttext.owner(effect) != hero_name:
            continue
        if any(gate in (effect.get("modifiers") or {})
               for gate in model.GATE_FIELDS):
            continue
        build = model.compute(hero, advisor.LEVEL, [effect], curves)
        if not build.sources and not build.situational:
            return int(effect["id"])
    pytest.skip(f"no effect of this dataset belongs to {hero_name} and moves "
                f"no number, so the ownership filling has no case here")


def an_armament_bound_effect_that_moves_no_number(data: dict,
                                                  hero: dict) -> int:
    """An effect whose worth is a question about the armaments carried.

    Picked by the gate `model.GATE_FIELDS` itself calls "only with a matching
    weapon type", "needs several of that weapon equipped" or "changes the
    armament's skill" -- the model's own account of the family -- and only
    where the model did not park it as a switch, because a switch is the
    condition filling and comes first.
    """
    curves = data.get("curves", {})
    hero_name = str(hero.get("name", ""))
    wanted = {field_name for field_name, why in model.GATE_FIELDS.items()
              if "weapon" in why or "armament" in why}
    for key in sorted(data["effects"], key=int):
        effect = data["effects"][key]
        if not any(gate in (effect.get("modifiers") or {})
                   for gate in wanted):
            continue
        if not effecttext.works_for(effect, hero_name):
            continue
        build = model.compute(hero, advisor.LEVEL, [effect], curves)
        if not build.sources and not any(not entry.live
                                         for entry in build.situational):
            return int(effect["id"])
    pytest.skip("no armament-bound effect of this dataset is silent without "
                "also being a switch, so filling (c) has no case here")


def test_the_armament_gates_are_the_ones_the_model_names(game_data):
    """The four field names are `model.GATE_FIELDS` keys, not a private list.

    A family that drifted from the model's would put an effect into the
    remainder filling and say `no number here shows what this adds.` about
    something whose whole answer is "carry the other axe".
    """
    named = {field_name for field_name, why in model.GATE_FIELDS.items()
             if "weapon" in why or "armament" in why}

    assert set(explain._ARMAMENT_GATES) == named, (
        f"the module and the model disagree about which gates are about the "
        f"armaments: {sorted(set(explain._ARMAMENT_GATES) ^ named)}")


def test_an_effect_of_another_nightfarer_says_whose_it_is(game_data, wylder):
    """AK-152's own check: the same effect, two Nightfarers, two sentences.

    An effect named `[Wylder] ...` is dead weight on Duchess and works on
    Wylder. The filling that says so is the strongest news a silent line
    carries -- this one will never do anything in that slot -- and it is the
    commonest of the six: 150 of 426 on the save the vorgabe was measured on.
    """
    duchess = cases.hero_by_name(game_data, "Duchess")
    quiet = an_effect_of_this_nightfarer_that_moves_no_number(game_data,
                                                              wylder)
    problem = advisor.problem([advisor.RED])
    chosen = (a_copy(0, 1, "A relic", [quiet]),)
    name = effect_names(game_data, [quiet]).pop()

    said = {}
    for hero in (wylder, duchess):
        ctx = advisor.context(game_data, hero)
        groups = explain.reasons(problem, chosen, evaluate(problem, (), ctx),
                                 evaluate(problem, chosen, ctx), ctx,
                                 goals.GOALS[DAMAGE])
        said[hero["name"]] = groups[0].lines

    assert [line.text for line in said["Duchess"]] == [
        f"{name}: works only for Wylder, and you are Duchess."]
    assert [line.silence for line in said["Duchess"]] == [
        types.SILENT_ANOTHER_NIGHTFARER]
    assert [line.text for line in said["Wylder"]] == [
        f"{name}: no number here shows what this adds."], (
        "an effect whose owner is the Nightfarer being played works, and "
        "must never be reported as another Nightfarer's")


def test_an_effect_waiting_on_a_condition_says_so_in_both_places(game_data,
                                                                 wylder,
                                                                 armament):
    """AK-154: the line and the list at the end come out of one set.

    `Build.situational` with `live == False` is that set. Declaring the
    condition met has to empty both in the **same** run -- two separate
    findings of one fact is QA-082 and QA-087, and this project has paid for
    that twice.
    """
    waiting = advisor.a_declarable_effect(game_data, wylder)
    problem = advisor.problem([advisor.RED])
    chosen = (a_copy(0, 1, "A relic", [waiting]),)
    name = effect_names(game_data, [waiting]).pop()

    def both(declared):
        ctx = advisor.context(game_data, wylder, reference=armament,
                              declared=declared)
        built = evaluate(problem, chosen, ctx)
        groups = explain.reasons(problem, chosen, evaluate(problem, (), ctx),
                                 built, ctx, goals.GOALS[DAMAGE])
        return lines_of(groups), explain.not_counted(built)

    waiting_lines, waiting_list = both(())
    declared_lines, declared_list = both(((waiting, 1),))

    assert waiting_lines == (
        f"{name}: only applies under a condition, so no number here.",)
    assert name in waiting_list
    assert name not in declared_list, (
        "the condition was declared met and the list at the end of the "
        "dialog still calls it uncounted")
    assert not any("under a condition" in line for line in declared_lines), (
        f"the condition was declared met and the line under the relic still "
        f"says it is waiting: {declared_lines}")


def test_an_effect_bound_to_the_armaments_says_that_and_not_the_remainder(
        game_data, wylder, armament):
    """QA-104's family, and why it is not the leftover filling.

    What such an effect is worth is a question about the grid -- carry the
    matching armament and it counts. `no number here shows what this adds.`
    would be true and useless: it hides the one thing the player can do
    about it.
    """
    bound = an_armament_bound_effect_that_moves_no_number(game_data, wylder)
    problem = advisor.problem([advisor.RED])
    ctx = advisor.context(game_data, wylder, reference=armament)
    chosen = (a_copy(0, 1, "A relic", [bound]),)

    groups = explain.reasons(problem, chosen, evaluate(problem, (), ctx),
                             evaluate(problem, chosen, ctx), ctx,
                             goals.GOALS[DAMAGE])

    name = effect_names(game_data, [bound]).pop()
    assert lines_of(groups) == (
        f"{name}: it depends on the armaments you carry, so no number here.",)
    assert [line.silence for line in groups[0].lines] == [
        types.SILENT_ARMAMENT_BOUND]


def test_an_effect_that_fits_two_fillings_takes_the_earlier_one(game_data,
                                                                wylder,
                                                                armament):
    """AK-152: the first filling that fits wins, in the order T-080 §4 sets.

    `Improved Attack Power with 3+ Bows Equipped` fits two of them at once --
    it is a switch the player can declare, and what it is worth is a question
    about the armaments. The order decides, and it decides for the switch:
    the player can turn that one on and see the number, which is the more
    useful half. 226 effects of this dataset carry both, so this is not a
    corner.
    """
    fits_both = an_effect_that_is_both_a_switch_and_armament_bound(game_data,
                                                                   wylder)
    problem = advisor.problem([advisor.RED])
    ctx = advisor.context(game_data, wylder, reference=armament)
    chosen = (a_copy(0, 1, "A relic", [fits_both]),)

    group, = explain.reasons(problem, chosen, evaluate(problem, (), ctx),
                             evaluate(problem, chosen, ctx), ctx,
                             goals.GOALS[DAMAGE])

    name = effect_names(game_data, [fits_both]).pop()
    assert lines_of((group,)) == (
        f"{name}: only applies under a condition, so no number here.",)


def an_effect_that_is_both_a_switch_and_armament_bound(data: dict,
                                                       hero: dict) -> int:
    """An effect the model parks as a switch **and** gates on the armaments.

    Both halves asked of the model: `Build.situational` for the switch, and
    `model.GATE_FIELDS`' own wording for the armament family.
    """
    curves = data.get("curves", {})
    wanted = {field_name for field_name, why in model.GATE_FIELDS.items()
              if "weapon" in why or "armament" in why}
    for key in sorted(data["effects"], key=int):
        effect = data["effects"][key]
        if not any(gate in (effect.get("modifiers") or {})
                   for gate in wanted):
            continue
        build = model.compute(hero, advisor.LEVEL, [effect], curves)
        if build.sources:
            continue
        if any(not entry.live for entry in build.situational):
            return int(effect["id"])
    pytest.skip("no effect of this dataset is both a switch and bound to the "
                "armaments, so the order of the fillings has no case here")


def test_a_silent_effect_is_no_curse_and_carries_no_warning(game_data,
                                                            wylder,
                                                            armament):
    """AK-156: it costs nothing, it brings nothing here.

    The marks belong to what they mean: `✦` and `CURSE` to a price, `⚠` to an
    effect the game refuses to stack. A silent effect is neither, and the
    window can only know that from the shape -- which is why `is_curse` is a
    field and not a character in the sentence.
    """
    quiet = an_effect_that_moves_no_number(game_data, wylder)
    problem = advisor.problem([advisor.RED])
    ctx = advisor.context(game_data, wylder, reference=armament)
    chosen = (a_copy(0, 1, "A relic", [quiet]),)

    groups = explain.reasons(problem, chosen, evaluate(problem, (), ctx),
                             evaluate(problem, chosen, ctx), ctx,
                             goals.GOALS[DAMAGE])

    line, = groups[0].lines
    assert not line.is_curse
    assert line.silence == types.SILENT_NO_NUMBER_HERE
    for mark in ("✦", "⚠", "CURSE", "BAD"):
        assert mark not in line.text, (
            f"a silent effect carries {mark!r}, which the window uses for a "
            f"price or for a refusal to stack: {line.text!r}")
    assert line.text.endswith("."), (
        "a line that ends on a sentence carries a full stop (AK-136)")


def test_the_two_lists_of_what_carried_no_figure_are_the_lines_themselves(
        game_data, wylder, armament):
    """AK-139 and AK-153, including the direction that is easy to skip.

    An effect **with** a figure is in neither list, and a **curse** with one
    is not in the curse list either -- the direction that is easy to leave
    out, and a list of every curse would pass every other assertion here.
    The curses and the effects are two lists and not one: the status line
    says `2 curses carry no number.` about the first and nothing at all about
    the second.
    """
    quiet = an_effect_that_moves_no_number(game_data, wylder)
    loud = advisor.raising_effects(game_data, wylder, 1)[0]
    silent_curse = a_curse_that_moves_no_number(game_data, wylder)
    biting, _lowered = a_curse_this_armament_cannot_feel(
        game_data, wylder, armament.weapon)
    problem = advisor.problem([advisor.RED])
    ctx = advisor.context(game_data, wylder, reference=armament)
    chosen = (a_copy(0, 1, "A relic", tuple(loud) + (quiet,),
                     [biting, silent_curse]),)

    groups = explain.reasons(problem, chosen, evaluate(problem, (), ctx),
                             evaluate(problem, chosen, ctx), ctx,
                             goals.GOALS[SURVIVAL])

    biting_name = effect_names(game_data, [biting]).pop()
    assert any(line.is_curse and biting_name in line.text
               and line.silence == types.CARRIES_A_FIGURE
               for group in groups for line in group.lines), (
        f"{biting_name!r} moved no figure in this build, so this case cannot "
        f"tell a list of the silent curses from a list of all of them")
    loud_name = effect_names(game_data, loud).pop()
    quiet_name = effect_names(game_data, [quiet]).pop()
    curse_name = effect_names(game_data, [silent_curse]).pop()
    assert [line.text for line
            in explain.effects_without_a_figure(groups)] == [
        f"{quiet_name}: no number here shows what this adds."]
    assert [line.text for line
            in explain.curses_without_a_figure(groups)] == [
        f"{curse_name}: no number here shows what this costs."]
    assert not any(loud_name in line.text
                   for line in explain.effects_without_a_figure(groups)
                   + explain.curses_without_a_figure(groups)), (
        "an effect that moved a figure is listed as having moved none")


def test_a_line_that_ends_on_a_figure_carries_no_full_stop(game_data, wylder,
                                                           armament):
    """AK-136's punctuation rule, over every line of one real suggestion.

    A line ending on a figure is a value and takes no full stop -- the stat
    sheet sets none either, and this reasoning is read beside it. A line
    ending on a sentence takes one. `, counted against it` is the one ending
    that is neither a figure nor a sentence, and it goes without: it is a
    clause on the value in front of it.
    """
    loud = advisor.raising_effects(game_data, wylder, 1)[0]
    quiet = an_effect_that_moves_no_number(game_data, wylder)
    biting, _lowered = a_curse_this_armament_cannot_feel(
        game_data, wylder, armament.weapon)
    silent_curse = a_curse_that_moves_no_number(game_data, wylder)
    problem = advisor.problem([advisor.RED])
    ctx = advisor.context(game_data, wylder, reference=armament)
    chosen = (a_copy(0, 1, "A relic", tuple(loud) + (quiet,),
                     [biting, silent_curse]),)
    groups = explain.reasons(problem, chosen, evaluate(problem, (), ctx),
                             evaluate(problem, chosen, ctx), ctx,
                             goals.GOALS[SURVIVAL])

    seen = set()
    for line in [one for group in groups for one in group.lines]:
        a_value = line.text.endswith("counted against it") or (
            line.text[-1] in "0123456789%")
        seen.add(a_value)
        assert a_value != line.text.endswith("."), (
            f"this line ends on {'a value' if a_value else 'a sentence'} and "
            f"punctuates it the other way round: {line.text!r}")
    for group in groups:
        assert group.count_line.endswith("."), group.count_line
    assert seen == {True, False}, (
        f"this suggestion has only one kind of ending, so the case says "
        f"nothing about the other: {lines_of(groups)}")


def test_the_advisor_carries_none_of_the_barred_sentences_at_all():
    """AK-133, AK-140, AK-142 and AK-157, searched over the module itself.

    The case above reads one run; this one reads the source, so a sentence
    that only appears for a dataset nobody here owns cannot hide. `Chosen
    for` was the summary the block used to promise (T-078 §1 struck it, and
    it cannot be written honestly: it claims a rank among contributions that
    no exchange rate in the game files supports). The other two are claims
    about the game files that are simply false for `All Resistances Down`.
    """
    barred = ("Chosen for", "carry no numbers", "carries no numbers",
              "counted for nothing:")
    advisor_package = pathlib.Path(explain.__file__).parent

    found = {}
    for module in sorted(advisor_package.glob("*.py")):
        text = module.read_text(encoding="utf-8")
        for sentence in barred:
            if sentence in text:
                found.setdefault(sentence, []).append(module.name)

    assert not found, (
        f"the advisor carries sentences it is not allowed to say, even in a "
        f"comment where the next reader will copy them: {found}")


def test_the_advisor_says_nothing_about_the_game_files_and_no_jargon(
        game_data, wylder, armament):
    """AK-140, AK-144 and AK-157 over the text of one real run.

    Two claims, and the first is about truth rather than tone: `the game
    files carry no numbers for these` is **false** for `All Resistances
    Down`, which lowers seven resistances by 80 apiece and is merely not
    read by anything the advisor consults. What the lines say instead is
    that no number stands here.

    The second is A11's vocabulary list. It is asked of the wording this
    module composes, with the names of the effects taken out of the text
    first: a relic called something with `Field` in it would be the
    dataset's word, not the program's, and failing on it would train the
    next reader to loosen the check.
    """
    barred = ("field", "pool", "handle", "beam", "scorer", "source",
              "snapshot", "slot_index", "not_counted", "contribution")
    inventory = advisor.make_inventory(game_data, wylder, colour=advisor.RED,
                                       count=6)
    problem = advisor.problem([advisor.RED, advisor.RED])
    ctx = advisor.context(game_data, wylder, reference=armament)
    pools = candidates.pools(inventory, problem, ctx, goals.GOALS, DAMAGE)
    found = search.beam(problem, pools, types.DEFAULT_BUDGET,
                        search.goal_scorer(problem, ctx, goals.GOALS[DAMAGE]))
    chosen = explain.chosen_for(found[0], pools)
    built = evaluate(problem, chosen, ctx)
    groups = explain.reasons(problem, chosen, evaluate(problem, (), ctx),
                             built, ctx, goals.GOALS[DAMAGE])

    shown = list(lines_of(groups)) + [group.count_line for group in groups]
    shown += list(explain.unknowns(problem)) + [explain.data_note(ctx)]
    assert shown, "nothing was said, so nothing is being read here"

    for text in shown:
        assert "carry no numbers" not in text and (
            "carries no numbers" not in text), text
    names = set()
    for choice in found[0].choices:
        copy = owned_by_handle(inventory, choice.handle)
        names |= effect_names(game_data, copy.effect_ids + copy.curse_ids)
        names.add(copy.name)
    for text in shown:
        stripped = text.lower()
        for name in names:
            stripped = stripped.replace(name.lower(), " ")
        words = set(stripped.translate(
            str.maketrans(",.:—-%", "      ")).split())
        for word in barred:
            assert word not in words, (
                f"the advisor says {word!r} to the player: {text!r}")


# -- the heading of a slot group --------------------------------------------

def test_the_heading_counts_effects_and_not_the_lines_they_produced():
    """AK-146: one effect that moves two figures is two lines and one effect.

    Counting lines instead would say `2 of its 1 effects`, which is not a
    sentence anybody can act on, and it would break the arithmetic the
    heading exists for.
    """
    ctx = a_context({1: "Physical Attack Up"})
    built = a_build({"physicsAttackRate": [("Physical Attack Up", 1.12, 1)],
                     "Strength": [("Physical Attack Up", 3, 1)]},
                    rates=("physicsAttackRate",))

    group, = explain.reasons(a_vessel(1), (a_copy(0, 1, "A relic", [1]),),
                             a_build({}), built, ctx, goals.GOALS[DAMAGE])

    assert len(group.lines) == 2
    assert (group.effects_total, group.effects_with_a_figure) == (1, 1)
    assert group.count_line == "Its one effect moved a number in this build."


@pytest.mark.parametrize("effects,moved,wording", [
    ((), (), "This relic carries no effects of its own."),
    ((1,), (), "Nothing on this relic moved a number in this build — it "
               "fills the slot without changing the figure."),
    ((1,), (1,), "Its one effect moved a number in this build."),
    ((1, 2), (2,), "1 of its 2 effects moved a number in this build."),
    ((1, 2), (1, 2), "All 2 of its effects moved a number in this build."),
])
def test_the_heading_of_a_group_says_which_case_this_is(effects, moved,
                                                        wording):
    """The fillings of `UI_SPEC` T-078 §6 and T-080 §5, written out here.

    Stated rather than imported: a case that asked the module for the
    sentence it is checking would agree with whatever the module said.

    `Murk`, `Sovereign Sigil` and `Scenic Flatstone` are the three relics of
    this dataset with no effect role at all -- the first filling is theirs
    and it is not hypothetical.
    """
    ctx = a_context({1: "First", 2: "Second"})
    built = a_build({f"field{one}": [(f"{'First' if one == 1 else 'Second'}",
                                      one, one)] for one in moved})

    group, = explain.reasons(a_vessel(1),
                             (a_copy(0, 1, "A relic", effects),),
                             a_build({}), built, ctx, goals.GOALS[DAMAGE])

    assert group.count_line == wording
    assert group.effects_total - group.effects_with_a_figure == len(
        [line for line in group.lines
         if line.silence != types.CARRIES_A_FIGURE]), (
        f"the heading claims {group.effects_with_a_figure} of "
        f"{group.effects_total} moved a number, and the silent lines below "
        f"it do not add up to the difference (AK-155): "
        f"{lines_of((group,))}")


def test_a_copy_whose_curse_moved_a_number_is_not_told_nothing_moved(
        game_data, wylder, armament):
    """The second new filling stops at the curses, and this is why.

    `Nothing on this relic moved a number in this build` would be false where
    a curse moved one: the figure did change, downwards. What the heading
    then says is that none of its **effects** did, and the curse line below
    speaks for itself.
    """
    biting, _lowered = a_curse_this_armament_cannot_feel(
        game_data, wylder, armament.weapon)
    quiet = an_effect_that_moves_no_number(game_data, wylder)
    problem = advisor.problem([advisor.RED])
    ctx = advisor.context(game_data, wylder, reference=armament)
    chosen = (a_copy(0, 1, "Cursed copy", [quiet], [biting]),)

    group, = explain.reasons(problem, chosen, evaluate(problem, (), ctx),
                             evaluate(problem, chosen, ctx), ctx,
                             goals.GOALS[SURVIVAL])

    assert group.count_line == (
        "Its one effect moved no number in this build.")
    assert group.effects_with_a_figure == 0
    assert with_a_figure((group,)), (
        "the curse moved no figure either, so this case cannot tell the two "
        "headings apart")


# -- the run findings -------------------------------------------------------

def test_a_curse_the_direction_cannot_feel_is_named(game_data, wylder,
                                                     armament):
    """AD-015's mandatory line, and the same curse under the other direction.

    A curse that takes an attribute away moves effective HP and does not move
    an attack rating that scales on something else. Under `Minimise damage
    taken` it is in the ranking figure and needs no line; under `Maximise
    damage` the suggestion block is the only place it becomes visible at all.
    One curse, two directions -- so the case cannot pass by naming everything
    or nothing.
    """
    biting, lowered = a_curse_this_armament_cannot_feel(
        game_data, wylder, armament.weapon)
    problem = advisor.problem([advisor.RED])
    ctx = advisor.context(game_data, wylder, reference=armament)
    chosen = (a_copy(0, 1, "Cursed copy", (), [biting]),)
    base = evaluate(problem, (), ctx)
    built = evaluate(problem, chosen, ctx)

    assert base.derived["HP"] != built.derived["HP"], (
        f"this curse lowers {lowered} and leaves HP where it was, so the "
        f"survival direction cannot feel it either and there is no contrast "
        f"in this case")

    blind = lines_of(explain.reasons(problem, chosen, base, built, ctx,
                                     goals.GOALS[DAMAGE]))
    feeling = lines_of(explain.reasons(problem, chosen, base, built, ctx,
                                       goals.GOALS[SURVIVAL]))

    name = effect_names(game_data, [biting]).pop()
    assert blind and all(
        line.startswith(f"{name}: ")
        and line.endswith(" — this figure does not count it.")
        for line in blind), blind
    assert feeling and not any("does not count it" in line
                               for line in feeling), (
        f"the direction that ranks on the HP this curse moved was told it "
        f"does not rank it: {feeling}")
    assert all("counted against it" in line for line in feeling), (
        f"the direction that does feel the curse has to say it was charged "
        f"for it (F3): {feeling}")
    assert explain.unknowns(problem) == (), (
        "nothing was held, and the curse now speaks for itself in its own "
        "group instead of a second time at the end of the dialog")


def test_the_held_slots_are_named_with_a_count(game_data, wylder, armament):
    """A run finding in the sense of AD-025: it carries a count.

    The search ran over fewer slots than the vessel has, and a result that
    did not say so would read as a search over all of them.
    """
    inventory = advisor.make_inventory(game_data, wylder, colour=advisor.RED,
                                       count=2)
    kept = inventory.relics_for(advisor.RED, False)[0]
    problem = advisor.problem([advisor.RED, advisor.RED, advisor.RED],
                              held={0: advisor.held_relic(kept)})
    ctx = advisor.context(game_data, wylder, reference=armament)
    base = evaluate(problem, (), ctx)

    lines = explain.unknowns(problem)

    assert lines == ("1 of 3 slots is held, so only the other 2 were filled.",)


def test_the_two_counts_of_the_held_line_each_take_their_own_verb(game_data,
                                                                  wylder,
                                                                  armament):
    """QA-183: `is`/`are` follows the held slots, `was`/`were` the rest.

    One held slot of two leaves one filled, and the sentence carried the
    singular in front and the plural behind: `1 of 2 slots is held, so only
    the other 1 were filled.` The two numbers are different numbers, and the
    case that saw it needs a vessel where they disagree -- on three slots
    both halves read plural and the fault is invisible.
    """
    inventory = advisor.make_inventory(game_data, wylder, colour=advisor.RED,
                                       count=2)
    kept = inventory.relics_for(advisor.RED, False)[0]
    problem = advisor.problem([advisor.RED, advisor.RED],
                              held={0: advisor.held_relic(kept)})
    ctx = advisor.context(game_data, wylder, reference=armament)
    base = evaluate(problem, (), ctx)

    lines = explain.unknowns(problem)

    assert lines == ("1 of 2 slots is held, so only the other 1 was filled.",)


def test_every_slot_held_says_that_nothing_was_searched(game_data, wylder,
                                                        armament):
    """Checkpoint 14: with everything held the answer is the build as it is.

    The search says so by returning that build with its figure; this line is
    the half the player reads. `2 of 2 slots are held` would be true and
    would leave the reader to work out that nothing was searched at all.

    The last three words are the correction of T-078 §8: the sentence ended
    on `scored.`, a participle standing alone, where A11 asks for the word
    the player sees on the screen beside it.
    """
    inventory = advisor.make_inventory(game_data, wylder, colour=advisor.RED,
                                       count=2)
    worn, other = inventory.relics_for(advisor.RED, False)
    problem = advisor.problem(
        [advisor.RED, advisor.RED],
        held={0: advisor.held_relic(worn), 1: advisor.held_relic(other)})
    ctx = advisor.context(game_data, wylder, reference=armament)
    base = evaluate(problem, (), ctx)

    lines = explain.unknowns(problem)

    assert lines == ("All 2 slots are held, so there was nothing to search — "
                     "this is your build as it stands, with its figure.",)


def test_a_run_that_left_nothing_out_says_nothing():
    """Empty is a statement, not an omission (AD-025.2).

    Nothing was held, so there is no run finding to carry. The procedural
    sentences of the direction are not here at all -- they are read off
    `Goal.scope`, once for the screen (AK-50).
    """
    lines = explain.unknowns(advisor.problem([advisor.RED, advisor.RED]))

    assert lines == ()
    assert goals.GOALS[DAMAGE].scope, (
        "the direction carries no scope either, so this case says nothing "
        "about where the two kinds of sentence live")


# -- what went into no total ------------------------------------------------

def test_a_condition_the_player_declared_is_not_reported_as_uncounted(
        game_data, wylder, armament):
    """`not_counted` is read off what `model.compute` actually parked.

    Declaring the condition is the one thing the sheet cannot work out for
    itself, and it changes whether the effect counted. Reading the effect
    records instead would report a counted effect as uncounted -- and the
    figure beside it would already contain it.
    """
    gated = advisor.a_gated_attribute_effect(game_data, wylder)
    problem = advisor.problem([advisor.RED])
    chosen = (a_copy(0, 1, "A relic", [gated]),)
    name = effect_names(game_data, [gated]).pop()

    silent = advisor.context(game_data, wylder, reference=armament)
    declared = advisor.context(game_data, wylder, reference=armament,
                               declared=((gated, 1),))

    assert name in explain.not_counted(evaluate(problem, chosen, silent))
    assert name not in explain.not_counted(evaluate(problem, chosen,
                                                    declared))


def test_what_was_not_counted_keeps_its_number_and_its_order():
    """AD-010 asks for a count, so the duplicates and the order are the point.

    Two relics carrying one uncounted condition are two effects that did not
    count, and `len(not_counted)` is what AD-010 asks for. The order is the
    one `model.compute` parked them in, which is the order the relics sit in.

    Stated rather than computed, and stated so that the two ways of losing it
    are different answers: run through a `set()` the list would be two long
    instead of three, and sorted it would lead with `Alpha`. Neither is
    visible to a case that only asks whether a name is in the list -- which
    was the whole of what watched this, and is why the two edits above
    survived a full run (QA-182).
    """
    def gated(effect_id: int, name: str, count: int = 0) -> model.Situational:
        return model.Situational(effect_id=effect_id, name=name,
                                 detail="under some condition",
                                 why="the sheet cannot know",
                                 accumulates=False, count=count)

    built = model.Build(situational=[
        gated(30, "Gamma"),
        gated(10, "Alpha", count=1),
        gated(11, "Alpha"),
        gated(12, "Alpha"),
    ])

    assert explain.not_counted(built) == ("Gamma", "Alpha", "Alpha")


# -- where the numbers came from --------------------------------------------

def test_the_data_note_names_the_version_and_where_it_was_read(game_data,
                                                               wylder):
    """AD-010, F7: two different reasons to distrust a figure.

    Which version of the game's data, and **when** it was read from the
    installation. `datasource` marks a fresh extraction with `regenerated`.

    The wording is `UI_SPEC` T-078 §8 and it is written out here rather than
    imported: a case that asks the module for the sentence it is checking
    agrees with whatever the module says.
    """
    stored = advisor.context(game_data, wylder)
    version = game_data["meta"]["data_version"]

    assert explain.data_note(stored) == (
        f"Ranked on game data version {version}, read from your game files "
        f"earlier and kept since.")

    fresh = dict(game_data, meta=dict(game_data["meta"], regenerated=True))
    assert explain.data_note(
        advisor.context(fresh, wylder)) == (
        f"Ranked on game data version {version}, read from your game files "
        f"just now.")


def test_the_data_note_says_when_and_never_where_it_is_kept(game_data,
                                                            wylder):
    """The word `snapshot` is barred from the advisor's own sentences.

    AK-127 keeps it off the first-run screen because a player does not know
    what a stored snapshot is, and a word that has to be avoided in one place
    is not honest in another (T-078 §8). What the note has to answer is
    *when*, not *where it lives*.
    """
    fresh = dict(game_data, meta=dict(game_data["meta"], regenerated=True))
    notes = (explain.data_note(advisor.context(game_data, wylder)),
             explain.data_note(advisor.context(fresh, wylder)),
             explain.data_note(advisor.context(dict(game_data, meta={}),
                                               wylder)))

    for note in notes:
        assert "snapshot" not in note.lower(), note
    assert all(("just now" in note) != ("earlier and kept since" in note)
               for note in notes), (
        f"every filling says when the data was read, and says it once: "
        f"{notes}")


def test_a_dataset_that_records_no_version_says_so(game_data, wylder):
    """A7: where the data gives no answer, the program says so.

    An empty version silently interpolated reads as a version, and every
    figure of the run would then claim a provenance it does not have. The
    sentence still carries the time, because that half is known.
    """
    nameless = advisor.context(dict(game_data, meta={}), wylder)

    assert explain.data_note(nameless) == (
        "Ranked on game data read from your game files earlier and kept "
        "since. It does not say which game version it is from, so these "
        "figures cannot be tied to a patch.")


# -- reading a suggestion back ----------------------------------------------

def test_a_suggestion_is_read_back_as_the_copies_it_came_from(game_data,
                                                              wylder,
                                                              armament):
    """`SlotChoice` carries what applies a relic, not what explains one.

    The roll stays in the pools the search consumed, and it is looked up
    there rather than carried a second time beside the suggestion: a second
    copy of one fact is a second thing to keep in step, and QA-107 is what
    that cost here already.
    """
    inventory = advisor.make_inventory(game_data, wylder, colour=advisor.RED,
                                       count=3)
    problem = advisor.problem([advisor.RED, advisor.RED])
    ctx = advisor.context(game_data, wylder, reference=armament)
    pools = candidates.pools(inventory, problem, ctx, goals.GOALS, DAMAGE)
    found = search.beam(problem, pools, types.DEFAULT_BUDGET,
                        search.goal_scorer(problem, ctx, goals.GOALS[DAMAGE]))

    chosen = explain.chosen_for(found[0], pools)

    assert [copy.handle for copy in chosen] == [choice.handle for choice
                                                in found[0].choices]
    for copy, choice in zip(chosen, found[0].choices):
        owned = owned_by_handle(inventory, choice.handle)
        assert copy.effect_ids == tuple(owned.effect_ids)


def test_a_suggestion_from_another_run_is_refused(game_data, wylder,
                                                  armament):
    """Explaining one run's answer with another run's pools names the wrong
    effects.

    Loud, because the failure is otherwise a reasoning that reads perfectly
    and describes a build nobody has.
    """
    inventory = advisor.make_inventory(game_data, wylder, colour=advisor.RED,
                                       count=3)
    problem = advisor.problem([advisor.RED, advisor.RED])
    ctx = advisor.context(game_data, wylder, reference=armament)
    pools = candidates.pools(inventory, problem, ctx, goals.GOALS, DAMAGE)
    found = search.beam(problem, pools, types.DEFAULT_BUDGET,
                        search.goal_scorer(problem, ctx, goals.GOALS[DAMAGE]))

    with pytest.raises(KeyError, match="no pool"):
        explain.chosen_for(found[0], pools[:1])

    stranger = types.Suggestion(
        choices=(types.SlotChoice(slot_index=0, handle=999, relic_id=1,
                                  name="Not on offer"),),
        score=found[0].score)
    with pytest.raises(KeyError, match="does not offer"):
        explain.chosen_for(stranger, pools)
