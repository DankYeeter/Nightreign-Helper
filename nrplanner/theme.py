"""The colours and sizes more than one part of the window uses, one name each.

A colour or size only one module uses stays in that module, next to what it paints.
"""

from __future__ import annotations

#: The gold the whole window uses for a section title.
ACCENT = "#d9b56a"
#: The same gold where it is the light itself: a title, a chosen entry.
ACCENT_BRIGHT = "#f3d99a"
#: The grey for text that explains rather than states.
MUTED = "#9a9db3"
#: A panel is a translucent fill over the window's picture (`backdrop`), so
#: these two carry their alpha: `#AARRGGBB`, which `QColor` and a style sheet
#: both read.
PANEL = "#12ffffff"
BORDER = "#24ffffff"
#: What a panel has behind it where there is no picture: a dialog, a popup,
#: a pixmap filled by hand.
SOLID = "#12152b"
#: The window colour under everything.
NIGHT = "#0a0d1f"
TEXT = "#eceaf4"
#: The face of a title. Named by family because none ships with the program:
#: the first one the machine has is the one used, and Windows has the first.
SERIF = '"Palatino Linotype", "Book Antiqua", "Cambria", "Georgia", serif'
# Purple against the gold of a selected card: the two states have to be told
# apart at a glance, and gold's opposite is the one colour the rest of the
# window never uses.
FAVOURITE = "#a86fe0"
GOOD = "#6fbf73"
BAD = "#d1655f"
#: Curses are a cost, and read in the same colour as one.
CURSE = BAD
#: A rolled curse or cost in a list or table cell; lighter than BAD so it
#: stays readable at cell size.
DEBUFF = "#e07a74"
DEEP = "#9a6fc4"

SLOT_COLOURS = {
    0: "#b4544e",   # Red
    1: "#4e7ab4",   # Blue
    2: "#c2a24a",   # Yellow
    3: "#5c9e63",   # Green
    4: "#d8d8d8",   # White -- wildcard
}

#: How a card shows that the pointer is standing on it: the Nightlord grid
#: (QA-154), the relic cards and the armament tiles (QA-157). Measured on the
#: Nightlord grid, whose cards share PANEL with the other two.
#:
#: The finding is not the hit area. Measured on 2026-09-06 on Windows under
#: Fusion at 150 % scale, at a 1600x900 logical-px window: every one of 3 420
#: probe points, one every 4 logical px over the whole 302x178 card, opened
#: that card -- the labels inside it ignore a press and Qt hands it to the
#: frame. What is dead is the 8 logical px between two neighbours, and a
#: reader had no way to see which side of that line he was on: a near miss
#: opened the wrong Nightlord and a miss opened nothing, and the grid looked
#: identical in both cases.
#:
#: So the marker is on the pointer rather than on the click. A third channel
#: again: fill only, edge untouched. Selection changes both, an Everdark twin
#: owns DEEP on the edge, and hover changes the one thing neither of those
#: two moves -- so the three states stay apart at a glance.
#:
#: **The value is measured, not chosen by eye.** Sampled off a grab of the
#: whole window -- a card grabbed alone lands its translucent selection fill
#: on a transparent pixmap and reads back as the colour the stylesheet names
#: rather than the colour a reader sees -- on Windows under Fusion at 150 %
#: scale, at a 1600x900 logical-px window. An unmarked card is (30, 31, 35)
#: and a chosen one composites to (64, 57, 42), a WCAG contrast of 1.440.
#: The first hover fill tried here, `#26272c`, composited to (38, 39, 44):
#: **1.105**, a step small enough that the screenshot had to be measured to
#: tell whether the pointer was on the card at all. That is not feedback.
#: This one composites to (51, 52, 60) -- **1.331** against an unmarked card,
#: nearly the 1.440 the selection's own fill manages, while staying the only
#: neutral of the three: the selection is the one warm thing on this grid and
#: keeps its gold edge as well, so hover and selection are apart by hue and
#: by border even where their luminance is close.
#:
#: Cooler fills were measured too and reach further -- `#334055` gives 1.572
#: and `#3a4a60` 1.825 -- but both put a new hue on a tab where DEEP already
#: means something on the edge of a card. That is the `ui-ux-designer`'s call
#: to make with these figures, not this file's.
HOVER_FILL = "#2cffffff"

#: What the Nightfarer's name is set in on its tile, in points (QA-155), in
#: the sidebar and in the favourite menu alike.
#:
#: The ten portraits carried no text at all, so a player had to click one and
#: read the answer somewhere else to find out whom he had picked. The name has
#: to fit the tile it names: the tile is `TILE_SIZE + TILE_PAD` wide and the
#: five columns of the grid have to stay inside the sidebar's 300 px floor, so
#: widening the tile would push the whole window's minimum out. Measured on
#: Windows under Fusion at 150 % scale, in logical px: the widest of the ten
#: names, `Undertaker`, asks 59 px at the default 9 pt, 54 at 8 and 44 at 7,
#: against the 52 px a 56 px tile has inside its border. Seven is the size at
#: which all ten stand whole; Qt shortens anything that does not fit and the
#: tooltip has carried the full name all along.
NAME_POINT_SIZE = 7


#: What a glass pane keeps between its edge and what it holds, in logical px.
PANE_PAD = 14


def as_glass(widget) -> None:
    """Make `widget` one of the translucent panes of the window.

    The fill and the edge are `#glassPane` in `STYLE`. A plain `QWidget`
    ignores a style sheet's background unless it is told to paint one.
    """
    from PySide6.QtCore import Qt

    widget.setObjectName("glassPane")
    widget.setAttribute(Qt.WA_StyledBackground, True)


#: The one style sheet of the application (`app.apply_appearance`). What a
#: single module paints stays in that module; this is what every control of
#: a kind shares, so a button is the same button on all seven views.
STYLE = f"""
QToolTip {{
    background: {SOLID}; color: {TEXT};
    border: 1px solid rgba(255, 255, 255, 50); padding: 4px 6px;
}}
QTabWidget::pane {{ border: 0; background: transparent; }}
QScrollArea {{ background: transparent; border: 0; }}
QScrollArea > QWidget > QWidget {{ background: transparent; }}
#glassPane {{
    background: rgba(255, 255, 255, 13);
    border: 1px solid rgba(255, 255, 255, 28);
    border-radius: 16px;
}}
QPushButton {{
    background: rgba(255, 255, 255, 20); color: {TEXT};
    border: 1px solid rgba(255, 255, 255, 40); border-radius: 8px;
    padding: 4px 12px;
}}
QPushButton:hover {{ background: rgba(255, 255, 255, 38); }}
QPushButton:pressed {{ background: rgba(255, 255, 255, 12); }}
QPushButton:disabled {{
    color: #6f7187; border-color: rgba(255, 255, 255, 18);
    background: rgba(255, 255, 255, 8);
}}
QPushButton:default, QPushButton#primary {{
    color: #231a08; border: 1px solid {ACCENT};
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {ACCENT_BRIGHT}, stop:1 {ACCENT});
}}
QPushButton#primary:disabled {{
    color: #6f7187; border-color: rgba(255, 255, 255, 18);
    background: rgba(255, 255, 255, 8);
}}
QComboBox, QLineEdit, QSpinBox {{
    background: rgba(0, 0, 0, 80); color: {TEXT};
    border: 1px solid rgba(255, 255, 255, 34); border-radius: 8px;
    padding: 2px 6px;
    selection-background-color: {ACCENT}; selection-color: #14150f;
}}
QComboBox:hover, QLineEdit:hover {{ border-color: rgba(255, 255, 255, 70); }}
QComboBox:focus, QLineEdit:focus {{ border-color: {ACCENT}; }}
QComboBox::drop-down {{ border: 0; width: 20px; }}
QComboBox QAbstractItemView {{
    background: {SOLID}; color: {TEXT};
    border: 1px solid rgba(255, 255, 255, 50);
    selection-background-color: rgba(217, 181, 106, 90);
    selection-color: {ACCENT_BRIGHT}; outline: 0;
}}
QListView, QTreeView, QTableView, QTextEdit, QTextBrowser, QPlainTextEdit {{
    background: rgba(0, 0, 0, 70); color: {TEXT};
    alternate-background-color: rgba(255, 255, 255, 8);
    border: 1px solid rgba(255, 255, 255, 26); border-radius: 10px;
    selection-background-color: rgba(217, 181, 106, 90);
    selection-color: {ACCENT_BRIGHT}; outline: 0;
    gridline-color: rgba(255, 255, 255, 16);
}}
QHeaderView {{ background: transparent; }}
QHeaderView::section {{
    background: rgba(255, 255, 255, 14); color: {ACCENT};
    border: 0; border-bottom: 1px solid rgba(255, 255, 255, 30);
    padding: 5px 8px;
}}
QTableCornerButton::section {{ background: transparent; border: 0; }}
QMenu {{
    background: {SOLID}; color: {TEXT};
    border: 1px solid rgba(255, 255, 255, 50); padding: 4px;
}}
QMenu::item {{ padding: 5px 18px; border-radius: 6px; }}
QMenu::item:selected {{
    background: rgba(217, 181, 106, 90); color: {ACCENT_BRIGHT};
}}
QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 2px; }}
QScrollBar::handle {{
    background: rgba(255, 255, 255, 46); border-radius: 3px;
    min-height: 28px; min-width: 28px;
}}
QScrollBar::handle:hover {{ background: rgba(217, 181, 106, 150); }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}
QSplitter::handle {{ background: transparent; }}
QSlider::groove:horizontal {{
    height: 4px; border-radius: 2px; background: rgba(255, 255, 255, 36);
}}
QSlider::sub-page:horizontal {{
    border-radius: 2px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #a98bff, stop:1 {ACCENT});
}}
QSlider::handle:horizontal {{
    width: 14px; margin: -6px 0; border-radius: 7px;
    background: {ACCENT_BRIGHT}; border: 1px solid {ACCENT};
}}
QCheckBox::indicator {{
    width: 14px; height: 14px; border-radius: 4px;
    border: 1px solid rgba(255, 255, 255, 70); background: rgba(0, 0, 0, 80);
}}
QCheckBox::indicator:checked {{
    background: {ACCENT}; border-color: {ACCENT_BRIGHT};
}}
"""
