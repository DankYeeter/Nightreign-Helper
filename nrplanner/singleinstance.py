"""One copy of the program at a time.

Nothing stopped a second copy from starting. Two of them open at the same
size, in the same place, under the same title, and a reader cannot tell them
apart on screen: measured on 2026-09-06 on Windows, both windows came up at
[60, 60, 1320, 860], and a click aimed at the front one was taken by the back
one -- the front window stayed on `Select a Nightlord` while the other opened
the Nightlord. The report that followed said "I clicked the card and nothing
happened", and cost a full regression investigation that found no regression
(QA-163, T-070).

They also write the same settings, so the copy that is closed last decides
what the next launch reads.

So the second copy does not open a window. It finds the one already running,
brings it forward and ends -- which is what a double-click on the shortcut
means when the program is already there.

**The claim outlives nothing.** Windows drops a shared-memory segment when
the last process holding it goes, crash included, so a copy that dies without
tidying up does not lock the next one out.
"""

from __future__ import annotations

import sys

from PySide6.QtCore import QSharedMemory

#: The name the running copy is known by. Machine-wide, so it carries the
#: program's name rather than a generic one.
KEY = "NightreignHelper-running-copy"

#: Bytes of the segment that hold the running window's handle. Eight, because
#: a Windows handle is pointer-sized and this program runs 64-bit.
HANDLE_BYTES = 8

_BYTE_ORDER = "little"


def raise_window(handle: int) -> bool:
    """Bring the window with this native handle to the front.

    Windows only, and it says so rather than pretending: everything else this
    program does is portable Qt, but there is no portable way to reach into
    another process's window. On a platform without the call the second copy
    still ends -- which is the half of this that matters -- and returns False
    so a caller can tell the difference.
    """
    if sys.platform != "win32" or handle <= 0:
        return False
    import ctypes

    user32 = ctypes.windll.user32
    if not user32.IsWindow(handle):
        return False
    # A minimised window has to be restored before it can be raised; SW_RESTORE
    # puts it back at the size it had rather than maximising it.
    SW_RESTORE = 9
    if user32.IsIconic(handle):
        user32.ShowWindow(handle, SW_RESTORE)
    return bool(user32.SetForegroundWindow(handle))


class RunningCopy:
    """The claim that this process is the copy of the program that runs.

    `activate` is the way the window of an already-running copy is brought
    forward, and it is a parameter so a test can watch what handle it is
    given: the act of raising a window is the one part of this that cannot be
    observed from inside the process that asks for it.
    """

    def __init__(self, key: str = KEY, activate=raise_window):
        self._memory = QSharedMemory(key)
        self._activate = activate
        self._claimed = False

    def claim(self) -> bool:
        """Try to become the running copy. True if this process is it.

        False only where the segment is already there, which is another copy
        holding it. Any other failure -- a refused permission, a store that
        will not make the segment -- is answered with True and the program
        starts: a copy that will not run because a shared-memory segment could
        not be created would be a worse fault than the one being prevented,
        and nothing here is load-bearing for correctness.
        """
        if self._memory.create(HANDLE_BYTES):
            self._claimed = True
            self.announce(0)
            return True
        return self._memory.error() != QSharedMemory.AlreadyExists

    def announce(self, handle: int) -> None:
        """Record the handle of this copy's window for the next one to find."""
        if not self._claimed:
            return
        self._memory.lock()
        try:
            self._memory.data()[:HANDLE_BYTES] = int(handle).to_bytes(
                HANDLE_BYTES, _BYTE_ORDER)
        finally:
            self._memory.unlock()

    def running_handle(self) -> int:
        """The window handle the running copy announced, or 0.

        Zero has a meaning of its own and is not an error: the running copy
        has claimed the segment but has not put a window on screen yet. There
        is then nothing to raise, and this copy still steps aside rather than
        opening a second window.
        """
        if not (self._memory.isAttached() or self._memory.attach()):
            return 0
        self._memory.lock()
        try:
            return int.from_bytes(
                bytes(self._memory.constData())[:HANDLE_BYTES], _BYTE_ORDER)
        finally:
            self._memory.unlock()

    def raise_the_running_one(self) -> bool:
        """Bring the copy that is already running to the front."""
        return self._activate(self.running_handle())

    def release(self) -> None:
        """Let go of the claim. Windows does this at exit anyway."""
        self._memory.detach()
        self._claimed = False
