# T-133 - U1: der Vorfilter am Spielstand-Lesen (developer)

```
STATUS: erledigt
AUFTRAG: T-133 - U1: Vorfilter in nrdata/savefile.py (AD-029 Stufe C)
GELESEN: docs/tasks/T-133.md, ARCHITECTURE.md (AD-029 ganz, Nachtrag VIII
  Umsetzungstabelle), docs/berichte/T-118-performance-tuner.md (P2),
  nrdata/savefile.py, nrplanner/inventory.py (load, _scan_save, _decrypt_slots),
  nrplanner/app.py (nur lesend: rescan_save 3435-3446, Aufrufstellen),
  nrplanner/paths.py, nrplanner/shortcut.py, nrplanner/favourites.py,
  tests/conftest.py, tests/test_hostile_savefile.py, pytest.ini, CLAUDE.md
GEÄNDERT: nrdata/savefile.py (committet 3a292cf, 214e885),
  tests/test_relic_scan_prefilter.py (neu, committet 3a292cf),
  docs/berichte/T-133-developer.md (diese Datei),
  .claude/agent-memory/developer/project_real_save_shape.md (Zahlen korrigiert,
  uncommittet)
ANNAHMEN: keine offenen. Die eine tragende Annahme (relic_id < 0x01000000)
  steht jetzt als Pruefung im Code und wird gegen den Datensatz getestet.
NÄCHSTER: performance-tuner (U3, Nachmessung von inventory.load und
  Prozessstart) und security-reviewer (U2, praeparierte Datei aus T-096)
BLOCKIERT DURCH: nichts
```

## Umgesetzt

**`nrdata/savefile.py`** (einzige Produktivdatei, Commit `3a292cf`, Nachtrag
`214e885`):

- **`_relic_id_offsets(slot_data)`** - der Vorfilter. Ein Record beginnt mit
  `relic_id | RELIC_ID_FLAG`; unterhalb `RELIC_ID_CEILING` ist dessen oberstes
  Byte immer das der Flagge, in Little-Endian also das vierte Byte des
  Records. `bytes.find` laeuft den Slot in C ab, die Python-Schleife sieht nur
  noch Versaetze, die ueberhaupt ein Record sein koennen. Die Obergrenze
  (`len - 24`, exklusiv) und die Vier-Byte-Ausrichtung sind woertlich die des
  alten Walks.
- **`_check_the_prefilter_can_see_every_id(valid_relic_ids)`** - die
  Id-Annahme als Pruefung, gerufen zu Beginn jedes `read_owned_relics`. Eine
  Relikt-Id ab `RELIC_ID_CEILING = 0x01000000` kann der Vorfilter nicht
  finden; statt still weniger zu finden, verweigert der Scan laut
  (`ValueError`, wie SEC-022 in diesem Modul).
- `read_owned_relics`: eine Zeile getauscht
  (`for off in range(0, len(slot_data) - 24, 4)` -> `for off in
  _relic_id_offsets(slot_data)`). Rumpf, Dichteschranke und `seen_offsets`
  unveraendert.
- Neue Konstanten: `RELIC_ID_CEILING`, `RELIC_FIELDS_SIZE`, `_ID_TOP_BYTE`
  (aus `RELIC_ID_FLAG` gepackt, damit beide nicht auseinanderlaufen).

**`tests/test_relic_scan_prefilter.py`** (neu, 13 Faelle). Die Erwartung kommt
nie aus dem Vorfilter: die Datei schreibt den alten vollen Walk als
`full_walk` aus und haelt den Vorfilter dagegen (L-008b).

## Die vier harten Punkte

### 1. Gleichheitsprobe am echten Spielstand - das Ergebnis

Skript `…/scratchpad/T-133/equal_and_measure.py`, **nur lesend**. Es traegt
den alten Scan woertlich aus `nrdata/savefile.py:192-238` (Stand `0128971`)
in sich und vergleicht ihn im selben Prozess mit dem Modul.

**Gefuehrt ueber 28 von 28 Slots aus 2 Dateien:**

```
C:\Users\Daniel\AppData\Roaming\Nightreign\76561198073567627\NR0000.sl2   19 531 312 B
C:\Users\Daniel\AppData\Roaming\Nightreign\76561198179244962\NR0000.sl2   19 531 312 B
-> 28 entschluesselte Slots, 39 060 416 Byte
```

```
28 of 28 slots equal, 543 records found in total
  NR0000.sl2/USER_DATA000: 234 old / 234 new -> equal
  NR0000.sl2/USER_DATA000: 309 old / 309 new -> equal
positive control (one record dropped): DIFFERENT
```

Verglichen wird je Record `(relic_id, offset, effect_ids, curse_ids)`, nicht
nur die Anzahl. **Positivkontrolle:** derselbe Vergleich, um einen Eintrag
gekuerzt, meldet `DIFFERENT` - der erste Lauf meldete hier faelschlich
`equal`, weil er den groessten statt den bestbestueckten Slot nahm; das war
die Kontrolle, die die Kontrolle gefunden hat.

**Vorlauf, der die eingebettete Kopie belegt:** dasselbe Skript **vor** der
Aenderung gelaufen - alt gegen Modul 28/28 gleich, beide Zeiten im selben Band
(4849,8 / 5240,7 ms). Die Kopie ist also der Scan, den sie zu sein behauptet.

**Nicht gefuehrt:** an einer praeparierten Datei - das ist U2
(`security-reviewer`, T-096). Der Waechter deckt die Dichte-Seite ab (unten).

### 2. Die Id-Annahme ist eine Pruefung, kein Kommentar

`_check_the_prefilter_can_see_every_id` nimmt das groesste Element von
`valid_relic_ids` und verweigert ab `0x01000000`. Groesste Id im heutigen
Datensatz: **2 013 322** (`0x001eb88a`), Faktor 8 darunter, gemessen aus
`nightreign_data.json` des festen Testabzugs. Drei Faelle sichern das:
Verweigerung, Wortlaut (kein Pfad, kein `.sl2`, "too old"), und die Kontrolle
an der Grenze (`RELIC_ID_CEILING - 1` wird vollstaendig gelesen). Dazu
`test_the_games_own_relic_ids_are_all_below_the_ceiling`, das die Kopplung
gegen den Datensatz der installierten Spielinstallation prueft - das ist der
Fall, der einen Patch meldet.

### 3. Dichteschranke unangetastet, `load()` bricht nicht frueher ab

- `MIN_BYTES_PER_RELIC_RECORD`, `limit`, der `raise` an dem Record, der die
  Linie ueberschreitet: **unveraendert** (siehe `git diff`).
- `test_a_slot_that_is_nothing_but_the_searched_byte_is_still_refused` fuehrt
  einen Slot aus lauter `0x80` durch **beide** Scans: beide verweigern.
- **Gegenprobe, dass die Schranke noch beisst:** `if len(out) > limit` zu
  `limit * 2` mutiert -> `tests/test_hostile_savefile.py::
  test_one_record_more_than_the_slot_can_hold_is_a_data_error` faellt
  (1 failed, 27 passed). Danach zurueckkopiert, 28 passed.
- `nrplanner/inventory.py` und `nrplanner/app.py` sind **nicht angefasst**;
  `load()` liest weiter alle Dateien und alle Slots und waehlt den
  bestbestueckten.

### 4. Vorher/nachher, mit Messumgebung (L-009)

**Messumgebung:** Windows 10 Home 19045 x64, AMD Ryzen (Family 25, 16
Threads), Python 3.12.10 aus `.venv`, kein Qt und keine Oberflaeche beteiligt,
kein cProfile, Slots **einmal entschluesselt und im Speicher gehalten**
(gemessen wird der Scan, nicht das Lesen von der Platte), warmer
Dateicache, derselbe Prozess fuer beide Werte, Median aus n=5. Die Zahlen sind
Zeiten, keine Oberflaechenmasse - physisch/logisch entfaellt.

| Was | vorher | nachher |
|---|---|---|
| `read_owned_relics`, alle 28 Slots | **4 835,3 ms** (min 4755,4, max 4870,0) | **93,3 ms** (min 88,1, max 115,3) |
| abgelaufene Versaetze, 28 Slots | 9 764 936 | **27 320** |
| Anteil `0x80` an 39 060 416 Byte | — | 0,20 % |

**Faktor 51,8 auf dem Scan.** Das ist **nicht** `inventory.load` und **nicht**
der Prozessstart: die 6147,6 ms aus S11-E enthalten Entschluesseln und
Modellbau. Die Nachmessung von `inventory.load` und damit die Entscheidung
ueber den Ausloeser fuer Stufe B gehoert U3 (`performance-tuner`) - ich habe
sie bewusst nicht gefuehrt.

**Vergleich zu T-118:** dort 14 Slots 2802,7 -> 61,9 ms (45x). Meine Zahl
liegt ueber 28 Slots und in einem anderen Harness; die Groessenordnung deckt
sich. Der geerbte Docstring-Wert "0,22 %" ist durch die hier gemessenen
0,20 % ersetzt (Commit `214e885`), damit im Code keine Zahl ohne ihre
Messumgebung steht.

## Waechter und Mutationsbeweis

`tests/test_relic_scan_prefilter.py`, 13 Faelle, **1,74 s** allein.
**Standardlauf**, kein Skip, kein Marker (der Datensatz-Fall skippt nur auf
einem Rechner ohne Spiel).

12 Mutanten, **12 tot**, jeder mit benanntem Toeter
(`…/scratchpad/T-133/mutate.py`, Datei vorher per `cp` zur Seite kopiert und
danach zurueckkopiert - kein `git checkout`):

| Mutant | Ergebnis | getoetet von |
|---|---|---|
| M1 Ausrichtungspruefung entfernt | KILLED | `…_off_the_four_byte_grid_is_not_a_record` |
| M2 Suche beginnt bei 4 statt 3 | KILLED | 4 Faelle, u. a. `…_at_the_very_first_offset_is_found` |
| M3 Obergrenze `<` -> `<=` | KILLED | `…_at_the_walks_own_upper_bound_is_not_read` |
| M4 Suche springt `pos + 4` statt `pos + 1` | KILLED | `…_carrying_the_flag_byte_inside_itself…` |
| M5 `yield pos` statt `yield pos - 3` | KILLED | 6 Faelle |
| M6 anderes Byte gesucht (`b"\x00"`) | KILLED | 7 Faelle |
| M7 Id-Pruefung nicht mehr gerufen | KILLED | `…_above_the_ceiling_is_refused_out_loud` + Wortlautfall |
| M8 Schranke auf `0x02000000` angehoben | KILLED | `…_largest_id_the_prefilter_can_see_is_read_in_full` |
| M9 `max` -> `min` in der Pruefung | KILLED | `…_above_the_ceiling_is_refused_out_loud` |
| M10 Vorfilter durch den vollen Walk ersetzt (verhaltensgleich!) | KILLED | `…_hands_over_a_fraction_of_the_offsets` |
| M11 Schranke auf `0x100` gesenkt | KILLED | 9 Faelle |
| M12 SEC-022-Schranke `limit * 2` | in dieser Datei SURVIVED, getoetet von `tests/test_hostile_savefile.py` | s. Punkt 3 |

**M10 ist der wichtigste:** ein Vorfilter, der wieder alles ablaeuft, ist
*korrekt* und nur langsam - alle Gleichheitsfaelle bleiben gruen. Genau dafuer
gibt es `test_the_prefilter_hands_over_a_fraction_of_the_offsets`, der die
Kandidaten **exakt** (`[0, 4, 80, 84, 160, 164]`) gegen die 16 378 Versaetze
des Walks stellt.

**M12 ist die vom Rahmen verlangte Meldung eines Ueberlebenden:** er ueberlebt
diese Datei zu Recht - er mutiert nicht den Vorfilter, sondern SEC-022, und
dessen Waechter steht in `test_hostile_savefile.py`, wo er faellt. Nachgebessert
habe ich nichts.

**Rot-vorher, je Schutzmassnahme einzeln abgeschaltet:** M7 (Id-Pruefung
entfernt) und M1/M3 (die beiden Bedingungen des Vorfilters) sind genau diese
Probe; jede einzelne Abschaltung faerbt Faelle rot, die kein anderer Mutant
rot faerbt.

## Suite

```
.venv\Scripts\python.exe -m pytest -n auto -q
1336 passed, 9 skipped in 180.35s
```

Gegen die Vorgabe **1323 passed, 9 skipped, 0 failed**: **+13 = genau die
neue Datei**, 9 Skips unveraendert, 0 failed. Die 180 s liegen ueber den in
`CLAUDE.md` genannten 127 s; die Maschine trug waehrenddessen noch andere
Arbeit (paralleler `architect`-Lauf), gemessene Faelle sind davon nicht
betroffen.

## Datenverzeichnisse - Nachweis der drei Umlenkungen

Jedes Messskript setzt alle drei **vor** dem Import von `nrplanner` und
belegt sie zur Laufzeit (Ausgabe des Laufs):

```
LOCALAPPDATA -> …\scratchpad\T-133\local\NightreignHelper\nightreign_data.json
APPDATA      -> …\scratchpad\T-133\roaming\Microsoft\Windows\Start Menu\Programs
settings org -> DankYeeterT-133
```

plus `assert savefile.save_roots()[0] == …scratchpad\T-133\roaming\Nightreign`.
Der feste Testabzug wurde **kopiert**, nicht neu gebaut (22 MB nach
`…\T-133\local\NightreignHelper`). Den Spielstand findet das Skript bewusst
ueber `Path.home()/AppData/Roaming/Nightreign` und oeffnet ihn nur lesend.

**Gegenprobe nach dem Lauf:** beide `.sl2` unveraendert (mtime 2025-09-20 bzw.
2026-09-01), `…\Local\NightreignHelper\nightreign_data.json` unveraendert
(2026-09-05), im echten Start-Menue keine `Nightreign`-Verknuepfung. Heute ist
der 2026-09-08. Das Programm selbst wurde nicht gestartet; es lief kein
Server, es ist kein Prozess offen.

## DoD

- [x] Anforderung verstanden, Annahmen dokumentiert
- [x] Build & Tests gruen in der benannten Testumgebung (Windows 10 x64)
- [x] Neue Tests fuer neue Logik, mit vollem Mutationsbeweis
- [x] Linter: **entfaellt**, das Projekt hat keinen konfiguriert
      (`requirements-dev.txt` = pytest + xdist; kein ruff/flake8/pyproject)
- [x] Keine Secrets, keine TODOs, kein toter Code
- [x] Nur `nrdata/savefile.py` und `tests/` beruehrt; `ARCHITECTURE.md` ist
      im Arbeitsbaum vom parallelen `architect` geaendert und **nicht** von
      mir committet (`git commit … -- <pfad>`)
- Linux/macOS: **ungeprueft** und kein Ziel.

## An qa-engineer

- **Das Bild, das ein Bruch macht, ist ein leeres Inventar** - nicht ein
  Fehler. Pruefen ist deshalb: Relikt-Zahl im Fenster vor und nach dem Fix
  gleich (der Nutzer hat 309 in einem Slot, 234 im zweiten Save), `Rescan`
  liefert dieselbe Zahl, `Load equipped` findet dieselben Relikte.
- Kanten, die der Waechter abdeckt und die eine Handprobe bestaetigen kann:
  erster Record eines Slots, letzter Record vor `len-24`, Save ohne
  Loadout-Tabelle (der 234er Slot - `loadout_error` ist dort normal).
- **Neu beobachtbar:** `Rescan` sollte spuerbar schneller sein. Der Start ist
  es nur teilweise - der Rest ist Entschluesseln und der Loadout-Walk (unten).

## An director

1. **Derselbe Vorfilter fehlt an der zweiten Stelle, und sie ist jetzt die
   teuerste.** L-006-Suche ueber den ganzen Baum, zwei unabhaengige Masken:
   `range\(0, .*, 4\)` -> **3 Treffer** (1 Produktivcode, 2 in Tests),
   `for off in range` -> **3 Treffer** (1 Produktivcode, 2 in Tests). Die eine
   Produktivstelle ist `find_loadout_table` (`nrdata/savefile.py:410`) - der
   gleiche volle Vier-Byte-Walk, nur nach dem Marker `0x0000ff01`.
   **Gemessen heute, gleiche Umgebung, n=5:** 244,3 ms auf dem Slot **ohne**
   Tabelle (er laeuft alles ab und findet nichts) und 120,8 ms auf dem guten,
   zusammen **365 ms** - nach diesem Fix der groesste verbleibende Posten des
   Moduls, und **groesser als die 250-ms-Schwelle, an der AD-029 Stufe B
   haengt**. Ich habe ihn **nicht** angefasst (ausserhalb U1). Empfehlung: ein
   eigener kleiner `developer`-Auftrag derselben Form (`bytes.find` auf den
   Marker), **vor** U3 - sonst misst U3 einen Wert, den ein Folgeauftrag
   sofort wieder verschiebt. Alternativ U3 zuerst und die Zahl bewusst mit dem
   Loadout-Walk drin lesen; dann bitte im Auftrag sagen, welche der beiden.
2. **Die Verweigerung bei gebrochener Id-Annahme ist hart.** AD-029 verlangt
   "laut werden"; das habe ich gebaut. Konsequenz: ein Spiel-Patch, der
   Relikte ab `0x01000000` nummeriert, macht den Spielstand fuer das Programm
   **unlesbar**, bis eine neue Fassung kommt - statt still weniger zu finden.
   Der Gegenentwurf (Rueckfall auf den vollen Walk, T-118 nennt dafuer den
   `array`-Weg mit 2,1x) waere korrekt, aber leise. Wenn der Nutzer lieber
   "langsam und vollstaendig" als "verweigert" haette, ist das eine kleine
   Aenderung - aber es ist eine Produktentscheidung, nicht meine.
3. **Wortlaut-Reibung ausserhalb meines Umfangs:** `app.py:3445` setzt jede
   `ValueError` aus dem Leser als `"Save could not be read: {exc}"` vor den
   Text. Meine Meldung sagt "nothing is wrong with the save" - das
   widerspricht dem Praefix. `nrplanner/app.py` war mir verboten; Fall fuer
   `ui-ux-designer` oder einen Folgeauftrag.
4. **Kein Debt hinterlassen**, keine neue Abhaengigkeit, kein Netzwerkzugriff,
   kein Schreibzugriff auf den Spielstand.
5. **Fuer den `architect` zur Kenntnis (T-134 laeuft parallel):** AD-029
   nennt "28 Slots gelesen, einer gebraucht" und "543 Records" ist neu -
   **beide** Spielstanddateien tragen einen bestueckten `USER_DATA000`
   (234 und 309), nicht nur einer. An der Entscheidung aendert das nichts.

## An ui-ux-designer

Keine Abweichung von einer UI-Vorgabe; die Oberflaeche ist nicht beruehrt.
Der einzige neue Text, den ein Spieler je sehen kann, ist die Verweigerung aus
Punkt 3 oben - englisch (A8), ohne Pfad, ohne `.sl2`.
