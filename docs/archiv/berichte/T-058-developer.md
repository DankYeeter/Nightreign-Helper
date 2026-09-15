```
STATUS: erledigt
AUFTRAG: T-058 — Was der Spieler nicht sehen kann: Fenstergeometrie und abgeschnittene Inhalte
GELESEN: docs/tasks/T-058.md · GOAL.md (A10 bis A14) · docs/state.md · DESIGN_REVIEW.md (Review vom 05.09., DR-013 bis DR-018 samt Backlog) · UI_SPEC.md (AK-71 bis AK-77, AK-83 bis AK-90, AK-95 bis AK-97, §8, und der Nachtrag des Directors vom 05.09. zu AK-81/82/88 am Dateiende) · docs/berichte/T-056-ui-ux-designer.md · docs/berichte/T-057-developer.md (Abschnitte 5 bis 9) · docs/screenshots/2026-09-05-T056/ (tab1-effects.png, tab3-nightlords.png, tab4-deep.png, zoom-tile-clipped.png, zoom-tile-wrap.png) · nrplanner/{app,arsenaltab,bosstab,deeptab,depthstab,effectstab,eventlore,eventstab,relicpicker,stacking,weaponslots,uiscale,advisor/goals}.py · tests/{conftest,tabtext,test_weapon_slot_tile_wrap,test_arsenal_tab_asks_the_facade,test_deep_tab_display,test_effects_tab_display}.py · scripts/{make_screenshots,differential/mutate}.py · CLAUDE.md
GEÄNDERT: nrplanner/cardgrid.py (neu) · nrplanner/bosstab.py · nrplanner/arsenaltab.py · nrplanner/deeptab.py · nrplanner/effectstab.py · nrplanner/eventlore.py · nrplanner/advisor/goals.py · scripts/make_screenshots.py · scripts/differential/mutate.py · tests/rendered.py (neu) · tests/test_tab_geometry.py (neu) · tests/test_weapon_tile_value_wrap.py (neu) · tests/test_one_dash_style.py (neu) · tests/test_one_name_per_figure.py (neu) · docs/screenshots/2026-09-05-T058/ (20 PNG, neu) · docs/berichte/T-058-developer.md (neu, diese Datei) — in 10 eigenen Commits 8b26594..HEAD. Keine fremde Datei angefasst und keine committet; kein push/pull/fetch/merge/rebase/checkout/branch/reset/revert/stash.
ANNAHMEN: (1) Die Pixelzahlen in DR-013, DR-014 und DR-016a sind **physische** px auf dem 150-%-Bildschirm des Nutzers, nicht logische. Begruendung und Beleg in Abschnitt 1; ich habe deshalb bei 833 und 1067 **logischen** px gemessen und getestet, zusaetzlich zu den 1250/1600/2100 aus AK-72/84/90. (2) Der Splitter aus der Loesungsrichtung von DR-013 ist nicht gebaut: mit dem umbrechenden Raster passen alle zehn Karten neben das Panel, und ein Splitter waere ein neues Bedienelement statt einer Reparatur. (3) Bei Fensterbreiten unter etwa 1100 logischen px gebe ich die beiden Untergrenzen aus AK-77 auf, statt eine Spalte ueber den rechten Rand zu schieben — Begruendung und Zahlen in Abschnitt 4a, das ist eine bewusste Abweichung von AK-77 und gehoert dir.
NÄCHSTER: qa-engineer
BLOCKIERT DURCH: nichts
```

# T-058 — Bericht des `developer`

## 0. Stand in Zahlen

| | vorher | nachher |
|---|---|---|
| `-m "not slow"` | 662 passed, 5 deselected | **722 passed, 5 deselected** |
| `-m "slow"` | 5 passed | **5 passed, 722 deselected** |
| Mutationen in `scripts/differential/mutate.py` | 63 | **71** |
| Neue Waechter | — | **52 Faelle in 4 neuen Dateien**, dazu 8 neue Ankerfaelle in `test_differential_track.py` |

```
722 passed, 5 deselected in 223.69s (0:03:43)
5 passed, 722 deselected in 50.28s
```

---

## 1. Zuerst: die Pixelzahlen des Reviews sind physisch, nicht logisch

**Das ist der wichtigste einzelne Befund dieses Auftrags, weil ohne ihn jeder
Waechter gruen und wertlos gewesen waere.**

`DESIGN_REVIEW.md` nennt fuer DR-013 „bei 1600 px Fensterbreite" und fuer
DR-016a „reproduziert bei 1600 px (5. Spalte) und 1250 px (4. Spalte)".
`UI_SPEC.md` AK-72, AK-84 und AK-90 verlangen die Pruefung bei „1250, 1600 und
2100 **logischen** px". Beides sind nicht dieselben Zahlen: der Bildschirm ist
2560x1600 physisch bei 150 % Skalierung, also sind 1600 physische px
**1067 logische** und 1250 physische **833 logische**.

Gemessen am unveraenderten Baum (`git archive HEAD | tar -x`, Windows-Plattform):

| Fensterbreite (logisch) | Nightlord-Karten ganz gezeichnet | Waffenkacheln ganz |
|---|---|---|
| 833 | **3 von 10** | 47 von 77 |
| 1067 | **6 von 10** | **62 von 77** |
| 1250 | **8 von 10** | 77 von 77 |
| 1600 | 10 von 10 | 77 von 77 |
| 2100 (auf 1707 begrenzt) | 10 von 10 | 77 von 77 |

Bei 1067 logischen px sind genau die vier Karten abgeschnitten, die DR-013
nennt — Gnoster und Caligo halb, **Maris** und **Harmonia** gar nicht —, und
bei 1250 logischen px genau die beiden, die DR-013 als Spalte 4 benennt.

**Die Folge: haette ich nur bei 1250/1600/2100 logischen px getestet, waere
DR-016a bei keiner einzigen Breite reproduzierbar gewesen.** Der Waechter
waere gruen gewesen und haette nichts belegt — genau die Falle, vor der der
Auftrag warnt, nur eine Ebene tiefer. `tests/test_tab_geometry.py` prueft
deshalb bei **833, 1067, 1250, 1600 und 2100** logischen px.

### 1b. Die zweite Messfalle: die Testumgebung sieht nicht die Schrift des Spielers

`tests/conftest.py` setzt `QT_QPA_PLATFORM=offscreen`, bevor Qt geladen wird —
richtig, weil die Suite keinen Bildschirm brauchen darf. Die Offscreen-
Plattform hat aber **eine andere Schrift**: gemessen am selben Datensatz ist
ein Effektname dort rund **12 px pro Zeichen** breit, unter der Windows-
Plattform rund **6**. Alle absoluten Pixelzahlen des Reviews und die meines
eigenen ersten Messlaufs sind Offscreen-Zahlen.

Konkret: T-056 nennt fuer DR-014 `Effect` **22 px** bei 1516 px
Tabellenbreite. Ich reproduziere unter Offscreen **17 px** (kein Zufall,
sondern Qts `minimumSectionSize`) und unter Windows an derselben Stelle
**32 px** bei 833 px Fensterbreite. Dieselbe Ursache, drei Zahlen.

**Was ich daraus gemacht habe:** jede Zahl unten steht mit ihrer Plattform da.
Die Waechter behaupten nur Beziehungen, die unter **beiden** gelten (`Effect`
ist die breiteste Spalte, keine Karte angeschnitten, keine waagerechte
Bildlaufleiste); die beiden absoluten Untergrenzen aus AK-77 werden nur bei
den Breiten behauptet, bei denen sie unter der **engeren** der beiden
Plattformen halten. Alle neuen Faelle laufen unter beiden gruen:

```
QT_QPA_PLATFORM=offscreen  ->  36 passed (tab_geometry)
QT_QPA_PLATFORM=windows    ->  52 passed (die vier neuen Dateien)
```

**An den `director` und den `qa-engineer`:** die Suite kann die Pixel des
Spielers nicht sehen. Der Screenshot und der Messlauf gegen die Windows-
Plattform sind der Beleg fuer die Maschine; die Suite ist der Beleg, dass eine
Aenderung auffiele. Das gehoert in `docs/lessons.md`, nicht von mir eingetragen.

---

## 2. Punkt 1 des Auftrags — die Fensterhoehe

Gemessen an einer echten `Planner`-Instanz, Windows-Plattform, 150 % Skalierung:

| | vorher | nachher | Schranke AK-71 |
|---|---|---|---|
| `DeepTab().minimumSizeHint().height()` | **1195** | **69** | 860 |
| Fenster-Mindesthoehe (logisch) | **1225** | **513** | — |
| Fenster-Mindesthoehe (physisch, 150 %) | **1838** | **770** | 1552 nutzbar |
| Effects / Weapons / Nightlords / Red variants / World Events | 190 / 188 / 163 / 240 / 150 | unveraendert | alle ok |

Unter der Offscreen-Plattform, wo T-056 und T-057 gemessen haben, lauten
dieselben zwei Zahlen **1047 → 68** und **1075 → 480**. Der Auftrag nennt
1047 als Ausgangswert; das ist die Offscreen-Zahl und sie stimmt.

**Aufgefangen: 1126 logische px** (1195 → 69) statt der verlangten 187, bzw.
979 px gegen den Offscreen-Ausgangswert.

Die zweite Haelfte von AK-97, die eine Hoehenzahl nicht zeigen kann:

```
vorher : scroll areas on the tab: 0; last line exists: True
         no scroll area: the line cannot be reached by scrolling
nachher: scroll areas on the tab: 1; last line exists: True
         scrolled to the bottom, the line is visible: True
```

**Der Screenshot ist hier selbst die Messung.** Beide Bilder entstehen aus
`window.resize(1600, 900)`:

* `deep-at-900-before.png` ist **2400x1727** px — das Fenster hat sich
  geweigert, 900 logische px hoch zu sein, und ist bei 1151 geblieben;
* `deep-at-900-after.png` ist **2400x1350** px, und 1350 / 1,5 = **900**.

Die letzte Zeile *„Read from the game's own depth table."* steht im
Nachher-Bild unten am Rand, erreicht durch Scrollen.

**Wie:** der Inhalt liegt in einer `QScrollArea` mit `setWidgetResizable(True)`.
Die vier Tabellen **behalten** ihre gefittete Hoehe. AK-97 sagt woertlich „die
vier Tabellen setzen keine feste Hoehe mehr, die das ganze Fenster bindet" —
ich habe den Nebensatz als die Bedingung gelesen: innerhalb eines
Scrollbereichs bindet die Hoehe nichts mehr, und ohne sie zoege jede Tabelle
eine eigene Bildlaufleiste ein, was A13 verletzte. Wenn du den ersten
Halbsatz woertlich willst, sag es; das Ergebnis waere schlechter.

---

## 3. Punkt 2 des Auftrags — DR-013, die zwei unsichtbaren Nachtlords

Gemessen als gerenderte Rechtecke im gerenderten Viewport (Windows-Plattform):

| Fensterbreite | vorher: ganz / angeschnitten / waagerechte Leiste | nachher |
|---|---|---|
| 833 | 3 / 7 / ja | **10 / 0 / nein** |
| 1067 | 6 / 4 / ja | **10 / 0 / nein** |
| 1250 | 8 / 2 / ja | **10 / 0 / nein** |
| 1600 | 10 / 0 / nein | 10 / 0 / nein |
| 2100 | 10 / 0 / nein | 10 / 0 / nein |

**Bei welchen Fensterbreiten alle zehn Nightlords sichtbar sind:** vorher ab
1600 logischen px; nachher bei **jeder gemessenen Breite ab 833**.

Angeschnitten vorher: bei 1067 `Gnoster, Maris, Caligo, Harmonia`, bei 1250
`Maris, Harmonia` — die Namen aus DR-013, an ihren jeweiligen Breiten.

Belege: `nightlords-1067-before.png` (acht Karten, dritte Spalte mitten im
Blurb abgeschnitten, waagerechte Leiste an der Unterkante) gegen
`nightlords-1067-after.png` (zehn Karten, alle Blurbs vollstaendig, eine
**senkrechte** Leiste statt der waagerechten).

**Wie:** `nrplanner/cardgrid.py`, ein Raster, dessen Spaltenzahl aus der
verfuegbaren Breite folgt und bei jeder Groessenaenderung neu gerechnet wird.
`bosstab.COLUMNS = 4` ist entfallen.

**Die Haelfte, die man im Quelltext nicht sieht** und die eine eigene Mutation
hat: die Mindestbreite eines `QGridLayout` ist die Summe seiner Spalten. Ein
Halter in einer `QScrollArea` kann deshalb nie unter die Zeile schrumpfen, in
der er gerade liegt — der Scrollbereich gibt auf, zeigt eine waagerechte
Leiste, das Widget bekommt nie eine kleinere Groesse, und der Umbruch, der das
geheilt haette, laeuft nie. `CardGrid.minimumSizeHint()` meldet deshalb **eine**
Karte. Ohne diese vier Zeilen sieht der Code richtig aus und zeichnet dieselben
angeschnittenen Karten.

**Der Splitter aus der Loesungsrichtung ist nicht gebaut** (Annahme 2 oben):
das Detailpanel behaelt seine 330 px, und alle zehn Karten passen daneben.

---

## 4. Punkt 3 des Auftrags — DR-014, die abgeschnittenen Effektnamen

Windows-Plattform, gerenderte `sectionSize`:

| Fenster | `Effect` vorher → nachher | breiteste Spalte vorher → nachher | Namen abgeschnitten vorher → nachher | waagerechte Leiste |
|---|---|---|---|---|
| 833 | **32 → 271** | `Stacking` → `Effect` | **652 → 173** von 652 | ja → **nein** |
| 1067 | **138 → 320** | `Stacking` (159) → `Effect` | **573 → 80** | nein → nein |
| 1250 | 230 → 320 | `Effect` → `Effect` | 274 → 80 | nein |
| 1600 | 405 → 446 | `Effect` | 35 → 12 | nein |
| 2100 (1707) | 459 → 506 | `Effect` | 7 → 2 | nein |

Offscreen, zum Vergleich mit den Zahlen von T-056/T-057: `Effect` **248 px**
von 2052 bei 2100 px mit **603 von 652** abgeschnitten, und bei 1250/1600 eine
Tabelle von **4823 px** Breite hinter einer waagerechten Bildlaufleiste, bei
der sechs der elf Spalten gar nicht auf dem Schirm waren. Nachher: 322 / 320 /
323 / 321 / 478, keine Leiste, `Effect` immer die breiteste.

Belege: `effects-1067-before.png` — vier Zeilen hintereinander lesen sich als
`Successful …` — gegen `effects-1067-after.png`, wo jeder Name vollstaendig
dasteht.

**Wie:** `EffectTable` in `nrplanner/effectstab.py`. Die beiden Untergrenzen
(320 / 260 aus AK-77) werden zuerst abgezogen, die neun Beschriftungsspalten
teilen sich den Rest bis zu einer Obergrenze, und was dann noch uebrig ist,
geht im Verhaeltnis 320:260 an die beiden Spalten, um die es geht. Die
Aufteilung laeuft bei jeder Breitenaenderung, wie `Stretch` es auch tat —
geaendert hat sich, **wer zuerst bedient wird**, nicht wann.

Zwei Entscheidungen, die ich ausdruecklich vorlege:

**(a) Unterhalb von etwa 1100 logischen px gebe ich die beiden Untergrenzen
auf.** Dort passen die elf Spalten und 320 + 260 nicht zusammen. Die
Alternative waere gewesen, die Tabelle ueber ihren eigenen Viewport wachsen zu
lassen — und eine Spalte hinter dem rechten Rand ist auf diesem Programm
unerreichbar, weil die Leiste, die sie erreichte, die hinter der Taskleiste
ist (DR-015). `Effect` ist bei 833 px 271 statt 320; das ist eine Abweichung
von AK-77 und deine Entscheidung. Gemessen: mit erzwungener Untergrenze haette
die Tabelle bei 833 px 883 px in einem 780-px-Viewport gebraucht.

**(b) Die Verkleinerung nimmt der breitesten Spalte zuerst.** Alle gleich
prozentual zu kuerzen brachte `Type` auf Qts Minimum (32 px, gezeichnet als
`B…`), waehrend `Stacking` noch 93 px hatte. Die Stufenverteilung haelt `Type`
bei den 37 px, die seine eigene Kopfzeile braucht, und bringt `Stacking` auf 51.

**(c) Gekuerzt heisst erreichbar, nicht verloren.** Jede Zelle ohne eigenen
Tooltip traegt jetzt ihren vollen Text als einen; die beiden Zellen, die einen
anderen Tooltip hatten (der Name mit seiner Spielkategorie, die
Stacking-Klasse mit ihrem Beleg), tragen ihren eigenen Text **darueber**. Ein
eigener Waechter prueft das an den ersten 120 Zeilen mal elf Spalten gegen die
gerenderte Spaltenbreite; er war beim ersten Lauf rot und hat die
Stacking-Zelle gefunden.

---

## 5. Punkt 4 des Auftrags — DR-016, die abgeschnittene Waffenkachel

**(a) Das Raster.** Windows-Plattform, sichtbare Kacheln:

| Fenster | vorher ganz / angeschnitten / Leiste | nachher |
|---|---|---|
| 833 | 47 / **30** / ja | **77 / 0 / nein** |
| 1067 | 62 / **15** / ja | **77 / 0 / nein** |
| 1250 | 77 / 0 / nein | 77 / 0 / nein |
| 1600 | 77 / 0 / nein | 77 / 0 / nein |
| 2100 | 77 / 0 / nein | 77 / 0 / nein |

`arsenaltab.COLUMNS = 5` ist entfallen; dasselbe `CardGrid` wie beim
Nightlord-Tab, nur ohne Spaltendehnung, weil die Kacheln eine feste Breite
haben.

**(b) Der Umbruch mitten im Begriff.** Gemessen an den 77 Kacheln, mit denen
der Tab jetzt oeffnet, bei 1600 px, an der Schriftart und der gerenderten
Breite des jeweiligen Labels und mit Qts eigenem Zeilenumbrecher:

```
vorher : multi-group value labels: 122   broken inside a group: 46
         'STR -21 · INT +29 · DEX +6' breaks at [4, 14, 24]
nachher: multi-group value labels: 122   broken inside a group:  0
         single-group value labels: 315  taking a second line: 0
```

Die Bruchstellen 4, 14, 24 sind genau `STR` / `-21`, `INT` / `+29`, `DEX` /
`+6` — DR-016b woertlich. Nachher bricht die Zeile nur zwischen zwei Gruppen,
sichtbar in `weapons-1067-after.png` (`DEX +6 · INT +29 ·` / `STR -21`).

**Ein bestehender Test hat mich dabei korrigiert, und zu Recht.** Mein erster
Wurf setzte den geschuetzten Zwischenraum in **jeden** Wert, also auch in
`+3 Rare` auf der `Upgraded to`-Zeile;
`test_arsenal_tab_asks_the_facade::test_every_type_row_and_the_upgrade_line_match_the_facade`
verglich diese Zeichenkette Byte fuer Byte und wurde rot. Das war kein
Testfehler, sondern eine angezeigte Zeichenkette, die kein Befund zu aendern
verlangt hat. `unbroken()` gibt einen Wert ohne Gruppentrenner jetzt
unveraendert zurueck — belegt dadurch, dass **0 von 315** einwertigen Werten
auf diesen Kacheln ueberhaupt umbrechen.

---

## 6. Punkt 5 des Auftrags — DR-017 / AK-83 und DR-018 / AK-75

**DR-017.** Sichtbare Kacheln beim Oeffnen des Tabs: **0 → 77**.
`weapons-1067-before.png` zeigt drei zugeklappte Ueberschriften ueber einer
leeren schwarzen Flaeche; `weapons-1067-after.png` zeigt `Weapons (1792)` →
`Axe (77)` aufgeklappt.

Es wird **ein** Unterabschnitt geoeffnet, nicht alle: `expand_all` auf
`Weapons` haette 1 792 Kacheln gebaut. Gemessene Kosten, Fensteraufbau und
Layout: **1,80 s → 2,14 s**; vollstaendiger Start einschliesslich Datenladen
**2,30 s → 2,70 s**. Ein Waechter haelt die Zahl gebauter Kacheln unter 500.

**DR-018 / AK-75.** Gerenderter Text aller sechs Tabs, einschliesslich aller
15 Zeilen der World-Events-Liste und aller zehn Nightlord-Panels:

```
vorher : Effects 0 · Weapons 0 · Nightlords 0 · Deep 0 · Red variants 0 · World Events 8   TOTAL 8
nachher: 0 0 0 0 0 0   TOTAL 0
```

Die acht standen alle in `eventlore.py` und werden erst gezeichnet, wenn ihr
Ereignis angewaehlt ist — deshalb fand ein Zaehler auf dem frisch geoeffneten
Tab null und haette immer null gefunden. Beleg auf dem Schirm:
`worldevents-1600-after.png`, `Hordes of the Night`.

---

## 7. Punkt 6 des Auftrags — AK-88 an der einen verbliebenen Stelle

`nrplanner/advisor/goals.py:112` sagt jetzt `spell power`. Suchbelege in
Abschnitt 9.

---

## 8. Je Waechter die toetende Mutation und ihr Ergebnis

Acht neue Mutationen, jede einzeln auf eine Kopie **dieses** Baums angewandt
und mit der vollstaendigen schnellen Suite gefahren (sauber: 722 passed).
`test_differential_track::test_every_mutation_still_finds_its_anchor_in_the_real_source`
faellt in jedem Lauf mit, weil der Anker im mutierten Baum naturgemaess fehlt;
er ist unten nicht mitgezaehlt.

| Mutation | faellt | die Faelle, die sie toeten |
|---|---|---|
| `deep-tab-back-outside-a-scroll-area` | 2 | `test_no_content_tab_asks_the_window_for_more_than_the_limit`, `test_the_last_line_of_deep_of_night_can_be_reached_by_scrolling` |
| `card-grid-back-to-a-fixed-column-count` | 7 | `test_every_nightlord_card_is_drawn_whole[833/1067/1250]`, `test_the_two_cards_the_review_lost_are_among_them[833/1067/1250]`, `test_the_count_above_the_grid_matches_the_cards_drawn` |
| `card-grid-minimum-back-to-the-whole-row` | 3 | `test_every_nightlord_card_is_drawn_whole[833/1067]`, `test_the_count_above_the_grid_matches_the_cards_drawn` |
| `effect-column-back-to-the-leftovers` | 10 | `test_the_effect_column_is_the_widest_column_at_every_width[833/1067/1250/1516]`, `test_the_two_reading_columns_hold_their_floors[1250/1516/1600]`, `test_the_effects_table_needs_no_horizontal_scrollbar[833/1067/1250]` |
| `tile-value-free-to-break-inside-a-group` | 1 | `test_no_value_breaks_inside_one_of_its_groups` |
| `arsenal-opens-on-three-collapsed-headings-again` | 8 | `test_every_weapon_tile_is_drawn_whole[alle fuenf Breiten]`, `test_the_arsenal_shows_a_tile_without_being_asked`, dazu die beiden Vorbedingungsfaelle der Umbruchdatei |
| `world-event-prose-back-to-two-hyphens` | 2 | `test_no_rendered_text_of_the_six_tabs_holds_a_double_hyphen`, `test_no_displayed_literal_of_a_tab_module_holds_a_double_hyphen[eventlore]` |
| `catalyst-figure-named-twice` | 3 | `test_the_catalyst_figure_is_named_the_same_on_the_card_and_in_the_scope`, `test_the_retired_name_is_in_no_displayed_string_anywhere[beide Masken]` |

**`card-grid-minimum-back-to-the-whole-row` ist die wichtigste der acht.** Sie
laesst den Umbruch im Quelltext stehen und macht ihn unerreichbar — der
Zustand, in dem der Code richtig aussieht und dieselben angeschnittenen Karten
zeichnet. Ohne sie waere die Reparatur nur zur Haelfte belegt (L-002).

**Zwei Mutationen musste ich nach einer Codeaenderung nachziehen**, und der
Ankerfall hat beide gefunden statt sie stillschweigend ins Leere laufen zu
lassen: `deep-tab-back-outside-a-scroll-area` (die erste Fassung liess den Tab
mit zwei Layouts und ohne Inhalt zurueck, also fiel `…_asks_the_window_…` gar
nicht — jetzt stellt sie den Zustand von HEAD woertlich wieder her) und
`effect-column-back-to-the-leftovers` (Anker war auf eine Zeile gesetzt, die
ich danach umgeschrieben habe).

---

## 9. Suchbelege (L-006), je zwei unabhaengige Masken

**` -- ` in angezeigten Zeichenketten** (AST ueber alle `.py` unter
`nrplanner/`, Docstrings ausgenommen, Kommentare sind keine Konstanten):

* Maske 1 `" -- "` · Maske 2 `\S\s--\s\S`
* in den **sieben Tab-Modulen**: vorher 10, nachher **0** (beide Masken)
* im **ganzen Paket**: nachher **4**, alle ausserhalb der sechs Tabs —
  `datasource.py:173` (Erststart-Text), `model.py:889` (Ausnahmetext),
  `model.py:1058` (Build-Warnung auf dem `Build planner`), `weapons.py:221`
  (Fehlertext zu einem veralteten Cache). **An den `director`:** AK-75 ist auf
  die sechs Tabs geschrieben, deshalb habe ich diese vier stehen lassen. Wenn
  die Regel fuer das ganze Programm gelten soll, ist das ein eigener Auftrag.

**`spell scaling` in angezeigten Zeichenketten**:

* Maske 1 `spell\s+scaling` · Maske 2 `scaling the game` (unabhaengig, faengt
  auch eine Umformulierung ohne den ersten Ausdruck)
* vorher **1** (`advisor/goals.py:108`), nachher **0**, beide Masken, ganzes Paket.
* Der Fall dazu steht in `tests/test_one_name_per_figure.py` und laeuft ueber
  **alle** `.py` unter `nrplanner/`, nicht ueber die eine bekannte Datei.

**Feste Spaltenzahlen (die Eigenschaft hinter DR-013 und DR-016a)** —
Maske 1 `^[A-Z_]*COLUMNS *= *[0-9]+`, Maske 2 `addWidget\(.*//.*,`:

| Fundstelle | Zustand |
|---|---|
| `bosstab.COLUMNS = 4` | **behoben** |
| `arsenaltab.COLUMNS = 5` | **behoben** |
| `app.py:2702` (`per_row` der Artwork-Auswahl) | war schon aus der Breite gerechnet |
| `relicpicker.py:16` `COLUMNS = 5`, benutzt `:531` | **offen, ausserhalb des Auftrags** |
| `relicpicker.py:31` `HERO_COLUMNS = 5`, benutzt `:235` | **offen, ausserhalb** |
| `weaponslots.py:59` `SLOT_COLUMNS = 3`, benutzt `app.py:1665` | **offen, ausserhalb** |
| `app.py:1416` `grid.addWidget(tile, i // 5, i % 5)` (Nightfarer-Leiste) | **offen, ausserhalb** |

Alle vier offenen liegen im `Build planner` bzw. im Relikt-Picker, die T-058
ausdruecklich ausnimmt. **Der Befund ist damit nicht geschlossen** — die
Eigenschaft besteht an vier weiteren Stellen fort. Bewertung in Abschnitt 12.

---

## 10. Was ich am laufenden Fenster gesehen habe

Zehn Paare unter `docs/screenshots/2026-09-05-T058/`, alle von der echten
Windows-Plattform, mit `app.setStyle("Fusion")` und
`app.setPalette(appmod._dark_palette())` vor dem Fensterbau und mit
`window.grab()` ueber das ganze Fenster. Ein Offscreen-Bild haette eine andere
Schrift und ein anderes Layout gezeigt, und ein Treiber, der `Planner` selbst
baut, bekommt sonst die helle Fusion-Palette.

* `nightlords-1067` — acht Karten und eine angeschnittene dritte Spalte unter
  der Zeile „10 Nightlords", gegen zehn ganze Karten
* `nightlords-1250` — Maris und Harmonia am Rand abgeschnitten, gegen zehn ganze
* `nightlords-1600` — beide Zustaende gleich, als Kontrolle
* `weapons-1067` / `weapons-1600` — drei zugeklappte Ueberschriften ueber
  leerer Flaeche, gegen vier Spalten Kacheln mit jeder Zahl neben ihrem Label
* `effects-1067` — vier Zeilen `Successful …`, gegen jeden Namen lesbar
* `effects-1600` / `effects-2100` — `Effect` 405 → 446 bzw. 459 → 506
* `deep-at-900` — das Vorher-Bild ist 1727 px hoch fuer ein Fenster, das 900
  logische px sein sollte; das Nachher-Bild ist 1350 px, also genau 900
* `worldevents-1600` — `Hordes of the Night` mit dem Gedankenstrich

---

## 11. An den `qa-engineer`

**Zu testen, mit den Kanten:**

1. **Fenstergroesse von Hand.** Das Fenster laesst sich jetzt auf 513 logische
   px Hoehe ziehen. Sieh dir an, was bei dieser Hoehe auf **jedem** der sieben
   Tabs passiert — ich habe die Mindesthoehe gesenkt, nicht jeden Tab bei
   dieser Hoehe geprueft. Der `Build planner` ist dabei ausdruecklich mit
   gemeint, obwohl er nicht in meinem Auftrag stand.
2. **Nightlords bei sehr schmalem Fenster.** Bei 833 px liegt das Raster
   einspaltig und es gibt eine senkrechte Bildlaufleiste. Kante: das
   Detailpanel behaelt 330 px, der Kartenbereich bekommt dann 444.
3. **Effects unter 1100 px.** Dort geben die beiden Untergrenzen nach
   (Abschnitt 4a) und die Beschriftungsspalten sind stark gekuerzt: bei 1067 px
   `Type` 37, `Tier` 44, `Colours` 51. Jede gekuerzte Zelle muss ihren vollen
   Text als Tooltip tragen — das ist die Zusicherung, die den Kompromiss
   traegt, und die pruefe nicht nur ich.
4. **Effects, Sortieren und Filtern.** Ich habe die Spaltenpolitik geaendert,
   nicht den Inhalt; die Aufteilung laeuft bei jeder Groessenaenderung und nach
   jedem `refresh()`. Kante: eine Spalte von Hand ziehen und dann das Fenster
   aendern — meine Aufteilung ueberschreibt die Handbreite.
5. **Weapons, Suche.** Der Erstzustand klappt jetzt eine Gruppe auf; eine Suche
   mit <= 60 Treffern klappt weiterhin alles auf, eine mit mehr nichts. Kante:
   Suche eingeben und wieder loeschen — danach steht wieder `Axe` offen.
6. **Weapons, Kachelwerte.** Der Umbruch ist an 122 mehrgruppigen Werten
   geprueft. Kante: eine Waffe mit vier oder mehr Skalierungsgruppen, falls es
   sie gibt, und die `vs standard`-Zeile.
7. **World Events, alle 15 Zeilen.** Der Gedankenstrich ist ueber alle
   Listenzeilen gezaehlt, aber nur `Hordes of the Night` ist als Bild belegt.
8. **Das, was ich nicht abgedeckt habe:** ich habe die Geometrie des `Build
   planner` nicht angefasst und nicht gemessen. Er teilt sich das Fenster mit
   den sechs Tabs, und seine Mindesthoehe war nie der Verursacher — aber jetzt,
   wo `Deep of Night` nicht mehr 1195 px fordert, ist irgendein anderer Tab der
   hoechste, und das ist bei 240 px `Red variants`.

---

## 12. An den `director` — Debt, Risiken, Entscheidungen

**Zu entscheiden:**

1. **AK-77 unterhalb 1100 px** (Abschnitt 4a). Ich gebe die Untergrenzen auf,
   um keine Spalte hinter den rechten Rand zu schieben. Wenn AK-77 woertlich
   gelten soll, bekommt der Tab dort eine waagerechte Bildlaufleiste, deren
   Griff hinter der Taskleiste liegt.
2. **AK-97, erster Halbsatz** (Abschnitt 2). Die vier Tabellen behalten ihre
   feste Hoehe, weil sie ohne sie eigene Bildlaufleisten bekaemen.
3. **AK-75 ausserhalb der sechs Tabs** (Abschnitt 9): vier angezeigte
   Zeichenketten mit ` -- ` bleiben stehen, weil AK-75 auf die sechs Tabs
   geschrieben ist. Eigener Auftrag oder bewusst so lassen?
4. **Die vier verbliebenen festen Spaltenzahlen** (Abschnitt 9), alle im
   `Build planner` und im Relikt-Picker. **Risiko:** der Picker setzt sich beim
   Oeffnen selbst auf `CARD_WIDTH * COLUMNS + 80` = 1030 px und ist
   groessenveraenderlich — wer ihn schmaler zieht, bekommt dieselbe
   angeschnittene letzte Karte wie DR-016a. Aufwand: klein, das `CardGrid`
   liegt fertig da; es ist ein Auftrag von vielleicht einer Stunde plus
   Waechter. Ich habe es **nicht** gemacht, weil T-058 den `Build planner`
   ausnimmt.
5. **Startkosten +0,40 s** (Abschnitt 6), Folge von AK-83. Der naheliegende
   Hebel — erst beim ersten *Anzeigen* des Tabs aufklappen statt beim Bau des
   Fensters — hat eine Ereignisreihenfolge-Falle: `QTabWidget` zeigt die Seite,
   **bevor** es `currentChanged` sendet, und `currentChanged` ruft
   `recalculate()`, das die Abschnitte wieder zuklappt. Ich habe die einfache,
   robuste Fassung gebaut. **Empfehlung: `performance-tuner` beauftragen**,
   falls 0,4 s stoeren; selbst getunt habe ich nichts.
6. **Die Testumgebung sieht die Pixel des Spielers nicht** (Abschnitt 1b). Das
   ist der Befund mit der laengsten Halbwertszeit aus diesem Auftrag und
   betrifft jede kuenftige Geometriezusicherung. Er gehoert in
   `docs/lessons.md`; ich schreibe dort nicht hinein.

**Debt, gefunden und nicht behoben:**

* `scripts/make_screenshots.py` trug einen Kommentar, der nach AK-83 falsch
  geworden waere („dieser Tab oeffnet mit allem zugeklappt"). Den habe ich
  richtiggestellt — es war meine Aenderung, die ihn falsch gemacht haette.
  Sonst nichts an dem Skript.
* `DESIGN_REVIEW.md` Backlog: unter 1250 physischen px wird die **Tab-Leiste**
  scrollbar. Ich habe das bei 833 logischen px (= 1250 physisch) gesehen und
  nicht angefasst; es steht schon als eigener Auftrag im Backlog.
* Die Spalten `Colours`, `Stacking`, `Type` und `Tier` sind bei <= 1067 px
  stark gekuerzt. Die eigentliche Antwort darauf ist die Streichliste in
  `UI_SPEC.md` §8, und die gehoert dem App Designer. Solange sie offen ist,
  ist mein Kompromiss der beste, den elf Spalten hergeben.

**Sicherheitsfunde:** keine. Diese Aenderung liest keine Datei, oeffnet keinen
Socket, baut keinen Pfad und keine Query, und bringt keine neue Abhaengigkeit.

**Neue Abhaengigkeiten:** keine. `nrplanner/cardgrid.py` benutzt nur PySide6,
das schon da war.

---

## 13. DoD

- [x] Anforderung verstanden, Annahmen dokumentiert (Kopfblock, Abschnitt 1)
- [x] Build und Tests gruen in der benannten Testumgebung: Windows 10,
      `-m "not slow"` **722 passed, 5 deselected**, `-m "slow"` **5 passed**.
      Zusaetzlich alle neuen Faelle gegen `QT_QPA_PLATFORM=windows`: 52 passed.
      **Ungeprueft: Linux und macOS** (Windows-only), und ein **gebautes
      Artefakt** (GOAL A9) — dieselben zwei Luecken wie in jedem Zyklus.
- [x] Neue Tests fuer neue Logik: 52 Faelle in vier neuen Dateien plus 8
      Ankerfaelle (662 -> 722), je Waechter eine
      toetende Mutation, gefahren, Ergebnisse in Abschnitt 8
- [ ] **Linter sauber: nicht pruefbar.** Es gibt keinen im Projekt (Frage F-A
      seit vier Zyklen offen). Ersatzweise: `compileall` sauber, und keine
      Zeile ueber 79 Zeichen in den von mir geschriebenen Dateien — das ist
      eine Luecke, kein Beleg.
- [x] Keine Secrets, keine TODOs, kein toter Code
- [x] QA-Akzeptanzkriterien selbst durchgespielt; UX/UI-Vorgaben eingehalten
      oder Abweichung begruendet (Abschnitte 2, 4a, 12)
- [x] Screenshots abgelegt, Abschlussbericht geschrieben
