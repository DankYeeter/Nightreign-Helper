"""Which effects the player struck out of, or pinned into, every suggestion.

`GOAL.md` A18 gives the player *Avoid* per effect id, A19 *Favourite*
(AK-300), A23 *Avoid* per family with *Allow* per member (AD-039); AD-036.5
puts all of it in the one settings store the program has, under one fixed
key each. The ids and family names are the **value**, never the key
(AD-030, OF-15): nothing here derives a key from anything, and the key
space this adds is four, for good. No `__schema` step either -- a store that
never held a key reads back as empty, which is exactly what an older
program state means by it.

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

from PySide6.QtCore import QObject, QSettings, Signal

from . import favourites

EXCLUDED = "excluded"
REQUIRED = "required"
ALLOWED = "allowed"
AVOIDED_FAMILIES = "avoided_families"
KEYS = {EXCLUDED: "advisor/excluded", REQUIRED: "advisor/required",
        ALLOWED: "advisor/allowed",
        AVOIDED_FAMILIES: "advisor/avoided_families"}

#: Family names are stored one per line: a comma is part of some of them
#: (`Improved Mind and Faith, Reduced Intelligence`), a line break of none
#: (`effecttext.name` folds it).
FAMILY_SEPARATOR = "\n"


def _settings() -> QSettings:
    return QSettings(favourites.ORG, favourites.APP)


def stored(kind: str) -> frozenset[int]:
    """The ids under this key. Anything that is not an integer is skipped,
    so a damaged value reads as empty and never as an error.

    `type=str` for the reason `gamepath._remembered` gives: a file-backed
    store hands back a *list* as soon as the text holds a comma, and this
    text is nothing but commas.
    """
    raw = _settings().value(KEYS[kind], "", type=str)
    ids = set()
    for part in str(raw).split(","):
        try:
            ids.add(int(part))
        except ValueError:
            continue
    return frozenset(ids)


def stored_text(kind: str) -> frozenset[str]:
    """The family names under this key, one per line; blank lines and the
    whitespace around a name (a stray `\\r` included) fall away."""
    raw = _settings().value(KEYS[kind], "", type=str)
    return frozenset(part.strip() for part in str(raw).split(FAMILY_SEPARATOR)
                     if part.strip())


def store(excluded: Iterable[int], required: Iterable[int],
          allowed: Iterable[int], avoided_families: Iterable[str]) -> None:
    """All four keys, through one store object and one `sync()`."""
    settings = _settings()
    for kind, ids in ((EXCLUDED, excluded), (REQUIRED, required),
                      (ALLOWED, allowed)):
        settings.setValue(KEYS[kind], ",".join(str(i) for i in sorted(ids)))
    settings.setValue(KEYS[AVOIDED_FAMILIES],
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
                 families: Mapping[int, str] | None = None) -> None:
        super().__init__(parent)
        self.families: Mapping[int, str] = dict(families or {})
        self.required = stored(REQUIRED)
        as_stored = (stored(EXCLUDED), stored(ALLOWED))
        self.allowed = as_stored[1] - self.required
        self.excluded = as_stored[0] - self.required - self.allowed
        self.avoided_families = stored_text(AVOIDED_FAMILIES)
        if (self.excluded, self.allowed) != as_stored:
            store(self.excluded, self.required, self.allowed,
                  self.avoided_families)
        self._resolve()

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

    def _apply(self, excluded, required, allowed, avoided_families) -> None:
        after = (excluded, required, allowed, avoided_families)
        if after == (self.excluded, self.required, self.allowed,
                     self.avoided_families):
            return
        (self.excluded, self.required, self.allowed,
         self.avoided_families) = after
        store(*after)
        self._resolve()
        self.changed.emit()

    def _resolve(self) -> None:
        by_family = {effect_id for effect_id, key in self.families.items()
                     if key in self.avoided_families}
        #: AD-039.3: what `SlotProblem.excluded` is handed.
        self.resolved_excluded: frozenset[int] = frozenset(
            (self.excluded | by_family) - self.allowed - self.required)
