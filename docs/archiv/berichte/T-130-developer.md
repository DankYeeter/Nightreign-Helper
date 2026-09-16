# T-130 — U5b: die Picker-Spur verdrahten (developer)

```
STATUS: erledigt
AUFTRAG: T-130 — U5b: die Picker-Spur verdrahten
GELESEN: docs/tasks/T-130.md · ARCHITECTURE.md AD-028 (ab 3985) samt
  Lesehinweis und Nachtrag IX ganz (4461-4900) · UI_SPEC.md beide
  Picker-Abschnitte (T-124 ab 6027 mit AK-197 bis AK-210, T-127 ab 6444 mit
  der Streichliste und AK-211 bis AK-219) · docs/berichte/T-128-developer.md
  (Quittung U5a) · Quellstand: nrplanner/advisor/{worker,run,types,goals,
  candidates}.py, nrplanner/{relicpicker,advisorbar,app,cardgrid}.py,
  tests/{test_relic_picker_advisor,test_relic_picker_geometry,
  test_advisor_worker,test_advisor_types,test_advisor_slot_pool,
  test_differential_track}.py, scripts/differential/mutate.py
GEÄNDERT: nrplanner/advisor/types.py · nrplanner/advisor/worker.py ·
  nrplanner/app.py · nrplanner/relicpicker.py ·
  scripts/differential/mutate.py (zwei Mutationsanker, siehe „Ausserhalb der
  fuenf Dateien") · tests/test_advisor_types.py ·
  tests/test_advisor_worker.py · tests/test_relic_picker_advisor.py ·
  tests/test_relic_picker_geometry.py — alles in Commit `1a2cc5b`;
  dieser Bericht in einem zweiten Commit
ANNAHMEN: drei, unten unter „Annahmen" einzeln begruendet
NÄCHSTER: director (danach U6: die Waechter W1 bis W5)
BLOCKIERT DURCH: nichts
```

> **Zum Schluss dieses Laufs:** die Zugschwelle (150 Werkzeugaufrufe) hat beim
> **letzten** Punkt gegriffen — einer Nachpruefung, wie `tests/conftest.py` die
> drei Datenverzeichnisse behandelt. Code, Tests, Suitelauf und Commit `1a2cc5b`
> lagen da vollstaendig vor; betroffen ist nur eine Nebenaussage weiter unten,
> die deshalb jetzt so eng steht, wie ich sie belegen kann. Nichts ist
> uncommittet, nichts halbfertig.

## Umgesetzt

**Commit `1a2cc5b`** auf `docs/audit-and-advisor-design`, Basis `5639b84`.
Ein Commit, weil jede Teilmenge einen roten Zwischenstand ergibt: der Picker
ruft `advisor.candidates` nicht mehr, und der Controller kann die Pool-Antwort
erst nach der Generations-Stempelung zustellen.

### `nrplanner/advisor/worker.py`

| Stelle | was |
|---|---|
| `AdvisorController.__init__(..., answer=advisor_run.run)` | die Antwortfunktion kommt bei der Konstruktion (AD-028 Option D); `_Worker` bekommt sie durchgereicht |
| `PICKER_DEBOUNCE_MS = 0`, `PICKER_CACHE_SIZE = 64` | mit Herleitung, Wiederkehrbedingung (IX-1.2) und der 140-KiB-Messauflage (IX-3.2) im `#:`-Block |
| `ask_and_answer_if_known(request, inventory, ctx)` | IX-1.3: Treffer als **Rueckgabewert**, ohne `ready`, ohne `started`, ohne etwas zu starten; Fehltreffer `None` und der gewohnte Weg |
| `_question_from` / `_wait_for` | die gemeinsame private Frageerzeugung; `ask` ist Zeile fuer Zeile dasselbe Verhalten wie vorher (die Advisor bar ist unveraendert) |
| `_Worker.work` | stempelt die Generation auf die Antwort — **das war der Fehler, der den ganzen Weg still stillstehen liess**, siehe „Befund 1" |

### `nrplanner/advisor/types.py`

- **`ChosenDirection` und `PoolOrder`**, beide `str`-Unterklassen, und
  `AdvisorRequest.__post_init__` macht aus einem schlichten `str` eine
  `ChosenDirection`. Damit sagt **jede** Anfrage im Typ, in welchem der
  beiden Sinne ihr `goal_id` gemeint ist; `isinstance` beantwortet es, und
  Gleichheit, Hash und `repr` bleiben die des Strings, damit Cache-Schluessel,
  `goals[request.goal_id]` und jeder Vergleich unveraendert weiterlaufen.
  Das ist Entscheidung 4 des Auftrags; die gewaehlte Form ist der eigene Typ.
- **`SlotPool.generation: int = 0`.** Der Controller entscheidet an diesem
  Feld, ob eine Antwort noch die gefragte ist, und `ResultCache.get` stempelt
  es beim Treffer um. `candidates.pool` setzt es nie, also traegt jeder Pool
  der Beam-Suche 0, und zwei Pools derselben Frage bleiben gleich.

### `nrplanner/app.py`

- `self.picker_advisor = AdvisorController(self, answer=advisor_run.slot_pool,
  cache=advisor_run.ResultCache(PICKER_CACHE_SIZE),
  debounce_ms=PICKER_DEBOUNCE_MS)` — direkt neben der Advisor bar, am
  Fenster, nicht am Dialog (AD-028.5).
- `the_advisor_data_is_changing()` und `shutdown_the_advisor()`: **eine**
  Stelle, die an beide Spuren verteilt (AD-028.6). Die drei bisherigen
  Aufrufer (`rescan_save`, `load_equipped`, `closeEvent`) rufen jetzt diese.

### `nrplanner/relicpicker.py`

- **Importe:** `advisor.candidates` und `advisor.run` sind raus — die beiden,
  die AD-028.7 nennt und die den Picker rechnen liessen. `advisor.goals` und
  `advisor.types` bleiben (Begruendung unter „Annahmen", Punkt 1).
- **`SlotAdvice`** rechnet nichts mehr: `ask(answered) -> Asked | None` stellt
  die eine Frage der Oeffnung an die Spur des Fensters, unter
  `PoolOrder(goals.CANONICAL_POOL_ORDER)` und mit **jedem Slot ausser dem
  geoeffneten gehalten** (die kanonische Form aus U5a). `stop_listening()`
  trennt beim Schliessen. Der Docstring `276-281` ist ersetzt; die widerlegten
  ~51 ms stehen nicht mehr da (OF-27, dritte Fundstelle).
- **`Asked`** (neu, frozen dataclass) trennt „die Antwort ist noch unterwegs"
  von „es gab nichts zu fragen" (kein Spielstand). Beide sahen vorher gleich
  aus und haetten den Wartezustand zur Anzeige fuer „kein Save" gemacht.
- **`Ranking.goal_id` ist entfernt.** Es gab `pool.rank_by` heraus; genau das
  verbietet AK-205. Die Anzeige nimmt ihre Richtung aus
  `RelicPicker._drawn_direction()` = die eine Einstellung des Programms.
- **Wartezustand (F-P, F-R, AK-212 bis AK-219):** kein Kartenwidget, auch
  nicht die Custom-Kachel; eine Zeile `Your relics appear here.` am Ursprung
  des Rasterinhalts; Zeile 3 traegt nur
  `Working out what each relic is worth with <slot> empty`; Kopfzeile leer;
  Pflichtzeile und `scope`-Saetze stehen (AK-201), die Laufbefundzeile wartet.
  Nichts ist gesperrt. **Die Karten werden gebaut und gemessen, nur nicht
  gezeigt**, damit die Groesse beim ersten Anstrich steht (AK-216).
- **`_sort_chosen` fragt nicht mehr** (IX-0); **`_the_answer_arrived`** setzt
  alles in einem Anstrich (AK-211); Fehlschlag und Abbruch fuellen das Raster
  mit `—` und der Kopfzeile aus AK-208/AK-218; **`done()`** hoert auf zu
  hoeren (AK-207); **`waiting`** ist als Eigenschaft lesbar, weil sonst
  niemand „noch keine Antwort" von „nichts zu ranken" unterscheiden kann.

## Befunde

### Befund 1 — eine Antwortfunktion, die die Generation nicht stempelt, wird **immer** still verworfen

Der erste lauffaehige Stand hat nie geantwortet: `started` kam, `ready` und
`failed` nicht, der Thread war sauber zu Ende. Grund: `run.slot_pool` gibt
zurueck, was `candidates.pool` gebaut hat, und die Vorsortierung weiss nichts
von Controllern — also `generation = 0`, waehrend `_on_ready` gegen die
laufende Generation `1` prueft und wortlos aussteigt (`worker.py`, AD-006.3).
`run.run` stempelt selbst, deshalb ist das nie aufgefallen.

**Behoben an der einzigen Stelle, die Frage und Antwort zugleich kennt:**
`_Worker.work` stempelt. Damit muss keine Antwortfunktion von Generationen
wissen, und die naechste (falls je eine dritte Spur kommt) faellt nicht in
dieselbe Grube. Der Testfall dazu (`Answering` in
`tests/test_advisor_worker.py`) stempelt **absichtlich nicht** und prueft, dass
die Antwort trotzdem mit der Generation der Frage ankommt — sonst haette der
Test den Fehler mitgemacht.

**An den `director` fuer U6:** das ist ein Kandidat fuer einen eigenen
Waechter neben W3. Die toetende Aenderung ist eine Zeile
(`dataclasses.replace(...)` in `work` durch `result` ersetzen), das Symptom
ist ein Dialog, der ewig wartet, und die gruene Suite von vorher hat nichts
gemerkt.

### Befund 2 — `scripts/measure_picker_cards.py` misst ab jetzt ein leeres Raster

Das Skript oeffnet den `RelicPicker` und liest `findChildren(RelicCard)`
(Zeilen 89-107, 175-179). Nach diesem Auftrag steht dort bis zur Antwort nichts.
**Nicht angefasst** — es gehoert dem `performance-tuner` und U7 braucht es. Was
es braucht, ist die Schleife, die auch die Test-Vorrichtung jetzt hat: warten,
bis `picker.waiting` falsch ist. **An den `director`:** vor U7 einplanen.

### Befund 3 — der Laufbefund-Zeile wegen waechst der Dialog nicht mit

Traegt der Pool `unknowns`, erscheint die Laufbefundzeile (3b) erst mit der
Antwort. Der Dialog hat seine Groesse da schon (`_sized`), waechst also nicht
mehr; der Kartenbereich bekommt entsprechend weniger Platz. Das ist genau, was
AK-201 (3b darf warten) und AK-216 (die Masse der beraterfreien Ordnung)
zusammen verlangen — **es ist eine Folge, kein Fehler**, und es steht hier,
weil es der `ui-ux-designer` wissen sollte, bevor es jemand als Bug meldet.

## Belege

### Suite

```
pytest -n auto  ->  1297 passed, 9 skipped, 0 failed  (170,39 s)
```

gegen die Vorgabe **1275 passed, 9 skipped, 0 failed**: **+22 Faelle**, alle
neu von mir (5 in `test_advisor_worker.py`, 5 in `test_advisor_types.py`, 12 in
`test_relic_picker_advisor.py`). Kein Fall geloescht, keiner deaktiviert. Der
Lauf lag **nach** dem Stand von `1a2cc5b` und vor dem Schreiben dieses
Berichts; danach wurde keine Quell- oder Testdatei mehr angefasst.

### Rot-vorher (L-007), je Aenderung einzeln geprueft

Jede Zeile ist ein von Hand angebrachter Gegenbau, danach `cp`-Wiederherstellung
der Datei (nie `git checkout`), Arbeitsbaum hinterher geprueft
(`git diff --stat`).

| Gegenbau | Faelle, die fallen |
|---|---|
| `_drawn_direction` gibt `self.ranking.pool.rank_by` zurueck (AK-205) | `test_the_drawn_direction_is_the_setting_and_not_the_pools_order` (1 failed, 2 passed) |
| `waiting = False` in `_refresh` (der Wartezustand faellt weg) | `test_the_card_area_is_empty_until_the_answer_arrives`, `test_the_waiting_line_says_nothing_a_card_would_say`, `test_a_filter_that_matches_nothing_leaves_the_line_standing` (3 failed, 2 passed) |
| `_fit_to_three_rows` im Wartezweig weglassen (die Groesse wartet auf die Antwort) | `test_the_dialog_takes_its_size_at_the_first_paint` (1 failed) |
| die Generations-Stempelung in `_Worker.work` ausbauen | der ganze Picker-Weg steht — gefunden **als** Fehler, siehe Befund 1; `test_a_controller_runs_the_answer_it_was_built_with` prueft es seitdem |

**Zwei meiner Faelle ueberleben den Wartezustands-Gegenbau, und das ist
richtig** (L-008c, gemeldet statt nachgebessert):
`test_the_mandatory_lines_do_not_wait` bewacht `_say_what_was_left_out` — es
faellt, wenn dort wieder **beide** Zeilen bei fehlender Rangfolge versteckt
werden. `test_the_dialog_takes_its_size_at_the_first_paint` bewacht
`_sized`/`_fit_to_three_rows` — seine toetende Aenderung steht eine Zeile
darueber in der Tabelle.

### Die beiden Mutationsanker, die ich verschoben habe, toeten weiterhin

| Mutation | geprueft |
|---|---|
| `advisor-controller-answers-every-keystroke` | `tests/test_advisor_worker.py::test_a_burst_of_questions_is_one_run` → **1 failed**, 17 passed |
| `picker-back-to-a-fixed-column-count` | `tests/test_relic_picker_geometry.py` → **4 failed**, 2 passed (drei Breiten plus die Drei-Reihen-Hoehe) |

`tests/test_differential_track.py` (222 Faelle, darunter der Ankerwaechter) ist
gruen.

### AK-216, die Messauflage des `ui-ux-designer` (L-009)

**Umgebung:** Windows 10 x64, Qt-Plattform **offscreen**, Stil **fusion**,
`devicePixelRatio` **1.0**, also **logische = physische px**; Bestand des
Nutzers, Slot 1, **54 Karten**; Standardmass des Pickers (Dialog 1024 px breit,
Kartenbereich `room` = 996 px); gemessen im Baum von `1a2cc5b` ueber
`RelicPicker._chrome_height`, `_room_for_three_rows` und `wanted_height`.

| Groesse | heutiger Weg (Karten im Raster) | Weg des Wartezustands (Karten gebaut, nicht gezeigt) |
|---|---|---|
| `_chrome_height()` | **297 px** | **297 px** |
| `_room_for_three_rows(cards)` | **840 px** | **840 px** |
| `wanted_height(cards)` | **1137 px** | **1137 px** |
| Aussenmasse des Dialogs | 1024 x 800 px | 1024 x 800 px |

**Differenz 0 px an jeder der vier Zeilen.** (Die 800 px sind der offscreen-
Desktop, an dem `_fit_to_three_rows` deckelt — beide Wege gleich.)

### AK-214, die zweite Messauflage (Zeile 3 waehrend des Wartens)

Dieselbe Umgebung, `heightForWidth(996)` auf `summary`:

| Fassung | Zeichen | Hoehe |
|---|---|---|
| Wartefassung | 54 | **11 px** |
| fertige Fassung | 103 | **24 px** |

Die Wartefassung wird also **nicht hoeher** gezeichnet als die fertige; gekuerzt
werden muss nichts. (Dass die fertige Fassung an dieser Stelle zwei Zeilen
misst, `_chrome_height` sie aber wie 24 px behandelt, liegt am
`sizeHint`-Rueckfall in `_asked_height` — das ist Bestand und beruehrt die
Zusage nicht.)

### Was die neuen Faelle abdecken

`tests/test_relic_picker_advisor.py`: leeres Raster mit allen fuenf Zusagen aus
AK-212 · Zeile 3 ohne Zaehlung (AK-214) · Pflichtzeilen stehen (AK-201) ·
nichts gesperrt, ein Anschlag fragt nicht nach (AK-213, AK-206) · Filter ohne
Treffer waehrend des Wartens (§3-Randfall) · die Antwort fuellt in einem Zug
und ohne `…` (AK-211, AK-219) · Fehlschlag mit Wortlaut (AK-208) · Abbruch mit
eigenem Grund (AK-218) · geschlossener Dialog hoert nichts mehr (AK-207) ·
Oeffnung ohne eine einzige Karte wartet nicht (AK-212-Ausnahme) · Groesse beim
ersten Anstrich (AK-216) · gezeichnete Richtung ist die Einstellung (AK-205).
`test_advisor_worker.py`: die Antwortfunktion kommt von aussen und laeuft im
Thread · Treffer im selben Aufruf, ohne `started`, ohne zweites `ready` ·
Zaehler steigt auch fuer den Treffer (IX-1.4) · Fehltreffer ist `None` und
nimmt den gewohnten Weg · beide Wege frieren den Bestand **gleich oft** ein.
`test_advisor_types.py`: die beiden Sinne von `goal_id` im Typ, ueber
`dataclasses.replace` hinweg, ohne die Gleichheit zu brechen · `SlotPool`
traegt die Generation der Frage.

Die vorhandene Vorrichtung `FakeAdvice` ist auf das neue Protokoll gezogen und
ist jetzt zugleich die vier Vorrichtungen der Spec: antwortet sofort, antwortet
nie, meldet `failed`, meldet `stopped`. `test_the_figure_on_a_card_is_the_pools_own_float`
faehrt jetzt ueber die **echte** Spur des Fensters (Frage, Thread, Antwort) statt
ueber einen Direktaufruf — der einzige Fall, der den ganzen Weg zusammen prueft.

## Annahmen

1. **`advisor.goals` und `advisor.types` bleiben in `relicpicker` importiert.**
   AD-028.7 nennt namentlich `advisor.candidates` und `advisor.run` — die
   beiden, die den Picker rechnen liessen; die sind weg. `goals` liefert die
   Labels des `Sort by`, die `scope`-Saetze und `CANONICAL_POOL_ORDER`, `types`
   die `PoolOrder` und die Typangabe von `Ranking`. Sie herauszunehmen hiesse,
   das alles ueber `advisorbar` zu reichen — und `advisorbar.py` steht nicht in
   den fuenf Dateien des Auftrags. **Wenn „direkte `advisor`-Importe entfernt"
   woertlich alle vier meint, ist das ein eigener kleiner Auftrag mit
   `advisorbar.py` im Umfang.**
2. **Die Groesse wird immer in der beraterfreien Ordnung genommen.**
   `_refresh` baut die Karten einmal und liest sie in zwei Ordnungen: die
   gezeigte und die, in der `_fit_to_three_rows` misst. Damit nimmt auch eine
   Oeffnung mit Cache-Treffer dieselben Masse wie eine wartende — was AK-216
   woertlich verlangt („dieselben, die er mit denselben Karten in der
   beraterfreien Ordnung annaehme") und was seine Vorrichtung sonst nur
   zufaellig bestanden haette. Es ist eine **Aenderung gegenueber heute**: bis
   jetzt bestimmte die sortierte Ordnung die Hoehe.
3. **Bei „kein Spielstand" stehen die `scope`-Saetze jetzt auch.** Vorher waren
   Pflichtzeile und `scope` bei fehlender Rangfolge versteckt. AK-201 verlangt
   sie fuer den Wartezustand; sie haengen an der Richtung und nicht am Lauf,
   also stehen sie ueberall, wo es eine Richtung gibt. Sichtbar wird das im
   4.8-Zustand (kein Save).

## Ausserhalb der fuenf Dateien: `scripts/differential/mutate.py`

**Zwei Mutationsanker, sonst nichts** — kein `survival_means` geaendert, keine
Mutation hinzugefuegt oder entfernt. Beide Anker zeigten auf Zeilen, die ich in
diesem Auftrag umgebaut habe (`ask` → `_wait_for`, und der `CardGrid`-Aufruf),
und `tests/test_differential_track.py` war dadurch **rot**. Die Datei sagt an
genau dieser Stelle selbst, was zu tun ist: *„Update the mutation to the new
source; do not loosen the anchor."* Ich habe die Anker nachgezogen, die Bedeutung
beider Mutationen unveraendert gelassen und **nachgewiesen, dass beide weiter
toeten** (Tabelle oben). Ich melde es ausdruecklich, weil der Auftrag fuenf
Dateien plus `tests/` als Obergrenze nennt: das ist die sechste, und sie ist
eine Folge meiner Aenderung, keine Nebenarbeit.

## Nicht gemacht (Auftragsgrenzen eingehalten)

- **W1 bis W5** samt toetenden Mutationen und Registry-Eintraegen — das ist U6.
  Ich habe den Zustand gebaut, den W2 pruefen wird, und meine eigenen Faelle
  liegen daneben; sie ersetzen die Waechter nicht.
- **Der Rueckweg aus `UI_SPEC` §4** (Richtungswechsel fragt doch) — nicht
  gebaut und nicht noetig: ein Pool traegt fuer jeden Kandidaten beide
  Richtungen, und die Anzeige liest beide aus **einem** Pool
  (`Ranking.gain`/`top_handles` je Richtung). Kein Befund.
- **Kein Vorwaermen**, **`AdvisorResult` nicht um den Pool erweitert**, **kein
  zweiter Zaehler**, **kein zweiter Thread-Weg**, **SEC-022 nicht angefasst**,
  **keine Zeitschranke in der Suite** (die einzigen Zeiten im neuen Testcode
  sind zwei **Sicherungen** gegen eine Frage, die in keinem der drei Ausgaenge
  endet: 30 s in `test_relic_picker_advisor.py` und in der Geometrie-
  Vorrichtung; nichts behauptet etwas ueber Dauer).
- **Die Entprellung der Klasse** ist unveraendert 250 ms; die 0 ms gehoeren der
  Instanz. **Der Cache wird nicht generell vor den Zeitgeber gezogen** — nur
  `ask_and_answer_if_known` sieht vorher nach, und die Advisor bar ruft
  weiterhin `ask`.
- `UI_SPEC.md`, `ARCHITECTURE.md`, `GOAL.md`, `docs/state.md`, `qa/findings.md`
  und `docs/tasks/` sind nicht angefasst (`git status` nach dem Commit: sauber
  bis auf die untracked Auftragsdatei des Directors und diesen Bericht).

## An den qa-engineer

- **Der Weg, der am ehesten bricht, ist der Cache-Treffer.** Zweimal denselben
  Slot oeffnen: das zweite Mal darf **kein** leeres Raster aufblitzen. Ein
  Test dafuer braucht keine Uhr — `RelicPicker.waiting` ist am fertig gebauten
  Dialog `False`, wenn der Treffer im ersten Anstrich kam.
- **Randfaelle, die ich gebaut, aber nicht ueber die Oberflaeche erreicht
  habe:** `stopped` (kommt nur ueber `before_the_data_changes`/`shutdown`, und
  beide sind waehrend eines modalen Dialogs nicht ausloesbar) und `failed`
  (braucht eine werfende Rechnung). Beide sind mit der Vorrichtung
  `FakeAdvice(..., at_once=False)` + `.stop()` / `.fail(reason)` zu stellen.
- **Zwei Oeffnungen an einer Spur** (Slot A oeffnen, schliessen, B oeffnen,
  bevor As Antwort da ist): As Antwort darf Bs Raster nicht fuellen. Das faellt
  doppelt (Zaehler im Controller **und** getrennte Verbindung), was Absicht ist
  — ein Gegenbau muss beide einzeln ausbauen, sonst belegt er nur einen.
- **AK-217** (Fokus springt nicht auf eine Karte, Bildlauf am Anfang) habe ich
  nicht als Fall geschrieben: `RelicCard` nimmt keinen Fokus, und das Raster
  ist beim Erscheinen neu. Wenn das eine Zusage bleiben soll, gehoert ein Fall
  dazu — ich melde die Luecke, statt sie stillschweigend zu lassen.
- Der einzige Wackler, den ich gesehen habe: `test_a_burst_of_questions_is_one_run`
  (Bestand, Wanduhr) fiel **einmal** unter `-n auto` mit 175 ms gegen seine
  100-ms-Schranke, seriell und im vollen Lauf danach gruen. Kein Zusammenhang
  mit dieser Aenderung erkennbar (die Arbeit je Frage ist dieselbe), aber es
  ist ein zeitabhaengiger Fall unter Parallellast — notiert, nicht angefasst.

## An den ui-ux-designer

- **AK-216 haelt, mit 0 px** (Tabelle oben) — und der Weg dorthin ist Annahme 2:
  gemessen wird **immer** in der beraterfreien Ordnung, auch bei einem
  Cache-Treffer. Ohne das haetten zwei Oeffnungen desselben Slots zwei Masse
  annehmen koennen, sobald die sortierte Ordnung in ihren ersten drei Reihen
  hoehere Karten hat.
- **Befund 3** (Laufbefundzeile erscheint erst mit der Antwort, der Dialog
  waechst nicht mit) — Folge von AK-201 plus AK-216, gemeldet, nicht gefixt.
- **AK-219 haelt nur mittelbar:** `PENDING` steht weiterhin beim Bau jeder Karte
  in den Wertzeilen (AK-41), aber keine solche Karte erreicht je den
  Rollbereich, solange die Frage laeuft — im Wartezustand wird die Karte
  gebaut, gemessen und wieder verworfen. Wer den Waechter schreibt, sollte auf
  „im Rollbereich stehend" pruefen, nicht auf „existiert".
- **Kein Wortlaut erfunden:** `Your relics appear here.`,
  `Working out what each relic is worth with <slot> empty`,
  `Could not work out what these are worth — <reason>. They are in name order below.`
  und `the search was stopped` sind woertlich aus §7 uebernommen.

## An den director

- **Befund 1** (Generations-Stempelung) und **Befund 2**
  (`scripts/measure_picker_cards.py` misst ein leeres Raster) brauchen eine
  Entscheidung: Befund 1 als zusaetzlicher Waechter in U6, Befund 2 als kleiner
  Auftrag **vor** U7.
- **Annahme 1** (die zwei verbliebenen `advisor`-Importe im Picker) braucht
  entweder ein „so ist es gemeint" oder einen Auftrag, der `advisorbar.py`
  in den Umfang nimmt.
- **Sechste Datei:** `scripts/differential/mutate.py`, zwei Anker, Begruendung
  im eigenen Abschnitt. Wenn das nicht in Ordnung geht, ist der Rueckweg eine
  Zeile pro Anker.
- **Fuer U7:** die Picker-Spur liegt jetzt an, also ist die Antwortform fuer
  die 140-KiB-Schranke aus IX-3.2 messbar. Ein Eintrag ist ein `SlotPool` mit
  dem neuen Feld `generation` — an der Groesse aendert das nichts Nennenswertes,
  es gehoert aber in die Messnotiz.
- **Keine Sicherheitsfunde.** Kein Netzwerkzugriff, kein neuer Dateizugriff,
  keine Secrets; der Spielstand wurde nur gelesen. Ich habe das Programm
  **nicht** gestartet — gearbeitet wurde ausschliesslich ueber `pytest` unter
  der offscreen-Plattform. Zu den drei Umlenkungen kann ich belegen:
  `tests/conftest.py:44` setzt `NIGHTREIGN_SETTINGS_ORG = "DankYeeterTests"`.
  **Wie die Suite `LOCALAPPDATA` und `APPDATA` behandelt, habe ich nicht mehr
  nachgesehen** — die Zugschwelle fiel genau in diese Pruefung. Ich habe an
  keiner der drei Variablen etwas geaendert und nichts geschrieben; wer eine
  vollstaendige Aussage braucht, prueft `tests/conftest.py` und die
  `planner`-Vorrichtung. **Das ist eine Luecke im Beleg, kein Beleg.**
- **Keine neue Abhaengigkeit.**
