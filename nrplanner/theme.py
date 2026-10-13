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

SLOT_COLOURS = {
    0: "#b4544e",   # Red
    1: "#4e7ab4",   # Blue
    2: "#c2a24a",   # Yellow
    3: "#5c9e63",   # Green
    4: "#d8d8d8",   # White -- wildcard
}

#: How a card shows that the pointer is standing on it: the Nightlord grid
#: (QA-154), the relic cards and the armament tiles (QA-157). Measured on the
#: Nightlord grid, whose cards share PANEL with the other two.
#:
#: The finding is not the hit area. Measured on 2026-09-06 on Windows under
#: Fusion at 150 % scale, at a 1600x900 logical-px window: every one of 3 420
#: probe points, one every 4 logical px over the whole 302x178 card, opened
#: that card -- the labels inside it ignore a press and Qt hands it to the
#: frame. What is dead is the 8 logical px between two neighbours, and a
#: reader had no way to see which side of that line he was on: a near miss
#: opened the wrong Nightlord and a miss opened nothing, and the grid looked
#: identical in both cases.
#:
#: So the marker is on the pointer rather than on the click. A third channel
#: again: fill only, edge untouched. Selection changes both, an Everdark twin
#: owns DEEP on the edge, and hover changes the one thing neither of those
#: two moves -- so the three states stay apart at a glance.
#:
#: **The value is measured, not chosen by eye.** Sampled off a grab of the
#: whole window -- a card grabbed alone lands its translucent selection fill
#: on a transparent pixmap and reads back as the colour the stylesheet names
#: rather than the colour a reader sees -- on Windows under Fusion at 150 %
#: scale, at a 1600x900 logical-px window. An unmarked card is (30, 31, 35)
#: and a chosen one composites to (64, 57, 42), a WCAG contrast of 1.440.
#: The first hover fill tried here, `#26272c`, composited to (38, 39, 44):
#: **1.105**, a step small enough that the screenshot had to be measured to
#: tell whether the pointer was on the card at all. That is not feedback.
#: This one composites to (51, 52, 60) -- **1.331** against an unmarked card,
#: nearly the 1.440 the selection's own fill manages, while staying the only
#: neutral of the three: the selection is the one warm thing on this grid and
#: keeps its gold edge as well, so hover and selection are apart by hue and
#: by border even where their luminance is close.
#:
#: Cooler fills were measured too and reach further -- `#334055` gives 1.572
#: and `#3a4a60` 1.825 -- but both put a new hue on a tab where DEEP already
#: means something on the edge of a card. That is the `ui-ux-designer`'s call
#: to make with these figures, not this file's.
HOVER_FILL = "#33343c"
