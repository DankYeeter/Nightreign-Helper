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

**Every text element states its format** (AK-29, D-10). Where a label draws no
markup of its own it is `Qt.PlainText`, which is the whole of the escaping
question for that label; where it draws the bullets and colours of
`RelicSlot._sync_mode` it is `Qt.RichText` and **every** string out of the
save or the game files goes through `html.escape` first. A tooltip has no
text format in Qt, so it is wrapped as rich text and escaped, which is the
only form that shows a name carrying `<b>` letter for letter (AK-30).

**The `Use` button, and nothing else.** Applying is one thing with one undo
model, so the block asks for it and does not do it: `use_requested` says the
player pressed it and the window is what puts the relic in the slot. The
button is drawn only where there is something to press it for -- a suggestion
that is already lying in the slot draws the one line of §3.2 and no control.

**The bullet is the marking control** (AK-276/AK-277). In the `Why` dialog
and on a picker card -- `MarkedLine`, shared by both -- the `•`/`✦` at the
head of a line is a flat `QToolButton` that cycles the effect through
neutral, `Don't include` and `Must include` (`effectfilters`). It is bound
to the effect **id**: every line about that id, in every open widget,
redraws from the one `EffectFilters.changed`, so two lines about one effect
never show two states. The compact block keeps its plain markup; it has no
room for a control (AK-160/AK-189) and the card's `Why` is one click away.
"""

from __future__ import annotations

import html
from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QDialog, QFrame, QHBoxLayout, QLabel,
                               QPushButton, QScrollArea, QSizePolicy,
                               QToolButton, QVBoxLayout, QWidget)

from . import effectfilters, effecttext
from .pressable import PRESS_KEYS
from .advisor import goals as advisor_goals
from .advisor import types

#: The one line a block shows when the suggestion is already lying in the slot
#: (`UI_SPEC` §3.2). Everything else falls away with it: there is nothing to
#: weigh and nothing to change.
ALREADY_EQUIPPED = "Already equipped — nothing to change here."

#: The legend for `✦`, once per `Why` dialog and in no block (AK-141).
CURSE_LEGEND = ("✦ marks a curse. A cost with no number beside it is still a "
                "cost — weigh it before you apply.")

#: The heading of the conditional list under the slot groups (4.9b).
CONDITIONAL_HEADING = ("These effects only apply under a condition, so this "
                       "ranking did not count them:")

#: The bullets, as `RelicSlot._sync_mode` draws them.
EFFECT_BULLET = "•"
CURSE_BULLET = "✦"
#: The bullet of a line the player marked `Must include` (AK-277).
REQUIRED_BULLET = "▲"

#: How a line is marked and what the marks mean, once per `Why` dialog and
#: once in the picker, always on screen (AK-297): the reader who needs it
#: most has not marked anything yet.
MARK_LEGEND = ("Click an effect's bullet to exclude it, click again to "
               "require it (▲), and once more to clear it.")

#: The headings of the two management lists under the slot groups (AK-279).
EXCLUDED_HEADING = "Effects you've excluded:"
REQUIRED_HEADING = "Effects you require:"

#: What the control says about its state and the next one (AK-277), by
#: `EffectFilters` kind; `None` is neutral.
MARK_TOOLTIPS = {
    None: ("Counts toward every suggestion. Click to exclude it, click "
           "again to require it."),
    effectfilters.EXCLUDED: ("Don't include — counts in no suggestion or "
                             "ranking. Click to require it instead."),
    effectfilters.REQUIRED: ("Must include — every suggestion carries this "
                             "effect. Click to clear it."),
}
#: The cycle a click runs: neutral, excluded, required, neutral.
NEXT_MARK = {None: effectfilters.EXCLUDED,
             effectfilters.EXCLUDED: effectfilters.REQUIRED,
             effectfilters.REQUIRED: None}

#: The colour `RelicSlot._sync_mode` gives a working rolled effect. A literal
#: there and a literal here on purpose: naming it in one place while the other
#: keeps the literal would be two names for one colour.
EFFECT_TEXT = "#cfcfcf"

#: The line height of an effect line, in px (`UI_SPEC` §3.2, AK-156).
SMALL_TEXT = 11


# --- one line, as the markup that draws it ---------------------------------

@dataclass(frozen=True)
class LineStyle:
    """How one line is drawn: the facts `line_markup` turns into markup and
    `MarkedLine` into a font and a stylesheet, so the two cannot disagree.
    `small` is the 11 px of a silent effect (AK-156)."""

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

    The two marked states override all four (AK-277): `Don't include` is
    exactly the dead-effect style, `Must include` is bold in `ACCENT` under
    `▲`. The bullet keeps its kind for an excluded curse, so it is still
    read as a curse.
    """
    from .app import ACCENT, BAD, CURSE, MUTED

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


def line_markup(line: types.ReasonLine) -> str:
    """One drawn line in its neutral shape, bullet and all -- the block's
    form, which carries no control."""
    style = _styled(line, None)
    text = html.escape(line.text)
    if style.struck:
        text = f"<s>{text}</s>"
    css = f"color:{style.colour}" + (f"; font-size:{SMALL_TEXT}px"
                                     if style.small else "")
    return f"<div style='{css}'>{style.bullet} {text}</div>"


def lines_markup(lines) -> str:
    """A run of drawn lines, in the order they were handed over."""
    return "".join(line_markup(line) for line in lines)


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


def _rich() -> QLabel:
    """A label that draws the bullets and colours itself, and says so."""
    label = QLabel()
    label.setTextFormat(Qt.RichText)
    label.setWordWrap(True)
    label.setStyleSheet("border: none;")
    return label


def _stacked(widgets) -> QWidget:
    """These widgets one under the other, as tight as lines of one label."""
    holder = QWidget()
    layout = QVBoxLayout(holder)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    for widget in widgets:
        layout.addWidget(widget)
    return holder


class MarkButton(QToolButton):
    """The bullet as a button Enter presses too (AK-278, DR-025).

    A `QToolButton` answers to Space alone; `pressable.PRESS_KEYS` is the
    catalogue every pressable thing in this program answers to, and this is
    the same rule as `PressableFrame.keyPressEvent`.
    """

    def keyPressEvent(self, event) -> None:  # noqa: N802 - Qt naming
        if event.key() in PRESS_KEYS:
            self.click()
            event.accept()
            return
        super().keyPressEvent(event)


class MarkedLine(QWidget):
    """One drawn line whose bullet is the marking control (AK-276/AK-277).

    The `MarkButton` stands where the bullet stood, at the line's own font
    height, so the line is no taller than a `QLabel` drawing the same text
    would be; `AutoRaise` and no border, so at rest it *is* the bullet. Tab
    reaches it, Space or Enter presses it (AK-278); the focus ring is drawn in
    `ACCENT`, because a stylesheet without a border takes Fusion's own ring
    with it.

    `size` is the line's font size in px, `0` for the widget default -- the
    `Why` dialog draws effect lines at the default and a picker card at
    `SMALL_TEXT`, and the bullet has to match the text beside it.
    """

    def __init__(self, line: types.ReasonLine,
                 filters: effectfilters.EffectFilters, *, size: int = 0,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        from .app import ACCENT

        self.line = line
        self._filters = filters
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(4)
        # Plain text and a font, not markup: the text is a name out of the
        # game files (AK-29), and a plain label is one px shorter than a
        # rich one -- the px AK-277 does not allow.
        self.label = _plain(line.text)
        self._base_font = QFont(self.label.font())
        if size:
            self._base_font.setPixelSize(size)
        self.mark = MarkButton()
        self.mark.setAutoRaise(True)
        self.mark.setCursor(Qt.PointingHandCursor)
        self._mark_css = (f"QToolButton {{ border: none; padding: 0; "
                          f"margin: 0; background: transparent; color: %s; "
                          f"}} QToolButton:focus {{ border: 1px solid "
                          f"{ACCENT}; }}")
        # The button is one bullet tall and one bullet wide, read off the
        # label's own metrics, so the line keeps a label's height (AK-277's
        # measure) and the text loses only the bullet's width.
        self._set_font(self.label, small=False)
        self._set_font(self.mark, small=False)
        metrics = self.label.fontMetrics()
        self.mark.setFixedSize(metrics.horizontalAdvance(REQUIRED_BULLET) + 4,
                               metrics.height())
        self.mark.clicked.connect(self._cycle)
        row.addWidget(self.mark, 0, Qt.AlignTop)
        row.addWidget(self.label, 1)
        filters.changed.connect(self._redraw)
        self._redraw()

    def kind(self) -> str | None:
        """Which of the two sets holds this line's effect, `None` for neutral."""
        if self.line.effect_id in self._filters.excluded:
            return effectfilters.EXCLUDED
        if self.line.effect_id in self._filters.required:
            return effectfilters.REQUIRED
        return None

    def _cycle(self) -> None:
        self._filters.mark(self.line.effect_id, NEXT_MARK[self.kind()])

    def _set_font(self, widget: QWidget, *, small: bool,
                  struck: bool = False, bold: bool = False) -> None:
        """The base font of this line with the state's marks on it -- from
        the base every time, so a state that ends takes its mark with it."""
        font = QFont(self._base_font)
        if small:
            font.setPixelSize(SMALL_TEXT)
        font.setStrikeOut(struck)
        font.setBold(bold)
        widget.setFont(font)

    def _redraw(self) -> None:
        kind = self.kind()
        style = _styled(self.line, kind)
        self.mark.setText(style.bullet)
        self.mark.setStyleSheet(self._mark_css % style.colour)
        self.mark.setToolTip(MARK_TOOLTIPS[kind])
        self.label.setStyleSheet(f"border: none; color: {style.colour};")
        self._set_font(self.label, small=style.small, struck=style.struck,
                       bold=style.bold)


# --- the block in the slot card --------------------------------------------

class SuggestionBlock(QFrame):
    """What the advisor would put in this slot, while the answer lives.

    The dashed border is the one `CustomRelicCard` already carries: in this
    program dashed means "planned, not real", which is exactly what a
    suggestion is until it is applied (`UI_SPEC` §3.2).

    Two controls, `Use` and `Why` (AK-274), and neither changes anything
    here: the block holds no relics, so it says the player asked and the
    window does the rest.
    """

    #: `Use` was pressed on this block (`UI_SPEC` §3.2: only this one slot).
    use_requested = Signal()
    #: `Why` was pressed on this block. Opens the one dialog the bar's own
    #: `Why` opens, with the same, whole content -- AK-274 forbids a second,
    #: card-only account of the answer.
    why_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        from .app import ACCENT, MUTED, PANEL, _heading

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
        # §3.2 draws the heading, `Use` and `Why` on one line, the buttons at
        # the right end of it. The stretch is what keeps them there and is
        # also why the row asks for no width of its own beyond the buttons
        # themselves: the heading is a `_heading`, which does not grow.
        head = QHBoxLayout()
        head.setContentsMargins(0, 0, 0, 0)
        head.addWidget(self.heading)
        head.addStretch()
        self.use_button = QPushButton("Use")
        self.use_button.clicked.connect(self.use_requested)
        head.addWidget(self.use_button)
        # AK-274: next to `Use`, never in its place.
        self.why_button = QPushButton("Why")
        self.why_button.clicked.connect(self.why_requested)
        head.addWidget(self.why_button)
        column.addLayout(head)

        self.relic_name = _plain()
        column.addWidget(self.relic_name)

        self.count_line = _plain(colour=MUTED, size=SMALL_TEXT)
        column.addWidget(self.count_line)

        self.lines = _rich()
        column.addWidget(self.lines)

        # Its own label rather than a filling of `count_line`: the one-line
        # case draws nothing else at all, and a shared label would have to be
        # emptied of a style as well as of a text.
        self.already_equipped = _plain(ALREADY_EQUIPPED, colour=MUTED,
                                       size=SMALL_TEXT)
        column.addWidget(self.already_equipped)

        self.setVisible(False)

    def show_the_suggestion(self, goal_label: str,
                            group: types.SlotReasons, *,
                            already_equipped: bool = False,
                            may_be_used: bool = True,
                            may_explain: bool = True,
                            curse_tooltip: str = "") -> None:
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
        so this never follows `may_be_used`.
        """
        self.heading.setText(f"Suggested — {goal_label}".upper())
        self.heading.setVisible(not already_equipped)
        self.use_button.setVisible(may_be_used and not already_equipped)
        self.why_button.setVisible(may_explain and not already_equipped)
        self.relic_name.setText(group.relic_name)
        self.relic_name.setVisible(not already_equipped)
        self.count_line.setText(group.count_line)
        self.count_line.setVisible(not already_equipped)
        drawn = [line for line in group.lines if types.drawn_in_the_block(line)]
        self.lines.setText(lines_markup(drawn))
        self.lines.setToolTip(as_a_tooltip(curse_tooltip))
        self.lines.setVisible(not already_equipped)
        self.already_equipped.setVisible(already_equipped)
        self.setVisible(True)

    def put_the_suggestion_away(self) -> None:
        """No answer lives for this slot any more."""
        self.lines.clear()
        self.lines.setToolTip("")
        self.relic_name.clear()
        self.count_line.clear()
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
                 effects: dict) -> None:
        super().__init__(parent)
        from .app import MUTED

        self._filters = filters
        self._effects = effects
        self.setModal(True)
        self.setWindowTitle(f"Why this build — {heading.goal_label}")
        self.resize(640, 620)

        outer = QVBoxLayout(self)
        scroller = QScrollArea()
        scroller.setWidgetResizable(True)
        scroller.setFrameShape(QFrame.NoFrame)
        page = QWidget()
        column = QVBoxLayout(page)
        column.setContentsMargins(0, 0, 6, 0)
        column.setSpacing(4)

        self.head = _plain(head_sentence(heading))
        column.addWidget(self.head)

        self.groups: list[tuple[QLabel, QLabel, list[MarkedLine]]] = []
        for group in _groups_of(result):
            title = _plain(group_heading(group))
            column.addWidget(title)
            count_line = _plain(group.count_line, colour=MUTED,
                                size=SMALL_TEXT)
            column.addWidget(count_line)
            # One holder per group at spacing 0: the lines used to be the
            # `<div>`s of one label, and a column gap between line widgets
            # would make the dialog taller than that label was (AK-277).
            lines = [MarkedLine(line, filters) for line in group.lines]
            column.addWidget(_stacked(lines))
            self.groups.append((title, count_line, lines))

        # AK-279: the marking's own two lists, every marked id whether or not
        # this answer carries it -- the way back from a marking made on a
        # card long since scrolled away. Rebuilt on every change, because a
        # click on one of their own lines takes that line out of the list.
        self.excluded_list = _stacked([])
        self.required_list = _stacked([])
        column.addWidget(self.excluded_list)
        column.addWidget(self.required_list)

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

        self.footer = _plain(_footer_text(result), colour=MUTED,
                             size=SMALL_TEXT)
        self.footer.setVisible(bool(self.footer.text()))
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

    def _show_the_marked_lists(self) -> None:
        for holder, heading, ids in (
                (self.excluded_list, EXCLUDED_HEADING,
                 self._filters.excluded),
                (self.required_list, REQUIRED_HEADING,
                 self._filters.required)):
            layout = holder.layout()
            while layout.count():
                gone = layout.takeAt(0).widget()
                gone.setParent(None)
                gone.deleteLater()
            if ids:
                layout.addWidget(_plain(heading))
                for effect_id in sorted(ids, key=self._name_of):
                    layout.addWidget(MarkedLine(
                        types.ReasonLine(slot_index=0, effect_id=effect_id,
                                         text=self._name_of(effect_id)),
                        self._filters))
            holder.setVisible(bool(ids))

    def _name_of(self, effect_id: int) -> str:
        """The display name, or the id for one the dataset has lost."""
        effect = self._effects.get(str(effect_id))
        return (effecttext.name(effect) if effect
                else f"effect {effect_id}")


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
