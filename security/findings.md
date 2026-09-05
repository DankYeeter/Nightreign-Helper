# Sicherheitsbefunde

Quelle: T-003, `security-reviewer`, Zyklus 1.
Repo-Stand bei der Pruefung: `3da8428` (v1.7.1).
Status je Befund: offen | behoben | zurueckgestellt | entkraeftet

## Log

| ID | Titel | Prioritaet | Status | Letzte Pruefung |
|---|---|---|---|---|
| SEC-001 | Endlosschleife beim Lesen UTF-16-terminierter Namen (`savefile.py`, `binary.py`, `tpf.py`, `fmg.py`) | Hoch | **behoben - Retest bestanden**; keine sechste Suche vorhanden | 2026-09-02 |
| SEC-002 | Unbegrenzte Zaehler aus der Datei steuern Schleifen und Allokationen (`savefile.py`, `bnd4.py` inkl. `read_split_header`, `fmg.py`, `dvdbnd.py`, `tae.py`) | Mittel | **behoben - Retest bestanden**; kein Integer-Ueberlauf moeglich, alle Pruefungen vor der Allokation. Klasse offen -> SEC-017 | 2026-09-02 |
| SEC-003 | *(gesperrt, im Audit entkraeftet)* | - | entkraeftet | 2026-09-01 |
| SEC-004 | Save-Strings ungefiltert in Qt-Rich-Text, `QLabel` auf `AutoText` (`app.py`, `inventory.py`) | Hoch | **behoben - Retest bestanden** an den drei genannten Stellen. UNC-/SMB-Vorbehalt **belegt** -> SEC-019 | 2026-09-02 |
| SEC-005 | Nativer Texturdecoder erhaelt ungeprueftes Format und zu kurze Nutzlast (`dds.py`) | Hoch | **behoben - Retest bestanden**; Whitelist vollstaendig, Blockgroessen korrekt, Ausgabeallokation mitbegrenzt | 2026-09-02 |
| SEC-006 | Oodle-DLL aus dem Spielverzeichnis per `ctypes`, Zielgroesse ungeprueft (`oodle.py`) | Mittel | **Deckel behoben - Retest bestanden**; Herkunftspruefung akzeptiertes Restrisiko. Offen: relative Schranke statt fester 2 GiB (kein Blocker) | 2026-09-02 |
| SEC-007 | `powershell` ohne absoluten Pfad, CWD-/PATH-Hijack (`shortcut.py`) | Mittel | **behoben - Retest bestanden**; Rest ueber `%SystemRoot%` -> SEC-020 | 2026-09-02 |
| SEC-008 | Dateinamen aus `manifest.json` ungeprueft zu Pfaden (`iconpack.py`) | Niedrig | **behoben - Retest bestanden**; sieben Windows-Umgehungswege einzeln geprueft. Die Schreibseite war nie offen - der Regressionstest 4 prueft dort nichts | 2026-09-02 |
| SEC-009 | Lieferkette des veroeffentlichten EXE (`release.yml`) | Hoch | **offen - geteilt (Director 2026-09-02):** Action-Pin auf Commit-SHA + SHA-256-Pruefsumme **sperren das Release**; Signatur und `--require-hashes` sind tragbares Restrisiko | 2026-09-02 |
| SEC-010 | `ElementTree` ohne Schutz vor Entitaeten-Expansion (`icons.py`) | Niedrig | **behoben - Retest bestanden**; auch externe Parameter-Entitaeten und externe DTD abgedeckt, kein SSRF | 2026-09-02 |
| SEC-011 | `pip-audit` fehlt; Schwachstellenstand der Abhaengigkeiten ungeprueft | Niedrig | **GESTRICHEN (Nutzer 05.09.2026)** - anderer Grund als die uebrigen vier: kein Angriff ueber Spieldateien, sondern ein fehlendes Abhaengigkeits-Audit. Gestrichen wegen der kleinen Abhaengigkeitsflaeche (PySide6 plus zstandard); haengt an derselben Frage wie `ruff` (F-A) und kommt mit ihr zurueck, falls der Nutzer Werkzeuge aufnimmt | 2026-09-02 |
| SEC-012 | Markup-Injektion in `bosstab.py::_stance_rank` (nicht `PART_NAMES`, siehe Korrektur) | Niedrig | **behoben - Retest bestanden**; wird als Instanz von SEC-019 gefuehrt | 2026-09-02 |
| SEC-013 | `owned_label.setToolTip(self.owned.folder)` ungeescapt (`app.py`) | Niedrig | **behoben - Retest bestanden**; Escape in beiden Richtungen gegen das echte Widget geprueft | 2026-09-02 |
| SEC-014 | `bossdata._utf16` schneidet nicht terminierte Namen still ab | Niedrig | **behoben - Retest bestanden**; Funktion geloescht | 2026-09-02 |
| SEC-015 | `bosstab.py detail_expedition` auf AutoText mit `everdark_label` | Niedrig | offen - Instanz von SEC-019, Prioritaet folgt der Klasse | 2026-09-02 |
| SEC-016 | `dcx.py:38-41` reicht `uncompressed_size` ungeprueft als `max_output_size` an `zstandard` | Niedrig | **GESTRICHEN (Nutzer 05.09.2026)** - setzt eine boesartige Spielinstallation oder ein bereits uebernommenes Benutzerkonto voraus; nicht erneut vorlegen | 2026-09-02 |
| SEC-017 | `tpf.read` prueft `file_count` gegen nichts; quadratische Speicheraufnahme, 256 KiB Eingabe -> 3,2 GiB Spitzenhaufen gemessen (`tpf.py:27/37/53`) | Niedrig | **GESTRICHEN (Nutzer 05.09.2026)** - setzt eine boesartige Spielinstallation oder ein bereits uebernommenes Benutzerkonto voraus; nicht erneut vorlegen | 2026-09-02 |
| SEC-018 | `dcx.py:41-42` DFLT-Zweig ohne jeden Deckel, `zlib.decompress` ohne `bufsize`; x1029 gemessen. Gehoert in denselben Fix wie SEC-016 | Niedrig | **GESTRICHEN (Nutzer 05.09.2026)** - setzt eine boesartige Spielinstallation oder ein bereits uebernommenes Benutzerkonto voraus; nicht erneut vorlegen | 2026-09-02 |
| SEC-019 | **SEC-004 als Klasse offen:** 90 von 95 `QLabel` stehen auf AutoText, 35 von 36 Tooltips sind ungeescapt. Gemessen belegt, dass ein `<img src="file://host/...">` aus Spieltext Qt dazu bringt, eine Ressource von einem fremden Host zu oeffnen - bei UNC-Ziel eine SMB-Verbindung samt NTLMv2-Antwort des Windows-Kontos. Bricht zugleich die oeffentliche Zusage "kein Netzwerkzugriff" | **Mittel** | **neu, offen - Prioritaet am 2026-09-02 vom Nutzer auf Mittel gesenkt** (Entscheid: die eigene Spielinstallation gilt als vertrauenswuerdig). **Sperrt das Release nicht mehr.** Der gemessene Beleg bleibt gueltig, und die Zusage "kein Netzwerkzugriff" muss trotzdem umformuliert werden | 2026-09-02 |
| SEC-020 | PowerShell-Pfad wird aus `%SystemRoot%` abgeleitet; Umgebungs-Hijack ueber `HKCU\Environment` bleibt (`shortcut.py:68`) | Niedrig | **GESTRICHEN (Nutzer 05.09.2026)** - setzt eine boesartige Spielinstallation oder ein bereits uebernommenes Benutzerkonto voraus; nicht erneut vorlegen | 2026-09-02 |

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

### Zyklus 3 (2026-09-02)

- **T-017 abgenommen unter Vorbehalt des Retests.** SEC-001, SEC-002 und
  SEC-004 haben einen Fix mit 13 neuen Regressionstests (Suite 78 -> 91) und
  einer Mutationspruefung, die 10 von 13 Faellen gegen den Vorher-Stand
  fehlschlagen liess. Commits `bdff837`, `4c55860`, `511021a`. Status bleibt
  bis zum Durchlauf von `qa-engineer` und `security-reviewer` auf
  "Fix vorliegt". **Ein Fix ist kein Nachweis.**
- **Ausweitung auf `bnd4.read_split_header` bestaetigt.** Die
  Zwillingsfunktion hat denselben Defekt wie die in SEC-002 genannte; ein
  "behoben", das sie offenlaesst, waere eine falsche Aussage.
- **Drei neue Befunde aus dem T-017-Bericht aufgenommen** (SEC-012 bis
  SEC-014) und in T-018 eingeplant, statt sie einzeln nachzuziehen.
- **`inventory.py:189` bleibt unveraendert.** Die Abwehr gegen SEC-004 sitzt
  an der Anzeige, nicht am Ursprung. Eine Laengenbegrenzung am Ursprung waere
  eine geratene Konstante und neues Verhalten — nicht in einem Sicherheitsfix.
- **Testsockel-Luecke als Debt aufgenommen, nicht zurueckgestellt:**
  `tests/conftest.py` nimmt den Snapshot-Cache, wenn er existiert. Damit
  laufen `fmg`, `bnd4`, `dvdbnd`, `tpf` und `tae` in einem gruenen Lauf gar
  nicht — **jede kuenftige `nrdata/`-Aenderung sieht getestet aus, ohne es zu
  sein.** Geht als eigener Punkt in T-018.

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

### Zyklus 3, nach T-018 (2026-09-02)

- **SEC-012 Befundtext korrigiert.** Der urspruengliche Text benannte
  `PART_NAMES.get((boss["name"], label), label)`. Das ist aus den Spieldaten
  **nicht** erreichbar: `label` erzeugt der Extraktor als `"Part N"`
  (`bossdata._profile`), und `PART_NAMES` ist ein im Quelltext stehendes,
  derzeit leeres Dict (`bosstab.py:50`) - der Boss-Name ist dort nur der
  Nachschlage-Schluessel, nicht der eingesetzte Wert. Die tatsaechlich
  erreichbare Injektion in `detail_body` sitzt in `bosstab.py::_stance_rank`,
  wo `other["name"]` zweier anderer Bosse per Konkatenation in den HTML-String
  geht. Der `developer` hat beide Stellen geschlossen und den Befundtext
  gemeldet, statt formal gegen die falsche Zeile zu liefern. **Der QA-Retest
  prueft `_stance_rank`, nicht `PART_NAMES`.**
- **SEC-006-Deckel akzeptiert, Messgrenze dokumentiert.** Gemessen wurde die
  groesste Oodle-Nutzlast ueber 5 103 unverschluesselte KRAK-Mitglieder:
  982 464 964 Byte (937 MiB). **24 261 verschluesselte Mitglieder wurden nicht
  gemessen** - die Zahl ist eine untere Schranke, keine Obergrenze. Der Deckel
  steht auf 2 GiB, gut das Doppelte, und ein Ueberschreiten faellt als
  `ValueError` auf, nicht still. Eine vollstaendige Messung waere ein Durchlauf
  ueber alle 24 261 verschluesselten Eintraege; **das ist den Preis nicht wert,
  solange der Fehlerfall laut ist.** Bewusst akzeptiert.
- **Zwei neue Befunde aufgenommen** (SEC-015, SEC-016) statt sie in T-018
  nachzuschieben - der Stand ist fuer die Pruefphase eingefroren.
- **`-ExecutionPolicy Bypass` in `shortcut.py` ist kein Befund**, aber es
  gehoert in den Audit-Bericht nach GOAL A1 erklaert: das Skript kommt aus dem
  Quelltext, die Pfade gehen ueber die Umgebung.
- **`ruff` als Entwicklungsabhaengigkeit zurueckgestellt, nicht abgelehnt.**
  Im Repo existiert kein Linter; die DoD verlangt "Linter sauber" und das ist
  derzeit nicht pruefbar. Eine neue Abhaengigkeit zieht `researcher` und
  `compliance-agent` (Modus `lizenzen`) nach sich - das gehoert in einen
  eigenen Zyklus, nicht in einen Sicherheitszyklus. Vermerkt, damit es nicht
  verloren geht.

### Zyklus 3, nach dem Retest (2026-09-02)

- **Alle zwoelf Fixes halten dem adversarialen Retest stand.** Kein Fix ist
  umgehbar. Drei (SEC-005, SEC-008, SEC-010) decken mehr ab, als der Auftrag
  verlangte. SEC-001, der bisherige Sperrgrund, ist geschlossen - es gibt keine
  sechste UTF-16-Suche, alle Zaehlerpruefungen stehen vor der Allokation, und
  ein Integer-Ueberlauf ist in Python-Ints nicht moeglich.
- **Der Sperrgrund hat gewechselt: SEC-019 sperrt jetzt.** Er ist keine neue
  Luecke, sondern die alte in ihrer wahren Groesse. SEC-004, SEC-012, SEC-013
  und SEC-015 waren als "ein Name wird fett gerendert" eingestuft. Gemessen ist
  die Wirkung: *ein Name entscheidet, welche Datei auf welchem Host geoeffnet
  wird.* Ein AutoText-`QLabel` mit `<img src="C:/.../probe_64.png">` bekommt
  `sizeHint` 64x64 - die Groesse der Datei auf der Platte; das Label hat sie
  gelesen. `QTextDocument.loadResource` wird mit der URL wortgetreu aus dem
  Text aufgerufen, und `QUrl("file://127.0.0.1/share/a.png").toLocalFile()`
  liefert einen UNC-Pfad. Der letzte Schritt (SMB-Verbindung, NTLM-Antwort)
  wurde per Richtlinie **nicht** ausgefuehrt und stuetzt sich auf
  dokumentiertes Windows-Verhalten.
- **Behebungsrichtung fuer SEC-019 steht fest, falls der Nutzer sie will:
  nicht 90 Einzelaenderungen.** Neunzig `setTextFormat`-Aufrufe schliessen den
  heutigen Stand und oeffnen sich beim naechsten neuen Label wieder. Was die
  Klasse schliesst, ist eine gemeinsame Fabrik fuer Labels mit
  Extraktionsdaten (`developer`) plus ein **Waechtertest**, der den gebauten
  Widget-Baum ueber `findChildren(QLabel)` durchlaeuft und fuer jedes Label
  mit Snapshot-Text `textFormat() != AutoText` verlangt (`qa-engineer`).
- **Ursprungsseitiges Escapen bleibt ausgeschlossen - jetzt mit Beleg.** Der
  echte Spieltext dieser Installation enthaelt `<?codenameIcon?>` und in 30
  weiteren Zeichenketten ein rohes `&`. Der Ursprung kann Markup nicht von
  Inhalt unterscheiden, ohne echten Text zu veraendern. Die Abwehr sitzt an
  der Anzeige.
- **SEC-016 wird NICHT hochgestuft.** Der Pruefer widerspricht meiner Vermutung
  begruendet, und er hat recht: `dcx.decompress` ist von einem Savefile aus
  nicht erreichbar (`savefile.py` ruft `dcx` nirgends auf), und der Pfad laeuft
  beim **Erst**start bzw. beim Neuaufbau des Snapshots, nicht bei jedem Start.
  Es ist dieselbe Grenze und dieselbe Wirkung wie SEC-006, das der Nutzer mit
  Deckel und lautem Fehlerfall angenommen hat. Anheben waere inkonsistent.
- **SEC-016, SEC-018 und die relative Schranke zu SEC-006 gehen in EINEN
  Nachtrag.** Es ist derselbe Defekt in drei Codecs. Die tragfaehige Loesung
  ist keine gemessene Konstante, sondern eine relative Schranke aus der
  komprimierten Nutzlast, die beim Aufruf ohnehin vorliegt: fuer ein kleines
  Mitglied schrumpft der schlimmste Fall von 2 GiB auf wenige MiB.
  **Die Messung der 24 261 verschluesselten Mitglieder wird ausdruecklich
  nicht nachgeholt** - sie liefert nur eine andere feste Zahl mit demselben
  Problem.
- **SEC-009 wird geteilt.** Sperrend sind genau zwei Punkte, zusammen unter
  zehn Zeilen YAML: `softprops/action-gh-release@v2` auf einen Commit-SHA
  pinnen (bewegliches Tag in einem Job mit `contents: write` - der einzige Weg
  zu einer untergeschobenen EXE), und eine SHA-256-Pruefsumme in die
  Release-Notes. Signatur (kostet Geld, Entscheidung des App Designers) und
  `--require-hashes` (verlangt Lockdatei und Prozess; `requirements.txt` ist
  bereits auf sieben exakte Versionen gepinnt) sind tragbares Restrisiko.
- **`-ExecutionPolicy Bypass` bleibt ein Nicht-Befund, aber die Begruendung im
  Register war falsch.** Nicht tragend ist "das Skript kommt aus dem
  Quelltext". Tragend ist: `-ExecutionPolicy` regelt **nur Skriptdateien**, eine
  `-Command`-Zeichenkette unterliegt ihr gar nicht - der Schalter ist an dieser
  Stelle wirkungslos und sollte verschwinden, weil er den Leser glauben macht,
  hier werde ein Schutz abgeschaltet. Und: alles, was den Aufruf beeinflussen
  koennte (Umgebungsblock, `HKCU`, `PSModulePath`, die `.exe` selbst), steht
  bereits auf derselben Integritaetsstufe wie der Prozess. Diese Fassung geht
  in den Audit-Bericht nach GOAL A1.
- **Offen beim Nutzer, von mir nicht beantwortet:** ob die Spielinstallation
  eine Vertrauensgrenze ist. Der Pruefer nimmt an, dass modifizierte
  Spieldateien (Randomizer, Texturpakete, Uebersetzungen) in dieser
  Spielergemeinschaft ein normaler, von Fremden bezogener Artefakttyp sind, und
  fuehrt `nrdata/` deshalb gegen "diese Bytes hat ein Fremder geliefert".
  **Widerspricht der App Designer, sinken SEC-005, SEC-016 bis SEC-019 je eine
  Stufe** - und SEC-019 waere dann kein Release-Blocker mehr. Das ist eine
  Produktentscheidung ueber die eigene Bedrohungslage, keine technische.

### Ergaenzung zu "Verifizierte Projektzusagen" (2026-09-02)

Alle drei Zusagen wurden nach den zwoelf Codeaenderungen erneut geprueft.
**Save read-only** und **keine Telemetrie** halten unveraendert; neu
hinzugekommen ist nur `urllib.parse` (`chalices.py:24`) als reine
Zeichenkettenverarbeitung fuer die QA-003-Schluesselableitung, ohne I/O.
Zusaetzlich wurde die **Git-Historie ueber 79 Commits auf entfernte Secrets**
geprueft - nichts gefunden; die Schluessel in `keys.py`/`bhd5.py` sind ein
oeffentlicher AES-Konstantenwert und oeffentliche RSA-Schluessel aus der
Community-Toolchain.

**Die Zusage "kein Netzwerkzugriff" braucht eine neue Fassung.** Auf
Programmebene haelt sie (kein `socket`, `urllib.request`, `requests`, `http`,
`QtNetwork`, `QDesktopServices`, `webbrowser`, kein `setOpenExternalLinks`).
Der SEC-004-Vorbehalt ist aber von "unbelegte Hypothese" auf **belegt**
(SEC-019) zu setzen. Ehrliche Fassung: *"Das Programm oeffnet selbst keine
Verbindung. Qts Rich-Text-Darstellung laedt eine Ressource, die im angezeigten
Text benannt wird; 90 von 95 Labels reichen Spieltext ungefiltert dorthin."*
Solange SEC-019 offen ist, darf die kurze Fassung nicht im README stehen.

### Nicht geprueft (Stand 2026-09-02)

- `nrdata/extract.py` und `nrplanner/app.py` Zeile fuer Zeile - gezielt an den
  Senken gelesen. **Die Aufzaehlung in SEC-019 belegt die Klasse, sie
  erschoepft sie nicht.**
- Bekannte CVEs der sieben Abhaengigkeiten (kein Netzzugriff im Pruefauftrag).
  Bleibt unter "nicht geprueft", nicht unter "in Ordnung" - SEC-011.
- Signaturkette der ausgelieferten EXE - kein gebautes Artefakt zur Hand,
  GOAL A9 offen.
- Die vermutete 4-GiB-Allokation aus `dvdbnd._read_entry`
  (`fh.read(entry.padded_size)`, u32 ungeprueft): als Hypothese notiert, nicht
  ausgeloest.
- Der letzte Schritt der UNC-Kette in SEC-019 (SMB-Verbindung, NTLM-Antwort) -
  Richtlinie, keine Angriffe gegen laufende Systeme.
- `vendor/Paramdex` - unveraendert vom Auftrag ausgeschlossen.

### Entscheid des Nutzers, 2026-09-02: die Spielinstallation ist vertrauenswuerdig

Auf die Frage, ob modifizierte Spieldateien (Randomizer, Texturpakete,
Uebersetzungen) als "von einem Fremden geliefert" zu behandeln sind, hat der
App Designer entschieden: **nein - die eigene Spielinstallation gilt als
vertrauenswuerdiger Bereich.** Folgen, ohne Ausnahme angewandt:

- **SEC-015, SEC-016, SEC-017, SEC-018 sinken auf Niedrig**; **SEC-019 sinkt
  von Hoch auf Mittel.** Grenze A (heruntergeladenes Save) ist davon
  **nicht** beruehrt - dort bleibt jede Einstufung, wie sie ist.
- **SEC-019 sperrt das Release nicht mehr.** GOAL A2 ist an dieser Stelle
  nicht mehr verletzt.
- **Der Beleg bleibt trotzdem stehen und wird nicht relativiert**: dass ein
  AutoText-Label eine Datei von einem fremden Host oeffnen kann, ist gemessen,
  nicht vermutet. Gesunken ist die Wahrscheinlichkeit des Ausloesers, nicht
  die Wirkung.
- **Die Zusage "kein Netzwerkzugriff" muss dennoch umformuliert werden**,
  bevor etwas veroeffentlicht wird. Eine Zusage, die der Code nicht haelt,
  wird nicht dadurch richtig, dass der Ausloeser unwahrscheinlich ist.
