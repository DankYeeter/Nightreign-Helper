"""The first run promises no duration it cannot keep (`UI_SPEC` T-178, AK-253 to AK-255).

**What was wrong.** The window said *"This happens once, and takes about a
minute."* Four measurements of the same build, on the same machine and the
same game, came back at 107 s, at 163-283 s and twice at about five minutes
(QA-198, T-176, T-177). Every one of them is longer than the promise, and the
spread has no cause anybody has measured -- so the mistake is naming a figure
at all, not naming the wrong one, and no invented reason ("on a slow drive")
may take its place.

**What replaces it, and what deliberately does not.** The bar stays
indeterminate. The steps are two, and a bar out of two steps stands on 0 for
the larger part of the wait and then jumps; the split between them is a guess
in a docstring; and the fine messages underneath are not a fixed number (one
only with DLC, one per Nightfarer without a portrait). An estimate that is
wrong is worse than none. What the player gets instead is the order of
magnitude in words and the line that keeps changing -- the part the
`power-user` singled out as *"better than a silent progress bar"*.

**The wording is transcribed out of `UI_SPEC` T-178 §8**, not imported from
`nrplanner.firstrun`: a case that compared the window against the module it
came from would be green whatever either of them said. W-C is transcribed a
second time in `test_first_run_panel.py`, with the rest of that panel.
"""

from __future__ import annotations

import inspect
import re

import pytest
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QCheckBox, QLabel, QProgressBar

from nrplanner import firstrun
from tests import rendered
from tests.test_game_dir_recognition import make_game

# --- the wording, transcribed out of UI_SPEC T-178 §8 ---------------------

W_A = ("Reading your installation. This happens once, and takes minutes "
       "rather than seconds — sometimes several. The line below changes as "
       "it goes.")

W_B = ("Re-reading your installation so the numbers are up to date. This "
       "takes minutes rather than seconds — sometimes several. The line "
       "below changes as it goes.")

W_C = ("Its folder is not named after ELDEN RING NIGHTREIGN, so this may be "
       "a different game. Reading it takes minutes, and every number would "
       "be wrong.")

#: What the two lines said until T-179, kept as the positive control of the
#: search below: a mask that does not strike these two has not been reading
#: the texts it claims to read.
WAS_SAID_BEFORE = (
    "Reading your installation. This happens once, and takes about a minute.",
    "Its folder is not named after ELDEN RING NIGHTREIGN, so this may be a "
    "different game. Reading it takes about a minute, and every number would "
    "be wrong.",
)

#: A figure of time, however it is spelled: `about a minute`, `takes a
#: minute`, and any digit standing immediately before a unit of time.
A_FIXED_DURATION = re.compile(
    r"about a minute|takes a minute|\d+\s*(seconds?|minutes?|hours?)",
    re.IGNORECASE)

#: The other three ways to claim progress nobody can compute (AK-254).
INVENTED_PROGRESS = re.compile(
    r"\d+\s*%|left\b|remaining|elapsed|running for|step \d+", re.IGNORECASE)


def names_a_duration(text: str) -> bool:
    return bool(A_FIXED_DURATION.search(text))


# --- what this module puts on a screen ------------------------------------

def a_verdict(tmp_path):
    picked = tmp_path / "picked"
    picked.mkdir(exist_ok=True)
    return firstrun.Verdict(picked, make_game(tmp_path / "game"), True,
                            firstrun.INSIDE)


def every_panel(tmp_path) -> list:
    """Every question this module can put on the screen.

    Enumerated by hand and then checked against the module, so that a panel
    added tomorrow fails this file instead of slipping past the sweep below.
    """
    verdict = a_verdict(tmp_path)
    remembered = tmp_path / "remembered"
    panels = [firstrun.a1(), firstrun.a2(remembered),
              firstrun.a3(remembered, "12 March"),
              firstrun.e1(tmp_path / "picked"), firstrun.w1(verdict),
              firstrun.c3(verdict),
              firstrun.the_opening_panel(remembered, "12 March")]
    made_here = {"a1", "a2", "a3", "e1", "w1", "c3", "the_opening_panel"}
    in_the_module = {
        name for name, function in vars(firstrun).items()
        if inspect.isfunction(function)
        and inspect.signature(function).return_annotation == "Panel"}
    assert in_the_module == made_here, in_the_module ^ made_here
    return panels


def the_words_of(panel) -> list[str]:
    return [panel.headline, *(line.text for line in panel.lines),
            *(button.label for button in panel.buttons),
            panel.footer]


def a_window_in_the_build_state(first_time: bool, said: str = ""):
    window = firstrun._Window()
    window.show_the_build(first_time=first_time, said=said)
    rendered.settle(2)
    return window


def everything_written_in(window) -> list[str]:
    """Every word of the window: labels, the offer, and what it explains."""
    words = [label.text() for label in window.findChildren(QLabel)]
    for box in window.findChildren(QCheckBox):
        words += [box.text(), box.toolTip()]
    return [word for word in words if word]


def shut(window) -> None:
    window.close()
    window.deleteLater()
    rendered.settle(2)


# -- AK-253: no duration, in either state or in the question ---------------

@pytest.mark.parametrize("first_time, expected", [(True, W_A), (False, W_B)])
def test_the_build_state_says_how_long_without_naming_a_length(
        qapp, first_time, expected):
    """AK-253's first half: W-A and W-B, word for word.

    `minutes rather than seconds` is true of all four measurements and would
    still be true at ten minutes; `sometimes several` errs in the direction
    that costs nothing.
    """
    window = a_window_in_the_build_state(first_time)
    try:
        assert expected in everything_written_in(window)
        # And it says nothing about why, because nobody knows why: the spread
        # was measured on one machine with one game.
        for word in everything_written_in(window):
            assert "drive" not in word.lower()
            assert "your machine" not in word.lower()
            assert "your pc" not in word.lower()
    finally:
        shut(window)


def test_no_text_this_module_shows_names_a_duration(qapp, tmp_path):
    """AK-253's second half, as a property of the module rather than of a line.

    Every question, both build states and the confirmation, swept with one
    mask. The two assertions above it are the control the criterion asks
    for: the mask has to strike the two sentences that stood here until
    T-179, or it is measuring nothing but itself.
    """
    assert [names_a_duration(said) for said in WAS_SAID_BEFORE] == [True, True]
    assert not names_a_duration(W_A)

    shown = []
    for panel in every_panel(tmp_path):
        shown += the_words_of(panel)
    shown.append(firstrun.found_it(a_verdict(tmp_path)))
    for first_time in (True, False):
        window = a_window_in_the_build_state(first_time, said="Found it")
        try:
            shown += everything_written_in(window)
        finally:
            shut(window)

    # The collection really reaches the screen texts it claims to: the three
    # sentences this task rewrote are all in it.
    assert W_A in shown and W_B in shown and W_C in shown
    assert not [word for word in shown if names_a_duration(word)]


# -- AK-254: no invented progress, and the line that stays ------------------

def test_the_bar_promises_no_progress_it_cannot_compute(qapp):
    """AK-254's first half: indeterminate, silent, and no figure beside it."""
    window = a_window_in_the_build_state(first_time=True)
    try:
        bars = window.findChildren(QProgressBar)
        assert len(bars) == 1
        assert (bars[0].minimum(), bars[0].maximum()) == (0, 0)
        assert not bars[0].isTextVisible()
        for word in everything_written_in(window):
            assert not INVENTED_PROGRESS.search(word), word
    finally:
        shut(window)


#: The build's own messages, in the order a run gives them: the two of
#: `_Builder`, then `iconbuild`'s, one of them the DLC line that only some
#: machines ever see.
TODAYS_MESSAGES = (
    "Reading the game's data tables ...",
    "Decoding artwork ...",
    "hero 3: portrait 900 missing",
    "portraits: 10",
    "item icons: 713 of 786 requested",
    "boss icons: 18 of 18 requested",
    "ui sprites: 6 of 6",
    "DLC illustrations found: 4",
    "verification: every written icon reads back",
    "character variants: 41 across 10 Nightfarers",
    "icon pack: 21.4 MB in icons",
)


class _BuilderThatOnlyTalks(QObject):
    """Stands where `_Builder` stands, and says what a build says.

    Same two signals, same thread, same `run` -- so the messages travel the
    real way from the worker to the line under the bar, across the thread
    boundary and through whatever the window does with them.
    """

    progress = Signal(str)
    finished = Signal(str)

    def __init__(self, game, steps) -> None:
        super().__init__()
        self.game = game
        self.steps = steps

    def run(self) -> None:
        for message in TODAYS_MESSAGES:
            self.progress.emit(message)
        self.finished.emit("")


class _WindowThatRemembersItsLine(firstrun._Window):
    """The real window, with the line under the bar writing down what it is told."""

    def show_the_build(self, first_time: bool, said: str = "") -> None:
        super().show_the_build(first_time, said)
        self.said_in_the_line: list[str] = []
        write = self.status.setText

        def remember(text: str) -> None:
            self.said_in_the_line.append(text)
            write(text)

        self.status.setText = remember


def test_every_message_reaches_the_line_word_for_word_and_in_order(
        qapp, monkeypatch, tmp_path):
    """AK-254's second half. The part the `power-user` asked to keep.

    Counted against a literal: as many messages in the line as the build gave
    out, in the order it gave them, unshortened. A bar with a range would be
    read off the same list -- which is what the killing mutation does, and why
    the count and the order are both asserted here.
    """
    game = make_game(tmp_path / "game")
    monkeypatch.setattr(firstrun, "_Builder", _BuilderThatOnlyTalks)
    monkeypatch.setattr(firstrun, "what_is_needed",
                        lambda _game: ["snapshot", "icons"])
    monkeypatch.setattr(firstrun, "bundled_path",
                        lambda: tmp_path / "nothing built yet.json")
    # The offer of a Start Menu entry is ticked by default, and a case is not
    # allowed to put one anywhere: this is the one place the build writes
    # outside its own cache.
    written = []
    monkeypatch.setattr(firstrun.shortcut, "create", lambda: written.append(1))

    window = _WindowThatRemembersItsLine()
    error = firstrun._build_what_is_missing(game, window)

    assert error is None
    assert window.said_in_the_line == list(TODAYS_MESSAGES)
    assert len(window.said_in_the_line) == 11
    window.deleteLater()
    rendered.settle(2)


# -- AK-255: nothing is cut off ---------------------------------------------

#: What the build state was fixed at before T-179, and what it may never fall
#: below now: the splash it has always been, at the height it has always had.
FLOORS = {True: 190, False: 150}


@pytest.mark.parametrize("first_time", [True, False])
def test_the_build_state_is_as_tall_as_what_it_says(qapp, first_time):
    """AK-255. The height follows the text, and no sentence is cut off.

    The same fault `_height_of_the_content` was written for on the question
    states: the `sizeHint` of a wrapped label is its height on one long line,
    so a window sized by a fixed figure leaves the last line under its own
    bottom edge. Asserted as a relation and not as a figure -- the figures
    are in the task's report, with the platform, the style and the scaling
    they were measured under (L-009).
    """
    window = a_window_in_the_build_state(first_time)
    try:
        assert window.height() >= FLOORS[first_time]
        assert window.width() == firstrun.PANEL_WIDTH

        note = [label for label in window.findChildren(QLabel)
                if label.text() in (W_A, W_B)]
        assert len(note) == 1, "the explaining line is on screen exactly once"
        assert note[0].height() >= note[0].heightForWidth(note[0].width())
        # And it ends above the bottom edge of the window it sits in.
        bottom = note[0].mapTo(window, note[0].rect().bottomLeft()).y()
        assert bottom <= window.height()
    finally:
        shut(window)


def test_a_confirmation_that_wraps_makes_the_window_taller(qapp):
    """AK-255's other half: the C1/C2 line is measured, not guessed at.

    A Steam path has no spaces in it, so the confirmation wraps rather than
    fitting; the window was already growing for it and goes on growing.
    """
    plain = a_window_in_the_build_state(first_time=True)
    tall = a_window_in_the_build_state(
        first_time=True,
        said=r"Found your game in D:\SteamLibrary\steamapps\common\ELDEN "
             r"RING NIGHTREIGN\Game, inside the folder you picked.")
    try:
        assert tall.height() > plain.height()
    finally:
        shut(plain)
        shut(tall)
