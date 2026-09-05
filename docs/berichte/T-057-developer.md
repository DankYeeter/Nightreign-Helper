```
STATUS: teilweise
AUFTRAG: T-057 — Die sechs Tabs: erst die falschen Zahlen, dann die Beschriftungen, dann die Waechter
GELESEN: docs/tasks/T-057.md · UI_SPEC.md (Abschnitt "Die sechs Inhalts-Tabs (T-056)", AK-68 bis AK-105, sowie der Nachtrag zu AK-67) · GOAL.md (A7, A10 bis A14) · DESIGN_REVIEW.md (DR-013 bis DR-018) · docs/berichte/T-055-qa-engineer.md (QA-125 bis QA-139, QA-128 Belegliste, QA-137 Gegenbau) · docs/berichte/T-056-ui-ux-designer.md · docs/berichte/T-054-power-user.md (existiert seit 05.09. 13:39 auf Platte — der `ui-ux-designer` hat zum Zeitpunkt seiner Suche wahr berichtet) · nrplanner/{effectstab,arsenaltab,bosstab,deeptab,depthstab,eventstab,eventlore,advisor/candidates,advisor/goals,damage,weapons}.py · nrdata/{extract,bossdata}.py · tests/{conftest,test_arsenal_tab_asks_the_facade,test_pool_finding_wording,test_differential_track}.py · scripts/differential/mutate.py · CLAUDE.md
GEÄNDERT: nrplanner/tabheader.py (neu) · nrplanner/effectstab.py · nrplanner/bosstab.py · nrplanner/deeptab.py · nrplanner/depthstab.py · nrplanner/eventstab.py · nrplanner/eventlore.py · nrplanner/arsenaltab.py · nrplanner/advisor/candidates.py · scripts/differential/mutate.py · tests/tabtext.py (neu) · tests/test_effects_tab_display.py (neu) · tests/test_nightlord_panel_display.py (neu) · tests/test_deep_tab_display.py (neu) · tests/test_red_variants_display.py (neu) · tests/test_world_events_display.py (neu) · tests/test_arsenal_tab_asks_the_facade.py · tests/test_pool_finding_wording.py — alle in 11 eigenen Commits d0d04c9..856101f. Keine fremde Datei angefasst, kein push/pull/fetch/merge/rebase/checkout/branch/reset/revert/stash.
ANNAHMEN: (1) `DEBUFF_ON_BREAK` und `ladder.down` sind **nicht** nachweisbar derselbe Mechanismus — Begruendung unten, Punkt 1; ich habe deshalb getrennt dargestellt statt zusammengefuehrt. (2) Die Scope-Grenze "DR-013 bis DR-018 gehoert T-058" habe ich woertlich genommen, also auch fuer DR-017/AK-83 und DR-018/AK-75, die keine Geometrie sind — beide sind offen und unten benannt. (3) Fuer AK-70 Punkt 10 (`stamina recovery speed +5`) gibt §7 keinen Wortlaut vor; ich habe einen im vorgeschriebenen Stil geschrieben ("the files do not say") und markiere ihn als von mir, nicht vom `ui-ux-designer`.
NÄCHSTER: director
BLOCKIERT DURCH: nichts
```

# T-057 — Bericht des `developer`

## 0. Stand in Zahlen

| | vorher | nachher |
|---|---|---|
| `-m "not slow"` | 622 passed, 5 deselected | **662 passed, 5 deselected** |
| `-m "slow"` | 5 passed | **5 passed** |
| Tests, die die Anzeige der sechs Tabs lesen | 0 fuer fuenf Tabs, 8 fuer den Arsenal-Tab | **40 neue**, mindestens einer je Tab |
| Mutationen in `scripts/differential/mutate.py` | 55 | **63** |
| QA-137, alle sieben Mutationen gleichzeitig | 622 von 622 gruen | **16 failed, 646 passed** |

Befehle und Ausgaben stehen unten bei den jeweiligen Punkten.

---

## 1. Die verlangte Antwort: `DEBUFF_ON_BREAK` gegen `ladder.down`

**Antwort: die Daten geben nicht her, dass es derselbe Mechanismus ist, und
an einer Stelle sprechen sie ausdruecklich dagegen.** Woran ich das
festmache, in der Reihenfolge des Gewichts:

1. **`x2.0 damage taken` hat im ganzen Datensatz keine Entsprechung.** Das
   einzige Feld, das an einer `ladder`-Zeile in diese Richtung zeigt, ist
   `saReceiveDamageRate`, und das ist **Stance**-Schaden, nicht Schaden. Es
   steht auf allen `down`-Zeilen bei 1,118 oder 1,136. Ein Faktor 2,0 auf
   erlittenen Schaden kommt nirgends vor. Diese Haelfte der Zeile ist also
   nicht nur unbelegt, sie ist unbelegbar.
2. **Die Menge der Namen passt nicht.** Gemessen ueber alle zehn Nightlords
   (`ladder.down`, aus `%LOCALAPPDATA%\NightreignHelper\nightreign_data.json`):

   | Boss | `ladder.down` Angriff | in `DEBUFF_ON_BREAK`? |
   |---|---|---|
   | Gladius | 0,815 | ja |
   | Adel | 0,917 | nein |
   | Gnoster | 0,846 und 0,957 | nein |
   | Maris | `null` | nein |
   | Libra | 0,957 | nein |
   | Fulghor | 0,88 | nein |
   | Caligo | `[]` (leer) | **ja** |
   | Harmonia | 0,8 | nein |
   | Straghess | 0,8 | nein |
   | Heolstor the Nightlord | `[]` (leer) | **ja** |

   Caligo und Heolstor tragen eine `ladder` mit `up`-Eintraegen und einer
   **leeren** `down`-Liste — der Extraktor hat dort gesucht und nichts
   gefunden, das ist kein fehlender Schluessel. Waeren die beiden Groessen
   dasselbe, muesste die Extraktion sie finden.
3. **Die Herkunft ist verschieden.** `ladder.down` ist ein SpEffect aus dem
   Band 7330–7398 mit `physicsAttackPowerRate < 1`, und `nrdata/bossdata.py`
   haengt an die meisten Eintraege ein `from` mit Animation und Zeitpunkt —
   bei Gladius Animation 20004 bei t=9,133, also der Taunt-Walk, den
   `BUFF_TRIGGER` als Ausloeser seines **Selbstbuffs** nennt. Harmonia und
   Straghess teilen sich Zeile 7397 **ohne** Animation. `DEBUFF_ON_BREAK`
   dagegen ist laut Kommentar eine Sichtungsliste zum Stance-Bruch.
   Ein gemeinsamer Ausloeser ist aus den Dateien nicht ableitbar.

**Was ich daraus gebaut habe** (`nrplanner/bosstab.py`, Commit 555d749):

* Die beiden handgetippten Groessen sind **weg**. Kein Ersatz, keine
  geschaetzte Zahl (A7, deine Vorgabe).
* Die Sichtung **bleibt als Sichtung**: ein Satz in `OBSERVED_COLOUR`
  (`#7fae72`, AK-94), der sagt, was gesehen wurde, und ausdruecklich
  hinzufuegt: *„The files do not say by how much."* Jemand hat es beobachtet;
  die Beobachtung zu loeschen waere ein Verlust, sie zu beziffern eine
  Erfindung.
* **`ladder.down` wird jetzt gezeigt**, in eigenem Abschnitt `IT IS WEAKENED`,
  in der Typografie extrahierter Werte, mit einer Bezugsgroessen-Zeile:
  *„A step the game's own data gives this Nightlord: while it is on, these
  multiply its normal figures. The files do not say what puts it into the
  step."* Sieben von zehn Bossen zeigen jetzt eine belegte Schwaechungsstufe,
  vorher null.
* Eigener Abschnitt und **nicht** eine Zeile unter `IT BUFFS ITSELF`: die
  Zahlen bewegen den Boss in die andere Richtung, und eine gemeinsame
  Ueberschrift ist genau der Weg, auf dem ein Leser die eine fuer die andere
  haelt — der Fehler, den QA-129 als "zwei Groessen im selben Panel ohne
  Unterscheidung" benennt.

**Was ich dem `director` vorlege:** Ob die Sichtung ueberhaupt bleiben soll,
ist eine Streichfrage und damit deine bzw. die des App Designers. Ich habe
sie behalten, weil dein Auftrag "die Zeile entfernen" auf die **Zahlen**
zielte ("das Programm sagt einem Spieler etwas ueber einen Boss, das nicht
stimmt") und die qualitative Sichtung nichts Falsches sagt.

---

## 2. Teil 1 — die drei falschen Zahlen

### QA-126 / AK-79, AK-80 — `Avg chance` ist jetzt gewichtet

**Der geforderte Nachweis an genau dem Fall.** `[Wylder] Improved Mind,
Reduced Vigor` traegt im Datensatz:

```
chance      : {"0": {"pools": 1,  "avg": 1.0,      "max": 1.0}}
deep_chance : {"0","1","2","3": je {"pools": 60, "avg": 0.005012, ...}}
```

* ungewichtet: (1,0 + 4 × 0,005012) / 5 = 0,20401 → **20.4 %**
* gewichtet:  (1 × 1,0 + 240 × 0,005012) / 241 = 0,0091406 → **0.91 %**

Gemessen an der gerenderten Zelle nach der Aenderung:

```
AK-80 case: [('[Scholar] Improved Mind, Reduced Vigor', '100.0%'),
             ('[Wylder] Improved Mind, Reduced Vigor', '0.91%')]
```

Die Rechnung steht in `effectstab.refresh()`:
`sum(c["avg"] * c["pools"]) / sum(c["pools"])`, mit `0.0` wenn keine Slots
erreichbar sind.

**AK-79** ist umgesetzt: der Wortlaut steht **wortgleich** und **genau
einmal** auf dem Tab (Test zaehlt ueber Labels, Tooltips, Spaltenkoepfe und
Zellen zusammen). Die beiden alten Definitionen kommen im gesamten Baum
ausserhalb des Tests, der sie verbietet, nicht mehr vor — Suchbeleg unten,
§6.

### QA-125 / AK-78 — `Pools` heisst `Relic slots`

Ausgang B, wie von dir entschieden.

* Spaltenkopf `Relic slots`, Kopf-Tooltip **wortgleich** nach AK-78.
* Das 0-Signal ist in die Chance-Zelle gewandert: sie zeigt ohnehin `—` und
  traegt jetzt den AK-78-Tooltip *„No relic effect slot can roll this under
  the current colour and mode filters…"*. Die alte, sinnlose Zeile
  *„…— see the Pools column"* ist weg.
* Die Zeichenkette `A pool is one of the lists a relic's effects are drawn
  from` kommt nur noch in dem Test vor, der sie verbietet.
* Der Wertebereich der Spalte bleibt 0…1 110, und **das ist jetzt richtig**:
  1 110 Relikt-Effektplaetze sind moeglich, das Spiel hat 2 619 Plaetze ueber
  598 Pool-Tabellen. Der Widerspruch war die Beschriftung, nicht die Zahl.
* Der `power-user` hat genau diese Spalte als einzige Stelle genannt, die er
  „nicht verstanden" hat (T-054, Zeile 82 und 187).

### QA-127 / AK-81 — `Tier` und `Copies` aus dem ungefilterten Bestand

Beide werden jetzt einmal beim Bau des Tabs ueber `data["effects"]` ermittelt
und je Zeile nachgeschlagen.

**Ein Befund dabei, den erst mein eigener Waechter gefunden hat** (Commit
301cbed, und er ist wichtig genug fuer die QA): mein erster Wurf schlug die
Leitersprosse ueber `tier_label(effect, siblings)` nach, und das matcht auf
`effect["id"]`. Welche Zeile einer Identitaetsgruppe die Filter ueberlebt,
ist **nicht** fest — `refresh()` behaelt den ersten Kandidaten, und das ist
unter einem Farbfilter eine andere `id` als ohne. Folge: leere Zelle fuer
genau die Leitern, um die es geht. Der neue Test hat das im ersten Lauf rot
gemacht; die Sprosse wird jetzt pro **Identitaet** vorberechnet.

Gemessen nach der Korrektur:

```
Tier at All colours: [('Continuous HP Recovery', '3 of 3'),
                      ('Continuous HP Recovery', '1 of 3')]
Tier at Red        : [('Continuous HP Recovery', '1 of 3')]
```

**Abweichung von AK-81, die du entscheiden musst:** AK-81 nennt als Probe
`1 of 2` / `2 of 2`. Das sind die Zahlen der **gefilterten** Leiter — also
genau das, was AK-81 verbietet. Aus dem ungefilterten Bestand hat diese
Leiter **drei** Sprossen, von denen zwei rollbar sind; darum `1 of 3` und
`3 of 3`. Die pruefbare Aussage von AK-81 („traegt dieselbe Leitersprosse
auch bei Farbfilter Red, statt eine leere Zelle zu zeigen") ist erfuellt, die
Beispielzahlen der AK sind es nicht und koennen es nicht sein.

---

## 3. Teil 2 — die Beschriftungen, AK fuer AK

**Umgesetzt** (alle Wortlaute, die §2 bis §7 vorgeben, sind wortgleich
uebernommen):

| AK | Tab | was |
|---|---|---|
| AK-68 | alle sechs | Ueberschrift + Fragesatz, ueber jedem Bedienelement und jeder Zahl. Ein gemeinsamer Helfer `nrplanner/tabheader.py` statt sechs Kopien derselben drei Stilregeln |
| AK-69 | alle sechs | die **zehn** Stellen aus QA-128 sind einzeln abgedeckt: 1 → AK-85, 2 → AK-86, 3 → AK-87, 4/5/6 → AK-91, 7/8 → AK-96, 9 → AK-95 Satz 2, 10 → eigener Satz (siehe unten) |
| AK-70 | 4 Stellen | „the files do not say" bei `Reward multiplier`, `Refills at`, `… buildup`, `stamina recovery speed +5` |
| AK-74 | Nightlords | beide Gruen-Bedeutungen werden jetzt in den AK-91-Zeilen benannt |
| AK-76 / 82 / 89 / 95 / 98 | je Tab | Ueberschrift und Fragesatz wortgleich; die alten Bestandszeilen rutschen darunter und verlieren die Saetze, die jetzt oben stehen |
| AK-78 / 79 / 80 / 81 | Effects | siehe §2 |
| AK-85 / 86 / 87 / 88 | Weapons | Scaling-Skala, Buildup-Bezug, `FP cost` / `FP cost charged` / `Stamina cost` / `Spell slots`, `spell power` statt `spell scaling` |
| AK-91 / 92 / 93 / 94 | Nightlords | drei Erklaerzeilen; `Refills at — not in the game's files` fuer Maris; Schwaeche-Abschnitt oeffnet auch bei reiner Status-Schwaeche (Adel); Sichtungen in `OBSERVED_COLOUR` |
| AK-96 | Deep of Night | beide Notizen wortgleich; `sigil_info` erscheint einmal, zitiert |
| AK-99 | Red variants | `Examples (any map)`, Kopf-Tooltip wortgleich, `— the files name none` in den zwei Zeilen ohne Namen |
| AK-100 | Red variants | `Depth 1` / `Depth 2–3` / `Depth 4–5`, **aus den Daten gelesen**, mit Rueckfall auf fuenf Spalten |
| AK-101 / 102 / 103 | World Events | Tagesverteilung je Ereignis; Geltungsbereich der Prozentzahl und der Allaussage; Dauer nur an Zustandszeilen |
| AK-104 | World Events | Quellennamen, Param-Zeile und Reparaturgeschichte raus; `rune_scaling` erscheint an der Zeile, die es beziffert |
| AK-105 | World Events | die beiden Merchant-Eintraege verweisen sichtbar aufeinander |

### Zwei Stellen, an denen AK-93 und AK-70 den Code nicht getragen haben

**AK-93 / Adel.** Der Abschnitt heisst `WEAKNESS SPECIAL INTERACTION`, und
der Satz darunter sagte bisher: *„Pile on X damage. It builds a hidden
meter…"*. Fuer Adel gibt es kein solches X — `weak_damage` ist leer. Sein
`weak_status` ist im Datensatz **die Menge der niedrigsten
Aufbau-Schwellen** (Frostbite/Poison/Scarlet Rot/Sleep, alle 154), und das
ist eine andere Aussage als „dieser Status fuellt das versteckte Meter".
Denselben Satz auf Status zu uebertragen waere geraten. Ich habe deshalb
einen zweiten Satz geschrieben, der nur sagt, was die Daten hergeben:

> `No damage type hurts it more than another. Where it gives way is status:
> it needs least of Frostbite / Poison / Scarlet Rot / Sleep, listed with the
> rest under STATUS BUILDUP below.`

Die dafuer geschriebene Notiz (*„Phase 1 only — the poison stagger is gone in
phase 2…"*) erscheint jetzt, wie AK-93 verlangt. **An den
`ui-ux-designer`:** dieser Satz ist von mir, nicht aus §4.

**AK-70 Punkt 10 / `stamina recovery speed +5`.** AK-70 nennt die Stelle und
sagt, der Wortlaut stehe „je Stelle unten festgelegt" — §7 legt fuer diese
Stelle keinen fest. Ich habe im vorgeschriebenen Stil geschrieben:

> `The stamina recovery figure is the game's own number for that field. The
> files do not say what it is counted in, so read it as "recovers faster" and
> not as an amount per second.`

**An den `ui-ux-designer`:** auch dieser Satz ist von mir.

### AK-104: `rune_scaling` und ein Konflikt in der AK selbst

AK-104 haelt die Modulregel („Herleitung gehoert nicht auf den Bildschirm")
ausdruecklich in Kraft **und** verlangt, `rune_scaling` zu zeigen. Der Satz,
der die unbezifferte Behauptung beziffert, lautet im Datensatz aber:

> `Expeditions completed: ClearCountCorrectParam.SoulRate runs ×1 → ×1.1 → …`

— ein Param-Name mitten in der Anzeige. Den Satz wegzulassen haette die
Zahlen gekostet, die AK-104 gerade sehen will; den Param-Namen zu belassen
haette die Regel gebrochen, die dieselbe AK in Kraft haelt. Ich habe den
Token beim Rendern entfernt, an eine Zeile gebunden und begruendet
(`eventstab.PARAM_NAME`, Regex auf die Form `SomethingParam.field`). Der
uebrige Satz ist unveraendert; auf dem Bildschirm steht jetzt
*„Expeditions completed: runs ×1 → ×1.1 → …"*.

**An den `director`:** die saubere Loesung waere, den Param-Namen im
Extraktor gar nicht erst in den Anzeigetext zu schreiben
(`nrdata/extract.py::_rune_scaling`). Das ist eine Formataenderung mit
`EXTRACT_VERSION`-Anhebung und einer erzwungenen Neuextraktion; UI_SPEC §9
sagt ausdruecklich „Kein Punkt verlangt eine neue Extraktion", also habe ich
es nicht gemacht. Eintrag fuer die Debt-Liste.

---

## 4. Teil 3 — die Waechter, und je Mutation ihr Ergebnis

### Neue Dateien

| Datei | Faelle | deckt |
|---|---|---|
| `tests/tabtext.py` | Helfer | liest Labels, Tooltips, Tabellenkoepfe und Zellen eines Widgets |
| `tests/test_effects_tab_display.py` | 6 | AK-68/76, 78, 79, 80, 81 |
| `tests/test_nightlord_panel_display.py` | 6 | QA-129, 130, 131, AK-89, 91, 92, 93, 94 |
| `tests/test_deep_tab_display.py` | 5 | M1, M2, AK-95, 96 |
| `tests/test_red_variants_display.py` | 4 | M3, AK-98, 99, 100 |
| `tests/test_world_events_display.py` | 7 | M5, QA-133, 134, 135, 136, AK-68 |
| `tests/test_arsenal_tab_asks_the_facade.py` (erweitert) | +3 | M7, AK-82, 85, 86, 87 |

**Alles liest ein Widget**, nie die Funktion darunter. Tooltips zaehlen als
Anzeige, weil AK-79 eine Definition „genau einmal" verlangt und eine Zaehlung
ohne Tooltips mit zwei Vorkommen gruen bliebe.

### Die Falle, die du benannt hast

Kein Fall rechnet seine Erwartung aus der Konstante, die er bewacht:

* die Siegzahl steht mit ihrer Herleitung im Test (`+200`, im Spiel bestaetigt,
  in keinem Param), **nicht** `import WIN_RATING`;
* die Prozentzahlen werden aus der **Regel** formatiert, nicht ueber
  `format_chance` — genau die Funktion, die M4 bricht;
* die Kategorie-Ids der roten Varianten sind im Test ausgeschrieben, nicht aus
  `PLAYER_GROUPS` importiert — ein Import wuerde Kategorie 160 dorthin folgen,
  wohin M3 sie verschiebt;
* die beiden Skalierungszeilen werden im Test aggregiert, nicht ueber
  `_summary()`;
* die Boss-Zahlen werden gegen `weakness.profile` geprueft, nie gegen
  `nrplanner.bosstab`.

### Die acht Mutationen, einzeln nachgefahren

Verfahren je Mutation: frischer Baum aus dem Arbeitsstand (`tar`, ohne
`.git`), `mutate.py --apply`, dann
`NIGHTREIGN_TEST_SNAPSHOT=… python -m pytest -q -m "not slow"`.

| Name | Ergebnis | wer sie toetet |
|---|---|---|
| `deep-win-rating-at-999` (M1) | **2 failed, 660 passed** | `test_deep_tab_display::test_the_win_row_shows_the_rating_confirmed_in_game` |
| `deep-scaling-rows-swapped` (M2) | **2 failed, 660 passed** | `test_deep_tab_display::test_each_scaling_row_holds_the_field_its_label_names` |
| `red-variants-evergaol-row-folded-away` (M3) | **3 failed, 659 passed** | `test_red_variants_display::test_every_row_counts_the_categories_its_label_names` (+ `…::test_the_examples_column_does_not_claim_the_selected_map` als Nebentreffer) |
| `effects-percentages-times-ten` (M4) | **3 failed, 659 passed** | `test_effects_tab_display::test_the_average_is_weighted…` und `…::test_every_row_shows_the_weighted_average_and_the_best_slot` |
| `effects-average-over-buckets-again` (neu, QA-126 als Rueckfall) | **3 failed, 659 passed** | dieselben beiden |
| `events-day-sentence-for-every-event` (M5) | **2 failed, 660 passed** | `test_world_events_display::test_the_day_sentence_names_this_event_s_own_split` |
| `nightlord-weakened-step-inflated` (M6, angepasst) | **2 failed, 660 passed** | `test_nightlord_panel_display::test_every_weakened_step_in_the_data_reaches_the_panel` |
| `arsenal-attack-rating-redefined` (M7) | **2 failed, 660 passed** | `test_arsenal_tab_asks_the_facade::test_the_summary_defines_every_figure_a_tile_can_carry` |

**Wichtig zur Lesart:** in jeder Zeile ist **eines** der `failed` der
Ankertest `test_differential_track::test_every_mutation_still_finds_its_anchor_in_the_real_source[<name>]`.
Der schlaegt an, weil der Anker im mutierten Baum nicht mehr passt — das ist
Absicht und **kein** zweiter Waechter. Der Beleg ist jeweils das andere
Fehlschlagen.

**M6 ist angepasst und ich sage warum.** QA-137 formuliert sie als
`x2.0`→`x9.9`, `x0.8`→`x0.1`. Diese Konstanten gibt es nach der QA-129-Fix
nicht mehr; ein Anker auf sie wuerde nichts patchen und die Suite gruen
lassen — genau der Fall, gegen den `mutate.py` gebaut ist. Die registrierte
Fassung greift dieselbe Aussage an derselben Stelle an: sie multipliziert die
**gelesene** Zahl mit 9,9, wo M6 die **getippte** verfaelschte.

### QA-137s eigener Aufbau: alle sieben gleichzeitig

Ein Baum, sieben Mutationen, ein Lauf:

```
16 failed, 646 passed, 5 deselected
  test_arsenal_tab_asks_the_facade::test_the_summary_defines_every_figure_a_tile_can_carry
  test_deep_tab_display::test_the_win_row_shows_the_rating_confirmed_in_game
  test_deep_tab_display::test_each_scaling_row_holds_the_field_its_label_names
  test_effects_tab_display::test_the_average_is_weighted_by_how_many_slots_each_entry_stands_for
  test_effects_tab_display::test_every_row_shows_the_weighted_average_and_the_best_slot
  test_nightlord_panel_display::test_every_weakened_step_in_the_data_reaches_the_panel
  test_red_variants_display::test_every_row_counts_the_categories_its_label_names
  test_red_variants_display::test_the_examples_column_does_not_claim_the_selected_map
  test_world_events_display::test_the_day_sentence_names_this_event_s_own_split
  + 7x test_differential_track::…[<name>]
```

Vorher: 622 von 622 gruen.

---

## 5. Nebenher

* **`[wording pending: QA-113]` ist ersetzt.** Wortlaut aus AK-67 wortgleich,
  Singular und Plural; die Konstante `WORDING_PENDING` ist entfallen.
  `test_an_undecided_line_says_so_on_its_face` war ausdruecklich geschrieben,
  um an dem Tag rot zu werden, an dem der Wortlaut kommt („the marker has to
  be removed deliberately, not survive because nothing was watching") — der
  Fall ist jetzt der Wort-fuer-Wort-Test dessen, wofuer der Platzhalter stand,
  plus eine Zusicherung, dass die Konstante weg ist.
  Die Mutation `settled-wording-still-marked-as-pending` schreibt den Marker
  jetzt als Literal: den Namen zu nennen haette einen `NameError` erzeugt, und
  rot aus dem falschen Grund ist kein Beleg (L-007).
* **`mutate.py::newline_of`.** Ich habe **nicht** einfach umformuliert, weil
  die Behauptung des Auftrags („der Baum ist durchgehend LF") nur zur Haelfte
  stimmt. Gemessen:

  ```
  archive  nrplanner/app.py   LF     (git archive HEAD | tar -x)
  worktree nrplanner/app.py   CRLF   (3744 CRLF, 0 reine LF)
  ```

  `.gitattributes` sagt `* text=auto eol=lf`, also ist ein per `git archive`
  gezogener Baum — der, den der Modulkopf vorschreibt — durchgehend LF. Der
  **Arbeitsbaum** hat `app.py` aber wirklich in CRLF. Die Funktion bleibt also
  noetig; die Begruendung nennt jetzt beide Messungen.

---

## 6. Suchbelege (L-006), je zwei unabhaengige Masken

**„spell scaling" in angezeigten Zeichenketten** (AST ueber `nrplanner/`,
Docstrings ausgenommen):

* Maske 1 `spell scaling`: **1 Treffer**
* Maske 2 `scaling the game`: **1 Treffer** — derselbe:
  `nrplanner/advisor/goals.py:108`, ein `Goal.scope`-Satz.

**Das ist eine offene Stelle von AK-88 und liegt ausserhalb meines Auftrags**
(„nicht der Berater, S7 bis S11"). Der Satz lautet dort *„For staves and
seals the figure is the spell scaling the game shows…"* und wird laut
`types.py:363` „once for the screen" gezeichnet. **An den `director`:**
entweder AK-88 gilt auch fuer den Berater, dann braucht es einen Auftrag
dafuer, oder AK-88 wird auf die sechs Tabs eingeschraenkt.

Im ganzen Baum inklusive Kommentaren und Docstrings: 31 Vorkommen in
`goals.py`, `app.py`, `arsenaltab.py`, `damage.py`, `weapons.py`,
`extract.py` und sechs Testdateien — alles Prosa ueber ein Feld namens
`catalyst_scaling`, keine Anzeige. **AK-88 woertlich („kommt im Baum nicht
mehr vor") wuerde eine Umbenennung dieses Begriffs quer durch Extraktor und
Fassade verlangen, ohne dass ein Spieler etwas davon sieht.** Ich habe die
Anzeige umgestellt und den Rest gelassen; das entscheidest du.

**Quellensprache in angezeigten Zeichenketten** (AST, `nrplanner/`):
Maske `fextralife|game8|eldenpedia|thefifthmatt` und, unabhaengig davon,
Maske `wiki|http|.co/|github.io|pattern modifier|param.` →
**0 Treffer** in angezeigten Literalen. Die `sources`-Listen in
`eventlore.py` bestehen weiter, werden aber nirgends gerendert (AK-104 laesst
die Frage, ob sie erscheinen sollen, dem App Designer, §10 Frage 5).

**Die drei zurueckgezogenen Chance-/Pool-Saetze**: kommen ausserhalb der
Tests, die sie verbieten, und der Prosa in `mutate.py` nicht mehr vor.

---

## 7. Was ich NICHT gemacht habe, und warum

### Geometrie — T-058, wie beauftragt

AK-71, AK-72, AK-73, AK-77, AK-84, AK-90, AK-97 sind unangetastet. **Fass die
Layoutgroessen nicht an** habe ich woertlich genommen.

**Wichtig fuer T-058: ich habe DR-015 messbar verschlimmert.**
`DeepTab().minimumSizeHint().height()` gemessen mit
`QT_QPA_PLATFORM=offscreen`:

| Tab | vorher (T-056) | jetzt |
|---|---|---|
| Deep of Night | 949 | **1047** |
| Effects & chances | — | 180 |
| Nightlords | — | 150 |
| Red variants | — | 220 |
| World Events | — | 141 |

Ursache: AK-95 und AK-96 verlangen vier neue Zeilen auf genau dem Tab, der
schon zu hoch war. Die Zielschranke von AK-71 ist 860; T-058 muss also
zusaetzlich 187 px auffangen statt 89. Die Loesungsrichtung aendert sich
nicht (`QScrollArea` plus Aufgabe der festen Tabellenhoehen), der Bedarf
schon.

### Zwei Punkte im ausgeschlossenen DR-Bereich, die keine Geometrie sind

Beide liegen in „DR-013 bis DR-018", das du T-058 zugeschlagen hast, sind aber
Beschriftung bzw. Erstzustand. **Ich habe sie nicht gemacht und lege sie dir
vor:**

* **DR-017 / AK-83** — `Weapons & spells` oeffnet weiterhin mit drei
  zugeklappten Ueberschriften und ~95 % leerer Flaeche. Ein
  `setChecked(True)`, aber es aendert die Mindesthoehe des Tabs und greift
  damit in dieselbe Rechnung wie T-058. Screenshot des Ist-Zustands liegt in
  meinem Arbeitsverzeichnis; der Zustand ist unveraendert der aus
  `docs/screenshots/2026-09-05-T056/tab2-weapons.png`.
* **DR-018 / AK-75** — ` -- ` steht weiterhin in **10** angezeigten Literalen,
  alle in `nrplanner/eventlore.py`. Eines davon habe ich beim AK-104-Umbau
  angefasst und den Strich bewusst stehen lassen, damit T-058 einen einzigen
  Durchgang machen kann statt zwei halbe. **Jede Zeichenkette, die ich neu
  geschrieben habe, benutzt `—`.**

### AK-99, halb

Die **Beschriftung** ist umgesetzt. Die Zusicherung „die Spalte ist **nie**
breiter als `What can be red`" habe ich nicht garantiert, sondern nur den
Stretch-Modus getauscht (Spalte 0 bekommt jetzt den Rest, Spalte 1
`ResizeToContents`). Am laufenden Fenster bei 1600 px ist `What can be red`
klar die breiteste Spalte. Eine harte Zusicherung bei **jeder** Breite waere
eine Spaltenbreiten-Regel und gehoert zu DR-014/T-058.

### AK-104, `sources` als eigene Zeile

Nicht gebaut. AK-104 macht es ausdruecklich davon abhaengig, ob der App
Designer die Quellen sehen will (§10 Frage 5) — das ist unbeantwortet.

### AK-74, zwei Farbrollen ohne Legende

AK-74 nennt als „Betroffen" nur Gruen im Nightlords-Tab und Blau/Rot im
Effects-Tab; beide sind erfuellt. Beim Bauen sind mir **zwei weitere
bedeutungstragende Farben ohne Legende** aufgefallen, die in dieser Liste
nicht stehen:

1. `Effects & chances`, Spalte `Stacking`: **Rot** bedeutet „eine zweite Kopie
   ist verschwendet" (`Qt.red`, `effectstab.py`). Nirgends benannt.
2. `Nightlords`: `OBSERVED_COLOUR` (`#7fae72`) bedeutet „im Spiel gesehen, nicht
   aus den Dateien gelesen" — nach AK-94 jetzt auf **drei** Zeilenarten, und
   nirgends erklaert. Ein Leser sieht ein Gruen, das dem „Schwaeche"-Gruen
   sehr aehnlich sieht, und kann die Bedeutung nicht erraten.

**An den `ui-ux-designer`:** ich habe nichts dazu erfunden, weil die
„Betroffen"-Liste abschliessend formuliert ist. Beides braucht je einen Satz.

---

## 8. Was ich am laufenden Fenster gesehen habe

`.venv\Scripts\python.exe run.py`-Aufbau, 1600x900 logisch, Screenshots von
allen sechs Tabs plus den drei geaenderten Nightlord-Panels (Adel, Maris,
Gladius). Bestaetigt:

* Alle sechs Tabs oeffnen mit Ueberschrift und Fragesatz, oberhalb aller
  Bedienelemente.
* Effects: Spalte heisst `Relic slots`, `Tier` traegt Werte, der
  Definitionssatz steht unter der Filterzeile.
* Nightlords/Adel: Schwaeche-Abschnitt **und** seine Notiz sind da; die drei
  AK-91-Zeilen stehen unter ihren Bloecken; `IT IS WEAKENED` erscheint.
* Nightlords/Maris: `Refills at — not in the game's files`.
* Red variants: `Depth 1 / Depth 2–3 / Depth 4–5`, `Examples (any map)`,
  `— the files name none` in zwei Zeilen, `What can be red` ist die breiteste
  Spalte.
* World Events: die Tagessaetze unterscheiden sich (Judgment „19 of the 20",
  Fire-Summoning Beasts „9 of the 30"); `10,000 runes` ohne Dauer;
  `invulnerable for 5s` mit.
* **Beobachtung fuer den `ui-ux-designer`:** der Zusammenfassungsblock des
  Weapons-Tabs traegt jetzt vier Saetze und laeuft bei 1600 px ueber drei
  Zeilen Grau. Das ist die Folge von AK-64 + AK-85 + AK-86 an einer Stelle.
  Inhaltlich richtig, optisch dicht — falls das stoert, ist die
  Aufteilung deine Entscheidung, nicht meine.

---

## 9. An den `qa-engineer`

**Zu testen, mit den Kanten:**

1. **Effects, `Avg chance`.** Der Beleg ist `[Wylder] Improved Mind, Reduced
   Vigor` = **0.91 %**. Kante: Effekte, bei denen `Relic slots` 0 ist — dort
   muss die Chance-Zelle `—` zeigen und den AK-78-Tooltip tragen, nicht `0.00 %`.
2. **Effects, `Tier`/`Copies` unter jedem Farbfilter.** Die Sprosse darf sich
   beim Filtern nie aendern und nie leer werden. Das war der Fehler, den mein
   eigener Waechter gefunden hat; er kann in anderer Form wiederkommen.
3. **Nightlords, alle zehn Panels.** Sieben muessen `IT IS WEAKENED` zeigen
   (Gladius, Adel, Gnoster, Libra, Fulghor, Harmonia, Straghess), drei nicht
   (Maris, Caligo, Heolstor). Kante: Gnoster hat **zwei** `down`-Eintraege.
4. **Nightlords, Adel.** Der einzige mit reiner Status-Schwaeche.
5. **Nightlords, Maris.** Der einzige mit `recovery = -1`.
6. **World Events, alle elf plus die vier unannounced.** Kanten:
   `Beast's Hunt` (vier `parts`, davon zwei mit `duration` 0 bzw. 0,1 und
   leeren `lines`), `Power to Balance the World` (`invulnerable` mit
   `duration` 0,0 — darf **kein** `for 0s` erzeugen), `Judgment` (19:1).
7. **Red variants, alle sechs Karten.** Kante: `Great Hollow` — dort faellt
   die Evergaol-Zeile ganz weg, weil ihre Zahlen 0 sind. Das ist richtig und
   sieht wie ein Fehler aus.
8. **Deep of Night.** Der Tab ist **hoeher** geworden (1047 statt 949). Auf
   dem Bildschirm des Nutzers sind die letzten Zeilen weiterhin nicht
   erreichbar; das bleibt DR-015/T-058 und ist **kein** neuer Befund, aber der
   Abstand ist groesser.

**Was ich nicht abgedeckt habe und wo du hinschauen solltest:** Die
Zauberkacheln bleiben in ihren **Zahlen** ungedeckt (das ist die bewusste
Entscheidung aus `_build_spells`, QA-086); mein neuer Fall liest nur ihre
**Beschriftungen**. Und `eventlore.py` hat keinen Waechter fuer die Prosa,
die ich umgeschrieben habe — nur die Zusicherung, dass die sechs verbotenen
Zeichenketten nicht mehr erscheinen.

---

## 10. An den `director` — Debt, Risiken, Entscheidungen

**Zu entscheiden:**

1. **AK-88 im Berater.** `nrplanner/advisor/goals.py:108` zeigt weiterhin
   `spell scaling` in einem `Goal.scope`-Satz. Ausserhalb meines Auftrags.
2. **AK-88 woertlich („im Baum").** 31 Vorkommen in Kommentaren, Docstrings
   und Feldprosa. Umbenennung quer durch Extraktor und Fassade, ohne
   sichtbaren Gewinn. Empfehlung: AK-88 auf angezeigten Text einschraenken.
3. **DR-017/AK-83 und DR-018/AK-75** — im ausgeschlossenen Bereich, aber
   keine Geometrie. Wer macht sie?
4. **Die Sichtungszeile im Nightlords-Panel** — behalten (mein Stand) oder
   streichen? Streichung ist App-Designer-Sache.
5. **AK-81s Beispielzahlen** (`1 of 2` / `2 of 2`) widersprechen AK-81s
   eigener Regel. Der `ui-ux-designer` sollte sie auf `1 of 3` / `3 of 3`
   nachziehen, sonst prueft die naechste QA gegen einen falschen Wert.
6. **AK-82s Fragesatz sagt „set above"**, waehrend AK-68 die beiden Zeilen
   **ueber** die Bedienelemente stellt. Ich habe beides woertlich umgesetzt,
   also steht jetzt „the Nightfarer, level and upgrade set above" ueber den
   Bedienelementen, die darunter sitzen. Einer der beiden AK muss nachziehen.

**Debt, gefunden, nicht behoben:**

* `nrdata/extract.py::_rune_scaling` schreibt einen Param-Namen in einen
  Anzeigetext. Behebung braucht `EXTRACT_VERSION`-Anhebung; UI_SPEC §9
  verbietet neue Extraktion in diesem Auftrag. Ich habe es im Renderer
  abgefangen — das ist eine Reparatur an der falschen Stelle und sollte
  irgendwann an die richtige.
* `nrplanner/bosstab.py` hatte eine ungenutzte Modulfunktion `_heading` (toter
  Code seit unbekanntem Datum). Sie ist mit dem gemeinsamen Helfer entfallen.
* `nrplanner/bosstab.py::PART_NAMES` ist weiterhin leer, der Abschnitt
  `BODY PARTS` zeigt `Part 1`, `Part 2`. UI_SPEC §8 schlaegt Streichung vor —
  App Designer.

**Sicherheit:** nichts gefunden. Der einzige neue Verarbeitungspfad fuer
Fremddaten ist `PARAM_NAME.sub()` auf extrahiertem Text; das entfernt
Zeichen und fuegt keine ein. Alles Neue geht ueber Qt-Textsetzung, kein
`setText` mit gebautem Markup ausser in `bosstab`, wo `html.escape` an den
bestehenden Stellen unveraendert bleibt.

**Zwei Eingestaendnisse zu meinen eigenen Commits:**

* Commit `301cbed` enthaelt neben der Logikkorrektur eine reine
  Zeilenumbruch-Aenderung in `depthstab.py` (`_counts_for` ueber die
  79-Spalten-Grenze). Formatierung und Logik gehoeren nicht in denselben
  Commit; ich habe es im Text benannt, aber es ist ein Verstoss gegen meine
  eigene Regel.
* Commit `0c4f8fa` traegt drei Aenderungen an `scripts/differential/mutate.py`
  mit, die thematisch zu drei verschiedenen Commits gehoert haetten (der
  Arsenal-Anker, der Wording-Marker, die `newline_of`-Begruendung). Ursache:
  die Aenderungen lagen bereits verschraenkt in derselben Datei, als ich mit
  dem Committen begann.

---

## 11. DoD

- [x] Anforderung verstanden, Annahmen dokumentiert (Block oben)
- [x] Build & Tests gruen in der benannten Umgebung: Windows 10,
      `.venv\Scripts\python.exe -m pytest -q -m "not slow"` → **662 passed,
      5 deselected**; `-m "slow"` → **5 passed**
- [x] Neue Tests fuer neue Logik: 40 Faelle, je Tab mindestens einer, jeder
      mit einer registrierten toetenden Mutation, jede Mutation nachgefahren
- [x] Kein Linter im Projekt (nur pytest). Manuell geprueft: keine neue Zeile
      ueber 79 Spalten ausser den Mutationsankern, die der Modulkopf
      ausdruecklich ausnimmt; keine TODO/FIXME/XXX; kein toter Code; keine
      Secrets
- [x] QA-Akzeptanzkriterien selbst durchgespielt, am laufenden Fenster
      angesehen (§8)
- [ ] **Offen:** AK-71/72/73/77/84/90/97 (Geometrie, T-058), AK-75 und AK-83
      (im ausgeschlossenen DR-Bereich), AK-99 Breitenzusicherung, AK-104
      `sources`-Zeile, AK-88 im Berater. Alle in §7 und §10 einzeln benannt.
- [x] Bericht geschrieben
