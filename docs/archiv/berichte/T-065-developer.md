```
STATUS: erledigt
AUFTRAG: T-065 — die letzten zwei Luecken vor A11, plus zwei Kleinschulden (QA-150 bis QA-153)
GELESEN: GOAL.md (A7, A10-A14, Erweiterung 2026-09-05) · qa/findings.md (QA-140 bis QA-153,
  Retest-Block T-064) · docs/berichte/T-064-qa-engineer.md · docs/berichte/T-060-developer.md
  (Abschnitte 11-13) · nrplanner/{bosstab,effectstab,cardgrid,depthstab,deeptab,eventstab,
  eventlore,relicpicker,weaponslots,app}.py · nrdata/extract.py · tests/{conftest,rendered,
  tabtext,test_nightlord_panel_display,test_tab_geometry,test_weapon_damage_golden,
  test_differential_track}.py · tests/golden/weapon_damage.json ·
  scripts/{capture_weapon_damage,differential/mutate}.py · .claude/agent-memory/developer/
  (screenshot-evidence, pixel-measurements, guard-teeth-traps, mutation-campaign-cost,
  scope-and-reporting)
  NICHT gelesen: docs/state.md und docs/plan-restarbeiten.md — im Arbeitsbaum uncommittet
  geaendert (` M docs/state.md`), gehoeren dem director; ich habe sie nicht angefasst.
GEÄNDERT: nrplanner/bosstab.py · nrplanner/effectstab.py · tests/test_nightlord_selection.py (neu)
  · tests/test_heading_hint.py (neu) · tests/test_nightlord_panel_display.py ·
  tests/test_weapon_damage_golden.py · tests/golden/weapon_damage.json ·
  scripts/differential/mutate.py · docs/screenshots/2026-09-05-T065/ (7 Bilder, neu) ·
  docs/berichte/T-065-developer.md (diese Datei, uncommittet) ·
  .claude/agent-memory/developer/{MEMORY.md,project_screenshot_evidence.md,
  project_mutation_campaign_cost.md} (gitignoriert)
  Sieben Commits, 1eafee3 bis c656e6c. Nicht angefasst und nicht committet: docs/state.md,
  qa/findings.md, docs/berichte/T-064-qa-engineer.md, docs/tasks/T-067.md.
ANNAHMEN: (1) „Zieh den Stempel nach" heisst den Wert korrigieren, nicht neu aufzeichnen — die
  36 Faelle laufen heute gegen Extraktor-11-Daten und sind gruen, also ist `11` eine geprueste
  Aussage und keine Reparatur. (2) Der Auftrag nennt bei QA-152 zwei Stellen; ich habe genau die
  zwei geaendert und die dritte Fundstelle derselben Eigenschaft (Deep of Night) nur gemeldet.
  (3) Meinen eigenen Bericht habe ich **nicht** committet — T-038 bis T-063 wurden gesammelt vom
  director nachgezogen; ich folge der beobachteten Praxis. Sag Bescheid, wenn ich ihn selbst
  committen soll.
NÄCHSTER: qa-engineer
BLOCKIERT DURCH: nichts
```

# T-065 — QA-150 bis QA-153

## 0. Zahlen

| Lauf | Ergebnis |
|---|---|
| `-m "not slow"` vorher (Auftrag, T-064 bestaetigt) | 759 passed, 9 skipped, 5 deselected |
| `-m "not slow"` auf dem Endstand (c656e6c) | **781 passed, 9 skipped, 5 deselected** (349,6 s) |
| `-m "slow"` | **5 passed**, 790 deselected (54,4 s) |
| Mutationen | **6 von 6 getoetet**, 0 Ueberlebende |

+22 Faelle: 7 Auswahl, 6 Kopf-Tooltip, 2 Sichtungsfarbe, 1 Stempel, 6 neue
Ankerpruefungen in `test_differential_track.py`.

Umgebung aller Oberflaechenzahlen unten, wo nicht anders gesagt: **Windows,
Fusion, 150 % Skalierung, logische px**, echtes Fenster (`QT_QPA_PLATFORM=windows`).
Die Suite misst offscreen; wo eine Zahl von dort stammt, steht es dabei.

---

## 1. QA-150 — das Raster zeigt jetzt, welche Karte das Panel beschreibt

**Umgesetzt** in `nrplanner/bosstab.py`: `BossCard._apply_appearance()`,
`BossCard.set_selected()`, `BossCard.selected`, `BossTab._mark_selected()`,
Aufruf als erste Zeile von `BossTab.show_detail()`.

**Zwei Kanaele, nicht einer.** Der Rand ist vergeben: eine Karte mit
Everdark-Zwilling traegt dort `DEEP` (#9a6fc4). Eine Auswahl, die nur die
Randfarbe tauscht, waere eine Nuance neben einer Markierung mit ganz anderer
Bedeutung. Die gewaehlte Karte bekommt deshalb **Rand in ACCENT** (#c8a45c)
**und** eine **Fuellung** — `rgba(200, 164, 92, 60)`. Das ist kein neuer Wert:
genau diese Tinte waehlt der `Red variants`-Tab (`depthstab.py:214`) und die
`World Events`-Liste (`eventstab.py:126`) schon heute fuer eine ausgewaehlte
Zeile. Drei der sechs Tabs sagen „diese hier" jetzt gleich (A13).

**Randbreite bleibt 1 px.** Eine dickere Umrandung haette den Karteninhalt um
ein Pixel nach innen geschoben, und das Raster haette bei jedem Probieren
gezuckt.

**Ein echter Fehler, den erst der Klick-Fall gefunden hat.** `BossCard.clicked`
ist `Signal(dict)`; Qt marshallt den Eintrag darueber. Was nach einem Klick in
`show_detail` ankommt, ist ein **gleicher, aber nicht derselbe** dict —
gemessen: `emitted is card.boss` False, `==` True. Mein erster Entwurf verglich
per `is` und markierte damit **nichts**, lautlos: fuenf von sieben Faellen waren
gruen, nur der Fall, der wirklich klickt, fiel. Jetzt wird per Name verglichen,
mit dem Grund an der Codestelle.

**Nachweis.** `tests/test_nightlord_selection.py`, sieben Faelle, alle lesen
**Pixel** (`card.grab().toImage()`), keiner fragt `card.selected` — genau die
Frage, um die es geht: der Zustand war nie das Problem, der Bildschirm war es.
Einer davon klickt wirklich (synthetisches `QMouseEvent` auf die Karte), einer
liest ein um 8 px eingerueckt beschnittenes Rechteck, damit die Markierung nicht
auf dem Strich leben kann, den der Zwillings-Marker benutzt.

Rot-vorher, gemessen im Arbeitsbaum durch Entfernen von `self._mark_selected(boss)`
und sofortiges Zuruecksetzen: **7 failed**, Meldung `choosing Gladius (with an
Everdark twin) changed the look of [] on the grid`. Danach `git diff --numstat`
unveraendert (111/26).

**Screenshots:** `docs/screenshots/2026-09-05-T065/nightlords-01-no-choice.png`,
`-02-chosen-without-everdark.png` (Straghess, graue Nachbarn), `-03-chosen-with-everdark.png`
(Gladius, gegen acht violette Zwillingsraender). 1250 logische px.

---

## 2. QA-151 — meine Wahl und warum

**Gewaehlt: die Weckverzoegerung fuer genau diese Koepfe verkuerzen.** Neue
Klasse `HeadingHint` in `nrplanner/effectstab.py`, ein Ereignisfilter auf dem
Viewport des Spaltenkopfs, plus `WAKE_UP_DIVISOR = 4`.

### Warum nicht die drei Auswege aus T-060 §12

* **Kuerzere Kopfnamen.** Loest das Problem dort nicht, wo es beisst: bei
  833 px stehen die Sektionen auf Qts `minimumSectionSize`, und drei Namen, die
  mit `Co` beginnen, bleiben ununterscheidbar, wie kurz sie auch sind. Gemessen
  am laufenden Fenster bei 833 px: `Copies`→`Co…`, `Colours`→`Co…`,
  `Comes with curse`→`Co…`, dazu `Type`→`…`. Ausserdem ist der Wortlaut
  Sache des `ui-ux-designer`, nicht meine.
* **Kopf ueber zwei Zeilen.** Eine zweite Zeile kauft bei einer 32-px-Sektion
  rund fuenf Zeichen und trennt dieselben drei Namen ebenfalls nicht. Sie
  aendert ausserdem die Kopfhoehe auf **jeder** Breite und beruehrt damit die
  gemeinsame Typografie der sechs Tabs (A13) — das ist eine Gestaltungs-, keine
  Fehlerentscheidung.
* **Zugestaendnis „unter 1000 px wird nur ueberflogen".** Laesst A11 genau an
  der Breite unbeantwortet, an der der Befund lebt.
* **(Nicht in §12, aber naheliegend) eine sichtbare Legende der Spalten.** Das
  ist die Klasse „derselbe Text ein zweites Mal", die der Tab-Audit gerade
  beseitigt hat, und der Auftrag schliesst sie ausdruecklich aus.

Bleibt die **Zeit**. Sie ist der einzige Hebel, der den Kopf auf **jeder**
Breite aufloest, keinen zweiten Ort schafft und keinen Wortlaut anfasst.

### Der Wert, mit seiner Herleitung (L-001, L-009)

`delay() = SH_ToolTip_WakeUpDelay // 4`, beim Stil erfragt statt fest verdrahtet
— aus demselben Grund, aus dem `_label_room` den Stil fragt (Fusion gegen
windowsvista, QA-146). Unter Fusion: **700 ms // 4 = 175 ms**.

* **Obere Schranke:** alles nahe 700 aendert nichts; 700 ms ist die Wartezeit,
  vor der der Spieler am 2026-09-05 aufgegeben hat (T-064: 750-800 ms real).
* **Untere Schranke:** ein Zeiger, der nur ueber die Tabelle streicht,
  verbringt ueber dem breitesten je gekuerzten Kopf rund **100 ms** — die
  Label-Spalten sind auf 160 logische px gedeckelt, und ein Strich ueber ein
  1600-px-Fenster in einer Sekunde quert 160 px in 100 ms.
* **Was nicht gemessen ist, behaupte ich nicht:** wie lange ein Spieler, der
  *fragt*, stillhaelt, steht nirgends. Ein Viertel ist genommen, weil es beide
  Schranken um einen Faktor raeumt — nicht, weil es der einzige Wert waere,
  der das tut. Das steht so auch am Code.

**Bewusste Abweichung vom Systemverhalten, benannt:** sie gilt **nur** fuer
einen Kopf, den die Tabelle selbst gekuerzt hat. Ein ganz gezeichneter Kopf
bleibt vollstaendig beim Stil. Damit ist das schnelle Auftauchen **selbst** das
Signal „hier wurde etwas weggenommen" — die Haelfte des Befunds, die die
Auslassungspunkte nicht abdecken.

**Messung am laufenden Fenster** (Windows, Fusion, 150 %, 833 logische px):
der volle Name von `Comes with curse` steht **266 ms** nach Ankunft des Zeigers
auf dem Schirm, gegen 700 ms Stilvorgabe. Die Messschleife gibt bei 690 ms auf,
also kann das Bild nicht von Qts eigener Mechanik stammen.

**Nachweis.** `tests/test_heading_hint.py`, sechs Faelle. Jeder wartet eine aus
dem Stil abgeleitete Spanne (die Haelfte von `SH_ToolTip_WakeUpDelay`, 350 ms
unter Fusion) und behauptet **vor** dem Hover, dass diese Spanne kuerzer ist als
die des Stils — ein gruenes Ergebnis kann also nur vom gepruesften Mechanismus
kommen (L-003). Dazu drei Gegenfaelle: ein ganz gezeichneter Kopf antwortet in
derselben Spanne **nicht**; ein abgebrochener Hover (Verlassen, Klick) wird
nicht nachtraeglich beantwortet.

Rot-vorher, gemessen mit `WAKE_UP_DIVISOR = 1` im Arbeitsbaum und sofortigem
Zuruecksetzen: **3 failed, 3 passed** — die drei Gegenfaelle bleiben gruen, weil
sie ueber ein *Ausbleiben* reden. Genau so steht es im `survival_means` der
Mutation, und genau so ist sie im Campaign gefallen.

**Screenshots:** `effects-05-headings-at-833px.png` (die drei `Co…`),
`effects-06-shortened-head-answers-a-brief-hover.png` (derselbe Kopf, geoeffnet).

---

## 3. QA-152 — die AK-94-Luecke, beide Stellen

**Umgesetzt** in `nrplanner/bosstab.py`:

* `sighting()` zerfaellt in `legend_once()` + `sighting()`, damit auch eine
  Sichtung, die **kein** ganzer Satz ist, die einmalige Legende mitbringt.
* `_row(label, value, colour="#d8d8d8")` — der Wert kann in Sichtungsfarbe
  gezeichnet werden, das Label bleibt gedaempft: das Label ist das Wort dieses
  Moduls, nicht die Sichtung.
* `Set off by` (frueher :737) zeichnet seinen Wert in `OBSERVED_COLOUR`.
* Die Defence-Zeile (frueher :743): die Sichtungsfarbe sitzt auf der **Klausel**,
  nicht auf der Zeile. Das ist der Fall, an dem T-060 stehengeblieben ist — die
  Zahlen kommen aus den Dateien, der Ausloeser aus dem Spiel, auf einer Zeile.
  Eine Farbe ueber die ganze Zeile haette gesagt, die Zahlen seien auch
  gesichtet.

Der **gezeichnete Text ist unveraendert** (`  ·  ` bleibt Trenner), nur die
Farbe wandert — deshalb faellt kein bestehender Textwaechter darueber.

**Nachweis.** Zwei Faelle in `tests/test_nightlord_panel_display.py` mit einem
neuen Helfer `colour_of(markup, needle)`, der die Farbe der **innersten**
Auszeichnung vor dem Text liest. Keine der beiden Farben ist aus dem Modul
importiert: die gesichtete kommt von der eigenen Sichtungszeile des Panels
(`Stacks: yes`), die gewoehnliche von einer Zahl, die das Panel selbst rechnet
(`for bar size`) bzw. — beim Defence-Fall — von der Zahl **auf derselben Zeile**
(`% less damage`). Ein einfarbig gestrichenes Panel faellt hier durch.

Rot-vorher: beide Faelle vor dem Fix rot, Meldung
`Libra: the clause saying what sets this defence step off was watched in play
and is drawn in #d8d8d8, the same colour as the figure beside it on the same
line`.

**Screenshot:** `nightlord-panel-04b-watched-clauses-libra-detail.png` —
`Set off by  after a madness proc` gruen, `Defence  takes 10% less damage · 50s`
grau mit gruener Ausloeser-Klausel, die zweite Defence-Zeile (ohne Ausloeser)
ganz grau.

---

## 4. QA-153 — Stempel und Waechter

`tests/golden/weapon_damage.json` steht auf `extract_version: 11`
(Ein-Zeilen-Diff), und `test_the_golden_file_names_the_extractor_this_tree_runs_on`
vergleicht ihn ab jetzt mit `nrdata.extract.EXTRACT_VERSION`.

**Die Korrektur ist eine geprueste Aussage, keine Reparatur.**
`tests/conftest.py` verweigert jeden Datensatz eines anderen Extraktors, also
sind die 36 eingefrorenen Faelle heute gegen Extraktor-11-Ausgabe gelaufen —
Beleg: `pytest tests/test_weapon_damage_golden.py -rs` = **36 passed, keine
Skips**, vor der Aenderung. Was die Datei ueber ihre eigene Herkunft sagte, war
schlicht falsch.

**Der Waechter faellt, er ueberspringt nicht** — anders als `_same_dataset`
daneben. Jene Frage betrifft das Spiel darunter, das ein Runner nicht aendern
kann; diese betrifft den Extraktor in genau diesem Baum. Der Fehlertext sagt,
welche der beiden Seiten sich bewegt.

Rot-vorher: `assert 10 == 11`, mit der Meldung `weapon_damage.json says it was
captured from extractor 10 and this tree is on 11`.

---

## 5. Mutations-Campaign — 6 von 6 getoetet, 0 Ueberlebende

Jede in einem eigenen `git archive HEAD | tar -x`-Baum, jede ein voller
`-m "not slow"`-Standardlauf (L-008). Der Selbst-Ankerfall
`test_every_mutation_still_finds_its_anchor_in_the_real_source[<name>]` faellt
in jedem Mutantenbaum von Natur aus und ist **nicht** als Toetung gezaehlt.

| Mutation | Lauf | Getoetet durch |
|---|---|---|
| `nightlord-grid-without-a-selection` | 8 failed / 773 passed, 6:04 | alle **7** Faelle in `test_nightlord_selection.py` |
| `nightlord-selection-only-on-the-edge` | 3 failed / 778 passed, 6:12 | genau `test_the_marker_reaches_the_inside_of_the_card` (beide Parameter) |
| `nightlord-buff-trigger-back-in-the-ordinary-colour` | 2 failed / 779 passed, 6:01 | `test_the_buff_trigger_is_drawn_as_the_sighting_it_is` |
| `nightlord-defence-trigger-back-in-the-ordinary-colour` | 2 failed / 779 passed, 5:56 (nach Umbruch neu gefahren) | `test_a_defence_trigger_is_drawn_as_the_sighting_it_is` |
| `effect-headings-wait-as-long-as-the-style` | 4 failed / 777 passed, 5:58 | drei von sechs Faellen in `test_heading_hint.py` — die drei Gegenfaelle halten, wie im `survival_means` angekuendigt |
| `golden-file-stamped-with-the-earlier-extractor` | 2 failed / 779 passed, 6:06 | `test_the_golden_file_names_the_extractor_this_tree_runs_on` |

**Ein bestehender Anker musste mitwandern.**
`sighting-colour-back-without-its-legend` zeigte auf die Closure, die ich in
`legend_once()` + `sighting()` zerlegt habe. Ein Anker, der nichts trifft,
patcht nichts, und der gruene Lauf danach laese sich als Beweis lesen — deshalb
ist er auf die neuen Zeilen gezogen (gleicher Defekt: die Legende erscheint nie).
Ohne den Nachzug faellt `test_every_mutation_still_finds_its_anchor_in_the_real_source`
im Arbeitsbaum, was ich vor dem Nachzug auch gesehen habe (1 failed, 85 passed).

Kosten fuer den director: sechs volle Laeufe in **drei parallelen Shells**, rund
18 Minuten Wanduhr statt 36 seriell; die Laufzeiten pro Mutation sind dabei
nicht gestiegen (5:56 bis 6:12 gegen 5:49 allein).

---

## 6. Projektweite Suche je Befund (L-006)

Jeweils zwei unabhaengig formulierte Masken, mit Trefferzahl.

**QA-150 — „Klick oeffnet eine Detailansicht, das Angeklickte bleibt unmarkiert"**
* Maske A `Signal(` in `nrplanner/`: **2 Treffer** (`bosstab.BossCard.clicked`,
  `firstrun` Fortschritt/Ende — kein Auswahlfall).
* Maske B `mousePressEvent|show_detail|currentRowChanged|itemClicked` in
  `nrplanner/`: **8 Treffer**. Davon in den sechs Tabs: `bosstab` (behoben) und
  `eventstab.py:147` — dessen `QListWidget` zeichnet Auswahl selbst
  (`QListWidget::item:selected`, `eventstab.py:126`), also keine Luecke. Die
  uebrigen (`relicpicker`, `weaponslots`, `app`) liegen im `Build planner`, der
  laut GOAL ausgenommen ist; `app.py:1939-1984` markiert die gewaehlte
  Gefaess-Zeile bereits in ACCENT.
* **Ergebnis: eine Fundstelle in den sechs Tabs, behoben.**

**QA-151 — „auf dem Schirm gekuerzter Text, dessen volle Form nur im Tooltip steht"**
* Maske A `elidedText|setTextElideMode|ElideRight` in `nrplanner/`: **1 Treffer**
  (`effectstab._elide_headings`, behoben).
* Maske B `setToolTip` je Modul: **37 Treffer**, davon in den sechs Tabs
  `effectstab` 7, `arsenaltab` 2, `depthstab` 1, `bosstab`/`deeptab`/`eventstab` 0.
* **Ein weiterer Treffer derselben Eigenschaft, den ich nicht angefasst habe:**
  `effectstab.py:848` `item.setToolTip(item.text())` — jede gequetschte **Zelle**
  haengt genauso an den 700 ms. Siehe Abschnitt 8, Punkt 1.

**QA-152 — „kuratierte Beobachtung in gewoehnlicher Farbe"**
* Maske A `Watched in play|watched in play|community|sighting` in `nrplanner/`:
  **17 Treffer**, davon ausserhalb `bosstab`: `eventstab` (eigener Helfer
  `_community()`, 6 Zeichenstellen — markiert korrekt), `eventlore`, `deeptab`,
  `stacking`.
* Maske B: modulweite Literaltabellen in den Tab-Modulen: **7 Treffer**
  (`GROUP_MAPS`, `UNKNOWN_REFERENCE`, `RATING_LOSSES`, `CURSE_LABEL`,
  `HEADER_TIPS`, `RARITY_NAMES`, `RARITY_COLOURS`).
* **Ein weiterer Treffer derselben Eigenschaft:** `deeptab.py`
  (`WIN_RATING`, `RATING_BONUSES`, `RATING_LOSSES`) — community-berichtete
  Zahlen, gezeichnet mit demselben `_cell()` wie die extrahierten, kenntlich
  nur durch einen Prosasatz darunter (`deeptab.py:433`). Siehe Abschnitt 8,
  Punkt 2.

**QA-153 — „aufgezeichnete Herkunftsangabe, die niemand vergleicht"**
* Maske A `regulation_sha256|data_version|extract_version` in
  `tests|scripts|nrplanner|nrdata`: **40 Treffer**.
* Maske B alle eingefrorenen JSON-Anlagen unter `tests/`: **3 Dateien**
  (`golden/weapon_damage.json`, `data/game_attack_power.json`,
  `data/game_catalyst_scaling.json`). Die beiden `game_*.json` vergleichen ihr
  `game_data_version` (`test_attack_power_against_the_game.py:65`,
  `test_catalyst_scaling_against_the_game.py:83`).
* **Ein weiterer Treffer derselben Eigenschaft:** die Golden-Datei zeichnet
  **drei** Herkunftsfelder auf; `data_version` wurde verglichen, `extract_version`
  jetzt auch, **`regulation_sha256` von nichts**. Siehe Abschnitt 8, Punkt 3.

---

## 7. Definition of Done

- [x] Anforderung verstanden, Annahmen im Kopfblock
- [x] Build und Tests gruen in der benannten Umgebung: `-m "not slow"` 781/9/5,
      `-m "slow"` 5 passed (die `nrdata`-Parser sind also gegen echte
      Spieldateien gelaufen)
- [x] Neue Waechter fuer jede neue Logik, jeder mit gefahrener toetender
      Mutation im Standardlauf; jeder zusaetzlich vorab im Arbeitsbaum rot
      gesehen
- [x] Keine Secrets. `git diff 882ecac..c656e6c` (mein ganzer Beitrag: 15
      Dateien, 958 Zeilen zu, 35 weg) enthaelt **0** Zeilen mit
      `TODO|FIXME|XXX|HACK`, keinen auskommentierten Code, keine toten Zweige
- [x] Zeilenlaenge: fuenf eingefuegte Zeilen ueber 79 Zeichen, in einem eigenen
      Formatierungs-Commit umgebrochen (c656e6c). Die eine verbleibende lange
      Zeile steht in `mutate.py` und ist ein Anker — das Modul sagt selbst, dass
      Anker die Marge reissen muessen. Ein Linter ist im Projekt weiterhin nicht
      eingerichtet (Frage F-A, offen seit Zyklus 12)
- [x] Ergebnis am laufenden Fenster angesehen, 7 Screenshots unter
      `docs/screenshots/2026-09-05-T065/`
- [x] Fremde Dateien nicht angefasst und nicht committet
- [ ] **Ungeprueft:** Linux, macOS, andere Skalierungen als 150 %, ein gebautes
      Artefakt (A9), Tastaturbedienung, Kontrastwerte des neuen Auswahl-Tons,
      und ob ein nicht-technischer Spieler die drei `Co…` mit 175 ms jetzt
      wirklich aufloest — das ist A11 und gehoert dem `power-user`.

---

## 8. An den `director` — Debt, Funde, Risiken

**Zuerst der Beinahe-Unfall, weil er der wichtigste Punkt ist.**

**S-1 (Sicherheit/Datenschutz, behoben, aber meldepflichtig).** Mein erster
Versuch, den Tooltip zu fotografieren, war ein **Bildschirmabzug des Desktops**,
zugeschnitten auf das Fensterrechteck. Der Tooltip haengt bei 833 px ueber den
rechten Fensterrand hinaus, also habe ich den Zuschnitt erweitert — und damit
ein fremdes Chatfenster mit deutschem Projekttext in eine Datei unter
`docs/screenshots/` geschrieben. Ich habe es beim Ansehen bemerkt, die Datei
**vor jedem `git add`** geloescht und auf eine reine Qt-Wiedergabe umgestellt
(beide Fenster einzeln `grab()`, am echten Versatz zusammengesetzt). Belegt:
`git log --all -- "docs/screenshots/2026-09-05-T065/*"` nennt **einen** Commit
(8f27e26), und der dort abgelegte Blob ist 1725x1350 — die Komposition; der
Desktop-Zuschnitt war 1725x1395. **In der Historie ist nichts.** Empfehlung:
Bildschirmabzuege in diesem Repo generell verbieten, das Verfahren steht jetzt
im Agent-Memory. Fuer ein oeffentliches Repo war das ein Kommando Abstand.

**D-1 (QA-151, gleiche Eigenschaft, andere Stelle).** `effectstab.py:848`
setzt jeder gequetschten **Zelle** ihren eigenen Text als Tooltip (AK-77,
„squeezed is not lost"). Diese Zellen haengen weiterhin an den 700 ms, die der
Befund fuer die Koepfe verwirft. Aufwand, wenn gewollt: klein — `HeadingHint`
ist auf den Kopf-Viewport gebunden, ein zweiter Filter auf dem Tabellen-Viewport
mit derselben Bedingung „ist der gezeichnete Text kuerzer als der volle" waere
dieselbe Mechanik. Risiko, wenn nicht: ein Spieler, der bei 1067 px 573 von 652
gekuerzten Effektnamen liest, hat dasselbe Problem wie bei den Koepfen, nur
oefter. **Ich habe es nicht gemacht**, weil der Befund die Koepfe nennt.

**D-2 (QA-152, gleiche Eigenschaft, andere Stelle).** `Deep of Night` zeichnet
seine community-berichteten Wertungszahlen (`WIN_RATING`, `RATING_BONUSES`,
`RATING_LOSSES`) mit demselben `_cell()` wie die extrahierten; kenntlich sind
sie nur durch einen Prosasatz unter der Tabelle. Ob AK-94 dort ebenso gilt, ist
eine Spec-Frage fuer den `ui-ux-designer`, keine, die ich entscheide. Aufwand
klein, Risiko: dieselbe Verwechslung, gegen die AK-94 auf dem Nightlord-Panel
gebaut ist.

**D-3 (QA-153, gleiche Eigenschaft, andere Stelle).**
`tests/golden/weapon_damage.json` traegt `regulation_sha256`, und **nichts**
vergleicht ihn. `data_version` ist nur die ASCII-Version aus dem Kopf der
regulation.bin; zwei Staende mit gleicher Version und verschiedenem Inhalt
wuerden die 36 Faelle stillschweigend gegen andere Eingaben rechnen lassen.
`nrplanner/datasource.py:92` und `firstrun.py:63` prueft den Hash fuer den
Cache — die Golden-Datei tut es nicht. Aufwand: eine Zeile in `_same_dataset`.
Ich habe es nicht getan, weil es ueber den Auftrag hinausgeht und die Wirkung
nicht neutral ist: auf einer Maschine mit anderem regulation.bin wuerden die
36 Faelle ab dann **skippen** statt zu laufen. Das ist eine Entscheidung.

**D-4 (latenter Fehler, `bosstab.py`).** In `show_detail` steht

```python
if ladder.get("up") or defence:
    parts.append(self._section("IT BUFFS ITSELF"))
    for entry in ladder["up"]:
```

Ein Nightlord mit `defence_buffs`, aber ohne `ladder.up`, liefert `KeyError`.
Im heutigen Datensatz nicht erreichbar (einziger Defence-Traeger ist Libra, und
Libra hat `ladder.up`), also **kein aktueller Fehler** — aber eine Zeile, die
ein Datensatzwechsel zum Absturz macht. Nicht von mir eingebaut und nicht von
mir angefasst. Aufwand: `ladder.get("up") or []`.

**D-5 (Debt, `bosstab.py`).** `#d8d8d8` steht als Literal an rund zehn Stellen
in dem Modul. Ich habe es als Vorgabewert von `_row` uebernommen statt eine
Konstante einzufuehren, weil ein halb migrierter Zustand schlechter waere als
ein einheitlich unschoener. Eine reine Umbenennung waere ein eigener kleiner
Commit.

**P-1 (Performance-Fund, nicht getunt).** `BossCard.clicked = Signal(dict)`
marshallt bei **jedem** Klick den ganzen Nightlord-Eintrag durch Qt, inklusive
`weakness.profile` — belegt durch die gemessene Identitaetsverletzung
(`emitted is card.boss` False). Ein `Signal(object)` waere eine Referenz und
zugleich die natuerliche Behebung der Identitaetsfalle. Ich habe es **nicht**
geaendert (nicht mein Auftrag, und Tunen ist Sache des `performance-tuner`).
Empfehlung: `performance-tuner` beauftragen oder es dem naechsten
`bosstab`-Auftrag mitgeben.

**Fremde Dateien im Arbeitsbaum, die ich nicht angefasst habe:**
` M docs/state.md`, ` M qa/findings.md`, `?? docs/berichte/T-064-qa-engineer.md`,
`?? docs/tasks/T-067.md`. Der letzte ist waehrend meines Laufs aufgetaucht; ich
habe ihn nicht gelesen und nicht committet.

**Nachzutragen in `qa/findings.md`** (gehoert dir, nicht mir): QA-150 bis
QA-153 auf *behoben*, Beleg dieser Bericht, Commits 1eafee3, d7fb01f, 49811a8,
a398a1a.

---

## 9. An den `qa-engineer` — was zu pruefen ist und wo ich die Kanten sehe

* **QA-150, der Fall, den meine Waechter nicht sehen:** `refresh()` baut die
  Karten neu und beginnt ohne Markierung, waehrend das Detailpanel stehenbleibt.
  Heute wird `refresh()` nur im Konstruktor gerufen, also ist der Zustand nicht
  erreichbar — wenn jemand den Tab spaeter neu aufbauen laesst, ist er es. Ich
  habe ihn bewusst nicht geraten-behandelt.
* **QA-150, Kontrast:** der Auswahl-Ton `rgba(200, 164, 92, 60)` liegt ueber
  dem Tab-Hintergrund, nicht ueber `PANEL`. Ich habe ihn **nicht** gegen einen
  Kontrastwert geprueft, und `Everdark`-Karten verlieren ihren violetten Rand,
  solange sie gewaehlt sind (Zwilling steht weiter im Symbol, im `+ Everdark
  Sovereign`-Etikett und im Panel). Ob das gestalterisch traegt, ist eine Frage
  an den `ui-ux-designer`.
* **QA-151, was ich nicht gemessen habe:** ob 175 ms bei einem Spieler mit
  Zittern oder mit langsamem Zeiger als Flackern ankommt; wie es sich mit
  aktivierten Bedienungshilfen verhaelt; Verhalten bei einer anderen
  Skalierung als 150 %. Der Wert kommt vom Stil, faellt also mit einem Stil,
  der anders denkt, automatisch anders aus — das ist Absicht, aber ungeprueft.
* **QA-151, die Kante der Mechanik:** der Timer wird **nicht** neu gestartet,
  solange der Zeiger auf demselben Kopf bleibt. Zeiger auf Kopf A, weg vom
  Header, zurueck auf A: startet neu (Leave setzt zurueck). Zeiger A → B → A
  ohne den Header zu verlassen: startet jedes Mal neu. Beides gewollt, beides
  nur an einer Kante getestet.
* **QA-152:** ich habe die Farben ueber die **zehn** Panels des heutigen
  Datensatzes geprueft; `DEFENCE_TRIGGER` hat genau **einen** Eintrag (Libra,
  45852), also ist die zweite Stelle an einem einzigen Fall belegt. Kaeme ein
  zweiter Eintrag dazu, wuerde mein Fall ihn mitpruefen — aber heute steht er
  auf einem Bein.
* **QA-153:** der Waechter faellt, sobald jemand `EXTRACT_VERSION` hebt. Das
  ist gewollt; der Fehlertext sagt, was zu tun ist. Wenn du findest, dass das
  einen legitimen Extraktor-Sprung zu teuer macht, ist das ein Befund und ich
  baue es um.
* **Was ich ausdruecklich nicht geprueft habe:** die vier uebrigen Tabs nach
  meinen Aenderungen am Bild (nur die Suite deckt sie), das gebaute Artefakt,
  und ob die Screenshots auf einem anderen Rechner gleich aussehen.

---

## 10. An den `ui-ux-designer` — Abweichungen und Entscheidungen, die dir gehoeren

1. **Der Auswahl-Ton ist geliehen, nicht erfunden:** `rgba(200, 164, 92, 60)`
   ist derselbe, den `Red variants` und `World Events` fuer eine ausgewaehlte
   Zeile benutzen. Wenn du fuer eine Karte etwas anderes willst als fuer eine
   Zeile, ist das deine Entscheidung; die beiden Kanaele (Rand **und**
   Fuellung) sollten es dann bleiben, weil der Rand allein den
   Everdark-Marker doppelt belegt.
2. **Eine gewaehlte Everdark-Karte zeigt ihren violetten Rand nicht**, solange
   sie gewaehlt ist. Begruendet: der Zwilling steht weiter im geteilten Symbol
   und im `+ Everdark Sovereign`-Etikett derselben Karte, und das Panel daneben
   sagt es im Klartext. Wenn du beides gleichzeitig sichtbar haben willst,
   brauchen wir einen dritten Kanal (Aussenring, Ecke) — sag an.
3. **Die 175 ms sind eine bewusste Abweichung vom Qt-Stil**, nur fuer gekuerzte
   Spaltenkoepfe. Der Wert ist ein Viertel dessen, was der Stil verlangt, und
   folgt ihm, wenn der Stil wechselt. Wenn du eine andere Spanne willst, ist es
   eine Zahl an einer Stelle (`WAKE_UP_DIVISOR`).
4. **Was ich bewusst *nicht* gebaut habe:** eine sichtbare Spaltenlegende, ein
   Fragezeichen-Cursor ueber gekuerzten Koepfen (er kollidiert mit Qts eigenem
   `SplitHCursor` auf den Sektionsgrenzen — der Header setzt und loescht den
   Cursor selbst, ein eigener wuerde die Groessenaenderung als Affordanz
   kaputtmachen) und einen zweiten Ort fuer denselben Text.
5. **Wortlaute habe ich keine geaendert.** Der gezeichnete Text der
   Defence-Zeile ist Zeichen fuer Zeichen derselbe wie vorher; nur die Farbe
   der Ausloeser-Klausel ist gewandert.
