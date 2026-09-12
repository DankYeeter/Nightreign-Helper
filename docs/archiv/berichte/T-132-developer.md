# T-132 — Zwei Skripte nachziehen (developer)

```
STATUS: erledigt
AUFTRAG: T-132 - Zwei Skripte nachziehen (developer)
GELESEN: docs/tasks/T-132.md; docs/berichte/T-128-developer.md;
  docs/berichte/T-130-developer.md; nrplanner/advisor/run.py;
  nrplanner/advisor/goals.py; nrplanner/advisor/candidates.py;
  nrplanner/advisor/worker.py; nrplanner/relicpicker.py;
  scripts/differential/mutate.py; scripts/measure_picker_cards.py;
  tests/test_advisor_slot_pool.py; tests/test_advisor_worker.py;
  tests/test_relic_picker_advisor.py (nur Testnamen und Assertions
  gelesen, nichts dort geaendert); CLAUDE.md
GEÄNDERT: scripts/differential/mutate.py (Commit 0302f41);
  scripts/measure_picker_cards.py (Commit 086bd74)
ANNAHMEN: drei, unten unter "Annahmen" einzeln begruendet
NÄCHSTER: director
BLOCKIERT DURCH: nichts
```

## Umgesetzt

### 1. Mutationen aus T-128 und T-130 nachgetragen (`scripts/differential/mutate.py`)

Elf neue Eintraege, in zwei Abschnitten ans Dateiende gehaengt (vor der
schliessenden `}`):

**T-128 (U5a, `run.slot_pool`), sechs Eintraege:**

| Name | Anker | Killed by |
|---|---|---|
| `slot-pool-asks-the-wrong-slot` | `open_slots[0].index` → `problem.slots[0].index` | 3 Faelle in test_advisor_slot_pool.py |
| `slot-pool-accepts-any-number-of-open-slots` | `if len(open_slots) != 1:` → `if False:` | 1 Fall, 2 Parameter |
| `slot-pool-skips-its-own-guard-against-another-run` | `_refuse_a_request_that_asks_about_another_run(...)` in `slot_pool` entfernt | 1 Fall |
| `slot-pool-does-not-hand-on-should-cancel` | letztes Argument `should_cancel` → `never_cancelled` | 1 Fall |
| `canonical-pool-order-names-no-goal` | `CANONICAL_POOL_ORDER = MAX_DAMAGE.id` → `"max_style"` | 2 Faelle |
| `slot-pool-is-not-qt-free` | `from PySide6 import QtCore` in `run.py` ergaenzt | 1 Fall, Kindprozess |

T-128s siebte Mutation (`base_state_for` hebt die Haltung des offenen Slots
nicht mehr auf) bekommt **keinen eigenen Eintrag**: der Anker
(`kept = tuple(entry for entry in problem.held if entry.index != slot_index)`
in `candidates.py`) ist bereits durch `advisor-ranks-the-slot-as-it-stands`
registriert — an genau dieser Zeile gibt es im ganzen Baum nur ein
Vorkommen (`grep` bestaetigt). Ein zweiter Eintrag auf denselben Anker waere
kein zusaetzlicher Nachweis.

**T-130 (U5b, Picker-Spur verdrahtet), fuenf Eintraege:**

| Name | Anker | Datei |
|---|---|---|
| `picker-reads-the-pool-s-order-instead-of-the-setting` | `_drawn_direction` gibt `self.ranking.pool.rank_by` statt `self.advice.goal_id()` | relicpicker.py |
| `picker-refresh-never-waits` | `waiting = self._waiting and self._wait_is_drawn` → `waiting = False` | relicpicker.py |
| `picker-waiting-branch-skips-the-size-fit` | `self._fit_to_three_rows(for_size)` im Wartezweig entfernt | relicpicker.py |
| `picker-mandatory-lines-wait-for-the-answer` | `if self.advice is None:` → `if self.advice is None or self.ranking is None:` in `_say_what_was_left_out` | relicpicker.py |
| `picker-worker-does-not-stamp-the-generation` | die Generations-Stempelung in `_Worker.work` entfernt | worker.py |

### Nachweis: `--apply` plus rote Fallzahl im Standardlauf

Jede Mutation frisch gegen den **aktuellen** Quellstand gemessen, nicht
gegen die Zahlen aus den alten Berichten. Baum: `git stash create` (fasst
meine uncommitteten Aenderungen an `mutate.py` zusammen, ohne den
Arbeitsbaum zu beruehren) → `git archive <stash-commit> | tar -x` in
`scratchpad/T-132/mutant` (kein `.git`, kein `ROOT` — vom Skript selbst
gegengeprueft). Je Mutation: Zieldatei nach `.orig` kopiert, `mutate.py
--apply NAME --tree <mutant>` vom **echten** Repo aus aufgerufen (nie das
`mutate.py` im mutierten Baum selbst, das waere der `ROOT`-Schutz), dann
`pytest <datei>` **ohne `-n`** im mutierten Baum — der in CLAUDE.md
benannte Standardlauf fuer eine einzeln genannte Datei — dann `.orig`
zurueckkopiert (nie `git checkout`, der mutierte Baum hat ohnehin kein
`.git`).

| Mutation | Standardlauf-Datei | rote Faelle |
|---|---|---|
| slot-pool-asks-the-wrong-slot | test_advisor_slot_pool.py | 4 failed, 7 passed |
| slot-pool-accepts-any-number-of-open-slots | test_advisor_slot_pool.py | 2 failed, 9 passed |
| slot-pool-skips-its-own-guard-against-another-run | test_advisor_slot_pool.py | 1 failed, 10 passed |
| slot-pool-does-not-hand-on-should-cancel | test_advisor_slot_pool.py | 1 failed, 10 passed |
| canonical-pool-order-names-no-goal | test_advisor_slot_pool.py | 2 failed, 9 passed |
| slot-pool-is-not-qt-free | test_advisor_slot_pool.py | 1 failed, 10 passed |
| picker-reads-the-pool-s-order-instead-of-the-setting | test_relic_picker_advisor.py | **17** failed, 37 passed |
| picker-refresh-never-waits | test_relic_picker_advisor.py | **5** failed, 49 passed |
| picker-waiting-branch-skips-the-size-fit | test_relic_picker_advisor.py | 1 failed, 53 passed |
| picker-mandatory-lines-wait-for-the-answer | test_relic_picker_advisor.py | 1 failed, 53 passed |
| picker-worker-does-not-stamp-the-generation | test_advisor_worker.py | **4** failed, 14 passed |

Kein Ueberlebender. Alle elf toeten im Standardlauf.

**Drei Zahlen weichen vom Wortlaut der alten Berichte ab** — das ist der
Befund, den der Auftrag ausdruecklich verlangt, nicht ein Passendmachen:

- `picker-reads-the-pool-s-order-instead-of-the-setting`: T-130 hatte
  "1 failed, 2 passed" notiert. Grund: `_drawn_direction` wird nicht nur von
  der Stelle gerufen, die AK-205 direkt bewacht, sondern auch aus
  `_say_what_was_left_out` und `_say_what_they_are_worth`, und `self.ranking`
  ist `None`, solange die Antwort noch aussteht. Die Mutation liest dann
  `self.ranking.pool.rank_by` auf `None` und wirft `AttributeError` — jeder
  Fall, der die Wartephase durchlaeuft, stirbt mit. Der von T-130 zitierte
  Wert stammte aus einem enger gefassten Lauf (vermutlich mit `-k`), nicht
  aus dem Standardlauf der Datei. Ich habe den `survival_means`-Text auf die
  tatsaechliche Zahl (17 von 54) umgeschrieben und den Absturz-Mechanismus
  benannt, statt nur den einen ursprünglich genannten Fall aufzufuehren.
- `picker-refresh-never-waits`: 5 statt 3 — zwei weitere Faelle
  (`test_a_closed_dialog_hears_nothing_more`,
  `test_an_opening_with_no_relic_to_offer_does_not_wait`) lesen den
  Wartezustand auf dem Weg zu einer anderen Zusicherung und fallen mit.
- `picker-worker-does-not-stamp-the-generation`: 4 statt 1 — drei weitere
  Faelle bauen auf derselben Vorrichtung auf und sehen ohne die Stempelung
  nie ein `ready`-Signal.

Die uebrigen acht Zahlen decken sich mit den Berichten von T-128/T-130.

**Positivkontrolle, dass die Registrierung selbst greift:**
`tests/test_differential_track.py` (der Waechter, der jeden Anker gegen die
**echte, unmutierte** Quelle prueft) stieg von 222 auf **233 passed** — genau
die elf neuen Faelle, nicht mehr und nicht weniger.

### 2. `scripts/measure_picker_cards.py` wartet jetzt auf die echte Antwort

**Vorher:** Das Skript oeffnete den `RelicPicker` und rief `settle(app)` —
drei feste Runden `app.processEvents()` — bevor es `findChildren(RelicCard)`
las. Seit U5b (T-130) rechnet der Picker seine Kandidaten in einem echten
`QThread` und liefert sie per Qt-Signal; bis dahin ist das Raster leer
(`dialog.waiting is True`, AK-211/AK-212). Drei feste Runden sind keine
Wartebedingung, sondern eine Annahme ueber Zeit, die nirgends geprueft
wurde.

**Nachgewiesen mit einer isolierten Probe** (derselbe Aufbau wie der Skript-
Beginn, ohne die Skriptlogik zu aendern), dreimal wiederholt, immer gleich:

```
unmittelbar nach dem Oeffnen:      waiting=True,  0 Karten
nach 1x processEvents():           waiting=True,  0 Karten
nach 2x processEvents():           waiting=False, 54 Karten
nach 3x processEvents():           waiting=False, 54 Karten
```

Im vollen Skriptlauf (mit dem Umbau von `QApplication`, Snapshot-Laden und
dem ganzen `Planner`-Fenster **vor** dem Oeffnen des Pickers) war die Antwort
zufaellig schon da, wenn das Skript zum ersten Mal las — die Wartezeit war
von der Aufbauzeit davor bereits verdeckt. Das ist die exakte Bruchstelle,
die T-130 (Befund 2) gemeldet hat: kein garantiertes Verhalten, sondern ein
Wettlauf mit einer Marge von genau einer `processEvents()`-Runde in dieser
Messung. Ein kleineres Vessel, ein kaelterer Diskcache oder eine langsamere
Maschine haetten `cards[0]` im nachfolgenden Code (Zeile 163 alt) mit
`IndexError` abbrechen lassen, weil das Skript nirgends prueft, ob `cards`
ueberhaupt etwas enthaelt, bevor es indiziert.

**Fix:** `spin(app, still_waiting, timeout)` — derselbe Wortlaut wie
`tests/test_advisor_worker.py::spin` (`while ... processEvents(...); return`)
— wartet explizit auf `not dialog.waiting` bzw. `not picker.waiting`, mit
10 s Limit (das Zehnfache des schlechtesten real gemessenen `run.run`-Falls,
960 ms, S11-C) und einer Meldung statt eines stillen Fehlschlags: `main()`
bricht mit `SystemExit` ab, `second_sample()` ueberspringt die einzelne
Oeffnung und macht mit der naechsten weiter (passend zum bestehenden Muster
fuer "kein Slot dieser Art").

**Gemessen: vorher und jetzt liefern dieselben Zahlen** — der Fix aendert
die Verlaesslichkeit des Wartens, nicht was gemessen wird:

```
54 relic cards, dialog 1024 x 800, viewport 982 x 502, grid asks 982
horizontal scrollbar: False
whole card rows visible: 1
AK-51 asks for 1174 px; this desktop offers 800
at 1174 px: viewport 876, whole card rows 3
card 190 x 264, minimum width 184
card height with '…' 173, with '+1234.5 effective HP' 173, difference 0
card height with no value block 145, minimum width 184
value block asks 138 x 31, minimum width 138, card body has 174
```

**Messumgebung (L-009):** Windows 10 x64 (Windows-10-10.0.19045-SP0), Qt-
Plugin `offscreen`, Stil `fusion`, `devicePixelRatio 1.0` — logische =
physische px. Gemessen gegen den festen Testabzug
(`C:\Users\Daniel\AppData\Local\NightreignHelper-Testabzug`), Slot 1 des
Basis-Vessels, 54 zutreffende Relikte.

`second_sample()` (vier Oeffnungen: Wylder Slot/Deep-Slot, Guardian
Slot/Deep-Slot) lieferte nach dem Fix ebenfalls dieselben Werte wie vorher
(54/27/51/23 Kandidaten) — auch hier unveraendert in der Zahl, jetzt
garantiert statt zufaellig.

## Annahmen

1. **"Standardlauf" = `pytest <datei>` ohne `-n`** (CLAUDE.md-Testbefehl fuer
   eine einzeln genannte Datei), je Mutation gegen die eine betroffene
   Testdatei gemessen — nicht die volle Suite je Mutation (elfmal `pytest
   -n auto` waere rund 30 Minuten gewesen und misst nichts, was die
   betroffene Datei nicht schon zeigt).
2. **Keine eigene Registrierung fuer T-128s siebte Mutation**
   (`base_state_for`), weil sie mit einem bereits registrierten Eintrag
   identisch ist (Begruendung oben). Falls das nicht gewuenscht ist, ist ein
   zweiter Eintrag auf denselben alten Anker ein Einzeiler.
3. **Die drei abweichenden Fallzahlen wurden nicht "passend gemacht"**,
   sondern die `survival_means`-Texte auf die tatsaechlich gemessene Zahl
   umgeschrieben (siehe Nachweis-Tabelle). Der Auftrag nennt das
   ausdruecklich als moeglichen Ausgang ("ist ein Befund, kein Anlass, sie
   passend zu machen") — ich lese das so, dass die **Zahl** im Eintrag der
   Realitaet folgt, nicht dass die Mutation deswegen verworfen wird: alle
   elf toeten weiterhin, nur teils breiter als urspruenglich notiert.

## Tests

- `tests/test_differential_track.py`: **233 passed in 3.96 s** (vorher 222,
  +11 — genau die neuen Eintraege), zweimal gelaufen (vor und nach dem
  zweiten Commit, unveraendert).
- `pytest -n auto` (volle Suite, nach dem ersten Commit, vor dem zweiten):
  **1323 passed, 9 skipped in 164,66 s**. Die Differenz zur im Auftrag
  genannten Vorgabe (1297 passed, 9 skipped) stammt **nicht** von dieser
  Aenderung: waehrend dieses Laufs hat T-131 parallel sieben eigene Waechter
  fuer die Picker-Spur committet (`05e923f`, `2f0eb8e`) — +15 Faelle, die
  nicht zu diesem Auftrag gehoeren und die ich nicht angefasst habe. Mein
  eigener Beitrag ist exakt die 11 in `test_differential_track.py`; ich habe
  das ueber `git log --oneline` zwischen meinem ersten und zweiten
  `git status`-Aufruf bestaetigt (siehe "Ausgefuehrte Befehle").
- `scripts/measure_picker_cards.py` ist **von keinem Test importiert**
  (`grep -r` nach `measure_picker` und nach `picker_cards`, zwei unabhaengig
  formulierte Suchmasken, beide null Treffer in `tests/`) — der zweite
  Commit kann die Suite folglich nicht bewegt haben; ich habe sie danach
  nicht erneut vollstaendig laufen lassen, weil kein Mechanismus existiert,
  ueber den er es koennte.
- `python -m py_compile` auf beiden geaenderten Dateien: fehlerfrei.
- Zeilenlaenge: alle von mir neu geschriebenen Zeilen ≤ 79 Zeichen ausser
  fuenf `old="""`/`new="""`-Bloecken, die Quelltext woertlich reproduzieren
  — die Datei erlaubt das ausdruecklich in ihrem eigenen Docstring
  ("the anchors below run past the margin ... they are the source
  verbatim").

## DoD

- [x] Anforderung verstanden, Annahmen dokumentiert (drei, oben)
- [x] Build & Tests gruen in der benannten Testumgebung (Windows 10 x64,
      Branch `docs/audit-and-advisor-design`)
- [x] Neue Pruefungen fuer neue Registrierungen: jede der elf Mutationen mit
      `--apply` und rotem Standardlauf belegt (Tabelle oben). **Linter:
      entfaellt** — das Projekt hat keinen konfiguriert
      (Nutzerentscheid 2026-09-06)
- [x] Keine Secrets, keine TODOs, kein toter Code
- [x] Nur die zwei genannten Skripte beruehrt; `tests/`, Anwendungscode und
      Doku unangetastet (`git status` nach beiden Commits: sauber bis auf
      die untracked Auftragsdateien des Directors)
- [x] `git commit` je Aenderung mit Pfad hinter `--`
- [x] Bericht geschrieben

**Ungeprueft:** Linux und macOS (nie Ziel dieses Projekts, CLAUDE.md). Die
Testabzug-Registry-Isolation (`DankYeeterT-132`) und die drei Scratch-
Verzeichnisse liegen unter `scratchpad/T-132/`; die Registry-Nebenwirkung
(`HKCU\Software\DankYeeterT-132`) habe ich nach der Messung entfernt
(`Remove-Item`, bestaetigt geloescht). Der reale Nutzer-Cache
(`C:\Users\Daniel\AppData\Local\NightreignHelper\nightreign_data.json`,
Aenderungsdatum 2026-09-05) ist unveraendert — geprueft mit
`Get-Item ... LastWriteTime`, nicht nur behauptet.

## An den director

- **Elf Mutationen nachgetragen, keine ausgelassen** aus den beiden
  genannten Berichten, mit einer Ausnahme (T-128s siebte, identisch mit
  einem Bestandseintrag, siehe Annahme 2).
- **T-131 ist waehrend meines Laufs gelandet** (`05e923f`,
  `2f0eb8e`) — sieben neue Waechter fuer die Picker-Spur (W1–W7 vermutlich,
  ich habe den Bericht nicht gelesen, das ist ausserhalb meines Auftrags).
  Deren Mutationen sind **nicht** in `mutate.py` — der Auftrag sagt
  ausdruecklich, dass ein spaeterer Auftrag sie nachtraegt. Die Suitezahl
  1297 aus dem Auftrag ist damit bereits ueberholt (aktuell 1323 vor meinem
  zweiten Commit); wer als naechstes die Zahl zitiert, sollte den aktuellen
  `git log` gegenpruefen statt die alte Zahl aus einem Auftrag zu
  uebernehmen.
- **Kein Sicherheitsfund, keine neue Abhaengigkeit.** `spin()` nutzt nur
  `PySide6.QtCore.QEventLoop`, bereits eine Laufzeitabhaengigkeit des
  Projekts.
- **Kleiner Fund, nicht behoben (ausserhalb des Auftrags):**
  `scripts/measure_picker_cards.py` indiziert `cards[0]` an mehreren Stellen
  ohne zu pruefen, ob die Liste leer ist (Zeile 163 alt/neu unveraendert
  durch mich). Das ist unabhaengig von Befund 2 — selbst mit garantierter
  Wartezeit crasht das Skript, wenn Slot 1 des Basis-Vessels irgendwann
  keine passenden Relikte mehr hat. War nicht Teil des Auftrags (nur das
  leere-Raster-Timing war benannt) und ich habe es nicht angefasst, um den
  Diff pruefbar zu halten. Empfehlung: eigener kleiner Auftrag, falls
  relevant.
