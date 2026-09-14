"""Nightreign Helper -- Nightfarer, chalice, relic slots, stat sheet."""

from __future__ import annotations

import html
import os
import pathlib
import sys
import traceback

from PySide6.QtCore import (QObject, QPoint, QProcess, QSettings, QSize, Qt,
                            QThread, Signal)
from PySide6.QtGui import (
    QColor, QCursor, QFont, QFontMetrics, QIcon, QPainter, QPalette, QPen,
    QPixmap,
)
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFileDialog,
    QFrame, QInputDialog,
    QGridLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QLineEdit, QMainWindow, QMessageBox, QPushButton, QScrollArea, QSizePolicy,
    QSlider, QSplitter, QTabWidget, QToolButton, QToolTip, QVBoxLayout,
    QWidget,
)

from nrdata import savefile

from . import __version__
from . import (advisorblock, chalices, damage, datasource, effecttext,
               errortext, favourites, firstrun, gamepath, inventory, model,
               shortcut, singleinstance, uiscale, weaponslots, weapons)
from .advisor import run as advisor_run
from .advisor.worker import (AdvisorController, PICKER_CACHE_SIZE,
                             PICKER_DEBOUNCE_MS)
from .advisorbar import AdvisorBar, asking_from, reading_label
from .effectstab import EffectsTab
from .iconpack import IconPack
from .arsenaltab import ArsenalTab
from .bosstab import BossTab
from .datasource import load_data
from .deeptab import DeepTab
from .depthstab import DepthsTab
from .eventstab import WorldEventsTab
from .relicslots import (RelicSlot, SLOT_COLOURS, _custom_effects,
                         _relic_count, slot_chip)

WHITE_SLOT = 4

# The four shared Grails sit under their own heroType rather than any
# Nightfarer's, because every Nightfarer can use them.
GRAIL_HERO_TYPE = 11

# Link target for the weapon attack-rating breakdown. Not a modifier field, so
# it is namespaced to keep it out of the way of the real ones.
AR_BREAKDOWN_KEY = "ar:total"

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

# Where the three panes' widths are kept, so a window sized once stays
# that way. QSplitter's own encoding, which survives a pane being added.
PANES_KEY = "ui/panes"

# The opening pane widths, shared by first run, the restore fallback and the
# Reset layout button so all three mean the same thing by construction.
PANE_DEFAULTS = (430, 520, 370)

#: How tall the window opens, in logical px. Unchanged from the size the
#: window has always given itself; no tab asks for more (AK-71), so nothing
#: on this side has to be derived.
OPENING_HEIGHT = 860

TILE_SIZE = 50
TILE_PAD = 6
VARIANT_STRIP = 46

#: What the Nightfarer's name is set in on its tile, in points (QA-155).
#:
#: The ten portraits carried no text at all, so a player had to click one and
#: read the answer somewhere else to find out whom he had picked. The name has
#: to fit the tile it names: the tile is `TILE_SIZE + TILE_PAD` wide and the
#: five columns of the grid have to stay inside the sidebar's 300 px floor, so
#: widening the tile would push the whole window's minimum out. Measured on
#: Windows under Fusion at 150 % scale, in logical px: the widest of the ten
#: names, `Undertaker`, asks 59 px at the default 9 pt, 54 at 8 and 44 at 7,
#: against the 52 px a 56 px tile has inside its border. Seven is the size at
#: which all ten stand whole; Qt shortens anything that does not fit and the
#: tooltip has carried the full name all along.
NAME_POINT_SIZE = 7

ACCENT = "#c8a45c"
GOOD = "#6fbf73"
BAD = "#d1655f"
MUTED = "#8a8a8a"
PANEL = "#1e1f23"
BORDER = "#2e2f35"


def _dark_palette() -> QPalette:
    p = QPalette()
    p.setColor(QPalette.Window, QColor("#16171a"))
    p.setColor(QPalette.WindowText, QColor("#e4e4e4"))
    p.setColor(QPalette.Base, QColor(PANEL))
    p.setColor(QPalette.AlternateBase, QColor("#26272c"))
    p.setColor(QPalette.Text, QColor("#e4e4e4"))
    p.setColor(QPalette.Button, QColor("#26272c"))
    p.setColor(QPalette.ButtonText, QColor("#e4e4e4"))
    p.setColor(QPalette.Highlight, QColor(ACCENT))
    p.setColor(QPalette.HighlightedText, QColor("#16171a"))
    return p


def apply_appearance(app: QApplication) -> None:
    """Style and palette, exactly as a player's run has them.

    One function so there is one answer. `main` set these two lines itself and
    the test suite set nothing, so Qt gave the suite `windowsvista` while a
    player ran Fusion -- and the two do not measure the same. Same data, same
    width, style the only variable: the `Effect` column of the effects table
    renders 446 px under windowsvista and 388 under Fusion at a 1600 px
    window, and the count of effect names too long for it goes from 12 to 44
    (QA-146). Nothing was falsely green, because the guards are written as
    relations that hold under both; every absolute figure ever reported from
    the suite was a figure off a machine nobody runs.

    Called by `main` and by `tests/conftest.py::qapp`. A second place saying
    what the program looks like is a second place for it to be said
    differently.
    """
    app.setStyle("Fusion")
    app.setPalette(_dark_palette())


def _heading(text: str) -> QLabel:
    label = QLabel(text.upper())
    font = label.font()
    font.setPointSize(8)
    font.setBold(True)
    font.setLetterSpacing(QFont.AbsoluteSpacing, 1.2)
    label.setFont(font)
    label.setStyleSheet(f"color: {MUTED};")
    return label


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
            # Free text, not a spin box with a ceiling. How many Night Invaders
            # a map can hold, or how many Sites of Grace are in reach, is a
            # fact about the run rather than about this program -- so the
            # player states the number and the arithmetic follows it.
            self.times = QLabel("×")
            self.times.setStyleSheet(f"color: {MUTED}; border: none;")
            head.addWidget(self.times, 0, Qt.AlignTop)
            self.count = QLineEdit(str(max(count, 1)))
            self.count.setFixedWidth(42)
            self.count.setAlignment(Qt.AlignCenter)
            self.count.setToolTip("How many times this is true right now")
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
            return max(int(text), 1)
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


class VesselStrip(QWidget):
    """The vessel's slots as one small row, the way the game shows them.

    The six editing panels below say what each relic *does*; this says what
    the chalice *is* -- which slots it has, what colour each one is, and which
    are filled. Reading that off six tall panels means scrolling; reading it
    off one row is a glance, which is the whole point of it.

    A Deep of Night vessel exposes three more slots, so the strip is three or
    six tiles wide and never a fixed six: showing three greyed tiles for slots
    the vessel does not have would be inventing a chalice.
    """

    TILE = 40
    ICON = 30

    def __init__(self, icons=None):
        super().__init__()
        self.icons = icons
        self._row = QHBoxLayout(self)
        self._row.setContentsMargins(0, 2, 0, 2)
        self._row.setSpacing(4)
        self._row.addStretch(1)
        self.tiles: list[QLabel] = []

    def show_slots(self, colours: list[int], items: list) -> None:
        """One tile per slot the vessel has: its colour, and its relic."""
        while self._row.count() > 1:
            item = self._row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.tiles = []

        for index, colour in enumerate(colours):
            tint = SLOT_COLOURS.get(colour, "#8a8a8a")
            backing = slot_chip(self.icons, colour,
                                items[index] if index < len(items) else None,
                                self.TILE)
            tile = QLabel()
            tile.setFixedSize(self.TILE, self.TILE)
            tile.setAlignment(Qt.AlignCenter)
            owned = items[index] if index < len(items) else None
            if backing is not None:
                tile.setPixmap(backing)
                tile.setStyleSheet("border: none; background: transparent;")
                tile.setToolTip(getattr(owned, "name", "") or "empty slot")
                self._row.insertWidget(index, tile)
                self.tiles.append(tile)
                continue
            # A filled slot is drawn in its colour; an empty one keeps the
            # colour as an outline only, so "this chalice has a red slot" and
            # "there is a red relic in it" never look the same.
            if owned is not None:
                tile.setStyleSheet(
                    f"background: rgba(255,255,255,18);"
                    f" border: 2px solid {tint}; border-radius: 5px;")
                icon = None
                if self.icons is not None:
                    icon = self.icons.item(getattr(owned, "icon", None))
                if icon is not None:
                    tile.setPixmap(icon.scaled(
                        self.ICON, self.ICON, Qt.KeepAspectRatio,
                        Qt.SmoothTransformation))
                tile.setToolTip(getattr(owned, "name", ""))
            else:
                tile.setStyleSheet(
                    f"background: transparent;"
                    f" border: 1px dashed {tint}; border-radius: 5px;")
                tile.setToolTip("empty slot")
            self._row.insertWidget(index, tile)
            self.tiles.append(tile)


#: What a slot says when its hold fell away because the relic went (§4.3,
#: AK-56). Said out loud rather than dropped quietly: a hold that vanished in
#: silence is the case that produces a suggestion the player did not ask for.
HOLD_RELEASED = ("A relic you were holding is no longer in your inventory, "
                 "so this slot was released.")

#: What the save line says while the first read of the session is out
#: (`UI_SPEC` T-141 §9 (a), AK-221). A state rather than a nothing: an empty
#: line here cannot be told apart from "no save was found".
READING_THE_SAVE = "Reading your save."

#: The same state on a `Rescan` (§9 (b)). The second sentence is the promise
#: of §3 -- everything on screen goes on being true until the answer lands --
#: and it is why the relic button is shut for exactly as long as it stands.
READING_THE_SAVE_AGAIN = ("Reading your save again. Nothing changes until it "
                          "is done.")

#: What the line says when there was no save to read (§9 (f), and S5 of the
#: first-run spec). The last sentence names the button that now stands beside
#: it: without the button the sentence would be a dead end, and without the
#: sentence the button is a word the player has no reason to press.
NO_SAVE_FOUND = ("No save file found. Relic slots stay empty; the Effects and "
                 "Weapons tabs still work in full. If your save is somewhere "
                 "else, use Find my save.")

#: The button of AK-123, and the ellipsis is three dots for the reason the
#: first-run panel's `Choose folder...` has three: another window follows.
FIND_MY_SAVE = "Find my save..."

#: S1, the one text of this flow that may name the file and the folder --
#: naming them is its whole job, and it is what makes the button pressable
#: for somebody who has never seen either.
FIND_MY_SAVE_TOOLTIP = ("Your save is a file called NR0000.sl2, in a folder "
                        "named Nightreign under your Windows user profile. "
                        "This opens there.")

#: S2. Unlike the folder dialog of the first run, whose caption is left to
#: Qt, this one is written here: the spec gives it as a text of this program
#: (AK-128), and a file dialog's caption is the only place that says which
#: file is being asked for.
CHOOSE_YOUR_SAVE = "Choose your Nightreign save file"

#: The three filter entries of section 5, in that order. The third is not an
#: oversight: `find_saves` deliberately takes renamed backups as well, so a
#: dialog that refused them would be stricter than the program behind it.
SAVE_FILE_FILTERS = ("Nightreign save (NR*.sl2);;"
                     "Save file (*.sl2);;"
                     "All files (*)")

#: S3, the second of the three exits (AK-124): the file was read and holds
#: nothing. Not a failure, and it says the one thing that explains it -- two
#: Steam accounts, which is the case this whole flow exists for.
CHOSEN_SAVE_IS_EMPTY = ("That save has no relics in it yet. If you play on "
                        "more than one Steam account, this may be the wrong "
                        "one.")

#: S4, the third exit: the player's sentence, and the technical reason under
#: it on its own line. The order is DESIGN_REVIEW DR-006 -- what happened
#: first, why second.
CHOSEN_SAVE_UNREADABLE = "That file is not a Nightreign save this can read."

#: The one place this prefix is written (§8, AK-229). It stands only where no
#: inventory came out of the read at all, so nothing behind it may claim that
#: the save is fine.
UNREADABLE_SAVE = "Save could not be read: "

#: §9 (d), appended to the inventory note exactly like `loadout_error` --
#: same leading dash, same "on to whatever the note already says". Said when
#: `Inventory.read_the_slow_way` is set (AD-031, AK-228): the fast prefilter
#: could not see every id this save's relics use, so the slower walk was read
#: instead. Written only on to a note that already names a relic count, so it
#: can never land behind the prefix above (AK-229): the read still worked.
READ_THE_SLOW_WAY_NOTE = (
    " — read the slow way: this version of the game numbers its relics "
    "above what the quick scan looks for. Nothing is missing and nothing "
    "needs fixing.")

#: The line of its own that the total belongs on (`UI_SPEC` T-178 §4, AK-251).
#: `You own` is the scope the player was looking for and tells this number
#: apart from the two it was confused with: what fits one slot
#: (`Slot 1 — Red (51 available)`) and what the game knows at all
#: (`577 buffs, 75 curses`). `in total` is the bearing on the slot number,
#: without which a bare number stands beside a bare number again.
OWNED_TOTAL = "You own {count} in total."

#: The tooltip of the same line: where the number was counted from, and the
#: confusion resolved in as many words. It does not say the slot number is
#: *smaller* -- it can be equal, when everything the player owns fits the one
#: slot, and an assurance that breaks in a corner is not one.
OWNED_TOTAL_TOOLTIP = ("Counted from your save {source}. The number beside a "
                       "relic slot counts only the relics that fit that slot.")


class HeroTile(QToolButton):
    """One portrait in the 2x5 Nightfarer grid, with the name under it.

    Left click selects the Nightfarer; right click offers that character's
    alternate illustrations so the tile can show a preferred one.

    The name is drawn on the tile because the artwork alone did not say who
    it was (QA-155): the player of 2026-09-06 clicked a portrait and then had
    to find the answer elsewhere on the screen. See NAME_POINT_SIZE for what
    decides the size of it.
    """

    def __init__(self, index: int, hero: dict, icons):
        super().__init__()
        self.index = index
        self.hero = hero
        self.icons = icons
        self.variant_id: int | None = None

        self.setCheckable(True)
        self.setAutoRaise(True)
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setText(hero["name"])
        font = self.font()
        font.setPointSize(NAME_POINT_SIZE)
        self.setFont(font)
        self.setIconSize(QSize(TILE_SIZE, TILE_SIZE))
        # Before the height is fixed, and that order is load-bearing:
        # `QToolButton::initStyleOption` reports a button with no icon and
        # some text as text-only however it was configured, so a size asked
        # for here first comes back 19 px tall -- one line of name and no
        # portrait at all.
        self._apply_image()
        # The width is the grid's to keep; the height is whatever the name
        # needs under the portrait, asked of Qt rather than added up here, so
        # a different font or a different scale still gets a whole line.
        self.setFixedSize(TILE_SIZE + TILE_PAD, self.sizeHint().height())
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # A visible frame keeps neighbouring portraits from reading as one
        # continuous image, since the artwork itself has no margin. Two pixels
        # in both states: a border that thickened on selection would narrow
        # the room the name has by 2 px, and the longest of the ten would
        # shorten itself the moment it was picked.
        self.setStyleSheet(
            f"QToolButton {{ border: 2px solid {BORDER}; border-radius: 4px;"
            f" background: {PANEL}; padding: 0px; color: {MUTED}; }}"
            f"QToolButton:checked {{ border: 2px solid {ACCENT};"
            f" color: {ACCENT}; }}"
        )
        self.setToolTip(f"{hero['name']}\nRight-click to change the artwork")
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_variants)

    def current_pixmap(self):
        if self.variant_id is not None:
            pixmap = self.icons.variant(self.variant_id)
            if pixmap is not None:
                return pixmap
        return self.icons.portrait(self.hero["id"])

    def _apply_image(self) -> None:
        pixmap = self.current_pixmap()
        if pixmap is not None:
            self.setIcon(QIcon(pixmap))
        else:
            # No artwork for this Nightfarer: the DLC characters' assets live
            # in dlc01, whose archive key is not published. Draw initials so
            # the tile keeps the exact same footprint as the others.
            self.setIcon(QIcon(self._placeholder()))

    def _placeholder(self) -> QPixmap:
        pixmap = QPixmap(TILE_SIZE, TILE_SIZE)
        pixmap.fill(QColor("#26272c"))
        painter = QPainter(pixmap)
        painter.setPen(QColor(MUTED))
        font = painter.font()
        font.setPointSize(18)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, self.hero["name"][:2])
        painter.end()
        return pixmap

    def _show_variants(self, _point) -> None:
        # Handled by the window, which shows the strip inside the sidebar.
        window = self.window()
        if hasattr(window, "show_variant_strip"):
            window.show_variant_strip(self)

    def set_variant(self, texture_id: int | None) -> None:
        self.variant_id = texture_id
        self._apply_image()
        settings = QSettings(favourites.ORG, favourites.APP)
        settings.setValue(f"variant/{self.hero['id']}", texture_id if texture_id else "")

    def restore_variant(self) -> None:
        settings = QSettings(favourites.ORG, favourites.APP)
        stored = settings.value(f"variant/{self.hero['id']}", "")
        if stored:
            self.variant_id = int(stored)
            self._apply_image()


#: How long the window waits for a running save read when it is closing. A
#: `wait()` in the main thread is forbidden while the program is running
#: (AD-006.4) and is the only correct thing here: the alternative is a
#: `QThread` deleted while its read is still going.
#:
#: Derived, not chosen. What this waits for is `inventory.scan`, measured at
#: 657,2 ms (p50, the player's own save, S11-E carried forward in T-140). Its
#: worst measured shape is the same read on the same save and the same machine
#: before the prefilter existed: 6147,6 ms. Ten per cent over that is what is
#: waited, so a save the prefilter turns out not to help still finishes its
#: read instead of losing its thread underneath it: 6147,6 x 1,1 = 6762 ms,
#: rounded up.
SAVE_READ_SHUTDOWN_WAIT_MS = 6800

def where_saves_usually_are() -> pathlib.Path | None:
    """Where the file dialog opens (AK-123, section 5).

    The start location is the actual help in this dialog: the player cannot
    type the variable his profile lives under and should not have to. So the
    `Nightreign` folder if it is there, the profile itself if it is not, and
    None -- "wherever Qt would" -- if neither is.

    Resolved, always, and never named as a variable anywhere he can read it
    (AK-127): what he sees in the dialog is a path.
    """
    roots = savefile.save_roots()
    for folder in roots:
        if folder.is_dir():
            return folder.resolve()
    for folder in roots:
        if folder.parent.is_dir():
            return folder.parent.resolve()
    return None


def _pick_a_save_file(parent) -> pathlib.Path | None:
    """The system's own file dialog, opened where the saves are.

    Native, for the reason `firstrun._pick_a_folder` gives: it is the dialog
    the player knows from everything else on his machine, with his quick
    access places and his network drives in it.

    A file and not a folder, which is the difference from the first run's
    question and the reason it is the right one here: with two Steam accounts
    the file is the only thing that says *which* account he means.
    """
    start_at = where_saves_usually_are()
    picked, _chosen_filter = QFileDialog.getOpenFileName(
        parent, CHOOSE_YOUR_SAVE,
        "" if start_at is None else os.fspath(start_at),
        SAVE_FILE_FILTERS)
    return pathlib.Path(picked) if picked else None


def _refuse_a_file_no_save_can_be(path: pathlib.Path) -> None:
    """Ask SEC-029's question of the file the player named, before any read.

    The limit itself and the sentence it is refused with live in
    `inventory.refuse_a_size_no_save_can_have`, which the read behind this
    asks again of every file either route hands it. One number, one wording,
    two places that can be reached -- and this one is reached first, so that
    the second read of `read_the_save`, the one that tells S3 from S4, is
    never given a file this size either.
    """
    inventory.refuse_a_size_no_save_can_have(path.stat().st_size)


def read_the_save(data: dict, save_path: pathlib.Path | None = None):
    """Read the save the window is to show, and answer for the file it read.

    The default reading of `SaveReader`, and the one place the three exits of
    AK-124 are told apart. `inventory.scan` cannot tell them apart and should
    not: it answers None both for "there is no save here" and for "this file
    holds no relics", and it swallows an unreadable file on purpose, because
    on the automatic route the next file may well be the good one.

    For a file the **player pointed at** those are three different pieces of
    news, and he is owed the difference: a scan gives the ordinary line, a
    None means the file was read and holds nothing (S3), and a raise carries
    the reason he cannot be expected to guess (S4).

    **No path and no Windows wording is ever put into the reason.** The save
    folder is named after the Steam account id (AK-126), and an `OSError`
    writes the whole path into its message; `strerror` drops the path but is
    in the language of the Windows installation and broke A8 (QA-211). What
    comes out of one here is `errortext`'s sentence for its `errno`, and it
    leaves as this module's own class so that the window may quote it.
    """
    if save_path is None:
        return inventory.scan(data)
    try:
        _refuse_a_file_no_save_can_be(save_path)
        found = inventory.scan(data, save_path)
        if found is None:
            # Reading it again is what tells S3 from S4, and it is only ever
            # done when the scan came back empty -- so the ordinary case pays
            # nothing for it, and the two cases that are left are the ones
            # the player is about to ask about.
            savefile.read(save_path)
        return found
    except OSError as exc:
        raise inventory.SaveNotReadable(errortext.in_english(exc)) from None


class _SaveReadWorker(QObject):
    """One reading of the save, off the main thread. Built once and dropped.

    Never touches a widget, not even to read one: it is built with the dataset
    it needs and everything it has to say goes out as a signal Qt delivers
    into the main thread's event loop.

    **The generation is stamped on here and nowhere else**, exactly as the
    advisor's `_Worker` stamps an answer (AD-006.3): this is the one place
    that knows both which reading was asked for and what came back, so
    `inventory.scan` does not have to know that generations exist.
    """

    #: What the save held, as a `SaveScan` -- or `None` when no save was
    #: found, which is an answer and not a failure.
    ready = Signal(int, object)
    #: A read that could not be finished, in one line and without a traceback.
    #: An exception that merely propagated would end the thread in silence and
    #: leave the window on its waiting sentence for ever (AK-224). The line is
    #: `errortext`'s and never the exception's own: anything at all can come
    #: out of `self._read`, and whatever Windows would have said here it would
    #: have said in its own language (QA-211, A8).
    failed = Signal(int, str)
    #: Always last, whatever happened, so the thread is quit from one place.
    finished = Signal()

    def __init__(self, generation: int, data: dict, read,
                 save_path: pathlib.Path | None = None) -> None:
        super().__init__()
        self._generation = generation
        self._data = data
        self._read = read
        # Which file this reading is about, or None for "whichever the
        # automatic route finds". Handed in rather than looked up here: the
        # settings store is the main thread's, and a `stat` on a dead network
        # path is exactly what this thread exists to keep off it.
        self._save_path = save_path

    def work(self) -> None:
        try:
            found = self._read(self._data, self._save_path)
        except Exception as exc:  # noqa: BLE001 - reported, never raised on
            traceback.print_exc()
            self.failed.emit(self._generation, errortext.in_english(exc))
        else:
            self.ready.emit(self._generation, found)
        self.finished.emit()


class SaveReader(QObject):
    """One reading of the save at a time, in a thread, and never out of date.

    The same build as `AdvisorController` and deliberately not a second
    mechanism (AD-029, AD-028): a worker in a `QThread`, a generation counter
    that decides whether an answer still belongs to anybody, and a `shutdown`
    that is the one place a `wait()` in the main thread is right.

    Three differences, each because the two are asked different questions:

    * **no debounce.** `Rescan save` is a click, not a dragged slider, and a
      second click while a read is out starts nothing at all (AD-029 point 4)
      rather than replacing what is running.
    * **no cache.** A rescan exists to find out what changed on disk; an
      answer kept from the last one is the one thing it must not hand back.
    * **no cancelling.** `inventory.scan` has no place to look at a flag, and
      a read the player abandoned costs the window nothing -- the generation
      is what keeps its answer off the screen.

    What crosses the thread boundary is a `SaveScan` and nothing else
    (AD-029 point 1): records read out of bytes, never the living `Inventory`,
    which the main thread builds out of them at the arrival (AD-006.8).

    **What is read is handed in at construction**, the seam AD-028 built for
    the advisor's two tracks: a case can state a read that never answers, one
    that answers at once, or one that fails, and drive the whole real way --
    thread, signal, generation check, window.
    """

    #: The scan for the read that is still the current one. Never for an
    #: overtaken one: those are dropped here, wordlessly.
    ready = Signal(object)
    #: A read that could not be finished, in one line.
    failed = Signal(str)

    def __init__(self, parent: QObject | None = None, *, read=None) -> None:
        super().__init__(parent)
        # Looked up when a read starts and not written down here, so that
        # `None` really means "whatever `read_the_save` is at that moment".
        # A default bound at import time would be a different function from
        # the one a case had put in the module, and the case would pass by
        # measuring the wrong thing.
        self._read = read
        self._generation = 0
        self._answering = False
        self._thread: QThread | None = None
        self._worker: _SaveReadWorker | None = None

    @property
    def generation(self) -> int:
        """Which reading is the current one (AD-006.3)."""
        return self._generation

    def is_reading(self) -> bool:
        """Is an answer still to come?

        Not "is a thread alive": the window asks this to decide what it may
        say and what it may do, and from the moment the answer has been handed
        over there is nothing left to wait for. The two part company for one
        turn of the event loop -- the worker's `finished` is queued behind its
        `ready` -- and a window that read the thread instead would refuse, at
        the arrival, the very import the arrival is there to do.
        """
        return self._answering

    def start(self, data: dict, save_path: pathlib.Path | None = None) -> bool:
        """Begin a read, unless one is already out. Says which it did.

        One read at a time (AD-029 point 4). A second `Rescan` while the first
        is still going does nothing whatever -- it does not queue, it does not
        replace -- because the line under the button already says what is
        happening and the answer that is coming is the one the player wants.

        `save_path` is the file the player picked, resolved by the caller in
        the main thread (AD-030). None is "let the automatic route decide",
        which is what it has always been.

        Hands back whether it started one, so the window can tell a read it
        has to draw a waiting state for from a click that changed nothing.
        """
        if self._thread is not None:
            return False
        self._generation += 1
        self._answering = True
        self._thread = QThread()
        self._worker = _SaveReadWorker(self._generation, data,
                                       self._read or read_the_save, save_path)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.work)
        self._worker.ready.connect(self._on_ready)
        self._worker.failed.connect(self._on_failed)
        self._worker.finished.connect(self._thread.quit)
        self._thread.finished.connect(self._on_thread_finished)
        self._thread.start()
        return True

    def shutdown(self, timeout_ms: int = SAVE_READ_SHUTDOWN_WAIT_MS) -> None:
        """Stop caring about the read and wait for it. Closing only.

        **The generation goes up first**, and that line is the whole of the
        lesson from the advisor's `shutdown` (Nachtrag X-1): a worker that
        emitted its answer between the last check and the wait has left a
        `ready` in the main thread's queue, `wait()` does not empty that
        queue, and the turn of the event loop that the closing itself is would
        deliver it to a window that is already going. Silence after `shutdown`
        is meant to be a property of this class, and this is what makes it one
        rather than a race no guard could watch without flickering.

        Nothing is emitted here and nothing will be. There is nobody left to
        read a sentence.
        """
        self._generation += 1
        self._answering = False
        thread = self._thread
        if thread is not None:
            thread.wait(timeout_ms)

    def _on_thread_finished(self) -> None:
        """Clear the read away, so the next `Rescan` can start one."""
        self._worker.deleteLater()
        self._thread.deleteLater()
        self._worker = None
        self._thread = None

    def _on_ready(self, generation: int, found) -> None:
        """Pass the scan on, if it is still the reading anybody is waiting for."""
        self._answering = False
        if generation != self._generation:
            return
        self.ready.emit(found)

    def _on_failed(self, generation: int, reason: str) -> None:
        """A read that could not be finished, if anyone is still waiting.

        Judged by the same generation as an answer: a failure of a reading
        nobody is waiting for any more is not news, and the sentence on screen
        would be about a state that no longer exists.
        """
        self._answering = False
        if generation != self._generation:
            return
        self.failed.emit(reason)


class Planner(QMainWindow):
    def __init__(self, data: dict, *, read_save=None):
        """The window, and what it reads the save with.

        `read_save` is the seam AD-028 built for the advisor's two tracks,
        here for the one thing about this window that a case cannot otherwise
        reach: a read that never answers, one that answers at once, one that
        fails, one that finds no save. `None` is `read_the_save`, which is
        what a player always gets, and nothing but the reading goes through
        it.
        """
        super().__init__()
        self.data = data
        self.effects = data["effects"]
        self.effect_list = list(self.effects.values())
        self.heroes = data["heroes"]
        self.vessels = data["vessels"]
        self.curves = data.get("curves", {})
        self.icons = IconPack()
        self.hero_index = 0
        # The six armament tiles, and one saved set per Nightfarer. Slot 1
        # defaults to that Nightfarer's starting armament, but anything you
        # build is kept for the rest of the session, so switching Nightfarer
        # and back does not undo it. Not persisted to disk -- it lasts the run
        # of the program, no longer.
        self.weapon_slots: list[weaponslots.WeaponSlot] = [
            weaponslots.WeaponSlot() for _ in range(weaponslots.SLOT_COUNT)
        ]
        self.weapon_loadouts: dict[int, list[weaponslots.WeaponSlot]] = {}
        # Which tile the damage breakdown describes.
        self.active_weapon = 0
        # effect id -> how many times the player says its condition is met.
        # Session state, like the armament tiles: a declaration is about the
        # run you are in, not a preference worth remembering across launches.
        self.declared: dict[int, int] = {}
        # The advisor's reading (`GOAL.md` A16, AD-035): True is the worst
        # case, every conditional curse counted; False the best, every
        # conditional buff. Window state like `declared`, set by the bar's
        # `reading_changed`, not persisted -- and it reaches a run only as a
        # default for `declared`, never as a number.
        self.worst_case = True
        # The build every tab reads, computed once per change by recompute().
        # None until the first one has been computed.
        self._build: model.Build | None = None
        # Held while a stored build is being put back, so the act of restoring
        # a vessel and six relics does not write a half-restored build over
        # the one still being read.
        self._restoring = False
        # Set when a restore had to take a relic out of a slot because another
        # slot holds the same physical one. The stored build is then left as
        # it was, so the player can still decide which slot keeps it.
        self._unresolved_clash = False
        # What every slot held before the answer on screen was first applied,
        # as stored keys, or None while there is nothing to undo. Taken once
        # per answer and not once per applying: `Use` on three slots one after
        # another is one act of applying seen from three cards, and 4.13 says
        # `Undo puts your slots back as they were` -- as they were before any
        # of it, which is the only reading a single button can carry.
        self._slots_before_applying: list[str] | None = None
        # Which slots the player is holding, per (Nightfarer, vessel, Deep),
        # and which copy each hold was made on (AD-017.2). Session state of
        # the window and **nowhere else**: nothing here reaches `QSettings`,
        # so a hold cannot outlive the program (OF-15) and no stored key
        # space grows by a byte. Three losses of data in that key space in
        # cycles 4 and 5 are the reason, not convenience -- a held handle
        # written down today points at a copy that may be melted tomorrow.
        self._holds: dict[tuple[int, int | None, bool],
                          dict[int, int | None]] = {}

        # The data version is a build number off the game install. It means
        # nothing to a player and ate half the title bar, so the title just
        # names the tool. Only a re-read after a patch is worth saying, and it
        # is said in words rather than as a version id.
        # The tool's own version does belong in the title: it is the one thing
        # a bug report needs and the one thing a reporter cannot look up after
        # the fact.
        stale = data.get("meta", {}).get("regenerated")
        self.setWindowTitle(
            f"Nightreign Helper {__version__}"
            + ("  —  updated for your installed game version" if stale else "")
        )
        # No resize here. The opening width is derived from the effect
        # table, which does not exist yet -- see showEvent.

        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        # A Start Menu entry is offered during first-run setup, which a player
        # upgrading from an earlier version never sees, and which anyone can
        # decline and later want. So it also lives here, permanently, in the
        # one piece of chrome that is on screen whichever tab is open. A corner
        # widget rather than a menu bar: the window has never had one, and
        # growing one for a single action would cost more room than it earns.
        self.shortcut_button = QToolButton()
        self.shortcut_button.setAutoRaise(True)
        self.shortcut_button.setCursor(Qt.PointingHandCursor)
        self.shortcut_button.clicked.connect(self._toggle_shortcut)
        self._sync_shortcut_button()

        # How large the interface is drawn goes beside it, for the same
        # reason: it belongs to no tab, and this is the only chrome on screen
        # whichever tab is open. Automatic follows Windows, which is what the
        # program has always done and stays the default.
        corner = QWidget()
        corner_row = QHBoxLayout(corner)
        corner_row.setContentsMargins(0, 0, 6, 0)
        corner_row.setSpacing(6)
        scale_caption = QLabel("UI scale")
        scale_caption.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        corner_row.addWidget(scale_caption)
        self.scale_box = QComboBox()
        for label, value in uiscale.CHOICES:
            self.scale_box.addItem(label, value)
        stored_scale = self.scale_box.findData(uiscale.stored())
        self.scale_box.setCurrentIndex(max(stored_scale, 0))
        self.scale_box.setToolTip(
            "How large everything is drawn, on top of Windows' own display "
            "scaling. Automatic is Windows' setting unchanged."
        )
        self.scale_box.activated.connect(self._choose_scale)
        corner_row.addWidget(self.scale_box)
        # A way back for the panes. Anyone can drag a splitter somewhere
        # unfortunate, and 1.7.0 could store such a state on its own; without
        # an inverse the player's only route was hand-editing the registry.
        reset_layout = QPushButton("Reset layout")
        reset_layout.setToolTip(
            "Put the three Build planner panes back to their opening widths")
        reset_layout.clicked.connect(self._reset_layout)
        corner_row.addWidget(reset_layout)
        if shortcut.available():
            corner_row.addWidget(self.shortcut_button)
        tabs.setCornerWidget(corner, Qt.TopRightCorner)

        planner = QWidget()
        root = QHBoxLayout(planner)
        root.setContentsMargins(14, 14, 14, 14)
        # The splitter draws its own gaps, so the layout no longer adds any.
        root.setSpacing(0)

        # Panes rather than three columns pinned to the pixel. The sidebar was
        # 430 wide and the sheet 370 on every machine, so the same numbers had
        # to serve a laptop and a 4K monitor: relic names were cut off on one
        # while the sheet had room going spare on the other, and nothing could
        # be done about either. Collapsing is off -- a pane dragged shut
        # leaves nothing on screen to say it is still there, and reads as the
        # program having lost it.
        self.panes = QSplitter(Qt.Horizontal)
        self.panes.setChildrenCollapsible(False)
        self.panes.setHandleWidth(10)
        self.panes.addWidget(self._build_left())
        self.panes.addWidget(self._build_middle())
        self.panes.addWidget(self._build_right())
        self._wire_the_advisor()
        # Extra width goes to the slots in the middle; the two edges keep the
        # size they were given, which is what they had before.
        self.panes.setStretchFactor(0, 0)
        self.panes.setStretchFactor(1, 1)
        self.panes.setStretchFactor(2, 0)
        self.panes.setSizes(list(PANE_DEFAULTS))
        stored_panes = QSettings(favourites.ORG, favourites.APP).value(PANES_KEY)
        if stored_panes:
            try:
                self.panes.restoreState(stored_panes)
            except TypeError:
                pass    # a key from some older shape of this setting
            # No validation here, and that is deliberate: sizes() before the
            # first layout returns placeholder values (measured: [276, 68,
            # 276] for a stored [520, 328, 420]), so any check at this point
            # condemns good states. The pane floors and childrenCollapsible
            # already clamp a genuinely broken state at layout time --
            # smoke_layout.py proves a stored [4000, 4000, 0] comes back with
            # the stat sheet at its floor -- and Reset layout is the way out
            # of anything merely unfortunate.
        root.addWidget(self.panes)

        # Written once, on the way out. splitterMoved fires for every pixel of
        # a drag, and a settings write per pixel is a lot of nothing.
        instance = QApplication.instance()
        if instance is not None:
            instance.aboutToQuit.connect(self._store_layout)

        tabs.addTab(planner, "Build planner")
        self.effects_tab = EffectsTab(data)
        tabs.addTab(self.effects_tab, "Effects && chances")

        self.owned = None
        # Set when the player put something in a slot themselves while the
        # first read was still out. The stored build of the Nightfarers in it
        # is then not taken over -- not at the arrival and not at a later
        # change of Nightfarer either (AK-226). A set of hero ids and not a
        # setting: it is about this session, and OF-15 is why nothing new goes
        # into the settings store.
        self._own_slots_beat_the_stored_build: set[int] = set()
        # Is the read that is out the answer to a file the player just
        # picked? The three exits of AK-124 are the answer to *a choice*: the
        # same three endings on an ordinary start are the four endings of
        # `UI_SPEC` section 9, which are worded for a save nobody pointed at.
        # Session state and nothing else -- OF-15 is why nothing new goes
        # into the settings store beyond the one path key.
        self._answers_a_chosen_save = False
        self.save_reader = SaveReader(self, read=read_save)
        self.save_reader.ready.connect(self._on_save_read)
        self.save_reader.failed.connect(self._on_save_failed)
        self.rescan_save(initial=True)
        # With the reading in the background this runs on no inventory, which
        # is the point: every tab that does not come out of the save is
        # complete in the first paint (AK-220). What the save would have added
        # is added at the arrival, by `_on_save_read`.
        self.select_hero(0)

        self.weapons_tab = ArsenalTab(data, self, self.icons)
        tabs.addTab(self.weapons_tab, "Weapons && spells")
        # Recalculate when the weapons tab comes to the front, so it always
        # reflects the build currently set up on the planner tab.
        tabs.currentChanged.connect(
            lambda index: self.weapons_tab.recalculate()
            if tabs.widget(index) is self.weapons_tab else None
        )

        # Reference tabs. None of these depend on the build, so they are built
        # once and never recalculated. They are skipped entirely when the
        # snapshot predates them rather than showing three empty tabs.
        if data.get("bosses"):
            self.boss_tab = BossTab(data, self.icons)
            tabs.addTab(self.boss_tab, "Nightlords")
        if data.get("deep_of_night"):
            self.deep_tab = DeepTab(data)
            tabs.addTab(self.deep_tab, "Deep of Night")
            self.depths_tab = DepthsTab(data)
            tabs.addTab(self.depths_tab, "Red variants")
        if (data.get("world_events") or {}).get("events"):
            self.events_tab = WorldEventsTab(data)
            tabs.addTab(self.events_tab, "World Events")

    # -- panels ----------------------------------------------------------
    def _build_left(self) -> QWidget:
        panel = QWidget()
        # 430 is what this pane opens at, and is no longer all it can be:
        # it is a pane of a splitter now, and the player sizes it. The floor
        # is what a vessel's icon and its six slots need before the name has
        # anywhere left to go -- below that the list stops saying which vessel
        # each row is, which is worse than a scrollbar.
        panel.setMinimumWidth(300)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(_heading("Nightfarer"))
        grid = QGridLayout()
        grid.setSpacing(4)
        self.hero_tiles: list[HeroTile] = []
        for i, hero in enumerate(self.heroes):
            tile = HeroTile(i, hero, self.icons)
            tile.restore_variant()
            tile.clicked.connect(
                lambda _checked=False, index=i: self.select_hero(index)
            )
            self.hero_tiles.append(tile)
            grid.addWidget(tile, i // 5, i % 5)
        layout.addLayout(grid)

        # Artwork chooser lives inside the sidebar rather than in its own
        # window, and stays hidden until a portrait is right-clicked.
        self.variant_panel = QFrame()
        self.variant_panel.setVisible(False)
        self.variant_panel.setStyleSheet(
            f"QFrame {{ background: {PANEL}; border: 1px solid {BORDER};"
            f" border-radius: 5px; }}"
        )
        strip_outer = QVBoxLayout(self.variant_panel)
        strip_outer.setContentsMargins(6, 5, 6, 6)
        strip_outer.setSpacing(4)

        self.variant_title = QLabel()
        self.variant_title.setStyleSheet(
            f"border: none; color: {MUTED}; font-size: 10px;"
        )
        strip_outer.addWidget(self.variant_title)

        # A grid, not a row. Seven variants at 50px need 374px of width and
        # the sidebar has about 250, so a single row was being squeezed until
        # the tiles overlapped each other. Wrapping keeps every tile its full
        # size however many there are.
        self.variant_row = QGridLayout()
        self.variant_row.setSpacing(4)
        self.variant_row.setContentsMargins(0, 0, 0, 0)
        strip_outer.addLayout(self.variant_row)
        layout.addWidget(self.variant_panel)

        self.hero_name_label = QLabel()
        self.hero_name_label.setAlignment(Qt.AlignCenter)
        self.hero_name_label.setStyleSheet(
            f"color: {ACCENT}; font-size: 14px; font-weight: bold;"
        )
        layout.addWidget(self.hero_name_label)

        layout.addSpacing(8)
        # "Chalice" named the section and also one of the seven things in it,
        # next to Urns and Goblets. "Vessel" is the category; a Chalice is one
        # kind of vessel.
        layout.addWidget(_heading("Vessel"))
        self.chalice_list = QListWidget()
        # Wide enough for the vessel's own icon plus its slots drawn beside
        # it; six of them in Deep of Night is the widest case.
        self.chalice_list.setIconSize(QSize(34 + 5 + 6 * 24, 34))
        self.chalice_list.currentRowChanged.connect(lambda *_: self.apply_chalice())
        layout.addWidget(self.chalice_list, 1)

        self.deep_check = QCheckBox("Deep of Night (3 extra slots)")
        self.deep_check.toggled.connect(self._on_deep_toggled)
        layout.addWidget(self.deep_check)

        layout.addSpacing(6)
        # AK-250: the total gets a line of its own, in the gap that was
        # already here, at the head of the group that is about the save --
        # `Rescan save`, `Load equipped`, `Find my save` and the note under
        # them. The number is a property of the save that was read, so it
        # stands with the save's controls; the head of this pane belongs to
        # the Nightfarer's identity, and a stock figure there would sit
        # beside figures that count something else (`UI_SPEC` T-178 §3.1).
        #
        # It is not in `owned_label`, and that is the whole point: the number
        # was in that line all along and the first `Load equipped` wiped it
        # (QA-201). Exactly one function writes this widget.
        self.owned_total_label = QLabel()
        self.owned_total_label.setWordWrap(True)
        # A save's own slot name reaches this line through the tooltip, so it
        # is told once what it is told at every other place a save writes
        # (SEC-004): text, never markup.
        self.owned_total_label.setTextFormat(Qt.PlainText)
        # No colour of its own: the ordinary text colour of the dark palette,
        # one step above the 10 px note and one below the Nightfarer's name.
        self.owned_total_label.setStyleSheet("font-size: 12px;")
        # Polished first, so the height below is asked of the font the style
        # sheet gives this label and not of the one it was born with.
        self.owned_total_label.ensurePolished()
        # Room for its one line from the first paint, empty or not, so that
        # the arrival of the save does not push the buttons under it down
        # (AK-252, the same rule AK-225 sets for the note below).
        self.owned_total_label.setMinimumHeight(
            self.owned_total_label.fontMetrics().lineSpacing())
        layout.addWidget(self.owned_total_label)

        row = QHBoxLayout()
        self.rescan_button = QPushButton("Rescan save")
        self.rescan_button.clicked.connect(self.rescan_save)
        row.addWidget(self.rescan_button)
        self.import_button = QPushButton("Load equipped")
        self.import_button.setToolTip(
            "Load this Nightfarer's equipped vessel and relics from the save"
        )
        self.import_button.clicked.connect(self.load_equipped)
        row.addWidget(self.import_button)
        # AK-123: a third button, and only while there is no save. A real
        # button in this row rather than a link in the 10 px line under it --
        # an offer the player overlooks does not solve A15.
        #
        # Hidden at the start and shown by whichever ending of a read finds
        # no inventory. Not "hidden while a save is loaded": that would make
        # it appear during the first read and disappear again at the arrival,
        # and this row is one of the places AK-106 says the successful case
        # does not change.
        self.find_save_button = QPushButton(FIND_MY_SAVE)
        self.find_save_button.setToolTip(FIND_MY_SAVE_TOOLTIP)
        self.find_save_button.clicked.connect(self.find_my_save)
        self.find_save_button.setVisible(False)
        row.addWidget(self.find_save_button)
        layout.addLayout(row)

        self.owned_label = QLabel()
        self.owned_label.setWordWrap(True)
        # This label prints the save's own slot name, and a save is a file the
        # player may have been handed by someone else. A QLabel left on
        # AutoText decides for itself whether what it was given is markup, so
        # a slot named "<img src='//host/share/x'>" would be rendered as an
        # image rather than shown as the name it is (SEC-004). Nothing here
        # ever wants markup, so the label is told so once, at the one place it
        # is built, rather than at each of the seven places it is written.
        self.owned_label.setTextFormat(Qt.PlainText)
        self.owned_label.setStyleSheet(f"color: {MUTED}; font-size: 10px;")
        # Room for two lines from the first paint, so that the arrival of the
        # save does not push what is under this line down (AK-225).
        #
        # Measured offscreen under Fusion at this pane's default width of 430
        # logical px, 100 % scaling, on the player's own save: the waiting
        # sentence `Reading your save.` takes 10 px and the inventory note
        # `309 relics in USER_DATA000, 110 stored builds` takes 22 -- so
        # without a floor the arrival would move everything below it by 12 px.
        # Two lines, because the ordinary note is one clause and at most one
        # optional clause (`UI_SPEC` T-141 §9 (e)); the two long endings, the
        # fall-back note and the failure sentence, may still be higher and are
        # exempted by AK-225 itself. Taken from the font rather than written
        # down as a figure, so it follows whoever changes the font.
        self.owned_label.setMinimumHeight(
            2 * QFontMetrics(self.owned_label.font()).lineSpacing())
        layout.addWidget(self.owned_label)

        layout.addSpacing(8)
        layout.addWidget(_heading("Level"))
        self.level_label = QLabel()
        self.level_label.setStyleSheet(
            f"color: {ACCENT}; font-size: 17px; font-weight: bold;"
        )
        layout.addWidget(self.level_label)
        self.level_slider = QSlider(Qt.Horizontal)
        self.level_slider.setMinimum(1)
        self.level_slider.setMaximum(15)
        self.level_slider.setTickPosition(QSlider.TicksBelow)
        self.level_slider.valueChanged.connect(lambda *_: self.recompute())
        layout.addWidget(self.level_slider)
        self.level_note = QLabel()
        self.level_note.setWordWrap(True)
        self.level_note.setStyleSheet(f"color: {MUTED}; font-size: 10px;")
        layout.addWidget(self.level_note)
        return panel

    def _build_middle(self) -> QWidget:
        # Three pieces stacked: what does not scroll, the advisor's row, and
        # the slots. The row has to sit under the "Build" line and stay put
        # while the slots scroll (`UI_SPEC` §3.1, AK-02) -- and a "Build"
        # line that slid away from above a pinned row would read as the
        # program having mislaid it, so everything above the row is pinned
        # with it.
        column = QWidget()
        stack = QVBoxLayout(column)
        stack.setContentsMargins(0, 0, 0, 0)
        stack.setSpacing(0)

        # `Ignored` horizontally, here and on the advisor row: inside a
        # scroll area a wide row costs the window nothing, and outside one it
        # costs the window's floor pixel for pixel. Measured 2026-09-07 in
        # this tree, UI scale Automatic: under the Windows platform the
        # window's minimum width (760) *is* the Build planner page (756), and
        # this block asks for 382 of its own. AK-03 says that floor may not
        # grow, so neither of the two asks for anything and both take the
        # width the column has.
        top = QWidget()
        top.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        layout = QVBoxLayout(top)
        layout.setContentsMargins(0, 0, 6, 0)

        # The heading and, opposite it, the way out of a build. Equipped
        # relics now survive a restart, so there has to be something that
        # clears them on purpose -- otherwise the only way back to an empty
        # vessel is to empty six slots by hand.
        header = QHBoxLayout()
        header.addWidget(_heading("Relic slots"))
        header.addStretch()
        self.reset_button = QPushButton("Reset Chalice")
        self.reset_button.setToolTip(
            "Empty every slot and forget this Nightfarer's saved build"
        )
        self.reset_button.clicked.connect(self.reset_chalice)
        header.addWidget(self.reset_button)
        layout.addLayout(header)

        # The vessel at a glance, above the six panels that edit it.
        self.vessel_strip = VesselStrip(self.icons)
        layout.addWidget(self.vessel_strip)

        # Saved builds. The scratchpad -- whatever is in the slots now -- is
        # still restored on launch; this is for keeping several worked-out
        # builds and flipping between them to compare.
        builds = QHBoxLayout()
        builds.setSpacing(6)
        builds.addWidget(QLabel("Build"))
        self.build_box = QComboBox()
        self.build_box.setMinimumWidth(180)
        self.build_box.activated.connect(self._on_build_chosen)
        builds.addWidget(self.build_box, 1)
        save_build = QPushButton("Save")
        save_build.setToolTip("Save the slots as they are under a name")
        save_build.clicked.connect(self._save_build)
        builds.addWidget(save_build)
        self.delete_build_button = QPushButton("Delete")
        self.delete_build_button.setToolTip("Forget the selected saved build")
        self.delete_build_button.clicked.connect(self._delete_build)
        builds.addWidget(self.delete_build_button)
        self.hide_build_button = QPushButton("Hide")
        self.hide_build_button.setToolTip(
            "Keep this build out of the list without deleting it — "
            "Show hidden lists it again")
        self.hide_build_button.clicked.connect(self._toggle_hidden_build)
        builds.addWidget(self.hide_build_button)
        # Hiding was one-way. The build left the list as soon as anything else
        # was selected and nothing anywhere offered it back, so the only route
        # a player found was to save a new build under the same name -- which
        # does bring the entry back, and overwrites everything that was in it.
        self.show_hidden_check = QCheckBox("Show hidden")
        self.show_hidden_check.setToolTip(
            "List the builds you have hidden, so one can be selected and "
            "unhidden")
        self.show_hidden_check.toggled.connect(
            lambda *_: self.refresh_build_list())
        builds.addWidget(self.show_hidden_check)
        layout.addLayout(builds)
        stack.addWidget(top)

        # The advisor's row, between the "Build" line and the hint and
        # outside the scroll area below: a run that is being waited for may
        # not scroll out of sight (§3.1). It is handed a way to ask the
        # window what it would be asked right now, and nothing else -- it
        # reads no widget of this window and writes to none.
        self.advisor_bar = AdvisorBar(
            lambda goal_id: asking_from(self, goal_id), column)
        stack.addWidget(self.advisor_bar)

        # The relic picker's track: the same class, a second instance, and
        # three figures of its own -- the pool rather than the whole answer,
        # no debounce and a cache twice the size (AD-028, Nachtrag IX-1.1 and
        # IX-3). It lives here and not in the dialog because the measured use
        # of the cache is across openings (30 % hits, S11-F) and a cache in a
        # dialog dies with it. Owned by the window so that it outlives every
        # picker and is shut down with the window.
        self.picker_advisor = AdvisorController(
            self, answer=advisor_run.slot_pool,
            cache=advisor_run.ResultCache(PICKER_CACHE_SIZE),
            debounce_ms=PICKER_DEBOUNCE_MS)

        outer = QScrollArea()
        outer.setWidgetResizable(True)
        outer.setFrameShape(QFrame.NoFrame)

        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 6, 0)

        # No search box here. A single filter across every slot narrowed each
        # slot's own list, so a relic already chosen could stop matching and be
        # dropped out from under you -- relics would not stay put. Filtering
        # belongs to the picker, where it narrows the grid you are choosing
        # from and cannot disturb what is already equipped. The picker keeps
        # its own box, and the term carries from one opening to the next.
        hint = QLabel("Open a slot to choose a relic — the picker has its own "
                      "filter, supporting AND, OR, NOT and \"quoted phrases\".")
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        layout.addWidget(hint)

        self.base_slots = [
            RelicSlot(i, False, self._relic_changed, self.icons,
                      self._set_search, self._relics_taken_elsewhere,
                      self._hold_changed)
            for i in range(3)
        ]
        for slot in self.base_slots:
            layout.addWidget(slot)

        self.deep_heading = _heading("Deep of Night slots")
        layout.addWidget(self.deep_heading)
        self.deep_slots = [
            RelicSlot(i, True, self._relic_changed, self.icons,
                      self._set_search, self._relics_taken_elsewhere,
                      self._hold_changed)
            for i in range(3)
        ]
        for slot in self.deep_slots:
            layout.addWidget(slot)

        layout.addStretch()
        outer.setWidget(panel)
        stack.addWidget(outer, 1)
        return column

    def _build_right(self) -> QWidget:
        # The whole sheet scrolls. With six relics equipped the conditional and
        # curse sections alone can outrun the window, and content was simply
        # falling off the bottom with no way to reach it.
        outer = QScrollArea()
        # 348 was tight before the situational switches and cramped after them:
        # a multiplier line such as "All damage +6.0% - melee armaments only"
        # had nowhere to go, and the count box sat past the right edge. 370 is
        # still what it opens at -- the splitter's initial sizes say so -- but
        # a player who wants the sheet wider may now have it, and one who
        # drags it narrow gets the wrapping rather than a cut-off column.
        outer.setMinimumWidth(340)
        outer.setWidgetResizable(True)
        outer.setFrameShape(QFrame.NoFrame)
        outer.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

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
                index, self._edit_weapon_slot, self._clear_weapon_slot,
                self._activate_weapon_slot,
            )
            self.weapon_tiles.append(tile)
            grid.addWidget(tile, index // weaponslots.SLOT_COLUMNS,
                           index % weaponslots.SLOT_COLUMNS)
        layout.addLayout(grid)
        self.apply_hero_weapon()

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
        outer.setWidget(panel)
        return outer

    # -- window chrome: opening size, pane widths, scale, Start Menu ------
    def showEvent(self, event) -> None:  # noqa: N802 - Qt naming
        """Size the window on the way to the screen, unless it was sized.

        Here and not in `__init__` for one reason: the width the window opens
        at depends on how much room the tab page has, and before the first
        layout pass there is no page -- every rectangle inside the window is
        a placeholder. Qt sends the show event *before* it maps the window,
        so a size set here is the first size that ever reaches the screen and
        there is nothing to see blink.

        `WA_Resized` is Qt's own record of whether anybody has asked for a
        size, and it is what makes this the *opening* size rather than an
        override: a caller that resized the window first keeps its width, and
        showing the window again later -- after a minimise, say -- finds the
        attribute set and leaves the player's own size alone.
        """
        if not self.testAttribute(Qt.WA_Resized):
            self.resize(self._opening_width(), OPENING_HEIGHT)
        super().showEvent(event)

    def the_advisor_data_is_changing(self) -> None:
        """Both advisor tracks, from one place (AD-028 point 6).

        Called before the save or the dataset is read again (AD-006.7). With
        two tracks a forgotten call is a cache that survives a rescan --
        answers worked out on relics the player no longer owns, handed back
        with no sign that anything is wrong -- so the distribution stands
        here once rather than beside every call site.
        """
        self.advisor_bar.the_data_is_changing()
        self.picker_advisor.before_the_data_changes()

    def shutdown_the_advisor(self) -> None:
        """Stop both tracks and wait for their threads. Closing only."""
        self.advisor_bar.shutdown()
        self.picker_advisor.shutdown()

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt naming
        """Stop every thread of this window and wait for it before it goes.

        The one place a `wait()` in the main thread is right (AD-006 point 4):
        a `QThread` that outlives the window it belongs to is destroyed while
        its run is still going, and that ends the process rather than the
        run.

        Three threads and not two now: the two advisor tracks and the reading
        of the save. All three raise their generation before they wait, so an
        answer already in the main thread's queue cannot be delivered into a
        window that is on its way out -- which is the defect T-137 measured on
        the advisor, and there is no reason it would behave differently here.
        """
        self.shutdown_the_advisor()
        self.save_reader.shutdown()
        super().closeEvent(event)

    def _opening_width(self, room: int | None = None) -> int:
        """Wide enough to read every column heading, and no wider.

        Four terms, in the order they bind:

        * what a window has to be for the effect table to get the viewport it
          asked for, worked out below;
        * what a window has to be for the advisor row to keep every action
          button once a suggestion puts them up, `_width_around_the_advisor_
          row` -- the wider of the two wins, since the window opens once and
          has to suit both;
        * `room`, the width the desktop has. On a machine that cannot show
          that much, the desktop wins: a window wider than the screen opens
          with its right-hand edge past the edge of it, which is worse than
          the shortened heading it was meant to avoid. It defaults to the
          screen this window is on, and is a parameter so a case can ask what
          the window would do on a desktop other than the one it runs on;
        * the window's own minimum. It is the last word because a window
          narrower than its layout allows is not a width the program can
          honour anyway.
        """
        if room is None:
            room = self.screen().availableGeometry().width()
        return max(self.minimumSizeHint().width(),
                   min(max(self._width_around_the_effect_table(),
                           self._width_around_the_advisor_row()), room))

    def _width_around_the_effect_table(self) -> int:
        """A window width that leaves the effect table the viewport it wants.

        **Every term but the first comes from a style or a layout, not from a
        laid-out rectangle**, and that is the whole of it: the tab in front
        when this is asked is the Build planner, so the effects tab has never
        been given the width of a page and every rectangle inside it is a
        placeholder. Measured on 2026-09-06 with the planner in front, on
        Windows under Fusion at 150 % scale: the table reports 640 px and its
        viewport 638, which reads as 2 px of chrome against the 16 it really
        has -- the scrollbar is not up yet. A window sized against that
        placeholder came out at 1 802 px and was cut to the screen's 1 707;
        with the effects tab in front the same code said 1 350. An opening
        size that depends on which tab happens to be in front is not an
        opening size.

        The one term that does come off the screen is the page inset, and it
        can: the tab in front is laid out by definition, and every page of a
        `QTabWidget` gets the same rectangle.
        """
        tabs = self.centralWidget()
        beside_the_page = self.width() - tabs.currentWidget().width()
        margins = self.effects_tab.layout().contentsMargins()
        table = self.effects_tab.table
        # The scrollbar's own width, whether or not it happens to be up.
        # 652 effects against a page holding some thirty rows: it is up. If a
        # later dataset ever fitted without one, the window would open those
        # px wider than it had to, which costs a reader nothing.
        bar = table.verticalScrollBar().sizeHint().width()
        return (table.width_for_full_headings()
                + 2 * table.frameWidth() + bar
                + margins.left() + margins.right()
                + beside_the_page)

    def _width_around_the_advisor_row(self) -> int:
        """A window width that leaves the advisor row every action button.

        Not `_width_around_the_effect_table`'s own trick of subtracting a
        current width: the advisor row lives inside the middle pane of
        `self.panes`, the one `QSplitter.setStretchFactor` gives every extra
        pixel of window to. Before the first layout pass -- which is exactly
        when `showEvent` first asks this -- that pane is squeezed well below
        its share, so `self.width() - self.advisor_bar.width()` would read a
        placeholder split, not the real one (measured: an offset of 836 px
        pre-layout against 852 px once the window has actually settled).

        What does not depend on that squeeze is the stretch factor itself:
        every pixel added to the window arrives at the middle pane, and so
        at the row. So this starts from `_width_around_the_effect_table`'s
        own result -- a width the window has already opened at for real,
        never a placeholder -- and adds exactly the extra the row needs,
        `AdvisorBar.action_buttons_extra_width`.
        """
        return (self._width_around_the_effect_table()
                + self.advisor_bar.action_buttons_extra_width())

    def _store_layout(self) -> None:
        """Remember how wide the player made each pane."""
        if hasattr(self, "panes"):
            QSettings(favourites.ORG, favourites.APP).setValue(
                PANES_KEY, self.panes.saveState())

    def _reset_layout(self) -> None:
        """The panes back to their opening widths, and the stored state gone.

        Both halves matter: setSizes alone would come back wrong on the next
        launch if the stored state is the broken thing being escaped from.
        """
        self.panes.setSizes(list(PANE_DEFAULTS))
        QSettings(favourites.ORG, favourites.APP).remove(PANES_KEY)

    def _choose_scale(self, _index: int) -> None:
        """Store the chosen scale, and offer the restart it needs to show.

        Qt reads the scale factor once, while the QApplication is being made,
        and gives nothing that changes it afterwards. So this cannot redraw
        what is already on screen. Saying that and offering the restart is
        the honest version of a control that would otherwise look broken.
        """
        chosen = self.scale_box.currentData()
        if chosen == uiscale.stored():
            return
        uiscale.set_stored(chosen)

        box = QMessageBox(self)
        box.setWindowTitle("Nightreign Helper")
        box.setIcon(QMessageBox.Question)
        box.setText(
            f"The interface is drawn at {self.scale_box.currentText()} from "
            f"the next launch."
        )
        # What a restart costs, in the player's terms. Relics, builds,
        # favourites and artwork are in the settings and come straight back;
        # the armament tiles and the switched-on conditions are session state
        # by design, and would start again from the Nightfarer's default.
        box.setInformativeText(
            "Your relics, saved builds and favourites are kept. The armament "
            "tiles and any conditions you have switched on last only for the "
            "run of the program, and would start again."
        )
        restart = box.addButton("Restart now", QMessageBox.AcceptRole)
        box.addButton("Later", QMessageBox.RejectRole)
        box.exec()
        if box.clickedButton() is restart:
            self._restart()

    def _restart(self) -> None:
        """Start this program again and leave.

        Frozen, the executable is its own launcher and takes no arguments of
        ours; from a checkout it is the interpreter that has to be started,
        with the script it was given. Nothing is written on the way out that
        is not written already -- every build is stored as it changes.
        """
        if getattr(sys, "frozen", False):
            arguments = []
        else:
            arguments = [os.path.abspath(sys.argv[0]), *sys.argv[1:]]
        if QProcess.startDetached(sys.executable, arguments):
            QApplication.quit()
            return
        QMessageBox.information(
            self, "Nightreign Helper",
            "This could not restart itself. Close it and open it again, and "
            "the new scale will be in place."
        )

    def _sync_shortcut_button(self) -> None:
        """Label the button for what it will do, not for what it is."""
        if not shortcut.available():
            self.shortcut_button.setVisible(False)
            return
        on = shortcut.exists()
        self.shortcut_button.setText(
            "  ✓ In Start Menu  " if on else "  ★ Add to Start Menu  "
        )
        self.shortcut_button.setToolTip(
            f"Remove {shortcut.SHORTCUT_NAME} from your Start Menu"
            if on else
            "Put a shortcut in your Start Menu so this can be launched by "
            "name. Your account only — no admin rights, nothing installed."
        )
        self.shortcut_button.setStyleSheet(
            f"QToolButton {{ color: {ACCENT if on else MUTED}; "
            f"font-size: 11px; border: none; padding: 2px 4px; }}"
            f"QToolButton:hover {{ color: {ACCENT}; }}"
        )

    def _toggle_shortcut(self) -> None:
        error = shortcut.remove() if shortcut.exists() else shortcut.create()
        self._sync_shortcut_button()
        if error:
            QMessageBox.warning(
                self, "Start Menu",
                f"The Start Menu entry could not be changed.\n\n{error}",
            )

    # -- logic -----------------------------------------------------------
    def current_hero(self) -> dict:
        return self.heroes[self.hero_index]

    def select_hero(self, index: int) -> None:
        self.hero_index = index
        for i, tile in enumerate(self.hero_tiles):
            tile.setChecked(i == index)
        self.hero_name_label.setText(self.heroes[index]["name"])
        self.apply_hero_weapon()
        self.reload_chalices()
        # Saved builds are per Nightfarer, so the list and the strip both
        # belong to whoever is selected.
        self.refresh_build_list(
            keep=chalices.selected_build(self.heroes[index]["id"]))
        self.refresh_vessel_strip()

    # -- armament tiles ---------------------------------------------------
    def weapon_by_id(self, weapon_id: int) -> dict | None:
        return next((w for w in self.data["weapons"] if w["id"] == weapon_id),
                    None)

    def active_slot(self) -> weaponslots.WeaponSlot:
        return self.weapon_slots[self.active_weapon]

    def equipped_weapons(self) -> list[dict]:
        return [s.weapon for s in self.weapon_slots if s.filled]

    def weapon_effects(self) -> list[dict]:
        """Rolled effects from every armament on the grid, not just the active
        one. A weapon's passive is not switched off by holding something else;
        the ones that genuinely need the weapon in hand carry their own gate
        and land under Conditional & situational."""
        out = []
        for slot in self.weapon_slots:
            for effect_id in slot.effect_ids:
                effect = self.effects.get(str(effect_id))
                if effect is not None:
                    out.append(effect)
        return out

    def _store_weapon_loadout(self) -> None:
        self.weapon_loadouts[self.current_hero()["id"]] = [
            s.copy() for s in self.weapon_slots
        ]

    def _activate_weapon_slot(self, index: int) -> None:
        self.active_weapon = index
        self.recompute()

    def _clear_weapon_slot(self, index: int) -> None:
        self.weapon_slots[index] = weaponslots.WeaponSlot()
        self._store_weapon_loadout()
        self.recompute()

    def _edit_weapon_slot(self, index: int) -> None:
        dialog = weaponslots.WeaponDialog(
            self, self.data, self.weapon_slots[index], self.icons)
        if dialog.exec():
            self.weapon_slots[index] = dialog.result_slot()
            self._store_weapon_loadout()
        self.recompute()

    def apply_hero_weapon(self) -> None:
        """Load this Nightfarer's tiles: what was built earlier this session,
        or slot 1 seeded with their own starting armament."""
        if not hasattr(self, "weapon_tiles"):
            return                      # called before the panel exists
        hero = self.current_hero()
        saved = self.weapon_loadouts.get(hero["id"])
        if saved is not None:
            self.weapon_slots = [s.copy() for s in saved]
        else:
            self.weapon_slots = [weaponslots.WeaponSlot()
                                 for _ in range(weaponslots.SLOT_COUNT)]
            starting = self.weapon_by_id(hero.get("starting_weapon", -1))
            if starting is not None:
                self.weapon_slots[0] = weaponslots.WeaponSlot(weapon=starting)
        self.active_weapon = 0

    ROW_SLOT = 22

    def _vessel_row_art(self, vessel: dict, items=None, worn: bool = False,
                        selected: bool = False):
        """A vessel's own icon followed by its slots, as one row image.

        Reading a vessel's colours off a letter code -- "R B Y" -- means
        translating in your head every time. Drawing the slots is what the
        game does, and the selected vessel shows what is actually sitting in
        them, which is the thing the list could never say before.

        `worn` marks the chalice the game has equipped, with a mark on the
        vessel rather than words after its name: the name is what the list is
        read for, and a label pushed the longer names out of sight.

        `selected` flips that mark dark. The row highlight is the same accent
        the mark was drawn in -- exactly, #c8a45c on both -- so on the row the
        player had open the mark was gold on gold and only its outline showed.
        That is the row it matters on most: the equipped chalice is the one
        open after an import and on a Nightfarer's first visit.
        """
        cell = self.chalice_list.iconSize().height()
        colours = list(vessel.get("slots", []))
        if self.deep_check.isChecked():
            colours += list(vessel.get("deep_slots") or [])
        gap = 5
        width = cell + gap + len(colours) * (self.ROW_SLOT + 2)
        art = QPixmap(width, cell)
        art.fill(Qt.transparent)
        painter = QPainter(art)
        base = self.icons.item(vessel.get("icon")) if self.icons else None
        if base is not None:
            base = base.scaled(cell, cell, Qt.KeepAspectRatio,
                               Qt.SmoothTransformation)
            painter.drawPixmap(0, (cell - base.height()) // 2, base)
        top = (cell - self.ROW_SLOT) // 2
        for i, colour in enumerate(colours):
            owned = items[i] if items and i < len(items) else None
            painter.drawPixmap(cell + gap + i * (self.ROW_SLOT + 2), top,
                               slot_chip(self.icons, colour, owned,
                                         self.ROW_SLOT))
        if worn:
            # Drawn rather than taken from the game: the menus mark the worn
            # chalice by moving it, not with a sprite this program could
            # borrow, so this mark is the planner's own.
            dot = 10
            painter.setRenderHint(QPainter.Antialiasing, True)
            fill, edge = ((QColor("#14150f"), QColor("#e6d3a3"))
                          if selected else (QColor(ACCENT), QColor("#14150f")))
            painter.setPen(QPen(edge, 1))
            painter.setBrush(fill)
            painter.drawEllipse(cell - dot - 1, 1, dot, dot)
        painter.end()
        return art

    def _relics_by_handle(self) -> dict:
        """Owned relics keyed by their save handle, for drawing rows."""
        if self.owned is None:
            return {}
        return {r.handle: r for r in self.owned.relics
                if getattr(r, "handle", None) is not None}

    def _stored_relics(self, hero_id: int, vessel_id: int, by_handle: dict):
        """What one chalice holds, read from its stored build.

        Rows other than the selected one have no live slots to read, so the
        stored build is the only account of what is in them.
        """
        _vessel, _deep, keys = chalices.load(hero_id, vessel_id)
        if not keys:
            return None
        out = []
        for key in (list(keys) + [""] * 6)[:6]:
            handle, _roll = chalices.split_key(key)
            out.append(by_handle.get(handle) if handle is not None else None)
        return out

    def _worn_vessel_id(self) -> int | None:
        """The chalice the game has equipped on this Nightfarer.

        Read from the save's own record -- the vessel id in the Nightfarer's
        loadout group header -- and not from which chalice holds relics: a
        Nightfarer can be wearing an empty one while built ones sit beside it.
        """
        if (getattr(self, "owned", None) is None
                or not getattr(self, "hero_vessels", None)):
            return None
        worn = self.owned.selected_loadout(self.current_hero()["id"])
        return worn.vessel_id if worn is not None else None

    def refresh_vessel_rows(self) -> None:
        """Redraw every vessel row, not only the selected one.

        The Deep of Night switch changes how many slots a chalice shows, and
        redrawing just the selected row left every chalice the player had not
        clicked on still drawing three -- so turning Deep on appeared to add
        slots to one chalice and not the rest. The relics come from each
        chalice's stored build, so a row says what is in it without being
        opened.
        """
        if not getattr(self, "hero_vessels", None):
            return
        hero_id = self.current_hero()["id"]
        by_handle = self._relics_by_handle()
        current = self.chalice_list.currentRow()
        for row in range(self.chalice_list.count()):
            item = self.chalice_list.item(row)
            vessel = item.data(Qt.UserRole)
            if not vessel:
                continue
            if row == current:
                items = [s.current_relic() for s in self._visible_slots()]
            else:
                items = self._stored_relics(hero_id, vessel["id"], by_handle)
            item.setIcon(QIcon(self._vessel_row_art(
                vessel, items, vessel["id"] == self._worn_vessel_id(),
                row == current)))

    def refresh_vessel_row(self) -> None:
        """Redraw the selected vessel's row so its slots show what is in them."""
        row = self.chalice_list.currentRow()
        item = self.chalice_list.item(row) if row >= 0 else None
        vessel = item.data(Qt.UserRole) if item is not None else None
        if not vessel:
            return
        slots = self._visible_slots()
        # The worn mark has to be passed here too. Without it this redraw --
        # which runs on every slot change -- quietly rubbed the mark off the
        # selected row, and the equipped chalice is the row most likely to be
        # selected, so the mark appeared to not work at all.
        item.setIcon(QIcon(self._vessel_row_art(
            vessel, [s.current_relic() for s in slots],
            vessel["id"] == self._worn_vessel_id(), True)))

    def reload_chalices(self) -> None:
        hero = self.current_hero()
        self.chalice_list.blockSignals(True)
        self.chalice_list.clear()
        # A Nightfarer's own vessels, then the four shared Grails. The Grails
        # belong to every Nightfarer, which the save confirms: each one stores
        # its own arrangement of all four.
        own = [v for v in self.vessels if v["hero_type"] == hero["id"]]
        grails = [v for v in self.vessels if v["hero_type"] == GRAIL_HERO_TYPE]
        self.hero_vessels = own + grails

        def add_separator(text: str) -> None:
            """A caption row. Selecting it would mean nothing, so it cannot be
            picked -- without it the four shared Grails read as four more of
            this Nightfarer's own vessels, and the list looks twice as long as
            the Nightfarer actually has."""
            item = QListWidgetItem(text)
            item.setFlags(Qt.NoItemFlags)
            item.setForeground(QColor(MUTED))
            self.chalice_list.addItem(item)

        worn_id = self._worn_vessel_id()
        first_row = None
        for group, vessels in ((f"{hero['name']}'s own", own),
                               ("Shared Grails — any Nightfarer", grails)):
            if not vessels:
                continue
            add_separator(group)
            for vessel in vessels:
                item = QListWidgetItem(vessel["name"])
                item.setData(Qt.UserRole, vessel)
                item.setIcon(QIcon(self._vessel_row_art(
                    vessel, None, vessel["id"] == worn_id)))
                slots = " ".join(
                    model.COLOUR_NAMES.get(c, "?")[0] for c in vessel["slots"]
                )
                tip = f"{vessel['name']} — slots {slots}"
                if vessel["id"] == worn_id:
                    # The mark is on the vessel, not after the name: the name
                    # is what the list is read for, and a label pushed the
                    # longer chalice names out of the panel.
                    tip += "\nEquipped in game"
                item.setToolTip(tip)
                self.chalice_list.addItem(item)
                if first_row is None:
                    first_row = self.chalice_list.count() - 1
        self.chalice_list.blockSignals(False)

        # The first time a Nightfarer is opened, their chalices are read out
        # of the save and the equipped one is the one shown. Until this ran on
        # its own, a Nightfarer nobody had pressed the button on showed eleven
        # empty chalices, and pressing it changed the whole list at once --
        # the same list, moments apart, telling two different stories.
        #
        # It happens once. From then on the chalice the player last had open
        # is what reopens, across sessions, because that choice is theirs;
        # Load equipped is how the save is asked again.
        #
        # Except where the player filled the slots themselves while the first
        # read was still out (AK-226). Their work is what is on screen, and
        # the save's build would be laid over it -- so it is marked as taken
        # over without being taken over, which is what stops it turning up at
        # the next change of Nightfarer instead.
        if (self.owned is not None
                and not chalices.imported(hero["id"])
                and self.owned.loadouts_for(hero["id"])):
            chalices.set_imported(hero["id"])
            if hero["id"] in self._own_slots_beat_the_stored_build:
                self._keep_the_slots_the_player_filled(first_row)
                return
            self.load_equipped()
            return

        # The build this Nightfarer was last left holding, if there is one.
        # Restored in the same order load_equipped uses -- vessel and mode
        # first, because both rebuild the slots and would otherwise empty them
        # again straight after they were filled.
        view_vessel, view_deep = chalices.view(hero["id"])
        vessel_id, deep_on, slot_keys = chalices.load(hero["id"], view_vessel)
        # The view wins for both: an empty chalice with Deep on stores no
        # build, and its choice would otherwise be lost on the next launch.
        if view_vessel is not None:
            vessel_id, deep_on = view_vessel, view_deep
        saved_row = None
        if vessel_id is not None:
            saved_row = next(
                (i for i in range(self.chalice_list.count())
                 if (self.chalice_list.item(i).data(Qt.UserRole) or {}).get("id")
                 == vessel_id),
                None,
            )

        self._restoring = True
        try:
            if saved_row is not None:
                self.chalice_list.setCurrentRow(saved_row)
            if saved_row is not None or view_vessel is not None:
                self.deep_check.blockSignals(True)
                self.deep_check.setChecked(bool(deep_on))
                self.deep_check.blockSignals(False)
            if saved_row is None and first_row is not None:
                self.chalice_list.setCurrentRow(first_row)
            self.apply_chalice()

            # Emptied first, every time. This whole block runs with the
            # restoring guard up, so apply_chalice does not set the slots
            # from the chalice -- and rebuilding a slot keeps the relic that
            # was in it when the colour still fits. Changing Nightfarer
            # therefore carried relics across, and the write that followed
            # stored them: a Nightfarer whose chalice is empty in the game
            # inherited whatever the Nightfarer before them had on.
            slots = list(self.base_slots) + list(self.deep_slots)
            for slot in slots:
                slot.clear_relic()

            if saved_row is not None and slot_keys:
                self._restore_slot_keys(slots, slot_keys)
            self._mark_vessel_applied()
        finally:
            self._restoring = False
        self._settle_slots()
        # Drawn once the Deep switch and the slots have settled, so every row
        # shows the right number of slots and what that chalice holds.
        self.refresh_vessel_rows()
        self.recompute()

    def _keep_the_slots_the_player_filled(self, first_row) -> None:
        """Put the vessel list back around the slots without touching them.

        The way out of `reload_chalices` for the one case AK-226 is about: the
        player put something in a slot while the first read was still out, so
        what is in the slots is theirs and neither the save's build nor a
        stored one goes over it. The list itself has just been rebuilt and has
        no current row, so the row of the vessel already applied is selected
        back -- with the list's signals held, because its handler is what
        would set the slots from a build.
        """
        row = next(
            (i for i in range(self.chalice_list.count())
             if (self.chalice_list.item(i).data(Qt.UserRole) or {}).get("id")
             == getattr(self, "_applied_vessel", None)),
            first_row,
        )
        if row is not None:
            self.chalice_list.blockSignals(True)
            self.chalice_list.setCurrentRow(row)
            self.chalice_list.blockSignals(False)
        # Written down under the vessel that is on screen, because nothing
        # else has: the list's own handler is what usually stores a build and
        # it was held above. Without this the slots the player filled would be
        # theirs until they changed Nightfarer and back, and the restore would
        # then find nothing stored and empty them -- which is the same loss by
        # a longer road (AK-226 asks for both).
        self._store_chalice()
        self._settle_slots()
        self.refresh_vessel_rows()
        self.recompute()

    def _restore_slot_keys(self, slots: list, keys: list[str]) -> None:
        """Put a stored build back into these slots, one physical relic each.

        In two passes over the whole build rather than slot by slot, because
        the question "which physical relic is this" has to be answered the
        same way everywhere it is asked (QA-016, QA-021):

        1. the copies each slot names by handle, and the custom relics, which
           are rebuilt from what the build wrote down because nothing owns
           them and no list can offer them until they exist again (QA-025);
        2. the rolls, which are what is left when the save has been rewritten
           and the handles renumbered -- each answered with a copy no slot of
           this build has already been given.

        Slot order used to decide the second pass, which is not a rule but an
        accident of iteration: the earlier slot took the only copy the list
        offered and the later one was told the relic was already worn.

        A slot whose stored relic cannot be placed is emptied here, and that is
        why nothing is returned: three callers each had to be told the same
        thing and one of them was not listening, which is how a slot came to
        keep the relic of the chalice being left (QA-014). The rule is carried
        out where it is decided instead of being handed out as an answer.
        """
        claimed = set()
        rolls = []
        for index, slot in enumerate(slots):
            key = keys[index] if index < len(keys) else ""
            if not key:
                slot.clear_relic()
                continue
            handle, roll = chalices.split_key(key)
            custom = _custom_effects(roll)
            if custom is not None:
                if not slot.adopt_custom(custom):
                    slot.clear_relic()
                continue
            if handle is not None and slot.select_copy(handle):
                claimed.add(inventory.copy_key(slot.current_relic()))
                continue
            rolls.append((slot, roll))

        for slot, roll in rolls:
            if roll and slot.select_roll(roll, claimed):
                claimed.add(inventory.copy_key(slot.current_relic()))
                continue
            # The stored relic is not one this slot can be given -- melted
            # since, or belonging to another save. Whatever the slot holds
            # belongs to the chalice being left, so it goes: keeping it would
            # make that relic part of this chalice's build at the next store.
            slot.clear_relic()

    def _store_chalice(self) -> None:
        """Write down what this Nightfarer is holding, for the next session."""
        self.refresh_vessel_strip()
        # Never mid-apply: see apply_chalice. The slots and the chosen vessel
        # disagree until the apply finishes, and apply_chalice stores itself
        # once it has.
        if getattr(self, "_applying", False):
            return
        if self._restoring or not getattr(self, "hero_vessels", None):
            return
        vessel = self.current_vessel()
        slots = list(self.base_slots) + list(self.deep_slots)
        keys = [slot.saved_key() for slot in slots]
        # The default vessel with nothing in it is not a build worth keeping.
        # Storing it anyway is what made Reset Chalice look as though it had
        # not worked: the reset emptied everything and the write that followed
        # put the starting state straight back as a saved one.
        # The view is always recorded: which chalice is open and whether Deep
        # of Night is on survive even an empty vessel, because they are what
        # the player was looking at rather than what they had equipped.
        chalices.save_view(self.current_hero()["id"],
                           vessel["id"] if vessel else None,
                           self.deep_check.isChecked())
        # The build itself is not. An empty set of slots is never written
        # over a stored one -- Reset Chalice is how a build is forgotten,
        # deliberately and per vessel.
        if not any(keys):
            return
        # Nor is a build the restore had to resolve. It names one physical
        # relic in two slots; which slot keeps it is the player's to decide,
        # and writing the resolution down decided it for them, irreversibly
        # and without a word once the note had gone. So the stored build is
        # left as it was until the player changes something themselves, and
        # the note comes back with it every time (director, 2026-09-02).
        if getattr(self, "_unresolved_clash", False):
            return
        chalices.save(
            self.current_hero()["id"],
            vessel["id"] if vessel else None,
            self.deep_check.isChecked(),
            keys,
        )

    # -- saved builds ----------------------------------------------------

    def _visible_slots(self) -> list:
        """The slot panels the current vessel actually exposes."""
        slots = list(self.base_slots)
        if self.deep_check.isChecked():
            slots += list(self.deep_slots)
        return slots

    def refresh_vessel_strip(self) -> None:
        """Redraw the small slot row from the vessel and what is in it."""
        if not hasattr(self, "vessel_strip"):
            return
        slots = self._visible_slots()
        self.vessel_strip.show_slots([s.colour for s in slots],
                                     [s.current_relic() for s in slots])
        self.refresh_vessel_row()

    def refresh_build_list(self, keep: str | None = None) -> None:
        """Rebuild the build picker for the current Nightfarer.

        The equipped build is always offered first and is never stored here:
        it is read from the save, so it cannot go stale. Hidden builds drop
        out of the list but keep their entry, which is what "hidden, not
        deleted" has to mean.
        """
        if not hasattr(self, "build_box"):
            return
        hero_id = self.current_hero()["id"]
        hidden = chalices.hidden_builds(hero_id)
        names = ([chalices.EQUIPPED_NAME, chalices.UNSAVED_NAME]
                 + chalices.build_names(hero_id))
        if keep is None:
            # No explicit target means "whatever was selected", and on the
            # first build of the list that is what the last session left.
            keep = self.build_box.currentData() or chalices.selected_build(
                hero_id)
        # A hidden build is listed while the player asks for it, and while it
        # is the one selected. Without the first of those, hiding was a thing
        # that could not be undone.
        show_hidden = getattr(self, "show_hidden_check", None)
        showing = show_hidden is not None and show_hidden.isChecked()

        self.build_box.blockSignals(True)
        self.build_box.clear()
        for name in names:
            if name in hidden and name != keep and not showing:
                continue
            label = f"{name}  (hidden)" if name in hidden else name
            self.build_box.addItem(label, name)
        index = self.build_box.findData(keep)
        self.build_box.setCurrentIndex(index if index >= 0 else 0)
        self.build_box.blockSignals(False)
        self._sync_build_buttons()

    def _sync_build_buttons(self) -> None:
        name = self.build_box.currentData()
        # The equipped build belongs to the save, not to this program: it can
        # be looked at and hidden, never deleted or written over. The unsaved
        # entry is not a build at all -- it is the list's way of saying the
        # slots are nobody's saved work -- so there is nothing to delete and
        # nothing to hide.
        unsaved = name == chalices.UNSAVED_NAME
        self.delete_build_button.setEnabled(
            bool(name) and name not in chalices.RESERVED_NAMES)
        hidden = name in chalices.hidden_builds(self.current_hero()["id"])
        self.hide_build_button.setText("Unhide" if hidden else "Hide")
        self.hide_build_button.setEnabled(bool(name) and not unsaved)

    def _on_build_chosen(self, _index: int) -> None:
        name = self.build_box.currentData()
        if not name:
            return
        chalices.set_selected_build(self.current_hero()["id"], name)
        self._sync_build_buttons()
        if name == chalices.UNSAVED_NAME:
            # A label, not a build. Picking it says "these slots are not one
            # of my saved builds" and changes nothing on screen: emptying them
            # is Reset Chalice's job, and doing it from a name in a list would
            # throw away work nobody asked to lose.
            return
        if name == chalices.EQUIPPED_NAME:
            self.load_equipped()
            return
        hero_id = self.current_hero()["id"]
        vessel_id, deep, keys = chalices.load_build(hero_id, name)
        self._apply_stored_build(vessel_id, deep, keys)

    def _apply_stored_build(self, vessel_id, deep, keys) -> None:
        """Put a stored build into the slots, the way a restore does."""
        self._restoring = True
        try:
            self.deep_check.blockSignals(True)
            self.deep_check.setChecked(bool(deep))
            self.deep_check.blockSignals(False)
            if vessel_id is not None:
                for i in range(self.chalice_list.count()):
                    entry = self.chalice_list.item(i).data(Qt.UserRole)
                    if entry is not None and entry["id"] == vessel_id:
                        self.chalice_list.setCurrentRow(i)
                        break
            self.apply_chalice()
            # A saved build can name a relic that has since been melted. The
            # slot it was stored for is empty then, not left holding whatever
            # the build before it had there.
            self._restore_slot_keys(
                list(self.base_slots) + list(self.deep_slots), keys)
            self._mark_vessel_applied()
        finally:
            self._restoring = False
        self._settle_slots()
        self.recompute()
        self._store_chalice()

    def _save_build(self) -> None:
        suggested = self.build_box.currentData() or ""
        if suggested in chalices.RESERVED_NAMES:
            suggested = ""
        name, ok = QInputDialog.getText(
            self, "Save build", "Name this build:", text=suggested)
        name = (name or "").strip()
        if not ok or not name:
            return
        if name in chalices.RESERVED_NAMES:
            QToolTip.showText(
                QCursor.pos(),
                "That name belongs to the build your save has equipped."
                if name == chalices.EQUIPPED_NAME else
                "That name means the slots hold no saved build.")
            return
        if not chalices.name_fits_the_store(name):
            # Said here rather than swallowed below: the store cannot write a
            # name this long, and a name that looks short can still be too
            # long, so the player has no way of guessing why the build never
            # appeared (QA-035).
            QToolTip.showText(
                QCursor.pos(),
                "That name is too long to save. Symbols and emoji take up "
                "several characters each, so try a shorter name.")
            return
        vessel = self.current_vessel()
        slots = list(self.base_slots) + list(self.deep_slots)
        chalices.save_build(
            self.current_hero()["id"], name,
            vessel["id"] if vessel else None,
            self.deep_check.isChecked(),
            [slot.saved_key() for slot in slots],
        )
        chalices.set_selected_build(self.current_hero()["id"], name)
        self.refresh_build_list(keep=name)

    def _delete_build(self) -> None:
        name = self.build_box.currentData()
        if not name or name == chalices.EQUIPPED_NAME:
            return
        chalices.delete_build(self.current_hero()["id"], name)
        chalices.set_selected_build(self.current_hero()["id"],
                                    chalices.EQUIPPED_NAME)
        self.refresh_build_list(keep=chalices.EQUIPPED_NAME)

    def _toggle_hidden_build(self) -> None:
        name = self.build_box.currentData()
        if not name:
            return
        hero_id = self.current_hero()["id"]
        hidden = name in chalices.hidden_builds(hero_id)
        chalices.set_hidden(hero_id, name, not hidden)
        if not hidden:
            # Said at the moment of hiding, because that is the moment the
            # player has to learn there is a way back. Finding out afterwards
            # meant not finding out at all.
            QToolTip.showText(
                QCursor.pos(),
                'Hidden. Tick "Show hidden" to list it again.')
        # Hiding the one on screen leaves it selected until something else is
        # chosen -- dropping it out from under the player would look like the
        # build had been deleted, which is the one thing Hide must not do.
        self.refresh_build_list(keep=name)

    def reset_chalice(self) -> None:
        """Empty this vessel and forget the build stored for it.

        Scoped to the vessel on screen now that each keeps its own build --
        clearing every vessel's work from one button would be a far bigger
        thing than the label promises.
        """
        vessel = self.current_vessel()
        chalices.clear(self.current_hero()["id"],
                       vessel["id"] if vessel else None)
        self._restoring = True
        try:
            self.deep_check.blockSignals(True)
            self.deep_check.setChecked(False)
            self.deep_check.blockSignals(False)
            # Row 0 is the group caption, which cannot be selected; the first
            # real vessel is whatever follows it.
            for i in range(self.chalice_list.count()):
                if self.chalice_list.item(i).data(Qt.UserRole) is not None:
                    self.chalice_list.setCurrentRow(i)
                    break
            self.apply_chalice()
            for slot in list(self.base_slots) + list(self.deep_slots):
                slot.clear_relic()
            self._mark_vessel_applied()
        finally:
            self._restoring = False
        # The lists were drawn up while the slots still held the build that
        # has just been thrown away, so they are missing every relic that was
        # in it. Nothing else here can put them right: the next rebuild only
        # happens when a relic changes, and there is nothing left to change.
        self._settle_slots()
        self.recompute()
        # The picker went on naming the build that was loaded before the
        # reset. An emptied chalice still read as "Test", clicking that entry
        # put it back, and the reset looked as though it had half worked --
        # so the list now has an entry for exactly this state, and lands on
        # it.
        chalices.set_selected_build(self.current_hero()["id"],
                                    chalices.UNSAVED_NAME)
        self.refresh_build_list(keep=chalices.UNSAVED_NAME)

    def current_vessel(self) -> dict | None:
        """The vessel selected in the list, ignoring the caption rows."""
        item = self.chalice_list.currentItem()
        vessel = item.data(Qt.UserRole) if item is not None else None
        if vessel is None:
            vessel = self.hero_vessels[0] if self.hero_vessels else None
        return vessel

    def _on_deep_toggled(self, *_args) -> None:
        """The Deep switch changes every chalice, so every row is redrawn."""
        self.apply_chalice()
        self.refresh_vessel_rows()

    def apply_chalice(self) -> None:
        if not self.hero_vessels:
            return
        # This is not re-entrant. It rebuilds the slots, and rebuilding a slot
        # can put a relic in it, which is a change like any other and comes
        # back round here. Nesting is never useful -- the outer call finishes
        # by drawing and recomputing anyway -- and left unguarded the nesting
        # grew until the program died of a stack overflow while stepping
        # through one Nightfarer's chalices in order.
        if getattr(self, "_applying", False):
            return
        # Whatever this call changes -- vessel, Deep of Night, slot colours --
        # the strip is drawn from it, so it is refreshed at the end below.
        vessel = self.current_vessel()
        if vessel is None:
            return
        deep_on = self.deep_check.isChecked()
        self._applying = True
        try:
            self._apply_chalice(vessel, deep_on)
        finally:
            self._applying = False
        # Only now, with the slots holding this chalice and nothing of the
        # one before it. Rebuilding a slot can emit, and a store that ran
        # part-way through wrote the old chalice's relics under the new
        # chalice's name: the vessel id had already changed while the slots
        # had not caught up. That is how a chalice empty in the game ended up
        # owning a relic nobody put there.
        self._store_chalice()
        # The whole list, because selection moved: the row being left has to
        # lose the light mark and the row arrived at has to gain it, and only
        # one of the two is the current row. Chip drawing is cached, so this
        # costs little and only runs when the chalice or the mode changes.
        self.refresh_vessel_rows()

    def _apply_chalice(self, vessel: dict, deep_on: bool) -> None:
        """The body of apply_chalice, held apart so it cannot nest."""

        owned = self.owned
        # Whether this is a different chalice from the one the slots are
        # holding, asked before anything is touched: both the emptying just
        # below and the restore at the end turn on the answer.
        changed = getattr(self, "_applied_vessel", None) != vessel["id"]
        # On a change of chalice the slots still hold the one being left, and
        # they are emptied before the lists are rebuilt rather than after. A
        # list drawn up around relics that are on their way out treats them as
        # taken, and the incoming chalice's own build could then not be put
        # back: its relic was "already worn" by the chalice it was replacing
        # (QA-014).
        if changed and not self._restoring:
            for slot in self.base_slots + self.deep_slots:
                slot.clear_relic()
        # Slots always list everything they can hold. Narrowing them from
        # outside is what made an equipped relic disappear.
        for i, slot in enumerate(self.base_slots):
            slot.set_colour(vessel["slots"][i], self.effect_list, owned,
                            hero_name=self.current_hero()["name"])
        for i, slot in enumerate(self.deep_slots):
            slot.set_colour(vessel["deep_slots"][i], self.effect_list, owned,
                            hero_name=self.current_hero()["name"])
            slot.setVisible(deep_on)
        self.deep_heading.setVisible(deep_on)

        # set_colour above does NOT empty the slots. It repopulates them and
        # deliberately keeps the relic that was in one if that relic still
        # fits -- which is what the Deep switch needs, and is wrong the
        # moment the chalice itself changes. Every slot the new
        # chalice happens to share a colour with the old one kept the old
        # relic, and the write that followed stored it: opening a Grail whose
        # slots are all Yellow inherited the Yellow relic from the chalice
        # before it, and the Grail then owned a relic nobody put there.
        #
        # So on a change of chalice the slots are set from that chalice's own
        # stored build and from nothing else, empty included.
        #
        # The note of which chalice was last applied is only made when the
        # slots were actually set from it. Marking it regardless meant a pass
        # that skipped the restore still claimed the chalice as applied, so
        # the next pass saw no change and never cleared -- one relic from the
        # chalice before survived, and was stored.
        if not self._restoring:
            self._applied_vessel = vessel["id"]
            self._restore_vessel_build(vessel, clear=changed)

        self.refresh_vessel_strip()
        self.recompute()

    def _restore_vessel_build(self, vessel: dict, clear: bool = False) -> None:
        """Put back whatever this vessel was last holding.

        With `clear`, a vessel that has no stored build has its slots emptied
        rather than left alone -- the chalice has just changed, and whatever
        is in the slots belongs to the chalice being left.
        """
        _stored_id, deep, keys = chalices.load(
            self.current_hero()["id"], vessel["id"])
        if not any(keys) and not clear:
            return
        self._restoring = True
        try:
            # The Deep of Night switch is left exactly as the player set it.
            # Restoring the stored flag here fought the switch: turning Deep
            # off reloaded a build that had it on and turned it straight back.
            #
            # Every slot is filled regardless, the hidden Deep ones included,
            # so toggling the switch reveals the full array instead of an
            # empty half. Only the visible ones reach the totals --
            # selected_effects() reads active_slots().
            self._restore_slot_keys(
                list(self.base_slots) + list(self.deep_slots), keys)
        finally:
            self._restoring = False
        self._settle_slots()

    def _settle_slots(self) -> int:
        """Bring the slots into agreement, once a restore has filled them.

        Two things are settled here, and both come of a board being written to
        while it was being read.

        A build stored before ownership was enforced can name one physical
        relic in two slots. Restored as written, both slots showed it and both
        were counted (measured: Endurance 5 where the relic gives 4), and the
        doubling was then resolved by the *next* change to any slot -- which
        emptied the lower-numbered of the two, elsewhere on the screen, with
        nothing said anywhere (QA-015, DR-002). It is resolved here instead:
        at the restore, once, and the slot that loses the relic says why.

        Then every list is rebuilt, because they were drawn up before the
        slots were set and each was written down against a board that no
        longer exists.

        Returns how many slots had to give a relic up, which is the one thing
        about a restore that only this function knows: the stored build is
        left exactly as it was, so nothing downstream could work it out again.
        """
        worn_in: dict = {}
        resolved = 0
        for slot in self.base_slots + self.deep_slots:
            # An empty slot and a custom relic both answer None: the one has
            # nothing to clash with, the other is imaginary by design and may
            # be planned into every slot.
            key = inventory.copy_key(slot.current_relic())
            if key is None:
                continue
            keeper = worn_in.setdefault(key, slot)
            if keeper is not slot:
                resolved += 1
                # The reason is about the keeper, so it is kept with the
                # condition it describes: the moment that slot gives the relic
                # up, this one has nothing to explain any more (QA-022).
                slot.clear_relic(
                    f"Already worn in {keeper.slot_name()} — "
                    "pick another relic for this slot.",
                    while_true=lambda held=key, by=keeper: (
                        inventory.copy_key(by.current_relic()) == held),
                )
        for slot in self.base_slots + self.deep_slots:
            slot.populate()
        # Until the player resolves it themselves. Writing the resolution into
        # the stored build made it permanent and, one click later, unexplained
        # -- the note is gone by then and nothing records that a slot was
        # emptied (director, 2026-09-02).
        self._unresolved_clash = bool(resolved)
        return resolved

    def _mark_vessel_applied(self) -> None:
        """Note the chalice the slots now hold, after a restore has set them.

        `_apply_chalice` makes this note only when it set the slots itself,
        which it does not do while a restore is in progress -- and every
        restoring path sets them afterwards from its own authority: the save,
        a stored build, or an emptying. Leaving the note alone through all of
        that left it naming the chalice the player was on *before*, and one
        click later that was read as "the chalice has not changed": the slots
        were left exactly as they were, and Load equipped's relics were stored
        under a chalice that is empty in the game.

        The mirror of this was a real bug too, which is why the note is not
        simply made every time: a pass that changes the chalice and does
        *not* set the slots must not claim it, or the next pass sees no change
        and never clears.
        """
        vessel = self.current_vessel()
        self._applied_vessel = vessel["id"] if vessel else None

    def show_variant_strip(self, tile) -> None:
        """Inline artwork chooser for one Nightfarer, inside the sidebar."""
        while self.variant_row.count():
            item = self.variant_row.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
                item.widget().deleteLater()

        choices = [(None, self.icons.portrait(tile.hero["id"]))]
        choices += [(v["id"], self.icons.variant(v["id"]))
                    for v in self.icons.variants(tile.hero["id"])]
        choices = [(tid, pix) for tid, pix in choices if pix is not None]

        if not choices:
            self.variant_title.setText(f"{tile.hero['name']} — no artwork")
            self.variant_panel.setVisible(True)
            return

        self.variant_title.setText(f"{tile.hero['name']} — pick artwork")
        # How many fit across the panel at full size, never fewer than one.
        available = max(self.variant_panel.width() - 16, VARIANT_STRIP + 4)
        per_row = max(1, available // (VARIANT_STRIP + 4 + 4))
        for index, (texture_id, pixmap) in enumerate(choices):
            button = QToolButton()
            button.setIconSize(QSize(VARIANT_STRIP, VARIANT_STRIP))
            button.setFixedSize(VARIANT_STRIP + 4, VARIANT_STRIP + 4)
            button.setCheckable(True)
            button.setChecked(texture_id == tile.variant_id)
            button.setIcon(QIcon(pixmap))
            button.setStyleSheet(
                f"QToolButton {{ border: 1px solid {BORDER}; border-radius: 3px; }}"
                f"QToolButton:checked {{ border: 2px solid {ACCENT}; }}"
            )
            button.clicked.connect(
                lambda _c=False, t=tile, tid=texture_id: self._apply_variant(t, tid)
            )
            self.variant_row.addWidget(button, index // per_row, index % per_row)
        self.variant_row.setColumnStretch(per_row, 1)
        self.variant_panel.setVisible(True)

    def _apply_variant(self, tile, texture_id) -> None:
        tile.set_variant(texture_id)
        self.variant_panel.setVisible(False)

    def _set_search(self, text: str) -> None:
        """Remember the picker's filter so the next slot opens with it.

        Deliberately does not re-filter the slots themselves -- that is what
        used to drop an equipped relic when it stopped matching.
        """
        self.last_search = text
        for slot in self.base_slots + self.deep_slots:
            slot.search_text = text

    def _relics_taken_elsewhere(self, asking: RelicSlot) -> set:
        """The physical relics the other slots are already holding.

        Asked by a slot while it works out what it can offer. The asking slot
        is skipped, or a slot would hide the very relic sitting in it.

        Every slot is considered, the hidden Deep ones included: they hold
        Deep relics, which no ordinary slot can take anyway, so the two
        never contend -- and a Deep slot that is out of sight still has a
        relic in it, which is exactly the case where a doubled relic would go
        unnoticed.

        Not while a restore is running. The slots are then half the build
        being left and half the one arriving, and an answer drawn from that
        mixture withheld from the incoming build exactly the relics it was
        about to be given (QA-014). The board is settled once, at the end of
        the restore, by _settle_slots.
        """
        if self._restoring:
            return set()
        taken = set()
        for slot in self.base_slots + self.deep_slots:
            if slot is asking:
                continue
            key = inventory.copy_key(slot.current_relic())
            if key is not None:
                taken.add(key)
        return taken

    def _relic_changed(self) -> None:
        """A relic moved, so both the totals and the other slots' lists change.

        The lists have to be rebuilt here and not only when the chalice
        changes: what a slot may offer depends on what the other five are
        holding at this moment, and a list built before the choice was made
        would still be offering the relic that has just been taken.

        The rebuild is about ownership and nothing else. It used to hand each
        slot the term last typed into the picker, which had nothing to do with
        the question being asked and everything to do with QA-013.

        This is also the moment a build the restore had to resolve becomes the
        player's own again: they have just moved a relic, so what the slots
        hold is theirs and is written down from here on.

        That is also what makes this the place to note a slot set while the
        first read is still out (AK-226). What arrives afterwards must not be
        laid over it -- neither at the arrival nor at the next change of
        Nightfarer, which is where a skipped import would otherwise turn up
        unannounced.
        """
        if self.save_reader.is_reading() and self.owned is None:
            self._own_slots_beat_the_stored_build.add(self.current_hero()["id"])
        self._unresolved_clash = False
        for slot in self.base_slots + self.deep_slots:
            slot.populate()
        self.recompute()

    # Populated by recompute(), read by the click-to-break-down popup.
    last_sources: dict = {}
    last_rates: dict = {}

    def _show_breakdown(self, key: str) -> None:
        """Which buffs make up one figure, shown beside the number clicked.

        A single "+12.4%" hides how many relics contributed and how much each
        one gave, which is exactly what you need when deciding whether one is
        worth a slot.
        """
        if key == AR_BREAKDOWN_KEY:
            self._show_ar_breakdown()
            return

        # An "All damage" row stands for five fields; its sources live under
        # the real one behind it.
        entries = self.last_sources.get(model.real_field(key), [])
        label = model.label_for(key)
        if not entries:
            QToolTip.showText(QCursor.pos(),
                              f"{label}\nno contributing effects recorded")
            return

        multiplicative = model.real_field(key) in self.last_rates
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

        # Offset to the right of the cursor so the number stays readable.
        QToolTip.showText(QCursor.pos() + QPoint(18, 0), "<br>".join(rows))

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
        # What the three figures are, named by the facade: for a staff or a
        # seal they are a spell scaling, and heading them "Attack rating"
        # would be the right numbers under the wrong name (QA-099).
        rows = [f"<b>{ar['headline']} — {ar['weapon']}</b>",
                f"&nbsp;&nbsp;Base &nbsp; "
                f"<b>{damage.displayed(base)}</b>"]

        from_attributes = scaled - base
        if abs(from_attributes) >= VISIBLE_CHANGE:
            rows.append(f"&nbsp;&nbsp;From attributes &nbsp; "
                        f"<b>{from_attributes:+.0f}</b>")

        weapon_class = ar.get("class")
        for field_name, value in ar["rates"].items():
            rows.append(f"&nbsp;&nbsp;{model.label_for(field_name)} &nbsp; "
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

        if not ar["rates"] and abs(from_attributes) < VISIBLE_CHANGE:
            rows.append("&nbsp;&nbsp;<i>nothing equipped moves this weapon</i>")

        delta = final - base
        pct = (delta / base * 100) if base else 0.0
        rows.append(f"&nbsp;&nbsp;<b>Total {damage.displayed(final)}</b> "
                    f"({delta:+.0f}{f', {pct:+.1f}%' if base else ''})")
        return "<br>".join(rows)

    def _show_ar_breakdown(self) -> None:
        """The breakdown, beside the figure that was clicked."""
        # Offset to the right of the cursor so the number stays readable --
        # but only where there is a figure to keep clear. The "no weapon"
        # notice has none, and sat under the cursor before this split did.
        beside = QPoint(18, 0) if getattr(self, "last_ar", None) else QPoint()
        QToolTip.showText(QCursor.pos() + beside, self._ar_breakdown_text())

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
        hero = self.current_hero()
        answers: dict[int, tuple] = {}
        for index, slot in enumerate(self.weapon_slots):
            equipped = None
            if slot.filled:
                answers[index] = damage.equipped(slot, index, build, hero,
                                                 self.data)
                equipped = answers[index][1]
            self.weapon_tiles[index].show_slot(
                slot, equipped, active=index == self.active_weapon,
                effects=self.data["effects"])

        slot = self.active_slot()
        if not slot.filled:
            self.last_ar = {}
            self.ar_label.setText(
                f"<span style='color:{MUTED}'>Slot "
                f"{self.active_weapon + 1} is empty — double-click a tile to "
                f"choose an armament, single-click one to break it down here."
                f"</span>")
            return
        weapon = slot.weapon

        # The figure itself is not computed here. It is the one piece of
        # domain arithmetic that had ended up inside the window, and the build
        # advisor needs to ask for it without drawing anything, so it lives in
        # nrplanner/damage.py and this method formats what comes back. The
        # tile above this panel was rated in the same call.
        bare, now = answers[self.active_weapon]
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
            rows.append(
                f"<div>{weapons.DAMAGE_LABELS[damage_type]} "
                f"<span style='color:{MUTED}'>{damage.displayed(was)}</span> "
                f"<span style='color:{colour}'>{change}</span> "
                f"<b>{damage.displayed(value)}</b></div>"
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
            f"{damage.displayed(base_total)}</span> "
            f"<a href='{AR_BREAKDOWN_KEY}' style='color:{colour};"
            f"text-decoration:none'>{change}</a> "
            f"<b style='color:{ACCENT}'>"
            f"{damage.displayed(final_total)}</b>"
            + (f" <span style='color:{colour}'>({pct:+.1f}%)</span>"
               if abs(pct) >= VISIBLE_PERCENT else "") +
            "</div>"
        )

        # Status the armament applies on a landed hit. This belongs with the
        # weapon rather than in the relic list: "Starting armament inflicts
        # frost" is the reason the attack rating above is 15% lower **on slot
        # 1**, and the buildup is what you are buying with it.
        #
        # Only statuses your attacks apply are shown. The ones that build up on
        # you -- "Taking Damage Causes Poison Buildup" and the like -- reach the
        # player, not the enemy, and would read as a weapon property here.
        on_hit: dict[str, list[tuple[str, float]]] = {}
        for eff in self.selected_effects():
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
                f"<div style='margin-top:6px'>Inflicts {status} "
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

    def rescan_save(self, initial: bool = False) -> None:
        """Ask for the save to be read, in the background, and say so.

        The reading itself is 657,2 ms of the main thread on the player's own
        save (S11-E, T-140), which is over the 250 ms AK-09 allows a window to
        be gone for, so it happens in a thread (AD-029 stage B). What this
        method does is start it and put the window into the state that says
        so; what comes back arrives at `_on_save_read`.

        **Nothing is invalidated here.** While the read is out, everything on
        screen is still true -- the relics, the slots and every answer the
        advisor has given about them -- and it stays true until the moment
        `self.owned` is replaced. That is AD-029 point 3, and it is the whole
        difference from the synchronous version, which had to throw the
        advisor's caches away before it began because the replacement followed
        immediately.

        A press while a read is out starts nothing and changes nothing on
        screen (AK-227): the line under the button already says what is
        happening.

        Which file is read is the resolution point's answer and no longer
        this method's (AD-030): the file the player picked while it is there,
        and otherwise -- silently, and without the picked one being forgotten
        -- whatever the automatic route finds (AK-125).
        """
        if not self.save_reader.start(self.data, gamepath.resolve_save()):
            return
        self._answers_a_chosen_save = False
        self._show_the_save_is_being_read(initial)

    def find_my_save(self) -> None:
        """Let the player say where his save is, keep it, and read it.

        A15 through AK-123 to AK-125. Three steps and nothing else: the
        system's file dialog, the path into `paths/save`, a read of that file.

        **The write is the confirmation and nothing else is** (AD-030): this
        is the only place in the program that writes that key, a cancelled
        dialog writes nothing, and no automatic find ever gets here. It
        happens before the read rather than after it, for the reason AK-117
        gives for the game folder: a crash during the read must not cost him
        the answer he has just given.

        Nothing is written back if the file turns out to be unreadable
        either. It is the file he pointed at; the line says what came of it
        (S3, S4), the button is still there, and he can point at another one.
        A single failure deletes nothing (AK-121).

        While a read is out this button does nothing at all, exactly as
        `Load equipped` does: the answer that is coming is about the file
        that was named before it.
        """
        if self.save_reader.is_reading():
            return
        chosen = _pick_a_save_file(self)
        if chosen is None:
            return
        if not self.save_reader.start(self.data, chosen):
            return
        gamepath.remember_save(chosen)
        self._answers_a_chosen_save = True
        self._show_the_save_is_being_read(False)

    def _show_the_save_is_being_read(self, initial: bool) -> None:
        """The waiting state: one line, one shut button, and nothing else.

        A state and not a nothing (AK-221). No progress bar, no wait cursor,
        no spinner, no second dialog -- a waiting mark beside a line that says
        the same thing in words is the same news twice (`UI_SPEC` §4 (4)).
        """
        self.owned_label.setText(
            READING_THE_SAVE if initial else READING_THE_SAVE_AGAIN)
        self.find_save_button.setVisible(False)
        for slot in self.base_slots + self.deep_slots:
            slot.show_the_save_is_being_read(True)

    def _the_save_has_been_read(self) -> None:
        """Leave the waiting state. Every ending of a read comes through here.

        The stock goes to the cards here, on every ending, because an ending
        without a stock is a replacement too (AK-267, QA-247): a read that
        came back empty used to leave the cards holding the relics of the
        save the header said had not been read.
        """
        for slot in self.base_slots + self.deep_slots:
            slot.show_the_save_is_being_read(False)
        self._hand_the_stock_to_the_slots()
        self._say_how_many_relics_are_owned()
        # The row's answer went with the old stock (`the_advisor_data_is_
        # changing`); now that the new stock is in, the row rests on it --
        # 4.1 with a save, 4.8 without one (AK-268). Until T-230 nothing put
        # the row back, and after a rescan that found nothing it went on
        # offering `Optimize` under a line saying no save was found.
        self.advisor_bar.clear()

    def _say_how_many_relics_are_owned(self) -> None:
        """The only place the line of its own is written (AK-250).

        Called from the one place every ending of a read passes through, and
        from nowhere else: a number that shares a line with messages is a
        number on loan, which is what QA-201 found. The stock it reads is the
        one this window holds by then -- `_on_save_read` and `_on_save_failed`
        both settle `self.owned` before they come here.

        Nothing at all until something has been read (AK-252, out of AK-222).
        Not `0`: that is an assertion about a stock nobody has looked at yet,
        and it is the one that reads like lost data. Not a waiting sentence
        either -- the line under this one already carries `Reading your save.`
        while a read is out, and the same news twice is what `UI_SPEC` §4 (4)
        rules out.

        "Nothing has been read" is asked as "there is nothing to name", not as
        "the stock is None". A character slot with no relics in it never
        becomes an `Inventory` at all (`inventory.py`, `_scan_save`), but
        `build` drops every record the dataset cannot name -- so a save from a
        newer game than the snapshot came from would arrive as a stock that
        counts zero, and `You own 0 relics in total.` is the one sentence
        AK-252 rules out.
        """
        if self.owned is None or not self.owned.relic_count:
            self.owned_total_label.clear()
            self.owned_total_label.setToolTip("")
            return
        self.owned_total_label.setText(
            OWNED_TOTAL.format(count=_relic_count(self.owned.relic_count)))
        # Escaped for the reason the note's own tooltip is escaped: a tooltip
        # decides for itself whether what it is handed is markup, and no text
        # format can be set on one (SEC-013). The name comes out of the
        # player's save file.
        self.owned_total_label.setToolTip(
            OWNED_TOTAL_TOOLTIP.format(source=html.escape(self.owned.source)))

    def _on_save_read(self, found) -> None:
        """The save has been read: put the window where a synchronous read left it.

        Counts, freed relic buttons, the chalice list on the new stock and --
        when this was the first read of the session -- the one-off taking over
        of the displayed Nightfarer's stored build, which `reload_chalices`
        does and which had nothing to take over from when it last ran.

        The advisor's caches are emptied **here**, not where the read was
        asked for (AD-029 point 3): every answer in them was worked out on the
        stock that is being replaced in the next line, and until this line
        every one of them was right.
        """
        self.the_advisor_data_is_changing()
        self.owned = None if found is None else inventory.build(self.data, found)
        self._the_save_has_been_read()
        if self.owned is None:
            # Two of the three exits of AK-124 meet here. For a file the
            # player picked, "nothing came back" means that file holds no
            # relics -- S3, and the reason for it is the one he can act on.
            # Without a choice behind it, it means no save was found at all.
            self.owned_label.setText(
                CHOSEN_SAVE_IS_EMPTY if self._answers_a_chosen_save
                else NO_SAVE_FOUND)
            self.find_save_button.setVisible(True)
            return

        note = f"{self.owned.relic_count} relics in {self.owned.source}"
        if self.owned.loadouts:
            note += f", {len(self.owned.loadouts)} stored builds"
        elif self.owned.loadout_error:
            # A save whose relics read but whose builds do not is a specific
            # failure with a specific cause, and reporting "0 builds" without
            # the cause left it undiagnosable from a bug report.
            note += f" — no stored builds could be read: {self.owned.loadout_error}"
        else:
            note += " — this save stores no builds yet"
        if self.owned.read_the_slow_way:
            note += READ_THE_SLOW_WAY_NOTE
        self.owned_label.setText(note)
        # The folder is named after the Steam account id, so it is offered on
        # hover rather than printed where every screenshot would carry it.
        #
        # Escaped, because a tooltip decides for itself whether what it is
        # given is markup exactly as a QLabel on AutoText does, and setting a
        # text format is not offered for tooltips (SEC-013). No Windows path
        # can contain a "<", so this is depth rather than a hole being shut:
        # the path is shown as the path, whatever it turns out to hold.
        self.owned_label.setToolTip(html.escape(self.owned.folder))
        # A save is loaded, so the offer to find one is gone (AK-123).
        self.find_save_button.setVisible(False)
        # reload_chalices, not apply_chalice: the relics have just changed
        # underneath the slots, so the saved build has to be matched
        # against the new inventory rather than left pointing at the old.
        # Unconditional now, first read included -- when it ran during
        # `__init__` there was no stock to match anything against.
        self.reload_chalices()

    def _hand_the_stock_to_the_slots(self) -> None:
        """Give every card the inventory the window now holds.

        Before the chalices are rebuilt, because the restore chooses out of
        what the cards can offer: a build put back against an empty stock puts
        nothing anywhere.

        It is done here and not left to `apply_chalice` because `apply_chalice`
        is not reached on every path out of `reload_chalices` -- a Nightfarer
        whose save stores no equipped loadout leaves `load_equipped` before it.
        While the reading was synchronous that could not be felt: the cards had
        been given the stock during `select_hero`, long before any chalice was
        built. With the reading in a thread the arrival is the only moment it
        can happen, so it happens here, once, whatever the chalices go on to
        do.
        """
        for slot in self.base_slots + self.deep_slots:
            slot.owned = self.owned
            slot.populate()
            slot.stock_replaced.emit()

    def _on_save_failed(self, reason: str) -> None:
        """The read could not be finished. The one place the prefix is written.

        The waiting sentence is never the last word (AK-224), on any of the
        four ways a read can end, and this is the way that used to be a bare
        `return` out of a `try`.

        For a file the player picked this is the third exit of AK-124, and it
        is worded the other way round: his sentence first, the reason under
        it (S4). The prefix stays where it was for every other read, and
        AK-229 holds either way -- both endings are endings with no stock.
        """
        self.the_advisor_data_is_changing()
        self.owned = None
        self._the_save_has_been_read()
        self.owned_label.setText(
            f"{CHOSEN_SAVE_UNREADABLE}\n{reason}" if self._answers_a_chosen_save
            else f"{UNREADABLE_SAVE}{reason}")
        self.find_save_button.setVisible(True)

    def load_equipped(self) -> None:
        """Load the current Nightfarer's equipped loadout out of the save.

        Reads the vessel that Nightfarer has selected and the relics sitting in
        it, so the planner starts from the real build rather than an empty one.
        """
        # While a read is out this button does nothing and writes nothing into
        # the line (`UI_SPEC` T-141 §5). The sentence it would write --
        # `No save loaded, so there is nothing to import.` -- is one of the
        # three §9 (h) forbids in this state, and it would be false: a save is
        # being read at this very moment.
        if self.save_reader.is_reading():
            return
        # The slots of every chalice are about to be written from the save, so
        # nothing may still be searching against what they held (AD-006.7).
        self.the_advisor_data_is_changing()
        if self.owned is None:
            self.owned_label.setText("No save loaded, so there is nothing to import.")
            return

        hero = self.current_hero()
        entries = self.owned.loadouts_for(hero["id"])
        # Every chalice is imported, not only the one being worn. The save
        # stores all of them, and a player who has built several and happens
        # to have an empty one equipped used to get an empty planner back.
        imported = 0
        for entry in entries:
            keys = [chalices.slot_key(r) for r in entry.relics]
            keys += [""] * (6 - len(keys))
            if any(keys):
                chalices.save(hero["id"], entry.vessel_id, entry.deep_used, keys)
                imported += 1
            else:
                # Empty in the game means empty here: this button says the
                # save is the truth. Named builds are stored separately and
                # are not touched, so planning work survives an import.
                chalices.clear(hero["id"], entry.vessel_id)

        # The vessel shown is the one actually worn, even when it is empty:
        # the button says "equipped", and opening a different chalice because
        # it happens to have relics in it would misreport the game. The empty
        # case is explained in the note instead, and the other chalices are
        # already filled in by then.
        loadout = self.owned.selected_loadout(hero["id"])
        if loadout is None:
            if self.owned.loadout_error:
                self.owned_label.setText(
                    "This save's stored builds could not be read: "
                    f"{self.owned.loadout_error}"
                )
            else:
                self.owned_label.setText(
                    f"This save stores no equipped loadout for {hero['name']}."
                )
            return

        # Rows include the two caption rows, so the vessel is found by its own
        # id on the item rather than by position.
        row = next(
            (i for i in range(self.chalice_list.count())
             if (self.chalice_list.item(i).data(Qt.UserRole) or {}).get("id")
             == loadout.vessel_id),
            None,
        )
        if row is None:
            self.owned_label.setText(
                f"{hero['name']} has vessel {loadout.vessel_id} equipped, which "
                "is not in this list."
            )
            return

        # What is on screen after this is the save's build, so the picker has
        # to say so. It kept naming whichever saved build was chosen before,
        # which then described a chalice it had nothing to do with.
        chalices.set_selected_build(hero["id"], chalices.EQUIPPED_NAME)
        self.refresh_build_list(chalices.EQUIPPED_NAME)

        # The guard goes up before the row changes, not after. Changing the
        # row fires the list's own handler, which stores what the slots hold
        # -- and at that moment they still hold the chalice being left, while
        # the vessel id has already moved on. That wrote one chalice's relics
        # under another one's name: importing a Nightfarer whose equipped
        # chalice is empty gave it whatever was on screen beforehand.
        #
        # It also holds off the per-vessel restore inside apply_chalice: the
        # save is the authority here, and restoring would put the stored
        # build back and take the save's Deep of Night setting with it.
        self._restoring = True
        try:
            # Set the vessel and mode first: both rebuild the slots, which
            # would otherwise discard the relics just put in them.
            self.chalice_list.setCurrentRow(row)
            # Deep of Night is only ever switched ON here, never off. The
            # save says whether the equipped build uses the extra slots, but
            # the switch is also how the player chooses what to look at:
            # turning it on and then importing used to turn it straight back
            # off. Slots are filled either way, so nothing is lost by
            # leaving it on.
            if loadout.deep_used and not self.deep_check.isChecked():
                self.deep_check.blockSignals(True)
                self.deep_check.setChecked(True)
                self.deep_check.blockSignals(False)
            self.apply_chalice()
        finally:
            self._restoring = False

        slots = list(self.base_slots) + list(self.deep_slots)
        # By copy, not by list entry. The lists hold one entry per roll, and
        # this save equips two copies of one roll in the same chalice -- the
        # second was not in any list and could not be placed at all (QA-021).
        #
        # A relic the save names and the inventory no longer has arrives here
        # as None, indistinguishable from an empty slot, so what is left when
        # a placement fails is a relic this slot will not take: the wrong
        # colour for it, or the wrong side of Deep of Night. That is what is
        # said, because it is what happened.
        unfit = 0
        for slot, item in zip(slots, loadout.relics):
            if item is not None and slot.select_copy(item.handle):
                continue
            if item is not None:
                unfit += 1
            # The slot the save names a relic for is empty when that relic
            # cannot be placed, never left holding the one the chalice
            # before it had there.
            slot.clear_relic()
        # These slots are the equipped chalice's now, and the next click on
        # the chalice list has to know it. Without this, clicking back on the
        # chalice that was open *before* Load equipped counted as no change
        # at all: nothing cleared the slots, and the equipped build was
        # written into a chalice that is empty in the game.
        self._mark_vessel_applied()

        # Every row, not only the one on screen: the import has just filled
        # the other chalices, and they should say so without being clicked.
        self.refresh_vessel_rows()
        # Before the note is written, because settling can empty a slot and
        # the note is about what is on screen when it is read.
        clashed = self._settle_slots()
        vessel_name = self.chalice_list.item(row).data(Qt.UserRole)["name"]
        count = f"{imported} {'chalice' if imported == 1 else 'chalices'}"
        # What the slots actually hold. Counting the save's relics instead
        # told the player about six relics they could not see, on a screen
        # holding none of them (QA-024).
        placed = sum(1 for slot in slots if slot.current_relic() is not None)
        if placed:
            note = (f"Loaded {hero['name']} — {count}, showing the equipped "
                    f"{vessel_name} with {_relic_count(placed)}"
                    f"{' (Deep of Night)' if loadout.deep_used else ''}.")
        elif unfit or clashed:
            note = (f"Loaded {hero['name']} — {count}. Nothing the equipped "
                    f"{vessel_name} holds in game could be placed.")
        elif imported:
            note = (f"Loaded {hero['name']} — {count}. The equipped "
                    f"{vessel_name} is empty in game; the others are in the "
                    "list on the left.")
        else:
            note = (f"Loaded {hero['name']} — every chalice is empty in game.")
        # Each with the reason it happened for. "Could not be placed" on its
        # own left the player to guess, and the guess it invited was that the
        # program had lost the relic.
        if unfit:
            fit = ("it does not fit the slot the save has it in" if unfit == 1
                   else "they do not fit the slots the save has them in")
            note += f" {_relic_count(unfit)} could not be placed: {fit}."
        if clashed:
            worn = "it is" if clashed == 1 else "they are"
            note += (f" {_relic_count(clashed)} could not be placed: "
                     f"{worn} already worn in another slot.")
        self.owned_label.setText(note)
        self.recompute()

    def _wire_the_advisor(self) -> None:
        """Every way an answer leaves the bar or a card and reaches the slots.

        The bar is handed nothing here and reads no widget of this window: it
        says an answer stands or has gone (`suggestion_changed`), that the
        player asked for the long form (`why_requested`) and that they asked
        for the answer to be applied or taken back. This window decides what
        each of those means for the cards, because this window owns them.

        `Use` is wired per card and carries the card with it: the block knows
        which slot it is drawn in only by being in it, and a signal that
        arrived without saying which slot it came from would have to be
        matched back to one by looking at the screen.
        """
        self.advisor_bar.suggestion_changed.connect(self._the_suggestion_changed)
        self.advisor_bar.reading_changed.connect(self._the_reading_changed)
        self.advisor_bar.why_requested.connect(self.open_why)
        self.advisor_bar.apply_all_requested.connect(self.apply_all)
        self.advisor_bar.undo_apply_requested.connect(self.undo_apply)
        for card in list(self.base_slots) + list(self.deep_slots):
            card.suggestion.use_requested.connect(
                lambda slot=card: self.use_the_suggestion(slot))

    def _the_suggestion_changed(self, result) -> None:
        """A different answer stands, or none does.

        What the slots held before the last applying goes with it: it was the
        state to undo **that** answer into, and an answer that has been
        replaced cannot be undone any more -- `Apply all` on the new one
        would otherwise offer to put back a build the player has not seen
        since.
        """
        self._slots_before_applying = None
        self.show_the_suggestion(result)

    def _the_reading_changed(self, worst: bool) -> None:
        """The bar's second box moved; the window holds what it stands on."""
        self.worst_case = worst

    # -- applying an answer -------------------------------------------------

    def _all_slots(self) -> list:
        """Every slot panel of this vessel, Deep ones included and in order.

        The order is the one `active_slots` counts in and the one
        `_restore_slot_keys` writes in, which is why a slot index out of an
        answer can be used against this list without translating.
        """
        return list(self.base_slots) + list(self.deep_slots)

    # -- holding a slot -----------------------------------------------------

    def _hold_key(self) -> tuple:
        """Which build a hold belongs to: Nightfarer, vessel, Deep (AD-017.2).

        The Deep switch is part of it because it changes which slots there
        are: slot 4 of a vessel with Deep of Night on is not slot 4 of the
        same vessel with it off, and a hold that carried across would be a
        hold on a slot the player cannot see.
        """
        vessel = self.current_vessel()
        return (self.current_hero()["id"],
                vessel["id"] if vessel else None,
                self.deep_check.isChecked())

    def held_slot_indices(self) -> frozenset:
        """The slots the player is holding in the build now on screen."""
        return frozenset(self._holds.get(self._hold_key(), {}))

    def _hold_changed(self, card, on: bool) -> None:
        """The player worked a card's `Hold` button.

        The copy the hold was made on is written down beside it, and that is
        what makes AK-56 answerable later: once the relic has gone from the
        save the slot is empty, and an empty held slot is a legitimate state
        of its own (AK-55) -- so "held on nothing" and "held on a relic that
        has since gone" cannot be told apart afterwards unless the handle was
        kept at the moment of holding.
        """
        slots = self._all_slots()
        if card not in slots:
            return
        key = self._hold_key()
        holds = self._holds.setdefault(key, {})
        if on:
            holds[slots.index(card)] = getattr(card.current_relic(), "handle",
                                               None)
        else:
            holds.pop(slots.index(card), None)
        if not holds:
            self._holds.pop(key, None)
        # A held slot is one no applying may touch, so the card's own `Use`
        # comes and goes with the hold.
        self.show_the_suggestion(self.advisor_bar.answer)

    def _show_the_holds(self) -> None:
        """Draw the hold state of the build now on screen, and drop the dead.

        Called wherever the build on screen changes -- a vessel, a Nightfarer,
        the Deep switch, a relic -- because all four change either which holds
        apply or what they were made on. Going away and coming back therefore
        carries (AK-60, OF-12): nothing was thrown away when the vessel was
        left, and this puts it back on the cards.

        **A hold whose copy the save no longer has falls away, and says so**
        (AK-56, §4.3, AD-017.3). Checked against the inventory rather than
        against the slot: by the time this runs the slot has already been
        emptied by the repopulation, and an empty slot is what a legitimately
        held empty slot looks like too.

        **Never mid-restore.** A restore holds slots that are half the build
        being left and half the one arriving, and a released hold's sentence
        written into a slot there is wiped by the restore's own emptying a
        line later -- so the hold would fall away in silence, which is the
        one thing §4.3 forbids. Every restoring path ends in `recompute`
        with the guard down, which is where this really runs.
        """
        if self._restoring or getattr(self, "base_slots", None) is None:
            return
        slots = self._all_slots()
        key = self._hold_key()
        holds = self._holds.get(key, {})
        # The inventory is only asked when there is a hold to ask about it:
        # this runs on every recomputation, and with nothing held there is
        # nothing for the answer to decide.
        owned_handles = set(self._relics_by_handle()) if holds else set()
        released = [index for index, handle in holds.items()
                    if handle is not None and handle not in owned_handles]
        for index in released:
            holds.pop(index, None)
        if not holds:
            self._holds.pop(key, None)
        for index, slot in enumerate(slots):
            slot.show_the_hold(index in holds)
        # What a surviving hold is now made on, because the player may have
        # put another relic in that slot themselves since -- the tooltip says
        # they still can, and a hold left pointing at the relic before would
        # release itself the next time that one was melted.
        for index in list(holds):
            if index < len(slots):
                holds[index] = getattr(slots[index].current_relic(), "handle",
                                       None)
        for index in released:
            if index < len(slots):
                slots[index].clear_relic(HOLD_RELEASED)

    def apply_all(self) -> None:
        """`Apply all`: every suggested slot the player is not holding."""
        self._apply_the_answer_to(None)

    def use_the_suggestion(self, card) -> None:
        """`Use` on one card: that slot and no other (`UI_SPEC` §3.2)."""
        slots = self._all_slots()
        if card not in slots:
            return
        self._apply_the_answer_to({slots.index(card)})

    def _apply_the_answer_to(self, only: set | None) -> None:
        """Put the suggested copies into the slots, the way a restore does.

        `only` names the slots to touch, or `None` for all of them.

        **The existing road, not a second one.** AK-14 asks that the state
        after applying be the state that choosing the relics one at a time in
        the picker would have left, persistence per chalice included, and the
        way this window already reaches that state is `_restore_slot_keys`
        over a list of stored keys. So applying writes the keys it wants into
        the list the slots are holding now and hands the whole list to that.
        An empty slot, a custom relic and a copy named by handle all travel
        as keys already, which is also what makes `Undo apply` a list of the
        same kind and not a second mechanism (AK-15).

        **A held slot is never touched** (AK-57, §5.4). Not because a run
        ever offers one -- the request takes the held slots out of the search
        (`asking_from`) -- but because a hold can be made *after* the answer
        arrived, and the answer standing on screen does then name it.

        **Only copies the save has.** A choice whose handle is not in the
        inventory is passed over rather than guessed at: AK-16 forbids
        suggesting a relic that is not owned, and this is where that would
        otherwise become a relic in a slot.
        """
        result = self.advisor_bar.answer
        if result is None or not result.suggestions:
            return
        slots = self._all_slots()
        before = [slot.saved_key() for slot in slots]
        keys = list(before)
        held = self.held_slot_indices()
        by_handle = self._relics_by_handle()
        for choice in result.suggestions[0].choices:
            index = choice.slot_index
            if index >= len(slots) or index in held:
                continue
            if only is not None and index not in only:
                continue
            copy = by_handle.get(choice.handle)
            if copy is None:
                continue
            keys[index] = chalices.slot_key(copy)
        if keys == before:
            return
        if self._slots_before_applying is None:
            self._slots_before_applying = before
        self._put_these_keys_in_the_slots(keys)
        self.advisor_bar.the_suggestion_was_applied()
        self.show_the_suggestion(result)

    def undo_apply(self) -> None:
        """`Undo apply`: the slots exactly as they were before (AK-15).

        Exactly, and that word is the whole criterion: a slot that was empty
        goes back to empty and a slot that held a custom relic gets that
        custom relic back, both of which fall out of restoring the keys
        rather than the relics -- an empty slot is the empty key and a custom
        relic is a key that carries its own effects.

        A slot held since the applying keeps what it holds: no applying put
        anything of the advisor's there, so there is nothing to take back
        (§5.4).
        """
        before = self._slots_before_applying
        if before is None:
            return
        held = self.held_slot_indices()
        keys = [slot.saved_key() if index in held else before[index]
                for index, slot in enumerate(self._all_slots())]
        self._slots_before_applying = None
        self._put_these_keys_in_the_slots(keys)
        self.advisor_bar.the_suggestion_was_undone()
        self.show_the_suggestion(self.advisor_bar.answer)

    def _put_these_keys_in_the_slots(self, keys: list[str]) -> None:
        """Set every slot from a list of stored keys, as a restore does.

        The same four steps `_apply_stored_build` ends on, and for the same
        reasons: the restore itself, then the clash resolution, then the one
        recomputation, then the store. The vessel and the Deep switch are not
        touched here -- applying a suggestion changes what is in the slots
        and never which slots there are.

        Wrapped in `while_the_player_applies_it` because every one of those
        steps ends in `recompute`, which tells the advisor that the build has
        changed (AK-12). It has -- but by the row's own doing, and an answer
        that threw itself away as it was being applied would leave `Undo
        apply` with nothing to undo.
        """
        slots = self._all_slots()
        with self.advisor_bar.while_the_player_applies_it():
            self._restoring = True
            try:
                self._restore_slot_keys(slots, keys)
            finally:
                self._restoring = False
            self._settle_slots()
            self.recompute()
            self._store_chalice()

    def show_the_suggestion(self, result) -> None:
        """Put the living answer on the slot cards, or take it off them.

        Every card is cleared first, the Deep ones included. That breadth is
        belt to a brace and has **no case that can catch it**: `recompute`
        tells the bar the build changed, the bar drops the answer, and this
        runs with `None` before the Deep cards can leave `active_slots`. It
        stays because the rule it states -- no card keeps a block when no
        answer stands -- is this method's own, and reading it off another
        module's order of calls is how a stale block would arrive one day.

        A group naming a slot this vessel does not have means the answer and
        the window are describing different builds. Nothing is drawn then --
        `AdvisorBar.the_build_changed` throws such an answer away before it
        gets here, so this is the belt to that brace and not a state the
        player can reach.
        """
        cards = self.active_slots()
        for card in list(self.base_slots) + list(self.deep_slots):
            card.put_the_suggestion_away()
        if result is None or not result.suggestions:
            return
        suggestion = result.suggestions[0]
        if any(group.slot_index >= len(cards)
               for group in suggestion.reasons):
            return
        by_slot = {choice.slot_index: choice for choice in suggestion.choices}
        # The reading is the window's now, and the bar has already thrown
        # away any answer given under the other one (AK-183), so the head of
        # every block names the reading its figures were formed under.
        reading = reading_label(self.worst_case)
        for group in suggestion.reasons:
            cards[group.slot_index].show_the_suggestion(
                result.goal_label, reading, group,
                by_slot.get(group.slot_index))

    def open_why(self) -> None:
        """The long form of the answer on screen (`UI_SPEC` §3.4).

        The head of the dialog names five things no result carries -- the
        reading, who is being built, on which vessel, with Deep of Night on
        or off, and out of how many relics -- so they are read off this
        window at the moment the dialog opens.
        """
        result = self.advisor_bar.answer
        if result is None:
            return
        vessel = self.current_vessel() or {}
        heading = advisorblock.WhyHeading(
            goal_label=result.goal_label,
            reading=reading_label(self.worst_case),
            nightfarer=str(self.current_hero()["name"]),
            vessel=str(vessel.get("name", "")),
            deep=self.deep_check.isChecked(),
            relics=0 if self.owned is None else self.owned.relic_count,
        )
        advisorblock.WhyDialog(heading, result, self).exec()

    def active_slots(self) -> list:
        slots = list(self.base_slots)
        if self.deep_check.isChecked():
            slots += self.deep_slots
        return slots

    def selected_curses(self) -> list[tuple[str, dict]]:
        """Every curse on the currently equipped relics, with its source.

        Only Deep of Night relics carry curses, so this is empty unless the
        Deep slots are in play.
        """
        out = []
        for slot in self.active_slots():
            item = slot.relic_box.currentData()
            if item is None:
                continue
            for cid in getattr(item, "curse_ids", ()) or ():
                eff = self.effects.get(str(cid))
                if eff:
                    out.append((item.name, eff))
        return out

    def selected_effects(self) -> list[dict]:
        slots = self.active_slots()
        out = []
        for slot in slots:
            for eid in slot.selected_ids():
                eff = self.effects.get(str(eid))
                if eff:
                    out.append(eff)
        return out

    def _sync_situational(self, entries: list) -> None:
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
                    entry, self.declared.get(entry.effect_id, 0),
                    self._situational_changed,
                )
                self.situational_rows[entry.effect_id] = row
                self.qual_rows_layout.addWidget(row)
        self.qual_rows.setVisible(bool(entries))

        # An effect that is no longer equipped stops being declared, so putting
        # the same relic back on does not silently bring a stale count with it.
        for eid in list(self.declared):
            if eid not in self.situational_rows:
                del self.declared[eid]

    def _situational_changed(self) -> None:
        self.declared = {
            eid: row.value()
            for eid, row in self.situational_rows.items()
            if row.value() > 0
        }
        self.recompute()

    def _rebuild(self) -> model.Build:
        """Turn what is on screen into a build. The only call to the model.

        Everything that reaches a total is gathered in this one place: the
        relics in the slots, the effects the armaments rolled, the curses
        those relics carry, the weapon-type gates and whatever conditional
        effects the player has declared.

        A second caller with an argument list of its own is how the Weapons
        tab came to rank every armament in the game against a build three
        attributes away from the one on screen, with nothing on the window to
        say which was right (QA-001). So there is one caller, and everyone
        else is handed the result through current_build().
        """
        # Curses are part of the relic you equipped, so they count towards the
        # totals exactly as the good rolls do. Leaving them out meant a curse
        # reading "Reduced Dexterity and Faith -3" changed no attribute, which
        # made the sheet quietly wrong for every Deep of Night build.
        curses = [eff for _source, eff in self.selected_curses()]
        return model.compute(
            self.current_hero(), self.level_slider.value(),
            # Armament effects count towards the sheet alongside the relics.
            self.selected_effects() + self.weapon_effects() + curses,
            self.curves,
            # A weapon-type buff such as "Improved Axe Attack Power" is live
            # when any armament on the grid is of that type, so the gate is
            # tested against all six rather than only the active tile.
            weapon=self.active_slot().weapon,
            weapons_held=self.equipped_weapons(),
            declared=self.declared,
        )

    def current_build(self) -> model.Build:
        """The build every tab reads.

        Kept up to date by recompute(), which runs on every change that can
        move a number. Computed on the spot if something asks before the
        first recompute -- a tab built during startup, for instance.
        """
        if self._build is None:
            self._build = self._rebuild()
        return self._build

    def recompute(self) -> None:
        # Both halves of the guard say the same thing -- the window is still
        # being built -- and both are needed: the level slider is made in the
        # left pane and the advisor's row in the middle one, so between the
        # two there is a moment when a signal could reach here.
        if not hasattr(self, "level_slider") or not hasattr(self, "advisor_bar"):
            return
        # ...and the one place the hold state can be drawn, for the same
        # reason: every change that decides which holds apply -- Nightfarer,
        # vessel, Deep of Night -- and every change to what a hold was made
        # on ends here. Drawn from one place rather than from the four that
        # cause it, because a fifth arrived once already and did not know it
        # had to say so (see `populate`'s note about narrowing a slot).
        self._show_the_holds()
        # Every path that changes a vessel, a mode or a relic ends here, so
        # this is the one place the stored build has to be kept up to date.
        self._store_chalice()
        # ...and the one place the advisor can hear that the build it was
        # asked about is not the build any more (AK-12).
        self.advisor_bar.the_build_changed()
        hero = self.current_hero()
        level = self.level_slider.value()
        self.level_label.setText(str(level))
        exact = hero["exact_levels"]
        self.level_note.setText(
            "Exact value from the game data."
            if level in exact
            else f"Interpolated — the game defines levels {', '.join(map(str, exact))}."
        )

        build = self._build = self._rebuild()

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
            lines.append(f"<div>{label} {value}</div>")
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
            restricted += spell_out(bucket, f"{class_name} armaments only")

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
        if build.other:
            lines = []
            for fname, value in sorted(
                    model.collapse_by_label(build.other).items()):
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
                    f"<div>{model.label_for(fname)} "
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

        self._sync_situational(build.situational)

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

        curses = self.selected_curses()
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
        elif self.deep_check.isChecked():
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


def main() -> int:
    # Before the QApplication, which is when Qt reads it and so the last
    # moment it can be said.
    uiscale.apply_to_environment()

    app = QApplication(sys.argv)
    apply_appearance(app)

    # Before anything is read, written or drawn. A second copy that got as
    # far as the first-run check would already have touched the player's
    # files, and one that got as far as a window would be the finding itself:
    # two windows at the same size in the same place, sharing one settings
    # store, with clicks landing in whichever happens to be in front
    # (QA-163).
    running = singleinstance.RunningCopy()
    if not running.claim():
        running.raise_the_running_one()
        return 0

    icon = datasource.icon_path()
    if icon:
        app.setWindowIcon(QIcon(str(icon)))

    # Nothing ships with the program, so the first launch on a machine has
    # to read the installed game before there is anything to show. Where the
    # game is, is the resolution point's question and no longer this line's:
    # a folder the player pointed at himself counts for as much here as it
    # does everywhere else (AD-030).
    first = firstrun.run(gamepath.resolve_game())
    if not first.go_on:
        # He was asked where his game is and said Quit, Escape or the cross.
        # Nothing to report back to him: he has just said it (AK-116).
        return 0
    if first.error:
        QMessageBox.critical(
            None, "Nightreign Helper", f"Could not read your game:\n\n{first.error}"
        )
        return 1

    try:
        data = load_data()
    except Exception as exc:  # noqa: BLE001
        # The last A8 hole of QA-211, and the only one a player can reach
        # before the window exists. `load_data` raises `NoGameData` with the
        # long English explanation of the no-game case, and `errortext` hands
        # that through because the class is this program's; anything else --
        # an `OSError` from reading the snapshot, a library's complaint about
        # its contents -- is worded here instead of by Windows.
        QMessageBox.critical(None, "Nightreign Helper",
                             errortext.in_english(exc))
        return 1

    window = Planner(data)
    window.show()
    # After show(), because a window has no native handle before it has been
    # to the screen. `running` is held for the run of the program: dropping
    # it would release the claim and let a second copy in.
    running.announce(int(window.winId()))
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
