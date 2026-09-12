# T-083 - S10a: die Advisor bar und der Anschluss des Controllers (developer)

```
STATUS: teilweise
AUFTRAG: T-083 - S10a: die Advisor bar und der Anschluss des Controllers
GELESEN: docs/tasks/T-083.md; UI_SPEC.md (§3.1 Z.92-140, §4 Z.223-251, §5
  Z.253-282, §6/§7 Z.284-330, AK Z.329-402 und Z.1070-1090, §3.7 Z.815-822,
  §5 T-080-Revision Z.3410-3440); nrplanner/advisor/worker.py,
  types.py, run.py, goals.py, candidates.py (Signaturen);
  nrplanner/app.py (__init__, _build_left, _build_middle, _build_right,
  showEvent, rescan_save, load_equipped, active_slots, recompute);
  nrplanner/firstrun.py (Fortschrittsbalken); tests/conftest.py,
  tests/rendered.py, tests/advisor_cases.py;
  scripts/measure_advisor_worker.py; .gitattributes; pytest.ini
GEÄNDERT: nrplanner/advisorbar.py (neu), nrplanner/app.py,
  tests/test_advisor_bar.py (neu), docs/berichte/T-083-developer.md (diese
  Datei). Commit 775173c. Zusaetzlich beruehrt und im selben Zustand wie
  vorher zurueckgegeben: nrplanner/advisor/worker.py - der Mutationstreiber
  schreibt die Datei fuer M2 und stellt sie wieder her; die
  Zeilenenden habe ich danach von Hand auf LF zurueckgesetzt,
  `git diff --numstat` zeigt fuer die Datei nichts.
ANNAHMEN: (1) Ein fertiger Lauf erreicht 4.6/4.9/4.11 - der Auftrag zaehlt
  diese Zustaende nicht zu den "erreichbaren", aber ein abgeschlossener Lauf
  muss etwas sagen. (2) `Apply all`, `Undo apply` und `Why` sind **nicht**
  gebaut (Begruendung unten); `Clear` ist gebaut, weil es hier vollstaendig
  wirkt. (3) Bei 4.9 und 4.11 zugleich gewinnt 4.11. (4) Der Plural von 4.11
  ist mechanisch gebildet. (5) Ein Vorschlag, der seinen Build ueberlebt,
  faellt auf 4.1 zurueck - §4 hat keine Zeile dafuer. (6) Die Zahl "292
  relics" in 4.4 ist `owned.relic_count`, die Zahl der Slots die des
  Problems.
NÄCHSTER: director
BLOCKIERT DURCH: nichts fuer die gebaute Leiste. Offen bleibt **4.10/AK-20**:
  im Berater gibt es nichts, das "dieses Ziel ist gar nicht bewertbar"
  meldet - beide Ziele liefern immer eine Zahl. Der Zustand und sein Wortlaut
  sind gebaut und einzeln geprueft, aus einem echten Lauf ist er nicht
  erreichbar. Das braucht eine Entscheidung (Feld auf `AdvisorResult` oder
  ein benanntes Kriterium), nicht Code von mir.
```

## Umgesetzt

**`nrplanner/advisorbar.py` (neu, 630 Zeilen).**

- `State` - die vierzehn Zeilen aus `UI_SPEC` §4 als benannte Zustaende, der
  Tabellennummer als Wert (`"4.1"` … `"4.13"`; 4.14 ist kein Zustand, sondern
  die Regel "nichts erzwingt Breite").
- `Situation` - Zustand plus alles, was seine Zeile braucht (Ziel-Label,
  Relikt- und Slotzahlen, Nightfarer, Grund). Wert statt Widget-Feldern.
- `status_line(situation)` - **Qt-frei**, die einzige Stelle, an der die
  Wortlaute stehen. Jede Zeile der Tabelle ist ein Fall davon und wird im
  Test woertlich gegen `UI_SPEC.md` gehalten, nicht gegen sich selbst.
- `Asking` und `asking_from(planner, goal_id)` - was das Fenster fragen
  wuerde; `None`, wenn kein Save gelesen wurde (4.8). Baut Request und
  Context aus einer Quelle, damit
  `run._refuse_a_request_that_asks_about_another_run` nicht zuschlaegt.
  **Alle Slots sind frei**, `held=()`: `Optimize` verspricht, jeden Slot zu
  fuellen; Halten ist S10b. `declared` wird sortiert (Determinismus).
  `generation` und `inventory_fingerprint` setzt die Leiste **nicht** - das
  tut `ask()`.
- `_ElidingLabel` - `Qt.PlainText`, horizontal `Ignored`, kuerzt sich in
  seinem eigenen `resizeEvent` per `QFontMetrics`, voller Text immer als
  Tooltip.
- `AdvisorBar` - `ADVISOR` (inline, `app._heading`), Zielwahl
  (`AdjustToContents`, `setMaximumWidth(200)`, Reihenfolge aus §3.1),
  `Optimize`/`Cancel` (**derselbe** Knopf), Statuszeile, `QProgressBar`
  (`setRange(0,0)`, `setTextVisible(False)`, `setFixedHeight(6)`,
  `setMinimumWidth(0)`), `Clear`. Signale fuer S10b:
  `suggestion_changed(object)`, `apply_all_requested`,
  `undo_apply_requested`, `why_requested`.
- Zwei Uhren, ausdruecklich getrennt: `WAIT_VISIBLE_MS = 250` (ab
  **Beginn des Laufs**, 4.2 gegen 4.3) und `FIGURES_VISIBLE_MS = 3000` (4.4).
  Keine Ableitung aus `worker.DEBOUNCE_MS`, das dieselbe Zahl traegt und
  etwas anderes misst.

**`nrplanner/app.py`** - vier Stellen:

1. Import von `AdvisorBar`/`asking_from`.
2. `_build_middle`: die mittlere Spalte ist jetzt ein `QWidget` mit drei
   Stuecken - der nicht scrollende Block (Ueberschrift, Vessel-Streifen,
   Build-Zeile), die Advisor bar, und die `QScrollArea` mit Hinweistext und
   Slots. Beide oberen Stuecke horizontal `QSizePolicy.Ignored` (siehe
   AK-03 unten).
3. `rescan_save` und `load_equipped`: `the_data_is_changing()` als **erste**
   Zeile, vor dem Austausch des Bestands (AD-006.7).
4. `recompute`: `the_build_changed()` (AK-12); die Baustellen-Wache am Anfang
   fragt jetzt zusaetzlich nach `advisor_bar`, weil der Level-Slider in der
   linken und die Leiste in der mittleren Spalte entsteht.
5. Neuer `closeEvent`: `advisor_bar.shutdown()`.

**`RelicSlot` (app.py:543-1097) ist unberuehrt.** `git diff` des Commits
zeigt in app.py nur die fuenf genannten Stellen.

## Zwei Entscheidungen, die der Director kennen muss

### 1. Die Leiste steht in der Spalte, aber der Block darueber musste mit heraus

`UI_SPEC` §3.1/AK-02 verlangt die Leiste **zwischen** der Build-Zeile und dem
Hinweistext und **ausserhalb** der `QScrollArea`. Beides zugleich geht nur,
wenn alles oberhalb der Leiste die Scrollflaeche ebenfalls verlaesst - sonst
wuerde die Build-Zeile unter einer festgenagelten Leiste wegscrollen.

Folge, die nicht in der Spec steht und die der `ui-ux-designer` sehen sollte:
**Vessel-Streifen und Build-Zeile scrollen nicht mehr mit**, sie stehen
dauerhaft. Nur die Slots scrollen.

### 2. Die zwei herausgezogenen Bloecke fordern horizontal nichts an

Gemessen (Skript `measure_pages.py`, unten):

| Plattform | Fensterboden HEAD vorher | Build-planner-Seite | Build-Zeile allein | Leiste (Ruhe) |
|---|---|---|---|---|
| offscreen | 988 x 508 | 756 | 616 | 414 |
| windows | 760 x 547 | 756 | 382 | 310 |

Unter der Windows-Plattform **ist** der Fensterboden die Build-planner-Seite
(760 gegen 756 + Rahmen). Jedes Pixel Mindestbreite ausserhalb der
Scrollflaeche schlaegt dort eins zu eins durch: der herausgezogene Block
haette +314 px gekostet, die Leiste allein +242. AK-03 verbietet das
("nicht groesser als auf 3da8428"). Deshalb tragen beide
`QSizePolicy.Ignored` horizontal - dieselbe Technik, die §3.1 fuer die
Statuszeile vorschreibt, eine Ebene hoeher.

**Preis, ausdruecklich benannt:** unterhalb von ~382 px Spaltenbreite
(Windows-Plattform) wird die Build-Zeile jetzt abgeschnitten statt per
horizontaler Bildlaufleiste erreichbar zu bleiben. Bei der Startbreite 1320
px hat die mittlere Spalte ein Vielfaches davon; erreichbar ist der Fall nur
am Fensterboden, wo die Spalte 68 px bekommt und auch heute niemand etwas
lesen kann. Wenn der `ui-ux-designer` das anders will, ist die Alternative
eine zweite Scrollflaeche fuer den oberen Block - mehr Mechanik fuer denselben
Anblick.

## AK-03 und AK-04 gegen 3da8428

Gemessen **vor dem ersten `show()`**, gleiche Umgebung, UI scale Automatic,
Fusion + dunkle Palette wie `apply_appearance`, Snapshot
`%LOCALAPPDATA%\NightreignHelper\nightreign_data.json`. Skript:
`scratchpad/measure_floor.py` (nicht committet, Inhalt unten zitiert).

| Baum | offscreen | windows |
|---|---|---|
| 3da8428 | 964 x 977 | 760 x 1033 |
| HEAD vor T-083 (fd9f2bc) | 988 x 508 | 760 x 547 |
| **HEAD mit T-083 (775173c)** | **988 x 508** | **760 x 547** |

- **AK-03 durch diese Aenderung erfuellt: 0 px Zuwachs** auf beiden
  Plattformen.
- **Befund, nicht von mir:** offscreen liegt der Boden schon vor diesem
  Auftrag 24 px ueber 3da8428 (988 gegen 964) - das setzt die Seite
  "Effects & chances" (984), nicht der Build planner (756). Unter der
  Windows-Plattform sind beide Staende gleich (760). Wer AK-03 woertlich
  gegen 3da8428 abnimmt, muss wissen, auf welcher Plattform er misst.
- **AK-04 erfuellt: 0 px Zuwachs** der Mindesthoehe (508 bzw. 547
  unveraendert; gegen 3da8428 ist sie sogar um 469 bzw. 486 px gefallen).
  Die Leiste selbst: `sizeHint().height()` = 34 px offscreen, 36 px unter
  der Windows-Plattform; Inhaltshoehe ohne die 6+6 px Rand: **22 bzw. 24 px**
  gegen die 32 px, die §3.1 erlaubt.

## Tests

`tests/test_advisor_bar.py` (neu), 46 Faelle, zwei Haelften:

- **Wortlaute:** 13 Faelle, je eine Zeile der Tabelle 4.1-4.13, Literale aus
  `UI_SPEC.md` - einschliesslich der Auslassungspunkte, der Geviertstriche
  und des Mittelpunkts mit doppeltem Abstand. Dazu: nur der erste Buchstabe
  des Ziels wird klein geschrieben; ein Zustand ohne Zeile ist laut
  (`KeyError`); die beiden Schwellen 250/3000 als Zahlen gegen die Spec.
- **Zustandsautomat** an einem Controller des Tests (die vier Signale des
  echten, von Hand ausgeloest): 4.1 mit Tooltip, 4.8 mit den zwei
  abgeschalteten Bedienelementen, AK-09, AK-10, 4.4, die **Folge**
  4.1 → 4.3 → 4.5 → 4.1, die **Folge** 4.3 → 4.7, ein Vorschlag der seinen
  Build ueberlebt, 4.11 vor 4.9, 4.9, `Clear`, 4.12, Maskierung, ein
  Zielwechsel, AK-07, AD-006.7, `shutdown`, und dass eine lange Statuszeile
  der Leiste keine Breite gibt.
- **Im echten Fenster** (`planner`-Fixture, echter `AdvisorController`,
  echter Save): AK-02 (Reihenfolge der Spalte, was in der Scrollflaeche
  liegt, und dass die Leiste beim Scrollen stehen bleibt), AK-03 als
  Relation, AK-04 als Budget, AK-05 bei 1320 px, **AK-13 + AK-08** an einem
  echten Lauf, **AK-11** gemessen, und die vier Anschlussstellen in `app.py`
  (Level, `rescan_save`, `load_equipped`, `closeEvent`).

Der Fall `test_a_real_optimize_answers_and_changes_no_slot` ist der wichtigste
der Datei: er zeigt, dass der vom Fenster gebaute Request von `run.run`
**angenommen** wird. Ein Feld, das den Lauf daneben nicht beschreibt, kaeme
als 4.12 zurueck.

### Rot-vorher: 16 Gegenbauten, 15 toeten

Treiber: `scratchpad/mutate.py` (nicht committet), je Mutation ein frischer
`pytest`-Lauf mit `PYTHONDONTWRITEBYTECODE=1`.

| # | Aenderung | Fall | Ergebnis |
|---|---|---|---|
| M1 | `WAIT_VISIBLE_MS = 0` | AK-09 | KILLED |
| M2 | `worker.DEBOUNCE_MS = 0` | AK-09 | **SURVIVED** (Begruendung unten) |
| M3 | `WAIT_VISIBLE_MS = 10000` | AK-10 | KILLED |
| M4 | Fortschrittsbalken auch in 4.2 | AK-09 | KILLED |
| M5 | `Ignored` vom oberen Block genommen | AK-03 | KILLED |
| M6 | `Ignored` von der Leiste genommen | AK-03 | KILLED |
| M7 | Grund des Abbruchs nicht mitgegeben | 4.7 | KILLED |
| M8 | leerer Slot verliert gegen Stille | 4.11 | KILLED |
| M9 | Tooltip ohne `html.escape` | Maskierung | KILLED |
| M10 | ein Wort aus 4.5 | Tabelle | KILLED |
| M11 | Antwort ueberlebt ihren Build | AK-12 | KILLED |
| M12 | `the_data_is_changing` aus `rescan_save` | AD-006.7 | KILLED |
| M13 | `the_build_changed` aus `recompute` | AK-12 | KILLED |
| M14 | `shutdown` aus `closeEvent` | Abschalten | KILLED |
| M15 | `Ignored` von der Statuszeile genommen | Breite | KILLED |
| M16 | 4.4-Uhr nicht gestartet | 4.4 | KILLED |

**M2 ueberlebt, und das ist die richtige Antwort auf die Frage der Abnahme.**
Der Auftrag verlangt zu zeigen, dass der Fall "kein Aufblitzen" rot wird,
wenn die Entprellung auf 0 gesetzt wird. Er wird es nicht, und zwar weil das
Aufblitzen keine Eigenschaft der Entprellung ist: 4.2 ist ein Zustand der
**Rechnung** ("Rechnet, < 250 ms"), also laeuft die Uhr der Leiste ab
`started` und nicht ab dem Klick. Mit Entprellung 0 beginnt der Lauf frueher,
dauert aber unveraendert weniger als 250 ms - es blitzt weiterhin nichts auf.
Die Mutation, die den Fall toetet, ist M1: die Schwelle der Leiste selbst.
Waere die Uhr am Klick festgemacht, wuerden Entprellung und Schwelle sich
ueberlappen und die Anzeige waere **mitten im Lauf** aufgeblitzt - genau der
Fehler, den AK-09 verbietet.

**Zwei Fallen, die der Lauf gefunden hat und die Review nicht gefunden hatte**
(beide vor dem Commit behoben):

- Der AK-10-Fall wartete `advisorbar.WAIT_VISIBLE_MS + 120` ms - er nahm
  seine Erwartung also aus der Stelle, die er bewacht, und blieb bei einer
  Schwelle von 10 s gruen (M3). Jetzt wartet er 370 ms als Literal (250 aus
  `UI_SPEC` 4.3 + 120 ms fuer die Ereignisschleife).
- Der Breitenfall deckte die Statuszeile nicht ab: weil schon die **Leiste**
  `Ignored` ist, aendert das Wegnehmen der Politik an der Statuszeile am
  Spaltenboden nichts (M15 ueberlebte). Dafuer gibt es jetzt einen eigenen
  Fall, der die Eigenschaft prueft: eine sehr lange Statuszeile darf die
  Mindestbreite der Leiste nicht bewegen.

Der erste Kampagnenlauf meldete zusaetzlich M9 als ueberlebend; das war der
Treiber, nicht der Test - zwei Schreibvorgaenge in derselben Sekunde liessen
Python eine veraltete `.pyc` laden. Mit `PYTHONDONTWRITEBYTECODE=1`
reproduziert das nicht mehr, und M9 toetet.

### Zweite Stichprobe: die Zustaende in Folge

Wie die Abnahme verlangt, nicht nur einzeln:

- `test_the_sequence_rest_working_stopped_rest`: 4.1 → 4.3 → 4.5 → 4.1, mit
  Pruefung, dass Fortschrittsbalken und `Cancel`-Beschriftung in jedem
  Schritt mitgehen.
- `test_a_build_that_changes_under_a_run_ends_in_4_7_and_not_in_4_5`:
  4.3 → 4.7 beim Wechsel waehrend der Rechnung, ausdruecklich gegen die
  Verwechslung mit 4.5 (beide kommen durch dasselbe `stopped`-Signal).
- Ein echter Lauf am echten Save (Skript `one_real_run.py`): 309 Relikte,
  drei Slots, **473 ms vom Klick bis zur Antwort** (250 ms Entprellung + ~220
  ms Suche), Zustaende `4.1 → 4.2 → 4.9`, Zeile
  `Maximise damage — 3 of 3 slots filled  ·  some effects carry no numbers.`
  Der Lauf blieb unter der Schwelle, es blitzte nichts auf - AK-09 am echten
  Fall.

## Maskierung: die Eigenschaft, nicht die Fundstelle (D-10, L-006)

Zwei unabhaengige Suchmasken ueber `nrplanner/`:

1. Widget-Konstruktoren (`QLabel|QPushButton|QComboBox|QProgressBar\(`) in
   der neuen Datei: **4 Treffer** - `goal_box`, `optimize_button`,
   `progress`, `clear_button` (die Statuszeile ist eine Unterklasse und
   erscheint nur in Maske 2).
2. Alles, was Text in ein Widget schreibt (`setText|setToolTip|addItem`):
   **6 Treffer** - der Tooltip der Statuszeile, ihr `setText`, die zwei
   Ziel-Eintraege, die zwei festen Tooltips, die `Cancel`-Beschriftung.

Beide Masken kommen auf dieselbe Aussage: **genau eine** neue Beschriftung
zeigt Fremdtext - die Statuszeile (Nightfarer-Name in 4.10, Fehlergrund in
4.12). Sie traegt `setTextFormat(Qt.PlainText)`, ihr Tooltip laeuft durch
`html.escape`. Die Ziel-Labels kommen aus der Registry (`goals.py`), nicht
aus Spieldaten. `grep -rn setTextFormat nrplanner/` zeigt 6 Stellen im ganzen
Programm, davon eine neue - meine.

**Nebenbefund an der Tooltip-Maskierung (nicht von mir, nicht behoben):** ein
Tooltip hat kein `setTextFormat`, Qt entscheidet selbst. `Qt::mightBeRichText`
erkennt `&lt;`, aber **nicht** `&amp;`. `html.escape` allein ist deshalb in
beide Richtungen falsch: ein `&` im Text erscheint als `&amp;`. Ich habe fuer
meine Statuszeile deshalb `<span>` + `html.escape` gewaehlt (Test
`test_foreign_text_in_a_reason_reaches_the_label_as_text`, Mutation M9).
`nrplanner/app.py:3294` (`owned_label.setToolTip(html.escape(folder))`) hat
den Wrapper nicht - ein Save-Ordner mit `&` im Namen wird dort als `&amp;`
angezeigt. Kosmetisch, kein Loch; gehoert dem Director als Debt.

## Testergebnis

| Lauf | Ergebnis |
|---|---|
| vorher (Auftrag, frischer Klon) | 1059 passed, 9 skipped, 5 deselected |
| nachher, Arbeitsbaum, `-m "not slow"` | 1105 passed, 9 skipped, 5 deselected (495 s) |
| **nachher, frischer Export von 775173c** | **1105 passed, 9 skipped, 5 deselected (518 s)** |
| nachher, `-m slow` | 5 passed, 1114 deselected (57 s) |
| neue Datei unter `QT_QPA_PLATFORM=windows` | 46 passed (30 s) |

Der frische Export: `git archive HEAD | tar -x -C <scratchpad>/fresh`, dort
`pytest -m "not slow"` mit dem Python des Arbeitsbaums.

Linter: das Projekt hat keinen konfiguriert (kein flake8/ruff/pylint in
`pytest.ini`, `.github/workflows/*.yml` oder als Konfigurationsdatei) - der
Punkt entfaellt.

## Commits

- `775173c feat(advisor): die Leiste zeigt den Zustand des Beraters an`
  (`nrplanner/advisorbar.py`, `nrplanner/app.py`,
  `tests/test_advisor_bar.py`; committet mit Pfadangabe hinter `--`).

Ein Commit statt drei: die Leiste ohne ihren Anschluss ist tot, der Anschluss
ohne die Leiste ist rot. Zwischenstaende mit gruener Suite gab es dazwischen
nicht.

`UI_SPEC.md` und `ARCHITECTURE.md` sind im Arbeitsbaum geaendert - das ist
T-084, nicht ich.

## Offene Fragen

**An den `director`:**

1. **4.10/AK-20 hat keinen Erzeuger.** Weder `max_damage` noch
   `min_damage_taken` kann "gar nicht bewertbar" melden: beide liefern immer
   eine Zahl (`goals.py:196-207` faellt ohne Waffe auf Angriffsmultiplikatoren
   zurueck, `min_damage_taken` wirft bei fehlenden Kurven - das ist 4.12).
   `AdvisorResult` traegt kein Feld dafuer. Der Zustand und sein Wortlaut
   sind gebaut und geprueft, aber aus einem Lauf nicht erreichbar. AK-20
   kann heute niemand abnehmen. Entscheidung noetig: Feld auf
   `AdvisorResult` (dann ein Auftrag an den `developer` fuer `advisor/`),
   oder ein benanntes Kriterium, das die Leiste pruefen darf.
2. **`Apply all`, `Undo apply`, `Why` habe ich nicht gebaut.** Der Auftrag
   sagt, sie bleiben "ohne Wirkung und ohne Sichtbarkeit, solange kein
   Vorschlag lebt" - und ein Lauf, der fertig wird, laesst nach §3.1 einen
   Vorschlag leben. Drei sichtbare Knoepfe, die beim Klick nichts tun,
   waeren ein QA-Befund und ein halbes Feature; drei unsichtbare Knoepfe
   waeren toter Code. Deshalb: gebaut ist `Clear` (wirkt hier vollstaendig),
   die drei anderen sind je ein Signal (`apply_all_requested`,
   `undo_apply_requested`, `why_requested`) und ein Eintrag in
   `ANSWERED_STATES`/`_show`. T-085 braucht dafuer drei `QPushButton` und
   drei Zeilen in `_show`. Wenn der Director sie schon jetzt sichtbar will,
   sage ich es dazu: dann ist AK-07 zwar gemessen, aber zwei der drei
   Knoepfe tun nichts.
3. **Debt, bestehend:** `app.py:3294`, Tooltip ohne `<span>`-Wrapper (oben).
   Nicht behoben, weil ausserhalb des Auftrags.
4. **Kleinigkeit in meinem eigenen Code, bewusst so:** `_resting()` baut ein
   ganzes `Asking`, nur um zu erfahren, ob ein Save existiert - einmal je
   `recompute`, also bei jedem Zug am Level-Regler. Das sind sechs Slots und
   ein paar Tupel, keine Datensatz-Laeufe; ich habe es nicht optimiert, weil
   die Alternative ein zweiter Weg zur selben Frage waere. Wenn der
   `performance-tuner` in S11 misst, ist das die Stelle in dieser Datei, die
   ihn interessieren koennte.

**An den `ui-ux-designer` (T-084 arbeitet gerade in `UI_SPEC.md` - ich habe
die Datei nicht angefasst):**

5. **§4 hat keine Zeile fuer "ein Vorschlag hat seinen Build ueberlebt".**
   4.7 sagt "while this was working out" und passt nur, wenn noch gerechnet
   wurde. Ich falle auf 4.1 zurueck (der Vorschlag wird verworfen, danach ist
   "Nothing suggested yet." wahr). Wenn das eine eigene Zeile bekommen soll,
   ist es eine Zeile in der Tabelle und drei Zeichen in `status_line`.
6. **4.9 und 4.11 koennen gleichzeitig zutreffen.** Die Tabelle gibt je einen
   Text. Ich zeige 4.11 (ein leerer Slot ist das Sichtbare). Falls die
   Leiste beide Klauseln tragen soll, braucht 4.11+4.9 einen eigenen
   Wortlaut - erfinden wollte ich ihn nicht.
7. **Der Plural von 4.11 ist ungeprueft.** Die Tabelle schreibt
   `1 slot has nothing to choose from`; bei zwei Slots schreibe ich
   `2 slots have nothing to choose from`. Das ist der Plural desselben
   Satzes, aber niemand hat ihn abgenommen.
8. **4.14 gegen §3.1 bei der Statuszeile.** §7 verlangt `setWordWrap(True)`
   fuer jede neue Beschriftung mit variablem Text, §3.1 verlangt fuer die
   Statuszeile eine Zeile mit `…`-Kuerzung und Tooltip. Ich bin §3.1
   gefolgt (die speziellere Regel); die Statuszeile bricht nicht um. Alle
   anderen neuen Beschriftungen tragen festen Text.
9. **Die Statuszeile bekommt bei 1320 px wenig Platz.** Gemessen: 158 px
   unter der Windows-Plattform, 54 px offscreen (die Schrift dort ist doppelt
   so breit). Der volle Text steht im Tooltip, aber `Working out maximise
   damage…` ist bei 158 px schon fast am Rand. Falls das stoert, ist die
   Stellschraube die Aufteilung der mittleren Spalte, nicht die Leiste.
10. **Vessel-Streifen und Build-Zeile scrollen nicht mehr** (siehe
    Entscheidung 1 oben) - der sichtbarste Nebeneffekt dieses Auftrags.

**An den `qa-engineer`:**

- Abzunehmen sind 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.11, 4.12.
  **4.10 und 4.13 sind nicht erreichbar** (4.10: kein Erzeuger, siehe oben;
  4.13: braucht `Apply all`, also T-085).
- Der Weg zu 4.3/4.4 braucht einen langsamen Lauf: am gemessenen Save (309
  Relikte, drei Slots) ist die Rechnung nach ~220 ms fertig, es erscheint
  **kein** Fortschrittsbalken. Mit Deep of Night an (sechs Slots) wird sie
  laenger; der schlechteste gemessene Fall ist ~960 ms.
- Kanten, die ich fuer interessant halte: `Optimize` zweimal schnell
  hintereinander (die Entprellung faengt es); `Optimize`, dann sofort
  Nightfarer wechseln (muss 4.7 geben, nie einen Vorschlag); `Optimize`,
  dann `Rescan save` (muss 4.5 geben und den Cache leeren); Fenster
  schliessen, waehrend gerechnet wird (darf nicht abstuerzen); kein Save
  vorhanden (4.8, Zielwahl und `Optimize` aus, **alles andere an**);
  waehrend der Rechnung Tab wechseln, Slot oeffnen, Vessel wechseln.
- Nicht geprueft, weil nicht pruefbar oder nicht meins: **AK-06** (UI scale
  150 % mit lebendem Vorschlag - T-085), **AK-17** (kein Schreiben in den
  Save, keine Netzverbindung: durch Lesen des Codes belegt, kein Test - die
  Leiste oeffnet nichts und schreibt nichts), **AK-14/15/16/18-22/24-27**
  (alle an Vorschlagsblock oder Picker).
- Beide Testlaeufe der neuen Datei sind gruen: offscreen und
  `QT_QPA_PLATFORM=windows`. Die Pixelzahlen unterscheiden sich um etwa den
  Faktor zwei; jede Zahl in diesem Bericht traegt ihre Plattform.

## Ausgefuehrte Befehle (Auszug, mit Ausgabe)

```
$ .venv\Scripts\python.exe -m pytest -m "not slow" -q      (Arbeitsbaum)
1105 passed, 9 skipped, 5 deselected in 495.73s (0:08:15)

$ git archive HEAD | tar -x -C <scratchpad>/fresh
$ cd <scratchpad>/fresh && <venv>/python.exe -m pytest -m "not slow" -q
1105 passed, 9 skipped, 5 deselected in 517.71s (0:08:37)

$ .venv\Scripts\python.exe -m pytest -m slow -q
5 passed, 1114 deselected in 57.35s

$ QT_QPA_PLATFORM=windows .venv\Scripts\python.exe -m pytest tests/test_advisor_bar.py -q
46 passed in 30.44s

$ <venv>/python.exe scratchpad/measure_floor.py <3da8428-export>
window.minimumSizeHint = 964 x 977        (offscreen)
window.minimumSizeHint = 760 x 1033       (windows)

$ <venv>/python.exe scratchpad/measure_floor.py .        (mit T-083)
window.minimumSizeHint = 988 x 508        (offscreen)
window.minimumSizeHint = 760 x 547        (windows)

$ <venv>/python.exe scratchpad/measure_bar.py .
bar sizeHint height : 34 (offscreen) / 36 (windows)
content height      : 22 (offscreen) / 24 (windows)      Budget: 32

$ <venv>/python.exe scratchpad/one_real_run.py
save: 309 relics
click to answer: 473 ms
states seen    : ['4.1', '4.2', '4.9']
status line    : 'Maximise damage — 3 of 3 slots filled  ·  some effects carry no numbers.'

$ <venv>/python.exe scratchpad/mutate.py
15 von 16 KILLED; M2 (worker.DEBOUNCE_MS = 0) SURVIVED, siehe Begruendung.
```

Die Messskripte liegen im Scratchpad und sind **nicht** committet. Sie
brauchen den Snapshot unter `%LOCALAPPDATA%\NightreignHelper` und, fuer den
echten Lauf, den Save des Nutzers - beides nur lesend.
