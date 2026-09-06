"""One copy of the program at a time.

QA-163: nothing stopped a second copy from starting, and two of them are not
distinguishable on screen -- same size, same place, same title. A click aimed
at the front window was taken by the back one, and the report that came out of
it said "the program does not react".

**Each case uses a key of its own.** The claim is machine-wide by nature, so
two test runs at once on the same machine would otherwise take each other's
claim away -- the same fault the settings store was given per-process names
for (QA-043). The key carries the process id for that reason.

**What is not covered here.** Bringing another process's window to the front
is a call into Windows, and no case in this suite can watch a window it does
not own come forward. So the handle is followed as far as the boundary: the
cases prove that the second copy stands down and that it asks for the right
window. The step past the boundary was checked by hand and is written up in
the T-071 report, not asserted here.
"""

from __future__ import annotations

import os

import pytest

from nrplanner import singleinstance


@pytest.fixture
def key() -> str:
    """A claim name no other run on this machine will be using."""
    return f"NightreignHelperTests-{os.getpid()}-{id(object())}"


def test_the_first_copy_gets_the_claim(key):
    first = singleinstance.RunningCopy(key)
    try:
        assert first.claim() is True
    finally:
        first.release()


def test_a_second_copy_is_refused_while_the_first_holds_it(key):
    first = singleinstance.RunningCopy(key)
    second = singleinstance.RunningCopy(key)
    try:
        assert first.claim() is True
        assert second.claim() is False, (
            "a second copy was allowed to start alongside the first, which "
            "is the finding")
    finally:
        second.release()
        first.release()


def test_the_claim_is_free_again_once_the_first_copy_lets_go(key):
    """Otherwise a crash would lock the player out until he rebooted."""
    first = singleinstance.RunningCopy(key)
    assert first.claim() is True
    first.release()

    second = singleinstance.RunningCopy(key)
    try:
        assert second.claim() is True, (
            "the claim outlived the copy that made it, so the program cannot "
            "be started again")
    finally:
        second.release()


def test_the_second_copy_is_told_which_window_to_raise(key):
    """The handle goes across the claim, so no guessing by title is needed.

    Two copies of this program have the same window title, so a second copy
    that searched for one by name could not tell which it had found.
    """
    asked = []
    first = singleinstance.RunningCopy(key)
    second = singleinstance.RunningCopy(key, activate=asked.append)
    try:
        assert first.claim() is True
        first.announce(0xBEEF)
        assert second.claim() is False

        second.raise_the_running_one()
        assert asked == [0xBEEF], (
            f"the second copy asked to raise {asked}, not the window the "
            f"first one announced")
    finally:
        second.release()
        first.release()


def test_a_copy_that_has_no_window_yet_is_asked_to_raise_nothing(key):
    """Zero is an answer, not a failure: the first copy has claimed the name
    but has not been to the screen yet. The second copy still stands down --
    a handle it cannot raise is no reason to open a second window."""
    asked = []
    first = singleinstance.RunningCopy(key)
    second = singleinstance.RunningCopy(key, activate=asked.append)
    try:
        assert first.claim() is True
        assert second.claim() is False
        second.raise_the_running_one()
        assert asked == [0]
    finally:
        second.release()
        first.release()


def test_a_copy_that_never_claimed_announces_nothing(key):
    """A copy standing down must not write into the claim it lost.

    It is attached to the segment to read the handle out of it; a write from
    there would put its own handle where the running copy's belongs, and the
    next copy to start would be sent to a window that no longer exists.
    """
    first = singleinstance.RunningCopy(key)
    second = singleinstance.RunningCopy(key)
    try:
        assert first.claim() is True
        first.announce(0x1234)
        assert second.claim() is False
        second.announce(0x9999)

        assert second.running_handle() == 0x1234, (
            "a copy that lost the claim overwrote the running copy's window "
            "handle")
    finally:
        second.release()
        first.release()


def test_raising_a_window_that_is_not_one_says_so_rather_than_throwing():
    """`main` calls this on the way out and cannot afford an exception.

    Zero and a handle no window answers for are the two cases a second copy
    actually meets -- the first copy has not drawn yet, or has just gone.
    """
    assert singleinstance.raise_window(0) is False
    assert singleinstance.raise_window(-1) is False
