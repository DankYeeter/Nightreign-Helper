# T-143 — architect

```
STATUS: erledigt
AUFTRAG: T-143 — A15 entwerfen, und AD-029s dritte Vertrauensgrenze nachziehen
GELESEN: docs/tasks/T-143.md · ~/.claude/agents/_rahmen.md · CLAUDE.md · GOAL.md ·
  docs/state.md · ARCHITECTURE.md (AD-029, Nachtraege VIII-X, Kopf) ·
  UI_SPEC.md (§2-§11 zu A15, AK-106 bis AK-132; §11-§14, AK-220 bis AK-229) ·
  qa/findings.md (QA-195, QA-199, QA-200) · security/findings.md (SEC-015 bis
  SEC-019, SEC-022) · docs/perf/baselines.md (S11-E, U3/T-140) ·
  nrdata/savefile.py · nrdata/gamefiles.py · nrdata/oodle.py ·
  nrplanner/firstrun.py · nrplanner/paths.py · nrplanner/favourites.py ·
  nrplanner/chalices.py:180-330 · nrplanner/datasource.py · nrplanner/inventory.py ·
  nrplanner/app.py (Startweg, rescan_save) · tests/test_settings_store.py ·
  tests/test_relic_scan_prefilter.py · tests/test_hostile_savefile.py ·
  .claude/agent-memory/architect/ (drei Eintraege)
GEÄNDERT: ARCHITECTURE.md (Nachtrag XI angehaengt; plus Abloesungsvermerk in
  AD-029 Vertrauensgrenze Punkt 3 und der Auflagen-Absatz in der Umsetzung —
  zusammen 5358 → 5972 Zeilen) · docs/berichte/T-143-architect.md (dieser
  Bericht, neu) · .claude/agent-memory/architect/ (MEMORY.md,
  project_berater_stand.md, project_of15_qsettings_schluesselraum.md — neu;
  nicht versioniert). **Nichts committet, nichts gestaged.**
  Die sechs geaenderten Dateien unter `nrplanner/` und `tests/` in
  `git status` stammen aus dem parallel laufenden T-142, nicht von mir.
ANNAHMEN: (1) Die Schaetzungen der Auftragsdauer (45-60 min je Schritt) sind
  Schaetzungen aus Dateigroesse und Umfang, keine Messwerte — als solche
  benannt. (2) Ein toter UNC-Pfad kann ein `stat` zweistellig verzoegern:
  Erfahrungswert, hier nicht gemessen, deshalb OF-32 statt einer Vorkehrung.
  Keine Annahme zu `docs/research/`/`docs/legal/` — dort geprueft, siehe unten.
NÄCHSTER: director — er erteilt V1 (developer) und legt fest, ob OF-31 vor V2
  an den security-reviewer geht.
BLOCKIERT DURCH: nichts. Hinweis: `nrplanner/app.py`, `nrplanner/inventory.py`
  und `tests/` sind zum Zeitpunkt dieses Berichts durch T-142 belegt; V2 bis V5
  koennen erst danach starten. V1 und V4 beruehren keine dieser Dateien.
```

---

## Ergebnis in fuenf Zeilen

A15 bekommt **zwei feste QSettings-Schluessel** (`paths/game`, `paths/save`) im
vorhandenen Speicher und **einen** Aufloesungspunkt, den auch `datasource.py`
benutzt — heute rufen **vier** Produktivstellen `find_game_dir()` und meinen
Verschiedenes. Der Vorfilter verweigert kuenftig nicht mehr, sondern **waehlt**
den langsamen Weg, der dafuer wieder gebaut wird. Fuenf Bauauftraege (V1 bis
V5), achtzehn Regressionsfaelle (R1 bis R18), zwei offene Fragen.

## Die beiden Entscheidungen

**AD-030 — der gemerkte Pfad.** Ort: der vorhandene Speicher ueber
`favourites.ORG`/`favourites.APP`, **genau zwei feste Schluessel**, Pfad im
**Wert**. Format: ein `str`, absolut, aufgeloest auf den Ordner mit
`regulation.bin` — dieselbe Form, die `find_game_dir()` liefert; gelesen mit
`type=str`, weil QSettings einen Wert mit **Komma** sonst als Liste
zurueckgibt und ein Ordnername ein Komma tragen darf. Beschaedigter Eintrag
(leer, kein `str`, kein baubarer Pfad): **wie abwesend**, kein Dialog, kein
Fehler — **und nicht geloescht**. Pfad beim naechsten Start weg: Stufe-1-Pruefung
scheitert (jede `OSError` gilt als ungueltig) → `find_game_dir()` → bei Erfolg
benutzt **ohne** das Gemerkte zu ueberschreiben → sonst Panel A3 (Abzug da) oder
A2 (kein Abzug). Geschrieben wird nur, was der Nutzer bestaetigt hat, und zwar
**vor** dem Bau (AK-117).

**AD-031 — Rueckfall statt Verweigerung.** `relic_scan_mode(valid_relic_ids)`
entscheidet **einmal je Ladevorgang** aus dem Datensatz, nicht aus der Datei;
`read_owned_relics` bekommt ein Schluesselwort `mode`, der **Rueckgabetyp
aendert sich nicht**. Ein Rekord-Leser, zwei Versatz-Erzeuger. Der Weg reist als
`Inventory.read_the_slow_way: bool` (unveraenderlich, passiert die Thread-Grenze
von Stufe B ohne Sonderfall) bis in die Bestandszeile.

## Warum OF-15 nicht verletzt wird — die Randbedingung, nachgelesen

OF-15 begruendet „kein neuer persistenter Zustand" mit drei Datenverlusten. Ich
habe sie an der Stelle nachgelesen, an der sie dokumentiert sind
(`nrplanner/chalices.py:190-320`), statt die Begruendung zu uebernehmen:
**alle drei** (QA-003, QA-046, QA-033) entstanden, weil **Nutzertext zum
Schluessel** wurde — unbegrenzter, aus Eingaben abgeleiteter Schluesselraum, und
die zerstoerende Operation war jedes Mal `remove`. **Kein einziger** betrifft
einen festen Schluessel mit veraenderlichem Wert; das ist die Bauform von
`ui/scale` und `ui/panes`, die nichts verloren hat. Die zweite tragende Aussage
aus OF-15 — „ein Halt verweist auf einen Handle, und Handles werden neu
vergeben" (AD-013) — trifft auf einen Pfad nicht zu: er ist von aussen pruefbar
und wird bei **jedem** Start geprueft. **OF-15 ist damit nicht widerlegt,
sondern in seiner Reichweite benannt.** Daraus die Invariante, die einen
Waechter bekommt (R2): **auf `paths/…` wird nie `remove` gerufen; die zwei Werte
werden nur ueberschrieben.**

## Drei Befunde, die ich melde

1. **`find_game_dir()` steht an vier Produktivstellen, nicht an einer**
   (`app.py:4428`, `datasource.py:96/142/168`). Wird nur `app.py` umgestellt,
   heisst es an drei Stellen weiter „der automatisch gefundene Ordner" und wird
   als „der Spielordner" gelesen: `_load_data` extrahiert nach einem Patch nicht
   live aus dem gewaehlten Ordner, `_regulation_matches` reicht den alten Abzug
   kommentarlos durch (**das ist QA-171s Loch**), und `_no_data_message`
   behauptet, es sei nichts gefunden, waehrend etwas gemerkt ist. Deshalb der
   Aufloesungspunkt.
2. **`tests/test_relic_scan_prefilter.py:43-80` traegt `full_walk` als
   absichtlich unabhaengige dritte Implementierung.** Zieht der `developer` sie
   in den Produktivcode und vergleicht dann Produktion gegen Produktion, ist der
   Waechter entkernt, **ohne dass ein Test rot wird** — L-008 (b). Steht als
   Verbot im „nicht tun"-Abschnitt.
3. **Es gibt zwei Vorfilter, nicht einen** — `_relic_id_offsets` (`:209`) und
   `_loadout_marker_offsets` (`:388`). Ein Rueckfall wird trotzdem nur an einer
   Stelle gebraucht: der Loadout-Filter sucht eine **Programmkonstante**
   (`HERO_MARKER_BASE + 1`), der Relikt-Filter steht auf einer **Annahme ueber
   die Spieldaten**. Nur die zweite kann ein Patch **still** brechen.

## Die Vertrauensgrenze verschiebt sich — Fall fuer den `security-reviewer`

**Ja, der Auswahldialog aendert etwas**, an zwei Stellen:

- **Der gewaehlte Ordner wird nicht nur gelesen — aus ihm wird eine native DLL
  in den Prozess geladen** (`oodle.load()` → `ctypes.CDLL(str(game_dir / name))`,
  `nrdata/oodle.py:34-46`), und **AK-112 nimmt den Ordner gerade deshalb an,
  weil eine dieser DLLs darin liegt**. Bisher konnte `find_game_dir()` nur Pfade
  aus der Steam-Bibliothekliste liefern.
- **SEC-016, SEC-017 und SEC-018 sind am 05.09.2026 gestrichen worden mit der
  Begruendung, sie setzten „eine boesartige Spielinstallation oder ein bereits
  uebernommenes Benutzerkonto voraus"** (`security/findings.md:26-28`), samt
  „nicht erneut vorlegen". Es sind Entpackbomben im Spieldatenpfad. **Diese
  Bedingung ist unter A15 keine Kontouebernahme mehr, sondern eine
  Ordnerauswahl.** Ich lege den Befund **nicht** erneut vor — ich melde, dass
  seine Randbedingung fuer den geprueften Fall galt und fuer den neuen nicht
  geprueft ist. Das ist OF-31.
- **Beim Spielstand aendert sich die Erreichbarkeit, nicht die Haerte.** Filter
  `All files (*)` macht ein heruntergeladenes Save in einem Klick erreichbar —
  die scharfe Grenze, die der Nutzer am 02.09.2026 stehen gelassen hat. Die
  Abwehr (SEC-022, zweite Dichtepruefung, SEC-002-Deckel) bleibt unveraendert
  und traegt weiter; ob sie fuer einen bewusst von aussen geholten Spielstand
  reicht, gehoert dem `security-reviewer`.

## Reihenfolge der Bauauftraege

| # | Dateien (Produktiv) | Schaetzung | haengt an |
|---|---|---|---|
| **V1** | `nrdata/gamefiles.py`, `nrplanner/gamepath.py` (neu), `nrplanner/datasource.py` | 45-60 min | — |
| **V2** | `nrplanner/firstrun.py`, `nrplanner/app.py` | 60 min, **grenzwertig** | V1 |
| **V3** | `nrplanner/app.py`, `nrplanner/gamepath.py` | 40-50 min | V1 (**nicht** V2) |
| **V4** | `nrdata/savefile.py`, `nrplanner/inventory.py` | 40 min | — |
| **V5** (= U8) | `nrplanner/app.py`, `nrplanner/inventory.py`, Qt-Modul fuer die Lesespur | eigener Auftrag | V4, U3 |

**V4 gehoert unmittelbar vor V5**, nicht irgendwann davor: dazwischen faellt das
Programm im Patch-Fall zwar zurueck, **sagt es aber noch nicht** — ein
A7-Bruch, der genau so lange dauert, wie die zwei Auftraege auseinanderliegen.
Ist eine Luecke absehbar, gehoert V4 **hinter** V5.
**V2 und V3 fassen beide `app.py` an** und laufen nacheinander.
**Neu und relevant fuer die Planung:** U3 (T-140) hat den Ausloeser fuer AD-029
Stufe B bereits gemeldet — `inventory.load` **657,2 ms** gegen die Schwelle
250 ms (`docs/perf/baselines.md`, Zeilen 191/213). **V5 ist faellig**, und
`UI_SPEC` §11 ist seine Vorgabe.

## Regressionstests

R1 bis R18, vollstaendig mit toetender Mutation in `ARCHITECTURE.md`, Nachtrag
XI. Dieselbe Liste fuer `developer` (baut) und `qa-engineer` (prueft nach). Die
tragenden vier:

- **R2** — `remove` auf `paths/…` gibt es nicht, gehalten in **zwei** Formen
  (Verhalten und AST-Klasse, Form von `test_settings_store.py`), `OFFEN`-Liste
  leer und darf nur schrumpfen.
- **R6** — **ein** Aufloesungspunkt: kein Modul unter `nrplanner/` ruft
  `gamefiles.find_game_dir()` ausser `gamepath`; benannte Ausnahme `scripts/`;
  `.claude/` ausgelassen (Worktrees).
- **R12/R14** — beide Scanwege sagen dasselbe, je gegen das **unabhaengige**
  `full_walk`; die Verweigerung faellt, toetende Mutation ist der wieder
  eingesetzte `raise` — genau die, die AK-228 selbst nennt.
- **R13** — die Wahl an **drei Literalen** (`2013322`, `0x00FFFFFF`,
  `0x01000000`), **nicht** aus `RELIC_ID_CEILING` gerechnet.

**In keinen dieser Tests gehoert eine Zeitschranke.** Der Rueckfallweg ist
langsam von Bauart; Zeiten stehen in `docs/perf/baselines.md`.

## Was ich nachgeprueft statt uebernommen habe

| Aussage | Herkunft | Ergebnis |
|---|---|---|
| Der Code verweigert statt zurueckzufallen | T-141 | **haelt** — `savefile.py:237-246`, `raise`, erste Zeile von `read_owned_relics` |
| Den langsamen Weg gibt es nicht mehr | T-141 | **haelt** — zwei unabhaengige Suchen (`range(0, len(`; `slow way\|fallback scan\|every fourth\|stride`), genau ein Versatz-Erzeuger |
| Kein `QFileDialog` in `nrplanner/` | Auftrag, QA-199 | **haelt** — zwei Suchen, 0 Treffer; ebenso `paths/game\|paths/save`, 0 Treffer |
| „der Vorfilter" (Einzahl) | T-141 | **praezisiert** — es sind **zwei**, ein Rueckfall wird an **einem** gebraucht, mit Grund |

## Was `docs/research/` und `docs/legal/` dazu sagen — geprueft, nicht angenommen

**`docs/research/` R-001 bis R-006:** keine der sechs Recherchen beruehrt A15
oder den Spielstand-Scan (Themen: `texture2ddecoder`-Puffer, EULA-Klausel,
Fan-Wiki-Praxis, Angriffsfaktor, Multiplikatoren, heldengebundene Boni). **Kein
Ergebnis, das diesen Entwurf beruehrt.**

**`docs/legal/AUFLAGEN.md` — zwei Auflagen treffen A15**, beide fuer den
`technical-writer`, nicht fuer den `developer`, und beide **nach** V3:

- **A-026 (GRUEN, `developer`, vor Veroeffentlichung):** „kein Pfad mit
  Steam-Konto-Id auf der Flaeche" (SEC-023). **Der Entwurf haelt das** —
  AK-126 laesst nur den Dateinamen zu, der volle Pfad bleibt im Tooltip. Der
  Bauauftrag V3 traegt diese Auflage; R11 haelt sie fest.
- **A-024 / A-027 (GELB bzw. GRUEN, `technical-writer`):** der Transparenztext
  und der README-Absatz „What it reads and where it writes" **zaehlen heute
  auf, was das Programm speichert.** A15 fuegt zwei gespeicherte Werte hinzu
  (`paths/game`, `paths/save`). **Diese Auflage ist damit nach V3 nachzuziehen**
  — das steht in keinem Auftrag und gehoert dem `director`.
- **A-032** ("neu klaeren bei … Schreiben in Spielstand/Spiel") ist **nicht**
  ausgeloest: A15 schreibt weder in den Spielstand noch in die Installation.

## Offene Fragen

- **OF-31 — `director` → `security-reviewer`, vor V2.** Die drei Punkte oben
  (DLL-Ladung aus gewaehltem Ordner; die Streichbedingung von SEC-016/017/018;
  Erreichbarkeit eines heruntergeladenen Saves).
- **OF-32 — `director` → `performance-tuner`, nach V1.** Die
  Gueltigkeitspruefung laeuft **vor** dem ersten Fenster; ein toter UNC-Pfad
  kann sie verzoegern. Nicht gemessen, hier ohne Netzfreigabe nicht messbar.
  Empfehlung: erst messen, dann entscheiden — keine Frist auf Vorrat.

**Kein Widerspruch zur Spec gefunden.** AK-106 bis AK-132 und AK-220 bis AK-229
sind gegen den Entwurf gelesen; AD-030 **ergaenzt** sie an vier Punkten
(Aufloesungspunkt, Nie-Loeschen-Invariante, `type=str`, ein Praedikat fuer
Annahme und Gueltigkeit), widerspricht aber keinem. `UI_SPEC.md` ist von mir
nicht angefasst.

## Buchfuehrung fuer den `director`

Vergeben: **AD-030**, **AD-031**, **OF-31**, **OF-32**, Umsetzungsschritte
**V1 bis V5**, Regressionsfaelle **R1 bis R18**. **AD ab AD-032** · **OF ab
OF-33**. Der `U`-Kreis wird **nicht** fortgesetzt (V5 ist U8 unter neuem Namen),
damit „U8" eindeutig AD-029 Stufe B bleibt. **AD-027 bleibt unbelegt.**
