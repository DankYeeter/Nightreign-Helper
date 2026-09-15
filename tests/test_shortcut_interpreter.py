"""The Start Menu entry is written by Windows' own PowerShell, not by whatever
answers to that name first.

SEC-007. `subprocess.run(["powershell", ...])` resolves the name against the
current directory and PATH before it ever reaches System32, and the program
ships as a single executable the player drops wherever they like -- Downloads
among them. A powershell.exe sitting beside it would have been run instead,
with this module's own arguments.
"""

from __future__ import annotations

import os
import pathlib
import subprocess

import pytest

from nrplanner import shortcut


def test_the_interpreter_is_taken_from_the_windows_folder():
    found = shortcut.powershell_path()
    if found is None:
        pytest.skip("this machine has no %SystemRoot% PowerShell to find")
    assert found.is_absolute()
    assert found.is_file()
    system_root = pathlib.Path(os.environ["SystemRoot"]).resolve()
    assert found.resolve().is_relative_to(system_root)


def test_no_system_root_means_no_interpreter(monkeypatch):
    monkeypatch.delenv("SystemRoot", raising=False)
    assert shortcut.powershell_path() is None


def test_an_interpreter_that_is_not_there_is_not_offered(tmp_path, monkeypatch):
    # A SystemRoot without a PowerShell under it: the path is checked for
    # existence, not assembled and hoped for.
    monkeypatch.setenv("SystemRoot", str(tmp_path))
    assert shortcut.powershell_path() is None


def test_the_shortcut_fails_with_a_message_when_powershell_is_missing(
        tmp_path, monkeypatch):
    """A missing interpreter costs the shortcut, never the program."""
    monkeypatch.setattr(shortcut, "available", lambda: True)
    monkeypatch.setattr(shortcut, "shortcut_path",
                        lambda: tmp_path / shortcut.SHORTCUT_NAME)
    monkeypatch.setattr(shortcut, "powershell_path", lambda: None)

    def refuse(*_args, **_kwargs):
        raise AssertionError("nothing may be started when the path is unknown")

    monkeypatch.setattr(subprocess, "run", refuse)
    message = shortcut.create()
    assert message
    assert "PowerShell" in message


def test_the_interpreter_is_started_by_its_full_path(tmp_path, monkeypatch):
    started: dict[str, list] = {}
    fake = tmp_path / "powershell.exe"
    fake.write_bytes(b"")

    monkeypatch.setattr(shortcut, "available", lambda: True)
    monkeypatch.setattr(shortcut, "shortcut_path",
                        lambda: tmp_path / shortcut.SHORTCUT_NAME)
    monkeypatch.setattr(shortcut, "powershell_path", lambda: fake)

    class Result:
        returncode = 0
        stdout = ""
        stderr = ""

    def capture(command, **_kwargs):
        started["command"] = command
        (tmp_path / shortcut.SHORTCUT_NAME).write_bytes(b"")
        return Result()

    monkeypatch.setattr(subprocess, "run", capture)
    assert shortcut.create() == ""
    assert started["command"][0] == str(fake)
    assert pathlib.Path(started["command"][0]).is_absolute()
