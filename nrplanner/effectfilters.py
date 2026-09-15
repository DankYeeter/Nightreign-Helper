"""Which effects the player struck out of, or pinned into, every suggestion.

`GOAL.md` A18 gives the player *Avoid* per effect id, A19 *Favourite*
(AK-300); AD-036.5 puts both in the one settings store the program has,
under one fixed key each. The ids are the **value**, never the key
(AD-030, OF-15): nothing here derives a key from anything, and the key
space this adds is two, for good. No `__schema` step either -- a store that
never held the key reads back as empty, which is exactly what an older
program state means by it.

The two sets are disjoint by construction (AK-276: an effect is never
excluded and required at once). Marking an effect in one set takes it out
of the other, so the window never has to ask which state it is leaving. The
store is not trusted to agree: a process that ended between two writes, or
a hand in the registry, can leave one id under both keys, and a pair that
reached `SlotProblem` stopped the advisor at every start (QA-267/SEC-045).
Loading therefore makes the two disjoint -- `required` wins (Director,
2026-09-14) -- and writes the repair back; a marking writes both keys
through one `QSettings` with one `sync()`, so the gap is as small as the
store allows.

An id the dataset has since lost stays stored and travels with the
problem; it meets nothing and costs nothing.
"""

from __future__ import annotations

from collections.abc import Iterable

from PySide6.QtCore import QObject, QSettings, Signal

from . import favourites

EXCLUDED = "excluded"
REQUIRED = "required"
KEYS = {EXCLUDED: "advisor/excluded", REQUIRED: "advisor/required"}


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


def store(excluded: Iterable[int], required: Iterable[int]) -> None:
    """Both sets, through one store object and one `sync()`."""
    settings = _settings()
    for kind, ids in ((EXCLUDED, excluded), (REQUIRED, required)):
        settings.setValue(KEYS[kind], ",".join(str(i) for i in sorted(ids)))
    settings.sync()


class EffectFilters(QObject):
    """The two sets as the window holds them, written through on every change.

    `changed` fires after the store is written, once per marking that moved
    anything. The advisor row hears it the way it hears a goal change
    (AK-183): the answer goes, a run in flight says AK-289, none starts.
    """

    changed = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.required = stored(REQUIRED)
        as_stored = stored(EXCLUDED)
        self.excluded = as_stored - self.required
        if self.excluded != as_stored:
            store(self.excluded, self.required)

    def mark(self, effect_id: int, kind: str | None) -> None:
        """Put one effect into the `kind` set, or into neither for `None`."""
        excluded = self.excluded - {effect_id}
        required = self.required - {effect_id}
        if kind == EXCLUDED:
            excluded |= {effect_id}
        elif kind == REQUIRED:
            required |= {effect_id}
        if (excluded, required) == (self.excluded, self.required):
            return
        self.excluded, self.required = excluded, required
        store(excluded, required)
        self.changed.emit()
