STATUS: erledigt
AUFTRAG: T-312a - Artefakt 1.15.0 bauen (release-manager, Modus `build`),
Code-Stand `79b3ecb` (Docs-Commit `04e0089` obendrauf, nur `docs/`)
GELESEN: docs/legal/AUFLAGEN.md (vollstaendig, 559 Zeilen; juengster Abschnitt
"Auflagen vor der Veroeffentlichung 1.13.1", Stand `1f51485`, keine Auflage auf
ROT, Bau/Eigenlauf bleibt GRUEN nach T-241a/T-283c); docs/tasks/T-312.md;
docs/berichte/T-295-release-manager-build.md und T-294-release-manager-build.md
(Vorlage); CLAUDE.md; nrplanner/__init__.py (vor Aenderung 1.14.0);
.gitignore (`dist/`, `build/` beide erfasst); docs/plan-restarbeiten.md
(Testabzug-Verlauf, `EXTRACT_VERSION` 15 bereits vom developer als Vorlage
eingetragen T-310 - kein eigener Nachtrag noetig)
GEAENDERT: nrplanner/__init__.py (1.14.0 -> 1.15.0). dist/NightreignHelper.exe
neu gebaut (Code-Stand `79b3ecb`, gitignored). Vorheriges Artefakt (1.14.0,
Stand `099459b`, T-295b) gesichert als
`<scratchpad>/T-312/release-manager/artefakte/NightreignHelper-1.14.0-t295b.exe`,
Hash vor und nach dem Kopieren identisch. Neu:
docs/berichte/T-312-release-manager.md (dieser Bericht). Kein Anwendungscode
angefasst.
ANNAHMEN: "Vorstand" meint das in T-295b gebaute 1.14.0-Artefakt (SHA-256
`A45BDF11...`) - im Arbeitsbaum lag genau dieses in `dist/` vor Beginn dieses
Laufs, Groesse und Hash deckungsgleich mit T-295b.
NAECHSTER: T-312c (qa-engineer, A24-Nachweis und AK-319..326 am neuen
Artefakt; T-312b security-reviewer laeuft parallel, unabhaengig von diesem
Bau).
BLOCKIERT DURCH: nichts fuer diesen Bau.

---

# T-312a - Bau 1.15.0

## Kontraktblock

| | |
|---|---|
| **Pfad** | `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe` |
| **Groesse** | 59.152.448 Byte (56,41 MiB) |
| **SHA-256** | `E2F614F80BD5ED6661A7059ED862E16FD81DF51B2901D913B592CE93A4E8405A` |
| **Code-Stand des Artefakts** | `79b3ecb` (letzter Code-Commit vor T-312; `04e0089` obendrauf ist reiner Docs-Commit), Branch `docs/audit-and-advisor-design` |
| **Version** | 1.15.0 (Bump-Commit dieser Lauf) |
| **Dauer** | 44,81 s (PyInstaller-Log "Build complete!" bei 44.813 ms) |
| **UPX** | nicht im `PATH` (`where upx`: "Could not find files") - `upx=True` im `.spec` bleibt wirkungslos, wie in jedem vorherigen Bau |
| **`scripts/check_licences.py`** | `OK`, alle drei Pflichtdateien und alle fuenf `requirements.txt`-Bibliotheken erfasst (pycryptodome, zstandard, PySide6, pillow, texture2ddecoder) |
| **Vorstandssicherung** | `<scratchpad>/T-312/release-manager/artefakte/NightreignHelper-1.14.0-t295b.exe`, 59.141.726 Byte, SHA-256 `A45BDF1151C28D2ED0F43B8797F4E27F4C8F7BD114A30BF186A954C3692CEA9C` (identisch mit T-295b) |

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
`04e0089` (Docs-Commit "Pruefphase T-312" auf `docs/state.md` und
`docs/tasks/T-312.md`, gegengeprueft mit `git show --stat`); Code-Stand
darunter `79b3ecb`, wie beauftragt. `dist/` enthielt noch das T-295b-Artefakt:
59.141.726 Byte, SHA-256
`a45bdf1151c28d2ed0f43b8797f4e27f4c8f7bd114a30bf186a954c3692cea9c` -
deckungsgleich mit T-295b (`dist`/`build` sind gitignored, `git status` zeigt
sie deshalb nicht als Aenderung).

## Sicherung des Vorstands 1.14.0 (T-295b-Stand)

Vor `Get-Process`-Pruefung (kein laufender `NightreignHelper.exe`) kopiert
nach `<scratchpad>/T-312/release-manager/artefakte/NightreignHelper-1.14.0-t295b.exe`,
Hash der Kopie erneut geprueft: identisch
(`a45bdf1151c28d2ed0f43b8797f4e27f4c8f7bd114a30bf186a954c3692cea9c`).

## Versionsbump

`nrplanner/__init__.py`: `__version__ = "1.14.0"` -> `"1.15.0"` (neues
Feature A24, unveroeffentlicht). `git status --porcelain` danach: nur diese
eine Datei geaendert.

## Bau

`Get-Process -Name NightreignHelper`: 0 Treffer vor dem Loeschen von
`dist/`/`build/`. Bau ausschliesslich ueber
`./.venv/Scripts/python.exe -m PyInstaller NightreignHelper.spec` (`.venv`
Python 3.12.10, kein globales `python`).

| | Lauf |
|---|---|
| `rc` | 0 ("Build complete!") |
| Dauer | 44,81 s |
| Groesse | 59.152.448 Byte |
| SHA-256 | `E2F614F80BD5ED6661A7059ED862E16FD81DF51B2901D913B592CE93A4E8405A` |

Zweiter Lauf zur Reproduzierbarkeitspruefung (Bit-Identitaet) entfaellt -
Auftrag nennt keinen Zweitbau; interne Bit-Nichtidentitaet zwischen Laeufen
derselben Umgebung ist in T-241/T-275/T-279/T-294b/T-295b bereits mehrfach
belegt.

Warnungsdatei: **37 Zeilen** (davon 21 `missing module`), inhaltsgleich mit
T-295b/T-294b/T-293/T-290: dieselben `missing module`-Zeilen (u. a. `numpy`
nur ueber `PIL._typing`, `olefile`, `cffi`), keine neue Warnungsart, kein
fehlender Bestandteil. Build-Log: 79 Zeilen, 0 Treffer fuer "error", 0 fuer
"deprecat".

Groessendifferenz zum T-295b-Artefakt (59.141.726 Byte): **+10.722 Byte
(+0,018 %)** - plausibel: der Diff `ffac292..79b3ecb` (T-303, T-305, T-306,
T-308, T-310, T-312b-Umfang) fuehrt einen neuen EMEVD-Leser und
MSB-Part-Lesung ueber 64 Karten sowie die Balkenname-Bindung an die
Entityquelle ein (`f184b06`) - mehr Code, keine neue externe Abhaengigkeit
(`check_licences.py` weiterhin `OK`, dieselbe Bibliotheksliste).

## Testabzug

`C:\Users\Daniel\Desktop\ClaudeCode\NightreignHelper-Testabzug` nach
`<scratchpad>/T-312/release-manager/localappdata\NightreignHelper` **kopiert**
(nicht verlinkt, nicht unter echtem `%LOCALAPPDATA%`). Dateizahl nach dem
Kopieren: **841**, Gesamtgroesse **21.131.645 Byte** - deckungsgleich mit dem
im Auftrag genannten Stand (`EXTRACT_VERSION` 15, T-310). Nach dem Rauchtest
erneut gezaehlt: weiterhin 841 Dateien, unveraendert (read-only bestaetigt).
Der Testabzug-Vorlage in `CLAUDE.md` (`EXTRACT_VERSION` 12) ist damit veraltet
gegenueber `docs/plan-restarbeiten.md`; das ist dort bereits seit T-310
(developer, 19.09.) als Ersetzung vermerkt - kein neuer Befund, kein eigener
Nachtrag noetig.

## Startprobe (Rauchtest, NH-004)

Vor dem Start: `Get-Process -Name NightreignHelper` = 0 Treffer - keine Kopie
des Nutzers lief, keine Wartezeit noetig.

Isolierung: `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-312a`, `LOCALAPPDATA`/
`APPDATA` auf `<scratchpad>/T-312/release-manager/localappdata` bzw.
`appdata` umgelenkt (in derselben PowerShell-Sitzung wie der Start).

- **Start:** `dist\NightreignHelper.exe` gestartet, nach 8 s zwei Prozesse
  (Bootloader-PID ohne Fenstertitel, Kind-PID mit Fenster), beide
  `Responding = True`.
- **Fenstertitel:** "Nightreign Helper 1.15.0" - Version am Fenster
  bestaetigt.
- **Echte Schreibaktion:** `Get-ChildItem HKCU:\Software\DankYeeterT-312a`
  findet nach dem Start `NightreignHelper`, `NightreignHelper\builds\1`,
  `NightreignHelper\chalices\1` - die Testorganisation, nicht `DankYeeter`.
  Die echten Nutzerdaten (309 Relikte, ~110 Builds unter
  `HKCU\Software\DankYeeter`) wurden nicht beruehrt (Positivnachweis der
  Umlenkung genuegt laut CLAUDE.md, kein erneutes Lesen der echten Daten).
- **Beendet sofort** (Auftrag: kein laengerer Fensterlauf, der qa-engineer
  braucht das Fenster als Naechstes): `Stop-Process -Force` auf beide
  `NightreignHelper`-PIDs, 0,5 s Wartezeit, danach `Get-Process -Name
  NightreignHelper`: **0 Treffer** - belegt, wie im Auftrag verlangt.

Keine ueber die Startprobe hinausgehende Schreibaktion (Update-Pfad,
Neustart-Probe, fachliche Bedienhandlung) ausgefuehrt - das ist `clean-room`
bzw. `qa-engineer` (T-312c), nicht Teil dieses Auftrags.

## Blocker

Keiner fuer diesen Bau.

## Risiken

- Kein UPX auf diesem Bau-Wirt - unveraendert seit T-282/T-290/T-293/T-294b/
  T-295b.
- Nur ein gueltiger Lauf: interne Reproduzierbarkeit (Bit-Identitaet zwischen
  zwei Laeufen derselben Umgebung) wurde nicht neu belegt, sondern aus
  T-241/T-275/T-279/T-294b/T-295b uebernommen (auftragsgemaess, kein
  Zweitbau verlangt).

## Ungeprueft

- Clean-Room-Installation, Update-Pfad (1.14.0 -> 1.15.0), Zweitstart nach
  Neustart - nicht Teil dieses Auftrags (nur Startprobe, keine Schreibaktion
  darueber hinaus).
- Windows ARM64, Windows 8.1/aelter, Linux/macOS - kein Ziel laut `CLAUDE.md`.
- A24-Nachweis selbst (Feldboss 4551, Nachtboss-Tag-Kennung, adversariale
  Faelle AK-319..326) - fachliche Pruefung ist T-312c (qa-engineer), nicht
  dieser Bau. Sicherheitsdiff (EMEVD/MSB-Leser) ist T-312b
  (security-reviewer), laeuft unabhaengig von diesem Bau.

## An `developer`

Kein Befund am Anwendungscode.

## An `power-user` (Ausgangspunkt, falls angefordert)

- **Pfad:** `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe`
- **Groesse:** 59.152.448 Byte (56,41 MiB)
- **SHA-256:** `E2F614F80BD5ED6661A7059ED862E16FD81DF51B2901D913B592CE93A4E8405A`
- **Versionsressource:** 1.15.0, am Fenstertitel bestaetigt (Startprobe).
- **Vorstands-Vergleichsartefakt** (T-295b-Stand, 1.14.0, falls fuer
  Vergleich gebraucht):
  `C:\Users\Daniel\AppData\Local\Temp\claude\C--Users-Daniel-Desktop-ClaudeCode-Nightreign-Helper\6bddddf0-aa03-4ff3-b040-79bcd15d445d\scratchpad\T-312\release-manager\artefakte\NightreignHelper-1.14.0-t295b.exe`,
  SHA-256 `A45BDF1151C28D2ED0F43B8797F4E27F4C8F7BD114A30BF186A954C3692CEA9C`.
- Drei Umlenkungen zwingend beim Start: `NIGHTREIGN_SETTINGS_ORG`,
  `LOCALAPPDATA`, `APPDATA` - Testabzug kopieren, nicht darauf zeigen
  (`CLAUDE.md`).
- Kein laufender `NightreignHelper.exe`-Prozess nach diesem Lauf
  (`Get-Process` geprueft, 0 Treffer) - vor eigenem Start dennoch selbst
  pruefen (NH-004, maschinenweite Instanzsperre).

## An `director`

**Empfehlung: freigeben mit benannter Einschraenkung** (fuer den Weiterlauf
zu T-312b/T-312c - kein Release-Votum, das bleibt an A-025 und eine
ausdrueckliche Weitergabe-Entscheidung gebunden).

1. Kein `.gitignore`-Nachtrag noetig (`dist/`, `build/` bereits erfasst).
2. Keine offene rote Auflage - Build war nicht gesperrt.
3. Arbeitsbaum war beim Bau sauber; nach dem Bau nur der beauftragte
   Versionsbump als Aenderung (`nrplanner/__init__.py`), `dist/`/`build/`
   weiterhin ignoriert.
4. Tag-Vorschlag: keiner in diesem Lauf - 1.15.0 ist unveroeffentlicht,
   Notes folgen erst nach QA (Auftragstext T-312a).
