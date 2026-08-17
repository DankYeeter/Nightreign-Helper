"""Regenerate the README screenshots from the current build.

The set in docs/screenshots was shot by hand and went stale the moment a tab
changed -- by 1.2.0 the Deep of Night image showed a layout that no longer
existed. Doing it from code means the pictures are a build artefact like the
EXE: rerun this after a change and they are current, with no hand cropping and
no window chrome to line up.

Rendered off-screen at the size the existing set used, so replacing them does
not reflow the README.

    .venv\\Scripts\\python.exe scripts\\make_screenshots.py [outdir]

Note what ends up in these: the Build planner shot shows the relics the save on
this machine actually holds. That is intended -- the README says as much -- and
the one thing that must not appear, the Steam account id, is only ever in a
tooltip, never on the face of the window.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from PySide6.QtCore import QEventLoop, QTimer
from PySide6.QtWidgets import QApplication

from nrplanner.app import Planner
from nrplanner.datasource import load_data

ROOT = pathlib.Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 2156, 1140

# Tab label -> file name. The labels carry Qt's && escape for the ampersand.
SHOTS = [
    ("Build planner", "build_planner.png"),
    ("Effects && chances", "effects.png"),
    ("Weapons && spells", "weapons.png"),
    ("Nightlords", "nightlords.png"),
    ("Deep of Night", "deep_of_night.png"),
    ("Red variants", "depth_weighting.png"),
    ("World Events", "world_events.png"),
]


def settle(app: QApplication, ms: int = 900) -> None:
    """Let a tab finish building itself before it is photographed.

    Several tabs fill themselves lazily on first show, and grabbing too early
    catches a half-drawn table -- which is how the first attempt produced a
    Build planner with its attribute rows stacked on top of each other.
    """
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()
    app.processEvents()


def expand_first(app: QApplication, widget, depth: int = 1) -> None:
    """Open the first folding section, and the first inside it, and so on.

    Driven through the same toggle a click drives, so the body is built the
    way it is built for a player rather than by reaching past the widget.
    """
    from nrplanner.arsenaltab import Section

    for _ in range(depth):
        section = next((s for s in widget.findChildren(Section)
                        if not s.toggle.isChecked()), None)
        if section is None:
            return
        section.toggle.setChecked(True)
        section._on_toggle()
        settle(app, 700)
        widget = section.body


def main() -> None:
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs" / "screenshots"
    out.mkdir(parents=True, exist_ok=True)

    app = QApplication(sys.argv)
    window = Planner(load_data())
    window.resize(WIDTH, HEIGHT)
    window.show()
    settle(app, 1500)

    # Level 15 rather than the slider's starting 1. At level 1 every figure on
    # the right-hand panel is single digits and the attack rating is a Common
    # weapon's base, which shows the layout but not what it is for. The level
    # is session state and is not written back to settings, so this changes
    # nothing the player would find later.
    window.level_slider.setValue(window.level_slider.maximum())
    settle(app, 400)

    tabs = window.centralWidget()
    by_label = {tabs.tabText(i): i for i in range(tabs.count())}
    missing = [label for label, _f in SHOTS if label not in by_label]
    if missing:
        raise SystemExit(f"no such tab: {missing}  (have {list(by_label)})")

    for label, name in SHOTS:
        tabs.setCurrentIndex(by_label[label])
        settle(app)
        if label == "Nightlords":
            # The detail panel is the tab, and it opens empty on "Select a
            # Nightlord". Picking the first one shows what selecting does.
            tab = tabs.currentWidget()
            if getattr(tab, "bosses", None):
                tab.show_detail(tab.bosses[0])
                settle(app, 500)
        if label == "Weapons && spells":
            # This tab opens with every group folded, because building tens of
            # thousands of tiles up front stalls the window. Photographed as it
            # opens, it is three collapsed headings and an acre of empty panel
            # -- true, and useless as a picture of what the tab does. Two
            # clicks' worth of unfolding shows the armament tiles.
            expand_first(app, tabs.currentWidget(), depth=2)
        path = out / name
        if not window.grab().save(str(path)):
            raise SystemExit(f"could not write {path}")
        print(f"  {path.name:<22} {path.stat().st_size / 1024:>6.0f} KB")

    print(f"\n{len(SHOTS)} screenshots written to {out}")
    window.close()
    window.deleteLater()


main()
