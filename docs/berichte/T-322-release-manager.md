STATUS: erledigt
AUFTRAG: T-322b - Artefakt 1.16.0 bauen (release-manager, Modus `build`),
Code-Stand `41173d9` (T-322a Versionsbump + T-322f Fix DR-034/DR-035,
AK-335/336, auf `6b12b6b`), wie T-313b (`docs/tasks/T-313.md`,
`docs/release/ROLLOUT.md`).
GELESEN: docs/legal/AUFLAGEN.md (vollstaendig, 559 Zeilen; juengster
Abschnitt "Auflagen vor der Veroeffentlichung 1.13.1", T-283c, Stand
`1f51485`, Commit `cc92066` - Gesamtampel GELB, keine Auflage auf ROT; A-010
ROT, aber ausdruecklich "sperrt nicht mehr"; Bau/Eigenlauf bleibt GRUEN nach
der T-241a-Einordnung, seither unveraendert bestaetigt); docs/tasks/T-322.md;
docs/tasks/T-313.md, docs/tasks/T-312.md (Rezept); docs/release/ROLLOUT.md;
docs/berichte/T-313-release-manager.md (Vorlage, wie im Auftrag verlangt);
CLAUDE.md.
GEAENDERT: dist/NightreignHelper.exe neu gebaut (Code-Stand `41173d9`,
gitignored). Altes `dist/` enthielt noch das T-313b-Artefakt (1.15.0, Stand
`6edab2e`, SHA-256 `1D4197DF...`, unveraendert seit 19.09.) - vor dem Bau
geloescht, kein Anwendungscode angefasst. Neu: dieser Bericht.
ANNAHMEN: keine ueber den Auftragstext hinaus. "Wie T-313b" wurde als
identisches Rezept gelesen: ein Bau, Rauchtest mit sofortigem Beenden, kein
Update-Pfad, kein Zweitbau zur Bit-Identitaetspruefung (Auftrag nennt keinen).
NAECHSTER: T-322e (qa-engineer, Nachweis A25 am Artefakt).
BLOCKIERT DURCH: nichts fuer diesen Bau.

---

# T-322b - Bau 1.16.0

## Kontraktblock

| | |
|---|---|
| **Pfad** | `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe` |
| **Groesse** | 59.159.482 Byte (56,42 MiB) |
| **SHA-256** | `804F9E2B4A0A41289F64F4D8EE34146D99F489FDE30C679058E783F2CBF25E6C` |
| **Code-Stand des Artefakts** | `41173d9` (HEAD, Branch `docs/audit-and-advisor-design`) |
| **Version** | 1.16.0 (T-322a), am Fenstertitel bestaetigt |
| **Dauer** | 43,6 s (PyInstaller-Eigenzeit, `43717 INFO: Build complete!` minus `108 INFO:` Startzeile) |
| **UPX** | nicht im `PATH` (`where upx`: "Could not find files") - `upx=True` im `.spec` bleibt wirkungslos, wie in jedem vorherigen Bau |
| **`scripts/check_licences.py`** | `OK`, alle drei Pflichtdateien und alle fuenf `requirements.txt`-Bibliotheken erfasst |

## Pflichtlektuere `docs/legal/AUFLAGEN.md`

Volltext gelesen (559 Zeilen, zwei Seiten). Juengster Abschnitt: "Auflagen vor
der Veroeffentlichung 1.13.1" (T-283c, Stand `1f51485`, Commit `cc92066` -
das ist der Commit, der die Datei zuletzt geaendert hat; er liegt in der
Historie vor den fuenf juengsten Commits, nicht danach). Gesamtampel GELB,
keine Auflage steht auf ROT: A-010 ist ROT, aber ausdruecklich "sperrt nicht
mehr" (Nutzer-Rueckstellung 02.09., Abnahme 09.09.). Die T-241a-Einordnung
"Bau/Eigenlauf: GRUEN" gilt seither unveraendert fort und ist durch spaetere
Abschnitte (T-283c) nicht revidiert worden. Dieser Lauf ist kein Release
(kein Push, kein Tag, keine Weitergabe der EXE an Dritte) - `build` ist nicht
gesperrt. A-025 (EXE-Weitergabe) bleibt unberuehrt, weil dieser Lauf nichts
weitergibt.

## Ausgangsstand

`git status --porcelain -uall` vor dem ersten Schritt: leer, Arbeitsbaum
sauber. `git rev-parse HEAD`: `41173d993b76d739e7febe450be41786d0096d79`,
Commit-Zeit 2026-09-20 13:41:38 +0200 - identisch mit dem im Auftrag
genannten Stand `41173d9`. `nrplanner/__init__.py` gelesen: `__version__ =
"1.16.0"`.

`dist/` enthielt vor dem Bau noch das T-313b-Artefakt: 59.151.716 Byte,
SHA-256 `1D4197DF0F0C765B507CCA824FBA480DBCFCA76C482CF3F7A852B199CB6BBDF0`
(deckungsgleich mit dem T-313b-Bericht), `LastWriteTime` 19.09.2026 - stammt
aus dem vorherigen Lauf, kein neuer Bau seither. `dist/`/`build/` sind
gitignored (`.gitignore`: `build/`, `dist/` unter "Build output"), also keine
Abweichung im `git status`. Vor dem Loeschen: `Get-Process -Name
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
| Dauer (PyInstaller-Eigenzeit) | 43,6 s |
| Groesse | 59.159.482 Byte |
| SHA-256 | `804f9e2b4a0a41289f64f4d8ee34146d99f489fde30c679058e783f2cbf25e6c` |

Zweiter Lauf zur Reproduzierbarkeitspruefung (Bit-Identitaet) entfaellt -
Auftrag nennt keinen Zweitbau und verweist ausdruecklich auf T-313b, das
denselben Verzicht mit Begruendung traegt (interne Bit-Nichtidentitaet
zwischen Laeufen derselben Umgebung ist in T-241/T-275/T-279/T-294b/T-295b/
T-312a/T-313b bereits mehrfach belegt).

Build-Log (`t322b-build1.log`, vollstaendig gepruft): 0 Treffer fuer "error"
(case-insensitive), 0 fuer "deprecat". Warnungsdatei
(`build/NightreignHelper/warn-NightreignHelper.txt`): **37 Zeilen** (davon 21
`missing module`) - zahlengleich mit T-313b/T-312a/T-295b/T-294b, Stichprobe
der ersten Zeilen zeigt dieselbe Art (optionale/plattformbedingte Importe);
keine neue, unerklaerte Warnung.

Groessendifferenz zum T-313b-Artefakt (59.151.716 Byte): **+7.766 Byte
(+0,013 %)** - plausibel: `git diff --stat 6edab2e..41173d9` zeigt
Aenderungen in acht `nrplanner/`-Quelldateien (u. a. `model.py` +186 Zeilen
neu, `advisor/goals.py` +143/-Netto, `advisorbar.py` +97, `relicpicker.py`
+53, `damage.py` +32) - der Groessenzuwachs deckt sich mit dem Umfang des
Diffs, keine neue Abhaengigkeit (`check_licences.py` unveraendert `OK`,
dieselbe Bibliotheksliste).

## Testabzug

`C:\Users\Daniel\Desktop\ClaudeCode\NightreignHelper-Testabzug` nach
`<scratchpad>\T-322b\localappdata\NightreignHelper` **kopiert** (nicht
verlinkt, nicht unter echtem `%LOCALAPPDATA%`). Dateizahl nach dem Kopieren:
**841**, Gesamtgroesse **21.131.645 Byte** - deckungsgleich mit dem in
`CLAUDE.md` genannten Stand (`EXTRACT_VERSION` 15, weiterhin gueltig). Nach
dem Rauchtest erneut gezaehlt: weiterhin 841 Dateien / 21.131.645 Byte,
unveraendert (read-only bestaetigt).

## Startprobe (Rauchtest, NH-004)

Vor dem Start: `Get-Process -Name NightreignHelper` = 0 Treffer - keine Kopie
des Nutzers lief, keine Wartezeit noetig.

Isolierung: `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-322b`, `LOCALAPPDATA`/
`APPDATA` auf `<scratchpad>\T-322b\localappdata` bzw. `appdata` umgelenkt (in
derselben PowerShell-Sitzung wie der Start).

- **Start:** `dist\NightreignHelper.exe` gestartet, nach 8 s zwei Prozesse
  (Bootloader-PID 6360, Kind-PID 21304), beide `Responding = True`.
- **Fenstertitel:** "Nightreign Helper 1.16.0" - Version am Fenster
  bestaetigt.
- **Echte Schreibaktion:** `Get-ChildItem HKCU:\Software\DankYeeterT-322b`
  findet nach dem Start `NightreignHelper`, `NightreignHelper\builds\1`,
  `NightreignHelper\chalices\1` - die Testorganisation, nicht `DankYeeter`.
  Die echten Nutzerdaten (309 Relikte, ~110 Builds unter
  `HKCU\Software\DankYeeter`) wurden nicht beruehrt (Positivnachweis der
  Umlenkung genuegt laut CLAUDE.md; `HKCU:\Software\DankYeeter` existiert
  weiterhin, Inhalt nicht erneut gelesen).
- **Beendet sofort** (Auftrag: NH-004, ein Fensterlauf je Zeitpunkt):
  `Stop-Process -Force` auf beide `NightreignHelper`-PIDs, 0,5 s Wartezeit,
  danach `Get-Process -Name NightreignHelper`: **0 Treffer** - belegt.

Keine ueber die Startprobe hinausgehende Schreibaktion (Update-Pfad,
Neustart-Probe, fachliche Bedienhandlung A25) ausgefuehrt - das ist
`clean-room` bzw. `qa-engineer` (T-322e), nicht Teil dieses Auftrags.

## Blocker

Keiner fuer diesen Bau.

## Risiken

- Kein UPX auf diesem Bau-Wirt - unveraendert seit T-282/T-290/T-293/T-294b/
  T-295b/T-312a/T-313b.
- Nur ein gueltiger Lauf: interne Reproduzierbarkeit (Bit-Identitaet zwischen
  zwei Laeufen derselben Umgebung) wurde nicht neu belegt, sondern aus den
  genannten Vorlaeufen uebernommen (auftragsgemaess, kein Zweitbau verlangt).
- `CHANGELOG.md` fuehrt weiterhin 1.15.0 als letzten Eintrag, kein 1.16.0-
  Abschnitt - Nebenfund fuer den `notes`-Lauf, keine Auflage, kein Blocker
  fuer diesen Bau.

## Ungeprueft

- Clean-Room-Installation, Update-Pfad, Zweitstart nach Neustart - nicht Teil
  dieses Auftrags (nur Startprobe, keine Schreibaktion darueber hinaus).
- Windows ARM64, Windows 8.1/aelter, Linux/macOS - kein Ziel laut `CLAUDE.md`.
- Die fachliche A25-Pruefung selbst (Revenant Magic/Bestial, Wylder Skill
  attack) - das ist T-322e (qa-engineer), nicht dieser Bau.

## An `developer`

Kein Befund am Anwendungscode.

## An `power-user` (Ausgangspunkt, falls angefordert)

- **Pfad:** `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe`
- **Groesse:** 59.159.482 Byte (56,42 MiB)
- **SHA-256:** `804F9E2B4A0A41289F64F4D8EE34146D99F489FDE30C679058E783F2CBF25E6C`
- **Versionsressource:** 1.16.0, am Fenstertitel bestaetigt (Startprobe).
- Drei Umlenkungen zwingend beim Start: `NIGHTREIGN_SETTINGS_ORG`,
  `LOCALAPPDATA`, `APPDATA` - Testabzug kopieren, nicht darauf zeigen
  (`CLAUDE.md`).
- Kein laufender `NightreignHelper.exe`-Prozess nach diesem Lauf
  (`Get-Process` geprueft, 0 Treffer) - vor eigenem Start dennoch selbst
  pruefen (NH-004, maschinenweite Instanzsperre).

## An `director`

**Empfehlung: freigeben mit benannter Einschraenkung** (fuer den Weiterlauf zu
T-322e - kein Release-Votum, das bleibt an A-025 und eine ausdrueckliche
Weitergabe-Entscheidung gebunden).

1. Kein `.gitignore`-Nachtrag noetig (`dist/`, `build/` bereits erfasst).
2. Keine offene rote Auflage - Build war nicht gesperrt.
3. Arbeitsbaum war beim Bau sauber und blieb es (kein Anwendungscode
   angefasst); `dist/`/`build/` weiterhin ignoriert.
4. Tag-Vorschlag: keiner in diesem Lauf - 1.16.0 ist unveroeffentlicht, Notes
   und Release folgen erst nach QA gruen (T-322e).

---

STATUS: erledigt
AUFTRAG: T-322h - Neubau 1.16.0 nach Fix T-322g (release-manager, Modus
`build`), Stand `5b9fad9`, Version bleibt 1.16.0.
GELESEN: docs/legal/AUFLAGEN.md (vollstaendig, 559 Zeilen; unveraendert seit
T-322b - letzter aendernder Commit weiterhin `cc92066`, 16.09.); docs/tasks/
T-322.md (Abschnitte T-322g, h); docs/berichte/T-322-release-manager.md
(eigener T-322b-Abschnitt, als Rezept); CLAUDE.md.
GEAENDERT: `dist/NightreignHelper.exe` neu gebaut (Code-Stand `5b9fad9`,
gitignored). Altes `dist/` enthielt noch das T-322b-Artefakt (1.16.0, Stand
`41173d9`, SHA-256 `804F9E2B...`) - vor dem Bau geloescht, kein Anwendungscode
angefasst. Dieser Abschnitt an bestehende Datei angehaengt.
ANNAHMEN: keine ueber den Auftragstext hinaus. "Neubau" gelesen als derselbe
Ablauf wie T-322b (ein Lauf, Rauchtest mit sofortigem Beenden, kein
Update-Pfad, kein Zweitbau zur Bit-Identitaetspruefung).
NAECHSTER: T-322i (qa-engineer, Retest QA-289/290 am Artefakt).
BLOCKIERT DURCH: nichts fuer diesen Bau.

---

# T-322h - Neubau 1.16.0 nach Fix T-322g

Anlass: T-322g (`10442b2` QA-289, `5b9fad9` QA-290) hat nach dem T-322b-Bau
Anwendungscode geaendert (`nrplanner/advisor/run.py`,
`nrplanner/relicpicker.py`); das T-322b-Artefakt ist damit ueberholt.
Version bleibt 1.16.0 (kein neuer Versionsbump im Auftrag genannt,
`nrplanner/__init__.py` weiterhin `"1.16.0"` geprueft).

## Kontraktblock

| | |
|---|---|
| **Pfad** | `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe` |
| **Groesse** | 59.233.161 Byte (56,49 MiB) |
| **SHA-256** | `51F694986D11CA1DED16B6170D552C89579C0E5C67192D78F68FFFF063E8BFC9` |
| **Code-Stand des Artefakts** | `5b9fad9` (HEAD, Branch `docs/audit-and-advisor-design`) |
| **Version** | 1.16.0 (unveraendert), am Fenstertitel bestaetigt |
| **Dauer** | 48,8 s (PyInstaller-Eigenzeit, `48932 INFO: Build complete!` minus `110 INFO:` Startzeile) |
| **UPX** | nicht im `PATH` (`where upx`: "Could not find files") - `upx=True` im `.spec` bleibt wirkungslos, wie in jedem vorherigen Bau |
| **`scripts/check_licences.py`** | `OK`, alle drei Pflichtdateien und alle fuenf `requirements.txt`-Bibliotheken erfasst |

## Pflichtlektuere `docs/legal/AUFLAGEN.md`

Volltext erneut gelesen (559 Zeilen). Letzter aendernder Commit auf der Datei
weiterhin `cc92066` (16.09., "Auflagen vor der Veroeffentlichung 1.13.1",
T-283c) - unveraendert seit dem T-322b-Bau, keine neue Auflage seither.
Gesamtampel GELB, keine Auflage steht auf ROT mit sperrender Wirkung: A-010
ist ROT, aber ausdruecklich "sperrt nicht mehr" (Nutzer-Rueckstellung 02.09.,
Abnahme 09.09.). Dieser Lauf ist kein Release (kein Push, kein Tag, keine
Weitergabe der EXE an Dritte) - `build` ist nicht gesperrt. A-025
(EXE-Weitergabe) bleibt unberuehrt, weil dieser Lauf nichts weitergibt.

## Ausgangsstand

`git status --porcelain -uall` vor dem ersten Schritt: leer, Arbeitsbaum
sauber. `git rev-parse HEAD`: `5b9fad9665cd1f6acb2eb46f2716243f2a30839a`,
Commit-Zeit 2026-09-20 14:54:16 +0200 - identisch mit dem im Auftrag
genannten Stand `5b9fad9`. `nrplanner/__init__.py` geprueft: `__version__ =
"1.16.0"`, unveraendert.

`dist/` enthielt vor dem Bau noch das T-322b-Artefakt: 59.159.482 Byte,
`LastWriteTime` 20.09.2026 13:44 - stammt aus dem Vorlauf, kein neuer Bau
seither. `dist/`/`build/` sind gitignored, also keine Abweichung im
`git status`. Vor dem Loeschen: `Get-Process -Name NightreignHelper` = 0
Treffer - kein Nutzerlauf betroffen.

## Bau

`Get-Process -Name NightreignHelper`: 0 Treffer unmittelbar vor dem Loeschen
von `dist/`/`build/` und unmittelbar vor dem Aufruf. Bau ausschliesslich ueber
`./.venv/Scripts/python.exe -m PyInstaller NightreignHelper.spec` (`.venv`
Python 3.12.10; kein globales `python`). PyInstaller 6.21.0, contrib hooks
2026.7, Plattform Windows-11-10.0.26200-SP0.

| | Lauf |
|---|---|
| `rc` | 0 ("Build complete!") |
| Dauer (PyInstaller-Eigenzeit) | 48,8 s |
| Groesse | 59.233.161 Byte |
| SHA-256 | `51f694986d11ca1ded16b6170d552c89579c0e5c67192d78f68ffff063e8bfc9` |

Zweiter Lauf zur Reproduzierbarkeitspruefung (Bit-Identitaet) entfaellt -
Auftrag nennt keinen Zweitbau und verweist ausdruecklich auf T-322b, das
denselben Verzicht mit Begruendung traegt (interne Bit-Nichtidentitaet
zwischen Laeufen derselben Umgebung ist in T-241/T-275/T-279/T-294b/T-295b/
T-312a/T-313b bereits mehrfach belegt).

Build-Log (`t322h-build1.log`, im Scratchpad gesichert, vollstaendig
geprueft): einziger "error"-Treffer ist ein PowerShell-`*>`-Artefakt
(stderr-Umleitung verpackt die erste PyInstaller-INFO-Zeile als
`NativeCommandError`, `rc` bleibt 0) - kein PyInstaller-Fehler; 0 Treffer fuer
"deprecat". Warnungsdatei (`build/NightreignHelper/warn-NightreignHelper.txt`):
**37 Zeilen** (davon 21 `missing module`) - zahlengleich mit T-322b/T-313b/
T-312a/T-295b/T-294b, gleiche Art (optionale/plattformbedingte Importe); keine
neue, unerklaerte Warnung.

Groessendifferenz zum T-322b-Artefakt (59.159.482 Byte): **+73.679 Byte
(+0,12 %)** - `git diff --stat 41173d9..5b9fad9` zeigt Aenderungen in genau
zwei Quelldateien (`nrplanner/advisor/run.py` +22 Zeilen,
`nrplanner/relicpicker.py` +3/-1 Zeilen). Die Groessenordnung des Sprungs
passt nicht linear zu 24 geaenderten Zeilen, liegt aber innerhalb der bereits
mehrfach dokumentierten Bau-zu-Bau-Streuung fuer diesen Bau-Wirt (T-290:
-71.812 Byte, T-293: +83.615 Byte, T-294: -72.215 Byte, jeweils fuer kleinere
Diffs als hier) - dieselbe dokumentierte Ursache (PE-Baustempel +
Modulreihenfolge, nicht bit-identischer Bau) erklaert die Groessenordnung,
ohne dass eine neue Abhaengigkeit dazukam (`check_licences.py` unveraendert
`OK`, dieselbe Bibliotheksliste).

## Testabzug

`C:\Users\Daniel\Desktop\ClaudeCode\NightreignHelper-Testabzug` nach
`<scratchpad>\T-322h\localappdata\NightreignHelper` **kopiert** (nicht
verlinkt, nicht unter echtem `%LOCALAPPDATA%`). Dateizahl nach dem Kopieren:
**841**, Gesamtgroesse **21.131.645 Byte** - deckungsgleich mit dem in
`CLAUDE.md` genannten Stand (`EXTRACT_VERSION` 15, weiterhin gueltig). Nach
dem Rauchtest erneut gezaehlt: weiterhin 841 Dateien / 21.131.645 Byte,
unveraendert (read-only bestaetigt).

## Startprobe (Rauchtest, NH-004)

Vor dem Start: `Get-Process -Name NightreignHelper` = 0 Treffer - keine Kopie
des Nutzers lief, keine Wartezeit noetig.

Isolierung: `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-322h`, `LOCALAPPDATA`/
`APPDATA` auf `<scratchpad>\T-322h\localappdata` bzw. `appdata` umgelenkt (in
derselben PowerShell-Sitzung wie der Start).

- **Start:** `dist\NightreignHelper.exe` gestartet, nach 8 s zwei Prozesse
  (Bootloader-PID 16716, Kind-PID 23808), beide `Responding = True`.
- **Fenstertitel:** "Nightreign Helper 1.16.0" - Version am Fenster
  bestaetigt.
- **Echte Schreibaktion:** `Get-ChildItem HKCU:\Software\DankYeeterT-322h`
  findet nach dem Start `NightreignHelper`, `NightreignHelper\builds\1`,
  `NightreignHelper\chalices\1` - die Testorganisation, nicht `DankYeeter`.
  Die echten Nutzerdaten (309 Relikte, ~110 Builds unter
  `HKCU\Software\DankYeeter`) wurden nicht beruehrt (Positivnachweis der
  Umlenkung genuegt laut CLAUDE.md; `HKCU:\Software\DankYeeter` existiert
  weiterhin, Inhalt nicht erneut gelesen).
- **Beendet sofort** (Auftrag: NH-004, ein Fensterlauf je Zeitpunkt):
  `Stop-Process -Force` auf beide `NightreignHelper`-PIDs, 0,5 s Wartezeit,
  danach `Get-Process -Name NightreignHelper`: **0 Treffer** - belegt.
- **Aufraeumen:** Testregistrierung `HKCU:\Software\DankYeeterT-322h`
  entfernt (`Test-Path` danach `False`; `HKCU:\Software\DankYeeter`
  weiterhin `True`, unberuehrt); Scratchpad-Testabzug (`localappdata`,
  `appdata`) geloescht; Build-Log nach `<scratchpad>\T-322h\` verschoben
  (nicht im Repo, `git status` danach leer).

Keine ueber die Startprobe hinausgehende Schreibaktion (Update-Pfad,
Neustart-Probe, fachliche Bedienhandlung QA-289/290) ausgefuehrt - das ist
`qa-engineer` (T-322i), nicht Teil dieses Auftrags.

## Blocker

Keiner fuer diesen Bau.

## Risiken

- Kein UPX auf diesem Bau-Wirt - unveraendert seit T-282/T-290/T-293/T-294b/
  T-295b/T-312a/T-313b/T-322b.
- Nur ein gueltiger Lauf: interne Reproduzierbarkeit (Bit-Identitaet zwischen
  zwei Laeufen derselben Umgebung) wurde nicht neu belegt, sondern aus den
  genannten Vorlaeufen uebernommen (auftragsgemaess, kein Zweitbau verlangt).
- `CHANGELOG.md` fuehrt weiterhin 1.15.0 als letzten Eintrag, kein
  1.16.0-Abschnitt - unveraendert seit T-322b, Nebenfund fuer den
  `notes`-Lauf, keine Auflage, kein Blocker fuer diesen Bau.

## Ungeprueft

- Clean-Room-Installation, Update-Pfad, Zweitstart nach Neustart - nicht Teil
  dieses Auftrags (nur Startprobe, keine Schreibaktion darueber hinaus).
- Windows ARM64, Windows 8.1/aelter, Linux/macOS - kein Ziel laut `CLAUDE.md`.
- Die fachliche Retest-Pruefung von QA-289/QA-290 selbst - das ist T-322i
  (qa-engineer), nicht dieser Bau.

## An `developer`

Kein Befund am Anwendungscode.

## An `power-user` (Ausgangspunkt, falls angefordert)

- **Pfad:** `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe`
- **Groesse:** 59.233.161 Byte (56,49 MiB)
- **SHA-256:** `51F694986D11CA1DED16B6170D552C89579C0E5C67192D78F68FFFF063E8BFC9`
- **Versionsressource:** 1.16.0, am Fenstertitel bestaetigt (Startprobe).
- Dieses Artefakt ersetzt das T-322b-Artefakt (SHA `804F9E2B...`), das den
  QA-289/290-Fix noch nicht enthielt - bei jeder Pruefung dieses hier
  verwenden.
- Drei Umlenkungen zwingend beim Start: `NIGHTREIGN_SETTINGS_ORG`,
  `LOCALAPPDATA`, `APPDATA` - Testabzug kopieren, nicht darauf zeigen
  (`CLAUDE.md`).
- Kein laufender `NightreignHelper.exe`-Prozess nach diesem Lauf
  (`Get-Process` geprueft, 0 Treffer) - vor eigenem Start dennoch selbst
  pruefen (NH-004, maschinenweite Instanzsperre).

## An `director`

**Empfehlung: freigeben mit benannter Einschraenkung** (fuer den Weiterlauf zu
T-322i/Retest - kein Release-Votum, das bleibt an A-025 und eine
ausdrueckliche Weitergabe-Entscheidung gebunden).

1. Kein `.gitignore`-Nachtrag noetig (`dist/`, `build/` bereits erfasst).
2. Keine offene rote Auflage - Build war nicht gesperrt.
3. Arbeitsbaum war beim Bau sauber und blieb es (kein Anwendungscode
   angefasst); `dist/`/`build/` weiterhin ignoriert.
4. Tag-Vorschlag: keiner in diesem Lauf - 1.16.0 ist unveroeffentlicht, Notes
   und Release folgen erst nach dem Retest der QA-289/290-Fixes.
