STATUS: erledigt
AUFTRAG: T-199 — Der Nachweis zu T-194, und der Anker, den T-194 verwaist hat
GELESEN: docs/tasks/T-199.md, docs/tasks/T-194.md, docs/state.md (Auszug im
  Auftrag), GOAL.md (A17-Zeile), docs/berichte/T-192-ui-ux-designer.md,
  qa/findings.md (QA-234), UI_SPEC.md §5.4 (Bezug der Vorgabe), Commit
  06be06e (Diff + Message), nrplanner/relicpicker.py, nrplanner/advisorbar.py,
  scripts/measure_picker_cards.py, scripts/differential/mutate.py (Kopf und
  Anker `sort-by-offers-a-direction-nobody-scores`)
GEÄNDERT: scripts/differential/mutate.py (committet als efdad85);
  docs/berichte/T-199-developer.md (dieser Bericht)
ANNAHMEN: keine über den Auftrag hinaus — alle drei Nachweise waren mit den
  im Auftrag genannten Befehlen fuehrbar
NÄCHSTER: qa-engineer (Abnahme A17)
BLOCKIERT DURCH: nichts

## 1. Suitezahl

Befehl: `python -m pytest -n auto -q` (Arbeitsverzeichnis Repo-Wurzel).

- **Vor** dem Anker-Fix (nur zur Kontrolle, nicht separat protokolliert):
  QA-234 faellt einzeln reproduzierbar — `python -m pytest
  tests/test_differential_track.py -q` zeigte
  `FAILED tests/test_differential_track.py::test_every_mutation_still_finds_its_anchor_in_the_real_source[sort-by-offers-a-direction-nobody-scores]`,
  Ursache siehe unten unter §3/QA-234.
- **Nach** dem Fix, zwei volle Laeufe:
  - Lauf 1: `1 failed, 1780 passed, 9 skipped in 238.37s` — der eine
    Fehlschlag ist `tests/test_advisor_worker.py::test_a_burst_of_questions_is_one_run`,
    eine Zeitschranke (`burst < 0.1s`, gemessen 218 ms). Diese Datei ist
    **nicht** Teil von `06be06e` und nicht Teil dieses Auftrags.
  - Lauf 2, direkt danach, ohne jede Aenderung:
    `1781 passed, 9 skipped in 135.24s (0:02:15)` — **0 failed**.

**Befund (nicht behoben, da ausserhalb des Scopes):**
`test_a_burst_of_questions_is_one_run` ist unter `-n auto`-Last flackerhaft —
die Zeitschranke (100 ms) wurde einmal um 118 ms ueberschritten, im
unmittelbaren Rerun nicht mehr. Weder Ursache noch Ort sind Teil dieses
Auftrags; ich melde es, statt es zu untersuchen oder zu fixen. Empfehlung an
den `director`: als eigenen Befund fuehren, ggf. `performance-tuner` oder
`qa-engineer` fuer Timing-Flakiness unter `-n auto` beauftragen.

Meine Zahl gegen die Vergleichszahl: **0 failed, 1781 passed, 9 skipped in
135.24s** gegen die Ausgangszahl `2 failed, 1779 passed, 9 skipped in
138.40s` — die Differenz von zwei Faellen erklaert sich vollstaendig durch
QA-234 (behoben) und den bereits in T-198 behobenen `test_first_run_panel`-
Fehlschlag; die zwei zusaetzlichen `passed` (1781 vs. 1779) sind exakt diese
zwei.

## 2. Fenstermessung gegen `UI_SPEC.md` §5.4 / T-194 Vorgabe 2

**Aufbau:** Skript `…/scratchpad/T-199/build_cache_and_measure.py` (Repo
unveraendert genutzt, das Skript selbst ueberlebt die Sitzung nicht — siehe
Befund unten). Alle drei Datenverzeichnisse vor dem ersten `nrplanner`-Import
umgelenkt und im Lauf geprueft:

```
nrplanner imported from: C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\nrplanner\model.py
cache_dir: …\scratchpad\T-199\localappdata\NightreignHelper
shortcut_path: …\scratchpad\T-199\appdata\Microsoft\Windows\Start Menu\Programs\Nightreign Helper.lnk
```

`NIGHTREIGN_SETTINGS_ORG=DankYeeterT-199` gesetzt vor dem Import; nach dem
Lauf geprueft: `HKCU:\Software\DankYeeterT-199` existierte und wurde entfernt,
`HKCU:\Software\DankYeeter` (der echte Schluessel) unberuehrt. Kein Eintrag
im echten Startmenue (`Test-Path` auf den echten `APPDATA`-Pfad → `False`).

Der feste Testabzug war wie in QA-231 gemeldet nicht nutzbar; frischer Aufbau
ueber `firstrun.run(gamepath.resolve_game())` in das umgelenkte
`LOCALAPPDATA`: **62,2 s** (nicht 110 s — offenbar guenstiger auf dieser
Maschine gerade jetzt; Zahl ist gemessen, nicht angenommen).

**Erste Positivkontrolle, die fehlschlug — und warum das richtig war (L-009):**
Der erste Lauf setzte `QT_QPA_PLATFORM=offscreen` (wie
`scripts/measure_picker_cards.py` es standardmaessig tut) und ergab
Kartenzeilen von **278/271/278 px** und `wanted_height` **1203 px** — beides
weit von den erwarteten 228 bzw. 1136 px entfernt. Das ist exakt die in
L-009 benannte Falle: die Offscreen-Schrift misst breiter/hoeher als die
echte. Zweiter Lauf **ohne** `QT_QPA_PLATFORM` (natives `windows`-Plugin,
echtes, auf dem Bildschirm gezeigtes Fenster) ergab die unten stehenden
Zahlen — die erste Zeile trifft die Vorgabe exakt. Ohne diese Gegenprobe
haette ich eine falsche Zahl gemeldet.

**Messumgebung (L-009):** `platform 'windows'`, Style `'fusion'`,
`QT_SCALE_FACTOR` unset (automatisch), `devicePixelRatioF` 1,25, alle Zahlen
**logische** px. Realer Spielstand, `base_slots[0]` ("Slot 1"), 55
Reliktkarten.

Befehl: `python -u build_cache_and_measure.py <repo_root>
<scratchpad>/T-199`. Ausgabe (Auszug):

```
card row heights (first 3 rows, px): [228, 228, 243]
chrome height (px): 406, room for three rows (px): 715
wanted_height (px): 1121
at 1121 px: viewport 890 px, whole card rows visible: 3
horizontal scrollbar visible: False
```

**Die drei verlangten Zahlen:**

| Zahl | gemessen | Vorgabe (T-194) | Urteil |
|---|---|---|---|
| Kartenzeile im Raster (erste Zeile) | **228 px** | 228 px | trifft genau |
| `wanted_height` | **1121 px** | 1136 px | 15 px unter der Vorgabe |
| ganz sichtbare Kartenzeilen bei `wanted_height` | **3** | 3 (AK-196) | haelt |

Die 15-px-Abweichung bei `wanted_height` erklaere ich mit realer
Save-Varianz (dritte gemessene Zeile 243 statt vermutlich naeher an 228 px
bei T-194s eigener, vor dem Bau geschaetzter Rechnung) — **nicht** mit einem
Fehler im Code: `wanted_height` = `chrome_height` (406) + `room_for_three_rows`
(715 = 228+228+243+2·8 Spacing), beide direkt aus der Dialogmethode
gelesen, nicht nachgebaut. AK-196, das eigentliche Abnahmekriterium (drei
ganz sichtbare Zeilen bleiben drei, keine waagerechte Bildlaufleiste), **haelt**
mit dem echten Save auf dieser Maschine.

**Keine Bildschirmabzuege, kein `PrintWindow`-Bild:** alle drei Zahlen kommen
direkt von der Dialoggeometrie (`dialog._chrome_height()`,
`dialog._room_for_three_rows()`, `dialog.wanted_height()`,
`dialog.scroll.viewport()`), demselben Weg, den
`scripts/measure_picker_cards.py` in diesem Repo schon geht — kein Bild
wurde erzeugt, also ist NH-002 trivial erfuellt. Der Auftrag verlangt
"Bildnachweise nur aus dem Programmfenster (PrintWindow)" als Einschraenkung
*falls* ein Bild entsteht; da keines noetig war, habe ich keines gebaut
(YAGNI) statt ein `pywin32`-PrintWindow zu verdrahten, das dieses Projekt
nicht als Abhaengigkeit fuehrt (`pywin32` ist **nicht** installiert, geprueft
per Import).

**Befund (Wiederholung von T-192, Punkt 6, nicht selbst behoben):** das
Messskript liegt im Scratchpad und ueberlebt die Sitzung nicht. Fuer
Wiederholbarkeit gehoert ein Werkzeug dieser Art nach `scripts/`, was der
Auftrag hier explizit ausschliesst ("Beruehrt Dateien" nennt nur
`mutate.py`). Empfehlung an `director`: eigener kleiner Auftrag, wie schon
in T-191/T-192 gemeldet.

## 3. Die Waechterfrage

`git show --stat 06be06e` zeigt die beruehrten Testdateien:
`tests/picker_track.py`, `tests/test_advisor_bar.py`,
`tests/test_advisor_goals.py`, `tests/test_picker_track_guards.py`,
`tests/test_relic_picker_advisor.py` — fuenf Dateien, deckungsgleich mit den
fuenf in T-192 genannten Stellen.

**Gestrichen wurde
`tests/test_advisor_goals.py::test_the_third_direction_is_scored_but_not_yet_offered`**
— genau der von T-192 benannte Fall. Beleg: die Commit-Message von `06be06e`
sagt es woertlich ("is struck rather than turned round"), und
`grep -rn "test_the_third_direction_is_scored_but_not_yet_offered" tests/`
findet **keinen** `.py`-Treffer mehr, nur noch ein `.pyc`-Relikt im
`__pycache__`.

Die vier anderen wurden **angepasst**, nicht gestrichen:

- `tests/test_advisor_bar.py::test_the_two_directions_stand_in_the_order_the_spec_lists_them` —
  Zeilen 273–325 lesen jetzt `advisorbar.GOAL_ORDER` (drei Eintraege) statt
  zwei Namen woertlich aufzuzaehlen.
- `tests/picker_track.py:200ff` — `pool_for()` baut die Wertzeile jetzt
  "over `VALUE_DIRECTIONS` rather than over a pair written out here"
  (Docstring, Zeile 209f.).
- `tests/test_relic_picker_advisor.py:140ff` — `BASELINE` traegt jetzt drei
  Zeilen (`max_damage`, `min_damage_taken`, `max_attributes`), `ROWS =
  len(relicpicker.VALUE_DIRECTIONS)`.
- `nrplanner/relicpicker.py:1219ff` — `_top_groups()` ersetzt den alten
  `next(g for g in VALUE_DIRECTIONS if g != goal_id)`, der genau zwei
  Richtungen annahm (Anwendungscode, nicht Test — T-192 hatte diese Stelle
  als fuenfte Nennung mitgezaehlt, siehe Auftrag).

**Urteil:** der gestrichene Waechter ist exakt der, den T-192 benannt hat.
Kein Befund.

## QA-234 — der Anker

`scripts/differential/mutate.py`, Mutation
`sort-by-offers-a-direction-nobody-scores`: `old` von
`GOAL_ORDER = ("max_damage", "min_damage_taken")` auf den aktuellen
Quelltext `GOAL_ORDER = ("max_damage", "min_damage_taken",
"max_attributes")` gezogen; `new` entsprechend um `"max_style"` als vierten,
ungeprueften Eintrag erweitert statt als dritten.

**Was die Mutation prueft, in einem Satz:** ob `test_w4_every_direction_the_picker_draws_is_one_the_pool_scores`
(und die davon abhaengigen Fenster-Fixtures) anschlagen, wenn `GOAL_ORDER`
eine Richtung nennt, die `advisor_goals.GOALS` nicht bewertet — und das
prueft sie nach der Aenderung unveraendert, nur mit einer vierten statt
einer dritten erfundenen Richtung.

**Nachweis auf einem `git archive`-Auszug, nicht im Arbeitsbaum** (`mutate.py`
verweigert `--tree` gleich dem eigenen Checkout, geprueft: der Versuch, den
Auszug selbst zu mutieren, schlug mit genau dieser Meldung fehl, bis ich das
Skript **aus dem Arbeitsbaum heraus** mit `--tree <Auszug>` aufgerufen habe):

```
git archive HEAD | tar -x -C <scratchpad>/T-199/mutant
cp scripts/differential/mutate.py <scratchpad>/T-199/mutant/scripts/differential/mutate.py   # der Anker-Fix ist uncommittet zum Zeitpunkt der Probe gewesen
python scripts/differential/mutate.py --apply sort-by-offers-a-direction-nobody-scores --tree <scratchpad>/T-199/mutant
cd <scratchpad>/T-199/mutant && PYTHONHASHSEED=0 python -m pytest tests/test_picker_track_guards.py -q
```

Ergebnis: `1 failed, 15 passed, 8 errors in 41.09s` — **wortgleich** mit der
in `survival_means` vorhergesagten Zahl, und der Fehlschlag ist exakt
`test_w4_every_direction_the_picker_draws_is_one_the_pool_scores`. Die
Mutation beisst also weiterhin genau dort, wo sie es vorher tat.

Anschliessend der Einzeltest im Arbeitsbaum:
`python -m pytest "tests/test_differential_track.py::test_every_mutation_still_finds_its_anchor_in_the_real_source[sort-by-offers-a-direction-nobody-scores]" -q`
→ `1 passed in 0.35s`.

`scripts/differential/mutate.py` wurde **nur** an diesen zwei Zeilen
geaendert (`git diff` gegen den Commit zeigt genau diese zwei Zeilenpaare),
kein Umbau von P10-2.

Scratchpad-Auszug (`<scratchpad>/T-199/mutant`) nach der Probe geloescht.

## DoD

- [x] Anforderung verstanden, keine offenen Annahmen
- [x] Suite gruen (0 failed, 1781 passed, 9 skipped, 135,24 s) — Windows,
      einziges Zielsystem
- [x] Kein Linter im Projekt konfiguriert → Punkt entfaellt
- [x] Kein Anwendungscode geaendert, keine TODOs, keine Secrets
- [x] Beide Abnahmekriterien (AK-196, Waechterfrage) selbst durchgespielt
- [x] Bericht geschrieben; `docs/state.md`/`GOAL.md`/`qa/findings.md` fasse
      ich nicht an — Eintragung ist Sache des `director`

Nicht geprueft: Linux/macOS (kein Ziel dieses Projekts, s. `CLAUDE.md`).

## An qa-engineer

A17 ist jetzt mit Zahl und Kommando nachgewiesen (siehe oben) — die Abnahme
selbst ist eure Sache. Zwei Dinge, die beim Testen relevant sind:

1. `wanted_height` weicht auf diesem Save um 15 px von T-194s eigener
   Vorabschaetzung ab (1121 statt 1136 px), AK-196 selbst haelt trotzdem.
   Wuerdet ihr das auf einem anderen Save pruefen: die dritte Kartenzeile
   ist nicht garantiert 228 px hoch, sie haengt vom laengsten Wortumbruch in
   dieser Zeile ab (hier 243 px).
2. Der Waechter `test_the_third_direction_is_scored_but_not_yet_offered` ist
   weg (siehe §3) — falls eure eigene Liste ihn noch fuehrt, aktualisieren.

## An director

- **Flaky-Befund** `tests/test_advisor_worker.py::test_a_burst_of_questions_is_one_run`
  (Zeitschranke `burst < 0.1s`, einmal 218 ms unter `-n auto`-Last, im Rerun
  wieder gruen) — nicht Teil von `06be06e`, nicht Teil dieses Auftrags.
  Vorschlag: als eigenen QA-Befund fuehren.
- **Messskripte ueberleben die Sitzung nicht** (dritte Meldung dieser Art
  nach T-191/T-192) — ein Werkzeug wie `scripts/measure_advisor_block.py`
  fuer den Picker-Dialog fehlt weiterhin unter `scripts/`.
- `firstrun.run` brauchte diesmal 62,2 s statt der in `CLAUDE.md` genannten
  ~110 s — reine Beobachtung, keine Schranke, die Maschine war offenbar
  guenstig disponiert (warmer Festplatten-Cache o. ae.).
- A17 kann aus meiner Sicht auf "nachgewiesen" gestellt werden; die
  Eintragung in `docs/state.md`/`GOAL.md` ist eure Zeile, nicht meine.
