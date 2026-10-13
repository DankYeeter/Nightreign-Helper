"""The suite's own surroundings: what it leaves behind and where it writes.

QA-047: a run killed half way never clears its settings store, and a finished
one leaves the empty key, so `HKCU\\Software\\DankYeeterTests` held ten of
them. QA-212: only the settings store was redirected; the cache and the Start
Menu folder were the player's own. Both are put right in `conftest.py`, and
these cases hold it there.

The sweep is exercised on an organisation of its own, never the one the suite
writes to and never the player's.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys

import pytest

from nrplanner import paths, shortcut
from tests import conftest

pytestmark = pytest.mark.skipif(sys.platform != "win32",
                                reason="the stores are registry keys")

ORG = f"DankYeeterT-334j-{os.getpid()}"


@pytest.fixture
def sweep_org():
    """An organisation that exists for one case and is gone after it."""
    import winreg

    yield ORG
    conftest._delete_key_tree(winreg.HKEY_CURRENT_USER, f"Software\\{ORG}")


def _a_store(org: str, app: str) -> None:
    """A key with a value and a subkey, as a run's store has."""
    import winreg

    with winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                          rf"Software\{org}\{app}\build") as key:
        winreg.SetValueEx(key, "name", 0, winreg.REG_SZ, "kept or swept")


def _stores_under(org: str) -> set[str]:
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            f"Software\\{org}") as root:
            return {winreg.EnumKey(root, i)
                    for i in range(winreg.QueryInfoKey(root)[0])}
    except FileNotFoundError:
        return set()


def _a_process_id_that_is_gone() -> int:
    process = subprocess.Popen([sys.executable, "-c", "pass"])
    process.wait()
    return process.pid


def test_a_store_of_a_dead_run_is_swept_and_a_living_one_is_not(sweep_org):
    dead = f"{conftest.STORE_PREFIX}{_a_process_id_that_is_gone()}"
    alive = f"{conftest.STORE_PREFIX}{os.getpid()}"
    not_a_run = "NightreignHelper"
    for app in (dead, alive, not_a_run):
        _a_store(sweep_org, app)

    conftest.remove_stores_of_dead_runs(sweep_org)

    assert _stores_under(sweep_org) == {alive, not_a_run}


def test_the_sweep_of_an_organisation_that_does_not_exist_is_a_no_op():
    conftest.remove_stores_of_dead_runs(f"{ORG}-never-created")


def test_a_running_process_is_told_from_one_that_has_ended():
    assert conftest._process_is_running(os.getpid())
    assert not conftest._process_is_running(_a_process_id_that_is_gone())


def test_the_cache_is_a_folder_of_this_run_and_not_the_players(
        data_dirs_of_this_run):
    real_cache = (pathlib.Path.home() / "AppData" / "Local"
                  / paths.APP_NAME)

    assert paths.cache_dir() == data_dirs_of_this_run
    assert data_dirs_of_this_run.is_dir()
    assert data_dirs_of_this_run != real_cache


def test_the_start_menu_is_a_folder_of_this_run_and_not_the_players(
        data_dirs_of_this_run):
    real_roaming = pathlib.Path.home() / "AppData" / "Roaming"
    this_run = data_dirs_of_this_run.parents[1]

    assert shortcut.start_menu_dir().is_relative_to(this_run)
    assert not shortcut.start_menu_dir().is_relative_to(real_roaming)
