STATUS: erledigt
AUFTRAG: T-265 - Artefakt 1.12.0 bauen (release-manager, Modus `build`)
GELESEN: docs/legal/AUFLAGEN.md (vollstaendig, 526 Zeilen, Stand `02e0721`/T-265b, selbst nachgeprueft - siehe unten); docs/berichte/T-253-release-manager-build.md (vollstaendig, als Vorlage fuer den Ablauf); nrplanner/__init__.py (Version 1.12.0 bestaetigt); NightreignHelper.spec (unveraendert gegenueber T-253); .gitignore (`dist/`, `build/` beide erfasst)
GEAENDERT: `dist/NightreignHelper.exe` (neu gebaut, ein Lauf). Kein Commit, kein Anwendungscode angefasst.
ANNAHMEN: keine ausser den im Auftrag benannten (Version 1.12.0 ist bereits gesetzt, developer-Arbeit vor diesem Lauf, nur gelesen). Ein Lauf statt zwei - Auftrag nennt keinen Zweitlauf; Nicht-Bit-Identitaet ist in T-241 bereits dreifach dokumentiert und wird hier nicht erneut per Zweitlauf geprueft.
NAECHSTER: qa-engineer / power-user (clean-room), sofern vom director angestossen. Kein Programmstart in diesem Lauf (technical-writer haelt ggf. eine Fensterinstanz).
BLOCKIERT DURCH: nichts fuer diesen Bau - siehe Pflichtlektuere unten.

---

# T-265 - Bau 1.12.0

## Kontraktblock

| | |
|---|---|
| **Pfad** | `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe` |
| **Groesse** | 59.118.289 Byte (56,38 MiB) |
| **SHA-256** | `89C2967ACAAAAAC8CA108935CAC0A79C8292D2C7EC0E77831755A15B295F59D8` (64 Zeichen, `certutil -hashfile … SHA256` und `sha256sum` stimmen ueberein) |
| **Commit** | `79e6089fa055df3bdb2d86ef227fc005ceafd2a7` ("docs(qa,security): T-265 Retest PASS - QA-272, SEC-046/047 geschlossen"), Branch `docs/audit-and-advisor-design`; enthaelt `02e0721` (Versionsbump 1.12.0) und `2640602` (SEC-046-Fix) als Vorfahren |
| **Dauer** | 46,7 s (`time pyinstaller …`) |
| **UPX** | nicht im `PATH` (`where upx`: "Could not find files for the given pattern(s)") - `upx=True` im `.spec` bleibt wirkungslos, wie in jedem vorherigen Bau. **A-031 bleibt gegenstandslos**, solange dieser Bau-Wirt kein UPX hat |
| **`check_licences.py`** | `OK`, exit 0 - alle drei Pflichtdateien und alle sechs Bibliotheken erfasst |

## Pflichtlektuere: `docs/legal/AUFLAGEN.md` selbst geprueft

Volltext gelesen (526 Zeilen, Stand nach T-265b, letzter Nachtrag 15.09., Abschnitt "Auflagen fuer Bau und Eigenlauf 1.12.0"). Kein Eintrag der gesamten Tabelle (A-001 bis A-036, S1-S3) traegt Ampel ROT mit sperrendem Status:
- **A-010** ist ROT, aber ausdruecklich "sperrt nicht mehr" - vom Nutzer zurueckgestellt (02.09., Abnahme 09.09.), im 1.12.0-Abschnitt erneut bestaetigt (Z. 480-491: "Was Daniel am 02.09. hingenommen hat, darf so bleiben").
- Der neueste Abschnitt selbst haelt fest: "**Ampel Bau/Eigenlauf: GRUEN.**" (Z. 453-454). Die Screenshot-Ampel GELB (S1-S3) betrifft die Neuaufnahme der PNG durch den technical-writer, nicht den Bau der EXE - `NightreignHelper.spec` bindet keine `docs/screenshots/*` ein.
- A-020, A-025, A-033 greifen laut Register weiterhin erst bei Weitergabe, nicht beim lokalen Bau; dieser Auftrag schliesst Weitergabe aus (kein Commit, kein Push, kein Programmstart durch mich).
- `git log -1 -- docs/legal/AUFLAGEN.md` zeigt `9f19628` als letzten Aenderungs-Commit, vor HEAD `79e6089` - die Datei war waehrend dieses Laufs nicht in Bearbeitung.

Damit ist `build` nicht gesperrt.

## Ausgangsstand

`git status --porcelain` vor dem ersten Schritt:
```
 M README.md
 M docs/screenshots/build_planner.png
 M docs/screenshots/deep_of_night.png
 M docs/screenshots/depth_weighting.png
 M docs/screenshots/effects.png
 M docs/screenshots/nightlords.png
 M docs/screenshots/weapons.png
 M docs/screenshots/world_events.png
```
Wie im Auftrag angekuendigt (technical-writer parallel, T-241b/T-265b-Nachfolgearbeit an S1-S3) - **nicht als Blocker gewertet**, weil keine der acht Dateien Eingang in `NightreignHelper.spec` findet (`datas` bindet ausschliesslich `nrplanner/data/icon.ico` und `vendor/Paramdex/NR/Defs`, gegengelesen). Das Artefakt ist von diesen Aenderungen unberuehrt. HEAD `79e6089` entspricht dem beauftragten Stand. `.venv` liegt aus frueheren Laeufen vor: Python 3.12.10, `pyinstaller --version` -> `6.21.0` (gepinnte Version), unveraendert gegenueber T-253.

## `dist/` und `build/` waren belegt - Reste aus einem frueheren Lauf

`tasklist /FI "IMAGENAME eq NightreignHelper.exe"` zeigte **keinen** laufenden Prozess. `dist/NightreignHelper.exe` und `build/NightreignHelper/` lagen von einem frueheren Lauf vor (Datum nicht dieses Laufs), liessen sich aber vollstaendig loeschen (`rm -rf dist build`, rc=0, danach nicht mehr vorhanden) - echter Kaltstart.

## Bau, ein Lauf

| | Lauf |
|---|---|
| `rc` | 0 |
| Dauer | 46,7 s |
| Groesse | 59.118.289 Byte |
| SHA-256 | `89C2967ACAAAAAC8CA108935CAC0A79C8292D2C7EC0E77831755A15B295F59D8` |

Zweiter Lauf entfallen - Nicht-Bit-Identitaet ist in T-241 bereits dreifach belegt (Byte-273-PE-Baustempel, Modulreihenfolgen-Vertauschung im `Analysis-00.toc`, `ROLLOUT.md:255-267`); hier nicht erneut per Zweitlauf nachgewiesen, wie schon in T-253 gehandhabt.

Warnungsdatei (`build/NightreignHelper/warn-NightreignHelper.txt`) 37 Zeilen - gleiche Anzahl wie in allen vorherigen Bauten (T-241, T-249, T-253); `grep -iE "error|deprecat"` liefert 0 Treffer.

Dauer 46,7 s liegt im Rahmen der T-241-Laeufe (36-41 s) und unter T-253 (61,7 s). Keine Auffaelligkeit.

Groessendifferenz zu 1.11.0 (T-253: 59.105.391 Byte) betraegt +12.898 Byte (+0,022 %) - plausibel fuer die Codeaenderungen seit 08ddba6 (SEC-046/047-Fixes, A20-Zweihand-Umschalter, Gefaess-Tooltip u. a., siehe AUFLAGEN.md-Tabelle "Neu seit 1.10.0"/1.12.0-Abschnitt).

## Blocker

Keiner fuer diesen Bau.

## Risiken

- Kein UPX auf diesem Bau-Wirt - unveraendert gegenueber allen bisherigen Laeufen.
- Nur ein Lauf: die interne Reproduzierbarkeit dieses konkreten Artefakts wurde in diesem Auftrag nicht per Zwei-Lauf-Vergleich neu nachgewiesen, sondern aus T-241 uebernommen (siehe oben).
- Acht uncommittete Dateien im Arbeitsbaum (README.md + 7 Screenshots) - vom technical-writer parallel bearbeitet, nicht Teil des Artefakts, aber der Arbeitsbaum war zum Zeitpunkt dieses Baus **nicht sauber**. Fuer die naechste Version-Notes-/Release-Vorbereitung ist zu pruefen, dass diese Aenderungen vor der Weitergabe committet sind (S1-S3, A-012 aus AUFLAGEN.md betreffen genau diese Dateien).

## Ungeprueft

- Clean-Room-Installation, Update-Pfad, Rauchtest mit Datenumlenkung - nicht Teil dieses Auftrags (kein Programmstart).
- Windows ARM64, Windows 8.1/aelter, Linux/macOS - kein Ziel laut `CLAUDE.md`.

## An `developer`

Keine neuen Befunde im Anwendungscode.

## An `power-user` (Ausgangspunkt, falls angefordert)

- **Pfad:** `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe`
- **Groesse:** 59.118.289 Byte (56,38 MiB)
- **SHA-256:** `89C2967ACAAAAAC8CA108935CAC0A79C8292D2C7EC0E77831755A15B295F59D8`
- **Versionsressource:** 1.12.0 (aus `nrplanner/__init__.py`, ungeprueft am Fenstertitel - kein Rauchtest in diesem Lauf)
- **Fuer den clean-room-Vergleich:** Vorversion 1.11.0 liegt gesichert unter `C:\Users\Daniel\AppData\Local\Temp\claude\C--Users-Daniel-Desktop-ClaudeCode-Nightreign-Helper\1102cb1a-733e-4319-a4c2-e819573c0f84\scratchpad\artefakte\NightreignHelper-1.11.0.exe`, SHA-256 `F23EB0F784665A8C018C19F353AD114E9809061033076311DCDF21DBB916E8E0` in diesem Lauf gegengeprueft (`certutil`, stimmt mit dem Auftragstext ueberein) - fuer einen Update-Pfad-Test (alte Version installieren/Daten erzeugen, 1.12.0 drueberbauen) geeignet.
- Drei Umlenkungen zwingend beim Start: `NIGHTREIGN_SETTINGS_ORG`, `LOCALAPPDATA`, `APPDATA` - Testabzug kopieren, nicht darauf zeigen (`CLAUDE.md`).
- Kein laufender `NightreignHelper.exe`-Prozess zum Zeitpunkt dieses Laufs (`tasklist` geprueft) - der Auftrag nennt eine moegliche parallele Fensterinstanz des technical-writer; vor eigenem Start selbst mit `tasklist` pruefen.

## An `director`

**Empfehlung: freigeben mit benannter Einschraenkung** (fuer den Weiterlauf zu qa-engineer/power-user - kein Release-Votum, das bleibt an A-025 und den Nutzerauftrag "keine Weitergabe" gebunden).

Zu entscheiden/zur Kenntnis:
1. Kein `.gitignore`-Nachtrag noetig (`dist/`, `build/` bereits erfasst).
2. Keine offene rote Auflage - Build war nicht gesperrt (siehe Pflichtlektuere oben); der 1.12.0-Abschnitt in `AUFLAGEN.md` bestaetigt "Ampel Bau/Eigenlauf: GRUEN" ausdruecklich.
3. Arbeitsbaum war beim Bau nicht sauber (README.md + 7 Screenshots, technical-writer parallel) - keine Auswirkung auf das Artefakt, aber vor jeder Weitergabe von 1.12.0 zu committen bzw. gegen S1-S3/A-012 abzunehmen.
