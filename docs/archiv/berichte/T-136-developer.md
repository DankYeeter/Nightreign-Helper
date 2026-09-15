# T-136 - Vorfilter fuer find_loadout_table (developer)

```
STATUS: erledigt
AUFTRAG: T-136 - Derselbe Walk steckt noch in find_loadout_table (AD-029/QA-209)
GELESEN: docs/tasks/T-136.md, docs/berichte/T-133-developer.md,
  nrdata/savefile.py (ganz), tests/test_loadout_table.py,
  tests/test_hostile_savefile.py (SEC-024-Abschnitt, Zeilen 464-638),
  nrplanner/inventory.py (nur lesend: load, _scan_save, _decrypt_slots,
  Zeilen 190-320), tests/conftest.py
GEÄNDERT: nrdata/savefile.py (committet b5c01b6),
  tests/test_loadout_table_prefilter.py (neu, committet b5c01b6),
  docs/berichte/T-136-developer.md (diese Datei)
ANNAHMEN: keine offenen. Eine Annahme wurde beim Messen widerlegt und
  korrigiert (siehe unten: das Messskript musste denselben Decrypt-Pfad wie
  nrplanner.inventory._decrypt_slots nehmen, nicht savefile.read()/
  decrypt_member -- letzteres liefert 0 von 28 Slots mit gueltiger
  Pruefsumme auf diesem Save, weil die Produktivfunktion die MD5-Pruefung
  gar nicht macht).
NÄCHSTER: performance-tuner (U3, jetzt ohne die 365-ms-Verschiebung durch
  diesen Auftrag) oder director fuer die Priorisierung von AD-029 Stufe B
BLOCKIERT DURCH: nichts
```

## Umgesetzt

**`nrdata/savefile.py`** (einzige Produktivdatei):

- **`_loadout_marker_offsets(slot_data)`** - der Vorfilter, unmittelbar vor
  `find_loadout_table`. Der Marker, nach dem `find_loadout_table`'s aeusserer
  Walk sucht (`HERO_MARKER_BASE + 1` = `0x0000ff01`), ist anders als die
  Relikt-Id aus T-133 ein **fester, bekannter Wert** und keine Spieldatum.
  `bytes.find` sucht deshalb direkt nach den vollen vier Bytes des Markers
  (nicht nur einem kennzeichnenden Byte wie bei der Relikt-Id) und die
  Schleife filtert nur noch auf Vier-Byte-Ausrichtung (`pos % 4 == 0`).
  Ausrichtung (`pos % 4 == 0`) und Obergrenze (`len(slot_data) - 8`,
  exklusiv) sind woertlich die des alten `range(0, limit - 8, 4)`-Walks.
- `find_loadout_table`: die Zeile `for off in range(0, max(limit - 8, 0), 4):`
  plus der anschliessende `struct.unpack_from`-Vergleich (3 Zeilen) ersetzt
  durch `for off in _loadout_marker_offsets(slot_data):`. Der
  `struct.unpack_from`-Abgleich entfaellt vollstaendig, weil `bytes.find`
  bereits den exakten 4-Byte-Treffer liefert -- anders als bei
  `_relic_id_offsets`, wo `read_owned_relics` den Doppel-Id-Abgleich
  weiterhin selbst macht, weil dort nur ein einzelnes kennzeichnendes Byte
  gesucht wird. Rumpf, `allowed_starts`, `starts`-Zaehlung und die
  SEC-024-Verweigerung: **unveraendert**.
- Neue Konstante `_LOADOUT_MARKER = struct.pack("<I", HERO_MARKER_BASE + 1)`,
  aus dem Marker gepackt statt separat ausgeschrieben, damit beide nicht
  auseinanderlaufen (dieselbe Begruendung wie `_ID_TOP_BYTE` in T-133).

**`tests/test_loadout_table_prefilter.py`** (neu, 14 Faelle, 1,8 s). Die
Erwartung kommt nie vom Vorfilter: `full_walk` ist der alte
`find_loadout_table`-Rumpf woertlich als eigene Funktion in der Testdatei,
gegen die verglichen wird (L-008b) -- dieselbe Form wie
`tests/test_relic_scan_prefilter.py`.

## Die vier harten Punkte

### 1. Gleichheitsprobe am echten Spielstand, mit Positivkontrolle

Skript `…/scratchpad/T-136/equal_and_measure.py`, **nur lesend**. Traegt
denselben `full_walk` woertlich in sich.

**Wichtige Korrektur unterwegs:** Der erste Anlauf nutzte
`savefile.read()`/`decrypt_member` (die MD5-gepruefte Payload) und fand
**0 von 28 gueltigen Slots** -- die Produktivfunktion `_scan_save` prueft die
MD5 gar nicht, sondern arbeitet mit dem rohen AES-entschluesselten Klartext
(`nrplanner/inventory.py:201-212`, `_decrypt_slots`). `find_loadout_table`s
Versaetze sind nur gegen genau diese Bytes sinnvoll (die MD5-Payload ist um
4 Byte verschoben und kuerzer). Das Messskript wurde auf
`inventory._decrypt_slots` umgestellt.

**Gefuehrt ueber 28 von 28 Slots aus 2 Dateien:**

```
-> 28 decrypted, checksum-valid slots from 2 files
  NR0000.sl2/USER_DATA000: 10 groups found
28 of 28 slots equal
positive control (byte 126616 of NR0000.sl2/USER_DATA000's own first
marker flipped): DIFFERENT
```

Nur **ein** Slot von 28 traegt eine erkennbare Tabelle -- die uebrigen 27
sagen "not found", beide Walks stimmen darin ueberein. **Positivkontrolle:**
ein Byte des ersten gefundenen Markers geflippt -> `DIFFERENT`. Der erste
Versuch (Byte 0 der ganzen Datei geflippt) meldete faelschlich "equal", weil
Byte 0 weit weg von jeder gelesenen Struktur liegt -- das war die Kontrolle,
die die Kontrolle gefunden hat (derselbe Fehlerpfad, den T-133 schon einmal
gemeldet hat, hier an anderer Stelle).

**Nicht gefuehrt:** an einer praeparierten Datei -- das deckt bereits
`tests/test_hostile_savefile.py` (SEC-024-Abschnitt, unveraendert gruen, s.
unten).

### 2. Der Slot ohne Tabelle ist der teure Fall

`tests/test_loadout_table_prefilter.py::test_a_slot_with_no_marker_at_all_is_the_expensive_case_made_cheap`
prueft das direkt: 1 MiB Nullen, beide Walks sagen "refused", `both_walks_agree`
vergleicht die volle Fehlermeldung. Am echten Save ist genau das der teure
Fall (240,6 ms vorher) -- "nichts gefunden" bleibt ein gueltiges Ergebnis,
kein Fehler; `nrplanner/inventory.py` faengt die `ValueError` unveraendert in
`loadout_error` ab (Zeilen 310-314, nicht angefasst).

### 3. SEC-024 unangetastet, `load()` bricht nicht frueher ab

- `MIN_BYTES_PER_LOADOUT_TABLE`, `allowed_starts`, der `raise` an der Stelle,
  die die Grenze ueberschreitet: **unveraendert** (`git diff` zeigt nur den
  Offset-Erzeuger getauscht).
- Bestehende SEC-024-Tests unveraendert gruen (siehe Suite unten):
  `test_a_slot_packed_with_table_starts_is_a_data_error`,
  `test_a_slot_with_as_many_table_starts_as_it_has_room_for_is_read`,
  `test_one_table_start_more_than_the_slot_can_hold_is_a_data_error`,
  `test_a_slot_at_a_real_saves_table_density_is_read_in_full`,
  `test_the_refusal_reaches_the_window_instead_of_the_console`.
- Zusaetzlich in der neuen Datei:
  `test_a_slot_that_is_nothing_but_the_marker_is_still_refused` (Gegenprobe
  durch den Vorfilter).
- `nrplanner/inventory.py` und `nrplanner/app.py`: **nicht angefasst**;
  `load()` liest weiter alle Dateien und Slots.

### 4. Vorher/nachher, mit Messumgebung (L-009)

**Messumgebung:** Windows 10 Home 19045 x64, AMD Ryzen (Family 25, 16
Threads), Python 3.12.10 aus `.venv`, kein Qt und keine Oberflaeche
beteiligt, kein cProfile, Slots einmal entschluesselt und im Speicher
gehalten, warmer Dateicache, derselbe Prozess fuer alle Werte, Median aus
n=5. Zeiten, keine Oberflaechenmasse -- physisch/logisch entfaellt.

| Was | vorher | nachher |
|---|---|---|
| Slot ohne Tabelle (teurer Fall) | **240,6 ms** (min 235,9-237,9, max 262,1-266,0) | **124,4 ms** (min 124,0-125,0, max 126,8-127,3) |
| Slot mit Tabelle (guter Fall) | **119,9-121,3 ms** (min 113,9-118,1, max 124,0-167,3) | **8,5-8,7 ms** (min 8,4-8,5, max 8,7-9,5) |
| **zusammen** | **~360,5-360,9 ms** | **~133,1-134,3 ms** |

(Zwei Werte je Zelle: der Lauf wurde zweimal ausgefuehrt, einmal vor und
einmal nach einer reinen Docstring-Ergaenzung; beide Laeufe liegen im selben
Band, der Docstring-Text im Code zitiert den zweiten.)

**Auffaellig, und im Docstring von `_loadout_marker_offsets` festgehalten:**
Der Slot **ohne** Tabelle gewinnt nur Faktor **1,9**, nicht die 14-51x aus
T-133 oder dem guten Slot hier. `bytes.find` laeuft den ganzen Slot in C ab,
wenn der Marker gar nicht vorkommt -- der Gewinn ist dort der Sprung von
Python nach C, nicht das Ueberspringen von Bytes wie bei der Relikt-Id, wo
ein Treffer den Walk frueh abbricht. Das war so nicht vorherzusehen, ohne
tatsaechlich zu messen.

**Kombiniert 133-134 ms liegt unter der 250-ms-Schwelle**, an der laut T-133
und diesem Auftrag AD-029 Stufe B haengt.

## Waechter und Mutationsbeweis

`tests/test_loadout_table_prefilter.py`, 14 Faelle, **1,8 s**, Standardlauf,
kein Skip, kein Marker.

Mutationsskript `…/scratchpad/T-136/mutate.py`: Datei vor jeder Mutation aus
`…/scratchpad/T-136/savefile.py.orig` **kopiert** (kein `git checkout`),
Mutation textuell eingespielt, `tests/test_loadout_table_prefilter.py`
laufen lassen, Original zurueckkopiert.

| Mutant | Ergebnis |
|---|---|
| M1 Ausrichtungspruefung entfernt (`if True: yield pos`) | KILLED (3 failed) |
| M2 Suche beginnt bei Byte 1 statt 0 | KILLED (3 failed) |
| M3 Obergrenze `<` -> `<=` | KILLED (1 failed) |
| M4 Schritt `pos + 1` -> `pos + 4` | **SURVIVED** -- siehe unten |
| M5 falscher Marker gesucht (`HERO_MARKER_BASE + 2`) | KILLED (8 failed) |
| M6 zurueckgegebener Versatz `pos + 4` statt `pos` | KILLED (7 failed) |
| M9 Obergrenze `-4` statt `-8` | KILLED (1 failed) |
| M7 Vorfilter durch unfiltrierten vollen Bereich ersetzt (`yield from range(0, limit, 4)`, kein nachgelagerter Abgleich mehr vorhanden) | KILLED (12 failed) |
| M8 Vorfilter durch den alten `range`+`unpack_from`-Walk mit **identischer** Filterung nachgebaut | **SURVIVED (echtes Aequivalent)** |

**M4 und M8 sind beide echte Verhaltensgleichheit, kein Testluecke.**
Begruendung, nicht nur Beobachtung: Der Marker `0x0000ff01`
(`b"\x01\xff\x00\x00"`) ueberlappt sich nachweislich nicht selbst -- keines
seiner Suffixe der Laenge 1-3 stimmt mit dem entsprechenden Praefix
ueberein. Zwei echte Treffer koennen deshalb nie weniger als 4 Byte
auseinanderliegen, und `find(marker, start)` prueft `start` selbst mit --
"Schritt +1" und "Schritt +4" liefern fuer **jeden** Input identisch dieselbe
Trefferliste (M4). Und weil `find_loadout_table` (anders als
`read_owned_relics` in T-133) **keinen** nachgelagerten Abgleich mehr hat,
ist die einzige Art, den Vorfilter unbemerkt langsam zu machen, ihn exakt so
neu zu implementieren wie er spezifiziert ist -- das ist M8, mathematisch von
aussen ununterscheidbar (dieselbe Eingabe -> dieselbe Ausgabe, fuer jede
Eingabe). Beide Mutanten sind hier gemeldet statt stillschweigend
nachgebessert (L-008c): Ich habe keinen dritten Weg gefunden, sie mit einem
Verhaltenstest zu toeten, weil keiner existiert -- nur ein Test auf
Implementierungsdetails (z. B. Aufrufzaehler von `bytes.find`) koennte das,
und das haette T-133 fuer die analoge Stelle ebenfalls nicht getan.

**Rot-vorher, je Schutzmassnahme einzeln abgeschaltet:** M1 (Ausrichtung) und
M9 (Obergrenze) sind genau diese Probe -- jede einzelne Abschaltung faerbt
Faelle rot, die kein anderer Mutant rot faerbt.

**L-006-Suche nach dem Fix**, zwei unabhaengige Masken, ueber den ganzen
Baum: `range\(0, .*, 4\)` -> 8 Treffer, davon **0 in Produktivcode**
(`nrdata/`, `nrplanner/`), 2 in Tests (die beiden woertlichen `full_walk`-
Kopien in `test_relic_scan_prefilter.py` und `test_loadout_table_prefilter.py`),
6 in Dokumentation/Berichten (historisch). `for off in range` -> 6 Treffer,
gleiches Bild: 0 in Produktivcode, 2 in Tests (dieselben Kopien),
1 `tests/test_hostile_savefile.py:313` mit variabler `stride` (kein Treffer
der Maske im engeren Sinn, unveraendert, nicht mein Code), Rest
Dokumentation. Beide Stellen aus T-133s Befund (`_relic_id_offsets`,
`find_loadout_table`) sind jetzt behoben; keine dritte Produktivstelle
gefunden.

## Suite

```
.venv\Scripts\python.exe -m pytest -n auto -q
1350 passed, 9 skipped in 185.21s
```

Gegen die Vorgabe **1336 passed, 9 skipped, 0 failed**: **+14 = genau die
neue Datei**, 9 Skips unveraendert, 0 failed. Danach noch eine reine
Docstring-Ergaenzung an `_loadout_marker_offsets` (Messzahlen eingetragen,
kein Verhaltensaenderung) -- erneut gezielt gegen die vier betroffenen
Testdateien gelaufen (`test_loadout_table_prefilter.py`,
`test_loadout_table.py`, `test_hostile_savefile.py`,
`test_relic_scan_prefilter.py`, 64 passed), die volle Suite dafuer nicht
erneut sechs Minuten gelaufen, weil an Verhalten nichts mehr geaendert war.

## Datenverzeichnisse - Nachweis der drei Umlenkungen

```
LOCALAPPDATA -> …\scratchpad\T-136\local
APPDATA      -> …\scratchpad\T-136\roaming
settings org -> DankYeeterT-136
save_roots()[0] (proves the redirect) -> …\scratchpad\T-136\roaming\Nightreign
```

Der feste Testabzug wurde **kopiert** (nicht neu gebaut) nach
`…\T-136\local\NightreignHelper`. Den Spielstand las das Skript ueber
`Path.home()/AppData/Roaming/Nightreign`, ausdruecklich getrennt von der
umgelenkten `APPDATA` -- nur lesend (`savefile.read` fuer die
Gleichheitsprobe-Metadaten, `inventory._decrypt_slots` fuer die Slots
selbst; kein Schreibzugriff irgendwo auf den Pfad).

**Gegenprobe nach dem Lauf:**
- `NR0000.sl2` (Konto 76561198073567627): mtime `1758385293.067532` vor und
  nach dem Lauf identisch.
- `NR0000.sl2` (Konto 76561198179244962): mtime `1788286942.0` vor und nach
  dem Lauf identisch.
- Umgelenktes `…\T-136\roaming`: keine neue `Nightreign`-Verknuepfung, keine
  QSettings-Datei (das Skript importiert `nrplanner.inventory`, nicht
  `nrplanner.favourites`/`app` -- QSettings wurde nie beruehrt).
- Echtes Startmenue (`%APPDATA%\Microsoft\Windows\Start Menu\Programs`):
  nur der vorhandene Steam-Eintrag (`Steam\ELDEN RING NIGHTREIGN.url`),
  keine neue Datei.
- Kein laufender Prozess (`tasklist | grep -i nightreign` -> leer).

## DoD

- [x] Anforderung verstanden, Annahmen dokumentiert (eine Annahme unterwegs
      widerlegt und korrigiert, s. o.)
- [x] Build & Tests gruen in der benannten Testumgebung (Windows 10 x64)
- [x] Neue Tests fuer neue Logik, mit vollem Mutationsbeweis inkl. zweier
      gemeldeter, begruendeter Aequivalenz-Ueberlebender
- [x] Linter: **entfaellt**, das Projekt hat keinen konfiguriert
- [x] Keine Secrets, keine TODOs, kein toter Code
- [x] Nur `nrdata/savefile.py` und `tests/` beruehrt; `ARCHITECTURE.md`,
      `UI_SPEC.md`, `docs/state.md` sind im Arbeitsbaum von parallelen
      Rollen geaendert und **nicht** von mir committet
- [x] QA-Kriterien aus dem Auftrag selbst durchgespielt (Gleichheitsprobe,
      Positivkontrolle, SEC-024-Gegenprobe, Datenverzeichnis-Nachweis)
- Linux/macOS: **ungeprueft** und kein Ziel.

## An director

1. **Beide von T-133 gemeldeten Fundstellen sind jetzt behoben.** Kombiniert
   liegt der Modul-Rest bei **133,1 ms**, unter der 250-ms-Schwelle aus
   AD-029 Stufe B -- der Auftrag lief wie entschieden vor U3, damit der
   `performance-tuner` keinen bereits ueberholten Wert misst.
2. **Der Slot-ohne-Tabelle-Fall gewinnt nur Faktor 1,9, nicht die 14-51x der
   anderen Faelle** (Punkt 4 oben) -- eine reine C-vs-Python-Verbesserung,
   weil `bytes.find` bei einem fehlenden Marker den ganzen Slot ablaufen
   muss. Falls AD-029 Stufe B trotzdem noch fuer noetig gehalten wird, ist
   dieser Fall (27 von 28 real gemessenen Slots) der massgebliche.
3. **Zwei Mutanten sind echte Verhaltensgleichheit** (M4, M8 oben), keine
   Testluecke -- mathematisch begruendet ueber die Selbstueberlappung des
   4-Byte-Markers. Kein Nachbesserungsbedarf, nur zur Kenntnis, falls ein
   spaeterer Mutationslauf dieselben zwei wieder als "survived" meldet.
4. **Fund waehrend der Arbeit, ausserhalb des Auftrags:** Das erste
   Gleichheitsprobe-Skript benutzte `savefile.read()`/`decrypt_member`
   (die MD5-gepruefte Payload) und fand 0 von 28 gueltigen Slots, weil die
   Produktivfunktion `nrplanner/inventory.py::_decrypt_slots` die MD5
   ueberhaupt nicht prueft, sondern mit dem rohen AES-Klartext arbeitet
   (Zeilen 201-212). `savefile.read()`/`decrypt_member` scheinen damit ein
   zweiter, in der Praxis ungenutzter Lesepfad zu sein -- verwendet nur in
   `tests/test_relic_scan_prefilter.py`(nicht direkt, dort eigene Kopie) und
   nirgends in `nrplanner/`. Nicht selbst angefasst (ausserhalb `nrdata/
   savefile.py`s Kernaenderung waere das eine zweite, unbeauftragte
   Aenderung); falls das ungenutzter Code ist, waere das ein Fall fuer den
   `performance-tuner` oder einen eigenen kleinen Aufraeum-Auftrag,
   **keine Debt aus diesem Task**.
5. Kein Netzwerkzugriff, keine neue Abhaengigkeit, kein Schreibzugriff auf
   den Spielstand.

## An qa-engineer

- **Das Bild, das ein Bruch macht, ist ein leeres "Stored builds"-Feld** --
  nicht ein Fehler (wie bei T-133s Relikt-Fund). Pruefen: gespeicherte
  Builds vor und nach dem Fix identisch (der Nutzer hat rund 110 gespeicherte
  Builds), `Rescan` liefert dieselben Builds.
- Kanten, die der Waechter abdeckt und eine Handprobe bestaetigen kann:
  Marker am allerersten moeglichen Versatz, am letzten erreichbaren Versatz
  vor der alten Obergrenze, Save ganz ohne Tabelle (Normalfall fuer 27 von
  28 realen Slots).
- **Neu beobachtbar:** Save-Scan/Rescan sollte insgesamt spuerbar schneller
  sein als vor T-133+T-136 zusammen, besonders auf einem Slot ohne Tabelle.

## An ui-ux-designer

Keine Abweichung; die Oberflaeche ist nicht beruehrt, keine neue oder
geaenderte Nutzertext-Meldung.
