STATUS: erledigt
AUFTRAG: T-253 - Artefakt 1.11.0 bauen (release-manager, Modus `build`)
GELESEN: docs/legal/AUFLAGEN.md (vollstaendig, 445 Zeilen, selbst nachgeprueft - siehe unten); docs/berichte/T-249-release-manager-build.md (vollstaendig, als Vorlage fuer den Ablauf); nrplanner/__init__.py (Version 1.11.0 bestaetigt); NightreignHelper.spec (unveraendert gegenueber T-249); .gitignore (`dist/`, `build/` beide erfasst)
GEAENDERT: `dist/NightreignHelper.exe` (neu gebaut, ein Lauf). Kein Commit, kein Anwendungscode angefasst.
ANNAHMEN: keine ausser der im Auftrag benannten (Version 1.11.0 ist bereits gesetzt, developer-Arbeit vor diesem Lauf, nur gelesen). Ein Lauf statt zwei - der Auftrag nennt "ein Lauf" ausdruecklich; Nicht-Bit-Identitaet ist in T-241 bereits dreifach dokumentiert (Byte-273-PE-Baustempel, Modulreihenfolge) und wird hier nicht erneut per Zweitlauf gepruft.
NAECHSTER: qa-engineer / power-user (clean-room), sofern vom director angestossen. Kein Programmstart in diesem Lauf.
BLOCKIERT DURCH: nichts fuer diesen Bau - siehe Pflichtlektuere unten.

---

# T-253 - Bau 1.11.0

## Kontraktblock

| | |
|---|---|
| **Pfad** | `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe` |
| **Groesse** | 59.105.391 Byte (56,37 MiB) |
| **SHA-256** | `F23EB0F784665A8C018C19F353AD114E9809061033076311DCDF21DBB916E8E0` (64 Zeichen, `sha256sum` und `certutil -hashfile … SHA256` stimmen ueberein) |
| **Commit** | `08ddba6c1deddd53b510a33fcdb3d70e42474101` ("chore(version): Version auf 1.11.0 angehoben"), Branch `docs/audit-and-advisor-design` |
| **Dauer** | 1 Min 1,7 s (`time pyinstaller …`) |
| **UPX** | nicht im `PATH` (`where upx`: "Could not find files for the given pattern(s)") - `upx=True` im `.spec` bleibt wirkungslos, wie in jedem vorherigen Bau |
| **`check_licences.py`** | `OK`, exit 0 - alle drei Pflichtdateien und alle sechs Bibliotheken erfasst |

## Pflichtlektuere: `docs/legal/AUFLAGEN.md` selbst geprueft

Volltext gelesen (445 Zeilen, Stand nach QA-243-Aufloesung, letzter Nachtrag 14.09.). Kein Eintrag der gesamten Tabelle (A-001 bis A-036) traegt Ampel ROT mit Status `offen`:
- **A-010** ist ROT, aber ausdruecklich "sperrt nicht mehr" - vom Nutzer zurueckgestellt (02.09., Abnahme 09.09.).
- **A-020, A-033** sind erfuellt/abgenommen bzw. ausgefuehrt - sperren laut Register den Bau nicht.
- **A-025** (GRAU, Weitergabe der EXE) ist entschieden (FORTSETZEN, 09.09.) und sperrt ohnehin nur das Release, nicht den Bau - dieser Auftrag schliesst Weitergabe ohnehin aus (kein Commit, kein Programmstart durch mich, kein Push).
- Datei selbst haelt fest (Z. 267, 331): "Keine Auflage steht auf ROT." Fuer den lokal gebauten, nicht weitergegebenen Fall (Abschnitt Z. 325-445) greift heute nur A-032 (Schwellenwaechter, kein Ereignis ausgeloest durch diesen Bau).

Damit ist `build` nicht gesperrt. `git log -1 -- docs/legal/AUFLAGEN.md` zeigt keinen Aenderungs-Commit nach HEAD `08ddba6` - die Datei war waehrend dieses Laufs nicht in Bearbeitung.

## Ausgangsstand

`git status --porcelain` vor dem ersten Schritt: leer, sauberer Arbeitsstand. HEAD `08ddba6` entspricht exakt dem beauftragten Stand ("Version auf 1.11.0 angehoben"). `.venv` liegt aus frueheren Laeufen vor: Python 3.12.10, `pyinstaller --version` -> `6.21.0` (gepinnte Version aus `requirements.txt`), unveraendert.

## `dist/` war frei - anders als T-249

`tasklist` zeigte vor dem Bau **keinen** laufenden `NightreignHelper.exe`-Prozess (anders als in T-249, wo der qa-engineer zwei Instanzen hielt). `dist/` und `build/` liessen sich vollstaendig loeschen (`rm -rf dist build`, rc=0, beide Verzeichnisse danach nicht mehr vorhanden) - echter Kaltstart, keine Abweichung vom Referenzablauf noetig.

## Bau, ein Lauf

| | Lauf |
|---|---|
| `rc` | 0 |
| Dauer | 1 Min 1,7 s |
| Groesse | 59.105.391 Byte |
| SHA-256 | `F23EB0F784665A8C018C19F353AD114E9809061033076311DCDF21DBB916E8E0` |

Zweiter Lauf entfallen, wie im Auftrag verlangt ("ein Lauf") - Nicht-Bit-Identitaet ist in T-241 bereits dreifach belegt (Byte-273-PE-Baustempel, Modulreihenfolgen-Vertauschung im `Analysis-00.toc`, `ROLLOUT.md:255-267`). Hier nicht erneut per zweitem Lauf/`cmp` nachgewiesen.

Warnungsdatei (`build/NightreignHelper/warn-NightreignHelper.txt`) 37 Zeilen - gleiche Anzahl wie in allen vorherigen Bauten (T-241, T-249); `grep -iE "error|deprecat"` liefert 0 Treffer.

Dauer 1 Min 1,7 s liegt zwischen den 36-41 s der T-241-Laeufe und den 1 Min 15 s aus T-249 (dort mit zwei parallelen qa-engineer-Prozessen). Keine Auffaelligkeit.

## Blocker

Keiner fuer diesen Bau.

## Risiken

- Kein UPX auf diesem Bau-Wirt - unveraendert gegenueber allen bisherigen Laeufen.
- Nur ein Lauf: die interne Reproduzierbarkeit dieses konkreten Artefakts wurde in diesem Auftrag nicht erneut per Zwei-Lauf-Vergleich nachgewiesen, sondern aus T-241 (drei Vorlaeufe, alle nicht bit-identisch mit dokumentierter Ursache) uebernommen.

## Ungeprueft

- Clean-Room-Installation, Update-Pfad, Rauchtest mit Datenumlenkung - nicht Teil dieses Auftrags (`kein Programmstart`).
- Windows ARM64, Windows 8.1/aelter, Linux/macOS - kein Ziel laut `CLAUDE.md`.

## An `developer`

Keine neuen Befunde im Anwendungscode.

## An `power-user` (Ausgangspunkt, falls angefordert)

- **Pfad:** `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe`
- **Groesse:** 59.105.391 Byte (56,37 MiB)
- **SHA-256:** `F23EB0F784665A8C018C19F353AD114E9809061033076311DCDF21DBB916E8E0`
- **Versionsressource:** 1.11.0 (aus `nrplanner/__init__.py`, ungeprueft am Fenstertitel - kein Rauchtest in diesem Lauf, Auftrag verlangt ihn nicht)
- Drei Umlenkungen zwingend beim Start: `NIGHTREIGN_SETTINGS_ORG`, `LOCALAPPDATA`, `APPDATA` - Testabzug kopieren, nicht darauf zeigen (`CLAUDE.md`).
- Keine parallele Instanz zum Zeitpunkt dieses Laufs bekannt (anders als bei T-249) - vor eigenem Start trotzdem selbst mit `tasklist` pruefen.

## An `director`

**Empfehlung: freigeben mit benannter Einschraenkung** (fuer den Weiterlauf zu qa-engineer/power-user - kein Release-Votum, das bleibt an A-025 und den Nutzerauftrag "keine Weitergabe" gebunden).

Zu entscheiden/zur Kenntnis:
1. Kein `.gitignore`-Nachtrag noetig (`dist/`, `build/` bereits erfasst).
2. Keine offene rote Auflage - Build war nicht gesperrt (siehe Pflichtlektuere oben).
