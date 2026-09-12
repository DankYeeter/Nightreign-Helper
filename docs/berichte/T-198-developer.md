STATUS: erledigt
AUFTRAG: T-198 — QA-235: der Test, der an der Steam-Installation dieser Maschine haengt
GELESEN: docs/tasks/T-198.md, qa/findings.md (QA-235), tests/test_first_run_panel.py, nrplanner/firstrun.py, nrdata/gamefiles.py, tests/test_steam_library_start_folder.py, tests/test_game_dir_recognition.py, tests/test_shortcut_interpreter.py, tests/conftest.py, docs/state.md (Abschnitt "Beschlossen, nicht beauftragt", SEC-036-Zitat), security/findings.md (SEC-036)
GEÄNDERT: tests/test_first_run_panel.py (committet, eb9a7af)
ANNAHMEN: keine
NÄCHSTER: qa-engineer
BLOCKIERT DURCH: nichts

## Umgesetzt

`tests/test_first_run_panel.py::test_the_first_dialog_opens_at_the_folder_that_was_remembered`
(Zeile 567 ff.) setzt jetzt die Steam-Umgebung selbst, statt sie von der
Maschine zu lesen:

```python
monkeypatch.setattr(firstrun.gamefiles, "steam_common_folders", lambda: [])
fallback = tmp_path / "fallback" / "steamapps" / "common"
fallback.mkdir(parents=True)
monkeypatch.setattr(firstrun, "STEAM_COMMON", fallback)

assert firstrun.where_to_start_looking(None) == fallback
```

Muster uebernommen aus derselben Datei, Zeile 343
(`monkeypatch.setattr(firstrun, "bundled_path", lambda: snapshot)`). Die
Erwartung ist jetzt eine Gleichheit statt einer Tupel-Mitgliedschaft — der
Test sagt, welcher Ordner erwartet wird, und das ist bei gesetzter Wurzel
eindeutig (Vorgabe 2).

`nrplanner/firstrun.py` wurde **nicht** geaendert — der Test war ohne
Aenderung an `where_to_start_looking` reparierbar, wie in Vorgabe 4
verlangt.

## Rot-vorher (Vorgabe 3)

`firstrun.py` vor der Aenderung mit `cp` in den Scratchpad
(`…/scratchpad/T-198/firstrun.py.orig`) gesichert, dann testweise
`places.append(STEAM_COMMON)` aus `where_to_start_looking` entfernt (die
Zeile, die den Fallback ueberhaupt ausloest) und den Test isoliert
gelaufen:

```
python -m pytest tests/test_first_run_panel.py -q -k test_the_first_dialog_opens_at_the_folder_that_was_remembered
```

```
AssertionError: assert None == WindowsPath('.../fallback/steamapps/common')
tests\test_first_run_panel.py:586: AssertionError
1 failed, 63 deselected in 0.61s
```

Danach `firstrun.py` aus der Sicherung zurueckkopiert (nicht
`git checkout --`); `git diff -- nrplanner/firstrun.py` bestaetigt keine
Abweichung mehr. Voller Testlauf danach wieder gruen (64 passed).

## Zwei Fragen aus Vorgabe 4

**Frage A — ist `STEAM_COMMON` als feste Wurzel noch richtig, angesichts
SEC-036?**

Ja, aber sie ist jetzt **funktional redundant**, nicht neu riskant. Ablauf:
`where_to_start_looking(None)` ruft zuerst `gamefiles.steam_common_folders()`
auf, die ihre Kandidaten aus `gamefiles._steam_roots()` zieht — und die
haengt (SEC-036, offen) neben der Registry-Wurzel selbst **schon** die
festen Pfade `C:\Program Files (x86)\Steam` und `C:\Steam` an, unbedingt,
unabhaengig vom Registry-Ergebnis. Der `steamapps\common`-Ordner unter
`C:\Program Files (x86)\Steam` — exakt der Wert von `firstrun.STEAM_COMMON`
— steckt also bereits in der Liste, die `steam_common_folders()` liefert,
bevor `where_to_start_looking` `STEAM_COMMON` ueberhaupt separat anhaengt.

Sicherheitsseitig ist `firstrun.STEAM_COMMON` nicht dasselbe Risiko wie
SEC-036: SEC-036 betrifft den klick- und fensterlosen Automatikpfad
(`find_game_dir`), der eine DLL laedt, ohne dass der Nutzer je eine Wahl
trifft. `where_to_start_looking` bestimmt nur, wo sich der
Ordnerauswahl-Dialog beim ersten Oeffnen befindet — der Nutzer sieht und
bestaetigt den Ordner danach noch per Klick. Kein eigenstaendiges
Sicherheitsrisiko.

Aber: sollte SEC-036 in der von ihr selbst vorgeschlagenen Richtung
behoben werden ("feste Wurzel entfernen, Steam schreibt seine Wurzel in
die Registry"), wuerde `_steam_roots()` die festen Pfade verlieren — und
`firstrun.STEAM_COMMON` bliebe dann die **einzige** verbleibende feste
Fallback-Wurzel im ganzen Modul, mit genau der Schwaeche, die SEC-036 fuer
`_steam_roots()` beschreibt (jedes authentifizierte Konto darf unter `C:\`
Unterordner anlegen). Das ist eine Frage an den Director/Sicherheitsprozess,
nicht an mich zu entscheiden: Soll `STEAM_COMMON` bei einer SEC-036-Behebung
mitgezogen werden, oder bleibt sie bewusst als reiner UI-Startpunkt
(niedriges Risiko, da klickpflichtig) bestehen? Ich habe `firstrun.py`
dafuer **nicht** angefasst — das waere ueber die im Auftrag erlaubte
Aenderung hinausgegangen und QA-232 (A7-Regression, offen auf derselben
Datei) haette mitgetroffen werden koennen.

**Frage B — weitere Stellen in `tests/`, die eine Maschineneigenschaft
lesen statt sie zu setzen?**

Eine gefunden, nicht repariert (Auftrag verlangt nur Meldung):

`tests/test_shortcut_interpreter.py:22-29`
(`test_the_interpreter_is_taken_from_the_windows_folder`) liest
`os.environ["SystemRoot"]` direkt von der laufenden Maschine und prueft,
dass der gefundene PowerShell-Pfad relativ dazu liegt — kein
`monkeypatch.setenv`. Milder als QA-235, weil `SystemRoot` auf jeder
Windows-Installation praktisch `C:\Windows` ist (kein Analogon zu einer frei
waehlbaren Steam-Bibliothek), und die drei Nachbartests derselben Datei
(`test_no_system_root_means_no_interpreter`,
`test_an_interpreter_that_is_not_there_is_not_offered`,
`test_the_shortcut_fails_with_a_message_when_powershell_is_missing`) setzen
`SystemRoot` bereits explizit per `monkeypatch`. Kein `skipif`, aber ein
Laufzeit-`pytest.skip`, falls auf der Maschine kein PowerShell unter
`%SystemRoot%` gefunden wird — bewusst gebaut, keine Umgehung.

Geprueft, keine weiteren Treffer: `grep` nach `winreg`, `expanduser`,
`getpass`, `Program Files`, `LOCALAPPDATA`/`APPDATA` (ausser
Doku-/Konstantentext) in `tests/` — keine weiteren direkten
Maschinenlesungen ausser der genannten Stelle. `gamefiles`-bezogene Tests
(`test_steam_library_start_folder.py`, `test_game_dir_recognition.py`)
monkeypatchen `_steam_roots`/`steam_common_folders` bereits durchgehend.

## Tests

`python -m pytest tests/test_first_run_panel.py -q` (einzeln, ohne `-n`):
**64 passed** in 0.78 s (vorher: 1 failed von 407 kombiniert ueber beide
Dateien, siehe Direktor-Messung im Auftrag — die 64 sind die Zahl der Datei
allein).

Nachbardateien zur Absicherung mitgelaufen (nicht Teil des Auftrags,
Gegenprobe): `python -m pytest tests/test_steam_library_start_folder.py
tests/test_game_dir_recognition.py -q` — 46 passed.

Rot-vorher siehe oben. Bewusst nicht abgedeckt: die volle Suite mit `-n
auto` (Auftrag verlangt nur die Zahl der beruehrten Datei einzeln); T-196
laeuft parallel am festen Testabzug und wurde nicht angefasst.

## DoD

- Anforderung verstanden, Annahmen dokumentiert: erfuellt, keine offenen
  Annahmen.
- Build & Tests gruen in der benannten Testumgebung (Windows, dieser
  Rechner): erfuellt fuer die beruehrte Datei und ihre zwei Nachbardateien.
  Volle Suite (`pytest -n auto`) nicht erneut gelaufen — nicht verlangt,
  nicht Teil dieses kleinen Auftrags.
- Linter: kein Linter im Projekt konfiguriert (Standardaussage laut
  Rahmen) — entfaellt, keine Luecke.
- Keine Secrets, keine TODOs, kein toter Code: erfuellt.
- QA-Akzeptanzkriterien selbst durchgespielt: der Rotlauf-Nachweis ist die
  Abnahme dieses kleinen Auftrags, siehe oben.
- Doku aktualisiert: nicht meine Datei (`qa/findings.md`, `docs/state.md`) —
  QA-235 kann laut diesem Bericht auf "behoben" gesetzt werden, das traegt
  der Director/qa-engineer ein.

## An qa-engineer

QA-235 kann geschlossen werden: `tests/test_first_run_panel.py` ist jetzt
unabhaengig von der Steam-Installation der Testmaschine gruen (Rotlauf
nachgewiesen, siehe oben). Bitte QA-235 in `qa/findings.md` auf "behoben"
setzen — das ist eure Datei, nicht meine.

## An director

- **Frage A (SEC-036-Zusammenhang)** siehe oben: `firstrun.STEAM_COMMON`
  ist heute funktional redundant zu `gamefiles._steam_roots()`s eigenem
  festen Fallback, und wuerde bei einer SEC-036-Behebung nach der im Befund
  vorgeschlagenen Richtung ("feste Wurzel entfernen") zur letzten
  verbleibenden festen Wurzel im Modul. Niedriges eigenstaendiges Risiko
  (Klickpflicht), aber eine Entscheidung wert, ob sie mit SEC-036
  mitgezogen wird oder bewusst bestehen bleibt.
- **Frage B (Befund, nicht Vorgabe):** `tests/test_shortcut_interpreter.py:28`
  liest `os.environ["SystemRoot"]` von der echten Maschine statt es zu
  setzen — milde, weil `SystemRoot` praktisch immer `C:\Windows` ist, aber
  strukturell dasselbe Muster wie QA-235. Nicht repariert, wie im Auftrag
  verlangt.
- QA-232 (A7-Regression, `firstrun.py`) und QA-234 (verwaister
  Mutationsanker in `tests/test_differential_track.py`) unberuehrt, wie
  vorgegeben.

## An ui-ux-designer

Keine Abweichung, keine Beruehrung von UI-Text oder -Verhalten.
