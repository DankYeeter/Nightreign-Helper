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
    """
    settings = _settings()
    path = f"{GROUP}/{hero_id}"
    if vessel_id is None and not any(slots):
        settings.remove(path)
        return
    parts = [str(vessel_id if vessel_id is not None else ""),
             "1" if deep else "0"]
    parts.extend(slots)
    settings.setValue(path, FIELD.join(parts))


def load(hero_id: int) -> tuple[int | None, bool, list[str]]:
    """(vessel id, Deep of Night on, six slot keys) for this Nightfarer."""
    raw = _settings().value(f"{GROUP}/{hero_id}", "", type=str)
    parts = str(raw).split(FIELD) if raw else []
    if len(parts) < 2:
        return None, False, []
    try:
        vessel_id = int(parts[0])
    except ValueError:
        vessel_id = None
    return vessel_id, parts[1] == "1", parts[2:]


def clear(hero_id: int) -> None:
    _settings().remove(f"{GROUP}/{hero_id}")
