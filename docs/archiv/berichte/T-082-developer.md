# T-082 - S9: die Rechnung in den Hintergrund (developer)

```
STATUS: teilweise
AUFTRAG: T-082 - S9: die Rechnung in den Hintergrund, dazu D-4 (`rank_by`)
GELESEN: docs/tasks/T-082.md · ARCHITECTURE.md (AD-001, AD-003, AD-006,
  AD-007, AD-008, AD-010 mit der Praezisierung nach D1, AD-013, AD-014,
  AD-016 mit der Praezisierung D3, AD-018, Risiko F4, Fahrplan S4-S11) ·
  UI_SPEC.md (§3.1, §4 Zustandstabelle, §5, AK-08 bis AK-27, T-024 §5
  `Optimize`, T-078 §6/§8, T-080 §7, Offene Frage 3 des T-080-Nachtrags) ·
  docs/state.md (D-1 bis D-11, "Der Rest - in dieser Reihenfolge") ·
  docs/berichte/T-077-qa-engineer.md (die D-4-Messung) ·
  docs/berichte/T-081-developer.md (Verfahren fuer den frischen Klon) ·
  qa/findings.md (QA-105) · nrplanner/advisor/*.py · nrplanner/firstrun.py ·
  nrplanner/inventory.py · tests/advisor_cases.py, conftest.py,
  test_advisor_{search,candidates,types,explain}.py ·
  scripts/differential/mutate.py · scripts/measure_advisor_search.py
GEAENDERT: nrplanner/advisor/run.py (neu) · nrplanner/advisor/worker.py (neu)
  · nrplanner/advisor/types.py · nrplanner/advisor/search.py ·
  nrplanner/advisor/candidates.py · nrplanner/advisor/__init__.py ·
  tests/test_advisor_run.py (neu) · tests/test_advisor_worker.py (neu) ·
  tests/advisor_cases.py · tests/test_advisor_search.py ·
  tests/test_advisor_candidates.py · tests/test_advisor_types.py ·
  scripts/differential/mutate.py · scripts/measure_advisor_search.py ·
  scripts/measure_advisor_worker.py (neu) · UI_SPEC.md (nur die
  `Suggest`/`Optimize`-Korrektur)
ANNAHMEN: sechs, unten einzeln aufgefuehrt (Cache-Schluessel = Anfrage ohne
  Generation; Fingerabdruck des Bestands wird gebaut, weil es keinen gab;
  jeder Vorschlag bekommt seine Begruendung, nicht nur der beste; die
  Einzelfelder des Ergebnisses gehoeren dem besten Vorschlag; `budget_note`
  bleibt leer; kein `progress`-Signal)
NAECHSTER: director
BLOCKIERT DURCH: nichts inhaltlich - **der volle Suitenlauf nach der letzten
  Aenderung fehlt**. Der Lauf wurde vom Zugschwellen-Limit abgeschnitten,
  bevor er starten konnte. Alles ist committet, der Arbeitsbaum ist sauber.
```

**Warum `teilweise` und nicht `erledigt`:** der gesamte Auftragsumfang ist
gebaut, gemessen und in sechs Commits; **die Abnahmezahl der ganzen Suite ist
nicht belegt**. Ich habe nach jedem Teilschritt die betroffenen Dateien
gefahren (unten einzeln mit Zahlen), aber der abschliessende
`pytest -q -m "not slow"` - und erst recht der aus dem frischen Klon - ist
nicht gelaufen. Das ist eine Luecke, kein Beleg. Der naechste Schritt steht
unten unter „Was offen ist".

---

## 1. Testergebnis

| Lauf | Ergebnis | Dauer |
|---|---|---|
| **vorher**, mein Arbeitsbaum, vor der ersten Zeile Code | `985 passed, 9 skipped, 5 deselected` | 440,38 s |
| **nachher**, ganze Suite | **nicht gelaufen** | - |

Der Ausgangswert deckt sich mit der Zahl aus dem Auftrag (985/9/5, Lauf des
`director` aus dem frischen Klon). Befehl:
`.venv\Scripts\python.exe -m pytest -q -m "not slow"`, Windows 10, Python
3.12.10 aus `.venv`, Branch `docs/audit-and-advisor-design`.

**Was tatsaechlich gelaufen ist** (jeweils nach dem zugehoerigen Teilschritt,
Arbeitsbaum):

| Umfang | Ergebnis |
|---|---|
| `test_advisor_types/search/candidates` nach D-4 | `126 passed` |
| `test_advisor_run.py` | `39 passed` |
| `test_advisor_worker.py` | `13 passed` |
| `test_advisor_run + worker` nach dem Helfer-Umzug | `52 passed` |
| `run, search, candidates, types, explain, differential_track, one_build` | `415 passed` |
| `worker, run, differential_track, one_build, single_instance` | `291 passed` |
| `test_differential_track.py` allein | `222 passed` (vorher 207) |

**Erwartung fuer den vollen Lauf, ausdruecklich als Erwartung und nicht als
Zahl:** 985 + 39 (`test_advisor_run.py`) + 13 (`test_advisor_worker.py`) + 2
(`test_advisor_search.py`) + 2 (`test_advisor_candidates.py`) + 15 (die
Ankerprobe ist je Mutation parametrisiert, 15 neue Mutationen) = **1056**,
9 skipped, 5 deselected. Kein Fall wurde geloescht oder deaktiviert; ein
bestehender Fall wurde umgeschrieben (siehe 3.1).

## 2. Commits

| Commit | Inhalt |
|---|---|
| `0409524` | `feat(advisor): der Pool sagt, welche Richtung ihn geordnet hat (D-4)` |
| `26102a8` | `feat(advisor): eine Frage ganz beantworten, und die Antwort behalten` - `run.py`, Cache, Fingerabdruck, eingefrorene Momentaufnahme |
| `c824127` | `feat(advisor): der Lauf bekommt einen eigenen Thread (AD-006)` - `worker.py` |
| `bafc3e1` | `docs(spec): der Knopf heisst ueberall `Optimize`` |
| `792318a` | `test(advisor): miss den Abbruch am echten Spielstand` - `scripts/measure_advisor_worker.py` |
| `c609e87` | `test(advisor): die Frage und ihre Anfrage stehen bei den anderen Faellen` |

## 3. Was gebaut wurde

### 3.1 D-4: `SlotPool` bekommt `rank_by` (`0409524`)

- `types.SlotPool.rank_by` ist **Pflichtfeld ohne Vorgabewert**. Ein Pool, der
  seine Sortierrichtung nicht nennen kann, ist genau der Zustand, gegen den
  das Feld existiert.
- `search.Scorer` ist vom Typalias zur eingefrorenen Datenklasse mit
  `goal_id` **und** `score` geworden. Die Richtung faehrt **mit** der
  Rechenvorschrift statt als zweites Argument neben ihr: ein separater
  Parameter waere ein drittes Ding, das widersprechen kann, und die Pruefung
  vergliche die Pools dann gegen eine Beschriftung statt gegen das, was
  wirklich rankt. `goal_scorer` fuellt `goal_id` aus dem uebergebenen Goal,
  der gewoehnliche Weg kann sich also nicht falsch beschriften.
- `search.beam` weist die Paarung zurueck (`_refuse_pools_ranked_by_another_direction`),
  mit beiden Richtungen in der Meldung.
- **Ein bestehender Fall musste umgeschrieben werden:**
  `test_the_search_ranks_by_the_scorer_it_is_handed` baute **einen** Satz
  Pools (`max_damage`) und fuhr ihn unter beiden Richtungen - also genau das,
  was D-4 verbietet. Er baut jetzt je Richtung eigene Pools; die Behauptung
  wird dadurch staerker (die Zahl muss aus dem Scorer kommen **und** die
  Ordnung, auf der verzweigt wurde, muss die dieses Scorers sein). Die
  Mutation `search-bakes-the-direction-into-the-scorer` toetet er weiterhin.
- Angepasste Aufrufstellen: `tests/test_advisor_search.py` (Helfer `pool_of`,
  `adding_scorer`, `tied_scorer`, das Kindprozess-Skript `ACROSS_PROCESSES`),
  `tests/test_advisor_types.py`, `scripts/measure_advisor_search.py`.
- Ein Anker in `mutate.py` ist mitgewandert
  (`search-refuses-a-vessel-with-every-slot-held`: `scorer(())` →
  `scorer.score(())`).

### 3.2 `advisor/run.py`: eine Frage ganz beantworten (`26102a8`)

Qt-frei. `run.run(request, inventory, ctx, goals, should_cancel)` setzt
Vorsortierung, Beam und Begruendung zu dem einen `AdvisorResult` zusammen,
das AD-010 vorschreibt. Dazu drei Dinge, die daran haengen:

1. **`_refuse_a_request_that_asks_about_another_run`** - der Cache-Schluessel
   ist die Anfrage selbst (AD-007/AD-016 in der Fassung D3), also wird eine
   Anfrage zurueckgewiesen, deren Felder dem Material daneben widersprechen
   (Held-Id, Level, Gewichtung, Referenzwaffe, deklarierte Effekte,
   Datenversion, Effekte der Waffen, Fingerabdruck des Bestands). Ohne das
   kann ein Schluessel fuer einen Lauf stehen, den es nicht gab.
2. **`inventory_fingerprint`** nach dem Rezept aus AD-007 **einschliesslich
   Handle** (die Korrektur vom 01.09.2026). **Es gab bisher keine solche
   Funktion** - `AdvisorRequest.inventory_fingerprint` war in jedem
   existierenden Aufruf leer. Ohne sie traefe der Cache ueber verschiedene
   Bestaende hinweg, und „ueber Bestand" ist die erste Bedingung der
   Cache-Entscheidung des Directors.
3. **`frozen_inventory` / `FrozenInventory` / `OfferedCopy`** - was ueber die
   Threadgrenze geht, ist eingefroren (AD-006 Punkt 8). Die Momentaufnahme
   **fragt** `inventory.relics_for` je Slot des Gefaesses und antwortet aus
   dem Gemerkten; die Farbregel wird nicht wiederholt. Ein Paar
   `(Farbe, Deep)`, nach dem nie gefragt wurde, ist ein `KeyError` und keine
   leere Liste.

**`ResultCache`** (LRU, 32 nach AD-007). Schluessel ist
`dataclasses.replace(request, generation=0)`; ein Treffer kommt mit der
Generation **der Frage** zurueck, nicht mit der des Laufs, der ihn erzeugt
hat - sonst verwuerfe der Controller die Antwort, die er gerade geholt hat.

**Abbruch:** gefragt wird zwischen Vorsortierung und Suche und innerhalb der
Suche zwischen den Slot-Ebenen. Die Vorsortierung wird **nicht** zerteilt.
Begruendung mit Zahl: auf dem schlimmsten echten Fall kostet sie **43 ms von
960 ms** (`scripts/measure_advisor_search.py`, Median aus drei: pre-sort
43,0 ms, beam 916,2 ms, 3621 Bewertungen) - ein Fuenftel der 200 ms aus
AK-11. Die Zeit steckt in der Suche.

### 3.3 `advisor/worker.py`: der Thread (`c824127`)

- `_Worker(QObject)` + `AdvisorController(QObject)`, `moveToThread` nach dem
  Muster aus `firstrun.ensure_data`, **ohne** dessen
  `while not thread.wait(50): processEvents()`-Schleife.
- Signale des Controllers: `ready(object)`, `failed(str)`, `started()`,
  `stopped()`. Signale des Workers: `ready`, `failed`, `finished`.
- `ask(request, inventory, ctx)` fuellt **zwei** Felder der Anfrage selbst -
  Generation und Fingerabdruck -, weil beide nichts darueber sagen, *was*
  gefragt ist, sondern ueber *dieses* Fragen, und das Fenster sie nicht
  wissen kann. Alles andere prueft `run.run` gegen den Kontext.
- Entprellung: `QTimer`, `setSingleShot(True)`, `DEBOUNCE_MS = 250`
  (AD-006 Punkt 5; der `performance-tuner` setzt den Wert in S11).
- Hoechstens ein Lauf: eine neue Frage unterbricht die alte und erhoeht die
  Generation; ein neuer `QThread` entsteht erst, wenn der alte `finished`
  gemeldet hat. Kein `terminate()`, kein `wait()` im Hauptthread - ausser in
  `shutdown()`, das ausdruecklich fuer das schliessende Fenster da ist.
- `before_the_data_changes()` (AD-006 Punkt 7, Risiko F4): bricht ab, erhoeht
  die Generation, leert den Cache - **vor** einem erneuten
  `model.configure()`.
- Ueberholte Antworten werden in `_on_ready` **wortlos** verworfen; vorher
  aber in den Cache gelegt, denn sie beantworten die Frage, unter der sie
  abgelegt werden, richtig - und das Hin- und Herwechseln ist genau der Fall,
  fuer den AD-007 existiert.

### 3.4 `UI_SPEC.md`: `Suggest` → `Optimize` (`bafc3e1`)

Elf Stellen: §3.1 (Leistenskizze und die Knopfzeile), Zustandstabelle 4.1,
4.3, 4.7, 4.8, §5 Punkte 1 und 7, AK-10, AK-13 (zweimal im Satz), AK-25.
**Nicht** angefasst: F4 (Name der Karte), der T-024-Nachtrag und §5.1 - die
halten den Umbenennungsvorgang fest und muessen ihn nennen koennen.

## 4. Die Abnahmezahlen

Skript: `scripts/measure_advisor_worker.py` (Commit `792318a`), Lauf vom
07.09.2026. Umgebung in jeder Ausgabe: Windows-10-10.0.19045-SP0, Python
3.12.10 (CPython), `data_version 10350000`, 309 Relikte im Save, Wylder auf
Level 15, `max_damage`, K=20 W=40.

### Erste Stichprobe - der synthetische Fall

4 eigene Kopien einer Farbe, 2 freie Slots, nichts gehalten:

| | |
|---|---|
| ganzer Lauf durch den Controller | **4,7 ms**, 6 Vorschlaege, 35 Bewertungen |
| Fenster erfaehrt den Abbruch | Median **0,02 ms**, min 0,02, max 0,04, sd 0,01, n=10 |
| Arbeiter danach | nichts mehr bewertet - der Lauf war schon fertig, n=10 |

Die zweite Zeile ist ehrlich uninteressant: bei 4,7 ms ist alles vorbei,
bevor der Abbruch kommt. Genau deshalb gibt es die zweite Stichprobe.

### Zweite Stichprobe - der echte Spielstand

309 Relikte, `Wylder's Chalice` `[0, 2, 4]` + Deep `[0, 1, 3]`, sechs freie
Slots, nichts gehalten:

| | |
|---|---|
| ganzer Lauf durch den Controller | **954,4 ms**, 40 Vorschlaege, 4513 Bewertungen |
| Herzschlag des Hauptthreads (10-ms-Timer) | **87 Ausloesungen, 86 davon waehrend** der Lauf zwischen seiner ersten und seiner letzten Bewertung war |
| Abbruch 100 ms in den Lauf: Fenster erfaehrt es | Median **0,06 ms**, min 0,05, max 16,26, sd 6,24, n=10 |
| Abbruch 100 ms: letzte Bewertung des Arbeiters danach | Median **87,56 ms**, min 74,85, max 102,41, sd 8,18, n=10 |
| Abbruch 500 ms in den Lauf: Fenster erfaehrt es | Median **0,06 ms**, min 0,04, max 22,76, sd 8,00, n=10 |
| Abbruch 500 ms: letzte Bewertung des Arbeiters danach | Median **64,48 ms**, min 43,15, max 77,32, sd 8,64, n=10 |

**Zur AK-11-Zahl:** AK-11 misst „vom Klick bis sichtbar in Zustand 4.5, auch
wenn der Arbeiter laenger zum Beenden braucht". Das ist die Zeile „Fenster
erfaehrt es": **schlimmster gemessener Einzelwert 22,76 ms von 200 ms
erlaubten**, ueber 40 Abbrueche in zwei Momenten. Die Ausreisser (16-23 ms
gegen einen Median von 0,06 ms) liegen in der Messschleife selbst
(Ereignisverarbeitung unmittelbar davor), nicht im Controller: `cancel()`
sendet `stopped` in demselben Aufruf, direkt verbunden.

**Zur Stelle, an der die Suche nachsieht** (der Auftrag verlangt sie
ausdruecklich): zwischen den Slot-Ebenen in `search.beam` (unveraendert seit
S7, AD-003 Punkt 4) und zusaetzlich zwischen Vorsortierung und Suche in
`run.run`. Warum das reicht: der Arbeiter hoerte in 20 von 20 Messungen
zwischen **43 ms und 103 ms** nach dem Abbruch auf zu rechnen - unter der
200-ms-Schranke, obwohl AK-11 das gar nicht von ihm verlangt. Die
Vorsortierung bleibt ungeteilt, weil sie 43 ms von 960 ms kostet.

**Das Fenster bleibt bedienbar** ist hier eine Zahl: 86 von 87
Timer-Ausloesungen des Hauptthreads fielen **in** den Lauf. Haette der Lauf
den Hauptthread gehalten, waeren sie alle danach gekommen.

### Der Cache: byte-identisch, mit Nenner

`test_a_hit_is_what_a_fresh_run_would_have_said` ist ueber **zwei
Zielrichtungen x beide Deep-Stellungen = 4 Kombinationen** parametrisiert.
Verglichen wird der Treffer nicht mit dem abgelegten Objekt, sondern mit
einem **frischen** Lauf derselben Frage - `==` und zusaetzlich `repr()`,
damit ein Gleitkommawert, den nur eine Seite gerundet haette, auffaellt. Der
Nenner steht daneben und ist selbst gepruefte Zusicherung
(`test_all_four_combinations_of_direction_and_deep_are_covered`: 4
Kombinationen, und `set(goals.GOALS) == {max_damage, min_damage_taken}` -
kommt eine dritte Richtung dazu, wird der Fall rot statt still unvollstaendig).

## 5. Rot-vorher: 15 Gegenbauten, jeder einzeln gefahren

Alle in `scripts/differential/mutate.py` registriert (Ankerprobe:
`test_every_mutation_still_finds_its_anchor_in_the_real_source`, 222 passed).
Verfahren: Arbeitsbaum ohne `.git` in ein Scratch-Verzeichnis kopiert,
Mutation ueber `mutate.py --apply` eingespielt, `pytest -q -m "not slow"`
ueber die betroffenen Dateien, `PYTHONHASHSEED=0`. **Alle 15 sterben im
Standardlauf**, und keiner stirbt nur an der Ankerprobe - die Ankerprobe lief
in diesen Laeufen gar nicht mit.

| Gegenbau | toetender Fall |
|---|---|
| `search-takes-pools-ranked-by-another-direction` | `test_pools_ranked_by_another_direction_are_refused` |
| `search-refuses-every-pairing-of-pools-and-scorer` | `test_pools_and_scorer_of_one_direction_are_accepted` (+23 weitere) |
| `advisor-pool-does-not-say-what-ranked-it` | `test_a_pool_says_which_direction_put_it_in_this_order`, `test_the_search_ranks_by_the_scorer_it_is_handed` |
| `advisor-run-takes-a-request-about-another-run` | `test_a_request_that_describes_another_run_is_refused` (7 Felder) |
| `advisor-run-walks-into-the-search-after-a-stop` | `test_a_run_stopped_before_the_search_says_so`, `..._asks_once_between_the_pre_sort_and_the_search` |
| `advisor-run-explains-only-the-best-suggestion` | `test_every_suggestion_carries_its_reasons_and_not_only_the_first` |
| `advisor-gain-against-the-empty-build` | `test_the_gain_is_the_difference_to_the_build_as_it_stands` |
| `advisor-cache-key-keeps-the-generation` | `test_the_generation_is_not_part_of_the_question` |
| `advisor-cache-key-forgets-the-held-state` | `test_a_question_that_differs_in_which_slot_is_held_misses` |
| `advisor-cache-hands-back-a-stale-generation` | `test_the_generation_is_not_part_of_the_question` |
| `advisor-snapshot-decides-the-colour-rule-itself` | `test_the_snapshot_asks_the_inventory_what_fits_and_does_not_decide_it` |
| `advisor-fingerprint-without-the-handle` | `test_the_fingerprint_changes_when_a_copy_gets_another_handle` |
| `advisor-controller-shows-an-overtaken-answer` | `test_an_overtaken_answer_never_reaches_the_window`, `test_a_cancelled_run_never_answers_even_if_it_finishes` |
| `advisor-controller-waits-for-the-worker-before-it-says-it-stopped` | `test_cancel_is_visible_at_once_however_long_the_worker_takes` |
| `advisor-controller-answers-every-keystroke` | `test_a_burst_of_questions_is_one_run` |
| `advisor-controller-runs-in-the-main-thread` | `test_the_run_happens_in_another_thread_...` (+5 weitere) |
| `advisor-controller-keeps-the-answers-through-a-data-rebuild` | `test_a_data_rebuild_stops_the_run_and_forgets_every_answer` |
| `advisor-controller-forgets-what-it-has-worked-out` | `test_a_question_already_answered_is_not_computed_again` |

**Der veraltete Cachetreffer, den der Auftrag ausdruecklich verlangt**, ist
`advisor-cache-key-forgets-the-held-state`: der Schluessel vergisst den
Haltezustand, eine Frage mit gehaltenem Slot trifft die Antwort der Frage
ohne ihn - und die Antwort traegt Slotnummern und Handles, wuerde also einen
bewusst gehaltenen Slot ueberschreiben. Rot.

### Zwei Gegenbauten haben den ersten Lauf ueberlebt - das ist ein Befund

L-008 (c). Beide betrafen **meine eigenen** Faelle, beide sind nachgebessert
und beide sterben jetzt; ich melde sie, statt sie stillschweigend zu
reparieren:

1. **`advisor-controller-waits-for-the-worker-before-it-says-it-stopped`
   ueberlebte**, weil mein AK-11-Fall auf einem synthetischen Lauf mass, der
   ohnehin in Millisekunden endet: `thread.wait()` vor dem Signal fiel unter
   200 ms und der Fall blieb gruen. Die Zeit allein belegt nichts. Der Fall
   prueft jetzt zusaetzlich **mechanismusgebunden**, dass der Arbeiter nach
   dem Signal noch gerechnet hat (Bewertungen nach dem `stopped`) - das ist
   die Haelfte, die AK-11 mit „auch wenn der Arbeiter laenger braucht" meint,
   und sie kann nicht durch eine schnelle Maschine erfuellt werden.
2. **`advisor-controller-answers-every-keystroke` ueberlebte**, weil fuenf
   `ask`-Aufrufe in einer Schleife **ohne dazwischenliegende
   Ereignisschleife** keine Salve sind: der Timer feuert erst beim naechsten
   Durchlauf, also lief auch ohne Entprellung nur ein Lauf. Ein Schieberegler
   schickt seine Schritte durch dieselbe Schleife, in der der Timer wartet.
   Der Fall dreht die Schleife jetzt zwischen den Fragen (5 x 5 ms bei 100 ms
   Entprellung) und prueft ausserdem, dass die Salve wirklich kuerzer war als
   die Entprellung - sonst sagte er nichts.

Beide Male war die Suite gruen und der Fall belegte nicht, was sein Name
sagt. Gefunden hat es der Mutationslauf, nicht die gruene Suite.

### Zwei Faelle, die die Ordnung herstellen mussten, statt sie zu hoffen

`test_an_overtaken_answer_never_reaches_the_window` und
`test_a_cancelled_run_never_answers_even_if_it_finishes` waren in ihrer
ersten Fassung blind: ein unterbrochener Lauf antwortet ohnehin nicht, also
haetten sie die Unterbrechung geprueft und den Generationszaehler gemeint -
und `advisor-controller-shows-an-overtaken-answer` haette ueberlebt. Beide
lassen den Lauf jetzt zuerst **hinter seine letzte Abbruchpruefung** laufen
(gezaehlt: `scorings_of(question)` misst, wie viele Bewertungen die Frage
kostet) und halten dabei die Ereignisschleife an, damit die fertige Antwort
in der Warteschlange steht, wenn die naechste Frage sie ueberholt. Das ist
genau die Verschraenkung, fuer die AD-006 Punkt 3 geschrieben ist.

## 6. Annahmen

1. **Cache-Schluessel = `AdvisorRequest` ohne `generation`.** AD-016/D3 sagt
   „der Schluessel ist der `AdvisorRequest`", und AD-006.3 legt die Generation
   in dieselbe Klasse. Beides zusammen waere ein toter Cache. Ich habe die
   Generation herausgenommen und das im Docstring von `cache_key` begruendet.
2. **`inventory_fingerprint` wird hier gebaut.** Es gab keine solche Funktion
   im Repo (geprueft: Volltextsuche nach `fingerprint` und nach
   `inventory_fingerprint`, nur Docstrings und der geloeschte
   `held_fingerprint`). Ohne sie ist „ueber Bestand" im Schluessel leer.
   Rezept aus AD-007 **mit** Handle. Sie liegt in `run.py`, nicht in
   `inventory.py`, damit `advisor/` weiterhin nichts aus dem Save-Leser
   importiert.
3. **Jeder Vorschlag bekommt seine Begruendung**, nicht nur der beste.
   `Suggestion.reasons` ist ein Feld je Vorschlag; ein Beam, dessen Kopf
   begruendet ist und dessen Rest nicht, waere eine Form mit zwei
   Bedeutungen. Kosten gemessen: der ganze Lauf inkl. 40 Begruendungen
   954 ms gegen 960 ms fuer Vorsortierung + Suche allein - im Rauschen.
4. **Die Einzelfelder des Ergebnisses gehoeren dem besten Vorschlag**
   (`gain`, `curses`, `not_counted`, die beiden stummen Listen). `Apply all`
   wendet den ersten an. `baseline` und `gain` tragen je einen Eintrag pro
   Richtung, wie `SlotPool.baseline` es tut.
5. **`budget_note` bleibt leer.** AD-010 fordert das Feld, aber den Satz
   dafuer gibt es nirgends (geprueft: `budget_note` und „Best found" in
   `UI_SPEC.md` - keine Fundstelle im Wortlautteil). Wortlaut ist Sache des
   `ui-ux-designer`; ein Lauf, der sich einen ausdenkt, schreibt Text auf den
   Schirm, den niemand entschieden hat. Siehe Punkt 8.
6. **Kein `progress`-Signal**, gegen AD-006 Punkt 1. Begruendung im
   Modul-Docstring und unten in Punkt 8.

## 7. An den qa-engineer

- **Wo die Zahlen herkommen:** `scripts/measure_advisor_worker.py` (Abbruch,
  Herzschlag, beide Stichproben) und `scripts/measure_advisor_search.py`
  (Aufteilung Vorsortierung/Suche). Beide lesen den Save nur.
- **Was ich nicht geprueft habe und was zu pruefen ist:**
  - **Das Fenster selbst.** S9 ist nirgends an `app.py` angebunden - das ist
    S10. Meine A6-Zahl ist der Herzschlag der Ereignisschleife des
    Hauptthreads, nicht das gezeichnete Fenster. AK-08 (kein Bedienelement
    deaktiviert, kein modaler Dialog, kein Wartecursor) ist erst nach S10
    pruefbar.
  - **AK-11 am Knopf.** Ich habe vom Aufruf `cancel()` bis zum Signal
    gemessen. Vom Klick bis zum gezeichneten Zustandswechsel kommt die
    Zeichenzeit des Fensters dazu.
  - Kanten, die ich fuer wahrscheinlich halte: Frage stellen waehrend ein
    Datenneuaufbau laeuft; `shutdown()` waehrend eines Laufs (Fenster
    schliessen); zwei Fragen, deren zweite ein Cachetreffer ist, waehrend die
    erste noch rechnet; ein Save ohne lesbare Handle-Tabelle (jede Kopie ohne
    Handle - der Fingerabdruck traegt sie, angeboten werden sie nicht).
  - **Der Fall „jeder Slot gehalten"**: `beam` liefert dann einen Vorschlag
    mit null Slots, `run.run` gibt ein Ergebnis mit `unknowns`-Haltezeile
    zurueck. Gedeckt in `test_advisor_search.py`, aber nicht durch den
    Controller gefahren.
- **Was ich absichtlich nicht getan habe:** kein Bildnachweis (NH-002), kein
  Start des Fensters - es gibt nichts zu sehen, S9 zeichnet nichts.

## 8. An den director

**Befunde und Entscheidungen, die nicht mir gehoeren** (ohne Nummern, wie
verlangt):

1. **`AdvisorResult.budget_note` hat keinen Wortlaut.** AD-010 zaehlt es zur
   Pflichtinhaltsliste („Suchbreite und ob der Lauf abgeschnitten wurde"),
   `UI_SPEC` nennt an keiner Stelle einen Satz dafuer. Das Feld bleibt leer.
   **Zustaendig: `ui-ux-designer`**, am besten im S10-Review, da es dort
   gezeichnet wuerde. Fundstelle: `nrplanner/advisor/run.py`, Ende von
   `run()`; Modul-Docstring nennt die Luecke.
2. **Kein `progress`-Signal, gegen AD-006 Punkt 1.** Der Fortschrittsbalken
   der Advisor bar ist laut `UI_SPEC` §3.1 unbestimmt (`setRange(0, 0)`), und
   die Zahlen aus 4.4 („292 relics, 6 slots") stehen vor dem Lauf fest und
   sind die des Fensters. Ein Signal, dessen Zahlen nichts zeichnet, koennte
   nichts bedeuten (L-003). Ich habe es weggelassen und im Docstring von
   `worker.py` benannt. **Falls der `director` es trotzdem will**, braucht es
   einen Haken in `search.beam` (je Ebene) - ein Eingriff in S7-Code, den ich
   ohne Auftrag nicht gemacht habe.
3. **Eine Aenderung an Nutzertext in `UI_SPEC.md`**, die ich fuer noetig
   hielt und die dem `ui-ux-designer` zur Bestaetigung gehoert: die
   Statuszeile aus 4.7 heisst jetzt `Your build changed while this was
   working out. Optimize again.` (vorher `Suggest again.`). Sie verweist den
   Spieler auf einen Knopf; der Knopf heisst `Optimize`. Alles andere an der
   Korrektur war reine Bezeichnung.
4. **Offene Frage 3 im T-080-Nachtrag ist jetzt teilweise falsch**
   (`UI_SPEC.md` Zeile ~3723): „Die Zustandstabelle 4.1-4.14 und mehrere AK
   sprechen noch vom Knopf `Suggest`" - das stimmt seit `bafc3e1` nicht mehr.
   Die Frage selbst gehoert dem `ui-ux-designer`; ich habe sie nicht
   angefasst, weil der Auftrag genau eine Aenderung an `UI_SPEC.md` erlaubt.
5. **QA-105, letzter Punkt, bleibt offen und ist jetzt sichtbarer:**
   „`pools` prueft `rank_by` ohne freie Slots nicht". `candidates.pools` mit
   null freien Slots ruft `pool` nie auf, also prueft nichts, ob `rank_by`
   ueberhaupt eine bekannte Richtung ist. Mit D-4 faellt das nicht mehr
   auf - die Pools sind leer, also hat `beam` nichts zu vergleichen. Kein
   Blocker (der Lauf ist dann ohnehin „alles gehalten"), aber ein eigener
   kleiner Auftrag. **Nicht behoben**, weil ausserhalb des Auftrags.
6. **Bestehende Debt, die mir aufgefallen ist, unangetastet:** `model.py`
   haelt veraenderlichen Modulzustand (Risiko F4 in `ARCHITECTURE.md`).
   `before_the_data_changes()` entschaerft es fuer den Berater, behebt es
   aber nicht: solange `model.configure` Modulglobals fuellt, ist jede
   Nebenlaeufigkeit auf `model` eine Absprache statt einer Eigenschaft. Der
   saubere Weg (Konfigurationsobjekt statt Globals) ist laut F4 ein eigener
   Auftrag, und ich stimme dem zu.
7. **Performance-Fund fuer S11 / `performance-tuner`, nicht selbst
   optimiert:** die Suche ist **916 ms von 960 ms** und macht 3621 der 4513
   Bewertungen eines Laufs; die Vorsortierung kostet 43 ms. D-1 nennt
   `model.compute` als 94 % - das deckt sich, aber die Aufrufe kommen fast
   alle aus dem Beam, nicht aus der Vorsortierung. Wer das Budget setzt,
   sollte an K und W drehen, bevor er an `compute` denkt: `Ebenen x W x K`
   ist die Formel, und W=40 Endzustaende werden alle begruendet, obwohl das
   Fenster einen zeichnet.
8. **Sicherheit:** nichts gefunden. Der Worker oeffnet nichts, schreibt
   nichts, und `failed(str)` traegt `str(exc)` - dieselbe Praxis wie
   `firstrun`. Der Stacktrace geht nach stderr, nicht in das Signal. **Fuer
   S10 wichtig:** dieser Text darf nicht ungefiltert als HTML gezeichnet
   werden (D-10 nennt `html.escape` bereits fuer den S10-Auftrag).

## 9. Was offen ist - der naechste Schritt

**Genau eine Sache: der volle Suitenlauf.** Reihenfolge fuer den naechsten
Lauf:

1. `.venv\Scripts\python.exe -m pytest -q -m "not slow"` im Arbeitsbaum.
   Erwartung `1056 passed, 9 skipped, 5 deselected` (Herleitung in
   Abschnitt 1). Weicht die Zahl ab, ist die Differenz die Nachricht.
2. Frischer Klon (`git clone . <tmp>`, mit dem `python.exe` des
   Arbeitsbaums, weil der Klon kein `.venv` hat), derselbe Befehl, dieselbe
   Erwartung. Das ist die Zahl, die zaehlt.
3. Erst danach ist S9 abnahmefaehig; alles andere aus dem Auftrag ist
   erledigt und committet.

Der Arbeitsbaum ist sauber (`git status` leer), HEAD ist `c609e87`. Es liegt
nichts Uncommittetes herum.

---

## Nachtrag des Directors, 07.09.2026 — der fehlende Suitenlauf

Der `developer` kam nicht mehr dazu; ich habe ihn gefahren. Frischer Klon
(`git archive HEAD | tar -x`) vom Stand `5fa50c1`:

```
1059 passed, 9 skipped, 5 deselected in 447.65s (0:07:27)
```

**Die Erwartung im Bericht lautete 1056.** Es sind **drei mehr**. Alle gruen,
also kein Defekt — aber die Herleitung im Bericht traf nicht zu, und das
gehoert hingeschrieben statt geglaettet. Wer die Zahl das naechste Mal
herleitet, rechnet gegen 1059, nicht gegen die Herleitung.

**STATUS ist damit `erledigt`.**
