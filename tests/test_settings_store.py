"""Every settings store this program opens is the one it was told to open.

QA-049. `nrplanner.favourites` reads the store's organisation and application
names out of NIGHTREIGN_SETTINGS_ORG / _APP, and conftest sets both before Qt
is imported, so a run writes into a store of its own and clears it again
afterwards. Two lines in app.py built `QSettings("DankYeeter",
"NightreignHelper")` from literals instead and went straight past that: the
tile that shows a Nightfarer's artwork read the player's own settings on
every launch of the suite, and would have written there the first time a test
clicked a variant. The key it used is derived from a Nightfarer id and is
harmless; the store it used was not.

Two things are held to account here, and they are different questions:

* the behaviour -- an artwork variant, saved and read back, goes through the
  named store, which is the only claim a test can make by running the code;
* the class -- no source in this repository builds a settings store any other
  way. That is read off the syntax tree, because the fix itself is two lines
  and a fix of two lines is what the last three cycles kept producing right
  before the same fault turned up somewhere else (L-001).

What the scan does not see, and does not claim to:

* a store reached at run time rather than by name -- a class fetched out of
  sys.modules, a name assembled from strings. A tree is what is written, not
  what is executed;
* a store pinned through the environment instead of through QSettings.
  `scripts/capture_weapon_damage.py` sets NIGHTREIGN_SETTINGS_APP to a fixed
  literal, which is a store of the right kind under a name two runs can
  share -- a different fault (QA-043), reported and not touched here;
* anything that is not a .py file, and anything under .venv, which is
  PySide6's own code and not ours.

There are no exempted call sites. Every construction in the repository names
the store through `favourites`, and a future one that genuinely cannot -- a
file-backed store for an export, say -- belongs in this file as a named
exception with its reason, not as a quiet second spelling.
"""

from __future__ import annotations

import ast
import os
import pathlib

import pytest
from PySide6.QtCore import QSettings

from nrplanner import app as appmod
from nrplanner import favourites

REPO = pathlib.Path(__file__).resolve().parents[1]

# The virtual environment is PySide6's code and the caches hold no source.
NOT_OURS = frozenset({".venv", ".git", "__pycache__", "build", "dist"})

# The two module-level names in nrplanner.favourites, in the order QSettings
# takes them, and the module they are read from.
STORE_NAMES = ("ORG", "APP")
THE_MODULE = "favourites"


def python_modules(root: pathlib.Path) -> list[pathlib.Path]:
    """Every source file in the repository, however deeply it is nested.

    The whole tree and not just `nrplanner/`: `run.py` and `scripts/` build
    Planners too, and a store opened from either lands in the same registry
    as one opened from the package.
    """
    found: list[pathlib.Path] = []
    for folder, subfolders, files in os.walk(root):
        subfolders[:] = [d for d in subfolders if d not in NOT_OURS]
        found.extend(pathlib.Path(folder) / name for name in files
                     if name.endswith(".py"))
    return sorted(found)


def _class_names(tree: ast.AST) -> set[str]:
    """What this module calls QSettings, since an import may rename it."""
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "QSettings":
                    names.add(alias.asname or alias.name)
    return names


def _is_the_class(node: ast.AST, names: set[str]) -> bool:
    """Whether this expression names QSettings, imported or through Qt."""
    if isinstance(node, ast.Name):
        return node.id in names
    return isinstance(node, ast.Attribute) and node.attr == "QSettings"


def _is_one_of_the_names(node: ast.AST, wanted: str) -> bool:
    """Whether this argument is favourites.ORG / favourites.APP.

    The bare name counts too: favourites itself opens the store that way, and
    so would a module that imported the two names from it.
    """
    if isinstance(node, ast.Name):
        return node.id == wanted
    if not isinstance(node, ast.Attribute) or node.attr != wanted:
        return False
    owner = node.value
    if isinstance(owner, ast.Name):
        return owner.id == THE_MODULE
    return isinstance(owner, ast.Attribute) and owner.attr == THE_MODULE


def _names_the_store(call: ast.Call) -> bool:
    """Whether this call hands the store exactly the two names, in order."""
    return (not call.keywords and len(call.args) == len(STORE_NAMES)
            and all(_is_one_of_the_names(argument, wanted)
                    for argument, wanted in zip(call.args, STORE_NAMES)))


def _through_a_base_class(tree: ast.AST, names: set[str]) -> list[int]:
    """Where a subclass of QSettings hands its base something else.

    A route the repository has rather than one it might grow: the suite holds
    a QSettings subclass already, to stand in for a store that drops a write.
    A store built by a base class is built all the same.
    """
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        if not any(_is_the_class(base, names) for base in node.bases):
            continue
        for inner in ast.walk(node):
            if (isinstance(inner, ast.Call)
                    and isinstance(inner.func, ast.Attribute)
                    and inner.func.attr == "__init__"
                    and not _names_the_store(inner)):
                found.append(inner.lineno)
    return found


def stores_built_another_way(source: str) -> list[int]:
    """The line of every settings store this source opens by another name."""
    tree = ast.parse(source)
    names = _class_names(tree)
    found = [node.lineno for node in ast.walk(tree)
             if isinstance(node, ast.Call)
             and _is_the_class(node.func, names)
             and not _names_the_store(node)]
    return sorted(found + _through_a_base_class(tree, names))


def test_no_source_opens_a_settings_store_of_its_own():
    offenders = {}
    for path in python_modules(REPO):
        lines = stores_built_another_way(path.read_text(encoding="utf-8"))
        if lines:
            offenders[path.relative_to(REPO).as_posix()] = lines
    assert not offenders, (
        "these lines open a settings store that is not the one "
        "NIGHTREIGN_SETTINGS_ORG / _APP name, so a test run reaches the "
        f"player's own settings: {offenders}. Build it from favourites.ORG "
        "and favourites.APP, as every persisting module does."
    )


# One entry per way of opening a store the two names do not reach. A search
# for the literal text would have found the first and none of the rest.
WAYS_ROUND_THE_GUARD = {
    "the two names written out":
        "from PySide6.QtCore import QSettings\n"
        "QSettings('DankYeeter', 'NightreignHelper')\n",
    "one name and one literal":
        "from PySide6.QtCore import QSettings\n"
        "from . import favourites\n"
        "QSettings(favourites.ORG, 'NightreignHelper')\n",
    "the names the wrong way round":
        "from PySide6.QtCore import QSettings\n"
        "from . import favourites\n"
        "QSettings(favourites.APP, favourites.ORG)\n",
    "the class under an alias":
        "from PySide6.QtCore import QSettings as Store\n"
        "Store('DankYeeter', 'NightreignHelper')\n",
    "the class through its module":
        "from PySide6 import QtCore\n"
        "QtCore.QSettings('DankYeeter', 'NightreignHelper')\n",
    "no names at all, which is the application's own store":
        "from PySide6.QtCore import QSettings\nQSettings()\n",
    "a name put together at the call":
        "from PySide6.QtCore import QSettings\n"
        "QSettings('DankYeeter', 'Nightreign' + 'Helper')\n",
    "the file form, which is a store of another kind":
        "from PySide6.QtCore import QSettings\n"
        "QSettings('builds.ini', QSettings.IniFormat)\n",
    "a subclass handing its base literals":
        "from PySide6.QtCore import QSettings\n"
        "class Store(QSettings):\n"
        "    def __init__(self):\n"
        "        super().__init__('DankYeeter', 'NightreignHelper')\n",
}

SPELLINGS_THAT_ARE_RIGHT = {
    "through the module":
        "from PySide6.QtCore import QSettings\n"
        "from . import favourites\n"
        "QSettings(favourites.ORG, favourites.APP)\n",
    "the package spelled out":
        "from PySide6.QtCore import QSettings\n"
        "import nrplanner.favourites\n"
        "QSettings(nrplanner.favourites.ORG, nrplanner.favourites.APP)\n",
    "the names imported bare, as favourites itself opens it":
        "from PySide6.QtCore import QSettings\n"
        "from .favourites import ORG, APP\n"
        "QSettings(ORG, APP)\n",
    "a subclass handing its base the names":
        "from PySide6.QtCore import QSettings\n"
        "from . import favourites\n"
        "class Store(QSettings):\n"
        "    def __init__(self):\n"
        "        super().__init__(favourites.ORG, favourites.APP)\n",
}


@pytest.mark.parametrize("spelling", sorted(WAYS_ROUND_THE_GUARD))
def test_the_scan_sees_every_way_round_it(spelling):
    assert stores_built_another_way(WAYS_ROUND_THE_GUARD[spelling])


@pytest.mark.parametrize("spelling", sorted(SPELLINGS_THAT_ARE_RIGHT))
def test_the_scan_passes_the_spellings_that_are_right(spelling):
    assert stores_built_another_way(SPELLINGS_THAT_ARE_RIGHT[spelling]) == []


# A Nightfarer of its own per case, so neither of the two below can be read
# out of what the other left behind. No dataset is needed: a tile is a
# portrait, an id and a name, and the artwork it cannot find is drawn as
# initials, which is the case every DLC Nightfarer is in anyway.
WRITING_NIGHTFARER = {"id": 990_001, "name": "Store test one"}
READING_NIGHTFARER = {"id": 990_002, "name": "Store test two"}
A_VARIANT = 4242


def test_a_chosen_artwork_is_written_to_the_named_store(qapp):
    tile = appmod.HeroTile(0, WRITING_NIGHTFARER, appmod.IconPack())

    tile.set_variant(A_VARIANT)

    settings = QSettings(favourites.ORG, favourites.APP)
    stored = settings.value(f"variant/{WRITING_NIGHTFARER['id']}", "",
                            type=str)
    assert stored == str(A_VARIANT)


def test_a_chosen_artwork_is_read_back_from_the_named_store(qapp):
    settings = QSettings(favourites.ORG, favourites.APP)
    settings.setValue(f"variant/{READING_NIGHTFARER['id']}", A_VARIANT)
    settings.sync()
    tile = appmod.HeroTile(0, READING_NIGHTFARER, appmod.IconPack())

    tile.restore_variant()

    assert tile.variant_id == A_VARIANT
