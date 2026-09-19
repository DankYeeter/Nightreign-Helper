STATUS: erledigt
AUFTRAG: T-293a - Artefakt 1.14.0 bauen (release-manager, Modus `build`)
GELESEN: docs/legal/AUFLAGEN.md (vollstaendig, 651 Zeilen; juengster Abschnitt
"Auflagen vor der Veroeffentlichung 1.13.1", Stand `1f51485`, keine Auflage auf
ROT, Bau/Eigenlauf bleibt GRUEN nach T-241a); docs/berichte/T-290-release-manager-build.md
(Vorlage); docs/tasks/T-293.md; CLAUDE.md; nrplanner/__init__.py (vor
Aenderung: 1.13.2); .gitignore (`dist/`, `build/` beide erfasst);
NightreignHelper.spec
GEAENDERT: nrplanner/__init__.py (`__version__` 1.13.2 -> 1.14.0, Commit
`565e3b9`); dist/NightreignHelper.exe (neu gebaut). Sicherungskopie der
Vorversion 1.13.2 nach `<scratchpad>/artefakte/NightreignHelper-1.13.2.exe`
(Hash gegen das im Arbeitsbaum liegende Original verifiziert, vor dem
Loeschen von `dist/`). Kein Anwendungscode angefasst.
ANNAHMEN: Versionsnummer 1.14.0 stand bereits im Auftrag fest (Feature A22/A23,
Minor-Bump) - keine eigene Entscheidung noetig.
NAECHSTER: T-293b (qa-engineer, allein am Fenster), danach T-293c/T-293d laut
Auftrag.
BLOCKIERT DURCH: nichts fuer diesen Bau.

---

# T-293a - Bau 1.14.0

## Kontraktblock

| | |
|---|---|
| **Pfad** | `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe` |
| **Groesse** | 59.213.433 Byte (56,47 MiB) |
| **SHA-256** | `79E217617481B086FD63610EB3DB0A60E1C64BDBAE15294045320D98C22FD8B4` (`sha256sum`) |
| **Versionsbump-Commit** | `565e3b9` ("chore(release): Version 1.14.0") |
| **Code-Stand des Artefakts** | `85dc0ea` (letzter Anwendungscode-/Doku-Commit vor dem Bump), Branch `docs/audit-and-advisor-design` |
| **Dauer** | 41,67 s (Wanduhr; PyInstaller-Log "Build complete!" bei 41,464 s - konsistent) |
| **UPX** | nicht im `PATH` (`where upx`: "Could not find files") - `upx=True` im `.spec` bleibt wirkungslos, wie in jedem vorherigen Bau |
| **`scripts/check_licences.py`** | `OK`, alle drei Pflichtdateien und alle sechs Bibliotheken erfasst |

## Pflichtlektuere: `docs/legal/AUFLAGEN.md`

Volltext gelesen (651 Zeilen). Kein Eintrag auf ROT, der diesen Lauf sperrt:
A-010 ist ROT, aber ausdruecklich "sperrt nicht mehr" (Nutzer-Ruecksstellung
02.09., Abnahme 09.09.). Der juengste Abschnitt (T-283c, Stand `1f51485`,
16.09.) haelt fest, dass A-020/A-023/A-030/A-031/A-035 fuer 1.13.1 erfuellt
bzw. GRUEN sind und nichts auf ROT steht; die T-241a-Einordnung
"Bau/Eigenlauf: GRUEN" gilt seither unveraendert fort. Dieser Lauf ist kein
Release (kein Push, kein Tag, keine Weitergabe der EXE) - `build` ist nicht
gesperrt.

## Ausgangsstand

`git status --porcelain` vor dem ersten Schritt: leer, Baum sauber. HEAD
`85dc0ea` entspricht dem beauftragten Stand. `dist/` enthielt noch ein
Artefakt aus einem fruheren Lauf (T-290): 59.129.818 Byte, SHA-256
`F988C5207AF533F7E6EE993F4B91A2C23D1FC43538799C7C35425A7EA8B82367` -
deckungsgleich mit dem in T-290 gefuehrten Wert fuer 1.13.2 (`dist`/`build`
sind gitignored, `git status` zeigt sie deshalb nicht als Aenderung).

## Sicherung der Vorversion 1.13.2

Kopiert nach `<scratchpad>/artefakte/NightreignHelper-1.13.2.exe`, Hash der
Kopie erneut geprueft: identisch (`F988C5207AF533F7E6EE993F4B91A2C23D1FC43538799C7C35425A7EA8B82367`).

## Versionsbump

`nrplanner/__init__.py`: `__version__` 1.13.2 -> 1.14.0, ein Commit
(`565e3b9`, `-- nrplanner/__init__.py`).

## Bau

`Get-Process -Name NightreignHelper`: kein Treffer vor dem Loeschen von
`dist/`/`build/`. Bau ausschliesslich ueber
`.\.venv\Scripts\python.exe -m PyInstaller NightreignHelper.spec` (kein
globales `python`, wie in T-290 als Anleitungsluecke gemeldet).

| | Lauf |
|---|---|
| `rc` | 0 ("Build complete!") |
| Dauer | 41,67 s |
| Groesse | 59.213.433 Byte |
| SHA-256 | `79E217617481B086FD63610EB3DB0A60E1C64BDBAE15294045320D98C22FD8B4` |

**Log-Umleitung, ein erklaerbarer Befund:** Die Ausgabe wurde mit
PowerShells `*>` in eine Logdatei umgeleitet; PyInstaller schreibt sein
INFO-Log nach stderr, und PowerShell 5.1 verpackt jede stderr-Zeile eines
nativen Prozesses in einen `NativeCommandError`. Der Log enthaelt dadurch
eine Zeile mit `FullyQualifiedErrorId : NativeCommandError` - kein Fehler
im Build selbst (`rc=0`, keine weitere Fundstelle fuer `error` im Log, kein
Treffer fuer `deprecat`). Ursache ist die Umleitungsmethode, nicht
PyInstaller oder der Code.

Zweiter Lauf zur Reproduzierbarkeitspruefung (Bit-Identitaet) entfaellt -
Auftrag nennt keinen Zweitbau; interne Bit-Nichtidentitaet zwischen Laeufen
derselben Umgebung ist in T-241/T-275/T-279 bereits mehrfach belegt und wird
hier nicht erneut nachgewiesen.

Warnungsdatei: **37 Zeilen**, inhaltsgleich mit T-290 (gegengelesen): dieselben
`missing module`-Zeilen (u. a. `numpy` nur ueber `PIL._typing`, `olefile`,
`cffi`), keine neue Warnungsart, kein fehlender Bestandteil.

Groessendifferenz zu 1.13.2 (59.129.818 Byte): **+83.615 Byte (+0,14 %)** -
plausibel: A22 (Attributabzug in der Schadenszahl) und A23 (Familien-Filter)
sind neuer Anwendungscode ohne neue Abhaengigkeit.

## Startprobe (Rauchtest, NH-004)

Isolierung: `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-293a`,
`LOCALAPPDATA`/`APPDATA` auf `<scratchpad>/T-293/release-manager/localappdata`
bzw. `appdata` umgelenkt (in derselben Kommandozeile wie jeder Aufruf, der die
EXE nennt - der Hook wertet bereits die blosse Namensnennung, z. B. bei
`Get-FileHash`, als Programmstart). Testabzug `NightreignHelper-Testabzug`
(841 Dateien, `EXTRACT_VERSION` 12, weiterhin gueltig) nach
`<localappdata>\NightreignHelper` **kopiert**, nicht verlinkt (Dateizahl nach
dem Kopieren erneut gezaehlt: 841). Vor dem Start `Get-Process -Name
NightreignHelper`: kein Treffer.

- **Start:** `dist\NightreignHelper.exe` gestartet, nach 8 s zwei Prozesse
  (Bootloader-PID ohne Fenstertitel, Kind-PID mit Fenster), beide
  `Responding = True`.
- **Fenstertitel:** "Nightreign Helper 1.14.0" (Kind-Prozess) -
  Versionsressource stimmt mit dem Bump ueberein.
- **Echte Schreibaktion:** `Get-ChildItem HKCU:\Software\DankYeeterT-293a`
  findet nach dem Lauf `NightreignHelper`, `NightreignHelper\builds\1`,
  `NightreignHelper\chalices\1` - die Testorganisation, nicht `DankYeeter`.
  Die echten Nutzerdaten (309 Relikte, ~110 Builds unter
  `HKCU\Software\DankYeeter`) wurden nicht beruehrt (nicht erneut ausgelesen -
  Positivnachweis der Umlenkung genuegt laut CLAUDE.md). Dateizahl im
  umgelenkten `LOCALAPPDATA` nach dem Lauf weiterhin 841 - der Testabzug
  bleibt unveraendert (read-only bestaetigt).
- **Beendet:** `Stop-Process -Force` auf beide `NightreignHelper`-PIDs; danach
  `Get-Process -Name NightreignHelper`: kein Treffer.

Keine ueber die Startprobe hinausgehende Schreibaktion (Update-Pfad,
Neustart-Probe) ausgefuehrt - das ist `clean-room`, nicht Teil dieses
Auftrags.

## Blocker

Keiner fuer diesen Bau.

## Risiken

- Kein UPX auf diesem Bau-Wirt - unveraendert seit T-282/T-290.
- Nur ein gueltiger Lauf: interne Reproduzierbarkeit (Bit-Identitaet zwischen
  zwei Laeufen derselben Umgebung) wurde nicht neu belegt, sondern aus
  T-241/T-275/T-279 uebernommen (auftragsgemaess, kein Zweitbau verlangt).

## Ungeprueft

- Clean-Room-Installation, Update-Pfad (1.13.2 -> 1.14.0), Zweitstart nach
  Neustart - nicht Teil dieses Auftrags (nur Startprobe, keine Schreibaktion
  darueber hinaus).
- Windows ARM64, Windows 8.1/aelter, Linux/macOS - kein Ziel laut `CLAUDE.md`.

## An `developer`

Kein Befund am Anwendungscode. Die in T-290 gemeldete Anleitungsluecke
(`python` im PATH loest global auf, nicht auf `.venv`) betraf nur die
Bau-Anleitung, nicht diesen Lauf - hier wurde durchgehend
`.\.venv\Scripts\python.exe` verwendet.

## An `power-user` (Ausgangspunkt, falls angefordert)

- **Pfad:** `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe`
- **Groesse:** 59.213.433 Byte (56,47 MiB)
- **SHA-256:** `79E217617481B086FD63610EB3DB0A60E1C64BDBAE15294045320D98C22FD8B4`
- **Versionsressource:** 1.14.0, am Fenstertitel bestaetigt (Startprobe).
- **Fuer den Update-Pfad-Test:** Vorversion 1.13.2 liegt gesichert unter
  `C:\Users\Daniel\AppData\Local\Temp\claude\C--Users-Daniel-Desktop-ClaudeCode-Nightreign-Helper\0c1b1951-b796-49a5-9cbc-7588742f286c\scratchpad\artefakte\NightreignHelper-1.13.2.exe`,
  SHA-256 `F988C5207AF533F7E6EE993F4B91A2C23D1FC43538799C7C35425A7EA8B82367`
  (gegen Original verifiziert).
- Drei Umlenkungen zwingend beim Start: `NIGHTREIGN_SETTINGS_ORG`,
  `LOCALAPPDATA`, `APPDATA` - Testabzug kopieren, nicht darauf zeigen
  (`CLAUDE.md`).
- Kein laufender `NightreignHelper.exe`-Prozess nach diesem Lauf (`Get-Process`
  geprueft) - vor eigenem Start dennoch selbst pruefen (NH-004, maschinenweite
  Instanzsperre).

## An `director`

**Empfehlung: freigeben mit benannter Einschraenkung** (fuer den Weiterlauf zu
T-293b/c/d - kein Release-Votum, das bleibt an A-025 und eine ausdrueckliche
Weitergabe-Entscheidung gebunden).

1. Kein `.gitignore`-Nachtrag noetig (`dist/`, `build/` bereits erfasst).
2. Keine offene rote Auflage - Build war nicht gesperrt.
3. Arbeitsbaum war beim Bau sauber, unveraendert nach dem Bau (`dist/`,
   `build/` ignoriert; einziger Commit ist der Versionsbump `565e3b9`).
4. Tag-Vorschlag (nicht gesetzt, Sache des `director`/`archivist`): `v1.14.0`
   auf `565e3b9`, erst nach QA-Urteil und Ingame-Test des Nutzers (laut
   Auftrag T-293).
