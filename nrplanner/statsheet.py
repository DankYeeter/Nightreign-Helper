"""The stat sheet: the right-hand pane of the Build planner.

Base stats, attributes, the six armament tiles with the damage panel under
them, resistances, multipliers, the condition switches, flat bonuses, curses
and the stacking warnings -- everything the window draws out of a
`model.Build`. The sheet reads the window through its query methods
(`current_hero()`, `active_slot()`, `selected_effects()`, ...) and writes
nothing back: a moved condition switch goes out as `declared_changed`, and
the window, which owns `declared`, recomputes (AD-034).
"""

from __future__ import annotations

import html

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QCursor, QFont
from PySide6.QtWidgets import (
    QCheckBox, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QScrollArea, QToolButton, QToolTip, QVBoxLayout, QWidget,
)

from . import (castingbar, damage, effecttext, iconpack, model, relicslots,
               weapons, weaponslots)
from .theme import ACCENT, BAD, GOOD, MUTED

# Link target for the weapon attack-rating breakdown. Not a modifier field, so
# it is namespaced to keep it out of the way of the real ones.
AR_BREAKDOWN_KEY = "ar:total"

# The second such key, for the spell-damage click-through (AK-361): the
# rates behind the figure, and why a 0.00 is one, are shown when the player
# asks for them, the way this panel already shows the attack rating's, rather
# than as a third standing line under every catalyst tile.
SPELL_BREAKDOWN_KEY = "spell:total"

#: AK-356: the Weapon art row of a staff or a seal. The game ranks a catalyst
#: on the spell power it prints for it and no attack art reaches that figure
#: (AD-048/AD-053 point 5), so the row says so where its number would be --
#: a statement here rather than the refusal of a choice
#: (`goals._ART_ON_A_CATALYST`), because this panel has no box to refuse.
#: The art names itself out of `model.ART_LABELS` (AK-363).
ART_ON_A_CATALYST = (
    "{art} — not shown: a staff or a seal is ranked on the spell power the "
    "game shows for it, and no attack art reaches that figure.")

# -- what counts as visible on this screen ------------------------------
#
# Three thresholds, and each one is half of the smallest unit its own display
# can print. They say "this is not distinguishable from zero **on screen**",
# which is a property of the display and not of the game (`UI_SPEC.md` AK-65,
# QA-117).
#
# **They do not move with a calibration factor and must not be made to.**
# `weapons.GAME_ATTACK_POWER_RATE` made every attack figure 0.6 times what it
# was, which moved 89 `From attributes` rows below the first of these and
# turned 66 change cells into a dash; scaling the threshold to 0.3 alongside
# it would keep no set of cases the same -- rounding a sum of several damage
# types does not scale linearly with a factor -- and would translate a
# property of the calibration into a property of the display. Under the
# threshold the change shown really **is** zero, which is the same honesty
# rule that writes `no change` instead of `+0.0`.
#
# Half of one, for a figure printed as a whole number (`f"{x:+.0f}"`).
VISIBLE_CHANGE = 0.5
# Half of a tenth, for a share printed with one decimal (`f"{x:+.1f}%"`).
VISIBLE_PERCENT = 0.05
# What earns a change cell a colour rather than the muted grey. Not a
# rounding boundary at all: a figure below it prints as `+0` or `-0`, and
# green or red on a zero would tell the player something moved when nothing
# did. Small enough that everything the display can distinguish is coloured.
COLOURED_CHANGE = 0.05


#: What the hand switch says, one-handed and two-handed -- the abbreviation
#: the attack figure already uses (`damage.TWO_HANDED_MARK`, AK-286), so
#: there is one spelling for the hand (AK-292).
HAND_CAPTIONS = ("1H", "2H")

#: The tooltip of that switch, one text for both states (AK-292/AK-299).
HAND_TOOLTIP = ("Ranks the build's attack power 1H or 2H — Optimize and "
                "effects that only read while two-handing follow this "
                "switch, and the figure it uses is the one highlighted and "
                "tagged 1H or 2H on every tile, sheet and arsenal row. "
                "Armaments that cannot be two-handed keep their 1H figure "
                "either way. Saved with this build.")


class HandSwitch(QToolButton):
    """The `1H`/`2H` button: one for the whole build, not one per tile (AK-292).

    Which hand the advisor ranks is one value per build (AN-2). The button
    changes no figure on screen -- both hands stay side by side (AK-286) --
    and it wears the look of the `Hold` button (AK-54). The caption follows
    the check state in `checkStateSet`, which Qt runs for a click and for a
    `setChecked` alike, so a stored build put on the switch with its signals
    held still reads right.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setCheckable(True)
        self.setToolTip(HAND_TOOLTIP)
        self.setStyleSheet(relicslots.WORD_BUTTON_STYLE)
        self.checkStateSet()

    def checkStateSet(self) -> None:
        self.setText(HAND_CAPTIONS[self.isChecked()])


def _rate_label(field_name: str) -> str:
    """What one multiplier is called in a breakdown row.

    An art carries its own name (`model.ART_LABELS`, AK-363) -- the spell
    row's rates hold the genus the catalyst casts beside the damage-type
    rates, and `Incantations` is what the chooser calls it too. Everything
    else is a rate field and is named as it always was.
    """
    return model.ART_LABELS.get(field_name) or model.label_for(field_name)


def breakdown_text(label: str, entries: list, multiplicative: bool) -> str:
    """The tooltip behind one clicked figure: its sources, one row each (QA-077).

    `entries` carry `name` and `own`. A multiplier is shown as its percentage
    (`own` 1.124 reads `+12.4%`), a flat bonus as its number.
    """
    if not entries:
        return f"{label}\nno contributing effects recorded"
    rows = [f"<b>{label}</b>"]
    for entry in entries:
        if multiplicative:
            shown = f"{(entry.own - 1.0) * 100:+.1f}%"
        else:
            shown = f"{entry.own:+g}"
        rows.append(f"&nbsp;&nbsp;{entry.name} &nbsp; <b>{shown}</b>")

    if multiplicative and len(entries) > 1:
        total = 1.0
        for entry in entries:
            total *= entry.own
        rows.append(f"&nbsp;&nbsp;<i>combined multiplicatively: "
                    f"{(total - 1.0) * 100:+.1f}%</i>")
    elif not multiplicative and len(entries) > 1:
        rows.append(f"&nbsp;&nbsp;<i>total "
                    f"{sum(entry.own for entry in entries):+g}</i>")
    return "<br>".join(rows)


def _heading(text: str) -> QLabel:
    label = QLabel(text.upper())
    font = label.font()
    font.setPointSize(8)
    font.setBold(True)
    font.setLetterSpacing(QFont.AbsoluteSpacing, 1.2)
    label.setFont(font)
    label.setStyleSheet(f"color: {MUTED};")
    return label


#: For the effect with no ceiling in the game's scripts (`model.STACK_LIMITS`),
#: and so not a fact about the game, only a stop for a slip of the keyboard:
#: above it the count is left at this. Measured 2026-11-07, offscreen, on "Attack power
#: increased for each Night Invader defeated": the page takes 12 ms at 99; at
#: 100000 it takes 1.4 s, the attack rating is infinite and `damage.displayed`
#: raises in the middle of drawing it. Not `effectfilters.MOST_STACKS`: that one
#: holds Optimize to its budget, and this page computes only one build.
MOST_COUNT = 99


def _within_reason(count: int, effect_id: int) -> int:
    return min(max(count, 1), model.stack_limit(effect_id, MOST_COUNT))


class SituationalRow(QFrame):
    """One gated effect, with a switch and -- if it stacks -- a count.

    The sheet cannot know whether the condition is met. This is where the
    player says so: tick it and the effect joins every total, exactly as an
    always-on roll would.
    """

    def __init__(self, entry, count: int, on_change):
        super().__init__()
        self.effect_id = entry.effect_id
        self.accumulates = entry.accumulates
        self.on_change = on_change
        self.setStyleSheet("QFrame { border: none; }")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 5)
        layout.setSpacing(1)

        head = QHBoxLayout()
        head.setSpacing(6)
        # The name is a separate wrapping label rather than the checkbox's own
        # text. A QCheckBox will not wrap, so a long effect name set the whole
        # sheet's minimum width -- which pushed the panel wider than its
        # viewport and clipped every other line in it, count box included.
        self.check = QCheckBox()
        self.check.setChecked(count > 0)
        self.check.setStyleSheet("border: none;")
        self.check.toggled.connect(self._toggled)
        head.addWidget(self.check, 0, Qt.AlignTop)

        self.title = QLabel(entry.name)
        self.title.setWordWrap(True)
        self.title.setCursor(Qt.PointingHandCursor)
        self.title.setStyleSheet(f"color: {ACCENT}; border: none;")
        self.title.mousePressEvent = lambda _e: self.check.toggle()
        head.addWidget(self.title, 1)

        if entry.accumulates:
            # Free text, not a spin box. How many Night Invaders this run has
            # brought is a fact about the run rather than about this program
            # -- so the player states the number and the arithmetic follows
            # it, up to the effect's own limit.
            self.times = QLabel("×")
            self.times.setStyleSheet(f"color: {MUTED}; border: none;")
            head.addWidget(self.times, 0, Qt.AlignTop)
            self.count = QLineEdit(str(_within_reason(count, self.effect_id)))
            self.count.setFixedWidth(42)
            self.count.setAlignment(Qt.AlignCenter)
            self.count.setToolTip(
                "How many times this is true right now, at most "
                f"{_within_reason(MOST_COUNT, self.effect_id)}")
            self.count.editingFinished.connect(self._edited)
            head.addWidget(self.count, 0, Qt.AlignTop)
            self._set_count_enabled(count > 0)
        else:
            self.count = None
        layout.addLayout(head)

        detail = QLabel(entry.detail)
        detail.setWordWrap(True)
        detail.setStyleSheet("color: #cfcfcf; font-size: 11px; border: none;")
        layout.addWidget(detail)

        self.why_text = entry.why
        self.why = QLabel()
        self.why.setWordWrap(True)
        self.why.setStyleSheet(f"color: {MUTED}; font-size: 10px; border: none;")
        layout.addWidget(self.why)
        self._refresh_why()

    def _refresh_why(self) -> None:
        """Say whether this is currently counted, not only why it is gated."""
        value = self.value()
        if value:
            times = f" ×{value}" if self.count is not None else ""
            self.why.setText(f"counted in the totals{times} — {self.why_text}")
            self.why.setStyleSheet(
                f"color: {GOOD}; font-size: 10px; border: none;")
        else:
            self.why.setText(self.why_text)
            self.why.setStyleSheet(
                f"color: {MUTED}; font-size: 10px; border: none;")

    def _set_count_enabled(self, on: bool) -> None:
        if self.count is not None:
            self.count.setEnabled(on)
            self.times.setEnabled(on)

    def value(self) -> int:
        """How many times the player says this applies; 0 when switched off."""
        if not self.check.isChecked():
            return 0
        if self.count is None:
            return 1
        text = self.count.text().strip()
        try:
            # A blank or nonsense box means "it is true", not "it is true zero
            # times" -- switching it on is already the statement that it holds.
            return _within_reason(int(text), self.effect_id)
        except ValueError:
            return 1

    def _toggled(self, on: bool) -> None:
        self._set_count_enabled(on)
        self._refresh_why()
        self.on_change()

    def _edited(self) -> None:
        value = self.value()
        if self.count is not None and self.count.text().strip() != str(value):
            self.count.setText(str(value))
        self._refresh_why()
        if self.check.isChecked():
            self.on_change()


class StatSheet(QScrollArea):
    """The right-hand pane. Built once by the window, drawn by `draw`."""

    #: The player moved a condition switch: effect id -> how many times it
    #: holds, zero entries left out. The window sets `declared` and recomputes.
    #: `object`, not `dict`: a `dict` signal is a QVariantMap to Qt, whose
    #: keys are strings, and effect ids are ints -- the emit silently fails.
    declared_changed = Signal(object)

    # Populated by draw(), read by the click-to-break-down popup.
    last_sources: dict = {}
    last_rates: dict = {}
    #: The spell row's own answer, the input of its click-through (AK-361),
    #: `None` wherever the row is not drawn. Held for the same reason
    #: `last_ar` is: the popup's text is testable only where its input is.
    last_spell = None

    def __init__(self, planner):
        # The whole sheet scrolls. With six relics equipped the conditional and
        # curse sections alone can outrun the window, and content was simply
        # falling off the bottom with no way to reach it.
        super().__init__()
        self.planner = planner
        # 348 was tight before the situational switches and cramped after them:
        # a multiplier line such as "All damage +6.0% - melee armaments only"
        # had nowhere to go, and the count box sat past the right edge. 370 is
        # still what it opens at -- the splitter's initial sizes say so -- but
        # a player who wants the sheet wider may now have it, and one who
        # drags it narrow gets the wrapping rather than a cut-off column.
        self.setMinimumWidth(340)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 8, 0)

        layout.addWidget(_heading("Base stats"))
        self.derived_grid = QGridLayout()
        self.derived_grid.setHorizontalSpacing(10)
        self.derived_grid.setVerticalSpacing(4)
        layout.addLayout(self.derived_grid)

        layout.addSpacing(12)
        layout.addWidget(_heading("Attributes"))
        self.attr_grid = QGridLayout()
        self.attr_grid.setHorizontalSpacing(10)
        self.attr_grid.setVerticalSpacing(4)
        layout.addLayout(self.attr_grid)

        layout.addSpacing(12)
        layout.addWidget(_heading("Weapon damage"))
        # Six armament tiles, 3x2. Slot 1 starts as this Nightfarer's own
        # starting armament -- CharaInitParam rows 90000-90009, agreed by three
        # other row families (see verify_starting_weapons.py). Every tile's
        # rolled effects count towards the sheet; the active one, ringed in
        # gold, is the one the damage breakdown below describes.
        # Single-click activates, double-click edits, right-click empties.
        grid = QGridLayout()
        grid.setHorizontalSpacing(6)
        grid.setVerticalSpacing(6)
        self.weapon_tiles = []
        for index in range(weaponslots.SLOT_COUNT):
            tile = weaponslots.WeaponTile(
                index, planner._edit_weapon_slot,
                planner._clear_weapon_slot,
                planner._activate_weapon_slot, planner.icons,
            )
            self.weapon_tiles.append(tile)
            grid.addWidget(tile, index // weaponslots.SLOT_COLUMNS,
                           index % weaponslots.SLOT_COLUMNS)
        layout.addLayout(grid)

        # AK-410: the spell and the weapon art the selected tile uses, chosen
        # here; the window stores a choice on the tile and recomputes.
        self.casting = castingbar.CastingBar(_heading("Casting"),
                                             planner.icons)
        layout.addWidget(self.casting)

        # Every toggle ends in the window's `recompute`, which stores the
        # build and tells the advisor (AK-293 point 5); the window wires it.
        self.hand_switch = HandSwitch()
        layout.addWidget(self.hand_switch, alignment=Qt.AlignLeft)

        self.ar_label = QLabel()
        self.ar_label.setWordWrap(True)
        self.ar_label.linkActivated.connect(self._show_breakdown)
        layout.addWidget(self.ar_label)

        layout.addSpacing(12)
        layout.addWidget(_heading("Resistances"))
        self.resist_label = QLabel()
        self.resist_label.setWordWrap(True)
        layout.addWidget(self.resist_label)

        layout.addSpacing(12)
        layout.addWidget(_heading("Multipliers"))
        self.rates_label = QLabel()
        self.rates_label.setWordWrap(True)
        self.rates_label.linkActivated.connect(self._show_breakdown)
        layout.addWidget(self.rates_label)

        layout.addSpacing(12)
        self.qual_heading = _heading("Conditional &amp; situational")
        # Pinned to rich text: the count carries markup only when something is
        # not working, and without this the plain case printed "&amp;" raw.
        self.qual_heading.setTextFormat(Qt.RichText)
        layout.addWidget(self.qual_heading)

        # The switchable ones first, as widgets, then the rest as text. Only
        # the top group can be acted on, and mixing them would hide that.
        self.qual_rows = QWidget()
        self.qual_rows_layout = QVBoxLayout(self.qual_rows)
        self.qual_rows_layout.setContentsMargins(0, 0, 0, 0)
        self.qual_rows_layout.setSpacing(0)
        layout.addWidget(self.qual_rows)
        self.situational_rows: dict[int, SituationalRow] = {}

        self.qual_label = QLabel()
        self.qual_label.setWordWrap(True)
        layout.addWidget(self.qual_label)

        layout.addSpacing(12)
        self.other_heading = _heading("Flat bonuses")
        layout.addWidget(self.other_heading)
        self.other_label = QLabel()
        self.other_label.setWordWrap(True)
        self.other_label.linkActivated.connect(self._show_breakdown)
        layout.addWidget(self.other_label)

        layout.addSpacing(12)
        layout.addWidget(_heading("Curses"))
        self.curse_label = QLabel()
        self.curse_label.setWordWrap(True)
        layout.addWidget(self.curse_label)

        layout.addSpacing(12)
        layout.addWidget(_heading("Stacking"))
        self.warn_label = QLabel()
        self.warn_label.setWordWrap(True)
        self.warn_label.setAlignment(Qt.AlignTop)
        layout.addWidget(self.warn_label)

        layout.addStretch(1)
        self.setWidget(panel)

    def _show_breakdown(self, key: str) -> None:
        """Which buffs make up one figure, shown beside the number clicked.

        A single "+12.4%" hides how many relics contributed and how much each
        one gave, which is exactly what you need when deciding whether one is
        worth a slot.
        """
        if key == AR_BREAKDOWN_KEY:
            self._show_ar_breakdown()
            return

        if key == SPELL_BREAKDOWN_KEY:
            QToolTip.showText(QCursor.pos() + QPoint(18, 0),
                              self._spell_breakdown_text())
            return

        # An "All damage" row stands for five fields; its sources live under
        # the real one behind it.
        entries = self.last_sources.get(model.real_field(key), [])
        text = breakdown_text(model.label_for(key), entries,
                              model.real_field(key) in self.last_rates)
        # Offset to the right of the cursor so the number stays readable; the
        # "nothing recorded" sentence has no number beside it to keep clear.
        offset = QPoint(18, 0) if entries else QPoint(0, 0)
        QToolTip.showText(QCursor.pos() + offset, text)

    def _rate_rows(self, rates: dict[str, float],
                   weapon_class: str | None = None) -> list[str]:
        """One row per multiplier in play, with the relics behind each.

        Read by both click-throughs: the attack rating's and the spell
        damage's (AK-361). The two figures come out of one facade and one
        rate loop (`damage._multiplied`), so formatting them twice would let
        one percentage be written two ways. A spell reaches no class-scoped
        buff at all (AD-053 point 4), which is why the armament class is the
        armament's business and left out here.
        """
        rows = []
        for field_name, value in rates.items():
            rows.append(f"&nbsp;&nbsp;{_rate_label(field_name)} &nbsp; "
                        f"<b>{(value - 1.0) * 100:+.1f}%</b>")
            # Which relics produced that multiplier, in the same order and
            # wording the other breakdowns use. A buff scoped to melee or
            # ranged armaments is filed under its own key, so both are read:
            # the flat sources, then the ones that apply because of what this
            # armament is.
            entries = list(self.last_sources.get(field_name, []))
            if weapon_class:
                scoped = (f"{model.WEAPON_CLASS_PREFIX}{weapon_class}:"
                          f"{field_name}")
                entries += [
                    entry._replace(
                        name=f"{entry.name} — {weapon_class} armaments only")
                    for entry in self.last_sources.get(scoped, [])]
            for entry in entries:
                rows.append(f"&nbsp;&nbsp;&nbsp;&nbsp;"
                            f"<span style='color:{MUTED}'>{entry.name} "
                            f"{(entry.own - 1.0) * 100:+.1f}%</span>")
        return rows

    def _type_tag(self, label: str) -> str:
        """The `<img>` of a damage type or status, for this sheet's rich text."""
        return iconpack.inline_type(self.planner.icons, label)

    def _spell_breakdown_text(self) -> str:
        """Where the spell row's figure comes from, and the note it carries.

        AK-361: the baseline, the rates that moved it with their relics, the
        figure -- and, for a spell that damages nothing, the facade's
        sentence saying so. Handed back rather than only shown, for the
        reason `_ar_breakdown_text` is (QA-073 b): a text built straight into
        a tooltip is a text no test can read.
        """
        rating = self.last_spell
        if rating is None:
            return "No spell on this armament."
        # Game text in a rich-text tooltip: the spell's own name, in the
        # heading and inside the facade's sentence, is escaped here rather
        # than where the facade writes it -- its other sinks are PlainText
        # and would show a `&amp;` of their own (SEC-019).
        rows = [f"<b>{damage.SPELL_DAMAGE_NAME} — "
                f"{html.escape(str(rating.spell.get('name', '')))}</b>",
                f"&nbsp;&nbsp;Base &nbsp; "
                f"<b>{damage.displayed(rating.bare_figure)}</b>"]
        rows += self._rate_rows(rating.rates)
        rows.append(f"&nbsp;&nbsp;<b>{damage.SPELL_DAMAGE_NAME} "
                    f"{damage.displayed(rating.figure)}</b>")
        if rating.reason:
            rows.append(f"<span style='color:{MUTED}'>"
                        f"{html.escape(rating.reason)}</span>")
        return "<br>".join(rows)

    def _ar_breakdown_text(self) -> str:
        """Where the weapon's attack-rating change came from.

        Two different things move this number and they are worth telling apart:
        raising an attribute makes the weapon scale harder, while an attack
        multiplier scales the finished figure. A relic can do either, and "+35"
        alone does not say which -- or whether it came from one relic or six.

        Handed back rather than only shown. Until now this text was built and
        passed straight to a tooltip, so it existed nowhere a test could reach
        it: the golden file freezes `last_ar`, and `last_ar` is this display's
        **input**, never its output. A mutation that swapped `base` for
        `scaled` therefore changed what the player reads and left the whole
        suite green (QA-073 b). Returning the text is the whole of the fix --
        what is shown, and where, is unchanged.
        """
        ar = getattr(self, "last_ar", None)
        if not ar:
            return "No weapon selected."

        base, scaled, final = ar["base"], ar["scaled"], ar["final"]
        # The other hand's base and final, where the armament has one
        # (AK-286); they stand beside the one-handed figure, not on a row
        # of their own.
        two_handed = ar.get("two_handed", {})
        two_handing = self.hand_switch.isChecked()
        # What the three figures are, named by the facade: for a staff or a
        # seal they are a spell scaling, and heading them "Attack rating"
        # would be the right numbers under the wrong name (QA-099).
        shown_base = damage.displayed_hands(base, two_handed.get("base"),
                                            two_handing)
        rows = [f"<b>{ar['headline']} — {ar['weapon']}</b>",
                f"&nbsp;&nbsp;Base &nbsp; <b>{shown_base}</b>"]

        from_attributes = scaled - base
        if abs(from_attributes) >= VISIBLE_CHANGE:
            rows.append(f"&nbsp;&nbsp;From attributes &nbsp; "
                        f"<b>{from_attributes:+.0f}</b>")

        rows += self._rate_rows(ar["rates"], ar.get("class"))

        if not ar["rates"] and abs(from_attributes) < VISIBLE_CHANGE:
            rows.append("&nbsp;&nbsp;<i>nothing equipped moves this weapon</i>")

        # A factor read off the game for this Nightfarer/armament pairing
        # (`weapons.nightfarer_calibration`). It is already inside every
        # figure above; the line says so, and says where the number is from.
        # The damage-type conversion of a "Starting armament deals <element>
        # damage" relic, per type, so the player sees what the element cost
        # in physical damage (`damage.converted`, measured 3 of 3).
        conversion = ar.get("conversion")
        if conversion:
            moved = ", ".join(
                f"{self._type_tag(weapons.DAMAGE_LABELS[damage_type])}"
                f"{weapons.DAMAGE_LABELS[damage_type]} {value:+.0f}"
                for damage_type, value in conversion.items())
            rows.append(f"&nbsp;&nbsp;Starting armament conversion &nbsp; "
                        f"<b>{moved}</b> "
                        f"<span style='color:{MUTED}'>measured, not read "
                        f"from the files</span>")

        calibration = ar.get("calibration")
        if calibration:
            rows.append(f"&nbsp;&nbsp;{calibration['reason']} &nbsp; "
                        f"<b>x{calibration['factor']:.2f}</b> "
                        f"<span style='color:{MUTED}'>measured, not read "
                        f"from the files; in every figure here</span>")

        delta = final - base
        pct = (delta / base * 100) if base else 0.0
        shown_final = damage.displayed_hands(final, two_handed.get("final"),
                                             two_handing)
        rows.append(f"&nbsp;&nbsp;<b>Total {shown_final}</b> "
                    f"({delta:+.0f}{f', {pct:+.1f}%' if base else ''})")
        return "<br>".join(rows)

    def _show_ar_breakdown(self) -> None:
        """The breakdown, beside the figure that was clicked."""
        # Offset to the right of the cursor so the number stays readable --
        # but only where there is a figure to keep clear. The "no weapon"
        # notice has none, and sat under the cursor before this split did.
        beside = QPoint(18, 0) if getattr(self, "last_ar", None) else QPoint()
        QToolTip.showText(QCursor.pos() + beside, self._ar_breakdown_text())

    def _weapon_art_row(self, slot, build, hero, now) -> str:
        """The Weapon art row: what the art in use hits for (AK-416, F1).

        The art and its figure are the facade's (`damage.weapon_art`,
        AD-056): one hit, AR x motion value, and one figure with no
        two-handed twin -- the dummy shows Stamp at 262 either way (M1), so
        the row does not follow the hand switch. Grey is the same hit with
        nothing equipped, the yardstick every other row of this panel uses
        (the panel's own footnote, and the spell row's AK-359); AK-355's
        "the total above" was a yardstick for a factor on the total and has
        no meaning for a figure 2.15 times it.

        An art without a figure names itself and says why (AD-056.5); a
        rolled armament nobody chose an art for gets no row -- the casting
        bar asks for the choice (AK-412).

        AK-356: on a staff or a seal the head of the armament is a spell
        power and no attack art reaches it (AD-048/AD-053 point 5), so the
        row says that where its number would be.
        """
        label = model.ART_LABELS[model.SKILL_ART]
        if now.catalyst_scaling is not None:
            return (f"<div style='color:{MUTED}'>"
                    f"{ART_ON_A_CATALYST.format(art=label)}</div>")
        art = damage.weapon_art(slot, self.planner.active_weapon, build, hero,
                                self.planner.data)
        if art.art is None:
            return ""
        # Game text in a rich-text label is escaped (SEC-019, AK-419).
        symbol = iconpack.inline(self.planner.icons, "items", art.art.get("icon"))
        head = f"{label} ({symbol}{html.escape(str(art.art.get('name', '')))})"
        if art.reason:
            return (f"<div>{head} <span style='color:{MUTED}'>"
                    f"{html.escape(art.reason)}</span></div>")
        delta = art.figure - art.bare_figure
        colour = (GOOD if delta > COLOURED_CHANGE
                  else BAD if delta < -COLOURED_CHANGE else MUTED)
        change = (f"{delta:+.0f}" if abs(delta) >= VISIBLE_CHANGE
                  else "no change")
        return (
            f"<div>{head} <span style='color:{MUTED}'>"
            f"{damage.displayed(art.bare_figure)}</span> "
            f"<span style='color:{colour}'>{change}</span> "
            f"<b style='color:{ACCENT}'>{damage.displayed(art.figure)}"
            f"</b></div>"
        )

    def _spell_damage_rows(self, slot, build, hero,
                           starting: bool) -> list[str]:
        """The spell row, where the selected tile or this Nightfarer's own
        equipment casts one.

        AK-353 point 2: any staff or seal on the selected tile, at that
        tile's tier, so that the rows of one tile describe one armament
        (T-335b: a Duchess or a Raider can pick a staff up). Without one, the
        right starting hand still gets the starting catalyst's row -- what
        Revenant needs: his Finger Seal is in the left hand and
        `Planner.apply_hero_weapon` fills one tile, so the seal sits on no
        tile at all and the row still belongs under his claws.

        AK-358: a Nightfarer with neither staff nor seal gets no row, not a
        sentence -- this panel already leaves out what does not apply, the
        way it leaves out "Inflicts <status>". Eight of the ten are in that
        case (AD-052).

        Which catalyst and which spell is the facade's choice and never this
        panel's (AK-357/AD-052). A starting catalyst on no tile has no tier
        of its own and is asked at `weapons.MIN_UPGRADE`, as the advisor
        asks it.
        """
        data = self.planner.data
        catalyst, own = damage.spell_catalyst(slot.weapon, hero, data)
        on_tile = catalyst is slot.weapon
        if catalyst is None or not (on_tile or starting):
            return []
        thrown = damage.spell_thrown(
            build, data, catalyst, starting=own,
            chosen=slot.spell_id if on_tile else None)[0]
        if thrown is None:
            return []
        # `damage_type=""`: this panel has no damage-type box, so the figure
        # is every type of the spell together (AK-357).
        rating = damage.spell(
            thrown, catalyst, slot.tier if on_tile else weapons.MIN_UPGRADE,
            build, data,
            hit_with=damage.GENUS_OF_CATALYST[catalyst["wep_type"]])
        self.last_spell = rating
        delta = rating.figure - rating.bare_figure
        colour = (GOOD if delta > COLOURED_CHANGE
                  else BAD if delta < -COLOURED_CHANGE else MUTED)
        change = (f"{delta:+.0f}" if abs(delta) >= VISIBLE_CHANGE
                  else "no change")
        # No two-handed twin (AK-359/AD-053 point 4): the two-handing bucket
        # does not reach a spell, so the figure is the same at either stand
        # of the switch. Game text in a rich-text label is escaped (SEC-019).
        return [
            f"<div>{damage.SPELL_DAMAGE_NAME} "
            f"({iconpack.inline(self.planner.icons, 'items', thrown.get('icon'))}"
            f"{html.escape(str(thrown.get('name', '')))}) "
            f"<span style='color:{MUTED}'>"
            f"{damage.displayed(rating.bare_figure)}</span> "
            f"<span style='color:{colour}'>{change}</span> "
            f"<a href='{SPELL_BREAKDOWN_KEY}' style='color:{ACCENT};"
            f"text-decoration:none'><b>"
            f"{damage.displayed(rating.figure)}</b></a></div>"
        ]

    def _refresh_weapon_damage(self, build) -> None:
        """Attack rating before and after everything equipped.

        Every tile is rated so each can show its own total; the active one gets
        the full breakdown underneath. Both figures come out of one
        `damage.equipped()` call per slot, so the tile and the panel below it
        are the same question with the same answer -- until W3 the tile chose
        the raised attributes without the multipliers and the panel chose
        both, and a player saw two totals for one armament with nothing to
        tell them apart (AD-020, point 6; QA-056).
        """
        hero = self.planner.current_hero()
        # The switch's stand goes into every figure that shows both hands
        # (AK-298); the figures themselves do not move with it (AK-293).
        two_handing = self.hand_switch.isChecked()
        # Cleared before anything is drawn: a spell row that is not drawn
        # this time round must not leave the last one's figures behind for
        # the click-through to show (AK-358).
        self.last_spell = None
        answers: dict[int, tuple] = {}
        for index, slot in enumerate(self.planner.weapon_slots):
            equipped = None
            if slot.filled:
                answers[index] = damage.equipped(slot, index, build, hero,
                                                 self.planner.data)
                equipped = answers[index][1]
            self.weapon_tiles[index].show_slot(
                slot, equipped, active=index == self.planner.active_weapon,
                effects=self.planner.data["effects"], two_handing=two_handing)

        slot = self.planner.active_slot()
        self._refresh_casting(slot, build, hero)
        if not slot.filled:
            self.last_ar = {}
            self.ar_label.setText(
                f"<span style='color:{MUTED}'>Slot "
                f"{self.planner.active_weapon + 1} is empty — double-click a "
                f"tile to choose an armament, single-click one to break it "
                f"down here."
                f"</span>")
            return
        weapon = slot.weapon

        # The figure itself is not computed here. It is the one piece of
        # domain arithmetic that had ended up inside the window, and the build
        # advisor needs to ask for it without drawing anything, so it lives in
        # nrplanner/damage.py and this method formats what comes back. The
        # tile above this panel was rated in the same call.
        bare, now = answers[self.planner.active_weapon]
        # Which figure this armament is headed by, and whether it has
        # damage-type rows at all, is the facade's answer: a staff has a
        # spell scaling and no attack rating to break down (QA-099).
        boosted = now.shown_per_type
        base_total = bare.scaled_headline
        final_total = now.final_headline
        delta = final_total - base_total
        self.last_ar = damage.breakdown_figures(bare, now)

        # The left-hand column of each row: the same armament on the level's
        # own attributes, before anything equipped raised them. It stays a
        # different question from the total beside it, and on purpose --
        # without it the panel has no before to put against its after
        # (AD-020, point 2).
        was_per_type = bare.scaled_per_type

        rows = []
        for damage_type, value in boosted.items():
            was = was_per_type.get(damage_type, 0.0)
            diff = value - was
            colour = (GOOD if diff > COLOURED_CHANGE
                      else BAD if diff < -COLOURED_CHANGE else MUTED)
            change = (f"{diff:+.0f}" if abs(diff) >= VISIBLE_CHANGE
                      else "—")
            # Each figure with its two-handed twin where there is one
            # (AK-286); the change between them stays the one-handed one.
            was_shown = bare.displayed_hands(
                lambda r: r.scaled_per_type.get(damage_type, 0.0), two_handing)
            value_shown = now.displayed_hands(
                lambda r: r.final_per_type.get(damage_type, 0.0), two_handing)
            rows.append(
                f"<div>{self._type_tag(weapons.DAMAGE_LABELS[damage_type])}"
                f"{weapons.DAMAGE_LABELS[damage_type]} "
                f"<span style='color:{MUTED}'>{was_shown}</span> "
                f"<span style='color:{colour}'>{change}</span> "
                f"<b>{value_shown}</b></div>"
            )

        colour = (GOOD if delta > COLOURED_CHANGE
                  else BAD if delta < -COLOURED_CHANGE else MUTED)
        change = (f"{delta:+.0f}" if abs(delta) >= VISIBLE_CHANGE
                  else "no change")
        pct = (delta / base_total * 100) if base_total else 0.0
        # "Total" while there are rows above it to total. A catalyst has
        # none, so this line is the figure itself and is named after it.
        total_label = "Total" if boosted else now.headline_name
        rows.append(
            f"<div style='margin-top:4px'><b>{total_label}</b> "
            f"<span style='color:{MUTED}'>"
            f"{bare.displayed_hands(lambda r: r.scaled_headline, two_handing)}"
            f"</span> "
            f"<a href='{AR_BREAKDOWN_KEY}' style='color:{colour};"
            f"text-decoration:none'>{change}</a> "
            f"<b style='color:{ACCENT}'>"
            f"{now.displayed_hands(lambda r: r.final_headline, two_handing)}"
            f"</b>"
            + (f" <span style='color:{colour}'>({pct:+.1f}%)</span>"
               if abs(pct) >= VISIBLE_PERCENT else "") +
            "</div>"
        )

        # AK-353/AK-364: the two new rows, directly under the total and
        # before the status ones, and on no tile. What brings the Weapon art
        # row is not "a tile is active" but the identity of the active tile
        # against this Nightfarer's starting equipment -- the same pairing
        # the status penalty follows (AD-038), so a starting armament carried
        # to another slot takes the row with it. Three rows, three
        # yardsticks, never a sum of them (AK-362).
        starting = damage.is_starting_armament(
            weapon, hero, self.planner.active_weapon)
        if starting or now.catalyst_scaling is None:
            rows.append(self._weapon_art_row(slot, build, hero, now))
        rows += self._spell_damage_rows(slot, build, hero, starting)

        # Status the armament applies on a landed hit. This belongs with the
        # weapon rather than in the relic list: "Starting armament inflicts
        # frost" is the reason the attack rating above is 15% lower **on slot
        # 1**, and the buildup is what you are buying with it.
        #
        # Only statuses your attacks apply are shown. The ones that build up on
        # you -- "Taking Damage Causes Poison Buildup" and the like -- reach the
        # player, not the enemy, and would read as a weapon property here.
        on_hit: dict[str, list[tuple[str, float]]] = {}
        for eff in self.planner.selected_effects():
            for status, value in (eff.get("inflicts_on_hit") or {}).items():
                label = " ".join(str(eff.get("name", "")).split())
                on_hit.setdefault(status, []).append((label, value))

        for status, entries in sorted(on_hit.items()):
            total = sum(v for _n, v in entries)
            detail = ""
            if len(entries) > 1:
                # Whether two sources of one status really add is not stated in
                # the params, so the parts are shown rather than only the sum.
                parts = ", ".join(f"{n} {v:g}" for n, v in entries)
                detail = (f"<div style='color:{MUTED};font-size:11px'>"
                          f"{parts} — shown added; the params do not say "
                          f"whether they truly stack.</div>")
            rows.append(
                f"<div style='margin-top:6px'>Inflicts {self._type_tag(status)}{status} "
                f"<b style='color:{ACCENT}'>{total:g}</b>"
                f"<span style='color:{MUTED}'> buildup per hit</span></div>"
                + detail
            )

        # Rally: how much HP this armament wins back per landed hit. It is a
        # flat figure carried by the weapon, not a share of the damage dealt,
        # so it belongs here next to the weapon rather than with the relic that
        # enables the mechanic. A weapon on 0 reclaims nothing no matter which
        # rally relic is equipped, which is the one thing worth seeing before
        # committing a slot to one.
        regain = weapon.get("regain_hp") or 0
        if regain:
            # "Partial HP Restoration upon Post-Damage Attacks" carries
            # regainRate, so it scales what the armament reclaims. Shown the
            # same way as the damage rows -- grey base, the change, then the
            # figure that actually applies -- because a rally relic changing
            # nothing on screen is exactly what makes it look broken.
            rate = build.rates.get("regainRate", 1.0)
            final_regain = regain * rate
            diff = final_regain - regain
            colour = (GOOD if diff > COLOURED_CHANGE
                      else BAD if diff < -COLOURED_CHANGE else MUTED)
            change = (f"{diff:+.0f}" if abs(diff) >= VISIBLE_CHANGE
                      else "—")
            rows.append(
                f"<div style='margin-top:6px'>Rally recovery "
                f"<span style='color:{MUTED}'>{regain:.0f}</span> "
                f"<span style='color:{colour}'>{change}</span> "
                f"<b style='color:{ACCENT}'>{final_regain:.0f} HP</b>"
                f"<span style='color:{MUTED}'> per landed hit</span></div>"
                f"<div style='color:{MUTED};font-size:11px'>"
                f"A flat amount, not a share of the damage you deal, and it "
                f"varies by attack — some recover nothing.</div>"
            )
        else:
            rows.append(
                f"<div style='margin-top:6px;color:{MUTED}'>Rally recovery "
                f"<b style='color:{BAD}'>none</b> — this armament reclaims no "
                f"HP, so rally relics do nothing with it.</div>"
            )

        rows.append(
            f"<div style='color:{MUTED}; font-size:10px; margin-top:2px'>"
            f"Grey is your base at this level; the change is what the equipped "
            f"relics add, counting stat gains and attack multipliers.</div>"
        )
        self.ar_label.setText("".join(rows))

    def _refresh_casting(self, slot, build, hero) -> None:
        """Redraw the casting bar for the active tile, its chips in the tab
        order between the tiles and the hand switch (AK-413)."""
        self.casting.show_chips(*castingbar.chips_for(
            slot, self.planner.active_weapon, build, hero, self.planner.data))
        chain = [*self.weapon_tiles, *self.casting.chip_widgets,
                 self.hand_switch]
        for before, after in zip(chain, chain[1:]):
            QWidget.setTabOrder(before, after)

    def _sync_situational(self, entries: list, declared: dict) -> None:
        """Draw one switch per gated effect, rebuilding only when the set changes.

        recompute() runs on every keystroke that reaches it, and rebuilding the
        rows each time would take the count box out from under the cursor
        mid-number. The rows are therefore kept while the same effects are
        equipped, and only their values are pushed back.
        """
        wanted = [e.effect_id for e in entries]
        if wanted != list(self.situational_rows):
            while self.qual_rows_layout.count():
                item = self.qual_rows_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self.situational_rows = {}
            for entry in entries:
                row = SituationalRow(
                    entry, declared.get(entry.effect_id, 0),
                    self._situational_changed,
                )
                self.situational_rows[entry.effect_id] = row
                self.qual_rows_layout.addWidget(row)
        self.qual_rows.setVisible(bool(entries))

    def _situational_changed(self) -> None:
        self.declared_changed.emit({
            eid: row.value()
            for eid, row in self.situational_rows.items()
            if row.value() > 0
        })

    def draw(self, build: model.Build, declared: dict) -> None:
        """Draw `build`; `declared` seeds the condition switches, read only.

        Not `show`: that is `QWidget.show()`, and a pane whose `show` took
        two arguments would break the first caller that meant the other one.
        """
        hero = self.planner.current_hero()
        for grid in (self.attr_grid, self.derived_grid):
            while grid.count():
                item = grid.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

        for r, label in enumerate(("HP", "FP", "Stamina")):
            if label not in build.derived:
                continue
            base, total = build.derived[label]
            delta = total - base

            name = QLabel(label)
            name.setStyleSheet("font-size: 13px;")
            self.derived_grid.addWidget(name, r, 0)

            base_lbl = QLabel(f"{base:.0f}")
            base_lbl.setStyleSheet(f"color: {MUTED};")
            base_lbl.setAlignment(Qt.AlignRight)
            self.derived_grid.addWidget(base_lbl, r, 1)

            diff = QLabel(f"{delta:+.0f}"
                          if abs(delta) >= VISIBLE_CHANGE else "")
            diff.setStyleSheet(f"color: {GOOD if delta > 0 else BAD};")
            diff.setAlignment(Qt.AlignRight)
            self.derived_grid.addWidget(diff, r, 2)

            total_lbl = QLabel(f"{total:.0f}")
            total_lbl.setStyleSheet(
                f"font-weight: bold; font-size: 15px; color: {ACCENT};"
            )
            total_lbl.setAlignment(Qt.AlignRight)
            self.derived_grid.addWidget(total_lbl, r, 3)

        for r, name in enumerate(model.ATTRIBUTE_ORDER):
            base = build.base_attributes.get(name, 0)
            total = build.attributes.get(name, 0)
            delta = total - base

            self.attr_grid.addWidget(QLabel(name), r, 0)
            base_lbl = QLabel(str(base))
            base_lbl.setStyleSheet(f"color: {MUTED};")
            base_lbl.setAlignment(Qt.AlignRight)
            self.attr_grid.addWidget(base_lbl, r, 1)

            # ":+d" already carries the sign; prefixing another "+" printed
            # "+-3" for every curse. Clickable for the same reason as the
            # multipliers: a net +6 could be one relic or three fighting a curse.
            colour = GOOD if delta > 0 else BAD
            diff = QLabel(
                f"<a href='{name}' style='color:{colour}; "
                f"text-decoration:none'>{delta:+d}</a>" if delta else ""
            )
            diff.linkActivated.connect(self._show_breakdown)
            diff.setAlignment(Qt.AlignRight)
            self.attr_grid.addWidget(diff, r, 2)

            total_lbl = QLabel(str(total))
            total_lbl.setStyleSheet("font-weight: bold; font-size: 13px;")
            total_lbl.setAlignment(Qt.AlignRight)
            self.attr_grid.addWidget(total_lbl, r, 3)

        # Kept for the click-to-break-down popup, which fires long after this
        # method has returned.
        self.last_sources = dict(build.sources)
        self.last_rates = dict(build.rates)

        self._refresh_weapon_damage(build)

        # Every resistance type, always, so an untouched one is visibly zero
        # rather than absent. Buffs and curses are already summed per type by
        # compute_resistances, so what shows is the single net figure.
        lines = []
        for label in model.RESISTANCES:
            points, rate = build.resistances.get(label, (0, 1.0))
            parts = []
            if points:
                parts.append(
                    f"<span style='color:{GOOD if points > 0 else BAD}'>"
                    f"{points:+d}</span>"
                )
            if abs(rate - 1.0) > 1e-9:
                pct = (rate - 1.0) * 100
                parts.append(
                    f"<span style='color:{GOOD if pct > 0 else BAD}'>"
                    f"{pct:+.0f}%</span>"
                )
            value = " ".join(parts) or f"<span style='color:{MUTED}'>—</span>"
            lines.append(f"<div>{self._type_tag(label)}{label} {value}</div>")
        lines.append(
            f"<div style='color:{MUTED}; font-size:10px; margin-top:4px'>"
            f"The net change from everything you have equipped. These are "
            f"changes to your resistances, not the totals.</div>"
        )
        self.resist_label.setText("".join(lines))

        if build.rates:
            lines = []
            cooldown = float(hero.get("ability_cooldown") or 0.0)
            # The `*AttackPowerRate` family is not a build-wide multiplier: it
            # is the "Starting armament inflicts frost / poison / blood loss"
            # penalty, and it reaches the starting armament alone. Reported from
            # play for 1.7.0, having previously read here as "All damage
            # -15.0%" against everything equipped. It is applied to slot 1 by
            # `_refresh_weapon_damage`, where its 15% is visible in that
            # weapon's own figure, so it is dropped from this section rather
            # than shown twice.
            shown_rates = {f: v for f, v in build.rates.items()
                           if f not in model.ELEMENT_ATTACK_POWER_RATES}
            # A buff that raises all five damage types by the same amount is one
            # buff, not five. Printing a row each turned a single relic into
            # five identical lines.
            family = model.ELEMENT_ATTACK_RATES
            present = [f for f in family if f in shown_rates]
            values = {round(shown_rates[f], 6) for f in present}
            if len(present) == len(family) and len(values) == 1:
                for f in present:
                    del shown_rates[f]
                # Linked to a real field so the click-through breakdown
                # still names the relics behind the number.
                shown_rates[f"{model.ALL_DAMAGE_PREFIX}{present[0]}"] = \
                    build.rates[present[0]]
            for fname, value in sorted(
                    model.collapse_by_label(shown_rates).items()):
                pct = (value - 1.0) * 100
                # For damage taken and resource costs, less is the good news.
                helpful = pct <= 0 if model.is_better_lower(model.real_field(fname)) else pct >= 0
                colour = GOOD if helpful else BAD
                # A percentage on its own is not actionable. Where the game
                # gives a time base, show what the number actually becomes.
                suffix = ""
                if fname == "characterSkillCooldownReduction" and cooldown:
                    suffix = (f" <span style='color:{MUTED}'>"
                              f"{cooldown:.1f}s → {cooldown * value:.1f}s</span>")
                # The number is a link: clicking it breaks the total back down
                # into the individual buffs behind it.
                lines.append(
                    f"<div>{model.label_for(fname)} "
                    f"<a href='{fname}' style='color:{colour}; "
                    f"text-decoration:none'>{pct:+.1f}%</a>{suffix}</div>"
                )
            self.rates_label.setText("".join(lines))
        else:
            lines = []

        # Buffs that cover only some armaments are held apart from the flat
        # totals so they cannot lift a weapon they do not apply to -- but they
        # still have to be visible, or a melee buff looks like it does nothing.
        def spell_out(bucket: dict, where: str) -> list[tuple[str, str, float]]:
            """One line per figure, but the five element rates collapse into a
            single "All damage" when they carry the same number between them --
            which they almost always do, and five identical rows read as five
            separate buffs."""
            rest = dict(bucket)
            values = [rest.pop(f) for f in model.ELEMENT_ATTACK_RATES
                      if f in rest] if all(
                f in rest for f in model.ELEMENT_ATTACK_RATES) else []
            out = []
            if values and len({round(v, 6) for v in values}) == 1:
                out.append((where, "All damage", values[0]))
            else:
                rest = dict(bucket)
            out += [(where, model.label_for(f), v)
                    for f, v in sorted(rest.items())]
            return out

        restricted: list[tuple[str, str, float]] = []
        for class_name, bucket in sorted(build.class_rates.items()):
            restricted += spell_out(bucket,
                                    effecttext.restricted_to(class_name))

        for where, label, value in restricted:
            pct = (value - 1.0) * 100
            colour = GOOD if pct >= 0 else BAD
            lines.append(
                f"<div>{label} "
                f"<span style='color:{colour}'>{pct:+.1f}%</span>"
                f"<span style='color:{MUTED}'> — {where}</span></div>"
            )

        self.rates_label.setText(
            "".join(lines) if lines
            else f"<span style='color:{MUTED}'>none</span>")

        # Flat additions are not percentages and were being computed into
        # build.other and then never shown at all.
        # A HP threshold is the "40" of "below 40% HP", already said on the
        # effect's own Situational row -- not a bonus (AK-295 point 2).
        flat = {fname: value for fname, value in build.other.items()
                if fname not in effecttext.CONDITIONS}
        if flat:
            lines = []
            for fname, value in sorted(model.collapse_by_label(flat).items()):
                label = effecttext.field_label(fname)
                if label is None:
                    # A number nobody named is not shown as a number at all
                    # (AK-295 point 3): the effects that carry it, and A7.
                    carriers = sorted({entry.name for entry
                                       in build.sources.get(fname, ())})
                    lines.append(f"<div>{', '.join(carriers)}: "
                                 f"{effecttext.UNLABELLED}</div>")
                    continue
                # Damage taken and resource costs read the other way round:
                # more of them is worse news, so the colour follows what the
                # figure means rather than its sign.
                helpful = (value <= 0 if model.is_better_lower(fname)
                           else value >= 0)
                colour = GOOD if helpful else BAD
                # Additive fields whose neutral is 0 but which the game states
                # as a percentage -- item discovery, bow drop-off and the like.
                shown, unit = value, ""
                if fname in model.PERCENT_FIELDS:
                    shown, unit = model.percent_value(fname, value), "%"
                elif fname in model.PERCENT_OF_100_FIELDS:
                    # Already reduced to its distance from the neutral 100.
                    unit = "%"
                lines.append(
                    f"<div>{label} "
                    f"<a href='{fname}' style='color:{colour}; "
                    f"text-decoration:none'>{shown:+g}{unit}</a></div>"
                )
            self.other_label.setText("".join(lines))
            self.other_label.setVisible(True)
            self.other_heading.setVisible(True)
        else:
            self.other_label.setVisible(False)
            self.other_heading.setVisible(False)

        # Effects that do something real but move no number in the sheet. They
        # are listed rather than dropped, so an equipped effect is never
        # silently absent from the overview.
        # The heading always shows, with a count. Hiding the section outright
        # when empty meant you could not tell whether an effect had been filed
        # here or had simply vanished -- which is exactly how a conditional
        # attack buff reads as doing nothing at all.
        dead_count = sum(1 for _n, _d, why in build.qualitative
                         if why.startswith("NOT WORKING"))
        total = len(build.qualitative)
        if total:
            suffix = f" — {total}"
            if dead_count:
                suffix += (f", <span style='color:{BAD}'>{dead_count} not "
                           f"working</span>")
        else:
            suffix = " — none"
        self.qual_heading.setText(f"Conditional &amp; situational{suffix}")
        self.qual_heading.setVisible(True)

        self._sync_situational(build.situational, declared)

        switchable = {entry.name for entry in build.situational}
        rest = [row for row in build.qualitative if row[0] not in switchable]
        if rest:
            lines = []
            for name, detail, why in rest:
                dead = why.startswith("NOT WORKING")
                head = BAD if dead else ACCENT
                shown = f"<s>{name}</s>" if dead else name
                lines.append(
                    f"<div style='margin-bottom:6px'>"
                    f"<span style='color:{head}'>{shown}</span>"
                    f"<div style='color:#cfcfcf; font-size:11px'>{detail}</div>"
                    f"<div style='color:{BAD if dead else MUTED}; "
                    f"font-size:10px'>{why}</div>"
                    f"</div>"
                )
            self.qual_label.setText("".join(lines))
        elif build.situational:
            # The switches above are the whole list. Repeating "nothing depends
            # on a condition" underneath them would contradict them.
            self.qual_label.clear()
        else:
            self.qual_label.setText(
                f"<span style='color:{MUTED}; font-size:11px'>Nothing you have "
                f"equipped depends on a condition. Effects that only work "
                f"below a HP threshold, with a particular armament, or on a "
                f"trigger would be listed here.</span>"
            )
        self.qual_label.setVisible(bool(self.qual_label.text()))

        curses = self.planner.selected_curses()
        if curses:
            lines = []
            for source, eff in curses:
                detail = effecttext.describe_full(eff)
                lines.append(
                    f"<div style='margin-bottom:6px'>"
                    f"<span style='color:{BAD}'>✦ {effecttext.name(eff)}</span>"
                    f"<div style='color:{MUTED}; font-size:11px'>{detail}</div>"
                    f"<div style='color:{MUTED}; font-size:10px'>from {source}</div>"
                    f"</div>"
                )
            self.curse_label.setText("".join(lines))
        elif self.planner.deep_check.isChecked():
            self.curse_label.setText(
                f"<span style='color:{GOOD}'>none on the equipped relics</span>"
            )
        else:
            self.curse_label.setText(
                f"<span style='color:{MUTED}'>only Deep of Night relics carry "
                f"curses — tick Deep of Night to plan with them</span>"
            )

        if build.warnings:
            self.warn_label.setText(
                "".join(
                    f"<div style='color:{BAD}; margin-bottom:6px'>⚠ {w.text}</div>"
                    for w in build.warnings
                )
            )
        else:
            self.warn_label.setText(
                f"<span style='color:{GOOD}'>All selected effects stack.</span>"
            )
