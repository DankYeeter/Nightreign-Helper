"""A3 over the whole dataset: every Nightfarer, every chalice layout.

The acceptance criterion reads:

    A3 -- The build advisor delivers, for every Nightfarer and every known
    chalice layout, at least two named directions (maximise damage, minimise
    damage taken) and suggests one concrete relic out of the player's holdings
    per slot.

Until this file existed, the suite said nothing about the two words that do
the work in that sentence. `test_advisor_goals.py` checks that the registry
holds two entries and their labels -- with no dataset, no Nightfarer and no
chalice anywhere near it -- and every other advisor test runs through a local
`wylder` fixture, so **one** of the ten heroes answered for all of them and
six of them appeared in no advisor test at all (QA-191, QA-205). A run at the
built artefact closed that once by hand (T-114: 440 runs, 10/10 Nightfarers,
74/74 chalices); this file closes it at every commit.

**No number in here is written down.** How many Nightfarers there are, which
chalices each of them may open, how many slots a layout has and how many
copies of one colour a layout can want are all read out of the dataset. A
figure typed in here would go false-green or false-red at the next game patch,
which is the one thing a completeness guard must not do.

**The pool is made, not read, and it is small on purpose.** Every run gets an
inventory of a few made copies per colour instead of the player's own
hundreds. That is the case cut smaller, never the promise: all 110
Nightfarer/chalice pairs are still asked, both directions and both layouts of
each chalice, which is 440 answers. Measured on this machine (Windows 10,
snapshot of extract version 11, `python - <<script` outside pytest): the same
sweep against a made pool takes 33 s, of which 25 s is the Deep of Night half
with its six free slots. Against the player's real 309 relics T-114 measured
3,5 s for a **single** run, so the honest reading of "every layout" is only
affordable with a made pool. What the pool must still do is leave a choice --
each copy carries a different effect that measurably raises an attribute, so
a suggestion is a decision and not the only thing that fitted.

**What this file covers.** That an answer comes back at all, that it names two
different directions, that every free slot of the layout is filled, and that
every copy named is one the player holds, of a colour and a depth the slot
accepts. It does **not** check that the suggestion is the best one -- that is
`test_advisor_search.py`'s and `test_advisor_evaluate.py`'s subject -- nor
what the reasons say, which is `test_advisor_explain.py`'s.

**Where the question comes from.** The sweep builds its own `SlotProblem` out
of the chalice record, because building one through a `Planner` window per
pair would cost a window per Nightfarer. T-114 warned that
`tests/advisor_cases.py` holds a second translation from window to advisor
question and that two translations drift, so the last case here pins the one
used above to `advisorbar.asking_from` -- the translation the window itself
performs -- for the chalice a real window is standing on.
"""

from __future__ import annotations

import pytest

from nrplanner import inventory, model
from nrplanner.advisor import goals, run, types

from tests import advisor_cases as advisor
from tests import relics as relic_helpers


def shared_hero_type(data: dict) -> int:
    """The `hero_type` of the chalices that belong to no single Nightfarer.

    The Grails are open to everyone, and the window puts them under every
    Nightfarer (`app.Planner._fill_chalices`). Which number stands for "shared"
    is asked of the data -- it is the one `hero_type` on a chalice that no hero
    id claims -- rather than imported from the window, so this file cannot
    inherit a wrong answer from the code it is asking about, and a renumbering
    in a patch moves it by itself.
    """
    hero_ids = {hero["id"] for hero in data["heroes"]}
    shared = {vessel["hero_type"] for vessel in data["vessels"]
              if vessel["hero_type"] not in hero_ids}
    if len(shared) != 1:
        pytest.fail(f"expected exactly one shared chalice type, found {shared}")
    return shared.pop()


def pairs(data: dict) -> list[tuple[dict, dict]]:
    """(Nightfarer, chalice) for every chalice that Nightfarer may open.

    Their own seven and the four Grails, which is the list the window offers.
    """
    shared_type = shared_hero_type(data)
    out = []
    for hero in data["heroes"]:
        for vessel in data["vessels"]:
            if vessel["hero_type"] in (hero["id"], shared_type):
                out.append((hero, vessel))
    return out


def colours_relics_come_in(data: dict) -> list[int]:
    """Every colour an owned relic can carry, lowest first.

    Not `model.COLOUR_NAMES`: white is a slot colour and not a relic colour,
    and asking the relics themselves is the only way to say that without
    restating the rule the advisor is being asked about.
    """
    return sorted({relic["colour"] for relic in data["relics"]})


def copies_per_colour(data: dict) -> int:
    """Enough copies of one colour to fill the widest layout with that colour.

    A layout of three white slots wants three copies of some one colour, so
    the count that always suffices is the number of slots a layout has -- read
    off the chalices rather than written down as three.
    """
    return max(max(len(vessel["slots"]), len(vessel["deep_slots"]))
               for vessel in data["vessels"])


def made_inventory(data: dict, hero: dict):
    """A few copies of every colour, ordinary and Deep, each worth something.

    One distinct attribute-raising effect per copy, so no two candidates are
    interchangeable and a suggestion is a decision. The effects are found by
    measurement in `advisor_cases.raising_effects`, never by name.
    """
    colours = colours_relics_come_in(data)
    per_colour = copies_per_colour(data)
    rolls = advisor.raising_effects(data, hero, len(colours) * per_colour * 2)
    owned = []
    for colour in colours:
        templates = (relic_helpers.templates_for(data, colour, per_colour)
                     + advisor.deep_templates_for(data, colour, per_colour))
        for template in templates:
            index = len(owned)
            owned.append(relic_helpers.make_relic(template, 100 + index, index,
                                                  rolls[index]))
    return inventory.Inventory(source="test", relics=owned)


def layout_of(vessel: dict, deep: bool) -> types.SlotProblem:
    """The chalice as a question with every slot free.

    The three ordinary slots, and in Deep of Night the three Deep ones after
    them -- the order and the per-slot `deep` flag the window builds in
    `Planner.active_slots`, checked against it in the last case of this file.
    """
    wanted = [(colour, False) for colour in vessel["slots"]]
    if deep:
        wanted += [(colour, True) for colour in vessel["deep_slots"]]
    return types.SlotProblem(
        slots=tuple(types.Slot(index=index, colour=colour, deep=is_deep)
                    for index, (colour, is_deep) in enumerate(wanted)),
        held=())


@pytest.fixture(scope="module")
def equipment(game_data):
    """Per Nightfarer, the inventory and the context every run of them uses.

    Built once for the module: the reference armament is found by measuring
    every armament in the dataset, and paying that per chalice would be ten
    times the work for the same answer.
    """
    return {
        hero["id"]: (
            made_inventory(game_data, hero),
            advisor.context(game_data, hero,
                            reference=advisor.scaling_armament(game_data,
                                                               hero)),
        )
        for hero in game_data["heroes"]
    }


def _faults(data: dict, equipment, hero: dict, vessel: dict,
            deep: bool) -> list[str]:
    """Everything A3 promises about one chalice, and what it failed to keep."""
    owned, ctx = equipment[hero["id"]]
    by_handle = {copy.handle: copy for copy in owned.relics}
    problem = layout_of(vessel, deep)
    frozen = run.frozen_inventory(owned, problem)
    where = (f"{hero['name']} / {vessel['name']}"
             f"{' / Deep of Night' if deep else ''}")

    faults: list[str] = []
    labels: list[str] = []
    for goal_id in sorted(goals.GOALS):
        request = advisor.request_for(problem, ctx, frozen, goal_id)
        result = run.run(request, frozen, ctx, goals.GOALS)

        if not result.goal_label.strip():
            faults.append(f"{where}: direction {goal_id} came back unnamed")
        else:
            labels.append(result.goal_label)
        if not result.suggestions:
            faults.append(f"{where}: {goal_id} suggested nothing at all")
            continue

        best = result.suggestions[0]
        filled = {choice.slot_index for choice in best.choices}
        free = {slot.index for slot in problem.slots}
        if filled != free:
            faults.append(f"{where}: {goal_id} left slots {sorted(free - filled)} "
                          f"empty and answered for {sorted(filled)}")
        for choice in best.choices:
            copy = by_handle.get(choice.handle)
            if copy is None:
                faults.append(f"{where}: {goal_id} suggested handle "
                              f"{choice.handle}, which the player does not own")
                continue
            if not choice.name.strip():
                faults.append(f"{where}: {goal_id} suggested a copy with no "
                              f"name in slot {choice.slot_index}")
            slot = problem.slots[choice.slot_index]
            if copy.is_deep != slot.deep:
                faults.append(f"{where}: {goal_id} put a "
                              f"{'Deep' if copy.is_deep else 'an ordinary'} "
                              f"relic in slot {slot.index}, which is not")
            if slot.colour != model.WHITE_SLOT and copy.colour != slot.colour:
                faults.append(f"{where}: {goal_id} put colour {copy.colour} "
                              f"in slot {slot.index}, which takes "
                              f"{slot.colour}")

    if len(set(labels)) < 2:
        faults.append(f"{where}: {len(set(labels))} named direction(s), and "
                      f"A3 promises at least two")
    return faults


def _sweep(game_data, equipment, deep: bool) -> None:
    """Ask every Nightfarer about every chalice they may open, and report all."""
    asked = pairs(game_data)
    faults: list[str] = []
    for hero, vessel in asked:
        faults.extend(_faults(game_data, equipment, hero, vessel, deep))

    # The denominator, said out loud: a sweep that quietly asked about two
    # pairs would pass exactly as loudly as one that asked about all of them.
    heroes = {hero["id"] for hero, _ in asked}
    vessels = {vessel["id"] for _, vessel in asked}
    assert heroes == {hero["id"] for hero in game_data["heroes"]}
    assert vessels == {vessel["id"] for vessel in game_data["vessels"]}
    assert not faults, (
        f"{len(faults)} of A3's promises were broken over {len(asked)} "
        f"Nightfarer/chalice pairs ({len(heroes)} Nightfarers, "
        f"{len(vessels)} chalices, {len(asked) * len(goals.GOALS)} runs):\n"
        + "\n".join(faults[:40]))


def test_every_nightfarer_and_chalice_is_answered_in_full(game_data,
                                                          equipment):
    """A3 for the three ordinary slots, over all of them."""
    _sweep(game_data, equipment, deep=False)


def test_every_nightfarer_and_chalice_is_answered_in_full_in_deep_of_night(
        game_data, equipment):
    """A3 for the six slots Deep of Night opens, over all of them.

    Kept apart from the case above rather than folded into it: the six-slot
    layout is a different question -- three of its slots draw only from Deep
    copies -- and it costs three times as much, which two cases can spread
    over two workers and one cannot.
    """
    _sweep(game_data, equipment, deep=True)


def test_the_layout_this_file_builds_is_the_one_the_window_asks_about(
        shared_planner, game_data):
    """`layout_of` says what `advisorbar.asking_from` says (T-114).

    The sweep above builds its own question out of the chalice record, and
    `tests/advisor_cases.py` holds a second translation from window to advisor
    question that predates `asking_from`. Two translations of one thing drift,
    and a sweep asking a question the window never asks would prove nothing
    about the program. So the chalice a real window is standing on is asked
    both ways, with Deep of Night off and on, and the two must agree.
    """
    from PySide6.QtCore import Qt

    from nrplanner import advisorbar

    if shared_planner.owned is None:
        pytest.skip("this machine has no save, so the window asks nothing")
    row = shared_planner.chalice_list.currentRow()
    vessel = shared_planner.chalice_list.item(row).data(Qt.UserRole)
    if vessel is None:
        pytest.skip("no chalice is selected in this window")

    was_deep = shared_planner.deep_check.isChecked()
    try:
        for deep in (False, True):
            shared_planner.deep_check.setChecked(deep)
            asking = advisorbar.asking_from(shared_planner,
                                            sorted(goals.GOALS)[0])
            assert asking is not None
            assert asking.request.problem.slots == layout_of(vessel,
                                                             deep).slots
    finally:
        shared_planner.deep_check.setChecked(was_deep)
