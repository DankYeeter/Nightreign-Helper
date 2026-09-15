STATUS: erledigt
AUFTRAG: T-106 - Rollout-Plan und Releasefaehigkeit (release-manager, Modus `plan`)
GELESEN: ~/.claude/agents/_rahmen.md, docs/tasks/T-106.md, GOAL.md, docs/state.md, CLAUDE.md, NightreignHelper.spec, .github/workflows/release.yml, .github/workflows/tests.yml, requirements.txt, requirements-dev.txt, .gitignore, README.md, THIRD_PARTY.md, scripts/check_licences.py, nrplanner/__init__.py, nrplanner/datasource.py, nrplanner/paths.py, nrplanner/chalices.py, nrplanner/favourites.py, nrplanner/firstrun.py, nrplanner/singleinstance.py, nrplanner/app.py (Ausschnitte), security/findings.md (SEC-009, SEC-025), qa/findings.md (QA-195), docs/berichte/T-105-developer.md. `docs/release/ROLLOUT.md` und `CHANGELOG.md` existierten vor diesem Lauf nicht (Dateisystem und `git ls-files` einzeln geprueft).
GEÄNDERT: docs/release/ROLLOUT.md (neu, unversioniert), docs/berichte/T-106-release-manager.md (dieser Bericht). Kein Commit, kein Git-Zustand veraendert. Temporaer angelegt und wieder geloescht: zwei Probebauten unter <scratchpad>\T-106\{dist1,dist2,build1,build2}; dort liegen nur noch build1.log und build2.log.
ANNAHMEN: keine geraten. Der Auftrag war vollstaendig zitiert; **eine seiner Tatsachenangaben ist widerlegt** (siehe Blocker B0).
NÄCHSTER: director (Entscheidung ueber Versionsnummer und Reihenfolge), danach `release-manager` im Modus `build`
BLOCKIERT DURCH: nichts fuer diesen Lauf. Der `build`-Lauf ist blockiert durch die Versionsentscheidung (B1) — ein Bau mit `__version__ = "1.7.1"` erzeugt ein Artefakt mit der Nummer einer bereits ausgelieferten Datei.

---

# T-106 — Rollout-Plan und Releasefaehigkeit

**Modus:** `plan`. **Geprueft gegen:** Commit `006a604`, Branch
`docs/audit-and-advisor-design`, Arbeitsbaum sauber vor und nach dem Lauf (einzige fremde Datei:
`docs/legal/C-003.md` aus dem parallel laufenden T-104).

**Umgebung:** Windows 10 Home 19045 x64, Python 3.12.10, PyInstaller 6.21.0,
PySide6 6.11.1, kein `upx` im PATH. **Nicht isoliert:** dies ist der
Entwicklungsrechner mit `.venv`, gesetzten Pfaden, vorhandener
Spielinstallation, gefuelltem `%LOCALAPPDATA%\NightreignHelper` und gefuelltem
`HKCU\Software\DankYeeter`. Fuer den `plan`-Modus ist das in Ordnung; jede
Aussage ueber eine Fremdinstallation ist unten als **ungeprueft** markiert.

**Ergebnis: `docs/release/ROLLOUT.md`**, Abschnitt
`## 1.8.0 (vorgeschlagen, nicht entschieden) — 2026-09-07`.

## Urteil zur Releasefaehigkeit

**FAIL fuer ein Release heute** — bei gleichzeitig **gruenem Bauweg**. Das
Artefakt laesst sich heute bauen (gemessen, zweimal). Ein *Release* kann heute
nicht herausgehen, und zwar nicht aus Vorsicht, sondern weil der Workflow es
mechanisch verweigern wuerde.

Was das Urteil hebt, je Punkt: **B1** Versionsbump entschieden und gesetzt ·
**B2** Update-Weg ueber 1.7.1 an einem Artefakt geprueft · **B3** `CHANGELOG.md`
mit dem Migrationssatz · **B4** Stand am Remote. Danach: **freigeben mit
benannten Einschraenkungen** (R1-R6 unten).

## Ergebnis je Schritt

| Schritt | Ergebnis |
|---|---|
| Werkzeugkette vollstaendig | **bestanden** — PyInstaller 6.21.0, alle sieben Laufzeit-Abhaengigkeiten in der `.venv`, nichts fehlt |
| Probebau 1 | **bestanden** — `rc=0`, 61 s, 59.010.324 B |
| Probebau 2 | **bestanden** — `rc=0`, 58 s, 59.011.279 B |
| Bau bit-identisch wiederholbar | **fehlgeschlagen** — zwei verschiedene SHA-256, Δ 955 B (Ursache eingegrenzt, siehe Artefakt) |
| Bauwarnungen erklaerbar | **bestanden** — keine `ERROR`-Zeile; `warn`-Datei nur mit optionalen Stdlib-Importen (37 Zeilen) |
| Keine Spieldaten im Bundle | **bestanden** — nur `data\icon.ico` + 236 Paramdef-XML; `icon.png` liegt daneben und ist **nicht** im Bundle |
| Versionsressource der EXE | **bestanden** — FileVersion/ProductVersion 1.7.1, aus `nrplanner/__init__.py` gelesen |
| Laufzeit-Voraussetzungen auf dem Ziel | **bestanden** — `VCRUNTIME140(.._1).dll` und `api-ms-win-*` im Bundle, kein Redistributable noetig |
| `.gitignore` deckt Bauausgabe | **bestanden** — `build/`, `dist/` enthalten; nichts vorzuschlagen |
| Start des Artefakts | **nicht pruefbar in diesem Modus** — ein Start haette in `HKCU\Software\DankYeeter` und `%LOCALAPPDATA%` des Nutzers geschrieben. Gehoert in `build`/`clean-room` mit gesetztem `NIGHTREIGN_SETTINGS_ORG` und umgelenktem `LOCALAPPDATA` |
| Update ueber 1.7.1 | **nicht geprueft** — Modus `plan`, kein Start. Vorgehen im ROLLOUT festgelegt |
| Fremdinstallation, Virenscanner, SmartScreen | **nicht pruefbar** — keine zweite Maschine, kein zweites Konto |

## Artefakt

Zwei Probebauten, **beide geloescht**. Pfad war
`<scratchpad>\T-106\dist1\NightreignHelper.exe` bzw. `\dist2\`. Gebaut mit
`.venv\Scripts\pyinstaller.exe NightreignHelper.spec --noconfirm --distpath …
--workpath …` aus der Repo-Wurzel; `dist/` und `build/` im Repository wurden
**nicht** angelegt. **Reproduzierbar: nein** (Inhalt gleich, Verpackung nicht:
`PYZ-00.pyz` byte-identisch, `PKG-00.toc` nach Normalisierung identisch, erste
Abweichung Byte 273 im PE-Kopf, instabile Modulreihenfolge in
`Analysis-00.toc`).

## Blocker

**B0 — Die Aktenlage ist falsch, und sie traegt den ganzen Zyklus.**
`docs/state.md` und T-106 sagen, es habe **nie** ein gebautes Artefakt gegeben,
„weder lokal noch ueber die Releases-Seite". Gemessen: **12 Releases, 12 von 12
mit `NightreignHelper.exe` als Asset, 25 Downloads insgesamt, juengstes
`v1.7.1` vom 2026-08-24 (58.827.005 B, 2 Downloads)**, lokal 12 Tags `v1.0.0`
bis `v1.7.1`. Daraus folgt die Umkehrung der Zyklusplanung: **nicht die
Erstinstallation ist der Risikoweg, sondern das Update ueber eine vorhandene
Installationsbasis.** Zustaendig: `director` (Korrektur in `docs/state.md`).

**B1 — Ohne Versionsbump geht kein Release heraus.** `__version__ = "1.7.1"`,
und `v1.7.1` ist veroeffentlicht. Ein erneutes `v1.7.1` ist nicht taggbar; ein
`v1.8.0` laesst den Workflow-Schritt „Tag must match the version in the source"
**fehlschlagen**. Zustaendig: `director` (Nummer, Vorschlag **1.8.0**),
`developer` (die Zeile — sie liegt unter `nrplanner/`, also nicht bei mir).

**B2 — Der Update-Weg ist ungeprueft, und er fasst die Arbeit des Spielers an.**
Zwischen `v1.7.1` und heute: `EXTRACT_VERSION` **8 → 11** (erzwingt einen
Neuaufbau des Datenabzugs, ~1 Minute) und der Schluesselraum der gespeicherten
Builds wandert vom **unmarkierten Namenszustand** (`v1.7.1` kennt `SCHEMA_KEY`
nicht) auf **Schema 3**. Der Migrationscode ist sorgfaeltig gebaut und von der
Suite gedeckt, aber **nie gegen ein Artefakt gelaufen**. Zustaendig:
`release-manager` (`clean-room`).

**B3 — `CHANGELOG.md` existiert nicht**, bei 353 Commits seit `v1.7.1`.
Zustaendig: `release-manager` (`notes`).

**B4 — Der Stand ist nicht am Remote.** 9 lokale Commits ungepusht, PR #16
offen, `origin/main` 351 Commits zurueck, `main` geschuetzt. Ein tag-getriebenes
Release baut aus dem getaggten Commit. Zustaendig: `archivist` (Push) und
**Nutzer** (Merge).

## Risiken (verhindern kein Release, treffen aber Nutzer)

- **R1 SmartScreen** bei jedem Nutzer: die EXE ist unsigniert.
- **R2 Virenscanner-Fehlalarm**, bekanntes Risiko der PyInstaller-Einzeldatei;
  hier nicht gemessen.
- **R3 Der Erststart ohne gefundenes Spiel ist eine Sackgasse** (A15
  spezifiziert, nicht gebaut) — `app.py:4396-4400` beendet mit
  `QMessageBox.critical` und `return 1`.
- **R4 Kein reproduzierbarer Bau** → die mitgelieferte SHA-256 belegt die
  ausgelieferte Datei, nicht den Quellstand. Muss so in der Release-Notiz
  stehen, sonst liest sich eine abweichende Nachrechnung als Manipulation.
- **R5 `release.yml` faehrt keine Tests.** Ein Tag baut und veroeffentlicht,
  ohne dass die Suite gelaufen ist.
- **R6 Kein Deinstallierer, kein Downgrade.** Nach der Migration sieht 1.7.1
  die Builds unter abgeleiteten Schluesseln. Der `notes`-Lauf sollte
  `reg export "HKCU\Software\DankYeeter" nightreign-backup.reg` **vor** dem
  Update empfehlen.
- **R7 UPX:** der `.spec` setzt `upx=True`; hier ist kein UPX vorhanden, auf
  einem Rechner mit UPX entsteht eine andere Datei.

## Ungeprueft

Windows 11 · Windows ARM64 · echte Fremdmaschine, fremdes Nutzerkonto ·
Verhalten unter einem aktiven Virenscanner · SmartScreen-Dialog im Original ·
Start des Artefakts ueberhaupt · Update-Weg 1.7.1 → neu · Deinstallation und
Rueckstaende · Linux/macOS (Nicht-Ziel) · der Pruefsummenschritt unter
**`pwsh`** (PowerShell 7 ist auf diesem Rechner nicht installiert; die Luecke
stammt aus T-105 und besteht unveraendert — sie faellt beim ersten echten
Release auf).

## An `developer`

1. **`nrplanner/__init__.py` traegt eine bereits ausgelieferte Nummer**
   (1.7.1). Nach dem Entscheid des `director` die Zeile hochziehen; ich fasse
   Quellverzeichnisse nicht an.
2. **Kein Waechter haelt den `.spec` an seiner Grenze fest.** Dass keine
   Spieldaten ins Bundle geraten, folgt heute allein daraus, dass `datas` sie
   nicht auflistet — der Workflow-Schritt „Refuse to ship game data" prueft den
   **Baum** und laeuft ausserdem *nach* dem Bau. Ein Test in der Art des
   bestehenden „pytest stays out of requirements" waere die Stelle. Vorschlag,
   kein Auftrag; Reihenfolge gehoert dem `director`.
3. Kein Fehler im Anwendungscode gefunden, der den Bau verhindert.

## An `power-user`

Es liegt **kein** Artefakt bereit — meine beiden Probebauten sind geloescht,
damit der `build`-Lauf nichts vorfindet, was er fuer seins halten koennte.
Dein Ausgangspunkt entsteht dort und wird dort mit Pfad genannt.
Vorbereitung fuer deine Sitzung steht in `docs/release/ROLLOUT.md` (Abschnitt 5
und „Ablaufplan fuer den `clean-room`-Lauf"): SmartScreen, ~1 Minute
Erststart, die Sackgasse aus R3 — und **setz `NIGHTREIGN_SETTINGS_ORG` und ein
umgelenktes `LOCALAPPDATA`**, sonst schreibt deine Sitzung in die echten Builds
des Nutzers (QA-195).

## An `director`

- **Empfehlung: nicht freigeben (heute).** Nach B1-B4: freigeben mit den
  benannten Einschraenkungen R1-R7.
- **`docs/state.md` korrigieren:** „nie ein gebautes Artefakt" ist widerlegt
  (B0). Das ist die Praemisse, auf der Zyklus 16 aufgebaut wurde.
- **Entscheidung noetig: Versionsnummer.** Vorschlag **1.8.0** nach der Regel,
  die im Quelltext selbst steht (mittlere Stelle bei neuer Funktion; der
  Build-Berater ist eine).
- **Tag-Vorschlag, nicht gesetzt:** `v1.8.0` auf den Merge-Commit von PR #16
  auf `main`, **erst nachdem** die Versionszeile 1.8.0 sagt und der
  `clean-room` den Update-Weg bestaetigt hat. Begruendung: der Workflow baut
  aus dem getaggten Commit, und `main` ist der einzige Stand, den ein Nutzer je
  sieht. Ich setze und veroeffentliche nichts.
- **Offene Entscheidungen:** (a) wird ARM64 zugesagt? (b) soll `release.yml`
  die Suite fahren (R5)? (c) wird 1.8.0 mit offenem A15 ausgeliefert (R3)?
  (d) `security/findings.md` Zeile 19 fuehrt SEC-009 in der Tabelle noch als
  „offen", waehrend Zeile 424 ff. es als behoben und gegengeprueft ausweist —
  eine der beiden Stellen ist alt.
- **Keine fehlenden `.gitignore`-Eintraege.** `build/` und `dist/` sind
  gefuehrt.
- Nicht committet: `docs/release/ROLLOUT.md` und dieser Bericht liegen
  unversioniert im Baum.
