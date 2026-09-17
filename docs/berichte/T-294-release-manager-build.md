STATUS: erledigt
AUFTRAG: T-294b - Artefakt 1.14.0 erneut bauen (release-manager, Modus `build`),
nach dem Fixbuendel T-294a (DR-032, QA-285, QA-284)
GELESEN: docs/legal/AUFLAGEN.md (vollstaendig, 559 Zeilen; juengster Abschnitt
"Auflagen vor der Veroeffentlichung 1.13.1", Stand `1f51485`, keine Auflage auf
ROT, Bau/Eigenlauf bleibt GRUEN nach T-241a/T-283c); docs/berichte/T-293-release-manager-build.md
(Vorlage); docs/tasks/T-294.md; CLAUDE.md; nrplanner/__init__.py (unveraendert
1.14.0); .gitignore (`dist/`, `build/` beide erfasst); NightreignHelper.spec
GEAENDERT: dist/NightreignHelper.exe (neu gebaut, gleicher Code-Stand `e0a2f5e`
wie T-294a, keine Version). Vorheriges 1.14.0-Artefakt (Vorfix-Stand, identisch
mit T-293) gesichert als
`<scratchpad>/artefakte/NightreignHelper-1.14.0-vorfix.exe`, Hash vor und nach
dem Kopieren identisch. Kein Anwendungscode angefasst, kein Versionsbump-
Commit (Auftrag: 1.14.0 bleibt unveraendert, unveroeffentlicht).
ANNAHMEN: "vorheriges 1.14.0-Artefakt" meint das in T-293 gebaute (SHA-256
`79e21761...`, Vorfix-Stand vor T-294a) - im Arbeitsbaum lag genau dieses in
`dist/` vor Beginn dieses Laufs, Hash deckungsgleich mit T-293s Angabe.
NAECHSTER: T-294c (qa-engineer, Retest DR-032/QA-285/QA-284 am neuen
Artefakt).
BLOCKIERT DURCH: nichts fuer diesen Bau.

---

# T-294b - Bau 1.14.0 (nach Fixbuendel T-294a)

## Kontraktblock

| | |
|---|---|
| **Pfad** | `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe` |
| **Groesse** | 59.141.218 Byte (56,40 MiB) |
| **SHA-256** | `8CF4B6943416357EEB443B3AB0DB473BE30E5C1287620D21EBC43B5D4329D3E7` |
| **Code-Stand des Artefakts** | `e0a2f5e` (T-294a-Fixbuendel: DR-032, QA-285, QA-284), Branch `docs/audit-and-advisor-design` |
| **Version** | 1.14.0, unveraendert - kein Bump-Commit (Auftrag) |
| **Dauer** | 41,05 s (PyInstaller-Log "Build complete!" bei 41.049 ms) |
| **UPX** | nicht im `PATH` (`where upx`: "Could not find files") - `upx=True` im `.spec` bleibt wirkungslos, wie in jedem vorherigen Bau |
| **`scripts/check_licences.py`** | `OK`, alle drei Pflichtdateien und alle sechs Bibliotheken erfasst |
| **Vorfix-Sicherung** | `<scratchpad>/artefakte/NightreignHelper-1.14.0-vorfix.exe`, 59.213.433 Byte, SHA-256 `79E217617481B086FD63610EB3DB0A60E1C64BDBAE15294045320D98C22FD8B4` (identisch mit T-293) |

## Pflichtlektuere: `docs/legal/AUFLAGEN.md`

Volltext gelesen (559 Zeilen). Keine Auflage steht auf ROT, die diesen Lauf
sperrt: A-010 ist ROT, aber ausdruecklich "sperrt nicht mehr" (Nutzer-
Ruecksstellung 02.09., Abnahme 09.09.). Der juengste Abschnitt (T-283c, Stand
`1f51485`, 16.09.) haelt fest, dass A-020/A-023/A-030/A-031/A-035 fuer 1.13.1
erfuellt bzw. GRUEN sind; die T-241a-Einordnung "Bau/Eigenlauf: GRUEN" gilt
seither unveraendert fort. Dieser Lauf ist kein Release (kein Push, kein Tag,
keine Weitergabe der EXE) - `build` ist nicht gesperrt.

## Ausgangsstand

`git status --porcelain` vor dem ersten Schritt: leer, Baum sauber. HEAD
`e0a2f5e` entspricht dem beauftragten Stand. `dist/` enthielt noch das
Vorfix-Artefakt aus T-293/T-294a: 59.213.433 Byte, SHA-256
`79e217617481b086fd63610eb3db0a60e1c64bdbae15294045320d98c22fd8b4` -
deckungsgleich mit T-293s Angabe (`dist`/`build` sind gitignored, `git
status` zeigt sie deshalb nicht als Aenderung).

## Sicherung der Vorfix-Version 1.14.0

Kopiert nach `<scratchpad>/artefakte/NightreignHelper-1.14.0-vorfix.exe`,
Hash der Kopie erneut geprueft: identisch
(`79e217617481b086fd63610eb3db0a60e1c64bdbae15294045320d98c22fd8b4`).

## Bau

`Get-Process -Name NightreignHelper`: kein Treffer vor dem Loeschen von
`dist/`/`build/`. Bau ausschliesslich ueber
`.\.venv\Scripts\python.exe -m PyInstaller NightreignHelper.spec` (`.venv`
Python 3.12.10, kein globales `python`).

| | Lauf |
|---|---|
| `rc` | 0 ("Build complete!") |
| Dauer | 41,05 s |
| Groesse | 59.141.218 Byte |
| SHA-256 | `8CF4B6943416357EEB443B3AB0DB473BE30E5C1287620D21EBC43B5D4329D3E7` |

Zweiter Lauf zur Reproduzierbarkeitspruefung (Bit-Identitaet) entfaellt -
Auftrag nennt keinen Zweitbau; interne Bit-Nichtidentitaet zwischen Laeufen
derselben Umgebung ist in T-241/T-275/T-279 bereits mehrfach belegt.

Warnungsdatei: **37 Zeilen** (davon 21 `missing module`), inhaltsgleich mit
T-293/T-290: dieselben `missing module`-Zeilen (u. a. `numpy` nur ueber
`PIL._typing`, `olefile`, `cffi`), keine neue Warnungsart, kein fehlender
Bestandteil. Build-Log: 79 Zeilen, 0 Treffer fuer "error", 0 fuer "deprecat".

Groessendifferenz zum Vorfix-Artefakt (59.213.433 Byte): **-72.215 Byte
(-0,12 %)** - plausibel: DR-032/QA-285/QA-284 sind kleine, teils entfernende
Code-Aenderungen (Statuszeilen-Bedingung, Betrag an skalierendes Attribut
statt fixer Reihenfolge) ohne neue Abhaengigkeit.

## Startprobe (Rauchtest, NH-004)

Vor dem Start: `Get-Process -Name NightreignHelper` (mit vollstaendiger
Umlenkung in derselben Kommandozeile) = 0 Treffer - keine Kopie des Nutzers
lief, keine Wartezeit noetig.

Isolierung: `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-294b`, `LOCALAPPDATA`/
`APPDATA` auf `<scratchpad>/T-294/release-manager/localappdata` bzw.
`appdata` umgelenkt (in derselben Kommandozeile wie jeder Aufruf, der die
EXE nennt). Testabzug `NightreignHelper-Testabzug` (841 Dateien,
`EXTRACT_VERSION` 12, weiterhin gueltig) nach `<localappdata>\NightreignHelper`
**kopiert**, nicht verlinkt (Dateizahl nach dem Kopieren gezaehlt: 841).

- **Start:** `dist\NightreignHelper.exe` gestartet, nach 8 s zwei Prozesse
  (Bootloader-PID ohne Fenstertitel, Kind-PID mit Fenster), beide
  `Responding = True`.
- **Fenstertitel:** "Nightreign Helper 1.14.0" (Kind-Prozess) - Version
  unveraendert, wie beabsichtigt.
- **Echte Schreibaktion:** `Get-ChildItem HKCU:\Software\DankYeeterT-294b`
  findet nach dem Lauf `NightreignHelper`, `NightreignHelper\builds\1`,
  `NightreignHelper\chalices\1` - die Testorganisation, nicht `DankYeeter`.
  Die echten Nutzerdaten (309 Relikte, ~110 Builds unter
  `HKCU\Software\DankYeeter`) wurden nicht beruehrt (Positivnachweis der
  Umlenkung genuegt laut CLAUDE.md, kein erneutes Lesen der echten Daten).
  Dateizahl im umgelenkten `LOCALAPPDATA` nach dem Lauf weiterhin 841 - der
  Testabzug bleibt unveraendert (read-only bestaetigt).
- **Beendet:** `Stop-Process -Force` auf beide `NightreignHelper`-PIDs;
  danach `Get-Process -Name NightreignHelper`: kein Treffer.

Keine ueber die Startprobe hinausgehende Schreibaktion (Update-Pfad,
Neustart-Probe) ausgefuehrt - das ist `clean-room`, nicht Teil dieses
Auftrags. Kein Fensterstart durch den `developer` in T-294a laut Auftrag -
dieser Lauf ist der erste Fensterstart des neuen Artefakts.

## Blocker

Keiner fuer diesen Bau.

## Risiken

- Kein UPX auf diesem Bau-Wirt - unveraendert seit T-282/T-290/T-293.
- Nur ein gueltiger Lauf: interne Reproduzierbarkeit (Bit-Identitaet
  zwischen zwei Laeufen derselben Umgebung) wurde nicht neu belegt, sondern
  aus T-241/T-275/T-279 uebernommen (auftragsgemaess, kein Zweitbau
  verlangt).

## Ungeprueft

- Clean-Room-Installation, Update-Pfad (1.13.2 -> 1.14.0 bzw. Vorfix ->
  Fix), Zweitstart nach Neustart - nicht Teil dieses Auftrags (nur
  Startprobe, keine Schreibaktion darueber hinaus).
- Windows ARM64, Windows 8.1/aelter, Linux/macOS - kein Ziel laut `CLAUDE.md`.
- DR-032/QA-285/QA-284 selbst (Fenstergroesse, Betragszeile, Statuszeile) -
  fachliche Pruefung ist T-294c (qa-engineer), nicht dieser Bau.

## An `developer`

Kein Befund am Anwendungscode.

## An `power-user` (Ausgangspunkt, falls angefordert)

- **Pfad:** `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe`
- **Groesse:** 59.141.218 Byte (56,40 MiB)
- **SHA-256:** `8CF4B6943416357EEB443B3AB0DB473BE30E5C1287620D21EBC43B5D4329D3E7`
- **Versionsressource:** 1.14.0, am Fenstertitel bestaetigt (Startprobe).
- **Vorfix-Vergleichsartefakt** (falls fuer T-294c/Power-User-Vergleich
  gebraucht):
  `C:\Users\Daniel\AppData\Local\Temp\claude\C--Users-Daniel-Desktop-ClaudeCode-Nightreign-Helper\0c1b1951-b796-49a5-9cbc-7588742f286c\scratchpad\artefakte\NightreignHelper-1.14.0-vorfix.exe`,
  SHA-256 `79E217617481B086FD63610EB3DB0A60E1C64BDBAE15294045320D98C22FD8B4`.
- Drei Umlenkungen zwingend beim Start: `NIGHTREIGN_SETTINGS_ORG`,
  `LOCALAPPDATA`, `APPDATA` - Testabzug kopieren, nicht darauf zeigen
  (`CLAUDE.md`).
- Kein laufender `NightreignHelper.exe`-Prozess nach diesem Lauf
  (`Get-Process` geprueft) - vor eigenem Start dennoch selbst pruefen
  (NH-004, maschinenweite Instanzsperre).

## An `director`

**Empfehlung: freigeben mit benannter Einschraenkung** (fuer den Weiterlauf
zu T-294c - kein Release-Votum, das bleibt an A-025 und eine ausdrueckliche
Weitergabe-Entscheidung gebunden).

1. Kein `.gitignore`-Nachtrag noetig (`dist/`, `build/` bereits erfasst).
2. Keine offene rote Auflage - Build war nicht gesperrt.
3. Arbeitsbaum war beim Bau sauber, unveraendert nach dem Bau (`dist/`,
   `build/` ignoriert; kein Versionsbump, da 1.14.0 unveroeffentlicht
   bleibt).
4. Tag-Vorschlag: keiner in diesem Lauf - erst nach T-294c-Urteil.
