# Rollout

Fortgeschrieben, ein `## {Version}`-Abschnitt je Lauf. **Bestehende Abschnitte
werden nie ueberschrieben.**

---

## 1.8.0 (vorgeschlagen, nicht entschieden) — 2026-09-07, T-106, Modus `plan`

Gemessen gegen Commit `006a604` (`docs/audit-and-advisor-design`, Arbeitsbaum
sauber vor und nach diesem Lauf). Werkzeuge: Windows 10 Home 19045 x64,
Python 3.12.10, PyInstaller 6.21.0, PySide6 6.11.1.

### 0. Die Ausgangslage der Auftragsakte stimmt nicht

`docs/state.md` und der Auftrag T-106 sagen: *"es gab nie ein gebautes
Artefakt, weder lokal noch ueber die Releases-Seite"*. Am Bestand geprueft ist
das falsch:

| Messung | Wert |
|---|---|
| Releases auf `DankYeeter/Nightreign-Helper` | **12** (`gh release list --limit 100`) |
| davon mit `NightreignHelper.exe` als Asset | **12 von 12** (`gh api .../releases`) |
| juengstes Release | **v1.7.1**, 2026-08-24, 58.827.005 B, 2 Downloads |
| Downloads ueber alle Releases | **25** |
| Tags lokal | 12: `v1.0.0` … `v1.7.1` |

**Folge, und sie aendert den ganzen Plan:** Dies ist **kein Erstrelease**,
sondern ein Update ueber eine vorhandene Installationsbasis. Der Weg, der
scheitern kann, ist damit nicht die Erstinstallation, sondern das **Update
ueber 1.7.1** — und der ist heute ungeprueft.

### 1. Zielsysteme

| System | Stand |
|---|---|
| Windows 10/11 **x64** | zugesagt (GOAL.md „Rahmen"), einziges gebautes Ziel |
| Windows **ARM64** | **nicht gebaut.** PyInstaller nimmt den Bootloader `Windows-64bit-intel`; ein x64-Artefakt laeuft auf ARM64 nur ueber die Windows-Emulation, ungeprueft |
| Windows 8.1 / aelter | nicht zugesagt, nicht gebaut (PySide6 6.11 verlangt Win10 1809+) |
| Linux / macOS | **nie geprueft**, ausdrueckliches Nicht-Ziel (das Programm liest eine Windows-Spielinstallation) |

Offene Frage an den App Designer: soll ARM64 zugesagt werden? Heute steht
nirgends, dass es ausgeschlossen ist — die Releases-Seite bietet eine Datei
ohne Architekturangabe an.

### 2. Laufzeit-Voraussetzungen auf dem Zielrechner

**Der Nutzer muss nichts installieren.** Am gebauten Artefakt geprueft (TOC des
Probebaus, 500 Eintraege):

- Python-Laufzeit, PySide6/Qt, pycryptodome, zstandard, pillow,
  texture2ddecoder: **im Artefakt**.
- `VCRUNTIME140.dll`, `VCRUNTIME140_1.dll` und die `api-ms-win-*`-Stubs:
  **im Artefakt** — es braucht **kein** Visual-C++-Redistributable.
- An Daten mitgeliefert: `data\icon.ico` und **236** Paramdef-XML unter
  `paramdefs\` (2,4 MB Quelle).

**Was der Nutzer trotzdem selbst haben muss, einzeln benannt:**

1. **Eine Installation von ELDEN RING NIGHTREIGN.** Ohne sie gibt es keine
   Daten; das Programm bringt keine mit (bewusst). Findet die Automatik den
   Ordner nicht, endet der Erststart heute in `QMessageBox.critical`
   („Could not read your game…", `nrplanner/app.py:4396-4400`) — **A15 ist
   spezifiziert, aber nicht gebaut**, es gibt keinen Auswahldialog. Das ist
   der wahrscheinlichste Abbruchgrund einer Fremdinstallation.
2. **Rund 60 MB Platz fuer die EXE** plus den Datenabzug unter
   `%LOCALAPPDATA%\NightreignHelper` (auf diesem Rechner: 8,5 MB Snapshot
   plus Icon-Ordner).
3. **Geduld beim Erststart:** rund eine Minute Datenaufbau (README,
   `nrplanner/firstrun.py`), davor bei jedem Start das Auspacken einer
   56-MiB-Einzeldatei.

### 3. Abhaengigkeiten

- `requirements.txt` fixiert alle sieben Eintraege auf `==`-Versionen. Keine
  Bereiche, kein `latest`.
- **Nicht fixiert sind die Hashes.** Der Release-Workflow ruft
  `pip install -r requirements.txt` ohne `--require-hashes`. Der Nutzer hat
  das am 02.09.2026 als tragbares Restrisiko entschieden (SEC-009,
  `security/findings.md`) — hier nur als Zustand vermerkt, nicht neu
  aufgeworfen.
- **Nur lokal vorhandene Abhaengigkeit: keine gefunden.** Gesucht wurde nach
  `sys._MEIPASS`-Aufloesung, absoluten Pfaden und Umgebungsvariablen;
  `nrplanner/datasource.py` loest Icon, Snapshot und Paramdefs ueber
  `_MEIPASS` bzw. den Nutzer-Cache auf, `nrplanner/paths.py` ueber
  `%LOCALAPPDATA%`. `vendor/Paramdex/NR/Defs` liegt im Repository und geht in
  das Artefakt.
- **UPX:** der `.spec` setzt `upx=True`, auf diesem Rechner ist **kein `upx`
  im PATH** — es wurde also nicht komprimiert. Ein Rechner **mit** UPX baut
  eine andere Datei. Das gehoert in die Bauanweisung, sonst wandert die
  Artefaktgroesse mit dem Bauwirt.

### 4. Datenhaltung

| Ort | Inhalt | ueberlebt Neuinstallation |
|---|---|---|
| `%LOCALAPPDATA%\NightreignHelper\nightreign_data.json` | Datenabzug aus dem Spiel | ja (wird bei Bedarf neu gebaut) |
| `%LOCALAPPDATA%\NightreignHelper\icons\` | Icon-Pack | ja |
| `HKCU\Software\DankYeeter\NightreignHelper` | **die Arbeit des Spielers**: gespeicherte Builds, Kelche, Favoriten, Fensterzustand, UI-Skalierung | ja — und genau deshalb ist die Migration der kritische Punkt |
| `%APPDATA%\…\Startmenue\…\.lnk` | Verknuepfung, nur wenn angeboten und angenommen | ja |

Alle vier sind ohne Adminrechte schreibbar. Der Ablageort ist **nicht** nach
Version getrennt: alte und neue Fassung teilen Cache **und** Registry.

### 5. Erstinstallation vs. Update

**Erstinstallation:** EXE von der Releases-Seite herunterladen und starten.
Kein Installer, keine Adminrechte. Was der Nutzer sieht — und was in die
Release-Notiz gehoert, weil es nach einem Fehler aussieht und keiner ist:

1. **SmartScreen.** Die EXE ist **nicht signiert** (`codesign_identity=None`).
   Ein frisch veroeffentlichtes, unsigniertes Binary ohne Reputation zeigt
   „Der Computer wurde durch Windows geschuetzt"; „Trotzdem ausfuehren" liegt
   hinter „Weitere Informationen".
2. **Virenscanner.** PyInstaller-Einzeldateien entpacken sich beim Start in
   ein Temp-Verzeichnis und werden regelmaessig als Fehlalarm gemeldet. Das
   ist ein bekanntes Risiko dieser Bauform, hier **nicht gemessen** (kein
   Zweitscanner, keine Fremdmaschine).
3. **Wartezeit vor dem Fenster.** 56 MiB auspacken bei jedem Start, dann beim
   ersten Mal rund eine Minute Datenaufbau mit Fortschrittsanzeige.
4. **Angebot der Startmenue-Verknuepfung** (`nrplanner/shortcut.py`).

**Update ueber 1.7.1 — der Weg, der heute nicht abgesichert ist.** Zwei
Umstellungen liegen zwischen `v1.7.1` und `006a604`:

- **`EXTRACT_VERSION` 8 → 11.** Der Datenabzug des Nutzers gilt damit als
  veraltet; der erste Start nach dem Update baut ihn neu (~1 Minute, sichtbar).
  Kein Datenverlust, aber eine Wartezeit, die erklaert werden muss.
  `ICON_VERSION` bleibt **3** — das Icon-Pack wird nicht neu gebaut.
- **Der Schluesselraum der gespeicherten Builds wird migriert.** `v1.7.1`
  kennt `SCHEMA_KEY` nicht (`git show v1.7.1:nrplanner/chalices.py`: kein
  Treffer) — es ist der Zustand „vor jeder Ableitung", in dem der **Name**
  der Schluessel ist. Der heutige Stand fuehrt `CURRENT_SCHEMA = "3"` und
  raeumt beim ersten Zugriff um (`_migrate_keys`). **Die Arbeit des Spielers
  wird also beim ersten Start nach dem Update angefasst.** Der Code ist gegen
  die bekannten Fallen gebaut (QA-003, QA-033, QA-035, QA-041, QA-046,
  QA-050: erst lesen, dann schreiben, zuletzt loeschen; nur loeschen, was
  zurueckgelesen wurde), und die Suite deckt es ab — **gegen ein gebautes
  Artefakt ist es nie gelaufen.**
- Auf diesem Entwicklungsrechner steht der Speicher **bereits** auf Schema 3
  (`reg query HKCU\Software\DankYeeter\NightreignHelper\builds\1` →
  `__schema REG_SZ 3`). Der Migrationsweg ist hier also **nicht mehr
  beobachtbar** und muss im `clean-room` kuenstlich hergestellt werden.

### 6. Rueckweg

- **Deinstallation:** EXE loeschen, `%LOCALAPPDATA%\NightreignHelper` loeschen,
  `HKCU\Software\DankYeeter` loeschen, Verknuepfung loeschen. Der README nennt
  genau diese vier. Es gibt **keinen Deinstallierer**, der das tut.
- **Downgrade auf 1.7.1: verlustbehaftet und nicht vorgesehen.** Nach der
  Migration stehen die Builds unter abgeleiteten Schluesseln
  (`Fire / ice` → `fire%20%2F%20ice`). Die 1.7.1-Fassung liest Schluessel als
  Namen — der Spieler saehe seine Builds unter verstuemmelten Namen oder gar
  nicht. **Ohne vorherige Sicherung gibt es keinen Weg zurueck.**
  Empfehlung fuer den `notes`-Lauf: ein Satz und ein Befehl —
  `reg export "HKCU\Software\DankYeeter" nightreign-backup.reg` — **vor** dem
  Update.
- Der Datenabzug ist unkritisch: eine aeltere Fassung erkennt den neueren
  `extract_version` als fremd und baut ihren eigenen neu.

### 7. Luecken bis zum lauffaehigen Rollout

| # | Luecke | Aufwand | Rolle |
|---|---|---|---|
| L1 | `__version__` steht auf **1.7.1**, und `v1.7.1` ist bereits veroeffentlicht. Der Tag existiert; ein Tag `v1.8.0` liesse den Schritt „Tag must match the version in the source" **fehlschlagen**. Ohne Bump geht kein Release heraus | 1 Zeile in `nrplanner/__init__.py` | Nummer: `director`; Aenderung: `developer` (Quellverzeichnis, nicht meins) |
| L2 | Update ueber 1.7.1 (Schluesselmigration + Neuaufbau des Abzugs) ist an keinem Artefakt geprueft | ein `clean-room`-Durchgang | `release-manager` |
| L3 | `CHANGELOG.md` existiert nicht (Dateisystem **und** `git ls-files` geprueft) — 353 Commits seit `v1.7.1` ohne Nutzertext | ein `notes`-Lauf | `release-manager` |
| L4 | Die 9 lokalen Commits sind nicht gepusht, PR #16 ist offen, `main` ist geschuetzt und steht 351 Commits zurueck. Ein tag-getriebenes Release braucht den Stand am Remote | Push + Merge | `archivist` / **Nutzer** |
| L5 | A15 (Erststart ohne gefundenes Spiel) ist spezifiziert, nicht gebaut. Jede Fremdinstallation mit ungewoehnlichem Speicherort endet in einer Sackgasse | Umsetzung AK-106-132 | `developer` |
| L6 | Keine Signatur → SmartScreen bei jedem Nutzer | Zertifikat, Kosten | **Nutzer** |
| L7 | Der Bau ist **nicht bit-identisch** wiederholbar (siehe unten). Die SHA-256 des Releases identifiziert **eine Datei**, nicht den Quellstand | Aufnahme in die Release-Notiz | `release-manager` |
| L8 | `release.yml` faehrt **keine Tests**. Ein Tag baut und veroeffentlicht ohne Suite | ein Schritt oder eine Regel | `director` entscheidet |

### Die sechs Fragen aus T-106, kurz beantwortet

**1. Geht der Bau?** **Ja, gemessen.** Zwei vollstaendige Probebauten,
`rc=0`, **61 s** und **58 s**, Ergebnis **59.010.324 B** (56,3 MiB).
Werkzeuge und Abhaengigkeiten dieses Rechners reichen; es fehlt nichts.
Nachweis, Warnungen und Reproduzierbarkeit unter „Befunde des Probebaus".

**2. Was bringt der `.spec` mit, was er nicht soll?** Nichts —
aber **die Grenze zieht er nicht, er stolpert nur nicht darueber**. `datas`
zaehlt genau zwei Quellen auf (`nrplanner/data/icon.ico`,
`vendor/Paramdex/NR/Defs`); es gibt keinen Glob ueber `nrplanner/data` und
keine Pruefung wie im Workflow. **Beweis, dass nichts eingesammelt wird:**
`nrplanner/data/icon.png` liegt (1.245.708 B) direkt neben der `icon.ico` und
ist im Bundle **nicht enthalten**. Laege also `nightreign_data.json` oder
`icons/` im Baum, kaeme es trotzdem nicht in die EXE. **Der Workflow-Schritt
„Refuse to ship game data" ist damit eine Hygienepruefung des Baums, keine
Schutzwand — und er laeuft ausserdem erst *nach* dem Bau.** Ein lokaler Bau
umgeht ihn, ohne dass daraus ein Leck folgt. Das Restrisiko ist eine Aenderung
am `.spec` selbst; ein Waechter dagegen gehoerte in `tests.yml` (Vorschlag,
kein Auftrag).

**3. Wie kommt der Nutzer an das Programm?** Siehe Abschnitt 5. In
Nutzersprache: *herunterladen, Warnung wegklicken, warten, einmal eine Minute
zuschauen, danach sofort*.

**4. Nutzerdaten und Migration.** Siehe Abschnitte 4 bis 6. Fuer den
`notes`-Lauf verbindlich: (a) der erste Start nach dem Update dauert wieder
eine Minute, (b) gespeicherte Builds werden einmalig umgeraeumt, (c) ein
Downgrade ist ohne Registry-Sicherung nicht vorgesehen.
**QA-195 beruehrt den `clean-room` unmittelbar:** unter derselben Organisation
`DankYeeter` liegt neben `NightreignHelper` ein `NightreignHelperTests`
(`reg query HKCU\Software\DankYeeter`, beide bestaetigt). Ein Artefakttest auf
diesem Rechner schreibt **in die echten Daten des Nutzers**, wenn er nichts
dagegen tut. Dagegen zu tun ist: `NIGHTREIGN_SETTINGS_ORG` setzen (existiert
in `v1.7.1` **und** heute, `nrplanner/favourites.py:25`) und `LOCALAPPDATA`
auf ein Wegwerf-Verzeichnis zeigen lassen.

**5. Versionsstand.** Quelle sagt **1.7.1**, veroeffentlicht ist **1.7.1**.
Vorschlag: **1.8.0** — die Projektregel in `nrplanner/__init__.py` sagt
„mittlere Stelle, wenn eine Funktion oder eine korrigierte Zahl landet", und
seit `v1.7.1` liegen 353 Commits mit dem Build-Berater als neuer Funktion.
**Entscheidet der `director`.** Die Zeile aendert der `developer`; sie liegt
im Quellverzeichnis und damit nicht in meiner Zustaendigkeit.

**6. Urteil: FAIL fuer ein Release heute** — bei gleichzeitig gruenem Bauweg.
Was es hebt: **L1** (Versionsbump, sonst faellt der Workflow), **L2**
(Update-Weg am Artefakt geprueft), **L3** (Changelog mit dem Satz zur
Migration), **L4** (Stand am Remote). L5-L8 sind benannte Einschraenkungen,
keine Sperren — ueber sie entscheidet der `director`.

### Befunde des Probebaus (T-106, nicht der `build`-Lauf)

Ausgefuehrt aus dem Repo-Wurzelverzeichnis, Ziel **ausserhalb** des
Repositories, damit der `build`-Lauf nichts vorfindet, was er fuer seins
haelt:

```
.venv\Scripts\pyinstaller.exe NightreignHelper.spec --noconfirm
    --distpath <scratchpad>\T-106\dist1 --workpath <scratchpad>\T-106\build1
```

- **`dist/` und `build/` im Repository sind unberuehrt** (existieren nicht),
  beide stehen in `.gitignore`. **Kein fehlender `.gitignore`-Eintrag.** Alle
  Probeartefakte sind geloescht; `git status` ist sauber bis auf
  `docs/legal/C-003.md` des parallel laufenden T-104.
- **Warnungen: keine.** `warn-NightreignHelper.txt` (37 Zeilen) enthaelt
  ausschliesslich „missing module named"-Eintraege der ueblichen optionalen
  Importe der Standardbibliothek. Keine `ERROR`-Zeile, keine Deprecation.
- **Der `.spec` liest `nrplanner/__init__.py` ueber einen relativen Pfad.**
  Ein Bau aus einem anderen Arbeitsverzeichnis bricht mit
  `could not find __version__` ab. Der `build`-Lauf startet aus der Wurzel.
- **Versionsressource der EXE** (`Get-Item .VersionInfo`): FileVersion und
  ProductVersion **1.7.1**, CompanyName `DankYeeter`, OriginalFilename
  `NightreignHelper.exe`. Der `.spec` funktioniert — nach dem Bump traegt er
  die neue Nummer von selbst.
- **Reproduzierbarkeit: nein, nicht bit-identisch.**

  | | Lauf 1 | Lauf 2 |
  |---|---|---|
  | Groesse | 59.010.324 B | 59.011.279 B (Δ 955 B) |
  | SHA-256 | `f5b50846658560ad4f2f31f2ee4ab3b5937912faf0cccd4773d7d6f9e577a47d` | `e92673047bd14a09eac6d28a0f9259887f0e3ea288c8ba5358ae673afd3aa367` |

  **Quelle der Abweichung, soweit eingegrenzt:** der Inhalt ist gleich, die
  Verpackung nicht. `PYZ-00.pyz` ist **byte-identisch** (`cmp` = 0,
  3.087.062 B), und die Eintragsmenge von `PKG-00.toc` ist nach Normalisierung
  des Arbeitspfads **identisch** (0 Diff-Zeilen). Unterschiedlich sind (a) die
  erste Abweichung bei **Byte 273** — PE-Kopf, der den Baustempel traegt — und
  (b) die **Reihenfolge** der Module in `Analysis-00.toc` (`enum`, `types`,
  `tracemalloc` tauschen zwischen den Laeufen die Plaetze), woraus die 955 Byte
  Unterschied im CArchive folgen.
  **Konsequenz fuer das Release:** die SHA-256-Datei aus `release.yml` belegt
  die **ausgelieferte Datei**, nicht den Quellstand. Wer nachbaut, bekommt eine
  andere Pruefsumme. Das gehoert so in die Release-Notiz, sonst liest es sich
  als Manipulation.

### Ablaufplan fuer den `build`-Lauf

1. `git status` vor dem Bau; `docs/legal/C-003.md` (T-104) gehoert nicht dazu.
   Nur aus einem sauberen Stand bauen, Commit-Kennung in den Bericht.
2. **Zuerst pruefen, ob L1 entschieden ist.** Baut man mit `__version__`
   1.7.1, traegt das Artefakt die Nummer einer bereits ausgelieferten Datei —
   genau der Fehler, den `nrplanner/__init__.py` in seinem eigenen Kommentar
   beschreibt.
3. `python scripts/check_licences.py` vor dem Bau — der Workflow tut es auch,
   lokal faellt es sonst durch.
4. `.venv\Scripts\pyinstaller.exe NightreignHelper.spec --noconfirm` aus der
   Repo-Wurzel. Rechne mit **~60 s** und **~56 MiB**.
5. Kein `upx` im PATH; taucht doch eines auf, im Bericht nennen.
6. `Get-FileHash -Algorithm SHA256` auf das Ergebnis, Wert in den Bericht.
   Zweiter Bau nur, um L7 zu bestaetigen — nicht, um Gleichheit zu erwarten.
7. Artefakt bleibt in `dist/` (gitignoriert) und wird im Bericht mit Pfad,
   Groesse und Pruefsumme genannt.

### Ablaufplan fuer den `clean-room`-Lauf

Reihenfolge nach Wert, nicht nach Bequemlichkeit — Schritt 3 ist der, an dem
echte Releases scheitern.

0. **Isolierung herstellen und im Bericht benennen:** eigenes leeres
   Verzeichnis, `LOCALAPPDATA` auf ein Wegwerf-Verzeichnis,
   `NIGHTREIGN_SETTINGS_ORG=DankYeeterCleanroom`, geleerter `PATH`, keine
   `.venv` erreichbar. **Ohne die beiden Variablen schreibt der Test in die
   Builds des Nutzers** (QA-195). Was nicht isoliert werden konnte — echte
   Fremdmaschine, fremdes Konto, Virenscanner —, wird als **ungeprueft**
   ausgewiesen, nicht als bestanden.
1. Nur die EXE in das leere Verzeichnis, Installation **ausschliesslich** nach
   README. Abweichung vom Text = Befund gegen den Text.
2. Starten, eine Aktion ausfuehren, **die schreibt** (Build speichern),
   beenden, neu starten, Build wieder da?
3. **Update-Weg, der Kern des Laufs:** `gh release download v1.7.1` → 1.7.1 in
   der isolierten Umgebung starten → mehrere Builds speichern, darunter
   **einen Namen mit `/`, einen mit `|`, einen mit Grossbuchstaben** (die drei
   Faelle, aus denen QA-003, QA-046 und die Migration entstanden sind) →
   beenden → neue EXE darueber → starten → **sind alle Builds unter ihren
   Namen da?** Danach `reg query` auf `__schema`: steht `3`.
4. Zweitstart nach Neustart der Umgebung — siehe CLAUDE.md, Abschnitt
   "Datenverzeichnisse und Umlenkung" (QA-256, NH-004).
5. Aufraeumen: Verzeichnis, Wegwerf-`LOCALAPPDATA`, Test-Organisation in der
   Registry, etwaige Verknuepfung. Was liegen bleibt, kommt in den Bericht.

### An den `power-user` (Ausgangspunkt seiner Sitzung)

Es gibt heute **kein** abgelegtes Artefakt — die beiden Probebauten sind
geloescht. Sein Ausgangspunkt entsteht im `build`-Lauf und wird dort mit Pfad
genannt. Vorwarnung fuer seine Sitzung: SmartScreen-Dialog, rund eine Minute
Erststart, und die Sackgasse aus L5, falls die Automatik das Spiel nicht
findet.

---

## 1.10.0 — 2026-09-14, T-241e, Modus `notes`

Gemessen gegen Artefakt-Commit `1b36238`, HEAD zum Zeitpunkt dieses Laufs
`1fb9ac8` (nur `docs/berichte/`, ruehrt den Code nicht an). Artefakt
`dist/NightreignHelper.exe`, 59.083.751 B, SHA-256
`11f5eecd3be4dbc2583ad1dca82dda0f78d54f84b205a4ab6f060f028792158c`
(certutil nachgemessen, siehe Korrektur in
`docs/berichte/T-241-release-manager-build.md`). Kein Release, kein Push,
keine Weitergabe in diesem Lauf (Nutzerauftrag 12./14.09.).

### L1-L8, Stand gegen die 1.8.0-Liste oben

| # | 1.8.0-Luecke | Stand 1.10.0 |
|---|---|---|
| L1 | `__version__` nicht gebumpt | **gehoben.** `nrplanner/__init__.py` steht auf `1.10.0` (developer, vor T-241c). |
| L2 | Update-Weg an keinem Artefakt geprueft | **weiterhin offen, jetzt schwerer:** kein 1.9.0-Artefakt mehr vorhanden (`gh release list` zeigt nur `v1.7.1`; lokale Suche nach der 1.9.0-Pruefsumme `A2180D5D…66EF3` aus T-174 findet nichts). T-241d (`clean-room`) weist Schritt 3 deshalb als **ungeprueft** aus, nicht als bestanden. Migration (`__schema`, `EXTRACT_VERSION`) bleibt damit am Artefakt unverifiziert — siehe Migrationsabschnitt unten. |
| L3 | Kein `CHANGELOG.md` | **gehoben.** `CHANGELOG.md` neu angelegt (Keep-a-Changelog, Englisch), Abschnitt 1.10.0 mit den Nutzeraenderungen seit 1.9.0. |
| L4 | Lokale Commits nicht am Remote | unveraendert offen, betrifft diesen Lauf nicht (kein Push beauftragt). |
| L5 | Sackgasse ohne Spielordner nicht gebaut | **gehoben** seit T-217/T-230: Pfaddialog + Steam-Herkunftspruefung (A15) sind im Artefakt, von `clean-room` bestaetigt (Erststart fand den Ordner automatisch ueber die Steam-Registry). |
| L6 | Keine Signatur → SmartScreen | **unveraendert offen, Nutzerentscheid.** Kein Zertifikat vorgesehen; jeder Erststart zeigt SmartScreen. Liegt bei A-Designer/Nutzer, nicht bei mir. |
| L7 | Bau nicht bit-identisch | **unveraendert**, dokumentierte Ursache (PE-Baustempel, Modulreihenfolge), erneut beobachtet zwischen den drei T-241c-Rebuilds. |
| L8 | `release.yml` faehrt keine Tests | **unveraendert offen** (A-008, weiterhin `offen` in `AUFLAGEN.md`). |

Neu gegenueber der 1.8.0-Liste, aus diesem Bau-Lauf: `.venv` fehlte auf dem
Bau-Rechner vollstaendig (T-241c-Bericht, "Befund: `.venv` fehlte
vollstaendig") — kein Repo-Fehler (`.venv/` korrekt in `.gitignore`), aber
ein Hinweis, dass ein dritter Rechner ohne vorbereitetes `.venv` und ohne
passenden System-Python am selben Punkt scheitert. Fuer diesen Lauf ohne
Folgen, da `.venv` neu angelegt und mit den gepinnten Versionen befuellt
wurde.

### Migration 1.9.0 → 1.10.0

Geprueft (nicht vermutet): `git diff 0716911..1b36238 -- nrplanner nrdata`
zeigt `nrplanner/favourites.py`, `nrplanner/paths.py` und
`nrdata/extract.py` **nicht** in der Liste der geaenderten Dateien — weder
`EXTRACT_VERSION` (unveraendert `11`, Datenabzug-Testvorlage in `CLAUDE.md`
bleibt gueltig) noch das Registrierschema fuer Favoriten/Builds haben sich
zwischen 1.9.0 und 1.10.0 geaendert. `clean-room` (T-241d) bestaetigt das am
Artefakt indirekt: `__schema=3` beim Speichern eines Builds, derselbe Wert,
den T-174 fuer 1.9.0 dokumentiert. **Es gibt keine Schemaaenderung, also
keine Migrationslogik noetig** — bestehende Registry-Eintraege und der
Datenabzug eines 1.9.0-Nutzers werden von 1.10.0 unveraendert weitergelesen.
Einzige offene Frage ist L2: dieser Satz ist aus dem Quelldiff und dem
`__schema`-Wert abgeleitet, **nicht** an einem tatsaechlichen
1.9.0→1.10.0-Update-Lauf verifiziert, weil kein 1.9.0-Artefakt mehr existiert.

### Ergebnis fuer den heutigen Zweck (Ingame-Test des Nutzers, keine Weitergabe)

Kein Blocker. L2 (Update-Pfad) und L6 (Signatur) sind benannte
Einschraenkungen, keine Sperren fuer den heutigen Eigenlauf — beide werden
erst bei einer echten Weitergabe/einem Release relevant (dann zusaetzlich
A-020/A-023/A-031 aus `AUFLAGEN.md`, dort bereits gefuehrt).

---

## 1.13.2 — 2026-09-17, T-290, Modus `notes`

Stand `c537c8b`. `AUFLAGEN.md` gelesen (Stand T-283c/1.13.1, GELB): keine
Auflage steht auf ROT, keine sperrt diesen `notes`-Lauf. Kein Build, kein
Release, keine Weitergabe in diesem Lauf.

### Migration

Keine. Der Aenderung (`bc4443e`, `1be0d9e`, AK-314) liegt kein neuer
`QSettings`-Schluessel, kein Schema und kein Ablageort zugrunde — nur eine
zusaetzliche Textzeile im Vorschlag und im Why-Dialog, aus bestehenden Daten
berechnet. `986216d` (Hook-Fix) beruehrt kein Nutzerdatenformat.

### Ergebnis

Kein Blocker fuer diesen Lauf. Fuer eine Weitergabe gilt dieselbe Liste wie
im 1.13.1-Abschnitt unten (A-008/A-020/A-023/A-030/A-031/A-033/A-035).

---

## 1.13.1 — 2026-09-16, T-285c, Modus `notes`

Stand `cdf4f50`. Artefakt (T-282) `dist/NightreignHelper.exe`,
59.201.630 B, SHA-256
`71E8202980BA528119815C75818757668EA956480A918C0236D1C8E420E67E1C`.
`AUFLAGEN.md` gegen Stand 16.09. gelesen: **keine Auflage steht auf ROT**;
Gesamtampel des letzten Auflagenlaufs (T-283c, `1f51485`) ist GELB und
sperrt weder diesen `notes`-Lauf noch den Bau. Kein Release, kein Push,
keine Weitergabe in diesem Lauf (Auftrag: nur `notes`).

### Migration von 1.7.1 (letztes oeffentliche Release, `gh release list`) bis 1.13.1

1.13.1 ist das 13. Release; das zwoelfte und bislang letzte oeffentliche war
`v1.7.1` (24.08.2026). Ein Nutzer, der seit `v1.7.1` nicht aktualisiert hat,
ueberspringt beim Update auf 1.13.1 alle Zwischenversionen auf einmal. Drei
Speicherorte geprueft, Quelle je `git show <tag>:<pfad>` gegen den heutigen
Stand:

| Ort | Bei 1.7.1 | Bei 1.13.1 | Wirkung beim ersten Start |
|---|---|---|---|
| `QSettings`-Organisation/Schluessel (`nrplanner/favourites.py:25`, `paths.py:15`) | `ORG = "DankYeeter"`, `APP_NAME = "NightreignHelper"` | **unveraendert** (Diff `v1.7.1..HEAD` auf beide Dateien: nur eine neue Hilfsfunktion `favourites.parts()` fuer Custom-Relikte hinzugekommen, kein Format- oder Ortswechsel) | Bestehende Favoriten, Fenstergroesse und UI-Skalierung werden unveraendert weitergelesen |
| Gefaess-/Build-Store (`nrplanner/chalices.py`) | **kein Schema** (`SCHEMA_KEY`/`CURRENT_SCHEMA` existieren in `v1.7.1` nicht; Schluessel = Klartextname) | `CURRENT_SCHEMA = CASE_SAFE_KEYS = "3"`; Schluessel URL-kodiert, Vergleich case-gefaltet; Feldformat um ein optionales Suffix `TWO_HANDED = "2H"` erweitert (`_encode`/`_decode`, Z. 458-479) | Erster Zugriff auf einen Helden migriert dessen Schluessel automatisch (`_migrate_keys`, Fundstelle bereits im 1.10.0-Abschnitt oben verifiziert: gleicher Mechanismus, unveraendert seit 1.11.0). Ein 1.7.1-Build ohne `2H`-Suffix decodiert **einhaendig** (`_decode` Z. 477: `two_handed = parts[-1] == TWO_HANDED`, sonst `False`) — der Build erscheint nach dem Update als einhaendig gesetzt, nicht als beschaedigt. **Am Code verifiziert, nicht an einem echten Schema-losen 1.7.1-Datensatz** (kein 1.7.1-Artefakt mehr im Zugriff dieses Laufs) |
| Datenabzug-Cache (`nrdata/extract.py:84`, `%LOCALAPPDATA%\NightreignHelper`) | `EXTRACT_VERSION = 8` | `EXTRACT_VERSION = 12` | Der Vergleich laeuft automatisch beim Start (`nrplanner/firstrun.py`, `datasource.py`, unveraendert seit dem 1.10.0-Abschnitt oben); die gespeicherte Version im Snapshot (8) weicht von der aktuellen (12) ab, der Cache wird verworfen und neu gebaut — rund eine Minute mit Fortschrittsanzeige, wie beim Ersteinrichten. Kein Datenverlust, nur Wartezeit |

**Was ein 1.7.1-Nutzer beim ersten Start von 1.13.1 erlebt, zusammengefasst:**
SmartScreen wie gehabt, dann einmalig rund eine Minute Neuextraktion des
Datenabzugs (EXTRACT_VERSION-Sprung), danach ein Fenster mit allen
bestehenden Kelchen/Builds — automatisch auf das neue Schluesselformat
umgeraeumt und, sofern ohne `2H`-Suffix gespeichert, auf einhaendig gesetzt.
Favoriten, Fenstergroesse und die neuen Effektmarkierungen (Favourite/Avoid,
seit 1.11.0/1.13.0 im eigenen Filters-Fenster) sind ohne Migrationsschritt
vorhanden, weil ihr `QSettings`-Schlussel sich nie geaendert hat. **Kein
Datenverlust in der Kette; die einzige nicht an einem echten 1.7.1-Artefakt
gepruefte Stelle ist die Schema-lose→Schema-3-Migration selbst** (deckt sich
mit L2 aus dem 1.8.0-Abschnitt, dort erstmals benannt).

### Ergebnis

Kein Blocker fuer diesen Lauf. Fuer eine Weitergabe: A-008/A-020/A-023/A-030/
A-031/A-033/A-035 aus `AUFLAGEN.md` (T-283c, GELB) — A-023 verlangt, dass der
`release-manager` Variante A aus `docs/release/RELEASE_BODY.md` von Hand an
den Anfang der Release-Beschreibung setzt, `generate_release_notes` tut das
nicht. **Ungeprueft:** ein echter `clean-room`-Update-Lauf 1.7.1 → 1.13.1 an
gebauten Artefakten (kein 1.7.1-Artefakt mehr lokal vorhanden; laeuft laut
Auftrag parallel beim `power-user`/`clean-room`).

---

## 1.12.3 — 2026-09-15, Modus `notes`

Stand `4b65523`, Code-Commit `2907a66`. Artefakt `dist/NightreignHelper.exe`,
59.123.168 B, SHA-256
`1c8b4ff52286928b7fc795cc65597bf7f0a65ed40c987c7fe63d0e9e2bb4dc88`.
`AUFLAGEN.md` gegen Stand 15.09. gelesen: keine Auflage steht auf ROT, keine
sperrt diesen Lauf (offene GELB-Punkte betreffen Screenshots und README-
Quellenangabe, nicht diesen Auftrag). Kein Release, kein Push, keine
Weitergabe in diesem Lauf (Auftrag: nur `notes`).

### Migration 1.12.2 → 1.12.3

Reiner Fix, kein Schema. `git diff fb23e24..2907a66 -- nrplanner/favourites.py
nrplanner/paths.py nrplanner/chalices.py nrdata/extract.py` zeigt keine
Aenderung; `EXTRACT_VERSION` bleibt 12. Keine Migration noetig.

### Ergebnis

Kein Blocker. Fuer eine Weitergabe gilt weiterhin A-020/A-023 aus
`AUFLAGEN.md`.

---

## 1.12.2 — 2026-09-15, Modus `notes`

Stand `d2a1598`, Code-Commit `fb23e24`. Artefakt `dist/NightreignHelper.exe`,
59.120.312 B, SHA-256
`7279528507491809616beab5f498ce4d03153c907d8d18c54f92bb4fed67abcf`.
`AUFLAGEN.md` gegen Stand 15.09. gelesen: keine Auflage steht auf ROT, keine
sperrt diesen Lauf. Kein Release, kein Push, keine Weitergabe in diesem Lauf
(Auftrag: nur `notes`).

### Migration 1.12.1 → 1.12.2

Geprueft: `git diff 3c2ff23..fb23e24 -- nrplanner/favourites.py
nrplanner/paths.py nrplanner/chalices.py` zeigt keine Aenderung — Ablageort
und Schema unveraendert. Migration liegt stattdessen im Datenextrakt:
`EXTRACT_VERSION` 11 → 12 (`nrdata/extract.py:84`, neues Feld `paired` aus
`isDualBlade`). Der Vergleich laeuft automatisch beim Start
(`nrplanner/firstrun.py:75`, `nrplanner/datasource.py:106`): stimmt die
gespeicherte `extract_version` im Snapshot nicht mit der aktuellen ueberein,
wird der Cache verworfen und neu gebaut, ohne Nutzerhandlung. Am Quelltext
bestaetigt, nicht an einem echten 1.12.1→1.12.2-Update-Lauf (kein
`clean-room` in diesem Auftrag). Builds und Effektmarkierungen (`QSettings`)
bleiben unberuehrt, dieselbe Schlussfolgerung wie in den Abschnitten 1.12.0
und 1.12.1.

### Ergebnis

Kein Blocker. Fuer eine Weitergabe gilt weiterhin A-020/A-023 aus
`AUFLAGEN.md`; A-031 entfaellt laut T-265 (keine UPX-Sektionen im Artefakt).
Ungeprueft: der EXTRACT_VERSION-11→12-Uebergang an einem echten Artefakt
(kein 1.12.1-Cache-Beispiel in diesem Lauf verwendet).

---

## 1.12.1 — 2026-09-15, Modus `notes`

Stand `6533449`, Code-Commit `3c2ff23`. Artefakt `dist/NightreignHelper.exe`,
59.119.378 B, SHA-256
`f29eb92d88ed14416a488f32f7ab655bf27fec77e2be74105782d0980904cf1b`
(Build-Commit `6533449`, T-268). `AUFLAGEN.md` gegen Stand 15.09. gelesen:
keine Auflage steht auf ROT, keine sperrt diesen Lauf. Kein Release, kein
Push, keine Weitergabe in diesem Lauf (Auftrag: nur `notes`).

### Migration 1.12.0 → 1.12.1

Geprueft: `git diff 02e0721..3c2ff23 -- nrplanner/favourites.py
nrplanner/paths.py nrplanner/chalices.py nrdata/extract.py` zeigt keine
Aenderung. Reiner Fix (AK-297/AK-298, QA-272, SEC-046/047) ohne Schema- oder
Ablageortaenderung — keine Migrationslogik noetig, kein Update-Test gegen
1.12.0 fuer diesen Lauf erforderlich.

### Ergebnis

Kein Blocker. Fuer eine Weitergabe gilt weiterhin A-020/A-023/A-031 aus
`AUFLAGEN.md`; A-031 entfaellt laut T-265 (keine UPX-Sektionen im Artefakt).

---

## 1.12.0 — 2026-09-15, Modus `notes`

Stand `02e0721`. Artefakt-Nachweis aus T-265 (`release-manager`, Modus
`clean-room`): `dist/NightreignHelper.exe`, 59.118.289 B, SHA-256
`89c2967acaaaac8ca108935cac0a79c8292d2c7ec0e77831755a15b295f59d8`.

### Migration 1.11.0 → 1.12.0

**Clean-room bestanden**, nicht nur am Diff geprueft:
`docs/berichte/T-265-release-manager-cleanroom.md`. 1.11.0 installiert, vier
Builds mit Sonderzeichen im Namen sowie eine Effektmarkierung gespeichert,
1.12.0 darueber kopiert und gestartet — alle vier Builds (Registry und
UI-Combo), `__schema=3` und die Effektmarkierung unveraendert vorhanden;
Zweitstart nach vollstaendigem Prozessende bestand ebenfalls. Einschraenkung
laut demselben Bericht: die 1H-Voreinstellung fuer Altbuilds ohne
`2H`-Suffix ist nur am Code (`chalices.py:459-479`), nicht an einem echten
Schema-2-Datensatz verifiziert — kein solches Artefakt mehr vorhanden. A-031
(UPX) entfaellt, das Artefakt enthaelt keine UPX-Sektionen.

### Ergebnis

Kein Blocker. Fuer eine Weitergabe von 1.12.0 gilt A-020/A-023 aus
`AUFLAGEN.md` (A-031 entfaellt).

---

## 1.11.0 — 2026-09-15, Modus `notes`

Stand `8b7b782` (Doku, ruehrt Code nicht an), Code `2a0ca0d`. Artefakt
`dist/NightreignHelper.exe`, 59.105.391 B, SHA-256
`f23eb0f784665a8c018c19f353ad114e9809061033076311dcdf21dbb916e8e0`
(certutil nachgemessen, deckt sich mit Direktors Messung und dem
Build-Commit `08ddba6` laut `d564205`). `AUFLAGEN.md` gegen Stand 15.09.
gelesen: keine Auflage steht auf ROT, keine sperrt diesen Lauf. Kein Release,
kein Push, keine Weitergabe in diesem Lauf (Auftrag: nur `notes`).

### Migration 1.10.1 → 1.11.0

Geprueft (nicht vermutet): `git diff dde2efc..08ddba6 -- nrplanner/favourites.py nrplanner/paths.py`
zeigt **keine** Aenderung an beiden Dateien. Neu ist `nrplanner/effectfilters.py`
(neue Datei) mit zwei zusaetzlichen `QSettings`-Schluesseln
(`advisor/excluded`, `advisor/required`); der Docstring der Datei haelt fest:
"No `__schema` step either -- a store that never held the key reads back as
empty". Das ist am Quelltext bestaetigt, nicht an einem echten
1.10.1→1.11.0-Update-Lauf verifiziert (kein `clean-room` in diesem Auftrag) —
gleiche Einschraenkung wie L2 aus dem 1.10.0-Abschnitt. Ein 1.10.1-Artefakt
existiert (`5e19a02`, 59.089.432 B, SHA-256 `dfdeadc4…6a558` laut
Build-Commit), waere also fuer einen echten Update-Test vorhanden.

### Gegenueber 1.10.0-Abschnitt unveraendert offen

L2 (Update-Pfad nie an einem echten Artefakt geprueft) und L6 (keine Signatur,
SmartScreen) gelten unveraendert; L2 ist mit dem vorhandenen 1.10.1-Artefakt
diesmal technisch pruefbar, aber in diesem `notes`-Lauf nicht geprueft.

### Ergebnis

Kein Blocker fuer diesen Lauf. Fuer eine Weitergabe von 1.11.0 gilt dieselbe
Liste wie bei 1.10.0 (A-020/A-023/A-031 aus `AUFLAGEN.md`) plus ein
`clean-room`-Update-Test 1.10.1 → 1.11.0, bisher ungeprueft.

---

## 1.14.0 — 2026-09-19, T-295d, Modus `notes`

Stand `44a524e`. Artefakt (T-295b) `dist/NightreignHelper.exe`,
59.141.726 Byte, SHA-256
`A45BDF1151C28D2ED0F43B8797F4E27F4C8F7BD114A30BF186A954C3692CEA9C`,
Code-Stand `099459b` (AK-317-Nachtrag "Allow immer klickbar"). `AUFLAGEN.md`
gelesen (Stand 19.09., letzter Auflagenlauf T-283c/1.13.1 GELB, kein
Nachtrag mit ROT seither): keine Auflage sperrt diesen `notes`-Lauf. Kein
Release, kein Push, keine Weitergabe in diesem Lauf.

### Migration

Zwei neue `QSettings`-Schluessel, `advisor/allowed` und
`advisor/avoided_families` (AD-039.4), neben den zwei bestehenden aus
1.11.0 (`advisor/excluded`, `advisor/required`). Kein `__schema`-Schritt,
kein neuer Ablageort: der Docstring von `nrplanner/effectfilters.py`
(AD-039) haelt fest, dass ein Speicher, der einen Schluessel nie hielt, ihn
leer zurueckgibt — genau das, was ein aelterer Programmzustand meint. Der
Datenstand aus 1.13.x (Builds, Favourite/Avoid, die beiden bestehenden
Schluessel) laeuft unter 1.14.0 unveraendert weiter; kein Update-Skript
noetig. Nicht an einem echten Update-Lauf geprueft (kein `clean-room` in
diesem Auftrag) — Annahme am Quelltext, wie bei den fruehreren
`notes`-Laeufen dieses Projekts ueblich.

### Ergebnis

Kein Blocker fuer diesen Lauf. Fuer eine Weitergabe gilt dieselbe Liste wie
im 1.13.2-Abschnitt oben (A-008/A-020/A-023/A-030/A-031/A-033/A-035).

---

## 1.15.0 — 2026-09-19, T-328c, Modus `notes`

Stand `6edab2e` (Code-Stand, Bau T-313b). Lokal gebautes Pruef-Artefakt
`dist/NightreignHelper.exe`: 59.151.716 Byte, SHA-256
`1D4197DF0F0C765B507CCA824FBA480DBCFCA76C482CF3F7A852B199CB6BBDF0`
(`docs/berichte/T-313-release-manager.md`; QA T-313c und Sicherheit T-312b
liefen gegen diesen bzw. den Vorlauf-Stand). Das tatsaechlich ausgelieferte
Release-Artefakt (CI-Bau ueber `release.yml`) weicht davon ab — wie bei
jedem bisherigen Release in diesem Projekt (anderer Bau-Wirt): 59.232.620
Byte, SHA-256
`59D0D4308460CD6DC6F5D9E3156A1575E40FE68CD9695719CF514C4FD0E1CCDE`
(nachgemessen in T-322l per `gh release download v1.15.0`). Tag `v1.15.0`
auf `c536daa`, Run 35451242996, 3 Assets (`docs/state.md`, Tabelle
"Veroeffentlicht"). `AUFLAGEN.md` gelesen (juengster Abschnitt zum Zeitpunkt
dieses Laufs: "Stand 1.18.0", T-328b, 21.09.2026 — keine Auflage auf ROT).
Kein Release, kein Push, keine Weitergabe in diesem `notes`-Lauf.

### Migration

`nrdata/extract.py`: `EXTRACT_VERSION` 12 auf Stand `v1.14.0` (gemessen per
`git show v1.14.0:nrdata/extract.py`) auf 15 auf Stand `v1.15.0` — neue
Unterboss-, Beute- und Ortsdaten (A24). Erster Start nach dem Update baut
den Cache einmalig neu (CHANGELOG nennt rund 35 s); keine QSettings- oder
Registry-Aenderung, keine Nutzerdaten (Relikte, Builds) betroffen — die
liegen unveraendert in der Registry, nicht im Cache.

**Ungeprueft:** der reale Update-Lauf 1.14.0 → 1.15.0 selbst. Fuer diesen
Uebergang existiert in `docs/berichte/` kein `clean-room`-Bericht (nur die
drei Dateien `T-285-`, `T-322-` und `T-325-release-manager-clean-room.md`);
die release-manager-Laeufe T-312a/T-313b waren Rauchtests mit vorab
kopiertem, bereits aktuellem Testabzug, kein Versionswechsel. Die beiden
folgenden Uebergaenge (1.15→1.16, 1.16→1.17) sind clean-room-geprueft,
dieser nicht.

### Ergebnis

Kein Blocker fuer diesen Lauf. Fuer eine erneute Weitergabe gilt dieselbe
Auflagenliste wie in den vorherigen Abschnitten
(A-008/A-020/A-023/A-030/A-031/A-033/A-035); der Update-Pfad 1.14.0→1.15.0
bleibt ungeprueft (oben).

---

## 1.16.0 — 2026-09-20, T-328c, Modus `notes`

Stand `a33e92b` (Tag, Run 35518272445, 3 Assets, `docs/state.md`). Artefakt
laut Kontraktblock des clean-room-Laufs T-322l: 59.233.161 Byte, SHA-256
`51F694986D11CA1DED16B6170D552C89579C0E5C67192D78F68FFFF063E8BFC9`.
`AUFLAGEN.md` gelesen wie im Abschnitt zuvor (Stand "1.18.0", T-328b,
21.09.2026 — keine Auflage auf ROT). Kein Release, kein Push, keine
Weitergabe in diesem `notes`-Lauf.

### Migration

Kein `EXTRACT_VERSION`-Sprung: die Schadensart-Auswahl ist reine
Berater-/UI-Logik, kein neuer Extraktionsschritt. Neuer QSettings-Schluessel
`damage_art` speichert die gewaehlte Schadensart; ein Speicher ohne diesen
Schluessel (jeder Stand vor 1.16.0) liest ihn leer und faellt auf "All"
zurueck (CHANGELOG-Note, am Quelltext plausibilisiert).

**Clean-room belegt** (`docs/berichte/T-322-release-manager-clean-room.md`):
echter Uebergang 1.15.0 → 1.16.0 aus dem GitHub-Release geladen und
installiert, vier Testbuilds mit Sonderzeichen im Namen (`Name/WithSlash`,
`Name|WithPipe`, `UPPERCASE`) ueberstanden das Update unveraendert
(Registry-Beleg: `__schema`, `__order`, `__selected` intakt), Zweitstart
nach Prozessende bestanden, Aufraeumen vollstaendig. Urteil des Laufs:
freigeben.

### Ergebnis

Kein Blocker. Update-Pfad 1.15.0→1.16.0 ist der erste in diesem Viererblock,
der tatsaechlich an einem echten Artefakt clean-room-geprueft wurde (nicht
nur am Quelltext plausibilisiert wie im Abschnitt zuvor).

---

## 1.17.0 — 2026-09-21, T-328c, Modus `notes`

Stand `fc57b93` (Quell-Commit des Artefakts laut T-325l), Tag `v1.17.0` auf
`28b7f1e` (Notes-Commit, gleiches Muster wie beim 1.15.0-Tag auf `c536daa`),
Run 35560029819, 3 Assets (`docs/state.md`). Artefakt laut Kontraktblock des
clean-room-Laufs T-325l: 59.250.281 Byte, SHA-256
`BFEEB0270D16C88FDEC67DF10F2D5C76FD29AB5002F6EEC2E14691F321E7C4B4`.
`AUFLAGEN.md` gelesen wie oben, keine Auflage auf ROT. Kein Release, kein
Push, keine Weitergabe in diesem `notes`-Lauf.

### Migration

`EXTRACT_VERSION` 15 → 16 (Zauberschaden, linke Starthand, Tauschzauber
werden neu gelesen).

**Clean-room belegt, echter Sprung, nicht nur behauptet**
(`docs/berichte/T-325-release-manager-clean-room.md`): Cache vor dem Update
`extract_version: 15` (8.803.996 Byte), nach **37,2 s** Neubau
(Prozessstart 22:25:10 → `nightreign_data.json` neu geschrieben 22:25:47)
`extract_version: 16` (8.811.742 Byte) — deckt sich mit dem in
`docs/tasks/T-328.md` genannten Wert ("clean-room T-325 37 s"). Vier
Testbuilds mit Sonderzeichen ueberstanden den Sprung unveraendert
(Registry-Beleg), Zweitstart nach Prozessende warm (3,4 s, kein zweiter
Neubau), Aufraeumen vollstaendig.

**Zusaetzlich, settingsseitiger Bruch ohne Datenverlust:** der bisherige
Schluessel `damage_art` (seit 1.16.0) wird ab 1.17.0 nicht mehr gelesen; die
neuen Schluessel `hit_with` und `damage_type` ersetzen ihn (CHANGELOG-Note).
Eine Aktualisierung von 1.16.0 startet also ohne die zuletzt gemerkte
Schadensart (Ruecksprung auf Weapon/All) statt mit dem alten Wert — kein
Datenverlust, da reine Bedienvorlieben betroffen sind, keine Relikte oder
Builds, aber ein bewusster Bruch der Kontinuitaet. **Ungeprueft:** der
clean-room-Bericht T-325l prueft diesen Schluesselwechsel nicht gezielt
(Fokus lag auf dem Cache-Sprung und den vier Builds mit Sonderzeichen) — ob
ein zuvor gesetzter `damage_art`-Wert sauber ignoriert wird oder ob das
Lesen scheitert, ist am echten Artefakt nicht belegt; aus Nutzersicht sind
beide Faelle als "Ruecksetzung auf Weapon/All" nicht unterscheidbar, solange
kein Fehlerdialog erscheint.

### Ergebnis

Kein Blocker. Die Cache-Migration ist clean-room-geprueft; der
Settings-Schluesselwechsel `damage_art` → `hit_with`/`damage_type` ist nur
am Quelltext (CHANGELOG-Note) belegt, nicht an einem echten Update-Lauf mit
zuvor gesetztem `damage_art`.

---

## 1.18.0 — 2026-09-21, T-328c, Modus `notes`

Stand `5a35272` (Code-Stand des Bau-Laufs T-327g), Tag `v1.18.0` auf
`1ae6952`, Run 35633098282, 3 Assets (`docs/state.md`). Artefakt laut
`docs/state.md` ("A27 abgeschlossen"): SHA-256-Anfang/-Ende `89DAACBB…DCCC`
— die volle Pruefsumme steht in keiner in diesem Lauf gelesenen Quelle
ausgeschrieben; **ungeprueft** in diesem Umfang. `AUFLAGEN.md` gelesen, keine
Auflage auf ROT. Kein Release, kein Push, keine Weitergabe in diesem
`notes`-Lauf.

### Migration

Kein `EXTRACT_VERSION`-Sprung: `v1.17.0` und `v1.18.0` stehen beide auf 16
(gemessen per `git show <tag>:nrdata/extract.py`). Keine neue
QSettings-Struktur — Weapon art und Spell damage sind reine Anzeigefelder
im Schadensblock, kein gespeicherter Auswahlzustand. Damit ist 1.18.0 die
einzige Version dieses Viererblocks ohne Datenmigrationsfrage.

**Ausdruecklich kein Update-Pfad geprueft:** `docs/state.md` haelt zu "A27
abgeschlossen" fest, dass die Release-Kette 1.18.0 **ohne clean-room und
ohne power-user** lief — Nutzerentscheid 21.09. 19:25 ("kurze Kette").
Gegengeprueft: `docs/berichte/` enthaelt keine Datei
`T-327-release-manager-clean-room.md` (nur die drei Dateien zu T-285, T-322,
T-325). Der Uebergang 1.17.0 → 1.18.0 — einschliesslich des im
1.17.0-Abschnitt offen gebliebenen Settings-Bruchs — ist damit **ungeprueft**,
nicht nur im Nebenpunkt.

### Ergebnis

Kein Blocker fuer diesen `notes`-Lauf selbst. Fuer die bereits erfolgte
Weitergabe von 1.18.0 gilt: der Update-Pfad von der Vorversion wurde vor der
Weitergabe nicht verifiziert — eine bewusste Nutzerentscheidung, hier nur
nachrichtlich festgehalten. Dieser `notes`-Auftrag (T-328c) schliesst Bau
und `clean-room` ausdruecklich aus; eine nachtraegliche Pruefung waere ein
eigener `clean-room`-Auftrag.
