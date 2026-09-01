# Sicherheitsbefunde

Quelle: T-003, `security-reviewer`, Zyklus 1.
Repo-Stand bei der Pruefung: `3da8428` (v1.7.1).
Status je Befund: offen | behoben | zurueckgestellt | entkraeftet

## Log

| ID | Titel | Prioritaet | Status | Letzte Pruefung |
|---|---|---|---|---|
| SEC-001 | Endlosschleife beim Lesen UTF-16-terminierter Namen (`savefile.py:55`, `binary.py:77`, `tpf.py:50`, `fmg.py:42`) | Hoch | offen | 2026-09-01 |
| SEC-002 | Unbegrenzte Zaehler aus der Datei steuern Schleifen und Allokationen (`savefile.py:38`, `bnd4.py:104`, `fmg.py:32`, `dvdbnd.py:42`, `tae.py:76`) | Mittel | offen | 2026-09-01 |
| SEC-003 | *(vergeben, im Audit entkraeftet: Parser-Abstuerze werden von den Aufrufern gefangen. ID bleibt gesperrt, damit Verweise eindeutig bleiben.)* | — | entkraeftet | 2026-09-01 |
| SEC-004 | Save- und Spieldaten-Strings ungefiltert in Qt-Rich-Text, `QLabel` auf `AutoText` (`app.py:1207/2665`, `inventory.py:189`) | Hoch | offen | 2026-09-01 |
| SEC-005 | Nativer Texturdecoder erhaelt ungeprueftes Format und zu kurze Nutzlast (`dds.py:25-57`) — **bestaetigt**, das Paket prueft nicht (R-001) | Hoch | offen | 2026-09-01 |
| SEC-006 | Oodle-DLL aus dem Spielverzeichnis per `ctypes` geladen, Zielgroesse ungeprueft (`oodle.py:28`, `oodle.py:55`) | Mittel | **teilweise zurueckgestellt** (Deckel ja, Herkunftspruefung nein) | 2026-09-01 |
| SEC-007 | `powershell` ohne absoluten Pfad gestartet, CWD-/PATH-Hijack (`shortcut.py:97`) | Mittel | offen — **Fix beauftragt** | 2026-09-01 |
| SEC-008 | Dateinamen aus `manifest.json` ungeprueft zu Pfaden zusammengesetzt (`iconpack.py:79/118`) | Niedrig | offen | 2026-09-01 |
| SEC-009 | Lieferkette des veroeffentlichten EXE nicht fixiert: Actions auf beweglichen Tags, `pip install` ohne Hashes, unsigniert, keine Pruefsumme (`.github/workflows/release.yml`) | Hoch | offen | 2026-09-01 |
| SEC-010 | `ElementTree` ohne Schutz vor Entitaeten-Expansion auf Archiv-XML (`icons.py:65`) | Niedrig | offen | 2026-09-01 |
| SEC-011 | Abhaengigkeiten: Schwachstellenstand nicht gegen eine Datenbank pruefbar, `pip-audit` fehlt im Release-Workflow | Niedrig | offen | 2026-09-01 |

## Verifizierte Projektzusagen (2026-09-01)

Alle drei oeffentlich gemachten Zusagen halten dem Code stand:

- **Save wird read-only geoeffnet** — bestaetigt. Einzige Zugriffe auf `*.sl2`
  sind `read_bytes()`; kein Schreib-, Loesch- oder Ersetzungsaufruf auf einem
  Save-Pfad im gesamten Baum.
- **Kein Netzwerkzugriff** — bestaetigt. Kein `socket`, `urllib`, `requests`,
  `QtNetwork`; `setOpenExternalLinks` wird nirgends gesetzt. Vorbehalt:
  SEC-004 koennte ueber einen UNC-Pfad in Rich-Text eine SMB-Verbindung
  erzwingen (unbelegte Hypothese, siehe unten).
- **Keine Telemetrie** — bestaetigt. Schreibziele des ausgelieferten Programms
  sind vollstaendig: `%LOCALAPPDATA%\NightreignHelper\`, `HKCU` via
  `QSettings`, eine `.lnk` im eigenen Startmenue. Sonst nichts.

Diese drei Aussagen gehoeren in den Audit-Bericht nach GOAL.md A1.

## Offene Klaerungen

- **SEC-005 — beantwortet, Befund bestaetigt.** `docs/research/R-001.md`
  (T-005, 2026-09-01): `texture2ddecoder` 1.0.6 prueft weder im Bruecken-Code
  (`pylink.cpp` fuellt `view.len`, vergleicht es aber nie) noch im Decoder
  (`bcn.cpp` iteriert ueber `ceil(w/4) * ceil(h/4)` Bloecke und rueckt den
  Eingabezeiger blind um 8 bzw. 16 Byte je Block vor). `copy_block_buffer`
  prueft nur die Grenzen des *Ausgabe*-Bildes. Eine zu kurze Nutzlast fuehrt
  zum Lesen jenseits des Puffers in nativem Code.
  **Prioritaet bleibt Hoch.** Die Eingangspruefung muss der Aufrufer
  herstellen, weil sie sonst niemand herstellt.
- **SEC-004**, SMB-Teil: unbelegt, weil der Pruefer PySide6 nicht zur Hand
  hatte. Die Markup-Injektion selbst ist belegt und genuegt fuer den Fix.

## Entscheidungen des Directors

- **SEC-001, SEC-002, SEC-004** gehen gemeinsam in einen Fix-Durchgang: sie
  betreffen denselben Eingabepfad (Savefile → Parser → Anzeige) und werden vom
  selben Regressionstest abgedeckt.
- **Kein Release**, bevor SEC-001 behoben ist. Ausloeser ohne
  Nutzerinteraktion beim Start, Wirkung ist ein dauerhaftes Einfrieren.
- **SEC-009** laeuft als eigener Strang parallel zum Feature-Zyklus — es
  beruehrt keine Programmzeile.
- **SEC-007 wird behoben** (Nutzerentscheid 2026-09-01): absoluter Pfad nach
  `%SystemRoot%\System32\WindowsPowerShell1.0\powershell.exe`, Existenz
  pruefen, sonst die Verknuepfung ausfallen lassen. Kostet eine Zeile.
- **SEC-006 wird dokumentiert statt geschlossen** (Nutzerentscheid
  2026-09-01): Groessendeckel auf `uncompressed_size` vor der Allokation, und
  ein ehrlicher Satz im README, dass der Helper eine Bibliothek aus dem
  Spielordner laedt. Eine Herkunftspruefung der DLL ist nicht vorgesehen — wer
  dort schreiben kann, hat den Nutzerkontext ohnehin. **Akzeptiertes
  Restrisiko**, bewusst und dokumentiert.

## Nicht geprueft

- `vendor/Paramdex` inhaltlich (vom Auftrag ausgeschlossen; enthaelt nur
  226 XML-Dateien, keinen Code, nichts wird zur Laufzeit nachgeladen).
- `nrdata/extract.py` und `nrplanner/app.py` Zeile fuer Zeile — gezielt an den
  sicherheitsrelevanten Stellen gelesen.
- Bekannte CVEs der Abhaengigkeiten (kein Netzzugriff im Pruefauftrag).
- Git-Historie auf entfernte Secrets.
- Signaturkette des ausgelieferten EXE (kein Artefakt zur Hand).
