STATUS: erledigt
AUFTRAG: T-217 — Spielordner nur aus Steam-Herkunft: SEC-038, SEC-036, SEC-026
GELESEN: docs/tasks/T-217.md (vollstaendig); CLAUDE.md; nrdata/gamefiles.py, nrdata/oodle.py (vollstaendig); nrplanner/firstrun.py (140-250, 300-560, 1025-1052); nrplanner/gamepath.py (100-175); nrplanner/paths.py (18-30); tests/conftest.py (100-255); tests/test_game_dir_recognition.py (1-60, 130-175); tests/test_steam_library_start_folder.py (vollstaendig); tests/test_first_run_panel.py (1-60, 160-170, 240-270, 440-600); tests/test_game_path_memory.py (1-80, 120-240); tests/test_differential_track.py (470-500); scripts/differential/mutate.py (4554-4580)
GEÄNDERT: nrdata/gamefiles.py; nrplanner/firstrun.py; scripts/differential/mutate.py; tests/conftest.py; tests/test_first_run_panel.py; tests/test_game_dir_recognition.py; tests/test_game_path_memory.py; tests/test_steam_library_start_folder.py; docs/berichte/T-217-developer.md
ANNAHMEN: (1) Der Worktree-Branch heisst `worktree-agent-ab519a55f909fc9ba`, nicht `docs/audit-and-advisor-design`; beide standen bei Schritt 0 auf 83cfed8 (enthaelt 41206be), darum weitergearbeitet — Commit 09f5cdb liegt auf dem Worktree-Branch, der director fuehrt ihn nach. (2) "Bibliothek auf einem anderen Laufwerk" ist auf C: gebaut: eine Bibliothek, die nur `libraryfolders.vdf` nennt und ausserhalb der Steam-Wurzel liegt; ein zweites Laufwerk gibt es in der Suite nicht. (3) Beide Seiten der Herkunftspruefung werden aufgeloest (`resolve()`): eine Junction *in* einer Bibliothek, die hinauszeigt, gilt nicht; eine Bibliothek, die *selbst* eine Junction ist, gilt — sie ist der Ordner, den Steam nennt.
NÄCHSTER: director (Nachfuehren auf `docs/audit-and-advisor-design`; Spec AK-230/A28 mit dem Satz unten; Befunde 1-4)
BLOCKIERT DURCH: nichts

## Pruefpunkt und Aufrufer

`gamefiles.looks_like_the_game` fragt als letzte Bedingung
`gamefiles.in_a_steam_library(folder)` (aufgeloester Pfad beginnt mit
`<root>/steamapps/common` einer Bibliothek aus `steam_common_folders()`,
d. h. Registry + `libraryfolders.vdf`). Aufrufer von `looks_like_the_game`
im Anwendungscode (`grep -rn looks_like_the_game --include=*.py`, ohne
tests/scripts): `gamefiles.find_game_dir:84`, `gamefiles._search_within_budget`
(`:273`, `:289`, Route des gezeigten Ordners ueber `firstrun.look_at` →
`search_from`), `gamepath.resolve_game:134` (gemerkter Pfad). Die drei
`oodle.load`-Aufrufer (`bossdata:320`, `extract:181`, `icons:82`) erhalten
`game_dir` nur ueber `gamepath.resolve_game` oder `Settled.game`
(Waechter `test_only_the_resolution_point_asks_where_the_game_is`). Darum ein
Pruefpunkt, keiner vor `ctypes.CDLL`.

## Ablehnungssatz (E1, dritte Zeile, wenn der gezeigte Ordner ausserhalb liegt)

> That folder is not inside a Steam library, so Nightreign Helper will not run the game's files from there. Pick the folder Steam installed the game in: in Steam that is Manage, then Browse local files.

Headline und die beiden ersten Zeilen von E1 bleiben; Panelname bleibt E1.

## Rot/Gruen

Rot (vor SEC-036-Fix): `python -m pytest tests/test_steam_library_start_folder.py -q`
→ 5 failed, 4 passed; darunter `test_the_real_root_list_holds_nothing_the_registry_did_not_name`
mit `Extra items in the left set: WindowsPath('C:/Steam'), WindowsPath('C:/Program Files (x86)/Steam')`.
Gruen: derselbe Befehl → 9 passed. Suite: `pytest -n auto` (umgelenkt,
`NIGHTREIGN_SETTINGS_ORG=DankYeeterT-217`) → 1797 passed, 9 skipped, 65,6 s.
Mutation `dll-condition-dropped` per Kopie eingespielt: 2 failed (dieselben
zwei Tests wie dokumentiert), zurueckkopiert, 42 passed.

## Befunde

1. **SEC-038-Zaehlung:** `grep -rn _steam_roots tests/` ergibt 5 Zeilen, davon
   **4 Stubs** (`test_game_dir_recognition.py:153`,
   `test_steam_library_start_folder.py:46,57,67`) und 1 Docstring-Erwaehnung
   (`:10`). Nicht "5 von 5 Stubs"; Richtung des Befunds unveraendert.
2. **SEC-042 (`firstrun.STEAM_COMMON:153`):** bleibt als Dialogstart
   funktionsfaehig. Folge des Fixes: ohne Steam in der Registry wird jeder
   Ordner abgelehnt, auch einer unter `STEAM_COMMON` — das ist die
   Nutzerentscheidung (Herkunft), kein Fehler; melden, nicht gebaut.
3. **E1-Headline** "That folder does not hold a copy of the game." steht auch
   ueber dem Herkunftssatz; bei einer echten Kopie ausserhalb Steams ist sie
   streng genommen falsch. Ausserhalb des Auftrags (nur der Satz) — an
   ui-ux-designer/Spec.
4. **Aufgaben-Datei ausserhalb der Liste:** `scripts/differential/mutate.py`
   (Anker der Mutation `dll-condition-dropped`) musste nachgezogen werden,
   sonst rot in `test_differential_track.py`. Nur `old`/`new`, Messtext
   unveraendert.

## Ponytail

`git diff 83cfed8..HEAD`: 8 Dateien, +228/−20, net +208 (davon Tests +170).
Gestrichen: nichts weiter — die fuenf neuen Herkunftstests sind je ein
Kriterium des Auftrags, die Fixture ersetzt 27 Einzel-Stubs.
