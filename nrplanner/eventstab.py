"""World events, written for the player who meets one mid-run.

Each event is one card: which Nightlords it can appear under and how often,
what happens, what you win, what you lose. The figures come out of the game's
own data and the prose comes from the community; community material is tinted
blue so the two never blur. Everything about *how* any of it was derived
stays in the project's documents -- none of it belongs on screen.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QScrollArea,
    QVBoxLayout, QWidget,
)

from . import tabheader
from .eventlore import LORE, UNANNOUNCED

ACCENT = "#c8a45c"
MUTED = "#8a8a8a"
PANEL = "#1e1f23"
BORDER = "#2e2f35"
DLC = "#9a6fc4"
UNKNOWN = "#7d6f52"
PENALTY = "#c07a6a"
# Community material is tinted throughout, so it never sits on the page
# looking like the extracted text beside it.
COMMUNITY = "#6f9ac4"

#: Figures whose reference quantity is not in the files, keyed by the exact
#: prefix `nrdata.extract._buff_lines` writes them with (AK-70, A7). Naming
#: the prefix rather than the whole line keeps the entry valid when the
#: magnitude changes, which is the only part of the line that can.
UNKNOWN_REFERENCE = {
    "stamina recovery speed ": (
        "The stamina recovery figure is the game's own number for that "
        "field. The files do not say what it is counted in, so read it as "
        "\"recovers faster\" and not as an amount per second."),
}


def _note(text: str) -> QLabel:
    label = QLabel(text)
    label.setWordWrap(True)
    label.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
    return label


def _colour(hex_value: str) -> QColor:
    return QColor(hex_value)


def _community(text: str) -> QLabel:
    label = QLabel(text)
    label.setWordWrap(True)
    label.setStyleSheet(f"color: {COMMUNITY}; font-size: 12px;")
    return label


def _stat(text: str) -> QLabel:
    """A figure read from the game's data -- same weight as the game's own
    wording, so it is not tinted."""
    label = QLabel("▸  " + text)
    label.setWordWrap(True)
    label.setStyleSheet("color: #e8dcc0; font-size: 12px;")
    return label


def _grants_an_amount(line: str) -> bool:
    """Does this line hand over an amount once, rather than name a state?

    A duration belongs to a state -- you are invulnerable *for five seconds*.
    An amount is handed over and then it is yours, so `10,000 runes for 1s`
    and `restores 100 stamina for 0.3s` say something that is not true of
    either (QA-133, AK-103).

    `nrdata.extract._buff_lines` builds exactly two amount-granting shapes,
    from `soul` and from `changeStaminaPoint`, and both are recognised here by
    the shape that function gives them. The default is the other way -- an
    unrecognised line keeps its duration -- because every other field that
    function words is a state, and losing a real duration would cost a player
    more than this rule gains.
    """
    return line.endswith(" runes") or line.startswith("restores ")


class WorldEventsTab(QWidget):
    def __init__(self, data: dict):
        super().__init__()
        section = data.get("world_events") or {}
        self.events = section.get("events", [])
        self.unknowns = section.get("unknowns", [])
        self.buffs = {b["id"]: b for b in section.get("buffs", [])}
        self.creatures = section.get("creatures", {})
        self.states = {s["sp_id"]: s for s in section.get("states", [])}
        self.rune_scaling = section.get("rune_scaling", [])
        self.gating = section.get("gating", {})
        self.drops = section.get("drops", {})

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        layout.addWidget(tabheader.heading("WORLD EVENTS"))
        layout.addWidget(_note(
            "Events that can interrupt an expedition: where each one can "
            "appear, what happens, what you win and what you lose. Blue "
            "lines are community-reported; everything else is the game's "
            "own data."
        ))

        body = QHBoxLayout()
        body.setSpacing(10)

        self.list = QListWidget()
        self.list.setMaximumWidth(280)
        self.list.setWordWrap(True)
        self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list.setStyleSheet(
            f"QListWidget {{ background: {PANEL}; border: 1px solid {BORDER};"
            " border-radius: 4px; padding: 4px; }}"
            "QListWidget::item { padding: 6px 8px; }"
            "QListWidget::item:selected { background: rgba(200, 164, 92, 60);"
            " color: #f0f0f0; }"
        )
        # Extracted events first, then the things players call world events
        # that the game never announces. Listing those under their own label
        # is honest; dropping them is not.
        self.rows: list[tuple[str, dict]] = [("event", e) for e in self.events]
        self.rows += [("unannounced", u) for u in UNANNOUNCED]

        for kind, entry in self.rows:
            if kind == "event":
                lore = LORE.get(entry["log_id"], {})
                label = lore.get("name") or entry["announce"]
                if entry.get("is_dlc"):
                    label = f"{label}  · Deep of Night"
            else:
                label = entry["name"]
            item = QListWidgetItem(label)
            if kind == "unannounced":
                item.setForeground(_colour(COMMUNITY))
            self.list.addItem(item)
        self.list.currentRowChanged.connect(self._show)
        body.addWidget(self.list)

        self.detail_area = QScrollArea()
        self.detail_area.setWidgetResizable(True)
        self.detail_area.setFrameShape(QFrame.NoFrame)
        body.addWidget(self.detail_area, 1)

        layout.addLayout(body, 1)

        if not self.events:
            layout.addWidget(_note(
                "No world events in this snapshot. Start the app with the "
                "game installed and it will rebuild itself."
            ))
        else:
            self.list.setCurrentRow(0)

    # ------------------------------------------------------------------

    def _show(self, row: int) -> None:
        if not (0 <= row < len(self.rows)):
            return
        kind, entry = self.rows[row]

        page = QWidget()
        column = QVBoxLayout(page)
        column.setContentsMargins(4, 0, 4, 4)
        column.setSpacing(10)

        if kind == "unannounced":
            self._render_unannounced(entry, column)
        else:
            self._render_event(entry, column)

        column.addStretch(1)
        self.detail_area.setWidget(page)

    def _render_event(self, event: dict, column: QVBoxLayout) -> None:
        lore = LORE.get(event["log_id"], {})

        title = QLabel(lore.get("name") or event["announce"])
        title.setWordWrap(True)
        title.setStyleSheet(
            f"color: {DLC if event.get('is_dlc') else ACCENT};"
            " font-size: 15px; font-weight: bold;"
        )
        column.addWidget(title)

        subtitle = f"Announced as “{event['announce']}”"
        if event.get("is_dlc"):
            subtitle += "  ·  Deep of Night only"
        column.addWidget(_note(subtitle))

        # -- where, and how often ---------------------------------------
        gate = self.gating.get(str(event["log_id"]))
        if gate:
            bosses = "   ·   ".join(
                f"{b['name']} {b['share']:g}%" for b in gate["bosses"])
            column.addWidget(_stat(bosses))
            day1 = gate.get("day1_patterns", 0)
            day2 = gate.get("day2_patterns", 0)
            # The split is in the data and used to be thrown away, so all
            # eleven events carried the same sentence while Judgment is 19
            # Day-1 patterns against 1 and this one is 9 against 21 (QA-134).
            if day1 and day2:
                when = (f"Can fire on Day 1 or Day 2 — {day1} of the "
                        f"{day1 + day2} map patterns that carry it are Day 1")
            elif day1:
                when = "Fires on Day 1"
            else:
                when = "Fires on Day 2"
            column.addWidget(_note(
                f"{when}. Every other Nightlord: never — across every map "
                "pattern in the game's data. The percentage is how much of "
                "that Nightlord's map pool carries the event. The pool is "
                "drawn with weights, so it is not the chance of seeing it on "
                "a given run."))

        # -- what happens ------------------------------------------------
        if lore.get("what"):
            column.addWidget(tabheader.heading("WHAT HAPPENS"))
            column.addWidget(_community(lore["what"]))

        # -- win ----------------------------------------------------------
        buff = self.buffs.get(lore.get("buff_id"))
        creature = self.creatures.get(str(lore.get("creature_chr")))
        drops = self.drops.get(str(lore.get("creature_chr")))
        if buff or creature or drops or lore.get("reward"):
            column.addWidget(tabheader.heading("WIN"))
        if buff:
            column.addWidget(_stat(f"{buff['name']} — {buff['info']}"))
            figures = list(buff["lines"])
            cap = buff.get("stacks_to")
            per_trigger_suffix = (
                f" each time it triggers, up to +{cap} stacks" if cap
                else " each time it triggers")
            figures += [line + per_trigger_suffix
                        for line in buff["per_trigger"]]
            for part in buff["parts"]:
                # Split before the duration is attached, so a part carrying
                # both an amount and a state gives the window to the state
                # alone rather than to whichever came first (AK-103).
                amounts = [line for line in part["lines"]
                           if _grants_an_amount(line)]
                states = [line for line in part["lines"]
                          if not _grants_an_amount(line)]
                if amounts:
                    figures.append(", ".join(amounts))
                if states:
                    window = (f" for {part['duration']:g}s"
                              if part["duration"] and part["duration"] > 0
                              else "")
                    figures.append(", ".join(states) + window)
            if figures:
                column.addWidget(_stat("   ·   ".join(figures)))
            for prefix, sentence in UNKNOWN_REFERENCE.items():
                if any(line.startswith(prefix) for line in figures):
                    column.addWidget(_note(sentence))
            forever = buff["duration"] == -1
            column.addWidget(_note(
                "Lasts the rest of the expedition — not consumed, no cooldown."
                if forever else f"Lasts {buff['duration']:g}s."))
        elif lore.get("reward"):
            column.addWidget(_community("Reward: " + lore["reward"]))
        if creature:
            runes = creature["runes"]
            low, high = min(runes), max(runes)
            label = (f"{low:,}–{high:,}" if low != high else f"{low:,}")
            column.addWidget(_stat(
                f"Runes: {label} base — rises the more expeditions "
                "you have cleared"))
            # "Rises" was the tab's one unnumbered claim, while the figures
            # that number it were loaded on the line above and thrown away
            # (AK-104). They go here, at the claim, and nowhere else.
            if self.rune_scaling:
                column.addWidget(_note(" ".join(self.rune_scaling)))
        if drops:
            column.addWidget(_stat("Drops: " + self._drop_summary(drops)))

        # -- lose ---------------------------------------------------------
        state = self.states.get(lore.get("penalty_sp"))
        if state or lore.get("penalty"):
            column.addWidget(tabheader.heading("LOSE"))
        if state:
            forever = state["duration"] == -1
            line = QLabel(
                f"▸  {state['name']} — {', '.join(state['lines'])}"
                + (", for the rest of the expedition" if forever
                   else f", for {state['duration']:g}s"))
            line.setWordWrap(True)
            line.setStyleSheet(f"color: {PENALTY}; font-size: 12px;")
            column.addWidget(line)
        elif lore.get("penalty"):
            column.addWidget(_community("Penalty: " + lore["penalty"]))

        # -- the demon's forms -------------------------------------------
        if event.get("variants"):
            column.addWidget(tabheader.heading("WHAT THE DEMON CAN DO"))
            for variant in event["variants"]:
                line = QLabel("•  " + variant["text"])
                line.setWordWrap(True)
                line.setStyleSheet("color: #d8d8d8; font-size: 12px;")
                column.addWidget(line)

        # -- caveats worth a player's attention ---------------------------
        for key, prefix in (("note", "Note"),
                            ("uncertain", "Least certain"),
                            ("conflict", "Sources disagree")):
            if lore.get(key):
                label = QLabel(f"<b>{prefix}:</b> {lore[key]}")
                label.setWordWrap(True)
                label.setStyleSheet(f"color: {UNKNOWN}; font-size: 11px;")
                column.addWidget(label)

    def _drop_summary(self, drops: list[dict]) -> str:
        """One line for what the fight itself can pay out."""
        kinds = {"power": 0, "talisman": 0, "weapon": 0, "item": 0}
        for drop in drops:
            kinds[drop["kind"]] = kinds.get(drop["kind"], 0) + 1
        parts = []
        if kinds["power"]:
            parts.append(f"{kinds['power']} different Dormant Powers")
        if kinds["talisman"]:
            parts.append(f"{kinds['talisman']} talismans")
        if kinds["weapon"]:
            parts.append("weapons")
        if kinds["item"]:
            parts.append("items")
        return ", ".join(parts) if parts else "varies"

    def _render_unannounced(self, entry: dict, column: QVBoxLayout) -> None:
        title = QLabel(entry["name"])
        title.setWordWrap(True)
        title.setStyleSheet(
            f"color: {COMMUNITY}; font-size: 15px; font-weight: bold;")
        column.addWidget(title)
        column.addWidget(_note(
            "Everything on this one is community-reported."
        ))
        if entry.get("what"):
            column.addWidget(tabheader.heading("WHAT HAPPENS"))
            column.addWidget(_community(entry["what"]))
        if entry.get("reward"):
            column.addWidget(tabheader.heading("WIN"))
            column.addWidget(_community(entry["reward"]))
        if entry.get("penalty") and entry["penalty"] not in ("None.",):
            column.addWidget(tabheader.heading("LOSE"))
            column.addWidget(_community(entry["penalty"]))
        bosses = entry.get("nightlords")
        if bosses:
            text = "Every Nightlord." if bosses == ["Any"] else ", ".join(bosses)
            column.addWidget(_community(f"Nightlords: {text}"))
        if entry.get("note"):
            label = QLabel(f"<b>Note:</b> {entry['note']}")
            label.setWordWrap(True)
            label.setStyleSheet(f"color: {UNKNOWN}; font-size: 11px;")
            column.addWidget(label)
