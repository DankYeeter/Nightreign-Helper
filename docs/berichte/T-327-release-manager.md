STATUS: erledigt
AUFTRAG: T-327g - Artefakt 1.18.0 bauen (release-manager, Modus `build`),
Abschnitt T-327g aus `docs/tasks/T-327.md`, Stand HEAD (`git log --oneline -1`:
`03c6b78`, Version 1.18.0 seit `7a8276e`, Code-Stand A27 `5a35272`). Wie
T-325k (`docs/berichte/T-325-release-manager.md`). Parallel lief nur eine
Leserolle (security-reviewer). Umlenkung `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-327g`,
eigenes LOCALAPPDATA/APPDATA, Testabzug v16 kopieren, NH-004.
GELESEN: docs/legal/AUFLAGEN.md (vollstaendig, 559 Zeilen). Juengster
Abschnitt "Auflagen vor der Veroeffentlichung 1.13.1" (T-283c, Stand
`1f51485`, 16.09.2026). Gesamtampel GELB, **keine Auflage steht auf ROT mit
sperrender Wirkung**: A-010 ist ROT, aber ausdruecklich "sperrt nicht mehr"
(Nutzer-Rueckstellung 02.09., Abnahme 09.09.); A-025 (GRAU, EXE-Weitergabe)
ist entschieden (FORTSETZEN, 09.09.) und betrifft ohnehin nur Weitergabe,
nicht diesen Bau. Seit T-283c (16.09.) kein neuer Abschnitt in der Datei -
dieselbe Lage wie beim letzten `build`-Lauf (T-325k, 21.09.). Dieser Lauf ist
kein Release (kein Push, kein Tag, keine Weitergabe der EXE an Dritte) -
`build` ist nicht gesperrt. Weiter gelesen: `docs/tasks/T-327.md` (Abschnitt
T-327g); `docs/berichte/T-325-release-manager.md` (Rezept T-325k, wie im
Auftrag verlangt); `CLAUDE.md`.
GEAENDERT: `dist/NightreignHelper.exe` neu gebaut (Code-Stand `5a35272`,
gitignored). `dist/`/`build/` enthielten vor dem Bau noch das T-325k-Artefakt
(59.250.281 Byte, SHA-256 `BFEEB027...`, byteidentisch mit dem dort
dokumentierten Bau - unaufgeraeumter Ruecklauf, kein neuer Anwendungscode
angefasst) - vor dem Bau geloescht. Neu: diese Datei.
ANNAHMEN: keine ueber den Auftragstext hinaus. "Wie T-325k" gelesen als
derselbe Ablauf: ein Bau, Rauchtest mit sofortigem Beenden, kein Update-Pfad,
kein Zweitbau zur Bit-Identitaetspruefung (Begruendung siehe T-325f/T-325k,
unveraendert gueltig).
NAECHSTER: T-327h (release-manager, Modus `notes`), danach Release nach
Nutzerfreigabe (Auftrag: "Nutzer 21.09. 19:25: kurze Kette").
BLOCKIERT DURCH: nichts fuer diesen Bau.

---

# T-327g - Bau 1.18.0

## Kontraktblock

| | |
|---|---|
| **Pfad** | `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe` |
| **Groesse** | 59.184.762 Byte (56,44 MiB) |
| **SHA-256** | `89DAACBBB8D6F74B446C5FFA37FD3B47B0EB1C5B07079D20D65ECE05DF0ADCCC` |
| **Code-Stand des Artefakts** | `5a35272` (= HEAD `03c6b78` App-Code; `git diff --stat 5a35272..HEAD` zeigt nur `docs/anleitung/guide.md`, 0 Treffer unter `nrplanner/`) |
| **Version** | 1.18.0 (`nrplanner/__init__.py`, T-327d), am Fenstertitel bestaetigt |
| **Dauer** | 45,0 s (PyInstaller-Eigenzeit: erste Log-Zeile `107 INFO`, letzte `45104 INFO: Build complete!`) |
| **UPX** | nicht im `PATH` (`where.exe upx`: "Could not find files", exit 1) - `upx=True` im `.spec` bleibt wirkungslos, wie in jedem vorherigen Bau |
| **`scripts/check_licences.py`** | `OK`, alle drei Pflichtdateien und alle fuenf `requirements.txt`-Bibliotheken erfasst |

## Ausgangsstand

`git status --porcelain -uall` vor dem ersten Schritt: leer, Arbeitsbaum
sauber. `git rev-parse HEAD`: `03c6b78b72c850822831ddee82703a88c2e6284e`.
`nrplanner/__init__.py` gelesen: `__version__ = "1.18.0"`.

`git diff --stat 7a8276e..HEAD` (Versionsbump-Commit bis HEAD): nur
`docs/anleitung/guide.md` (+30 Zeilen, T-327f) - kein Anwendungscode seit dem
Versionsbump. `git diff --stat v1.17.0..HEAD -- nrplanner/ requirements.txt
requirements-dev.txt NightreignHelper.spec .gitignore` (Vergleich zum letzten
Release): `nrplanner/__init__.py`, `advisor/explain.py` (+138/-?),
`advisor/goals.py` (-95 Netto, Funktion in die Fassade gehoben, AD-019/038/
052/053), `damage.py` (+140), `statsheet.py` (+229) - insgesamt 474
Einfuegungen/130 Loeschungen, deckt A27 (Weapon art/Spell damage) und
QA-293/294. Keine neue Abhaengigkeit: `requirements.txt`,
`requirements-dev.txt`, `NightreignHelper.spec`, `.gitignore` im selben Diff
0 Treffer.

`dist/`/`build/` enthielten vor dem Bau noch das T-325k-Artefakt (59.250.281
Byte, SHA-256 `BFEEB0270D16C88FDEC67DF10F2D5C76FD29AB5002F6EEC2E14691F321E7C4B4`
- unabhaengig nachgemessen, deckungsgleich mit dem in
`docs/berichte/T-325-release-manager.md` dokumentierten Bau, also derselbe
Ruecklauf, nicht aufgeraeumt). `Get-Process -Name NightreignHelper` vor dem
Loeschen: 0 Treffer - kein Nutzerlauf betroffen. `dist/`/`build/` sind
gitignored (`.gitignore` Z. 9-10), also keine Abweichung im `git status`.

## Bau

`Get-Process -Name NightreignHelper`: 0 Treffer unmittelbar vor dem Loeschen
von `dist/`/`build/` und unmittelbar vor dem Aufruf. Bau ausschliesslich ueber
`./.venv/Scripts/python.exe -m PyInstaller NightreignHelper.spec` (`.venv`
Python 3.12.10; kein globales `python`). PyInstaller 6.21.0, contrib hooks
2026.7, Plattform Windows-11-10.0.26200-SP0.

| | Lauf |
|---|---|
| `rc` | 0 ("Build complete!") |
| Dauer (PyInstaller-Eigenzeit) | 45,0 s |
| Groesse | 59.184.762 Byte |
| SHA-256 | `89daacbbb8d6f74b446c5ffa37fd3b47b0eb1c5b07079d20d65ece05df0adccc` |

Zweiter Lauf zur Reproduzierbarkeitspruefung (Bit-Identitaet) entfaellt - wie
T-325f/T-325k, mit derselben Begruendung (interne Bit-Nichtidentitaet
zwischen Laeufen derselben Umgebung ist in mehreren Vorlaeufern bereits
belegt; der Auftrag verweist ausdruecklich auf T-325k, das denselben
Verzicht traegt).

Build-Log (`t327g-build1.log`, im Scratchpad gesichert, vollstaendig
gelesen): 0 Treffer fuer "error" (kein PowerShell-Umleitungsartefakt diesmal,
da direkt in eine Datei umgeleitet statt ueber `*>` in der Konsole), 0
Treffer fuer "deprecat". Warnungsdatei
(`build/NightreignHelper/warn-NightreignHelper.txt`, `wc -l`): **37 Zeilen**
(davon 21 `missing module`) - zahlengleich mit T-325f/T-325k und allen
frueheren dokumentierten Bauten; keine neue, unerklaerte Warnung.

Groessendifferenz zum letzten dokumentierten Bau (T-325k, 1.17.0,
59.250.281 Byte): **-65.519 Byte (-0,11 %)** trotz eines Netto-Zuwachses von
+344 Zeilen Anwendungscode (474 Einfuegungen/130 Loeschungen, siehe oben) -
passt der Richtung nach nicht zum reinen Codezuwachs, liegt aber innerhalb
der bereits in T-322b/T-322h/T-325f/T-325k dokumentierten Bau-zu-Bau-Streuung
fuer diesen Bau-Wirt (dort wechselten die Vorzeichen ebenfalls zwischen den
Bauten). Keine neue Abhaengigkeit im Diff (siehe Ausgangsstand) - die
Streuung ist damit nicht durch ein neues Paket erklaerbar.

## Testabzug

`C:\Users\Daniel\Desktop\ClaudeCode\NightreignHelper-Testabzug` unabhaengig
nachgezaehlt vor dem Kopieren: **841 Dateien, 21.139.391 Byte** -
deckungsgleich mit dem im Auftrag genannten Stand v16. Nach
`<scratchpad>\T-327g\localappdata\NightreignHelper` **kopiert** (nicht
verlinkt, nicht unter echtem `%LOCALAPPDATA%`). Nach dem Kopieren erneut
gezaehlt: 841 Dateien / 21.139.391 Byte, deckungsgleich. Nach dem Rauchtest
an der **Quelle** erneut gezaehlt: weiterhin 841 Dateien / 21.139.391 Byte,
unveraendert (read-only bestaetigt).

## Startprobe (Rauchtest, NH-004)

Vor dem Start: `Get-Process -Name NightreignHelper` = 0 Treffer - keine Kopie
des Nutzers lief, keine Wartezeit noetig.

Isolierung: `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-327g`, `LOCALAPPDATA`/
`APPDATA` auf `<scratchpad>\T-327g\localappdata` bzw. `appdata` umgelenkt (in
derselben PowerShell-Sitzung wie der Start).

- **Start:** `dist\NightreignHelper.exe` gestartet, nach 8 s zwei Prozesse
  (Bootloader-PID 11888, Kind-PID 33448), beide `Responding = True`.
- **Fenstertitel:** "Nightreign Helper 1.18.0" - Version am Fenster
  bestaetigt.
- **Echte Schreibaktion:** `Get-ChildItem HKCU:\Software\DankYeeterT-327g`
  findet nach dem Start `NightreignHelper\builds\1` und
  `NightreignHelper\chalices\1` (Autoimport aus dem umgelenkten Testabzug,
  Werte `__last`/`__deep`/`__schema`/`__imported` etc. befuellt) - die
  Testorganisation, nicht `DankYeeter`. Die echten Nutzerdaten (309 Relikte,
  ~110 Builds unter `HKCU\Software\DankYeeter`) wurden nicht beruehrt
  (Positivnachweis der Umlenkung genuegt laut `CLAUDE.md`;
  `HKCU:\Software\DankYeeter` vor und nach dem Lauf mit `Test-Path` gepruft:
  beide Male `True`, Inhalt nicht erneut gelesen).
- **Beendet sofort** (NH-004, ein Fensterlauf je Zeitpunkt): `Stop-Process
  -Force` auf beide `NightreignHelper`-PIDs, 1 s Wartezeit, danach
  `Get-Process -Name NightreignHelper`: **0 Treffer** - belegt.
- **Aufraeumen:** Testregistrierung `HKCU:\Software\DankYeeterT-327g`
  entfernt (`Test-Path` danach `False`; `HKCU:\Software\DankYeeter`
  weiterhin `True`, unberuehrt); Scratchpad-Testabzug (`localappdata`,
  `appdata`) geloescht (`Test-Path` danach `False` fuer beide); Umgebungs-
  variablen zurueckgesetzt (`NIGHTREIGN_SETTINGS_ORG` entfernt,
  `LOCALAPPDATA`/`APPDATA` auf die echten Pfade des Nutzers gesetzt);
  Build-Log verbleibt im Scratchpad (nicht im Repo, `git status` danach
  leer).

Keine ueber die Startprobe hinausgehende Schreibaktion (Update-Pfad,
Neustart-Probe, fachliche A27-Bedienhandlung mit Revenant/Wylder) ausgefuehrt
- der Auftrag nennt fuer diesen Bau nur den Rauchtest; die fachliche Pruefung
ist bereits in T-327c (qa-engineer, Quellstand) gelaufen, eine
Clean-Room-Installation ist fuer diese Kette nicht beauftragt.

## Blocker

Keiner fuer diesen Bau.

## Risiken

- Kein UPX auf diesem Bau-Wirt - unveraendert seit allen dokumentierten
  Vorlaeufern.
- Nur ein gueltiger Lauf: interne Reproduzierbarkeit (Bit-Identitaet
  zwischen zwei Laeufen derselben Umgebung) wurde nicht neu belegt, sondern
  aus den in T-325f/T-325k genannten Vorlaeufern uebernommen (auftragsgemaess,
  kein Zweitbau verlangt).
- Groessenabweichung -0,11 % trotz Codezuwachs (siehe Bau-Abschnitt) - nach
  bisheriger Aktenlage reine Bau-Streuung, aber nicht mit einem Zweitbau
  gegengeprueft in diesem Lauf.
- Keine Clean-Room-Installation und kein Update-Pfad in dieser Kette geprueft
  - siehe "Ungeprueft".
- `docs/legal/AUFLAGEN.md` ist seit T-283c (16.09., 1.13.1) nicht
  fortgeschrieben, obwohl 1.14.0-1.18.0 seither erschienen sind - unveraendert
  seit T-325n gemeldete Buchfuehrungsluecke, kein neuer Befund, keine
  Blockade fuer diesen Bau (dieselbe GELB-Lage, keine neue Auflage in Sicht).

## Ungeprueft

- Clean-Room-Installation, Update-Pfad (1.17.0 -> 1.18.0), Zweitstart nach
  Neustart - nicht Teil dieses Auftrags (Kette nennt nur `build` -> `notes`
  -> Release, keinen `clean-room`-Lauf).
- Windows ARM64, Windows 8.1/aelter, Linux/macOS - kein Ziel laut `CLAUDE.md`.
- Die fachliche A27-Pruefung selbst (Revenant/Beast-Claw, Wylder/Skill-Buff)
  - das ist T-327c (qa-engineer, bereits am Quellstand bestanden laut
  `docs/berichte/T-327-qa-engineer.md`), nicht dieser Bau.

## An `developer`

Kein Befund am Anwendungscode.

## An `power-user` (Ausgangspunkt, falls angefordert)

- **Pfad:** `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe`
- **Groesse:** 59.184.762 Byte (56,44 MiB)
- **SHA-256:** `89DAACBBB8D6F74B446C5FFA37FD3B47B0EB1C5B07079D20D65ECE05DF0ADCCC`
- **Versionsressource:** 1.18.0, am Fenstertitel bestaetigt (Startprobe).
- Dieses Artefakt ersetzt das T-325k-Artefakt (SHA-256 `BFEEB027...`, 1.17.0).
- Drei Umlenkungen zwingend beim Start: `NIGHTREIGN_SETTINGS_ORG`,
  `LOCALAPPDATA`, `APPDATA` - Testabzug **v16** (841 Dateien, 21.139.391
  Byte) kopieren, nicht darauf zeigen (`CLAUDE.md`, Auftrag).
- Kein laufender `NightreignHelper.exe`-Prozess nach diesem Lauf
  (`Get-Process` geprueft, 0 Treffer) - vor eigenem Start dennoch selbst
  pruefen (NH-004, maschinenweite Instanzsperre).
- Kein `clean-room`-Lauf in dieser Kette vorgelagert - falls eine
  Ersteinrichtungspruefung gewuenscht ist, fehlt sie noch (siehe
  "Ungeprueft").

## An `director`

**Empfehlung: freigeben mit benannter Einschraenkung** (fuer den Weiterlauf
zu T-327h `notes` - kein Release-Votum, das bleibt an A-025 und eine
ausdrueckliche Weitergabe-Entscheidung gebunden, die am 09.09. bereits als
FORTSETZEN entschieden ist).

1. Auflagenlage: keine ROT-Auflage sperrt (siehe GELESEN). Nebenfund
   unveraendert seit T-325n: `docs/legal/AUFLAGEN.md` ist seit T-283c
   (16.09., 1.13.1) nicht fortgeschrieben, obwohl 1.14.0-1.18.0 seither
   erschienen sind - keine Blockade, aber weiterhin eine Buchfuehrungsluecke.
2. Kein `.gitignore`-Nachtrag noetig (`dist/`, `build/` bereits erfasst).
3. Arbeitsbaum war beim Bau sauber und blieb es (kein Anwendungscode
   angefasst); `dist/`/`build/` weiterhin ignoriert.
4. Tag-Vorschlag: keiner in diesem Lauf - 1.18.0 ist unveroeffentlicht, Notes
   und Tag-Vorschlag folgen in T-327h.
5. Einschraenkung: kein `clean-room`-Lauf in dieser Kette (Auftrag nennt nur
   `build` -> `notes` -> Release). Fuer eine Weitergabe an Dritte ohne
   vorherige Ersteinrichtungspruefung bleibt der Update-Pfad ungeprueft -
   Entscheidung, ob das fuer diese kurze Kette ausreicht, liegt beim
   `director`/Nutzer.
