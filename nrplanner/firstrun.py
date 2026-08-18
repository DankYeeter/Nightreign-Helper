"""Building the local data set before the main window opens.

The program ships no game content, so on a machine that has never run it
there is nothing to show until the installed game has been read. That takes
about a minute: roughly half extracting the params, half decoding the icon
atlases. Doing it silently would look like a hang, and doing it on every
launch would be intolerable, so it happens once, visibly, into the per-user
cache, and is reused until the game is patched.
"""

from __future__ import annotations

import pathlib
import traceback

from PySide6.QtCore import QObject, Qt, QThread, Signal
from PySide6.QtWidgets import (QApplication, QCheckBox, QLabel, QProgressBar,
                               QVBoxLayout, QWidget)

from . import paths, shortcut
from .datasource import bundled_path, defs_dir


def _regulation_stamp(game: pathlib.Path) -> tuple[str, int] | None:
    """Identify the installed game version, as (sha256, size)."""
    import hashlib

    path = game / "regulation.bin"
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_size


def what_is_needed(game: pathlib.Path | None) -> list[str]:
    """Which build steps have to run: any of "snapshot", "icons"."""
    if game is None:
        return []

    needed = []

    # Whichever snapshot the app would actually load -- the cache, or one
    # built beside the package in a source tree. Checking only the cache
    # would rebuild for a developer who already has a local snapshot.
    snapshot = bundled_path()
    if not snapshot.exists():
        needed.append("snapshot")
    else:
        # A patched game invalidates the snapshot. Hashing 2 MB costs a few
        # milliseconds, which is worth it to avoid a minute of rebuilding.
        try:
            import json

            from nrdata import extract

            meta = json.loads(snapshot.read_text(encoding="utf-8")).get("meta", {})
            stamp = _regulation_stamp(game)
            # Two ways to be out of date, and both have to rebuild here or the
            # cache is never written: a patched game, and a snapshot built by
            # an older version of this program's extractor.
            if meta.get("extract_version") != extract.EXTRACT_VERSION:
                needed.append("snapshot")
            elif stamp and (
                meta.get("regulation_sha256") != stamp[0]
                or meta.get("regulation_size") != stamp[1]
            ):
                needed.append("snapshot")
        except Exception:  # noqa: BLE001 - an unreadable snapshot is a rebuild
            needed.append("snapshot")

    # Same for the icon pack: whichever one IconPack would find.
    from .iconpack import IconPack

    icon_manifest = IconPack.locate() / "manifest.json"
    if not icon_manifest.exists():
        needed.append("icons")
    else:
        # A pack that exists is not necessarily a pack this build can use.
        # Rebuilding only when the manifest was missing meant an upgrading
        # player kept whatever an older build wrote: 1.5.0 draws chalice
        # slots and damage icons from sprites 1.4.0 never extracted, and
        # every existing installation would have come up without them.
        #
        # A manifest that cannot be read is left alone rather than rebuilt.
        # On this machine the icons directory intermittently refuses to
        # open -- see iconpack._read_with_retries -- and treating that as
        # "out of date" would rebuild the whole pack on every single launch,
        # which is far worse than keeping the pack already on disk.
        import json

        from nrdata import iconbuild

        from .iconpack import _read_with_retries

        raw = _read_with_retries(icon_manifest)
        if raw is not None:
            try:
                built = json.loads(raw.decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                needed.append("icons")
            else:
                if built.get("icon_version", 1) != iconbuild.ICON_VERSION:
                    needed.append("icons")

    return needed


class _Builder(QObject):
    """Runs the extraction off the GUI thread."""

    progress = Signal(str)
    finished = Signal(str)  # empty on success, else the error text

    def __init__(self, game: pathlib.Path, steps: list[str]) -> None:
        super().__init__()
        self.game = game
        self.steps = steps

    def run(self) -> None:
        try:
            defs = defs_dir()
            if defs is None:
                raise FileNotFoundError(
                    "The param definitions are missing, so the game cannot be "
                    "read. Reinstalling should restore them."
                )

            paths.cache_dir().mkdir(parents=True, exist_ok=True)

            if "snapshot" in self.steps:
                from nrdata import extract

                self.progress.emit("Reading the game's data tables ...")
                extract.write_snapshot(self.game, defs, paths.snapshot_path())

            if "icons" in self.steps:
                from nrdata import iconbuild

                self.progress.emit("Decoding artwork ...")
                iconbuild.build(
                    self.game,
                    defs,
                    paths.icons_dir(),
                    report=lambda line: self.progress.emit(line.strip()),
                )
        except Exception as exc:  # noqa: BLE001 - reported in the dialog
            traceback.print_exc()
            self.finished.emit(str(exc) or exc.__class__.__name__)
            return

        self.finished.emit("")


class _Window(QWidget):
    """A plain progress panel. Deliberately not a QProgressDialog: there is
    no cancelling a half-built cache into something usable, so there should
    be no cancel button offering to."""

    def __init__(self, first_time: bool) -> None:
        super().__init__(None, Qt.WindowType.SplashScreen)
        # Taller on the first run only, where the Start Menu offer appears.
        self.setFixedSize(460, 190 if first_time else 150)

        # The rebuild is no longer only for a patched game -- upgrading the
        # tool itself can need one too -- so the wording says what is being
        # done rather than guessing at the reason for it.
        headline = (
            "Setting up Nightreign Helper"
            if first_time
            else "Refreshing your game data"
        )
        detail = (
            "Reading your installation. This happens once, and takes about a "
            "minute."
            if first_time
            else "Re-reading your installation so the numbers are up to date."
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(10)

        title = QLabel(headline)
        font = title.font()
        font.setPointSize(font.pointSize() + 3)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        note = QLabel(detail)
        note.setWordWrap(True)
        layout.addWidget(note)

        bar = QProgressBar()
        bar.setRange(0, 0)  # no total is knowable, so keep it indeterminate
        bar.setTextVisible(False)
        layout.addWidget(bar)

        self.status = QLabel("")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)

        # This minute of setup is the closest thing the program has to being
        # installed, so it is the natural place to offer what an installer
        # would: an entry in the Start Menu. Offered rather than done, and only
        # on the first run -- a rebuild after a patch is not an install, and
        # putting the shortcut back after someone deleted it would be a program
        # overruling its user.
        #
        # Ticked by default. It is a single file in the user's own profile,
        # trivially undone from inside the program or by deleting it, and
        # someone who has just downloaded a tool almost always does want to be
        # able to find it again.
        self.shortcut_check = None
        if first_time and shortcut.available():
            self.shortcut_check = QCheckBox("Add to my Start Menu")
            self.shortcut_check.setChecked(True)
            self.shortcut_check.setToolTip(
                "Creates one shortcut in your own Start Menu. No admin "
                "rights, nothing installed, and removable from inside the "
                "program at any time."
            )
            layout.addWidget(self.shortcut_check)

    def wants_shortcut(self) -> bool:
        return bool(self.shortcut_check and self.shortcut_check.isChecked())


def ensure_data(game: pathlib.Path | None) -> str | None:
    """Build whatever is missing, showing progress. Returns an error or None.

    Returning None also covers "nothing needed to be done", which is the
    normal case on every launch after the first.
    """
    steps = what_is_needed(game)
    if not steps or game is None:
        return None

    window = _Window(first_time="snapshot" in steps and not bundled_path().exists())
    window.show()
    QApplication.processEvents()

    thread = QThread()
    builder = _Builder(game, steps)
    builder.moveToThread(thread)

    outcome: dict[str, str] = {}
    thread.started.connect(builder.run)
    builder.progress.connect(window.status.setText)
    builder.finished.connect(lambda err: outcome.setdefault("error", err))
    builder.finished.connect(thread.quit)

    thread.start()
    while not thread.wait(50):
        QApplication.processEvents()

    # Acted on after the build rather than before it, so a setup that fails
    # does not leave a Start Menu entry pointing at a program that cannot run.
    # A shortcut that cannot be written is not worth stopping for or reporting
    # here: the data is what the user is waiting on, and the button in the main
    # window says plainly whether the entry exists.
    if not outcome.get("error") and window.wants_shortcut():
        shortcut.create()

    window.close()
    return outcome.get("error") or None
