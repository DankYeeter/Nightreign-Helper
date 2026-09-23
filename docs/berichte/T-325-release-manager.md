STATUS: erledigt
AUFTRAG: T-325f - Artefakt 1.17.0 bauen (release-manager, Modus `build`),
nach T-325b (Versionsbump) und T-325e (Startbreite), Stand `f24376b`
(`docs/tasks/T-325.md`, Rezept wie T-322b/h,
`docs/berichte/T-322-release-manager.md`).
GELESEN: docs/legal/AUFLAGEN.md (vollstaendig, 558 Zeilen; juengster
Abschnitt "Auflagen vor der Veroeffentlichung 1.13.1", T-283c, Stand
`1f51485`, letzter aendernder Commit auf der Datei weiterhin `cc92066`
(16.09.) - seit dem T-322h-Bau unveraendert, keine neue Auflage; Gesamtampel
GELB, keine Auflage steht auf ROT mit sperrender Wirkung: A-010 ist ROT, aber
ausdruecklich "sperrt nicht mehr"; die T-241a-Einordnung "Bau/Eigenlauf:
GRUEN" gilt fort); docs/tasks/T-325.md (Abschnitt T-325f); docs/berichte/
T-322-release-manager.md (Rezept, wie im Auftrag verlangt); CLAUDE.md.
GEAENDERT: dist/NightreignHelper.exe neu gebaut (Code-Stand `f24376b`,
gitignored). Altes `dist/`/`build/` enthielt noch einen Vorlauf (59.233.451
Byte, LastWriteTime 20.09. 16:41 - vermutlich ein Entwicklerbau aus T-325b/e,
kein SHA-Abgleich noetig) - vor dem Bau geloescht, kein Anwendungscode
angefasst. Neu: diese Datei.
ANNAHMEN: keine ueber den Auftragstext hinaus. "Rezept wie T-322b/h" gelesen
als derselbe Ablauf: ein Bau, Rauchtest mit sofortigem Beenden, kein
Update-Pfad, kein Zweitbau zur Bit-Identitaetspruefung.
NAECHSTER: T-325g (ui-ux-designer, Review, parallel bereits gelaufen) und
T-325h (qa-engineer, QA am Artefakt aus diesem Lauf, Nachweis A26).
BLOCKIERT DURCH: nichts fuer diesen Bau.

---

# T-325f - Bau 1.17.0

## Kontraktblock

| | |
|---|---|
| **Pfad** | `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe` |
| **Groesse** | 59.249.345 Byte (56,50 MiB) |
| **SHA-256** | `D136FB2DCAA9F4C44C9D23557F05ED2206C75BBF7D71128EA47F4065BA120101` |
| **Code-Stand des Artefakts** | `f24376b` (HEAD, Branch `docs/audit-and-advisor-design`) |
| **Version** | 1.17.0 (T-325b), am Fenstertitel bestaetigt |
| **Dauer** | 40,7 s (PyInstaller-Eigenzeit, `40501 INFO: Build complete!` minus `121 INFO:` Startzeile) |
| **UPX** | nicht im `PATH` (`where upx`: "Could not find files") - `upx=True` im `.spec` bleibt wirkungslos, wie in jedem vorherigen Bau |
| **`scripts/check_licences.py`** | `OK`, alle drei Pflichtdateien und alle fuenf `requirements.txt`-Bibliotheken erfasst |

## Pflichtlektuere `docs/legal/AUFLAGEN.md`

Volltext gelesen (558 Zeilen). `git log -1 -- docs/legal/AUFLAGEN.md`:
`cc92066` (16.09.2026, T-283c, "Auflagen vor der Veroeffentlichung 1.13.1")
- identisch mit dem Stand, den T-322b/h bereits gegen dieselbe Datei gelesen
hatten; seither kein neuer Commit auf der Datei, also keine neue Auflage.
Gesamtampel GELB, keine Auflage steht auf ROT mit sperrender Wirkung: A-010
ist ROT, aber ausdruecklich "sperrt nicht mehr" (Nutzer-Rueckstellung 02.09.,
Abnahme 09.09.). Die T-241a-Einordnung "Bau/Eigenlauf: GRUEN" (Modus
`auflagen`, 14.09.) gilt seither unveraendert fort und ist durch die
spaeteren Abschnitte (T-283c, 16.09.) nicht revidiert worden. Dieser Lauf ist
kein Release (kein Push, kein Tag, keine Weitergabe der EXE an Dritte) -
`build` ist nicht gesperrt. A-025 (EXE-Weitergabe) bleibt unberuehrt, weil
dieser Lauf nichts weitergibt.

## Ausgangsstand

`git status --porcelain -uall` vor dem ersten Schritt: leer, Arbeitsbaum
sauber. `git rev-parse HEAD`: `f24376b1a6e3b88bc274b32f4d5e5528b7c462d6` -
identisch mit dem im Auftrag genannten Stand `f24376b`. `nrplanner/__init__.py`
gelesen: `__version__ = "1.17.0"`.

`dist/` enthielt vor dem Bau noch eine EXE (59.233.451 Byte, `LastWriteTime`
20.09.2026 16:41) - vermutlich ein Zwischenbau aus T-325b/e, kein SHA-Abgleich
gegen ein Vorlaeuferartefakt vorgenommen, da nicht Gegenstand dieses Auftrags.
`dist/`/`build/` sind gitignored (`.gitignore` Z. 9-10: `build/`, `dist/`),
also keine Abweichung im `git status`. Vor dem Loeschen: `Get-Process -Name
NightreignHelper` = 0 Treffer - kein Nutzerlauf betroffen.

## Bau

`Get-Process -Name NightreignHelper`: 0 Treffer unmittelbar vor dem Loeschen
von `dist/`/`build/` und unmittelbar vor dem Aufruf. Bau ausschliesslich ueber
`./.venv/Scripts/python.exe -m PyInstaller NightreignHelper.spec` (`.venv`
Python 3.12.10; kein globales `python`). PyInstaller 6.21.0, contrib hooks
2026.7, Plattform Windows-11-10.0.26200-SP0.

| | Lauf |
|---|---|
| `rc` | 0 ("Build complete!") |
| Dauer (PyInstaller-Eigenzeit) | 40,7 s |
| Groesse | 59.249.345 Byte |
| SHA-256 | `d136fb2dcaa9f4c44c9d23557f05ed2206c75bbf7d71128ea47f4065ba120101` |

Zweiter Lauf zur Reproduzierbarkeitspruefung (Bit-Identitaet) entfaellt -
Auftrag verweist ausdruecklich auf T-322b/h, das denselben Verzicht mit
Begruendung traegt (interne Bit-Nichtidentitaet zwischen Laeufen derselben
Umgebung ist in T-241/T-275/T-279/T-294b/T-295b/T-312a/T-313b/T-322b/T-322h
bereits mehrfach belegt).

Build-Log (`t325f-build1.log`, im Scratchpad gesichert, vollstaendig
geprueft): einziger "error"-Treffer ist derselbe PowerShell-`*>`-Artefakt wie
in T-322h (stderr-Umleitung verpackt die erste PyInstaller-INFO-Zeile als
`NativeCommandError`, `rc` bleibt 0, Build-Log endet mit "Build complete!")
- kein PyInstaller-Fehler; 0 Treffer fuer "deprecat". Warnungsdatei
(`build/NightreignHelper/warn-NightreignHelper.txt`, `wc -l`): **37 Zeilen**
(davon 21 `missing module`) - zahlengleich und inhaltsgleich mit T-322b/T-322h/
T-313b/T-312a/T-295b/T-294b (Volltext gegengelesen: dieselben 21 Module,
durchweg optionale/plattformbedingte Importe wie `pwd`, `grp`, `resource`,
`olefile`, `numpy`, `cffi`); keine neue, unerklaerte Warnung.

Groessendifferenz zum letzten dokumentierten Bau (T-322h, 1.16.0, 59.233.161
Byte): **+16.184 Byte (+0,027 %)** - `git diff --stat 5b9fad9..f24376b`
zeigt 48 geaenderte Dateien mit 5.362 Einfuegungen/402 Loeschungen, davon
Anwendungscode in `nrplanner/app.py`, `advisor/goals.py`, `advisorbar.py`,
`damage.py` (+290 Zeilen), `model.py`, `relicpicker.py` (deckt T-323/T-324/
T-325-Serie, nicht nur T-325b/e) - die geringe Groessenaenderung trotz
grossem Diff passt zur bereits dokumentierten Bau-zu-Bau-Streuung fuer diesen
Bau-Wirt; keine neue Abhaengigkeit (`requirements.txt`/`requirements-dev.txt`/
`NightreignHelper.spec`/`.gitignore` im Diff `5b9fad9..f24376b`: 0 Treffer,
`check_licences.py` unveraendert `OK`, dieselbe Bibliotheksliste).

## Testabzug

`C:\Users\Daniel\Desktop\ClaudeCode\NightreignHelper-Testabzug` unabhaengig
nachgezaehlt vor dem Kopieren: **841 Dateien, 21.139.391 Byte** - deckungsgleich
mit dem im Auftrag genannten Stand v16 (`EXTRACT_VERSION` 15 in `CLAUDE.md`
ist damit veraltet; dieser Lauf verwendet den im Auftrag genannten neueren
Abzug, kein Widerspruch, da der Auftrag ausdruecklich v16 mit der neuen
Byte-Zahl vorgibt). Nach `<scratchpad>\T-325f\localappdata\NightreignHelper`
**kopiert** (nicht verlinkt, nicht unter echtem `%LOCALAPPDATA%`). Nach dem
Kopieren erneut gezaehlt: 841 Dateien / 21.139.391 Byte, deckungsgleich. Nach
dem Rauchtest an der **Quelle** erneut gezaehlt: weiterhin 841 Dateien /
21.139.391 Byte, unveraendert (read-only bestaetigt).

## Startprobe (Rauchtest, NH-004)

Vor dem Start: `Get-Process -Name NightreignHelper` = 0 Treffer - keine Kopie
des Nutzers lief, keine Wartezeit noetig.

Isolierung: `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-325f`, `LOCALAPPDATA`/
`APPDATA` auf `<scratchpad>\T-325f\localappdata` bzw. `appdata` umgelenkt (in
derselben PowerShell-Sitzung wie der Start).

- **Start:** `dist\NightreignHelper.exe` gestartet, nach 8 s zwei Prozesse
  (Bootloader-PID 604, Kind-PID 20896), beide `Responding = True`.
- **Fenstertitel:** "Nightreign Helper 1.17.0" - Version am Fenster
  bestaetigt.
- **Echte Schreibaktion:** `Get-ChildItem HKCU:\Software\DankYeeterT-325f`
  findet nach dem Start `NightreignHelper`, `NightreignHelper\builds\1`,
  `NightreignHelper\chalices\1` - die Testorganisation, nicht `DankYeeter`.
  Die echten Nutzerdaten (309 Relikte, ~110 Builds unter
  `HKCU\Software\DankYeeter`) wurden nicht beruehrt (Positivnachweis der
  Umlenkung genuegt laut CLAUDE.md; `HKCU:\Software\DankYeeter` existiert
  weiterhin, Inhalt nicht erneut gelesen).
- **Beendet sofort** (Auftrag: NH-004, ein Fensterlauf je Zeitpunkt):
  `Stop-Process -Force` auf beide `NightreignHelper`-PIDs, 0,5 s Wartezeit,
  danach `Get-Process -Name NightreignHelper`: **0 Treffer** - belegt.
- **Aufraeumen:** Testregistrierung `HKCU:\Software\DankYeeterT-325f`
  entfernt (`Test-Path` danach `False`; `HKCU:\Software\DankYeeter`
  weiterhin `True`, unberuehrt); Scratchpad-Testabzug (`localappdata`,
  `appdata`) geloescht; Build-Log verbleibt im Scratchpad (nicht im Repo,
  `git status` danach leer).

Keine ueber die Startprobe hinausgehende Schreibaktion (Update-Pfad,
Neustart-Probe, fachliche Bedienhandlung A26) ausgefuehrt - Nachweis A26 und
Fensterlauf sind laut Auftrag T-325h (qa-engineer), nicht Teil dieses
Auftrags; NH-004 verlangt zudem genau einen Fensterlauf je Zeitpunkt.

## Blocker

Keiner fuer diesen Bau.

## Risiken

- Kein UPX auf diesem Bau-Wirt - unveraendert seit T-282/T-290/T-293/T-294b/
  T-295b/T-312a/T-313b/T-322b/T-322h.
- Nur ein gueltiger Lauf: interne Reproduzierbarkeit (Bit-Identitaet zwischen
  zwei Laeufen derselben Umgebung) wurde nicht neu belegt, sondern aus den
  genannten Vorlaeufen uebernommen (auftragsgemaess, kein Zweitbau verlangt).
- `CHANGELOG.md` fuehrt weiterhin 1.16.0 als letzten Eintrag, kein
  1.17.0-Abschnitt - Nebenfund fuer den `notes`-Lauf, keine Auflage, kein
  Blocker fuer diesen Bau.
- `CLAUDE.md` nennt `EXTRACT_VERSION` 15 mit 21.131.645 Byte; der Auftrag
  verlangt ausdruecklich v16 mit 21.139.391 Byte (dieser Lauf verwendet v16,
  unabhaengig nachgezaehlt und deckungsgleich) - `CLAUDE.md` ist damit
  veraltet. Nach der Projektregel ersetzt der erste betroffene Lauf die
  Vorlage und vermerkt es in `docs/plan-restarbeiten.md`; das gehoert nicht
  in den Kontraktblock dieses Bau-Auftrags und wird hier nur gemeldet, nicht
  selbst editiert (Grenzfrage an `director`/`developer`, siehe unten).

## Ungeprueft

- Clean-Room-Installation, Update-Pfad, Zweitstart nach Neustart - nicht Teil
  dieses Auftrags (nur Startprobe, keine Schreibaktion darueber hinaus).
- Windows ARM64, Windows 8.1/aelter, Linux/macOS - kein Ziel laut `CLAUDE.md`.
- Die fachliche A26-Pruefung selbst (Advisor-Vorschlag, Startbreite als
  Monitor-Ratio) - das ist T-325h (qa-engineer), nicht dieser Bau.

## An `developer`

Kein Befund am Anwendungscode.

## An `power-user` (Ausgangspunkt, falls angefordert)

- **Pfad:** `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe`
- **Groesse:** 59.249.345 Byte (56,50 MiB)
- **SHA-256:** `D136FB2DCAA9F4C44C9D23557F05ED2206C75BBF7D71128EA47F4065BA120101`
- **Versionsressource:** 1.17.0, am Fenstertitel bestaetigt (Startprobe).
- Dieses Artefakt ersetzt jeden aelteren Zwischenbau in `dist/` (u. a. den
  59.233.451-Byte-Stand von 16:41 desselben Tages, vermutlich aus T-325b/e).
- Drei Umlenkungen zwingend beim Start: `NIGHTREIGN_SETTINGS_ORG`,
  `LOCALAPPDATA`, `APPDATA` - Testabzug **v16** (841 Dateien, 21.139.391
  Byte) kopieren, nicht darauf zeigen (`CLAUDE.md`, Auftrag).
- Kein laufender `NightreignHelper.exe`-Prozess nach diesem Lauf
  (`Get-Process` geprueft, 0 Treffer) - vor eigenem Start dennoch selbst
  pruefen (NH-004, maschinenweite Instanzsperre).

## An `director`

**Empfehlung: freigeben mit benannter Einschraenkung** (fuer den Weiterlauf zu
T-325h - kein Release-Votum, das bleibt an A-025 und eine ausdrueckliche
Weitergabe-Entscheidung gebunden).

1. Kein `.gitignore`-Nachtrag noetig (`dist/`, `build/` bereits erfasst).
2. Keine offene rote Auflage - Build war nicht gesperrt.
3. Arbeitsbaum war beim Bau sauber und blieb es (kein Anwendungscode
   angefasst); `dist/`/`build/` weiterhin ignoriert.
4. Tag-Vorschlag: keiner in diesem Lauf - 1.17.0 ist unveroeffentlicht, Notes
   und Release folgen erst nach QA gruen (T-325h).
5. **Nebenfund:** `CLAUDE.md` nennt fuer den Testabzug `EXTRACT_VERSION` 15
   (841 Dateien, 21.131.645 Byte); dieser Auftrag nannte bereits v16
   (841 Dateien, 21.139.391 Byte) und dieser Lauf hat v16 unabhaengig
   nachgezaehlt und verwendet. Die Projektregel verlangt, dass der erste
   betroffene Lauf die Vorlage ersetzt und es in
   `docs/plan-restarbeiten.md` vermerkt - das aendert `CLAUDE.md`
   (Projektregel-Pflege, nicht Anwendungscode) und liegt damit ausserhalb
   des reinen Bau-Kontraktblocks dieses Auftrags; wird hier nur gemeldet.

---

STATUS: erledigt
AUFTRAG: T-325k - Neubau 1.17.0 nach DR-038-Fix (release-manager, Modus
`build`), Stand HEAD (`git log --oneline -1`, Code `eaf9ea9`), Version
bleibt 1.17.0. Wie T-325f; Umlenkung `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-325k`,
Testabzug v16 kopieren, NH-004 (`Get-Process` vor dem Rauchtest 0, sofort
beenden, danach 0).
GELESEN: docs/legal/AUFLAGEN.md (vollstaendig, 558 Zeilen; letzter
aendernder Commit weiterhin `cc92066`, 16.09., "Auflagen vor der
Veroeffentlichung 1.13.1", T-283c - unveraendert seit T-325f, keine neue
Auflage seither. Gesamtampel GELB, keine Auflage steht auf ROT mit
sperrender Wirkung: A-010 ist ROT, aber ausdruecklich "sperrt nicht mehr";
A-025 GRAU, entschieden FORTSETZEN; die T-241a-Einordnung "Bau/Eigenlauf:
GRUEN" gilt fort. Dieser Lauf ist kein Release - `build` ist nicht
gesperrt); docs/tasks/T-325.md (Abschnitt T-325k); docs/berichte/
T-325-release-manager.md (eigener T-325f-Abschnitt, als Rezept); CLAUDE.md.
GEAENDERT: `dist/NightreignHelper.exe` neu gebaut (Code-Stand `2aaf114` =
HEAD; Anwendungscode darin identisch mit `eaf9ea9` - `git diff --stat
eaf9ea9..HEAD` zeigt seither ausschliesslich `GOAL.md`, zwei Berichte,
`docs/tasks/T-325.md`, `docs/tasks/T-326.md`, `qa/findings.md`, kein Treffer
unter `nrplanner/`). Altes `dist/` enthielt noch das T-325f-Artefakt (SHA-256
`D136FB2D...`, byteidentisch mit dem in jenem Abschnitt dokumentierten Bau -
offenbar aus T-325f stehengeblieben, nicht aufgeraeumt) - vor diesem Bau
geloescht, kein Anwendungscode angefasst. Dieser Abschnitt an bestehende
Datei angehaengt.
ANNAHMEN: "Neubau" gelesen wie T-325f/T-322h: ein Bau, Rauchtest mit
sofortigem Beenden, kein Update-Pfad, kein Zweitbau zur
Bit-Identitaetspruefung - die vollstaendige Installationspruefung folgt in
T-325l (clean-room).
NAECHSTER: T-325l (release-manager, clean-room), danach T-325m (power-user),
T-325n (notes); parallel laeuft nur eine Leserolle (ui-ux-designer, kein
Fenster).
BLOCKIERT DURCH: nichts fuer diesen Bau.

---

# T-325k - Neubau 1.17.0 nach DR-038-Fix

Anlass: T-325i (`eaf9ea9`, DR-038) hat nach dem T-325f-Bau Anwendungscode
geaendert (`nrplanner/advisor/goals.py`, Grossbuchstabe der Art im Satz).
Version bleibt 1.17.0 (kein neuer Versionsbump im Auftrag genannt,
`nrplanner/__init__.py` weiterhin `"1.17.0"` geprueft).

## Kontraktblock

| | |
|---|---|
| **Pfad** | `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe` |
| **Groesse** | 59.250.281 Byte (56,51 MiB) |
| **SHA-256** | `BFEEB0270D16C88FDEC67DF10F2D5C76FD29AB5002F6EEC2E14691F321E7C4B4` |
| **Code-Stand des Artefakts** | `2aaf114` (HEAD, Branch `docs/audit-and-advisor-design`); Anwendungscode identisch mit `eaf9ea9` |
| **Version** | 1.17.0 (unveraendert), am Fenstertitel bestaetigt |
| **Dauer** | 42,3 s (Stopwatch um den PyInstaller-Aufruf) |
| **UPX** | nicht im `PATH` (`where.exe upx`: exit 1) - `upx=True` im `.spec` bleibt wirkungslos, wie in jedem vorherigen Bau |
| **`scripts/check_licences.py`** | `OK`, alle drei Pflichtdateien und alle fuenf `requirements.txt`-Bibliotheken erfasst |

## Pflichtlektuere `docs/legal/AUFLAGEN.md`

Volltext erneut gelesen (558 Zeilen, `git log -1 -- docs/legal/AUFLAGEN.md`:
`cc92066`, 16.09.) - unveraendert seit T-325f, keine neue Auflage seither.
Gesamtampel GELB, keine Auflage steht auf ROT mit sperrender Wirkung: A-010
ist ROT, aber ausdruecklich "sperrt nicht mehr" (Nutzer-Rueckstellung 02.09.,
Abnahme 09.09.); A-025 (GRAU, EXE-Weitergabe) ist entschieden (FORTSETZEN,
09.09.) und betrifft ohnehin nur Weitergabe, nicht diesen Bau. Dieser Lauf
ist kein Release (kein Push, kein Tag, keine Weitergabe der EXE an Dritte) -
`build` ist nicht gesperrt.

## Ausgangsstand

`git status --porcelain -uall` vor dem ersten Schritt: leer, Arbeitsbaum
sauber. `git rev-parse HEAD`: `2aaf114c1598ad9e69c99f89a8942b8e8021aa2c`.
`nrplanner/__init__.py` gelesen: `__version__ = "1.17.0"`.

`dist/` enthielt vor dem Bau noch eine EXE (59.249.345 Byte, SHA-256
`D136FB2DCAA9F4C44C9D23557F05ED2206C75BBF7D71128EA47F4065BA120101`) -
byteidentisch mit dem in T-325f dokumentierten Artefakt, also derselbe
Bau-Ruecklauf, nicht aufgeraeumt. `Get-Process -Name NightreignHelper` vor
dem Loeschen: 0 Treffer - kein Nutzerlauf betroffen. `dist/`/`build/` sind
gitignored (`.gitignore` Z. 9-10), also keine Abweichung im `git status`.

`git diff --stat eaf9ea9..HEAD`: nur `GOAL.md`, `docs/berichte/
T-325-qa-engineer.md`, `docs/tasks/T-325.md`, `docs/tasks/T-326.md`,
`qa/findings.md` - kein Anwendungscode. Der Code-Stand des Artefakts ist
damit deckungsgleich mit `eaf9ea9`, dem im Auftrag genannten Stand.
`git diff --stat f24376b..HEAD` (Vergleich zum T-325f-Bau) zeigt als
einzige Anwendungscode-Aenderung `nrplanner/advisor/goals.py` (+44/-3
Zeilen, DR-038) und `tests/test_advisor_goals.py` (+36 Zeilen); keine neue
Abhaengigkeit (`requirements.txt`/`requirements-dev.txt`/
`NightreignHelper.spec`/`.gitignore` im selben Diff: 0 Treffer).

## Bau

`Get-Process -Name NightreignHelper`: 0 Treffer unmittelbar vor dem Loeschen
von `dist/`/`build/` und unmittelbar vor dem Aufruf. Bau ausschliesslich
ueber `./.venv/Scripts/python.exe -m PyInstaller NightreignHelper.spec`
(`.venv` Python, kein globales `python`). PyInstaller 6.21.0, contrib hooks
2026.7, Plattform Windows-11-10.0.26200-SP0.

| | Lauf |
|---|---|
| `rc` | 0 ("Build complete!") |
| Dauer | 42,3 s |
| Groesse | 59.250.281 Byte |
| SHA-256 | `bfeeb0270d16c88fdec67df10f2d5c76fd29ab5002f6eec2e14691f321e7c4b4` |

Zweiter Lauf zur Reproduzierbarkeitspruefung (Bit-Identitaet) entfaellt -
wie T-325f/T-322h, mit derselben Begruendung (interne Bit-Nichtidentitaet
zwischen Laeufen derselben Umgebung bereits in mehreren Vorlaeufern belegt).
Zum Beleg hier zusaetzlich beobachtet: dieser Bau (Code `eaf9ea9`) und der
T-325f-Bau (Code `f24376b`, unterschiedlicher Anwendungscode) unterscheiden
sich um 936 Byte - passt zur bekannten Bau-zu-Bau-Streuung, kein Hinweis auf
einen fehlerhaften Bau.

Build-Log (`t325k-build1.log`, im Scratchpad gesichert, vollstaendig
geprueft): einziger "error"-Treffer ist derselbe PowerShell-`*>`-Artefakt wie
in T-325f/T-322h (stderr-Umleitung verpackt die erste PyInstaller-INFO-Zeile
als `NativeCommandError`, `rc` bleibt 0, Build-Log endet mit "Build
complete!") - kein PyInstaller-Fehler; 0 Treffer fuer "deprecat".
Warnungsdatei (`build/NightreignHelper/warn-NightreignHelper.txt`): **37
Zeilen** (davon 21 `missing module`) - zahlengleich mit T-325f und allen
frueheren Bauten; keine neue, unerklaerte Warnung.

## Testabzug

`C:\Users\Daniel\Desktop\ClaudeCode\NightreignHelper-Testabzug` unabhaengig
nachgezaehlt vor dem Kopieren: **841 Dateien, 21.139.391 Byte** - deckungsgleich
mit dem in T-325f verwendeten Stand v16 (`EXTRACT_VERSION` 15 in `CLAUDE.md`
bleibt veraltet, wie dort bereits gemeldet; keine neue Meldung noetig, da
bereits an `docs/plan-restarbeiten.md` verwiesen). Nach
`<scratchpad>\T-325k\localappdata\NightreignHelper` **kopiert** (nicht
verlinkt, nicht unter echtem `%LOCALAPPDATA%`). Nach dem Kopieren erneut
gezaehlt: 841 Dateien / 21.139.391 Byte, deckungsgleich. Nach dem Rauchtest
an der **Quelle** erneut gezaehlt: weiterhin 841 Dateien / 21.139.391 Byte,
unveraendert (read-only bestaetigt).

## Startprobe (Rauchtest, NH-004)

Vor dem Start: `Get-Process -Name NightreignHelper` = 0 Treffer - keine Kopie
des Nutzers lief, keine Wartezeit noetig.

Isolierung: `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-325k`, `LOCALAPPDATA`/
`APPDATA` auf `<scratchpad>\T-325k\localappdata` bzw. `appdata` umgelenkt (in
derselben PowerShell-Sitzung wie der Start).

- **Start:** `dist\NightreignHelper.exe` gestartet, nach 8 s zwei Prozesse
  (Bootloader-PID 4148, Kind-PID 26216), beide `Responding = True`.
- **Fenstertitel:** "Nightreign Helper 1.17.0" - Version am Fenster
  bestaetigt.
- **Echte Schreibaktion:** `Get-ChildItem HKCU:\Software\DankYeeterT-325k`
  findet nach dem Start `NightreignHelper\builds\1` und
  `NightreignHelper\chalices\1` (Autoimport aus dem umgelenkten Testabzug) -
  die Testorganisation, nicht `DankYeeter`. Die echten Nutzerdaten (309
  Relikte, ~110 Builds unter `HKCU\Software\DankYeeter`) wurden nicht
  beruehrt (Positivnachweis der Umlenkung genuegt laut CLAUDE.md;
  `HKCU:\Software\DankYeeter` existiert weiterhin, Inhalt nicht erneut
  gelesen).
- **Beendet sofort** (NH-004, ein Fensterlauf je Zeitpunkt): `Stop-Process
  -Force` auf beide `NightreignHelper`-PIDs, 1 s Wartezeit, danach
  `Get-Process -Name NightreignHelper`: **0 Treffer** - belegt.
- **Aufraeumen:** Testregistrierung `HKCU:\Software\DankYeeterT-325k`
  entfernt (`Test-Path` danach `False`; `HKCU:\Software\DankYeeter`
  weiterhin `True`, unberuehrt); Scratchpad-Testabzug (`localappdata`,
  `appdata`) geloescht; Umgebungsvariablen zurueckgesetzt
  (`NIGHTREIGN_SETTINGS_ORG` entfernt, `LOCALAPPDATA`/`APPDATA` auf die
  echten Pfade des Nutzers gesetzt); Build-Log verbleibt im Scratchpad
  (nicht im Repo, `git status` danach leer).

Keine ueber die Startprobe hinausgehende Schreibaktion (Update-Pfad,
Neustart-Probe, fachliche Bedienhandlung A26) ausgefuehrt - die
vollstaendige Installationspruefung ist T-325l (clean-room), NH-004
verlangt zudem genau einen Fensterlauf je Zeitpunkt.

## Blocker

Keiner fuer diesen Bau.

## Risiken

- Kein UPX auf diesem Bau-Wirt - unveraendert seit allen Vorlaeufern.
- Nur ein gueltiger Lauf: interne Reproduzierbarkeit (Bit-Identitaet
  zwischen zwei Laeufen derselben Umgebung) wurde nicht neu belegt, sondern
  aus den in T-325f genannten Vorlaeufern uebernommen (auftragsgemaess, kein
  Zweitbau verlangt).
- `CHANGELOG.md` fuehrt weiterhin 1.16.0 als letzten Eintrag, kein
  1.17.0-Abschnitt - unveraendert seit T-325f, Nebenfund fuer den
  `notes`-Lauf (T-325n), keine Auflage, kein Blocker fuer diesen Bau.
- Der T-325f-Bau-Ruecklauf lag noch unaufgeraeumt in `dist/` - fuer diesen
  Lauf ohne Wirkung (vor dem Bau geloescht), aber ein Hinweis, dass `dist/`
  zwischen Bauten nicht automatisch geleert wird.

## Ungeprueft

- Clean-Room-Installation, Update-Pfad, Zweitstart nach Neustart - das ist
  T-325l (release-manager, eigener Lauf), nicht Teil dieses Bau-Auftrags.
- Windows ARM64, Windows 8.1/aelter, Linux/macOS - kein Ziel laut `CLAUDE.md`.
- Die fachliche DR-038/A26-Pruefung selbst (Wortlaut der Art im Satz,
  Advisor-Vorschlag) - Retest ist T-325j (qa-engineer, bereits am
  Quellstand bestanden laut `docs/berichte/T-325-qa-engineer.md`), nicht
  dieser Bau.

## An `developer`

Kein Befund am Anwendungscode.

## An `power-user` (Ausgangspunkt fuer T-325m, ueber T-325l)

- **Pfad:** `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe`
- **Groesse:** 59.250.281 Byte (56,51 MiB)
- **SHA-256:** `BFEEB0270D16C88FDEC67DF10F2D5C76FD29AB5002F6EEC2E14691F321E7C4B4`
- **Versionsressource:** 1.17.0, am Fenstertitel bestaetigt (Startprobe).
- Dieses Artefakt ersetzt das T-325f-Artefakt (SHA-256 `D136FB2D...`, DR-038
  war zu dem Zeitpunkt noch nicht behoben).
- Drei Umlenkungen zwingend beim Start: `NIGHTREIGN_SETTINGS_ORG`,
  `LOCALAPPDATA`, `APPDATA` - Testabzug **v16** (841 Dateien, 21.139.391
  Byte) kopieren, nicht darauf zeigen (`CLAUDE.md`, Auftrag).
- Kein laufender `NightreignHelper.exe`-Prozess nach diesem Lauf
  (`Get-Process` geprueft, 0 Treffer) - vor eigenem Start dennoch selbst
  pruefen (NH-004, maschinenweite Instanzsperre); T-325l (clean-room) laeuft
  vor dieser Rolle in der Auftragsreihenfolge.

## An `director`

**Empfehlung: freigeben mit benannter Einschraenkung** (fuer den Weiterlauf
zu T-325l - kein Release-Votum, das bleibt an A-025 und eine ausdrueckliche
Weitergabe-Entscheidung gebunden).

1. Kein `.gitignore`-Nachtrag noetig (`dist/`, `build/` bereits erfasst).
2. Keine offene rote Auflage - Build war nicht gesperrt.
3. Arbeitsbaum war beim Bau sauber und blieb es (kein Anwendungscode
   angefasst); `dist/`/`build/` weiterhin ignoriert.
4. Tag-Vorschlag: keiner in diesem Lauf - 1.17.0 ist unveroeffentlicht,
   Notes und Tag-Vorschlag folgen erst in T-325n nach `clean-room` (T-325l)
   und `power-user` (T-325m).
5. Nebenfund unveraendert aus T-325f: `CLAUDE.md` `EXTRACT_VERSION` 15 ist
   veraltet gegenueber dem tatsaechlich verwendeten v16 - keine erneute
   Meldung, Verweis genuegt.

---

STATUS: erledigt
AUFTRAG: T-325n - Version, Changelog, Migration (release-manager, Modus
`notes`), letzte Rolle der T-325-Kette nach T-325h/j (qa, PASS), T-325c
(security, PASS) und T-325l/m (clean-room PASS, power-user) (`docs/tasks/
T-325.md`).
GELESEN: docs/legal/AUFLAGEN.md (vollstaendig, 559 Zeilen; juengster
Abschnitt "Auflagen vor der Veroeffentlichung 1.13.1", T-283c, Stand
`1f51485`; Gesamtampel GELB, keine Auflage steht auf ROT mit sperrender
Wirkung - A-010 ist ROT, aber ausdruecklich "sperrt nicht mehr"; keine
Auflage seit 1.13.1 neu erfasst, obwohl seither 1.14.0-1.16.0 erschienen
sind - Buchfuehrungsluecke des `compliance-agent`/`director`, kein Befund
dieses Laufs); `nrplanner/__init__.py` (Version 1.17.0, gesetzt in T-325b);
`nrplanner/advisorbar.py` Z. 135-138, 743, 760, 1039-1040 (Schluessel
`hit_with`/`damage_type`, Kommentar "Der einzelne alte Schluessel
`damage_art` wird nicht mehr gelesen" - Migrationsnachweis); `CHANGELOG.md`
[1.16.0] als Formmuster; `docs/release/RELEASE_BODY.md` (Verlaufsliste "What's
new since 1.7.1"); `git log --oneline 9f95de0..eaf9ea9` (23 Commits, A26);
`docs/tasks/T-325.md`; Auftragstext mit den fertigen Inhaltsangaben (A26,
englisch).
GEAENDERT: `CHANGELOG.md` (Abschnitt `[1.17.0] - 2026-09-21` eingefuegt,
Added/Changed/Fixed/Note); `docs/release/RELEASE_BODY.md` (Zeile
"**1.17.0**" an die Verlaufsliste angehaengt); neuer Abschnitt in dieser
Datei. Commit `28b7f1e` (nur die beiden Dateien, kein Push, kein Tag).
ANNAHMEN: keine ueber den Auftragstext hinaus - Inhalt, Migrationsaussage
und QA-293/294-Verweis waren vorgegeben; gegen den Code (siehe GELESEN)
gegengeprueft, nicht neu erfunden.
NAECHSTER: director (Freigabeentscheidung, Tag setzen); danach archivist
(Push/Sync).
BLOCKIERT DURCH: nichts.

---

# T-325n - Notes 1.17.0

## Kontraktblock

| | |
|---|---|
| **Version** | 1.17.0 (`nrplanner/__init__.py`, gesetzt T-325b, unveraendert in diesem Lauf) |
| **Code-Stand** | `eaf9ea9` (DR-038-Fix, letzter Anwendungscode-Commit der Kette; alle Commits danach sind Doku/Release) |
| **Artefakt** | T-325k, Commit `fc57b93`, `dist/NightreignHelper.exe`, 59.250.281 Byte, SHA-256 `BFEEB0270D16C88FDEC67DF10F2D5C76FD29AB5002F6EEC2E14691F321E7C4B4` |
| **QA** | T-325h/j PASS (`docs/berichte/T-325-qa-engineer.md`) |
| **Sicherheit** | T-325c PASS (`security/findings.md`, SEC-019-Senken-Retest) |
| **clean-room** | T-325l PASS, Cache-Neubau beim Update 37 s, `EXTRACT_VERSION` 15 → 16 (`docs/berichte/T-325-release-manager-clean-room.md`) |
| **power-user** | T-325m abgelegt, QA-293/294 angehaengt (`docs/berichte/T-325-power-user.md`) |
| **CHANGELOG.md** | Abschnitt `[1.17.0] - 2026-09-21` ergaenzt |
| **RELEASE_BODY.md** | Verlaufszeile "1.17.0" ergaenzt; Bestandssatz "Skill attack" in der 1.16.0-Zeile bewusst unveraendert (historisch) |
| **Migration** | Settings-Schluessel `damage_art` verworfen, ersetzt durch `hit_with`/`damage_type` (`advisorbar.py` Z. 135-138). Kein Uebernahmepfad: ein Update liest den alten Schluessel nicht, startet mit der Voreinstellung Weapon/All. Kein neuer Cache-Ordner, kein neuer Ablageort - nur `EXTRACT_VERSION` 15 → 16 loest den bestehenden, dokumentierten Neubau-Mechanismus aus (bereits in T-325l geprueft: 37 s, Daten danach vollstaendig). Kein Rueckweg noetig: ein Downgrade auf 1.16.0 faellt beim unbekannten neuen Schluessel ebenso auf die Voreinstellung zurueck (bestehendes Verhalten, in [1.16.0]/[1.17.0]-Notes je dokumentiert). |
| **Bekannt, fuer naechstes Release** | QA-293 (Why-Zuschreibung unter Schulwahl), QA-294 (leere Zelle ohne Begruendung) - beide nicht releasesperrend laut T-325h/j/m |
| **Tag-Vorschlag** | `v1.17.0` auf **diesem** Commit (`28b7f1e`, "docs(release): T-325n CHANGELOG und RELEASE_BODY fuer 1.17.0") - nicht auf `eaf9ea9`. Begruendung: identisches Muster wie `v1.16.0`, das auf `a33e92b` sitzt (dem Commit, der CHANGELOG/RELEASE_BODY zuletzt nachzog, nicht auf dem letzten Codecommit `9f95de0`) - der Code ist seit `eaf9ea9`/`fc57b93` unveraendert, das Artefakt aus T-325k bleibt gueltig. Tag wird von diesem Lauf **nicht gesetzt** (director/archivist). |

## An `director`

**Empfehlung: freigeben mit einer benannten Einschraenkung.**

1. Auflagenlage: keine ROT-Auflage sperrt (siehe GELESEN). Nebenfund: das
   Auflagenregister ist seit T-283c (1.13.1, 16.09.) nicht fortgeschrieben,
   obwohl 1.14.0-1.16.0 dazwischen erschienen sind - das ist keine
   Blockade fuer 1.17.0 (dieselbe GELB-Lage wie am 16.09., keine neue
   Auflage in Sicht), aber eine Buchfuehrungsluecke, die vor dem naechsten
   `compliance-agent`-Lauf auffallen sollte.
2. Einschraenkung: QA-293/294 bleiben offen, von T-325h/j/m als nicht
   releasesperrend eingestuft - im CHANGELOG unter "Note" ausdruecklich
   benannt, damit ein Nutzerbericht nicht als Ueberraschung ankommt.
3. Tag-Vorschlag siehe Kontraktblock: `v1.17.0` auf `28b7f1e`.
4. Kein `.gitignore`-Nachtrag noetig.
5. Diese Rolle hat nicht committet ausser den beiden genannten Dateien;
   kein Push, kein Tag gesetzt.

## An `power-user` / `qa-engineer` / `developer`

Kein neuer Befund - diese Rolle hat nur Doku geschrieben, keinen Code und
kein Artefakt veraendert.
