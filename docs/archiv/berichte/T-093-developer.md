# T-093 - S10c: der Relic Picker als Hauptweg des Beraters (developer)

```
STATUS: teilweise
AUFTRAG: T-093 - S10c: der Relic Picker als Hauptweg des Beraters
GELESEN: docs/tasks/T-093.md (ganz), UI_SPEC.md Zeilen 670-835 (T-024 §3),
  1006-1095 (AK-41 bis AK-53, AK-62), 1188-1340 (Nachtrag zu AK-47, AK-63),
  4307-4475 (T-084 §1, AK-162 bis AK-166), 5475-5500 und 5745-5765 (AK-193),
  nrplanner/relicpicker.py, nrplanner/advisorbar.py, nrplanner/app.py
  (RelicSlot, available_items, active_slots), nrplanner/cardgrid.py,
  nrplanner/advisor/{types,candidates,goals,run,evaluate}.py,
  nrplanner/damage.py (headline_label), nrplanner/model.py (label_for),
  tests/{conftest,advisor_cases,test_relic_picker_geometry,
  test_advisor_hold,test_one_dash_style,test_game_text_is_never_markup}.py,
  scripts/measure_advisor_picker.py, .claude/agent-memory/developer/*
GEAENDERT: nrplanner/relicpicker.py, nrplanner/advisorbar.py,
  tests/test_relic_picker_advisor.py (neu), tests/test_relic_picker_geometry.py,
  scripts/measure_picker_cards.py (neu), docs/berichte/T-093-developer.md
  (diese Datei). Fuenf Commits, alle auf docs/audit-and-advisor-design.
  nrplanner/app.py ist **nicht** angefasst.
ANNAHMEN: (1) `Sort by` = `Name` laesst die Zielwahl stehen und zeigt Zeile 4
  weiter - AK-62 verlangt die Pflichtzeile "in jeder Sortierung", der
  T-052-Nachtrag laesst sie "fuer Name" entfallen; die beiden widersprechen
  sich, ich bin AK-62 gefolgt (Begruendung unten). (2) Vorzeichen als ASCII
  `+`/`-` wie im ganzen uebrigen Programm, nicht als typografisches Minus der
  §3.3-Skizze. (3) Die Einheit steht am Wert, auch bei `Damage taken`
  (`effective HP`), obwohl die Skizze dort keine zeigt - A12. (4) Die
  Custom-Karte traegt keinen Wertblock. (5) `—` steht auch fuer eine Kopie,
  die der Pool nicht traegt. Alle fuenf unten je mit Begruendung.
NAECHSTER: director
BLOCKIERT DURCH: nichts - aber zwei Punkte brauchen eine Entscheidung, bevor
  die Pruefphase gegen sie testet: AK-48 (die Fluchzeile) ist **nicht**
  gebaut, weil der Auftrag das Kriterium fuer "welche Zahl misst dieses Feld"
  nicht festlegt; AK-51 (drei ganze Kartenzeilen) ist mit dem vorgegebenen
  Inhalt auf diesem Bildschirm **nicht erreichbar** (1122 px gegen 1027).
```

---

## 1. Was gebaut wurde, und warum so

### 1.1 Die Wertspalte (AK-41, AK-42, AK-45, AK-46, AK-47, AK-49)

`RelicCard` traegt einen `ValueBlock` als erste Zeile des Kartenkoerpers,
unter der Kopfzeile, ueber den Effektpunkten, abgetrennt durch eine
1-px-`QFrame.HLine` in `BORDER`. Der Block hat **immer** beide Zeilen,
`Damage` und `Damage taken`, und ist vom ersten Anstrich an da; bis Zahlen
vorliegen steht `…` an ihrer Stelle.

**Keine Zahl wird im Picker gerechnet.** `Ranking` ist eine Nachschlagehilfe
ueber einen `SlotPool`: `gain()` liefert `types.marginal_for(candidate,
goal_id)` unveraendert zurueck, indiziert nach Handle. Der Pool kommt aus
`advisor.candidates.pool` - derselbe Aufruf, den `advisor.run.run` fuer die
Beam-Suche macht, mit derselben `frozen_inventory`-Lesung.

`gain_text` rundet **zuerst** und entscheidet **danach**: ein Gewinn von 0.04
heisst `no change`, nicht `+0.0`. Damit ist AK-45 eine Eigenschaft der
Darstellung und nicht eine Zusicherung: der Chip wird auf dem **angezeigten
Text** entschieden, also tragen zwei Karten genau dann dieselbe
Kennzeichnung, wenn sie dieselbe Zahl zeigen. Der Spitzenwert wird ueber den
**ganzen Pool** gebildet, nicht ueber die gefilterte Ansicht - sonst wanderte
die Kennzeichnung mit jedem Tastendruck im Filter.

Kein Chip, wenn der Spitzenwert `no change` oder negativ ist; dann sagt es
die Kopfzeile einmal (`Nothing you own raises damage in this slot.`).

`unverified` kommt nirgends vor. Zwei unabhaengige Suchen ueber `nrplanner/`:
`grep -rin "unverified"` -> **0** Treffer, `grep -rinE "unverif|not verified"`
-> **0** Treffer. Dazu ein Fall, der die gezeichneten Labels des Dialogs
liest, und ein zweiter ueber den Quelltext (L-006).

### 1.2 `Sort by` (AK-43, AK-44, AK-52)

Drei Eintraege, die beiden Zielrichtungen mit den Beschriftungen **aus der
Registry** (`advisor_goals.GOALS[id].label`), dann `Name`.

Es gibt **eine** Zielwahl. Der Picker liest sie beim Oeffnen aus
`AdvisorBar.goal_id()` und schreibt sie ueber das neue
`AdvisorBar.choose_goal()` zurueck, das dabei dieselbe Folge zieht wie
`_goal_chosen`: die stehende Antwort war die Antwort auf die andere Frage und
geht. `choose_goal` ist still, wenn die Richtung schon steht - sonst kostete
das Oeffnen des Pickers dem Spieler eine Antwort, die er nicht verworfen hat.

Sortiert wird **stabil auf der Ordnung, die das Raster ohne Berater haette**
(Favoriten, dann Name): `sorted(items, key=worth)` auf der Liste, die
`_candidates` ohnehin liefert. Gleichstaende sind hier der Normalfall - die
Kurven sind stueckweise linear - und behalten damit die Ordnung, die der
Spieler kennt. Keine Ordnungszahl, kein Rangabzeichen; ein Fall liest jedes
Label des Dialogs und weist `1.`, `#`, `Top ` zurueck.

### 1.3 Die Zeilen ausserhalb der Scrollflaeche (AK-50, AK-62, AK-162-166)

* **Zeile 3** nennt jetzt die Bezugsgroesse:
  `… · ranked against your build with Slot 3 empty · right-click a relic to favourite it`.
* **Zeile 3b** (`self.findings`) traegt zuerst `Baseline.unknowns` der
  Zielrichtung aus `SlotPool.rank_by`, danach `SlotPool.unknowns`, mit
  `  ·  ` getrennt (`advisorbar.CLAUSES`, eine Quelle). Entfaellt ganz, wenn
  beide leer sind.
* **Zeile 4** (`self.caveats`) traegt die Pflichtzeile aus AD-018.3 und danach
  die Saetze aus `Goal.scope`, wortgleich, in Tupel-Reihenfolge. **Kein
  Vorbehaltssatz steht im UI-Code** - ein Fall haengt der Registry einen
  sechsten Satz an und findet ihn hier wieder, ohne dass eine Zeichenkette
  angefasst wurde.
* **Nichts wird verglichen, gefiltert, sortiert oder entdoppelt** (AK-165).
  Ein Fall setzt denselben Satz in beide Quellen und verlangt, dass er
  **zweimal** dasteht. Gegenprobe per Grep ueber `relicpicker.py`: die
  einzigen `sorted(`/`not in` stehen ueber Karten bzw. ueber den
  Effektfilter, keines ueber `scope`/`unknowns`/`weights_note`.
* `weights_note` kommt im Picker nicht vor (AK-166), gepruefte Zeichenkette
  `EVEN_WEIGHTING.note` gegen den gezeichneten Text.

Alle drei Zeilen liegen im Dialoglayout ausserhalb der `QScrollArea`, brechen
um (`setWordWrap(True)`), setzen `setTextFormat(Qt.PlainText)` und werden nie
gekuerzt.

### 1.4 Warten und Generationszaehler (§3.8, AD-006.3)

**Kein Warteindikator, und kein zweiter Generationszaehler.** Herleitung der
Unnoetigkeit (L-002, dritter Weg): der Pool wird synchron im Konstruktor des
**modalen** Dialogs berechnet und liegt vor, ehe der Dialog sichtbar ist.
Waehrend der Rechnung kann der Grundzustand nicht wandern, weil keine Eingabe
das Fenster erreicht; der Filter aendert nur, welche der schon bewerteten
Karten gezeigt werden, und ein Wechsel der Zielrichtung rechnet den Pool
synchron neu. Ein ueberholtes Ergebnis kann damit nicht entstehen. Die
gemessene Grundlage ist `scripts/measure_advisor_picker.py` (AD-018: ~51 ms
schlimmster Slot, gegen 250 ms aus AK-09).

## 2. Die Kartenhoehe, vor und nach dem Eintreffen der Werte

Umgebung jeder Zahl (L-009): **Windows 10, PySide6, `QT_QPA_PLATFORM=offscreen`,
Stil Fusion, UI-Skalierung Automatic, logische Pixel**, Karte auf
`CARD_WIDTH = 190` fixiert, Skript `scripts/measure_picker_cards.py`,
Commit e29ef97.

| Messung | `sizeHint().height()` | `heightForWidth(190)` |
|---|---|---|
| Karte mit `…` im Block | 173 | 197 |
| Karte mit `+1234.5 effective HP` und Chip | 173 | 197 |
| **Differenz** | **0** | **0** |
| Karte ohne Wertblock (Vergleich) | 145 | 169 |

Der Block kostet also **28 px** Kartenhoehe (Vorgabe schaetzte ~34) und
**0 px** beim Eintreffen der Werte. Der Chip liegt als leerer Streifen
fester Hoehe (13 px) im Kartenkopf neben dem Icon und kostet dort nichts,
weil das 62-px-Icon die Kopfzeile hoeher macht als Chip plus Name.

Der Block verbreitert die Karte nicht: `minimumSizeHint().width()` ist mit
und ohne Block **184**; der Block selbst fragt 138 gegen 174 verfuegbare px,
und die Zahl ist waagerecht `Ignored` (Erinnerung aus T-089: ein Kind mit
Mindestbreite schiebt **jede** Karte ueber den Sichtbereich).

## 3. Die Geometrie gegen AK-51 - **hier ist der Auftrag nicht erfuellbar**

Am Standardmass, offscreen gemessen:

* Sichtbereich **982 x 502** gegen Inhalt **982** - **keine** waagerechte
  Bildlaufleiste (AK-51, erste Bedingung: erfuellt).
* **Zwei** vollstaendige Kartenzeilen sichtbar, nicht drei.

Die zweite Bedingung ist nicht erfuellbar, und das ist keine Folge der
Wertspalte allein:

| Posten (offscreen, logische px, Dialogbreite 1024) | Hoehe |
|---|---|
| Filterzeile | 22 |
| `Sort by`-Zeile | 22 |
| Zeile 3 (umgebrochen) | 37 |
| Zeile 3b (umgebrochen, dieser Spielstand) | 89 |
| Zeile 4 (Pflichtzeile + 5 `Goal.scope`-Saetze, 738 Zeichen) | 128 |
| Raender und Abstaende | 88 |
| **Summe ueber dem Raster** | **386** |
| drei ganze Kartenzeilen (die drei ersten, je hoechste Karte) | 736 |
| **AK-51 verlangt** | **1122** |
| dieser Bildschirm gibt her (`availableGeometry`, `QT_QPA_PLATFORM=windows`, 1707 x 1027 logisch, dpr 1.5) | **1027** |

Fehlbetrag **95 px**. Breiter oeffnen hilft nicht - gemessen mit 6, 7 und 8
Spalten steigt der Bedarf auf **1148, 1213, 1213 px**, weil eine breitere
Zeile die hoechste Karte je Zeile wahrscheinlicher macht, schneller als der
Text schrumpft.

**Was ich gemacht habe:** der Dialog fragt nach dem, was AK-51 braucht, und
wird vom Schirm begrenzt (`_fit_to_three_rows`). `wanted_height()` haelt die
ungekuerzte Forderung fest, damit ein Fall sie messen kann - der
Offscreen-Schirm ist 800 px hoch, ein Fall auf der **erreichten** Hoehe waere
dort inhaltsleer (Erinnerung `window-measurement-traps` Punkt 1). Zwei Faelle:
bei `wanted_height` sind drei ganze Zeilen da und keine waagerechte Leiste;
und der Dialog oeffnet nie hoeher als der Schirm.

**Vor dieser Aenderung waren es an derselben Stelle ebenfalls nur zwei ganze
Zeilen** (720 px Standardmass, Sichtbereich 639, Zeilenhoehen 229/236/275) -
AK-51 war also schon offen, bevor der Wertblock dazukam. Die drei neuen
Zeilen und der Block vergroessern den Fehlbetrag, sie verursachen ihn nicht.

**Entscheidung des `director` noetig**, Optionen mit Folgen:
(a) AK-51 auf **zwei** ganze Zeilen aendern - kostet nichts, gibt die
Begruendung "eine Liste durch einen Briefschlitz" auf;
(b) `CARD_WIDTH`/Karteninhalt verkleinern - beruehrt jede Karte und die
Effektnamen, und AK-51 verbietet ausdruecklich das Kuerzen;
(c) Zeile 4 kuerzen - verboten durch AK-50 und AK-162;
(d) so lassen: der Picker oeffnet 1027 px hoch mit zwei ganzen Zeilen und
scrollt, die Zusage aus AK-51 steht offen. **Meine Empfehlung: (d) jetzt,
(a) als Spezifikationsaenderung** - der Fehlbetrag ist mit dem vorgegebenen
Inhalt nicht wegzurechnen, und (b) waere eine Aenderung an einem Bildschirm,
den der `ui-ux-designer` verantwortet.

## 4. Die fuenf Gegenbauten, einzeln gefahren

Jeder wurde in `nrplanner/relicpicker.py` eingesetzt, die benannten Faelle im
**Standardlauf** (`-m "not slow"`) gefahren, danach der Stand wortgleich
zurueckgeschrieben (Pruefung: Datei identisch).

| # | Gegenbau | Fall | Ergebnis |
|---|---|---|---|
| 1 | Der Wertblock wird erst gebaut, wenn `show_values` gerufen wird | `test_a_card_is_the_same_height_before_the_figures_and_after` | **rot**: `(158, 197)` gegen `(130, 169)` |
| 2 | `Ranking.texts_for` liefert nur die sortierte Zielrichtung | `test_both_directions_stand_on_every_card`, `..._in_name_order` | **rot** (2 Faelle): zweite Zeile bleibt auf `…` |
| 3 | `marked = best is not None` (Chip auch bei `no change`) | `test_nothing_is_marked_best_when_the_best_is_no_change`, `..._is_negative` | **rot** (2 Faelle): 2 bzw. 1 Karte tragen den Chip |
| 4a | `_sort_chosen` schreibt die Richtung nicht zurueck | `test_choosing_a_direction_in_the_picker_moves_the_one_setting` | **rot**: `[] != ['min_damage_taken']` |
| 4b | `Sort by` oeffnet immer auf `GOAL_ORDER[0]` | `test_the_bar_decides_what_sort_by_opens_on` | **rot**: `'max_damage' != 'min_damage_taken'` |
| 5 | `Ranking.gain` rundet auf 6 Nachkommastellen | `test_the_figure_on_a_card_is_the_pools_own_float` | **rot**: `0x1.26e978d4fdf3bp+2` gegen `0x1.26e978d4fdf38p+2` |

Zu **4**: der Auftrag verlangt die Kopplung in **beide** Richtungen, deshalb
zwei Gegenbauten und zwei Faelle - Leiste -> Picker (4b) und Picker -> Leiste
(4a).

Zu **5**: die Abweichung ist `4.6035000000000004` gegen `4.603500000000000`,
also rund **1e-15** - vier Groessenordnungen unter der angezeigten Genauigkeit
von 0.1. Der Fall prueft damit die Gleichheit und nicht die Anzeige.

**Ein Gegenbau hat unterwegs ueberlebt und das ist ein Befund ueber meine
eigene erste Fassung** (L-008c): Gegenbau 1 blieb gegen den urspruenglichen
Hoehenfall **gruen**. Gemessen: der `sizeHint` des Blocks ging von 3 px auf
31, und die Karte meldete beide Male 169 px - die Layout-Zwischenspeicher
werden von einer Layout-Anforderung geleert, die ohne Ereignisschleife
niemand zustellt, und jedes Layout der Karte von Hand zu entwerten
(`invalidate()` ueber `findChildren(QLayout)` plus `activate()`) hat sie
ebenfalls nicht geleert. Der Fall misst jetzt **zwei** Karten desselben
Relikts - eine wartende und eine gefuellte -, jede genau einmal, und an
**beiden** Massen (`sizeHint` sieht ein hinzugekommenes Widget,
`heightForWidth` sieht einen zusaetzlichen Zeilenumbruch). Danach toetet der
Gegenbau. Commit 0b0197e.

## 5. Bitgleichheit, Pruefpunkt 15

Der Beleg ist `test_the_figure_on_a_card_is_the_pools_own_float`: er nimmt
den **echten** Pool (`relicpicker.advice_for(slot).ranking("max_damage")`) und
vergleicht fuer jede Kandidatenkopie und **beide** Zielrichtungen
`Ranking.gain(item, goal).hex()` gegen `types.marginal_for(candidate,
goal).hex()`. `float.hex()` und nicht `==` oder eine gerundete Zeichenkette:
verglichen wird die Bitfolge.

Der Weg dorthin ist der Grund, warum die Gleichheit gilt und nicht nur
gemessen ist: der Picker ruft `advisor.candidates.pool(...)` mit derselben
`run.frozen_inventory`-Lesung, demselben `GoalContext` aus
`advisorbar.asking_from` und derselben `goals.GOALS`, die `advisor.run.run`
benutzt. Es gibt im Picker keine zweite Subtraktion und keinen zweiten
Aufruf von `goal.score`.

## 6. Zweite Stichprobe: beide Slotarten, zwei Nightfarer

Offscreen, Fusion, logische px, Deep of Night eingeschaltet
(`scripts/measure_picker_cards.py`):

| Nightfarer / Slot | Karten | Kandidaten | Karten mit Chip | erste drei Wertzeilen |
|---|---|---|---|---|
| Wylder, Slot 1 | 54 | 54 | 1 | `+4.6 AR` / `no change`, `+3.1 AR` / `no change`, `+3.1 AR` / `+60.0 effective HP` |
| Wylder, Deep Slot 1 | 27 | 27 | **2** | `+5.9 AR` / `no change`, `+5.9 AR` / `no change`, `+3.3 AR` / `no change` |
| Guardian, Slot 1 | 51 | **52** | 1 | `+8.2 AR` / `-20.0 effective HP`, `+3.7 AR` / `no change`, `+3.2 AR` / `no change` |
| Guardian, Deep Slot | - | - | - | dieses Gefaess hat keinen Deep-Slot |

Drei Dinge daran sind der Bericht wert:

1. **Der Gleichstand ist real**, nicht konstruiert: Wylder Deep Slot 1 hat
   zwei Karten mit `+5.9 AR`, und beide tragen den Chip. Genau die Aussage,
   die §3.5 verlangt.
2. **`no change` ist der haeufigste Wert** in der Ueberlebensrichtung, wie
   §3.3 es vorhersagt.
3. **51 Karten gegen 52 Kandidaten** bei Guardian: die eine Differenz ist die
   zweite Kopie einer Rolle, die `favourites.distinct` im Raster zu einer
   Karte zusammenfasst, waehrend der Pool Kopien zaehlt (AD-013). Kein Fehler
   dieses Auftrags, aber es heisst: **eine Kopie im Pool hat keine Karte**.
   Sichtbar wird das nur, wenn beide Kopien verschiedene Werte haetten - was
   sie bei identischer Rolle nicht koennen. Ich melde es, damit die QA nicht
   danach sucht.

Der Nightfarer an Index 1 ist auf diesem Spielstand **Guardian**, nicht
Ironeye; sein Standardgefaess hat keinen Deep-Slot, deshalb steht die vierte
Zeile leer. Die Deep-Seite ist damit nur an **einem** Nightfarer gemessen.

## 7. Commits

| Commit | Inhalt |
|---|---|
| `6aa9a63` | `feat(picker)`: Wertspalte, Chip, `no change`, `—`, Kopfzeilenfaelle, `_fit_to_three_rows`, `advisorbar.held_slot` oeffentlich |
| `0c2b42e` | `feat(picker)`: `Sort by`, `AdvisorBar.choose_goal`, stabile Wertordnung, Tab-Reihenfolge |
| `dd91895` | `feat(picker)`: Bezugsgroesse in Zeile 3, Zeile 3b, Zeile 4, Schirmgrenze und `wanted_height` |
| `0b0197e` | `test(picker)`: Kartenhoehe an zwei Karten und an beiden Massen (Nachbesserung nach ueberlebendem Gegenbau) |
| `e29ef97` | `chore(scripts)`: zweite Stichprobe im Messskript |

Kein `push`, kein `pull`, kein `checkout`, kein `stash`. Der Arbeitsbaum ist
sauber; einzig `docs/tasks/T-093.md` liegt unversioniert da, das ist die Datei
des `director`.

## 8. Testergebnis

* **Vorher** (Auftrag, frischer Klon von `725182f`): 1190 passed, 9 skipped,
  5 deselected.
* **Nachher**, dieser Arbeitsbaum, `.venv\Scripts\python.exe -m pytest -m "not slow"`:
  **1229 passed, 9 skipped, 5 deselected in 737.87s (0:12:17)**.
  1190 + 37 neue Faelle in `tests/test_relic_picker_advisor.py` + 2 neue in
  `tests/test_relic_picker_geometry.py` = 1229.
* Python 3.12.10 aus `.venv`, PySide6, `QT_QPA_PLATFORM=offscreen`, Windows 10.
* **Die Suite braucht jetzt 12:17 und nicht mehr ~10 Minuten.** Sie hat damit
  das 10-Minuten-Zeitlimit gerissen, das der Auftragsrahmen als Obergrenze
  nennt; ich habe den Lauf zu Ende gefuehrt und das Ergebnis abgewartet. Der
  Zuwachs geht auf die neuen Faelle: jeder oeffnet einen echten `Planner` und
  rechnet echte Pools. Meldung an den `director`, damit die naechste
  Auftragsvorlage nicht mit einem Limit arbeitet, das nicht mehr reicht.
* **Kein Linter im Projekt konfiguriert** (nur `pytest.ini`,
  `requirements-dev.txt` = pytest); der DoD-Punkt entfaellt.

## 9. Offene Fragen und Entscheidungen

### 9.1 An den `director`: AK-48 ist **nicht** gebaut

Die Zeile `Its curse changes <field>, which neither figure counts.` fehlt.
Grund, und er ist kein Zeitgrund: **der Auftrag legt das Kriterium nicht
fest, und es gibt zwei, die verschiedene Saetze auf die Karte schreiben.**

* (i) **Feldtaxonomie**: ein Feld gilt als gezaehlt, wenn es in
  `goals.DAMAGE_CUT_FIELDS`, in `damage.AR_RATE_FOR` oder unter den
  skalierenden Attributen steht. Billig, aber es ist eine **Behauptung ueber
  die Rechnung**, die von ihr abdriften kann - und ein falscher Satz hier
  sagt dem Spieler, ein Preis koste ihn nichts.
* (ii) **Gemessen**: den Kandidaten ein zweites Mal ohne seine `curse_ids`
  auswerten und sehen, ob sich eine der beiden Zahlen bewegt. Immer wahr,
  keine Taxonomie - aber es ist eine **zweite Rechnung**, und sie gehoert
  nach `advisor/candidates.py` (etwa als drittes Feld neben den `marginals`),
  nicht in die Anzeige. `candidates.py` steht nicht in meinem Umfang.

Der Auftrag zaehlt AK-48 im Bereich "AK-41 bis AK-53" mit und nennt es unter
"Maskierung" und im Rahmen ("Betrifft dich bei AK-48"), listet die Fluchzeile
aber in der Aufzaehlung dessen, was an `relicpicker.py` zu aendern ist,
**nicht** auf. Nach der Regel "ein Feldname ist keine Beschreibung, drei
Gegenproben" habe ich nicht geraten. **Empfehlung: (ii), als eigener Auftrag
an `advisor/candidates.py`**, damit die Anzeige weiterhin nichts rechnet.

### 9.2 An den `director`: ein Widerspruch in der Vorgabe

**AK-62** verlangt die Pflichtzeile "sichtbar im Picker, **in jeder
Sortierung** und in jedem Zustand, in dem Kartenwerte gezeigt werden". Der
T-052-Nachtrag (UI_SPEC Zeile 1289) sagt: "Fuer `Name` (keine Zahlen, AK-49)
entfaellt die Zeile ganz."

Die beiden koennen nicht zugleich gelten, seit **AK-42** die Werte auch in
der Namenssortierung auf jede Karte setzt: `Name` ist **nicht** der Fall
"keine Zahlen", sondern eine Art hinzusehen. Ich bin AK-62 gefolgt: Zeile 4
steht, solange es ein Ranking gibt, in jeder Sortierung; sie entfaellt nur,
wenn es gar keine Zahlen gibt (AK-49). Wenn das falsch ist, ist es eine
Zeile Code - aber die Spezifikation sollte sich vorher einigen.

### 9.3 Entscheidungen, die ich getroffen habe (an `ui-ux-designer` und `director`)

1. **Vorzeichen als ASCII** `+`/`-` (`f"{x:+.1f}"`), nicht als das
   typografische Minus `−` der §3.3-Skizze. Grund: **jede** andere
   Vorzeichenzahl im Programm wird so geschrieben (app.py, effecttext.py,
   advisor/explain.py); zwei Minuszeichen nebeneinander waeren dieselbe
   Sorte Fehler, die AK-75 fuer den Gedankenstrich behoben hat. Wenn die
   Skizze verbindlich sein soll, sage es und ich drehe es um.
2. **Die Einheit steht am Wert, auch bei `Damage taken`**:
   `-20.0 effective HP`. Die §3.3-Skizze zeigt dort `−18` ohne Einheit. Ohne
   Einheit ist die Zeile aber irrefuehrend: die Zahl ist ein **Zuwachs an
   effektiven Trefferpunkten**, also bedeutet `+` weniger erlittener Schaden -
   unter der Beschriftung `Damage taken` liest sich `+18` sonst wie das
   Gegenteil. A12 verlangt die Einheit ausserdem. Sie kommt aus
   `Baseline.unit`, faellt also von selbst weg, sobald AD-004 eine
   einheitenlose Punktzahl liefert (das ist genau der AK-193-Fall).
3. **Eine Kopfzeile mehr.** §3.5 Punkt 5 und §3.7 verlangen einen Satz "in der
   Kopfzeile", der in der §3.2-Skizze keinen Platz hat. Ich habe dafuer eine
   eigene, umbrechende Zeile ueber Zeile 3 gesetzt (`self.headline`),
   sichtbar nur, wenn sie etwas zu sagen hat. Damit stehen vier statt drei
   Zeilen ausserhalb der Scrollflaeche.
4. **Die Custom-Karte traegt keinen Wertblock.** Sie ist kein Relikt, das man
   besitzt, hat kein Handle und steht in keinem Pool; AK-41 spricht von
   "Reliktkarte". Sie fuehrt das Raster weiterhin in jeder Sortierung
   (Fall vorhanden).
5. **`—` steht auch fuer eine Kopie, die der Pool nicht traegt** (kein Handle,
   AD-013 Punkt 4) - nicht nur fuer den AK-49-Fall. Beide Male ist die
   Aussage "hier wurde nichts gemessen", und die Begruendung steht in Zeile 3b.
   Auf diesem Spielstand tritt der Fall nicht auf (0 von 309 ohne Handle).
6. **Der Chip steht auch in der Namenssortierung.** AK-46 spricht von der
   "sortierten Zielrichtung"; bei `Name` gibt es keine, wohl aber die
   stehende Zielwahl. Die Aussage bleibt wahr, und sie verschwinden zu lassen
   waere eine Information weniger ohne Gewinn.

### 9.4 An den `director`: Abweichung vom Dateiumfang

Der Auftrag nennt `relicpicker.py`, `app.py` (nur `_open_picker`) und die
zwei Testdateien. Tatsaechlich:

* **`app.py` ist gar nicht angefasst.** Der Picker baut seine `SlotAdvice`
  selbst (`advice_for(slot)`), wenn der Aufrufer keine mitgibt. Das ist
  weniger Diff und ein Fehler weniger: ein Aufrufer, der das Argument
  vergisst, verliert sonst still die Zahlen. Tests geben eine gebaute Advice
  herein und brauchen dafuer kein Fenster.
* **`advisorbar.py` ist angefasst**, zweimal und minimal:
  `_held_slot` -> `held_slot` (der Picker liest jeden anderen Slot genauso,
  wie `Optimize` einen gehaltenen liest - sonst rechnen die beiden gegen zwei
  Builds), und `AdvisorBar.choose_goal` neu (ohne das gibt es keine Kopplung
  in beide Richtungen, ausser man greift von aussen in die Combo, und dann
  faellt die Folge aus `_goal_chosen` weg). Beides steht nicht im Umfang; ich
  sehe keinen Weg zu AK-43 ohne das zweite.

### 9.5 An den `director`: Bestandsbefunde und Beobachtungen

* **AK-51 war schon vorher offen** (zwei statt drei ganze Kartenzeilen am
  alten Standardmass 720 px). Kein Befund dieses Auftrags, aber er wird
  jetzt gemessen und ist damit sichtbar.
* **Ein zeitempfindlicher Fall wackelt unter Last.**
  `tests/test_advisor_bar.py::test_a_run_under_the_threshold_shows_nothing_at_all`
  ist mir einmal rot geworden, als ich ihn direkt hinter den neuen
  Picker-Faellen laufen liess (die echte Pools rechnen); allein und im vollen
  Lauf ist er gruen. Der Fall wartet 150 ms gegen eine 250-ms-Schwelle - das
  ist wenig Luft auf einer beschaeftigten Maschine. Nichts, was ich hier
  aendere; der `qa-engineer` sollte es wissen, bevor er es als Regression
  liest.
* **Performance, an den `performance-tuner` (nicht selbst getunt):** Das
  Oeffnen des Pickers kostet jetzt einen vollstaendigen `candidates.pool`-Lauf
  im Hauptthread, und jeder Wechsel der Zielrichtung im `Sort by` einen
  weiteren. AD-018 misst den teuersten Slot mit ~51 ms; auf einem groesseren
  Spielstand oder einem langsameren Rechner ist das die Zahl, die zuerst
  ueber 250 ms geht - und dann braucht der Picker doch den Zustandsautomaten,
  den er heute (§3.8) nicht haben soll.
* **SEC-021** (`_sync_mode` und `curse_tooltip` maskieren nicht) habe ich
  weder repariert noch nachgebaut: **jedes** neue Label und jeder neue Text
  in diesem Auftrag setzt `setTextFormat(Qt.PlainText)` ausdruecklich, und
  keiner meiner neuen Saetze interpoliert Spieltext. Zusaetzlich habe ich
  `self.summary` auf `PlainText` gestellt - dort steht der **Suchtext des
  Spielers** drin, und das Label stand vorher auf `AutoText`. Das ist eine
  Zeile ausserhalb des engen Auftrags; ich melde sie, statt sie zu
  verschweigen.
* **`docs/state.md`, `qa/findings.md`, `UI_SPEC.md`** habe ich nicht
  angefasst. Die Widersprueche aus 9.2 und die Zahlen aus 3 gehoeren dorthin,
  wenn der `director` sie uebernimmt.

## 10. An den `qa-engineer`

Was zu testen ist, und die Kanten, die ich kenne:

1. **Ein Slot, in dem schon ein Relikt steckt.** Der Grundzustand ist der Build
   **mit geleertem Slot**, auch fuer dieses Relikt - es muss also einen
   eigenen, von Null verschiedenen Wert zeigen und darf nicht gegen sich
   selbst antreten.
2. **Ein gehaltener Slot** (`Hold`): der Picker haelt beim Rechnen ohnehin
   jeden anderen Slot; ein vom Spieler gehaltener Slot darf daran nichts
   aendern.
3. **Der Filter**: die Kennzeichnung ist ueber den **ganzen** Pool gebildet.
   Filtert man die beste Karte weg, traegt **keine** sichtbare Karte den Chip -
   das ist Absicht und sieht wie ein Fehler aus.
4. **Zielrichtung im Picker umstellen und den Dialog abbrechen**: die
   Zielwahl der Leiste bleibt umgestellt (es ist dieselbe Einstellung) und
   die stehende `Optimize`-Antwort ist weg. Auch das ist Absicht.
5. **Ein Deep-Slot** eines Gefaesses mit Deep-Slots (Wylder hat welche,
   Guardian nicht) - dort haben fast alle Kandidaten Fluche, und dort tritt
   der echte Gleichstand auf (zwei Karten `+5.9 AR`).
6. **`Sort by` = `Name`**: beide Zahlen bleiben auf jeder Karte, Zeile 4
   bleibt stehen (siehe 9.2 - falls der `director` anders entscheidet, dreht
   sich dieser Fall um).
7. **Ohne Spielstand**: keine Karten ausser der Custom-Karte, Kopfzeile
   `The game's data carries no figures this goal can be ranked on, …`.
   Der Satz ist dort streng genommen nicht die ganze Wahrheit (es fehlt der
   Spielstand, nicht die Zahl) - wenn das stoert, ist es eine eigene
   Kopfzeile wert.
8. **Nicht getestet, weil nicht gebaut:** AK-48 (die Fluchzeile). Nicht
   dagegen testen, bis 9.1 entschieden ist.

## 11. An den `ui-ux-designer`

* Der Wertblock kostet **28 px** je Karte; am Standardmass sind statt ~19
  noch ~16 Karten sichtbar (Vorgabe schaetzte 34 px und ~16 Karten).
* Der Chip liegt als **leerer 13-px-Streifen** ueber dem Namen auf **jeder**
  Karte, auch wo er nie gefuellt wird. Das ist der Preis fuer AK-41
  (0 px Unterschied) und es verschiebt den Namen jeder Karte um 13 px nach
  unten. Wenn das stoert, ist die Alternative, den Chip rechts neben den
  Namen zu legen - dann wird der Name schmaler und bricht bei langen Relikten
  mehr um.
* Vier statt drei Zeilen ueber dem Raster (siehe 9.3 Punkt 3), zusammen
  **386 px**. Das ist viel Grau ueber wenig Raster, und es ist der Grund,
  warum AK-51 nicht aufgeht (Abschnitt 3).
* `-20.0 effective HP` statt `−18` (siehe 9.3 Punkt 2).
