# T-068 — developer

```
STATUS: erledigt
AUFTRAG: T-068 — die letzten drei A11-Luecken (QA-154, QA-155, QA-156)
GELESEN: GOAL.md · docs/state.md · docs/berichte/T-066-power-user.md ·
         qa/findings.md (QA-150 bis QA-156) · UI_SPEC.md (AK-68, AK-77,
         AK-79, AK-81, AK-82, §2.5, §3.1) · docs/tasks/T-067.md (nur um
         auszuschliessen, dass es mein Auftrag ist) · tests/rendered.py,
         tests/conftest.py, tests/tabtext.py ·
         scripts/differential/mutate.py · nrplanner/{bosstab,cardgrid,
         effectstab,arsenaltab,app,relicpicker,weaponslots,depthstab}.py
GEAENDERT: nrplanner/bosstab.py · nrplanner/app.py · nrplanner/arsenaltab.py ·
         nrplanner/effectstab.py · tests/test_nightlord_selection.py ·
         tests/test_nightfarer_is_named.py (neu) ·
         tests/test_effects_tab_display.py ·
         scripts/differential/mutate.py ·
         docs/screenshots/2026-09-06-T068/ (7 Bilder, neu) ·
         .claude/agent-memory/developer/{MEMORY.md,
         project_pointer_and_floor_traps.md} (gitignoriert)
         Sieben Commits, c9682d2 bis 46a8d24. Fremde Dateien nicht
         angefasst: docs/state.md, qa/findings.md, docs/plan-restarbeiten.md
         und die vier ungetrackten Dateien stehen unveraendert im Baum.
ANNAHMEN: (1) Die Anweisung des Directors, den Fragesatz des Waffen-Tabs zu
         aendern, geht der Wortlaut-Bindung von AK-82 vor. (2) Die
         Beschriftung der Nightfarer-Kacheln liegt im `Build planner`, der
         vom Tab-Audit ausgenommen ist — der Auftrag verlangt sie
         ausdruecklich, also habe ich sie dort gebaut. (3) Der Farbwert des
         Zeigerhinweises ist von mir gemessen und gewaehlt; die
         gestalterische Entscheidung gehoert dem ui-ux-designer, die Zahlen
         liegen bei.
NAECHSTER: director
BLOCKIERT DURCH: nichts
```

---

## Umgesetzt

### 1. QA-154 — die Nightlord-Karte

**Die Trefferflaeche ist nicht der Fehler.** Gemessen am 2026-09-06 auf
Windows, Stil Fusion, 150 % Skalierung, Fenster 1600x900 **logische** px (das
Fenster hat beide Zahlen erreicht, sonst haette der Lauf abgebrochen):
**3 420 Prueflpunkte, einer je 4 logische px ueber die ganze 302x178-Karte,
jeder ueber `qApp.notify` zugestellt, damit Qts eigene Weiterreichung
entscheidet — 3 420 von 3 420 oeffneten diese Karte, 0 tot.** Die Labels auf
der Karte ignorieren einen Druck, und Qt gibt ihn an den Rahmen weiter.

Tot ist der Streifen **zwischen** zwei Karten: **8 logische px** bei 1600,
1250 und 1067 px, und ein Klick darin oeffnet nichts. Vom Rasterrechteck bei
1600 px sind 79,3 % Karte; von den 20,7 %, die es nicht sind, sind drei
Viertel der ungefuellte Rest der letzten Zeile (zehn Karten in vier Spalten)
und der Rest jenes 8-px-Gitter. Bei 1067 px sind es 4,6 %, bei 833 px 4,1 %.

**Was der Spieler nicht sehen konnte, war, auf welcher Seite dieser 8-px-Linie
er stand.** Ein Fehlklick oeffnete den Nachbarn, ein Danebenklick nichts, und
das Raster sah in beiden Faellen gleich aus. Deshalb sitzt die Markierung
jetzt am **Zeiger**, nicht am Klick: `BossCard.enterEvent`/`leaveEvent`,
Fuellung allein, Rand unberuehrt. Die Auswahl bewegt beides, ein
Everdark-Zwilling besitzt DEEP am Rand — die drei Zustaende bleiben getrennt,
und die Auswahl behaelt ihre Karte, waehrend der Zeiger wandert.

**Die T-065-Markierung greift in diesem Fall.** Geprueft: eine gewaehlte Karte
bleibt gewaehlt markiert, waehrend der Zeiger ueber ihr steht
(`nightlords-07-…png`).

**Der erste Farbwert war zu schwach, und das ist ein eigener Befund.**
`#26272c` ergab komponiert (38, 39, 44) gegen (30, 31, 35) — WCAG-Kontrast
**1,105**. Am Bildschirmabzug musste ich *messen*, ob der Zeiger ueberhaupt
auf einer Karte stand. Das ist keine Rueckmeldung, sondern der Befund noch
einmal. Jetzt `#33343c` → (51, 52, 60), **1,331**, nahe an den 1,440, die die
Fuellung der Auswahl selbst schafft. Kuehlere Werte reichen weiter (`#334055`
1,572, `#3a4a60` 1,825) und stehen mit ihren Zahlen im Kommentar — sie
brauechten aber einen neuen Farbton auf einem Tab, auf dem DEEP am Kartenrand
schon etwas bedeutet. Das ist die Entscheidung des `ui-ux-designer`.

### 2. QA-155 — die Charakterauswahl

**Kein zweiter Auswaehler.** Zwei Beschriftungen:

- **Die Kachel sagt, wen sie zeigt.** `HeroTile` traegt den Namen unter dem
  Portrait, 7 pt. Gemessen auf Windows/Fusion/150 %, logische px: der
  laengste der zehn, `Undertaker`, braucht 59 px bei den voreingestellten
  9 pt, 54 bei 8 und **44 bei 7**, gegen die **52 px**, die eine 56-px-Kachel
  innerhalb ihres Rands hat. Bei 7 pt stehen **alle zehn vollstaendig**, kein
  Name wird gekuerzt (gemessen, `planner-01-…png`). Breiter darf die Kachel
  nicht werden: fuenf Spalten muessen in den 300-px-Boden der Seitenleiste
  passen, und QSplitter reicht jeden Ueberhang an das Fenstermindestmass
  weiter. Die Hoehe erfragt Qt (56x56 → **56x73**); `_apply_image` steht jetzt
  davor, weil `initStyleOption` einen Knopf mit Text und ohne Symbol als
  reinen Textknopf meldet — eine dort bemessene Kachel kam **19 px** hoch und
  ohne Portrait heraus. Der Rand ist in beiden Zustaenden 2 px, damit die
  Auswahl dem Namen keine 2 px wegnimmt.
  **Kosten, am Ende des Auftrags gegen einen Baum aus `git archive 264d328`
  gemessen:** Fenstermindestmass auf Windows **760x514 → 760x548** logische
  px (Breite unveraendert, Hoehe +34 fuer zwei Kachelreihen); offscreen
  **964x471 → 988x499** — die +24 px Breite dort sind die vier
  Filterbeschriftungen aus Punkt 3, nicht die Kacheln.
- **Der Waffen-Tab sagt, wo gewechselt wird.** AK-82 lautete `rated for the
  Nightfarer, level and upgrade set above` — und **nur das Upgrade** wird
  oben eingestellt. Der Spieler hat auf diesem Tab gesucht, weil der Satz es
  ihm gesagt hat. Neu: `Every armament and spell in the game, rated at the
  upgrade you set here, for the Nightfarer and level you set on the Build
  planner tab. Spell damage is not in the game's data, so spells show what
  they cost you instead.` **Das ist eine Abweichung von einem wortgleich
  festgeschriebenen AK** — siehe „An ui-ux-designer".

### 3. QA-156 — die letzten zwei „ich haette geraten"

**(a) Was `Copies` wirklich zaehlt.** *Die Vermutung des Spielers stimmt
nicht.* „Wie viele gleiche Kopien in verschiedenen Slots existieren" ist die
Spalte **`Relic slots`**. `Copies` zaehlt, **wie oft die Effekttabelle des
Spiels denselben Effekt getrennt definiert** — gleicher Name, gleiche
SpEffect-Ids, gleiche Modifikatoren; die Zeilen werden hier zu einer
zusammengefasst. Gemessen am aktuellen Datensatz: **2 076 Effektzeilen
ergeben 1 064 verschiedene Effekte**; unter den Anfangsfiltern des Tabs sagen
**620 Zeilen 1, 29 sagen 2, zwei sagen 3, eine sagt 4** (das deckt sich mit
seinem „meist 1 oder 2"). **68** Identitaeten kommen mehr als einmal vor, und
bei **29 von 68** unterscheiden sich die Kopien in den Farben, auf denen sie
rollen koennen — deshalb muss die Zahl die des Spiels bleiben und nicht die
der Ansicht (AK-81), und deshalb steht genau das im Satz.

Der Satz steht dort, wo `Tier` erklaert wird und wo es funktioniert hat, und
der Spaltenkopf benutzt **dieselbe Konstante**, damit die beiden nicht
auseinanderlaufen koennen — das ist AK-79 mit dem Namen einer anderen Spalte.

**(b) Die vier Filtermenues** tragen jetzt `Colour`, `Relics`, `Stacking`,
`Type` — jeweils der Name der Spalte, die sie einschraenken; ausser dem
Menue, das zwischen gewoehnlichen und Deep-of-Night-Relikten waehlt, wozu es
keine Spalte gibt.

**Und das ist der Teil, den der Director lesen sollte.** Als schlichte
`QLabel` kosteten die vier den Tab **160** und das Fenster **56** logische px
(760 → 816) auf Windows — und unter der breiteren Schrift, mit der die Suite
rendert, hoben sie den Boden des Fensters von **964 auf 1276 px**, ueber drei
der vier Breiten, an denen die Geometriefaelle messen. **47 Faelle haben sich
uebersprungen und die Suite meldete gruen** (781+31 erwartet, 754 gezaehlt,
Skips 9 → 56). Als `FilterCaption` — `minimumSizeHint().width() == 0`, eigenes
Kuerzen im `paintEvent` — kosten sie das Fenster **nichts** (760 vorher, 760
nachher) und den Tab **24 px**, die vier Zwischenraeume der Zeile, die kein
Widget zurueckgeben kann. Offscreen: 964 → 988.

---

## Tests

**Neu: 31 Faelle** (790 gesammelt vorher, 821 nachher; gezaehlt gegen einen
Baum aus `git archive 264d328`, nicht aus dem Gedaechtnis).

| Datei | neu | worauf |
|---|---|---|
| `tests/test_nightlord_selection.py` | 7 | Zeigermarke, Luecke, Trefferflaeche |
| `tests/test_nightfarer_is_named.py` (neu) | 9 | Kachelname, Waffen-Tab-Satz |
| `tests/test_effects_tab_display.py` | 8 | `Copies`, Filterbeschriftungen, Boden |
| `tests/test_differential_track.py` | +11 | Ankerpruefung der neuen Mutationen |

**Belege, Befehle und Ausgaben**

```
.venv\Scripts\python.exe -m pytest -q -m "not slow"
  815 passed, 9 skipped, 5 deselected in 383.69s
.venv\Scripts\python.exe -m pytest -q -m "slow"
  5 passed, 824 deselected in 49.39s
QT_QPA_PLATFORM=windows ... -m pytest -q -m "not slow"
  813 passed, 11 skipped, 5 deselected in 399.32s
```

Die 9 Skips offscreen sind der Ausgangsstand (781 + 9 = 790 gesammelt). Auf
der Windows-Plattform 11: zehnmal „Fenster erreicht 2100 px nicht" (Schirm
1709 logische px) und einmal „der physische Zeiger sitzt auf der Karte, die
dieser Fall selbst ansteuert". Beide Laeufe zusammen decken alle Breiten.

**Toetende Mutationen — 20 gefahren, alle rot im Standardlauf.** Elf davon
sind in `scripts/differential/mutate.py` eingetragen und jede wurde vor dem
Eintragen gegen diesen Baum angewandt und ihre Faelle gelaufen (Datei-Hash vor
und nach jedem Lauf gleich):

| Mutation | rot bei |
|---|---|
| `nightlord-card-without-a-hover-mark` | 4 Faelle |
| `nightlord-card-keeps-the-hover-mark` (leaveEvent) | 2 |
| `nightlord-hover-drawn-as-the-selection` | 1 |
| `nightlord-hover-outranks-the-selection` | 1 |
| `nightlord-card-labels-eat-the-press` | 1 |
| `nightlord-selection-only-on-the-edge` (Anker nachgezogen) | 3 |
| `nightfarer-tiles-without-names` | 1 |
| `arsenal-question-back-to-set-above` | 3 |
| `copies-explained-only-on-the-header` | 3 |
| `copies-counted-from-the-filtered-view` | 1 |
| `filter-boxes-without-a-caption` | 3 |
| `filter-captions-set-the-window-floor` | 1 |

Nicht eingetragen, aber gefahren: `HOVER_FILL = PANEL` (3), alle zehn Kacheln
gleich beschriftet (2), Groesse vor dem Symbol festgelegt (2), Kachel 24 px
breiter (1), Kopf und Satz laufen auseinander (1), Beschriftung ist ein
eigener Wert des Menues (2), Beschriftung erfindet ein Wort (1), Definition
laesst ihre Nachbarspalten weg (1).

**Drei ueberlebende Gegenbauten — als Befund, nicht stillschweigend
nachgebessert (L-008c):**

1. **`HOVER_FILL = SELECTED_FILL` ueberlebte die erste Fassung seines eigenen
   Falls.** Der Fall verglich ganze Karten, und die Auswahl aendert **auch den
   Rand** — also blieb er gruen, obwohl beide Fuellungen identisch waren. Er
   liest jetzt innerhalb des Rands, wie der Everdark-Fall daneben es schon
   tat.
2. **„Jede Kachel 24 px breiter" ueberlebte zwei Fassungen.** Der Fall las
   ausgelegte Positionen; die Spalten dehnen sich aber auf die Seitenleiste,
   also passten 416 px Kacheln in 430 px Bereich, waehrend sie 116 px mehr
   brauchten, als der Bereich je garantiert. Er fragt jetzt
   `QGridLayout.minimumSize`.
3. **„Der Rand der gewaehlten Kachel waechst auf 4 px" ueberlebte und ist
   nicht zu toeten.** Gemessen: `contentsRect`,
   `subControlRect(CC_ToolButton, SC_ToolButton)` und
   `subElementRect(SE_ToolButtonLayoutItem)` melden **alle drei 56x73**, ob
   der Rand 2, 4 oder 8 px ist. Qt gibt die Randbreite einer Stylesheet-Regel
   nirgends her. **Ich habe den zahnlosen Fall geloescht statt ihn gruen
   stehen zu lassen**; an seiner Stelle steht ein Fall, der prueft, dass die
   gewaehlte Kachel ueberhaupt anders gezeichnet wird. Die Gleichheit der
   beiden Randbreiten ist damit **ungeschuetzt** und nur im Kommentar
   begruendet.

**Was die Suite nicht prueft, und das ist eine Luecke, kein Beleg.** Die
Zeigerfaelle stellen Enter/Leave mit `QApplication.sendEvent` direkt zu. Qts
`dispatchEnterLeave` — wer die Ereignisse bekommt — laeuft dabei **nicht**.
Grund, gemessen: `QTest.mouseMove` landet nur im **ersten Fenster eines
Prozesses**; jedes spaetere erbt die Zeigerposition des vorigen, bekommt ein
Enter fuer die Karte darunter und nie das passende Leave. Unter der
Windows-Plattform landet nicht einmal der erste Zug (Ziel Gnoster → markiert
Gladius). Diese Haelfte ist **am laufenden Fenster** mit `QCursor.setPos`
gemessen, und zwar mit diesem Ergebnis:

```
centre of card 0 (its own surface)      hovered=['Gladius']  active=True
on the name label inside card 0         hovered=['Gladius']  active=True
in the 8 px gap between card 0 and 1    hovered=[]           active=True
centre of card 1                        hovered=['Adel']     active=True
```

---

## Am laufenden Fenster angesehen

Sieben Bilder, `docs/screenshots/2026-09-06-T068/`, alle mit `grab()` auf ein
Widget plus Rechteck aus dem Fenster des Programms — **kein Bildschirmabzug
und kein Zuschnitt eines solchen** (L-012). Jede Abmessung wurde vor dem
Ablegen gegen die 2561x1601 physischen px des Schirms geprueft; das groesste
Bild ist 2400x1350. Der Zeiger in den drei Nightlord-Bildern ist der echte
Cursor, mit `QCursor.setPos` gesetzt und danach zurueckgestellt.

---

## DoD

- [x] Anforderung verstanden, Annahmen dokumentiert
- [x] Build & Tests gruen — offscreen **und** `QT_QPA_PLATFORM=windows`, mit
      Befehl und Ausgabe oben
- [x] Neue Tests fuer neue Logik; toetende Mutation je Waechter, drei
      Ueberlebende berichtet
- [ ] **Linter: nicht pruefbar.** `ruff` ist nicht freigegeben und `flake8`
      nicht installiert (`No module named flake8`). Ersatzweise gemessen:
      **0** neue Zeilen ueber 79 Zeichen und 0 mit Leerzeichen am Ende in
      allen geaenderten Modulen und Testdateien; die 8 langen Zeilen in
      `mutate.py` sind woertliche Anker, die nicht umgebrochen werden duerfen
      (46 solche standen dort schon).
- [x] Keine Secrets, keine TODOs, kein toter Code
- [x] QA-Akzeptanzkriterien selbst durchgespielt; Abweichungen begruendet
- [x] Ergebnis am laufenden Fenster angesehen, 7 Bilder
- [x] Abschlussbericht
- **Ungeprueft:** ein gebautes Artefakt (A9) · Linux/macOS · jede
  Schirmaufloesung ausser 2560x1600 bei 150 % · jede Skalierung ausser 150 %

---

## Projektweite Suche nach demselben Muster (L-006)

Drei Muster, je mindestens zwei unabhaengig formulierte Suchmasken, mit
Trefferzahl.

**Muster A — anklickbare Flaeche ohne Zeichen, welche der Zeiger trifft.**
Masken: `def mousePressEvent|def mouseReleaseEvent` (**4** Treffer),
`PointingHandCursor` (**7**), `def enterEvent|def leaveEvent|:hover` (**3**).
Vereinigt: sieben anklickbare Flaechen, davon hat jetzt **eine** eine
Zeigermarke (`BossCard`) und **eine** einen `:hover` (`shortcut_button`,
`app.py:1879`). **Fuenf offen:** `relicpicker.py:136` (`RelicCard` — die
Relikt-Karten des Pickers, gleiche Kartenform, gleiche 8-px-Luecken),
`relicpicker.py:210` (die Karte „eigenes Relikt"), `weaponslots.py:200`
(`WeaponSlotTile`; hat einen *Aktiv*-Zustand, aber keine Zeigermarke),
`relicpicker.py:253` (die Favoriten-Portraits) und `app.py:199` (die
anklickbare Titelzeile der Schadenstafel).

**Muster B — Bedienelement nur als Bild, Name nur im Tooltip.** Masken:
`ToolButtonIconOnly|TextUnderIcon|TextBesideIcon` (**4**), `setToolTip` auf
`QToolButton` in Verbindung mit `setIcon` (**3**). **Ein offener Fall:**
`relicpicker.py:258` — das `FavouriteMenu` zeigt dieselben zehn Nightfarer als
reine Portraits, Name nur im Tooltip. Wortgleich QA-155(b) an einer zweiten
Stelle. Der Fall `app.py:1124` (Bildauswahl) ist **kein** Treffer: dort *ist*
das Bild der Inhalt.

**Muster C — Bedienelement ohne sichtbare Beschriftung.** Masken:
`QComboBox()` (**10**), `QCheckBox(` (**6**). Nach diesem Auftrag: **0**
sichtbare Auswahlmenues ohne Beschriftung. Jedes andere traegt bereits eines
— `UI scale` (app.py:1347), `Build` (1605), `Rarity` (arsenaltab.py:314),
`Map:` (depthstab.py:188), `Upgrade` (weaponslots.py:319); `relic_box`
(app.py:593) ist `setVisible(False)`. Alle sechs Kontrollkaestchen tragen
ihren Text selbst. **Muster geschlossen.**

**Muster D — Erklaerung nur im Tooltip erreichbar.** Auf dem Effects-Tab
gezaehlt: **7 von 11** Spalten haben eine Erklaerung, deren Wortlaut nur im
Kopf-Tooltip steht (`Tier`, `Colours`, `Relic slots`, `Avg chance`, `Best
chance`, `Stacking`, `Comes with curse`) — bei `Tier` steht der *Gedanke*
sichtbar in der Zusammenfassung, nur mit anderen Worten, also sind es
**sechs**, deren Bedeutung nirgends ausserhalb eines Tooltips steht. Drei
Spalten (`Effect`, `Type`, `What it does`) tragen ueberhaupt keine Erklaerung.
Ob das ein Mangel ist, entscheidet nicht der Code.

---

## Offene Fragen

**An den App Designer** — keine neuen. Die gesammelten (F-A bis F-F) bleiben.

**An den `ui-ux-designer`:**

1. **Abweichung von AK-82, wortgleich festgeschrieben.** Der Fragesatz des
   Waffen-Tabs lautet nicht mehr wie in `UI_SPEC.md` §3.1. Begruendung: der
   alte Satz war an der Stelle, um die es geht, **falsch** — er sagte, der
   Nightfarer werde „above" eingestellt, wo nur das Upgrade eingestellt wird,
   und genau dorthin ist der Spieler gegangen. Der zweite Satz (Zauber) steht
   unveraendert. **`UI_SPEC.md` §3.1 muss nachgezogen werden; ich habe die
   Datei nicht angefasst.**
2. **Der Farbwert der Zeigermarke gehoert dir.** `HOVER_FILL = "#33343c"`,
   komponiert (51, 52, 60), WCAG **1,331** gegen eine unmarkierte Karte
   (30, 31, 35) und gegen die komponierte Auswahl (64, 57, 42), die selbst
   1,440 erreicht. Gemessene Alternativen: `#2b2c33` 1,185 · `#334055` 1,572
   · `#3a4a60` 1,825. Die beiden kuehlen reichen weiter, bringen aber einen
   neuen Farbton auf einen Tab, auf dem DEEP am Kartenrand schon etwas
   bedeutet.
3. **Beschriftungen der Filter:** `Colour`, `Relics`, `Stacking`, `Type` —
   drei sind Spaltennamen, `Relics` hat keine Spalte. Falls dir ein anderes
   Wort lieber ist: es kostet keine Breite mehr, `FilterCaption` kuerzt sich
   selbst.
4. **Kleine Inkonsistenz nebenbei:** `depthstab.py:188` schreibt `Map:` mit
   Doppelpunkt, jede andere Beschriftung im Programm ohne. Nicht angefasst.

**An den `qa-engineer`:**

- **QA-154:** Zeiger auf eine Karte, in die 8-px-Luecke, auf den Nachbarn, und
  auf die **gewaehlte** Karte — vier Zustaende, drei Bilder. Randfaelle: die
  letzte Zeile des Rasters ist bei 1600 px nur halb gefuellt (10 Karten, 4
  Spalten), der leere Rest reagiert auf nichts; bei 833 px ist das Raster
  einspaltig und hat gar keine Luecke. Ein Klick auf **jede** Stelle einer
  Karte muss sie oeffnen — auch auf dem Bild, dem Namen und dem Beschreibtext.
- **QA-155:** alle **zehn** Kachelnamen bei 100 %, 125 %, 150 % und 200 %
  Skalierung ansehen — ich habe nur 150 % gemessen, und `Undertaker` hat bei
  7 pt genau 44 von 52 px. Dazu: Seitenleiste auf ihren 300-px-Boden ziehen
  und pruefen, dass keine Kachel abgeschnitten wird. Der Waffen-Tab
  aktualisiert seinen Kopf **nur beim Nach-vorn-Holen** (`currentChanged`) —
  Charakter wechseln, ohne den Tab zu verlassen, zeigt weiter den alten Namen;
  das ist bestehendes, beabsichtigtes Verhalten, aber ein Pruefpfad.
- **QA-156:** `Copies` unter jedem Farbfilter — die Zahl darf sich **nicht**
  aendern, obwohl bei 29 von 68 mehrfach definierten Effekten eine Kopie aus
  der Ansicht faellt. Und die vier Beschriftungen bei 833 px ansehen: dort
  kuerzen sie sich selbst, mit Auslassungspunkten.
- **Neu und wichtig:** ein Suitelauf mit `QT_QPA_PLATFORM=windows` bringt 18
  Faelle mehr zum Laufen als der Standardlauf (die 833/1067-px-Faelle). Ich
  habe beide gefahren; beide gruen.

**An den `director`:**

1. **Sicherheitsfunde: keine.** Kein neuer externer Input, keine neue
   Abhaengigkeit, kein Netzwerk, keine Secrets.
2. **Beinahe-Falschmeldung, die du kennen solltest.** Zwischenstaendlich
   meldete die Suite `754 passed, 56 skipped` — 47 Faelle uebersprangen sich
   still, weil vier gewoehnliche `QLabel` den Fenstermindestbreite offscreen
   von 964 auf 1276 px gehoben hatten. Ohne den Vergleich gegen den
   gesammelten Ausgangsstand (`git archive 264d328` + `--collect-only`, 790
   gegen 821) waere das als gruen durchgegangen. Behoben durch
   `FilterCaption`; als `filter-captions-set-the-window-floor` in der
   Mutationsregistratur, damit es nicht wiederkommt.
3. **Debt, bestehend, nicht angefasst (Ort, Art, Risiko, Aufwand):**
   - `nrplanner/effectstab.py`, Filterzeile: **die geschlossenen
     Auswahlmenues schneiden ihren eigenen Wert ab.** Gemessen bei 1600 px
     logisch: Textraum **81 px**; `Normal + Deep` braucht 82 (1 px zu wenig),
     `Buffs and curses` braucht 86 (5 px), und `Strongest only (adds +
     multiplies)` braucht 178 (97 px). **Unveraendert durch T-068** — die
     Kaesten sind in beiden Baeumen 106 px breit, gemessen gegen `git archive
     264d328`. Verstoesst gegen A13 („nichts abgeschnitten"), faellt jetzt
     staerker auf, weil neben jedem Kasten eine Beschriftung steht.
     Risiko: mittel (ein Spieler liest einen falschen Filterwert).
     Aufwand: klein, aber es ist eine Breitenentscheidung — gehoert dem
     `ui-ux-designer`.
   - Fuenf anklickbare Flaechen ohne Zeigermarke (Muster A oben). Risiko:
     dasselbe wie QA-154, im Relikt-Picker mit denselben 8-px-Luecken.
     Aufwand: je ~15 Zeilen plus Faelle, dieselbe Form wie hier.
   - Das `FavouriteMenu` zeigt zehn Portraits ohne Namen (Muster B). Risiko:
     wie QA-155(b). Aufwand: klein.
   - Die Gleichheit der beiden Randbreiten der `HeroTile` ist **durch nichts
     geschuetzt**; Qt gibt die Randbreite einer Stylesheet-Regel nicht her
     (gemessen, drei Wege). Risiko: klein, aber real.
   - Aus `docs/state.md` uebernommen und **weiterhin offen**, von mir nicht
     angefasst: `ARCHITECTURE.md` nennt `held_fingerprint` an vier Stellen
     weiter als geltend · `model.Build.level` fehlt im Entwurf · AK-94-Luecke
     in `bosstab.py` — die Zeilen sind durch T-068 gewandert und ich habe sie
     nachgeschlagen statt geschaetzt: `docs/state.md` nennt `:730,736`, das
     steht jetzt auf **802** und **808**; `qa/findings.md` QA-152 nennt
     `:737/:743`, das steht jetzt auf **809** und **815** ·
     `tests/golden/weapon_damage.json` traegt `extract_version: 10` gegen
     Extraktor **11**.
4. **Performance:** nichts Auffaelliges gemessen. Die Zeigermarke zeichnet
   eine Karte neu, wenn der Zeiger sie betritt oder verlaesst; das ist ein
   `setStyleSheet` je Wechsel. Aufgefallen ist nichts, gemessen habe ich es
   nicht — falls der `performance-tuner` ohnehin auf diesem Tab arbeitet,
   waere es ein Blick wert. **Keine Empfehlung, ihn dafuer allein zu rufen.**
5. **Eskalation: keine.** A11 ist aus meiner Sicht an den drei benannten
   Stellen geschlossen; ob ein Spieler jetzt ohne Raten durchkommt,
   entscheidet der naechste `power-user`-Lauf, nicht dieser Bericht.
6. **Nummernkreise, die du fuehrst:** ich habe **T-068** verbraucht, keine
   neuen QA-/AK-/DR-Nummern vergeben und `qa/findings.md` nicht angefasst.
   Die vier neuen Befunde aus Punkt 3 brauchen QA-Nummern von dir.
