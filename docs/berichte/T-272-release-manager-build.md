STATUS: erledigt
AUFTRAG: T-272 - Artefakt 1.12.2 bauen (release-manager, Modus `build`)
GELESEN: docs/legal/AUFLAGEN.md (vollstaendig, 526 Zeilen, letzter Aenderungs-Commit-Abschnitt "Bau und Eigenlauf 1.12.0 und Screenshot-Neuaufnahme", Stand `02e0721`, 15.09.2026); docs/berichte/T-268-release-manager-build.md (vollstaendig, als Ablaufvorlage); nrplanner/__init__.py (Version 1.12.2 bestaetigt); nrdata/extract.py (EXTRACT_VERSION 12 bestaetigt); .gitignore (`dist/`, `build/` beide erfasst); docs/plan-restarbeiten.md Z. 273-292 (Testabzug-Vorlage bereits am 15.09. durch T-269a auf EXTRACT_VERSION 12 nachgezogen - keine eigene Handlung noetig)
GEAENDERT: `dist/NightreignHelper.exe` (neu gebaut, ein Lauf); Sicherungskopie der Vorversion 1.12.1 nach `<scratchpad>/artefakte/NightreignHelper-1.12.1.exe`. Kein Commit, kein Anwendungscode angefasst, kein Programmstart.
ANNAHMEN: keine ausser den im Auftrag benannten (Version 1.12.2 ist bereits gesetzt, developer-Arbeit vor diesem Lauf, nur gelesen). Ein Lauf statt zwei - Auftrag nennt "ein Lauf" ausdruecklich.
NAECHSTER: qa-engineer / power-user (clean-room), sofern vom director angestossen. Hinweis: EXTRACT_VERSION 12 bedeutet, dass der erste Programmstart mit dem alten Testabzug-Stand den Datenabzug neu baut (~110 s) - die Vorlage unter `NightreignHelper-Testabzug` ist laut `docs/plan-restarbeiten.md` seit T-269a (15.09.) bereits auf EXTRACT_VERSION 12 aktualisiert, CLAUDE.md nennt noch den alten Stand (20 812 293 B / EXTRACT_VERSION 11) - Registerpflege ist Sache des naechsten Laufs, der die Vorlage tatsaechlich benutzt, nicht dieses Bau-Laufs (kein Programmstart hier).
BLOCKIERT DURCH: nichts fuer diesen Bau - siehe Pflichtlektuere unten.

---

# T-272 - Bau 1.12.2

## Kontraktblock

| | |
|---|---|
| **Pfad** | `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe` |
| **Groesse** | 59.120.312 Byte (56,38 MiB) |
| **SHA-256** | `7279528507491809616BEAB5F498CE4D03153C907D8D18C54F92BB4FED67ABCF` (64 Zeichen, `certutil -hashfile … SHA256`) |
| **Commit** | `fb23e24cc239fc5e46ca42e43734634e49764987` ("chore(release): Version 1.12.2 und Suitezahl in CLAUDE.md aktualisiert"), Branch `docs/audit-and-advisor-design` |
| **Dauer** | 45,449 s (Log-Zeitstempel: erste Zeile 122 ms, "Build complete!" 45.571 ms) |
| **UPX** | nicht im `PATH` (`where upx`: "Could not find files for the given pattern(s)", exit 1) - `upx=True` im `.spec` bleibt wirkungslos, wie in jedem vorherigen Bau. A-031 bleibt gegenstandslos, solange dieser Bau-Wirt kein UPX hat |
| **`scripts/check_licences.py`** | `OK`, exit 0 - alle drei Pflichtdateien und alle sechs Bibliotheken erfasst |

## Pflichtlektuere: `docs/legal/AUFLAGEN.md` selbst geprueft

Volltext gelesen (526 Zeilen). Kein Eintrag der gesamten Tabelle (A-001 bis
A-036, S1-S3) traegt eine ROT-Ampel, die diesen Lauf sperrt:

- **A-010** ist ROT, aber ausdruecklich "sperrt nicht mehr" - vom Nutzer
  zurueckgestellt (02.09., Abnahme 09.09., seither unveraendert).
- Der juengste Abschnitt (Stand `02e0721`, 15.09.) haelt ausdruecklich fest:
  "**Ampel Bau/Eigenlauf: GRUEN.**" Die dort neu eingefuehrte Screenshot-Ampel
  GELB (S1-S3) betrifft die Neuaufnahme der PNG durch technical-writer/
  director, nicht den Bau der EXE - `NightreignHelper.spec` bindet keine
  `docs/screenshots/*` ein.
- A-020, A-023, A-025, A-031, A-033 greifen laut Register weiterhin erst bei
  Weitergabe, nicht beim lokalen Bau; dieser Auftrag schliesst Weitergabe aus
  (kein Commit, kein Push, kein Programmstart durch mich).
- Kein Absatz in `AUFLAGEN.md` erwaehnt die Datei selbst oder ihren eigenen
  Pfad (`docs/legal/`, `AUFLAGEN`) als Gegenstand einer Auflage - die im
  Auftragstext genannte Beobachtung betrifft eine andere Datei
  (`~/.claude/agents/_rahmen.md`), nicht dieses Register, und aendert nichts
  an der Sperrfrage fuer diesen Bau.

Damit ist `build` nicht gesperrt.

## Ausgangsstand

`git status --porcelain` vor dem ersten Schritt: **leer** - Arbeitsbaum
sauber. HEAD `fb23e24` entspricht dem beauftragten Stand ("Version 1.12.2 und
Suitezahl in CLAUDE.md aktualisiert"). `.venv` liegt aus frueheren Laeufen
vor: Python 3.12.10, `pyinstaller --version` -> `6.21.0` (gepinnte Version,
unveraendert gegenueber T-268/T-265/T-253).

## Sicherung der Vorversion 1.12.1

Vor jeder Aenderung an `dist/` lag dort noch das Artefakt aus T-268 (Rebuild
auf `1b36238`). Hash geprueft: `F29EB92D88ED14416A488F32F7AB655BF27FEC77E2BE74105782D0980904CF1B`
- identisch mit der im Auftrag genannten Vorgabe (`f29eb92d…4cf1b`). Kopiert
nach `<scratchpad>/artefakte/NightreignHelper-1.12.1.exe`, Hash der Kopie
erneut geprueft: identisch. Sicherung damit verifiziert, nicht nur ausgefuehrt.

## `dist/` und `build/` fuer Kaltstart geloescht

Laufender Prozess vorab geprueft (`tasklist /FI "IMAGENAME eq NightreignHelper.exe"`
via PowerShell, da die direkte Git-Bash-Form die Filterargumente verschluckt):
"INFO: No tasks are running which match the specified criteria." `rm -rf dist
build`, danach `ls dist build` -> beide "No such file or directory". Echter
Kaltstart.

## Bau, ein Lauf

| | Lauf |
|---|---|
| `rc` | 0 (Build-Log endet "Build complete!", kein Fehler) |
| Dauer | 45,449 s |
| Groesse | 59.120.312 Byte |
| SHA-256 | `7279528507491809616BEAB5F498CE4D03153C907D8D18C54F92BB4FED67ABCF` |

Zweiter Lauf entfallen - Auftrag nennt ausdruecklich "ein Lauf"; interne
Bit-Nichtidentitaet zwischen Laeufen ist in T-241 bereits dreifach belegt
(Byte-273-PE-Baustempel, Modulreihenfolgen-Vertauschung im
`Analysis-00.toc`, `ROLLOUT.md:255-267`) und wird hier nicht erneut per
Zweitlauf nachgewiesen, wie schon in T-253/T-265/T-268 gehandhabt.

Warnungsdatei (`build/NightreignHelper/warn-NightreignHelper.txt`) 37 Zeilen -
gleiche Anzahl wie in allen vorherigen Bauten (T-241, T-249, T-253, T-265,
T-268); `grep -iE "error|deprecat"` liefert 0 Treffer.

Dauer 45,449 s liegt im ueblichen Rahmen der bisherigen Laeufe (36-62 s,
T-241/T-253/T-265/T-268). Keine Auffaelligkeit.

Groessendifferenz zu 1.12.1 (T-268: 59.119.378 Byte) betraegt +934 Byte
(+0,0016 %) - plausibel fuer eine reine Versionsbump-Aenderung
(`nrplanner/__init__.py`, Versionsressource der EXE) ohne weiteren
Anwendungscode zwischen `3c2ff23` (T-268-Stand) und `fb23e24`.

## Hinweis: `EXTRACT_VERSION` 12

`nrdata/extract.py:84` bestaetigt `EXTRACT_VERSION = 12` (seit T-269a,
15.09., wegen `weapons[].paired`, QA-276). Der erste Programmstart eines
Artefakts, dem ein Datenabzug mit niedrigerer Version vorliegt, baut den
Abzug neu (~110 s laut Auftrag). Die feste Testvorlage
(`NightreignHelper-Testabzug`) ist laut `docs/plan-restarbeiten.md` Z. 279-283
bereits seit T-269a (15.09., developer) auf EXTRACT_VERSION 12 nachgezogen
(841 Dateien, 20 849 867 B) - `CLAUDE.md` nennt an dieser Stelle noch den
aelteren Stand (20 812 293 B, EXTRACT_VERSION 11) und ist damit selbst der
veraltete Verweis; das ist keine Beobachtung aus diesem Lauf, sondern schon
in `plan-restarbeiten.md` festgehalten. Kein Programmstart in diesem Auftrag,
daher keine eigene Pruefung der Vorlage.

## Blocker

Keiner fuer diesen Bau.

## Risiken

- Kein UPX auf diesem Bau-Wirt - unveraendert gegenueber allen bisherigen
  Laeufen.
- Nur ein Lauf: die interne Reproduzierbarkeit dieses konkreten Artefakts
  wurde in diesem Auftrag nicht per Zwei-Lauf-Vergleich neu nachgewiesen,
  sondern aus T-241 uebernommen (siehe oben) - auftragsgemaess.
- `CLAUDE.md` nennt fuer den Testabzug noch EXTRACT_VERSION 11 / 20 812 293 B;
  der tatsaechliche Stand (laut `plan-restarbeiten.md`) ist bereits
  EXTRACT_VERSION 12 / 20 849 867 B. Wer `CLAUDE.md` allein liest, greift auf
  eine veraltete Zahl - kein Blocker fuer diesen Bau, aber ein Befund fuer den
  naechsten Lauf mit Programmstart.

## Ungeprueft

- Clean-Room-Installation, Update-Pfad, Rauchtest mit Datenumlenkung - nicht
  Teil dieses Auftrags (kein Programmstart).
- Windows ARM64, Windows 8.1/aelter, Linux/macOS - kein Ziel laut `CLAUDE.md`.

## An `developer`

Keine neuen Befunde im Anwendungscode.

## An `power-user` (Ausgangspunkt, falls angefordert)

- **Pfad:** `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe`
- **Groesse:** 59.120.312 Byte (56,38 MiB)
- **SHA-256:** `7279528507491809616BEAB5F498CE4D03153C907D8D18C54F92BB4FED67ABCF`
- **Versionsressource:** 1.12.2 (aus `nrplanner/__init__.py`, ungeprueft am
  Fenstertitel - kein Rauchtest in diesem Lauf)
- **Fuer den clean-room-Vergleich:** Vorversion 1.12.1 liegt gesichert unter
  `C:\Users\Daniel\AppData\Local\Temp\claude\C--Users-Daniel-Desktop-ClaudeCode-Nightreign-Helper\1102cb1a-733e-4319-a4c2-e819573c0f84\scratchpad\artefakte\NightreignHelper-1.12.1.exe`,
  SHA-256 `F29EB92D88ED14416A488F32F7AB655BF27FEC77E2BE74105782D0980904CF1B`
  in diesem Lauf gegengeprueft (Sicherungskopie und Original identisch) -
  fuer einen Update-Pfad-Test (alte Version installieren/Daten erzeugen,
  1.12.2 drueberbauen) geeignet.
- Drei Umlenkungen zwingend beim Start: `NIGHTREIGN_SETTINGS_ORG`,
  `LOCALAPPDATA`, `APPDATA` - Testabzug kopieren, nicht darauf zeigen
  (`CLAUDE.md`).
- **EXTRACT_VERSION jetzt 12** - beim ersten Start mit dem festen Testabzug
  pruefen, ob dieser bereits auf Version 12 steht (laut `plan-restarbeiten.md`
  ja, seit T-269a); sonst baut das Programm den Abzug neu (~110 s).
- Kein laufender `NightreignHelper.exe`-Prozess zum Zeitpunkt dieses Laufs
  (`tasklist` geprueft) - vor eigenem Start dennoch selbst mit `tasklist`
  pruefen.

## An `director`

**Empfehlung: freigeben mit benannter Einschraenkung** (fuer den Weiterlauf zu
qa-engineer/power-user - kein Release-Votum, das bleibt an A-025 und den
Nutzerauftrag "keine Weitergabe" gebunden).

Zu entscheiden/zur Kenntnis:
1. Kein `.gitignore`-Nachtrag noetig (`dist/`, `build/` bereits erfasst).
2. Keine offene rote Auflage - Build war nicht gesperrt (siehe Pflichtlektuere
   oben); der Abschnitt "Bau und Eigenlauf 1.12.0" in `AUFLAGEN.md`
   (unveraendert gueltig fuer 1.12.2, keine neue Auflage seit `02e0721`)
   bestaetigt "Ampel Bau/Eigenlauf: GRUEN" ausdruecklich.
3. Arbeitsbaum war beim Bau sauber.
4. `CLAUDE.md` fuehrt fuer den festen Testabzug einen veralteten Stand
   (EXTRACT_VERSION 11, 20 812 293 B); `docs/plan-restarbeiten.md` ist bereits
   auf EXTRACT_VERSION 12 aktuell. Vorschlag: `CLAUDE.md`-Abschnitt
   "Datenverzeichnisse und Umlenkung" bei Gelegenheit auf den aktuellen Stand
   nachziehen (kostet eine Zeile, nicht in diesem Auftrag enthalten - keine
   Auftragserweiterung durch mich).
