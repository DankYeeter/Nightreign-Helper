# T-239a — qa-engineer, 14.09.2026: Pruefphase auf `a68cd3d`

Code eingefroren; einzige Aenderung ausser diesem Bericht: die zwei
nachgefahrenen `MUTATIONS`-Eintraege in `scripts/differential/mutate.py`
geleert (OF-35). Umgebung durchgehend: `NIGHTREIGN_SETTINGS_ORG`/
`LOCALAPPDATA`/`APPDATA` auf `<scratchpad>/T-239/qa/...` umgelenkt, fester
Testabzug (841 Dateien, `EXTRACT_VERSION` 11) kopiert. Fenster: 4096x1728
logisch, dPR 1.25, Stil `fusion`, 1536 px logische Fensterbreite, PrintWindow
(NH-002). Skripte im Scratchpad `T-239/qa/`.

## Bestehende Tests

`pytest tests/test_relic_picker_geometry.py tests/test_arsenal_tab_asks_the_facade.py
tests/test_world_events_display.py tests/test_differential_track.py -q` →
**70 passed** (ohne `-n`, direkt). NH-003-Waechter auf `qa/findings.md` nach
Anhaengen: 8 passed.

## 1. Regression Build-planner nach AD-034 — live, kein Befund

Reliktkarte + Hold-Button (`Hold`→`Held`→zurueck), Picker (offen, 54 Karten,
`card.button.click()` → `dialog.chosen` korrekt, `relic_box` uebernimmt die
Wahl), Wartetext beim Save-Lesen (`is_reading()` true vor `ready`), `Find my
save` (Button existiert, per Konstruktion verdeckt solange der Save
automatisch gefunden wurde — `find_save_button.setVisible(False)` ist der
Default, `True` nur auf den Fehlpfaden), Werteblatt Grundwerte (`ar_label`
gefuellt), Aufschluesselung per Klick (`AR_BREAKDOWN_KEY = "ar:total"` im
HTML-Link, `_ar_breakdown_text()` liefert echten Text, `linkActivated.emit`
wirft nicht), Situationsschalter → `declared_changed` (mit echtem
Reliktbesitz ausgeloest: `Grand Luminous Scene` erzeugt eine Zeile, Toggle
feuert `declared_changed` mit int-Schluessel-Payload, `ar_label` aendert sich
— Vertrag `Signal(object)` aus dem AD-034-Nachtrag bestaetigt), Optimize
(`answer` kommt in 0,39 s als `AdvisorResult`, Button faellt auf `Optimize`
zurueck). **Anmerkung zur eigenen Messung:** die ersten Laeufe zeigten
Fehlanzeigen (Picker "waehlte nichts", Optimize "keine Antwort") — beides war
ein Fehler im eigenen Skript (falscher Klick-Handler bzw. falsche
Wartebedingung), nach Korrektur reproduzierbar gruen. Kein Befund.

## 2. A12/A13 je Tab (sechs Content-Tabs, 1536 px/fusion/PrintWindow)

| Tab | AK-68 Kopf+Frage | A13 abgeschnittene Labels | Bemerkung |
|---|---|---|---|
| Effects && chances | vorhanden | 0 | — |
| Weapons && spells | vorhanden | 0 | s. Pkt 3 |
| Nightlords | vorhanden | 0 | — |
| Deep of Night | vorhanden | 0 | minimumSizeHint 68 px (Screen 1728 hoch) |
| Red variants | vorhanden | 0 | — |
| World Events | vorhanden | 0 | — |

Kein Tab mit horizontaler Bildlaufleiste, keine `minimumSizeHint().height()`
ueber 242 px (AK-71-Grenze 860). Keine Sammelaussage noetig: alle sechs
einzeln null Treffer.

## 3. QA-128 Punkte 1-3 (Waffenkacheln `Scaling STR 50`) — bestaetigt behoben

`arsenaltab.SCALING_SENTENCE` (AK-85, Commit `324abf0`, 05.09.2026 — **vor**
dieser Pruefphasen-Reihe, aber im Findings-Register bislang als "ungeprueft"
fuer 1-3 gefuehrt) steht live im Zusammenfassungsblock, wortgleich zur
UI_SPEC-Vorgabe, ungekuerzt. 230 sichtbare Kacheln tragen weiterhin
`Scaling STR 50` ohne eigene Einheit — das ist beabsichtigt (A7-Fall: die
Buchstabennote ist aus den Dateien nicht ableitbar, der Satz sagt das statt
zu raten). Register nachgezogen (Zeile QA-128 unten).

## 4. Retest QA-229/QA-230 — bestaetigt, plus eigenstaendiges Rot-vorher

Live: 0 von 6 Chips, 0 von 162 Wertzellen abgeschnitten (plain und
favourite). Zusaetzlich zum Vergleich mit T-237s Bildern (Scratchpad
`T-237/shots/`) eigene PrintWindow-Aufnahmen (`T-239/qa/shots/`). Rot-vorher
beider Mutationen selbst nachgefahren (`git archive` + Extraktion in zwei
Scratch-Klone, nicht der Checkout): beide Waechtertests fallen mit der in
`mutate.py` vorhergesagten Meldung. Register nachgezogen, `MUTATIONS`
anschliessend geleert (OF-35) — beide Eintraege waren die einzigen lebenden,
kein Rest.

## 5. AK-188/AK-169 auf 314 Kopien nachgezaehlt

`inventory.load(data).relic_count` = **314** (drei unabhaengige Messungen:
Fenster-Skript, `measure_advisor_language.py`, Picker-Skript — alle 314).
`GOAL.md` A6 nennt noch **312** (Nachtrag 13.09.2026 morgens); beide Zahlen
gemeldet, nichts geaendert.

`scripts/measure_advisor_language.py` (Rezept A, T-092-Umgebung) auf dem
lebenden Save:
- `curses_without_a_figure` = **67** von 143 Fluchzeilen — deckt sich mit dem
  in UI_SPEC A33 fuer 314 Kopien festgehaltenen Wert (beide Rezepte).
- `effects_without_a_figure` = **437 von 860** — deckt sich exakt mit A33s
  Rezept-A-Zahl (437). Rezept B (`asking_from`, Programmpfad, dort 438) habe
  ich nicht separat nachgerechnet; die exakte Uebereinstimmung bei Rezept A
  und bei den Curses ist aber ein Indiz, dass der Save seit T-231 nicht
  weitergewachsen ist und Rezept B ebenfalls noch stimmt.
- AK-169/AK-180-Partition (a/a2/b/c/d/e), bisher nur fuer 309 Kopien
  gemessen und laut UI_SPEC "ausserhalb des Auftrags nicht nachgezaehlt": bei
  314 Kopien, Rezept A, jetzt gemessen: **154 / 0 / 147 / 40 / 96 / 0 = 437**.
  Nicht ins UI_SPEC uebernommen (Register nicht mein Dokument) — Zahl geht an
  den `ui-ux-designer`.
- `schlechtester Fall 42` (AK-188s zweite Zahl) habe ich nicht reproduziert;
  welche Rezeptvariante das erzeugt, war aus dem Code in der verfuegbaren
  Zeit nicht sicher zu bestimmen. Als offen vermerkt, kein Befund.

## 6. A2-A8 gegen den Quellstand

- **A2**: einziger offener P1 ist QA-237, vom Nutzer am 14.09. ausdruecklich
  zurueckgestellt (`docs/state.md`) — erfuellt. Kein offener P1 in
  `security/findings.md`.
- **A3**: `goals.GOALS` fuehrt mindestens `max_damage` und
  `min_damage_taken`; Optimize-Lauf live lieferte 40 Vorschlaege mit
  Slot-Zuordnung.
- **A4**: Farb-/Deep-Parameter (`types.Slot(colour=, deep=)`) strukturell
  vorhanden und im Lauf genutzt; keine vertiefte Nachpruefung ueber die
  bestehende Suite hinaus (Advisor-Code von AD-034 nicht beruehrt).
- **A5**: `explain.reasons` liefert Begruendungszeilen je Vorschlag, live
  bestaetigt.
- **A6**: ein Optimize-Lauf 0,39 s (Budget 6 s) — Stichprobe, keine
  Ersatzmessung fuer `performance-tuner`.
- **A7**: `SCALING_SENTENCE`/`BUILDUP_SENTENCE` u. a. tragen die
  "files do not say"-Formel, live bestaetigt.
- **A8**: alle live gesehenen Texte (sechs Tabs, Planner, Picker,
  Fehlermeldungen) Englisch, keine Ausnahme gefunden.

## Nicht getestet

Linux/macOS (nie Ziel). Rezept-B-Nachrechnung fuer AK-188 (438/331) und der
"schlechtester Fall 42". A4-Stacking-Kanten- und A6-Vollmessung (gehoert
`performance-tuner`). Gebautes Artefakt (A9 — separater Auftrag).

## Urteil

**PASS.** Kein P1/P2-Befund aus dieser Pruefphase; QA-128/QA-229/QA-230
schliessen mit dieser Bestaetigung. Zwei offene Zahlen (Rezept B, "42") als
Beobachtung an den `ui-ux-designer`/`director` — nicht releaseblockierend.

```
STATUS: erledigt
AUFTRAG: docs/tasks/T-239.md, Abschnitt T-239a
GELESEN: docs/tasks/T-239.md, GOAL.md, qa/findings.md, UI_SPEC.md (AK-85,
  AK-168-188), docs/state.md, docs/berichte/T-236-developer.md,
  scripts/differential/mutate.py, nrplanner/{arsenaltab,relicpicker,
  statsheet,relicslots,advisorbar,tabheader}.py, scripts/measure_advisor_language.py
GEÄNDERT: scripts/differential/mutate.py (MUTATIONS geleert, OF-35),
  qa/findings.md (3 Zeilen angehaengt), docs/berichte/T-239-qa-engineer.md (neu)
ANNAHMEN: "sechs Tabs" aus A12/A13 sind die sechs Content-Tabs ohne
  "Build planner" (AK-68-Wortlaut, konsistent mit dem Register); Rezept A
  aus measure_advisor_language.py ist die T-092-Umgebung, Rezept B ist
  advisorbar.asking_from am echten Fenster (aus dem UI_SPEC-Text abgeleitet)
NÄCHSTER: ui-ux-designer prueft AK-188 Rezept B/„schlechtester Fall" und
  traegt die AK-169-Partition (154/0/147/40/96/0=437) nach; director
  entscheidet ueber GOAL.md 312 vs. 314
BLOCKIERT DURCH: keins
```
