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
from PySide6.QtWidgets import QApplication, QLabel, QProgressBar, QVBoxLayout, QWidget

from . import paths
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

            meta = json.loads(snapshot.read_text(encoding="utf-8")).get("meta", {})
            stamp = _regulation_stamp(game)
            if stamp and (
                meta.get("regulation_sha256") != stamp[0]
                or meta.get("regulation_size") != stamp[1]
            ):
                needed.append("snapshot")
        except Exception:  # noqa: BLE001 - an unreadable snapshot is a rebuild
            needed.append("snapshot")

    # Same for the icon pack: whichever one IconPack would find.
    from .iconpack import IconPack

    if not (IconPack.locate() / "manifest.json").exists():
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
        self.setFixedSize(460, 150)

        headline = (
            "Setting up Nightreign Helper"
            if first_time
            else "Your game was updated"
        )
        detail = (
            "Reading your installation. This happens once, and takes about a "
            "minute."
            if first_time
            else "Re-reading your installation so the numbers match the new "
            "version."
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

    window.close()
    return outcome.get("error") or None
