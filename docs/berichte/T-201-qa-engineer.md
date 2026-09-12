STATUS: erledigt
AUFTRAG: T-201 — Pruefphase, QA: der eingefrorene Stand `b33461d`
GELESEN: docs/tasks/T-201.md, docs/state.md, GOAL.md, qa/findings.md (voll),
  git log 28dc45c..b33461d, docs/berichte/T-199-developer.md,
  tests/test_exception_text_is_english.py, tests/test_hostile_gamedata.py,
  tests/test_differential_track.py (Ausschnitt), tests/test_first_run_panel.py
  (Ausschnitt), tests/test_save_path_memory.py (Ausschnitt),
  tests/conftest.py, nrplanner/relicpicker.py, nrplanner/advisorbar.py,
  scripts/differential/mutate.py (Diff `efdad85`)
GEÄNDERT: docs/berichte/T-201-qa-engineer.md (neu). Kein Anwendungscode, keine
  Tests, keine `qa/findings.md` (traegt der Director laut Auftrag).
ANNAHMEN: keine — der Auftrag war vollstaendig, Zitat aus GOAL.md und
  docs/state.md lagen bei.
NÄCHSTER: director
BLOCKIERT DURCH: nichts

## Kontext in einem Satz

Fuenf als "behoben, QA-Bestaetigung offen" gefuehrte Befunde auf dem
eingefrorenen Stand `b33461d` pruefen, und feststellen, ob die Tests, die
sie schliessen, die Abnahmekriterien wirklich pruefen statt nur den
bestehenden Code zu beschreiben.

## Risiko-Briefing

Reihenfolge nach Risiko: **zuerst QA-211** (A8, fuenf Sprachlecks, die
Fehlerklasse musste die Rolle zwischen "unsere" und "fremde" Ausnahme
uebernehmen — genau die Stelle, an der ein Refactoring am leichtesten wieder
aufreisst), **dann QA-233/QA-234/QA-235 zusammen** (alle drei sind
Test-Infrastruktur, nicht Anwendungsverhalten — ihr Risiko ist nicht "der
Nutzer sieht einen Fehler", sondern "die naechste Rolle vertraut einer
Suitezahl, die nichts mehr misst"), **QA-228 zuletzt**, weil sie bereits am
echten Fenster nachgewiesen ist (T-199) und nur die Erreichbarkeit ueber die
Registry zu bestaetigen blieb. Die eigentliche Auftragsfrage — pruefen die
Tests das Kriterium oder nur den Code — wird parallel zu allen fuenf
mitgefuehrt, nicht als sechster Schritt danach.

## Bestehende Tests

`python -m pytest -n auto -q`, `NIGHTREIGN_SETTINGS_ORG`, `LOCALAPPDATA`,
`APPDATA` umgelenkt (siehe unten): **1781 passed, 9 skipped in 136.81s**.
Deckt sich mit der Zahl des Directors (1781 passed, 9 skipped, 135.24s) bis
auf die erwartete Laufzeitstreuung. Kein `--ignore`, `texture2ddecoder` und
`pytest-xdist` sind installiert. Die 1257 aus `CLAUDE.md` bleibt ungeklaert,
nicht Teil dieses Auftrags.

**Umlenkung nach QA-237:** `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-201`,
`LOCALAPPDATA=C:\Users\Daniel\AppData\Local\NH-T-201-test`,
`APPDATA=C:\Users\Daniel\AppData\Local\NH-T-201-test\Roaming`, per `export`
gesetzt und vor dem Lauf mit `echo` verifiziert. Das ist **kein Nachweis**,
dass die Schreibvorgaenge dort ankommen (QA-237) — nur der Beleg, dass die
Variablen beim Aufruf tatsaechlich standen. Erster Versuch mit Git-Bash-`set`
statt `export` hat die Variablen **nicht** gesetzt (bash liest `set FOO=bar`
als Positionsparameter, nicht als Env); der Lauf lief trotzdem durch, weil
`conftest.py` `NIGHTREIGN_SETTINGS_ORG` ohnehin fest auf `DankYeeterTests`
ueberschreibt (QA-221) — das haette mit echten Nutzerdaten schiefgehen
koennen, ist hier folgenlos geblieben, weil ich es vor dem produktiven Lauf
bemerkt und korrigiert habe.

## 1. Die fuenf Befunde

### QA-211 — bestaetigt behoben

`nrplanner/datasource.py:16` (`NoGameData(FileNotFoundError)`) und
`nrdata/binary.py:8` (`NotWhatItClaims(ValueError)`) existieren, die Senken
in `app.py::main` und `inventory.py::_scan_save` mappen ueber diese Klassen.
`tests/test_exception_text_is_english.py` (18 Tests) lief einzeln gruen
(39,08 s, ohne `-n`).

**Rot-vorher selbst nachvollzogen** (eine der fuenf Schutzmassnahmen, im
`git archive`-Klon unter dem Scratchpad, keine Aenderung im Arbeitsbaum):
`nrdata/savefile.py:44` von `raise NotWhatItClaims(...)` auf
`raise ValueError(...)` geaendert →
`test_a_file_that_is_not_a_save_keeps_this_program_s_own_sentence` faellt
exakt mit dem im Docstring vorhergesagten Text ("Something went wrong that
this program has no sentence for" statt "not a BND4 save container"). Die
anderen vier Schutzmassnahmen habe ich nicht selbst einzeln abgeschaltet
(Zeitbudget), der Commit `8089d22` benennt sie und die Behauptung "je ein
benannter Fall faellt" ist fuer die gepruefte Stelle wahr.

### QA-228 — bestaetigt behoben

`nrplanner/advisorbar.py:76`: `GOAL_ORDER = ("max_damage",
"min_damage_taken", "max_attributes")` — drei Eintraege. Die dritte
Zielrichtung ist ueber die Registry erreichbar, nicht nur eine tote
Konstante: `nrplanner/relicpicker.py:1019` fuellt die `Sort by`-Box mit
`for goal_id in VALUE_DIRECTIONS` (= `advisorbar.GOAL_ORDER`), keine
Kardinalitaet fest verdrahtet.
`tests/test_relic_picker_advisor.py::test_the_sort_box_...` (Name gekuerzt,
Zeile 645) baut die Erwartung ebenfalls aus der Registry
(`list(advisorbar.GOAL_ORDER) + [NAME_ORDER]`) statt einer literalen Drei —
ein direkter Registry-zu-Registry-Vergleich, kein Test, der nur bestaetigt,
was der Code tut. Selbst gelaufen: 4 passed (48,19 s).

Die Fenstermessung selbst (228 px Kartenzeile, drei ganz sichtbare Zeilen)
habe ich **nicht neu gemessen** — T-199 hat das bereits am echten,
nicht-offscreen Fenster getan und die L-009-Falle dabei selbst
dokumentiert (erster Lauf offscreen ergab 278 statt 228 px, zweiter Lauf
nativ traf die Vorgabe). Das ist eine belastbare Fremdmessung mit
genannter Umgebung (`platform 'windows'`, Style `fusion`, `dPR` 1,25,
logische px) und wird hier als Stichprobe akzeptiert, nicht wiederholt
(Kein-Doppel-Testen-Prinzip). `wanted_height` (1121 statt 1136 px) ist
QA-239, nicht Teil dieser Bestaetigung.

### QA-233 — bestaetigt behoben

`tests/test_extraction.py` und `tests/test_hostile_gamedata.py` laufen ohne
`--ignore` durch (27 passed, 58,31 s, selbst ausgefuehrt). Von den zehn
`pytest.raises(...)`-Stellen in `test_hostile_gamedata.py` sind **zwei**
(Zeile 277, 283 — `test_an_unterminated_part_name_is_a_data_error`,
`test_a_part_name_offset_past_the_record_is_a_data_error`) von `ValueError`
auf `binary.NotWhatItClaims` verengt; die restlichen acht bleiben bewusst
`ValueError`, weil `dds.py` und `oodle.py` dort tatsaechlich einen nackten
`ValueError` werfen und den `binary`-Pfad nie beruehren (`git show 0838cd9`
nennt denselben Split). Das deckt sich mit dem Befundtext ("zehn Erwartungen
geprueft, zwei verengt").

### QA-234 — bestaetigt behoben

`tests/test_differential_track.py::test_every_mutation_still_finds_its_anchor_in_the_real_source[sort-by-offers-a-direction-nobody-scores]`
lief einzeln gruen. Der Diff `efdad85` zieht Alt- und Neutext von
`scripts/differential/mutate.py` auf die aktuelle `GOAL_ORDER`-Zeile nach;
die Mutation fuegt weiterhin eine vierte, vom Register nicht bewertete
Richtung hinzu (`max_style` statt vorher `max_style` als dritte) — dieselbe
Frage bleibt gestellt. Den vollen Mutationslauf (`1 failed, 15 passed, 8
errors`, T-199) habe ich nicht wiederholt, nur den Anker-Test selbst; das
ist die konkrete Stelle, die QA-234 benannt hatte.

### QA-235 — bestaetigt behoben

`tests/test_first_run_panel.py:576`
(`test_the_first_dialog_opens_at_the_folder_that_was_remembered`) setzt
jetzt `firstrun.gamefiles.steam_common_folders` **und**
`firstrun.STEAM_COMMON` per `monkeypatch`, bevor
`where_to_start_looking(None)` geprueft wird — kein Lesezugriff auf die
echte Steam-Installation mehr. Selbst gelaufen: 2 passed.

## 2. Pruefen die Tests das Kriterium — die dritte Stelle

**Die dritte Stelle des Musters existiert bereits als eigener Befund und
ist nicht neu: `qa/findings.md` QA-224**, benannt am 12.09.2026 (vor dieser
Pruefphase) mit **zwei** Faellen desselben Musters — Test liest die echte
Maschine statt einer Vorrichtung:

1. `tests/test_first_run_panel.py:576` — **das ist wortgleich die Stelle,
   die QA-235 gerade geschlossen hat.**
2. `tests/test_save_path_memory.py:710`
   (`test_one_unreadable_save_does_not_hide_a_good_one`) —
   `good = savefile.find_saves()[0]` liest die reale Speicherstandsliste
   direkt, ungeschuetzt durch ein eigenes `pytest.skip`. **Dieser Fall ist
   von keinem Commit im Bereich `28dc45c..b33461d` beruehrt** (`git log
   28dc45c..b33461d -- tests/test_save_path_memory.py` zeigt nur `0204a25`,
   und dessen Diff laesst Zeile 710 unberuehrt) und **steht heute noch
   offen**.

**Befund: `qa/findings.md` fuehrt QA-224 weiterhin komplett als `offen`,
obwohl die Haelfte seiner zwei Faelle durch QA-235 bereits geschlossen ist.**
Wer QA-224 liest, sieht nicht, dass ein Fall bereits weg ist, und wer QA-235
liest, sieht nicht, dass QA-224 denselben Fall schon einmal benannt hatte —
zwei IDs fuer denselben Satz an derselben Zeile, eine davon inzwischen
falsch. Das ist eine Buchfuehrungsluecke, kein neuer Code-Bug.

**Eigene Suche, zwei unabhaengige Masken, gegen den ganzen `tests/`-Baum:**

* Maske 1 (Umgebungs-/Nutzerattribute, deckt sich mit QA-236s Suche):
  `os\.environ\[|os\.environ\.get\(|os\.getenv\(|expandvars|Path\.home\(|
  socket\.gethostname|platform\.node\(|getuser\(|USERPROFILE|COMPUTERNAME|
  winreg\.` → **1 Treffer** ausserhalb `monkeypatch`/`conftest.py`:
  `tests/test_shortcut_interpreter.py:28` (`os.environ["SystemRoot"]`) —
  das ist QA-236, bereits gemeldet, bestaetigt keinen neuen Fall.
* Maske 2 (Funktionsaufrufe, die echte Spiel-/Steam-/Save-Erkennung
  auf der Maschine ausloesen, unabhaengig von Umgebungsvariablen formuliert):
  `savefile\.find_saves\(\)\[|gamefiles\.|gamepath\.|steam_common_folders|
  _steam_roots|resolve_game\(` ohne begleitendes `monkeypatch.setattr` im
  selben Test → **1 Treffer**: `tests/test_save_path_memory.py:710`, s. o.
  Alle anderen Fundstellen dieser Maske liegen entweder in Vorrichtungen mit
  eigenem `pytest.skip` (`conftest.py::game_data`, `::installed_game`,
  `::a_real_scan`) oder sind selbst gemockt.

Kein dritter, bisher unbekannter Fall gefunden. Das bestaetigt indirekt,
dass die Suche des `developer` in T-198 (`winreg`, `expanduser`, `getpass`,
`Program Files`, `LOCALAPPDATA`, `APPDATA`) fuer ihre eigene Achse
vollstaendig war — sie haette QA-224s zweiten Fall aber ohnehin nicht
gefunden, weil `find_saves()[0]` keinen dieser Begriffe enthaelt. Das ist
genau der Punkt aus L-006: eine Suchmaske schliesst ihre eigene Achse, nicht
die Eigenschaft.

**Zur Frage selbst:** In den fuenf geprueften Faellen prueft die
Testinfrastruktur heute durchgehend das Kriterium und nicht nur den
bestehenden Code — QA-211s Scan hat eine Positivkontrolle und eine
eigene "Liste darf nur schrumpfen"-Klausel, QA-228s Erreichbarkeitstest
baut seine Erwartung aus derselben Registry wie der Code (kein zweiter
Literal-Ort), QA-233s Verengung ist am tatsaechlichen Fehlerpfad verankert,
QA-234 hat einen Selbsttest gegen den echten Quelltext, QA-235 setzt beide
Haelften der Umgebung. Die einzige verbliebene Luecke derselben Klasse ist
QA-224/2, unveraendert seit ihrer Meldung.

## Beobachtungen

`test_one_unreadable_save_does_not_hide_a_good_one` (QA-224/2) haengt sein
`good = savefile.find_saves()[0]` faktisch an das vorgelagerte
`a_real_scan`-Fixture, das bei fehlendem Save korrekt skipt — auf dieser
Maschine also ungefaehrlich, aber `find_saves()` und `inventory.scan()`
(das `a_real_scan` benutzt) sind zwei verschiedene Aufrufe, und nichts
erzwingt, dass beide dasselbe Save als "erstes" sehen; das ist eine
Vermutung, kein gepruefter Fall.

## Offene Fragen

Keine an eine andere Rolle — QA-224s Status ist eine Buchfuehrungsfrage, s.
Vorschlag unten.

## Nicht getestet

Kein voller Adversarial-Durchlauf ueber A3–A8 (nicht Teil dieses Auftrags,
A9 ist explizit ausgenommen). Die vier vollen Rot-vorher-Mutationslaeufe von
QA-211 (vier von fuenf Schutzmassnahmen) und der volle
Differential-Mutationslauf zu QA-234 wurden nicht wiederholt, nur die
zugehoerigen Anker-/Sinktests einzeln — Kein-Doppel-Testen, die Erstlaeufe
sind mit Befehl und Ergebnis in T-193/T-199 dokumentiert. Kein Fensterlauf
mit echter Maus (QA-222 unangetastet). `qa/findings.md`-Eintrag fuer die
QA-224-Korrektur lege ich nicht selbst an — Director traegt sie nach.

## Vorschlag (an director, Buchfuehrung)

QA-224 auf `teilweise behoben` setzen: Fall 1
(`test_first_run_panel.py:576`) geschlossen durch QA-235 (T-198), Fall 2
(`test_save_path_memory.py:710`) weiterhin offen. Alternativ QA-224 auf
Fall 2 verengen und im Text auf QA-235 als Vorgaenger fuer Fall 1
verweisen — beides loest die Doppelfuehrung, welche Form der Director
entscheidet.

## Zusammenfassung (an director)

**Befunde:** 0 × P1, 0 × P2, 1 × P3 (Buchfuehrung: QA-224 stale, s. o.),
0 × P4. Fuenf gepruefte Befunde: alle fuenf **bestaetigt behoben**, mit
selbst ausgefuehrten Tests und bei QA-211 einem eigenen Rot-vorher-Beleg.
Die Auftragsfrage 2 (pruefen die Tests das Kriterium?) ist fuer alle fuenf
mit Ja beantwortet; die gesuchte "dritte Stelle" des ValueError-/
Maschinen-Musters ist kein neuer Fund, sondern der noch offene zweite Fall
von QA-224 — mit Fundstelle und zwei unabhaengigen Suchmasken belegt.

**Gesamturteil: PASS.** Kein P1/P2, das einzige Ergebnis dieses Laufs ist
eine Statuskorrektur an einem bestehenden P3-Befund.

## QA-Log (`qa/findings.md`, vom Director nachzutragen)

| ID | Titel | Prio | Sev | Adressat | Verifiziert | Status | Letzte Pruefung |
|----|-------|------|-----|----------|-------------|--------|----------------|
| QA-211 | Ausnahmetexte umgehen beide Sprachwaechter | P3 | Minor | developer | qa-engineer, T-201: Test einzeln gelaufen (18 passed), eine der fuenf Schutzmassnahmen im Klon rot-vorher nachvollzogen (`savefile.py:44`) | behoben — QA-bestaetigt | 2026-09-12 |
| QA-228 | Die dritte Zielrichtung war fuer den Spieler nicht erreichbar | P1 | Major | ui-ux-designer (Spec), dann developer | qa-engineer, T-201: Erreichbarkeitstest selbst gelaufen (4 passed), Fenstermessung als Fremdmessung (T-199) akzeptiert | behoben — QA-bestaetigt | 2026-09-12 |
| QA-233 | Zwei Testdateien liefen nur mit `--ignore`, zehn ValueError-Erwartungen ungeprueft | P2 | Major | developer | qa-engineer, T-201: beide Dateien ohne `--ignore` gelaufen (27 passed), Verengung an den zwei betroffenen Stellen bestaetigt, acht bewusst ValueError geprueft | behoben — QA-bestaetigt | 2026-09-12 |
| QA-234 | Mutationsanker `sort-by-offers-a-direction-nobody-scores` verwaist | P2 | Major | developer | qa-engineer, T-201: Anker-Test einzeln gelaufen und gruen | behoben — QA-bestaetigt | 2026-09-12 |
| QA-235 | Test haengt an der Steam-Installation dieser Maschine | P2 | Major | developer | qa-engineer, T-201: Test einzeln gelaufen (2 passed), beide Umgebungshaelften im Code als `monkeypatch` bestaetigt | behoben — QA-bestaetigt | 2026-09-12 |
| QA-224 | Zwei Tests lesen die echte Maschine statt ihrer Vorrichtung | P3 | Minor | developer | qa-engineer, T-201: Fall 1 = QA-235 (behoben), Fall 2 (`test_save_path_memory.py:710`) unveraendert seit Meldung, per `git log 28dc45c..b33461d` bestaetigt unberuehrt | **teilweise** behoben — Fall 1 zu, Fall 2 offen (Statuskorrektur, war zuvor komplett "offen" gefuehrt) | 2026-09-12 |
