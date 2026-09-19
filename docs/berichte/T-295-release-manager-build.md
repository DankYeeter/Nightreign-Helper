STATUS: erledigt
AUFTRAG: T-295b - Artefakt 1.14.0 nach AK-317-Nachtrag (Allow immer klickbar,
Commit `099459b`) erneut bauen (release-manager, Modus `build`)
GELESEN: docs/legal/AUFLAGEN.md (vollstaendig, 559 Zeilen; juengster Abschnitt
"Auflagen vor der Veroeffentlichung 1.13.1", Stand `1f51485`, keine Auflage auf
ROT, Bau/Eigenlauf bleibt GRUEN nach T-241a/T-283c); docs/tasks/T-295.md;
docs/berichte/T-294-release-manager-build.md (Vorlage); CLAUDE.md;
nrplanner/__init__.py (unveraendert 1.14.0); .gitignore (`dist/`, `build/`
beide erfasst); NightreignHelper.spec
GEAENDERT: dist/NightreignHelper.exe (neu gebaut, Code-Stand `099459b`, AK-317-
Nachtrag "Allow immer klickbar"). Vorheriges 1.14.0-Artefakt (Stand `e0a2f5e`,
T-294b) gesichert als `<scratchpad>/artefakte/NightreignHelper-1.14.0-t294.exe`,
Hash vor und nach dem Kopieren identisch. Kein Anwendungscode angefasst, kein
Versionsbump-Commit (Auftrag: 1.14.0 bleibt unveraendert). Neu:
docs/berichte/T-295-release-manager-build.md (dieser Bericht).
ANNAHMEN: "Vorstand" meint das in T-294b gebaute Artefakt (SHA-256
`8cf4b694...d3e7`) - im Arbeitsbaum lag genau dieses in `dist/` vor Beginn
dieses Laufs, Hash deckungsgleich mit T-294b.
NAECHSTER: T-295c (qa-engineer, Retest am neuen Artefakt: Allow ohne
Familien-Avoid klickbar und nach Avoid wirksam, plus DR-032/QA-285/QA-284).
BLOCKIERT DURCH: nichts fuer diesen Bau.

---

# T-295b - Bau 1.14.0 (nach AK-317-Nachtrag "Allow immer klickbar")

## Kontraktblock

| | |
|---|---|
| **Pfad** | `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe` |
| **Groesse** | 59.141.726 Byte (56,40 MiB) |
| **SHA-256** | `A45BDF1151C28D2ED0F43B8797F4E27F4C8F7BD114A30BF186A954C3692CEA9C` |
| **Code-Stand des Artefakts** | `099459b` (AK-317-Nachtrag "Allow immer klickbar", T-295a), Branch `docs/audit-and-advisor-design` |
| **Version** | 1.14.0, unveraendert - kein Bump-Commit (Auftrag) |
| **Dauer** | 48,08 s (PyInstaller-Log "Build complete!" bei 47.754 ms) |
| **UPX** | nicht im `PATH` (`where upx`: "Could not find files") - `upx=True` im `.spec` bleibt wirkungslos, wie in jedem vorherigen Bau |
| **`scripts/check_licences.py`** | `OK`, alle drei Pflichtdateien und alle sechs Bibliotheken erfasst |
| **Vorstandssicherung** | `<scratchpad>/artefakte/NightreignHelper-1.14.0-t294.exe`, 59.141.218 Byte, SHA-256 `8CF4B6943416357EEB443B3AB0DB473BE30E5C1287620D21EBC43B5D4329D3E7` (identisch mit T-294b) |

## Pflichtlektuere: `docs/legal/AUFLAGEN.md`

Volltext gelesen (559 Zeilen). Keine Auflage steht auf ROT, die diesen Lauf
sperrt: A-010 ist ROT, aber ausdruecklich "sperrt nicht mehr" (Nutzer-
Rueckstellung 02.09., Abnahme 09.09.). Der juengste Abschnitt (T-283c, Stand
`1f51485`, 16.09.) haelt fest, dass A-020/A-023/A-030/A-031/A-035 fuer 1.13.1
erfuellt bzw. GRUEN sind; die T-241a-Einordnung "Bau/Eigenlauf: GRUEN" gilt
seither unveraendert fort. Dieser Lauf ist kein Release (kein Push, kein Tag,
keine Weitergabe der EXE) - `build` ist nicht gesperrt.

## Ausgangsstand

`git status --porcelain` vor dem ersten Schritt: leer, Baum sauber. HEAD
`099459b` entspricht dem beauftragten Stand (T-295a-Fix "AK-317 Allow immer
klickbar" bereits committet). `dist/` enthielt noch das T-294b-Artefakt:
59.141.218 Byte, SHA-256
`8cf4b6943416357eeb443b3ab0db473be30e5c1287620d21ebc43b5d4329d3e7` -
deckungsgleich mit T-294b (`dist`/`build` sind gitignored, `git status` zeigt
sie deshalb nicht als Aenderung).

## Sicherung des Vorstands 1.14.0 (T-294b-Stand)

Vor `Get-Process`-Pruefung (kein laufender `NightreignHelper.exe`) kopiert
nach `<scratchpad>/artefakte/NightreignHelper-1.14.0-t294.exe`, Hash der Kopie
erneut geprueft: identisch
(`8cf4b6943416357eeb443b3ab0db473be30e5c1287620d21ebc43b5d4329d3e7`).

## Bau

`tasklist /FI "IMAGENAME eq NightreignHelper.exe"`: kein Treffer vor dem
Loeschen von `dist/`/`build/`. Bau ausschliesslich ueber
`.\.venv\Scripts\python.exe -m PyInstaller NightreignHelper.spec` (`.venv`
Python 3.12.10, kein globales `python`).

| | Lauf |
|---|---|
| `rc` | 0 ("Build complete!") |
| Dauer | 48,08 s |
| Groesse | 59.141.726 Byte |
| SHA-256 | `A45BDF1151C28D2ED0F43B8797F4E27F4C8F7BD114A30BF186A954C3692CEA9C` |

Zweiter Lauf zur Reproduzierbarkeitspruefung (Bit-Identitaet) entfaellt -
Auftrag nennt keinen Zweitbau; interne Bit-Nichtidentitaet zwischen Laeufen
derselben Umgebung ist in T-241/T-275/T-279/T-294b bereits mehrfach belegt.

Warnungsdatei: **37 Zeilen** (davon 21 `missing module`), inhaltsgleich mit
T-294b/T-293/T-290: dieselben `missing module`-Zeilen (u. a. `numpy` nur ueber
`PIL._typing`, `olefile`, `cffi`), keine neue Warnungsart, kein fehlender
Bestandteil. Build-Log: 79 Zeilen, 0 Treffer fuer "error", 0 fuer "deprecat".

Groessendifferenz zum T-294b-Artefakt (59.141.218 Byte): **+508 Byte
(+0,0009 %)** - plausibel: T-295a (AK-317-Nachtrag) aendert nur
`effectfilterdialog.py` (Allow-Kaestchen nicht mehr `setEnabled(False)`, ein
Tooltip-Text statt zwei), keine neue Abhaengigkeit.

## Startprobe (Rauchtest, NH-004)

Vor dem Start: `tasklist /FI "IMAGENAME eq NightreignHelper.exe"` (mit
vollstaendiger Umlenkung in derselben Kommandozeile) = 0 Treffer - keine Kopie
des Nutzers lief, keine Wartezeit noetig.

Isolierung: `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-295b`, `LOCALAPPDATA`/
`APPDATA` auf `<scratchpad>/T-295/release-manager/localappdata` bzw.
`appdata` umgelenkt (in derselben Kommandozeile wie jeder Aufruf, der die EXE
nennt). Testabzug `NightreignHelper-Testabzug` (841 Dateien, `EXTRACT_VERSION`
12, weiterhin gueltig) nach `<localappdata>\NightreignHelper` **kopiert**,
nicht verlinkt (Dateizahl nach dem Kopieren gezaehlt: 841).

- **Start:** `dist\NightreignHelper.exe` gestartet, nach 8 s zwei Prozesse
  (Bootloader-PID "PyInstaller Onefile Hidden Window", Kind-PID mit Fenster),
  beide `Running`.
- **Fenstertitel:** "Nightreign Helper 1.14.0" (Kind-Prozess) - Version
  unveraendert, wie beabsichtigt.
- **Echte Schreibaktion:** `reg query HKCU\Software\DankYeeterT-295b /s`
  findet nach dem Lauf `NightreignHelper\builds\1` und
  `NightreignHelper\chalices\1` mit Werten - die Testorganisation, nicht
  `DankYeeter`. Die echten Nutzerdaten (309 Relikte, ~110 Builds unter
  `HKCU\Software\DankYeeter`) wurden nicht beruehrt (Positivnachweis der
  Umlenkung genuegt laut CLAUDE.md, kein erneutes Lesen der echten Daten).
  Dateizahl im umgelenkten `LOCALAPPDATA` nach dem Lauf weiterhin 841 - der
  Testabzug bleibt unveraendert (read-only bestaetigt).
- **Beendet:** `taskkill /F /IM NightreignHelper.exe /T`; danach `tasklist`:
  kein Treffer.

Keine ueber die Startprobe hinausgehende Schreibaktion (Update-Pfad,
Neustart-Probe) ausgefuehrt - das ist `clean-room`, nicht Teil dieses
Auftrags. Der AK-317-Nachtrag selbst (Allow-Kaestchen klickbar ohne
Familien-Avoid) ist fachliche Pruefung und bleibt T-295c (qa-engineer)
vorbehalten - dieser Lauf pruefte nur Start, Fenstertitel und eine Schreib-
aktion, keine Bedienhandlung an den Filtern.

## Blocker

Keiner fuer diesen Bau.

## Risiken

- Kein UPX auf diesem Bau-Wirt - unveraendert seit T-282/T-290/T-293/T-294b.
- Nur ein gueltiger Lauf: interne Reproduzierbarkeit (Bit-Identitaet zwischen
  zwei Laeufen derselben Umgebung) wurde nicht neu belegt, sondern aus
  T-241/T-275/T-279/T-294b uebernommen (auftragsgemaess, kein Zweitbau
  verlangt).

## Ungeprueft

- Clean-Room-Installation, Update-Pfad (aeltere Version -> 1.14.0), Zweitstart
  nach Neustart - nicht Teil dieses Auftrags (nur Startprobe, keine
  Schreibaktion darueber hinaus).
- Windows ARM64, Windows 8.1/aelter, Linux/macOS - kein Ziel laut `CLAUDE.md`.
- Der AK-317-Nachtrag selbst (Allow-Kaestchen ohne/mit Familien-Avoid) -
  fachliche Pruefung ist T-295c (qa-engineer), nicht dieser Bau.

## An `developer`

Kein Befund am Anwendungscode.

## An `power-user` (Ausgangspunkt, falls angefordert)

- **Pfad:** `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe`
- **Groesse:** 59.141.726 Byte (56,40 MiB)
- **SHA-256:** `A45BDF1151C28D2ED0F43B8797F4E27F4C8F7BD114A30BF186A954C3692CEA9C`
- **Versionsressource:** 1.14.0, am Fenstertitel bestaetigt (Startprobe).
- **Vorstands-Vergleichsartefakt** (T-294b-Stand, falls fuer Vergleich
  gebraucht):
  `C:\Users\Daniel\AppData\Local\Temp\claude\C--Users-Daniel-Desktop-ClaudeCode-Nightreign-Helper\0c1b1951-b796-49a5-9cbc-7588742f286c\scratchpad\artefakte\NightreignHelper-1.14.0-t294.exe`,
  SHA-256 `8CF4B6943416357EEB443B3AB0DB473BE30E5C1287620D21EBC43B5D4329D3E7`.
- Drei Umlenkungen zwingend beim Start: `NIGHTREIGN_SETTINGS_ORG`,
  `LOCALAPPDATA`, `APPDATA` - Testabzug kopieren, nicht darauf zeigen
  (`CLAUDE.md`).
- Kein laufender `NightreignHelper.exe`-Prozess nach diesem Lauf
  (`tasklist` geprueft) - vor eigenem Start dennoch selbst pruefen (NH-004,
  maschinenweite Instanzsperre).

## An `director`

**Empfehlung: freigeben mit benannter Einschraenkung** (fuer den Weiterlauf
zu T-295c - kein Release-Votum, das bleibt an A-025 und eine ausdrueckliche
Weitergabe-Entscheidung gebunden).

1. Kein `.gitignore`-Nachtrag noetig (`dist/`, `build/` bereits erfasst).
2. Keine offene rote Auflage - Build war nicht gesperrt.
3. Arbeitsbaum war beim Bau sauber, unveraendert nach dem Bau (`dist/`,
   `build/` ignoriert; kein Versionsbump, da 1.14.0 unveroeffentlicht
   bleibt).
4. Tag-Vorschlag: keiner in diesem Lauf - erst nach T-295c-Urteil.
