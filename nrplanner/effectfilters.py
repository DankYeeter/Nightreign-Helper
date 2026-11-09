"""Which effects the player struck out of, or pinned into, every suggestion.

`GOAL.md` A18 gives the player *Avoid* per effect id, A19 *Favourite*
(AK-300), A23 *Avoid* per family with *Allow* per member (AD-039); AD-036.5
puts all of it in the one settings store the program has, under one fixed
key each. The ids and family names are the **value**, never the key
(AD-030, OF-15): nothing here derives a key from anything, and the key
space is five per Nightfarer (`key_for`, user 2026-11-08), plus the five
shared keys of older versions, which a Nightfarer reads until it has its own. No `__schema` step either -- a store that
never held a key reads back as empty, which is exactly what an older
program state means by it.

The fifth key is no marking: `stacks` says how many stacks the advisor's
questions, Optimize's and the relic picker's, count for a stack effect
(`model.accumulates`, user decision 2026-11-07), over whatever the stat sheet
says, and it touches none of the sets below.

The three id sets are disjoint by construction (AK-276: an effect is never
excluded and required at once, and `Allow` is a third state of the same
kind). Marking an effect in one set takes it out of the others, so the
window never has to ask which state it is leaving. The store is not trusted
to agree: a process that ended between two writes, or a hand in the
registry, can leave one id under two keys, and a pair that reached
`SlotProblem` stopped the advisor at every start (QA-267/SEC-045). Loading
therefore makes the sets disjoint -- `required` wins, then `allowed`
(Director, 2026-09-14; AD-039.4) -- and writes the repair back; a marking
writes all four keys through one `QSettings` with one `sync()`, so the gap
is as small as the store allows.

What the advisor is handed is one resolved set (AD-039.3): the ids marked
`Avoid` and every id whose family is avoided, less the ids on `Allow` and
the ids on `Favourite` -- Favourite wins over a family, so `SlotProblem`
never sees an id in both of its sets. Resolved over every id of the
dataset, not the owned ones: a relic of an avoided family found tomorrow is
avoided too.

An id the dataset has since lost, or a family name it no longer forms,
stays stored and travels with the problem; it meets nothing and costs
nothing.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from PySide6.QtCore import QObject, Signal

from . import favourites, model

EXCLUDED = "excluded"
REQUIRED = "required"
ALLOWED = "allowed"
AVOIDED_FAMILIES = "avoided_families"
STACKS = "stacks"
KEYS = {EXCLUDED: "advisor/excluded", REQUIRED: "advisor/required",
        ALLOWED: "advisor/allowed",
        AVOIDED_FAMILIES: "advisor/avoided_families",
        STACKS: "advisor/stacks"}

#: Family names are stored one per line: a comma is part of some of them
#: (`Improved Mind and Faith, Reduced Intelligence`), a line break of none
#: (`effecttext.name` folds it).
FAMILY_SEPARATOR = "\n"

#: For the effect with no ceiling in the game's scripts (`model.STACK_LIMITS`),
#: and so not a fact about the game: `model.compute` expands one copy per stack,
#: so Optimize slows with the value
#: (QA-336, user decision 2026-11-07). Measured 2026-11-07 on the A6 case, offscreen:
#: 2.5 s at 10 against 14.2 s at 99, with the budget at 6 s.
MOST_STACKS = 10


def key_for(kind: str, hero_id: int | None = None) -> str:
    """The store key of one set for one Nightfarer (user 2026-11-08: "pro
    charakter"), `advisor/<hero id>/<set>`; the old shared key for `None`.
    A Nightfarer whose own key was never written reads the shared one, so
    the markings made before this change start out on every Nightfarer."""
    if hero_id is None:
        return KEYS[kind]
    return f"advisor/{int(hero_id)}/{kind}"


def _raw(kind: str, hero_id: int | None) -> str:
    settings = favourites.settings()
    own = key_for(kind, hero_id)
    if hero_id is not None and not settings.contains(own):
        own = KEYS[kind]
    return str(settings.value(own, "", type=str))


def stored(kind: str, hero_id: int | None = None) -> frozenset[int]:
    """The ids under this key. Anything that is not an integer is skipped,
    so a damaged value reads as empty and never as an error.

    `type=str` for the reason `gamepath._remembered` gives: a file-backed
    store hands back a *list* as soon as the text holds a comma, and this
    text is nothing but commas.
    """
    raw = _raw(kind, hero_id)
    ids = set()
    for part in str(raw).split(","):
        try:
            ids.add(int(part))
        except ValueError:
            continue
    return frozenset(ids)


def stored_text(kind: str, hero_id: int | None = None) -> frozenset[str]:
    """The family names under this key, one per line; blank lines and the
    whitespace around a name (a stray `\\r` included) fall away."""
    raw = _raw(kind, hero_id)
    return frozenset(part.strip() for part in str(raw).split(FAMILY_SEPARATOR)
                     if part.strip())


def stack_limit(effect_id: int) -> int:
    """The largest value the Stacks field takes for this effect."""
    return model.stack_limit(effect_id, MOST_STACKS)


def stack_count(text: str, effect_id: int) -> int | None:
    """The count this text says, or `None` for anything but a whole number
    from 0 to this effect's limit in plain digits (`int` would read other
    scripts, and raise on five thousand of them, so the length comes first)."""
    if text.isascii() and text.isdigit() and len(text) <= len(str(MOST_STACKS)):
        count = int(text)
        return count if count <= stack_limit(effect_id) else None
    return None


def stored_stacks(hero_id: int | None = None) -> dict[int, int]:
    """Effect id -> stacks, stored as `id=count,id=count`. A part that does not
    read as an id and a count in that effect's range is skipped, as in `stored`:
    a value saved under an older, wider limit reads as empty (AK-470)."""
    raw = _raw(STACKS, hero_id)
    stacks = {}
    for part in str(raw).split(","):
        effect_id, _, text = part.partition("=")
        try:
            effect_id = int(effect_id)
        except ValueError:
            continue
        count = stack_count(text, effect_id)
        if count is not None:
            stacks[effect_id] = count
    return stacks


def store(excluded: Iterable[int], required: Iterable[int],
          allowed: Iterable[int], avoided_families: Iterable[str],
          hero_id: int | None = None) -> None:
    """All four keys, through one store object and one `sync()`."""
    settings = favourites.settings()
    for kind, ids in ((EXCLUDED, excluded), (REQUIRED, required),
                      (ALLOWED, allowed)):
        settings.setValue(key_for(kind, hero_id),
                          ",".join(str(i) for i in sorted(ids)))
    settings.setValue(key_for(AVOIDED_FAMILIES, hero_id),
                      FAMILY_SEPARATOR.join(sorted(avoided_families)))
    settings.sync()


class EffectFilters(QObject):
    """The sets as the window holds them, written through on every change.

    `families` maps every effect id of the dataset to its family key
    (`effecttext.family_key`); it is what `resolved_excluded` resolves an
    avoided family against. `changed` fires after the store is written,
    once per marking that moved anything. The advisor row hears it the way
    it hears a goal change (AK-183): the answer goes, a run in flight says
    AK-289, none starts.
    """

    changed = Signal()

    def __init__(self, parent: QObject | None = None,
                 families: Mapping[int, str] | None = None,
                 hero_id: int | None = None) -> None:
        super().__init__(parent)
        self.families: Mapping[int, str] = dict(families or {})
        self._load(hero_id)

    def _load(self, hero_id: int | None) -> None:
        self.hero_id = hero_id
        self.required = stored(REQUIRED, hero_id)
        as_stored = (stored(EXCLUDED, hero_id), stored(ALLOWED, hero_id))
        self.allowed = as_stored[1] - self.required
        self.excluded = as_stored[0] - self.required - self.allowed
        self.avoided_families = stored_text(AVOIDED_FAMILIES, hero_id)
        self.stacks = stored_stacks(hero_id)
        if (self.excluded, self.allowed) != as_stored:
            store(self.excluded, self.required, self.allowed,
                  self.avoided_families, hero_id)
        self._resolve()

    def set_hero(self, hero_id: int | None) -> None:
        """Load the markings of this Nightfarer; every set is its own."""
        if hero_id == self.hero_id:
            return
        before = (self.excluded, self.required, self.allowed,
                  self.avoided_families, self.stacks)
        self._load(hero_id)
        if before != (self.excluded, self.required, self.allowed,
                      self.avoided_families, self.stacks):
            self.changed.emit()

    def mark(self, effect_id: int, kind: str | None) -> None:
        """Put one effect into the `kind` set, or into none for `None`."""
        sets = {name: getattr(self, name) - {effect_id}
                for name in (EXCLUDED, REQUIRED, ALLOWED)}
        if kind in sets:
            sets[kind] |= {effect_id}
        self._apply(sets[EXCLUDED], sets[REQUIRED], sets[ALLOWED],
                    self.avoided_families)

    def mark_family(self, key: str, avoided: bool) -> None:
        """Avoid, or stop avoiding, every effect of one family."""
        families = (self.avoided_families | {key} if avoided
                    else self.avoided_families - {key})
        self._apply(self.excluded, self.required, self.allowed, families)

    def set_stacks(self, effect_id: int, count: int | None) -> None:
        """How many stacks the advisor's questions count for this effect;
        `None` leaves it to the stat sheet, 0 does not count it."""
        stacks = {**self.stacks, effect_id: count}
        if count is None:
            del stacks[effect_id]
        if stacks == self.stacks:
            return
        self.stacks = stacks
        settings = favourites.settings()
        settings.setValue(key_for(STACKS, self.hero_id), ",".join(
            f"{i}={stacks[i]}" for i in sorted(stacks)))
        settings.sync()
        self.changed.emit()

    def counted_stacks(self, effects: Mapping[str, dict]) -> dict[int, int]:
        """The values a question uses. The store is not trusted to hold stack
        effects alone: `model.compute` would count any other condition that
        many times, and an id the dataset lost is nothing to count."""
        return {effect_id: count for effect_id, count in self.stacks.items()
                if model.accumulates(effects.get(str(effect_id)) or {})}

    def _apply(self, excluded, required, allowed, avoided_families) -> None:
        after = (excluded, required, allowed, avoided_families)
        if after == (self.excluded, self.required, self.allowed,
                     self.avoided_families):
            return
        (self.excluded, self.required, self.allowed,
         self.avoided_families) = after
        store(*after, hero_id=self.hero_id)
        self._resolve()
        self.changed.emit()

    def _resolve(self) -> None:
        by_family = {effect_id for effect_id, key in self.families.items()
                     if key in self.avoided_families}
        #: AD-039.3: what `SlotProblem.excluded` is handed.
        self.resolved_excluded: frozenset[int] = frozenset(
            (self.excluded | by_family) - self.allowed - self.required)
