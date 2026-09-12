# T-190 — QA-211: die Ausnahmetexte holt kein Sprachwaechter ein (developer)

```
STATUS: teilweise
AUFTRAG: T-190 — QA-211: die Ausnahmetexte holt kein Sprachwaechter ein
GELESEN: docs/tasks/T-190.md; ~/.claude/agents/_rahmen.md; CLAUDE.md;
  qa/findings.md (QA-204, QA-207, QA-211, QA-217, QA-224);
  docs/archiv/berichte/T-126-qa-engineer.md (Herkunft von QA-211, die fuenf
  Fundstellen mit ihren damaligen Zeilennummern);
  nrplanner/app.py, inventory.py, shortcut.py, firstrun.py, datasource.py,
  relicpicker.py; nrdata/savefile.py, icons.py, extract.py;
  scripts/differential/mutate.py;
  tests/test_save_read_in_the_background.py (AK-229-Sammelfunktion),
  tests/test_interface_language.py, tests/test_save_path_memory.py,
  tests/test_hostile_savefile.py, tests/test_first_run_panel.py,
  tests/test_the_owned_total_has_its_own_line.py, tests/conftest.py
GEAENDERT: nrplanner/errortext.py (neu); nrplanner/app.py;
  nrplanner/inventory.py; nrplanner/shortcut.py; nrplanner/firstrun.py;
  tests/test_exception_text_is_english.py (neu);
  tests/test_save_read_in_the_background.py; tests/test_save_path_memory.py;
  scripts/differential/mutate.py; docs/berichte/T-190-developer.md.
  Commits 555d520, 2b47e91, e23f51f, 0204a25, 6ad6332, d3b3ca9 — alle mit
  Pfadangabe hinter `--`, keiner mit `-a` oder `add .`.
  Ausserdem angelegt und wieder entfernt: ein versehentlich im
  Repo-Wurzelverzeichnis gelandetes `klon/` (untracked, `rm -rf`, siehe D-4).
ANNAHMEN: (1) Der Auftrag nennt "fuenf Fundstellen"; die Bauform hat
  13 Stellen (gezaehlt, s. u.), die fuenf aus QA-211 sind eine Teilmenge.
  Gearbeitet wurde an der Bauform, berichtet gegen beide Zahlen.
  (2) Die Grenze "hoechstens fuenf Quelldateien" wurde fuer Anwendungscode
  eingehalten (genau fuenf); zwei Stellen bleiben deshalb offen, beide mit
  gemessener Begruendung. `scripts/differential/mutate.py` ist als sechste
  Datei dazugekommen — kein Anwendungscode, sondern ein Mutationskatalog,
  dessen Anker meine Aenderung zwingend tot gemacht hat (D-7).
  (3) `A_SAVE_PATH` und `GERMAN_FROM_WINDOWS` in den Tests sind Literale,
  kein Abgriff der laufenden Maschine — der Fall muss auf jedem Rechner
  gleich ausfallen (QA-224 ist die Gegenlehre).
NAECHSTER: director
BLOCKIERT DURCH: nichts. Zwei Reststellen brauchen je eine weitere
  Quelldatei und damit eine Scope-Entscheidung (D-1).
```

---

## Urteil in einem Absatz

Die Senke ist gebunden, aber nicht ueberall. Von **13** Stellen der Bauform
(ein gefangener Ausnahmewert wird zu Text und kann gezeigt werden) sind
**7 geschlossen** und **6 offen**; von den **fuenf Fundstellen aus QA-211**
sind **drei geschlossen** — darunter **beide alltaeglichen**,
Start-Menue-Knopf und fehlgeschlagener Spielstand-Reread —, eine ist **tabu**
(`advisor/worker.py`, dort laeuft A17) und eine braucht eine weitere
Quelldatei. Der Waechter steht, faellt fuer jede geschlossene Stelle
einzeln, und traegt die uebrigen als OFFEN-Liste mit Vorkommenszahl, die nur
schrumpfen darf. **QA-211 ist damit nicht geschlossen, sondern deutlich
verkleinert und ab jetzt bewacht.**

## Widerspruch zum Auftrag — die Bauform ist groesser als fuenf

Der Auftrag (und QA-211) sprechen von fuenf Fundstellen. Gezaehlt **vor**
der ersten Reparatur, per AST ueber `nrplanner/**` und `nrdata/**`, auf dem
im Auftrag genannten Stand `b8f71a8` in einem frischen Klon
(`git clone` in den Scratchpad, `scan.py` dort ausgefuehrt):

```
$ python scan.py            # Klon auf b8f71a8
('nrplanner/advisor/worker.py', 'work', 190, 'str(exc)')
('nrplanner/app.py', 'read_the_save', 1638, 'exc.strerror')
('nrplanner/app.py', 'main', 5192, 'str(exc)')
('nrplanner/app.py', 'work', 1682, 'str(exc)')
('nrplanner/firstrun.py', 'run', 618, 'str(exc)')
('nrplanner/inventory.py', '_scan_save', 521, 'exc.strerror')
('nrplanner/inventory.py', '_scan_save', 524, 'str(exc)')
('nrplanner/inventory.py', 'scan', 429, 'str(exc)')
('nrplanner/inventory.py', '_scan_save', 542, 'str(exc)')
('nrplanner/shortcut.py', 'create', 131, 'str(exc)')
('nrplanner/shortcut.py', 'remove', 147, 'str(exc)')
('nrdata/extract.py', '_bosses', 324, '{exc}')
('nrdata/icons.py', 'read_subtextures', 74, '{exc}')
count: 13
```

**Lesart der Zahl:** gezaehlt sind *Vorkommen* (einzelne Zeilen), nicht
Anzeigewege. QA-211 hat die fuenf **Anzeigewege** gezaehlt: `shortcut` steht
dort als eine Fundstelle mit zwei Zeilen, und die **Quellen** unter dem
Anzeigeweg — `exc.strerror` in `read_the_save` und in `_scan_save` — fehlen
ganz, obwohl genau sie auf deutschem Windows den deutschen Text erzeugen.
Der Befundtext ist nicht falsch, aber er zaehlt eine andere Groesse; wer nur
seine fuenf repariert, laesst die beiden `strerror`-Zeilen stehen und hat A8
nicht geschlossen. Dieselbe Messung nach der Aenderung (Arbeitsbaum,
`d3b3ca9`): **count: 6**.

## Beurteilung des security-reviewer-Vorschlags — zur Haelfte Widerspruch

Der Vorschlag aus T-185 war, `texts_that_can_land_behind_the_prefix()`
(`tests/test_save_read_in_the_background.py`) um eine **zweite Maske** zu
erweitern und damit die Senke zu binden.

**Fuer die Sprachseite traegt das nicht, und zwar prinzipiell.** Die
Sammelfunktion sammelt `ast.Constant`-Knoten aus `raise`-Ausdruecken — also
**Quelltextliterale**. `str(exc)` ist kein Literal; es steht als
`ast.Call`/`ast.Name` da und hat zur Uebersetzungszeit keinen Text. Eine
zweite Maske auf dieser Sammlung zoege ueber die betroffene Textklasse
**null Stichproben** und waere genau der Fall, vor dem der Rahmen warnt: ein
Waechter, der sein Pruefmittel misst statt der Sache. Dass die beiden
bestehenden A8-Waechter dieselbe Blindstelle haben, ist der Inhalt von
QA-211.

**Fuer die Pfadseite traegt es, und ich habe es mitgenommen.** Ob ein
*geschriebener* Satz der Lesekette einen Ort nennt, ist an Literalen
entscheidbar. Die Maske ist dazugekommen
(`test_no_text_behind_the_prefix_names_a_path`, mit eigener
Positivkontrolle `test_the_mask_for_a_path_really_fires`) und deckt die
**Literalhaelfte** von SEC-023s offener Randbedingung. Die
**Laufzeithaelfte** — `_on_save_failed` bekommt `str(exc)`, und
`str(OSError)` traegt den ganzen Pfad — ist **nicht** ueber eine Maske
geschlossen, sondern dadurch, dass die Senke gar keinen Ausnahmetext mehr
bekommt; bewacht wird sie im neuen Waechter, dessen Verhaltensfaelle jede
geschlossene Senke mit einem `OSError` treiben, der Pfad *und* deutsches
Wort traegt, und beides im Ergebnis verbieten.

## Umgesetzt

**`nrplanner/errortext.py` (neu, 139 Zeilen).** `in_english(exc)` gibt genau
einen englischen Satz je Fehlerart zurueck:

1. Ist die **Klasse** in `nrplanner`/`nrdata` definiert, wird ihr Text
   gezeigt — er ist ein Literal dieses Repositories und faellt damit unter
   den bestehenden Quelltext-Waechter von A8 (nachgewiesen, M7).
2. `OSError` wird ueber `errno` abgebildet — 23 Eintraege, 22 verschiedene
   Saetze (`EMFILE`/`ENFILE` teilen sich einen absichtlich). Das ist der
   Ersatz fuer `strerror`: es sagt weiter, *was* schiefging, nur in einer
   Sprache, die nicht von der Windows-Installation abhaengt. Ein Code ohne
   Tabellenzeile bekommt Pythons eigenen ASCII-Namen (`EDEADLOCK`), keine
   Windows-Meldung.
3. Sonst eine Klassentabelle (`struct.error`, `subprocess.TimeoutExpired`,
   `MemoryError`, `RecursionError`, `UnicodeError`).
4. Rueckfall nennt den Klassennamen, wenn der ein ASCII-Bezeichner ist.

**Geschlossene Stellen (7).** `shortcut.create` und `shortcut.remove` (der
Start-Menue-Knopf), `app._SaveReadWorker.work` (die Zeile unter dem
Spielstand), `app.read_the_save` (`exc.strerror`), `inventory._scan_save`
OSError-Zweig (`exc.strerror`), `inventory.scan`, `firstrun._Builder.run`.

**Zwei Klassen, damit A8 nicht gegen A7 getauscht wird.** `read_the_save`
wirft jetzt `inventory.SaveNotReadable` statt eines nackten `ValueError`,
`firstrun` eine eigene `CannotBuild` statt eines `FileNotFoundError`. Beide
Saetze sind geschrieben und sollen gezeigt werden; als Fremdklasse waeren
sie von der Abbildung verschluckt worden.

**Der Waechter, `tests/test_exception_text_is_english.py` (13 Faelle).**
Eine AST-Suche ueber `nrplanner` und `nrdata` findet jede Stelle, die einen
per `except ... as` gebundenen Wert in Text verwandelt (`str(x)`, f-String,
`x.strerror`/`.args`/`.winerror`/`.message`/`.reason`), **mit
Vorkommenszahl**, und prueft sie gegen `STILL_QUOTING` — eine Literalliste,
die nur schrumpfen darf, in beide Richtungen gebunden. Dazu:
Positivkontrolle auf hier hinterlegtem Quelltext (alle drei Formen treffen;
`errortext.in_english(exc)` und `exc.__class__.__name__` treffen nicht),
eine Selbstpruefung, dass jede Zeile der OFFEN-Liste eine Stelle ist, die es
noch in der genannten Zahl gibt, und vier Verhaltensfaelle, die je eine
geschlossene Senke mit
`OSError(EACCES, "Zugriff verweigert", <Pfad mit Steam-Konto-Id>)` treiben
und im Ergebnis deutsches Wort, Pfad, Trennzeichen und Nicht-ASCII
verbieten. Die Suche laeuft von den zwei Paketordnern, **nicht** von der
Repo-Wurzel — Worktrees unter `.claude/` werden so nicht als zweite
Fundstelle gelesen.

**Drei Vorrichtungen angepasst, keine abgeschaltet.** In
`test_save_read_in_the_background.py` (zwei) und `test_save_path_memory.py`
(eine) warfen Vorrichtungen einen nackten `ValueError` als Ersatz fuer
`read_the_save`. Das ist seit dieser Aenderung nicht mehr, was
`read_the_save` wirft, und die Unterscheidung ist gerade der Fix. Sie werfen
jetzt `inventory.SaveNotReadable` mit demselben Text; dass die Zeile fuer
eine **fremde** Ausnahme etwas anderes sagt, ist im neuen Waechter belegt.

## Rote Phase — jede Schutzmassnahme einzeln abgeschaltet

Skript `…/scratchpad/T-190/mutate.py`, Sicherung per `cp datei datei.orig`
und Rueckkopieren (nie `git checkout`), Arbeitsbaum nach jedem Lauf sauber
(`git status --short` leer). **Elf Mutationen, elf tot:**

| # | abgeschaltete Massnahme | Ergebnis |
|---|---|---|
| M1 | `shortcut.create` zurueck auf `str(exc)` | RED — 2 failed, 11 passed |
| M2 | `shortcut.remove` zurueck auf `str(exc)` | RED — 2 failed, 11 passed |
| M3 | `_SaveReadWorker.work` zurueck auf `str(exc)` | RED — 2 failed, 11 passed |
| M4 | `read_the_save` zurueck auf `exc.strerror` | RED — 2 failed, 11 passed |
| M5 | `firstrun._Builder.run` zurueck auf `str(exc)` | RED — 2 failed, 11 passed |
| M6 | `inventory._scan_save` zurueck auf `exc.strerror` | RED — 1 failed, 12 passed |
| M7 | ein `errortext`-Satz auf Deutsch | RED — `test_interface_language.py::test_no_sentence_this_program_can_author_is_german`, woertlich: `1 of 5433 strings in 65 shipped files read as German: nrplanner/errortext.py:47: ['den'] in 'Windows hat den Zugriff darauf verweigert.'` |
| M8 | ein `raise` der Lesekette nennt `%APPDATA%/userdata` | RED — 1 failed, 25 passed (die neue Pfadmaske) |
| M9 | eine noch gueltige Zeile aus `STILL_QUOTING` entfernt | RED — 1 failed, 12 passed |
| M10 | eine erledigte Zeile in `STILL_QUOTING` stehen gelassen | RED — 1 failed, 12 passed |
| M11 | **eine von zwei** Stellen derselben Funktion repariert, Liste unveraendert | RED — `test_the_list_of_the_ones_left_is_still_true`, 1 failed, 12 passed |

M1–M6 sind die "brechende Aenderung" im Sinne von L-007: jede ist die
woertliche Rueckschaltung genau **einer** Zeile auf den Stand von `b8f71a8`,
keine Schnittstellenverschiebung. M9/M10 zeigen, dass die OFFEN-Liste in
beide Richtungen gebunden ist — sie kann weder heimlich wachsen noch
veralten.

**M11 ist ein Fehler, den ich an mir selbst gefunden habe, und er stand
vorher gruen.** Die erste Fassung der OFFEN-Liste war eine Menge von
`(Modul, Funktion, Form)`. `_scan_save` schreibt `str(exc)` an **zwei**
Stellen aus zwei Gruenden; beide fielen zu einem Eintrag zusammen, und wer
eine von ihnen repariert haette, haette den Waechter unveraendert gruen
gesehen. Gefunden hat es nicht die gruene Suite, sondern die Gegenprobe mit
einer zweiten Suchmaske (`grep` fand 12 Zeilen, der AST-Waechter meldete 5
Eintraege — die Differenz war der Fehler). Seit `6ad6332` haelt die Liste je
Eintrag die Anzahl; M11 ist der Beleg.

**M7 ist der Nachweis, dass die neuen Saetze unter dem bestehenden
A8-Waechter stehen.** Mein eigener Satzfall
(`test_every_sentence_is_a_plain_english_sentence`) haette ihn **nicht**
gefangen: "Windows hat den Zugriff darauf verweigert." ist ASCII, beginnt
mit einem Grossbuchstaben und endet auf einen Punkt. Das ist eine Luecke
meines Falls und eine Staerke des vorhandenen Waechters; es steht hier, weil
ich es sonst nicht gesehen haette.

## Gemessen statt vermutet: wo A8 A7 gekostet haette

Der erste Bau hatte in `inventory._scan_save` **einen** Handler fuer alles.
Drei bestehende Faelle wurden rot:

```
E  AssertionError: assert 'BND4' in 'Something went wrong that this program
   has no sentence for (ValueError).'
   tests/test_save_path_memory.py:671
```

`nrdata/savefile.py` verweigert in eigenen englischen Saetzen ("not a BND4
save container", die zwei Dichte-Verweigerungen), aber als nackter
`ValueError` — nicht unterscheidbar von dem, den pycryptodome wirft (QA-217).
Die Klassenabbildung haette die Saetze weggeworfen. Der OSError-Zweig (die
deutsche Haelfte) ist geschlossen, der andere Zweig steht unveraendert und
mit Begruendung in der OFFEN-Liste. **Das ist der Beleg dafuer, dass die
Fuenf-Dateien-Grenze hier wirklich bindet und nicht bloss behauptet wird.**

## Zahlen

**Volllauf (Regressionsmessung, einmal am Ende).**

```
$ python -m pytest -q --no-header \
      --ignore=tests/test_extraction.py --ignore=tests/test_hostile_gamedata.py
1 failed, 1712 passed, 9 skipped in 443.00s (0:07:22)
FAILED tests/test_first_run_panel.py::
       test_the_first_dialog_opens_at_the_folder_that_was_remembered
```

**Gegen T-188** (12.09.2026, derselbe Rechner, dieselbe Datenbedingung):
1697 passed, 1 failed, 9 skipped in 451 s. Differenz **+15 passed**, und die
ist vollstaendig erklaert: 13 neue Faelle in
`test_exception_text_is_english.py`, 2 neue in
`test_save_read_in_the_background.py`. Der eine Fehlschlag ist unveraendert
**QA-224** (liest die echte Steam-Installation: erwartet `None` oder
`C:/Program Files (x86)/Steam/steamapps/common`, bekommt
`d:/steam/steamapps/common`), kein Regress meiner Aenderung.

**Datenbedingung.** Windows 11, Quellstand, Branch
`docs/audit-and-advisor-design`, Arbeitsbaum auf `d3b3ca9`. `pytest-xdist`
und `texture2ddecoder` sind **nicht** installiert; `-n auto` ist nicht
lauffaehig und wurde nicht benutzt, nichts nachinstalliert. **Neu gegenueber
T-188:** ohne `--ignore` bricht der Lauf schon beim Einsammeln ab
(`2 errors in 0.94s`, `ModuleNotFoundError: No module named
'texture2ddecoder'` in `tests/test_extraction.py` und
`tests/test_hostile_gamedata.py`) — die beiden Module muessen ausdruecklich
uebersprungen werden, sonst gibt es gar keine Zahl. Das Programm wurde
**nicht gestartet**; es gab nichts umzulenken und keinen Testabzug zu
kopieren, alle Faelle sind Testfaelle. Echter Spielstand und echte
Spielinstallation liegen auf der Maschine (nur gelesen), `game_data` kommt
aus dem Cache-Snapshot.

**Vorher/Nachher der Bauform:** 13 → 6 Vorkommen (Skript
`…/scratchpad/T-190/scan.py`; vorher gegen einen frischen Klon auf
`b8f71a8`, nachher gegen den Arbeitsbaum auf `d3b3ca9`).

## Suche ueber den ganzen Baum (L-006)

Zwei unabhaengig formulierte Masken, beide nach der Aenderung:

```
$ grep -rn "str(exc)\|str(e)\b\|{exc}\|{error}\|{err}\|{reason}\|\.strerror\|exc\.args" \
      --include=*.py nrplanner/ nrdata/          ->  12 Treffer
$ python scan.py       # AST, bindet an den von except gebundenen Namen
                                                 ->  count: 6
```

Die 12 Textreffer zerfallen in: **6** echte Stellen der Bauform (die
OFFEN-Liste), **2** Prosa in `errortext.py` (Zeile 94 ist die eine erlaubte
Stelle, Zeile 118 ein Docstring), **2** lokale Zeichenketten, die bereits
gefilterten Text hereinbekommen (`app.py:2722 {error}` aus `shortcut`,
`relicpicker.py:137 {reason}` aus dem Berater), **2** Anzeigezeilen mit
`{reason}` in `app.py:4224/4225`, die den schon gefilterten Text der Senke
setzen. Die AST-Suche ist die zweite, unabhaengig formulierte Maske: sie
bindet an den Namen, den die `except`-Klausel gebunden hat, findet daher
auch Schreibweisen, die die Textsuche nicht kennt, und **sie** ist es, die
als Waechter im Repository steht.

## OFFEN — die sechs Vorkommen, die der Waechter noch meldet

| Stelle | A8-Risiko heute | was zum Schliessen fehlt |
|---|---|---|
| `nrplanner/advisor/worker.py::work` | **ja**, jeder `OSError` in einem Beraterlauf | nichts Technisches — **tabu in T-190** (A17/T-189). Eine Zeile, derselbe Fix |
| `nrplanner/app.py::main` | **ja**, `load_data` kann mit `OSError` scheitern | eine Ausnahmeklasse in `nrplanner/datasource.py`. Ohne sie wuerde die Abbildung `_no_data_message()` verschlucken |
| `nrplanner/inventory.py::_scan_save` (**2×**: Slot-Lesen und gespeicherte Builds) | **nein** — der OSError-Zweig faengt die deutsche Haelfte ab | eine Ausnahmeklasse in `nrdata/savefile.py`; gemessen, s. o. |
| `nrdata/extract.py::_bosses` | nein — `print` auf die Konsole, kein Fenster | Entscheidung, ob die Konsole ueberhaupt unter A8 faellt (D-6) |
| `nrdata/icons.py::read_subtextures` | nein — `LayoutError` interpoliert ElementTree, das ist Englisch | Satz je Fall statt Interpolation |

## DoD

- [x] Anforderung verstanden, Annahmen dokumentiert
- [x] Build & Tests in der benannten Testumgebung (Windows, Quellstand):
      1712 passed, 1 failed (QA-224, Bestand), 9 skipped in 443 s
- [x] Neue Tests fuer neue Logik: 13 Faelle im neuen Waechter, 2 in der
      AK-229-Sammlung; rote Phase fuer jede Massnahme einzeln nachgewiesen
      (11 Mutationen, 11 tot)
- [x] Linter: **entfaellt** — das Projekt hat keinen konfiguriert. Geprueft
      im Wurzelverzeichnis: kein `ruff.toml`, `.ruff.toml`, `.flake8`,
      `setup.cfg`, `pyproject.toml`, `.pylintrc`; `pytest.ini` enthaelt
      keinen Lint-Hook
- [x] Keine Secrets, keine TODOs, kein toter Code
- [x] UI-Vorgaben: die Satztabelle folgt DR-006 (was passiert ist zuerst,
      warum danach) und AK-126 (kein Ort im Satz)
- [x] Bericht geschrieben
- [ ] **QA-211 nicht geschlossen** — 3 von 5 Fundstellen, 7 von 13 Vorkommen
      der Bauform

## An qa-engineer

- **Zu pruefen am laufenden Programm, mit umgelenkten Datenverzeichnissen:**
  (1) Klick auf den Start-Menue-Knopf, wenn das Ziel nicht schreibbar ist —
  der Warnkasten muss `Windows would not allow access to it.` zeigen, nicht
  eine PowerShell- oder Windows-Meldung. (2) `Rescan save` auf einen
  Spielstand, den das Spiel gerade haelt — die Zeile unter dem Save muss
  `Save could not be read: Another program has it open.` lauten.
- **Randfaelle mit eigenem Satz:** getrenntes Netzlaufwerk
  (`ETIMEDOUT`/`ECONNRESET`), Datei verschwindet zwischen `exists()` und
  `stat()` (`ENOENT`), voller Datentraeger beim Erstaufbau (`ENOSPC`),
  Erstaufbau ohne Param-Definitionen (muss weiterhin den geschriebenen Satz
  zeigen, nicht die errno-Zeile).
- **Was ich nicht pruefen konnte, und das ist eine Luecke, kein Beleg:** ob
  auf einem **deutschen** Windows wirklich kein deutscher Satz mehr
  erscheint. Die Systemsprache zu wechseln liegt ausserhalb der erlaubten
  Testumgebung; die Faelle stellen den deutschen Text als Literal her.
- Die Stellen in der OFFEN-Tabelle sind weiterhin scharf, zwei davon fuer A8.

## An ui-ux-designer

Keine Abweichung von einer Vorgabe. Neu sind 23 + 5 + 2 Saetze in
`nrplanner/errortext.py`, die im Fehlerfall in der Statuszeile, im
Warnkasten des Start-Menue-Knopfs und im Erstaufbau-Dialog erscheinen. Sie
stehen bisher in keinem `UI_SPEC`-Abschnitt; sie sind bewusst kurz gehalten
und nennen keinen Ort (AK-126). **Wenn der Wortlaut abgenommen werden soll,
ist das ein eigener Auftrag** — ich habe ihn nicht angemeldet, weil das
Scope-Sache des Director ist.

## An den director

- **D-1 (Scope-Entscheidung, klein):** zwei Reststellen brauchen je **eine**
  weitere Quelldatei — `nrplanner/datasource.py` (eine Ausnahmeklasse, damit
  `app.py::main` abgebildet werden kann, ohne `_no_data_message()` zu
  verlieren) und `nrdata/savefile.py` (dito fuer die BND4-Saetze). Beide
  sind "eine Klasse, ein paar `raise` umgehaengt". Die erste schliesst ein
  echtes A8-Loch; die zweite schliesst nur die Eigenschaft, kein akutes
  Sprachrisiko.
- **D-2 (tabu, gehoert in den naechsten A17-Auftrag):**
  `nrplanner/advisor/worker.py:190` ist die letzte **alltaegliche**
  A8-Luecke und eine Zeile:
  `str(exc) or exc.__class__.__name__` → `errortext.in_english(exc)`.
  Wer dort als Naechstes arbeitet, kann sie mitnehmen; danach wird die Zeile
  aus `STILL_QUOTING` gestrichen, sonst faellt
  `test_the_list_of_the_ones_left_is_still_true`.
- **D-3 (Befund ohne Nummer, Doku):** der Befundtext von QA-211 zaehlt
  **Anzeigewege**, nicht **Vorkommen**, und laesst die beiden
  `exc.strerror`-Quellen aus, die auf deutschem Windows den deutschen Text
  erst erzeugen. Wer nur die fuenf genannten Stellen repariert haette, haette
  A8 nicht geschlossen. Vorschlag fuer den Statuseintrag: *"teilweise — 7
  von 13 Vorkommen der Bauform, Waechter steht, 6 in `STILL_QUOTING`,
  Fortschritt zaehlbar"*.
- **D-4 (mein Fehler, behoben, gemeldet weil folgenreich):** ein erster
  `git clone` hat wegen `-C` ins **Repo-Wurzelverzeichnis** geklont statt in
  den Scratchpad. `klon/` lag untracked im Arbeitsbaum und ist mit
  `rm -rf klon` entfernt; es war nie gestaged und nie committet
  (`git status --short` danach leer). Gemeldet, weil ein untracked
  Verzeichnis im Wurzelverzeichnis genau das ist, was ein `git add -A` einer
  parallel arbeitenden Rolle mitgenommen haette — und T-189 lief parallel.
- **D-5 (Waechter-Befund an mir selbst, behoben):** die erste Fassung meiner
  OFFEN-Liste liess eine halbe Reparatur unsichtbar (s. M11). Sie stand rund
  eine Stunde gruen im Repository. Der Grund ist allgemein und nicht auf
  diesen Waechter beschraenkt: **eine Menge aus (Ort, Form) verliert die
  Vielfachheit.** Wer im Team eine OFFEN-Liste baut, sollte Vorkommen
  zaehlen.
- **D-6 (bestehende Debt, nicht angefasst):** `nrdata/extract.py:324`
  schreibt einen Ausnahmetext mit `print` auf die Konsole. Ob die
  Konsolenausgabe unter A8 faellt, ist nirgends entschieden — das ist eine
  Frage an `GOAL.md`, nicht an den Code.
- **D-7 (sechste Datei, unvermeidbar):**
  `scripts/differential/mutate.py` haelt den Mutationskatalog am Wortlaut der
  Quelle fest. Meine Aenderung an `read_the_save` hat den Anker von
  `the-reason-carries-the-path` tot gemacht, und
  `test_differential_track.py::test_every_mutation_still_finds_its_anchor_in_the_real_source`
  ist deshalb rot geworden. Der Anker ist nachgezogen, die Mutation sagt
  dasselbe wie vorher und toetet jetzt **drei** Faelle statt einem
  (gemessen: 3 failed, 46 passed in 42,53 s). Ich melde es, weil die
  Dateiliste des Auftrags diese Datei nicht nannte und ein Auftrag ohne sie
  nicht gruen zu bekommen war.
- **Sicherheitsfunde:** keiner neu. SEC-023s offene Randbedingung ist
  geschlossen, aber **anders als vorgeschlagen** — die Literalhaelfte ueber
  die zweite Maske auf der AK-229-Sammlung, die Laufzeithaelfte dadurch, dass
  `_on_save_failed` keinen Ausnahmetext mehr bekommt. Beide mit eigenem
  Waechter, beide rot nachgewiesen (M8 bzw. M3). Der `security-reviewer`
  sollte das gegenlesen; sein Vorschlag ist zur Haelfte begruendet
  zurueckgewiesen.
- **Performance:** nichts aufgefallen. Der Volllauf ist gegenueber T-188 um
  8 s **schneller** bei 15 Faellen mehr; das liegt im Rauschen und ist keine
  Aussage.

## Werkzeug im Scratchpad (fluechtig)

`…/scratchpad/T-190/scan.py` (Bauform-Zaehlung) und `mutate.py`
(Mutationslauf) liegen im Scratchpad und sind weg, sobald er geleert wird.
`scan.py` ist als Waechter versioniert
(`tests/test_exception_text_is_english.py::everywhere_an_exception_is_quoted`);
`mutate.py` ist es **nicht**. Wenn das Team einen wiederverwendbaren
Mutationslauf will, gehoert er nach `scripts/differential/` — das ist eine
Entscheidung des `director`, nicht meine. Der Klon auf `b8f71a8` liegt
ebenfalls im Scratchpad und enthaelt keine Commits, die nicht im
Arbeitsbaum sind.
