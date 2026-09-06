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

import pytest

from nrplanner import model
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

    lines = explain.reasons(chosen, evaluate(problem, (), ctx),
                            evaluate(problem, chosen, ctx), ctx)

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

    lines = explain.reasons(chosen, evaluate(problem, (), ctx),
                            evaluate(problem, chosen, ctx), ctx)

    name = effect_names(game_data, roll).pop()
    named = [line for line in lines if name in line]
    assert len(named) == 3, (
        f"three copies carry {name!r}; it is named in {len(named)} lines: "
        f"{named}")
    assert sorted(line.split(",")[0] for line in named) == [
        "Slot 1", "Slot 2", "Slot 3"]


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

    assert explain.reasons(chosen, base, built, ctx) == (), (
        "the chosen copy was credited with the held relic's contribution")


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

    lines = explain.reasons(chosen, evaluate(problem, (), ctx),
                            evaluate(problem, chosen, ctx), ctx)

    assert [line for line in lines if line.startswith("Slot 1")], (
        "the first copy was not credited with the effect it did contribute")
    assert not [line for line in lines if line.startswith("Slot 2")], (
        f"the second copy of a non-stacking effect was credited with "
        f"something: {lines}")


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

    lines = explain.reasons((a_copy(0, 1, "Vigor relic", [7000090]),
                             a_copy(1, 2, "Max HP relic", [6610400])),
                            a_build({}), built, ctx)

    assert lines == (
        "Slot 1, Vigor relic — Increased Maximum HP: Vigor +5",
        "Slot 2, Max HP relic — Increased Maximum HP: Max HP +10.0%",
    )


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

    lines = explain.reasons(chosen, evaluate(problem, (), ctx),
                            evaluate(problem, chosen, ctx), ctx)

    assert effect_names(game_data, [first]) == effect_names(game_data,
                                                            [second]), (
        "the two effects no longer share a name, so this case cannot tell an "
        "attribution by name from one by id")
    for slot, effect_id in ((1, first), (2, second)):
        labels = labels_moved_by(game_data, wylder, effect_id)
        said = [line for line in lines if line.startswith(f"Slot {slot},")]
        assert said, (
            f"slot {slot} carries an effect that moves {sorted(labels)} and "
            f"the reasoning says nothing about it at all: {lines}")
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

    lines = explain.reasons((a_copy(0, 1, "A relic", [1]),), a_build({}),
                            built, ctx)

    assert lines == (
        "Slot 1, A relic — Physical Attack Up: Physical Attack +12.0%",
        "Slot 1, A relic — Physical Attack Up: Strength +3",
    )


def test_a_figure_that_is_better_small_is_not_called_a_cost_for_falling():
    """`GOAL.md` F3 needs the direction, and the sign does not carry it.

    A damage-cut rate at 0.85 is 15 % less damage taken, and an FP cost at
    0.92 is 8 % cheaper: both fall and both are gains. A flask that restores
    15 % less falls the same way and is a loss. `model.is_better_lower` is the
    one place that knows which is which.
    """
    ctx = a_context({1: "Improved Fire Damage Negation +1",
                    2: "Reduced Flask HP Restoration"})
    built = a_build(
        {"fireDamageCutRate": [("Improved Fire Damage Negation +1", 0.85, 1)],
         "changeHpEstusFlaskCorrectRate": [("Reduced Flask HP Restoration",
                                            0.85, 2)]},
        rates=("fireDamageCutRate", "changeHpEstusFlaskCorrectRate"))

    lines = explain.reasons((a_copy(0, 1, "A relic", [1], [2]),), a_build({}),
                            built, ctx)

    assert lines == (
        "Slot 1, A relic — Improved Fire Damage Negation +1: "
        "Fire damage taken -15.0%",
        "Slot 1, A relic — Reduced Flask HP Restoration: "
        "HP restored per flask -15.0%, counted against it",
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

    assert explain.reasons((a_copy(0, 1, "A relic", [1]),), a_build({}),
                           built, ctx) == ()


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

    lines = explain.reasons((a_copy(0, 1, "A relic", [1]),), a_build({}),
                            built, ctx)

    assert lines == (
        "Slot 1, A relic — Reduced FP Consumption: Skill FP cost -8.0%",
        "Slot 1, A relic — Reduced FP Consumption: Spell FP cost -8.0%",
        "Slot 1, A relic — Reduced FP Consumption: Item use cost -8.0%",
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

    lines = explain.reasons((a_copy(0, 1, "A relic", [1]),), a_build({}),
                            built, ctx)

    assert lines == (
        "Slot 1, A relic — Improved Melee Attack Power: "
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

    lines = explain.reasons((a_copy(0, 1, "A relic", [1]),), a_build({}),
                            built, ctx)

    assert lines == (
        "Slot 1, A relic — Improved Skill Attack Power: +15.0%",
    )


def test_an_effect_this_dataset_does_not_carry_is_named_nowhere():
    """`evaluate` skips an unknown id, so it moved nothing to explain.

    Inherited from `Planner.selected_effects` on purpose rather than solved
    in a second place (P4, QA-004/QA-032). What must not happen is a line
    about it: a reasoning that names an effect the calculation never saw is
    the fault this step is accepted against.
    """
    ctx = a_context({1: "Known"})
    built = a_build({"Strength": [("Known", 3, 1)]})

    lines = explain.reasons((a_copy(0, 1, "A relic", [1, 4242]),),
                            a_build({}), built, ctx)

    assert lines == ("Slot 1, A relic — Known: Strength +3",)


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
    """
    biting = cases.curses_lowering_an_attribute(game_data, wylder, 1)[0]
    problem = advisor.problem([advisor.RED])
    ctx = advisor.context(game_data, wylder, reference=armament)
    chosen = (a_copy(0, 1, "Cursed copy", (), [biting]),)

    lines = explain.reasons(chosen, evaluate(problem, (), ctx),
                            evaluate(problem, chosen, ctx), ctx)

    name = effect_names(game_data, [biting]).pop()
    charged = [line for line in lines if name in line]
    assert charged, f"the curse is named nowhere in the reasoning: {lines}"
    assert all("counted against it" in line for line in charged), (
        f"a curse that lowers an attribute is not marked as counted against "
        f"the relic: {charged}")


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

    blind = explain.unknowns(problem, chosen, base, built, ctx,
                             goals.GOALS[DAMAGE])
    feeling = explain.unknowns(problem, chosen, base, built, ctx,
                               goals.GOALS[SURVIVAL])

    assert blind and all(line.startswith("A curse on Cursed copy changes ")
                         and line.endswith("which this goal does not rank.")
                         for line in blind), blind
    assert feeling == (), (
        f"the direction that ranks on the HP this curse moved was told it "
        f"does not rank it: {feeling}")


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

    lines = explain.unknowns(problem, (), base, base, ctx,
                             goals.GOALS[DAMAGE])

    assert lines == ("1 of 3 slots is held, so only the other 2 were filled.",)


def test_every_slot_held_says_that_nothing_was_searched(game_data, wylder,
                                                        armament):
    """Checkpoint 14: with everything held the answer is the build as it is.

    The search says so by returning that build, scored; this line is the half
    the player reads. `2 of 2 slots are held` would be true and would leave
    the reader to work out that nothing was searched at all.
    """
    inventory = advisor.make_inventory(game_data, wylder, colour=advisor.RED,
                                       count=2)
    worn, other = inventory.relics_for(advisor.RED, False)
    problem = advisor.problem(
        [advisor.RED, advisor.RED],
        held={0: advisor.held_relic(worn), 1: advisor.held_relic(other)})
    ctx = advisor.context(game_data, wylder, reference=armament)
    base = evaluate(problem, (), ctx)

    lines = explain.unknowns(problem, (), base, base, ctx,
                             goals.GOALS[DAMAGE])

    assert lines == ("All 2 slots are held, so nothing was searched: this is "
                     "the build as it stands, scored.",)


def test_a_run_that_left_nothing_out_says_nothing(game_data, wylder,
                                                  armament):
    """Empty is a statement, not an omission (AD-025.2).

    Nothing was held and no curse fell outside the figure, so there is no run
    finding to carry. The procedural sentences of the direction are not here
    at all -- they are read off `Goal.scope`, once for the screen (AK-50).
    """
    roll = advisor.raising_effects(game_data, wylder, 1)[0]
    problem = advisor.problem([advisor.RED])
    ctx = advisor.context(game_data, wylder, reference=armament)
    chosen = (a_copy(0, 1, "A relic", roll),)

    lines = explain.unknowns(problem, chosen, evaluate(problem, (), ctx),
                             evaluate(problem, chosen, ctx), ctx,
                             goals.GOALS[DAMAGE])

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


# -- where the numbers came from --------------------------------------------

def test_the_data_note_names_the_version_and_where_it_was_read(game_data,
                                                               wylder):
    """AD-010, F7: two different reasons to distrust a figure.

    Which version of the game's data, and whether it was read from the
    installation now or has been sitting in a snapshot since the last patch.
    `datasource` marks a fresh extraction with `regenerated`.
    """
    stored = advisor.context(game_data, wylder)
    version = game_data["meta"]["data_version"]

    assert explain.data_note(stored) == (
        f"Ranked on game data version {version}, from the stored snapshot.")

    fresh = dict(game_data, meta=dict(game_data["meta"], regenerated=True))
    assert explain.data_note(
        advisor.context(fresh, wylder)) == (
        f"Ranked on game data version {version}, read from the installed "
        f"game.")


def test_a_dataset_that_records_no_version_says_so(game_data, wylder):
    """A7: where the data gives no answer, the program says so.

    An empty version silently interpolated reads as a version, and every
    figure of the run would then claim a provenance it does not have.
    """
    nameless = advisor.context(dict(game_data, meta={}), wylder)

    assert explain.data_note(nameless) == (
        "Ranked on game data from the stored snapshot, which records no "
        "version, so there is no way to say which patch it is from.")


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
