"""A8: every word this program puts in front of a player is English.

The acceptance criterion reads:

    A8 -- All texts in the interface are English (existing project rule).

The rule held because everybody remembered it, and nothing held it: three
independently worded searches over the 64 test files found no case that would
go red if a German sentence reached the screen (QA-192, QA-204). T-114 checked
it once by hand at the built artefact -- 4 806 strings of the packed code and
545 sentences the advisor produced -- and this file is that check turned into
one that runs at every commit. The mask below is T-114's: German is looked for
as **German**, not as "not ASCII", because German written for a German reader
is perfectly good ASCII and `Die Datei kann nicht gelesen werden` would sail
through an ASCII test.

**What this file covers.**

1. Every string literal in the Python this program ships -- `nrplanner`,
   `nrdata` and `run.py` -- except docstrings. That is a **superset** of the
   interface: a sentence a player can read has to be written down somewhere in
   here first, so nothing shown can escape the scan, while plenty that is
   never shown (settings keys, object names, field names) is scanned too. A
   hit is worth reading either way.
2. Every piece of text a built `Planner` really carries: labels, buttons,
   check boxes, group titles, tab titles, tooltips, placeholders, and the
   entries of its combo boxes, lists and tables. This is the half that would
   still hold if interface text ever came from somewhere the source scan does
   not read.

**What it does not cover**, said out loud rather than left to be discovered:

* Docstrings and comments -- nobody reads them from inside the program, and
  the project writes its documents in German on purpose.
* Text Qt itself supplies. The buttons of a standard dialog are translated by
  Qt, not by this program, and a German Windows can put German on them. That
  is outside A8's reach and outside this file's.
* Text that only appears after an action this file does not perform -- a
  message shown after a failed save read, say. The source scan sees the
  sentence anyway; the window half does not.
* Game data. Relic, effect, weapon and boss names belong to the game, and a
  guard that went red at them would be bullying the wrong author. The two
  halves keep them out in two different ways: a literal in the source is by
  construction never game data, and for the window half
  `test_the_games_own_words_cannot_trip_the_mask` measures the separation
  instead of assuming it -- no word of the mask and no German letter occurs
  anywhere in the dataset, so a hit in a rendered string is this program's.

**What the mask catches**: German written as German -- its function words as
whole words, case-insensitively, and the letters that only German writes.
**What it lets through**: a lone German noun with no function word and no
umlaut (`Fehler`), a language that is neither German nor English, and a
deliberate transliteration that avoids both lists. It is a guard against the
sentence that slips in, not a proof of Englishness.
"""

from __future__ import annotations

import ast
import pathlib
import re

from PySide6.QtWidgets import (QComboBox, QListWidget, QTabWidget,
                               QTableWidget, QWidget)

from tests import tabtext

#: German function words that are not also English words. Whole words only,
#: so `under` does not read as `der` and `submit` does not read as `mit`.
#: Deliberately absent: `die`, `war`, `man`, `hat`, `am`, `was` -- each of them
#: is an ordinary English word and would make the guard cry wolf.
GERMAN_FUNCTION_WORDS = (
    "aber", "alle", "allen", "alles", "als", "auch", "auf", "aus", "bei",
    "beim", "bis", "damit", "dann", "darf", "das", "dass", "dem", "den",
    "der", "des", "diese", "dieser", "dieses", "duerfen", "durch", "ein",
    "eine", "einem", "einen", "einer", "etwas", "fuer", "gegen", "haben",
    "hatte", "ihr", "ihre", "immer", "ist", "jede", "jeder", "jedes", "kann",
    "kein", "keine", "koennen", "mehr", "mit", "muessen", "muss", "nach",
    "nicht", "nichts", "noch", "nur", "ohne", "oder", "schon", "sehr", "sein",
    "seine", "sich", "sie", "sind", "soll", "sollen", "sondern", "statt",
    "ueber", "und", "unter", "vom", "von", "vor", "waehrend", "weil", "wenn",
    "werden", "wie", "wieder", "wir", "wird", "zum", "zur", "zwischen",
)

#: Letters no English word carries. The transliterations the project uses in
#: its German documents (`ae`, `oe`, `ue`, `ss`) are covered by the word list
#: above instead, which is why `fuer` and `ueber` stand in it.
GERMAN_LETTERS = "ÄÖÜäöüß"

_WORD = re.compile(r"(?<![A-Za-z])(" + "|".join(GERMAN_FUNCTION_WORDS)
                   + r")(?![A-Za-z])", re.IGNORECASE)
_LETTER = re.compile(f"[{GERMAN_LETTERS}]")

#: The packages that go into the artefact. `NightreignHelper.spec` names
#: `run.py` as the entry point and these two packages are what it imports;
#: `tests/` and `scripts/` are deliberately outside, because they are written
#: in German by the project's own rule and nobody sees them run.
SHIPPED = ("nrplanner", "nrdata")

#: Files that must turn up in the scan. A glob that quietly matched nothing
#: would pass silently, and these three are where interface text lives:
#: the window, the sentences the advisor writes, and the extractor.
ANCHORS = ("nrplanner/app.py", "nrplanner/advisor/explain.py",
           "nrdata/extract.py")


def german_in(text: str) -> list[str]:
    """Every German word and German letter in `text`, or an empty list."""
    return [match.group(0) for match in _WORD.finditer(text)] + \
           [match.group(0) for match in _LETTER.finditer(text)]


def repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def shipped_sources() -> list[pathlib.Path]:
    """Every Python file that goes into the program, newest layout and all."""
    root = repo_root()
    found = [root / "run.py"]
    for package in SHIPPED:
        found += [path for path in sorted((root / package).rglob("*.py"))
                  if "__pycache__" not in path.parts]
    return found


def _docstrings(tree: ast.AST) -> set[int]:
    """The ids of the constant nodes that are docstrings, not text."""
    out = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                                 ast.AsyncFunctionDef)):
            continue
        first = node.body[0] if node.body else None
        if (isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)):
            out.add(id(first.value))
    return out


def literals(path: pathlib.Path) -> list[tuple[int, str]]:
    """(line, text) for every string literal in the file bar its docstrings.

    Read with `ast` rather than with a regular expression, so a docstring is
    told from a sentence by what it is and not by how it is quoted, and so
    comments -- German by project rule -- never enter the scan at all.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    skip = _docstrings(tree)
    return [(node.lineno, node.value) for node in ast.walk(tree)
            if isinstance(node, ast.Constant)
            and isinstance(node.value, str) and id(node) not in skip]


def _texts_of(widget: QWidget) -> list[str]:
    """Every piece of text this widget and its children carry.

    Markup is stripped through `tabtext.plain`, so a sentence split across two
    `<span>`s is read as the one sentence a player sees.
    """
    found: list[str] = []
    for child in [widget] + widget.findChildren(QWidget):
        for name in ("text", "title", "placeholderText", "toolTip",
                     "windowTitle"):
            reader = getattr(child, name, None)
            if not callable(reader):
                continue
            value = reader()
            if isinstance(value, str) and value.strip():
                found.append(value)
        if isinstance(child, QTabWidget):
            found += [child.tabText(i) for i in range(child.count())]
        if isinstance(child, QComboBox):
            found += [child.itemText(i) for i in range(child.count())]
        if isinstance(child, QListWidget):
            found += [child.item(i).text() for i in range(child.count())]
        if isinstance(child, QTableWidget):
            found += _table_texts(child)
    return [tabtext.plain(text) for text in found if tabtext.plain(text)]


def _table_texts(table: QTableWidget) -> list[str]:
    found = []
    for column in range(table.columnCount()):
        header = table.horizontalHeaderItem(column)
        if header is not None:
            found.append(header.text())
        for row in range(table.rowCount()):
            cell = table.item(row, column)
            if cell is not None:
                found.append(cell.text())
    return found


def _every_string_in(node) -> list[str]:
    """Every string anywhere in the dataset, keys and values alike."""
    if isinstance(node, str):
        return [node]
    if isinstance(node, dict):
        return [text for key, value in node.items()
                for text in _every_string_in(key) + _every_string_in(value)]
    if isinstance(node, list):
        return [text for value in node for text in _every_string_in(value)]
    return []


# -- the mask itself, before it is trusted with anything --------------------

def test_the_mask_notices_german_when_it_meets_it():
    """The positive control: a guard that fires at nothing guards nothing.

    Three sentences of the kind that would actually slip in -- an error
    message, a heading, an empty-state line -- and one of them is the sentence
    T-114 used at the artefact. Written out here rather than taken from
    anywhere in the project, so the control cannot be quietly emptied by a
    change somewhere else.
    """
    german = [
        "Die Datei kann nicht gelesen werden",
        "Der Berater hat keine Vorschlaege fuer diesen Kelch",
        "Für diesen Nightfarer ist nichts hinterlegt",
    ]
    english = [
        "The file could not be read",
        "The advisor has nothing to suggest for this chalice",
        "Nothing is stored for this Nightfarer",
        "Reset chalice",
        "2 of its 3 effects moved a number in this build",
    ]
    for sentence in german:
        assert german_in(sentence), f"the mask slept through {sentence!r}"
    for sentence in english:
        assert not german_in(sentence), (
            f"the mask cried wolf at {sentence!r}: {german_in(sentence)}")


def test_the_games_own_words_cannot_trip_the_mask(game_data):
    """Game data is the game's, and this is how the two are kept apart.

    Relic, effect, weapon, boss and chalice names reach the screen unchanged,
    and a language guard that went red at one of them would be asking the
    wrong author to fix it. Rather than filtering them out of the window scan
    -- a filter that fires at nothing is a filter nobody can trust -- the
    separation is measured: not one word of the mask and not one German letter
    occurs anywhere in the dataset, keys and values alike. So a hit on a
    rendered string is this program's own text, whatever it was built out of.

    If a patch ever brings a name that collides, this case is the one that
    says so, and the answer is to narrow the mask -- never to widen what the
    window half is allowed to ignore.
    """
    collisions = {}
    for text in _every_string_in(game_data):
        for hit in german_in(text):
            collisions.setdefault(hit.lower(), text)
    assert not collisions, (
        f"the dataset uses {len(collisions)} word(s) of the language mask, so "
        f"the window guard can no longer tell the game's text from this "
        f"program's: {sorted(collisions.items())[:10]}")


# -- what this program can say ----------------------------------------------

def test_no_sentence_this_program_can_author_is_german():
    """Every string literal the artefact ships, minus its docstrings.

    A superset of the interface on purpose: whatever a player reads was
    written down here first, so a German sentence cannot hide behind an
    f-string, a lazy import or a branch no test walks.
    """
    files = shipped_sources()
    seen = {path.relative_to(repo_root()).as_posix() for path in files}
    missing = [anchor for anchor in ANCHORS if anchor not in seen]
    assert not missing, (f"the scan did not reach {missing}, so a green run "
                         f"would mean nothing")

    scanned = 0
    faults = []
    for path in files:
        for line, text in literals(path):
            scanned += 1
            found = german_in(text)
            if found:
                faults.append(f"{path.relative_to(repo_root()).as_posix()}:"
                              f"{line}: {sorted(set(found))} in {text[:80]!r}")
    assert scanned, "no string literal was read at all"
    assert not faults, (
        f"{len(faults)} of {scanned} strings in {len(files)} shipped files "
        f"read as German:\n" + "\n".join(faults[:20]))


def test_what_the_window_puts_on_screen_is_english(shared_planner):
    """The other half: text the window really carries, tab by tab.

    Read off the widgets rather than off the modules behind them, for the
    reason `tests/tabtext.py` gives -- a guard standing on the constant agrees
    with the code by construction. Every page of the tab bar has to contribute
    something, which is what keeps a walk that quietly only reached the front
    tab from passing as a walk over the window.
    """
    bars = [bar for bar in shared_planner.findChildren(QTabWidget)]
    assert len(bars) == 1, f"expected one tab bar, found {len(bars)}"
    bar = bars[0]
    assert bar.count(), "the window has no tabs"

    everywhere = list(_texts_of(shared_planner))
    for index in range(bar.count()):
        page = bar.widget(index)
        on_this_page = _texts_of(page)
        assert on_this_page, (f"tab {bar.tabText(index)!r} contributed no text "
                              f"at all, so nothing on it was checked")
        everywhere += on_this_page

    faults = []
    for text in everywhere:
        found = german_in(text)
        if found:
            faults.append(f"{sorted(set(found))} in {text[:100]!r}")
    assert not faults, (
        f"{len(faults)} of {len(everywhere)} pieces of text the window carries "
        f"read as German:\n" + "\n".join(sorted(set(faults))[:20]))
