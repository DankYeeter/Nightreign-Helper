"""Per-Nightfarer relic favourites.

A favourite is a relic the player has marked as wanted for one or more
Nightfarers. It changes nothing about the build; it only pulls that relic to
the front of the picker so a good roll does not have to be hunted for again in
a grid of two hundred.

Kept in the same QSettings the artwork variants use, so it survives restarts
without adding a file of its own.
"""

from __future__ import annotations

import os

from PySide6.QtCore import QSettings

# Named by the environment when it says so, and by the program otherwise.
# Every script that drives a real Planner writes into the player's own
# settings without this -- builds, favourites and artwork included -- so the
# order the smoke battery ran in mattered, and a test could overwrite work
# somebody had done in the game. Setting NIGHTREIGN_SETTINGS_APP in front of
# a run gives that run a store of its own without any script having to know
# it is being isolated. OPEN_QUESTIONS §21.8.
ORG = os.environ.get("NIGHTREIGN_SETTINGS_ORG") or "DankYeeter"
APP = os.environ.get("NIGHTREIGN_SETTINGS_APP") or "NightreignHelper"
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


def parts(roll: str) -> tuple[int, list[int], list[int]] | None:
    """A roll key read back: the relic id, its effects, its curses.

    The inverse of key(), and here because this is where the format is
    decided. A custom relic is why it exists: it is owned by nobody, so a
    stored build that names one has nothing to be looked up in and can only be
    rebuilt from the key itself (QA-025).

    None when the text is not a roll key -- an empty stored slot, or one
    written by a version that spelled it differently. The text comes out of
    the settings store, so it is checked rather than trusted.
    """
    fields = str(roll).split("|")
    if len(fields) != 3:
        return None
    try:
        relic_id = int(fields[0])
        effects = [int(e) for e in fields[1].split(",") if e]
        curses = [int(c) for c in fields[2].split(",") if c]
    except ValueError:
        return None
    return relic_id, effects, curses


def distinct(items) -> list:
    """One entry per roll, in the order given.

    Two copies with the same roll are interchangeable in a build, and the
    save can also carry stale duplicate records (HANDOVER §6k), so every
    place that lists or counts relics collapses on key(). The picker always
    did; the slot header did not, and the two disagreed by exactly the
    number of duplicate rolls -- "(50 owned)" over a picker saying
    "49 of 49". One function, so a count and a list can never differ again.
    """
    seen = set()
    out = []
    for item in items:
        k = key(item)
        if k in seen:
            continue
        seen.add(k)
        out.append(item)
    return out


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
