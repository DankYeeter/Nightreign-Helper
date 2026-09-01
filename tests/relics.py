"""Building an inventory a test can describe exactly.

The relics here are made in the test rather than read from the save, so the
awkward cases can be stated instead of hoped for: a relic owned once, two
copies of one roll, a copy whose handle could not be read, and a stored build
naming a relic that is no longer owned. The save itself is only ever read, and
never by these helpers.

Shared by the ownership tests (a relic may be worn once) and the restore tests
(a build comes back the way it was left), because both need the same three
things: a vessel whose slots repeat a colour, relics of that colour, and a way
to put one in a slot the way the picker does.
"""

from __future__ import annotations

from typing import NamedTuple

import pytest

from nrplanner import inventory


class VesselPair(NamedTuple):
    """Two chalices a relic of one colour can move between.

    `colour` sits at `here` in the vessel on `row`, and at `there` in the
    vessel on `other_row` -- two different positions, which is the condition
    under which a build switched between them used to be destroyed (QA-014).
    Both vessels take that colour at `there`, so a relic left in the outgoing
    vessel's slot is one the incoming vessel could legitimately keep: that is
    what makes it visible when it is wrongly kept.
    """
    row: int
    here: int
    other_row: int
    there: int
    colour: int

# Not a real save offset, only distinct per record, which is all it has to be.
FIRST_OFFSET = 0x1000
OFFSET_STRIDE = 0x50


def make_relic(template: dict, handle: int | None, index: int,
               effects: list[int]) -> inventory.OwnedItem:
    """One owned copy of a relic template."""
    return inventory.OwnedItem(
        relic_id=template["id"],
        name=template["name"].strip(),
        colour=template["colour"],
        effect_ids=list(effects),
        is_deep=bool(template.get("is_deep")),
        handle=handle,
        offset=FIRST_OFFSET + index * OFFSET_STRIDE,
    )


def templates_for(data: dict, colour: int, count: int) -> list[dict]:
    """Ordinary (not Deep) relic templates of one colour, lowest ids first."""
    found = sorted(
        (r for r in data["relics"]
         if r["colour"] == colour and not r.get("is_deep")),
        key=lambda r: r["id"],
    )
    if len(found) < count:
        pytest.skip(f"this dataset has fewer than {count} relics of colour "
                    f"{colour}")
    return found[:count]


def some_effect_ids(data: dict, count: int) -> list[int]:
    return [int(k) for k in sorted(data["effects"], key=int)[:count]]


def vessel_at(planner, row: int):
    """The vessel one row of the chalice list stands for."""
    from PySide6.QtCore import Qt

    return planner.chalice_list.item(row).data(Qt.UserRole)


def select_vessel(planner, row: int) -> None:
    """Click a chalice in the list, which is what applies it."""
    planner.chalice_list.setCurrentRow(row)


def offered(slot) -> list:
    """The relics this slot's list holds, without the empty entry."""
    return [slot.relic_box.itemData(i) for i in range(slot.relic_box.count())
            if slot.relic_box.itemData(i) is not None]


def equip(slot, item) -> None:
    """Put a relic in a slot the way choosing it in the picker does.

    Through the combo box rather than by assignment, so the slot emits and
    the window reacts -- the reaction is what several of these tests are
    about.
    """
    index = slot.relic_box.findData(item)
    assert index >= 0, f"{item.name} is not on offer in slot {slot.index + 1}"
    slot.relic_box.setCurrentIndex(index)
