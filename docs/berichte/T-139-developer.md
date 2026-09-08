# T-139 - Die Reste aus U10, und die Mutationen ins Register (developer)

```
STATUS: erledigt
AUFTRAG: T-139 - Die Reste aus U10, und die Mutationen ins Register
GELESEN: docs/tasks/T-139.md; ARCHITECTURE.md Nachtrag X (X-0 bis X-3, U-Tabelle
  U9/U10) und die Zeigerstellen 1547/1835/3985/4385/4875; docs/berichte/
  T-131-developer.md, T-133-developer.md, T-136-developer.md,
  T-137-developer.md; tests/test_picker_track_guards.py, tests/test_one_build.py
  (call_sites/_local_names), tests/test_differential_track.py,
  scripts/differential/mutate.py; nrplanner/advisor/worker.py, nrplanner/app.py,
  nrplanner/advisor/run.py, nrplanner/paths.py, nrplanner/favourites.py,
  nrplanner/shortcut.py; die vier Kampagnentreiber der Vorauftraege im
  Scratchpad dieser Sitzung (T-131/campaign.py, T-133/mutate.py,
  T-136/mutate.py, T-137/mutate_t137.py)
GEÄNDERT: tests/test_picker_track_guards.py, scripts/differential/mutate.py
  (beide committet: 87d063e, 95e1c4e), docs/berichte/T-139-developer.md
ANNAHMEN: 1. Die vier Zeilen von AD-028 W9 sind Methodennamen, nicht
  Zeilennummern - X-2 nennt Zeilen (309/334/354/380), die durch U9 gewandert
  sind (heute 324/349/369/410); eine Tabelle auf Zeilennummern waere bei jedem
  Einrueckungswechsel rot. 2. U10 ist als ein Schritt committet (zwei Commits:
  U10 selbst, Registrierung getrennt) - Aufgabe 1 und 2 stehen in einer Datei
  und in derselben Tabelle der Architektur.
NÄCHSTER: director
BLOCKIERT DURCH: nichts
```

## Umgesetzt

**1. AD-028 W9, der Struktur-Waechter aus X-2**
(`tests/test_picker_track_guards.py`, Abschnitt „W9", Commit `87d063e`):

- `INTERRUPTING_PLACES` - vier Zeilen, Methodenname → was die abgehende Frage
  hoert, mit Begruendung; die vier Zusagen als benannte Konstanten
  (`STOPPED_IN_THE_SAME_CALL`, `THE_SUCCESSOR_QUESTION_WILL_ANSWER`,
  `THE_RETURN_VALUE_ALREADY_ANSWERED`, `NOTHING_HERE_AND_NOTHING_AFTER`).
- `places_that_interrupt_a_running_worker()` liest die Aufrufstellen von
  `_interrupt_the_running_worker` **ueber den ganzen Syntaxbaum** von
  `worker.py`, nicht nur ueber `AdvisorController`: eine Stelle in einer
  zweiten Klasse, in einer Modulfunktion oder in einer verschachtelten
  Funktion unterbricht genauso, und ein Lauf, der nur die eine Klasse kennt,
  meldete die Tabelle als gehalten. Verschachtelte Funktionen zaehlen unter
  ihrem eigenen Namen (`_named_scopes`/`_calls_of_this_scope`), damit keine
  Stelle doppelt gezaehlt wird.
- `test_w9_every_interrupting_place_has_a_row_and_every_row_a_place`:
  Mengengleichheit in beide Richtungen, Zaehlstand in der Fehlermeldung.
- **Die Zeilen nachgeprueft, wie beauftragt:** X-2 zaehlt am Stand `0128971`
  die Zeilen 309/334/354/380 (Definition 387). Heute stehen dieselben vier
  Stellen in `ask_and_answer_if_known` (324), `_wait_for` (349), `cancel`
  (369) und `shutdown` (410), Definition 417 - U9 hat die Datei um 15 bis 16
  Zeilen verschoben, es sind unveraendert **vier**.

**2. Die zwei uebrigen U10-Teile** (dieselbe Datei, derselbe Commit):

- **`candidates.pools` → `nrplanner/advisor/run.py`** als vierte Zeile in
  `MAY_REACH_THE_CALCULATION` (X-3 Fassung 2). Gemessen: der Name steht heute
  genau einmal unter `nrplanner/`, in `advisor/run.py:379` innerhalb von
  `run.run`. Die Nennung in `advisor/search.py:297` steht in einem Docstring
  und ist fuer `call_sites` kein Knoten - das ist der Grund, warum der
  Waechter am Syntaxbaum haengt und nicht an einer Textsuche.
- **Die Randbedingung im Docstring der Tabelle** (X-3, letzter Absatz): W1
  haengt an `test_one_build.call_sites` und damit an Modulkurzname plus
  Funktionsname; eine Rechnung, die unter einem **anderen** Namen in den
  Hauptthread kaeme (etwa ein direkter Griff in `search`), sieht er nicht.
  Als Grenze geschrieben, nicht als Luecke.
- Folgeaenderung: `test_w1_the_picker_holds_none_of_the_three` heisst jetzt
  `..._none_of_the_four` und erwartet vier Nullen statt drei.
- **Mehr stand in der U10-Zeile nicht.** Die Zeile lautet vollstaendig: „W8
  neu (X-2, Tabelle der vier unterbrechenden Stellen, beide Mutationen); W1
  um die Zeile `candidates.pools` → `advisor/run.py` erweitert (X-3.3) und um
  die Randbedingung im Docstring der Tabelle (X-3, letzter Absatz)." Der
  erste Teil ist der Waechter aus Aufgabe 1 (heute AD-028 W9), die anderen
  zwei sind Aufgabe 2. Nichts Drittes.

**Benennung, wie entschieden:** im Modul-Docstring steht jetzt der Absatz, dass
`AD-019 W0-W6` und `AD-028 W1-W9` zwei Reihen sind, dass keine umbenannt wird
und dass jede Nennung ihre Herkunft traegt. Alle W-Nennungen im neuen Code
lauten `AD-028 W…`.

**3. Die Mutationen ins Register** (`scripts/differential/mutate.py`, Commit
`95e1c4e`): **36 nachgetragen**, alle 36 heute erneut gefahren. Dazu die
**drei neuen** aus Aufgabe 1 und 2, die im U10-Commit stehen. Register jetzt
**232** Eintraege (vorher 193).

## Woher die Texte kommen - und was am Auftrag nicht stimmte

Der Auftrag sagt, die Mutationen stuenden „woertlich in den Berichten". **Das
stimmt nur fuer T-131.** T-133, T-136 und T-137 nennen in ihren Berichten
Prosa („M1 Ausrichtungspruefung entfernt") und verweisen auf einen Treiber im
Scratchpad. Ich habe die vier Treiber im Scratchpad **dieser** Sitzung
gefunden (`…/scratchpad/T-131/campaign.py`, `T-133/mutate.py`,
`T-136/mutate.py`, `T-137/mutate_t137.py`) und Pfad, `old` und `new` daraus
woertlich uebernommen - kein Nachbau, kein Erraten. Waeren sie geloescht
gewesen (der Scratchpad ist pro Sitzung, und ein anderer Lauf haette sie
raeumen koennen), waeren 29 der 36 nicht wiederherstellbar gewesen, sondern
nur neu erfindbar. **Mit diesem Commit haengen sie nicht mehr am Scratchpad.**

**Jeder Anker matcht im heutigen Stand genau einmal** - vor dem Schreiben
geprueft, 38 von 38, obwohl U9 `worker.py` bewegt hat. **Keine Mutation traegt
nicht mehr**; es gibt an dieser Stelle also keinen Befund zu melden.

## Nachweise

### Die drei Umlenkungen, mit Positivkontrolle

Ein Skript, das `paths.cache_dir()`, `shortcut.shortcut_path()` und
`favourites.ORG` druckt, zweimal gefahren (`…/scratchpad/T-139/where.py`):

```
=== ohne Umlenkung (Positivkontrolle)
cache_dir   : C:\Users\Daniel\AppData\Local\NightreignHelper
shortcut    : C:\Users\Daniel\AppData\Roaming\Microsoft\Windows\Start Menu\
              Programs\Nightreign Helper.lnk
settings ORG: DankYeeter / APP: NightreignHelper
=== mit Umlenkung
cache_dir   : …\scratchpad\T-139\local\NightreignHelper
shortcut    : …\scratchpad\T-139\appdata\Microsoft\Windows\Start Menu\
              Programs\Nightreign Helper.lnk
settings ORG: DankYeeterT-139 / APP: NightreignHelper
```

Die erste Haelfte ist die Positivkontrolle: sie zeigt, dass die Messung
wirklich auf den Platz des Spielers zeigt, wenn nichts umlenkt. **Alle drei
Variablen waren in jedem Test- und Kampagnenlauf gesetzt**
(`NIGHTREIGN_SETTINGS_ORG=DankYeeterT-139`, `LOCALAPPDATA` und `APPDATA` auf
`…/scratchpad/T-139/{local,appdata}`).

Fester Testabzug hineinkopiert statt daraufgezeigt: 841 Dateien, 22 MB in
`…/T-139/local/NightreignHelper` - `EXTRACT_VERSION` unveraendert, der Abzug
bleibt gueltig.

**Nachkontrolle des echten Bestands:** unter
`%LOCALAPPDATA%\NightreignHelper` ist heute **keine** Datei geaendert worden
(`find … -newermt "2026-09-08 00:00"`, leer); im echten Start-Menue steht
**keine** heute geaenderte Verknuepfung; `HKCU\Software\DankYeeterT-139`
existiert **nicht** (`reg query … -s`, leer) - unter `pytest` setzt
`tests/conftest.py` die Org ohnehin auf `DankYeeterTests` und die App auf
`NightreignHelperTests-<pid>`, mein eigener Wert kam also nur in den
Nicht-pytest-Laeufen zum Tragen; beides ist vom Speicher des Spielers weg.

### Mutationsbeweis fuer die drei neuen Waechterteile

Kopie des Arbeitsbaums (`tar`, `nrplanner nrdata tests scripts pytest.ini
run.py`), je Mutation ein frischer Baum, `PYTHONDONTWRITEBYTECODE=1`,
`-p no:cacheprovider`, angewandt ueber `mutate.py --apply --tree` - also
ueber das Register selbst, nicht ueber einen Privattreiber. Datei vorher
gruen: **24 passed**.

| Mutation | rot geworden ist |
|---|---|
| `a-fifth-place-interrupts-the-run` (`before_the_data_changes` unterbricht zusaetzlich) | 1 von 24: `test_w9_…_has_a_row_and_every_row_a_place` |
| `cancel-interrupts-nothing-and-still-says-stopped` (Aufruf in `cancel` entfernt) | 1 von 24: derselbe Fall |
| `the-window-holds-the-refused-warm-up` (`candidates.pools` in `app.py` genannt) | 1 von 24: `test_w1_…_reaches_the_calculation[candidates-pools]` |

**Keine hat ueberlebt**, und keine hat ausser ihrem Ziel etwas mitgerissen.

**Das Ergebnis, das ich nicht verschweige, und es ist die Begruendung fuer
W9:** bei `cancel-interrupts-nothing-and-still-says-stopped` bleibt **AD-028
W6 gruen**. `stopped` geht weiter in derselben Aufrufung hinaus, die Zusage
„genau einer von drei Ausgaengen" ist also gehalten - waehrend die
Unterbrechung dahinter weg ist und der Worker nach `Cancel` den ganzen Lauf
zu Ende rechnet. Genau diese Luecke konnte „drei Aufrufer" nicht schliessen.

**Rot-vorher, je Schutzmassnahme einzeln (L-007).** Die drei Mutationen
**sind** diese Probe: jede nimmt genau eine Sache weg (eine Stelle dazu, eine
Stelle weg, eine Nennung dazu), und jede faerbt genau einen Fall rot, den
keine andere rot faerbt. Keine davon ist eine Schnittstellenverschiebung -
Signaturen, Aufrufer und Rueckgaben von `cancel`, `before_the_data_changes`
und `AdvisorController.__init__` bleiben unveraendert; der Fall bricht an der
Menge der Stellen, nicht am Importieren.

**L-008b:** die Erwartung steht als Tabelle im Test. Kein Wert wird aus
`worker.py` gerechnet, keine Zeilennummer gelesen. Ein Tippfehler im
Methodennamen `THE_INTERRUPTING_CALL` liefert die leere Menge und faellt
ebenfalls - der Waechter kann sich nicht selbst gruen messen.

**L-002/L-004:** Nachweisweg ist der Gegenbau (die zwei Mutationen aus X-2).
Bau-Konfiguration: keine noetig, es ist ein reiner pytest-Fall, den kein
Buildschalter aktiviert - das ist die Herleitung, nicht ihr Fehlen.

### Die 36 nachgetragenen Mutationen, heute gefahren

Alle ueber `mutate.py --apply --tree` in je einem frischen Baum, Ergebnis
in jeder `survival_means`-Zeile eingetragen (Datum, Zieldatei, Zahl, Namen
der fallenden Faelle).

- **T-137, acht** gegen `tests/test_picker_track_guards.py`: **acht tot**,
  Verteilung genau wie im T-137-Bericht (1/2/1/2/1/4/1/1 Faelle).
- **T-131, sieben** gegen dieselbe Datei: **sieben tot** (2/4/2/1/2/4/2). Die
  Zahlen liegen ueber denen von T-131, weil die Datei seither um W8 und W9
  gewachsen ist; `sort-by-offers-a-direction-nobody-scores` bringt heute acht
  statt vier Fehler in den Fensterfaellen (`KeyError: 'max_style'` beim Bau
  der Advisor bar) - W4 selbst faellt ohne Fenster auf seiner eigenen Zusage.
- **T-133, zwoelf** gegen `tests/test_relic_scan_prefilter.py`: **elf tot**,
  Verteilung identisch mit dem T-133-Bericht (1/4/1/1/6/7/2/1/1/9/1). Die
  zwoelfte (`the-density-limit-doubled`) ueberlebt diese Datei
  bestimmungsgemaess und faellt in `tests/test_hostile_savefile.py::
  test_one_record_more_than_the_slot_can_hold_is_a_data_error` - so gefahren,
  so eingetragen.
- **T-136, neun** gegen `tests/test_loadout_table_prefilter.py`: **sieben
  tot** (3/3/1/8/7/1/12), **zwei ueberlebend** -
  `loadout-prefilter-steps-on-by-a-word` und
  `loadout-prefilter-rebuilt-as-the-old-walk`. Beide sind mit der Begruendung
  von T-136 eingetragen, nicht weggelassen: der Marker `0x0000ff01`
  ueberlappt sich nicht selbst, deshalb liefern Schritt +1 und Schritt +4
  fuer jede Eingabe dieselbe Trefferliste; und weil `find_loadout_table`
  keinen nachgelagerten Abgleich hat, ist die einzige stille Verlangsamung
  die spezifikationsgleiche Neufassung. Ich habe nichts nachgebessert.

### Suite

```
pytest -n auto -q   ->   1398 passed, 9 skipped in 175,28 s
```

Gegen die Vorgabe **1357 passed, 9 skipped, 0 failed**: **+41**, und die Zahl
ist vorhersagbar - **2** neue Faelle in `test_picker_track_guards.py` (die
vierte W1-Parametrisierung und W9) und **39** neue Parametrisierungen von
`test_every_mutation_still_finds_its_anchor_in_the_real_source` (36 + 3
Mutationen). Skips unveraendert 9, 0 failed.

`pytest tests/test_picker_track_guards.py` einzeln (ohne `-n`, wie die
Gegenprobenregel es verlangt): **24 passed in 28,4 s**.
`pytest tests/test_differential_track.py`: **236 passed in 4,0 s**.

## Definition of Done

- [x] Anforderung verstanden, Annahmen oben dokumentiert
- [x] Build und Tests gruen auf Windows 10 x64 (Zielsystem); Linux und macOS
      sind kein Ziel und **ungeprueft**
- [x] Neue Tests fuer neue Logik, jeder mit toetender Mutation im Register
- [ ] Linter: **entfaellt** - im Projekt ist keiner konfiguriert (keine
      `.flake8`, `setup.cfg`, `ruff.toml`, `pyproject.toml`; `pytest.ini`
      konfiguriert nur Marker). Keine Ersatzpruefung, keine Luecke.
- [x] Keine Secrets, keine TODOs, kein toter Code; keine neue Abhaengigkeit
- [x] Kein Anwendungscode angefasst; die drei beauftragten Dateien und der
      Bericht, sonst nichts
- [x] Zwei atomare Commits, beide mit Pfad hinter `--`

## An den director

1. **Zaehlfehler im Auftrag, harmlos, aber er gehoert korrigiert:** T-136 hat
   **neun** Mutanten gefahren, nicht elf (Tabelle im Bericht, neun Zeilen; der
   Treiber hat neun Eintraege, die Nummerierung springt von M6 auf M9 und
   endet bei M8). Sieben tot, zwei ueberlebend. Die uebrigen Zahlen des
   Auftrags stimmen: T-131 neun (davon zwei bereits registriert -
   `picker-refresh-never-waits` und
   `picker-worker-does-not-stamp-the-generation` -, also sieben neu), T-133
   zwoelf, T-137 acht. **Summe neu: 36.**
2. **Die Berichte tragen die Mutationen nicht woertlich** (siehe oben, nur
   T-131 tut es). Wenn die Registrierung kuenftig ein eigener Auftrag bleiben
   soll, muss die Rolle, die die Kampagne faehrt, **den Anker in den Bericht
   schreiben** - sonst haengt die Wiederholbarkeit am Scratchpad, und der ist
   pro Sitzung.
3. **Prosa und Tabelle in X-2 gehen an einer Stelle auseinander** (kein
   Fehler in der Sache, aber jemand wird darueber stolpern): der Satz nennt
   **drei** erlaubte Formen (einen der drei Ausgaenge senden, eine
   Nachfolgefrage stellen, die Spur beenden), die Tabelle darunter hat eine
   **vierte** - der Cache-Treffer, der in derselben Aufrufung als
   Rueckgabewert antwortet (IX-1.3). Ich habe die Tabelle als verbindlich
   genommen und die vier Formen als vier benannte Konstanten gebaut; im
   Docstring steht, dass die Prosa drei kennt. **Vorschlag an den
   `architect`:** den Satz in X-2 um die vierte Form ergaenzen.
4. **Kein Fremd-Commit im Zeitfenster.** `git log` vor und nach meiner Arbeit:
   `148edb6` war der Stand beim Start (der Auftrag nennt `ab522d7`, seither
   liegt der T-139-Auftragscommit darauf), meine beiden Commits sind
   `87d063e` und `95e1c4e`, dazwischen nichts Fremdes. Die Zusage hat diesmal
   gehalten.
5. **Kein Sicherheitsfund.** Kein Netzwerk, keine Secrets, keine neue
   Dateizugriffsart; der Spielstand wurde nicht angefasst.
6. **Keine bestehende Debt entdeckt, die den Task blockiert hat.** Eine
   Beobachtung ohne Handlungsbedarf: das Register mutiert an genau **zwei**
   Stellen die Suite statt des Programms (`tests/conftest.py` fuer QA-146 und
   jetzt `the-table-forgets-the-return-value` aus T-137); beide sagen es an
   Ort und Stelle.
7. **Nicht gemessen, weil nicht beauftragt:** ob die 175 s der Suite gegen die
   127 s aus `CLAUDE.md` eine Verschlechterung sind. Die 39 neuen
   Anker-Faelle lesen je eine Datei und kosten zusammen unter einer Sekunde;
   die Differenz ist Maschinenlast, keine Aussage. Der
   `performance-tuner` kommt ohnehin als naechstes.

## An den qa-engineer

- **Neu zu treten:** `test_w9_every_interrupting_place_has_a_row_and_every_
  row_a_place`. Er ist ein reiner Struktur-Fall, braucht kein Fenster, keinen
  Spielstand und keine Uhr; er faellt, sobald jemand in `worker.py` eine
  fuenfte Stelle einbaut, die einen laufenden Worker unterbricht - oder eine
  der vier entfernt.
- **Der interessante Randfall fuer dich:** eine Aenderung, die `cancel` das
  Unterbrechen wegnimmt, **haelt AD-028 W6 gruen** (gemessen, s. o.). Wenn du
  explorativ am Abbrechen arbeitest: ein `Cancel`, nach dem die Oberflaeche
  sofort 4.5 sagt, sagt nichts darueber, ob der Worker wirklich aufgehoert
  hat. Der Beleg dafuer ist heute strukturell, nicht ueber die Oberflaeche.
- **W1 hat jetzt vier Zeilen statt drei.** Wer `candidates.pools` irgendwo
  unter `nrplanner/` ausserhalb von `advisor/run.py` nennt - auch nur nennt,
  ohne aufzurufen -, faerbt den Waechter rot. Das ist Absicht (IX-5s
  abgelehnte Vorwaermung).
- **Was W9 ausdruecklich nicht kann:** er sieht die Stellen, die es gibt, nie
  die Abwesenheit einer, die niemand geschrieben hat. Verhaltensproben ueber
  `cancel`/`shutdown` bleiben deine Sache.

## An den ui-ux-designer

Keine Abweichung: an der Oberflaeche wurde nichts geaendert, keine Zeichenkette
und kein Zustand. Die Meldung aus Nachtrag X zu **AK-218 Fassung 2** (der
Cache-Treffer endet im Rueckgabewert und in keinem der drei Ausgaenge) steht
weiter beim `director`; ich habe `UI_SPEC.md` nicht angefasst.
