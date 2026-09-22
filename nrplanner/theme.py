"""The colours more than one part of the window uses, under one name each.

A colour only one module uses stays in that module, next to what it paints.
"""

from __future__ import annotations

#: The gold the whole window uses for a section title.
ACCENT = "#c8a45c"
#: The grey for text that explains rather than states.
MUTED = "#8a8a8a"
PANEL = "#1e1f23"
BORDER = "#2e2f35"
GOOD = "#6fbf73"
BAD = "#d1655f"
#: Curses are a cost, and read in the same colour as one.
CURSE = BAD
#: A rolled curse or cost in a list or table cell; lighter than BAD so it
#: stays readable at cell size.
DEBUFF = "#e07a74"
DEEP = "#9a6fc4"
#: What players have reported rather than what the game files state.
COMMUNITY = "#7fb2e5"

SLOT_COLOURS = {
    0: "#b4544e",   # Red
    1: "#4e7ab4",   # Blue
    2: "#c2a24a",   # Yellow
    3: "#5c9e63",   # Green
    4: "#d8d8d8",   # White -- wildcard
}
