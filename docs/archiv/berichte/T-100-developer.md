# T-100 - SEC-024 und der Waechter, der in fremde Worktrees sieht (developer)

```
STATUS: erledigt
AUFTRAG: T-100 - SEC-024 und der Waechter, der in fremde Worktrees sieht
GELESEN: docs/tasks/T-100.md, tests/test_settings_store.py,
  tests/test_hostile_savefile.py, tests/test_one_build.py,
  tests/test_one_name_per_figure.py, tests/test_differential_track.py,
  nrdata/savefile.py, nrplanner/inventory.py, nrplanner/app.py (3400-3496),
  nrplanner/deeptab.py (313-450), .gitignore
GEAENDERT: tests/test_settings_store.py, nrdata/savefile.py,
  tests/test_hostile_savefile.py, docs/berichte/T-100-developer.md
  (Commits 2570d86, 912a39a)
ANNAHMEN: keine offenen - die Schranke, ihr Sicherheitsabstand und der
  Anzeigeweg sind gemessen bzw. am Code nachgelesen, nicht geschaetzt.
NAECHSTER: qa-engineer (SEC-024 nachpruefen), danach director
BLOCKIERT DURCH: nichts
```

## Schritt 1 - der Waechter, der in fremde Worktrees sah

**Vorher rot, gemessen im Hauptarbeitsbaum bei bestehendem Worktree:**

```
.venv/Scripts/python.exe -m pytest tests/test_settings_store.py -q
1 failed, 15 passed in 2.15s
FAILED test_no_source_opens_a_settings_store_of_its_own
AssertionError: ... {'.claude/worktrees/agent-ae1f6543a6c23b08a/nrplanner/app.py': [933, 937]}
```

Genau der im Auftrag beschriebene Fehlschlag: die Fundstelle ist die Kopie von
`app.py` in der Arbeitskopie eines anderen Laufs, an einem Commit vor der
Behebung dieser beiden Zeilen.

**Behebung:** `.claude` steht jetzt in `NOT_OURS` von
`tests/test_settings_store.py` - der Ordner traegt keinen Quelltext dieses
Programms, sondern Agentengedaechtnis und Worktrees. Dazu ein Absatz im
Modulkopf, der sagt, warum.

**Nachher gruen:** `17 passed in 1.56s` (15 alte + der reparierte + der neue
Fall).

**Neuer Fall mit Zaehnen:**
`tests/test_settings_store.py::test_the_walk_reads_our_own_tree_and_not_a_worktree_inside_it`
baut in `tmp_path` zweimal dieselbe Datei `nrplanner/app.py`, einmal im Baum
und einmal unter `.claude/worktrees/agent-1/`, inhaltlich identisch. Der Fall
kann also nur an der Lage entscheiden und ist rot, sobald `.claude` aus
`NOT_OURS` verschwindet - auch auf einer Maschine ohne Worktree.

### Suche nach demselben Fehler in weiteren Waechtern (drei Masken)

| Maske | Suche | Treffer |
|---|---|---|
| 1 | `os.walk` in allen `*.py` ausserhalb `.venv`/`.claude` | **1** (`tests/test_settings_store.py:71`) |
| 2 | `rglob` / `.glob(` / `iterdir` in `tests scripts nrplanner nrdata run.py` | **8**, davon 4 in `tests/` |
| 3 | `parents[1]` bzw. `REPO` in `tests/` (welcher Test hat die Wurzel ueberhaupt in der Hand) | **13 Zeilen in 6 Dateien** |

Ergebnis: **genau ein** Waechter suchte vom Repo-Wurzelverzeichnis aus, und das
war dieser. Die anderen Baumsucher sind enger gefasst und koennen einen
Worktree nicht sehen: `tests/test_one_build.py:48` sucht `REPO/"nrplanner"`,
`tests/test_one_name_per_figure.py:34` denselben Ordner,
`tests/test_advisor_explain.py:1490` nur das Advisor-Paket,
`tests/test_one_build.py:447` ein `tmp_path`. `tests/test_differential_track.py`
haelt `ROOT` nur fuer einzelne Dateipfade, nicht fuer eine Suche.

## Schritt 2 - SEC-024

### Die Schranke, mit Rezept

```python
MIN_BYTES_PER_LOADOUT_TABLE = MAX_HEROES * LOADOUT_GROUP     # 16 * 120 = 1920
allowed_starts = max(1, len(slot_data) // MIN_BYTES_PER_LOADOUT_TABLE)
```

**Herleitung, nicht geraten:** die breiteste Tabelle, die dieser Leser
ueberhaupt liest, sind `MAX_HEROES` Gruppen der Breite `LOADOUT_GROUP`, also
16 x 120 = 1 920 Bytes. Eine Tabelle je 1 920 Bytes Slot ist damit bereits
Schulter an Schulter, und ein Character-Slot traegt **eine** Tabelle A.

**Sicherheitsabstand, am echten Save gemessen (2026-09-07, nur lesend, beide
`.sl2` je 19 531 312 Bytes):**

| Groesse | Wert |
|---|---|
| echter Character-Slot `USER_DATA000` | 1 048 608 Bytes, **1** ausgerichteter `0x0000ff01`-Marker |
| die uebrigen 13 Slots derselben Datei | **0** Marker |
| erlaubt fuer diesen Slot | **546** Starts |
| **Abstand** | **Faktor 546** |
| markergefuellter Slot | 262 144 Starts je MiB, **480-fach** ueber der Schranke |

Der echte Save liest nach der Aenderung unveraendert seine **10 Gruppen**, in
**49,5 ms**.

### Wirkung, gemessen auf dieser Maschine (Windows 10, Python 3.12.10, `.venv`)

Skripte im Scratchpad: `t100_cost.py` (praeparierte Slots), `t100_real.py`
(echter Save, nur lesend).

| Slot | vorher | nachher |
|---|---|---|
| 1 MiB nur `ff01` | 1,028 s | **0,002 s** |
| 1 MiB: eine gueltige Tabelle, Rest `ff01` | 0,955 s, **gelesen** | **0,002 s**, abgewiesen |
| 1 MiB, 16 Markerbaender (teuerste gefundene Form) | 0,967 s | **0,027 s** |
| 19,5 MB nur `ff01` | ~19 s (linear) | **0,033 s** |
| 19,5 MB, 16 Markerbaender | ~19 s (linear) | **0,565 s** |

Die zweite Zeile ist der Kern des Befunds: **ein einziger gueltiger
Reliktdatensatz** genuegt, beide SEC-022-Deckel schweigen, und die Datei wurde
vorher vollstaendig gelesen - inklusive der Sekunde je MiB.

Die letzte Zeile ist der teuerste Fall, den ich unter der neuen Schranke bauen
konnte (16 Baender, jedes Band gerade noch in Reichweite des naechsten, damit
jeder Start 13 Sonden je Gruppe kostet). **0,565 s** liegen unter den rund
**0,67 s**, die derselbe Umfang an ehrlicher Datei allein zum Absuchen kostet
(gemessen: 36 ms je MiB). Der praeparierte Fall kostet damit nicht mehr als der
ehrliche.

### Der Fehlertext im Wortlaut

```
a save slot of 19531312 bytes begins a Nightfarer loadout table at more than
135634 places, denser than one table per 1920 bytes, which is not a save; the
file is damaged or was not written by the game. Take it out of the save folder
and rescan.
```

Englisch (A8), kein Dateipfad, kein `.sl2`, keine Slash- oder
Backslash-Zeichen (SEC-023) - eigener Fall dafuer:
`test_the_refusal_over_packed_table_starts_names_no_file_path`.

### Wo der Satz ankommt - nachgelesen und im Test gefahren

1. `nrplanner/inventory.py:311-314` faengt `(ValueError, struct.error)` aus
   `savefile.read_loadouts` und legt den Satz in `Inventory.loadout_error` ab.
2. `nrplanner/app.py:3426-3430` (`rescan_save`) haengt ihn an die Notiz unter
   dem Save: `… — no stored builds could be read: <Satz>`.
3. `nrplanner/app.py:3488-3491` (`load_equipped`) zeigt ihn beim Oeffnen eines
   Nightfarers: `This save's stored builds could not be read: <Satz>`.
4. Rueckfall: `nrplanner/app.py:3409-3413` faengt zusaetzlich alles, was aus
   `inventory.load` herausfaellt, und schreibt `Save could not be read: …`.

Der Weg wird gefahren, nicht behauptet:
`test_the_refusal_reaches_the_window_instead_of_the_console` baut eine
praeparierte `.sl2` im Temp-Ordner des Tests (**nicht** im Save-Verzeichnis des
Nutzers), laesst sie durch `inventory._scan_save` laufen und prueft, dass die
Inventarliste ihr eine Relikt findet, `loadouts` leer ist und der Satz in
`loadout_error` steht.

**Zu QA-193, praezisiert (nicht behoben):** der fehlende Anzeigeweg betrifft
den **zweiten** SEC-022-Deckel, `Inventory._refuse_a_density_no_save_can_have`
ueber `relics_for` - der laeuft zur Interaktionszeit und liegt ausserhalb des
`try` in `rescan_save`. Der **erste** Deckel (`read_owned_relics`) faellt
dagegen sehr wohl in `app.py:3409` hinein. Beides gehoert in den eigenen
Auftrag; ich habe nichts daran geaendert.

### `should_cancel` in `read_loadouts`? Nein, nicht ohne Umbau

`should_cancel` gibt es ausschliesslich im Berater
(`nrplanner/advisor/{run,search,candidates}.py`). Der Startpfad
`app.rescan_save → inventory.load → _scan_save → read_loadouts` kennt kein
Abbruchsignal - es gaebe keinen Aufrufer, der eines liefern koennte, ohne dass
`load` und `_scan_save` eines durchreichen. Das ist ein Umbau und faellt unter
"nur bauen, wenn es ohne Umbau passt". **Nicht gebaut**, an den `director`
gemeldet.

### Dritte Suchmaske: Eigenschaft statt Fundstelle

`scratchpad/t100_mask3.py`, unabhaengig von den beiden Masken aus T-098
formuliert: **kein Textfund, sondern der Syntaxbaum** - jede `for`-Schleife in
`nrdata/`, `nrplanner/`, `scripts/`, `run.py`, deren Laufbereich aus einer
Laenge gebaut ist (auch ueber einen Namen, dem vorher ein `len(...)` zugewiesen
wurde) und die in ihrem Rumpf eine **zweite** Schleife oder Comprehension
startet.

**6 Treffer in 86 Dateien:**

| Stelle | Bewertung |
|---|---|
| `nrdata/savefile.py:200` (`read_owned_relics`) | von SEC-022 gedeckelt |
| `nrdata/savefile.py:348` (`find_loadout_table`) | **SEC-024, jetzt gedeckelt** |
| `nrplanner/deeptab.py:317` | Schleife ueber `reward["items"]` aus dem Datenabzug, kein Save |
| `nrplanner/deeptab.py:363/415/444` | Schleifen ueber `self.depth_names` (Anzahl Tiefen der Oberflaeche) |

Keine weitere Stelle, in der Bytes aus einer fremden Datei die Zahl der
inneren Durchlaeufe steuern.

**Positivkontrolle der Maske, und sie ist beim ersten Lauf durchgefallen:** die
erste Fassung suchte `len(` im Schleifenkopf und fand `find_loadout_table`
**nicht**, weil dort `limit = len(slot_data)` eine Zeile vorher steht. Erst die
Fassung, die Laengennamen mitfuehrt, findet den Befund, den sie suchen soll (4
Treffer vorher, 6 nachher). Eine Maske, die ihren eigenen Anlassfall nicht
findet, misst sich selbst.

## Die drei Gegenbauten, jeder einzeln

Alle ueber den **Dateinamen** gefahren, nie ueber einen Filter.

**1. Die Schranke entfernen** (`if starts > allowed_starts: raise …` geloescht,
`nrdata/savefile.py`) - `pytest tests/test_hostile_savefile.py -q`:

```
4 failed, 24 passed in 4.60s
FAILED test_a_slot_packed_with_table_starts_is_a_data_error
FAILED test_the_refusal_over_packed_table_starts_names_no_file_path
FAILED test_one_table_start_more_than_the_slot_can_hold_is_a_data_error
FAILED test_the_refusal_reaches_the_window_instead_of_the_console
```

**2. Still kuerzen statt laut ausfallen** (dieselbe Stelle, `raise` durch
`break` ersetzt, also: zurueckgeben, was bis dahin gefunden wurde) - dieselbe
Datei:

```
4 failed, 24 passed in 7.24s
```

dieselben vier Faelle. Wichtig dabei: bei `starts=5` liefert die stille
Fassung die **vollstaendige, echt aussehende Tabelle** zurueck - genau der
Zustand, den der laute Ausfall verhindert.

**3. Die Ausschlusszeile aus Schritt 1 zuruecknehmen** (`.claude` aus
`NOT_OURS`) - zweimal gefahren, weil die Bedingung "nur, wenn ein Worktree
existiert" mitgeprueft gehoert:

* **mit Worktree** (Hauptarbeitsbaum; der Worktree
  `.claude/worktrees/agent-ae1f6543a6c23b08a` lag beim Auftragsbeginn bereits
  da, angelegt vom parallel laufenden Lauf - ich habe **keinen** angelegt und
  **keinen** entfernt, `git worktree list` weist ihn vor und nach meiner
  Arbeit aus):
  `2 failed, 15 passed` - `test_no_source_opens_a_settings_store_of_its_own`
  **und** der neue Fall.
* **ohne Worktree**: `git clone` des Repos nach
  `…/scratchpad/t100_klon` (ein Klon traegt nur versionierte Dateien, und
  `.claude/worktrees/` ist nicht versioniert - im Klon existiert kein
  `.claude`). Dort dieselbe Mutation:
  `1 failed, 16 passed` - **nur** der neue Fall, der Baumscan bleibt gruen.

Damit ist belegt: der alte rote Fall kam vom fremden Worktree und von nichts
sonst, und der neue Fall haengt nicht davon ab, dass zufaellig einer da ist.

Beide Mutationen wurden ueber eine vorher zur Seite kopierte Fassung
zurueckgenommen (`cp datei datei.orig` / zurueck), nie ueber `git checkout`.

## Commits

| Commit | Inhalt |
|---|---|
| `2570d86` | `test(settings): another run's worktree is not our source` |
| `912a39a` | `fix(savefile): a slot may not begin a Nightfarer table everywhere` |

Beide mit Pfadangabe hinter `--` gestaged, kein `-a`, kein `add .`.

## Suite - einmal am Ende, geteilt im Vordergrund

Gemessen auf Stand `912a39a`:

| Teil | Ergebnis |
|---|---|
| `tests/test_relic_picker_advisor.py tests/test_relic_picker_geometry.py` | **48 passed in 176,91 s** |
| Rest mit `--ignore` auf diese beiden | **1208 passed, 9 skipped in 3222,14 s (53:42)** |
| Summe | **1256 passed, 9 skipped, 0 failed** |
| `--collect-only` | 1265 Tests (= 1256 + 9) |

Ausgangszahl selbst gemessen: der eine Fehlschlag aus T-098 war der Waechter
aus Schritt 1 und ist nach Schritt 1 weg (siehe oben). Meine beiden Commits
fuegen **7** Faelle hinzu (1 Waechterfall + 6 SEC-024-Faelle); die Differenz zu
T-098s 1195 erklaert sich zusaetzlich aus Commits, die zwischen jenem Lauf und
diesem gelandet sind - ich habe die Zwischenstaende nicht nachgemessen und
behaupte darueber nichts.

Zwischenlaeufe waehrend der Arbeit: nur die beruehrten Dateien
(`tests/test_settings_store.py`, `tests/test_hostile_savefile.py`, sowie
`tests/test_loadout_table.py tests/test_relic_ownership.py
tests/test_relic_restore.py tests/test_custom_relic.py
tests/test_hostile_gamedata.py` zusammen: **94 passed in 92,05 s**).

**Zur Laufzeit:** der zweite Teil brauchte 53:42 statt der im Auftrag
genannten rund 14 Minuten. Waehrend des Laufs arbeitete der parallele Lauf im
eigenen Worktree auf derselben Maschine (er hat waehrenddessen auch seinen
Stand von `11f0d97` auf `313f372` bewegt). Die Zahl ist als Regressionsmessung
belastbar (0 failed), als **Zeitmessung nicht** - sie sagt etwas ueber die
Maschinenlast, nicht ueber die Suite.

**Waehrend meines Laufs ist `97b8837` (`docs(qa): QA-195 bis QA-197 aus dem
xdist-Probelauf`) auf dem Branch gelandet**, also nach meinem zweiten Commit.
Reine Dokumentation, kein Code - die Suite-Zahl bleibt fuer `912a39a` gueltig.

## DoD

- [x] Anforderung verstanden, Annahmen dokumentiert
- [x] Build und Tests gruen in der benannten Umgebung (Windows 10,
      Python 3.12.10 aus `.venv`, PySide6, `QT_QPA_PLATFORM=offscreen`)
- [x] Neue Tests fuer neue Logik (7 Faelle), jeder mit belegter roter Phase
- [ ] Linter: **entfaellt**, das Projekt hat keinen konfiguriert
      (`pytest.ini` ist die einzige Werkzeugkonfiguration)
- [x] Keine Secrets, keine TODOs, kein toter Code
- [x] Save nur gelesen, keine `.sl2` im Save-Verzeichnis des Nutzers, kein
      Fenster gestartet, keine Bildschirmabzuege (NH-002), kein Netzzugriff
- [x] Fremder Worktree unangetastet, nur ausgeschlossen
- [x] Bericht geschrieben

Nicht geprueft: andere Plattformen als Windows 10 (macOS, Linux) - die
Aenderung ist plattformunabhaengiger Python-Code ohne Pfad- oder
Qt-Abhaengigkeit, aber gefahren wurde sie nur hier.

## An den qa-engineer

* **SEC-024 nachpruefen:** `tests/test_hostile_savefile.py`, Abschnitt
  SEC-024. Interessante Kanten: ein Slot mit *genau* `allowed_starts` Starts
  (muss lesen), einer mit einem mehr (muss abweisen), ein Slot kleiner als
  1 920 Bytes (`max(1, …)` erlaubt dort genau einen Start - ein echter
  Character-Slot ist 1 MiB gross, aber die Kante existiert), und ein Save
  **ohne DLC** (weniger als zehn Gruppen, schmalere Gruppen) - dafuer habe ich
  keinen echten Beleg, nur die Regel, dass die Schranke Starts zaehlt und
  nicht Gruppenbreiten.
* **Der Anzeigeweg** ist bis `Inventory.loadout_error` und bis in beide
  Label-Stellen nachgelesen und bis `loadout_error` auch gefahren; **nicht**
  gefahren habe ich das Fenster selbst (der Nutzer hat eine Programmkopie
  offen, kein Fenster gestartet). Der Satz ist lang - wie er in der Notiz
  unter dem Save umbricht, hat niemand gesehen.
* Vor dieser Aenderung gab es **keinen einzigen** Test, der `loadout_error`
  ueberhaupt erwaehnt (Volltextsuche in `tests/`: 0 Treffer). Der Pfad "Save
  liest Relikte, aber keine Builds" war unbelegt.

## An den director

1. **`.claude/worktrees/` steht nicht in `.gitignore`** - nur
   `.claude/agent-memory/`. Aktuell liegen dort **55** unversionierte
   `.py`-Dateien eines fremden Laufs. Ein einziges `git add .` committet die
   Arbeitskopie eines anderen Laufs in dieses **oeffentliche** Repo. Risiko
   mittel, Aufwand eine Zeile - gehoert dem `archivist` oder einem eigenen
   Auftrag, ich habe `.gitignore` nicht angefasst.
2. **QA-193 praezisiert** (siehe oben): der fehlende Anzeigeweg betrifft nur
   den zweiten SEC-022-Deckel (`relics_for` zur Interaktionszeit). Der erste
   faellt in `app.py:3409`. Der Auftragstext dort koennte das schaerfer fassen.
3. **`should_cancel` in `read_loadouts`: nicht gebaut**, Begruendung oben. Wenn
   der Startscan abbrechbar werden soll, ist das ein eigener Auftrag ueber
   `inventory.load` / `_scan_save`.
4. **Restrisiko SEC-024, ehrlich beziffert:** die Schranke ist relativ, also
   waechst der Aufwand des teuersten praeparierten Falls linear mit der Datei -
   0,565 s bei 19,5 MB. Das liegt unter den Kosten einer ehrlichen Datei
   gleicher Groesse, aber es ist kein konstanter Deckel. Eine Datei von
   200 MB kaeme auf rund 6 s; ob der Leser zusaetzlich eine absolute
   Obergrenze fuer die Slotgroesse braucht, ist eine eigene Entscheidung
   (beruehrt auch SEC-022, dort gilt dasselbe).
5. **Zeitmessung der Suite unbrauchbar bei paralleler Last** (53:42 statt
   ~14 min, 0 failed). Fuer die laufende Parallelisierung relevant: die
   Regressionsaussage haelt, die Laufzeitaussage nicht.
6. **Performance:** nichts getunt. `find_loadout_table` bleibt ein
   Volldurchlauf ueber den Slot (36 ms je MiB, 14 Slots je Datei) - das ist
   die ehrliche Grundlast beim Start und faellt in die Zustaendigkeit des
   `performance-tuner`, falls sie jemandem auffaellt.

## An den ui-ux-designer

Keine Abweichung. Der neue Satz erscheint an den beiden Stellen, an denen
`loadout_error` schon vorher erschien, im selben Stil wie die
SEC-022-Meldung (Englisch, kein Pfad, endet mit der Handlungsanweisung
"Take it out of the save folder and rescan.").
