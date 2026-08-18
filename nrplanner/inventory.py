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
    # Why the loadouts are missing, when they are. A save that reads its
    # relics but not its builds used to be indistinguishable from one that has
    # no builds stored, which made the failure impossible to report.
    loadout_error: str = ""

    def loadouts_for(self, hero_id: int) -> list[EquippedLoadout]:
        """Every chalice this Nightfarer has, not only the one worn.

        The save stores all of them, and a player who builds several and
        wears one still expects to see the others.
        """
        return [e for e in self.loadouts if e.hero_id == hero_id]

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


def _read_settled(path: pathlib.Path, attempts: int = 3) -> bytes:
    """The save's bytes, read while the game was not part-way through writing.

    The game rewrites this file in place, and a read taken during that gets a
    file that was never real. Measured: a scan during a write reported 290
    relic records where a scan of the settled file reported 284, which is
    exactly what the game itself showed. The extra records were well-formed and
    simply not there afterwards.

    So the read is only trusted when the file did not change across it. Size
    and mtime are what a rewrite in progress moves, and checking them costs
    nothing next to decrypting 19 MB. Three tries, then the last read is
    returned anyway -- a slightly wrong count is a better answer than none, and
    the caller has no better file to offer.
    """
    blob = b""
    for _ in range(attempts):
        before = path.stat()
        blob = path.read_bytes()
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns):
            return blob
    return blob


def _decrypt_slots(path: pathlib.Path) -> dict[str, bytes]:
    blob = _read_settled(path)
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
    """Scan the player's saves and return what they own, or None.

    Every save found is tried, newest first, rather than only the newest one.
    A machine can hold more than one -- a second Steam account folder, a save
    restored from a backup, a leftover from a reinstall -- and picking by
    modification time alone would pick the wrong one and then report the whole
    installation as unreadable. The best-populated save wins, which is the
    same rule already used to choose between the slots inside one file.
    """
    saves = [save_path] if save_path else savefile.find_saves()
    saves = [p for p in saves if p and p.exists()]
    if not saves:
        return None

    relic_meta = {r["id"]: r for r in data["relics"]}
    valid_relics = set(relic_meta)
    valid_effects = {int(k) for k in data["effects"]}

    best: Inventory | None = None
    for path in sorted(saves, key=lambda p: p.stat().st_mtime, reverse=True):
        best = _scan_save(path, relic_meta, valid_relics, valid_effects, best)
    return best


def _scan_save(path: pathlib.Path, relic_meta: dict, valid_relics: set,
               valid_effects: set, best: Inventory | None) -> Inventory | None:
    """Read one save file, returning it if it beats what was found so far."""
    try:
        slots = _decrypt_slots(path)
    except Exception:  # noqa: BLE001
        # An unreadable file is not a reason to abandon the others. A save
        # half-written by a running game, or a truncated backup, would
        # otherwise take down the scan before it reached a good one.
        return best

    for name, blob in slots.items():
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
        # One record, one relic. This used to count distinct *rolls* instead,
        # to correct an over-count of 275 found against 273 shown -- the two
        # extras being byte-identical duplicates of a real relic.
        #
        # That correction was aimed at the wrong thing. Re-measured 2026-08-14
        # against a settled file: 284 records read, 284 relics shown in game,
        # an exact match with nothing to collapse. The over-count came from
        # reading the save while it was being written, which _read_settled now
        # refuses to do; it was never a surplus of records to be deduplicated.
        # The old correction did not even close the gap it was written for --
        # it took 290 down to 288 against a true 284.
        #
        # Keeping it would be actively wrong. Collapsing rolls can only ever
        # lower the number, the number is already exact, and the day two relics
        # roll identically -- which is ordinary, not exotic -- it would quietly
        # report one relic fewer than the player owns.
        inv.relic_count = len(inv.relics)

        # The equipped-loadout table lives in the same member as the inventory.
        # A save from before the table existed, or one this reader does not
        # recognise, simply leaves the list empty -- the planner then behaves
        # exactly as it did before.
        try:
            stored = savefile.read_loadouts(blob)
        except (ValueError, struct.error) as exc:
            stored = []
            inv.loadout_error = str(exc)
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
