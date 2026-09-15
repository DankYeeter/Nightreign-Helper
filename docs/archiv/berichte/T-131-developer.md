# T-131 — U6: die Waechter der Picker-Spur (developer)

```
STATUS: erledigt
AUFTRAG: T-131 — U6: die sieben Waechter der Picker-Spur
GELESEN: docs/tasks/T-131.md · ARCHITECTURE.md AD-028 (3985-4200, W1 bis W3
  im Wortlaut) und Nachtrag IX-4 (4749-4816, W3 neu, W4, W5) · UI_SPEC.md
  Abschnitt T-127 ab 6444 samt Streichliste und AK-211 bis AK-219
  (6839-6960) · docs/berichte/T-130-developer.md ganz · Quellstand:
  nrplanner/advisor/{worker,run,types,goals}.py, nrplanner/{relicpicker,
  advisorbar,app}.py, tests/{conftest,advisor_cases,test_one_build,
  test_advisor_worker,test_relic_picker_advisor}.py,
  scripts/differential/mutate.py (nur gelesen, siehe „Parallellauf")
GEÄNDERT: tests/picker_track.py (neu) · tests/test_picker_track_guards.py
  (neu) — beide in Commit `05e923f`. Dieser Bericht. Sonst nichts;
  insbesondere **nicht** scripts/differential/mutate.py.
ANNAHMEN: zwei, unten unter „Annahmen" begruendet
NÄCHSTER: director (Registrierung der neun Mutationen ist T-132)
BLOCKIERT DURCH: nichts
```

## Umgesetzt

**Commit `05e923f`** auf `docs/audit-and-advisor-design`, Basis `f98ba9c`.
Zwei Dateien, beide unter `tests/`, **kein Anwendungscode**.

| Datei | was |
|---|---|
| `tests/picker_track.py` | Vorrichtungen: `StatedAnswers` (die Antwortfunktion, die eine Spur bei der Konstruktion bekommt — hält die Antwort auf Wunsch im Thread fest), `Outcomes` (alle drei Ausgangssignale in **einer** Liste), `a_track`, `pool_for`, `picker_over`, `CountingPicker`, `spin`/`settle`. Kein Testmodul. |
| `tests/test_picker_track_guards.py` | die sieben Waechter, 15 Faelle |

**Alle Waechter fahren ueber den echten `AdvisorController` und die echte
`SlotAdvice`.** Gestellt wird die **Antwortfunktion** (AD-028 Option D), nicht
die Advice: die vorhandenen Picker-Faelle stellen ihre Rangfolge ueber
`FakeAdvice`, was fuer Faelle ueber das *Gezeichnete* richtig ist und fuer
diese Waechter falsch waere — der Generationszaehler, der Cache-Treffer im
selben Aufruf und der eine Ausgang einer Frage liegen genau in dem Stueck, das
`FakeAdvice` ersetzt.

**Keine Zeitschranke.** Wo eine Ereignisschleife gedreht wird, wird sie
gedreht, **bis ein Zustand eintritt**; der mitgegebene Zeitwert ist eine
Sicherung gegen ein Haengen, und kein Fall behauptet etwas ueber Dauer.

| Waechter | Fall(e) | woran er sich festmacht |
|---|---|---|
| **W1** | `test_w1_nothing_but_the_named_places_reaches_the_calculation` (3 Parameter) · `test_w1_the_picker_holds_none_of_the_three` | AST-Zaehlung von `test_one_build.call_sites` ueber **alle** Module unter `nrplanner/`; die Erwartung ist eine Tabelle im Test |
| **W2** | `test_w2_the_first_paint_is_an_empty_grid_that_says_so` | AK-212 vollstaendig, an einer Spur, die nachweislich **rechnet** (gewartet wird, bis die Antwortfunktion betreten ist) |
| **W3** | `test_w3_the_answer_of_a_closed_opening_never_fills_the_next_one` · `test_w3_an_answer_arriving_after_the_close_touches_nothing` | zwei Oeffnungen zweier Slots an **einer** Spur; `pool.slot_index` der zweiten Anzeige |
| **W4** | `test_w4_every_direction_the_picker_draws_is_one_the_pool_scores` | `advisorbar.GOAL_ORDER` ⊆ `goals.GOALS`, ohne Fenster |
| **W5** | `test_w5_a_known_answer_is_one_build_of_the_grid_and_never_pending` | Zaehler der Rasterbauten (1 bei Treffer, 2 ohne) plus „kein `…` im Rollbereich" |
| **W6** | `test_w6_a_question_ends_in_exactly_one_of_the_three` (5 Parameter) | eine Liste fuer alle drei Signale; die Behauptung ist ihre **Summe** |
| **W7** | `test_w7_an_answer_that_stamps_nothing_still_arrives_stamped` | eine Antwortfunktion, die absichtlich **nicht** stempelt; der Fall prueft das erst und behauptet dann |

### Die beiden Abweichungen, die der Auftrag entschieden hat

- **W2 nimmt seine Form aus AK-212**, nicht aus *„jede Karte traegt
  `PENDING`"*. Umgesetzt: der Waechter prueft, dass **kein** Kartenwidget im
  Rollbereich steht, und nicht, was auf einer stehenden Karte steht.
- **W5s PENDING-Satz** ist als *Abwesenheit* gebaut (AK-219): im Rollbereich
  der Cache-Treffer-Oeffnung steht zu keinem Zeitpunkt `…`. Die Zaehlung —
  ein Bau gegen zwei — haelt und ist der Kern des Falls.

## Belege

### Suite

```
pytest -n auto   ->   1323 passed, 9 skipped, 0 failed   (176,47 s)
```

Gegen die Vorgabe **1297 passed, 9 skipped, 0 failed**: **+26**. Davon sind
**15 meine und 11 nicht**, und das ist nachgemessen, nicht geschaetzt:

| Messung | Befehl | Ergebnis |
|---|---|---|
| Arbeitsbaum **ohne** meine zwei Dateien | `pytest --collect-only -q` (Dateien voruebergehend in den Scratchpad verschoben und zurueckgelegt) | **1317** |
| Arbeitsbaum **mit** ihnen | dasselbe | **1332** |
| frischer Klon auf `1a2cc5b` (T-130s Stand) | `git clone <lokales repo> …/klon`, `git checkout 1a2cc5b`, `--collect-only` | **1306** |
| derselbe Klon auf `f98ba9c` (HEAD) | dasselbe | **1306** |

1306 = T-130s 1297 passed + 9 skipped. **Mein Anteil ist exakt +15**
(1332 − 1317). Die **11** dazwischen stammen **nicht aus einem Commit** —
zwischen `1a2cc5b` und `f98ba9c` haben sich nur Dokumente geaendert
(`git diff --stat`: `docs/berichte/T-130-developer.md`, `docs/tasks/T-130.md`,
`qa/findings.md`) —, sondern aus dem **uncommitteten
`scripts/differential/mutate.py` des parallel laufenden T-132**: der Diff der
gesammelten Test-Ids nennt sie einzeln, elf neue Parameter von
`test_every_mutation_still_finds_its_anchor_in_the_real_source`
(`canonical-pool-order-names-no-goal`, `picker-refresh-never-waits`,
`picker-worker-does-not-stamp-the-generation`, `slot-pool-*` u. a.).

**Keiner meiner 15 Faelle wird uebersprungen** (Dateilauf:
`pytest tests/test_picker_track_guards.py -q` → `15 passed in 25,19 s`; im
vollen Lauf bleibt die Zahl der Skips unveraendert bei 9).

**Kosten:** 25 s im Dateilauf. Der `a_track_to_ask`-Fixture haengt bewusst an
`shared_planner` und nicht an `planner` — mit `planner` waren es 57 s, weil
jedes der vier Fenster rund 10 s Spielstandlesen kostet. Kein Fall schreibt an
das Fenster; sie oeffnen einen Dialog ueber einer **eigenen** Spur, lesen ihn
und schliessen ihn.

### L-008 — die toetende Mutation je Waechter

**Wo gemessen:** in einer **isolierten Kopie** des Arbeitsbaums
(`tar -cf - --exclude=.git … | tar -xf - -C …/T-131/mutant`), nicht im
Arbeitsbaum — T-132 arbeitet gleichzeitig in demselben Verzeichnis, und eine
Mutation an Ort und Stelle haette seinen Lauf getroffen. `PYTHONDONTWRITEBYTECODE=1`
gesetzt; nach jeder Mutation wird der Baum aus einer unberuehrten Kopie
wiederhergestellt (nie `git checkout`). Kopie vorher **gruen**: `15 passed`.
Jeder Anker matcht genau einmal (vom Treiber geprueft, sonst Abbruch).
Befehl je Mutation: `pytest tests/test_picker_track_guards.py -q`.

| # | Mutation (Datei, Stelle) | alt → neu | rote Ausgabe |
|---|---|---|---|
| 1 | `nrplanner/relicpicker.py`, `SlotAdvice.ask` | vor `window = self._slot.window()` eingesetzt: `from .advisor import candidates as advisor_candidates` + `pool = advisor_candidates.pool` | `2 failed, 13 passed` — `…[candidates-pool]`: `assert {'nrplanner/a...licpicker.py'} == {'nrplanner/advisor/run.py'}`; `test_w1_the_picker_holds_none_of_the_three`: `assert {…'candidates.pool': 1} == {…'candidates.pool': 0}` |
| 2 | `nrplanner/relicpicker.py`, `_refresh` | `waiting = self._waiting and self._wait_is_drawn` → `waiting = False` | `3 failed, 12 passed` — **W2**, `test_w3_the_answer_of_a_closed_opening_never_fills_the_next_one`, `test_w3_an_answer_arriving_after_the_close_touches_nothing`; W2: `assert [<RelicCard…>, …] == []`, `Left contains 54 more items` |
| 3 | `nrplanner/advisor/worker.py`, `_on_ready` | `if result.generation != self._generation: return` **entfernt** | `3 failed, 12 passed` — **W3 (erster Fall)**, dazu **W6** zweimal: `a question that ended by 'cancelled while it works' was answered with ['stopped', 'ready']` |
| 4 | `nrplanner/relicpicker.py`, `done` | `if self.advice is not None: self.advice.stop_listening()` **entfernt** | `2 failed, 13 passed` — **beide W3-Faelle**: `an answer that arrived after the close drew into the dialog` |
| 5 | `nrplanner/advisorbar.py` | `GOAL_ORDER = ("max_damage", "min_damage_taken")` → `(…, "max_style")` | `1 failed, 10 passed, 4 errors` — **W4**: `the picker and the Advisor bar offer ['max_style'], which the registry does not score`. Die vier Fehler sind die Fensterfaelle (`KeyError: 'max_style'` beim Bau der Advisor bar) — W4 selbst braucht kein Fenster und faellt auf seiner eigenen Zusicherung |
| 6 | `nrplanner/advisor/worker.py`, `ask_and_answer_if_known` | Cache-Nachsehen entfernt, `self._wait_for(question); return None` | `1 failed, 14 passed` — **W5**: `the answer was in the cache and the dialog waited for it anyway` |
| 7 | `nrplanner/advisor/worker.py`, `cancel` | `self.stopped.emit()` **entfernt** | `3 failed, 12 passed` — **W6** dreimal: `a question that ended by 'cancelled before it runs' was answered with []` … `assert [] == ['stopped']` |
| 8 | `nrplanner/advisor/worker.py`, `_Worker.work` | `self.failed.emit(str(exc) or exc.__class__.__name__)` → `pass` | `1 failed, 14 passed` — **W6**: `a question that ended by 'the answer raises' was answered with []`, `assert [] == ['failed']` |
| 9 | `nrplanner/advisor/worker.py`, `_Worker.work` | `self.ready.emit(dataclasses.replace(result, generation=self._question.request.generation))` → `self.ready.emit(result)` | `4 failed, 11 passed` — **W7**: `the first answer never reached the window ([])`; dazu W6 (`'the answer comes back'` → `[]`), W5 und W3 |

**Jeder der sieben Waechter hat mindestens eine Mutation, die ihn toetet.
Keine Mutation hat ueberlebt** — es gibt also keinen Befund nach L-008c.

**L-008a (rot im Standardlauf, nicht isoliert).** Zweifach belegt:
1. Keiner der 15 Faelle traegt einen Marker, keiner wird uebersprungen; im
   vollen `-n auto`-Lauf sind alle 15 **passed** (Skipzahl unveraendert 9).
2. Kreuzprobe mit dem vollen Standardlauf **in der mutierten Kopie**, Mutation
   9:
   ```
   pytest -n auto -q   ->   11 failed, 1301 passed, 14 skipped, 6 errors (265,85 s)
   ```
   darunter `test_picker_track_guards.py::test_w7_…`,
   `…::test_w6_…[the answer comes back]`, `…::test_w5_…`, `…::test_w3_…`.
   *(Die 14 statt 9 Skips und der Fehlschlag von
   `test_release_spec_datas.py` sind Eigenschaften der `tar`-Kopie — sie
   enthaelt `NightreignHelper.spec` und `vendor/` nicht —, nicht der
   Mutation. `test_differential_track.py::…[picker-worker-does-not-stamp-the-generation]`
   faellt in einem mutierten Baum von Natur aus und zaehlt nicht als Kill.)*

**L-008b (die Erwartung kommt nicht aus der bewachten Stelle).** Je Waechter:

- **W1:** die erlaubten Stellen stehen als Tabelle im Test, nicht als das, was
  `relicpicker.py` gerade sagt.
- **W2:** die Wortlaute stehen als **Literale aus `UI_SPEC` §7** im Test
  (`"Your relics appear here."`, `"Working out what each relic is worth with
  <slot> empty"`, der AK-201-Satz), nicht als `relicpicker.NOTHING_YET` &c.
- **W3:** die Erwartung ist der `slot_index` des Slots, der **gefragt** hat —
  eine Eigenschaft der Frage, nicht der Anzeige.
- **W4:** die Erwartung ist die Relation zweier Dateien; keine Seite ist die
  Quelle der anderen.
- **W5:** gezaehlt wird der Bau des Rasters (1 gegen 2); die Gegenprobe im
  selben Fall verhindert, dass ein Raster gruen ist, das **nie** neu gebaut
  wird.
- **W6:** erwartet wird der Name des Ausgangs, in der Tabelle
  `WAYS_A_QUESTION_ENDS` geschrieben.
- **W7:** der Fall prueft **zuerst**, dass die Antwortfunktion tatsaechlich
  `generation == 0` zurueckgibt (`assert [pool.generation for pool in
  handed_back] == [0, 0]`), und behauptet erst danach etwas ueber das
  Zugestellte. Eine Vorrichtung, die selbst stempelte, waere hier laut.

**Rot-vorher, je Schutzmassnahme einzeln (L-007).** Der Fix aus T-130 hat
**zwei** Vorrichtungen gegen eine ueberholte Antwort, und beide sind einzeln
ausgebaut worden: Mutation 3 (der Generationszaehler) und Mutation 4 (das
Abmelden beim Schliessen). Jede allein macht mindestens einen W3-Fall rot —
der zweite W3-Fall existiert genau deshalb, weil der erste gegen Mutation 4
allein nicht scharf waere.

## Annahmen

1. **W1s erlaubte Stellen sind drei, nicht eine.** AD-028 schreibt *„keine
   Datei unter `nrplanner/` ausser `advisor/worker.py`"*. Gemessen mit der
   AST-Zaehlung ueber alle Module unter `nrplanner/`:

   | wer | was | warum |
   |---|---|---|
   | `nrplanner/advisor/worker.py` | `run.run` | die Advisor bar bekommt ihre Antwortfunktion bei der Konstruktion (AD-028 Option D) |
   | `nrplanner/app.py` | `run.slot_pool` | dasselbe fuer die Picker-Spur; **uebergeben, nie aufgerufen** |
   | `nrplanner/advisor/run.py` | `candidates.pool` | `slot_pool` **ist** die Pool-Funktion; das dort zu verbieten hiesse die Funktion zu verbieten |

   Der Wortlaut ist vor U5b geschrieben; die beiden zusaetzlichen Stellen
   konnten nach AD-028 gar nicht woanders liegen. Was AD-028 meint, steht
   unveraendert: **kein Fenster, kein Dialog und kein Tab** bekommt die
   Rechnung zu fassen, also kann sie nur im Thread des Workers laufen. Die
   Tabelle steht mit dieser Begruendung im Test. **Wenn der `architect` den
   Wortlaut woertlich haben will, ist das ein Auftrag an den `developer` fuer
   `app.py` — dann muesste die Antwortfunktion der Picker-Spur ueber
   `worker.py` benannt werden.**
2. **W6s Liste der Ausgaenge ist die, die der Controller anbietet.** Fuenf
   Wege, aus `worker.py` abgelesen: die Antwortfunktion kehrt zurueck oder
   wirft; die Frage wird vor dem Lauf, waehrend des Laufs oder durch einen
   Datenneubau aufgegeben. `shutdown` ist **nicht** dabei — siehe Befund 1.

## Befunde (gemeldet, nicht behoben)

### Befund 1 — `shutdown()` beendet eine laufende Frage ohne Ausgangssignal

`AdvisorController.shutdown` leert `_pending`, stoppt den Zeitgeber,
unterbricht den Worker und wartet — und sendet **keines** der drei Signale.
Eine Frage, die beim Schliessen des Fensters unterwegs ist, endet damit in
keinem der drei Ausgaenge.

**Kein Fehler im laufenden Betrieb**, und deshalb nicht in W6 aufgenommen: der
Picker ist modal, `shutdown` kommt aus `closeEvent`, und es gibt kein Raster
mehr, das leer bleiben koennte. Es steht hier, weil die Zusage im Docstring
(`worker.py:144`) ohne diese Einschraenkung gelesen wird und W6 genau diese
Zusage bewacht. **An den `architect`:** entweder ein Halbsatz im Docstring
(„ausser beim Schliessen") oder ein sechster Eintrag in W6s Tabelle — beides
ist eine Entscheidung, keine Programmierarbeit.

### Befund 2 — `search.Cancelled` aus der Antwortfunktion endet ebenfalls stumm

`_Worker.work` faengt `search.Cancelled` und sendet nur `finished`. Erreichbar
ist das nur, nachdem `requestInterruption()` gelaufen ist, und das geschieht
an genau drei Stellen: `cancel()` (sendet `stopped`), `_wait_for` (dann
beantwortet die **neue** Frage den Ausgang) und `shutdown` (Befund 1). Die
Zusage haelt also — aber sie haelt **mittelbar**, ueber drei Aufrufer, und
nicht aus sich heraus. Gemeldet, nicht gebaut: ein Waechter dafuer waere ein
Waechter ueber drei Aufrufstellen und gehoert in denselben Entscheid wie
Befund 1.

### Befund 3 — der Parallellauf T-132 arbeitet im selben Arbeitsbaum

`scripts/differential/mutate.py` ist zur Stunde **uncommittet geaendert**
(+206 Zeilen, 11 neue Mutationen), und zwei `python.exe` laufen mit
`-m pytest tests/test_relic_picker_advisor.py`. **Ich habe die Datei nur
gelesen, nichts daran geaendert und sie nicht mit committet** (`git status`
nach dem Commit: sie steht weiter als ` M`). Die beiden Prozesse gehoeren
nicht mir — ich habe keinen Hintergrundlauf gestartet — und wurden **nicht**
beendet. Meine eigene Messkopie und der Klon sind geloescht; im Scratchpad
`T-131/` liegen nur noch `campaign.py` und zwei Textdateien.

**Fuer den `director` heisst das:** meine Suitezahl **1323** ist im
gemeinsamen Baum gemessen und enthaelt 11 Faelle, die T-132 gehoeren. Die
Zahl, gegen die die naechste Rolle misst, ist erst stabil, wenn T-132
committet hat.

## An T-132 — die neun Mutationen, uebernahmefertig

Namen sind Vorschlaege; Pfad, `old` und `new` sind woertlich das, was
gemessen wurde. **Zwei davon stehen bereits in eurer Registry** und toeten
jetzt zusaetzlich Faelle aus meiner Datei:

| Name | Pfad | zusaetzlich getoetet |
|---|---|---|
| `picker-refresh-never-waits` *(vorhanden)* | `nrplanner/relicpicker.py` | **W2** und **beide W3-Faelle** — bitte in `survival_means` nachtragen |
| `picker-worker-does-not-stamp-the-generation` *(vorhanden)* | `nrplanner/advisor/worker.py` | **W7**, W6 (`the answer comes back`), W5, W3 |

Neu, mit exaktem Anker:

1. **`picker-holds-the-pre-sort-again`** — `nrplanner/relicpicker.py`
   `old`:
   ```
           window = self._slot.window()
           asking = advisorbar.asking_from(
   ```
   `new`:
   ```
           from .advisor import candidates as advisor_candidates

           pool = advisor_candidates.pool
           window = self._slot.window()
           asking = advisorbar.asking_from(
   ```
   *survival_means:* der Picker duerfte die Vorsortierung wieder in die Hand
   nehmen — 318,1 ms im Thread des Fensters, das Sechsfache von A6s 50 ms —
   und niemand haelt fest, dass er es nicht darf. Getoetet von
   `test_picker_track_guards.py::test_w1_nothing_but_the_named_places_reaches_the_calculation[candidates-pool]`
   und `::test_w1_the_picker_holds_none_of_the_three`.
2. **`controller-delivers-an-overtaken-answer`** —
   `nrplanner/advisor/worker.py`
   `old`:
   ```
           self._cache.put(self._running.request, result)
           if result.generation != self._generation:
               return
   ```
   `new`:
   ```
           self._cache.put(self._running.request, result)
   ```
   *survival_means:* die Antwort einer geschlossenen Oeffnung fuellt das
   Raster der naechsten — dieselben Karten, plausible Zahlen, kein Fehler,
   den irgendjemand sieht (Nachtrag IX-4 Fall 3). Getoetet von
   `::test_w3_the_answer_of_a_closed_opening_never_fills_the_next_one` und
   zweimal von `::test_w6_…`.
3. **`picker-goes-on-listening-after-it-closes`** —
   `nrplanner/relicpicker.py`
   `old`:
   ```
           if self.advice is not None:
               self.advice.stop_listening()
           super().done(result)
   ```
   `new`:
   ```
           super().done(result)
   ```
   *survival_means:* AK-207 faellt; eine Antwort zeichnet in einen Dialog,
   den es nicht mehr gibt. Getoetet von beiden W3-Faellen.
4. **`sort-by-offers-a-direction-nobody-scores`** — `nrplanner/advisorbar.py`
   `old`: `GOAL_ORDER = ("max_damage", "min_damage_taken")`
   `new`: `GOAL_ORDER = ("max_damage", "min_damage_taken", "max_style")`
   *survival_means:* die Wiederverwendung aus IX-0 waere eine Annahme ueber
   zwei Dateien, die niemand zusammenhaelt. Getoetet von `::test_w4_…`.
5. **`a-known-answer-goes-round-by-the-timer`** —
   `nrplanner/advisor/worker.py`
   `old`:
   ```
           question = self._question_from(request, inventory, ctx)
           known = self._cache.get(question.request)
           if known is None:
               self._wait_for(question)
               return None
   ```
   `new`:
   ```
           question = self._question_from(request, inventory, ctx)
           self._wait_for(question)
           return None
   ```
   *survival_means:* IX-1.C faellt, und mit ihr die Voraussetzung des leeren
   Rasters: bei jeder dritten Oeffnung (30 %, S11-F) blitzt das ganze Raster
   auf. Getoetet von `::test_w5_…`.
6. **`cancelling-says-nothing`** — `nrplanner/advisor/worker.py`
   `old`:
   ```
           self._interrupt_the_running_worker()
           self.stopped.emit()
           return True
   ```
   `new`:
   ```
           self._interrupt_the_running_worker()
           return True
   ```
   *survival_means:* AK-218 bricht an seiner dritten Stelle — das Raster
   bleibt leer, fuer immer, ohne Fehlermeldung. Getoetet von drei
   W6-Faellen.
7. **`a-run-that-raises-says-nothing`** — `nrplanner/advisor/worker.py`
   `old`: `            self.failed.emit(str(exc) or exc.__class__.__name__)`
   `new`: `            pass`
   *survival_means:* dasselbe an der zweiten Stelle; eine geworfene Rechnung
   endet stumm, `traceback.print_exc()` schreibt in eine Konsole, die kein
   Spieler sieht. Getoetet von `::test_w6_…[the answer raises]`.

**Vorsicht bei zwei Ankern:** `self._interrupt_the_running_worker()` steht
viermal in `worker.py`; der Anker oben ist der dreizeilige Block aus `cancel`
und matcht genau einmal (vom Treiber geprueft). Ebenso ist
`self._cache.put(...)` einmalig nur zusammen mit den zwei folgenden Zeilen.

## An den qa-engineer

- **Der Weg, der am ehesten bricht, bleibt der Cache-Treffer** (W5). Die
  Oberflaechenprobe dazu braucht keine Uhr: denselben Slot zweimal oeffnen,
  beim zweiten Mal darf kein leeres Raster aufblitzen, und
  `RelicPicker.waiting` ist am fertigen Dialog `False`.
- **Zwei Oeffnungen an einer Spur** sind jetzt als Waechter da (W3), aber nur
  in der Reihenfolge *A oeffnen → A schliessen → B oeffnen → A antwortet*.
  **Nicht** abgedeckt, weil es die Oberflaeche nicht hergibt (modal): zwei
  gleichzeitig offene Picker.
- **`failed` und `stopped` erreiche ich weiterhin nicht ueber die
  Oberflaeche** — sie kommen nur ueber `before_the_data_changes`/`shutdown`,
  und beide sind waehrend eines modalen Dialogs nicht ausloesbar. W6 stellt
  sie am Controller.
- **AK-217** (Fokus springt nicht auf eine Karte, Bildlauf am Anfang) ist
  weiterhin **kein** Fall — T-130 hat die Luecke gemeldet, T-131 hatte sie
  nicht im Umfang. Sie steht noch offen.
- W2 prueft zusaetzlich, dass **nichts im leeren Bereich den Tastaturfokus
  nimmt** (`focusPolicy() != Qt.NoFocus` → leer) und dass kein Wartecursor
  gesetzt ist (`QApplication.overrideCursor() is None`).

## An den ui-ux-designer

- **AK-212 ist jetzt in einem Fall vollstaendig gehalten** — alle acht
  Klauseln in `test_w2_…`, inklusive der Kopfzeile („leer") und der beiden
  AK-201-Zeilen. Die Wortlaute stehen als Literale aus §7 im Test; wenn ein
  Satz sich aendert, faellt der Waechter, und das ist Absicht.
- **AK-216 und AK-214** sind von T-130 gemessen und mit Faellen belegt; ich
  habe sie nicht verdoppelt.
- **Keine Abweichung von einer UI-Vorgabe.** Wo AD-028s Wortlaut und AK-212
  auseinandergehen (W2), gilt AK-212 — so hat es der Auftrag entschieden.

## An den director

- **Befund 1 und Befund 2** brauchen eine Entscheidung des `architect`
  (Docstring praezisieren oder W6 erweitern). Beides ist klein; keins
  blockiert.
- **Annahme 1** (W1s drei erlaubte Stellen) braucht ein „so ist es gemeint"
  vom `architect` — sonst steht im Test eine Tabelle, die von AD-028s
  Wortlaut abweicht.
- **Befund 3** (Parallellauf T-132 im selben Baum, uncommittete
  `mutate.py`, zwei fremde `pytest`-Prozesse): meine Suitezahl enthaelt 11
  fremde Faelle. Ich habe fremde Dateien weder angefasst noch committet.
- **Keine neue Abhaengigkeit.** Kein Netzwerkzugriff, keine Secrets, kein
  neuer Dateizugriff. **Keine Sicherheitsfunde.**
- **QA-212:** ich habe das Programm **nicht gestartet**; gearbeitet wurde
  ausschliesslich mit `pytest` unter der offscreen-Plattform, also unter
  genau den Umlenkungen, die `tests/conftest.py` setzt (`NIGHTREIGN_SETTINGS_ORG`
  und `NIGHTREIGN_SETTINGS_APP`). `LOCALAPPDATA` und `APPDATA` habe ich
  **nicht** umgelenkt und auch nicht umlenken muessen — mein Code schreibt
  nirgends hin, und die Fenster, die meine Faelle bauen, baut die Suite an
  vielen anderen Stellen genauso. **QA-212 bleibt offen und unberuehrt.**
- **Linter:** im Projekt ist keiner konfiguriert (`requirements-dev.txt` fuehrt
  nur `pytest` und `pytest-xdist`; keine `.flake8`, `setup.cfg`, `ruff.toml`,
  `pyproject.toml`). Der DoD-Punkt entfaellt.
- **Nicht angefasst:** `scripts/differential/mutate.py`,
  `scripts/measure_picker_cards.py`, `UI_SPEC.md`, `ARCHITECTURE.md`,
  `GOAL.md`, `docs/state.md`, `qa/findings.md`, `docs/tasks/`. Kein
  Anwendungscode.
