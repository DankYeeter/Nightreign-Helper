"""Read the player's actually owned relics for filtering the planner."""

from __future__ import annotations

import pathlib
import struct
from dataclasses import dataclass, field

from Crypto.Cipher import AES

from nrdata import savefile


# Relic id for a hypothetical relic the player does not own, used by the
# planner's custom-relic tile. Negative so it can never collide with a real
# EquipParamAntique row id.
CUSTOM_RELIC_ID = -1


@dataclass
class OwnedItem:
    """One relic the player actually holds, with the effects it rolled."""
    relic_id: int
    name: str
    colour: int
    effect_ids: list[int]
    is_deep: bool
    has_curse: bool = False
    icon: int | None = None
    caption: str = ""
    # The curses this copy actually rolled, read from the save. Distinct from
    # has_curse, which only says the template carries curse slots at all.
    curse_ids: list[int] = field(default_factory=list)
    # This copy's handle in the save. The equipped-loadout table refers to
    # relics by handle, and several copies of one relic id can be owned with
    # different rolls, so the handle is what makes "the relic in that slot"
    # exact rather than merely the right name.
    handle: int | None = None


@dataclass
class EquippedLoadout:
    """One stored loadout: a vessel and the six slots as the game has them."""
    hero_id: int
    vessel_id: int
    selected: bool
    # Six entries, None where the slot is empty. 0-2 normal, 3-5 Deep of Night.
    relics: list[OwnedItem | None] = field(default_factory=list)

    @property
    def deep_used(self) -> bool:
        return any(r is not None for r in self.relics[3:])


@dataclass
class Inventory:
    source: str
    # Kept apart from `source` because it contains the Steam account id, and
    # so belongs in a tooltip rather than on the face of the window.
    folder: str = ""
    relic_count: int = 0
    # slot colour -> set of effect ids obtainable in that colour
    effects_by_colour: dict[int, set[int]] = field(default_factory=dict)
    relics: list[OwnedItem] = field(default_factory=list)
    # Every stored loadout, or empty if this save has no readable table.
    loadouts: list[EquippedLoadout] = field(default_factory=list)

    def selected_loadout(self, hero_id: int) -> EquippedLoadout | None:
        """The loadout for the vessel this Nightfarer currently has on."""
        for entry in self.loadouts:
            if entry.hero_id == hero_id and entry.selected:
                return entry
        return None

    def available(self, colour: int, white_slot: int = 4) -> set[int]:
        if colour == white_slot:
            out: set[int] = set()
            for ids in self.effects_by_colour.values():
                out |= ids
            return out
        return self.effects_by_colour.get(colour, set())

    def relics_for(self, colour: int, deep: bool, white_slot: int = 4) -> list[OwnedItem]:
        """Relics that may go into a slot of this colour and mode."""
        return sorted(
            (
                r for r in self.relics
                if r.is_deep == deep and (colour == white_slot or r.colour == colour)
            ),
            key=lambda r: (r.name, r.relic_id),
        )


def _decrypt_slots(path: pathlib.Path) -> dict[str, bytes]:
    blob = path.read_bytes()
    out = {}
    for _i, name, offset, size in savefile._members(blob):
        raw = blob[offset : offset + size]
        iv, body = raw[:16], raw[16:]
        plain = AES.new(savefile.SAVE_KEY, AES.MODE_CBC, iv).decrypt(
            body[: len(body) // 16 * 16]
        )
        if plain.count(0) != len(plain):
            out[name] = plain
    return out


def load(data: dict, save_path: pathlib.Path | None = None) -> Inventory | None:
    """Scan the newest save and return what the player owns, or None."""
    saves = [save_path] if save_path else savefile.find_saves()
    saves = [p for p in saves if p and p.exists()]
    if not saves:
        return None

    path = max(saves, key=lambda p: p.stat().st_mtime)
    relic_meta = {r["id"]: r for r in data["relics"]}
    valid_relics = set(relic_meta)
    valid_effects = {int(k) for k in data["effects"]}

    best: Inventory | None = None
    for name, blob in _decrypt_slots(path).items():
        owned = savefile.read_owned_relics(blob, valid_relics, valid_effects)
        if not owned:
            continue

        # The save folder is named after the Steam account id. Naming it in
        # the window puts that id into every screenshot and bug report, so
        # the label says which slot is loaded and the id stays in the path.
        inv = Inventory(source=name, folder=str(path.parent))
        by_offset = savefile.read_relic_handles(blob, owned)
        handle_of = {relic.offset: handle for handle, relic in by_offset.items()}
        item_by_handle: dict[int, OwnedItem] = {}

        for entry in owned:
            meta = relic_meta.get(entry.relic_id)
            if meta is None:
                continue
            colour = meta["colour"]
            inv.effects_by_colour.setdefault(colour, set()).update(entry.effect_ids)
            handle = handle_of.get(entry.offset)
            item = OwnedItem(
                relic_id=entry.relic_id,
                name=meta["name"].strip(),
                colour=colour,
                effect_ids=entry.effect_ids,
                is_deep=bool(meta.get("is_deep")),
                has_curse=bool(meta.get("has_curse")),
                icon=meta.get("icon"),
                caption=meta.get("caption", ""),
                curse_ids=list(entry.curse_ids),
                handle=handle,
            )
            inv.relics.append(item)
            if handle is not None:
                item_by_handle[handle] = item
        inv.relic_count = len(inv.relics)

        # The equipped-loadout table lives in the same member as the inventory.
        # A save from before the table existed, or one this reader does not
        # recognise, simply leaves the list empty -- the planner then behaves
        # exactly as it did before.
        try:
            stored = savefile.read_loadouts(blob)
        except (ValueError, struct.error):
            stored = []
        for entry in stored:
            inv.loadouts.append(
                EquippedLoadout(
                    hero_id=entry.hero_id,
                    vessel_id=entry.vessel_id,
                    selected=entry.selected,
                    relics=[item_by_handle.get(h) if h else None
                            for h in entry.handles],
                )
            )

        if best is None or inv.relic_count > best.relic_count:
            best = inv

    return best
