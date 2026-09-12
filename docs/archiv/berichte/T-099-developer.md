# T-099 - Probelauf: haelt die Suite parallel? (developer)

```
STATUS: teilweise
AUFTRAG: T-099 - Probelauf: haelt die Suite parallel?
GELESEN: docs/tasks/T-099.md (aus dem Hauptarbeitsbaum, siehe ANNAHMEN),
  tests/conftest.py, pytest.ini, requirements.txt, requirements-dev.txt,
  NightreignHelper.spec, .github/workflows/tests.yml, run.py,
  tests/test_build_names.py, tests/test_advisor_hold.py,
  tests/test_settings_store.py, tests/test_advisor_bar.py,
  tests/test_advisor_worker.py, tests/test_extraction.py (alle am Stand
  f79f770)
GEAENDERT: docs/berichte/T-099-developer.md (in meinem Worktree, Zweig
  worktree-agent-ae1f6543a6c23b08a). Sonst nichts im Repository. Die
  Messungen liefen in einem Wegwerf-Klon im Scratchpad.
ANNAHMEN: (1) Mein Worktree steht auf fa2de4c vom 01.09.2026 und enthaelt
  weder `tests/` noch `pytest.ini` noch `requirements-dev.txt` (mit zwei
  unabhaengigen Suchen belegt, siehe unten). Der Auftrag liegt dort ebenfalls
  nicht; ich habe `docs/tasks/T-099.md` lesend aus dem Hauptarbeitsbaum
  genommen. Gemessen habe ich deshalb gegen einen Klon, den ich mit
  `git clone --revision=f79f770...` auf den Stand der Zweigspitze
  festgenagelt habe, die beim Auftragsbeginn galt.
  (2) "sinnvolle Zahl fuer diesen Rechner" habe ich als 4 gelesen, wie im
  Auftrag vorgeschlagen; `os.cpu_count()` ist 16, `-n auto` startet 16 Worker.
NAECHSTER: director
BLOCKIERT DURCH: die eine Zeile in `requirements-dev.txt` konnte ich nicht
  setzen - die Datei existiert am Stand meines Worktrees nicht (sie kam erst
  nach dem 01.09. dazu). Sie in einem sechs Tage alten Baum neu anzulegen
  wuerde beim Zusammenfuehren einen add/add-Konflikt gegen die echte Datei
  erzeugen. Der genaue Einzeiler steht unter Punkt 3; er gehoert auf den
  Zweig `docs/audit-and-advisor-design`, nicht hierher.
```

## Urteil in einem Satz

**Einfuehren** - `-n auto` drueckt die Suite auf ein Siebtel statt auf ein
Drittel, kein einziger Fall aendert dabei sein Urteil, und die Stelle, an der
es haette schiefgehen koennen, ist im Projekt bereits abgesichert; die
Bedingung ist, dass `-n` an `-m "not slow"` gekoppelt bleibt oder mit
`--dist loadfile` gefahren wird (Begruendung unter "Was daneben auffiel", 3.).

## Punkt 1 - die sechs Messungen

Alle sechs auf demselben Stand **f79f770c511f69447c1e08c9193cf7bd3df8bdee**,
alle im Vordergrund, alle mit `-m "not slow" -q --junitxml=...`.

| Lauf | Konfiguration | Wanduhr | pytest-Zeit | Ergebnis |
|---|---|---|---|---|
| seriell-1 | ohne xdist auf dem Pfad | 1118,38 s | 1100,03 s | 1244 passed, 9 skipped, 5 deselected |
| seriell-2 | ohne xdist auf dem Pfad | 989,55 s | 973,98 s | 1244 passed, 9 skipped, 5 deselected |
| auto-1 | `-n auto` = 16 Worker | 152,37 s | 151,46 s | 1244 passed, 9 skipped |
| auto-2 | `-n auto` = 16 Worker | 148 s | 147,75 s | 1244 passed, 9 skipped |
| n4-1 | `-n 4` | 278,75 s | 278,13 s | 1244 passed, 9 skipped |
| n4-2 | `-n 4` | 302 s | 300,92 s | 1244 passed, 9 skipped |

**Das Rezept zu den Zahlen.**

- Kernzahl: `os.cpu_count()` = **16**. `-n auto` meldet im Kopf woertlich
  `created: 16/16 workers` - nachgesehen, nicht angenommen.
- Werkzeuge: Python 3.12.10, pytest 9.1.1, PySide6 6.11.1, pytest-xdist
  **3.8.0**, execnet **2.1.2**, beide **MIT** (aus den `METADATA` der
  installierten Pakete gelesen).
- Wanduhr = Zeit um den `subprocess`-Aufruf herum, pytest-Zeit = die Zahl aus
  der Zusammenfassungszeile. Die Differenz ist der Prozessstart.
- **Cache:** kein Lauf lief auf kaltem Cache. Vor seriell-1 lief ein
  `--collect-only` (2,57 s), das den Baum bereits angefasst hatte; danach lief
  jede Konfiguration zweimal. Warm ist hier die schlechtere Bedingung fuer die
  parallele Seite, nicht fuer die serielle: sie nimmt dem ersten Lauf den
  Nachteil, nicht dem sechsten.
- **Streuung ueber die zwei Laeufe** (pytest-Zeit): seriell 1100,03 / 973,98,
  Spanne **126,05 s** = 12,2 % des Mittels; `-n auto` 151,46 / 147,75, Spanne
  **3,71 s** = 2,5 %; `-n 4` 278,13 / 300,92, Spanne **22,79 s** = 7,9 %.
- **Beschleunigung** aus den Mittelwerten (1037,01 s seriell): `-n auto`
  149,61 s → **Faktor 6,93**; `-n 4` 289,53 s → **Faktor 3,58**.
- **Und die Einschraenkung, ohne die diese Zahlen falsch gelesen werden:** die
  Absolutwerte liegen weit ueber den 737,87 s des Ausgangsstands, weil
  waehrend der Messung zwei weitere Laeufe auf derselben Maschine rechneten
  (T-098 und T-100). Belegt: waehrend seriell-1 hielt ein fremder
  Python-Prozess rund **9 GB** Arbeitsspeicher, und kurz darauf hatte ein
  weiterer in 462 s Laufzeit **391 s CPU** verbrannt - nachgesehen ueber
  `tasklist` und `GetProcessTimes`, nicht geschaetzt. Die Absolutzahlen sind
  deshalb **nicht** mit
  den 737,87 s vergleichbar. Das Verhaeltnis ist es, weil alle sechs Laeufe
  unter derselben Fremdlast standen - und es ist eher zu niedrig als zu hoch,
  denn Fremdlast trifft 16 Worker haerter als einen.
- seriell-2 (973,98 s) ist der ehrlichste serielle Wert: er lief, als die
  Fremdlast bereits abgeklungen war.

**Was bei den letzten beiden Laeufen schiefging und wie es geheilt wurde.**
Der urspruengliche Stapellauf verlor die Laeufe 5 und 6: um 19:25 Uhr war das
Verzeichnis meines Messklons bis auf `.pytest_cache` **leer**, waehrend der
Stapel noch lief. seriell-2 (19:25) ging gerade noch durch, auto-2 und n4-2
sammelten danach null Faelle ein (`no tests ran`, rc=5). Geloescht hat das
nicht mein Lauf - der Scratchpad ist zwischen den gleichzeitig laufenden
Rollen geteilt, und dort lagen zur selben Zeit Dateien eines T-100-Laufs
(19:20 bis 19:22). Ich habe neu geklont, diesmal auf `--revision=f79f770`
festgenagelt, und auto-2 und n4-2 einzeln im Vordergrund wiederholt. Das ist
derselbe Stand wie die ersten vier Laeufe; die Zweigspitze war inzwischen auf
2570d861 weitergewandert, was ich bewusst **nicht** mitgemessen habe.

## Die zweite Stichprobe: die Namen, nicht die Summe

`--junitxml` je Lauf, danach Mengenvergleich der 1253 Fall-Namen
(`classname::name`) gegen seriell-1:

| Lauf | Faelle | nur hier | fehlt gegen seriell-1 | Urteilswechsel |
|---|---|---|---|---|
| auto-1 | 1253 | 0 | 0 | 0 |
| n4-1 | 1253 | 0 | 0 | 0 |
| seriell-2 | 1253 | 0 | 0 | 0 |
| auto-2 | 1253 | 0 | 0 | 0 |
| n4-2 | 1253 | 0 | 0 | 0 |

**Dieselbe Menge, dieselben Urteile, dieselben 9 Uebersprungenen** - es sind
in jedem Lauf die neun `test_tab_geometry`-Faelle `[833]`, und sogar mit
demselben Grund: "this platform will not give the window 833 logical px: it
is 988 px wide". Seriell wie parallel dieselbe Zeile; die offscreen-Plattform
verhaelt sich in jedem Worker gleich.

**Gegenprobe zu diesem Vergleich** (sonst haette ich mein Pruefmittel
gemessen, nicht die Sache): aus `n4-2.xml` einen Fall entfernt und bei einem
zweiten das Urteil gedreht, denselben Vergleich noch einmal - er meldet genau
den entfernten Fall und genau den gedrehten. Der Vergleich schlaegt also an,
wenn es etwas zu melden gibt.

## Punkt 2 - wird ein Test dabei falsch?

### Der Registrierungsschluessel - zuerst gesucht, und er ist schreibend

**Ja, schreibend.** `tests/conftest.py:229-236` (`clear_settings`) ruft
`QSettings(favourites.ORG, favourites.APP).clear()` und `.sync()`, die
`settings_store`-Sitzungsfixtur ruft das am Anfang und am Ende jedes Laufs,
und `test_build_names.py` baut sich den Store an **8** Stellen selbst
(`QSettings(favourites.ORG, favourites.APP)`, nachgezaehlt). Der
Zweig ist `HKCU\Software\<ORG>\<APP>` und damit maschinenweit geteilt.

**Er ist bereits abgesichert, und die Absicherung traegt.**
`tests/conftest.py:45` setzt `NIGHTREIGN_SETTINGS_APP` auf
`NightreignHelperTests-{os.getpid()}` - eine *Zuweisung*, keine
`setdefault`-Zeile wie eine Zeile darueber. Das ist der Unterschied, an dem
alles haengt: die Worker erben die Umgebung des Steuerprozesses, und ein
`setdefault` haette allen Workern den Schluessel des Steuerprozesses gegeben.

Direkt gemessen, nicht hergeleitet - zwoelf Wegwerf-Faelle unter `-n 4`, jeder
schreibt heraus, in welchem Prozess er lief:

```
3x pid=13652 app=NightreignHelperTests-13652 qapplication=1314969962176 platform=offscreen
4x pid=14756 app=NightreignHelperTests-14756 qapplication=2039804437952 platform=offscreen
2x pid=17028 app=NightreignHelperTests-17028 qapplication=1722425165376 platform=offscreen
3x pid=23480 app=NightreignHelperTests-23480 qapplication=3000522589824 platform=offscreen
```

Vier Worker, vier Prozesse, **vier verschiedene Schluessel**, vier
verschiedene QApplication-Objekte.

**Und die rote Phase, ohne die das nichts belegt.** `tests/conftest.py:45` im
Klon auf einen festen Namen ohne Prozessnummer gesetzt und dieselben drei
Settings-Dateien noch einmal unter `-n 4` gefahren:

| Zustand von conftest.py:45 | `-n 4` ueber test_build_names, test_advisor_hold, test_settings_store |
|---|---|
| `NightreignHelperTests-{os.getpid()}` (wie im Baum) | **92 passed** in 29,95 s |
| `NightreignHelperTests-T099shared` (fest) | **15 failed**, 77 passed in 27,45 s |

Die Mutation wurde ueber eine vorher angelegte Kopie zurueckgenommen
(`cp tests/conftest.py tests/conftest.py.orig`, danach zurueckkopiert), nicht
ueber git; `git status` im Klon ist danach leer.

Das heisst: die gefaehrlichste Stelle des Auftrags ist scharf, sie war schon
vor diesem Auftrag zugedreht (der Kommentar dort nennt QA-043), und die
Zudrehung ist nachweislich das, was `-n` traegt. Wer diese Zeile je anfasst,
zerlegt den parallelen Lauf - das gehoert in den Kommentar der Zeile, steht
aber schon sinngemaess da.

**Was liegen bleibt:** nach jedem der drei einzeln vermessenen Laeufe
(seriell-1, auto-1, n4-1) hielt `HKCU\Software\DankYeeterTests` **genau
null** neue Unterschluessel - auch nach dem 16-Worker-Lauf nicht. Die
Fixtur raeumt am Sitzungsende, und ein leerer Schluessel wird von Qt beim
`sync()` entfernt. Auch `NightreignHelperTests-T099shared` aus dem
Mutationslauf ist nicht liegengeblieben.

### Qt

`QT_QPA_PLATFORM=offscreen` steht in jedem Worker (siehe Messung oben), und
je Worker gibt es **genau eine** QApplication: die Wegwerf-Faelle prueften
`QApplication.instance() is qapp` und die vier Identitaeten unterscheiden
sich. Zusaetzlich: die neun `[833]`-Faelle ueberspringen seriell und parallel
mit derselben Begruendung und derselben gemessenen Breite (988 px) - haette
ein Worker eine andere Plattform oder einen anderen Stil erwischt, waere genau
das die Zeile gewesen, die sich unterscheidet. Die Annahme haelt.

### Datenabzug und echter Spielstand

Belegt statt angenommen, ueber einen Zustandsabzug vor dem ersten und nach dem
letzten Lauf (`st_mtime_ns` und Groesse, plus die Zeitstempel der
Registrierungsschluessel):

| | vorher = nachher? |
|---|---|
| `%LOCALAPPDATA%\NightreignHelper\nightreign_data.json` (8.484.651 Byte) | **ja**, Zeitstempel unveraendert |
| `...\Roaming\Nightreign\76561198073567627\NR0000.sl2` | **ja**, Zeitstempel und Groesse unveraendert |
| `...\Roaming\Nightreign\76561198179244962\NR0000.sl2` | **ja**, Zeitstempel und Groesse unveraendert |
| `HKCU\Software\DankYeeter` (der Schluessel des Spielers) | **ja**, `last_write` unveraendert |

Dazu die statische Seite mit zwei unabhaengigen Masken: in `nrdata/` und
`nrplanner/` gibt es genau zwei schreibende Stellen (`extract.write_snapshot`
und `iconbuild`), und keine davon wird von einem Test gerufen; jede
schreibende Stelle in `tests/` zielt auf `tmp_path` - **7** Fundstellen in 4
Dateien, einzeln nachgesehen und alle auf einen aus `tmp_path` abgeleiteten
Pfad.

### Faelle, die seriell gruen und parallel rot waeren

**Keine.** Vier parallele Laeufe (2x16 Worker, 2x4 Worker) ueber 1253 Faelle,
kein einziger Fehlschlag, kein Urteilswechsel.

### Faelle, die parallel gruen und seriell rot waeren - der gefaehrlichere Fall

**Keine gefunden**, und das ist hier kein Nichts: beide seriellen Laeufe waren
ebenfalls vollstaendig gruen und decken dieselbe Namensmenge ab. Ein Fall, der
nur parallel gruen ist, muesste seriell rot sein - er war es nicht.

**Was ich trotzdem melde, weil es die naechste Rolle braucht:** drei Faelle
messen echte Wanduhr und sind damit lastabhaengig, nicht parallelitaets-fest
per Konstruktion.

| Ort | Schranke | was sie misst |
|---|---|---|
| `tests/test_advisor_bar.py:702` | `elapsed_ms < 200` | AK 4.5: der zweite Klick meldet `Stopped` |
| `tests/test_advisor_worker.py:255` | `visible < 0.2` | AK-11: das Fenster erfaehrt vom Abbruch |
| `tests/test_advisor_worker.py:382` | `burst < 0.1` | Eigenpruefung: fuenf Fragen muessen in ein 100-ms-Fenster passen |

Alle drei hielten in vier parallelen Laeufen, davon zwei mit 16 Workern auf 16
Kernen **und** Fremdlast von zwei anderen Rollen - das ist die haertere
Bedingung, nicht die weichere. Sie bleiben die Kandidaten, die auf einer
langsameren Maschine oder in CI unter `-n` zuerst flackern wuerden. Die dritte
ist dabei die harmloseste Art von Rot: sie sagt "diese Messung ist ungueltig"
und nicht "das Programm ist kaputt".

## Punkt 3 - landet es im Artefakt?

Nein, und zwar mit Primaerquelle statt mit Annahme:

1. **Volltext, zwei unabhaengige Masken, ganzes Repo:** `xdist` findet **5**
   Treffer, alle in `vendor/Paramdex/.../*.xml` und alle Teil von
   Feldnamen wie `NearMaxDist`. `execnet` findet **0 Treffer**. Kein Treffer
   in `NightreignHelper.spec`, in `requirements*.txt` oder im Quelltext.
2. **`NightreignHelper.spec` selbst:** `Analysis(['run.py'])`, `excludes=[]`,
   `hiddenimports` nennt genau vier `nrdata`-Module. Der Bau folgt also dem
   Importgraph von `run.py`.
3. **Der Importgraph, gemessen mit xdist absichtlich auf dem Pfad** - sonst
   haette ich bewiesen, dass ein nicht installiertes Paket nicht importiert
   wird, was nichts heisst:

   ```
   xdist reachable on sys.path: True
   after importing the shipped entry point: []
   positive control, after importing xdist by hand: ['pytest', 'xdist', 'xdist._version', 'xdist.plugin']
   ```

   Importiert wurden `run` und alle vier `hiddenimports`. Die Pruefung sieht
   xdist, wenn es da ist - nach dem Auslieferungs-Einstiegspunkt ist es nicht
   da.
4. **Kein Modul unter `nrplanner/` oder `nrdata/` importiert pytest**
   (Volltext, 0 Treffer). Ohne pytest kein xdist.

**Der Eintrag, den ich nicht setzen konnte.** Mein Urteil ist positiv, also
gehoert in `requirements-dev.txt` unter die Zeile `pytest==9.1.1`:

```
pytest-xdist==3.8.0
```

`execnet==2.1.2` braucht keine eigene Zeile, es kommt als Abhaengigkeit mit.
**Nicht** in `requirements.txt` - dort steht nur das Ausgelieferte. Warum ich
die Zeile nicht selbst gesetzt habe, steht oben unter BLOCKIERT DURCH.

**Ein Hinweis zur Waechter-Zeile in `.github/workflows/tests.yml`:** sie
prueft `grep -iq '^pytest' requirements.txt`. Eine Zeile `pytest-xdist=...`
in `requirements.txt` faellt darunter, wird also gefangen. Eine Zeile
`execnet==...` **nicht** - der Waechter ist auf den Namen `pytest*` gebaut,
nicht auf "Testwerkzeug". Das ist heute folgenlos (execnet kaeme nur
transitiv), aber es ist die Luecke, die er hat.

## Lizenz und Version fuer die Akte

`pytest-xdist 3.8.0` - MIT. `execnet 2.1.2` - MIT. Beide aus dem
`License-Expression`-Feld der installierten `METADATA` gelesen.

## Wie ich die gemeinsame Umgebung nicht angefasst habe

`pip install --target <scratchpad>/xdistlib --no-deps pytest-xdist execnet`,
eingehaengt ueber `PYTHONPATH` und **nur** fuer die parallelen Laeufe. Danach
nachgesehen: `pip list` der gemeinsamen `.venv` kennt weder `xdist` noch
`execnet`. Die seriellen Laeufe liefen ohne `PYTHONPATH`, also mit gar keinem
xdist auf dem Pfad - das ist genau der Lauf, den das Projekt heute hat.

## Was daneben auffiel und nicht in den Auftrag gehoerte

1. **Ein Testschluessel unter der Organisation des Spielers.**
   `HKCU\Software\DankYeeter` haelt neben `NightreignHelper` einen
   Unterschluessel **`NightreignHelperTests`**. Das ist genau die Klasse der
   drei Datenverluste: irgendwann hat ein Lauf Testeinstellungen unter die
   echte Organisation geschrieben, nicht unter `DankYeeterTests`. Kein Lauf
   von mir hat ihn angefasst (`last_write` unveraendert). Aufwand fuer den
   Blick hinein: Minuten. Ich habe ihn nicht geloescht - das ist eine
   Entscheidung des Directors, und was drin steht, weiss ich nicht.
2. **141 verwaiste Unterschluessel unter `HKCU\Software\DankYeeterTests`** mit
   Namen wie `T060seed-4400`, `NightreignHelperProbe-10688`,
   `NightreignHelperDifferential-*`. Die Suite ist es nicht - sie legt null
   an. Es sind Messkripte frueherer Auftraege, die den Store nicht geraeumt
   haben. Harmlos, aber es waechst.
3. **`-n` sollte an `-m "not slow"` gekoppelt bleiben, oder an
   `--dist loadfile`.** Der einzige Nutzer der Fixtur `extracted_game_data`
   ist `tests/test_extraction.py`, komplett `slow`, fuenf Faelle, und die
   Fixtur kostet rund 40 s Auszug **je Prozess**. Unter der Voreinstellung
   `--dist load` koennen die fuenf Faelle auf fuenf Worker fallen: aus einem
   Auszug werden fuenf. `--dist loadfile` haelt eine Datei auf einem Worker
   und macht daraus wieder einen.
4. **Der Scratchpad ist zwischen gleichzeitig laufenden Rollen geteilt**, und
   er wird von ihnen aufgeraeumt. Mein Messbaum wurde mitten im Stapellauf
   geleert (siehe Punkt 1). Solange `isolation: "worktree"` nur den
   Arbeitsbaum trennt und nicht das Temp-Verzeichnis, ist jede lange Messung
   angreifbar. Ein Verzeichnisname mit Auftragsnummer haette es nicht
   verhindert, aber sichtbar gemacht, wem er gehoert.
5. **Mein Worktree stand auf einem Stand vom 01.09.2026** (fa2de4c, 313
   Dateien, kein `tests/`, kein `pytest.ini`, kein `requirements-dev.txt`,
   kein `docs/tasks/`). Mit zwei Suchen belegt: `git ls-tree -r --name-only
   HEAD` findet unter `requirements|pytest|^tests/` genau `requirements.txt`,
   und `git grep -li pytest HEAD` findet nur meinen eigenen Bericht. Ein
   Auftrag, der im eigenen Worktree gemessen werden soll, braucht einen
   Worktree auf dem Stand des Auftrags - sonst wird daraus ein Klon, und der
   Unterschied faellt erst auf, wenn man ihn sucht.

## Definition of Done

- [x] Anforderung verstanden, Annahmen dokumentiert
- [x] Sechs Laeufe gemessen, je Konfiguration zwei, alle auf f79f770
- [x] Namensvergleich statt Summenvergleich, mit Gegenprobe
- [x] Die drei Risikostellen gemessen, die gefaehrlichste mit roter Phase
- [x] Punkt 3 mit Primaerquelle und Positivkontrolle
- [ ] **Offen:** die Zeile in `requirements-dev.txt` (siehe BLOCKIERT DURCH)
- [x] Keine Aenderung an `requirements.txt`, kein Testumbau, kein
      `-p no:randomly`, keine Marker-Kosmetik
- [x] Keine Abhaengigkeit in der gemeinsamen `.venv`; nachgesehen
- [x] Kein Fenster gestartet, keine Bildschirmabzuege
- Linter: das Projekt hat keinen konfiguriert - Punkt entfaellt
- **Ungeprueft:** Linux und macOS (das Projekt ist Windows-only), sowie das
  Verhalten unter `-n` in CI (`windows-latest`, andere Kernzahl, andere
  Lastlage). Die drei Wanduhr-Schranken oben sind dort das Risiko.
