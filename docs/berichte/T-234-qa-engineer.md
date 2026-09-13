# T-234 — Retest-Bericht (qa-engineer, 13.09.2026)

```
STATUS: erledigt
AUFTRAG: docs/tasks/T-234.md — Retest auf dcd061d (Code 7bc8b04): QA-250/251/
232/252/249/253/254, SEC-041/043, DR-022/023 bestaetigen/zurueckweisen,
Urteil PASS/CONCERNS/FAIL
GELESEN: docs/tasks/T-234.md (ganz), CLAUDE.md, ~/.claude/agents/_rahmen.md,
docs/berichte/T-229-qa-engineer.md, T-230-developer.md, git log
acbe241..7bc8b04, qa/findings.md (Z. 254-293), security/findings.md
(Z. 59-74), DESIGN_REVIEW.md (DR-022/023), scripts/differential/mutate.py
(ganz), nrplanner/relicpicker.py (_ask, _the_stock_was_replaced,
_refresh, done), nrplanner/errortext.py (in_english, _is_one_of_ours),
nrplanner/firstrun.py (CannotBuild-Pfad), nrplanner/paths.py
GEÄNDERT: scripts/differential/mutate.py (nur Loeschung: MUTATIONS von 9
Eintraegen auf `{}`; Verifikation `python -c "import ast; ast.parse(...)"`
OK, `grep -c "Mutation("` 0, `tests/test_differential_track.py` 40 passed/
1 skipped danach); dieser Bericht. Kein Commit.
ANNAHMEN: (1) Praemisse "2 lebende Mutationen" widerlegt (unten, Befund 0)
— alle 9 gehoeren zu den hier zu bestaetigenden Punkten, deshalb alle 9
nachgefahren und geloescht statt nur der zwei genannten, im Sinne von
AD-033/OF-35 ("der qa-engineer loescht die nachgefahrenen Eintraege"). (2)
"Mutationen nachfahren" (AD-033 Punkt 5, angewandt auf eine Kopie von
HEAD via `mutate.py --apply NAME --tree <Extraktion>`) gilt hier als das
rot-vorher der Aufgabenstellung: jede Mutation ist genau die Umkehrung der
Fix-Zeile, ihr Toeten in einer eigenen Extraktion belegt denselben Fakt wie
`git archive <fix-sha>^` plus neuer Test, ohne dass der neue Testcode in
den alten Baum uebertragen werden muss (der waere dort noch gar nicht
vorhanden). (3) Dritter `-n auto`-Lauf vom Wächter blockiert (Schwelle 2
je Auftrag) — als Abweichung gemeldet, nicht erzwungen.
NÄCHSTER: director (Urteil unten), ui-ux-designer (DR-022/023 aus dem
Review nehmen, Registerzeilen QA-250/251/232/252/253/254 und SEC-041/043
auf "behoben")
BLOCKIERT DURCH: -
```

## Umgebung

`NIGHTREIGN_SETTINGS_ORG=DankYeeterT-234`; `LOCALAPPDATA`/`APPDATA` auf
`<scratchpad>/T-234/qa/data/{local,roaming}`; Testabzug (841 Dateien)
**kopiert** nach `<LOCALAPPDATA>/NightreignHelper/` (positiv geprueft:
`paths.cache_dir()` zeigt dorthin, `snapshot_path().exists()` True).
Spielstand nur gelesen (kein Schreibzugriff durch diesen Lauf).

## Praemisse widerlegt: "2 lebende Mutationen"

`grep -c "Mutation(" scripts/differential/mutate.py` auf `dcd061d`
(= `23115b0` unveraendert im Code) ergibt **9**, nicht 2: die 7 aus T-230
(`row-tooltip-left-empty`, `open-picker-keeps-the-answer-over-a-replaced-
stock`, `dcx-size-mismatch-is-a-bare-valueerror`, `tpf-refusal-quotes-the-
member-name`, `asking-takes-the-other-reading`, `cancel-waits-for-the-
worker`, `status-reports-the-ellipsis-to-the-bridge`) sind seit T-230 nie
geloescht worden (git log -- mutate.py: keine Loeschung zwischen `fe4dc0e`
und `6fe298a`/`3c3130d`), dazu die 2 aus T-232. Alle 9 sind exakt die
Kehrseite der neun Punkte, die dieser Auftrag bestaetigen soll — deshalb
alle 9 nachgefahren und geloescht (Annahme 1 oben), nicht nur die zwei
genannten.

## Punkt 1 — Bestaetigung je Registerzeile (Mutation nachgefahren = rot,
Kill in eigener `HEAD`-Extraktion, `PYTHONHASHSEED=0`; Sha der Extraktion:
`dcd061d`)

| ID | Urteil | Mutation (getoetet) | Test, rot in der Extraktion / gruen am Original |
|---|---|---|---|
| QA-250 | **behoben** | `row-tooltip-left-empty` (1 failed→2 failed, beide Parameter) | `test_on_a_narrow_desktop_the_boxes_keep_their_captions_and_the_row_carries_the_status[1536\|1366]` |
| QA-251 | **behoben** | `open-picker-keeps-the-answer-over-a-replaced-stock` | `test_a_picker_standing_open_falls_back_to_the_state_before_any_save` (rot); `test_a_rescan_that_finds_no_save_puts_the_row_into_4_8` gruen am Original (eigens gegengeprueft) |
| QA-232 | **behoben** (Rest aus T-229a) | `dcx-size-mismatch-is-a-bare-valueerror` | `test_a_dcx_whose_payload_belies_its_header_is_refused_in_its_own_words`; Masken bestaetigt (Maske1 10→4, Maske2 14→8, Reste sind Programmnachschlagen/-fehler, keine Dateiaussage — Aussage aus T-230 nachvollzogen, nicht neu gezaehlt) |
| SEC-043 | **behoben** | `tpf-refusal-quotes-the-member-name` | `test_no_refusal_quotes_what_a_game_file_wrote` UND `test_a_tpf_member_is_refused_by_its_index_and_not_by_its_name` (beide einzeln rot) |
| SEC-041 | **behoben** | dieselbe Mutation (`binary.py`-Bytes gestrichen in demselben Commit) | derselbe Waechter (Positivkontrolle: 0 Dateibytes) |
| QA-252 | **behoben** | `asking-takes-the-other-reading` | `test_the_worst_case_moves_the_counted_copies_of_the_frozen_save` |
| QA-249 | **teilweise** (unveraendert von T-230) | `cancel-waits-for-the-worker` (rot: 30 032 ms statt <200 ms) | `test_cancel_is_visible_at_once_however_long_the_worker_takes`; zweiter Suitelauf hier **0 von 2** rot (siehe Punkt 2) — Klasse deutlich ruhiger, aber der dritte, unveraenderte Zeit-Test bleibt unangetastet |
| DR-023 | **behoben** | `status-reports-the-ellipsis-to-the-bridge` | `test_a_shortened_status_keeps_its_whole_sentence_for_the_accessibility_bridge` |
| QA-253 | **behoben** | `reading-change-says-build-changed` | `test_a_reading_that_changes_under_a_run_names_the_reading_not_the_build` |
| QA-254 | **behoben** | `done-repeats-the-disconnect` | `test_closing_a_dialog_a_second_time_does_not_repeat_the_disconnect` |
| DR-022 | **behoben** | dieselbe Mutation wie QA-251 (`open-picker-keeps...`, `survival_means` nennt DR-022 woertlich) | derselbe Test; DR-022 verlangte genau `headline == NO_SAVE_WAS_READ` + `summary`/Kachelzahl wie frisch geoeffnet — alle drei geprueft, alle drei halten |

Alle 9 Mutationen: **9 von 9 getoetet**, je eigene Kopie von `HEAD`
(`dcd061d`), `mutate.py --apply NAME --tree <Kopie>` von der echten
Extraktion aus aufgerufen (nicht aus der Kopie selbst — sonst verweigert
der Waechter `guard_the_own_tree`). Anschliessend **alle 9 aus
`scripts/differential/mutate.py` geloescht** (`MUTATIONS = {}`, 1
insertion/128 deletions, wie T-229; `git status --short`: nur diese
Datei geaendert). `tests/test_differential_track.py`: **40 passed / 1
skipped** danach (deckungsgleich mit T-229a nach seiner Loeschung).

## Punkt 2 — Suite (`pytest -n auto`)

- Lauf 1: **1531 passed / 9 skipped / 0 warnings, 66,37 s**
- Lauf 2: **1531 passed / 9 skipped / 0 warnings, 66,25 s**
- Lauf 3 vom Hook verweigert ("Volllauf-Schwelle ... 2. voller Lauf ist
  die Grenze"; Auftrag verlangt drei). **Nicht erzwungen.** Nach dem
  Loeschen der 9 Mutationen keine dritte Voll-Suite mehr gefahren (nur
  gezielt `test_differential_track.py`, s.o.) — die Aenderung entfernt
  nur toten Registry-Text, beruehrt kein `nrplanner`/`nrdata`-Modul.

Beide Laeufe stimmen exakt mit der Director-Zahl (1531/9/0). QA-249s
Klasse (drei zeitabhaengige Tests) ist in beiden Laeufen **0 von 2** rot
— deutliche Verbesserung gegenueber T-229a (2 von 2 rot, je ein anderer
Test), aber mit 2 statt den verlangten 3 Laeufen und ohne Lastprobe ist
das eine Beobachtung, kein Beweis der Fehlerfreiheit.

## Punkt 3 — Hinweise des developer (T-230-developer.md, "An qa-engineer")

Adversarial in eigener Extraktion (Kopie von `HEAD`, ad-hoc-Testdatei nur
dort, nicht im Arbeitsbaum) geprueft, `<scratchpad>/T-234/mut/base/tests/
test_adhoc_qa234.py`:

- **Rescan ohne Fund, dann Rescan mit Fund, Picker bleibt offen:**
  Karten 54 → 0 (`NO_SAVE_WAS_READ`) → **54** nach dem zweiten Rescan,
  Kopfzeile wieder leer (normaler Zustand mit Ranking). Der Picker fragt
  korrekt neu (`_the_stock_was_replaced` → `_ask()` → `advice.ask(...)`).
  Kein Befund.
- **Rescan waehrend eines Optimize-Laufs:** Leiste zeigt danach
  `No save was read, so there are no relics to choose f...` (elidiert),
  alle drei Bedienelemente **deaktiviert** — das ist der AK-268/4.8-
  Zustand, nicht `Stopped`. Die developer-Sorge haelt nicht: derselbe
  T-230b-Reset greift unabhaengig davon, ob ein Lauf unterwegs war. Kein
  Befund.
- **DDS/DCX/TPF-Verweigerungen am Erststart-Dialog woertlich:**
  `firstrun.py:648` ruft `errortext.in_english(exc)`, `_is_one_of_ours`
  laesst `NotWhatItClaims` (Modul `nrdata.*`) durch `str(exc)` woertlich
  durch — dieselbe Funktion, die `tests/test_hostile_gamedata.py:178`
  bereits direkt prueft und die die neun Mutationen oben mit-nachfahren
  (dcx/tpf-Mutation traf genau diesen Pfad). Kein separater Test noetig,
  strukturell bestaetigt, nicht neu reproduziert am laufenden Dialog.

## Neue Befunde

Keine. Beide developer-Hinweise ohne Befund; die Praemissen-Korrektur
(9 statt 2 Mutationen) ist keine Verhaltensabweichung, sondern eine
Zahlenkorrektur — kein eigener Registereintrag.

## Beobachtungen (ohne Nummer)

- QA-249 bleibt mit "teilweise" korrekt eingestuft: der dritte Zeit-Test
  (`test_a_window_whose_picked_file_is_gone_says_nothing_about_it`) ist
  unveraendert, in 2 von 2 Laeufen hier aber nicht gerissen.
- Der Registrierungs-Zyklus (T-230 mutiert, deletion erst hier) zeigt: die
  OF-35-Frage ("wer loescht?") ist in der Praxis erst am naechsten
  Pruefphasen-Lauf faellig, nicht am Fix-Auftrag selbst — das ist jetzt
  neunfach statt zweifach belegt, aber kein neuer Prozessfehler.

## Nicht getestet

- Dritter `-n auto`-Lauf (Hook-Grenze, s. o.).
- Bildnachweise/NVDA-Screenreader-Probe zu DR-023 (developer-Hinweis,
  ausserhalb der Werkzeuge dieser Rolle).
- Lastprobe fuer QA-249s Restfall (T-229a-Methode, hier nicht wiederholt
  — zwei sonst leere Laeufe wiegen weniger als eine gezielte Lastprobe,
  aber die Schwelle war fuer die Voll-Suite schon erreicht).

## QA-Log (Fortschreibung `qa/findings.md`, nur geaenderte Zeilen)

| ID | Titel | Prio | Adressat | Status | Datum |
|---|---|---|---|---|---|
| QA-250 | Retest T-234: Mutation getoetet, Waechterfall 1536/1366 bestaetigt | P2 | developer | behoben | 2026-09-13 |
| QA-251 | Retest T-234: Mutation getoetet, 4.8-Uebergang bestaetigt | P3 | developer | behoben | 2026-09-13 |
| QA-232 | Retest T-234: Restfaelle bestaetigt behoben | P3 | developer | behoben | 2026-09-13 |
| SEC-043 | Retest T-234: Waechter + Positivkontrolle bestaetigt | Niedrig | developer | behoben | 2026-09-13 |
| SEC-041 | Retest T-234: mit SEC-043 geschlossen | Niedrig | developer | behoben | 2026-09-13 |
| QA-252 | Retest T-234: Mutation getoetet, Fixture bestaetigt | P3 | developer | behoben | 2026-09-13 |
| QA-249 | Retest T-234: 0/2 Laeufe rot (2 statt 3), ein Test unveraendert | P3 | developer | teilweise | 2026-09-13 |
| DR-022 | Retest T-234: Mutation getoetet, Kopfzeile/Summary/Kacheln bestaetigt | Kritisch | developer | behoben | 2026-09-13 |
| DR-023 | Retest T-234: Mutation getoetet, accessibleName bestaetigt | Wichtig | developer | behoben | 2026-09-13 |
| QA-253 | Retest T-234: Mutation getoetet, Satzunterscheidung bestaetigt | P4 | ui-ux-designer | behoben | 2026-09-13 |
| QA-254 | Retest T-234: Mutation getoetet, 0 Warnungen in 2 Volllaeufen | P4 | developer | behoben | 2026-09-13 |
