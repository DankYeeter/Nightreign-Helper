"""The cases the attack-rating golden file freezes, and the harness that runs them.

Shared by the capture script (`scripts/capture_weapon_damage.py`) and by the
golden test, so that both drive the calculation through the same path. A
golden file captured through a different path than the one the test replays
would prove nothing about the code in between.

Nothing here picks an effect or an armament by a hardcoded id it made up.
Every choice is a query against the dataset -- "the effects that measurably
lower physical attack power", "the heaviest colossal sword" -- so the case
list says *why* each case is in it. The ids the query resolved to are written into
the golden file, and it is those ids the test replays: a game patch that
changes what the query would pick cannot silently change what is compared.
"""

from __future__ import annotations

from nrplanner import damage, model, weaponslots, weapons


def hero_by_name(data: dict, name: str) -> dict:
    for hero in data["heroes"]:
        if hero["name"] == name:
            return hero
    raise LookupError(f"no Nightfarer named {name!r} in this dataset")


def weapon_by_id(data: dict, weapon_id: int) -> dict:
    for weapon in data["weapons"]:
        if weapon["id"] == weapon_id:
            return weapon
    raise LookupError(f"no armament with id {weapon_id} in this dataset")


def effect_by_id(data: dict, effect_id: int) -> dict:
    effect = data["effects"].get(str(effect_id))
    if effect is None:
        raise LookupError(f"no effect with id {effect_id} in this dataset")
    return effect


PROBE_LEVEL = 15


def _alone(data: dict, hero: dict, effect: dict) -> model.Build:
    """What one effect does on its own, asked of the model itself."""
    return model.compute(hero, PROBE_LEVEL, [effect], data.get("curves", {}))


def _lowest_first(data: dict) -> list[dict]:
    return [data["effects"][k] for k in
            sorted(data["effects"], key=lambda k: int(data["effects"][k]["id"]))]


def _pick(data: dict, moves, count: int, what: str) -> list[int]:
    """The lowest-numbered effects that pass `moves`, or a loud failure.

    Chosen by asking `model.compute` what the effect actually does, not by
    reading its modifier names. Most effects carrying an attack rate are
    gated -- on a weapon switch, on grease, on three bows -- or scoped to
    skills rather than to the swing, and they move an attack rating by
    nothing at all. A case built on one would look like a case about a buff
    and be a case about a bare armament. Lowest-numbered so two runs against
    the same dataset choose the same effects.
    """
    out: list[int] = []
    for effect in _lowest_first(data):
        if moves(effect):
            out.append(int(effect["id"]))
            if len(out) == count:
                return out
    raise LookupError(
        f"this dataset has {len(out)} effects that {what}, "
        f"fewer than the {count} this case needs")


def effects_raising_rate(data: dict, hero: dict, field_name: str,
                         count: int = 1) -> list[int]:
    """Effects that measurably move this multiplier for this Nightfarer."""
    def moves(effect: dict) -> bool:
        if field_name not in (effect.get("modifiers") or {}):
            return False
        rates = _alone(data, hero, effect).rates
        return abs(rates.get(field_name, 1.0) - 1.0) > 1e-9

    return _pick(data, moves, count, f"move {field_name}")


def effects_raising_attribute(data: dict, hero: dict, attribute: str,
                              count: int = 1) -> list[int]:
    """Effects that measurably raise this attribute for this Nightfarer."""
    def moves(effect: dict) -> bool:
        build = _alone(data, hero, effect)
        return (build.attributes.get(attribute, 0)
                > build.base_attributes.get(attribute, 0))

    return _pick(data, moves, count, f"raise {attribute}")


def scoped_effect(data: dict, hero: dict, class_name: str) -> int:
    """An attack buff that reaches only one class of armament."""
    def moves(effect: dict) -> bool:
        bucket = _alone(data, hero, effect).class_rates.get(class_name, {})
        return any(abs(v - 1.0) > 1e-9 for v in bucket.values())

    return _pick(data, moves, 1, f"buff {class_name} armaments only")[0]


def heaviest_of_family(data: dict, family: str) -> int:
    """The armament of this family with the steepest Strength requirement.

    Kept for the two cases that want a heavy-looking, deterministic pick of
    this family rather than the first one alphabetically. The name is now
    aspirational rather than load-bearing: QA-061 measured that the
    requirement this sorts on is zero for every Colossal Sword in the
    dataset, so on a tie the id -- the second key -- decides (T-034).
    """
    candidates = [w for w in data["weapons"] if w.get("family") == family]
    if not candidates:
        raise LookupError(f"no armament of family {family!r} in this dataset")
    return max(candidates,
               key=lambda w: (w["requires"].get("Strength", 0), w["id"]))["id"]


def first_of_family(data: dict, family: str) -> int:
    candidates = sorted((w["id"] for w in data["weapons"]
                         if w.get("family") == family))
    if not candidates:
        raise LookupError(f"no armament of family {family!r} in this dataset")
    return candidates[0]


def _case(name: str, hero: str, level: int, active: int,
          armaments: list[dict], relic_effects: list[int] | None = None,
          curse_effects: list[int] | None = None,
          declared: dict[int, int] | None = None) -> dict:
    return {
        "name": name,
        "hero": hero,
        "level": level,
        "active": active,
        # One entry per filled tile: {"slot", "weapon", "tier", "effects"}.
        "armaments": armaments,
        "relic_effects": list(relic_effects or []),
        "curse_effects": list(curse_effects or []),
        "declared": {str(k): v for k, v in (declared or {}).items()},
    }


def cases(data: dict) -> list[dict]:
    """Every combination the golden file covers, and why it is covered."""
    # Wylder is the build QA measured the divergence on; Ironeye is the one
    # who fights at range; Recluse carries the magic scaling; Executor is one
    # of the two DLC Nightfarers the allow flags cannot speak about (QA-006).
    wylder = hero_by_name(data, "Wylder")
    ironeye = hero_by_name(data, "Ironeye")
    recluse = hero_by_name(data, "Recluse")
    executor = hero_by_name(data, "Executor")

    wylder_start = wylder["starting_weapon"]
    recluse_start = recluse["starting_weapon"]
    executor_start = executor["starting_weapon"]

    # The x0.85 the game charges for a status on the starting armament. Three
    # effects carry the STARTING_AR_RATE_FOR **fields**, and they are all of
    # them (frost, poison, blood loss) -- which is not the same as saying
    # they are all the "starting armament" relics there are: four more of
    # those convert a damage type instead, through fields nothing here reads
    # (QA-113, QA-114). See `damage.STARTING_AR_RATE_FOR` for the counts and
    # for what could and could not be reproduced from the dataset.
    starting_penalty = effects_raising_rate(
        data, wylder, "physicsAttackPowerRate", 3)
    # The ordinary attack buff, carried by 200-odd effects.
    attack_rate = effects_raising_rate(data, wylder, "physicsAttackRate", 2)
    magic_rate = effects_raising_rate(data, recluse, "magicAttackRate", 1)
    strength = effects_raising_attribute(data, wylder, "Strength", 2)
    dexterity = effects_raising_attribute(data, wylder, "Dexterity", 1)
    intelligence = effects_raising_attribute(data, recluse, "Intelligence", 1)
    regain = effects_raising_rate(data, wylder, "regainRate", 1)
    melee_only = scoped_effect(data, wylder, "melee")
    ranged_only = scoped_effect(data, ironeye, "ranged")

    bow = first_of_family(data, "Bow")
    staff = first_of_family(data, "Glintstone Staff")
    colossal = heaviest_of_family(data, "Colossal Sword")

    declarable = declarable_attack_buff(data, wylder)

    out = [
        _case("bare starting armament, level 1",
              "Wylder", 1, 0,
              [{"slot": 0, "weapon": wylder_start, "tier": 1, "effects": []}]),
        _case("bare starting armament, level 15, legendary",
              "Wylder", 15, 0,
              [{"slot": 0, "weapon": wylder_start, "tier": 4, "effects": []}]),
        # The starting-armament penalty needs both halves: slot 1 AND this
        # Nightfarer's own weapon. Verified in play 2026-08-22, and these two
        # cases are what keeps that pair together.
        _case("starting armament with the frost penalty, in slot 1",
              "Wylder", 15, 0,
              [{"slot": 0, "weapon": wylder_start, "tier": 3, "effects": []}],
              relic_effects=[starting_penalty[0]]),
        _case("same penalty, same weapon, moved to slot 2",
              "Wylder", 15, 1,
              [{"slot": 1, "weapon": wylder_start, "tier": 3, "effects": []}],
              relic_effects=[starting_penalty[0]]),
        _case("all three status penalties at once, slot 1",
              "Wylder", 15, 0,
              [{"slot": 0, "weapon": wylder_start, "tier": 3, "effects": []}],
              relic_effects=list(starting_penalty)),
        _case("physical attack buff on a foreign armament",
              "Wylder", 15, 0,
              [{"slot": 0, "weapon": colossal, "tier": 2, "effects": []}],
              relic_effects=list(attack_rate)),
        # Renamed 2026-09-03 (T-034, QA-019): this used to be named for an
        # "unmet requirements" branch that never existed on real data --
        # QA-061 measured every armament's requirement at zero or trivially
        # met, and the user confirmed in play that Nightreign has none at
        # all. What the case actually covers, and still needs to: a bare
        # armament with two damage types and no relic effects, the baseline
        # the next case's scaling growth is measured against.
        _case("a two-type armament with no relic effects",
              "Wylder", 1, 0,
              [{"slot": 0, "weapon": colossal, "tier": 1, "effects": []}]),
        _case("attribute gains feeding the scaling",
              "Wylder", 8, 0,
              [{"slot": 0, "weapon": colossal, "tier": 3, "effects": []}],
              relic_effects=strength + dexterity),
        # A melee-scoped buff on a bow must not move it, and a ranged-scoped
        # buff must. Both directions, one armament each. The ranged case is
        # also the only one in this file whose relic contributes a
        # class-scoped source line to the click-through breakdown (rendered
        # as "... -- ranged armaments only"); it is the sole case exercising
        # that half of `_ar_breakdown_text`, so removing it would silently
        # stop covering it (QA-081).
        _case("melee-only buff with a bow in hand",
              "Ironeye", 15, 0,
              [{"slot": 0, "weapon": bow, "tier": 3, "effects": []}],
              relic_effects=[melee_only]),
        _case("ranged-only buff with a bow in hand",
              "Ironeye", 15, 0,
              [{"slot": 0, "weapon": bow, "tier": 3, "effects": []}],
              relic_effects=[ranged_only]),
        # A staff's own hit is physical, so a magic buff does not lift it and
        # Intelligence does. Both halves of that in one case.
        _case("catalyst: magic buff idle, Intelligence at work",
              "Recluse", 15, 0,
              [{"slot": 0, "weapon": staff, "tier": 3, "effects": []}],
              relic_effects=magic_rate + intelligence),
        _case("Recluse on her own starting armament",
              "Recluse", 15, 0,
              [{"slot": 0, "weapon": recluse_start, "tier": 2, "effects": []}],
              relic_effects=[starting_penalty[1]]),
        # A DLC Nightfarer: the allow flags cannot name Executor, so every
        # effect here has to count (QA-006, decided "works").
        _case("Executor, allow-flagged effects and a curse",
              "Executor", 15, 0,
              [{"slot": 0, "weapon": executor_start, "tier": 3,
                "effects": []}],
              relic_effects=list(attack_rate) + strength,
              curse_effects=curses_lowering_an_attribute(data, executor)),
        # An armament's own rolled effects count towards the sheet just as a
        # relic's do, including from a tile that is not the active one.
        _case("armament effects count too",
              "Wylder", 15, 0,
              [{"slot": 0, "weapon": wylder_start, "tier": 3,
                "effects": [attack_rate[0]]},
               {"slot": 1, "weapon": bow, "tier": 2,
                "effects": [ranged_only]}],
              relic_effects=[]),
        # Rally recovery is read off the armament and scaled by regainRate.
        _case("rally recovery with the relic that scales it",
              "Wylder", 15, 0,
              [{"slot": 0, "weapon": wylder_start, "tier": 3, "effects": []}],
              relic_effects=[regain[0]]),
        _case("rally recovery on an armament that reclaims nothing",
              "Wylder", 15, 0,
              [{"slot": 0, "weapon": bow, "tier": 3, "effects": []}],
              relic_effects=[regain[0]]),
        # A declared conditional effect counts exactly as that many copies.
        _case("a conditional effect the player declares",
              "Wylder", 15, 0,
              [{"slot": 0, "weapon": wylder_start, "tier": 3, "effects": []}],
              relic_effects=[declarable],
              declared={declarable: 2}),
        _case("empty tile",
              "Wylder", 15, 2, []),
    ]
    return out


def curses_lowering_an_attribute(data: dict, hero: dict,
                                 count: int = 1) -> list[int]:
    """Curses that really take an attribute away.

    Only Deep of Night relics carry curses, and a curse that moves no number
    would make the case indistinguishable from the same build without it.
    """
    def moves(effect: dict) -> bool:
        if not effect.get("is_curse"):
            return False
        build = _alone(data, hero, effect)
        return any(build.attributes.get(name, 0) < value
                   for name, value in build.base_attributes.items())

    return _pick(data, moves, count, "lower an attribute")


def declarable_attack_buff(data: dict, hero: dict) -> int:
    """A gated attack buff that counts once the player declares its condition.

    Gated effects are left out of every total until declared -- that is the
    whole point of the declaration -- so the case has to prove both halves:
    nothing while silent, a multiplier once declared.
    """
    curves = data.get("curves", {})

    def moves(effect: dict) -> bool:
        if not model.is_conditional(effect, None):
            return False
        if abs(_alone(data, hero, effect).rates
               .get("physicsAttackRate", 1.0) - 1.0) > 1e-9:
            return False        # not gated in practice; a plain buff
        declared = model.compute(hero, PROBE_LEVEL, [effect], curves,
                                 declared={int(effect["id"]): 1})
        return abs(declared.rates.get("physicsAttackRate", 1.0) - 1.0) > 1e-9

    return _pick(data, moves, 1, "buff attack once declared")[0]


#: How the arsenal tab's own list is read, on either side of AD-019 step W4.
#: Written out for both shapes rather than reached for with `getattr`: a
#: silent fallback would answer "nothing moved" for a tab that never moved
#: onto the facade, which is the one answer a differential run must not give
#: by accident. The class name goes into the record beside the figure, so a
#: comparison shows the move rather than assuming it.
def arsenal_figure(rating) -> float:
    """The layer-two figure behind an arsenal tile, unrounded.

    **Not always the number the tile prints.** Since T-046 a staff or a seal
    is headed by the spell scaling the game shows for it (QA-099), and this
    still reads `final_total`, the attack rating underneath. That is the
    split the capture is built on rather than an oversight: this field
    answers "did the arithmetic move", `arsenal_tiles` beside it answers
    "did the text move", and keeping them apart is what QA-074 asks for. A
    change of *which* figure a tile shows is a change of text, and it shows
    up there -- for the 30 catalysts of the dataset, it did.
    """
    if isinstance(rating, weapons.WeaponRating):
        # The tab before W4: `weapons.rank`. Read off `scaled_per_type()`
        # rather than the `total` field this branch used to read -- `total`
        # fell in W5 (AD-019), and the two were the same addends bracketed
        # differently, so the figure this branch reports is unchanged.
        return sum(rating.scaled_per_type().values())
    if isinstance(rating, damage.Rating):
        return rating.final_total    # the tab on the facade: layer two
    raise TypeError(
        f"the arsenal tab is holding {type(rating).__name__} objects, which "
        f"this reader has never seen. Nothing captured -- a figure guessed "
        f"off an unknown shape is worse than no figure.")


def arsenal_tile_texts(tab, name: str) -> list[list[str]]:
    """Every label of every tile the tab drew for this armament's name.

    The whole tile, not only its AR row: the rarity band, the "Upgraded to"
    line and the scaling rows are read off the same rating and move with it.
    Names are not unique in the dataset, so this hands back one list per tile
    carrying the name and the comparison sees how many there were.
    """
    from PySide6.QtWidgets import QLabel

    from nrplanner import arsenaltab

    out = []
    for tile in tab.scroll.widget().findChildren(arsenaltab.Tile):
        texts = [label.text() for label in tile.findChildren(QLabel)]
        # The icon badge carries no text and the name follows it.
        if len(texts) >= 2 and texts[1] == name:
            out.append(texts)
    return out


def arsenal_reading(planner, data: dict, build, request: dict) -> dict:
    """Drive the real arsenal tab for one armament and read it back.

    The tab is the one the Planner built, and every control the reading
    depends on is set from the request: the target tier and the rarity
    filter. The search box is set to the armament's own name because the tab
    builds its sections lazily and opens them itself only for a modest
    result set -- without a search nothing is drawn at all.

    The requirements checkbox this used to also set is gone (T-034): QA-061
    measured it could never filter anything on real data, and the user
    confirmed Nightreign has no attribute requirement for armaments at all.

    **`planner._build` is set here, not by `Planner.recompute()`.** The tab
    asks `current_build()`, and in the running program `recompute()` is what
    stores that; here it is set directly for the same reason `last_sources`
    is set in `run` below -- so the reading depends on the case and on
    nothing the planner happened to be holding. That means no case in this
    file exercises the assignment inside `recompute()`; the three cases in
    `tests/test_one_build.py` that call `recompute()` for real and then check
    `weapons_tab.attributes` are what cover that half.
    """
    tab = planner.weapons_tab
    weapon = weapon_by_id(data, int(request["weapon"]))

    planner._build = build
    tab.upgrade.setValue(int(request["tier"]))
    wanted_rarity = int(request["rarity"])
    index = tab.rarity_box.findData(wanted_rarity)
    if index < 0:
        raise LookupError(
            f"the rarity filter has no entry for {wanted_rarity}; -1 is "
            f"'All' and 0..3 are the bands")
    tab.rarity_box.setCurrentIndex(index)
    tab.search.setText(f'"{weapon["name"]}"')
    tab.recalculate()

    listed = [r for r in tab.ratings if r.weapon["id"] == weapon["id"]]
    return {
        # What kind of object the tab's own list holds. The signal that the
        # tab moved onto the facade at all, rather than a figure that would
        # look the same either way.
        "arsenal_kind": (type(listed[0]).__name__ if listed else None),
        # The tier the tab really ranked at, read off the control.
        "arsenal_tier": tab.upgrade.value(),
        # Exact bits, so a one-ULP change cannot hide behind rounding. The
        # rendered text sits in `arsenal_tiles` beside it, on purpose: the
        # two answer different questions (QA-074).
        "arsenal_figure": (arsenal_figure(listed[0]).hex() if listed
                           else None),
        # How many rows the list holds for this armament. Zero means the
        # rarity filter dropped it, which is a finding and not an absence.
        "arsenal_listed": len(listed),
        "arsenal_tiles": arsenal_tile_texts(tab, weapon["name"]),
        "arsenal_summary": tab.summary.text(),
    }


def build_for(data: dict, case: dict) -> model.Build:
    """The build this case describes.

    Assembled exactly as `Planner.recompute` assembles it -- relics, armament
    effects and curses in one list, the weapon gates from the tiles, the
    declared counts as given. Written out here rather than borrowed from the
    Planner so the golden file survives the refactoring of the Planner, which
    is the very thing it exists to police.
    """
    hero = hero_by_name(data, case["hero"])
    slots = armament_slots(data, case)
    relic_effects = [effect_by_id(data, e) for e in case["relic_effects"]]
    weapon_effects = [effect_by_id(data, e)
                      for slot in slots for e in slot.effect_ids]
    curses = [effect_by_id(data, e) for e in case["curse_effects"]]
    active = slots[case["active"]]
    return model.compute(
        hero, case["level"],
        relic_effects + weapon_effects + curses,
        data.get("curves", {}),
        weapon=active.weapon,
        weapons_held=[s.weapon for s in slots if s.filled],
        declared={int(k): v for k, v in case["declared"].items()},
    )


def armament_slots(data: dict, case: dict) -> list[weaponslots.WeaponSlot]:
    """The six tiles this case puts on the grid."""
    slots = [weaponslots.WeaponSlot()
             for _ in range(weaponslots.SLOT_COUNT)]
    for entry in case["armaments"]:
        slots[entry["slot"]] = weaponslots.WeaponSlot(
            weapon=weapon_by_id(data, entry["weapon"]),
            tier=entry["tier"],
            effect_ids=list(entry["effects"]),
        )
    return slots


def run(planner, data: dict, case: dict) -> dict:
    """Drive the real weapon-damage displays for one case and read them back.

    The Planner is the real one, headless. Only the pieces the case describes
    are set on it; `selected_effects` is replaced because the relics behind it
    live in combo boxes the case has no business filling.

    All three displays, not one. Until W3b this read the panel and the figures
    behind it and nothing else, which left two ways for a wrong number to
    reach the player unremarked (QA-073): the five tiles that are not the
    active one, and the text of the click-through breakdown. Both are here
    now, so they hang on the same frozen state the panel does.

    **`last_sources`/`last_rates` below are set by this function, not by
    `Planner.recompute()`.** In the running program those two lines are
    `recompute()`'s own doing, right before it calls the same
    `_refresh_weapon_damage`; here they are set directly so the captured text
    depends on the case and nothing else, as the comment below explains. That
    means no case in this file exercises the assignment inside `recompute()`
    itself -- a green suite here says nothing about whether `recompute()`
    still wires it up (QA-076). `tests/test_breakdown_sources_wiring.py`
    covers that half separately, against `recompute()` directly.

    **A fifth reading, and only where a case asks for it.** A case carrying
    an `arsenal` block also gets the arsenal tab driven and read back. The
    golden cases carry none, so what they freeze is unchanged by its being
    here; the block is written by `scripts/differential/plan.py` out of a
    raster, for the differential run of AD-019 step W4. The tab is a fourth
    display of the same calculation and it ranks at a tier of its own
    choosing (AD-020, point 1), which is exactly why it needs measuring
    separately rather than folding into the panel's cases.
    """
    hero = hero_by_name(data, case["hero"])
    planner.hero_index = data["heroes"].index(hero)
    planner.weapon_slots = armament_slots(data, case)
    planner.active_weapon = case["active"]
    planner.declared = {int(k): v for k, v in case["declared"].items()}
    relic_effects = [effect_by_id(data, e) for e in case["relic_effects"]]
    planner.selected_effects = lambda: relic_effects

    build = build_for(data, case)
    # What `Planner.recompute` hands the breakdown before it draws. Set from
    # this case rather than left to whatever the planner last held, so the
    # captured text depends on the case and on nothing else -- otherwise the
    # source lines would follow the order the cases happened to run in.
    planner.last_sources = dict(build.sources)
    planner.last_rates = dict(build.rates)
    planner._refresh_weapon_damage(build)
    shown = {
        # The figures the panel keeps for the click-through breakdown: the
        # calculation's own output, before it is turned into text.
        "last_ar": rounded(planner.last_ar),
        # And the text itself, which catches a change in what is shown even
        # when every number behind it stayed the same.
        "panel": planner.ar_label.text(),
        # Every tile, including the five that are not ringed. The active one
        # was already held between the golden total and checkpoint 19; the
        # other five were held by nothing at all.
        "tiles": [{"title": tile.title.text(), "detail": tile.detail.text()}
                  for tile in planner.weapon_tiles],
        # What a click on the total actually puts on screen. `last_ar` above
        # is this display's input; without its output a swap of two of those
        # figures changes what the player reads and nothing notices.
        "breakdown": planner._ar_breakdown_text(),
    }
    # Only when the case asks. A case without an `arsenal` block gets exactly
    # the four keys above, which is what keeps the golden file -- whose cases
    # all predate W4 and ask for none -- unchanged by this addition.
    if case.get("arsenal"):
        shown.update(arsenal_reading(planner, data, build, case["arsenal"]))
    return shown


def rounded(value):
    """Six decimals: enough to catch a changed calculation, loose enough that
    the last bit of a float cannot fail the test on its own."""
    if isinstance(value, dict):
        return {k: rounded(v) for k, v in value.items()}
    if isinstance(value, float):
        return round(value, 6)
    return value
