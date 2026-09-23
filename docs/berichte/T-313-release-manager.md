STATUS: erledigt
AUFTRAG: T-313b - Artefakt 1.15.0 neu bauen (release-manager, Modus `build`),
Code-Stand `6edab2e` (T-313a-Fix `fix(bosstab): Beute-Umschalter an toggled
statt clicked haengen` obendrauf auf `79b3ecb`)
GELESEN: docs/legal/AUFLAGEN.md (vollstaendig, 559 Zeilen; juengster Abschnitt
"Auflagen vor der Veroeffentlichung 1.13.1", Stand `1f51485`, Gesamtampel
GELB, keine Auflage auf ROT; Bau/Eigenlauf bleibt GRUEN nach T-241a-Einordnung,
seither unveraendert bestaetigt); docs/tasks/T-313.md; docs/tasks/T-312.md
(Kontext); docs/berichte/T-312-release-manager.md (Vorlage, wie im Auftrag
verlangt); CLAUDE.md
GEAENDERT: dist/NightreignHelper.exe neu gebaut (Code-Stand `6edab2e`,
gitignored, kein Versionsbump - Version bleibt 1.15.0 laut Auftrag). Voriges
Artefakt (1.15.0, Stand `79b3ecb`, T-312a) gesichert als
`<scratchpad>/T-313/release-manager/artefakte/NightreignHelper-1.15.0-t312a-79b3ecb.exe`,
Hash vor und nach dem Kopieren identisch. Neu:
docs/berichte/T-313-release-manager.md (dieser Bericht). Kein Anwendungscode
angefasst.
ANNAHMEN: "Vorstand" meint das in T-312a gebaute 1.15.0-Artefakt auf `79b3ecb`
(SHA-256 `E2F614F8...`) - im Arbeitsbaum lag genau dieses in `dist/` vor
Beginn dieses Laufs, Groesse und Hash deckungsgleich mit T-312a.
NAECHSTER: T-313c (qa-engineer, Retest QA-288 am neuen Artefakt).
BLOCKIERT DURCH: nichts fuer diesen Bau.

---

# T-313b - Bau 1.15.0 (Fix QA-288)

## Kontraktblock

| | |
|---|---|
| **Pfad** | `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe` |
| **Groesse** | 59.151.716 Byte (56,41 MiB) |
| **SHA-256** | `1D4197DF0F0C765B507CCA824FBA480DBCFCA76C482CF3F7A852B199CB6BBDF0` |
| **Code-Stand des Artefakts** | `6edab2e` (HEAD, Branch `docs/audit-and-advisor-design`) |
| **Version** | 1.15.0 (unveraendert, kein Bump laut Auftrag) |
| **Dauer** | 38,617 s (PyInstaller-Eigenzeit "Build complete!"), Wanduhr ~39 s |
| **UPX** | nicht im `PATH` (`where upx`: "Could not find files") - `upx=True` im `.spec` bleibt wirkungslos, wie in jedem vorherigen Bau |
| **`scripts/check_licences.py`** | `OK`, alle drei Pflichtdateien und alle fuenf `requirements.txt`-Bibliotheken erfasst |
| **Vorstandssicherung** | `<scratchpad>/T-313/release-manager/artefakte/NightreignHelper-1.15.0-t312a-79b3ecb.exe`, 59.152.448 Byte, SHA-256 `E2F614F80BD5ED6661A7059ED862E16FD81DF51B2901D913B592CE93A4E8405A` (identisch mit T-312a) |

## Pflichtlektuere `docs/legal/AUFLAGEN.md`

Volltext gelesen (559 Zeilen). Keine Auflage steht auf ROT, die diesen Lauf
sperrt: A-010 ist ROT, aber ausdruecklich "sperrt nicht mehr" (Nutzer-
Rueckstellung 02.09., Abnahme 09.09.). Juengster Abschnitt (T-283c, Stand
`1f51485`, 16.09.): Gesamtampel GELB fuer 1.13.1, die T-241a-Einordnung
"Bau/Eigenlauf: GRUEN" gilt seither unveraendert fort. Dieser Lauf ist kein
Release (kein Push, kein Tag, keine Weitergabe der EXE) - `build` ist nicht
gesperrt.

## Ausgangsstand

`git status --porcelain` vor dem ersten Schritt: leer, Baum sauber. HEAD
`6edab2e` ("fix(bosstab): Beute-Umschalter an toggled statt clicked
haengen"), wie im Auftrag genannt. `dist/` enthielt noch das T-312a-Artefakt:
59.152.448 Byte, SHA-256 `e2f614f80bd5ed6661a7059ed862e16fd81df51b2901d913b592ce93a4e8405a`
- deckungsgleich mit T-312a (`dist`/`build` sind gitignored, `git status`
zeigt sie deshalb nicht als Aenderung).

## Sicherung des Vorstands (T-312a-Stand, Code `79b3ecb`)

`Get-Process -Name NightreignHelper`: 0 Treffer vor dem Loeschen von `dist/`.
Kopiert nach
`<scratchpad>/T-313/release-manager/artefakte/NightreignHelper-1.15.0-t312a-79b3ecb.exe`,
Hash der Kopie erneut geprueft: identisch
(`e2f614f80bd5ed6661a7059ed862e16fd81df51b2901d913b592ce93a4e8405a`).

## Versionsbump

Keiner. Auftrag T-313b: "Version bleibt 1.15.0" - `nrplanner/__init__.py`
unveraendert gelassen, nach dem Bau erneut geprueft: weiterhin `"1.15.0"`.

## Bau

`Get-Process -Name NightreignHelper`: 0 Treffer vor dem Loeschen von
`dist/`/`build/`. Bau ausschliesslich ueber
`./.venv/Scripts/python.exe -m PyInstaller NightreignHelper.spec` (`.venv`
Python; kein globales `python`).

| | Lauf |
|---|---|
| `rc` | 0 ("Build complete!") |
| Dauer (PyInstaller-Eigenzeit) | 38,617 s |
| Groesse | 59.151.716 Byte |
| SHA-256 | `1d4197df0f0c765b507cca824fba480dbcfca76c482cf3f7a852b199cb6bbdf0` |

Zweiter Lauf zur Reproduzierbarkeitspruefung (Bit-Identitaet) entfaellt -
Auftrag nennt keinen Zweitbau; interne Bit-Nichtidentitaet zwischen Laeufen
derselben Umgebung ist in T-241/T-275/T-279/T-294b/T-295b/T-312a bereits
mehrfach belegt.

Warnungsdatei (`build/NightreignHelper/warn-NightreignHelper.txt`): **37
Zeilen** (davon 21 `missing module`) - zahlengleich mit T-312a/T-295b/T-294b,
dieselbe Art (u. a. `numpy` nur ueber `PIL._typing`, `olefile`, `cffi`), keine
neue Warnung. Build-Log: 0 Treffer fuer "error" (case-insensitive), 0 fuer
"deprecat".

Groessendifferenz zum T-312a-Artefakt (59.152.448 Byte): **-732 Byte
(-0,0012 %)** - plausibel: der einzige Unterschied im Diff `79b3ecb..6edab2e`
ist T-313a (`bosstab.py`: Signal-Verdrahtung `toggled` statt `clicked`, keine
neue Abhaengigkeit; `check_licences.py` weiterhin `OK`, dieselbe
Bibliotheksliste).

## Testabzug

`C:\Users\Daniel\Desktop\ClaudeCode\NightreignHelper-Testabzug` nach
`<scratchpad>/T-313/release-manager/localappdata\NightreignHelper` **kopiert**
(nicht verlinkt, nicht unter echtem `%LOCALAPPDATA%`). Dateizahl nach dem
Kopieren: **841**, Gesamtgroesse **21.131.645 Byte** - deckungsgleich mit dem
im Auftrag genannten Stand. Nach dem Rauchtest erneut gezaehlt: weiterhin 841
Dateien / 21.131.645 Byte, unveraendert (read-only bestaetigt).

## Startprobe (Rauchtest, NH-004)

Vor dem Start: `Get-Process -Name NightreignHelper` = 0 Treffer - keine Kopie
des Nutzers lief, keine Wartezeit noetig.

Isolierung: `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-313b`, `LOCALAPPDATA`/
`APPDATA` auf `<scratchpad>/T-313/release-manager/localappdata` bzw.
`appdata` umgelenkt (in derselben PowerShell-Sitzung wie der Start).

- **Start:** `dist\NightreignHelper.exe` gestartet, nach 8 s zwei Prozesse
  (Bootloader-PID 11720, Kind-PID 24456), beide `Responding = True`.
- **Fenstertitel:** "Nightreign Helper 1.15.0" - Version am Fenster
  bestaetigt.
- **Echte Schreibaktion:** `Get-ChildItem HKCU:\Software\DankYeeterT-313b`
  findet nach dem Start `NightreignHelper`, `NightreignHelper\builds\1`,
  `NightreignHelper\chalices\1` - die Testorganisation, nicht `DankYeeter`.
  Die echten Nutzerdaten (309 Relikte, ~110 Builds unter
  `HKCU\Software\DankYeeter`) wurden nicht beruehrt (Positivnachweis der
  Umlenkung genuegt laut CLAUDE.md, kein erneutes Lesen der echten Daten).
- **Beendet sofort** (Auftrag: "Rauchtest sofort beenden"): `Stop-Process
  -Force` auf beide `NightreignHelper`-PIDs, 0,5 s Wartezeit, danach
  `Get-Process -Name NightreignHelper`: **0 Treffer** - belegt, wie im Auftrag
  verlangt.

Keine ueber die Startprobe hinausgehende Schreibaktion (Update-Pfad,
Neustart-Probe, fachliche Bedienhandlung QA-288 selbst) ausgefuehrt - das ist
`clean-room` bzw. `qa-engineer` (T-313c), nicht Teil dieses Auftrags.

## Blocker

Keiner fuer diesen Bau.

## Risiken

- Kein UPX auf diesem Bau-Wirt - unveraendert seit T-282/T-290/T-293/T-294b/
  T-295b/T-312a.
- Nur ein gueltiger Lauf: interne Reproduzierbarkeit (Bit-Identitaet zwischen
  zwei Laeufen derselben Umgebung) wurde nicht neu belegt, sondern aus
  T-241/T-275/T-279/T-294b/T-295b/T-312a uebernommen (auftragsgemaess, kein
  Zweitbau verlangt).

## Ungeprueft

- Clean-Room-Installation, Update-Pfad, Zweitstart nach Neustart - nicht Teil
  dieses Auftrags (nur Startprobe, keine Schreibaktion darueber hinaus).
- Windows ARM64, Windows 8.1/aelter, Linux/macOS - kein Ziel laut `CLAUDE.md`.
- QA-288-Fix selbst (UIA-Toggle, Leertaste, Maus) - fachliche Pruefung ist
  T-313c (qa-engineer), nicht dieser Bau.

## An `developer`

Kein Befund am Anwendungscode.

## An `power-user` (Ausgangspunkt, falls angefordert)

- **Pfad:** `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe`
- **Groesse:** 59.151.716 Byte (56,41 MiB)
- **SHA-256:** `1D4197DF0F0C765B507CCA824FBA480DBCFCA76C482CF3F7A852B199CB6BBDF0`
- **Versionsressource:** 1.15.0, am Fenstertitel bestaetigt (Startprobe).
- **Vorstands-Vergleichsartefakt** (T-312a-Stand, 1.15.0 auf `79b3ecb`, falls
  fuer Vergleich gebraucht):
  `C:\Users\Daniel\AppData\Local\Temp\claude\C--Users-Daniel-Desktop-ClaudeCode-Nightreign-Helper\6bddddf0-aa03-4ff3-b040-79bcd15d445d\scratchpad\T-313\release-manager\artefakte\NightreignHelper-1.15.0-t312a-79b3ecb.exe`,
  SHA-256 `E2F614F80BD5ED6661A7059ED862E16FD81DF51B2901D913B592CE93A4E8405A`.
- Drei Umlenkungen zwingend beim Start: `NIGHTREIGN_SETTINGS_ORG`,
  `LOCALAPPDATA`, `APPDATA` - Testabzug kopieren, nicht darauf zeigen
  (`CLAUDE.md`).
- Kein laufender `NightreignHelper.exe`-Prozess nach diesem Lauf
  (`Get-Process` geprueft, 0 Treffer) - vor eigenem Start dennoch selbst
  pruefen (NH-004, maschinenweite Instanzsperre).

## An `director`

**Empfehlung: freigeben mit benannter Einschraenkung** (fuer den Weiterlauf
zu T-313c - kein Release-Votum, das bleibt an A-025 und eine ausdrueckliche
Weitergabe-Entscheidung gebunden).

1. Kein `.gitignore`-Nachtrag noetig (`dist/`, `build/` bereits erfasst).
2. Keine offene rote Auflage - Build war nicht gesperrt.
3. Arbeitsbaum war beim Bau sauber und blieb es (kein Versionsbump in diesem
   Lauf); `dist/`/`build/` weiterhin ignoriert.
4. Tag-Vorschlag: keiner in diesem Lauf - 1.15.0 ist unveroeffentlicht, Notes
   folgen erst nach QA gruen (T-313d, Auftragstext).
