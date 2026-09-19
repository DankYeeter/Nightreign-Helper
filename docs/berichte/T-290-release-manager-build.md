STATUS: erledigt
AUFTRAG: T-290a - Artefakt 1.13.2 bauen (release-manager, Modus `build`)
GELESEN: docs/legal/AUFLAGEN.md (vollstaendig, 559 Zeilen; juengster Abschnitt
"Auflagen vor der Veroeffentlichung 1.13.1", Stand `1f51485`, keine Auflage auf
ROT, Bau/Eigenlauf bleibt GRUEN nach T-241a); docs/berichte/T-282-release-manager-build.md
(Vorlage); docs/tasks/T-290.md; CLAUDE.md; nrplanner/__init__.py (vor
Aenderung: 1.13.1); .gitignore (`dist/`, `build/` beide erfasst);
requirements.txt
GEAENDERT: nrplanner/__init__.py (`__version__` 1.13.1 -> 1.13.2, Commit
`7d2a100`); dist/NightreignHelper.exe (neu gebaut, zwei Laeufe - siehe Befund
unten). Sicherungskopie der Vorversion 1.13.1 nach
`<scratchpad>/artefakte/NightreignHelper-1.13.1.exe` (Hash gegen das im
Arbeitsbaum liegende Original verifiziert, vor dem Loeschen von `dist/`). Kein
Anwendungscode angefasst.
ANNAHMEN: Versionssprung 1.13.1 -> 1.13.2 (Patch) fuer einen reinen Bugfix
(AK-314, zwei Commits `bc4443e`/`1be0d9e`) - keine neue Funktion, Patch-Ziffer
korrekt, keine Ruecksprache noetig.
NAECHSTER: T-290b (qa-engineer, nach dem Ingame-Test des Nutzers), T-290c
(security-reviewer), laut Auftrag in dieser Reihenfolge nach dem Nutzertest.
BLOCKIERT DURCH: nichts fuer diesen Bau.

---

# T-290a - Bau 1.13.2

## Kontraktblock

| | |
|---|---|
| **Pfad** | `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe` |
| **Groesse** | 59.129.818 Byte (56,38 MiB) |
| **SHA-256** | `F988C5207AF533F7E6EE993F4B91A2C23D1FC43538799C7C35425A7EA8B82367` (`Get-FileHash -Algorithm SHA256`) |
| **Versionsbump-Commit** | `7d2a100` ("chore(release): Version 1.13.2") |
| **Code-Stand des Artefakts** | `1be0d9e` (letzter Anwendungscode-Commit vor dem Bump), Branch `docs/audit-and-advisor-design` |
| **Dauer (gueltiger Lauf)** | 47,48 s (Wanduhr; PyInstaller-Log "Build complete!" bei 47,214 s - konsistent) |
| **UPX** | nicht im `PATH` (`where upx`: "Could not find files") - `upx=True` im `.spec` bleibt wirkungslos, wie in jedem vorherigen Bau |
| **`scripts/check_licences.py`** | `OK`, alle drei Pflichtdateien und alle sechs Bibliotheken erfasst |

## Pflichtlektuere: `docs/legal/AUFLAGEN.md`

Volltext gelesen (559 Zeilen). Kein Eintrag auf ROT, der diesen Lauf sperrt:
A-010 ist ROT, aber ausdruecklich "sperrt nicht mehr" (Nutzer-Ruecksstellung
02.09., Abnahme 09.09.). Der juengste Abschnitt (T-283c, Stand `1f51485`,
16.09.) haelt fest, dass A-020/A-023/A-030/A-031/A-035 fuer 1.13.1 erfuellt
bzw. GRUEN sind und nichts auf ROT steht; die T-241a-Einordnung
"Bau/Eigenlauf: GRUEN" gilt seither unveraendert fort - kein neuer
Abschnitt seit `1f51485` ausser diesem Bau selbst. Dieser Lauf ist kein
Release (kein Push, kein Tag, keine Weitergabe der EXE) - `build` ist nicht
gesperrt.

## Ausgangsstand

`git status --porcelain` vor dem ersten Schritt: leer, Baum sauber. HEAD
`427b434` entspricht dem beauftragten Stand (Auftrag nennt `427b434`; die
Praemisse "Stand `1be0d9e`" im Auftragskopf ist der letzte
Anwendungscode-Commit, `427b434` ist ein reiner Doku-Commit darueber - kein
Widerspruch). Seit dem 1.13.1-Bump (`b46641c`) genau zwei
Anwendungscode-Commits im Baum: `bc4443e` und `1be0d9e` (beide AK-314), plus
`986216d` (Hook, kein Anwendungscode).

## Sicherung der Vorversion 1.13.1

In `dist/` lag noch das Artefakt aus T-282: Groesse 59.201.630 Byte, SHA-256
`71E8202980BA528119815C75818757668EA956480A918C0236D1C8E420E67E1C` -
deckungsgleich mit dem in T-282 gefuehrten Wert. Kopiert nach
`<scratchpad>/artefakte/NightreignHelper-1.13.1.exe`, Hash der Kopie erneut
geprueft: identisch.

## Versionsbump

`nrplanner/__init__.py`: `__version__` 1.13.1 -> 1.13.2, ein Commit
(`7d2a100`, `-- nrplanner/__init__.py`).

## Befund: erster Bau lief gegen die falsche Python-Umgebung

Vor dem Loeschen von `dist/`/`build/` (`Get-Process -Name NightreignHelper`:
kein Treffer) wurde der erste Bau ueber `python -m PyInstaller
NightreignHelper.spec` gestartet. `python` loeste dabei auf die
system-globale Installation auf
(`C:\Users\Daniel\AppData\Local\Programs\Python\Python312\python.exe`, **nicht**
das projekteigene `.venv`), mit PyInstaller 6.22.1 statt der in
`requirements.txt` gepinnten 6.21.0 und einem global installierten `numpy`
(2.5.2), das in `requirements.txt` nirgends vorkommt. Sichtbare Folge: die
Warnungsdatei sprang von 33 Zeilen (T-282, Referenzwert) auf 228 - fast
vollstaendig `numpy._core.*`-Introspektionszeilen der neueren Hook-Version.
**Dieser erste Lauf wurde verworfen** (`dist`/`build` erneut geloescht) und
durch einen zweiten Lauf ueber `.\.venv\Scripts\python.exe -m PyInstaller`
ersetzt - dort ist `numpy` nicht installiert (`pip show numpy` im `.venv`:
"Package(s) not found") und PyInstaller ist die gepinnte 6.21.0. **Nur der
zweite Lauf ist das ausgelieferte Artefakt**; die Zahlen im Kontraktblock
stammen aus diesem Lauf. Ursache des Fehlgriffs: `python` im PATH dieser
Shell zeigt nicht auf `.venv` - ein Befund fuer den `developer`/`architect`
unten, kein Blocker fuer diesen Bau.

## Bau, gueltiger Lauf (`.venv`)

| | Lauf |
|---|---|
| `rc` | 0 ("Build complete!", 0 Treffer fuer `error`/`deprecat` im Log) |
| Dauer | 47,48 s |
| Groesse | 59.129.818 Byte |
| SHA-256 | `F988C5207AF533F7E6EE993F4B91A2C23D1FC43538799C7C35425A7EA8B82367` |

Zweiter Lauf im Sinne einer Reproduzierbarkeitspruefung (Bit-Identitaet)
entfaellt - Auftrag nennt keinen Zweitbau, interne Bit-Nichtidentitaet
zwischen Laeufen ist in T-241/T-275/T-279 bereits mehrfach belegt (PE-
Baustempel, Modulreihenfolgen-Vertauschung) und wird hier nicht erneut
nachgewiesen. Die beiden hier ausgefuehrten Laeufe sind **keine** Wiederholung
desselben Vorgangs, sondern unterschiedliche Umgebungen (siehe Befund oben)
und daher fuer diesen Vergleich nicht heranzuziehen.

Warnungsdatei (`.venv`-Lauf): **37 Zeilen** gegen 33 in T-282. Differenz
gelesen und erklaerbar: eine neue Zeile "missing module named numpy -
imported by PIL._typing (conditional, optional)" (Pillow bietet seit einem
Minor-Update optionale NumPy-Typhinweise an - harmlos, `numpy` wird nicht
gebuendelt) sowie geringfuegig andere Wortwahl in drei bestehenden Zeilen
(`pyinstaller-hooks-contrib` im `.venv` ist 2026.7, T-282 nennt keine
Version). Keine neue Warnungsart, kein fehlender Bestandteil.

Groessendifferenz zu 1.13.1 (59.201.630 Byte): **-71.812 Byte (-0,12 %)** -
plausibel: zwei kleine Fix-Commits ohne neue Abhaengigkeit sind der einzige
Unterschied im Baum; die Richtung (kleiner statt groesser) liegt in der
ueblichen Kompressions-/Layout-Schwankung zwischen Baeumen.

## Startprobe

Isolierung: `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-290`,
`LOCALAPPDATA`/`APPDATA` auf `<scratchpad>/T-290/release-manager/localappdata`
bzw. `appdata` umgelenkt (in derselben Kommandozeile wie der Start, sonst
sperrt der Hook). Testabzug `NightreignHelper-Testabzug` (841 Dateien,
`EXTRACT_VERSION` 12, weiterhin gueltig) nach `<localappdata>\NightreignHelper`
**kopiert**, nicht verlinkt (Dateizahl nach dem Kopieren erneut gezaehlt: 841).
Vor dem Start `Get-Process -Name NightreignHelper`: kein Treffer.

- **Start:** `dist\NightreignHelper.exe` gestartet, nach 11 s weiterhin aktiv.
  PyInstaller-Onefile erzeugt zwei Prozesse (Bootloader-PID ohne Fenstertitel,
  Kind-PID mit Fenster) - beide `Responding` = `True`, `HasExited` = `False`.
- **Fenstertitel:** "Nightreign Helper 1.13.2" (Kind-Prozess) -
  Versionsressource stimmt mit dem Bump ueberein.
- **Echte Schreibaktion:** `reg query`/`Get-ChildItem HKCU:\Software\DankYeeterT-290`
  findet nach dem Lauf `NightreignHelper`, `NightreignHelper\builds\1`,
  `NightreignHelper\chalices\1` - die Testorganisation, nicht `DankYeeter`. Die
  echten Nutzerdaten (309 Relikte, ~110 Builds unter `HKCU\Software\DankYeeter`)
  wurden nicht beruehrt (nicht erneut ausgelesen - Positivnachweis der
  Umlenkung genuegt laut CLAUDE.md). Dateizahl im umgelenkten `LOCALAPPDATA`
  nach dem Lauf weiterhin 841 - der Testabzug bleibt unveraendert (read-only
  bestaetigt).
- **Beendet:** `Stop-Process -Force` auf beide `NightreignHelper`-PIDs; danach
  `Get-Process -Name NightreignHelper`: kein Treffer.

Keine ueber die Startprobe hinausgehende Schreibaktion (Update-Pfad,
Neustart-Probe) ausgefuehrt - das ist `clean-room`, nicht Teil dieses
Auftrags.

## Blocker

Keiner fuer diesen Bau.

## Risiken

- Kein UPX auf diesem Bau-Wirt - unveraendert.
- Nur ein gueltiger Lauf: interne Reproduzierbarkeit (Bit-Identitaet zwischen
  zwei Laeufen derselben Umgebung) wurde nicht neu belegt, sondern aus
  T-241/T-275/T-279 uebernommen (auftragsgemaess).
- Der verworfene erste Lauf zeigt, dass `python` in dieser Shell nicht auf das
  projekteigene `.venv` zeigt. Ohne die Pruefung der Warnungsdatei waere ein
  Artefakt mit einer aus `requirements.txt` nicht ersichtlichen,
  ungewollten `numpy`-Introspektion durch die Pruefkette gelaufen - keine
  Auswirkung auf das ausgelieferte Artefakt (verworfen), aber ein Befund fuer
  die Bau-Anleitung.

## Ungeprueft

- Clean-Room-Installation, Update-Pfad (1.13.1 -> 1.13.2), Zweitstart nach
  Neustart - nicht Teil dieses Auftrags (nur Startprobe, keine
  Schreibaktion darueber hinaus).
- Windows ARM64, Windows 8.1/aelter, Linux/macOS - kein Ziel laut `CLAUDE.md`.

## An `developer`

- **Kein Befund am Anwendungscode selbst.** Ein Befund an der Bau-Umgebung:
  `python` im PATH dieser Maschine loest auf die system-globale Installation
  auf, nicht auf `.venv\Scripts\python.exe`. Ein Bau-Rezept, das `python -m
  PyInstaller ...` ohne expliziten `.venv`-Pfad aufruft, kann ein Artefakt
  mit ungepinnten, projektfremden Paketen erzeugen (hier: PyInstaller 6.22.1
  statt 6.21.0, ein zufaellig global installiertes `numpy`). Empfehlung: das
  Bau-Rezept (Doku oder Skript) ruft ausdruecklich `.venv\Scripts\python.exe`
  auf, nicht `python`. Kein Anwendungscode betroffen, daher keine
  Auflage/Blocker, nur eine Anleitungsluecke.

## An `power-user` (Ausgangspunkt, falls angefordert)

- **Pfad:** `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe`
- **Groesse:** 59.129.818 Byte (56,38 MiB)
- **SHA-256:** `F988C5207AF533F7E6EE993F4B91A2C23D1FC43538799C7C35425A7EA8B82367`
- **Versionsressource:** 1.13.2, am Fenstertitel bestaetigt (Startprobe).
- **Fuer den Update-Pfad-Test:** Vorversion 1.13.1 liegt gesichert unter
  `C:\Users\Daniel\AppData\Local\Temp\claude\C--Users-Daniel-Desktop-ClaudeCode-Nightreign-Helper\0c1b1951-b796-49a5-9cbc-7588742f286c\scratchpad\artefakte\NightreignHelper-1.13.1.exe`,
  SHA-256 `71E8202980BA528119815C75818757668EA956480A918C0236D1C8E420E67E1C`
  (gegen Original verifiziert).
- Drei Umlenkungen zwingend beim Start: `NIGHTREIGN_SETTINGS_ORG`,
  `LOCALAPPDATA`, `APPDATA` - Testabzug kopieren, nicht darauf zeigen
  (`CLAUDE.md`).
- Kein laufender `NightreignHelper.exe`-Prozess nach diesem Lauf (`Get-Process`
  geprueft) - vor eigenem Start dennoch selbst pruefen (NH-004, maschinenweite
  Instanzsperre).

## An `director`

**Empfehlung: freigeben mit benannter Einschraenkung** (fuer den Weiterlauf zu
T-290b/T-290c nach dem Ingame-Test des Nutzers - kein Release-Votum, das
bleibt an A-025 und eine ausdrueckliche Weitergabe-Entscheidung gebunden).

1. Kein `.gitignore`-Nachtrag noetig (`dist/`, `build/` bereits erfasst).
2. Keine offene rote Auflage - Build war nicht gesperrt.
3. Arbeitsbaum war beim Bau sauber, unveraendert nach dem Bau (`dist/`,
   `build/` ignoriert; einziger Commit ist der Versionsbump `7d2a100`).
4. **Befund zur Bau-Umgebung** (siehe "An `developer`" oben): der erste
   Bau-Versuch lief unbeabsichtigt gegen die system-globale Python-Installation
   statt `.venv` und wurde deshalb verworfen. Das ausgelieferte Artefakt stammt
   ausschliesslich aus dem `.venv`-Lauf.
5. Tag-Vorschlag (nicht gesetzt, Sache des `director`/`archivist`): `v1.13.2`
   auf `7d2a100`.
