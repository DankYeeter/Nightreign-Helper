"""The build each Nightfarer is left holding, remembered between sessions.

Closing the program used to throw away every vessel and every relic placed in
it. That is fine for a scratchpad and wrong for a planner: a build is worked
out once and then referred to for as long as the relics behind it are owned,
and having to rebuild all six slots on every launch is what stops it being
referred to at all.

Kept in the same QSettings as the relic favourites, so it needs no file of its
own and no migration when the snapshot is rebuilt.

Relics are stored by handle *and* by roll. The handle is exact -- it picks out
one copy of a relic among several with different rolls -- but it belongs to
the save, and melting a relic or moving to another machine renumbers it. The
roll survives all of that and identifies an interchangeable copy. Trying the
handle first and the roll second means a build comes back exactly as it was
left where the save still agrees, and as near as makes no difference where it
does not.
"""

from __future__ import annotations

import string
import urllib.parse

from PySide6.QtCore import QSettings

from . import favourites

GROUP = "chalices"
SEPARATOR = "|"
FIELD = "\x1f"


def _settings() -> QSettings:
    return QSettings(favourites.ORG, favourites.APP)


def slot_key(item) -> str:
    """How one equipped relic is written down: its handle, then its roll."""
    if item is None:
        return ""
    handle = getattr(item, "handle", None)
    return f"{handle if handle is not None else ''}{SEPARATOR}{favourites.key(item)}"


def split_key(key: str) -> tuple[int | None, str]:
    """The handle and roll a stored slot names, either of which may be absent."""
    handle_text, _, roll = str(key).partition(SEPARATOR)
    try:
        handle = int(handle_text)
    except ValueError:
        handle = None
    return handle, roll


def save(hero_id: int, vessel_id: int | None, deep: bool, slots: list[str]) -> None:
    """Remember what this Nightfarer is holding.

    An empty build is removed rather than written. Otherwise clearing every
    slot would leave a stored record that says "no vessel, nothing equipped",
    which reloads as a build and stops the list falling back to its default.

    `deep` records whether this build uses the three Deep of Night slots, and
    is taken from the slots themselves rather than from the switch on screen.
    The switch is a view -- it belongs to the player, not to the chalice --
    and is stored by save_view(). Reading it here meant importing a build
    while the switch happened to be on marked that build as Deep even when
    the game says it is not.
    """
    settings = _settings()
    # Keyed per vessel, not per Nightfarer. With one key per Nightfarer,
    # selecting another chalice cleared the slots -- correctly, since the
    # colours differ -- and the write that followed stored that empty state
    # over the build, so switching away and back destroyed it. Each vessel
    # now keeps its own arrangement, which is also what the save file does:
    # 110 records, one per vessel.
    path = f"{GROUP}/{hero_id}/{vessel_id}"
    settings.setValue(f"{GROUP}/{hero_id}/__last", vessel_id)
    if vessel_id is None and not any(slots):
        settings.remove(path)
        return
    deep = any(slots[3:6])
    parts = [str(vessel_id if vessel_id is not None else ""),
             "1" if deep else "0"]
    parts.extend(slots)
    settings.setValue(path, FIELD.join(parts))


def save_view(hero_id: int, vessel_id: int | None, deep: bool) -> None:
    """Remember what the player is looking at, apart from what is equipped.

    Which chalice is open and whether Deep of Night is on are view state, not
    a build, and they have to persist even when the vessel is empty. Storing
    them inside the build record meant they were dropped by the guard that
    stops an empty set of slots overwriting a real build -- so selecting an
    empty chalice, turning Deep on and restarting came back to neither.
    """
    settings = _settings()
    if vessel_id is not None:
        settings.setValue(f"{BUILDS}/{hero_id}/__last", vessel_id)
    settings.setValue(f"{BUILDS}/{hero_id}/__deep", "1" if deep else "0")


def view(hero_id: int) -> tuple[int | None, bool]:
    """(vessel this Nightfarer was last on, Deep of Night as they left it)."""
    settings = _settings()
    raw = settings.value(f"{BUILDS}/{hero_id}/__last", "", type=str)
    try:
        vessel_id = int(raw)
    except (TypeError, ValueError):
        vessel_id = None
    deep = str(settings.value(f"{BUILDS}/{hero_id}/__deep", "", type=str)) == "1"
    return vessel_id, deep


def last_vessel(hero_id: int) -> int | None:
    """The vessel this Nightfarer was last working on."""
    raw = _settings().value(f"{GROUP}/{hero_id}/__last", "", type=str)
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def load(hero_id: int, vessel_id: int | None = None) -> tuple[int | None, bool, list[str]]:
    """(vessel id, Deep of Night on, six slot keys) for one vessel.

    With no vessel given, the one this Nightfarer was last on is used, so a
    fresh session opens where the last one stopped.
    """
    settings = _settings()
    if vessel_id is None:
        vessel_id = view(hero_id)[0] or last_vessel(hero_id)
        if vessel_id is None:
            return None, False, []
    raw = settings.value(f"{GROUP}/{hero_id}/{vessel_id}", "", type=str)
    parts = str(raw).split(FIELD) if raw else []
    if len(parts) < 2:
        return None, False, []
    try:
        vessel_id = int(parts[0])
    except ValueError:
        vessel_id = None
    return vessel_id, parts[1] == "1", parts[2:]


def clear(hero_id: int, vessel_id: int | None = None) -> None:
    """Forget one vessel's build, or every one this Nightfarer has."""
    settings = _settings()
    if vessel_id is None:
        settings.remove(f"{GROUP}/{hero_id}")
    else:
        settings.remove(f"{GROUP}/{hero_id}/{vessel_id}")


# ---------------------------------------------------------------------------
# Named builds
#
# The single build above is the scratchpad: whatever the Nightfarer is holding
# right now, restored on the next launch. A named build is a copy of that put
# aside so several can be compared without rebuilding each one from its six
# slots.
#
# Names are stored under their own group, keyed by Nightfarer, and the encoded
# value is exactly the same string the scratchpad uses -- so a build saved
# today still loads after the format learns a new field, and there is only one
# encoder to keep right.
BUILDS = "builds"

# The build the save file says is equipped. It is not stored here at all: it
# is read from the save every time, which is what makes it always current and
# impossible to leave behind as a stale copy. The UI keeps it in the list,
# refuses to delete it, and lets it be hidden like any other.
EQUIPPED_NAME = "Equipped in game"

# The slots as they stand, belonging to no saved build. Nothing is stored
# under it -- the scratchpad already persists per vessel -- and it exists so
# the list can say "these are not one of your saved builds" instead of going
# on naming the last one loaded. Reset Chalice left it doing exactly that:
# the slots were empty, the picker still said "Test", and clicking that
# entry brought the build back, so the reset read as though it had half
# worked.
UNSAVED_NAME = "Unsaved build"

# Neither of the two above is a name a build may be saved under: one belongs
# to the save file and the other to the empty state.
RESERVED_NAMES = (EQUIPPED_NAME, UNSAVED_NAME)

# ---------------------------------------------------------------------------
# Where the player's name for a build ends and the store's key for it begins
#
# These were one thing, and a name is not a key. QSettings reads "/" in a key
# as the path separator it is, so a build called "Fire / ice" was never an
# entry of that name: it was a group called "Fire " holding an entry called
# " ice". `childKeys()` cannot see into a group, so the build dropped out of
# the list the moment it was saved, and deleting the Nightfarer's builds took
# the group with it -- the player's work gone, without an error anywhere
# (QA-003). Two smaller versions of the same mistake sat beside it: "|" splits
# one name into two in the order list, and a name beginning "__" reads as one
# of the bookkeeping entries.
#
# So the key is derived from the name and nothing else is stored: every
# character that is not a lower-case letter or a digit becomes %XX of its
# UTF-8 bytes. That derivation is
#   total       -- every name has a key, "/" and "\" and emoji included;
#   injective in the store -- no two names are filed in one place, which is a
#                  stronger thing than no two names sharing a string, and is
#                  the property that was missing (see below);
#   reversible  -- the name is read back out of the key, which is why the name
#                  is not written anywhere else and the two cannot drift;
#   inert       -- a key holds no "/", no "|" and no "\x1f", and cannot begin
#                  with "_", so nothing in it means anything to QSettings, to
#                  the order list or to the value encoding.
#
# The second line used to read "no two names share a key", and that was true
# and not enough. A key is the name of a registry value on Windows, and the
# registry tells value names apart without regard to their case. Keeping the
# capital letters therefore filed "Bleed build" and "bleed build" in one
# entry: two names in the list, one build behind both of them, and deleting
# either took the other with it (QA-046). What makes the derivation injective
# under the store's equality rather than only under Python's is two properties
# together:
#
#   the safe set holds no character that has a second spelling -- a-z and
#     0-9, never A-Z, so nothing a name says reaches the key as a character
#     the store could fold onto another one;
#   the escapes are written one way only -- %XX with the hex digits in
#     capitals, always. That is the spelling schema 2 already used, so a name
#     with no capital letters in it keeps the key it was filed under and the
#     move costs it nothing.
#
# Folding the case of a key cannot merge two of them. "%" has no case and
# every escape is exactly three characters long, so folding never moves a
# character across the line between an escape and a plain one: a folded key
# still reads one token at a time, each token still stands for one byte, and
# the bytes still spell one name.
_KEY_SAFE = frozenset(string.ascii_lowercase + string.digits)

# Set on a Nightfarer's group to say which derivation its builds are filed
# under. The marker is what makes each move a one-off: a second pass over
# migrated entries would encode the encoding, and "Fire %2F ice" is not a
# build anyone saved.
#
# "2" is the first derivation, injective in Python and not in the store. "3"
# is the one above. There is no marker for the state before either: a store
# from then carries none, and a group with no marker is read as holding names
# rather than keys.
SCHEMA_KEY = "__schema"
DERIVED_KEYS = "2"
CASE_SAFE_KEYS = "3"
CURRENT_SCHEMA = CASE_SAFE_KEYS


def build_key(name: str) -> str:
    """The storage key a build name is filed under."""
    return "".join(
        character if character in _KEY_SAFE
        else "".join(f"%{byte:02X}" for byte in character.encode("utf-8"))
        for character in str(name)
    )


def build_name(key: str) -> str:
    """The name a storage key was derived from, character for character."""
    return urllib.parse.unquote(str(key), encoding="utf-8", errors="replace")


# QSettings files each build as a registry value on Windows, and the registry
# takes at most 16 383 characters in the name of a value. The derived key is
# what goes there, and one character of a name can become twelve of key, so a
# name that looks short can still overrun the limit. Past it setValue writes
# nothing and reports nothing, and the build would be lost in silence with its
# name left behind in the order list (QA-035).
MAX_KEY_LENGTH = 16383


def name_fits_the_store(name: str) -> bool:
    """Whether the key derived from this name is short enough to be stored."""
    return len(build_key(name)) <= MAX_KEY_LENGTH


def _migrate_keys(hero_id: int) -> None:
    """File this Nightfarer's existing builds under derived keys, once.

    Everything saved before this change is filed under the name itself, so a
    fix that only changed how new builds are written would have hidden every
    old one. This runs first in every operation that touches a saved build.

    The old entries are collected with `allKeys()` rather than `childKeys()`
    because a name holding a "/" is exactly the case that has to be rescued
    and `childKeys()` is blind to it -- `allKeys()` walks into the group and
    reports the whole path, which is the name that was typed. Backslashes,
    leading spaces and non-ASCII survived as ordinary key characters and come
    back untouched. A name holding a "|" comes back, but at the end of the
    list: the order entry it was written into had already been split in two
    and there is no way to tell from here which half went where.

    Everything is read first, then written, then removed, and the removals
    come last of all. That order is the whole of QA-033. A name holding a "/"
    is a group as much as a key, so an old store holding "Fire ice" and
    "Fire ice/v2" holds the entry "Fire ice" and the group "Fire ice" side by
    side -- and `QSettings.remove("Fire ice")` takes the group away with the
    entry. Removing while still walking the list therefore deleted
    "Fire ice/v2" before it had been read, and the empty string that came
    back was written under its new key: the build gone from the store beyond
    recovery, its name still in the list, and the player left holding an
    empty vessel with no error anywhere. Read everything up front and a
    removal can take whatever it likes with it, because by then nothing is
    read or written again.

    Nor is a build given up on the strength of having been written. The old
    entry is removed only where the new key can be read back holding it, so a
    write that did not land -- for whatever reason the store had, which this
    code never has to enumerate -- costs the player a place in the order list
    and nothing else: the build stays where it was, and is listed after the
    ones that moved. Deciding this on the store's answer rather than on the
    shape of the name is what makes it hold for the reasons nobody has met
    yet (QA-041).

    Two starting points reach here, and the marker says which: a store from
    before there was a marker, where the key is the name as it was typed, and
    a store on schema 2, where the key is the name encoded with the capitals
    left standing. Both are read into names first and filed again from there,
    so there is one migration and not two.

    A store on schema 2 can hold a collision, and it is the reason for the
    move: two names that differ only in case were one entry, and the order
    list names both of them. Both are carried over, and both take the one
    value the store had for them -- which is the build the player saw under
    either name before this ran. It is not known which of the two the value
    was written for, so neither name is the one to drop, and from here on they
    are two entries that can be edited apart (QA-046).
    """
    settings = _settings()
    settings.beginGroup(f"{BUILDS}/{hero_id}")
    try:
        schema = settings.value(SCHEMA_KEY, "", type=str)
        if schema == CURRENT_SCHEMA:
            return
        # What a stored key says its build is called. Only schema 2 wrote a
        # marker of its own, so a group carrying anything else -- nothing at
        # all, in every store that reaches this -- holds names and not keys.
        name_of = build_name if schema == DERIVED_KEYS else str
        # Bookkeeping entries are not builds. A build whose name began "__"
        # was unreachable before this change for exactly that reason, so
        # there is none to rescue.
        old_paths = [k for k in settings.allKeys() if not k.startswith("__")]
        order = [n for n in str(settings.value("__order", "", type=str))
                 .split(SEPARATOR) if n]
        # A name in the order list the store answers for is a build too, even
        # where allKeys() does not report it. That is what a collision looks
        # like from here: one entry, and two names the store both accepts as
        # the name of it. Reading the value under each name is what gives the
        # two of them somewhere separate to go; going by allKeys() alone would
        # carry one name over and drop the other, which is the loss this move
        # exists to undo rather than to finish.
        named_only_in_the_list = [
            n for n in order if n not in old_paths
            and not n.startswith("__") and settings.contains(n)]
        sources = old_paths + named_only_in_the_list
        names = {source: name_of(source) for source in sources}
        keys = {source: build_key(names[source]) for source in sources}
        values = {source: settings.value(source, "", type=str)
                  for source in sources}
        for source in sources:
            settings.setValue(keys[source], values[source])
        # setValue answers nothing, so the store is asked instead of trusted.
        # A write can fail to land for more reasons than this code can name:
        # the registry refuses a value name longer than 16 383 characters
        # (QA-041), and a quota, a denied permission or a backend that will
        # not take some other shape of name would look exactly the same from
        # here -- like a write that worked. So nothing below rests on having
        # called setValue. A build counts as migrated only where its new key
        # is in the store holding what was written to it, and only such a
        # build gives up its old path. The sync is what puts the question to
        # the store rather than to the writes still pending inside it: the
        # registry answers from itself either way, a file-backed store would
        # answer out of its own cache and confirm whatever it had been told.
        settings.sync()
        migrated = {source for source in sources
                    if settings.contains(keys[source])
                    and settings.value(keys[source], "", type=str)
                    == values[source]}
        migrated_names = {names[source] for source in migrated}
        # The order list holds keys, so a key with nothing behind it has no
        # business in it: it shows no build, and save_build finds the name
        # already listed and leaves a later build of that name standing in
        # the phantom's place instead of at the end (QA-040). Old fragments
        # are how a name holding a "|" arrived -- as two halves, neither of
        # which names anything -- and a build that could not be written is
        # the same case seen from the other side.
        if order:
            settings.setValue("__order", SEPARATOR.join(
                keys[n] for n in order if n in migrated))
        # A hidden name holding a "|" reached this point as two fragments,
        # and neither of them names a build. Carried over as they stood they
        # became two hidden entries no build could answer for, so nothing
        # could ever un-hide them, while the build itself was left showing
        # (QA-034). Only a fragment that names a build the migration brought
        # through is kept, or the equipped build, which is hideable and
        # stored nowhere -- a mark on a key with nothing behind it is the
        # same phantom whether the name was split or the write was lost. The
        # rest is dropped, so a build hidden under such a name comes back
        # visible: hiding is a view and the player can set it again, where an
        # indelible phantom is nobody's to remove.
        # The comparison is on names and not on stored keys, because one of
        # the things it has to recognise is a reserved name -- and a store on
        # schema 2 spells "Equipped in game" encoded, so asking whether the
        # stored key is one of them answers no every time and the player's
        # mark on the equipped build is thrown away.
        hidden = [n for n in str(settings.value("__hidden", "", type=str))
                  .split(SEPARATOR) if n]
        if hidden:
            known = migrated_names | set(RESERVED_NAMES)
            settings.setValue("__hidden", SEPARATOR.join(
                build_key(name_of(n)) for n in hidden
                if name_of(n) in known))
        selected = str(settings.value("__selected", "", type=str) or "")
        if selected:
            settings.setValue("__selected", build_key(name_of(selected)))
        settings.setValue(SCHEMA_KEY, CURRENT_SCHEMA)
        # Last of all, because a removal is the one step here that cannot be
        # taken back, and only where both of these hold:
        #
        #   the old path is not one of the places just written to -- its own
        #     new key, or another build's; either way it holds a migrated
        #     build now, and removing it would delete the very thing that was
        #     rescued into it;
        #   the build was read back from its new key -- the old copy is not
        #     given up until the new one is known to exist.
        #
        # The two are independent: an old path can be a written key while its
        # own build migrated perfectly, and a build can migrate perfectly
        # while its old path is nobody else's key.
        #
        # "One of the places written to" is decided by folding case, not by
        # ==, because that is the question the store answers: it files
        # "Bleed%20build" and "bleed%20build" in one entry, so a removal that
        # went by == would delete the build it had just written. Folding
        # errs towards leaving an entry behind, which costs a stale line in
        # the list; going by == errs towards deleting a build.
        written = {key.casefold() for key in keys.values()}
        for path in old_paths:
            if path.casefold() not in written and path in migrated:
                settings.remove(path)
    finally:
        settings.endGroup()


def _encode(vessel_id: int | None, deep: bool, slots: list[str]) -> str:
    parts = [str(vessel_id if vessel_id is not None else ""),
             "1" if deep else "0"]
    parts.extend(slots)
    return FIELD.join(parts)


def _decode(raw: str) -> tuple[int | None, bool, list[str]]:
    parts = str(raw).split(FIELD) if raw else []
    if len(parts) < 2:
        return None, False, []
    try:
        vessel_id = int(parts[0])
    except ValueError:
        vessel_id = None
    return vessel_id, parts[1] == "1", parts[2:]


def build_names(hero_id: int) -> list[str]:
    """Every saved build for this Nightfarer, in the order they were saved."""
    _migrate_keys(hero_id)
    settings = _settings()
    settings.beginGroup(f"{BUILDS}/{hero_id}")
    try:
        order = settings.value("__order", "", type=str)
        keys = [k for k in str(order).split(SEPARATOR) if k]
        # Anything written without an order entry still has to appear. The
        # bookkeeping keys are not builds and must never be offered as one.
        #
        # Whether the order list already names an entry is the store's
        # question and not Python's. An entry the store spells one way while
        # the list spells it another is one build, not two, and comparing
        # with `in` would offer it twice -- twice under one name, which is
        # exactly the shape the player cannot act on.
        listed = {k.casefold() for k in keys}
        for key in settings.childKeys():
            if not key.startswith("__") and key.casefold() not in listed:
                keys.append(key)
                listed.add(key.casefold())
        return [build_name(k) for k in keys
                if not k.startswith("__") and settings.contains(k)]
    finally:
        settings.endGroup()


def save_build(hero_id: int, name: str, vessel_id: int | None, deep: bool,
               slots: list[str]) -> None:
    """Store a build under a name, replacing one of the same name.

    The name is stored exactly as it was given -- a leading space belongs to
    the player, not to this function -- and only the derived key reaches the
    settings store. A name that is nothing but whitespace is refused, because
    it would show in the list as a row with no label. So is one whose derived
    key is longer than the store will take: it cannot be written at all, and
    a caller that asks is told rather than left to find out (QA-035).

    The build goes in before the order list, never the other way round. An
    order entry for a value that never landed is a name in the list with
    nothing behind it, and the player cannot even delete it, because deleting
    works through the name the list offers.
    """
    if (not str(name).strip() or name in RESERVED_NAMES
            or not name_fits_the_store(name)):
        return
    _migrate_keys(hero_id)
    key = build_key(name)
    settings = _settings()
    settings.beginGroup(f"{BUILDS}/{hero_id}")
    try:
        settings.setValue(key, _encode(vessel_id, deep, slots))
        existing = [k for k in str(
            settings.value("__order", "", type=str)).split(SEPARATOR) if k]
        if key not in existing:
            existing.append(key)
        settings.setValue("__order", SEPARATOR.join(existing))
    finally:
        settings.endGroup()


def load_build(hero_id: int, name: str) -> tuple[int | None, bool, list[str]]:
    _migrate_keys(hero_id)
    settings = _settings()
    settings.beginGroup(f"{BUILDS}/{hero_id}")
    try:
        return _decode(settings.value(build_key(name), "", type=str))
    finally:
        settings.endGroup()


def delete_build(hero_id: int, name: str) -> None:
    """Forget a saved build, and everything else that named it.

    The reserved ones are not ours to delete. For the rest, the entry, its
    place in the order list, its hidden mark and the selection all go, because
    a mark that outlives the build it describes is inherited by the next build
    of that name: a deleted build that had been hidden left "hidden" behind,
    so saving a build under the same name again gave a build the player could
    not see -- present in the list until the next refresh, then filtered out
    of it and out of every later session, with the "Show hidden" box as the
    only way back (QA-039). Hiding is a view of a build; with the build gone
    there is nothing for it to be a view of.
    """
    if name in RESERVED_NAMES:
        return
    _migrate_keys(hero_id)
    key = build_key(name)
    settings = _settings()
    settings.beginGroup(f"{BUILDS}/{hero_id}")
    try:
        settings.remove(key)
        order = [k for k in str(
            settings.value("__order", "", type=str)).split(SEPARATOR)
            if k and k != key]
        settings.setValue("__order", SEPARATOR.join(order))
        hidden = [k for k in str(
            settings.value("__hidden", "", type=str)).split(SEPARATOR)
            if k and k != key]
        settings.setValue("__hidden", SEPARATOR.join(hidden))
        if str(settings.value("__selected", "", type=str) or "") == key:
            settings.remove("__selected")
    finally:
        settings.endGroup()


def hidden_builds(hero_id: int) -> set[str]:
    """Builds the player has hidden from the list, the equipped one included."""
    _migrate_keys(hero_id)
    raw = _settings().value(f"{BUILDS}/{hero_id}/__hidden", "", type=str)
    return {build_name(k) for k in str(raw).split(SEPARATOR) if k}


def set_hidden(hero_id: int, name: str, hidden: bool) -> None:
    names = hidden_builds(hero_id)
    names.add(name) if hidden else names.discard(name)
    _settings().setValue(f"{BUILDS}/{hero_id}/__hidden",
                         SEPARATOR.join(sorted(build_key(n) for n in names)))


def selected_build(hero_id: int) -> str:
    """The build this Nightfarer's picker was last set to.

    Set by the player when they choose one, and by the program when it reads
    the save: finding a vessel equipped for this Nightfarer puts the picker on
    the equipped build and stores that over whatever was there before, because
    what is on screen at that moment is the save's build and the picker has to
    say so. A session therefore opens on the equipped build wherever the save
    has one, and on the last build the player chose wherever it has not.
    """
    _migrate_keys(hero_id)
    key = str(_settings().value(f"{BUILDS}/{hero_id}/__selected", "",
                                type=str) or "")
    return build_name(key) if key else EQUIPPED_NAME


def set_selected_build(hero_id: int, name: str) -> None:
    _migrate_keys(hero_id)
    _settings().setValue(f"{BUILDS}/{hero_id}/__selected", build_key(name))


def imported(hero_id: int) -> bool:
    """Whether this Nightfarer's chalices have been read out of the save yet.

    A row draws its relics from that chalice's stored build, so a Nightfarer
    nobody had pressed Load equipped on showed a list of empty chalices --
    and pressing the button then changed the whole list at once. Reading the
    save the first time a Nightfarer is opened is what makes the list true
    without asking, and this flag is how "the first time" is known.
    """
    return _settings().value(f"{BUILDS}/{hero_id}/__imported", "", type=str) == "1"


def set_imported(hero_id: int) -> None:
    _settings().setValue(f"{BUILDS}/{hero_id}/__imported", "1")
