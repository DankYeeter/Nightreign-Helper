"""The build advisor: what to put in a relic slot, and why (`GOAL.md` A3-A8).

A package rather than a module, and Qt-free rather than convenient (AD-001).
The whole calculation has to run without a display or it cannot be tested,
and an advisor that cannot be tested cannot be accepted (A9). The one file
that imports PySide6 is `worker.py`, and it holds the thread and nothing
else: what it runs is `run.run`, which knows nothing about threads.

The order the modules may depend on each other in is fixed (AD-001) and is
the order they are listed in:

    types      the shapes, and the lookups over them
    evaluate   the one door to `model.compute` (AD-014.1)
    candidates what may go into a slot, and what it is worth there
    goals      the named directions to optimise in
    search     the beam over the free slots
    explain    `Build.sources` turned into English
    run        one question answered whole, and the memo of the answer
    worker     the QThread, the debounce and the generation counter

`types` imports nothing from this package. `candidates` takes its goals as a
parameter rather than importing the registry, so the two below it stay
independent of each other.

Everything visible to the player from here is English (`GOAL.md` A8);
comments and docstrings are German or English as the rest of the project is.
"""

from __future__ import annotations

from .goals import DEFAULT_WEIGHTING, GOALS
from .types import (
    AdvisorRequest,
    AdvisorResult,
    Candidate,
    Goal,
    GoalContext,
    GoalScore,
    SlotPool,
    SlotProblem,
    Suggestion,
    Weighting,
)

__all__ = [
    "DEFAULT_WEIGHTING",
    "GOALS",
    "AdvisorRequest",
    "AdvisorResult",
    "Candidate",
    "Goal",
    "GoalContext",
    "GoalScore",
    "SlotPool",
    "SlotProblem",
    "Suggestion",
    "Weighting",
]
