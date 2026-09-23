"""The Nightlords: what each one takes, what breaks it, and how it buffs itself.

The resistance figures this file once said were unreachable are here now --
`nrdata/bossdata.py` links the boss menu to an NpcParam row through the event
script and the map, and `nrdata/tae.py` says which animation applies a boss's
buff.

Each Nightlord is one entry, carrying its Everdark twin rather than appearing
twice. That is safe because the two are the same character with identical
figures; see `merge_everdark`.
"""

from __future__ import annotations

import functools
import html
import pathlib

from PySide6.QtCore import QSignalBlocker, Qt, Signal
from PySide6.QtGui import (
    QAccessible, QAccessibleActionInterface, QColor, QCursor, QFont, QPainter,
    QPainterPath, QPen, QPixmap,
)
from PySide6.QtWidgets import (
    QAbstractScrollArea, QAccessibleWidget, QApplication, QFrame, QHBoxLayout,
    QHeaderView, QLabel, QScrollArea, QSizePolicy, QStyle,
    QStyleOptionFocusRect, QToolButton, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget,
)

from . import cardgrid, relicslots, tabheader
from .theme import ACCENT, BAD, BORDER, DEEP, GOOD, MUTED, PANEL

# Watched in play: above a wiki claim, below a param read.
OBSERVED_COLOUR = "#7fae72"

ICON = 64
CARD_WIDTH = 250

#: How the grid shows which card the detail panel is describing (QA-150).
#: Two channels rather than one, because the edge colour is already spoken
#: for: a Nightlord with an Everdark twin carries DEEP there, and a selection
#: that only swapped one edge colour for another would be a single hue apart
#: from the twin marker. The fill is a channel no other marker on this grid
#: uses, and it is the tint the Red variants table already selects rows with,
#: so the two tabs say "this one" the same way (A13).
SELECTED_EDGE = ACCENT
SELECTED_FILL = "rgba(200, 164, 92, 60)"

#: How the grid shows which card the pointer is standing on (QA-154).
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

#: What the detail panel is given where there is room for it, and the least it
#: is ever given. `setFixedWidth(330)` was one figure doing both jobs, so at
#: an 833 px window the panel held 330 px of `Select a Nightlord` while the
#: ten cards it describes stood one to a row in the 463 px left over
#: (QA-147). The floor is a card's width: under that the damage bars and their
#: labels stop lining up.
DETAIL_WIDTH = 330
DETAIL_FLOOR = CARD_WIDTH

#: At most one part panel to two parts cards. The panel describes one of the
#: cards beside it, so where there is not room for both it is the panel that
#: gives way; where there is, it keeps DETAIL_WIDTH and every further pixel
#: goes to the grid, because a wider window should mean more Nightlords on
#: screen and not a roomier column of text. Measured on Windows at 150 % scale
#: under Fusion: at an 833 px window the panel goes from 330 px to 276 and the
#: cards from 463 to 517; from 1067 px up nothing moves.
DETAIL_SHARE = 3

#: What the portrait is given on a Nightlord's panel. A sub-boss carries no
#: artwork at all (AD-041), so its panel gives the label nothing rather than
#: opening with an empty block of this height (AK-321.3).
DETAIL_ART_HEIGHT = 180

#: The three groups of the sub-boss tree, in the order AK-319 fixes them, and
#: the day each one asks a card about. `None` is the field-boss group: a card
#: the night lottery never draws.
TREE_GROUPS = (
    (1, "NIGHT BOSSES  ·  DAY 1"),
    (2, "NIGHT BOSSES  ·  DAY 2"),
    (None, "FIELD BOSSES"),
)

TREE_HEADERS = ("Boss", "Share of patterns")

#: AK-319.3. The same honesty the World Events tab already puts on its own
#: percentage (`eventstab`), carried over to this column rather than restated
#: as a new idea: a share of a pool that is drawn with weights is not a
#: chance per run.
SHARE_TIP = (
    "How much of the selected Nightlord's own map-pattern pool includes this "
    "card. The pool is drawn with weights, so this is not the chance of "
    "seeing it on a given run.")

#: AK-320. The tree answers the same question the empty panel does, and in
#: the same voice, rather than sitting there blank.
NO_NIGHTLORD_YET = ("Select a Nightlord above to see which field and night "
                    "bosses can appear for it.")

#: The two confidences that come with a name out of the files (AD-040).
NAMED = ("single", "group")

#: AK-322.3. What a card is called where the files do not name its boss. The
#: same words in the tree and at the head of the panel, because they are the
#: same claim -- and two different words, because "we cannot pick between
#: these" and "we do not know who this is" are not the same failure.
AMBIGUOUS_NAME = "Multiple possible bosses"
UNRESOLVED_NAME = "Not identified"

#: What the panel says where the files leave a fight underivable -- for a
#: Nightlord whose weakness cannot be worked out, and, word for word, for a
#: card whose boss the files never identify (AK-322.4).
NOT_DERIVABLE = "Not derivable for this fight."

#: AK-324.3. How many drops stand open before the toggle takes over.
LOOT_OPEN = 5
NO_LOOT = "no loot recorded in the files"
LOOT_NOTE = (
    "Percentages are the game's own drop tables. A few point at tables this "
    "program cannot read, so on some bosses they do not add up to 100% — "
    "nothing is hidden, the shortfall is missing data.")

#: What this tab is for, in the reader's own words (AK-68, AK-89). Above the
#: count and above the cards, because a player arrives with the question and
#: not with the roster.
HEADING = "HOW TO HURT EACH NIGHTLORD"
QUESTION = (
    "What each Nightlord takes extra damage from, what breaks its stance, "
    "and what it does to you once it is broken. Click a card for the full "
    "profile.")

# What body part a numbered slot actually is, once someone has watched it.
#
# The files will not say. `partsDamageRate1..8` and `isWeakA..F` carry no
# description in the paramdef, and the AI scripts only ever number parts
# (`ANIME_ID_PART1_DAMAGE`), so anything anatomical here has to come from
# play. Keyed by (boss name, the label the extractor produced).
#
# There is a clean way to fill this in: a weak-part hit plays its own
# reaction, so hitting each part in turn and watching for it identifies the
# slot. Add entries only from an actual sighting -- a guess here would read
# exactly like a fact.
PART_NAMES: dict[tuple[str, str], str] = {}

# Bosses seen to take the attack-down / defence-down debuff when broken. Not
# all of them do -- Gnoster shows nothing at all -- and the files never say
# who gets it, so this is a sighting list. Showing the line for every boss
# would put a flat lie on the page.
#
# The two figures this list used to print with -- "x2.0 damage taken" and
# "x0.8 attack power" -- are gone (QA-129). They were typed in here, and the
# dataset neither confirms nor places them: `x2.0 damage taken` has no
# counterpart anywhere in it, and the one field that is an attack-power
# multiplier for a boss, `ladder.down`, says 0.815 for Gladius and nothing at
# all for the other two names below, while saying exactly 0.8 for Harmonia and
# Straghess, who are not on this list. Whether the two describe one mechanism
# cannot be decided from the files, so the sighting is kept as a sighting -- it
# says what was watched and admits that the size of it is not in the data (A7).
DEBUFF_ON_BREAK = {"Gladius", "Heolstor the Nightlord", "Caligo"}

# The sighting itself, without a magnitude. Shown in OBSERVED_COLOUR (AK-94),
# so a reader can see at a glance that this line was watched rather than read.
DEBUFF_ON_BREAK_SIGHTING = (
    "Watched in play: breaking its stance leaves it weakened for a time — a "
    "golden shine, with damage-down and defence-down icons on its health bar. "
    "The files do not say by how much.")

# What OBSERVED_COLOUR means, said once on the panel that uses it (AK-74,
# QA-145). It sat one step from GOOD -- 0x7f against 0x6f in the red channel
# alone -- with nothing anywhere saying the two were different things. Drawn
# in the colour it explains.
#
# It says what the colour means and stops there. "Everything else is the
# game's own data" would not be true on this panel -- `Set off by` and the
# trigger clause of a defence step are sightings drawn in the ordinary colour
# (AK-94, reported to the director rather than changed here). A legend that claimed it would be the
# one false sentence on the panel.
SIGHTING_LEGEND = (
    "Lines in this colour were watched in play rather than read from the "
    "game's files.")

# The reference each block of figures is measured against (A12, AK-91's
# pattern). Three sections carried one and three did not, which made the
# missing ones read as an oversight rather than as "nothing to say" (QA-149).
#
# `IT BUFFS ITSELF` holds two kinds of line and they differ in exactly the
# point a reader would have to guess, so one note covers both and separates
# them.
BUFF_NOTE = (
    "Buff steps multiply this Nightlord's own attack and stance figures while "
    "the step is on; the files give no duration for them, and `always on` "
    "means no trigger is recorded. Defence steps carry their own duration.")

# The green on `Weakened` is the third meaning GOOD carries on this panel and
# the one AK-91 does not name (QA-145); the sentence that already stood here
# gains the clause, rather than a fourth note appearing beside it.
WEAKENED_NOTE = (
    "A step the game's own data gives this Nightlord: while it is on, these "
    "multiply its normal figures — green, because every one of them is in "
    "your favour. The files do not say what puts it into the step.")

PARTS_NOTE = (
    "Damage dealt to that part, against the same hit anywhere else on this "
    "Nightlord. The files number the parts and never say which part is which, "
    "so a number here is worth more than the name beside it.")

# What sets a boss's self-buff off. The files give the animation id and never
# what provokes it, so these are sightings. Only bosses actually watched are
# listed; the rest show the buff with no trigger claimed.
# What sets a defence buff off, keyed by the exact effect rather than the
# boss: Libra has two and only one of them is the bubble. Keying by boss would
# have put the bubble note against both.
DEFENCE_TRIGGER = {
    ("Libra", 45852): ("finishing the bubble cast — pop the bubble and it "
                       "never lands"),
}

BUFF_TRIGGER = {
    "Gladius": ("during the taunt walk, which only happens once he has merged "
                "into one body — every attack he takes during it adds a stack"),
    "Adel": "when he bites and inflicts blood loss",
    "Libra": "after a madness proc",
    "Straghess": "seemingly tied to how many adds are alive — least certain",
}

# Caveats on the weakness interaction itself, from play. Only the three that
# change how you use the weakness are kept -- the rest of what was recorded
# here is now implied by the panel's own structure: a boss with no debuff rows
# is a boss that does not take the debuff, and the Tell row says what to watch
# for on the ones that do.
WEAKNESS_NOTE = {
    "Gladius": ("While he is split into hounds, each one takes the debuff "
                "separately."),
    "Adel": ("Phase 1 only — the poison stagger is gone in phase 2 and in the "
             "Everdark version."),
    "Fulghor": ("Lightning during his charged attack knocks him out of the "
                "charge, and the attack then lands with none of it."),
}


def has_card_name(entry: dict) -> bool:
    """Does this card come with a name out of the files?

    Confidence and name are two separate questions and the tab has met cards
    where they disagree: a card can resolve to one character with a full
    profile and still carry `""`, because the game holds no NpcName for that
    row. The placeholder covers that too -- a blank row and a blank panel
    heading would read as a fault in this program rather than as the gap in
    the files that it is (A7).
    """
    return bool(entry["name"]) and (
        (entry.get("weakness") or {}).get("confidence") in NAMED)


def card_name(entry: dict) -> str:
    """What a sub-boss card is called, name or placeholder (AK-322.3).

    One function for the tree row and the panel heading: they are the same
    claim about the same card, and two copies of this rule would be two
    chances for a card to be named in one place and not in the other.
    """
    if has_card_name(entry):
        return entry["name"]
    confidence = (entry.get("weakness") or {}).get("confidence")
    return AMBIGUOUS_NAME if confidence == "ambiguous" else UNRESOLVED_NAME


def card_role(days: list[int]) -> str:
    """The line under the name: what this card is, not how it was opened.

    AK-322.1. A card the night lottery draws on both days says so whichever
    of the two tree groups the reader came in through -- the sentence
    describes the card.
    """
    if not days:
        return "Field boss"
    if 1 in days and 2 in days:
        return "Night boss  ·  Day 1 & 2"
    return f"Night boss  ·  Day {days[0]}"


def _tree_order(entry: dict):
    """Named cards alphabetically, the unnamed ones after them by card id.

    AK-319.4: scattered among the names, a placeholder reads as a name that
    failed to render rather than as the answer it is.
    """
    if has_card_name(entry):
        return (0, entry["name"])
    return (1, entry["map"])


def _group_font() -> QFont:
    """A tree group heading in the same voice as a panel heading (AK-319.1).

    The figures the `_section` divs carry, so the tree and the panel beside
    it read as one language rather than as two lists that happen to be on
    the same tab.
    """
    font = QFont()
    font.setPixelSize(10)
    font.setBold(True)
    font.setLetterSpacing(QFont.AbsoluteSpacing, 1)
    return font


def merge_everdark(bosses: list[dict]) -> list[dict]:
    """One entry per Nightlord, carrying its Everdark twin rather than
    repeating it.

    The two are the same character -- Gladius Everdark still resolves to
    c7500 -- and every extracted figure is identical between them, so two
    rows said the same thing twice. Straghess and Heolstor ship no Everdark
    version and pass through untouched.

    Merging here rather than in the snapshot keeps `nightreign_data.json`
    a plain record of what the files say; the pairing is a presentation
    choice and belongs on this side of the line.
    """
    everdark = {b["name"]: b for b in bosses if b.get("is_everdark")}
    out = []
    for boss in bosses:
        if boss.get("is_everdark"):
            continue
        merged = dict(boss)
        merged["everdark"] = everdark.get(boss["name"])
        out.append(merged)
    return out


def _split_circle(regular, sovereign, size: int):
    """One circle, halved on the top-left/bottom-right diagonal.

    Regular art fills the lower-left triangle and the Everdark art the
    upper-right, so a glance at the list says whether a boss has a Sovereign
    version at all. Same footprint as the plain badge it replaces.
    """
    canvas = QPixmap(size, size)
    canvas.fill(Qt.transparent)
    painter = QPainter(canvas)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.SmoothPixmapTransform)

    circle = QPainterPath()
    circle.addEllipse(0, 0, size, size)
    painter.setClipPath(circle)

    def half(pixmap, points):
        if pixmap is None:
            return
        painter.save()
        wedge = QPainterPath()
        wedge.moveTo(*points[0])
        for point in points[1:]:
            wedge.lineTo(*point)
        wedge.closeSubpath()
        painter.setClipPath(wedge, Qt.IntersectClip)
        scaled = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding,
                               Qt.SmoothTransformation)
        # Centre the crop, or the art drifts left on a non-square source.
        painter.drawPixmap(-(scaled.width() - size) // 2,
                           -(scaled.height() - size) // 2, scaled)
        painter.restore()

    half(regular, [(0, 0), (0, size), (size, size)])
    half(sovereign, [(0, 0), (size, 0), (size, size)])

    if regular is not None and sovereign is not None:
        pen = QPen(QColor(BORDER))
        pen.setWidthF(max(1.0, size / 48))
        painter.setPen(pen)
        painter.drawLine(0, 0, size, size)
    painter.end()
    return canvas


#: The keys that press a card. Return and Enter are the same gesture on two
#: keyboards; Space is what a button answers to everywhere else in Windows,
#: and a card that reads as a button to an assistive tool has to keep that
#: promise.
PRESS_KEYS = (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space)


class CardAccessible(QAccessibleWidget):
    """A card as an assistive tool sees it: a button that can be pressed.

    QA-161: a plain `QFrame` reports `Role.Border` -- furniture, not a
    control -- and has no Press action, so Qt's UIA bridge answered `Invoke`
    with `INVOKE_OK` and did nothing. The role matters as much as the action:
    a reader looking for something to activate passes over furniture even
    once the action is there.
    """

    def __init__(self, widget: BossCard):
        super().__init__(widget, QAccessible.Button)

    def actionNames(self) -> list[str]:  # noqa: N802 - Qt naming
        """Press first, then whatever `QAccessibleWidget` already offers.

        First because Qt's Windows bridge takes the *first* name as the one
        `InvokePattern` invokes; behind it stays `SetFocus`, which is how a
        client moves the keyboard to the card without pressing it.
        """
        return [QAccessibleActionInterface.pressAction(), *super().actionNames()]

    def doAction(self, name: str) -> None:  # noqa: N802 - Qt naming
        if name == QAccessibleActionInterface.pressAction():
            self.widget().press()
            return
        super().doAction(name)

    def keyBindingsForAction(self, name: str) -> list[str]:  # noqa: N802
        """What a reader can type to do this without a pointer.

        Announced rather than merely working: a screen reader reads this list
        out, and a key that works but is never named is a key nobody presses.
        """
        if name == QAccessibleActionInterface.pressAction():
            return ["Enter", "Space"]
        return super().keyBindingsForAction(name)


def _accessible_for(_key: str, obj) -> QAccessible:
    return CardAccessible(obj) if isinstance(obj, BossCard) else None


@functools.cache
def _install_factory() -> None:
    """Register `CardAccessible` with Qt, once per process.

    Called from the card's constructor rather than from `main`, because a
    factory that some entry point has to remember to install is a factory
    that is missing wherever somebody forgot -- and the symptom would be
    exactly QA-161 again: a card that looks right and does nothing.
    """
    QAccessible.installFactory(_accessible_for)


class BossCard(QFrame):
    """One expedition: its icon, the boss it ends on, and the flavour text.

    The card answers to more than a mouse (QA-161): it carries the Nightlord's
    name for an assistive tool to find it by, stands in the tab order, and
    answers Enter, Space and the accessibility interface's Press on the same
    call a click makes -- `press()`. The tab stop, the keys, the focus
    rectangle and the accessible role are settled together here, because the
    finding was not that the card lacked one of them but all four.
    """

    clicked = Signal(dict)

    def __init__(self, boss: dict, icons):
        super().__init__()
        _install_factory()
        # StrongFocus and not TabFocus: a card that answers to a press is a
        # button, and a button takes the keyboard when it is clicked. A
        # reader who clicks a card and then reaches for Tab expects to move on
        # from there and not from wherever the focus happened to be left.
        self.setFocusPolicy(Qt.StrongFocus)
        # The name is the Nightlord's, because that is what a reader is
        # looking for; the expedition goes in the description, which is the
        # second line a screen reader says and the answer to "which of the
        # ten is this".
        self.setAccessibleName(boss["name"])
        self.setAccessibleDescription(boss["expedition"])
        self.boss = boss
        # A minimum rather than a fixed width: the columns share the grid's
        # width, so cards grow to fill it instead of leaving a dead strip on
        # the right of a wide window.
        self.setMinimumWidth(CARD_WIDTH)
        self.setObjectName("card")
        self.setCursor(Qt.PointingHandCursor)

        self._edge = DEEP if boss.get("everdark") else BORDER
        self._selected = False
        self._hovered = False
        self._apply_appearance()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(9, 9, 9, 9)
        layout.setSpacing(4)

        header = QHBoxLayout()
        header.setSpacing(9)
        badge = QLabel()
        badge.setFixedSize(ICON, ICON)
        base = icons.menu(boss.get("icon")) if icons else None
        twin = boss.get("everdark")
        other = icons.menu(twin.get("icon")) if (icons and twin) else None
        if base is not None and other is not None:
            badge.setPixmap(_split_circle(base, other, ICON))
        elif base is not None:
            badge.setPixmap(base.scaled(ICON, ICON, Qt.KeepAspectRatio,
                                        Qt.SmoothTransformation))
        header.addWidget(badge)

        titles = QVBoxLayout()
        titles.setSpacing(1)
        name = QLabel(boss["name"])
        name.setWordWrap(True)
        name.setStyleSheet("color: #e8e8e8; font-size: 13px; font-weight: bold;")
        titles.addWidget(name)

        expedition = QLabel(boss["expedition"])
        expedition.setWordWrap(True)
        expedition.setStyleSheet(f"color: {ACCENT}; font-size: 11px;")
        titles.addWidget(expedition)

        twin_group = (boss.get("everdark") or {}).get("group")
        tag = QLabel(f"+ {twin_group}" if twin_group
                     else "no Everdark version")
        tag.setStyleSheet(
            f"color: {DEEP if twin_group else MUTED}; font-size: 10px;")
        titles.addWidget(tag)
        titles.addStretch(1)
        header.addLayout(titles, 1)
        layout.addLayout(header)

        description = QLabel(boss["description"] or "no description in the files")
        description.setWordWrap(True)
        description.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        layout.addWidget(description, 1)

    def _apply_appearance(self) -> None:
        """Draw the card in the state it is in.

        Border width is the same either way. A selected card that grew its
        border would push its own contents a pixel inwards, and the grid
        would twitch every time a reader tried another Nightlord.

        Selection outranks hover, and deliberately: the card the panel is
        describing must keep saying so while a reader runs the pointer along
        the row looking for the next one.
        """
        edge = SELECTED_EDGE if self._selected else self._edge
        if self._selected:
            fill = SELECTED_FILL
        elif self._hovered:
            fill = HOVER_FILL
        else:
            fill = PANEL
        self.setStyleSheet(
            f"#card {{ background: {fill}; border: 1px solid {edge};"
            f" border-radius: 7px; }}"
            " #card QLabel { background: transparent; border: none; }"
        )

    @property
    def selected(self) -> bool:
        """Is this the card the detail panel is describing?"""
        return self._selected

    def set_selected(self, selected: bool) -> None:
        """Mark, or unmark, this card as the one the panel is describing."""
        if selected == self._selected:
            return
        self._selected = selected
        self._apply_appearance()

    @property
    def hovered(self) -> bool:
        """Is the pointer on this card, its own area or a label inside it?"""
        return self._hovered

    def _set_hovered(self, hovered: bool) -> None:
        if hovered == self._hovered:
            return
        self._hovered = hovered
        self._apply_appearance()

    def enterEvent(self, event) -> None:  # noqa: N802 - Qt naming
        """The pointer arrived, here or on one of the labels.

        Qt sends Enter down the whole chain under the pointer and Leave only
        to the widgets it actually left, so moving from the card onto the
        name inside it is not a departure and this card stays marked.
        """
        self._set_hovered(True)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # noqa: N802 - Qt naming
        self._set_hovered(False)
        super().leaveEvent(event)

    def _pointer_is_here(self) -> bool:
        """Is the pointer standing on this card at this instant?

        Asked of the screen instead of remembering the last Enter and Leave,
        because Qt sends those on pointer movement only. `widgetAt` answers
        for this application's windows and takes clipping and stacking with
        it, so a card scrolled out of sight or covered by another program
        does not claim the pointer.
        """
        under = QApplication.widgetAt(QCursor.pos())
        return under is not None and (under is self or self.isAncestorOf(under))

    def follow_the_pointer(self) -> None:
        """Put the mark where the pointer actually is, not where it was.

        QA-164: the grid reflows from three columns to two while the pointer
        rests, and the mark stays on a card that is no longer under it -- or
        a card appears under a resting pointer and never takes the mark at
        all. Both are the same gap: geometry changed and no pointer event
        followed. The card's own move, resize and show are exactly the
        moments that happens, so it re-reads the pointer there.
        """
        self._set_hovered(self._pointer_is_here())

    def moveEvent(self, event) -> None:  # noqa: N802 - Qt naming
        super().moveEvent(event)
        self.follow_the_pointer()

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt naming
        super().resizeEvent(event)
        self.follow_the_pointer()

    def showEvent(self, event) -> None:  # noqa: N802 - Qt naming
        super().showEvent(event)
        self.follow_the_pointer()

    def press(self) -> None:
        """Open this Nightlord's profile. Every route ends here."""
        self.clicked.emit(self.boss)

    def mousePressEvent(self, event) -> None:  # noqa: N802 - Qt naming
        self.press()
        super().mousePressEvent(event)

    def keyPressEvent(self, event) -> None:  # noqa: N802 - Qt naming
        if event.key() in PRESS_KEYS:
            self.press()
            event.accept()
            return
        super().keyPressEvent(event)

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt naming
        """Draw the card, then say where the keyboard is standing.

        The style's own focus rectangle rather than a fourth colour of this
        program's. The Nightlord grid already spends its three channels --
        fill for the chosen card, a second fill for the pointer, the edge for
        an Everdark twin (QA-150, QA-154) -- and a keyboard mark invented on
        top of those would have to be told apart from all three. The platform
        draws focus one way everywhere, and this is that way.
        """
        super().paintEvent(event)
        if not self.hasFocus():
            return
        option = QStyleOptionFocusRect()
        option.initFrom(self)
        # Inside the 1 px border and the 7 px corner radius, so the mark is
        # a mark of its own rather than a recolouring of the edge that
        # already means "Everdark twin".
        option.rect = self.rect().adjusted(4, 4, -4, -4)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_FrameFocusRect, option, painter,
                                   self)
        painter.end()


class BossTab(QWidget):
    def __init__(self, data: dict, icons=None):
        super().__init__()
        self.bosses = merge_everdark(data.get("bosses", []))
        # Keyed by card id as text, because JSON has no other key type. The
        # tree below filters this on the chosen Nightlord (AD-041 point 2).
        self.subbosses = data.get("subbosses") or {}
        self.drops = ((data.get("world_events") or {}).get("drops")) or {}
        self.icons = icons
        # Which entry the panel is describing, and whether its loot list is
        # open. Both belong to the panel and not to a row, because the panel
        # is what gets rebuilt (AK-324.3).
        self._shown: dict | None = None
        self._loot_expanded = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        layout.addWidget(tabheader.heading(HEADING))
        layout.addWidget(tabheader.question(QUESTION))

        # No filter box. Ten entries all fit on screen at once, so a search
        # field only took up room and gave the list a state it did not need.
        self.summary = QLabel()
        self.summary.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        # Wrap, or this line's full text width becomes the tab's minimum and
        # QTabWidget imposes it on the whole window -- the fault that hid the
        # detail panel off the right edge of the screen. See effectstab.
        self.summary.setWordWrap(True)
        layout.addWidget(self.summary)

        body = QHBoxLayout()
        body.setSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        # Scrolling brings other cards under a pointer that has not moved,
        # and Qt sends no pointer event for it -- the QA-164 gap reached by a
        # third route. A card cannot notice this one for itself: the holder
        # is what moves, and the cards keep their places inside it, so not
        # one of them sees a move of its own.
        scroll.verticalScrollBar().valueChanged.connect(
            self._follow_the_pointer)
        self.holder = QWidget()
        self.grid_outer = QVBoxLayout(self.holder)
        self.grid_outer.setContentsMargins(0, 0, 0, 0)
        self.grid_outer.setSpacing(10)
        scroll.setWidget(self.holder)
        body.addWidget(scroll, 1)

        self.detail_panel = self._build_detail()
        body.addWidget(self.detail_panel, 0)
        layout.addLayout(body, 1)

        # Cards and tree first, then the panel is put into its opening state:
        # clearing the panel also clears the marks on both of them.
        self.refresh()
        self.show_detail(None)

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt naming
        super().resizeEvent(event)
        self._share_the_width()

    def _follow_the_pointer(self) -> None:
        """Every card re-reads the pointer, because the grid moved under it."""
        for card in self.holder.findChildren(BossCard):
            card.follow_the_pointer()

    def _share_the_width(self) -> None:
        """Give the detail panel its width, which depends on the tab's.

        `DETAIL_WIDTH` wherever there is room for it, its share of the tab
        where there is not, and never below `DETAIL_FLOOR`. See DETAIL_SHARE
        for what the share is and why it is that.
        """
        self.detail_panel.setFixedWidth(
            min(DETAIL_WIDTH,
                max(DETAIL_FLOOR, self.width() // DETAIL_SHARE)))

    def _build_detail(self) -> QWidget:
        """Everything the files hold about one boss, not just its blurb.

        Scrollable, because the field list is longer than the artwork panel it
        replaced and grows whenever another link is cracked.
        """
        outer = QScrollArea()
        # No width here: `_share_the_width` gives it one on every resize,
        # because the right width depends on how much tab there is.
        outer.setWidgetResizable(True)
        outer.setFrameShape(QFrame.NoFrame)

        panel = QFrame()
        panel.setObjectName("detail")
        panel.setStyleSheet(
            f"#detail {{ background: {PANEL}; border: 1px solid {BORDER};"
            f" border-radius: 7px; }}"
            " #detail QLabel { background: transparent; border: none; }"
        )
        outer.setWidget(panel)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        self.detail_art = QLabel()
        self.detail_art.setAlignment(Qt.AlignCenter)
        self.detail_art.setMinimumHeight(DETAIL_ART_HEIGHT)
        layout.addWidget(self.detail_art)

        self.detail_name = QLabel()
        self.detail_name.setWordWrap(True)
        # The boss's own name, straight out of the game's FMG text. A QLabel
        # left on AutoText decides for itself whether what it is handed is
        # markup, so a name carrying a tag would be rendered as one instead of
        # shown as the name it is (SEC-012, the same defect as SEC-004). This
        # label never wants markup, so it is told so where it is built.
        self.detail_name.setTextFormat(Qt.PlainText)
        self.detail_name.setStyleSheet(
            "color: #e8e8e8; font-size: 15px; font-weight: bold;")
        layout.addWidget(self.detail_name)

        self.detail_expedition = QLabel()
        self.detail_expedition.setWordWrap(True)
        self.detail_expedition.setStyleSheet(f"color: {ACCENT}; font-size: 12px;")
        layout.addWidget(self.detail_expedition)

        self.detail_text = QLabel()
        self.detail_text.setWordWrap(True)
        # The boss's description, from the same FMG text and on AutoText for
        # the same reason (SEC-012).
        self.detail_text.setTextFormat(Qt.PlainText)
        self.detail_text.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        layout.addWidget(self.detail_text)

        self.detail_body = QLabel()
        self.detail_body.setWordWrap(True)
        self.detail_body.setTextFormat(Qt.RichText)
        self.detail_body.setAlignment(Qt.AlignTop)
        layout.addWidget(self.detail_body)

        # The rest of the loot list, behind the Hold/Held toggle this program
        # already has (AK-54/AK-292, AK-324.3). A widget and not a line of
        # the rich text above it, because rich text cannot be clicked; it
        # sits directly under the LOOT rows, which are the last thing a
        # sub-boss panel draws.
        self.loot_button = QToolButton()
        self.loot_button.setCheckable(True)
        self.loot_button.setStyleSheet(relicslots.WORD_BUTTON_STYLE)
        self.loot_button.setVisible(False)
        # `toggled` and not `clicked`: a mouse and the space bar emit both,
        # but a screen reader's `TogglePattern.Toggle()` arrives as
        # `QAbstractButton::toggle()` and emits only this one, so `clicked`
        # left the button dead to assistive software (QA-288). The `Hold`
        # button of AK-54 is wired the same way.
        self.loot_button.toggled.connect(self._toggle_loot)
        layout.addWidget(self.loot_button, 0, Qt.AlignLeft)
        layout.addStretch(1)

        return outer

    def _build_tree(self) -> QTreeWidget:
        """The sub-boss list that hangs under the grid (AD-041 point 1).

        No scrollbar of its own: it sits in the tab's own scroll area, and a
        second one inside the first would be a second place to be lost in
        (AK-319.6). Its chosen row wears the fill the cards wear, not Qt's
        blue, so the two halves of the tab say "this one" the same way
        (AK-321.1).
        """
        tree = QTreeWidget()
        tree.setHeaderLabels(list(TREE_HEADERS))
        tree.headerItem().setToolTip(1, SHARE_TIP)
        tree.setRootIsDecorated(False)
        tree.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tree.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # As tall as its rows and no taller, worked out by Qt at every
        # layout rather than by this file once: a height measured here would
        # be a height measured before the window put its own font on the
        # tree, and the rows past it would be cut off with the scrollbar
        # switched off and nothing on screen saying so.
        tree.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        tree.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        tree.setStyleSheet(
            f"QTreeWidget {{ background: {PANEL}; border: 1px solid {BORDER};"
            f" border-radius: 7px; }}"
            f"QTreeWidget::item:selected {{ background: {SELECTED_FILL};"
            " color: #f0f0f0; }"
        )
        tree.itemSelectionChanged.connect(self._tree_chose)
        return tree

    def _subboss_entries(self, boss: dict) -> list[dict]:
        """The cards this Nightlord's own map patterns can put on the board.

        One entry per card and not per character (AD-040): the same figure
        stands on several cards at different HP. Each entry carries its card
        id as `key`, which is what tells two of them apart (AD-041 point 4).
        """
        out = []
        for card, entry in self.subbosses.items():
            share = next((100 * row["patterns"] / row["of"]
                          for row in entry.get("nightlords") or []
                          if row["boss"] == boss.get("id") and row["of"]),
                         None)
            if share is not None:
                out.append(dict(entry, key=card, share=share))
        return out

    def _fill_tree(self, boss: dict | None) -> None:
        """Draw the tree for one Nightlord, or the line that asks for one."""
        self.tree.clear()
        if boss is None:
            asking = QTreeWidgetItem([NO_NIGHTLORD_YET, ""])
            # Not selectable and not focusable: it is a sentence, not a card.
            asking.setFlags(Qt.NoItemFlags)
            asking.setForeground(0, QColor(MUTED))
            self.tree.addTopLevelItem(asking)
            self.tree.updateGeometry()
            return

        entries = self._subboss_entries(boss)
        for day, title in TREE_GROUPS:
            if day is None:
                members = [e for e in entries if not e.get("days")]
            else:
                members = [e for e in entries if day in (e.get("days") or [])]
            # A group with nothing in it goes entirely, the way a row with no
            # hits goes from the Red variants table (AK-319.2).
            if not members:
                continue
            group = QTreeWidgetItem([title, ""])
            # Reachable with the arrow keys, but never the chosen row.
            group.setFlags(Qt.ItemIsEnabled)
            group.setForeground(0, QColor(ACCENT))
            group.setFont(0, _group_font())
            self.tree.addTopLevelItem(group)
            for entry in sorted(members, key=_tree_order):
                group.addChild(self._tree_row(entry, day))
        self.tree.expandAll()
        # The row count decides the height, so the layout has to be told the
        # hint has moved.
        self.tree.updateGeometry()

    @staticmethod
    def _tree_row(entry: dict, day: int | None) -> QTreeWidgetItem:
        """One card, under one of the two days or under the field bosses.

        A card both days can draw stands in both groups, and each of the two
        rows says so (AK-319.5) -- without that, the repetition reads as the
        QA-150 fault rather than as two ways into one card.
        """
        label = card_name(entry)
        days = entry.get("days") or []
        if day is not None and 1 in days and 2 in days:
            label = f"{label}  ·  also Day {2 if day == 1 else 1}"
        item = QTreeWidgetItem([label, f"{entry['share']:g}%"])
        item.setTextAlignment(1, Qt.AlignRight | Qt.AlignVCenter)
        item.setData(0, Qt.UserRole, entry)
        return item

    def _tree_chose(self) -> None:
        """A row of the tree is the chosen entry now."""
        items = self.tree.selectedItems()
        entry = items[0].data(0, Qt.UserRole) if items else None
        if entry is not None:
            self.show_detail(entry)

    def _toggle_loot(self, expanded: bool) -> None:
        """Open or close the rest of the loot list on the entry on screen.

        Takes the state the button reports rather than flipping its own, so
        that `_sync_loot_button`'s `setChecked` -- which emits `toggled` too
        -- finds nothing left to do and the panel is not redrawn on top of
        itself.
        """
        if expanded == self._loot_expanded:
            return
        self._loot_expanded = expanded
        self.show_detail(self._shown)

    @staticmethod
    def _section(title: str) -> str:
        return (f"<div style='color:{ACCENT}; font-size:10px; font-weight:bold;"
                f" letter-spacing:1px; margin-top:10px'>{title}</div>")

    @staticmethod
    def _note(text: str) -> str:
        """What the figures directly above are measured against (A12).

        Quieter than the figures and directly under them, because it is read
        once and the figures are read every time.
        """
        return (f"<div style='color:{MUTED}; font-size:10px; "
                f"margin-top:4px'>{text}</div>")

    # Chart label -> the game's own damage-type icon, extracted from the
    # relic screen's filter list. The three grey physical icons were pinned
    # by looking at them enlarged -- club on rubble is Strike, the broad
    # blade Slash, the gauntlet thrust Pierce -- not assumed from their ids.
    TYPE_ICONS = {
        "Standard": "MENU_FL_40141.png",
        "Strike": "MENU_FL_40142.png",
        "Slash": "MENU_FL_40143.png",
        "Pierce": "MENU_FL_40144.png",
        "Holy": "MENU_FL_40145.png",
        "Magic": "MENU_FL_40146.png",
        "Frostbite": "MENU_FL_40147.png",
        "Fire": "MENU_FL_40148.png",
        "Lightning": "MENU_FL_40150.png",
        "Madness": "MENU_FL_40151.png",
        "Poison": "MENU_FL_40172.png",
        "Blood loss": "MENU_FL_40173.png",
        # Not in the MENU_FL filter set, which holds twelve icons and neither
        # of these. Taken from the equipment screen's own status symbols
        # instead -- MenuPropertySpecParam names the ids, and the three of that
        # run the FL set already covers identify the rest. See iconbuild's
        # UI_SPRITES for the working.
        "Scarlet Rot": "MENU_PropertyIcon_31231.png",
        "Sleep": "MENU_PropertyIcon_31234.png",
    }

    def _type_icon_cell(self, label: str) -> str:
        """A table cell with the type's game icon, or an empty spacer.

        Death has no icon here, so that row keeps a spacer rather than
        borrowing a lookalike.
        """
        sprite = self.TYPE_ICONS.get(label)
        path = self.icons.ui_path(sprite) if (self.icons and sprite) else None
        if path is None:
            return "<td style='padding-right:4px'></td>"
        src = pathlib.Path(path).as_uri()
        return (f"<td style='padding-right:4px'>"
                f"<img src='{src}' width='16' height='16'></td>")

    def _bars(self, damage: dict, weak: list) -> str:
        """Damage multipliers as a bar chart, 1.00 being neutral."""
        # Block characters rather than styled divs: Qt's rich text ignores
        # percentage widths, so a CSS bar renders as nothing at all.
        rows = []
        widest = max(list(damage.values()) + [1.0])
        for label, value in damage.items():
            filled = max(1, round(14 * value / widest)) if widest else 1
            if label in weak:
                colour = GOOD
            elif value < 1.0:
                colour = "#5a5a5a"
            else:
                colour = "#98a0ad"
            bar = "&#9608;" * filled
            rows.append(
                "<tr>"
                + self._type_icon_cell(label) +
                f"<td style='color:{MUTED}; font-size:11px;"
                f" padding-right:8px; white-space:nowrap'>{label}</td>"
                f"<td style='color:{colour}; font-size:11px;"
                f" white-space:nowrap'>{bar}</td>"
                f"<td style='color:{colour}; font-size:11px;"
                f" padding-left:8px; white-space:nowrap'>x{value:g}</td>"
                "</tr>"
            )
        return f"<table>{''.join(rows)}</table>"

    def _status(self, status: dict, weak: list) -> str:
        rows = []
        for label, value in sorted(status.items(), key=lambda kv: kv[1]):
            if value >= 999:
                shown, colour = "immune", "#5a5a5a"
            elif label in weak:
                shown, colour = str(value), GOOD
            else:
                shown, colour = str(value), "#d8d8d8"
            rows.append(
                "<tr>"
                + self._type_icon_cell(label) +
                f"<td style='color:{MUTED}; font-size:11px;"
                f" padding-right:8px; white-space:nowrap'>{label}</td>"
                f"<td style='color:{colour}; font-size:11px;"
                f" white-space:nowrap'>{shown}</td>"
                "</tr>"
            )
        return f"<table>{''.join(rows)}</table>"

    @staticmethod
    def _row(label: str, value, colour: str = "#d8d8d8") -> str:
        """A labelled value. `colour` is what the value itself is drawn in.

        The default is the colour the panel gives everything it read out of
        the game's files. A row whose value was watched in play rather than
        read passes OBSERVED_COLOUR instead (AK-94); the label keeps the
        muted colour either way, because the label is this module's word and
        not the sighting.
        """
        return (f"<div style='margin-top:2px'>"
                f"<span style='color:{MUTED}; font-size:11px'>{label}</span>"
                f"<span style='color:{colour}; font-size:11px'> &nbsp;{value}"
                f"</span></div>")

    def _stance_rank(self, profile: dict) -> str:
        """Where this boss sits among the ten on how hard it is to stagger.

        A bar size alone means little without the field to compare it to,
        and "how are they different" is the question the tab is really for.
        """
        bars = []
        for other in self.bosses:
            stance = ((other.get("weakness") or {}).get("profile")
                      or {}).get("stance") or {}
            if "bar" in stance:
                bars.append((stance["bar"], other["name"]))
        mine = (profile.get("stance") or {}).get("bar")
        if mine is None or len(bars) < 2:
            return "-"
        bars.sort()
        place = sum(1 for value, _ in bars if value < mine) + 1
        # The two names are the game's own text and this string is put into a
        # rich-text label, so they are escaped rather than concatenated
        # (SEC-012). Escaping at the point the value enters the markup is the
        # only place it can be got right: the caller cannot know it will.
        return (f"{place} of {len(bars)} for bar size  "
                f"(smallest {html.escape(bars[0][1])} {bars[0][0]:g}, "
                f"largest {html.escape(bars[-1][1])} {bars[-1][0]:g})")

    @staticmethod
    def _entry_key(entry: dict | None):
        """What tells two entries on this tab apart (AD-041 point 4).

        A Nightlord's name is unique among the ten. A sub-boss's is not: Red
        Wolf stands on two cards and the Bell Bearing Hunter on three, at
        different HP, so a sub-boss carries its card id as `key` instead.
        Comparing by value and not by identity, because `BossCard.clicked`
        is declared `Signal(dict)` and Qt marshals the entry across it: what
        reaches the slot after a click is an equal dict and never the object
        the card holds -- measured 2026-09-05, `emitted is card.boss` is
        False and `==` is True. An `is` here would mark nothing, silently.
        """
        if entry is None:
            return None
        return entry.get("key", entry["name"])

    def _mark_selected(self, boss: dict | None) -> None:
        """Put the marker on the row this entry came from, and on no other.

        Both sources at once: a card and a tree row are two ways to choose
        one panel, and at most one mark may stand anywhere on the tab
        (AK-321.2).
        """
        key = self._entry_key(boss)
        for card in self.holder.findChildren(BossCard):
            card.set_selected(self._entry_key(card.boss) == key)
        # Blocked, or setting a row would come straight back through
        # `_tree_chose` and rebuild the panel on top of itself.
        with QSignalBlocker(self.tree):
            for top in range(self.tree.topLevelItemCount()):
                item = self.tree.topLevelItem(top)
                for index in range(item.childCount()):
                    row = item.child(index)
                    row.setSelected(
                        self._entry_key(row.data(0, Qt.UserRole)) == key)

    def show_detail(self, boss: dict | None) -> None:
        # Which card the panel is describing belongs on the grid and not only
        # in the panel. At 8 px between cards a near miss opens the neighbour,
        # and with no marker the grid looks exactly as it did before -- so a
        # player can read a profile, believe it is the Nightlord he aimed at
        # and plan the fight against a different one (QA-150).
        subboss = boss is not None and "key" in boss
        if self._entry_key(boss) != self._entry_key(self._shown):
            # Another entry, so its loot list starts closed again.
            self._loot_expanded = False
        self._shown = boss
        self._mark_selected(boss)
        if not subboss:
            # The tree is the chosen Nightlord's own list: refilled when the
            # Nightlord changes, left alone when one of its rows is opened.
            self._fill_tree(boss)
        if boss is None:
            self.detail_art.clear()
            self.detail_name.setText("Select a Nightlord")
            self.detail_expedition.clear()
            self.detail_text.clear()
            self.detail_body.clear()
            self._sync_loot_button(0)
            return

        twin = boss.get("everdark")
        if subboss:
            # No artwork exists for these (AD-041), so the label gives its
            # height back rather than opening every sub-boss panel with an
            # empty block that means nothing (AK-321.3). No description
            # either: a sub-boss entry carries no such field (AD-040), and a
            # stand-in sentence would read as one the files gave (AK-322.2).
            self.detail_art.clear()
            self.detail_art.setMinimumHeight(0)
            self.detail_name.setText(card_name(boss))
            self.detail_expedition.setText(card_role(boss.get("days") or []))
            self.detail_text.clear()
        else:
            self.detail_art.setMinimumHeight(DETAIL_ART_HEIGHT)
            base = (self.icons.menu(boss.get("large_icon"))
                    if self.icons else None)
            other = (self.icons.menu(twin.get("large_icon"))
                     if (self.icons and twin) else None)
            if base is not None and other is not None:
                self.detail_art.setPixmap(_split_circle(base, other, 256))
            elif base is not None:
                self.detail_art.setPixmap(base.scaled(
                    256, 256, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self.detail_art.clear()
            self.detail_name.setText(boss["name"])
            # The expedition name is dropped: it says nothing a player
            # planning a fight can act on. What replaces it is whether there
            # is a Sovereign version, which is what the split portrait above
            # is showing.
            self.detail_expedition.setText(
                f"Nightlord  ·  {twin.get('group') or 'Everdark Sovereign'}"
                if twin else "Nightlord  ·  no Everdark version"
            )
            self.detail_text.setText(boss["description"])

        parts: list[str] = []
        # The description sits in its own label directly above; without this
        # the first heading crowds straight into it.
        parts.append("<div style='height:14px'></div>")

        told_about_sightings = False

        def legend_once() -> str:
            """What the sighting colour means, the first time it is used.

            AK-74 asks that a colour carrying a meaning be named once. It is
            named here rather than at the top of the tab because a panel whose
            Nightlord has no sighting must not explain a colour that is
            nowhere on it (QA-145). Separate from `sighting` below because two
            of the watched lines on this panel are not plain sentences -- a
            labelled row and a clause inside an extracted line -- and they
            need the legend just as much (QA-152).
            """
            nonlocal told_about_sightings
            if told_about_sightings:
                return ""
            told_about_sightings = True
            return (f"<div style='color:{OBSERVED_COLOUR}; font-size:11px;"
                    f" margin-top:3px'><i>{SIGHTING_LEGEND}</i></div>")

        def sighting(text: str) -> str:
            """A line watched in play, and — the first time — what that means.

            AK-94 gives these lines their own colour.
            """
            return (legend_once()
                    + f"<div style='color:{OBSERVED_COLOUR}; "
                      f"font-size:11px; margin-top:3px'>{text}</div>")

        # Everything here is written for someone about to fight this boss.
        # How a figure was derived, what could not be extracted and which
        # evidence class a claim belongs to are all real questions -- they
        # live in OPEN_QUESTIONS.md, not on screen. If a line does not change
        # how the fight is played, it does not belong in this panel.

        weakness = boss.get("weakness")
        profile = (weakness or {}).get("profile")
        if not profile:
            # Two headings, not one. The Nightlord case means "we know who he
            # is and cannot derive the weakness"; the sub-boss case means "we
            # do not know who this is", and one title over both would make
            # the stronger of the two sound like the weaker (AK-322.4).
            parts.append(self._section("IDENTITY" if subboss else "WEAKNESSES"))
            parts.append(
                f"<div style='color:{BAD}; font-size:11px'>"
                f"{self._identity(boss) if subboss else NOT_DERIVABLE}</div>")
            self.detail_body.setText("".join(parts))
            self._sync_loot_button(0)
            return

        if subboss:
            # One number with nothing to compare it to, which is why it is
            # not ranked the way the stance bar is (AK-323).
            parts.append(self._section("VITALS"))
            parts.append(self._row("HP", f"{profile['hp']:g}"))

        weak = profile.get("weak_damage") or []
        weak_status = profile.get("weak_status") or []
        # Any weakness at all opens the section, damage type or status
        # (QA-131). Gating it on the damage types alone hid Adel's whole
        # weakness -- he is the one Nightlord of the ten with no type that
        # hurts him more than another -- and with it the note written for him.
        if weak or weak_status:
            parts.append(self._section("WEAKNESS SPECIAL INTERACTION"))
            if weak:
                parts.append(
                    "<div style='color:#d8d8d8; font-size:11px'>"
                    "Pile on <b style='color:" + ACCENT + "'>"
                    + " / ".join(weak) + "</b> damage. It builds a hidden "
                    "meter, and filling it breaks the boss's stance and "
                    "opens it up for a critical.</div>"
                )
            else:
                # Deliberately not the sentence above. `weak_status` is the
                # set of lowest buildup thresholds, which is a different claim
                # from "this type fills the hidden meter", and saying the
                # second where the files only support the first would be the
                # guess A7 forbids.
                parts.append(
                    f"<div style='color:#d8d8d8; font-size:11px'>"
                    "No damage type hurts it more than another. Where it "
                    "gives way is status: it needs least of "
                    f"<b style='color:{ACCENT}'>{' / '.join(weak_status)}</b>"
                    ", listed with the rest under STATUS BUILDUP below.</div>"
                )
            if boss["name"] in WEAKNESS_NOTE:
                parts.append(sighting(WEAKNESS_NOTE[boss["name"]]))
            if boss["name"] in DEBUFF_ON_BREAK:
                parts.append(sighting(DEBUFF_ON_BREAK_SIGHTING))

        parts.append(self._section("DAMAGE TAKEN"))
        parts.append(self._bars(profile["damage"], profile["weak_damage"]))
        parts.append(self._note(
            "Bars compare this Nightlord's damage types with each other, not "
            "with another Nightlord. Green marks the type it is weak to."))
        parts.append(self._section("STATUS BUILDUP"))
        parts.append(self._status(profile["status"], profile["weak_status"]))
        parts.append(self._note(
            "How much status you have to apply before it lands — lower is "
            "easier. Green marks this Nightlord's easiest statuses."))

        stance = profile.get("stance") or {}
        if stance:
            parts.append(self._section("STANCE"))
            if "bar" in stance:
                parts.append(self._row("Bar to break", f"{stance['bar']:g}"))
            recovery = stance.get("recovery")
            # `-1` is the files' way of saying "no value here", and Maris is
            # the one Nightlord carrying it. Printing it read as `Refills at
            # x-1`, an impossible rate on a panel of real ones (QA-130). The
            # same guard already stands over `immune` in the status list.
            if isinstance(recovery, (int, float)) and recovery > 0:
                parts.append(self._row("Refills at", f"x{recovery:g}"))
            elif "recovery" in stance:
                parts.append(self._row(
                    "Refills at", "— not in the game's files"))
            # The rank compares this boss with the ten Nightlords, which is
            # not a field a sub-boss belongs to; its raw stance figures above
            # stay (AD-041 point 3).
            if not subboss:
                parts.append(self._row("Ranking", self._stance_rank(profile)))
            parts.append(self._note(
                "Bar to break is in the game's own stance points. The refill "
                "figure is the rate the files give; they do not say what it "
                "is per, so compare it between Nightlords rather than reading "
                "it as a speed."))

        ladder = profile.get("ladder") or {}
        defence = profile.get("defence_buffs") or []
        if ladder.get("up") or defence:
            parts.append(self._section("IT BUFFS ITSELF"))
            for entry in ladder["up"]:
                bits = [f"x{entry['attack']:g} attack"]
                stance_taken = entry.get("stance_taken")
                if stance_taken and abs(stance_taken - 1.0) > 1e-6:
                    bits.append("harder to stagger" if stance_taken < 1
                                else "easier to stagger")
                if not entry.get("from"):
                    bits.append("always on")
                parts.append(
                    f"<div style='margin-top:2px'>"
                    f"<span style='color:{BAD}; font-size:11px'>Buff</span>"
                    f"<span style='color:#d8d8d8; font-size:11px'>"
                    f" &nbsp;{'  ·  '.join(bits)}</span></div>")
            # Not in the dataset -- it is somebody's sighting, and AK-94 puts
            # sightings in OBSERVED_COLOUR so a reader can tell it from the
            # extracted figures directly above it.
            parts.append(sighting("Stacks: yes — repeats compound"))
            if boss["name"] in BUFF_TRIGGER:
                # Watched, like the line above it: the files hold the
                # animation id and never what provokes it, so BUFF_TRIGGER is
                # kept in this module from play. It stayed a labelled row
                # drawn in the colour of the extracted figures above it, which
                # is the one place on this panel where a sighting read as a
                # reading (AK-94, QA-152).
                parts.append(legend_once() + self._row(
                    "Set off by", BUFF_TRIGGER[boss["name"]],
                    colour=OBSERVED_COLOUR))
        for entry in defence:
            cut = round((1 - entry["taken"]) * 100)
            bits = [f"takes {cut}% less damage", f"{entry['seconds']:g}s"]
            trigger = DEFENCE_TRIGGER.get((boss["name"], entry["id"]))
            # The figures come out of the files and the trigger clause out of
            # play, on one line. So the sighting colour goes on the clause and
            # not on the line: colouring the whole line would say the figures
            # beside it were watched too, and leaving the clause in the
            # ordinary colour said the opposite (AK-94, QA-152).
            watched = ""
            if trigger:
                watched = (f"<span style='color:{OBSERVED_COLOUR}; "
                           f"font-size:11px'>  ·  {trigger}</span>")
            parts.append(
                (legend_once() if trigger else "")
                + f"<div style='margin-top:2px'>"
                f"<span style='color:{DEEP}; font-size:11px'>Defence</span>"
                f"<span style='color:#d8d8d8; font-size:11px'>"
                f" &nbsp;{'  ·  '.join(bits)}</span>{watched}</div>")
        # A12, and the reason it is one note over both kinds of line: the two
        # differ in exactly the point a reader would otherwise have to guess.
        # `x1.35 attack` stood here with no reference at all, between three
        # neighbouring sections that each carried one (QA-149).
        if ladder.get("up") or defence:
            parts.append(self._note(BUFF_NOTE))

        # The other half of the same ladder, and until QA-129 the tab threw it
        # away: seven of the ten carry a step that lowers their attack, and not
        # one of them showed it. What stood there instead were two figures
        # typed into this module, against three names that are not those seven.
        #
        # Its own section rather than a row under "IT BUFFS ITSELF": these
        # figures move the boss the other way, and the same heading over both
        # is how a reader ends up taking one for the other.
        weakened = ladder.get("down") or []
        if weakened:
            parts.append(self._section("IT IS WEAKENED"))
            for entry in weakened:
                bits = [f"x{entry['attack']:g} its attack power"]
                stance_taken = entry.get("stance_taken")
                if stance_taken and abs(stance_taken - 1.0) > 1e-6:
                    bits.append(f"x{stance_taken:g} the stance damage it "
                                f"takes")
                parts.append(
                    f"<div style='margin-top:2px'>"
                    f"<span style='color:{GOOD}; font-size:11px'>Weakened"
                    f"</span><span style='color:#d8d8d8; font-size:11px'>"
                    f" &nbsp;{'  ·  '.join(bits)}</span></div>")
            parts.append(self._note(WEAKENED_NOTE))

        rates = profile.get("part_rates") or {}
        if rates:
            parts.append(self._section("BODY PARTS"))
            for label, value in rates.items():
                parts.append(self._row(
                    html.escape(PART_NAMES.get((boss["name"], label), label)),
                    f"x{value:g} damage"
                    + ("  — armoured" if value < 1 else "  — soft spot")))
            if profile.get("skips_weak_animation"):
                parts.append(self._row("Hit reaction", "none, ever"))
            parts.append(self._note(PARTS_NOTE))

        drops = self._loot(boss) if subboss else []
        if subboss:
            parts.append(self._section("LOOT"))
            if not drops:
                parts.append(f"<div style='color:{MUTED}; font-size:11px'>"
                             f"{NO_LOOT}</div>")
            else:
                shown = drops if self._loot_expanded else drops[:LOOT_OPEN]
                for drop in shown:
                    # `quote=False`: this is element text, not an attribute
                    # value, so an apostrophe in an item name stays an
                    # apostrophe on screen while `<` and `&` are still shut
                    # out of the markup (SEC-012).
                    parts.append(self._row(
                        html.escape(drop["name"], quote=False),
                        f"{drop['share']:g}%"))
                parts.append(self._note(LOOT_NOTE))
        self._sync_loot_button(len(drops))

        if twin:
            parts.append(self._section("EVERDARK"))
            parts.append(
                f"<div style='color:{MUTED}; font-size:11px'>"
                "Same stats as above — resistances, stance and buff are "
                "identical. What differs is behaviour, not numbers.</div>"
            )

        self.detail_body.setText("".join(parts))

    @staticmethod
    def _identity(entry: dict) -> str:
        """Why this card has no name, in the two ways the files can fail.

        `ambiguous` lists what the files do give -- the HP of the figures
        that could be standing there -- and no names, because the data
        carries none (AD-040 point 4.3). Guessing one would be the very
        thing A7 forbids.
        """
        if (entry.get("weakness") or {}).get("confidence") != "ambiguous":
            return NOT_DERIVABLE
        hp = sorted((candidate["hp"]
                     for candidate in entry.get("candidates") or []),
                    reverse=True)
        return ("Multiple bosses could be on this card — the files don't say "
                f"which. Candidates by HP: "
                f"{', '.join(f'{value:g}' for value in hp)}.")

    def _loot(self, entry: dict) -> list[dict]:
        """What this card's boss drops, rarest first (AK-324.3).

        Ascending `share`, because that is the one figure the drop tables
        carry: they say how often an item falls and never whether a player
        wants it, so "rarest first" is the reader's own order and not a
        ranking read out of the data. A tie goes alphabetically -- there is
        no second figure to break it on.
        """
        drops = self.drops.get(str(entry.get("chr"))) or []
        return sorted(drops, key=lambda drop: (drop["share"], drop["name"]))

    def _sync_loot_button(self, count: int) -> None:
        """Offer the rest of the loot list, where there is a rest."""
        rest = count - LOOT_OPEN
        self.loot_button.setVisible(rest > 0)
        if rest > 0:
            self.loot_button.setChecked(self._loot_expanded)
            self.loot_button.setText(
                "Show fewer" if self._loot_expanded else f"Show {rest} more")

    def refresh(self) -> None:
        while self.grid_outer.count():
            item = self.grid_outer.takeAt(0)
            widget = item.widget()
            if widget:
                # Unparent before scheduling deletion. deleteLater alone leaves
                # the old cards attached until the event loop next runs, so a
                # rebuild would briefly stack two generations of the grid.
                widget.setParent(None)
                widget.deleteLater()

        cards = []
        for boss in self.bosses:
            card = BossCard(boss, self.icons)
            card.clicked.connect(self.show_detail)
            cards.append(card)
        # As many columns as the width takes, recounted whenever the window
        # changes. The four hard-coded ones sliced Gnoster, Maris, Caligo and
        # Harmonia at a 1067 px window and Maris and Harmonia at 1250, while
        # the line above them said "10 Nightlords" (DR-013).
        self.cards = cardgrid.CardGrid(CARD_WIDTH, cards, stretch=True)
        self.grid_outer.addWidget(self.cards)
        # Under the grid and in the same scroll area (AD-041 point 1).
        self.tree = self._build_tree()
        self.grid_outer.addWidget(self.tree)
        self.grid_outer.addStretch(1)

        paired = sum(1 for b in self.bosses if b.get("everdark"))
        # The click hint has moved into QUESTION above, where it is the first
        # thing read rather than the last (AK-89). Repeating it here would put
        # the same instruction twice on one screen.
        self.summary.setText(
            f"{len(self.bosses)} Nightlords  ·  {paired} also have an "
            f"Everdark Sovereign, shown as the upper-right half of each "
            f"circle"
        )
