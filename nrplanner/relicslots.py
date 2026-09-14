"""The relic slot cards on the Build planner, and the chip that draws a slot.

A card holds one relic of the colour its chalice gives the slot, shows the
effects that relic rolled, and offers the picker over the relics the save
holds for that colour. The window builds the cards, hands each one its stock
and its callbacks, and reads their choices back; a card never reaches into
the window (AD-034).
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, QSignalBlocker, Qt, Signal
from PySide6.QtGui import (
    QColor, QLinearGradient, QPainter, QPixmap, QPolygonF, QRadialGradient,
)
from PySide6.QtWidgets import (
    QComboBox, QFrame, QHBoxLayout, QLabel, QPushButton, QToolButton,
    QVBoxLayout,
)

from . import advisorblock, chalices, effecttext, favourites, inventory, model

ACCENT = "#c8a45c"
MUTED = "#8a8a8a"
PANEL = "#1e1f23"
BORDER = "#2e2f35"
# The window's BAD: curses are a cost, and read in the same colour as one.
CURSE = "#d1655f"

SLOT_COLOURS = {
    0: "#b4544e",   # Red
    1: "#4e7ab4",   # Blue
    2: "#c2a24a",   # Yellow
    3: "#5c9e63",   # Green
    4: "#d8d8d8",   # White -- wildcard
}


# The slot-colour gems, by relic colour. White ships none -- the game has
# only four -- so it is drawn as a pale diamond to match.
SLOT_GEMS = {
    0: "MENU_MenuIcon_40480.png",
    1: "MENU_MenuIcon_40481.png",
    2: "MENU_MenuIcon_40483.png",   # Yellow
    3: "MENU_MenuIcon_40482.png",   # Green
}


# Drawn chips, keyed by what actually changes their pixels. Without this the
# vessel list redrew every slot of every vessel on each hero switch -- eleven
# vessels times six slots, each a scaled composite -- which took the import
# smoke test from seconds to minutes.
_CHIP_CACHE: dict[tuple, QPixmap] = {}


def slot_chip(icons, colour: int, owned=None, size: int = 26):
    """One relic slot, drawn the way the game presents it.

    A dark cell, a coloured glow rising from its floor, the relic sitting in
    it, and the colour gem in the corner. The gem matters precisely because a
    filled slot hides most of the glow -- which is why the game puts it there
    -- so it is drawn only when something is in the slot.

    The glow is drawn rather than extracted: the sprite atlas carries the
    gems and the relic art but no slot light, so this is the one piece with
    no authentic source, and it is generated to sit under the real ones.
    """
    key = (colour, size, getattr(owned, "icon", None) if owned else None)
    cached = _CHIP_CACHE.get(key)
    if cached is not None:
        return cached

    chip = QPixmap(size, size)
    chip.fill(Qt.transparent)
    tint = QColor(SLOT_COLOURS.get(colour, "#8a8a8a"))
    painter = QPainter(chip)
    painter.setRenderHint(QPainter.Antialiasing, True)

    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor("#15161a"))
    painter.drawRoundedRect(0, 0, size - 1, size - 1, 4, 4)

    # The light standing in the cell. The game renders this per frame -- it
    # is in no sprite anywhere in the menu atlas, which was searched
    # exhaustively -- so it is drawn.
    #
    # It is drawn small and scaled up, which is the whole trick: at a quarter
    # size the shapes are a few pixels across, and the smooth upscale turns
    # their edges into a gradient. Drawing at full size gives either a hard
    # triangle or visible rings, both of which read as a drawn shape rather
    # than as light -- each was tried and looked it.
    lit = 1.0 if owned is None else 0.5
    small = max(8, size // 4)
    layer = QPixmap(small, small)
    layer.fill(Qt.transparent)
    lp = QPainter(layer)
    lp.setRenderHint(QPainter.Antialiasing, True)
    lp.setPen(Qt.NoPen)

    cone = QLinearGradient(0, small * 0.88, 0, small * 0.18)
    base = QColor(tint).lighter(140); base.setAlpha(int(230 * lit))
    tip = QColor(tint); tip.setAlpha(0)
    cone.setColorAt(0.0, base)
    cone.setColorAt(1.0, tip)
    lp.setBrush(cone)
    lp.drawPolygon(QPolygonF([
        QPointF(small * 0.5, small * 0.12),
        QPointF(small * 0.88, small * 0.88),
        QPointF(small * 0.12, small * 0.88),
    ]))

    pool = QRadialGradient(small / 2, small * 0.82, small * 0.5)
    hot = QColor(tint).lighter(170); hot.setAlpha(int(245 * lit))
    pool.setColorAt(0.0, hot)
    rim = QColor(tint); rim.setAlpha(0)
    pool.setColorAt(1.0, rim)
    lp.setBrush(pool)
    lp.drawEllipse(QPointF(small / 2, small * 0.82),
                   small * 0.46, small * 0.20)
    lp.end()

    painter.setClipRect(1, 1, size - 2, size - 2)
    painter.drawPixmap(0, 0, layer.scaled(size, size, Qt.IgnoreAspectRatio,
                                          Qt.SmoothTransformation))
    painter.setClipping(False)

    if owned is not None and icons is not None:
        art = icons.item(getattr(owned, "icon", None))
        if art is not None:
            inner = int(size * 0.78)
            art = art.scaled(inner, inner, Qt.KeepAspectRatio,
                             Qt.SmoothTransformation)
            painter.drawPixmap((size - art.width()) // 2,
                               (size - art.height()) // 2 - 1, art)
        gem = icons.ui(SLOT_GEMS[colour]) if colour in SLOT_GEMS else None
        pip = max(7, size // 3)
        if gem is not None and not gem.isNull():
            gem = gem.scaled(pip, pip, Qt.KeepAspectRatio,
                             Qt.SmoothTransformation)
            painter.drawPixmap(size - pip - 1, size - pip - 1, gem)
        else:
            # White has no gem of its own; a plain diamond stands in for it.
            painter.save()
            painter.translate(size - pip / 2 - 2, size - pip / 2 - 2)
            painter.rotate(45)
            painter.setBrush(tint)
            painter.setPen(QColor("#00000060"))
            painter.drawRect(-pip // 3, -pip // 3, 2 * pip // 3, 2 * pip // 3)
            painter.restore()

    painter.setBrush(Qt.NoBrush)
    painter.setPen(QColor("#00000070"))
    painter.drawRoundedRect(0, 0, size - 1, size - 1, 4, 4)
    painter.end()
    _CHIP_CACHE[key] = chip
    return chip


def _same_copy(one, other) -> bool:
    """Whether two entries stand for the same physical relic.

    By copy_key where there is one -- the handle the save's loadout table
    uses, or the record's own place in the save. A relic with neither (a
    custom one, or an entry that never came out of a save) stands for itself
    and nothing else.
    """
    key = inventory.copy_key(one)
    if key is None:
        return one is other
    return key == inventory.copy_key(other)


def _relic_count(how_many: int) -> str:
    """"1 relic" or "4 relics", because "1 relics" was on screen."""
    return "1 relic" if how_many == 1 else f"{how_many} relics"


def _custom_effects(roll: str) -> list[int] | None:
    """The effects a stored slot names, when what it names is a custom relic.

    A custom relic is owned by nobody, so a build naming one cannot be put
    back by looking it up: it is built again out of what was written down.
    None for every other relic, which is looked up rather than rebuilt.
    """
    parts = favourites.parts(roll)
    if parts is None or parts[0] != inventory.CUSTOM_RELIC_ID:
        return None
    return parts[1]


#: What a held slot's button says, unchecked and checked (`UI_SPEC` §4.1 of
#: the T-024 section, AK-54). Words rather than a padlock: a padlock reads
#: "you cannot change this", and a hold binds the **advisor**, not the player.
HOLD_CAPTIONS = ("Hold", "Held")

#: The tooltip of that button, verbatim (AK-54). The second sentence is the
#: meaning of the control and the third is AK-59's whole subject -- neither is
#: decoration, and neither may be dropped to shorten the line.
HOLD_TOOLTIP = ("Optimize leaves this slot alone. You can still change it "
                "yourself. Holds are forgotten when the program closes.")

#: What a slot held with nothing in it says (§4.2, AK-55). "Held and staying
#: empty" is a different instruction from "free", and the search has to be
#: able to tell them apart (`types.HeldSlot`), so the player does too.
HELD_EMPTY = "Held empty — Optimize will not fill this slot."

#: The line an empty slot card carries while the first read is still out
#: (§9 (c)). Related to the picker's `Your relics appear here.` and not the
#: same sentence: there the empty surface is a grid, here it is one card, and
#: the difference is in the subordinate clause.
RELICS_AFTER_THE_SAVE = "Your relics appear when the save has been read."


class RelicSlot(QFrame):
    """One relic slot: a fixed colour from the chalice, up to three effects."""

    #: The window handed this card another stock. A picker standing open
    #: over the card redraws on it (AK-267): the read runs in a thread and
    #: its ending is delivered into the dialog's own event loop.
    stock_replaced = Signal()

    def __init__(self, index: int, deep: bool, on_change, icons=None,
                 on_search_changed=None, taken_elsewhere=None,
                 on_hold_changed=None):
        super().__init__()
        self.index = index
        self.deep = deep
        self.on_change = on_change
        self.icons = icons
        self.on_search_changed = on_search_changed or (lambda _text: None)
        # Which physical relics the other slots are already holding. A slot on
        # its own knows of no others and so blocks nothing.
        self.taken_elsewhere = taken_elsewhere or (lambda _slot: frozenset())
        # Said when the player works the `Hold` button, never when the window
        # draws it: the hold itself lives at the window (AD-017.1), and a card
        # that told the window about a state the window had just handed it
        # would be writing over what it was drawing.
        self.on_hold_changed = on_hold_changed or (lambda _slot, _on: None)
        self.search_text = ""
        # Why this slot is empty, when it was emptied for a reason worth
        # saying. An empty slot otherwise looks the same whether nothing was
        # ever put in it or its relic was taken away by a rule.
        self.empty_reason = ""
        # The condition that reason describes, where it is a condition about
        # something other than this slot. Kept beside the text and asked again
        # at every redraw: a reason that has stopped being true is not a
        # reason, it is a leftover (QA-022).
        self.reason_holds = None
        # Is a read of the save out at this moment? The card draws two things
        # from it and nothing else keeps it: the relic button is shut while it
        # is true (AK-223), and while it is true *and* nothing has been read
        # yet the empty card says why it is empty (AK-221). Written by the
        # window, which is the one place that knows.
        self.the_save_is_being_read = False
        self.owned = None
        self.colour = 0
        self.pool: list[dict] = []
        self.effect_by_id: dict[int, dict] = {}
        self.all_effects: list[dict] = []
        self.custom_item = None
        self.hero_name = ""

        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(
            f"QFrame {{ background: {PANEL}; border: 1px solid {BORDER};"
            f" border-radius: 6px; }}"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 10)
        layout.setSpacing(5)

        header = QHBoxLayout()
        self.title = QLabel()
        self.title.setStyleSheet("font-weight: bold; border: none;")
        header.addWidget(self.title)
        header.addStretch()
        # §4.1: a checkable button carrying a word, in the card's own header
        # and left of the colour chip. The two states are told apart by the
        # word first and by the colour second, so a player who cannot tell
        # `MUTED` from `ACCENT` still reads which one this is.
        self.hold_button = QToolButton()
        self.hold_button.setCheckable(True)
        self.hold_button.setToolTip(HOLD_TOOLTIP)
        self.hold_button.setStyleSheet(
            f"QToolButton {{ color: {MUTED}; border: none;"
            f" padding: 1px 6px; }}"
            f"QToolButton:checked {{ color: {ACCENT};"
            f" border: 1px solid {ACCENT}; border-radius: 3px; }}"
        )
        self.hold_button.toggled.connect(self._hold_toggled)
        header.addWidget(self.hold_button)
        self.chip = QLabel()
        self.chip.setFixedSize(14, 14)
        header.addWidget(self.chip)
        layout.addLayout(header)

        # A slot holds a relic you own, exactly as in game: the effects come
        # with the relic and cannot be mixed and matched. The combo is kept as
        # hidden state so the visible control can be a proper icon grid.
        self.relic_box = QComboBox()
        self.relic_box.setVisible(False)
        self.relic_box.currentIndexChanged.connect(self._on_relic_changed)
        layout.addWidget(self.relic_box)

        self.choose_button = QPushButton("Empty slot")
        self.choose_button.setStyleSheet("text-align: left; padding: 6px 8px;")
        self.choose_button.clicked.connect(self._open_picker)
        layout.addWidget(self.choose_button)

        self.rolled_label = QLabel()
        self.rolled_label.setWordWrap(True)
        self.rolled_label.setStyleSheet("border: none;")
        layout.addWidget(self.rolled_label)

        # The advisor's block, under the rolled effects and inside the card:
        # a suggestion for this slot belongs where the slot is (`UI_SPEC`
        # §3.2). Built here and hidden rather than created on demand, so that
        # an answer arriving does not change the card's layout order.
        self.suggestion = advisorblock.SuggestionBlock()
        layout.addWidget(self.suggestion)

        # Last, because it draws the card: the caption of the hold button and
        # the line an empty held slot carries are both `_sync_mode`'s work,
        # and `_sync_mode` reads widgets built above.
        self._draw_the_hold()

    # -- state -----------------------------------------------------------
    def _on_relic_changed(self, *_args) -> None:
        # Whatever this slot was last told to say about being empty is spent:
        # the player has just put something here or taken it away themselves.
        self.empty_reason = ""
        self.reason_holds = None
        self._sync_mode()
        self.on_change()

    def _open_picker(self) -> None:
        from .relicpicker import RelicPicker

        dialog = RelicPicker(
            self, self.icons, self.search_text, self.on_search_changed
        )
        if dialog.exec() and dialog.chosen is not None:
            index = self.relic_box.findData(dialog.chosen)
            if index >= 0:
                self.relic_box.setCurrentIndex(index)
        elif dialog.chosen is None and dialog.result():
            self.relic_box.setCurrentIndex(0)

    # -- holding ----------------------------------------------------------
    def is_held(self) -> bool:
        """Is the advisor being told to leave this slot alone?

        The button is the one place this is drawn and the one place it is
        read: the window keeps the hold and hands it here, and asking two
        places for one fact is how they come to disagree.
        """
        return self.hold_button.isChecked()

    def show_the_hold(self, on: bool) -> None:
        """Draw the hold the window is holding for this slot.

        Signals blocked, because this is the window telling the card. Left
        unblocked, the card would tell the window straight back and would
        overwrite the state it was being handed -- and on a change of vessel
        it would overwrite it with the vessel being left.
        """
        with QSignalBlocker(self.hold_button):
            self.hold_button.setChecked(on)
        self._draw_the_hold()

    def _hold_toggled(self, on: bool) -> None:
        """The player worked the button, so the window is told."""
        self._draw_the_hold()
        self.on_hold_changed(self, on)

    def _draw_the_hold(self) -> None:
        """The caption, and the line an empty held slot carries (AK-55)."""
        self.hold_button.setText(HOLD_CAPTIONS[self.is_held()])
        self._sync_mode()

    def _forget_a_spent_reason(self) -> None:
        """Drop the reason for being empty once it has stopped being true."""
        if self.empty_reason and self.reason_holds is not None:
            if not self.reason_holds():
                self.empty_reason = ""
                self.reason_holds = None

    def show_the_save_is_being_read(self, on: bool) -> None:
        """Draw the read the window is waiting for, or the end of it.

        Both halves of it at once, because they begin and end together: the
        button that would open a picker with nothing in it, and the line that
        says why the card is empty. Nothing else on the card moves.
        """
        self.the_save_is_being_read = on
        self._sync_mode()

    def _sync_mode(self) -> None:
        """Show the rolled effects of the relic currently in this slot."""
        self._forget_a_spent_reason()
        item = self.relic_box.currentData()
        self.choose_button.setText(item.name if item is not None else "Empty slot")
        # Shut for as long as the read is out, in both situations (AK-223):
        # at the start it would open on nothing, and on a `Rescan` the stock
        # under its cards is replaced while it stands.
        self.choose_button.setEnabled(not self.the_save_is_being_read)
        if item is None:
            # An empty slot says nothing unless it was emptied for a reason,
            # or unless it is being held empty on purpose. A slot whose relic
            # is worn elsewhere used to read exactly like one never filled,
            # leaving the player to work out where the relic went (DR-002).
            #
            # Both lines can stand at once and both are then true: "the
            # advisor will not fill this" and "this is why it is empty" are
            # different statements, and dropping either would answer a
            # question the player did not ask.
            # The third line of the same kind, and it is a condition rather
            # than a stored reason (§9 (c)). It cannot be put into
            # `empty_reason`: the chalice restore that runs moments after a
            # read begins calls `clear_relic()` on every slot, which is what
            # a stored reason is for and would wipe this one -- so the card
            # would fall silent exactly during the state the line is about.
            # Same `MUTED` line in the same label as the other two (§10).
            waiting = self.the_save_is_being_read and self.owned is None
            said = ([HELD_EMPTY] if self.is_held() else []) + (
                [self.empty_reason] if self.empty_reason else []) + (
                [RELICS_AFTER_THE_SAVE] if waiting else [])
            self.rolled_label.setText("".join(
                f"<div style='color:{MUTED}'>{line}</div>" for line in said))
            self.rolled_label.setVisible(bool(said))
            return

        lines = []
        for eid in item.effect_ids:
            eff = self.effect_by_id.get(eid)
            name = effecttext.name(eff) if eff else f"<{eid}>"
            mark = "" if not eff or eff["stacks"] else "  ⚠"
            colour = "#d1655f" if eff and eff.get("is_curse") else "#cfcfcf"
            # An effect belonging to another Nightfarer is doing nothing at
            # all here. Say so on the slot rather than letting it sit among
            # the working rolls looking identical to them.
            if eff is not None and not effecttext.works_for(eff, self.hero_name):
                who = effecttext.owner(eff) or "another Nightfarer"
                lines.append(
                    f"<div style='color:{CURSE}'>&bull; <s>{name}</s>"
                    f" — not working ({who} only)</div>"
                )
                continue
            lines.append(f"<div style='color:{colour}'>&bull; {name}{mark}</div>")
        if not lines:
            lines = ["<div style='color:#8a8a8a'>no rolled effects</div>"]
        lines.extend(self.curse_lines(item))
        self.rolled_label.setText("".join(lines))
        self.rolled_label.setToolTip(self.curse_tooltip(item))
        self.rolled_label.setVisible(True)

    def curse_lines(self, item) -> list[str]:
        """The curses this relic actually carries, named rather than hinted at.

        A relic that came out of the save knows exactly which curses it rolled,
        so say so. One that does not -- a template the player has never picked
        up -- can only report that it has curse slots at all.
        """
        curse_ids = list(getattr(item, "curse_ids", ()) or ())
        if curse_ids:
            out = []
            for cid in curse_ids:
                eff = self.effect_by_id.get(cid)
                name = effecttext.name(eff) if eff else f"<{cid}>"
                out.append(f"<div style='color:{CURSE}'>✦ {name}</div>")
            return out
        if getattr(item, "has_curse", False):
            count = getattr(item, "curse_count", 0) or 0
            what = f"{count} curses" if count > 1 else "a curse"
            return [f"<div style='color:{CURSE}'>✦ comes with {what}</div>"]
        return []

    def show_the_suggestion(self, goal_label: str, reading: str, group,
                            choice, *, may_explain: bool = True) -> None:
        """Draw what the advisor would put here, while the answer lives.

        Whether the suggestion is already lying in this slot is decided on
        the **handle** -- the save's own identifier for one physical copy --
        and never on the name: several copies of one relic are owned with
        different rolls, and this save equips the second copy of The Wylder's
        Earring while the first sits unused (`select_copy`, QA-021).

        `may_explain` is the window's own reading of the bar's `Why` gate
        (AK-274), passed straight through: it names the same fact for every
        slot at once, and this card has no state of its own to add to it.
        """
        in_the_slot = getattr(self.relic_box.currentData(), "handle", None)
        already = (choice is not None and in_the_slot is not None
                   and in_the_slot == choice.handle)
        self.suggestion.show_the_suggestion(
            goal_label, reading, group, already_equipped=already,
            may_be_used=not self.is_held(), may_explain=may_explain,
            curse_tooltip=self._suggested_curse_tooltip(choice))

    def put_the_suggestion_away(self) -> None:
        """No answer names this slot any more."""
        self.suggestion.put_the_suggestion_away()

    def _suggested_curse_tooltip(self, choice) -> str:
        """The full wording of the suggested copy's curses, found by handle.

        The block's lines name the curses; what each one does is the same
        tooltip the slot already offers for the relic it holds, so a player
        reads a curse the same way whether it is equipped or offered.
        """
        if choice is None:
            return ""
        copy = next((item for item in self._holdable()
                     if item.handle == choice.handle), None)
        return "" if copy is None else self.curse_tooltip(copy)

    def curse_tooltip(self, item) -> str:
        """Full wording for each curse, so the cost is legible not cryptic."""
        curse_ids = list(getattr(item, "curse_ids", ()) or ())
        if not curse_ids:
            return ""
        parts = ["This relic's curses:"]
        for cid in curse_ids:
            eff = self.effect_by_id.get(cid)
            if eff is None:
                parts.append(f"  • <{cid}>")
                continue
            parts.append(f"  • {effecttext.name(eff)}")
            parts.append(f"      {effecttext.describe_full(eff)}")
        return "\n".join(parts)

    def set_colour(self, colour: int, all_effects: list[dict], owned=None,
                   hero_name: str = "") -> None:
        """Give this slot the colour the chalice says it has, and rebuild it.

        Runs on every apply of the chalice, the Deep of Night switch included,
        and most of those applies leave this slot's colour exactly as it was.
        """
        self.hero_name = hero_name or self.hero_name
        # A custom relic is built for one slot colour, so a colour that has
        # really changed invalidates it -- and nothing else does. Dropping it
        # on every rebuild deleted the relic the player had planned at one
        # click on the Deep switch, took its effects out of the totals, and
        # left the key the build had written down for it behind, redeemable
        # by nothing ever again (QA-025). A slot's mode is fixed when the slot
        # is built, so the colour is the whole of the question.
        if colour != self.colour:
            self.custom_item = None
        self.colour = colour
        self.owned = owned
        self.all_effects = list(all_effects)
        self.effect_by_id = {e["id"]: e for e in all_effects}
        self.chip.setStyleSheet(
            f"background: {SLOT_COLOURS.get(colour, '#888')};"
            f" border: 1px solid {BORDER}; border-radius: 7px;"
        )
        self.populate()

    def effect_names(self, item) -> list[str]:
        return [
            effecttext.name(self.effect_by_id.get(e) or {"name": f"<{e}>"})
            for e in item.effect_ids
        ]

    def curse_names(self, item) -> list[str]:
        """The names of the curses this relic actually rolled.

        Kept apart from `effect_names` -- that list feeds the card's effect
        block, and a curse already gets its own `✦ ...` block from
        `_curses` (`relicpicker.py`); joining them there would show a curse
        twice. This one exists so the search haystack can include what the
        card's curse block shows (QA-264).
        """
        return [
            effecttext.name(self.effect_by_id.get(c) or {"name": f"<{c}>"})
            for c in getattr(item, "curse_ids", ()) or ()
        ]

    def rollable_effects(self) -> list[dict]:
        """Effects that can legitimately appear on a relic in this slot.

        Drawn from what the game says can roll in this colour and mode, not
        from what the player happens to own -- the whole point of a custom
        relic is to plan around one they have not found yet. A White slot
        takes any colour, so it accepts everything.
        """
        key = "deep_colours" if self.deep else "colours"
        out = []
        for eff in self.all_effects:
            colours = eff.get(key) or []
            if not colours:
                continue
            if self.colour == model.WHITE_SLOT or self.colour in colours:
                out.append(eff)
        return sorted(out, key=effecttext.name)

    def set_custom(self, effect_ids: list[int]) -> None:
        """Put a made-up relic in this slot, or clear it when given nothing.

        What the player does in the picker. The window is told once, at the
        end, the way it is told about any other relic landing in a slot.
        """
        self._hold_custom(effect_ids)
        self.on_change()

    def adopt_custom(self, effect_ids: list[int]) -> bool:
        """Rebuild this slot's custom relic from a stored build, silently.

        A custom relic is owned by nobody, so a build that names one cannot be
        put back by looking it up -- there is nothing to look it up in. It is
        rebuilt here out of the effects the build wrote down, which is what
        lets it outlive a session or a chalice the player wandered through
        (QA-025).

        Refused when this slot could not have rolled those effects: a relic
        built for a Red slot has no business reappearing in a Blue one. Asked
        here and not in `set_custom` because the two are asked by different
        parties -- the picker offers the player the effects this slot can roll
        and nothing else, while a stored build was written down when the slot
        may have had another colour entirely.

        Emits nothing. A restore is one change to the build, not one per slot.
        """
        rollable = {e["id"] for e in self.rollable_effects()}
        if not all(eid in rollable for eid in effect_ids):
            return False
        self._hold_custom(effect_ids)
        return True

    def _hold_custom(self, effect_ids: list[int]) -> None:
        """Put a made-up relic in this slot, or clear it when given nothing."""
        if not effect_ids:
            self.custom_item = None
            self.populate()
            return
        self.custom_item = inventory.OwnedItem(
            relic_id=inventory.CUSTOM_RELIC_ID,
            name="Custom relic",
            colour=self.colour,
            effect_ids=list(effect_ids),
            is_deep=self.deep,
        )
        self.populate()
        index = self.relic_box.findData(self.custom_item)
        if index >= 0:
            self._select_index(index)

    def available_items(self) -> list:
        """The relics this slot may be given.

        Owned, of a colour and mode this slot takes, and not already lying in
        another slot: a relic is one physical object and cannot be worn twice.
        It used to be offered everywhere it fit, and taking the same entry
        into two slots counted its effects twice -- silently, with no warning
        and a plausible total (QA-002). With 306 distinct rolls across 309
        owned relics, an entry in this list stands for exactly one physical
        relic 99 times out of 100, so the second helping was almost never real.
        Planning around a relic you do not own is what "Custom relic" is for,
        and that stays untouched.

        The ownership filter runs *before* the collapse to one entry per roll,
        not after: a player who owns two copies of the same roll may wear both,
        and the second copy has to survive to be offered.

        The collapse is a way of showing relics, not a way of counting them.
        One entry stands for one roll, and while the first copy of that roll
        is free the second is behind it, unreachable by anything that asks
        this list. A build names *copies*, so the restore asks by handle and
        reaches past this list to the copy itself (see `select_copy`) --
        reading a build out of this list put one physical relic in two slots
        and emptied the later one (QA-021).
        """
        taken = self.taken_elsewhere(self)
        free = [item for item in self._holdable()
                if inventory.copy_key(item) not in taken]
        # The same collapse the picker applies, or the header counts the
        # save's records while the picker counts distinct rolls and the
        # two sit one apart on screen ("50 owned" over "49 of 49").
        return favourites.distinct(free)

    def _holdable(self) -> list:
        """Every owned copy this slot could take: its colour, its mode.

        One entry per physical relic, before anything is collapsed away. Both
        questions this slot answers about a relic -- may it be offered, and is
        this the copy a build names -- are asked of this list, so the two
        cannot come to mean different things by one relic.
        """
        if self.owned is None:
            return []
        return self.owned.relics_for(self.colour, self.deep, model.WHITE_SLOT)

    def slot_name(self) -> str:
        """What this slot is called on screen, and in anything said about it."""
        return f"{'Deep ' if self.deep else ''}Slot {self.index + 1}"

    def _may_hold(self, item) -> bool:
        """Whether this slot could take this relic at all: colour and mode.

        Asked about the relic already in the slot, which stays in the list
        whatever else is being filtered out -- but not past a change of
        chalice. A relic of a colour this slot no longer takes belongs to the
        chalice before it, and keeping such a relic is how a Grail came to own
        one nobody put there.

        Asked about owned relics only. A custom relic is owned by nobody and
        is answered for one line earlier, by `custom_item`: it is this slot's
        own, it is put in the list by `populate` itself, and giving this
        function a second opinion about it would be two answers to one
        question (QA-016).
        """
        if item is None:
            return False
        return any(_same_copy(item, other) for other in self._holdable())

    def _label(self, item) -> str:
        """One line for the list: the relic's name and what it rolled."""
        summary = ", ".join(self.effect_names(item))
        return (f"{item.name} — {summary}" if summary else item.name)[:120]

    def populate(self) -> None:
        """List the relics this slot may be given, and the one it has.

        What a slot may be given is a question of ownership, colour and mode.
        Narrowing it by effect is the picker's work: there a filter changes
        what is being *chosen from* and can disturb nothing that is already
        equipped. Applied here it dropped the relic out of a slot the moment
        it stopped matching, and the loss was written down (QA-013) -- one
        mistyped word in the picker emptied every other slot.

        Whatever is in the slot is in the slot's own list, however that list
        was arrived at. The rule is enforced here rather than trusted to the
        callers: two of them already carry a comment saying that narrowing a
        slot from outside is what makes an equipped relic disappear, and a
        third arrived and did it anyway, for an unrelated reason.
        """
        worn = self.relic_box.currentData()
        items = self.available_items()
        if (worn is not None and worn is not self.custom_item
                and self._may_hold(worn)
                and not any(_same_copy(worn, item) for item in items)):
            items = items + [worn]

        with QSignalBlocker(self.relic_box):
            self.relic_box.clear()
            self.relic_box.addItem("Empty slot", None)
            # A custom relic is not owned, so it survives repopulation only by
            # being re-added here.
            if self.custom_item is not None:
                self.relic_box.addItem(
                    self._label(self.custom_item), self.custom_item)
            for item in items:
                self.relic_box.addItem(self._label(item), item)
            if worn is not None:
                idx = self.relic_box.findData(worn)
                if idx >= 0:
                    self.relic_box.setCurrentIndex(idx)

        # "available" rather than "owned": a relic lying in another slot is
        # owned and is not offered here, so counting it would put a number on
        # the heading that the list underneath contradicts.
        #
        # No stock, no bracket (AK-222). While nothing has been read the
        # number is not zero, it is unknown, and `(0 available)` would be a
        # claim about what the player owns that the program cannot support
        # (A7) -- and it is the shape that reads like lost data.
        count = "" if self.owned is None else f"  ({len(items)} available)"
        self.title.setText(
            f"{self.slot_name()} — "
            f"{model.COLOUR_NAMES.get(self.colour, self.colour)}"
            f"{count}"
        )
        self._sync_mode()

    def clear_relic(self, reason: str = "", while_true=None) -> None:
        """Take whatever is in this slot out of it, and say why if there is a why.

        `while_true` is the condition the reason describes, asked again every
        time the slot is redrawn. "Already worn in Slot 1" is a statement
        about slot 1, and it was kept as a property of this one: it stayed on
        screen after slot 1 had given the relic up or been filled with
        another, so the text was false exactly when the player did what it
        asked (QA-022). A reason with no condition holds until the slot is
        changed, which is what the ones about this slot alone need.

        Signals are held back. A slot emptied during a restore is part of
        setting one build, not six separate changes by the player, and the
        window settles the slots itself once the restore has finished.
        """
        self.empty_reason = reason
        self.reason_holds = while_true
        with QSignalBlocker(self.relic_box):
            self.relic_box.setCurrentIndex(0)
        self._sync_mode()

    def selected_ids(self) -> list[int]:
        item = self.relic_box.currentData()
        return list(item.effect_ids) if item is not None else []

    def current_relic(self):
        """The relic sitting in this slot, or None.

        Named deliberately: `self.owned` is the whole inventory, not the
        chosen relic, and reading it as the relic is a mistake already made
        once -- it renders as a filled slot with no art in it.
        """
        return self.relic_box.currentData()

    def saved_key(self) -> str:
        """How this slot's relic is written down for the next session."""
        return chalices.slot_key(self.relic_box.currentData())

    def select_copy(self, handle: int) -> bool:
        """Put one exact physical copy in this slot, list or no list.

        Matching on the handle rather than the name matters: several copies of
        one relic can be owned with different rolls, and this save equips the
        second copy of The Wylder's Earring while the first sits unused.

        The list is not asked, it is only tried first. It holds one entry per
        roll, so a second copy of a roll is not in it -- and a build naming
        that copy fell through to the roll, landed on the first copy, and left
        two slots holding one relic, the later of which was then emptied and
        the loss stored (QA-021). What identifies a copy here is the handle,
        which is what `copy_key` and `_settle_slots` mean by "the same relic"
        as well.

        Signals are held back so importing six slots recomputes the build once
        at the end rather than six times.
        """
        # A relic with no handle is not identified by one, and the custom
        # relic has none: asked for "the copy with handle None", this would
        # otherwise hand back whatever the player had invented.
        if handle is None:
            return False
        for i in range(self.relic_box.count()):
            item = self.relic_box.itemData(i)
            if item is not None and getattr(item, "handle", None) == handle:
                self._select_index(i)
                return True
        copy = next((item for item in self._holdable()
                     if getattr(item, "handle", None) == handle), None)
        if copy is None:
            return False
        self._select_index(self._offer(copy))
        return True

    def select_roll(self, roll: str, taken=frozenset()) -> bool:
        """Put back a relic named by its roll alone, avoiding copies spoken for.

        The fallback for a build stored before the save was rewritten: handles
        are renumbered by the game, and a build that came back empty every
        time the player melted an unrelated relic would not be worth storing.

        `taken` are the copies other slots of this same build have already
        been given. Without it two slots asking for one roll are both answered
        with the first copy -- the same loss as QA-021 by another road, and
        the more so because the player may own the roll twice and be entitled
        to both.
        """
        for i in range(self.relic_box.count()):
            item = self.relic_box.itemData(i)
            if (item is not None and favourites.key(item) == roll
                    and inventory.copy_key(item) not in taken):
                self._select_index(i)
                return True
        for item in self._holdable():
            if (favourites.key(item) == roll
                    and inventory.copy_key(item) not in taken):
                self._select_index(self._offer(item))
                return True
        return False

    def _offer(self, item) -> int:
        """Add one relic to the end of this slot's list, and say where it went.

        For a copy the collapsed list has no entry of its own for. The next
        `populate` draws the list up again from what the slots hold by then,
        and keeps whatever is in this one.
        """
        with QSignalBlocker(self.relic_box):
            self.relic_box.addItem(self._label(item), item)
        return self.relic_box.count() - 1

    def _select_index(self, index: int) -> None:
        """Make one entry of the list the one in the slot, without emitting.

        Whatever this slot was last told to say about being empty is spent: it
        is not empty now.
        """
        self.empty_reason = ""
        self.reason_holds = None
        with QSignalBlocker(self.relic_box):
            self.relic_box.setCurrentIndex(index)
        self._sync_mode()
