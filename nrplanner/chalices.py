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
    settings = _settings()
    settings.beginGroup(f"{BUILDS}/{hero_id}")
    try:
        order = settings.value("__order", "", type=str)
        names = [n for n in str(order).split(SEPARATOR) if n]
        # Anything written without an order entry still has to appear. The
        # bookkeeping keys are not builds and must never be offered as one.
        for key in settings.childKeys():
            if not key.startswith("__") and key not in names:
                names.append(key)
        return [n for n in names
                if not n.startswith("__") and settings.contains(n)]
    finally:
        settings.endGroup()


def save_build(hero_id: int, name: str, vessel_id: int | None, deep: bool,
               slots: list[str]) -> None:
    """Store a build under a name, replacing one of the same name."""
    name = name.strip()
    if not name or name == EQUIPPED_NAME:
        return
    settings = _settings()
    settings.beginGroup(f"{BUILDS}/{hero_id}")
    try:
        existing = [n for n in str(
            settings.value("__order", "", type=str)).split(SEPARATOR) if n]
        if name not in existing:
            existing.append(name)
        settings.setValue("__order", SEPARATOR.join(existing))
        settings.setValue(name, _encode(vessel_id, deep, slots))
    finally:
        settings.endGroup()


def load_build(hero_id: int, name: str) -> tuple[int | None, bool, list[str]]:
    settings = _settings()
    settings.beginGroup(f"{BUILDS}/{hero_id}")
    try:
        return _decode(settings.value(name, "", type=str))
    finally:
        settings.endGroup()


def delete_build(hero_id: int, name: str) -> None:
    """Forget a saved build. The equipped one is not ours to delete."""
    if name == EQUIPPED_NAME:
        return
    settings = _settings()
    settings.beginGroup(f"{BUILDS}/{hero_id}")
    try:
        settings.remove(name)
        order = [n for n in str(
            settings.value("__order", "", type=str)).split(SEPARATOR)
            if n and n != name]
        settings.setValue("__order", SEPARATOR.join(order))
    finally:
        settings.endGroup()


def hidden_builds(hero_id: int) -> set[str]:
    """Builds the player has hidden from the list, the equipped one included."""
    raw = _settings().value(f"{BUILDS}/{hero_id}/__hidden", "", type=str)
    return {n for n in str(raw).split(SEPARATOR) if n}


def set_hidden(hero_id: int, name: str, hidden: bool) -> None:
    names = hidden_builds(hero_id)
    names.add(name) if hidden else names.discard(name)
    _settings().setValue(f"{BUILDS}/{hero_id}/__hidden",
                         SEPARATOR.join(sorted(names)))


def selected_build(hero_id: int) -> str:
    """Which build this Nightfarer had selected when the program last closed.

    Stored so a session picks up where the last one left off: without it the
    list always reopened on the equipped build, quietly discarding the choice
    a player had made.
    """
    return str(_settings().value(f"{BUILDS}/{hero_id}/__selected",
                                 EQUIPPED_NAME, type=str) or EQUIPPED_NAME)


def set_selected_build(hero_id: int, name: str) -> None:
    _settings().setValue(f"{BUILDS}/{hero_id}/__selected", name)


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
