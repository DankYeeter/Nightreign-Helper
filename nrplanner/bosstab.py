"""The Nightlords: expedition, artwork and the game's own description.

No resistance figures here, and that is a data limit rather than an omission.
They live in NpcParam and nothing links the boss menu to an NPC row -- see the
note in nrdata/extract.py._bosses.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QScrollArea,
    QVBoxLayout, QWidget,
)

ACCENT = "#c8a45c"
MUTED = "#8a8a8a"
PANEL = "#1e1f23"
BORDER = "#2e2f35"
DEEP = "#9a6fc4"
BAD = "#d1655f"
GOOD = "#6fbf73"

COLUMNS = 4
ICON = 64
CARD_WIDTH = 250


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

        edge = DEEP if boss["is_everdark"] else BORDER
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
        pixmap = icons.menu(boss.get("icon")) if icons else None
        if pixmap:
            badge.setPixmap(pixmap.scaled(ICON, ICON, Qt.KeepAspectRatio,
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

        if boss["is_everdark"]:
            tag = QLabel(boss.get("group") or "Everdark Sovereign")
            tag.setStyleSheet(f"color: {DEEP}; font-size: 10px;")
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
        self.bosses = data.get("bosses", [])
        self.icons = icons

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        controls = QHBoxLayout()
        controls.setSpacing(8)
        self.search = QLineEdit()
        self.search.setPlaceholderText(
            "Filter by boss, expedition or description")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.refresh)
        controls.addWidget(self.search, 1)
        layout.addLayout(controls)

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

    @staticmethod
    def _bars(damage: dict, weak: list) -> str:
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
                f"<td style='color:{MUTED}; font-size:11px;"
                f" padding-right:8px; white-space:nowrap'>{label}</td>"
                f"<td style='color:{colour}; font-size:11px;"
                f" white-space:nowrap'>{bar}</td>"
                f"<td style='color:{colour}; font-size:11px;"
                f" padding-left:8px; white-space:nowrap'>x{value:g}</td>"
                "</tr>"
            )
        return f"<table>{''.join(rows)}</table>"

    @staticmethod
    def _status(status: dict, weak: list) -> str:
        rows = []
        for label, value in sorted(status.items(), key=lambda kv: kv[1]):
            if value >= 999:
                shown, colour = "immune", "#5a5a5a"
            elif label in weak:
                shown, colour = str(value), GOOD
            else:
                shown, colour = str(value), "#d8d8d8"
            rows.append(
                f"<div style='margin-top:2px'>"
                f"<span style='color:{MUTED}; font-size:11px'>{label}</span>"
                f"<span style='color:{colour}; font-size:11px'>"
                f" &nbsp;{shown}</span></div>"
            )
        return "".join(rows)

    @staticmethod
    def _row(label: str, value) -> str:
        return (f"<div style='margin-top:2px'>"
                f"<span style='color:{MUTED}; font-size:11px'>{label}</span>"
                f"<span style='color:#d8d8d8; font-size:11px'> &nbsp;{value}</span>"
                f"</div>")

    def show_detail(self, boss: dict | None) -> None:
        if boss is None:
            self.detail_art.clear()
            self.detail_name.setText("Select a Nightlord")
            self.detail_expedition.clear()
            self.detail_text.clear()
            self.detail_body.clear()
            return

        pixmap = self.icons.menu(boss.get("large_icon")) if self.icons else None
        if pixmap:
            self.detail_art.setPixmap(
                pixmap.scaled(256, 256, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            self.detail_art.clear()
        self.detail_name.setText(boss["name"])
        self.detail_expedition.setText(
            boss["expedition"]
            + (f"   ·   {boss.get('group') or 'Everdark Sovereign'}"
               if boss["is_everdark"] else "")
        )
        self.detail_text.setText(boss["description"])

        parts: list[str] = []

        # Weaknesses first, because that is what the tab is asked for most --
        # and saying exactly why they are missing beats a silent gap.
        weakness = boss.get("weakness")
        profile = (weakness or {}).get("profile")
        if profile:
            parts.append(self._section("DAMAGE TAKEN"))
            parts.append(self._bars(profile["damage"], profile["weak_damage"]))
            parts.append(self._section("STATUS BUILDUP"))
            parts.append(self._status(profile["status"], profile["weak_status"]))
            if profile.get("weak_part_rate") or profile.get("part_rates"):
                parts.append(self._section("BODY PARTS"))
                if profile.get("weak_part_rate"):
                    parts.append(self._row(
                        "Designated weak point",
                        f"x{profile['weak_part_rate']:g} damage"))
                for label, value in profile.get("part_rates", {}).items():
                    parts.append(self._row(
                        label, f"x{value:g}"
                        + ("  (armoured)" if value < 1 else "  (soft)")))

            # Exactly how this boss was identified, because two of them rest
            # on a weaker argument than the rest and that must be visible.
            if weakness.get("confidence") == "shared":
                trace = (
                    f"<b>Base figures, shared with {weakness.get('shared_from')}"
                    f".</b> No separate Everdark character or NpcParam row "
                    f"exists: every boss has exactly one resistance profile "
                    f"across all its rows. Everdark differences players report "
                    f"-- Adel's poison stagger not firing, for one -- are "
                    f"behavioural, and behaviour is not in these fields."
                )
            elif weakness.get("confidence") == "inferred":
                if weakness.get("group_boss"):
                    how = (
                        f"this is a group fight, so no single body is "
                        f"boss-scale; the arena places this character "
                        f"{weakness.get('placements')} times where every "
                        f"other map in the game places it once. The figures "
                        f"are per member, not for the group."
                    )
                else:
                    how = ("the character is the only tuned, boss-scale one "
                           "in that arena")
                trace = (
                    f"<b style='color:{BAD}'>Inferred, not proven.</b> The "
                    f"event script names this boss's defeat flag in "
                    f"{weakness['map']} but never pairs it with an entity, so "
                    f"{how}"
                )
            else:
                trace = (
                    f"Traced from this boss's defeat flag through the event "
                    f"script to entity {weakness['entity']} in "
                    f"{weakness['map']}."
                )
            parts.append(
                f"<div style='color:{MUTED}; font-size:10px; margin-top:6px'>"
                f"c{weakness['primary']}, NpcParam row {profile['npc_row']}, "
                f"base HP {profile['hp']}. {trace} Multipliers are what the "
                f"enemy takes: above 1.00 is a weakness. Status is buildup "
                f"resistance, so lower is easier to apply and 999 is immune."
                f"</div>"
            )
        else:
            parts.append(self._section("WEAKNESSES"))
            parts.append(
                f"<div style='color:{BAD}; font-size:11px; margin-top:2px'>"
                "Not derivable for this fight.</div>"
                f"<div style='color:{MUTED}; font-size:10px; margin-top:3px'>"
                "The chain that resolves the other bosses -- defeat flag to "
                "event script to arena entity -- stops here: this fight's "
                "event does not carry the flag/entity pair. The base boss's "
                "figures are deliberately not reused, since this is a "
                "different encounter.</div>"
            )

        parts.append(self._section("EXPEDITION"))
        parts.append(self._row("Group", boss.get("group") or "-"))
        parts.append(self._row("Menu order", boss.get("sort")))
        scenario = boss.get("scenario_id")
        if isinstance(scenario, int) and scenario >= 0:
            parts.append(self._row("Scenario id", scenario))
        if boss.get("music_cue"):
            parts.append(self._row("Music cue", boss["music_cue"]))

        parts.append(self._section("EVENT FLAGS"))
        parts.append(self._row("Unlock", boss.get("unlock_event_flag")))
        parts.append(self._row("Defeat", boss.get("defeat_event_flag")))

        parts.append(self._section("ARTWORK IDS"))
        parts.append(self._row("Icon", boss.get("icon")))
        parts.append(self._row("Large", boss.get("large_icon")))
        parts.append(self._row("Defeated", boss.get("defeated_icon")))
        parts.append(self._row("Background", boss.get("background")))

        unnamed = boss.get("unnamed") or {}
        if any(v is not None for v in unnamed.values()):
            parts.append(self._section("NOT IDENTIFIED"))
            parts.append(
                f"<div style='color:{MUTED}; font-size:10px'>Four fields the "
                "paramdef does not name. They differ per boss, so they mean "
                "something, but nothing in the files says what.</div>"
            )
            for key, value in unnamed.items():
                parts.append(self._row(key.replace("unknown_", "field "), value))

        self.detail_body.setText("".join(parts))

    def _matches(self, boss: dict, needle: str) -> bool:
        if not needle:
            return True
        haystack = " ".join(
            str(boss.get(key, "")) for key in ("name", "expedition", "description")
        ).lower()
        return needle in haystack

    def refresh(self) -> None:
        needle = self.search.text().strip().lower()
        shown = [b for b in self.bosses if self._matches(b, needle)]

        while self.grid_outer.count():
            item = self.grid_outer.takeAt(0)
            widget = item.widget()
            if widget:
                # Unparent before scheduling deletion. deleteLater alone leaves
                # the old cards attached until the event loop next runs, so a
                # rebuild would briefly stack two generations of the grid.
                widget.setParent(None)
                widget.deleteLater()

        # The Everdark heading is the game's own string; the base one is ours,
        # since the files give that group no label of its own.
        everdark_label = next(
            (b.get("group") for b in self.bosses
             if b["is_everdark"] and b.get("group")),
            "Everdark Sovereign",
        )
        groups = [
            ("NIGHTLORDS", [b for b in shown if not b["is_everdark"]]),
            (everdark_label.upper(), [b for b in shown if b["is_everdark"]]),
        ]
        for title, members in groups:
            if not members:
                continue
            section = QWidget()
            box = QVBoxLayout(section)
            box.setContentsMargins(0, 0, 0, 0)
            box.setSpacing(6)
            box.addWidget(_heading(f"{title}  ({len(members)})"))

            grid_host = QWidget()
            grid = QGridLayout(grid_host)
            grid.setContentsMargins(0, 0, 0, 0)
            grid.setSpacing(8)
            for i, boss in enumerate(members):
                card = BossCard(boss, self.icons)
                card.clicked.connect(self.show_detail)
                grid.addWidget(card, i // COLUMNS, i % COLUMNS)
            for column in range(COLUMNS):
                grid.setColumnStretch(column, 1)
            box.addWidget(grid_host)
            self.grid_outer.addWidget(section)

        self.grid_outer.addStretch(1)

        everdark = sum(1 for b in shown if b["is_everdark"])
        self.summary.setText(
            f"{len(shown)} of {len(self.bosses)} expeditions  ·  "
            f"{len(shown) - everdark} Nightlord, {everdark} {everdark_label}"
        )
