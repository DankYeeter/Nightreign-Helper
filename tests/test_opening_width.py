"""How wide the window opens, and why that width and not another.

The window used to open at 1320 logical px, a number set by hand. At that
width exactly one of the eleven effect-table headings was shortened -- and it
was the widest one, `Comes with curse`, drawn as `Comes with c…`. Two
`power-user` runs in a row reported it as the first thing they could not read
(T-066, T-069), and a third reading of it opened a regression investigation
against a release that had no regression (T-070).

**What is asserted here is a rule, not a figure.** The width a table needs
depends on the data, the style and the font, and none of the three is the
same on two machines: measured on 2026-09-06 in this tree, the nine middle
columns want 848 px together under Segoe UI 9 on Windows at 150 % scale and
1 185 px under the font the suite renders with. A case carrying either figure
would be a case about one machine. So every case below asks the table what it
needs and then checks the window against that answer.

**Why `room` is passed in.** The desktop bounds the opening width, and the
desktop under the offscreen platform is 800 px -- narrower than the window's
own minimum. Handing the bound in lets a case ask what the window would do on
a desktop that is not this one, which is the question the rule is about.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QTabWidget

from nrplanner import app as appmod

from tests import rendered

#: How far past the width under test a case looks for a heading it could
#: still have had. Wide enough that every column would reach its cap.
FURTHER = 400


def drawn_headings(table) -> list[str]:
    """The headings as the header draws them right now, ellipses included."""
    return [table.horizontalHeaderItem(column).text()
            for column in range(table.columnCount())]


def header_at(table, viewport_width: int) -> list[str]:
    """The header as it would read with the table's viewport this wide."""
    return table.headings_as_drawn(table.column_widths(viewport_width))


def test_the_width_the_table_asks_for_is_the_last_pixel_that_buys_a_heading(
        game_data, qapp):
    """Tight in both directions, which is the whole of the derivation.

    One pixel wider must buy the reader nothing -- otherwise the window opens
    too narrow, which is the finding. One pixel narrower must cost him a name
    -- otherwise the window opens wider than it needs to and eats desktop for
    nothing.

    Both are asked of `column_widths`, the share-out the table really
    applies, so a font under which some heading can never be drawn whole is
    handled by the same two statements rather than by a special case.
    """
    with rendered.laid_out(game_data, "effects_tab", 1250) as (_, tab):
        table = tab.table
        width = table.width_for_full_headings()

        assert header_at(table, width) == header_at(table, width + FURTHER), (
            f"at {width} px the header reads {header_at(table, width)} and "
            f"{FURTHER} px wider it reads {header_at(table, width + FURTHER)} "
            f"-- so this is not the width at which the headings read as well "
            f"as they can")
        assert header_at(table, width - 1) != header_at(table, width), (
            f"one pixel narrower reads exactly the same "
            f"({header_at(table, width)}), so {width} px is wider than the "
            f"table needs")


def test_the_window_opens_wide_enough_that_more_width_would_add_nothing(
        game_data, qapp):
    """The claim in the reader's terms, read off the drawn header.

    Not off `column_widths` this time: what the finding was about is the word
    a reader sees in the header, so this case widens a real window and
    compares the two headers as they are drawn.
    """
    with rendered.laid_out(game_data, "effects_tab", 1250) as (window, tab):
        opening = window._opening_width(room=10_000)
        window.resize(opening, appmod.OPENING_HEIGHT)
        rendered.settle()
        assert window.width() == opening, (
            f"this platform will not give the window {opening} px, so the "
            f"header measured here is not the header this case is about")
        at_opening = drawn_headings(tab.table)

        window.resize(opening + FURTHER, appmod.OPENING_HEIGHT)
        rendered.settle()

        assert at_opening == drawn_headings(tab.table), (
            f"at its opening width the header reads {at_opening}, and "
            f"{FURTHER} px wider it reads {drawn_headings(tab.table)} -- the "
            f"window opens too narrow to read what it could")


def test_the_opening_width_does_not_depend_on_which_tab_is_in_front(
        game_data, qapp):
    """The program opens on the Build planner, not on the effects tab.

    The width is read off the effect table, and a tab that is not in front
    has never been given the width of a page: measured on 2026-09-06 on
    Windows under Fusion at 150 % scale, the same code said 1 350 px with the
    effects tab in front and 1 802 -- cut to the screen's 1 707 -- with the
    Build planner in front, which is the tab a player actually starts on.
    Every other case in this file opens the effects tab first and would have
    passed on either.

    **Read at `showEvent` and on a desktop wide enough to grant it.** The
    width the window ends up at is bounded by the screen and by its own
    layout, and under the offscreen platform both bounds bite at once: the
    desktop is 800 px and the window floor 988, so every width above the
    floor comes out as 988 and the two arrangements agree whatever the code
    does. Measured: a mutation reading the width off the effects tab survived
    a case written that way.
    """
    from tests.conftest import clear_settings

    class Watched(appmod.Planner):
        """Says what width it asked for on the way to the screen."""

        asked_for = 0

        def showEvent(self, event):  # noqa: N802 - Qt naming
            self.asked_for = self._opening_width(room=10_000)
            super().showEvent(event)

    asked = {}
    for front in ("effects_tab", "the tab the program opens on"):
        clear_settings()
        window = Watched(game_data)
        try:
            if front == "effects_tab":
                window.findChild(QTabWidget).setCurrentWidget(
                    window.effects_tab)
            window.show()
            rendered.settle()
            asked[front] = window.asked_for
        finally:
            window.close()
            window.deleteLater()
            rendered.settle(2)

    assert len(set(asked.values())) == 1, (
        f"the window asks for a different width depending on the tab in "
        f"front: {asked}")


def test_the_window_does_not_open_wider_than_the_desktop(game_data, qapp):
    """A window past the edge of the screen is worse than a short heading.

    The floor is the second half of it: where the desktop is narrower than
    the window's own minimum there is no width that satisfies both, and the
    minimum is what the program can actually honour.
    """
    with rendered.laid_out(game_data, "effects_tab", 1250) as (window, _):
        floor = window.minimumSizeHint().width()
        for desktop in (640, 1024, floor + 1):
            assert window._opening_width(room=desktop) <= max(desktop, floor), (
                f"on a {desktop} px desktop the window would open "
                f"{window._opening_width(room=desktop)} px wide")


def test_the_window_never_opens_below_the_width_its_layout_needs(
        game_data, qapp):
    with rendered.laid_out(game_data, "effects_tab", 1250) as (window, _):
        assert (window._opening_width(room=1)
                == window.minimumSizeHint().width())


def test_the_window_puts_itself_at_its_opening_size_on_the_way_to_the_screen(
        game_data, qapp):
    """`showEvent` and not `__init__`, and only when nobody asked for a size."""
    from tests.conftest import clear_settings

    clear_settings()
    window = appmod.Planner(game_data)
    try:
        window.findChild(QTabWidget).setCurrentWidget(window.effects_tab)
        window.show()
        rendered.settle()
        assert window.width() == window._opening_width()
        assert window.height() == appmod.OPENING_HEIGHT
    finally:
        window.close()
        window.deleteLater()
        rendered.settle(2)


def test_a_window_that_was_given_a_size_opens_at_that_size(game_data, qapp):
    """The opening width is an opening width, not an override.

    Every geometry case in this suite sizes the window before showing it, and
    a program that restores a remembered geometry one day will do the same.
    Neither may be overruled by the opening size.

    **The width is checked before the window is shown, and the skip is on
    that check alone.** A skip after `show()` would swallow the very failure
    this case is for: an opening size that overrules its caller leaves the
    window at some other width, which reads exactly like a platform that
    would not grant 1100 px -- and the case would step aside instead of
    failing. Measured: with that guard after `show()`, a mutation removing
    the `WA_Resized` check survived.
    """
    from tests.conftest import clear_settings

    clear_settings()
    window = appmod.Planner(game_data)
    try:
        window.findChild(QTabWidget).setCurrentWidget(window.effects_tab)
        window.resize(1100, 700)
        if window.width() != 1100:
            pytest.skip(
                f"this window's layout will not go to 1100 logical px: it is "
                f"{window.width()} px before it has even been shown, so this "
                f"case has no request to see honoured")

        window.show()
        rendered.settle()

        assert window.width() == 1100, (
            f"the window was asked for 1100 px and came to the screen at "
            f"{window.width()} px, so the opening size overrules its caller")
    finally:
        window.close()
        window.deleteLater()
        rendered.settle(2)
