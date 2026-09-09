STATUS: erledigt
AUFTRAG: T-162 - Der Automatikweg bekommt dieselbe Pruefung (developer)
GELESEN: docs/tasks/T-162.md, nrdata/gamefiles.py, nrplanner/firstrun.py,
tests/test_game_path_memory.py, tests/test_game_dir_recognition.py
GEÄNDERT: nrdata/gamefiles.py, tests/test_game_dir_recognition.py,
nrplanner/firstrun.py, tests/test_game_path_memory.py (alle vier committet,
zwei Commits: 55c441c fix(gamefiles), caa8c11 docs(firstrun))
ANNAHMEN: keine wesentlichen -- der Auftrag war eindeutig, das Praedikat
existierte bereits (`looks_like_the_game`).
NÄCHSTER: director
BLOCKIERT DURCH: nichts (der eigene Auftrag ist erledigt; siehe unten zwei
Funde ausserhalb des eigenen Scopes, die dem director gemeldet werden)

## Umgesetzt

**SEC-031, erste Haelfte.** `find_game_dir()` (`nrdata/gamefiles.py:51-77`)
fragt jetzt `looks_like_the_game(path)` statt nur
`(path / "regulation.bin").exists()`. Die Kandidatenliste (Steam-Registry,
`libraryfolders.vdf`, Laufwerksfallback C-H) ist unveraendert -- nur das
Praedikat auf jedem Kandidaten wurde ausgetauscht. Docstring ergaenzt, die
Begruendung nennt SEC-031 und die AK-106/AK-107-Unberuehrtheit.

**Sechs neue Testfaelle** in `tests/test_game_dir_recognition.py`
(Abschnitt "find_game_dir asks the same predicate (SEC-031)"):
- findet einen Ordner, der alle drei Bedingungen erfuellt
- verwirft `regulation.bin` allein (die urspruengliche Luecke)
- verwirft eine leere `regulation.bin`
- verwirft eine `regulation.bin` ueber der Decke
- akzeptiert eine `regulation.bin` genau an der Decke (Positivkontrolle)
- findet nichts, wenn kein Kandidat existiert

Ein Helfer `_the_only_candidate()` patcht `INSTALL_DIR`, `_steam_roots` und
`_library_paths`, sodass sowohl der Steam-Kandidat als auch die sechs
Laufwerks-Fallback-Kandidaten auf einen kontrollierten, garantiert nicht
real existierenden Ordnernamen zeigen -- das schuetzt die "verwirft"-Faelle
davor, durch die echte Installation oder ein zufaellig passendes Laufwerk
verfaelscht zu werden.

**Zwei Docstrings entschaerft** (B8, security-reviewer widerlegt seine
eigene Auflage M3):
- `tests/test_game_path_memory.py:3-13` (Modul-Docstring)
- `nrplanner/firstrun.py:427-432` (`_confirm`)

Beide behaupteten, das Nicht-Schreiben von `paths/game` sei "die einzige
Schranke, die SEC-026 stehen laesst" bzw. "die eine Sicherheitsfunktion
dieses ganzen Ablaufs". Falsch: die Invariante bewacht die **Ablage**
(was gemerkt wird), nicht die **Nutzung** (welcher Ordner in dieser
Sitzung tatsaechlich gebaut wird) -- ein automatisch gefundener Ordner lief
immer schon in den Bau, egal ob er je geschrieben wurde. Was tatsaechlich
haelt und gemessen bleibt (ein Aufrufer von `remember_game`, eine
`setValue`-Stelle auf `paths/`), steht unveraendert in beiden Texten.

## Was ich nicht angefasst habe

Der Laufwerksfallback `C`-`H` in `find_game_dir()` (Zeilen 68-72
unveraendert) -- laut Auftrag eine offene Frage an den Nutzer, nicht meine
Entscheidung.

## Tests

`pytest tests/test_game_dir_recognition.py tests/test_game_path_memory.py`
(env: `LOCALAPPDATA`/`APPDATA` auf eigenes Scratchpad-Unterverzeichnis
`T-162/`, `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-162` umgelenkt, siehe unten):
**79 passed**.

**Mutationsbeweis, manuell gefuehrt** (Kopie-Trick, kein `git checkout`):
`nrdata/gamefiles.py` vor der Mutation nach `.fixed` kopiert, die
Schleife programmatisch auf `(path / "regulation.bin").exists()`
zurueckgesetzt, dieselben drei Faelle liefen erneut:

```
FAILED test_find_game_dir_rejects_regulation_bin_alone
FAILED test_find_game_dir_rejects_an_empty_regulation
FAILED test_find_game_dir_rejects_a_regulation_over_the_ceiling
3 failed, 3 passed
```

Alle drei "verwirft"-Faelle sterben unter der Rueckumstellung -- der
Mutationsbeweis beisst. Datei danach aus `.fixed` zurueckkopiert, `git
diff --stat` bestaetigt: nur die beabsichtigte Aenderung steht noch im
Baum.

**A15-Beleg (reale Installation dieser Maschine):** `find_game_dir()`
liefert vor **und** nach der Aenderung denselben Ordner
(`D:\SteamLibrary\steamapps\common\ELDEN RING NIGHTREIGN\Game`),
`looks_like_the_game()` darauf ist `True`. Geprueft per Kopie-Trick
(alte Fassung aus `git show HEAD:nrdata/gamefiles.py` temporaer
eingespielt, Ergebnis verglichen, dann zurueckkopiert). Kein heute
gefundener Ordner faellt durch -- A15 bleibt erfuellt, keine Frage an
den `ui-ux-designer` noetig.

**Volle Suite** (`pytest -n auto`, dieselbe Umlenkung): siehe unten --
mit zwei Funden ausserhalb meines Scopes, die die Zahl verfaelschen.

## Datenverzeichnisse (Nachweis)

`LOCALAPPDATA` und `APPDATA` auf
`…\scratchpad\T-162\localappdata` bzw. `…\appdata`, `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-162`
gesetzt und mit `env | grep` vor dem ersten Testlauf bestaetigt (siehe
Werkzeugprotokoll). Fuer den Vergleichslauf am frischen Klon (siehe unten)
ein zweites, eigenes Paar `localappdata2`/`appdata2` mit
`NIGHTREIGN_SETTINGS_ORG=DankYeeterT-162-klon`. Spielinstallation nur
gelesen (`find_game_dir`, `looks_like_the_game` -- beide lesen ausschliesslich
Metadaten und einen Byte aus `regulation.bin`), nirgends geschrieben.

## Zwei Funde ausserhalb meines Scopes -- an den director

Beim vollen Suitelauf (`pytest -n auto`) sind **zwei Fehlerbilder**
aufgetreten, die **nichts** mit `gamefiles.py`/`firstrun.py` zu tun haben
und **nicht** auf meiner Datei-Whitelist stehen:

1. **`tests/test_advisor_evaluate.py::test_the_advisor_computes_the_build_the_window_shows`**
   und **9 Setup-Errors in `tests/test_marginal_returns.py`**
   (`KeyError: '15'` bzw. `KeyError: '1'` auf `hero["levels"][str(level)]`).
   **Verifiziert als vorbestehend, unabhaengig von meiner Aenderung:** frischer
   `git clone` des aktuellen committeten HEAD (`f72f93e` zum Zeitpunkt der
   Pruefung) nach `…/scratchpad/T-162/klon`, dort `pytest
   tests/test_advisor_evaluate.py tests/test_marginal_returns.py` mit
   eigener Datenumlenkung -- **identischer Fehler, 1 failed, 9 errors**,
   ganz ohne meine uncommitteten Aenderungen. Der Klon wurde danach geloescht.
2. **`tests/test_save_read_in_the_background.py::test_the_collector_of_the_texts_really_fires`**
   (Assertion auf einen erwarteten Text, der im aktuellen Ausgabetext fehlt).
   Diese Datei steht explizit auf der Dateiliste von **T-161**, das laut
   Auftrag **parallel** in diesem Arbeitsbaum laeuft -- `git status` zeigte
   sie waehrend meines Laufs als veraendert, und `git log` zeigte
   zwischenzeitlich neue Commits von T-161 (`f72f93e`, danach `f645c01`).
   Sehr wahrscheinlich Kontamination durch die parallele, noch laufende
   Bearbeitung derselben Datei -- ich habe das **nicht** weiter untersucht,
   da die Datei nicht meiner Rolle in diesem Auftrag gehoert.

Mit diesen beiden ausgeklammert lief die restliche Suite sauber durch:
`pytest -n auto` mit `--deselect` auf die zehn Faelle aus Fund 1 ergab
**1 failed** (Fund 2), **1669 passed**, **9 skipped** -- keine weiteren
Ueberraschungen. Die vom Auftrag genannte Zielzahl **1674 passed, 9
skipped, 0 failed** ist wegen der beiden Funde und der parallel
laufenden T-161-Commits derzeit nicht sauber nachstellbar; das ist keine
Aussage ueber meinen eigenen Auftrag, dessen Dateien und Tests isoliert
gruen sind.

## DoD

- Anforderung verstanden, Annahmen: keine wesentlichen
- Build & Tests gruen fuer die eigene Whitelist (79/79, plus
  Mutationsbeweis manuell gefuehrt); volle Suite zeigt zwei fremde,
  nachgewiesen unabhaengige Fehlerbilder (siehe oben)
- Kein Linter im Projekt konfiguriert -- entfaellt
- Keine Secrets, keine TODOs, kein toter Code
- QA-/UX-Vorgaben: keine (kein Fenster, kein Klick beruehrt, AK-106/AK-107
  unveraendert)
- Doku: zwei Docstrings korrigiert (B8); `docs/state.md`,
  `security/findings.md` etc. nicht angefasst -- SEC-031 (erste Haelfte)
  und B8 sind fuer den director zum Eintragen

## An qa-engineer

Zu testen: ein Automatik-Fund, dessen `regulation.bin` ueber der 64-MiB-Decke
liegt oder ohne `.bhd`/DLL ist, darf nicht mehr automatisch gefunden werden
(vorher: ja). Ein realer, vollstaendiger Spielordner muss weiterhin
automatisch gefunden werden -- auf dieser Maschine empirisch bestaetigt,
auf anderen Maschinen ungeprueft.

## An director

- SEC-031 erste Haelfte umgesetzt und getestet (Mutationsbeweis siehe
  oben). Zweite Haelfte (Laufwerksfallback C-H) bleibt offen, liegt dem
  Nutzer vor.
- B8 (falsche M3-Schranke in zwei Docstrings) entschaerft.
- **Zwei Funde ausserhalb meines Scopes**, siehe Abschnitt oben: die
  `test_advisor_evaluate.py`/`test_marginal_returns.py`-Fehler sind
  nachweislich vorbestehend im aktuellen HEAD (nicht durch mich
  verursacht); der `test_save_read_in_the_background.py`-Fehler faellt in
  T-161s Dateiliste und lief waehrend meines Suitelaufs parallel und live.
  Beide bitte an die zustaendige Rolle (developer T-161 bzw. den
  Verursacher der advisor/marginal_returns-Regression) weiterreichen.
- Zielsystem: Windows 10/11 x64, diese Maschine. macOS/Linux ungeprueft
  (kein Ziel laut CLAUDE.md).
