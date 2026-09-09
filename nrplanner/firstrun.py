"""Building the local data set before the main window opens.

The program ships no game content, so on a machine that has never run it
there is nothing to show until the installed game has been read. That takes
about a minute: roughly half extracting the params, half decoding the icon
atlases. Doing it silently would look like a hang, and doing it on every
launch would be intolerable, so it happens once, visibly, into the per-user
cache, and is reused until the game is patched.

**And when there is no installation to read, the player is asked where his
is** (A15, `UI_SPEC` "Der Erststart mit Ordnerauswahl"). Until this the
answer to "no game found" was a `QMessageBox.critical` and the end of the
program -- a dead end for everybody whose game sits where the automatic route
does not look. The question is the first state of the same window the build
happens in: question, confirmation, build, done.
"""

from __future__ import annotations

import dataclasses
import datetime
import os
import pathlib
import traceback

from PySide6.QtCore import QEventLoop, QObject, Qt, QThread, Signal
from PySide6.QtWidgets import (QApplication, QCheckBox, QFileDialog,
                               QHBoxLayout, QLabel, QProgressBar, QPushButton,
                               QVBoxLayout, QWidget)

from nrdata import gamefiles

from . import gamepath, paths, shortcut
from .datasource import bundled_path, defs_dir


def _regulation_stamp(game: pathlib.Path) -> tuple[str, int] | None:
    """Identify the installed game version, as (sha256, size)."""
    import hashlib

    path = game / "regulation.bin"
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_size


def what_is_needed(game: pathlib.Path | None) -> list[str]:
    """Which build steps have to run: any of "snapshot", "icons"."""
    if game is None:
        return []

    needed = []

    # Whichever snapshot the app would actually load -- the cache, or one
    # built beside the package in a source tree. Checking only the cache
    # would rebuild for a developer who already has a local snapshot.
    snapshot = bundled_path()
    if not snapshot.exists():
        needed.append("snapshot")
    else:
        # A patched game invalidates the snapshot. Hashing 2 MB costs a few
        # milliseconds, which is worth it to avoid a minute of rebuilding.
        try:
            import json

            from nrdata import extract

            meta = json.loads(snapshot.read_text(encoding="utf-8")).get("meta", {})
            stamp = _regulation_stamp(game)
            # Two ways to be out of date, and both have to rebuild here or the
            # cache is never written: a patched game, and a snapshot built by
            # an older version of this program's extractor.
            if meta.get("extract_version") != extract.EXTRACT_VERSION:
                needed.append("snapshot")
            elif stamp and (
                meta.get("regulation_sha256") != stamp[0]
                or meta.get("regulation_size") != stamp[1]
            ):
                needed.append("snapshot")
        except Exception:  # noqa: BLE001 - an unreadable snapshot is a rebuild
            needed.append("snapshot")

    # Same for the icon pack: whichever one IconPack would find.
    from .iconpack import IconPack

    icon_manifest = IconPack.locate() / "manifest.json"
    if not icon_manifest.exists():
        needed.append("icons")
    else:
        # A pack that exists is not necessarily a pack this build can use.
        # Rebuilding only when the manifest was missing meant an upgrading
        # player kept whatever an older build wrote: 1.5.0 draws chalice
        # slots and damage icons from sprites 1.4.0 never extracted, and
        # every existing installation would have come up without them.
        #
        # A manifest that cannot be read is left alone rather than rebuilt.
        # On this machine the icons directory intermittently refuses to
        # open -- see iconpack._read_with_retries -- and treating that as
        # "out of date" would rebuild the whole pack on every single launch,
        # which is far worse than keeping the pack already on disk.
        import json

        from nrdata import iconbuild

        from .iconpack import _read_with_retries

        raw = _read_with_retries(icon_manifest)
        if raw is not None:
            try:
                built = json.loads(raw.decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                needed.append("icons")
            else:
                if built.get("icon_version", 1) != iconbuild.ICON_VERSION:
                    needed.append("icons")

    return needed


# --- Where is the game? ---------------------------------------------------
#
# The texts, the panels, and every decision the flow makes. Word for word out
# of `UI_SPEC` section 7; nothing here is written freehand, and the section
# numbers in this half of the file are that document's.

#: The three colours this window sets text in. Written out here as every
#: other module writes them out (`app.py:115-117`): importing them from `app`
#: would be a circle, since `app` is what starts this.
GOOD = "#6fbf73"
BAD = "#d1655f"
MUTED = "#8a8a8a"

#: The title of the question state, in its title bar and in the taskbar.
WINDOW_TITLE = "Nightreign Helper"

#: Both states are this wide, so the window does not jump when the question
#: turns into the build (AK-118). Logical pixels, Windows display 100 %.
PANEL_WIDTH = 460
#: The question state is as tall as its content, and no shorter than this.
LEAST_PANEL_HEIGHT = 230
#: The margins the panel has always had, kept as names because the height of
#: a wrapped line has to be worked out against the width they leave.
SIDE_MARGIN = 28
TOP_MARGIN = 24

#: The last place worth opening the folder dialog in when nothing nearer is
#: known (section 4.1) -- Steam's own library list, read through
#: `gamefiles.steam_common_folders`, is tried first in
#: `where_to_start_looking`; this is only what stands in for it when Steam
#: itself cannot be found at all.
STEAM_COMMON = pathlib.Path(r"C:\Program Files (x86)\Steam\steamapps\common")

#: What a button hands back. Plain strings rather than an enum: they are
#: compared and never counted, and a failed comparison reads as itself.
QUIT = "quit"
CHOOSE = "choose"
USE = "use"
CARRY_ON = "carry on"

#: How a line of a panel is set. A path is *not* MUTED: it is the one thing
#: the user is being asked to check (AK-129).
TEXT = "text"
PATH = "path"

#: An invisible break opportunity (U+200B), put after every separator of a
#: path so that a long one wraps instead of running past the edge (AK-129).
BREAK_HERE = "\u200b"

#: Where the folder that was found sits, relative to the one that was picked.
#: Four answers rather than three since AK-246: how far *into* the picked
#: folder the search had to go decides as much as whether it stayed in it.
SAME = "same"        # the folder he picked is the one that holds the game
INSIDE = "inside"    # one level in: the ordinary case of section 4.2
DEEPER = "deeper"    # two levels in or more: found, but never shown to him
OUTSIDE = "outside"  # a climb, another branch, or a junction leading out

#: How far the search may go down into the folder the user picked and still
#: come back with something that passes for the folder he showed. One level,
#: because that is the case section 4.2 describes and the whole of it: Steam's
#: `Browse local files` opens ...\ELDEN RING NIGHTREIGN, one level above the
#: ...\Game the search returns. From two levels down, what was found is a
#: folder he never pointed at -- an attacker chooses the shape of the archive
#: somebody unpacks, so that distance is not a matter of chance (SEC-032) --
#: and it is put to him as C3 before anything is read (AK-246). The search
#: itself keeps its reach: SEARCH_DEPTH and SEARCH_PARENTS are unchanged at 3
#: and 2, because refusing those folders outright would turn a question into
#: a rejection of cases section 4.2 supports (AK-249).
LEVELS_TAKEN_ON_TRUST = 1

#: Said under A1 and A2, below the buttons, in MUTED (section 3, point 7).
COME_BACK_LATER = "You can close this and come back later. It will ask again."


@dataclasses.dataclass(frozen=True)
class Line:
    """One line of a panel, and how it is set."""

    text: str
    kind: str = TEXT


@dataclasses.dataclass(frozen=True)
class Button:
    """One button of a panel: what it says, and what pressing it means."""

    label: str
    answer: str


@dataclasses.dataclass(frozen=True)
class Verdict:
    """What the folder the user pointed at turned out to hold."""

    picked: pathlib.Path
    found: pathlib.Path | None
    named: bool
    where: str


@dataclasses.dataclass(frozen=True)
class Panel:
    """One state of the question: what it says, and what it offers.

    `about` is the verdict a `Use ...` button confirms. Only the two panels
    that offer one carry it, which is what makes "at most one question per
    pick" (AK-237) a property of the panels rather than of the loop.
    """

    name: str
    headline: str
    lines: tuple[Line, ...]
    buttons: tuple[Button, ...]
    escape: str
    footer: str = ""
    rejects: bool = False
    about: Verdict | None = None

    @property
    def default(self) -> Button:
        """The rightmost button, which is the one Enter presses (section 9)."""
        return self.buttons[-1]


QUIT_BUTTON = Button("Quit", QUIT)
CHOOSE_BUTTON = Button("Choose folder...", CHOOSE)
ANOTHER_BUTTON = Button("Choose a different folder...", CHOOSE)


def a1() -> Panel:
    """First run, and nothing found anywhere."""
    return Panel(
        name="A1",
        headline="Where is ELDEN RING NIGHTREIGN installed?",
        lines=(
            Line("Nightreign Helper reads every number it shows out of your "
                 "own copy of the game, and it could not find one on this PC."),
            Line("In Steam, right-click ELDEN RING NIGHTREIGN in your library "
                 "and choose Manage, then Browse local files. Pick the folder "
                 "that opens."),
            # Not a reassurance, and not MUTED (T-145, SEC-027): a library out
            # of this folder is *run*, and the sentence the consent rests on
            # may not be the faintest text in the window.
            Line("Nothing in that folder is changed, moved or deleted. To "
                 "read the game's files, Nightreign Helper runs a small "
                 "program out of that folder, so pick a copy of the game you "
                 "trust — normally the one you play."),
        ),
        buttons=(QUIT_BUTTON, CHOOSE_BUTTON),
        escape=QUIT,
        footer=COME_BACK_LATER,
    )


def a2(remembered) -> Panel:
    """A later start: the remembered folder is gone, and there is no data."""
    return Panel(
        name="A2",
        headline="Your game is not where it was last time.",
        lines=(
            Line("Nightreign Helper last read it from:"),
            Line(os.fspath(remembered), PATH),
            Line("That folder is not there now. If the game was moved or "
                 "reinstalled, or if it sits on a drive that is not plugged "
                 "in right now, point this at the new place."),
        ),
        buttons=(QUIT_BUTTON, CHOOSE_BUTTON),
        escape=QUIT,
        footer=COME_BACK_LATER,
    )


def a3(remembered, day: str) -> Panel:
    """A later start: the folder is gone, but what was read from it is not.

    An unplugged drive is not a total loss, so this one does not block, and
    Escape means carrying on rather than quitting (AK-116, AK-119).
    """
    return Panel(
        name="A3",
        headline="Your game is not where it was last time.",
        lines=(
            Line("Nightreign Helper last read it from:"),
            Line(os.fspath(remembered), PATH),
            Line(f"You can carry on with what was read on {day}. Those "
                 "numbers stay right until the game is updated."),
        ),
        buttons=(Button(f"Continue with the data from {day}", CARRY_ON),
                 CHOOSE_BUTTON),
        escape=CARRY_ON,
    )


def e1(picked) -> Panel:
    """Stage 1 said no: no installed game at or around this folder."""
    return Panel(
        name="E1",
        headline="That folder does not hold a copy of the game.",
        lines=(
            Line("You picked:"),
            Line(os.fspath(picked), PATH),
            Line("Nothing inside it looked like an installed game. Pick the "
                 "folder the game itself is in: in Steam that is Manage, then "
                 "Browse local files."),
        ),
        buttons=(QUIT_BUTTON, ANOTHER_BUTTON),
        escape=QUIT,
        rejects=True,
    )


def w1(verdict: Verdict) -> Panel:
    """Stage 2 is unsure: a FromSoftware game, but not named after this one.

    Not a rejection -- renaming an install folder is allowed and happens
    (section 4.3) -- but the default button is the way out and not the way on
    (AK-113): a minute spent on ELDEN RING, and every number afterwards
    wrong, is the more expensive mistake.
    """
    return Panel(
        name="W1",
        headline="This does not look like ELDEN RING NIGHTREIGN.",
        lines=(
            Line("There is an installed FromSoftware game here:"),
            Line(os.fspath(verdict.found), PATH),
            Line("Its folder is not named after ELDEN RING NIGHTREIGN, so "
                 "this may be a different game. Reading it takes about a "
                 "minute, and every number would be wrong."),
            Line("To read it, Nightreign Helper runs a small program out of "
                 "this folder, so only carry on with a copy of the game you "
                 "installed yourself."),
        ),
        buttons=(Button("Use this folder anyway", USE), ANOTHER_BUTTON),
        escape=QUIT,
        rejects=True,
        about=verdict,
    )


def c3(verdict: Verdict) -> Panel:
    """The search did not come back with the folder he showed, so it is put
    to him.

    Two triggers since AK-246, and one text for both: the search left the
    tree he pointed at (a climb, a change of branch, a junction leading out),
    or it stayed inside it but went two levels down or more. A folder that
    deep is still inside the one he picked, so `outside that folder` -- the
    T-146 wording -- would be false there; what is true of both is that the
    game is not directly in what he pointed at (AK-247).
    """
    return Panel(
        name="C3",
        headline="Is this your game?",
        lines=(
            Line("You picked:"),
            Line(os.fspath(verdict.picked), PATH),
            Line("The game itself is not directly in that folder. It is in:"),
            Line(os.fspath(verdict.found), PATH),
            Line("That is the folder Nightreign Helper will read from."),
        ),
        buttons=(ANOTHER_BUTTON, Button("Use this folder", USE)),
        escape=QUIT,
        about=verdict,
    )


def found_it(verdict: Verdict) -> str:
    """The confirmation: C2 for the one-level descent, C1 for everything else.

    C2 says `inside the folder you picked`, so it may only be said where that
    is the whole news. After a C3 the user has just read both paths and
    agreed to them, and C1 -- which claims no relation at all -- is what
    belongs under that (AK-242). That is why a descent of two levels or more
    gets C1 as well, although the folder really is inside his: it is a folder
    he was asked about, not one he showed.
    """
    if verdict.where == INSIDE:
        return (f"Found your game in {os.fspath(verdict.found)}, inside the "
                "folder you picked.")
    return f"Found your game in {os.fspath(verdict.found)}"


def _where_it_sits(found, picked) -> str:
    """Did the search stay inside the tree the user saw, how far in, or did
    it leave?

    Held against the folder **as he was shown it**, and against the
    **resolved** result (T-146, SEC-030). That is what makes a junction
    inside the picked folder a leaving: it resolves to somewhere he never
    saw, and that is precisely the case the question C3 exists for.

    Compared as parts rather than as text, so that a separator or a trailing
    slash cannot decide it, and through `normcase`, because Windows spells
    one folder in more than one way and none of them is a different folder.
    Counting the parts is also what the distance is: the levels between the
    two folders, and nothing the search has to hand out to say it.
    """
    seen = pathlib.PurePath(os.path.normcase(os.path.abspath(picked))).parts
    landed = pathlib.PurePath(os.path.normcase(os.path.abspath(found))).parts
    if landed == seen:
        return SAME
    if landed[:len(seen)] != seen:
        return OUTSIDE
    levels = len(landed) - len(seen)
    return INSIDE if levels <= LEVELS_TAKEN_ON_TRUST else DEEPER


def look_at(picked) -> Verdict:
    """Search around the folder the user picked, and say what came of it.

    Both stages of section 4.3 in one answer: `found` is stage 1 (there is an
    installed game here, and this is the folder holding it), `named` is stage
    2 (it is named after this game), and `where` is what the confirmation and
    the question C3 turn on.
    """
    picked = pathlib.Path(picked)
    found = gamefiles.search_from(picked)
    if found is None:
        return Verdict(picked, None, False, OUTSIDE)
    return Verdict(picked, found, gamefiles.is_named_nightreign(found),
                   _where_it_sits(found, picked))


@dataclasses.dataclass(frozen=True)
class Settled:
    """How the question ended: what was confirmed, and whether to go on."""

    game: pathlib.Path | None
    go_on: bool
    said: str = ""


def _confirm(verdict: Verdict) -> Settled:
    """Keep the folder the user confirmed, before anything is built.

    **The only line in the program that writes `paths/game`** (M3, T-144).
    That keeps a folder the user never confirmed from being *remembered* as
    one he did -- it does not stand between a folder and the library run out
    of it this session; `looks_like_the_game` does that (SEC-031), on every
    route that hands a folder to the build, confirmed or automatic alike.
    Kept before the build begins, not after, so that a crash during the
    minute does not cost the answer (AK-117).
    """
    gamepath.remember_game(verdict.found)
    return Settled(verdict.found, True, found_it(verdict))


def the_opening_panel(remembered, day: str) -> Panel:
    """Which of A1, A2 and A3 the question starts with (sections 3 and 6)."""
    if remembered is None:
        return a1()
    return a3(remembered, day) if day else a2(remembered)


def where_to_start_looking(remembered) -> pathlib.Path | None:
    """The nearest place to the goal that exists, or nowhere (section 4.1).

    Nowhere means "This PC": an empty start is what opens the system dialog
    there, and a start that does not exist would open it anywhere at all.
    """
    places = []
    if remembered is not None:
        places += [pathlib.Path(remembered), pathlib.Path(remembered).parent]
    places += gamefiles.steam_common_folders()
    places.append(STEAM_COMMON)
    for place in places:
        try:
            if place.is_dir():
                return place
        except OSError:  # an unplugged drive is not a place to start in
            continue
    return None


def settle_the_game_folder(ask, pick_a_folder, *, remembered=None,
                           day: str = "") -> Settled:
    """Ask until there is an answer: the whole of section 3.1.

    `ask(panel)` puts one panel on the screen and comes back with the answer
    of the button that was pressed; `pick_a_folder(start_at)` opens the
    system folder dialog and returns what was picked, or None if it was
    cancelled. Both are handed in, so every decision this flow makes can be
    driven and read without a screen -- the same seam `Planner` has for the
    reading of the save.

    The loop never ends by itself: `Quit`, Escape and the window cross end
    the program, and nothing else does (AK-114).
    """
    panel = the_opening_panel(remembered, day)
    start_at = where_to_start_looking(remembered)
    while True:
        answer = ask(panel)
        if answer == QUIT:
            return Settled(None, False)
        if answer == CARRY_ON:
            return Settled(None, True)
        if answer == USE:
            return _confirm(panel.about)

        picked = pick_a_folder(start_at)
        if picked is None:
            # AK-115: back to the panel he left, in the state he left it.
            continue
        # The next dialog opens where this one did, not at the folder the
        # search resolved to: he wants to go somewhere else from here (3.3).
        start_at = pathlib.Path(picked)
        verdict = look_at(picked)
        if verdict.found is None:
            panel = e1(picked)
        elif not verdict.named:
            panel = w1(verdict)
        elif verdict.where == OUTSIDE:
            # The search left the tree he pointed at (AK-232).
            panel = c3(verdict)
        elif verdict.where == DEEPER:
            # It stayed in his tree, but came back with a folder two levels
            # down or more -- one he was never shown (AK-246, SEC-032).
            panel = c3(verdict)
        else:
            return _confirm(verdict)


def _the_day(when: float) -> str:
    """A day a player can read, in English and without a leading zero."""
    day = datetime.datetime.fromtimestamp(when)
    return f"{day.day} {day:%B %Y}"


def the_day_the_data_was_read() -> str:
    """The day the snapshot was written, or "" when there is none.

    The only honest thing that can be said about how old the numbers are
    (section 6), and the reason A3 can offer to carry on at all.
    """
    try:
        return _the_day(bundled_path().stat().st_mtime)
    except OSError:
        return ""


def a_question_is_due() -> bool:
    """Is there anything to ask, on a machine with no game folder?

    Yes when a folder was remembered -- A2 and A3 name it, and the player is
    owed the news that it is gone. Yes when there is no data either, which is
    the dead end A15 is about (AK-108).

    No in the one remaining case: nothing was ever confirmed and there is
    usable data anyway -- a snapshot beside the package in a source tree, or
    one built before the game was uninstalled. Such a machine works today
    without a word being said, A2 and A3 have no path to print on it, and A1
    would block a program that has everything it needs.
    """
    return gamepath.remembered_game() is not None or not bundled_path().exists()


class _Builder(QObject):
    """Runs the extraction off the GUI thread."""

    progress = Signal(str)
    finished = Signal(str)  # empty on success, else the error text

    def __init__(self, game: pathlib.Path, steps: list[str]) -> None:
        super().__init__()
        self.game = game
        self.steps = steps

    def run(self) -> None:
        try:
            defs = defs_dir()
            if defs is None:
                raise FileNotFoundError(
                    "The param definitions are missing, so the game cannot be "
                    "read. Reinstalling should restore them."
                )

            paths.cache_dir().mkdir(parents=True, exist_ok=True)

            if "snapshot" in self.steps:
                from nrdata import extract

                self.progress.emit("Reading the game's data tables ...")
                extract.write_snapshot(self.game, defs, paths.snapshot_path())

            if "icons" in self.steps:
                from nrdata import iconbuild

                self.progress.emit("Decoding artwork ...")
                iconbuild.build(
                    self.game,
                    defs,
                    paths.icons_dir(),
                    report=lambda line: self.progress.emit(line.strip()),
                )
        except Exception as exc:  # noqa: BLE001 - reported in the dialog
            traceback.print_exc()
            self.finished.emit(str(exc) or exc.__class__.__name__)
            return

        self.finished.emit("")


class _Window(QWidget):
    """The one window of the first run, in either of its two states.

    Question first, then the build, at the same width, so that answering does
    not make the screen jump (AK-118, section 3).

    **The two states are different kinds of window, and that is the point.**
    The build state is a splash: no title bar, no taskbar entry, nothing to
    press. That is right for a minute nobody can shorten and wrong for a
    question, because a question opens the system folder dialog -- which can
    come up behind it, leaving a player looking for this program in a taskbar
    it is not in.

    Deliberately not a QProgressDialog in the build state: there is no
    cancelling a half-built cache into something usable, so there should be
    no cancel button offering to.
    """

    def __init__(self) -> None:
        super().__init__(None, Qt.WindowType.SplashScreen)
        self.setWindowTitle(WINDOW_TITLE)
        # One page at a time inside a frame that adds nothing of its own. A
        # state gets a page of its own rather than the last one emptied out:
        # a layout whose items have just been taken out answers -1 for its
        # height until the deleted widgets are really gone, which is an event
        # cycle away -- and the second panel of a session came up at the
        # 230 px floor with its text cut off (measured, AK-129).
        self._frame = QVBoxLayout(self)
        self._frame.setContentsMargins(0, 0, 0, 0)
        self._frame.setSpacing(0)
        self._page: QWidget | None = None
        self._body: QVBoxLayout | None = None

        self.status = QLabel("")
        self.shortcut_check = None
        #: The buttons of the question on screen, by the answer each gives.
        self.buttons: dict[str, QPushButton] = {}
        self._asking = False
        self._answer = ""
        self._escape = ""
        self._default = ""
        self._loop: QEventLoop | None = None

    # --- the question state ----------------------------------------------

    def show_the_question(self, panel: Panel) -> None:
        """Lay one panel out and put the window in front, as a question.

        Order from section 3, top to bottom: headline, the words, the path,
        the buttons, the footer. The answer starts out as the one Escape
        gives, so a window that goes away by any means at all has answered
        something, and the flow never waits on a window that is gone.
        """
        self._new_page()
        self.buttons = {}
        self._asking = True
        self._escape = panel.escape
        self._default = panel.default.answer
        self._answer = panel.escape

        heading = QLabel(panel.headline)
        font = heading.font()
        font.setPointSize(font.pointSize() + 3)
        font.setBold(True)
        heading.setFont(font)
        heading.setWordWrap(True)
        if panel.rejects:
            heading.setStyleSheet(f"color: {BAD}")
        self._body.addWidget(heading)

        for line in panel.lines:
            label = QLabel(_wrappable(line))
            label.setTextFormat(Qt.TextFormat.PlainText)
            label.setWordWrap(True)
            self._body.addWidget(label)

        self._body.addStretch(1)

        row = QHBoxLayout()
        row.addStretch(1)
        for button in panel.buttons:
            pressed = QPushButton(button.label)
            # Off, so that Return reaches this window instead of whichever
            # button happens to hold the focus: one place decides what the
            # default is, and it is the panel (section 9).
            pressed.setAutoDefault(False)
            pressed.clicked.connect(
                lambda _checked=False, answer=button.answer: self.press(answer))
            row.addWidget(pressed)
            self.buttons[button.answer] = pressed
        self.buttons[panel.default.answer].setDefault(True)
        self._body.addLayout(row)

        if panel.footer:
            footer = QLabel(panel.footer)
            footer.setWordWrap(True)
            footer.setStyleSheet(f"color: {MUTED}; font-size: 10px")
            self._body.addWidget(footer)

        self.setWindowFlags(Qt.WindowType.Window)
        self.setFixedWidth(PANEL_WIDTH)
        self.setFixedHeight(self._height_of_the_content())
        self.show()
        self.raise_()
        self.activateWindow()
        # After the window is up, not before: changing the window flags makes
        # Qt build a new native window, and a focus set on the old one is
        # gone with it -- which would leave a keyboard-only player pressing
        # Enter into nothing.
        self.buttons[panel.default.answer].setFocus()

    def ask(self, panel: Panel) -> str:
        """Show one question and wait for the answer to it."""
        self.show_the_question(panel)
        loop = QEventLoop()
        self._loop = loop
        try:
            loop.exec()
        finally:
            self._loop = None
        return self._answer

    def _height_of_the_content(self) -> int:
        """How tall this panel has to be at `PANEL_WIDTH`, and never shorter.

        Asked of the laid-out content at *that* width rather than of
        `sizeHint`: the hint of a word-wrapped label is its height on one
        long line, so `adjustSize` leaves a window too short for the text it
        wraps into. Measured offscreen at 100 %: five of the six panels came
        up at the 230 px floor with sentences cut off inside them (AK-129).
        """
        self._body.activate()
        return max(LEAST_PANEL_HEIGHT, self._body.heightForWidth(PANEL_WIDTH))

    @property
    def answer(self) -> str:
        """What the question on screen has been answered with so far."""
        return self._answer

    def press(self, answer: str) -> None:
        """Answer the question on screen, as a button press does."""
        self._answer = answer
        if self._loop is not None:
            self._loop.quit()

    def keyPressEvent(self, event) -> None:
        """Enter presses the default button, Escape leaves (section 9)."""
        if not self._asking:
            super().keyPressEvent(event)
            return
        if event.key() == Qt.Key.Key_Escape:
            self.press(self._escape)
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.press(self._default)
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event) -> None:
        """The window cross means what Escape means (section 9, AK-116)."""
        if self._asking:
            self.press(self._escape)
        super().closeEvent(event)

    def _new_page(self) -> None:
        """Put an empty page in the frame, and the one before it out."""
        before = self._page
        self._page = QWidget(self)
        self._body = QVBoxLayout(self._page)
        self._body.setContentsMargins(SIDE_MARGIN, TOP_MARGIN,
                                      SIDE_MARGIN, TOP_MARGIN)
        self._body.setSpacing(10)
        self._frame.addWidget(self._page)
        if before is not None:
            self._frame.removeWidget(before)
            before.setParent(None)
            before.deleteLater()

    # --- the build state --------------------------------------------------

    def show_the_build(self, first_time: bool, said: str = "") -> None:
        """Turn into the progress panel: what this window has always been.

        `said` is the confirmation C1 or C2, when a folder was just picked.
        It stands in `GOOD` above the bar and is the whole of the middle step
        of "question, confirmation, build": there is no click between it and
        the build (AK-118).
        """
        self._new_page()
        self.buttons = {}
        self._asking = False

        # The rebuild is no longer only for a patched game -- upgrading the
        # tool itself can need one too -- so the wording says what is being
        # done rather than guessing at the reason for it.
        headline = (
            "Setting up Nightreign Helper"
            if first_time
            else "Refreshing your game data"
        )
        detail = (
            "Reading your installation. This happens once, and takes about a "
            "minute."
            if first_time
            else "Re-reading your installation so the numbers are up to date."
        )

        layout = self._body

        title = QLabel(headline)
        font = title.font()
        font.setPointSize(font.pointSize() + 3)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        note = QLabel(detail)
        note.setWordWrap(True)
        layout.addWidget(note)

        confirmation = None
        if said:
            confirmation = QLabel(said)
            confirmation.setWordWrap(True)
            confirmation.setStyleSheet(f"color: {GOOD}")
            layout.addWidget(confirmation)

        bar = QProgressBar()
        bar.setRange(0, 0)  # no total is knowable, so keep it indeterminate
        bar.setTextVisible(False)
        layout.addWidget(bar)

        self.status = QLabel("")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)

        # This minute of setup is the closest thing the program has to being
        # installed, so it is the natural place to offer what an installer
        # would: an entry in the Start Menu. Offered rather than done, and only
        # on the first run -- a rebuild after a patch is not an install, and
        # putting the shortcut back after someone deleted it would be a program
        # overruling its user.
        #
        # Ticked by default. It is a single file in the user's own profile,
        # trivially undone from inside the program or by deleting it, and
        # someone who has just downloaded a tool almost always does want to be
        # able to find it again.
        self.shortcut_check = None
        if first_time and shortcut.available():
            self.shortcut_check = QCheckBox("Add to my Start Menu")
            self.shortcut_check.setChecked(True)
            self.shortcut_check.setToolTip(
                "Creates one shortcut in your own Start Menu. No admin "
                "rights, nothing installed, and removable from inside the "
                "program at any time."
            )
            layout.addWidget(self.shortcut_check)

        # Back to the splash it has always been, at the height it has always
        # had -- plus whatever the confirmation line needs, which is measured
        # rather than guessed at: a long path wraps.
        extra = 0
        if confirmation is not None:
            extra = (confirmation.heightForWidth(PANEL_WIDTH - 2 * SIDE_MARGIN)
                     + layout.spacing())
        self.setWindowFlags(Qt.WindowType.SplashScreen)
        self.setFixedSize(PANEL_WIDTH, (190 if first_time else 150) + extra)
        self.show()

    def wants_shortcut(self) -> bool:
        return bool(self.shortcut_check and self.shortcut_check.isChecked())


def _wrappable(line: Line) -> str:
    """The line as it is set: a path breaks after its separators.

    A label that wraps breaks at spaces, and a Windows path has none -- so it
    stays on one line and runs out past the edge of a 460 px window, which is
    the one thing AK-129 says a path line may not do. A zero-width space
    after each separator puts the break where it belongs anyway. Nothing a
    player can see changes, and neither does `Line.text`, which is what the
    wording is held against.
    """
    if line.kind != PATH:
        return line.text
    return (line.text.replace("\\", "\\" + BREAK_HERE)
            .replace("/", "/" + BREAK_HERE))


def _pick_a_folder(parent, start_at) -> pathlib.Path | None:
    """The system's own folder dialog, opened as near the goal as may be.

    The native one on purpose (section 9): it arrives in the light Windows
    dress while this program is dark, and it is still the dialog the player
    knows from everything else on his machine -- a dark rebuild of it loses
    his quick-access places, his network drives and his OneDrive.

    The caption is left to Qt, which supplies one in the language of his
    Windows. Writing one here would put an English sentence where his own
    system has its own word; A8 is about this program's texts, not Qt's.
    """
    picked = QFileDialog.getExistingDirectory(
        parent, "", "" if start_at is None else os.fspath(start_at),
        QFileDialog.Option.ShowDirsOnly)
    return pathlib.Path(picked) if picked else None


def ensure_data(game: pathlib.Path | None) -> str | None:
    """Build whatever is missing, showing progress. Returns an error or None.

    Returning None also covers "nothing needed to be done", which is the
    normal case on every launch after the first.
    """
    return _build_what_is_missing(game, None)


def _build_what_is_missing(game: pathlib.Path | None, window: _Window | None,
                           said: str = "") -> str | None:
    """The build state, in the window the question was asked in if there was one."""
    steps = what_is_needed(game)
    if not steps or game is None:
        if window is not None:
            window.close()
        return None

    if window is None:
        window = _Window()
    window.show_the_build(
        first_time="snapshot" in steps and not bundled_path().exists(),
        said=said)
    QApplication.processEvents()

    thread = QThread()
    builder = _Builder(game, steps)
    builder.moveToThread(thread)

    outcome: dict[str, str] = {}
    thread.started.connect(builder.run)
    builder.progress.connect(window.status.setText)
    builder.finished.connect(lambda err: outcome.setdefault("error", err))
    builder.finished.connect(thread.quit)

    thread.start()
    while not thread.wait(50):
        QApplication.processEvents()

    # Acted on after the build rather than before it, so a setup that fails
    # does not leave a Start Menu entry pointing at a program that cannot run.
    # A shortcut that cannot be written is not worth stopping for or reporting
    # here: the data is what the user is waiting on, and the button in the main
    # window says plainly whether the entry exists.
    if not outcome.get("error") and window.wants_shortcut():
        shortcut.create()

    window.close()
    return outcome.get("error") or None


@dataclasses.dataclass(frozen=True)
class FirstRun:
    """What the first run settled: where to read, and whether to go on."""

    game: pathlib.Path | None
    go_on: bool
    error: str | None = None


def run(game: pathlib.Path | None) -> FirstRun:
    """Get this machine to readable data, asking for the folder if need be.

    `game` is what the resolution point made of the remembered folder and the
    automatic route (`gamepath.resolve_game`). None means neither had an
    answer, and that used to be the end of the program: a `QMessageBox` and a
    return code. It is now the question A15 asks (AK-108).

    Question, confirmation, build -- one window, in that order (section 3).
    `go_on` is False only where the user said so himself: `Quit`, Escape or
    the window cross, and never as the outcome of a failure (AK-114).
    """
    window = None
    said = ""
    if game is None and a_question_is_due():
        window = _Window()
        settled = settle_the_game_folder(
            window.ask,
            lambda start_at: _pick_a_folder(window, start_at),
            remembered=gamepath.remembered_game(),
            day=the_day_the_data_was_read(),
        )
        if not settled.go_on:
            window.close()
            return FirstRun(None, False)
        game, said = settled.game, settled.said

    return FirstRun(game, True, _build_what_is_missing(game, window, said))
