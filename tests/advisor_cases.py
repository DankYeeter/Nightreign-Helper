"""Building an advisor question a test can state exactly.

The relics here are made rather than read, for the same reason
`tests/relics.py` makes its own: the awkward cases -- a copy with no handle, a
Deep copy sitting beside an ordinary one of the same colour, two copies of one
roll -- have to be *stated*, or a green run means only that this save happens
not to contain them.

The one thing that is **not** made up is the effect an offered relic carries.
Which effect actually moves an attack rating or an HP total is a property of
the dataset, so it is asked of `model.compute` through
`tests/weapon_damage_cases.py`, never assumed from a modifier name. A pool
built on effects that move nothing would rank every candidate at zero and
every assertion about an order would hold vacuously.
"""

from __future__ import annotations

import pytest

from nrplanner import inventory
from nrplanner.advisor import types

from tests import relics as relic_helpers
from tests import weapon_damage_cases as cases

#: The level the ladders in `tests/test_marginal_returns.py` are probed at,
#: reused so two files asking about the same dataset ask at the same point.
LEVEL = cases.PROBE_LEVEL

#: Colour numbers as `model.COLOUR_NAMES` gives them. Named here so the cases
#: below read as colours instead of as digits.
RED, BLUE, WHITE = 0, 1, 4


def deep_templates_for(data: dict, colour: int, count: int) -> list[dict]:
    """Deep of Night relic templates of one colour, lowest ids first.

    The counterpart of `relics.templates_for`, which takes ordinary ones. Both
    are needed at once: the whole point of the Deep separation is that a Deep
    slot and an ordinary slot of the same colour see different relics.
    """
    found = sorted(
        (r for r in data["relics"]
         if r["colour"] == colour and r.get("is_deep")),
        key=lambda r: r["id"],
    )
    if len(found) < count:
        pytest.skip(f"this dataset has fewer than {count} Deep relics of "
                    f"colour {colour}")
    return found[:count]


def raising_effects(data: dict, hero: dict, count: int) -> list[list[int]]:
    """`count` distinct effects that each raise Strength, one per relic.

    Strength because the reference armament below scales on it, so each of
    them moves the damage goal by a different, measurable amount rather than
    by nothing.
    """
    found = cases.effects_raising_attribute(data, hero, "Strength", count)
    return [[effect_id] for effect_id in found]


def a_non_stacking_effect(data: dict, hero: dict, field_name: str) -> int:
    """An effect the game refuses to count twice, that really moves a field.

    `isStrongestEffect`: two copies of it are worth exactly one. That is what
    makes it the sharp case for AD-014.3 -- a candidate carrying it is worth
    nothing beside a held relic that already carries it, and worth something
    beside a build that does not. A pre-sort measured against the wrong
    reference cannot tell those two apart.

    Found by asking `model.compute` for one copy and for two, never by name:
    whether the game stacks an effect is a field on the record, and whether
    the field is honoured is what the model does with it.
    """
    from nrplanner import model

    curves = data.get("curves", {})
    for key in sorted(data["effects"], key=int):
        effect = data["effects"][key]
        if effect.get("stacks"):
            continue
        once = model.compute(hero, LEVEL, [effect], curves)
        twice = model.compute(hero, LEVEL, [effect, effect], curves)
        moved = once.rates.get(field_name, 1.0)
        if abs(moved - 1.0) > 1e-9 and twice.rates.get(field_name) == moved:
            return int(effect["id"])
    raise LookupError(f"this dataset has no non-stacking effect moving "
                      f"{field_name}")


def a_damage_type_conversion(data: dict) -> int:
    """An effect that converts damage from one type into another (QA-113).

    Found through `model.FLAT_ATTACK_POWER_FIELDS`, which is the model's own
    account of the fields it has no compartment for -- asking the model rather
    than naming an id keeps the case pointing at the same thing if the
    dataset's ids move. The lowest id with a negative and a positive entry, so
    it really is a conversion and not a flat bonus.
    """
    from nrplanner import model

    for key in sorted(data["effects"], key=int):
        modifiers = data["effects"][key].get("modifiers") or {}
        moved = [modifiers[name] for name in model.FLAT_ATTACK_POWER_FIELDS
                 if name in modifiers]
        if any(value < 0 for value in moved) and any(value > 0
                                                     for value in moved):
            return int(data["effects"][key]["id"])
    raise LookupError("this dataset carries no damage-type conversion, so "
                      "there is nothing here for QA-113's line to report")


def an_armament_type_gate(data: dict, hero: dict) -> tuple[int, dict, dict]:
    """An effect gated on a weapon type, and two armaments that tell it apart.

    Hands back `(effect id, an armament of the wanted type, an armament of
    another)`. A weapon-type gate is the one input that distinguishes "every
    armament on the grid" from "the one being rated": the gate is met by any
    of them (`model.satisfied_by_weapon`), so an effect gated on the *second*
    armament's type is counted only while the whole grid is passed on.

    Measured through `model.compute` and not read off a modifier name: 102
    effects in this dataset carry such a gate and most of them move no number
    the comparison can see, so a case built on the first one found would
    compare a build with itself.
    """
    from nrplanner import model

    curves = data.get("curves", {})
    present = {weapon.get("wep_type") for weapon in data["weapons"]}
    present.discard(None)
    for key in sorted(data["effects"], key=int):
        effect = data["effects"][key]
        mods = effect.get("modifiers") or {}
        wanted = next((mods[field_name]
                       for field_name in model.WEAPON_TYPE_GATES
                       if mods.get(field_name) in present), None)
        if wanted is None:
            continue
        carrier = next(w for w in data["weapons"]
                       if w.get("wep_type") == wanted)
        other = next((w for w in data["weapons"]
                      if w.get("wep_type") not in (None, wanted)), None)
        if other is None:
            continue
        blind = model.compute(hero, LEVEL, [effect], curves,
                              weapon=other, weapons_held=[other])
        seeing = model.compute(hero, LEVEL, [effect], curves,
                               weapon=other, weapons_held=[other, carrier])
        if (blind.rates != seeing.rates
                or blind.attributes != seeing.attributes):
            return int(effect["id"]), carrier, other
    raise LookupError("this dataset has no weapon-type gate that moves a "
                      "number, so nothing here can tell the whole grid from "
                      "the armament being rated")


def a_declarable_effect(data: dict, hero: dict) -> int:
    """A gated effect the sheet offers this Nightfarer as a switch.

    `Build.situational` is the list the conditional line of a pool counts, and
    an effect reaches it only when its condition is one the player can
    actually be in: another Nightfarer's effect is gated on nothing you can
    do, and `model.compute` leaves it out of the switches for that reason.
    Asked of the model rather than read off a modifier name, because whether
    an effect gets a switch is a decision `compute` makes out of three fields
    at once.
    """
    from nrplanner import model

    curves = data.get("curves", {})
    for key in sorted(data["effects"], key=int):
        effect = data["effects"][key]
        offered = model.compute(hero, LEVEL, [effect], curves).situational
        if any(entry.effect_id == int(effect["id"]) and not entry.live
               for entry in offered):
            return int(effect["id"])
    raise LookupError("this dataset offers no effect as a switch, so nothing "
                      "here can be left uncounted for a stated reason")


def a_gated_attribute_effect(data: dict, hero: dict) -> int:
    """A gated effect that raises an attribute once its condition is declared.

    It has to move an **attribute**: a rate an assertion cannot see would make
    a case pass for a build that received nothing.
    """
    from nrplanner import model

    curves = data.get("curves", {})
    for key in sorted(data["effects"], key=int):
        effect = data["effects"][key]
        if not model.is_conditional(effect, None):
            continue
        silent = model.compute(hero, LEVEL, [effect], curves)
        declared = model.compute(hero, LEVEL, [effect], curves,
                                 declared={int(effect["id"]): 1})
        if declared.attributes != silent.attributes:
            return int(effect["id"])
    raise LookupError("no gated attribute effect in this dataset")


def a_move_scoped_attack_buff(data: dict, hero: dict) -> int:
    """An attack buff the game restricts to one move, in prose only.

    QA-018, closed by the user's measurement in play: "counterattack ist nur
    bei konter, nicht global". The four families are listed by id in
    `model.MOVE_SCOPED_EFFECT_IDS`, and `compute` routes them to a scoped key
    instead of into the flat multiplier -- so they reach no ordinary attack
    rating. Asked of the model here rather than assumed from the list, because
    the list is the input to that routing and not proof that it happened.
    """
    from nrplanner import damage, model

    curves = data.get("curves", {})
    flat = {name for names in damage.AR_RATE_FOR.values() for name in names}
    for effect_id in sorted(model.MOVE_SCOPED_EFFECT_IDS):
        effect = data["effects"].get(str(effect_id))
        if effect is None:
            continue
        rates = model.compute(hero, LEVEL, [effect], curves).rates
        scoped = any(key.startswith(model.SCOPED_PREFIX) for key in rates)
        if scoped and not any(abs(rates.get(f, 1.0) - 1.0) > 1e-9
                              for f in flat):
            return effect_id
    raise LookupError("no move-scoped attack buff in this dataset")


def make_inventory(data: dict, hero: dict, *, colour: int = RED,
                   count: int = 4, handles: list[int | None] | None = None,
                   deep_count: int = 0, other_colour: int | None = None,
                   rolls: list[list[int]] | None = None
                   ) -> inventory.Inventory:
    """An inventory whose every copy is known by name, colour and handle.

    `handles` may carry `None` for a copy this save gives no handle for -- the
    case AD-013 point 4 keeps out of the candidate space and reports instead.
    `deep_count` adds Deep copies of the same colour, which is what makes the
    Deep separation checkable. `other_colour` adds one copy of a second colour,
    which is what makes the white slot's reach checkable.

    `rolls` names what each copy carries where a case needs that stated --
    two copies of one roll, say. Left out, every copy gets a different
    Strength effect, so their values differ and an order is a claim.
    """
    if handles is None:
        handles = list(range(100, 100 + count))
    if len(handles) != count:
        raise ValueError("one handle per copy, or None where there is none")

    needed = count + deep_count + 1
    rolls = rolls if rolls is not None else raising_effects(data, hero, needed)
    if len(rolls) < needed:
        rolls = rolls + [list(rolls[-1])] * (needed - len(rolls))
    templates = relic_helpers.templates_for(data, colour, count)
    owned = [relic_helpers.make_relic(template, handle, index, rolls[index])
             for index, (template, handle)
             in enumerate(zip(templates, handles))]

    for index, template in enumerate(deep_templates_for(data, colour,
                                                        deep_count)):
        owned.append(relic_helpers.make_relic(
            template, 200 + index, count + index, rolls[count + index]))

    if other_colour is not None:
        template = relic_helpers.templates_for(data, other_colour, 1)[0]
        owned.append(relic_helpers.make_relic(
            template, 300, count + deep_count, rolls[-1]))

    return inventory.Inventory(source="test", relics=owned)


def problem(colours, deep: bool = False,
            held: dict[int, types.HeldRelic | None] | None = None
            ) -> types.SlotProblem:
    """A vessel of these slot colours, with these slots held.

    `held` maps a slot index to what is in it, or to `None` for a slot held
    empty -- a slot absent from the mapping is free. The two are different
    questions and the type keeps them apart (AD-014 points 2 and 7).
    """
    slots = tuple(types.Slot(index=index, colour=colour, deep=deep)
                  for index, colour in enumerate(colours))
    entries = tuple(types.HeldSlot(index=index, relic=relic)
                    for index, relic in sorted((held or {}).items()))
    return types.SlotProblem(slots=slots, held=entries)


def held_relic(item) -> types.HeldRelic:
    """One owned copy as the held content of a slot.

    The same reading `Planner.selected_effects` and `Planner.selected_curses`
    take off a slot -- the effects this copy rolled and the curses it rolled --
    so a held slot in a test carries exactly what the window would put there.
    """
    return types.HeldRelic(
        relic_id=item.relic_id,
        name=item.name,
        effect_ids=tuple(item.effect_ids),
        curse_ids=tuple(item.curse_ids),
        handle=item.handle,
    )


def problem_from_planner(planner) -> types.SlotProblem:
    """The window's relic slots as an advisor problem, everything held.

    Every slot is held, including the empty ones: that is the state
    "the build as it stands", which is what a base state has to be for the
    advisor's figure to be comparable with the stat sheet's (checkpoint 13).
    An empty slot is held **empty** rather than left free, because a free slot
    is one the advisor may fill and there is nothing here to fill it with.

    This does the reading S10 will do in the window. It lives in the tests
    because S10 is not this task; when it is written, this is the shape it
    has to produce.
    """
    slots = []
    held: dict[int, types.HeldRelic | None] = {}
    for index, slot in enumerate(planner.active_slots()):
        slots.append(types.Slot(index=index, colour=slot.colour,
                                deep=slot.deep))
        item = slot.current_relic()
        held[index] = None if item is None else held_relic(item)
    return types.SlotProblem(
        slots=tuple(slots),
        held=tuple(types.HeldSlot(index=index, relic=relic)
                   for index, relic in sorted(held.items())),
    )


def context_from_planner(planner, data: dict) -> types.GoalContext:
    """The window's armament grid, level and declarations as a context.

    The three things beyond AD-004's four fields are here for one reason: the
    window passes them to `model.compute`, so leaving any of them out would
    make the advisor's build differ from the one on screen -- which is QA-001
    in a new place rather than a rounding difference.
    """
    from nrplanner.advisor import goals

    active = planner.active_slot()
    reference = None
    if active.weapon is not None:
        reference = types.ReferenceArmament(weapon=active.weapon,
                                            tier=active.tier,
                                            slot_index=planner.active_weapon)
    armament_effects: list[int] = []
    for slot in planner.weapon_slots:
        armament_effects.extend(slot.effect_ids)
    return types.GoalContext(
        data=data,
        hero=planner.current_hero(),
        level=planner.level_slider.value(),
        reference=reference,
        weighting=goals.DEFAULT_WEIGHTING,
        weapons_held=tuple(planner.equipped_weapons()),
        armament_effect_ids=tuple(armament_effects),
        declared=tuple(sorted(planner.declared.items())),
    )


def scaling_armament(data: dict, hero: dict, attribute: str = "Strength"
                     ) -> types.ReferenceArmament:
    """An armament this Nightfarer's `attribute` measurably moves.

    Measured rather than named: which attribute feeds which damage type comes
    out of AttackElementCorrectParam, so an armament with a large Strength
    coefficient can still be unmoved by Strength, and a case built on one
    would compare zero against zero.
    """
    from nrplanner import damage, model

    curves = data.get("curves", {})
    bare = model.compute(hero, LEVEL, [], curves)
    raised = model.compute(
        hero, LEVEL,
        [cases.effect_by_id(data, cases.effects_raising_attribute(
            data, hero, attribute, 1)[0])],
        curves)
    best = None
    for weapon in data["weapons"]:
        if not (weapon.get("scaling") or {}).get(attribute):
            continue
        gain = (damage.candidate(weapon, 1, raised, data).final_total
                - damage.candidate(weapon, 1, bare, data).final_total)
        # Largest gain wins, lowest id breaks the tie, so two runs over one
        # dataset choose the same armament.
        key = (gain, -weapon["id"])
        if best is None or key > best[0]:
            best = (key, weapon)
    if best is None or best[0][0] <= 0:
        raise LookupError(
            f"no armament in this dataset visibly scales on {attribute}")
    return types.ReferenceArmament(weapon=best[1], tier=1, slot_index=0)


def context(data: dict, hero: dict, *,
            reference: types.ReferenceArmament | None = None,
            weighting: types.Weighting | None = None,
            declared: tuple[tuple[int, int], ...] = (),
            armament_effect_ids: tuple[int, ...] = ()) -> types.GoalContext:
    """The context a run is asked in.

    `weapons_held` follows the reference armament, because a weapon-type gate
    is met by any armament on the grid and the grid in these cases holds one.
    """
    from nrplanner.advisor import goals

    held = () if reference is None else (reference.weapon,)
    return types.GoalContext(
        data=data,
        hero=hero,
        level=LEVEL,
        reference=reference,
        weighting=weighting or goals.DEFAULT_WEIGHTING,
        weapons_held=held,
        armament_effect_ids=armament_effect_ids,
        declared=declared,
    )
