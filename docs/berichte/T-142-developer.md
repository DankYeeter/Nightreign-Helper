# T-142 - U8: das Lesen des Spielstands in den Hintergrund (developer)

```
STATUS: erledigt
AUFTRAG: T-142 - U8 / AD-029 Stufe B: inventory.load in einen Worker
GELESEN: docs/tasks/T-142.md - UI_SPEC.md Abschnitt T-141 vollstaendig
  (§0 bis §14, AK-220 bis AK-229) - ARCHITECTURE.md AD-029 vollstaendig -
  nrplanner/advisor/worker.py vollstaendig - nrplanner/app.py (main,
  Planner.__init__, _build_left, RelicSlot, rescan_save, load_equipped,
  reload_chalices, apply_chalice, _relic_changed) - nrplanner/inventory.py -
  nrdata/savefile.py (nur gelesen: OwnedRelic, Loadout,
  _check_the_prefilter_can_see_every_id, read_owned_relics,
  read_relic_handles, read_loadouts) - tests/conftest.py, tests/rendered.py -
  eigene Memory-Dateien (guard-teeth-traps, advisor-display-path,
  redirect-and-commit-devices, mutation-registry)
GEÄNDERT: nrplanner/inventory.py - nrplanner/app.py -
  tests/test_save_read_in_the_background.py (neu) - tests/conftest.py -
  tests/rendered.py - tests/test_advisor_bar.py - tests/test_advisor_hold.py -
  tests/test_custom_relic.py - tests/test_game_text_is_never_markup.py -
  tests/test_hostile_savefile.py - .claude/agent-memory/developer/
  project_background_save_read.md (neu) und MEMORY.md -
  docs/berichte/T-142-developer.md (diese Datei).
  Committet: ea80c6f (inventory.py, test_hostile_savefile.py),
  09518a4 (app.py und die uebrigen tests/-Dateien).
ANNAHMEN: (1) AK-229 zweite Haelfte ist erst nach AK-228 erfuellbar - die
  Id-Pruefung wirft heute noch und ihr Text sagt "nothing is wrong with the
  save."; der Waechter laesst genau diese eine Stelle namentlich zu und hat
  eine Positivkontrolle. (2) `chalices.set_imported` wird auch im
  unterdrueckten Fall gesetzt (AK-226); das ist derselbe Schluessel wie
  bisher, kein neuer Zustand, wirkt aber ueber die Sitzung hinaus - der
  Wortlaut sagt "in dieser Sitzung". (3) Der Wartezustand entfaellt fuer die
  Klammer `(n available)` auch dann, wenn gar kein Spielstand gefunden wurde
  (AK-222 sagt "solange kein Bestand vorliegt", ohne Fallunterscheidung).
NÄCHSTER: director
BLOCKIERT DURCH: nichts
```

## Umgesetzt

**`nrplanner/inventory.py` - die Thread-Grenze (AD-029 Punkt 1).**
`load` ist in zwei Haelften geteilt:

- `scan(data, save_path=None) -> SaveScan | None` - das Teure: Dateien
  finden, entschluesseln, Records lesen, Handles und Loadouts. Kein Qt, keine
  Widgets, kein Settings-Zugriff.
- `build(data, found) -> Inventory` - das Billige: aus den Records mit den
  Spieldaten das lebende `Inventory`.
- `load` bleibt und ist beides nacheinander, fuer jeden Aufrufer ohne Thread.
- `SaveScan` ist `frozen`; ueber die Grenze gehen nur Records, nie das
  `Inventory` (AD-006.8 unangetastet).

**`nrplanner/app.py` - `SaveReader` und `_SaveReadWorker`.** Dieselbe Bauform
wie `AdvisorController`, kein zweiter Mechanismus: Worker in einem `QThread`,
Generationszaehler, `ready`/`failed`, `shutdown`, das den Zaehler **vor** dem
`wait()` erhoeht. Unterschiede und ihre Begruendung stehen im Klassen-
Docstring: keine Entprellung (ein Klick ist kein gezogener Regler), kein
Zwischenspeicher (ein Rescan will gerade wissen, was sich geaendert hat), kein
kooperatives Abbrechen (`inventory.scan` hat keine Stelle zum Nachsehen).

**Der dritte Fensterzustand.** `rescan_save` startet nur noch und setzt den
Zustand; `_on_save_read` / `_on_save_failed` sind die Enden.

- Wartezeile: `READING_THE_SAVE` / `READING_THE_SAVE_AGAIN` (§9 a/b).
- Leere Slotkarte: `RELICS_AFTER_THE_SAVE` (§9 c) als dritte Zeile derselben
  `MUTED`-Zeile in `rolled_label`, in der `HELD_EMPTY` und `empty_reason`
  schon stehen.
- Reliktknopf gesperrt, solange gelesen wird; sonst nichts.
- `(n available)` entfaellt, solange kein Bestand vorliegt.
- `load_equipped` tut waehrend eines Lesens nichts und schreibt nichts.
- Die Entwertung der Berater-Zwischenspeicher wandert an die **Ankunft**
  (AD-029 Punkt 3).
- `closeEvent` faehrt den Reader mit herunter.

**AK-226.** `_relic_changed` merkt sich den Nightfarer, wenn der Spieler
waehrend des ersten Lesens selbst einen Slot setzt (`set` im Speicher, kein
QSettings-Schluessel, OF-15). `reload_chalices` markiert das gespeicherte
Build dann als uebernommen, **ohne** es zu uebernehmen, und
`_keep_the_slots_the_player_filled` setzt nur die Kelchliste zurueck auf das
angewandte Gefaess, ohne die Slots anzufassen.

**AK-225.** `owned_label` bekommt beim Bau eine Mindesthoehe von zwei Zeilen,
aus der Schrift gerechnet statt als Zahl hingeschrieben.

## Messungen (L-009: Umgebung mit jeder Zahl)

**Skript:** `…/scratchpad/T-142/measure_save_line.py`, gegen Commit `09518a4`.
Alle Zahlen **logisch**, Qt-Stil **Fusion** (ueber `app.apply_appearance`,
wie das Programm selbst), linker Bereich auf seiner Vorgabebreite
**430 logische px** (`PANE_DEFAULTS = (430, 520, 370)`), Bestand des Nutzers
(309 Relikte, 110 Builds, Slot `USER_DATA000`).

| Umgebung | Wartezeile (a) | Bestandsnotiz | Rescan-Zeile (b) |
|---|---|---|---|
| offscreen, 800x800, dpr 1,0, **ohne** die Mindesthoehe | 10 px | **22 px** | 22 px |
| offscreen, 800x800, dpr 1,0, **mit** der Mindesthoehe | 28 px | 28 px | 28 px |
| Windows-Plattform, 1707x1067 logisch, **dpr 1,5**, mit | 32 px | 32 px | 32 px |

Ohne die Mindesthoehe schiebt die Ankunft alles unter der Zeile um **12 px**
nach unten. Mit ihr sind alle drei Faelle gleich hoch, auf beiden Plattformen.
Die zwei langen Enden (§9 d und der Fehlersatz) duerfen hoeher ausfallen -
ausdrueckliche Ausnahme in AK-225.

*Herleitung der Mindesthoehe (L-001):* `2 x QFontMetrics(font).lineSpacing()`.
Zwei, weil die gewoehnliche Bestandsnotiz ein Satzglied plus hoechstens ein
weiteres ist (§9 e) und an der Vorgabebreite gemessen zwei Zeilen braucht
(22 px); die Zahl selbst steht nirgends im Code, sie kommt aus der Schrift.
Unter der Windows-Plattform ergibt dieselbe Formel 32 statt 28 - das ist der
Punkt der Formel.

## Tests

**Neu: `tests/test_save_read_in_the_background.py`, 19 Faelle.**
Alles ueber den Konstruktor-Nahtstelle `Planner(data, read_save=…)` gefahren,
nie an ihr vorbei; gewartet wird auf **Zustaende**, die 30-s-Sicherung in
`StatedRead` kommt in keiner Behauptung vor.

| AK | Fall |
|---|---|
| AK-220 | `test_the_window_stands_complete_before_the_save_has_been_read` |
| AK-221, AK-222 | `test_the_waiting_state_is_a_state_and_not_a_nothing`, `test_the_arrival_puts_the_count_back_in_every_heading`, `test_a_rescan_says_that_nothing_changes_until_it_is_done` |
| AK-223 | `test_the_read_shuts_the_relic_button_and_nothing_else` (mit Kontrolle am Fenster ohne Spielstand) |
| AK-224 | `test_every_ending_of_a_read_leaves_a_sentence_of_its_own` (drei Enden) |
| Warnung 1 | `test_the_answer_of_the_read_actually_reaches_the_window` |
| AK-225 | `test_the_arrival_moves_neither_the_window_nor_the_focus` |
| AK-226 | `test_the_stored_build_is_taken_over_when_nobody_touched_a_slot`, `test_a_slot_set_during_the_read_survives_the_arrival` |
| AK-227 | `test_pressing_rescan_during_a_read_starts_no_second_one` (Zaehlwert `== 2` gegen ein Literal), `test_the_reader_starts_nothing_while_one_read_is_out` |
| §5, §9 (h) | `test_load_equipped_says_nothing_while_a_read_is_out` |
| Warnung 2 | `test_nothing_arrives_after_shutdown` |
| AK-229 | `test_the_collector_of_the_texts_really_fires` (Positivkontrolle), `test_no_other_text_behind_the_prefix_says_the_save_is_fine`, `test_the_prefix_is_written_in_exactly_one_place`, `test_the_prefix_appears_only_where_no_inventory_came_out` |

**Angepasst, weil das Lesen jetzt asynchron ist:** `tests/conftest.py`
(`wait_for_the_save`, in `_new_planner` benutzt), `tests/rendered.py`,
`tests/test_advisor_hold.py`, `tests/test_custom_relic.py`,
`tests/test_advisor_bar.py` (der AD-006.7-Fall prueft die Reihenfolge jetzt an
der Ankunft und zusaetzlich, dass **waehrend** des Lesens nichts entwertet
wird), `tests/test_game_text_is_never_markup.py`, `tests/test_hostile_savefile.py`
(neue `_scan_save`-Signatur plus `build`).

### Suitezahl

```
pytest -n auto  ->  1417 passed, 9 skipped, 0 failed  in 173,41 s
```

gegen die Vorgabe **1398 passed, 9 skipped, 0 failed**. Die Differenz ist
**+19** und das sind genau die 19 Faelle des neuen Moduls; keine andere Zahl
hat sich bewegt.

### Gleichheitsbeleg fuer die Trennung von `scan`/`build`

`inventory.load` am echten Spielstand, kanonischer Dump aller Felder
(Relikte mit Effekten, Fluechen, Handle und Offset; alle Loadouts):

```
Klon a8d31bb  : relics 309 loadouts 110 source USER_DATA000
Arbeitsbaum   : relics 309 loadouts 110 source USER_DATA000
diff          : IDENTISCH
```

Skript `…/scratchpad/T-142/dump_inventory.py`, Klon per `git clone . <klon>`.

### Mutationskampagne - 13 Mutationen, 12 getoetet, **1 ueberlebt**

Auf einem Klon von `09518a4` (`…/scratchpad/T-142/mutant`), Treiber
`…/scratchpad/T-142/mutate.py`, gelaufen gegen
`tests/test_save_read_in_the_background.py`.

| Mutation | Ergebnis | erster fallender Fall |
|---|---|---|
| `answer-stamped-with-a-dead-generation` (Generation 0 wie in U5b) | KILLED | 9 failed - u. a. `arrival_puts_the_count_back` |
| `shutdown-does-not-raise-the-generation` (T-137) | KILLED | `nothing_arrives_after_shutdown` |
| `a-read-per-press` | KILLED, **aber durch Prozessabbruch** (s. u.) | - |
| `no-waiting-sentence` | KILLED | `waiting_state_is_a_state` |
| `no-line-on-the-empty-card` | KILLED | `waiting_state_is_a_state` |
| `the-bracket-stays-at-zero` | KILLED | `waiting_state_is_a_state` |
| `the-relic-button-stays-open` | KILLED | `read_shuts_the_relic_button` |
| `the-waiting-line-is-one-line-high` | KILLED | `arrival_moves_neither_the_window_nor_the_focus` |
| `the-failure-keeps-the-waiting-sentence` | KILLED | `every_ending_leaves_a_sentence` |
| `skipped-without-being-marked` | KILLED | `stored_build_is_taken_over` |
| `the-players-slot-is-overwritten` | KILLED | `slot_set_during_the_read_survives` |
| `load-equipped-speaks-during-the-read` | KILLED | `load_equipped_says_nothing` |
| `the-stock-never-reaches-the-cards` | **SURVIVED** | 19 passed |

Die Anker stehen woertlich in `…/scratchpad/T-142/mutate.py` (`MUTATIONS`),
generierbar mit `ast.literal_eval`.

**Zur Mutation `a-read-per-press`:** der Lauf endet mit Exitcode 127 und ohne
pytest-Zusammenfassung - ein zweiter `QThread` wird neben einem lebenden
gebaut, die Referenz auf den ersten wird ueberschrieben und er wird waehrend
des Laufens zerstoert; der Prozess bricht ab. Auch einzeln auf
`test_the_reader_starts_nothing_while_one_read_is_out` eingegrenzt bleibt es
beim Abbruch. Der Lauf ist damit rot, aber das Signal ist ein Prozessabbruch
und keine benannte Behauptung - `assert read.calls == 1` kommt nicht mehr zu
Wort. Das gehoert gesagt (L-003).

## Meldungen

### An den director

**1. Ueberlebende Mutation - nicht nachgebessert, wie vorgegeben.**
`the-stock-never-reaches-the-cards`: `self._hand_the_stock_to_the_slots()` in
`_on_save_read` durch `pass` ersetzt - alle 19 Faelle bleiben gruen. Grund,
soweit ich ihn sehe: nachdem `is_reading()` an der Ankunft `False` ist, laeuft
`reload_chalices -> load_equipped -> apply_chalice -> set_owned` und gibt den
Karten den Bestand ohnehin. Die Zeile ist damit auf **allen von meinen
Faellen erreichten Wegen** ueberfluessig; noetig bleibt sie auf dem Weg, auf
dem `load_equipped` vorher aussteigt (`selected_loadout(hero) is None`) - ein
Nightfarer, fuer den der Spielstand Builds, aber kein *ausgeruestetes* Build
hat. Der Spielstand des Nutzers hat fuer den ersten Nightfarer eines, deshalb
trifft kein Fall diesen Weg. **Entweder** ein Fall mit einem `SaveScan`, dessen
Loadouts kein `selected` tragen, **oder** die Zeile faellt. Das ist eine
Entscheidung ueber Umfang, nicht ueber Code.

**2. `scripts/` bauen jetzt ein Fenster ohne Bestand.** Fuenf Skripte machen
`appmod.Planner(data)` und lesen danach `planner.owned`:
`scripts/make_screenshots.py`, `scripts/measure_advisor_block.py`,
`scripts/measure_picker_cards.py`, `scripts/capture_weapon_damage.py`,
`scripts/differential/capture.py`. Sie bekommen `owned is None`, weil sie das
Lesen nicht abwarten. **Nicht behoben** - `scripts/` steht nicht in den
beruehrten Dateien. Es faellt kein Test darueber (Suite gruen), aber der
naechste Messlauf misst ein leeres Fenster. Eine Zeile je Skript
(`while planner.save_reader.is_reading(): app.processEvents()`), oder
`Planner(data)` bekommt einen ausdruecklichen synchronen Weg.

**3. Mutationen nicht in `scripts/differential/mutate.py` registriert.**
Die Registrierung wuerde `scripts/` beruehren, das nicht in meinen Dateien
steht, und je Eintrag einen Suitefall hinzufuegen (dann waere die Suitezahl
nicht mehr 1417 gegen 1398 vergleichbar). Die 13 Eintraege liegen fertig in
`…/scratchpad/T-142/mutate.py` und sind copy-paste-faehig. **Der Scratchpad
ist sitzungsgebunden** - wenn registriert werden soll, dann in dieser Sitzung.

**4. Ein Commit traegt zwei versehentliche Zeilen im Body.** `ea80c6f` endet
mit `-- nrplanner/inventory.py nrplanner/inventory.py` und
`-- tests/test_hostile_savefile.py`; das sind Reste, keine Aussage. Nicht
korrigiert, weil ein `--amend` eine Historienaenderung waere und die Freigabe
dafuer beim director liegt.

**5. Kein Sicherheitsfund.** Der Spielstand wird nur gelesen; beide `.sl2`
sind nach dem Lauf byte- und mtime-gleich (Belege unten). Kein Netzwerk,
kein neuer persistenter Zustand. Der `SaveScan` traegt den Ordnernamen (mit
Steam-Id) wie bisher nur in den Tooltip, escaped.

### An den ui-ux-designer

**A. AK-223 wird um genau ein Bedienelement verfehlt, und ich schlage vor,
das Kriterium nachzuziehen statt den Code.** Waehrend des Lesens ist neben den
sechs Reliktknoepfen auch **`Optimize`** in der Berater-Zeile gesperrt. Das
ist nicht neu und nicht meine Sperre: die Berater-Zeile sperrt `Optimize`,
sobald kein Bestand da ist - auf einem Fenster ohne Spielstand genauso.
Gemessen und im Waechter festgehalten
(`test_the_read_shuts_the_relic_button_and_nothing_else` prueft zusaetzlich am
Fenster ohne Spielstand, dass `Optimize` dort ebenso gesperrt ist). Ihn
freizugeben waere schlechter: der Klick wuerde den Satz
`No save was read, so there are no relics to choose from — use Rescan save.`
schreiben, und der ist waehrend eines laufenden Lesens **falsch**.
**Vorschlag:** AK-223 lesen als "das *Lesen* sperrt genau eines - den
Reliktknopf; `Optimize` ist durch das Fehlen des Bestands gesperrt, wie schon
heute ohne Spielstand".

**B. AK-224 zaehlt vier Enden, und beim ersten Lesen einer Sitzung steht in
der Zeile ein fuenfter Satz.** Nach der Ankunft laeuft die einmalige
Uebernahme des gespeicherten Builds (§6 verlangt sie ausdruecklich), und
`load_equipped` schreibt danach seinen eigenen Satz ueber die Bestandsnotiz,
z. B.:

```
Loaded Wylder — 5 chalices, showing the equipped Wylder's Goblet with 2 relics.
```

Das tut es **auf dem synchronen Weg genauso** und ist keine Aenderung von mir
- es faellt nur auf, weil AK-224 die Enden jetzt aufzaehlt. Der Satz, an dem
AK-224 haengt, ist eingehalten: **nie ein Wartesatz am Ende**, und das prueft
der Waechter. **Frage:** ist der Import-Satz ein zulaessiges fuenftes Ende
("die Aufzaehlung waechst mit"), oder soll die Bestandsnotiz das letzte Wort
behalten? Zweiteres waere eine Aenderung am Verhalten des Imports und braucht
einen eigenen Auftrag.

**C. AK-229, zweite Haelfte, ist erst mit AK-228 erfuellbar.** Auf dem
Lesepfad gibt es heute genau **einen** Text, der sagt, mit dem Spielstand sei
alles in Ordnung: `nrdata/savefile.py:241-246`,
`_check_the_prefilter_can_see_every_id`, `… nothing is wrong with the save.`
Er hoert nach §7 auf zu existieren - das ist AK-228s Arbeit und ausdruecklich
nicht meine (`nrdata/savefile.py` ist gesperrt). Gebaut ist deshalb:
der Sammler ueber **alle acht** `raise ValueError`-Texte von
`nrdata/savefile.py` und `nrplanner/inventory.py` (AST, nicht Grep), die
Wortliste `nothing is wrong | nothing is missing | nothing needs fixing`, die
**Positivkontrolle** (dieser eine Text **muss** anschlagen, sonst sammelt der
Sammler nicht) und die Behauptung `offenders <= {diese eine Stelle}`. Wer
AK-228 baut, streicht die Positivkontrolle und setzt `offenders == set()`;
beides steht so im Docstring der Faelle.

**D. Erste Haelfte von AK-229 ist erfuellt und als Eigenschaft geprueft.**
`Save could not be read: ` steht in `nrplanner/` an genau **einer** Stelle.
Suche ueber den ganzen Baum, zwei unabhaengig formulierte Masken:

```
grep -rn "Save could not be read" nrplanner/ --include=*.py     -> 1 Treffer
  nrplanner/app.py:595  UNREADABLE_SAVE = "Save could not be read: "

grep -rn "could not be read" nrplanner/ nrdata/ --include=*.py  -> 4 Treffer
  nrplanner/app.py:595        das Praefix selbst
  nrplanner/app.py:3957       "This save's stored builds could not be read: "
                              -- ein anderer Satz aus `load_equipped`, kein Praefix
  nrplanner/effecttext.py:86  Kommentar, kein Text auf dem Bildschirm
  nrplanner/inventory.py:246  Docstring von `SaveScan.loadout_error`
```

Der Waechter `test_the_prefix_is_written_in_exactly_one_place` haelt das
fest; `test_the_prefix_appears_only_where_no_inventory_came_out` prueft
dieselbe Aussage als Verhalten ueber drei Enden.

### An den qa-engineer

Zu pruefen, mit dem echten Spielstand und einem echten Fenster:

1. **Der Start.** Fenster sofort da, `Reading your save.` unter den Knoepfen,
   sechs leere Karten mit `Your relics appear when the save has been read.`,
   keine `(n available)`-Klammer, `Empty slot` grau. Danach: Zahlen in jeder
   Ueberschrift, Knoepfe frei, Kelchliste am Spielstand.
2. **`Rescan` waehrend eines laufenden `Rescan`.** Fuenfmal druecken - es darf
   sich nichts bewegen, und die Zeile muss
   `Reading your save again. Nothing changes until it is done.` bleiben.
3. **Schliessen waehrend des Lesens.** Fenster zu, kein Absturz, kein Fenster,
   das nach dem Schliessen noch etwas schreibt.
4. **Der Umzug der Zeile.** Ob beim Uebergang Warte -> Notiz irgendetwas unter
   der Zeile springt (Kelchliste, `Level`). Gemessen ist es an 430 px; die
   Bereichsteiler sind verschiebbar, und bei **schmalem linken Bereich** kann
   die Notiz drei Zeilen brauchen, wo die Wartezeile zwei belegt - dann
   springt es doch. AK-225 misst ausdruecklich an der Vorgabebreite; der
   schmale Fall ist ungeprueft.
5. **Ein Nightfarer ohne ausgeruestetes Build.** Das ist der Weg, auf dem die
   ueberlebende Mutation (Meldung 1) beisst: nach der Ankunft muessen die
   Slotueberschriften trotzdem Zahlen tragen und der Picker Relikte anbieten.
6. **Kein Spielstand** (Ordner umbenennen): Zeile muss
   `No save file found. …` sein, nicht der Wartesatz, und die Klammer
   `(n available)` fehlt jetzt ganz - das ist beabsichtigt (AK-222), aber es
   ist eine sichtbare Aenderung gegenueber `(0 available)` von frueher.
7. **Nicht geprueft von mir:** Linux und macOS (kein Ziel), der langsame
   Rueckfallweg (AK-228, gibt es nicht), und das Verhalten bei einem waehrend
   des Lesens gepatchten Spiel.

## Nachweise der Pflichtvorgaben

**Alle drei Umlenkungen, mit Positivkontrolle** (`…/scratchpad/T-142/where.py`):

```
=== POSITIVKONTROLLE (ohne Umlenkung) ===
favourites.ORG           : DankYeeter
paths.cache_dir()        : C:\Users\Daniel\AppData\Local\NightreignHelper
shortcut.shortcut_path() : C:\Users\Daniel\AppData\Roaming\Microsoft\Windows\
                           Start Menu\Programs\Nightreign Helper.lnk

=== MIT UMLENKUNG ===
favourites.ORG           : DankYeeterT-142
paths.cache_dir()        : …\scratchpad\T-142\local\NightreignHelper
shortcut.shortcut_path() : …\scratchpad\T-142\appdata\Microsoft\Windows\
                           Start Menu\Programs\Nightreign Helper.lnk
```

Die Positivkontrolle zeigt, dass die Messung ohne die Umlenkung wirklich auf
die Orte des Spielers zeigt - sonst haette ich mein Pruefmittel gemessen.

**Testabzug kopiert, nicht neu gebaut:**
`cp -r C:\…\NightreignHelper-Testabzug …\scratchpad\T-142\local\NightreignHelper`
-> 841 Dateien, 22 MB. Kein Neuaufbau in diesem Lauf.

**Beide `.sl2` unveraendert**, vor und nach allen Laeufen:

```
c2da42ee2124a51233e6630b8a07eac8  …\76561198073567627\NR0000.sl2
e52bd9dd2fbab319dec22b79985f14b3  …\76561198179244962\NR0000.sl2
diff md5   : SPIELSTAENDE UNVERAENDERT
diff mtime : MTIME/GROESSE UNVERAENDERT
```

**Keine Zeitschranke in der Suite.** Die einzigen Zeiten im neuen Modul sind
`READ_FUSE_S = 30.0` und die Fristen in den Warteschleifen; beide sind
Sicherungen gegen Haengen, keine kommt in einer Behauptung vor.

**Keine neue Abhaengigkeit.** Nur `threading`, `ast`, `dataclasses`,
`pathlib` aus der Standardbibliothek und das schon benutzte `PySide6`.

**Aufgeraeumt.** Kein Server gestartet; `tasklist` nach dem letzten Lauf:
`No tasks are running which match the specified criteria.` Klon, Mutantenbaum
und Messkopie liegen ausschliesslich unter
`…/scratchpad/T-142/` und damit ausserhalb des Projektbaums.
