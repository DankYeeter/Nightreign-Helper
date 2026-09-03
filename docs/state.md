# Stand

Stand: 2026-09-03, **Session pausiert fuer Handover** auf Nutzerwunsch,
mitten in Zyklus 11. Branch `docs/audit-and-advisor-design`. `main` ist
geschuetzt, PR #16 offen — Merge gehoert dem Nutzer.

**Naechster Schritt fuer die neue Session: `archivist` im Modus `sync-in`
zuerst**, dann diese Datei und `docs/plan-restarbeiten.md` lesen, dann direkt
weiterarbeiten. Der Plan `docs/plan-restarbeiten.md` ist die Reihenfolge,
diese Datei ist der Ist-Zustand.

## Was in dieser Session bis zum Pausieren geschah

**Der komplette AD-019-Fassaden-Umbau (W0 bis W6) ist fertig, abgenommen und
gepusht.** `nrplanner/damage.py` ist jetzt der einzige Aufrufer von
`weapons.rate`/`rank`, der AD-021-Waechter ist scharf, `WeaponRating.total`
ist entfernt. Testsuite 78 (Sessionbeginn) -> 296.

**Der Nutzer hat zwei entscheidende Spielmessungen geliefert:**
- **QA-018 GESCHLOSSEN:** "counterattack ist nur bei konter. nicht global."
  -> vier Effektfamilien (~22 IDs, `MOVE_SCOPED_EFFECT_IDS` in `model.py`)
  aus der flachen Multiplikatorschicht genommen. 203,4 steht jetzt auf
  Waffen-Tab **und** Detailtafel fuer den Ausgangsfall (Wylder's Greatsword +
  Improved Thrusting Counterattack).
- **QA-061 GESCHLOSSEN:** "anforderung ist das charakter level. sonst
  nichts." -> Checkbox "Meets requirements", Kachel-Dimmen, "Requires"-Zeile
  und der auf echten Daten unerreichbare `weapons.rate`-Zweig entfernt. Die
  **Skalierung** (Attribute wirken darueber) ist unangetastet.

**Danach in derselben Session, alles abgeschlossen und committet:**
- W6 vollstaendig (Multiplikatorschicht scharf, `weapons.rank` mit stabilem
  Zweitschluessel)
- Beschriftungen nachgezogen (UI_SPEC AK-34 Fassung B, README, ARCHITECTURE.md)
- **QA-085 behoben:** Signalverdrahtung des Arsenal-Tabs war von nichts
  gehalten (Spinbox und Tab-Wechsel bewegten nach Mutation keine Zahl, Suite
  blieb gruen) — jetzt mit eigenen Waechtern.
- **W5 vollstaendig:** `WeaponRating.total` faellt, `attack_rating` bleibt
  bewusst als zweite Schnittstelle (QA-071 entschieden, begruendet in
  `damage.py`).
- **QA-086 behoben:** zwei gezielte Faelle (mehrtypige Armatur vollstaendig,
  Rarity-Filter gegen Zusammenfassung), Zauber-Sektionen bewusst ohne
  Waechter mit Begruendungssatz.

## GENAU HIER unterbrochen — Anschlusspunkt fuer die neue Session

**Ein `qa-engineer`-Retest fuer T-036 (QA-085/086/W5, Commits `d4d4a50`,
`2be5e84`, `696e3d7`) wurde gestartet und ist NICHT zurueckgekommen** —
Session wurde pausiert, bevor das Ergebnis eintraf. **Diese drei Commits sind
NICHT gepusht** und haben KEINE unabhaengige Bestaetigung.

**Erster Auftrag der neuen Session:** den Retest fuer T-036 neu ansetzen
(gleicher Auftrag wie zuletzt: die fuenf neuen Mutationen nachfahren, die
W5-Charakterisierung gegenpruefen, den neuen Gleichstandsfall bei Duchess
verifizieren, den AD-021-Waechter angreifen, QA-085-Nebenpruefung). Dann bei
Freigabe `archivist` `sync-out`.

## Der Plan fuer den Rest — `docs/plan-restarbeiten.md`

Diese Datei existiert und ist die verbindliche Reihenfolge. **Nutzerauftrag:
alle Punkte abarbeiten, autonom, Zwischenfragen erlaubt, erst pausieren wenn
alles fertig ist** (das war der Stand vor dieser Pause — der Nutzer hat
gerade explizit unterbrochen, das gilt bis zur naechsten Anweisung).

Kurzfassung der Reihenfolge nach P2 (P1 und P2 sind fertig):
- **P3 — der Build-Berater selbst.** Das eigentliche Ziel aus `GOAL.md`
  (A3-A8). Entwurf (AD-014 bis AD-018, AD-023) und UI-Spec (AK-41 bis AK-62)
  stehen vollstaendig, **gebaut ist noch nichts.** Zwei UI-Defaults
  (Picker-Sortierung, ein/zwei Zielzahlen) sind vom `ui-ux-designer` bereits
  mit begruendetem Standard und Rueckfallweg entschieden — blockieren den Bau
  nicht.
  **Wichtig:** der Berater MUSS `damage.candidate()`/`rank_candidates()`
  nutzen, nicht `weapons.rate` direkt — der AD-021-Waechter erzwingt das
  automatisch, sobald `nrplanner/advisor/` existiert.
- **P4** — Save-Lesen/Inventar: QA-004, QA-007, QA-008, QA-010, QA-012,
  QA-016, QA-020, QA-027, QA-032, QA-038
- **P5** — Builds/Gefaesse: QA-026, QA-028, QA-030, QA-031, QA-044, QA-047,
  QA-048 (+ Nebenlaeufigkeit der Migration, dasselbe Fenster), QA-054
- **P6** — Sicherheit: SEC-016+018+006-Nachtrag als EIN Auftrag, SEC-017,
  SEC-019+015 (Label-Fabrik, NICHT 90 Einzelaenderungen), SEC-020, SEC-011
- **P7** — Waechter-/Testschulden: QA-019 (Status pruefen, evtl. schon durch
  T-034 erledigt), QA-023, QA-037, QA-052/053, QA-059, QA-066, QA-077 (34
  Tooltips ungedeckt), QA-078, QA-087, QA-088
- **P8** — Oberflaeche: DR-004 bis DR-007, QA-029, QA-067, QA-089
- **P9** — Releasefaehigkeit: QA-036 (Icon-Pack-Ursache), SEC-009 (2 Punkte),
  dann `compliance-agent`, `technical-writer`, `release-manager`
  (build/clean-room), `power-user`, **GOAL A9**

**Zurueckgestellt, nicht vergessen:** `ruff` (kein Linter im Repo, dritte
Erwaehnung), C-002 (**auf Nutzeranweisung ignoriert, nicht erneut
vorlegen**).

## Regeln, die fuer jeden Schritt weiter gelten
- Jeder neue Waechter braucht seine **toetende Mutation**.
- Charakterisierungen auf der **ungerundeten** Zahl, Anzeigetext getrennt
  (QA-074-Disziplin).
- Die Messstrecke unter `scripts/differential/` **benutzen, nicht neu
  bauen** — sie liegt im Repo, das Raster als Datei.
- **Eine Zusicherung nennt ihren Geltungsbereich** — die dominante
  Fehlerklasse dieses Projekts (QA-046, 050, 052, 062, 063, 064, 070, 073,
  082, 083, 086, 087). Jede Familienliste, jeder Kommentar, jeder
  Docstring: sagen, was er deckt und was nicht.
- Bitgleiche Schritte: 0 Abweichungen ist die Abnahme. Bewusst aendernde
  Schritte: Charakterisieren, nicht vermeiden — jede Abweichung einem Grund
  zuordnen, unpassende melden statt einsortieren.

## Was niemand geprueft hat, und das bleibt so
- Die Oberflaeche als **benutztes Programm** — Waffen-Tab und Tafel sind
  headless UND einmal am laufenden Fenster fotografiert (W3/W4-Abnahmen),
  aber niemand hat es als Nutzer bedient. Das ist `power-user`, nach P9.
- Ein gebautes Artefakt (GOAL A9) — noch nie geprueft.
- Linux/macOS — Windows-only-Projekt, nie ein Thema.
