"""The first run promises no duration it cannot keep (`UI_SPEC` T-178, AK-253 to AK-255).

**What was wrong.** The window said *"This happens once, and takes about a
minute."* Four measurements of the same build, on the same machine and the
same game, came back at 107 s, at 163-283 s and twice at about five minutes
(QA-198, T-176, T-177). Every one of them is longer than the promise, and the
spread has no cause anybody has measured -- so the mistake is naming a figure
at all, not naming the wrong one, and no invented reason ("on a slow drive")
may take its place.

**What replaces it.** One sentence, the same on a first start and on a
rebuild, with the order of magnitude in words and no figure. Under it a bar
that moves on its own until the build reports, and from then on shows how
much of the work is behind it: the build names that share each time one of
its stages ends, weighted by what the stage took in a measured run. It
counts work done and promises no time left. The build's own messages
("item icons: 713 of 786 requested") are no longer shown: the owner read
them and they told him nothing (15.11.2026).

**The wording is transcribed here**, not imported from `nrplanner.firstrun`:
a case that compared the window against the module it came from would be
green whatever either of them said. W-C is transcribed a second time in
`test_first_run_panel.py`, with the rest of that panel.
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

# --- the wording ----------------------------------------------------------

#: The one sentence of the build state, first start and rebuild alike.
LINE = "Reading your game files, this may take a few minutes."

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

@pytest.mark.parametrize("first_time", [True, False])
def test_the_build_state_says_how_long_without_naming_a_length(
        qapp, first_time):
    """AK-253's first half: one sentence and the offer, nothing else.

    `a few minutes` is true of all four measurements; a figure is not.
    """
    window = a_window_in_the_build_state(first_time)
    try:
        written = everything_written_in(window)
        assert [word for word in written if "Start Menu" not in word
                and "shortcut" not in word] == [LINE]
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
    assert not names_a_duration(LINE)

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
    assert LINE in shown and W_C in shown
    assert not [word for word in shown if names_a_duration(word)]


# -- AK-254: the bar shows work done, and nothing else ----------------------

def test_the_bar_moves_on_its_own_until_the_build_reports(qapp):
    """Indeterminate at first, silent throughout, and no figure beside it."""
    window = a_window_in_the_build_state(first_time=True)
    try:
        bars = window.findChildren(QProgressBar)
        assert len(bars) == 1
        assert (bars[0].minimum(), bars[0].maximum()) == (0, 0)
        assert not bars[0].isTextVisible()
        for word in everything_written_in(window):
            assert not INVENTED_PROGRESS.search(word), word

        window.show_the_share(420)
        assert (bars[0].maximum(), bars[0].value()) == (firstrun.SHARES, 420)
    finally:
        shut(window)


class _BuilderThatOnlyReports(QObject):
    """Stands where `_Builder` stands: same signals, same thread, same `run`."""

    share = Signal(int)
    finished = Signal(str)

    def __init__(self, game, steps) -> None:
        super().__init__()

    def run(self) -> None:
        for done in (130, 520, 1000):
            self.share.emit(done)
        self.finished.emit("")


class _WindowThatRemembersItsShares(firstrun._Window):
    """The real window, writing down what its bar is told.

    A method of the window and not a function put in its place: a signal
    connected to a plain function runs it in the thread that emits, and
    that is the builder's.
    """

    def show_the_share(self, done: int) -> None:
        self.__dict__.setdefault("seen", []).append(done)
        super().show_the_share(done)


def test_what_the_build_reports_reaches_the_bar(qapp, monkeypatch, tmp_path):
    """Across the thread boundary, in order, and into the one bar."""
    game = make_game(tmp_path / "game")
    monkeypatch.setattr(firstrun, "_Builder", _BuilderThatOnlyReports)
    monkeypatch.setattr(firstrun, "what_is_needed",
                        lambda _game: ["snapshot", "icons"])
    monkeypatch.setattr(firstrun, "bundled_path",
                        lambda: tmp_path / "nothing built yet.json")
    # The offer of a Start Menu entry is ticked by default, and a case is not
    # allowed to put one anywhere: this is the one place the build writes
    # outside its own cache.
    monkeypatch.setattr(firstrun.shortcut, "create", lambda: None)

    window = _WindowThatRemembersItsShares()

    assert firstrun._build_what_is_missing(game, window) is None
    assert window.seen == [130, 520, 1000]
    assert window.bar.value() == window.bar.maximum() == firstrun.SHARES
    window.deleteLater()
    rendered.settle(2)


@pytest.mark.parametrize("steps", [["snapshot", "icons"], ["snapshot"],
                                   ["icons"]])
def test_the_real_builder_ends_on_a_full_bar_and_never_goes_back(
        qapp, monkeypatch, tmp_path, steps):
    """Whichever steps are due, the shares rise and the last one is all of it."""
    from nrdata import extract, iconbuild

    def a_snapshot(_game, _defs, _out, progress):
        for share in (extract.P_ARCHIVES, extract.P_EFFECTS,
                      extract.P_TABLES, extract.P_BOSSES):
            progress(share)

    def an_icon_pack(_game, _defs, _out, progress):
        for share in (iconbuild.P_PORTRAITS, iconbuild.P_ITEMS,
                      iconbuild.P_SPRITES, iconbuild.P_VERIFIED,
                      iconbuild.P_BACKDROPS, 1.0):
            progress(share)

    monkeypatch.setattr(extract, "write_snapshot", a_snapshot)
    monkeypatch.setattr(iconbuild, "build", an_icon_pack)
    monkeypatch.setattr(firstrun, "defs_dir", lambda: tmp_path)
    monkeypatch.setattr(firstrun.paths, "cache_dir", lambda: tmp_path / "c")

    builder = firstrun._Builder(tmp_path / "game", steps)
    seen, ended = [], []
    builder.share.connect(seen.append)
    builder.finished.connect(ended.append)
    builder.run()

    assert ended == [""]
    assert seen == sorted(seen) and len(set(seen)) > 4
    assert 0 < seen[0] and seen[-1] == firstrun.SHARES


# -- AK-255: nothing is cut off ---------------------------------------------

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
        assert window.width() == firstrun.PANEL_WIDTH

        note = [label for label in window.findChildren(QLabel)
                if label.text() == LINE]
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
