STATUS: erledigt
AUFTRAG: T-111 — Das Artefakt bauen (release-manager, Modus `build`)
GELESEN: docs/tasks/T-111.md · docs/state.md · docs/release/ROLLOUT.md ·
  NightreignHelper.spec · .github/workflows/release.yml ·
  nrplanner/__init__.py · nrplanner/favourites.py · nrplanner/paths.py ·
  CHANGELOG.md (existiert nicht, geprueft per `ls`/`git ls-files`, deckt sich
  mit L3 aus ROLLOUT.md)
GEÄNDERT: dist/NightreignHelper.exe (neu) · dist/NightreignHelper.exe.sha256
  (neu) · dist/NightreignHelper-notices.zip (neu) ·
  build/NightreignHelper/* (Bau-Zwischenstand, PyInstaller) — alle vier unter
  `dist/`/`build/`, beide gitignoriert, kein Git-Zustand veraendert. Scratchpad:
  T-111/archive_listing.txt, T-111/build1.log, T-111/build1_summary.txt,
  T-111/build2.log, T-111/pytest_pre_build.log (Zweitbau-Binaries build2/dist2
  nach Auswertung geloescht, nur Kennzahlen im Bericht behalten).
ANNAHMEN: keine — L1 (Versionsbump) war bereits durch T-109 erledigt, keine
  eigene Entscheidung noetig.
NÄCHSTER: clean-room (dieselbe Rolle oder wer sie als naechstes ausfuehrt)
BLOCKIERT DURCH: nichts

## Ausgangsstand (vor dem Bau)

- Commit `3fb56e464a448b22ab7ce6e7e7fb1d809d49473d`, Branch
  `docs/audit-and-advisor-design`, `git status` **sauber** (vor und nach
  Testlauf und Bau erneut geprueft).
- `python scripts/check_licences.py` (venv-Python): **OK**, alle drei
  Pflichtdateien und alle sechs Bibliotheken erfasst.
- Suite `pytest -n auto` (venv-Python): **1257 passed, 9 skipped, 0 failed**,
  119,51 s. Deckt sich mit dem in `docs/state.md` gemeldeten Stand.
- Werkzeuge: Windows 10 Home 19045 x64, Python 3.12.10 (`.venv`), PyInstaller
  6.21.0, PySide6 6.11.1. Kein `upx` im `PATH` (`where upx` → kein Treffer,
  auch im Build-Log keine UPX-Zeile) — `upx=True` im `.spec` bleibt wirkungslos,
  wie in T-106 vorhergesagt.

## Bau

`.venv\Scripts\pyinstaller.exe NightreignHelper.spec --noconfirm`, aus der
Repo-Wurzel, Ausgabe nach `dist/` und `build/` (Standardpfade des `.spec`,
beide in `.gitignore`).

- **Lauf 1** (das ausgelieferte Artefakt): `rc=0`, **57 s**,
  `dist/NightreignHelper.exe` **59.010.777 Byte**.
- **Lauf 2** (nur zur Reproduzierbarkeits-Gegenprobe, in den Scratchpad
  gebaut, nicht nach `dist/`): `rc=0`, **57 s**, **59.009.561 Byte** (Δ 1.216 B
  zu Lauf 1). `cmp` zeigt die erste Abweichung bei **Byte 273** — PE-Kopf,
  Baustempel. **Nicht bit-identisch**, wie in T-106 gemessen; Ursache
  unveraendert (Baustempel + Modulreihenfolge in der Analysis, kein
  Inhaltsunterschied). Lauf-2-Binaries sind nach der Auswertung geloescht.
- **Warnungen:** `build/NightreignHelper/warn-NightreignHelper.txt`, 37
  Zeilen. Nach Abzug des Kopftexts ausschliesslich "missing/excluded module
  named"-Eintraege fuer plattform- bzw. bedingt importierte Stdlib-/Paket-Module
  (`pwd`, `grp`, `posix`, `resource`, `fcntl`, `termios`, `olefile`, `numpy`,
  `cffi`, `defusedxml`, `zstandard.backend_rust`, Java/VMS/Winreg-Zweige von
  `platform`). Keine `ERROR`-Zeile, keine Deprecation-Warnung — deckungsgleich
  mit dem Befund aus T-106.

## Identifikation des Artefakts

- **Pfad:** `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe`
- **Groesse:** 59.010.777 Byte (56,3 MiB)
- **SHA-256:** `42B21AA2743FE64A83A093BE0261ABAEC361D99903150D620E5324BD4301F221`
  (per `Get-FileHash` **und** `sha256sum` gegengeprueft, identisch) — abgelegt
  in `dist/NightreignHelper.exe.sha256`, Format wie im Workflow
  (`<hash>  NightreignHelper.exe`, ASCII, ohne Zeilenumbruch).
- **Versionsbeleg an der gebauten Datei, nicht am Quelltext:**
  `(Get-Item dist\NightreignHelper.exe).VersionInfo` liefert
  `FileVersion = 1.8.0`, `ProductVersion = 1.8.0`, `CompanyName = DankYeeter`,
  `ProductName = Nightreign Helper`, `OriginalFilename = NightreignHelper.exe`.
  Das ist die Windows-Versionsressource der EXE selbst (Rechtsklick →
  Eigenschaften → Details zeigt dasselbe), keine Quelldatei wurde dafuer
  gelesen.

## Hinweispaket (fuer A-033)

Lokal mit denselben drei Schritten wie `release.yml` erzeugt: Pflichtpfade
pruefen (`LICENSE`, `THIRD_PARTY.md`, `licenses`,
`vendor/Paramdex/NOTICE` — alle vorhanden), dann
`Compress-Archive -Path $required -DestinationPath dist/NightreignHelper-notices.zip`.

- **Pfad:** `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper-notices.zip`
- **Groesse:** 46.448 Byte
- **Inhalt** (9 Eintraege):
  `LICENSE` (1.430 B) · `THIRD_PARTY.md` (8.255 B) ·
  `licenses\GPL-3.0.txt` (35.147 B) · `licenses\LGPL-3.0.txt` (7.652 B) ·
  `licenses\Pillow-LICENSE.txt` (78.016 B) ·
  `licenses\pycryptodome-LICENSE.rst` (2.987 B) ·
  `licenses\texture2ddecoder-LICENSE.txt` (1.083 B) ·
  `licenses\zstandard-LICENSE.txt` (1.511 B) ·
  `NOTICE` (1.958 B, aus `vendor/Paramdex/NOTICE` — `Compress-Archive` legt
  eine Einzeldatei aus einem Unterpfad ohne Ordnerpraefix ab; derselbe Befehl
  im Workflow tut dasselbe, das ist keine Abweichung meines Laufs, sondern
  wie das Archiv im Release aussehen wird).

## Gegenprobe: keine Spieldaten im gebauten Bundle

Der Waechter aus T-109 (`tests/test_release_spec_datas.py`) prueft die
`datas`-Liste der `.spec`. Ich habe stattdessen das **Ergebnis** befragt:
`pyi-archive_viewer --list --recursive dist/NightreignHelper.exe` (872
Zeilen, `T-111/archive_listing.txt` im Scratchpad) durchsucht nach
`nightreign_data`, `icons/`, `data/icons` und `.png` — **keine Treffer**.

Die einzigen Daten unter `data\` bzw. `paramdefs\`:

- `data\icon.ico` (134.008 B entpackt) — das Programmsymbol, keine Spieldaten.
- 236 Dateien unter `paramdefs\*.xml` (Feldschemata aus
  `vendor/Paramdex/NR/Defs`) — Deckungsgleich mit T-106.

Kein `nightreign_data.json`, kein `nrplanner/data/icons`-Ordner im gebauten
Bundle. Die Grenze haelt nicht nur in der Spec, sondern im Ergebnis.

## Wo alles liegt (absolute Pfade)

- Artefakt: `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe`
- Pruefsumme: `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe.sha256`
- Hinweispaket: `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper-notices.zip`
- Bau-Zwischenstand (Warnungen, TOC, PYZ/PKG): `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\build\NightreignHelper\`
- Archiv-Listing (Gegenprobe Spieldaten):
  `C:\Users\Daniel\AppData\Local\Temp\claude\C--Users-Daniel-Desktop-ClaudeCode-Nightreign-Helper\d5442c81-d951-4427-90b6-000173ab1906\scratchpad\T-111\archive_listing.txt`
- Bau- und Testlogs: derselbe Scratchpad-Ordner, Dateien `build1.log`,
  `build1_summary.txt`, `build2.log`, `pytest_pre_build.log`.

Alle drei nachfolgenden Rollen (`clean-room`, `qa-engineer`, `power-user`)
benutzen **dieselbe** Datei unter `dist\NightreignHelper.exe`
(SHA-256 `42B21AA2743FE64A83A093BE0261ABAEC361D99903150D620E5324BD4301F221`) —
niemand baut neu.

## QA-195 — Variablen fuer clean-room und power-user (verbindlich)

Ohne diese zwei Variablen schreibt jeder Testlauf in die echten Daten dieses
Rechners:

- **`NIGHTREIGN_SETTINGS_ORG`** — Standardwert im Programm ist `"DankYeeter"`
  (`nrplanner/favourites.py:25`, `os.environ.get("NIGHTREIGN_SETTINGS_ORG") or "DankYeeter"`).
  Fuer isolierte Laeufe auf einen abweichenden Wert setzen, z. B.
  `NIGHTREIGN_SETTINGS_ORG=DankYeeterCleanroom`. Es gibt zusaetzlich
  `NIGHTREIGN_SETTINGS_APP` (Standard `"NightreignHelper"`,
  `nrplanner/favourites.py:26`) — normalerweise nicht noetig zu aendern, aber
  vorhanden, falls zwei isolierte Laeufe parallel nicht kollidieren duerfen.
- **`LOCALAPPDATA`** — auf ein Wegwerf-Verzeichnis umlenken
  (`nrplanner/paths.py:20`, `os.environ.get("LOCALAPPDATA")`); dort liegen
  `nightreign_data.json` und das Icon-Pack. Ohne Umlenkung landet der
  Datenabzug im echten `%LOCALAPPDATA%\NightreignHelper` des Nutzers.

Beide Variablen muessen in der Prozessumgebung stehen, **bevor** die EXE
startet (PyInstaller-Einzeldatei liest sie beim eigenen Start).

## Blocker

Keine. Der Bauweg blieb gruen, wie in T-106 vorhergesagt; L1 (Versionsbump)
war bereits durch T-109 erledigt.

## Risiken (treffen Nutzer, verhindern kein Release)

- **Nicht bit-identischer Bau** (PE-Baustempel + Modulreihenfolge) — die
  SHA-256 in `dist/NightreignHelper.exe.sha256` identifiziert genau diese
  Datei, nicht den Quellstand. Gehoert in die Release-Notiz (L7 aus
  `docs/release/ROLLOUT.md`, unveraendert).
- Kein UPX auf diesem Bau-Wirt — ein Rechner mit UPX im `PATH` baut eine
  andere (kleinere) Datei bei gleichem Quellstand. Nur relevant, falls der
  tatsaechliche Release-Bau auf einem anderen Rechner als diesem laeuft; der
  GitHub-Actions-Runner hat ebenfalls kein UPX vorinstalliert, insofern
  konsistent mit dem CI-Bau.

## Ungeprueft

- Windows ARM64, Windows 8.1/aelter, Linux/macOS — wie in T-106 vermerkt,
  weiterhin nicht Teil dieses Laufs.
- Eine echte Fremdinstallation (anderes Geraet/Konto) — dieser Lauf fand auf
  dem Entwicklungsrechner statt, siehe `clean-room`-Auftrag als naechsten
  Schritt.
- Der GitHub-Actions-Bau selbst lief nicht (kein Push, kein Tag) — dieser
  Bericht bezeugt den lokalen Bauweg mit denselben Schritten, nicht den
  CI-Lauf.

## An `developer`

Keine neuen Befunde im Anwendungscode. Die einzigen bereits bekannten Punkte
(A15/Sackgasse ohne gefundenes Spiel, L5; SmartScreen/UPX, L6) stehen
unveraendert in `docs/release/ROLLOUT.md` und sind nicht meine Zustaendigkeit
in diesem Lauf.

## An `power-user` (Ausgangspunkt seiner Sitzung)

- Artefakt: `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe`
  (SHA-256 `42B21AA2743FE64A83A093BE0261ABAEC361D99903150D620E5324BD4301F221`,
  Version 1.8.0 laut Versionsressource).
- Vor dem Start `NIGHTREIGN_SETTINGS_ORG` und `LOCALAPPDATA` wie oben
  umlenken — sonst schreibt die Sitzung in die echten Daten dieses Rechners
  (QA-195).
- Installationsanleitung: README des Repos (keine eigene Anleitung von mir
  erzeugt — die Ablage entspricht dem, was der Nutzer nach der Anleitung von
  der Releases-Seite bekaeme).
- Vorwarnung aus T-106 unveraendert: SmartScreen-Dialog (unsigniert), rund
  eine Minute Erststart-Datenaufbau, Sackgasse falls die Spiel-Automatik den
  Installationsordner nicht findet (A15/L5, nicht behoben).

## An `director`

- **Empfehlung: freigeben mit benannten Einschraenkungen.** Der Bauweg ist
  gruen, das Artefakt traegt korrekt 1.8.0, die Spieldaten-Grenze haelt auch
  im Ergebnis, das Hinweispaket ist vollstaendig. Offen bleiben ausschliesslich
  Punkte, die nicht in diesem Modus zu heben sind: **L2** (Update-Weg am
  Artefakt, naechster Schritt `clean-room`), **L3** (`CHANGELOG.md` fehlt
  weiterhin — Dateisystem und `git ls-files` erneut geprueft, kein Treffer;
  gehoert in den `notes`-Lauf), **L4** (9 lokale Commits ungepusht, PR #16
  offen — `archivist`/Nutzer), **L7** (Nicht-Reproduzierbarkeit, siehe oben,
  Release-Notiz-Text).
- **`.gitignore`:** keine fehlenden Eintraege. `dist/` und `build/` sind
  bereits erfasst (Zeilen 9-10), von mir nur bestaetigt, nicht geaendert.
- **Kein Tag-Vorschlag von mir** — das ist Teil des `notes`-Modus, nicht
  dieses Laufs.
- Offene Entscheidung unveraendert aus `docs/release/ROLLOUT.md`: ARM64
  zusagen oder nicht, sowie die C-003-Fragen beim Nutzer (A-025 Verbreitung
  vs. Nutzung, Repo-Sichtbarkeit, Arbeitsvertrag, US-Recht) — alle weiterhin
  unbeantwortet, keine davon durch diesen Bau beruehrt.
