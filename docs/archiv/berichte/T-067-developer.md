# T-067 — developer

```
STATUS: erledigt
AUFTRAG: T-067 — P3-b: Die Suche (S7) und die Begruendung (S8)
GELESEN: docs/tasks/T-067.md (mit den Pflichtzitaten aus GOAL.md und
         docs/state.md, beide tragen den Auftrag) · ARCHITECTURE.md
         (AD-003 Z. 361-470, AD-004, AD-006 Z. 645-730, AD-009 Z. 824-930,
         AD-010, AD-013 Z. 1097-1175, AD-014 Z. 1175-1340, AD-015
         Z. 1340-1410, AD-016, AD-018 Z. 1532-1650, AD-025 Nachtrag VI
         Z. 2867-3130, Schritttabelle S1-S11, Pruefpunkte 8-18) ·
         UI_SPEC.md (§3.1-3.8, §4.1-4.4, §5.1-5.4, AK-41 bis AK-67, Nachtrag
         zu AK-63/AK-67, Zustandstabelle 4.1-4.14) · docs/state.md · CLAUDE.md
         · nrplanner/advisor/{__init__,types,evaluate,candidates,goals}.py ·
         nrplanner/{model,damage,inventory,datasource,app}.py (Leseteile:
         Build/sources/situational/qualitative, label_for,
         collapse_by_label, is_multiplier, is_better_lower, relics_for,
         _show_breakdown, _ar_breakdown_text) ·
         tests/{conftest,advisor_cases,relics,weapon_damage_cases}.py ·
         tests/test_advisor_{types,evaluate,candidates,goals}.py ·
         tests/test_{one_build,differential_track}.py ·
         scripts/differential/mutate.py · scripts/measure_advisor_picker.py
GEAENDERT: nrplanner/advisor/search.py (neu) ·
           nrplanner/advisor/explain.py (neu) ·
           nrplanner/advisor/__init__.py (zwei Zeilen des Modul-Docstrings) ·
           tests/test_advisor_search.py (neu) ·
           tests/test_advisor_explain.py (neu) ·
           scripts/measure_advisor_search.py (neu) ·
           scripts/differential/mutate.py (41 neue Mutationen) ·
           docs/berichte/T-067-developer.md (diese Datei).
           Vier Commits auf `docs/audit-and-advisor-design`
           (b5059c6, b10e5f3, 5aca29f, 688deda), alle nur mit eigenen
           Dateien. Kein push/pull/fetch/merge/rebase/checkout/branch/reset/
           revert/stash.
ANNAHMEN: (1) Der Wortlaut aller vier neuen nutzersichtbaren Satzarten ist
          **meiner** und von keinem AK gedeckt (Begruendungszeile, Fluchzeile,
          Halte-Zeile, `data_note`). AD-025.6 gibt den Wortlaut dem
          `ui-ux-designer`; die Saetze sind durch Tests festgenagelt, damit
          ihre Aenderung eine Entscheidung ist und kein Nebeneffekt.
          (2) AD-003 Punkt 5 nennt "die besten `top_n` Endzustaende"; ich habe
          **kein** zweites Stellrad gebaut — der Beam **ist** diese Liste, W
          ist die Zahl der Endzustaende. Siehe Abschnitt 6, D-5.
          (3) `AdvisorResult.not_counted` ist nach AD-010 gelesen worden
          ("konditionale Effekte, die in kein Total eingingen"), nicht nach
          `UI_SPEC` 4.9 ("Effekte, die keine Zahlen tragen"). Das sind zwei
          verschiedene Mengen; siehe Abschnitt 6, Befund D-3.
NAECHSTER: director (zwoelf Befunde, davon sechs entscheidungsbeduerftig),
           danach ui-ux-designer (vier Wortlaute und die Form des
           Vorschlagsblocks) und qa-engineer
BLOCKIERT DURCH: nichts
```

---

## 0. Ergebnis in fuenf Zeilen

1. **S7 steht** (`nrplanner/advisor/search.py`, 318 Zeilen): Beam ueber die
   freien Slots, Handle-Menge im Suchzustand, Symmetrie ueber
   `(Farbe, Deep)` der **freien** Slots, Scorer als Parameter, abbrechbar
   zwischen den Ebenen, deterministisch **ueber Prozessgrenzen hinweg**
   gemessen. Qt-frei.
2. **S8 steht** (`nrplanner/advisor/explain.py`, 480 Zeilen): sechs reine
   Funktionen — `chosen_for`, `reasons`, `curses`, `not_counted`,
   `data_note`, `unknowns`. Bezugspunkt ist der Grundzustand, Fluche kommen
   aus `Build.sources`, kein zweiter Rechenweg. Qt-frei.
3. **41 Mutationen** neu in `scripts/differential/mutate.py`, **alle
   toetend**, jede im **Standardlauf** gefahren. **Ein** Fall der 47 neuen
   Testfaelle hat keine eigene Mutation und ist als Charakterisierung
   ausgewiesen statt als Waechter (Abschnitt 3, Ende).
4. **Laufzeit gemessen und protokolliert**: der `Optimize`-Lauf gegen
   `Wylder's Chalice` + Deep kostet **941,6 ms**, nicht die 0,46 s aus
   AD-003. Die **Bewertungszahl** stimmt (3 621 gegen 3 929), die Kosten je
   Bewertung nicht. Abschnitt 4.
5. **Groesster Befund ausserhalb des Auftrags:** **36 von 309** besessenen
   Relikten tragen einen Fluch, den das Ergebnis **nirgends** nennt — nicht
   in `curses`, nicht in `not_counted`. Gegen `UI_SPEC` §3.2 ("ein Vorschlag,
   dessen Preis erst nach dem Anwenden sichtbar wird, ist eine Falle").
   Abschnitt 7, D-2. **Nicht behoben**, weil er ein Feld oder einen Wortlaut
   braucht, die mir nicht gehoeren.

**Suite:** vorher **864 passed, 9 skipped, 5 deselected** (`not slow`,
selbst gefahren, 449 s), nachher **952 passed, 9 skipped, 5 deselected**
(454 s). `-m "slow"`: **5 passed** (53 s), selbst gefahren am Endstand.
Neu sind 25 Faelle in `test_advisor_search.py`, 22 in
`test_advisor_explain.py` und 41 Ankerfaelle der Messstrecke.
**Kein Linter im Projekt konfiguriert** (Nutzerentscheid F-A vom 06.09.,
Option B) — der Punkt entfaellt.

---

## 1. Was gebaut ist — S7

`beam(problem, pools, budget, scorer, should_cancel)` gibt die besten
Belegungen zurueck, beste zuerst.

- **Ebenen sind die freien Slots.** Kein Zweig fuer "alles gehalten": die
  Schleife laeuft dann nullmal und der Grundzustand, bewertet, faellt heraus.
  Ein Sonderfall waere eine zweite Stelle, an der die Antwort auf diese Frage
  steht.
- **Handle-Menge im Zustand** (AD-013.2), vorbelegt mit
  `types.held_handles(problem)` (AD-014.5). Der Test dazu reicht der Suche
  einen Pool, der die gehaltene Kopie **enthaelt** — sonst wuerde er nur
  `candidates.pool` messen.
- **Symmetriegruppen ueber `(colour, deep)` der freien Slots.** Der Boden
  einer Gruppe wird aus `state.chosen` gelesen, per `max`, damit ein Slot,
  der nichts mehr zu waehlen hatte, keinen Zweig braucht, den keine Daten
  erreichen.
- **Drei Ausgaenge je Ebene und je Zustand**, jeder mit einem Grund und jeder
  einzeln getestet: Nachfolger je Zweig; der Zustand selbst, wenn der Slot
  wirklich nichts hat (`UI_SPEC` 4.11); **fallen gelassen**, wenn allein der
  Symmetrieboden ihn geleert hat — das waere derselbe Build mit vertauschten
  Slots, den ein anderer Zweig schon traegt.
- **Abbruch zwischen den Ebenen** (AD-003.4, AD-006.6) mit `Cancelled` statt
  einer kurzen Antwort: ein abgeschnittener und ein fertiger Beam haben
  dieselbe Form, und das Fenster sagt Verschiedenes dazu (4.5 gegen 4.6).
- **Vorbedingungen laut:** Pools, die nicht die freien Slots sind; ein Budget
  mit K oder W unter 1. Beides antwortet sonst mit einer leeren Liste, und
  eine leere Liste ist bereits die Form von zwei anderen Zustaenden.

## 2. Was gebaut ist — S8

Sechs reine Funktionen, jede mit einer Verantwortung; `worker.py` (S9) setzt
das `AdvisorResult` daraus zusammen.

| Funktion | AD-010-Feld | Quelle |
|---|---|---|
| `chosen_for(suggestion, pools)` | — | die Pools des Laufs |
| `reasons(chosen, base, built, ctx)` | `Suggestion.reasons` | `built.sources` **minus** `base.sources` |
| `curses(chosen, base, built, ctx)` | `curses` | dieselbe Differenz, nur die Fluchrollen |
| `not_counted(built)` | `not_counted` | `Build.situational`, `live == False` |
| `data_note(ctx)` | `data_note` | `meta.data_version` + `meta.regenerated` |
| `unknowns(problem, chosen, base, built, ctx, goal)` | `unknowns` | Haltezustand + Fluchprobe |

Eine Beispielzeile aus einem echten Lauf (Wylder, `Wylder's Chalice` + Deep,
309 Relikte, `max_damage`):

```
Slot 4, Deep Grand Burning Scene — Physical Attack Up +4: Physical Attack +12.0%
Slot 4, Deep Grand Burning Scene — Ultimate Art Charging Impaired: Ultimate Art auto-charge speed -15.0%, counted against it
A curse on Deep Grand Burning Scene changes HP restored per flask, which this goal does not rank.
Ranked on game data version 10350000, from the stored snapshot.
```

---

## 3. Rueckgabeformat Punkt 1 — je Waechter die toetende Mutation

Alle 41 Mutationen stehen in `scripts/differential/mutate.py` und sind damit
wiederholbar statt einmal gefahren. Jede wurde in einer **Kopie** des Baumes
angewandt (`git archive HEAD | tar -x`, bzw. waehrend der Arbeit ein
Tar-Abzug ohne `.git`) und gegen den **Standardlauf**
`pytest -q tests/test_advisor_search.py tests/test_advisor_explain.py`
gefahren — keine uebersprungene Konfiguration, kein Skip-Label. Zwei davon
sind zusaetzlich mit dem offiziellen Werkzeug gegengeprueft
(`mutate.py --apply … --tree`), damit die Registry und nicht nur mein
Hilfsskript belegt ist.

### 3.1 S7 — 19 Mutationen

| Mutation | toetet |
|---|---|
| `search-forgets-the-copies-a-branch-has-spent` | `…a_white_slot_does_not_take_the_copy_a_coloured_slot_already_has` |
| `search-starts-with-no-copies-spent` | `…the_search_spends_the_copies_the_held_relics_occupy` |
| `search-branches-on-the-first-k-of-the-list` | `…the_branching_takes_the_first_available_and_not_the_first_listed` |
| `search-without-the-symmetry-rule` | `…two_slots_of_one_colour_are_not_offered_the_same_pair_twice` (+2) |
| `search-groups-by-what-a-slot-is-offered-rather-than-by-its-colour` | `…a_white_slot_is_not_interchangeable_with_a_coloured_one` |
| `search-groups-the-deep-slots-with-the-ordinary-ones` | `…a_deep_slot_and_an_ordinary_slot_of_one_colour_are_not_one_group` |
| `search-keeps-the-build-the-symmetry-rule-emptied` | `…a_slot_the_symmetry_rule_empties_is_not_a_half_filled_build` (+2) |
| `search-a-slot-with-nothing-ends-the-branch` | `…a_slot_with_nothing_to_choose_from_does_not_end_the_run` (+3) |
| `search-orders-equal-builds-by-how-they-were-found` | `…the_order_among_equals_follows_the_copies_and_not_the_pre_sort` |
| `search-cuts-the-beam-before-it-is-ordered` | `…the_best_found_is_the_first_of_the_list` (+1) |
| `search-dedupes-the-beam-through-a-set` | `…two_processes_under_two_hash_seeds_answer_the_same` (+1) |
| `search-never-asks-whether-it-was-stopped` | `…a_stopped_run_says_so_instead_of_answering_short` (+1) |
| `search-asks-inside-the-level-instead-of-between` | `…a_run_is_asked_once_before_every_level` (+1) |
| `search-reads-one-pool-for-every-level` | `…no_suggestion_puts_a_copy_in_a_slot_that_cannot_hold_it` (+7) |
| `search-refuses-a-vessel-with-every-slot-held` | `…every_slot_held_is_no_search_and_the_build_as_it_stands` |
| `search-bakes-the-direction-into-the-scorer` | `…the_search_ranks_by_the_scorer_it_is_handed` |
| `search-hands-back-a-mutable-list-of-choices` | `…a_suggestion_the_search_produced_can_be_a_cache_key` (+1) |
| `search-lets-a-budget-of-zero-answer-nothing` | `…a_budget_that_searches_nothing_is_refused` |
| `search-takes-any-pools-it-is-handed` | `…pools_that_are_not_the_free_slots_are_refused` |

### 3.2 S8 — 22 Mutationen

| Mutation | toetet |
|---|---|
| `explain-reasons-against-the-empty-build` | `…a_copy_whose_effect_the_held_relic_already_caps_is_not_credited` |
| `explain-renders-every-figure-in-the-build` | `…the_reasons_name_only_effects_the_suggestion_brought` (+7) |
| `explain-lets-one-copy-claim-every-entry-of-its-name` | `…a_stacking_effect_on_three_copies_is_named_once_per_copy` |
| `explain-credits-every-copy-with-the-same-entry` | `…a_copy_whose_effect_the_game_refused_to_stack_gets_no_line` |
| `explain-guesses-the-number-format-from-the-field-name` | `…a_buff_the_game_restricts_to_one_move_does_not_say_its_name_twice` |
| `explain-writes-every-figure-as-a-flat-number` | `…a_multiplier_reads_as_a_percentage_and_a_bonus_as_a_number` (+4) |
| `explain-calls-a-smaller-cost-a-penalty` | `…a_figure_that_is_better_small_is_not_called_a_cost_for_falling` (+1) |
| `explain-reports-a-figure-that-did-not-move` | `…a_figure_that_did_not_move_is_no_reason` |
| `explain-says-one-idea-once-per-field-it-touches` | `…one_idea_split_over_several_fields_is_not_said_several_times` |
| `explain-drops-the-armament-class-from-a-scoped-buff` | `…a_buff_bound_to_one_class_of_armament_says_which` |
| `explain-reads-the-curses-off-the-relic-instead-of-the-reckoning` | `…the_curses_are_the_ones_the_calculation_applied` |
| `explain-does-not-mark-what-was-counted-against-the-relic` | `…a_curse_is_among_the_reasons_as_a_cost_that_was_counted` (+1) |
| `explain-names-every-curse-as-one-the-goal-cannot-feel` | `…a_curse_the_direction_cannot_feel_is_named` |
| `explain-never-names-a-curse-the-figure-cannot-feel` | `…a_curse_the_direction_cannot_feel_is_named` |
| `explain-says-nothing-about-the-held-slots` | `…the_held_slots_are_named_with_a_count` (+1) |
| `explain-counts-held-slots-where-none-are-held` | `…a_run_that_left_nothing_out_says_nothing` (+1) |
| `explain-does-not-say-that-nothing-was-searched` | `…every_slot_held_says_that_nothing_was_searched` |
| `explain-reports-a-declared-condition-as-uncounted` | `…a_condition_the_player_declared_is_not_reported_as_uncounted` |
| `explain-does-not-say-where-the-data-came-from` | `…the_data_note_names_the_version_and_where_it_was_read` |
| `explain-interpolates-a-version-that-is-not-there` | `…a_dataset_that_records_no_version_says_so` |
| `explain-reads-back-whatever-the-pool-leads-with` | `…a_suggestion_is_read_back_as_the_copies_it_came_from` (+1) |
| `explain-takes-a-suggestion-from-any-run` | `…a_suggestion_from_another_run_is_refused` |

### 3.3 Zwei Gegenbauten haben mich korrigiert

Beide sind der Grund, warum L-008 auf einem gefahrenen Lauf besteht und nicht
auf einer Durchsicht.

**(a) `explain-reasons-against-the-empty-build` ueberlebte den ersten Anlauf.**
Mein Abnahmefall — "keine Zeile nennt einen Effekt des **gehaltenen**
Relikts" — ging gruen durch die Mutation. Grund: die Zuordnung laeuft ueber
die Effekt-Ids der **gewaehlten** Kopien, also kann ein gehaltener Effekt
ohnehin nie genannt werden; die Differenz zum Grundzustand schuetzt etwas
**anderes**. Der Fall, der sie schuetzt, ist enger: ein gehaltenes Relikt mit
einem `isStrongestEffect` und eine gewaehlte Kopie mit demselben. Der Eintrag
in `sources` gehoert dem gehaltenen Relikt, die gewaehlte Kopie hat nichts
beigetragen — und ohne die Differenz wird ihr der ganze Betrag gutgeschrieben.
Das ist AD-014.3s erstgenannter Fehler als Prosa. Der Fall heisst
`test_a_copy_whose_effect_the_held_relic_already_caps_is_not_credited` und
toetet die Mutation. Der urspruengliche Abnahmefall ist geblieben und hat
inzwischen eine eigene Mutation (`explain-renders-every-figure-in-the-build`).

**(b) `search-keeps-ascending-across-every-colour` war ein Aequivalent.**
Meine erste Fassung dieser Mutation aenderte kein Verhalten, weil die
Handle-Mengen zweier verschiedenfarbiger Slots disjunkt sind. Die
Ersatzmutation
(`search-groups-by-what-a-slot-is-offered-rather-than-by-its-colour`) trennt
die beiden Lesarten an genau der Stelle, an der sie auseinandergehen: am
**weissen** Slot, der jede Farbe zieht. Dafuer ist der Fall
`test_a_white_slot_is_not_interchangeable_with_a_coloured_one` neu
dazugekommen.

### 3.4 Ein Fall ohne eigene Mutation — ausgewiesen, nicht nachgebessert

`test_an_effect_this_dataset_does_not_carry_is_named_nowhere` hat **keine**
toetende Mutation und bekommt keine. Eine Zeile kann einen unbekannten Effekt
nicht nennen, weil nur Namen gerendert werden, die in `Build.sources` stehen —
das folgt aus der Form und nicht aus einem Waechter. Der Fall bleibt als
Charakterisierung stehen und ist hier als solche benannt, statt eine Mutation
zu erfinden, die etwas anderes belegt.

---

## 4. Rueckgabeformat Punkt 2 — die Laufzeit mit ihrer Messumgebung

**Rezept:** `scripts/measure_advisor_search.py` (neu, Gegenstueck zu
`scripts/measure_advisor_picker.py`). Es liest den Spielstand nur und
schreibt nichts. Es setzt **kein Budget** — das ist S11.

**Messumgebung, wie das Skript sie selbst ausgibt (L-009):**

```
Windows-10-10.0.19045-SP0, Python 3.12.10 (CPython)
data_version 10350000, 309 relics owned
Wylder's Chalice [0, 2, 4] deep [0, 1, 3], Wylder at level 15,
nothing held, ranked by max_damage, K=20 W=40
```

**Gemessen wurde gegen `Wylder's Chalice` + Deep mit nichts festgehalten** —
der Fall, den AD-003 und AD-014 beide als den unguenstigsten benennen.

```
  pool sizes: [52, 54, 208, 23, 30, 21]
  pre-sort:       43.9 ms median of 3
  beam:          895.6 ms median of 3, 3621 evaluations
  whole run:     941.6 ms median
  40 suggestions, best Attack rating 202, 6 of 6 slots filled
  the three runs agree: True
```

**Die Poolgroessen bestaetigen AD-003** (49-54 farbig, 205 weiss, 21-30 deep;
hier 52/54/208/23/30/21). **Die Bewertungszahl bestaetigt AD-003 fast genau**:
3 621 gegen die dort genannten 3 929 — Herleitung `1 + 20 + 400 + 4 x 800`,
also `1 + K + W*K + (Ebenen-2) * W*K` bei K=20/W=40.

**Die Sekunden bestaetigen AD-003 nicht.** 941,6 ms gegen 0,46 s, also gut
das Doppelte. Der Unterschied sitzt vollstaendig in den Kosten **einer**
Bewertung: 895,6 ms / 3 621 = **0,247 ms**, wo AD-003 mit ~0,117 ms gerechnet
hat. AD-014 nennt fuer einen vollen Build selbst schon "0,18-0,25 ms", die
Messung liegt also am oberen Rand des dort genannten Bandes und widerspricht
AD-014 nicht.

**Wo die 0,247 ms liegen** (dieselbe Maschine, voller Sechs-Relikt-Build,
Median aus 300 Laeufen, Skript nicht committet, Rezept hier):

| | |
|---|---|
| `evaluate` (= `model.compute`) | **0,369 ms** |
| `goal.score` `max_damage` (= `damage.equipped`) | 0,021 ms |
| `goal.score` `min_damage_taken` | 0,003 ms |

**Damit ist der Vorbehalt in `goals.py` gemessen und faellt klein aus:** der
dort benannte "zweite `weapons.rate` je Bewertung" ist **5 %** der Kosten.
Die 94 % liegen in `model.compute`. Empfehlung an den `director`:
`performance-tuner` in S11 auf `model.compute` ansetzen, nicht auf die
Fassade.

**Kosten der Begruendung, zum Vergleich** (schlechtester Vorschlag des
Laufs, 7 Fluchrollen): `unknowns()` **1,02 ms** (zwei zusaetzliche
`evaluate`-Aufrufe fuer die Fluchprobe), die anderen vier Funktionen zusammen
**0,35 ms**. S8 kostet also rund **1,4 ms** auf einen 940-ms-Lauf.

---

## 5. Rueckgabeformat Punkt 3 — der Nachweis fuer die S8-Abnahme

**Die Abnahme lautet: jede Begruendungszeile nennt einen Effekt, der im
Vorschlag wirklich vorkommt.** Sie ist auf drei Wegen belegt, und der erste
ist der einzige, der ohne den Code auskommt, den er bewacht.

**(1) Der Testfall leitet die erlaubte Menge unabhaengig her.**
`test_the_reasons_name_only_effects_the_suggestion_brought` nimmt die Handles
aus `Suggestion.choices`, sucht damit die Kopien im **Inventar**, liest deren
`effect_ids` und `curse_ids` und loest sie ueber `ctx.data["effects"]` in
Namen auf. Kein Schritt davon laeuft durch `explain`. Der Fall prueft beide
Richtungen: jede Zeile nennt mindestens einen erlaubten Namen, und **keine**
Zeile nennt einen Namen des gehaltenen Relikts. Er prueft zusaetzlich, dass
die beiden Namensmengen ueberhaupt disjunkt sind — sonst waere er blind, und
das sagt er dann laut.

**(2) Die Zuordnung kann strukturell nichts anderes nennen.** `_attributed`
laeuft ueber die Effekt-Ids der gewaehlten Kopien und sucht dazu Eintraege in
`sources`; ein Name, den keine gewaehlte Kopie traegt, wird nie
nachgeschlagen. Das ist der Grund, warum (1) allein nicht ausreicht — siehe
Abschnitt 3.3 (a) — und warum es die Mutation
`explain-renders-every-figure-in-the-build` gibt, die genau diese Form
aufbricht und den Fall rot macht.

**(3) Ueber alle Vorschlaege gemessen, nicht nur ueber den besten.** Auf dem
echten Spielstand, drei Gefaesse (`Wylder's Chalice`, `Wylder's Urn`,
`Wylder's Goblet`) mal beide Zielrichtungen, **240 Vorschlaege** erklaert:
10 bis 43 Zeilen je Vorschlag, Median 21, laengste Zeile **142 Zeichen**.
Keine Zeile nennt einen Effekt ausserhalb ihres Vorschlags — geprueft mit
derselben unabhaengigen Herleitung wie in (1).

**Die Gegenrichtung ist ebenfalls belegt:** ein Effekt, den die Rechnung
**nicht** angewandt hat, bekommt keine Zeile. Drei Faelle:
`…a_copy_whose_effect_the_game_refused_to_stack_gets_no_line` (zweite Kopie
eines `isStrongestEffect`), `…a_copy_whose_effect_the_held_relic_already_caps…`
(dasselbe ueber die Haltegrenze) und `…the_curses_are_the_ones_the_calculation_applied`
(ein konditionaler Fluch steht nicht unter den Kosten, sondern in
`not_counted`).

---

## 6. Rueckgabeformat Punkt 4 — wo AD-003, AD-014 und AD-025 nicht aufgehen

Sechs Stellen. Keine davon habe ich entschieden.

**D-4 (AD-003.2 / AD-018): `SlotPool` sagt nicht, wonach er sortiert wurde.**
Die Suche muss Pools bekommen, die nach **derselben** Zielrichtung geordnet
sind, in der ihr Scorer bewertet — sonst verzweigt sie auf der falschen
Vorsortierung, und kein Wert im Ergebnis sieht falsch aus. `SlotPool` traegt
kein `rank_by`, also **kann `beam` das nicht pruefen**; ich habe es als
Vorbedingung im Docstring festgehalten. Optionen: ein Feld auf `SlotPool`
(beruehrt `types.py` und die Hashbarkeit, aber nur um ein `str`), oder es
bleibt ein S9-Vertrag. Eine Vorbedingung, die niemand pruefen kann, ist genau
die Sorte, an der dieses Projekt schon einmal haengengeblieben ist (QA-107).

**D-5 (AD-003.5): `top_n` ist nicht gebaut.** AD-003 nennt "die besten
`top_n` Endzustaende". Ich habe kein zweites Stellrad eingezogen: der Beam
**ist** diese Liste, seine Breite W ist die Zahl der Endzustaende, und ein
Aufrufer, der weniger will, nimmt den Kopf. Ein eigenes `top_n` waere eine
zweite Zahl mit eigener Begruendung und eine dritte im Cache-Schluessel.
Wenn du es als eigenes Stellrad willst, sag es — es sind zwei Zeilen, aber
sie brauchen ihre Herleitung (L-001).

**D-6 (AD-013.3): die Listenlaenge `K + (freie Slots − 1)` deckt die
Symmetrieregel nicht.** Ihre Herleitung spricht nur ueber belegte Handles.
Der Symmetrieboden schneidet aus **derselben** Liste, also kann ein spaeterer
Slot einer gleichfarbigen Gruppe schmaler verzweigen als K. Gemessen im Fall
`…the_branching_takes_the_first_available_and_not_the_first_listed`: bei K=2
und drei roten Slots verzweigt die dritte Ebene 1 bis 2 breit statt 2. Das
ist **kein Fehler** — die Beschneidung ist gewollt —, aber die Formel deckt
es nicht ab, und wer sie liest, glaubt K sei garantiert.

**D-7 (AD-009.4): `Wylder's Urn` kann die Exemplarregel nicht isolieren.**
Gemessen: auf `[Rot, Rot, Blau]` verhindert **die Symmetrieregel allein**
schon jede Wiederholung, weil sie die Raenge streng aufsteigen laesst; die
Handle-Menge ist dort ohne Wirkung. Der Pruefpunkt ist trotzdem gebaut wie
verlangt (`test_no_copy_lies_in_two_slots_of_wylders_urn`), aber die Mutation
`search-forgets-the-copies-a-branch-has-spent` laesst ihn **gruen**. Was sie
toetet, ist der zweite Fall auf `Wylder's Chalice`: ein **weisser** Slot
neben einem farbigen ist eine andere Symmetriegruppe und sieht dieselben
Kopien. Beide Faelle stehen in der Suite; AD-009.4 sollte den zweiten
mitnennen, sonst belegt der Pruefpunkt etwas anderes, als er zu belegen
meint.

**D-8 (AD-014.4 / Pruefpunkt 10): der Fall ist eine Charakterisierung.**
Die Symmetriefalle, gegen die AD-014.4 geschrieben ist, kann in dieser
Fassung **nicht** entstehen: der Boden wird aus `state.chosen` gelesen, und
darin stehen per Konstruktion nur freie Slots. Eine Gruppenbildung ueber
`problem.slots` statt ueber `free_slots` aendert deshalb **nichts** — ich habe
es gefahren. Der Pruefpunkt ist gebaut
(`test_a_hold_does_not_forbid_the_free_slot_the_better_copies`) und gruen,
aber er wird nur von der Pool-Verwechslung mitgetoetet, nicht von einer
Mutation seiner eigenen Regel. Ehrlicher Stand: AD-014.4 wird von der **Form**
getragen, nicht von einem Waechter.

**D-9 (AD-009.5): Monotonie hat ihren Geltungsbereich im Fall stehen.**
`test_a_strictly_better_copy_never_lowers_the_best_found` misst bei einem
Budget, das **jede** Belegung erreicht (fuenf Kopien auf zwei Slots gegen
K=20/W=40). Weiter reicht die Zusage nicht: AD-003 gewaehrt keine
Optimalitaet, ein schmaler Beam darf den alten Besten fuer den neuen fallen
lassen, und ein Fall, der das Gegenteil behauptet, behauptet eine Garantie,
die der Entwurf ablehnt. Das steht so im Docstring des Falls.

**D-3 (AD-010 gegen `UI_SPEC` 4.9): `not_counted` beschreibt zwei
verschiedene Mengen.** AD-010 sagt "konditionale Effekte im Besitz, die
nicht in die Totals eingingen"; `UI_SPEC` 4.9 sagt "some effects carry no
numbers" und laesst den `Why`-Dialog
`The game files carry no numbers for these, so they counted for nothing:`
schreiben. Das sind nicht dieselben Effekte: ein Fluch ohne Zahlen ist nicht
konditional, ein konditionaler Effekt traegt Zahlen. Ich habe **AD-010**
umgesetzt (`Build.situational`, `live == False`) und den Geltungsbereich im
Docstring benannt. Die Entscheidung, ob `UI_SPEC` 4.9 ein zweites Feld
braucht, gehoert dir — sie haengt an D-2 unten.

---

## 7. An den `director` — Befunde

**D-1 — Laufzeit, Empfehlung `performance-tuner`.** Siehe Abschnitt 4. Der
`Optimize`-Lauf kostet **941,6 ms**, nicht 0,46 s, und 94 % davon liegen in
`model.compute`. Folgen: A6 bekommt in S11 eine andere Zahl als AD-003
erwartet; `UI_SPEC` 4.3 (Fortschrittsbalken ab 250 ms) greift damit bei
**jedem** `Optimize`-Lauf, nicht nur im Ausnahmefall; die Picker-Frage
(AD-018, eine Ebene) bleibt davon unberuehrt und unter der Schwelle.
**Ich habe nichts optimiert** — das ist der `performance-tuner`.

**D-2 — 36 von 309 Relikten tragen einen Fluch, den das Ergebnis nirgends
nennt.** Gemessen auf dem echten Spielstand, Wylder, Level 15. Zwei Ursachen:

- **33 Relikte:** Fluche wie `Taking Damage Causes Madness Buildup` (9x),
  `… Sleep` (7x), `… Rot` (6x), `… Poison` (5x), `… Frost` (5x),
  `… Blood Loss` (4x), `… Death` (1x). Ihre Modifier sind reine Engine-Felder
  (`replaceSpEffectId`, `effectTargetPcDeceased`, `deleteCriteriaDamage`), es
  entsteht **kein** `sources`-Eintrag. Sie landen in `Build.qualitative` —
  und **kein Feld von `AdvisorResult` traegt `qualitative`**.
- **3 Relikte:** `All Resistances Down` (Effekt 6850200) senkt sieben
  Widerstandswerte um je 80. Das bewegt `Build.resistances` wirklich, aber
  `compute_resistances` schreibt **nicht** in `sources`, und in `qualitative`
  steht es auch nicht. Dieser Fluch ist in **jedem** Feld unsichtbar.

`UI_SPEC` §3.2: *"Ein Vorschlag, dessen Preis erst nach dem Anwenden sichtbar
wird, ist eine Falle."* Genau das ist es. **Nicht behoben:** die Behebung
braucht entweder ein neues `AdvisorResult`-Feld oder eine Verbreiterung von
`not_counted` (dann gegen AD-010s Wortlaut), dazu einen Wortlaut vom
`ui-ux-designer` — und im zweiten Fall vermutlich eine Aenderung an
`model.compute_resistances`, die weit ausserhalb dieses Auftrags liegt.
Zusammen mit D-3 zu entscheiden.

**D-10 — Sicherheitshinweis an S10, nicht an mich.** `explain.py` gibt
**unmaskierten** Text aus Spiel- und Savedateien zurueck: Reliktnamen,
Effektnamen, Fluchnamen, Feldnamen aus `model.label_for`. Das ist richtig so —
das Modul ist Qt-frei und liefert einfachen Text; dort zu escapen wuerde in
einem `PlainText`-Label Entitaeten anzeigen. **Aber `UI_SPEC` §3.5 und AK-53
gelten unveraendert:** wer diese Zeilen in einen `RichText`-Block schreibt,
muss sie vorher durch `html.escape()` fuehren und `setTextFormat()`
ausdruecklich setzen. Das gehoert in den S10-Auftrag, sonst wird die Luecke,
die der `security-reviewer` gefunden hat, an einer neuen Stelle wieder
eingebaut. — Was `data_note` **nicht** enthaelt: `meta["game_dir"]`. Der
Datensatz traegt einen absoluten Pfad auf die Spielinstallation; er kommt in
keiner meiner Zeilen vor, und das ist Absicht.

**D-11 — kleine Debt, nicht behoben.** Die Zahlenformatierung
`+15.0%` / `+1` steht jetzt an zwei Stellen: `app.py::_show_breakdown` (und
`_ar_breakdown_text`) und `explain.py::_amount`. Eine Regel, zwei Orte. Ich
habe sie **nicht** zusammengelegt: `app.py` ist Qt, `explain.py` muss Qt-frei
bleiben, ein gemeinsamer Ort waere ein neues Modul oder `model.py`, und beides
ist ein eigener Auftrag. Aufwand geschaetzt klein (eine Funktion, zwei
Aufrufer, ein Test), Risiko gering, aber es ist eine Aenderung an
Anzeigecode, der heute funktioniert.

**D-12 — Ungenauigkeit in einer Commit-Nachricht.** `688deda` schreibt "Three
of the forty-six new cases"; es sind **47** (25 + 22). Ich habe die Historie
**nicht** geaendert; die richtige Zahl steht hier.

---

## 8. An den `qa-engineer`

**Was neu ist und getestet werden will:**

1. **Der `Optimize`-Lauf ist noch nirgends an einer Oberflaeche.** S9 und S10
   fehlen; alles hier ist headless. Ein Lauf gegen ein gebautes Artefakt (A9)
   ist damit weiterhin nicht moeglich.
2. **Determinismus ueber Prozessgrenzen** ist fuer `search.py` belegt (drei
   Hash-Saaten, synthetische Pools mit lauter Gleichstaenden). **Nicht**
   belegt: `explain.py` ueber Prozessgrenzen. Es iteriert `built.sources`
   (ein Dict in Einfuegereihenfolge) und ein `by_curse`-Dict, beides
   deterministisch — aber gemessen ist es nicht. Wenn du eine unabhaengige
   Probe willst: derselbe Aufbau wie
   `test_two_processes_under_two_hash_seeds_answer_the_same`.
3. **Kanten, die ich gebaut, aber nur synthetisch gesehen habe:** ein Slot,
   dessen Pool leer ist (`UI_SPEC` 4.11 — auf dem echten Spielstand kommt das
   fuer eine Deep-Farbe wirklich vor, siehe die Poolgroesse 21); ein Gefaess
   mit allen Slots gehalten; ein Lauf, der zwischen zwei Ebenen abgebrochen
   wird.
4. **Der Fall, den ich fuer den scharfsten halte:** ein gehaltenes Relikt mit
   einem `isStrongestEffect` und eine vorgeschlagene Kopie mit demselben. Die
   Begruendung darf der Kopie **nichts** gutschreiben, die Punktzahl steigt
   nicht, und der Vorschlag sieht trotzdem plausibel aus.
5. **D-2 ist ein Befund fuer dich zum Nachzaehlen**, nicht nur fuer den
   `director`: auf einem anderen Spielstand ist die Zahl eine andere. Mein
   Zaehlweg: fuer jedes besessene Relikt jede Fluch-Id einzeln durch
   `model.compute` schicken und pruefen, ob `Build.sources` leer bleibt und
   `model.is_conditional` falsch ist.

**Was ich ausdruecklich nicht geprueft habe:** Linux, macOS, ein gebautes
Artefakt, und jede Frage, die eine Oberflaeche braucht.

---

## 9. An den `ui-ux-designer`

**Vier Wortlaute sind meine und brauchen deine Entscheidung** (AD-025.6 gibt
sie dir). Alle vier sind durch Tests festgenagelt, damit eine Aenderung eine
Entscheidung ist und kein Nebeneffekt:

1. **Begruendungszeile:**
   `Slot 4, Deep Grand Burning Scene — Physical Attack Up +4: Physical Attack +12.0%`
   und mit angehaengtem `, counted against it`, wo der Beitrag das Feld
   schlechter macht.
2. **Fluchzeile** (`AdvisorResult.curses`): dieselbe Form ohne den Zusatz.
3. **Halte-Zeile:** `3 of 6 slots are held, so only the other 3 were filled.`
   bzw. `All 6 slots are held, so nothing was searched: this is the build as
   it stands, scored.`
4. **`data_note`:** `Ranked on game data version 10350000, from the stored
   snapshot.` bzw. `…, read from the installed game.`, und fuer einen
   Datensatz ohne Version ein eigener Satz.

Die AD-015-Pflichtzeile ist **woertlich** aus der AD uebernommen:
`A curse on <relic> changes <field>, which this goal does not rank.`

**Eine Formfrage, die ich nicht entscheiden konnte.** `UI_SPEC` §3.2 verlangt
fuer den Vorschlagsblock **einen** Satz je Slot, hoechstens 160 Zeichen;
§3.4 Punkt 2 verlangt im `Why`-Dialog je Slot den Reliktnamen und **darunter
die Effekte** mit ihrem Beitrag. Ich habe die zweite Form gebaut — eine Zeile
je Effekt und je bewegter Groesse — weil die Abnahme in der Schritttabelle
"jede Zeile nennt **einen** Effekt" sagt. **Gemessen ueber 240 Vorschlaege:
10 bis 43 Zeilen je Vorschlag, Median 21, laengste Zeile 142 Zeichen.** Je
Slot sind das bis zu sieben Zeilen. §3.2s "ein Satz" ist damit **nicht**
erfuellt, und ich habe bewusst nichts gekuerzt und nichts mit "and 3 more"
abgeschnitten: das waere eine Anzeigeentscheidung. Bitte entscheide, ob der
Slot-Block eine dieser Zeilen zeigt, eine daraus gebaute Zusammenfassung, oder
ob §3.2 auf mehrere Zeilen geht.

**Zwei Kleinigkeiten:**

- Die Slotnummer in der Zeile ist **einsbasiert** (`slot_index + 1`), wie im
  Fenster; `SlotChoice.slot_index` bleibt nullbasiert, weil es einen Slot
  adressiert. Wenn der Block ohnehin je Slot ueberschrieben ist, ist die
  Nummer in der Zeile doppelt.
- Ein Buff, den das Spiel auf eine Bewegung beschraenkt, traegt seinen eigenen
  Namen als Feldbezeichnung (`model.label_for`). Er wuerde sonst als
  `Improved Skill Attack Power: Improved Skill Attack Power +15.0%` dastehen;
  ich lasse die Bezeichnung dann weg. Wenn du dort lieber etwas anderes haben
  willst, ist es eine Zeile in `_named`.

---

## 10. Offene Fragen

| # | Frage | An wen |
|---|---|---|
| 1 | D-2: Wie wird ein Fluch ohne Zahlen im Ergebnis genannt — neues Feld, `not_counted` verbreitern, oder gar nicht? | `director`, dann `ui-ux-designer` fuer den Wortlaut |
| 2 | D-3: Gilt fuer `not_counted` AD-010 (konditional) oder `UI_SPEC` 4.9 (ohne Zahlen)? | `director` |
| 3 | D-4: Bekommt `SlotPool` ein `rank_by`, oder bleibt die Uebereinstimmung ein ungeprueftes S9-Versprechen? | `director` |
| 4 | D-5: Soll `top_n` ein eigenes Stellrad werden, oder bleibt W die Zahl der Endzustaende? | `director` |
| 5 | Die Form des Vorschlagsblocks (§3.2 gegen §3.4) und die vier Wortlaute | `ui-ux-designer` |
| 6 | D-1: `performance-tuner` fuer S11 auf `model.compute` ansetzen? | `director` |
