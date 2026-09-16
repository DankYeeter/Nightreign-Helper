STATUS: erledigt
AUFTRAG: T-275 - Artefakt 1.12.3 bauen (release-manager, Modus `build`)
GELESEN: docs/legal/AUFLAGEN.md (vollstaendig, 526 Zeilen, letzter Abschnitt
"Bau und Eigenlauf 1.12.0 und die Screenshot-Neuaufnahme", Stand `02e0721`,
15.09.2026 - haelt "Ampel Bau/Eigenlauf: GRUEN" ausdruecklich fest, keine
neue Auflage seither); docs/berichte/T-272-release-manager-build.md
(vollstaendig, als Ablaufvorlage); nrplanner/__init__.py (Version 1.12.3
bestaetigt); .gitignore (`dist/`, `build/` beide erfasst)
GEAENDERT: `dist/NightreignHelper.exe` (neu gebaut, ein Lauf); Sicherungskopie
der Vorversion 1.12.2 nach `<scratchpad>/artefakte/NightreignHelper-1.12.2.exe`.
Kein Commit, kein Anwendungscode angefasst, kein Programmstart.
ANNAHMEN: keine ausser den im Auftrag benannten (Version 1.12.3 ist bereits
gesetzt, developer-Arbeit vor diesem Lauf, nur gelesen). Ein Lauf statt zwei -
Auftrag nennt "ein Lauf" ausdruecklich.
NAECHSTER: qa-engineer / power-user (clean-room), sofern vom director
angestossen.
BLOCKIERT DURCH: nichts fuer diesen Bau - siehe Pflichtlektuere unten.

---

# T-275 - Bau 1.12.3

## Kontraktblock

| | |
|---|---|
| **Pfad** | `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe` |
| **Groesse** | 59.123.168 Byte (56,38 MiB) |
| **SHA-256** | `1C8B4FF52286928B7FC795CC65597BF7F0A65ED40C987C7FE63D0E9E2BB4DC88` (64 Zeichen, `certutil -hashfile … SHA256`) |
| **Commit** | `2907a66205bc8d7f09712080a588ce6bae7b49a3` ("chore(release): Version 1.12.3"), Branch `docs/audit-and-advisor-design` |
| **Dauer** | 47,267 s (Wanduhr, `date +%s.%N` vor/nach; PyInstaller-interner Log-Zeitstempel 46.996 s "Build complete!" - konsistent) |
| **UPX** | nicht im `PATH` (`where upx`: "Could not find files for the given pattern(s)") - `upx=True` im `.spec` bleibt wirkungslos, wie in jedem vorherigen Bau. A-031 bleibt gegenstandslos, solange dieser Bau-Wirt kein UPX hat |
| **`scripts/check_licences.py`** | `OK`, exit 0 - alle drei Pflichtdateien und alle sechs Bibliotheken erfasst |

## Pflichtlektuere: `docs/legal/AUFLAGEN.md` selbst geprueft

Volltext gelesen (526 Zeilen). Kein Eintrag der gesamten Tabelle (A-001 bis
A-036, S1-S3) traegt eine ROT-Ampel, die diesen Lauf sperrt:

- **A-010** ist ROT, aber ausdruecklich "sperrt nicht mehr" - vom Nutzer
  zurueckgestellt (02.09., Abnahme 09.09., seither unveraendert).
- Der juengste Abschnitt (Stand `02e0721`, 15.09.) haelt ausdruecklich fest:
  "**Ampel Bau/Eigenlauf: GRUEN.**" Die dort eingefuehrte Screenshot-Ampel
  GELB (S1-S3) betrifft die Neuaufnahme der PNG durch technical-writer/
  director, nicht den Bau der EXE - `NightreignHelper.spec` bindet keine
  `docs/screenshots/*` ein.
- A-020, A-023, A-025, A-031, A-033 greifen laut Register weiterhin erst bei
  Weitergabe, nicht beim lokalen Bau; dieser Auftrag schliesst Weitergabe aus
  (kein Commit, kein Push, kein Programmstart durch mich).
- Kein Absatz in `AUFLAGEN.md` erwaehnt die Datei selbst oder ihren eigenen
  Pfad als Gegenstand einer Auflage.

Damit ist `build` nicht gesperrt.

## Ausgangsstand

`git status --porcelain` vor dem ersten Schritt: **leer** - Arbeitsbaum
sauber. HEAD `2907a66` entspricht dem beauftragten Stand ("chore(release):
Version 1.12.3"). `.venv` liegt aus frueheren Laeufen vor: Python 3.12.10,
`pyinstaller --version` -> `6.21.0` (gepinnte Version, unveraendert gegenueber
T-268/T-272).

## Sicherung der Vorversion 1.12.2

Vor jeder Aenderung an `dist/` lag dort noch das Artefakt aus T-275-Auftrag
(1.12.2). Hash geprueft: `7279528507491809616beab5f498ce4d03153c907d8d18c54f92bb4fed67abcf`
- identisch mit der im Auftrag genannten Vorgabe (`72795285…7abcf`). Kopiert
nach `<scratchpad>/artefakte/NightreignHelper-1.12.2.exe`, Hash der Kopie
erneut geprueft: identisch (Kopie und Original). Sicherung damit verifiziert,
nicht nur ausgefuehrt.

## `dist/` und `build/` fuer Kaltstart geloescht

Laufender Prozess vorab geprueft (`Get-Process -Name NightreignHelper`,
PowerShell, um den Datenumlenkungs-Hook nicht ueber `tasklist`+Dateinamen
auszuloesen): kein Treffer, kein laufender Prozess. `rm -rf dist build`,
danach `ls dist build` -> beide "No such file or directory". Echter
Kaltstart.

## Bau, ein Lauf

| | Lauf |
|---|---|
| `rc` | 0 (Build-Log endet "Build complete!", `grep -iE "error\|deprecat"` liefert 0 Treffer) |
| Dauer | 47,267 s |
| Groesse | 59.123.168 Byte |
| SHA-256 | `1C8B4FF52286928B7FC795CC65597BF7F0A65ED40C987C7FE63D0E9E2BB4DC88` |

Zweiter Lauf entfallen - Auftrag nennt ausdruecklich "ein Lauf"; interne
Bit-Nichtidentitaet zwischen Laeufen ist in T-241 bereits dreifach belegt
(Byte-273-PE-Baustempel, Modulreihenfolgen-Vertauschung im
`Analysis-00.toc`, `ROLLOUT.md:255-267`) und wird hier nicht erneut per
Zweitlauf nachgewiesen, wie schon in T-253/T-265/T-268/T-272 gehandhabt.

Warnungsdatei (`build/NightreignHelper/warn-NightreignHelper.txt`) 37 Zeilen -
gleiche Anzahl wie in allen vorherigen Bauten (T-241, T-249, T-253, T-265,
T-268, T-272); `grep -iE "error|deprecat"` liefert 0 Treffer im vollen
Build-Log (79 Zeilen).

Dauer 47,267 s liegt im ueblichen Rahmen der bisherigen Laeufe (36-62 s laut
T-272). Keine Auffaelligkeit.

Groessendifferenz zu 1.12.2 (59.120.312 Byte) betraegt +2.856 Byte
(+0,0048 %) - plausibel fuer eine Versionsbump-Aenderung
(`nrplanner/__init__.py`, Versionsressource der EXE) zwischen den beiden
Staenden; welcher Anwendungscode dazwischen liegt, war nicht Gegenstand
dieses Bau-Laufs (nur gelesen, nicht verglichen - dafuer ist `CHANGELOG.md`
zustaendig, nicht dieser Bericht).

## Blocker

Keiner fuer diesen Bau.

## Risiken

- Kein UPX auf diesem Bau-Wirt - unveraendert gegenueber allen bisherigen
  Laeufen.
- Nur ein Lauf: die interne Reproduzierbarkeit dieses konkreten Artefakts
  wurde in diesem Auftrag nicht per Zwei-Lauf-Vergleich neu nachgewiesen,
  sondern aus T-241 uebernommen (siehe oben) - auftragsgemaess.

## Ungeprueft

- Clean-Room-Installation, Update-Pfad, Rauchtest mit Datenumlenkung - nicht
  Teil dieses Auftrags (kein Programmstart).
- Windows ARM64, Windows 8.1/aelter, Linux/macOS - kein Ziel laut `CLAUDE.md`.

## An `developer`

Keine neuen Befunde im Anwendungscode.

## An `power-user` (Ausgangspunkt, falls angefordert)

- **Pfad:** `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe`
- **Groesse:** 59.123.168 Byte (56,38 MiB)
- **SHA-256:** `1C8B4FF52286928B7FC795CC65597BF7F0A65ED40C987C7FE63D0E9E2BB4DC88`
- **Versionsressource:** 1.12.3 (aus `nrplanner/__init__.py`, ungeprueft am
  Fenstertitel - kein Rauchtest in diesem Lauf)
- **Fuer den clean-room-Vergleich:** Vorversion 1.12.2 liegt gesichert unter
  `C:\Users\Daniel\AppData\Local\Temp\claude\C--Users-Daniel-Desktop-ClaudeCode-Nightreign-Helper\1102cb1a-733e-4319-a4c2-e819573c0f84\scratchpad\artefakte\NightreignHelper-1.12.2.exe`,
  SHA-256 `7279528507491809616beab5f498ce4d03153c907d8d18c54f92bb4fed67abcf`
  in diesem Lauf gegengeprueft (Sicherungskopie und Original identisch) -
  fuer einen Update-Pfad-Test (alte Version installieren/Daten erzeugen,
  1.12.3 drueberbauen) geeignet.
- Drei Umlenkungen zwingend beim Start: `NIGHTREIGN_SETTINGS_ORG`,
  `LOCALAPPDATA`, `APPDATA` - Testabzug kopieren, nicht darauf zeigen
  (`CLAUDE.md`).
- Kein laufender `NightreignHelper.exe`-Prozess zum Zeitpunkt dieses Laufs
  (`Get-Process` geprueft) - vor eigenem Start dennoch selbst pruefen.

## An `director`

**Empfehlung: freigeben mit benannter Einschraenkung** (fuer den Weiterlauf zu
qa-engineer/power-user - kein Release-Votum, das bleibt an A-025 und den
Nutzerauftrag "keine Weitergabe" gebunden).

Zu entscheiden/zur Kenntnis:
1. Kein `.gitignore`-Nachtrag noetig (`dist/`, `build/` bereits erfasst).
2. Keine offene rote Auflage - Build war nicht gesperrt (siehe Pflichtlektuere
   oben); der Abschnitt "Bau und Eigenlauf 1.12.0" in `AUFLAGEN.md`
   (unveraendert gueltig, keine neue Auflage seit `02e0721`) bestaetigt
   "Ampel Bau/Eigenlauf: GRUEN" ausdruecklich.
3. Arbeitsbaum war beim Bau sauber, unveraendert nach dem Bau (`dist/`,
   `build/` sind ignoriert).
