"""The Nightlords: what each one takes, what breaks it, and how it buffs itself.

The resistance figures this file once said were unreachable are here now --
`nrdata/bossdata.py` links the boss menu to an NpcParam row through the event
script and the map, and `nrdata/tae.py` says which animation applies a boss's
buff.

Each Nightlord is one entry, carrying its Everdark twin rather than appearing
twice. That is safe because the two are the same character with identical
figures; see `merge_everdark`.
"""

from __future__ import annotations

import pathlib

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QScrollArea,
    QVBoxLayout, QWidget,
)

ACCENT = "#c8a45c"
MUTED = "#8a8a8a"
PANEL = "#1e1f23"
BORDER = "#2e2f35"
DEEP = "#9a6fc4"
BAD = "#d1655f"
GOOD = "#6fbf73"
# Watched in play: above a wiki claim, below a param read.
OBSERVED_COLOUR = "#7fae72"

COLUMNS = 4
ICON = 64
CARD_WIDTH = 250

# What body part a numbered slot actually is, once someone has watched it.
#
# The files will not say. `partsDamageRate1..8` and `isWeakA..F` carry no
# description in the paramdef, and the AI scripts only ever number parts
# (`ANIME_ID_PART1_DAMAGE`), so anything anatomical here has to come from
# play. Keyed by (boss name, the label the extractor produced).
#
# There is a clean way to fill this in: a weak-part hit plays its own
# reaction, so hitting each part in turn and watching for it identifies the
# slot. Add entries only from an actual sighting -- a guess here would read
# exactly like a fact.
PART_NAMES: dict[tuple[str, str], str] = {}

# Bosses seen to take the attack-down / defence-down debuff when broken. Not
# all of them do -- Gnoster shows nothing at all -- and the files never say
# who gets it, so this is a sighting list. Showing the line for every boss
# would put a flat lie on the page.
DEBUFF_ON_BREAK = {"Gladius", "Heolstor the Nightlord", "Caligo"}

# What sets a boss's self-buff off. The files give the animation id and never
# what provokes it, so these are sightings. Only bosses actually watched are
# listed; the rest show the buff with no trigger claimed.
# What sets a defence buff off, keyed by the exact effect rather than the
# boss: Libra has two and only one of them is the bubble. Keying by boss would
# have put the bubble note against both.
DEFENCE_TRIGGER = {
    ("Libra", 45852): ("finishing the bubble cast — pop the bubble and it "
                       "never lands"),
}

BUFF_TRIGGER = {
    "Gladius": ("during the taunt walk, which only happens once he has merged "
                "into one body — every attack he takes during it adds a stack"),
    "Adel": "when he bites and inflicts blood loss",
    "Libra": "after a madness proc",
    "Straghess": "seemingly tied to how many adds are alive — least certain",
}

# Caveats on the weakness interaction itself, from play. Only the three that
# change how you use the weakness are kept -- the rest of what was recorded
# here is now implied by the panel's own structure: a boss with no debuff rows
# is a boss that does not take the debuff, and the Tell row says what to watch
# for on the ones that do.
WEAKNESS_NOTE = {
    "Gladius": ("While he is split into hounds, each one takes the debuff "
                "separately."),
    "Adel": ("Phase 1 only — the poison stagger is gone in phase 2 and in the "
             "Everdark version."),
    "Fulghor": ("Lightning during his charged attack knocks him out of the "
                "charge, and the attack then lands with none of it."),
}


def merge_everdark(bosses: list[dict]) -> list[dict]:
    """One entry per Nightlord, carrying its Everdark twin rather than
    repeating it.

    The two are the same character -- Gladius Everdark still resolves to
    c7500 -- and every extracted figure is identical between them, so two
    rows said the same thing twice. Straghess and Heolstor ship no Everdark
    version and pass through untouched.

    Merging here rather than in the snapshot keeps `nightreign_data.json`
    a plain record of what the files say; the pairing is a presentation
    choice and belongs on this side of the line.
    """
    everdark = {b["name"]: b for b in bosses if b.get("is_everdark")}
    out = []
    for boss in bosses:
        if boss.get("is_everdark"):
            continue
        merged = dict(boss)
        merged["everdark"] = everdark.get(boss["name"])
        out.append(merged)
    return out


def _split_circle(regular, sovereign, size: int):
    """One circle, halved on the top-left/bottom-right diagonal.

    Regular art fills the lower-left triangle and the Everdark art the
    upper-right, so a glance at the list says whether a boss has a Sovereign
    version at all. Same footprint as the plain badge it replaces.
    """
    canvas = QPixmap(size, size)
    canvas.fill(Qt.transparent)
    painter = QPainter(canvas)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.SmoothPixmapTransform)

    circle = QPainterPath()
    circle.addEllipse(0, 0, size, size)
    painter.setClipPath(circle)

    def half(pixmap, points):
        if pixmap is None:
            return
        painter.save()
        wedge = QPainterPath()
        wedge.moveTo(*points[0])
        for point in points[1:]:
            wedge.lineTo(*point)
        wedge.closeSubpath()
        painter.setClipPath(wedge, Qt.IntersectClip)
        scaled = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding,
                               Qt.SmoothTransformation)
        # Centre the crop, or the art drifts left on a non-square source.
        painter.drawPixmap(-(scaled.width() - size) // 2,
                           -(scaled.height() - size) // 2, scaled)
        painter.restore()

    half(regular, [(0, 0), (0, size), (size, size)])
    half(sovereign, [(0, 0), (size, 0), (size, size)])

    if regular is not None and sovereign is not None:
        pen = QPen(QColor(BORDER))
        pen.setWidthF(max(1.0, size / 48))
        painter.setPen(pen)
        painter.drawLine(0, 0, size, size)
    painter.end()
    return canvas


def _heading(text: str) -> QLabel:
    label = QLabel(text)
    label.setStyleSheet(
        f"color: {ACCENT}; font-size: 12px; font-weight: bold;"
        " letter-spacing: 1px;"
    )
    return label


class BossCard(QFrame):
    """One expedition: its icon, the boss it ends on, and the flavour text."""

    clicked = Signal(dict)

    def __init__(self, boss: dict, icons):
        super().__init__()
        self.boss = boss
        # A minimum rather than a fixed width: the columns share the grid's
        # width, so cards grow to fill it instead of leaving a dead strip on
        # the right of a wide window.
        self.setMinimumWidth(CARD_WIDTH)
        self.setObjectName("card")
        self.setCursor(Qt.PointingHandCursor)

        edge = DEEP if boss.get("everdark") else BORDER
        self.setStyleSheet(
            f"#card {{ background: {PANEL}; border: 1px solid {edge};"
            f" border-radius: 7px; }}"
            " #card QLabel { background: transparent; border: none; }"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(9, 9, 9, 9)
        layout.setSpacing(4)

        header = QHBoxLayout()
        header.setSpacing(9)
        badge = QLabel()
        badge.setFixedSize(ICON, ICON)
        base = icons.menu(boss.get("icon")) if icons else None
        twin = boss.get("everdark")
        other = icons.menu(twin.get("icon")) if (icons and twin) else None
        if base is not None and other is not None:
            badge.setPixmap(_split_circle(base, other, ICON))
        elif base is not None:
            badge.setPixmap(base.scaled(ICON, ICON, Qt.KeepAspectRatio,
                                        Qt.SmoothTransformation))
        header.addWidget(badge)

        titles = QVBoxLayout()
        titles.setSpacing(1)
        name = QLabel(boss["name"])
        name.setWordWrap(True)
        name.setStyleSheet("color: #e8e8e8; font-size: 13px; font-weight: bold;")
        titles.addWidget(name)

        expedition = QLabel(boss["expedition"])
        expedition.setWordWrap(True)
        expedition.setStyleSheet(f"color: {ACCENT}; font-size: 11px;")
        titles.addWidget(expedition)

        twin_group = (boss.get("everdark") or {}).get("group")
        tag = QLabel(f"+ {twin_group}" if twin_group
                     else "no Everdark version")
        tag.setStyleSheet(
            f"color: {DEEP if twin_group else MUTED}; font-size: 10px;")
        titles.addWidget(tag)
        titles.addStretch(1)
        header.addLayout(titles, 1)
        layout.addLayout(header)

        description = QLabel(boss["description"] or "no description in the files")
        description.setWordWrap(True)
        description.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        layout.addWidget(description, 1)

    def mousePressEvent(self, event) -> None:  # noqa: N802 - Qt naming
        self.clicked.emit(self.boss)
        super().mousePressEvent(event)


class BossTab(QWidget):
    def __init__(self, data: dict, icons=None):
        super().__init__()
        self.bosses = merge_everdark(data.get("bosses", []))
        self.icons = icons

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # No filter box. Ten entries all fit on screen at once, so a search
        # field only took up room and gave the list a state it did not need.
        self.summary = QLabel()
        self.summary.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        layout.addWidget(self.summary)

        body = QHBoxLayout()
        body.setSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        self.holder = QWidget()
        self.grid_outer = QVBoxLayout(self.holder)
        self.grid_outer.setContentsMargins(0, 0, 0, 0)
        self.grid_outer.setSpacing(10)
        scroll.setWidget(self.holder)
        body.addWidget(scroll, 1)

        body.addWidget(self._build_detail(), 0)
        layout.addLayout(body, 1)

        self.refresh()

    def _build_detail(self) -> QWidget:
        """Everything the files hold about one boss, not just its blurb.

        Scrollable, because the field list is longer than the artwork panel it
        replaced and grows whenever another link is cracked.
        """
        outer = QScrollArea()
        outer.setFixedWidth(330)
        outer.setWidgetResizable(True)
        outer.setFrameShape(QFrame.NoFrame)

        panel = QFrame()
        panel.setObjectName("detail")
        panel.setStyleSheet(
            f"#detail {{ background: {PANEL}; border: 1px solid {BORDER};"
            f" border-radius: 7px; }}"
            " #detail QLabel { background: transparent; border: none; }"
        )
        outer.setWidget(panel)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        self.detail_art = QLabel()
        self.detail_art.setAlignment(Qt.AlignCenter)
        self.detail_art.setMinimumHeight(180)
        layout.addWidget(self.detail_art)

        self.detail_name = QLabel()
        self.detail_name.setWordWrap(True)
        self.detail_name.setStyleSheet(
            "color: #e8e8e8; font-size: 15px; font-weight: bold;")
        layout.addWidget(self.detail_name)

        self.detail_expedition = QLabel()
        self.detail_expedition.setWordWrap(True)
        self.detail_expedition.setStyleSheet(f"color: {ACCENT}; font-size: 12px;")
        layout.addWidget(self.detail_expedition)

        self.detail_text = QLabel()
        self.detail_text.setWordWrap(True)
        self.detail_text.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        layout.addWidget(self.detail_text)

        self.detail_body = QLabel()
        self.detail_body.setWordWrap(True)
        self.detail_body.setTextFormat(Qt.RichText)
        self.detail_body.setAlignment(Qt.AlignTop)
        layout.addWidget(self.detail_body)
        layout.addStretch(1)

        self.show_detail(None)
        return outer

    @staticmethod
    def _section(title: str) -> str:
        return (f"<div style='color:{ACCENT}; font-size:10px; font-weight:bold;"
                f" letter-spacing:1px; margin-top:10px'>{title}</div>")

    # Chart label -> the game's own damage-type icon, extracted from the
    # relic screen's filter list. The three grey physical icons were pinned
    # by looking at them enlarged -- club on rubble is Strike, the broad
    # blade Slash, the gauntlet thrust Pierce -- not assumed from their ids.
    TYPE_ICONS = {
        "Standard": "MENU_FL_40141.png",
        "Strike": "MENU_FL_40142.png",
        "Slash": "MENU_FL_40143.png",
        "Pierce": "MENU_FL_40144.png",
        "Holy": "MENU_FL_40145.png",
        "Magic": "MENU_FL_40146.png",
        "Frostbite": "MENU_FL_40147.png",
        "Fire": "MENU_FL_40148.png",
        "Lightning": "MENU_FL_40150.png",
        "Madness": "MENU_FL_40151.png",
        "Poison": "MENU_FL_40172.png",
        "Blood loss": "MENU_FL_40173.png",
    }

    def _type_icon_cell(self, label: str) -> str:
        """A table cell with the type's game icon, or an empty spacer.

        Scarlet Rot, Sleep and Death have no icon in the set the game ships
        for its own filter list, so those rows keep a spacer rather than
        borrowing a lookalike.
        """
        sprite = self.TYPE_ICONS.get(label)
        path = self.icons.ui_path(sprite) if (self.icons and sprite) else None
        if path is None:
            return "<td style='padding-right:4px'></td>"
        src = pathlib.Path(path).as_uri()
        return (f"<td style='padding-right:4px'>"
                f"<img src='{src}' width='16' height='16'></td>")

    def _bars(self, damage: dict, weak: list) -> str:
        """Damage multipliers as a bar chart, 1.00 being neutral."""
        # Block characters rather than styled divs: Qt's rich text ignores
        # percentage widths, so a CSS bar renders as nothing at all.
        rows = []
        widest = max(list(damage.values()) + [1.0])
        for label, value in damage.items():
            filled = max(1, round(14 * value / widest)) if widest else 1
            if label in weak:
                colour = GOOD
            elif value < 1.0:
                colour = "#5a5a5a"
            else:
                colour = "#98a0ad"
            bar = "&#9608;" * filled
            rows.append(
                "<tr>"
                + self._type_icon_cell(label) +
                f"<td style='color:{MUTED}; font-size:11px;"
                f" padding-right:8px; white-space:nowrap'>{label}</td>"
                f"<td style='color:{colour}; font-size:11px;"
                f" white-space:nowrap'>{bar}</td>"
                f"<td style='color:{colour}; font-size:11px;"
                f" padding-left:8px; white-space:nowrap'>x{value:g}</td>"
                "</tr>"
            )
        return f"<table>{''.join(rows)}</table>"

    def _status(self, status: dict, weak: list) -> str:
        rows = []
        for label, value in sorted(status.items(), key=lambda kv: kv[1]):
            if value >= 999:
                shown, colour = "immune", "#5a5a5a"
            elif label in weak:
                shown, colour = str(value), GOOD
            else:
                shown, colour = str(value), "#d8d8d8"
            rows.append(
                "<tr>"
                + self._type_icon_cell(label) +
                f"<td style='color:{MUTED}; font-size:11px;"
                f" padding-right:8px; white-space:nowrap'>{label}</td>"
                f"<td style='color:{colour}; font-size:11px;"
                f" white-space:nowrap'>{shown}</td>"
                "</tr>"
            )
        return f"<table>{''.join(rows)}</table>"

    @staticmethod
    def _row(label: str, value) -> str:
        return (f"<div style='margin-top:2px'>"
                f"<span style='color:{MUTED}; font-size:11px'>{label}</span>"
                f"<span style='color:#d8d8d8; font-size:11px'> &nbsp;{value}</span>"
                f"</div>")

    def _stance_rank(self, profile: dict) -> str:
        """Where this boss sits among the ten on how hard it is to stagger.

        A bar size alone means little without the field to compare it to,
        and "how are they different" is the question the tab is really for.
        """
        bars = []
        for other in self.bosses:
            stance = ((other.get("weakness") or {}).get("profile")
                      or {}).get("stance") or {}
            if "bar" in stance:
                bars.append((stance["bar"], other["name"]))
        mine = (profile.get("stance") or {}).get("bar")
        if mine is None or len(bars) < 2:
            return "-"
        bars.sort()
        place = sum(1 for value, _ in bars if value < mine) + 1
        return (f"{place} of {len(bars)} for bar size  "
                f"(smallest {bars[0][1]} {bars[0][0]:g}, "
                f"largest {bars[-1][1]} {bars[-1][0]:g})")

    def show_detail(self, boss: dict | None) -> None:
        if boss is None:
            self.detail_art.clear()
            self.detail_name.setText("Select a Nightlord")
            self.detail_expedition.clear()
            self.detail_text.clear()
            self.detail_body.clear()
            return

        twin = boss.get("everdark")
        base = self.icons.menu(boss.get("large_icon")) if self.icons else None
        other = (self.icons.menu(twin.get("large_icon"))
                 if (self.icons and twin) else None)
        if base is not None and other is not None:
            self.detail_art.setPixmap(_split_circle(base, other, 256))
        elif base is not None:
            self.detail_art.setPixmap(
                base.scaled(256, 256, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            self.detail_art.clear()
        self.detail_name.setText(boss["name"])
        # The expedition name is dropped: it says nothing a player planning a
        # fight can act on. What replaces it is whether there is a Sovereign
        # version, which is what the split portrait above is showing.
        self.detail_expedition.setText(
            f"Nightlord  ·  {twin.get('group') or 'Everdark Sovereign'}"
            if twin else "Nightlord  ·  no Everdark version"
        )
        self.detail_text.setText(boss["description"])

        parts: list[str] = []
        # The description sits in its own label directly above; without this
        # the first heading crowds straight into it.
        parts.append("<div style='height:14px'></div>")

        # Everything here is written for someone about to fight this boss.
        # How a figure was derived, what could not be extracted and which
        # evidence class a claim belongs to are all real questions -- they
        # live in OPEN_QUESTIONS.md, not on screen. If a line does not change
        # how the fight is played, it does not belong in this panel.

        weakness = boss.get("weakness")
        profile = (weakness or {}).get("profile")
        if not profile:
            parts.append(self._section("WEAKNESSES"))
            parts.append(
                f"<div style='color:{BAD}; font-size:11px'>"
                "Not derivable for this fight.</div>")
            self.detail_body.setText("".join(parts))
            return

        weak = profile.get("weak_damage") or []
        if weak:
            parts.append(self._section("WEAKNESS SPECIAL INTERACTION"))
            parts.append(
                f"<div style='color:#d8d8d8; font-size:11px'>"
                f"Pile on <b style='color:{ACCENT}'>{' / '.join(weak)}</b> "
                "damage. It builds a hidden meter, and filling it breaks the "
                "boss's stance and opens it up for a critical.</div>"
            )
            if boss["name"] in WEAKNESS_NOTE:
                parts.append(
                    f"<div style='color:{OBSERVED_COLOUR}; font-size:11px; "
                    f"margin-top:3px'>{WEAKNESS_NOTE[boss['name']]}</div>")
            if boss["name"] in DEBUFF_ON_BREAK:
                for label, value in (("Debuff", "x2.0 damage taken"),
                                     ("Debuff", "x0.8 attack power")):
                    parts.append(
                        f"<div style='margin-top:2px'>"
                        f"<span style='color:{GOOD}; font-size:11px'>{label}"
                        f"</span><span style='color:#d8d8d8; font-size:11px'>"
                        f" &nbsp;{value}</span></div>")
                parts.append(self._row(
                    "Tell", "golden shine, damage-down and defence-down "
                            "icons on its health bar"))
                parts.append(self._row("Lasts", "temporary"))

        parts.append(self._section("DAMAGE TAKEN"))
        parts.append(self._bars(profile["damage"], profile["weak_damage"]))
        parts.append(self._section("STATUS BUILDUP"))
        parts.append(self._status(profile["status"], profile["weak_status"]))

        stance = profile.get("stance") or {}
        if stance:
            parts.append(self._section("STANCE"))
            if "bar" in stance:
                parts.append(self._row("Bar to break", f"{stance['bar']:g}"))
            if "recovery" in stance:
                parts.append(self._row(
                    "Refills at", f"x{stance['recovery']:g}"))
            parts.append(self._row("Ranking", self._stance_rank(profile)))

        ladder = profile.get("ladder") or {}
        defence = profile.get("defence_buffs") or []
        if ladder.get("up") or defence:
            parts.append(self._section("IT BUFFS ITSELF"))
            for entry in ladder["up"]:
                bits = [f"x{entry['attack']:g} attack"]
                stance_taken = entry.get("stance_taken")
                if stance_taken and abs(stance_taken - 1.0) > 1e-6:
                    bits.append("harder to stagger" if stance_taken < 1
                                else "easier to stagger")
                if not entry.get("from"):
                    bits.append("always on")
                parts.append(
                    f"<div style='margin-top:2px'>"
                    f"<span style='color:{BAD}; font-size:11px'>Buff</span>"
                    f"<span style='color:#d8d8d8; font-size:11px'>"
                    f" &nbsp;{'  ·  '.join(bits)}</span></div>")
            parts.append(self._row("Stacks", "yes — repeats compound"))
            if boss["name"] in BUFF_TRIGGER:
                parts.append(self._row("Set off by", BUFF_TRIGGER[boss["name"]]))
        for entry in defence:
            cut = round((1 - entry["taken"]) * 100)
            bits = [f"takes {cut}% less damage", f"{entry['seconds']:g}s"]
            trigger = DEFENCE_TRIGGER.get((boss["name"], entry["id"]))
            if trigger:
                bits.append(trigger)
            parts.append(
                f"<div style='margin-top:2px'>"
                f"<span style='color:{DEEP}; font-size:11px'>Defence</span>"
                f"<span style='color:#d8d8d8; font-size:11px'>"
                f" &nbsp;{'  ·  '.join(bits)}</span></div>")

        rates = profile.get("part_rates") or {}
        if rates:
            parts.append(self._section("BODY PARTS"))
            for label, value in rates.items():
                parts.append(self._row(
                    PART_NAMES.get((boss["name"], label), label),
                    f"x{value:g} damage"
                    + ("  — armoured" if value < 1 else "  — soft spot")))
            if profile.get("skips_weak_animation"):
                parts.append(self._row("Hit reaction", "none, ever"))

        if twin:
            parts.append(self._section("EVERDARK"))
            parts.append(
                f"<div style='color:{MUTED}; font-size:11px'>"
                "Same stats as above — resistances, stance and buff are "
                "identical. What differs is behaviour, not numbers.</div>"
            )

        self.detail_body.setText("".join(parts))

    def refresh(self) -> None:
        while self.grid_outer.count():
            item = self.grid_outer.takeAt(0)
            widget = item.widget()
            if widget:
                # Unparent before scheduling deletion. deleteLater alone leaves
                # the old cards attached until the event loop next runs, so a
                # rebuild would briefly stack two generations of the grid.
                widget.setParent(None)
                widget.deleteLater()

        grid_host = QWidget()
        grid = QGridLayout(grid_host)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(8)
        for i, boss in enumerate(self.bosses):
            card = BossCard(boss, self.icons)
            card.clicked.connect(self.show_detail)
            grid.addWidget(card, i // COLUMNS, i % COLUMNS)
        for column in range(COLUMNS):
            grid.setColumnStretch(column, 1)
        self.grid_outer.addWidget(grid_host)
        self.grid_outer.addStretch(1)

        paired = sum(1 for b in self.bosses if b.get("everdark"))
        self.summary.setText(
            f"{len(self.bosses)} Nightlords  ·  {paired} also have an "
            f"Everdark Sovereign, shown as the upper-right half of each circle"
        )
