STATUS: erledigt
AUFTRAG: T-164 - Der Laufwerks-Rueckfall faellt, C3 fragt ab zwei Ebenen (developer)
GELESEN: docs/tasks/T-164.md · UI_SPEC.md (Nachtrag „SEC-032 nachgezogen",
Zeile 8869-9049, mit AK-246 bis AK-249 und den Vermerken an AK-232, AK-237,
AK-240, AK-241; AK-131 Zeile 3219-3222) · docs/berichte/T-163-ui-ux-designer.md
· docs/berichte/T-162-developer.md · nrdata/gamefiles.py ·
nrplanner/firstrun.py · nrplanner/app.py (nur gelesen, `main()` um Zeile
5090-5104) · tests/test_first_run_panel.py, tests/test_game_dir_recognition.py,
tests/test_game_path_memory.py, tests/conftest.py ·
scripts/differential/mutate.py (nur gelesen, Anker-Bestand) ·
tests/test_differential_track.py (Ankertest)
GEÄNDERT: nrdata/gamefiles.py, nrplanner/firstrun.py,
tests/test_game_dir_recognition.py, tests/test_first_run_panel.py — drei
Commits: `bd6bd90` fix(gamefiles), `b0e7ee4` feat(firstrun), `dcc8a11`
test(firstrun). Ausserdem diese Berichtsdatei. `tests/test_game_path_memory.py`
stand auf der Liste, brauchte aber keine Aenderung.
ANNAHMEN: (1) „Abstand" ist die Zahl der Verzeichnisebenen zwischen gewaehltem
und gefundenem Ordner, wie vom `ui-ux-designer` als billigste Umsetzung
vorgeschlagen (`len(landed) - len(seen)`). (2) Bei AK-131, Fall 2, ist die
Fehlermeldung selbst die des Lesers und nicht dieses Ablaufs, der Fall prueft
deshalb nur, **dass** ein Fehler zurueckkommt, und nicht seinen Wortlaut.
NÄCHSTER: director
BLOCKIERT DURCH: nichts. Eine Entscheidung liegt beim director: die Form der
C3-Ausloeser in `settle_the_game_folder` (siehe „An den director", Punkt 1).

## Umgesetzt

### 1. Der Laufwerks-Rueckfall ist weg (`nrdata/gamefiles.py`)

`find_game_dir()` baut seine Kandidaten nur noch aus Steams eigener Liste
(Registry → `libraryfolders.vdf` → `common\<INSTALL_DIR>\Game` je Bibliothek).
Der Block „Bare-drive fallback" mit `C:/SteamLibrary/...` bis
`H:/SteamLibrary/...` ist ersatzlos entfallen; der Docstring haelt fest, was
dort stand, warum es faellt (SEC-031, Nutzerentscheid 09.09.2026) und dass der
seltene Rest jetzt ueber A15 laeuft.

**Deine Grenze, belegt.** Die echte Installation dieser Maschine wird
weiterhin gefunden, und zwar aus der `.vdf`, nicht aus dem Rueckfall — die
Bibliotheksliste nennt `D:\SteamLibrary\steamapps`, bevor der Rueckfall
ueberhaupt drankaeme. Ausgefuehrt vor **und** nach der Aenderung, mit allen
drei Umlenkungen gesetzt, Ausgabe beide Male identisch:

```
steam root: c:\program files (x86)\steam
   library: c:\program files (x86)\steam\steamapps | exists: True
   library: C:\Program Files (x86)\Steam\steamapps | exists: True
   library: D:\SteamLibrary\steamapps | exists: True
find_game_dir(): D:\SteamLibrary\steamapps\common\ELDEN RING NIGHTREIGN\Game
```

**Neuer Fall** `test_find_game_dir_asks_about_nothing_steam_did_not_name`
(`tests/test_game_dir_recognition.py`). Er haelt die **Kandidatenliste** fest,
nicht ihre Antwort: er ersetzt `looks_like_the_game` durch einen Zaehler und
prueft, dass genau **ein** Ordner vorgelegt wird, der aus der Bibliothek. Ein
Fall, der nur das Ergebnis (`None`) gelesen haette, waere auf jeder Maschine
gruen, an der gerade nichts haengt.

Ausserdem angepasst: der Modul-Docstring und zwei Kommentare in derselben
Datei, die den Rueckfall noch als bestehend beschrieben.

### 2. C3 fragt ab zwei Ebenen Abstieg (`nrplanner/firstrun.py`)

- `_where_it_sits` kennt einen **vierten** Zustand `DEEPER`: gleicher Ordner
  (`SAME`), eine Ebene hinein (`INSIDE`), zwei oder mehr (`DEEPER`), oder
  ausserhalb (`OUTSIDE`). Der Abstand ist `len(landed) - len(seen)`, dieselben
  Pfadteile, die die Funktion ohnehin vergleicht.
- Neue Konstante `LEVELS_TAKEN_ON_TRUST = 1` mit ihrer Herleitung im
  Kommentar: **eine** Ebene, weil Steams `Browse local files` genau eine Ebene
  ueber `...\Game` landet (UI_SPEC 4.2). Keine Messung, sondern die
  dokumentierte Form des Regelfalls — die Zahl ist nicht gemessen und gibt
  auch nicht vor, es zu sein.
- `SEARCH_DEPTH` und `SEARCH_PARENTS` **unveraendert 3 und 2** (AK-249);
  `git show b0e7ee4 -- nrdata/gamefiles.py` ist leer, die Datei ist in diesem
  Commit nicht enthalten.
- C3, zweite Pfadzeile, woertlich aus §3 des Nachtrags:
  `The game itself is not directly in that folder. It is in:`. Titel, erste
  Pfadzeile, Schlusssatz und Knopfbeschriftungen unveraendert.
- `settle_the_game_folder` zeigt C3 jetzt bei `OUTSIDE` **und** bei `DEEPER`.
- `found_it` bleibt unveraendert und liefert damit fuer `DEEPER` **C1**, nicht
  C2 (AK-242): C2 sagt `inside the folder you picked`, und unter einer gerade
  beantworteten Rueckfrage steht der Satz, der keine Lagebeziehung behauptet.

**Fuenf neue Faelle** in `tests/test_first_run_panel.py`, dazu die
Transkription von C3 auf den neuen Wortlaut gezogen und drei Bestandsfaelle
erweitert bzw. umbenannt:

| Fall | Kriterium |
|---|---|
| `test_two_levels_down_is_asked_about` (neu) | AK-246, Gegenprobe 1 |
| `test_three_levels_down_is_asked_about_and_not_turned_down` (neu) | AK-246, Gegenprobe 2 (Grenzfall `SEARCH_DEPTH`) |
| `test_nothing_is_built_while_the_question_about_a_deep_descent_is_open` (neu) | AK-246: „der Bau beginnt nicht", als gezaehlter Aufruf statt als Bildschirmzustand |
| `test_the_question_reads_the_same_for_a_climb_and_for_a_descent` (neu) | AK-247, beide Ausloeser |
| `test_c3_says_the_game_is_not_directly_in_the_folder_that_was_picked` (Bestand, umbenannt) | AK-247, Wortlaut plus die ausdrueckliche Abwesenheit von `outside that folder` |
| `test_at_most_one_question_when_the_name_fails_two_levels_down` (neu) | AK-248 |
| `test_the_parent_folder_is_the_ordinary_case_and_costs_no_click` (Bestand) | AK-246, die klickfreie Haelfte — Docstring um AK-246 ergaenzt |
| `test_the_confirmation_says_inside_only_when_it_is_inside` (Bestand) | AK-242, um den `DEEPER`-Fall erweitert |

### 3. AK-131 bekommt seine zwei Tests (`tests/test_first_run_panel.py`)

`app.py` wurde **nicht** angefasst und musste es auch nicht.

- `test_missing_param_definitions_do_not_open_the_folder_question`:
  `defs_dir()` ist `None`, es gibt einen Spielordner, und `run()` liefert
  `go_on=True` mit genau der bestehenden Meldung („The param definitions are
  missing, …"), die `app.py` in seine `QMessageBox` gibt.
- `test_an_installation_that_cannot_be_read_does_not_open_the_question`:
  Stufe 1 sagt ja (drei Dateien und ein Byte), das Lesen scheitert
  (`ValueError: expected magic b'BND4' at 0, got b''`), und wieder kommt der
  Fehler zurueck statt eines Panels.

Beide **stubben den Bau nicht aus**, sondern lassen ihn wirklich laufen: das
Fenster ist eine Unterklasse des echten `_Window`, deren Frage-Zustand eine
Assertion ist. Beide Faelle schreiben in kein echtes Verzeichnis
(`paths.cache_dir` und `paths.snapshot_path` zeigen auf `tmp_path`), und die
Verknuepfung wird nicht angelegt, weil `_build_what_is_missing` sie nur ohne
Fehler anlegt.

## Tests

**Volle Suite, `pytest -n auto`, mit allen drei Umlenkungen:**

```
1699 passed, 9 skipped in 181.71s (0:03:01)
```

Gegen die Vorgabe **1691 passed, 9 skipped, 0 failed** (Director, `ef6761b`):
**+8 passed**, und das sind genau die acht neuen Faelle — 5 fuer Punkt 2, 2
fuer Punkt 3, 1 fuer Punkt 1. Je Datei nachgezaehlt:
`tests/test_first_run_panel.py` 57 → 64, `tests/test_game_dir_recognition.py`
41 → 42. Die beiden weiteren Zeilen der Tabelle oben sind **kein** Zuwachs:
`test_c3_says_the_game_is_not_directly_in_the_folder_that_was_picked` ist der
umbenannte Bestandsfall zum alten Wortlaut, die zwei letzten Zeilen sind
erweiterte Bestandsfaelle. Skips unveraendert 9, keine Fehlschlaege.

**Mutationsbeweis, zehn Mutationen, alle getoetet, keine ueberlebt.** Gefahren
ueber einen `tar`-Abzug des Baums (kein `git checkout`, kein Eingriff in den
Arbeitsbaum), je Mutation ein frischer Baum aus einer unberuehrten Kopie,
`PYTHONDONTWRITEBYTECODE=1`, gelaufen gegen `tests/test_first_run_panel.py`
und `tests/test_game_dir_recognition.py` (106 Faelle, ~9 s je Lauf). Treiber:
`…/scratchpad/T-164/campaign.py`. Jede Mutation wurde vorher darauf geprueft,
dass ihr Anker **genau einmal** passt.

| Mutation | Ergebnis | was faellt |
|---|---|---|
| 1a die sechs Laufwerkskandidaten sind zurueck | 1 failed | `test_find_game_dir_asks_about_nothing_steam_did_not_name` |
| 1b **ein** Laufwerkskandidat ist zurueck (`D:`) | 1 failed | derselbe |
| 2a `LEVELS_TAKEN_ON_TRUST = 3` (jeder Abstieg wieder klickfrei) | 4 failed | `two_levels_down`, `three_levels_down`, `question_reads_the_same`, `nothing_is_built_while…` |
| 2b `LEVELS_TAKEN_ON_TRUST = 0` (auch die eine Ebene fragt) | 3 failed | `the_parent_folder_is_the_ordinary_case…`, `the_next_dialog_opens…`, `the_folder_is_kept_before…` |
| 2c der `DEEPER`-Zweig entfernt | 4 failed | wie 2a |
| 2d C3 sagt wieder `outside that folder, in:` | 4 failed | `c3_says_the_game_is_not_directly_in…`, `a_climb_out_of_the_picked_folder…`, `question_reads_the_same`, `two_levels_down` |
| 2e `found_it` gibt auch fuer `DEEPER` C2 | 2 failed | `the_confirmation_says_inside_only_when_it_is_inside`, `two_levels_down` |
| 2f der neue Ausloeser gewinnt gegen die Namensfrage | 1 failed | `at_most_one_question_when_the_name_fails_two_levels_down` |
| 3a die `defs is None`-Meldung entfernt | 1 failed | `missing_param_definitions_do_not_open_the_folder_question` |
| 3b `run()` fragt auch mit vorhandenem Spielordner | 3 failed | beide AK-131-Faelle und `a_find_by_the_automatic_route_is_never_written_back` |

**2b ist die Gegenrichtung und deshalb wichtig:** sie zeigt, dass die
klickfreie Haelfte von AK-246 (eine Ebene bleibt ohne Klick, A15) genauso
bewacht ist wie die fragende. **1b zeigt**, dass der Waechter nicht an der
Sechserzahl haengt, sondern an der Eigenschaft.

**Rot-vorher, je Schutzmassnahme einzeln (L-007):** die Tabelle ist genau
das — jede der drei Aenderungen (Rueckfall weg, `DEEPER`-Zweig, neuer
Wortlaut) wurde einzeln zurueckgebaut, und jedes Mal fiel ein benannter Fall.
Keine der Mutationen verschiebt eine Schnittstelle; alle bleiben importierbar
und aendern nur Verhalten.

**Eigenschaft statt Fundstelle (L-006).** Nach dem Wegfall des Rueckfalls
projektweit gesucht, mit vier unabhaengig formulierten Masken:

| Maske | Treffer |
|---|---|
| `SteamLibrary` in `*.py` | 3 ausserhalb `tests/` (2× Prosa im neuen Docstring, 1× ein Testname in `mutate.py`), in `tests/` 6 in drei Dateien — alle **Beispielpfade** fuer die Namenspruefung bzw. den Bibliotheksstart, keine Kandidatenbildung |
| `for drive in`, `CDEFGH`, `ascii_uppercase` in `*.py` | **0** |
| `bare.drive` (case-insensitiv) | 2, beide in `tests/test_game_dir_recognition.py` und beide beschreiben den **Wegfall** |
| `outside that folder` in `*.py`/`*.md` ausserhalb `UI_SPEC.md`/`docs/` | 3, alle drei erklaeren den alten Wortlaut oder pruefen seine Abwesenheit |

Es gibt also im Programm **keine** zweite Stelle, die einen Pfad aus einem
Laufwerksbuchstaben baut.

## Umlenkung der drei Datenverzeichnisse — mit Positivkontrolle

Ein Skript druckt `favourites.ORG`, `paths.cache_dir()` und
`shortcut.shortcut_path()`; einmal ohne und einmal mit Umlenkung.

**Ohne (Positivkontrolle — die Messung zeigt wirklich auf den Nutzer):**
```
favourites.ORG          = DankYeeter
paths.cache_dir()       = C:\Users\Daniel\AppData\Local\NightreignHelper
shortcut path           = C:\Users\Daniel\AppData\Roaming\...\Programs\Nightreign Helper.lnk
```
**Mit (`NIGHTREIGN_SETTINGS_ORG=DankYeeterT-164`, `LOCALAPPDATA`/`APPDATA` auf
`…/scratchpad/T-164/local` bzw. `/roaming`):**
```
favourites.ORG          = DankYeeterT-164
paths.cache_dir()       = …\scratchpad\T-164\local\NightreignHelper
shortcut path           = …\scratchpad\T-164\roaming\...\Programs\Nightreign Helper.lnk
```

**Beide Haelften, nicht nur die eine:** Unter `pytest` ueberschreibt
`tests/conftest.py` die Organisation unbedingt auf `DankYeeterTests` und die
Anwendung auf `NightreignHelperTests-<pid>` — also lief die Suite **nicht**
unter meinem Wert, aber ebenfalls nicht am Speicher des Nutzers.
Gegengeprueft: `HKCU\Software\DankYeeterT-164` existiert **nicht** (kein
Skript von mir hat QSettings geoeffnet), `HKCU\Software\DankYeeter\...` ist
unberuehrt geblieben. Das echte Start-Menue enthaelt **keinen** Eintrag mit
„Nightreign" (geprueft nach dem Lauf), das umgelenkte `roaming` ist leer —
es wurde ueberhaupt keine Verknuepfung angelegt. Der feste Testabzug wurde in
das umgelenkte `LOCALAPPDATA` **kopiert** (841 Dateien, 22 MB), nicht
referenziert.

**Der Spielstand** wurde nicht angefasst; gelesen wurde nur die
Spielinstallation, und auch die nur durch `find_game_dir()` (drei `stat` und
ein Byte). Kein Bildnachweis noetig, kein Programmfenster gezeigt.

## DoD

- [x] Anforderung verstanden, Annahmen oben dokumentiert
- [x] Build und Tests gruen in der benannten Umgebung (Windows 10 x64,
      `docs/audit-and-advisor-design`): 1699 passed, 9 skipped, 0 failed
- [x] Neue Tests fuer neue Logik, jede mit einer toetenden Mutation
- [—] Linter: das Projekt konfiguriert keinen (keine `pyproject.toml`, keine
      `setup.cfg`, keine `ruff`/`flake8`-Datei). Punkt entfaellt.
- [x] Keine Secrets, keine TODOs, kein toter Code
- [x] UI-Vorgaben: Texte woertlich aus `UI_SPEC.md` §3 des SEC-032-Nachtrags
- [x] Bericht geschrieben; `UI_SPEC.md`, `docs/state.md`, `qa/findings.md`,
      `security/findings.md` und `scripts/` nicht angefasst
- Ungeprueft: Linux und macOS (kein Ziel). **Kein Nachweis am laufenden
  Fenster** — AK-129/AK-132-Muster bleibt der Baurunde vorbehalten, wie im
  Auftrag vorgesehen.

## An den director

**1. Eine Entscheidung, die ich fuer dich offengelassen habe (kein
Blocker).** Der neue Ausloeser steht in `settle_the_game_folder` als
**zweiter Zweig neben** dem alten, jeder mit seinem eigenen Kriterium:

```python
        elif verdict.where == OUTSIDE:
            # The search left the tree he pointed at (AK-232).
            panel = c3(verdict)
        elif verdict.where == DEEPER:
            # It stayed in his tree, but came back with a folder two levels
            # down or more -- one he was never shown (AK-246, SEC-032).
            panel = c3(verdict)
```

Die knappere Form waere eine Zeile: `elif verdict.where in (DEEPER, OUTSIDE):`.
Sie haette den registrierten Anker der Mutation
`C3-d-any-deviation-asks-as-t145-had-it` in `scripts/differential/mutate.py`
zerstoert (`old = "        elif verdict.where == OUTSIDE:"`, muss **genau
einmal** passen) und damit
`test_every_mutation_still_finds_its_anchor_in_the_real_source[C3-d…]` rot
gemacht. `scripts/` steht auf deiner Nicht-anfassen-Liste, also habe ich die
Form gewaehlt, die beides haelt: gruene Suite **und** unveraenderte Zaehne der
Bestandsmutation (C3-d beisst weiter, ihre Begruendungstext stimmt weiter).
**Willst du die einzeilige Form, ist genau eine Zeile in `mutate.py`
nachzuziehen** — `old` auf den neuen Wortlaut, `new` bleibt
`elif verdict.where != SAME:`. Das ist ein Einzeiler fuer den naechsten
Auftrag, kein Umbau.

Dieselbe Ruecksicht traf `found_it`: der Anker
`    if verdict.where == INSIDE:` (Mutation `C2-g`) blieb unveraendert, weil
der vierte Zustand `DEEPER` die Unterscheidung traegt. Das war hier kein
Kompromiss, sondern die bessere Loesung — `C2-g` beisst dadurch sogar
schaerfer als vorher (3 statt 2 falsche Zustaende).

**2. Das Mutationsregister ist nicht nachgetragen** (laut Auftrag nicht mein
Scope). Die zehn Mutationen dieses Laufs liegen im Treiber
`…/scratchpad/T-164/campaign.py` und `campaign_ak131.py`, mit Anker, Ersatz
und gemessenem Ergebnis — daraus laesst sich ein Register-Eintrag ohne
Nachmessen erzeugen. **Der Scratchpad ist fluechtig**: wenn die Eintraege
gewollt sind, muss der Auftrag dafuer kommen, solange das Verzeichnis noch
steht. Kandidaten mit Wert: 1a (Rueckfall zurueck), 2a und 2b (beide
Richtungen der Schwelle), 2d (Wortlaut), 3b (`run()` fragt zu viel).

**3. Ein Fund ausserhalb des Auftrags, nicht behoben.** In
`nrdata/gamefiles.py` liefert `_steam_roots()` die Registry-Wurzel **und**
`C:\Program Files (x86)\Steam` fest — dieselbe Bibliothek wird dadurch
regelmaessig doppelt und dreifach als Kandidat gebaut (siehe die Ausgabe oben:
`C:\Program Files (x86)\Steam\steamapps` erscheint viermal, `D:\SteamLibrary`
zweimal). Das ist **keine** Sicherheitsluecke — diese Pfade stehen unter dem
Schutz von `Program Files` bzw. kommen aus Steams eigener Liste — sondern
Doppelarbeit und ein leicht irrefuehrender Bestand. Art: Debt. Risiko: gering.
Aufwand: klein (Kandidaten vor der Pruefung eindeutig machen). **Nicht
angefasst**, weil es weder im Auftrag noch in SEC-031 steht.

**4. Kein Sicherheitsfund** ueber SEC-031/SEC-032 hinaus. Der Automatikweg
fasst nach dieser Aenderung ausschliesslich Pfade an, die Steam selbst nennt.

## An qa-engineer

- **AK-246**, drei Faelle am laufenden Fenster: (a) den Ordner **direkt
  ueber** `...\Game` waehlen — **kein** C3, sofort C2 und der Bau; (b) dessen
  Elternordner (`...\common`) — C3 mit beiden Pfaden, **keine
  Fortschrittsanzeige**, bevor `Use this folder` gedrueckt ist; (c) drei Ebenen
  darueber — ebenfalls C3 und **nicht** E1.
- **AK-247:** derselbe Satz in beiden Faellen, Abstieg **und** Aufstieg (aus
  einem Unterordner von `...\Game` heraus waehlen).
- **AK-248:** einen **umbenannten** Installationsordner ueber seinen
  Elternordner waehlen — genau **ein** Frage-Zustand (W1), nicht zwei.
- **Nach C3 kommt C1**, nicht C2: die Bestaetigungszeile darf beim tiefen
  Abstieg **nicht** `inside the folder you picked` sagen.
- **SEC-031, zweite Haelfte:** ein Laufwerk mit
  `X:\SteamLibrary\steamapps\common\ELDEN RING NIGHTREIGN\Game` (X zwischen C
  und H) darf beim Start **nicht** mehr automatisch uebernommen werden,
  solange Steam diese Bibliothek nicht kennt — erwartet wird der
  A15-Auswahldialog. Umgekehrt muss eine Installation, die in
  `libraryfolders.vdf` steht, weiterhin **wortlos** gefunden werden (auf
  dieser Maschine `D:\SteamLibrary\...`, belegt).
- **Kanten, die ich nicht mit einem Fenster gepruefen habe:** AK-129
  (Umbruch/Abschneiden) mit dem **neuen, laengeren** C3-Satz bei 125 % und
  150 % — der Satz ist rund 20 Zeichen laenger als der alte und steht auf
  einer eigenen Zeile ueber dem Pfad. Das ist der wahrscheinlichste Ort, an
  dem diese Aenderung eine Oberflaechenregel verletzt.

## An ui-ux-designer

Keine Abweichung von deiner Vorgabe. Zwei Anmerkungen:

1. Dein Umsetzungshinweis (`len(landed) - len(seen)` in `_where_it_sits`) hat
   getragen; die Schwelle steht als benannte Konstante
   `LEVELS_TAKEN_ON_TRUST = 1` mit deiner Begruendung im Kommentar, nicht als
   nackte `1` im Vergleich.
2. AK-248 ist **strukturell** erfuellt und nicht nur zufaellig: die
   Namensfrage steht in der Kette **vor** beiden C3-Ausloesern, W1 kann also
   nie mit C3 zusammenfallen. Die Mutation 2f (Reihenfolge getauscht) faellt
   auf genau diesen Fall.
