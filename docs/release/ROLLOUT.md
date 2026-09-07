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
4. Zweitstart nach Neustart der Umgebung. Die Einzelinstanz-Sperre haengt an
   einem maschinenweiten `QSharedMemory`-Schluessel
   (`nrplanner/singleinstance.py:32`): eine noch laufende Entwicklungsfassung
   faengt den Start ab, und der Test misst nichts.
5. Aufraeumen: Verzeichnis, Wegwerf-`LOCALAPPDATA`, Test-Organisation in der
   Registry, etwaige Verknuepfung. Was liegen bleibt, kommt in den Bericht.

### An den `power-user` (Ausgangspunkt seiner Sitzung)

Es gibt heute **kein** abgelegtes Artefakt — die beiden Probebauten sind
geloescht. Sein Ausgangspunkt entsteht im `build`-Lauf und wird dort mit Pfad
genannt. Vorwarnung fuer seine Sitzung: SmartScreen-Dialog, rund eine Minute
Erststart, und die Sackgasse aus L5, falls die Automatik das Spiel nicht
findet.
