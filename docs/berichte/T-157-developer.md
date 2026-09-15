# T-157 - SEC-029 zu Ende, und drei Altlasten (developer)

```
STATUS: erledigt
AUFTRAG: T-157 - SEC-029 zu Ende, und drei Altlasten (developer)
GELESEN: docs/tasks/T-157.md, ~/.claude/agents/_rahmen.md, CLAUDE.md,
  nrplanner/inventory.py, nrplanner/app.py (Spielstandteil),
  tests/test_save_path_memory.py, tests/test_save_read_in_the_background.py,
  tests/test_hostile_savefile.py, DESIGN_REVIEW.md 535-580 (DR-005),
  UI_SPEC.md 2990-3070 (S1-S5) und 7600-7680 (Paragraph 9 (f)/(g)),
  docs/berichte/T-142-developer.md, nrdata/savefile.py (read, Loadout)
GEAENDERT: nrplanner/inventory.py, nrplanner/app.py,
  tests/test_save_path_memory.py, tests/test_save_read_in_the_background.py,
  docs/berichte/T-157-developer.md (diese Datei);
  Commits 8f68b49, aec3d05, 81fc6ce, 60f24c6, 3069344
ANNAHMEN: keine geraten; die drei Entscheidungen, die ich getroffen habe,
  stehen unten unter "Entscheidungen" mit Begruendung
NAECHSTER: director
BLOCKIERT DURCH: nichts fuer meinen Auftrag. Aber die Suite ist **nicht**
  gruen: ein Fall in tests/test_differential_track.py faellt, weil meine
  Aenderung einen Mutationsanker von T-156 verschoben hat. Die Reparatur ist
  eine Zeile in scripts/differential/mutate.py - ausserhalb meiner Whitelist,
  darum gemeldet und nicht angefasst (Details unten).
```

## Vorbedingungen - nachgewiesen, nicht behauptet

**Drei Umlenkungen, mit Positivkontrolle** (`.venv/Scripts/python.exe`,
Skript `…/scratchpad/T-157/where.py`, das `paths.cache_dir()`,
`shortcut.shortcut_path()` und `favourites.ORG` ausgibt):

| | ohne Umlenkung (Positivkontrolle) | mit Umlenkung |
|---|---|---|
| `cache_dir()` | `C:\Users\Daniel\AppData\Local\NightreignHelper` | `…\scratchpad\T-157\local\NightreignHelper` |
| `shortcut_path()` | `C:\Users\Daniel\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Nightreign Helper.lnk` | `…\scratchpad\T-157\roaming\…\Nightreign Helper.lnk` |
| `favourites.ORG` | `DankYeeter` | `DankYeeterT-157` |

Die Positivkontrolle zeigt, dass die Messung wirklich auf den Ort des Spielers
zeigt, wenn nichts umlenkt. Alle Testlaeufe dieses Auftrags liefen mit
`LOCALAPPDATA`, `APPDATA` und `NIGHTREIGN_SETTINGS_ORG` auf den Scratchpad.
Unter pytest ueberschreibt `tests/conftest.py` den Org-Wert auf
`DankYeeterTests` - auch das ist vom Speicher des Spielers weg, aber es ist
nicht mein Wert; das gehoert gesagt.

**`APPDATA` umgelenkt heisst nicht "der Spielstand ist weg":**
`savefile.save_roots()` sucht zusaetzlich unbedingt unter
`~/AppData/Roaming/Nightreign`. Die spielstandabhaengigen Faelle lesen also
weiter die echte Datei - lesend.

**Testabzug kopiert**, nicht darauf gezeigt: 841 Dateien, 22 MB, nach
`…/scratchpad/T-157/local/NightreignHelper`.

**Spielstand unveraendert.** Vorher/nachher `find -printf "%T@ %s %p"` ueber
`%APPDATA%/Nightreign` (4 Dateien) plus `md5sum` beider `NR0000.sl2`:

```
1758385293.0675320000 19531312 …/76561198073567627/NR0000.sl2   c2da42ee2124a51233e6630b8a07eac8
1788286942.0000000000 19531312 …/76561198179244962/NR0000.sl2   e52bd9dd2fbab319dec22b79985f14b3
```

`diff` der beiden Aufstellungen: leer. Keine Verknuepfung im echten
Startmenue (nachgesehen, `Programs/` enthaelt nichts mit "Nightreign").

## Umgesetzt

### 1. SEC-029 - der Deckel sitzt jetzt an der Stelle, die alloziert

`nrplanner/inventory.py`: `LARGEST_SAVE_TO_READ` (unveraendert 256 MiB) und
`refuse_a_size_no_save_can_have(size)` sind aus `app.py` hierher gezogen, und
`_read_settled` fragt vor `read_bytes()` mit der Groesse, die es fuer die
Settling-Pruefung ohnehin schon hat (`before.st_size`) - eine `stat`, zwei
Fragen. `app._refuse_a_file_no_save_can_be` stellt dieselbe Frage weiter und
ist nur der Erste, der sie stellt; das ist kein zweiter Deckel mit eigener
Zahl, sondern derselbe Aufruf.

Warum der Aufrufer bleibt: er steht **vor** dem zweiten Lesevorgang in
`read_the_save` (`savefile.read`), der S3 von S4 trennt. Ohne ihn bekaeme
dieser Aufruf die grosse Datei doch noch zu sehen.

Die Herleitung der Zahl ist woertlich mitgezogen (19 531 312 Byte je
Spielstand, beide Konten, Faktor 13,7) und steht jetzt bei der Zahl.

### 2. A7 - ein gefundener, unlesbarer Spielstand meldet nicht mehr "kein Spielstand"

`nrplanner/inventory.py`: neue Ausnahme `SaveNotReadable(ValueError)`.
`_scan_save` gibt bei einem nicht lesbaren File nicht mehr das unveraenderte
`best` zurueck, sondern wirft sie; `scan` faengt sie **pro Datei** ab - ein
kaputtes File bricht den Scan weiterhin nicht ab - und wirft sie am Ende nur,
wenn ueberhaupt nichts Gutes dabei war. Aufgehoben wird der Grund des
**ersten** Kandidaten in der Sortierung, also des neuesten.

`OSError` wird mit `strerror` gemeldet, nie mit `str(exc)`: dessen Text
enthaelt den vollen Pfad, und der Save-Ordner traegt die Steam-Konto-Id
(AK-126). Dafuer gibt es einen eigenen Fall und eine eigene Mutation.

**Kein neuer Text.** Das Fenster hat den Satz schon: `UNREADABLE_SAVE`
(`Save could not be read: <Grund>`), `UI_SPEC` T-141 Paragraph 9 (g), und
`_on_save_failed` setzt ihn auf dem Automatikweg bereits. Was gefehlt hat, war
das Stueck davor: `read_the_save` gab `None` zurueck, wo es haette scheitern
muessen. Erfunden habe ich nichts.

Die Lagen, wie sie jetzt auseinandergehen:

| Lage | Antwort | Satz |
|---|---|---|
| kein File gefunden | `None` | `NO_SAVE_FOUND` (S5) |
| File gefunden, lesbar, keine Relikte | `None` | unveraendert (das ist QA-008, nicht angefasst) |
| File gefunden, nicht lesbar | `SaveNotReadable` | `Save could not be read: <Grund>` |

`load()` bricht **nicht** frueher ab: es ruft weiter `scan` und dann `build`.
Was sich aendert: wo alle gefundenen Saves unlesbar sind, wirft `load` jetzt,
statt `None` zu liefern - genau wie `scan`, und das ist der Sinn der Funktion
("die zwei Haelften in einem Aufruf"). Der einzige Aufrufer ausserhalb der
Tests ist `scripts/measure_advisor_language.py` (nur im Text erwaehnt), der
gegen den echten, lesbaren Spielstand laeuft.

### 3. Der Fall, den kein Weg getroffen hat

`tests/test_save_read_in_the_background.py::test_the_cards_get_the_stock_when_no_build_is_worn`:
ein `SaveScan`, dessen Loadouts alle `selected=False` tragen - der frische
Charakter, der Vessels hat und keines davon traegt. `reload_chalices` gibt an
`load_equipped` ab (der Nightfarer *hat* Builds), und `load_equipped` steigt
bei `selected_loadout(...) is None` aus, vor `apply_chalice`. Damit ist
`_hand_the_stock_to_the_slots` das Einzige zwischen der Ankunft und sechs
Karten, die nichts anbieten.

Behauptet wird, was der Spieler sieht: `(n available)` in der Ueberschrift
jeder aktiven Karte - geschrieben aus dem, was die **Karte** haelt, nicht aus
dem, was das Fenster haelt (L-008 b).

### 4. Der Waechter, der aus dem falschen Grund rot wurde

`a-read-per-press` wurde bisher durch Prozessabbruch rot. Ursache ist nicht
nur der Thread: `SaveReader` haelt die einzige Referenz auf **Thread und
Worker**, ein zweites `start()` ueberschreibt beide, und Qt zerstoert dann
einen laufenden Thread und ein Objekt, in dem dieser Thread gerade steht.

Neuer Helfer `whatever_the_reader_is_running(reader)` im Testmodul; beide
Faelle, die waehrend eines Lesens druecken, halten damit fest, was der Reader
laufen hat - der Controller-Fall und
`test_pressing_rescan_during_a_read_starts_no_second_one`, das fuenfmal
drueckt und deshalb **jedes** gestartete Lesen aufsammelt. Unter der
geltenden Regel ist das nach jedem Druecken dasselbe Paar und kostet nichts.

Messung, drei Stufen (jeweils volle Datei, Mutation `a-read-per-press`):

| Stand | Ergebnis |
|---|---|
| vorher (T-142) | Prozessabbruch, keine Zusammenfassung |
| nur Thread gehalten | `exit=3221226505` (0xC0000409), keine Zusammenfassung - der Lauf stirbt schon in `test_pressing_rescan_during_a_read_starts_no_second_one`, lange vor dem Controller-Fall |
| Thread und Worker, beide Faelle | `exit=1`, `2 failed, 22 passed`, erster Fall `test_pressing_rescan_during_a_read_starts_no_second_one` (`assert first.calls == 2`) |

## Entscheidungen

1. **Punkt 2 ohne eigenen Textentwurf.** `UI_SPEC` Paragraph 9 (g) hat den
   Satz, das Fenster hat die Verdrahtung, es fehlte nur die Meldung von
   unten. Kein Befund an den `ui-ux-designer` noetig.
2. **Beweis auch fuer 2 und 4**, obwohl der Auftrag dort einen Waechter ohne
   Beweis erlaubt: die Mutationen waren billig (drei Laeufe a 35 s fuer
   Punkt 2), und bei Punkt 4 war der Beweis die einzige Art, ueberhaupt zu
   sehen, dass die erste Fassung noch nichts taugte.
3. **Der Aufrufer-Deckel in `app.py` bleibt**, statt ihn durch den neuen zu
   ersetzen. Zwei Gruende: er steht vor `savefile.read`, und der bestehende
   Fall mit dem Spion auf `inventory.scan` ("die Datei wurde gelesen, bevor
   ihre Groesse angesehen wurde") bleibt damit scharf. Beide Stellen haben
   eine eigene toetende Mutation - es ist kein Fall von "zwei Guertel, jeder
   ueberlebt allein", weil sie auf **verschiedenen Wegen** liegen.

## Mutationskampagne - 12 Mutationen, 12 getoetet

Auf einem frischen Klon (`git clone . …/scratchpad/T-157/klon`), Treiber
`…/scratchpad/T-157/mutate.py`, jede Mutation einzeln angewandt, Datei vorher
kopiert und danach zurueckkopiert (nie `git checkout`). Der Interpreter ist
das `.venv` des Hauptbaums, der gepruefte Code kommt aus dem Klon
(nachgewiesen: `inventory.__file__` zeigt in den Klon).

| Mutation | Datei | Ergebnis | erster fallender Fall |
|---|---|---|---|
| `no-limit-in-the-read` | inventory.py | KILLED `1 failed, 35 passed` | `test_the_automatic_route_is_held_to_the_same_limit` |
| `the-limit-refuses-nothing` | inventory.py | KILLED `2 failed, 34 passed` | `test_a_file_too_large_to_be_a_save_is_not_read` |
| `the-limit-is-twice-as-large` | inventory.py | KILLED `1 failed, 35 passed` | `test_the_limit_is_far_above_a_real_save` |
| `the-limit-is-below-a-real-save` | inventory.py | KILLED `2 failed, 30 passed, 4 errors` | `test_a_save_of_the_ordinary_size_is_read` (Kontrolle) |
| `the-caller-does-not-ask` | app.py | KILLED `1 failed, 35 passed` | `test_a_file_too_large_to_be_a_save_is_not_read` |
| `any-error-is-swallowed` | inventory.py | KILLED `2 failed, 34 passed` | `test_the_automatic_route_is_held_to_the_same_limit` |
| `os-error-is-swallowed` | inventory.py | KILLED `1 failed, 35 passed` | `test_the_reason_for_an_unopenable_save_carries_no_path` |
| `the-reason-is-never-answered` | inventory.py | KILLED `3 failed, 33 passed` | `test_the_automatic_route_is_held_to_the_same_limit` |
| `the-path-goes-into-the-message` | inventory.py | KILLED `1 failed, 35 passed` | `test_the_reason_for_an_unopenable_save_carries_no_path` |
| `the-first-bad-file-ends-the-scan` | inventory.py | KILLED `1 failed, 35 passed` | `test_one_unreadable_save_does_not_hide_a_good_one` |
| `the-stock-never-reaches-the-cards` | app.py | KILLED `1 failed, 23 passed` | `test_the_cards_get_the_stock_when_no_build_is_worn` |
| `a-read-per-press` | app.py | KILLED `2 failed, 22 passed` | `test_pressing_rescan_during_a_read_starts_no_second_one` |

Keine ueberlebende Mutation. `the-stock-never-reaches-the-cards` toetet
**nur** der neue Fall - die 23 anderen bleiben gruen, womit die Analyse aus
T-142 bestaetigt ist.

**Anker fuer die Nachregistrierung** (Pfad, `old` → `new`), damit sie ohne
den Scratchpad reproduzierbar sind:

```
no-limit-in-the-read        nrplanner/inventory.py
  "        refuse_a_size_no_save_can_have(before.st_size)\n" -> ""
the-limit-refuses-nothing   nrplanner/inventory.py
  "    if size > LARGEST_SAVE_TO_READ:" -> "    if False:"
the-limit-is-twice-as-large nrplanner/inventory.py
  "LARGEST_SAVE_TO_READ = 256 * 1024 * 1024" -> "LARGEST_SAVE_TO_READ = 512 * 1024 * 1024"
the-limit-is-below-a-real-save nrplanner/inventory.py
  "LARGEST_SAVE_TO_READ = 256 * 1024 * 1024" -> "LARGEST_SAVE_TO_READ = 1024"
the-caller-does-not-ask     nrplanner/app.py
  "    inventory.refuse_a_size_no_save_can_have(path.stat().st_size)" -> "    pass"
any-error-is-swallowed      nrplanner/inventory.py
  "        raise SaveNotReadable(\n            str(exc) or exc.__class__.__name__) from exc" -> "        return best"
os-error-is-swallowed       nrplanner/inventory.py
  "        raise SaveNotReadable(\n            exc.strerror or \"the file could not be opened\") from exc" -> "        return best"
the-reason-is-never-answered nrplanner/inventory.py
  "    if best is None and unreadable:\n        raise SaveNotReadable(unreadable)\n" -> ""
the-path-goes-into-the-message nrplanner/inventory.py
  "            exc.strerror or \"the file could not be opened\") from exc" -> "            str(exc)) from exc"
the-first-bad-file-ends-the-scan nrplanner/inventory.py
  "            unreadable = unreadable or str(exc)" -> "            raise"
the-stock-never-reaches-the-cards nrplanner/app.py
  "        self._hand_the_stock_to_the_slots()" -> "        pass"
a-read-per-press            nrplanner/app.py
  "        if self._thread is not None:\n            return False\n" -> ""
```

**Warnung zu einer Mutation, die Schaden anrichten kann.** Meine erste Fassung
von `the-limit-is-twice-as-large` hiess `…-a-thousand-times-larger`
(`* 1000`). Die beiden Ueberschreitungsfaelle bauen ihre Datei aus der
Konstanten (`LARGEST_SAVE_TO_READ + 1`), also waechst die Datei mit der
Mutation mit: der Lauf hat eine **256-GB-Datei** angelegt und angefangen sie
zu lesen. Die Platte verlor 6,6 GB alle 45 s; 140 GB waren weg, bevor ich es
gestoppt und die Datei geloescht hatte (danach wieder frei: 265 GB). Wer die
Registrierung macht, nimmt `* 2` - dort faellt ohnehin nur der Fall, der das
Literal festnagelt.

## Tests

**Neu (5):**

| Fall | Datei | was er festnagelt |
|---|---|---|
| `test_the_automatic_route_is_held_to_the_same_limit` | test_save_path_memory.py | SEC-029 auf dem Weg ohne Dialog; Spion auf `savefile._members` macht "nicht gelesen" zur Behauptung |
| `test_a_save_that_cannot_be_read_is_not_reported_as_no_save` | test_save_path_memory.py | A7: der Grund kommt heraus statt `None` |
| `test_the_reason_for_an_unopenable_save_carries_no_path` | test_save_path_memory.py | AK-126 auf dem neuen Weg (OSError) |
| `test_one_unreadable_save_does_not_hide_a_good_one` | test_save_path_memory.py | die Gegenseite: ein kaputtes File nimmt kein gutes mit |
| `test_the_cards_get_the_stock_when_no_build_is_worn` | test_save_read_in_the_background.py | der Weg ohne getragenes Build |

**Rot-vorher, je Fall die Aenderung, die ihn heute bricht** (gemessen, siehe
Kampagne): Fall 1 → `refuse_a_size_no_save_can_have`-Aufruf aus
`_read_settled` entfernen; Fall 2 → das `raise SaveNotReadable` im generischen
Zweig durch `return best` ersetzen; Fall 3 → `strerror` durch `str(exc)`
ersetzen; Fall 4 → im `except` von `scan` `raise` statt Aufheben; Fall 5 →
`self._hand_the_stock_to_the_slots()` durch `pass` ersetzen. Keine davon ist
eine blosse Schnittstellenverschiebung.

**Suitezahl.** `pytest -n auto` mit allen drei Umlenkungen:

```
1 failed, 1673 passed, 9 skipped in 185.98s
```

gegen T-153 (1595 passed, 9 skipped, 0 failed). Die 78 Faelle mehr: 5 sind
meine, 73 kommen aus den parametrisierten Ankerfaellen, die T-156 parallel in
`scripts/differential/mutate.py` eingetragen hat (`aeaab8c`). Der eine
Fehlschlag ist der naechste Abschnitt.

## An den director

**1. Ein Ankerfall von T-156 faellt durch meine Aenderung - eine Zeile, in
seiner Datei, nicht in meiner.**

```
FAILED tests/test_differential_track.py::test_every_mutation_still_finds_its_anchor_in_the_real_source[the-limit-is-under-a-real-save]
  the anchor of mutation 'the-limit-is-under-a-real-save' occurs 0 times in nrplanner/app.py
```

`scripts/differential/mutate.py:5238-5241` traegt fuer diese Mutation
`path="nrplanner/app.py"` und den Anker
`LARGEST_SAVE_TO_READ = 256 * 1024 * 1024`. Die Konstante steht seit `aec3d05`
in `nrplanner/inventory.py`; dort kommt der Anker genau **einmal** vor
(nachgezaehlt: `grep -c` → 1 in inventory.py, 0 in app.py). Die Reparatur ist
also `path="nrplanner/inventory.py"`, Anker und `new` unveraendert.

`scripts/` steht nicht in meinen beruehrten Dateien, und `mutate.py` ist
genau die Datei, an der T-156 gleichzeitig arbeitet - deshalb **nicht
angefasst**. Der Ankerwaechter hat hier getan, wofuer er gebaut ist.

**2. Ich habe einen laufenden pytest-Prozess von T-156 abgeschossen.** Beim
Stoppen meines eigenen ausser Kontrolle geratenen Messlaufs (die 256-GB-Datei
oben) war mein Filter zu breit: er traf jeden `pytest`-Prozess auf
`tests/test_save_path_memory.py`. Zwei davon (`--no-header -p
no:cacheprovider`, PIDs 8436/2160, ca. 04:20) gehoerten nicht mir, sondern dem
Mutationslauf von T-156. Ein Kampagnenergebnis von T-156 gegen
`test_save_path_memory.py` aus diesem Zeitraum ist damit wertlos und muss
wiederholt werden. Meine Schuld, und der Grund: nach PID filtern, nicht nach
Kommandozeile.

**3. Debt-Kandidat, nicht behoben:** `read_the_save` liest die Datei ein
zweites Mal (`savefile.read(save_path)`), um S3 von S4 zu trennen. Seit
`scan` fuer unlesbare Files wirft, kann dieser zweite Lesevorgang nur noch
Dateien treffen, die `scan` bereits erfolgreich gelesen hat - er trennt nichts
mehr, kostet auf dem S3-Weg aber ein zweites Lesen der ganzen Datei (19,5 MB
beim echten Spielstand). Entfernen waere eine Vereinfachung mit kleinem
Restrisiko (`savefile.read` entschluesselt zusaetzlich jedes Member); ich habe
es gelassen, weil es ausserhalb des Auftrags liegt. Ort: `nrplanner/app.py`,
`read_the_save`.

**4. L-006-Suche, zwei unabhaengige Masken.**
*Maske A* `read_bytes(` ueber `nrplanner/` und `nrdata/`: **9 Treffer**
(datasource 106, firstrun 44, iconpack 26, inventory 246, dvdbnd 37,
extract 2805, iconbuild 206, regulation 16, savefile 105). Auf dem
Spielstandweg liegen genau zwei: `inventory.py:246` (jetzt gedeckelt) und
`savefile.py:105` - letzteres hat genau **einen** Aufrufer im Anwendungscode
(`app.py:1620`) und der steht hinter dem Aufrufer-Deckel. Die sieben uebrigen
lesen Dateien der Spielinstallation, nicht des Spielers; SEC-028 hat diese
Familie gemessen. Nichts davon mitbehoben - ausserhalb des Auftrags.
*Maske B* `open(..., "rb")` / `.read()`: **4 Treffer**, alle in
`nrdata/dvdbnd.py` und `nrdata/gamefiles.py`, alle mit Groessen- oder
Offsetgrenzen davor.

**5. L-006 fuer die A7-Bauform** ("eine geschluckte Ausnahme wird zu einem
Satz, der etwas anderes behauptet"): 22 `except`-Zweige in `nrplanner/`.
Durchgesehen: der eine aus dem Befund (behoben); `shortcut.py:130/146` und
`firstrun.py:580` reichen den Grund an den Nutzer weiter; `datasource.py`,
`gamepath.py:81`, `chalices.py`, `favourites.py` behandeln einen unlesbaren
**gespeicherten Wert** als abwesend, was jeweils dokumentiert und gewollt ist
(AK-125). Einziger verbleibender Kandidat derselben Form:
`nrplanner/iconpack.py:27/94` - ein nicht lesbares Symbol wird zu "kein
Symbol". Folge ist kosmetisch, kein Satz behauptet etwas Falsches. **Nicht
angefasst, kein Befund vorgeschlagen** - zur Kenntnis.

## An qa-engineer

Zu pruefen, mit einem praeparierten Spielstandordner (der echte bleibt
unberuehrt):

- **Ein einziges, unlesbares File** im Save-Ordner (z. B. 32 Byte Text unter
  dem Namen `NR0000.sl2`): die Zeile unter dem Build-Planer muss
  `Save could not be read: <Grund>` sein, **nicht** `No save file found.`.
  Der Grund darf den Ordnernamen (Konto-Id) nicht enthalten - das ist der
  Fall, den ich fuer `OSError` eigens abgesichert habe.
- **Ein kaputtes und ein gutes File nebeneinander**, das kaputte neuer: die
  Bestandsnotiz muss ganz normal die Relikte des guten nennen.
- **Ein lesbares, leeres File** (64-Byte-Container): unveraendert
  `No save file found.` - das ist QA-008 und ausdruecklich nicht Teil dieses
  Auftrags.
- **Eine sehr grosse Datei** im Save-Ordner (`fsutil file createnew`, > 256
  MiB): das Programm darf sie nicht lesen; die Zeile nennt die Groesse in MB.
  Der Speicherverbrauch des Prozesses darf dabei nicht um die Dateigroesse
  steigen - das ist der eigentliche Gegenstand von SEC-029.
- **Frischer Nightfarer ohne getragenes Build**: nach dem Lesen muessen die
  Slotkarten `(n available)` in der Ueberschrift tragen und der Reliktknopf
  muss Relikte anbieten. Im Spiel herstellbar, indem ein Nightfarer gewaehlt
  wird, fuer den ein Build gespeichert, aber keines ausgeruestet ist.

## An ui-ux-designer

Keine Abweichung, kein neuer Text. Der Satz aus `UI_SPEC` T-141 Paragraph 9
(g) (`Save could not be read: <Grund>`) erscheint jetzt auch dort, wo er
gemeint war, aber nie ankam. **Ein Hinweis zur Spec:** die Stelle
`DESIGN_REVIEW` 552-566 (DR-005) ist damit erledigt, und QA-032
("Beschaedigtes Save wird still uebersprungen; ist es das einzige, meldet das
Programm 'No save file found.'", Director-Entscheid 2026-09-02 Lesart B) ist
inhaltlich mitgeschlossen - beides traegt der `director` nach, nicht ich.
