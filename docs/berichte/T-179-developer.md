# T-179 - Die Zahl bekommt einen Ort, der Erststart einen ehrlichen Satz (developer)

```
STATUS: erledigt
AUFTRAG: T-179 - Die Zahl bekommt einen Ort, der Erststart einen ehrlichen Satz
GELESEN: docs/tasks/T-179.md; UI_SPEC.md Zeilen 9061-9700 (T-178 vollstaendig,
  AK-250 bis AK-255); CLAUDE.md; nrplanner/app.py (_build_left, _relic_count,
  _show_the_save_is_being_read, _the_save_has_been_read, _on_save_read,
  _on_save_failed, load_equipped, die Textkonstanten 570-660);
  nrplanner/firstrun.py (Modul-Docstring, w1, _Window, _height_of_the_content,
  show_the_build, _build_what_is_missing); nrplanner/inventory.py (Inventory,
  SaveScan, build, EquippedLoadout); nrdata/savefile.py (OwnedRelic, Loadout);
  nrdata/iconbuild.py (die report()-Aufrufe); scripts/setup_check.py;
  tests/conftest.py, tests/rendered.py, tests/relics.py,
  tests/test_first_run_panel.py, tests/test_save_read_in_the_background.py,
  tests/test_game_dir_recognition.py; scripts/differential/mutate.py (nur die
  registrierten Anker, gelesen ueber den Import, nicht geaendert)
GEAENDERT: nrplanner/app.py; nrplanner/firstrun.py; scripts/setup_check.py;
  tests/test_first_run_panel.py; tests/test_the_owned_total_has_its_own_line.py
  (neu); tests/test_the_first_run_promises_no_duration.py (neu);
  docs/berichte/T-179-developer.md (diese Datei).
  Zwei Commits: d93a6bb (Teil 1), b19a2cd (Teil 2). Arbeitsbaum sauber.
ANNAHMEN: (1) Die Datenbedingung der Vorgabezahl 1704 stand nicht im Auftrag;
  meine Zahl ist gegen die unten genannte Bedingung gemessen und geht mit
  1704 + 19 neuen Faellen auf. (2) `docs/state.md` und `GOAL.md` habe ich nicht
  zusaetzlich gelesen - der Auftrag zitiert A7, A11, A12 und den A11-Stand
  woertlich, und beide Zitate tragen den Auftrag.
NAECHSTER: qa-engineer
BLOCKIERT DURCH: nichts
```

## Umgesetzt

### Teil 1 - die Zahl bekommt einen Ort (`nrplanner/app.py`, Commit d93a6bb)

- **`OWNED_TOTAL` / `OWNED_TOTAL_TOOLTIP`** (bei den uebrigen Textkonstanten,
  ~Zeile 650): die beiden Wortlaute T1 und T2 aus `UI_SPEC` T-178 §4.
- **`Planner._build_left`**: ein neues `QLabel self.owned_total_label`, in der
  Luecke `layout.addSpacing(6)` unmittelbar ueber der Knopfzeile
  `Rescan save` / `Load equipped`. `font-size: 12px` ohne Farbangabe,
  `WordWrap`, `Qt.PlainText`, Mindesthoehe = eine Zeile der eigenen
  Schriftmetrik (nach `ensurePolished()`, damit die Stylesheet-Schrift gemessen
  wird und nicht die, mit der das Label geboren wurde).
- **`Planner._say_how_many_relics_are_owned`** (neu): die **einzige** Funktion,
  die dieses Widget beschreibt. Gerufen aus **`_the_save_has_been_read`** - der
  einen Stelle, durch die jedes Ende eines Lesens laeuft. `self.owned` ist
  dort in beiden Handlern bereits gesetzt (`_on_save_read` Zeile 4056,
  `_on_save_failed` Zeile 4134), also sieht der Schreiber immer den endgueltigen
  Bestand.
- **`owned_label` ist unberuehrt** - kein Wort, keine Zeile, keine Reihenfolge.
  AK-224, AK-228, AK-244, AK-245 bleiben, wie sie waren.

### Teil 2 - der Erststart (`nrplanner/firstrun.py`, `scripts/setup_check.py`, Commit b19a2cd)

- **W-A** und **W-B** woertlich in `show_the_build`, **W-C** woertlich in `w1`.
- **Die Hoehe des Bau-Zustands folgt seinem Inhalt**:
  `max(floor, layout.heightForWidth(PANEL_WIDTH))` nach `layout.activate()`,
  mit `floor = (190 if first_time else 150) + extra`. Der Zuschlag fuer die
  Bestaetigungszeile bleibt unveraendert.
- **Der Balken ist unveraendert** (`setRange(0, 0)`, `setTextVisible(False)`),
  die Statuszeile und ihre Verdrahtung ebenfalls. Kein neues Signal, keine
  Zahl ueber die Threadgrenze (AD-029, AD-006.8 unangetastet).
- **`scripts/setup_check.py:234`**: "That takes minutes rather than seconds,
  and is only needed once per patch." (auf zwei `print`-Zeilen, weil die Zeile
  sonst ueber die Randbreite ginge).

## Abweichungen und bewusste Ausweitungen - beides bitte lesen

1. **AK-252 haerter umgesetzt als der Buchstabe:** die Zeile bleibt leer, wenn
   `self.owned is None` **oder** `relic_count == 0`. Grund: `inventory.build`
   verwirft jeden Datensatz, den der Datenbestand nicht kennt - ein Spielstand
   eines neueren Spiels als der Datenabzug kaeme als Bestand an, der **null**
   zaehlt, und `You own 0 relics in total.` ist genau der Satz, den AK-252
   verbietet. Der `ui-ux-designer` argumentiert in §3.3, der Fall existiere
   nicht (`inventory.py:529`); das gilt fuer `scan`, nicht fuer `build`. Ein
   eigener Testfall haelt es fest, und eine Mutation, die die Pruefung
   zuruecknimmt, toetet ihn.
2. **Vier Nicht-Anzeigetexte in `firstrun.py` mit derselben widerlegten
   Zusage** habe ich mitgeaendert, weil sie in den Stellen stehen, die ich
   ohnehin bearbeite, und sonst als toter Widerspruch stehenblieben:
   Modul-Docstring (Zeile 5, vom Auftrag ausdruecklich uebergeben), Docstring
   von `w1` ("a minute spent on ELDEN RING"), Kommentar in `what_is_needed`
   ("a minute of rebuilding"), Klassendocstring `_Window` ("right for a minute
   nobody can shorten") und der Kommentar ueber dem Start-Menue-Angebot ("This
   minute of setup"). **Keiner davon erscheint auf dem Bildschirm**, AK-253
   fordert keinen von ihnen. Wenn der `director` das als Ausweitung des Diffs
   sieht, ist es in b19a2cd isoliert nachvollziehbar.
3. **`tests/test_first_run_panel.py`**: die W1-Transkription (Zeile 62) musste
   auf W-C nachgezogen werden, sonst ist die Suite rot. Nur diese drei Zeilen.

## Tests

**Neu: 19 Faelle in zwei Dateien.**

`tests/test_the_owned_total_has_its_own_line.py` (11 Faelle, AK-250 bis
AK-252). Der Bestand wird **hier gebaut** (`SaveScan` von Hand, ein bzw. drei
Relikte) und durch die echte Lese-Naht in das Fenster gegeben - so ist die
Zahl ein Literal des Falls, und kein Fall braucht eine Maschine mit
Spielstand. Die vier `load_equipped`-Enden werden nacheinander ausgeloest;
**die Positivkontrolle ist in jeder Runde die zweite Zusicherung**: die
Meldung muss wirklich in `owned_label` ankommen, sonst drueckt der Fall einen
Knopf, der nichts tut.

`tests/test_the_first_run_promises_no_duration.py` (8 Faelle, AK-253 bis
AK-255). Der Waechter sammelt die **Anzeigetexte** ein (alle sieben
Panel-Fabriken, beide Bau-Zustaende, die Bestaetigung) und sucht darin nach
`about a minute`, `takes a minute` und einer Ziffer vor einer Zeiteinheit.
Zwei Kontrollen, damit er nicht sein eigenes Pruefmittel misst:
(a) dieselbe Suche schlaegt auf den **beiden alten** Saetzen an (als Literale
im Test), (b) die Sammlung enthaelt nachweislich W-A, W-B und W-C. Dazu eine
Vollstaendigkeitspruefung: die Menge der von Hand aufgezaehlten Panel-Fabriken
muss der Menge der Modulfunktionen mit Rueckgabetyp `Panel` gleichen - ein
neues Panel faellt hier auf, statt an der Sammlung vorbeizulaufen.

### Mutationsbeweis - 12 Mutationen, 12 getoetet

Treiber: Tar-Kopie des Baums je Mutation, `PYTHONDONTWRITEBYTECODE=1`,
`-p no:cacheprovider`, Anker muss **genau einmal** passen, danach aus der
unberuehrten Kopie zurueckgesetzt
(`<scratchpad>/T-179/mutate_t179.py`, Ergebnisse in `mutations.txt`).

| Mutation | getoetet von |
|---|---|
| AK-250 die Zahl wieder in `owned_label` schreiben | 5 Faelle, u. a. `test_the_total_stands_through_every_message_that_takes_the_note` |
| AK-250 den Aufruf aus `_the_save_has_been_read` entfernen | 6 Faelle |
| AK-251 die Zahl aus `base_slots[0].available_items()` nehmen | 4 Faelle |
| AK-251 den Spielstandnamen unescaped in den Tooltip | `test_a_save_name_that_looks_like_markup_is_shown_as_the_name_it_is` |
| AK-252 die leere Zeile `setVisible(False)` | 4 Faelle (drei Zustaende + der Ein-Schreiber-Waechter) |
| AK-252 die `relic_count`-Pruefung zuruecknehmen ("0" erscheint) | `test_a_stock_that_names_nothing_is_no_stock_at_all` |
| AK-252 `setMinimumHeight(0)` | `test_the_arrival_moves_no_control_of_the_left_pane` |
| AK-253 "about a minute" in W-A zurueck | 3 Faelle |
| AK-253 "about a minute" in W-C zurueck | 2 Faelle, davon einer in `test_first_run_panel.py` |
| AK-254 dem Balken einen Bereich geben | `test_the_bar_promises_no_progress_it_cannot_compute` |
| AK-254 die Statuszeile abklemmen | `test_every_message_reaches_the_line_word_for_word_and_in_order` |
| AK-255 die festen Hoehen stehen lassen | beide Faelle von `test_the_build_state_is_as_tall_as_what_it_says` |

**Keine Mutation hat ueberlebt.** Eine Beobachtung dazu, die kein Mangel ist:
`setVisible(False)` toetet den Zustand *"ein Lesen, das nie antwortet"*
**nicht** - dort hat der Schreiber noch nie gelaufen. Das ist richtig so und
der Grund, warum vier Zustaende und nicht einer geprueft werden.

**Nicht registriert:** `scripts/differential/mutate.py` steht nicht auf der
Whitelist dieses Auftrags. Die zwoelf Anker liegen fertig im Treiber; das
Nachtragen ist ein eigener, kleiner Auftrag (siehe *An director*).

### Suitezahl

```
pytest -n auto  ->  1723 passed, 9 skipped, 0 failed in 168,70 s
```

**Datenbedingung** (ohne die die Zahl in diesem Repo nichts wert ist,
`docs/debug/D-001.md`): `LOCALAPPDATA` in den Scratchpad umgelenkt und dort
**eine Kopie des festen Testabzugs** (841 Dateien, 22 MB,
`meta.extract_version` = 11 = `extract.EXTRACT_VERSION`). `game_data` kommt
damit aus dem **zwischengespeicherten Datenabzug**, nicht aus einer frischen
Extraktion; die 9 Skips sind die Faelle, die eine Spielinstallation
verlangen, die dieser Rechner hat. 1704 (Vorgabe) + 19 neue Faelle = 1723.

**Ein Fehlschlag im ersten Vollauf, nicht meiner:**
`tests/test_advisor_worker.py::test_cancel_is_visible_at_once_however_long_the_worker_takes`
(`assert 2 > 2` - der Arbeiter war fertig, bevor das Fenster vom Abbruch
erfuhr). Einzeln gruen (18 passed in 11,10 s), im zweiten Vollauf gruen. Ich
habe keine Zeile des Advisors angefasst. Meldung an den `director`, kein Fix
von mir.

## Messungen (L-009) - Plattform, Stil, Skalierung, logisch/physisch

Alle Zahlen sind **logische** Pixel, Stil **Fusion**, Schrift die
Voreinstellung. Der Bildschirm des Rechners laeuft auf 150 %
Windows-Skalierung (`dpr` 1,5 bei `QT_SCALE_FACTOR=1`), physisch ist also
das 1,5-fache. Skript: `<scratchpad>/T-179/measure_t179.py`.

**AK-252 - die Zeile im `Build planner`,** linker Bereich auf seiner
Vorgabebreite von 430 px, Bestand von drei Relikten:

| Umgebung | leer | gefuellt | y |
|---|---|---|---|
| `offscreen`, Skalierung 1 / 1,25 / 1,5 | 430 x **14** | 430 x **14** | 642 |
| `windows`, `QT_SCALE_FACTOR` 1 / 1,25 / 1,5 | 430 x **16** | 430 x **16** | 614 / 591 / 452 |

Leer und gefuellt sind in **jeder** Umgebung gleich hoch und stehen an
derselben Stelle - das ist die Messung, die AK-252 verlangt. `QT_SCALE_FACTOR`
aendert offscreen **nichts** (bekannt, T-089); unter der Windows-Plattform
schrumpft der gemeldete Bildschirm (1707x1067 -> 1365x853 -> 1138x711), was
die y-Position des Fensters verschiebt, nicht die Zeile.

**AK-255 - die Hoehe der beiden Bau-Zustaende** bei `PANEL_WIDTH` = 460:

| Umgebung | Erststart | Neuaufbau | Erklaerzeile (Hoehe / benoetigt) |
|---|---|---|---|
| `offscreen` (alle drei Faktoren) | **196** (Boden 190) | **196** (Boden 150) | 404 x 68 / 68 |
| `windows`, alle drei Faktoren | **190** (Boden 190) | **188** (Boden 150) | 32 / 32 bzw. 48 / 48 |

Kein Zustand ist niedriger als vorher, und die Erklaerzeile bekommt an jeder
gemessenen Stelle genau die Hoehe, die sie braucht. **Der Fall, der die feste
Zahl toetet, ist der Neuaufbau unter der Windows-Plattform: 188 gebraucht
gegen 150 fest** - der laengere Satz waere unten abgeschnitten worden.
Offscreen faellt derselbe Fehler nicht auf, weil die Offscreen-Schrift den
Satz auf vier Zeilen umbricht und beide Zustaende ohnehin ueber 190 hebt.

## Umlenkungen - mit Positivkontrolle

Vor dem ersten Testlauf, `<scratchpad>/T-179/where.py`, zweimal gelaufen:

| | ohne Umlenkung (Positivkontrolle) | mit Umlenkung |
|---|---|---|
| `favourites.ORG` | `DankYeeter` | `DankYeeterT-179` |
| `paths.cache_dir()` | `…\AppData\Local\NightreignHelper` | `…\scratchpad\T-179\localappdata\NightreignHelper` |
| `shortcut_path()` | `…\Roaming\…\Start Menu\Programs\Nightreign Helper.lnk` | `…\scratchpad\T-179\appdata\…\Nightreign Helper.lnk` |

Nachher geprueft: das echte Start-Menue hat unveraendert **24** Eintraege, im
umgelenkten Start-Menue liegt **keine** Datei, der Spielstand ist unveraendert
(19 531 312 Bytes, Zeitstempel wie zuvor; nur gelesen). Unter `pytest`
ueberschreibt `conftest` die Org ohnehin auf `DankYeeterTests` - das steht so
im Repo und ist ebenfalls neben dem Speicher des Spielers.
**Aufgeraeumt:** der Messlauf hat `HKCU\Software\DankYeeterT-179` angelegt
(genau das, wofuer die Umlenkung da ist); ich habe den Schluessel danach
entfernt und beides geprueft - er ist weg, `HKCU\Software\DankYeeter` steht
unveraendert. Nebenbefund fuers naechste Mal: `reg.exe delete … /f` **und**
`-f` scheitern aus der Git-Bash an "Invalid syntax"; `powershell -Command
Remove-Item -Path 'HKCU:\…' -Recurse -Force` tut es.

## DoD

- [x] Anforderung verstanden, Annahmen dokumentiert
- [x] Build & Tests gruen in der benannten Umgebung (Windows 10 x64), mit
      Datenbedingung
- [x] Neue Tests fuer neue Logik; jede neue Zusicherung mit toetender Mutation
      belegt. **Kein Linter im Projekt konfiguriert** - Punkt entfaellt.
- [x] Keine Secrets, keine TODOs, kein toter Code
- [x] Messauflagen aus AK-252 und AK-255 gefuehrt
- [x] Doku: dieser Bericht. `UI_SPEC.md`, `docs/state.md`, `qa/findings.md`
      nicht angefasst (fremde Dateien).
- **Ungeprueft:** Linux, macOS (kein Ziel). **Nicht am gebauten Artefakt
      geprueft** - kein PyInstaller-Lauf, kein echter Erststart auf einer
      Maschine ohne Datenabzug. Der Erststart-Dialog ist offscreen und unter
      der Windows-Plattform gemessen, aber nie in einem echten Erstlauf
      gesehen. Das ist eine Luecke, kein Beleg.

## An qa-engineer

- **Der Kern von Teil 1:** Fenster oeffnen, warten bis der Bestand da ist -
  `You own 309 relics in total.` steht ueber `Rescan save`. Dann
  `Load equipped` druecken, mehrfach, mit verschiedenen Nightfarern: **die
  Zeile darf sich nie aendern**, waehrend die 10-px-Notiz darunter durch alle
  Meldungen laeuft. Genau das war der Fehler.
- **Tooltip der Zeile:** nennt den Spielstand (`USER_DATA000`) und loest die
  Verwechslung mit `Slot 1 — Red (51 available)` auf.
- **Randfaelle:** `Rescan save` waehrend eines Lesens (Zahl muss **stehen
  bleiben**, nicht leer werden); `Find my save...` auf eine Datei ohne
  Relikte (Zeile leer, nicht `0`); ein zweites Steam-Konto - der Nutzer hat
  zwei mit 234 und 309 Relikten, und laut Nutzerentscheid vom 09.09. gilt die
  Zahl des **bestbestueckten** Charakterslots.
- **Beim ersten Anstrich** darf sich beim Ankommen des Spielstands **nichts**
  verschieben (Knopfzeile, Notiz, Level-Regler, Gefaessliste).
- **Teil 2 braucht einen echten Erststart**, den ich nicht herstellen kann:
  Datenabzug wegnehmen, Programm starten, Satz lesen, Fenster auf
  Abschneiden pruefen - bei 100 %, 125 % und 150 % Skalierung. Der
  Neuaufbau-Zustand (`Refreshing your game data`) ist der knappere von beiden.
- **Nicht in diesem Auftrag:** QA-222 (der erste Klick), `README.md`, die
  slotbezogenen Zahlen.

## An ui-ux-designer

- Beide Wortlaute sind woertlich umgesetzt, ohne Kuerzung.
- **Eine Verschaerfung** gegenueber §3.3: die Zeile bleibt auch dann leer,
  wenn ein Bestand ankommt, der **null** zaehlt (Begruendung oben unter
  *Abweichungen*, Punkt 1). Wenn das gegen die Absicht laeuft, ist es eine
  Zeile Code.
- **Zur Kenntnis:** `UI_SPEC.md:2949` (Abschnitt T-074/T-145, die dortige
  W1-Transkription) traegt weiterhin *"Reading it takes about a minute"*.
  Der Text der Anwendung ist auf W-C gezogen, die aeltere Stelle in deiner
  Datei nicht - ich darf sie nicht anfassen.

## An director

1. **`README.md:80`** - *"First launch takes about a minute."* Nicht
   angefasst, gehoert dem `technical-writer`. Das ist die Stelle, die ein
   neuer Nutzer **zuerst** liest, und sie ist jetzt die einzige verbliebene
   im Auslieferungsumfang.
2. **`DESIGN_REVIEW.md:892`** - dort steht die Zeitangabe noch als
   *"ehrlich"* gelobt. Der `ui-ux-designer` hat es in T-178 §11.4 selbst
   gemeldet; gehoert in den naechsten Review-Durchlauf.
3. **`UI_SPEC.md:2949`** - alte W1-Fassung, siehe oben.
4. **Die zwoelf Mutationen sind nicht in `scripts/differential/mutate.py`
   registriert** (Datei ausserhalb der Whitelist). Anker und Ersetzungen
   liegen fertig in `<scratchpad>/T-179/mutate_t179.py`; ein Nachtrags-Auftrag
   kann sie uebernehmen. **Achtung:** der Scratchpad ist sitzungsgebunden -
   wenn das nicht bald geschieht, muessen die Anker neu erzeugt werden.
5. **Flackernder Test, nicht von mir:**
   `test_advisor_worker.py::test_cancel_is_visible_at_once_however_long_the_worker_takes`
   faellt unter Last (`assert 2 > 2`), ist einzeln und im zweiten Vollauf
   gruen. Der Fall misst, ob der Arbeiter nach dem Abbruchsignal **noch**
   gerechnet hat; auf einer belasteten Maschine ist er vorher fertig. Das ist
   eine Eigenschaft des Falls, nicht des Programms - Empfehlung: dem
   `qa-engineer` oder dem `fehlerdiagnostiker` als eigenen kleinen Auftrag.
6. **Zwei ungepruefte Zeitangaben in Docstrings** (Volltextsuche, zweite
   Maske): `nrplanner/datasource.py:75` *"Extracting takes ~16 seconds"* und
   `nrdata/iconbuild.py:3` *"Decoding … takes ~25 seconds"*. Beide betreffen
   **einzelne Schritte**, nicht das Erststart-Versprechen, und keiner kommt
   auf den Bildschirm - deshalb nicht angefasst. Sie tragen aber kein Rezept
   und stehen im Widerspruch zu einem Erststart von bis zu fuenf Minuten.
7. **Sicherheitsfunde:** keine. Der Spielstandname geht durch `html.escape()`
   in den neuen Tooltip (SEC-013-Muster), das Widget ist `Qt.PlainText`
   (SEC-004-Muster), und eine Mutation, die das Escaping entfernt, wird
   getoetet.
8. **Performance:** nichts aufgefallen. Die neue Zeile wird einmal je Ende
   eines Lesens geschrieben.

### Volltextsuche zum Schliessen der Eigenschaft (L-006)

Zwei unabhaengig formulierte Masken ueber den ganzen Baum:

- `about a minute|takes a minute` -> **6 Treffer**: `README.md:80` (Punkt 1),
  `DESIGN_REVIEW.md:892` (Punkt 2) und **vier in meiner eigenen neuen
  Testdatei** - die Positivkontrolle und die Suchmaske selbst. Keine Stelle
  im Anwendungscode.
- `[0-9]+ ?(second|minute|hour)s?` ueber `nrplanner/`, `nrdata/`, `scripts/`
  -> **2 Treffer**, beide Punkt 6, beide Docstrings.
