"""Read the player's actually owned relics for filtering the planner."""

from __future__ import annotations

import pathlib
import struct
from dataclasses import dataclass, field

from Crypto.Cipher import AES

from nrdata import savefile

from . import errortext


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
    # Where this copy's record sits in the character slot. One record is one
    # relic -- established when the relic count was matched against the game,
    # 284 records to 284 relics -- so the offset identifies the copy even on a
    # save whose loadout table cannot be read and which therefore has no
    # handles. See copy_key.
    offset: int | None = None


def copy_key(item) -> tuple[str, int] | None:
    """What makes two entries the same *physical* relic, or None.

    A relic can be worn in one slot at a time, so the planner has to be able
    to tell one copy from another. The handle is the exact answer -- it is
    what the save's own loadout table uses -- but it is not always there: a
    save whose loadout table cannot be read yields no handles at all.

    Dropping those relics from the planner would cost far more than the rule
    is worth (a player with an unreadable table would be offered nothing),
    and treating them as endlessly available would abandon the rule precisely
    where it cannot be checked. Neither is necessary: the record's own offset
    in the save identifies the copy just as exactly, because one record is one
    relic. So the handle answers when it can and the offset answers otherwise.

    Returns None for anything that is not a copy the player owns -- an empty
    slot, or a custom relic, which is imaginary by design and may therefore
    be planned into as many slots as the player likes.
    """
    if item is None or getattr(item, "relic_id", None) == CUSTOM_RELIC_ID:
        return None
    if item.handle is not None:
        return ("handle", item.handle)
    if item.offset is not None:
        return ("record", item.offset)
    return None


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
    # How many bytes of character slot these relics were read out of, or None
    # when this inventory did not come from a save file at all -- a hand-built
    # one in a test has no save behind it and so makes no claim about density.
    # `relics_for` needs it for the second SEC-022 check.
    source_bytes: int | None = None
    # Whether these relics were read on the slow way (AD-031). True when the
    # dataset numbers a relic at or above `savefile.RELIC_ID_CEILING`, which
    # the fast prefilter cannot see: the read then falls back to the walk that
    # assumes nothing about ids, and the window says so (AK-228). A plain bool
    # with a default, so every hand-built `Inventory` stays valid and the
    # value crosses the worker's thread boundary unchanged (AD-006.8).
    read_the_slow_way: bool = False

    def _refuse_a_density_no_save_can_have(self) -> None:
        """The second SEC-022/SEC-034 limit, on the way out rather than in.

        `savefile.read_owned_relics` already refuses to build a list denser
        than one record per `MIN_BYTES_PER_RELIC_RECORD` bytes of slot, or
        longer than `MOST_RELIC_RECORDS_A_SLOT_MAY_HOLD` whatever the slot's
        size. This asks the same two questions of the finished list, at the
        door every reader that wants to know what fits a slot goes through:
        the planner's slots,
        and -- by way of `advisor.run.frozen_inventory` -- the advisor's
        pre-sort, which costs 175,6 us per offered relic
        (`scripts/measure_advisor_cancel.py`, 309 relics, six free slots, this
        machine) and so is where an inventory that got past the reader would
        be felt. Readers that only walk the list, such as the picker's map of
        handles, are a dict comprehension and not a place a size can hurt.

        Two checks and not one, because a limit in the reader is a property of
        that function and a player is protected by the property rather than by
        the line: whoever writes the next reader, or loosens this one, still
        cannot get such a list as far as the search.
        """
        if self.source_bytes is None:
            return
        by_density = max(1, self.source_bytes
                         // savefile.MIN_BYTES_PER_RELIC_RECORD)
        limit = min(by_density, savefile.MOST_RELIC_RECORDS_A_SLOT_MAY_HOLD)
        if len(self.relics) > limit:
            # Whole sentences, for the reason `read_owned_relics` states at
            # the same place: AK-229 collects what this path can say out of
            # the `raise` itself.
            if limit == by_density:
                raise ValueError(
                    f"this inventory holds {len(self.relics)} relics read "
                    f"from {self.source_bytes} bytes of save slot, denser "
                    f"than one per {savefile.MIN_BYTES_PER_RELIC_RECORD} "
                    f"bytes, which is not an inventory; the file is damaged "
                    f"or was not written by the game. Take it out of the "
                    f"save folder and rescan.")
            raise ValueError(
                f"this inventory holds {len(self.relics)} relics read from "
                f"{self.source_bytes} bytes of save slot, more records than "
                f"any save this game writes, which is not an inventory; the "
                f"file is damaged or was not written by the game. Take it "
                f"out of the save folder and rescan.")

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
        self._refuse_a_density_no_save_can_have()
        return sorted(
            (
                r for r in self.relics
                if r.is_deep == deep and (colour == white_slot or r.colour == colour)
            ),
            key=lambda r: (r.name, r.relic_id),
        )


#: The largest file this program will read as a save (SEC-029).
#:
#: Derived, not chosen. The saves on this installation are 19 531 312 bytes
#: each -- both accounts, measured 09.09.2026 with
#: `find %APPDATA%/Nightreign -printf "%s"` -- and the file is a fixed layout
#: of character slots rather than a container that grows with what is in it.
#: 256 MiB is 13,7 times that, so no save this program will ever meet is cut
#: off, and the refusal is loud: it carries the size it refused.
#:
#: Why a limit at all: `_read_settled` reads whatever it is handed **whole**
#: before the first check on its contents runs, so a 30 GB disk image would
#: be allocated in full and only then thrown away. That is true of both ways
#: a file gets here -- the one the player picked through `Find my save...`,
#: whose filter is `All files (*)`, and the ones the automatic route takes
#: out of the profile folder itself, which nobody chose and which the program
#: therefore knows even less about.
LARGEST_SAVE_TO_READ = 256 * 1024 * 1024


def refuse_a_size_no_save_can_have(size: int) -> None:
    """Stop before a file too large to be a save is read into memory.

    SEC-029. Size is what can be known without reading anything -- `stat()`
    costs no bytes -- and it is the only question that has to be answered
    before the file is in memory rather than after.

    Asked in bytes rather than of a path, because both callers have stat'ed
    the file already for their own reasons and a second `stat` would be a
    second answer to a question that has one.

    **No path in the message** (AK-126): the save folder is named after the
    Steam account id, and this sentence is shown to the player.
    """
    if size > LARGEST_SAVE_TO_READ:
        raise ValueError(
            f"the file is {size // (1024 * 1024)} MB, far larger than any "
            f"save this game writes")


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

    The size the settling is judged by is the size SEC-029 is judged by, and
    it is looked at here because this is the line that would allocate it: one
    `stat` already stands in front of the read, and everything above it in
    the program has already handed the file on.
    """
    blob = b""
    for _ in range(attempts):
        before = path.stat()
        refuse_a_size_no_save_can_have(before.st_size)
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


@dataclass(frozen=True)
class SaveScan:
    """One character slot as it came off the disk, before it is an `Inventory`.

    The boundary AD-029 point 1 draws: everything expensive -- finding the
    files, decrypting them, walking the records -- happens on one side of this
    object, and building the planner's living `Inventory` out of it happens on
    the other. That is what lets the reading run in a thread of its own while
    AD-006.8 stands: what crosses is this, and everything in it is a record
    read out of bytes, never a widget and never the `Inventory` the window
    holds.

    Frozen for the reason the advisor's `Question` is frozen: it is handed to
    a thread that must not be able to change what the main thread will read
    back. The lists inside are not deep-frozen -- Python has no such thing --
    but nothing on either side writes to them, and the worker is thrown away
    the moment it has emitted this.
    """

    #: The save's own slot name, which is what the window shows.
    source: str
    #: The folder the file was found in. Kept apart from `source` because it
    #: contains the Steam account id (see `Inventory.folder`).
    folder: str
    #: How many bytes of character slot the records were read out of, for the
    #: second SEC-022 check.
    source_bytes: int
    #: Every relic record this slot holds, as `savefile` read it.
    owned: list
    #: Record offset -> this copy's handle in the save.
    handle_of: dict
    #: Every stored loadout, or empty when the table could not be read.
    loadouts: list
    #: Why the loadouts are missing, when they are.
    loadout_error: str = ""
    #: Whether this slot was walked the slow way (AD-031). Carried across the
    #: boundary with everything else the reading half found out, because the
    #: half that builds the window has no dataset to ask again.
    read_the_slow_way: bool = False


class SaveNotReadable(ValueError):
    """A save file was there and could not be read.

    The difference "nothing was found" was standing in for. A scan that
    answers None for both says of a save that exists and cannot be opened
    that there is none, which is not a missing answer but a wrong one -- the
    one thing GOAL A7 is about. So the two answers are two things: None is
    "there is no save here", and this carries the reason the one that is
    here could not be read (`UI_SPEC` T-141 §9 (g)).

    A `ValueError`, because that is what every caller of this module already
    treats as "this file was no good": the reading worker turns it into the
    one line the window shows, and nothing has to learn a new exception to
    keep working.

    Being a class of this program is what lets the window quote it at all:
    `errortext.in_english` passes the words of an exception this program
    defines and maps every other exception on to a sentence of its own
    (QA-211). Everything raised here is therefore written here, in English.
    """


def _changed_at(path: pathlib.Path) -> float:
    """When this save was last written, or 0.0 when that cannot be asked.

    A sort key and nothing more, so a file that has gone since it was found
    sorts oldest and is tried last rather than taking the whole scan down
    with it (SEC-035). The window between finding the saves and stat'ing them
    is small and real: a removable drive pulled out, a network path dropped,
    the game rewriting its file.

    Why it may not raise: the raw `OSError` would reach `_SaveReadWorker.work`
    and be put in the line under the save. Even now that nothing quotes an
    exception there (QA-211), a failure here is not news the player can act
    on -- the next file may well be the good one. `_scan_save` already answers
    the same question this way for the read itself; this is the one `stat`
    that stood outside it.

    The shape is `gamefiles._changed_at`'s, which answers the same question
    about the game's folders.
    """
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def load(data: dict, save_path: pathlib.Path | None = None) -> Inventory | None:
    """Scan the player's saves and return what they own, or None.

    The two halves in one call, for every caller that has no thread to put the
    first half in -- the tests, the measuring scripts, and any code that wants
    the inventory and nothing else. The window uses `scan` and `build`
    separately (AD-029 point 1); this is the same work in the same order, so
    the two cannot come to mean different things by one save.

    Which includes the failures: a set of saves of which none can be read
    raises `SaveNotReadable` out of here exactly as it does out of `scan`.
    Swallowing it would make this call mean something different from the two
    halves it stands for.
    """
    found = scan(data, save_path)
    return None if found is None else build(data, found)


def scan(data: dict, save_path: pathlib.Path | None = None) -> SaveScan | None:
    """Read the player's saves off the disk. The expensive half, and no Qt.

    Every save found is tried, newest first, rather than only the newest one.
    A machine can hold more than one -- a second Steam account folder, a save
    restored from a backup, a leftover from a reinstall -- and picking by
    modification time alone would pick the wrong one and then report the whole
    installation as unreadable. The best-populated save wins, which is the
    same rule already used to choose between the slots inside one file.

    "Best-populated" counts records here rather than the relics the planner
    ends up with, and the two are the same number: `read_owned_relics` is
    given the ids of the dataset as its filter, so every record it hands back
    has an entry in the metadata `build` looks it up in. Counting records is
    what lets the choice be made on this side of the boundary, which is the
    side that has the bytes.

    Nothing here touches a widget, the settings store or the dataset beyond
    reading two of its fields, so it is safe to run in a thread of its own --
    which is the whole point of the split (AD-029 point 1).
    """
    saves = [save_path] if save_path else savefile.find_saves()
    saves = [p for p in saves if p and p.exists()]
    if not saves:
        return None

    valid_relics = {r["id"] for r in data["relics"]}
    valid_effects = {int(k) for k in data["effects"]}
    # Once per load and not once per slot: the question is about the dataset,
    # which does not change between the slots of a read (AD-031). Deciding it
    # here also keeps it on this side of the boundary, where the answer can
    # travel with the records it belongs to.
    mode = savefile.relic_scan_mode(valid_relics)

    best: SaveScan | None = None
    unreadable = ""
    for path in sorted(saves, key=_changed_at, reverse=True):
        try:
            best = _scan_save(path, valid_relics, valid_effects, best,
                              mode=mode)
        except SaveNotReadable as exc:
            # One file that cannot be read is no reason to abandon the others:
            # a save half-written by a running game, or a truncated backup,
            # would otherwise take down the scan before it reached a good one.
            # The reason is kept in case none of them turns out to be good --
            # the first one, which is the newest, because that is the file the
            # player most likely means.
            unreadable = unreadable or errortext.in_english(exc)
    if best is None and unreadable:
        raise SaveNotReadable(unreadable)
    return best


def build(data: dict, found: SaveScan) -> Inventory:
    """Turn one scanned save into what the planner reads. The cheap half.

    Records in, `OwnedItem`s out: this is where the dataset's names, colours
    and icons are put on what the save had, and it is the only half that knows
    what a relic is called. It stays in the thread that owns the `Inventory`
    (AD-006.8).
    """
    relic_meta = {r["id"]: r for r in data["relics"]}
    inv = Inventory(source=found.source, folder=found.folder,
                    source_bytes=found.source_bytes,
                    loadout_error=found.loadout_error,
                    read_the_slow_way=found.read_the_slow_way)
    item_by_handle: dict[int, OwnedItem] = {}

    for entry in found.owned:
        meta = relic_meta.get(entry.relic_id)
        if meta is None:
            continue
        colour = meta["colour"]
        inv.effects_by_colour.setdefault(colour, set()).update(entry.effect_ids)
        handle = found.handle_of.get(entry.offset)
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
            offset=entry.offset,
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

    for entry in found.loadouts:
        inv.loadouts.append(
            EquippedLoadout(
                hero_id=entry.hero_id,
                vessel_id=entry.vessel_id,
                selected=entry.selected,
                relics=[item_by_handle.get(h) if h else None
                        for h in entry.handles],
            )
        )
    return inv


def _scan_save(path: pathlib.Path, valid_relics: set, valid_effects: set,
               best: SaveScan | None, *, mode: str) -> SaveScan | None:
    """Read one save file, returning it if it beats what was found so far.

    A file that cannot be read leaves here as `SaveNotReadable` rather than as
    the untouched `best`: whether the scan goes on to the next file is the
    caller's decision and it still makes it, but the reason is no longer lost
    on the way, and a scan that ends with nothing can say which of the two
    endings it had.
    """
    try:
        slots = _decrypt_slots(path)
    except Exception as exc:  # noqa: BLE001 - said in one line, never raw
        # One handler for both, because the answer to both is the same one
        # sentence. `str(OSError)` writes the whole path into the message and
        # the save folder is named after the Steam account id (AK-126), while
        # `strerror` is in the language of the Windows installation and breaks
        # A8 (QA-211). `errortext` says what happened without saying where and
        # without letting Windows choose the words.
        raise SaveNotReadable(errortext.in_english(exc)) from exc

    for name, blob in slots.items():
        owned = savefile.read_owned_relics(blob, valid_relics, valid_effects,
                                           mode=mode)
        if not owned:
            continue

        by_offset = savefile.read_relic_handles(blob, owned)
        # The equipped-loadout table lives in the same member as the inventory.
        # A save from before the table existed, or one this reader does not
        # recognise, simply leaves the list empty -- the planner then behaves
        # exactly as it did before.
        loadout_error = ""
        try:
            stored = savefile.read_loadouts(blob)
        except (ValueError, struct.error) as exc:
            stored = []
            loadout_error = str(exc)

        # The save folder is named after the Steam account id. Naming it in
        # the window puts that id into every screenshot and bug report, so
        # the label says which slot is loaded and the id stays in the path.
        found = SaveScan(
            source=name,
            folder=str(path.parent),
            source_bytes=len(blob),
            owned=owned,
            handle_of={relic.offset: handle
                       for handle, relic in by_offset.items()},
            loadouts=stored,
            loadout_error=loadout_error,
            read_the_slow_way=(mode == savefile.SLOW),
        )
        if best is None or len(found.owned) > len(best.owned):
            best = found

    return best
