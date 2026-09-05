```
STATUS: erledigt
AUFTRAG: T-060 — die Restbefunde des Tab-Audits schliessen (QA-140 bis QA-149)
GELESEN: der Auftragstext des `director` (keine Datei unter docs/tasks/ — dort liegt nichts zu T-060, geprueft mit `ls docs/tasks/`) · GOAL.md (A7, A10 bis A14, Erweiterung 2026-09-05) · docs/state.md · docs/berichte/T-059-qa-engineer.md (vollstaendig, alle 18 Abschnitte) · UI_SPEC.md (AK-68, AK-71 bis AK-78, AK-83, AK-91 bis AK-94, AK-99 bis AK-105, §8, §9, §10 und die drei Nachtraege des Directors vom 05.09.) · nrplanner/{app,arsenaltab,bosstab,cardgrid,depthstab,effectstab,eventstab,relicpicker,weaponslots,model,datasource}.py · nrdata/{extract,param}.py · tests/{conftest,rendered,tabtext,test_tab_geometry,test_effects_tab_display,test_red_variants_display,test_nightlord_panel_display,test_world_events_display,test_arsenal_tab_asks_the_facade,test_weapon_damage_golden}.py · scripts/differential/mutate.py · .claude/agent-memory/developer/
GEÄNDERT: nrplanner/{app,arsenaltab,bosstab,cardgrid,depthstab,effectstab,eventstab,relicpicker}.py · nrdata/extract.py · scripts/differential/mutate.py · tests/{conftest,rendered,test_tab_geometry,test_effects_tab_display,test_nightlord_panel_display,test_world_events_display,test_arsenal_tab_asks_the_facade}.py · tests/test_relic_picker_geometry.py (neu) · docs/screenshots/2026-09-05-T060/ (11 Bilder, neu) · docs/berichte/T-060-developer.md (diese Datei). 16 Commits, `86fb5a7` bis `c44af00`, alle auf `docs/audit-and-advisor-design`. Kein push, kein Branch, kein Merge. **Nicht angefasst und nicht committet:** die acht fremden ungespeicherten Dateien (ARCHITECTURE.md, DESIGN_REVIEW.md, GOAL.md, UI_SPEC.md, docs/plan-restarbeiten.md, docs/state.md, qa/findings.md, security/findings.md) und die Berichte anderer Rollen — `git status` zeigt sie unveraendert als ` M` bzw. `??`.
ANNAHMEN: (1) `docs/screenshots/2026-09-05-T060/` ist mein Ordner; die Ordner anderer Rollen (`2026-09-05/`, `2026-09-05-T056/`) habe ich nicht angefasst. (2) Alle Pixelzahlen unten sind **logische px unter der Windows-Plattform, Fusion, dunkle Palette, 150 % Skalierung**, sofern nicht anders bezeichnet — das ist ab jetzt auch die Umgebung der Waechter (QA-146). (3) Der Nutzer laeuft mit einem Bildschirm von 1709 logischen px; 2100 px ist dort nicht darstellbar. (4) QA-147 lese ich als Flaechenbefund, nicht als Aufforderung, einen Splitter zu bauen — Begruendung in Abschnitt 8.
NÄCHSTER: qa-engineer (Retest QA-140 bis QA-149), danach director
BLOCKIERT DURCH: nichts
```

# T-060 — die zehn Restbefunde des Tab-Audits

## 0. Kurzfassung

Alle zehn Befunde sind umgesetzt. **Drei Dinge muss der `director` lesen, bevor
er den Rest ueberfliegt:**

1. **Von den vier fest verdrahteten Spaltenzahlen habe ich eine geaendert, nicht
   vier.** Der Reliktpicker schneidet Karten an — gemessen, behoben, belegt. Die
   anderen drei (`relicpicker.py` Heldenraster im Favoritenmenue,
   `weaponslots.py:59`, `app.py:1416`) schneiden bei **keiner** Fensterbreite
   bis hinunter zum Programm-Minimum von 760 px eine Kachel an; `CardGrid` dort
   einzuziehen waere eine sichtbare Umgestaltung ohne Befund dahinter. Zahlen in
   Abschnitt 7, Entscheidung liegt beim `director`.
2. **Zwei meiner eigenen Waechter waren zahnlos, und die Mutationskampagne hat
   es gezeigt, nicht ich.** Beide sind nachgebessert; beide Vorgaenge stehen
   ungekuerzt in Abschnitt 9, weil sie mehr ueber die Testlage sagen als die
   zwoelf, die auf Anhieb hielten.
3. **Ein Satz, den ich selbst neu geschrieben hatte, war falsch.** Die
   Farblegende im Nightlord-Panel behauptete „alles andere stammt aus den
   Spieldateien"; zwei Sichtungszeilen auf demselben Panel stehen aber in der
   gewoehnlichen Farbe. Der Satz ist gekuerzt; die zwei Zeilen sind ein
   AK-94-Befund, den ich melde statt ihn mitzunehmen (Abschnitt 12).

**Suite.** Vorher `722 passed, 5 deselected`. Jetzt:

| Lauf | Ergebnis |
|---|---|
| `-m "not slow"`, offscreen (Voreinstellung) | **759 passed, 9 skipped, 5 deselected** (308 s) |
| `-m "not slow"`, `QT_QPA_PLATFORM=windows` | **758 passed, 10 skipped, 5 deselected** (320 s) |
| `-m "slow"` | **5 passed, 768 deselected** (51 s) |

Die neun bzw. zehn Uebersprungenen sind kein Ausfall, sondern QA-146s zweite
Haelfte, jetzt sichtbar: offscreen kann kein 833 px breites Fenster zeichnen
(Minimum 964), die Windows-Plattform kein 2100 px breites (Bildschirm 1709). Ein
Fall misst jetzt entweder die Breite, die in seinem Namen steht, oder er sagt,
dass er es nicht kann. **Die Vereinigung beider Laeufe deckt alle fuenf Breiten
ab: 759 + 9 = 758 + 10 = 768.**

**Mutationen.** 14 registriert, 14 gefahren, **14 toeten** — Tabelle in
Abschnitt 9. Zwei weitere waren zuerst registriert, ueberlebten und sind
ersetzt; auch das steht dort.

---

## 1. Reihenfolge und Vollstaendigkeit

| # | Befund | Ort | Zustand |
|---|---|---|---|
| 1 | **QA-141** Picker schneidet 11 von 55 Karten an | `relicpicker.py`, `cardgrid.py` | behoben |
| 2 | **QA-140** Spaltenkoepfe beidseitig beschnitten | `effectstab.py` | behoben |
| 3 | **QA-146** Waechter messen unter anderem Stil | `app.py`, `tests/conftest.py`, `tests/rendered.py` | behoben, Weg begruendet in Abschnitt 4 |
| 4 | **QA-142** `vs standard` ordnet ueber ein `set` | `arsenaltab.py` | behoben, L-006-Suche in Abschnitt 5 |
| 5 | **QA-143** Suche mit vielen Treffern zeigt leere Flaeche | `arsenaltab.py` | behoben |
| 5 | **QA-145** drei Bedeutungen auf einem Gruen | `bosstab.py` | behoben, mit einer Einschraenkung (Abschnitt 12) |
| 6 | **QA-144** `Examples` breiter als `What can be red` | `depthstab.py` | behoben |
| 6 | **QA-147** leeres Detailpanel haelt 330 von 833 px | `bosstab.py` | behoben, Loesungsweg begruendet in Abschnitt 8 |
| 6 | **QA-148** Runen-Leiter ohne Bezugspunkte | `nrdata/extract.py`, `eventstab.py` | behoben, `EXTRACT_VERSION` 10 → 11 |
| 6 | **QA-149** zwei Abschnitte ohne Bezugsgroesse | `bosstab.py` | behoben |

Nicht angefasst, wie beauftragt: der Berater (S7 bis S11), die dreizehn
Streichvorschlaege aus `UI_SPEC.md` §8, der `Build planner` ausser dem Picker.

---

## 2. QA-141 — der Reliktpicker

**Ist-Zustand, gemessen am laufenden Dialog** (Windows-Plattform, Fusion,
150 %), vor der Aenderung:

| Dialogbreite | Sichtbereich | Karten angeschnitten | waagerechte Leiste |
|---|---|---|---|
| **1030** (die er sich selbst gibt) | 988 | **11 von 55** | ja |
| 900 | 858 | 11 von 55 | ja |
| 700 | 658 | 22 von 55 | ja |

Bei 900 und 700 px standen die elf Karten **an derselben Stelle wie bei
1030 px** (x = 801…990): das Raster hat sich nie neu aufgeteilt, der Ueberhang
wurde nur groesser. Bei 900 px fehlten 132 der 190 px je Karte.

**Warum es ohne Zutun des Nutzers brach.** `CARD_WIDTH * COLUMNS + 80` = 1030
laesst 988 px Sichtbereich, und fuenf 190-px-Karten brauchen 982 — das haette
gepasst. Was fehlte, waren die **Standard-Innenraender des `QGridLayout`**, rund
20 px, die niemand mitgerechnet hatte. 1002 in 988.

**Umsetzung.** `cardgrid.CardGrid` mit `margins=(0,0,0,0)`, und die
Oeffnungsbreite aus derselben Arithmetik: neu `cardgrid.room_for(columns,
card_width)` plus die beiden Layoutraender des Dialogs plus die Breite, die die
senkrechte Bildlaufleiste sich selbst gibt (`sizeHint().width()`, gefragt statt
angenommen). `COLUMNS = 5` heisst jetzt `OPENING_COLUMNS = 5` und ist
ausdruecklich nur noch die Startgroesse, keine Behauptung ueber das Raster.

**Nachher:**

| Dialogbreite | Sichtbereich | Spalten | angeschnitten | Leiste |
|---|---|---|---|---|
| **1024** (Startgroesse) | 982 | 5 | **0** | nein |
| 900 | 858 | 4 | **0** | nein |
| 700 | 658 | 3 | **0** | nein |

Bilder: `docs/screenshots/2026-09-05-T060/picker-opening.png`, `picker-900.png`.

---

## 3. QA-140 — die Spaltenkoepfe

**Ist-Zustand, gemessen** (Kopftextbreite gegen Sektionsbreite, alle elf
Spalten, fuenf Fensterbreiten):

| Fensterbreite | Koepfe zu breit fuer ihre Sektion |
|---|---|
| 833 | **7** (`Copies`, `Colours`, `Relic slots`, `Avg chance`, `Best chance`, `Stacking`, `Comes with curse`) |
| 1067 | **4** (`Relic slots`, `Avg chance`, `Best chance`, `Comes with curse`) |
| 1320 (Standardmass) | 1 (`Comes with curse`) |
| 1600 / 2100 | 0 |

Das reproduziert QA-140 genau. Qt zeichnet einen zentrierten Kopf und schneidet
ihn **an beiden Enden** ab — deshalb `vg chanc` und `est chanc`, zwei Koepfe,
die derselbe Text zu sein scheinen.

**Umsetzung.** `EffectTable.set_headings(headings, tips)` haelt die vollen Namen
im Widget; `fit_columns` kuerzt jeden Kopf mit `QFontMetrics.elidedText(...,
Qt.ElideRight, room)` auf den Platz, den der **Stil** seiner Beschriftung laesst;
jeder Kopf traegt seinen vollen Namen als erste Zeile des Tooltips. Vor jeder
Messung werden die vollen Namen zurueckgeschrieben.

Zwei Details, die je eine Messung gekostet haben:

* `room` kommt aus `QStyle.SE_HeaderLabel`, nicht aus einem geschaetzten Rand.
  Der Rand ist unter Fusion **2 px je Seite**, unter windowsvista **4** — genau
  die Falle, um die es in QA-146 geht.
* Die `QStyleOptionHeader` traegt `State_Horizontal`. Ohne dieses Flag zieht
  `QCommonStyle` den **Sortierpfeil** nicht von der Beschriftungsflaeche ab, und
  `Type` — die Spalte, nach der diese Tabelle von Anfang an sortiert — kam als
  `y.` heraus: eine in der Mitte durchgeschnittene Auslassung, also genau der
  Fehler, den ich eine Spalte weiter gerade behoben hatte. Der Fehler stand im
  ersten Screenshot; ohne den Screenshot waere er geblieben.

**Nachher**, gemessen: bei jeder der fuenf Breiten sind **0** Koepfe zu breit
fuer ihre Sektion, **11 von 11** tragen ihren vollen Namen im Tooltip, und jeder
gekuerzte endet auf `…`.

| Fensterbreite | Koepfe gekuerzt | wie sie aussehen |
|---|---|---|
| 833 | 8 | `…` (`Type`, mit Sortierpfeil), `Co…`, `Co…`, `Re…`, `Av…`, `Be…`, `St…`, `Co…` |
| 1067 | 4 | `Relic sl…`, `Avg ch…`, `Best c…`, `Comes…` |
| 1320 | 1 | `Comes with c…` |
| 1600 / 2100 | 0 | — |

Bilder: `effects-833.png`, `effects-1067.png`, `effects-1320.png`.

**Was bei 833 px uebrig bleibt, und ich melde es als Rest, nicht als Erfolg.**
Dort sitzen neun Spalten auf Qts eigener Mindestbreite von 28 px. Drei Koepfe
lesen sich dann als `Co…` (`Copies`, `Colours`, `Comes with curse`) und sind
untereinander nicht zu unterscheiden. Das ist die vom `director` genehmigte
AK-77-Ausnahme in ihrer haesslichsten Auspraegung. Der Unterschied zum vorherigen
Zustand ist trotzdem real und der, um den es dem Befund ging: `cha` sieht aus wie
ein Wort, `Co…` sagt „hier steht mehr, fahr drueber". Bei 1067 px — der Breite,
an der QA-140 aufgehaengt war — sind `Avg ch…` und `Best c…` wieder
auseinanderzuhalten. **Frage an den `ui-ux-designer`** in Abschnitt 12.

---

## 4. QA-146 — die Messumgebung, und welchen Weg ich gewaehlt habe

Der Auftrag liess zwei Wege zu. **Ich habe den ersten genommen: die Umgebung
angleichen** — und zwar so, dass es keine zweite Stelle mehr gibt, an der sie
auseinanderlaufen kann.

`main()` sagte den Stil und die Palette selbst; die Suite sagte nichts. Beides
steht jetzt in **`nrplanner.app.apply_appearance(app)`**, und `main()` wie
`tests/conftest.py::qapp` rufen dieselbe Funktion. Session-weit gesetzt, nicht je
Fenster: `setStyle` ist global, und angewandt vom ersten Fall, der zufaellig ein
Fenster baut, haenge jede Pixelzahl des Laufs an der Reihenfolge der Faelle.

**Warum ich nicht den zweiten Weg genommen habe** (im Testmodul festhalten, was
plattformunabhaengig ist): das haette die Zahlen in den Berichten korrekt
gemacht und die Ursache stehen lassen. Die Ursache ist, dass zwei Stellen
dasselbe sagen mussten.

**Zweite Haelfte des Befunds, und sie kostet sichtbar etwas.** `laid_out` prueft
jetzt, ob das Fenster die angeforderte Breite wirklich bekommen hat, und
ueberspringt sonst mit der erreichten Zahl in der Meldung. Ergebnis oben: neun
Faelle offscreen bei 833 px, zehn unter Windows bei 2100 px. **Das ist ein
Verlust an Bequemlichkeit und ein Gewinn an Wahrheit** — vorher hat der Fall
`[833]` offscreen bei 964 px gemessen und 833 in den Namen geschrieben. Wer alle
fuenf Breiten sehen will, faehrt die Suite zweimal; beide Laeufe stehen oben.

**Der Waechter dazu** vergleicht nicht gegen das Literal `"Fusion"`, sondern
prueft, dass `apply_appearance` auf die laufende Anwendung angewandt **nichts
mehr aendert**. Damit ist die Zusicherung „Programm und Suite messen dasselbe",
nicht „beide messen Fusion" — und die faellt auch dann, wenn kuenftig etwas
anderes gesetzt wird und die Suite nicht mitgeht.

---

## 5. QA-142 — und die geforderte projektweite Suche (L-006)

**Fix:** die Vereinigung laeuft in der Reihenfolge, in der die `Scaling`-Zeile
darueber ihre Stats nennt (`stats_of(scaling, base_scaling)`). Belegt ueber vier
Prozesse mit `PYTHONHASHSEED=0..3`: **dieselbe Reihenfolge in allen vieren**, und
die beiden Zeilen einer Kachel stimmen ueberein — `Scaling STR 33 · DEX 50 · INT
29` ueber `vs standard STR -21 · DEX +6 · INT +29`. Vorher vier Seeds, vier
Reihenfolgen. **46 der 77 Erstkacheln** tragen beide Zeilen und werden vom
Waechter verglichen.

### „Gibt es weitere Mengenoperationen, die bis zum Anzeigetext durchschlagen?"

**Antwort: nein. `arsenaltab.py:508` war die einzige.** Zwei unabhaengig
formulierte Suchmasken ueber `nrplanner/` und `nrdata/`:

| Maske | Muster | Treffer |
|---|---|---|
| 1 | `\.keys\(\)\s*[|&^-]` · `\bset\(` · `\bfrozenset\(` · `[|&^]\s*\w+\.keys\(\)` | **53** |
| 2 | `for … in …{…}` · `for … in (set\|frozenset)\(` · Mengenliteral auf Modulebene | **25** |

Jeden Treffer, dessen Ergebnis in eine Anzeige laufen koennte, habe ich einzeln
verfolgt. Sechs waren naeher zu pruefen, alle sechs sind unbedenklich:

| Stelle | Warum unbedenklich |
|---|---|
| `effectstab.py:566,587` | Farben werden unioniert und in `:593` **sortiert** ausgegeben |
| `model.py:737` (`for attr in set(low) \| set(high)`) | schreibt in ein `dict`, dessen Schluessel schon aus den Grundwerten stehen; die Anzeige laeuft ueber die feste Liste `model.ATTRIBUTE_ORDER` — die Mengenordnung erreicht den Bildschirm nicht |
| `weaponslots.py:145` | Rueckgabe wird nur mit `in` geprueft, nie iteriert |
| `nrdata/extract.py:2614` | nur bei `len(shared) == 1` benutzt, also einelementig |
| `nrdata/extract.py:2741` (`_named_stats`) | Ergebnis wird nur auf Mengengleichheit verglichen |
| `advisor/candidates.py:155` | nur `in`-Pruefung |

Der Vollstaendigkeit halber: `nrdata/bossdata.py:215` und `extract.py:2262`
sortieren bereits ausdruecklich.

---

## 6. QA-143 — die leere Flaeche

Die Schwelle „bei bis zu 60 Treffern alles aufklappen" hatte keinen `else`-Fall.
Bei mehr als 60 griff **keiner** der beiden Zweige, und der Tab zeichnete drei
zugeklappte Ueberschriften ueber Leere. Jetzt gilt die Erstansichts-Regel auch
fuer die Suche: ein Unterabschnitt klappt auf. Das ist der billigste Weg zum
Prinzip „kein Zustand dieses Tabs zeigt eine leere Flaeche, wo Inhalt hingehoert"
und baut kein neues Verhalten — es ist dieselbe Regel, die AK-83 schon fuer die
Erstansicht setzt.

Beleg am laufenden Fenster: `weapons-search-a.png` — `a`, **1835 shown**,
`Weapons (1680)` → `Axe (77)` offen, Kacheln auf der Seite. Der Fall „0 Treffer"
zeigt weiterhin nichts, und das ist richtig: dort gehoert kein Inhalt hin, und
die Bestandszeile sagt es.

---

## 7. Die vier fest verdrahteten Spaltenzahlen — hier weiche ich vom Auftrag ab

Der Auftrag sagt: *„Zieh die vier Stellen nach."* Ich habe **eine** nachgezogen
und melde die anderen drei, weil die Messung die Begruendung des Auftrags fuer
sie nicht traegt. Der Auftrag stuetzt die Kehrtwende ausdruecklich darauf, dass
die Spaltenzahlen **sichtbar** brechen (*„sie sind sichtbar, jetzt, im
Auslieferungszustand"*). Fuer den Picker stimmt das (Abschnitt 2). Fuer die
anderen drei habe ich es geprueft und es stimmt nicht:

| Stelle | Kachelbreite | Raum, den sie bekommt | angeschnitten | waagerechte Leiste |
|---|---|---|---|---|
| `app.py:1416` Heldenraster der Seitenleiste | 56 px, 5 je Reihe = **296 px** | Bereich 373–430 px, Mindestbreite des Bereichs **300** | **0** bei 760 / 833 / 1067 / 1320 / 1600 / 1709 px Fensterbreite | keine |
| `weaponslots.py:59` Waffenslots | 116–126 px, 3 je Reihe | Bereich 326–356 px | **0** bei denselben sechs Breiten | keine |
| `relicpicker.py:31` Heldenraster im Favoritenmenue | 52 px, 5 je Reihe | `QMenu`, misst sich selbst auf **292 px** | **0**, und ein `QMenu` wird vom Nutzer nicht in der Groesse veraendert | — |

760 px ist die Mindestbreite des ganzen Fensters, also die schmalste Lage, die
ein Spieler herstellen kann.

**Was ein Umbau dort kosten wuerde.** `CardGrid` rechnet die Spaltenzahl aus der
Breite. Das Heldenraster bekaeme bei 430 px Bereichsbreite **sieben** Spalten
statt fuenf — die zehn Nightfarer stuenden nicht mehr 2x5 wie im Spiel, sondern
7+3, und zwar **sofort beim Start**, nicht erst in einer Randlage. Das ist eine
Umgestaltung, kein Richtigstellen, und der Auftrag verbietet mir beides:
„Keine neuen Funktionen" und „nur richtigstellen und sichtbar machen".

**Was ich dem `director` zur Entscheidung vorlege.** AK-72 laesst zwei Lesarten
zu. Als **Formregel** („kein Raster hat eine feste Spaltenzahl") sind alle drei
Stellen offen, und die Entscheidung, ob das 2x5-Raster der Nightfarer aufgegeben
wird, gehoert dem `ui-ux-designer`. Als **Ergebnisregel** („nie wird eine Kachel
teilweise gezeichnet" — so begruendet AK-72 sich selbst) sind alle drei bereits
erfuellt. Ich empfehle die zweite Lesart und einen Vermerk, dass die drei festen
Zahlen von einer Mindestbreite gedeckt sind, die **nicht** an ihnen haengt: wer
`panel.setMinimumWidth(300)` auf 250 senkt, schneidet das Heldenraster an, ohne
dass ein Test es merkt. Das ist die verbleibende Latenz und der ehrliche Grund,
die Stellen nicht ganz zu vergessen.

---

## 8. QA-147 — warum kein Splitter

DR-013 hatte einen Splitter als Richtung genannt; ich habe erst einen gebaut und
ihn wieder ausgebaut. Der Grund steht hier, weil der `qa-engineer` sonst nach ihm
sucht.

Ein Splitter **loest den Befund nicht**: eine Flaeche ohne Streckfaktor behaelt
ihre Breite, bis die andere nichts mehr hat. Gemessen mit Splitter und
`setStretchFactor(1, 0)`: bei 833 px hielt das Panel weiterhin **330** px. Mit
gleichmaessiger Streckung waere es bei 1709 px auf 570 px gewachsen — Platz, den
der Textspalte niemand gegeben haben wollte. Ein Splitter mit einer Obergrenze
obendrauf braucht ausserdem eine Regel, wann er die Groesse des Nutzers
ueberschreibt, und das ist neue Interaktion, die niemand bestellt hat.

**Gewaehlt: die Breite haengt an der des Tabs.** `DETAIL_WIDTH` (330) wo Platz
ist, hoechstens ein Drittel des Tabs wo nicht, nie unter einer Kartenbreite.
Gemessen, und ohne Hysterese (schmal → breit → schmal gibt dieselben Zahlen):

| Fensterbreite | Karten vorher | Panel vorher | Karten nachher | Panel nachher |
|---|---|---|---|---|
| 760 | 390 | 330 | **468** | **252** |
| **833** | 463 | 330 | **517** | **276** |
| 1067 | 697 | 330 | 697 | 330 |
| 1320 / 1600 / 1709 | unveraendert | 330 | unveraendert | 330 |

Ab 1067 px bewegt sich nichts. Bild: `nightlords-833.png`.

---

## 9. Waechter und toetende Mutationen

**Neu: 13 Testfaelle in sechs Dateien**, davon eine neue Datei
(`tests/test_relic_picker_geometry.py`; die vorherige Abdeckung des Pickers war
*keine* — zwei unabhaengige Suchen ueber `tests/` nach `relicpicker` und nach
`RelicPicker` finden zwei Dateien, die den Dialog oeffnen und schliessen und
kein gerendertes Rechteck lesen).

Kampagne: **jede Mutation in einen frischen `git archive HEAD`-Baum, volle
schnelle Suite.** Basis-Commit fuer alle vierzehn Zeilen unten:
**`c44af0099ba50d38e1175638810a818e53c35fb4`**. Der Ankertest
`test_every_mutation_still_finds_its_anchor_in_the_real_source[...]` faellt in
jedem mutierten Baum als Selbstverstaendlichkeit und ist **nicht** mitgezaehlt.

| Mutation | faellt (ohne Anker) | welche Faelle |
|---|---|---|
| `picker-back-to-a-fixed-column-count` | **3** | `test_every_card_in_the_picker_is_drawn_whole[None/900/700]` |
| `picker-opening-width-without-any-chrome` | **1** | `test_the_picker_opens_wide_enough_for_the_cards_it_opens_with` |
| `effect-headings-drawn-whole-or-not-at-all` | **5** | `test_no_column_heading_is_drawn_cut_off[1067/1250/1600/2100]`, `test_a_narrow_window_does_not_shrink_the_columns_for_good` |
| `effect-heading-tooltip-without-the-name` | **5** | `test_the_slot_column_says_what_it_counts`, `test_every_shortened_heading_says_so_and_keeps_its_name[1067/1250/1600/2100]` |
| `effect-headings-measured-while-elided` | **1** | `test_a_narrow_window_does_not_shrink_the_columns_for_good` |
| `suite-measures-under-another-style` | **1** | `test_the_suite_measures_under_the_appearance_the_program_starts_with` |
| `vs-standard-back-to-a-set` | **1** | `test_a_tile_names_its_stats_in_one_order_on_both_of_its_rows` |
| `arsenal-search-back-to-an-empty-page` | **1** | `test_a_search_with_more_hits_than_the_cap_still_draws_a_tile` |
| `arsenal-opens-on-three-collapsed-headings-again` *(Anker nachgezogen)* | **9** | u. a. `test_the_arsenal_shows_a_tile_without_being_asked`, `test_a_search_with_more_hits_than_the_cap_still_draws_a_tile`, 4x `test_every_weapon_tile_is_drawn_whole`, 2x `test_weapon_tile_value_wrap` |
| `examples-column-back-to-its-natural-width` | **3** | `test_the_examples_column_never_outgrows_the_column_it_illustrates[1067/1250/1600]` |
| `nightlord-panel-back-to-a-fixed-width` | **1** | `test_the_detail_panel_gives_way_at_the_narrowest_window_there_is` |
| `sighting-colour-back-without-its-legend` | **1** | `test_the_colour_kept_for_sightings_is_named_where_it_is_used` |
| `buff-and-parts-figures-without-a-reference` | **1** | `test_no_block_of_figures_is_left_without_its_reference` |
| `rune-ladder-back-to-seven-bare-figures` | **2** | `test_the_rune_ladder_says_which_step_each_figure_belongs_to`, `test_the_rune_claim_carries_the_figures_that_were_loaded_for_it` |

### Zwei Waechter, die zuerst zahnlos waren — und wie es herauskam

Das ist der Teil des Berichts, den ich am wenigsten gern schreibe und der am
meisten sagt.

**(a) `picker-opening-width-guessed-again` — die Mutation ueberlebte.** Ich hatte
die alte Konstante `CARD_WIDTH * OPENING_COLUMNS + 80` als toetende Mutation
registriert. Ergebnis: **1 failed (der Anker), 756 passed.** Der Grund ist
lehrreich: 1030 px lassen 988 px Sichtbereich, und fuenf Karten brauchen ohne
Rasterrand 982. **Was QA-141 geschlossen hat, ist `CardGrid` — nicht die
Herleitung der Oeffnungsbreite.** Die Herleitung schuetzt gegen einen Stil mit
breiteren Bildlaufleisten, und den kann diese Maschine nicht herstellen. Beides
steht jetzt so in der Registry; die Ersatzmutation laesst die Randbreiten ganz
weg und wird gefangen.

**(b) `nightlord-panel-back-to-a-fixed-width` — die Mutation ueberlebte.**
Ergebnis: **1 failed (der Anker), 757 passed.** Mein Waechter war auf die fuenf
Abnahmebreiten parametrisiert, und ein festes 330-px-Panel liegt bei vier von
ihnen **innerhalb** seines Drittels. Die fuenfte ist 833 px — und die
ueberspringt der Standardlauf seit meiner eigenen QA-146-Aenderung. *Ein
Waechter, der nur bei der einen Breite beisst, die der Standardlauf nicht
erreicht, ist keiner.* Neuer Fall
`test_the_detail_panel_gives_way_at_the_narrowest_window_there_is`: er verlangt
ein Fenster, das schmaler ist als alles, und misst, was die Plattform hergibt
(760 unter Windows, 964 offscreen). Er toetet die Mutation auf beiden
Plattformen.

**Und einer, dessen Registry-Eintrag falsch war.**
`effect-headings-measured-while-elided` nannte
`test_the_two_reading_columns_hold_their_floors` als toetenden Fall. Die
Kampagne sagt etwas anderes, und sie hat recht: die Untergrenzen halten so oder
so, weil als Stummel gemessene Beschriftungsspalten **weniger** wollen und die
beiden Lesespalten dadurch mehr bekommen. Was faellt, ist der neue Fall — und
**nur in einer bestimmten Reihenfolge**: schmal, `refresh` *waehrend* schmal,
dann breit. Erst verbreitern und dann aktualisieren hinterlaesst keine Spur.
Gemessen im mutierten Baum: zurueck bei 1600 px stand `Type` auf 37 px statt 53,
`Relic slots` auf 51 statt 82, `Avg chance` auf 52 statt 91, und fuenf Koepfe
waren noch gekuerzt, wo alle elf ganz gewesen waren. Der Eintrag nennt jetzt den
richtigen Fall und die Reihenfolge.

---

## 10. Screenshots

`docs/screenshots/2026-09-05-T060/`, elf Bilder. Windows-Plattform, Fusion und
dunkle Palette wie `app.main` sie setzt, `window.grab()` ueber das ganze Fenster,
mit echtem Timer statt `processEvents` — der Grund steht in
`scripts/make_screenshots.py` und der `qa-engineer` hat ihn in T-059 §14
bestaetigt.

Der Screenshot `nightlords-panel-notes.png` ist der, der den falschen Satz in
meiner eigenen Legende gefunden hat (Abschnitt 12). Er ist deshalb so
aufgehoben, wie er entstanden ist.

---

## 11. Definition of Done

- [x] Anforderung verstanden, Annahmen im Kopfblock
- [x] Build und Tests gruen in der benannten Umgebung — **zwei** Umgebungen,
      Zahlen in Abschnitt 0; `-m "slow"` 5 passed, also sind die
      `nrdata`-Parser mit echten Spieldateien gelaufen (die
      `EXTRACT_VERSION`-Anhebung macht das noetig)
- [x] Neue Waechter fuer jede neue Logik, jeder mit gefahrener toetender
      Mutation
- [x] Keine Secrets, keine TODOs, kein toter Code — `git diff` gegen `354ef82`
      ueber `nrplanner/ nrdata/ tests/ scripts/` enthaelt **0** Zeilen mit
      `TODO|FIXME|XXX|HACK|pending`; `PARAM_NAME` und `import re` in
      `eventstab.py` sind mit ihrem Anlass entfernt worden
- [x] Zeilenlaenge: 3 eingefuegte Zeilen ueber 79 Zeichen, umgebrochen in einem
      eigenen Formatierungs-Commit (kein Linter im Projekt — Frage F-A steht
      seit Zyklus 12 offen)
- [x] Doku: die Begruendungen stehen als Kommentar an der Codestelle, wie im
      Projekt ueblich; die Fremddateien habe ich **nicht** angefasst
- [ ] **Ungeprueft:** Linux, macOS, andere Skalierungen als 150 %, ein gebautes
      Artefakt (A9), Tastaturbedienung und Kontrastwerte

**Nicht als erledigt gemeldet, weil ich es nicht belegen kann:** dass ein
nicht-technischer Spieler die gekuerzten Koepfe bei 833 px versteht. Das ist A11
und gehoert dem `power-user`.

---

## 12. An den `ui-ux-designer`

1. **Drei Koepfe lesen sich bei 833 px als `Co…`** (`Copies`, `Colours`,
   `Comes with curse`) und sind untereinander nicht zu unterscheiden; `Type`
   steht dort als blosses `…`, weil der Sortierpfeil von 28 px Sektionsbreite
   10 px fuer den Text uebriglaesst. Alle vier tragen ihren Namen im Tooltip.
   Ich sehe drei Auswege und keiner davon ist meine Entscheidung: kuerzere
   Kopfnamen, ein Kopf ueber zwei Zeilen, oder das ausdrueckliche Zugestaendnis,
   dass die Tabelle unter 1000 px nicht mehr gelesen, sondern nur noch
   ueberflogen wird.
2. **Zwei Sichtungszeilen tragen die Sichtungsfarbe nicht** — `Set off by`
   (vier Nightlords) und der Ausloeser-Zusatz einer `Defence`-Zeile (Libra).
   Beide sind laut den Kommentaren im Modul Sichtungen; gezeichnet werden sie
   in der gewoehnlichen Farbe. Das ist ein AK-94-Fall, nicht QA-145, und
   deshalb habe ich ihn **nicht** mitgenommen. Er hat aber meine Legende falsch
   gemacht: sie hiess zuerst *„Lines in this colour were watched in play.
   Everything else on this panel is read from the game's own files."* — der
   zweite Satz stimmte nicht. Er ist gestrichen; die Legende sagt jetzt nur, was
   die Farbe bedeutet. Der Fall bei der `Defence`-Zeile ist unangenehm, weil dort
   ein Satzteil Sichtung und der Rest extrahiert ist; eine Farbe fuer die ganze
   Zeile waere wieder falsch.
3. **Wortlaute, die ich neu geschrieben habe** und die dir gehoeren, falls du sie
   anders willst — alle drei im Stil der drei AK-91-Zeilen:
   * `IT BUFFS ITSELF`: *„Buff steps multiply this Nightlord's own attack and
     stance figures while the step is on; the files give no duration for them,
     and `always on` means no trigger is recorded. Defence steps carry their own
     duration."*
   * `BODY PARTS`: *„Damage dealt to that part, against the same hit anywhere
     else on this Nightlord. The files number the parts and never say which part
     is which, so a number here is worth more than the name beside it."*
   * `IT IS WEAKENED`, ergaenzt um die Farbaussage: *„… these multiply its normal
     figures — green, because every one of them is in your favour. …"*
   * Runen-Leiter (aus dem Extraktor): *„Expedition progress moves it up a
     7-step ladder: step 1 ×1, then ×1.1, ×1.125, ×1.2, ×1.225, ×1.25, ×1.275 at
     step 7. The game's files number the steps and do not say how many
     expeditions reach each one."*
4. **Der `Red variants`-Tab hat bei 833 px zwei exakt gleich breite
   Textspalten** (315 / 315). AK-99 sagt „nie breiter", also ist es erfuellt;
   ob gleich breit gestalterisch gewollt ist, entscheidest du.

---

## 13. An den `qa-engineer`

**Was zu pruefen ist, und wo ich die Kanten sehe:**

* **QA-140:** die drei `Co…` bei 833 px (oben). Und: der Kopf-Tooltip enthaelt
  jetzt den Namen **plus** die alte Erklaerung, durch `\n` getrennt. AK-78
  verlangte den Erklaersatz „wortgleich" — er steht wortgleich da, aber nicht
  mehr allein. Der gepinnte Test vergleicht auf
  `f"{SLOTS_HEADER} {SLOTS_TIP}"`. Wenn du das fuer eine Verletzung von AK-78
  haeltst, ist das ein Befund und ich baue es um.
* **QA-141:** der Picker mit **wenigen** Relikten (ein Slot mit weniger als
  fuenf) — dann gibt es keine volle Reihe; mein Waechter ueberspringt diesen Fall
  ausdruecklich mit Meldung. Und der Fall „Suche im Picker filtert auf 0
  Treffer": dann steht dort nur die Custom-Kachel, was richtig ist, aber ich habe
  es nicht am Bild geprueft.
* **QA-142:** Ich habe die Ordnung ueber vier Hashseeds belegt, aber nur an den
  46 Erstkacheln. Waffen anderer Familien (Suche aufklappen) habe ich nicht
  einzeln durchgesehen.
* **QA-143:** Suche mit genau 60 und mit genau 61 Treffern — die Schwelle selbst
  habe ich nicht bewegt und den Uebergang nicht am Bild geprueft.
* **QA-147:** Fenster **waehrend** eines geoeffneten Detailpanels von 1600 auf
  760 und zurueck ziehen. Ich habe die Folge einmal gemessen (keine Hysterese),
  aber nicht mit einem ausgewaehlten Nightlord und langem Panelinhalt.
* **QA-148:** Der Text kommt aus dem **Datensatz**, nicht aus dem Renderer. Wenn
  du gegen einen aelteren Snapshot pruefst, siehst du den alten Satz; die
  `EXTRACT_VERSION` steht deshalb jetzt auf 11. Auf einer Maschine ohne
  Spielinstallation ist das ein Skip, kein Fehler.
* **Die zwei Ueberlebenden aus Abschnitt 9** waeren die zwei Stellen, an denen
  ich als Erstes nach einem weiteren zahnlosen Waechter suchen wuerde.

**Was ich ausdruecklich nicht geprueft habe:** ob die Kopf-Tooltips auf einem
System mit vergroesserter Schrift noch lesbar sind; ob `Set off by` in der
falschen Farbe einem Leser tatsaechlich auffaellt; alle sechs Karten des
`Red variants`-Tabs nach dem Spaltenumbau (ich habe die Voreinstellung
`Default Limveld` am Bild und alle Breiten am Widget geprueft).

---

## 14. An den `director`

**Entscheidungen, die ich brauche:**

1. **Die drei uebrigen Spaltenzahlen** (Abschnitt 7). Meine Empfehlung: als
   erfuellt vermerken, mit der Notiz zur Latenz. Wenn du die Formregel willst,
   ist es ein `ui-ux-designer`-Auftrag, kein `developer`-Auftrag — es aendert das
   2x5-Raster der Nightfarer sofort beim Start.
2. **AK-78 und der erweiterte Kopf-Tooltip** (Abschnitt 13, erster Punkt).

**Schulden und Funde ausserhalb des Auftrags:**

* **AK-94-Luecke:** `Set off by` und der Ausloeser-Zusatz der `Defence`-Zeile
  sind Sichtungen in der Farbe extrahierter Werte (`bosstab.py`, Zeilen 730 und
  736). Aufwand klein, Risiko klein; die zweite Stelle braucht eine
  Wortlautentscheidung des `ui-ux-designer`, weil dort ein Satzteil Sichtung und
  der Rest Datei ist.
* **`tests/golden/weapon_damage.json` traegt weiter `"extract_version": 10`,**
  waehrend der Baum auf 11 steht. Der Stempel wird von keinem Test geprueft, und
  der Kopf der Golden-Datei erlaubt eine Neuaufnahme nur bei einem echten
  Eingabewechsel — QA-148 aendert keine Waffenzahl. Ich habe ihn deshalb stehen
  lassen. Wenn du willst, dass der Stempel mitzieht, ist das ein eigener,
  begruendeter Neuaufnahme-Commit.
* **Zwei Waffenkacheln-Faelle haengen an `arsenal-opens-on-...`:**
  `test_weapon_tile_value_wrap.py` faellt mit, wenn die Erstansicht keine Kachel
  mehr baut. Kein Fehler, aber es heisst, dass diese zwei Faelle stillschweigend
  von einer anderen Zusicherung abhaengen.
* **Kein Sicherheitsfund.** Kein Datei-, Socket-, Shell- oder Pfadzugriff neu,
  keine neue Abhaengigkeit, kein Secret. Der einzige externe Eingang, den ich
  angefasst habe, ist `nrdata/extract.py::_rune_scaling`, und der liest
  weiterhin nur `ClearCountCorrectParam` und formatiert Zahlen.
* **Keine Performance-Auffaelligkeit,** die ich dem `performance-tuner` melden
  wuerde. Das Eliden laeuft ueber elf Koepfe je Groessenaenderung; die Suite ist
  von 231 s auf 308 s gewachsen, und das kommt aus 37 zusaetzlichen Faellen, die
  je ein ganzes `Planner`-Fenster bauen — nicht aus dem Programm.

**Was diese Aufgabe an Zeit gekostet hat, damit du die naechste planen kannst:**
die Mutationskampagne. 14 Mutationen zu je etwa 5 Minuten und 20 Sekunden sind
75 Minuten reine Laufzeit, und zwei Durchlaeufe waren noetig, weil zwei
Waechter beim ersten Mal nichts fingen. Das war es wert — beide Male hat die
Kampagne einen Fehler gefunden, den kein gruener Lauf gezeigt haette.
