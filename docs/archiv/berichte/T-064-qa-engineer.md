```
STATUS: erledigt
AUFTRAG: T-064 — Retest von QA-140 bis QA-149, Schwerpunkt: der Tooltip-Widerspruch aus T-063
GELESEN: GOAL.md (A7, A10-A14, Erweiterung 2026-09-05) · docs/state.md (inkl. der uncommitteten
  lokalen Aenderung, ` M`) · qa/findings.md (komplett, 1660 Zeilen) · docs/berichte/T-060-developer.md
  (vollstaendig) · docs/berichte/T-063-power-user.md (vollstaendig) · nrplanner/{app,effectstab,
  arsenaltab,relicpicker,cardgrid,depthstab,bosstab}.py · nrdata/extract.py · tests/{conftest,rendered,
  test_tab_geometry,test_relic_picker_geometry,test_effects_tab_display,test_nightlord_panel_display,
  test_arsenal_tab_asks_the_facade}.py · scripts/differential/mutate.py · tests/golden/weapon_damage.json
  · .claude/agent-memory/qa-engineer/ (nightreign-helper-qa, nightreign-display-guards,
  nightreign-tab-content, qa-qt-sichtpruefung)
GEÄNDERT: docs/berichte/T-064-qa-engineer.md (diese Datei) — sonst nichts im Arbeitsbaum. `git status`
  im Projekt-Repo zeigt vor und nach meinem Lauf nur die bereits vorhandene ` M docs/state.md`, die ich
  nicht angefasst habe. Alle Messungen liefen in einem eigenen `git clone` und `git archive`-Extraktionen
  unter dem Scratchpad; nichts davon existiert im Arbeitsbaum oder wurde gepusht/committed.
ANNAHMEN: (1) Die Bedienungshilfen-Hypothese des Directors habe ich so gelesen, dass der Kern der Frage
  "genuine OS-Maus-Hover vs. reine Property-Pruefung" ist, nicht eine konkrete Assistive-Technology-API —
  siehe Abschnitt 1, Methodik. (2) Fuer den Live-Fenstertest habe ich `NIGHTREIGN_SETTINGS_ORG/_APP` auf
  eigene Werte umgebogen (nie den echten Nutzerspeicher beruehrt) und den vorhandenen Snapshot unter
  `%LOCALAPPDATA%\NightreignHelper\nightreign_data.json` verwendet, nicht neu extrahiert. (3) Die
  Windows-Plattform-Zahl (758/10/5) habe ich nicht selbst nachgemessen (Kostengrund), sondern indirekt
  bestaetigt: meine drei Live-Fenster liefen alle unter der echten `windows`-Plattform und erreichten
  833 px ohne die Offscreen-Untergrenze — siehe „Nicht getestet".
NÄCHSTER: director
BLOCKIERT DURCH: nichts
```

# T-064 — Retest QA-140 bis QA-149, Schwerpunkt Tooltip-Widerspruch

## 0. Ausgangslage bestaetigt

`.venv` Suite in einem frischen `git clone` (nicht im Arbeitsbaum) gegen den
bestehenden Snapshot:

| Lauf | Ergebnis | Abweichung von der gemeldeten Zahl |
|---|---|---|
| `-m "not slow"`, offscreen | **759 passed, 9 skipped, 5 deselected** (308 s) | keine |
| `-m "slow"` | **5 passed, 768 deselected** (53 s) | keine |

Alle 9 Skips sind exakt der gemeldete Grund (`tests/rendered.py:86`,
Offscreen-Plattform kann 833 px nicht darstellen, misst 964 px) — per
gezieltem `-rs`-Lauf ueber die T-060-Testdateien einzeln nachgesehen, keine
unerwartete Uebersprungmeldung darunter (90 passed, 9 skipped in diesem
Teillauf).

---

## 1. Der Schwerpunkt: haelt die Tooltip-Zusicherung von QA-140 am laufenden Fenster?

**Ergebnis vorweg: Lesart (b). Der Tooltip existiert, ist korrekt verdrahtet
und erscheint zuverlaessig bei echtem Maus-Hover — an allen drei Breiten, bei
denen QA-140 ueberhaupt etwas kuerzt, inklusive der einen Spalte, die der
`power-user` tatsaechlich gesehen hat. QA-140 bleibt geschlossen.**

### Methodik — warum nicht die Testsuite selbst befragt wurde

Die vorhandenen Waechter (`test_every_shortened_heading_says_so_and_keeps_its_name`
u.a.) lesen ausschliesslich `item.toolTip()` — die **Modelldaten**, nicht ob
Qt sie beim Hover tatsaechlich **anzeigt**. Das ist fuer diese Waechter richtig
(L-003: sie pruefen genau das Signal, das `set_headings`/`_elide_headings`
erzeugen), beantwortet aber nicht die Frage des Directors. Ich habe deshalb
drei Ebenen unabhaengig gemessen, jede naeher am echten Spielerverhalten als
die vorige:

1. **Direktes `QHelpEvent(QEvent.ToolTip)`** an `header.viewport()` (nicht an
   `header` selbst — das war ein Fehler in meinem ersten Versuch und erklaert
   ein anfaengliches Fehlschlagen, das **nicht** die App betraf, siehe
   Explorationsprotokoll). Ergebnis: `QToolTip.isVisible()==True`,
   `QToolTip.text()=="Type"` — der Mechanismus antwortet korrekt auf ein
   echtes ToolTip-Event, ohne Timer.
2. **`QTest.mouseMove` + echtes Warten**, offscreen. Hier zeigte sich bei
   1067 px ein kurzes Verschwinden bei 400 ms nach einem Erscheinen bei
   100 ms — ein Artefakt der synthetischen Qt-internen Event-Injektion unter
   `offscreen`, nicht reproduzierbar in Schritt 3 (siehe unten). Diese Ebene
   allein haette also selbst eine falsche Unsicherheit erzeugt.
3. **Echtes, am laufenden, sichtbaren Fenster gemessenes OS-Hover**: das
   eigentliche Verfahren fuer die Frage des Directors. `QCursor.setPos()`
   ruft dasselbe `SetCursorPos`, das ein echter Maustreiber ausloest — Windows
   liefert daraufhin echte `WM_MOUSEMOVE`, anders als `QTest.mouseMove`, das
   nur Qts eigene Event-Queue fuellt. Das Fenster war das echte `Planner`-
   Fenster (`nrplanner.app.Planner`, `apply_appearance()` genau wie `main()`
   es aufruft — Fusion, dunkle Palette, bestaetigt per
   `app.style().objectName() == "fusion"`), nicht offscreen, an Position
   (80, 80) auf dem echten Bildschirm, mit `NIGHTREIGN_SETTINGS_ORG/_APP`
   auf einen eigenen Store umgebogen. Fuer den Beleg, dass wirklich der
   Tooltip-Popup (ein eigenes Top-Level-Fenster, nicht Teil des Planner-HWND)
   erscheint, habe ich per `EnumWindows` das zum selben Prozess gehoerende
   Popup-HWND gefunden und **nur dieses** per `PrintWindow` fotografiert —
   nie den Bildschirm, nie ein fremdes Fenster.

### Messung — alle drei betroffenen Breiten, am laufenden Fenster

| Fensterbreite | Betroffene Spalte (die der `power-user` sah: `Comes with curse`) | Text gezeigt | Zeit bis `QToolTip.isVisible()==True` |
|---|---|---|---|
| **1320 (Standardmass beim Start)** | `Comes with c…` | volltext + Erklaersatz, korrekt | **~750-800 ms** feinaufgeloest gemessen |
| 1067 | `Comes…` | volltext + Erklaersatz, korrekt | ~800-1000 ms |
| 833 | `Co…` (identisch mit `Copies` und `Colours`) | volltext + Erklaersatz, korrekt | ~800-1000 ms |
| 833, Spalte `Copies` (die schaerfste Mehrdeutigkeit: drei Koepfe zeigen `Co…`) | `Co…` | eigener, von `Comes with curse` verschiedener Text | ~800-1000 ms |

Bei **1320 px — das ist die Breite, mit der das Programm startet, bevor der
Spieler irgendetwas tut** — steht laut T-060s eigener Tabelle genau **eine**
gekuerzte Spalte: `Comes with curse` → `Comes with c…`. Das ist Zeichen fuer
Zeichen die Stelle, die der `power-user` zitiert hat. Der `power-user` hat
also **nicht** in eine exotische, selbst herbeigefuehrte schmale Breite
navigiert — er hat den Ausgangszustand gesehen.

Screenshot des tatsaechlichen Popups (nur das Popup-Fenster, per `PrintWindow`
auf sein eigenes HWND, physische Pixelgroesse via `GetWindowRect` nach
`SetProcessDPIAware()` — die logische Groesse haette bei 150 % Skalierung nur
zwei Drittel des Fensters eingefangen, ein Messfehler, der mich beim ersten
Versuch selbst getaeuscht hat): zeigt exakt
`"Comes with curse\nWhether relics carrying this effect can also roll a curse
— 'sometimes' by relic, 'always cursed' without exception."` — Name plus
Erklaersatz, wie in `HEADER_TIPS[COL_CURSE]` hinterlegt. Bild lag unter
`…/scratchpad/nh/live_tooltip_<hwnd>.png`; **Scratchpad ist sitzungsgebunden,
das Bild ueberlebt diese Sitzung nicht** — die Zahlen und die Log-Ausgabe
oben sind die belastbare, dauerhafte Evidenz.

### Warum trotzdem etwas fuer den `ui-ux-designer` bleibt

Der Mechanismus funktioniert — aber er braucht **durchgehend ~750-800 ms**
ruhig gehaltenen Hovers, bevor er reagiert. Das ist Qts eigener, aus dem
laufenden Fenster ausgelesener Stilwert (`SH_ToolTip_WakeUpDelay = 700 ms`
unter Fusion) plus reales OS-Overhead — kein Zufall dieser Maschine, sondern
etwas, das jeder Spieler unter Fusion so vorfindet. Der `power-user` hat
selbst berichtet: *"ich habe nur kurz mit der Maus darueber gewartet"* — genau
die Kategorie Interaktion, die unter 700-800 ms bleibt und deshalb nichts
gesehen haben kann. Das ist neu und eigenstaendig gemeldet als **QA-151**
unten; es ist **keine** Wiedereroeffnung von QA-140.

**Antwort auf die groessere Frage des Directors:** Die Zusicherung "voller
Text im Tooltip" **traegt wirklich**, nicht nur auf dem Papier — sie ist am
laufenden Fenster nachgewiesen, nicht nur an einer Property. Sie traegt aber
mit einer Einschraenkung, die A11 beruehrt: der Beweis, dass Information *da*
ist, ist nicht dasselbe wie der Beweis, dass ein durchschnittlicher Spieler
sie in der Zeitspanne findet, die er einem Hover typischerweise gibt. Das
ist eine Designfrage (mehr Zeit lassen ist keine Option — der Wert kommt aus
dem Qt-Stil selbst; kuerzere Kopfnamen, ein sichtbareres "hier ist mehr"-
Signal oder eine bewusste Akzeptanz sind die Stellschrauben), keine, die ich
entscheide.

---

## 2. QA-140 bis QA-149 einzeln

| ID | Verdikt | Beleg |
|---|---|---|
| QA-140 | **behoben** | Abschnitt 1 oben, vollstaendig am laufenden Fenster nachgewiesen |
| QA-141 | **behoben** | Code: `cardgrid.CardGrid(margins=(0,0,0,0))`, `room_for()` fragt Scrollbar-Breite ab statt sie zu schaetzen. Mutation `picker-back-to-a-fixed-column-count` frisch gefahren: **3 failed** bei `[None/900/700]`, exakte Fehlertexte ("22 von 55 Karten angeschnitten bei 700 px") decken sich mit dem Bericht |
| QA-142 | **behoben** | Code: `stats_of(scaling, base_scaling)` ersetzt `set`-Vereinigung. Mutation `vs-standard-back-to-a-set` frisch gefahren: **1 failed**, "46 von 46 Kacheln" — Zahl deckt sich exakt |
| QA-143 | **behoben** | Code gelesen (`arsenaltab.py:382-395`): der `elif`-Zweig faengt jetzt sowohl die Erstansicht als auch eine Suche >60 Treffer ab. Nicht selbst neu mutiert (Stichprobe an anderer Stelle gesetzt), Suite gruen |
| QA-144 | **behoben** | Code gelesen (`depthstab.py:127-137`): `share = (available - depths) // 2`, ein Anteil statt eines geschaetzten Pixelwerts. Nicht selbst neu mutiert, Suite gruen |
| QA-145 | **behoben** | Mutation `sighting-colour-back-without-its-legend` frisch gefahren: **1 failed**, exakt der gemeldete Fall (Gladius: Legende 0x statt 1x). AK-94-Restluecke siehe Abschnitt 3 |
| QA-146 | **behoben** | `apply_appearance()` wird laut Code von `main()` und `tests/conftest.py::qapp` gleichermassen gerufen; live an drei eigenen Fensterinstanzen bestaetigt: `app.style().objectName() == "fusion"` in jedem Lauf. Skip-Zahlen der Suite (9 offscreen) exakt wie gemeldet |
| QA-147 | **behoben, und das ist die wichtigste Einzelbestaetigung dieses Retests** | Diese Mutation war in T-060 selbst zunaechst **zahnlos** (siehe deren Abschnitt 9b). Ich habe sie unabhaengig neu aus dem Repo-Text gezogen und frisch gefahren: **1 failed**, exakt der gemeldete Fall bei der schmalsten vom Fenstersystem erreichbaren Breite (964 px offscreen). Der zweite Anlauf des `developer` haelt wirklich |
| QA-148 | **behoben** | Code gelesen (`nrdata/extract.py:1313-1320`): der Satz baut sich aus `rungs` auf und nennt jetzt Stufenzahlen und Faktoren. `EXTRACT_VERSION = 11` bestaetigt |
| QA-149 | **behoben** | Code gelesen: `BUFF_NOTE` und `PARTS_NOTE` in `bosstab.py:126-142`, beide mit Bezugsgroesse ("against the same hit anywhere else...", "Defence steps carry their own duration") |

**Keine Abweichung von den in T-060 berichteten Zahlen gefunden**, weder bei
den sechs von mir frisch gefahrenen Mutationen noch bei den drei nur per
Code-Lesung bestaetigten Faellen.

---

## 3. Die 14 Mutationen: Stichprobe

6 von 14 frisch aus `scripts/differential/mutate.py` gezogen (nicht aus einer
Kopie oder Beschreibung — der exakte `old`/`new`-Text der Registry), je in
einer frischen `git archive HEAD`-Extraktion angewandt (kein `.git`, damit
`mutate.py`s eigene Schutzpruefung nicht anspringt — beim ersten Versuch
habe ich `mutate.py` versehentlich aus der mutierten Kopie selbst heraus
aufgerufen, was die eigene "das ist die Kopie, in der ich lebe"-Sperre
ausgeloest und beinahe einen falschen Gruen-Befund erzeugt haette, siehe
Explorationsprotokoll):

| Mutation | Datei | Erwartet (T-060) | Gemessen |
|---|---|---|---|
| `effect-headings-drawn-whole-or-not-at-all` | effectstab.py | 5 failed | **5 failed**, identische Testnamen |
| `effect-heading-tooltip-without-the-name` | effectstab.py | 5 failed | **5 failed**, identische Testnamen (bei erster, unvollstaendiger Dateiauswahl zunaechst nur 4 gesehen — Nachtrag mit beiden Testdateien ergab exakt 5) |
| `picker-back-to-a-fixed-column-count` | relicpicker.py | 3 failed | **3 failed**, inkl. exakter Zahl "22 von 55" bei 700 px |
| `vs-standard-back-to-a-set` | arsenaltab.py | 1 failed | **1 failed**, inkl. "46 von 46" |
| `nightlord-panel-back-to-a-fixed-width` | bosstab.py | 1 failed (**vormals zahnlos**) | **1 failed** — der reparierte Waechter beisst wirklich |
| `sighting-colour-back-without-its-legend` | bosstab.py | 1 failed | **1 failed** |

**Null Abweichungen.** Die verbleibenden acht (`picker-opening-width-...`,
`effect-headings-measured-while-elided`, `suite-measures-under-another-style`,
`arsenal-search-back-to-an-empty-page`,
`arsenal-opens-on-three-collapsed-headings-again`,
`examples-column-back-to-its-natural-width`,
`buff-and-parts-figures-without-a-reference`,
`rune-ladder-back-to-seven-bare-figures`) habe ich **nicht** erneut gefahren —
Stichprobe im Auftrag, sechs verschiedene Dateien/Mechanismen abgedeckt,
darunter bewusst die einzige Mutation, die beim ersten Anlauf durchgekommen
war.

---

## 4. Zwei Schulden aus T-060: beide bestaetigt offen

**AK-94-Luecke.** `bosstab.py:737` (`self._row("Set off by",
BUFF_TRIGGER[boss["name"]])`) und `bosstab.py:743`
(`bits.append(trigger)` im `DEFENCE_TRIGGER`-Zweig) — Zeilenzahlen heute 737/
743 statt der berichteten 730/736, reine Verschiebung durch einen
zwischenzeitlichen Formatierungscommit, derselbe Befund. Beide Stellen
drucken eine von Hand kuratierte Beobachtung (`BUFF_TRIGGER["Straghess"]`
lautet woertlich *"seemingly tied to how many adds are alive — least
certain"* — unmoeglich eine Extraktion) in der gewoehnlichen Textfarbe statt
in `OBSERVED_COLOUR`. Bestaetigt: **weiterhin offen**, wie vom `developer`
selbst gemeldet.

**Golden-Datei-Stempel.** `tests/golden/weapon_damage.json:4` traegt
`"extract_version": 10`, `nrdata/extract.py:79` steht auf `EXTRACT_VERSION =
11`. Gezielt gesucht, ob irgendein Test diesen Stempel gegen den Extraktor
vergleicht: **kein Treffer** (`tests/conftest.py`s
`_built_by_this_extractor`-Pruefung betrifft ausschliesslich den
Laufzeit-Snapshot, nie die Golden-Datei). Bestaetigt: **offen, und
nachweislich folgenlos** — kein Test wird davon gruen oder rot beeinflusst.

---

## 5. Die zwei ungeprueften Punkte aus dem `power-user`-Bericht

### 5.1 Nightlord-Karten: Fehlklick unbemerkbar

Code gelesen (`bosstab.py`, `BossCard`, `BossTab.show_detail`): jede Karte ist
komplett klickbar (`mousePressEvent` auf dem ganzen `QFrame`), das
`cardgrid`-Raster trennt Nachbarn durch **8 px** (`cardgrid.SPACING`). Beim
Klick aktualisiert `show_detail()` Bild, Name (15 px, fett) und Text im
Detailpanel — **aber keine einzige Codezeile veraendert das Aussehen der
Karte selbst.** Gezielt gesucht nach `selected`, `highlight`, `_current`,
`active`, `checked` im Zusammenhang mit `BossCard`: **0 Treffer.** Es gibt
keinen hervorgehobenen Rahmen, keine Hintergrundaenderung, kein sonstiges
Signal auf dem Raster, welche Karte gerade aktiv ist.

Das erklaert exakt, was der `power-user` beschreibt: er hat "Gnoster" statt
"Adel" getroffen und es **nicht am Raster gemerkt**, sondern erst am
Detailinhalt. Ein Portraitwechsel (256 px, deutlich sichtbar) ist der
staerkste Hinweis, den es gibt — er ersetzt aber keine Rueckmeldung *am Ort
des Klicks*. Das ist ein reproduzierbarer Befund, kein Verdacht: siehe
**QA-150** unten.

### 5.2 Red variants: fehlt eine Staerkeangabe wirklich in den Dateien?

Direkt am Snapshot geprueft: `deep_of_night.mutations` (46 Eintraege, Quelle
`ChaosMatchingMutationCategoryParam`) traegt ausschliesslich die Felder
`id, counts, category, group, varies` — keine numerische Groesse ausser den
Platzierungs-*Zaehlungen* je Tiefe. Die Roster-Quelle
(`ChaosMatchingMutationEnemyTableParam`, im Code gelesen) liefert
Charakter-IDs und Kachelpositionen, ebenfalls keinen Multiplikator. Beide vom
Code zitierten Herleitungsanker (Feldnamen, Byte-Offsets) sind im Kommentar
nachvollziehbar und stimmen mit dem tatsaechlich extrahierten Snapshot
ueberein — die Behauptung *"the game's files do not say by how much"* ist
fuer **diese beiden, tatsaechlich gelesenen** Paramtabellen wahr und deckt
sich mit A7.

**Grenze meiner Pruefung, ausdruecklich benannt:** Ich habe nicht
ausgeschlossen, dass irgendeine der ueber tausend ungelesenen Paramtabellen
des Spiels eine eigene, von diesen beiden getrennte Staerke-Kennzahl fuer
mutierte ("rote") Gegner traegt. Das waere eine neue Datenrecherche, keine
Verifikation einer bestehenden Behauptung, und liegt ausserhalb dessen, was
ein Retest leisten kann — dafuer gibt es die Rolle `researcher` (siehe
`docs/research/`, wo ich **keine** Notiz zu ChaosMatching/roten Varianten
gefunden habe: zwei unabhaengige Suchbegriffe, 0 Treffer). Innerhalb der
Grenzen dessen, was das Programm tatsaechlich liest, ist die Aussage auf dem
Bildschirm ehrlich und belegt — **kein Befund.**

---

## 6. Neue Befunde

### [P3 | Minor | Mittel] Nightlord-Kartenraster zeigt keine aktive Auswahl

**Adressat:** ui-ux-designer
**Betroffen:** `nrplanner/bosstab.py`, Klasse `BossCard` (Zeilen 248-317),
Methode `show_detail` (577 ff.)
**Umgebung:** Nightlords-Tab, jede Fensterbreite, jede Karte

**Reproduktion:**
1. Nightlords-Tab oeffnen.
2. Eine Karte anklicken, deren Nachbarin man eigentlich meinte (die zehn
   Karten stehen mit 8 px Abstand, `cardgrid.SPACING`).
3. Auf das Kartenraster zurueckblicken.

**Erwartet:** Ein Blick auf das Raster allein sagt, welche Karte aktiv ist.
**Tatsaechlich:** Keine Karte traegt einen Hervorhebungszustand. Die einzige
Rueckmeldung steht im Detailpanel (Portrait + 15-px-Name); das Raster selbst
sieht vor und nach dem Klick identisch aus.

**Analyse:** `show_detail()` schreibt ausschliesslich in die
Detailpanel-Widgets. Keine Codezeile in `BossCard` oder `BossTab` reagiert
auf "diese Karte ist die aktuell gewaehlte" (Suche nach `selected`,
`highlight`, `_current`, `active`, `checked` im Modul: 0 Treffer).

**Auswirkung:** Reproduziert am echten `power-user`-Lauf (T-063): ein knapper
Fehlklick (dort: Gnoster statt Adel) blieb unbemerkt, bis der Detailinhalt
gelesen wurde. Ein Spieler, der sich auf das Raster statt auf den Detailtext
verlaesst, plant moeglicherweise gegen den falschen Nachtlord, ohne es zu
merken — das beruehrt A11 direkt.

**Vorschlag:** Eine sichtbare Markierung der zuletzt geklickten Karte (Rahmen
oder Hintergrund, analog zum bestehenden `edge`-Rahmen fuer Everdark-Karten).
Kein Vorschlag zur genauen Gestaltung — das ist die Entscheidung des
`ui-ux-designer`.

---

### [P3 | Minor | Mittel] Spaltenkopf-Tooltip braucht ~750-800 ms ruhigen Hovers, ohne dass die Kuerzung selbst darauf hinweist

**Adressat:** ui-ux-designer
**Betroffen:** `nrplanner/effectstab.py`, `EffectTable._elide_headings` /
`set_headings`; strukturell jede Stelle im Projekt, die sich auf
Qt-Standard-Tooltips fuer eine Kurzfassung verlaesst
**Umgebung:** Effects-Tab, jede Breite, bei der mindestens ein Kopf gekuerzt
wird (833/1067/1320/1600 je nach Spalte)

**Reproduktion:**
1. Effects-Tab bei Standardbreite (1320 px) oeffnen — kein Resize noetig.
2. Maus auf `Comes with c…` bewegen und **weniger als ~700 ms** dort halten.
3. Wegbewegen.

**Erwartet:** Ein Spieler, der kurz hovert um zu pruefen "gibt es hier mehr
zu lesen", bekommt eine Antwort.
**Tatsaechlich:** Fuer knapp unter 700-800 ms gehaltenen Hover erscheint
nichts (gemessen am laufenden Fenster, Abschnitt 1). Der Wert ist Qts eigener
Fusion-Stilwert (`SH_ToolTip_WakeUpDelay`), kein Zufall dieser Maschine.

**Analyse:** Der Tooltip selbst funktioniert (Abschnitt 1) — das ist eine
Timing-/Entdeckbarkeitsfrage, keine Funktionsluecke. Das Ellipsis-Zeichen
signalisiert "gekuerzt", aber nichts signalisiert "und das lohnt einen
laengeren Hover als ueblich".

**Auswirkung:** Exakt der vom `power-user` berichtete Fall: kurzer Hover,
keine Erklaerung gesehen, geraten statt gelesen. Betrifft am staerksten die
833-px-Breite, wo drei Koepfe identisch `Co…` zeigen und nur der Tooltip sie
unterscheidet.

**Vorschlag:** Keiner meinerseits zur Umsetzung — der `developer` hat in
T-060 Abschnitt 12 bereits drei Ausweichrouten genannt (kuerzere Namen,
zweizeiliger Kopf, explizites Zugestaendnis). Ich ergaenze nur die
Beobachtung, dass die Zeitspanne selbst ein Faktor ist, unabhaengig davon,
welche der drei Routen gewaehlt wird.

---

### [P4 | Minor | Niedrig] AK-94-Luecke weiterhin offen: zwei Sichtungen ohne Sichtungsfarbe

**Adressat:** ui-ux-designer, developer
**Betroffen:** `nrplanner/bosstab.py:737` und `:743`

Bereits vom `developer` in T-060 Abschnitt 14 selbst gemeldet und von mir
bestaetigt (Abschnitt 4 oben). Kein neuer Fund; wird hier fortgefuehrt, damit
er im QA-Register sichtbar bleibt statt nur in einem Abschnitt eines
Entwicklerberichts zu stehen. Vorschlag unveraendert: die `Set off by`-Zeile
laesst sich analog zu den bestehenden `sighting(...)`-Aufrufen einfaerben; die
`Defence`-Zeile braucht zuerst eine Wortlautentscheidung (Satzteil-Sichtung
in sonst extrahierter Zeile).

---

### [P4 | Trivial | Niedrig] Golden-Datei traegt veralteten `extract_version`-Stempel

**Adressat:** developer, director
**Betroffen:** `tests/golden/weapon_damage.json:4` (`10`) gegen
`nrdata/extract.py:79` (`EXTRACT_VERSION = 11`)

Bereits vom `developer` in T-060 Abschnitt 14 selbst gemeldet, von mir
bestaetigt als weiterhin offen **und** als folgenlos (kein Test vergleicht
diesen Stempel). Reine Buchfuehrungsfrage, keine Funktionsauswirkung.
Vorschlag unveraendert: nur bei einem echten Neuaufnahme-Anlass mitziehen,
kein eigener Commit dafuer noetig.

---

## Zusammenfassung (an director)

**10 von 10 retesteten Befunde (QA-140 bis QA-149) sind behoben**, sechs
davon durch eine frisch gefahrene, unabhaengige Mutation bestaetigt statt nur
durch Code-Lesung — darunter die eine Mutation, die beim ersten Anlauf des
`developer` **zahnlos** war (QA-147/`nightlord-panel-back-to-a-fixed-width`):
der zweite Anlauf haelt wirklich. Keine Abweichung von den berichteten
Zahlen. **Der zentrale Auftrag — der Tooltip-Widerspruch — ist geklaert:
Lesart (b).** Der Tooltip existiert, ist korrekt und erscheint zuverlaessig
bei echtem, am laufenden Fenster gemessenem OS-Hover, bei genau der Breite
und genau der Spalte, die der `power-user` gesehen hat. Seine Beobachtung war
eine Grenze seiner kurzen Hover-Sitzung (unter ~700-800 ms), keine Luecke im
Programm. Zwei neue, kleinere Befunde (QA-150, QA-151) und zwei bestaetigte,
bereits bekannte Schulden (AK-94, Golden-Stempel) kommen dazu — keiner davon
ist releaseblockierend.

**Releasefaehig bezueglich QA-140 bis QA-149: ja.** Nichts in diesem Retest
verlangt einen weiteren Fix-Zyklus, bevor der Nutzer selbst am laufenden
Spiel pruefen kann.

## Explorationsprotokoll

- Frischer `git clone` im Scratchpad, Suite zweimal gefahren (`not slow` und
  `slow`) — beide Zahlen bestaetigt.
- Tooltip: zunaechst headless mit `QHelpEvent` an `header` (statt
  `header.viewport()`) gesendet → `isVisible()==False`. Das war ein Fehler in
  meinem Skript (falsches Zielobjekt), keine Beobachtung ueber die App — mit
  dem richtigen Ziel sofort korrekt. Danach `QTest.mouseMove` unter offscreen
  mit einem seltsamen Verschwinden bei 400 ms, das sich am echten Fenster
  (Schritt 3) nicht wiederholte — als Artefakt der Offscreen-Simulation
  eingeordnet, nicht als App-Verhalten gemeldet.
- Live-Fenster-Screenshot: erster Versuch mit `PrintWindow` in **logischer**
  Fenstergroesse zeigte nur zwei Drittel der Tabelle (150 % Skalierung nicht
  beruecksichtigt) — mit `SetProcessDPIAware()` + `GetWindowRect` (physische
  Groesse) korrigiert. Zweiter Fehlschlag: das Tooltip-Popup ist ein eigenes
  Top-Level-Fenster, `PrintWindow` auf das Planner-HWND zeigt es nie — geloest
  durch `EnumWindows` auf alle Fenster desselben Prozesses.
- Mutationskampagne: erster Versuch rief `mutate.py --tree .` aus der
  mutierten Kopie selbst auf und wurde von deren eigener
  "das ist meine eigene Kopie"-Sperre zurueckgewiesen — der Testlauf danach
  waere ohne angewandte Mutation gelaufen und haette einen falschen
  Gruen-Befund erzeugt, waere er nicht an der Ausgabe von `mutate.py` selbst
  aufgefallen. Korrigiert: `mutate.py` immer aus dem Klon heraus, `--tree` auf
  eine externe `git archive`-Extraktion.
- Bash unter Windows: `tar -C` mit rueckwaertsschraegen Pfaden schlaegt fehl;
  POSIX-Pfade (`/c/Users/...`) fuer alles, was `tar`/`git archive` sieht.

## Offene Fragen

Keine an eine andere Rolle — die einzige echte Unklarheit des Auftrags (Bug
oder Sitzungsgrenze bei QA-140) ist in Abschnitt 1 mit Messung beantwortet.

## Nicht getestet

- **Windows-Plattform-Suite (758/10/5) nicht als Ganzes nachgefahren** —
  Kostengrund (320 s zusaetzlich). Indirekt bestaetigt: alle drei Live-
  Fenstertests liefen unter der echten `windows`-Plattform und erreichten
  833 px ohne die Offscreen-Untergrenze von 964 px, genau das Verhalten, das
  den Unterschied zwischen beiden Laeufen erklaert.
- **8 der 14 Mutationen nicht neu gefahren** (Liste in Abschnitt 3) —
  Stichprobe im Auftrag, sechs verschiedene Dateien bereits abgedeckt.
- **Die vom `developer` selbst in T-060 §13 offen benannten Randfaelle**
  (Picker mit <5 Relikten, Suche auf 0 Treffer, Schwelle 60/61 exakt,
  Fenster-Resize waehrend offenem Nightlord-Detailpanel mit langem Inhalt) —
  nicht Teil dieses Auftrags, hier nur vermerkt, damit sie nicht als geprueft
  gelten.
- **Ob eine der ueber tausend ungelesenen Paramtabellen doch eine
  Staerke-Kennzahl fuer rote Varianten traegt** — das ist Datenrecherche,
  keine Verifikation, gehoert an `researcher`.
- **Tastaturbedienung, Bildschirmleser/Vergroesserung fuer den Tooltip** —
  ausserhalb des Auftrags; nur die Maus-Hover-Sitzung des `power-user` war
  hier zu klaeren.

## QA-Log

```markdown
| ID | Titel | Prio | Adressat | Status | Letzte Pruefung |
|----|-------|------|----------|--------|----------------|
| QA-140 | Effects: Spaltenkoepfe mitten im Wort beschnitten; Tooltip-Zusicherung am laufenden Fenster geprueft | P3 | developer, ui-ux-designer | **behoben** — OS-Hover am echten Fenster bei 1320/1067/833 px bestaetigt, ~750-800 ms bis sichtbar | 2026-09-05 |
| QA-141 | Relic picker schneidet die 5. Kartenspalte an | P2 | developer, director | **behoben** — Mutation frisch gefahren, 3/3 Faelle exakt | 2026-09-05 |
| QA-142 | `vs standard` ordnet seine Gruppen bei jedem Start anders | P3 | developer | **behoben** — Mutation frisch gefahren, 1/1 exakt | 2026-09-05 |
| QA-143 | Weapons: Suche >60 Treffer zeigt leere Flaeche | P3 | ui-ux-designer, director | **behoben** — Code bestaetigt, nicht neu mutiert | 2026-09-05 |
| QA-144 | Red variants: `Examples` breiter als `What can be red` | P3 | developer | **behoben** — Code bestaetigt, nicht neu mutiert | 2026-09-05 |
| QA-145 | Nightlords: drei Bedeutungen auf einem Gruen | P3 | ui-ux-designer | **behoben** — Mutation frisch gefahren, 1/1 exakt; Restluecke siehe AK-94-Eintrag unten | 2026-09-05 |
| QA-146 | Waechter messen unter anderem Stil als das Programm | P3 | developer, director | **behoben** — live an 3 Fensterinstanzen bestaetigt (Fusion) | 2026-09-05 |
| QA-147 | Nightlords bei 833 px: leeres Detailpanel haelt 330 px | P4 | ui-ux-designer | **behoben** — war beim ersten Anlauf zahnlos, zweiter Anlauf per frischer Mutation bestaetigt scharf | 2026-09-05 |
| QA-148 | World Events: Runen-Leiter ohne Bezugspunkte | P4 | developer, ui-ux-designer | **behoben** — Code bestaetigt, EXTRACT_VERSION 11 | 2026-09-05 |
| QA-149 | Nightlords: zwei Abschnitte ohne Bezugsgroesse | P4 | ui-ux-designer | **behoben** — Code bestaetigt (BUFF_NOTE, PARTS_NOTE) | 2026-09-05 |
| QA-150 | Nightlord-Kartenraster zeigt keine aktive Auswahl; Fehlklick bleibt am Raster unbemerkt | P3 | ui-ux-designer | offen | 2026-09-05 |
| QA-151 | Spaltenkopf-Tooltip braucht ~750-800 ms ruhigen Hovers ohne eigenes Signal dafuer | P3 | ui-ux-designer | offen | 2026-09-05 |
| QA-152 | AK-94-Luecke: `Set off by` und Defence-Ausloeser ohne Sichtungsfarbe | P4 | ui-ux-designer, developer | offen (vom developer selbst gemeldet, T-060) | 2026-09-05 |
| QA-153 | Golden-Datei `weapon_damage.json` traegt `extract_version: 10` gegen Extraktor 11 | P4 | developer, director | offen, folgenlos (vom developer selbst gemeldet, T-060) | 2026-09-05 |
```

Alle uebrigen Eintraege (QA-001 bis QA-139 und aeltere) unveraendert — siehe
bestehende Tabellen in `qa/findings.md`, hier nicht wiederholt.
