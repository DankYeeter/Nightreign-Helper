"""The window as a rail of views over one picture (the glass look).

What is held here is what a player would notice going wrong: a view that has
no entry in the rail, an entry that opens the wrong view, a tab bar back on
screen beside the rail, and a window with no picture behind it.
"""

from __future__ import annotations

from PySide6.QtCore import QSize
from PySide6.QtGui import QColor, QImage
from PySide6.QtWidgets import QTabWidget

from nrplanner import backdrop, paths


def _tabs(window) -> QTabWidget:
    return window.findChild(QTabWidget)


def test_every_view_has_an_entry_in_the_rail(planner):
    tabs = _tabs(planner)
    buttons = planner.rail.group.buttons()
    assert len(buttons) == tabs.count() >= 3
    for index in range(tabs.count()):
        assert planner.rail.full_name(index) == tabs.tabText(index)


def test_an_entry_opens_its_view_and_shows_it_chosen(planner):
    tabs = _tabs(planner)
    for index in reversed(range(tabs.count())):
        planner.rail.group.button(index).click()
        assert tabs.currentIndex() == index
        assert planner.rail.group.checkedId() == index


def test_a_view_brought_forward_elsewhere_is_marked_in_the_rail(planner):
    tabs = _tabs(planner)
    tabs.setCurrentIndex(tabs.count() - 1)
    assert planner.rail.group.checkedId() == tabs.count() - 1


def test_the_tab_bar_is_not_shown_beside_the_rail(planner):
    assert _tabs(planner).tabBar().isHidden()


def test_the_scale_box_and_reset_layout_live_in_the_rail(planner):
    assert planner.rail.isAncestorOf(planner.scale_box)


def test_the_painted_scene_fills_the_size_asked_for(qapp):
    scene = backdrop.painted_scene(QSize(640, 360))
    assert (scene.width(), scene.height()) == (640, 360)
    image = scene.toImage()
    # A night sky: dark at the top, and not one flat colour.
    top = image.pixelColor(320, 4)
    low = image.pixelColor(470, 330)
    assert top.lightness() < 40
    assert top != low


def test_a_picture_in_the_icon_pack_is_the_one_shown(qapp, tmp_path,
                                                     monkeypatch):
    monkeypatch.setattr(paths, "icons_dir", lambda: tmp_path)
    assert backdrop.game_scene(QSize(320, 180)) is None

    picture = QImage(64, 36, QImage.Format_RGB32)
    picture.fill(QColor("#ff0000"))
    picture.save(str(tmp_path / backdrop.backdrop_file(backdrop.DEFAULT)))
    scene = backdrop.game_scene(QSize(320, 180))
    assert (scene.width(), scene.height()) == (320, 180)
    shown = backdrop.veiled(scene).toImage().pixelColor(160, 170)
    # The picture, under the veil that keeps text readable: still red, and
    # darker than it was.
    assert shown.red() > shown.blue() + 40
    assert shown.red() < 255


def test_a_broken_picture_falls_back_to_the_painted_scene(qapp, tmp_path,
                                                          monkeypatch):
    monkeypatch.setattr(paths, "icons_dir", lambda: tmp_path)
    (tmp_path / backdrop.backdrop_file(backdrop.DEFAULT)).write_bytes(b"not a picture")
    assert backdrop.game_scene(QSize(320, 180)) is None


def test_the_background_list_offers_what_the_pack_holds(qapp, tmp_path,
                                                        monkeypatch):
    monkeypatch.setattr(paths, "icons_dir", lambda: tmp_path)
    assert backdrop.available() == [(backdrop.PAINTED, backdrop.PAINTED_LABEL)]

    picture = QImage(64, 36, QImage.Format_RGB32)
    picture.fill(QColor("#00ff00"))
    picture.save(str(tmp_path / backdrop.backdrop_file("augur")))
    assert [key for key, _label in backdrop.available()] == [
        "augur", backdrop.PAINTED]


def test_every_listed_background_is_one_the_icon_build_writes():
    from nrdata import iconbuild
    assert [key for key, _label in backdrop.BACKDROPS] == list(
        iconbuild.BACKDROPS)


def test_choosing_a_background_shows_it_and_keeps_it(planner, tmp_path,
                                                     monkeypatch):
    monkeypatch.setattr(paths, "icons_dir", lambda: tmp_path)
    assert planner.rail.isAncestorOf(planner.backdrop_box)
    planner.backdrop.choose("augur")
    assert planner.backdrop.choice == "augur"
    assert backdrop.stored() == "augur"
    # A key nobody knows is not kept.
    planner.backdrop.choose("no such picture")
    assert backdrop.stored() == backdrop.DEFAULT
    # Chosen but not in this pack: the painted scene stands in.
    assert backdrop.game_scene(QSize(320, 180), "augur") is None


def test_a_choice_box_asks_for_its_longest_name_and_may_shrink(qapp):
    """"Normal + Deep" was cut to "Normal + Deeg" at 1600 px: the box asked
    for its minimum contents length only."""
    from PySide6.QtWidgets import QComboBox

    box = backdrop.ChoiceBox()
    box.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
    box.setMinimumContentsLength(4)
    box.addItems(["All", "Buffs and curses, a long name"])
    widest = box.fontMetrics().horizontalAdvance(box.itemText(1))
    assert box.sizeHint().width() > widest
    assert box.minimumSizeHint().width() < widest
