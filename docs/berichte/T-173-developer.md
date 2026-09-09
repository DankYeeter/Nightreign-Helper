STATUS: erledigt
AUFTRAG: T-173 - Die Auflage bekommt einen Mechanismus (developer)
GELESEN: docs/tasks/T-173.md, docs/debug/D-001.md, tests/conftest.py,
tests/test_extraction.py, .github/workflows/tests.yml, pytest.ini,
nrplanner/paths.py, nrplanner/favourites.py, nrplanner/shortcut.py,
git log/show a1172fb (T-171-Fix)
GEÄNDERT: tests/conftest.py, tests/test_extraction.py (committet als
adaab13, Pfad hinter `--`)
ANNAHMEN: siehe unten unter "Prüfung der Begründung" und "Abweichung"
NÄCHSTER: qa-engineer (Retest QA-220)
BLOCKIERT DURCH: nichts

## Prüfung der Begründung, wie im Auftrag verlangt

Vor dem Bauen geprüft: `extracted_game_data` (tests/conftest.py:172-189)
baute schon **vor** diesem Auftrag immer frisch über `extract.build()` -
anders als `game_data` hat sie nie `_snapshot_from_env`/`_snapshot_from_cache`
konsultiert. `nrdata/extract.py` hat keinerlei eigene Cache-Logik, die das
unterlaufen könnte (geprüft: kein Treffer auf `snapshot_path` oder
`EXTRACT_VERSION`-Vergleich innerhalb von `extract.build`). Volltextsuche
`extracted_game_data` im ganzen `tests/`-Baum: **zwei** Treffer, `conftest.py`
und `test_extraction.py` - keine dritte Stelle hängt an ihrer Gestalt. Die
Begründung aus dem Auftrag ("Rundlauf-Test deckt die JSON-Gestalt") trägt
also, und kein anderer Test bezieht die gelesene Gestalt nur über diese
Fixture.

**Damit gab es nichts an der Fixture selbst zu ändern** - der Mechanismus war
schon richtig, nur ungeschützt: nichts hätte eine künftige "schneller
machen"-Änderung verhindert, die ihr denselben Snapshot-Vorrang gibt wie
`game_data` direkt daneben (ein naheliegendes Vorbild). Seit D-001s Fix
(Commit `a1172fb`, T-171) tragen Snapshot und Frischbau dieselbe Gestalt, die
sechs bestehenden Fälle in `test_extraction.py` hätten einen solchen Rückbau
also **nicht mehr bemerkt** - genau die Lücke, die der Auftrag mit einem
Wächter schließen lässt.

## Umgesetzt

**Neuer Wächter** `test_extracted_game_data_never_falls_back_to_a_cached_snapshot`
in `tests/test_extraction.py` (Zeile ~151). Legt einen Snapshot an, den jeder
bekannte Fallback-Pfad (`NIGHTREIGN_TEST_SNAPSHOT`-Env und Programm-Cache über
`paths.snapshot_path`) annehmen würde, ersetzt `extract.build` durch einen
Spion und ruft die rohe Fixture-Funktion direkt auf
(`conftest.extracted_game_data.__wrapped__`, umgeht `installed_game`s Skip).
Läuft deshalb **auch ohne installiertes Spiel** und damit auch in der CI -
stärker als vom Auftrag verlangt, aber ohne die CI-Datei anzufassen oder ihr
Verhalten zu ändern (sie führt jetzt einen zusätzlichen, für sie neuen,
schnellen Test aus statt ihn zu überspringen).

**`pytestmark = pytest.mark.slow`** (Modulebene) durch `@pytest.mark.slow` je
der sechs bestehenden Fälle ersetzt. Grund: der neue Wächter braucht kein
Spiel; ein Blanket-Mark hätte ihn über `pytest -m "not slow"` genauso
ausgeblendet wie die Konstellation, die QA-220 gefunden hat - dieselbe Falle
unter neuem Namen.

**Kleine Doku-Ergänzung** im Docstring von `extracted_game_data`
(`tests/conftest.py:172`): hält fest, warum die Fixture absichtlich keinen
Fallback hat und welcher Test das bewacht - für die nächste Person, die dort
"optimiert".

Keine Änderung an `nrdata/`, `nrplanner/`, `.github/workflows/`, `pytest.ini`
oder sonst etwas außerhalb der Whitelist.

## Mutationsbeweis (voll, wie verlangt)

Datei vor der Mutation gesichert (`cp`, nicht `git checkout`), zwei Mutationen
einzeln eingebaut und wieder zurückkopiert:

1. `return _snapshot_from_cache() or extract.build(game, defs)` → Wächter rot:
   `AssertionError: extracted_game_data did not call extract.build with the
   installed game -- it must have read a snapshot instead`
2. `return _snapshot_from_env() or extract.build(game, defs)` → derselbe
   Fehler, Wächter rot.

Danach `tests/conftest.py` aus der Sicherung zurückkopiert, `git diff` danach
zeigte nur die beabsichtigte Docstring-Ergänzung (9 Zeilen), keine Reste der
Mutation.

## Tests / Suite

Testbefehl nach CLAUDE.md, `.venv/Scripts/python.exe -m pytest -n auto`,
Windows 10/11 x64, Branch `docs/audit-and-advisor-design`.

- **Mit Testabzug** (fester Abzug `NightreignHelper-Testabzug` ins
  umgelenkte `LOCALAPPDATA` kopiert): **1704 passed, 9 skipped, 0 failed**,
  173,92 s (+1 gegen die genannten 1703, exakt der neue Wächter).
- **Ohne erreichbaren Datenabzug** (umgelenktes `LOCALAPPDATA` leer, echtes
  Spiel installiert, jeder xdist-Worker extrahiert selbst): **1704 passed,
  9 skipped, 0 failed**, 275,53 s.
- Differenz: **101,61 s** gegen die im Auftrag genannten rund 108,26 s aus
  T-171/T-172 - kein Befund, im Rahmen der Messschwankung (~6 %, andere
  Prozess-/Systemlast).
- `tests/test_extraction.py` einzeln (ohne `-n`, wie CLAUDE.md verlangt):
  alle 7 Fälle grün, 203,24 s (das echte Spiel ist auf dieser Maschine
  installiert, alle sechs bisherigen "slow"-Fälle liefen tatsächlich, nicht
  nur der neue Wächter).

## Datenverzeichnisse - Nachweis der Umlenkung

- `LOCALAPPDATA` und `APPDATA`: per `os.environ.get` zur Laufzeit gelesen
  (`nrplanner/paths.py:20`, `nrplanner/shortcut.py:45`), nicht von
  `conftest.py` überschrieben - meine Exports auf eigene Scratchpad-Ordner
  (`…/scratchpad/T-173/local[_empty]`, `…/roaming`) waren wirksam. Beide
  Ordner nach den Läufen geprüft: keine Schreibvorgänge außerhalb dieser
  Ordner, kein Zugriff auf den echten `LOCALAPPDATA`/`APPDATA` des Nutzers.
- `NIGHTREIGN_SETTINGS_ORG`: **mein Export war wirkungslos** -
  `tests/conftest.py:44` überschreibt ihn beim Import unbedingt
  (`os.environ["NIGHTREIGN_SETTINGS_ORG"] = "DankYeeterTests"`, keine
  `setdefault`). Die tatsächliche Isolation läuft nicht über den in CLAUDE.md
  vorgesehenen Weg (eigener Wert je Auftrag), sondern über den fest verdrahteten
  Namen `DankYeeterTests` plus PID-Suffix in `NIGHTREIGN_SETTINGS_APP`
  (ebenfalls Zeile 45, ebenfalls unbedingt überschrieben). Registry-Probe
  bestätigt: unter `HKCU\Software\DankYeeterT-173` (mein exportierter Wert)
  landete nichts; unter `HKCU\Software\DankYeeterTests\NightreignHelperTests-<pid>`
  schon, und `clear_settings()` (das die Suite selbst über die
  `settings_store`-Fixture aufruft) räumt das beim Sitzungsende korrekt ab -
  direkt mit `QSettings.clear()+sync()` nachgestellt und verifiziert (Schlüssel
  vor dem Aufruf vorhanden, danach weg). Der reale Registry-Zweig
  `HKCU\Software\DankYeeter\NightreignHelper` (Produktion) wurde zu keinem
  Zeitpunkt berührt.
- Spielstand: nicht gelesen oder geschrieben von den geänderten/neuen Tests
  selbst; die sechs bestehenden `slow`-Fälle lesen das echte Spiel read-only,
  wie sie es vor diesem Auftrag auch schon taten (unverändert).

## DoD

- [x] Anforderung verstanden, Begründung vor dem Bauen geprüft
- [x] Build & Tests grün unter Windows 10/11 x64, beide Datenbedingungen
- [x] Neuer Test für neue Invarianz, mit vollem Mutationsbeweis. Kein Linter
      im Projekt konfiguriert (geprüft: kein `.flake8`, `pyproject.toml`
      ohne Lint-Sektion, kein `ruff`/`pylint` in requirements-dev.txt) -
      Punkt entfällt, keine Lücke.
- [x] Keine Secrets, keine TODOs, kein toter Code
- [x] Whitelist eingehalten (`tests/conftest.py`, `tests/test_extraction.py`
      ausschließlich; commit mit Pfad hinter `--`)
- [x] Doku aktualisiert (Docstring in `conftest.py`), Abschlussbericht
      abgelegt

## Beobachtung außerhalb des Auftrags - für den director

**Registry-Altlast unter `HKCU\Software\DankYeeterTests`:** beim Verifizieren
der Umlenkung gefunden, nicht gesucht. **147** Schlüssel, aus vielen
vergangenen Aufträgen/Sitzungen (u. a. `T060*`, `NHProbe*`, `*Differential-*`,
`*QAProbe*`, `*Timing*`) - erkennbar älter als diese Sitzung, nicht von mir
angelegt und nicht Teil meiner Auftrags-Whitelist, deshalb nicht angefasst.
Der Räum-Mechanismus selbst funktioniert nachweislich (siehe oben); die
Altlast deutet auf Sitzungen, die vor der Teardown-Fixture abgebrochen
wurden (Kill, Absturz, Hintergrundprozess nicht sauber beendet). Kein
Sicherheits- oder Datenverlustrisiko (eigene Test-Organisation, nie die
echte `DankYeeter`), aber unbegrenztes Wachstum in der echten Registry des
Nutzers. Ort: `HKCU\Software\DankYeeterTests\*`. Empfehlung: eigener kleiner
Aufwand, keine Blockade für laufende Aufträge.

**Stray-Datei `nul`** im Projektwurzelverzeichnis (54 Byte, untracked), war
schon vor meiner ersten Aktion vorhanden (vermutlich ein `> nul`-Redirect
unter Windows aus einer früheren Sitzung). Nicht von mir erzeugt, nicht
angefasst, nicht committet.

**Strukturelle Lücke in CLAUDE.md vs. Code:** CLAUDE.md schreibt vor, jeder
Auftrag lenke `NIGHTREIGN_SETTINGS_ORG` auf einen eigenen Wert um - das ist
seit der QA-043-Absicherung in `tests/conftest.py:44` technisch für **keinen**
Testlauf mehr möglich, weil die Datei den Wert beim Import unbedingt auf
`DankYeeterTests` setzt (die tatsächliche Isolation läuft über den
PID-Suffix in `NIGHTREIGN_SETTINGS_APP`, nicht über die Organisation). Das
ist keine Lücke, die dieser Auftrag verursacht oder beheben sollte
(`conftest.py`-Kopfzeilen waren nicht Teil der Whitelist-Änderung an dieser
Stelle), aber die Doku beschreibt einen Weg, den der Code seit T-046/QA-043
nicht mehr zulässt.

## An qa-engineer

Zu prüfen (Retest QA-220):
- Der neue Wächter läuft **ohne** installiertes Spiel grün (z. B. per CI oder
  mit leerem `LOCALAPPDATA` **ohne** Spielinstallation) - er hängt nicht an
  `installed_game`.
- Mutationsprobe wiederholbar wie oben beschrieben (Datei sichern, Fallback
  einbauen, Wächter muss rot werden, zurückkopieren).
- Beide Datenbedingungen weiterhin grün mit 1704/9/0.
- Die sechs bestehenden `slow`-Fälle laufen unverändert weiter, jetzt einzeln
  markiert statt per Modul-`pytestmark` - Verhalten bei `pytest -m "not slow"`
  bewusst geändert für den neuen Fall, für die sechs alten unverändert.
