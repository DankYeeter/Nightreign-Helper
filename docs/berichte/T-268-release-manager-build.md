STATUS: erledigt
AUFTRAG: T-268 - Artefakt 1.12.1 bauen (release-manager, Modus `build`)
GELESEN: docs/legal/AUFLAGEN.md (vollstaendig, 526 Zeilen, Stand `9f19628`/T-265b, selbst nachgeprueft - siehe unten); docs/berichte/T-265-release-manager-build.md (vollstaendig, als Ablaufvorlage); nrplanner/__init__.py (Version 1.12.1 bestaetigt); NightreignHelper.spec (unveraendert); .gitignore (`dist/`, `build/` beide erfasst)
GEAENDERT: `dist/NightreignHelper.exe` (neu gebaut, ein Lauf); Sicherungskopie der Vorversion 1.12.0 nach `<scratchpad>/artefakte/NightreignHelper-1.12.0.exe`. Kein Commit, kein Anwendungscode angefasst, kein Programmstart.
ANNAHMEN: keine ausser den im Auftrag benannten (Version 1.12.1 ist bereits gesetzt, developer-Arbeit vor diesem Lauf, nur gelesen). Ein Lauf statt zwei - Auftrag nennt "ein Lauf" ausdruecklich.
NAECHSTER: qa-engineer / power-user (clean-room), sofern vom director angestossen.
BLOCKIERT DURCH: nichts fuer diesen Bau - siehe Pflichtlektuere unten.

---

# T-268 - Bau 1.12.1

## Kontraktblock

| | |
|---|---|
| **Pfad** | `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe` |
| **Groesse** | 59.119.378 Byte (56,38 MiB) |
| **SHA-256** | `F29EB92D88ED14416A488F32F7AB655BF27FEC77E2BE74105782D0980904CF1B` (64 Zeichen, `certutil -hashfile … SHA256`) |
| **Commit** | `3c2ff23f2f9341c3000a51884be9652d2687d0b5` ("chore(release): Version auf 1.12.1 angehoben"), Branch `docs/audit-and-advisor-design` |
| **Dauer** | 42,0 s (`time pyinstaller …`) |
| **UPX** | nicht im `PATH` (`where upx`: "Could not find files for the given pattern(s)") - `upx=True` im `.spec` bleibt wirkungslos, wie in jedem vorherigen Bau. A-031 bleibt gegenstandslos, solange dieser Bau-Wirt kein UPX hat |
| **`scripts/check_licences.py`** | `OK`, exit 0 - alle drei Pflichtdateien und alle sechs Bibliotheken erfasst (Pfad korrigiert gegenueber T-265: das Skript liegt unter `scripts/`, nicht im Repo-Root) |

## Pflichtlektuere: `docs/legal/AUFLAGEN.md` selbst geprueft

Volltext gelesen (526 Zeilen, letzter Aenderungs-Commit `9f19628`, "T-265b Auflagen 1.12.0 GRUEN, Screenshots GELB (S1-S3)"). Kein Eintrag der gesamten Tabelle (A-001 bis A-036, S1-S3) traegt Ampel ROT mit sperrendem Status:
- **A-010** ist ROT, aber ausdruecklich "sperrt nicht mehr" - vom Nutzer zurueckgestellt (02.09., Abnahme 09.09.), im 1.12.0-Abschnitt erneut bestaetigt.
- Der juengste Abschnitt selbst haelt fest: "**Ampel Bau/Eigenlauf: GRUEN.**" Die Screenshot-Ampel GELB (S1-S3) betrifft die Neuaufnahme der PNG durch den technical-writer, nicht den Bau der EXE - `NightreignHelper.spec` bindet keine `docs/screenshots/*` ein.
- A-020, A-025, A-033 greifen laut Register weiterhin erst bei Weitergabe, nicht beim lokalen Bau; dieser Auftrag schliesst Weitergabe aus (kein Commit, kein Push, kein Programmstart durch mich).
- `git log -1 -- docs/legal/AUFLAGEN.md` zeigt `9f19628` als letzten Aenderungs-Commit, vor HEAD `3c2ff23` - die Datei war waehrend dieses Laufs nicht in Bearbeitung.

Damit ist `build` nicht gesperrt.

## Ausgangsstand

`git status --porcelain` vor dem ersten Schritt: **leer** - Arbeitsbaum sauber, kein uncommitteter Rest (Unterschied zu T-265, wo acht Dateien parallel vom technical-writer bearbeitet wurden). HEAD `3c2ff23` entspricht dem beauftragten Stand ("Version auf 1.12.1 angehoben"). `.venv` liegt aus frueheren Laeufen vor: Python 3.12.10, `pyinstaller --version` -> `6.21.0` (gepinnte Version, unveraendert gegenueber T-265/T-253).

## Sicherung der Vorversion 1.12.0

Vor jeder Aenderung an `dist/` lag dort noch das Artefakt aus T-265 (Datum 15.09. 04:58). Hash geprueft: `89c2967acaaaaac8ca108935cac0a79c8292d2c7ec0e77831755a15b295f59d8` - identisch mit der im Auftrag genannten Vorgabe (`89c2967a…f59d8`). Kopiert nach `<scratchpad>/artefakte/NightreignHelper-1.12.0.exe`, Hash der Kopie erneut gepruft: identisch. Sicherung damit verifiziert, nicht nur ausgefuehrt.

## `dist/` und `build/` fuer Kaltstart geloescht

`tasklist /FI "IMAGENAME eq NightreignHelper.exe"` zeigte vor und nach dem Bau **keinen** laufenden Prozess. `rm -rf dist build`, danach `ls dist build` -> beide "No such file or directory". Echter Kaltstart.

## Bau, ein Lauf

| | Lauf |
|---|---|
| `rc` | 0 (Build-Log endet "Build complete!", kein Fehler) |
| Dauer | 42,0 s |
| Groesse | 59.119.378 Byte |
| SHA-256 | `F29EB92D88ED14416A488F32F7AB655BF27FEC77E2BE74105782D0980904CF1B` |

Zweiter Lauf entfallen - Auftrag nennt ausdruecklich "ein Lauf"; Nicht-Bit-Identitaet ist in T-241 bereits dreifach belegt (Byte-273-PE-Baustempel, Modulreihenfolgen-Vertauschung im `Analysis-00.toc`, `ROLLOUT.md:255-267`) und wird hier nicht erneut per Zweitlauf nachgewiesen, wie schon in T-253/T-265 gehandhabt.

Warnungsdatei (`build/NightreignHelper/warn-NightreignHelper.txt`) 37 Zeilen - gleiche Anzahl wie in allen vorherigen Bauten (T-241, T-249, T-253, T-265); `grep -iE "error|deprecat"` liefert 0 Treffer.

Dauer 42,0 s liegt im Rahmen der T-241-Laeufe (36-41 s) und unter T-253 (61,7 s) und T-265 (46,7 s). Keine Auffaelligkeit.

Groessendifferenz zu 1.12.0 (T-265: 59.118.289 Byte) betraegt +1.089 Byte (+0,0018 %) - plausibel fuer eine reine Versionsbump-Aenderung (`nrplanner/__init__.py`, Versionsressource der EXE) ohne weiteren Anwendungscode zwischen `79e6089` (T-265-Stand) und `3c2ff23`.

## Blocker

Keiner fuer diesen Bau.

## Risiken

- Kein UPX auf diesem Bau-Wirt - unveraendert gegenueber allen bisherigen Laeufen.
- Nur ein Lauf: die interne Reproduzierbarkeit dieses konkreten Artefakts wurde in diesem Auftrag nicht per Zwei-Lauf-Vergleich neu nachgewiesen, sondern aus T-241 uebernommen (siehe oben) - auftragsgemaess.

## Ungeprueft

- Clean-Room-Installation, Update-Pfad, Rauchtest mit Datenumlenkung - nicht Teil dieses Auftrags (kein Programmstart).
- Windows ARM64, Windows 8.1/aelter, Linux/macOS - kein Ziel laut `CLAUDE.md`.

## An `developer`

Keine neuen Befunde im Anwendungscode.

## An `power-user` (Ausgangspunkt, falls angefordert)

- **Pfad:** `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe`
- **Groesse:** 59.119.378 Byte (56,38 MiB)
- **SHA-256:** `F29EB92D88ED14416A488F32F7AB655BF27FEC77E2BE74105782D0980904CF1B`
- **Versionsressource:** 1.12.1 (aus `nrplanner/__init__.py`, ungeprueft am Fenstertitel - kein Rauchtest in diesem Lauf)
- **Fuer den clean-room-Vergleich:** Vorversion 1.12.0 liegt gesichert unter `C:\Users\Daniel\AppData\Local\Temp\claude\C--Users-Daniel-Desktop-ClaudeCode-Nightreign-Helper\1102cb1a-733e-4319-a4c2-e819573c0f84\scratchpad\artefakte\NightreignHelper-1.12.0.exe`, SHA-256 `89C2967ACAAAAAC8CA108935CAC0A79C8292D2C7EC0E77831755A15B295F59D8` in diesem Lauf gegengeprueft (Sicherungskopie und Original identisch) - fuer einen Update-Pfad-Test (alte Version installieren/Daten erzeugen, 1.12.1 drueberbauen) geeignet.
- Drei Umlenkungen zwingend beim Start: `NIGHTREIGN_SETTINGS_ORG`, `LOCALAPPDATA`, `APPDATA` - Testabzug kopieren, nicht darauf zeigen (`CLAUDE.md`).
- Kein laufender `NightreignHelper.exe`-Prozess zum Zeitpunkt dieses Laufs (`tasklist` geprueft) - vor eigenem Start dennoch selbst mit `tasklist` pruefen.

## An `director`

**Empfehlung: freigeben mit benannter Einschraenkung** (fuer den Weiterlauf zu qa-engineer/power-user - kein Release-Votum, das bleibt an A-025 und den Nutzerauftrag "keine Weitergabe" gebunden).

Zu entscheiden/zur Kenntnis:
1. Kein `.gitignore`-Nachtrag noetig (`dist/`, `build/` bereits erfasst).
2. Keine offene rote Auflage - Build war nicht gesperrt (siehe Pflichtlektuere oben); der 1.12.0-Abschnitt in `AUFLAGEN.md` (unveraendert gueltig fuer 1.12.1, keine neue Auflage seit `9f19628`) bestaetigt "Ampel Bau/Eigenlauf: GRUEN" ausdruecklich.
3. Arbeitsbaum war beim Bau sauber - keine Einschraenkung wie in T-265.
4. `scripts/check_licences.py` (nicht `check_licences.py` im Root, wie T-265 im Kontraktblock notierte) lief mit exit 0 - kleine Pfadkorrektur zur Vorlage, ohne inhaltliche Folge.
