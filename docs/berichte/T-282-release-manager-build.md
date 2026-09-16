STATUS: erledigt
AUFTRAG: T-282 - Artefakt 1.13.1 bauen (release-manager, Modus `build`)
GELESEN: docs/legal/AUFLAGEN.md (vollstaendig, 526 Zeilen; letzter Abschnitt
"Bau und Eigenlauf 1.12.0 und die Screenshot-Neuaufnahme", Stand `02e0721`,
haelt "Ampel Bau/Eigenlauf: GRUEN" fest, kein neuer Abschnitt seither);
docs/berichte/T-279-release-manager-build.md (Vorlage); CLAUDE.md;
nrplanner/__init__.py (vor Aenderung: 1.13.0); .gitignore (`dist/`, `build/`
beide erfasst)
GEAENDERT: nrplanner/__init__.py (`__version__` 1.13.0 -> 1.13.1, Commit
`b46641c`); `dist/NightreignHelper.exe` (neu gebaut, ein Lauf). Sicherungskopie
der Vorversion 1.13.0 nach `<scratchpad>/artefakte/NightreignHelper-1.13.0.exe`
(Hash gegen Original verifiziert). Kein weiterer Anwendungscode angefasst.
ANNAHMEN: Versionssprung 1.13.0 -> 1.13.1 (Patch) folgt der Projektregel in
`nrplanner/__init__.py` fuer eine kleine, in sich abgeschlossene Ergaenzung
(AK-313 Erklaerungszeile) plus einen reinen CI-Schritt (A-008) - kein
Widerspruch noetig, Auftrag nannte die Zielversion ohnehin explizit.
NAECHSTER: nach Weisung des director (`notes`, qa-engineer, power-user).
BLOCKIERT DURCH: nichts fuer diesen Bau.

---

# T-282 - Bau 1.13.1

## Kontraktblock

| | |
|---|---|
| **Pfad** | `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe` |
| **Groesse** | 59.201.630 Byte (56,46 MiB) |
| **SHA-256** | `71E8202980BA528119815C75818757668EA956480A918C0236D1C8E420E67E1C` (`Get-FileHash -Algorithm SHA256`) |
| **Versionsbump-Commit** | `b46641c` ("chore(release): Version 1.13.1") |
| **Code-Stand des Artefakts** | `3e2ed42` (letzter Anwendungscode-Commit vor dem Bump), Branch `docs/audit-and-advisor-design` |
| **Dauer** | 43,08 s (Wanduhr, `Stopwatch`; PyInstaller-Log "Build complete!" bei 42,875 s - konsistent) |
| **UPX** | nicht im `PATH` (`where upx`: "Could not find files") - `upx=True` im `.spec` bleibt wirkungslos, wie in jedem vorherigen Bau |
| **`scripts/check_licences.py`** | `OK`, alle drei Pflichtdateien und alle sechs Bibliotheken erfasst |

## Pflichtlektuere: `docs/legal/AUFLAGEN.md`

Volltext gelesen. Kein Eintrag auf ROT, der diesen Lauf sperrt: A-010 ist ROT,
aber ausdruecklich "sperrt nicht mehr" (Nutzer-Ruecksstellung 02.09., Abnahme
09.09.). Der juengste Abschnitt (Stand `02e0721`) haelt ausdruecklich
"Ampel Bau/Eigenlauf: GRUEN" fest; seither kein neuer Abschnitt in der Datei.
A-020/A-023/A-025/A-031/A-033 greifen erst bei Weitergabe - dieser Lauf ist
kein Release (kein Push, kein Commit auf `main`, keine Weitergabe der EXE).
`build` ist damit nicht gesperrt.

## Ausgangsstand

`git status --porcelain` vor dem ersten Schritt: leer, Baum sauber. HEAD
`3e2ed42` entspricht dem beauftragten Stand. Seit 1.13.0 nur zwei
Anwendungscode-/CI-Commits im Baum: `8e1fc9d` (AK-313 Erklaerungszeile im
Effektfilter-Fenster) und `c148585` (release.yml Testschritt, beruehrt die
EXE nicht). `.venv` vorhanden: Python 3.12.10, PyInstaller 6.21.0 (gepinnt,
unveraendert gegenueber T-279).

## Sicherung der Vorversion 1.13.0

Vor jeder Aenderung lag in `dist/` noch das Artefakt aus T-279: Hash
`332955EC291308334CD3E2ED6437BA90EBB6E543A4F7FCD7A4A0FA56D3701113`, deckungsgleich
mit dem in T-279 gefuehrten Wert. Kopiert nach
`<scratchpad>/artefakte/NightreignHelper-1.13.0.exe`, Hash der Kopie erneut
geprueft: identisch. Sicherung verifiziert, nicht nur ausgefuehrt.

## Versionsbump

`nrplanner/__init__.py`: `__version__` 1.13.0 -> 1.13.1, ein Commit
(`b46641c`, `-- nrplanner/__init__.py`).

## `dist/` und `build/` fuer Kaltstart geloescht

Laufender Prozess vorab geprueft (`Get-Process -Name NightreignHelper`): kein
Treffer. `Remove-Item -Recurse -Force dist,build`, danach beide Pfade
`Test-Path` -> `False`. Echter Kaltstart.

## Bau, ein Lauf

| | Lauf |
|---|---|
| `rc` | 0 ("Build complete!", 0 Treffer fuer `error`/`deprecat` im Log ausser der erwarteten PowerShell-Stderr-Huelle um die letzte INFO-Zeile) |
| Dauer | 43,08 s |
| Groesse | 59.201.630 Byte |
| SHA-256 | `71E8202980BA528119815C75818757668EA956480A918C0236D1C8E420E67E1C` |

Zweiter Lauf entfallen - Auftrag nennt keinen Zweitbau, interne
Bit-Nichtidentitaet zwischen Laeufen ist in T-241/T-275/T-279 bereits mehrfach
belegt (PE-Baustempel, Modulreihenfolgen-Vertauschung) und wird hier nicht
erneut nachgewiesen.

Warnungsdatei (`build/NightreignHelper/warn-NightreignHelper.txt`): **33
Zeilen** - identisch mit T-279 (1.13.0). Keine neue Warnungsart.

Groessendifferenz zu 1.13.0 (59.201.789 Byte): **-159 Byte (-0,0003 %)** -
plausibel: eine Erklaerungszeile im Effektfilter-Fenster (8e1fc9d) und ein
reiner CI-Textschritt (c148585, beruehrt keinen Anwendungscode) sind der
einzige Unterschied im Baum; die Aenderung liegt in der Groessenordnung von
Kompressions-/Layout-Rauschen zwischen Baeumen, kein Hinweis auf einen
fehlenden Bestandteil.

## Startprobe

Isolierung: `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-282`,
`LOCALAPPDATA`/`APPDATA` auf `<scratchpad>/T-282/localappdata`|`appdata`
umgelenkt (in derselben Kommandozeile wie der Start, sonst sperrt der Hook).
Testabzug `NightreignHelper-Testabzug` (841 Dateien, `EXTRACT_VERSION` 12,
weiterhin gueltig) nach `<localappdata>\NightreignHelper` **kopiert**, nicht
verlinkt. Vor dem Start `Get-Process -Name NightreignHelper`: kein Treffer.

- **Start:** `dist\NightreignHelper.exe` gestartet, nach 8 s weiterhin aktiv
  (`HasExited` = `False`).
- **Fenstertitel:** "Nightreign Helper 1.13.1", `Responding` = `True` -
  Versionsressource stimmt mit dem Bump ueberein.
- **Beweis der Umlenkung:** `reg query HKCU\Software\DankYeeterT-282` findet
  den Schluessel `...\NightreignHelper` (Test-Organisation, nicht die echte
  `DankYeeter`); der redirected `LOCALAPPDATA`-Pfad enthaelt Dateien nach dem
  Lauf. Die echten Nutzerdaten (309 Relikte, ~110 Builds unter
  `HKCU\Software\DankYeeter`) wurden nicht beruehrt (nicht erneut ausgelesen -
  Positivnachweis der Umlenkung genuegt laut CLAUDE.md).
- **Beendet:** `Stop-Process -Force` auf alle `NightreignHelper`-Prozesse;
  danach `Get-Process -Name NightreignHelper` erneut: kein Treffer.

Keine ueber die Startprobe hinausgehende Schreibaktion (Build speichern,
Update-Pfad) ausgefuehrt - das ist `clean-room`, nicht Teil dieses Auftrags.

## Blocker

Keiner fuer diesen Bau.

## Risiken

- Kein UPX auf diesem Bau-Wirt - unveraendert.
- Nur ein Lauf: interne Reproduzierbarkeit dieses konkreten Artefakts wurde
  nicht per Zwei-Lauf-Vergleich neu belegt, sondern aus T-241/T-275/T-279
  uebernommen (auftragsgemaess).

## Ungeprueft

- Clean-Room-Installation, Update-Pfad (1.13.0 -> 1.13.1), Zweitstart nach
  Neustart - nicht Teil dieses Auftrags (nur Startprobe, keine Schreibaktion).
- Windows ARM64, Windows 8.1/aelter, Linux/macOS - kein Ziel laut `CLAUDE.md`.

## An `developer`

Keine neuen Befunde am Anwendungscode fuer diesen Bau.

## An `power-user` (Ausgangspunkt, falls angefordert)

- **Pfad:** `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe`
- **Groesse:** 59.201.630 Byte (56,46 MiB)
- **SHA-256:** `71E8202980BA528119815C75818757668EA956480A918C0236D1C8E420E67E1C`
- **Versionsressource:** 1.13.1, am Fenstertitel bestaetigt (Startprobe).
- **Fuer den Update-Pfad-Test:** Vorversion 1.13.0 liegt gesichert unter
  `C:\Users\Daniel\AppData\Local\Temp\claude\C--Users-Daniel-Desktop-ClaudeCode-Nightreign-Helper\0c1b1951-b796-49a5-9cbc-7588742f286c\scratchpad\artefakte\NightreignHelper-1.13.0.exe`,
  SHA-256 `332955EC291308334CD3E2ED6437BA90EBB6E543A4F7FCD7A4A0FA56D3701113`
  (gegen Original verifiziert).
- Drei Umlenkungen zwingend beim Start: `NIGHTREIGN_SETTINGS_ORG`,
  `LOCALAPPDATA`, `APPDATA` - Testabzug kopieren, nicht darauf zeigen
  (`CLAUDE.md`).
- Kein laufender `NightreignHelper.exe`-Prozess nach diesem Lauf (`Get-Process`
  geprueft) - vor eigenem Start dennoch selbst pruefen.

## An `director`

**Empfehlung: freigeben mit benannter Einschraenkung** (fuer den Weiterlauf zu
`notes`/qa-engineer/power-user - kein Release-Votum, das bleibt an A-025 und
eine ausdrueckliche Weitergabe-Entscheidung gebunden).

1. Kein `.gitignore`-Nachtrag noetig (`dist/`, `build/` bereits erfasst).
2. Keine offene rote Auflage - Build war nicht gesperrt.
3. Arbeitsbaum war beim Bau sauber, unveraendert nach dem Bau (`dist/`,
   `build/` ignoriert; einziger Commit ist der Versionsbump `b46641c`).
4. Tag-Vorschlag (nicht gesetzt, Sache des `director`/`archivist`): `v1.13.1`
   auf `b46641c`.
