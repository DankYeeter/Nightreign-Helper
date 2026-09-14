"""Which effects the player struck out of, or pinned into, every suggestion.

`GOAL.md` A18 gives the player *Don't include* per effect id, A19 *Must
include*; AD-036.5 puts both in the one settings store the program has,
under one fixed key each. The ids are the **value**, never the key
(AD-030, OF-15): nothing here derives a key from anything, and the key
space this adds is two, for good. No `__schema` step either -- a store that
never held the key reads back as empty, which is exactly what an older
program state means by it.

The two sets are disjoint by construction (AK-276: an effect is never
excluded and required at once). Marking an effect in one set takes it out
of the other, so the window never has to ask which state it is leaving.

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


def store(kind: str, ids: Iterable[int]) -> None:
    _settings().setValue(KEYS[kind], ",".join(str(i) for i in sorted(ids)))


class EffectFilters(QObject):
    """The two sets as the window holds them, written through on every change.

    `changed` fires after the store is written, once per marking that moved
    anything. The advisor row hears it the way it hears a goal change
    (AK-183): the answer goes, a run in flight says AK-289, none starts.
    """

    changed = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.excluded = stored(EXCLUDED)
        self.required = stored(REQUIRED)

    def mark(self, effect_id: int, kind: str | None) -> None:
        """Put one effect into the `kind` set, or into neither for `None`."""
        if kind not in (EXCLUDED, REQUIRED, None):
            raise ValueError(f"no effect filter is called {kind!r}")
        excluded = self.excluded - {effect_id}
        required = self.required - {effect_id}
        if kind == EXCLUDED:
            excluded |= {effect_id}
        elif kind == REQUIRED:
            required |= {effect_id}
        if (excluded, required) == (self.excluded, self.required):
            return
        self.excluded, self.required = excluded, required
        store(EXCLUDED, excluded)
        store(REQUIRED, required)
        self.changed.emit()
