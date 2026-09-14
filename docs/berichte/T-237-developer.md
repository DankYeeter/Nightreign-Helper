# T-237 — A12/A13 auf Build planner und Weapons: Chips, Karten, Wertzellen (developer)

```
STATUS: erledigt
AUFTRAG: T-237
GELESEN: docs/tasks/T-237.md, ~/.claude/agents/_rahmen.md, CLAUDE.md (Projekt),
         qa/findings.md Z. 163/166/251/252, DESIGN_REVIEW.md Z. 516-530,
         UI_SPEC.md AK-46, AK-73, AK-84, AK-99, AK-262, AK-271,
         docs/berichte/T-192-ui-ux-designer.md (Messteil), nrplanner/relicpicker.py,
         arsenaltab.py (Tile, Section, _grid), depthstab.py (VariantTable, nur gelesen),
         cardgrid.py, scripts/differential/mutate.py, scripts/make_screenshots.py,
         scripts/measure_picker_cards.py, tests/advisor_row_at_the_window.py,
         tests/test_relic_picker_geometry.py, tests/test_relic_picker_advisor.py
GEÄNDERT: nrplanner/relicpicker.py, tests/relic_card_at_the_window.py (neu),
          tests/test_relic_picker_geometry.py, scripts/differential/mutate.py,
          docs/berichte/T-237-developer.md
ANNAHMEN: 1) "1536 px logisch" = Hauptfenster auf 1536 px Breite gesetzt; der
          Picker oeffnet in seiner eigenen Breite (1024 vorher, 1114 nachher).
          2) Drei Stellen von effective HP (`+999.9`) sind die Obergrenze, gegen
          die die Karte bemessen ist; T-192 nennt vier als ausserhalb des Datensatzes.
          3) Die Suitezahl der Praemisse (1531/9 auf 49b5a78) habe ich nicht
          nachgezaehlt (Volllauf-Schwelle); gesammelt sind jetzt 1535 Knoten.
NÄCHSTER: qa-engineer (Retest, zwei Mutationen nachfahren und loeschen)
BLOCKIERT DURCH: nichts
```

## Je Befund

Messumgebung aller Zahlen: Windows 11, Qt `windows`, Fusion, Segoe UI 9 pt,
dPR 1,25, logische px; Hauptfenster 1536 px breit; Daten umgelenkt
(`HKCU\Software\DankYeeterT-237`, `paths.cache_dir()` im Scratchpad,
Testabzug kopiert, `extract_version` 11); Bilder per `PrintWindow` auf das
eigene HWND. Skript und Bilder: `<scratchpad>/T-237/measure.py`,
`shots-before/`, `shots/`.

| Befund | Reproduktion vorher | Ergebnis | Commit |
|---|---|---|---|
| QA-229 | 3 von 6 Chips abgeschnitten: `BEST FOR DAMAGE` 91 px, `BEST FOR SURVIVAL` 95 px in 79 px auf favorisierten Karten (`picker-fav-1536-cut-chip.png`) | **behoben** — Stern neben dem Namen statt neben der Namensspalte; Chipstreifen 118 px auf jeder Karte, 0 von 6 abgeschnitten | `5dd0cf7` |
| QA-230 | 6 von 162 Wertzellen abgeschnitten, `+64.2 effective HP` 104 px in 93-95 px (`picker-fav-1536-cut-cell.png`, Vorzeichen und erste Ziffer fehlen) | **behoben** — `CARD_WIDTH` 190 → 208, bemessen an `Damage taken` (70) + 6 + `+999.9 effective HP` (111) + 16 Rand + 4 Rahmen; 0 von 162 | `5dd0cf7` |
| QA-141 | 0 von 54 Karten ueber den Viewport hinaus, 5 Spalten, keine waagerechte Leiste (`picker-plain-1536.png`, vorher) | **bereits behoben** | `86fb5a7` (05.09.) |
| DR-016 | (a) 0 von 92 sichtbaren Kacheln abgeschnitten, 7 Spalten, keine Leiste; (b) 135 mehrgruppige Werte, 46 umgebrochen, 0 Gruppen breiter als ihr Label — Umbruch nur an ` · ` (`arsenal-1536.png`) | **bereits behoben** | `a39d58f` (05.09.) |
| QA-144 | 1536 px: `What can be red` 984 px, `Examples (any map)` 349 px; 833 px: 315 / 315 px (`depths-1536.png`, `depths-833.png`) | **bereits behoben** — Datei gehoert T-236, nichts geaendert | `ba22a06` |

Waechter: `test_the_chip_is_whole_on_a_favourite_card`,
`test_every_value_cell_holds_its_widest_figure` in
`tests/test_relic_picker_geometry.py`; beide messen im Kindprozess unter
`QT_QPA_PLATFORM=windows` (`tests/relic_card_at_the_window.py`), weil die
Offscreen-Schrift jede Karte schneidet. Beide von Hand gegen die Mutation
gefahren: Stern im Kopf → `chip_cut true, 79 px`; 190 px → `cells_cut
["+999.9 effective HP"]`. `MUTATIONS`: `favourite-star-back-beside-the-chip`,
`relic-card-back-to-190-px` (`d40f71d`).

Suite `pytest -n auto` auf `d40f71d`: **1526 passed, 9 skipped, 168 s**
(1535 gesammelt, davon 2 neu).

## Befunde und Hinweise (Nummern vergibt der Director)

1. **Register veraltet:** QA-141, QA-144, DR-016 stehen als `offen`, sind seit
   dem 05.09. behoben (Commits oben, heute am Fenster bestaetigt).
2. **AK-262 neu vorlegen (ui-ux-designer):** die Spec sagt selbst, ein
   verbreiterter Chipstreifen legt `BEST FOR ATTRIBUTES` (106 px) wieder vor.
   Der Streifen ist jetzt 118 px auf jeder Karte. Ich habe `BEST FOR STATS`
   nicht angeruehrt; der Kommentar an `DIRECTION_NOUNS` nennt den Stand.
3. **Kartenbreite (ui-ux-designer, zur Kenntnis):** Karte 190 → 208 px, Picker
   oeffnet 1114 statt 1024 px breit; Stern steht rechts neben dem Namen, oben
   ausgerichtet. AK-262 nennt die Karte mit "190 px" als Messbeschreibung, nicht
   als Vorgabe.
4. **Suitezahl:** Praemisse 1531/9 (=1540) gegen 1535 gesammelt heute inkl.
   2 neuer Knoten; die Differenz von 7 habe ich nicht aufgeklaert
   (Volllauf-Schwelle erreicht). `tests/` ist gegen `49b5a78` nur um die zwei
   Dateien gewachsen (`git diff 49b5a78 --stat -- tests`).
5. **Aufraeumen belegt:** `HKCU\Software\DankYeeterT-237` geloescht
   (`reg query`: not found), `HKCU\Software\DankYeeter` vorhanden; kein
   Fensterprozess offen; Scratchpad `T-237/` bleibt mit Skript und Bildern.

Ponytail-Review `git diff 49b5a78..HEAD`: net +181 Zeilen (196 hinzu, 15 weg; Kindprozess-Modul
99, Tests 42, Mutationen 26, Picker 25). Kein Streichkandidat: der Kindprozess
ist der einzige Weg zu echten Schriftbreiten in der Suite.
