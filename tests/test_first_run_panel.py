"""The panel that asks where the game is (A15, V2).

`UI_SPEC` "Der Erststart mit Ordnerauswahl" and its three addenda: AK-106 to
AK-132, AK-230 to AK-239 (T-145, SEC-027) and AK-240 to AK-242 (T-146). The
Qt-free half underneath -- stage 1, stage 2 and the search itself -- is
`test_game_dir_recognition.py` and is not repeated here.

**Everything is driven through the seam, never around it.**
`settle_the_game_folder` is handed the two things that need a screen: showing
a panel, and opening the system folder dialog. A case states what the player
answers and what he picks, and every decision the flow makes -- which panel
comes next, whether anything is kept, what the confirmation says -- travels
its real way. Only the cases about the window itself build one.

**The wording is transcribed a second time here**, out of `UI_SPEC` section 7
rather than out of `firstrun`. A test that compared the panel against the
module it came from would be green whatever either of them said; two
transcriptions disagree the moment one of them is wrong.
"""

from __future__ import annotations

import pathlib
import re

import pytest
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QLabel

from nrplanner import firstrun, gamepath
from tests import conftest, rendered
from tests.test_game_dir_recognition import make_game

# --- the wording, transcribed out of UI_SPEC section 7 --------------------

A1 = (
    "Where is ELDEN RING NIGHTREIGN installed?",
    "Nightreign Helper reads every number it shows out of your own copy of "
    "the game, and it could not find one on this PC.",
    "In Steam, right-click ELDEN RING NIGHTREIGN in your library and choose "
    "Manage, then Browse local files. Pick the folder that opens.",
    "Nothing in that folder is changed, moved or deleted. To read the game's "
    "files, Nightreign Helper runs a small program out of that folder, so "
    "pick a copy of the game you trust — normally the one you play.",
)
A1_FOOTER = "You can close this and come back later. It will ask again."

E1 = (
    "That folder does not hold a copy of the game.",
    "You picked:",
    "{path}",
    "Nothing inside it looked like an installed game. Pick the folder the "
    "game itself is in: in Steam that is Manage, then Browse local files.",
)

W1 = (
    "This does not look like ELDEN RING NIGHTREIGN.",
    "There is an installed FromSoftware game here:",
    "{path}",
    "Its folder is not named after ELDEN RING NIGHTREIGN, so this may be a "
    "different game. Reading it takes about a minute, and every number would "
    "be wrong.",
    "To read it, Nightreign Helper runs a small program out of this folder, "
    "so only carry on with a copy of the game you installed yourself.",
)

C3 = (
    "Is this your game?",
    "You picked:",
    "{picked}",
    "The game itself is outside that folder, in:",
    "{found}",
    "That is the folder Nightreign Helper will read from.",
)

#: The words no text of this flow may carry (AK-127).
FORBIDDEN = ("regulation.bin", "steamapps", "libraryfolders.vdf", ".sl2",
             "AppData", "Steam ID", "account id", "snapshot", "cache",
             "param", "extract", "%")


def a_panel_reads_as(panel) -> tuple[str, ...]:
    """The panel as a player reads it: headline first, then its lines."""
    return (panel.headline, *(line.text for line in panel.lines))


# --- the player at the panel ---------------------------------------------


class Player:
    """A player answering the panel and picking folders in the dialog.

    Stands where the window and the system dialog stand. Running out of
    answers is an assertion and not a return: a flow that asks once more than
    the case expects has done something the case is about, and swallowing it
    would make "the panel never closes by itself" (AK-114) untestable.
    """

    def __init__(self, answers, picks=()) -> None:
        self.answers = list(answers)
        self.picks = list(picks)
        self.seen = []
        self.opened_at = []

    def ask(self, panel):
        self.seen.append(panel)
        if not self.answers:
            raise LooksLikeAnotherQuestion(panel.name)
        return self.answers.pop(0)

    def pick(self, start_at):
        self.opened_at.append(start_at)
        return self.picks.pop(0) if self.picks else None

    @property
    def panels(self) -> list[str]:
        return [panel.name for panel in self.seen]


class LooksLikeAnotherQuestion(Exception):
    """The flow asked again after the case had said everything it meant to."""


def settle(player, **rest):
    return firstrun.settle_the_game_folder(player.ask, player.pick, **rest)


@pytest.fixture(autouse=True)
def a_store_of_our_own(qapp):
    """Nothing of another case is inherited, and nothing is left behind.

    Through `clear_settings`, which empties the whole test store; no case
    here may call `QSettings.remove` on a `paths/` key, because the scan that
    forbids it (R5) reads the tests as well.
    """
    conftest.clear_settings()
    yield
    conftest.clear_settings()


def an_install(root: pathlib.Path, named: str = "ELDEN RING NIGHTREIGN"):
    """A Steam-shaped tree, and the folder that holds regulation.bin in it."""
    return make_game(root / "common" / named / "Game")


# --- the wording ---------------------------------------------------------


def test_a1_is_word_for_word_the_spec_and_says_a_program_is_run():
    """AK-230, AK-231: the sentence SEC-027 asked for, and no other."""
    assert a_panel_reads_as(firstrun.a1()) == A1
    assert firstrun.a1().footer == A1_FOOTER


def test_w1_carries_the_same_news_a_shade_firmer():
    """AK-230: W1 is the panel nearest the decision, so it says it too."""
    verdict = firstrun.Verdict(pathlib.Path(r"C:\picked"),
                               pathlib.Path(r"C:\picked\Game"), False,
                               firstrun.INSIDE)

    assert a_panel_reads_as(firstrun.w1(verdict)) == tuple(
        line.format(path=r"C:\picked\Game") for line in W1)


def test_e1_names_the_folder_that_was_turned_down():
    assert a_panel_reads_as(firstrun.e1(pathlib.Path(r"C:\nothing"))) == tuple(
        line.format(path=r"C:\nothing") for line in E1)


def test_c3_says_the_game_is_outside_the_folder_that_was_picked():
    """AK-241: the T-146 wording, not the neutral one it replaced."""
    verdict = firstrun.Verdict(pathlib.Path(r"C:\picked\Game\sub"),
                               pathlib.Path(r"C:\picked\Game"), True,
                               firstrun.OUTSIDE)

    assert a_panel_reads_as(firstrun.c3(verdict)) == tuple(
        line.format(picked=r"C:\picked\Game\sub", found=r"C:\picked\Game")
        for line in C3)


def test_the_two_later_panels_name_the_folder_that_is_gone():
    """AK-119, AK-120: A2 blocks, A3 offers the data and its date."""
    gone = pathlib.Path(r"D:\Games\common\ELDEN RING NIGHTREIGN\Game")

    a2 = firstrun.a2(gone)
    a3 = firstrun.a3(gone, "3 September 2026")

    assert a_panel_reads_as(a2) == (
        "Your game is not where it was last time.",
        "Nightreign Helper last read it from:",
        str(gone),
        "That folder is not there now. If the game was moved or reinstalled, "
        "or if it sits on a drive that is not plugged in right now, point "
        "this at the new place.",
    )
    assert a_panel_reads_as(a3) == (
        "Your game is not where it was last time.",
        "Nightreign Helper last read it from:",
        str(gone),
        "You can carry on with what was read on 3 September 2026. Those "
        "numbers stay right until the game is updated.",
    )
    assert [button.label for button in a3.buttons] == [
        "Continue with the data from 3 September 2026", "Choose folder..."]
    assert [button.label for button in a2.buttons] == ["Quit",
                                                       "Choose folder..."]


def test_the_confirmation_says_inside_only_when_it_is_inside():
    """AK-242: C2 for a descent, C1 for a leaving and for the folder itself."""
    game = pathlib.Path(r"C:\common\ELDEN RING NIGHTREIGN\Game")
    picked = pathlib.Path(r"C:\common\ELDEN RING NIGHTREIGN")

    inside = firstrun.found_it(
        firstrun.Verdict(picked, game, True, firstrun.INSIDE))
    same = firstrun.found_it(
        firstrun.Verdict(game, game, True, firstrun.SAME))
    outside = firstrun.found_it(
        firstrun.Verdict(game / "sub", game, True, firstrun.OUTSIDE))

    assert inside == f"Found your game in {game}, inside the folder you picked."
    assert same == f"Found your game in {game}"
    assert outside == f"Found your game in {game}"


def every_panel():
    verdict = firstrun.Verdict(pathlib.Path(r"C:\picked"),
                               pathlib.Path(r"C:\picked\Game"), False,
                               firstrun.INSIDE)
    return {
        "A1": firstrun.a1(),
        "A2": firstrun.a2(pathlib.Path(r"C:\gone")),
        "A3": firstrun.a3(pathlib.Path(r"C:\gone"), "3 September 2026"),
        "E1": firstrun.e1(pathlib.Path(r"C:\nothing")),
        "W1": firstrun.w1(verdict),
        "C3": firstrun.c3(verdict),
    }


@pytest.mark.parametrize("name", sorted(every_panel()))
def test_no_panel_says_a_forbidden_word(name):
    """AK-127. The paths in these panels are the cases' own, not a player's."""
    panel = every_panel()[name]
    written = " ".join((panel.headline, panel.footer,
                        *(line.text for line in panel.lines),
                        *(button.label for button in panel.buttons)))

    assert not [word for word in FORBIDDEN if word.lower() in written.lower()]


@pytest.mark.parametrize("name, answer", [("A1", firstrun.CHOOSE),
                                          ("A2", firstrun.CHOOSE),
                                          ("A3", firstrun.CHOOSE),
                                          ("E1", firstrun.CHOOSE),
                                          ("W1", firstrun.CHOOSE),
                                          ("C3", firstrun.USE)])
def test_the_default_button_is_the_rightmost_one(name, answer):
    """Section 9, AK-113 and AK-234: W1 defaults out, C3 defaults on."""
    panel = every_panel()[name]

    assert panel.default is panel.buttons[-1]
    assert panel.default.answer == answer


@pytest.mark.parametrize("name, answer", [("A1", firstrun.QUIT),
                                          ("A2", firstrun.QUIT),
                                          ("A3", firstrun.CARRY_ON),
                                          ("E1", firstrun.QUIT),
                                          ("W1", firstrun.QUIT),
                                          ("C3", firstrun.QUIT)])
def test_escape_means_the_smallest_loss(name, answer):
    """AK-116 and AK-238: out of the question, losing as little as may be."""
    assert every_panel()[name].escape == answer


def test_the_sentence_that_was_withdrawn_is_nowhere_in_the_program():
    """AK-230: `It is only read.` is gone, and not only from A1.

    Two masks, formulated independently of each other and of the panel: the
    withdrawn sentence, and the claim behind it however it is worded.
    """
    repo = pathlib.Path(__file__).resolve().parents[1]
    sources = [path for folder in ("nrplanner", "nrdata")
               for path in (repo / folder).rglob("*.py")]
    assert sources

    said = [path.name for path in sources
            if "it is only read" in path.read_text(encoding="utf-8").lower()]
    claimed = [path.name for path in sources
               if re.search(r"only read", path.read_text(encoding="utf-8"),
                            re.IGNORECASE)]

    assert said == []
    assert claimed == []


# --- which panel opens the question --------------------------------------


def test_nothing_remembered_opens_with_a1():
    assert firstrun.the_opening_panel(None, "").name == "A1"


def test_a_folder_that_is_gone_opens_with_a2_when_there_is_no_data():
    assert firstrun.the_opening_panel(pathlib.Path(r"C:\gone"), "").name == "A2"


def test_a_folder_that_is_gone_opens_with_a3_when_the_data_is_still_there():
    panel = firstrun.the_opening_panel(pathlib.Path(r"C:\gone"),
                                       "3 September 2026")

    assert panel.name == "A3"


@pytest.mark.parametrize("remembered, data, due", [
    (None, False, True),    # AK-108: the dead end A15 is about
    (None, True, False),    # works today without a word, and goes on doing so
    ("kept", False, True),  # A2
    ("kept", True, True),   # A3
])
def test_when_there_is_something_to_ask(monkeypatch, tmp_path, remembered,
                                        data, due):
    snapshot = tmp_path / "nightreign_data.json"
    if data:
        snapshot.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(firstrun, "bundled_path", lambda: snapshot)
    if remembered:
        gamepath.remember_game(tmp_path / "somewhere")

    assert firstrun.a_question_is_due() is due


# --- the flow ------------------------------------------------------------


def test_the_parent_folder_is_the_ordinary_case_and_costs_no_click(tmp_path):
    """AK-240 and AK-111: a descent resolves and confirms, with no question."""
    game = an_install(tmp_path)
    player = Player([firstrun.CHOOSE], [game.parent])

    settled = settle(player)

    assert player.panels == ["A1"]
    assert settled.game == game
    assert settled.said == (f"Found your game in {game}, inside the folder "
                            "you picked.")


def test_the_game_folder_itself_confirms_without_the_place_it_was_found_in(
        tmp_path):
    """AK-233: resolved equals picked, so C1 and nothing else."""
    game = an_install(tmp_path)
    player = Player([firstrun.CHOOSE], [game])

    settled = settle(player)

    assert player.panels == ["A1"]
    assert settled.said == f"Found your game in {game}"


def test_a_climb_out_of_the_picked_folder_is_asked_about(tmp_path):
    """AK-232: the search had to go up, so the two paths are put to him."""
    game = an_install(tmp_path)
    inside = game / "sound"
    inside.mkdir()
    player = Player([firstrun.CHOOSE, firstrun.USE], [inside])

    settled = settle(player)

    assert player.panels == ["A1", "C3"]
    assert a_panel_reads_as(player.seen[1]) == tuple(
        line.format(picked=str(inside), found=str(game)) for line in C3)
    assert settled.game == game
    assert settled.said == f"Found your game in {game}"


def test_a_junction_out_of_the_picked_folder_is_asked_about(tmp_path):
    """SEC-030, the half this flow answers: the resolved folder is elsewhere.

    The player points at a name; the name leads somewhere he has not seen.
    The search resolves it (T-147), and this is what makes the difference
    visible to him instead of leaving it in the program.
    """
    import _winapi

    game = an_install(tmp_path)
    door = tmp_path / "shortcut to my game"
    try:
        _winapi.CreateJunction(str(game), str(door))
    except (AttributeError, OSError) as exc:  # not Windows, or not permitted
        pytest.skip(f"no junction could be made here: {exc}")
    player = Player([firstrun.CHOOSE, firstrun.USE], [door])

    settled = settle(player)

    assert player.panels == ["A1", "C3"]
    assert settled.game == game


def test_a_folder_with_no_game_in_it_is_turned_down(tmp_path):
    """AK-112, AK-114: E1, and the question stays open."""
    empty = tmp_path / "Documents"
    empty.mkdir()
    player = Player([firstrun.CHOOSE], [empty])

    with pytest.raises(LooksLikeAnotherQuestion):
        settle(player)

    assert player.panels == ["A1", "E1"]
    assert gamepath.remembered_game() is None


def test_a_rejection_does_not_end_the_program_by_itself(tmp_path):
    """AK-114: turned down twice, and it is still asking the third time."""
    empty = tmp_path / "Documents"
    empty.mkdir()
    player = Player([firstrun.CHOOSE, firstrun.CHOOSE], [empty, empty])

    with pytest.raises(LooksLikeAnotherQuestion):
        settle(player)

    assert player.panels == ["A1", "E1", "E1"]


def test_a_game_by_another_name_is_asked_about_and_not_turned_down(tmp_path):
    """AK-113: stage 2 is soft, so W1 -- and `Use this folder anyway` takes."""
    game = an_install(tmp_path, named="my games")
    player = Player([firstrun.CHOOSE, firstrun.USE], [game.parent])

    settled = settle(player)

    assert player.panels == ["A1", "W1"]
    assert settled.game == game
    assert gamepath.remembered_game() == game


def test_at_most_one_question_per_pick(tmp_path):
    """AK-237: the name fails *and* the search climbs -- and W1 is the only one."""
    game = an_install(tmp_path, named="my games")
    inside = game / "sound"
    inside.mkdir()
    player = Player([firstrun.CHOOSE, firstrun.USE], [inside])

    settled = settle(player)

    assert player.panels == ["A1", "W1"]
    assert settled.game == game


def test_cancelling_the_dialog_comes_back_to_the_same_panel(tmp_path):
    """AK-115: nothing kept, nothing said, and the state he left it in."""
    player = Player([firstrun.CHOOSE, firstrun.QUIT], [])

    settled = settle(player)

    assert player.panels == ["A1", "A1"]
    assert player.seen[0] is player.seen[1]
    assert len(player.opened_at) == 1
    assert settled.go_on is False
    assert gamepath.remembered_game() is None


def test_the_next_dialog_opens_where_the_last_one_was_answered(tmp_path):
    """AK-235: from C3, `Choose a different folder...` starts at his pick."""
    game = an_install(tmp_path)
    inside = game / "sound"
    inside.mkdir()
    player = Player([firstrun.CHOOSE, firstrun.CHOOSE, firstrun.USE],
                    [inside, game.parent])

    settled = settle(player)

    assert player.panels == ["A1", "C3"]
    assert player.opened_at[1] == inside
    assert settled.game == game


def test_the_first_dialog_opens_at_the_folder_that_was_remembered(tmp_path):
    """Section 4.1: as near his goal as anything known can put him."""
    game = an_install(tmp_path)
    player = Player([firstrun.QUIT])

    settle(player, remembered=game)

    assert firstrun.where_to_start_looking(game) == game
    assert firstrun.where_to_start_looking(game / "gone") == game
    assert firstrun.where_to_start_looking(None) in (None, firstrun.STEAM_COMMON)


def test_quitting_keeps_nothing_and_carrying_on_keeps_nothing(tmp_path):
    """AK-116, AK-236: `paths/game` is untouched unless he confirmed a folder."""
    gone = tmp_path / "gone"
    gamepath.remember_game(gone)

    quit_settled = settle(Player([firstrun.QUIT]), remembered=gone)
    carried = settle(Player([firstrun.CARRY_ON]), remembered=gone,
                     day="3 September 2026")

    assert quit_settled == firstrun.Settled(None, False, "")
    assert carried == firstrun.Settled(None, True, "")
    assert gamepath.remembered_game() == gone


def test_a_folder_that_is_gone_is_never_deleted_by_the_asking(tmp_path):
    """AK-121: a failure is not an answer, so it may not overwrite one."""
    gone = tmp_path / "gone"
    gamepath.remember_game(gone)
    empty = tmp_path / "Documents"
    empty.mkdir()
    player = Player([firstrun.CHOOSE], [empty])

    with pytest.raises(LooksLikeAnotherQuestion):
        settle(player, remembered=gone)

    assert gamepath.remembered_game() == gone


def test_nothing_is_kept_while_the_question_c3_is_still_open(tmp_path):
    """AK-236: he has not answered yet, so there is nothing to keep."""
    game = an_install(tmp_path)
    inside = game / "sound"
    inside.mkdir()
    player = Player([firstrun.CHOOSE, firstrun.QUIT], [inside])

    settled = settle(player)

    assert player.panels == ["A1", "C3"]
    assert settled.go_on is False
    assert gamepath.remembered_game() is None


# --- what run() does with it ---------------------------------------------


class FakeWindow:
    """A window that answers instead of showing anything."""

    def __init__(self, answers) -> None:
        self.answers = list(answers)
        self.closed = False

    def ask(self, panel):
        return self.answers.pop(0)

    def close(self) -> None:
        self.closed = True


def a_run(monkeypatch, *, answers, picks, order=None, game=None):
    """`firstrun.run`, with the window and the dialog stated by the case."""
    windows = []

    def a_window():
        window = FakeWindow(answers)
        windows.append(window)
        return window

    monkeypatch.setattr(firstrun, "_Window", a_window)
    monkeypatch.setattr(firstrun, "_pick_a_folder",
                        lambda parent, start_at: picks.pop(0))
    monkeypatch.setattr(firstrun, "a_question_is_due", lambda: True)

    def built(folder, window, said=""):
        if order is not None:
            order.append("built")
        return None

    monkeypatch.setattr(firstrun, "_build_what_is_missing", built)
    return firstrun.run(game), windows


def test_the_folder_is_kept_before_anything_is_built(monkeypatch, tmp_path):
    """AK-117, R9: the order as a counted value, not as a state to look at.

    A crash during the minute the build takes must not cost the answer, so
    the keeping is the step before it and not the step after.
    """
    game = an_install(tmp_path)
    order = []
    kept = firstrun.gamepath.remember_game

    def remember(path):
        order.append("kept")
        kept(path)

    monkeypatch.setattr(firstrun.gamepath, "remember_game", remember)
    outcome, _windows = a_run(monkeypatch, answers=[firstrun.CHOOSE],
                              picks=[game.parent], order=order)

    assert order == ["kept", "built"]
    assert outcome == firstrun.FirstRun(game, True, None)
    assert gamepath.remembered_game() == game


def test_a_find_by_the_automatic_route_is_never_written_back(monkeypatch,
                                                             tmp_path):
    """M3 (T-144): only a confirmation writes `paths/game`.

    It is the one security function this flow has. A folder nobody consented
    to must not inherit the consent, or SEC-026 has nothing left standing.
    """
    game = an_install(tmp_path)

    outcome, windows = a_run(monkeypatch, answers=[], picks=[], game=game)

    assert outcome == firstrun.FirstRun(game, True, None)
    assert windows == []
    assert gamepath.remembered_game() is None


def test_quitting_the_question_ends_the_program_without_a_word(monkeypatch):
    """AK-108, AK-116: the panel is what happens instead of the message box."""
    outcome, windows = a_run(monkeypatch, answers=[firstrun.QUIT], picks=[])

    assert outcome == firstrun.FirstRun(None, False, None)
    assert windows[0].closed is True


def test_carrying_on_with_the_old_data_asks_for_no_folder(monkeypatch):
    """AK-119: A3's way out leads into the program, not out of it."""
    outcome, _windows = a_run(monkeypatch, answers=[firstrun.CARRY_ON],
                              picks=[])

    assert outcome == firstrun.FirstRun(None, True, None)


# --- the window itself ---------------------------------------------------


def a_question_on_screen(panel):
    window = firstrun._Window()
    window.show_the_question(panel)
    return window


def press(window, key):
    window.keyPressEvent(QKeyEvent(QEvent.Type.KeyPress, key,
                                   Qt.KeyboardModifier.NoModifier))


def test_the_question_is_an_ordinary_window_and_the_build_is_not(qapp):
    """AK-109: a title bar and a taskbar entry, because a dialog opens out of it."""
    window = a_question_on_screen(firstrun.a1())
    kind = window.windowFlags() & Qt.WindowType.WindowType_Mask

    assert kind != Qt.WindowType.SplashScreen
    assert window.windowTitle() == "Nightreign Helper"
    assert window.width() == firstrun.PANEL_WIDTH
    assert window.height() >= firstrun.LEAST_PANEL_HEIGHT

    window.show_the_build(first_time=True)

    assert (window.windowFlags()
            & Qt.WindowType.WindowType_Mask) == Qt.WindowType.SplashScreen
    assert window.width() == firstrun.PANEL_WIDTH
    window.close()
    window.deleteLater()


def test_the_confirmation_stands_in_the_build_state(qapp):
    """C1/C2: said once, in GOOD, with no click between it and the build."""
    window = firstrun._Window()
    window.show_the_build(first_time=True, said="Found your game in C:\\here")
    said = [child.text() for child in window.findChildren(type(window.status))]

    assert "Found your game in C:\\here" in said
    assert window.height() > 190
    window.close()
    window.deleteLater()


def test_enter_presses_the_default_button_and_escape_leaves(qapp):
    """AK-130, AK-116: the whole question without a mouse."""
    verdict = firstrun.Verdict(pathlib.Path(r"C:\picked"),
                               pathlib.Path(r"C:\found"), True,
                               firstrun.OUTSIDE)
    window = a_question_on_screen(firstrun.c3(verdict))

    assert window.focusWidget() is window.buttons[firstrun.USE]
    press(window, Qt.Key.Key_Return)
    assert window.answer == firstrun.USE

    window.show_the_question(firstrun.c3(verdict))
    press(window, Qt.Key.Key_Escape)
    assert window.answer == firstrun.QUIT
    window.deleteLater()


#: Longer than any of these panels was drawn for, and with no space in it at
#: all -- which is what a real Steam path looks like.
LONG_PATH = pathlib.Path(r"D:\SteamLibrary\steamapps\common"
                         r"\ELDEN RING NIGHTREIGN with a very long name\Game")


def panels_carrying_a_long_path() -> dict:
    verdict = firstrun.Verdict(LONG_PATH.parent, LONG_PATH, False,
                               firstrun.INSIDE)
    return {
        "A1": firstrun.a1(),
        "A2": firstrun.a2(LONG_PATH),
        "A3": firstrun.a3(LONG_PATH, "8 September 2026"),
        "E1": firstrun.e1(LONG_PATH.parent),
        "W1": firstrun.w1(verdict),
        "C3": firstrun.c3(verdict),
    }


def test_no_panel_cuts_its_own_text_off(qapp):
    """AK-129, as far as an offscreen window can carry it.

    Not the acceptance proof -- that is a picture out of a real window at
    100 %, 125 % and 150 % (AK-239, AK-132) -- but the property it rests on:
    at 460 px the window is as tall as what the text wraps into. Measured
    offscreen, Fusion, dark palette, logical px.

    **Rot-vorher**, both measured: sizing the window by `adjustSize()`
    instead of by the content at this width leaves five of the six panels at
    the 230 px floor with sentences cut off in them; emptying the page
    instead of replacing it leaves every panel after the first one there.
    One window for all six on purpose -- the flow reuses it, and each of
    those two faults only shows from the second panel on.
    """
    window = firstrun._Window()
    try:
        for name, panel in panels_carrying_a_long_path().items():
            window.show_the_question(panel)
            # The geometry the check reads exists once the layout has run.
            rendered.settle()
            cut = [label.text()[:30] for label in window.findChildren(QLabel)
                   if label.heightForWidth(label.width()) > label.height() + 1]

            assert not cut, f"{name}: cut off at {window.height()} px: {cut}"
            assert window.width() == firstrun.PANEL_WIDTH, name
            assert window.height() >= firstrun.LEAST_PANEL_HEIGHT, name
    finally:
        window.close()
        window.deleteLater()


def test_a_path_is_given_places_to_break_and_nothing_else_is():
    """AK-129: a path line wraps. It has no spaces, so it is given breaks.

    Invisible and outside the wording: `Line.text` is what the panel says,
    and it is unchanged -- the breaks are put in as the line is set.
    """
    line = firstrun.Line(str(LONG_PATH), firstrun.PATH)
    written = firstrun._wrappable(line)

    assert written != line.text
    assert written.replace(firstrun.BREAK_HERE, "") == line.text
    assert written.count(firstrun.BREAK_HERE) == line.text.count("\\")
    assert firstrun._wrappable(firstrun.Line("plain words")) == "plain words"


def test_every_button_can_be_reached_by_tab(qapp):
    window = a_question_on_screen(firstrun.a1())

    assert sorted(window.buttons) == sorted([firstrun.QUIT, firstrun.CHOOSE])
    assert all(button.focusPolicy() != Qt.FocusPolicy.NoFocus
               for button in window.buttons.values())
    window.close()
    window.deleteLater()


def test_the_window_cross_answers_the_way_escape_does(qapp):
    """AK-116: closing is not a third answer, it is the same one."""
    window = a_question_on_screen(firstrun.a3(pathlib.Path(r"C:\gone"),
                                              "3 September 2026"))

    window.close()

    assert window.answer == firstrun.CARRY_ON
    window.deleteLater()
