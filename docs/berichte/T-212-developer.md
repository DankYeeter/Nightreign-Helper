STATUS: erledigt
AUFTRAG: T-212 — L-009, die mechanische Haelfte: kein Offscreen-Plugin fuer Geometriemessungen
GELESEN: docs/tasks/T-212.md; docs/berichte/T-199-developer.md; docs/berichte/T-209-retrospective.md;
  .github/workflows/tests.yml; nrplanner/paths.py; nrplanner/favourites.py; nrplanner/gamepath.py;
  nrplanner/firstrun.py (Signatur); nrdata/extract.py (Signatur, nicht vollstaendig);
  tests/conftest.py (game_data-Fixture, `_snapshot_from_game`); tests/weapon_damage_cases.py (vollstaendig);
  tests/test_tab_geometry.py (Kopf, zur Bestaetigung der L-009-Mechanik); tests/rendered.py (Kopf);
  scripts/capture_weapon_damage.py, scripts/differential/capture.py, scripts/measure_advisor_block.py,
  scripts/measure_display_thresholds.py, scripts/measure_picker_cards.py (alle vollstaendig);
  .claude/agent-memory/developer/MEMORY.md und die drei referenzierten Memory-Dateien
GEÄNDERT: scripts/measure_advisor_block.py, scripts/measure_picker_cards.py (committet als a0a6be2);
  docs/berichte/T-212-developer.md (dieser Bericht). Ausserhalb von Git (Memory, per .gitignore
  von der Versionierung ausgenommen): .claude/agent-memory/developer/MEMORY.md (Zeile ergaenzt),
  .claude/agent-memory/developer/reference_frischer_snapshot_fuer_fenstermessungen.md (neu).
ANNAHMEN: (1) Meine eigene Zaehlung der geometrie-messenden Skripte weicht von der in der
  Auftragsdatei zitierten Zahl der Retrospektive ("drei") ab — ich zaehle **zwei**, mit Beleg
  unten; der Auftrag selbst sagt ausdruecklich "das ist seine Zahl, nicht meine", ich behandle
  das nicht als Widerspruch. (2) "Verweigern" statt "warnen" fuer beide betroffenen Skripte, weil
  ihre Zahlen laut eigenem Docstring in UI_SPEC.md-Entscheidungen (AK-160/AK-161) bzw. einen
  Bericht, der AK-41/AK-51 traegt (T-093, L-001), einfliessen — keine Momentaufnahme fuer einen
  Menschen. (3) Fuer die Verifikationslaeufe habe ich einen frischen, aktuellen Datensnapshot
  in-process aus der installierten Spielinstallation gebaut (rein lesend), weil der feste
  Testabzug laut CLAUDE.md nicht existiert (QA-231) und der echte Cache des Nutzers aelter als
  EXTRACT_VERSION 9 ist (KeyError beim Bau des Planner). Details im Memory-Eintrag.
NÄCHSTER: director
BLOCKIERT DURCH: nichts

---

## 1. Wer misst wirklich Geometrie — meine Zaehlung, nicht die der Retrospektive

| Skript | misst Geometrie? | Begruendung |
|---|---|---|
| `scripts/measure_advisor_block.py` | **Ja** | Liest `label.width()`, `label.minimumSizeHint().width()`, `scroller.width()`, `cards[0].width()`, `bar.maximum()` (Scrollbar-Bereich), `window.width()/.height()` — alles Pixelwerte eines echten, gebauten `Planner`-Fensters. Direkt betroffen von unterschiedlichen Schriftmetriken. |
| `scripts/measure_picker_cards.py` | **Ja** | Liest `card.width()/.height()`, `dialog.width()/.height()`, `dialog.scroll.viewport().width()/.height()`, `wanted_height`, zaehlt Kartenzeilen ueber `card.height()` — dieselbe Klasse Pixelmessung an echten Widgets. |
| `scripts/capture_weapon_damage.py` | **Nein** | Treibt einen echten `Planner`, liest aber ausschliesslich `.text()`-Strings (`ar_label.text()`, `tile.title.text()`, `tile.detail.text()`, `_ar_breakdown_text()`) und numerische Felder (`last_ar`). `QLabel.text()` liefert den gesetzten Text unveraendert zurueck, unabhaengig von Schriftmetriken. Kein `.width()`, `.height()`, `sizeHint`, keine Scrollbar-Abfrage im ganzen Skript (grep bestaetigt: keine Treffer). |
| `scripts/differential/capture.py` | **Nein** | Nutzt denselben Harness (`tests/weapon_damage_cases.py::run`) wie oben, plus `arsenal_tile_texts()`, die ebenfalls nur `label.text()` liest. Gleicher Befund, gleiche Begruendung. |
| `scripts/measure_display_thresholds.py` | **Nein** | Baut **gar keine** `QApplication` — importiert `nrplanner.app` nur wegen der Konstante `VISIBLE_CHANGE` (ein `float`) und rechnet ausschliesslich mit `damage.candidate(...).scaled_headline`, reiner Modellrechnung. Kein Widget, keine Pixelmessung moeglich. |

**Ergebnis: zwei von fuenf, nicht drei.** Die Retrospektive (`docs/berichte/T-209-retrospective.md`,
Abschnitt 8) nennt "fuenf Skripte setzen offscreen, drei messen Geometrie", ohne die drei zu
benennen. Nach Volltextsuche auf `\.width\(\)|\.height\(\)|sizeHint|scrollBar` in allen drei
uebrigen Skripten (kein Treffer in allen dreien) und Durchsicht jeder Zeile bleibe ich bei zwei.
Falls die Retrospektive ein drittes Skript im Blick hatte, das ich uebersehen habe, ist das ein
offener Punkt fuer den `director` — meine Suche deckt nur die fuenf im Auftrag genannten Dateien.

Die drei nicht betroffenen Skripte bleiben **unveraendert**: `offscreen` ist dort schneller und
korrekt (Vorgabe 1 erlaubt das ausdruecklich).

## 2. Verweigern statt warnen — fuer beide betroffenen Skripte, mit Begruendung im Skript selbst

Beide Skripte tragen jetzt eine Funktion `refuse_if_offscreen(app)`, die nach dem Bau der
`QApplication` `app.platformName()` prueft und mit `SystemExit` abbricht, wenn das Ergebnis
`"offscreen"` ist — statt wie bisher `QT_QPA_PLATFORM` per `setdefault` selbst auf `offscreen`
zu setzen. Die Entscheidung steht als Satz im Docstring der Funktion und im Modul-Docstring,
nicht nur in diesem Bericht:

- **`measure_advisor_block.py`**: "A script whose numbers become a spec value must not hand one
  back that only looks plausible, so this refuses outright rather than warning: T-212." — die
  Zahlen fliessen laut eigenem Kopf-Docstring in die AK-160/AK-161-Entscheidung von `UI_SPEC.md`.
- **`measure_picker_cards.py`**: "This script's figures are the recipe behind the T-093 report
  (L-001) and feed AK-41/AK-51, so a wrong number here does not stay in a terminal -- it becomes
  a spec value. Refusing outright, not warning: T-212." — laut eigenem Kopf-Docstring dieselbe
  Klasse Folgenutzung.

Beide Begruendungen folgen der Vorgabe woertlich: "Ein Messskript, dessen Zahlen in eine Vorgabe
wandern, sollte verweigern." Keines der beiden Skripte ist eine reine Momentaufnahme fuer einen
Menschen — beide sind explizit als Rezept fuer eine Spezifikationsentscheidung dokumentiert.

Ich habe **keinen** Override-Schalter eingebaut (etwa eine Umgebungsvariable, die die Verweigerung
umgeht): die einzige harte Vorgabe des Auftrags ist "kein Skript darf schweigend falsch messen",
und ein Override waere genau die Tuer dafuer. Wer geometrisch auf `offscreen` messen will, kann
das Skript weiterhin lesen und die Zeile von Hand entfernen — das ist eine bewusste, sichtbare
Handlung und kein Standardpfad mehr.

## 3. Laeufe vorher/nachher, mit Kommando

Fuer beide Skripte gebraucht: ein aktueller Datensnapshot (Details Abschnitt 5) unter einem
umgelenkten `LOCALAPPDATA`/`APPDATA`/`NIGHTREIGN_SETTINGS_ORG` (T-212-eigener Wert), sowie
`PYTHONPATH` auf die Repo-Wurzel fuer die "vorher"-Kopien (die aus dem Scratchpad liefen).

### `measure_advisor_block.py`

**Vorher** (Stand vor dieser Aenderung, `git show HEAD:scripts/measure_advisor_block.py` in eine
Scratch-Kopie geschrieben), **kein** `QT_QPA_PLATFORM` gesetzt → das Skript setzt es selbst
schweigend auf `offscreen`:

```
python <scratch>/measure_advisor_block.before.py
```
```
platform 'offscreen', style 'fusion', ... screen 800x800 logical px
  window 1320x900 logical px, middle column 468 px, cards 565 px
  horizontal scroll in the middle column: 0..117 px with the blocks, 0..103 px with no suggestion drawn
```

**Vorher, mit `QT_QPA_PLATFORM=windows` von aussen erzwungen** (dieselbe Skriptfassung, echtes
Fenster) — die Referenzzahl:

```
QT_QPA_PLATFORM=windows python <scratch>/measure_advisor_block.before.py
```
```
platform 'windows', style 'fusion', ... device pixel ratio 1.25, screen 4096x1728 logical px
  window 1320x900 logical px, middle column 468 px, cards 448 px
  horizontal scroll in the middle column: 0..0 px with the blocks, 0..0 px with no suggestion drawn
```

**565 px gegen 448 px, und offscreen behauptet 117 px Scrollbedarf, wo real keiner besteht (0..0)**
— exakt die Klasse Fehlmessung, die L-009 benennt, unabhaengig reproduziert von T-199s Zahlen.

**Nachher** (aktueller Stand), `QT_QPA_PLATFORM=offscreen` **explizit angefordert** → verweigert:

```
QT_QPA_PLATFORM=offscreen python scripts/measure_advisor_block.py
```
```
refusing to measure geometry on the 'offscreen' Qt platform (L-009): its font metrics differ
from a real, shown window, and the widths and heights this script prints feed UI_SPEC.md
decisions (AK-160/AK-161). Run this on a machine with a real display and without
QT_QPA_PLATFORM=offscreen set.
```
Exitcode 1.

**Nachher, kein `QT_QPA_PLATFORM` gesetzt** → laeuft jetzt automatisch auf der echten Plattform
und trifft exakt die "vorher, erzwungen echt"-Zahl:

```
python scripts/measure_advisor_block.py
```
```
platform 'windows', style 'fusion', ... screen 4096x1728 logical px
  window 1320x900 logical px, middle column 468 px, cards 448 px
  horizontal scroll in the middle column: 0..0 px with the blocks, 0..0 px with no suggestion drawn
```

### `measure_picker_cards.py`

**Vorher**, kein `QT_QPA_PLATFORM` gesetzt → schweigend offscreen:

```
python <scratch>/measure_picker_cards.before.py
```
```
platform Windows-11-..., Qt plugin offscreen, style fusion, logical px
card 190 x 278, minimum width 184
whole card rows visible: 1
AK-51 asks for 1203 px; this desktop offers 800
```

**278 px Kartenhoehe** — deckungsgleich mit T-199s eigenem Fund ("278/271/278 px offscreen").

**Vorher, `QT_QPA_PLATFORM=windows` erzwungen**:

```
QT_QPA_PLATFORM=windows python <scratch>/measure_picker_cards.before.py
```
```
platform Windows-11-..., Qt plugin windows, style fusion, logical px
card 190 x 228, minimum width 146
whole card rows visible: 3
AK-51 asks for 1121 px; this desktop offers 1728
```

**228 px** — deckungsgleich mit T-199s "echten" 228 px. Offscreen behauptet zusaetzlich nur eine
sichtbare Kartenzeile statt drei, weil der falsche 800x800-Desktop das Fenster kappt.

**Nachher**, `QT_QPA_PLATFORM=offscreen` explizit angefordert → verweigert:

```
QT_QPA_PLATFORM=offscreen python scripts/measure_picker_cards.py
```
```
refusing to measure geometry on the 'offscreen' Qt platform (L-009): its font metrics differ
from a real, shown window, and the widths and heights this script prints feed the T-093 report
and AK-41/AK-51. Run this on a machine with a real display and without QT_QPA_PLATFORM=offscreen
set.
```
Exitcode 1.

**Nachher**, kein `QT_QPA_PLATFORM` gesetzt → laeuft echt, trifft die "vorher, erzwungen echt"-Zahl:

```
python scripts/measure_picker_cards.py
```
```
platform Windows-11-..., Qt plugin windows, style fusion, logical px
card 190 x 228, minimum width 146
whole card rows visible: 3
AK-51 asks for 1121 px; this desktop offers 1728
```

## 4. Suitezahl

Ausgangswert laut Auftrag: `1781 passed, 9 skipped`.

```
python -m pytest -n auto -q
```
```
1789 passed, 9 skipped in 132.53s (0:02:12)
```

**Differenz von 8 erklaert sich vollstaendig durch eine unveraendert gebliebene, nicht von mir
erzeugte Datei:** `tests/test_findings_tables.py` ist im Arbeitsbaum **untracked** (`git status`
zeigte sie schon vor meiner ersten Aenderung) und gehoert laut Retrospektive (T-209, NH-003-
Vorschlag) zu einer parallel laufenden Arbeit, nicht zu T-212. `pytest
tests/test_findings_tables.py -q --collect-only` zaehlt genau **8** parametrisierte Faelle. `0
failed` in meinem Lauf, keine neue Datei von mir unter `tests/`. Ich habe diese Datei nicht
angefasst — sie liegt ausserhalb meines Scopes (T-211 laut Auftrag disjunkt) und ich melde sie
nur der Vollstaendigkeit halber, damit die Differenz nicht unerklaert stehen bleibt.

## 5. Wie ich gemessen habe, ohne echte Daten zu gefaehrden

Der feste Testabzug existiert laut `CLAUDE.md` nicht (QA-231). Der echte Cache des Nutzers
(`%LOCALAPPDATA%\NightreignHelper\nightreign_data.json`, 24.08.) ist aelter als `EXTRACT_VERSION`
9: `Planner(data)` wirft beim Bau des Arsenal-Tabs `KeyError` auf `catalyst_scaling`, bevor
ueberhaupt ein Fenster entsteht — reproduziert, betrifft beide Skripte unabhaengig von
Offscreen/Windows. `firstrun.run(gamepath.resolve_game())` (das Rezept aus T-199) scheitert in
dieser Git-Bash-Umgebung mit Exitcode 127 ohne Python-Traceback — nicht weiter untersucht, ausser-
halb des Auftrags, vermutlich ein externes Werkzeug in der Extraktionspipeline, das das PATH von
Git Bash nicht findet.

Stattdessen **in-process**, genau der Weg, den `tests/conftest.py::_snapshot_from_game` fuer die
Suite selbst nimmt: `nrdata.extract.build(game, defs)`, rein lesend gegen die installierte
Spielinstallation, ~34 s, kein Subprozess. Ergebnis in einem eigenen, umgelenkten `LOCALAPPDATA`
(`NIGHTREIGN_SETTINGS_ORG=DankYeeterT-212`, eigenes Scratch-Verzeichnis fuer `LOCALAPPDATA` und
`APPDATA`) abgelegt: `data_version 10350000`, `extract_version 11` — der in `CLAUDE.md` genannte
Sollwert. Nach den Laeufen: Test-Registry-Schluessel `HKCU:\Software\DankYeeterT-212` entfernt,
`HKCU:\Software\DankYeeter` (echt) gegengeprueft und unberuehrt; kein Eintrag im echten
Startmenue (`%APPDATA%\...\Nightreign Helper.lnk` → `Test-Path` `False`); Scratchpad geloescht.
Rezept als Memory-Eintrag festgehalten (`reference_frischer_snapshot_fuer_fenstermessungen.md`),
da es beim naechsten Mal wieder gebraucht wird.

## An director — zwei Funde ausserhalb des Auftrags, nicht behoben

1. **`measure_advisor_block.py` und `measure_picker_cards.py` setzen
   `NIGHTREIGN_SETTINGS_ORG`/`NIGHTREIGN_SETTINGS_APP` nicht selbst** — anders als
   `capture_weapon_damage.py` und `scripts/differential/capture.py`, die das tun. Ohne
   Umlenkung von aussen schreibt ein `Planner`, den eines der beiden Skripte baut (Favoriten
   ueber `QSettings`), in den echten `DankYeeter`-Registryzweig des Nutzers. Ich habe das fuer
   meine eigenen Laeufe von aussen umgelenkt, aber die Skripte selbst tragen die Umlenkung nicht
   — ein Lauf ohne dieses Wissen wuerde in die echten Einstellungen schreiben. Ausserhalb des
   Auftrags (der nennt nur den Offscreen-Punkt), daher nicht selbst gefixt.
2. **Der echte, vom Nutzer gepflegte Cache ist aelter als `EXTRACT_VERSION` 9** und laesst
   keinen vollen `Planner` mehr bauen (`KeyError` auf `catalyst_scaling`). Das ist derselbe
   Themenkreis wie QA-231 (fehlender fester Testabzug), aber am **Nutzer-eigenen** Cache, nicht
   nur am Testabzug — ein Befund fuer `qa-engineer`/`director`, ob das gemeldet werden soll.
3. **`firstrun.run` schlaegt in Git Bash mit Exitcode 127 fehl** (kein Traceback). Reine
   Beobachtung dieser einen Umgebung, nicht untersucht — falls andere Rollen `firstrun.run` aus
   Git Bash heraus fuer Messlaeufe nutzen wollen (wie T-199 es aus einer anderen Shell tat),
   koennte das dieselbe Falle treffen.

## DoD

- [x] Anforderung verstanden; eigene Zaehlung (2 statt 3) explizit begruendet und dokumentiert
- [x] Suite gruen, `1789 passed, 9 skipped, 0 failed` gegen Ausgangswert `1781 passed, 9 skipped`
      — Differenz erklaert (Abschnitt 4), Windows das einzige geprueft Zielsystem
- [x] Kein Linter im Projekt konfiguriert → Punkt entfaellt
- [x] Kein Anwendungscode unter `nrplanner/`/`nrdata/` geaendert, kein neuer Test, kein Waechter,
      `tests/conftest.py` und `tests/test_tab_geometry.py` unberuehrt, `mutate.py` unberuehrt
- [x] Keine Secrets, keine TODOs, kein toter Code
- [x] Beide Entscheidungen (verweigern/verweigern) selbst durchgespielt mit Vorher/Nachher-Lauf
- [x] Bericht geschrieben; `docs/state.md`/`GOAL.md`/`qa/findings.md` fasse ich nicht an

Nicht geprueft: Linux/macOS (kein Ziel dieses Projekts).
