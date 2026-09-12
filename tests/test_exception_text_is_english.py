"""A8 for the one text nobody wrote: the exception's own words (QA-211).

Two guards of A8 already stand. `test_interface_language.py` reads the string
literals of the source, and its window-text half reads what a built window
actually shows. Between them lies a third class of text that neither can see:
the text an **exception** brings with it and a display line puts on the
surface. It is not a literal, so the source scan walks past it, and no
ordinary run provokes it, so the window scan never has it on screen.

On a German Windows that text is German. `OSError` gets its message from
`FormatMessageW`, which answers in the language of the installation, and
`strerror` -- the half of it that carries no path (AK-126) -- is the same
message minus the path. Two of the five places QA-211 found are everyday
ones: the Start Menu button and a save re-read that failed.

**What this file holds.**

* a scan of `nrplanner` and `nrdata` for any place that puts an exception's
  own text where a caller can show it, against a list that may only shrink;
* its positive control, because a scan that has stopped scanning also finds
  nothing;
* the four sinks QA-211 named and this change closed, driven with an
  exception worded in German, checked for what comes out;
* the sentences of `errortext` themselves, which are the text that replaced
  it and are therefore in the window under A8 like any other.
"""

from __future__ import annotations

import ast
import errno
import pathlib
import subprocess

import pytest

from nrplanner import app as appmod
from nrplanner import errortext, firstrun, inventory, shortcut

#: What Windows says on a German installation when it will not open a file.
#: A literal and not a call into the running system: the point is a text this
#: program did not write, and the test has to be the same on any machine.
GERMAN_FROM_WINDOWS = "Zugriff verweigert"

#: A save path shaped like the real one. The folder is named after the Steam
#: account id (AK-126), so it may not reach the surface either -- an `OSError`
#: carries it in `str(exc)` and in `filename`.
A_SAVE_PATH = r"C:\Users\someone\AppData\Roaming\Nightreign\76561198000000000\NR0000.sl2"


def a_refusal_worded_by_windows(code: int = errno.EACCES) -> OSError:
    """An `OSError` exactly as Windows hands one over on a German machine."""
    return OSError(code, GERMAN_FROM_WINDOWS, A_SAVE_PATH)


def says_nothing_windows_said(said: str) -> None:
    """The three things that must not have survived into a shown sentence."""
    assert GERMAN_FROM_WINDOWS not in said, said
    assert A_SAVE_PATH not in said, said
    assert "\\" not in said and "/" not in said, said
    assert said.isascii(), said
    assert said.strip(), "a sink that says nothing is not an answer"


# -- the scan ---------------------------------------------------------------

#: Attributes that hand out the operating system's own wording. `args` and
#: `message` are the whole of it, `strerror` and `winerror` the halves AK-126
#: left behind when it took the path out.
WORDING_ATTRIBUTES = ("strerror", "args", "winerror", "message", "reason")

#: The packages whose modules are scanned. `nrdata` is in because the first
#: run shows what its extraction raises, in the same dialog.
SCANNED = ("nrplanner", "nrdata")


def places_that_quote_an_exception(source: str) -> list[tuple[str, str]]:
    """Every place that turns a caught exception into text, by function.

    Three shapes, because those are the three ways it has been written in
    this repository: `str(exc)`, an f-string that interpolates it, and one of
    its wording attributes. The name it looks for is the one the `except`
    clause bound, so a local string called `error` -- of which this program
    has several, and they are its own words -- is not a hit.

    Not a hit either: `errortext.in_english(exc)`, which is the one way an
    exception is allowed to reach the surface. It hands over the object and
    gets back a sentence written in this repository, so the exception's own
    text never leaves the object. That asymmetry is the whole point of the
    scan, and it is why `errortext` needs no exemption from it.
    """
    tree = ast.parse(source)
    found: list[tuple[str, str]] = []
    for handler in ast.walk(tree):
        if not isinstance(handler, ast.ExceptHandler) or not handler.name:
            continue
        caught = handler.name
        for node in ast.walk(handler):
            shape = _how_it_is_quoted(node, caught)
            if shape:
                found.append((_the_function_around(tree, node.lineno), shape))
    return found


def _how_it_is_quoted(node: ast.AST, caught: str) -> str:
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id in ("str", "repr", "format")
            and any(isinstance(arg, ast.Name) and arg.id == caught
                    for arg in node.args)):
        return f"{node.func.id}({caught})"
    if isinstance(node, ast.FormattedValue):
        for inner in ast.walk(node.value):
            if isinstance(inner, ast.Name) and inner.id == caught:
                return "{%s}" % caught
    if (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
            and node.value.id == caught and node.attr in WORDING_ATTRIBUTES):
        return f"{caught}.{node.attr}"
    return ""


def _the_function_around(tree: ast.AST, lineno: int) -> str:
    """The innermost function a line sits in, or `<module>`."""
    name = "<module>"
    span = None
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        end = node.end_lineno or node.lineno
        if node.lineno <= lineno <= end:
            here = end - node.lineno
            if span is None or here < span:
                name, span = node.name, here
    return name


def everywhere_an_exception_is_quoted() -> dict[tuple[str, str, str], int]:
    """The scan over the two packages: `(module, function, shape)` and how many.

    **How many, and not just where.** `_scan_save` writes `str(exc)` twice for
    two different reasons, and a set would have shown one entry for both -- so
    repairing one of them would have left the guard saying exactly what it
    said before. The count is what makes half a repair visible.

    Walked from the two package folders and not from the repository root, so
    a worktree checked out under `.claude/` is not read as a second copy of
    every finding (it is the same repository on an older commit, and no run
    can repair it).
    """
    root = pathlib.Path(__file__).resolve().parents[1]
    out: dict[tuple[str, str, str], int] = {}
    for package in SCANNED:
        for path in sorted((root / package).rglob("*.py")):
            source = path.read_text(encoding="utf-8")
            for function, shape in places_that_quote_an_exception(source):
                here = (path.relative_to(root).as_posix(), function, shape)
                out[here] = out.get(here, 0) + 1
    return out


#: The places the scan still finds, and why each is still there. **This list
#: may only shrink.** It is the guard's red phase written down: a scan whose
#: expected set is empty is indistinguishable from a scan that has broken,
#: and every line here is a real place where an exception's own text can
#: still reach a reader.
#:
#: * `advisor/worker.py` -- out of bounds for T-190 (A17 is being rebuilt
#:   there). The same sink, one line, the same fix.
#: * `app.py::main` -- `load_data` raises `FileNotFoundError` with a message
#:   this program wrote (`datasource._no_data_message`). Mapping it by class
#:   would throw that message away, and marking it needs `datasource.py`,
#:   which is over T-190's file budget.
#: * `inventory.py::_scan_save`, **twice** -- the slot read and the stored
#:   builds both quote what `nrdata/savefile.py` refused with. Those refusals
#:   are English sentences of this repository, collected by AK-229's guard,
#:   but they arrive as a plain `ValueError` and so cannot be told from
#:   pycryptodome's. Mapping them by class was tried and threw the sentences
#:   away; telling them apart needs a class in `nrdata/savefile.py`, also
#:   over budget.
#: * `nrdata/extract.py::_bosses` -- a `print` to the console, not a window.
#: * `nrdata/icons.py::read_subtextures` -- `LayoutError` is this program's
#:   class, so its text is shown, and it interpolates what ElementTree said.
STILL_QUOTING = {
    ("nrplanner/advisor/worker.py", "work", "str(exc)"): 1,
    ("nrplanner/app.py", "main", "str(exc)"): 1,
    ("nrplanner/inventory.py", "_scan_save", "str(exc)"): 2,
    ("nrdata/extract.py", "_bosses", "{exc}"): 1,
    ("nrdata/icons.py", "read_subtextures", "{exc}"): 1,
}


def test_the_scan_really_fires():
    """The positive control. Without it the guard measures its own mask.

    All three shapes, on source held here rather than read off the tree: the
    offenders in the list below could all be repaired tomorrow, and then an
    empty scan and a broken scan would look the same.
    """
    quoting = """
def one():
    try:
        go()
    except OSError as exc:
        say(str(exc))
        shout(f"it went wrong: {exc}")
        note(exc.strerror)
"""
    assert set(places_that_quote_an_exception(quoting)) == {
        ("one", "str(exc)"), ("one", "{exc}"), ("one", "exc.strerror")}

    allowed = """
def two():
    error = "a sentence this program wrote"
    try:
        go()
    except OSError as exc:
        say(errortext.in_english(exc))
        shout(f"it went wrong: {error}")
        note(exc.__class__.__name__)
"""
    assert places_that_quote_an_exception(allowed) == []


def test_no_new_place_quotes_an_exception():
    """A property of the two packages, not a list of five known lines.

    Anything the scan finds that is not below is a new way for Windows to
    write in the window, and a line below that the scan no longer finds is
    one fewer -- that is allowed, and removing it from the list is part of
    repairing it.
    """
    found = everywhere_an_exception_is_quoted()
    assert set(found) - set(STILL_QUOTING) == set(), sorted(set(found)
                                                            - set(STILL_QUOTING))
    grown = {where: (many, STILL_QUOTING[where])
             for where, many in found.items()
             if many > STILL_QUOTING[where]}
    assert grown == {}, sorted(grown.items())


def test_the_list_of_the_ones_left_is_still_true():
    """Every line of `STILL_QUOTING` is a place that exists.

    The self-check the guard needs: a list that has outlived its places stops
    being a ceiling and becomes a lie about how much is left. Shrinking is
    the only correct way for it to change, and this is what makes a stale
    entry loud instead of comfortable.
    """
    found = everywhere_an_exception_is_quoted()
    assert set(STILL_QUOTING) - set(found) == set(), sorted(set(STILL_QUOTING)
                                                            - set(found))
    shrunk = {where: (found[where], many)
              for where, many in STILL_QUOTING.items()
              if found[where] < many}
    assert shrunk == {}, sorted(shrunk.items())


# -- the sentences that replaced it -----------------------------------------

def every_sentence() -> list[str]:
    return (list(errortext.WHAT_THE_SYSTEM_REFUSED.values())
            + [sentence for _, sentence in errortext.WHAT_WENT_WRONG]
            + [errortext.NOTHING_WAS_SAID])


def test_every_sentence_is_a_plain_english_sentence():
    """A8 for the replacement text, which is in the window like any other."""
    for sentence in every_sentence():
        assert sentence.isascii(), sentence
        assert sentence[0].isupper(), sentence
        assert sentence.endswith("."), sentence


def test_no_two_failures_share_a_sentence_by_accident():
    """A7: what `strerror` said has to survive as *which* thing went wrong.

    Two codes may share a sentence on purpose -- `EMFILE` and `ENFILE` are
    one thing to a player -- so this counts rather than forbids: mapping the
    whole table on to a handful of sentences would be A8 bought with A7, and
    that is what the number below would show.
    """
    said = list(errortext.WHAT_THE_SYSTEM_REFUSED.values())
    assert len(set(said)) >= len(said) - 1, sorted(said)


def test_the_operating_system_never_supplies_the_words():
    """The table's own case, and the two ways past it."""
    says_nothing_windows_said(errortext.in_english(a_refusal_worded_by_windows()))
    assert (errortext.in_english(a_refusal_worded_by_windows())
            == errortext.WHAT_THE_SYSTEM_REFUSED[errno.EACCES])

    # A code the table has no line for still says what it can, and says it
    # here: `errorcode` is Python's own ASCII name for the number, which is
    # the standard library's and not this program's -- so naming it is not
    # the guard reading its own expectation off the thing it guards.
    unlisted = OSError(errno.EDEADLK, GERMAN_FROM_WINDOWS, A_SAVE_PATH)
    says_nothing_windows_said(errortext.in_english(unlisted))
    assert errno.errorcode[errno.EDEADLK] in errortext.in_english(unlisted)
    assert errortext.in_english(unlisted) != errortext.in_english(OSError())

    # No code at all, which is what a hand-built `OSError` looks like.
    says_nothing_windows_said(errortext.in_english(OSError()))


def test_a_library_never_supplies_the_words():
    """Anything not of this program is mapped, whatever it has to say."""
    says_nothing_windows_said(errortext.in_english(ValueError(GERMAN_FROM_WINDOWS)))
    assert "ValueError" in errortext.in_english(ValueError(GERMAN_FROM_WINDOWS))
    says_nothing_windows_said(errortext.in_english(
        subprocess.TimeoutExpired(["powershell", A_SAVE_PATH], 30)))


def test_this_program_s_own_classes_are_quoted():
    """The one exception, and the reason A8 still holds over it.

    Their text is a literal in this repository, which is exactly what the
    source half of `test_interface_language.py` already reads. Dropping it
    would cost the sentences AK-124 and AK-229 are about.
    """
    ours = inventory.SaveNotReadable("That file is not a Nightreign save.")
    assert errortext.in_english(ours) == "That file is not a Nightreign save."
    assert errortext.in_english(inventory.SaveNotReadable("")) \
        == errortext.NOTHING_WAS_SAID


# -- the sinks QA-211 named -------------------------------------------------

def test_the_start_menu_button_says_it_in_english(monkeypatch, tmp_path):
    """QA-211's first everyday way: a click on the Start Menu button.

    Both halves of the button, because both had the same line: writing the
    shortcut goes through PowerShell and can fail with anything, removing it
    is an `unlink` and fails with an `OSError`.
    """
    monkeypatch.setattr(shortcut, "available", lambda: True)
    monkeypatch.setattr(shortcut, "shortcut_path", lambda: tmp_path / "a.lnk")
    monkeypatch.setattr(shortcut, "powershell_path", lambda: tmp_path / "ps.exe")
    monkeypatch.setattr(shortcut, "target", lambda: tmp_path / "nrh.exe")

    def refuse(*args, **kwargs):
        raise a_refusal_worded_by_windows()

    monkeypatch.setattr(subprocess, "run", refuse)
    said = shortcut.create()
    says_nothing_windows_said(said)
    assert said == errortext.WHAT_THE_SYSTEM_REFUSED[errno.EACCES]

    monkeypatch.setattr(pathlib.Path, "unlink", refuse)
    said = shortcut.remove()
    says_nothing_windows_said(said)
    assert said == errortext.WHAT_THE_SYSTEM_REFUSED[errno.EACCES]


def test_a_save_windows_will_not_open_is_reported_in_english(game_data,
                                                             monkeypatch,
                                                             tmp_path):
    """QA-211's second everyday way, at its source: the read itself.

    `read_the_save` is where AK-126 already took the path out of the
    `OSError`. What was left was `strerror`, and that is the half Windows
    writes in its own language.
    """
    chosen = tmp_path / "NR0000.sl2"
    chosen.write_bytes(b"")
    monkeypatch.setattr(appmod, "_refuse_a_file_no_save_can_be", lambda _p: None)

    def refuse(*args, **kwargs):
        raise a_refusal_worded_by_windows()

    monkeypatch.setattr(inventory, "scan", refuse)

    with pytest.raises(inventory.SaveNotReadable) as raised:
        appmod.read_the_save(game_data, chosen)

    says_nothing_windows_said(str(raised.value))
    assert str(raised.value) == errortext.WHAT_THE_SYSTEM_REFUSED[errno.EACCES]


def test_the_line_under_the_save_never_carries_windows_words(game_data, qapp):
    """QA-211's second everyday way, at the sink: the line in the window.

    The worker takes whatever the read raised and hands one line to the main
    thread. Driven here without the thread, because the question is what the
    line says and not when it arrives -- and driven with an exception no part
    of this program raised, which is the case the sink has to survive.
    """
    said: list[str] = []

    def refuse(_data, _path):
        raise a_refusal_worded_by_windows()

    worker = appmod._SaveReadWorker(7, game_data, refuse)
    worker.failed.connect(lambda generation, reason: said.append(reason))
    worker.work()

    assert len(said) == 1, said
    says_nothing_windows_said(said[0])
    assert said[0] == errortext.WHAT_THE_SYSTEM_REFUSED[errno.EACCES]


def test_the_first_run_says_it_in_english(monkeypatch, tmp_path):
    """QA-211's third way: the dialog of the very first start.

    The build reads the game's own folders, so most of what can fail in it is
    an `OSError` -- and the one text the player gets is what this emits.
    """
    said: list[str] = []
    builder = firstrun._Builder(tmp_path / "game", ["snapshot"])
    builder.finished.connect(said.append)

    monkeypatch.setattr(firstrun, "defs_dir", lambda: tmp_path / "defs")

    class ARefusedFolder:
        def mkdir(self, **kwargs):
            raise a_refusal_worded_by_windows()

    monkeypatch.setattr(firstrun.paths, "cache_dir", ARefusedFolder)
    builder.run()

    assert len(said) == 1, said
    says_nothing_windows_said(said[0])
    assert said[0] == errortext.WHAT_THE_SYSTEM_REFUSED[errno.EACCES]


def test_the_first_run_keeps_the_sentence_it_wrote_itself(monkeypatch,
                                                          tmp_path):
    """A7's half of the same change, and the reason `CannotBuild` exists.

    The missing param definitions are the one failure of the first run this
    program can explain, and it explained it as a `FileNotFoundError` -- an
    `OSError`, which the mapping would have answered with the `errno` table
    and the sentence would have been lost.
    """
    said: list[str] = []
    builder = firstrun._Builder(tmp_path / "game", ["snapshot"])
    builder.finished.connect(said.append)

    monkeypatch.setattr(firstrun, "defs_dir", lambda: None)
    builder.run()

    assert said == ["The param definitions are missing, so the game cannot be "
                    "read. Reinstalling should restore them."]
