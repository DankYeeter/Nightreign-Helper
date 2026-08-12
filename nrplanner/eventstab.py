"""World events: what can interrupt a Limveld expedition, in the game's words.

The roster and every line of text on this tab come from the game's own display
log (`UserDispLogParam`) paired with `CL_MenuText` -- see `nrdata.extract.
_world_events` for why that pairing, and not the event scripts, is the source.

Rewards, penalties, rune values and Nightlord gating are all extracted -- see
`nrdata.extract._event_buffs`, `_event_states`, `_event_creatures` and
`_gating`. What is still missing is the item half of each reward, which is an
item lot, and `ItemLotParam_enemy` ships no paramdef.

Everything that could not be verified against the files is tinted blue and
labelled, so a reader can always tell which half of the page they are looking
at without checking the source.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QScrollArea,
    QVBoxLayout, QWidget,
)

from .eventlore import LORE, UNANNOUNCED

ACCENT = "#c8a45c"
MUTED = "#8a8a8a"
PANEL = "#1e1f23"
BORDER = "#2e2f35"
DLC = "#9a6fc4"
UNKNOWN = "#7d6f52"
# Community material is tinted throughout, so it never sits on the page
# looking like the extracted text beside it.
COMMUNITY = "#6f9ac4"
# A line someone actually watched happen in a run. Stronger than a wiki claim
# and weaker than a param read, so it gets its own colour rather than
# borrowing either.
OBSERVED = "#7fae72"

# An outcome line that mentions one of these reads as the event ending badly.
# It is only used to colour the line, never to claim a penalty: the wording is
# the game's, and the colouring is the app's reading of it.
BAD_WORDS = ("failed", "enmity", "lost", "multiply", "spur", "stronger",
             "threatens", "invaded")


def _heading(text: str) -> QLabel:
    label = QLabel(text)
    label.setStyleSheet(
        f"color: {ACCENT}; font-size: 12px; font-weight: bold;"
        " letter-spacing: 1px;"
    )
    return label


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
    """A number read straight out of the params. Deliberately not tinted like
    the community text -- these carry the same weight as the extracted
    wording, because that is what they are."""
    label = QLabel("▸  " + text)
    label.setWordWrap(True)
    label.setStyleSheet("color: #e8dcc0; font-size: 12px;")
    return label


def _card() -> QFrame:
    frame = QFrame()
    frame.setStyleSheet(
        f"QFrame {{ background: {PANEL}; border: 1px solid {BORDER};"
        " border-radius: 4px; }}"
    )
    return frame


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

        layout.addWidget(_heading("WORLD EVENTS"))
        layout.addWidget(_note(
            "Events that can interrupt an expedition. Rewards, penalties and "
            "rune values are read out of the game's own data. Anything still "
            "tinted blue is community-reported and could not be verified "
            "against the files — see nrplanner/eventlore.py for its sources."
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
        # The list holds the extracted events first, then the handful of
        # things players call world events that the game never announces.
        # Those have no display log row at all, so they cannot be extracted --
        # listing them under a divider is honest, dropping them is not.
        self.rows: list[tuple[str, dict]] = [("event", e) for e in self.events]
        self.rows += [("unannounced", u) for u in UNANNOUNCED]

        for kind, entry in self.rows:
            if kind == "event":
                lore = LORE.get(entry["log_id"], {})
                label = lore.get("name") or entry["announce"]
                if entry.get("is_dlc"):
                    label = f"{label}  · DLC"
            else:
                label = f"{entry['name']}  · no banner"
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
                "No world events in this snapshot. Rebuild it with "
                "scripts/build_snapshot.py against an installed game."
            ))
        else:
            self.list.setCurrentRow(0)

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
            column.addStretch(1)
            self.detail_area.setWidget(page)
            return

        event = entry
        lore = LORE.get(event["log_id"], {})

        title = QLabel(lore.get("name") or event["announce"])
        title.setWordWrap(True)
        title.setStyleSheet(
            f"color: {DLC if event.get('is_dlc') else ACCENT};"
            " font-size: 15px; font-weight: bold;"
        )
        column.addWidget(title)
        column.addWidget(_note(
            f"The game announces it as “{event['announce']}”"
            + ("  ·  expansion content" if event.get("is_dlc") else "")
        ))

        covered = self._render_payout(lore, column)
        if self._render_gating(event["log_id"], column):
            covered.add("nightlords")
        self._render_lore(lore, column, covered)

        if event.get("variants"):
            column.addWidget(_heading("WHAT THE DEMON CAN DO"))
            column.addWidget(_note(
                "The demon does not do the same thing every time. These are "
                "its forms, one contiguous block of the game's text with no "
                "param grouping them -- so the order is the file's order, and "
                "which one a given expedition draws is not recorded anywhere."
            ))
            for variant in event["variants"]:
                line = QLabel("•  " + variant["text"])
                line.setWordWrap(True)
                line.setStyleSheet("color: #d8d8d8; font-size: 12px;")
                column.addWidget(line)

        column.addWidget(_heading("WHY THE BLUE TEXT IS NOT EXTRACTED"))
        for reason in self.unknowns:
            label = QLabel("•  " + reason)
            label.setWordWrap(True)
            label.setStyleSheet(f"color: {UNKNOWN}; font-size: 11px;")
            column.addWidget(label)

        column.addStretch(1)
        self.detail_area.setWidget(page)

    def _render_payout(self, lore: dict, column: QVBoxLayout) -> set[str]:
        """The half of the reward that IS extracted: the buff and the runes.

        Which buff and which creature belongs to which event is a
        community-reported pairing, but everything shown about them -- the
        name, the wording, who it lands on, how long it lasts, the rune value
        -- is read out of the params. The heading says exactly that, so the
        two halves stay distinguishable even here.
        """
        buff = self.buffs.get(lore.get("buff_id"))
        creature = self.creatures.get(str(lore.get("creature_chr")))
        state = self.states.get(lore.get("penalty_sp"))
        covered: set[str] = set()
        if not buff and not creature and not state:
            return covered

        column.addWidget(_heading("REWARD  ·  FROM THE GAME FILES"))
        covered.add("reward")

        if buff:
            title = QLabel(f"<b>{buff['name']}</b> — {buff['info']}")
            title.setWordWrap(True)
            title.setStyleSheet("color: #d8d8d8; font-size: 12px;")
            column.addWidget(title)

            # -1 endurance is the game's way of saying "no timer". Every
            # event buff is -1, which is what answers "is it used up?".
            forever = buff["duration"] == -1
            bits = [
                "lasts the rest of the expedition — not consumed, no cooldown"
                if forever else f"lasts {buff['duration']}s",
            ]
            # Only stated when the game's own caption states it. The params'
            # effectTarget* flags look like they answer this and do not --
            # they are eligibility filters sitting at their modal value.
            if buff.get("shares_with_allies"):
                bits.insert(0, "reaches nearby allies, per the game's caption")
            if buff.get("fires_at") and buff["fires_at"] > 0:
                bits.append(
                    f"builds up and fires at {buff['fires_at']}, then rebuilds")
            column.addWidget(_note("· " + "  ·  ".join(bits)))

            for line in buff["lines"]:
                column.addWidget(_stat(line))
            for line in buff["per_trigger"]:
                column.addWidget(_stat(f"{line} — each time it triggers"))

            # The procs. These carry the magnitudes for every buff whose
            # marker row is only a marker, which is most of them.
            for part in buff["parts"]:
                if not part["lines"]:
                    continue
                duration = part["duration"]
                window = (f" for {duration:g}s" if duration and duration > 0
                          else "")
                label = f"{', '.join(part['lines'])}{window}"
                if part["name"]:
                    label += f"  ({part['name']})"
                column.addWidget(_stat(label))

            if buff.get("fires_at") and buff["fires_at"] > 0:
                column.addWidget(_note(
                    "The counter resets after firing, so this one repeats for "
                    "as long as you keep attacking."))

        if creature:
            runes = creature["runes"]
            label = " / ".join(f"{v:,}" for v in runes)
            names = " · ".join(creature["names"][:3])
            line = QLabel(
                f"<b>Runes:</b> {label} base from {names} "
                f"(character c{creature['chr']})")
            line.setWordWrap(True)
            line.setStyleSheet("color: #d8d8d8; font-size: 12px;")
            column.addWidget(line)
            column.addWidget(_note(
                "This is the base value on the creature itself "
                "(NpcParam.getSoul). It is deliberately lower than what a run "
                "pays, because these multiply it:"))
            for line in self.rune_scaling:
                column.addWidget(_note("   · " + line))

        self._render_drops(lore, column)

        if state:
            column.addWidget(_heading("PENALTY  ·  FROM THE GAME FILES"))
            covered.add("penalty")
            forever = state["duration"] == -1
            line = QLabel(
                f"<b>{state['name']}</b> — {', '.join(state['lines'])}"
                + (", for the rest of the expedition" if forever
                   else f", for {state['duration']:g}s"))
            line.setWordWrap(True)
            line.setStyleSheet("color: #c07a6a; font-size: 12px;")
            column.addWidget(line)
            column.addWidget(_note(
                "The game files do not say whether this hits the whole party "
                "or only the player who went down, so this tool will not "
                "guess at it. Worth watching for on a run."
            ))

        return covered

    def _render_drops(self, lore: dict, column: QVBoxLayout) -> None:
        """The creature's drop table, flattened, with weights as shares.

        Percentages are shares within the table, so they say what the reward
        is *made of* rather than how likely it is to appear at all. A short
        table is shown whole; a long one is topped and counted, because a
        158-entry weapon pool on screen is noise.
        """
        drops = self.drops.get(str(lore.get("creature_chr")))
        if not drops:
            return

        powers = [d for d in drops if d["kind"] == "power"]
        rest = [d for d in drops if d["kind"] != "power"]
        column.addWidget(_heading("DROPS  ·  FROM THE GAME FILES"))

        shown = 0
        for group, label in ((powers, "Dormant Power"), (rest, None)):
            for drop in group[:12]:
                suffix = f"  ({label})" if label else ""
                column.addWidget(_stat(
                    f"{drop['share']:g}%  {drop['name']}{suffix}"))
                shown += 1
            if len(group) > 12:
                column.addWidget(_note(
                    f"   … and {len(group) - 12} more, each "
                    f"{group[12]['share']:g}% or less"))

        column.addWidget(_note(
            "Share of the drop table, not the chance the event pays out at "
            "all. Read through a borrowed def and a nested ItemTableParam — "
            "any entry the chain cannot name is shown as a raw category and "
            "id rather than guessed at."))

    def _render_gating(self, log_id: int, column: QVBoxLayout) -> bool:
        """Which Nightlords can roll this event, and how much of their pool.

        The share is exact: it is the fraction of that Nightlord's own map
        patterns carrying the event's modifier. It is deliberately not called
        a chance -- MapPatternSet weights the patterns, so the draw is not
        proven uniform, and "18% of Adel's patterns" is a statement the data
        actually supports.
        """
        entry = self.gating.get(str(log_id))
        if not entry:
            return False

        column.addWidget(_heading("WHICH NIGHTLORD  ·  FROM THE GAME FILES"))
        for boss in entry["bosses"]:
            column.addWidget(_stat(
                f"{boss['name']} — {boss['share']:g}% of its map patterns "
                f"({boss['patterns']} of {boss['of']})"))
        note = ("Every other Nightlord: never. Share of that Nightlord's map "
                "pattern pool, not a spin probability — the patterns carry "
                "their own draw weights, so the pool composition is what the "
                "data supports.")
        if entry["undersampled"]:
            note += (" This event draws rarely enough that a fourth eligible "
                     "Nightlord may simply not appear in the pool.")
        column.addWidget(_note(note))
        return True

    # -- the community layer ---------------------------------------------
    # Kept in its own methods, and every line it emits is tinted, so that a
    # later edit cannot quietly mix reported material into the extracted text.

    def _render_lore(self, lore: dict, column: QVBoxLayout,
                     covered: set[str] | None = None) -> None:
        if not lore:
            column.addWidget(_heading("WHAT IT DOES"))
            column.addWidget(_note(
                "Nothing recorded for this one. The files give the wording "
                "below and no more."
            ))
            return

        column.addWidget(_heading("WHAT IT DOES  ·  COMMUNITY-REPORTED"))
        column.addWidget(_community(lore["what"]))

        covered = covered or set()
        for label, key in (("Reward", "reward"), ("Penalty", "penalty")):
            # Never repeat something the extracted block above already said.
            if lore.get(key) and key not in covered:
                heading = QLabel(f"<b>{label}:</b> {lore[key]}")
                heading.setWordWrap(True)
                heading.setStyleSheet(f"color: {COMMUNITY}; font-size: 12px;")
                column.addWidget(heading)

        bosses = lore.get("nightlords") if "nightlords" not in covered else None
        if bosses:
            text = ("Every Nightlord." if bosses == ["Any"]
                    else ", ".join(bosses))
            label = QLabel(f"<b>Nightlord:</b> {text}")
            label.setWordWrap(True)
            label.setStyleSheet(f"color: {COMMUNITY}; font-size: 12px;")
            column.addWidget(label)
            column.addWidget(_note(
                "Still blue because it could not be confirmed. The gating is "
                "real and readable in outline — every one of the 520 map "
                "patterns carries exactly one targetBoss, and several pattern "
                "modifiers are drawn only for a subset of the ten — but no "
                "modifier can yet be tied to a named event, so which subset "
                "belongs to this event is unverified."))
        elif "nightlords" not in covered:
            column.addWidget(_note("Nightlord gating: not reported anywhere."))

        if lore.get("confirmed"):
            label = QLabel("<b>Confirmed in play:</b> " + lore["confirmed"])
            label.setWordWrap(True)
            label.setStyleSheet(f"color: {OBSERVED}; font-size: 12px;")
            column.addWidget(label)

        for key, prefix in (("note", "Note"), ("uncertain", "Least certain"),
                            ("conflict", "Sources disagree")):
            if lore.get(key):
                label = QLabel(f"<b>{prefix}:</b> {lore[key]}")
                label.setWordWrap(True)
                label.setStyleSheet(f"color: {UNKNOWN}; font-size: 11px;")
                column.addWidget(label)

        if lore.get("sources"):
            column.addWidget(_note("Reported by: " + ", ".join(lore["sources"])))

    def _render_unannounced(self, entry: dict, column: QVBoxLayout) -> None:
        title = QLabel(entry["name"])
        title.setWordWrap(True)
        title.setStyleSheet(
            f"color: {COMMUNITY}; font-size: 15px; font-weight: bold;")
        column.addWidget(title)
        column.addWidget(_note(
            "The game never puts a banner on screen for this one, so it has "
            "no display log row and cannot be extracted. Everything below is "
            "community-reported."
        ))
        self._render_lore(entry, column)
