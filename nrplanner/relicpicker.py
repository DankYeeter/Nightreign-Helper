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
from .advisor import candidates as advisor_candidates
from .advisor import goals as advisor_goals
from .advisor import run as advisor_run
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
    """

    def __init__(self, pool: advisor_types.SlotPool) -> None:
        self.pool = pool
        self._by_handle = {candidate.handle: candidate
                           for candidate in pool.candidates}

    @property
    def goal_id(self) -> str:
        """The direction this pool was put in order by (`SlotPool.rank_by`)."""
        return self.pool.rank_by

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

    def best_text(self, goal_id: str) -> str | None:
        """The top figure of the whole pool as a card would show it.

        **Of the pool, not of what a filter left on screen.** The mark is the
        answer to "is this the best you own here", and a mark that moved as
        the player typed would answer a different question with every
        keystroke. `None` when the pool is empty -- nothing fits this slot,
        which the header then says once.
        """
        gains = [advisor_types.marginal_for(candidate, goal_id)
                 for candidate in self.pool.candidates]
        return gain_text(max(gains), self.unit(goal_id)) if gains else None

    def texts_for(self, item) -> list[str]:
        """The value rows of one card, both directions, in order."""
        rows = []
        for goal_id in VALUE_DIRECTIONS:
            gain = self.gain(item, goal_id)
            rows.append(NO_FIGURE if gain is None
                        else gain_text(gain, self.unit(goal_id)))
        return rows


class SlotAdvice:
    """Where the picker's figures and its one goal setting come from.

    **There is one goal setting in the program** (AK-43). It lives in the
    advisor bar's combo box, and this object is how the picker reads and
    writes it: a `Sort by` with a setting of its own would be a fourth place
    that can disagree with the other three.

    The pool is computed here, in the calling thread, and that is deliberate:
    AD-018 measures the worst slot at ~51 ms against the 250 ms of AK-09, so
    there is nothing to draw a wait for (§3.8). Because the dialog is modal
    and the computation returns before it opens, no base state can change
    underneath a running one -- which is why AD-006.3's generation counter has
    nothing to guard here and no second one is kept.
    """

    def __init__(self, slot, bar) -> None:
        self._slot = slot
        self._bar = bar

    def goal_id(self) -> str:
        """The direction the whole program is standing on."""
        return self._bar.goal_id()

    def choose_goal(self, goal_id: str) -> None:
        """Stand on another direction, everywhere at once (AK-43)."""
        self._bar.choose_goal(goal_id)

    def ranking(self, goal_id: str) -> Ranking | None:
        """This slot's pool under one direction, or `None`.

        `None` is "there is nothing to rank against" -- no save, so no
        inventory and no build. The picker then shows what AK-49 asks for
        rather than a figure it made up.

        **Every other slot is held, held by the player or not** (AD-018.1):
        the question here is what fits *this* slot beside the build as it
        stands, so the rest of the build is a boundary condition.
        `candidates.pool` lifts the hold on this one slot itself, which is
        what makes the relic already sitting in it comparable with the ones
        that might replace it.
        """
        window = self._slot.window()
        asking = advisorbar.asking_from(window, goal_id)
        if asking is None:
            return None
        cards = window.active_slots()
        try:
            slot_index = [card is self._slot for card in cards].index(True)
        except ValueError:
            return None
        problem = dataclasses.replace(
            asking.request.problem,
            held=tuple(advisorbar.held_slot(index, card)
                       for index, card in enumerate(cards)))
        # The same reading the run takes, so the picker and `Optimize` are
        # looking at one inventory rather than at two readings of it.
        frozen = advisor_run.frozen_inventory(asking.inventory, problem)
        return Ranking(advisor_candidates.pool(
            frozen, problem, slot_index, asking.ctx, advisor_goals.GOALS,
            goal_id))


def advice_for(slot) -> SlotAdvice | None:
    """The advisor as this slot can reach it, or `None` for a slot on its own.

    A `RelicSlot` outside the main window -- which is every slot a test builds
    by hand -- has no advisor bar and therefore no direction to rank in. That
    is a state of the window and not a failure, exactly as 4.8 is.
    """
    bar = getattr(slot.window(), "advisor_bar", None)
    return None if bar is None else SlotAdvice(slot, bar)


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
        self.ranking = (None if self.advice is None
                        else self.advice.ranking(self.advice.goal_id()))
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
        return self._in_the_chosen_order(items), text.strip()

    def _in_the_chosen_order(self, items):
        """`items` as `Sort by` asks for them (§3.4, AK-44).

        **Stable, on top of the order the grid would have anyway.** Two
        candidates inside one segment of a piecewise-linear curve are worth
        exactly the same, so ties are the common case rather than the
        exception; where the figure cannot decide, the order the player knows
        does -- favourites first, then name. Twice the same state is twice the
        same list, and no ordinal is ever drawn to suggest otherwise.

        A copy the pool does not carry has no place in a value order and goes
        to the end, keeping the order it had among its own kind.
        """
        if self.sort_box.currentData() == NAME_ORDER or self.ranking is None:
            return items
        goal_id = self.ranking.goal_id

        def worth(item):
            gain = self.ranking.gain(item, goal_id)
            return (1, 0.0) if gain is None else (0, -gain)

        return sorted(items, key=worth)

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

    def _refresh(self) -> None:
        items, needle = self._candidates()
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
        cards: list[QWidget] = [
            CustomRelicCard(
                self.slot.effect_names(custom) if custom is not None else [],
                selected=current is not None
                and getattr(current, "relic_id", None) == CUSTOM_RELIC_ID,
                on_pick=self._open_custom,
            )
        ]

        relic_cards = []
        for item in items:
            icon = self.icons.item(item.icon) if item.icon else None
            card = RelicCard(
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
            cards.append(card)
            relic_cards.append((item, card))
        self._say_what_they_are_worth(relic_cards)

        # As many columns as the dialog is actually wide, not five whatever it
        # is wide. Five fixed ones put the last column past the right-hand
        # edge at the size the dialog opens at, and dragging it narrower moved
        # nothing: eleven of fifty-five cards were sliced at 1 030 px and the
        # same eleven lost 142 of their 190 px at 900, names ending mid-word
        # (QA-141, DR-016a at a place T-058 left out).
        self.scroll.setWidget(cardgrid.CardGrid(CARD_WIDTH, cards))
        self._fit_to_three_rows(cards)

    def _sort_chosen(self, _index: int) -> None:
        """The player picked an order, and a direction with it (AK-43).

        A direction chosen here is chosen everywhere: it goes to the one
        setting the program has, and the pool is asked again, because a pool
        ranked one way and read another is the fault `SlotPool.rank_by`
        exists against. `Name` is not a direction and changes none: it is a
        way of looking at the same figures.
        """
        chosen = self.sort_box.currentData()
        if chosen != NAME_ORDER and self.advice is not None:
            self.advice.choose_goal(chosen)
            self.ranking = self.advice.ranking(chosen)
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
        equal numbers of which only one is marked.

        With no ranking every card says `—` (AK-49). Not `0`, and not an
        empty row: the block stands either way, so the card is the same
        height, and what it says is that nothing was measured.
        """
        if self.ranking is None:
            for _item, card in pairs:
                card.show_values([NO_FIGURE] * len(VALUE_DIRECTIONS))
            self._headline(NO_FIGURES_AT_ALL)
            return

        goal_id = self.ranking.goal_id
        column = VALUE_DIRECTIONS.index(goal_id)
        rows = [(card, self.ranking.texts_for(item)) for item, card in pairs]
        best = self.ranking.best_text(goal_id)
        # Twenty cards marked `BEST FOR DAMAGE` at a top value of nothing
        # would be a lie in bold (§3.5 point 5). The header says it once
        # instead, and no card is marked.
        marked = best is not None and not (best == NO_CHANGE
                                           or best.startswith("-"))
        for card, texts in rows:
            card.show_values(
                texts,
                chip_text(goal_id) if marked and texts[column] == best else "")
        self._headline("" if marked else nothing_raises(goal_id))

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
        """
        if self.ranking is None:
            self.findings.setVisible(False)
            self.caveats.setVisible(False)
            return
        pool = self.ranking.pool
        goal_id = self.ranking.goal_id
        found = [line
                 for baseline in pool.baseline if baseline.goal_id == goal_id
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
