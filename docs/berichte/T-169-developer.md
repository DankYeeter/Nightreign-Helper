STATUS: teilweise
AUFTRAG: T-169 - Die Version sagt 1.8.0 und meint etwas anderes (developer)
GELESEN: docs/tasks/T-169.md, nrplanner/__init__.py, nrplanner/app.py (Zeile 28, 1889), NightreignHelper.spec (Zeile 21-40), .github/workflows/release.yml (Zeile 66-77), scripts/setup_check.py (Zeile 179-186), CLAUDE.md (Projektzeilen)
GEÄNDERT: nrplanner/__init__.py (Version auf 1.9.0), tests/test_app_version.py (neu, Waechter) — beide committet in 84a22ef auf docs/audit-and-advisor-design
ANNAHMEN: keine (Vorgaben aus dem Auftrag vollstaendig, Director-Entscheidung 1.9.0 uebernommen)
NÄCHSTER: release-manager (clean-room-Lauf mit der neuen Version)
BLOCKIERT DURCH: nichts fuer diesen Auftrag selbst — aber ein Suite-Befund fuer den director (siehe unten), unabhaengig von meiner Aenderung

## Umgesetzt

- `nrplanner/__init__.py`: `__version__` von `"1.8.0"` auf `"1.9.0"` geaendert.
  Kommentarblock unveraendert gelassen — er beschreibt die Regel ("bump the
  patch/middle digit ...") und die Datei als einzige Quelle, beides bleibt
  gueltig.
- `tests/test_app_version.py` (neu, 3 Tests):
  - `test_version_is_assigned_exactly_once_in_the_source_file` — genau eine
    `__version__ = "..."`-Zuweisung in `nrplanner/__init__.py`.
  - `test_version_has_the_expected_shape` — Semver-Form `\d+\.\d+\.\d+`, weil
    `release.yml` den Tag zeichengenau dagegen vergleicht.
  - `test_no_other_source_file_hardcodes_the_current_version` — prueft die
    vier Dateien, die die Version zur Build-/Laufzeit lesen (`app.py`,
    `NightreignHelper.spec`, `.github/workflows/release.yml`,
    `scripts/setup_check.py`), dass keine das aktuelle Versionsliteral
    ausschreibt statt es dynamisch zu importieren/parsen.

## Zur "mehreren Stellen"-Frage

Vor der Aenderung geprueft (zwei unabhaengige Suchen: `1\.8\.0` und
`__version__`, je projektweit): 34 bzw. 14 Treffer, aber bei genauer Durchsicht
sind das ausschliesslich **Doku-/Auftrags-/Berichtsdateien** unter `docs/`,
`qa/`, `ARCHITECTURE.md`, `CLAUDE.md` (historische Auftragszahlen, keine
Quelle-der-Wahrheit) sowie die vier oben genannten Leser, die alle dynamisch
lesen (`from nrplanner import __version__` bzw. Regex auf
`nrplanner/__init__.py`). **Kein zweiter hartcodierter Ort in Code oder
Build-Konfiguration gefunden** — die Datei war schon vorher als einzige Quelle
dokumentiert und ist es tatsaechlich. Kein Befund im Sinne des Auftrags, daher
keine Erweiterung ueber die Whitelist hinaus noetig.

## Rot-vorher (statt vollem Mutationsbeweis)

Auftrag erlaubt Verzicht auf vollen Mutationsbeweis, wenn der Bruch sofort
sichtbar ist. Zwei der drei Assertions handgepr fuft, per Kopie-vorher/
Kopie-zurueck (nie `git checkout --`), dritte durch Lesen begruendet:

1. Zweite `__version__`-Zeile an `nrplanner/__init__.py` angehaengt →
   `test_version_is_assigned_exactly_once_in_the_source_file` faellt (belegt
   oben mit vollem pytest-Output).
2. Kommentarzeile `# fallback = "1.9.0"` in `NightreignHelper.spec` angehaengt
   → `test_no_other_source_file_hardcodes_the_current_version` faellt (belegt).
3. `test_version_has_the_expected_shape` nicht mutiert: der Regex
   `\d+\.\d+\.\d+` (`re.fullmatch`) laesst offensichtlich weder `"1.9"` noch
   `"v1.9.0"` noch `"unknown"` durch — kein Zweifel, der eine eigene Probe
   rechtfertigt.

Beide Dateien danach per `cp *.orig` zurueckkopiert, `git status --porcelain`
bestaetigt: nur die beabsichtigte Aenderung an `nrplanner/__init__.py` blieb
stehen.

## Datenverzeichnis-Umlenkung

`NIGHTREIGN_SETTINGS_ORG=DankYeeterT-169`,
`LOCALAPPDATA=…/scratchpad/T-169/localappdata`,
`APPDATA=…/scratchpad/T-169/appdata` — alle drei vor jedem Testlauf gesetzt und
im Bash-Output sichtbar. Kein Spielstand geschrieben (read-only, nicht
angefasst).

## Tests

- `tests/test_app_version.py` einzeln (ohne `-n`): 3 passed, 1.25 s.
- Volle Suite `pytest -n auto`: **1 failed, 1692 passed, 9 skipped, 9 errors**
  in 277,76 s — **nicht** die geforderten 1699 passed/0 failed.

### Befund: 10 vorbestehende, von meiner Aenderung unabhaengige Fehlschlaege

`tests/test_advisor_evaluate.py::test_the_advisor_computes_the_build_the_window_shows`
und 9 Faelle in `tests/test_marginal_returns.py` (`KeyError: '15'` in
`a_nightfarer_other_than_the_first`, Zeile
`planner.heroes[0]["levels"][str(level)]` — Level 15 fehlt im geladenen
Datensatz). **Verifiziert unabhaengig von meiner Aenderung**: `git clone .`
in den Scratchpad, dort mit umgelenkten Variablen (`DankYeeterT-169klon`,
eigenes `LOCALAPPDATA`/`APPDATA`) dieselben zwei Testdateien mit `-n auto`
laufen lassen — identischer Fehler, gleiche Zeile, gleiches `KeyError: '15'`,
auf dem Commit-Stand **vor** meiner Aenderung. Scratch-Klon danach geloescht.

Rechnung stimmt: 1699 (Baseline) − 10 (jetzt rot) + 3 (neue Waechtertests) =
1692 passed — deckungsgleich mit dem gemessenen Ergebnis. Das bestaetigt: die
10 Fehlschlaege sind **nicht** durch T-169 verursacht, aber die im Auftrag
genannte Referenzzahl "1699 passed, 9 skipped, 0 failed" ist zum jetzigen
Stand (Commit vor `84a22ef`) **nicht mehr grün** — unabhaengig von dieser
Aenderung.

Ursache nicht untersucht (ausserhalb der Whitelist `nrplanner/__init__.py` +
`tests/`, und ausserhalb des Auftragsziels).

## DoD

- [x] Anforderung verstanden, Annahmen dokumentiert (keine)
- [ ] Build & Tests gruen — Waechtertest und mein eigener Diff sind gruen,
      aber die **volle Suite ist nicht gruen** (10 vorbestehende Fehlschlaege,
      s.o.). Nicht durch T-169 verursacht, aber offen fuer die Freigabe der
      naechsten Stufe (clean-room).
- [x] Linter: keiner konfiguriert (Punkt entfaellt lt. Vorgabe)
- [x] Keine Secrets, keine TODOs, kein toter Code
- [x] Whitelist eingehalten, nur `nrplanner/__init__.py` und `tests/` beruehrt
- [x] Doku: kein `CHANGELOG.md` (Vorgabe), Bericht liegt vor

## An director

**Neuer, von T-169 unabhaengiger Befund:** die volle Suite ist auf dem
aktuellen Branch-Stand **nicht** mehr bei 1699 passed/0 failed — sondern bei
1 failed + 9 errors in `tests/test_advisor_evaluate.py` und
`tests/test_marginal_returns.py` (`KeyError: '15'`, Level 15 fehlt im
Datensatz beim Aufbau des Vergleichszustands). Reproduziert in einem frischen
`git clone` **vor** meiner Aenderung — also nicht durch T-169 eingefuehrt.
Wahrscheinlich seit T-164 (letzte bestaetigte 1699er-Zahl) eine echte
Regression aus einer der Zwischenauftraege, oder eine Umgebungsabhaengigkeit
der Testdaten (z. B. Testabzug/Datenschnappschuss inzwischen anders befuellt).
Empfehlung: `fehlerdiagnostiker` oder `qa-engineer` beauftragen, bevor der
`clean-room`-Lauf (naechster Schritt laut `docs/state.md`) gegen ein
Artefakt mit dieser Suite als Referenz laeuft — die genannte Zahl
1699/9/0 stimmt sonst nicht mehr als Vergleichsbasis.

Kein Sicherheits-, kein Datenverlustrisiko in meiner eigenen Aenderung. Die
Version 1.9.0 ist gesetzt und durch den neuen Waechter gegen kuenftige
Duplizierung abgesichert.

## An release-manager (via director)

`nrplanner/__init__.py` traegt jetzt `1.9.0`, committet als `84a22ef` auf
`docs/audit-and-advisor-design`. Der `clean-room`-Lauf kann das Update
1.8.0 → 1.9.0 pruefen, sobald ein neues Artefakt aus diesem Commit gebaut ist
(das aus T-168 traegt noch die alte Zeichenkette).

## An qa-engineer

Nichts Neues zu pruefen aus dieser Aenderung selbst (eine Konstante plus ein
reiner Quell-Waechtertest, keine Laufzeit-/UI-Aenderung). Der oben gemeldete
Suite-Befund (`KeyError: '15'`) betrifft `tests/test_advisor_evaluate.py` und
`tests/test_marginal_returns.py` — falls QA das Advisor-Level-Verhalten
ohnehin im naechsten Zyklus anfasst, ist das ein Hinweis, kein Auftrag von
mir.
