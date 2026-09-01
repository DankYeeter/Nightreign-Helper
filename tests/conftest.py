"""Shared fixtures for the whole suite.

Two rules shape everything here.

**Headless.** Qt reads QT_QPA_PLATFORM once, when the first QApplication is
created, so it is set before anything imports PySide6 -- at module import
time, above the imports that matter. A test that needs a window gets one that
is never shown.

**The player's own files are read and never written.** The dataset comes from
the installed game or from a snapshot built from it; the save is opened
read-only by the code under test. Settings are the one thing the program does
write, so the suite redirects them to a store of its own through the
environment variables the program already honours (see nrplanner.favourites).
Without that redirect a test run would overwrite the builds and favourites of
whoever is sitting at the machine.

Where a test genuinely needs the installed game, it is skipped with a message
saying so rather than failing -- a runner has no Nightreign installation, and
that is the correct state for a runner to be in.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys

import pytest

# Before PySide6 is imported anywhere, including by a test module.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
# nrplanner.favourites reads these at import time and every persisting module
# (favourites, chalices, uiscale) goes through it.
os.environ["NIGHTREIGN_SETTINGS_ORG"] = "DankYeeterTests"
os.environ["NIGHTREIGN_SETTINGS_APP"] = "NightreignHelperTests"

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

# Point this at a nightreign_data.json to run the data-backed tests without
# waiting ~40 s for a fresh extraction. It is a convenience for the developer
# loop; the tests are identical either way.
SNAPSHOT_ENV = "NIGHTREIGN_TEST_SNAPSHOT"

NO_DATA = (
    "needs the dataset: set {env} to a nightreign_data.json, run the program "
    "once so it builds one, or run this on a machine with NIGHTREIGN "
    "installed. Nothing here ships game data."
).format(env=SNAPSHOT_ENV)


def _snapshot_from_env() -> dict | None:
    raw = os.environ.get(SNAPSHOT_ENV)
    if not raw:
        return None
    path = pathlib.Path(raw)
    if not path.is_file():
        pytest.fail(f"{SNAPSHOT_ENV} points at {path}, which is not a file")
    return json.loads(path.read_text(encoding="utf-8"))


def _snapshot_from_cache() -> dict | None:
    """The snapshot the program itself built, if this machine has run it."""
    from nrplanner import paths

    path = paths.snapshot_path()
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _snapshot_from_game() -> dict | None:
    """Read the installed game. Read-only, as the program promises."""
    from nrdata import extract, gamefiles
    from nrplanner import datasource

    game = gamefiles.find_game_dir()
    defs = datasource.defs_dir()
    if game is None or defs is None:
        return None
    return extract.build(game, defs)


@pytest.fixture(scope="session")
def game_data() -> dict:
    """The dataset the planner computes on, with model.configure() applied.

    Session-scoped because a fresh extraction costs about 40 seconds and the
    data is read-only for every test that takes it.
    """
    from nrplanner import model

    data = (_snapshot_from_env() or _snapshot_from_cache()
            or _snapshot_from_game())
    if data is None:
        pytest.skip(NO_DATA)
    # Without this the module falls back to guessing from field names, which
    # is a different calculation -- QA-011. Every test that computes anything
    # takes this fixture, so no test can compute in the unconfigured state by
    # accident.
    model.configure(data)
    return data


@pytest.fixture(scope="session")
def qapp():
    """One QApplication for the session; Qt allows no more than one."""
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app


def clear_settings() -> None:
    """Empty the test settings store.

    The Planner stores the build it is holding on almost every change, so a
    test that builds one leaves entries behind and the next Planner would
    restore them. They are under the test organisation set at the top of this
    file, never the player's.
    """
    from PySide6.QtCore import QSettings

    from nrplanner import favourites

    settings = QSettings(favourites.ORG, favourites.APP)
    settings.clear()
    settings.sync()


@pytest.fixture(scope="session", autouse=True)
def settings_store(qapp):
    """Nothing of an earlier run is inherited, and nothing is left behind."""
    clear_settings()
    yield
    clear_settings()


def _new_planner(data: dict):
    """A real Planner window, never shown.

    This is the whole application object: it reads the save if there is one,
    builds every tab and computes a build. Tests that compare what two tabs
    say need exactly that -- a stub would be the thing under test.
    """
    from nrplanner import app as appmod

    clear_settings()
    return appmod.Planner(data)


@pytest.fixture
def planner(game_data, qapp):
    """A Planner of its own for one test, for tests that fill its slots."""
    window = _new_planner(game_data)
    yield window
    window.close()
    window.deleteLater()


@pytest.fixture(scope="module")
def shared_planner(game_data, qapp):
    """One Planner for a whole module.

    Building one costs a couple of seconds, which a table of twenty cases
    should not pay twenty times. Only for tests that set every input they
    depend on, so the order they run in cannot matter.
    """
    window = _new_planner(game_data)
    yield window
    window.close()
    window.deleteLater()
