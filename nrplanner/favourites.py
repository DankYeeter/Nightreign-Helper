"""Per-Nightfarer relic favourites.

A favourite is a relic the player has marked as wanted for one or more
Nightfarers. It changes nothing about the build; it only pulls that relic to
the front of the picker so a good roll does not have to be hunted for again in
a grid of two hundred.

Kept in the same QSettings the artwork variants use, so it survives restarts
without adding a file of its own.
"""

from __future__ import annotations

from PySide6.QtCore import QSettings

ORG = "DankYeeter"
APP = "NightreignHelper"
GROUP = "favourites"


def _settings() -> QSettings:
    return QSettings(ORG, APP)


def key(item) -> str:
    """Identify a relic by the roll it carries, not by its handle.

    The save's handle is per-copy and changes when a relic is melted and a new
    one earned, and two copies with the same roll are interchangeable anyway,
    so the roll is what a favourite should follow. Curses are part of it: the
    same relic with and without a curse is not the same thing to a player.
    """
    effects = ",".join(str(e) for e in item.effect_ids)
    curses = ",".join(str(c) for c in (getattr(item, "curse_ids", None) or ()))
    return f"{item.relic_id}|{effects}|{curses}"


def heroes_for(item) -> set[int]:
    """Nightfarer ids this relic is favourited for."""
    raw = _settings().value(f"{GROUP}/{key(item)}", "", type=str)
    out = set()
    for part in str(raw).split(","):
        part = part.strip()
        if part:
            try:
                out.add(int(part))
            except ValueError:
                continue
    return out


def is_favourite(item, hero_id: int) -> bool:
    return hero_id in heroes_for(item)


def set_favourite(item, hero_id: int, wanted: bool) -> None:
    heroes = heroes_for(item)
    if wanted:
        heroes.add(hero_id)
    else:
        heroes.discard(hero_id)
    settings = _settings()
    path = f"{GROUP}/{key(item)}"
    # An empty entry is a dead key that would be reloaded and re-parsed for
    # the rest of the save's life, so unfavouriting removes it outright.
    if heroes:
        settings.setValue(path, ",".join(str(h) for h in sorted(heroes)))
    else:
        settings.remove(path)


def toggle(item, hero_id: int) -> bool:
    """Flip this relic's favourite state for one Nightfarer; returns the new one."""
    wanted = not is_favourite(item, hero_id)
    set_favourite(item, hero_id, wanted)
    return wanted
