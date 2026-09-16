"""One English sentence per kind of failure, whatever language Windows speaks.

A8 says every text in the window is English, and an exception's own text is
the one text in this program that is not written here. `OSError` carries what
`FormatMessageW` returned, and on a German Windows that is German; a
third-party library writes whatever it likes. Neither can be seen by the
source-text guard (`tests/test_interface_language.py`), because neither is in
the source, and neither shows up in the window-text guard, because no ordinary
run provokes it (QA-211).

So no exception hands its own words to the player. What the player is shown is
written here and keyed on **what kind of failure it was** -- the class, and
for an `OSError` the `errno`, which is a number and speaks no language.

**The one exception, and the reason it is safe.** An exception class this
program defines carries a message this program wrote: `SaveNotReadable` says
"the file could not be opened" because a line of this repository says so.
Those texts are source literals, which is exactly what the source-text guard
of A8 already reads. Any other class -- `builtins`, `struct`, PySide6,
pycryptodome -- is mapped, never quoted.

**What must not be lost on the way.** `strerror` is the half of an `OSError`
that says *what* happened rather than *where* (AK-126), and dropping it for a
single "something went wrong" would buy A8 at the price of A7. The table below
is that sentence, written once per case, in English.
"""

from __future__ import annotations

import errno
import struct
import subprocess

#: The packages whose exception classes are this program's own. A class from
#: one of these was given its message by a line of this repository; a class
#: from anywhere else was given its message by Windows or by a library.
OUR_OWN_PACKAGES = ("nrplanner", "nrdata")

#: Said when the class is ours but somebody raised it with nothing to say.
NOTHING_WAS_SAID = "It failed without saying why."

#: What `strerror` would have said, in this program's own words, one case at a
#: time. Keyed on `errno`, which Python fills in from the operating system's
#: code and which carries no language.
WHAT_THE_SYSTEM_REFUSED = {
    errno.ENOENT: "It is not there any more.",
    errno.EACCES: "Windows would not allow access to it.",
    errno.EPERM: "Windows would not allow that operation.",
    errno.EBUSY: "Another program has it open.",
    errno.EEXIST: "Something is already there under that name.",
    errno.EISDIR: "That is a folder, not a file.",
    errno.ENOTDIR: "Part of that path is not a folder.",
    errno.ENOTEMPTY: "That folder still has something in it.",
    errno.ENOSPC: "There is no room left on the disk.",
    errno.EROFS: "The disk is write-protected.",
    errno.EMFILE: "Too many files are open at once.",
    errno.ENFILE: "Too many files are open at once.",
    errno.ENAMETOOLONG: "The path is longer than Windows accepts.",
    errno.EINVAL: "Windows rejected that path as invalid.",
    errno.EIO: "The drive reported a read or write error.",
    errno.ELOOP: "The path leads round in a circle of shortcuts.",
    errno.EXDEV: "That would move something between two drives.",
    errno.ETIMEDOUT: "The drive did not answer in time.",
    errno.ECONNRESET: "The network drive dropped the connection.",
    errno.ENETDOWN: "The network the drive is on is down.",
    errno.ENETUNREACH: "The network drive cannot be reached.",
    errno.EHOSTUNREACH: "The machine the drive is on cannot be reached.",
    errno.EPIPE: "The other end closed the connection.",
}

#: Failures that are not the operating system refusing something. Checked in
#: order and by `isinstance`, so a subclass lands on its base's sentence.
WHAT_WENT_WRONG = (
    (struct.error,
     "The file ends in the middle of something this had to read."),
    (subprocess.TimeoutExpired,
     "The command Windows was asked to run did not finish in time."),
    (MemoryError,
     "There was not enough memory to finish that."),
    (RecursionError,
     "This program lost its way working that out."),
    (UnicodeError,
     "Some of the text in it is not written in an encoding this can read."),
)


def in_english(exc: BaseException) -> str:
    """One English sentence for this failure. Never the exception's own text.

    Total by construction: every branch ends in a sentence, so a caller can
    put the answer straight on the surface without a fallback of its own.
    """
    if _is_one_of_ours(exc):
        return str(exc).strip() or NOTHING_WAS_SAID
    if isinstance(exc, OSError):
        return _what_the_system_said(exc)
    for kind, sentence in WHAT_WENT_WRONG:
        if isinstance(exc, kind):
            return sentence
    return (f"Something went wrong that this program has no sentence for "
            f"({_a_name_safe_to_show(exc)}).")


def _is_one_of_ours(exc: BaseException) -> bool:
    """Was this class defined in this program, and so worded in English?

    The module of the **class**, not of the raising line: a `ValueError` that
    a line of this repository raised is still `builtins.ValueError` and still
    indistinguishable from one pycryptodome raised, which is why the classes
    whose words are meant to be read are classes of this program's own.
    """
    return type(exc).__module__.split(".")[0] in OUR_OWN_PACKAGES


def _what_the_system_said(exc: OSError) -> str:
    """The `errno` half of an `OSError`, said in English.

    Never `exc.strerror` and never `str(exc)`: the first is in the language of
    the Windows installation, the second is that plus the whole path, whose
    folder is named after the Steam account id (AK-126).
    """
    said = WHAT_THE_SYSTEM_REFUSED.get(exc.errno)
    if said:
        return said
    code = errno.errorcode.get(exc.errno)
    if code:
        return f"Windows refused it, reporting {code}."
    return "Windows refused it and gave no reason this program can name."


def _a_name_safe_to_show(exc: BaseException) -> str:
    """The class name, when it is a plain ASCII identifier and nothing else.

    A class name is not a text a translator ever touches, but it is the one
    thing here that comes from outside this program, and a name is cheap to
    check. Anything unexpected becomes no name rather than an unknown text.
    """
    name = type(exc).__name__
    return name if name.isascii() and name.isidentifier() else "unnamed"
