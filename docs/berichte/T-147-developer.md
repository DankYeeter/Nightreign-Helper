# T-147 - V1: ein Aufloesungspunkt fuer den Spielordner (developer)

```
STATUS: erledigt
AUFTRAG: T-147 - V1 aus ARCHITECTURE.md Nachtrag XI (AD-030), plus SEC-028 und
         der Traversierungsteil von SEC-030
GELESEN: docs/tasks/T-147.md · ARCHITECTURE.md Nachtrag XI (Zeilen 5370-6100,
         ganz: XI-0, AD-030, AD-031, Umsetzungstabelle V1-V5, R1-R18, Verbote,
         Risiken, offene Fragen) · UI_SPEC.md §4 (4.1-4.4), §5, §6, Text E1/W1,
         AK-106 bis AK-132 · docs/berichte/T-144-security-reviewer.md
         (SEC-028, SEC-029, SEC-030) · docs/berichte/T-142-developer.md
         (Suitezahl) · nrdata/gamefiles.py, nrdata/bhd5.py, nrdata/oodle.py,
         nrplanner/datasource.py, nrplanner/favourites.py,
         tests/test_settings_store.py, tests/conftest.py · CLAUDE.md
GEAENDERT: nrdata/gamefiles.py · nrplanner/gamepath.py (neu) ·
         nrplanner/datasource.py · tests/test_game_dir_recognition.py (neu) ·
         tests/test_game_path_memory.py (neu). Zwei Commits, 83e1b90 und
         87d6334, beide mit Pfad hinter `--`. Kein Push.
ANNAHMEN: (1) R7 und R8 stehen in Nachtrag XI unter der V2-Datei
         `test_first_run_panel.py`, ihre Gegenstaende (`looks_like_the_game`,
         `search_from`) baue aber ich. Ich habe ihren Qt-freien Teil in
         `tests/test_game_dir_recognition.py` gebaut; der Panel-Teil (E1, W1,
         die zwei Knoepfe, der Standardknopf) bleibt V2. (2) „Wird die Grenze
         erreicht, gilt der Ordner als nicht erkannt" (UI_SPEC 4.2) lese ich
         als „ohne Fund"; ein Treffer, der vor dem Aufbrauchen des Budgets
         schon gefunden war, wird zurueckgegeben. Begruendung unten, Punkt 7.
         (3) Die 16 383 Zeichen aus R3 habe ich uebernommen, nicht selbst
         hergeleitet - der Beleg gehoert dem `architect`.
NAECHSTER: qa-engineer (prueft R1-R6 nach), danach director wegen der drei
         Meldungen unten
BLOCKIERT DURCH: nichts
```

---

## 1. Umgesetzt

### `nrdata/gamefiles.py` (Qt-frei, +203 Zeilen, Commit 83e1b90)

| Neu | Was es tut |
|---|---|
| `looks_like_the_game(path)` | Stufe 1, AK-112: `regulation.bin` vorhanden, lesbar, nicht leer **und unter der Obergrenze**; eine `data*.bhd` aus `bhd5.ARCHIVE_KEYS`; eine DLL aus `oodle._DLL_NAMES`. Jede `OSError`/`ValueError` heisst „ungueltig", nie ein Fehler nach oben. |
| `is_named_nightreign(path)` | Stufe 2, AK-113: der Ordner oder eine seiner drei Elternebenen traegt `NIGHTREIGN` im Namen, Gross-/Kleinschreibung egal. |
| `search_from(start)` | UI_SPEC 4.2: drei Ebenen runter, zwei rauf, 400 Verzeichnisse, 2 s. Ergebnis ist immer der Ordner, der `regulation.bin` direkt enthaelt, `Path.resolve()`-gehalten. |
| `IDENTITY_WORD`, `NAMED_LEVELS`, `MAX_REGULATION_BYTES`, `SEARCH_DEPTH`, `SEARCH_PARENTS`, `MAX_DIRECTORIES`, `SEARCH_SECONDS` | Die Zahlen der Vorgabe als benannte Konstanten, jede mit ihrer Herleitung im Kommentar. |
| `_search_within_budget`, `_is_a_door_out_of_the_tree`, `_subfolders`, `_changed_at`, `_the_best_of`, `_monotonic` | Innenleben. `_search_within_budget` gibt zusaetzlich die **Zahl besuchter Verzeichnisse** zurueck - nur deshalb ist sie eine eigene Funktion (R8 haelt sie gegen das Literal 400). `_monotonic` ist ein Modulattribut, damit ein Test dem Budget eine eigene Uhr geben kann; **keine Zeitschranke in der Suite**. |

`find_game_dir()` ist **unveraendert** (Vorgabe: „wie heute").

### `nrplanner/gamepath.py` (neu, Qt-Seite, 136 Zeilen, Commit 87d6334)

`GAME_KEY = "paths/game"`, `SAVE_KEY = "paths/save"`, `remembered_game()`,
`remembered_save()`, `remember_game()`, `remember_save()`, `resolve_game()`.
Der Speicher wird ausschliesslich ueber `favourites.ORG`/`favourites.APP`
geoeffnet (`test_settings_store.py` haelt das weiterhin, es ist gruen).

`resolve_game()` ist die Kette 1-3 aus AD-030 in vier Zeilen: gemerkter Pfad,
der **dieselbe** Pruefung besteht, unter der er angenommen wurde; sonst
`find_game_dir()`, dessen Ergebnis **nicht** zurueckgeschrieben wird. Schritt 4
(Panel) ist V2 und steht hier nicht.

### `nrplanner/datasource.py` (Commit 87d6334)

Die drei Stellen `_regulation_matches:96`, `_load_data:142`,
`_no_data_message:168` fragen jetzt `gamepath.resolve_game()`, lazy importiert
in der Funktion, wie `from nrdata import gamefiles` es dort schon war. Kein
Text geaendert.

### Die zwei Sicherheitsbefunde

**SEC-028.** Die Obergrenze steht in `looks_like_the_game`, also in derselben
Funktion, die AK-112 prueft - nicht als Deckel an den Lesestellen. Rezept der
Zahl, im Code und hier: gemessen **1 974 720 Byte** auf dieser Installation
(08.09.2026, `stat().st_size`, **Stichprobe 1**, nicht von mir gemessen,
sondern aus T-144 uebernommen); Schranke **64 MiB = 67 108 864 Byte**; Faktor
**34,0**. Eine zu grosse Datei laesst den Ordner durchfallen, und ein
durchgefallener Ordner ist genau der Fall, den Text E1 laut abweist (V2).
Ein Fall haelt fest, dass die Schranke ihren **eigenen Wert noch annimmt**
(64 MiB genau) und erst einen Zaehler darueber ablehnt.

**SEC-030, Traversierungsteil.** `_subfolders` betritt keine Reparse-Punkte
(Junction oder Symlink, ueber `st_file_attributes` und
`FILE_ATTRIBUTE_REPARSE_POINT`, nicht ueber `is_junction()` - das gibt es erst
ab 3.12), und `_the_best_of` gibt das Ergebnis ueber `Path.resolve()` zurueck.
Drei Faelle mit **echten Junctions** (`_winapi.CreateJunction`, keine
Adminrechte noetig): das Ziel ausserhalb wird nicht gefunden, eine Junction auf
sich selbst haengt die Suche nicht auf, und ein vom Nutzer **selbst gewaehlter**
Verknuepfungsordner liefert den echten Ordner dahinter.

---

## 2. Tests

**73 neue Faelle**, zwei neue Dateien, beide ohne Fenster:

* `tests/test_game_dir_recognition.py` - 36 Faelle: Stufe 1 (die drei
  Bedingungen einzeln, leer, Decke, ueber der Decke, Ordner weg, Pfad mit
  `\0`), Stufe 2 (sechs Pfade parametrisiert), die Suche (runter 1/3, nicht 4;
  rauf 1/2, nicht 3; flachster gewinnt; bei Gleichstand der neuere), beide
  Budgets, vier Junction-Faelle.
* `tests/test_game_path_memory.py` - 37 Faelle: **R1** (beide Schluessel als
  Literal), **R2** (AST-Scan ueber den ganzen Baum plus ein schaerferer Scan
  auf `gamepath.py` selbst, dazu zehn Positiv- und Negativproben und die leere
  `OFFEN`-Liste), **R3** (sechs Beschaedigungen, je zweimal: „liest sich wie
  abwesend" und „faellt durch, wirft nicht, laesst den Eintrag stehen"),
  **R4** (Komma im Ordnernamen), **R5** (Kette und Zaehlwerte, drei Faelle),
  **R6** (AST-Scan ueber `nrplanner/`, plus der Fall, der eine ueberfluessig
  gewordene Ausnahme erzwingt).

**Suitezahl.** `pytest -n auto` → **1490 passed, 9 skipped, 0 failed** in
172,21 s. Vorgabe aus T-142: **1417 passed, 9 skipped, 0 failed**. Differenz
**+73**, und das ist genau die Zahl der neuen Faelle - nichts anderes hat sich
bewegt. (Zwischenmessung nach der ersten Haelfte: 1488 = 1417 + 71, vor den
zwei zuletzt ergaenzten Faellen.)

Alle drei Umlenkungen waren dabei gesetzt und sind unten belegt.

---

## 3. Mutationsbeweis - 22 Mutationen, 20 tot, 2 ueberlebend, 3 Kontrollen

Gefahren gegen eine `copytree`-Kopie des Baumes (`nrplanner nrdata tests
scripts pytest.ini run.py`), je Mutation eine Zeile ersetzt, danach die Datei
aus einer unberuehrten Zweitkopie zurueck; `PYTHONDONTWRITEBYTECODE=1`,
`-p no:cacheprovider`, nur die zwei neuen Dateien (10,1 s je Lauf). Jeder Anker
musste **genau einmal** passen, sonst haette der Lauf `ANCHOR MISSED` gemeldet;
das ist nicht vorgekommen. Treiber:
`…/scratchpad/T-147/mutate_driver.py`, Ergebnisdatei
`…/tasks/blglpk02a.output`.

| # | Mutation | Ergebnis | Was gefallen ist |
|---|---|---|---|
| 1 | `ceiling-on-regulation-removed` | KILLED | ueber der Decke wird angenommen |
| 2 | `ceiling-excludes-its-own-value` (`<=`→`<`) | KILLED | die Decke selbst wird abgelehnt |
| 3 | `empty-regulation-accepted` (`0 <`→`0 <=`) | **SURVIVED** | siehe unten (a) |
| 4 | `archive-condition-dropped` | KILLED | Regulation+DLL genuegt |
| 5 | `dll-condition-dropped` | KILLED | Regulation+Archiv genuegt |
| 6 | `junctions-walked-into` | KILLED | SEC-030, Ziel ausserhalb wird gefunden |
| 7 | `result-not-resolved` | KILLED | SEC-030, Verknuepfung statt Ziel |
| 8 | `directory-budget-removed` | KILLED | 501 statt 400 besucht |
| 9 | `second-budget-removed` | KILLED | die Uhr wird nicht mehr gelesen |
| 10 | `directory-budget-raised` (400→4000) | KILLED | Zaehlwert gegen das Literal |
| 11 | `one-level-deeper` (Tiefe 4) | KILLED | vier Ebenen werden gefunden |
| 12 | `one-parent-further` (3 rauf) | KILLED | drei Ebenen rauf werden gefunden |
| 13 | `name-check-widened` | KILLED | Stufe 2 sagt zu allem ja |
| 14 | `automatic-find-written-back` | KILLED | **M3**, 8 Faelle |
| 15 | `a-second-predicate-for-the-start-check` (`exists()`) | KILLED | **M3**, der Umkehrfall |
| 16 | `remove-on-a-path-key-by-name` (`remove(key)`) | KILLED | Verhalten **und** der `gamepath`-Scan |
| 17 | `remove-on-a-path-key-written-out` (`remove("paths/game")`) | KILLED | Verhalten **und** der Baum-Scan |
| 18 | `the-key-renamed` | KILLED | R1 |
| 19 | `type-str-dropped-when-reading` | **SURVIVED** | siehe unten (b) |
| 20 | `absolute-check-dropped` | KILLED | „42" und „Game" gelten als Pfad |
| 21 | `empty-null-and-length-checks-dropped` | KILLED | `\0` und 20 000 Zeichen gelten |
| 22 | `datasource-asks-the-automatic-route-again` | KILLED | R6 |

**Die zwei Ueberlebenden, gemeldet und nicht nachgebessert (L-008 c):**

**(a) Die Leerheitspruefung wird von zwei Guerteln getragen, und keiner haelt
allein.** `0 < size` und die Zeile `if not handle.read(1)` lehnen beide eine
leere `regulation.bin` ab. Kontrolle gefahren: `control-emptiness-read-dropped`
(nur die Lesezeile weg) **ueberlebt ebenfalls**;
`control-both-emptiness-belts-dropped` (beide zusammen weg) **toetet**
(`…/tasks/`-Lauf `mutate_controls.py` / `mutate_controls2.py`). Nach L-007 ist
damit **keiner der beiden Guertel fuer sich** eine Regressionssicherung fuer den
Leerfall - das Paar ist es. Beide haben ihren eigenen Grund (AK-112 verlangt
„lesbar" **und** „nicht leer"; die Groessenpruefung traegt zusaetzlich die
Decke), deshalb habe ich nichts entfernt. **Wer den Leerfall einzeln gesichert
haben will, braucht eine dritte Form** - das ist eine Entscheidung des
`director`, keine, die ich still treffe.

**(b) `type=str` ist auf dem Windows-Registry-Speicher nicht messbar.** Der
`architect` nennt als toetende Mutation zu R4 „`type=str` beim Lesen entfernen
→ der Wert kommt als Liste zurueck". **Auf dem nativen Windows-Speicher
stimmt das nicht.** Gemessen (`…/scratchpad/T-147/probe.py`):

```
comma, type=str : 'D:\\Games\\Elden Ring, alt\\Game'
comma, no type  : 'D:\\Games\\Elden Ring, alt\\Game'   <- keine Liste
list,  type=str : ''
list,  no type  : ['a', 'b']
```

Das Komma wird auf der Registry **nie** zur Liste; die Liste entsteht nur bei
einem dateigestuetzten Speicher (INI, und damit auf Linux). Meine
`isinstance`-Pruefung faengt den Listenfall auf beiden Speicherformen ab,
deshalb ueberlebt das Entfernen von `type=str` allein - und das Entfernen der
`isinstance`-Pruefung allein ebenso. **Beide zusammen entfernt toetet vier
Faelle** (`control-type-str-and-isinstance-both-dropped`). Auch hier: zwei
Guertel, die eine Luecke von zwei Seiten decken; `type=str` bleibt, weil AD-030
es verlangt und weil es der Guertel ist, der auf einem dateigestuetzten
Speicher greift.

**Nicht getan: die 22 Mutationen in `scripts/differential/mutate.py`
eintragen.** `scripts/` steht nicht auf der Liste der beruehrten Dateien
dieses Auftrags. Eine Nachregistrierung wuerde die Suite um **22** Faelle auf
1512 heben (je Eintrag ein
`test_every_mutation_still_finds_its_anchor_in_the_real_source`). Die Anker
liegen wortwoertlich im Treiber im Scratchpad; **der ist nur so lange lesbar,
wie diese Sitzung lebt** - wenn die Registrierung gewollt ist, gehoert sie in
den naechsten Auftrag dieser Sitzung, sonst muss sie neu erzeugt werden.

---

## 4. Eigenschaft statt Fundstelle (L-006) - zwei Suchen je Befund

**SEC-028.** Maske A `read_bytes()` ueber `nrdata/` und `nrplanner/` →
**9 Treffer**; Maske B `regulation.bin` ueber dieselben →
**13 Dateien**. Vier davon lesen `regulation.bin` ganz: `extract.py:2805`,
`datasource.py:106`, `firstrun.py:31`, `regulation.py:16` - dieselbe Vier, die
T-144 nennt. **Keine davon habe ich angefasst**, das ist die Behebungsrichtung
des Pruefers: die Schranke sitzt an der Annahme, nicht an den Lesestellen.
Was das **nicht** deckt, und ich melde es als eigenen Punkt an den `director`:
`find_game_dir()` prueft nur `(<Ordner>/regulation.bin).exists()` und geht
**nicht** durch `looks_like_the_game`. Ein automatisch gefundener Steam-Ordner
mit einer 20-GiB-`regulation.bin` wird also weiterhin ungedeckelt gehasht. Das
ist die **alte** Vertrauensgrenze (Schreibrechte im Spielordner, SEC-006,
angenommen), nicht die neue - deshalb habe ich sie **nicht** eigenmaechtig
geschlossen. `resolve_game()` durch Stufe 1 auch auf den Automatikfund zu
zwingen waere zwei Zeilen, wuerde aber AK-106/AK-107 beruehren („der
geglueckte Fall aendert sich nicht") und gehoert dem `ui-ux-designer` und dem
`security-reviewer`, nicht mir.

**SEC-030.** Maske `os.walk|scandir|rglob|\.glob(` ueber `nrdata/` und
`nrplanner/` → **3 Treffer**: mein `gamefiles.py:181`,
`paramdef.py:139` (`defs_dir`, das eigene Verzeichnis des Programms) und
`savefile.py:615` (`find_saves`, das Roaming-Profil). **Nur einer laeuft
ueber einen Baum, den der Nutzer aussucht** - der neue. Die Eigenschaft ist
damit an der einzigen Stelle geschlossen, an der sie heute existiert; kommt
mit V3 die Dateiauswahl fuer den Spielstand, ist `find_saves` erneut zu
betrachten (dort geht es aber um **eine** Datei, nicht um einen Abstieg).

---

## 5. Nachweis der drei Umlenkungen (mit Positivkontrolle)

Skript `…/scratchpad/T-147/where.py`, zweimal gefahren, unveraendert:

```
--- ohne Umlenkung (Positivkontrolle) ---
favourites.ORG          = DankYeeter
paths.cache_dir()       = C:\Users\Daniel\AppData\Local\NightreignHelper
shortcut.shortcut_path()= C:\Users\Daniel\AppData\Roaming\Microsoft\Windows\
                          Start Menu\Programs\Nightreign Helper.lnk
--- mit Umlenkung ---
favourites.ORG          = DankYeeterT-147
paths.cache_dir()       = …\scratchpad\T-147\localappdata\NightreignHelper
shortcut.shortcut_path()= …\scratchpad\T-147\appdata\Microsoft\Windows\
                          Start Menu\Programs\Nightreign Helper.lnk
```

Die Positivkontrolle zeigt, dass die Messung ohne Umlenkung wirklich auf die
Orte des Spielers zeigt. Alle Testlaeufe und der Mutationslauf liefen mit
`NIGHTREIGN_SETTINGS_ORG=DankYeeterT-147`, `LOCALAPPDATA` und `APPDATA` auf
das Scratchpad-Verzeichnis. **Unter `pytest` ueberschreibt `conftest.py` die
Org-Variable** auf `DankYeeterTests` / `NightreignHelperTests-<pid>` - auch das
ist vom Speicher des Spielers weg, aber es ist nicht mein Wert, und ich sage es
statt es zu behaupten. Der feste Testabzug aus `CLAUDE.md` wurde in das
umgelenkte `LOCALAPPDATA` **kopiert** (841 Dateien, 22 MB), nicht neu gebaut.
In den Spielstand und die Spielinstallation wurde nicht geschrieben; gelesen
hat davon in diesem Auftrag nichts (die neuen Faelle bauen ihre Ordner aus drei
leeren Dateien und einem Byte).

---

## 6. DoD

- [x] Anforderung verstanden, Annahmen oben benannt
- [x] Build & Tests gruen auf dem Zielsystem (Windows 10 x64):
      1490 passed, 9 skipped, 0 failed
- [x] Neue Tests fuer neue Logik; **Linter: das Projekt hat keinen
      konfiguriert**, der Punkt entfaellt (Zeilenlaenge habe ich von Hand auf
      < 80 gehalten, wie der Bestand)
- [x] Keine Secrets, keine TODOs, kein toter Code
- [x] Mutationsbeweis fuer alles, dessen Bruch still bliebe; zwei
      Ueberlebende gemeldet statt nachgebessert
- [x] Keine Zeitschranke in der Suite
- [x] `UI_SPEC.md`, `ARCHITECTURE.md`, `docs/state.md`, `qa/findings.md`,
      `security/findings.md`, `GOAL.md`, `firstrun.py`, `app.py` **nicht**
      angefasst
- [x] Doku: dieser Bericht. **Ungeprueft:** Linux und macOS (kein Ziel);
      die Junction-Faelle sind mit `skipif` versehen und laufen auf Windows -
      auf einem Nicht-Windows-Laeufer wuerden sie **4 zusaetzliche Skips**
      erzeugen.

---

## 7. An den `ui-ux-designer` (Abweichung mit Begruendung)

**Eine Lesart, die ich entschieden habe und die in der Spec offen ist.**
UI_SPEC 4.2 sagt: „Wird die Grenze erreicht, gilt der Ordner als nicht
erkannt." Ich gebe einen Treffer, der **vor** dem Aufbrauchen des Budgets
gefunden wurde, trotzdem zurueck. Der Fall, in dem sich die zwei Lesarten
unterscheiden, ist genau einer: `steamapps` mit vielen Spielen, das Spiel liegt
auf Ebene 3, und das 400. Verzeichnis faellt mitten in diese Ebene. Nach der
woertlichen Lesart bekaeme der Nutzer dann E1, obwohl sein Spiel gefunden war.
Die Budgets sollen eine Plattensuche verhindern, nicht einen Fund verwerfen -
deshalb so. **Wenn das falsch ist, ist es eine Zeile.**

Zweitens, damit es nicht untergeht: **AK-108 ist noch nicht erfuellt**, und
das ist Absicht (V2). `datasource._no_data_message` sagt weiterhin „No ELDEN
RING NIGHTREIGN installation was found." - jetzt aber erst, wenn auch der
gemerkte Pfad nichts hergibt, statt schon dann, wenn die Automatik leer
ausgeht. Der Satz ist unveraendert, seine Bedingung ist enger geworden.

## 8. An den `qa-engineer`

**Was zu pruefen ist:** R1-R6 in `tests/test_game_path_memory.py`, die Stufe-1-
und Suchfaelle in `tests/test_game_dir_recognition.py`.

**Kanten, die ich fuer die wichtigsten halte:**

1. **Der Umkehrfall zu M3** (`test_what_is_accepted_today_is_valid_tomorrow`):
   er prueft beide Richtungen mit **einem** Praedikat. Eine zweite
   Startpruefung faellt nur in einer der beiden Richtungen auf.
2. **Der gemerkte Wert nach einem Fehlschlag.** Drei Faelle vergleichen den
   Wert **vor und nach** der Aufloesung, nicht nur „ist noch irgendwas da".
3. **Junctions** brauchen echte Reparse-Punkte; ein `tmp_path`-Unterordner
   genuegt nicht. `_winapi.CreateJunction` reicht, keine Adminrechte.
4. **Der Zaehlwert 400** steht als Literal im Test und wird gegen
   `_search_within_budget` gehalten, nicht gegen `MAX_DIRECTORIES`.
5. **Was hier nicht geprueft ist:** alles mit Fenster. E1, W1, C1/C2, der
   Startort des Dialogs, AK-114 bis AK-120 - das ist V2. Und `paths/save` hat
   heute nur Lesen und Schreiben (R10/R11 gehoeren zu V3).
6. **Eine Falle fuer den Nachbau:** `tests/test_game_path_memory.py` darf
   `QSettings.remove` auf `paths/…` **selbst nicht** benutzen - der eigene
   Scan laeuft ueber die Tests mit. Aufraeumen geht ueber `setValue(key, "")`.

## 9. An den `director`

1. **Parallel lief T-148 im selben Arbeitsbaum.** Mein Auftrag sagt
   „Parallel: nichts". Waehrend ich arbeitete, stand `UI_SPEC.md` als
   `M` im `git status`, obwohl ich sie nur gelesen habe; inzwischen ist sie als
   `f0f8f24` („AK-243 und AK-244") committet. Es ist nichts passiert - meine
   zwei Commits nennen nur meine fuenf Dateien -, aber der naechste Lauf
   sollte es wissen, und die **erste Suitezahl** (1488) ist gegen einen
   Arbeitsbaum gemessen, in dem `UI_SPEC.md` uncommittet veraendert war. Die
   Endzahl 1490 ist gegen den jetzigen Stand gemessen.
2. **Die Decke greift nicht auf dem Automatikweg** (Punkt 4 oben). Der
   Automatikfund geht nicht durch `looks_like_the_game`. Ich habe es
   **nicht** geaendert, weil es AK-106/AK-107 beruehrt. Empfehlung: als Frage
   an `security-reviewer` und `ui-ux-designer` weiterreichen, zusammen mit
   OF-31 - es ist dieselbe Vertrauensgrenze.
3. **Zwei Ueberlebende, beide vom Typ „zwei Guertel, keiner allein"** (Punkt 3
   oben). Kein Nachbessern von mir. Wenn der Leerfall oder `type=str` einzeln
   gesichert sein soll, ist das eine kleine, eigene Entscheidung.
4. **Nachregistrierung der 22 Mutationen in `scripts/differential/mutate.py`**
   ist offen und war nicht in meinen Dateien. Kosten: +22 Suitefaelle. Die
   Anker sind nur so lange billig verfuegbar, wie diese Sitzung lebt.
5. **Bestehende Debt, nicht behoben:** `looks_like_the_game` liest
   `oodle._DLL_NAMES`, einen **privaten** Namen eines Nachbarmoduls. UI_SPEC
   4.3 schreibt genau das vor, und `firstrun`/`oodle` teilen die Liste heute
   schon so. Ein oeffentlicher Name (`oodle.DLL_NAMES`) waere eine
   Zwei-Zeilen-Aenderung an einer Datei, die mir nicht gehoert.
6. **Kein Messgut hinterlassen:** kein Server, kein Hintergrundprozess. Die
   Laeufe (Suite, Mutationskampagne) sind beendet; die Kopien liegen unter
   `…/scratchpad/T-147/` und ausserhalb des Projektbaums. Der Testabzug in
   `…/scratchpad/T-147/localappdata` ist eine Kopie, die Vorlage unter
   `%LOCALAPPDATA%\NightreignHelper-Testabzug` ist unberuehrt
   (`EXTRACT_VERSION` unveraendert, kein Grund zum Ersetzen).
