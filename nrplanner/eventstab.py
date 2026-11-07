"""World events, written for the player who meets one mid-run.

Each event is one page: a header with the event's own symbol and the banner
the game puts on screen, a row of number tiles, where it can appear (one bar
per Nightlord), what happens, every banner the event can end on, and the two
outcomes side by side -- WIN on the left, LOSE on the right. The figures come
out of the game's own data and the prose comes from the community
(`eventlore`); both read alike on screen (GOAL.md non-goals). Everything about
*how* any of it was derived stays in the project's documents -- none of it
belongs on screen.

Long explanations sit in tooltips; the page itself shows symbols, bars and
numbers with a short legend (user preference, 2026-11-07). `tests/tabtext`
counts tooltips as displayed text, so a sentence moved there is still on the
tab.
"""

from __future__ import annotations

import html
import re

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)

from . import iconpack, tabheader
from .eventlore import LORE, UNANNOUNCED
from .theme import ACCENT, BORDER, GOOD, MUTED, PANEL

DLC = "#9a6fc4"
UNKNOWN = "#7d6f52"
PENALTY = "#c07a6a"
DAY1 = "#c8a45c"
DAY2 = "#6f8fc4"

#: Symbol sizes on this tab, in logical pixels.
LIST_ICON = 24
HEADER_ICON = 56
EFFECT_ICON = 32
ROW_ICON = 20

#: How many drops of one kind stand open before "Show N more" takes over.
DROPS_OPEN = 6

#: The drop kinds the extractor writes, in the order and wording shown.
DROP_KINDS = (("power", "Dormant Powers"), ("talisman", "Talismans"),
              ("weapon", "Weapons"), ("item", "Items"))

#: A placeholder the game fills with the player's name symbol at runtime.
CODENAME = "<?codenameIcon?>"

#: Figures whose reference quantity is not in the files, keyed by the exact
#: prefix `nrdata.extract._buff_lines` writes them with (AK-70, A7). Naming
#: the prefix rather than the whole line keeps the entry valid when the
#: magnitude changes, which is the only part of the line that can.
UNKNOWN_REFERENCE = {
    "stamina recovery speed ": (
        "The stamina recovery figure is the game's own number for that "
        "field. The files do not say what it is counted in, so read it as "
        "\"recovers faster\" and not as an amount per second."),
}

#: AK-102: what a Nightlord's percentage is a share of, and the ground the
#: "never" is asserted over. Shown in full as the tooltip of the short legend.
NEVER_SCOPE = ("Every other Nightlord: never — across every map pattern in "
               "the game's data.")
PERCENTAGE_SCOPE = (
    "The percentage is how much of that Nightlord's map pool carries the "
    "event. The pool is drawn with weights, so it is not the chance of "
    "seeing it on a given run.")
WHERE_LEGEND = "▸ % = share of that Nightlord's map pool   ▸ not listed = never"


# -- small building blocks ------------------------------------------------

def _prose(text: str) -> QLabel:
    label = QLabel(text)
    label.setWordWrap(True)
    label.setStyleSheet("color: #d8d8d8; font-size: 12px;")
    return label


def _muted(text: str, size: int = 11) -> QLabel:
    label = QLabel(text)
    label.setWordWrap(True)
    label.setStyleSheet(f"color: {MUTED}; font-size: {size}px;")
    return label


def _marked(tag: str, text: str) -> str:
    """Game text after a symbol. The `<img>` turns the label into rich text,
    where the text is markup unless it is escaped (SEC-021)."""
    return tag + html.escape(text, quote=False) if tag else text


def _stat(text: str, colour: str = "#e8dcc0") -> QLabel:
    """A figure read from the game's data -- same weight as the game's own
    wording, so it is not tinted."""
    label = QLabel("▸  " + text)
    label.setWordWrap(True)
    label.setTextFormat(Qt.PlainText)
    label.setStyleSheet(f"color: {colour}; font-size: 12px;")
    return label


def _chip(text: str, colour: str, tooltip: str = "") -> QLabel:
    """A short tag: a duration, a day, a kind of drop."""
    label = QLabel(text)
    label.setTextFormat(Qt.PlainText)
    label.setStyleSheet(
        f"color: {colour}; background: rgba(255, 255, 255, 18);"
        f" border: 1px solid {colour}; border-radius: 9px;"
        " padding: 1px 8px; font-size: 11px;")
    label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
    if tooltip:
        label.setToolTip(tooltip)
    return label


def _chips(*labels: QLabel) -> QHBoxLayout:
    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(6)
    for label in labels:
        row.addWidget(label)
    row.addStretch(1)
    return row


def _symbol(pixmap, size: int) -> QLabel | None:
    return iconpack.symbol_label(pixmap, size) if pixmap is not None else None


def _glyph(text: str, colour: str, size: int) -> QLabel:
    """A round stand-in where the game has no symbol for the thing."""
    label = QLabel(text)
    label.setAlignment(Qt.AlignCenter)
    label.setFixedSize(size, size)
    label.setStyleSheet(
        f"color: {colour}; background: {PANEL}; border: 2px solid {colour};"
        f" border-radius: {size // 2}px; font-size: {size // 2}px;"
        " font-weight: bold;")
    return label


def _section(text: str) -> QLabel:
    label = QLabel(text)
    label.setStyleSheet(
        f"color: {ACCENT}; font-size: 11px; font-weight: bold;"
        " letter-spacing: 1px; margin-top: 4px;")
    return label


def _card(colour: str) -> tuple[QFrame, QVBoxLayout]:
    """A panel with a coloured top edge: WIN, LOSE, a header."""
    frame = QFrame()
    frame.setObjectName("eventCard")
    frame.setStyleSheet(
        f"QFrame#eventCard {{ background: {PANEL}; border: 1px solid "
        f"{BORDER}; border-top: 3px solid {colour}; border-radius: 6px; }}")
    inner = QVBoxLayout(frame)
    inner.setContentsMargins(12, 10, 12, 12)
    inner.setSpacing(6)
    return frame, inner


def _tile(value: str, caption: str, colour: str = ACCENT,
          tooltip: str = "") -> QFrame:
    """One number, large, with what it counts under it."""
    frame = QFrame()
    frame.setObjectName("eventTile")
    frame.setStyleSheet(
        f"QFrame#eventTile {{ background: {PANEL}; border: 1px solid "
        f"{BORDER}; border-radius: 6px; }}")
    inner = QVBoxLayout(frame)
    inner.setContentsMargins(12, 6, 12, 6)
    inner.setSpacing(0)
    number = QLabel(value)
    number.setTextFormat(Qt.PlainText)
    number.setStyleSheet(f"color: {colour}; font-size: 17px; font-weight: bold;")
    under = QLabel(caption)
    under.setTextFormat(Qt.PlainText)
    under.setStyleSheet(f"color: {MUTED}; font-size: 10px;")
    inner.addWidget(number)
    inner.addWidget(under)
    if tooltip:
        frame.setToolTip(tooltip)
        under.setToolTip(tooltip)
    frame.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
    return frame


def _span(values: list[int]) -> str:
    low, high = min(values), max(values)
    return f"{low:,}–{high:,}" if low != high else f"{low:,}"


class _Bar(QWidget):
    """A horizontal bar, `fraction` of its width filled."""

    def __init__(self, fraction: float, colour: str, height: int = 8):
        super().__init__()
        self.fraction = max(0.0, min(1.0, fraction))
        self.colour = QColor(colour)
        self.setFixedHeight(height)
        self.setMinimumWidth(60)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        radius = self.height() / 2
        painter.setBrush(QColor(255, 255, 255, 22))
        painter.drawRoundedRect(QRectF(self.rect()), radius, radius)
        if self.fraction > 0:
            filled = QRectF(0, 0, max(self.height(), self.width()
                                      * self.fraction), self.height())
            painter.setBrush(self.colour)
            painter.drawRoundedRect(filled, radius, radius)


class _Split(QWidget):
    """Two shares of one whole, side by side in one bar: Day 1 and Day 2."""

    def __init__(self, first: int, second: int):
        super().__init__()
        self.first, self.second = first, second
        self.setFixedHeight(10)
        self.setMinimumWidth(120)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def paintEvent(self, _event) -> None:
        total = self.first + self.second
        if not total:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        radius = self.height() / 2
        cut = self.width() * self.first / total
        painter.setBrush(QColor(DAY2))
        painter.drawRoundedRect(QRectF(self.rect()), radius, radius)
        if self.first:
            painter.setBrush(QColor(DAY1))
            painter.drawRoundedRect(QRectF(0, 0, max(cut, self.height()),
                                           self.height()), radius, radius)


class _Column(QWidget):
    """One rung of a ladder: a vertical bar `fraction` of its height high."""

    def __init__(self, fraction: float, colour: str):
        super().__init__()
        self.fraction = max(0.08, min(1.0, fraction))
        self.colour = QColor(colour)
        self.setFixedSize(26, 34)

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.colour)
        high = self.height() * self.fraction
        painter.drawRoundedRect(QRectF(4, self.height() - high,
                                       self.width() - 8, high), 2, 2)


def _grants_an_amount(line: str) -> bool:
    """Does this line hand over an amount once, rather than name a state?

    A duration belongs to a state -- you are invulnerable *for five seconds*.
    An amount is handed over and then it is yours, so `10,000 runes for 1s`
    and `restores 100 stamina for 0.3s` say something that is not true of
    either (QA-133, AK-103).

    `nrdata.extract._buff_lines` builds exactly two amount-granting shapes,
    from `soul` and from `changeStaminaPoint`, and both are recognised here by
    the shape that function gives them. The default is the other way -- an
    unrecognised line keeps its duration -- because every other field that
    function words is a state, and losing a real duration would cost a player
    more than this rule gains.
    """
    return line.endswith(" runes") or line.startswith("restores ")


def _buff_figures(buff: dict) -> list[str]:
    """Every figure a reward buff carries, one line each, windows attached
    only to states (AK-103)."""
    figures = list(buff["lines"])
    cap = buff.get("stacks_to")
    per_trigger_suffix = (
        f" each time it triggers, up to +{cap} stacks" if cap
        else " each time it triggers")
    figures += [line + per_trigger_suffix for line in buff["per_trigger"]]
    for part in buff["parts"]:
        # Split before the duration is attached, so a part carrying both an
        # amount and a state gives the window to the state alone rather than
        # to whichever came first (AK-103).
        amounts = [line for line in part["lines"] if _grants_an_amount(line)]
        states = [line for line in part["lines"]
                  if not _grants_an_amount(line)]
        if amounts:
            figures.append(", ".join(amounts))
        if states:
            window = (f" for {part['duration']:g}s"
                      if part["duration"] and part["duration"] > 0 else "")
            figures.append(", ".join(states) + window)
    return figures


def _duration_chip(duration, colour: str) -> QLabel:
    if duration == -1:
        return _chip("∞  rest of the expedition", colour,
                     "Lasts the rest of the expedition — not consumed, no "
                     "cooldown.")
    return _chip(f"⏱  {duration:g}s", colour)


class WorldEventsTab(QWidget):
    def __init__(self, data: dict, icons=None):
        super().__init__()
        self.icons = icons
        # The first entry of a name is the base Nightlord; an Everdark twin
        # repeats the name further down and keeps its own symbol there.
        self.boss_icons: dict[str, int | None] = {}
        for boss in data.get("bosses", []):
            self.boss_icons.setdefault(boss["name"], boss.get("icon"))
        section = data.get("world_events") or {}
        self.events = section.get("events", [])
        self.unknowns = section.get("unknowns", [])
        self.buffs = {b["id"]: b for b in section.get("buffs", [])}
        self.creatures = section.get("creatures", {})
        self.states = {s["sp_id"]: s for s in section.get("states", [])}
        self.rune_scaling = section.get("rune_scaling", [])
        self.gating = section.get("gating", {})
        self.drops = section.get("drops", {})
        #: (list row, drop kind) whose full list is open.
        self._drops_open: set[tuple[int, str]] = set()
        self._row = -1

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        layout.addWidget(tabheader.heading("WORLD EVENTS"))
        layout.addWidget(tabheader.question(
            "Events that can interrupt an expedition: where each one can "
            "appear, what happens, what you win and what you lose."
        ))

        body = QHBoxLayout()
        body.setSpacing(10)

        self.list = QListWidget()
        self.list.setMaximumWidth(290)
        self.list.setWordWrap(True)
        self.list.setIconSize(QSize(LIST_ICON, LIST_ICON))
        self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list.setStyleSheet(
            f"QListWidget {{ background: {PANEL}; border: 1px solid {BORDER};"
            " border-radius: 4px; padding: 4px; }"
            "QListWidget::item { padding: 6px 8px; }"
            "QListWidget::item:selected { background: rgba(200, 164, 92, 60);"
            " color: #f0f0f0; }"
        )
        # Extracted events first, then the things players call world events
        # that the game never announces, listed like any other event.
        self.rows: list[tuple[str, dict]] = [("event", e) for e in self.events]
        self.rows += [("unannounced", u) for u in UNANNOUNCED]

        blank = QPixmap(LIST_ICON, LIST_ICON)
        blank.fill(Qt.transparent)
        blank = QIcon(blank)
        for kind, entry in self.rows:
            if kind == "event":
                lore = LORE.get(entry["log_id"], {})
                label = lore.get("name") or entry["announce"]
                if entry.get("is_dlc"):
                    label = f"{label}  · Deep of Night"
                pixmap = self._event_pixmap(lore)
            else:
                label = entry["name"]
                pixmap = None
            item = QListWidgetItem(label)
            # A blank symbol where the game has none, so every name in the
            # list starts at the same edge.
            item.setIcon(QIcon(pixmap) if pixmap is not None else blank)
            self.list.addItem(item)
        self.list.currentRowChanged.connect(self._show)
        body.addWidget(self.list)

        self.detail_area = QScrollArea()
        self.detail_area.setWidgetResizable(True)
        self.detail_area.setFrameShape(QFrame.NoFrame)
        body.addWidget(self.detail_area, 1)

        layout.addLayout(body, 1)

        if not self.events:
            layout.addWidget(tabheader.question(
                "No world events in this snapshot. Start the app with the "
                "game installed and it will rebuild itself."
            ))
        else:
            self.list.setCurrentRow(0)

    # -- symbols ------------------------------------------------------------

    def _status(self, icon_id):
        return self.icons.status(icon_id) if self.icons is not None else None

    def _item(self, icon_id):
        return self.icons.item(icon_id) if self.icons is not None else None

    def _boss_pixmap(self, name: str):
        if self.icons is None:
            return None
        return self.icons.menu(self.boss_icons.get(name))

    def _event_pixmap(self, lore: dict):
        """The event's own symbol: its reward buff, else what it leaves on
        you, else nothing."""
        buff = self.buffs.get(lore.get("buff_id"))
        if buff and self._status(buff.get("icon")) is not None:
            return self._status(buff["icon"])
        for key in ("reward_sp", "penalty_sp"):
            state = self.states.get(lore.get(key))
            if state and self._status(state.get("icon")) is not None:
                return self._status(state["icon"])
        return None

    def _nightlord(self, name: str) -> str:
        """A Nightlord's name with its symbol, where it has one."""
        return _marked(iconpack.inline(self.icons, "menu",
                                       self.boss_icons.get(name)), name)

    # -- page -----------------------------------------------------------------

    def _show(self, row: int) -> None:
        if not (0 <= row < len(self.rows)):
            return
        self._row = row
        kind, entry = self.rows[row]

        page = QWidget()
        column = QVBoxLayout(page)
        column.setContentsMargins(4, 0, 8, 8)
        column.setSpacing(10)

        if kind == "unannounced":
            self._render_unannounced(entry, column)
        else:
            self._render_event(entry, column)

        column.addStretch(1)
        scroll = self.detail_area.verticalScrollBar().value()
        self.detail_area.setWidget(page)
        self.detail_area.verticalScrollBar().setValue(scroll)

    def _header(self, column: QVBoxLayout, name: str, pixmap, colour: str,
                banner: str = "", chips: list[QLabel] = ()) -> None:
        frame, inner = _card(colour)
        row = QHBoxLayout()
        row.setSpacing(12)
        symbol = (_symbol(pixmap, HEADER_ICON) if pixmap is not None
                  else _glyph("✦", colour, HEADER_ICON))
        row.addWidget(symbol, 0, Qt.AlignTop)
        text = QVBoxLayout()
        text.setSpacing(4)
        title = QLabel(name)
        title.setWordWrap(True)
        title.setTextFormat(Qt.PlainText)
        title.setStyleSheet(
            f"color: {colour}; font-size: 17px; font-weight: bold;")
        text.addWidget(title)
        if banner:
            quote = QLabel(f"“{banner}”")
            quote.setWordWrap(True)
            quote.setTextFormat(Qt.PlainText)
            quote.setToolTip(f"Announced as “{banner}”")
            quote.setStyleSheet(
                "color: #e8dcc0; font-size: 12px; font-style: italic;")
            text.addWidget(quote)
        if chips:
            text.addLayout(_chips(*chips))
        row.addLayout(text, 1)
        inner.addLayout(row)
        column.addWidget(frame)

    def _render_event(self, event: dict, column: QVBoxLayout) -> None:
        lore = LORE.get(event["log_id"], {})
        gate = self.gating.get(str(event["log_id"]))
        buff = self.buffs.get(lore.get("buff_id"))
        creature = self.creatures.get(str(lore.get("creature_chr")))
        drops = self.drops.get(str(lore.get("creature_chr"))) or []
        penalty = self.states.get(lore.get("penalty_sp"))

        # -- header -------------------------------------------------------
        chips = []
        if gate:
            day1 = gate.get("day1_patterns", 0)
            day2 = gate.get("day2_patterns", 0)
            if day1:
                chips.append(_chip("Day 1", DAY1))
            if day2:
                chips.append(_chip("Day 2", DAY2))
        if event.get("is_dlc"):
            chips.append(_chip("Deep of Night only", DLC))
        self._header(column, lore.get("name") or event["announce"],
                     self._event_pixmap(lore),
                     DLC if event.get("is_dlc") else ACCENT,
                     event["announce"], chips)

        # -- number tiles ---------------------------------------------------
        tiles = []
        if gate:
            tiles.append(_tile(str(len(gate["bosses"])), "Nightlords"))
        if creature:
            tiles.append(_tile(_span(creature["hp"]), "enemy HP", "#d8d8d8"))
            tiles.append(_tile(_span(creature["runes"]), "runes, base", GOOD))
        if drops:
            tiles.append(_tile(str(len(drops)), "possible drops", GOOD))
        if tiles:
            row = QHBoxLayout()
            row.setSpacing(8)
            for tile in tiles:
                row.addWidget(tile)
            row.addStretch(1)
            column.addLayout(row)

        # -- where, and how often -----------------------------------------
        if gate:
            self._render_where(gate, column)

        # -- what happens ---------------------------------------------------
        if lore.get("what"):
            column.addWidget(_section("WHAT HAPPENS"))
            column.addWidget(_prose(lore["what"]))

        # -- the demon's forms ---------------------------------------------
        if event.get("variants"):
            column.addWidget(_section("WHAT THE DEMON CAN DO"))
            grid = QGridLayout()
            grid.setHorizontalSpacing(16)
            grid.setVerticalSpacing(4)
            for index, variant in enumerate(event["variants"]):
                line = QLabel("◆  " + variant["text"])
                line.setWordWrap(True)
                line.setTextFormat(Qt.PlainText)
                line.setStyleSheet("color: #d8d8d8; font-size: 12px;")
                grid.addWidget(line, index // 2, index % 2)
            column.addLayout(grid)

        # -- the banners it can end on -------------------------------------
        if event.get("outcomes"):
            column.addWidget(_section("IN-GAME BANNERS"))
            for outcome in event["outcomes"]:
                text = outcome["text"].replace(CODENAME, "a Nightfarer")
                line = QLabel("◆  " + text)
                line.setWordWrap(True)
                line.setTextFormat(Qt.PlainText)
                line.setStyleSheet(
                    "color: #e8dcc0; font-size: 12px; font-style: italic;")
                column.addWidget(line)

        # -- win and lose, side by side --------------------------------------
        win = self._win_card(lore, buff, creature, drops)
        lose = self._lose_card(lore, penalty)
        if win or lose:
            pair = QHBoxLayout()
            pair.setSpacing(10)
            for card in (win, lose):
                if card is not None:
                    pair.addWidget(card, 1, Qt.AlignTop)
            column.addLayout(pair)

        # -- caveats worth a player's attention -----------------------------
        self._caveats(lore, column)

    def _render_where(self, gate: dict, column: QVBoxLayout) -> None:
        column.addWidget(_section("WHERE IT APPEARS"))
        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(4)
        top = max((b["share"] for b in gate["bosses"]), default=0) or 1
        for index, boss in enumerate(gate["bosses"]):
            symbol = _symbol(self._boss_pixmap(boss["name"]), ROW_ICON)
            if symbol is not None:
                grid.addWidget(symbol, index, 0)
            name = QLabel(boss["name"])
            name.setTextFormat(Qt.PlainText)
            name.setStyleSheet("color: #d8d8d8; font-size: 12px;")
            grid.addWidget(name, index, 1)
            grid.addWidget(_Bar(boss["share"] / top, ACCENT), index, 2)
            share = QLabel(f"{boss['share']:g}%")
            share.setTextFormat(Qt.PlainText)
            share.setToolTip(
                f"{boss['patterns']} of {boss['of']} map patterns")
            share.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            share.setStyleSheet(
                f"color: {ACCENT}; font-size: 12px; font-weight: bold;")
            grid.addWidget(share, index, 3)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setColumnStretch(2, 1)
        grid.setColumnMinimumWidth(1, 150)
        holder = QWidget()
        holder.setMaximumWidth(560)
        holder.setLayout(grid)
        column.addWidget(holder)

        legend = _muted(WHERE_LEGEND, 10)
        legend.setToolTip(f"{NEVER_SCOPE} {PERCENTAGE_SCOPE}")
        column.addWidget(legend)

        day1 = gate.get("day1_patterns", 0)
        day2 = gate.get("day2_patterns", 0)
        # The split is in the data and used to be thrown away, so all eleven
        # events carried the same sentence while Judgment is 19 Day-1
        # patterns against 1 and this one is 9 against 21 (QA-134).
        if day1 and day2:
            when = (f"Can fire on Day 1 or Day 2 — {day1} of the "
                    f"{day1 + day2} map patterns that carry it are Day 1.")
        elif day1:
            when = "Fires on Day 1."
        else:
            when = "Fires on Day 2."
        split = QHBoxLayout()
        split.setContentsMargins(0, 0, 0, 0)
        split.setSpacing(8)
        first = QLabel(f"Day 1 · {day1}")
        first.setStyleSheet(f"color: {DAY1}; font-size: 11px;")
        second = QLabel(f"{day2} · Day 2")
        second.setStyleSheet(f"color: {DAY2}; font-size: 11px;")
        split.addWidget(first)
        split.addWidget(_Split(day1, day2), 1)
        split.addWidget(second)
        holder = QWidget()
        holder.setMaximumWidth(560)
        holder.setLayout(split)
        holder.setToolTip(when)
        column.addWidget(holder)
        column.addWidget(_muted(when, 10))

    def _win_card(self, lore: dict, buff, creature, drops) -> QFrame | None:
        reward_state = self.states.get(lore.get("reward_sp"))
        if not (buff or reward_state or creature or drops
                or lore.get("reward")):
            return None
        frame, inner = _card(GOOD)
        inner.addWidget(_section("✔  WIN"))

        if buff:
            self._effect(inner, self._status(buff.get("icon")), buff["name"],
                         buff["info"], GOOD)
            figures = _buff_figures(buff)
            for figure in figures:
                inner.addWidget(_stat(figure))
            for prefix, sentence in UNKNOWN_REFERENCE.items():
                if any(line.startswith(prefix) for line in figures):
                    inner.addWidget(_muted(sentence, 10))
            chips = [_duration_chip(buff["duration"], GOOD)]
            if buff.get("shares_with_allies"):
                chips.append(_chip("👥  nearby allies too", GOOD))
            inner.addLayout(_chips(*chips))
        elif reward_state:
            self._effect(inner, self._status(reward_state.get("icon")),
                         reward_state["name"], "", GOOD)
            for line in reward_state["lines"]:
                inner.addWidget(_stat(line))
            inner.addLayout(_chips(
                _duration_chip(reward_state["duration"], GOOD)))
        # The community line stands in where the files name no buff; where
        # they do, only what the buff does not already say (`reward_more`).
        more = lore.get("reward_more") if buff else lore.get("reward")
        if more:
            inner.addWidget(_prose(more))

        if creature:
            self._rune_ladder(inner, creature)
        if drops:
            self._drop_lists(inner, drops)
        return frame

    def _lose_card(self, lore: dict, state) -> QFrame | None:
        if not (state or lore.get("penalty")):
            return None
        frame, inner = _card(PENALTY)
        inner.addWidget(_section("✘  LOSE"))
        if state:
            self._effect(inner, self._status(state.get("icon")),
                         state["name"], "", PENALTY)
            for line in state["lines"]:
                inner.addWidget(_stat(line, PENALTY))
            inner.addLayout(_chips(_duration_chip(state["duration"],
                                                  PENALTY)))
        more = lore.get("penalty_more") if state else lore.get("penalty")
        if more:
            inner.addWidget(_prose(more))
        return frame

    def _effect(self, inner: QVBoxLayout, pixmap, name: str, info: str,
                colour: str) -> None:
        """An effect's symbol, name and the game's one-line description."""
        row = QHBoxLayout()
        row.setSpacing(10)
        symbol = (_symbol(pixmap, EFFECT_ICON) if pixmap is not None
                  else _glyph("✦", colour, EFFECT_ICON))
        row.addWidget(symbol, 0, Qt.AlignTop)
        text = QVBoxLayout()
        text.setSpacing(2)
        title = QLabel(name)
        title.setWordWrap(True)
        title.setTextFormat(Qt.PlainText)
        title.setStyleSheet(
            f"color: {colour}; font-size: 13px; font-weight: bold;")
        text.addWidget(title)
        if info:
            text.addWidget(_muted(info.replace("\n", " ")))
        row.addLayout(text, 1)
        inner.addLayout(row)

    def _rune_ladder(self, inner: QVBoxLayout, creature: dict) -> None:
        """The creature's runes and the ladder that raises them (AK-104,
        QA-148): the figures as columns, the sentences behind them."""
        inner.addWidget(_section("RUNES"))
        claim = _stat(f"Runes: {_span(creature['runes'])} base — rises the "
                      "more expeditions you have cleared", GOOD)
        explanation = " ".join(self.rune_scaling)
        claim.setToolTip(explanation)
        inner.addWidget(claim)
        ladder = next((line for line in self.rune_scaling if "step" in line),
                      "")
        steps = re.findall(r"×(\d+(?:\.\d+)?)", ladder)
        if len(steps) > 1:
            values = [float(step) for step in steps]
            low, high = values[0], max(values)
            row = QHBoxLayout()
            row.setSpacing(2)
            for value, text in zip(values, steps):
                cell = QVBoxLayout()
                cell.setSpacing(1)
                fraction = (0.25 + 0.75 * (value - low) / (high - low)
                            if high > low else 1.0)
                cell.addWidget(_Column(fraction, GOOD), 0, Qt.AlignHCenter)
                caption = QLabel(f"×{text}")
                caption.setAlignment(Qt.AlignCenter)
                caption.setStyleSheet(f"color: {MUTED}; font-size: 9px;")
                cell.addWidget(caption)
                row.addLayout(cell)
            row.addStretch(1)
            inner.addLayout(row)
            legend = _muted("▸ step 1 → step "
                            f"{len(values)}: expedition progress   "
                            "▸ hover for details", 10)
            legend.setToolTip(explanation)
            inner.addWidget(legend)

    def _drop_lists(self, inner: QVBoxLayout, drops: list[dict]) -> None:
        """Every drop, grouped by kind, likeliest first, each with its
        symbol and share of the drop table."""
        inner.addWidget(_section("DROPS"))
        known = {kind for kind, _ in DROP_KINDS}
        groups = list(DROP_KINDS) + sorted(
            {(d["kind"], d["kind"].title()) for d in drops
             if d["kind"] not in known})
        for kind, title in groups:
            entries = sorted((d for d in drops if d["kind"] == kind),
                             key=lambda d: (-d["share"], d["name"]))
            if not entries:
                continue
            key = (self._row, kind)
            expanded = key in self._drops_open
            shown = entries if expanded else entries[:DROPS_OPEN]
            inner.addLayout(_chips(_chip(f"{title} · {len(entries)}", GOOD)))
            grid = QGridLayout()
            grid.setHorizontalSpacing(8)
            grid.setVerticalSpacing(3)
            for index, drop in enumerate(shown):
                cell = QHBoxLayout()
                cell.setSpacing(6)
                symbol = _symbol(self._item(drop.get("icon")), ROW_ICON)
                if symbol is not None:
                    cell.addWidget(symbol)
                name = QLabel(drop["name"])
                name.setTextFormat(Qt.PlainText)
                name.setWordWrap(True)
                name.setStyleSheet("color: #d8d8d8; font-size: 11px;")
                cell.addWidget(name, 1)
                share = QLabel(f"{drop['share']:g}%")
                share.setTextFormat(Qt.PlainText)
                share.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
                cell.addWidget(share)
                grid.addLayout(cell, index // 2, index % 2)
            grid.setColumnStretch(0, 1)
            grid.setColumnStretch(1, 1)
            inner.addLayout(grid)
            rest = len(entries) - DROPS_OPEN
            if rest > 0:
                button = QPushButton("Show fewer" if expanded
                                     else f"Show {rest} more")
                button.setCursor(Qt.PointingHandCursor)
                button.setFlat(True)
                button.setStyleSheet(
                    f"color: {ACCENT}; font-size: 11px; text-align: left;"
                    " padding: 0;")
                button.clicked.connect(
                    lambda _checked=False, key=key: self._toggle_drops(key))
                inner.addWidget(button, 0, Qt.AlignLeft)
        inner.addWidget(_muted("▸ % = share of the drop table", 10))

    def _toggle_drops(self, key: tuple[int, str]) -> None:
        self._drops_open ^= {key}
        self._show(self._row)

    @staticmethod
    def _caveats(lore: dict, column: QVBoxLayout) -> None:
        for key, prefix, mark in (("note", "Note", "ⓘ"),
                                  ("uncertain", "Least certain", "?"),
                                  ("conflict", "Sources disagree", "⇄")):
            if lore.get(key):
                label = QLabel(f"{mark}  <b>{prefix}:</b> {lore[key]}")
                label.setWordWrap(True)
                label.setStyleSheet(f"color: {UNKNOWN}; font-size: 11px;")
                column.addWidget(label)

    def _render_unannounced(self, entry: dict, column: QVBoxLayout) -> None:
        self._header(column, entry["name"], None, ACCENT, "",
                     [_chip("no banner", MUTED)])
        bosses = entry.get("nightlords")
        if bosses:
            column.addWidget(_section("WHERE IT APPEARS"))
            if bosses == ["Any"]:
                column.addWidget(_prose("Every Nightlord."))
            else:
                row = QHBoxLayout()
                row.setSpacing(12)
                for name in bosses:
                    symbol = _symbol(self._boss_pixmap(name), ROW_ICON)
                    if symbol is not None:
                        row.addWidget(symbol)
                    label = QLabel(name)
                    label.setTextFormat(Qt.PlainText)
                    label.setStyleSheet("color: #d8d8d8; font-size: 12px;")
                    row.addWidget(label)
                row.addStretch(1)
                column.addLayout(row)
        if entry.get("what"):
            column.addWidget(_section("WHAT HAPPENS"))
            column.addWidget(_prose(entry["what"]))
        cards = []
        if entry.get("reward"):
            frame, inner = _card(GOOD)
            inner.addWidget(_section("✔  WIN"))
            inner.addWidget(_prose(entry["reward"]))
            cards.append(frame)
        if entry.get("penalty") and entry["penalty"] not in ("None.",):
            frame, inner = _card(PENALTY)
            inner.addWidget(_section("✘  LOSE"))
            inner.addWidget(_prose(entry["penalty"]))
            cards.append(frame)
        if cards:
            pair = QHBoxLayout()
            pair.setSpacing(10)
            for card in cards:
                pair.addWidget(card, 1, Qt.AlignTop)
            column.addLayout(pair)
        if entry.get("note"):
            label = QLabel(f"ⓘ  <b>Note:</b> {entry['note']}")
            label.setWordWrap(True)
            label.setStyleSheet(f"color: {UNKNOWN}; font-size: 11px;")
            column.addWidget(label)
