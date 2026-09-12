"""Relic chooser laid out like the in-game relic screen: a grid of icons.

**This is the advisor's main way in, not a side door** (`GOAL.md` F2,
AD-018). `Optimize` on the Build planner answers "what is the best set
altogether"; this screen answers "what does *this* relic do for me *now*, in
*this* slot" -- and those are two questions. The figure on a card is the
candidate's marginal contribution against the current build with this slot
emptied, and the diminishing return the player asked about falls out of it by
itself, because the game's own curves are concave.

**Not one figure is computed here.** Every number a card shows is read off a
`SlotPool` that `advisor.candidates.pool` produced -- the very list the beam
search consumes, so the picker and `Optimize` cannot disagree about what a
relic is worth (AD-018 checkpoint 15). A second arithmetic in this file would
be exactly the duplication the design was built against.

**And not one figure is computed in this thread either** (AD-028). The pool
comes from the window's picker track -- a second instance of the same
`AdvisorController` the Advisor bar uses -- so the dialog opens at once and
fills in when the answer arrives. Until it does, the card area is empty
(§3.8 fassung 3): the App Designer weighed a wait against cards that move
under the pointer and chose the wait.
"""

from __future__ import annotations

import dataclasses

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QComboBox, QDialog, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QMenu, QPushButton, QScrollArea,
    QSizePolicy, QToolButton, QVBoxLayout, QWidget, QWidgetAction,
)

from . import advisorbar, cardgrid, effecttext, favourites, model
from .advisor import goals as advisor_goals
from .advisor import types as advisor_types
from .inventory import CUSTOM_RELIC_ID

#: How many cards wide the dialog first asks to be. Not a claim about the
#: grid: the grid reflows to whatever width it is actually given, and this
#: only decides the size the window manager is asked for. The opening width
#: is derived from it through `cardgrid.room_for`, so the two cannot part.
OPENING_COLUMNS = 5
#: The height the dialog first asks for, before it knows how tall a card is.
#: `_grow_to_three_rows` raises it once the cards exist; it never lowers it,
#: so this is a floor and not a size.
OPENING_HEIGHT = 720
#: How many whole rows of cards have to be readable at the opening size
#: (AK-51). Three, because two rows of a 29-card grid is a list seen through
#: a letterbox.
MINIMUM_ROWS = 3
ICON = 56
CARD_WIDTH = 190
#: The dialog's own layout margin, one side. Named because the opening width
#: has to add both of them back.
MARGIN = 14

ACCENT = "#c8a45c"
MUTED = "#8a8a8a"
PANEL = "#1e1f23"
BORDER = "#2e2f35"
CURSE = "#d1655f"
# Purple against the gold of a selected card: the two states have to be told
# apart at a glance, and gold's opposite is the one colour the rest of the
# window never uses.
FAVOURITE = "#a86fe0"

# The Nightfarer grid inside the favourite menu, matching the sidebar's shape.
HERO_COLUMNS = 5
HERO_ICON = 44

SLOT_COLOURS = {
    0: "#b4544e", 1: "#4e7ab4", 2: "#c2a24a", 3: "#5c9e63", 4: "#d8d8d8",
}

#: The caption of each value row, in one place. `UI_SPEC` AK-193 renames the
#: damage row to `Attack multipliers` once A17 lands, and that is meant to be
#: this one entry rather than five string literals spread over the file.
VALUE_CAPTIONS = {
    "max_damage": "Damage",
    "min_damage_taken": "Damage taken",
}

#: What a direction is called where a sentence or a chip needs a noun for it
#: (`UI_SPEC` §3.5 points 4 and 5). Beside the captions rather than inside
#: them: `Damage taken` is the row of a figure, `survival` is what the
#: direction is for, and the two are not interchangeable.
DIRECTION_NOUNS = {
    "max_damage": "damage",
    "min_damage_taken": "survival",
}

#: The directions a card shows, in the order the advisor bar lists them.
#: **Both, always, whatever the sorting** (AK-42): OF-13 asks for a way to say
#: "this costs you something, but not in the direction you are asking about"
#: that does not judge, and two figures side by side are that -- each in its
#: own unit, with no exchange rate invented between them (AD-023, A7).
VALUE_DIRECTIONS = advisorbar.GOAL_ORDER

#: What stands where a figure will be until it arrives (§3.3). The block is
#: built with this, so a card is exactly as tall before the figures as after
#: them -- with 29 cards a block that appeared later would jump the grid.
PENDING = "…"

#: What stands there when this direction carries no figure at all (AK-49).
#: An em dash and not a `0`: nothing was measured, which is a different
#: statement from "measured, and it came to nothing".
NO_FIGURE = "—"

#: A gain that is zero at the precision the card shows (AK-42). `+0.0` reads
#: like a rounded something, and on piecewise-linear curves an exact zero is
#: the commonest value there is.
NO_CHANGE = "no change"

#: The header when the direction being ranked in carries no figures at all
#: (AK-49, §3.7). The cards then say `—` and stand in name order, and the
#: `Sort by` box keeps standing on the direction that was chosen, so the
#: statement does not wander to another one while the player reads it.
NO_FIGURES_AT_ALL = ("The game's data carries no figures this goal can be "
                     "ranked on, so these relics are in name order.")

#: What stands where the top left card will stand while the question is out
#: (§3.8 fassung 3, AK-212). One line and nothing else: an empty area three
#: card rows tall is not to be told from a dialog that is broken, and a
#: skeleton of placeholder cards would be the movement this state exists to
#: avoid. It sits at the origin of the grid's content, so the card that
#: replaces it lands where it stood.
NOTHING_YET = "Your relics appear here."

#: What the run could not be, in the player's language (AK-208, AK-218). The
#: reason is the track's own line, and it is the only place the picker says
#: anything about a failure: the AK-49 sentence is about the game's data and
#: would be a claim about the dataset that nothing measured.
COULD_NOT_WORK_OUT = ("Could not work out what these are worth — {reason}. "
                      "They are in name order below.")

#: What `<reason>` is when the track was stopped rather than broken (AK-218).
#: A stop reaches the picker through `before_the_data_changes` and `shutdown`
#: only, and neither can be triggered while a modal dialog stands -- but an
#: unhandled `stopped` leaves an empty grid rather than a grid without
#: figures, which is why the case is built rather than reasoned away.
SEARCH_WAS_STOPPED = "the search was stopped"

#: The mandatory line of AD-018.3, in the player's language (§5.3), word for
#: word. It stands in the picker and not at the `Optimize` button, because it
#: is a warning about choosing one slot at a time and that is what happens
#: here.
ONE_SLOT_AT_A_TIME = ("One slot at a time — some relics only pay off "
                      "together; Optimize on the Build planner looks for "
                      "those.")

#: The third entry of `Sort by`, and what it stands for: the order the grid
#: has without an advisor at all. Not a direction, so it changes no goal
#: setting -- which is why it needs a value of its own that no goal id can
#: collide with (`advisor.goals.GOALS` keys the two directions by their own
#: names).
NAME_ORDER = "sort-by-name"

#: What `Sort by` calls that entry (§3.4).
NAME_ORDER_LABEL = "Name"

#: Widest the `Sort by` box may get (§3.4). A combo that sized itself to the
#: longest direction label would move with the registry.
SORT_BOX_WIDTH = 220

#: Decimal places every gain is shown at. Ties are decided here and nowhere
#: else (AK-45): two cards carry the same tie mark exactly when they show the
#: same text, so there can be no pair that looks equal and is marked apart.
GAIN_DECIMALS = 1


def _asked_height(widget, width: int, fallback: int) -> int:
    """How tall this widget is at `width`, wrapping included.

    One place because the dialog asks it of two different things -- the lines
    above the grid and the cards inside it -- and a second reading that used
    `sizeHint` for one of them would size the dialog against a layout it
    never has.
    """
    if widget is None:
        return fallback
    if widget.hasHeightForWidth():
        return max(widget.heightForWidth(width), fallback)
    return max(widget.sizeHint().height(), fallback)


def gain_text(gain: float, unit: str) -> str:
    """One gain as a card shows it: sign, figure, unit -- or `no change`.

    Rounded first and judged afterwards, which is the whole of AK-45: a gain
    of 0.04 is `no change` because that is what the card would otherwise say
    in three characters that mean something else (`+0.0`).

    The sign comes from `format`'s own `+`, as every other signed figure in
    this program is written (A13), so a reader meets one style of number.
    """
    shown = round(gain, GAIN_DECIMALS)
    if shown == 0:
        return NO_CHANGE
    figure = f"{shown:+.{GAIN_DECIMALS}f}"
    return f"{figure} {unit}" if unit else figure


def chip_text(goal_id: str) -> str:
    """The tie mark of one direction, in words (AK-46).

    Words and not only a colour: five cards worth the same carry the same
    mark, and a mark nobody can name is a mark nobody can compare.
    """
    return f"BEST FOR {DIRECTION_NOUNS[goal_id].upper()}"


def working_out(slot_name: str) -> str:
    """Line 3 while the question is out (§7(a), AK-214).

    This clause and nothing else: no count, no filter hint, no favourite
    hint, no right-click sentence. Every one of them is about cards that are
    not standing, and `29 of 29 relics` over an empty area announces relics
    the dialog is not showing.
    """
    return f"Working out what each relic is worth with {slot_name} empty"


def could_not_work_out(reason: str) -> str:
    """The header of a question that ended in no figures (AK-208, AK-218).

    The reason is a **clause** here -- the template puts the full stop after
    it -- and since T-191 one of the two reasons that reach this line is a
    whole sentence: a run that raised now reports through `errortext`, whose
    entries all end in a full stop by design, because most of them are shown
    on their own. Stripping it is what `advisorbar` has always done at its
    own sink (`_on_failed`), and doing it in one place here keeps the two
    screens from saying the same failure two ways.
    """
    return COULD_NOT_WORK_OUT.format(reason=reason.rstrip(". "))


def nothing_raises(goal_id: str) -> str:
    """What the header says instead of a chip nobody may wear (AK-46)."""
    return (f"Nothing you own raises {DIRECTION_NOUNS[goal_id]} in this "
            f"slot.")


class Ranking:
    """One slot's pool, read the way a card draws it.

    **It computes nothing.** Every figure comes out of `pool` as
    `advisor.candidates` left it, looked up by handle, so the number on a card
    and the number the beam search pre-sorted by are the same bits
    (AD-018 checkpoint 15). The lookup is a mapping rather than a scan because
    a slot offers up to 309 copies and the grid asks twice per card.

    **It has no direction of its own, and that is the point** (AK-205,
    Nachtrag IX-2). Every method here is asked which direction to answer in.
    The pool does carry one -- `SlotPool.rank_by`, the direction that put the
    list in this order -- and reading the drawn direction off it was right
    only while the picker asked under the direction the player had chosen.
    The picker now asks under one fixed direction whatever is chosen, so
    `rank_by` says nothing about what the player is looking at; a property
    here that handed it out would be the one line from which every value row,
    chip and sentence took the wrong direction at once.
    """

    def __init__(self, pool: advisor_types.SlotPool) -> None:
        self.pool = pool
        self._by_handle = {candidate.handle: candidate
                           for candidate in pool.candidates}

    def gain(self, item, goal_id: str) -> float | None:
        """What this copy adds under one direction, or `None`.

        `None` is a copy the pool does not carry -- a save that gives it no
        handle (AD-013 point 4). It is not a zero: the pool says so in its own
        findings, and a zero here would put a figure on a card the run never
        measured.
        """
        candidate = self._by_handle.get(getattr(item, "handle", None))
        if candidate is None:
            return None
        return advisor_types.marginal_for(candidate, goal_id)

    def unit(self, goal_id: str) -> str:
        """The unit that direction's figure is in, off the base state."""
        for baseline in self.pool.baseline:
            if baseline.goal_id == goal_id:
                return baseline.unit
        raise KeyError(f"this pool carries no baseline for goal {goal_id!r}")

    def top_handles(self, goal_id: str) -> frozenset:
        """Handles earning AK-46's chip under one direction, or none.

        **The one computation AK-46's chip and AK-195's ordering both read
        from** (T-094 Vorgaben point 1): a second maximum computed apart from
        this one is the duplication the task was written against. Equality is
        decided on the rounded text a card would show (AK-45), not the raw
        float, so two gains that display alike both count.

        Empty under the same three conditions AK-46 marks no card at all: the
        pool is empty, the top figure is `no change`, or it is negative.
        """
        pairs = [(candidate.handle, advisor_types.marginal_for(candidate, goal_id))
                 for candidate in self.pool.candidates]
        if not pairs:
            return frozenset()
        unit = self.unit(goal_id)
        top = gain_text(max(gain for _handle, gain in pairs), unit)
        if top == NO_CHANGE or top.startswith("-"):
            return frozenset()
        return frozenset(handle for handle, gain in pairs
                         if gain_text(gain, unit) == top)

    def texts_for(self, item) -> list[str]:
        """The value rows of one card, both directions, in order."""
        rows = []
        for goal_id in VALUE_DIRECTIONS:
            gain = self.gain(item, goal_id)
            rows.append(NO_FIGURE if gain is None
                        else gain_text(gain, self.unit(goal_id)))
        return rows


@dataclasses.dataclass(frozen=True)
class Asked:
    """What came of asking: an answer already, or a question on its way.

    Told apart from "there was nothing to ask" -- which is `None` in place of
    this object -- because the two look the same on screen and are not the
    same state: a dialog with no save behind it says what AK-49 asks for and
    waits for nothing, and a dialog whose question is out shows the empty
    grid. One `None` for both would have made the waiting state the display
    for "no save".
    """

    #: The answer, or `None` while it is still out.
    ranking: Ranking | None


class SlotAdvice:
    """Where the picker's figures and its one goal setting come from.

    **There is one goal setting in the program** (AK-43). It lives in the
    advisor bar's combo box, and this object is how the picker reads and
    writes it: a `Sort by` with a setting of its own would be a fourth place
    that can disagree with the other three.

    **Nothing is computed here any more** (AD-028). The pool used to be worked
    out in this call, in the calling thread, on the measurement that the worst
    slot cost about 51 ms -- a figure that was never measured but calculated,
    and that is out by a factor of 6,3: the worst slot is **318,1 ms** (median
    of 25, S11-C), above the 250 ms at which `UI_SPEC` AK-09 stops allowing a
    dialog to freeze at all and six times A6's 50 ms for the main thread. The
    question now goes to the window's picker track, which answers from its
    cache in the same call if it can and out of a thread otherwise; the
    dialog's part is in `RelicPicker`.

    **The direction asked under is not the direction drawn in** (Nachtrag
    IX-2). The track is asked under `goals.CANONICAL_POOL_ORDER`, marked as a
    `PoolOrder` so no reader can take it for the player's choice: a pool
    measures every candidate under every direction, so one entry serves both,
    and the same slot opened under the two directions is one question rather
    than two. What the screen draws in is `goal_id()` below.

    **The answer may arrive after the dialog has gone.** The track lives at
    the window and outlives every picker (AD-028 point 5), so this object
    stops listening when the dialog closes, and the track's own generation
    counter drops what belongs to an earlier opening.
    """

    def __init__(self, slot, bar, track) -> None:
        self._slot = slot
        self._bar = bar
        self._track = track
        self._answered = None

    def goal_id(self) -> str:
        """The direction the whole program is standing on."""
        return self._bar.goal_id()

    def choose_goal(self, goal_id: str) -> None:
        """Stand on another direction, everywhere at once (AK-43)."""
        self._bar.choose_goal(goal_id)

    def ask(self, answered) -> Asked | None:
        """Ask this slot's question once, or `None` if there is none to ask.

        `None` is "there is nothing to rank against" -- no save, so no
        inventory and no build, or a slot that is not one of the window's.
        The picker then shows what AK-49 asks for rather than a figure it made
        up, and no answer is ever coming.

        Otherwise the answer is either here already, in `Asked.ranking`, or
        `answered(ranking, reason)` is called once, later, with exactly one of
        the track's three outcomes: an answer, a failure with its reason, or a
        stop. Every one of the three fills the grid (AK-218) -- an outcome
        that did nothing would leave a dialog in which no relic can be chosen.

        **Every slot but this one is held, held by the player or not**
        (AD-018.1, AD-028 point 3): the question is what fits *this* slot
        beside the build as it stands, so the rest of the build is a boundary
        condition -- and the one slot left free is how the question says which
        slot it is about, without a field of its own in the key.
        """
        window = self._slot.window()
        asking = advisorbar.asking_from(
            window, advisor_types.PoolOrder(advisor_goals.CANONICAL_POOL_ORDER))
        if asking is None:
            return None
        cards = window.active_slots()
        try:
            open_index = [card is self._slot for card in cards].index(True)
        except ValueError:
            return None
        problem = dataclasses.replace(
            asking.request.problem,
            held=tuple(advisorbar.held_slot(index, card)
                       for index, card in enumerate(cards)
                       if index != open_index))
        request = dataclasses.replace(asking.request, problem=problem)
        known = self._track.ask_and_answer_if_known(
            request, asking.inventory, asking.ctx)
        if known is not None:
            return Asked(Ranking(known))
        self._answered = answered
        self._track.ready.connect(self._on_ready)
        self._track.failed.connect(self._on_failed)
        self._track.stopped.connect(self._on_stopped)
        return Asked(None)

    def stop_listening(self) -> None:
        """Hear nothing more. The dialog is closing, or has its answer."""
        if self._answered is None:
            return
        self._answered = None
        self._track.ready.disconnect(self._on_ready)
        self._track.failed.disconnect(self._on_failed)
        self._track.stopped.disconnect(self._on_stopped)

    def _on_ready(self, pool) -> None:
        self._deliver(Ranking(pool), "")

    def _on_failed(self, reason: str) -> None:
        self._deliver(None, reason)

    def _on_stopped(self) -> None:
        self._deliver(None, SEARCH_WAS_STOPPED)

    def _deliver(self, ranking: Ranking | None, reason: str) -> None:
        """One outcome, once: stop listening before anything is drawn."""
        answered = self._answered
        self.stop_listening()
        if answered is not None:
            answered(ranking, reason)


def advice_for(slot) -> SlotAdvice | None:
    """The advisor as this slot can reach it, or `None` for a slot on its own.

    A `RelicSlot` outside the main window -- which is every slot a test builds
    by hand -- has neither the advisor bar that holds the one goal setting nor
    the track that answers, and there is no direction to rank in without them.
    That is a state of the window and not a failure, exactly as 4.8 is.
    """
    window = slot.window()
    bar = getattr(window, "advisor_bar", None)
    track = getattr(window, "picker_advisor", None)
    if bar is None or track is None:
        return None
    return SlotAdvice(slot, bar, track)


class ValueBlock(QWidget):
    """What a relic is worth to this build, in both directions (§3.3).

    **Built with its rows already in place**, carrying `PENDING` where the
    figures go. AK-41 measures a difference of 0 px between a card before the
    figures and the same card after them, and the way to get that is to
    reserve the room rather than to add the block once there is something to
    put in it.

    Nothing here asks for width. The cards sit in a `QScrollArea` only as wide
    as the dialog, and a child that states a minimum widens **every** card
    past the viewport and puts a horizontal scrollbar under all of them -- a
    relic name with no space in it was enough to do it once already. The
    figure is therefore `Ignored` horizontally and takes the room the caption
    leaves.
    """

    def __init__(self, captions):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 0)
        layout.setSpacing(2)

        rule = QFrame()
        rule.setFrameShape(QFrame.HLine)
        rule.setFixedHeight(1)
        rule.setStyleSheet(f"border: none; background: {BORDER};")
        layout.addWidget(rule)

        self.values: list[QLabel] = []
        for caption in captions:
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(6)
            name = QLabel(caption)
            name.setTextFormat(Qt.PlainText)
            name.setStyleSheet(
                f"border: none; color: {MUTED}; font-size: 11px;")
            row.addWidget(name)
            value = QLabel(PENDING)
            value.setTextFormat(Qt.PlainText)
            value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            value.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
            value.setStyleSheet(
                "border: none; font-weight: bold; font-size: 12px;")
            row.addWidget(value, 1)
            layout.addLayout(row)
            self.values.append(value)

    def show_values(self, texts) -> None:
        """Put the figures where `PENDING` was standing."""
        for value, text in zip(self.values, texts):
            value.setText(text)


class RelicCard(QFrame):
    """One relic: its icon, name and the effects it actually rolled."""

    def __init__(self, item, effect_names: list[str], icon, selected: bool,
                 on_pick, curses: list[tuple[str, str]] | None = None,
                 tooltip: str = "", favourite: bool = False,
                 on_favourite=None, captions=()):
        super().__init__()
        self.item = item
        self.on_favourite = on_favourite
        self.setFixedWidth(CARD_WIDTH)
        self.setCursor(Qt.PointingHandCursor)
        # Selection and favourite are different questions -- "is this relic on
        # right now" and "do I want this relic on this character" -- so a card
        # can be both. Selection takes the border because it is about the slot
        # being edited; the star carries the favourite through either state.
        if selected:
            edge, width = ACCENT, 2
        elif favourite:
            edge, width = FAVOURITE, 2
        else:
            edge, width = BORDER, 1
        self.setStyleSheet(
            f"QFrame {{ background: {PANEL};"
            f" border: {width}px solid {edge};"
            f" border-radius: 6px; }}"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        header = QHBoxLayout()
        header.setSpacing(8)

        self.button = QToolButton()
        self.button.setIconSize(QSize(ICON, ICON))
        self.button.setFixedSize(ICON + 6, ICON + 6)
        self.button.setAutoRaise(True)
        self.button.setStyleSheet("border: none;")
        if icon is not None:
            self.button.setIcon(QIcon(icon))
        self.button.clicked.connect(lambda: on_pick(item))
        header.addWidget(self.button)

        if favourite:
            star = QLabel("★")
            star.setStyleSheet(
                f"border: none; color: {FAVOURITE}; font-size: 13px;")
            header.addWidget(star, 0, Qt.AlignTop)

        # The chip stands above the name, inside the header and beside the
        # icon (§3.5 point 4). It is built empty rather than added when it is
        # earned: a strip that appeared with the figures would move the name
        # down and break the 0 px of AK-41. Where the icon is the tallest
        # thing in the header -- which it is for every name shorter than four
        # lines -- reserving it costs no card height at all.
        naming = QVBoxLayout()
        naming.setContentsMargins(0, 0, 0, 0)
        naming.setSpacing(1)
        self.chip = QLabel()
        self.chip.setTextFormat(Qt.PlainText)
        self.chip.setFixedHeight(13)
        self.chip.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.chip.setStyleSheet(
            f"border: none; color: {ACCENT}; font-size: 10px;"
            f" font-weight: bold;")
        naming.addWidget(self.chip)

        title = QLabel(item.name)
        title.setWordWrap(True)
        title.setStyleSheet(
            f"border: none; font-weight: bold; "
            f"color: {ACCENT if selected else '#e4e4e4'};"
        )
        naming.addWidget(title, 1)
        header.addLayout(naming, 1)
        layout.addLayout(header)

        # First line of the card body, under the header and over the effect
        # points, told apart by the same hairline the arsenal tile uses
        # (§3.3): the figure is the reason this screen exists, so it stands
        # before what the relic rolled rather than after it.
        self.block = ValueBlock(captions)
        layout.addWidget(self.block)

        for name in effect_names:
            label = QLabel(f"• {name}")
            label.setWordWrap(True)
            label.setStyleSheet(f"border: none; color: #cfcfcf; font-size: 11px;")
            layout.addWidget(label)

        # Name the curses outright. "Comes with a curse" tells the player there
        # is a cost but not what it is, which is the one thing they need to
        # know before putting the relic on.
        for curse_name, curse_detail in (curses or []):
            label = QLabel(f"✦ {curse_name}")
            label.setWordWrap(True)
            label.setStyleSheet(f"border: none; color: {CURSE}; font-size: 11px;")
            if curse_detail:
                label.setToolTip(curse_detail)
            layout.addWidget(label)

        if not curses and item.has_curse:
            count = getattr(item, "curse_count", 0) or 0
            what = f"{count} curses" if count > 1 else "a curse"
            curse = QLabel(f"✦ comes with {what}")
            curse.setWordWrap(True)
            curse.setStyleSheet(f"border: none; color: {CURSE}; font-size: 11px;")
            layout.addWidget(curse)

        if tooltip:
            self.setToolTip(tooltip)

        layout.addStretch()

    def show_values(self, texts, chip: str = "") -> None:
        """The figures for this card, and the tie mark if it has earned one.

        Both in one call because they are one reading of one pool: a card
        whose figure said one thing and whose chip said another would be two
        answers to `UI_SPEC` §3.5.
        """
        self.block.show_values(texts)
        self.chip.setText(chip)

    def mousePressEvent(self, event):  # noqa: N802 - Qt naming
        # Right-click belongs to the favourite menu. Without this guard the
        # menu would open and the card would be picked in the same gesture,
        # closing the picker out from under it.
        if event.button() != Qt.LeftButton:
            event.ignore()
            return
        self.button.click()

    def contextMenuEvent(self, event):  # noqa: N802 - Qt naming
        if self.on_favourite is None:
            return
        self.on_favourite(self.item, event.globalPos())


class CustomRelicCard(QFrame):
    """The build-your-own tile that leads the grid.

    Everything else in the picker is a relic the player actually holds. This
    one is deliberately styled apart so it reads as a tool rather than as a
    relic that has somehow been acquired.
    """

    def __init__(self, effect_names: list[str], selected: bool, on_pick):
        super().__init__()
        self.setFixedWidth(CARD_WIDTH)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(
            f"QFrame {{ background: {PANEL};"
            f" border: 1px dashed {ACCENT if selected else MUTED};"
            f" border-radius: 6px; }}"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        header = QHBoxLayout()
        header.setSpacing(8)
        self.button = QToolButton()
        self.button.setText("+")
        self.button.setFixedSize(ICON + 6, ICON + 6)
        self.button.setAutoRaise(True)
        self.button.setStyleSheet(
            f"border: none; color: {ACCENT}; font-size: 26px;")
        self.button.clicked.connect(on_pick)
        header.addWidget(self.button)

        title = QLabel("Custom relic")
        title.setWordWrap(True)
        title.setStyleSheet(
            f"border: none; font-weight: bold;"
            f" color: {ACCENT if selected else '#e4e4e4'};"
        )
        header.addWidget(title, 1)
        layout.addLayout(header)

        if effect_names:
            for name in effect_names:
                label = QLabel(f"• {name}")
                label.setWordWrap(True)
                label.setStyleSheet(
                    "border: none; color: #cfcfcf; font-size: 11px;")
                layout.addWidget(label)
        else:
            hint = QLabel("Pick any effects that can roll in this slot, to "
                          "plan around a relic you have not found yet.")
            hint.setWordWrap(True)
            hint.setStyleSheet(f"border: none; color: {MUTED}; font-size: 11px;")
            layout.addWidget(hint)

        layout.addStretch()
        self.setToolTip("Build a hypothetical relic for this slot")

    def mousePressEvent(self, event):  # noqa: N802 - Qt naming
        self.button.click()


class FavouriteMenu(QMenu):
    """"Favourite for" — the Nightfarers, in the same 2x5 grid as the sidebar.

    The menu deliberately stays open while portraits are toggled: a relic that
    suits one character usually suits its neighbours too, and reopening the
    menu once per Nightfarer for a good roll would be tedious.
    """

    def __init__(self, parent, item, heroes: list[dict], icons):
        super().__init__(parent)
        self.item = item
        self.changed = False

        heading = QLabel("Favourite for")
        heading.setStyleSheet(
            f"color: {MUTED}; font-size: 11px; padding: 6px 8px 2px 8px;")
        title = QWidgetAction(self)
        title.setDefaultWidget(heading)
        self.addAction(title)

        holder = QWidget()
        grid = QGridLayout(holder)
        grid.setContentsMargins(8, 2, 8, 8)
        grid.setSpacing(4)
        marked = favourites.heroes_for(item)
        for i, hero in enumerate(heroes):
            grid.addWidget(
                self._tile(hero, icons, hero["id"] in marked),
                i // HERO_COLUMNS, i % HERO_COLUMNS,
            )
        body = QWidgetAction(self)
        body.setDefaultWidget(holder)
        self.addAction(body)

    def _tile(self, hero: dict, icons, checked: bool) -> QToolButton:
        button = QToolButton()
        button.setCheckable(True)
        button.setChecked(checked)
        button.setAutoRaise(True)
        button.setCursor(Qt.PointingHandCursor)
        button.setFixedSize(HERO_ICON + 8, HERO_ICON + 8)
        button.setToolTip(hero["name"])
        pixmap = icons.portrait(hero["id"]) if icons is not None else None
        if pixmap is not None:
            button.setToolButtonStyle(Qt.ToolButtonIconOnly)
            button.setIconSize(QSize(HERO_ICON, HERO_ICON))
            button.setIcon(QIcon(pixmap))
        else:
            # The DLC characters have no extractable artwork, so their tiles
            # carry initials and keep the grid the same shape either way.
            button.setText(hero["name"][:2])
        button.setStyleSheet(
            f"QToolButton {{ border: 1px solid {BORDER}; border-radius: 4px;"
            f" background: {PANEL}; color: #cfcfcf; padding: 0px; }}"
            f"QToolButton:checked {{ border: 2px solid {FAVOURITE}; }}"
        )
        button.clicked.connect(
            lambda _checked=False, h=hero, b=button: self._toggle(h, b))
        return button

    def _toggle(self, hero: dict, button: QToolButton) -> None:
        button.setChecked(favourites.toggle(self.item, hero["id"]))
        self.changed = True


class CustomRelicDialog(QDialog):
    """Choose up to three effects to make up a relic that does not exist yet."""

    MAX_EFFECTS = 3

    def __init__(self, parent, choices: list[dict], chosen: list[int]):
        super().__init__(parent)
        self.choices = choices
        self.chosen = list(chosen)[:self.MAX_EFFECTS]

        self.setWindowTitle("Custom relic")
        self.setModal(True)
        self.resize(640, 620)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        blurb = QLabel(
            f"A real relic rolls up to three effects. Only effects that can "
            f"actually appear in this slot are listed ({len(choices)} of them)."
        )
        blurb.setWordWrap(True)
        blurb.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        layout.addWidget(blurb)

        self.picked = QLabel()
        self.picked.setWordWrap(True)
        self.picked.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.picked)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Filter effects…")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self._refresh)
        layout.addWidget(self.search)

        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(self._toggle)
        layout.addWidget(self.list, 1)

        buttons = QHBoxLayout()
        add = QPushButton("Add / remove selected")
        add.clicked.connect(lambda: self._toggle(self.list.currentItem()))
        buttons.addWidget(add)
        clear = QPushButton("Clear")
        clear.clicked.connect(self._clear)
        buttons.addWidget(clear)
        buttons.addStretch()
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        buttons.addWidget(cancel)
        self.ok = QPushButton("Use this relic")
        self.ok.setDefault(True)
        self.ok.clicked.connect(self.accept)
        buttons.addWidget(self.ok)
        layout.addLayout(buttons)

        self._refresh()

    def _refresh(self) -> None:
        needle = self.search.text().strip().lower()
        self.list.clear()
        for eff in self.choices:
            label = effecttext.name(eff)
            detail = effecttext.describe_full(eff)
            if needle and needle not in f"{label} {detail}".lower():
                continue
            mark = "✓ " if eff["id"] in self.chosen else "   "
            entry = QListWidgetItem(f"{mark}{label} — {detail}")
            entry.setData(Qt.UserRole, eff["id"])
            entry.setToolTip(detail)
            self.list.addItem(entry)

        by_id = {e["id"]: e for e in self.choices}
        if self.chosen:
            names = [effecttext.name(by_id[i]) for i in self.chosen if i in by_id]
            self.picked.setText(
                f"<b>{len(self.chosen)} of {self.MAX_EFFECTS} chosen:</b> "
                + ", ".join(names))
        else:
            self.picked.setText(
                f"<b>Nothing chosen yet</b> — double-click up to "
                f"{self.MAX_EFFECTS} effects.")
        self.ok.setEnabled(bool(self.chosen))

    def _toggle(self, entry) -> None:
        if entry is None:
            return
        eid = entry.data(Qt.UserRole)
        if eid in self.chosen:
            self.chosen.remove(eid)
        elif len(self.chosen) < self.MAX_EFFECTS:
            self.chosen.append(eid)
        self._refresh()

    def _clear(self) -> None:
        self.chosen = []
        self._refresh()


class RelicPicker(QDialog):
    """Grid of the relics that fit one slot."""

    def __init__(self, slot, icons, search_text: str, on_search_changed,
                 advice=None):
        super().__init__(slot.window())
        self.slot = slot
        self.icons = icons
        self.on_search_changed = on_search_changed
        self.chosen = None
        # Where the figures and the one goal setting come from. Handed in by
        # a caller that has one (a test with a pool of its own), asked of the
        # slot otherwise, so no call site loses the figures by forgetting an
        # argument.
        self.advice = advice_for(slot) if advice is None else advice
        #: This slot's pool, once there is one. `None` covers three states
        #: that look alike and are not: the question is still out, it ended
        #: without figures, and there was never anything to ask. `_waiting`
        #: and `_failure` are what tell them apart.
        self.ranking = None
        #: Whether the answer to this opening's one question is still out.
        self._waiting = False
        #: Why there are no figures, in the track's own words -- empty unless
        #: the question failed or was stopped (AK-208, AK-218).
        self._failure = ""
        #: Whether the first paint had cards to wait for. AK-212 excepts the
        #: opening that offers no relic at all -- a slot nothing fits, or a
        #: filter that was already typed and matches nothing: there is
        #: nothing to order and nothing to value, so the dialog draws once
        #: and says nothing about waiting. Decided at the first paint and not
        #: at every one, because a filter typed *during* the wait leaves the
        #: line standing (§3, the named edge case) rather than making the
        #: dialog change its mind about what state it is in.
        self._wait_is_drawn = None
        asked = None if self.advice is None else self.advice.ask(
            self._the_answer_arrived)
        if asked is not None:
            self.ranking = asked.ranking
            self._waiting = asked.ranking is None
        # Favourites are per Nightfarer, so the picker has to know which one
        # the build is for. A slot outside the main window simply has none.
        window = slot.window()
        current = getattr(window, "current_hero", None)
        hero = current() if callable(current) else None
        self.hero_id = hero["id"] if hero else None
        self.hero_label = hero["name"] if hero else ""

        colour = model.COLOUR_NAMES.get(slot.colour, slot.colour)
        self.setWindowTitle(
            f"{'Deep ' if slot.deep else ''}Slot {slot.index + 1} — {colour}"
        )
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)
        layout.setSpacing(10)

        top = QHBoxLayout()
        chip = QLabel()
        chip.setFixedSize(16, 16)
        chip.setStyleSheet(
            f"background: {SLOT_COLOURS.get(slot.colour, '#888')};"
            f" border: 1px solid {BORDER}; border-radius: 8px;"
        )
        top.addWidget(chip)

        self.search = QLineEdit(search_text)
        self.search.setPlaceholderText("Filter by effect…")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self._refresh)
        top.addWidget(self.search, 1)

        clear = QPushButton("Empty slot")
        clear.clicked.connect(lambda: self._pick(None))
        top.addWidget(clear)
        layout.addLayout(top)

        # §3.4. The two directions carry the registry's own labels, because
        # they are the registry's own directions: `Sort by` here and the
        # advisor bar's box are **one** setting seen from two screens, and a
        # second list of words would be a second place for them to differ.
        sorting = QHBoxLayout()
        sorting.setSpacing(6)
        caption = QLabel("Sort by")
        caption.setTextFormat(Qt.PlainText)
        sorting.addWidget(caption)
        self.sort_box = QComboBox()
        self.sort_box.setMaximumWidth(SORT_BOX_WIDTH)
        for goal_id in VALUE_DIRECTIONS:
            self.sort_box.addItem(advisor_goals.GOALS[goal_id].label, goal_id)
        self.sort_box.addItem(NAME_ORDER_LABEL, NAME_ORDER)
        standing = (advisorbar.GOAL_ORDER[0] if self.advice is None
                    else self.advice.goal_id())
        self.sort_box.setCurrentIndex(self.sort_box.findData(standing))
        self.sort_box.activated.connect(self._sort_chosen)
        sorting.addWidget(self.sort_box)
        sorting.addStretch()
        layout.addLayout(sorting)
        # AK-52: between the filter field and the cards, which is where a
        # reader arrives at it after typing what they are looking for.
        self.setTabOrder(self.search, self.sort_box)

        # The one sentence that replaces a tie mark no card may wear (§3.5
        # point 5, §3.7). Outside the scroll area with the other lines, and
        # wrapped rather than shortened: AK-50 lets none of them be cut.
        self.headline = QLabel()
        self.headline.setTextFormat(Qt.PlainText)
        self.headline.setWordWrap(True)
        self.headline.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
        self.headline.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        self.headline.setVisible(False)
        layout.addWidget(self.headline)

        self.summary = QLabel()
        self.summary.setTextFormat(Qt.PlainText)
        self.summary.setWordWrap(True)
        self.summary.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
        self.summary.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        layout.addWidget(self.summary)

        # Line 3b: what this run could not consider, in the player's language
        # (AK-163). Two sources, drawn in the order they were handed over and
        # neither compared, filtered nor de-duplicated -- a sentence that
        # appears twice is a fault of the calculation and is meant to be seen
        # (AK-165).
        self.findings = QLabel()
        self.findings.setTextFormat(Qt.PlainText)
        self.findings.setWordWrap(True)
        self.findings.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
        self.findings.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        self.findings.setVisible(False)
        layout.addWidget(self.findings)

        # Line 4: the mandatory line, then what the chosen direction cannot
        # know whatever the run (AK-162). Not one word of it is written here
        # -- the reservations live in `Goal.scope`, so a sixth sentence added
        # to the registry stands here without this file being touched.
        self.caveats = QLabel()
        self.caveats.setTextFormat(Qt.PlainText)
        self.caveats.setWordWrap(True)
        self.caveats.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
        self.caveats.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        self.caveats.setVisible(False)
        layout.addWidget(self.caveats)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        layout.addWidget(self.scroll, 1)

        # After the scroll area, because the opening width has to account for
        # the vertical scrollbar the card list will need: with 55 cards it is
        # always there, and the width it takes came off the last column. The
        # height follows in `_refresh`, which is where the cards exist.
        #: Whether the opening size has been fitted to the cards yet.
        self._sized = False
        self.resize(self._opening_width(), OPENING_HEIGHT)

        self._refresh()

    @property
    def waiting(self) -> bool:
        """Whether this opening's one question is still out (§3.8).

        Public because it is the state the display is in, and a caller that
        wants the figures -- a case measuring a card, a reader of this file --
        has no other way to tell "the answer is not here yet" from "there is
        nothing to rank against", which look identical on screen.
        """
        return self._waiting

    def _opening_width(self) -> int:
        """A width at which `OPENING_COLUMNS` whole cards fit the viewport.

        Everything between the dialog edge and the card area is added back:
        the layout margin on both sides and the vertical scrollbar. Asking the
        scrollbar rather than assuming a figure is what makes this hold under
        a style whose scrollbars are not the width this machine's are.
        """
        return (cardgrid.room_for(OPENING_COLUMNS, CARD_WIDTH)
                + 2 * MARGIN
                + self.scroll.verticalScrollBar().sizeHint().width())

    def _chrome_height(self) -> int:
        """Everything of the dialog that is not the card area.

        Read off the layout rather than counted by hand, so a line added
        above the grid moves this figure by itself. A wrapping label is asked
        `heightForWidth` at the width it will really have: its `sizeHint` is
        the height of one long line, which is not a height this dialog ever
        gives it.
        """
        layout = self.layout()
        margins = layout.contentsMargins()
        room = self.width() - margins.left() - margins.right()
        total = (margins.top() + margins.bottom()
                 + layout.spacing() * (layout.count() - 1))
        for index in range(layout.count()):
            item = layout.itemAt(index)
            widget = item.widget()
            if widget is self.scroll:
                continue
            if widget is not None and not widget.isVisibleTo(self):
                continue
            total += _asked_height(widget, room, item.sizeHint().height())
        return total

    def _room_for_three_rows(self, cards) -> int:
        """What the first `MINIMUM_ROWS` rows of these cards need, in px.

        The same arithmetic the grid will do at the opening width -- as many
        cards to a row as `OPENING_COLUMNS`, each row as tall as the tallest
        card in it -- so the dialog and the reflow cannot part company again
        (QA-141 was that parting, on the other axis).

        `heightForWidth` and not `sizeHint`: every card wraps its name, its
        effects and its curses, and a wrapped label's `sizeHint` is the one
        long line it would rather have. Measured offscreen at 190 px cards on
        this save, the difference between the two readings is up to 104 px on
        a single card -- which is most of a row.
        """
        heights = [_asked_height(card, CARD_WIDTH, 0) for card in cards]
        rows = [max(heights[start:start + OPENING_COLUMNS])
                for start in range(0, len(heights), OPENING_COLUMNS)]
        rows = rows[:MINIMUM_ROWS]
        return sum(rows) + max(0, len(rows) - 1) * cardgrid.SPACING

    def wanted_height(self, cards) -> int:
        """The height AK-51 asks for, before any screen is consulted.

        Kept apart from what the dialog ends up at, because the two are
        different statements and only the first is about this program: a
        desktop that cannot hold the dialog is a fact about the desktop. It
        is also the only one a case can read -- the offscreen desktop is
        800 px tall, so a guard written on the size the dialog *reaches*
        would agree with itself whatever this file said.
        """
        return self._chrome_height() + self._room_for_three_rows(cards)

    def _fit_to_three_rows(self, cards) -> None:
        """Open tall enough to read three whole rows of cards (AK-51).

        AK-51 says which way this goes: the dialog grows, the content is
        never cut. Only at opening -- a player who has dragged the dialog to
        a size of their own is not corrected by the next keystroke in the
        filter.

        Bounded by the desktop, because a dialog taller than the screen is
        one whose bottom row cannot be read at all. Measured on this machine
        2026-09-07: AK-51 asks for 1122 px against 1027 available, so the
        three rows are 95 px short of fitting and the picker opens as tall as
        the desktop allows. That shortfall is reported, not hidden.
        """
        if self._sized or not cards:
            return
        self._sized = True
        wanted = self.wanted_height(cards)
        screen = self.screen()
        if screen is not None:
            wanted = min(wanted, screen.availableGeometry().height())
        if wanted > self.height():
            self.resize(self.width(), wanted)

    def _candidates(self):
        from . import search

        text = self.search.text()
        predicate = search.parse(text)
        # The slot decides what it can hold -- one card per roll, and nothing
        # that is already lying in another slot. Asking the inventory here as
        # well is how the picker came to offer a relic the slot beside it was
        # already wearing (QA-002); the count below is drawn from the same
        # answer, so the grid and the "x of y" above it cannot disagree.
        items = self.slot.available_items()
        if predicate is not None:
            items = [i for i in items if predicate(self.slot.effect_names(i))]
        # Favourites for the Nightfarer currently being planned lead the grid.
        # sorted() is stable, so everything else keeps the name order it had.
        if self.hero_id is not None:
            items = sorted(
                items,
                key=lambda i: 0 if favourites.is_favourite(i, self.hero_id) else 1,
            )
        # In the order the grid has without an advisor at all -- favourites,
        # then name. `_refresh` puts the answer's order on top of it, and
        # keeps this one, because the dialog measures itself against it
        # (AK-216).
        return items, text.strip()

    def _in_the_chosen_order(self, items):
        """`items` as `Sort by` asks for them (§3.4, AK-44, AK-195).

        **Stable, on top of the order the grid would have anyway.** Two
        candidates inside one segment of a piecewise-linear curve are worth
        exactly the same, so ties are the common case rather than the
        exception; where the figure cannot decide, the order the player knows
        does -- favourites first, then name. Twice the same state is twice the
        same list, and no ordinal is ever drawn to suggest otherwise.

        A copy the pool does not carry has no place in a value order and goes
        to the end, keeping the order it had among its own kind.

        **AK-195: the chip-bearing cards of both directions lead, ahead of
        the value order** -- the sorted direction's first, then the other
        direction's, each in the favourite/name order `items` already
        carries rather than by value: a real tie among them has no order the
        figure decided, and AK-44 forbids inventing one. The set for each
        direction is `Ranking.top_handles`, read once and not recomputed
        (Vorgaben point 1); a card the filter already dropped from `items`
        cannot be promoted, so a hidden top pick gets no substitute
        (Vorgaben point 3). `Sort by` = `Name` promotes nothing at all.
        """
        if self.sort_box.currentData() == NAME_ORDER or self.ranking is None:
            return items
        goal_id = self._drawn_direction()
        other_id = next(g for g in VALUE_DIRECTIONS if g != goal_id)

        def worth(item):
            gain = self.ranking.gain(item, goal_id)
            return (1, 0.0) if gain is None else (0, -gain)

        by_value = sorted(items, key=worth)

        leading = self.ranking.top_handles(goal_id)
        trailing = self.ranking.top_handles(other_id) - leading

        def handle_of(item):
            return getattr(item, "handle", None)

        first = [item for item in items if handle_of(item) in leading]
        second = [item for item in items if handle_of(item) in trailing]
        rest = [item for item in by_value
                if handle_of(item) not in leading and handle_of(item) not in trailing]
        return first + second + rest

    def _drawn_direction(self) -> str:
        """The direction the value rows, chips and sentences are in (AK-205).

        The one goal setting of the program (AK-43), and **never**
        `SlotPool.rank_by`: since Nachtrag IX-2 the picker asks under one
        fixed direction whatever the player has chosen, so the direction that
        ordered the list says nothing about the direction being read. The two
        agreed most of the time before, which is worse than never: a fault
        that shows up sometimes is one nobody catches.
        """
        return self.advice.goal_id()

    def _heroes(self) -> list[dict]:
        return getattr(self.slot.window(), "heroes", None) or []

    def _open_favourites(self, item, position) -> None:
        heroes = self._heroes()
        if not heroes:
            return
        menu = FavouriteMenu(self, item, heroes, self.icons)
        # Refreshing while the menu is open would delete the card it is
        # anchored to, so the grid is rebuilt only once the menu has closed.
        menu.exec(position)
        if menu.changed:
            self._refresh()

    def _curses(self, item) -> list[tuple[str, str]]:
        """(name, full description) for each curse this relic actually rolled."""
        out = []
        for cid in getattr(item, "curse_ids", ()) or ():
            eff = self.slot.effect_by_id.get(cid)
            if eff is None:
                out.append((f"<{cid}>", ""))
            else:
                out.append((effecttext.name(eff), effecttext.describe_full(eff)))
        return out

    def _card_for(self, item, current):
        """One relic's card, with everything but its figures on it."""
        icon = self.icons.item(item.icon) if item.icon else None
        return RelicCard(
            item,
            self.slot.effect_names(item),
            icon,
            selected=current is not None and current.relic_id == item.relic_id
            and current.effect_ids == item.effect_ids,
            on_pick=self._pick,
            curses=self._curses(item),
            tooltip=self.slot.curse_tooltip(item),
            favourite=self.hero_id is not None
            and favourites.is_favourite(item, self.hero_id),
            on_favourite=self._open_favourites,
            captions=self._captions(),
        )

    def _waiting_area(self) -> QWidget:
        """The scroll area's content while the question is out (AK-212).

        No card, not even the custom tile: a single tile in an otherwise
        empty area looks more like a fault than the empty area does, and in
        a third of a second nobody reaches for the fallback. One line, at the
        origin of the grid's content, so that the first card lands where the
        line stood and the eye moves by nothing.
        """
        holder = QWidget()
        layout = QVBoxLayout(holder)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        line = QLabel(NOTHING_YET)
        line.setTextFormat(Qt.PlainText)
        line.setWordWrap(True)
        line.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        layout.addWidget(line)
        return holder

    def _refresh(self) -> None:
        plain, needle = self._candidates()
        items = self._in_the_chosen_order(plain)
        if self._wait_is_drawn is None:
            self._wait_is_drawn = self._waiting and bool(plain)
        waiting = self._waiting and self._wait_is_drawn
        total = len(self.slot.available_items())
        starred = sum(
            1 for i in items
            if self.hero_id is not None and favourites.is_favourite(i, self.hero_id)
        )
        note = f" — {starred} favourited for {self.hero_label}" if starred else ""
        # The reference size, without which `+12.4` says nothing: the figures
        # are measured against the build as it stands with **this** slot
        # emptied -- including for the relic that is sitting in it right now
        # (AD-018.1).
        against = (f"  ·  ranked against your build with "
                   f"{self.slot.slot_name()} empty"
                   if self.ranking is not None else "")
        self.summary.setText(
            working_out(self.slot.slot_name()) if waiting else
            f"{len(items)} of {total} relics"
            + (f" matching “{needle}”" if needle else "")
            + note
            + against
            + "  ·  right-click a relic to favourite it"
        )
        self._say_what_was_left_out()

        current = self.slot.relic_box.currentData()

        # The custom tile always leads, and is never filtered out -- it is the
        # answer to "none of these are what I want", so hiding it behind a
        # search that matched nothing would remove it exactly when it is needed.
        custom = getattr(self.slot, "custom_item", None)
        tile = CustomRelicCard(
            self.slot.effect_names(custom) if custom is not None else [],
            selected=current is not None
            and getattr(current, "relic_id", None) == CUSTOM_RELIC_ID,
            on_pick=self._open_custom,
        )
        # Built once, in the order the grid has without an answer, and read
        # in two orders: the one the grid shows and the one the dialog
        # measures itself in (AK-216). Two builds of the same cards would be
        # the one place this state costs real time, and it would be paid
        # unseen.
        by_item = {id(item): self._card_for(item, current) for item in plain}
        for_size: list[QWidget] = [tile] + [by_item[id(item)]
                                            for item in plain]

        if waiting:
            # The cards are built and measured, and simply not shown (§4):
            # what fits the slot and how tall a card is at 190 px has nothing
            # to do with the advisor, so the dialog can take its final size
            # at the first paint and never grow under the player's hands.
            self._headline("")
            self.scroll.setWidget(self._waiting_area())
            self._fit_to_three_rows(for_size)
            return

        relic_cards = [(item, by_item[id(item)]) for item in items]
        self._say_what_they_are_worth(relic_cards)

        # As many columns as the dialog is actually wide, not five whatever it
        # is wide. Five fixed ones put the last column past the right-hand
        # edge at the size the dialog opens at, and dragging it narrower moved
        # nothing: eleven of fifty-five cards were sliced at 1 030 px and the
        # same eleven lost 142 of their 190 px at 900, names ending mid-word
        # (QA-141, DR-016a at a place T-058 left out).
        self.scroll.setWidget(cardgrid.CardGrid(
            CARD_WIDTH, [tile] + [card for _item, card in relic_cards]))
        self._fit_to_three_rows(for_size)

    def _the_answer_arrived(self, ranking, reason: str) -> None:
        """The one answer of this opening, whichever of the three it is.

        `ready`, `failed` and `stopped` all end here and all fill the grid
        (AK-218): under this design an unhandled outcome is not a grid without
        figures but a dialog in which no relic can be chosen at all. One
        `_refresh` for all of it, because everything that hangs on the answer
        -- the cards, both value rows, the chips, the order, the header and
        the run findings -- appears in one paint or the grid moves twice
        (AK-211).
        """
        self._waiting = False
        self.ranking = ranking
        self._failure = reason
        self._refresh()

    def done(self, result: int) -> None:  # noqa: N802 - Qt naming
        """Hear nothing more from the track, whatever closed the dialog.

        The track outlives this dialog (AD-028 point 5), so an answer may
        arrive after it has gone. It is dropped twice over -- the counter in
        the controller has moved on, and nothing here is listening any more --
        because one of the two would be a guard nobody could see fail
        (AK-207).
        """
        if self.advice is not None:
            self.advice.stop_listening()
        super().done(result)

    def _sort_chosen(self, _index: int) -> None:
        """The player picked an order, and a direction with it (AK-43).

        A direction chosen here is chosen everywhere: it goes to the one
        setting the program has. **Nothing is asked again** (Nachtrag IX-0,
        AK-204, AK-206): a pool measures every candidate under every
        direction, so the answer already on screen serves the other direction
        too, and only its order and what is drawn from it change. Asking
        again cost a measured 318,1 ms in the middle of an interaction and
        answered with the same figures. `Name` is not a direction and changes
        none: it is a way of looking at the same figures.
        """
        chosen = self.sort_box.currentData()
        if chosen != NAME_ORDER and self.advice is not None:
            self.advice.choose_goal(chosen)
        self._refresh()

    def _captions(self) -> list[str]:
        """The value rows every card carries, in order (AK-42)."""
        return [VALUE_CAPTIONS[goal_id] for goal_id in VALUE_DIRECTIONS]

    def _say_what_they_are_worth(self, pairs) -> None:
        """Put the pool's figures on the cards, and the tie mark where it is
        earned.

        **The mark is decided on the text, not on the float** (AK-45): two
        cards showing `+12.4` carry the same mark whatever their unrounded
        gains are, because the worst thing this screen could do is show two
        equal numbers of which only one is marked. `Ranking.top_handles` is
        the one place that decision is made -- `_in_the_chosen_order` reads
        the very same set to promote these cards to the top of the grid
        (AK-195, T-094 Vorgaben point 1).

        With no ranking every card says `—` (AK-49). Not `0`, and not an
        empty row: the block stands either way, so the card is the same
        height, and what it says is that nothing was measured.

        **Two ways to have no ranking, two headers** (AK-208, AK-218). One is
        that there is nothing to rank against -- no save, or a direction the
        game's data carries no figures for -- and the AK-49 sentence says so.
        The other is that the question ended without an answer, and then the
        header names the reason the track gave: the AK-49 sentence would be a
        statement about the game's data that nothing measured (A7).
        """
        if self.ranking is None:
            for _item, card in pairs:
                card.show_values([NO_FIGURE] * len(VALUE_DIRECTIONS))
            self._headline(could_not_work_out(self._failure) if self._failure
                           else NO_FIGURES_AT_ALL)
            return

        goal_id = self._drawn_direction()
        top = self.ranking.top_handles(goal_id)
        # Twenty cards marked `BEST FOR DAMAGE` at a top value of nothing
        # would be a lie in bold (§3.5 point 5). The header says it once
        # instead, and no card is marked.
        for item, card in pairs:
            card.show_values(
                self.ranking.texts_for(item),
                chip_text(goal_id) if getattr(item, "handle", None) in top else "")
        self._headline("" if top else nothing_raises(goal_id))

    def _say_what_was_left_out(self) -> None:
        """Lines 3b and 4, the two halves of what this figure cannot know.

        **Two sources, two places, and neither is edited** (AD-025, AK-165):
        the run findings belong to *this* pool and stand at the pool summary;
        the procedural sentences belong to the direction and stand once,
        below. Nothing here compares the two lists, sorts them or drops a
        repeat -- a sentence in both classes is a fault of the calculation
        (checkpoint 30), and an display that de-duplicated would hide exactly
        the fault the checkpoint is written against.

        `weights_note` is in neither (AK-166). While there is no control for
        the weighting, `EVEN_WEIGHTING.note` opens with the same eight words
        as the second `Goal.scope` sentence of the survival direction, and
        two lines under each other that begin alike are read as one repeat
        and skipped. It stands in the `Why` dialog instead.

        **Neither of them waits for the answer** (AK-201). The mandatory line
        and the direction's `scope` sentences are true before any run and
        stand from the first paint; only the run findings (3b) belong to a
        pool and wait for one. That is a promise about reading, and it is
        also what lets the dialog measure itself at the first paint:
        `_chrome_height` skips what is not visible, so a line that appeared
        with the answer would be a line the opening size did not include.
        """
        if self.advice is None:
            self.findings.setVisible(False)
            self.caveats.setVisible(False)
            return
        goal_id = self._drawn_direction()
        found = []
        if self.ranking is not None:
            pool = self.ranking.pool
            found = [line
                     for baseline in pool.baseline
                     if baseline.goal_id == goal_id
                     for line in baseline.unknowns] + list(pool.unknowns)
        self.findings.setText(advisorbar.CLAUSES.join(found))
        self.findings.setVisible(bool(found))

        scope = advisor_goals.GOALS[goal_id].scope
        self.caveats.setText(" ".join((ONE_SLOT_AT_A_TIME, *scope)))
        self.caveats.setVisible(True)

    def _headline(self, text: str) -> None:
        """The one sentence that stands in for a mark nobody may wear."""
        self.headline.setText(text)
        self.headline.setVisible(bool(text))

    def _open_custom(self) -> None:
        existing = getattr(self.slot, "custom_item", None)
        dialog = CustomRelicDialog(
            self,
            self.slot.rollable_effects(),
            list(existing.effect_ids) if existing is not None else [],
        )
        if not dialog.exec():
            return
        self.slot.set_custom(dialog.chosen)
        self.chosen = self.slot.custom_item
        self.on_search_changed(self.search.text())
        self.accept()

    def _pick(self, item) -> None:
        self.chosen = item
        self.on_search_changed(self.search.text())
        self.accept()
