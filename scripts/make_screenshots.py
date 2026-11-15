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

**The background is always "Roundtable Hold", the one the program starts
with.** It is a picture out of the game's own files, read from the install on
this machine, and this repository is public; that it is shown here all the
same is the owner's decision of 2026-11-15, taken knowing that. The guide
names the game and its owners above the pictures. Where the install holds no
such picture the painted "Night sky" stands in, as it does in the program. The
choice, and the marks set for the Filters picture, go to a settings key of
this script's own (`NIGHTREIGN_SETTINGS_ORG`, unless the caller set one), so
the player's own background, builds and marks are neither read nor changed.

**No more of the game's prose than the pictures already carry** (A-010, A-013,
A-014 in docs/legal/AUFLAGEN.md). The Nightlords picture shows the ten card
descriptions and the description of the first Nightlord once more in the
detail panel, eleven blocks and not one more; the World Events picture shows
the first event of the list and never "Curse of the Demon / Libra", whose
card is the game's own text from top to bottom. Both entries are set here in
code. Look at the two pictures after a run, and at any new one, before they
are committed. The size stays 2156 x 1140, so a picture does not come to hold
more rows than it did.

The save is read in the background (AD-029 stage B, T-142); this script waits
for that read to end before touching a tab, or the Build planner shot would
show an empty stock instead of the save's own relics.
"""

import os
import pathlib
import sys
import time

# Before anything of nrplanner is imported: `favourites` reads it on import.
os.environ.setdefault("NIGHTREIGN_SETTINGS_ORG", "DankYeeterScreenshots")
# One picture pixel per window pixel, whatever Windows' display scaling says:
# at 125% the pictures came out 2695 x 1425 instead of WIDTH x HEIGHT.
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
# With the scaling off Qt would still size the text for the screen's own DPI,
# and the names in the list of views were cut short. 96 is Windows at 100%.
os.environ["QT_FONT_DPI"] = "96"

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from PySide6.QtCore import QEventLoop, Qt, QTimer
from PySide6.QtWidgets import QAbstractItemView, QApplication

from nrplanner import backdrop, effectfilterdialog, firstrun
from nrplanner.app import Planner
from nrplanner.datasource import load_data
from nrplanner.statsheet import SituationalRow

ROOT = pathlib.Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 2156, 1140

# Tab label -> file name. The labels carry Qt's && escape for the ampersand.
SHOTS = [
    ("Build planner", "build_planner.png"),
    ("Effects && chances", "effects.png"),
    ("Recommended effects", "recommended_effects.png"),
    ("Weapons && spells", "weapons.png"),
    ("Nightlords", "nightlords.png"),
    ("Deep of Night", "deep_of_night.png"),
    ("Red variants", "depth_weighting.png"),
    ("World Events", "world_events.png"),
]
#: The three pictures that are not a view of the whole main window.
CONDITIONS_SHOT = "conditions.png"
FILTERS_SHOT = "filters.png"
FIRST_START_SHOT = "first_start.png"


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


#: Ten times `run.run`'s worst measured real case (960 ms), the margin
#: `measure_picker_cards.py` uses for the advisor's own answer.
SAVE_READ_TIMEOUT_S = 10.0


def wait_for_the_save(app: QApplication, window,
                      timeout: float = SAVE_READ_TIMEOUT_S) -> None:
    """Let the window finish reading its save before anything is shot.

    Since T-142 (AD-029 stage B) the save is read in a background `QThread`;
    a window is complete before its relics are. Without this the Build
    planner tab would be photographed on an empty stock instead of the
    save's own relics -- a wrong picture, not a crash, the failure class
    T-132 found in `measure_picker_cards.py`.
    """
    deadline = time.monotonic() + timeout
    while window.save_reader.is_reading():
        app.processEvents(QEventLoop.AllEvents, 10)
        if time.monotonic() > deadline:
            raise SystemExit(
                f"the save was still being read after {timeout:.0f} s; "
                f"nothing to shoot")
    settle(app, 200)


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


def save(widget, path: pathlib.Path) -> None:
    if not widget.grab().save(str(path)):
        raise SystemExit(f"could not write {path}")
    print(f"  {path.name:<24} {path.stat().st_size / 1024:>6.0f} KB")


def dress_the_build_planner(app: QApplication, window) -> None:
    """Show the planner in use: the worn relics, and one condition ticked.

    An empty chalice shows the layout but not what the window is for. The
    worn build comes in through the button a player presses, and the first
    condition under "Conditional & situational" is ticked through its own
    box, so the picture shows a switch that is on beside those that are not.
    """
    # The first Nightfarer whose worn build brings a condition with it: one
    # that wears nothing in game would give the empty chalice back.
    for index in range(len(window.heroes)):
        if index != window.hero_index:
            window.select_hero(index)
            settle(app, 500)
        window.load_equipped()
        settle(app, 800)
        row = next(iter(window.stat_sheet.findChildren(SituationalRow)), None)
        if row is not None:
            row.check.setChecked(True)
            settle(app, 400)
            return


def off_screen(widget) -> None:
    """Keep a window off the desktop while it is photographed.

    A window that is really shown sits under the mouse pointer, and whatever
    row the pointer happens to rest on is photographed highlighted.
    """
    widget.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen)


def shoot_the_filters(app: QApplication, window, path: pathlib.Path) -> None:
    """The Filters window, with Favourite set on the first family heading.

    Built the way `Planner.open_effect_filters` builds it, but shown instead
    of run, so that it can be photographed. The mark is taken back at once.
    """
    if window.owned is None:
        print(f"  {path.name:<24} skipped: no save was read")
        return
    rows = effectfilterdialog.rows_from(
        window.owned, window.effects, window.effect_filters.families)
    dialog = effectfilterdialog.EffectFilterWindow(
        window.effect_filters, rows, "", window,
        symbol_of=window._symbol_of_effect)
    dialog.setModal(False)
    off_screen(dialog)
    dialog.show()
    settle(app, 600)
    family = next(iter(dialog._family_marks), None)
    if family is not None:
        dialog.family_favourite_box(family).click()
        dialog.tree.scrollToItem(dialog._family_marks[family][1],
                                 QAbstractItemView.ScrollHint.PositionAtTop)
        settle(app, 400)
    save(dialog, path)
    if family is not None:
        dialog.family_favourite_box(family).click()
    dialog.close()
    dialog.deleteLater()


def shoot_the_first_start(app: QApplication, path: pathlib.Path) -> None:
    """The loading window of the first start, with its bar a third full."""
    splash = firstrun._Window()
    off_screen(splash)
    splash.show_the_build(first_time=False)
    splash.show_the_share(firstrun.SHARES // 3)
    settle(app, 400)
    save(splash, path)
    splash.close()
    splash.deleteLater()


def main() -> None:
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs" / "screenshots"
    out.mkdir(parents=True, exist_ok=True)

    app = QApplication(sys.argv)
    window = Planner(load_data())
    window.backdrop.choose(backdrop.DEFAULT)
    window.backdrop_box.setCurrentIndex(
        max(0, window.backdrop_box.findData(window.backdrop.choice)))
    off_screen(window)
    window.resize(WIDTH, HEIGHT)
    window.show()
    wait_for_the_save(app, window)
    settle(app, 1500)

    # Level 15 rather than the slider's starting 1. At level 1 every figure on
    # the right-hand panel is single digits and the attack rating is a Common
    # weapon's base, which shows the layout but not what it is for. The level
    # is session state and is not written back to settings, so this changes
    # nothing the player would find later.
    window.level_slider.setValue(window.level_slider.maximum())
    settle(app, 400)

    tabs = window.tabs
    by_label = {tabs.tabText(i): i for i in range(tabs.count())}
    missing = [label for label, _f in SHOTS if label not in by_label]
    if missing:
        raise SystemExit(f"no such tab: {missing}  (have {list(by_label)})")

    for label, name in SHOTS:
        tabs.setCurrentIndex(by_label[label])
        settle(app)
        if label == "Build planner":
            dress_the_build_planner(app, window)
        if label == "Nightlords":
            # The detail panel is the tab, and it opens empty on "Select a
            # Nightlord". Picking the first one shows what selecting does.
            tab = tabs.currentWidget()
            if getattr(tab, "bosses", None):
                tab.show_detail(tab.bosses[0])
                settle(app, 500)
        if label == "World Events":
            # The first event, set here and not left to the tab's default
            # (A-013): see the module docstring for the card to keep out.
            tabs.currentWidget().list.setCurrentRow(0)
            settle(app, 500)
        if label == "Weapons && spells":
            # Since T-058 the tab opens with its first group already unfolded
            # (AK-83), so the picture is no longer three headings over an acre
            # of empty panel. This still opens the next folded group, because
            # a picture showing two of them says more about what the tab is
            # than a picture showing one.
            expand_first(app, tabs.currentWidget(), depth=2)
        save(window, out / name)

    tabs.setCurrentIndex(by_label["Build planner"])
    settle(app, 300)
    # The stat sheet alone, scrolled to its switches: in the picture of the
    # whole window they are below the fold.
    rows = window.stat_sheet.findChildren(SituationalRow)
    if rows:
        window.stat_sheet.ensureWidgetVisible(rows[-1])
        window.stat_sheet.ensureWidgetVisible(rows[0])
        settle(app, 300)
        save(window.stat_sheet, out / CONDITIONS_SHOT)
    shoot_the_filters(app, window, out / FILTERS_SHOT)
    shoot_the_first_start(app, out / FIRST_START_SHOT)

    print(f"\nscreenshots written to {out}")
    window.close()
    window.deleteLater()


main()
