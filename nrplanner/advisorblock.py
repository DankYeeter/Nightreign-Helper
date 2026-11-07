"""The living suggestion in the slot card, and the `Why` dialog behind it.

Two views of one answer, and the difference between them is decided on the
shape of a line rather than on its words (`types.drawn_in_the_block`):

* the **block** sits in the slot card under `rolled_label` and shows what the
  player has to weigh **before** applying -- the figures, and every curse of
  the suggested copy including the one no figure covers. A curse is a trap;
  the price has to be readable before the deal (Director, 06.09.2026);
* the **`Why` dialog** shows the whole account: the same lines plus the
  silent effects, the conditional list, the legend and the procedural
  sentences of the direction.

**Nothing here reads a sentence.** Every line arrives with its slot, with
whether it is a curse and with why it carries no figure, and this module maps
those three facts onto a bullet, a colour and a strikethrough. Splitting a
line on `: ` or looking for `works only for` is what `UI_SPEC` AK-147 forbids
and what QA-107 cost this project once already -- one field of this dataset
is called `Regain -- HP won back by attacking after a hit`.

**Every text element states its format** (AK-29, D-10). Every label is
`Qt.PlainText`, which is the whole of the escaping question for it. A tooltip
has no text format in Qt, so it is wrapped as rich text and escaped, which is
the only form that shows a name carrying `<b>` letter for letter (AK-30).

**The block asks, the window does.** Applying is one thing with one undo model,
and `Reject` and the X at a line (AK-420, AK-427) change the question: each
signal says the player pressed it, and the window acts. `Use` and `Reject` are
drawn only where there is something to press them for -- a suggestion that is
already lying in the slot draws the one line of §3.2 and no control.

**The dialog shows the marks, it does not set them** (AK-301), the X in the
block is the one other place that sets one. A line whose
effect the player favourited or avoided (`effectfilters`) is drawn in that
state -- `▲` and bold, or struck through -- as a `WhyLine`, a `QLabel` bullet
beside a `QLabel` text with no control on it: marks are set in the effect
filter window alone, and the legend says where. The line is bound to the
effect **id** and redraws from `EffectFilters.changed`, so two lines about
one effect never show two states. The compact block keeps its plain markup.
"""

from __future__ import annotations

import html
from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QDialog, QFrame, QHBoxLayout, QLabel,
                               QPushButton, QScrollArea, QSizePolicy,
                               QToolButton, QVBoxLayout, QWidget)

from . import effectfilters, effecttext, iconpack
from .advisor import goals as advisor_goals
from .advisor import types
from .theme import ACCENT, BAD, CURSE, FAVOURITE, MUTED, PANEL

#: How tall a relic's symbol stands beside its name.
RELIC_SYMBOL = 18

#: The one line a block shows when the suggestion is already lying in the slot
#: (`UI_SPEC` §3.2). Everything else falls away with it: there is nothing to
#: weigh and nothing to change.
ALREADY_EQUIPPED = "Already equipped — nothing to change here."

#: The line under the name of a relic that is here because it is starred
#: (AK-437).
PINNED_LINE = "★ Your favourite — included because it fits."

#: The heading of the stars left out, over the slot groups (AK-439).
PINS_LEFT_OUT_HEADING = "Favourited relics left out:"

#: What `Reject` does (AK-427), and the sentence a starred relic adds.
REJECT_TOOLTIP = ("Do not suggest this relic, or any copy with the same "
                  "effects, for this build.")
REJECT_PINNED_TOOLTIP = "Your favourite stays marked."

#: The X at the end of a line in the block (AK-420, AK-421).
AVOID_CAPTION = "✕"
AVOID_BUTTON_SIZE = 24

#: The legend for `✦`, once per `Why` dialog and in no block (AK-141).
CURSE_LEGEND = ("✦ marks a curse. A cost with no number beside it is still a "
                "cost — weigh it before you apply.")

#: The heading of the conditional list under the slot groups (4.9b).
CONDITIONAL_HEADING = ("These effects only apply under a condition, so this "
                       "ranking did not count them:")

#: The bullets, as `RelicSlot._sync_mode` draws them.
EFFECT_BULLET = "•"
CURSE_BULLET = "✦"
#: The bullet of a line the player favourited (AK-301).
REQUIRED_BULLET = "▲"

#: What the marks mean and where they are set, once per `Why` dialog, always
#: on screen (AK-408, verbatim from the spec). A strikethrough is both an
#: avoided effect and one of another Nightfarer, one style for both.
MARK_LEGEND = ("▲ marks an effect you favourited. A struck-through effect does "
               "nothing for you: you avoided it (change that in the effect "
               "filter, filter icon in the advisor bar) or it works only for "
               "another Nightfarer.")

#: The headings of the two read-only lists under the slot groups (AK-279,
#: wording AK-300).
EXCLUDED_HEADING = "Effects you've avoided:"
REQUIRED_HEADING = "Effects you've favourited:"
STACKS_HEADING = "Stacks you set in the effect filter:"

#: The colour `RelicSlot._sync_mode` gives a working rolled effect. A literal
#: there and a literal here on purpose: naming it in one place while the other
#: keeps the literal would be two names for one colour.
EFFECT_TEXT = "#cfcfcf"

#: The line height of an effect line, in px (`UI_SPEC` §3.2, AK-156).
SMALL_TEXT = 11

#: The silent fillings that only say "there is no number", folded away in a
#: freshly opened `Why` dialog (AK-372). Every other silent filling tells of
#: a decision of the player's or its consequence and stays drawn (AK-373).
NUMBERLESS = frozenset({types.SILENT_NO_NUMBER_HERE,
                        types.SILENT_UNDER_A_CONDITION,
                        types.SILENT_ARMAMENT_BOUND})

#: The least height of a fold button, in px (AK-376).
FOLD_HEIGHT = 24


# --- one line, as the markup that draws it ---------------------------------

@dataclass(frozen=True)
class LineStyle:
    """How one line is drawn: the facts `_dress` turns into a font and a
    stylesheet, for the block and the dialog alike. `small` is the 11 px of a
    silent effect (AK-156)."""

    bullet: str
    colour: str
    struck: bool = False
    bold: bool = False
    small: bool = False


def _styled(line: types.ReasonLine, kind: str | None) -> LineStyle:
    """The style of one line in the given marked state (`None`: neutral).

    Four neutral cases, and all four are read off `is_curse` and `silence`
    -- never off the words:

    * a curse: `✦` in `CURSE`, whether or not a figure covers it;
    * an effect that belongs to another Nightfarer: drawn the way the rest of
      the program draws a dead effect, struck through and in `BAD` (Director,
      06.09.2026). It is the commonest silent case there is -- 150 of 426
      measured on one save -- and two ways of saying one thing is one thing
      for the player to remember;
    * any other silent effect: `MUTED`, 11 px, no warning colour, no `⚠`
      (AK-156);
    * an effect with a figure: `•` in the colour `_sync_mode` gives one.

    The two marked states override all four (AK-301): `Avoid` is exactly
    the dead-effect style, `Favourite` is bold in `ACCENT` under `▲`. The
    bullet keeps its kind for an avoided curse, so it is still read as a
    curse.
    """
    bullet = CURSE_BULLET if line.is_curse else EFFECT_BULLET
    if kind == effectfilters.EXCLUDED:
        return LineStyle(bullet, BAD, struck=True)
    if kind == effectfilters.REQUIRED:
        return LineStyle(REQUIRED_BULLET, ACCENT, bold=True)
    if line.is_curse:
        return LineStyle(bullet, CURSE)
    if line.silence == types.SILENT_ANOTHER_NIGHTFARER:
        return LineStyle(bullet, BAD, struck=True)
    if line.silence != types.CARRIES_A_FIGURE:
        return LineStyle(bullet, MUTED, small=True)
    return LineStyle(bullet, EFFECT_TEXT)


def _dress(style: LineStyle, bullet: QLabel, label: QLabel,
           base_font: QFont) -> None:
    """Put one style on a bullet and its text. From the base font every time,
    so a state that ends takes its mark with it."""
    css = f"border: none; color: {style.colour};"
    bullet.setText(style.bullet)
    bullet.setStyleSheet(css)
    label.setStyleSheet(css)
    font = QFont(base_font)
    if style.small:
        font.setPixelSize(SMALL_TEXT)
    font.setStrikeOut(style.struck)
    font.setBold(style.bold)
    label.setFont(font)


def effect_name(effects: dict, effect_id: int) -> str:
    """The display name, or the id for one the dataset has lost."""
    effect = effects.get(str(effect_id))
    return effecttext.name(effect) if effect else f"effect {effect_id}"


def as_a_tooltip(text: str) -> str:
    """`text` in a tooltip, letter for letter, markup and all (AK-30).

    Qt offers no text format for tooltips and decides for itself whether what
    it was handed is markup, so a curse name carrying `<b>` would come out
    bold with a piece missing. Escaping alone is not the answer either: an
    escaped string carries no tag, Qt then reads it as plain text, and the
    player is shown `&lt;b&gt;`. Declared rich text over escaped content is
    the one form that shows the name as it is written.
    """
    if not text:
        return ""
    rows = []
    for row in html.escape(text).split("\n"):
        stripped = row.lstrip(" ")
        indent = "&nbsp;" * (len(row) - len(stripped))
        rows.append(indent + stripped)
    return "<html>" + "<br>".join(rows) + "</html>"


def _plain(text: str = "", *, colour: str = "", size: int = 0) -> QLabel:
    """A label that draws no markup, and says so (AK-29)."""
    label = QLabel(text)
    label.setTextFormat(Qt.PlainText)
    label.setWordWrap(True)
    style = ["border: none;"]
    if colour:
        style.append(f"color: {colour};")
    if size:
        style.append(f"font-size: {size}px;")
    label.setStyleSheet(" ".join(style))
    return label


def _add_named(column: QVBoxLayout, symbols: tuple, label: QLabel) -> None:
    """A heading of the dialog, in a row with its symbols if it has any."""
    if any(symbol is not None for symbol in symbols):
        column.addLayout(iconpack.beside(list(symbols), label, RELIC_SYMBOL))
    else:
        column.addWidget(label)


def _stacked(widgets) -> QWidget:
    """These widgets one under the other, as tight as lines of one label."""
    holder = QWidget()
    layout = QVBoxLayout(holder)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    for widget in widgets:
        layout.addWidget(widget)
    return holder


def is_numberless(line: types.ReasonLine) -> bool:
    """Does this line only say that it has no number (AK-372)? A curse never
    does: its price is read before applying (AK-373)."""
    return not line.is_curse and line.silence in NUMBERLESS


class FoldButton(QToolButton):
    """Shows and hides one widget, saying which with an arrow (AK-376).

    Checked is open. The state lives in the dialog alone (AK-377). Enter
    folds as Space does: in a dialog it would otherwise press `Close`.
    """

    def __init__(self, closed_text: str, open_text: str, target: QWidget,
                 opened: bool = False) -> None:
        super().__init__()
        self._texts = (closed_text, open_text)
        self._target = target
        self.setAutoRaise(True)
        self.setCheckable(True)
        self.setMinimumHeight(FOLD_HEIGHT)
        self.setStyleSheet(
            f"QToolButton {{ color: {ACCENT};"
            f" border: 1px solid transparent; }}"
            f" QToolButton:focus {{ border: 1px solid {ACCENT}; }}")
        self.toggled.connect(self._fold)
        self.setChecked(opened)
        self._fold(opened)

    def say(self, closed_text: str, open_text: str) -> None:
        """Other words for the same fold, where it counts something."""
        self._texts = (closed_text, open_text)
        self._fold(self.isChecked())

    def _fold(self, opened: bool) -> None:
        self._target.setVisible(opened)
        text = self._texts[opened]
        self.setText(("▾ " if opened else "▸ ") + text)
        self.setAccessibleName(text)

    def keyPressEvent(self, event) -> None:
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.click()
            return
        super().keyPressEvent(event)


def _numberless_fold(count: int, target: QWidget) -> FoldButton:
    effects = "1 effect" if count == 1 else f"{count} effects"
    return FoldButton(f"Show {effects} without a number",
                      f"Hide {effects} without a number", target)


class WhyLine(QWidget):
    """One drawn line of the `Why` dialog, in the state its effect carries.

    Read-only (AK-301): a `QLabel` bullet beside a `QLabel` text, no tab
    stop, no click, no tooltip. Plain text and a font, not markup: the text
    is a name out of the game files (AK-29), and strikethrough and bold are
    the font's. Redrawn from `EffectFilters.changed`, so a mark set in the
    filter window while this dialog stands shows here at once.
    """

    def __init__(self, line: types.ReasonLine,
                 filters: effectfilters.EffectFilters,
                 parent: QWidget | None = None, *, symbol=None) -> None:
        super().__init__(parent)
        self.line = line
        self._filters = filters
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(4)
        self.bullet = _plain()
        self.bullet.setWordWrap(False)
        self.label = _plain(line.text)
        self._base_font = QFont(self.label.font())
        row.addWidget(self.bullet, 0, Qt.AlignTop)
        if symbol is not None:
            row.addWidget(iconpack.symbol_label(symbol), 0, Qt.AlignTop)
        row.addWidget(self.label, 1)
        filters.changed.connect(self._redraw)
        self._redraw()

    def kind(self) -> str | None:
        """Which of the two sets holds this line's effect, `None` for
        neutral. Avoided is the resolved set (AD-039.3): a member of an
        avoided family is struck through, one on `Allow` is not (AK-317.5).
        """
        if self.line.effect_id in self._filters.resolved_excluded:
            return effectfilters.EXCLUDED
        if self.line.effect_id in self._filters.required:
            return effectfilters.REQUIRED
        return None

    def _redraw(self) -> None:
        _dress(_styled(self.line, self.kind()), self.bullet, self.label,
               self._base_font)


def _avoid_tooltip(line: types.ReasonLine, name: str, favourited: bool) -> str:
    """AK-422: what the X will do, and where it is taken back."""
    if favourited:
        first = f"Avoid “{name}” — this replaces your Favourite for it."
    else:
        first = (f"Avoid {'the curse ' if line.is_curse else ''}“{name}” — no "
                 f"suggestion will use a relic that carries it.")
    return f"{first} Undo in Filters."


class AvoidButton(QToolButton):
    """The X at the end of one line (AK-420, AK-421).

    All of a block's are one tab stop (AK-423): `walk` asks the block to move
    along them, and only the one standing on the stop takes `Tab`.
    """

    def __init__(self, line: types.ReasonLine, name: str, favourited: bool,
                 walk, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.effect_id = line.effect_id
        self._walk = walk
        tooltip = _avoid_tooltip(line, name, favourited)
        self.setText(AVOID_CAPTION)
        self.setFixedSize(AVOID_BUTTON_SIZE, AVOID_BUTTON_SIZE)
        self.setAutoRaise(True)
        self.setFocusPolicy(Qt.ClickFocus)
        self.setToolTip(as_a_tooltip(tooltip))
        self.setAccessibleName(f"Avoid {name}")
        self.setAccessibleDescription(tooltip)
        self.setStyleSheet(
            f"QToolButton {{ color: {MUTED}; border: 1px solid transparent; }}"
            f" QToolButton:hover {{ color: {BAD}; }}"
            f" QToolButton:focus {{ color: {BAD};"
            f" border: 1px solid {ACCENT}; }}")

    def keyPressEvent(self, event) -> None:
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.click()
        elif event.key() == Qt.Key_Up:
            self._walk(self, -1)
        elif event.key() == Qt.Key_Down:
            self._walk(self, 1)
        else:
            super().keyPressEvent(event)


class BlockLine(QWidget):
    """One line of the block: bullet, text, X (AK-420), plain text throughout."""

    def __init__(self, line: types.ReasonLine, name: str, favourited: bool,
                 walk, parent: QWidget | None = None, *,
                 symbol=None) -> None:
        super().__init__(parent)
        self.line = line
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(4)
        self.bullet = _plain()
        self.bullet.setWordWrap(False)
        self.label = _plain(line.text)
        _dress(_styled(line, None), self.bullet, self.label, self.label.font())
        self.avoid = AvoidButton(line, name, favourited, walk)
        row.addWidget(self.bullet, 0, Qt.AlignTop)
        if symbol is not None:
            row.addWidget(iconpack.symbol_label(symbol), 0, Qt.AlignTop)
        row.addWidget(self.label, 1)
        row.addWidget(self.avoid, 0, Qt.AlignTop)


# --- the block in the slot card --------------------------------------------

class SuggestionBlock(QFrame):
    """What the advisor would put in this slot, while the answer lives.

    The dashed border is the one `CustomRelicCard` already carries: in this
    program dashed means "planned, not real", which is exactly what a
    suggestion is until it is applied (`UI_SPEC` §3.2).

    `Use`, `Why this relic`, `Reject` and an X per line (AK-274, AK-378,
    AK-420, AK-427), and none changes anything here: the block holds no relics,
    so it says the player asked and the window does the rest.
    """

    #: `Use` was pressed on this block (`UI_SPEC` §3.2: only this one slot).
    use_requested = Signal()
    #: `Why` was pressed on this block. Opens the one dialog the bar's own
    #: `Why` opens, with the same, whole content -- AK-274 forbids a second,
    #: card-only account of the answer.
    why_requested = Signal()
    #: `Reject` was pressed on this block (AK-427).
    reject_requested = Signal()
    #: An X was pressed: avoid this effect or curse (AK-424).
    avoid_requested = Signal(int)

    def __init__(self, parent: QWidget | None = None, *, icons=None) -> None:
        super().__init__(parent)
        from .app import _heading

        self._icons = icons

        self.setStyleSheet(
            f"QFrame {{ background: {PANEL};"
            f" border: 1px dashed {ACCENT}; border-radius: 5px; }}"
        )
        # The block asks for no width of its own, exactly as §3.1 has the
        # advisor's row ask for none: it sits in a card inside the middle
        # column's scroll area, and a widget that states a minimum width
        # there widens the card past the viewport and puts a **horizontal**
        # scrollbar under six cards that are all too wide (AK-160). Measured
        # on `Wylder's Goblet` at 1320 logical px offscreen: the middle
        # column scrolls 0..11 px without the advisor and 0..25 px with it
        # while this line is missing.
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        column = QVBoxLayout(self)
        column.setContentsMargins(8, 8, 8, 8)
        column.setSpacing(2)

        # `_heading` for the font of every other heading in this window; the
        # words are this block's own, because the goal travels with them --
        # the block has to stand for itself once the bar has scrolled away.
        self.heading = _heading("Suggested")
        self.heading.setTextFormat(Qt.PlainText)
        # AK-427: the heading gives way when the width runs out, the buttons
        # never do.
        self.heading.setWordWrap(True)
        # §3.2 draws the heading and the buttons on one line, the buttons at
        # the right end of it, because the heading takes what they leave.
        head = QHBoxLayout()
        head.setContentsMargins(0, 0, 0, 0)
        head.addWidget(self.heading, 1)
        self.use_button = QPushButton("Use")
        self.use_button.clicked.connect(self.use_requested)
        head.addWidget(self.use_button)
        # AK-274: next to `Use`, never in its place.
        self.why_button = QPushButton("Why this relic")
        self.why_button.setToolTip("Why this relic is suggested for this slot")
        self.why_button.clicked.connect(self.why_requested)
        head.addWidget(self.why_button)
        self.reject_button = QPushButton("Reject")
        self.reject_button.clicked.connect(self.reject_requested)
        head.addWidget(self.reject_button)
        column.addLayout(head)

        self.relic_name = _plain()
        self.relic_symbol = QLabel()
        self.relic_symbol.setTextFormat(Qt.PlainText)
        self.relic_symbol.setFixedSize(RELIC_SYMBOL, RELIC_SYMBOL)
        self.relic_symbol.setStyleSheet("border: none;")
        naming = QHBoxLayout()
        naming.setContentsMargins(0, 0, 0, 0)
        naming.setSpacing(4)
        naming.addWidget(self.relic_symbol, 0, Qt.AlignTop)
        naming.addWidget(self.relic_name, 1)
        column.addLayout(naming)

        self.pinned_line = _plain(PINNED_LINE, colour=FAVOURITE, size=SMALL_TEXT)
        column.addWidget(self.pinned_line)

        self.count_line = _plain(colour=MUTED, size=SMALL_TEXT)
        column.addWidget(self.count_line)

        self.lines = QWidget()
        self._line_column = QVBoxLayout(self.lines)
        self._line_column.setContentsMargins(0, 0, 0, 0)
        self._line_column.setSpacing(0)
        self.drawn_lines: list[BlockLine] = []
        column.addWidget(self.lines)

        # A held favourite's own line (AK-314), between the effect/curse
        # lines and `already_equipped`: the bullet reads like a normal
        # effect line, the colour and size like `count_line` -- muted
        # information, never a marked or clickable state (AK-301's `▲` is a
        # different thing on a different line).
        self.held_favourite = _plain(colour=MUTED, size=SMALL_TEXT)
        column.addWidget(self.held_favourite)

        # Its own label rather than a filling of `count_line`: the one-line
        # case draws nothing else at all, and a shared label would have to be
        # emptied of a style as well as of a text.
        self.already_equipped = _plain(ALREADY_EQUIPPED, colour=MUTED,
                                       size=SMALL_TEXT)
        column.addWidget(self.already_equipped)

        self.empty_reason = _plain(colour=MUTED, size=SMALL_TEXT)
        self.empty_reason.setVisible(False)
        column.addWidget(self.empty_reason)

        self.setVisible(False)

    def show_the_suggestion(self, goal_label: str,
                            group: types.SlotReasons, *,
                            already_equipped: bool = False,
                            may_be_used: bool = True,
                            may_explain: bool = True,
                            curse_tooltip: str = "",
                            held_favourite_line: str = "",
                            pinned: bool = False,
                            names=None,
                            favourited: frozenset[int] = frozenset(),
                            relic_icon: int | None = None,
                            symbol_of=None) -> None:
        """Draw one slot group, or the one line that replaces it.

        `already_equipped` is the window's answer, not this block's: whether
        the suggested copy is the copy in the slot is a question about the
        handle in the slot, and the block holds no relics. `may_be_used` is
        the window's answer for the same reason -- whether this slot is held
        is a fact about the window, and a held slot is one no applying may
        touch (`UI_SPEC` §5.4). `may_explain` is a third, independent fact of
        the window's: whether the bar's own `Why` is offered right now
        (`advisorbar.ACTING_STATES`, AK-274). A held slot still explains
        itself -- holding is about applying, not about reading the account --
        so this never follows `may_be_used`. `pinned`: the run laid this relic
        because it is starred (AK-437). `names` and `favourited` are the X's
        words (AK-422): the block has no dataset and no marks to read.
        """
        self.heading.setText(f"Suggested — {goal_label}".upper())
        self.heading.setVisible(not already_equipped)
        self.use_button.setVisible(may_be_used and not already_equipped)
        self.why_button.setVisible(may_explain and not already_equipped)
        self.reject_button.setVisible(may_be_used and not already_equipped)
        self.reject_button.setToolTip(as_a_tooltip(
            f"{REJECT_TOOLTIP} {REJECT_PINNED_TOOLTIP}" if pinned
            else REJECT_TOOLTIP))
        self._symbol_of = symbol_of or (lambda _effect_id: None)
        self.relic_name.setText(group.relic_name)
        self.relic_name.setVisible(not already_equipped)
        art = self._icons.item(relic_icon) if self._icons is not None else None
        if art is not None:
            self.relic_symbol.setPixmap(iconpack.sharp(art, RELIC_SYMBOL))
        self.relic_symbol.setVisible(art is not None and not already_equipped)
        self.pinned_line.setVisible(pinned and not already_equipped)
        self.count_line.setText(group.count_line)
        self.count_line.setVisible(not already_equipped)
        self._draw_the_lines(
            [line for line in group.lines if types.drawn_in_the_block(line)],
            names or {}, favourited)
        self.lines.setToolTip(as_a_tooltip(curse_tooltip))
        self.lines.setVisible(not already_equipped)
        self.held_favourite.setText(f"{EFFECT_BULLET} {held_favourite_line}"
                                    if held_favourite_line else "")
        self.held_favourite.setVisible(not already_equipped
                                       and bool(held_favourite_line))
        self.already_equipped.setVisible(already_equipped)
        self.empty_reason.setVisible(False)
        self.setVisible(True)

    def _draw_the_lines(self, lines, names, favourited) -> None:
        """One `BlockLine` each. The X's follow `Reject` in the tab order, the
        first of them standing on the group's one stop (AK-423)."""
        self._clear_the_lines()
        before = self.reject_button
        for line in lines:
            drawn = BlockLine(line, names.get(line.effect_id,
                                              f"effect {line.effect_id}"),
                              line.effect_id in favourited, self._walk_the_xs,
                              symbol=self._symbol_of(line.effect_id))
            drawn.avoid.clicked.connect(
                lambda _checked=False, effect_id=line.effect_id:
                self.avoid_requested.emit(effect_id))
            self._line_column.addWidget(drawn)
            self.drawn_lines.append(drawn)
            QWidget.setTabOrder(before, drawn.avoid)
            before = drawn.avoid
        if self.drawn_lines:
            self.drawn_lines[0].avoid.setFocusPolicy(Qt.StrongFocus)

    def _clear_the_lines(self) -> None:
        for drawn in self.drawn_lines:
            self._line_column.removeWidget(drawn)
            drawn.hide()
            drawn.deleteLater()
        self.drawn_lines = []

    def _walk_the_xs(self, button: AvoidButton, step: int) -> None:
        """Arrow keys along the X's, and the tab stop moves along (AK-423)."""
        buttons = [drawn.avoid for drawn in self.drawn_lines]
        target = buttons[(buttons.index(button) + step) % len(buttons)]
        button.setFocusPolicy(Qt.ClickFocus)
        target.setFocusPolicy(Qt.StrongFocus)
        target.setFocus(Qt.TabFocusReason)

    def first_x(self) -> AvoidButton | None:
        """Where the focus goes after an X or `Reject` (AK-426): none while
        `already_equipped` hides the lines, or the focus falls on nothing."""
        return (self.drawn_lines[0].avoid
                if self.drawn_lines and self.lines.isVisibleTo(self) else None)

    def show_no_suggestion(self, reason: str) -> None:
        """AK-441: this slot has no choice in the answer, and says why.

        Nothing to press, and at most two lines with the whole text in the
        tooltip: a reason names effects, and those can be long.
        """
        self.heading.setText("NO SUGGESTION")
        self.heading.setVisible(True)
        self._clear_the_lines()
        for part in (self.use_button, self.why_button, self.reject_button,
                     self.relic_name, self.relic_symbol, self.pinned_line, self.count_line, self.lines, self.held_favourite,
                     self.already_equipped):
            part.setVisible(False)
        self.empty_reason.setText(reason)
        self.empty_reason.setToolTip(as_a_tooltip(reason))
        self.empty_reason.ensurePolished()
        self.empty_reason.setMaximumHeight(
            2 * self.empty_reason.fontMetrics().lineSpacing())
        self.empty_reason.setVisible(True)
        self.setVisible(True)

    def put_the_suggestion_away(self) -> None:
        """No answer lives for this slot any more."""
        self.empty_reason.clear()
        self.empty_reason.setToolTip("")
        self._clear_the_lines()
        self.lines.setToolTip("")
        self.relic_name.clear()
        self.count_line.clear()
        self.held_favourite.clear()
        self.setVisible(False)


# --- the `Why` dialog ------------------------------------------------------

@dataclass(frozen=True)
class WhyHeading:
    """What the head of the dialog names, and what no result carries.

    The goal is on the result; the other four are the window's own knowledge
    at the moment the run was asked (`UI_SPEC` §3.4 point 1). They travel in
    one shape so that the dialog takes one argument for the head instead of
    four positional strings that can be handed over in the wrong order.
    """

    goal_label: str
    nightfarer: str
    vessel: str
    deep: bool
    relics: int


def head_sentence(heading: WhyHeading) -> str:
    """The head of the dialog: what was asked, of what, with how much.

    **Wording written by the `developer`, not laid down anywhere** -- §3.4
    names the five facts and no sentence. It is reported as such rather than
    presented as a specified text (see the T-089 report).
    """
    relics = "1 relic" if heading.relics == 1 else f"{heading.relics} relics"
    return (f"{heading.goal_label} — {heading.nightfarer}, {heading.vessel}, "
            f"Deep of Night {'on' if heading.deep else 'off'}, "
            f"{relics} considered.")


def group_heading(group: types.SlotReasons) -> str:
    """`Slot {n} — {relic}`, and the slot is counted the way a window counts.

    One-based here and nowhere else: the data path addresses a slot and
    counts from zero, the player reads `Slot 1` (AK-135, T-078 §6).
    """
    return f"Slot {group.slot_index + 1} — {group.relic_name}"


class WhyDialog(QDialog):
    """The whole account of one answer, in the order §3.4 sets.

    Head, the slot groups, the conditional list, the legend, and the
    procedural sentences of the direction with the run's own findings under
    them. **No `Apply`**: applying has two places, the bar and the slot, and a
    third makes the action unfindable rather than easier to reach.
    """

    def __init__(self, heading: WhyHeading, result,
                 parent: QWidget | None = None, *,
                 filters: effectfilters.EffectFilters,
                 effects: dict, slot_index: int | None = None,
                 icons=None, head_symbols: tuple = (),
                 relic_icons: dict | None = None) -> None:
        super().__init__(parent)
        self._filters = filters
        self._effects = effects
        self._icons = icons
        self.setModal(True)
        self.setWindowTitle(f"Why this build — {heading.goal_label}")
        self.resize(640, 620)

        outer = QVBoxLayout(self)
        self.scroller = scroller = QScrollArea()
        scroller.setWidgetResizable(True)
        scroller.setFrameShape(QFrame.NoFrame)
        page = QWidget()
        column = QVBoxLayout(page)
        column.setContentsMargins(0, 0, 6, 0)
        column.setSpacing(4)

        self.head = _plain(head_sentence(heading))
        _add_named(column, head_symbols, self.head)

        # Over the slot groups, one statement in one label (AK-439).
        self.pins_left_out = _plain("\n".join(
            (PINS_LEFT_OUT_HEADING, *(pin.line for pin in result.pins_left_out))))
        self.pins_left_out.setVisible(bool(result.pins_left_out))
        column.addWidget(self.pins_left_out)

        self.groups: list[tuple[QLabel, QLabel, list[WhyLine]]] = []
        #: Per group, its fold of the numberless lines, `None` for none.
        self.folds: list[FoldButton | None] = []
        #: The title the card's `Why this relic` scrolls to (AK-379).
        self._slot_title: QLabel | None = None
        for group in _groups_of(result):
            title = _plain(group_heading(group))
            bold = title.font()
            bold.setBold(True)
            title.setFont(bold)
            art = (icons.item((relic_icons or {}).get(group.relic_name))
                   if icons is not None else None)
            _add_named(column, (art,), title)
            if group.slot_index == slot_index:
                self._slot_title = title
            count_line = _plain(group.count_line, colour=MUTED,
                                size=SMALL_TEXT)
            column.addWidget(count_line)
            # One holder per group at spacing 0: the lines used to be the
            # `<div>`s of one label, and a column gap between line widgets
            # would make the dialog taller than that label was (T-250b).
            # The numberless ones go into a second holder under their fold
            # (AK-372), in the order they had.
            lines = [WhyLine(line, filters, symbol=self._symbol_of(line.effect_id))
                     for line in group.lines]
            column.addWidget(_stacked(
                [line for line in lines if not is_numberless(line.line)]))
            folded = [line for line in lines if is_numberless(line.line)]
            fold = None
            if folded:
                hidden = _stacked(folded)
                fold = _numberless_fold(len(folded), hidden)
                column.addWidget(fold, 0, Qt.AlignLeft)
                column.addWidget(hidden)
            self.folds.append(fold)
            self.groups.append((title, count_line, lines))

        # AK-279/AK-301: the two marked sets, every marked id whether or not
        # this answer carries it, as a read-only overview -- one plain label
        # per list, heading and names as one statement, like `conditional`.
        self.excluded_list = _plain()
        self.required_list = _plain()
        self.stacks_list = _plain()
        column.addWidget(self.excluded_list)
        column.addWidget(self.required_list)
        column.addWidget(self.stacks_list)

        # One label rather than one per name: the heading and the names are
        # one statement, they are plain text throughout, and a label apiece
        # would put a paragraph gap between a heading and its own list.
        self.conditional = _plain()
        if result.not_counted:
            self.conditional.setText("\n".join(
                (CONDITIONAL_HEADING,) + tuple(result.not_counted)))
        self.conditional.setVisible(bool(result.not_counted))
        column.addWidget(self.conditional)

        self.legend = _plain(CURSE_LEGEND, colour=MUTED, size=SMALL_TEXT)
        self.legend.setVisible(_a_curse_is_drawn(result))
        column.addWidget(self.legend)
        self.mark_legend = _plain(MARK_LEGEND, colour=MUTED, size=SMALL_TEXT)
        column.addWidget(self.mark_legend)
        filters.changed.connect(self._show_the_marked_lists)
        self._show_the_marked_lists()

        # AK-375: behind one fold, open where it speaks of this run.
        self.footer = _plain(_footer_text(result), colour=MUTED,
                             size=SMALL_TEXT)
        self.notes_button: FoldButton | None = None
        if self.footer.text():
            self.notes_button = FoldButton(
                "Notes on these figures", "Hide notes on these figures",
                self.footer,
                opened=bool(result.unknowns or result.budget_note))
            column.addWidget(self.notes_button, 0, Qt.AlignLeft)
        else:
            self.footer.setVisible(False)
        column.addWidget(self.footer)

        column.addStretch()
        scroller.setWidget(page)
        outer.addWidget(scroller, 1)

        row = QHBoxLayout()
        row.addStretch()
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        row.addWidget(self.close_button)
        outer.addLayout(row)

    def _symbol_of(self, effect_id: int):
        """An effect's status symbol, or None."""
        if self._icons is None:
            return None
        return self._icons.status(
            iconpack.effect_icon(self._effects, effect_id))

    def showEvent(self, event) -> None:
        """AK-379: the card's dialog stands on its slot's group, title at the
        top -- once laid out, as only then has the title a place."""
        super().showEvent(event)
        if self._slot_title is not None:
            self.layout().activate()
            self.scroller.widget().layout().activate()
            bar = self.scroller.verticalScrollBar()
            bar.setValue(min(self._slot_title.y(), bar.maximum()))

    def _show_the_marked_lists(self) -> None:
        for label, heading, ids in (
                (self.excluded_list, EXCLUDED_HEADING,
                 self._filters.excluded),
                (self.required_list, REQUIRED_HEADING,
                 self._filters.required)):
            names = sorted(self._name_of(effect_id) for effect_id in ids)
            label.setText("\n".join((heading, *names)))
            label.setVisible(bool(ids))
        stacks = self._filters.counted_stacks(self._effects)
        self.stacks_list.setText("\n".join((STACKS_HEADING, *sorted(
            f"{self._name_of(effect_id)}: {count}"
            for effect_id, count in stacks.items()))))
        self.stacks_list.setVisible(bool(stacks))

    def _name_of(self, effect_id: int) -> str:
        return effect_name(self._effects, effect_id)


def _groups_of(result) -> tuple[types.SlotReasons, ...]:
    """The slot groups of the answer on screen, or none.

    An answer with no suggestion is 4.10 or 4.11 territory: the dialog still
    opens and still explains what it can, which is what `UI_SPEC` 4.10 asks
    of it.
    """
    if not result.suggestions:
        return ()
    return result.suggestions[0].reasons


def _a_curse_is_drawn(result) -> bool:
    """Is there a `✦` in this dialog for the legend to explain?

    Asked of the shape -- `is_curse` -- and not of the wording. §3 names the
    narrower condition "filling (ii) or (iii)", and those two are not
    distinguishable from filling (i) without reading the sentence, which
    AK-147 forbids. AK-141, which is the criterion that has to hold, asks for
    the sentence exactly once per dialog and in no block; drawn whenever a
    curse is drawn, it is the legend of a mark that is on screen.
    """
    return any(line.is_curse
               for group in _groups_of(result) for line in group.lines)


def _footer_text(result) -> str:
    """Point 4 of §3.4, then the budget note, then the data note.

    In the order they were handed over and **without** comparing, filtering,
    sorting or de-duplicating them (AK-165): the direction's own procedural
    sentences first (`Goal.scope`), then what this run left out, then the
    weighting note, then `budget_note` (AK-171) and last the data note.

    An empty `budget_note` draws nothing at all -- no heading, no placeholder,
    no dash (AK-170) -- and that falls out of joining only the sentences that
    are there.
    """
    goal = advisor_goals.GOALS.get(result.goal_id)
    parts = list(goal.scope) if goal is not None else []
    parts += list(result.unknowns)
    for note in (result.weights_note, result.budget_note, result.data_note):
        if note:
            parts.append(note)
    return "\n".join(parts)
