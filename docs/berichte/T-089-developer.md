STATUS: erledigt
AUFTRAG: T-089 - S10b, Teil 1: der Vorschlagsblock und der `Why`-Dialog (developer)
GELESEN: docs/tasks/T-089.md; UI_SPEC.md §3.1, §3.2, §3.4, §3.5, AK-18 bis AK-30, T-078-Abschnitt §2 bis §9 (AK-133 bis AK-150), T-080-Abschnitt §4 bis §9 (AK-151 bis AK-161), Director-Korrektur zu T-078/T-080 vom 06.09.2026, T-084-Nachtrag (AK-162 bis AK-176), T-086-Nachtrag (AK-177 bis AK-181); nrplanner/advisor/types.py, explain.py, run.py, goals.py, worker.py; nrplanner/advisorbar.py, app.py (RelicSlot, Planner), effecttext.py, inventory.py, uiscale.py; tests/conftest.py, tests/rendered.py, tests/test_advisor_bar.py, tests/test_game_text_is_never_markup.py; scripts/measure_advisor_language.py
GEAENDERT: nrplanner/advisorblock.py (neu), nrplanner/app.py, tests/test_advisor_block.py (neu), scripts/measure_advisor_block.py (neu) - alle vier committet (5a611a2, 8694154, 5e04ce6); docs/berichte/T-089-developer.md (neu, **nicht** committet); .claude/agent-memory/developer/MEMORY.md, project_pixel_measurements.md, project_advisor_display_path.md (nicht committet, Agentengedaechtnis)
ANNAHMEN: (1) Der Kopfsatz des `Why`-Dialogs hat keinen vorgegebenen Wortlaut - §3.4 nennt fuenf Angaben und keinen Satz; ich habe ihn formuliert und melde ihn unten woertlich. (2) Der `Begruendungssatz`, den der Auftrag im Block auffuehrt, wird nicht gezeichnet: AK-133 verbietet ihn und kein Feld traegt ihn. (3) Die `✦`-Legende steht immer dann, wenn ueberhaupt ein Fluch gezeichnet ist - die Fuellungen (i) und (ii) sind an der Datenform nicht unterscheidbar. (4) Die Halte-Zeile steht einmal, in der Fusszeile (AK-164), nicht zusaetzlich vor den Slotgruppen. (5) `⚠` fuer nicht stapelnde Effekte wird nicht gezeichnet - `ReasonLine` traegt die Auskunft nicht. Alle fuenf sind unten als Befund oder Frage aufgefuehrt.
NAECHSTER: qa-engineer
BLOCKIERT DURCH: nichts

---

## Umgesetzt

**`nrplanner/advisorblock.py` (neu)** - der Block, der Dialog und die
Zeilenformatierung:

- `line_markup(line)` / `lines_markup(lines)` - eine Zeile als das Markup, das
  sie zeichnet. Vier Faelle, alle vier **an der Form** entschieden
  (`is_curse`, `silence`), nie an den Worten: Fluch → `✦` in `CURSE`;
  Fuellung (a) → `•`, `BAD`, `<s>…</s>`; jede andere stumme Zeile → `•`,
  `MUTED`, 11 px; Zeile mit Zahl → `•` in `#cfcfcf` (die Farbe aus
  `_sync_mode`).
- `as_a_tooltip(text)` - Tooltip als ausgewiesener Rich Text ueber
  escapetem Inhalt.
- `SuggestionBlock` - `1px dashed ACCENT`, Radius 5, `PANEL`, Innenabstand 8;
  Kopfzeile `SUGGESTED — <ZIEL>` im `_heading`-Stil, Reliktname, Zaehlzeile,
  Zeilen. Gezeichnet werden nur die Zeilen, die `types.drawn_in_the_block`
  durchlaesst. Der Sonderfall `Already equipped — nothing to change here.`
  ersetzt alles uebrige.
- `WhyHeading`, `head_sentence`, `group_heading`, `WhyDialog` - modaler
  `QDialog`, Titel `Why this build — <Ziel>`, `resize(640, 620)`, einziger
  Knopf `Close`; Kopf, Slotgruppen (`Slot {n} — {Relikt}` einsbasiert,
  Zaehlzeile, **alle** Zeilen), 4.9b-Liste, `✦`-Legende, Fusszeile
  (`Goal.scope` → `unknowns` → `weights_note` → `budget_note` →
  `data_note`, in gelieferter Reihenfolge, ohne Vergleichen, Filtern,
  Sortieren oder Entdoppeln).

**`nrplanner/app.py`:**

- `RelicSlot.__init__` - der Block unter `rolled_label`.
- `RelicSlot.show_the_suggestion` / `put_the_suggestion_away` /
  `_suggested_curse_tooltip` - `already equipped` wird am **Handle**
  entschieden, nie am Namen; der Fluchtooltip wird ueber denselben Handle in
  `_holdable()` gefunden und mit dem vorhandenen `curse_tooltip` gebaut.
- `Planner._wire_the_advisor` (aus `__init__` gerufen, `_build_middle`
  unberuehrt), `Planner.show_the_suggestion`, `Planner.open_why`.

**Kein `Use`-Knopf, kein `Apply`, kein Anwenden** - der Block traegt
ueberhaupt kein Bedienelement (`test_the_block_carries_no_control`).

## Zuordnung ohne Namen (QA-180)

Nirgends wird eine Zeile ueber einen Namen einem Slot zugeordnet. Der Weg ist
durchgehend `ReasonLine.slot_index` / `SlotReasons.slot_index` →
`Planner.active_slots()[index]`, und die vorgeschlagene Kopie wird ueber
`SlotChoice.handle` gefunden. Ich bin **nicht** auf eine Stelle gestossen, an
der das ohne `model.py` nicht ginge - `ReasonLine` traegt allerdings **keine
Effekt-Id**, sodass die Anzeige eine Zeile gar nicht erst einem Effekt
zuordnen *kann* (siehe Befund 5). Der Fall `test_a_line_reaches_the_card_its_slot_names`
gibt beiden Slotgruppen denselben Reliktnamen, damit eine Zuordnung ueber
Namen dort nicht gruen sein kann.

## Zeilenmessung am laufenden Fenster (AK-160, AK-161)

Skript: `scripts/measure_advisor_block.py` (Commit 8694154). Es nennt seine
Umgebung selbst und misst den Zustand **vor** dem Zeichnen daneben.

**Messumgebung (L-009):** Plattform `windows` (die, auf der das Programm
laeuft), Qt-Stil `fusion`, `QT_SCALE_FACTOR` ungesetzt (= UI scale
`Automatic`), device pixel ratio 1.5, Bildschirm 1707x1067 **logische** px,
Fenster 1320x900 logische px. `data_version 10350000`, Stufe 15, Richtung
`Maximise damage`, Deep of Night an, 309 Relikte. Alle Breiten **logisch**,
alle Zeilenzahlen sind gezeichnete Zeilen **vor** dem Umbruch.

Zaehlweise: Block = 3 Kopfzeilen (`SUGGESTED — <Ziel>`, Reliktname,
Zaehlzeile) + die im Block gezeichneten Zeilen. Dialog = 1 Kopfzeile + je
Gruppe (2 Kopfzeilen + **alle** Zeilen) + 4.9b-Liste + Legende + Fusszeile.

| Nightfarer / Vessel | Block je Karte | Block gesamt | `Why`-Dialog | groesste Gruppe im Dialog |
|---|---|---|---|---|
| Wylder / `Wylder's Goblet` | 5, 5, 4, 5, 10, 7 (hoechste **10**) | 36 | **54** | 10 |
| Ironeye / `Sealed Ironeye's Urn` | 5, 4, 1, 10, 9, 9 (hoechste **10**) | 38 | **55** | 9 |

(Die Karte mit **1** Zeile bei Ironeye ist der Fall `Already equipped`.)

**Schlechtfall, nachgestellt.** Die groesste Slotgruppe, die dieser Spielstand
erzeugen kann, ist - auf beiden Figuren - **14 Zeilen auf `Deep Grand
Tranquil Scene`**, also genau das Relikt, das AK-160 nennt. In **jeden** der
sechs Slots gelegt ergibt das **17 Zeilen je Karte** (14 + 3 Kopfzeilen); im
Dialog waeren es 16 je Gruppe (14 + 2). Alle 14 Zeilen sind Zahl- oder
Fluchzeilen - die eine stumme Zeile dieses Relikts ist ein **Fluch** ohne
Zahl und steht daher auch im Block. **Der Block faellt hier also nicht
kleiner aus als der Dialog**; die Ersparnis der Director-Korrektur 1 traegt
bei diesem einen Relikt nicht (bei den echten Vorschlaegen oben sehr wohl:
36 gegen 54 bzw. 38 gegen 55 Zeilen).

**Waagerechte Bildlaufleiste in der mittleren Spalte (AK-160):**

| Umgebung | Fenster | mittlere Spalte | mit Bloecken | ohne Vorschlag |
|---|---|---|---|---|
| `windows`, Automatic | 1320x900 | 468 px | **0..0 px** | 0..0 px |
| `windows`, `QT_SCALE_FACTOR=1.5` | **1140x698** | 288 px | **0..0 px** | 0..0 px |
| `offscreen`, Automatic | 1320x900 | 468 px | 0..25 px | **0..11 px** |
| `offscreen`, 1.5 | 1320x900 | 468 px | 0..25 px | 0..11 px |

Keine Zeile ist abgeschnitten (kein Label ist schmaler als sein
`minimumSizeHint`, und im Modul gibt es kein `elidedText`), jede bricht um
(`setWordWrap(True)` ueberall), und jede ist durch senkrechtes Scrollen
erreichbar. **Kein Bildschirmabzug** (NH-002).

Drei Anmerkungen zu diesen Zahlen, die ohne sie falsch gelesen wuerden:

1. **Bei 150 % ist 1320 px auf dieser Maschine nicht messbar.** Der Bildschirm
   meldet dann 1138x711 logische px, das Fenster klemmt auf 1140x698. Gemessen
   ist also die **schmalere** Lage (mittlere Spalte 288 statt 468 px), und sie
   besteht die Pruefung ebenfalls.
2. **Offscreen aendert `QT_SCALE_FACTOR` nichts** an den Layoutzahlen - die
   beiden offscreen-Zeilen sind identisch. Eine offscreen-Messung "bei 150 %"
   ist keine zweite Messung.
3. **Die offscreen-Ueberlaeufe sind nicht meine.** 11 px stehen dort schon
   **ohne jeden Vorschlag** (Inhalt 479 px gegen 468 px Sichtfeld). Die 25 px
   mit Bloecken sind dieselben 11 px plus die senkrechte Bildlaufleiste, die
   das Sichtfeld von 468 auf 454 verengt. Unter `windows` ist beides 0.

## Tests

`tests/test_advisor_block.py` (neu), **36 Faelle**, ohne Spielinstallation
lauffaehig ausser den sechs, die die `planner`-Fixture nehmen.

**Die drei ausdruecklich verlangten Gegenbauten** - jeder einzeln angewandt,
im **Standardlauf** (`pytest tests/test_advisor_block.py`, keine
Sonderkonfiguration), danach zurueckgesetzt:

| # | Gegenbau | wird rot |
|---|---|---|
| 1 | `drawn = list(group.lines)` - stumme Zeilen auch im Block | `test_the_block_leaves_the_silent_effects_to_the_why_dialog` |
| 2 | den `SILENT_ANOTHER_NIGHTFARER`-Zweig entfernen, Fuellung (a) faellt auf `MUTED` | `test_an_effect_of_another_nightfarer_is_drawn_as_the_program_draws_one` |
| 3 | `types.drawn_in_the_block` ohne `line.is_curse` - der Fluch ohne Zahl faellt weg | `test_every_curse_of_the_copy_stands_in_the_block` (und Fall 1) |

**Acht weitere Gegenbauten, alle toetend:**

| Gegenbau | wird rot |
|---|---|
| Zaehlzeile geleert | `test_the_count_line_stands_in_the_block` |
| Legende immer sichtbar | `test_a_dialog_without_a_curse_carries_no_legend` |
| `weights_note`/`budget_note`/`data_note` bedingungslos angehaengt | `test_an_empty_budget_note_draws_nothing_at_all` |
| kein `html.escape` vor der Interpolation | `test_a_hostile_name_is_shown_letter_for_letter` |
| Tooltip unveraendert weitergereicht | `test_a_tooltip_is_declared_rich_text_…` (+ der Fall darueber) |
| `already equipped` am Namen statt am Handle | `test_the_slot_tells_the_suggested_copy_from_the_one_it_holds` |
| 4.9b-Liste immer sichtbar | `test_an_answer_with_nothing_left_out_draws_no_conditional_list` |
| jede Gruppe auf die erste Karte gezeichnet | `test_a_line_reaches_the_card_its_slot_names` |
| Gruppenkopf nullbasiert | `test_the_dialog_heads_each_group_with_a_one_based_slot` |
| Pruefung auf zu viele Slots entfernt | `test_an_answer_for_more_slots_than_this_vessel_has_draws_nothing` |
| `QSizePolicy.Ignored` entfernt | `test_the_block_asks_the_card_for_no_width_of_its_own` (4840 gegen 160 px) |

**Rot-vorher, konkret (L-007):** jede Zeile oben nennt die Aenderung am
**Produktionscode**, die den Fall heute brechen wuerde - keine davon ist eine
Schnittstellenverschiebung, alle sind Verhaltensaenderungen. Die Erwartungen
der Faelle sind Literale aus `UI_SPEC.md` bzw. aus dem Wortlaut der
Director-Korrektur, nicht aus dem gepruefen Code gerechnet (L-008 b). Der
Breitenfall vergleicht eine **Beziehung** (Karte mit Block gegen Karte ohne),
und die Mutation bewegt nur eine Seite davon - gepruefte Ausgabe 4840 gegen
160.

**Zwei Gegenbauten haben zuerst ueberlebt (L-008 c), beide gemeldet statt
stillschweigend nachgebessert:**

1. *`open_why` ohne die Pruefung auf die fehlende Antwort.* Der Fall rief ueber
   `why_requested.emit()`; eine Ausnahme in einem Qt-Slot kommt aus `emit`
   nicht zurueck, also blieb er gruen, obwohl der Code in
   `result.goal_label` lief und warf. **Behoben** (Commit 5e04ce6): der Fall
   ruft `planner.open_why()` geradeaus, die Mutation ist jetzt toetend.
2. *`show_the_suggestion` leert nur die Karten im Spiel statt alle.* Ueberlebt
   weiterhin, und das ist ein **aequivalenter Mutant**: `Planner.recompute`
   ruft `advisor_bar.the_build_changed()`, die Leiste wirft die Antwort weg
   und schickt `None`, bevor eine Deep-Karte aus `active_slots()` fallen kann.
   Der Code bleibt breit (die Regel "keine Karte behaelt einen Block, wenn
   keine Antwort steht" ist die dieser Methode), und der Kommentar sagt
   ausdruecklich, dass kein Fall ihn fangen kann. Ein Kommentar, der vorher
   einen erreichbaren Fall behauptete, ist mit korrigiert.

**Maskierungssuche (L-006), Trefferzahlen:**

- Maske A, `grep "QLabel(" nrplanner/advisorblock.py`: **2** Treffer (beide
  Fabriken `_plain`/`_rich`), beide setzen `setTextFormat`; dazu **1**
  ausdruecklicher Aufruf auf dem `_heading`-Label = **3** `setTextFormat` im
  Modul, **0** Elemente auf `Qt.AutoText`.
- Maske B, `grep "f\"<div|f\"<html|<s>{|{text}<" nrplanner/advisorblock.py`:
  **5** Interpolationsstellen in Markup, alle ueber `text = html.escape(...)`;
  dazu die Tooltipstelle in `as_a_tooltip`, ebenfalls escaped - **6 von 6**.
- Maske C, zur Laufzeit statt am Text: `test_no_text_element_of_the_advisor_runs_on_autotext`
  laeuft ueber **jedes** `QLabel`, das Block und Dialog besitzen (nicht ueber
  eine Liste genannter Namen) - **0** auf `AutoText`.
- Gegenprobe im Bestand: `nrplanner/advisorbar.py:329` benutzt bereits
  `f"<span>{html.escape(text)}</span>"` fuer seinen Tooltip - dieselbe
  Vorkehrung, unabhaengig in T-083 gebaut. **Kein weiteres Element des
  Beraters** zeigt Fremdtext ohne ausgewiesenes Format.

**Ausgefuehrte Befehle und Ergebnis:**

```
.venv\Scripts\python.exe -m pytest -m "not slow" -q
  vor meiner Arbeit: nicht selbst gemessen - der Auftrag nennt
  1107 passed, 9 skipped, 5 deselected, und 1107 + 36 neue = 1143 geht auf
  nach Commit 5a611a2: 1142 passed, 9 skipped, 5 deselected (550.94s)
  nach Commit 8694154: 1143 passed, 9 skipped, 5 deselected (542.94s)
  nach Commit 5e04ce6: 1143 passed, 9 skipped, 5 deselected (523.04s)

frischer Baum (git archive HEAD | tar -x, HEAD = 5e04ce6), gelaufen aus dem
Export heraus mit demselben Interpreter:
  1143 passed, 9 skipped, 5 deselected in 638.26s (0:10:38)
```

**Linter:** das Projekt hat keinen konfiguriert (kein `.flake8`, `ruff.toml`,
`pyproject.toml`, `setup.cfg`, `tox.ini`, `.pylintrc` - geprueft im
Wurzelverzeichnis). Der Punkt entfaellt.

## Commits

| Commit | was |
|---|---|
| `5a611a2` | `feat(advisor): der Vorschlag steht in der Karte, der Why-Dialog erklaert ihn` - advisorblock.py, app.py, tests |
| `8694154` | `fix(advisor): der Block verlangt keine Breite, und die Messung sagt warum` - `QSizePolicy.Ignored`, Waechter, Messskript |
| `5e04ce6` | `test(advisor): Why ohne Antwort wird direkt gerufen, nicht ueber das Signal` - ueberlebender Gegenbau, korrigierter Kommentar |

`nrplanner/advisorbar.py` und `tests/test_advisor_bar.py` stehen weiterhin als
geaendert in `git status`, mit leerem `git diff` - das im Auftrag genannte
Zeilenende-Rauschen. **In keinem Commit.**

## An qa-engineer

Was zu testen ist, und die Kanten, die ich beim Bauen gesehen habe:

- **Der `Why`-Dialog ist heute mit der Maus nicht erreichbar** - siehe Befund
  1. Fuer eine Abnahme: `planner.open_why()` bzw.
  `planner.advisor_bar.why_requested.emit()` nach einem echten `Optimize`.
- **Der Schlechtfall.** `Deep Grand Tranquil Scene` in einem Deep-Slot, sechs
  belegte Slots, Fensterbreite 1320 px - 17 Zeilen je Karte. Zu pruefen ist
  auch die **schmale** Lage: bei UI scale 150 % klemmt das Fenster auf 1140 px
  und die mittlere Spalte auf 288 px, was der engere Fall ist.
- **`Already equipped`.** Tritt auf dem echten Spielstand wirklich auf (eine
  von sechs Karten bei Ironeye). Dort faellt **alles** weg ausser der einen
  Zeile - auch die Kopfzeile mit dem Ziel. Das ist §3.2 woertlich; falls das
  in der Abnahme stoert, ist es eine Frage an den ui-ux-designer, keine an
  mich.
- **Der Fluchtooltip** haengt am Zeilenblock des Vorschlags und ist bei
  Nicht-Deep-Relikten leer (die tragen keine Fluche) - gemessen: Slots 0-2
  leer, Deep-Slots 209 / 313 / 365 Zeichen. Leer ist richtig, nicht fehlend.
- **Ein Relikt-, Effekt- oder Fluchname mit `<b>x</b><img src=x>&lt;`**
  erscheint buchstabengetreu in Block, Dialog und Tooltip. Der Tooltip ist
  ausgewiesener Rich Text ueber escapetem Inhalt - blosses Escapen haette dem
  Spieler `&lt;b&gt;` gezeigt, was ebenfalls nicht buchstabengetreu ist.
- **Nicht abgedeckt, bewusst:** alles Anwendende (`Use`, `Apply all`,
  `Undo apply`), `Hold`/`Held`, der Relic Picker, die Advisor bar selbst.
- **Kein Fall prueft ueber Namen**, weder Zuordnung noch Identitaet. Bitte
  Findings zur Zuordnung an QA-180 haengen, nicht an die Anzeige.

## An ui-ux-designer

Vier Stellen, an denen die Vorgabe entweder schweigt oder sich widerspricht.
Ich habe jeweils entschieden und baue nichts um, bevor es beantwortet ist.

1. **Der Kopfsatz des `Why`-Dialogs hat keinen Wortlaut.** §3.4 Punkt 1 nennt
   fuenf Angaben. Gebaut ist, vom `developer` formuliert (wie 4.7 in T-082):
   > `{Ziel} — {Nightfarer}, {Vessel}, Deep of Night {on|off}, {n} relics considered.`
   > z. B. `Maximise damage — Wylder, Wylder's Goblet, Deep of Night on, 309 relics considered.`
   Einzahl: `1 relic considered`. Gehoert ins S10-Review.
2. **Die `✦`-Legende: die Bedingung aus §3 ist nicht entscheidbar.** §3
   verlangt sie, "wenn mindestens eine Fluchzeile der Fuellung (ii) oder (iii)
   im Dialog steht". Die Fuellungen (i) und (ii) sind an der Datenform
   identisch (`is_curse=True`, `silence=CARRIES_A_FIGURE`); sie
   auseinanderzuhalten hiesse den Satz zu lesen, was AK-147 verbietet. Gebaut
   nach **AK-141**: genau einmal je Dialog, immer wenn ueberhaupt ein `✦`
   gezeichnet ist, und in keinem Block. Entweder die Bedingung wird auf "wenn
   ein Fluch gezeichnet ist" gesetzt, oder `ReasonLine` braucht eine eigene
   Auskunft fuer Fuellung (ii).
3. **Die Halte-Zeile steht an zwei Orten gleichzeitig.** T-078 §7 Punkt 2
   setzt sie **vor** die Slotgruppen; AK-164 setzt `AdvisorResult.unknowns`
   unter die `Goal.scope`-Saetze in Punkt 4 - und `explain.unknowns()` gibt
   genau die Halte-Zeile zurueck. AK-165 verbietet, sie an einem der beiden
   Orte herauszufiltern. Gebaut nach **AK-164** (juenger und benennt das
   Feld), also einmal, in der Fusszeile. Heute ist nichts davon sichtbar:
   `asking_from` haelt keinen Slot, also ist `unknowns` immer leer.
4. **`⚠` fuer nicht stapelnde Effekte ist nicht zeichenbar** - siehe Befund 5.
   §3.2 und T-078 §7 nennen es als Bestand aus `_sync_mode`; ich zeichne es
   nicht.

## An director - Befunde (ohne Nummer, wie verlangt)

**1. Der `Why`-Dialog hat keinen Ausloeser.** §3.1 sieht `Apply all` / `Why` /
`Clear` in der Leiste vor; T-083 hat nur `Clear` gebaut, und die Leiste ist
mir hier verboten. Der Dialog haengt an `AdvisorBar.why_requested`, das
**nichts** emittiert (geprueft: `grep -rn "why_requested" nrplanner/` gibt die
Definition und meine Verbindung, keinen Sender). *Risiko:* niedrig, der Code
ist fertig und wartet auf einen Knopf. *Aufwand:* eine Zeile in der Leiste -
gehoert sinnvollerweise in den Auftrag, der `Apply all` baut, weil die drei
Knoepfe nach §3.1 zusammen erscheinen.

**2. `explain.py` baut die Fuellungsreihenfolge von T-080, nicht die von
AK-167/AK-177/AK-178/AK-179.** `_silent_effect` prueft (a) → (a2) → **(b)** →
**(c)** → (d) → (e), und `_ARMAMENT_GATES` (vier Felder, `wepTypeTriggerCount`
eingeschlossen) ist unveraendert der Ausloeser von (c);
`model.satisfied_by_weapon`, der Wertevorrat der Waffentypen und
`startSwordArtsId` kommen dort nicht vor. **Gemessen** mit
`scripts/measure_advisor_language.py` auf dem heutigen Spielstand (Wylder,
Stufe 15, 309 Relikte, 845 Effektrollen):

| Fuellung | gebaut | AK-180 verlangt |
|---|---|---|
| (a) | 150 | 150 |
| (a2) | 0 | 0 |
| (b) | **170** | **144** |
| (c) | **13** | **38** |
| (d) | **93** | **94** |
| (e) | 0 | 0 |
| Summe | 426 | 426 |

Die Summe stimmt, die Verteilung nicht - genau der Fall, vor dem AK-180s
Rot-vorher warnt. *Risiko:* A5/A11 - eine Zeile sagt "it depends on the
armaments you carry" ueber Effekte, die keine Armatur verlangen (AK-177 nennt
19 von 20 solcher Zeilen). *Aufwand:* mittel, liegt ganz in `explain.py` und
braucht `model.WEAPON_TYPE_GATES` + den Wertevorrat aus `data["weapons"]`.
*Betrifft meine Arbeit nicht:* die Anzeige nimmt die Fuellung entgegen und
faerbt danach; sie wird von selbst richtig, sobald die Rechnung es ist.
**Empfehlung: eigener Auftrag an den `developer`, vor der QA-Abnahme von
S10b.**

**3. Die Statuszeile 4.9 in `advisorbar.py` ist die alte.** Zeile 181 sagt
`some effects carry no numbers.`; AK-142/AK-143 verlangen die zwei getrennten
Klauseln (`{n} curses carry no number.` und `{n} effects were left out: they
only apply under a condition.`). Ebenso ist 4.7 dort
`… working out. Optimize again.`, waehrend AK-173 buchstabengetreu
`… working out — use Optimize again.` verlangt. Beides in der Leiste (T-083),
beides mir verboten. *Risiko:* AK-143/AK-173 fallen in der Abnahme durch.
*Aufwand:* klein.

**4. Der Auftrag und AK-133 widersprechen sich beim Begruendungssatz.** T-089
listet unter "Was der Block zeichnet" `· der Begruendungssatz`, und §3.2
(Zeilen 130-160) beschreibt ihn noch; AK-133 verbietet ihn ausdruecklich
("zeigt **keinen** zusammenfassenden Begruendungssatz", `Chosen for` kommt im
Programm nicht vor) und T-078 §7 hat ihn gestrichen. Es gibt auch **kein
Feld**, das ihn traegt. Gebaut nach AK-133: nicht gezeichnet.

**5. `ReasonLine` traegt weder eine Effekt-Id noch die Stapelbarkeit, also
kann `⚠` nicht gezeichnet werden.** §3.2 und T-078 §7 verlangen "`⚠` fuer
nicht stapelnde Effekte - Bestand aus `_sync_mode`". `_sync_mode` liest dafuer
`effect["stacks"]`; die Anzeige des Beraters hat den Effektsatz nicht und darf
den Satz nicht durchsuchen (AK-147). Hinzu kommt: der Fall, den `_sync_mode`
mit `⚠` markiert, ist im Berater Fuellung (a2), und AK-156 verbietet `⚠` auf
stummen Zeilen ausdruecklich. *Entscheidung noetig:* entweder `⚠` faellt aus
§3.2 (meine Empfehlung - die Aussage steht als Fuellung (a2) in Worten da), 
oder `ReasonLine` bekommt ein Feld dafuer, was `explain.py` betrifft und
S9 nachtraeglich aendert.

**6. Bestehende Debt, nicht angefasst:** `RelicSlot._sync_mode`
(`nrplanner/app.py:650-687`, die Markup-Zeile ist `:684`) und `curse_tooltip`
(`:746`) interpolieren Relikt-, Effekt-
und Fluchnamen ungefiltert in Rich Text bzw. in einen Tooltip
(`f"<div …>&bull; {name}"`, `f"  • {effecttext.name(eff)}"`). Das ist
dieselbe Luecke, die AK-29/AK-30 fuer den Berater schliessen, im **Bestand**
der Slotkarte. Ich habe sie nicht behoben (ausserhalb des Auftrags, und
`_sync_mode` gehoert nicht zu den vier Stellen, die T-089 nennt). *Risiko:*
ein praeparierter Name aus einem fremden Spielstand oder einer manipulierten
Datenlage wird als Markup gerendert, `<img src=…>` laedt eine Ressource.
*Aufwand:* klein - `html.escape` an drei Stellen und ein
`setTextFormat(Qt.RichText)`. **Empfehlung: an den `security-reviewer`
melden.**

**7. Messumgebung, zwei Zahlen, die kuenftige Auftraege betreffen:** (a) bei
UI scale 150 % meldet dieser Bildschirm 1138x711 logische px, ein
1320-px-Fenster ist dort **nicht herstellbar**; jede AK, die 1320 px *und*
150 % verlangt, ist auf dieser Maschine nur an der geklemmten Breite pruefbar.
(b) Offscreen ignoriert `QT_SCALE_FACTOR` fuer die Layoutzahlen vollstaendig -
eine offscreen-Messung "bei 150 %" ist dieselbe Messung wie bei Automatic.

## Was mir sonst aufgefallen ist

- `nrplanner/advisor/types.py` traegt mit `drawn_in_the_block` bereits die
  Entscheidung der Director-Korrektur 1 **an der Datenform**. Das war die
  Stelle, an der dieser Auftrag haette schiefgehen koennen, und sie war schon
  richtig gebaut - ich habe sie benutzt statt eine zweite Regel zu schreiben.
- `AdvisorBar.suggestion_changed` hatte bis heute keinen Empfaenger und
  `why_requested` hat weiterhin keinen Sender. Die Haelften passen zusammen;
  es fehlt nur der Knopf.
- Der `Why`-Dialog oeffnet auch, wenn ein Lauf **keinen** Vorschlag hat
  (4.10/4.11): Kopf und Fusszeile stehen dann fuer sich, was §3.1 fuer 4.10
  ausdruecklich verlangt ("`Why` bleibt erreichbar und erklaert es lang").
