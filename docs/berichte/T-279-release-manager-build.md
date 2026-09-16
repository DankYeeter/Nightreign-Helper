STATUS: erledigt
AUFTRAG: T-279 - Artefakt 1.13.0 bauen (release-manager, Modus `build`)
GELESEN: docs/legal/AUFLAGEN.md (vollstaendig, 526 Zeilen, letzter Abschnitt
"Bau und Eigenlauf 1.12.0 und die Screenshot-Neuaufnahme", Stand `02e0721` -
haelt "Ampel Bau/Eigenlauf: GRUEN" ausdruecklich fest, keine neue Auflage seit
diesem Stand); docs/release/ROLLOUT.md (Abschnitt Build/1.8.0-Ablaufplan als
Vorlage); docs/berichte/T-275-release-manager-build.md (Vorlage); CLAUDE.md;
nrplanner/__init__.py (vor Aenderung: 1.12.3); .gitignore (`dist/`, `build/`
beide erfasst)
GEAENDERT: nrplanner/__init__.py (`__version__` 1.12.3 -> 1.13.0, Commit
`5c07392`); `dist/NightreignHelper.exe` (neu gebaut, ein Lauf). Sicherungskopie
der Vorversion 1.12.3 nach `<scratchpad>/artefakte/NightreignHelper-1.12.3.exe`
(Hash gegen Original verifiziert). Kein weiterer Anwendungscode angefasst.
ANNAHMEN: Versionssprung 1.12.3 -> 1.13.0 (Minor) folgt der Projektregel in
`nrplanner/__init__.py` ("die mittlere Stelle, wenn eine Funktion … landet") -
kein Widerspruch noetig. Nebenfund, kein Blocker: HEAD-Commit `0d14a0e` traegt
selbst die Bezeichnung "AK-312" fuer eine Enter-Tasten-Navigation, waehrend der
Auftrag AK-312 dem Effektfilter-Fenster zuordnet; das Fenster selbst gehoert zu
AK-300-311 (Commits `33f8ecb`, `e7057ab`, `ca1a99f`, `f81068b`). Beide
Aenderungen sind im Baum, die Versionsnummer wird durch die Abweichung nicht
beruehrt - Hinweis an director/technical-writer fuer den `notes`-Lauf (CHANGELOG).
NAECHSTER: `notes` (CHANGELOG/ROLLOUT-Abschnitt 1.13.0) oder qa-engineer/
power-user, je nach Weisung des director.
BLOCKIERT DURCH: nichts fuer diesen Bau.

---

# T-279 - Bau 1.13.0

## Kontraktblock

| | |
|---|---|
| **Pfad** | `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe` |
| **Groesse** | 59.201.789 Byte (56,46 MiB) |
| **SHA-256** | `332955EC291308334CD3E2ED6437BA90EBB6E543A4F7FCD7A4A0FA56D3701113` (`Get-FileHash -Algorithm SHA256`) |
| **Versionsbump-Commit** | `5c07392` ("chore(release): Version 1.13.0") |
| **Code-Stand des Artefakts** | `0d14a0e` (letzter Anwendungscode-Commit vor dem Bump), Branch `docs/audit-and-advisor-design` |
| **Dauer** | 46,18 s (Wanduhr, `Stopwatch`; PyInstaller-Log "Build complete!" bei 45,939 s - konsistent) |
| **UPX** | nicht im `PATH` (`where.exe upx`: "Could not find files") - `upx=True` im `.spec` bleibt wirkungslos, wie in jedem vorherigen Bau |
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
`0d14a0e` entspricht dem beauftragten Stand. `.venv` vorhanden: Python
3.12.10, PyInstaller 6.21.0 (gepinnt, unveraendert gegenueber T-275).

## Sicherung der Vorversion 1.12.3

Vor jeder Aenderung lag in `dist/` noch das Artefakt aus T-275: Hash
`1C8B4FF52286928B7FC795CC65597BF7F0A65ED40C987C7FE63D0E9E2BB4DC88`, deckungsgleich
mit dem in `ROLLOUT.md` gefuehrten Wert. Kopiert nach
`<scratchpad>/artefakte/NightreignHelper-1.12.3.exe`, Hash der Kopie erneut
geprueft: identisch. Sicherung verifiziert, nicht nur ausgefuehrt.

## Versionsbump

`nrplanner/__init__.py`: `__version__` 1.12.3 -> 1.13.0, ein Commit
(`5c07392`, `-- nrplanner/__init__.py`).

## `dist/` und `build/` fuer Kaltstart geloescht

Laufender Prozess vorab geprueft (`Get-Process -Name NightreignHelper`): kein
Treffer. `Remove-Item -Recurse -Force dist,build`, danach beide Pfade
`Test-Path` -> `False`. Echter Kaltstart.

## Bau, ein Lauf

| | Lauf |
|---|---|
| `rc` | 0 ("Build complete!", 0 Treffer fuer `error`/`deprecat` im Log) |
| Dauer | 46,18 s |
| Groesse | 59.201.789 Byte |
| SHA-256 | `332955EC291308334CD3E2ED6437BA90EBB6E543A4F7FCD7A4A0FA56D3701113` |

Zweiter Lauf entfallen - Auftrag nennt keinen Zweitbau, interne
Bit-Nichtidentitaet zwischen Laeufen ist in T-241/T-275 bereits mehrfach belegt
(PE-Baustempel, Modulreihenfolgen-Vertauschung) und wird hier nicht erneut
nachgewiesen.

Warnungsdatei (`build/NightreignHelper/warn-NightreignHelper.txt`): **33
Zeilen** - abweichend von den 37 Zeilen der letzten sieben Bauten (T-241 bis
T-275). Volltext gepruft: alle Eintraege sind bekannte "missing module named
…"-Hinweise auf optionale/POSIX-only Stdlib-Importe (`pwd`, `grp`, `posix`,
`resource`, `fcntl`, `termios`, `cffi`, `imp`, `StringIO` u. a.) - dieselbe
Kategorie wie bisher, keine neue Art von Eintrag, kein `ERROR`. Die Differenz
liegt an der Zahl der erkannten optionalen Importe (vermutlich durch den
Codezuwachs seit 1.12.3, u. a. `effectfilters.py`), nicht an einem neuen
Problem - Erklaerung, keine Unerklaerte-Warnung-Meldung noetig.

Groessendifferenz zu 1.12.3 (59.123.168 Byte): +78.621 Byte (+0,13 %) -
plausibel fuer den Funktionszuwachs (Effektfilter-Fenster, Umbenennung
Favourite/Avoid, Enter-Navigation) zwischen den Staenden.

## Startprobe

Isolierung: `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-279`,
`LOCALAPPDATA`/`APPDATA` auf `<scratchpad>/T-279/localappdata`|`appdata`
umgelenkt (in derselben Kommandozeile wie der Start, sonst sperrt der Hook).
Testabzug `NightreignHelper-Testabzug` (841 Dateien, 20.849.867 Byte,
`EXTRACT_VERSION` 12) nach `<localappdata>\NightreignHelper` **kopiert**, nicht
verlinkt. Vor dem Start `Get-Process -Name NightreignHelper`: kein Treffer.

- **Start:** `dist\NightreignHelper.exe` gestartet, nach 8 s weiterhin aktiv
  (`HasExited` = `False`).
- **Fenstertitel:** "Nightreign Helper 1.13.0", `Responding` = `True` -
  Versionsressource stimmt mit dem Bump ueberein.
- **Beweis der Umlenkung:** `reg query HKCU\Software\DankYeeterT-279` findet
  den Schluessel `...\NightreignHelper` (Test-Organisation, nicht die echte
  `DankYeeter`); der redirected `LOCALAPPDATA`-Pfad enthaelt Dateien nach dem
  Lauf. Die echten Nutzerdaten (309 Relikte, ~110 Builds unter
  `HKCU\Software\DankYeeter`) wurden nicht beruehrt (nicht erneut ausgelesen -
  Positivnachweis der Umlenkung genuegt laut CLAUDE.md).
- **Beendet:** `Stop-Process -Force` auf beide `NightreignHelper`-Prozesse
  (PyInstaller-Onefile startet Launcher + Kindprozess); danach
  `Get-Process -Name NightreignHelper` erneut: kein Treffer.

Keine ueber die Startprobe hinausgehende Schreibaktion (Build speichern,
Update-Pfad) ausgefuehrt - das ist `clean-room`, nicht Teil dieses Auftrags.

## Blocker

Keiner fuer diesen Bau.

## Risiken

- Kein UPX auf diesem Bau-Wirt - unveraendert.
- Nur ein Lauf: interne Reproduzierbarkeit dieses konkreten Artefakts wurde
  nicht per Zwei-Lauf-Vergleich neu belegt, sondern aus T-241/T-275
  uebernommen (auftragsgemaess).
- Warnungsdatei 33 statt 37 Zeilen - erklaert (s. o.), kein neuer Fehlertyp.

## Ungeprueft

- Clean-Room-Installation, Update-Pfad (1.12.x -> 1.13.0), Zweitstart nach
  Neustart - nicht Teil dieses Auftrags (nur Startprobe, keine Schreibaktion).
- Windows ARM64, Windows 8.1/aelter, Linux/macOS - kein Ziel laut `CLAUDE.md`.

## An `developer`

Nebenfund, kein Blocker: HEAD-Commit `0d14a0e` traegt "AK-312" fuer die
Enter-Tasten-Navigation; der Auftrag T-279 ordnete AK-312 dem
Effektfilter-Fenster zu. Beide Funktionen sind im Baum (AK-300-311 fuer das
Fenster, AK-312 fuer die Enter-Taste); nur die Nummernzuordnung im
Auftragstext war ungenau. Fuer den `notes`-Lauf relevant (CHANGELOG-Text).

## An `power-user` (Ausgangspunkt, falls angefordert)

- **Pfad:** `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe`
- **Groesse:** 59.201.789 Byte (56,46 MiB)
- **SHA-256:** `332955EC291308334CD3E2ED6437BA90EBB6E543A4F7FCD7A4A0FA56D3701113`
- **Versionsressource:** 1.13.0, am Fenstertitel bestaetigt (Startprobe).
- **Fuer den Update-Pfad-Test:** Vorversion 1.12.3 liegt gesichert unter
  `C:\Users\Daniel\AppData\Local\Temp\claude\C--Users-Daniel-Desktop-ClaudeCode-Nightreign-Helper\1102cb1a-733e-4319-a4c2-e819573c0f84\scratchpad\artefakte\NightreignHelper-1.12.3.exe`,
  SHA-256 `1C8B4FF52286928B7FC795CC65597BF7F0A65ED40C987C7FE63D0E9E2BB4DC88`
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
3. Nebenfund AK-312/Effektfilter-Fenster (s. o. "An developer") fuer den
   `notes`-Lauf beachten.
4. Arbeitsbaum war beim Bau sauber, unveraendert nach dem Bau (`dist/`,
   `build/` ignoriert; einziger Commit ist der Versionsbump `5c07392`).
