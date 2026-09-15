STATUS: erledigt
AUFTRAG: T-168 - Das Artefakt bauen, zweiter Anlauf (release-manager, Modus `build`)
GELESEN: docs/tasks/T-168.md (vollstaendig); docs/legal/AUFLAGEN.md (vollstaendig, 205 Zeilen, selbst nachgeprueft, nicht nur zitiert - siehe "Pflichtlektuere" unten); docs/release/ROLLOUT.md (Abschnitt "Ablaufplan fuer den `build`-Lauf", Zeilen 269-286, uebernommen); CHANGELOG.md (existiert nicht im Repo, `git ls-files | grep -i changelog` ohne Treffer - bestaetigt L3, nicht angefasst wie vorgeschrieben); docs/berichte/T-167-release-manager.md (Sperr-Vorgeschichte); docs/berichte/T-111-release-manager.md und T-113-release-manager.md (Methodik vorheriger Baeulaeufe); docs/berichte/T-114-qa-engineer.md (Methodik der Bytecode-Modulpruefung, dort erstmals mit "62 von 62" beschrieben - hier reproduziert); NightreignHelper.spec; nrplanner/__init__.py (nur gelesen, siehe "An developer/director" unten); nrplanner/paths.py, nrplanner/favourites.py:25, nrplanner/shortcut.py:44-49 (die drei Umlenkungspunkte); CLAUDE.md (Projektzeilen)
GEÄNDERT: `dist/NightreignHelper.exe` (neu gebaut, ueberschrieben), `dist/NightreignHelper.exe.sha256` (neu geschrieben, neue Pruefsumme), `build/NightreignHelper/*` (Bau-Zwischenstand, danach selbst wieder geloescht - siehe unten), `docs/berichte/T-168-release-manager.md` (dieser Bericht). Alle vier unter `dist/`/`build/`, beide gitignoriert (`.gitignore` Zeilen 9-10, bestaetigt), kein Git-Objekt veraendert (`git status --porcelain` vor und nach dem Lauf leer). Ausserhalb des Repositories: `HKCU\Software\DankYeeterT-168\*` wurde fuer den Rauchtest angelegt und danach vollstaendig geloescht (`Test-Path` → `False`, nachgeprueft). Scratchpad `…\scratchpad\T-168\` (Bau-Logs, Vergleichsskripte, Archiv-Listing) angelegt, Testverzeichnis-Kopien (`localappdata`, `appdata`, extrahierte PYZ-Datei, zwei EXE-Kopien) nach Auswertung selbst geloescht, nur Kennzahlen/Logs behalten.
ANNAHMEN: (1) Die Version wird von mir **entschieden und begruendet** (1.9.0), aber **nicht** in `nrplanner/__init__.py` eingetragen - diese Datei liegt unter `nrplanner/`, das die Scope-Grenzen dieses Auftrags ausdruecklich sperren ("Nicht anfassen: nrplanner/ … Buildskripte … sind deins; der Anwendungscode … nicht"), und `docs/release/ROLLOUT.md` weist die Aenderung selbst dem `developer` zu ("Nummer: director; Aenderung: developer (Quellverzeichnis, nicht meins)"). Das gebaute Artefakt traegt deshalb weiterhin die Versionsressource 1.8.0, obwohl es inhaltlich ein anderer Stand ist - das ist ein bewusst offen gelassener Punkt, kein Versehen, siehe "An developer/director". (2) Der geforderte "Nachweis am gebauten Artefakt" fuer A9/A11/A15 ist explizit Sache von `qa-engineer`/`clean-room`/`power-user`, nicht des `build`-Laufs selbst (Scope-Grenzen: "Nicht: clean-room … power-user"); mein Rauchtest unten prueft nur, dass das Artefakt ueberhaupt startet und die drei Umlenkungen greifen, nicht die Funktionen selbst. (3) `dist/NightreignHelper-notices.zip` (Sep 7, alter Zyklus) liegt weiterhin unveraendert in `dist/` - Regeneration ist nicht Teil dieses Auftrags (Vorgaben nennen nur die EXE), wird aber unten als Risiko benannt.
NÄCHSTER: qa-engineer (fuer A9 am neuen Artefakt) bzw. clean-room-Lauf; danach power-user; `notes` (Versionsbump, CHANGELOG) erst danach
BLOCKIERT DURCH: nichts fuer diesen Bau selbst. Fuer das **Release** (nicht den Bau) unveraendert A-025 (GRAU, Nutzerentscheidung ueber Fortsetzung/Ende/anwaltliche Klaerung der Verbreitung) - dieser Lauf hat nichts veroeffentlicht, nichts getaggt, nichts gepusht.

---

# T-168 - Bau des Artefakts, zweiter Anlauf

## Ganz oben, wie verlangt

| | |
|---|---|
| **Pfad** | `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe` |
| **Groesse** | **59.063.047 Byte** (56,33 MiB) |
| **SHA-256** | `357F8D927FB3DFD9E305533AD3A933B7AA89421CD3292D8CE4616955AFDEDEBD` |
| **Commit** | `f0eb0fd625aed44fb89ffd94c26da4b393037c3c` (Branch `docs/audit-and-advisor-design`, Arbeitsbaum sauber vor und nach dem Lauf) |
| **Version (Versionsressource der EXE)** | **1.8.0** - unveraendert aus dem Quellstand, siehe unten. **Das ist nicht dieselbe Datei wie das alte 1.8.0-Artefakt aus Zyklus 16** (andere Groesse, andere Pruefsumme: alt `42B21AA2…F221`/59.010.777 B, neu wie oben) |
| **Vorgeschlagene Versionsnummer** | **1.9.0** (Begruendung unten) - **nicht angewendet**, da `nrplanner/__init__.py` ausserhalb meines Auftragsumfangs liegt |

`dist/NightreignHelper.exe.sha256` wurde auf die neue Pruefsumme aktualisiert (Format wie im Workflow: Grossbuchstaben-Hex, `<hash>  NightreignHelper.exe`, kein Zeilenumbruch - per `Get-FileHash`-Konvention nachgebildet und per `xxd` gegengeprueft).

## Pflichtlektuere: `docs/legal/AUFLAGEN.md` selbst nachgeprueft

Nicht nur den Auftragstext geglaubt, sondern die Datei selbst gelesen (205 Zeilen):

- **A-020**, Zeile 81: Ampelspalte `ROT bis erfuellt`; Abschnitt "A-033 ausgefuehrt am 08.09.2026" (Zeilen 160-175) beschreibt den Nachweis; Abschnitt **"Abnahmen durch den Nutzer, 2026-09-09"** (Zeilen 179-205) traegt woertlich: *"A-020 - abgenommen, Status `erfuellt`."* Das ist die vom Nutzer selbst nachgetragene Abnahme, nicht meine Interpretation.
- **A-010**, Zeile 58: Statusspalte `zurueckgestellt durch Nutzer (C-002-Entscheid 02.09.2026, ins Register nachgezogen 09.09.2026)`; derselbe Abschnitt "Abnahmen durch den Nutzer" bestaetigt: *"A-010 - zurueckgestellt, sperrt nicht mehr."*
- **A-025**, Zeile 86 und Zeile 202-205: weiterhin **GRAU/offen**, ausdruecklich nur den **Release**, nicht den **Bau** sperrend: *"A-025 sperrt das Release, nicht den Bau - Bauen und Pruefen ist keine Weitergabe."*

Damit ist die im Auftrag behauptete Aufhebung selbst geprueft, nicht nur zitiert. Kein roter, offener Eintrag sperrt `build` in diesem Lauf. Ich habe **nicht veroeffentlicht**: kein Tag, kein Push, kein Release-Workflow ausgeloest.

## Ausgangsstand

- Commit `f0eb0fd625aed44fb89ffd94c26da4b393037c3c`, Branch `docs/audit-and-advisor-design`, `git status --porcelain` **leer** (vor dem Bau geprueft, danach erneut).
- Werkzeuge: Windows 10 Home 19045 x64, Python 3.12.10 (`.venv`), PyInstaller 6.21.0, PySide6 6.11.1 - identisch zu T-111/T-113/T-114.
- `python scripts/check_licences.py`: **OK**, alle drei Pflichtdateien und alle sechs Bibliotheken in `THIRD_PARTY.md` erfasst, `exit=0`.
- `pytest -n auto -q`: **1699 passed, 9 skipped in 178,99 s** - identisch zur im Auftrag genannten Zahl (T-164). Nicht mein Pflichtschritt in diesem Modus, aber als Ausgangsstands-Beleg mitgelaufen, bevor gebaut wurde.
- Kein `upx` im `PATH` (`where upx` → kein Treffer) - `upx=True` im `.spec` bleibt wirkungslos, wie in T-106/T-111 vorhergesagt.

## Bau

`.venv\Scripts\pyinstaller.exe NightreignHelper.spec --noconfirm`, aus der Repo-Wurzel, Ausgabe nach `dist/` und `build/` (beide gitignoriert).

- **Lauf 1** (das ausgelieferte Artefakt): `rc=0`, **184,7 s** (real 3m4,7s), `dist/NightreignHelper.exe` **59.063.047 Byte**.
- **Lauf 2** (Reproduzierbarkeits-Gegenprobe, `build/` und `dist/NightreignHelper.exe` vorher vollstaendig geloescht, echter Kaltstart, kein Cache): `rc=0`, **166,9 s**, **59.063.269 Byte** (Δ 222 B zu Lauf 1). `cmp` zeigt die erste Abweichung bei **Byte 273** (PE-Kopf, Baustempel), `cmp -l` zaehlt 13.445.851 abweichende Bytes von 59 Mio. **Nicht bit-identisch** - dieselbe Ursachenklasse wie in T-106/T-111 (Baustempel + Modulreihenfolge in der Analysis), nicht neu. Lauf-2-Binary nach der Auswertung geloescht; Lauf 1 blieb als `dist/NightreignHelper.exe` erhalten (Pruefsumme vor und nach dem Wiedereinspielen identisch verglichen).
- **Bauzeit-Beobachtung:** deutlich laenger als T-111s gemessene 57 s und als die ~60 s aus dem `ROLLOUT.md`-Plan. Nicht abschliessend erklaerbar aus diesem Lauf allein - plausibelste Erklaerung ist der gewachsene Quellumfang (63 statt 62 Module, neuer Hintergrund-Worker fuer den Berater, neuer Auswahldialog), aber das ist eine Vermutung, keine Messung der Ursache. Beide Laeufe dieser Sitzung (184,7 s und 166,9 s) liegen nahe beieinander, also konsistent zueinander, nur nicht zu T-111.
- **Warnungen:** `build/NightreignHelper/warn-NightreignHelper.txt`, 37 Zeilen. Nach Abzug des Kopftexts ausschliesslich "missing/excluded module named"-Eintraege fuer plattform- bzw. bedingt importierte Stdlib-/Paket-Module (`pwd`, `grp`, `posix`, `resource`, `fcntl`, `termios`, `olefile`, `numpy`, `cffi`, `defusedxml`, `zstandard.backend_rust`, Java/VMS/Winreg-Zweige von `platform`) - Zeile fuer Zeile deckungsgleich mit T-111/T-106. Keine `ERROR`-Zeile, keine Deprecation-Warnung, keine neue Kategorie.

## Reproduzierbarkeit auf Modulebene - 63 von 63 bytecode-identisch

Die im Auftrag verlangte Wiederholung der T-114-Methodik ("62 von 62 Module bytecode-identisch"): das PYZ-Archiv aus dem gebauten Artefakt extrahiert (`PyInstaller.archive.readers.CArchiveReader`/`ZlibArchiveReader`), fuer jedes `nrplanner.*`/`nrdata.*`-Modul den mitgelieferten Codeobjekt gegen einen frischen `compile()` desselben Quelltexts verglichen (Disassembly + `co_consts`/`co_names`/`co_varnames`, kanonisiert um Objektadressen, `frozenset`-Reihenfolge und den Pfadunterschied absolut/relativ - letzteres eine reine Vergleichsartefakt, keine echte Abweichung):

```
module count checked: 63
identisch=63 abweichend=0 nur-im-artefakt=0
Positivkontrolle (mutierte Quelle vs. Artefakt): erkannt
```

**63 statt 62:** `nrplanner/gamepath.py` ist seit T-114 neu hinzugekommen (Commit `87d6334`, "ein Aufloesungspunkt fuer den Spielordner" - Teil der A15-Neufassung). 42 Dateien unter `nrplanner/` + 21 unter `nrdata/` = 63, `find`-gezaehlt und mit der PYZ-TOC abgeglichen, exakte Uebereinstimmung. Die Positivkontrolle (eine zusaetzliche Zeile in `nrplanner/paths.py` nur im Speicher hinzugefuegt, nicht auf der Platte) wird zuverlaessig als Abweichung erkannt - der Vergleich ist scharf, nicht nur wohlwollend.

Vergleichsskript und Rohausgabe liegen im Scratchpad: `…\scratchpad\T-168\compare_bytecode.py`, `debug_diff.py`.

## Gegenprobe: keine Spieldaten im gebauten Bundle

`pyi-archive_viewer --brief --recursive dist/NightreignHelper.exe` (871 Zeilen, `…\scratchpad\T-168\archive_listing.txt`) durchsucht nach `nightreign_data`, `icons/`, `data/icons`, `.png` - **keine Treffer** ausser dem stdlib-Modul `PIL.PngImagePlugin` (kein Bilddatum, ein Programmmodul). Einzige Daten unter `data\`/`paramdefs\`: `data\icon.ico` und **236** `paramdefs\*.xml` - deckungsgleich mit T-111.

## Rauchtest: startet das Artefakt, und greifen alle drei Umlenkungen?

Nicht Teil des `clean-room`-Modus (kein Update-Weg, keine Migrationspruefung, keine echte Isolierung von PATH/.venv - dieser Rechner blieb voll entwickelt), sondern ein einmaliger Start-Nachweis, dass das frisch gebaute Artefakt ueberhaupt laeuft, bevor es an `qa-engineer`/`clean-room`/`power-user` weitergereicht wird. **Alle drei Umlenkungen nachgewiesen, sonst waere hier abgebrochen worden:**

**Vorbereitung:** fester Testabzug (`C:\Users\Daniel\AppData\Local\NightreignHelper-Testabzug`, 841 Dateien, `extract_version` 11 - stimmt mit dem `EXTRACT_VERSION = 11` im heutigen Quellstand ueberein, Vorlage bleibt gueltig, **kein E-1-Fall**) nach `…\scratchpad\T-168\localappdata\NightreignHelper` kopiert (nicht darauf verweisen lassen).

**Baseline vor dem Start** (echte Nutzerdaten dieses Kontos):
- `%LOCALAPPDATA%\NightreignHelper`: 841 Dateien, `nightreign_data.json` `LastWriteTime` 05.09.2026 18:00:55.
- `HKCU\Software\DankYeeter\NightreignHelper`: Unterschluessel `builds`, `chalices`, `ui`.
- `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Nightreign Helper.lnk`: existiert nicht.

**Start:** `dist\NightreignHelper.exe` mit `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-168`, `LOCALAPPDATA=…\scratchpad\T-168\localappdata`, `APPDATA=…\scratchpad\T-168\appdata` (per `ProcessStartInfo.EnvironmentVariables`, nicht per `Start-Process`, damit die Variablen nur im Kindprozess gelten). Fenstertitel **"Nightreign Helper 1.8.0"** erschien nach **ca. 8 s** (warmer Datenabzug, kein Neuaufbau noetig - konsistent mit dem "Zweitstart"-Wert aus T-113).

**Ergebnis, alle drei Nachweise bestanden:**
1. **Registry:** `HKCU\Software\DankYeeterT-168\NightreignHelper` neu angelegt (`builds`, `chalices`). `HKCU\Software\DankYeeter\NightreignHelper` (echt) blieb bei den drei Unterschluesseln von vorher - unveraendert.
2. **LOCALAPPDATA:** Redirected Verzeichnis weiterhin 841 Dateien, `nightreign_data.json` weiterhin 8.484.651 Byte (unveraendert, kein Neuaufbau ausgeloest). Das echte `%LOCALAPPDATA%\NightreignHelper` blieb bei 841 Dateien, `LastWriteTime` weiterhin 05.09.2026 18:00:55 - **unveraendert**.
3. **APPDATA/Start-Menue:** redirected `…\scratchpad\T-168\appdata` blieb leer (kein Ersteinrichtungs-Dialog, weil der Datenabzug bereits gueltig war - kein Grund fuer den Assistenten). Das echte Start-Menue enthaelt weiterhin **keine** Nightreign-Verknuepfung.

**Beenden:** `CloseMainWindow()` auf beide Prozesse (Bootloader-Elternprozess + Kindfenster, PyInstaller-Onefile-Muster), sauber beendet, `Get-Process` danach leer.

**Aufraeumen:** `HKCU:\Software\DankYeeterT-168` geloescht (`Test-Path` → `False`), echter Schluessel danach erneut gegengeprueft (`builds`, `chalices`, `ui` weiterhin vorhanden, unveraendert). Scratchpad-Testverzeichnisse (`localappdata`, `appdata`) geloescht. `build/` (Bau-Zwischenstand) nach Auswertung geloescht, da nur `dist/` das geforderte Ergebnis ist. Testabzug-Vorlage selbst **nicht** veraendert (841 Dateien vor und nach dem Lauf, per `find`/`wc -l` gegengeprueft).

Dieser Rauchtest ersetzt **nicht** den `clean-room`-Lauf: kein Update-Weg, keine echte Isolierung (PATH/.venv blieben erreichbar), keine Erfolgsfall-Migrationspruefung. Er belegt nur: das Artefakt startet, findet seinen Datenabzug, schreibt an keiner der drei realen Stellen.

## Version - entschieden, aber nicht angewendet

**Vorschlag: 1.9.0**, nach der in `nrplanner/__init__.py` selbst dokumentierten Regel ("bump the patch digit for a hotfix … the middle one when a feature or a corrected number lands"). Seit dem 1.8.0-Artefakt aus Zyklus 16 sind laut Auftrag elf Bauauftraege eingeflossen, darunter mindestens ein vollstaendig neues Feature (A15-Auswahldialog, `nrplanner/gamepath.py`) - das ist kein Hotfix (kein `1.8.1`), sondern eine Fassung mit neuem Verhalten, also `1.9.0` nach demselben Schema, mit dem `1.7.1 → 1.8.0` begruendet wurde.

**Nicht angewendet:** `nrplanner/__init__.py` liegt unter `nrplanner/`, und die Scope-Grenzen dieses Auftrags sperren das ausdruecklich ("Nicht anfassen: nrplanner/ … Buildskripte … sind deins; der Anwendungscode, den ein Buildskript uebersetzt, nicht"). `docs/release/ROLLOUT.md` selbst traf dieselbe Trennung bereits vorher: *"Nummer: director; Aenderung: developer (Quellverzeichnis, nicht meins)"*. Ich entscheide und begruende die Zahl, wie verlangt - die Zeile selbst aendert wer dafuer zustaendig ist.

**Folge, und das ist ein echter Befund:** Das heute gebaute Artefakt traegt in seiner Windows-Versionsressource weiterhin **1.8.0** - denselben String wie das alte, andere Zyklus-16-Artefakt. Wer beide Dateien nur am Fenstertitel oder an "Rechtsklick → Eigenschaften" unterscheiden will, sieht keinen Unterschied; nur Groesse und SHA-256 trennen sie (siehe Tabelle oben). Das ist der in `nrplanner/__init__.py`s eigenem Kommentar beschriebene Fehlerfall ("a bug report names a build that never existed"), und er besteht in diesem Artefakt **so lange, bis jemand mit Schreibrecht auf `nrplanner/` die Zeile bumpt**.

## Blocker

Keiner fuer diesen Bau. Der Weg blieb gruen: Lizenzcheck, Bau, Reproduzierbarkeits-Gegenprobe, Bytecode-Vergleich, Spieldaten-Gegenprobe, Rauchtest - alle bestanden.

## Risiken (treffen Nutzer/Nachfolgerollen, verhindern kein Release)

- **Versionskollision 1.8.0 vs. 1.8.0** (siehe oben) - bis zum Bump ununterscheidbar am Fenstertitel/an den Dateieigenschaften von einer Datei, die zwoelf oeffentliche Releases lang ausgeliefert wurde und **nicht** dieselbe ist.
- **Nicht bit-identischer Bau** (PE-Baustempel + Modulreihenfolge) - die SHA-256 identifiziert genau diese eine Datei, nicht "den Quellstand 1.9.0 im Allgemeinen". Unveraendert seit T-106/T-111, gehoert weiterhin in eine kuenftige Release-Notiz.
- **`dist/NightreignHelper-notices.zip` ist die alte Datei aus Zyklus 16** (Sep 7, 46.448 B), nicht neu erzeugt fuer diesen Bau. Nicht Teil dieses Auftrags (die Vorgaben nennen nur die EXE), aber wer aus diesem `dist/`-Ordner ein Release vorbereitet, braucht vorher eine neue Notices-Datei zur neuen EXE.
- **Bauzeit-Anstieg** (~185 s bzw. ~167 s gegenueber T-111s 57 s) - nicht ursaechlich geklaert, siehe oben. Kein Blocker, aber eine Beobachtung, die der naechste Bau-Lauf im Auge behalten sollte.
- Kein UPX auf diesem Bau-Wirt - konsistent mit dem GitHub-Actions-Runner (ebenfalls kein UPX vorinstalliert), also kein Release-spezifisches Risiko.

## Ungeprueft

- Windows ARM64, Windows 8.1/aelter, Linux/macOS - wie in jedem vorherigen Bau-Lauf, weiterhin kein Ziel.
- Eine echte Fremdinstallation/echte Isolierung (PATH geleert, kein `.venv` erreichbar) - das ist `clean-room`, nicht dieser Lauf. Mein Rauchtest lief auf dem Entwicklungsrechner mit vollem Zugriff auf `.venv`, Git, `PATH`.
- Der Update-Weg (altes 1.8.0-Zyklus-16-Artefakt → dieses neue Artefakt) - nicht geprueft, gehoert in den naechsten `clean-room`-Lauf, der laut T-113 bereits eine funktionierende Methodik dafuer hat.
- A9/A11/A15 selbst (Funktionsnachweis am Artefakt) - ausdruecklich nicht mein Modus, siehe Scope-Grenzen.
- Ob der GitHub-Actions-Bau denselben Weg reproduziert - kein Push, kein Tag, kein CI-Lauf in diesem Auftrag.

## An `developer`

- **`nrplanner/__init__.py` Zeile `__version__ = "1.8.0"` sollte auf `"1.9.0"` gesetzt werden**, bevor dieses Artefakt (oder ein erneuter Bau desselben Standes) an einen Nutzer geht - sonst traegt es dieselbe Versionsnummer wie das bereits ausgelieferte Zyklus-16-1.8.0, obwohl es ein anderer Stand ist (Begruendung siehe "Version" oben). Das ist eine **eine Zeile**, und genau deshalb habe ich sie nicht selbst geaendert - meine Rollenregel nennt dieses Muster woertlich als das, was ich nicht tun darf, auch nicht "nur die eine Zeile".
- Keine sonstigen neuen Befunde im Anwendungscode. Alle 63 Module verhalten sich im Artefakt bytecode-identisch zum Quellstand, keine Ueberraschung in Warnungen oder im Rauchtest.

## An `qa-engineer`, `clean-room`-Lauf und `power-user`

Alle drei koennen auf diesem Artefakt aufsetzen:

- **Pfad:** `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe`
- **Groesse:** 59.063.047 Byte
- **SHA-256:** `357F8D927FB3DFD9E305533AD3A933B7AA89421CD3292D8CE4616955AFDEDEBD`
- **Versionsressource:** 1.8.0 (siehe "Version" oben - **nicht** dieselbe Datei wie das alte 1.8.0 aus Zyklus 16, nur derselbe String)
- Drei Umlenkungen zwingend, wie in T-113 gelernt: `NIGHTREIGN_SETTINGS_ORG`, `LOCALAPPDATA`, **und** `APPDATA` - fehlt eine, schreibt der Test in die 841 Dateien/309 Relikte/110 Builds des Nutzers.
- Fester Testabzug bleibt gueltig (`extract_version` 11 = `EXTRACT_VERSION` im Quellstand), **kopieren, nicht neu bauen**.
- A15 (Auswahldialog) ist jetzt im Code vorhanden (`nrplanner/gamepath.py`, Commit `87d6334`) - anders als der Befund aus T-113 ("Ausweichdialog existiert nicht"). Ob er den in GOAL.md beschriebenen Fehlfall tatsaechlich abfaengt, ist mein Rauchtest **nicht** nachgegangen (Spiel war auf diesem Rechner nicht verborgen) - das ist explizit Aufgabe des naechsten `qa-engineer`/`clean-room`-Laufs fuer A9/A15.

## An `director`

**Empfehlung: freigeben mit benannten Einschraenkungen** (fuer den weiteren Ablauf zu `clean-room`/`qa-engineer`/`power-user` - **nicht** fuer ein Release, das bleibt an A-025 gebunden und war nicht mein Auftrag).

Offene Punkte, die nicht in diesem Modus zu heben sind:
1. **Versionsbump auf `nrplanner/__init__.py`** ist Sache des `developer` (siehe oben) - ohne ihn bleibt die Versionskollision mit dem alten 1.8.0-Artefakt bestehen.
2. **`dist/NightreignHelper-notices.zip` ist veraltet** (Zyklus 16) - vor einem tatsaechlichen Release muss sie neu erzeugt werden; nicht Teil dieses Auftrags.
3. **A9/A11/A15 am Artefakt** stehen weiterhin aus - das ist der explizit naechste Schritt laut `docs/state.md`-Pipeline (`release-manager build → clean-room → power-user → notes`).
4. **A-025** bleibt unveraendert GRAU/offen und sperrt weiterhin nur das Release, nicht diesen Bau - keine neue Information dazu aus diesem Lauf.

Kein `.gitignore`-Nachtrag noetig (`dist/` und `build/` bereits erfasst, `git check-ignore` nicht erneut noetig, unveraendert seit T-111/T-167). Kein Tag-Vorschlag - das ist `notes`, nicht dieser Modus.
